#!/usr/bin/env python3
"""004D4C proof tests: index overflow is partial, never an UNSAT/SAT claim."""
from __future__ import annotations
import itertools
import random
import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"/"direct"))
from janus_time_sat_004d4c_bounded_support import extract_bounded_mixed_xor
from janus_time_sat_004d4_mixed_xor import (
    extract_mixed_xor,representation_satisfied
)

def parity(variables,rhs):
    return [tuple(-v if (mask>>i)&1 else v
                  for i,v in enumerate(variables))
            for mask in range(1<<len(variables))
            if (mask.bit_count()&1)!=rhs]

class BoundedPartialIndex(unittest.TestCase):
    def assert_equivalent(self,rows,n,max_groups):
        p=extract_bounded_mixed_xor(rows,n,max_groups=max_groups)
        self.assertEqual(p["status"],"SOURCE_PARTITION_VERIFIED")
        a=p["xor_source_clause_indices"]
        b=p["residual_source_clause_indices"]
        self.assertEqual(sorted(a+b),list(range(len(rows))))
        self.assertEqual(len(set(a)&set(b)),0)
        self.assertEqual(p["residual_clauses"],[list(rows[i]) for i in b])
        self.assertEqual(p["source_xor_clauses"]+p["source_residual_clauses"],len(rows))
        self.assertEqual(p["SAT_or_UNSAT_verdict"],"NOT_ATTEMPTED_SOURCE_ONLY")
        for bits in itertools.product((False,True),repeat=n):
            vals={i+1:bits[i] for i in range(n)}
            direct=all(any(vals[abs(l)]==(l>0) for l in row) for row in rows)
            self.assertEqual(direct,representation_satisfied(p,vals),
                             (rows,bits,p["equations"]))
        return p

    def test_select_valid_first_support_even_when_later_groups_saturate(self):
        rows=parity([1,2],0)+[(3,),(4,),(-3,),(2,3)]
        p=self.assert_equivalent(rows,4,max_groups=1)
        self.assertTrue(p["index_exhausted"])
        self.assertEqual(p["complete_xor_equation_count"],1)
        self.assertEqual(p["source_xor_clauses"],2)
        self.assertEqual(p["source_residual_clauses"],4)

    def test_late_complete_unindexed_xor_stays_in_original_residual(self):
        rows=[(1,2)]+parity([3,4],1)
        p=self.assert_equivalent(rows,4,max_groups=1)
        self.assertTrue(p["index_exhausted"])
        self.assertEqual(p["complete_xor_equation_count"],0)
        self.assertEqual(p["residual_source_clauses"],len(rows))
        self.assertIn("PARTIAL_SCAN",p["interpretation_when_index_exhausted"])

    def test_indexed_group_may_complete_after_cap_is_reached(self):
        rows=[(1,2),(3,),(-1,-2)]
        p=self.assert_equivalent(rows,3,max_groups=1)
        self.assertTrue(p["index_exhausted"])
        self.assertEqual(p["complete_xor_equation_count"],1)
        self.assertEqual(p["source_xor_clauses"],2)
        self.assertEqual(p["source_residual_clauses"],1)

    def test_multiple_opposite_parities_keep_contradiction_semantics(self):
        rows=parity([1,2,3],0)+parity([1,2,3],1)+[(4,)]
        p=self.assert_equivalent(rows,4,max_groups=1)
        self.assertEqual(p["complete_xor_equation_count"],2)
        self.assertEqual(p["source_residual_clauses"],1)

    def test_empty_wide_tautology_duplicate_are_not_lost(self):
        rows=parity([1,2],1)+[(1,-1),(),tuple(range(1,8)),(2,-1),(-1,2)]
        p=extract_bounded_mixed_xor(rows,7,max_groups=1)
        self.assertEqual(p["status"],"SOURCE_PARTITION_VERIFIED")
        self.assertEqual(sorted(p["xor_source_clause_indices"]+
                                p["residual_source_clause_indices"]),
                         list(range(len(rows))))
        self.assertIn([],p["residual_clauses"])
        self.assertIn(list(range(1,8)),p["residual_clauses"])

    def test_malformed_and_excess_budget_abstain_not_partial_verdict(self):
        for rows,n,max_groups in [
            ([(0,)],1,1), ([(2,)],1,1), ([(True,)],1,1),
            ([(1,)],0,1), ([(1,)],1,0), ([(1,)],1,20001),
            ([(1,)]*30001,1,1)]:
            self.assertTrue(extract_bounded_mixed_xor(
                rows,n,max_groups=max_groups)["status"].startswith("ABSTAIN"))

    def test_deterministic_randomized_equivalence_with_forced_overflow(self):
        rng=random.Random(20261101046)
        for n in range(2,6):
            for trial in range(24):
                rows=[]
                for k in range(rng.randrange(4,18)):
                    w=rng.randrange(0,n+1)
                    vv=rng.sample(list(range(1,n+1)),w)
                    rows.append(tuple(v if rng.randrange(2) else -v for v in vv))
                self.assert_equivalent(rows,n,max_groups=2)

    def test_zero_budget_regression_is_only_for_old_not_new(self):
        rows=[(1,),(2,),(-1,),(-2,), (1,2),(3,)]
        self.assertEqual(extract_mixed_xor(rows,3)["status"],
                         "SOURCE_PARTITION_VERIFIED")
        p=self.assert_equivalent(rows,3,max_groups=1)
        self.assertEqual(p["complete_xor_equation_count"],2)
        self.assertEqual(p["source_residual_clauses"],4)

if __name__=="__main__":
    unittest.main()
