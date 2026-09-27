#!/usr/bin/env python3
"""Exact regression for the trade-free unique-model 9x9 control.

This is a finite theorem regression / falsifier, not an E8-D1 SAT solver.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import product
import json
from math import gcd


A = [
    [0,0,0,0,0,0,1,1,1],
    [0,1,1,0,0,0,0,1,0],
    [0,0,1,0,1,0,1,0,0],
    [1,1,0,0,0,0,1,0,0],
    [0,0,1,1,0,1,0,0,0],
    [0,0,0,1,1,0,0,0,1],
    [1,0,0,0,1,1,0,0,0],
    [1,0,0,1,0,0,0,1,0],
    [0,1,0,0,0,1,0,0,1],
]
XSTAR = [1,0,1,0,0,0,0,0,1]
V = [2,-1,2,-1,-1,-1,-1,-1,2]


def matvec(M, x):
    return [sum(a*b for a,b in zip(row,x)) for row in M]


def rank_q(M):
    a = [[Fraction(x) for x in row] for row in M]
    m, n = len(a), len(a[0])
    r = 0
    for c in range(n):
        p = next((i for i in range(r,m) if a[i][c]), None)
        if p is None:
            continue
        a[r], a[p] = a[p], a[r]
        q = a[r][c]
        a[r] = [x/q for x in a[r]]
        for i in range(m):
            if i != r and a[i][c]:
                q = a[i][c]
                a[i] = [a[i][j]-q*a[r][j] for j in range(n)]
        r += 1
        if r == m:
            break
    return r


def tanner_connected(M):
    n = len(M)
    adj = [[] for _ in range(2*n)]
    for i,row in enumerate(M):
        for j,a in enumerate(row):
            if a:
                adj[i].append(n+j)
                adj[n+j].append(i)
    seen = {0}
    queue = [0]
    for u in queue:
        for w in adj[u]:
            if w not in seen:
                seen.add(w)
                queue.append(w)
    return len(seen) == 2*n


def tanner_girth(M):
    n=len(M)
    adj=[[] for _ in range(2*n)]
    for i,row in enumerate(M):
        for j,a in enumerate(row):
            if a:
                adj[i].append(n+j); adj[n+j].append(i)
    best=10**9
    for s in range(2*n):
        dist=[-1]*(2*n); parent=[-1]*(2*n)
        dist[s]=0; q=[s]
        for u in q:
            for w in adj[u]:
                if dist[w] < 0:
                    dist[w]=dist[u]+1; parent[w]=u; q.append(w)
                elif parent[u] != w:
                    best=min(best,dist[u]+dist[w]+1)
    return best


n=len(A)
assert n == 9 and all(len(row)==n for row in A)
assert all(sum(row)==3 for row in A)
assert all(sum(A[i][j] for i in range(n))==3 for j in range(n))
assert max(
    sum(A[i][c]*A[j][c] for c in range(n))
    for i in range(n) for j in range(i)
) <= 1
assert tanner_connected(A)
assert tanner_girth(A) == 6

assert matvec(A,XSTAR) == [1]*n
assert rank_q(A) == 8
assert matvec(A,V) == [0]*n
assert [3*x-1 for x in XSTAR] == V
assert gcd(*[abs(x) for x in V if x]) == 1

models=[]
for x in product((0,1), repeat=n):
    if matvec(A,x) == [1]*n:
        models.append(x)
assert models == [tuple(XSTAR)]

signed_trade_count=0
for h in product((-1,0,1), repeat=n):
    if not any(h):
        continue
    if matvec(A,h) == [0]*n:
        signed_trade_count += 1
assert signed_trade_count == 0

out = {
    "status": "PASS_TRADE_FREE_UNIQUE_MODEL_CONTROL",
    "n": n,
    "cubic_rows": True,
    "cubic_columns": True,
    "linear": True,
    "connected": True,
    "tanner_girth": 6,
    "rank_Q": 8,
    "nullity_Q": 1,
    "primitive_integer_kernel_generator": V,
    "exact_one_model_count": len(models),
    "unique_model": XSTAR,
    "signed_trade_search_space_nonzero": 3**n-1,
    "signed_trade_count": signed_trade_count,
    "trade_only_universal_coverage": "FALSIFIED",
    "active_gate": "R5_E9_DISSOCIATED_CUBIC_LINEAR_NULLITY_GATE_V1",
    "E8_D1": "EMPTY",
    "P_VS_NP": "OPEN",
}
print(json.dumps(out, sort_keys=True))
