#!/usr/bin/env python3
"""JANUS ExactSupport residual-DAG compression experiment.

Every search state is the EXACT residual exact-cover hypergraph with
already-satisfied clauses deleted and forbidden variables deleted
from remaining clauses. Equal LABELLED residuals are memoized, and
connected components are split via AND/product decomposition.

The solver handles arbitrary partial Boolean pins; SAT returns and
INDEPENDENTLY CHECKS the original Boolean witness. A state budget
returns UNKNOWN and never claims UNSAT from incomplete exploration.

Theorem (all legal inputs): one residual support state S is SAT iff
  (i) S is empty, or
  (ii) in each disjoint connected component of S there is a solution,
  (iii) when S is connected, some variable v of ANY clause C satisfies
       the exact deletion/forbidden-variable residual S/v.
Each reduction is exact. The computed graph has O(S * poly(n)) bit
cost for S distinct reachable labelled residual states.

CRITICAL LIMIT: S can a priori be EXPONENTIAL; this implementation
DOES NOT supply S <= poly(n), and is not a P=NP proof. The concrete
tested sizes are observations, not general bounds.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from r5_e61_two_level_kernel_hoffman_regular_set import (
    P_SAT, Q_SAT, P_UNSAT, Q_UNSAT, build_A
)
from r5_e64_connected_postquotient_nullity_firewall import tutte12_incidence
from r5_universal_boolean_quadratic_pc2_attack import (
    cyclic_source, source_solutions, e118_target, verify_target
)
from r5_e125_toroidal_one_check_block_splice import build_splice
from r5_universal_kettani_2025_toroidal_treewidth_counterexample import (
    toroidal_triangular_carrier
)
from r5_universal_e118_tropical_defect_variable_elimination import (
    constraints_from_matrix
)
from r5_universal_exact_support_pinned_oracle_attack import ExactSupport


class StateGuardExceeded(Exception):
    pass


@dataclass
class DAGStats:
    distinct_states: int = 0
    cache_hits: int = 0
    transitions: int = 0
    component_splits: int = 0
    max_clauses: int = 0
    guard_hits: int = 0


def validate_sparse(rows, n):
    """O(n polylog n) legal 3-regular and C4-free hypergraph validation."""
    if n<=0 or len(rows)!=n:
        raise ValueError("square incidence required")
    deg=[0]*n
    pairs=set()
    out=[]
    for row in rows:
        row=tuple(sorted(row))
        if len(row)!=3 or len(set(row))!=3:
            raise ValueError("row must have three distinct variables")
        if any(not isinstance(v,int) or v<0 or v>=n for v in row):
            raise ValueError("variable out of range")
        for v in row:
            deg[v]+=1
        a,b,c=row
        for e in ((a,b),(a,c),(b,c)):
            if e in pairs:
                raise ValueError("not C4-free: pair appears twice")
            pairs.add(e)
        out.append(row)
    if any(d!=3 for d in deg):
        raise ValueError("columns must all have weight 3")
    return tuple(sorted(out))


def _pins(n,pins):
    if pins is None:return {}
    pairs=pins.items() if isinstance(pins,dict) else pins
    result={}
    for key,value in pairs:
        if not isinstance(key,int) or not isinstance(value,int) or value not in (0,1):
            raise ValueError("pins must be 0/1 assignments to integer indices")
        if key<0 or key>=n:
            raise ValueError("pin index outside variables")
        if key in result and result[key]!=value:
            return None
        result[key]=value
    return result


def residual_normalize(rows, fixed_zero=(), fixed_one=()):
    """Exact residual hypergraph: None means a proved contradiction."""
    forbidden=set(fixed_zero)
    chosen=set(fixed_one)
    if forbidden & chosen:
        return None
    pending=[]
    for clause in rows:
        members=set(clause)
        ones=members & chosen
        if len(ones)>1:
            return None
        if ones:
            forbidden.update(members-chosen)
        else:
            pending.append(members)
    # No already-chosen member remains in pending.
    reduced=[]
    for members in pending:
        members=members-forbidden
        if not members:
            return None
        reduced.append(tuple(sorted(members)))
    return tuple(sorted(set(reduced)))


def residual_choose_one(state,chosen):
    """One exact branch v=1: satisfy all rows containing v; ban conflicts."""
    forbidden=set()
    remaining=[]
    touched=False
    for clause in state:
        if chosen in clause:
            touched=True
            forbidden.update(clause)
        else:
            remaining.append(clause)
    assert touched
    forbidden.remove(chosen)
    return residual_normalize(remaining,fixed_zero=forbidden)


def exact_components(state):
    """Connected components of current VARIABLE/CLAUSE incidence graph."""
    parent={v:v for clause in state for v in clause}
    def root(v):
        while parent[v]!=v:
            parent[v]=parent[parent[v]]
            v=parent[v]
        return v
    for clause in state:
        first=root(clause[0])
        for v in clause[1:]:
            other=root(v)
            if other!=first:
                parent[other]=first
    groups={}
    for clause in state:
        groups.setdefault(root(clause[0]),[]).append(clause)
    return tuple(
        sorted((tuple(sorted(g)) for g in groups.values()),
               key=lambda g:(len(g),g))
    )


def ExactSupportResidualDAG_sparse(rows,n,pins=None,max_states=None):
    """Sound SAT+witness, sound UNSAT or guarded UNKNOWN.

    With max_states=None the algorithm is total, but may use
    exponential time and memory. When a state cap is exceeded,
    returns UNKNOWN with no inferred SAT/UNSAT result.
    """
    rows=validate_sparse(rows,n)
    pins=_pins(n,pins)
    stats=DAGStats()
    if pins is None:
        return dict(status="UNSAT",witness=None,reason="CONFLICTING_PINS",
                    stats=vars(stats).copy())
    if n%3:
        return dict(status="UNSAT",witness=None,reason="3_DOES_NOT_DIVIDE_N",
                    stats=vars(stats).copy())
    if max_states is not None and (
        not isinstance(max_states,int) or max_states<0
    ):
        raise ValueError("max_states must be a nonnegative integer or None")

    ones={i for i,v in pins.items() if v==1}
    zero={i for i,v in pins.items() if v==0}
    initial=residual_normalize(rows,zero,ones)
    if initial is None:
        return dict(status="UNSAT",witness=None,reason="PIN_CLAUSE_CONFLICT",
                    stats=vars(stats).copy())

    cache={}
    def visit(state):
        if state in cache:
            stats.cache_hits+=1
            return cache[state]
        if max_states is not None and stats.distinct_states>=max_states:
            stats.guard_hits+=1
            raise StateGuardExceeded()
        stats.distinct_states+=1
        stats.max_clauses=max(stats.max_clauses,len(state))
        if not state:
            answer=()
        else:
            components=exact_components(state)
            if len(components)>1:
                stats.component_splits+=1
                combined=[]
                for part in components:
                    solution=visit(part)
                    if solution is None:
                        combined=None
                        break
                    combined.extend(solution)
                answer=(tuple(sorted(combined))
                        if combined is not None else None)
            else:
                shortest=min(state,key=lambda c:(len(c),c))
                answer=None
                for v in shortest:
                    stats.transitions+=1
                    next_state=residual_choose_one(state,v)
                    if next_state is None:
                        continue
                    rest=visit(next_state)
                    if rest is not None:
                        answer=tuple(sorted((v,)+rest))
                        break
        cache[state]=answer
        return answer

    try:
        found=visit(initial)
    except StateGuardExceeded:
        return dict(status="UNKNOWN",witness=None,
                    reason="UNIQUE_RESIDUAL_STATE_BUDGET",
                    stats=vars(stats).copy(),
                    runtime_bound="O(S * poly(n)); S may be exponential")

    if found is None:
        return dict(status="UNSAT",witness=None,
                    reason="COMPLETE_RESIDUAL_DAG_EXHAUSTION",
                    stats=vars(stats).copy(),
                    runtime_bound="O(S * poly(n)); S may be exponential")
    selected=ones|set(found)
    witness=[int(i in selected) for i in range(n)]
    assert all(sum(witness[v] for v in row)==1 for row in rows)
    assert all(witness[i]==value for i,value in pins.items())
    assert sum(witness)==n//3
    return dict(status="SAT",witness=witness,reason="EXACT_BOOLEAN_WITNESS",
                stats=vars(stats).copy(),
                runtime_bound="O(S * poly(n)); S may be exponential")


def ExactSupportResidualDAG(A,pins=None,max_states=None):
    """Matrix-input wrapper validating the entire legal SCL promise."""
    n=len(A)
    rows=constraints_from_matrix(A)
    return ExactSupportResidualDAG_sparse(rows,n,pins,max_states)


def check_case(name,rows,n,expected,limit=50000):
    answer=ExactSupportResidualDAG_sparse(rows,n,max_states=limit)
    assert answer["status"]==expected,(name,answer["status"],answer["stats"])
    print(f"{name}: {expected}, n={n}, "
          f"states={answer['stats']['distinct_states']}, "
          f"cache_hits={answer['stats']['cache_hits']}, "
          f"transitions={answer['stats']['transitions']}, "
          f"components={answer['stats']['component_splits']}")
    return answer


def main():
    for name,A,status in (
        ("E61_SAT12",build_A(P_SAT,Q_SAT),"SAT"),
        ("E61_UNSAT12",build_A(P_UNSAT,Q_UNSAT),"UNSAT"),
    ):
        rows=constraints_from_matrix(A)
        decision=check_case(name,rows,len(A),status)
        assert ExactSupport(A,max_nodes=20000)["status"]==status
        if status=="SAT":
            for j in (0,2,9,11):
                for val in (0,1):
                    pinned=ExactSupportResidualDAG(A,{j:val})
                    ref=ExactSupport(A,{j:val},max_nodes=20000)
                    assert pinned["status"]==ref["status"]
                    if pinned["witness"] is not None:
                        assert pinned["witness"][j]==val
            bounded=ExactSupportResidualDAG(A,max_states=0)
            assert bounded["status"]=="UNKNOWN" and bounded["witness"] is None
        else:
            assert decision["witness"] is None

    R=tutte12_incidence()
    q63=check_case("E123_UNSAT63",constraints_from_matrix(R),63,"UNSAT")
    assert q63["status"]==ExactSupport(R,max_nodes=0)["status"]
    RT=[list(col) for col in zip(*R)]
    check_case("E65_TRANSPOSE_SAT63",constraints_from_matrix(RT),63,"SAT")

    for label,a,b,status in (
        ("E118_UNSAT90",1,6,"UNSAT"),
        ("E118_SAT90",1,2,"SAT"),
    ):
        src=cyclic_source(9,a,b)
        assert bool(source_solutions(src))==(status=="SAT")
        rows,_,_=e118_target(src)
        verify_target(rows)
        result=check_case(label,rows,len(rows),status)
        reference=ExactSupport(
            [[int(j in row) for j in range(len(rows))] for row in rows],
            max_nodes=20000,
        )
        assert reference["status"]==result["status"]

    # E125 contains an unbounded-treewidth family of CONNECTED legal SCL
    # UNSAT carriers. These are finite benchmark observations ONLY.
    for t in (2,3):
        rows,n=build_splice(R,t)
        check_case(f"E125_TOROIDAL_UNSAT_t{t}",rows,n,"UNSAT")

    # Unlike dense min-plus tables, these SAT toroidal fixtures have a
    # short residual-DAG path. This is not a worst-case size theorem.
    for L in (9,12,15):
        rows=toroidal_triangular_carrier(L)
        check_case(f"TORUS_SAT_L{L}",rows,L*L,"SAT")

    print("EXACT_RESIDUAL_DAG_STATE_IDENTITY = PROVED_ALL_INPUTS")
    print("EXACT_RESIDUAL_DAG_PINNED_WITNESS_AND_GUARD = PROVED")
    print("EXACT_DAG_RUNTIME_O(S_POLY_N) = PROVED; S_MAY_BE_EXPONENTIAL")
    print("GLOBAL_S_LE_POLY_N = NOT_PROVED")
    print("UNIVERSAL_POLY_SolveLinearCubicXSAT = NOT_CONSTRUCTED; P_VS_NP=OPEN")


if __name__=="__main__":
    main()
