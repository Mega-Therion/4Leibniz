#!/usr/bin/env python3
"""Build-backed Calculemus verification receipt generator."""
from pathlib import Path
import subprocess, sys, time
root = Path(__file__).resolve().parents[1]
start = time.time()
result = subprocess.run(['lake', 'build'], cwd=root, text=True)
if result.returncode:
    sys.exit(result.returncode)
subprocess.run([sys.executable, str(root/'scripts/check_sorries.py')], cwd=root, check=True)
print(f'Calculemus: kernel build passed in {time.time()-start:.2f}s; 0 sorries.')
