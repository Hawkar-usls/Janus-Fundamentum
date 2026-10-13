#!/usr/bin/env python3
"""R5 deterministic search for REAL SCL UNSAT atoms invisible to frozen
F3 Boolean degree-3 polynomial calculus.

This is a finite, adversarial search for a degree-three LOWER
BOUND, not a proof against all polynomial methods.

Start from source-legal SAT K3,3 Holyer SCL27 and take 50 random
source-correct Tanner 2-switches: replace incidences
(row_i,variable_a),(row_j,variable_b) by
(row_i,variable_b),(row_j,variable_a), rejecting any nonlegal
output and independently replaying cubic+linear source legality.
The pseudorandom seed and algorithm are fixed for reproducibility.

For any candidate exact source F, independent exact-cover DFS
on ORIGINAL rows either returns a directly checked SAT witness
or an UNSAT DAG of uncovered ORIGINAL row subsets. Every UNSAT
DAG mask gives a source row whose every legal 3-row-cover
branch points to a smaller DAG mask; root present and no
zero-mask included, so an independent verifier certifies UNSAT.

For a SOURCE-CERTIFIED UNSAT candidate, run the complete exact
GF3 multilinear degree-3 polynomial-calculus span test. If
degree-3 constant refutation is absent, construct an independent
source-verifiable dual moment y with y(1)=1 and
y(E_i*x_M)=0 for ALL ORIGINAL source clauses i and
squarefree multiplier monomials |M|<=2.

This PAIR of independent certificates proves a genuine
fixed-degree-3 method obstruction on that original legal SCL.
It does NOT prove superpolynomial complexity of general
algorithms, NOR that larger proof degree must grow with n.

If no candidate is found within deterministic resource cap,
report NO_MATCH_FOUND only. Never infer universal theorem.
"""
from __future__ import annotations
import random
from r5_universal_exact_support_residual_dag_attack import validate_sparse
from r5_universal_cubic_edgecolor_direct_scl_bridge import make_scl,K33
from r5_universal_gf3_boolean_degree3_pc_probe import (
    degree3_source_span,verify_dual_source,multilinear_monomials
)


def original_exact_cover_options(rows,n,uncovered,covers):
    """Pick a most-constrained original source row and all columns
    that cover that row WITHOUT overlapping previously covered rows.
    """
    best=None
    for rowid,row in enumerate(rows):
        if (uncovered>>rowid)&1:
            choices=tuple(v for v in row if
                          covers[v]&uncovered==covers[v])
            if best is None or len(choices)<len(best[1]):
                best=(rowid,choices)
            if not choices:
                break
    assert best is not None
    return best


def original_source_exact_solve(rows,n,limit=500000):
    """Worst-case exponential, finite original-source negative proof."""
    rows=validate_sparse(rows,n)
    covers=[0]*n
    for i,row in enumerate(rows):
        for v in row:covers[v]|=1<<i
    assert all(v.bit_count()==3 for v in covers)
    dead=set()
    visits=0
    class ResourceLimit(Exception):pass
    def go(mask):
        nonlocal visits
        visits+=1
        if visits>limit:raise ResourceLimit
        if mask==0:return ()
        if mask in dead:return None
        row,choices=original_exact_cover_options(
            rows,n,mask,covers
        )
        for variable in choices:
            rest=go(mask^covers[variable])
            if rest is not None:
                return (variable,)+rest
        dead.add(mask)
        return None
    try:
        result=go((1<<n)-1)
    except ResourceLimit:
        return {"status":"UNKNOWN_RESOURCE_LIMIT","visits":visits}
    if result is not None:
        witness=tuple(int(v in result) for v in range(n))
        assert len(result)==n//3
        assert all(sum(witness[v] for v in row)==1 for row in rows)
        return {"status":"SAT","witness":witness,"visits":visits}
    assert verify_original_unsat_dag(rows,n,dead)
    return {"status":"UNSAT_CERTIFIED","dag":frozenset(dead),
            "dag_size":len(dead),"visits":visits}


def verify_original_unsat_dag(rows,n,dead):
    """Independent COMPLETE proof checker against source row IDs."""
    rows=validate_sparse(rows,n)
    assert 0 not in dead
    assert (1<<n)-1 in dead
    cover=[sum((1<<i) for i,row in enumerate(rows) if v in row)
           for v in range(n)]
    assert all(z.bit_count()==3 for z in cover)
    for mask in dead:
        assert type(mask) is int and 0<mask<=(1<<n)-1
        assert all(z&mask==z or (z&mask)!=z for z in cover)
        r,options=original_exact_cover_options(rows,n,mask,cover)
        assert (mask>>r)&1
        for v in options:
            nxt=mask^cover[v]
            assert nxt in dead,("forged UNSAT successor",mask,v,nxt)
            assert nxt.bit_count()<mask.bit_count()
    return True


def source_legal_switched(rows,n,rng,accepted=50,attempt_limit=15000):
    rows=validate_sparse(rows,n)
    state=list(rows)
    successful=0
    for t in range(attempt_limit):
        i,j=rng.sample(range(n),2)
        a=rng.choice(state[i]); b=rng.choice(state[j])
        if a==b or a in state[j] or b in state[i]:
            continue
        ra=state[i];rb=state[j]
        state[i]=tuple(sorted((set(ra)-{a})|{b}))
        state[j]=tuple(sorted((set(rb)-{b})|{a}))
        try:
            verify=validate_sparse(state,n)
        except ValueError:
            state[i]=ra
            state[j]=rb
            continue
        state=list(verify)
        successful+=1
        if successful==accepted:
            break
    assert successful==accepted,"SOURCE_SWITCH_RESOURCE_LIMIT"
    result=validate_sparse(state,n)
    assert len(result)==n
    return result


def main():
    from r5_universal_triple_fano_connected_divisible_high_girth_unsat import (
        certify_connected_tanner
    )
    rng=random.Random(20261013)
    base,n,_,_=make_scl(K33())
    assert n==27
    found=None
    full=0
    unsats=0
    for trial in range(1,17):
        source=source_legal_switched(base,n,rng,accepted=50)
        if not certify_connected_tanner(source,n):
            continue
        full+=1
        proof=original_source_exact_solve(source,n)
        assert proof["status"]!="UNKNOWN_RESOURCE_LIMIT",proof
        if proof["status"]=="SAT":
            print(f"RANDOM_SCL27_TRIAL_{trial}_SOURCE_SAT_WITNESS_VERIFIED",
                  flush=True)
            continue
        unsats+=1
        assert verify_original_unsat_dag(source,n,proof["dag"])
        alg=degree3_source_span(source,n,max_updates=45000000)
        print(f"RANDOM_SCL27_TRIAL_{trial}=SOURCE_UNSAT "
              f"DAG_{proof['dag_size']} "
              f"PC_DEG3_{alg['status']} "
              f"RANK_{alg['rank']} UPDATES_{alg['updates']}",
              flush=True)
        if alg["status"]=="DEGREE3_NO_REFUTATION_DUAL_CERTIFIED":
            mons,key=multilinear_monomials(n,3)
            assert verify_dual_source(
                source,n,alg["dual"],mons,key
            )==n*(1+n+n*(n-1)//2)
            found=(trial,source,proof,alg)
            break

    if found is not None:
        trial,source,proof,alg=found
        print("SOURCE_SCL27_CERTIFIED_UNSAT_AND_DEGREE3_DUAL="
              f"FOUND trial={trial} dag={proof['dag_size']} "
              f"dual_support={alg['dual_support']}",flush=True)
        print("FROZEN_ORIGINAL_SCL27_ROWS="+repr(source),flush=True)
        print("SOURCE_CERTIFICATE_FROZEN_DEGREE3_METHOD_NOGO=PROVED",
              flush=True)
    else:
        print(f"NO_DEGREE3_UNSAT_COUNTEREXAMPLE_IN_FINITE_SEARCH "
              f"connected_trials={full} unsats={unsats}",flush=True)
        print("DEGREE3_ALL_SCL_COMPLETENESS=NOT_PROVED",flush=True)

    print("GENERAL_POLY_BOOLEAN_PC_COMPLETENESS=NOT_PROVED")
    print("UNIVERSAL_POLY_SOLVELINEARCUBICXSAT=NOT_CONSTRUCTED")
    print("P_VS_NP=OPEN")


if __name__=="__main__":
    main()
