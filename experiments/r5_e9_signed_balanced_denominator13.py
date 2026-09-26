#!/usr/bin/env python3
"""Exact checks for the signed-balanced quotient hard micro-core."""

from fractions import Fraction
from itertools import product

A=(
 (0,1,0,1,0,-1),
 (-1,0,0,0,1,1),
 (0,0,1,-1,-1,0),
 (1,-1,-1,0,0,0),
 (-1,0,-1,0,0,-1),
 (0,1,0,0,-1,1),
 (1,0,0,-1,1,0),
 (0,-1,1,1,0,0),
)

R=tuple(Fraction(v,13) for v in (7,3,4,12,5,2))

def det_int(M):
    B=[list(map(int,row)) for row in M]
    n=len(B);sign=1;prev=1
    for k in range(n-1):
        if B[k][k]==0:
            sw=next((i for i in range(k+1,n) if B[i][k]!=0),None)
            if sw is None:return 0
            B[k],B[sw]=B[sw],B[k];sign*=-1
        p=B[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                B[i][j]=(B[i][j]*p-B[i][k]*B[k][j])//prev
        prev=p
        for i in range(k+1,n):B[i][k]=0
    return sign*B[-1][-1]

def bounds(row):
    neg=sum(1 for a in row if a==-1)
    pos=sum(1 for a in row if a==1)
    return 1-neg,pos-1

def signed_nae_ok(bits,row):
    vals=[]
    for x,a in zip(bits,row):
        if a==1:vals.append(x)
        elif a==-1:vals.append(1-x)
    return len(set(vals))>1

def no_boolean_model():
    return not any(
        all(signed_nae_ok(x,row) for row in A)
        for x in product((0,1),repeat=6)
    )

def fractional_vertex():
    tight=[]
    for i,row in enumerate(A):
        v=sum(Fraction(a)*x for a,x in zip(row,R))
        lo,hi=bounds(row)
        assert lo <= v <= hi
        assert v in (lo,hi)
        tight.append((i,v))

    # Independent active rows 0,1,2,4,5,6.
    M=[A[i] for i in (0,1,2,4,5,6)]
    assert det_int(M)==13

def local_signed_hole():
    H=((1,-1),(1,1))
    assert det_int(H)==2
    assert sum(sum(r) for r in H)%4==2

    # NAE(x,not y,u) & NAE(x,y,v) projects universally to (u,v).
    for u,v in product((0,1),repeat=2):
        ok=False
        for x,y in product((0,1),repeat=2):
            c1=len({x,1-y,u})>1
            c2=len({x,y,v})>1
            if c1 and c2:
                ok=True;break
        assert ok

def main():
    assert no_boolean_model()
    fractional_vertex()
    local_signed_hole()
    print("SIGNED_NAE_BOOLEAN_MODELS = 0")
    print("SIGNED_FRACTIONAL_VERTEX_DENOMINATOR = 13")
    print("ACTIVE_SIGNED_BASIS_DETERMINANT = 13")
    print("MIN_SIGNED_HOLE_BOUNDARY_PROJECTION = UNIVERSAL")
    print("D1 = EMPTY")
    print("P_VS_NP = OPEN")

if __name__=="__main__":
    main()
