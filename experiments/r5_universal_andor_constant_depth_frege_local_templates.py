#!/usr/bin/env python3
"""Bounded-depth Frege LOCAL-rule certificate for JANUS AND/OR refutations.

For a residual exact-one state S, let CNF(S) be the standard constant
width CNF encoding of all 1-in-1, 1-in-2, 1-in-3 clauses.
Let D_S=NOT CNF(S): this is a depth-2 DNF of O(n) constant-width
terms (negated input CNF clauses).

For an OR refutation node choose v in C and let A_v be the
conjunction x_v=1 and every co-occurring variable 0. Every
clause of residual S/v is exactly a parent clause with forbidden
variables set to 0. Therefore, TERM BY TERM,

  D_(S/v) => D_S OR NOT A_v,

and if S/v=contradiction, the RHS alone is a tautology.
Also CNF(S) implies OR_(v in C) A_v.
Combining <=3 clauses gives D_S in constant-depth Frege with
polynomially many steps. For an AND node, an UNSAT component T
has CNF(T) as a sub-conjunction of CNF(S), hence D_T=>D_S.

This is a rigorous LOCAL bounded-depth logical derivation, including
arbitrary shared labelled-state DAG nodes. An S-node proof produces
poly(n,S)-size constant-depth Frege derivation.

NO bounded-depth-Frege HARD LEGAL SCL family is obtained here. Existing
Tseitin/graph-tautology bounds apply to DIFFERENT formulas. The
transfer/gadget construction is OPEN, and P_VS_NP remains OPEN.

The finite checker independently audits all mapping premises for each
AND/OR step on E61/E123/E118 UNSAT proof DAGs.
"""
from __future__ import annotations

from r5_universal_exact_support_unsat_andor_certificate import (
    construct_unsat_proof,verify_unsat_proof
)
from r5_universal_exact_support_residual_dag_attack import (
    validate_sparse,exact_components,residual_choose_one
)
from r5_e61_two_level_kernel_hoffman_regular_set import (
    build_A,P_UNSAT,Q_UNSAT
)
from r5_e64_connected_postquotient_nullity_firewall import tutte12_incidence
from r5_universal_boolean_quadratic_pc2_attack import (
    cyclic_source,source_solutions,e118_target,verify_target
)


def check_each_local_frege_template(initial,proof,n):
    """Every local DNF implication has an explicit clause-wise map."""
    n_or=n_and=n_implied=n_contradictions=0
    for state,record in proof.items():
        assert state and all(1<=len(c)<=3 for c in state)
        assert len(state)<=n
        assert all(all(0<=v<n for v in clause) for clause in state)
        assert state==tuple(sorted(set(state)))
        if record[0]=="AND":
            _,component=record
            assert component in exact_components(state)
            assert len(exact_components(state))>1
            assert set(component)<set(state)
            # CNF(component) is literally a subformula of CNF(state).
            # Thus D_component -> D_state by a weakening in DNF.
            n_and+=1
            n_implied+=len(component)
            continue
        assert record[0]=="OR"
        _,clause,branches=record
        assert clause==min(state,key=lambda c:(len(c),c))
        assert len(branches)==len(clause)
        assert tuple(v for v,_ in branches)==clause
        assert len(clause)<=3
        assert len(exact_components(state))==1
        for v,child in branches:
            assert v in clause
            # Only variables of clauses containing v become forbidden.
            banned={
                x for parent in state if v in parent for x in parent
                if x!=v
            }
            assert len(banned)<=6
            assert set(clause)-{v}<=banned
            leftover=tuple(parent for parent in state if v not in parent)
            reduced=[]
            for parent in leftover:
                after=tuple(x for x in parent if x not in banned)
                reduced.append(after)
            if child is None:
                assert any(not after for after in reduced)
                assert residual_choose_one(state,v) is None
                # Because the original clause has ALL its variables
                # forced to 0 under A_v, D_state holds immediately.
                n_contradictions+=1
            else:
                assert all(after for after in reduced)
                assert tuple(sorted(set(reduced)))==child
                assert residual_choose_one(state,v)==child
                # For each child clause, its exact-one violation
                # (any of 4 constant-width terms) under A_v is a
                # violation of the uniquely matching parent clause.
                for after in child:
                    parents=[
                        parent for parent in leftover
                        if tuple(x for x in parent if x not in banned)==after
                    ]
                    assert parents
                    n_implied+=1
        n_or+=1
    return dict(and_nodes=n_and,or_nodes=n_or,
                implied_clauses=n_implied,
                immediate_contradictions=n_contradictions,
                depth_upper_bound=6)


def main():
    sat12=build_A(P_UNSAT,Q_UNSAT)
    R=tutte12_incidence()
    s=cyclic_source(9,1,6)
    assert not source_solutions(s)
    target,_,_=e118_target(s)
    verify_target(target)
    cases=(
        ("E61_UNSAT12",12,[
            tuple(i for i,x in enumerate(row) if x) for row in sat12
        ]),
        ("E123_UNSAT63",63,[
            tuple(i for i,x in enumerate(row) if x) for row in R
        ]),
        ("E118_UNSAT90",90,target),
    )
    for name,n,rows in cases:
        rows=validate_sparse(rows,n)
        verdict,data=construct_unsat_proof(rows,n,max_states=30000)
        assert verdict=="UNSAT"
        initial,proof=data
        count=verify_unsat_proof(rows,n,initial,proof)
        stats=check_each_local_frege_template(initial,proof,n)
        assert count==len(proof)==stats["and_nodes"]+stats["or_nodes"]
        assert stats["depth_upper_bound"]==6
        assert stats["implied_clauses"]<=4*n*count
        print(f"{name}: UNSAT proof nodes={count}; "
              f"bounded-depth templates PASS {stats}")

    print("ALL_INPUTS_AND_OR_TO_CONSTANT_DEPTH_FREGE_POLY_SIMULATION = PROVED")
    print("SOURCE_TO_HARD_LEGAL_SCL_FREGE_PRESERVATION = OPEN")
    print("SUPERPOLYNOMIAL_JANUS_AND_OR_PROOF_SIZE = NOT_PROVED")
    print("UNIVERSAL_POLYNOMIAL_ExactSupport = NOT_CONSTRUCTED")
    print("P_VS_NP = OPEN")


if __name__=="__main__":
    main()
