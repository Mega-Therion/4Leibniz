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
cfg ok Fix.NoSuchModule; python3 "$H/attest.py" "$T/fix" "$T/c.json" "$T/r.json" >/dev/null; check "leanchecker exception (exit 0) rejected" 1 $?
python3 -c "import json;r=json.load(open('$T/ok.json'));r['payload']['theorems'][0]['axioms']=['x'];json.dump(r,open('$T/t.json','w'))"
python3 "$H/verify.py" "$T/t.json" "$T/trusted.json" >/dev/null; check "tampered payload fails" 1 $?
python3 "$H/verify.py" "$T/ok.json" "$H/trusted_signers.json" >/dev/null; check "foreign signer fails" 1 $?
echo "-- edit" >> "$T/fix/Fix/Basic.lean"; python3 "$H/verify.py" "$T/ok.json" "$T/trusted.json" --source "$T/fix" >/dev/null; check "edited source fails" 1 $?
exit $fail
