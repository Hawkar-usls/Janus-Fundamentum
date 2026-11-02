#!/usr/bin/env python3
"""E10: new-source family group split, no training leakage, prefix-only OOD gate."""
from __future__ import annotations
from hashlib import sha256
import itertools
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"/"direct"))
import janus_time_sat_004e10_ood as e

class E10FamilySplitSafety(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m=e.model()

    def test_frozen_precommit_and_unchanged_model(self):
        p=e.frozen()
        self.assertEqual(e.MODEL_SHA,"12280a2df2cceea69fd1890603d1795994939b84636d7da9efc231a6a7298397")
        self.assertEqual(len(p["new_source_generator_families"]),6)
        self.assertEqual((p["budgets"]["original_workers"],p["budgets"]["total_children"]),(12,144))
        self.assertEqual(p["budgets"]["max_parallel"],6)
        self.assertEqual(len(self.m["training_entries"]),8)
        self.assertEqual(sum(x["label"]=="XOR" for x in self.m["training_entries"]),2)

    def test_all_six_new_family_sources_are_deterministic_and_true_sat(self):
        alltraining={x["training_source_SHA256"] for x in self.m["training_entries"]}
        shas=set();fams=set()
        for case in e.IDS:
            x=e.planted_source(case)
            y=e.planted_source(case)
            self.assertEqual(x["sha"],sha256(x["bytes"]).hexdigest())
            self.assertEqual(x["sha"],y["sha"])
            self.assertEqual(x["model_sha"],y["model_sha"])
            self.assertTrue(e.all_model_ok(x["rows"],x["n"],x["model"]))
            self.assertNotIn(x["sha"],alltraining)
            self.assertEqual(len(x["rows"]),x["m"])
            shas.add(x["sha"]);fams.add(x["family"])
        self.assertEqual(len(shas),6)
        self.assertEqual(fams,set(e.FAMILIES))

    def test_new_exact_one_clause_semantics(self):
        x=e.planted_source("e10-exactone-t28")
        self.assertTrue(any(len(c)==5 for c in x["rows"]))
        self.assertTrue(any(len(c)==2 for c in x["rows"]))
        self.assertEqual(x["n"],140)

    def test_graph_3color_source_complete(self):
        x=e.planted_source("e10-graph3color-v36")
        self.assertEqual((x["n"],x["m"]),(108,468))
        self.assertTrue(all(len(c) in (2,3) for c in x["rows"]))
        self.assertTrue(e.all_model_ok(x["rows"],x["n"],x["model"]))

    def test_guarded_parity_width4_mask_truth_table_sample(self):
        x=e.planted_source("e10-guarded-parity-n80")
        self.assertEqual(x["m"],480)
        self.assertEqual(sum(len(c)==4 for c in x["rows"]),320)
        self.assertEqual(sum(len(c)==3 for c in x["rows"]),160)
        # Extracted native XOR remains exact-source equivalent.
        chosen=e.decision(x["rows"],x["n"],"native_all",self.m)
        self.assertGreater(len(chosen["equations"]),0)
        bits={abs(x):x>0 for x in x["model"]}
        for eq in chosen["equations"]:
            self.assertEqual(sum(bits[v] for v in eq["variables"])%2,eq["rhs"])

    def test_ood_vs_E9_uses_only_original_fixed_model(self):
        for case in e.IDS:
            x=e.planted_source(case)
            current=e.decision(x["rows"],x["n"],"e10_ood_abstain",self.m)
            old=e.decision(x["rows"],x["n"],"e9_cost_nearest",self.m)
            self.assertIn(current["cost_prediction"]["choose"],(
                "E10_ADMIT_SOURCE_EQUIVALENT_XOR","E10_OOD_ABSTAIN_RAW"))
            self.assertIn(old["cost_prediction"]["choose"],(
                "SKIP_SCAN_RAW","NATIVE_SOURCE_XOR","RAW_SAFE_FALLBACK"))
            if current["choice"]=="ood_abstain_raw_without_scan":
                self.assertEqual(current["equations"],[])
                self.assertEqual(current["cnf_clauses"],x["rows"])
                self.assertFalse(current["cost_prediction"]["expensive_scan"])

    def test_full_preworker_source_lock_SHA(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp);l=e.prepare(root)
            obj,digest=e.checked_lock(root/"SOURCE_LOCK.json")
            self.assertEqual(l,obj)
            self.assertEqual(len(obj["source_precommit"]),6)
            self.assertEqual(obj["original_distinct_generator_families"],3)
            (root/"SOURCE_LOCK.sha256").write_text("0"*64+"  SOURCE_LOCK.json\n")
            with self.assertRaises(AssertionError):e.checked_lock(root/"SOURCE_LOCK.json")

    def test_bad_arm_or_unknown_family_fails_closed(self):
        with self.assertRaises(AssertionError):e.planted_source("unregistered")
        with self.assertRaises(AssertionError):e.decision([[1]],1,"self_tuned",self.m)
        self.assertNotIn("UNSAT",e.ALLOWED)

if __name__=="__main__":unittest.main()
