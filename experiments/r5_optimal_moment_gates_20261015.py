#!/usr/bin/env python3
"""R5 Gates A/B: independently verified optimal degree 3,4,5 moment LP.

Moment data sources are explicit:
- finite Petersen45: <=45**3 full affine enumeration (4096 words).
- 4-disjoint-K4 SCL72: exact independent component histograms,
  convolved by addition of t. Only 4*64 parity words per root, plus
  small local reruns under one-variable branch restrictions.

These finite or factorable sources are separate from the all-n
polynomial fixed-k moment via GF2-rank restrictions already proved.
The generic LP consumes raw exact moments and proves primal/dual
optimality using Fraction-only two-phase simplex.
"""
from collections import Counter
from itertools import combinations
from math import comb
import argparse,json

from r5_component_factor_20261015 import (
    connected_scl_components, k4_blocks, factor_exact
)
from r5_cooperative_scl_coverage_20261015 import gf2_affine, fixtures
from r5_optimal_moment_lp_20261015 import exact_optimal_lp
from r5_adjacent_root_dual_20261015 import best_cubic


def affine_hist(rows,cube=(0,0),cap=None):
    aff=gf2_affine(rows,*cube)
    if aff is None:
        return Counter()
    part,basis,d=aff
    words=1<<d
    if cap is not None and words>cap:
        raise ValueError("affine sample beyond explicit polynomial cap")
    hist=Counter()
    for seed in range(words):
        x=part
        for j,vec in enumerate(basis):
            if (seed>>j)&1:
                x^=vec
        t=sum(all((x>>v)&1 for v in row) for row in rows)
        assert t%3==0
        hist[t]+=1
    return hist


def component_hist(rows,cube=(0,0),limit_exponent=3):
    n=len(rows)
    blocks=connected_scl_components(rows)
    out=Counter({0:1})
    checked=0
    for block in blocks:
        verts=block["variables"]
        zero=sum(1<<j for j,v in enumerate(verts)
                 if (cube[0]>>v)&1)
        one=sum(1<<j for j,v in enumerate(verts)
                if (cube[1]>>v)&1)
        hist=affine_hist(block["rows"],(zero,one),n**limit_exponent)
        checked+=sum(hist.values())
        combined=Counter()
        for t,a in out.items():
            for u,b in hist.items():
                combined[t+u]+=a*b
        out=combined
    return out,checked


def optimum_for_hist(n,hist,degree):
    raw=[sum(cnt*comb(t,j) for t,cnt in hist.items())
         for j in range(degree+1)]
    return exact_optimal_lp(n,raw,degree)


def compare(root_rows,method,all_which=3):
    n=len(root_rows)
    if method=="small-affine":
        root_hist=affine_hist(root_rows,cap=n**3)
    else:
        root_hist,_=component_hist(root_rows)
    assert sum(root_hist.values())>0
    found_count=root_hist[0]
    base=best_cubic(root_rows)["new_bound"]
    roots={}
    for k in (3,4,5):
        sol=optimum_for_hist(n,root_hist,k)
        roots[str(k)]={
            "optimal_fraction":sol["exact_optimum"],
            "integer_upper_bound":sol["integer_upper_bound"],
            "primal_dual_exact":sol["exact_primal_dual_equality"],
            "primal_support":len(sol["primal_support"]),
            "dual_coefficients":sol["dual_coefficients"],
            "simplex_pivots":sol["iterations"]
        }
    assert roots["3"]["integer_upper_bound"]<=base
    assert all(roots[str(k+1)]["integer_upper_bound"]<=
               roots[str(k)]["integer_upper_bound"] for k in (3,4))
    splits=[]
    for v in range(min(all_which,n)):
        child=[]
        for bit in (0,1):
            cube=((1<<v,0) if bit==0 else (0,1<<v))
            hist=(affine_hist(root_rows,cube,cap=n**3)
                  if method=="small-affine"
                  else component_hist(root_rows,cube)[0])
            child.append(optimum_for_hist(n,hist,3)["integer_upper_bound"])
        total=sum(child)
        assert total<=roots["3"]["integer_upper_bound"]
        splits.append({"v":v,"children":child,"sum":total,
                       "c1_shrink":total*n <=
                       roots["3"]["integer_upper_bound"]*(n-1)})
    return {
        "n":n,"source":method,
        "exact_sol_count":found_count,
        "moment_source":"exhaustive finite oracle" if method=="small-affine"
                         else "independent local affine convolution",
        "previous_best_cubic_family_bound":base,
        "optimal_LPs":roots,
        "degree3_singletons_checked":len(splits),
        "degree3_shrink_pass_count":sum(s["c1_shrink"] for s in splits),
        "degree3_split_samples":splits[:4],
        "degree3_split_range":[min(s["sum"] for s in splits),
                               max(s["sum"] for s in splits)] if splits else None
    }


def self_test():
    p=compare(fixtures()["HolyerPetersen_UNSAT"],"small-affine",45)
    g=compare(k4_blocks(4),"component",72)
    assert p["n"]==45 and p["exact_sol_count"]==0
    assert g["n"]==72 and g["exact_sol_count"]==1296
    assert p["degree3_singletons_checked"]==45
    assert g["degree3_singletons_checked"]==72
    # All 3,4,5 optimum bounds rigorously checked via primal/dual.
    assert all(p["optimal_LPs"][str(k)]["primal_dual_exact"] for k in (3,4,5))
    assert all(g["optimal_LPs"][str(k)]["primal_dual_exact"] for k in (3,4,5))
    return {"scientific_status":"EXACT_OPTIMAL_FIXED_DEGREE_LP_FINITE_REPLAY",
            "Petersen45":p,"SCL72_4K4":g,
            "all_n_uniform_poly_coverage":"NOT_PROVED",
            "P_vs_NP":"OPEN"}


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--self-test",action="store_true")
    args=ap.parse_args()
    if args.self_test:
        print(json.dumps(self_test(),indent=2,sort_keys=True))
    else:
        ap.error("--self-test")
