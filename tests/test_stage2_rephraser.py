#!/usr/bin/env python3
"""
Unit Test Suite for the v8.0 Stage 2 rephraser scaffold.

The gate, generators, and loop are tested with the content-overlap fallback (no
heavy deps). The SBERT path is skip-guarded; Ollama is never contacted in tests.
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(ROOT, 'research', 'scripts'))
sys.path.insert(0, os.path.join(ROOT, 'skills', 'academic-humanizer', 'scripts'))

import stage2_rephraser as S

ORIG = "We recruited 12 participants and measured SUS scores, which improved from 54.5 to 88.5."
FAITHFUL = "We recruited 12 participants and measured SUS scores. These rose from 54.5 to 88.5."


class TestFidelityGate(unittest.TestCase):

    def setUp(self):
        self.gate = S.FidelityGate()

    def test_faithful_paraphrase_passes(self):
        ok, detail = self.gate.check(ORIG, FAITHFUL)
        self.assertTrue(ok, detail)

    def test_number_change_rejected(self):
        ok, detail = self.gate.check(ORIG, "We recruited participants and measured SUS from 54.5 to 88.5.")
        self.assertFalse(ok)
        self.assertIn('numbers changed', detail['reasons'])

    def test_term_change_rejected(self):
        bad = "We recruited 12 participants and measured usability scores, which rose from 54.5 to 88.5 overall."
        ok, detail = self.gate.check(ORIG, bad)
        self.assertFalse(ok)
        self.assertIn('terms/acronyms changed', detail['reasons'])

    def test_truncation_rejected(self):
        ok, detail = self.gate.check(ORIG, "We recruited 12 participants.")
        self.assertFalse(ok)

    def test_padding_rejected(self):
        padded = (ORIG + " " + "This result was observed consistently across every counterbalanced "
                  "session and cohort of the controlled laboratory study we conducted carefully.")
        ok, detail = self.gate.check(ORIG, padded)
        self.assertFalse(ok)
        self.assertTrue(any('length ratio' in r for r in detail['reasons']))

    def test_similarity_method_is_overlap_without_sbert(self):
        # When sentence-transformers is not installed, the method must be the overlap fallback.
        if S._sbert() is None:
            _, method = S.semantic_similarity(ORIG, FAITHFUL)
            self.assertEqual(method, 'overlap')


class TestGenerators(unittest.TestCase):

    def test_null_generator(self):
        self.assertEqual(S.NullGenerator().generate('hello world', 3), ['hello world'])

    def test_file_generator_returns_seeded(self):
        g = S.FileGenerator({'a b c': ['x y z', 'p q r']})
        self.assertEqual(g.generate('a b c', 4), ['x y z', 'p q r'])
        self.assertEqual(g.generate('unknown', 4), [])

    def test_file_generator_respects_n(self):
        g = S.FileGenerator({'a': ['1', '2', '3']})
        self.assertEqual(g.generate('a', 2), ['1', '2'])

    def test_from_aligned(self):
        g = S.FileGenerator.from_aligned(['base one', 'base two'], ['cand one', 'cand two'])
        self.assertEqual(g.generate('base two', 1), ['cand two'])


class TestRephraseLoop(unittest.TestCase):

    def setUp(self):
        self.gate = S.FidelityGate()

    def test_faithful_candidate_is_used(self):
        g = S.FileGenerator({ORIG: [FAITHFUL]})
        out, events = S.rephrase(ORIG, g, self.gate)
        self.assertEqual(events[0]['status'], 'rephrased')
        self.assertNotEqual(out.strip(), ORIG.strip())

    def test_unfaithful_candidate_falls_back(self):
        g = S.FileGenerator({ORIG: ["We recruited participants from 54.5 to 88.5."]})  # drops 12 + SUS
        out, events = S.rephrase(ORIG, g, self.gate)
        self.assertEqual(events[0]['status'], 'kept-original')
        self.assertEqual(out.strip(), ORIG.strip())

    def test_null_generator_is_passthrough(self):
        out, _ = S.rephrase(ORIG, S.NullGenerator(), self.gate)
        self.assertEqual(out.strip(), ORIG.strip())

    def test_paragraph_structure_preserved(self):
        doc = "First paragraph has 3 items here.\n\nSecond paragraph has 7 widgets."
        out, events = S.rephrase(doc, S.NullGenerator(), self.gate)
        self.assertEqual(out, doc)            # separators intact
        self.assertEqual(len(events), 2)      # one event per non-empty paragraph


class TestGateDocument(unittest.TestCase):

    def setUp(self):
        self.gate = S.FidelityGate()

    def test_aligned_faithful_draft_passes(self):
        base = ORIG + "\n\nThe system supports 4 locales."
        cand = FAITHFUL + "\n\nThe platform supports 4 locales."
        results = S.gate_document(base, cand, self.gate)
        self.assertTrue(all(r['passed'] for r in results), results)

    def test_paragraph_dropping_number_fails(self):
        base = ORIG + "\n\nThe system supports 4 locales."
        cand = FAITHFUL + "\n\nThe system supports many locales."  # drops 4
        results = S.gate_document(base, cand, self.gate)
        self.assertTrue(results[0]['passed'])
        self.assertFalse(results[1]['passed'])

    def test_missing_candidate_paragraph_fails(self):
        base = ORIG + "\n\nThe system supports 4 locales."
        results = S.gate_document(base, FAITHFUL, self.gate)   # candidate has only 1 paragraph
        self.assertFalse(results[1]['passed'])


@unittest.skipUnless(S._sbert() is not None, 'sentence-transformers not installed')
class TestSbertPath(unittest.TestCase):

    def test_sbert_similarity_high_for_paraphrase(self):
        sim, method = S.semantic_similarity(ORIG, FAITHFUL)
        self.assertEqual(method, 'sbert')
        self.assertGreater(sim, 0.8)


if __name__ == '__main__':
    unittest.main()
