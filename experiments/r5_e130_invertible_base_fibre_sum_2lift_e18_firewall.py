#!/usr/bin/env python3
"""R5 E130: fibre-sum theorem replay on the frozen E129 q24 2-lift."""

from fractions import Fraction

from r5_e129_invertible_base_cover_unsat_gauge_clean_seed import (
    base_matrix, build_2lift, rank_q,
)

N0=12


def kernel_rows(M):
    A=[[Fraction(x) for x in row] for row in M]
    m=len(A); n=len(A[0])
    r=0; piv=[]
    for c in range(n):
        p=next((i for i in range(r,m) if A[i][c]),None)
        if p is None:
            continue
        A[r],A[p]=A[p],A[r]
        z=A[r][c]
        A[r]=[x/z for x in A[r]]
        for i in range(m):
            if i!=r and A[i][c]:
                f=A[i][c]
                A[i]=[A[i][j]-f*A[r][j] for j in range(n)]
        piv.append(c)
        r+=1

    free=[c for c in range(n) if c not in piv]
    basis=[]
    for f in free:
        x=[Fraction(0)]*n
        x[f]=1
        for i,c in enumerate(piv):
            x[c]=-A[i][f]
        basis.append(x)

    return [
        tuple(basis[k][i] for k in range(len(basis)))
        for i in range(n)
    ]


def main():
    A=base_matrix()
    assert rank_q(A)==N0

    L=build_2lift(A)
    assert rank_q(L)==22

    B=kernel_rows(L)
    assert len(B[0])==2

    zero_fibres=0
    minus_pairs=0

    for v in range(N0):
        b0=B[2*v]
        b1=B[2*v+1]
        assert all(b0[k]+b1[k]==0 for k in range(len(b0)))

        if all(x==0 for x in b0):
            assert all(x==0 for x in b1)
            zero_fibres+=1
        else:
            assert b1==tuple(-x for x in b0)
            minus_pairs+=1

    assert zero_fibres==3
    assert minus_pairs==9

    print("R5 E130 fibre-sum / 2-lift E18 firewall: PASS")
    print("base rank_Q=12 (invertible)")
    print("q24 lift rank_Q=22 nullity_Q=2")
    print("12/12 variable fibres satisfy b1=-b0")
    print("zero fibres=3; nonzero lambda=-1 fibre pairs=9")
    print("therefore E18/KLOC2 rejects the frozen q24 seed")
    print("higher-sheet cover route remains OPEN")
    print("P_VS_NP remains OPEN")


if __name__=="__main__":
    main()
