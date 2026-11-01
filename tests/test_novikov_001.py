#!/usr/bin/env python3
"""NOVIKOV-001: falsify false global consistency, cycles and incorrect hints."""
from __future__ import annotations
from dataclasses import replace
from pathlib import Path
import random
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments" / "direct"))
from janus_novikov_001 import (
    RepairStep, audit_repair, finite_fixed_points, guided_search,
    independent_model, repair, violated_rows,
)
from janus_ufr_001 import normalize, verify_model


class Novikov001Tests(unittest.TestCase):
    def test_fixed_point_toy_no_satisfying_history_and_multiple_histories(self):
        self.assertEqual(finite_fixed_points((1, 0)), ())
        self.assertEqual(finite_fixed_points((0, 1)), (0, 1))
        self.assertEqual(finite_fixed_points((1, 1)), (1,))
        self.assertEqual(finite_fixed_points((0, 2, 1)), (0,))
        with self.assertRaises(ValueError):
            finite_fixed_points((1,))
        with self.assertRaises(ValueError):
            finite_fixed_points((False, 1))

    def test_local_minimum_cannot_certify_unsat(self):
        # Contradictory SAT: local repairs necessarily stall, DPLL still
        # needs complete independent proof, not self-consistency slogans.
        formula = ((1,), (-1,))
        result = repair(formula, 3, "SAT", hint=(0, 0, 0))
        self.assertEqual(result.status, "LOCAL_MINIMUM_NOT_UNSAT")
        self.assertGreater(result.final_violations, 0)
        self.assertTrue(audit_repair(formula, 3, "SAT", result))
        checked = guided_search(formula, 3, "SAT", hint=(0, 0, 0))
        self.assertFalse(checked.answer)
        self.assertIsNone(checked.candidate)
        self.assertTrue(checked.independent_search_verification_pass)

    def test_successful_projection_to_global_sat_model(self):
        rows = ((1,), (2,), (-3,))
        receipt = repair(rows, 3, hint=(0, 0, 0))
        self.assertEqual(receipt.status, "GLOBAL_MODEL_VERIFIED")
        self.assertEqual(receipt.final_violations, 0)
        self.assertEqual(receipt.final_candidate, 0b011)
        self.assertTrue(receipt.independently_verified)
        self.assertTrue(audit_repair(rows, 3, "SAT", receipt))
        self.assertTrue(guided_search(rows, 3, hint=(0, 0, 0)).answer)

    def test_unsatisfiable_two_constraint_trap_not_misreported(self):
        rows = ((1, 2), (-1,), (-2,))
        for initial in ((0, 0), (1, 1), (1, 0), (0, 1)):
            result = repair(rows, 2, hint=initial)
            self.assertFalse(result.independently_verified)
            self.assertGreater(result.final_violations, 0)
            self.assertEqual(result.status, "LOCAL_MINIMUM_NOT_UNSAT")
            self.assertFalse(guided_search(rows, 2, hint=initial).answer)

    def test_exact_one_repeated_lits_and_complementary_literals(self):
        cases = (
            (((1, 1),), 2, False),
            (((1, -1),), 2, True),
            (((1, 2, 3),), 3, True),
            (((1, 1), (-1, -1)), 2, False),
            (((),), 2, False),
        )
        for rows, n, expected in cases:
            for seed in ((0,) * n, (1,) * n):
                receipt = repair(rows, n, "EXACT_ONE", hint=seed)
                self.assertTrue(audit_repair(rows, n, "EXACT_ONE", receipt))
                output = guided_search(rows, n, "EXACT_ONE",
                                       hint=seed, fallback="candidate_first")
                self.assertEqual(output.answer, expected)
                if receipt.independently_verified:
                    self.assertTrue(independent_model(normalize(rows), n, "EXACT_ONE",
                                                      receipt.final_candidate))

    def test_detect_tampered_local_step_energy_or_forged_status(self):
        rows = ((1,), (2,), (-3,))
        receipt = repair(rows, 3, hint=(0, 0, 0))
        self.assertGreater(len(receipt.steps), 1)
        forged = [
            replace(receipt, status="LOCAL_MINIMUM_NOT_UNSAT"),
            replace(receipt, final_candidate=receipt.final_candidate ^ 1),
            replace(receipt, final_violations=999),
            replace(receipt, independently_verified=False),
            replace(receipt, steps=(
                replace(receipt.steps[0], violated_clauses=1000),
                *receipt.steps[1:])),
            replace(receipt, steps=receipt.steps[:-1]),
            replace(receipt, steps=(
                receipt.steps[0], receipt.steps[0], *receipt.steps[1:])),
        ]
        for counterfeit in forged:
            with self.subTest(fake=counterfeit):
                with self.assertRaises(AssertionError):
                    audit_repair(rows, 3, "SAT", counterfeit)

    def test_randomized_global_truth_and_proof_for_both_kinds(self):
        rng = random.Random(20261101)
        total = 0
        for kind in ("SAT", "EXACT_ONE"):
            for n in range(2, 8):
                for _ in range(25):
                    rows = tuple(tuple(rng.choice((-1, 1))*rng.randint(1, n)
                                       for __ in range(rng.randrange(5)))
                                 for ___ in range(rng.randrange(11)))
                    all_models = []
                    clean = normalize(rows)
                    for x in range(1 << n):
                        assignment = {v: bool(x >> (v-1) & 1)
                                      for v in range(1, n+1)}
                        if verify_model(clean, assignment, kind):
                            all_models.append(x)
                    hint = tuple(rng.randrange(2) for _ in range(n))
                    receipt = repair(rows, n, kind, hint=hint)
                    self.assertTrue(audit_repair(rows, n, kind, receipt))
                    self.assertEqual(receipt.independently_verified,
                                     receipt.final_candidate in all_models)
                    self.assertEqual(receipt.final_violations == 0,
                                     receipt.final_candidate in all_models)
                    for a, b in zip(receipt.steps, receipt.steps[1:]):
                        self.assertLess(b.violated_clauses, a.violated_clauses)
                        self.assertEqual((a.bits ^ b.bits).bit_count(), 1)
                    for fallback in ("candidate_first", "retrograde"):
                        result = guided_search(rows, n, kind, hint=hint,
                                               fallback=fallback)
                        self.assertEqual(result.answer, bool(all_models))
                        self.assertEqual(result.candidate in all_models,
                                         bool(all_models))
                        self.assertTrue(result.independent_repair_audit_pass)
                    total += 1
        self.assertEqual(total, 300)

    def test_absence_of_cycle_is_not_a_theorem_about_sat(self):
        # This circuit of contradictory requests has no globally satisfying
        # Boolean assignment. A stable LOCAL repair minimum still exists.
        rows = ((1, 2), (-1, -2), (1, -2), (-1, 2))
        result = repair(rows, 2, "EXACT_ONE", hint=(0, 0))
        self.assertEqual(result.status, "LOCAL_MINIMUM_NOT_UNSAT")
        self.assertTrue(audit_repair(rows, 2, "EXACT_ONE", result))
        self.assertFalse(guided_search(rows, 2, "EXACT_ONE",
                                       hint=(0, 0)).answer)

    def test_bounds_no_forged_future_solution_or_fallback_skip(self):
        with self.assertRaises(ValueError):
            repair(((1,),), 11)
        with self.assertRaises(ValueError):
            repair(((1,),), 3, hint=(True, 0, 0))
        with self.assertRaises(ValueError):
            repair(((1,),), 3, hint=(0, 0))
        with self.assertRaises(ValueError):
            guided_search(((1,),), 3, fallback="pretend_consistent")
        with self.assertRaises(ValueError):
            finite_fixed_points(())
        with self.assertRaises(ValueError):
            repair((tuple([1] * 17),), 3, "EXACT_ONE")


if __name__ == "__main__":
    unittest.main()
