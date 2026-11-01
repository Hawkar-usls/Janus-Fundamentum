#!/usr/bin/env python3
"""TIME-SAT-003 A/B/C falsification and proof tamper checks."""
import random
import sys
import unittest
from dataclasses import replace
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"/"direct"))

from janus_time_sat_003 import (ARMS,Wedge,direct_wedges,replay_wedges,
                                frozen_forecast,run_arm)
from janus_time_sat_003_drup_witness import (
    verify_drup,produce_and_check,ProofNotVerified)
from janus_time_sat_partial_001 import canonical_sat_cnf
from janus_ufr_001 import normalize,verify_model


class TimeSat003Tests(unittest.TestCase):
    def test_direct_unit_resolution_is_sound_and_original_index_replay(self):
        cnf=((-1,2),(-1,-2),(3,1))
        witnesses,litcount,occ=direct_wedges(cnf,3)
        self.assertEqual(tuple(w.literal for w in witnesses),(-1,))
        self.assertTrue(replay_wedges(cnf,witnesses))
        self.assertEqual(litcount,6)
        self.assertEqual(occ[1],3)
        for w in (replace(witnesses[0],literal=1),
                  replace(witnesses[0],second_idx=2),
                  replace(witnesses[0],companion=3),
                  replace(witnesses[0],first_idx=-1)):
            with self.assertRaises(AssertionError):
                replay_wedges(cnf,(w,))

    def test_unit_rule_proves_no_false_positive_under_random_sat(self):
        rng=random.Random(20261101)
        sample=0
        for kind in ("SAT","EXACT_ONE"):
            for n in range(2,7):
                for _ in range(25):
                    source=tuple(tuple(rng.choice((-1,1))*rng.randint(1,n)
                                       for __ in range(rng.randrange(4)))
                                       for ___ in range(rng.randrange(9)))
                    cnf=canonical_sat_cnf(source,n,kind)
                    units,_,_=direct_wedges(cnf,n)
                    self.assertTrue(replay_wedges(cnf,units))
                    solutions=[bits for bits in range(1<<n)
                              if verify_model(normalize(source),
                                              {i:bool(bits>>(i-1)&1)
                                               for i in range(1,n+1)},kind)]
                    for bits in solutions:
                        self.assertTrue(all(bool(bits>>(abs(w.literal)-1)&1)
                                        ==(w.literal>0) for w in units))
                    sample+=1
        self.assertEqual(sample,250)

    def test_tautology_and_complementary_cnf_do_not_forge_unit(self):
        for cnf in (((1,-1),),((1,1),),((1,2),(1,-2),(-1,3),(-1,-3))):
            units,_,_=direct_wedges(cnf,3)
            self.assertTrue(replay_wedges(cnf,units))
            if len(cnf)==4:
                self.assertEqual(units,()) # contradictory forced values rejected

    def test_forecast_is_source_only_conservative_and_freezes_small_skip(self):
        cnf=((-1,2),(-1,-2))
        w,lit,occ=direct_wedges(cnf,3)
        forecast=frozen_forecast(3,cnf,w,lit,occ)
        self.assertFalse(forecast.admit)
        self.assertEqual(forecast.reason,"TOO_SMALL_TO_AMORTIZE")
        self.assertEqual(forecast.candidate_count,1)
        self.assertEqual(forecast.estimated_net_work_units,
                         forecast.estimated_saved_work_units-
                         forecast.estimated_scan_work_units-
                         forecast.estimated_audit_work_units-
                         forecast.estimated_insert_work_units)

    def test_raw_direct_forecast_legacy_same_correct_answer(self):
        rows=((-1,2),(-1,-2),(1,3))
        for engine in ("cadical195","glucose4"):
            got={}
            for arm in ARMS:
                x=run_arm(rows,3,"SAT",solver_name=engine,arm=arm)
                got[arm]=x["status"]
                self.assertTrue(x["model_independently_verified"])
                self.assertEqual(x["audit_count"],len(x["derived_units"]))
            self.assertEqual(set(got.values()),{"SAT"})
            self.assertEqual(run_arm(rows,3,"SAT",solver_name=engine,
                           arm="forecast")["derived_units"],[])
            self.assertIn(-1,run_arm(rows,3,"SAT",solver_name=engine,
                           arm="direct")["derived_units"])

    def test_injected_extraction_failure_does_not_fake_unsat_or_a_unit(self):
        rows=((-1,2),(-1,-2))
        x=run_arm(rows,3,"SAT",solver_name="cadical195",
                  arm="direct",inject_fault=True)
        self.assertTrue(x["fault_fallback"])
        self.assertEqual(x["derived_units"],[])
        self.assertEqual(x["status"],"SAT")
        with self.assertRaises(ValueError):
            run_arm(rows,3,"SAT",solver_name="cadical195",arm="cheat")

    def test_drup_prover_and_independent_checker_real_unsat(self):
        cnf=((1,),(-1,))
        receipt=produce_and_check(cnf)
        self.assertEqual(receipt["solver_status"],"UNSAT")
        self.assertEqual(receipt["proof_status"],"INDEPENDENT_RUP_REPLAY_PASS")
        receipt=produce_and_check(((1,2),))
        self.assertEqual(receipt["solver_status"],"SAT")
        with self.assertRaises(ProofNotVerified):
            verify_drup(((1,2),),["0"])
        with self.assertRaises(ProofNotVerified):
            verify_drup(((1,2),),["1 0","0"])
        with self.assertRaises(ProofNotVerified):
            verify_drup(((1,2),),["invalid 0"])
        with self.assertRaises(ProofNotVerified):
            verify_drup(((1,2),),[])

    def test_drup_full_16_cube_unsat_core(self):
        core=tuple(tuple((-v if mask>>(v-1)&1 else v) for v in range(1,5))
                   for mask in range(16))
        receipt=produce_and_check(core)
        self.assertEqual(receipt["proof_status"],"INDEPENDENT_RUP_REPLAY_PASS")


if __name__=="__main__":
    unittest.main()
