#!/usr/bin/env python3
"""TIME-SAT-004D1: exhaustive parity source tests, including true 25x25 size."""
from __future__ import annotations
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"experiments"/"direct"))
from janus_time_sat_004d1_xor import (
    group_parity_equations,solve_if_exact_xor,
    check_original_cnf,independently_replay_unsat_combination
)

def encode_xor(variables, rhs):
    k=len(variables)
    return [tuple(-v if (mask>>i)&1 else v
                  for i,v in enumerate(variables))
            for mask in range(1<<k)
            if (mask.bit_count()&1)!=rhs]

def grid_game(n_side,seed=2026110105):
    rng=random.Random(seed)
    n=n_side*n_side
    planted=rng.getrandbits(n)
    rows=[]
    for y in range(n_side):
        for x in range(n_side):
            support=[y*n_side+x+1]
            for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
                xx=x+dx;yy=y+dy
                if 0<=xx<n_side and 0<=yy<n_side:
                    support.append(yy*n_side+xx+1)
            support=sorted(support)
            rhs=sum((planted>>(v-1))&1 for v in support)&1
            rows.extend(encode_xor(support,rhs))
    return rows,n

class ExactXor004D1Tests(unittest.TestCase):
    def test_random_small_all_models_are_valid(self):
        rng=random.Random(2026110106)
        for k in range(1,7):
            for trial in range(8):
                rhs=rng.randrange(2)
                src=encode_xor(list(range(1,k+1)),rhs)
                solved=solve_if_exact_xor(src,k)
                self.assertEqual(solved["verdict"],"SAT_ORIGINAL_MODEL_VERIFIED")
                answer=sum(1<<(abs(v)-1) for v in solved["model"] if v>0)
                self.assertTrue(check_original_cnf(src,k,answer))
                self.assertEqual(sum((answer>>i)&1 for i in range(k))&1,rhs)

    def test_small_exact_xor_unsat_has_source_bound_combination(self):
        rows=encode_xor([1,2],0)+encode_xor([1],1)+encode_xor([2],0)
        got=solve_if_exact_xor(rows,2)
        self.assertEqual(got["verdict"],"GF2_UNSAT_SAME_ADMIN_REPLAY_ONLY")
        receipt=got["xor_contradiction_equation_indices"]
        self.assertTrue(independently_replay_unsat_combination(rows,2,receipt))
        self.assertFalse(independently_replay_unsat_combination(rows,2,receipt+[receipt[0]]))
        self.assertFalse(independently_replay_unsat_combination(rows,2,[1000]))

    def test_incomplete_or_mixed_is_never_claimed_sat(self):
        rows=encode_xor([1,2,3],1)
        for case in (rows[:-1],
                     rows+[(1,2)],
                     [(1,2),(1,-2)],
                     [(1,1)],
                     [(1,-1)],
                     [()]):
            result=solve_if_exact_xor(case,3)
            self.assertEqual(result["verdict"],"ABSTAIN_NO_SAT_CLAIM",case)

    def test_bounded_rejects_invalid_data(self):
        for rows,n in [([(0,)],2),([(3,)],2),([(True,)],2),
                       ([(1,)],5001), ([(1,)]*30001,2),
                       ([(1,2,3,4,5,6,7)],7)]:
            self.assertNotEqual(group_parity_equations(rows,n)["status"],
                                "EXACT_XOR_COVER_PASS")

    def test_25_by_25_lights_out_encoded_control_dimensions_and_model(self):
        # Synthetic control of expected dimensions, NOT the external original.
        rows,n=grid_game(25)
        self.assertEqual(n,625)
        self.assertEqual(len(rows),9216)
        self.assertEqual(sum(map(len,rows)),45312)
        receipt=solve_if_exact_xor(rows,n)
        self.assertEqual(receipt["coverage_status"],"EXACT_XOR_COVER_PASS")
        self.assertEqual(receipt["equation_count"],625)
        self.assertEqual(receipt["verdict"],"SAT_ORIGINAL_MODEL_VERIFIED")
        assignment=sum(1<<(abs(v)-1) for v in receipt["model"] if v>0)
        self.assertTrue(check_original_cnf(rows,n,assignment))
        self.assertEqual(len(receipt["model"]),n)

if __name__=="__main__":
    unittest.main()
