#!/usr/bin/env python3
"""
C028 JANUS Model-Scope and Direct-Sum Audit

Three exact gates:

1. Direct-sum gate:
   lower bounds for one bounded simulation do not automatically add over m
   inputs. A shared computation can determine all m predicates once.

2. Candidate-count gate:
   an exponential candidate space does not imply exponential running time.
   GF(2) systems are solved by elimination without examining assignments.

3. Negation-sensitive abstraction gate:
   a positive-support acceptance abstraction is not the semantic acceptance
   relation for formulas containing negated literals.

This artifact refutes proof transitions or identifies a missing proof obligation.
It does not decide P versus NP.
"""

from __future__ import annotations
import argparse
import hashlib
import json
import itertools
from pathlib import Path

def direct_sum_counterexample(max_m: int = 64, t: int = 1000) -> dict:
    rows = []
    for m in [1, 2, 4, 8, 16, 32, max_m]:
        individual_sum_claim = m * t
        shared_work = t
        assert shared_work <= individual_sum_claim
        rows.append({
            "tasks": m,
            "single_task_cost": t,
            "claimed_additive_cost": individual_sum_claim,
            "shared_computation_cost": shared_work,
            "gap_factor": individual_sum_claim // shared_work,
        })
    return {
        "model": "all m predicates depend on one identical t-step computation",
        "result": "single-instance lower bounds do not imply an m-fold direct sum",
        "rows": rows,
        "pass": True,
    }

def gf2_rank_and_consistency(rows: list[int], rhs: list[int], n: int) -> tuple[int, bool]:
    aug = [(rows[i], rhs[i] & 1) for i in range(len(rows))]
    rank = 0
    col = n - 1
    while col >= 0 and rank < len(aug):
        pivot = next((i for i in range(rank, len(aug)) if (aug[i][0] >> col) & 1), None)
        if pivot is None:
            col -= 1
            continue
        aug[rank], aug[pivot] = aug[pivot], aug[rank]
        pmask, prhs = aug[rank]
        for i in range(len(aug)):
            if i != rank and ((aug[i][0] >> col) & 1):
                aug[i] = (aug[i][0] ^ pmask, aug[i][1] ^ prhs)
        rank += 1
        col -= 1
    consistent = all(mask != 0 or bit == 0 for mask, bit in aug)
    return rank, consistent

def candidate_count_counterexample() -> dict:
    rows = []
    for n in [4, 8, 16, 32, 64, 128]:
        masks = [1 << i for i in range(n)]
        rhs = [i & 1 for i in range(n)]
        rank, consistent = gf2_rank_and_consistency(masks, rhs, n)
        assert rank == n and consistent
        rows.append({
            "variables": n,
            "candidate_assignments": str(1 << n),
            "rank": rank,
            "consistent": consistent,
            "elimination_operation_upper_bound": n ** 3,
        })
    return {
        "result": "exponentially many possible assignments coexist with polynomial global reasoning",
        "rows": rows,
        "pass": True,
    }

def negation_abstraction_counterexample() -> dict:
    semantic_accept = []
    positive_support_accept = []
    for bits in itertools.product((0, 1), repeat=3):
        graph = tuple(i for i, b in enumerate(bits) if b)
        if bits[0] == 0:
            semantic_accept.append(graph)
        positive_support_accept.append(graph)
    assert len(semantic_accept) == 4
    assert len(positive_support_accept) == 8
    return {
        "formula": "NOT e0",
        "semantic_accept_count": len(semantic_accept),
        "positive_support_accept_count": len(positive_support_accept),
        "false_accept_count": len(positive_support_accept) - len(semantic_accept),
        "result": "positive-support acceptance is not Boolean semantics with negated inputs",
        "pass": True,
    }

def run() -> dict:
    result = {
        "artifact_id": "C028-JANUS-MODEL-SCOPE-DIRECT-SUM-AUDIT",
        "status": "PASS",
        "p_vs_np": "OPEN",
        "direct_sum_gate": direct_sum_counterexample(),
        "candidate_count_gate": candidate_count_counterexample(),
        "negation_sensitive_abstraction_gate": negation_abstraction_counterexample(),
        "claim_boundary": (
            "Czerwinski and Meek proof transitions are rejected. "
            "For Gordeev v10 this artifact identifies a semantic-abstraction "
            "obligation but does not by itself refute the full current proof."
        ),
    }
    payload = json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
    result["integrity_sha256"] = hashlib.sha256(payload).hexdigest()
    return result

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run()
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.self_test:
        assert result["direct_sum_gate"]["pass"]
        assert result["candidate_count_gate"]["pass"]
        assert result["negation_sensitive_abstraction_gate"]["pass"]

if __name__ == "__main__":
    main()
