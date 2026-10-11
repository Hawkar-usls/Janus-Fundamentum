#!/usr/bin/env python3
"""Universal moment-aggregation theorem: exact rank-subset formulation.

Scientific scope: rigorous identity for ALL square/cubic 0-1 inputs,
plus finite exact replay. NOT a polynomial-time universal solver.

For n=3m, K=ker_F2(A), all k in K have even weights <=2m.
Number of Exact-One witnesses = sum_{k in K} binom(|k|/2,m).

Expand binom(w/2,m) in the binomial polynomial basis binom(w,s):
    c_s = Delta^s [binom(w/2,m)]_{w=0}.
Each binomial moment sum_{k in K} binom(|k|,s) equals an
aggregate over coordinate-subset projection ranks, all individual
summands computable in polynomial time by GF2 elimination.
Computing the whole aggregate in polynomial time for EVERY input
is the UNPROVED / NP-hard universal algorithmic step.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from math import comb

from r5_e61_two_level_kernel_hoffman_regular_set import (
    P_SAT, Q_SAT, P_UNSAT, Q_UNSAT, build_A,
)
from r5_e64_connected_postquotient_nullity_firewall import tutte12_incidence
from r5_e65_transpose_asymmetry_quantized_defect import gf2_rref_basis


def half_binom(w: int, m: int) -> Fraction:
    v=Fraction(1)
    for i in range(m):
        v*=Fraction(w,2)-i
        v/=i+1
    return v


def binomial_basis_coefficients(m: int) -> list[Fraction]:
    # Newton forward differences: f(w) = sum_s Delta^s f(0) binom(w,s).
    return [
        sum(
            ((-1)**(s-j)*comb(s,j)*half_binom(j,m) for j in range(s+1)),
            Fraction(0),
        )
        for s in range(m+1)
    ]


def weights_of_kernel(A):
    n=len(A)
    assert n % 3==0
    assert all(len(row)==n and sum(row)==3 for row in A)
    assert all(sum(A[i][j] for i in range(n))==3 for j in range(n))
    _,_,basis=gf2_rref_basis(A)
    # Independent parity-kernel basis.
    rb=[sum(1<<j for j,v in enumerate(row) if v) for row in A]
    assert all(all((a&v).bit_count()%2==0 for a in rb) for v in basis)
    weights=[]
    for sel in range(1<<len(basis)):
        w=0
        for i,v in enumerate(basis):
            if sel>>i&1:
                w^=v
        assert w.bit_count() % 2==0
        assert w.bit_count()<=2*n//3
        weights.append(w)
    return basis,weights


def consistent_kernel_count(basis, n, ones=(), pins=None):
    """Count k in the GF2 kernel with k_j=1 on ones, k_j=pins[j] on pins.

    Exact polynomial work for EACH fixed subset. Affine RHS included.
    """
    d=len(basis)
    constraints=dict(pins or {})
    for j in ones:
        if j in constraints and constraints[j]!=1:
            return 0
        constraints[j]=1
    pivots={}
    full=(1<<d)-1
    for coord,rhs in sorted(constraints.items()):
        assert 0<=coord<n and rhs in (0,1)
        coeff=sum(((basis[t]>>coord)&1)<<t for t in range(d))
        packed=coeff | (rhs<<d)
        while packed&full:
            p=((packed&full).bit_length()-1)
            if p not in pivots:
                pivots[p]=packed
                break
            packed^=pivots[p]
        if not packed&full and packed>>d:
            return 0
    return 1<<(d-len(pivots))


def rank_moments(basis,n,m,pins=None):
    result=[]
    for s in range(m+1):
        B=sum(
            consistent_kernel_count(basis,n,S,pins)
            for S in combinations(range(n),s)
        )
        result.append(B)
    return result


def direct_count(words,m,pins=None):
    pins=pins or {}
    valid=[w for w in words if all((w>>i)&1==v for i,v in pins.items())]
    indicator=sum(half_binom(w.bit_count(),m) for w in valid)
    count=sum(w.bit_count()==2*m for w in valid)
    assert indicator==count
    return count,valid


def small_controls(A,expected):
    n=len(A)
    m=n//3
    basis,words=weights_of_kernel(A)
    coeff=binomial_basis_coefficients(m)
    for pins in [{},{0:0},{0:1},{0:0,1:1},{0:1,1:0}]:
        moments=rank_moments(basis,n,m,pins)
        direct,valid=direct_count(words,m,pins)
        assert all(
            moments[s]==sum(comb(w.bit_count(),s) for w in valid)
            for s in range(m+1)
        )
        reconstructed=sum((c*B for c,B in zip(coeff,moments)),Fraction(0))
        assert reconstructed==direct,(pins,reconstructed,direct)
        if not pins:
            assert direct==expected
    print(f"n={n} expected_sat_count={expected}: all 5 pin/rank-moment checks PASS")
    return coeff


def large_controls(A,expected):
    n=len(A)
    m=n//3
    basis,words=weights_of_kernel(A)
    count,_=direct_count(words,m)
    assert count==expected
    print(f"n={n} GF2 nullity={len(basis)} top_weight={2*m} exact_cover_count={count} PASS")


def main():
    assert half_binom(0,4)==0
    assert all(half_binom(2*t,4)==0 for t in range(4))
    assert half_binom(8,4)==1
    coeff=small_controls(build_A(P_SAT,Q_SAT),1)
    assert len(coeff)==5
    small_controls(build_A(P_UNSAT,Q_UNSAT),0)

    R=tutte12_incidence()
    large_controls(R,0)
    large_controls([list(c) for c in zip(*R)],36)

    for n in (12,30,63,90):
        m=n//3
        candidates=sum(comb(n,s) for s in range(m+1))
        print(f"rank-subset direct aggregation n={n}, m={m}: {candidates} subsets")
    assert sum(comb(63,s) for s in range(22))==51380672802765632
    print("ALL-INSTANCES BINOMIAL MOMENT IDENTITY=PROVED BY COUNTING")
    print("PER-SUBSET GF2 RANK COUNT=POLYNOMIAL; GLOBAL AGGREGATION NOT POLYNOMIAL")
    print("UNIVERSAL_POLYNOMIAL_AGGREGATOR=OPEN; P_VS_NP=OPEN")


if __name__=="__main__":
    main()
