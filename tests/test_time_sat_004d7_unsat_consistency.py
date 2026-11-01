#!/usr/bin/env python3
"""No scientific rank promotion from independently verified original UNSAT CNF."""
from __future__ import annotations
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"/"time_sat_004_external"))
from archive_time_sat_004d7_consistency import gate_for_performance

class ConsistencyGate(unittest.TestCase):
    def test_verified_original_unsat_blocks_all_positive_ranks(self):
        for n in (1,2,333,10000):
            self.assertEqual(gate_for_performance(new_rank=n,
                verified_original_sat_model=False,verified_original_unsat=True),
                "BLOCK_UNSAT_ORIGINAL_ENTAILS_EVERY_GF2_EQUATION")

    def test_unknown_original_satisfiability_does_not_promote(self):
        self.assertEqual(gate_for_performance(new_rank=2,
            verified_original_sat_model=False,verified_original_unsat=False),
            "BLOCK_NO_VERIFIED_SAT_SOURCE_ORIGINAL_MODEL")

    def test_verified_sat_with_zero_rank_does_not_promote(self):
        self.assertEqual(gate_for_performance(new_rank=0,
            verified_original_sat_model=True,verified_original_unsat=False),
            "BLOCK_NO_NEW_INDEPENDENT_GF2_RANK")

    def test_verified_sat_with_rank_only_allows_future_predeclared_review(self):
        self.assertEqual(gate_for_performance(new_rank=2,
            verified_original_sat_model=True,verified_original_unsat=False),
            "POTENTIAL_FUTURE_BENCHMARK_ONLY_AFTER_EXTERNAL_WITNESS_AND_PREREG")

if __name__=="__main__":unittest.main()
