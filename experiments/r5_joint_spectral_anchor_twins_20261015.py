#!/usr/bin/env python3
"""Gate E4: finite proof-carrying JOINT_SPECTRAL_ANCHOR_TWINS search.

Independent legal connected square/cubic/linear SCL mutations via
arbitrary incidence 2-switches. All retained graphs are revalidated;
only graphs with <= 2^12 parity words are independently classified
by COMPLETE affine enumeration (SAT witness or exact UNSAT).

Root signature includes n,d, low signed/unsigned dual spectrum
B1..B3, raw first two t moments, and ALL locally exact codeword
anchors A4,A6,A8,A10.

Only if an opposite SAT/UNSAT pair shares this signature do we
compute a branch-stable depth-1 signature by independently
recomputing both branches of every variable. The absence of a
collision in a FINITE seeded sample is NOT a lower bound.
"""
from collections import defaultdict,Counter
from itertools import combinations
from math import comb
import argparse,json,random

from r5_cooperative_scl_coverage_20261015 import (
    validate_scl,valid_witness,gf2_affine,fingerprint
)
from r5_connected_coverage_breaker_20261015 import (
    make_connected,swap_rows,connected_scl_components
)
from r5_bidirectional_macwilliams_lp_20261015 import (
    rowspace_low_counts,anchors_root
)
from r5_fixed_degree_moment_expert_20261015 import raw_binomial_moments
from r5_local_codeword_anchors_8_10_20261015 import anchor_8_10
from r5_local_codeword_anchors_20261015 import anchor_counts


def unrestricted_connected_mutation(rows,rng,steps=8):
    rows=validate_scl(rows)
    moves=[]
    n=len(rows)
    for _ in range(steps):
        for _ in range(120):
            a,b=rng.sample(range(n),2)
            va=rng.choice(rows[a])
            vb=rng.choice(rows[b])
            if va==vb or vb in rows[a] or va in rows[b]:
                continue
            try:
                new=swap_rows(rows,a,va,b,vb)
            except ValueError:
                continue
            if len(connected_scl_components(new))!=1:
                continue
            rows=new
            moves.append((a,va,b,vb))
            break
    return rows,moves


def classify_affine(rows,cap=1<<12):
    aff=gf2_affine(rows,0,0)
    if aff is None:
        raise AssertionError("parity inconsistent despite all-one solution")
    part,basis,d=aff
    if 1<<d>cap:
        return {"verdict":"UNKNOWN_RESOURCE_LIMIT",
                "d":d,"required":1<<d,"checked":0}
    cnt=0
    first=None
    for seed in range(1<<d):
        x=part
        for j,b in enumerate(basis):
            if seed>>j&1:
                x^=b
        if valid_witness(rows,x):
            cnt+=1
            if first is None:
                first=x
    return {"verdict":"SAT" if cnt else "UNSAT",
            "d":d,"count":cnt,"checked":1<<d,
            "witness_bits":first if first is not None else None,
            "proof_method":"complete replayable GF2-affine oracle"}


def root_signature(rows):
    n=len(rows)
    aff=gf2_affine(rows,0,0)
    d=aff[2]
    moment=raw_binomial_moments(rows,(0,0),degree=2)[0]
    b=rowspace_low_counts(rows,3)
    anchors=anchors_root(rows)
    return (n,d,tuple(moment),tuple(b[j] for j in range(4)),
            tuple(anchors.get(w,0) for w in (4,6,8,10)))


def depth1_signature(rows):
    """Finite root-plus-all-branches invariant, no graph canonicalization claim."""
    n=len(rows)
    root=root_signature(rows)
    child=[]
    for v in range(n):
        record=[]
        for bit in (0,1):
            cube=(1<<v,0) if bit==0 else (0,1<<v)
            moment=raw_binomial_moments(rows,cube,2)[0]
            a=anchor_counts(rows,cube)
            b,_=anchor_8_10(rows,cube)
            record.append((tuple(moment),a[n],a[n-6],a[n-9],
                           b[8],b[10]))
        child.append(tuple(sorted(record)))
    return (root,tuple(sorted(child)))


def search(samples=40,seed=20261015):
    if not 1<=samples<=200:
        raise ValueError("limited finite sample 1..200")
    rng=random.Random(seed)
    original,_,_=make_connected(2,20261015)
    classes={}
    results=[]
    collisions=[]
    verdict_counts=Counter()
    for number in range(samples):
        changed,moves=unrestricted_connected_mutation(
            original,rng,steps=4+(number%11))
        validate_scl(changed)
        assert len(connected_scl_components(changed))==1
        oracle=classify_affine(changed)
        verdict_counts[oracle["verdict"]]+=1
        if oracle["verdict"]=="UNKNOWN_RESOURCE_LIMIT":
            continue
        key=root_signature(changed)
        entry={"sample":number,"fingerprint":fingerprint(changed),
               "moves":moves,"verdict":oracle["verdict"],
               "exact_SAT_count":oracle["count"],
               "GF2_words_checked":oracle["checked"],
               "joint_signature":{
                   "n":key[0],"d":key[1],
                   "binomial_moments_degree2":key[2],
                   "row_dual_B0_to3":key[3],
                   "kernel_anchors_A4_A6_A8_A10":key[4]}}
        results.append(entry)
        if key in classes and classes[key]["verdict"]!=oracle["verdict"]:
            earlier=classes[key]
            # This second finite invariant tests only depth one.
            twinA,_=replay(seed,earlier["sample"])
            twinB=changed
            collisions.append({
                "first":earlier,"second":entry,
                "depth1_equal":depth1_signature(twinA)==
                               depth1_signature(twinB)
            })
            break
        classes.setdefault(key,entry)
    return {"status":"FINITE_SEARCH_NO_ALL_N_LOWER_BOUND",
            "seed":seed,"requested_samples":samples,
            "completed_exact_classifications":len(results),
            "verdict_counts":dict(verdict_counts),
            "distinct_joint_signatures":len(classes),
            "SAT_UNSAT_joint_twins":collisions,
            "result":"FOUND" if collisions else "NOT_FOUND_IN_FINITE_SAMPLE",
            "P_vs_NP":"OPEN"}


def replay(seed,index):
    rng=random.Random(seed)
    original,_,_=make_connected(2,20261015)
    last=None
    for number in range(index+1):
        last=unrestricted_connected_mutation(original,rng,
                     steps=4+(number%11))
    return last


def self_test():
    r=search(30,20261015)
    assert r["completed_exact_classifications"]>0
    assert r["result"] in ("FOUND","NOT_FOUND_IN_FINITE_SAMPLE")
    return r


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--samples",type=int,default=30)
    a=p.parse_args()
    out=self_test() if a.self_test else search(a.samples)
    print(json.dumps(out,indent=2,sort_keys=True))
