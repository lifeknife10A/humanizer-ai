#!/usr/bin/env python3
"""
Forensic PDF Analysis Script for Enterprise AI Detection Reports
Extracts vector drawing paths and bounding-box coordinates corresponding to
cyan highlights, comparing flagged vs. unflagged text blocks across document pages.
"""

import sys
import os

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Error: PyMuPDF (fitz) is required. Install via: pip install pymupdf")
    sys.exit(1)


def analyze_report(pdf_path):
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return

    doc = fitz.open(pdf_path)
    print(f"\n=======================================================")
    print(f"Analyzing Detection Report: {os.path.basename(pdf_path)}")
    print(f"Total Pages: {len(doc)}")
    print(f"=======================================================")

    for pno in range(len(doc)):
        page = doc[pno]
        drawings = page.get_drawings()
        
        # Cyan highlight filter: low red, elevated green and blue
        cyan_rects = [
            fitz.Rect(d['rect'])
            for d in drawings
            if d.get('fill') and len(d['fill']) >= 3
            and d['fill'][0] < 0.5 and d['fill'][1] > 0.6 and d['fill'][2] > 0.7
        ]

        words = page.get_text('words')
        if not words:
            continue

        flagged_count = sum(
            1 for w in words
            if any(fitz.Rect(w[:4]).intersects(cr) for cr in cyan_rects)
        )
        pct = (flagged_count / len(words)) * 100

        print(f"Page {pno+1:2d}: {flagged_count:4d} / {len(words):4d} words flagged ({pct:5.1f}%) | {len(cyan_rects):3d} highlight rects")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        for p in sys.argv[1:]:
            analyze_report(p)
    else:
        print("Usage: python3 forensic_pdf_analysis.py <path_to_report.pdf>")
