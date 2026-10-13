#!/usr/bin/env python3
"""R5 stronger INFINITE 3-EDGE-CONNECTED native SCL90+9k no-V3 theorem.

Start with native Isaacs J5 flower G0 and its independently
authenticated 6656-byte GF3 degree-three source-dual.
At each stage replace highest-index cubic graph vertex v
with a triangle T=(v,v+1,v+2), reattaching the three old
incidences (u_j,v) as (u_j,v+j) and adding all three
triangle-internal edges. This is the classical Delta-Y/
triangle vertex expansion.

Graph G_k: V=20+2k, E=30+3k, cubic, simple, connected,
3-edge-connected if G0 is 3-edge-connected (checked).
Native direct Holyer legal SCL F_k has n=90+9k.

SEMANTIC UNSAT: on the 3-vertex (odd) triangle cut, each
perfect-matching colour class must cross an ODD number of
edges. Exactly three external edges cross. Therefore each
colour appears on exactly one external edge. Contracting
triangle to v maps any valid new 3-edge-colouring to a
valid old one. The base flower is UNSAT, so all F_k UNSAT.

EXACT DEGREE-ONE ORIGINAL-SOURCE VARIABLE RETRACTION:
- Retained old edge e: x'_(e,c) -> x_(e,c)
- External edge (u_j,t_j): -> x_(old edge (u_j,v),c)
- Internal triangle edge (t_i,t_j), with {i,j,k}={0,1,2}:
       -> x_(old edge (u_k,v),c).
Any NEW exact-one edge-colour clause becomes the old
clause for its designated edge; any NEW vertex-colour
clause at t_j becomes the OLD clause at v for colour c;
all other old vertex-colour clauses preserved.

Thus EACH native NEW source row EXACTLY maps to ONE native
OLD source row and each Boolean variable maps to ONE Boolean
old variable. Every old degree-d dual pulls forward at
SAME degree via monomial variable identification.
Therefore for ALL k >=0, y_k(1)=1 and y_k(E'_r x'_M)=0
for every native new source row and all |M|<=2.
In particular no F_k has GF3 degree-three refutation.

THIS DOES NOT ESTABLISH NECESSARY DEGREE GROWTH:
proven lower bound is >=4 throughout. No general P != NP
lower bound or general polynomial SAT solver. P_VS_NP=OPEN.
"""
from __future__ import annotations
from itertools import combinations
from collections import deque
from r5_universal_cubic_flow_lowmoment_collision_20v import flower
from r5_universal_cubic_edgecolor_direct_scl_bridge import (
    make_scl,validate_cubic_graph
)
from r5_universal_exact_support_residual_dag_attack import validate_sparse
from r5_universal_infinite_connected_scl_degree3_dual_two_edge_sum import (
    frozen_native_j5_dual,
    source_homomorphism_verifier,
    source_dual_replay_with_mapping
)


def native_three_edge_connectivity(G):
    """Independently check every ORIGINAL graph cut with <=2 edges."""
    V,E=validate_cubic_graph(G)
    n=len(V)
    adj={v:[] for v in V}
    for i,(a,b) in enumerate(E):
        adj[a].append((b,i));adj[b].append((a,i))
    def connected_without(blocked):
        seen={0};stack=[0]
        while stack:
            for w,i in adj[stack.pop()]:
                if i in blocked or w in seen:continue
                seen.add(w);stack.append(w)
        return len(seen)==n
    assert connected_without(set())
    for i in range(len(E)):
        assert connected_without({i}),("bridge",i)
        for j in range(i):
            assert connected_without({i,j}),("2-edge-cut",i,j)
    return True


def triangle_expand_vertex_source(G):
    """Construct source-certified Delta vertex expansion and phi."""
    V,E=validate_cubic_graph(G)
    assert native_three_edge_connectivity(E)
    old_rows,old_n,old_edges,old_idx=make_scl(E)
    N=len(V)
    v=N-1
    old_incident=tuple(sorted(e for e in E if v in e))
    assert len(old_incident)==3
    old_neighbors=tuple(e[0] if e[1]==v else e[1]
                        for e in old_incident)
    assert len(set(old_neighbors))==3
    new_t=(v,N,N+1)
    E_new=set(E)-set(old_incident)
    extern={}
    for j,u in enumerate(old_neighbors):
        edge=tuple(sorted((u,new_t[j])))
        assert edge not in E_new
        E_new.add(edge)
        extern[edge]=j
    internal={}
    for i,j in combinations(range(3),2):
        edge=tuple(sorted((new_t[i],new_t[j])))
        assert edge not in E_new
        E_new.add(edge)
        missing=3-i-j
        internal[edge]=missing
    new_edges=tuple(sorted(E_new))
    assert len(new_edges)==len(E)+3
    assert len({u for e in new_edges for u in e})==N+2
    assert native_three_edge_connectivity(new_edges)
    new_rows,new_n,source_edges,new_idx=make_scl(new_edges)
    assert new_n==old_n+9
    phi=[-1]*new_n
    for e in source_edges:
        for color in range(3):
            if e in E and e not in old_incident:
                ancestor=e
            elif e in extern:
                ancestor=old_incident[extern[e]]
            elif e in internal:
                ancestor=old_incident[internal[e]]
            else:
                raise AssertionError(("uncategorized source edge",e))
            phi[new_idx[(e,color)]]=old_idx[(ancestor,color)]
    assert all(v>=0 for v in phi)
    phi=tuple(phi)
    assert source_homomorphism_verifier(
        old_rows,old_n,new_rows,new_n,phi
    )
    return new_edges,new_rows,new_n,phi


def main():
    base,n,G,base_keys,base_dual=frozen_native_j5_dual()
    assert native_three_edge_connectivity(G)
    source=base
    map_to_base=tuple(range(n))
    for k in range(1,5):
        G,nxt,nnew,step=triangle_expand_vertex_source(G)
        assert nnew==90+9*k
        assert source_homomorphism_verifier(
            source,n,nxt,nnew,step
        )
        map_to_base=tuple(map_to_base[j] for j in step)
        assert source_homomorphism_verifier(
            base,90,nxt,nnew,map_to_base
        )
        if k<=3:
            checked=source_dual_replay_with_mapping(
                nxt,nnew,map_to_base,base_keys,base_dual
            )
            print(f"TRIANGLE_INFLATION_K{k}_CONNECTED_3EDGECONNECTED_"
                  f"SCL{nnew}_UNSAT_NO_GF3_V3="
                  f"ALL_{checked}_ORIGINAL_GENERATORS_VERIFIED",
                  flush=True)
            # A forged pullback must be rejected by unrelated
            # original row source validation.
            invalid=list(map_to_base)
            j=nxt[0][0]
            invalid[j]=(invalid[j]+1)%90
            try:
                source_homomorphism_verifier(
                    base,90,nxt,nnew,tuple(invalid)
                )
            except AssertionError:
                print(f"TRIANGLE_INFLATION_SCL{nnew}_"
                      "FORGED_SOURCE_MAP_REJECTED",flush=True)
            else:
                raise AssertionError("forged source map accepted")
        else:
            print(f"TRIANGLE_INFLATION_K{k}_SCL{nnew}_"
                  "SOURCE_DEGREE_ONE_RETRACTION_VERIFIED",flush=True)
        source,n=nxt,nnew

    print("INFINITE_3EDGE_CONNECTED_ORIGINAL_SCL_N90_PLUS9K_"
          "UNSAT_AND_NO_GF3_DEGREE3_REFUTATION=PROVED")
    print("UNBOUNDED_NATIVE_GF3_PC_DEGREE=NOT_PROVED")
    print("UNIVERSAL_POLY_SOLVELINEARCUBICXSAT=NOT_CONSTRUCTED")
    print("P_VS_NP=OPEN")


if __name__=="__main__":
    main()
