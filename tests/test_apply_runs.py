#!/usr/bin/env python3
"""
Unit Test Suite for the Phase 4 Splicer (v7.3.0)
"""

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(ROOT, 'skills', 'academic-humanizer', 'scripts'))
from apply_runs import parse_runs, splice  # noqa: E402
from flagged_runs import runs_file  # noqa: E402

DRAFT = ("Title Line\n\n"
         "Attacks operate at the semantic level. Image classifiers differ. Syntactic attacks manipulate structure.\n"
         "Semantic attacks exploit reasoning gaps. Robustness varies.\n\n"
         "Our method reaches 87% robustness. Baseline filtering reaches 42%.")


def fill(runs_text, rewrites):
    parts = runs_text.split('REWRITE:\n')
    out = parts[0]
    for rewrite, part in zip(rewrites, parts[1:]):
        out += 'REWRITE:\n' + rewrite + '\n' + part
    return out


class TestApplyRuns(unittest.TestCase):

    def test_round_trip_changes_only_the_run(self):
        text = runs_file(DRAFT, ["Syntactic attacks manipulate", "Semantic attacks exploit"])
        new, applied, errors = splice(DRAFT, parse_runs(fill(text, ["We sorted the attacks by what they target."])))
        self.assertEqual(errors, [])
        self.assertEqual(applied, [1])
        self.assertEqual(new, DRAFT.replace(
            "Syntactic attacks manipulate structure.\nSemantic attacks exploit reasoning gaps.",
            "We sorted the attacks by what they target."))

    def test_empty_rewrite_keeps_run(self):
        text = runs_file(DRAFT, ["Our method reaches"])
        new, applied, errors = splice(DRAFT, parse_runs(text))
        self.assertEqual((new, applied, errors), (DRAFT, [], []))

    def test_multiline_rewrite_is_joined(self):
        text = runs_file(DRAFT, ["Our method reaches"])
        new, _, _ = splice(DRAFT, parse_runs(fill(text, ["We reached 87% robustness.\nThat beat the baseline."])))
        self.assertIn("We reached 87% robustness. That beat the baseline. Baseline filtering", new)

    def test_review_flags_copied_sentences_and_sorts_warnings(self):
        from apply_runs import review_runs
        from check_draft import check
        text = runs_file(DRAFT, ["Syntactic attacks manipulate", "Semantic attacks exploit"])
        runs = parse_runs(fill(text, ["Syntactic attacks manipulate structure. Furthermore, we sorted them; it helped."]))
        new, _, _ = splice(DRAFT, runs)
        inside, outside, general, copied = review_runs(runs, check(DRAFT, new))
        self.assertEqual([(n, s) for n, s, _ in copied], [(1, 'Syntactic attacks manipulate structure.')])
        self.assertTrue({'stock-phrase', 'semicolon'} <= {f['kind'] for f in inside})

    def test_lost_hedge_blocks_ready(self):
        from apply_runs import hedge_changes
        self.assertEqual(hedge_changes("They may also require new methods.", "We need new methods."),
                         ['possibility hedges went from 1 to 0'])
        self.assertEqual(hedge_changes("Teams should coordinate.", "Teams must coordinate."), ['a "must" was added'])
        self.assertEqual(hedge_changes("It may fail.", "Failure may follow."), [])

    def test_near_copy_counts_as_barely_changed(self):
        from apply_runs import review_runs
        from check_draft import check
        runs = [(1, "Syntactic attacks change linguistic structure while preserving surface semantics.",
                 "Syntactic attacks change linguistic structure while keeping surface semantics.")]
        _, _, _, copied = review_runs(runs, check(DRAFT, DRAFT))
        self.assertEqual(len(copied), 1)

    def test_edited_original_is_rejected(self):
        runs = [(1, "This sentence is not in the draft.", "Replacement.")]
        new, applied, errors = splice(DRAFT, runs)
        self.assertEqual(new, DRAFT)
        self.assertTrue(errors and 'found 0 times' in errors[0])

    def test_context_lines_are_not_part_of_original(self):
        text = runs_file(DRAFT, ["Image classifiers differ"])
        self.assertIn('CONTEXT BEFORE: Attacks operate', text)
        (_, original, _), = parse_runs(text)
        self.assertEqual(original, "Image classifiers differ.")


if __name__ == '__main__':
    unittest.main()
