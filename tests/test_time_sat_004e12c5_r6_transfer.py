#!/usr/bin/env python3
"""R6 frozen prospective-only cost selection proof tests."""
from hashlib import sha256
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"/"direct"))
import janus_time_sat_004e12c5_r6_model as r6
import janus_time_sat_004e12c5_r6_benchmark as bench
import janus_time_sat_004e12c5_r6_audit as audit

class R6PreSolveCostTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fit=r6.fit_from_past()

    def test_only_R5_train_old_sha_not_R6(self):
        p,sha=r6.frozen_protocol()
        self.assertEqual(p["status"],"FROZEN_BEFORE_ANY_R6_SAT_MEASUREMENTS")
        self.assertEqual(len(p["new_sources"]),12)
        self.assertEqual(len(self.fit["training_original_SHA256"]),12)
        self.assertEqual(len(set(self.fit["training_original_SHA256"])),12)
        self.assertTrue(self.fit["no_R6_source_used_for_fit"])
        self.assertEqual(self.fit["prereg_sha256"],sha)
        self.assertEqual(self.fit["n_distinct_GITUB_Hosts"],2)

    def test_new_source_cnf_sha_disjoint_unique_and_planted_sat(self):
        new=[]
        train=set(self.fit["training_original_SHA256"])
        for case,kind,n,w,eq,seed,dmg,extra in r6.CASES:
            size,rows=r6.source(case)
            self.assertEqual(size,n)
            h=r6.r1.original_sha(rows,n)
            self.assertNotIn(h,train)
            new.append(h)
            self.assertTrue(rows)
            f,cert=r6.signmask_profile(rows,n)
            self.assertGreaterEqual(f["complete_block_fraction"],0)
            self.assertLessEqual(f["complete_block_fraction"],1)
            if kind=="EXACT_RANDOM_XOR":
                self.assertTrue(f["whole_original_exact_xor"],case)
                self.assertIsNotNone(cert)
            else:
                self.assertFalse(f["whole_original_exact_xor"],case)
                self.assertIsNone(cert)
        self.assertEqual(len(set(new)),12)

    def test_prior_width3_cost_improvement_gate_is_empirically_grounded(self):
        history=self.fit["historical_cases"]["r5_xor3_96"]
        self.assertEqual(len(history["prior_hosts"]),2)
        for source in history["prior_hosts"]:
            self.assertGreaterEqual(source["GF2_over_fastest"],1.15)
        self.assertTrue(self.fit["decisions"]["gf2_width3_supported"])

    def test_width3_width4_width5_new_selector_chooses_proven_full_gf2(self):
        for key in ("r6_xor3_80","r6_xor3_128","r6_xor4_128","r6_xor5_160"):
            n,rows=r6.source(key)
            selected,proof,reason,info=r6.choose(rows,n,self.fit)
            self.assertEqual(selected,"janus_gf2",key)
            self.assertIsNotNone(proof)
            self.assertGreaterEqual(info["confidence_lower_bound_gain"],1.15)
            self.assertIsNotNone(info["forecast"])
            model,status,count=r6.r3.gf2(rows,n,proof)
            self.assertIsNone(status)
            self.assertTrue(r6.r1.cnf_ok(rows,model),key)

    def test_width6_unsupported_remains_certified_native_xor(self):
        n,rows=r6.source("r6_xor6_96")
        engine,cert,why,diag=r6.choose(rows,n,self.fit)
        self.assertEqual(engine,"cryptominisat_native_xor")
        self.assertIsNotNone(cert)

    def test_mixed_width4_uses_CaDiCaL_cost_not_wrong_GF2(self):
        for key in ("r6_mixed4_112","r6_mixed4_144"):
            n,rows=r6.source(key)
            engine,cert,reason,diag=r6.choose(rows,n,self.fit)
            self.assertEqual(engine,"cadical195_original_cnf",key)
            self.assertIsNone(cert)
            self.assertIsNotNone(diag["forecast"])
            history=self.fit["historical_cases"]["r5_mixed4_112"]
            self.assertTrue(all(h["CMS_original_over_CaDiCaL"]>=1.5 for h in history["prior_hosts"]))

    def test_partial_mixed_width5_and_standard_3cnf_abstain_from_GF2(self):
        expected={
            "r6_partial4_128":"cadical195_original_cnf",
            "r6_partial5_128":"cryptominisat_original_cnf",
            "r6_mixed5_128":"cryptominisat_original_cnf",
            "r6_3cnf96":"cryptominisat_original_cnf",
            "r6_3cnf144":"cryptominisat_original_cnf"}
        for key,want in expected.items():
            n,rows=r6.source(key)
            chosen,cert,reason,diag=r6.choose(rows,n,self.fit)
            self.assertEqual(chosen,want,key)
            self.assertIsNone(cert,key)

    def test_missing_original_XOR_clause_defeats_full_certification(self):
        n,rows=r6.source("r6_xor4_128")
        partial=rows[:-1]
        chosen,proof,reason,diag=r6.choose(partial,n,self.fit)
        self.assertNotIn(chosen,("janus_gf2","cryptominisat_native_xor"))
        self.assertIsNone(proof)
        with self.assertRaises(AssertionError):
            r6.r3.gf2(partial,n)

    def test_fit_SHA_and_auditor_two_host_fail_closed(self):
        with TemporaryDirectory() as t:
            f=Path(t)/"FIT.json"
            f.write_bytes(r6.canonical(self.fit))
            self.assertEqual(bench.read_fit(f,sha256(f.read_bytes()).hexdigest())["training_original_SHA256"],
                self.fit["training_original_SHA256"])
            with self.assertRaises(AssertionError):
                bench.read_fit(f,"0"*64)
        with self.assertRaisesRegex(AssertionError,"R6_NEED_TWO_FULL_HOST_REPORTS"):
            audit.audit([])
        with self.assertRaisesRegex(AssertionError,"R6_NEED_TWO_FULL_HOST_REPORTS"):
            audit.audit([{}])

if __name__=="__main__":
    unittest.main()
