from __future__ import annotations
import json, subprocess, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parent
VKEY = ROOT / 'circuits' / 'verification_key.json'

# B-04 bounds: a Groth16 proof/verification-key over the demo circuit is a few
# KB. This is generous headroom, not a tuned limit -- it exists to stop a
# request from writing an unbounded blob to disk before npx ever runs.
_MAX_JSON_BYTES = 262_144
_REQUIRED_PROOF_KEYS = {'pi_a', 'pi_b', 'pi_c', 'protocol'}

def _validate_shape(proof: dict, public_signals: list, key: dict) -> str | None:
    if not _REQUIRED_PROOF_KEYS.issubset(proof.keys()):
        return f"proof missing required field(s): {sorted(_REQUIRED_PROOF_KEYS - proof.keys())}"
    if not all(isinstance(s, (str, int, float)) for s in public_signals):
        return 'public_signals must be a flat list of scalars'
    if len(public_signals) > 256:
        return 'public_signals exceeds the 256-element bound for this circuit'
    for label, blob in (('proof', proof), ('public_signals', public_signals), ('verification_key', key)):
        if len(json.dumps(blob)) > _MAX_JSON_BYTES:
            return f'{label} exceeds the {_MAX_JSON_BYTES}-byte bound'
    return None

def verify_groth16(proof: dict, public_signals: list, verification_key: dict | None = None) -> dict:
    key = verification_key
    if key is None and VKEY.exists():
        key = json.loads(VKEY.read_text())
    if key is None:
        return {'verified': False, 'status': 'unavailable', 'reason': 'verification key is not installed'}

    shape_error = _validate_shape(proof, public_signals, key)
    if shape_error is not None:
        return {'verified': False, 'status': 'malformed', 'reason': shape_error}

    # B-04: each request gets its own throwaway directory instead of the
    # shared circuits/build/, so concurrent or malicious requests can no
    # longer overwrite each other's proof material.
    with tempfile.TemporaryDirectory(prefix='zk-verify-') as tmp:
        build = Path(tmp)
        proof_path, public_path, key_path = build/'proof.json', build/'public.json', build/'verification_key.json'
        proof_path.write_text(json.dumps(proof)); public_path.write_text(json.dumps(public_signals)); key_path.write_text(json.dumps(key))
        try:
            result = subprocess.run(
                ['npx', '--prefix', str(ROOT/'circuits'), '--no', 'snarkjs', 'groth16', 'verify', str(key_path), str(public_path), str(proof_path)],
                cwd=build, capture_output=True, text=True, timeout=60,
            )
            return {'verified': result.returncode == 0 and 'OK' in result.stdout, 'status': 'verified' if result.returncode == 0 else 'rejected', 'output': (result.stdout + result.stderr)[-2000:]}
        except (OSError, subprocess.TimeoutExpired) as exc:
            return {'verified': False, 'status': 'error', 'reason': str(exc)}
