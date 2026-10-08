# Draft upstream issues (NOT filed: RY decides)

## digama0/lean4lean: exits 0 when every .olean fails to load
Running against .oleans from a newer toolchain prints `failed to read ..., incompatible header` for each module and exits 0.
Expected: nonzero exit when any requested module could not be read.
