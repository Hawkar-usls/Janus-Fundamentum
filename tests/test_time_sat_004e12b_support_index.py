#!/usr/bin/env python3
"""E12B source-only masks, original SAT model, exact semantics, metamorphic order."""
from __future__ import annotations
from collections import Counter
import itertools
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"/"direct"))
import janus_time_sat_004e12b_support_index as m

def truth(rows,assign):
    return all(any((v>0)==assign[abs(v)] for v in row) for row in rows)
def representation(c,assign):
    return (all(sum(int(assign[v]) for v in eq["variables"])%2==eq["rhs"]
                for eq in c["equations"]) and truth(c["cnf_clauses"],assign))

class SourceCertificates(unittest.TestCase):
    def test_frozen_preregistered_plan_first_20VM_600_children(self):
        p=m.frozen();b=p["original_cross_family_tests"]
        self.assertEqual(len(m.IDS),10)
        self.assertEqual(len(m.ARMS),5)
        self.assertEqual((b["VM_jobs"],b["planned_cold_subprocesses"],b["parallel_limit"]),(20,600,8))
        self.assertEqual((m.MIN_COVER,m.MIN_EQUATIONS,m.WIDTH),(.7,4,5))
        self.assertEqual(b["true_new_independent_external_sources"],0)

    def test_ten_original_source_complete_models_sha_reproducible(self):
        originals={}
        for case in m.IDS:
            a=m.source(case)
            self.assertTrue(m.old.all_model_ok(a["rows"],a["n"],a["model"]))
            self.assertEqual(a["sha"],m.digest(a["bytes"]))
            self.assertEqual(a["sha"],m.source(case)["sha"])
            self.assertEqual(a["model_sha"],m.digest(json.dumps(a["model"]).encode()))
            originals[case]=a["sha"]
        self.assertEqual(len(set(originals.values())),10)

    def test_exact_source_permutations_keep_multiset_model_and_candidate_decision(self):
        for case in m.IDS:
            s=[m.variant(case,v) for v in m.VARIANTS]
            self.assertEqual(len({z["base_sha"] for z in s}),1)
            self.assertEqual(len({z["sha"] for z in s}),3)
            self.assertEqual(len({z["model_sha"] for z in s}),1)
            self.assertTrue(all(m.signature(z["rows"])==m.signature(s[0]["rows"]) for z in s))
            decisions=[m.policy(z["rows"],z["n"],"e12b_support_index")["decision"]["choice"] for z in s]
            self.assertEqual(len(set(decisions)),1,"E12B must be permutation-invariant on "+case)

    def test_two_original_sha_groups_per_family_and_exposed_e12a_excluded(self):
        p=m.frozen()
        families=Counter(row["family"] for row in p["original_source_configs"])
        self.assertEqual(families,Counter({"torus":2,"circulant":2,"diagonal":2,"exactone":2,"mixedxor":2}))
        self.assertTrue(all(case.startswith("e12b-") for case in m.IDS))
        self.assertTrue(set(m.IDS).isdisjoint(m.prior.IDS))

    def test_certified_entailment_truth_table_all_32_assignments(self):
        vs=(1,2,3,4,5)
        clauses=[[v if b==0 else -v for v,b in zip(vs,bits)]
                 for bits in itertools.product((0,1),repeat=5) if sum(bits)%2==1]
        for permutation in (list(clauses),list(reversed(clauses)),clauses[::2]+clauses[1::2]):
            c=m.certified_support_index(permutation,5)
            self.assertEqual(len(c["equations"]),1)
            self.assertEqual(len(c["source_clause_indices"]),16)
            eq=c["equations"][0]
            self.assertEqual(eq["rhs"],0)
            chosen={"equations":c["equations"],"cnf_clauses":[]}
            for bits in itertools.product((False,True),repeat=5):
                assignment={i+1:b for i,b in enumerate(bits)}
                self.assertEqual(truth(permutation,assignment),representation(chosen,assignment))

    def test_incomplete_mask_no_equation_all_original_constraints_retained(self):
        full=[[v if b==0 else -v for v,b in enumerate(bits,1)]
              for bits in itertools.product((0,1),repeat=5) if sum(bits)%2==1]
        short=full[:-1]
        self.assertEqual(m.certified_support_index(short,5)["source_complete_equation_count"],0)
        out=m.policy(short,5,"e12b_support_index")
        self.assertEqual(out["cnf_clauses"],short)
        self.assertEqual(out["decision"]["choice"],"RAW")

    def test_duplicate_complete_source_one_index_allocated_residual_retained(self):
        full=[[v if b==0 else -v for v,b in enumerate(bits,1)]
              for bits in itertools.product((0,1),repeat=5) if sum(bits)%2==1]
        f=full+[list(full[0])]
        idx=m.certified_support_index(f,5)
        self.assertEqual(len(idx["source_clause_indices"]),16)
        self.assertEqual(idx["source_complete_equation_count"],1)
        used=idx["source_clause_indices"]
        self.assertEqual(len([row for i,row in enumerate(f) if i not in used]),1)

    def test_extra_opposite_mask_remains_as_original_residual(self):
        full=[[v if b==0 else -v for v,b in enumerate(bits,1)]
              for bits in itertools.product((0,1),repeat=5) if sum(bits)%2==1]
        full.append([1,2,3,4,5])  # opposite parity: not part of XOR block
        indexed=m.certified_support_index(full,5)
        self.assertEqual(indexed["source_complete_equation_count"],1)
        self.assertNotIn(len(full)-1,indexed["source_clause_indices"])

    def test_width_four_negative_and_width_three_negatives_never_promoted(self):
        for case in m.IDS[4:]:
            self.assertEqual(m.policy(m.source(case)["rows"],m.source(case)["n"],
                       "e12b_support_index")["decision"]["choice"],"RAW",case)

    def test_bounds_fail_closed_without_consuming_unproved_original_clauses(self):
        out=m.policy([[1,2,3,4,5]]* (m.MAX_CLAUSES+1),5,"e12b_support_index")
        self.assertEqual(out["decision"]["choice"],"RAW")
        self.assertEqual(len(out["cnf_clauses"]),m.MAX_CLAUSES+1)
        self.assertEqual(out["equations"],[])

    def test_refuse_posthoc_arm_or_source(self):
        with self.assertRaises(AssertionError):m.source("unknown")
        with self.assertRaises(AssertionError):m.policy([[1]],1,"new_optimal_posthoc",None)

if __name__=="__main__":unittest.main()
