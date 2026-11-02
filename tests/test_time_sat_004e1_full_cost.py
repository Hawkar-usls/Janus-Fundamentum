#!/usr/bin/env python3
"""TIME-SAT-004E1 original SHA, source parity and fixed-cost safety tests."""
from __future__ import annotations
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"/"direct"))
import janus_time_sat_004e1_full_cost as run
from janus_time_sat_004d4_mixed_xor import extract_mixed_xor

class FrozenProfitGate(unittest.TestCase):
    def test_exact_precommitted_limits_four_real_engines(self):
        policy=run.check_frozen()
        self.assertEqual((run.CPU,run.WALL,run.REPEATS,run.MEM),
                         (30,36,2,2147483648))
        self.assertEqual(policy["locked_arms"],list(run.ARMS))
        self.assertEqual(len(run.ARMS),4)
        self.assertTrue(policy["comparability"]["no_finite_speedup_ratio_if_any_comparator_censored"])
        self.assertTrue(policy["comparability"]["not_hidden"])

    def test_exact_original_source_and_existing_full_sat_model(self):
        rows=run.read_original()
        self.assertEqual((len(rows),run.N,run.M),(4088,1023,4088))
        self.assertEqual(run.digest_file(run.SOURCE),run.SHA)

    def test_original_extraction_partitions_without_clause_loss(self):
        rows=run.read_original()
        extracted=extract_mixed_xor(rows,run.N)
        self.assertEqual(extracted["status"],"SOURCE_PARTITION_VERIFIED")
        self.assertEqual((len(extracted["equations"]),
                          extracted["source_xor_clauses"],
                          extracted["source_residual_clauses"]),
                          (857,3428,660))
        self.assertEqual(sorted(extracted["xor_source_clause_indices"]+
                                extracted["residual_source_clause_indices"]),
                         list(range(4088)))

    def test_no_posthoc_benchmark_arms_and_no_new_resolution_operator(self):
        self.assertNotIn("janus_resolved_xor",run.ARMS)
        self.assertEqual(run.ARMS[0],"janus_extracted_xor_cms_native")
        self.assertEqual(run.ARMS[1],"cryptominisat_original_cnf")
        self.assertEqual(set(run.ARMS[2:]),{"cadical195_original_cnf","glucose4_original_cnf"})

    def test_original_model_replay_rejects_fabricated_sat(self):
        rows=run.read_original()
        self.assertFalse(run.original_model_replay(rows,run.N,[1]*run.N))
        self.assertFalse(run.original_model_replay(rows,run.N,list(range(1,run.N))))

if __name__=="__main__":unittest.main()
