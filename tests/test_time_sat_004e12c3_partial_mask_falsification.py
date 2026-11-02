#!/usr/bin/env python3
"""E12C3 preregulated source proof falsification with exact full original SAT model."""
from __future__ import annotations
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory
import itertools,sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"/"direct"))
import janus_time_sat_004e12c3_partial_mask_falsification as m

class C3PartialMaskTest(unittest.TestCase):
 def test_immutable_protocol_no_new_algorithm_claim(self):
    p=m.frozen()
    self.assertEqual((len(m.IDS),len(m.ARMS),len(m.VARIANTS)),(8,5,4))
    self.assertEqual((p["compute"]["VM_jobs"],p["compute"]["planned_cold_children"]),(16,640))
    self.assertEqual(p["scientific_gates"]["independent_external_originals"],0)
    self.assertTrue(p["candidate_policy"]["read_frozen_C2_source_policy_directly"])
 def test_all_original_full_SAT_models_and_variant_source_digests(self):
    originals=set()
    for case in m.IDS:
        s=m.original(case)
        self.assertNotIn(s["sha"],originals);originals.add(s["sha"])
        self.assertTrue(m.b.old.all_model_ok(s["rows"],s["n"],s["model"]))
        shas=set()
        for var in m.VARIANTS:
            t=m.variant(case,var)
            self.assertEqual(t["base_sha"],s["sha"])
            self.assertTrue(m.b.old.all_model_ok(t["rows"],t["n"],t["model"]))
            self.assertEqual(t["sha"],m.digest(t["bytes"]))
            self.assertNotIn(t["sha"],shas);shas.add(t["sha"])
            if var=="variable_renaming_polarity_flip":
                self.assertNotEqual(t["model_sha"],t["base_model_sha"])
            else:
                self.assertEqual(t["model_sha"],t["base_model_sha"])
                self.assertEqual(m.signature(t["rows"]),m.signature(s["rows"]))
        self.assertEqual(len(shas),4)
 def test_all_six_variable_source_full_mask_ablation_exactly_zero_false_XOR(self):
    for case in m.IDS:
        cfg=m.config(case);src=m.original(case)
        for v in m.VARIANTS:
            t=m.variant(case,v)
            observed=m.c1.source_index_all_widths(t["rows"],t["n"])["counts"].get(6,0)
            self.assertEqual(observed,cfg["full_equations"],case+" / "+v)
 def test_frozen_old_C2_source_choice_invariant_under_renaming(self):
    expected={
       "e12c3-hyper6-full-n112":"XOR",
       "e12c3-hyper6-full-n146":"XOR",
       "e12c3-hyper6-partial-n112":"RAW",
       "e12c3-hyper6-partial-n146":"RAW",
       "e12c3-hyper6-mixed-low-n128":"RAW",
       "e12c3-hyper6-mixed-high-n128":"XOR",
       "e12c3-hyper6-full-diluted-n128":"RAW",
       "e12c3-planted3sat-n224":"RAW"
    }
    for case,want in expected.items():
        outcomes={m.policy(s["rows"],s["n"],m.ARMS[0])["decision"]["choice"]
                  for s in (m.variant(case,v) for v in m.VARIANTS)}
        self.assertEqual(outcomes,{want},case)
 def test_partial_even_if_source_model_sat_does_not_imply_XOR(self):
    for width in (5,6):
        vs=list(range(1,width+1))
        rows=[[v if bit==0 else -v for v,bit in zip(vs,bits)]
              for bits in itertools.product((0,1),repeat=width)
              if sum(bits)%2==1]
        self.assertEqual(len(m.c1.source_index_all_widths(rows,width)["equations"]),1)
        for missing in (0,len(rows)//2):
            sub=[row for i,row in enumerate(rows) if i!=missing]
            self.assertEqual(len(m.c1.source_index_all_widths(sub,width)["equations"]),0)
            # The parity-violating assignment explicitly falsified only by a
            # removed source clause satisfies the reduced CNF; enforcing the
            # removed XOR would incorrectly discard this SAT assignment.
            omitted=rows[missing]
            assignment={abs(lit): lit<0 for lit in omitted}
            self.assertTrue(all(any((lit>0)==assignment[abs(lit)] for lit in row)
                                for row in sub))
            self.assertEqual(sum(int(assignment[v]) for v in vs)%2,1)
 def test_mixed_full_and_partial_selected_source_indices_never_touch_incomplete(self):
    for case in ("e12c3-hyper6-mixed-low-n128","e12c3-hyper6-mixed-high-n128",
                 "e12c3-hyper6-full-diluted-n128"):
        s=m.original(case)
        idx=m.c1.source_index_all_widths(s["rows"],s["n"])
        self.assertEqual(idx["counts"].get(6,0),m.config(case)["full_equations"])
        chosen=m.policy(s["rows"],s["n"],m.ARMS[0])
        used={i for eq in chosen["equations"] for i in eq["original_clause_indices"]}
        self.assertEqual(len(used),sum(len(eq["original_clause_indices"]) for eq in chosen["equations"]))
        # All non-proof-bearing clauses, including duplicate masks and every
        # incomplete parity block, remain byte-for-byte in the original residual.
        self.assertEqual(chosen["cnf_clauses"],[row for i,row in enumerate(s["rows"]) if i not in used])
 def test_source_lock_protects_complete_models_and_renamed_isomorphisms(self):
    with TemporaryDirectory() as root:
        from pathlib import Path
        folder=Path(root)
        lock=m.preflight(folder)
        reread,sha=m.checked_lock(folder/"SOURCE_LOCK.json")
        self.assertEqual(reread,lock)
        self.assertEqual(len(lock["sources"]),8)
        self.assertTrue(all(lock["sources"][case]["variable_renaming_polarity_flip"]["isomorphism_not_clause_reorder"] for case in m.IDS))
        (folder/"SOURCE_LOCK.sha256").write_text("0"*64+"  SOURCE_LOCK.json\n")
        with self.assertRaises(AssertionError):m.checked_lock(folder/"SOURCE_LOCK.json")
 def test_source_partials_not_immediately_solved_by_forbidden_EQ(self):
    for case in ("e12c3-hyper6-partial-n112","e12c3-hyper6-partial-n146"):
        s=m.original(case);selected=m.policy(s["rows"],s["n"],m.ARMS[0])
        self.assertEqual(selected["equations"],[])
        self.assertEqual(selected["cnf_clauses"],s["rows"])
 def test_unsupported_status_candidate_rejected(self):
    with self.assertRaises(AssertionError):m.policy([[1]],1,"posthoc_invalid_arm")
    with self.assertRaises(AssertionError):m.original("external_false_source")
    self.assertNotIn("UNSAT",m.ALLOWED)
if __name__=="__main__":unittest.main()
