#!/usr/bin/env python3
"""Independent falsification tests for classical Deutsch / Grover simulation."""
from __future__ import annotations

from math import asin, isclose, sin, sqrt
from pathlib import Path
import random
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments" / "direct"))

from janus_deutsch_001 import (
    Circuit, MAX_QUBITS, anf_gates, apply_anf, check_ufr_covariance,
    deutsch_jozsa_zero_probability, evaluate, grover_simulate,
    hadamard_all, phase_kickback, relabel_index, truth_table,
)
from janus_ufr_001 import verify_renaming


class DeutschFalsification(unittest.TestCase):
    def test_sat_reversible_all_basis_states(self):
        for formula in (
            (),
            ((),),
            ((1,), (-2,), (3,)),
            ((1, -2), (2, 3), (-1, -3)),
            ((1,), (-1,)),
            ((1, -1), (2, -3)),
        ):
            circuit = Circuit.build(formula, 3, "SAT")
            self.assertTrue(circuit.check_reversible())
            for x in range(8):
                self.assertEqual(circuit.table[x], evaluate(circuit.rows, x, "SAT"))
                self.assertEqual(apply_anf(x, 0, circuit.gates, 3)[1], circuit.table[x])
                self.assertEqual(apply_anf(x, 1, circuit.gates, 3)[1], 1 ^ circuit.table[x])

    def test_exact_one_multiplicity_and_empty(self):
        for formula in (
            ((1, 2, 3),), ((1, 1),), ((1, -1),),
            ((1, 1, -2), (-1, 3)), ((),),
            ((1, 2), (-2, 3)),
        ):
            circuit = Circuit.build(formula, 3, "EXACT_ONE")
            self.assertTrue(circuit.check_reversible())
            self.assertEqual(circuit.table, truth_table(formula, 3, "EXACT_ONE"))
        double = Circuit.build(((1, 1),), 3, "EXACT_ONE")
        self.assertEqual(sum(double.table), 0)
        complement = Circuit.build(((1, -1),), 3, "EXACT_ONE")
        self.assertEqual(sum(complement.table), 8)

    def test_deutsch_jozsa_promise(self):
        zero = Circuit.build(((),), 4, "SAT")
        one = Circuit.build((), 4, "SAT")
        balanced = Circuit.build(((1,),), 4, "SAT")
        self.assertTrue(isclose(deutsch_jozsa_zero_probability(zero), 1, abs_tol=1e-12))
        self.assertTrue(isclose(deutsch_jozsa_zero_probability(one), 1, abs_tol=1e-12))
        self.assertTrue(isclose(deutsch_jozsa_zero_probability(balanced), 0, abs_tol=1e-12))

    def test_phase_kickback_and_unitarity(self):
        circuit = Circuit.build(((1,), (-2,)), 3, "SAT")
        u = 1 / sqrt(8)
        initial = tuple(complex(u) for _ in range(8))
        transformed = phase_kickback(circuit, initial)
        self.assertEqual(
            transformed, tuple(-z if v else z for z, v in zip(initial, circuit.table))
        )
        self.assertEqual(phase_kickback(circuit, transformed), initial)
        self.assertTrue(isclose(sum(abs(a) ** 2 for a in transformed), 1, abs_tol=1e-12))
        for recovered, expected in zip(hadamard_all(hadamard_all(initial)), initial):
            self.assertTrue(isclose(abs(recovered - expected), 0, abs_tol=1e-12))

    def test_ufr_variable_renaming_covariance(self):
        formula = ((1, -2), (-2, 3), (1, 2, 3))
        mapping = {1: 3, 2: 1, 3: 2}
        renamed = tuple(tuple((1 if literal > 0 else -1) * mapping[abs(literal)]
                              for literal in row) for row in formula)
        left = Circuit.build(formula, 3)
        right = Circuit.build(renamed, 3)
        self.assertTrue(verify_renaming(left.rows, right.rows, mapping))
        self.assertTrue(check_ufr_covariance(left, right, mapping))
        for x in range(8):
            self.assertEqual(left.table[x], right.table[relabel_index(x, mapping)])
        self.assertFalse(check_ufr_covariance(left, right, {1: 1, 2: 2, 3: 3}))

    def test_grover_probability_vs_exact_formula(self):
        for name, formula, kind in (
            ("SAT_UNIQUE", ((1,), (-2,), (3,)), "SAT"),
            ("EXACT_ONE", ((1, 2, 3),), "EXACT_ONE"),
            ("SAT_NONE", ((1,), (-1,)), "SAT"),
            ("SAT_ALL", (), "SAT"),
        ):
            c = Circuit.build(formula, 3, kind)
            result = grover_simulate(c)
            m, N = result.solutions, 1 << c.n
            expected = sin((2 * result.iterations + 1) * asin(sqrt(m / N))) ** 2
            self.assertTrue(isclose(result.success_probability, expected, abs_tol=1e-11),
                            (name, result, expected))
            self.assertEqual(result.oracle_basis_evaluations, N * (1 + result.iterations))
            self.assertEqual(result.synthesized_gate_applications,
                             2 * N * result.iterations * len(c.gates))
            if m == 0:
                self.assertFalse(result.best_candidate_validated)
                self.assertIsNone(result.best_candidate)
            self.assertTrue(c.check_reversible())

    def test_seeded_negative_controls_and_large_cap(self):
        rng = random.Random(20261101)
        for kind in ("SAT", "EXACT_ONE"):
            for n in range(1, 7):
                for _ in range(24):
                    rows = [tuple(rng.choice((-1, 1)) * rng.randint(1, n)
                                  for _ in range(rng.randint(0, 4)))
                            for _ in range(rng.randint(0, 9))]
                    c = Circuit.build(rows, n, kind)
                    self.assertTrue(c.check_reversible())
                    phase = phase_kickback(c, tuple([complex(1 / sqrt(1 << n))] * (1 << n)))
                    self.assertTrue(isclose(sum(abs(z) ** 2 for z in phase), 1,
                                            abs_tol=1e-11))
                    self.assertEqual(c.table, truth_table(rows, n, kind))
        with self.assertRaises(ValueError):
            Circuit.build(((9,),), 3)
        with self.assertRaises(ValueError):
            Circuit.build(((1,),), MAX_QUBITS + 1)
        with self.assertRaises(ValueError):
            anf_gates((0, 1, 0))
        with self.assertRaises(ValueError):
            grover_simulate(Circuit.build((), 3), iterations=33)

    def test_truth_table_anf_involution_random(self):
        rng = random.Random(4851985)
        for n in range(1, 7):
            N = 1 << n
            for _ in range(10):
                table = tuple(rng.randrange(2) for _ in range(N))
                gates = anf_gates(table)
                for x, truth in enumerate(table):
                    for b in (0, 1):
                        _, target = apply_anf(x, b, gates, n)
                        self.assertEqual(target, b ^ truth)
                        self.assertEqual(apply_anf(x, target, gates, n), (x, b))


if __name__ == "__main__":
    unittest.main()
