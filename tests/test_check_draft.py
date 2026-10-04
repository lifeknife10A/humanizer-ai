#!/usr/bin/env python3
"""
Unit Test Suite for the Phase 2 Draft Checker (v6.3.0)
Validates fact extraction, fact-sheet enforcement, and style warnings.
"""

import unittest
import subprocess
import sys
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SCRIPTS = os.path.join(ROOT, 'skills', 'academic-humanizer', 'scripts')
sys.path.insert(0, SCRIPTS)
from check_draft import (
    extract_numbers,
    extract_terms,
    read_fact_sheet,
    defined_acronyms,
    segment,
    check,
)

BASELINE = os.path.join(ROOT, 'benchmarks', '00_baseline_raw_1037w_100pct_ai.txt')
BREAKTHROUGH = os.path.join(ROOT, 'benchmarks', '04_breakthrough_pass_587w_2_9pct_ai.txt')
MASTER = os.path.join(ROOT, 'benchmarks', '07_master_empirical_untruncated_952w.txt')

SOURCE = "Cells cycled at 1.0 mA cm⁻² for fifty cycles. Pellets were made by spark plasma sintering."


def kinds(result, level=None):
    return [f['kind'] for f in result['findings'] if level is None or f['level'] == level]


def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


class TestFactExtraction(unittest.TestCase):

    def test_digit_and_word_numbers(self):
        text = "After fifty cycles and three hundred hours, a five-nanometer layer held 3,860 mAh at 7.0 MPa for twenty-five days."
        self.assertEqual(extract_numbers(text), {'50', '300', '5', '3860', '7', '25'})

    def test_formula_and_unit_digits_ignored(self):
        text = "Li6.4La3Zr1.4Ta0.6O12 and Li₂CO₃ in mA cm-2 with K_IC in MPa m^{1/2} and cm⁻²."
        self.assertEqual(extract_numbers(text), set())

    def test_list_markers_are_not_numbers(self):
        text = "Four kinds: (1) syntactic, (2) semantic, (iii) jailbreak, and (b) multi-turn attacks at 87%."
        self.assertEqual(extract_numbers(text), {'4', '87'})

    def test_lone_one_is_not_a_quantity(self):
        self.assertEqual(extract_numbers("One of the cells failed."), set())
        self.assertEqual(extract_numbers("One hundred cells failed."), {'100'})

    def test_terms_are_acronyms_and_formulas(self):
        text = "LLZTO pellets, Li₂CO₃, ToF-SIMS and X-ray scans at 50 MPa with K⁻¹ units."
        self.assertEqual(extract_terms(text), {'LLZTO', 'Li₂CO₃', 'ToF', 'SIMS'})

    def test_acronyms_defined_at_first_use(self):
        text = ("We used electrochemical impedance spectroscopy (EIS) and time-of-flight secondary "
                "ion mass spectrometry (ToF-SIMS) on dense ceramic pellets (LLZTO).")
        self.assertEqual(defined_acronyms(text), {'EIS', 'ToF', 'SIMS'})

    def test_formula_does_not_define_acronym(self):
        self.assertEqual(defined_acronyms("dense ceramic Li₆.₄La₃Zr₁.₄Ta₀.₆O₁₂ (LLZTO) pellets"), set())
        self.assertEqual(defined_acronyms("dense ceramic Li6.4La3Zr1.4Ta0.6O12 (LLZTO) pellets"), set())

    def test_fact_sheet_comments_and_headings_ignored(self):
        sheet = "# Results 2024\n<!-- example: 25 °C -->\n- Cycling temperature: 30 °C"
        self.assertEqual(extract_numbers(read_fact_sheet(sheet)), {'30'})

    def test_abbreviations_do_not_split_sentences(self):
        sentences = segment("Smith et al. (2021) measured it. See Fig. 2 for details. Done.")
        self.assertEqual([s.text for s in sentences],
                         ["Smith et al. (2021) measured it.", "See Fig. 2 for details.", "Done."])

    def test_unpunctuated_single_line_is_heading(self):
        sentences = segment("Extended Abstract: A Title\n\nBody text here.")
        self.assertTrue(sentences[0].heading)
        self.assertFalse(sentences[1].heading)


class TestFactChecks(unittest.TestCase):

    def test_invented_number_fails(self):
        draft = "Cells cycled at 1.0 mA cm⁻² for fifty cycles at 25 °C. Pellets were made by spark plasma sintering."
        result = check(SOURCE, draft)
        self.assertFalse(result['passed'])
        self.assertIn('new-number', kinds(result, 'FAIL'))

    def test_fact_sheet_number_allowed(self):
        draft = "Cells cycled at 1.0 mA cm⁻² for fifty cycles at 25 °C. Pellets were made by spark plasma sintering."
        result = check(SOURCE, draft, facts="- Cycling temperature: 25 °C")
        self.assertTrue(result['passed'])
        self.assertEqual(result['fact_sheet_numbers_used'], ['25'])

    def test_dropped_number_fails(self):
        draft = "Cells cycled at 1.0 mA cm⁻² for many cycles. Pellets were made by spark plasma sintering."
        result = check(SOURCE, draft)
        self.assertIn('missing-number', kinds(result, 'FAIL'))

    def test_digits_and_words_interchangeable(self):
        draft = "Cells cycled at 1.0 mA cm⁻² for 50 cycles. Pellets were made by spark plasma sintering."
        self.assertTrue(check(SOURCE, draft)['passed'])

    def test_new_formula_warns_but_units_do_not(self):
        source = "Lithium lanthanum zirconium tantalum oxide pellets held 7.0 megapascals."
        draft = "Li₆.₄La₃Zr₁.₄Ta₀.₆O₁₂ pellets held 7.0 MPa of stack pressure here."
        result = check(source, draft)
        new_terms = [f['message'] for f in result['findings'] if f['kind'] == 'new-term']
        self.assertEqual(len(new_terms), 1)
        self.assertIn('Li₆.₄La₃Zr₁.₄Ta₀.₆O₁₂', new_terms[0])

    def test_defined_abbreviation_is_not_a_new_term(self):
        source = "Electrochemical impedance spectroscopy tracked resistance growth over time."
        draft = "Electrochemical impedance spectroscopy (EIS) tracked resistance growth. EIS ran over time."
        self.assertNotIn('new-term', kinds(check(source, draft)))

    def test_long_draft_note_depends_on_fact_sheet(self):
        source = "Pellets were sintered."
        padded = check(source, "The pellets were sintered in the usual way.")
        with_facts = check(source, "The pellets were sintered at 1150 °C.", facts="- 1150 °C")
        self.assertIn('cut filler', padded['findings'][0]['message'])
        self.assertIn('fact-sheet details were added', with_facts['findings'][0]['message'])

    def test_lost_hedge_warns(self):
        source = "Results suggest that larger models may resist attacks less often than expected here."
        hedged = "Results suggest larger models may resist attacks less often than expected here."
        firm = "Results show larger models resist attacks less than expected in these runs here."
        self.assertNotIn('hedge', kinds(check(source, hedged)))
        self.assertIn('hedge', kinds(check(source, firm)))

    def test_stronger_modal_warns(self):
        source = "Robustness should not be treated as an isolated problem by the field."
        draft = "Robustness must not be treated as an isolated problem by the field."
        self.assertIn('modal', kinds(check(source, draft)))

    def test_dropped_sentence_warns(self):
        source = ("Attention heads fail on ambiguous inputs. Output filters miss indirect requests. "
                  "We hope this work catalyzes community attention to reliable development.")
        draft = "Attention heads fail on ambiguous inputs. Output filters miss indirect requests."
        drops = [f for f in check(source, draft)['findings'] if f['kind'] == 'possible-drop']
        self.assertEqual(len(drops), 1)
        self.assertIn('catalyzes', drops[0]['text'])

    def test_truncation_fails(self):
        result = check(SOURCE, "Cells cycled at 1.0 mA cm⁻² for fifty cycles.")
        self.assertIn('retention', kinds(result, 'FAIL'))


class TestStyleChecks(unittest.TestCase):

    def test_style_warnings(self):
        draft = (
            "Furthermore, the voltage dropped; the cell failed. "
            "The reason is simple: voids grew. "
            "The pellets, however, cracked under load. "
            "The active boundary receded quickly, cutting contact area by half. "
            "We measured roughness, fracture, and conductivity. "
            "During cycling, voids grew. During cycling, voids grew. "
            "Robustness matters—specifically, against crafted inputs."
        )
        found = kinds(check(draft, draft))
        for kind in ('stock-phrase', 'semicolon', 'colon', 'em-dash', 'however',
                     'participial-tail', 'triad', 'duplicate', 'openings'):
            self.assertIn(kind, found)

    def test_add_on_endings_over_limit(self):
        draft = ("Voids form during stripping. Contact loss follows too. "
                 "Dendrites grow during plating. Cracks spread as well. "
                 "Resistance rises with cycling. Capacity fades alongside them.")
        self.assertEqual(kinds(check(draft, draft)).count('add-on'), 3)
        self.assertNotIn('add-on', kinds(check(draft, draft.replace(' as well.', '.'))))

    def test_connector_swaps_still_count_as_add_ons(self):
        sentences = [f"Cell {w} cracked, alongside the separator." for w in
                     ('alpha', 'beta', 'gamma', 'delta')]
        draft = ' '.join(sentences + ["Resistance rose during cycling.", "Contact was lost at the interface."])
        found = [f['message'] for f in check(draft, draft)['findings'] if f['kind'] == 'add-on']
        self.assertTrue(any('alongside' in m for m in found))

    def test_short_sentence_share(self):
        medium = "Interfacial resistance rose steadily across the first fifty cycles of testing."
        uniform = ' '.join([medium] * 10)
        self.assertIn('short-sentences', kinds(check(uniform, uniform)))
        varied = ' '.join([medium] * 8 + ["Resistance tripled.", "Coated cells survived."])
        self.assertNotIn('short-sentences', kinds(check(varied, varied)))

    def test_near_duplicate_warns(self):
        draft = ("Adversarial attacks on language models operate at the semantic level. Pixels differ. "
                 "In contrast, adversarial attacks on language models operate at the semantic level.")
        self.assertIn('duplicate', kinds(check(draft, draft)))

    def test_prepositional_comma_is_not_a_tail(self):
        draft = "Stack pressure stayed steady across all tests, during cycling and rest."
        self.assertNotIn('participial-tail', kinds(check(draft, draft)))

    def test_heading_colon_ignored(self):
        draft = "Extended Abstract: A Title\n\nBody text stays short here."
        self.assertNotIn('colon', kinds(check(draft, draft)))


class TestBenchmarks(unittest.TestCase):

    def test_master_benchmark_contains_unsourced_numbers(self):
        result = check(read(BASELINE), read(MASTER))
        invented = {f['message'].split('"')[1] for f in result['findings'] if f['kind'] == 'new-number'}
        self.assertTrue({'1150', '84', '600', '86.4'} <= invented)

    def test_breakthrough_benchmark_is_truncated(self):
        result = check(read(BASELINE), read(BREAKTHROUGH))
        self.assertIn('retention', kinds(result, 'FAIL'))

    def test_cli_exit_codes(self):
        script = os.path.join(SCRIPTS, 'check_draft.py')
        run = lambda *args: subprocess.run([sys.executable, script, *args], capture_output=True, text=True)
        self.assertEqual(run(BASELINE, BASELINE).returncode, 0)
        self.assertEqual(run(BASELINE, MASTER).returncode, 1)
        ledger = run(BASELINE)
        self.assertEqual(ledger.returncode, 0)
        self.assertIn('FACT LEDGER', ledger.stdout)


if __name__ == '__main__':
    unittest.main()
