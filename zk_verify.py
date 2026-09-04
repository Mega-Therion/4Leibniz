from __future__ import annotations
import json, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parent
VKEY = ROOT / 'circuits' / 'verification_key.json'

def verify_groth16(proof: dict, public_signals: list, verification_key: dict | None = None) -> dict:
    key = verification_key
    if key is None and VKEY.exists():
        key = json.loads(VKEY.read_text())
    if key is None:
        return {'verified': False, 'status': 'unavailable', 'reason': 'verification key is not installed'}
    build = ROOT / 'circuits' / 'build'
    build.mkdir(exist_ok=True)
    proof_path, public_path, key_path = build/'api_proof.json', build/'api_public.json', build/'api_verification_key.json'
    proof_path.write_text(json.dumps(proof)); public_path.write_text(json.dumps(public_signals)); key_path.write_text(json.dumps(key))
    try:
        result = subprocess.run(['npx', '--prefix', str(ROOT/'circuits'), 'snarkjs', 'groth16', 'verify', str(key_path), str(public_path), str(proof_path)], cwd=ROOT/'circuits', capture_output=True, text=True, timeout=60)
        return {'verified': result.returncode == 0 and 'OK' in result.stdout, 'status': 'verified' if result.returncode == 0 else 'rejected', 'output': (result.stdout + result.stderr)[-2000:]}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {'verified': False, 'status': 'error', 'reason': str(exc)}
