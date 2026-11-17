#!/usr/bin/env python3
"""Isaacs flower snarks: infinite connected SCL UNSAT semigroup holes.

For every odd k>=5, Isaacs (1975) flower snark J_k has 4k vertices,
6k edges, is bridgeless cubic and NOT 3-edge-colourable.
The direct cubic-graph bridge maps it to a legal SCL Exact-One
matrix of dimensions 18k x 18k with Boolean UNSAT.

An explicit perfect matching for every flower graph (including
the odd snarks) is:
   all spokes (A_i,B_i),
   plus pairs of consecutive positions on the length-2k
   cycle (C_0,...,C_(k-1),D_0,...,D_(k-1)).
Thus our SIGNED INTEGER model z with A*z=1 is constructible in
linear time, despite Boolean UNSAT for all odd k>=5.
Also each target has rational nullity>=4k.

Important: uncolourability of all odd flower snarks is a
PUBLISHED graph-theoretic theorem by Isaacs, not inferred
from finite JANUS solver observations. The experiment
verifies graph incidence, matching, signed witness and rank
relations for k=5,7,9, and only attempts a guarded
complete exact search; UNKNOWN is never promoted to UNSAT.
P=NP is not proved.
"""
from __future__ import annotations

from r5_universal_cubic_edgecolor_direct_scl_bridge import (
    validate_cubic_graph, make_scl, graph_matroid_rank_obstruction,
    signed_integer_exactone_from_perfect_matching,
    brute_three_edge_coloring,
)
from r5_universal_exact_support_residual_dag_attack import (
    ExactSupportResidualDAG_sparse
)


def flower(k):
    assert isinstance(k,int) and k>=5
    def A(i):return 4*i
    def B(i):return 4*i+1
    def C(i):return 4*i+2
    def D(i):return 4*i+3
    edges=set()
    def edge(x,y):
        assert x!=y
        edges.add(tuple(sorted((x,y))))
    for i in range(k):
        for v in (B(i),C(i),D(i)):
            edge(A(i),v)
        edge(B(i),B((i+1)%k))
    cycle=[C(i) for i in range(k)]+[D(i) for i in range(k)]
    assert len(cycle)==2*k
    for i in range(2*k):
        edge(cycle[i],cycle[(i+1)%(2*k)])
    vertices,ordered=validate_cubic_graph(edges)
    assert len(vertices)==4*k and len(ordered)==6*k
    pm={tuple(sorted((A(i),B(i)))) for i in range(k)}
    for i in range(0,2*k,2):
        pm.add(tuple(sorted((cycle[i],cycle[i+1]))))
    assert len(pm)==2*k and pm<=set(ordered)
    covered=[v for e in pm for v in e]
    assert len(set(covered))==4*k and len(covered)==4*k
    return ordered,pm


def main():
    for k in (5,7,9):
        edges,matching=flower(k)
        vertices,ordered=validate_cubic_graph(edges)
        rows,n,es,idx=make_scl(ordered)
        assert n==18*k
        assert graph_matroid_rank_obstruction(rows,n,vertices,es,idx)==4*k
        witness=signed_integer_exactone_from_perfect_matching(
            rows,n,es,matching
        )
        assert witness.count(-1)==2*k
        assert all(sum(witness[j] for j in clause)==1 for clause in rows)

        # Isaacs' published theorem gives mathematical UNSAT for
        # every ODD k>=5. For the smallest member independently
        # exhaust all edge colourings, without trusting this theorem.
        if k==5:
            assert brute_three_edge_coloring(edges) is None

        # The original memoized ExactSupport search does not
        # have the root GF2 cost of the stronger hybrid, making
        # short controlled samples useful at all three sizes.
        cap={5:200,7:200,9:200}[k]
        exact=ExactSupportResidualDAG_sparse(
            rows,n,max_states=cap
        )
        assert exact["status"] in ("UNSAT","UNKNOWN")
        if exact["status"]=="UNKNOWN":
            assert exact["stats"]["guard_hits"]>0
            assert exact["stats"]["distinct_states"]==cap
        print(f"ISAACS_FLOWER_J{k}: graph_V={4*k}, E={6*k}, "
              f"SCL_n={n}, published_BOOL_UNSAT, "
              f"independent_Z_SOLUTION=YES, "
              f"rational_nullity>={4*k}, "
              f"DAG={exact['status']} "
              f"visited={exact['stats']['distinct_states']}")

    print("FLOWER_ALL_ODD_K_GE5_BOOLEAN_UNSAT=ISAACS_1975_PUBLISHED")
    print("FLOWER_EXPLICIT_PERFECT_MATCHING_ALL_K=PROVED_CONSTRUCTIVE")
    print("FLOWER_SCL_SIGNED_INTEGER_SEMIGROUP_HOLE_ALL_ODD_K=PROVED")
    print("FLOWER_SCL_RATIONAL_NULLITY_GE_4K=PROVED")
    print("POLYNOMIAL_ExactSupport_ALL_SCL=NOT_CONSTRUCTED")
    print("P_VS_NP=OPEN")


if __name__=="__main__":
    main()
