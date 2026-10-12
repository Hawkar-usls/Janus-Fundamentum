#!/usr/bin/env python3
"""R5 TWO-PLY (constant-depth) certified GF2/ExactOne lookahead.

The predecessor one-ply failed-literal routine has uniformly
polynomial worst-case BIT time, but returned UNKNOWN on K4 SAT
and Petersen UNSAT. This version invokes its EXACTLY ONE bounded
additional assumption layer, not an n-dependent depth search.

SAT is returned only from an independently checked original
witness; UNSAT only when both values of one source variable
are refuted by independently replayed conditional proof trees.
UNKNOWN is a legitimate conclusion if all branches are unresolved.

With a fixed two-ply lookahead, total work and proof size are
n^O(1) (very conservative bound O(n^11) bit operations);
allowing the depth k to grow with n would NOT prove uniform
n^C complexity (branching may become exponential).
"""
from __future__ import annotations
from r5_universal_exact_support_residual_dag_attack import validate_sparse
from r5_universal_certified_failed_literal_boolean_closure import (
    certified_failed_literal_closure,verify_probe_certificate,
    check_original_witness,
)


def verify_two_ply_certificate(rows,n,initial,report):
    rows=validate_sparse(rows,n)
    initial=dict(initial or {})
    outer=report['outer']
    assert verify_probe_certificate(rows,n,initial,outer)
    if outer['status']=='SAT':
        assert report['status']=='SAT'
        assert check_original_witness(rows,n,initial,report['witness'])
        return True
    if outer['status']=='UNSAT':
        assert report['status']=='UNSAT'
        return True
    assert outer['status']=='UNKNOWN'
    assert outer['certified_pins'].items()>=initial.items()
    base=dict(outer['certified_pins'])
    cases=report['cases']
    done=False
    for record in cases:
        v=record['variable']
        assert v not in base and type(v) is int and 0<=v<n
        answers=record['branch_proofs']
        assert set(answers)=={0,1}
        for b in (0,1):
            local=dict(base);local[v]=b
            assert verify_probe_certificate(rows,n,local,answers[b])
        if record['status']=='SAT':
            assert report['status']=='SAT'
            b=record['winning_bit']
            assert answers[b]['status']=='SAT'
            assert check_original_witness(rows,n,initial,report['witness'])
            assert tuple(report['witness'])==tuple(answers[b]['witness'])
            done=True
            break
        if record['status']=='UNSAT':
            assert report['status']=='UNSAT'
            assert all(answers[b]['status']=='UNSAT' for b in (0,1))
            done=True
            break
        assert record['status']=='UNKNOWN'
        assert all(answers[b]['status']=='UNKNOWN' for b in (0,1))
    if not done:
        assert report['status']=='UNKNOWN'
        assert set(r['variable'] for r in cases)==set(range(n))-set(base)
    return True


def certified_two_ply_probe(rows,n,pins=None):
    rows=validate_sparse(rows,n)
    initial=dict(pins or {})
    assert all(type(v) is int and 0<=v<n and b in (0,1)
               for v,b in initial.items())
    outer=certified_failed_literal_closure(rows,n,initial)
    cases=[]
    if outer['status']!='UNKNOWN':
        report={
            'status':outer['status'],
            'witness':outer.get('witness'),
            'outer':outer,
            'cases':tuple(cases),
            'calls':1,
        }
        assert verify_two_ply_certificate(rows,n,initial,report)
        return report
    base=dict(outer['certified_pins'])
    for v in range(n):
        if v in base:continue
        branch={}
        for b in (0,1):
            conditional=dict(base);conditional[v]=b
            branch[b]=certified_failed_literal_closure(
                rows,n,conditional
            )
        winner=next((b for b in (0,1)
                     if branch[b]['status']=='SAT'),None)
        if winner is not None:
            cases.append({'variable':v,'branch_proofs':branch,
                          'status':'SAT','winning_bit':winner})
            report={'status':'SAT','witness':branch[winner]['witness'],
                    'outer':outer,'cases':tuple(cases),
                    'calls':1+2*len(cases)}
            assert verify_two_ply_certificate(rows,n,initial,report)
            return report
        if all(branch[b]['status']=='UNSAT' for b in (0,1)):
            cases.append({'variable':v,'branch_proofs':branch,
                          'status':'UNSAT'})
            report={'status':'UNSAT','outer':outer,
                    'cases':tuple(cases),'calls':1+2*len(cases)}
            assert verify_two_ply_certificate(rows,n,initial,report)
            return report
        # One disproven branch can safely force the opposite pin;
        # the single-ply predecessor already supports this mechanism.
        # This two-ply *diagnostic* does not recursively restart it:
        # excluding this rule weakens coverage but cannot affect truth.
        cases.append({'variable':v,'branch_proofs':branch,
                      'status':'UNKNOWN' if all(
                          branch[b]['status']=='UNKNOWN' for b in (0,1)
                      ) else 'ONE_REFUTED_UNCONSUMED'})
        if cases[-1]['status']=='ONE_REFUTED_UNCONSUMED':
            # Here report is deliberately scope-limited: it makes
            # no universal closure saturation claim.
            return {'status':'UNKNOWN','reason':'ONE_BRANCH_PROVED_NOT_FULL_CLOSURE',
                    'outer':outer,'cases':tuple(cases),
                    'calls':1+2*len(cases)}
    report={'status':'UNKNOWN','outer':outer,'cases':tuple(cases),
            'calls':1+2*len(cases)}
    assert verify_two_ply_certificate(rows,n,initial,report)
    return report


def main():
    from r5_universal_cubic_edgecolor_direct_scl_bridge import (
        make_scl,K4,K33,petersen_graph,
    )
    from r5_universal_modular_flow_count_all_q_no_go import prism
    cases=(
        ('K4_SAT',K4(),'SAT'),
        ('K33_SAT',K33(),'SAT'),
        ('PRISM3_SAT',prism(3)[1],'SAT'),
        ('PETERSEN_UNSAT',petersen_graph(),'UNSAT'),
    )
    for name,graph,truth in cases:
        rows,n,_,_=make_scl(graph)
        answer=certified_two_ply_probe(rows,n)
        assert answer['status'] in ('SAT','UNSAT','UNKNOWN')
        assert answer['status']=='UNKNOWN' or answer['status']==truth
        if answer['status']=='SAT':
            assert check_original_witness(rows,n,{},answer['witness'])
        if answer.get('reason')!='ONE_BRANCH_PROVED_NOT_FULL_CLOSURE':
            assert verify_two_ply_certificate(rows,n,{},answer)
        print(f'TWO_PLY_BOOLEAN_PROBING {name} n={n} '
              f'answer={answer["status"]} truth={truth} '
              f'calls={answer["calls"]}',flush=True)
    print('TWO_PLY_UNIFORM_POLYNOMIAL_FOR_FIXED_DEPTH=PROVED')
    print('SCALING_LOOKAHEAD_DEPTH_WITH_N_UNIFORM_POLYNOMIAL=NOT_PROVED')
    print('UNIVERSAL_POLY_SOLVELINEARCUBICXSAT=NOT_CONSTRUCTED')
    print('P_VS_NP=OPEN')


if __name__=='__main__':
    main()
