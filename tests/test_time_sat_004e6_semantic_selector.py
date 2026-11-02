#!/usr/bin/env python3
"""004E6: adversarial semantics + all precommitted real-source model gates."""
from __future__ import annotations
from itertools import product
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"/"direct"))
import janus_time_sat_004e6_semantic_selector as m
from janus_time_sat_004d4b_real_pilot import original_model_replay

def equivalent_sat(rows,n,bits):
    return all(any(bits[abs(x)]==(x>0) for x in row) for row in rows)

def mixed(form,bits):
    return (all(sum(int(bits[v]) for v in eq["variables"])%2==eq["rhs"] for eq in form["equations"])
            and equivalent_sat(form["cnf_clauses"],max(bits),bits))

class SemanticRepair(unittest.TestCase):
    def test_frozen_precommit_and_all_caps(self):
        p=m.preregistered()
        self.assertEqual((len(m.FAMILIES),len(m.STATES),len(m.HOSTS),len(m.ARMS)),(2,3,2,4))
        self.assertEqual((m.CPU,m.WALL,m.REPS,m.MEM),(6,10,2,2147483648))
        self.assertEqual(p["comparison"]["total_children"],96)
        self.assertFalse(p["hard_gates"]["no_external_hidden_claim"] is False)

    def test_tautology_and_clause_duplicate_invariance_exact(self):
        original=[[1,2],[-1,2],[1,-2],[-1,-2],[3]]
        padded=original+[[2,-2],[-1,1,3],[-3,3,3]]+[[2,1],[1,2,2],[-2,1,1],[3]]
        base,base_s=m.semantic_core(original,3)
        core,stats=m.semantic_core(padded,3)
        self.assertEqual(base,core)
        self.assertEqual(stats["tautology_clauses"],3)
        self.assertEqual(stats["duplicate_clauses"],4)
        self.assertGreater(stats["repeated_literals_in_clause"],0)

    def test_reject_invalid_literals_and_keep_empty_cnf_contradiction(self):
        for rows in ([[[0]]],[[[4]]],[[["1"]]],[[[True]]]):
            with self.assertRaises(AssertionError):
                m.semantic_core(rows,3)
        self.assertEqual(m.semantic_core([[],[],[1],[-1]],3)[0],[[],[1],[-1]])

    def test_small_truth_table_normalization_preserves_satisfiability(self):
        examples=[
            [[1,1,2],[-2,1],[-1,-2],[1,-1,3],[3,3]],
            [[1,-1],[2,-2],[]],
            [[1,2],[-1,2],[-2,1]]
        ]
        for rows in examples:
            core,_=m.semantic_core(rows,3)
            for bs in product((False,True),repeat=3):
                bits={i:bs[i-1] for i in range(1,4)}
                self.assertEqual(equivalent_sat(rows,3,bits),equivalent_sat(core,3,bits))

    def test_real_model_permuted_new_seed_with_taut_and_exact_duplicates(self):
        for family in m.FAMILIES:
            for state in m.STATES:
                j=m.materialize(family,state)
                self.assertEqual(j["source_SHA256"],m.SHA[family])
                self.assertTrue(original_model_replay(j["rows"],j["n"],j["model"]))
                self.assertEqual(j["SHA256"],m.sha256(j["data"]).hexdigest())
                self.assertEqual(len(j["rows"]),j["old_source_clauses"]+j["added_tautologies"]+j["added_duplicates"])

    def test_new_semantic_choice_stable_against_tautology_padding_and_duplicates(self):
        for family in m.FAMILIES:
            choices=[]
            for state in m.STATES:
                j=m.materialize(family,state)
                x=m.normalized_selector(j["rows"],j["n"],"new_semantic80")
                self.assertEqual(x["choice"],"native_xor",msg=(family,state,x["metric"]))
                self.assertGreater(x["metric"]["fraction"],0.8)
                self.assertEqual(x["metric"]["selected"],625 if family=="lights-out" else 857)
                choices.append(x["metric"]["selected"])
            self.assertEqual(len(set(choices)),1)

    def test_old_known_failure_not_falsely_declared_fixed(self):
        for family,state in (("binary-tree-parity","taut5_duplicate5"),("binary-tree-parity","taut30_duplicate20"),("lights-out","taut30_duplicate20")):
            j=m.materialize(family,state)
            old=m.normalized_selector(j["rows"],j["n"],"old_adaptive80")
            new=m.normalized_selector(j["rows"],j["n"],"new_semantic80")
            self.assertEqual(new["choice"],"native_xor")
            self.assertEqual(old["choice"],"raw_after_scan",msg=(family,state,old["metric"]))

    def test_semantic_native_xor_truth_table_and_raw_fallback(self):
        # Original four-bit CNF, complete exact parity mask and leftover constraint.
        rows=[[1,2],[-1,-2],[3,-3],[2,3,4],[2,3,4]]
        base=m.normalized_selector(rows,4,"new_semantic80")
        self.assertEqual(base["choice"],"raw_original_after_core_scan")
        self.assertEqual(base["cnf_clauses"],rows)
        clean=m.semantic_core(rows,4)[0]
        for bs in product((False,True),repeat=4):
            vals={i:bs[i-1] for i in range(1,5)}
            self.assertEqual(equivalent_sat(rows,4,vals),equivalent_sat(clean,4,vals))
        self.assertEqual(m.normalized_selector(rows,4,"raw_cms")["choice"],"raw_original")

if __name__=="__main__":
    unittest.main()
