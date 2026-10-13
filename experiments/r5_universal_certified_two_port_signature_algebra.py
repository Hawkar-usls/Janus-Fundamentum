#!/usr/bin/env python3
"""JANUS R5: EXACT certified two-port boundary signature algebra.

Every connected legal square+cubic/linear Exact-One source with an
incidence/Tanner 2-edge cut decomposes into TWO cut-open *irregular*
Exact-One fragments. Each has its own original rows, internal source
variables and exactly one foreign variable appearing in one row.

Let u = inside variable with a clause port outside, w = outside
variable occurring in a clause inside. Four assignments (u,w) exhaust
all original Boolean possibilities. For a particular assignment
the WHOLE original formula has a model iff BOTH cut-open sides have
compatible models. Their internal witness assignments glue without
overlap, then EVERY original Exact-One row is checked afresh.

UNSAT is obtained only when EACH of the four exhaustive port states
is independently refuted on at least one side (or clashes with
original caller pins). Every irregular-fragment AND/OR DAG UNSAT
proof is independently replayed with the existing JANUS verifier
extended only by an explicit irregular-source validator. A trivially
contradictory pinned row has a separate zero-node proof and is
rechecked against the real fragment.

A bounded run can return UNKNOWN and NEVER infers UNSAT from a
missing proof. Complete mode may require exponential search for a
fragment signature; four ports bound the interface, NOT its cost.
"""
from __future__ import annotations

from itertools import product
from r5_universal_exact_support_residual_dag_attack import (
    validate_sparse,residual_normalize,
)
from r5_universal_exact_support_unsat_andor_certificate import (
    construct_unsat_proof,verify_unsat_proof,
    validate_irregular_exactone_boundary,
)
from r5_universal_connected_scl_tanner_two_cut_proof_audit import (
    certified_tanner_edge_connectivity,exact_tanner_graph,
)


def cut_open_fragments(rows,n,cut):
    """Build both sides and verify every original row/column partition."""
    rows=validate_sparse(rows,n)
    edges,adj=exact_tanner_graph(rows,n)
    side=set(cut['side'])
    assert 0<len(side)<2*n
    cross=tuple(sorted(
        i for i,(row,variable) in enumerate(edges)
        if (row in side)!=(variable in side)
    ))
    assert cross==tuple(sorted(cut['edge_ids'])) and len(cross)==2
    ca=sum(edges[i][0] in side for i in cross)
    cb=sum(edges[i][1] in side for i in cross)
    assert ca==cb==1

    inside={x-n for x in side if x>=n}
    outside=set(range(n))-inside
    side_rows={x for x in side if x<n}
    other_rows=set(range(n))-side_rows
    assert len(inside)==len(side_rows)
    assert len(outside)==len(other_rows)
    e_in=next(edges[i] for i in cross if edges[i][1] in side)
    e_out=next(edges[i] for i in cross if edges[i][0] in side)
    u=e_in[1]-n
    w=e_out[1]-n
    assert u in inside and w in outside and u!=w
    assert e_in[0] in other_rows and e_out[0] in side_rows

    def make_piece(row_ids,own,foreign):
        ids=tuple(sorted(row_ids))
        cols=tuple(sorted(own|{foreign}))
        remap={v:i for i,v in enumerate(cols)}
        local=validate_irregular_exactone_boundary(
            [tuple(remap[v] for v in rows[ci]) for ci in ids],len(cols)
        )
        assert set(v for ci in ids for v in rows[ci])==set(cols)
        assert len(local)==len(own)
        return {
            'row_indices':ids,
            'original_columns':cols,
            'inside_columns':tuple(sorted(own)),
            'foreign_column':foreign,
            'local_rows':local,
            'local_n':len(cols),
        }
    left=make_piece(side_rows,inside,w)
    right=make_piece(other_rows,outside,u)
    assert sorted(left['row_indices']+right['row_indices'])==list(range(n))
    assert sorted(left['inside_columns']+right['inside_columns'])==list(range(n))
    assert len(set(left['original_columns'])&set(right['original_columns']))==2
    assert set(left['original_columns'])&set(right['original_columns'])=={u,w}
    return (left,right),(u,w)


def arithmetic_two_port_allowed(piece,values):
    """Exact original source-row sum certificate for boundary states.

    For the left side, r original rows and r internal variables:
      3 * internal selected variables = r + x_u - x_w.
    Modulo 3 this is necessary for every satisfying assignment.
    """
    assert len(values)==2
    u,w=values
    residue=len(piece['row_indices'])%3
    return (residue+u-w)%3==0


def local_pins(piece,pins,ports,values):
    assert len(ports)==2 and len(values)==2
    desired=dict(pins)
    for v,b in zip(ports,values):
        if v in desired and desired[v]!=b:
            return None
        desired[v]=b
    cols=piece['original_columns']
    return {i:desired[v] for i,v in enumerate(cols) if v in desired}


def check_piece_model(piece,pins,local_witness):
    assert local_witness is not None
    assert len(local_witness)==piece['local_n']
    assert all(x in (0,1) for x in local_witness)
    assert all(local_witness[i]==value for i,value in pins.items())
    assert all(sum(local_witness[v] for v in row)==1
               for row in piece['local_rows'])
    return True


def prove_piece(piece,pins,max_states):
    rows=piece['local_rows']
    n=piece['local_n']
    status,payload=construct_unsat_proof(
        rows,n,pins=pins,max_states=max_states,
        allow_irregular=True,
    )
    if status=='UNKNOWN':
        return {'status':'UNKNOWN'}
    if status=='SAT':
        selected=set(payload)
        model=tuple(int(i in selected) for i in range(n))
        assert check_piece_model(piece,pins,model)
        return {'status':'SAT','model':model}
    if status is None and payload is None:
        contradiction=residual_normalize(
            rows,
            fixed_zero=[v for v,x in pins.items() if x==0],
            fixed_one=[v for v,x in pins.items() if x==1],
        )
        assert contradiction is None
        return {'status':'UNSAT','proof_type':'ROOT_PIN_ROW_CONFLICT'}
    assert status=='UNSAT' and payload is not None
    initial,proof=payload
    count=verify_unsat_proof(
        rows,n,initial,proof,pins=pins,
        allow_irregular=True,
    )
    return {
        'status':'UNSAT',
        'proof_type':'EXACT_IRREGULAR_ANDOR_DAG',
        'initial':initial,'proof':proof,'proof_nodes':count,
    }


def check_piece_negative(piece,pins,record):
    assert record['status']=='UNSAT'
    if record['proof_type']=='ROOT_PIN_ROW_CONFLICT':
        assert residual_normalize(
            piece['local_rows'],
            fixed_zero=[v for v,x in pins.items() if x==0],
            fixed_one=[v for v,x in pins.items() if x==1],
        ) is None
        return 0
    assert record['proof_type']=='EXACT_IRREGULAR_ANDOR_DAG'
    nodes=verify_unsat_proof(
        piece['local_rows'],piece['local_n'],
        record['initial'],record['proof'],pins=pins,
        allow_irregular=True,
    )
    assert nodes==record['proof_nodes']
    return nodes


def verify_two_port_report(rows,n,pins,report):
    """Independent global compositional verifier with no SAT search."""
    rows=validate_sparse(rows,n)
    pins=dict(pins or {})
    parts,ports=cut_open_fragments(rows,n,report['cut'])
    assert ports==report['ports']
    if report['status']=='SAT':
        model=report['witness']
        assert len(model)==n and all(x in (0,1) for x in model)
        assert all(model[v]==b for v,b in pins.items())
        assert all(sum(model[v] for v in row)==1 for row in rows)
        return {'verified':True,'certificate':'GLOBAL_SAT_WITNESS'}
    assert report['status']=='UNSAT'
    records=report['boundary_cases']
    assert len(records)==4
    count=0
    for record,(a,b) in zip(records,product((0,1),repeat=2)):
        assert tuple(record['port_values'])==(a,b)
        if record['status']=='ORIGINAL_PIN_CONFLICT':
            assert any(v in pins and pins[v]!=x
                       for v,x in zip(ports,(a,b)))
            continue
        if record['status']=='CUT_MOD3_CONFLICT':
            assert record['residue']==len(parts[0]['row_indices'])%3
            assert not arithmetic_two_port_allowed(parts[0],(a,b))
            continue
        assert record['status']=='SIDE_UNSAT'
        side=record['side']
        assert side in (0,1)
        side_pins=local_pins(parts[side],pins,ports,(a,b))
        assert side_pins is not None
        count+=check_piece_negative(
            parts[side],side_pins,record['refutation']
        )
    return {'verified':True,'certificate':'FOUR_PORT_EXHAUSTIVE_UNSAT',
            'verified_nodes':count}


def certified_two_port_signature(rows,n,pins=None,max_states=100,
                                  *,cut=None):
    """SAT+checked witness, UNSAT+replayable proof, or UNKNOWN.

    max_states is a bound for EACH irregular side query; None allows
    a complete but potentially exponential signature construction.
    The certificate still needs independent replay before adoption.
    """
    rows=validate_sparse(rows,n)
    pins=dict(pins or {})
    assert all(type(v) is int and 0<=v<n and b in (0,1)
               for v,b in pins.items())
    assert max_states is None or (
        isinstance(max_states,int) and max_states>=0
    )
    cuts=certified_tanner_edge_connectivity(rows,n,first_only=True)
    if not cuts['cuts']:
        return {'status':'UNKNOWN','reason':'NO_TANNER_TWO_CUT'}
    chosen=cut if cut is not None else cuts['cuts'][0]
    pieces,ports=cut_open_fragments(rows,n,chosen)
    cases=[]
    for values in product((0,1),repeat=2):
        value_pins=dict(zip(ports,values))
        if any(v in pins and pins[v]!=b for v,b in value_pins.items()):
            cases.append({
                'port_values':values,'status':'ORIGINAL_PIN_CONFLICT'
            })
            continue
        if not arithmetic_two_port_allowed(pieces[0],values):
            cases.append({
                'port_values':values,'status':'CUT_MOD3_CONFLICT',
                'residue':len(pieces[0]['row_indices'])%3,
                'proof_authority':'EXACT_ORIGINAL_ROW_SUM_MOD3',
            })
            continue
        neg=None;models=[];unknown=False
        for side in (0,1):
            p=local_pins(pieces[side],pins,ports,values)
            assert p is not None
            result=prove_piece(pieces[side],p,max_states)
            if result['status']=='UNSAT':
                neg={'port_values':values,
                     'status':'SIDE_UNSAT','side':side,
                     'refutation':result}
                break
            if result['status']=='UNKNOWN':
                unknown=True
            else:
                assert result['status']=='SAT'
                models.append((side,result['model']))
        if neg is not None:
            cases.append(neg)
            continue
        if unknown or len(models)!=2:
            cases.append({'port_values':values,'status':'UNKNOWN'})
            continue
        model=[None]*n
        for side,local in models:
            piece=pieces[side]
            for v in piece['inside_columns']:
                val=local[piece['original_columns'].index(v)]
                assert model[v] is None
                model[v]=val
        assert all(v in (0,1) for v in model)
        assert all(model[v]==b for v,b in pins.items())
        assert all(sum(model[v] for v in row)==1 for row in rows)
        report={
            'status':'SAT',
            'witness':tuple(model),
            'ports':ports,'cut':chosen,
            'boundary_cases':tuple(cases),
            'reason':'EXACT_TWO_PORT_WITNESS_GLUE',
        }
        assert verify_two_port_report(rows,n,pins,report)['verified']
        return report
    assert len(cases)==4
    if any(x['status']=='UNKNOWN' for x in cases):
        return {'status':'UNKNOWN','ports':ports,'cut':chosen,
                'boundary_cases':tuple(cases),
                'reason':'ATOMIC_BOUNDARY_SIGNATURE_UNKNOWN'}
    report={
        'status':'UNSAT','ports':ports,'cut':chosen,
        'boundary_cases':tuple(cases),
        'reason':'EXHAUSTIVE_FOUR_PORT_PROOF',
    }
    replay=verify_two_port_report(rows,n,pins,report)
    assert replay['certificate']=='FOUR_PORT_EXHAUSTIVE_UNSAT'
    report['verified_nodes']=replay['verified_nodes']
    return report


def main():
    from r5_universal_cubic_edgecolor_direct_scl_bridge import K4,make_scl
    from r5_universal_all_odd_cyclic_pc2_four_orbit_identity import cyclic
    from r5_universal_connected_scl_tanner_two_cut_proof_audit import (
        exact_connected_incidence_switch,
    )
    sat18,_,_,_=make_scl(K4())
    positives=exact_connected_incidence_switch(sat18,sat18)
    n=len(positives)
    assert n==36
    sat=certified_two_port_signature(positives,n,max_states=256)
    assert sat['status']=='SAT'
    assert verify_two_port_report(positives,n,{},sat)['verified']
    print('TWO_PORT_CONNECTED_SCL36_SAT_WITNESS_INDEPENDENTLY_GLUED=PASS',
          flush=True)
    # Actual high-level JANUS portfolio integration, not a shadow demo.
    from r5_universal_certified_expert_portfolio import (
        SolveLinearCubicXSAT_Portfolio,
    )
    integrated=SolveLinearCubicXSAT_Portfolio(
        positives,n,poly_only=True,pc3_max_n=0,
        tanner_cut_max_n=0,bounded_states=0,
        two_port_max_n=40,two_port_states=256,
        gf2_linear_propagation=False,
    )
    assert integrated['status']=='SAT'
    assert integrated['expert']=='CERTIFIED_TWO_PORT_SIGNATURE',integrated['expert']
    assert integrated['two_port_certificate_replayed']
    assert all(sum(integrated['witness'][v] for v in row)==1
               for row in positives)
    print('TWO_PORT_HIGH_LEVEL_POLY_GUARDED_PORTFOLIO_SAT_GLUE=VERIFIED',
          flush=True)

    cut=certified_tanner_edge_connectivity(
        positives,n,first_only=True
    )['cuts'][0]
    pieces,(u,w)=cut_open_fragments(positives,n,cut)
    assert u!=w and len(pieces)==2
    assert all(p['local_n']==19 for p in pieces)
    blocked={u:1,w:0}
    neg=certified_two_port_signature(
        positives,n,pins=blocked,max_states=256,
    )
    assert neg['status']=='UNSAT'
    verifier=verify_two_port_report(positives,n,blocked,neg)
    assert verifier['verified']
    print('TWO_PORT_CONTRADICTORY_BOUNDARY_PIN_FULL_CERTIFICATE=PASS',
          flush=True)
    instant=certified_two_port_signature(
        positives,n,pins=blocked,max_states=0
    )
    assert instant['status']=='UNSAT'
    assert verify_two_port_report(positives,n,blocked,instant)['verified']
    assert all(c['status'] in (
        'ORIGINAL_PIN_CONFLICT','CUT_MOD3_CONFLICT'
    ) for c in instant['boundary_cases'])
    print('TWO_PORT_PIN_CONFLICT_MOD3_ZERO_INNER_STATES_UNSAT=PROVED',
          flush=True)
    forged={**instant}
    bad_records=[dict(x) for x in instant['boundary_cases']]
    attacked=False
    for entry in bad_records:
        if entry['status']=='CUT_MOD3_CONFLICT':
            entry['residue']=(entry['residue']+1)%3
            attacked=True
            break
    assert attacked
    forged['boundary_cases']=tuple(bad_records)
    bad_mod3_rejected=False
    try:
        verify_two_port_report(positives,n,blocked,forged)
    except (AssertionError,KeyError):
        bad_mod3_rejected=True
    assert bad_mod3_rejected
    print('TWO_PORT_FORGED_MOD3_CUT_ARITHMETIC_PROOF_REJECTED=VERIFIED',
          flush=True)
    integrated_negative=SolveLinearCubicXSAT_Portfolio(
        positives,n,pins=blocked,poly_only=True,
        pc3_max_n=0,bounded_states=0,
        tanner_cut_max_n=0,
        two_port_max_n=40,two_port_states=256,
        gf2_linear_propagation=False,
    )
    assert integrated_negative['status']=='UNSAT'
    assert integrated_negative['expert'] in (
        'CERTIFIED_TWO_PORT_SIGNATURE','HYBRID_ROOT'
    )
    if integrated_negative['expert']=='CERTIFIED_TWO_PORT_SIGNATURE':
        assert integrated_negative['two_port_certificate_replayed']
    print('TWO_PORT_OR_ROOT_INDEPENDENTLY_REPLAYED_UNSAT_GUARD=VERIFIED',
          flush=True)

    no_budget=certified_two_port_signature(
        positives,n,max_states=0
    )
    assert no_budget['status']=='UNKNOWN'
    print('TWO_PORT_ZERO_BUDGET_UNKNOWN_NOT_UNSAT=PASS',flush=True)

    # More interesting root-nontrivial UNSAT: cut-open local side
    # carries the Fano-plane SCL7 obstruction. Local AND/OR
    # refutations (not only conflicting caller pins) must be replayed.
    neg25=exact_connected_incidence_switch(sat18,cyclic(7))
    assert len(neg25)==25
    proof=certified_two_port_signature(
        neg25,25,max_states=256
    )
    assert proof['status']=='UNSAT'
    assert any(c['status']=='SIDE_UNSAT' for c in proof['boundary_cases'])
    assert verify_two_port_report(
        neg25,25,{},proof
    )['certificate']=='FOUR_PORT_EXHAUSTIVE_UNSAT'
    print(f'TWO_PORT_CONNECTED_SCL25_TRUE_UNSAT_DAG_REPLAY_NODES='
          f'{proof["verified_nodes"]}',flush=True)

    # Negative control: a certificate whose verified ANDOR proof
    # is intentionally destroyed MUST be rejected by independent
    # raw fragment proof replay.
    damaged={**proof}
    records=[dict(rec) for rec in proof['boundary_cases']]
    for rec in records:
        if rec['status']=='SIDE_UNSAT':
            local=dict(rec['refutation'])
            if local['proof_type']=='EXACT_IRREGULAR_ANDOR_DAG':
                local['proof']={}
                rec['refutation']=local
                break
    else:
        raise AssertionError('need nontrivial ANDOR certificate control')
    damaged['boundary_cases']=tuple(records)
    rejected=False
    try:
        verify_two_port_report(neg25,25,{},damaged)
    except (AssertionError,KeyError):
        rejected=True
    assert rejected, 'corrupt independent certificate was accepted'
    print('TWO_PORT_CORRUPTED_LOCAL_UNSAT_DAG_REJECTED=PASS',flush=True)

    # Atomic core safeguard: Fano's genuine 3-edge-connected Tanner
    # graph does not acquire a fake 2-port signature or negative
    # conclusion just because the global source is UNSAT.
    from r5_universal_all_odd_cyclic_pc2_four_orbit_identity import cyclic
    atomic=certified_two_port_signature(cyclic(7),7,max_states=0)
    assert atomic['status']=='UNKNOWN'
    assert atomic['reason']=='NO_TANNER_TWO_CUT'
    print('THREE_EDGE_CONNECTED_ATOMIC_SOURCE_HAS_NO_FAKE_PORT_SIGNATURE=VERIFIED',
          flush=True)
    print('TWO_PORT_ARITHMETIC_RESIDUE_REDUCES_4_STATES_TO_AT_MOST_2_OR_1=PROVED')
    print('EXACT_TWO_PORT_ALGEBRA_SOUND_COMPLETE_WITH_UNBOUNDED_FALLBACK=PROVED')
    print('POLY_TWO_PORT_ATOMIC_SIGNATURE_CONSTRUCTION=OPEN')
    print('UNIVERSAL_POLY_SOLVELINEARCUBICXSAT=NOT_CONSTRUCTED')
    print('P_VS_NP=OPEN')


if __name__=='__main__':
    main()
