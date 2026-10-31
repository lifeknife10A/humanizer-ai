#!/usr/bin/env python3
"""
Academic Humanizer: Intake (v7.13.0)

Turns a source file into the plain text the pipeline works on, so the skill
never has to stop and ask what format it was handed.

  ingest.py SOURCE [-o source.txt] [--map PAPER.map.json] [--legend legend.txt]

Formats:
  .txt / .md / .markdown   copied through unchanged
  .tex                     prose view via latex_prose.py extract; writes the map
                           (default: <output-stem>.map.json) and, with --legend,
                           the placeholder legend. Rebuild with latex_prose.py.
  .docx                    paragraphs pulled from word/document.xml (a .docx is a
                           zip). Each paragraph becomes one line, paragraphs are
                           separated by blank lines.
  .pdf                     text via `pdftotext -layout` (from poppler). A scanned
                           PDF has no text layer: ingest reports that instead of
                           guessing at OCR.

Exit codes: 0 ok, 1 file missing or unsupported format,
            2 the file is malformed or has no text to extract,
            3 a needed tool is missing (pdftotext).
"""

import argparse
import io
import json
import re
import shutil
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET

from latex_prose import extract as tex_extract

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

SUPPORTED = '.txt, .md, .markdown, .tex, .docx, .pdf'


def docx_text(data):
    """Plain text from a .docx: one line per paragraph, blank lines between."""
    try:
        zf = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile:
        raise ValueError('not a valid .docx (the file is not a zip archive)')
    try:
        xml = zf.read('word/document.xml')
    except KeyError:
        raise ValueError('not a valid .docx (word/document.xml is missing)')
    try:
        root = ET.fromstring(xml)
    except ET.ParseError as e:
        raise ValueError(f'not a valid .docx (document.xml is broken: {e})')
    paragraphs = []
    for para in root.iter(W + 'p'):
        parts = []
        for node in para.iter():
            if node.tag == W + 't' and node.text:
                parts.append(node.text)
            elif node.tag in (W + 'tab',):
                parts.append('\t')
            elif node.tag in (W + 'br', W + 'cr'):
                parts.append(' ')
        line = ''.join(parts).strip()
        if line:
            paragraphs.append(line)
    text = '\n\n'.join(paragraphs)
    if not text:
        raise ValueError('the document has no text')
    return text + '\n'


def pdf_text(path, which=shutil.which, run=subprocess.run):
    """Plain text from a .pdf via pdftotext -layout."""
    if which('pdftotext') is None:
        return None, ('pdftotext is not installed (it comes with poppler). '
                      'Install poppler, or open the PDF and save its text as .txt.')
    r = run(['pdftotext', '-layout', '-enc', 'UTF-8', path, '-'],
            capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        raise ValueError('pdftotext could not read the file: '
                         + (r.stderr.strip().splitlines() or ['unknown error'])[0])
    text = r.stdout.replace('\x0c', '').strip()
    if not text:
        return None, ('pdftotext found no text. This is probably a scanned PDF; '
                      'it needs OCR first (for example `ocrmypdf in.pdf out.pdf`).')
    # Layout mode pads with spaces; collapse each line but keep the paragraph breaks.
    lines = [re.sub(r'[ \t]+', ' ', line).strip() for line in text.splitlines()]
    text = re.sub(r'\n{3,}', '\n\n', '\n'.join(lines)).strip()
    return text + '\n', None


def ingest(path, which=shutil.which, run=subprocess.run):
    """Returns (text, mapping_or_None, problem_or_None). Raises ValueError on a bad file."""
    low = path.lower()
    if low.endswith(('.txt', '.md', '.markdown')):
        with open(path, encoding='utf-8') as f:
            return f.read(), None, None
    if low.endswith('.docx'):
        with open(path, 'rb') as f:
            return docx_text(f.read()), None, None
    if low.endswith('.pdf'):
        text, problem = pdf_text(path, which=which, run=run)
        return (None, None, problem) if text is None else (text, None, None)
    if low.endswith('.tex'):
        with open(path, encoding='utf-8') as f:
            view, mapping = tex_extract(f.read())
        return view, mapping, None
    return None, None, (f'unsupported format; ingest handles {SUPPORTED}. '
                        'For anything else, save or export it as plain text first.')


def main(argv=None):
    parser = argparse.ArgumentParser(description='Academic Humanizer: Intake (v7.13.0)')
    parser.add_argument('source', help=f'Source file ({SUPPORTED})')
    parser.add_argument('-o', '--output', default='source.txt',
                        help='Plain text to write (default: source.txt)')
    parser.add_argument('--map', help='Placeholder map for a .tex source '
                                      '(default: <output-stem>.map.json)')
    parser.add_argument('--legend', help='Also write the placeholder legend for a .tex source')
    args = parser.parse_args(argv)

    try:
        with open(args.source, 'rb'):
            pass
    except OSError:
        print(f'No such file: {args.source}', file=sys.stderr)
        return 1

    try:
        text, mapping, problem = ingest(args.source)
    except ValueError as e:
        print(f'Cannot read {args.source}: {e}', file=sys.stderr)
        return 2
    if problem:
        usage_error = problem.startswith('unsupported format')
        missing_tool = problem.startswith('pdftotext is not installed')
        print(problem, file=sys.stderr)
        return 1 if usage_error else (3 if missing_tool else 2)

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(text)
    kind = args.source.rsplit('.', 1)[-1].lower()
    words = len(text.split())
    print(f'{kind} -> {args.output} ({words} words)')
    if mapping is not None:
        map_path = args.map or args.output.rsplit('.', 1)[0] + '.map.json'
        with open(map_path, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, ensure_ascii=False, indent=1)
        print(f'Map: {map_path} (needed by latex_prose.py restore)')
        if args.legend:
            from latex_prose import legend
            with open(args.legend, 'w', encoding='utf-8') as f:
                f.write(legend(mapping))
            print(f'Legend: {args.legend}')
        if mapping['inputs']:
            print('Not followed (extract each of these files separately): '
                  + ', '.join(mapping['inputs']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
