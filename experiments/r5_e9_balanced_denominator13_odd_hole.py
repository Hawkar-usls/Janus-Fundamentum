#!/usr/bin/env python3
"""Exact checks for balanced/odd-hole interaction frontier."""

from fractions import Fraction
from itertools import product, combinations
from math import prod

D1=((0,1),(2,3),(4,5),(6,7),(8,9),(10,11))
D2=((2,6,11),(1,8,10),(4,7,9),(0,3,5))
D3=((1,5,11),(2,9,10),(0,7,8),(3,4,6))

X=tuple(Fraction(v,13) for v in (7,6,3,10,4,9,12,1,5,8,2,11))

def det_int(M):
    # Bareiss exact determinant
    A=[list(map(int,row)) for row in M]
    n=len(A)
    sign=1
    prev=1
    for k in range(n-1):
        if A[k][k]==0:
            sw=next((i for i in range(k+1,n) if A[i][k]!=0),None)
            if sw is None:
                return 0
            A[k],A[sw]=A[sw],A[k]
            sign*=-1
        pivot=A[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                A[i][j]=(A[i][j]*pivot-A[i][k]*A[k][j])//prev
        prev=pivot
        for i in range(k+1,n):
            A[i][k]=0
    return sign*A[n-1][n-1]

def linear():
    rows=[set(e) for e in D1+D2+D3]
    return all(len(rows[i]&rows[j])<=1
               for i in range(len(rows))
               for j in range(i+1,len(rows)))

def feasible_bits(a):
    return (
        all(sum(a[i] for i in e)==1 for e in D1)
        and all(1<=sum(a[i] for i in e)<=2 for e in D2+D3)
    )

def fractional_checks():
    assert all(sum(X[i] for i in e)==1 for e in D1)
    assert [sum(X[i] for i in e) for e in D2]==[2,1,1,2]
    assert [sum(X[i] for i in e) for e in D3]==[2,1,1,2]

    # Independent active basis used in the receipt.
    active=[
        (D1[0],1),(D1[1],1),(D1[2],1),(D1[3],1),(D1[4],1),(D1[5],1),
        (D2[0],2),(D2[1],1),(D2[2],1),
        (D3[0],2),(D3[1],1),(D3[2],1),
    ]
    M=[]
    b=[]
    for e,rhs in active:
        row=[0]*12
        for v in e:
            row[v]=1
        M.append(row);b.append(rhs)

    assert det_int(M)==-13

    # Verify X is the unique solution of this nonsingular active system.
    for row,rhs in zip(M,b):
        assert sum(Fraction(a)*x for a,x in zip(row,X))==rhs

def no_integer_solution():
    return not any(feasible_bits(a) for a in product((0,1),repeat=12))

def nae(vals):
    return len(set(vals))>1

def odd_cycle_projection(edge_types,spokes):
    # edge_types is a tuple of 'P' or 'T', odd length.
    # spokes lists values in order of T edges.
    L=len(edge_types)
    ti=[None]*L
    k=0
    for i,t in enumerate(edge_types):
        if t=='T':
            ti[i]=spokes[k];k+=1
    for v in product((0,1),repeat=L):
        ok=True
        for i,t in enumerate(edge_types):
            a=v[i];b=v[(i+1)%L]
            if t=='P':
                ok &= (a!=b)
            else:
                ok &= nae((a,b,ti[i]))
            if not ok:break
        if ok:return True
    return False

def hole_projection_exhaustive():
    # Exhaust all odd cycle type strings up to length 9 and all spoke values.
    for L in (3,5,7,9):
        for types in product(('P','T'),repeat=L):
            if 'T' not in types:
                continue
            k=types.count('T')
            for s in product((0,1),repeat=k):
                assert odd_cycle_projection(types,s)

def explicit_hole():
    # rows D1[0]=(0,1), D2[1]=(1,8,10), D3[2]=(0,7,8)
    # on columns (0,1,8)
    M=((1,1,0),(0,1,1),(1,0,1))
    assert det_int(M)==2

def main():
    assert linear()
    fractional_checks()
    assert no_integer_solution()
    explicit_hole()
    hole_projection_exhaustive()
    print("LINEAR_THREE_PARTITION_INSTANCE = PASS")
    print("INTEGER_SOLUTIONS = 0")
    print("FRACTIONAL_VERTEX_DENOMINATOR = 13")
    print("ACTIVE_BASIS_DETERMINANT = -13")
    print("ODD_HOLE_BOUNDARY_PROJECTION = UNIVERSAL (exhaustive L<=9)")
    print("D1 = EMPTY")
    print("P_VS_NP = OPEN")

if __name__=="__main__":
    main()
