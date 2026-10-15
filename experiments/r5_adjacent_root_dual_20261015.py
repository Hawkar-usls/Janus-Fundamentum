#!/usr/bin/env python3
"""All-n certified cubic adjacent-root dual family for SCL moments.

For every legal SCL n divisible by 3 and a in {3,6,...,n-6}:
q_(a,n)(t)=(1-t/a)(1-t/(a+3))(1-t/n)
is >=0 on t=0,3,...,n and q(0)=1. This gives a uniformly
constructible polynomial set O(n) of VALID fixed-degree moment
certificates. The best member is chosen using EXACT rational arithmetic
and independently rank-computed N0..N3. No enumeration of affine words.

We test both Petersen45 and high-nullity 4K4 Holyer72 against the
previous restricted library. A finite stall may remain; never claim
general polynomial progress or P=NP.
"""
from fractions import Fraction as F
from math import comb
import argparse
import json

from r5_fixed_degree_moment_expert_20261015 import (
    check_dual, moment_bounds, raw_binomial_moments, rational_bound
)
from r5_cooperative_scl_coverage_20261015 import fixtures
from r5_moment_coverage_breaker_20261015 import k4_direct_sum


def adjacent_roots_dual(a,n):
    if n%3 or a%3 or not (3<=a<=n-6):
        raise ValueError("requires adjacent positive roots a,a+3 and terminal n")
    roots=(a,a+3,n)
    s1=sum((F(1,r) for r in roots),F(0))
    s2=sum((F(1,x*y) for i,x in enumerate(roots)
            for y in roots[i+1:]),F(0))
    s3=F(1,a*(a+3)*n)
    coeff=(F(1), -s1+s2-s3, 2*s2-6*s3, -6*s3)
    assert check_dual(n,coeff)
    return coeff


def best_cubic(rows,cube=(0,0)):
    n=len(rows)
    raw,d=raw_binomial_moments(rows,cube,3)
    baseline=moment_bounds(rows,cube,3)
    best=baseline["bound"]
    winner={"family":"baseline","root":None,
            "bound":best}
    for a in range(3,n-3,3):
        coeff=adjacent_roots_dual(a,n)
        value,rational=rational_bound(n,raw,coeff)
        if value<best:
            best=value
            winner={"family":"adjacent_roots","root":a,
                    "bound":value,"rational":rational,
                    "coefficients":[str(x) for x in coeff]}
    return {"n":n,"dimension":d,"old_bound":baseline["bound"],
            "new_bound":best,"chosen_certificate":winner}


def probe_graph(rows,variables=(0,1,2)):
    root=best_cubic(rows)
    n=len(rows)
    probes=[]
    for v in variables:
        assert 0<=v<n
        left=best_cubic(rows,(1<<v,0))
        right=best_cubic(rows,(0,1<<v))
        sumchild=left["new_bound"]+right["new_bound"]
        assert sumchild<=root["new_bound"]
        probes.append({"variable":v,
                       "U_root":root["new_bound"],
                       "U_children":sumchild,
                       "geometric_c1":sumchild*n<=root["new_bound"]*(n-1),
                       "left_certificate":left["chosen_certificate"],
                       "right_certificate":right["chosen_certificate"]})
    return {"root":root,"probes":probes}


def self_test():
    p=fixtures()["HolyerPetersen_UNSAT"]
    a=probe_graph(p,(0,1,44))
    assert a["root"]["new_bound"]==480
    assert all(x["U_children"]==467 and x["geometric_c1"] for x in a["probes"])
    g=k4_direct_sum(4)
    b=probe_graph(g,(0,1,2))
    assert b["root"]["new_bound"]<=5452595
    return {
        "status":"CERTIFIED_ALL_N_ADJACENT_ROOT_CUBIC_FAMILY",
        "proven":"all-n dual positivity for adjacent roots, polynomial n templates",
        "Petersen45":a,
        "HolyerK4x4_72":b,
        "uniform_cooperative_coverage":"NOT_PROVED",
        "P_vs_NP":"OPEN",
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--self-test",action="store_true")
    ap.add_argument("--fixture",choices=("Petersen45","HolyerK4x4_72"))
    args=ap.parse_args()
    if args.self_test:
        out=self_test()
    elif args.fixture=="Petersen45":
        out=probe_graph(fixtures()["HolyerPetersen_UNSAT"])
    elif args.fixture=="HolyerK4x4_72":
        out=probe_graph(k4_direct_sum(4))
    else:
        ap.error("--self-test or --fixture required")
    print(json.dumps(out,sort_keys=True,indent=2))


if __name__=="__main__":
    main()
