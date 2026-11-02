#!/usr/bin/env python3
"""004E2 synthetic adversarial gate and frozen public-source integrity."""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"/"direct"))
import janus_time_sat_004e2_adaptive_gate as run
from janus_time_sat_004d4_mixed_xor import extract_mixed_xor

def fixture(m=10,converted=8):
    return {
        "status":"SOURCE_PARTITION_VERIFIED",
        "complete_xor_equation_count":1,
        "source_xor_clauses":converted,
        "source_residual_clauses":m-converted,
        "equations":[{"variables":[1],"rhs":0}],
        "residual_clauses":[[1]]*(m-converted),
        "xor_source_clause_indices":list(range(converted)),
        "residual_source_clause_indices":list(range(converted,m))
    }

class AdaptSafety(unittest.TestCase):
    def test_frozen_prereg_and_all_source_hashes(self):
        policy=run.check_frozen()
        self.assertEqual(len(policy["cases"]),4)
        self.assertEqual(policy["fixed_arms"],list(run.ARMS))
        self.assertEqual((run.CPU,run.WALL,run.REPEATS),(6,10,2))
        self.assertTrue(policy["comparability"]["same_preseen_public_development_sources"])
        for family in run.NAMES:
            rows,n,sha=run.original(family)
            self.assertEqual(len(rows),run.CASES[run.NAMES.index(family)][4])
            self.assertEqual(n,run.CASES[run.NAMES.index(family)][3])
            self.assertEqual(len(sha),64)

    def test_exact_threshold_80pct_and_below(self):
        self.assertEqual(run.gate_decision(fixture(10,8),10)["choose"],"native_xor_CMS")
        self.assertEqual(run.gate_decision(fixture(10,7),10)["choose"],"raw_CMS")
        self.assertEqual(run.gate_decision(fixture(10,10),10)["choose"],"native_xor_CMS")

    def test_negative_abstain_group_budget_fallback_without_claim(self):
        for msg in ("ABSTAIN_GROUP_BUDGET","ABSTAIN_ROW_BUDGET","ABSTAIN_LITERAL_BUDGET"):
            self.assertEqual(run.gate_decision({"status":msg},100)["choose"],"raw_CMS")

    def test_missing_extraction_unknown_status_rejected(self):
        for status in ("SOURCE_UNVERIFIED","", "PASS", "MISSING"):
            with self.assertRaises(AssertionError):run.gate_decision({"status":status},10)

    def test_malformed_missing_or_duplicate_original_clause_rejected(self):
        for field,value in (
            ("source_xor_clauses",9),
            ("source_residual_clauses",3),
            ("complete_xor_equation_count",2),
            ("xor_source_clause_indices",list(range(7))+[7,7]),
            ("residual_source_clause_indices",[6,9]),
            ("equations",[]),
            ("residual_clauses",[])):
            case=fixture()
            case[field]=value
            with self.assertRaises(AssertionError,msg=field):run.gate_decision(case,10)

    def test_zero_equations_never_forces_native_xor(self):
        p=fixture(10,0)
        p["complete_xor_equation_count"]=0
        p["equations"]=[]
        self.assertEqual(run.gate_decision(p,10)["choose"],"raw_CMS")

    def test_real_preseen_family_gate_does_not_claim_automatic_generalization(self):
        results={}
        for family in run.NAMES:
            rows,n,sha=run.original(family)
            partition=extract_mixed_xor(rows,n)
            decision=run.gate_decision(partition,len(rows))
            results[family]=decision["choose"]
        # Known development case only; this must never be called a holdout.
        self.assertEqual(results,{
            "linear-equations":"raw_CMS",
            "xor-shifting":"raw_CMS",
            "minimum-disagreement-parity":"raw_CMS",
            "binary-tree-parity":"native_xor_CMS"})

    def test_no_production_writes_or_004d6_source_resolution(self):
        p=run.check_frozen()
        self.assertEqual(set(run.ARMS),{
            "adaptive_cms","noop_scan_cms","cms_original",
            "cadical195_original","glucose4_original"})
        self.assertTrue(p["stop_rules"]["no_C023_main_change"])
        self.assertTrue(p["stop_rules"]["no_hidden_claim"])
        self.assertTrue(p["stop_rules"]["no_posthoc_threshold_adjustment"])
        self.assertTrue(p["comparability"]["no_numeric_ratio_on_censored"])
        self.assertNotIn("derived_resolvent",run.ARMS)

if __name__=="__main__":unittest.main()
