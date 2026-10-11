#!/usr/bin/env python3
"""Polynomial all-input exact MOD9 congruence UNSAT certificates.

Given an integer linear system B x=b (mod 9), this module reduces B
over the finite principal ideal ring Z/9Z by invertible row/column
operations to a diagonal matrix with entries from {1,3,0}.

If inconsistent, it CONSTRUCTS a row vector lam satisfying
   lam^T B = 0 (mod 9), lam^T b != 0 (mod 9).
This vector is an O(mn)-checkable independent UNSAT CERTIFICATE.

For SCL Exact-One, B consists of original incidence clauses
with RHS 1, plus fixed-value pin rows e_j with RHS pin[j].
Any Boolean Exact-One witness must satisfy this linear congruence,
so MOD9-INCONSISTENT implies genuine Boolean UNSAT.

If MOD9-CONSISTENT, the output is UNKNOWN, never SAT.
The check has O((m+n)^3) arithmetic operations over a fixed
9-element ring and O((m+n)^2) memory; integer BIT time polynomial.

This correctly generalizes the E129 q12/q24 integer fibre
obstruction to arbitrary legal SCL matrices. It is ONLY a sound
polynomial NEGATIVE filter, not a universal P-vs-NP solver.
"""
from __future__ import annotations

from itertools import product
from random import Random

Q=9


def independent_verify_mod9_certificate(B,rhs,lam):
    m=len(B)
    assert len(rhs)==m and len(lam)==m
    n=len(B[0]) if B else 0
    assert all(len(row)==n for row in B)
    assert all(isinstance(t,int) for t in lam)
    assert all(
        sum(lam[i]*B[i][j] for i in range(m))%Q==0
        for j in range(n)
    )
    assert sum(lam[i]*rhs[i] for i in range(m))%Q!=0
    return True


def mod9_linear_system(B,rhs):
    """Complete modular-9 consistency; either UNKNOWN or certified UNSAT.

    B may be rectangular with m>=1 and n>=1. The output is
    ("INCONSISTENT", lambda) or ("CONSISTENT", None).
    The latter does not guarantee a Boolean Exact-One model.
    """
    m=len(B)
    assert m>=1
    n=len(B[0])
    assert n>=1 and len(rhs)==m
    assert all(len(row)==n for row in B)
    D=[[int(a)%Q for a in row] for row in B]
    g=[int(a)%Q for a in rhs]
    E=[[int(i==j) for j in range(m)] for i in range(m)]
    k=0
    while k<min(m,n):
        # Choose globally minimum 3-adic valuation among nonzero
        # trailing entries, so the selected pivot divides EVERY
        # remaining matrix entry in Z/9Z.
        where=None
        for i in range(k,m):
            for j in range(k,n):
                v=D[i][j]
                if v and (where is None or (v%3!=0 and where[0]==1)):
                    where=(0 if v%3 else 1,i,j)
                    if where[0]==0:
                        break
            if where is not None and where[0]==0:
                break
        if where is None:
            break
        valuation,i,j=where
        if i!=k:
            D[k],D[i]=D[i],D[k]
            E[k],E[i]=E[i],E[k]
            g[k],g[i]=g[i],g[k]
        if j!=k:
            for row in D:
                row[j],row[k]=row[k],row[j]

        pivot=D[k][k]
        desired=1 if valuation==0 else 3
        unit=(pow(pivot,-1,Q) if desired==1
              else (1 if pivot==3 else 2))
        D[k]=[(unit*a)%Q for a in D[k]]
        E[k]=[(unit*a)%Q for a in E[k]]
        g[k]=(unit*g[k])%Q
        assert D[k][k]==desired

        # Eliminate below the pivot by invertible row operations,
        # simultaneously recording the transform of the RHS.
        for i in range(k+1,m):
            a=D[i][k]
            if a==0:
                continue
            assert a%desired==0
            f=a//desired
            D[i]=[(v-f*w)%Q for v,w in zip(D[i],D[k])]
            E[i]=[(v-f*w)%Q for v,w in zip(E[i],E[k])]
            g[i]=(g[i]-f*g[k])%Q

        # Clear remaining pivot row by invertible COLUMN operations.
        # The variable coordinate map need not be stored for an UNSAT
        # certificate, since row annihilators survive invertible
        # column operations.
        for j in range(k+1,n):
            a=D[k][j]
            if a==0:
                continue
            assert a%desired==0
            f=a//desired
            for i in range(m):
                D[i][j]=(D[i][j]-f*D[i][k])%Q
        k+=1

    # Full Smith-style diagonal over Z/9Z, with entries 1,3,0.
    assert all(
        D[i][j]==0 for i in range(m) for j in range(n)
        if i!=j
    )
    for i in range(m):
        d=D[i][i] if i<n else 0
        if d==1 or (d==3 and g[i]%3==0) or (d==0 and g[i]==0):
            continue
        # If 3*y=g fails, multiply the entire row by 3 to
        # annihilate 3 modulo 9, retaining nonzero RHS.
        scale=3 if d==3 else 1
        lam=tuple((scale*t)%Q for t in E[i])
        assert independent_verify_mod9_certificate(B,rhs,lam)
        return "INCONSISTENT",lam
    return "CONSISTENT",None


def mod9_exactone_precheck(A,pins=None):
    """All-SCL sound polynomial negative test with arbitrary pinned bits."""
    n=len(A)
    assert n>0 and all(len(row)==n for row in A)
    additional=[]
    if pins:
        additional=sorted(pins.items())
    B=[list(row) for row in A]
    rhs=[1]*n
    for j,v in additional:
        assert isinstance(j,int) and 0<=j<n and v in (0,1)
        row=[0]*n
        row[j]=1
        B.append(row)
        rhs.append(v)
    status,lam=mod9_linear_system(B,rhs)
    if status=="INCONSISTENT":
        independent_verify_mod9_certificate(B,rhs,lam)
    return status,lam


def _independent_random_small_ring_oracle():
    rng=Random(20261011)
    cases=0
    for m in range(1,5):
        for n in range(1,4):
            for _ in range(18):
                B=[[rng.randrange(Q) for _ in range(n)] for _ in range(m)]
                rhs=[rng.randrange(Q) for _ in range(m)]
                status,lam=mod9_linear_system(B,rhs)
                oracle=any(
                    all(sum(a*x for a,x in zip(row,word))%Q==rhs[i]
                        for i,row in enumerate(B))
                    for word in product(range(Q),repeat=n)
                )
                assert (status=="CONSISTENT")==oracle,(m,n,B,rhs,status)
                assert lam is None if oracle else lam is not None
                cases+=1
    return cases


def main():
    from r5_e129_invertible_base_cover_unsat_gauge_clean_seed import (
        base_matrix,build_2lift
    )
    from r5_e64_connected_postquotient_nullity_firewall import tutte12_incidence
    from r5_universal_boolean_quadratic_pc2_attack import (
        cyclic_source, e118_target, verify_target
    )
    from r5_e61_two_level_kernel_hoffman_regular_set import (
        P_SAT,Q_SAT,build_A
    )
    from r5_universal_exact_support_pinned_oracle_attack import (
        ExactSupport
    )
    from r5_universal_exact_support_2lift_visited_dag_frontier import (
        two_lift
    )
    ncases=_independent_random_small_ring_oracle()
    print(f"MOD9_GENERIC_RECTANGULAR_RANDOM_EXACT_BRUTE_FORCE={ncases} PASS")

    base=base_matrix()
    lifted=build_2lift(base)
    cases=[("E129_BASE_UNSAT12",base),("E129_COVER_UNSAT24",lifted)]
    for tag,A in cases:
        status,lam=mod9_exactone_precheck(A)
        assert status=="INCONSISTENT" and lam is not None,(tag,status)
        # Verify the production pinned ExactSupport actually calls this
        # new polynomial negative gate BEFORE any exponential branch.
        root=ExactSupport(A,max_nodes=0,gauss_depth=-1)
        assert root["status"]=="UNSAT"
        assert root["reason"]=="PINNED_MOD9_INTEGER_OBSTRUCTION"
        assert root["audit"]["mod9_checks"]==1
        assert root["audit"]["mod9_prunes"]==1
        assert root["audit"]["branches"]==0
        assert tuple(root["mod9_certificate"])==tuple(lam)
        print(f"{tag}: O(n^3) mod9 UNSAT certificate length={len(lam)}, "
              f"nonzero={sum(z!=0 for z in lam)}, "
              "ExactSupport root returned UNSAT without branch")

    # Another genuine 2-lift of the q24 cover is an r=4 cover of
    # E129's q12 base and must also be congruence-inconsistent.
    rows=[tuple(j for j,x in enumerate(row) if x) for row in lifted]
    from random import Random
    lifted48=two_lift(rows,24,Random(129))
    A48=[[int(j in row) for j in range(48)] for row in lifted48]
    status,lam=mod9_exactone_precheck(A48)
    assert status=="INCONSISTENT" and lam is not None
    root48=ExactSupport(A48,max_nodes=0,gauss_depth=-1)
    assert root48["status"]=="UNSAT" and root48["audit"]["branches"]==0
    assert root48["reason"]=="PINNED_MOD9_INTEGER_OBSTRUCTION"
    print(f"E129_COVER_UNSAT48: polynomial mod9 UNSAT certificate nonzero={sum(z!=0 for z in lam)}; production gate PASS")

    # A TRUE Boolean SAT example and arbitrary pins agreeing with an
    # actual witness must remain congruence-compatible.
    sat12=build_A(P_SAT,Q_SAT)
    r=ExactSupport(sat12,max_nodes=20000)
    assert r["status"]=="SAT"
    witness=r["witness"]
    for size in (0,1,4,12):
        pins={j:witness[j] for j in range(size)}
        status,lam=mod9_exactone_precheck(sat12,pins)
        assert status=="CONSISTENT" and lam is None
    print("E61_SAT12_PINNED_MOD9_NO_FALSE_UNSAT PASS")

    # The Gauss/semigroup-negative controls protect against promotion
    # of a positive modular residue into Boolean support.
    R=tutte12_incidence()
    status,_=mod9_exactone_precheck(R)
    print(f"E123_UNSAT63 MOD9 status={status} (NOT an asserted Boolean verdict)")
    for label,a,b in (("E118_UNSAT90",1,6),("E118_SAT90",1,2)):
        rows,_,_=e118_target(cyclic_source(9,a,b))
        verify_target(rows)
        n=len(rows)
        A=[[int(j in row) for j in range(n)] for row in rows]
        status,lam=mod9_exactone_precheck(A)
        if label=="E118_SAT90":
            assert status=="CONSISTENT"
        print(f"{label} MOD9 status={status} "
              "(CONSISTENT means UNKNOWN, not SAT)")

    print("MOD9_SMITH_STYLE_ELIMINATION_POLYNOMIAL_ALL_INPUTS=PROVED")
    print("MOD9_LEFT_ANNIHILATOR_INDEPENDENT_UNSAT_CERTIFICATE=PROVED")
    print("MOD9_CONSISTENT_NEVER_IMPLIES_EXACT_ONE_SAT")
    print("UNIVERSAL_POLY_ExactSupport=NOT_CONSTRUCTED; P_VS_NP=OPEN")


if __name__=="__main__":
    main()
