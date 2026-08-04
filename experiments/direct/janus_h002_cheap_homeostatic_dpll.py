#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import janus_h001_homeostatic_dpll as h1

SCHEMA = "JANUS-H002-CHEAP-HOMEOSTATIC-PROOF-SEARCH-v1"


def choose_cheap_variable(
    cnf: list[list[int]],
    nvars: int,
    node: dict[str, Any],
    conflict_activity: dict[int, int],
    ledger: h1.Ledger,
) -> tuple[int, dict[str, Any]]:
    assignment = {int(k): bool(v) for k, v in node["assignment"].items()}
    unassigned = [var for var in range(1, nvars + 1) if var not in assignment]
    if not unassigned:
        raise AssertionError("open node has no unassigned variable")

    positive_pressure = {var: 0.0 for var in unassigned}
    negative_pressure = {var: 0.0 for var in unassigned}
    tight_occurrence = {var: 0 for var in unassigned}
    unresolved = 0
    pressure = 0.0
    for clause in cnf:
        ledger.charge("CHEAP_PRESSURE_CLAUSE_SCANS")
        state, residual = h1.clause_state(clause, assignment, ledger)
        if state != "OPEN":
            continue
        unresolved += 1
        weight = 1.0 / max(1, len(residual))
        pressure += weight
        for literal in residual:
            var = abs(literal)
            if literal > 0:
                positive_pressure[var] += weight
            else:
                negative_pressure[var] += weight
            if len(residual) <= 3:
                tight_occurrence[var] += 1

    max_total = max([positive_pressure[v] + negative_pressure[v] for v in unassigned] + [1.0])
    max_activity = max([conflict_activity.get(v, 0) for v in unassigned] + [1])
    max_tight = max([tight_occurrence[v] for v in unassigned] + [1])
    evaluations: list[dict[str, Any]] = []
    for var in unassigned:
        positive = positive_pressure[var]
        negative = negative_pressure[var]
        total = positive + negative
        p_positive = positive / total if total else 0.5
        entropy = h1.binary_entropy(p_positive)
        contrast = abs(positive - negative) / max(1e-12, total) if total else 0.0
        normalized_total = total / max_total
        activity = conflict_activity.get(var, 0) / max_activity
        tightness = tight_occurrence[var] / max_tight
        score = (
            1.2 * entropy
            + 0.9 * normalized_total
            + 0.4 * activity
            + 0.25 * tightness
            + 0.15 * contrast
        )
        evaluations.append(
            {
                "variable": var,
                "score": round(score, 12),
                "entropy": round(entropy, 12),
                "positive_pressure": round(positive, 12),
                "negative_pressure": round(negative, 12),
                "total_pressure": round(normalized_total, 12),
                "contrast": round(contrast, 12),
                "activity": round(activity, 12),
                "tightness": round(tightness, 12),
            }
        )
    evaluations.sort(key=lambda item: (-float(item["score"]), int(item["variable"])))
    selected = int(evaluations[0]["variable"])
    return selected, {
        "rule": "CHEAP_POLARITY_ENTROPY",
        "stress": round(pressure / max(1.0, unresolved), 12),
        "evaluations": evaluations,
        "selected_variable": selected,
    }


def solve(cnf: list[list[int]], nvars: int, mode: str, max_nodes: int) -> dict[str, Any]:
    if mode == "BASELINE":
        return h1.solve(cnf, nvars, "BASELINE", max_nodes=max_nodes)
    if mode != "HOMEOSTATIC_CHEAP":
        raise ValueError("unknown mode")
    previous = h1.choose_homeostatic_variable
    try:
        h1.choose_homeostatic_variable = choose_cheap_variable
        run = h1.solve(cnf, nvars, "HOMEOSTATIC", max_nodes=max_nodes)
    finally:
        h1.choose_homeostatic_variable = previous
    run["mode"] = "HOMEOSTATIC_CHEAP"
    run["semantic_digest"] = h1.digest({k: v for k, v in run.items() if k != "semantic_digest"})
    return run


def benchmark_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for seed in range(1, 21):
        cnf, _ = h1.planted_3sat(14, 60, seed)
        cases.append({"name": f"CALIBRATION_PLANTED_3SAT_14_60_SEED_{seed}", "suite": "CALIBRATION", "nvars": 14, "cnf": cnf, "expected": "SAT"})
    for seed in range(101, 201):
        cnf, _ = h1.planted_3sat(14, 60, seed)
        cases.append({"name": f"HOLDOUT_A_PLANTED_3SAT_14_60_SEED_{seed}", "suite": "HOLDOUT_A", "nvars": 14, "cnf": cnf, "expected": "SAT"})
    for seed in range(201, 251):
        cnf, _ = h1.planted_3sat(16, 68, seed)
        cases.append({"name": f"HOLDOUT_B_PLANTED_3SAT_16_68_SEED_{seed}", "suite": "HOLDOUT_B", "nvars": 16, "cnf": cnf, "expected": "SAT"})
    for pigeons, holes in ((4, 3), (5, 4)):
        cnf, nvars = h1.pigeonhole(pigeons, holes)
        cases.append({"name": f"STRUCTURAL_PIGEONHOLE_{pigeons}_{holes}", "suite": "STRUCTURAL", "nvars": nvars, "cnf": cnf, "expected": "UNSAT"})
    cnf, nvars = h1.contradiction_chain(20)
    cases.append({"name": "STRUCTURAL_UNIT_CONTRADICTION_CHAIN_20", "suite": "STRUCTURAL", "nvars": nvars, "cnf": cnf, "expected": "UNSAT"})
    return cases


def empty_totals() -> dict[str, dict[str, int]]:
    return {"BASELINE": {"nodes": 0, "work": 0, "closed": 0}, "HOMEOSTATIC_CHEAP": {"nodes": 0, "work": 0, "closed": 0}}


def comparison_from_totals(case_count: int, totals: dict[str, dict[str, int]]) -> dict[str, int]:
    return {
        "case_count": case_count,
        "baseline_closed": totals["BASELINE"]["closed"],
        "cheap_closed": totals["HOMEOSTATIC_CHEAP"]["closed"],
        "baseline_nodes": totals["BASELINE"]["nodes"],
        "cheap_nodes": totals["HOMEOSTATIC_CHEAP"]["nodes"],
        "baseline_work": totals["BASELINE"]["work"],
        "cheap_work": totals["HOMEOSTATIC_CHEAP"]["work"],
    }


def build_package(max_nodes: int) -> dict[str, Any]:
    cases_out: list[dict[str, Any]] = []
    totals = empty_totals()
    suite_totals: dict[str, dict[str, dict[str, int]]] = {}
    suite_counts: dict[str, int] = {}
    for case in benchmark_cases():
        suite = case["suite"]
        suite_totals.setdefault(suite, empty_totals())
        suite_counts[suite] = suite_counts.get(suite, 0) + 1
        runs: dict[str, Any] = {}
        for mode in ("BASELINE", "HOMEOSTATIC_CHEAP"):
            run = solve(case["cnf"], case["nvars"], mode, max_nodes)
            runs[mode] = run
            for target in (totals, suite_totals[suite]):
                target[mode]["nodes"] += run["audit"]["node_count"]
                target[mode]["work"] += run["audit"]["work"]["total"]
                target[mode]["closed"] += run["result"] in {"SAT", "UNSAT"}
        cases_out.append({"name": case["name"], "suite": suite, "nvars": case["nvars"], "cnf": case["cnf"], "expected": case["expected"], "runs": runs})
    package = {
        "schema": SCHEMA,
        "principle": {
            "persistent_hypotheses": "both decision children remain in the frontier; no branch is pruned heuristically",
            "cognitive_entropy": "binary Shannon entropy of positive and negative residual literal pressure",
            "stress_allocation": "one charged unresolved-clause pass concentrates selection on balanced high-pressure variables",
            "rejected_hypotheses": "every conflict leaf updates a charged variable-activity map",
            "delayed_collapse": "selection order changes, exact branch coverage does not",
            "expensive_branch_probes": False,
        },
        "benchmark_protocol": {
            "calibration": "20 planted 14-variable 60-clause instances, seeds 1 through 20",
            "holdout_a": "100 planted 14-variable 60-clause instances, seeds 101 through 200",
            "holdout_b": "50 planted 16-variable 68-clause instances, seeds 201 through 250",
            "structural": "pigeonhole 4->3, pigeonhole 5->4, and a 20-variable unit contradiction chain",
            "weights_frozen_before_holdout": True,
        },
        "cases": cases_out,
        "comparison": comparison_from_totals(len(cases_out), totals),
        "suite_comparison": {suite: comparison_from_totals(suite_counts[suite], suite_totals[suite]) for suite in sorted(suite_totals)},
        "strict_boundary": {
            "heuristic_component_novelty_claimed": False,
            "exactness_depends_on_independent_replay": True,
            "polynomial_worst_case_proved": False,
            "p_equals_np_claimed": False,
            "p_vs_np": "OPEN",
        },
    }
    package["semantic_digest"] = h1.digest({k: v for k, v in package.items() if k != "semantic_digest"})
    return package


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-nodes", type=int, default=200000)
    args = parser.parse_args()
    package = build_package(args.max_nodes)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(h1.canonical_json(package) + b"\n")
    print(json.dumps(package["comparison"], indent=2, sort_keys=True))
    print("semantic_digest", package["semantic_digest"])


if __name__ == "__main__":
    main()
