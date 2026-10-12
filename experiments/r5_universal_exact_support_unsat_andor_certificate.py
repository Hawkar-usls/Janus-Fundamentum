#!/usr/bin/env python3
"""Independent replayable AND/OR residual-DAG UNSAT proof certificates.

This research proves a polynomial-time proof VERIFIER for finite UNSAT
certificates of the exact formula-caching / connected-component system
used by JANUS ExactSupportResidualDAG.

Certificate nodes:
 - OR(state): name the canonical min-cardinality clause C, show the
   exact residual for EVERY choice of its unique selected member;
   every child is either an immediate contradiction or another
   certified UNSAT node.
 - AND(state): state has disjoint connected components, name ONE
   certified UNSAT component, which refutes the whole conjunction.

NO polynomial bound on certificate size is proved or claimed.
Generating them by recursive search is still exponential worst case.
KNOWN resolution/Tseitin lower bounds do NOT transfer automatically to
this formula-caching AND/OR proof system. P_VS_NP=OPEN.
"""
from __future__ import annotations

from r5_universal_exact_support_residual_dag_attack import (
    validate_sparse, residual_normalize, residual_choose_one,
    exact_components, ExactSupportResidualDAG_sparse
)
from r5_e64_connected_postquotient_nullity_firewall import tutte12_incidence
from r5_e61_two_level_kernel_hoffman_regular_set import (
    P_UNSAT,Q_UNSAT,build_A
)
from r5_universal_boolean_quadratic_pc2_attack import (
    cyclic_source,source_solutions,e118_target,verify_target
)
from r5_universal_exact_support_2lift_visited_dag_frontier import two_lift
from random import Random


class SearchLimit(Exception):
    pass


def validate_irregular_exactone_boundary(rows,n):
    """Narrow, checked extension for cut-open Exact-One fragments.

    Source boundary incidence need not be square/cubic: maintain
    original three-literal Exact-One clauses, all distinct within
    each clause, and local Boolean columns indexed [0,n).
    This does NOT alter strict validation of ordinary SCL sources.
    """
    assert isinstance(n,int) and n>=1
    normalized=[]
    for row in rows:
        clause=tuple(sorted(row))
        assert len(clause)==3 and len(set(clause))==3
        assert all(type(v) is int and 0<=v<n for v in clause)
        normalized.append(clause)
    assert len(set(normalized))==len(normalized)
    return tuple(sorted(normalized))


def construct_unsat_proof(rows,n,pins=None,max_states=None,*,
                          allow_irregular=False):
    rows=(validate_irregular_exactone_boundary(rows,n)
          if allow_irregular else validate_sparse(rows,n))
    pins=dict(pins or {})
    assert all(0<=j<n and x in (0,1) for j,x in pins.items())
    initial=residual_normalize(
        rows,
        fixed_zero=(j for j,x in pins.items() if x==0),
        fixed_one=(j for j,x in pins.items() if x==1),
    )
    if initial is None:
        return None,None # trivially contradictory pins
    cache={}
    proof={}
    def visit(state):
        if state in cache:
            return cache[state]
        if max_states is not None and len(cache)>=max_states:
            raise SearchLimit()
        if not state:
            cache[state]=()
            return ()
        parts=exact_components(state)
        if len(parts)>1:
            pieces=[]
            for part in parts:
                s=visit(part)
                if s is None:
                    proof[state]=("AND",part)
                    cache[state]=None
                    return None
                pieces.extend(s)
            answer=tuple(pieces)
        else:
            clause=min(state,key=lambda c:(len(c),c))
            all_failed=[]
            for v in clause:
                nxt=residual_choose_one(state,v)
                if nxt is None:
                    all_failed.append((v,None))
                    continue
                ans=visit(nxt)
                if ans is not None:
                    cache[state]=(v,)+ans
                    return cache[state]
                all_failed.append((v,nxt))
            proof[state]=("OR",clause,tuple(all_failed))
            cache[state]=None
            return None
        cache[state]=answer
        return answer
    try:
        ans=visit(initial)
    except SearchLimit:
        return "UNKNOWN",None
    if ans is not None:
        witness=set(j for j,x in pins.items() if x==1)|set(ans)
        if all(sum(j in witness for j in clause)==1 for clause in rows):
            return "SAT",tuple(sorted(witness))
        raise AssertionError("SAT witness failed")
    assert initial in proof
    return "UNSAT",(initial,proof)


def verify_unsat_proof(rows,n,initial,proof,pins=None,*,allow_irregular=False):
    """INDEPENDENT local proof verifier; never searches SAT assignments."""
    rows=(validate_irregular_exactone_boundary(rows,n)
          if allow_irregular else validate_sparse(rows,n))
    pins=dict(pins or {})
    expected=residual_normalize(
        rows,
        fixed_zero=(j for j,x in pins.items() if x==0),
        fixed_one=(j for j,x in pins.items() if x==1),
    )
    assert expected is not None and initial==expected
    checked=set()
    def check(state):
        if state in checked:return
        assert state in proof,("missing certified node",state[:3])
        assert state and state==tuple(sorted(set(state)))
        assert all(clause and clause==tuple(sorted(set(clause)))
                   for clause in state)
        record=proof[state]
        parts=exact_components(state)
        if record[0]=="AND":
            assert len(parts)>1
            child=record[1]
            assert child in parts
            assert len(child)<len(state)
            check(child)
        elif record[0]=="OR":
            assert len(parts)==1
            _,clause,branches=record
            assert clause==min(state,key=lambda c:(len(c),c))
            assert len(branches)==len(clause)
            assert tuple(v for v,child in branches)==clause
            for v,child in branches:
                calculated=residual_choose_one(state,v)
                assert child==calculated
                if child is not None:
                    assert len(child)<len(state)
                    check(child)
        else:
            raise AssertionError(("unknown proof rule",record[0]))
        checked.add(state)
    check(initial)
    assert len(checked)==len(proof),("orphan proof nodes",len(checked),len(proof))
    return len(checked)


def main():
    R=tutte12_incidence()
    rowsR=validate_sparse([
        tuple(j for j,x in enumerate(row) if x)
        for row in R
    ],63)
    q9neg=cyclic_source(9,1,6)
    assert not source_solutions(q9neg)
    target,_,_=e118_target(q9neg)
    verify_target(target)
    simple=build_A(P_UNSAT,Q_UNSAT)
    simple_rows=validate_sparse([
        tuple(j for j,x in enumerate(row) if x)
        for row in simple
    ],12)
    lifted=two_lift(rowsR,63,Random(9421))
    cases=[
        ("E61_UNSAT12",simple_rows,12,{}),
        ("E123_UNSAT63",rowsR,63,{}),
        ("E123_2LIFT_UNSAT126",lifted,126,{}),
        ("E118_UNSAT90",tuple(target),90,{}),
    ]
    for name,rows,n,pins in cases:
        answer,data=construct_unsat_proof(rows,n,pins,max_states=20000)
        assert answer=="UNSAT",(name,answer)
        initial,proof=data
        count=verify_unsat_proof(rows,n,initial,proof,pins)
        reference=ExactSupportResidualDAG_sparse(rows,n,pins,max_states=20000)
        assert reference["status"]=="UNSAT",(name,reference["status"])
        assert count<=reference["stats"]["distinct_states"]
        print(f"{name}: UNSAT independent DAG checker PASS; "
              f"proof_nodes={count}, "
              f"visited_solver_states={reference['stats']['distinct_states']}, "
              f"proof_rules={[sum(rec[0]==tag for rec in proof.values()) for tag in ('AND','OR')]}")
    guarded,data=construct_unsat_proof(rowsR,63,max_states=1)
    assert guarded=="UNKNOWN" and data is None
    print("AND_OR_RESIDUAL_DAG_UNSAT_PROOF_VERIFIER=PROVED_SOUND_ALL_INPUTS")
    print("VERIFICATION_TIME=POLY(n,certificate_size), NOT POLY(n) GUARANTEED")
    print("PROOF_CONSTRUCTION_TIME=EXPONENTIAL_WORST_CASE")
    print("NO_POLYNOMIAL_UNSAT_PROOF_SIZE_THEOREM")
    print("NO_LOWER_BOUND_TRANSFER_FROM_RESOLUTION_WITHOUT_SIMULATION")
    print("UNIVERSAL_POLYNOMIAL_ExactSupport=NOT_CONSTRUCTED; P_VS_NP=OPEN")


if __name__=="__main__":
    main()
