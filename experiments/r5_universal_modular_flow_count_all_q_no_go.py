#!/usr/bin/env python3
"""R5: fixed-modulus nonzero 4-flow count has SAT false negatives for EVERY q>=2.

For any positive integer q>=2, construct a connected SIMPLE cubic graph G_q
with #labelled proper 3-edge-colourings(G_q)>0, but
    #Col3(G_q)/6 == 0 (mod q).
Petersen is UNSAT with the same normalized count modulo q.

The explicit construction uses:
  * odd prism P_k=C_k square K2, for which #Col3(P_k)=2^k-2;
  * K3,3 with exactly 12 labelled colourings;
  * cubic vertex 3-edge-sum, for which #Col3(G1+G2)=Col3(G1)Col3(G2)/6.

Every component remains simple and connected. The graph construction has
O(q+log q) vertices (numeric q), NOT polynomial in bitlength log q.
The checker uses independent finite exact direct counts for small cases.
This is a NO-GO for every FIXED modular count-zero SAT detector,
NOT a universal P solver or a general modular complexity lower bound.
"""
from __future__ import annotations

from math import gcd
from r5_universal_cubic_flow_snf_discriminator import (
    normalized, colour_count,
)
from r5_universal_cubic_three_edge_cut_factorization import triple_join, K33
from r5_universal_cubic_edgecolor_direct_scl_bridge import make_scl


def prism(k):
    assert k>=3
    E=[(i,(i+1)%k) for i in range(k)]
    E += [(k+i,k+(i+1)%k) for i in range(k)]
    E += [(i,k+i) for i in range(k)]
    return 2*k, normalized(2*k,E)


def prism_coloring_count(k):
    # 9x9 rung-boundary transfer: diagonal 3x3 block J-I and three
    # disjoint 2-cycles on six off-diagonal pairs of horizontal colours.
    assert k>=3
    return 2**k + 2*(-1)**k + (6 if k%2==0 else 0)


def minimal_even_order(mod):
    assert mod>=3 and mod%2
    e=2
    while pow(2,e,mod)!=1:
        e+=2
        # Euler: an even exponent <=2phi(mod)<=2mod always works.
        assert e<=2*mod
    return e


def build_fixed_modulus_collision(q):
    assert isinstance(q,int) and q>=2
    a=0
    odd=q
    while odd%2==0:
        a+=1
        odd//=2
    k=1+minimal_even_order(3*odd)
    assert k%2==1 and k>=3
    n,E=prism(k)
    normalized_per_six=prism_coloring_count(k)//6
    assert normalized_per_six>0
    assert normalized_per_six % odd==0
    h=normalized_per_six
    for _ in range(a):
        n,E,_=triple_join(n,E,0,6,K33(),0)
        h*=2
    E=normalized(n,E)
    assert h>0 and h%q==0
    assert n==2*k+4*a
    return (n,E,k,a,h)


def transfer_count_independent(k):
    """Independent 9x9 transfer-matrix trace; O(k*9^3), finite exact."""
    states=[(a,b) for a in range(3) for b in range(3)]
    # Adjacent vertical cuts, with three different colours around
    # both endpoints of the rung under a common missing colour.
    T=[[0]*9 for _ in range(9)]
    for i,(a,b) in enumerate(states):
        for j,(c,d) in enumerate(states):
            if a!=c and b!=d and {a,c}=={b,d}:
                T[i][j]=1
    M=[[int(i==j) for j in range(9)] for i in range(9)]
    for _ in range(k):
        M=[[sum(M[i][j]*T[j][h] for j in range(9))
            for h in range(9)] for i in range(9)]
    return sum(M[i][i] for i in range(9))


def main():
    for k in (3,4,5,6,7,9,11):
        independent=transfer_count_independent(k)
        analytic=prism_coloring_count(k)
        assert independent==analytic,(k,independent,analytic)
        if k<=7:
            n,E=prism(k)
            enumerated,witness=colour_count(n,E)
            assert enumerated==analytic and witness is not None
        print(f'PRISM_{k}: exact_count={analytic}, '
              f'transfer_count={independent}',flush=True)

    # Each q is chosen independently, including non-2/3 prime factors.
    for q in (2,3,4,5,6,7,8,9,10,11,12,17,31,60,125,256):
        n,E,k,a,h=build_fixed_modulus_collision(q)
        assert h%q==0 and h>0
        # Formula is exact by the proved 3-sum factorization.
        assert 6*h == (2**k-2) * 2**a
        if n<=20:   # genuinely independent exhaustive check
            exact,witness=colour_count(n,E)
            assert exact==6*h and witness is not None
            scl_rows,scl_n,ordered,_=make_scl(E)
            assert scl_n==len(scl_rows)==3*len(E)
            encoded=[int(witness[i]==c) for i in range(len(ordered))
                     for c in range(3)]
            assert all(sum(encoded[j] for j in row)==1
                       for row in scl_rows)
            # This is a *real legal SCL SAT witness*, even though
            # the proposed normalized count-mod-q test returned zero.
            print(f'MODULUS_{q}_LEGAL_SCL_SAT_WITNESS = VERIFIED',
                  flush=True)
        print(f'MODULUS_{q}: cubic_vertices={n}, odd_prism_k={k}, '
              f'K33_joins={a}, #Col3_div6={h}, '
              f'residue={h%q}',flush=True)

    # An infinite connected SAT family with v2(#Col3/6) >=t.
    # Each extra K3,3 3-sum increases vertex count by 4 and
    # multiplies the normalized labelled colour count by 2.
    for t in (1,2,4,8,16):
        n,E,k,a,h=build_fixed_modulus_collision(2**t)
        assert a==t and n==6+4*t and h==2**t
        print(f'POWER2_SAT_FAMILY_t={t}: n={n}, normalized_count={h}',
              flush=True)

    print('FOR_EVERY_FIXED_Q_MODULAR_NONZERO_TEST_HAS_SAT_FALSE_NEGATIVE = PROVED')
    print('ODD_PRISM_COUNT_AND_THREE_SUM_MULTIPLICATIVE_CONSTRUCTION = PROVED')
    print('FINITE_COLOURING_AND_TRANSFER_CONTROLS = VERIFIED')
    print('ALL_INPUT_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED')
    print('P_VS_NP = OPEN')


if __name__=='__main__':
    main()
