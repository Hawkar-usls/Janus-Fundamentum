#!/usr/bin/env python3
"""004D3 source-frozen validation + safe parity abstention, no network."""
from __future__ import annotations
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"/"direct"))
from janus_time_sat_004d3_probe import verify_frozen_manifest,bounded_source_shape
from janus_time_sat_004d1_xor import solve_if_exact_xor,independently_replay_unsat_combination

def encode(vars_,rhs):
    return [tuple((-v if (mask>>i)&1 else v) for i,v in enumerate(vars_))
            for mask in range(1<<len(vars_)) if (mask.bit_count()&1)!=rhs]

class Sat004D3FrozenTests(unittest.TestCase):
    def test_frozen_nine_official_ids_exclude_previous_and_have_categories(self):
        j=verify_frozen_manifest()
        self.assertEqual(len(j),9)
        self.assertEqual([x["family"] for x in j][:2],["lights-out","lights-out"])
        self.assertEqual([x["upstream_metadata_label_UNVERIFIED"] for x in j][:2],
                         ["sat","unsat"])
        self.assertEqual(len({x["GBD_database_id_NOT_SHA256"] for x in j}),9)

    def test_new_unseen_public_source_is_not_inferred_from_family(self):
        # Caller must check all clause signs, not trust a family label.
        for rows in [
          [(1,2,3),(-1,2,3)],
          encode([1,2,3],1)+[(1,4)],
          encode([1,2,3],0)[:-1],
          [(1,1)],[(1,-1)]]:
            o=solve_if_exact_xor(rows,4)
            self.assertEqual(o["verdict"],"ABSTAIN_NO_SAT_CLAIM")

    def test_exact_satisfiable_and_source_bound_unsatisfiable(self):
        a=encode([1,2,3],0)+encode([2,3,4],1)
        r=solve_if_exact_xor(a,4)
        self.assertEqual(r["verdict"],"SAT_ORIGINAL_MODEL_VERIFIED")
        b=encode([1,2],0)+encode([1],1)+encode([2],0)
        u=solve_if_exact_xor(b,2)
        self.assertEqual(u["verdict"],"GF2_UNSAT_SAME_ADMIN_REPLAY_ONLY")
        self.assertTrue(independently_replay_unsat_combination(
                        b,2,u["xor_contradiction_equation_indices"]))

    def test_known_source_size_budgets_decline_without_loading(self):
        base={"n_variables":625,"n_clauses":9216,
              "n_literal_occurrences":45312,"max_clause_width":5}
        self.assertTrue(bounded_source_shape(base))
        for key,over in [("n_variables",5001),("n_clauses",30001),
                         ("n_literal_occurrences",120001),
                         ("max_clause_width",7)]:
            variant=dict(base,key="unused")
            variant.pop("key")
            variant[key]=over
            self.assertFalse(bounded_source_shape(variant))

    def test_frozen_manifest_is_safe_data_not_hidden_test(self):
        path=Path("experiments/time_sat_004_external/PREREGISTERED_004D3_SATCOMP2026_MULTIFAMILY_20261101.json")
        j=json.loads(path.read_text())
        self.assertEqual(j["cohort_type"],
                         "PUBLIC_EXTERNAL_ORIGIN_NEW_DEVELOPMENT_COHORT_NOT_SEALED_HOLDOUT")
        self.assertEqual(j["frozen_predeclared_protocol"]["C023_main"],"UNCHANGED")

if __name__=="__main__":
    unittest.main()
