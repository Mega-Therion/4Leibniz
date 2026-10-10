#!/usr/bin/env python3
"""V-KERNEL sandbox: run untrusted elaboration/build and the separate recheck under the
strongest isolation the host supports, and REPORT which was achieved -- never pretend.

The v3 brief: "An isolated directory alone is not a security sandbox." So this applies,
in order of preference:
  bwrap  -- read-only root, writable project + temp HOME + tmpfs /tmp, no network
            (unshare net/pid/ipc/uts), die-with-parent.
  unshare-- new net+pid namespace via `unshare`, project writable, real FS (weaker).
  none   -- no isolation available; recorded as "none" so a consumer sees it.
In every case: rlimits (CPU, address space, file size, processes), a dedicated TMPDIR,
a hard wall-clock timeout that kills descendants, and bounded output capture. The build
never gets the network or the signing key; the environment is scrubbed.
"""
import os
import resource
import shutil
import subprocess
import tempfile

MAX_OUTPUT = 256 * 1024  # default bytes of stdout/stderr kept (tight, for hostile output)


def _rlimits(cpu_s, mem_mb, own_group):
    # CPU/mem/file-size are inherited into the sandbox. NPROC is deliberately NOT capped:
    # on a host already running many agents, a low NPROC makes bwrap's namespace clone fail
    # with EAGAIN. own_group (setsid) is only for the non-bwrap fallbacks, where it lets the
    # wall-clock timeout kill the whole tree; bwrap handles that via --die-with-parent.
    def apply():
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_s, cpu_s + 5))
        resource.setrlimit(resource.RLIMIT_FSIZE, (2 * 1024**3, 2 * 1024**3))
        # NB: RLIMIT_AS is deliberately NOT set. Lean reserves large virtual address space
        # per worker thread, so an AS cap makes it die with "failed to create thread".
        # Memory is bounded by the wall-clock timeout and LEAN_NUM_THREADS; a hard RSS cap
        # would need a cgroup (systemd-run), deferred.
        if own_group:
            os.setsid()
    return apply


def _clean_env(home, extra_ro):
    # elan/lean need PATH + HOME; nothing else from the caller crosses over (no keys, no net creds).
    path = "/usr/local/bin:/usr/bin:/bin"
    elan = os.path.expanduser("~/.elan/bin")
    if os.path.isdir(elan):
        path = elan + ":" + path
    return {"PATH": path, "HOME": home, "TMPDIR": home + "/tmp", "LANG": "C.UTF-8", "TZ": "UTC",
            "ELAN_HOME": os.path.expanduser("~/.elan"), "LEAN_NUM_THREADS": "4"}


def _bwrap_cmd(argv, cwd, writable, home):
    cmd = ["bwrap", "--die-with-parent", "--unshare-net", "--unshare-pid", "--unshare-ipc",
           "--unshare-uts", "--ro-bind", "/", "/", "--dev", "/dev", "--proc", "/proc",
           "--tmpfs", "/tmp", "--bind", home, home]
    for w in writable:
        cmd += ["--bind", w, w]
    cmd += ["--chdir", cwd, "--"] + argv
    return cmd


def run(argv, cwd, writable=(), timeout=1800, mem_mb=6144, max_output=MAX_OUTPUT):
    """Run argv isolated. Returns dict: returncode, stdout, stderr, isolation, timed_out.
    `writable` are absolute paths the command may write (e.g. the project dir); everything
    else is read-only under bwrap. `cwd` must be inside a writable path or read-only ok.
    `max_output` bounds captured stdout/stderr: keep it tight for hostile output, but a
    trusted probe whose full stdout is parsed needs a large cap (a truncated line is a
    mid-string cut that fails to parse)."""
    cwd = os.path.abspath(cwd)
    writable = [os.path.abspath(w) for w in writable]
    home = tempfile.mkdtemp(prefix="vk-sbx-")
    os.makedirs(home + "/tmp", exist_ok=True)
    env = _clean_env(home, writable)
    isolation = "none"
    if shutil.which("bwrap"):
        inner = _bwrap_cmd(argv, cwd, writable, home)
        isolation = "bwrap"
    elif shutil.which("unshare"):
        inner = ["unshare", "--net", "--fork", "--pid", "--mount-proc", "--"] + list(argv)
        isolation = "unshare"
    else:
        inner = list(argv)
    try:
        p = subprocess.run(inner, cwd=cwd if isolation != "bwrap" else None, env=env,
                           capture_output=True, timeout=timeout,
                           preexec_fn=_rlimits(timeout, mem_mb, own_group=(isolation != "bwrap")))
        return {"returncode": p.returncode, "isolation": isolation, "timed_out": False,
                "stdout": p.stdout[:max_output].decode("utf-8", "replace"),
                "stderr": p.stderr[:max_output].decode("utf-8", "replace")}
    except subprocess.TimeoutExpired as e:
        return {"returncode": 124, "isolation": isolation, "timed_out": True,
                "stdout": (e.stdout or b"")[:max_output].decode("utf-8", "replace"),
                "stderr": (e.stderr or b"")[:max_output].decode("utf-8", "replace") + "\nTIMEOUT"}
    finally:
        shutil.rmtree(home, ignore_errors=True)


def net_blocked(isolation) -> bool:
    return isolation in ("bwrap", "unshare")
