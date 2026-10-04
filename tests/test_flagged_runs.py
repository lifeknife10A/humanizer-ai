#!/usr/bin/env python3
"""
Unit Test Suite for the Phase 4 Detector-Feedback Helper (v7.10.0)
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(ROOT, 'skills', 'academic-humanizer', 'scripts'))
from check_draft import segment  # noqa: E402
from flagged_runs import find_runs, match_flags, report  # noqa: E402

DRAFT = ("Attacks operate at the semantic level. Image classifiers differ. Syntactic attacks manipulate structure. "
         "Semantic attacks exploit reasoning gaps. Robustness varies. Models were particularly vulnerable.\n\n"
         "Our method reaches 87% robustness. Baseline filtering reaches 42%.")


class TestFlaggedRuns(unittest.TestCase):

    def setUp(self):
        self.sentences = [s for s in segment(DRAFT) if not s.heading]

    def test_prefix_matching_ignores_case_and_punctuation(self):
        flags, unmatched = match_flags(self.sentences, ["syntactic attacks manipulate", "OUR METHOD REACHES 87%"])
        self.assertEqual([i for i, f in enumerate(flags) if f], [2, 6])
        self.assertEqual(unmatched, [])

    def test_unmatched_lines_are_reported(self):
        _, unmatched = match_flags(self.sentences, ["this sentence is not in the draft"])
        self.assertEqual(len(unmatched), 1)

    def test_runs_bridge_one_gap_within_a_paragraph(self):
        flags, _ = match_flags(self.sentences, ["Syntactic attacks manipulate", "Robustness varies",
                                               "Models were particularly"])
        self.assertEqual(find_runs(self.sentences, flags), [[2, 3, 4, 5]])

    def test_runs_do_not_cross_paragraphs(self):
        flags, _ = match_flags(self.sentences, ["Models were particularly", "Our method reaches"])
        self.assertEqual(find_runs(self.sentences, flags), [[5], [6]])

    def test_headings_and_formulas_are_rewritable_but_title_is_not(self):
        from flagged_runs import rewritable_units
        text = "Title: A Paper\n\n2. Forecasting Methods\n\nModels learn patterns.\nP = 0.5 * A * v^3\nThat is all."
        units = [u.text for u in rewritable_units(text)]
        self.assertNotIn('Title: A Paper', units)
        self.assertIn('2. Forecasting Methods', units)
        self.assertIn('P = 0.5 * A * v^3', units)

    def test_report_estimates_share(self):
        text = report(DRAFT, ["Our method reaches", "Baseline filtering reaches"])
        self.assertIn('Flagged sentences: 2 of 8', text)
        self.assertIn('Runs to rewrite: 1', text)


if __name__ == '__main__':
    unittest.main()
