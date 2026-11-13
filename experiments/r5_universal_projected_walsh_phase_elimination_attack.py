#!/usr/bin/env python3
"""Exact ONE-STEP cyclotomic phase elimination via projected Walsh rank.

Goal of the research is universal poly-time phase evaluation, not obtained.

For an even-weight binary kernel K and any basis direction v:
  F_v(t)=zeta^(wt(u(t))/2) * g_v(t)
  g_v(t)=1+zeta^(wt(v)/2 - wt(u(t)&v)),
where u(t)=XOR(other basis words selected by t).
The residual factor g_v depends only on r independent F2-linear
coordinates of t, where
  r = rank_F2( (other generator columns restricted to supp(v)) ).

Thus g_v has an EXACT representation as <=2^r Walsh characters,
whose full rational cyclotomic coefficient vectors can be computed
in O(poly(n,Q)*r*2^r) bit operations using a Walsh transform.
The coefficient at a Walsh character shifts the residual phase by
(Q/2)*linear_F2_character; no approximate complex arithmetic.

For the canonical E65 RREF bases, the first direction costs:
E123 R63 / SAT transpose: r=12 => 4096 exact nonzero terms.
E118 n90 SAT and UNSAT: r=2 => 4 exact nonzero terms.

This is a constructive general step, not a polynomial ALL-INPUT
procedure because r can be linear in n and recursive sums can grow.
"""
from __future__ import annotations

from r5_e64_connected_postquotient_nullity_firewall import tutte12_incidence
from r5_e65_transpose_asymmetry_quantized_defect import gf2_rref_basis
from r5_universal_boolean_quadratic_pc2_attack import (
    cyclic_source,e118_target,verify_target,source_solutions,
)


def matrix_basis(A):
    n=len(A)
    assert n and n%3==0
    assert all(len(row)==n and sum(row)==3 for row in A)
    assert all(sum(A[i][j] for i in range(n))==3 for j in range(n))
    _,_,basis=gf2_rref_basis(A)
    for row in A:
        mask=sum(v<<j for j,v in enumerate(row))
        assert all((mask&w).bit_count()%2==0 for w in basis)
    return basis


def q_parameter(n):
    Q=1
    while Q<=2*(n//3):
        Q*=2
    assert Q//2>n//3 and n%3==0
    return Q


def compressed_projection(basis, pivot_index):
    """All Boolean coordinate forms on supp(v) in independent row coordinates.

    Independent generators r_i are ORIGINAL row masks so h_i(t)=r_i dot t.
    For every support coordinate j, its linear form is an XOR of h_i
    with mask representation combo_j.
    """
    v=basis[pivot_index]
    other=[u for i,u in enumerate(basis) if i!=pivot_index]
    support=[j for j in range(v.bit_length()) if v>>j&1]
    raw_rows=[
        sum(((u>>j)&1)<<t for t,u in enumerate(other))
        for j in support
    ]
    pivot={}
    row_basis=[]
    combo=[]
    for row in raw_rows:
        x=row
        coeff=0
        while x:
            p=x.bit_length()-1
            if p not in pivot:
                new=len(row_basis)
                row_basis.append(row)
                pivot[p]=(x,coeff^(1<<new))
                coeff=1<<new
                break
            reduced,reduction=pivot[p]
            x^=reduced
            coeff^=reduction
        combo.append(coeff)

    # Independently reconstruct every support coordinate form.
    for row,expr in zip(raw_rows,combo):
        actual=0
        for i,form in enumerate(row_basis):
            if expr>>i&1:
                actual^=form
        assert actual==row
    return v,other,row_basis,combo


def phase_factor(Q,halfweight,overlap):
    """Integral coordinate vector of 1+zeta^(halfweight-overlap).

    Phi_Q(X)=X^(Q/2)+1. The output uses the canonical integral
    basis [1,zeta,...,zeta^(Q/2-1)].
    """
    D=Q//2
    z=(halfweight-overlap)%Q
    out=[0]*D
    out[0]+=1
    out[z%D]+=1 if z<D else -1
    return out


def walsh_inplace(vectors):
    N=len(vectors)
    stride=1
    while stride<N:
        block=2*stride
        for k in range(0,N,block):
            for i in range(k,k+stride):
                j=i+stride
                a=vectors[i]
                b=vectors[j]
                vectors[i]=[x+y for x,y in zip(a,b)]
                vectors[j]=[x-y for x,y in zip(a,b)]
        stride=block
    return vectors


def projected_walsh_phase_elimination(basis,n,pivot_index=0):
    Q=q_parameter(n)
    v,other,row_basis,combo=compressed_projection(basis,pivot_index)
    assert v.bit_count()%2==0
    r=len(row_basis)
    N=1<<r
    D=Q//2

    # Exact phase factor on all r-bit coordinate signatures.
    signature_values=[]
    for y in range(N):
        overlap=sum((y&expr).bit_count()%2 for expr in combo)
        signature_values.append(phase_factor(Q,v.bit_count()//2,overlap))

    spectrum=walsh_inplace([w[:] for w in signature_values])
    nonzero={
        s:tuple(coeff)
        for s,coeff in enumerate(spectrum)
        if any(coeff)
    }

    # Fully independent inverse transform exactness:
    # W(W(g)) = 2^r g, and W_s = sum_y (-1)^(s dot y) g(y).
    inverted=walsh_inplace([w[:] for w in spectrum])
    assert all(
        got==[N*v for v in expected]
        for got,expected in zip(inverted,signature_values)
    )

    # A Walsh index s means the original Boolean coefficient-space
    # character (-1)^sum_i(s_i*h_i(t)), the XOR row_basis forms.
    # Each such sign equals zeta^(Q/2)*linear_character mod Q.
    original_masks={}
    for s in nonzero:
        mask=0
        for i,w in enumerate(row_basis):
            if s>>i&1:
                mask^=w
        assert mask not in original_masks.values()
        original_masks[s]=mask

    assert len(nonzero)<=N
    return {
        "n":n,"d":len(basis),"pivot_weight":v.bit_count(),
        "Q":Q,"r":r,"total_signatures":N,
        "walsh_support":len(nonzero),"max_coordinate_bit_length":max(
            0,*[abs(x).bit_length() for row in spectrum for x in row]
        ),
        "coeffs":nonzero,"character_masks":original_masks,
    }


def e118_matrix(a,b):
    source=cyclic_source(9,a,b)
    rows,_,_=e118_target(source)
    verify_target(rows)
    n=len(rows)
    return [[int(j in row) for j in range(n)] for row in rows],source_solutions(source)


def main():
    R=tutte12_incidence()
    RT=[list(col) for col in zip(*R)]
    un90,un_models=e118_matrix(1,6)
    sat90,sat_models=e118_matrix(1,2)
    assert not un_models and sat_models
    fixtures=[
        ("E123_UNSAT63",R,12,4096),
        ("E65_SAT_TRANSPOSE63",RT,12,4096),
        ("E118_UNSAT90",un90,2,4),
        ("E118_SAT90",sat90,2,4),
    ]
    for name,A,expected_r,expected_support in fixtures:
        v=matrix_basis(A)
        p=projected_walsh_phase_elimination(v,len(A))
        assert p["r"]==expected_r,(name,p)
        assert p["walsh_support"]==expected_support,(name,p)
        assert p["total_signatures"]==1<<expected_r
        print(
            f"{name}: d={p['d']} pivot_wt={p['pivot_weight']}, "
            f"proj_rank={p['r']}, exact Walsh support "
            f"{p['walsh_support']}/{p['total_signatures']}, "
            f"Q={p['Q']}, integer coeffs max bits={p['max_coordinate_bit_length']}"
        )
    print("EXACT_PROJECTED_WALSH_ONE_STEP_ELIMINATION = PROVED_AND_REPLAYED")
    print("TOTAL_RECURSIVE_POLYNOMIAL_COMPLEXITY = UNPROVED")
    print("UNIVERSAL_POLYNOMIAL_EXACTONE_SOLVER = NOT_CONSTRUCTED")
    print("P_VS_NP = OPEN")


if __name__=="__main__":
    main()
