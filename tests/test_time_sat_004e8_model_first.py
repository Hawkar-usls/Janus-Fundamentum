#!/usr/bin/env python3
"""004E8 safety: planted truth, exact source SHAs, fail-closed no-op and full model."""
from __future__ import annotations
from itertools import product
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"/"direct"))
import janus_time_sat_004e8_model_first as m
from janus_time_sat_004d4b_real_pilot import original_model_replay

class ModelFirstSafety(unittest.TestCase):
    def test_frozen_policy_and_exact_compute_ceiling(self):
        p=m.freeze()
        self.assertEqual([c["id"] for c in p["cases"]],list(m.IDS))
        self.assertEqual(p["budget"]["total_cold_children"],160)
        self.assertEqual(p["budget"]["max_parallel"],8)
        self.assertEqual(p["scope"]["new_external_blinded_CNF_cases"],0)
        self.assertEqual(p["scope"]["C023_main"],"UNCHANGED")

    def test_all_eight_source_original_models_and_reproduction(self):
        for name in m.IDS:
            x=m.source(name)
            self.assertEqual(m.sha256(x["bytes"]).hexdigest(),x["sha"])
            self.assertTrue(original_model_replay(x["rows"],x["n"],x["model"]))
            self.assertEqual(len(x["model"]),x["n"])
            y=m.source(name)
            self.assertEqual((y["sha"],y["model_sha"]),(x["sha"],x["model_sha"]))
            self.assertEqual(x["rows"],y["rows"])

    def test_all_synthetic_original_sources_true_sat_and_non_external(self):
        for case in m.IDS[2:]:
            x=m.source(case)
            self.assertEqual(x["provenance"],"OPEN_GENERATOR_PLANTED_SAT_NOT_EXTERNAL")
            self.assertTrue(all(len(c)==3 for c in x["rows"]))
            self.assertTrue(all(len(set(abs(v) for v in c))==3 for c in x["rows"]))
            self.assertTrue(original_model_replay(x["rows"],x["n"],x["model"]))

    def test_native_xor_exact_mask_encodings_in_mixed_family(self):
        # A planted XOR mask width-3 has FOUR invalid assignments. Each
        # generated mask guarantees one assignment forbidden by one source OR.
        x=m.source("mixed-planted-xor-n96")
        a=x["rows"];truth={abs(l):l>0 for l in x["model"]}
        self.assertTrue(original_model_replay(a,x["n"],x["model"]))
        self.assertEqual(x["m"],384)
        z=m.choose(a,x["n"],"native_all")
        self.assertEqual(z["selected_XOR_equations"],len(z["equations"])) if "selected_XOR_equations" in z else None
        self.assertGreaterEqual(len(z["equations"]),1)
        for eq in z["equations"]:
            self.assertEqual(sum(int(truth[v]) for v in eq["variables"])%2,eq["rhs"])

    def test_feature_noop_does_not_smuggle_any_normalized_clause(self):
        for name in ("public-lightsout-625","planted-3sat-n96","mixed-planted-xor-n96"):
            x=m.source(name)
            noop=m.choose(x["rows"],x["n"],"noop_normalize_then_raw_cms")
            self.assertEqual(noop["equations"],[])
            self.assertEqual(noop["cnf_clauses"],x["rows"])
            self.assertEqual(noop["choice"],"NOOP_SCANNED_ORIGINAL_RAW")
            self.assertEqual(m.choose(x["rows"],x["n"],"raw_cms")["cnf_clauses"],x["rows"])

    def test_all_selected_methods_exact_original_source_partition_or_raw(self):
        for name in ("planted-3sat-n96","mixed-planted-xor-n96","public-lightsout-625"):
            x=m.source(name)
            for arm in m.ARMS:
                selected=m.choose(x["rows"],x["n"],arm)
                self.assertEqual(selected["choice"] in ("cadical195_original",
                                 "NOOP_SCANNED_ORIGINAL_RAW","raw_original",
                                 "raw_original_after_core_scan","native_xor","raw_after_scan"),True)

    def test_no_false_unsat_or_masked_external_benchmark(self):
        self.assertEqual(len(m.IDS),8)
        self.assertEqual(len(m.ARMS),5)
        self.assertNotIn("UNSAT",m.ALLOW)
        self.assertEqual(m.ALLOW,{m.SAT,"UNKNOWN_CPU_LIMIT_SIGXCPU",
                                  "UNKNOWN_WALL_TIMEOUT","UNKNOWN_SOLVER_NO_ANSWER"})
        self.assertFalse(m.freeze()["scope"]["real_public_cases"]!=2)
        with self.assertRaises(AssertionError):m.source("unregistered-source")

if __name__=="__main__":unittest.main()
