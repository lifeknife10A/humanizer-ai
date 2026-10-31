#!/usr/bin/env python3
"""
Unit Test Suite for the v8.0 register-lowering lexicon (no spaCy needed).
Verifies the swaps fire, capitalization is preserved, multi-word phrases work,
and numbers/acronyms are never touched (number fidelity via check_draft).
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(ROOT, 'research', 'scripts'))
sys.path.insert(0, os.path.join(ROOT, 'skills', 'academic-humanizer', 'scripts'))

import register_lexicon as RL
from check_draft import extract_numbers, extract_terms


class TestRegisterLexicon(unittest.TestCase):

    def test_basic_swaps(self):
        out, n = RL.lower_register('We utilize numerous methods here.')
        self.assertEqual(out, 'We use many methods here.')
        self.assertEqual(n, 2)

    def test_capitalization_preserved(self):
        self.assertEqual(RL.lower_register('Utilize the tool.')[0], 'Use the tool.')
        self.assertEqual(RL.lower_register('Numerous trials ran.')[0], 'Many trials ran.')

    def test_multiword_phrases(self):
        self.assertEqual(RL.lower_register('We did it in order to win.')[0], 'We did it to win.')
        self.assertEqual(RL.lower_register('It failed due to the fact that time ran out.')[0],
                         'It failed because time ran out.')
        self.assertEqual(RL.lower_register('The majority of users agreed.')[0], 'Most users agreed.')

    def test_word_boundary_no_partial_match(self):
        # "induce" must not fire inside "inducement"
        self.assertEqual(RL.lower_register('The inducement was large.')[1], 0)

    def test_numbers_untouched(self):
        src = 'We utilized 12 models and ran 3 trials at 59.0% load.'
        out, _ = RL.lower_register(src)
        self.assertIn('used 12 models', out)
        self.assertEqual(extract_numbers(src), extract_numbers(out))

    def test_acronyms_untouched(self):
        src = 'The API utilizes HCI methods and WCAG rules.'
        out, _ = RL.lower_register(src)
        self.assertIn('The API uses HCI methods', out)
        self.assertEqual(extract_terms(src), extract_terms(out))

    def test_ecommerce_register(self):
        out, _ = RL.lower_register('Digital apparel storefronts induce friction.')
        self.assertEqual(out, 'Digital clothing websites cause friction.')

    def test_no_match_is_noop(self):
        text = 'The system works well today.'
        self.assertEqual(RL.lower_register(text), (text, 0))


if __name__ == '__main__':
    unittest.main()
