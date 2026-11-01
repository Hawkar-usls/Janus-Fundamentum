#!/usr/bin/env python3
"""004D7: truly independent GF2 consequence, redundant, tamper and guards."""
from __future__ import annotations
import itertools
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"/"direct"))
from janus_time_sat_004d7_rank_gate import (
    vector,add_to_basis,independence_record,source_rank_experiment
)
from janus_time_sat_004d6_replay import replay_all

def synthetic_masked(variables,rhs,auxiliary):
    rows=[]
    for bits in itertools.product((0,1),repeat=len(variables)):
        if sum(bits)%2==rhs:continue
        terms=tuple(-v if b else v for v,b in zip(variables,bits))
        rows.extend([terms+(auxiliary,),terms+(-auxiliary,)])
    return rows

def all_models(rows,n):
    for assignment in itertools.product((False,True),repeat=n):
        if all(any(assignment[abs(l)-1]==(l>0) for l in row) for row in rows):
            yield assignment

class ExactRankNovelty(unittest.TestCase):
    def test_rank_gate_finds_independent_hidden_ternary_xor(self):
        rows=synthetic_masked([1,2,3],1,4)
        e=source_rank_experiment(rows,4)
        self.assertEqual(e["status"],"SOURCE_PROOF_REPLAY_AND_EXACT_GF2_RANK_PASS")
        self.assertTrue(replay_all(rows,4,e["resolution_evidence"]))
        self.assertEqual(e["original_complete_mask_XOR_count"],0)
        self.assertGreater(e["source_derived_new_syntactic_XOR_count"],0)
        self.assertGreater(e["independent_rank_analysis"]["independent_new_augmented_rank"],0)
        self.assertGreater(e["independent_rank_analysis"]["independent_new_coefficient_rank"],0)
        for witness in e["independent_rank_analysis"]["new_augmented_rank_witnesses"]:
            for model in all_models(rows,4):
                parity=sum(int(model[v-1]) for v in witness["variables"])%2
                self.assertEqual(parity,witness["rhs"])

    def test_preexisting_explicit_parity_rank_does_not_increase(self):
        rows=[(1,2),(-1,-2)]
        e=source_rank_experiment(rows,2)
        self.assertEqual(e["status"],"SOURCE_PROOF_REPLAY_AND_EXACT_GF2_RANK_PASS")
        self.assertEqual(e["independent_rank_analysis"]["independent_new_augmented_rank"],0)
        self.assertEqual(e["original_complete_mask_XOR_count"],1)

    def test_augmented_rank_distinguishes_rhs_conflict_without_unsat_claim(self):
        known={((1,),0)}
        new={((1,),1)}
        a=independence_record(known,new,2)
        self.assertEqual(a["independent_new_coefficient_rank"],0)
        self.assertEqual(a["independent_new_augmented_rank"],1)
        self.assertTrue(a["source_plus_derived_GF2_inconsistent"])
        self.assertEqual(a["UNSAT_portable_proof"],"NOT_PRODUCED")

    def test_redundant_variable_equations_do_not_increase_rank(self):
        known={((1,2),0),((2,3),1)}
        novel={((1,3),1),((1,2),0)}
        a=independence_record(known,novel,3)
        self.assertEqual(a["independent_new_coefficient_rank"],0)
        self.assertEqual(a["independent_new_augmented_rank"],0)

    def test_input_validation(self):
        for variables,rhs,n in [([1,4],0,3),([1],2,3),([True],0,1)]:
            with self.assertRaises(ValueError):
                vector(variables,rhs,n)
        self.assertEqual(independence_record(set(),set(),3)
                         ["independent_new_augmented_rank"],0)

    def test_binary_resolution_trivial_or_empty_not_success(self):
        e=source_rank_experiment([(1,2),(2,3)],3)
        self.assertEqual(e["source_derived_new_syntactic_XOR_count"],0)
        self.assertEqual(e["independent_rank_analysis"]["independent_new_coefficient_rank"],0)

    def test_malformed_or_excessive_source_abstains(self):
        for src,n in [([(0,)],1),([(True,)],1),([(3,)],2),
                      ([(1,)]*30001,2)]:
            e=source_rank_experiment(src,n)
            self.assertTrue(e["status"].startswith("ABSTAIN"))

if __name__=="__main__":unittest.main()
