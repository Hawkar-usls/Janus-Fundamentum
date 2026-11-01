#!/usr/bin/env python3
"""TIME-SAT-PARTIAL-002: adversarial gate and CDCL fallback tests."""
from __future__ import annotations
import random
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"/"direct"))
from janus_time_sat_partial_002 import cheap_features, run_arm, ARMS
from janus_time_sat_partial_001 import canonical_sat_cnf
from janus_ufr_001 import normalize, verify_model


class TimeSatPartial002Tests(unittest.TestCase):
    def test_contradictory_binary_motif_admits_without_future_or_answer(self):
        rows=((-1,2),(-1,-2))
        check=cheap_features(canonical_sat_cnf(rows,3,"SAT"),3)
        self.assertTrue(check.admitted)
        self.assertEqual(check.reason,"WEDGE_ADMITTED")
        self.assertIn(-1,check.binary_wedge_targets)
        self.assertEqual(check.unit_clauses,0)
        result=run_arm(rows,3,"SAT",solver_name="cadical195",arm="adaptive")
        self.assertEqual(result["answer"],"SAT")
        self.assertTrue(result["probe_ran"])
        self.assertTrue(result["model_verified"])
        self.assertEqual(result["independent_unit_checks"],
                         len(result["derived_units"]))

    def test_all_large_known_bad_examples_are_skipped(self):
        for n in (18,220,240):
            rows=tuple((i,i+1,i+2) for i in range(1,min(70,n-2)))
            gate=cheap_features(canonical_sat_cnf(rows,n,"SAT"),n)
            self.assertFalse(gate.admitted)
            self.assertFalse(gate.binary_wedge_count)
            self.assertIn(gate.reason,("INSTANCE_TOO_LARGE","NO_BINARY_WEDGE"))
        for n in (220,240):
            rows=((1,2,3),(-1,-2,3))
            report=run_arm(rows,n,"SAT",solver_name="cadical195",
                           arm="adaptive")
            self.assertFalse(report["probe_ran"])
            self.assertEqual(report["answer"],"SAT")

    def test_unit_clauses_and_missing_wedge_deny_admission(self):
        rows=((-1,2),(-1,-2),(3,))
        self.assertEqual(cheap_features(rows,3).reason,"HAS_UNIT_CLAUSES")
        rows=((1,2),(1,3),(-1,2))
        self.assertEqual(cheap_features(rows,3).reason,"NO_BINARY_WEDGE")

    def test_truncated_or_faulted_probe_falls_back_exact_original_cdcl(self):
        rows=((-1,2),(-1,-2),(1,3))
        for solver in ("cadical195","glucose4"):
            raw=run_arm(rows,3,"SAT",solver_name=solver,arm="raw")
            interrupted=run_arm(rows,3,"SAT",solver_name=solver,
                                arm="adaptive",fault_probe=True)
            self.assertEqual(raw["answer"],interrupted["answer"])
            self.assertTrue(interrupted["model_verified"])
            self.assertEqual(interrupted["derived_units"],[])
            self.assertEqual(interrupted["preprocessor_fallback"],"TimeoutError")
        with self.assertRaises(ValueError):
            run_arm(rows,3,"SAT",solver_name="cadical195",arm="future_is_true")

    def test_gate_never_uses_results_or_external_solver_time(self):
        rows=((-1,2),(-1,-2))
        obj=cheap_features(rows,4)
        self.assertEqual(obj,cheap_features(tuple(reversed(rows)),4))
        self.assertFalse(hasattr(obj,"SAT_answer"))
        self.assertFalse(hasattr(obj,"elapsed_seconds"))
        with self.assertRaises(ValueError):
            cheap_features(((5,),),4)

    def test_random_same_answer_across_four_arms_and_two_engines(self):
        rng=random.Random(20261101)
        count=0
        for kind in ("SAT","EXACT_ONE"):
            for n in range(2,7):
                for _ in range(12):
                    rows=tuple(tuple(rng.choice((-1,1))*rng.randint(1,n)
                        for __ in range(rng.randint(0,4)))
                        for ___ in range(rng.randint(0,7)))
                    source=normalize(rows)
                    expected=any(
                        verify_model(source,{
                            v:bool((x>>(v-1))&1) for v in range(1,n+1)
                        },kind) for x in range(1<<n))
                    for solver in ("cadical195","glucose4"):
                        for arm in ARMS:
                            result=run_arm(rows,n,kind,solver_name=solver,arm=arm)
                            self.assertEqual(result["answer"]=="SAT",expected)
                            self.assertEqual(result["model_verified"],expected)
                            self.assertEqual(result["independent_unit_checks"],
                                             len(result["derived_units"]))
                            self.assertEqual(result["unsat_portable_proof"],
                                             "NOT_PRODUCED")
                            count+=1
        self.assertEqual(count,960)

    def test_no_probing_feature_only_control(self):
        motif=((-1,2),(-1,-2))
        for solver in ("cadical195","glucose4"):
            x=run_arm(motif,3,"SAT",solver_name=solver,arm="feature_only")
            self.assertFalse(x["probe_ran"])
            self.assertIsNotNone(x["gate"])
            self.assertTrue(x["gate"]["admitted"])
            self.assertEqual(x["derived_units"],[])
            self.assertEqual(x["independent_unit_checks"],0)

if __name__=="__main__":
    unittest.main()
