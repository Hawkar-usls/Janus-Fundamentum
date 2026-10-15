#!/usr/bin/env python3
"""R5 connected SCL Coverage Breaker with legal bipartite-incidence 2-switches.

Swap (clauseA,varA) and (clauseB,varB) across previously DISJOINT
source components. This preserves each degree-3 constraint, while
validate_scl independently checks source linearity (no length-4
incidence cycles). Connectedness is checked in source incidence,
NOT asserted from construction.

For 2-K4 (36 variables) variations with a preserved witness, record
exact SAT counts by polynomial-capped local affine enumeration.
For 4-K4 (72 vars), chain swaps to produce a fully connected SAT
instance; large d causes local LOG_KERNEL to decline.
Search for (but do not invent) low signed-dual-spectrum collisions
with different true SAT counts: such a pair would show strict limit
of k-th low-moment signatures. Finite search may return no pair.
"""
import argparse,json,random
from itertools import combinations
from collections import defaultdict

from r5_component_factor_20261015 import (
    k4_blocks, connected_scl_components, factor_exact
)
from r5_cooperative_scl_coverage_20261015 import (
    gf2_affine, validate_scl, valid_witness, fingerprint
)
from r5_optimal_moment_lp_20261015 import exact_optimal_lp


def swap_rows(rows, r1, v1, r2, v2):
    if r1==r2 or v1 not in rows[r1] or v2 not in rows[r2]:
        raise ValueError("invalid incidence switch")
    out=[list(row) for row in rows]
    out[r1].remove(v1)
    out[r2].remove(v2)
    out[r1].append(v2)
    out[r2].append(v1)
    return validate_scl(out)


def make_connected(blocks=4,seed=20261015):
    if blocks not in (2,4):
        raise ValueError("two or four blocks")
    rng=random.Random(seed)
    original=k4_blocks(blocks)
    local=factor_exact(original)
    assert local["solution_count"]==6**blocks
    witness=local["witness"]
    rows=original
    switches=[]
    for i in range(blocks-1):
        lo1,hi1=18*i,18*(i+1)
        lo2,hi2=18*(i+1),18*(i+2)
        # Only source rows whose three variables still belong to
        # one original block are used as new switch endpoints.
        choices=[]
        for r1,row1 in enumerate(rows):
            if not all(lo1<=v<hi1 for v in row1):
                continue
            for r2,row2 in enumerate(rows):
                if not all(lo2<=v<hi2 for v in row2):
                    continue
                for v1 in row1:
                    for v2 in row2:
                        if (witness>>v1)&1 != (witness>>v2)&1:
                            continue
                        try:
                            candidate=swap_rows(rows,r1,v1,r2,v2)
                        except ValueError:
                            continue
                        if valid_witness(candidate,witness):
                            choices.append((r1,v1,r2,v2,candidate))
        if not choices:
            raise AssertionError("no valid witness-preserving cross-component switch")
        # Seeds vary choice without altering legal construction contract.
        r1,v1,r2,v2,rows=rng.choice(choices)
        switches.append((r1,v1,r2,v2))
    assert len(connected_scl_components(rows))==1
    assert valid_witness(rows,witness)
    return rows,witness,switches


def signed_dual_low_spectrum(rows,k=2):
    if not 0<=k<=3:
        raise ValueError("only fixed low weights k<=3")
    n=len(rows)
    aff=gf2_affine(rows,0,0)
    assert aff is not None
    part,basis,d=aff
    signature=[]
    for size in range(k+1):
        signed=0
        for support in combinations(range(n),size):
            u=sum(1<<v for v in support)
            if any((u&vec).bit_count()%2 for vec in basis):
                continue
            signed+=(-1 if (u&part).bit_count()%2 else 1)
        signature.append(signed)
    return (d,tuple(signature))


def mutate_connected(rows,witness,rng,moves=8):
    """Witness-preserving legal random 2-switches WITHIN a connected source.

    A switch replaces two incidence edges, preserving degree three.
    Revalidation catches any forbidden 4-cycle; a connectivity check
    forbids disconnection. The old witness stays valid because both
    exchanged variable bits match exactly.
    """
    accepted=0
    rows=validate_scl(rows)
    for _ in range(moves):
        for attempt in range(300):
            r1,r2=rng.sample(range(len(rows)),2)
            v1=rng.choice(rows[r1])
            v2=rng.choice(rows[r2])
            if v1==v2 or (witness>>v1)&1 != (witness>>v2)&1:
                continue
            # A degenerate swap with shared variable membership is rejected.
            if v1 in rows[r2] or v2 in rows[r1]:
                continue
            try:
                updated=swap_rows(rows,r1,v1,r2,v2)
            except ValueError:
                continue
            if len(connected_scl_components(updated))!=1:
                continue
            assert valid_witness(updated,witness)
            rows=updated
            accepted+=1
            break
    return rows,accepted


def search_indistinguishable(samples=24,degree=2):
    seen={}
    collision=None
    records=[]
    for seed in range(samples):
        rows,witness,switches=make_connected(2,seed)
        rng=random.Random(seed*991+20261015)
        rows,moves=mutate_connected(rows,witness,rng,
                                   moves=4+(seed%13))
        count=factor_exact(rows,exponent=3)
        assert count["verdict"]=="SAT" and count["components"]==1
        spectrum=signed_dual_low_spectrum(rows,degree)
        key=spectrum
        rec={"seed":seed,"fingerprint":fingerprint(rows),
             "nullity":spectrum[0],"low_signed_spectrum":spectrum[1],
             "SAT_count":count["solution_count"],
             "swaps":switches,"extra_legal_switches":moves}
        records.append(rec)
        if key in seen and seen[key]["SAT_count"]!=rec["SAT_count"]:
            collision={"a":seen[key],"b":rec}
            break
        seen[key]=rec
    return {"searched":len(records),"k":degree,
            "mutation":"multiple witness-preserving valid connected incidence 2-switches",
            "pair_with_same_dual_low_spectrum_and_different_sat_count":collision,
            "distinct_signatures":len(seen),
            "honest_collision_status":"FOUND" if collision else "NOT_FOUND_IN_FINITE_SAMPLE"}


def frozen_low_spectrum_pair():
    """Independent replay of seeds 0,13 and raw violation moments.

    These are TWO connected legal SCL n36 instances. Equal low-weight
    signed dual spectra up to k=2 imply equal low-order moments of t,
    while exact SAT counts differ. The test enumerates only 2^7
    solutions PER example as a finite independent control.
    """
    from math import comb
    from collections import Counter
    specimens=[]
    for seed in (0,13):
        rows,witness,swaps=make_connected(2,seed)
        rng=random.Random(seed*991+20261015)
        rows,moves=mutate_connected(rows,witness,rng,moves=4+(seed%13))
        assert len(connected_scl_components(rows))==1
        assert valid_witness(rows,witness)
        affine=gf2_affine(rows,0,0)
        part,basis,d=affine
        assert d==7
        histogram=Counter()
        for mask in range(1<<d):
            x=part
            for j,b in enumerate(basis):
                if mask>>j&1:
                    x^=b
            t=sum(all((x>>v)&1 for v in row) for row in rows)
            assert t%3==0
            histogram[t]+=1
        moments=tuple(sum(cnt*comb(t,j) for t,cnt in histogram.items())
                      for j in range(3))
        specimens.append({
            "seed":seed,"sha256":fingerprint(rows),
            "low_signed_spectrum_k2":signed_dual_low_spectrum(rows,2),
            "low_signed_spectrum_k3":signed_dual_low_spectrum(rows,3),
            "raw_moments_degree2":moments,
            "SAT_count":histogram[0],
            "n":len(rows),"affine_dimension":d
        })
    a,b=specimens
    assert a["low_signed_spectrum_k2"]==b["low_signed_spectrum_k2"]
    assert a["low_signed_spectrum_k2"]==(7,(1,0,10))
    assert a["raw_moments_degree2"]==b["raw_moments_degree2"]
    assert (a["SAT_count"],b["SAT_count"])==(2,3)
    assert a["low_signed_spectrum_k3"]!=b["low_signed_spectrum_k3"]
    lpa=exact_optimal_lp(36,a["raw_moments_degree2"],2)
    lpb=exact_optimal_lp(36,b["raw_moments_degree2"],2)
    assert lpa["exact_optimum"]==lpb["exact_optimum"]
    return {"scientific_status":"EXACT_CONNECTED_SIGNED_LOW_SPECTRUM_INDISTINGUISHABILITY_K2",
            "examples":specimens,
            "same_moments_degree2":True,
            "same_optimal_degree2_LP":lpa["exact_optimum"],
            "degree3_signed_spectrum_distinguishes":True,
            "different_exact_sat_counts":True,
            "all_n_fixed_degree_lower_bound":"NOT_PROVED"}


def self_test():
    rows36,witness36,swaps36=make_connected(2)
    exact36=factor_exact(rows36,3)
    assert exact36["verdict"]=="SAT"
    rows72,witness72,swaps72=make_connected(4)
    assert len(rows72)==72 and len(connected_scl_components(rows72))==1
    assert valid_witness(rows72,witness72)
    affine72=gf2_affine(rows72,0,0)
    assert affine72 is not None
    d72=affine72[2]
    # 4 components linked by legal row-variable incidence switches.
    # This is connected and SAT; not assumed to be HARD.
    return {
        "status":"CONNECTED_LEGAL_SCL_COVERAGE_FIXTURES",
        "connected36":{"n":36,"components":1,
                       "swaps":swaps36,"exact_sat":exact36["solution_count"],
                       "affine_words_checked":exact36["total_parity_words_checked"]},
        "connected72":{"n":72,"components":1,
                       "swaps":swaps72,"GF2_dimension":d72,
                       "affine_words":1<<d72,
                       "log_kernel_c3":"DECLINE" if 1<<d72>72**3 else "COVERED"},
        "moment_indistinguishability_search":search_indistinguishable(80,2),
        "frozen_degree2_indistinguishable_pair":frozen_low_spectrum_pair(),
        "universal_result":"NOT_PROVED","P_vs_NP":"OPEN"
    }


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    if args.self_test:
        print(json.dumps(self_test(),indent=2,sort_keys=True))
    else:
        p.error("--self-test")
