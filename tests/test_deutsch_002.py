#!/usr/bin/env python3
"""Falsification tests for direct CNF-to-reversible oracle synthesis (Deutsch-002)."""
from __future__ import annotations

from math import asin, isclose, sin, sqrt
from pathlib import Path
import random
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments" / "direct"))
from janus_deutsch_001 import Circuit
from janus_deutsch_002 import (
    DirectOracle, check_ufr_covariance, deutsch_jozsa_probability,
    grover_statevector, phase_statevector,
)
from janus_tear_maj3_stifling_audit import maj3_lifted_tseitin_cnf
from janus_tear_policy0a_masked_tseitin import K4_EDGES
from janus_ufr_001 import verify_model, normalize


def independently_truth(rows, x, kind):
    assignment = {v: bool(x & (1 << (v - 1))) for v in range(1, max(
        (abs(l) for row in rows for l in row), default=0) + 1)}
    return verify_model(rows, assignment, kind)


class Deutsch002Falsification(unittest.TestCase):
    def test_sat_oracle_all_clean_and_dirty_basis_states(self):
        examples = [(), ((),), ((1,), (-1,)), ((1, -2), (2, 3)),
                    ((1, -1),), ((1, 1, 2),), ((1, -2), (1, -2))]
        for rows in examples:
            with self.subTest(rows=rows):
                direct = DirectOracle.compile(rows, 3, "SAT")
                previous = Circuit.build(rows, 3, "SAT")
                for x in range(8):
                    self.assertEqual(direct.evaluate(x), bool(previous.table[x]))
                    self.assertEqual(direct.phase(x), (-1 if previous.table[x] else 1))
                    for b in (0, 1):
                        work_patterns = (0, (1 << direct.work_qubits) - 1)
                        for work in work_patterns:
                            y = direct.apply_basis(x, b, work)
                            self.assertEqual(y[0], x)
                            self.assertEqual(y[2], work)
                            self.assertEqual(direct.apply_basis(*y), (x, b, work))
                        self.assertEqual(direct.apply_basis(x, b)[1],
                                         b ^ previous.table[x])

    def test_exact_one_oracle_multiplicity_pairwise_encoding(self):
        examples = [(), ((),), ((1, 1),), ((1, -1),), ((1, 1, -2),),
                    ((1, 2, 3),), ((1, 2), (-1, 3))]
        for rows in examples:
            direct = DirectOracle.compile(rows, 3, "EXACT_ONE")
            previous = Circuit.build(rows, 3, "EXACT_ONE")
            for x in range(8):
                self.assertEqual(direct.evaluate(x), bool(previous.table[x]), rows)
                self.assertEqual(direct.apply_basis(x, 0)[1], previous.table[x])
            self.assertLessEqual(direct.work_qubits, direct.encoded_clause_count)
        self.assertTrue(DirectOracle.compile(((1, -1),), 3, "EXACT_ONE").evaluate(0))
        self.assertFalse(DirectOracle.compile(((1, 1),), 3, "EXACT_ONE").evaluate(0))

    def test_seeded_random_oracles_and_involution(self):
        rng = random.Random(19851992)
        checks = 0
        for kind in ("SAT", "EXACT_ONE"):
            for n in range(1, 7):
                for _ in range(25):
                    rows = tuple(tuple(rng.choice((-1, 1)) * rng.randint(1, n)
                                       for __ in range(rng.randint(0, 4)))
                                 for ___ in range(rng.randint(0, 9)))
                    oracle = DirectOracle.compile(rows, n, kind)
                    for x in range(1 << n):
                        truth = independently_truth(rows, x, kind)
                        self.assertIs(oracle.evaluate(x), truth)
                        out = oracle.apply_basis(x, 0)
                        self.assertEqual(out, (x, int(truth), 0))
                        self.assertEqual(oracle.apply_basis(*out), (x, 0, 0))
                        checks += 1
        self.assertGreaterEqual(checks, 3000)

    def test_deutsch_jozsa_phase_and_grover_consistency(self):
        examples = [
            (((),), "SAT"), ((), "SAT"), (((1,),), "SAT"),
            (((1,), (-2,), (3,)), "SAT"),
            (((1, 2, 3),), "EXACT_ONE"),
        ]
        for rows, kind in examples:
            direct = DirectOracle.compile(rows, 3, kind)
            prev = Circuit.build(rows, 3, kind)
            self.assertTrue(isclose(
                deutsch_jozsa_probability(direct),
                abs(sum(((-1 if v else 1) for v in prev.table)) / 8) ** 2,
                abs_tol=1e-12))
            g = grover_statevector(direct)
            p = sin((2 * g.iterations + 1) * asin(sqrt(g.solutions / 8))) ** 2
            self.assertTrue(isclose(g.success_probability, p, abs_tol=1e-12),
                            (rows, kind, g))
            self.assertEqual(g.gate_condition_evaluations,
                             g.basis_predicate_evaluations * direct.work_qubits)
            if g.candidate_verified:
                self.assertIsNotNone(g.candidate)
                self.assertTrue(independently_truth(rows, g.candidate, kind))

    def test_ufr_permutation_covariance_and_rejection(self):
        formula = ((1, -2), (2, 3), (-1, -3))
        mapping = {1: 3, 2: 1, 3: 2}
        mapped = tuple(tuple((1 if lit > 0 else -1) * mapping[abs(lit)]
                             for lit in row) for row in formula)
        for kind in ("SAT", "EXACT_ONE"):
            left = DirectOracle.compile(formula, 3, kind)
            right = DirectOracle.compile(mapped, 3, kind)
            self.assertTrue(check_ufr_covariance(left, right, mapping))
            self.assertFalse(check_ufr_covariance(left, right, {1: 1, 2: 2, 3: 3}))

    def test_large_maj3_k4_compiles_without_truth_table(self):
        cnf, n = maj3_lifted_tseitin_cnf(4, K4_EDGES)
        self.assertEqual((n, len(cnf)), (18, 1024))
        oracle = DirectOracle.compile(cnf, n, "SAT")
        self.assertEqual(oracle.work_qubits, 1024)
        self.assertEqual(oracle.logical_mcx_gates, 2049)
        resources = oracle.resources()
        self.assertFalse(resources["truth_table_required_for_compilation"])
        self.assertGreater(resources["max_controlled_x_controls"], 1000)
        self.assertGreater(resources["qubit_count_with_clean_decomposition_estimate"], 2000)
        rng = random.Random(5741985)
        tested = [0, (1 << n) - 1, 0x15555, 0x2AAAA]
        tested += [rng.getrandbits(n) for _ in range(512)]
        for x in tested:
            expected = independently_truth(cnf, x, "SAT")
            self.assertEqual(oracle.evaluate(x), expected)
            self.assertEqual(oracle.apply_basis(x, 1), (x, int(not expected), 0))
        # Independently verified UFR covariance on the real 18-variable CNF:
        # this compares all 514 selected assignments, not the full truth table.
        mapping = {v: (v % n) + 1 for v in range(1, n + 1)}
        renamed = tuple(tuple((1 if lit > 0 else -1) * mapping[abs(lit)]
                              for lit in clause) for clause in cnf)
        renamed_oracle = DirectOracle.compile(renamed, n, "SAT")
        self.assertEqual(renamed_oracle.resources()["logical_mcx_gates"],
                         oracle.resources()["logical_mcx_gates"])
        self.assertTrue(check_ufr_covariance(oracle, renamed_oracle, mapping,
                                             sample_indices=tested))
        # MAJ3-K4 UNSAT is established by independent C023 replay, not
        # by 516 checked assignments.
        with self.assertRaises(ValueError):
            phase_statevector(oracle, (1+0j,))

    def test_resource_bounds_and_invalid_inputs(self):
        self.assertEqual(DirectOracle.compile((), 5).work_qubits, 0)
        self.assertEqual(DirectOracle.compile(((),), 5).work_qubits, 1)
        self.assertEqual(DirectOracle.compile(((),), 5).estimated_toffoli_count, 0)
        with self.assertRaises(ValueError):
            DirectOracle.compile(((5,),), 4)
        with self.assertRaises(ValueError):
            DirectOracle.compile(((1,),), 65)
        with self.assertRaises(ValueError):
            DirectOracle.compile(((1,),), 3, "invalid")
        with self.assertRaises(ValueError):
            DirectOracle.compile(((0,),), 3)
        with self.assertRaises(ValueError):
            DirectOracle.compile((tuple([1] * 130),), 3, "EXACT_ONE")
        with self.assertRaises(ValueError):
            DirectOracle.compile(((1,),), 0)
        with self.assertRaises(ValueError):
            DirectOracle.compile(((1,),), 3).apply_basis(8, 0)


if __name__ == "__main__":
    unittest.main()
