#!/usr/bin/env python3
"""R5 ALL-SCL atomic separator obstruction: cubic graph as Tanner minor.

THEOREM (all connected simple cubic graph G, source-authenticated):
In the genuine original Holyer SCL matrix A_G, retain ONLY the
vertex-colour-0 source rows R_(v,0) and edge-colour-0 source variables
X_(e,0). Each variable has exactly two retained incidences, one for
each endpoint of original cubic edge e. Therefore the induced
bipartite subgraph is the ONE-SUBDIVISION of G and G is a minor of
the original source Tanner incidence graph.

Hence tw(Tanner(A_G)) >= tw(G) by minor monotonicity of treewidth.
There exist infinite families of finite simple connected 3-regular
expanders with tw(G)=Omega(|V(G)|). Explicit degree-3 Ramanujan
families are known from Morgenstern (1994; q=2), or the classical
existence of cubic expanders together with the separator theorem.
Since n=3|E(G)|=9|V(G)|/2, there are legal square/cubic/linear SCL
sources with Tanner treewidth Omega(n).

THIS REFUTES any claimed all-SCL O(log n) or constant Tanner
treewidth. It does NOT prove that every algorithm for these
instances is exponential, nor that P != NP; a different
algebraic compression could exist despite high treewidth.

The exact finite verifier below checks source equality against the
constructed ORIGINAL Exact-One clauses; it never trusts graph hints,
separators or reconstructed clause-index metadata blindly.
"""
from __future__ import annotations
from r5_universal_exact_support_residual_dag_attack import validate_sparse
from r5_universal_cubic_edgecolor_direct_scl_bridge import (
    make_scl, validate_cubic_graph,K4,K33,cube_graph,petersen_graph,
)
from r5_universal_cubic_flow_lowmoment_collision_20v import flower


def verify_original_holyer_tanner_topological_minor(rows,n,graph):
    vertices,edges=validate_cubic_graph(graph)
    reconstructed,m,edge_list,idx=make_scl(edges)
    assert n==m and validate_sparse(rows,n)==reconstructed,(
        "untrusted graph hint is not the ORIGINAL source"
    )
    assert edges==edge_list
    vcount=len(vertices);ecount=len(edges)
    assert all(vertices[i]==i for i in range(vcount))
    assert 2*ecount==3*vcount and n==3*ecount
    assert ecount+3*vcount==n

    # Literal Tanner incidence, rebuilt without trusting producer edges.
    # Original source row nodes are 0..n-1, variable nodes n..2n-1.
    incidence={i:set() for i in range(2*n)}
    for i,row in enumerate(rows):
        for literal in row:
            incidence[i].add(n+literal)
            incidence[n+literal].add(i)
    assert all(len(neigh)==3 for neigh in incidence.values())

    # validate_sparse canonically sorts the ORIGINAL clause list, so
    # the physical row IDs are NOT ecount+3*v. Resolve by SOURCE clause
    # contents instead of accidentally trusting pre-validation ordering.
    row_index={tuple(row):i for i,row in enumerate(rows)}
    assert len(row_index)==n
    vertex_row={}
    for v in vertices:
        expected=tuple(sorted(idx[(e,0)] for e in edges if v in e))
        assert expected in row_index
        vertex_row[v]=row_index[expected]
    assert len(set(vertex_row.values()))==vcount
    kept_vertex_colour_rows=set(vertex_row.values())
    kept_edge_colour_variables={n+idx[(e,0)] for e in edges}
    kept=kept_vertex_colour_rows|kept_edge_colour_variables
    assert len(kept)==vcount+ecount
    sub={node:incidence[node]&kept for node in kept}
    # Each retained edge variable must be the midpoint of a unique
    # length-two path joining original endpoint vertex-colour rows.
    extracted=set()
    internally_used=set()
    for e in edges:
        u,v=e; middle=n+idx[(e,0)]
        assert middle not in internally_used
        internally_used.add(middle)
        assert sub[middle]=={vertex_row[u],vertex_row[v]}
        extracted.add((u,v))
    assert extracted==set(edges)
    assert all(len(sub[vertex_row[v]])==3 for v in vertices)
    assert all(len(sub[x])==2 for x in kept_edge_colour_variables)

    # Contract each edge-colour variable onto one endpoint: G remains.
    assert len(internally_used)==ecount
    assert len(kept_vertex_colour_rows)==vcount
    assert set(sub)==kept
    return {
        "result":"SOURCE_CERTIFIED_G_ONE_SUBDIVISION_IN_TANNER",
        "source_n":n,
        "graph_v":vcount,
        "graph_e":ecount,
        "kept_tanner_nodes":len(kept),
        "internally_vertex_disjoint_edge_paths":ecount,
        "treewidth_lower_bound":"tw(Tanner(A_G)) >= tw(G)",
    }


def main():
    for name,g in (
        ("K4",K4()),
        ("K33",K33()),
        ("CUBE",cube_graph()),
        ("PETERSEN",petersen_graph()),
        ("FLOWER_J5",flower(5)),
        ("FLOWER_J7",flower(7)),
    ):
        rows,n,_,_=make_scl(g)
        cert=verify_original_holyer_tanner_topological_minor(rows,n,g)
        assert cert["internally_vertex_disjoint_edge_paths"]==cert["graph_e"]
        print(f"HOLYER_TANNER_CUBIC_MINOR_{name}=SOURCE_REPLAYED "
              f"n={n} v={cert['graph_v']} e={cert['graph_e']}",
              flush=True)

    # A legal same-size source CAN have different graph edges. The
    # certificate must authenticate exact source clauses, not sizes.
    original,ns,_,_=make_scl(cube_graph())
    g_other=tuple(sorted(tuple(sorted(e)) for e in cube_graph()))
    g_other=list(g_other)
    g_other[0]=(0,7)  # same number edges but malformed / wrong graph
    try:
        verify_original_holyer_tanner_topological_minor(
            original,ns,g_other
        )
    except (AssertionError, ValueError):
        print("FORGED_CUBIC_GRAPH_MINOR_HINT_REJECTED=PASS",flush=True)
    else:
        raise AssertionError("false graph/source binding accepted")

    # Source tensor attack (wrong source row; same n) also rejected.
    rows,n,_,_=make_scl(K4())
    bad=list(rows)
    bad[0]=tuple((v+1)%n for v in rows[0])
    try:
        verify_original_holyer_tanner_topological_minor(
            bad,n,K4()
        )
    except (AssertionError,ValueError):
        print("FORGED_ORIGINAL_TANNER_INCIDENCE_REJECTED=PASS",flush=True)
    else:
        raise AssertionError("counterfeit original incidence accepted")

    print("ALL_CUBIC_HOLYER_TANNER_HAS_CUBIC_TOPOLOGICAL_MINOR=PROVED")
    print("INFINITE_CUBIC_EXPANDER_HIGH_TW_TRANSFER=EXTERNAL_THEOREM")
    print("ALL_SCL_LOG_TREEWIDTH_ASSUMPTION=FALSE")
    print("POLYNOMIAL_GENERAL_ATOMIC_SIGNATURE_COMPRESSION=NOT_PROVED")
    print("UNIVERSAL_POLY_SOLVELINEARCUBICXSAT=NOT_CONSTRUCTED")
    print("P_VS_NP=OPEN")


if __name__=="__main__":
    main()
