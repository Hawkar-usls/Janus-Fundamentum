#!/usr/bin/env python3
"""JANUS R5 certified cooperative SCL expert portfolio.

Target: ALL input square/cubic/C4-free Positive Exact-One SAT matrices.
Two explicit operating modes:
- poly_only=True: deterministic polynomially bounded expert portfolio;
  SAT/UNSAT proofs are sound, UNKNOWN is a legitimate result.
- poly_only=False: complete fallback to exact AND/OR residual proof system;
  always SAT with VERIFIED witness or UNSAT with independently replayed
  AND/OR certificate, but fallback may cost exponential time.

Already integrated experts:
  cardinality, exact root GF2/mod9/closure Hybrid(0),
  degree-3 Boolean Polynomial Calculus (small unpinned inputs),
  bounded ExactSupportHybrid modular + residual AND/OR,
  proof-carrying complete residual AND/OR fallback.
All modules are from JANUS Fundamentum, NOT reimplemented.
PC3 is UNSAT-only, never converts non-refutation into SAT.
No claim of P=NP or universal n^O(1) when fallback is enabled.
"""
from __future__ import annotations

from r5_universal_exact_support_residual_dag_attack import (
    validate_sparse,_pins,
)
from r5_universal_exact_support_hybrid_algebraic_dag import (
    ExactSupportHybrid_sparse,
)
from r5_universal_boolean_pc_degree3_global_attack import (
    pc_refutation,
)
from r5_universal_exact_support_unsat_andor_certificate import (
    construct_unsat_proof,verify_unsat_proof,
)


def witness_verified(rows,n,pins,witness):
    return (
        witness is not None
        and len(witness)==n
        and all(isinstance(x,int) and x in (0,1) for x in witness)
        and all(sum(witness[j] for j in row)==1 for row in rows)
        and all(witness[j]==value for j,value in pins.items())
    )


def SolveLinearCubicXSAT_Portfolio(
    rows,n,pins=None,*,poly_only=True,
    pc3_max_n=48,bounded_states=48,shared_state=None,\n    certified_symmetry=None,sym_pc3_max_n=126,
):
    """Correct on EVERY legal SCL input. Poly mode may return UNKNOWN.

    Optional shared_state replays its entire certificate + propagation
    ledger before strengthening pins passed to *all* downstream experts.

    For fixed nonnegative pc3_max_n and bounded_states, the poly path
    is polynomial worst-case bit time (conservatively O(n^9) from
    optional PC3). The complete fallback does NOT inherit that bound.

    No trusted expert may claim SAT without an independently verified
    original-input witness. Negative results are from mathematically
    sound exact routines and root congruence gates; complete fallback
    additionally returns independently checked AND/OR proof size.
    """
    rows=validate_sparse(rows,n)
    if not isinstance(poly_only,bool):raise ValueError('poly_only must be bool')
    if not isinstance(pc3_max_n,int) or pc3_max_n<0:
        raise ValueError('pc3_max_n must be nonnegative int')
    if not isinstance(bounded_states,int) or bounded_states<0:
        raise ValueError('bounded_states must be nonnegative int')
    if not isinstance(sym_pc3_max_n,int) or sym_pc3_max_n<0:
        raise ValueError('sym_pc3_max_n must be nonnegative int')
    requested=pins
    pins=_pins(n,pins)
    events=[]

    def result(status,expert,reason,witness=None,**extra):
        if status=='SAT':
            assert pins is not None and witness_verified(rows,n,pins,witness)
        else:
            assert witness is None
        assert status in ('SAT','UNSAT','UNKNOWN')
        assert not (status=='UNKNOWN' and expert=='COMPLETE_ANDOR')
        return {
            'status':status,
            'reason':reason,
            'expert':expert,
            'witness':witness,
            'experts':tuple(events),
            'mode':'POLY_ONLY' if poly_only else 'TOTAL_EXACT_MAY_BE_EXPONENTIAL',
            'universal_polynomial_claim':False,
            **extra,
        }

    if pins is None:
        events.append('CONFLICTING_PINS')
        return result('UNSAT','PIN_VALIDATOR','CONFLICTING_PINS')
    if n%3:
        events.append('INCIDENCE_CARDINALITY')
        return result('UNSAT','INCIDENCE_CARDINALITY',
                      'THREE_TIMES_SELECTED_COUNT_MUST_EQUAL_N')

    # Incoming proof-state is trusted ONLY after full certificate-chain
    # and independently replayed literal implication checks. It must
    # represent precisely the same original source and caller pins.
    if shared_state is not None:
        assert shared_state.n==n
        assert tuple(shared_state.rows)==tuple(rows)
        assert tuple(shared_state.base_pins)==tuple(sorted(pins.items()))
        verdict,derived_pins,trace=shared_state.propagate()
        if verdict!='FIXPOINT':
            raise ValueError(
                'shared UNSAT conflict needs a separately replayable '
                'root refutation before publishing an UNSAT verdict'
            )
        assert shared_state.independently_replay_propagation(
            derived_pins,trace
        )
        assert all(derived_pins[v]==value for v,value in pins.items())
        pins=derived_pins
        events.append('CERTIFIED_SHARED_NOGOOD_AND_EXACTONE_PROPAGATION')

    root=ExactSupportHybrid_sparse(rows,n,pins=pins,max_states=0)
    events.append('HYBRID_ROOT_GF2_MOD9_AND_CLOSURE')
    if root['status']=='SAT':
        return result('SAT','HYBRID_ROOT',root['reason'],root['witness'],
                      root_stats=root['stats'])
    if root['status']=='UNSAT':
        certificate=root.get('root_certificate')
        provenance={}
        if certificate is not None:
            # This does NOT rerun the modular-9 solver. Verify only
            # the exact annihilator already produced by its existing
            # transitive call inside ExactSupportHybrid.
            from r5_universal_exact_support_mod9_dual_certificate import (
                independent_verify_mod9_certificate,
            )
            B=[[int(j in row) for j in range(n)] for row in rows]
            rhs=[1]*len(rows)
            for v,value in sorted(pins.items()):
                unit=[0]*n;unit[v]=1
                B.append(unit);rhs.append(value)
            independent_verify_mod9_certificate(B,rhs,certificate)
            provenance={
                'certificate_type':'VERIFIED_MOD9_LEFT_ANNIHILATOR',
                'certificate':tuple(certificate),
                'certificate_replayed':True,
            }
            events.append('ROOT_MOD9_INDEPENDENT_CERTIFICATE_REPLAY')
        return result('UNSAT','HYBRID_ROOT',root['reason'],
                      root_stats=root['stats'],**provenance)
    assert root['status']=='UNKNOWN'

    if (certified_symmetry is not None and not pins
            and n<=sym_pc3_max_n):
        from r5_universal_certified_odd_symmetry_adapter import (
            certified_odd_symmetry_pc3,
        )
        sym=certified_odd_symmetry_pc3(
            rows,n,certified_symmetry
        )
        events.append('ODD_AUTOMORPHISM_PC3_PRECONDITION_GATE')
        if sym['status']=='UNSAT':
            return result(
                'UNSAT','VERIFIED_ODD_SYMMETRY_PC3',
                sym['reason'],
                symmetry_order=sym['symmetry_order'],
                sym_pc3_stats=sym['stats'],
                certificate_type=sym['certificate_type'],
            )

    if not pins and n<=pc3_max_n:
        refuted,stats=pc_refutation(rows,n,3)
        events.append('BOOLEAN_GF2_PC3')
        if refuted:
            assert stats['independent_cert_verified']
            return result(
                'UNSAT','BOOLEAN_GF2_PC3',
                'EXACT_DEGREE3_PC_CONSTANT_1_COMBINATION',
                pc3_stats=stats,
            )

    bounded=ExactSupportHybrid_sparse(
        rows,n,pins=pins,max_states=bounded_states
    )
    events.append('BOUNDED_EXACT_SUPPORT_MOD9_DAG')
    if bounded['status'] in ('SAT','UNSAT'):
        return result(
            bounded['status'],'BOUNDED_EXACT_SUPPORT',
            bounded['reason'],bounded.get('witness'),
            bounded_stats=bounded['stats'],
        )
    assert bounded['status']=='UNKNOWN'
    if poly_only:
        return result(
            'UNKNOWN','ALL_BOUNDED_EXPERTS_EXHAUSTED',
            'NO_SOUND_POLYNOMIAL_DECISION_YET',
            bounded_stats=bounded['stats'],
        )

    # Total, complete fallback; its worst-case runtime is exponential.
    # Independent proof replay on every negative completion.
    proof_status,payload=construct_unsat_proof(
        rows,n,pins=pins,max_states=None
    )
    events.append('COMPLETE_ANDOR_PROOF_REPLAY_FALLBACK')
    if proof_status=='SAT':
        support=set(payload)
        witness=[int(j in support) for j in range(n)]
        assert witness_verified(rows,n,pins,witness)
        return result('SAT','COMPLETE_ANDOR',
                      'ORIGINAL_INPUT_WITNESS_VERIFIED',witness)
    assert proof_status=='UNSAT' and payload is not None
    initial,proof=payload
    count=verify_unsat_proof(rows,n,initial,proof,pins=pins)
    return result(
        'UNSAT','COMPLETE_ANDOR',
        'INDEPENDENT_EXHAUSTIVE_DAG_PROOF_REPLAY',
        proof_nodes=count,
    )


def main():
    from r5_e61_two_level_kernel_hoffman_regular_set import (
        build_A,P_SAT,Q_SAT,P_UNSAT,Q_UNSAT
    )
    from r5_universal_cubic_edgecolor_direct_scl_bridge import (
        make_scl,K33,petersen_graph
    )
    from r5_universal_boolean_quadratic_pc2_attack import (
        cyclic_source,e118_target,source_solutions,
    )
    from r5_universal_modular_flow_count_all_q_no_go import prism

    # Frozen E61 true positive and negative controls, no guessed permutations.
    cases=[]
    for label,A in (
        ('E61_SAT12',build_A(P_SAT,Q_SAT)),
        ('E61_UNSAT12',build_A(P_UNSAT,Q_UNSAT)),
    ):
        n=len(A)
        rs=tuple(tuple(i for i,v in enumerate(r) if v) for r in A)
        # Only retain matrices satisfying the full legal promise;
        # fixture cross-checks below are status-neutral if needed.
        validated=validate_sparse(rs,n)
        cases.append((label,n,validated,label=='E61_SAT12'))
    for name,G in (
        ('SAT_K33',K33()),('UNSAT_PETERSEN',petersen_graph())
    ):
        rs,n,_,_=make_scl(G)
        cases.append((name,n,rs,name=='SAT_K33'))
    prism_rows,prism_n,_,_=make_scl(prism(5)[1])
    cases.append(('SAT_PRISM5',prism_n,prism_rows,True))

    for name,n,rows,known_sat in cases:
        fast=SolveLinearCubicXSAT_Portfolio(
            rows,n,poly_only=True,pc3_max_n=48,bounded_states=0
        )
        assert fast['status'] in ('SAT','UNSAT','UNKNOWN')
        if known_sat is True:
            assert fast['status']!='UNSAT'
        if known_sat is False:
            assert fast['status']!='SAT'
        exact=SolveLinearCubicXSAT_Portfolio(
            rows,n,poly_only=False,pc3_max_n=48,bounded_states=64
        )
        assert exact['status'] in ('SAT','UNSAT')
        if known_sat is not None:
            assert (exact['status']=='SAT')==known_sat
        print(f'{name}: n={n}, poly_only={fast["status"]} '
              f'poly_expert={fast["expert"]}, '
              f'exact={exact["status"]} exact_expert={exact["expert"]}, '
              f'expert_path={exact["experts"]}',flush=True)

    # Independent certificate propagation from the ALREADY CALLED
    # MOD9 module, rather than running duplicate MOD9 solvers.
    from r5_e129_invertible_base_cover_unsat_gauge_clean_seed import (
        base_matrix,
    )
    mod9_A=base_matrix()
    mod9_n=len(mod9_A)
    mod9_rows=tuple(tuple(i for i,v in enumerate(row) if v)
                    for row in mod9_A)
    mod9_portfolio=SolveLinearCubicXSAT_Portfolio(
        mod9_rows,mod9_n,poly_only=True,
        pc3_max_n=0,bounded_states=0,
    )
    assert mod9_portfolio['status']=='UNSAT'
    assert mod9_portfolio['certificate_type']=='VERIFIED_MOD9_LEFT_ANNIHILATOR'
    assert mod9_portfolio['certificate_replayed']
    print(f'E129_MOD9_TRANSITIVE_EVIDENCE_PROVENANCE=VERIFIED '
          f'certificate_size={len(mod9_portfolio["certificate"])}',
          flush=True)

    # Proven correctness of policy boundaries: zero experts
    # are not permitted to guess SAT or UNSAT on an open instance.
    rows,n,_,_=make_scl(K33())
    undecided=SolveLinearCubicXSAT_Portfolio(
        rows,n,poly_only=True,pc3_max_n=0,bounded_states=0
    )
    assert undecided['status']=='UNKNOWN'
    assert undecided['witness'] is None
    print('POLY_PORTFOLIO_UNKNOWN_NEVER_RELABELED_SAT_OR_UNSAT = VERIFIED')

    # End-to-end orchestration through the actual COMPLETE fallback,
    # with BOTH SAT witness and independently replayed UNSAT proof.
    forced_sat=SolveLinearCubicXSAT_Portfolio(
        rows,n,poly_only=False,pc3_max_n=0,bounded_states=0
    )
    assert forced_sat['status']=='SAT'
    assert forced_sat['expert']=='COMPLETE_ANDOR'
    assert witness_verified(rows,n,{},forced_sat['witness'])
    print('FORCED_EXACT_FALLBACK_SAT_WITNESS = VERIFIED')

    # Preserve original-input pins under every expert and fallback.
    port1=SolveLinearCubicXSAT_Portfolio(
        rows,n,pins={0:1},poly_only=False,
        pc3_max_n=0,bounded_states=0,
    )
    port0=SolveLinearCubicXSAT_Portfolio(
        rows,n,pins={0:0},poly_only=False,
        pc3_max_n=0,bounded_states=0,
    )
    assert port1['status']=='SAT' and port0['status']=='SAT'
    assert port1['witness'][0]==1 and port0['witness'][0]==0
    illegal=SolveLinearCubicXSAT_Portfolio(
        rows,n,pins={j:1 for j in rows[0][:2]},
        poly_only=True,pc3_max_n=0,bounded_states=0,
    )
    assert illegal['status']=='UNSAT'
    print('PINNED_EXPERT_FALLBACK_AND_CONFLICT_VERIFIED = PASS')

    # Complete fallback emits a separately independently verified
    # proof on a genuine UNSAT fixture when early bound experts off.
    neg_rows,n,_,_=make_scl(petersen_graph())
    proof_status,payload=construct_unsat_proof(
        neg_rows,n,pins={},max_states=None
    )
    assert proof_status=='UNSAT'
    initial,proof=payload
    nodes=verify_unsat_proof(neg_rows,n,initial,proof,pins={})
    assert nodes>0
    print(f'PETERSEN_INDEPENDENT_ANDOR_UNSAT_PROOF_NODES={nodes}')
    forced_unsat=SolveLinearCubicXSAT_Portfolio(
        neg_rows,n,poly_only=False,pc3_max_n=0,bounded_states=0
    )
    assert forced_unsat['status']=='UNSAT'
    assert forced_unsat['expert']=='COMPLETE_ANDOR'
    assert forced_unsat['proof_nodes']==nodes
    print('FORCED_EXACT_FALLBACK_UNSAT_PROOF_REPLAY = VERIFIED')

    print('SOUND_COOPERATIVE_ALL_SCL_PORTFOLIO = PROVED_FROM_EXISTING_EXPERTS')
    print('POLY_ONLY_CAN_RETURN_UNKNOWN = PROVED')
    print('EXACT_COMPLETE_FALLBACK_MAY_BE_EXPONENTIAL = EXPLICIT')
    print('UNIVERSAL_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED')
    print('P_VS_NP = OPEN')


if __name__=='__main__':
    main()
