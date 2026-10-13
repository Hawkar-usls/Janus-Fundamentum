#!/usr/bin/env python3
"""JANUS R5 finite adversarial COVERAGE audit of existing expert portfolio.

Source controls span unrelated generators in the repository, including
E61, Holyer graph bridge, the E118 equality splitter, E123 q63 Tutte
12-cage, E129 modular cover, and odd-source cardinality.
The polynomial portfolio is queried with PC3 n<=48 and zero residual
DAG expansion to isolate proof-bearing ROOT gates/PC3.

UNKNOWN on an independently classified SAT/UNSAT test proves that
THIS CONFIGURATION does not cover all inputs. It does NOT disprove
all possible n^O(1) methods or any broader hypothetical portfolio.
Independent ground-truth provenance is explicitly recorded.
"""
from __future__ import annotations

import json
from r5_universal_certified_expert_portfolio import SolveLinearCubicXSAT_Portfolio
from r5_universal_exact_support_residual_dag_attack import validate_sparse
from r5_e61_two_level_kernel_hoffman_regular_set import (
    build_A,P_SAT,Q_SAT,P_UNSAT,Q_UNSAT
)
from r5_universal_cubic_edgecolor_direct_scl_bridge import (
    make_scl,K33,petersen_graph
)
from r5_universal_boolean_quadratic_pc2_attack import (
    cyclic_source,e118_target,verify_target,source_solutions
)
from r5_e64_connected_postquotient_nullity_firewall import (
    tutte12_incidence,verify_square_cubic_linear,
)
from r5_e129_invertible_base_cover_unsat_gauge_clean_seed import base_matrix
from r5_universal_modular_flow_count_all_q_no_go import prism
from r5_universal_cubic_flow_lowmoment_collision_20v import (
    flower,three_edge_colour_count,
)


def rows_from_matrix(A):
    n=len(A)
    assert all(len(row)==n for row in A)
    return validate_sparse(
        [tuple(i for i,v in enumerate(row) if v) for row in A],n
    ),n


def fixtures():
    e61_sat,n12=rows_from_matrix(build_A(P_SAT,Q_SAT))
    e61_unsat,_=rows_from_matrix(build_A(P_UNSAT,Q_UNSAT))
    yield ('E61_SAT12',e61_sat,n12,'SAT','E61_SOURCE_FROZEN')
    yield ('E61_UNSAT12',e61_unsat,n12,'UNSAT','E61_SOURCE_FROZEN')
    e129,n129=rows_from_matrix(base_matrix())
    yield ('E129_MOD9_UNSAT12',e129,n129,'UNSAT','MOD9_LEFT_ANNIHILATOR')
    graph_controls=[
       ('GRAPH_K33_SAT27',K33(),6,'SAT',12),
       ('GRAPH_PETERSEN_UNSAT45',petersen_graph(),10,'UNSAT',0),
       ('GRAPH_PRISM5_SAT45',prism(5)[1],10,'SAT',30),
       ('GRAPH_FLOWER_J5_UNSAT90',flower(5),20,'UNSAT',0),
    ]
    for name,G,nvertices,expect,ncol in graph_controls:
        # independently ground all graph-based outcomes via finite
        # exact matching/2-factor oracle, not portfolio's assertion.
        E=tuple(sorted(tuple(sorted(e)) for e in G))
        exact,_,_=three_edge_colour_count(nvertices,E)
        assert exact==ncol and (exact>0)==(expect=='SAT')
        rows,n,_,_=make_scl(G)
        yield (name,validate_sparse(rows,n),n,expect,
               'INDEPENDENT_PERFECT_MATCHING_ENUMERATION')
    for label,a,b,expect in (
       ('E118_UNSAT90',1,6,'UNSAT'),
       ('E118_SAT90',1,2,'SAT'),
    ):
        source=cyclic_source(9,a,b)
        models=source_solutions(source)
        assert bool(models)==(expect=='SAT')
        rows,ports,idx=e118_target(source)
        verify_target(rows)
        n=len(rows)
        yield(label,validate_sparse(rows,n),n,expect,
              'EXACT_2POW9_SOURCE_TRUTH_EQUIVALENT_SPLITTER')
    A=tutte12_incidence()
    verify_square_cubic_linear(A,12)
    rows,n=rows_from_matrix(A)
    yield ('E123_TUTTE12_UNSAT63',rows,n,'UNSAT',
           'E64_E123_FROZEN_EXACT_KERNEL_ENUMERATION')
    n=7
    FANO=[tuple(sorted((i,(i+1)%7,(i+3)%7))) for i in range(7)]
    yield ('FANO_CYCLIC_UNSAT7',validate_sparse(FANO,n),n,
           'UNSAT','INCIDENCE_CARDINALITY_7_NOT_DIVISIBLE_BY3')


def main():
    report=[]
    for name,rows,n,known,source in fixtures():
        solver=SolveLinearCubicXSAT_Portfolio(
            rows,n,poly_only=True,pc3_max_n=48,bounded_states=0
        )
        observed=solver['status']
        assert observed in ('SAT','UNSAT','UNKNOWN')
        assert observed=='UNKNOWN' or observed==known,(
            name,known,observed
        )
        report.append({
            'fixture':name,'n':n,'truth':known,'truth_authority':source,
            'poly_portfolio_status':observed,
            'expert':solver['expert'],
            'bounded_states':0,'pc3_max_n':48,
            'correct_if_decided':True,
            'globally_complete_inferred':False,
        })
        print(f'COVERAGE {name}: truth={known}, n={n}, '
              f'poly_status={observed}, expert={solver["expert"]}',
              flush=True)
    unknown=[x['fixture'] for x in report
             if x['poly_portfolio_status']=='UNKNOWN']
    assert len(report)==11,len(report)
    assert unknown,'expected explicit finite insufficient coverage'
    print('POLY_PORTFOLIO_COVERAGE_AUDIT='+json.dumps(
        {'fixture_count':len(report),'known_unknown':unknown,
         'rows':report},
        sort_keys=True,separators=(',',':')),flush=True)
    print('ONE_CONFIGURED_FINITE_PORTFOLIO_ALL_INPUT_COVERAGE = REFUTED_BY_UNKNOWN')
    print('ALL_POSSIBLE_POLYNOMIAL_EXPERT_COVERAGE = OPEN')
    print('UNIVERSAL_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED')
    print('P_VS_NP = OPEN')


if __name__=='__main__':
    main()
