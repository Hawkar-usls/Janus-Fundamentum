#!/usr/bin/env python3
"""004D4D bounded paging adversarial/exhaustive source truth checks."""
from __future__ import annotations
import itertools
import random
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments" / "direct"))
from janus_time_sat_004d4d_paged_support import extract_paged_mixed_xor
from janus_time_sat_004d4c_bounded_support import extract_bounded_mixed_xor
from janus_time_sat_004d4_mixed_xor import representation_satisfied


def parity(vs, rhs):
    return [tuple(-v if (m >> j) & 1 else v for j, v in enumerate(vs))
            for m in range(1 << len(vs)) if (m.bit_count() & 1) != rhs]


class PagedSupportTest(unittest.TestCase):
    def equivalent(self, rows, n, cap=2):
        p = extract_paged_mixed_xor(rows, n, max_groups=cap)
        self.assertEqual(p["status"], "SOURCE_PARTITION_VERIFIED")
        x = p["xor_source_clause_indices"]
        r = p["residual_source_clause_indices"]
        self.assertEqual(sorted(x + r), list(range(len(rows))))
        self.assertEqual(len(set(x)), len(x))
        self.assertEqual(len(set(r)), len(r))
        self.assertEqual(p["residual_clauses"], [list(rows[i]) for i in r])
        self.assertTrue(p["exhaustive_supported_sign_mask_coverage"])
        self.assertEqual(p["SAT_or_UNSAT"], "NOT_ATTEMPTED_SOURCE_ONLY")
        self.assertTrue(all(z["indexed_unique_supports"] <= cap
                            for z in p["page_stats"]))
        for assignment in itertools.product((False, True), repeat=n):
            bits = {i + 1: assignment[i] for i in range(n)}
            old = all(any(bits[abs(lit)] == (lit > 0) for lit in row)
                      for row in rows)
            self.assertEqual(old, representation_satisfied(p, bits),
                             (rows, assignment))
        return p

    def test_second_page_recovers_complete_late_parity(self):
        rows = [(1, 2)] + parity([3, 4], 1)
        old = extract_bounded_mixed_xor(rows, 4, max_groups=1)
        self.assertEqual(old["complete_xor_equation_count"], 0)
        self.assertEqual(old["skipped_unindexed_source_clause_rows"], 2)
        p = self.equivalent(rows, 4, 1)
        self.assertEqual(p["page_count"], 2)
        self.assertEqual(p["first_page_unindexed_source_clause_rows"], 2)
        self.assertEqual(p["complete_xor_equation_count"], 1)
        self.assertEqual(p["source_residual_clauses"], 1)

    def test_incomplete_late_support_is_retained(self):
        rows = parity([1, 2], 0) + [parity([3, 4, 5], 1)[0]]
        p = self.equivalent(rows, 5, 1)
        self.assertEqual(p["complete_xor_equation_count"], 1)
        self.assertEqual(p["source_residual_clauses"], 1)

    def test_support_repeated_after_first_page_saturation(self):
        rows = [(1, 2), (3, 4), (-1, -2), (-3, -4)]
        p = self.equivalent(rows, 4, 1)
        self.assertEqual(p["page_count"], 2)
        self.assertEqual(p["complete_xor_equation_count"], 2)
        self.assertEqual(p["source_residual_clauses"], 0)

    def test_opposite_parity_both_complete_on_second_page(self):
        rows = [(1, 2)] + parity([3, 4], 0) + parity([3, 4], 1)
        p = self.equivalent(rows, 4, 1)
        self.assertEqual(p["complete_xor_equation_count"], 2)
        self.assertEqual(p["source_residual_clauses"], 1)

    def test_unsupported_and_duplicate_preserved(self):
        rows = [(1,), (1,), (2, -2), (), (1, 2, 3, 4, 5, 6, 7)]
        p = self.equivalent(rows, 7, 1)
        self.assertEqual(p["complete_xor_equation_count"], 1)
        self.assertEqual(p["source_residual_clauses"], 4)
        self.assertEqual(p["unsupported_or_repeated_clause_rows"], 3)

    def test_all_empty_and_large_no_groups(self):
        self.assertEqual(self.equivalent([], 2)["page_count"], 0)
        self.assertEqual(self.equivalent([(), (1, -1)], 2, 1)["page_count"], 0)

    def test_reject_malformed_or_excess_budget(self):
        for rows, n, cap in [
            ([(0,)], 2, 1), ([(True,)], 2, 1), ([(3,)], 2, 1),
            ([(1,)], 0, 1), ([(1,)], 2, 0),
            ([(1,)], 2, 20001), ([(1,)] * 30001, 2, 1),
        ]:
            self.assertTrue(extract_paged_mixed_xor(rows, n, max_groups=cap)
                            ["status"].startswith("ABSTAIN"))

    def test_random_exhaustive_with_many_pages(self):
        rng = random.Random(20261101047)
        for n in range(2, 6):
            for _ in range(40):
                rows = []
                for _ in range(rng.randrange(3, 16)):
                    support = rng.sample(range(1, n + 1), rng.randrange(n + 1))
                    rows.append(tuple(v if rng.randrange(2) else -v
                                      for v in support))
                self.equivalent(rows, n, cap=2)

    def test_against_uncapped_extractor_when_no_overflow(self):
        rows = parity([1, 2, 3], 1) + [(3, 4), (-4,)]
        old = extract_bounded_mixed_xor(rows, 4, max_groups=10)
        new = self.equivalent(rows, 4, cap=10)
        for key in ("xor_source_clause_indices", "residual_source_clause_indices",
                    "complete_xor_equation_count", "source_xor_clauses"):
            self.assertEqual(old[key], new[key])

if __name__ == "__main__":
    unittest.main()
