#!/usr/bin/env python3
"""Pre-R5 benchmarks structural/fit/cost tests; 12 future source SHAs isolated."""
from hashlib import sha256
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"/"direct"))
import janus_time_sat_004e12c5_r5_model as r5
import janus_time_sat_004e12c5_r5_benchmark as b
import janus_time_sat_004e12c5_r5_audit as audit

class R5FrozenTransferTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fit=r5.fit_from_prior()

    def test_prereg_unchanged_and_genuine_small_training(self):
        p,prereg_sha=r5.frozen()
        self.assertEqual(p["stage"],"R5 DEV ONLY; frozen before ANY R5 measurement")
        self.assertEqual(len(p["cohort"]),12)
        self.assertEqual(self.fit["prereg_sha256"],prereg_sha)
        self.assertEqual(self.fit["exact_non_grid_independent_original_count"],2)
        self.assertEqual(self.fit["R5_originals_in_fit"],0)
        self.assertEqual(set(self.fit["eligible_non_grid_exact_widths"]),{"4","5"})
        self.assertEqual(len(self.fit["R4_source_original_sha256"]),8)

    def test_no_inference_of_3_6_width_without_support(self):
        for case in ("r5_xor3_96","r5_xor6_128"):
            n,rows=r5.source(case)
            chosen,proof,reason,record=r5.choose(rows,n,self.fit)
            self.assertEqual(chosen,"cryptominisat_native_xor",case)
            self.assertIsNotNone(proof)
            self.assertIsNone(record["estimated_gain_lower_bound"])

    def test_exact_random_XOR_4_5_can_select_proven_GF2(self):
        for case in ("r5_xor4_112a","r5_xor4_160","r5_xor5_144a","r5_xor5_144b"):
            n,rows=r5.source(case)
            profile,cover=r5.feature_profile(rows,n)
            self.assertTrue(profile["exact_original_xor_cover"])
            self.assertFalse(profile["is_grid_topology"])
            self.assertIsNotNone(cover)
            chosen,proof,reason,pred=r5.choose(rows,n,self.fit)
            self.assertEqual(chosen,"janus_gf2",case)
            self.assertGreaterEqual(pred["estimated_gain_lower_bound"],1.25)
            self.assertEqual(len(pred["training_support_original_sha"]),1)
            signed,failed,num=r5.r3.gf2(rows,n,proof)
            self.assertIsNone(failed)
            self.assertEqual(num,n)
            self.assertTrue(r5.r1.cnf_ok(rows,signed))

    def test_partial_width4_can_use_cadical_but_never_gf2(self):
        n,rows=r5.source("r5_partial4_112")
        f,cert=r5.feature_profile(rows,n)
        self.assertFalse(f["exact_original_xor_cover"])
        self.assertEqual(f["incomplete_groups"],1)
        self.assertGreater(f["complete_group_fraction"],.98)
        self.assertIsNone(cert)
        chosen,proof,reason,diag=r5.choose(rows,n,self.fit)
        self.assertEqual(chosen,"cadical195_original_cnf")
        self.assertIsNone(proof)
        self.assertIsNone(diag["estimated_gain_lower_bound"])

    def test_partial_width5_and_mixed_3cnf_never_use_gf2(self):
        for case in ("r5_partial5_144","r5_mixed4_112","r5_mixed5_144",
                     "r5_three96","r5_three144"):
            n,rows=r5.source(case)
            f,cover=r5.feature_profile(rows,n)
            self.assertFalse(f["exact_original_xor_cover"])
            self.assertIsNone(cover)
            chosen,cert,reason,diag=r5.choose(rows,n,self.fit)
            self.assertEqual(chosen,"cryptominisat_original_cnf",case)
            self.assertIsNone(cert)

    def test_reuse_old_R4_generator_only_for_compatibility_not_training_on_R5(self):
        oldn,oldrows=r5.r4.planted_xor(96,4,96,202611031496)
        newn,newrows=r5.plant_random_xor(96,4,96,202611031496,0,0)
        self.assertEqual((oldn,oldrows),(newn,newrows))
        oldn,oldrows=r5.r4.source("r4_partial_xor4")
        newn,newrows=r5.plant_random_xor(96,4,96,202611031496,1,0)
        self.assertEqual((oldn,oldrows),(newn,newrows))

    def test_R5_source_SHAs_unique_and_not_R4_training(self):
        shas=[]
        training=set(self.fit["R4_source_original_sha256"].values())
        for case,*rest in r5.CASES:
            n,rows=r5.source(case)
            h=r5.r1.original_sha(rows,n)
            self.assertNotIn(h,training)
            self.assertEqual(len(h),64)
            shas.append(h)
        self.assertEqual(len(set(shas)),12)

    def test_fit_document_sha_and_tamper_detection(self):
        with TemporaryDirectory() as folder:
            file=Path(folder)/"FIT.json"
            file.write_bytes(r5.canonical(self.fit))
            digest=sha256(file.read_bytes()).hexdigest()
            self.assertEqual(b.read_fit(file,digest)["R4_source_original_sha256"],
                             self.fit["R4_source_original_sha256"])
            with self.assertRaises(AssertionError):b.read_fit(file,"0"*64)
            file.write_bytes(file.read_bytes()+b" ")
            with self.assertRaises(AssertionError):b.read_fit(file,digest)

    def test_external_audit_requires_complete_two_hosts(self):
        with self.assertRaisesRegex(AssertionError,"R5_NEED_TWO_FULL_HOST_REPORTS"):
            audit.audit([])
        with self.assertRaisesRegex(AssertionError,"R5_NEED_TWO_FULL_HOST_REPORTS"):
            audit.audit([{}])

if __name__=="__main__":
    unittest.main()
