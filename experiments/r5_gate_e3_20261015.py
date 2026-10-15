#!/usr/bin/env python3
"""Gate E3 complete finite anchored moment LP2..LP5 comparison.

All-n/local theorems are in sibling exact anchor and LP modules.
These instances are SMALL oracle controls, not evidence of an all-n
solver: connected n36 d=7, Petersen45 d=12, disconnected 4K4 n72
factored as 4 independent d=6 components.

Dual/primal optimality is verified in exact rational arithmetic for
each anchored and unanchored degree, and exact A4/A6 kernel codeword
counts are checked against independent affine enumeration where small.
"""
from itertools import combinations
from math import comb
import argparse, json, random

from r5_cooperative_scl_coverage_20261015 import fixtures
from r5_component_factor_20261015 import k4_blocks
from r5_connected_coverage_breaker_20261015 import (
    make_connected,mutate_connected
)
from r5_optimal_moment_gates_20261015 import affine_hist,component_hist
from r5_optimal_moment_lp_20261015 import exact_optimal_lp
from r5_anchored_moment_lp_20261015 import (
    anchored_optimal_lp,exact_manual_anchored_q36
)
from r5_local_codeword_anchors_20261015 import (
    anchor_counts,full_affine_anchor_oracle,incidence_girth_ge_10,
    local_codewords,linear_validate_and_incidence
)


def raw_moments(hist,k):
    return tuple(sum(cnt*comb(t,j) for t,cnt in hist.items())
                 for j in range(k+1))


def anchored_report(rows,method="finite",verify_local=True):
    n=len(rows)
    rows,_=linear_validate_and_incidence(rows)
    if method=="factor":
        hist,checks=component_hist(rows)
    else:
        hist=affine_hist(rows,cap=n**3)
        checks=sum(hist.values())
    a4,a6=local_codewords(rows,4),local_codewords(rows,6)
    assert len(a4)==len(set(a4)) and len(a6)==len(set(a6))
    simple={n:1,n-3:0}
    extended=anchor_counts(rows,precomputed={4:a4,6:a6})
    assert extended[n-6]==len(a4) and extended[n-9]==len(a6)
    if verify_local and method=="finite":
        assert full_affine_anchor_oracle(rows)==extended
    assert hist[n]==1 and hist[n-3]==0
    assert hist[n-6]==len(a4) and hist[n-9]==len(a6)
    grades={}
    for k in (2,3,4,5):
        raw=raw_moments(hist,k)
        base=exact_optimal_lp(n,raw,k)
        anchored=anchored_optimal_lp(n,raw,k,simple)
        local=anchored_optimal_lp(n,raw,k,extended)
        assert (local["integer_upper_bound"]<=
                anchored["integer_upper_bound"]<=
                base["integer_upper_bound"])
        grades[str(k)]={
            "old":base["exact_optimum"],
            "anchored_w_n_w_nminus3":anchored["exact_optimum"],
            "anchored_plus_A4_A6":local["exact_optimum"],
            "new_integer_bound":local["integer_upper_bound"],
            "primal_dual_optimality_verified":True,
        }
    return {
        "n":n,"method":method,
        "affine_words_checked":checks,
        "true_SAT_count":hist[0],
        "A4":len(a4),"A6":len(a6),
        "anchors":{str(t):v for t,v in sorted(extended.items())},
        "girth_ge10":incidence_girth_ge_10(rows),
        "degree_2_to_5":grades
    }


def build_pair(seed):
    rows,witness,_=make_connected(2,seed)
    rows,_=mutate_connected(rows,witness,
                           random.Random(seed*991+20261015),
                           moves=4+(seed%13))
    return rows


def self_test():
    manual=exact_manual_anchored_q36()
    assert manual["manual_exact_dual"]=="94/3"
    a=anchored_report(build_pair(0))
    b=anchored_report(build_pair(13))
    assert (a["A4"],a["A6"])==(0,3)
    assert (b["A4"],b["A6"])==(0,2)
    assert (a["true_SAT_count"],b["true_SAT_count"])==(2,3)
    assert (a["degree_2_to_5"]["2"]["anchored_w_n_w_nminus3"]==
            b["degree_2_to_5"]["2"]["anchored_w_n_w_nminus3"]=="94/3")
    assert a["degree_2_to_5"]["2"]["new_integer_bound"]<=23
    assert b["degree_2_to_5"]["2"]["new_integer_bound"]<=26
    # Independently derived valid quadratic q (not necessarily LP optimum):
    assert (188-21*a["A4"]-15*a["A6"])//6==23
    assert (188-21*b["A4"]-15*b["A6"])//6==26
    p=anchored_report(fixtures()["HolyerPetersen_UNSAT"])
    assert p["true_SAT_count"]==0
    g=anchored_report(k4_blocks(4),method="factor",verify_local=False)
    assert g["true_SAT_count"]==1296 and g["affine_words_checked"]==256
    return {
        "scientific_status":"GATE_E3_ANCHORED_LP_DEGREE2_TO5_VERIFIED",
        "manual_GateD_94_over_3":"PASS",
        "Connected_SCL36_seed0":a,
        "Connected_SCL36_seed13":b,
        "Petersen45":p,
        "Disconnected_SCL72":g,
        "uniform_polynomial_SCL_solver":"NOT_CONSTRUCTED",
        "P_vs_NP":"OPEN",
    }


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--self-test",action="store_true")
    options=p.parse_args()
    if not options.self_test:
        p.error("--self-test")
    print(json.dumps(self_test(),sort_keys=True,indent=2))
