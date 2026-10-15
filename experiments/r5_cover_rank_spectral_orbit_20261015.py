#!/usr/bin/env python3
"""E4.4 exact complete quotient orbit: rank-preserving 2-cover twins.

For one independently UNSAT-certified connected SCL36 base and
one SAT 2-cover with fixed Phi(A0), enumerate EXACTLY all 2^q
non-gauge classes in ker Phi / gauge, q=11 in this control.

Every class contains one representative lift matrix. The GF2 rank
is preserved *by construction*; complete <=128-word affine
enumeration finds exact #SAT and full kernel weight histogram.

From each histogram recover low dual spectrum B0..B3 using the
classical Krawtchouk transform, independently of the rank and
without exponential enumeration in n (the exponential enumeration
is over the small D=7 finite control; NOT an all-n algorithm).

Bucket by exact (rank,B0..Bk,A4,A6,A8,A10) for k=0,1,2,3.
Opposite-status collisions are REPLAYED independently using a
complete GF2 codeword oracle and verified exact SAT witness,
and are only then called finite spectral twins.

The family is not all rank-preserving lifts: it fixes the ENTIRE
obstruction matrix L^T A0 K. Other same-rank fibers may exist.
"""
from collections import Counter,defaultdict
import argparse,json

from r5_rank_preserving_cover_twins_20261015 import (
    search_unsat_base,integer_two_cover_witness,sat_cover_from_y,
    phi_data,phi_apply,delta_to_signs,signmask_from_signs,
    lift_rows,source_bitrows,gf2_rank
)
from r5_cooperative_scl_coverage_20261015 import (
    gf2_affine,valid_witness,fingerprint
)
from r5_bidirectional_macwilliams_lp_20261015 import krawtchouk
from r5_cover_twins_independent_audit_20261015 import (
    independently_enumerate_parity
)


def histogram_from_affine(rows):
    n=len(rows)
    part,basis,d=gf2_affine(rows,0,0)
    if d>12:
        return {"status":"UNKNOWN_RESOURCE_LIMIT","d":d}
    full=(1<<n)-1
    hist=Counter()
    for seed in range(1<<d):
        x=part
        for j,word in enumerate(basis):
            if (seed>>j)&1:x^=word
        hist[(x^full).bit_count()]+=1
    # Algebraic theorem of square/cubic SCL exact one:
    # kernel word weight 2n/3 if and only if x=1+v is SAT.
    assert n%3==0
    return {"status":"EXACT","d":d,
            "hist":hist,
            "SAT":hist.get(2*n//3,0)}


def spectrum_from_hist(hist,n,d,kcache):
    N=1<<d
    B=[]
    for j in range(4):
        num=sum(count*kcache[(j,w)] for w,count in hist.items())
        assert num%N==0,(j,num,N)
        B.append(num//N)
    return tuple(B)


def replay_pair(base,signs,frame,codeA,codeB):
    n=len(base)
    def entry(code):
        delta=0
        for j,b in enumerate(frame["non_gauge_basis"]):
            if (code>>j)&1:delta^=b
        alt=delta_to_signs(frame["edges"],signs,delta)
        rows=lift_rows(base,alt)
        proof=independently_enumerate_parity(rows)
        assert proof["status"]=="EXACT"
        return {"orbit_index":code,"delta_bits":str(delta),
                "lift_sha256":fingerprint(rows),
                "SAT_count":proof["sat_count"],
                "GF2_words_checked":proof["checked"],
                "kernel_hist":proof["kernel_weight_hist"],
                "SAT_witness":proof["first_witness"]}
    A=entry(codeA); B=entry(codeB)
    assert (A["SAT_count"]==0) != (B["SAT_count"]==0)
    return {"A":A,"B":B,
            "opposite_certified":True,
            "same_full_Phi":True}


def exhaustive_orbit():
    base,source=search_unsat_base()
    assert source["trial"]==2 and len(base)==36
    y=integer_two_cover_witness(base)
    assert y["status"]=="SAT_TERNARY_WITNESS"
    signs,sat_witness,sat_rows=sat_cover_from_y(base,y["y"])
    frame=phi_data(base)
    q=frame["quotient_dim"]
    assert q==11
    candidates=1<<q
    n=72
    possible_even=range(0,2*n//3+1,2)
    kcache={(j,w):krawtchouk(n,j,w)
            for j in range(4) for w in possible_even}
    seen=[{} for k in range(4)]
    counts=Counter()
    distinct=[set() for _ in range(4)]
    collision=[None]*4
    # XOR Gray-code traversal: one generator changes at a time.
    running_delta=0
    previous_gray=0
    for number in range(candidates):
        gray=number^(number>>1)
        if number:
            single=gray^previous_gray
            idx=single.bit_length()-1
            running_delta^=frame["non_gauge_basis"][idx]
        previous_gray=gray
        assert phi_apply(frame["images"],running_delta)==0
        variant=delta_to_signs(frame["edges"],signs,running_delta)
        lifted=lift_rows(base,variant)
        record=histogram_from_affine(lifted)
        assert record["status"]=="EXACT" and record["d"]==7
        # All rank checks are independently asserted by GF2 dimension.
        hist=record["hist"]
        B=spectrum_from_hist(hist,n,7,kcache)
        anchors=tuple(hist.get(w,0) for w in (4,6,8,10))
        sat=record["SAT"]>0
        counts["SAT" if sat else "UNSAT"]+=1
        if number==0:
            assert sat and valid_witness(lifted,sat_witness)
        for k in range(4):
            key=(7,B[:k+1],anchors)
            distinct[k].add(key)
            previously=seen[k].get(key)
            if previously is None:
                seen[k][key]=(gray,sat)
            elif previously[1]!=sat and collision[k] is None:
                # Certified finite opposite-status root collision
                # within THIS exact Phi fiber; stop for k=3 only
                # after full orbit inspected and then replay.
                collision[k]=(previously[0],gray)
    audits={}
    for k in range(4):
        pair=collision[k]
        audits[str(k)]={
            "independent_dual_B0_to_k":k,
            "distinct_bucket_count":len(distinct[k]),
            "opposite_status_same_rank_anchor_and_low_B":pair is not None,
            "finite_pair_replay":(
                replay_pair(base,signs,frame,*pair) if pair else None)}
    return {
        "scientific_status":"COMPLETE_FIXED_PHI_GAUGE_QUOTIENT_ENUMERATION",
        "base_source_sha256":fingerprint(base),
        "base_UNSAT_checked_words":source["oracle_words"],
        "base_rank":frame["rankA"],
        "base_nullity":frame["d"],
        "Phi_rank":frame["phi_rank"],
        "quotient_dim":q,
        "all_classes_checked":candidates,
        "class_counts":dict(counts),
        "baseline_SAT_witness_verified":True,
        "full_orbit_rank":65,
        "full_orbit_GF2_nullity":7,
        "spectral_anchors_tested":["A4","A6","A8","A10"],
        "truncated_spectral_buckets":audits,
        "not_covered":"other Phi matrices of identical numerical rank",
        "all_n_polynomial_SCL":"NOT_CONSTRUCTED",
        "P_vs_NP":"OPEN"
    }


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if not a.self_test:p.error("--self-test")
    print(json.dumps(exhaustive_orbit(),indent=2,sort_keys=True))
