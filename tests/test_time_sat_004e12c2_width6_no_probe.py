#!/usr/bin/env python3
"""E12C2 finite source soundness and order invariance before original workers."""
from __future__ import annotations
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory
import sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"/"direct"))
import janus_time_sat_004e12c2_width6_no_probe as e

class E12C2NoRawProbe(unittest.TestCase):
    def test_preregistered_model_cohort_and_limits(self):
        p=e.frozen()
        self.assertEqual((len(e.IDS),len(e.ARMS),len(e.VARIANTS)),(8,6,3))
        self.assertEqual((p["resources"]["VMs"],p["resources"]["total_cold_children"]),(16,576))
        self.assertFalse(p["candidate"]["raw_first_035_second_subprocess"])
        self.assertEqual(p["external_independent_custodian_count"],0)

    def test_all_eight_base_sources_and_equivalence(self):
        signatures=set()
        for case in e.IDS:
            base=e.original(case)
            self.assertTrue(e.b.old.all_model_ok(base["rows"],base["n"],base["model"]))
            self.assertNotIn(base["sha"],signatures)
            signatures.add(base["sha"])
            signature=e.signature(base["rows"])
            for v in e.VARIANTS:
                trial=e.variant(case,v)
                self.assertEqual(signature,e.signature(trial["rows"]))
                self.assertTrue(e.b.old.all_model_ok(trial["rows"],trial["n"],trial["model"]))
                self.assertEqual(trial["model_sha"],base["model_sha"])

    def test_candidate_original_width6_positive_and_negative_controls(self):
        for case in e.IDS:
            src=e.original(case)
            choices=set()
            for v in e.VARIANTS:
                s=e.variant(case,v)
                d=e.policy(s["rows"],s["n"],"e12c2_certified_width5_6_no_probe")
                choices.add(d["decision"]["choice"])
                self.assertEqual(d["decision"]["probe_second_process_s"],0.0)
                self.assertEqual(len(d["cnf_clauses"])+sum(2**(len(x["variables"])-1) for x in d["equations"]),len(s["rows"]))
                if case.startswith("e12c2-ring6") or case.startswith("e12c2-hyper6"):
                    self.assertEqual(d["decision"]["choice"],"XOR")
                    self.assertTrue(all(len(x["variables"])==6 for x in d["equations"]))
            self.assertEqual(len(choices),1)
        for name in ("e12c2-diagonal4-g12","e12c2-exactone-t25","e12c2-mixed3-n130"):
            source=e.original(name)
            self.assertEqual(e.policy(source["rows"],source["n"],"e12c2_certified_width5_6_no_probe")["decision"]["choice"],"RAW")

    def test_old_C1_rejects_width6_preserving_negative_control(self):
        s=e.original("e12c2-hyper6-n110")
        old=e.policy(s["rows"],s["n"],"e12c1_frozen_raw_pilot")
        new=e.policy(s["rows"],s["n"],"e12c2_certified_width5_6_no_probe")
        self.assertFalse(old["decision"]["eligible"])
        self.assertEqual(new["decision"]["choice"],"XOR")
        self.assertGreater(len(new["equations"]),0)

    def test_preflight_source SHA_lock(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp);a=e.preflight(root)
            b,dig=e.checked_lock(root/"SOURCE_LOCK.json")
            self.assertEqual(a,b);self.assertEqual(len(b["origins"]),8)
            (root/"SOURCE_LOCK.sha256").write_text("0"*64+"  SOURCE_LOCK.json\n")
            with self.assertRaises(AssertionError):e.checked_lock(root/"SOURCE_LOCK.json")

    def test_unregistered_and_invalid_source_fail_closed(self):
        self.assertNotIn("UNSAT",e.ALLOWED)
        with self.assertRaises(AssertionError):e.original("foreign")
        with self.assertRaises(AssertionError):e.policy([[1]],1,"self_tuned")

if __name__=="__main__":unittest.main()
