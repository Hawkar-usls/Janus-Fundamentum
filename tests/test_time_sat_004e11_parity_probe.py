#!/usr/bin/env python3
"""TIME-SAT-004E11: source proof, frozen new-source SHA, OOD controls & fail-closed."""
from __future__ import annotations
import itertools
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"/"direct"))
import janus_time_sat_004e11_parity_probe as m
from janus_time_sat_004d4b_real_pilot import original_model_replay

class Probe(unittest.TestCase):
    def test_frozen_16_vm_224_children_and_one_sided_parity_policy(self):
        p=m.frozen();b=p["benchmark"]
        self.assertEqual((len(m.IDS),len(m.NEW),len(m.ARMS)),(8,6,7))
        self.assertEqual((b["original_VM_jobs"],b["cold_subprocesses"]), (16,224))
        self.assertEqual((m.PREFIX,m.MIN_EQ,m.MIN_FRAC),(192,4,0.70))
        self.assertEqual(p["generator"]["independent_external_sources"],0)

    def test_all_six_internal_source_models_and_deterministic_exact_source_SHA(self):
        shas=set()
        for case in m.NEW:
            a=m.new_source(case)
            b=m.new_source(case)
            self.assertEqual((a["sha"],a["model_sha"]),(b["sha"],b["model_sha"]))
            self.assertEqual(a["m"],len(a["rows"]))
            self.assertTrue(original_model_replay(a["rows"],a["n"],a["model"]))
            self.assertEqual(a["source_block_complete"],True)
            shas.add(a["sha"])
        self.assertEqual(len(shas),6)

    def test_new_generator_families_are_distinct_source_SHA(self):
        families={m.new_source(case)["family"] for case in m.NEW}
        self.assertEqual(len(families),3)

    def test_old_two_negative_control_sources_original_model_known(self):
        for case in m.IDS[6:]:
            a=m.source(case)
            self.assertTrue(original_model_replay(a["rows"],a["n"],a["model"]))
            self.assertNotIn(case,m.NEW)

    def test_prefix_positive_proof_source_to_exact_native(self):
        a=m.new_source(m.NEW[0])
        out=m.policy(a["rows"],a["n"],"e11_prefix_certified",None)
        self.assertEqual(out["source_only_decision"]["decision"],"E11_PREFIX_SOURCE_CERTIFIED_NATIVE")
        self.assertGreaterEqual(out["source_only_decision"]["complete_prefix_source_XOR"],4)
        self.assertTrue(out["source_only_decision"]["full_scan_performed"])
        self.assertEqual(len(out["cnf_clauses"]),0)
        self.assertEqual(len(out["equations"]),a["n"])

    def test_negative_evidence_small_formula_abstains_without_full_scan(self):
        rows=[[1,2,3],[1,2,4],[-1,3,4],[2,3,-4],[1,-2,4]]
        out=m.policy(rows,4,"e11_prefix_certified",None)
        self.assertEqual(out["source_only_decision"]["decision"],"E11_PREFIX_ABSTAIN_RAW")
        self.assertEqual(out["cnf_clauses"],rows)
        self.assertEqual(out["equations"],[])
        self.assertFalse(out["source_only_decision"]["full_scan_performed"])

    def test_small_complete_source_parity_proof_preserves_all_truth_assignments(self):
        rows=[]
        for s in itertools.product((0,1),repeat=4):
            if sum(s)%2==0:continue
            rows.append([i+1 if not bit else -(i+1) for i,bit in enumerate(s)])
        transformed=m.policy(rows,4,"native_all",m.frozen_e9_model())
        for vals in itertools.product((0,1),repeat=4):
            a={i+1:bool(v) for i,v in enumerate(vals)}
            ori=all(any((lit>0)==a[abs(lit)] for lit in c) for c in rows)
            new=all(sum(a[v] for v in eq["variables"])%2==eq["rhs"]
                    for eq in transformed["equations"]) and all(
                        any((lit>0)==a[abs(lit)] for lit in c)
                        for c in transformed["cnf_clauses"])
            self.assertEqual(ori,new)

    def test_reject_unknown_case_or_arm(self):
        with self.assertRaises(AssertionError):m.source("not-source")
        with self.assertRaises(AssertionError):m.policy([[1]],1,"posthoc",{})

if __name__=="__main__":unittest.main()
