#!/usr/bin/env python3
"""Exact all-n cyclic SCL n%3 != 0 challenge to UNIVERSAL degree-3 PC.

For every odd n>=7, build n legal distinct triples
   C_i={i,i+1,i+3} mod n.
The differences are +/-1,+/-2,+/-3, all distinct modulo n>=7,
so every two checks share at most one variable, row/col degrees
are exactly 3, Levi is connected. For n mod3 !=0, Boolean
Exact-One is PROVED UNSAT by 3*|x|=n.

The translation i->i+1 is a syntactic automorphism of ODD
order n. Averaging over this group over GF2 is a projection
that preserves constant-one PC refutability EXACTLY.
Test full degree-3 PC using all invariant monomial orbits:
NO unexamined non-invariant refutation can exist if this
test returns INCONCLUSIVE.

Either obtain a finite LEGAL UNSAT degree-3 non-refutation
counterexample, or return a finite inconclusive search report.
No claims about universal P time for ExactOne.
"""
from __future__ import annotations
from itertools import combinations

from r5_universal_odd_automorphism_pc3_snark_probe import pc3_symmetry_test
from r5_universal_exact_support_residual_dag_attack import validate_sparse


def cyclic_n(n):
    assert n>=7 and n%2==1
    rows=tuple(tuple(sorted((i,(i+1)%n,(i+3)%n))) for i in range(n))
    rows=validate_sparse(rows,n)
    assert len(rows)==n
    sigma=tuple((i+1)%n for i in range(n))
    assert {tuple(sorted(sigma[v] for v in row)) for row in rows}==set(rows)
    assert n%3!=0, "Choose a guaranteed counting-UNSAT target"
    return rows,sigma


def main():
    tested=0
    for n in (7,11,13,17,19,23,25,29,31,35,37,41,43,47,53,59,65,71,77,83,89,95):
        rows,sigma=cyclic_n(n)
        refuted,stats=pc3_symmetry_test(rows,sigma,n)
        tested+=1
        print(f'CYCLIC_ALL_SCL_N={n} SAT_TRUTH=UNSAT_BY_3_DIVISIBILITY '
              f'FULL_PC3={"PROVED_UNSAT" if refuted else "INCONCLUSIVE"} '
              f'STATS={stats}',flush=True)
        if not refuted:
            print(f'EXPLICIT_ALL_LEGAL_SCL_PC3_NONREFUTATION_N={n}',flush=True)
            print('UNIVERSAL_FIXED_PC3_COMPLETENESS = REFUTED_EXACT_GROUP_RANK',flush=True)
            print('UNIVERSAL_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED')
            print('P_VS_NP = OPEN')
            return
    print(f'CYCLIC_UNSAT_ALL_CHECKED_REFUTED_BY_PC3 count={tested}',flush=True)
    print('UNIVERSAL_FIXED_PC3_COMPLETENESS = STILL_OPEN')
    print('UNIVERSAL_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED')
    print('P_VS_NP = OPEN')


if __name__=="__main__":
    main()
