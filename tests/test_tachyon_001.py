#!/usr/bin/env python3
"""Independent false-hint, SAT and Exact-One checks for JANUS-TACHYON-001."""
from __future__ import annotations
from pathlib import Path
import random
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments" / "direct"))

from janus_tachyon_001 import (
    BOTH, ZERO, ONE, domains_gac, evaluate, initial_echo, search,
)
from janus_ufr_001 import normalize, verify_model


class Tachyon001Tests(unittest.TestCase):
    def test_no_actual_future_information_and_wrong_echo_never_proves_sat(self):
        rows = ((1,), (2, -3))
        result = search(rows, 3, echo=(0, 0, 0))
        self.assertTrue(result.answer)
        self.assertFalse(result.echoed_candidate_accepted)
        self.assertTrue(result.result_verified)
        self.assertIsNotNone(result.candidate)
        self.assertTrue(evaluate(normalize(rows), result.candidate, "SAT"))
        # A "future prediction" is just a verified candidate, never a proof.
        self.assertTrue(search(rows, 3, echo=(1, 1, 1)).echoed_candidate_accepted)
        self.assertFalse(search(((1,), (-1,)), 3, echo=(1, 1, 1)).answer)

    def test_local_support_pruning_is_sound_and_independent_of_hint(self):
        cases = [
            ((), "SAT"), (((),), "SAT"), (((1, -1),), "SAT"),
            (((1, 1),), "EXACT_ONE"), (((1, -1),), "EXACT_ONE"),
            (((1, 2, 3),), "EXACT_ONE"), (((1, 2), (-2, 3)), "SAT"),
        ]
        for rows, kind in cases:
            normalized = normalize(rows)
            for n in (3, 4):
                for gac in (True, False):
                    data = domains_gac(normalized, n, kind, (BOTH,) * n,
                                       arc_consistency=gac)
                    truth = [x for x in range(1 << n)
                             if evaluate(normalized, x, kind)]
                    if not truth:
                        self.assertIsNone(data)
                    else:
                        self.assertIsNotNone(data)
                        for x in truth:
                            for v, domain in enumerate(data):
                                self.assertTrue(domain & (1 << ((x >> v) & 1)))

    def test_random_hints_may_change_order_not_truth(self):
        rng = random.Random(20261101)
        checks = 0
        for kind in ("SAT", "EXACT_ONE"):
            for n in range(1, 8):
                for _ in range(22):
                    rows = tuple(tuple(rng.choice((-1, 1)) * rng.randint(1, n)
                                       for __ in range(rng.randint(0, 5)))
                                 for ___ in range(rng.randint(0, 10)))
                    normalized = normalize(rows)
                    truth = [x for x in range(1 << n)
                             if verify_model(
                                 normalized,
                                 {i: bool(x & (1 << (i - 1)))
                                  for i in range(1, n + 1)},
                                 kind
                             )]
                    expected = bool(truth)
                    hint = tuple(rng.randrange(2) for _ in range(n))
                    for strategy, gac in (
                        ("forward", False), ("forward", True),
                        ("retrograde", True), ("retrograde", False)
                    ):
                        found = search(rows, n, kind, echo=hint,
                                       strategy=strategy, gac=gac)
                        self.assertIs(found.answer, expected)
                        self.assertTrue(found.result_verified)
                        self.assertEqual(found.candidate is not None, expected)
                        if expected:
                            self.assertIn(found.candidate, truth)
                        checks += 1
        self.assertGreaterEqual(checks, 1000)

    def test_adversarial_false_future_model_and_exact_one_multiplicity(self):
        for formula, kind, n, expected in [
            (((1, 1),), "EXACT_ONE", 3, False),
            (((1, -1),), "EXACT_ONE", 3, True),
            (((1, 1, -2),), "EXACT_ONE", 3, True),
            (((1,), (-1,)), "SAT", 3, False),
            (((),), "SAT", 3, False),
            (((),), "EXACT_ONE", 3, False),
            ((), "SAT", 3, True),
            ((), "EXACT_ONE", 3, True),
        ]:
            for wrong in ((0,) * n, (1,) * n):
                with self.subTest(formula=formula, kind=kind, echo=wrong):
                    res = search(formula, n, kind, echo=wrong)
                    self.assertEqual(res.answer, expected)

    def test_input_bounds_and_unsafe_hints_refused(self):
        with self.assertRaises(ValueError):
            search(((1,),), 11)
        with self.assertRaises(ValueError):
            search(((0,),), 3)
        with self.assertRaises(ValueError):
            search(((4,),), 3)
        with self.assertRaises(ValueError):
            search(((1,),), 3, echo=(2, 0, 0))
        with self.assertRaises(ValueError):
            search(((1,),), 3, echo=(True, 0, 0))
        with self.assertRaises(ValueError):
            search(((1,),), 3, echo=(0, 0))
        with self.assertRaises(ValueError):
            search(((1,),), 3, strategy="future_is_fact")
        with self.assertRaises(ValueError):
            search(((1,),), 3, kind="INVALID")

    def test_preregistered_negative_control_echo_reversal(self):
        rng = random.Random(574)
        for n in (4, 5, 6):
            rows = ((1,), (-2,), (3, -4))
            guessed = initial_echo(normalize(rows), n)
            reversed_hint = tuple(1 - v for v in guessed)
            right = search(rows, n, echo=guessed)
            wrong = search(rows, n, echo=reversed_hint)
            vanilla = search(rows, n, strategy="forward")
            self.assertTrue(right.answer and wrong.answer and vanilla.answer)
            self.assertTrue(all(evaluate(normalize(rows), x.candidate, "SAT")
                                for x in (right, wrong, vanilla)))


if __name__ == "__main__":
    unittest.main()
