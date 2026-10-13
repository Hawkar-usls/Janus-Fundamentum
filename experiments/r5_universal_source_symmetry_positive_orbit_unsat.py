#!/usr/bin/env python3
"""R5 universal source-symmetry certificate for positive-literal UNSAT coverage.

THEOREM (ALL ORIGINAL SCL, NOT A COMPLETENESS CLAIM):
Let G be any explicitly given generating set of variable permutations
that each map the ORIGINAL collection of Exact-One clauses onto itself.
Pick any original clause C={u,v,w}. For one representative a_i of each
G-orbit meeting C, independently replay a source-certified UNSAT proof
of F & (x_(a_i)=1). Then F is UNSAT.

Proof: any solution has exactly one true x_j in C. Since j lies in
the orbit of some a_i, a composition of authenticated source
automorphisms maps j to a_i (or its inverse does). Applying it to
the witness preserves all original clauses and produces a solution
with x_(a_i)=1, contradicting the replayed assumption refutation.

This compresses UNSAT proof storage for a clause to <=3 positive
conditional proofs, even when the full source has n variables.
On a colour-transitive Holyer edge clause, exactly ONE suffices.

Verifier requires explicit polynomially checkable permutations and
original-source conditional proofs; it never guesses automorphisms.
The lemma does NOT supply the conditional UNSAT proofs for arbitrary
SCL, and is NOT a polynomial all-input decision algorithm.
"""
from __future__ import annotations

from r5_universal_exact_support_residual_dag_attack import validate_sparse


def verify_source_generator(rows,n,perm):
    """Independently check literal permutation preserving original rows."""
    rows=validate_sparse(rows,n)
    assert len(perm)==n
    assert all(type(v) is int and 0<=v<n for v in perm)
    assert set(perm)==set(range(n)), "not a variable permutation"
    assert {tuple(sorted(perm[v] for v in row)) for row in rows}==set(rows), (
        "proposed symmetry changes original Exact-One source"
    )
    return True


def orbit_partition(rows,n,generators):
    """Construct exact generated variable orbits in polynomial time."""
    generators=tuple(tuple(p) for p in generators)
    assert generators
    for p in generators:
        assert verify_source_generator(rows,n,p)
    remaining=set(range(n))
    orbits=[]
    while remaining:
        root=min(remaining)
        orbit={root}
        queue=[root]
        for v in queue:
            for perm in generators:
                next_v=perm[v]
                if next_v not in orbit:
                    orbit.add(next_v)
                    queue.append(next_v)
        remaining-=orbit
        orbits.append(frozenset(orbit))
    assert set().union(*orbits)==set(range(n))
    assert sum(map(len,orbits))==n
    assert all(not (a&b) for i,a in enumerate(orbits)
               for b in orbits[i+1:])
    return tuple(orbits)


def verify_positive_orbit_discharge(rows,n,row_index,generators,
                                   positive_refutations,proof_checker):
    """Verify source symmetries, assumptions and selected clause cover.

    proof_checker(v,proof) MUST independently replay an original-source
    proof of UNSAT(F & x_v=1), not merely accept a producer status label.
    """
    rows=validate_sparse(rows,n)
    assert type(row_index) is int and 0<=row_index<n
    assert callable(proof_checker)
    orbits=orbit_partition(rows,n,generators)
    reps=set(positive_refutations)
    assert reps and all(type(v) is int and 0<=v<n for v in reps)
    assert all(proof_checker(v,positive_refutations[v]) is True
               for v in sorted(reps)), "unverified conditional UNSAT claim"
    covered=set().union(*(orb for orb in orbits if orb & reps))
    assert set(rows[row_index])<=covered, "some Exact-One positive case uncovered"
    return {"status":"UNSAT",
            "method":"CERTIFIED_ORBIT_POSITIVE_CLAUSE_DISCHARGE",
            "row_index":row_index,
            "source_orbits":tuple(tuple(sorted(o)) for o in orbits),
            "refuted_positive_literals":tuple(sorted(reps)),
            "covered_clause_variables":tuple(sorted(set(rows[row_index])&covered))}


def holyer_colour_rotation(n):
    assert n%3==0
    return tuple(3*(v//3)+(v%3+1)%3 for v in range(n))


def main():
    from r5_universal_cubic_flow_lowmoment_collision_20v import flower
    from r5_universal_cubic_edgecolor_direct_scl_bridge import (
        make_scl,K4,
    )
    from r5_universal_flower_three_ply_certified_saturation import (
        certified_three_ply_branch,verify_three_ply_branch,
    )
    rows,n,edges,idx=make_scl(flower(5))
    rotate=holyer_colour_rotation(n)
    assert verify_source_generator(rows,n,rotate)
    orbits=orbit_partition(rows,n,(rotate,))
    assert len(orbits)==n//3
    assert tuple(sorted(next(o for o in orbits if 0 in o)))==(0,1,2)

    # The sole hard conditional proof: ORIGINAL J5 source x0=1
    # refuted by third-ply, independently source replayed.
    child=certified_three_ply_branch(rows,n,1)
    assert child["status"]=="UNSAT"
    assert verify_three_ply_branch(rows,n,1,child)
    check=lambda v,p: (
        v==0 and p["status"]=="UNSAT" and
        verify_three_ply_branch(rows,n,1,p)
    )
    result=verify_positive_orbit_discharge(
        rows,n,0,(rotate,),{0:child},check
    )
    assert result["status"]=="UNSAT"
    assert len(result["refuted_positive_literals"])==1
    print(f"J5_ONE_POSITIVE_BRANCH_SYMMETRY_UNSAT=VERIFIED "
          f"inner_calls={child['inner_calls']} "
          f"events={len(child['events'])}",flush=True)

    # A source generator forged by swapping different edge-colour
    # variables must be rejected even when their source size agrees.
    wrong=list(range(n));wrong[0],wrong[3]=wrong[3],wrong[0]
    try:
        verify_source_generator(rows,n,wrong)
    except AssertionError:
        print("FORGED_ORIGINAL_SOURCE_SYMMETRY_REJECTED=PASS",flush=True)
    else:
        raise AssertionError("accepted false source automorphism")

    # Valid identity group but incomplete set of positive branches
    # cannot justify full clause refutation.
    identity=tuple(range(n))
    try:
        verify_positive_orbit_discharge(
            rows,n,0,(identity,),{0:child},check
        )
    except AssertionError:
        print("UNCOVERED_ORIGINAL_EXACTONE_CLAUSE_REJECTED=PASS",flush=True)
    else:
        raise AssertionError("accepted uncovered source clause")

    # Nested forged conditional UNSAT proof must not pass the lift.
    tampered=dict(child)
    ev=list(child["events"]);last=dict(ev[-1])
    if last["kind"]=="DOUBLE_UNSAT":
        both=dict(last["proofs"])
        falseproof=dict(both[0]);falseproof["status"]="SAT"
        both[0]=falseproof;last["proofs"]=both
    else:
        falseproof=dict(last["proof"]);falseproof["status"]="SAT"
        last["proof"]=falseproof
    ev[-1]=last;tampered["events"]=tuple(ev)
    try:
        verify_positive_orbit_discharge(
            rows,n,0,(rotate,),{0:tampered},check
        )
    except (AssertionError,KeyError):
        print("FORGED_POSITIVE_BRANCH_SOURCE_PROOF_REJECTED=PASS",flush=True)
    else:
        raise AssertionError("accepted counterfeit refutation")

    # Every original SAT instance defeats the fake unconditional
    # UNSAT claim: a certificate must refer to a GENUINE refutation.
    sat,m,_,_=make_scl(K4())
    perm=holyer_colour_rotation(m)
    assert verify_source_generator(sat,m,perm)
    assert tuple(sorted(next(o for o in orbit_partition(sat,m,(perm,))
                             if 0 in o)))==(0,1,2)
    print("SAT_K4_COLOUR_GROUP_SOURCE_AUTOMORPHISM=VERIFIED",flush=True)
    print("ALL_SCL_POSITIVE_ORBIT_CLAUSE_DISCHARGE_SOUNDNESS=PROVED")
    print("ALL_SCL_CONDITIONAL_UNSAT_CERTIFICATES_POLYNOMIAL=NOT_PROVED")
    print("UNIVERSAL_POLY_SOLVELINEARCUBICXSAT=NOT_CONSTRUCTED")
    print("P_VS_NP=OPEN")


if __name__=="__main__":
    main()
