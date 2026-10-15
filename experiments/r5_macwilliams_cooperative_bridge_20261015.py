#!/usr/bin/env python3
"""SCL Neural Gearbox: proof-carrying ROOT MacWilliams expert + exact DFS.

The full MacWilliams transform applies to the ROOT LINEAR kernel only.
An arbitrary partial x cube gives an affine slice; reusing the same
root constraints on it is NOT justified. Therefore this bridge keeps
the proven root bound separately and uses the earlier exact anchored
moment/LOG_KERNEL/DFS for descendant cubes. Any global frontier
bound may be min(root valid bound, the current anchored DFS bound).
A resource limit always returns UNKNOWN, never speculative UNSAT.

Exact rational simplex as a generator may have exponential pivot
count; polynomial-bit mathematical LP tractability is a DIFFERENT claim.
"""
import argparse,json
from r5_cooperative_scl_coverage_20261015 import (
    validate_scl,gf2_affine,fixtures
)
from r5_fixed_degree_moment_expert_20261015 import raw_binomial_moments
from r5_bidirectional_macwilliams_lp_20261015 import (
    anchors_root,rowspace_low_counts,solve_exact_mac_lp
)
from r5_moment_cooperative_solver_20261015 import solve as prior_scl_solver
from r5_component_factor_20261015 import k4_blocks
from r5_connected_coverage_breaker_20261015 import (
    make_connected,mutate_connected
)
import random


def solve(rows,node_budget=0,k=2,known_dual_degree=3):
    rows=validate_scl(rows)
    n=len(rows)
    if not 0<=k<=3 or not 0<=known_dual_degree<=3:
        raise ValueError("fixed budget k and dual degree <=3")
    if n%3:
        return {"verdict":"UNSAT","proof":"3*|x|=n impossible"}
    affine=gf2_affine(rows,0,0)
    if affine is None:
        raise AssertionError("Ax=1 mod2 has all-ones parity solution")
    _,_,d=affine
    raw,_=raw_binomial_moments(rows,(0,0),degree=k)
    anchors=anchors_root(rows)
    low=rowspace_low_counts(rows,known_dual_degree)
    result=solve_exact_mac_lp(n,d,raw,k,anchors,
                {j:b for j,b in low.items() if j>0})
    assert result["primal_dual_verified"] and result["all_krawtchouk_inequalities_verified"]
    if result["integer_upper_bound"]==0:
        return {
            "verdict":"UNSAT",
            "proof":"exact root dual shows number of SAT solutions <=0",
            "root_Mac_bound":0,"root_proof":result
        }
    # Only use the linear-root Mac constraints on the root, NEVER on
    # partial children without a separately proved affine analogue.
    descendant=prior_scl_solver(
        rows,node_budget=node_budget,moment_degree=3,
        log_kernel_exponent=1,anchored_moments=True)
    assert descendant["verdict"] in (
        "SAT","UNSAT","UNKNOWN_RESOURCE_LIMIT"
    )
    frontier=descendant.get("frontier_bound")
    global_bound=(min(result["integer_upper_bound"],frontier)
                  if frontier is not None else None)
    return {
        "verdict":descendant["verdict"],
        "root_Mac_bound":result["integer_upper_bound"],
        "root_proof":result,
        "descendant_solver":descendant,
        "shared_global_unresolved_upper_bound":global_bound,
        "claim":"root bound global, descendant bound on DFS frontier, both sound"
    }


def connected36(seed):
    rows,witness,_=make_connected(2,seed)
    return mutate_connected(rows,witness,
            random.Random(seed*991+20261015),
            moves=4+(seed%13))[0]


def self_test():
    testcases={
        "SCL36_seed0":(connected36(0),10),
        "SCL36_seed13":(connected36(13),12),
        "Petersen45":(fixtures()["HolyerPetersen_UNSAT"],330),
        "K4x4_72":(k4_blocks(4),1088899)
    }
    out={}
    for name,(rows,expected) in testcases.items():
        trial=solve(rows,node_budget=0,k=2)
        assert trial["verdict"]=="UNKNOWN_RESOURCE_LIMIT"
        assert trial["root_Mac_bound"]==expected
        assert trial["shared_global_unresolved_upper_bound"]<=expected
        out[name]={"n":len(rows),"verdict":trial["verdict"],
                   "root_Mac_bound":trial["root_Mac_bound"],
                   "shared_unresolved_bound":
                   trial["shared_global_unresolved_upper_bound"]}
    return {"scientific_status":"EXACT_ROOT_MAC_GEAR_NONINTRUSIVE_SCL_INTEGRATION",
            "controls":out,
            "root_Mac_on_partial_cubes":"FORBIDDEN_UNLESS_COSERET_PROOF",
            "total_polynomial_SCL":"NOT_CONSTRUCTED",
            "P_vs_NP":"OPEN"}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if not a.self_test:
        p.error("--self-test")
    print(json.dumps(self_test(),sort_keys=True,indent=2))
