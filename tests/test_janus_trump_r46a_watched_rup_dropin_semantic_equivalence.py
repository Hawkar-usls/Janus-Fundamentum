from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r35b_single_literal_rup_vivification as r35b
import janus_trump_r46a_watched_rup_dropin_semantic_equivalence as r46a


class R46AWatchedRUPTests(unittest.TestCase):
    def check_up(self, clauses, assumptions=()):
        formula = r33.canonical_formula(clauses)
        watched = r46a.watched_unit_propagation_trace(formula, assumptions)
        independent = r35b.independent_up_conflict_checker(formula, assumptions)
        self.assertEqual(bool(watched["conflict"]), bool(independent))
        return watched

    def test_empty_clause(self):
        self.assertTrue(self.check_up([()])["conflict"])

    def test_unit_chain(self):
        self.assertFalse(self.check_up([(1,), (-1, 2), (-2, 3)])["conflict"])

    def test_assumption_contradiction(self):
        self.assertTrue(self.check_up([(1, 2)], (1, -1))["conflict"])

    def test_watch_replacement_then_conflict(self):
        out = self.check_up([(1, 2, 3), (-1,), (-2,), (-3,)])
        self.assertTrue(out["conflict"])
        self.assertGreaterEqual(out["watch_clause_touches"], 1)

    def test_long_implication_chain_conflict(self):
        self.assertTrue(self.check_up([(1,), (-1, 2), (-2, 3), (-3, 4), (-4,)] )["conflict"])

    def test_candidate_normalized_semantics_small(self):
        formula = r33.canonical_formula([(1, 2), (-1, 2), (1, -2)])
        legacy = r35b.run_candidate(formula)
        watched = r46a.run_candidate_watched(formula)
        self.assertEqual(r46a.normalized(legacy), r46a.normalized(watched))
        self.assertTrue(r35b.independent_certificate_replay(formula, watched)["pass"])

    def test_microtest_bundle(self):
        self.assertTrue(all(x["pass"] for x in r46a.microtests().values()))


if __name__ == "__main__":
    unittest.main()
