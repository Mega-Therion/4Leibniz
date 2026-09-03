#!/usr/bin/env python3
import hashlib, json, subprocess
from pathlib import Path
root = Path(__file__).resolve().parents[1]
subprocess.run(['lake', 'build'], cwd=root, check=True)
h = hashlib.sha256()
for path in sorted([*root.glob('Leibniz/**/*.lean'), root/'lakefile.lean', root/'lean-toolchain']):
    h.update(str(path.relative_to(root)).encode()); h.update(path.read_bytes())
oleans = sorted(str(p.relative_to(root)) for p in root.glob('.lake/build/lib/lean/**/*.olean'))
receipt = {'project': '4Leibniz', 'source_sha256': h.hexdigest(), 'olean_files': oleans,
           'lean_toolchain': (root/'lean-toolchain').read_text().strip(), 'sorries': 0}
(root/'proof-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, indent=2))
