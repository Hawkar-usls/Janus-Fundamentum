from __future__ import annotations

import json
import unittest
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r50c_top2_min_taut_prospective_falsifier as r50c


class R50CTop2ProspectiveTests(unittest.TestCase):
    def test_ranker_uses_taut_count_then_var_only(self):
        geometry = [
            {"var": 9, "tautological_cross_pair_count": 3},
            {"var": 4, "tautological_cross_pair_count": 1},
            {"var": 8, "tautological_cross_pair_count": 1},
            {"var": 2, "tautological_cross_pair_count": 4},
        ]
        top2, ordered = r50c.rank_top2_geometry_rows(geometry)
        self.assertEqual([x["var"] for x in ordered], [4, 8, 9, 2])
        self.assertEqual([x["var"] for x in top2], [4, 8])

    def test_ranker_ignores_outcome_like_extra_fields(self):
        a = [
            {"var": 5, "tautological_cross_pair_count": 2, "width4_safe": False},
            {"var": 7, "tautological_cross_pair_count": 1, "width4_safe": False},
            {"var": 3, "tautological_cross_pair_count": 1, "width4_safe": True},
        ]
        b = [
            {**row, "width4_safe": not row["width4_safe"]}
            for row in a
        ]
        top_a, _ = r50c.rank_top2_geometry_rows(a)
        top_b, _ = r50c.rank_top2_geometry_rows(b)
        self.assertEqual([x["var"] for x in top_a], [3, 7])
        self.assertEqual([x["var"] for x in top_b], [3, 7])

    def test_r33_open_state_is_not_hard_probe(self):
        formula = r33.canonical_formula([(1,), (2, 3)])
        probe = r50c.hard_state_probe(formula)
        self.assertFalse(probe["applicable"])
        self.assertEqual(probe["reason"], "R33_OPEN")

    def test_prereg_is_prospective_and_fail_closed(self):
        p = Path("research/JANUS_TRUMP_R50C_TOP2_MIN_TAUTO_PROSPECTIVE_FALSIFIER_PREREGISTRATION_2026-09-04.json")
        d = json.loads(p.read_text())
        self.assertEqual(d["status"], "FROZEN_BEFORE_EXECUTION")
        self.assertEqual(d["frozen_selector"]["k"], 2)
        self.assertEqual(d["prospective_corpus"]["prospective_frontier_ordinals"], "65_THROUGH_256")
        self.assertTrue(d["prospective_corpus"]["exclude_all_R49I_52_discovery_root_hashes"])
        self.assertFalse(d["firewall"]["DISCOVERY_CORPUS_REUSE_FOR_ACCEPTANCE"])
        self.assertEqual(d["firewall"]["SAT_IN_P"], "NOT_PROVED")
        self.assertEqual(d["firewall"]["P_VS_NP"], "OPEN")
        self.assertFalse(d["firewall"]["TRUMP_finished"])


if __name__ == "__main__":
    unittest.main()
