from __future__ import annotations

import unittest

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r49i_bipolar_nontauto_cross_union_width5_core_hunt as r49i
import janus_trump_r50b_minimal_deadcore_structural_classification as r50b


class R50BStructuralClassificationTests(unittest.TestCase):
    def test_cross_pair_bad_width5_is_counted_exactly(self):
        formula = r33.canonical_formula([
            (1, 2, 3, 4),
            (-1, 5, 6, 7),
        ])
        p = r50b.cross_pair_profile(formula, 1)
        self.assertEqual(p["retained_nontautological_pair_count"], 1)
        self.assertEqual(p["bad_pair_count_union_ge_5"], 1)
        self.assertEqual(p["retained_union_size_histogram"], {"6": 1})
        self.assertEqual(p["first_bad_witness"]["union_size"], 6)

    def test_tautological_cross_pair_is_not_retained(self):
        formula = r33.canonical_formula([
            (1, 2, 3),
            (-1, -2, 4),
        ])
        p = r50b.cross_pair_profile(formula, 1)
        self.assertEqual(p["tautological_cross_pair_count"], 1)
        self.assertEqual(p["retained_nontautological_pair_count"], 0)
        self.assertEqual(p["bad_pair_count_union_ge_5"], 0)

    def test_cross_pair_measurement_matches_r49i_chi_definition(self):
        formula = r33.canonical_formula([
            (1, 2, 3, 4),
            (-1, 5, 6, 7),
            (1, 5, 8),
            (-1, 2, 9),
        ])
        exact = r50b.cross_pair_profile(formula, 1)
        profile = r49i.variable_profile(formula, 1)
        max_seen = max((int(k) for k, v in exact["retained_union_size_histogram"].items() if v), default=0)
        self.assertEqual(max_seen, profile["chi_star"])
        self.assertEqual(exact["retained_nontautological_pair_count"], profile["retained_nontautological_pair_count"])

    def test_r33_open_door_stops_deadcore_classification(self):
        formula = r33.canonical_formula([(1,), (2, 3)])
        c = r50b.classify_state(formula)
        self.assertNotEqual(c["r33_status"]["kind"], "STALL")
        self.assertTrue(c["covered_under_current_R50A_machine"])
        self.assertFalse(c["deadcore_under_current_R50A_machine"])
        self.assertFalse(c["r47j_scanned_all_current_variables"])

    def test_allowed_verdict_names_do_not_promote_theorem(self):
        allowed = {
            "REPLAYABLE_R50A_DEADCORE_FOUND",
            "FINITE_ASSIGNED_CORPUS_COVERED__STRUCTURAL_THEOREM_OPEN",
        }
        self.assertIn("FINITE_ASSIGNED_CORPUS_COVERED__STRUCTURAL_THEOREM_OPEN", allowed)
        self.assertNotIn("UNIVERSAL_R50A_PROGRESS_PROVED", allowed)
        self.assertNotIn("SAT_IN_P", allowed)


if __name__ == "__main__":
    unittest.main()
