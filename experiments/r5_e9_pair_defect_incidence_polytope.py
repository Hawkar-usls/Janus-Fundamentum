#!/usr/bin/env python3
"""Exact controls for the pair-defect incidence-polytope frontier."""

from fractions import Fraction
from itertools import combinations

D1=((8,10),(2,4),(6,7),(3,5),(0,1),(9,11))
D2=((2,5,10),(0,8,11),(4,6,9),(1,3,7))
D3=((3,6,10),(2,8,9),(1,5,11),(0,4,7))
NUM=(4,9,5,3,8,10,12,1,2,6,11,7)
DEN=13
N=12

def det_bareiss(A):
    A=[list(map(int,row)) for row in A]
    n=len(A)
    if n==0:
        return 1
    sign=1
    prev=1
    for k in range(n-1):
        if A[k][k]==0:
            q=next((i for i in range(k+1,n) if A[i][k]!=0),None)
            if q is None:
                return 0
            A[k],A[q]=A[q],A[k]
            sign*=-1
        pivot=A[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                A[i][j]=(A[i][j]*pivot-A[i][k]*A[k][j])//prev
        prev=pivot
        for i in range(k+1,n):
            A[i][k]=0
    return sign*A[-1][-1]

def row(scope):
    r=[0]*N
    for j in scope:
        r[j]=1
    return r

def linear_audit():
    parts=(D1,D2,D3)
    for a in range(3):
        for b in range(a+1,3):
            for r in parts[a]:
                for s in parts[b]:
                    assert len(set(r)&set(s))<=1

def fractional_vertex_audit():
    x=[Fraction(v,DEN) for v in NUM]
    assert all(sum(x[j] for j in r)==1 for r in D1)
    assert [sum(x[j] for j in r) for r in D2]==[2,1,2,1]
    assert [sum(x[j] for j in r) for r in D3]==[2,1,2,1]

    active=list(D1)+list(D2[:3])+list(D3[:3])
    A=[row(r) for r in active]
    assert len(A)==N
    assert det_bareiss(A)==13

def odd_cycle_audit():
    # D1[0]=(8,10), D2[0]=(2,5,10), D3[1]=(2,8,9)
    # on columns (2,8,10) this is the odd-cycle matrix.
    scopes=(D1[0],D2[0],D3[1])
    cols=(2,8,10)
    A=[[1 if c in s else 0 for c in cols] for s in scopes]
    assert A==[[0,1,1],[1,0,1],[1,1,0]]
    assert det_bareiss(A)==2

def half_center_audit():
    x=[Fraction(1,2)]*N
    assert all(sum(x[j] for j in r)==1 for r in D1)
    assert all(sum(x[j] for j in r)==Fraction(3,2) for r in D2+D3)

def main():
    linear_audit()
    half_center_audit()
    fractional_vertex_audit()
    odd_cycle_audit()
    print("LINEAR_3_DISJOINT_GEOMETRY = PASS")
    print("UNIVERSAL_HALF_CENTER = PASS")
    print("DENOMINATOR_13_VERTEX = PASS")
    print("ACTIVE_DETERMINANT = 13")
    print("LOCAL_STRONG_ODD_CYCLE_DETERMINANT = 2")
    print("HALF_INTEGRALITY = FALSE")
    print("D1 = EMPTY")
    print("P_VS_NP = OPEN")

if __name__=="__main__":
    main()
