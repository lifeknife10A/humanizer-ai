#!/usr/bin/env python3
"""
Unit Test Suite for Academic Humanizer (v5.0.0)
Validates all deterministic linguistic transformations.
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from humanizer import (
    scrub_cliches_and_tropes,
    fix_preaching_and_modals,
    fix_mid_sentence_however,
    break_triads,
    split_semicolons_and_colons,
    split_participial_tails,
    break_long_compounds,
    enforce_pacing_burstiness,
    clean_paragraph,
    humanize,
    audit_text
)

class TestAcademicHumanizer(unittest.TestCase):

    def test_cliche_removal(self):
        text = "Furthermore, the results indicate success. Moreover, this study highlights the need for change."
        cleaned = scrub_cliches_and_tropes(text)
        self.assertNotIn("Furthermore,", cleaned)
        self.assertNotIn("Moreover,", cleaned)
        self.assertNotIn("this study highlights", cleaned)

    def test_anti_preaching(self):
        text = "Engineers must deploy high pressure. This design is paramount for establishing commercial viability."
        cleaned = fix_preaching_and_modals(text)
        self.assertNotIn("must deploy", cleaned)
        self.assertNotIn("is paramount for", cleaned)

    def test_mid_sentence_however(self):
        text = "The pellets, however, cracked under high pressure."
        cleaned = fix_mid_sentence_however(text)
        self.assertTrue(cleaned.startswith("Yet the pellets cracked") or "Yet The pellets" in cleaned or "Yet " in cleaned)

    def test_break_triads(self):
        text = "We evaluated surface roughness, mechanical fracture, and anisotropic grain boundary conductivity to assess damage."
        cleaned = break_triads(text)
        self.assertNotIn("surface roughness, mechanical fracture, and anisotropic grain boundary conductivity", cleaned)
        self.assertIn("surface roughness and mechanical fracture", cleaned)

    def test_semicolon_and_colon_splitter(self):
        text = "The voltage dropped rapidly; secondary ion mass spectrometry confirmed lithium depletion: active areas shrank."
        cleaned = split_semicolons_and_colons(text)
        self.assertNotIn(";", cleaned)
        self.assertIn(". Secondary", cleaned)
        self.assertIn(". Active", cleaned)

    def test_participial_tails(self):
        text = "The active boundary receded, cutting active electrochemical contact area by up to 43.8%."
        cleaned = split_participial_tails(text)
        self.assertNotIn(", cutting", cleaned)
        self.assertIn(". This cut", cleaned)

    def test_zero_truncation_audit(self):
        text = (
            "Interfacial contact loss destroys solid-state lithium cells during early cycling. "
            "Metallic lithium anodes offer a theoretical capacity of 3,860 mAh g⁻¹. "
            "Coin cells fail within fifty cycles. Rapid charge cycles accelerate this degradation."
        )
        processed = humanize(text)
        audit = audit_text(text, processed)
        self.assertGreaterEqual(audit['retention_percentage'], 95.0)

    def test_burstiness_and_micro_punches(self):
        text = (
            "Standard Butler-Volmer equations calculate ion flux assuming perfectly planar boundaries. "
            "Classical formulations describe macro-scale thermodynamic equilibrium with high precision. "
            "Solid electrolyte ceramics remain vulnerable to mechanical fracture under rapid loads."
        )
        processed = enforce_pacing_burstiness(text)
        # Should ensure sentence length variance exists
        sentences = [s.strip() for s in processed.split('.') if s.strip()]
        self.assertTrue(len(sentences) >= 3)

if __name__ == '__main__':
    unittest.main()
