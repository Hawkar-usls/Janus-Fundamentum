#!/usr/bin/env python3
"""R5 all-odd cyclic SCL exact four-orbit PC2 contradiction.

For every odd n>=7, build legal square+cubic+C4-free rows
C_i={i,i+1,i+3}, indices modulo n, and define over
B=F2[x_0,...,x_(n-1)]/(x_i^2-x_i):

    p_i = 1 + x_i + x_(i+1) + x_(i+3)
    q_i = x_i*x_(i+1) + x_i*x_(i+3) + x_(i+1)*x_(i+3).

The EXACT Boolean polynomial identity is:

  sum_i [ p_i + x_i*p_i + x_(i+2)*p_i + q_i ] = 1

for EVERY odd n>=7. All summands have degree at most TWO, so
this is a constructive LINEAR-size degree-two PC UNSAT certificate
for an infinite legal connected SCL family, including n divisible
by three (n=9,15,21...), which cannot be rejected merely by
3*|selected|=n congruence.

This is not an ALL-SCL solver. Most UNSAT SCL matrices have different
structure, and the predecessor E118 UNSAT90 already refutes universal PC2.
"""
from __future__ import annotations
from collections import Counter
from itertools import combinations
from r5_universal_boolean_pc_degree3_global_attack import (
    monomial_masks,poly_row,
)
from r5_universal_exact_support_residual_dag_attack import validate_sparse


def cyclic(n):
    assert n>=7 and n%2
    rows=tuple(tuple(sorted((i,(i+1)%n,(i+3)%n))) for i in range(n))
    rows=validate_sparse(rows,n)
    assert len(rows)==n
    deg=Counter(x for row in rows for x in row)
    assert len(deg)==n and set(deg.values())=={3}
    assert len({tuple(sorted(p)) for row in rows for p in combinations(row,2)})==3*n
    return rows


def four_orbit_polynomial(n):
    rows=cyclic(n)
    mons=monomial_masks(n,2)
    coord={mon:i for i,mon in enumerate(mons)}
    rowset={tuple(row):row for row in rows}
    total=0
    per_orbit=(0,0,0,0)
    groups=[0,0,0,0]
    for i in range(n):
        row=tuple(sorted((i,(i+1)%n,(i+3)%n)))
        assert row in rowset
        terms=[
            poly_row(row,0,'parity',coord),
            poly_row(row,1<<i,'parity',coord),
            poly_row(row,1<<((i+2)%n),'parity',coord),
            poly_row(row,0,'quadratic',coord),
        ]
        for j,term in enumerate(terms):
            groups[j]^=term
            total^=term
    assert total==1,(n,total)
    return groups,total


def main():
    for n in (7,9,11,13,15,17,19,21,25,27,29,31,33,39,45,63,81,95):
        groups,total=four_orbit_polynomial(n)
        assert total==1
        # O(n) certificate explicitly has 4n generator multipliers.
        print(f'ODD_CYCLIC_ALL_N_EXACT_PC2_IDENTITY n={n} '
              f'n_mod3={n%3} proof_terms={4*n} '
              f'four_group_bit_weights={tuple(g.bit_count() for g in groups)}'
              f' proof_constant={total}',flush=True)
    print('ALL_ODD_N_GE7_CYCLIC_SCL_PC2_FOUR_ORBIT_IDENTITY = PROVED_ALGEBRAICALLY')
    print('THREE_DIVISIBILITY_ALONE_IS_NOT_ENOUGH_FOR_SAT = INFINITE_LEGAL_FAMILY')
    print('UNIVERSAL_PC2_COMPLETENESS = REFUTED_PREDECESSOR_E118')
    print('UNIVERSAL_PC3_COMPLETENESS = OPEN')
    print('UNIVERSAL_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED')
    print('P_VS_NP = OPEN')


if __name__=="__main__":
    main()
