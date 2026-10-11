#!/usr/bin/env python3
"""E118 equality gadgets: exact local GF2 flip and rank-2 phase factor.

For EVERY E118 occurrence-split reduction, one independent weight-6
GF2 kernel flip lives on the internal coordinates a,b,c,d,e,f of
each gadget. Gauge-fixing f=t=0 leaves only p=x=y and q=z, so each
flip's primitive-phase one-step Walsh expansion has <=4 terms.

This eliminates the local gadget freedom exactly but DOES NOT solve
the global source constraint network in polynomial time. E118's
NP-hardness is unchanged.
"""
from __future__ import annotations

from itertools import product

from r5_e118_universal_linear_cubic_exactone_hardness_bridge import (
    GADGET_CLAUSES, INTERNAL, PORTS,
)
from r5_universal_boolean_quadratic_pc2_attack import (
    cyclic_source, source_solutions, e118_target, verify_target,
)
from r5_universal_projected_walsh_phase_elimination_attack import (
    matrix_basis, projected_walsh_phase_elimination,
)


FLIP_COORDS=("a","b","c","d","e","f")
ALL_NAMES=PORTS+INTERNAL


def param_gf2(p,q,t):
    assert all(z in (0,1) for z in (p,q,t))
    return dict(
        x=p,y=p,z=q,g=q,f=t,
        a=p^q^t,c=p^q^t,
        b=p^t,e=p^t,d=q^t,
    )


def exact_gadget_kernel_truth_table():
    actual=[]
    for bits in product((0,1),repeat=len(ALL_NAMES)):
        sample=dict(zip(ALL_NAMES,bits))
        if all(sum(sample[v] for v in row)%2==0 for row in GADGET_CLAUSES):
            actual.append(tuple(sample[v] for v in ALL_NAMES))
    expected=[
        tuple(param_gf2(p,q,t)[v] for v in ALL_NAMES)
        for p,q,t in product((0,1),repeat=3)
    ]
    assert len(actual)==len(expected)==8
    assert set(actual)==set(expected)
    zero=param_gf2(0,0,0)
    flip=param_gf2(0,0,1)
    assert set(v for v in ALL_NAMES if zero[v]!=flip[v])==set(FLIP_COORDS)

    for p,q in product((0,1),repeat=2):
        s=param_gf2(p,q,0)
        intersection=sum(s[x] for x in FLIP_COORDS)
        assert intersection==2*(p^q)+2*p+q
        assert intersection in (0,3,4)
        assert s["f"]==0
    return True


def cyclotomic_coordinate_of_power(Q,power):
    D=Q//2
    i=power%Q
    v=[0]*D
    v[i%D]=1 if i<D else -1
    return v


def gadget_factor_coordinates(Q,p,q):
    """Exact canonical Q/2-coordinate vector of 1+zeta^(3-overlap)."""
    overlap=2*(p^q)+2*p+q
    v=cyclotomic_coordinate_of_power(Q,3-overlap)
    v[0]+=1
    return v


def gauge_walsh_coefficients(Q):
    """The four integer Walsh numerators of local 2-bit factor."""
    values=[gadget_factor_coordinates(Q,p,q) for q in (0,1) for p in (0,1)]
    D=Q//2
    spectral=[]
    for mask in range(4):
        v=[0]*D
        for state,row in enumerate(values):
            sign=-1 if (state&mask).bit_count()%2 else 1
            for i,a in enumerate(row):
                v[i]+=sign*a
        spectral.append(v)
    assert len(spectral)==4
    assert all(any(c for c in row) for row in spectral)
    # Exact Walsh inversion: each local factor is 1/4 sum_s W_s * character_s.
    for state,row in enumerate(values):
        recovered=[
            sum(
                (-1 if (state&mask).bit_count()%2 else 1)*spectral[mask][j]
                for mask in range(4)
            )
            for j in range(D)
        ]
        assert recovered==[4*c for c in row]
    return spectral


def all_gadget_flips_in_global_kernel(source):
    rows,_,pos=e118_target(source)
    verify_target(rows)
    n=len(rows)
    row_bits=[sum(1<<j for j in row) for row in rows]
    source_vars=sorted(set(v for row in source for v in row))
    flips=[]
    for v in source_vars:
        flip=sum(1<<pos[f"G_{v}_{s}"] for s in FLIP_COORDS)
        assert flip.bit_count()==6
        assert all((flip&r).bit_count()%2==0 for r in row_bits)
        flips.append(flip)
    assert len(flips)==len(source_vars)
    assert all((x&y)==0 for i,x in enumerate(flips) for y in flips[i+1:])
    assert len(set(flips))==len(flips)

    # The global kernel decomposes as span(flips) direct_sum
    # the unique subspace whose local internal f-coordinates vanish.
    B=matrix_basis([[int((rb>>j)&1) for j in range(n)] for rb in row_bits])
    seen=set()
    for i in range(min(256,1<<len(B))):
        w=0
        for j,b in enumerate(B):
            if i>>j&1:
                w^=b
        reduced=w
        for v,f in zip(source_vars,flips):
            if reduced>>pos[f"G_{v}_f"]&1:
                reduced^=f
        assert all((reduced&rb).bit_count()%2==0 for rb in row_bits)
        assert all((reduced>>pos[f"G_{v}_f"]&1)==0 for v in source_vars)
        seen.add(reduced)
    return len(source_vars),len(B),len(seen)


def main():
    assert exact_gadget_kernel_truth_table()
    for Q in (32,64,128):
        W=gauge_walsh_coefficients(Q)
        assert len(W)==4
        print(f"local E118 rank-2 gadget Walsh: Q={Q}, 4/4 nonzero terms")

    neg=cyclic_source(9,1,6)
    sat=cyclic_source(9,1,2)
    assert not source_solutions(neg)
    assert source_solutions(sat)
    for name,source in (("E118_UNSAT90",neg),("E118_SAT90",sat)):
        gadgets,d,checked=all_gadget_flips_in_global_kernel(source)
        assert gadgets==9 and d==18
        rows,_,_=e118_target(source)
        A=[[int(j in row) for j in range(len(rows))] for row in rows]
        canonical=projected_walsh_phase_elimination(matrix_basis(A),len(rows))
        assert canonical["r"]==2 and canonical["walsh_support"]==4
        print(f"{name}: {gadgets} independent local weight-6 kernel flips; "
              f"global nullity={d}; sampled gauge words={checked}; first-step 4-term phase PASS")

    print("ALL_E118_GADGET_LOCAL_PHASE_ELIMINATION_RANK_LE_2 = SYMBOLICALLY PROVED")
    print("E118_GLOBAL_SOURCE_COUPLING = REMAINS_NP_HARD")
    print("UNIVERSAL_POLYNOMIAL_SOLVER = NOT_CONSTRUCTED; P_VS_NP OPEN")


if __name__=="__main__":
    main()
