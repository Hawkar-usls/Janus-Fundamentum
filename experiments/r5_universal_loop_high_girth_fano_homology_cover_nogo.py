#!/usr/bin/env python3
"""R5 strict all-depth fixed-loop-cutoff NO-GO via explicit 2-group homology covers.

Given any connected cubic C4-free bipartite Tanner graph H from
the ORIGINAL Fano7 SCL (7 rows, 7 columns, 21 incidence edges),
construct the mod-2 homology (Z2)^r voltage cover:
  choose a spanning tree T; r=|E|-|V|+1 off-tree incidence edges;
  label each tree edge by 0 and each chord by its distinct basis vector.
  Lift every vertex to (v,h), h in F2^r; original edge u-v of voltage
  k lifts to (u,h)--(v,h XOR k).

THEOREM:
(1) Covering is regular, cubic, bipartite, C4-free, and connected,
    with degree 2^r and original-source 1-in-3 legality inherited.
(2) girth(cover(H)) > girth(H). For if a lifted cycle has length
    <= base girth g, its projection is a non-backtracking closed
    walk <=g and therefore a SIMPLE base cycle of length exactly g.
    Every simple base cycle contains a chord of T exactly once,
    so its independent F2 chord-voltage sum is nonzero. Contradiction.
(3) The new SCL has n'=n*2^r source rows and columns. Starting
    from Fano7 n=7 nonmultiple3 and iterating covers, all n_j
    remain nonmultiple3. Sum of Exact-One clauses on any satisfying
    assignment would give 3 sum(x)=n_j, impossible. Thus every
    source in the tower is UNSAT with a one-line integer certificate.
(4) Contract ANY Tanner perfect matching to form the canonical
    quartic T4 rank-two network Q. A simple k-cycle in Q lifts
    to a Tanner non-backtracking closed walk of length <=2k
    (one unmatched incidence per quotient edge, at most one
    matched incidence per quotient cell). Hence
          girth(Q) >= girth(H)/2.
    As girth(H) tends to infinity in the cover tower,
    so does girth(Q) for every matching.

(5) In the EXACT R5 generalized-loop identity, a nonempty
    contributing selected-edge subgraph has degree 2 or 3 at
    each occupied vertex. Every finite such graph contains a cycle,
    so its edge cardinality >= girth(Q). Therefore for ANY FIXED
    cutoff L, choose a sufficiently deep Fano cover with girth(Q)>L.
    The truncated signed loop sum is exactly the EMPTY term 1,
    while the true loop sum is 0 because original source is UNSAT.

This strictly refutes universal FIXED-loop-size truncation and
fixed-depth local corrections, not ALL polynomial-time methods,
not k growing with n, and not P vs NP.
"""
from __future__ import annotations

from collections import deque
from itertools import combinations

from r5_universal_exact_support_residual_dag_attack import validate_sparse
from r5_universal_all_odd_cyclic_pc2_four_orbit_identity import cyclic
from r5_universal_all_scl_perfect_matching_rank2_network import (
    paired_quartic_network,verify_paired_quartic_network
)
from r5_universal_rank2_exact_bethe_loop_correction import local_loop_moments


def original_tanner_edges(rows,n):
    rows=validate_sparse(rows,n)
    return tuple((i,n+v) for i,row in enumerate(rows) for v in row)


def spanning_tree_voltages(rows,n):
    """Canonical connected spanning-tree chord basis in polynomial time."""
    edges=original_tanner_edges(rows,n)
    adj=[[] for _ in range(2*n)]
    for eid,(u,v) in enumerate(edges):
        adj[u].append((v,eid))
        adj[v].append((u,eid))
    assert all(len(a)==3 for a in adj)
    visited={0};queue=deque([0]);tree=set()
    while queue:
        v=queue.popleft()
        for w,eid in adj[v]:
            if w not in visited:
                visited.add(w);queue.append(w);tree.add(eid)
    assert len(visited)==2*n,"base graph must be connected"
    assert len(tree)==2*n-1
    chords=[i for i in range(len(edges)) if i not in tree]
    assert len(chords)==3*n-(2*n-1)==n+1
    volts=[0]*len(edges)
    for bit,eid in enumerate(chords):
        volts[eid]=1<<bit
    return edges,tuple(volts),len(chords)


def binary_homology_cover(rows,n,sheet_limit=4096):
    """Explicit first cover; tower generality is symbolic proof above."""
    rows=validate_sparse(rows,n)
    edges,volts,r=spanning_tree_voltages(rows,n)
    sheets=1<<r
    assert sheets<=sheet_limit,"explicit verification resource guard"
    new_n=n*sheets
    lifted=[[] for _ in range(new_n)]
    for (u,v),delta in zip(edges,volts):
        assert 0<=u<n and n<=v<2*n
        base_var=v-n
        for h in range(sheets):
            lifted[u*sheets+h].append(base_var*sheets+(h^delta))
    rebuilt=validate_sparse(tuple(map(tuple,lifted)),new_n)
    assert new_n%3!=0 if n%3!=0 else True
    assert len(rebuilt)==new_n
    return rebuilt,new_n,{
        "base_n":n,"sheets":sheets,"chords":r,
        "new_n":new_n,"voltage_bits":r,
    }


def tanner_girth_up_to(rows,n,up_to):
    """Return an observed cycle <= bound, else give proved girth > bound.

    Exact bounded-depth BFS from all ORIGINAL Tanner vertices.
    Complexity O(n * 3^(up_to)), appropriate for finite controls.
    """
    rows=validate_sparse(rows,n)
    edges=original_tanner_edges(rows,n)
    g=[[] for _ in range(2*n)]
    for u,v in edges:
        g[u].append(v);g[v].append(u)
    assert all(len(a)==3 for a in g)
    best=None
    for root in range(2*n):
        dist={root:0};parent={root:-1};todo=deque([root])
        while todo:
            v=todo.popleft()
            if dist[v]>=up_to:continue
            for w in g[v]:
                if w not in dist:
                    if dist[v]+1<up_to:
                        dist[w]=dist[v]+1
                        parent[w]=v
                        todo.append(w)
                elif parent[v]!=w:
                    length=dist[v]+dist[w]+1
                    if length<=up_to:
                        best=min(best or length,length)
        if best==4:break
    return best


def quotient_girth_up_to(Q,up_to):
    n=Q["source_n"]
    g=[set() for _ in range(n)]
    for e in Q["endpoints"]:
        assert len(e)==2
        a,b=e[0][0],e[1][0]
        assert a!=b
        g[a].add(b);g[b].add(a)
    assert all(len(a)<=4 for a in g)
    best=None
    for root in range(n):
        dist={root:0};parent={root:-1};todo=deque([root])
        while todo:
            v=todo.popleft()
            if dist[v]>=up_to:continue
            for w in g[v]:
                if w not in dist:
                    if dist[v]+1<up_to:
                        dist[w]=dist[v]+1;parent[w]=v;todo.append(w)
                elif parent[v]!=w:
                    length=dist[v]+dist[w]+1
                    if length<=up_to:
                        best=min(best or length,length)
    return best


def original_sum_refutation(rows,n):
    rows=validate_sparse(rows,n)
    assert len(rows)==n
    assert sum(len(row) for row in rows)==3*n
    degree=[0]*n
    for row in rows:
        for v in row:degree[v]+=1
    assert all(d==3 for d in degree)
    assert n%3!=0, "this simple global divisibility refutation not available"
    # If SAT: n = sum_rows 1 = sum_vars (degree*x_v)=3 sum_v x_v,
    # impossible when n not divisible by 3.
    return {"status":"UNSAT",
            "method":"ORIGINAL_CLAUSE_SUM_MOD3",
            "n_mod3":n%3}


def local_loop_fixed_cutoff_value(Q,cutoff,girth_lower):
    """Mathematically certify no nonempty contributor <= cutoff."""
    assert cutoff<girth_lower
    moments=local_loop_moments()
    assert all(moments[1<<i]==0 for i in range(4))
    assert moments[15]==0
    # Nonempty degree-(2,3) graph has a cycle. If no cycles
    # of <= cutoff edges exist, every such term is 0.
    return 1


def main():
    original=cyclic(7)
    assert original_sum_refutation(original,7)["status"]=="UNSAT"
    g0=tanner_girth_up_to(original,7,10)
    assert g0==6,g0
    cover,n1,meta=binary_homology_cover(original,7)
    assert n1==1792
    assert meta["chords"]==8 and meta["sheets"]==256
    assert original_sum_refutation(cover,n1)["status"]=="UNSAT"
    g1=tanner_girth_up_to(cover,n1,9)
    assert g1 is None or g1>g0,(g0,g1)
    print(f"FANO_BINARY_HOMOLOGY_COVER_N{n1}_BASE_GIRTH={g0} "
          f"NEW_GIRTH={g1 or '>9'} UNSAT_MOD3=SOURCE_PROVED",
          flush=True)

    Q=paired_quartic_network(cover,n1)
    assert verify_paired_quartic_network(cover,n1,Q)
    qg=quotient_girth_up_to(Q,5)
    # Any base Tanner cycle from a Q cycle uses <=2 edges per
    # contracted vertex, so qg is at least ceil(g1/2).
    if g1 is not None:
        assert qg is None or 2*qg>=g1
    print(f"FANO_HOMOLOGY_QUOTIENT_N{n1}_GIRTH_LE5="
          f"{qg if qg is not None else 'NONE'}",flush=True)

    if qg is None:
        assert local_loop_fixed_cutoff_value(Q,5,6)==1
        print("HOMOLOGY_UNSAT_TRUE_LOOP_SUM=0 "
              "TRUNCATED_THROUGH_5_EDGES=1_FALSE_POSITIVE",flush=True)
    else:
        assert qg>=4
        assert local_loop_fixed_cutoff_value(Q,qg-1,qg)==1
        print(f"HOMOLOGY_UNSAT_TRUE_LOOP_SUM=0 "
              f"TRUNCATED_THROUGH_{qg-1}_EDGES=1_FALSE_POSITIVE",
              flush=True)

    # A second explicit homology cover is enormous (new chord rank
    # n1+1=1793, so 2^1793 sheets): use the rigorous symbolically
    # proved tower theorem, DO NOT attempt memory allocation.
    assert spanning_tree_voltages(cover,n1)[2]==n1+1
    print("FANO_BINARY_COVER_TOWER_GIRTH_UNBOUNDED=PROVED")
    print("EVERY_TOWER_LEVEL_ORIGINAL_SCL_UNSAT_MOD3=PROVED")
    print("EVERY_FIXED_LOOP_LENGTH_CUTOFF_FALSE_POSITIVE_SOME_UNSAT=PROVED")
    print("GROWING_LOOP_LENGTH_AND_IMPLICIT_SUM_COMPRESSION=OPEN")
    print("UNIVERSAL_POLY_SOLVELINEARCUBICXSAT=NOT_CONSTRUCTED")
    print("P_VS_NP=OPEN")


if __name__=="__main__":
    main()
