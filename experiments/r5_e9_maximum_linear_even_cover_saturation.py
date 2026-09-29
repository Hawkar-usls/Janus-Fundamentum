#!/usr/bin/env python3
"""Finite regression for maximum linear even-cover saturation theorem."""
from itertools import product
import json


def incidence(n,blocks):
    A=[[0]*n for _ in blocks]
    for r,b in enumerate(blocks):
        for j in b: A[r][j]=1
    return A


def mv(A,x):
    return [sum(a*b for a,b in zip(row,x)) for row in A]


def kernel(A):
    n=len(A[0])
    return [z for z in product((0,1),repeat=n) if all(v%2==0 for v in mv(A,z))]


def replay(name,A,expected_models):
    n=len(A)
    assert len(A)==len(A[0])
    assert all(sum(r)==3 for r in A)
    assert all(sum(A[r][c] for r in range(n))==3 for c in range(n))
    supp=[{j for j,v in enumerate(row) if v} for row in A]
    assert all(len(supp[i]&supp[j])<=1 for i in range(n) for j in range(i))

    C=kernel(A)
    models=[]
    maxw=0
    for z in C:
        rowdeg=mv(A,z)
        assert all(v in (0,2) for v in rowdeg)
        active=sum(v==2 for v in rowdeg)
        assert 3*sum(z)==2*active
        assert 3*sum(z)<=2*n
        if n%3==0:
            assert active%3==0
            assert (2*n//3-sum(z))%2==0
        maxw=max(maxw,sum(z))
        x=tuple(1-b for b in z)
        if mv(A,x)==[1]*n:
            models.append(x)
            assert 3*sum(z)==2*n
        if 3*sum(z)==2*n:
            assert mv(A,x)==[1]*n

    models=sorted(set(models))
    assert len(models)==expected_models
    sat=expected_models>0
    assert sat == (3*maxw==2*n)
    return {"name":name,"n":n,"kernel_size":len(C),"max_kernel_weight":maxw,
            "exact_models":len(models),"saturation":3*maxw==2*n}


def main():
    fano=[(0,1,2),(0,3,4),(0,5,6),(1,3,5),(1,4,6),(2,3,6),(2,4,5)]
    affine=[]
    for r in range(3): affine.append(tuple(3*r+c for c in range(3)))
    for c in range(3): affine.append(tuple(3*r+c for r in range(3)))
    for b in range(3): affine.append(tuple(3*r+((r+b)%3) for r in range(3)))
    out=[replay('FANO_7',incidence(7,fano),0),replay('AFFINE_3X3',incidence(9,affine),3)]
    print(json.dumps({"status":"PASS_MAXIMUM_LINEAR_EVEN_COVER_SATURATION_FINITE_REGRESSION",
                      "authority":"OFFLINE_FALSIFIER_ONLY","controls":out,
                      "scientific_boundary":{"E8_D1":"EMPTY","P_VS_NP":"OPEN"}},indent=2,sort_keys=True))

if __name__=='__main__': main()
