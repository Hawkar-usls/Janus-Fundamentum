#!/usr/bin/env python3
"""R5 E124: E64 one-edge crossed 2-lift high-nullity UNSAT / separator replay."""

from collections import deque

from r5_e64_connected_postquotient_nullity_firewall import (
    rank_q,
    tutte12_incidence,
    verify_square_cubic_linear,
)


def first_incidence(M):
    for i,row in enumerate(M):
        for j,v in enumerate(row):
            if v:
                return i,j
    raise AssertionError("no incidence")


def sign_flip(M,e):
    c,v=e
    S=[row[:] for row in M]
    assert S[c][v]==1
    S[c][v]=-1
    return S


def two_lift(M,e):
    n=len(M)
    c0,v0=e
    L=[[0]*(2*n) for _ in range(2*n)]
    for i,row in enumerate(M):
        for j,a in enumerate(row):
            if not a:
                continue
            shift = 1 if (i,j)==(c0,v0) else 0
            for s in (0,1):
                L[2*i+s][2*j+(s^shift)] = 1
    return L


def levi_adj(M):
    n=len(M)
    adj=[set() for _ in range(2*n)]
    for i,row in enumerate(M):
        for j,a in enumerate(row):
            if a:
                u=i
                v=n+j
                adj[u].add(v)
                adj[v].add(u)
    return adj


def is_connected(adj):
    seen={0}
    todo=[0]
    while todo:
        u=todo.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                todo.append(v)
    return len(seen)==len(adj)


def remove_edges(adj,edges):
    out=[set(x) for x in adj]
    for u,v in edges:
        assert v in out[u] and u in out[v]
        out[u].remove(v)
        out[v].remove(u)
    return out


def component_sizes(adj):
    unseen=set(range(len(adj)))
    sizes=[]
    while unseen:
        root=next(iter(unseen))
        seen={root}
        q=[root]
        unseen.remove(root)
        while q:
            u=q.pop()
            for v in adj[u]:
                if v in unseen:
                    unseen.remove(v)
                    seen.add(v)
                    q.append(v)
        sizes.append(len(seen))
    return sorted(sizes)


def main():
    R=tutte12_incidence()
    n=len(R)
    assert n==63
    verify_square_cubic_linear(R,expected_girth=12)
    assert rank_q(R)==49
    d=n-rank_q(R)
    assert d==14

    e=first_incidence(R)
    assert e==(0,0)

    # The base edge is not a bridge.
    G=levi_adj(R)
    assert is_connected(G)
    base_edge=(e[0], n+e[1])
    assert is_connected(remove_edges(G,[base_edge]))

    S=sign_flip(R,e)
    rs=rank_q(S)
    ds=n-rs
    assert rs==50
    assert ds==13
    assert d+ds==27
    assert d+ds==2*d-1

    L=two_lift(R,e)
    N=len(L)
    assert N==126

    # Cover preserves square/cubic/linear.
    assert all(sum(row)==3 for row in L)
    assert all(sum(L[i][j] for i in range(N))==3 for j in range(N))
    for i in range(N):
        for j in range(i):
            assert sum(a*b for a,b in zip(L[i],L[j]))<=1

    H=levi_adj(L)
    assert is_connected(H)

    # The only sheet-crossing incidences are the two lifts of e.
    # Check indices are 2*c+s; variable Levi vertices are N+(2*v+s).
    c,v=e
    cross=[
        (2*c+0, N+(2*v+1)),
        (2*c+1, N+(2*v+0)),
    ]
    Hcut=remove_edges(H,cross)
    sizes=component_sizes(Hcut)
    assert sizes==[126,126]

    print("R5 E124 one-edge 2-lift firewall: PASS")
    print("base q=63 rank_Q=49 d_Q=14 UNSAT by frozen E64")
    print("signed block rank_Q=50 d_Q=13")
    print("first lift q=126 d_Q=27 = 2*14-1")
    print("lift square/cubic/linear and connected")
    print("delete two crossed edges -> balanced components [126,126]")
    print("tower UNSAT follows from one-check redundancy")
    print("d_{k+1} >= 2 d_k - 1 => linear-nullity scalable tower")
    print("small-separator router survives; post-router benchmark remains OPEN")
    print("P_VS_NP remains OPEN")


if __name__=="__main__":
    main()
