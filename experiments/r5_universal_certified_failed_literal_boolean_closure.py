#!/usr/bin/env python3
"""R5 exact source-certified FAILED LITERAL lookahead over GF2/ExactOne.

A sound POLYNOMIAL (not complete) strengthening of the already audited
GF2/Exact-One least fixed point. For every unknown Boolean source variable
x and each Boolean b, run the *entire* certified GF2/Exact-One fixed point
under temporary assumption x=b.

- If one branch is UNSAT, original source entails x=1-b.
- If BOTH branches are UNSAT, original source is UNSAT.
- If either branch has a checked SAT witness, source is SAT.
- Otherwise only record UNKNOWN, never turn lack of deduction into proof.

Repeat proven new pins. At most n new pins, at most 2n² conditional
probes in total. A conditional closure performs <=n+1 polynomial
Gaussian rounds; a coarse worst-case bit bound O(n^8), including
certificate replay, suffices. Unlike exact 2^n DPLL, no nested case
branches are undertaken and no exponential fallback is hidden.

The independently checked output includes EVERY UNSAT assumption
proof and a verifier that replays both the inner original-source
certificate and the assumption-discharge implication. It also
checks any claimed SAT witness on the ORIGINAL source.

A finite UNKNOWN on Petersen disproves *this* polynomial closure's
universal decision completeness, not every conceivable polynomial
closure and NOT P!=NP. Reaching SAT or UNSAT on a few sources cannot
prove the all-input polynomial theorem either.
"""
from __future__ import annotations
from r5_universal_exact_support_residual_dag_attack import validate_sparse
from r5_universal_certified_gf2_boolean_fixedpoint_closure import (
    certified_boolean_fixed_point,verify_boolean_fixed_point,
)


def check_original_witness(rows,n,initial,witness):
    assert witness is not None and len(witness)==n
    assert all(type(b) is int and b in (0,1) for b in witness)
    assert all(witness[v]==b for v,b in initial.items())
    assert all(sum(witness[v] for v in row)==1 for row in rows)
    return True


def verify_probe_certificate(rows,n,initial,report):
    """Independent assumption-discharge replay, no producer Gaussian."""
    rows=validate_sparse(rows,n)
    current=dict(initial or {})
    assert all(type(v) is int and 0<=v<n and b in (0,1)
               for v,b in current.items())
    events=report['events']
    terminated=False
    for item in events:
        kind=item['kind']
        if kind=='BASE':
            before=dict(current)
            child=item['proof']
            assert verify_boolean_fixed_point(rows,n,before,child)
            if child['status']=='UNSAT':
                assert report['status']=='UNSAT' and item is events[-1]
                terminated=True
            elif child['status']=='SAT':
                assert report['status']=='SAT' and item is events[-1]
                assert check_original_witness(rows,n,initial,child['witness'])
                terminated=True
            else:
                assert child['status']=='UNKNOWN'
                current=dict(child['pins'])
        elif kind=='PROBE':
            v=item['var']
            assert type(v) is int and 0<=v<n and v not in current
            replies=item['branches']
            assert tuple(sorted(replies))==(0,1)
            for b in (0,1):
                assumption=dict(current);assumption[v]=b
                assert verify_boolean_fixed_point(
                    rows,n,assumption,replies[b]
                )
            if item['resolution']=='SAT_WITNESS':
                b=item['witness_branch']
                assert replies[b]['status']=='SAT'
                assert report['status']=='SAT' and item is events[-1]
                assert check_original_witness(
                    rows,n,initial,replies[b]['witness']
                )
                terminated=True
            elif item['resolution']=='DOUBLE_UNSAT':
                assert all(replies[b]['status']=='UNSAT' for b in (0,1))
                assert report['status']=='UNSAT' and item is events[-1]
                terminated=True
            elif item['resolution']=='FORCED_LITERAL':
                b=item['refuted_bit']
                assert replies[b]['status']=='UNSAT'
                assert replies[1-b]['status']!='UNSAT'
                assert item['derived_pin']==(v,1-b)
                current[v]=1-b
            else:
                assert item['resolution']=='INCONCLUSIVE'
                assert all(replies[b]['status']=='UNKNOWN' for b in (0,1))
        elif kind=='END_UNKNOWN':
            assert item is events[-1]
            assert report['status']=='UNKNOWN'
            # Verifier checks all currently unset original variables
            # were probed without a contradiction IN THIS ROUND.
            # No UNKNOWN outcome is an UNSAT proof.
            assert set(item['tested_vars'])=={
                ev['var'] for ev in events[
                    item['start_event_index']: -1
                ] if ev['kind']=='PROBE'
                and ev['resolution']=='INCONCLUSIVE'
            }
            assert set(item['tested_vars'])==set(range(n))-set(current)
            terminated=True
        else:
            raise AssertionError('invalid lookahead source proof event')
        if terminated:break
    assert terminated
    assert report['status'] in ('SAT','UNSAT','UNKNOWN')
    if report['status']=='SAT':
        assert check_original_witness(
            rows,n,initial,report['witness']
        )
    else:
        assert not report.get('witness')
    assert report['certified_pins']==current or report['status']=='SAT'
    return True


def certified_failed_literal_closure(rows,n,pins=None):
    rows=validate_sparse(rows,n)
    initial=dict(pins or {})
    assert all(type(v) is int and 0<=v<n and b in (0,1)
               for v,b in initial.items())
    current=dict(initial)
    events=[]
    passes=0;probes=0
    while True:
        passes+=1
        assert passes<=n+1
        base=certified_boolean_fixed_point(rows,n,current)
        events.append({'kind':'BASE','proof':base})
        assert verify_boolean_fixed_point(rows,n,current,base)
        if base['status'] in ('SAT','UNSAT'):
            out={'status':base['status'],
                 'reason':'BASE_GF2_BOOLEAN_'+base['status'],
                 'witness':base.get('witness'),
                 'events':tuple(events),'certified_pins':dict(current),
                 'passes':passes,'probes':probes}
            assert verify_probe_certificate(rows,n,initial,out)
            return out
        current=dict(base['pins'])
        batch_begin=len(events)
        strengthened=False
        for v in range(n):
            if v in current:continue
            outcomes={}
            for b in (0,1):
                trial=dict(current);trial[v]=b
                outcomes[b]=certified_boolean_fixed_point(
                    rows,n,trial
                )
                probes+=1
            if any(outcomes[b]['status']=='SAT' for b in (0,1)):
                b=next(b for b in (0,1)
                       if outcomes[b]['status']=='SAT')
                events.append({'kind':'PROBE','var':v,
                               'branches':outcomes,
                               'resolution':'SAT_WITNESS',
                               'witness_branch':b})
                out={'status':'SAT','reason':'PROBE_SAT_WITNESS',
                     'witness':outcomes[b]['witness'],
                     'events':tuple(events),
                     'certified_pins':dict(current),
                     'passes':passes,'probes':probes}
                assert verify_probe_certificate(rows,n,initial,out)
                return out
            rejected=[b for b in (0,1)
                      if outcomes[b]['status']=='UNSAT']
            if len(rejected)==2:
                events.append({'kind':'PROBE','var':v,
                               'branches':outcomes,
                               'resolution':'DOUBLE_UNSAT'})
                out={'status':'UNSAT','reason':'BOTH_VALUES_REFUTED',
                     'events':tuple(events),
                     'certified_pins':dict(current),
                     'passes':passes,'probes':probes}
                assert verify_probe_certificate(rows,n,initial,out)
                return out
            if rejected:
                b=rejected[0]
                events.append({'kind':'PROBE','var':v,
                               'branches':outcomes,
                               'resolution':'FORCED_LITERAL',
                               'refuted_bit':b,
                               'derived_pin':(v,1-b)})
                current[v]=1-b
                strengthened=True
                break
            events.append({'kind':'PROBE','var':v,
                           'branches':outcomes,
                           'resolution':'INCONCLUSIVE'})
        if not strengthened:
            tested=tuple(x['var'] for x in events[batch_begin:]
                         if x['kind']=='PROBE')
            events.append({'kind':'END_UNKNOWN',
                           'start_event_index':batch_begin,
                           'tested_vars':tested})
            out={'status':'UNKNOWN',
                 'reason':'ALL_SINGLE_ASSUMPTIONS_GF2_BOOLEAN_INCONCLUSIVE',
                 'events':tuple(events),'certified_pins':dict(current),
                 'passes':passes,'probes':probes}
            assert verify_probe_certificate(rows,n,initial,out)
            return out


def main():
    from r5_universal_cubic_edgecolor_direct_scl_bridge import (
        make_scl,K4,K33,petersen_graph,
    )
    from r5_universal_atomic_gf4_cycle_cut_fourier_duality import (
        bridged_cubic_graph,
    )
    from r5_universal_all_odd_cyclic_pc2_four_orbit_identity import cyclic
    from r5_universal_modular_flow_count_all_q_no_go import prism
    from r5_e61_two_level_kernel_hoffman_regular_set import (
        build_A,P_SAT,Q_SAT,P_UNSAT,Q_UNSAT,
    )
    def e61_rows(p,q):
        A=build_A(p,q)
        return validate_sparse(
            [tuple(i for i,v in enumerate(row) if v) for row in A],
            len(A),
        )
    cases=(
        ('SAT_K4',make_scl(K4())[0],'SAT'),
        ('SAT_K33',make_scl(K33())[0],'SAT'),
        ('SAT_PRISM3',make_scl(prism(3)[1])[0],'SAT'),
        ('SAT_PRISM5',make_scl(prism(5)[1])[0],'SAT'),
        ('UNSAT_PETERSEN',make_scl(petersen_graph())[0],'UNSAT'),
        ('UNSAT_BRIDGE',make_scl(bridged_cubic_graph())[0],'UNSAT'),
        ('UNSAT_FANO',cyclic(7),'UNSAT'),
        ('SAT_E61',e61_rows(P_SAT,Q_SAT),'SAT'),
        ('UNSAT_E61',e61_rows(P_UNSAT,Q_UNSAT),'UNSAT'),
    )
    for label,rows,truth in cases:
        n=len(rows)
        report=certified_failed_literal_closure(rows,n)
        assert report['status'] in ('SAT','UNSAT','UNKNOWN')
        assert report['status']=='UNKNOWN' or report['status']==truth
        assert verify_probe_certificate(rows,n,{},report)
        print('FAILED_LITERAL_GF2_BOOLEAN '
              f'name={label} n={n} truth={truth} '
              f'answer={report["status"]} '
              f'passes={report["passes"]} probes={report["probes"]}',
              flush=True)
    k4,n,_,_=make_scl(K4())
    pinned=certified_failed_literal_closure(k4,n,{0:1})
    assert pinned['status'] in ('SAT','UNKNOWN')
    assert verify_probe_certificate(k4,n,{0:1},pinned)
    print(f'PINNED_K4_SINGLE_LOOKAHEAD={pinned["status"]}',flush=True)
    # Alter an independently checked source GF2 proof nested in a
    # conditional branch; the complete outer proof must fail.
    petersen=certified_failed_literal_closure(
        make_scl(petersen_graph())[0],45
    )
    branches=[i for i,item in enumerate(petersen['events'])
              if item['kind']=='PROBE']
    assert branches
    idx=branches[0];e=petersen['events'][idx]
    tampered=dict(e)
    bad=dict(e['branches'])
    first=dict(bad[0])
    first['status']='UNSAT'
    bad[0]=first
    tampered['branches']=bad
    events=list(petersen['events']);events[idx]=tampered
    forged=dict(petersen);forged['events']=tuple(events)
    denied=False
    try:
        verify_probe_certificate(
            make_scl(petersen_graph())[0],45,{},forged
        )
    except (AssertionError,KeyError):
        denied=True
    assert denied
    print('FORGED_SINGLE_LOOKAHEAD_BRANCH_PROOF_REJECTED=PASS')
    print('POLYNOMIAL_CERTIFIED_SINGLE_ASSUMPTION_CLOSURE=PROVED')
    print('GLOBAL_ALL_INPUT_SCL_COMPLETENESS=NOT_PROVED')
    print('UNIVERSAL_POLY_SOLVELINEARCUBICXSAT=NOT_CONSTRUCTED')
    print('P_VS_NP=OPEN')


if __name__=='__main__':
    main()
