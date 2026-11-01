#!/usr/bin/env python3
"""TIME-SAT-004D0: adversarial correctness plus >240 variable regression."""
import random
import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"/"direct"))
from janus_time_sat_004d_adapter import (
    ARMS,derive_binary_wedges,independently_replay_witnesses,frozen_cost,run
)
from janus_time_sat_004b_baselines import classify_nonzero_exit


class TimeSat004D0Tests(unittest.TestCase):
    def test_genuine_original_source_wedge_and_independent_replay(self):
        cnf=((-1,2),(-1,-2),(1,3))
        witnesses,count,reason,occ=derive_binary_wedges(cnf,300)
        self.assertEqual(reason,"COMPLETE")
        self.assertEqual(witnesses,((-1,0,1,2),))
        self.assertEqual(independently_replay_witnesses(cnf,witnesses),1)
        self.assertEqual(count,6)
        self.assertFalse(frozen_cost(300,3,witnesses,count,occ)["admit"])
        with self.assertRaises(AssertionError):
            independently_replay_witnesses(cnf,((1,0,1,2),))
        with self.assertRaises(AssertionError):
            independently_replay_witnesses(cnf,((-1,0,2,2),))

    def test_exhaustive_small_random_model_equivalence(self):
        rng=random.Random(20261104)
        for n in range(2,7):
            for _ in range(24):
                rows=tuple(tuple(rng.choice((-1,1))*rng.randint(1,n)
                                 for ___ in range(rng.randint(0,3)))
                           for __ in range(rng.randint(0,7)))
                ws,_,reason,_=derive_binary_wedges(rows,n)
                self.assertEqual(reason,"COMPLETE")
                independently_replay_witnesses(rows,ws)
                for assignment_bits in range(1<<n):
                    assignment={v:bool((assignment_bits>>(v-1))&1) for v in range(1,n+1)}
                    sat=all(any(assignment[abs(l)]==(l>0) for l in row) for row in rows)
                    if sat:
                        for lit,*_ in ws:
                            self.assertEqual(assignment[abs(lit)],lit>0)

    def test_frozen_forecast_not_cheating_from_timing_or_answers(self):
        cnf=((-1,2),(-1,-2))
        ws,count,_,occ=derive_binary_wedges(cnf,300)
        a=frozen_cost(300,len(cnf),ws,count,occ)
        b=frozen_cost(300,len(cnf),ws,count,occ)
        self.assertEqual(a,b)
        self.assertNotIn("solver_seconds",a)
        self.assertNotIn("oracle_answer",a)

    def test_limit_returns_no_partial_unverified_units(self):
        rows=((-1,2),(-1,-2),(3,4))
        w,_,reason,_=derive_binary_wedges(rows,300,max_scan=4)
        self.assertEqual(reason,"SCAN_LITERAL_BUDGET")
        self.assertEqual(w,())
        w,_,reason,_=derive_binary_wedges(rows,300,max_entries=1)
        self.assertEqual(reason,"BINARY_INDEX_BUDGET")
        self.assertEqual(w,())

    def test_large_n300_old_240_cap_not_invoked(self):
        rows=((-1,2),(-1,-2),(1,3),(300,))
        result={arm:run(rows,300,"cadical195",arm) for arm in ARMS}
        self.assertEqual({v["verdict"] for v in result.values()},
                         {"SAT_ORIGINAL_MODEL_VERIFIED"})
        self.assertEqual(result["janus_direct"]["derived_units"],[-1])
        self.assertEqual(result["feature_only"]["derived_units"],[])
        self.assertEqual(result["janus_frozen_forecast"]["derived_units"],[])
        for value in result.values():
            self.assertEqual(value["unsat_portable_proof"],"NOT_PRODUCED")

    def test_signal_is_unknown_not_unsat(self):
        self.assertEqual(classify_nonzero_exit(-24)["verdict"],"UNKNOWN_CPU_LIMIT_SIGXCPU")
        self.assertNotIn("UNSAT",classify_nonzero_exit(-9)["verdict"])
        with self.assertRaises(ValueError):
            classify_nonzero_exit(0)

    def test_contradictory_implications_do_not_forge_unsat(self):
        rows=((1,2),(1,-2),(-1,3),(-1,-3))
        w,*_=derive_binary_wedges(rows,300)
        self.assertEqual(w,())
        output=run(rows,300,"glucose4","janus_direct")
        self.assertEqual(output["verdict"],"UNSAT_SOLVER_ONLY_NOT_CERTIFIED")
        self.assertEqual(output["derived_units"],[])


if __name__=="__main__":
    unittest.main()
