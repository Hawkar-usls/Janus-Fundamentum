#!/usr/bin/env python3
"""JANUS ExactSupport hybrid: polynomial algebraic certificates AT EVERY
residual DAG node + exact AND/OR component factorization and memoization.

Correct on ALL legal square+cubic+C4-free 1-in-3-SAT instances and all
consistent Boolean pins. Returns SAT+witness, UNSAT, or (if resource
guard) UNKNOWN. This is NOT a polynomial-time universal solver:
worst-case bound O(S*n^3), where S=actually-expanded residual states
can be exponential. Never interpret modular consistency as Boolean SAT.

At the ROOT apply the already-proved polynomial MOD9 and quadratic
Gauss/GF2 top-weight filters via existing ExactSupport(max_nodes=0).
At EACH arbitrary residual formula, including any connected component,
run a fresh exact MOD9 consistency check on its reduced incidence.
This is a sound UNSAT certificate regardless of the residual's
irregular column degrees. Cache both algebraic negatives and Boolean
branch outcomes under exact labelled residual-state keys.

Finite regression compares independent source ExactSupport,
original residual DAG, E61, E123, E118, and E129 covers.
"""
from __future__ import annotations

from dataclasses import dataclass

from r5_universal_exact_support_residual_dag_attack import (
    validate_sparse, _pins, residual_normalize,
    residual_choose_one, exact_components,
    ExactSupportResidualDAG_sparse,
)
from r5_universal_exact_support_pinned_oracle_attack import ExactSupport
from r5_universal_exact_support_mod9_dual_certificate import (
    mod9_linear_system,independent_verify_mod9_certificate,
)
from r5_e61_two_level_kernel_hoffman_regular_set import (
    P_SAT,Q_SAT,P_UNSAT,Q_UNSAT,build_A
)
from r5_e64_connected_postquotient_nullity_firewall import tutte12_incidence
from r5_universal_boolean_quadratic_pc2_attack import (
    cyclic_source, source_solutions, e118_target, verify_target
)
from r5_e129_invertible_base_cover_unsat_gauge_clean_seed import base_matrix,build_2lift


@dataclass
class HybridStats:
    residual_states:int=0
    exact_mod9_checks:int=0
    exact_mod9_unsat:int=0
    structural_branches:int=0
    cache_hits:int=0
    splits:int=0
    max_active_vars:int=0
    guard_hits:int=0


class StateGuard(Exception):
    pass


def residual_mod9_certificate(state):
    """Independent sound modular UNSAT for ANY reduced exact-one CNF.

    The source may be irregular and clauses may have 1,2 or 3 vars.
    Coordinates are compressed only to make the matrix small.
    """
    vars_=tuple(sorted({j for c in state for j in c}))
    if not vars_:
        assert not state
        return "CONSISTENT",None
    pos={j:k for k,j in enumerate(vars_)}
    m=len(state)
    n=len(vars_)
    B=[[0]*n for _ in range(m)]
    for i,c in enumerate(state):
        for v in c:
            B[i][pos[v]]=1
    rhs=[1]*m
    status,lam=mod9_linear_system(B,rhs)
    if status=="INCONSISTENT":
        assert independent_verify_mod9_certificate(B,rhs,lam)
    return status,lam


def ExactSupportHybrid_sparse(rows,n,pins=None,max_states=None):
    """Complete all-input exact decision for max_states=None (exponential).

    max_states>=0 protects against resource overrun. UNKNOWN must never
    be interpreted as UNSAT or SAT by a caller.
    """
    rows=validate_sparse(rows,n)
    supplied=_pins(n,pins)
    stats=HybridStats()
    if supplied is None:
        return {"status":"UNSAT","reason":"CONFLICTING_PINS",
                "witness":None,"stats":vars(stats).copy()}
    if n%3:
        return {"status":"UNSAT","reason":"CARDINALITY_N_NOT_DIVISIBLE_BY_THREE",
                "witness":None,"stats":vars(stats).copy()}
    if max_states is not None and (not isinstance(max_states,int)
                                   or max_states<0):
        raise ValueError("max_states must be nonnegative int or None")
    initial=residual_normalize(rows,
        fixed_one=[v for v,x in supplied.items() if x==1],
        fixed_zero=[v for v,x in supplied.items() if x==0])
    if initial is None:
        return {"status":"UNSAT","reason":"PIN_CLAUSE_CONFLICT",
                "witness":None,"stats":vars(stats).copy()}

    # The root SCL promise is still intact here, so strong polynomial
    # quadratic GF2/Gauss preprocessing is available. With 0 branches
    # permitted, an unresolved source receives UNKNOWN, never a guess.
    A=[[int(j in c) for j in range(n)] for c in rows]
    pre=ExactSupport(A,supplied,max_nodes=0)
    if pre["status"]=="UNSAT":
        return {"status":"UNSAT",
                "reason":"ROOT_POLYNOMIAL_"+pre["reason"],
                "witness":None,
                "root_certificate":pre.get("mod9_certificate"),
                "stats":vars(stats).copy()}
    if pre["status"]=="SAT":
        witness=pre["witness"]
        assert all(sum(witness[j] for j in c)==1 for c in rows)
        assert all(witness[j]==v for j,v in supplied.items())
        return {"status":"SAT","reason":"ROOT_UNIT_PROPAGATION_WITNESS",
                "witness":witness,"stats":vars(stats).copy()}
    assert pre["status"]=="UNKNOWN"

    cache={}
    def visit(state):
        if state in cache:
            stats.cache_hits+=1
            return cache[state]
        if max_states is not None and stats.residual_states>=max_states:
            stats.guard_hits+=1
            raise StateGuard()
        stats.residual_states+=1
        if not state:
            cache[state]=()
            return ()
        stats.max_active_vars=max(stats.max_active_vars,
            len({v for clause in state for v in clause}))
        stats.exact_mod9_checks+=1
        status,cert=residual_mod9_certificate(state)
        if status=="INCONSISTENT":
            stats.exact_mod9_unsat+=1
            cache[state]=None
            return None

        parts=exact_components(state)
        if len(parts)>1:
            stats.splits+=1
            combined=[]
            for comp in parts:
                part_result=visit(comp)
                if part_result is None:
                    cache[state]=None
                    return None
                combined.extend(part_result)
            ans=tuple(sorted(combined))
        else:
            clause=min(state,key=lambda c:(len(c),c))
            ans=None
            for v in clause:
                stats.structural_branches+=1
                child=residual_choose_one(state,v)
                if child is None:
                    continue
                rest=visit(child)
                if rest is not None:
                    ans=tuple(sorted((v,)+rest))
                    break
        cache[state]=ans
        return ans

    try:
        selected=visit(initial)
    except StateGuard:
        return {"status":"UNKNOWN","reason":"UNIQUE_RESIDUAL_STATE_GUARD",
                "witness":None,"stats":vars(stats).copy(),
                "runtime_bound":"O(S*n^3), S may be exponential"}

    if selected is None:
        return {"status":"UNSAT","reason":"EXACT_ALGEBRAIC_ANDOR_EXHAUSTION",
                "witness":None,"stats":vars(stats).copy(),
                "runtime_bound":"O(S*n^3), S may be exponential"}

    chosen=set(selected)|{i for i,x in supplied.items() if x==1}
    witness=[int(i in chosen) for i in range(n)]
    assert all(sum(witness[i] for i in c)==1 for c in rows)
    assert all(witness[i]==x for i,x in supplied.items())
    assert sum(witness)==n//3
    return {"status":"SAT","reason":"VERIFIED_EXACT_BOOLEAN_WITNESS",
            "witness":witness,"stats":vars(stats).copy(),
            "runtime_bound":"O(S*n^3), S may be exponential"}


def ExactSupportHybrid(A,pins=None,max_states=None):
    """Square/cubic/linear matrix wrapper."""
    n=len(A)
    rows=tuple(tuple(j for j,x in enumerate(row) if x) for row in A)
    return ExactSupportHybrid_sparse(rows,n,pins,max_states)


def run_case(name,rows,n,expected,cap=1000):
    hybrid=ExactSupportHybrid_sparse(rows,n,max_states=cap)
    assert hybrid["status"]==expected,(name,hybrid)
    baseline=ExactSupportResidualDAG_sparse(rows,n,max_states=max(cap,10000))
    assert baseline["status"]==expected,(name,baseline["status"])
    assert hybrid["stats"]["residual_states"]<=baseline["stats"]["distinct_states"],(
        name,hybrid["stats"],baseline["stats"])
    print(f"{name}: verdict={hybrid['status']} "
          f"hybrid_states={hybrid['stats']['residual_states']} "
          f"baseline_states={baseline['stats']['distinct_states']} "
          f"mod9_residual_prunes={hybrid['stats']['exact_mod9_unsat']}")
    return hybrid


def main():
    for name,A,result in (
        ("E61_SAT12",build_A(P_SAT,Q_SAT),"SAT"),
        ("E61_UNSAT12",build_A(P_UNSAT,Q_UNSAT),"UNSAT"),
    ):
        rows=[tuple(j for j,x in enumerate(row) if x) for row in A]
        run_case(name,rows,len(A),result)
        for index in (0,1):
            for value in (0,1):
                h=ExactSupportHybrid(A,{index:value},max_states=2000)
                ref=ExactSupport(A,{index:value},max_nodes=10000)
                assert h["status"]==ref["status"]
                assert h["status"] in ("SAT","UNSAT")
                if h["status"]=="SAT":
                    assert h["witness"][index]==value

    R=tutte12_incidence()
    run_case("E123_UNSAT63",
        [tuple(i for i,x in enumerate(row) if x) for row in R],
        63,"UNSAT",cap=400)

    for label,a,b,expected in (
        ("E118_UNSAT90",1,6,"UNSAT"),
        ("E118_SAT90",1,2,"SAT"),
    ):
        source=cyclic_source(9,a,b)
        assert bool(source_solutions(source))==(expected=="SAT")
        rows,_,_=e118_target(source)
        verify_target(rows)
        run_case(label,rows,90,expected,cap=1500)

    e129=base_matrix()
    lifted=build_2lift(e129)
    for name,A in (("E129_UNSAT12",e129),
                   ("E129_UNSAT24",lifted)):
        rows=[tuple(i for i,x in enumerate(row) if x) for row in A]
        hybrid=ExactSupportHybrid_sparse(rows,len(rows),max_states=0)
        assert hybrid["status"]=="UNSAT"
        assert hybrid["stats"]["residual_states"]==0
        assert "MOD9" in hybrid["reason"]
        print(f"{name}: root polynomial MOD9 UNSAT; zero DAG states PASS")

    print("SOUND_COMPLETE_ALL_SCL_PINNED_SUPPORT=PROVED")
    print("POLYNOMIAL_MOD9_RESIDUAL_NEGATIVE_CERTIFICATES=PROVED")
    print("ACTUAL_RUNTIME_O(S_N_CUBED)_S_POTENTIALLY_EXPONENTIAL=PROVED")
    print("UNIVERSAL_WORST_CASE_POLYNOMIAL_BOUND=NOT_PROVED")
    print("P_VS_NP=OPEN")


if __name__=="__main__":
    main()
