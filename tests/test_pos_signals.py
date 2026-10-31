#!/usr/bin/env python3
"""
Unit Test Suite for the POS Signal Prototype (v7.15.0)
Validates the pronoun, nominalization and passive proxies, their opt-in
warnings, and the integration through check_draft.check(pos_checks=...).
"""

import unittest
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SCRIPTS = os.path.join(ROOT, 'skills', 'academic-humanizer', 'scripts')
sys.path.insert(0, SCRIPTS)

import pos_signals as P
from check_draft import check


def kinds(result):
    return [f['kind'] for f in result['findings']]


class TestRates(unittest.TestCase):

    def test_pronoun_rate(self):
        # pronouns: they, it, we, this = 4; words = 6
        self.assertEqual(P.pronoun_rate("They measured it. We saw this."), round(4 / 6 * 100, 1))

    def test_pronoun_excludes_that(self):
        # "that" is not counted (relative/complementizer); only "it" here (7 words)
        self.assertEqual(P.pronoun_rate("The model that failed showed it clearly."), round(1 / 7 * 100, 1))

    def test_nominalization_rate(self):
        # evaluation, implementation, function = 3; words = 7
        self.assertEqual(P.nominalization_rate("The evaluation and implementation of the function."),
                         round(3 / 7 * 100, 1))

    def test_nominalization_stopword_excluded(self):
        # "moment" is a coincidental -ment word and is excluded; "tension" counts
        self.assertEqual(P.nominalization_rate("A moment of tension."), round(1 / 4 * 100, 1))

    def test_passive_share(self):
        sents = ["The sample was heated.", "We ran it quickly.", "Results are shown here."]
        self.assertEqual(P.passive_share(sents), round(2 / 3 * 100, 1))

    def test_passive_catches_irregular_participle(self):
        self.assertEqual(P.passive_share(["The data were given to the model."]), 100.0)

    def test_empty_inputs(self):
        self.assertEqual(P.pronoun_rate(""), 0.0)
        self.assertEqual(P.nominalization_rate(""), 0.0)
        self.assertEqual(P.passive_share([]), 0.0)


class TestWarnings(unittest.TestCase):

    def test_low_pronoun_warns(self):
        stats = {'pronoun_rate': 0.5, 'nominalization_rate': 5.0, 'passive_share': 20.0}
        self.assertEqual([k for k, _ in P.warnings(stats, 20)], ['pronoun'])

    def test_high_nominalization_warns(self):
        stats = {'pronoun_rate': 4.0, 'nominalization_rate': 15.0, 'passive_share': 20.0}
        self.assertEqual([k for k, _ in P.warnings(stats, 20)], ['nominalization'])

    def test_passive_never_warns(self):
        stats = {'pronoun_rate': 4.0, 'nominalization_rate': 5.0, 'passive_share': 0.0}
        self.assertEqual(P.warnings(stats, 20), [])

    def test_short_text_never_warns(self):
        stats = {'pronoun_rate': 0.0, 'nominalization_rate': 99.0, 'passive_share': 0.0}
        self.assertEqual(P.warnings(stats, 5), [])


class TestCheckIntegration(unittest.TestCase):

    STARVED = ("The optimization of the configuration requires evaluation of the implementation. ") * 12

    def test_pos_checks_off_by_default(self):
        found = kinds(check(self.STARVED, self.STARVED))
        self.assertNotIn('pronoun', found)
        self.assertNotIn('nominalization', found)

    def test_pos_checks_flag_enables_warnings(self):
        found = kinds(check(self.STARVED, self.STARVED, pos_checks=True))
        self.assertIn('pronoun', found)
        self.assertIn('nominalization', found)

    def test_stats_always_present(self):
        stats = check(self.STARVED, self.STARVED)['stats']
        for key in ('pronoun_rate', 'nominalization_rate', 'passive_share'):
            self.assertIn(key, stats)


if __name__ == '__main__':
    unittest.main()
