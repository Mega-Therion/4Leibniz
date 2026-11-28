//! Groth16 proof verification gate.
//!
//! Faithful port of `4leibniz/zk_verify.py`. **Fidelity statement (read
//! before relying on this module):** the Python reference does *not*
//! implement Groth16 pairing cryptography itself, and neither does this
//! port. The Python module is a *gate* around the external `snarkjs`
//! verifier: it (1) refuses to run when no verification key is
//! installed, (2) validates the shape and size bounds of the proof,
//! public signals, and key (the "B-04" bounds), and (3) delegates the
//! actual pairing check to `snarkjs groth16 verify` in a throwaway
//! directory, mapping its exit code/output onto a status taxonomy. This
//! Rust port reproduces all three layers: shape validation natively,
//! and the delegation behind the [`Groth16Verifier`] trait, with
//! [`SnarkJsVerifier`] mirroring the Python subprocess call.
//!
//! SAMO context (spec §1.3): these checks are the prototype verifier
//! for the W3C-DID + Groth16 selective-disclosure compliance
//! credentials. Note that `zk_verify.py` contains no DID-document
//! parsing — DIDs enter only as the public-signal payloads a caller
//! chooses to prove statements about — so this port likewise implements
//! the verification gate, not a DID resolver. Claiming more would
//! upgrade the Python's claims, which this port does not do.

use std::io::Write;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::time::{Duration, Instant};

use serde_json::Value;

/// B-04 bound from `zk_verify.py`: a Groth16 proof / verification key
/// over the demo circuit is a few KB; 256 KiB is generous headroom that
/// stops an unbounded blob from reaching disk.
pub const MAX_JSON_BYTES: usize = 262_144;

/// B-04 bound from `zk_verify.py`: maximum public-signal count for
/// this circuit.
pub const MAX_PUBLIC_SIGNALS: usize = 256;

/// Proof keys required by `zk_verify._validate_shape`.
pub const REQUIRED_PROOF_KEYS: [&str; 4] = ["pi_a", "pi_b", "pi_c", "protocol"];

/// Verification status, mirroring the `status` strings of
/// `zk_verify.verify_groth16`'s result dict.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum VerifyStatus {
    /// Backend ran and returned success.
    Verified,
    /// Backend ran and rejected the proof.
    Rejected,
    /// Shape validation failed before any backend ran.
    Malformed,
    /// No verification key installed.
    Unavailable,
    /// The backend itself failed (spawn error, timeout, ...).
    Error,
}

impl VerifyStatus {
    pub fn as_str(self) -> &'static str {
        match self {
            VerifyStatus::Verified => "verified",
            VerifyStatus::Rejected => "rejected",
            VerifyStatus::Malformed => "malformed",
            VerifyStatus::Unavailable => "unavailable",
            VerifyStatus::Error => "error",
        }
    }
}

/// Mirrors the dict returned by `zk_verify.verify_groth16`.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct VerifyOutcome {
    pub verified: bool,
    pub status: VerifyStatus,
    /// Set for `malformed`, `unavailable`, and `error` outcomes
    /// (Python key: `reason`).
    pub reason: Option<String>,
    /// Set when the backend ran (Python key: `output`): the last 2000
    /// characters of combined stdout+stderr.
    pub output: Option<String>,
}

impl VerifyOutcome {
    fn with_reason(status: VerifyStatus, reason: impl Into<String>) -> Self {
        VerifyOutcome {
            verified: false,
            status,
            reason: Some(reason.into()),
            output: None,
        }
    }
}

/// Length of CPython `json.dumps(value)` (default separators,
/// `ensure_ascii=True`), used to reproduce the B-04 byte bounds.
/// Character count equals byte count because `ensure_ascii` output is
/// pure ASCII.
///
/// Caveat: for non-integer JSON numbers this uses serde_json's
/// shortest-round-trip formatting, which can differ from CPython's
/// `repr` in exotic cases. The Python comment itself notes the bound
/// is "generous headroom, not a tuned limit", so boundary-exact float
/// formatting is not load-bearing.
pub fn py_dumps_len(value: &Value) -> usize {
    match value {
        Value::Null => 4,
        Value::Bool(b) => {
            if *b {
                4
            } else {
                5
            }
        }
        Value::Number(n) => n.to_string().len(),
        Value::String(s) => py_escaped_len(s),
        Value::Array(items) => {
            // "[" + items joined by ", " + "]"
            let inner: usize = items.iter().map(py_dumps_len).sum();
            let seps = if items.is_empty() {
                0
            } else {
                2 * (items.len() - 1)
            };
            2 + inner + seps
        }
        Value::Object(map) => {
            // "{" + "key": value pairs joined by ", " + "}"
            let inner: usize = map
                .iter()
                .map(|(k, v)| py_escaped_len(k) + 2 + py_dumps_len(v))
                .sum();
            let seps = if map.is_empty() {
                0
            } else {
                2 * (map.len() - 1)
            };
            2 + inner + seps
        }
    }
}

/// Length of a CPython `ensure_ascii=True` JSON string literal,
/// including the surrounding quotes.
fn py_escaped_len(s: &str) -> usize {
    let mut len = 2;
    for ch in s.chars() {
        len += match ch {
            '"' | '\\' | '\n' | '\r' | '\t' | '\u{08}' | '\u{0C}' => 2,
            c if ('\u{20}'..='\u{7E}').contains(&c) => 1,
            c if (c as u32) <= 0xFFFF => 6,
            _ => 12, // surrogate pair
        };
    }
    len
}

/// Port of `zk_verify._validate_shape`. Returns the Python error string
/// on failure.
///
/// One deliberate, documented deviation: Python tests public signals
/// with `isinstance(s, (str, int, float))`, and because `bool` is a
/// subclass of `int` in Python, JSON booleans pass that check there.
/// serde_json distinguishes booleans from numbers, so this port accepts
/// `Value::Bool` as a scalar to preserve the Python behavior.
pub fn validate_shape(proof: &Value, public_signals: &[Value], key: &Value) -> Option<String> {
    let proof_obj = proof.as_object();
    let missing: Vec<&str> = REQUIRED_PROOF_KEYS
        .iter()
        .copied()
        .filter(|k| proof_obj.map(|o| !o.contains_key(*k)).unwrap_or(true))
        .collect();
    if !missing.is_empty() {
        return Some(format!("proof missing required field(s): {:?}", missing));
    }
    let is_scalar = |v: &Value| matches!(v, Value::String(_) | Value::Number(_) | Value::Bool(_));
    if !public_signals.iter().all(is_scalar) {
        return Some("public_signals must be a flat list of scalars".into());
    }
    if public_signals.len() > MAX_PUBLIC_SIGNALS {
        return Some(format!(
            "public_signals exceeds the {}-element bound for this circuit",
            MAX_PUBLIC_SIGNALS
        ));
    }
    let signals_val = Value::Array(public_signals.to_vec());
    for (label, blob) in [
        ("proof", proof),
        ("public_signals", &signals_val),
        ("verification_key", key),
    ] {
        if py_dumps_len(blob) > MAX_JSON_BYTES {
            return Some(format!(
                "{} exceeds the {}-byte bound",
                label, MAX_JSON_BYTES
            ));
        }
    }
    None
}

/// The backend that performs the actual Groth16 pairing check. The
/// Python reference delegates to `snarkjs`; implementations must not
/// pretend to be the cryptography themselves.
pub trait Groth16Verifier {
    /// Run the verification. Returns `(verified, status, tail)` where
    /// `status` is `Verified` or `Rejected` and `tail` is the combined
    /// output (the caller truncates to the last 2000 chars, as Python
    /// does), or an error string for the `error` status.
    fn verify(
        &self,
        proof: &Value,
        public_signals: &[Value],
        verification_key: &Value,
    ) -> Result<(bool, VerifyStatus, String), String>;
}

/// Port of `zk_verify.verify_groth16`, parameterized over the key and
/// backend (the Python resolves a missing key from
/// `circuits/verification_key.json`; use [`load_default_key`] for that).
///
/// Behavior, in Python order:
/// 1. No key -> `unavailable`, without touching the proof.
/// 2. Shape error -> `malformed`.
/// 3. Backend result -> `verified` / `rejected`; backend failure ->
///    `error`.
///
/// Python quirk preserved: when the backend exits 0 the status is
/// `"verified"` even if the output lacks the `OK` marker — in that
/// case `verified` is `false` while `status` is `Verified`. See
/// [`SnarkJsVerifier`].
pub fn verify_groth16(
    proof: &Value,
    public_signals: &[Value],
    verification_key: Option<&Value>,
    backend: &dyn Groth16Verifier,
) -> VerifyOutcome {
    let key = match verification_key {
        Some(k) => k,
        None => {
            return VerifyOutcome::with_reason(
                VerifyStatus::Unavailable,
                "verification key is not installed",
            )
        }
    };
    if let Some(err) = validate_shape(proof, public_signals, key) {
        return VerifyOutcome::with_reason(VerifyStatus::Malformed, err);
    }
    match backend.verify(proof, public_signals, key) {
        Ok((verified, status, output)) => VerifyOutcome {
            verified,
            status,
            reason: None,
            output: Some(
                output
                    .chars()
                    .rev()
                    .take(2000)
                    .collect::<String>()
                    .chars()
                    .rev()
                    .collect(),
            ),
        },
        Err(reason) => VerifyOutcome::with_reason(VerifyStatus::Error, reason),
    }
}

/// Load the default verification key the way `zk_verify` does:
/// `circuits/verification_key.json` next to the module (here: under
/// `circuits_dir`). Returns `None` when the file is absent or
/// unparseable, which `verify_groth16` maps to `unavailable`.
pub fn load_default_key(circuits_dir: &Path) -> Option<Value> {
    let text = std::fs::read_to_string(circuits_dir.join("verification_key.json")).ok()?;
    serde_json::from_str(&text).ok()
}

/// Backend mirroring the Python subprocess delegation to snarkjs:
///
/// ```text
/// npx --prefix <circuits> --no snarkjs groth16 verify \
///     <tmp>/verification_key.json <tmp>/public.json <tmp>/proof.json
/// ```
///
/// run in a fresh throwaway directory per request (B-04), with a
/// 60-second timeout. `verified = (exit code 0) and ("OK" in stdout)`;
/// `status = "verified" if exit code 0 else "rejected"` — including
/// the Python quirk that a zero exit without `OK` yields
/// `verified=false, status=Verified`.
pub struct SnarkJsVerifier {
    /// The `circuits` directory passed to `npx --prefix` (the Python
    /// uses `<repo>/circuits`).
    pub circuits_dir: PathBuf,
    /// The `npx` executable name/path. Defaults to `"npx"`.
    pub npx: String,
    /// Timeout; the Python uses 60 s.
    pub timeout: Duration,
}

impl SnarkJsVerifier {
    pub fn new(circuits_dir: impl Into<PathBuf>) -> Self {
        SnarkJsVerifier {
            circuits_dir: circuits_dir.into(),
            npx: "npx".into(),
            timeout: Duration::from_secs(60),
        }
    }
}

impl Groth16Verifier for SnarkJsVerifier {
    fn verify(
        &self,
        proof: &Value,
        public_signals: &[Value],
        verification_key: &Value,
    ) -> Result<(bool, VerifyStatus, String), String> {
        // B-04: a fresh throwaway directory per request, so concurrent
        // or malicious requests cannot overwrite each other's proof
        // material (mirrors tempfile.TemporaryDirectory in Python).
        let tmp = std::env::temp_dir().join(format!(
            "zk-verify-{}-{}",
            std::process::id(),
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .map(|d| d.as_nanos())
                .unwrap_or(0)
        ));
        let run = (|| -> Result<(bool, VerifyStatus, String), String> {
            std::fs::create_dir_all(&tmp).map_err(|e| e.to_string())?;
            let proof_path = tmp.join("proof.json");
            let public_path = tmp.join("public.json");
            let key_path = tmp.join("verification_key.json");
            for (path, value) in [
                (&proof_path, proof.clone()),
                (&public_path, Value::Array(public_signals.to_vec())),
                (&key_path, verification_key.clone()),
            ] {
                let mut f = std::fs::File::create(path).map_err(|e| e.to_string())?;
                f.write_all(serde_json::to_string(&value).unwrap_or_default().as_bytes())
                    .map_err(|e| e.to_string())?;
            }
            let mut child = Command::new(&self.npx)
                .arg("--prefix")
                .arg(&self.circuits_dir)
                .arg("--no")
                .arg("snarkjs")
                .arg("groth16")
                .arg("verify")
                .arg(&key_path)
                .arg(&public_path)
                .arg(&proof_path)
                .current_dir(&tmp)
                .stdout(Stdio::piped())
                .stderr(Stdio::piped())
                .spawn()
                .map_err(|e| e.to_string())?;
            // Drain both pipes while the child runs. A child that
            // writes more than the pipe capacity blocks on the write
            // and never exits, so polling try_wait without draining
            // reports a false timeout for a run that would have
            // finished; the drainer threads keep the pipes moving.
            let mut out_pipe = child.stdout.take();
            let out_thread = std::thread::spawn(move || {
                let mut buf = Vec::new();
                if let Some(mut pipe) = out_pipe {
                    let _ = std::io::Read::read_to_end(&mut pipe, &mut buf);
                }
                buf
            });
            let mut err_pipe = child.stderr.take();
            let err_thread = std::thread::spawn(move || {
                let mut buf = Vec::new();
                if let Some(mut pipe) = err_pipe {
                    let _ = std::io::Read::read_to_end(&mut pipe, &mut buf);
                }
                buf
            });
            let deadline = Instant::now() + self.timeout;
            let status = loop {
                match child.try_wait().map_err(|e| e.to_string())? {
                    Some(status) => break status,
                    None => {
                        if Instant::now() >= deadline {
                            let _ = child.kill();
                            let _ = child.wait();
                            let _ = out_thread.join();
                            let _ = err_thread.join();
                            return Err("Command 'npx snarkjs groth16 verify' timed out".into());
                        }
                        std::thread::sleep(Duration::from_millis(25));
                    }
                }
            };
            let stdout_bytes = out_thread.join().unwrap_or_default();
            let stderr_bytes = err_thread.join().unwrap_or_default();
            let stdout = String::from_utf8_lossy(&stdout_bytes).into_owned();
            let stderr = String::from_utf8_lossy(&stderr_bytes).into_owned();
            let ok_exit = status.success();
            let verified = ok_exit && stdout.contains("OK");
            let status = if ok_exit {
                VerifyStatus::Verified
            } else {
                VerifyStatus::Rejected
            };
            Ok((verified, status, stdout + &stderr))
        })();
        let _ = std::fs::remove_dir_all(&tmp);
        run
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    struct StubBackend {
        result: Result<(bool, VerifyStatus, String), String>,
    }

    impl Groth16Verifier for StubBackend {
        fn verify(
            &self,
            _proof: &Value,
            _signals: &[Value],
            _key: &Value,
        ) -> Result<(bool, VerifyStatus, String), String> {
            self.result.clone()
        }
    }

    fn good_proof() -> Value {
        json!({"pi_a": ["1", "2", "1"], "pi_b": [["1", "2"], ["3", "4"], ["1", "0"]],
               "pi_c": ["1", "2", "1"], "protocol": "groth16", "curve": "bn128"})
    }

    fn key() -> Value {
        json!({"protocol": "groth16", "curve": "bn128", "nPublic": 1})
    }

    #[test]
    fn unavailable_without_key() {
        let backend = StubBackend {
            result: Ok((true, VerifyStatus::Verified, String::new())),
        };
        let out = verify_groth16(&good_proof(), &[json!(1)], None, &backend);
        assert_eq!(out.status, VerifyStatus::Unavailable);
        assert!(!out.verified);
        assert_eq!(
            out.reason.as_deref(),
            Some("verification key is not installed")
        );
    }

    #[test]
    fn malformed_when_proof_keys_missing() {
        let backend = StubBackend {
            result: Ok((true, VerifyStatus::Verified, String::new())),
        };
        let bad = json!({"pi_a": [], "pi_b": [], "protocol": "groth16"});
        let out = verify_groth16(&bad, &[json!(1)], Some(&key()), &backend);
        assert_eq!(out.status, VerifyStatus::Malformed);
        assert!(out.reason.unwrap().contains("pi_c"));
    }

    #[test]
    fn malformed_on_non_scalar_and_oversized_signals() {
        let backend = StubBackend {
            result: Ok((true, VerifyStatus::Verified, String::new())),
        };
        let nested = vec![json!([1, 2])];
        let out = verify_groth16(&good_proof(), &nested, Some(&key()), &backend);
        assert_eq!(out.status, VerifyStatus::Malformed);
        let many: Vec<Value> = (0..257).map(|i| json!(i)).collect();
        let out = verify_groth16(&good_proof(), &many, Some(&key()), &backend);
        assert_eq!(out.status, VerifyStatus::Malformed);
        assert!(out.reason.unwrap().contains("256-element bound"));
    }

    #[test]
    fn malformed_on_oversized_blob() {
        let backend = StubBackend {
            result: Ok((true, VerifyStatus::Verified, String::new())),
        };
        let big_key = json!({"pad": "x".repeat(MAX_JSON_BYTES)});
        let out = verify_groth16(&good_proof(), &[json!(1)], Some(&big_key), &backend);
        assert_eq!(out.status, VerifyStatus::Malformed);
        assert!(out.reason.unwrap().contains("verification_key exceeds"));
    }

    #[test]
    fn backend_outcomes_map_to_python_taxonomy() {
        let signals = vec![json!(7)];
        let k = key();
        let ok = StubBackend {
            result: Ok((true, VerifyStatus::Verified, "OK".into())),
        };
        let out = verify_groth16(&good_proof(), &signals, Some(&k), &ok);
        assert!(out.verified && out.status == VerifyStatus::Verified);

        let no = StubBackend {
            result: Ok((false, VerifyStatus::Rejected, "Invalid proof".into())),
        };
        let out = verify_groth16(&good_proof(), &signals, Some(&k), &no);
        assert!(!out.verified && out.status == VerifyStatus::Rejected);

        let err = StubBackend {
            result: Err("spawn failed".into()),
        };
        let out = verify_groth16(&good_proof(), &signals, Some(&k), &err);
        assert!(!out.verified && out.status == VerifyStatus::Error);
        assert_eq!(out.reason.as_deref(), Some("spawn failed"));
    }

    #[cfg(unix)]
    #[test]
    fn chatty_child_that_floods_stdout_still_verifies() {
        // Regression: the child writes ~300 KB (far past the pipe
        // capacity) before printing OK. Without concurrent draining it
        // blocks on the write and the run is misreported as a timeout.
        use std::os::unix::fs::PermissionsExt;
        let dir = std::env::temp_dir().join(format!("zk-flood-{}", std::process::id()));
        std::fs::create_dir_all(&dir).unwrap();
        let script = dir.join("fake-npx.sh");
        std::fs::write(
            &script,
            "#!/bin/sh\nhead -c 300000 /dev/zero | tr '\\0' 'x'\necho OK\n",
        )
        .unwrap();
        std::fs::set_permissions(&script, std::fs::Permissions::from_mode(0o755)).unwrap();
        let verifier = SnarkJsVerifier {
            circuits_dir: dir.clone(),
            npx: script.to_string_lossy().into_owned(),
            timeout: Duration::from_secs(30),
        };
        let result = verifier.verify(&good_proof(), &[json!(1)], &key());
        let _ = std::fs::remove_dir_all(&dir);
        let (verified, status, _output) = result.expect("flooded child must not error");
        assert!(verified);
        assert_eq!(status, VerifyStatus::Verified);
    }

    #[test]
    fn output_is_truncated_to_last_2000_chars() {
        let long = "x".repeat(5000);
        let backend = StubBackend {
            result: Ok((true, VerifyStatus::Verified, long)),
        };
        let out = verify_groth16(&good_proof(), &[json!(1)], Some(&key()), &backend);
        assert_eq!(out.output.unwrap().chars().count(), 2000);
    }

    #[test]
    fn py_dumps_len_matches_cpython_for_common_shapes() {
        // CPython: len(json.dumps({"a": 1, "b": [True, None, "x"]})) == 32
        let v = json!({"a": 1, "b": [true, null, "x"]});
        assert_eq!(py_dumps_len(&v), 32);
        assert_eq!(py_dumps_len(&json!("café")), 11); // "caf\u00e9" = 11 chars
    }
}
