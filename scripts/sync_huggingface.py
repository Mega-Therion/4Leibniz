#!/usr/bin/env python3
"""
Sync 4Leibniz Lean 4 relational geometry formalizations, benchmarks, and corpus
to Hugging Face dataset repository: ChyRho/4leibniz.
"""

import os
import sys
from pathlib import Path
from huggingface_hub import HfApi

REPO_ID = "ChyRho/4leibniz"
REPO_ROOT = Path(__file__).resolve().parent.parent

def get_token():
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")
    if not token:
        env_file = Path.home() / ".chyren" / "one-true.env"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith("HF_TOKEN=") or line.startswith("HUGGINGFACE_TOKEN="):
                    token = line.split("=", 1)[1].strip()
                    break
    if not token:
        raise RuntimeError("HF_TOKEN not found in environment or ~/.chyren/one-true.env")
    return token

def generate_hf_readme():
    return """---
license: mit
pretty_name: "4Leibniz: Formal Relational Information Geometry & Automated Verification"
tags:
  - lean4
  - formal-verification
  - relational-geometry
  - mathematics
  - leibniz
---

# 4Leibniz: Formal Relational Information Geometry & Automated Verification

Dedicated to **Gottfried Wilhelm Leibniz**'s relational foundations of geometry, monadology, and universal characteristic (*Characteristica Universalis*).

This dataset contains machine-checked Lean 4 formalizations, relational information geometry lemmas, automated adjudications, and cross-shard verification artifacts for the **4Leibniz** project:

- **Lean 4 Formal Proofs**: Machine-verified proofs in relational geometry, spectral gap bounding, and consensus invariants.
- **Relational Geometry Benchmarks**: Empirical and synthetic adjudications across relational topologies.
- **Corpus & Adjudication Ledgers**: Curated corpus documents and verification receipts.

---

### 🔗 Canonical Links & Provenance

- **GitHub Source of Truth**: [https://github.com/Mega-Therion/4Leibniz](https://github.com/Mega-Therion/4Leibniz)
- **Living Archive Web**: [https://github.com/Mega-Therion/4leibniz-web](https://github.com/Mega-Therion/4leibniz-web)
- **Leibniz Companion**: [https://github.com/Mega-Therion/leibniz-oracle](https://github.com/Mega-Therion/leibniz-oracle)
- **Research Atlas**: [https://resnova-hub-f4ucvy3e.manus.space](https://resnova-hub-f4ucvy3e.manus.space)
- **Author**: Ryan W. Yett ([ORCID: 0009-0001-1303-7190](https://orcid.org/0009-0001-1303-7190))
- **LinkedIn**: [R.W. Yett](https://www.linkedin.com/in/r-w-yett-152085293/)
- **X (Twitter)**: [@_ChyRho_](https://x.com/_chyrho_)

---

### 📂 Structure

- `Leibniz/` & `Leibniz.lean`: Core Lean 4 mathematical source code and formal definitions.
- `benchmarks/`: Benchmark suites for relational metric evaluation and performance metrics.
- `corpus/`: Leibniz historical and translated text corpus for retrieval-grounded verification.
- `adjudications.jsonl`: Multi-prover evaluation records.
- `lean-dependency-report.json`: Full AST dependency graph and axiom tracking.
- `proof-receipt.json`: Cryptographic verification receipts and signatures.
"""

def main():
    token = get_token()
    api = HfApi(token=token)
    print(f"Ensuring repository {REPO_ID} exists...")
    api.create_repo(repo_id=REPO_ID, repo_type="dataset", exist_ok=True)

    # 1. Upload dataset card README.md
    print("Uploading Hugging Face dataset card README.md...")
    api.upload_file(
        path_or_fileobj=generate_hf_readme().encode("utf-8"),
        path_in_repo="README.md",
        repo_id=REPO_ID,
        repo_type="dataset",
        commit_message="docs: update dataset card with cross-platform links and 4Leibniz metadata"
    )

    # 2. Upload directories
    dirs_to_upload = [
        "Leibniz",
        "benchmarks",
        "corpus",
        "docs",
    ]

    for d in dirs_to_upload:
        folder_path = REPO_ROOT / d
        if folder_path.exists():
            print(f"Uploading directory {d}...")
            api.upload_folder(
                folder_path=str(folder_path),
                path_in_repo=d,
                repo_id=REPO_ID,
                repo_type="dataset",
                commit_message=f"sync: upload {d} to Hugging Face dataset"
            )

    # 3. Upload key root files
    root_files = [
        "Leibniz.lean",
        "lakefile.lean",
        "lake-manifest.json",
        "lean-toolchain",
        "lean-dependency-report.json",
        "proof-receipt.json",
        "adjudications.jsonl",
        "LICENSE",
    ]
    for rf in root_files:
        fp = REPO_ROOT / rf
        if fp.exists():
            print(f"Uploading {rf}...")
            api.upload_file(
                path_or_fileobj=str(fp),
                path_in_repo=rf,
                repo_id=REPO_ID,
                repo_type="dataset",
                commit_message=f"sync: upload {rf}"
            )

    print(f"Successfully synced 4Leibniz to https://huggingface.co/datasets/{REPO_ID}")

if __name__ == "__main__":
    main()
