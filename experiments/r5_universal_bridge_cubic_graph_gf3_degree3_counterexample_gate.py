#!/usr/bin/env python3
"""R5 decisive original legal SCL degree-three TEST: cubic BRIDGE graphs.

A connected cubic graph G with a bridge is NOT 3-edge-colourable:
each colour class is a perfect matching. Removing any bridge
disconnects into TWO ODD-vertex sets because the sum of cubic
degrees in one side is 3|U|=2|E(U)|+1, so |U| odd. Each perfect
matching must cross an odd cut in an odd number of edges; only
one edge crosses, so EACH of THREE colour classes requires that
same bridge, impossible.

Build a family of simple cubic graphs by subdividing one edge
in two disjoint bridgeless 3-regular graphs H and adding an
edge between subdivision vertices. The added edge is a BRIDGE,
all degrees remain 3 and G simple. Base choices K4 (N=4),
K33 (N=6), cube Q3 (N=8): resulting G has N=10/14/18 and
native Holyer source F has 45/63/81 variables and clauses.

Original DIRECT Holyer source consists of variables x_(edge,color),
one ExactOne3 clause for each edge, and 3 ExactOne3 clauses per
graph vertex, all ORIGINAL square, cubic and C4-free linear.

For degree3 frozen Boolean PC over F3, compute exact span of
multilinear E_i*x_M, |M|<=2. If 1 is ABSENT, reconstruct source-
verifiable dual y with y(1)=1 and y(E_i*x_M)=0 for EVERY original
SCL clause and multiplier.

Pair proof:
 A. Independently source-verify G simple, cubic, unique declared
    bridge, both sides odd, and exact original-source Holyer map.
    This establishes ACTUAL UNSAT.
 B. Independently replay dual directly against ALL ORIGINAL source
    generators. This establishes NO DEGREE3 REFUTATION in frozen V3.

This pair, if found, is a strict counterexample to universal
V3 completeness, NOT a general P!=NP lower bound.
If resource exhausted or 1 in span report only observations.
"""
from __future__ import annotations
from collections import deque
from r5_universal_cubic_edgecolor_direct_scl_bridge import (
    K4,K33,cube_graph,make_scl,validate_cubic_graph
)
from r5_universal_gf3_boolean_degree3_pc_probe import (
    degree3_source_span,verify_dual_source,multilinear_monomials
)
from r5_universal_exact_support_residual_dag_attack import validate_sparse


def build_two_cubic_sides_bridge(H):
    H=tuple(sorted(tuple(sorted(e)) for e in H))
    vertices,edges=validate_cubic_graph(H)
    v=len(vertices)
    assert v%2==0
    edge=edges[0]
    result=[]
    for copy in (0,1):
        offset=copy*(v+1)
        bridge_vertex=offset+v
        for a,b in edges:
            if (a,b)==edge:
                result.append((offset+a,bridge_vertex))
                result.append((offset+b,bridge_vertex))
            else:
                result.append((offset+a,offset+b))
    result.append((v,2*v+1))
    result=tuple(tuple(sorted(e)) for e in result)
    vertices,out=validate_cubic_graph(result)
    return out,(v,2*v+1),v


def components_after_edge_cut(edges,cut):
    vertices,edges=validate_cubic_graph(edges)
    assert cut in edges
    adj={v:set() for v in vertices}
    for a,b in edges:
        if (a,b)==cut:continue
        adj[a].add(b);adj[b].add(a)
    components=[]
    unseen=set(vertices)
    while unseen:
        root=min(unseen)
        seen={root};todo=[root]
        while todo:
            for w in adj[todo.pop()]:
                if w not in seen:
                    seen.add(w);todo.append(w)
        components.append(frozenset(seen))
        unseen.difference_update(seen)
    return tuple(components)


def independent_original_unsat_bridge_proof(H,source,n,bridge):
    from collections import Counter
    vertices,edges=validate_cubic_graph(H)
    assert bridge in edges
    parts=components_after_edge_cut(edges,bridge)
    assert len(parts)==2 and all(len(p)%2 for p in parts)
    assert set().union(*parts)==set(vertices)
    crossing=[e for e in edges
              if (e[0] in parts[0]) != (e[1] in parts[0])]
    assert crossing==[bridge],crossing
    # Independently reconstruct every ORIGINAL Exact-One constraint,
    # as opposed to trusting a graph 'hard' label.
    independent,number,actual_edges,idx=make_scl(edges)
    assert n==number and actual_edges==edges
    assert validate_sparse(source,n)==independent
    # Colour classes are perfect matchings from original vertex
    # ExactOne constraints. On odd-size U, every matching must
    # use an ODD number of U-to-complement edges. Only bridge
    # crosses, so the SAME bridge must be present in all three
    # distinct colours, contrary to original edge ExactOne.
    return {"status":"ORIGINAL_SCL_UNSAT_BRIDGE_PARITY_PROVED",
            "n":n,"vertices":len(vertices),
            "bridge":bridge,"odd_parts":tuple(map(len,parts)),
            "direct_source_rows":len(independent)}


def run_case(label,H,guard=45000000):
    edges,bridge,v=build_two_cubic_sides_bridge(H)
    F,n,_,_=make_scl(edges)
    proof=independent_original_unsat_bridge_proof(edges,F,n,bridge)
    assert proof["status"]=="ORIGINAL_SCL_UNSAT_BRIDGE_PARITY_PROVED"
    print(f"SOURCE_BRIDGE_{label}_SCL{n}=PROVED_UNSAT "
          f"odd_parts={proof['odd_parts']} bridge={bridge}",
          flush=True)
    out=degree3_source_span(F,n,max_updates=guard)
    print(f"SOURCE_BRIDGE_{label}_SCL{n}_GF3_DEGREE3="
          f"{out['status']} rank={out['rank']} "
          f"ambient={out.get('ambient_dim','NA')} "
          f"updates={out['updates']} "
          f"dual_support={out.get('dual_support','NA')}",flush=True)
    if out["status"]=="DEGREE3_NO_REFUTATION_DUAL_CERTIFIED":
        mon,idx=multilinear_monomials(n,3)
        assert verify_dual_source(F,n,out["dual"],mon,idx)
        assert out["dual"][0]==1
        print(f"COUNTEREXAMPLE_TO_ALL_SCL_DEGREE3=SOURCE_CERTIFIED "
              f"GRAPH={label} n={n} dual_support={out['dual_support']}",
              flush=True)
    elif out["status"]=="DEGREE3_CONSTANT_IN_SPAN_REPLAY_REQUIRED":
        print(f"SOURCE_BRIDGE_{label}_GF3_DEGREE3_REFUTATION_CANDIDATE="
              "NOT_YET_INDEPENDENTLY_REPLAYED",flush=True)
    else:
        print(f"SOURCE_BRIDGE_{label}_DEGREE3=UNKNOWN_RESOURCE_LIMIT",
              flush=True)
    return out


def main():
    for label,H in (
        ("K4_K4",K4()),("K33_K33",K33()),
        ("Q3_Q3",cube_graph())
    ):
        result=run_case(label,H,guard=55000000)
        # Once a verified universal V3 counterexample is found,
        # do not burn runtime on larger redundant sources.
        if result["status"]=="DEGREE3_NO_REFUTATION_DUAL_CERTIFIED":
            break
        if result["status"]=="UNKNOWN_RESOURCE_LIMIT":
            print("SUBSEQUENT_CASES_NOT_REQUIRED_FOR_THIS_RESOURCE_LIMIT")
            break
    print("DEGREE3_PROBE_CONCLUSION=ONLY_CERTIFICATES_ABOVE")
    print("UNIVERSAL_POLY_LOOP_ZERO_TEST=NOT_CONSTRUCTED")
    print("UNIVERSAL_POLY_SOLVELINEARCUBICXSAT=NOT_CONSTRUCTED")
    print("P_VS_NP=OPEN")


if __name__=="__main__":
    main()
