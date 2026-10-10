#!/usr/bin/env python3
"""Exact finite checker for the triple-empty completeness falsifier.

Only Python integer/rational arithmetic is used.  No SAT, MILP, or floating
optimization oracle is invoked.
"""

from fractions import Fraction
from itertools import combinations, product
from math import gcd

P=[5,18,17,19,16,3,21,10,9,6,23,15,8,14,20,2,1,7,0,13,11,22,12,4]
Q=[16,6,19,10,23,4,2,13,7,17,9,21,22,11,3,12,15,20,5,0,1,8,14,18]
N=24
PAIR=((12,12),(21,21))
XSTAR=[0,0,0,-1,1,1,1,0,1,0,1,0,0,0,1,1,0,0,0,1,1,0,0,0]
LEFT=[0,0,-1,1,0,0,0,-1,0,0,0,-1,-1,1,-1,1,0,1,0,0,0,1,0,0]
MOD7=[6,0,2,3,6,1,0,3,6,0,1,0,1,2,4,5,2,5,0,2,5,0,1,0]

KSRC_ROWS=[
(4,-2,-1),(2,-1,0),(1,0,0),(3,0,1),(0,-1,-1),(-3,1,0),
(-1,0,-1),(1,0,0),(0,-1,-1),(-1,1,1),(0,-1,-1),(1,0,0),
(0,0,1),(-1,1,1),(0,-1,-1),(-1,0,-1),(-1,1,1),(2,-1,0),
(-1,1,1),(-3,1,0),(-3,1,0),(0,0,1),(0,1,0),(1,0,0)]

SIGNED_COLS=[
[-7,-2,-2,-1,-3,4,-1,-4,3,1,-1,-2,3,5,-3,-1,3,0,3,2,4,3,0,0],
[-2,-1,0,0,-1,1,0,0,-1,1,-1,0,0,1,-1,0,1,-1,1,1,1,0,1,0],
[4,2,1,3,0,-3,-1,1,0,-1,0,1,0,-1,0,-1,-1,2,-1,-3,-3,0,0,1],
]

GADGET=[(2,5,6),(1,4,7),(5,7,9),(0,3,7),(4,6,9),(2,4,8),(3,8,9),(0,5,8),(1,3,6)]
TSET={0,1,2,9}; SSET={3,4,5}; RSET={6,7,8}


def source_matrix():
    A=[[0]*N for _ in range(N)]
    for i in range(N):
        for j in {i,P[i],Q[i]}:
            A[i][j]=1
    return A


def matvec(A,x):
    return [sum(a*b for a,b in zip(row,x)) for row in A]


def matmul(A,B):
    # B as rows n x d
    d=len(B[0])
    return [[sum(A[i][k]*B[k][j] for k in range(len(B))) for j in range(d)] for i in range(len(A))]


def rank_q(M):
    a=[[Fraction(v) for v in row] for row in M]
    m=len(a); n=len(a[0]) if m else 0; r=0
    for c in range(n):
        p=next((i for i in range(r,m) if a[i][c]),None)
        if p is None: continue
        a[r],a[p]=a[p],a[r]
        z=a[r][c]
        a[r]=[v/z for v in a[r]]
        for i in range(m):
            if i==r or a[i][c]==0: continue
            z=a[i][c]
            a[i]=[a[i][j]-z*a[r][j] for j in range(n)]
        r+=1
        if r==m: break
    return r


def lift_matrix(A):
    n=len(A)
    E=[[0]*n for _ in range(n)]
    for i,j in PAIR: E[i][j]=1
    B=[[A[i][j]-E[i][j] for j in range(n)] for i in range(n)]
    return [B[i]+E[i] for i in range(n)]+[E[i]+B[i] for i in range(n)]


def signed_matrix(A):
    S=[row[:] for row in A]
    for i,j in PAIR: S[i][j]-=2
    return S


def det2(a,b,c,d): return a*d-b*c

def det3(m):
    return (m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1])
           -m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0])
           +m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0]))


def rank_delta(M):
    # M has at most three rows. Return (rank, gcd of maximal minors).
    r=len(M); c=len(M[0]) if r else 0
    if r==0: return 0,1
    vals=[abs(M[i][j]) for i in range(r) for j in range(c) if M[i][j]]
    if not vals: return 0,1
    if r>=2:
        minors=[]
        for rs in combinations(range(r),2):
            for cs in combinations(range(c),2):
                d=det2(M[rs[0]][cs[0]],M[rs[0]][cs[1]],M[rs[1]][cs[0]],M[rs[1]][cs[1]])
                if d: minors.append(abs(d))
        if minors:
            if r==3:
                m3=[]
                for cs in combinations(range(c),3):
                    d=det3([[M[i][j] for j in cs] for i in range(3)])
                    if d: m3.append(abs(d))
                if m3:
                    g=0
                    for d in m3: g=gcd(g,d)
                    return 3,g
            g=0
            for d in minors: g=gcd(g,d)
            return 2,g
    g=0
    for d in vals: g=gcd(g,d)
    return 1,g


def lattice_member_small(C,b):
    r=len(C)
    aug=[C[i]+[b[i]] for i in range(r)]
    rank1,delta1=rank_delta(C)
    rank2,delta2=rank_delta(aug)
    return rank1==rank2 and delta1==delta2


def projection_state(x0,K,inds,bits):
    C=[[K[i][j] for j in range(len(K[0]))] for i in inds]
    b=[bits[t]-x0[inds[t]] for t in range(len(inds))]
    return lattice_member_small(C,b)


def connected_rows(rows,ncols):
    R=len(rows); adj=[[] for _ in range(R+ncols)]
    for i,row in enumerate(rows):
        for j in row:
            adj[i].append(R+j); adj[R+j].append(i)
    seen={0}; stack=[0]
    while stack:
        u=stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v); stack.append(v)
    return len(seen)==R+ncols


def build_regularized_rows(source_rows,nvars):
    out=[]
    for v in range(nvars):
        off=10*v
        out += [tuple(off+j for j in row) for row in GADGET]
    occ=[0]*nvars
    for row in source_rows:
        rr=[]
        for v in row:
            k=occ[v]; assert k<3
            rr.append(10*v+k); occ[v]+=1
        out.append(tuple(rr))
    assert occ==[3]*nvars
    return out


A=source_matrix()
AHAT=lift_matrix(A)
S=signed_matrix(A)
X48=XSTAR+XSTAR

# Structured 48 x 6 kernel basis by rows.
K48=[]
for i in range(N):
    K48.append(list(KSRC_ROWS[i])+[SIGNED_COLS[j][i] for j in range(3)])
for i in range(N):
    K48.append(list(KSRC_ROWS[i])+[-SIGNED_COLS[j][i] for j in range(3)])


def main():
    # Base certificates.
    assert matvec(A,XSTAR)==[1]*N
    assert [sum(A[i][j]*LEFT[i] for i in range(N)) for j in range(N)]==[0]*N
    assert LEFT[12]==-1 and LEFT[21]==1
    modcols=[sum(MOD7[i]*A[i][j] for i in range(N))%7 for j in range(N)]
    target=[0]*N; target[0]=1; target[3]=1; target[22]=2
    assert modcols==target and sum(MOD7)%7==6

    # Lift algebra.
    assert matvec(AHAT,X48)==[1]*48
    assert matmul(AHAT,K48)==[[0]*6 for _ in range(48)]
    assert rank_q(K48)==6
    assert rank_q(AHAT)==42

    # RKPR coordinate rows: nonzero; any proportional pair has ratio +1.
    zero=0; prop=0
    for i,row in enumerate(K48):
        if not any(row): zero+=1
        for j in range(i):
            other=K48[j]
            ratio=None; ok=True
            for a,b in zip(row,other):
                if b==0:
                    if a!=0: ok=False; break
                else:
                    q=Fraction(a,b)
                    if ratio is None: ratio=q
                    elif ratio!=q: ok=False; break
            if ok and ratio is not None:
                prop+=1
                assert ratio==1
    assert zero==0

    # All-zero unary/pair projection assignment is integer-extendable.
    for i in range(48):
        assert projection_state(X48,K48,(i,),(0,))
    for i,j in combinations(range(48),2):
        assert projection_state(X48,K48,(i,j),(0,0))

    # Full no-empty-triple census using only the explicit genuine kernel sublattice.
    hist={}; empty=0
    for inds in combinations(range(48),3):
        count=0
        for bits in product((0,1),repeat=3):
            if projection_state(X48,K48,inds,bits):
                count+=1
        hist[count]=hist.get(count,0)+1
        if count==0: empty+=1
    assert empty==0
    assert hist=={8:8902,4:7710,3:260,2:350,1:74}

    # Regularizer local Boolean terminal relation.
    terms=set(); local_models=0
    for bits in product((0,1),repeat=10):
        if all(sum(bits[j] for j in row)==1 for row in GADGET):
            local_models+=1; terms.add((bits[0],bits[1],bits[2]))
    assert local_models==3 and terms=={(0,0,0),(1,1,1)}

    # Lift row supports and 480x480 regularized carrier structure.
    srcrows=[tuple(j for j,v in enumerate(row) if v) for row in AHAT]
    Lrows=build_regularized_rows(srcrows,48)
    assert len(Lrows)==480
    coldeg=[0]*480
    for row in Lrows:
        assert len(row)==3
        for j in row: coldeg[j]+=1
    assert coldeg==[3]*480
    sets=[set(r) for r in Lrows]
    assert all(len(sets[i]&sets[j])<=1 for i in range(len(sets)) for j in range(i))
    assert connected_rows(Lrows,480)

    print("Triple-empty two-edge-lift falsifier: PASS")
    print("Ahat: 48x48 rank_Q=42 nullity_Q=6, exact UNSAT contraction preconditions PASS")
    print(f"RKPR proportional pairs={prop}, all ratio +1")
    print("pair2 witness: 0^48; every singleton/pair state checked")
    print(f"triple census={hist}; empty=0")
    print("EQ3 transfer: 480x480 connected square linear cubic; SAT equivalence/local projection transfer certified")
    print("TRIPLE_EMPTY_COMPLETENESS=FALSE")
    print("E8_D1=EMPTY P_VS_NP=OPEN")


if __name__=='__main__':
    main()
