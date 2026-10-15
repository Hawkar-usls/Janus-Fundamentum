#!/usr/bin/env python3
"""R5 moment Coverage Breaker: legal high-nullity SCL stress witness.

4 disconnected K4 components -> 72 SCL variables via Holyer reduction.
Unlike Petersen45, 2^d exceeds n^3, so LOG_KERNEL(c=3) DECLINES.
Degree-3 dual polynomials are tested for ALL support points; invalid
Petersen-specific q3 is safely excluded at n=72. Limited one-bit
probes measure whether the certified potential still stalls.
Not an all-n negative lower bound or a hard-instance claim.
"""
import argparse
import json
from itertools import combinations

from r5_cooperative_scl_coverage_20261015 import (
    gf2_affine, holyer, validate_scl
)
from r5_fixed_degree_moment_expert_20261015 import (
    moment_bounds, log_kernel
)


def k4_direct_sum(num):
    edges=[]
    for i in range(num):
        edges.extend((4*i+u,4*i+v)
                     for u,v in combinations(range(4),2))
    return holyer(4*num,edges)


def run(num=4, probes=3):
    if not 1<=num<=4:
        raise ValueError("1<=num<=4")
    rows=validate_scl(k4_direct_sum(num))
    n=len(rows)
    _,basis,d=gf2_affine(rows,0,0)
    root=moment_bounds(rows,degree=3)
    kernel=log_kernel(rows,exponent=3)
    if num==4:
        assert n==72 and d==24 and 1<<d > n**3
        assert kernel["status"]=="DECLINE"
        assert "q3" not in root["duals"],"negative cubic must be rejected"
    results=[]
    for v in range(min(probes,n)):
        low=moment_bounds(rows,(1<<v,0),3)
        high=moment_bounds(rows,(0,1<<v),3)
        combined=low["bound"]+high["bound"]
        assert combined<=root["bound"]
        results.append({
            "variable":v,"U_root":root["bound"],
            "U_split":combined,
            "geometric_c1_met":combined*n<=root["bound"]*(n-1),
            "both_children":(low["bound"],high["bound"]),
            "valid_root_duals":sorted(root["duals"])
        })
    return {
        "scientific_status":"FINITE_COVERAGE_STRESS_NOT_UNIVERSAL_LOWER_BOUND",
        "legal_SCL":True,"connected":False,"n":n,
        "GF2_dimension":d,
        "log_kernel_c3":kernel["status"],
        "root_bound":root["bound"],
        "tested_singleton_splits":results,
        "no_geometric_progress_on_tested_splits":sum(
            not r["geometric_c1_met"] for r in results
        ),
        "fixed_degree_certificate_generation":"POLYNOMIAL_FOR_FIXED_DEGREE",
        "universality":"NOT_PROVED",
        "P_vs_NP":"OPEN"
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--blocks",type=int,default=4)
    ap.add_argument("--probes",type=int,default=3)
    ap.add_argument("--self-test",action="store_true")
    args=ap.parse_args()
    result=run(4,3) if args.self_test else run(args.blocks,args.probes)
    if args.self_test:
        assert len(result["tested_singleton_splits"])==3
        assert result["n"]==72
        assert result["log_kernel_c3"]=="DECLINE"
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
