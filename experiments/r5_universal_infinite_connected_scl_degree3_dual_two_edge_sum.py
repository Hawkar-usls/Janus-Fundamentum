#!/usr/bin/env python3
"""R5 INFINITE CONNECTED ORIGINAL-SCL NO-V3 family — exact source proof.

Starting from native J5 flower SCL90, attach any number of properly
3-edge-coloured K4 graphs by a CUBIC GRAPH TWO-EDGE-SUM, i.e.
delete one edge e=(u,v) of current bridgeless graph G and the
color-0 edge f=(0,1) of a disjoint properly 3-edge-coloured K4;
add edges (u,new0),(v,new1). Repeat k times.

New graph remains simple, connected, cubic, bridgeless, with
number of vertices 20+4k, edges 30+6k. Direct original-source
Holyer construction yields a FULL legal square, cubic, C4-free
Positive Exact-One SCL F_k with n=3(30+6k)=90+18k.

ORIGINAL SOURCE UNSAT by parity of 2-edge cut: for a cubic
edge3colouring every colour is a perfect matching. On the
even-sized original G side, the number of edges of EACH colour
crossing the cut is even. Exactly two edges cross; both must
share one colour. Restoring e with that colour 3-colours G.
This contradicts J5 27-state UNSAT, inductively.

MORE IMPORTANT: exact 1-DEGREE SOURCE HOMOMORPHISM.
Choose base K4 coloring psi with psi(0,1)=0. For EVERY new
indicator x'_(edge,color), source map phi is:
 - retained G edge h : x_(h,color)
 - two cross edges  : x_(e,color)
 - internal K4 edge h with psi(h)=s :
                       x_(e,(color-s)%3)
Every new SOURCE exact-one clause E'_r=sum x'_j-1
maps literally to SOME old ORIGINAL clause E_r under phi.
For G vertices this is the old vertex row; every K4
vertex and every new edge row maps to old edge E_e.
No degree growth; images are ORIGINAL source variables,
and image of any squarefree multiplier of degree<=d-1 is
a squarefree old monomial of degree<=d-1 (duplicates collapse
under ORIGINAL Boolean ideal).

For ANY exact original GF3 V_d dual y on F, define y' on
every degree<=d multilinear monomial of F' by
   y'(x'_M) := y(x_(set(phi(M)))).
Then y'(1)=1 and for ALL ORIGINAL F' clauses r,
  y'(E'_r x'_M) = y(E_old(r) x_(set(phi(M)))) = 0.
Therefore F' has no degree-d refutation whenever F had none.
By induction there are infinitely many CONNECTED, BRIDGELESS
original legal UNSAT SCL with NO degree3 GF3 refutation,
namely n=90+18k for all k>=0.

This is a restricted-proof-system infinite counterexample
and is NOT a proof of UNBOUNDED necessary degree; the proven
lower bound remains degree >=4. P_VS_NP=OPEN.

Checks: frozen J5 6656-byte source dual (SHA256), independent
source and graph parity verification, row-by-row homomorphism,
direct ALL degree3 source equations for k=1 and k=2, and
forged mapping rejection.
"""
from __future__ import annotations
import base64
import hashlib
import zlib
from pathlib import Path
from collections import Counter,deque
from itertools import combinations
from r5_universal_cubic_flow_lowmoment_collision_20v import flower
from r5_universal_cubic_edgecolor_direct_scl_bridge import (
    make_scl,validate_cubic_graph,K4
)
from r5_universal_exact_support_residual_dag_attack import validate_sparse
from r5_universal_flower_27state_transfer_unsat_certificate import (
    verify_authenticated_flower_unsat
)
from r5_universal_flower_j5_gf3_degree3_symmetry_dual import (
    source_symmetry_actions,source_moment_orbits
)


K4_COLORS={
    (0,1):0,(2,3):0,
    (0,2):1,(1,3):1,
    (0,3):2,(1,2):2
}
FROZEN_PATH=Path(
    "research/certificates/R5_J5_SCL90_GF3_V3_ORBIT_DUAL_2026-10-13.b64z"
)
HASH="f2944e1a4fb474ebaac3aa2fcc19689139d1bee256f3f01af1f4ecebfd7c1edd"


def source_graph_connected_bridgeless(edges):
    verts,E=validate_cubic_graph(edges)
    adj={v:[] for v in verts}
    for i,(a,b) in enumerate(E):
        adj[a].append((b,i));adj[b].append((a,i))
    def seen_without(drop):
        seen={0};stack=[0]
        while stack:
            for next_v,i in adj[stack.pop()]:
                if i==drop or next_v in seen:continue
                seen.add(next_v);stack.append(next_v)
        return len(seen)
    assert seen_without(-1)==len(verts)
    assert all(seen_without(i)==len(verts) for i in range(len(E)))
    return True


def original_holyer_edge_indicators(edges):
    rows,n,canonical,idx=make_scl(edges)
    assert rows==validate_sparse(rows,n)
    return rows,n,canonical,idx


def k4_coloring_source_audit():
    assert set(K4_COLORS)==set(K4())
    for v in range(4):
        incident=[K4_COLORS[e] for e in K4_COLORS if v in e]
        assert sorted(incident)==[0,1,2]


def graft_colored_K4_once(G):
    """Exact target-source and pullback construction, no SAT oracle."""
    vertices,G=validate_cubic_graph(G)
    assert len(vertices)%2==0
    assert source_graph_connected_bridgeless(G)
    old_rows,old_n,old_edges,old_idx=original_holyer_edge_indicators(G)
    e=G[0]
    u,v=e
    N=len(vertices)
    new0,new1=N,N+1
    target_edges=set(G)-{e}
    for f in K4():
        if f==(0,1):continue
        target_edges.add((N+f[0],N+f[1]))
    target_edges.add(tuple(sorted((u,new0))))
    target_edges.add(tuple(sorted((v,new1))))
    target_edges=tuple(sorted(target_edges))
    new_rows,new_n,new_edges,new_idx=original_holyer_edge_indicators(
        target_edges
    )
    assert new_n==old_n+18 and len(new_edges)==len(old_edges)+6
    assert source_graph_connected_bridgeless(new_edges)
    idx_mapping=[None]*new_n
    for edge in new_edges:
        for color in range(3):
            if edge in G and edge!=e:
                old=old_idx[(edge,color)]
            elif edge in (
                tuple(sorted((u,new0))),tuple(sorted((v,new1)))
            ):
                old=old_idx[(e,color)]
            else:
                assert min(edge)>=N
                f=(edge[0]-N,edge[1]-N)
                assert f in K4_COLORS and f!=(0,1)
                old=old_idx[(e,(color-K4_COLORS[f])%3)]
            idx_mapping[new_idx[(edge,color)]]=old
    assert all(v is not None for v in idx_mapping)
    idx_mapping=tuple(idx_mapping)
    old_row_set=set(old_rows)
    row_mapping=[]
    for row in new_rows:
        mapped=tuple(sorted(idx_mapping[v] for v in row))
        assert mapped in old_row_set,(row,mapped,e)
        row_mapping.append(old_rows.index(mapped))
    assert len(row_mapping)==new_n
    return new_edges,new_rows,new_n,idx_mapping,tuple(row_mapping)


def source_homomorphism_verifier(old_rows,old_n,new_rows,new_n,phi):
    old_rows=validate_sparse(old_rows,old_n)
    new_rows=validate_sparse(new_rows,new_n)
    assert len(phi)==new_n and all(0<=x<old_n for x in phi)
    trusted=set(old_rows)
    for row in new_rows:
        mapped=tuple(sorted(phi[x] for x in row))
        assert mapped in trusted,("counterfeit source homomorphism",
                                 row,mapped)
    # Boolean x'^2=x' maps EXACTLY to original x^2=x.
    # All source row-monomial generators map into old
    # source row-monomial span at SAME or SMALLER degree.
    return True


def frozen_native_j5_dual():
    old,n,edges,idx=original_holyer_edge_indicators(flower(5))
    assert n==90 and verify_authenticated_flower_unsat(old,n,5)
    text=FROZEN_PATH.read_text("ascii").strip()
    raw=zlib.decompress(base64.b64decode(text,validate=True))
    assert len(raw)==6656 and hashlib.sha256(raw).hexdigest()==HASH
    acts=source_symmetry_actions(5,edges,idx,old)
    monoms,keys,oid,_=source_moment_orbits(n,acts)
    dual=tuple(raw[i] for i in oid)
    assert dual[keys[()]]==1
    assert len(monoms)==121576
    return old,n,edges,keys,dual


def source_dual_replay_with_mapping(rows,n,map_to_j5,base_keys,base_dual):
    """Standalone ALL source generator check; mapping may identify
    many distinct new variables with one J5 variable.
    """
    rows=validate_sparse(rows,n)
    assert len(map_to_j5)==n and all(0<=u<90 for u in map_to_j5)
    def moment(M):
        old=tuple(sorted({map_to_j5[v] for v in M}))
        return base_dual[base_keys[old]]
    assert moment(())==1
    total=0
    # For |M|<=2, exactly n*(1+n+C(n,2)) generators,
    # independently constructed from ORIGINAL SCL rows.
    all_M=[()]
    all_M.extend((i,) for i in range(n))
    all_M.extend(combinations(range(n),2))
    for row in rows:
        for M in all_M:
            expr=-moment(M)+sum(moment(M+(v,)) for v in row)
            assert expr%3==0,("FORGED_SOURCE_DUAL",row,M,expr%3)
            total+=1
    assert total==n*(1+n+n*(n-1)//2)
    return total


def main():
    k4_coloring_source_audit()
    root,n,G,keys,dual=frozen_native_j5_dual()
    assert source_graph_connected_bridgeless(G)
    base_n=n;old_rows=root;mapping=tuple(range(base_n))
    for k in range(1,4):
        G,target,n,local_map,row_map=graft_colored_K4_once(G)
        assert n==90+18*k
        assert source_homomorphism_verifier(
            old_rows,len(old_rows),target,n,local_map
        )
        composed=tuple(mapping[v] for v in local_map)
        assert source_homomorphism_verifier(
            root,base_n,target,n,composed
        )
        if k<=2:
            checked=source_dual_replay_with_mapping(
                target,n,composed,keys,dual
            )
            print(f"CONNECTED_SCL{n}_ORIGINAL_UNSAT_AND_NO_GF3_D3="
                  f"DUAL_SOURCE_REPLAYED_ALL_{checked}_GENERATORS",
                  flush=True)
            # Invalidate ONE native source row's image.
            forged=list(composed)
            v=target[0][0]
            forged[v]=(forged[v]+1)%base_n
            try:
                source_homomorphism_verifier(
                    root,base_n,target,n,tuple(forged)
                )
            except AssertionError:
                print(f"CONNECTED_SCL{n}_FORGED_SOURCE_MAP_REJECTED",
                      flush=True)
            else:
                raise AssertionError("forged source map accepted")
        else:
            print(f"CONNECTED_SCL{n}_NO_D3="
                  "SYMBOLIC_SOURCE_HOMOMORPHISM_PROVED",
                  flush=True)
        mapping=composed
        old_rows=target

    print("THEOREM_INFINITE_CONNECTED_BRIDGELESS_SCL_N90_PLUS18K_UNSAT"
          "_WITH_GF3_DEGREE3_DUAL=PROVED")
    print("ALL_FIXED_DEGREE3_COMPLETENESS=REFUTED_FOR_INFINITE_CONNECTED_FAMILY")
    print("UNBOUNDED_GF3_DEGREE_LOWER_BOUND=NOT_PROVED")
    print("UNIVERSAL_POLY_SOLVELINEARCUBICXSAT=NOT_CONSTRUCTED")
    print("P_VS_NP=OPEN")


if __name__=="__main__":
    main()
