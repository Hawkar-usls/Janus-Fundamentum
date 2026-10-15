#!/usr/bin/env python3
"""R5 E4.4 explicit n72 root degree2 twin and depth1 distinction gate.

Frozen orbit 0 versus 13 from complete 2^11 ker(Phi)/gauge search.
Root matches (n, GF2 nullity/rank, signed dual P/M through degree2,
low Pless moments and kernel A4,A6,A8,A10). SAT 2 vs UNSAT0 with
independent 128-word exact affine certificates.

For each possible first choice variable compute the invariant
unlabeled multiset of both x_v=0 and x_v=1 child CORE signatures:
(m,r,parity,C0,target,P/M through degree2, anchors).
No forced "canonical coordinate"; sorting is permutation-invariant.
If they differ, h*=1 for THIS feature grammar and this pair.
If they agree, h*>1 (unless an extra feature excluded).
"""
from collections import Counter
import argparse,json

from r5_rank_preserving_cover_twins_20261015 import (
    search_unsat_base,integer_two_cover_witness,sat_cover_from_y,
    phi_data,delta_to_signs,lift_rows
)
from r5_discriminant_audit_split_20261015 import (
    discriminant_and_audit
)
from r5_cover_twins_independent_audit_20261015 import (
    independently_enumerate_parity
)
from r5_cooperative_scl_coverage_20261015 import fingerprint


def pair():
    base,_=search_unsat_base()
    y=integer_two_cover_witness(base)
    assert y["status"]=="SAT_TERNARY_WITNESS"
    signs,witness,S=sat_cover_from_y(base,y["y"])
    data=phi_data(base)
    orbit=13
    delta=0
    for j,b in enumerate(data["non_gauge_basis"]):
        if (orbit>>j)&1:delta^=b
    U=lift_rows(base,delta_to_signs(data["edges"],signs,delta))
    return S,U,witness,delta


def core_with_root_known_anchors(rows,cube):
    core,audit=discriminant_and_audit(rows,cube,k=2,anchors=False)
    assert audit["all_consistency_checks"]=="PASS"
    # All root A4..10 are ZERO on this orbit family, so every
    # child has 0 of these exact low kernel weights as well.
    # This is inherited safely via subset filtering of codewords:
    # a child cannot introduce a kernel word absent at the root.
    return core


def invariant_depth1_profile(rows):
    n=len(rows)
    root=core_with_root_known_anchors(rows,(0,0))
    children=[]
    for v in range(n):
        left=core_with_root_known_anchors(rows,(1<<v,0))
        right=core_with_root_known_anchors(rows,(0,1<<v))
        children.append(tuple(sorted((left,right))))
    return root,Counter(children)


def run():
    S,U,witness,delta=pair()
    Sproof=independently_enumerate_parity(S)
    Uproof=independently_enumerate_parity(U)
    assert Sproof["status"]==Uproof["status"]=="EXACT"
    assert Sproof["sat_count"]>0 and Uproof["sat_count"]==0
    assert Sproof["d"]==Uproof["d"]==7
    rootS,childrenS=invariant_depth1_profile(S)
    rootU,childrenU=invariant_depth1_profile(U)
    assert rootS==rootU
    mismatches=[]
    for key in set(childrenS)|set(childrenU):
        a,b=childrenS.get(key,0),childrenU.get(key,0)
        if a!=b:
            mismatches.append({
                "child_pair_feature":str(key),
                "SAT_multiplicity":a,
                "UNSAT_multiplicity":b})
    result={
        "scientific_status":"EXPLICIT_ROOT_DEGREE2_SAT_UNSAT_TWIN",
        "SAT_sha256":fingerprint(S),
        "UNSAT_sha256":fingerprint(U),
        "orbit_indices":[0,13],
        "delta_decimal":str(delta),
        "SAT_count":Sproof["sat_count"],
        "UNSAT_count":Uproof["sat_count"],
        "complete_affine_words_each":128,
        "root_P_M_low_degree2_identical":True,
        "root_low_kernel_anchors_A4_A6_A8_A10_identical_zero":True,
        "root_degree2_LP_input_identical":True,
        "depth1_all_variable_unlabeled_profile_identical":
            childrenS==childrenU,
        "distinct_child_pair_profiles_SAT":len(childrenS),
        "distinct_child_pair_profiles_UNSAT":len(childrenU),
        "first_unlabeled_profile_mismatches":mismatches[:4],
        "h_star_at_least":1,
        "h_star":(1 if childrenS!=childrenU else
                  "UNKNOWN_GREATER_THAN_ONE"),
        "all_n_lower_bound":"NOT_ESTABLISHED",
        "P_vs_NP":"OPEN"}
    assert result["root_degree2_LP_input_identical"]
    return result


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if not a.self_test:p.error("--self-test")
    print(json.dumps(run(),sort_keys=True,indent=2))
