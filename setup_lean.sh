#!/usr/bin/env bash
set -euo pipefail

# Install Lean/Lake using the pinned toolchain and fetch Mathlib's precompiled cache.
# `lake exe cache get` is intentionally best-effort because cache availability can
# vary by Lean release; a normal build remains the fallback.
if ! command -v elan >/dev/null 2>&1; then
  curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh -s -- -y --default-toolchain none
  export PATH="$HOME/.elan/bin:$PATH"
fi
elan toolchain install "$(cat lean-toolchain)"
elan default "$(cat lean-toolchain)"
if lake exe cache get; then
  echo "Mathlib precompiled cache installed."
else
  echo "Cache unavailable; Lake will compile Mathlib from source." >&2
fi
lake build
