#!/usr/bin/env python3
"""Source-level adversarial and exhaustive tests for TIME-SAT-004D4."""
import itertools
from pathlib import Path
import random
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments" / "direct"))

from janus_time_sat_004d4_mixed_xor import (
    extract_mixed_xor, representation_satisfied, solve_mixed_native,
)


def encode_xor(variables, rhs):
    clauses = []
    for bits in itertools.product((0, 1), repeat=len(variables)):
        if sum(bits) % 2 == rhs:
            continue
        clauses.append(tuple(-v if bit else v
                             for v, bit in zip(variables, bits)))
    return clauses


def source_satisfied(rows, values):
    return all(any(bool(values[abs(v)]) == (v > 0) for v in row)
               for row in rows)


class MixedXorTests(unittest.TestCase):
    def assert_lossless(self, rows, n):
        p = extract_mixed_xor(rows, n)
        self.assertEqual(p["status"], "SOURCE_PARTITION_VERIFIED")
        extracted = p["xor_source_clause_indices"]
        residual = p["residual_source_clause_indices"]
        self.assertEqual(sorted(extracted + residual), list(range(len(rows))))
        self.assertEqual(set(extracted) & set(residual), set())
        self.assertEqual(p["residual_clauses"],
                         [list(rows[i]) for i in residual])
        for assignment in itertools.product((False, True), repeat=n):
            values = {i + 1: assignment[i] for i in range(n)}
            self.assertEqual(
                source_satisfied(rows, values),
                representation_satisfied(p, values),
                (rows, assignment, p["equations"]),
            )
        return p

    def test_partial_mixed_equivalence(self):
        rows = encode_xor([1, 2, 3], 1) + [(3, 4), (-4,)]
        p = self.assert_lossless(rows, 4)
        self.assertEqual(len(p["equations"]), 1)
        self.assertEqual(len(p["residual_clauses"]), 2)

    def test_incomplete_group_never_promoted(self):
        block = encode_xor([1, 2, 3], 0)
        p = self.assert_lossless(block[:-1], 3)
        self.assertEqual(p["equations"], [])
        self.assertEqual(len(p["residual_clauses"]), 3)

    def test_other_parity_incomplete_retained(self):
        rows = encode_xor([1, 2], 1) + [encode_xor([1, 2], 0)[0]]
        p = self.assert_lossless(rows, 2)
        self.assertEqual(len(p["equations"]), 1)
        self.assertEqual(len(p["residual_clauses"]), 1)

    def test_duplicate_and_tautology_retained(self):
        original = encode_xor([1, 2], 0)
        rows = original + [original[0], (1, -1)]
        p = self.assert_lossless(rows, 2)
        self.assertEqual(len(p["equations"]), 1)
        self.assertEqual(len(p["residual_clauses"]), 2)

    def test_contradictory_complete_blocks_both_extracted(self):
        rows = encode_xor([1, 2, 3], 0) + encode_xor([1, 2, 3], 1)
        p = self.assert_lossless(rows, 3)
        self.assertEqual(len(p["equations"]), 2)
        self.assertEqual(len(p["residual_clauses"]), 0)

    def test_units_empty_and_wide_residual(self):
        rows = encode_xor([1], 1) + [(), tuple(range(1, 8))]
        p = self.assert_lossless(rows, 7)
        self.assertEqual(len(p["equations"]), 1)
        self.assertEqual(p["residual_clauses"], [[], list(range(1, 8))])

    def test_invalid_fail_closed(self):
        for rows, n in [([(0,)], 2), ([(3,)], 2),
                        ([(True,)], 2), ([(1,)], 0),
                        ([(1,)], 5001)]:
            self.assertTrue(extract_mixed_xor(rows, n)["status"].startswith("ABSTAIN"))

    def test_randomized_exhaustive_semantics(self):
        rng = random.Random(20261101044)
        for n in range(1, 5):
            for _ in range(60):
                rows = []
                for _ in range(rng.randrange(0, 12)):
                    width = rng.randrange(0, n + 1)
                    varset = rng.sample(range(1, n + 1), width)
                    rows.append(tuple(v if rng.randrange(2) else -v
                                      for v in varset))
                self.assert_lossless(rows, n)

    def test_native_solver_original_sat_and_unsat(self):
        try:
            import pycryptosat  # noqa: F401
        except ImportError:
            self.skipTest("pycryptosat unavailable in local environment")
        sat_rows = encode_xor([1, 2], 0) + [(2, 3)]
        sat = solve_mixed_native(sat_rows, 3)
        self.assertEqual(sat["verdict"], "SAT_ORIGINAL_MODEL_VERIFIED")
        self.assertEqual(len(sat["model"]), 3)
        unsat_rows = encode_xor([1, 2], 0) + [(1,), (-2,)]
        unsat = solve_mixed_native(unsat_rows, 2)
        self.assertEqual(unsat["verdict"], "UNSAT_SOLVER_ONLY_NO_PORTABLE_CERTIFICATE")
        self.assertEqual(unsat["portable_DRUP_LRAT"], "NOT_PRODUCED")

    def test_no_structural_xor_means_no_solver_claim(self):
        rows = [(1, 2, 3), (-1, 2, 3)]
        result = solve_mixed_native(rows, 3)
        self.assertEqual(result["verdict"], "ABSTAIN_NO_COMPLETE_XOR_BLOCK")


if __name__ == "__main__":
    unittest.main()
