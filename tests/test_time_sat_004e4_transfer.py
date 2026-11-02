#!/usr/bin/env python3
"""004E4 fixed independent-host/cross-cohort public source and adversarial controls."""
from __future__ import annotations
import itertools
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"/"direct"))
import janus_time_sat_004e4_transfer as m

def sat(rows,bits):
    return all(any(bits[abs(v)]==(v>0) for v in c) for c in rows)
def mixed(form,bits):
    return (all(sum(bits[v] for v in eq["variables"])%2==eq["rhs"] for eq in form["equations"])
            and sat(form["cnf_clauses"],bits))

def masks(support,rhs):
    return [tuple((-v if v in dict(zip(support,bit)) and dict(zip(support,bit))[v] else v) for v in support)
            for bit in itertools.product((0,1),repeat=len(support)) if sum(bit)%2!=rhs]

class OriginalTransfer(unittest.TestCase):
    def test_manifest_frozen_and_exact_24_matrix_combinations(self):
        p=m.frozen()
        self.assertEqual(len(p["cases"])*len(m.VARIANTS)*len(p["design"]["hosts"]),24)
        self.assertEqual((m.CPU,m.WALL,m.MEM,m.REPS),(6,10,2147483648,2))
        self.assertEqual(p["design"]["max_parallel"],20)
        self.assertTrue(p["disclosure"].startswith("Each source is PREVIOUSLY SEEN"))

    def test_original_archive_zip_and_four_SHA_on_exact_original(self):
        for family,(id,n,clauses,literals,digest) in m.CASES.items():
            rows,n2,sha=m.archived_cnf(family)
            self.assertEqual((n2,len(rows),sha),(n,clauses,digest))
            self.assertEqual(sum(map(len,rows)),literals)

    def test_all_three_variants_preserve_entire_truth_table(self):
        rows=masks((1,2),1)+masks((2,3,4),0)+[(1,-4)]
        for variant in m.VARIANTS+("raw_cms",):
            form=m.select_verified_xor(rows,4,variant)
            self.assertEqual(form["converted_source_clauses"]+len(form["cnf_clauses"]),len(rows))
            for b in itertools.product((False,True),repeat=4):
                bits={i:b[i-1] for i in range(1,5)}
                self.assertEqual(sat(rows,bits),mixed(form,bits),msg=variant)

    def test_unknown_variant_rejected(self):
        with self.assertRaises(ValueError):m.select_verified_xor([(1,)],1,"new_best_no_proof")

    def test_not_hidden_and_no_self_promotion(self):
        p=m.frozen()
        self.assertFalse(p["autonomous_production_promotion"])
        self.assertEqual(p["C023_main"],"UNCHANGED")
        self.assertEqual(p["external_004C_witness"],"OPEN")
        self.assertEqual(p["external_004D9B_response"],"AWAITING_EXTERNAL_RESPONSE")

    def test_exact_zero_source_model_shortcuts(self):
        self.assertEqual(set(m.VARIANTS),{"native_all","native_width3plus_only","adaptive_80"})
        self.assertEqual(len(m.ALLOWED),5)
        self.assertNotIn("SAT_UNVERIFIED",m.ALLOWED)

if __name__=="__main__":unittest.main()
