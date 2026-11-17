#!/usr/bin/env python3
"""R5 exact-support ACTUALLY VISITED DAG stress on deterministic E123 2-lifts.

This is a direct all-size legal-instance stress rather than an enumeration
of *possible* reachable states.

The 2-lift of a square cubic linear incidence system duplicates every
variable/check into two sheets; every original incidence chooses a
permutation of the two sheets. The new system is still square, cubic
and C4-free. Proof:
 - each lifted check sees exactly three distinct columns,
 - each lifted variable appears once per original incident check,
 - any two lifted checks with two shared variables would project to
   two shared base variables; if based on the SAME original check,
   its two lifts are disjoint; if based on distinct base checks,
   this contradicts original linearity.

A fixed-seed hierarchy from E123 (q63) gives sizes 63,126,252,504.
The EXPLICIT observable is S_explored, the number of cache states
actually expanded by the EXACT frozen deterministic solver, NOT
2^n potential states or a claim about polynomial complexity.

At each cap the output is SAT, UNSAT or UNKNOWN. UNKNOWN is never
treated as UNSAT. A SAT verdict contains a checked Boolean witness.
The upper limit is only a measurement-resource guard; a bounded finite
experiment cannot prove asymptotic worst-case time complexity.
"""
from __future__ import annotations

from collections import Counter
from random import Random

from r5_e64_connected_postquotient_nullity_firewall import tutte12_incidence
from r5_universal_exact_support_residual_dag_attack import (
    validate_sparse, ExactSupportResidualDAG_sparse,
)


def two_lift(base_rows, n, rng):
    """Square+cubic+linear preserving 2-cover of a base incidence system."""
    base=validate_sparse(base_rows,n)
    lifted=[]
    for row in base:
        signs=[rng.randrange(2) for _ in row]
        for layer in (0,1):
            lifted.append(tuple(
                sorted(2*v+(sign^layer)
                       for v,sign in zip(row,signs))
            ))
    out=validate_sparse(lifted,2*n)
    assert len(out)==2*n
    # The lifted base-check pair has DISJOINT three-point supports.
    paired={}
    for row in out:
        parent=tuple(sorted(v//2 for v in row))
        paired.setdefault(parent,[]).append(row)
    assert len(paired)==n
    assert all(len(pair)==2 and not(set(pair[0])&set(pair[1]))
               for pair in paired.values())
    return out


def hierarchy(seed=9421,levels=4):
    base=tutte12_incidence()
    n=len(base)
    rows=validate_sparse(
        [tuple(j for j,v in enumerate(r) if v) for r in base],
        n
    )
    rng=Random(seed)
    yield n,rows
    for _ in range(levels-1):
        rows=two_lift(rows,n,rng)
        n*=2
        yield n,rows


def main():
    # Cap values are fixed reproducible budgets, NOT claimed
    # polynomial upper bounds. The bound applies to actual
    # distinct expanded memo states in the frozen algorithm.
    caps={63:2000,126:8000,252:10000,504:1500}
    recorded=[]
    for n,rows in hierarchy():
        assert n in caps
        result=ExactSupportResidualDAG_sparse(
            rows,n,max_states=caps[n]
        )
        status=result["status"]
        stats=result["stats"]
        assert status in ("SAT","UNSAT","UNKNOWN")
        if status=="SAT":
            witness=result["witness"]
            assert witness is not None and len(witness)==n
            assert all(sum(witness[j] for j in r)==1 for r in rows)
        else:
            assert result["witness"] is None
        if status=="UNKNOWN":
            assert stats["guard_hits"]>0
        assert 0<=stats["distinct_states"]<=caps[n]
        recorded.append((n,status,stats["distinct_states"]))
        print(
            f"E123_2LIFT_LEVEL n={n} cap={caps[n]} "
            f"status={status} ACTUALLY_VISITED_S={stats['distinct_states']} "
            f"transitions={stats['transitions']} "
            f"cache_hits={stats['cache_hits']} "
            f"component_splits={stats['component_splits']}"
        )
    assert recorded[0][1]=="UNSAT"
    assert recorded[0][2]>=100
    assert any(n>=126 for n,_,_ in recorded)
    print("TWO_LIFTS_PRESERVE_SQUARE_CUBIC_C4FREE = PROVED_AND_CHECKED")
    print("ACTUAL_RESIDUAL_DAG_VISITS = FINITE_MEASUREMENT_NOT_THEOREM")
    print("UNKNOWN_NEVER_PROMOTED_TO_UNSAT = CHECKED")
    print("EXPONENTIAL_WORST_CASE_S_VISITED_LOWER_BOUND = NOT_PROVED")
    print("POLYNOMIAL_WORST_CASE_S_VISITED_UPPER_BOUND = NOT_PROVED")
    print("UNIVERSAL_POLYNOMIAL_SUPPORT = NOT_CONSTRUCTED; P_VS_NP=OPEN")


if __name__=="__main__":
    main()
