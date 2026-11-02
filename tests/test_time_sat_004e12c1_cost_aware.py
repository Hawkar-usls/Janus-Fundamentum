#!/usr/bin/env python3
"""C1 exhaustive source masks, new SAT originals, order and cold cost contracts."""
import itertools,json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"/"direct"))
import janus_time_sat_004e12c1_cost_aware as m

class CostAndSoundness(unittest.TestCase):
 def test_freeze_e12c0_and_new_workload_no_independence_claim(self):
    p=m.frozen()
    self.assertEqual(len(p["new_original_source_configs"]),10)
    self.assertEqual(p["limits"]["planned_cold_children"],720)
    self.assertEqual(p["science_gates"]["external_independent_custodians"],0)
    self.assertEqual(p["calibration"]["raw_probe_wall_budget_s"],0.35)
 def test_ten_origins_all_have_full_proven_planted_SAT_and_sha(self):
    shas=set()
    for case in m.IDS:
        z=m.source(case)
        self.assertTrue(m.b.old.all_model_ok(z["rows"],z["n"],z["model"]),case)
        self.assertEqual(z["model_sha"],m.sha(json.dumps(z["model"]).encode()))
        self.assertEqual(z["sha"],m.sha(z["bytes"]))
        self.assertNotIn(z["sha"],shas)
        shas.add(z["sha"])
 def test_representations_and_invariant_eligibility(self):
    for case in m.IDS:
        z=[m.variant(case,v) for v in m.VARIANTS]
        self.assertEqual(len({a["sha"] for a in z}),3,case)
        self.assertTrue(all(m.b.old.all_model_ok(a["rows"],a["n"],a["model"]) for a in z))
        choices=[m.index_or_raw(a["rows"],a["n"],"e12c1_cost_aware")["decision"]["eligible"] for a in z]
        self.assertEqual(len(set(choices)),1,case)
 def test_parity_certificates_width3_4_5_6_truth_table(self):
    for w in (3,4,5,6):
        vs=list(range(1,w+1))
        for rhs in (0,1):
            rows=[[v if bit==0 else -v for v,bit in zip(vs,bits)]
                  for bits in itertools.product((0,1),repeat=w)
                  if sum(bits)%2!=rhs]
            src=m.source_index_all_widths(rows,w)
            self.assertEqual(len(src["equations"]),1)
            self.assertEqual(len(src["used"]),len(rows))
            self.assertEqual(src["equations"][0]["rhs"],rhs)
            for assignment in itertools.product((False,True),repeat=w):
                truth={i+1:x for i,x in enumerate(assignment)}
                cnf=all(any((v>0)==truth[abs(v)] for v in row) for row in rows)
                xor=sum(int(truth[v]) for v in vs)%2==rhs
                self.assertEqual(cnf,xor)
 def test_partial_mask_and_extra_opposite_parity_fail_closed(self):
    for w in (3,4,5,6):
        rows=[[v if bit==0 else -v for v,bit in zip(range(1,w+1),bits)]
                for bits in itertools.product((0,1),repeat=w) if sum(bits)%2==1]
        self.assertEqual(len(m.source_index_all_widths(rows[:-1],w)["equations"]),0)
        self.assertEqual(len(m.source_index_all_widths(rows+[[i for i in range(1,w+1)]],w)["equations"]),0)
 def test_duplicate_original_mask_and_residual_never_deleted(self):
    original=[[v if bit==0 else -v for v,bit in zip(range(1,6),bits)]
             for bits in itertools.product((0,1),repeat=5) if sum(bits)%2==1]
    rows=original+[list(original[0])]+[[7,8,9]]
    idx=m.source_index_all_widths(rows,9)
    self.assertEqual(len(idx["used"]),16)
    self.assertNotIn(16,idx["used"])
    self.assertNotIn(17,idx["used"])
 def test_synthetic_out_of_domain_negative_controls_abstain_without_model_leak(self):
    for case in ("e12c1-exactone-t30","e12c1-mixed-xor3-n160","e12c1-planted-3sat-n200","e12c1-low-cover-w5-n180"):
        s=m.source(case)
        x=m.index_or_raw(s["rows"],s["n"],"e12c1_cost_aware")
        self.assertFalse(x["decision"]["eligible"],case)
        self.assertEqual(x["cnf_clauses"],s["rows"])
 def test_unknown_arms_rejected(self):
    with self.assertRaises(AssertionError):m.index_or_raw([[1]],1,"posthoc_cheat")
    with self.assertRaises(AssertionError):m.source("foreign_external_source")
 def test_aborted_frozen_width6_always_retains_source_residual(self):
    s=m.source("e12c1-random-hypergraph-w6-n160")
    c=m.index_or_raw(s["rows"],s["n"],"e12c1_cost_aware")
    self.assertEqual(c["cnf_clauses"],s["rows"])
    self.assertEqual(c["decision"]["full_source_width_distribution"][6],160)
if __name__=="__main__":unittest.main()
