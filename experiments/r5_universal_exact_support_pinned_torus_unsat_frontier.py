#!/usr/bin/env python3
"""Pinned toroidal SAT-carrier contradiction: actual visited DAG stress.

Let L>=9 be a multiple of 3. The legal SCL toroidal system
  x_(i,j)+x_(i+1,j)+x_(i,j+1)=1
has exactly three Boolean models, one per residue class (i-j)%3
(Fourier proof in the frozen Kettani audit).
Pin x_(0,0)=1 and x_(L//2,L//2+1)=1. The residues differ
(0 vs -1), so BOTH pins together are UNSAT, while either alone
is SAT. The two sites are separated by Theta(L) grid distance.

This family has exact independent mathematical verdicts, unlike
random 2-lifts whose SAT status may be UNKNOWN.

Experiment: replay the original frozen deterministic
ExactSupportResidualDAG with these pins. A guard returns UNKNOWN,
never a speculative UNSAT. Numeric state counts are finite
observations, not an n^omega(1) lower bound.
"""
from __future__ import annotations

from r5_universal_kettani_2025_toroidal_treewidth_counterexample import (
    toroidal_triangular_carrier
)
from r5_universal_exact_support_residual_dag_attack import (
    validate_sparse, ExactSupportResidualDAG_sparse
)


def periodic_witness(L,residue):
    return [
        int((i-j-residue)%3==0)
        for i in range(L) for j in range(L)
    ]


def main():
    for L in (9,12,15,18,21,24):
        assert L%3==0
        n=L*L
        rows=validate_sparse(toroidal_triangular_carrier(L),n)
        a=0
        b=(L//2)*L+(L//2+1)
        assert a!=b and (L//2-(L//2+1))%3==2
        witnesses=[periodic_witness(L,residue) for residue in (0,1,2)]
        assert all(
            all(sum(w[v] for v in row)==1 for row in rows)
            for w in witnesses
        )
        assert witnesses[0][a]==1
        assert sum(w[a] for w in witnesses)==1
        assert any(w[b] for w in witnesses)
        assert not any(w[a] and w[b] for w in witnesses)
        # Every Boolean model belongs to the three periodic vectors,
        # as proved in frozen Fourier theorem. This certifies pair UNSAT.
        cap={9:6000,12:8000,15:10000,18:6000,21:2500,24:1500}[L]
        result=ExactSupportResidualDAG_sparse(
            rows,n,pins={a:1,b:1},max_states=cap
        )
        assert result["status"] in ("UNSAT","UNKNOWN"),(L,result["status"])
        stats=result["stats"]
        if result["status"]=="UNKNOWN":
            assert stats["distinct_states"]==cap and stats["guard_hits"]>=1
        else:
            assert result["witness"] is None
        # Pin individually stays SAT, checked on L<=15 and
        # witnessed analytically for every size.
        if L<=15:
            one=ExactSupportResidualDAG_sparse(
                rows,n,pins={a:1},max_states=cap
            )
            two=ExactSupportResidualDAG_sparse(
                rows,n,pins={b:1},max_states=cap
            )
            assert one["status"]=="SAT" and two["status"]=="SAT"
        print(f"PINNED_TORUS L={L} n={n} "
              f"pins=({a}=1,{b}=1) math_UNSAT, "
              f"solver={result['status']} "
              f"ACTUAL_S={stats['distinct_states']} cap={cap} "
              f"components={stats['component_splits']} "
              f"cache_hits={stats['cache_hits']}")
    print("TOROIDAL_TWO_INCOMPATIBLE_PINS_UNSAT=PROVED_BY_3_MODEL_THEOREM")
    print("ACTUAL_VISITED_RESIDUAL_DAG=FINITE_MEASUREMENT")
    print("SUPERPOLY_LOWER_BOUND=NOT_PROVED")
    print("POLY_UPPER_BOUND=NOT_PROVED")
    print("UNIVERSAL_ExactSupport=NOT_CONSTRUCTED; P_VS_NP=OPEN")


if __name__=="__main__":
    main()
