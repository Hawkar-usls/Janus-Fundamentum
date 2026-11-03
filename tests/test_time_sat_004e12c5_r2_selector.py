#!/usr/bin/env python3
"""No benchmark timing or R2-label training: prereg and fail-closed tests."""
import unittest
from unittest.mock import patch
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"/"direct"))
import janus_time_sat_004e12c5_r2_selector as r2
import janus_time_sat_004e12c5_r2_audit as audit

class R2FrozenSelectorTests(unittest.TestCase):
    def test_prereg_and_training_evidence_cannot_mutate(self):
        p, h=r2.protocol()
        self.assertEqual(p["selector_frozen_before_tests"]["threshold_variables"],500)
        self.assertEqual(len(h),64)
        self.assertEqual(len(p["new_unseen_cases"]),4)

    def test_new_originals_have_unique_sha_and_provably_sat(self):
        originals=[]
        for case,side,seed in r2.CASES:
            n,rows=r2.source(case)
            self.assertEqual(n,side*side)
            cover=r2.r1.group_parity_equations(rows,n)
            self.assertEqual(cover["status"],"EXACT_XOR_COVER_PASS")
            self.assertEqual(len(cover["equations"]),n)
            model,other,_=r2.gf2(rows,n,cover)
            self.assertIsNone(other)
            self.assertTrue(r2.r1.cnf_ok(rows,model))
            originals.append(r2.r1.original_sha(rows,n))
        self.assertEqual(len(set(originals)),4)

    def test_no_test_time_learning_and_correct_21_23_boundary(self):
        for case,side,seed in r2.CASES:
            n,rows=r2.source(case)
            engine,cover,reason=r2.choose_pre_solver(rows,n)
            if side==21:
                self.assertEqual(engine,"cadical195_original_cnf")
                self.assertIsNone(cover)
            else:
                self.assertEqual(engine,"janus_gf2")
                self.assertIsNotNone(cover)
            self.assertEqual(r2.choose_pre_solver(rows,n)[0],engine)

    def test_cannot_treat_partial_xor_as_certified_solver(self):
        n,rows=r2.source("new_r2_grid_23")
        tampered=rows[:-1]
        chosen,cert,reason=r2.choose_pre_solver(tampered,n)
        self.assertEqual(chosen,"cadical195_original_cnf")
        self.assertIsNone(cert)
        self.assertEqual(reason,"NO_EXACT_CERTIFICATE")
        with self.assertRaises(AssertionError):
            r2.gf2(tampered,n)

    def test_R1_generator_consistency_and_same_admin_unsat_guard(self):
        for side,seed in ((19,202611030519),(25,202611030525),(37,202611030537)):
            n,rows=r2.grid(side,seed)
            a,b,status=r2.r1.generate_grid(side,seed)
            self.assertEqual((n,rows),(a,b))
            self.assertEqual(status,"SAT")
        n,rows,status=r2.r1.source("old_unsat_guard")
        self.assertEqual(status,"UNSAT")
        self.assertEqual(r2.r1.solve_if_exact_xor(rows,n)["verdict"],
                         "GF2_UNSAT_SAME_ADMIN_REPLAY_ONLY")

    def test_audit_requires_two_hosts_and_pinned_protocol(self):
        with self.assertRaisesRegex(AssertionError,"TWO_HOSTS_REQUIRED"):
            audit.audit([])
        with self.assertRaisesRegex(AssertionError,"TWO_HOSTS_REQUIRED"):
            audit.audit([{}])

if __name__=="__main__":
    unittest.main()
