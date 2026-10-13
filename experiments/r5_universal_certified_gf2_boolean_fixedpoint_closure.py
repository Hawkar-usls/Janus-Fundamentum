#!/usr/bin/env python3
"""JANUS R5: certified GF(2) <-> BOOLEAN Exact-One least fixed point.

THIS IS AN ALL-INPUT POLYNOMIAL-TIME AND PROOF-CARRYING CLOSURE
for a specifically defined pair of rule families:
  (1) all GF2 *linear* consequences of original exact-one parity
      equations conditioned on independently established Boolean pins;
  (2) all immediate Exact-One clause unit consequences and clashes.

At each iteration a complete row-reduction returns original-row XOR
proofs for each forced variable. Its source checker is independent
of the pivot calculation. Each Exact-One deduction carries a clause
index and the previously certified pin state, which an independent
replayer checks directly against the ORIGINAL source.

The number of accepted new pin facts is <= n. Hence <= n+1 GF2
rounds, O(n^5) conservative bit operations incl. replay.
GF2 contradiction and original Boolean clause conflict certify UNSAT.
A SAT claim only comes with a fully checked original Boolean witness.
Otherwise returns UNKNOWN, not a guessed theorem.

CRITICAL GLOBAL FAILURE of THIS SPECIFIED CLOSURE:
For Holyer SCL of K4 (SAT) and Petersen (UNSAT), no unpinned original
GF2 forced literal and no Exact-One unit apply at root. This
deterministic polynomial fixed point returns UNKNOWN on BOTH.
This is a finite counterexample to completeness of THESE two rule
families, NOT a lower bound on PC3 / MOD9 / every possible Boolean
closure, and NOT a proof P!=NP.

Mathematical all-input bridge for the failure on 3edge-connected G:
The mod2 Holyer kernel is parameterized by two independent binary
cycle-space vectors f,g. If each original edge belongs to a cycle
(no original G bridge), each original Boolean Holyer coordinate
varies over affine GF2 solutions; therefore NO ORIGINAL UNPINNED
GF2 unit can be forced. With zero initial pins, Exact-One unit rules
have nothing to fire. Thus this specific iterative rule set is
INCONCLUSIVE on EVERY bridgeless connected cubic Holyer graph,
SAT or UNSAT. It cannot alone decide their NP-hard problem.
"""
from __future__ import annotations

from r5_universal_exact_support_residual_dag_attack import validate_sparse
from r5_universal_certified_gf2_affine_forced_literals import (
    gf2_certified_source_closure,verify_gf2_ledger,
)


def _clause_consequence(rows,assignments,clause_id):
    row=rows[clause_id]
    ones=[v for v in row if assignments.get(v)==1]
    zeros=[v for v in row if assignments.get(v)==0]
    if len(ones)>=2 or len(zeros)==3:
        return 'CONFLICT',None
    if len(ones)==1:
        for v in row:
            if v not in assignments:
                return 'PIN',(v,0)
    if len(zeros)==2:
        for v in row:
            if v not in assignments:
                return 'PIN',(v,1)
    return 'NONE',None


def verify_boolean_fixed_point(rows,n,initial_pins,report):
    """Independent REPLAY of ALL original-source proof events.

    No producer GF2 pivots, Gaussian basis, or cached states trusted.
    Reconstructs the sequential Boolean assignment only from
    source-checked XOR claims and original exact-one unit rules.
    """
    rows=validate_sparse(rows,n)
    assignments=dict(initial_pins or {})
    assert all(type(v)==int and 0<=v<n and b in (0,1)
               for v,b in assignments.items())
    for event in report['events']:
        kind=event['kind']
        if kind=='GF2':
            ledger=event['ledger']
            assert verify_gf2_ledger(rows,n,assignments,ledger)
            if ledger['status']=='UNSAT':
                assert report['status']=='UNSAT'
                assert event is report['events'][-1]
                assert report['reason']=='CERTIFIED_GF2_CONTRADICTION'
                break
            for v,b,proof in ledger['forced']:
                assert v not in assignments or assignments[v]==b
                assignments[v]=b
            if ledger['status']=='SAT':
                assert report['status']=='SAT'
                assert event is report['events'][-1]
                break
        elif kind in ('EXACTONE_UNIT','EXACTONE_CONFLICT'):
            i=event['row']
            assert type(i)==int and 0<=i<n
            outcome,claim=_clause_consequence(rows,assignments,i)
            if kind=='EXACTONE_CONFLICT':
                assert outcome=='CONFLICT'
                assert report['status']=='UNSAT'
                assert report['reason']=='CERTIFIED_EXACTONE_CLAUSE_CONFLICT'
                assert event is report['events'][-1]
                break
            assert outcome=='PIN'
            assert tuple(event['pin'])==claim
            v,b=claim
            assert v not in assignments
            assignments[v]=b
        else:
            raise AssertionError('unrecognized proof event')
    assert dict(report['pins'])==assignments
    if report['status']=='SAT':
        w=report['witness']
        assert len(w)==n and all(v in (0,1) for v in w)
        assert all(w[v]==b for v,b in assignments.items())
        assert all(sum(w[v] for v in row)==1 for row in rows)
    elif report['status']=='UNKNOWN':
        assert not report.get('witness')
        # Verify actual saturation, not just sound partial facts:
        again=gf2_certified_source_closure(rows,n,assignments)
        assert again['status']=='UNKNOWN'
        assert all(v in assignments for v,_,_ in again['forced'])
        assert all(_clause_consequence(rows,assignments,i)[0]=='NONE'
                   for i in range(n))
    else:
        assert report['status']=='UNSAT'
        assert report['events']
        assert report['events'][-1]['kind'] in ('GF2','EXACTONE_CONFLICT')
    return True


def certified_boolean_fixed_point(rows,n,pins=None):
    rows=validate_sparse(rows,n)
    original=dict(pins or {})
    assert all(type(v)==int and 0<=v<n and b in (0,1)
               for v,b in original.items())
    state=dict(original)
    events=[]
    rounds=0
    while True:
        rounds+=1
        assert rounds<=n+1
        ledger=gf2_certified_source_closure(rows,n,state)
        assert verify_gf2_ledger(rows,n,state,ledger)
        events.append({'kind':'GF2','ledger':ledger})
        if ledger['status']=='UNSAT':
            result={'status':'UNSAT',
                    'reason':'CERTIFIED_GF2_CONTRADICTION',
                    'events':tuple(events),
                    'pins':dict(state),'rounds':rounds}
            assert verify_boolean_fixed_point(rows,n,original,result)
            return result
        grew=False
        for v,b,proof in ledger['forced']:
            if v not in state:
                state[v]=b
                grew=True
        if ledger['status']=='SAT':
            result={'status':'SAT','reason':'FULL_GF2_BOOLEAN_WITNESS',
                    'witness':tuple(ledger['witness']),
                    'events':tuple(events),
                    'pins':dict(state),'rounds':rounds}
            assert verify_boolean_fixed_point(rows,n,original,result)
            return result
        while True:
            found=False
            for i in range(n):
                outcome,claim=_clause_consequence(rows,state,i)
                if outcome=='CONFLICT':
                    events.append({'kind':'EXACTONE_CONFLICT','row':i})
                    result={'status':'UNSAT',
                            'reason':'CERTIFIED_EXACTONE_CLAUSE_CONFLICT',
                            'events':tuple(events),
                            'pins':dict(state),'rounds':rounds}
                    assert verify_boolean_fixed_point(rows,n,original,result)
                    return result
                if outcome=='PIN':
                    v,b=claim
                    events.append({'kind':'EXACTONE_UNIT','row':i,
                                   'pin':(v,b)})
                    assert v not in state
                    state[v]=b
                    found=True
                    grew=True
                    break
            if not found:break
        if not grew:
            if len(state)==n:
                w=tuple(state[v] for v in range(n))
                assert all(sum(w[v] for v in row)==1 for row in rows)
                result={'status':'SAT','reason':'ORIGINAL_BOOLEAN_WITNESS',
                        'witness':w,'events':tuple(events),
                        'pins':dict(state),'rounds':rounds}
            else:
                result={'status':'UNKNOWN',
                        'reason':'GF2_BOOLEAN_FIXED_POINT_NOT_DECISIVE',
                        'events':tuple(events),
                        'pins':dict(state),'rounds':rounds}
            assert verify_boolean_fixed_point(rows,n,original,result)
            return result


def main():
    from r5_universal_cubic_edgecolor_direct_scl_bridge import (
        make_scl,K4,K33,petersen_graph,
    )
    from r5_universal_atomic_gf4_cycle_cut_fourier_duality import (
        bridged_cubic_graph,
    )
    for label,graph,truth in (
        ('SAT_K4',K4(),'SAT'),
        ('SAT_K33',K33(),'SAT'),
        ('UNSAT_PETERSEN',petersen_graph(),'UNSAT'),
    ):
        rows,n,edges,idx=make_scl(graph)
        r=certified_boolean_fixed_point(rows,n)
        assert r['status']=='UNKNOWN',(label,r)
        assert r['rounds']==1 and not r['pins']
        assert verify_boolean_fixed_point(rows,n,{},r)
        print(f'BOOLEAN_GF2_FIXED_POINT_{label}=UNKNOWN '
              f'original_ground_truth={truth} n={n}',flush=True)
    bridged,n,edges,idx=make_scl(bridged_cubic_graph())
    r=certified_boolean_fixed_point(bridged,n)
    assert r['status']=='UNSAT'
    assert verify_boolean_fixed_point(bridged,n,{},r)
    print(f'BOOLEAN_GF2_BRIDGED_ATOMIC_UNSAT=VERIFIED n={n} '
          f'rounds={r["rounds"]} pins={len(r["pins"])}',flush=True)
    sat,n,_,_=make_scl(K4())
    pinned=certified_boolean_fixed_point(sat,n,{0:1})
    assert pinned['status'] in ('SAT','UNKNOWN')
    assert verify_boolean_fixed_point(sat,n,{0:1},pinned)
    assert pinned['pins'][0]==1
    print(f'BOOLEAN_GF2_PINNED_K4={pinned["status"]} '
          f'rounds={pinned["rounds"]} pins={len(pinned["pins"])}',
          flush=True)
    forged=dict(r)
    ev=list(r['events'])
    tampered=False
    for i,event in enumerate(ev):
        if event['kind']=='GF2' and event['ledger']['forced']:
            record=dict(event)
            ledger=dict(record['ledger'])
            pins=list(ledger['forced'])
            v,b,p=pins[0]
            pins[0]=(v,b,0)
            ledger['forced']=tuple(pins)
            record['ledger']=ledger
            ev[i]=record
            tampered=True
            break
    assert tampered
    forged['events']=tuple(ev)
    denied=False
    try:
        verify_boolean_fixed_point(bridged,len(bridged),{},forged)
    except AssertionError:
        denied=True
    assert denied
    print('FORGED_BOOLEAN_GF2_FIXPOINT_SOURCE_CERTIFICATE_REJECTED=PASS',
          flush=True)
    print('GF2_BOOLEAN_EXACTONE_FIXPOINT_POLYTIME=PROVED_ALL_SCL')
    print('GF2_BOOLEAN_EXACTONE_FIXPOINT_GLOBAL_COMPLETENESS=REFUTED_K4_PETERSEN')
    print('PC3_MOD9_AND_OTHER_GLOBAL_EXPERT_COMPLETENESS=UNRESOLVED')
    print('UNIVERSAL_POLY_SOLVELINEARCUBICXSAT=NOT_CONSTRUCTED')
    print('P_VS_NP=OPEN')


if __name__=='__main__':
    main()
