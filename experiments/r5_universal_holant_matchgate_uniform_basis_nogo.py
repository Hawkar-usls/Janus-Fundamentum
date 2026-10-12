#!/usr/bin/env python3
"""R5 ALL-SCL Holant equality/exact-one tensor and uniform-matchgate NO-GO.

Universal EXACT representation: for every original square/linear/cubic
positive Exact-One source, write one ternary ExactOne signature W on
each original clause row and one ternary Equality signature GHZ on
each original variable. Contract Tanner incidence wires to recover
the exact number of original 0/1 SAT witnesses. This representation
is source-preserving, but no polynomial-time universal contraction
algorithm is implied.

Strict uniform-basis impossibility (over any characteristic-zero field):
there is NO B in GL_2 such that applying B^{tensor 3} to the EXACTONE3
signature and (B^{-T})^{tensor 3} to EQUALITY3 makes BOTH signatures
pure even- or odd-parity. Pure parity is NECESSARY for any ordinary
matchgate signature, thus the most direct one-global-basis
Pfaffian/Valiant holographic reduction cannot handle this gate pair.

Proof is elementary coefficient elimination (not a numerical guess).
Write B=[[a,b],[c,d]], det(B)=ad-bc !=0. Let F=EXACTONE3
with 1 on assignments of Hamming weight 1. Its transformed
symmetric weight-vector is
    F'=[3a^2 b, a^2 d+2abc, 2acd+bc^2, 3c^2 d].
If F' is odd, f0=f2=0; a=0 would force bc!=0 and f2=bc^2!=0.
Thus a!=0 and b=0. Then det=ad!=0, and f2=2acd forces c=0.
B is diagonal.
If F' is even, f1=f3=0; d=0 forces bc!=0, and then
f1=2abc=0 implies a=0; if instead c=0, det=ad!=0
and f1=a^2 d!=0, contradiction. Thus d=a=0 and
B is antidiagonal.
For BOTH diagonal and antidiagonal B, the opposite dual change
(B^-T) applied to EQUALITY3 leaves two nonzero components,
at Hamming weights 0 and 3, violating both parity possibilities.

This prohibits ONE common homogeneous GL2 gauge with inverse-dual
on Tanner edges. It does not rule out nonuniform/local gauges,
higher-dimensional gadgets, non-matchgate signatures, cancellations,
nonplanar Pfaffians, or other universal algorithms. P vs NP OPEN.
"""
from __future__ import annotations

from itertools import product

from r5_universal_exact_support_residual_dag_attack import validate_sparse

W=(0,1,0,0)
GHZ=(1,0,0,1)


def parity_type(signature):
    assert len(signature)==4
    even=signature[1]==0 and signature[3]==0
    odd=signature[0]==0 and signature[2]==0
    if even and odd:
        return "ZERO"
    if even:
        return "EVEN"
    if odd:
        return "ODD"
    return "MIXED"


def transform_symmetric_ternary(signature, B):
    """Independent 8-state tensor contraction, integer or rational basis."""
    assert len(signature)==4 and len(B)==2 and all(len(row)==2 for row in B)
    by_weight=[]
    for w in range(4):
        target=(0,)*(3-w)+(1,)*w
        value=0
        for old in product((0,1),repeat=3):
            prod=signature[sum(old)]
            for i in range(3):
                prod*=B[target[i]][old[i]]
            value+=prod
        by_weight.append(value)
    return tuple(by_weight)


def transformed_exactone_coefficients(B):
    (a,b),(c,d)=B
    return (3*a*a*b, a*a*d+2*a*b*c, 2*a*c*d+b*c*c, 3*c*c*d)


def matrix_inverse_transpose(B):
    from fractions import Fraction
    (a,b),(c,d)=B
    det=a*d-b*c
    assert det!=0
    return ((Fraction(d,det),Fraction(-c,det)),
            (Fraction(-b,det),Fraction(a,det)))


def verify_parity_obstruction_on_basis(B):
    (a,b),(c,d)=B
    if a*d-b*c==0:
        return "SINGULAR"
    f=transform_symmetric_ternary(W,B)
    assert f==transformed_exactone_coefficients(B)
    kind=parity_type(f)
    if kind=="EVEN":
        assert a==0 and d==0,("contradicts proved coefficient lemma",B,f)
    if kind=="ODD":
        assert b==0 and c==0,("contradicts proved coefficient lemma",B,f)
    h=transform_symmetric_ternary(GHZ,matrix_inverse_transpose(B))
    if kind in ("EVEN","ODD"):
        assert h[0]!=0 and h[3]!=0 and h[1]==0 and h[2]==0
        assert parity_type(h)=="MIXED"
    return kind


def verify_symbolic_nogo_lemmas():
    """Algebraic proof rules independently mirrored in finite examples.

    The following is a small symbolic CASE PROOF, valid over
    characteristic zero and with det !=0, rather than relying on the
    finite sampled bases to infer a global result.
    (1) odd F': f0=3a^2b=0. If a=0, det=-bc!=0,
        and f2=bc^2!=0. Thus a!=0,b=0,det=ad!=0.
        f2=2acd=0 then c=0.
    (2) even F': f3=3c^2d=0. If c=0, det=ad!=0
        and f1=a^2d!=0. Thus d=0,det=-bc!=0.
        f1=2abc=0 then a=0.
    (3) diagonal or antidiagonal B and its inverse transpose
        are both monomial matrices. EQUALITY3 transforms to
        nonzero coefficients on weights 0 AND 3; cannot be pure
        matchgate parity. This establishes NO-GO over ALL GL2,
        not merely integer sample points.
    """
    # independent coefficient expansion for general integer matrices
    seen_even=seen_odd=seen_mixed=0
    for a,b,c,d in product(range(-2,3),repeat=4):
        B=((a,b),(c,d))
        kind=verify_parity_obstruction_on_basis(B)
        if kind=="EVEN":seen_even+=1
        elif kind=="ODD":seen_odd+=1
        elif kind=="MIXED":seen_mixed+=1
    assert (seen_even,seen_odd)==(16,16)
    assert seen_mixed>0
    # A nonmonomial invertible B can transform GHZ, but W then
    # necessarily violates parity. Hadamard is the key control.
    assert verify_parity_obstruction_on_basis(((1,1),(1,-1)))=="MIXED"
    assert verify_parity_obstruction_on_basis(((1,0),(0,1)))=="ODD"
    assert verify_parity_obstruction_on_basis(((0,1),(1,0)))=="EVEN"
    return True


def verify_original_holant_representation(rows,n,enumerate_sat=False):
    """Prove original tensor reconstruction with optional tiny controls.

    The source Tanner graph is a cubic bipartite incidence graph:
    rows degree 3; columns degree 3. A configuration on each wire
    satisfying GHZ at column nodes is a unique Boolean source
    assignment, and W on row nodes is exactly its Exact-One clauses.
    Thus every nonzero tensor configuration has value 1 and is in
    bijection with original SAT witnesses. No cancellations occur in
    this UNTAMPERED original basis.

    The optional exact counter enumerates 2^n assignments and is
    consciously NOT a polynomial all-input algorithm.
    """
    rows=validate_sparse(rows,n)
    assert len(rows)==n
    degree=[0]*n
    for row in rows:
        assert len(row)==3
        for v in row:
            degree[v]+=1
    assert all(v==3 for v in degree)
    assert 3*len(rows)==3*n
    result={
        "signature_row":"ExactOne3/W",
        "signature_variable":"Equality3/GHZ",
        "row_tensors":n,
        "variable_tensors":n,
        "tanner_wires":3*n,
        "source_bijection":"EXACT_BY_EQUALITY_WIRES",
    }
    if enumerate_sat:
        assert n<=18,"exponential finite control forbidden above n=18"
        masks=[sum(1<<v for v in row) for row in rows]
        count=sum(all((a&mask).bit_count()==1 for mask in masks)
                  for a in range(1<<n))
        result["original_sat_count"]=count
    return result


def main():
    from r5_universal_cubic_edgecolor_direct_scl_bridge import (
        K4,K33,make_scl,
    )
    from r5_universal_all_odd_cyclic_pc2_four_orbit_identity import cyclic
    assert verify_symbolic_nogo_lemmas()
    print("EXACTONE3_HOLOGRAPHIC_PARITY_ODD_IMPLIES_DIAGONAL_B=PROVED")
    print("EXACTONE3_HOLOGRAPHIC_PARITY_EVEN_IMPLIES_ANTIDIAGONAL_B=PROVED")
    print("EQUALITY3_INVERSE_DUAL_PARITY_CONFLICT=PROVED")
    print("UNIFORM_GL2_SIMULTANEOUS_MATCHGATE_TRANSFORM=IMPOSSIBLE")

    # Always authenticate the ORIGINAL source, not a generic 3-CSP.
    for name,rows,n,truth in (
        ("FANO7",cyclic(7),7,0),
        ("K4_SCL18",*make_scl(K4())[:2],6),
        ("K33_SCL27",*make_scl(K33())[:2],None),
    ):
        r=verify_original_holant_representation(
            rows,n,enumerate_sat=(n<=18)
        )
        if truth is not None:
            assert r["original_sat_count"]==truth,(name,r)
        print(f"HOLANT_ALL_ORIGINAL_{name}=EXACT_TENSORS "
              f"wires={r['tanner_wires']} sat_count={r.get('original_sat_count','NOT_ENUMERATED')}",
              flush=True)

    # A forged noncubic source must not receive the all-SCL certificate.
    valid,n,_,_=make_scl(K4())
    tampered=list(valid)
    tampered[0]=(0,1,2)
    if tuple(tampered[0])==tuple(valid[0]):
        tampered[0]=(0,1,3)
    try:
        verify_original_holant_representation(tampered,n)
    except (AssertionError,ValueError):
        print("FORGED_SOURCE_HOLANT_CERTIFICATE_REJECTED=PASS",flush=True)
    else:
        raise AssertionError("forged source accepted")

    print("ALL_SCL_W_AND_EQUALITY_HOLANT_EXACT_REPRESENTATION=PROVED")
    print("ALL_SCL_GLOBAL_UNIFORM_BASIS_MATCHGATE_ANSATZ=REFUTED")
    print("ARBITRARY_LOCAL_GAUGES_AND_NONMATCHGATE_COMPRESSION=OPEN")
    print("UNIVERSAL_POLY_SOLVELINEARCUBICXSAT=NOT_CONSTRUCTED")
    print("P_VS_NP=OPEN")


if __name__=="__main__":
    main()
