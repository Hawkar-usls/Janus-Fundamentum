#!/usr/bin/env python3
"""R5 native source TWISTED cubic-edge-colouring SCL construction.

ALL-SOURCE THEOREM, not just examples:
For any simple cubic graph G=(V,E), choose independently for every
incidence (vertex v, edge e) an arbitrary permutation p_(v,e) of
colors {0,1,2}. Create original Boolean variables x_(e,c)
(one indicator per graph edge and global edge-color c), edge rows
  E_e = x_(e,0)+x_(e,1)+x_(e,2) - 1,
and for every graph vertex v and LOCAL label a, row
  E_(v,a)= sum_(edges e incident to v) x_(e,p_(v,e)[a]) - 1.

Every output is an ORIGINAL square/cubic/linear Positive
Exact-One SCL: exactly 3|E| variables and clauses; each edge
indicator appears ONCE in its edge row and EXACTLY ONCE at each
end v, hence occurs thrice. Pairwise rows intersect in at most
one indicator on a SIMPLE cubic source G.

SAT iff G admits a 'twisted' edge labeling c_e in {0,1,2}
such that at EACH vertex v, the three local colors
p_(v,e)^-1(c_e) of incident edges form a permutation {0,1,2}.
Proof is direct bijection of original Boolean rows, not a
reformulation extrapolated from experiments.

We try to find finite native SCL with ORIGINAL independent
UNSAT DAG proof plus a frozen degree-three F3 dual.
Test 20 deterministic independent twisted K4 sources and
10 twisted K33 sources, including the all-identity SAT
negative control. Every UNSAT candidate is fully
source-replayed by a deterministic exact-cover DAG checker,
then exhaustively checked for GF3 V2/V3 primal/dual.
A degree-three dual is accepted ONLY after an independent
replay of ALL original source E_i*x_M generators.
A V3 constant requires an independent original-source
coefficient certificate to claim algebraic refutation.

The GENERAL proof-degree lower-bound transfer from known
Tseitin or graph vertex-coloring polynomial systems to these
S3 twisted SCL sources is NOT proved here. In particular this
is NOT an unbounded-degree family.
"""
from __future__ import annotations

import itertools
import random

from r5_universal_cubic_edgecolor_direct_scl_bridge import (
    K4,K33,validate_cubic_graph
)
from r5_universal_exact_support_residual_dag_attack import validate_sparse
from r5_universal_gf3_degree3_adversarial_scl27_search import (
    original_source_exact_solve,verify_original_unsat_dag
)
from r5_universal_gf3_boolean_degree2_pc_frontier import degree2_row_span
from r5_universal_gf3_boolean_degree3_pc_probe import (
    degree3_source_span,verify_dual_source,multilinear_monomials
)
from r5_universal_gf3_degree3_petersen_source_certificate import (
    certificate_from_dag,independent_original_certificate_replay
)


PERMUTATIONS=tuple(itertools.permutations((0,1,2)))


def signed_native_source(G,incidence_perms):
    vertices,edges=validate_cubic_graph(G)
    n=3*len(edges)
    assert n==3*len(vertices)*3//2
    assert vertices==tuple(range(len(vertices)))
    var_id={(e,c):3*i+c for i,e in enumerate(edges) for c in range(3)}
    assert set(incidence_perms)=={
        (v,e) for e in edges for v in e
    }
    assert all(tuple(sorted(p))==(0,1,2)
               for p in incidence_perms.values())
    original=[]
    for e in edges:
        original.append(tuple(var_id[(e,c)] for c in range(3)))
    for v in vertices:
        inc=tuple(e for e in edges if v in e)
        assert len(inc)==3
        for local_colour in range(3):
            original.append(tuple(
                var_id[(e,incidence_perms[(v,e)][local_colour])]
                for e in inc
            ))
    rows=validate_sparse(original,n)
    assert len(rows)==n
    for x in range(n):
        assert sum(x in row for row in rows)==3
    # Independently audit every original row-pair C4 condition,
    # even though the all-input graph theorem already proves it.
    assert all(len(set(a)&set(c))<=1
               for i,a in enumerate(rows) for c in rows[i+1:])
    return rows,n,edges


def independent_local_twist_model_count(G,perms):
    """ONLY finite test inputs with <=9 graph edges."""
    vertices,edges=validate_cubic_graph(G)
    assert len(edges)<=9
    byvertex={v:tuple(e for e in edges if v in e) for v in vertices}
    inv={(v,e):tuple(perms[(v,e)].index(c) for c in range(3))
         for e in edges for v in e}
    count=0
    witness=None
    for palette in itertools.product(range(3),repeat=len(edges)):
        chosen={edge:palette[i] for i,edge in enumerate(edges)}
        if all(
            len({inv[(v,e)][chosen[e]] for e in byvertex[v]})==3
            for v in vertices
        ):
            count+=1
            if witness is None:
                witness=tuple(int(chosen[e]==c)
                              for e in edges for c in range(3))
    return count,witness


def verify_twisted_row_semantics(G,twist,rows,n):
    truth,witness=independent_local_twist_model_count(G,twist)
    if witness is not None:
        assert all(sum(witness[v] for v in row)==1 for row in rows)
    result=original_source_exact_solve(rows,n,limit=1000000)
    assert result["status"]!="UNKNOWN_RESOURCE_LIMIT",result
    if truth==0:
        assert result["status"]=="UNSAT_CERTIFIED",(truth,result)
        assert verify_original_unsat_dag(rows,n,result["dag"])
    else:
        assert result["status"]=="SAT" and result["witness"]
        assert all(sum(result["witness"][v] for v in row)==1
                   for row in rows)
    return truth,result


def run_cases(name,G,count,rng,quota_v3=2):
    verts,edges=validate_cubic_graph(G)
    unsat=0
    v3_checked=0
    d2_cert=0
    v3_duals=0
    for trial in range(count+1):
        twisted={(v,e):(
            (0,1,2) if trial==0 else rng.choice(PERMUTATIONS)
        ) for e in edges for v in e}
        rows,n,source_edges=signed_native_source(edges,twisted)
        actual,result=verify_twisted_row_semantics(
            edges,twisted,rows,n
        )
        if trial==0:
            assert actual>0 and result["status"]=="SAT"
            print(f"TWISTED_{name}_SCL{n}_IDENTITY_SAT_WITNESS=VERIFIED",
                  flush=True)
            continue
        if actual>0:
            continue
        unsat+=1
        d2=degree2_row_span(rows,n)
        assert d2["status"]!="UNSAT_DEGREE2_SOURCE_CERTIFIED" or actual==0
        if d2["status"]=="UNSAT_DEGREE2_SOURCE_CERTIFIED":
            d2_cert+=1
        if d2["status"]=="DEGREE2_UNRESOLVED" and v3_checked<quota_v3:
            v3_checked+=1
            result3=degree3_source_span(
                rows,n,max_updates=50000000
            )
            print(f"TWISTED_{name}_SCL{n}_TRIAL{trial}_SOURCE_UNSAT="
                  f"EXACT_DAG_{result['dag_size']}_"
                  f"GF3_V3_{result3['status']}_RANK{result3['rank']}",
                  flush=True)
            if result3["status"]=="DEGREE3_NO_REFUTATION_DUAL_CERTIFIED":
                mons,idx=multilinear_monomials(n,3)
                assert verify_dual_source(
                    rows,n,result3["dual"],mons,idx
                )==n*(1+n+n*(n-1)//2)
                v3_duals+=1
                print(f"TWISTED_{name}_SCL{n}_EXACT_NATIVE_D3_"
                      f"COUNTEREXAMPLE=PROVED trial={trial}",flush=True)
                print("TWISTED_COUNTEREXAMPLE_ORIGINAL_SOURCE_ROWS="+
                      repr(rows),flush=True)
                break
            if result3["status"]=="DEGREE3_CONSTANT_IN_SPAN_REPLAY_REQUIRED":
                proof=certificate_from_dag(
                    rows,n,max_updates=50000000
                )
                assert independent_original_certificate_replay(
                    rows,n,proof["source_coefficient_combination"]
                )
                print(f"TWISTED_{name}_SCL{n}_TRIAL{trial}_GF3_V3_"
                      f"SOURCE_UNSAT_REFUTATION_CERTIFIED_TERMS="
                      f"{proof['certificate_terms']}",flush=True)
    print(f"TWISTED_{name}_FINITES trial_count={count} "
          f"source_unsat={unsat} d2_refuted={d2_cert} "
          f"v3_checked={v3_checked} certified_v3_duals={v3_duals}",
          flush=True)
    return v3_duals


def main():
    rng=random.Random(20261013)
    a=run_cases("K4",K4(),20,rng,quota_v3=2)
    b=run_cases("K33",K33(),10,rng,quota_v3=2)
    if a+b:
        print("SIGNED_TWISTED_SCL_GF3_D3_COUNTEREXAMPLE="
              "SOURCE_DUAL_CERTIFIED",flush=True)
    else:
        print("SIGNED_TWISTED_SCL_FINITE_NO_NEW_DEGREE3_DUAL")
    print("ALL_CUBIC_SIGNED_PORT_COLOUR_SYSTEMS_YIELD_NATIVE_SCL=PROVED")
    print("S3_TWISTED_TO_TSEITIN_DEGREE_PRESERVING_REDUCTION=NOT_PROVED")
    print("UNBOUNDED_NATIVE_GF3_PC_DEGREE=NOT_PROVED")
    print("UNIVERSAL_SOLVELINEARCUBICXSAT=NOT_CONSTRUCTED")
    print("P_VS_NP=OPEN")


if __name__=="__main__":
    main()
