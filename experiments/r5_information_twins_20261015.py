#!/usr/bin/env python3
"""E4.3 directed feature-preserving incidence-switch adversarial search.

NOT blind random graph-pair matching. Start from a frozen legal
connected SAT SCL36 source and propose local legal incidence 2-switch
"twists". Reject unless the target's CORE discriminator is EXACTLY
preserved: (m,r,parity,C0,target, signed P/M low degree2, A4,A6).
Only THEN spend complete 2^d exact affine classification.
If a SAT-to-UNSAT flip is witnessed, independently compare all
unlabeled singleton branch signatures.

A twist respecting low spectral features is NOT automatically
guaranteed to preserve them. This experiment measures how often the
rejection gate accepts, and can legitimately report NO CANDIDATES.
A matching full spectrum would force equal SAT count and is excluded
by the scientific goal.

Timeout/budget exhaustion NEVER means UNSAT.
"""
from collections import Counter
import json,argparse,random

from r5_discriminant_audit_split_20261015 import (
    rooted_pair,discriminant_and_audit
)
from r5_joint_spectral_anchor_twins_20261015 import (
    unrestricted_connected_mutation,classify_affine
)
from r5_local_codeword_anchors_20261015 import local_codewords
from r5_cooperative_scl_coverage_20261015 import (
    gf2_affine,fingerprint,validate_scl
)
from r5_connected_coverage_breaker_20261015 import (
    connected_scl_components
)


def cached_core(rows,k=2):
    sets={4:local_codewords(rows,4),6:local_codewords(rows,6)}
    core,audit=discriminant_and_audit(rows,k=k,
                         anchors=True,cached_words=sets)
    assert audit["all_consistency_checks"]=="PASS"
    return core,sets


def depth1_core_signature(rows,k=2):
    sets={4:local_codewords(rows,4),6:local_codewords(rows,6)}
    core,_=discriminant_and_audit(rows,k=k,anchors=True,
                                  cached_words=sets)
    n=len(rows)
    children=[]
    for v in range(n):
        left,_=discriminant_and_audit(rows,(1<<v,0),k=k,
                                      anchors=True,cached_words=sets)
        right,_=discriminant_and_audit(rows,(0,1<<v),k=k,
                                       anchors=True,cached_words=sets)
        children.append(tuple(sorted((left,right))))
    return core,tuple(sorted(children))


def directed_twists(start_seed=0,trial_limit=72,mutation_seed=20261015):
    if trial_limit<1 or trial_limit>200:
        raise ValueError("bounded 1..200 trials")
    source=rooted_pair(start_seed)
    target,sets=cached_core(source,2)
    original=classify_affine(source)
    assert original["verdict"]=="SAT"
    rng=random.Random(mutation_seed+start_seed)
    tallies=Counter()
    same=[]
    difference=None
    for trial in range(trial_limit):
        proposal,moves=unrestricted_connected_mutation(
            source,rng,steps=1)
        validate_scl(proposal)
        assert len(connected_scl_components(proposal))==1
        if not moves:
            tallies["NO_VALID_MUTATION"]+=1
            continue
        if fingerprint(source)==fingerprint(proposal):
            tallies["DUPLICATE_SOURCE"]+=1
            continue
        dims=gf2_affine(proposal,0,0)[2]
        if dims!=original["d"]:
            tallies["REJECT_NULLITY"]+=1
            continue
        core,local=cached_core(proposal,2)
        if core!=target:
            tallies["REJECT_DISCRIMINANT"]+=1
            continue
        tallies["ACCEPT_MATCHED_CORE"]+=1
        trial_oracle=classify_affine(proposal,cap=1<<12)
        if trial_oracle["verdict"]=="UNKNOWN_RESOURCE_LIMIT":
            tallies["UNKNOWN_BUDGET"]+=1
            continue
        same.append({"trial":trial,
                     "sha256":fingerprint(proposal),
                     "status":trial_oracle["verdict"],
                     "exact_count":trial_oracle["count"],
                     "checked_GF2_words":trial_oracle["checked"],
                     "kernel_A4":len(local[4]),
                     "kernel_A6":len(local[6])})
        if trial_oracle["verdict"]=="UNSAT":
            signature_before=depth1_core_signature(source,2)
            signature_after=depth1_core_signature(proposal,2)
            difference={
                "SAT_source_sha256":fingerprint(source),
                "UNSAT_target_sha256":fingerprint(proposal),
                "same_core_k2_plus_A4_A6":True,
                "depth1_unlabeled_core_equal":
                    signature_before==signature_after,
                "source_sat_witness":original["witness_bits"],
                "UNSAT_finite_proof":{
                    "oracle":"all 2^d affine candidates",
                    "word_count":trial_oracle["checked"],
                    "rank_nullity":trial_oracle["d"]
                }}
            break
    return {
        "start_seed":start_seed,
        "starting_source_sha256":fingerprint(source),
        "original_exact_SAT_count":original["count"],
        "target_core_signed_k2_A4_A6":str(target),
        "trial_limit":trial_limit,
        "rejection_statistics":dict(tallies),
        "accepted_exact_controls":same,
        "opposite_status_pair":difference,
        "status":"FOUND_CERTIFIED_CORE_TWIN" if difference else
                 "NO_OPPOSITE_STATUS_TWIN_IN_FINITE_BUDGET",
        "universal_hardness":"NOT_ESTABLISHED"
    }


def self_test():
    a=directed_twists(0,trial_limit=72)
    b=directed_twists(13,trial_limit=72)
    assert a["original_exact_SAT_count"]==2
    assert b["original_exact_SAT_count"]==3
    return {
        "gate":"DIRECTED_INFO_PRESERVING_PARITY_TWISTS",
        "runs":[a,b],
        "asymptotic_lower_bound":"NOT_PROVED",
        "P_vs_NP":"OPEN"
    }


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--trials",type=int,default=72)
    a=p.parse_args()
    print(json.dumps(self_test() if a.self_test else
                     directed_twists(0,a.trials),
                     indent=2,sort_keys=True))
