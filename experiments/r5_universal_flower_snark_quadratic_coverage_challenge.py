#!/usr/bin/env python3
"""R5 Isaacs flower snark scaling attack against a POLY budget portfolio.

For each odd k >=5, Isaacs flower J_k is a non-3-edge-colourable
simple cubic graph on 4k vertices. Its direct Holyer construction is
a connected square/cubic/C4-free SCL system of dimension 18k.
The original truth is UNSAT from the classical snark theorem, not
from an unknown finite search.

No symmetry certificate is supplied to the main router. This probes
whether its generic bounded root and exact residual DAG alone can
handle an unsymmetric view with B(n)=n or n² actual expanded states.

UNKNOWN at n² would refute coverage by THIS EXACT BUDGETED
PORTFOLIO configuration (not all possible polynomial algorithms).
Even all finite SUCCESSes would NOT establish global polynomiality.
"""
from __future__ import annotations
import json,os
from r5_universal_certified_expert_portfolio import SolveLinearCubicXSAT_Portfolio
from r5_universal_cubic_edgecolor_direct_scl_bridge import make_scl
from r5_universal_cubic_flow_lowmoment_collision_20v import flower
from r5_universal_exact_support_residual_dag_attack import validate_sparse


def main():
    k=int(os.environ.get('FLOWER_K','7'))
    assert k in (5,7,9,11)
    rows,n,edges,_=make_scl(flower(k))
    rows=validate_sparse(rows,n)
    assert n==18*k
    results=[]
    for label,budget in [('LINEAR',n),('QUADRATIC',n*n)]:
        result=SolveLinearCubicXSAT_Portfolio(
            rows,n,poly_only=True,pc3_max_n=0,
            bounded_states=budget,
        )
        assert result['status'] in ('UNKNOWN','UNSAT'),(k,result)
        stats=result.get('bounded_stats',result.get('root_stats',{}))
        point={
            'k':k,'n':n,'budget':label,'limit':budget,
            'status':result['status'],'expert':result['expert'],
            'residual_states':stats.get('residual_states'),
            'guard_hits':stats.get('guard_hits'),
            'ground_truth':'UNSAT_1975_ISAACS',
            'scientific_scope':'FINITE_POLYNOMIAL_BUDGET_PROFILE'
        }
        results.append(point)
        print('FLOWER_UNSAT_POLY_COVERAGE='+json.dumps(
            point,sort_keys=True),flush=True)
    assert len(results)==2
    print('ACTUAL_N_SQUARED_BUDGET_CHECKED',flush=True)
    print('UNIVERSAL_POLY_SOLVER=NOT_CONSTRUCTED')
    print('P_VS_NP=OPEN')


if __name__=='__main__':
    main()
