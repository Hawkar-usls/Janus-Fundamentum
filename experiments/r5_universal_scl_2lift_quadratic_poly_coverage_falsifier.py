#!/usr/bin/env python3
"""R5 certificate-safe polynomial quadratic coverage falsifier, 2-lifts.

Construct legal (square cubic linear C4-free) 2-covers of *genuine*
source matrices using existing audited JANUS 2-lift code:
 - E123 Tutte12 q63 UNSAT parent;
 - Petersen SCL45 UNSAT parent.

IMPORTANT: a 2-cover of an UNSAT positive Exact-One source need NOT be
UNSAT, because lifted integer/half-integral parity constructions can
create Boolean solutions. Therefore NO truth is inferred from the
parent for a lift. The only required ground truth for the key
claim 'this fixed bounded solver is incomplete' is that the lifted
instance is a legal SCL input, independently validated by checker.

A solver returning UNKNOWN at B=n^2 is a reproducible finite
counterexample to ALL-INPUT COMPLETENESS FOR THIS EXACT PROFILE.
This is NOT a counterexample to an UNKNOWN different polynomial
algorithm or an n^3, n^4, etc budget.
"""
from __future__ import annotations
import json,os
from random import Random

from r5_universal_exact_support_2lift_visited_dag_frontier import two_lift
from r5_universal_cubic_edgecolor_direct_scl_bridge import make_scl,petersen_graph
from r5_e64_connected_postquotient_nullity_firewall import tutte12_incidence
from r5_universal_exact_support_residual_dag_attack import validate_sparse
from r5_universal_certified_expert_portfolio import SolveLinearCubicXSAT_Portfolio


def source(name,seed):
    if name=='TUTTE63':
        A=tutte12_incidence()
        n=len(A)
        original=validate_sparse([
            tuple(j for j,v in enumerate(row) if v) for row in A
        ],n)
    elif name=='PETERSEN45':
        original,n,_,_=make_scl(petersen_graph())
    else:raise ValueError(name)
    lifted=two_lift(original,n,Random(seed))
    return validate_sparse(lifted,2*n),2*n


def main():
    name=os.environ.get('SOURCE','TUTTE63')
    seed=int(os.environ.get('SEED','9421'))
    rows,n=source(name,seed)
    rec=[]
    for label,budget in [('ROOT_ONLY',0),('QUADRATIC',n*n)]:
        result=SolveLinearCubicXSAT_Portfolio(
            rows,n,poly_only=True,pc3_max_n=0,
            bounded_states=budget
        )
        assert result['status'] in ('SAT','UNSAT','UNKNOWN')
        if result['status']=='SAT':
            assert all(sum(result['witness'][v] for v in row)==1
                       for row in rows)
        stats=result.get('bounded_stats',result.get('root_stats',{}))
        one={'base':name,'seed':seed,'n':n,'budget':label,
             'limit':budget,'status':result['status'],
             'expert':result['expert'],
             'visited':stats.get('residual_states'),
             'guard_hits':stats.get('guard_hits'),
             'authority':'INDEPENDENT_VALID_LEGAL_SCL_SOURCE'}
        rec.append(one)
        print('SCL_2LIFT_QUADRATIC_PORTFOLIO_CHALLENGE='+json.dumps(
            one,sort_keys=True),flush=True)
    if rec[-1]['status']=='UNKNOWN':
        print('THIS_EXACT_N_SQUARED_PORTFOLIO_PROFILE_ALL_INPUT_COMPLETENESS=REFUTED_FINITE')
    else:
        print('THIS_EXACT_PROFILE_CURRENT_LIFT_RESOLVED_FINITE_ONLY')
    print('ALL_POSSIBLE_POLYNOMIAL_EXPERT_COVERAGE = OPEN')
    print('P_VS_NP = OPEN')


if __name__=='__main__':
    main()
