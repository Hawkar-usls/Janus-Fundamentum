#!/usr/bin/env python3
"""Primitive cyclotomic phase: basis-INDEPENDENT obstruction to one-phase elimination.

A sum over binary kernel coordinate v at a primitive Q-th root zeta is
    F_v(u)=zeta^(wt(u)/2) * (1 + zeta^Delta_v(u))
    Delta_v(u) = wt(v)/2 - wt(u & v).
To replace F_v by C*zeta^P(u), a NECESSARY condition is
that |1+zeta^Delta_v(u)| be constant on the complementary subspace.

Since |1+zeta^a|^2=2+2*cos(2*pi*a/Q), equal magnitudes are equivalent to
a == +/- b (mod Q). Also Delta_v(u+v)=-Delta_v(u). Therefore,
if ANY kernel word u not in {0,v} violates this congruence relative to
Delta_v(0), then it violates it in EVERY complementary subspace
K=<v> direct_sum L; either u or u+v lies in L and their cosines agree.

An independent F2 basis is a sufficient set of candidates for finding
such a word, so we test every nonzero v against all other basis words.

All 2^d-1 directions are enumerated on FROZEN finite controls only.
This is a rigorous rejection of the SINGLE-PHASE CLOSURE ANSATZ,
NOT a lower bound against general polynomial algorithms, and
NOT itself a universal polynomial solver.
"""
from __future__ import annotations

from r5_e64_connected_postquotient_nullity_firewall import tutte12_incidence
from r5_e65_transpose_asymmetry_quantized_defect import gf2_rref_basis
from r5_universal_boolean_quadratic_pc2_attack import (
    cyclic_source, e118_target, verify_target, source_solutions,
)


def basis_from_matrix(A):
    n=len(A)
    assert n%3==0
    assert all(len(row)==n and sum(row)==3 for row in A)
    assert all(sum(A[i][j] for i in range(n))==3 for j in range(n))
    _,_,basis=gf2_rref_basis(A)
    rows=[sum(v<<j for j,v in enumerate(row)) for row in A]
    assert all(all((w&r).bit_count()%2==0 for r in rows) for w in basis)
    return basis


def target_from_q9(offsets):
    source=cyclic_source(9,*offsets)
    source_models=source_solutions(source)
    rows,_,_=e118_target(source)
    verify_target(rows)
    n=len(rows)
    assert n==90
    return [[int(j in row) for j in range(n)] for row in rows],source_models


def q_for_n(n):
    assert n%3==0
    Q=1
    while Q<=2*(n//3):
        Q*=2
    assert Q>2*(n//3) and Q<=4*(n//3)
    return Q


def direct_sum_obstruction_profile(basis,n):
    """Every nonzero direction v tested against ALL basis words u!=v.

    The proof that a witness u obstructs every choice of complement
    uses Delta_v(u+v)=-Delta_v(u). No basis-dependence in the verdict:
    the exhaustive list of ALL directions covers every possible basis
    first step. Only the certificate's chosen u comes from one basis.
    """
    Q=q_for_n(n)
    d=len(basis)
    assert 0<d<=18 # frozen fixture only; NOT universal complexity limit
    words=[0]*(1<<d)
    for t in range(1,1<<d):
        low=t&-t
        words[t]=words[t^low]^basis[low.bit_length()-1]
    assert len(set(words))==1<<d
    obstructions=[]
    all_min=100000
    minimal_directions=[]
    obstruction_witnesses=[]
    for coeff in range(1,len(words)):
        v=words[coeff]
        assert v.bit_count()%2==0
        a=v.bit_count()//2
        bad=[]
        for j,u in enumerate(basis):
            if u==v:
                continue
            # Exact test for different moduli of the eliminated
            # factor at u=0 and u or (u+v) in any complement L.
            intersection=(v&u).bit_count()
            delta=(a-intersection)%Q
            if delta not in (a%Q,(-a)%Q):
                # Independently reconstruct Delta from Hamming weights.
                assert delta==( (v^u).bit_count()-u.bit_count() )//2%Q
                bad.append(j)
        if not bad:
            minimal_directions.append(coeff)
        else:
            obstruction_witnesses.append((coeff,bad[0]))
        if len(bad)<all_min:
            all_min=len(bad)
        obstructions.append(len(bad))
    return {
        "Q":Q,"d":d,"directions":len(words)-1,
        "min_bad_basis_witnesses":all_min,
        "nonconstant_directions":sum(v>0 for v in obstructions),
        "possible_single_phase_directions":minimal_directions,
        "sample_certificate":obstruction_witnesses[0] if obstruction_witnesses else None,
    }


def main():
    R=tutte12_incidence()
    RT=[list(col) for col in zip(*R)]
    neg90,neg_models=target_from_q9((1,6))
    pos90,pos_models=target_from_q9((1,2))
    assert not neg_models and pos_models
    controls=[
        ("E123_UNSAT_R63",R,14,13),
        ("E65_SAT_RT63",RT,14,13),
        ("E118_UNSAT90",neg90,18,2),
        ("E118_SAT90",pos90,18,2),
    ]
    for name,A,dim,minimum in controls:
        basis=basis_from_matrix(A)
        p=direct_sum_obstruction_profile(basis,len(A))
        assert p["d"]==dim
        assert p["min_bad_basis_witnesses"]==minimum,(name,p)
        assert p["possible_single_phase_directions"]==[],(name,p)
        assert p["nonconstant_directions"]==(1<<dim)-1
        print(name,p)

    print("ONE_PHASE_SCALAR_CLOSURE = REFUTED ON FOUR EXACT SCL FIXTURES")
    print("EVERY FIRST KERNEL DIRECTION, EVERY COMPLEMENT, EVERY BASIS = OBSTRUCTED")
    print("THIS DOES NOT EXCLUDE SUM-OF-PHASES/TENSOR/SYMBOLIC REPRESENTATIONS")
    print("NO UNIVERSAL POLYNOMIAL PHASE EVALUATOR; P_VS_NP OPEN")


if __name__=="__main__":
    main()
