#!/usr/bin/env python3
"""004E12A preregistered SOURCE-equivalence and unmodified E11 falsification."""
from __future__ import annotations
from collections import Counter
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"/"direct"))
import janus_time_sat_004e12a_clause_order as m

class ClauseOrderAttack(unittest.TestCase):
    def test_frozen_budget_source_list_and_unmodified_probe(self):
        p=m.frozen()
        self.assertEqual(len(p["cases"]),8)
        self.assertEqual(len(m.VARIANTS),3)
        self.assertEqual(len(m.ARMS),3)
        self.assertEqual(p["benchmark"]["cold_children"],288)
        self.assertEqual(p["benchmark"]["max_parallel"],8)
        self.assertEqual((m.e.PREFIX,m.e.MIN_EQ,m.e.MIN_FRAC),(192,4,.70))
        self.assertFalse(p["benchmark"]["no_paid_Rowan"] is False)

    def test_same_source_exact_cnf_multiset_all_24(self):
        for case in m.IDS:
            original=m.e.source(case)
            sig=m.signature(original["rows"])
            for variant in m.VARIANTS:
                a=m.transformed(case,variant)
                b=m.transformed(case,variant)
                self.assertEqual(sig,m.signature(a["rows"]))
                self.assertEqual((a["n"],a["m"],a["model_sha"]),
                                 (original["n"],original["m"],original["model_sha"]))
                self.assertEqual(a["sha"],sha256(a["bytes"]).hexdigest())
                self.assertEqual(a["sha"],b["sha"])
                self.assertTrue(m.e.all_model_ok(a["rows"],a["n"],a["model"]))
                if variant=="as_emitted":self.assertEqual(a["sha"],original["sha"])

    def test_negative_original_models_and_bounds(self):
        for case in m.IDS[-2:]:
            for variant in m.VARIANTS:
                a=m.transformed(case,variant)
                self.assertTrue(m.e.all_model_ok(a["rows"],a["n"],a["model"]))
        self.assertNotIn("UNSAT",m.ALLOWED)
        with self.assertRaises(AssertionError):
            m.transformed("arbitrary","as_emitted")

    def test_presolve_source_lock_cannot_be_replaced(self):
        with TemporaryDirectory() as d:
            p=Path(d)
            lock=m.presolve_lock(p)
            got,digest=m.checked_lock(p/"SOURCE_LOCK.json")
            self.assertEqual(lock,got)
            self.assertEqual(len(got["sources_and_variant_decisions_preworker"]),8)
            self.assertEqual(sum(len(x) for x in got["sources_and_variant_decisions_preworker"].values()),24)
            (p/"SOURCE_LOCK.sha256").write_text("0"*64+"  SOURCE_LOCK.json\n")
            with self.assertRaises(AssertionError):
                m.checked_lock(p/"SOURCE_LOCK.json")

if __name__=="__main__":unittest.main()
