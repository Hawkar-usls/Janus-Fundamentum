#!/usr/bin/env python3
"""Exact sanity for R5 E10 local OR3 -> COPY3 gauge identity."""

from fractions import Fraction
from itertools import product

def mat_vec(M,v):
    return tuple(sum(M[i][j]*v[j] for j in range(2)) for i in range(2))

def tensor3(v,w,z):
    return {(i,j,k):v[i]*w[j]*z[k] for i,j,k in product(range(2), repeat=3)}

def add(X,Y,scale=1):
    out=dict(X)
    for key,val in Y.items():
        out[key]=out.get(key,0)+scale*val
    return out

def transform(T1,T2,T3,X):
    out={}
    for a,b,c in product(range(2), repeat=3):
        s=0
        for i,j,k in product(range(2), repeat=3):
            s += T1[a][i]*T2[b][j]*T3[c][k]*X[i,j,k]
        out[a,b,c]=s
    return out

def main():
    u=(1,1); e0=(1,0); e1=(0,1)
    A=((0,1),(1,-1))
    D=((1,0),(0,-1))
    DA=tuple(tuple(sum(D[i][r]*A[r][j] for r in range(2)) for j in range(2)) for i in range(2))

    OR=add(tensor3(u,u,u),tensor3(e0,e0,e0),scale=-1)
    COPY=add(tensor3(e0,e0,e0),tensor3(e1,e1,e1))

    assert transform(DA,A,A,OR)==COPY
    assert mat_vec(A,u)==e0
    assert mat_vec(A,e0)==e1

    # Verify OR truth table explicitly.
    for i,j,k in product(range(2), repeat=3):
        assert OR[i,j,k] == int(bool(i or j or k))

    print("R5 E10 OR3 -> COPY3 exact gauge identity: PASS")

if __name__=="__main__":
    main()
