#!/usr/bin/env python3
"""Exact regression for the pair2-completeness linear-cubic falsifier.

No SAT/ILP library is used.  All certificates are explicit integer arithmetic.
This is a finite falsifier/checker, not a universal solver.
"""

from fractions import Fraction
from itertools import combinations, product

P = [7,6,4,2,0,1,8,5,3]
Q = [6,8,7,0,5,2,1,3,4]
N = 9
Y = (0,1,0,0,0,0,1,0,1)

GADGET = [
    (2,5,6), (1,4,7), (5,7,9),
    (0,3,7), (4,6,9), (2,4,8),
    (3,8,9), (0,5,8), (1,3,6),
]
TSET = {0,1,2,9}
SSET = {3,4,5}
RSET = {6,7,8}


def build_source():
    rows=[]
    for i in range(N):
        s={i,P[i],Q[i]}
        assert len(s)==3
        rows.append(tuple(sorted(s)))
    return rows


def x_source(s,r):
    return [
        s,
        2*s-2*r-1,
        1-s+r,
        -r,
        -r,
        1-s+r,
        1-2*s,
        s,
        2*r+1,
    ]


def satisfies(rows,x):
    return all(sum(x[j] for j in row)==1 for row in rows)


def rational_rank(rows,ncols):
    a=[[Fraction(int(j in row)) for j in range(ncols)] for row in rows]
    m=len(a); r=0
    for c in range(ncols):
        p=next((i for i in range(r,m) if a[i][c]),None)
        if p is None:
            continue
        a[r],a[p]=a[p],a[r]
        z=a[r][c]
        a[r]=[v/z for v in a[r]]
        for i in range(m):
            if i==r or a[i][c]==0:
                continue
            z=a[i][c]
            a[i]=[a[i][j]-z*a[r][j] for j in range(ncols)]
        r+=1
    return r


def connected_bipartite(rows,ncols):
    # nodes 0..len(rows)-1 are rows, len(rows)+j are columns
    R=len(rows); total=R+ncols
    adj=[[] for _ in range(total)]
    for i,row in enumerate(rows):
        for j in row:
            adj[i].append(R+j); adj[R+j].append(i)
    seen={0}; stack=[0]
    while stack:
        u=stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v); stack.append(v)
    return len(seen)==total


def linear_rows(rows):
    ss=[set(r) for r in rows]
    return all(len(ss[i]&ss[j])<=1 for i in range(len(rows)) for j in range(i))


def source_pin_extension(indices):
    # Find exact integer source solution matching Y on the requested <=2 coords.
    for s in (-1,0,1):
        for r in (-1,0,1):
            x=x_source(s,r)
            if all(x[i]==Y[i] for i in indices):
                assert satisfies(SOURCE,x)
                return s,r,x
    raise AssertionError(f"missing source pin extension for {indices}")


def build_regularized():
    rows=[]
    for v in range(N):
        off=10*v
        for row in GADGET:
            rows.append(tuple(off+j for j in row))

    occ=[0]*N
    for srcrow in SOURCE:
        rr=[]
        for v in srcrow:
            k=occ[v]
            assert k<3
            rr.append(10*v+k)
            occ[v]+=1
        rows.append(tuple(rr))
    assert occ==[3]*N
    return rows


def z_pair2_assignment():
    z=[None]*(10*N)
    for v in range(N):
        for k in TSET: z[10*v+k]=Y[v]
        for k in RSET: z[10*v+k]=0
        for k in SSET: z[10*v+k]=1-Y[v]
    assert all(v in (0,1) for v in z)
    return z


def regularized_integer_extension(pinned_coords):
    # Search only the exact finite source certificates s,r in {-1,0,1}.
    for ss in (-1,0,1):
        for rr in (-1,0,1):
            q=x_source(ss,rr)
            if not satisfies(SOURCE,q):
                continue

            required_r={}
            ok=True
            for c in pinned_coords:
                v,k=divmod(c,10)
                target=Z[c]
                if k in TSET:
                    if q[v]!=target:
                        ok=False; break
                elif k in RSET:
                    want=target
                    if v in required_r and required_r[v]!=want:
                        ok=False; break
                    required_r[v]=want
                else:
                    assert k in SSET
                    want=1-q[v]-target
                    if v in required_r and required_r[v]!=want:
                        ok=False; break
                    required_r[v]=want
            if not ok:
                continue

            rv=[0]*N
            for v,val in required_r.items():
                rv[v]=val

            x=[0]*(10*N)
            for v in range(N):
                for k in TSET: x[10*v+k]=q[v]
                for k in RSET: x[10*v+k]=rv[v]
                for k in SSET: x[10*v+k]=1-rv[v]-q[v]

            if all(x[c]==Z[c] for c in pinned_coords) and satisfies(LINEARIZED,x):
                return x
    raise AssertionError(f"missing regularized integer extension for {pinned_coords}")


SOURCE=build_source()
LINEARIZED=build_regularized()
Z=z_pair2_assignment()


def main():
    # Source structure.
    assert len(SOURCE)==N
    coldeg=[0]*N
    for row in SOURCE:
        assert len(row)==3
        for j in row: coldeg[j]+=1
    assert coldeg==[3]*N
    assert connected_bipartite(SOURCE,N)
    assert rational_rank(SOURCE,N)==7

    # Exact affine integer parameterization: enough to verify the formulas
    # solve every source equation identically on a grid and rank/nullity agrees.
    for s in range(-3,4):
        for r in range(-3,4):
            assert satisfies(SOURCE,x_source(s,r))

    # Analytic Boolean contradiction plus exhaustive replay.
    # x8=2r+1 Boolean forces r=0; x7=s and x6=1-2s Boolean force s=0;
    # then x1=-1.  Exhaustive replay independently confirms no witness.
    assert not any(satisfies(SOURCE,bits) for bits in product((0,1),repeat=N))

    # Pair2 source certificate: every singleton and pair value from Y extends
    # to an exact integer solution, with s,r in {-1,0,1}.
    source_checks=0
    for size in (1,2):
        for inds in combinations(range(N),size):
            source_pin_extension(inds)
            source_checks+=1
    assert source_checks==9+36
    assert not satisfies(SOURCE,Y)

    # Local EQ3 gadget really realizes terminal equality 000/111.
    terminal_states=set()
    local_solutions=0
    for bits in product((0,1),repeat=10):
        if satisfies(GADGET,bits):
            local_solutions+=1
            terminal_states.add((bits[0],bits[1],bits[2]))
    assert local_solutions==3
    assert terminal_states=={(0,0,0),(1,1,1)}

    # 90x90 regularized carrier structure.
    assert len(LINEARIZED)==90
    coldeg=[0]*90
    for row in LINEARIZED:
        assert len(row)==3
        for j in row: coldeg[j]+=1
    assert coldeg==[3]*90
    assert linear_rows(LINEARIZED)
    assert connected_bipartite(LINEARIZED,90)

    # SAT equivalence on this concrete source follows from the independently
    # checked local terminal-equality relation plus the occurrence wiring:
    # every Boolean regularized witness collapses terminals to a source witness.
    assert terminal_states=={(0,0,0),(1,1,1)}

    # Full regularized pair2 falsifier: all 90 singleton and C(90,2)=4005 pair
    # values of Z extend to exact integer solutions, yet Z itself is not a witness.
    checks=0
    for c in range(90):
        regularized_integer_extension((c,)); checks+=1
    for c,d in combinations(range(90),2):
        regularized_integer_extension((c,d)); checks+=1
    assert checks==90+4005
    assert not satisfies(LINEARIZED,Z)

    print("PAIR2 completeness linear-cubic falsifier: PASS")
    print("source: n=9 rank_Q=7 cubic connected UNSAT, pair2 assignment exists")
    print(f"source pair projections certified: {source_checks}")
    print("regularized: n=90 square cubic linear connected UNSAT by EQ3 terminal equality")
    print(f"regularized singleton/pair integer extensions certified: {checks}")
    print("PAIR2_COMPLETENESS=FALSE")
    print("E8_D1=EMPTY P_VS_NP=OPEN")


if __name__=="__main__":
    main()
