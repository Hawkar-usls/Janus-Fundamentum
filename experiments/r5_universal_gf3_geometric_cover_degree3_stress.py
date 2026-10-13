#!/usr/bin/env python3
"""R5 geometric source stress test of proposed uniform F3 degree-3 bound.

A 15x15 source is generated from points of a 4-dimensional
symplectic vector space over F2: nonzero vectors 1..15, lines
{a,b,a xor b} with the standard alternating bilinear form.
Each point and line has degree3, any two lines overlap in <=1
point, and Tanner girth>=8. This is a legal square cubic
linear original Positive Exact-One SCL15, with exactly 6
independently source-enumerated witnesses.

A random cyclic s-sheet covering of its Tanner incidence graph
with s=2 and 3 is ALSO a legal original SCL on n=15s, and every
original SAT witness lifts by copying bits on all s sheets.
We deliberately introduce source-preserving 2-switches and
find candidate original UNSAT sources on n=30 and45.

Every reported UNSAT must have a complete independent original
Exact-One exact-cover DAG certificate; every reported degree3
refutation must be independently reconstructed from ORIGINAL
source row/multiplier coefficients (not mere Gaussian rank).

All outcomes are finite; this test neither proves uniform degree3
completeness nor any general running-time bound.
"""
from __future__ import annotations

import random
from itertools import combinations
from r5_universal_exact_support_residual_dag_attack import validate_sparse
from r5_universal_gf3_degree3_adversarial_scl27_search import (
    original_source_exact_solve,verify_original_unsat_dag,
)
from r5_universal_gf3_degree3_petersen_source_certificate import (
    certificate_from_dag,independent_original_certificate_replay,
)
from r5_universal_triple_fano_connected_divisible_high_girth_unsat import (
    certify_connected_tanner
)


def sp(a,b):
    terms=((0,1),(1,0),(2,3),(3,2))
    return sum(((a>>i)&1)*((b>>j)&1)
               for i,j in terms)%2


def symplectic_source15():
    lines={tuple(sorted((a-1,b-1,(a^b)-1)))
           for a in range(1,16) for b in range(a+1,16)
           if sp(a,b)==0}
    source=validate_sparse(tuple(sorted(lines)),15)
    assert len(source)==15
    assert certify_connected_tanner(source,15)
    assert all(sum(v in row for row in source)==3 for v in range(15))
    # Exact original Tanner girth>=8: linearity already excludes
    # quadrilaterals. A Tanner 6-cycle would be three distinct
    # source lines that pairwise meet in 3 distinct points.
    # On F2^4 symplectic space these 3 points would be 3
    # independent pairwise orthogonal vectors, impossible
    # in a rank-4 alternating nondegenerate form (maximal
    # totally isotropic dimension is 2). Check directly too.
    for a,b,c in combinations(source,3):
        ab=set(a)&set(b)
        ac=set(a)&set(c)
        bc=set(b)&set(c)
        if ab and ac and bc:
            assert len({next(iter(ab)),next(iter(ac)),
                        next(iter(bc))})!=3

    truth=original_source_exact_solve(source,15)
    assert truth["status"]=="SAT"
    assert all(sum(truth["witness"][v] for v in row)==1 for row in source)
    return source


def cyclic_source_cover(base,sheets,seed):
    base=validate_sparse(base,len(base))
    rng=random.Random(seed)
    k=len(base)
    shifts={(i,v):rng.randrange(sheets)
            for i,row in enumerate(base) for v in row}
    lift=[]
    for i,row in enumerate(base):
        for s in range(sheets):
            lift.append(tuple(sorted(
                sheets*v+(s+shifts[(i,v)])%sheets for v in row
            )))
    source=validate_sparse(lift,k*sheets)
    assert certify_connected_tanner(source,k*sheets)
    original=original_source_exact_solve(base,k)["witness"]
    witness=tuple(original[v//sheets] for v in range(k*sheets))
    assert all(sum(witness[v] for v in row)==1 for row in source)
    return source,witness


def single_source_2switch(source,n,rng):
    source=list(validate_sparse(source,n))
    for attempt in range(7000):
        i,j=rng.sample(range(n),2)
        x=rng.choice(source[i]);y=rng.choice(source[j])
        if x==y or x in source[j] or y in source[i]:
            continue
        p,q=source[i],source[j]
        source[i]=tuple(sorted((set(p)-{x})|{y}))
        source[j]=tuple(sorted((set(q)-{y})|{x}))
        try:
            res=validate_sparse(source,n)
            if certify_connected_tanner(res,n):
                return res
        except (ValueError,AssertionError):
            pass
        source[i],source[j]=p,q
    raise AssertionError("SOURCE_2SWITCH_RESOURCE_GUARD")


def geometric_source_adversarial(n,sheets,seed,trial_limit=16):
    base=symplectic_source15()
    cover,original=cyclic_source_cover(base,sheets,seed)
    assert n==15*sheets
    print(f"SYMPLECTIC_SOURCE_COVER_SCL{n}=ORIGINAL_SAT "
          f"TRUE_WITNESS_VERIFIED",flush=True)
    rng=random.Random(seed+424242)
    for trial in range(1,trial_limit+1):
        # Mutate a fresh covered legal source by successive
        # source-audited 2-switches. A SAT result is honestly
        # reported and does not become a negative proof.
        candidate=cover
        for _ in range(1+(trial%4)):
            candidate=single_source_2switch(candidate,n,rng)
        truth=original_source_exact_solve(
            candidate,n,limit=1000000
        )
        assert truth["status"]!="UNKNOWN_RESOURCE_LIMIT",truth
        if truth["status"]=="SAT":
            continue
        assert verify_original_unsat_dag(candidate,n,truth["dag"])
        proof=certificate_from_dag(
            candidate,n,max_updates=100000000
        )
        assert proof["status"]=="ORIGINAL_SOURCE_GF3_DEGREE3_UNSAT_CERTIFIED"
        assert independent_original_certificate_replay(
            candidate,n,proof["source_coefficient_combination"]
        )
        print(f"ADVERSARIAL_SYMPLECTIC_SCL{n}_TRIAL{trial}="
              f"UNSAT_EXACT_SOURCE_DAG_{truth['dag_size']} "
              f"DEGREE3_SOURCE_CERT_{proof['certificate_terms']} "
              f"rank_{proof['pivot_rank']}",flush=True)
        return candidate,proof
    print(f"ADVERSARIAL_SYMPLECTIC_SCL{n}="
          f"NO_UNSAT_WITHIN_{trial_limit}_SOURCE_TRIALS",flush=True)
    return None,None


def main():
    base=symplectic_source15()
    count=sum(
        all(sum((mask>>v)&1 for v in row)==1 for row in base)
        for mask in range(1<<15)
    )
    assert count==6
    print("SYMPLECTIC_W32_SCL15_SOURCE_SAT_COUNT6=VERIFIED",flush=True)
    for sheets,seed in ((2,20261013),(3,20261014)):
        result,proof=geometric_source_adversarial(
            15*sheets,sheets,seed
        )
        if proof:
            assert proof["certificate_terms"]>0
    print("GEOMETRIC_SCL15_SCL30_SCL45_FINITE_CERTIFICATES_ONLY")
    print("ALL_SCL_FIXED_DEGREE3_COMPLETENESS=NOT_PROVED")
    print("GENERAL_POLY_LOOP_ZERO_TEST=NOT_CONSTRUCTED")
    print("UNIVERSAL_POLY_SOLVELINEARCUBICXSAT=NOT_CONSTRUCTED")
    print("P_VS_NP=OPEN")


if __name__=="__main__":
    main()
