# archon_kernel (4Leibniz)

Rust port of the 4Leibniz verified epistemic/consensus primitives, per
the S.A.M.O. v2.0 specification §8 integration map (Target 2). Every
module is a faithful port of a named Python reference in this
repository; hash outputs are byte-identical to the Python
implementations (SHA-256 over CPython-canonical JSON), verified by
golden tests generated from the Python modules themselves.

## Source-trace map

| Rust module | Source of truth |
| --- | --- |
| `epistemic` | SAMO spec §3.1–§3.2 (memory tiers, monadic bind law); `Leibniz/Epistemic.lean` (`Status` lattice: `open < conjectured < axiomatic < derived < proven`, `rank`/`join`/`meet`); `STATUSES` tuples in `bft.py`, `multiprover.py` |
| `counterexample` | `counterexample.py` (`find`, `_certify`, `Counterexample`); `ucalculus.py` (`Claim`, `Premise`); `proof_engine.py::_relation` |
| `zk_verify` | `zk_verify.py` (`verify_groth16`, `_validate_shape`, B-04 bounds) |
| `bft` | `bft.py` (`decide`, `BFTPeer`, `BFTVote`, `Incentive`) |
| `multiprover` | `multiprover.py` (`aggregate`, `ProofReport`) |
| `jsoncanon` | CPython `json.dumps` canonicalization (`sort_keys`, both separator styles, `ensure_ascii`) used by the hashed payloads |

## Fidelity notes

- **No claim upgrades.** Where the Python is a model or a delegation
  layer, the Rust is the same model or delegation layer, and says so.
- **`zk_verify` does not implement Groth16 pairing cryptography** —
  neither does `zk_verify.py`. The Python delegates the pairing check
  to `snarkjs groth16 verify`; this port reproduces the gate (key
  availability, shape/size bounds, status taxonomy) natively and the
  delegation behind the `Groth16Verifier` trait, with `SnarkJsVerifier`
  mirroring the subprocess call. `zk_verify.py` contains no
  DID-document parsing (DIDs are spec §1.3 context for what the proofs
  are *about*), so this port implements no DID resolver.
- **`counterexample` is a falsifier, not a prover** — a `no-witness`
  outcome is inconclusive, exactly as in Python.
- **`bft` is a coordination layer** — it does not replace Lean proof
  checking, exactly as in Python.
- Documented Python quirks are preserved: a second proposal/round from
  one node counts as equivocation in `bft`; the multi-prover
  independence bar is the constant `2` regardless of quorum size; a
  zero exit from snarkjs without the `OK` marker yields
  `verified=false, status="verified"`.

## Tests

```sh
cargo test
```

Unit tests live beside each module; `tests/python_parity.rs` mirrors
the scenarios of `tests/test_phase7.py` and `tests/test_phase8.py`
plus golden-hash parity checks against the Python reference.
