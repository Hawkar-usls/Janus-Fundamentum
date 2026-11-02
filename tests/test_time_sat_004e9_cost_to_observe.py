#!/usr/bin/env python3
"""004E9: no train/test outcome leakage, model SHA, exact SAT source and gate."""
from __future__ import annotations
from hashlib import sha256
import itertools
import json
import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"/"direct"))
import janus_time_sat_004e9_cost_to_observe as m
from janus_time_sat_004d4b_real_pilot import original_model_replay

def sat(rows,assign):
    return all(any((x>0)==assign[abs(x)] for x in row) for row in rows)

class CostToObserveSafety(unittest.TestCase):
    def test_frozen_science_16_vm_160_children(self):
        p=m.frozen()
        self.assertEqual(len(m.TRAIN),8)
        self.assertEqual(len(m.NEW),6)
        self.assertEqual(len(m.IDS),8)
        self.assertEqual((m.REPS,m.CPU,m.WALL,m.MEM),(2,12,16,2147483648))
        self.assertEqual(p["validation_budget"]["cold_children"],160)
        self.assertEqual(p["validation_budget"]["maximum_simultaneous_jobs"],8)
        self.assertEqual(p["gate_004C_external"],"OPEN")

    def test_training_and_validation_disjoint_source_ids_except_public_regressions(self):
        self.assertTrue(set(m.NEW).isdisjoint(m.TRAIN))
        self.assertEqual(set(m.IDS).intersection(m.TRAIN),set(m.PUBLIC))
        p=m.frozen()
        for row in p["validation_sources"]:
            if row["id"] in m.NEW:
                self.assertEqual(row["kind"],"NEW_SEED_SAME_INTERNAL_GENERATOR")

    def test_full_synthetic_original_SAT_models_and_determinism(self):
        for case in m.NEW:
            a=m.validation_source(case)
            b=m.validation_source(case)
            self.assertEqual(a["sha"],b["sha"])
            self.assertEqual(a["model_sha"],b["model_sha"])
            self.assertTrue(original_model_replay(a["rows"],a["n"],a["model"]))
            self.assertEqual(sha256(a["bytes"]).hexdigest(),a["sha"])
        shas={m.validation_source(x)["sha"] for x in m.NEW}
        self.assertEqual(len(shas),6)

    def test_old_archived_training_groups_and_no_foreign_label(self):
        train,a=m.observed_training_model()
        self.assertEqual(len(train),8)
        self.assertEqual(a["original_children"],160)
        self.assertEqual({x["original_source_group"] for x in train},set(m.TRAIN))
        self.assertTrue(all(x["label"] in ("RAW","XOR") for x in train))
        self.assertEqual(len({x["training_source_SHA256"] for x in train}),8)

    def test_cost_gate_skip_scan_without_any_xor(self):
        cnf=[[1,2],[-1,2],[1,-2],[-1,-2]]
        f=m.fingerprint(cnf,2)
        synthetic={"training_entries":[{
          "original_source_group":"fake-only-for-test",
          "fingerprint":f,
          "label":"RAW",
          "original_FULL_COLD_native_verified_SAT":4}]}
        chosen=m.policy(cnf,2,"cost_nearest",synthetic)
        self.assertEqual(chosen["choice"],"raw_without_expensive_scan")
        self.assertEqual(chosen["cnf_clauses"],cnf)
        self.assertEqual(chosen["equations"],[])
        self.assertFalse(chosen["cost_prediction"]["expensive_XOR_scan_performed"])

    def test_cost_gate_positive_does_only_source_verified_full_equivalent_xor(self):
        cnf=[[1,2],[-1,2],[1,-2],[-1,-2]]
        f=m.fingerprint(cnf,2)
        synthetic={"training_entries":[{
          "original_source_group":"fake-only-for-test",
          "fingerprint":f,
          "label":"XOR",
          "original_FULL_COLD_native_verified_SAT":4}]}
        chosen=m.policy(cnf,2,"cost_nearest",synthetic)
        self.assertTrue(chosen["cost_prediction"]["expensive_XOR_scan_performed"])
        self.assertEqual(len(chosen["equations"]),0) # all four sign masks are contradictory, extractor must abstain
        self.assertEqual(chosen["cnf_clauses"],cnf)

    def test_xor_equivalence_with_constrained_complete_parity(self):
        cnf=[[1,2],[-1,-2],[3]]
        f=m.fingerprint(cnf,3)
        model={"training_entries":[{
          "original_source_group":"training",
          "fingerprint":f,
          "label":"XOR",
          "original_FULL_COLD_native_verified_SAT":4}]}
        candidate=m.policy(cnf,3,"cost_nearest",model)
        self.assertGreater(len(candidate["equations"]),0)
        for vals in itertools.product((False,True),repeat=3):
            bits={i+1:v for i,v in enumerate(vals)}
            raw=sat(cnf,bits)
            derived=(all(sum(int(bits[i]) for i in eq["variables"])%2==eq["rhs"]
                         for eq in candidate["equations"])
                     and sat(candidate["cnf_clauses"],bits))
            self.assertEqual(raw,derived)

    def test_unknown_source_or_unsanctioned_arm_aborts(self):
        with self.assertRaises(AssertionError):m.validation_source("not-a-registered-CNF")
        with self.assertRaises(AssertionError):m.policy([[1]],1,"posthoc_custom",{})

if __name__=="__main__":unittest.main()
