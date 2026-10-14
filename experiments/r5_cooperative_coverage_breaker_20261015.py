#!/usr/bin/env python3
"""R5 SCL-native Cooperative Coverage Breaker.

Generate exactly legal square/cubic/linear positive 1-in-3-SAT
incidences by summing three random permutation matrices, rejecting
any violation of simple, three-regular or linear requirements.
Freeze RNG seed and return COMPLETE rows and SHA256 for reproduction.

Run a bounded family of experts on each legal generated matrix.
A 'cooperative stall' means THIS PARTICULAR restricted portfolio,
potential and per-state bound fail to reach the prescribed relative
improvement; NOT a proof that all polynomial algorithms fail.
"""
import argparse
import json
import random
from r5_cooperative_scl_coverage_20261015 import (
    validate_scl, fingerprint, solve, fixtures
)


def generate_legal(n, rng, limit=20000):
    if n < 9:
        raise ValueError("n must be >=9 for randomized generator")
    for attempted in range(1, limit+1):
        perms = [rng.sample(range(n), n) for _ in range(3)]
        source = [
            tuple(perms[c][row] for c in range(3))
            for row in range(n)
        ]
        try:
            rows = validate_scl(source)
        except ValueError:
            continue
        return rows, attempted
    raise RuntimeError("rejection sampler found no legal graph in budget")


def cooperative_falsification_case(rows, node_budget=2, kernel_limit=8,
                                    power=1):
    state = solve(rows, node_budget=node_budget,
                  kernel_limit=kernel_limit, progress_power=power)
    branch = next((e for e in state["proof_step_log"]
                   if e["expert"] == "BRANCH"), None)
    found = {
        "n": len(rows),
        "sha256": fingerprint(rows),
        "rows": [list(r) for r in rows],
        "verdict": state["verdict"],
        "U_initial": state["initial_frontier_bound"],
        "U_remaining": state["frontier_bound"],
        "GF2_candidate_count": state["initial_GF2_candidates"],
        "cooperative_stalls": state["cooperative_stalls"],
        "budget_nodes": node_budget,
        "tried_nodes": state["work_nodes_this_call"],
        "bounded_progress_failed": False,
    }
    if branch:
        a, b = branch["U_before"], branch["U_after"]
        significant = (
            b * len(rows)**power <=
            (len(rows)**power - 1) * a
        )
        found["first_branch"] = {
            "U_before": a,
            "U_after": b,
            "fractional_threshold_met": significant
        }
        found["bounded_progress_failed"] = not significant
    return found


def search(n=12, samples=3, seed=20261015, node_budget=2,
           rejection_limit=30000):
    if n % 3:
        raise ValueError("n must be divisible by 3")
    if not 0 < samples <= 12:
        raise ValueError("1<=samples<=12")
    if node_budget > 4*n*n or node_budget < 1:
        raise ValueError("budget must be 1..4n^2")
    rng = random.Random(seed)
    outcomes = []
    total_tries = 0
    for _ in range(samples):
        rows, attempts = generate_legal(n, rng, rejection_limit)
        total_tries += attempts
        candidate = cooperative_falsification_case(
            rows, node_budget=node_budget
        )
        candidate["generation_attempts"] = attempts
        outcomes.append(candidate)
    # Known protected negative test from a Holyer reduction, not an
    # invented SAT/UNSAT decision at a tiny computational budget.
    protected = cooperative_falsification_case(
        fixtures()["HolyerPetersen_UNSAT"],
        node_budget=3
    )
    if not protected["bounded_progress_failed"]:
        raise AssertionError("frozen Petersen bounded stall changed")
    return {
        "status": "BOUNDED_PORTFOLIO_FALSIFICATION_NOT_ALL_N_LOWER_BOUND",
        "seed": seed, "n": n, "samples": samples,
        "generation_attempts": total_tries,
        "results": outcomes,
        "frozen_Holyer_Petersen45_stall": protected,
        "hypothesis": "this finite restricted expert portfolio at this finite budget",
        "universal_cooperative_progress": "NOT_PROVED",
        "P_vs_NP": "OPEN",
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n",type=int,default=12)
    parser.add_argument("--samples",type=int,default=3)
    parser.add_argument("--seed",type=int,default=20261015)
    parser.add_argument("--node-budget",type=int,default=2)
    parser.add_argument("--rejection-limit",type=int,default=30000)
    parser.add_argument("--self-test",action="store_true")
    args=parser.parse_args()
    if args.self_test:
        report=search(12,2,20261015,2,30000)
        assert len(report["results"])==2
        assert all(validate_scl(item["rows"])
                   for item in report["results"])
        assert report["frozen_Holyer_Petersen45_stall"]["bounded_progress_failed"]
    else:
        report=search(args.n,args.samples,args.seed,
                      args.node_budget,args.rejection_limit)
    print(json.dumps(report,sort_keys=True,indent=2))


if __name__ == "__main__":
    main()
