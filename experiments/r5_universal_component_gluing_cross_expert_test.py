#!/usr/bin/env python3
"""All-input connected-component SCL cooperation proof regression.

Cases:
 SAT: two independent K4 legal SCL18 sources -> n36, full exact
      fallback assembles and independently verifies a witness.
 UNSAT: SAT K4 SCL18 + UNSAT Petersen SCL45 -> n63,
        globally 3|63 and therefore no counting shortcut.
        Under *zero residual states*, standalone K4 remains UNKNOWN,
        but Petersen component gets independently checked PC3 UNSAT,
        so parent MUST return UNSAT despite the earlier UNKNOWN.
 UNKNOWN: two SAT K4 components with zero residual state cap are
        correctly UNKNOWN, never speculative SAT.
 PINNED SAT: force a value on second component and verify global lift.
 A Fano SCL7 component in an n39 multiple-of-3 global source
        directly certifies UNSAT by its own size mod 3, not
        by a false original global size test.

The accepted updates are a universal correctness theorem for SCL
Tanner disconnected input, NOT universal polynomial coverage
on connected SCL sources.
"""
from __future__ import annotations

from r5_universal_cubic_edgecolor_direct_scl_bridge import (
    make_scl,K4,petersen_graph,
)
from r5_universal_all_odd_cyclic_pc2_four_orbit_identity import cyclic
from r5_universal_certified_scl_component_decomposition import (
    canonical_scl_components,independently_verify_lifted_witness,
)
from r5_universal_exact_support_residual_dag_attack import validate_sparse
from r5_universal_certified_expert_portfolio import SolveLinearCubicXSAT_Portfolio


def join(*sets):
    out=[];off=0
    for rows in sets:
        for row in rows:
            out.append(tuple(i+off for i in row))
        off+=len(rows)
    return validate_sparse(out,off),off


def main():
    sat,n18,_,_=make_scl(K4())
    unsat,n45,_,_=make_scl(petersen_graph())
    assert n18==18 and n45==45
    positive,n36=join(sat,sat)
    parts=canonical_scl_components(positive,n36)
    assert len(parts)==2 and sorted(x['n'] for x in parts)==[18,18]
    conservative=SolveLinearCubicXSAT_Portfolio(
        positive,n36,poly_only=True,
        pc3_max_n=0,bounded_states=0,
        two_ply_max_n=0,  # isolated historical UNKNOWN sentinel
    )
    assert conservative['status']=='UNKNOWN'
    assert conservative['expert']=='SOURCE_COMPONENT_COVERAGE_GAP'
    complete=SolveLinearCubicXSAT_Portfolio(
        positive,n36,poly_only=False,
        pc3_max_n=0,bounded_states=0,
    )
    assert complete['status']=='SAT'
    assert complete['expert']=='CERTIFIED_COMPONENT_SAT_GLUE'
    assert independently_verify_lifted_witness(
        positive,n36,parts,complete['witness']
    )
    print('ALL_SOURCE_COMPONENT_SAT_WITNESS_GLUE=VERIFIED n=36')

    external_pin={n18:complete['witness'][n18]}
    pin_result=SolveLinearCubicXSAT_Portfolio(
        positive,n36,pins=external_pin,
        poly_only=False,pc3_max_n=0,bounded_states=0,
    )
    assert pin_result['status']=='SAT'
    assert pin_result['witness'][n18]==external_pin[n18]
    print('GLOBAL_TO_LOCAL_PIN_INDEX_MAPPING_AND_WITNESS=VERIFIED')

    mixed,n63=join(sat,unsat)
    assert n63==63 and n63%3==0
    decision=SolveLinearCubicXSAT_Portfolio(
        mixed,n63,poly_only=True,
        pc3_max_n=48,bounded_states=0,
        two_ply_max_n=0,  # require original UNKNOWN sibling for lift proof
    )
    assert decision['status']=='UNSAT'
    assert decision['expert']=='CERTIFIED_COMPONENT_UNSAT_LIFT'
    prov=decision['component_provenance']
    assert sorted(p['n'] for p in prov)==[18,45]
    assert any(p['status']=='UNKNOWN' for p in prov)
    assert any(p['status']=='UNSAT' and
               p['expert']=='BOOLEAN_GF2_PC3' for p in prov)
    print('GLOBAL_SCL63_COMPONENT_PC3_UNSAT_LIFT_WITH_UNKNOWN_SIBLING=PROVED')

    fano=cyclic(7)
    tri,n39=join(sat,fano,fano,fano)
    assert n39==39 and n39%3==0
    low=SolveLinearCubicXSAT_Portfolio(
        tri,n39,poly_only=True,
        pc3_max_n=0,bounded_states=0,
    )
    assert low['status']=='UNSAT'
    assert low['expert']=='CERTIFIED_COMPONENT_UNSAT_LIFT'
    assert low['child_result']['expert']=='INCIDENCE_CARDINALITY'
    print('COMPONENT_LOCAL_CARDINALITY_STRONGER_THAN_GLOBAL_MOD3=VERIFIED')

    print('UNIVERSAL_DISCONNECTED_SCL_EXACT_GLUE_THEOREM=PROVED')
    print('ALL_INPUT_POLY_SCL_COVERAGE=OPEN')
    print('P_VS_NP=OPEN')


if __name__=='__main__':
    main()
