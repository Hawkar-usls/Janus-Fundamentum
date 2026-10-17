#!/usr/bin/env python3
"""R5 E130 probe: mod-p consistency of full E127 signed affine quotients."""

from collections import Counter

from r5_e64_connected_postquotient_nullity_firewall import tutte12_incidence
from r5_e127_tutte12_affine_support_nullity_descent import (
    affine_closure,
    signed_matrix,
)

PRIMES=(2,3,5,7,11,13,17,19,23,29,31)


def rank_mod(M,p):
    A=[[x%p for x in row] for row in M]
    if not A:
        return 0
    m=len(A); n=len(A[0])
    r=0
    for c in range(n):
        q=next((i for i in range(r,m) if A[i][c]),None)
        if q is None:
            continue
        A[r],A[q]=A[q],A[r]
        inv=pow(A[r][c],-1,p)
        A[r]=[(x*inv)%p for x in A[r]]
        for i in range(m):
            if i!=r and A[i][c]:
                f=A[i][c]
                A[i]=[(a-f*b)%p for a,b in zip(A[i],A[r])]
        r+=1
        if r==m:
            break
    return r


def orientation_profile(A):
    n=len(A)
    clauses=[[j for j,v in enumerate(A[i]) if v] for i in range(n)]
    incon=Counter()
    rankpairs={p:Counter() for p in PRIMES}
    branch_count=0

    for c,vs in enumerate(clauses):
        for chosen in vs:
            branch_count+=1
            initial={j:(1 if j==chosen else 0) for j in vs}
            out=affine_closure(clauses,n,initial)
            assert out is not None
            vals,unknown,comps,parity,compid,qtern=out
            M,rhs=signed_matrix(comps,qtern)
            aug=[row+[rhs[i]] for i,row in enumerate(M)]
            for p in PRIMES:
                r=rank_mod(M,p)
                ra=rank_mod(aug,p)
                rankpairs[p][(r,ra)]+=1
                if ra!=r:
                    incon[p]+=1
    assert branch_count==189
    return incon,rankpairs


def main():
    R=tutte12_incidence()
    RT=[list(row) for row in zip(*R)]

    for name,A in (("R_UNSAT",R),("RT_SAT",RT)):
        incon,rankpairs=orientation_profile(A)
        print(name)
        for p in PRIMES:
            print(
                f"  p={p}: inconsistent={incon[p]}/189 "
                f"rankpairs={dict(rankpairs[p])}"
            )

    print("E130 affine quotient mod-p support probe COMPLETE")
    print("No theorem claim is implied by a finite prime list.")
    print("P_VS_NP remains OPEN")


if __name__=="__main__":
    main()
