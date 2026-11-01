#!/usr/bin/env python3
"""Independent bounded falsification of JANUS-DEUTSCH-003 pebble circuit."""
from __future__ import annotations

from pathlib import Path
import random
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments" / "direct"))
from janus_deutsch_001 import Circuit
from janus_deutsch_002 import DirectOracle
from janus_deutsch_003 import (
    BlockOracle, candidate_sizes, choose_block_size, verify_ufr_covariance,
)
from janus_tear_maj3_stifling_audit import maj3_lifted_tseitin_cnf
from janus_tear_policy0a_masked_tseitin import K4_EDGES
from janus_ufr_001 import verify_model


class BlockOracleTests(unittest.TestCase):
    def test_boolean_equivalence_and_dirty_ancilla_involution(self):
        rng = random.Random(20261101)
        tested = 0
        for kind in ("SAT", "EXACT_ONE"):
            for n in range(1, 6):
                for _ in range(24):
                    rows = tuple(
                        tuple(rng.choice((-1, 1)) * rng.randint(1, n)
                              for __ in range(rng.randint(0, 4)))
                        for _ in range(rng.randint(0, 7))
                    )
                    reference = Circuit.build(rows, n, kind)
                    direct = DirectOracle.compile(rows, n, kind)
                    for block in (1, 2, 4, 8):
                        oracle = BlockOracle.from_direct(direct, block_size=block)
                        self.assertEqual(
                            oracle.logical_mcx_gates, 4*direct.work_qubits +
                            2*oracle.blocks + 1)
                        self.assertEqual(sum(1 for _ in oracle.iter_instructions()),
                                         oracle.logical_mcx_gates)
                        for x in range(1 << n):
                            expected = bool(reference.table[x])
                            self.assertIs(oracle.evaluate(x), expected)
                            self.assertEqual(oracle.phase(x), -1 if expected else 1)
                            for target in (0, 1):
                                scratch_variants = (0, (1 << oracle.scratch_bits)-1)
                                summary_variants = (0, (1 << oracle.blocks)-1)
                                for scratch in scratch_variants:
                                    for summaries in summary_variants:
                                        initial = (x, target, scratch, summaries)
                                        after = oracle.apply_basis(*initial)
                                        self.assertEqual(after[0], x)
                                        self.assertEqual(after[2:], (scratch, summaries))
                                        self.assertEqual(oracle.apply_basis(*after), initial)
                                        if scratch == summaries == 0:
                                            self.assertEqual(after[1], target ^ int(expected))
                                        tested += 1
        self.assertGreater(tested, 20000)

    def test_fixed_adversarial_corner_cases(self):
        examples = [
            ((), "SAT", True),
            (((),), "SAT", False),
            (((1,), (-1,)), "SAT", False),
            (((1, -1),), "SAT", True),
            (((1, 1),), "EXACT_ONE", False),
            (((1, -1),), "EXACT_ONE", True),
            (((1, 2, 3),), "EXACT_ONE", True),
        ]
        for rows, kind, has_solution in examples:
            c = BlockOracle.compile(rows, 3, kind, block_size=2)
            self.assertEqual(any(c.evaluate(x) for x in range(8)), has_solution)
            for x in range(8):
                assignment = {i: bool(x & (1 << (i-1))) for i in range(1, 4)}
                expected = verify_model(rows, assignment, kind)
                self.assertEqual(c.evaluate(x), expected)
        for bad in (0, -1, 1.2, True, 8193):
            with self.assertRaises(ValueError):
                BlockOracle.compile((), 3, block_size=bad)
        c = BlockOracle.compile(((1,),), 3)
        with self.assertRaises(ValueError):
            c.apply_basis(8, 0)
        with self.assertRaises(ValueError):
            c.apply_basis(0, 2)
        with self.assertRaises(ValueError):
            c.apply_basis(0, 0, 2)
        with self.assertRaises(ValueError):
            c.apply_basis(0, 0, 0, 2)

    def test_resource_estimate_tradeoff_is_not_hidden(self):
        cnf, n = maj3_lifted_tseitin_cnf(4, K4_EDGES)
        direct = DirectOracle.compile(cnf, n, "SAT")
        baseline = direct.resources()
        oracle = choose_block_size(direct)
        self.assertEqual(oracle.block_size, 32)
        self.assertEqual(oracle.blocks, 32)
        self.assertEqual(oracle.scratch_bits, 32)
        self.assertEqual(oracle.total_clean_ancillas, 64)
        self.assertEqual(oracle.maximum_controls, 32)
        self.assertEqual(oracle.qubit_estimate, 113)
        self.assertEqual(oracle.logical_mcx_gates, 4161)
        self.assertEqual(oracle.estimated_toffolis, 65405)
        self.assertEqual(oracle.estimated_polarity_x_gates, 40960)
        self.assertEqual(baseline["qubit_count_with_clean_decomposition_estimate"], 2065)
        self.assertEqual(baseline["toffoli_count_clean_decomposition_estimate"], 32765)
        self.assertGreater(oracle.estimated_toffolis,
                           baseline["toffoli_count_clean_decomposition_estimate"])
        self.assertLess(oracle.qubit_estimate,
                        baseline["qubit_count_with_clean_decomposition_estimate"])
        self.assertLess(oracle.maximum_controls,
                        baseline["max_controlled_x_controls"])
        self.assertEqual(choose_block_size(direct, max_controls=32).block_size, 32)
        with self.assertRaises(ValueError):
            choose_block_size(direct, max_controls=8)
        for size in (1, 8, 16, 32, 64, 128, 1024):
            candidate = BlockOracle.from_direct(direct, block_size=size)
            self.assertEqual(sum(1 for _ in candidate.iter_instructions()),
                             candidate.logical_mcx_gates)

    def test_maj3_truth_samples_and_structural_ufr_covariance(self):
        rows, n = maj3_lifted_tseitin_cnf(4, K4_EDGES)
        direct = DirectOracle.compile(rows, n)
        new = BlockOracle.from_direct(direct, block_size=32)
        rng = random.Random(5741985)
        sample = [0, (1 << n)-1] + [rng.getrandbits(n) for _ in range(512)]
        for x in sample:
            self.assertEqual(new.evaluate(x), direct.evaluate(x))
            self.assertEqual(new.apply_basis(x, 1), (x, int(not direct.evaluate(x)), 0, 0))
        mapping = {v: (v % n)+1 for v in range(1, n+1)}
        renamed = tuple(
            tuple((1 if lit > 0 else -1)*mapping[abs(lit)] for lit in clause)
            for clause in rows
        )
        rhs = BlockOracle.compile(renamed, n, "SAT", block_size=32)
        self.assertTrue(verify_ufr_covariance(
            new, rhs, mapping, sampled_assignments=sample[:96]))
        self.assertFalse(verify_ufr_covariance(
            new, rhs, {v:v for v in range(1,n+1)}, sampled_assignments=sample[:16]))

    def test_controlled_finite_pebble_design(self):
        self.assertEqual(candidate_sizes(0), (1,))
        self.assertEqual(candidate_sizes(4), (1, 2, 3, 4))
        with self.assertRaises(ValueError):
            candidate_sizes(-1)
        with self.assertRaises(ValueError):
            choose_block_size(DirectOracle.compile(((1,),), 2), max_controls=-1)
        source = DirectOracle.compile(((1,2,3), (-2,3), (1,-3)), 3)
        selected = choose_block_size(source)
        variants = [BlockOracle.from_direct(source, block_size=k)
                    for k in candidate_sizes(source.work_qubits)]
        self.assertEqual(selected.qubit_estimate, min(v.qubit_estimate for v in variants))
        for left in variants:
            self.assertTrue(all(left.evaluate(x) == source.evaluate(x)
                                for x in range(8)))


if __name__ == "__main__":
    unittest.main()
