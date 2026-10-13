#!/usr/bin/env python3
"""R5 native SCL degree3 counterexample strike: Petersen dot products.

Build 18-vertex simple cubic graphs via a Petersen dot product:
cut two vertex-disjoint edges in Petersen A; delete the two
endpoints of one edge in disjoint Petersen B, each removed
vertex leaving two dangling neighbors; connect the four
Petersen-A endpoints to the four dangling Petersen-B vertices
by a bijection. The resulting 18-node graph is simple cubic.

Try deterministic edge/pair patterns. If non-3-edge-colourable,
verify ORIGINAL positive SCL81 source legality, give an
independently source-replayed exact-cover UNSAT DAG, and
check the ENTIRE GF3 Boolean degree-three V3 span.

A dual y(1)=1 annihilating all 81*(1+81+C(81,2))
original generators is a CERTIFIED counterexample to
V3 completeness, ONLY if ORIGINAL exact UNSAT also proven.
If V3 contains 1, record a candidate requiring independent
original source coefficient certificate; finite search is not
all-SCL theorem.

Bipartite graph sparsity/girth and connectivity checked, no
oracle trust. No P vs NP inference beyond fixed-degree proof scope.
"""
from __future__ import annotations
from itertools import combinations,permutations
from r5_universal_cubic_edgecolor_direct_scl_bridge import (
    petersen_graph,validate_cubic_graph,make_scl,brute_three_edge_coloring
)
from r5_universal_exact_support_residual_dag_attack import validate_sparse
from r5_universal_gf3_degree3_adversarial_scl27_search import (
    original_source_exact_solve,verify_original_unsat_dag
)
from r5_universal_gf3_boolean_degree3_pc_probe import (
    degree3_source_span,verify_dual_source,multilinear_monomials
)


def dot_petersen(e1,e2,removed_edge,order):
    G=tuple(petersen_graph())
    assert e1 in G and e2 in G and removed_edge in G
    assert len(set(e1+e2))==4
    u,v=removed_edge
    dangling=tuple(
        sorted(w for a,b in G for w in (
            ((a if b==u else b) if u in (a,b) else -1),
            ((a if b==v else b) if v in (a,b) else -1)
        ) if w>=0 and w not in (u,v))
    )
    assert len(dangling)==4 and len(set(dangling))==4
    left={e for e in G if e!=e1 and e!=e2}
    right={tuple(sorted((a+10,b+10))) for a,b in G
           if a not in (u,v) and b not in (u,v)}
    endpoints=tuple(sorted(e1+e2))
    assert len(set(endpoints))==4
    assert sorted(order)==[0,1,2,3]
    wires={tuple(sorted((a,10+dangling[order[i]])))
           for i,a in enumerate(endpoints)}
    result=tuple(sorted(left|right|wires))
    # Renumber remaining vertices 0..17, respecting sides.
    remaining=sorted({x for e in result for x in e})
    assert len(remaining)==18
    ren={x:i for i,x in enumerate(remaining)}
    out=tuple(sorted(tuple(sorted((ren[a],ren[b])))
                     for a,b in result))
    assert len(out)==27
    validate_cubic_graph(out)
    return out


def is_bridgeless(G):
    G=tuple(G)
    vertices,_=validate_cubic_graph(G)
    def connected(exclude):
        rest=set(vertices);seen={0};todo=[0]
        edges={x:[] for x in vertices}
        for e in G:
            if e==exclude:continue
            a,b=e
            edges[a].append(b);edges[b].append(a)
        while todo:
            x=todo.pop()
            for v in edges[x]:
                if v not in seen:
                    seen.add(v);todo.append(v)
        return len(seen)==len(vertices)
    return all(connected(e) for e in G)


def search(max_scans=2500, max_pc=3):
    G=tuple(petersen_graph())
    scans=0
    tested=0
    seen=set()
    for e1,e2 in combinations(G,2):
        if len(set(e1+e2))!=4:continue
        for rm in G:
            for order in permutations(range(4)):
                scans+=1
                if scans>max_scans:
                    print(f"DOT_PETERSEN_SEARCH_SCAN_GUARD={scans-1}",
                          flush=True)
                    return
                edges=dot_petersen(e1,e2,rm,order)
                if edges in seen:continue
                seen.add(edges)
                if not is_bridgeless(edges):continue
                if brute_three_edge_coloring(edges) is not None:
                    continue
                rows,n,source_edges,idx=make_scl(edges)
                assert n==81 and validate_sparse(rows,n)==rows
                original=original_source_exact_solve(
                    rows,n,limit=800000
                )
                if original["status"]!="UNSAT_CERTIFIED":
                    print("DOT_PETERSEN_UNSAT_SOURCE_CONTROL="
                          f"{original['status']}",flush=True)
                    continue
                assert verify_original_unsat_dag(
                    rows,n,original["dag"]
                )
                tested+=1
                print(f"DOT_PETERSEN_SCL81_NATIVE_UNSAT="
                      f"INDEPENDENT_SOURCE_DAG_{original['dag_size']} "
                      f"case={tested} graph_edges={edges}",
                      flush=True)
                proof=degree3_source_span(
                    rows,n,max_updates=100000000
                )
                print(f"DOT_PETERSEN_SCL81_GF3_V3_{tested}="
                      f"{proof['status']} rank={proof['rank']} "
                      f"updates={proof['updates']} "
                      f"dual_support={proof.get('dual_support','NA')}",
                      flush=True)
                if proof["status"]=="DEGREE3_NO_REFUTATION_DUAL_CERTIFIED":
                    mono,ids=multilinear_monomials(n,3)
                    assert verify_dual_source(rows,n,proof["dual"],mono,ids)
                    print("NATIVE_SCL81_D3_COUNTEREXAMPLE="
                          f"PROVED_SOURCE_AND_DUAL n={n}",flush=True)
                    print("EXPLICIT_COUNTEREXAMPLE_ROWS="+str(rows),
                          flush=True)
                    return
                if proof["status"]=="UNKNOWN_RESOURCE_LIMIT":
                    print("NATIVE_SCL81_GF3_D3_RESOURCE=UNKNOWN",
                          flush=True)
                    return
                if tested>=max_pc:return
    print(f"DOT_PETERSEN_SCANNED={scans} "
          f"SOURCE_UNSAT_PC_TESTED={tested}",flush=True)


if __name__=="__main__":
    search()
    print("UNIVERSAL_DEGREE3_SCL_THEOREM=NOT_PROVED")
    print("UNIVERSAL_POLY_SOLVELINEARCUBICXSAT=NOT_CONSTRUCTED")
    print("P_VS_NP=OPEN")
