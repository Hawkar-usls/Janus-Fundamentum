#!/usr/bin/env python3
"""R5 E128: exact boundary of the first SAT three-check puncture of E64."""

from fractions import Fraction

from r5_e64_connected_postquotient_nullity_firewall import (
    rank_q,
    tutte12_incidence,
    two_level_kernel_count,
)

DELETED=(33,34,39)
PORTS=(23,32,33,34,38,39,61)
EXPECTED_STATES={
    (1,1,0,1,1,1,1),
    (1,1,1,1,1,1,1),
}


def rref_affine(M,b):
    A=[[Fraction(v) for v in row]+[Fraction(rhs)]
       for row,rhs in zip(M,b)]
    m=len(A)
    n=len(M[0])
    pivots=[]
    r=0
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
                A[i]=[A[i][j]-f*A[r][j] for j in range(n+1)]
        pivots.append(c)
        r+=1
        if r==m:
            break
    return A,pivots


def enumerate_boolean_affine(M,b):
    R,pivots=rref_affine(M,b)
    n=len(M[0])
    free=[c for c in range(n) if c not in pivots]
    assert len(free)==15

    coeff=[]
    for rr,pc in enumerate(pivots):
        coeff.append((
            [R[rr][f] for f in free],
            R[rr][-1],
            pc,
        ))

    solutions=[]
    for mask in range(1<<len(free)):
        vals=[(mask>>k)&1 for k in range(len(free))]
        x=[None]*n
        for f,v in zip(free,vals):
            x[f]=v

        ok=True
        for co,rhs,pc in coeff:
            value=rhs
            for a,v in zip(co,vals):
                if a:
                    value-=a*v
            if value not in (0,1):
                ok=False
                break
            x[pc]=int(value)

        if ok:
            assert all(v in (0,1) for v in x)
            assert all(
                sum(M[i][j]*x[j] for j in range(n))==b[i]
                for i in range(len(M))
            )
            solutions.append(tuple(x))

    return solutions


def main():
    R=tutte12_incidence()
    n=len(R)
    assert n==63
    assert rank_q(R)==49
    d,count=two_level_kernel_count(R)
    assert d==14 and count==0

    deleted_supports=[
        tuple(j for j,v in enumerate(R[r]) if v)
        for r in DELETED
    ]
    assert deleted_supports==[
        (32,33,61),
        (23,33,34),
        (33,38,39),
    ]

    kept=[R[i] for i in range(n) if i not in DELETED]
    assert len(kept)==60
    assert rank_q(kept)==48

    sols=enumerate_boolean_affine(kept,[1]*60)
    assert len(sols)==8

    states={tuple(x[p] for p in PORTS) for x in sols}
    assert states==EXPECTED_STATES

    outer=[p for p in PORTS if p!=33]
    assert len(outer)==6
    assert all(all(x[p]==1 for p in outer) for x in sols)

    # Per m blocks: 6m forced-one outer deficits, but 3m replacement
    # Exact-One checks can accept only 3m selected incidences.
    for m in (1,2,7):
        assert 6*m > 3*m

    print("R5 E128 three-check puncture boundary firewall: PASS")
    print("deleted rows=(33,34,39), supports form a star at variable 33")
    print("retained rows=60 rank_Q=48 affine_free_dim=15")
    print("Boolean punctured-block solutions=8")
    print("exact 7-port boundary states=",sorted(states))
    print("six outer ports forced 1; central port 33 free")
    print("any degree-restoring 3-uniform splice: 6m forced incidences > 3m capacity => UNSAT")
    print("constant-state block decomposition remains easy; scalable post-router benchmark OPEN")
    print("P_VS_NP remains OPEN")


if __name__=="__main__":
    main()
