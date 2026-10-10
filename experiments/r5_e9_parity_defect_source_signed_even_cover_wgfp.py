#!/usr/bin/env python3
"""Finite exact regression for the source-signed even-cover / WGFP bridge.

OFFLINE_FALSIFIER_ONLY: exhaustive controls are not a universal proof.
The universal identities are proved in the companion research note.
"""
from itertools import product
import json


def incidence(n, blocks):
    A=[[0]*n for _ in blocks]
    for r,b in enumerate(blocks):
        for j in b:
            A[r][j]=1
    return A


def matvec(A,x):
    return [sum(a*b for a,b in zip(row,x)) for row in A]


def xor(a,b):
    return tuple(x^y for x,y in zip(a,b))


def linear_cubic(A):
    n=len(A)
    assert len(A)==len(A[0])
    assert all(sum(row)==3 for row in A)
    assert all(sum(A[r][c] for r in range(n))==3 for c in range(n))
    supp=[{j for j,v in enumerate(row) if v} for row in A]
    assert all(len(supp[i]&supp[j])<=1 for i in range(n) for j in range(i))


def kernel(A):
    n=len(A[0])
    return [z for z in product((0,1),repeat=n)
            if all(v%2==0 for v in matvec(A,z))]


def parity_coset(A):
    n=len(A[0])
    return [x for x in product((0,1),repeat=n)
            if all(v%2==1 for v in matvec(A,x))]


def defect_count(A,x):
    vals=matvec(A,x)
    assert all(v in (1,3) for v in vals)
    return sum(v==3 for v in vals)


def replay(name,A,expected_exact_models):
    linear_cubic(A)
    n=len(A)
    C=kernel(A)
    P=parity_coset(A)
    assert P

    exact=[x for x in product((0,1),repeat=n) if matvec(A,x)==[1]*n]
    assert len(exact)==expected_exact_models

    checked=0
    negative_equivalence=0
    for x in P:
        tx=defect_count(A,x)
        assert 3*sum(x)==n+2*tx
        w=[1-2*b for b in x]

        best=min(sum(xor(x,z)) for z in C)
        has_negative=False

        for z in C:
            row_degrees=matvec(A,z)
            assert all(d in (0,2) for d in row_degrees)

            # Levi factor: selected variable => all its 3 incidence edges.
            # Doubled incidence weight is w_i on each of those three edges.
            factor_cost2=0
            for r,row in enumerate(A):
                d=0
                for i,a in enumerate(row):
                    if a and z[i]:
                        d+=1
                        factor_cost2+=w[i]
                assert d in (0,2)

            y=xor(x,z)
            dy=sum(y)-sum(x)
            ty=defect_count(A,y)
            charge=sum(wi*zi for wi,zi in zip(w,z))

            assert charge==dy
            assert factor_cost2==3*charge
            assert factor_cost2==2*(ty-tx)

            if any(z) and charge<0:
                has_negative=True
            checked+=1

        assert has_negative == (best < sum(x))
        negative_equivalence += 1

    return {
        "name":name,
        "n":n,
        "kernel_size":len(C),
        "parity_coset_size":len(P),
        "exact_models":len(exact),
        "checks":checked,
        "parity_points_with_global_optimality_equivalence":negative_equivalence,
        "factor_constraints":"variables {0,3}; rows {0,2}",
        "identity":"factor_cost_doubled = 3*Delta_Hamming = 2*Delta_111_defects",
    }


def main():
    fano=[
        (0,1,2),(0,3,4),(0,5,6),(1,3,5),(1,4,6),(2,3,6),(2,4,5)
    ]
    affine=[]
    for r in range(3):
        affine.append(tuple(3*r+c for c in range(3)))
    for c in range(3):
        affine.append(tuple(3*r+c for r in range(3)))
    for b in range(3):
        affine.append(tuple(3*r+((r+b)%3) for r in range(3)))

    out=[
        replay("FANO_7",incidence(7,fano),0),
        replay("AFFINE_3X3",incidence(9,affine),3),
    ]
    print(json.dumps({
        "status":"PASS_SOURCE_SIGNED_EVEN_COVER_WGFP_FINITE_REGRESSION",
        "authority":"OFFLINE_FALSIFIER_ONLY",
        "controls":out,
        "scientific_boundary":{"E8_D1":"EMPTY","P_VS_NP":"OPEN"},
    },indent=2,sort_keys=True))


if __name__=="__main__":
    main()
