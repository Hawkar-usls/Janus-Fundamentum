#!/usr/bin/env python3
"""Source-preserving challenger variants and fixed 24 job exploratory grid."""
from __future__ import annotations
import itertools
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"/"direct"))
import janus_time_sat_004e3_swarm as mod
from janus_time_sat_004d4_mixed_xor import representation_satisfied

def masks(variables,rhs):
    out=[]
    for bits in itertools.product((0,1),repeat=len(variables)):
        if sum(bits)%2==rhs:continue
        out.append(tuple(-v if bit else v for v,bit in zip(variables,bits)))
    return out

def holds(rows,values):
    return all(any(values[abs(l)]==(l>0) for l in row) for row in rows)

def transformed(form,values):
    return (all(sum(int(values[v]) for v in e["variables"])%2==e["rhs"]
                for e in form["equations"])
            and holds(form["cnf_clauses"],values))

class SwarmChecks(unittest.TestCase):
    def test_pinned_24_unique_jobs_and_resources(self):
        p=mod.frozen()
        self.assertEqual(len(mod.NAMES)*len(mod.VARIANTS),24)
        self.assertEqual(p["plan"]["maximum_simultaneously_requested"],20)
        self.assertEqual((mod.CPU,mod.WALL,mod.REPS),(6,10,2))
        self.assertEqual(len(set(mod.VARIANTS)),6)

    def test_all_six_policies_keep_all_truth_assignments(self):
        rows=masks((1,2),1)+masks((1,2,3),0)+[(4,)]
        # 2-bit and 3-bit complete XOR + original independent residual.
        for variant in mod.VARIANTS:
            x=mod.select_verified_xor(rows,4,variant)
            for assignment in itertools.product((False,True),repeat=4):
                values={i:bool(assignment[i-1]) for i in range(1,5)}
                self.assertEqual(holds(rows,values),transformed(x,values),
                                 msg=str((variant,assignment)))
            self.assertLessEqual(len(x["cnf_clauses"]),len(rows))
            self.assertEqual(x["converted_source_clauses"]+len(x["cnf_clauses"]),len(rows))

    def test_width_variants_are_meaningfully_different(self):
        rows=masks((1,2),1)+masks((1,2,3),0)+[(4,)]
        small=mod.select_verified_xor(rows,4,"native_width2_only")
        wide=mod.select_verified_xor(rows,4,"native_width3plus_only")
        allx=mod.select_verified_xor(rows,4,"native_all")
        self.assertEqual(len(small["equations"]),1)
        self.assertEqual(len(wide["equations"]),1)
        self.assertEqual(len(allx["equations"]),2)
        self.assertEqual(len(mod.select_verified_xor(rows,4,"raw_cms")["equations"]),0)
        self.assertEqual(len(mod.select_verified_xor(rows,4,"scan_noop_cms")["equations"]),0)

    def test_80_percent_gate_is_a_genuine_frozen_policy(self):
        rows=masks((1,2),1)+[(3,),(-4,),(-3,4)]
        gate=mod.select_verified_xor(rows,4,"adaptive_80")
        self.assertEqual(gate["equations"],[])
        self.assertEqual(len(gate["cnf_clauses"]),len(rows))

    def test_original_source_shas_and_old_sat_model(self):
        for name in mod.NAMES:
            rows,n,sha=mod.original(name)
            self.assertEqual(len(rows),next(r[4] for r in mod.CASES if r[0]==name))
            self.assertEqual(len(sha),64)
            self.assertGreater(n,0)

    def test_bad_policy_rejected_without_running_CMS(self):
        with self.assertRaises(ValueError):
            mod.select_verified_xor([(1,)],1,"ghost_promoted")

if __name__=="__main__":unittest.main()
