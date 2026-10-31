#!/usr/bin/env python3
"""
Unit Test Suite for the v8.0 Stage 1 AST Clause Splitter (prototype).

Pure helpers (morphology, capitalization) are tested unconditionally. The
dependency-parse transforms need spaCy + en_core_web_sm; those tests skip when
the model is unavailable, the same way the LaTeX --compile test skips without
pdflatex.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(ROOT, 'research', 'scripts'))
sys.path.insert(0, os.path.join(ROOT, 'skills', 'academic-humanizer', 'scripts'))

import ast_clause_splitter as A

try:
    import spacy  # noqa: F401
    _NLP = A.load_nlp()
    HAVE_SPACY = True
except Exception:
    HAVE_SPACY = False
    _NLP = None


class TestPureHelpers(unittest.TestCase):

    def test_third_person_singular_regular(self):
        self.assertEqual(A._third_person_singular('reduce'), 'reduces')
        self.assertEqual(A._third_person_singular('yield'), 'yields')

    def test_third_person_singular_sibilants(self):
        self.assertEqual(A._third_person_singular('push'), 'pushes')
        self.assertEqual(A._third_person_singular('fix'), 'fixes')
        self.assertEqual(A._third_person_singular('go'), 'goes')

    def test_third_person_singular_y(self):
        self.assertEqual(A._third_person_singular('simplify'), 'simplifies')
        self.assertEqual(A._third_person_singular('play'), 'plays')   # vowel before y

    def test_third_person_singular_irregular(self):
        self.assertEqual(A._third_person_singular('be'), 'is')
        self.assertEqual(A._third_person_singular('have'), 'has')

    def test_capitalize_and_period(self):
        self.assertEqual(A._capitalize('the system ran'), 'The system ran')
        self.assertEqual(A._ensure_period('The system ran'), 'The system ran.')
        self.assertEqual(A._ensure_period('Done.'), 'Done.')


@unittest.skipUnless(HAVE_SPACY, 'spaCy + en_core_web_sm not installed')
class TestCoordinateSplit(unittest.TestCase):

    def _split(self, text, **kw):
        out, events = A.split_text(text, _NLP, **kw)
        return out, events

    def test_splits_independent_clauses(self):
        out, _ = self._split(
            'We evaluated the platform with twelve users, and the results confirmed that scores rose from 2.3 to 12.6.')
        self.assertIn('We evaluated the platform with twelve users.', out)
        self.assertIn('The results confirmed', out)

    def test_numbers_preserved(self):
        src = 'The time fell by 59.0% from 94.2 seconds to 38.6 seconds, and the score improved from 54.5 to 88.5.'
        out, _ = self._split(src)
        self.assertEqual(A.extract_numbers(src), A.extract_numbers(out))

    def test_noun_coordination_not_split(self):
        text = 'The model processes images and videos and audio streams in real time.'
        out, _ = self._split(text)
        self.assertEqual(out.strip(), text.strip())

    def test_shared_subject_vp_not_split(self):
        # "reduced X and improved Y" shares one subject -> no standalone right clause -> no split
        text = 'The redesigned system reduced the average task completion time and improved the satisfaction score.'
        out, _ = self._split(text)
        self.assertEqual(out.strip(), text.strip())

    def test_short_sentence_untouched(self):
        text = 'The system improved, and users were happy.'
        out, _ = self._split(text, max_words=16)
        self.assertEqual(out.strip(), text.strip())


@unittest.skipUnless(HAVE_SPACY, 'spaCy + en_core_web_sm not installed')
class TestParticipialSplit(unittest.TestCase):

    def test_participial_decoupling(self):
        text = ('The redesigned checkout interface reduced average task completion time across all cohorts, '
                'yielding higher conversion rates for the platform.')
        out, events = A.split_text(text, _NLP, participial=True)
        self.assertIn('This yields higher conversion rates', out)
        self.assertTrue(any(k == 'split-participial' for k, _, _ in events))

    def test_participial_off_by_default(self):
        text = ('The redesigned checkout interface reduced average task completion time across all cohorts, '
                'yielding higher conversion rates for the platform.')
        out, _ = A.split_text(text, _NLP, participial=False)
        self.assertNotIn('This yields', out)


@unittest.skipUnless(HAVE_SPACY, 'spaCy + en_core_web_sm not installed')
class TestFidelityGate(unittest.TestCase):

    def test_rejects_dropped_number(self):
        original = 'We recruited 12 users and 3 moderators for the study.'
        tampered = 'We recruited 12 users. We recruited moderators for the study.'
        self.assertFalse(A.is_faithful(original, tampered, _NLP))

    def test_rejects_dropped_content_word(self):
        original = 'The accessible interface improved contrast and the toolkit simplified navigation.'
        tampered = 'The interface improved contrast. The toolkit simplified navigation.'  # "accessible" dropped
        self.assertFalse(A.is_faithful(original, tampered, _NLP))

    def test_accepts_faithful_split(self):
        original = 'The interface improved contrast, and the toolkit simplified navigation across pages.'
        faithful = 'The interface improved contrast. The toolkit simplified navigation across pages.'
        self.assertTrue(A.is_faithful(original, faithful, _NLP))

    def test_rejects_fragment(self):
        # A bare participial clause with no subject is not well-formed.
        self.assertFalse(A.well_formed(_NLP('Yielding higher throughput for everyone.')))


if __name__ == '__main__':
    unittest.main()
