#!/usr/bin/env python3
"""Exact finite regression for the arbitrary-size exponential Graver theorem.

The theorem is symbolic.  This checker constructs k=1..6 members, verifies
square/linear/cubic/connected structure, rational rank n-1, and reconstructs the
primitive null vector with infinity norm 2^k using Fraction arithmetic.
"""

from fractions import Fraction
from itertools import combinations
from math import gcd

G_ROWS = [
    (6,3,0),(5,6,4),(8,4,0),(6,7,8),(4,7,3),(1,5,2),(8,3,5)
]
G_IN = (1,2)
G_OUT = (7,0)

C_ROWS = [
    (8,4,7),(6,3,4),(2,6,8),(0,3,7),(4,5,2),(8,5,3),(1,7,2)
]
C_IN = (1,0)
C_OUT = (5,6)


class DSU:
    def __init__(self,n):
        self.p=list(range(n))
    def find(self,x):
        if self.p[x]!=x:
            self.p[x]=self.find(self.p[x])
        return self.p[x]
    def union(self,a,b):
        a,b=self.find(a),self.find(b)
        if a!=b:
            self.p[b]=a


def build(k):
    blocks=k+1
    d=DSU(9*blocks)
    def v(block,local):
        return 9*block+local

    for t in range(k-1):
        for a,b in zip(G_OUT,G_IN):
            d.union(v(t,a),v(t+1,b))

    cap=k
    for a,b in zip(G_OUT,C_IN):
        d.union(v(k-1,a),v(cap,b))
    for a,b in zip(C_OUT,G_IN):
        d.union(v(cap,a),v(0,b))

    raw=[]
    for t in range(k):
        raw.extend(tuple(v(t,j) for j in row) for row in G_ROWS)
    raw.extend(tuple(v(cap,j) for j in row) for row in C_ROWS)

    labels={}
    def lab(x):
        r=d.find(x)
        if r not in labels:
            labels[r]=len(labels)
        return labels[r]

    rows=[tuple(lab(x) for x in row) for row in raw]
    anchor=lab(v(0,G_IN[0]))
    return rows,len(labels),anchor


def matrix(rows,n):
    A=[[0]*n for _ in range(n)]
    for i,row in enumerate(rows):
        for j in row:
            A[i][j]=1
    return A


def rank_q(A):
    a=[[Fraction(x) for x in row] for row in A]
    m=len(a); n=len(a[0]); r=0
    for c in range(n):
        p=next((i for i in range(r,m) if a[i][c]),None)
        if p is None:
            continue
        a[r],a[p]=a[p],a[r]
        q=a[r][c]
        a[r]=[x/q for x in a[r]]
        for i in range(m):
            if i!=r and a[i][c]:
                q=a[i][c]
                a[i]=[a[i][j]-q*a[r][j] for j in range(n)]
        r+=1
        if r==m:
            break
    return r


def solve_anchor(A,anchor):
    # Solve A h=0 plus h_anchor=1 by exact RREF.
    n=len(A)
    aug=[[Fraction(x) for x in row]+[Fraction(0)] for row in A]
    extra=[Fraction(0)]*(n+1)
    extra[anchor]=1; extra[-1]=1
    aug.append(extra)
    m=len(aug); row=0; piv=[]
    for c in range(n):
        p=next((i for i in range(row,m) if aug[i][c]),None)
        if p is None:
            continue
        aug[row],aug[p]=aug[p],aug[row]
        q=aug[row][c]
        aug[row]=[x/q for x in aug[row]]
        for i in range(m):
            if i!=row and aug[i][c]:
                q=aug[i][c]
                aug[i]=[aug[i][j]-q*aug[row][j] for j in range(n+1)]
        piv.append(c); row+=1
    assert len(piv)==n
    h=[Fraction(0)]*n
    for i,c in enumerate(piv):
        h[c]=aug[i][-1]
    return h


def verify_structure(rows,n):
    assert len(rows)==n
    deg=[0]*n
    pairs=set()
    adj=[set() for _ in range(n)]
    for row in rows:
        assert len(set(row))==3
        for j in row:
            deg[j]+=1
        for a,b in combinations(sorted(row),2):
            assert (a,b) not in pairs
            pairs.add((a,b))
            adj[a].add(b); adj[b].add(a)
    assert all(d==3 for d in deg)
    seen={0}; stack=[0]
    while stack:
        u=stack.pop()
        for w in adj[u]:
            if w not in seen:
                seen.add(w); stack.append(w)
    assert len(seen)==n


def main():
    for k in range(1,7):
        rows,n,anchor=build(k)
        verify_structure(rows,n)
        A=matrix(rows,n)
        r=rank_q(A)
        assert r==n-1,(k,n,r)
        h=solve_anchor(A,anchor)
        assert all(x.denominator==1 for x in h)
        h=[int(x) for x in h]
        assert all(sum(A[i][j]*h[j] for j in range(n))==0 for i in range(n))
        gg=0
        for x in h:
            gg=gcd(gg,abs(x))
        assert gg==1
        inf=max(abs(x) for x in h)
        assert inf==2**k,(k,inf,h)
        print(f"PASS k={k}: n={n} rank={r} nullity=1 primitive_inf={inf}")

    print("PASS: finite regression agrees with exponential Graver theorem")
    print("P_VS_NP=OPEN; E8_D1=EMPTY")


if __name__ == '__main__':
    main()
