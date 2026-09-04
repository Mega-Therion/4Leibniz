from __future__ import annotations
import json, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def status():
    circom=shutil.which('circom'); snarkjs=shutil.which('snarkjs')
    circuit=ROOT/'circuits'/'private_premise.circom'
    artifacts=ROOT/'circuits'/'build'
    return {'circuit':str(circuit.relative_to(ROOT)), 'circom_available':bool(circom), 'snarkjs_available':bool(snarkjs),
            'compiled_artifacts': sorted(p.name for p in artifacts.glob('*')) if artifacts.exists() else [],
            'verified': False if not (artifacts/'verification_key.json').exists() else None,
            'boundary':'A circuit source is not a proof. Generate a witness, produce a proof, and verify it with an independently reviewed key before setting verified=true.'}

def main(): print(json.dumps(status(), indent=2))
if __name__=='__main__': main()
