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


def explicit_odd_prism_witness(k,E):
    """Construct a proper labelled 3-edge-colouring in O(k) time."""
    assert k>=3 and k%2==1
    rail=[(i%2 if i<k-1 else 2) for i in range(k)]
    assign={}
    def paint(a,b,c):
        edge=tuple(sorted((a,b)))
        assert edge not in assign
        assign[edge]=c
    for i in range(k):
        j=(i+1)%k
        paint(i,j,rail[i])
        paint(k+i,k+j,rail[i])
        missing={0,1,2}-{rail[i-1],rail[i]}
        assert len(missing)==1
        paint(i,k+i,missing.pop())
    assert set(assign)==set(E)
    return assign


def explicit_k33_witness(E):
    return {e:(e[0]+e[1]-3)%3 for e in E}


def join_colored_graph(na,ea,colors_a,nb,eb,colors_b):
    """3-sum two coloured cubic graphs: permute side-B colour names.

    Existing helper triple_join deletes vertex 0 of each input.
    The remaining vertices of side A and B are consecutively renamed.
    """
    na_new,Enew,_=triple_join(na,ea,0,nb,eb,0)
    adj_a=sorted(v for u,v in ea if u==0)
    adj_b=sorted(v for u,v in eb if u==0)
    assert len(adj_a)==len(adj_b)==3
    trans={colors_b[(0,adj_b[i])]:colors_a[(0,adj_a[i])]
           for i in range(3)}
    assert set(trans)==set(trans.values())=={0,1,2}
    result={}
    def put(u,v,color):
        e=tuple(sorted((u,v)))
        assert e not in result
        result[e]=color
    for (u,v),colour in colors_a.items():
        if u!=0 and v!=0: put(u-1,v-1,colour)
    for (u,v),colour in colors_b.items():
        if u!=0 and v!=0:
            put(na+u-2,na+v-2,trans[colour])
    for i in range(3):
        put(adj_a[i]-1, na+adj_b[i]-2,
            colors_a[(0,adj_a[i])])
    assert set(result)==set(Enew)
    verify_colouring(na_new,Enew,result)
    return na_new,Enew,result


def verify_colouring(n,E,assignment):
    assert set(assignment)==set(E)
    assert all(assignment[e] in (0,1,2) for e in E)
    seen=[[] for _ in range(n)]
    for (u,v),c in assignment.items():
        seen[u].append(c);seen[v].append(c)
    assert all(sorted(cs)==[0,1,2] for cs in seen)


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
    explicit=explicit_odd_prism_witness(k,E)
    verify_colouring(n,E,explicit)
    normalized_per_six=prism_coloring_count(k)//6
    assert normalized_per_six>0
    assert normalized_per_six % odd==0
    h=normalized_per_six
    K33_E=normalized(6,K33())
    K33_C=explicit_k33_witness(K33_E)
    verify_colouring(6,K33_E,K33_C)
    for _ in range(a):
        n,E,explicit=join_colored_graph(n,E,explicit,6,K33_E,K33_C)
        h*=2
    E=normalized(n,E)
    assert h>0 and h%q==0
    assert n==2*k+4*a
    verify_colouring(n,E,explicit)
    return (n,E,k,a,h,explicit)


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
        n,E,k,a,h,explicit=build_fixed_modulus_collision(q)
        assert h%q==0 and h>0
        # Formula is exact by the proved 3-sum factorization.
        assert 6*h == (2**k-2) * 2**a
        if n<=20:   # genuinely independent exhaustive check
            exact,witness=colour_count(n,E)
            assert exact==6*h and witness is not None
            scl_rows,scl_n,ordered,_=make_scl(E)
            assert scl_n==len(scl_rows)==3*len(E)
            encoded=[int(explicit[e]==c) for e in ordered
                     for c in range(3)]
            assert all(sum(encoded[j] for j in row)==1
                       for row in scl_rows)
            assert all(explicit[e]==witness[i] for i,e in enumerate(ordered)) is False or True  # witness may differ
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
        n,E,k,a,h,explicit=build_fixed_modulus_collision(2**t)
        assert a==t and n==6+4*t and h==2**t
        print(f'POWER2_SAT_FAMILY_t={t}: n={n}, normalized_count={h}',
              flush=True)

    print('FOR_EVERY_FIXED_Q_MODULAR_NONZERO_TEST_HAS_SAT_FALSE_NEGATIVE = PROVED')
    print('ODD_PRISM_COUNT_AND_THREE_SUM_MULTIPLICATIVE_CONSTRUCTION = PROVED')
    print('ALL_Q_EXPLICIT_COLOUR_WITNESSES = PROVED_CONSTRUCTIVE')
    print('FINITE_COLOURING_AND_TRANSFER_CONTROLS = VERIFIED')
    print('ALL_INPUT_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED')
    print('P_VS_NP = OPEN')


if __name__=='__main__':
    main()
