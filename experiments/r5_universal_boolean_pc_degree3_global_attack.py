#!/usr/bin/env python3
"""R5 attack on UNIVERSAL polynomial-time SCL via GF(2) polynomial calculus.

This is a rigorously sound exact linear-algebraic UNSAT certificate
candidate for *all* Boolean Exact-One systems:
  p_c = 1 + x_a + x_b + x_c
  q_c = x_a*x_b + x_a*x_c + x_b*x_c,
with x_i^2=x_i in the Boolean ring F2[x]/<x_i^2-x_i>.

At PC degree d, generate all monomial multiples m*p_c
for deg(m)<=d-1 and all m*q_c for deg(m)<=d-2, and
exactly Gaussian-eliminate them over GF(2) using bit-packed
integer polynomials. If 1 is in the span, UNSAT is proved:
we reconstruct the generator-combination certificate and
independently re-evaluate it to the constant polynomial 1.

If constant 1 is NOT spanned, return INCONCLUSIVE, NOT SAT.
For FIXED degree d, this is a polynomial time UNSAT test
O(n^{O(d)}) in all n x n SCL inputs, but NO universal fixed
degree completeness theorem is established.

Distinguishes stage d=2 from new tested d=3; avoids any SAT oracle.
No claim of P=NP or universal n^{O(1)} SAT decider.
"""
from __future__ import annotations

from itertools import combinations
from math import comb

from r5_universal_cubic_edgecolor_direct_scl_bridge import (
    K33,petersen_graph,make_scl,
)
from r5_universal_cubic_flow_snf_discriminator import normalized
from r5_universal_modular_flow_count_all_q_no_go import prism


def monomial_masks(n,d):
    assert 0<=d<=n
    mons=[0]
    for k in range(1,d+1):
        mons.extend(sum(1<<i for i in sub) for sub in combinations(range(n),k))
    assert len(mons)==sum(comb(n,k) for k in range(d+1))
    return mons


def poly_row(row,mon_mask,which,coordinate):
    """Squarefree multiplication in Boolean quotient, exact F2."""
    a,b,c=row
    if which=="parity":
        terms=(0,1<<a,1<<b,1<<c)
    elif which=="quadratic":
        terms=((1<<a)|(1<<b),(1<<a)|(1<<c),(1<<b)|(1<<c))
    else:
        raise ValueError(which)
    p=0
    for term in terms:
        p^=1<<coordinate[mon_mask|term]
    return p


def pc_refutation(rows,n,d,progress=False):
    """Returns (refuted, stats), with independently verified certificate."""
    mons=monomial_masks(n,d)
    coordinate={mon:i for i,mon in enumerate(mons)}
    p_mult=monomial_masks(n,d-1)
    q_mult=monomial_masks(n,d-2) if d>=2 else []
    basis={}
    generators=[]   # (clause_id,multiplier,kind); no polynomial cache
    rank=0
    for ci,row in enumerate(rows):
        assert len(row)==3 and len(set(row))==3
        for kind,ms in (("parity",p_mult),("quadratic",q_mult)):
            for mult in ms:
                idx=len(generators)
                generators.append((ci,mult,kind))
                vec=poly_row(row,mult,kind,coordinate)
                cert=1<<idx
                while vec:
                    pivot=vec.bit_length()-1
                    if pivot in basis:
                        old_vec,old_cert=basis[pivot]
                        vec^=old_vec
                        cert^=old_cert
                    else:
                        basis[pivot]=(vec,cert)
                        rank+=1
                        break
        if progress and (ci+1)%5==0:
            print(f'PC{d}_PROGRESS clauses={ci+1}/{len(rows)} '
                  f'rank={rank} generators={len(generators)}',
                  flush=True)

    # Query independent polynomial constant=1, not a generator.
    residual=1  # monomial index zero is 1
    cert=0
    while residual:
        pivot=residual.bit_length()-1
        if pivot not in basis:
            break
        old_vec,old_cert=basis[pivot]
        residual^=old_vec
        cert^=old_cert
    refuted=residual==0
    terms=0
    if refuted:
        total=0
        for j in range(len(generators)):
            if (cert>>j)&1:
                clause,mult,kind=generators[j]
                total^=poly_row(rows[clause],mult,kind,coordinate)
                terms+=1
        assert total==1,"UNSAT cert re-evaluation failed"
    return refuted,{
        "degree":d,
        "dimension":len(mons),
        "generators":len(generators),
        "rank":rank,
        "nullity":len(mons)-rank,
        "certificate_terms":terms,
        "independent_cert_verified":refuted,
    }


def main():
    n33,rows33,_,_=make_scl(K33())
    nP,rowsP,_,_=make_scl(petersen_graph())
    _,prism5=prism(5)
    n5,rows5,_,_=make_scl(prism5)
    assert n33==27 and n5==nP==45

    # Known independent decision results:
    # K3,3 12 colourings, prism5 30, Petersen 0.
    for name,n,rows,sat in [
        ("SAT_K33",n33,rows33,True),
        ("SAT_PRISM5",n5,rows5,True),
        ("UNSAT_PETERSEN",nP,rowsP,False),
    ]:
        assert n==len(rows)
        for d in (2,3):
            refuted,st=pc_refutation(rows,n,d,progress=(d==3))
            if sat:
                assert not refuted,("FALSE UNSAT on SAT input",name,d)
            print(f'{name}: PC_degree={d}, result='
                  f'{"PROVED_UNSAT" if refuted else "INCONCLUSIVE"}, '
                  f'stats={st}',flush=True)
        print(f'{name}: checked independent SAT ground truth={sat}',flush=True)

    print('ALL_INPUT_FIXED_DEGREE_GF2_PC_UNSAT_SOUND = PROVED')
    print('UNSAT_CERT_RECONSTRUCTION_VERIFIED = FINITE')
    print('POLY_SAT_DECISION_IF_UNREFUTED = NOT_JUSTIFIED')
    print('UNIFORM_FIXED_DEGREE_PC_COMPLETENESS = NOT_PROVED')
    print('UNIVERSAL_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED')
    print('P_VS_NP = OPEN')


if __name__=="__main__":
    main()
