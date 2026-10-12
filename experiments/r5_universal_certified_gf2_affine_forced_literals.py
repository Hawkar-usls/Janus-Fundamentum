#!/usr/bin/env python3
"""JANUS all-SCL GF(2) source linear consequences with PROOF LEDGERS.

Proof theorem for every valid original n-by-n square/cubic/linear
positive Exact-One source A and caller pins P:

  Each valid exact-one assignment x satisfies A*x=1 over GF2.
  Gaussian elimination over GF2 of augmented source+pin equations
  yields independently replayable XOR-of-original-rows certificates.

  A pivot expression with zero free-variable support gives a
  CERTIFIED forced original Boolean literal.
  Two variables with identical free-variable coefficient signature
  satisfy x_i XOR x_j = c, with a certified row XOR witness.
  A zero left side and one right side certifies UNSAT.
  A clause with >=2 certified forced 1 values, or all 0 values,
  also certifies UNSAT using original exact-one semantics.

This is an ALL-INPUT deterministic polynomial-time deduction
and original-source certificate extractor. Algebraic consistency
alone is UNKNOWN, never SAT. Even knowing all pair relations
does NOT force a witness on every SAT instance (see earlier
semantic width2 barrier), nor produce a polynomial P=NP solver.

The point: this engine can automatically detect certain source
bridge obstructions without an UNTRUSTED Holyer graph hint,
unlike the predecessor conditional source bridge expert.
"""
from __future__ import annotations
from collections import defaultdict

from r5_universal_exact_support_residual_dag_attack import validate_sparse


def source_equations(rows,n,pins):
    rows=validate_sparse(rows,n)
    assert all(type(i) is int and 0<=i<n and b in (0,1)
               for i,b in pins.items())
    equations=[(sum(1<<v for v in clause),1)
               for clause in rows]
    equations+= [(1<<v,b) for v,b in sorted(pins.items())]
    return tuple(equations)


def verify_xor_claim(equations,mask,rhs,provenance):
    """Independent GF2 original-equation XOR replay."""
    lhs=0;bound=0
    assert type(provenance) is int and 0<=provenance<(1<<len(equations))
    for i,(a,b) in enumerate(equations):
        if (provenance>>i)&1:
            lhs^=a;bound^=b
    assert lhs==mask and bound==rhs,(mask,rhs,lhs,bound)
    return True


def verify_gf2_ledger(rows,n,pins,ledger):
    """No Gaussian basis, pivot order or producer rank is trusted."""
    eqs=source_equations(rows,n,pins)
    for v,b,p in ledger['forced']:
        assert 0<=v<n and b in (0,1)
        verify_xor_claim(eqs,1<<v,b,p)
    for u,v,c,p in ledger['pairs']:
        assert 0<=u<v<n and c in (0,1)
        verify_xor_claim(eqs,(1<<u)|(1<<v),c,p)
    if ledger['status']=='UNSAT':
        if ledger['reason']=='INCONSISTENT_GF2':
            verify_xor_claim(eqs,0,1,ledger['unsat_proof'])
        elif ledger['reason']=='EXACTONE_FORCED_CLAUSE_CONFLICT':
            i=ledger['clause_index'];row=tuple(rows[i])
            forced=dict((v,b) for v,b,_ in ledger['forced'])
            assert (sum(forced.get(v,0)==1 for v in row)>=2 or
                    all(v in forced and forced[v]==0 for v in row))
        else:
            raise AssertionError('unrecognized UNSAT proof')
    elif ledger['status']=='SAT':
        w=ledger['witness']
        assert len(w)==n and all(x in (0,1) for x in w)
        assert all(w[v]==b for v,b in pins.items())
        assert all(sum(w[v] for v in row)==1 for row in rows)
    else:
        assert ledger['status']=='UNKNOWN'
    return True


def gf2_certified_source_closure(rows,n,pins=None):
    rows=validate_sparse(rows,n)
    pins=dict(pins or {})
    equations=source_equations(rows,n,pins)
    # coefficient rows, rhs, and bit-mask of which ORIGINAL
    # source/pin equations were XORed to create this row.
    matrix=[[mask,rhs,1<<i] for i,(mask,rhs) in enumerate(equations)]
    pivot={}
    pos=0
    for column in range(n):
        needle=1<<column
        target=next((i for i in range(pos,len(matrix))
                     if matrix[i][0]&needle),None)
        if target is None:continue
        matrix[pos],matrix[target]=matrix[target],matrix[pos]
        for i in range(len(matrix)):
            if i!=pos and matrix[i][0]&needle:
                matrix[i][0]^=matrix[pos][0]
                matrix[i][1]^=matrix[pos][1]
                matrix[i][2]^=matrix[pos][2]
        pivot[column]=pos
        pos+=1
        if pos==len(matrix):break

    contradictions=[t for t in matrix if t[0]==0 and t[1]==1]
    if contradictions:
        p=contradictions[0][2]
        report={'status':'UNSAT','reason':'INCONSISTENT_GF2',
                'unsat_proof':p,'forced':(),'pairs':()}
        assert verify_gf2_ledger(rows,n,pins,report)
        return report

    free_mask=sum(1<<v for v in range(n) if v not in pivot)
    signatures={}
    for v in range(n):
        if v in pivot:
            row=matrix[pivot[v]]
            assert row[0]&(1<<v)
            assert not (row[0]&sum(1<<j for j in pivot if j!=v))
            signatures[v]=(row[0]&free_mask,row[1],row[2])
        else:
            signatures[v]=(1<<v,0,0)

    forced=tuple(sorted((v,b,p) for v,(m,b,p)
                        in signatures.items() if m==0))
    groups=defaultdict(list)
    for v,(mask,b,prov) in signatures.items():
        groups[mask].append((v,b,prov))
    relations=[]
    for mask,group in groups.items():
        if mask==0:continue
        u,bu,pu=group[0]
        for v,bv,pv in group[1:]:
            assert u<v
            relations.append((u,v,bu^bv,pu^pv))
    relations=tuple(sorted(relations))

    ff={v:b for v,b,p in forced}
    for i,row in enumerate(rows):
        if (sum(ff.get(v,0)==1 for v in row)>=2 or
            all(v in ff and ff[v]==0 for v in row)):
            report={'status':'UNSAT',
                    'reason':'EXACTONE_FORCED_CLAUSE_CONFLICT',
                    'clause_index':i,
                    'unsat_proof':None,
                    'forced':forced,'pairs':relations}
            assert verify_gf2_ledger(rows,n,pins,report)
            return report
    if len(ff)==n:
        witness=tuple(ff[v] for v in range(n))
        assert all(sum(witness[v] for v in row)==1 for row in rows)
        report={'status':'SAT','reason':'FULL_GF2_AFFINE_UNIQUE_WITNESS',
                'witness':witness,
                'forced':forced,'pairs':relations}
    else:
        report={'status':'UNKNOWN','reason':'GF2_AFFINE_NOT_BOOLEAN_COMPLETE',
                'forced':forced,'pairs':relations}
    assert verify_gf2_ledger(rows,n,pins,report)
    return report


def main():
    from r5_universal_atomic_gf4_cycle_cut_fourier_duality import (
        bridged_cubic_graph,
    )
    from r5_universal_cubic_edgecolor_direct_scl_bridge import (
        make_scl,K4,K33,petersen_graph,
    )
    from r5_universal_certified_expert_portfolio import (
        SolveLinearCubicXSAT_Portfolio,
    )
    bridged=bridged_cubic_graph()
    rows,n,_,_=make_scl(bridged)
    report=gf2_certified_source_closure(rows,n)
    assert report['status']=='UNSAT',report['status']
    assert report['reason']=='EXACTONE_FORCED_CLAUSE_CONFLICT'
    assert verify_gf2_ledger(rows,n,{},report)
    print(f'BRIDGED_ATOMIC_SCL_GF2_NO_GRAPH_HINT_UNSAT=VERIFIED '
          f'n={n} forced={len(report["forced"])} '
          f'pair_relations={len(report["pairs"])}',flush=True)

    # No symmetry, Holyer, or graph metadata supplied to this main
    # solver. Disable PC3, residual search and graph-hint gates so
    # any UNSAT must come from the independent GF2 proof ledger.
    routed=SolveLinearCubicXSAT_Portfolio(
        rows,n,poly_only=True,
        pc3_max_n=0,bounded_states=0,
        tanner_cut_max_n=0,two_port_max_n=0,
        gf2_linear_propagation=True,
    )
    assert routed['status']=='UNSAT'
    assert routed['expert']=='CERTIFIED_GF2_SOURCE_CLAUSE_CONFLICT'
    print('REAL_PORTFOLIO_NO_HOLYER_HINT_BRIDGE_UNSAT=VERIFIED',
          flush=True)

    for name,G in (('K4',K4()),('K33',K33()),
                   ('PETERSEN',petersen_graph())):
        A,k,_,_=make_scl(G)
        check=gf2_certified_source_closure(A,k)
        assert check['status'] in ('UNKNOWN','UNSAT','SAT')
        assert verify_gf2_ledger(A,k,{},check)
        if name in ('K4','K33'):
            assert check['status']!='UNSAT'
        print(f'GF2_CONTROL_{name}={check["status"]} '
              f'forced={len(check["forced"])} '
              f'pair_relations={len(check["pairs"])}',flush=True)

    # SAT with caller pins: every inferred relation is checked
    # against original equations, independently of producer basis.
    sat,ns,_,_=make_scl(K4())
    positive=gf2_certified_source_closure(sat,ns,{0:1})
    assert positive['status']!='UNSAT'
    assert any(v in (1,2) for a,b,_,_ in positive['pairs'] for v in (a,b))
    print('PINNED_K4_PARITY_RELATIONS_REPLAYED=PASS',flush=True)

    # Tamper with a genuinely accepted original-row provenance.
    target=next((x for x in report['forced'] if x[2]),None)
    assert target is not None
    forged=dict(report)
    forced=list(report['forced'])
    i=forced.index(target)
    forced[i]=(target[0],target[1],0)
    forged['forced']=tuple(forced)
    rejected=False
    try:
        verify_gf2_ledger(rows,n,{},forged)
    except AssertionError:rejected=True
    assert rejected
    print('FORGED_GF2_XOR_ROW_CERTIFICATE_REJECTED=PASS',flush=True)
    print('ALL_SCL_GF2_FORCED_LITERALS_AND_PAIR_RELATIONS=PROVED')
    print('GF2_PARITY_SOURCE_CLOSURE_ALONE_ALL_INPUT_DECISION=OPEN')
    print('UNIVERSAL_POLY_SOLVELINEARCUBICXSAT=NOT_CONSTRUCTED')
    print('P_VS_NP=OPEN')


if __name__=='__main__':
    main()
