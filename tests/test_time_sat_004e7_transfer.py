#!/usr/bin/env python3
"""004E7: fail-closed source SHA, exact SAT equivalence and frozen no-promotion."""
from __future__ import annotations
import itertools
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"/"direct"))
import janus_time_sat_004e7_transfer as m
from janus_time_sat_004e6_semantic_selector import semantic_core,normalized_selector

def holds(rows,bits):
    return all(any(((lit>0) == bits[abs(lit)]) for lit in row) for row in rows)

def transformed(form,bits):
    return (all((sum(int(bits[v]) for v in eq["variables"]) & 1)==eq["rhs"]
                for eq in form["equations"])
            and holds(form["cnf_clauses"],bits))

class TransferSafety(unittest.TestCase):
    def test_freeze_exact_source_and_five_arm_twenty_vm_grid(self):
        p=m.frozen()
        self.assertEqual((len(m.FAMILIES),len(m.STATES),len(m.ARMS),len(m.HOSTS)),(5,2,5,2))
        self.assertEqual(p["design"]["cold_child_count"],200)
        self.assertEqual(p["design"]["max_parallel"],20)
        self.assertEqual(p["new_external_blinded_sources"],0)
        self.assertEqual((m.CPU,m.WALL,m.REPS),(6,10,2))

    def test_deterministic_rewrite_and_exact_semantic_equivalence_all_truth_tables(self):
        rows=[[1,2],[-1,3],[-2,-3],[-1,2,3]]
        for family in m.FAMILIES:
            for state in m.STATES:
                a=m.transform(rows,3,family,state)
                b=m.transform(rows,3,family,state)
                self.assertEqual(a["bytes"],b["bytes"])
                self.assertEqual(a["CNF_SHA256"],b["CNF_SHA256"])
                self.assertEqual(a["generated_clauses"],len(a["rows"]))
                for sample in itertools.product([False,True],repeat=3):
                    bits={i+1:sample[i] for i in range(3)}
                    self.assertEqual(holds(rows,bits),holds(a["rows"],bits),
                        msg=(family,state,sample))

    def test_normalization_and_native_equivalent_on_rewritten_small_CNF(self):
        rows=[[1,2],[-1,2],[1,-2],[-1,-2],[3,4],[-4,3]]
        for state in m.STATES:
            transformed_src=m.transform(rows,4,"or_randxor",state)
            for arm in m.ARMS[:4]:
                chosen=normalized_selector(transformed_src["rows"],4,arm)
                for t in itertools.product((False,True),repeat=4):
                    bits={i+1:v for i,v in enumerate(t)}
                    self.assertEqual(holds(rows,bits),transformed(chosen,bits),
                                     msg=(state,arm,t))

    def test_semantic_core_proof_ignores_only_taut_and_duplicate_clauses(self):
        rows=[[1,1,2],[2,1],[-3,3],[4],[-4,2]]
        core,stats=semantic_core(rows,4)
        self.assertEqual(stats["repeated_literals_in_clause"],1)
        self.assertEqual(stats["tautology_clauses"],1)
        self.assertEqual(stats["duplicate_clauses"],1)
        self.assertEqual(len(core),3)
        for sample in itertools.product([False,True],repeat=4):
            bits={i+1:sample[i] for i in range(4)}
            self.assertEqual(holds(rows,bits),holds(core,bits))

    def test_five_archived_originals_unmodified_source_SHA_and_clause_count(self):
        for family in m.FAMILIES:
            rows,n,sha=m.source(family)
            self.assertEqual((sha,n,len(rows)),m.CASES[family])

    def test_all_unknown_case_names_and_arm_rejected(self):
        with self.assertRaises(AssertionError):
            m.transform([[1]],1,"ghost-family","unaltered")
        with self.assertRaises(AssertionError):
            m.transform([[1]],1,m.FAMILIES[0],"posthoc_state")
        with self.assertRaises(AssertionError):
            normalized_selector([[1]],1,"posthoc_arm")

if __name__=="__main__":unittest.main()
