#!/usr/bin/env python3
"""004D3B original SHA, algebraic UNSAT and specialized-model controls."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"/"direct"))
from janus_time_sat_004d3_compare import (
    CASES, ARMS, CPU, WALL, REPEATS, AS_BYTES,
    read_exact,run_one,model_valid,
)

class NewSourceCompare(unittest.TestCase):
    def test_two_exact_original_competition_sha_and_dimensions(self):
        self.assertEqual(len(CASES),2)
        for name,meta in CASES.items():
            rows=read_exact(name)
            self.assertEqual(len(rows),meta["m"])
            self.assertGreater(meta["n"],240)
            self.assertEqual(len(meta["sha256"]),64)

    def test_janus_new_sat_and_unsat_original_provenance(self):
        a=run_one("lightsout_new_sat","janus_gf2",read_exact("lightsout_new_sat"))
        self.assertEqual(a["verdict"],"SAT_ORIGINAL_CNF_MODEL_VERIFIED")
        b=run_one("lightsout_new_unsat","janus_gf2",read_exact("lightsout_new_unsat"))
        self.assertEqual(b["verdict"],"GF2_UNSAT_SOURCE_COMBINATION_REPLAYED_SAME_ADMIN")
        self.assertGreater(b["algebraic_certificate"]["equation_combination_length"],0)
        self.assertEqual(b["algebraic_certificate"]["portable_DRUP_LRAT"],"NOT_PRODUCED")

    def test_original_source_native_xor_solver_reports_consistent_verdicts(self):
        for name in CASES:
            r=run_one(name,"cryptominisat_native_xor",read_exact(name))
            expectation=("SAT_ORIGINAL_CNF_MODEL_VERIFIED" if name=="lightsout_new_sat"
                         else "UNSAT_SOLVER_ONLY_NO_PORTABLE_PROOF")
            self.assertEqual(r["verdict"],expectation)

    def test_full_original_model_verification_rejects_false_or_missing(self):
        self.assertFalse(model_valid([(1,)],1,{1:False}))
        self.assertFalse(model_valid([(1,)],1,{}))
        self.assertTrue(model_valid([(1,-2)],2,{1:True,2:False}))
        self.assertFalse(model_valid([()],2,{1:True,2:True}))

    def test_predeclared_budgets_and_exact_five_arms(self):
        self.assertEqual((CPU,WALL,REPEATS,AS_BYTES),(8,11,3,2_147_483_648))
        self.assertEqual(len(ARMS),5)

if __name__=="__main__":unittest.main()
