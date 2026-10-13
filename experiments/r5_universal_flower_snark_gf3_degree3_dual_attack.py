#!/usr/bin/env python3
"""R5 cubic GF3 Boolean polynomial calculus on Isaacs FLOWER SNARK sources.

Graph G=flower(k), k odd >=5, is cubic, not 3-edge-colourable by
independently source-replayed 27-state transfer obstruction for
all odd k. The ORIGINAL positive linear cubic square SCL has
n=9*k variables via make_scl(flower(k)).

Exact n^3 Boolean multilinear PC span over F3:
 original source E_i=x_a+x_b+x_c-1 and every multiplier x_M,
 |M|<=2. If 1 NOT in span, independent dual source certificate
 y(1)=1, y(E_i*x_M)=0 for ALL original generators proves
 a genuine counterexample to uniform degree3 completeness.

Resource/time guard preserves UNKNOWN, and finding constant 1 is
only a candidate until independently source-replayed primal combo.
No extrapolation from a few odd k to universal degree bounds.
"""
from __future__ import annotations

from r5_universal_cubic_flow_lowmoment_collision_20v import flower
from r5_universal_cubic_edgecolor_direct_scl_bridge import (
    make_scl,brute_three_edge_coloring
)
from r5_universal_gf3_boolean_degree3_pc_probe import (
    degree3_source_span,verify_dual_source,multilinear_monomials
)
from r5_universal_exact_support_residual_dag_attack import validate_sparse


def main():
    for k,guard in ((5,100000000),(7,100000000)):
        G=flower(k)
        rows,n,edges,idx=make_scl(G)
        assert n==9*k
        assert validate_sparse(rows,n)==rows
        if k==5:
            assert brute_three_edge_coloring(G) is None
            print("FLOWER_J5_SCL45? no, SCL90_SOURCE_UNSAT="
                  "DIRECT_EXACT_EDGE_3COLOR_BRUTE_VERIFIED",flush=True)
        result=degree3_source_span(rows,n,max_updates=guard)
        print(f"FLOWER_J{k}_SCL{n}_GF3_BOOLEAN_DEGREE3="
              f"{result['status']} rank={result['rank']} "
              f"updates={result['updates']} "
              f"dual_support={result.get('dual_support','NA')}",
              flush=True)
        if result["status"]=="DEGREE3_NO_REFUTATION_DUAL_CERTIFIED":
            m,ids=multilinear_monomials(n,3)
            assert verify_dual_source(rows,n,result["dual"],m,ids)
            print(f"SOURCE_VERIFIED_D3_COUNTEREXAMPLE="
                  f"FLOWER_J{k}_SCL{n} dual_support={result['dual_support']}",
                  flush=True)
            break
        if result["status"]=="UNKNOWN_RESOURCE_LIMIT":
            print("FLOWER_FROZEN_DEGREE3_RESOURCE_LIMIT=UNKNOWN",
                  flush=True)
            break
    print("P_VS_NP=OPEN")
    print("UNIVERSAL_POLY_SOLVELINEARCUBICXSAT=NOT_CONSTRUCTED")


if __name__=="__main__":
    main()
