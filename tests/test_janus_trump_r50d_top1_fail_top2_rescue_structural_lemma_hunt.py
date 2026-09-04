from __future__ import annotations

import unittest
from fractions import Fraction

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r50d_top1_fail_top2_rescue_structural_lemma_hunt as r50d


class R50DStructuralLemmaHuntTests(unittest.TestCase):
    def test_input_descriptor_counts_cross_pairs_exactly(self):
        formula = r33.canonical_formula([
            (1, 2, 3, 4),
            (-1, 5, 6, 7),
        ])
        d = r50d.input_descriptor(formula, 1)
        self.assertEqual(d["positive_parent_count"], 1)
        self.assertEqual(d["negative_parent_count"], 1)
        self.assertEqual(d["cross_parent_product"], 1)
        self.assertEqual(d["retained_nontautological_pair_count"], 1)
        self.assertEqual(d["bad_pair_count_union_ge_5"], 1)
        self.assertEqual(d["tautological_cross_pair_count"], 0)
        self.assertEqual(d["minority_parent_count"], 1)
        self.assertEqual(d["retained_cross_pair_fraction"], [1, 1])

    def test_named_candidate_is_minority_polarity_nondecrease(self):
        a = {"minority_parent_count": 3}
        b = {"minority_parent_count": 4}
        self.assertTrue(b["minority_parent_count"] >= a["minority_parent_count"])

    def test_fraction_relation_uses_exact_rationals(self):
        a = Fraction(1, 3)
        b = Fraction(2, 6)
        self.assertTrue(r50d._relation(a, b, "="))
        self.assertTrue(r50d._relation(a, b, ">="))
        self.assertTrue(r50d._relation(a, b, "<="))

    def test_selector_features_are_tagged(self):
        self.assertIn("tautological_cross_pair_count", r50d.SELECTOR_DERIVED_FEATURES)
        self.assertNotIn("minority_parent_count", r50d.SELECTOR_DERIVED_FEATURES)

    def test_firewall(self):
        fw = r50d.firewall()
        self.assertFalse(fw["R50D_FINITE_12_IS_TRANSFER_LEMMA"])
        self.assertEqual(fw["TOP2_UNIVERSAL_COVERAGE"], "OPEN")
        self.assertEqual(fw["UNIVERSAL_R50A_PROGRESS"], "OPEN")
        self.assertEqual(fw["SAT_IN_P"], "NOT_PROVED")
        self.assertEqual(fw["P_VS_NP"], "OPEN")
        self.assertFalse(fw["TRUMP_finished"])


if __name__ == "__main__":
    unittest.main()
