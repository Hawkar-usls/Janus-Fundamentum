#!/usr/bin/env python3
"""R3 frozen source shape/topology and no-peeking requirements. No timing fit."""
import unittest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"/"direct"))
import janus_time_sat_004e12c5_r3_selector as r3
import janus_time_sat_004e12c5_r3_audit as audit

class E12C5R3TheoryTests(unittest.TestCase):
    def test_R1_and_R2_training_reports_are_frozen_before_new_data(self):
        protocol, sha=r3.protocol()
        self.assertEqual(protocol["status"],"FROZEN_BEFORE_ANY_R3_MEASUREMENT")
        self.assertEqual(len(protocol["training_only"]),2)
        self.assertEqual(len(sha),64)
        self.assertEqual(protocol["pre_solve_selector"]["max_literal_scan_research_only"],140000)

    def test_new_sources_unique_and_original_sat_models_verifiable(self):
        original_shas=[]
        for case,side,seed in r3.CASES:
            n,rows=r3.source(case)
            self.assertEqual(n,side*side)
            cover=r3.r1.group_parity_equations(rows,n)
            self.assertEqual(cover["status"],"EXACT_XOR_COVER_PASS",case)
            self.assertTrue(r3.verified_lightsout_supports(cover,n,side))
            self.assertEqual(len(cover["equations"]),n)
            model,status,_=r3.gf2(rows,n,cover)
            self.assertIsNone(status)
            self.assertTrue(r3.r1.cnf_ok(rows,model))
            original_shas.append(r3.r1.original_sha(rows,n))
        self.assertEqual(len(set(original_shas)),len(r3.CASES))

    def test_frozen_mod4_selector_does_not_receive_solver_result_or_source_id(self):
        proto,_=r3.protocol()
        for case,side,seed in r3.CASES:
            n,rows=r3.source(case)
            chosen,proof,reason=r3.choose_pre_solver(rows,n)
            expected=next(x["expect_engine"] for x in proto["new_unseen_cases"]
                          if x["id"]==case)
            self.assertEqual(chosen,expected)
            self.assertEqual(r3.choose_pre_solver(rows,n)[0],chosen)
            if chosen=="janus_gf2":
                self.assertIsNotNone(proof)
            else:
                self.assertIsNone(proof)

    def test_missing_clause_prevents_GF2_on_33_and_41(self):
        for case in ("r3_grid_33","r3_grid_41a"):
            n,rows=r3.source(case)
            partial=rows[:-1]
            self.assertNotEqual(
                r3.r1.group_parity_equations(partial,n)["status"],
                "EXACT_XOR_COVER_PASS")
            engine,certificate,reason=r3.choose_pre_solver(partial,n)
            self.assertEqual(engine,"cryptominisat_original_cnf")
            self.assertIsNone(certificate)
            with self.assertRaises(AssertionError):
                r3.gf2(partial,n)

    def test_exact_XOR_without_grid_topology_cannot_use_mod4_grid_rule(self):
        n,rows=r3.source("r3_grid_33")
        def swap(lit):
            num=abs(lit)
            v=2 if num==1 else 1 if num==2 else num
            return v if lit>0 else -v
        permuted=[[swap(lit) for lit in row] for row in rows]
        cover=r3.r1.group_parity_equations(permuted,n)
        self.assertEqual(cover["status"],"EXACT_XOR_COVER_PASS")
        self.assertFalse(r3.verified_lightsout_supports(cover,n,33))
        engine,certificate,reason=r3.choose_pre_solver(permuted,n)
        self.assertEqual(engine,"cryptominisat_original_cnf")
        self.assertIsNone(certificate)

    def test_prior_R1_generator_unchanged_and_old_UNSAT_only_same_admin(self):
        for side,seed in ((19,202611030519),(25,202611030525),(37,202611030537)):
            a,b=r3.grid(side,seed)
            aa,bb,status=r3.r1.generate_grid(side,seed)
            self.assertEqual((a,b),(aa,bb))
            self.assertEqual(status,"SAT")
        n,rows,status=r3.r1.source("old_unsat_guard")
        self.assertEqual(status,"UNSAT")
        self.assertEqual(
            r3.r1.solve_if_exact_xor(rows,n)["verdict"],
            "GF2_UNSAT_SAME_ADMIN_REPLAY_ONLY")

    def test_two_host_audit_never_accepts_missing_receipt(self):
        with self.assertRaisesRegex(AssertionError,"TWO_HOSTS_REQUIRED"):
            audit.audit([])
        with self.assertRaisesRegex(AssertionError,"TWO_HOSTS_REQUIRED"):
            audit.audit([{}])

if __name__=="__main__":
    unittest.main()
