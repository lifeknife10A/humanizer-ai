#!/usr/bin/env python3
"""
pdf_to_md.py - High-fidelity PDF to Markdown extractor for academic papers.
Uses PyMuPDF (fitz) to extract text, headings based on font size, tables, and structure.
"""

import sys
import os
import re
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Error: pymupdf is not installed. Install via: pip install pymupdf", file=sys.stderr)
    sys.exit(1)


def clean_text(text: str) -> str:
    # Fix hyphenated line breaks in academic text: "exer- \n cise" -> "exercise"
    text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
    # Fix extraneous spaces before punctuation
    text = re.sub(r'\s+([,.:;?!])', r'\1', text)
    return text


def extract_pdf_to_markdown(pdf_path: str, output_path: str = None) -> str:
    doc = fitz.open(pdf_path)
    
    # First pass: analyze font sizes to detect heading thresholds
    font_sizes = []
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if "lines" in b:
                for line in b["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if text:
                            font_sizes.append(round(span["size"], 1))
                            
    if not font_sizes:
        # Fallback to plain text if no text spans found
        full_text = ""
        for i, page in enumerate(doc):
            full_text += f"\n\n## Page {i + 1}\n\n" + page.get_text()
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(full_text)
        return full_text

    # Calculate body font size (most common size)
    from collections import Counter
    size_counts = Counter(font_sizes)
    body_size = size_counts.most_common(1)[0][0]
    
    # Identify distinct heading levels larger than body text
    distinct_larger_sizes = sorted([s for s in size_counts.keys() if s > body_size + 1.2], reverse=True)
    
    h1_size = distinct_larger_sizes[0] if len(distinct_larger_sizes) > 0 else body_size + 4
    h2_size = distinct_larger_sizes[1] if len(distinct_larger_sizes) > 1 else body_size + 2.5
    h3_size = distinct_larger_sizes[2] if len(distinct_larger_sizes) > 2 else body_size + 1.2

    md_lines = []
    
    # Title / header metadata from document
    meta = doc.metadata
    title = meta.get("title") or Path(pdf_path).stem.replace("_", " ").title()
    author = meta.get("author") or ""
    
    md_lines.append(f"# {title}\n")
    if author:
        md_lines.append(f"**Authors / Metadata**: {author}\n")
    md_lines.append(f"> **Source File**: `{Path(pdf_path).name}` | **Total Pages**: {len(doc)}\n\n---\n")

    for page_num, page in enumerate(doc):
        md_lines.append(f"\n<!-- Page {page_num + 1} -->\n")
        
        # Check for tables using PyMuPDF table extraction if available
        tables = page.find_tables()
        table_rects = []
        if tables:
            for table in tables:
                table_rects.append(table.bbox)

        blocks = page.get_text("dict")["blocks"]
        
        for b in blocks:
            # Check if this block falls inside an extracted table
            bbox = b.get("bbox", (0, 0, 0, 0))
            in_table = any(
                rect[0] <= bbox[0] and rect[1] <= bbox[1] and rect[2] >= bbox[2] and rect[3] >= bbox[3]
                for rect in table_rects
            )
            if in_table:
                continue

            if "lines" in b:
                block_text = ""
                max_span_size = 0
                is_bold = False
                
                for line in b["lines"]:
                    line_spans = []
                    for span in line["spans"]:
                        t = span["text"]
                        size = span["size"]
                        flags = span["flags"]
                        if size > max_span_size:
                            max_span_size = size
                        if flags & 2:  # bold
                            is_bold = True
                        line_spans.append(t)
                    block_text += "".join(line_spans) + "\n"

                block_text = clean_text(block_text.strip())
                if not block_text:
                    continue

                # Format as heading or paragraph
                if max_span_size >= h1_size and len(block_text.splitlines()) <= 3:
                    md_lines.append(f"\n# {block_text}\n")
                elif max_span_size >= h2_size and len(block_text.splitlines()) <= 3:
                    md_lines.append(f"\n## {block_text}\n")
                elif max_span_size >= h3_size and len(block_text.splitlines()) <= 2:
                    md_lines.append(f"\n### {block_text}\n")
                else:
                    # Clean up paragraph formatting
                    para = " ".join(block_text.split())
                    md_lines.append(f"{para}\n\n")

        # Append markdown tables if extracted
        if tables:
            for t_idx, table in enumerate(tables):
                df_data = table.extract()
                if df_data and len(df_data) > 1:
                    md_lines.append(f"\n**Table (Page {page_num + 1}, #{t_idx + 1})**:\n\n")
                    header = [str(c or "").strip() for c in df_data[0]]
                    md_lines.append("| " + " | ".join(header) + " |\n")
                    md_lines.append("| " + " | ".join(["---"] * len(header)) + " |\n")
                    for row in df_data[1:]:
                        r = [str(c or "").replace("\n", " ").strip() for c in row]
                        md_lines.append("| " + " | ".join(r) + " |\n")
                    md_lines.append("\n")

    markdown_content = "".join(md_lines)
    
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        print(f"Successfully converted '{pdf_path}' -> '{output_path}'")
        
    return markdown_content


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 pdf_to_md.py <input.pdf> [output.md]")
        sys.exit(1)
        
    in_pdf = sys.argv[1]
    out_md = sys.argv[2] if len(sys.argv) > 2 else Path(in_pdf).with_suffix(".md").as_posix()
    extract_pdf_to_markdown(in_pdf, out_md)
