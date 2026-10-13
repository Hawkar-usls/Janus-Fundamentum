#!/usr/bin/env python3
"""R5 targeted asymptotic coverage challenge: pinned triangular torus.

The predecessor proof establishes that the legal torus
C_(i,j)={x_(i,j),x_(i+1,j),x_(i,j+1)}, L multiple 3, has exactly
three phase-colour SAT assignments; fixing (0,0)=1 and
(L//2,L//2+1)=1 selects two INCOMPATIBLE phases and is UNSAT.
Each pin separately is SAT. This is connected square cubic linear.

We DO NOT invent independent exhaustive truth for huge n:
the exact UNSAT authority is the archived Fourier predecessor.
This run challenges the modern portfolio's actual bounded
ExactSupportHybrid root and residual DAG under polynomial
budgets, not merely enumerating reachable but unvisited states.

UNKNOWN is an acceptable observation, not a false UNSAT.
No finite UNSAT success establishes universal quadratic state bound.
"""
from __future__ import annotations
from r5_universal_kettani_2025_toroidal_treewidth_counterexample import (
    toroidal_triangular_carrier,
)
from r5_universal_exact_support_residual_dag_attack import validate_sparse
from r5_universal_certified_expert_portfolio import SolveLinearCubicXSAT_Portfolio
from r5_universal_exact_support_pinned_torus_unsat_frontier import periodic_witness


def check_source(L):
    assert L%3==0 and L>=9
    n=L*L
    rows=validate_sparse(toroidal_triangular_carrier(L),n)
    site_a=0
    site_b=(L//2)*L+(L//2+1)
    models=[periodic_witness(L,c) for c in range(3)]
    assert all(all(sum(w[j] for j in row)==1 for row in rows)
               for w in models)
    assert sum(w[site_a] for w in models)==1
    assert sum(w[site_b] for w in models)==1
    assert all(not(w[site_a] and w[site_b]) for w in models)
    # The predecessor proves the three periodic assignments are ALL
    # satisfying assignments, not inferred from finite enumeration.
    return rows,n,{site_a:1,site_b:1}


def main():
    data=[]
    for L in (9,12,15):
        rows,n,pins=check_source(L)
        for label,budget in (
            ('LINEAR',n),
            ('QUADRATIC_WITH_RESOURCE_CEILING',min(n*n,12000)),
        ):
            r=SolveLinearCubicXSAT_Portfolio(
                rows,n,pins=pins,poly_only=True,pc3_max_n=0,
                bounded_states=budget
            )
            assert r['status'] in ('UNSAT','UNKNOWN')
            report={
                'torus_L':L,'n':n,'budget_label':label,
                'budget':budget,'observed':r['status'],
                'expert':r['expert'],
                'certifying_fourier_source':
                    'r5_universal_exact_support_pinned_torus_unsat_frontier.py',
                'claim_ceiling':'FINITE_STRESS_ONLY',
            }
            data.append(report)
            print('PINNED_TORUS_GLOBAL_COVERAGE_ATTACK='+str(report),
                  flush=True)
    print('TOTAL_PINNED_TORUS_CONTROLS='+str(len(data)))
    print('ANY_POLY_N2_UNIVERSAL_DECIDER = NOT_PROVED')
    print('ALL_INPUT_UNIVERSAL_SCL_SOLVER = NOT_CONSTRUCTED')
    print('P_VS_NP = OPEN')


if __name__=='__main__':
    main()
