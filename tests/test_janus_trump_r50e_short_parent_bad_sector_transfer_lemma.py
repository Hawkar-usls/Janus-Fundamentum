from __future__ import annotations

import unittest

import janus_trump_r50e_short_parent_bad_sector_transfer_lemma as r50e


class R50EShortParentBadSectorTests(unittest.TestCase):
    def test_arithmetic_kernel(self):
        rows = r50e.short_parent_theorem_kernel()
        self.assertEqual(len(rows), 16)
        for row in rows:
            pw = row["positive_parent_width"]
            nw = row["negative_parent_width"]
            if pw <= 2 or nw <= 2:
                self.assertLessEqual(row["max_union_without_overlap"], 4)
            if row["width6_possible_without_overlap"]:
                self.assertEqual((pw, nw), (4, 4))

    def test_binary_parent_cannot_make_width5(self):
        f = ((1, 2), (-1, 3, 4, 5))
        p = r50e.sector_profile(f, 1)
        self.assertEqual(p["bad_pair_count"], 0)
        self.assertEqual(p["long_long_capacity"], 0)
        self.assertTrue(p["theorem_bad_subset_long_long_pass"])

    def test_width3_by_width4_can_make_width5(self):
        f = ((1, 2, 3), (-1, 4, 5, 6))
        p = r50e.sector_profile(f, 1)
        self.assertEqual(p["bad_pair_count"], 1)
        self.assertEqual(p["width5_bad_pair_count"], 1)
        self.assertEqual(p["width6_bad_pair_count"], 0)
        self.assertEqual(p["long_long_capacity"], 1)

    def test_width6_requires_4_by_4(self):
        f = ((1, 2, 3, 4), (-1, 5, 6, 7))
        p = r50e.sector_profile(f, 1)
        self.assertEqual(p["bad_pair_count"], 1)
        self.assertEqual(p["width6_bad_pair_count"], 1)
        self.assertEqual(p["unique_bad_resolvent_count"], 1)

    def test_tautological_cross_pair_is_not_bad(self):
        f = ((1, 2, 3, 4), (-1, -2, 5, 6))
        p = r50e.sector_profile(f, 1)
        self.assertEqual(p["tautological_cross_pair_count"], 1)
        self.assertEqual(p["retained_cross_pair_count"], 0)
        self.assertEqual(p["bad_pair_count"], 0)

    def test_candidate_relations_are_frozen(self):
        self.assertEqual(
            r50e.CANDIDATES,
            (
                "LONG_LONG_CAPACITY_NONINCREASE",
                "BAD_PAIR_COUNT_NONINCREASE",
                "UNIQUE_BAD_RESOLVENT_COUNT_NONINCREASE",
                "WIDTH6_BAD_COUNT_NONINCREASE",
                "BAD_LONG_LONG_DENSITY_NONINCREASE",
                "FORCED_WIDE_CLAUSE_COUNT_NONINCREASE",
            ),
        )


if __name__ == "__main__":
    unittest.main()
