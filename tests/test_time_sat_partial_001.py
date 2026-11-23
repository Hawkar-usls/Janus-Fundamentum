#!/usr/bin/env python3
"""TIME-SAT-PARTIAL-001: attack tests on SAT/Exact-One partial consistency."""
from __future__ import annotations
from itertools import product
from pathlib import Path
import random
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"/"direct"))
from janus_time_sat_partial_001 import (
    canonical_sat_cnf, prepare, audit_units, one_run,
)
from janus_ufr_001 import verify_model, normalize


def reference(rows,n,kind):
    return [x for x in range(1<<n) if verify_model(normalize(rows), {
        i:bool((x>>(i-1))&1) for i in range(1,n+1)
    },kind)]


def check_cnf(cnf,n,x):
    return all(any(bool((x>>(abs(l)-1))&1)==(l>0) for l in row)
               for row in cnf)


class TimeSatPartial001Tests(unittest.TestCase):
    def test_exact_one_encoding_matches_literal_multiplicity(self):
        cases=[
            (((1,1),),2,"EXACT_ONE"),
            (((1,-1),),2,"EXACT_ONE"),
            (((1,1,-2),),2,"EXACT_ONE"),
            (((1,-1,2),),2,"EXACT_ONE"),
            (((),),2,"EXACT_ONE"),
            (((1,2,3),(-2,4)),4,"EXACT_ONE"),
            (((1,1,1),),2,"EXACT_ONE"),
        ]
        for rows,n,kind in cases:
            cnf=canonical_sat_cnf(rows,n,kind)
            expected=reference(rows,n,kind)
            actual=[x for x in range(1<<n) if check_cnf(cnf,n,x)]
            self.assertEqual(expected,actual,(rows,kind))

    def test_fail_literal_lookahead_before_full_model(self):
        rows=((-1,2),(-1,-2))
        cnf=canonical_sat_cnf(rows,3,"SAT")
        forward=prepare(cnf,3,stage="forward",max_visits=2000)
        bidirectional=prepare(cnf,3,stage="bidirectional",max_visits=2000)
        self.assertEqual(forward.units,())
        self.assertIn(-1,bidirectional.units)
        self.assertGreater(bidirectional.rejected_probe_values,0)
        self.assertGreater(bidirectional.explored_literal_assumptions,0)
        self.assertEqual(audit_units(cnf,bidirectional.units),len(bidirectional.units))

    def test_adversarial_fake_unit_is_rejected_independently(self):
        cnf=canonical_sat_cnf(((1,2),),2,"SAT")
        with self.assertRaises(AssertionError):
            audit_units(cnf,(1,))
        with self.assertRaises(AssertionError):
            audit_units(cnf,(1,-1))
        with self.assertRaises(AssertionError):
            audit_units(cnf,(1,1))

    def test_quota_abort_does_not_prove_conflict(self):
        cnf=canonical_sat_cnf(((-1,2),(-1,-2)),3,"SAT")
        prep=prepare(cnf,3,stage="bidirectional",
                     max_visits=200,probe_share=0)
        self.assertTrue(prep.quota_exhausted)
        self.assertEqual(prep.units,())
        self.assertEqual(prep.rejected_probe_values,0)

    def test_random_native_sat_exact_one_equivalence_and_sound_derived_units(self):
        rng=random.Random(20261101)
        total=0
        for kind in ("SAT","EXACT_ONE"):
            for n in range(2,8):
                for _ in range(30):
                    rows=tuple(tuple(
                        rng.choice((-1,1))*rng.randint(1,n)
                        for _ in range(rng.randint(0,5))
                    ) for _ in range(rng.randint(0,8)))
                    cnf=canonical_sat_cnf(rows,n,kind)
                    models=reference(rows,n,kind)
                    encoded=[x for x in range(1<<n) if check_cnf(cnf,n,x)]
                    self.assertEqual(models,encoded)
                    for stage in ("forward","bidirectional"):
                        prep=prepare(cnf,n,stage=stage,max_visits=8000,
                                     probe_share=0.1,max_goal_vars=8)
                        if prep.units:
                            for x in models:
                                self.assertTrue(all(
                                    bool((x>>(abs(l)-1))&1)==(l>0)
                                    for l in prep.units
                                ),f"UNSOUND {stage} {rows} {prep.units}")
                        self.assertGreaterEqual(prep.original_clause_visits,0)
                    total+=1
        self.assertEqual(total,360)

    def test_correct_strong_solver_for_both_kinds_and_both_engines(self):
        cases=[
            (((1,),(-1,)),2,"SAT",False),
            (((1,2),(-1,2)),2,"SAT",True),
            (((1,1),),2,"EXACT_ONE",False),
            (((1,-1),),2,"EXACT_ONE",True),
            (((1,2,3),(-1,2)),3,"EXACT_ONE",True),
        ]
        for solver in ("cadical195","glucose4"):
            for rows,n,kind,expected in cases:
                for stage in ("raw","forward","bidirectional"):
                    result=one_run(rows,n,kind,solver_name=solver,
                                   stage=stage,max_visits=8000)
                    self.assertEqual(result["answer"]=="SAT",expected)
                    if expected:
                        self.assertTrue(result["model_independently_verified"])
                    else:
                        self.assertEqual(result["portable_unsat_proof"],"NOT_PRODUCED")

    def test_preprocessing_bounds_and_unknown_status_not_disguised(self):
        cnf=((1,2),(-1,3))
        for bad in ("retrocausal","future_leak","other"):
            with self.assertRaises(ValueError):
                prepare(cnf,3,stage=bad)
        for kwargs in ({"max_visits":0},{"probe_share":0.7},
                       {"max_goal_vars":-1},{"time_limit":45}):
            with self.assertRaises(ValueError):
                prepare(cnf,3,stage="bidirectional",**kwargs)
        result=prepare(cnf,3,stage="bidirectional",
                       max_visits=1,probe_share=0.05)
        self.assertEqual(result.units,())
        self.assertEqual(result.stage,"FORWARD_BUDGET_EXHAUSTED")

if __name__=="__main__":
    unittest.main()
