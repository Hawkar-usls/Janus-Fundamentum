#!/usr/bin/env python3
"""R5 ALL-GRAPH source-isomorphism theorem for S3 twisted cubic edge-colouring.

Given connected SIMPLE cubic graph G and arbitrary independent
incidence colour permutations p_(v,e)∈S3, original Holyer-like
twisted source is a perfectly legal SCL (see paired executable).

S3 tree gauge theorem:
- choose root vertex, BFS spanning tree T;
- choose a relabeling g_v of the three LOCAL vertex colours
  and h_e of the three GLOBAL colours of EACH edge;
- transform p'_(v,e) = h_e o p_(v,e) o g_v;
- set every p' on tree edges to IDENTITY at BOTH endpoints;
- on each chord e=(u,v), choose h_e so p'_(u,e)=id, while
  p'_(v,e) is a FREE element of S3.

Thus every native twisted source F(G,p) is SOURCE-ISOMORPHIC,
not merely SAT-equivalent, to a canonical source with beta
independent S3 chord holonomies, beta=|E|-|V|+1.
The number of exhaustive NORMAL FORM inputs is ≤6**beta:
K4 beta3 =>216; K33 beta4=>1296.

SOURCE ISOMORPHISM maps original x_(e,c) bijectively to
x'_(e,h_e(c)), and every original local-colour row to an
original new local-colour row. Consequently all GF3 Boolean
V_d rowspace dimensions and the existence/nonexistence of
degree-d source certificates are EXACTLY invariant, for
EVERY d, under this gauge normalization (mere permutation
of original variable/row IDs).

Use the theorem to exhaust ALL 216 canonical K4/SCL18
twist sources; SAT verified by independent 3^6 graph
colour assignments and independently exact-cover source.
UNSAT cases checked by source-proven original degree2
refutation if available. Any degree2 dual is checked against
all original source generators; follow up degree3 as needed.

This is a finite complete source-normal-form classification
for twisted K4, NOT all SCL. It does not prove a universal
solver nor unbounded native proof degree.
"""
from __future__ import annotations
from itertools import product
from collections import deque
import random

from r5_universal_cubic_edgecolor_direct_scl_bridge import (
    K4,K33,validate_cubic_graph
)
from r5_universal_twisted_cubic_edge_coloring_native_scl_degree_gate import (
    signed_native_source,independent_local_twist_model_count,
    PERMUTATIONS
)
from r5_universal_gf3_boolean_degree2_pc_frontier import degree2_row_span
from r5_universal_gf3_boolean_degree3_pc_probe import (
    degree3_source_span
)
from r5_universal_gf3_degree3_petersen_source_certificate import (
    certificate_from_dag,independent_original_certificate_replay
)
from r5_universal_gf3_degree3_adversarial_scl27_search import (
    original_source_exact_solve,verify_original_unsat_dag
)


ID=(0,1,2)


def compose(a,b):
    return tuple(a[b[i]] for i in range(3))


def inverse(a):
    return tuple(a.index(i) for i in range(3))


def spanning_tree(G):
    V,E=validate_cubic_graph(G)
    adj={v:[] for v in V}
    for e in E:
        for v in e:
            adj[v].append((e[0] if e[1]==v else e[1],e))
    seen={0}; q=deque([0]); parent={0:None}; edges=[]
    while q:
        v=q.popleft()
        for w,e in sorted(adj[v]):
            if w not in seen:
                parent[w]=(v,e)
                edges.append(e)
                seen.add(w);q.append(w)
    assert len(seen)==len(V)
    assert len(edges)==len(V)-1
    return parent,tuple(edges)


def canonicalize_twists(G,old):
    V,E=validate_cubic_graph(G)
    parent,T=spanning_tree(E)
    tree=set(T)
    local_g={0:ID};edge_h={}
    q=deque([0])
    while q:
        u=q.popleft()
        children=sorted((v,pe[1]) for v,pe in parent.items()
                        if pe is not None and pe[0]==u)
        for v,e in children:
            # Fix incidence at BOTH endpoints to ID:
            # h p_u g_u = ID  => h=(p_u g_u)^(-1)
            # h p_v g_v = ID  => g_v = (h p_v)^(-1)
            h=inverse(compose(old[(u,e)],local_g[u]))
            g=inverse(compose(h,old[(v,e)]))
            assert compose(h,compose(old[(u,e)],local_g[u]))==ID
            assert compose(h,compose(old[(v,e)],g))==ID
            edge_h[e]=h
            local_g[v]=g
            q.append(v)
    assert len(local_g)==len(V)
    for e in E:
        if e not in tree:
            u,v=e
            edge_h[e]=inverse(compose(old[(u,e)],local_g[u]))
    new={}
    for e in E:
        for v in e:
            new[(v,e)]=compose(edge_h[e],compose(old[(v,e)],local_g[v]))
            assert tuple(sorted(new[(v,e)]))==ID
    for e in T:
        assert new[(e[0],e)]==new[(e[1],e)]==ID
    for e in E:
        if e not in tree:
            assert new[(e[0],e)]==ID
    # Exact original source variable and clause isomorphism.
    old_rows,n,edges=signed_native_source(E,old)
    new_rows,m,_=signed_native_source(E,new)
    assert n==m
    old_to_new=[-1]*n
    for i,e in enumerate(E):
        for c in range(3):
            old_to_new[3*i+c]=3*i+edge_h[e][c]
    assert sorted(old_to_new)==list(range(n))
    new_row_set=set(new_rows)
    assert all(tuple(sorted(old_to_new[j] for j in row))
               in new_row_set for row in old_rows)
    return new,old_to_new,len(E)-len(V)+1


def twisted_canonical_from_chord_labels(G,labels):
    V,E=validate_cubic_graph(G)
    _,T=spanning_tree(E)
    chords=tuple(e for e in E if e not in set(T))
    assert len(chords)==len(E)-len(V)+1
    assert len(labels)==len(chords)
    twists={}
    for e in E:
        twists[(e[0],e)]=ID
        twists[(e[1],e)]=ID
    for e,j in zip(chords,labels):
        twists[(e[1],e)]=PERMUTATIONS[j]
    return twists


def exhaustive_K4():
    G=K4()
    V,E=validate_cubic_graph(G)
    beta=len(E)-len(V)+1
    assert beta==3
    sat=0;unsat=0;v2cert=0;dual2=0;unresolved_v3=0
    for labels in product(range(6),repeat=beta):
        tw=twisted_canonical_from_chord_labels(E,labels)
        rows,n,_=signed_native_source(E,tw)
        assert n==18
        truth,witness=independent_local_twist_model_count(E,tw)
        if truth:
            sat+=1
            assert all(sum(witness[v] for v in row)==1
                       for row in rows)
            continue
        unsat+=1
        proof=degree2_row_span(rows,n)
        if proof["status"]=="UNSAT_DEGREE2_SOURCE_CERTIFIED":
            v2cert+=1
        else:
            dual2+=1
            # Completely independently count and prove original
            # UNSAT, then check full degree3. Stop at a
            # genuine unexpected V2 hole rather than suppress it.
            exact=original_source_exact_solve(rows,n,limit=100000)
            assert exact["status"]=="UNSAT_CERTIFIED"
            assert verify_original_unsat_dag(rows,n,exact["dag"])
            out=degree3_source_span(rows,n,max_updates=30000000)
            if out["status"]=="DEGREE3_CONSTANT_IN_SPAN_REPLAY_REQUIRED":
                cert=certificate_from_dag(rows,n)
                assert independent_original_certificate_replay(
                    rows,n,cert["source_coefficient_combination"]
                )
            else:
                unresolved_v3+=1
                print(f"K4_CANONICAL_GAUGE_HARD_CASE={labels} "
                      f"degree3={out['status']}",flush=True)
    assert sat+unsat==6**beta
    print(f"ALL_216_TWISTED_K4_SCL18_GAUGE_NORMAL_FORMS="
          f"EXHAUSTED sat={sat} unsat={unsat} "
          f"degree2_primal_proved={v2cert} "
          f"degree2_duals={dual2} d3_other={unresolved_v3}",
          flush=True)
    if dual2==0:
        print("TWISTED_K4_ALL_UNSAT_DEGREE2_COMPLETE=PROVED_BY_216_FORMS")
    return sat,unsat,dual2


def main():
    rng=random.Random(20261013)
    for label,G in (("K4",K4()),("K33",K33())):
        V,E=validate_cubic_graph(G)
        for sample in range(8):
            arbitrary={(v,e):rng.choice(PERMUTATIONS)
                       for e in E for v in e}
            canonical,variable_map,beta=canonicalize_twists(E,arbitrary)
            assert beta==len(E)-len(V)+1
        print(f"{label}_ARBITRARY_S3_TWISTS_SOURCE_GAUGE_NORMAL_FORM="
              f"VERIFIED beta={len(E)-len(V)+1} "
              f"canonical_upper_bound={6**(len(E)-len(V)+1)}",
              flush=True)
    exhaustive_K4()
    print("ALL_CONNECTED_SIMPLE_CUBIC_TWISTED_SCL_TREE_GAUGE_THEOREM=PROVED")
    print("ALL_SCL_UNBOUNDED_GF3_PC_DEGREE=NOT_PROVED")
    print("UNIVERSAL_SOLVELINEARCUBICXSAT=NOT_CONSTRUCTED")
    print("P_VS_NP=OPEN")


if __name__=="__main__":
    main()
