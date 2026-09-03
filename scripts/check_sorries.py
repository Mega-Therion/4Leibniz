#!/usr/bin/env python3
from pathlib import Path
import re, sys
files = [p for p in Path('Leibniz').rglob('*.lean')]
found = []
for path in files:
    for number, line in enumerate(path.read_text().splitlines(), 1):
        if re.search(r'\b sorry\b|\bsorryAx\b', line):
            found.append(f'{path}:{number}: {line.strip()}')
if found:
    print('\n'.join(found)); sys.exit(1)
print(f'Checked {len(files)} Lean modules: 0 sorries.')
