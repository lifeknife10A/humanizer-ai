#!/usr/bin/env python3
"""
Unit Test Suite for the v8.0 ablation harness.

Transforms that need no parse (paren_isolation), the variant-spec logic, and the
number-fidelity gate are tested unconditionally. The spaCy-dependent transforms
and the end-to-end run skip when spaCy/en_core_web_sm is unavailable, matching
the pdflatex-skip convention.
"""

import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(ROOT, 'research', 'scripts'))
sys.path.insert(0, os.path.join(ROOT, 'skills', 'academic-humanizer', 'scripts'))

import ablation_harness as H

try:
    import spacy  # noqa: F401
    _NLP = H.ACS.load_nlp()
    HAVE_SPACY = True
except Exception:
    HAVE_SPACY = False
    _NLP = None


class TestParenIsolation(unittest.TestCase):

    def test_splits_multistat_parenthetical(self):
        out, n = H.t_paren_isolation('Time fell (t(11) = 13.42, p < 0.001) overall.')
        self.assertEqual(out, 'Time fell (t(11) = 13.42) (p < 0.001) overall.')
        self.assertEqual(n, 1)

    def test_single_stat_unchanged(self):
        out, n = H.t_paren_isolation('Density rose (98% relative) here.')
        self.assertEqual(n, 0)
        self.assertIn('(98% relative)', out)

    def test_thousands_comma_not_split(self):
        # "3,860" has no space after the comma, so it must not be split.
        out, n = H.t_paren_isolation('Capacity reached (3,860 mAh) at peak.')
        self.assertEqual(n, 0)
        self.assertIn('(3,860 mAh)', out)


class TestVariantSpecs(unittest.TestCase):

    def test_single_mode(self):
        specs = H.variant_specs('single')
        ids = [vid for vid, _ in specs]
        self.assertEqual(ids[0], 'baseline')
        self.assertEqual(len(specs), 1 + len(H.TRANSFORMS))
        # each non-baseline variant turns on exactly one transform
        for vid, flags in specs[1:]:
            self.assertEqual(sum(flags.values()), 1)

    def test_all_mode(self):
        specs = H.variant_specs('all')
        self.assertEqual([v for v, _ in specs], ['baseline', 'all'])
        self.assertTrue(all(specs[1][1].values()))

    def test_leave_one_out_mode(self):
        specs = H.variant_specs('leave-one-out')
        ids = [vid for vid, _ in specs]
        self.assertEqual(ids[:2], ['baseline', 'all'])
        self.assertEqual(len(specs), 2 + len(H.TRANSFORMS))
        for vid, flags in specs[2:]:
            self.assertEqual(sum(flags.values()), len(H.TRANSFORMS) - 1)

    def test_bad_mode(self):
        with self.assertRaises(ValueError):
            H.variant_specs('nope')


class TestFidelityGate(unittest.TestCase):

    def test_identical_text_passes(self):
        src = 'We recruited 12 users and measured 3 metrics across the study.'
        self.assertTrue(H.fidelity(src, src)['numbers_ok'])

    def test_dropped_number_fails(self):
        src = 'We recruited 12 users and measured 3 metrics across the study.'
        variant = 'We recruited 12 users across the study.'   # drops 3
        fid = H.fidelity(src, variant)
        self.assertFalse(fid['numbers_ok'])
        self.assertTrue(fid['missing_numbers'])

    def test_apply_no_flags_is_noop(self):
        text = 'The system works well today.'
        out, counts = H.apply_transforms(text, {t: False for t in H.TRANSFORMS}, None)
        self.assertEqual(out, text)
        self.assertEqual(counts, {})


@unittest.skipUnless(HAVE_SPACY, 'spaCy + en_core_web_sm not installed')
class TestSpacyTransforms(unittest.TestCase):

    def test_demonstrative_chain(self):
        text = 'The team ran the study. The redesigned interface reduced the average completion time.'
        out, n = H.t_demonstrative_chain(text, _NLP)
        self.assertIn('This reduced the average completion time.', out)
        self.assertGreaterEqual(n, 1)

    def test_demonstrative_chain_skips_first_sentence(self):
        text = 'The redesigned interface reduced the average completion time for everyone.'
        out, n = H.t_demonstrative_chain(text, _NLP)
        self.assertEqual(n, 0)   # only sentence in the paragraph has no antecedent

    def test_lexical_repeat_distributes_adjective(self):
        text = 'The sessions revealed poor feedback and filtering across the storefront.'
        out, n = H.t_lexical_repeat(text, _NLP)
        self.assertIn('poor feedback and poor filtering', out)
        self.assertEqual(n, 1)

    def test_voice_alternation_converts_simple_clause(self):
        text = 'The team reduced the average task completion time across the cohorts.'
        out, n = H.t_voice_alternation(text, _NLP)
        self.assertIn('was reduced', out)
        self.assertEqual(n, 1)

    def test_voice_alternation_skips_coordinate_sentence(self):
        text = 'We conducted the study, and the sessions revealed clear gaps.'
        out, n = H.t_voice_alternation(text, _NLP)
        self.assertEqual(n, 0)
        self.assertEqual(out.strip(), text.strip())


@unittest.skipUnless(HAVE_SPACY, 'spaCy + en_core_web_sm not installed')
class TestEndToEnd(unittest.TestCase):

    BASELINE = ('We conducted empathy mapping with twelve participants, and the sessions revealed gaps. '
                'The redesigned interface reduced task completion time by 59.0% to 38.6 seconds '
                '(t(11) = 13.42, p < 0.001).')

    def test_run_writes_manifest_and_variants(self):
        with tempfile.TemporaryDirectory() as d:
            manifest = H.run(self.BASELINE, 'single', d, _NLP)
            self.assertTrue(os.path.exists(os.path.join(d, 'manifest.json')))
            self.assertTrue(os.path.exists(os.path.join(d, 'report.md')))
            on_disk = json.load(open(os.path.join(d, 'manifest.json')))
            self.assertEqual(len(on_disk['variants']), 1 + len(H.TRANSFORMS))
            for v in manifest['variants']:
                self.assertTrue(os.path.exists(os.path.join(d, v['file'])))

    def test_all_variants_preserve_numbers(self):
        with tempfile.TemporaryDirectory() as d:
            manifest = H.run(self.BASELINE, 'single', d, _NLP)
            for v in manifest['variants']:
                self.assertTrue(v['numbers_ok'], f"{v['id']} dropped/invented a number: "
                                f"{v['new_numbers']} {v['missing_numbers']}")


if __name__ == '__main__':
    unittest.main()
