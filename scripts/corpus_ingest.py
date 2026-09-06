#!/usr/bin/env python3
"""
scripts/corpus_ingest.py
Idempotent, config-driven ingest pipeline for 4Leibniz corpus sources.
"""

import os
import sys
import json
import html
import pymupdf

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SOURCES_JSON = os.path.join(REPO_ROOT, "scripts", "corpus_sources.json")
CATALOG_JSON = os.path.join(REPO_ROOT, "corpus", "manuscripts", "catalog.json")
WITNESS_DIR = "/tmp/witnesses"
PAGES_JSON = os.path.join(WITNESS_DIR, "pages.json")


def main():
    if not os.path.exists(SOURCES_JSON):
        print(f"Error: {SOURCES_JSON} not found.", file=sys.stderr)
        sys.exit(1)

    with open(SOURCES_JSON, "r", encoding="utf-8") as f:
        sources = json.load(f)

    if not os.path.exists(PAGES_JSON):
        print(f"Error: {PAGES_JSON} not found.", file=sys.stderr)
        sys.exit(1)

    with open(PAGES_JSON, "r", encoding="utf-8") as f:
        pages_ocr = json.load(f)

    # Load catalog.json
    with open(CATALOG_JSON, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    catalog_records = {r["id"]: r for r in catalog.get("records", [])}

    pdf_docs = {}

    for catalog_id, info in sources.items():
        print(f"Processing {catalog_id}...")
        pdf_name = info.get("pdf_filename", "gerhardt_math_schr_bd7.pdf")
        pdf_path = os.path.join(WITNESS_DIR, pdf_name)

        if pdf_name not in pdf_docs:
            if not os.path.exists(pdf_path):
                print(f"Error: PDF file {pdf_path} not found.", file=sys.stderr)
                sys.exit(1)
            pdf_docs[pdf_name] = pymupdf.open(pdf_path)

        doc = pdf_docs[pdf_name]

        # 1. Extract witness page images
        witness_img_dir = os.path.join(REPO_ROOT, "corpus", "latin", "witness", catalog_id)
        os.makedirs(witness_img_dir, exist_ok=True)

        leaf_range = info["leaf_range"]
        leaf_offset = info.get("leaf_offset", -16)

        leaves = list(range(leaf_range[0], leaf_range[1] + 1))
        images_extracted = 0

        for leaf in leaves:
            img_filename = f"leaf{leaf:04d}.jpg"
            img_path = os.path.join(witness_img_dir, img_filename)

            if not os.path.exists(img_path):
                page_idx = leaf - 1  # 0-indexed in PyMuPDF
                if page_idx < 0 or page_idx >= len(doc):
                    print(f"Warning: page index {page_idx} out of range for leaf {leaf}", file=sys.stderr)
                    continue
                page = doc[page_idx]
                rect = page.rect
                scale = 1100.0 / rect.width if rect.width > 0 else 1.0
                mat = pymupdf.Matrix(scale, scale)
                pix = page.get_pixmap(matrix=mat)
                pix.save(img_path, jpg_quality=70)
                images_extracted += 1

        print(f"  Extracted {images_extracted} new images (total {len(leaves)} leaves in witness dir).")

        # 2. Write corpus/latin/<catalog-id>_normalized.md
        norm_md_path = os.path.join(REPO_ROOT, "corpus", "latin", f"{catalog_id}_normalized.md")
        if not os.path.exists(norm_md_path):
            locator = info.get("edition_locator", "")
            header = (
                f"Witness: {catalog_id}\n"
                f"Locator: {locator}\n"
                f"Transcriber: OCR-assisted pipeline (Internet Archive scan of Gerhardt, Math. Schr. Bd. 7, 1863); editorial collation pending\n"
                f"Date: 2026-09-06\n"
                f"Policy: normalized\n"
            )

            sections = []
            for leaf in leaves:
                p_idx = leaf - 1
                printed_page = leaf + leaf_offset
                text_content = ""
                if 0 <= p_idx < len(pages_ocr):
                    text_content = html.unescape(pages_ocr[p_idx].strip())
                
                sec = f"## Page {printed_page} (Leaf {leaf})\n\n{text_content}"
                sections.append(sec)

            full_content = header + "\n" + "\n\n".join(sections) + "\n"
            with open(norm_md_path, "w", encoding="utf-8") as f:
                f.write(full_content)
            print(f"  Wrote {norm_md_path}")
        else:
            print(f"  Normalized MD {norm_md_path} already exists, skipping.")

        # 3. Update catalog status
        if catalog_id in catalog_records:
            catalog_records[catalog_id]["status"] = "transcription-ocr-assisted-review-needed"

    # Save updated catalog.json
    with open(CATALOG_JSON, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("Catalog status updated successfully.")


if __name__ == "__main__":
    main()
