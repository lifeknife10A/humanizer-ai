#!/usr/bin/env python3
"""
Unit Test Suite for the LaTeX Prose Extractor (v7.13.1)
"""

import os
import re
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(ROOT, 'skills', 'academic-humanizer', 'scripts'))
from latex_prose import PlaceholderError, compile_tex, extract, restore, verify  # noqa: E402

TEX = r"""\documentclass{article}
\usepackage{amsmath,amssymb}
\begin{document}

\title{Safe Routing in Microservices}
\maketitle

\begin{abstract}
Routing creates a conflict
between latency and correctness. We report 88.7\% accuracy---a clear gain.
\end{abstract}

\section{Introduction}\label{sec:intro}
Services scale on their own~\cite{gan2019}. % check this
The state vector $s_t \in \mathbb{R}^{n}$ evolves as
\begin{equation}
s_{t+1} = A s_t, \quad t = 1, 2, 3
\end{equation}
where $A$ is fixed. We use a \emph{hard action mask} and ``three'' rules.

\begin{itemize}
\item A capability map.
\item A learned policy\footnote{Trained on 10--20 traces.}.
\end{itemize}
\end{document}
"""


def token(view, latex_fragment, mapping):
    """The placeholder whose LaTeX contains the fragment."""
    for n, text in mapping['atoms'].items():
        if latex_fragment in text:
            return f'\u27e6{n}\u27e7'
    raise AssertionError(latex_fragment)


class TestLatexProse(unittest.TestCase):

    def setUp(self):
        self.view, self.map = extract(TEX)

    def test_view_hides_latex_and_converts_escapes(self):
        self.assertNotIn('\\', self.view)
        self.assertNotIn('$', self.view)
        self.assertIn('We report 88.7% accuracy\u2014a clear gain.', self.view)
        self.assertIn('\u201cthree\u201d rules', self.view)
        self.assertIn('Trained on 10\u201320 traces.', self.view)
        self.assertIn('Routing creates a conflict between latency', self.view)   # line break unwrapped
        self.assertTrue(any(v.startswith('~\\cite') for v in self.map['atoms'].values()))
        self.assertTrue(any(v == '% check this\n' for v in self.map['atoms'].values()))
        self.assertTrue(any(v.startswith('\\begin{equation}') for v in self.map['atoms'].values()))
        self.assertEqual(len(self.map['headings']), 1)
        self.assertIn('\\documentclass{article}', self.map['head'])
        self.assertEqual(self.map['tail'], '\\end{document}\n')

    def test_headings_and_paired_commands_keep_their_text_editable(self):
        self.assertRegex(self.view, '\u27e6(\\d+)\u27e7Introduction\u27e6/\\1\u27e7')
        self.assertRegex(self.view, '\u27e6(\\d+)\u27e7hard action mask\u27e6/\\1\u27e7')
        self.assertRegex(self.view, '\n\n\u27e6\\d+\u27e7 A capability map.')

    def test_unchanged_view_restores_byte_for_byte(self):
        self.assertEqual(restore(self.view, self.map), TEX)

    def test_rewritten_prose_is_escaped_and_latex_kept(self):
        view = self.view.replace('Services scale on their own', 'Each service scales by itself, 50% & more')
        view = view.replace('Introduction', 'Why routing needs guards')
        tex = restore(view, self.map)
        self.assertIn('Each service scales by itself, 50\\% \\& more~\\cite{gan2019}.', tex)
        self.assertIn('\\section{Why routing needs guards}\\label{sec:intro}', tex)
        self.assertIn('\\begin{equation}\ns_{t+1} = A s_t, \\quad t = 1, 2, 3\n\\end{equation}', tex)
        self.assertEqual(verify(self.map, tex), [])

    def test_untouched_paragraphs_stay_byte_for_byte_when_others_change(self):
        view = self.view.replace('Services scale on their own', 'Services scale alone')
        tex = restore(view, self.map)
        self.assertIn('Routing creates a conflict\nbetween latency and correctness. We report 88.7\\% '
                      'accuracy---a clear gain.', tex)

    def test_missing_duplicated_or_invented_placeholders_are_refused(self):
        cite = token(self.view, '\\cite{gan2019}', self.map)
        for broken, message in ((self.view.replace(cite, ''), 'is missing'),
                                (self.view.replace(cite, cite + ' ' + cite), 'appears 2 times'),
                                (self.view + ' \u27e699\u27e7', 'not in the map')):
            with self.assertRaises(PlaceholderError) as e:
                restore(broken, self.map)
            self.assertIn(message, str(e.exception))

    def test_latex_typed_into_the_prose_is_refused(self):
        with self.assertRaises(PlaceholderError) as e:
            restore(self.view.replace('Services scale', 'Services \\textbf{scale}'), self.map)
        self.assertIn('Write no LaTeX', str(e.exception))

    def test_pairs_must_stay_nested_and_on_one_line(self):
        m = re.search('\u27e6(\\d+)\u27e7hard action mask\u27e6/(\\d+)\u27e7', self.view)
        n = m.group(1)
        swapped = self.view.replace(m.group(0), f'\u27e6/{n}\u27e7hard action mask\u27e6{n}\u27e7')
        with self.assertRaises(PlaceholderError) as e:
            restore(swapped, self.map)
        self.assertIn('pairs must nest', str(e.exception))
        heading = re.search('\u27e6(\\d+)\u27e7Introduction', self.view).group(0)
        with self.assertRaises(PlaceholderError) as e:
            restore(self.view.replace(heading, heading.replace('Introduction', 'Intro\nduction')), self.map)
        self.assertIn('spans several lines', str(e.exception))

    def test_file_without_document_environment_is_all_body(self):
        view, mapping = extract('Some prose with a citation~\\cite{x}.\n')
        self.assertEqual((mapping['head'], mapping['tail']), ('', ''))
        self.assertEqual(restore(view, mapping), 'Some prose with a citation~\\cite{x}.\n')

    @unittest.skipUnless(shutil.which('pdflatex'), 'pdflatex not installed')
    def test_restored_file_compiles(self):
        tex = restore(self.view.replace('Services scale on their own', 'Each service scales alone, 50% of it'),
                      self.map)
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, 'paper.tex')
            with open(path, 'w') as f:
                f.write(tex)
            ok, message = compile_tex(path)
            self.assertTrue(ok, message)
            self.assertTrue(os.path.exists(os.path.join(d, 'paper.pdf')))


class TestPlaceholdersInTheOtherTools(unittest.TestCase):

    def setUp(self):
        self.view, self.map = extract(TEX)

    def test_checker_fails_on_lost_placeholder_and_ignores_latex_numbers(self):
        from check_draft import check
        self.assertTrue(check(self.view, self.view)['passed'])
        cite = token(self.view, '\\cite{gan2019}', self.map)
        result = check(self.view, self.view.replace(cite, ''))
        self.assertFalse(result['passed'])
        self.assertTrue(any(f['kind'] == 'placeholder' for f in result['findings']))
        numbers = {f['message'] for f in result['findings'] if f['kind'] == 'missing-number'}
        self.assertEqual(numbers, set())   # 1, 2, 3 live inside the equation, the 7 of a placeholder is not a number

    def test_pdf_highlights_match_sentences_with_placeholders(self):
        from check_draft import segment
        from flagged_runs import match_flags
        sentences = segment(self.view)
        flags, unmatched = match_flags(sentences, ['The state vector st ∈ Rn evolves as',
                                                    'Services scale on their own [1].',
                                                    'I. INTRODUCTION'])
        self.assertEqual(unmatched, [])
        flagged = [s.text for s, f in zip(sentences, flags) if f]
        self.assertTrue(any('The state vector' in t for t in flagged))
        self.assertEqual(len(flagged), 3)
        self.assertTrue(any('Services scale on their own' in t for t in flagged))
        self.assertTrue(any('Introduction' in t for t in flagged))

    def test_splicer_blocks_a_rewrite_that_drops_a_placeholder(self):
        from apply_runs import format_review, parse_runs, placeholder_run_changes
        from flagged_runs import runs_file
        text = runs_file(self.view, ['Services scale on their own'])
        cite = token(self.view, '\\cite{gan2019}', self.map)
        runs = parse_runs(text.replace('REWRITE:\n', 'REWRITE:\nEach service scales by itself.\n', 1))
        problems = placeholder_run_changes(runs)
        self.assertTrue(any(cite in p and 'missing' in p for p in problems))
        self.assertIn('REVISE', format_review([], [], [], [], runs=runs, placeholders=problems))


if __name__ == '__main__':
    unittest.main()
