from __future__ import annotations

import unittest

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r49m_r49k_obstruction_targeted_r47j_discharge as r49m
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

    def test_known_r49k_hard_core_is_classified_with_all_pivots(self):
        _, _, core = r49m.recreate_core()
        c = r50b.classify_state(core, {"kind": "UNIT_TEST_R49K_CORE"})
        self.assertEqual(c["r33_status"]["kind"], "STALL")
        self.assertEqual(c["direct_authorized_pivots"], [])
        self.assertTrue(c["r47j_scanned_all_current_variables"])
        self.assertEqual(len(c["r47j_rows"]), c["variable_count"])
        self.assertTrue(all(row["independent_replay_pass"] is True for row in c["r47j_rows"] if row["candidate"]))
        self.assertGreaterEqual(len(c["r47j_safe_pivots"]), 1)
        self.assertFalse(c["deadcore_under_current_R50A_machine"])
        self.assertTrue(c["every_current_variable_has_bad_pair"])
        self.assertGreaterEqual(c["total_bad_pair_count"], c["variable_count"])

    def test_r33_open_door_stops_deadcore_classification(self):
        formula = r33.canonical_formula([(1,), (2, 3)])
        c = r50b.classify_state(formula)
        self.assertNotEqual(c["r33_status"]["kind"], "STALL")
        self.assertTrue(c["covered_under_current_R50A_machine"])
        self.assertFalse(c["deadcore_under_current_R50A_machine"])
        self.assertFalse(c["r47j_scanned_all_current_variables"])

    def test_firewall_remains_open_on_single_root_shard(self):
        out = r50b.run(shard_index=0, shard_count=52)
        self.assertIn(out["verdict"], {
            "REPLAYABLE_R50A_DEADCORE_FOUND",
            "FINITE_ASSIGNED_CORPUS_COVERED__STRUCTURAL_THEOREM_OPEN",
        })
        self.assertFalse(out["firewall"]["FINITE_GREEN_IS_UNIVERSAL_COVERAGE"])
        self.assertEqual(out["firewall"]["UNIVERSAL_R50A_PROGRESS"], "OPEN")
        self.assertEqual(out["firewall"]["SAT_IN_P"], "NOT_PROVED")
        self.assertEqual(out["firewall"]["P_VS_NP"], "OPEN")
        self.assertFalse(out["firewall"]["TRUMP_finished"])


if __name__ == "__main__":
    unittest.main()
