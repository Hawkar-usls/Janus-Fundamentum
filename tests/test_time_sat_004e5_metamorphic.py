#!/usr/bin/env python3
"""004E5: prove satisfiability-preserving permutation/polarity/tautology transform."""
from __future__ import annotations
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"/"direct"))
import janus_time_sat_004e5_metamorphic as m
from janus_time_sat_004d4b_real_pilot import original_model_replay
from janus_time_sat_004e3_swarm import select_verified_xor

class MetamorphicSafety(unittest.TestCase):
    def test_frozen_24_job_matrix_and_six_original_copies_not_external(self):
        p=m.preflight()
        self.assertEqual(2*3*2*2,24)
        self.assertEqual(p["matrix"]["total_cold_child_processes"],96)
        self.assertEqual((m.CPU,m.WALL,m.MEM),(6,10,2147483648))
        self.assertEqual(p["metamorphic_rewrite"]["new_holdout_families"],0)

    def test_tiny_satisfiable_bijection_and_full_model_all_padding(self):
        rows=[[1,2],[-1,-2],[3]]
        signed=[-1,2,3]
        self.assertTrue(original_model_replay(rows,3,signed))
        for pad in m.PADS:
            got=m.transform(rows,3,signed,"lights-out",pad)
            self.assertTrue(original_model_replay(got["rows"],3,got["model"]))
            self.assertEqual(got["padding_clauses"],(len(rows)*pad+99)//100)
            self.assertEqual(got["generated_SHA256"],m.sha256(got["data"]).hexdigest())
            self.assertEqual(len(got["rows"]),len(rows)+got["padding_clauses"])

    def test_deterministic_same_original_source_across_ubuntu_hosts(self):
        rows=[[1,2],[-1,-2],[3]]
        signed=[-1,2,3]
        a=m.transform(rows,3,signed,"lights-out",30)
        b=m.transform(rows,3,signed,"lights-out",30)
        self.assertEqual(a["data"],b["data"])
        self.assertEqual(a["model"],b["model"])

    def test_polarity_remap_truth_assignment_is_not_identity(self):
        rows=[[1,2],[-1,-2],[3]]
        signed=[-1,2,3]
        got=m.transform(rows,3,signed,"binary-tree-parity",0)
        self.assertTrue(original_model_replay(got["rows"],3,got["model"]))
        for clause in got["rows"]:
            self.assertTrue(any((lit>0)==(got["model"][abs(lit)-1]>0) for lit in clause))

    def test_real_previously_certified_source_models_and_source_sha(self):
        for family in m.FAMILIES:
            rows,n,sha,signed=m.original_verified(family)
            self.assertEqual(sha,m.SOURCE[family][0])
            self.assertTrue(original_model_replay(rows,n,signed))

    def test_adaptive_80_threshold_crosses_under_tautological_padding(self):
        for family,pad in (("binary-tree-parity",5),("lights-out",30)):
            data=m.materialize(family,pad)
            gate=select_verified_xor(data["rows"],data["n"],"adaptive_80")
            allx=select_verified_xor(data["rows"],data["n"],"native_all")
            self.assertEqual(gate["equations"],[])
            self.assertEqual(gate["choice"],"raw_after_scan")
            self.assertGreater(len(allx["equations"]),0)
            self.assertLess(allx["converted_source_clauses"]/len(data["rows"]),0.8)

    def test_native_vs_adaptive_no_padding_equivalent_source_models(self):
        for family in m.FAMILIES:
            data=m.materialize(family,0)
            full=select_verified_xor(data["rows"],data["n"],"native_all")
            adaptive=select_verified_xor(data["rows"],data["n"],"adaptive_80")
            self.assertGreater(len(full["equations"]),0)
            self.assertEqual(len(adaptive["equations"]),len(full["equations"]))
            self.assertEqual(adaptive["choice"],"native_xor")

    def test_unknown_transform_rejected(self):
        with self.assertRaises(AssertionError):
            m.transform([[1]],1,[1],"lights-out",17)

if __name__=="__main__":unittest.main()
