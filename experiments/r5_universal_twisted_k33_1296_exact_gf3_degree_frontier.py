#!/usr/bin/env python3
"""R5 exhaustive ALL 6^4=1296 S3-twisted K3,3 native SCL27 normal forms.

The separately proven ALL-connected-cubic-graph S3-tree gauge
theorem eliminates every tree incidence twist by SOURCE-isomorphism,
leaving only one element of S3 for each of beta=|E|-|V|+1=4
chord edges. Thus 6^4 is a mathematically EXHAUSTIVE source
isomorphism representative set, not a statistical sample.

Original native K3,3 source has n=27 square, cubic, C4-free
positive Exact-One source rows. Enumerate ALL 1296 canonical
holonomy patterns. Independent EXACT-COVER SOURCE solver returns
either original SAT witness or replayable original source UNSAT
DAG. For UNSAT inputs, run F3 Boolean degree2 proof/dual
certificate engine; if 1 is absent from V2, independently
replay its source dual and run complete degree3, which on
small n27 should return primal candidate or independent dual.
If found, reconstruct the degree3 source primal coefficients
and independently verify actual polynomial identity 1.

The ALL-K33 finite classification does NOT establish any
uniform degree bound on larger cubic graphs or all-SCL, nor
unbounded proof degree. Resource cap means UNKNOWN, never
a proof of either result.
"""
from __future__ import annotations
from itertools import product
from r5_universal_cubic_edgecolor_direct_scl_bridge import K33,validate_cubic_graph
from r5_universal_twisted_s3_cycle_gauge_normal_forms import (
    twisted_canonical_from_chord_labels
)
from r5_universal_twisted_cubic_edge_coloring_native_scl_degree_gate import (
    signed_native_source
)
from r5_universal_gf3_degree3_adversarial_scl27_search import (
    original_source_exact_solve,verify_original_unsat_dag
)
from r5_universal_gf3_boolean_degree2_pc_frontier import (
    degree2_row_span,verify_degree2_dual_certificate
)
from r5_universal_gf3_boolean_degree3_pc_probe import (
    degree3_source_span,verify_dual_source,multilinear_monomials
)
from r5_universal_gf3_degree3_petersen_source_certificate import (
    certificate_from_dag,independent_original_certificate_replay
)


def main():
    G=K33()
    V,E=validate_cubic_graph(G)
    beta=len(E)-len(V)+1
    assert beta==4
    statuses={"SAT":0,"UNSAT_DEG2":0,"UNSAT_NO_DEG2":0,
              "UNSAT_NO_DEG3":0,"UNKNOWN_RESOURCE":0}
    hardest=None
    max_dag=0
    for labels in product(range(6),repeat=beta):
        twists=twisted_canonical_from_chord_labels(E,labels)
        rows,n,_=signed_native_source(E,twists)
        assert n==27
        truth=original_source_exact_solve(rows,n,limit=200000)
        if truth["status"]=="UNKNOWN_RESOURCE_LIMIT":
            statuses["UNKNOWN_RESOURCE"]+=1
            continue
        if truth["status"]=="SAT":
            statuses["SAT"]+=1
            assert all(sum(truth["witness"][v] for v in row)==1
                       for row in rows)
            continue
        assert truth["status"]=="UNSAT_CERTIFIED"
        assert verify_original_unsat_dag(rows,n,truth["dag"])
        max_dag=max(max_dag,truth["dag_size"])
        v2=degree2_row_span(rows,n)
        if v2["status"]=="UNSAT_DEGREE2_SOURCE_CERTIFIED":
            statuses["UNSAT_DEG2"]+=1
            continue
        assert v2["status"]=="DEGREE2_UNRESOLVED"
        assert verify_degree2_dual_certificate(
            rows,n,v2["dual_certificate"]
        )
        statuses["UNSAT_NO_DEG2"]+=1
        v3=degree3_source_span(rows,n,max_updates=100000000)
        if v3["status"]=="DEGREE3_NO_REFUTATION_DUAL_CERTIFIED":
            mono,keys=multilinear_monomials(n,3)
            assert verify_dual_source(rows,n,v3["dual"],mono,keys)
            statuses["UNSAT_NO_DEG3"]+=1
            print("FIRST_TWISTED_K33_SCL27_CERTIFIED_NO_DEG3="
                  f"labels={labels} "
                  f"source_rows={repr(rows)}",flush=True)
        elif v3["status"]=="DEGREE3_CONSTANT_IN_SPAN_REPLAY_REQUIRED":
            proof=certificate_from_dag(rows,n,max_updates=100000000)
            assert independent_original_certificate_replay(
                rows,n,proof["source_coefficient_combination"]
            )
            if hardest is None:
                hardest=(labels,proof["certificate_terms"],truth["dag_size"])
            print(f"K33_V2_COUNTEREXAMPLE_V3_SOURCE_REFUTED="
                  f"labels={labels} terms={proof['certificate_terms']}",
                  flush=True)
        else:
            statuses["UNKNOWN_RESOURCE"]+=1
    assert sum(statuses[k] for k in (
        "SAT","UNSAT_DEG2","UNSAT_NO_DEG2","UNKNOWN_RESOURCE"
    ))==6**beta
    print("ALL_1296_TWISTED_K33_SCL27_CANONICAL_CLASSES="
          f"EXHAUSTED {statuses} max_unsat_dag={max_dag} "
          f"first_d3_cert={hardest}",flush=True)
    if statuses["UNKNOWN_RESOURCE"]==0:
        print("ALL_K33_S3_TWISTED_SOURCE_TRUTH_AND_V2_STATUS="
              "EXACT_CI_CERTIFIED",flush=True)
    print("GENERAL_NATIVE_SCL_UNBOUNDED_DEGREE=NOT_PROVED")
    print("ALL_SCL_POLYNOMIAL_ZERO_TEST=NOT_CONSTRUCTED")
    print("P_VS_NP=OPEN")


if __name__=="__main__":
    main()
