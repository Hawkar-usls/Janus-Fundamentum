#!/usr/bin/env python3
"""JANUS R5 scalable polynomial-budget coverage ladder (NO new solver claim).

For eleven independent-source exact controls, rerun SAME certified
cooperative portfolio with increasing worst-case polynomial state
budgets B(n)=0, n, n*n, and compare against independently grounded
SAT/UNSAT. Every tested budget is polynomially bounded, whereas
full proof+SAT fallback is NOT used.

A finite success proves precisely those eleven instances, not the
global n^O(1) coverage theorem. Keep UNKNOWN visible.
"""
from __future__ import annotations
import json
from r5_universal_certified_portfolio_coverage_matrix import fixtures
from r5_universal_certified_expert_portfolio import SolveLinearCubicXSAT_Portfolio


def main():
    outcomes=[]
    for name,rows,n,truth,authority in fixtures():
        reports=[]
        for label,budget in (('ZERO',0),('LINEAR',n),('QUADRATIC',n*n)):
            result=SolveLinearCubicXSAT_Portfolio(
                rows,n,poly_only=True,pc3_max_n=48,
                bounded_states=budget,
            )
            assert result['status'] in ('SAT','UNSAT','UNKNOWN')
            assert result['status']=='UNKNOWN' or result['status']==truth
            if result['status']=='SAT':
                w=result['witness']
                assert w is not None and len(w)==n
                assert all(sum(w[v] for v in row)==1 for row in rows)
            reports.append({'budget':label,'limit':budget,
                'status':result['status'],'expert':result['expert']})
            print(f'POLY_LADDER {name} budget={label} '
                  f'states={budget} status={result["status"]} '
                  f'expert={result["expert"]}',flush=True)
        outcomes.append({'name':name,'size':n,'truth':truth,
                         'truth_authority':authority,'passes':reports})
    assert len(outcomes)==11
    print('POLY_BUDGET_COVERAGE_LADDER_JSON='+json.dumps(
        outcomes,sort_keys=True,separators=(',',':')),flush=True)
    print('FINITE_BUDGET_LADDER_PROOF_STATUS=OBSERVATION_ONLY')
    print('UNIVERSAL_POLY_SOLVER=NOT_CONSTRUCTED')
    print('P_VS_NP=OPEN')


if __name__=='__main__':
    main()
