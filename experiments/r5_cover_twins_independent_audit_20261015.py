#!/usr/bin/env python3
"""Independent science audit: exact SAT/UNSAT same-rank 2-lift pair.

REPLAY: canonical connected UNSAT SCL36 generated from fixed seed,
complete affine 64-word oracle; ternary y solver with independent
integer Ay=2 checks; constructive SAT lift; FIRST non-gauge delta
basis from exact Phi kernel. New UNSAT lift proven with complete
GF2-affine 128-word independent enumeration.

Compare:
 - same length, legality, connectivity and GF2 rank 65;
 - entire (tiny) kernel weight spectrum A_i and dual low spectrum;
 - A4,A6,A8,A10 and low binomial moments;
 - girth12 flag and balanced size<=2 separator (if feasible).
NO claim of genuine fixed-depth spectral twins if root differs.

A replay certificate includes canonical rows, exact huge integer
delta as string, signs bitmask and witness, so no dependence on
random implementation or truncated JSON floating integers.
"""
from collections import Counter
import argparse,json

from r5_rank_preserving_cover_twins_20261015 import (
    search_unsat_base,integer_two_cover_witness,sat_cover_from_y,
    phi_data,phi_apply,delta_to_signs,signmask_from_signs,
    lift_rows,check_rank_formula,source_bitrows,gf2_rank
)
from r5_cooperative_scl_coverage_20261015 import (
    validate_scl,valid_witness,gf2_affine,fingerprint
)
from r5_joint_spectral_anchor_twins_20261015 import (
    root_signature
)
from r5_connected_coverage_breaker_20261015 import (
    connected_scl_components
)
from r5_high_girth_adversarial_gate_20261015 import (
    girth12_gate,small_balanced_separator_profile
)


def independently_enumerate_parity(rows,cap=1<<12):
    """Independent from classify_affine; enumerate all GF2 affine words."""
    rows=validate_scl(rows)
    part,basis,d=gf2_affine(rows,0,0)
    if 1<<d>cap:
        return {"status":"UNKNOWN_RESOURCE_LIMIT","d":d}
    n=len(rows)
    full=(1<<n)-1
    histogram=Counter()
    witnesses=[]
    checked=0
    for pattern in range(1<<d):
        x=part
        for j,b in enumerate(basis):
            if (pattern>>j)&1:x^=b
        assert all(sum((x>>v)&1 for v in row)%2==1 for row in rows)
        v=full^x
        assert all(sum((v>>col)&1 for col in row)%2==0
                   for row in rows)
        histogram[v.bit_count()]+=1
        if all(sum((x>>col)&1 for col in row)==1 for row in rows):
            assert valid_witness(rows,x)
            witnesses.append(x)
        checked+=1
    return {"status":"EXACT",
            "d":d,
            "checked":checked,
            "sat_count":len(witnesses),
            "first_witness":witnesses[0] if witnesses else None,
            "kernel_weight_hist":dict(sorted(histogram.items()))}


def run():
    base,base_certificate=search_unsat_base()
    assert base is not None and len(base)==36
    oracle_base=independently_enumerate_parity(base)
    assert oracle_base["status"]=="EXACT"
    assert oracle_base["sat_count"]==0
    assert oracle_base["checked"]==64
    yreport=integer_two_cover_witness(base)
    assert yreport["status"]=="SAT_TERNARY_WITNESS"
    y=yreport["y"]
    assert all(sum(y[j] for j in row)==2 for row in base)
    signs,witness,sat=sat_cover_from_y(base,y)
    frame=phi_data(base)
    delta=frame["non_gauge_basis"][0]
    assert phi_apply(frame["images"],delta)==0
    alternative=delta_to_signs(frame["edges"],signs,delta)
    unsat=lift_rows(base,alternative)
    assert len(connected_scl_components(sat))==1
    assert len(connected_scl_components(unsat))==1
    assert valid_witness(sat,witness)
    satrank=check_rank_formula(base,signs,frame)
    unsatrank=check_rank_formula(base,alternative,frame)
    assert satrank==unsatrank and satrank["lift_rank"]==65
    # INDEPENDENT complete explicit parity enumeration:
    pure_sat=independently_enumerate_parity(sat)
    pure_unsat=independently_enumerate_parity(unsat)
    assert pure_sat["status"]==pure_unsat["status"]=="EXACT"
    assert pure_sat["d"]==pure_unsat["d"]==7
    assert pure_sat["sat_count"]>0
    assert pure_unsat["sat_count"]==0
    assert pure_sat["checked"]==pure_unsat["checked"]==128
    assert pure_sat["first_witness"] is not None
    # Deep root feature comparison only AFTER both SAT statuses certified.
    sig_sat=root_signature(sat)
    sig_unsat=root_signature(unsat)
    features=["n","nullity","binomial_moments_0_2",
              "dual_B_0_3","A_4_6_8_10"]
    exact_sig={name:{"SAT":sig_sat[i],"UNSAT":sig_unsat[i],
                     "equal":sig_sat[i]==sig_unsat[i]}
               for i,name in enumerate(features)}
    h_sat=pure_sat["kernel_weight_hist"]
    h_unsat=pure_unsat["kernel_weight_hist"]
    differences=[
        {"weight":w,"A_SAT":h_sat.get(w,0),
         "A_UNSAT":h_unsat.get(w,0)}
        for w in sorted(set(h_sat)|set(h_unsat))
        if h_sat.get(w,0)!=h_unsat.get(w,0)
    ]
    assert h_sat.get(48,0)==pure_sat["sat_count"]
    assert h_unsat.get(48,0)==0
    report={
        "scientific_status":"REPRODUCIBLE_SAT_UNSAT_SAME_GF2_RANK_2LIFTS",
        "base_n":36,"base_sha256":fingerprint(base),
        "base_complete_GF2_UNSAT_words":64,
        "Ay_eq_2_witness":list(y),
        "sheet_edge_signs_mask":str(signmask_from_signs(frame["edges"],signs)),
        "nongauge_kernel_delta":str(delta),
        "flip_edges":delta.bit_count(),
        "phi_rank":frame["phi_rank"],
        "gauge_rank":frame["gauge_rank"],
        "nongauge_quotient_dimension":frame["quotient_dim"],
        "same_lift_rank":satrank["lift_rank"],
        "same_lift_nullity":pure_sat["d"],
        "SAT_cover_sha256":fingerprint(sat),
        "UNSAT_cover_sha256":fingerprint(unsat),
        "SAT_cover_exact":pure_sat,
        "UNSAT_cover_exact":pure_unsat,
        "joint_root_signature_components":exact_sig,
        "joint_root_signature_equal":sig_sat==sig_unsat,
        "full_kernel_spectrum_first_differences":differences[:12],
        "SAT_cover_girth12":girth12_gate(sat),
        "UNSAT_cover_girth12":girth12_gate(unsat),
        "certificates":{
            "base_rows":[list(r) for r in base],
            "sat_lift_rows":[list(r) for r in sat],
            "unsat_lift_rows":[list(r) for r in unsat],
            "sat_witness_bits_decimal":str(witness),
            "complete_GF2_enumeration":"enumerate all 2^7 affine solutions for BOTH lifts",
            "SCL_legality":"3 per row and column; pairwise intersection<=1",
            "rank_check":"independent row echelon plus exact L^T A0 K"}
    }
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if not a.self_test:p.error("--self-test")
    print(json.dumps(run(),indent=2,sort_keys=True))
