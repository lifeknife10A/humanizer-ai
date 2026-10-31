#!/usr/bin/env python3
"""Unit Test Suite for the Intake script (v7.15.0)"""

import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from types import SimpleNamespace

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(ROOT, 'skills', 'academic-humanizer', 'scripts'))
import ingest  # noqa: E402

SCRIPTS = os.path.join(ROOT, 'skills', 'academic-humanizer', 'scripts')

DOC_XML = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:r><w:t>Solid-state cells promise higher energy density.</w:t></w:r>
         <w:r><w:t> They also remove flammable solvents.</w:t></w:r></w:p>
    <w:p><w:r><w:t>Retention fell to 82.6% after 300 cycles at 25 &amp;deg;C.</w:t></w:r></w:p>
    <w:p/>
  </w:body>
</w:document>'''


def make_docx(xml=DOC_XML):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as zf:
        zf.writestr('[Content_Types].xml', '<Types/>')
        zf.writestr('word/document.xml', xml)
    return buf.getvalue()


class TestDocx(unittest.TestCase):

    def test_paragraphs_runs_and_entities(self):
        text = ingest.docx_text(make_docx())
        self.assertIn('Solid-state cells promise higher energy density. They also remove flammable solvents.', text)
        self.assertIn('82.6% after 300 cycles at 25 &deg;C.', text)
        self.assertIn('\n\n', text)  # paragraphs separated by a blank line

    def test_empty_paragraphs_are_dropped(self):
        text = ingest.docx_text(make_docx())
        self.assertEqual(text.count('\n\n'), 1)

    def test_bad_zip(self):
        with self.assertRaises(ValueError):
            ingest.docx_text(b'not a zip at all')

    def test_missing_document_xml(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w') as zf:
            zf.writestr('readme.txt', 'hello')
        with self.assertRaises(ValueError):
            ingest.docx_text(buf.getvalue())

    def test_no_text(self):
        with self.assertRaises(ValueError):
            ingest.docx_text(make_docx('<?xml version="1.0"?><w:document '
                                       'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                                       '<w:body><w:p/></w:body></w:document>'))


class TestDispatch(unittest.TestCase):

    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.dir)

    def write(self, name, data, mode='w'):
        path = os.path.join(self.dir, name)
        with open(path, mode, encoding=None if 'b' in mode else 'utf-8') as f:
            f.write(data)
        return path

    def test_txt_passes_through_unchanged(self):
        raw = 'First paragraph.\n\nSecond paragraph with 12 numbers.\n'
        text, mapping, problem = ingest.ingest(self.write('source.txt', raw))
        self.assertEqual(text, raw)
        self.assertIsNone(mapping)
        self.assertIsNone(problem)

    def test_docx_dispatches(self):
        text, mapping, _ = ingest.ingest(self.write('paper.DOCX', make_docx(), 'wb'))
        self.assertIn('Solid-state cells', text)

    def test_tex_dispatches_to_latex_prose(self):
        tex = '\\documentclass{article}\n\\begin{document}\n\\section{Intro}\nWe tested 12 samples.\n\\end{document}\n'
        text, mapping, _ = ingest.ingest(self.write('paper.tex', tex))
        self.assertIn('\u27e6', text)  # placeholders present
        self.assertIn('atoms', mapping)

    def test_unsupported_extension(self):
        _, _, problem = ingest.ingest(self.write('paper.html', '<p>hi</p>'))
        self.assertIn('unsupported format', problem)

    def test_pdf_without_pdftotext(self):
        text, _, problem = ingest.ingest(self.write('paper.pdf', b'%PDF-1.4 fake', 'wb'),
                                         which=lambda name: None)
        self.assertIsNone(text)
        self.assertIn('pdftotext is not installed', problem)

    def test_pdf_without_text_layer(self):
        fake = SimpleNamespace(returncode=0, stdout='\x0c', stderr='')
        text, _, problem = ingest.ingest(self.write('paper.pdf', b'%PDF-1.4 fake', 'wb'),
                                         which=lambda name: '/usr/bin/pdftotext',
                                         run=lambda *a, **k: fake)
        self.assertIsNone(text)
        self.assertIn('scanned PDF', problem)

    def test_pdf_layout_is_collapsed(self):
        fake = SimpleNamespace(returncode=0, stdout='Line   with    padding.\x0c', stderr='')
        text, _, _ = ingest.ingest(self.write('paper.pdf', b'%PDF-1.4 fake', 'wb'),
                                   which=lambda name: '/usr/bin/pdftotext',
                                   run=lambda *a, **k: fake)
        self.assertEqual(text, 'Line with padding.\n')


class TestCli(unittest.TestCase):

    def test_missing_file(self):
        r = subprocess.run([sys.executable, os.path.join(SCRIPTS, 'ingest.py'), 'no_such_file.txt'],
                           capture_output=True, text=True, cwd=SCRIPTS)
        self.assertEqual(r.returncode, 1)
        self.assertIn('No such file', r.stderr)

    def test_txt_round_trip(self):
        with tempfile.TemporaryDirectory() as d:
            src = os.path.join(d, 'in.txt')
            out = os.path.join(d, 'source.txt')
            with open(src, 'w', encoding='utf-8') as f:
                f.write('Cells cycled at 1.0 mA for fifty cycles.\n')
            r = subprocess.run([sys.executable, os.path.join(SCRIPTS, 'ingest.py'), src, '-o', out],
                               capture_output=True, text=True, cwd=SCRIPTS)
            self.assertEqual(r.returncode, 0, r.stderr)
            with open(out, encoding='utf-8') as f:
                self.assertEqual(f.read(), 'Cells cycled at 1.0 mA for fifty cycles.\n')

    def test_tex_writes_map(self):
        with tempfile.TemporaryDirectory() as d:
            src = os.path.join(d, 'paper.tex')
            out = os.path.join(d, 'source.txt')
            with open(src, 'w', encoding='utf-8') as f:
                f.write('\\documentclass{article}\n\\begin{document}\nWe tested 12 samples.\n\\end{document}\n')
            r = subprocess.run([sys.executable, os.path.join(SCRIPTS, 'ingest.py'), src, '-o', out],
                               capture_output=True, text=True, cwd=SCRIPTS)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue(os.path.exists(os.path.join(d, 'source.map.json')))

    def test_directory_ingest_finds_root_tex(self):
        with tempfile.TemporaryDirectory() as d:
            paper_tex = os.path.join(d, 'conference_paper.tex')
            notes_txt = os.path.join(d, 'readme.txt')
            with open(paper_tex, 'w', encoding='utf-8') as f:
                f.write('\\documentclass{IEEEtran}\n\\begin{document}\nWe report 95\\% gain.\n\\end{document}\n')
            with open(notes_txt, 'w', encoding='utf-8') as f:
                f.write('Some readme notes.\n')
            out = os.path.join(d, 'source.txt')
            r = subprocess.run([sys.executable, os.path.join(SCRIPTS, 'ingest.py'), d, '-o', out],
                               capture_output=True, text=True, cwd=SCRIPTS)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn('conference_paper.tex', r.stdout)
            with open(out, encoding='utf-8') as f:
                self.assertIn('We report 95% gain.', f.read())
            self.assertTrue(os.path.exists(os.path.join(d, 'source.map.json')))


if __name__ == '__main__':
    unittest.main()

