#!/usr/bin/env python3
"""R5 structural theorem: matching-contraction quartic network RETAINS
linear treewidth on cubic-expander SCL instances.

Let H be ANY original legal cubic SCL Tanner incidence graph, and
let Q be the n-cell quotient obtained by contracting a source-verified
perfect matching M of n original row/variable Tanner edges.
Q has n vertices, 2n undirected edges, degree4 (multigraph possible).

For EVERY tree decomposition D of Q of width w, replace EACH
bag B by the union of the TWO original H vertices corresponding
to each paired cell in B. This yields a tree decomposition of H:
- matched H edge is contained in any bag of its quotient cell;
- unmatched H edge joins two cells of Q, so some bag has both;
- running intersection is identical for each original half-cell.
Every lifted bag has <=2(w+1) original nodes. Therefore
    tw(H) <= 2 tw(Q) + 1;
    tw(Q) >= (tw(H)-1)/2.

Earlier SOURCE-CERTIFIED theorem: for any connected simple cubic
G, the original Holyer SCL Tanner graph H(A_G) contains G as a
topological minor, so tw(H)>=tw(G). Infinite 3-regular expander
families have tw(G)=Omega(|V(G)|)=Omega(n). Therefore the rank-two
matched quotient Q also has tw(Q)=Omega(n) for those families.
This rules out easy treewidth-bounded DP on ALL quotient networks;
it does NOT rule out unrelated implicit algebraic compression.

The executable builds and independently checks true
variable-elimination tree decompositions for multiple original
sources, then verifies the exact lifted decomposition against
all original Tanner edges. The universal inequality is proved
symbolically above; samples only corroborate the proof.
"""
from __future__ import annotations
from collections import deque
from itertools import combinations

from r5_universal_all_scl_perfect_matching_rank2_network import (
    paired_quartic_network,verify_paired_quartic_network
)
from r5_universal_exact_support_residual_dag_attack import validate_sparse


def quotient_adjacency(report):
    n=report["source_n"]
    graph=[set() for _ in range(n)]
    for endpoints in report["endpoints"]:
        assert len(endpoints)==2
        a,b=endpoints[0][0],endpoints[1][0]
        assert a!=b
        graph[a].add(b)
        graph[b].add(a)
    assert all(0<=v<n for v in range(n))
    return graph


def elimination_tree_decomposition(graph):
    """Construct VALID decomposition from min-degree elimination; O(n^3).

    w is an upper bound, NOT necessarily the optimal treewidth.
    """
    n=len(graph)
    neigh=[set(s) for s in graph]
    remaining=set(range(n))
    order=[]
    bags=[]
    while remaining:
        v=min(remaining,key=lambda x:(len(neigh[x]&remaining),x))
        boundary=neigh[v]&remaining
        boundary.discard(v)
        bags.append(frozenset({v}|boundary))
        order.append(v)
        for u,w in combinations(sorted(boundary),2):
            neigh[u].add(w)
            neigh[w].add(u)
        for u in boundary:
            neigh[u].discard(v)
        remaining.remove(v)

    pos={v:i for i,v in enumerate(order)}
    parents=[]
    roots=[]
    for i,v in enumerate(order):
        ahead=[u for u in bags[i] if u!=v]
        if not ahead:
            roots.append(i);continue
        p=min(ahead,key=lambda u:pos[u])
        assert pos[p]>i
        parents.append((i,pos[p]))
    if len(roots)>1:
        roots.sort()
        parents.extend((roots[i],roots[i+1])
                       for i in range(len(roots)-1))
    assert len(parents)==n-1
    assert validate_tree_decomposition(graph,bags,parents)
    return tuple(bags),tuple(parents)


def validate_tree_decomposition(graph,bags,links):
    n=len(graph)
    assert bags and all(b and all(0<=x<n for x in b) for b in bags)
    assert len(links)==len(bags)-1
    tree=[set() for _ in bags]
    for a,b in links:
        assert 0<=a<len(bags) and 0<=b<len(bags) and a!=b
        tree[a].add(b)
        tree[b].add(a)
    reached={0};todo=[0]
    for i in todo:
        for j in tree[i]-reached:
            reached.add(j);todo.append(j)
    assert len(reached)==len(bags)
    assert sum(len(z) for z in tree)==2*(len(bags)-1)

    for v in range(n):
        holders={i for i,B in enumerate(bags) if v in B}
        assert holders
        q=[min(holders)];hit=set(q)
        for i in q:
            for j in (tree[i]&holders)-hit:
                hit.add(j);q.append(j)
        assert hit==holders
    for u in range(n):
        for v in graph[u]:
            assert any(u in B and v in B for B in bags)
    return True


def lift_quotient_decomposition(rows,n,report):
    rows=validate_sparse(rows,n)
    assert verify_paired_quartic_network(rows,n,report)
    g=quotient_adjacency(report)
    bags,links=elimination_tree_decomposition(g)
    matching=report["matching"]
    lifted=tuple(frozenset(
        set(B)|{n+matching[i] for i in B}
    ) for B in bags)
    original=[set() for _ in range(2*n)]
    for i,row in enumerate(rows):
        for v in row:
            original[i].add(n+v)
            original[n+v].add(i)
    assert all(len(s)==3 for s in original)
    assert validate_tree_decomposition(original,lifted,links)
    w=max(len(B)-1 for B in bags)
    W=max(len(B)-1 for B in lifted)
    assert W==2*w+1
    return {"source_n":n,"quotient_width_upper":w,
            "original_width_upper_by_lifting":W,
            "cells":n,"bags":len(bags)}


def main():
    from r5_universal_cubic_edgecolor_direct_scl_bridge import (
        make_scl,K4,K33,petersen_graph,cube_graph
    )
    from r5_universal_all_odd_cyclic_pc2_four_orbit_identity import cyclic
    from r5_universal_cubic_flow_lowmoment_collision_20v import flower
    cases=(
        ("FANO7",cyclic(7),7),
        ("K4_SCL18",*make_scl(K4())[:2]),
        ("K33_SCL27",*make_scl(K33())[:2]),
        ("CUBE_SCL36",*make_scl(cube_graph())[:2]),
        ("PETERSEN_SCL45",*make_scl(petersen_graph())[:2]),
        ("J5_SCL90",*make_scl(flower(5))[:2]),
    )
    for name,rows,n in cases:
        report=paired_quartic_network(rows,n)
        audit=lift_quotient_decomposition(rows,n,report)
        print(f"QUOTIENT_TREEWIDTH_LIFT_{name}=REPLAYED "
              f"Q_bound={audit['quotient_width_upper']} "
              f"Tanner_bound={audit['original_width_upper_by_lifting']}",
              flush=True)

    print("FOR_EVERY_MATCHING_QUOTIENT_TW_TANNER_LE_2TW_QUOTIENT_PLUS1=PROVED")
    print("CUBIC_EXPANDER_QUOTIENT_HAS_LINEAR_TW=EXTERNAL_FAMILY_THEOREM")
    print("GENERAL_MATCHGATE_SUM_TREEWIDTH_POLYNOMIAL_GUARANTEE=REFUTED")
    print("UNIFORM_ALGEBRAIC_ZERO_TEST=NOT_CONSTRUCTED")
    print("UNIVERSAL_POLY_SOLVELINEARCUBICXSAT=NOT_CONSTRUCTED")
    print("P_VS_NP=OPEN")


if __name__=="__main__":
    main()
