#!/usr/bin/env python3
"""Polynomial critical-core closure for 4-color graph quotients.

Exact rules:
  1. Connected components factor independently.
  2. A vertex of degree <=3 can be deleted: every 4-coloring of the remainder
     extends greedily to that vertex.
  3. Articulation blocks factor for k-colorability: color permutations let
     block colorings agree on their shared articulation vertex.
  4. Brooks terminal for a connected block of maximum degree <=4:
       if the block is K5 -> UNSAT;
       otherwise it is 4-colorable.
     (Odd-cycle exceptions to Brooks at Delta=2 are still 4-colorable.)

The procedure is sound, polynomial, and branch-free.  It returns OPEN only on
residual biconnected 4-cores that are not K5 and have maximum degree >=5.

This does not solve arbitrary 4-colorability.
"""

from collections import deque

from graph4color_2xnf_firewall import (
    cycle_graph,
    mycielski,
    graph4_xnf,
    exact_k_colorable,
)


def adjacency(graph):
    n,E=graph
    A=[set() for _ in range(n)]
    for u,v in E:
        A[u].add(v); A[v].add(u)
    return A


def induced_graph(vertices,A):
    verts=tuple(sorted(vertices))
    idx={v:i for i,v in enumerate(verts)}
    E=set()
    for u in verts:
        for v in A[u]:
            if v in idx and idx[u]<idx[v]:
                E.add((idx[u],idx[v]))
    return len(verts),frozenset(E),verts


def peel_degree_le3(graph):
    n,E=graph
    A=adjacency(graph)
    alive=[True]*n
    deg=[len(A[v]) for v in range(n)]
    q=deque(v for v in range(n) if deg[v]<=3)
    order=[]
    while q:
        v=q.popleft()
        if not alive[v] or deg[v]>3:
            continue
        alive[v]=False
        order.append(v)
        for u in A[v]:
            if alive[u]:
                deg[u]-=1
                if deg[u]<=3:
                    q.append(u)
    core={v for v in range(n) if alive[v]}
    return core,tuple(order),A


def connected_components(vertices,A):
    unseen=set(vertices)
    out=[]
    while unseen:
        s=next(iter(unseen))
        C={s}; unseen.remove(s); q=[s]
        while q:
            u=q.pop()
            for v in A[u]:
                if v in unseen:
                    unseen.remove(v); C.add(v); q.append(v)
        out.append(frozenset(C))
    return tuple(out)


def biconnected_blocks(vertices,A):
    """Tarjan edge-biconnected vertex blocks; isolated vertices included."""
    V=set(vertices)
    disc={}
    low={}
    parent={}
    stack=[]
    blocks=[]
    time=0

    def dfs(u):
        nonlocal time
        time+=1
        disc[u]=low[u]=time
        child=0
        for v in A[u]:
            if v not in V:
                continue
            edge=tuple(sorted((u,v)))
            if v not in disc:
                parent[v]=u
                child+=1
                stack.append(edge)
                dfs(v)
                low[u]=min(low[u],low[v])
                if low[v]>=disc[u]:
                    B=set()
                    while stack:
                        e=stack.pop()
                        B.update(e)
                        if e==edge:
                            break
                    if B:
                        blocks.append(frozenset(B))
            elif parent.get(u)!=v and disc[v]<disc[u]:
                low[u]=min(low[u],disc[v])
                stack.append(edge)

    for s in V:
        if s in disc:
            continue
        if not any(v in V for v in A[s]):
            blocks.append(frozenset({s}))
            disc[s]=low[s]=time+1
            time+=1
            continue
        dfs(s)
        if stack:
            B=set()
            while stack:
                B.update(stack.pop())
            if B:
                blocks.append(frozenset(B))

    return tuple(blocks)


def is_K5(block,A):
    if len(block)!=5:
        return False
    return all(
        v in A[u]
        for u in block for v in block
        if u!=v
    )


def block_max_degree(block,A):
    return max((sum(v in block for v in A[u]) for u in block),default=0)


def graph4_critical_core_closure(graph):
    n,E=graph
    core,peeled,A=peel_degree_le3(graph)

    if not core:
        return {
            "status":"SAT",
            "reason":"DEGENERACY_LE_3",
            "peeled":len(peeled),
            "core_vertices":0,
            "open_blocks":tuple(),
        }

    components=connected_components(core,A)
    open_blocks=[]
    brook_blocks=0

    for C in components:
        for B in biconnected_blocks(C,A):
            if len(B)<=1:
                continue
            if is_K5(B,A):
                return {
                    "status":"UNSAT",
                    "reason":"K5_BLOCK",
                    "peeled":len(peeled),
                    "core_vertices":len(core),
                    "witness_block":tuple(sorted(B)),
                    "open_blocks":tuple(),
                }

            Delta=block_max_degree(B,A)
            if Delta<=4:
                # Brooks: connected block other than K5 is 4-colorable.
                brook_blocks+=1
                continue

            open_blocks.append({
                "vertices":len(B),
                "max_degree":Delta,
                "min_degree":min(
                    sum(v in B for v in A[u]) for u in B
                ),
                "edge_count":sum(
                    1 for u in B for v in A[u]
                    if v in B and u<v
                ),
            })

    if not open_blocks:
        return {
            "status":"SAT",
            "reason":"PEEL_BLOCK_BROOKS",
            "peeled":len(peeled),
            "core_vertices":len(core),
            "brooks_blocks":brook_blocks,
            "open_blocks":tuple(),
        }

    return {
        "status":"OPEN",
        "reason":"HIGH_DEGREE_4CRITICAL_CORE",
        "peeled":len(peeled),
        "core_vertices":len(core),
        "brooks_blocks":brook_blocks,
        "open_blocks":tuple(open_blocks),
    }


def complete_graph(n):
    return n,frozenset((i,j) for i in range(n) for j in range(i+1,n))


def path_graph(n):
    return n,frozenset((i,i+1) for i in range(n-1))


def verify_terminals():
    # Degeneracy terminal.
    r=graph4_critical_core_closure(path_graph(20))
    assert r["status"]=="SAT"

    # Immediate K5 obstruction.
    r=graph4_critical_core_closure(complete_graph(5))
    assert r["status"]=="UNSAT"

    # K4 is 4-colorable and removed/closed.
    r=graph4_critical_core_closure(complete_graph(4))
    assert r["status"]=="SAT"

    # M(C5) is 4-colorable.
    G=mycielski(cycle_graph(5))
    assert exact_k_colorable(G,4)
    r=graph4_critical_core_closure(G)
    assert r["status"] in ("SAT","OPEN")

    # Twice-Mycielski C5 is the frozen 5-chromatic triangle-free firewall.
    H=mycielski(G)
    assert not exact_k_colorable(H,4)
    rH=graph4_critical_core_closure(H)
    assert rH["status"]=="OPEN"
    assert rH["core_vertices"]>0
    assert rH["open_blocks"]

    return r,rH


def main():
    sat_control,hard=verify_terminals()

    print("GRAPH 4-COLOR CRITICAL-CORE CLOSURE: PASS")
    print("4-colorable control M(C5):",sat_control)
    print("5-chromatic triangle-free M^2(C5):",hard)
    print("exact polynomial rules: degree<=3 peel + articulation blocks + Brooks Delta<=4 terminal")
    print("residual OPEN = biconnected 4-core block with max degree >=5")
    print("no Boolean color branching is used")
    print("GENERAL_SAT_IN_P = NOT_PROVED")
    print("P_VS_NP = OPEN")


if __name__=="__main__":
    main()
