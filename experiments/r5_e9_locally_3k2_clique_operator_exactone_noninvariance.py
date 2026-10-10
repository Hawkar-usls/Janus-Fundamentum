#!/usr/bin/env python3
"""Exact n=12 control: A is Exact-One SAT while A^T is UNSAT."""

from itertools import product

COLOR_CLASSES = [
    [(3,4),(1,2),(0,6)],
    [(4,7),(0,1),(3,5)],
    [(0,5),(2,7),(4,6)],
    [(2,6),(5,7),(1,3)],
]


def build():
    rows=[]
    for c,edges in enumerate(COLOR_CLASSES):
        for u,v in edges:
            rows.append((c,4+u,4+v))
    n=12
    A=[[int(j in row) for j in range(n)] for row in rows]
    return rows,A


def mv(A,x):
    return [sum(a*b for a,b in zip(row,x)) for row in A]


def connected_levi(A):
    n=len(A)
    adj=[[] for _ in range(2*n)]
    for i,row in enumerate(A):
        for j,a in enumerate(row):
            if a:
                adj[i].append(n+j);adj[n+j].append(i)
    seen={0}; stack=[0]
    while stack:
        u=stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v);stack.append(v)
    return len(seen)==2*n


def rainbow_matching():
    used=set(); chosen=[]
    def rec(c):
        if c==len(COLOR_CLASSES):
            return chosen[:]
        for e in COLOR_CLASSES[c]:
            u,v=e
            if u in used or v in used:
                continue
            used.add(u);used.add(v);chosen.append((c,e))
            ans=rec(c+1)
            if ans is not None:return ans
            chosen.pop();used.remove(u);used.remove(v)
        return None
    return rec(0)


def main():
    rows,A=build(); n=12
    assert len(rows)==n
    assert all(sum(row)==3 for row in A)
    assert all(sum(A[i][j] for i in range(n))==3 for j in range(n))
    supports=[set(r) for r in rows]
    assert all(len(supports[i]&supports[j])<=1 for i in range(n) for j in range(i))
    assert connected_levi(A)

    x=[1 if j<4 else 0 for j in range(n)]
    assert mv(A,x)==[1]*n

    # Dual witness iff one edge from each color forms a perfect matching.
    assert rainbow_matching() is None

    At=[list(col) for col in zip(*A)]
    # Independent finite replay over all 2^12 row selections.
    dual=[]
    for bits in product((0,1),repeat=n):
        if mv(At,bits)==[1]*n:
            dual.append(bits)
    assert dual==[]

    print({
        'status':'PASS_LOCALLY_3K2_CLIQUE_OPERATOR_NONINVARIANCE',
        'n':12,
        'connected':True,
        'linear_cubic':True,
        'A_exactone':'SAT',
        'A_witness':[0,1,2,3],
        'A_transpose_exactone':'UNSAT',
        'rainbow_perfect_matching':False,
        'E8_D1':'EMPTY',
        'P_VS_NP':'OPEN',
    })


if __name__=='__main__':
    main()
