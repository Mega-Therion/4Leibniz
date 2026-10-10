#!/usr/bin/env bash
# Sabotage suite: each guard must fire. Runs on a temp copy of the fixture with a
# throwaway key, so it never touches the real signing key.
set -u
H=$(cd "$(dirname "$0")" && pwd); T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
cp -r "$H/fixture" "$T/fix"; rm -rf "$T/fix/.lake"
python3 -c "import nacl.utils;open('$T/k','wb').write(nacl.utils.random(32))"
python3 -c "from nacl.signing import SigningKey;import json;print(json.dumps({'ed25519':[SigningKey(open('$T/k','rb').read()).verify_key.encode().hex()]}))" > "$T/trusted.json"
export VKERNEL_SIGNING_KEY="$T/k"; fail=0
check(){ if [ "$2" = "$3" ]; then echo "PASS $1"; else echo "FAIL $1 (expected $2, got $3)"; fail=1; fi; }
cfg(){ echo "{\"imports\":[\"Fix\"],\"theorems\":[\"$1\"],\"axiom_policy\":\"standard-3\",\"check_modules\":[\"${2:-Fix.Basic}\"]}" > "$T/c.json"; }
cfg ok;          python3 "$H/attest.py" "$T/fix" "$T/c.json" "$T/ok.json" >/dev/null; check "clean theorem accepted" 0 $?
python3 "$H/verify.py" "$T/ok.json" "$T/trusted.json" --source "$T/fix" >/dev/null; check "clean record verifies" 0 $?
cfg uses_axiom;  python3 "$H/attest.py" "$T/fix" "$T/c.json" "$T/r.json" >/dev/null; check "custom axiom rejected" 1 $?
cfg uses_sorry;  python3 "$H/attest.py" "$T/fix" "$T/c.json" "$T/r.json" >/dev/null; check "sorry rejected" 1 $?
cfg missing_thm; python3 "$H/attest.py" "$T/fix" "$T/c.json" "$T/r.json" >/dev/null; check "missing theorem rejected" 1 $?
cfg ok Fix.NoSuchModule; python3 "$H/attest.py" "$T/fix" "$T/c.json" "$T/r.json" >/dev/null; check "leanchecker failure rejected" 1 $?
python3 -c "import json;r=json.load(open('$T/ok.json'));r['payload']['theorems'][0]['axioms']=['x'];json.dump(r,open('$T/t.json','w'))"
python3 "$H/verify.py" "$T/t.json" "$T/trusted.json" >/dev/null; check "tampered payload fails" 1 $?
python3 "$H/verify.py" "$T/ok.json" "$H/trusted_signers.json" >/dev/null; check "foreign signer fails" 1 $?
echo "-- edit" >> "$T/fix/Fix/Basic.lean"; python3 "$H/verify.py" "$T/ok.json" "$T/trusted.json" --source "$T/fix" >/dev/null; check "edited source fails" 1 $?
cfg ok; env -u VKERNEL_SIGNING_KEY python3 "$H/attest.py" "$T/fix" "$T/c.json" "$T/u.json" --unsigned >/dev/null; check "unsigned CI attest runs" 0 $?
python3 "$H/verify.py" "$T/u.json" "$T/trusted.json" >/dev/null; check "unsigned record does not verify" 1 $?
python3 "$H/countersign.py" "$T/u.json" "$T/cs.json" >/dev/null 2>&1; check "countersign refuses record without ci_run" 1 $?
GITHUB_RUN_ID=42 GITHUB_SERVER_URL=https://github.com GITHUB_REPOSITORY=x/y env -u VKERNEL_SIGNING_KEY python3 "$H/attest.py" "$T/fix" "$T/c.json" "$T/u2.json" --unsigned >/dev/null
python3 "$H/countersign.py" "$T/u2.json" "$T/cs.json" >/dev/null && python3 "$H/verify.py" "$T/cs.json" "$T/trusted.json" >/dev/null; check "CI record countersigned locally verifies" 0 $?

# --- hardening (v0.2): isolation, strict parser, statement-match comparator ---
python3 -c "import json,sys;p=json.load(open('$T/ok.json'))['payload'];sys.exit(0 if p['network_blocked'] and p['build_isolation']=='bwrap' and p['recheck_isolation']=='bwrap' else 1)"; check "record shows build+recheck sandboxed, network blocked" 0 $?
printf '{"payload":{"a":1},"payload":{"a":2},"signature":"x"}' > "$T/dup.json"
python3 "$H/verify.py" "$T/dup.json" "$T/trusted.json" >/dev/null 2>&1; check "duplicate-key record rejected by strict parser" 1 $?
python3 -c "import json;r=json.load(open('$T/ok.json'));t=r['payload']['theorems'][0];json.dump({'protocol':'vkernel/0.2','theorems':{t['name']:{'statement_hash':t['statement_hash']}}},open('$T/chal.json','w'))"
# NB: no --source here; an earlier case ("edited source fails") deliberately corrupted the fixture.
python3 "$H/verify.py" "$T/ok.json" "$T/trusted.json" --challenge "$T/chal.json" >/dev/null; check "matching trusted challenge verifies" 0 $?
python3 -c "import json;c=json.load(open('$T/chal.json'));k=list(c['theorems'])[0];c['theorems'][k]['statement_hash']='deadbeef';json.dump(c,open('$T/chalbad.json','w'))"
python3 "$H/verify.py" "$T/ok.json" "$T/trusted.json" --challenge "$T/chalbad.json" >/dev/null; check "wrong-statement challenge rejected by consumer" 1 $?
cfg ok; python3 "$H/attest.py" "$T/fix" "$T/c.json" "$T/mm.json" --challenge "$T/chalbad.json" >/dev/null; check "attest rejects on statement_match mismatch" 1 $?
python3 -c "import json;r=json.load(open('$T/ok.json'));r['payload_digest']='sha256:'+('0'*64);json.dump(r,open('$T/dg.json','w'))"
python3 "$H/verify.py" "$T/dg.json" "$T/trusted.json" >/dev/null; check "forged payload_digest rejected" 1 $?
exit $fail
