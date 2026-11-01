#!/usr/bin/env python3
"""TIME-SAT-004D8 original SAT model gate; no SAT claims from metadata."""
from __future__ import annotations
from copy import deepcopy
import itertools
import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"/"direct"))
from janus_time_sat_004d8_sat_gate import certified_model,gate_rank_for_sat
from janus_time_sat_004d7_rank_gate import source_rank_experiment
from janus_time_sat_004d1_xor import solve_if_exact_xor


class SATModelFirst(unittest.TestCase):
    def test_complete_original_model(self):
        rows=[(1,2),(-1,2),(2,-3)]
        r=certified_model(rows,3,[-1,2,-3])
        self.assertEqual(r["status"],"SAT_VERIFIED_EVERY_ORIGINAL_CLAUSE")
        self.assertEqual(r["verified_original_clause_count"],3)

    def test_forged_or_incomplete_model_rejected(self):
        rows=[(1,),(-2,)]
        for bad in ([],[1],[-1,-2],[1,2],[1,1],[True,-2],[1,0],[3,-2]):
            self.assertNotEqual(certified_model(rows,2,bad)["status"],
                                "SAT_VERIFIED_EVERY_ORIGINAL_CLAUSE")

    def test_unsat_original_has_no_sat_model(self):
        rows=[(1,),(-1,)]
        for model in ([1],[-1]):
            self.assertNotEqual(certified_model(rows,1,model)["status"],
                                "SAT_VERIFIED_EVERY_ORIGINAL_CLAUSE")

    def test_invalid_original_rejected(self):
        self.assertEqual(certified_model([(3,)],2,[1,2])["status"],
                         "BLOCK_INVALID_ORIGINAL_CNF")

    def test_no_promotion_without_model(self):
        for status in ("BLOCK_NO_VERIFIED_SAT_MODEL","UNSAT_PORTABLE_CERTIFIED",
                       "UNKNOWN_TIMEOUT","SAT_CATALOG_LABEL_ONLY"):
            self.assertEqual(gate_rank_for_sat({"status":status},None),
                             "BLOCK_NO_VERIFIED_SAT_MODEL")

    def test_model_and_rank_gates(self):
        a={"status":"SAT_VERIFIED_EVERY_ORIGINAL_CLAUSE"}
        good={"status":"SOURCE_PROOF_REPLAY_AND_EXACT_GF2_RANK_PASS",
              "independent_rank_analysis":{"source_plus_derived_GF2_inconsistent":False,
               "independent_new_coefficient_rank":1,
               "independent_new_augmented_rank":1}}
        self.assertTrue(gate_rank_for_sat(a,good).startswith("POTENTIAL_RESEARCH"))
        bad=deepcopy(good)
        bad["independent_rank_analysis"]["source_plus_derived_GF2_inconsistent"]=True
        self.assertEqual(gate_rank_for_sat(a,bad),
                         "BLOCK_DERIVED_GF2_CONFLICTS_WITH_VERIFIED_SAT_MODEL")
        bad=deepcopy(good)
        bad["independent_rank_analysis"]["independent_new_coefficient_rank"]=0
        self.assertEqual(gate_rank_for_sat(a,bad),
                         "BLOCK_NO_NEW_INDEPENDENT_GF2_RANK")
        self.assertEqual(gate_rank_for_sat(a,{"status":"BAD_PROOF"}),
                         "BLOCK_SOURCE_PROOF_NOT_REPLAYED")

    def test_source_only_models_satisfy_independent_exact_xor(self):
        # x xor y = 1; exact source sign masks (1,2), (-1,-2).
        rows=[(1,2),(-1,-2)]
        found=solve_if_exact_xor(rows,2)
        self.assertEqual(found["verdict"],"SAT_ORIGINAL_MODEL_VERIFIED")
        m=certified_model(rows,2,found["model"])
        self.assertEqual(m["status"],"SAT_VERIFIED_EVERY_ORIGINAL_CLAUSE")
        d=source_rank_experiment(rows,2)
        self.assertEqual(d["status"],"SOURCE_PROOF_REPLAY_AND_EXACT_GF2_RANK_PASS")
        self.assertEqual(gate_rank_for_sat(m,d),"BLOCK_NO_NEW_INDEPENDENT_GF2_RANK")

    def test_unsat_exact_xor_no_fake_model(self):
        rows=[(1,),(-1,)]
        result=solve_if_exact_xor(rows,1)
        self.assertNotEqual(result.get("verdict"),"SAT_ORIGINAL_MODEL_VERIFIED")

    def test_random_exhaustive_model_guard(self):
        import random
        rnd=random.Random(20261102008)
        for n in range(1,5):
            for _ in range(25):
                rows=[]
                for __ in range(rnd.randrange(2,8)):
                    vars_=rnd.sample(range(1,n+1),rnd.randrange(1,n+1))
                    rows.append(tuple(v if rnd.randrange(2) else -v for v in vars_))
                for bits in itertools.product((False,True),repeat=n):
                    signed=[i+1 if bits[i] else -(i+1) for i in range(n)]
                    direct=all(any(bits[abs(v)-1]==(v>0) for v in r) for r in rows)
                    certified=certified_model(rows,n,signed)["status"]=="SAT_VERIFIED_EVERY_ORIGINAL_CLAUSE"
                    self.assertEqual(direct,certified)

if __name__=="__main__":
    unittest.main()
