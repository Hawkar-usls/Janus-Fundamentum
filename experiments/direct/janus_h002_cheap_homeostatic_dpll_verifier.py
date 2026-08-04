#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

import janus_h001_homeostatic_dpll_verifier as v1

EXPECTED_SCHEMA = "JANUS-H002-CHEAP-HOMEOSTATIC-PROOF-SEARCH-v1"


def independent_variable_receipt(
    cnf: list[list[int]],
    nvars: int,
    node: dict[str, Any],
    conflict_activity: dict[int, int],
    counter: v1.AuditCounter,
) -> dict[str, Any]:
    assignment = v1.parse_assignment(node["assignment"])
    unassigned = [var for var in range(1, nvars + 1) if var not in assignment]
    if not unassigned:
        raise AssertionError("open node without decision variable")

    positive_pressure = {var: 0.0 for var in unassigned}
    negative_pressure = {var: 0.0 for var in unassigned}
    tight = {var: 0 for var in unassigned}
    unresolved = 0
    pressure = 0.0
    for clause in cnf:
        counter.add("CHEAP_PRESSURE_CLAUSE_SCANS")
        state, residual = v1.inspect_clause(clause, assignment, counter)
        if state != "OPEN":
            continue
        unresolved += 1
        weight = 1.0 / max(1, len(residual))
        pressure += weight
        for literal in residual:
            variable = abs(literal)
            if literal > 0:
                positive_pressure[variable] += weight
            else:
                negative_pressure[variable] += weight
            if len(residual) <= 3:
                tight[variable] += 1

    max_total = max([positive_pressure[var] + negative_pressure[var] for var in unassigned] + [1.0])
    max_activity = max([conflict_activity.get(var, 0) for var in unassigned] + [1])
    max_tight = max([tight[var] for var in unassigned] + [1])
    evaluations: list[dict[str, Any]] = []
    for variable in unassigned:
        positive = positive_pressure[variable]
        negative = negative_pressure[variable]
        total = positive + negative
        p_positive = positive / total if total else 0.5
        entropy = v1.entropy(p_positive)
        contrast = abs(positive - negative) / max(1e-12, total) if total else 0.0
        normalized_total = total / max_total
        activity = conflict_activity.get(variable, 0) / max_activity
        tightness = tight[variable] / max_tight
        score = (
            1.2 * entropy
            + 0.9 * normalized_total
            + 0.4 * activity
            + 0.25 * tightness
            + 0.15 * contrast
        )
        evaluations.append(
            {
                "variable": variable,
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
    return {
        "rule": "CHEAP_POLARITY_ENTROPY",
        "stress": round(pressure / max(1.0, unresolved), 12),
        "evaluations": evaluations,
        "selected_variable": selected,
    }


def verify_run(run: dict[str, Any], mode: str, cnf: list[list[int]], nvars: int) -> None:
    if run.get("mode") != mode or run.get("cnf") != cnf or int(run.get("nvars")) != nvars:
        raise AssertionError("run identity mismatch")
    if run.get("cnf_digest") != v1.digest(cnf):
        raise AssertionError("CNF digest mismatch")
    if run.get("semantic_digest") != v1.digest({k: value for k, value in run.items() if k != "semantic_digest"}):
        raise AssertionError("run digest mismatch")

    raw_nodes = run.get("nodes")
    if not isinstance(raw_nodes, list) or not raw_nodes:
        raise AssertionError("missing nodes")
    nodes = {int(node["node_id"]): node for node in raw_nodes}
    if sorted(nodes) != list(range(len(nodes))):
        raise AssertionError("non-contiguous node ids")
    for node_id, node in sorted(nodes.items()):
        v1.verify_node(cnf, nvars, node, v1.AuditCounter())
        parent_id = node.get("parent_id")
        decision = node.get("decision")
        if node_id == 0:
            if parent_id is not None or decision is not None or node.get("depth") != 0:
                raise AssertionError("malformed root")
            continue
        if parent_id not in nodes or not isinstance(decision, dict):
            raise AssertionError("malformed child")
        parent = nodes[int(parent_id)]
        if node.get("depth") != int(parent["depth"]) + 1:
            raise AssertionError("depth mismatch")
        seed = v1.parse_assignment(parent["assignment"])
        seed[int(decision["variable"])] = bool(decision["value"])
        if node.get("input_assignment") != {str(key): value for key, value in sorted(seed.items())}:
            raise AssertionError("child seed mismatch")

    counter = v1.AuditCounter()
    v1.verify_node(cnf, nvars, nodes[0], counter)
    generated = {0}
    frontier = [0] if nodes[0]["status"] == "OPEN" else []
    activity: dict[int, int] = {}
    v1.add_conflict(cnf, nodes[0], activity)
    expanded: set[int] = set()

    for step, event in enumerate(run.get("events", [])):
        if event.get("step") != step or event.get("frontier_before") != frontier:
            raise AssertionError("frontier transcript mismatch")
        if mode == "BASELINE":
            priorities: list[dict[str, Any]] = []
            selected = min(frontier)
        else:
            priorities = [v1.state_receipt(nodes[node_id], nodes, frontier, nvars) for node_id in frontier]
            priorities.sort(key=lambda item: (-float(item["score"]), int(item["node_id"])))
            selected = int(priorities[0]["node_id"])
            counter.add("STATE_PRIORITY_EVALUATIONS", len(frontier))
        if event.get("node_priorities") != priorities or event.get("selected_node_id") != selected:
            raise AssertionError("state scheduler mismatch")
        frontier.remove(selected)
        node = nodes[selected]
        assignment = v1.parse_assignment(node["assignment"])
        if mode == "BASELINE":
            variable = min(var for var in range(1, nvars + 1) if var not in assignment)
            receipt = {"selected_variable": variable, "rule": "MIN_UNASSIGNED"}
        else:
            receipt = independent_variable_receipt(cnf, nvars, node, activity, counter)
            variable = int(receipt["selected_variable"])
        if event.get("variable_receipt") != receipt or node.get("decision_variable") != variable:
            raise AssertionError("variable scheduler mismatch")

        child_ids = event.get("child_ids")
        if child_ids != [len(generated), len(generated) + 1] or node.get("children") != child_ids:
            raise AssertionError("binary child allocation mismatch")
        counter.add("NODE_EXPANSIONS")
        for value, child_id in zip((False, True), child_ids):
            if child_id not in nodes or child_id in generated:
                raise AssertionError("missing child")
            child = nodes[int(child_id)]
            v1.verify_node(cnf, nvars, child, counter)
            generated.add(int(child_id))
            if child.get("parent_id") != selected or child.get("decision") != {"variable": variable, "value": value}:
                raise AssertionError("child decision mismatch")
            v1.add_conflict(cnf, child, activity)
            if child["status"] == "OPEN":
                frontier.append(int(child_id))
        if event.get("frontier_after") != frontier:
            raise AssertionError("frontier-after mismatch")
        if event.get("conflict_activity_after") != {str(key): value for key, value in sorted(activity.items())}:
            raise AssertionError("conflict activity mismatch")
        if event.get("cumulative_work") != counter.total:
            raise AssertionError("cumulative work mismatch")
        expanded.add(selected)

    if generated != set(nodes) or run.get("remaining_frontier") != frontier:
        raise AssertionError("unreachable nodes or final frontier mismatch")
    result = run.get("result")
    terminal = run.get("terminal_node_id")
    if result == "SAT":
        if terminal not in nodes or nodes[int(terminal)]["status"] != "SAT":
            raise AssertionError("invalid SAT terminal")
        witness = v1.parse_assignment(run.get("witness") or {})
        if any(not any(v1.lit_value(literal, witness) is True for literal in clause) for clause in cnf):
            raise AssertionError("false SAT witness")
    elif result == "UNSAT":
        if terminal is not None or frontier:
            raise AssertionError("incomplete UNSAT tree")
        if any(node["status"] == "OPEN" and node_id not in expanded for node_id, node in nodes.items()):
            raise AssertionError("unexpanded UNSAT leaf")
    elif result != "OPEN_NODE_BUDGET" or not frontier:
        raise AssertionError("invalid terminal")

    expected_audit = {
        "node_count": len(nodes),
        "expansion_count": len(run.get("events", [])),
        "conflict_count": sum(node["status"] == "CONFLICT" for node in nodes.values()),
        "max_frontier": max([0] + [len(event["frontier_before"]) for event in run.get("events", [])] + [len(frontier)]),
        "work": {"counts": dict(sorted(counter.counts.items())), "total": counter.total},
    }
    if run.get("audit") != expected_audit:
        raise AssertionError("audit mismatch")


def empty_comparison() -> dict[str, int]:
    return {"case_count": 0, "baseline_closed": 0, "cheap_closed": 0, "baseline_nodes": 0, "cheap_nodes": 0, "baseline_work": 0, "cheap_work": 0}


def add_pair(summary: dict[str, int], baseline: dict[str, Any], cheap: dict[str, Any]) -> None:
    summary["case_count"] += 1
    summary["baseline_closed"] += baseline["result"] in {"SAT", "UNSAT"}
    summary["cheap_closed"] += cheap["result"] in {"SAT", "UNSAT"}
    summary["baseline_nodes"] += baseline["audit"]["node_count"]
    summary["cheap_nodes"] += cheap["audit"]["node_count"]
    summary["baseline_work"] += baseline["audit"]["work"]["total"]
    summary["cheap_work"] += cheap["audit"]["work"]["total"]


def verify_package(package: dict[str, Any]) -> None:
    if package.get("schema") != EXPECTED_SCHEMA:
        raise AssertionError("schema mismatch")
    if package.get("semantic_digest") != v1.digest({k: value for k, value in package.items() if k != "semantic_digest"}):
        raise AssertionError("package digest mismatch")
    boundary = package.get("strict_boundary") or {}
    if boundary.get("polynomial_worst_case_proved") is not False or boundary.get("p_equals_np_claimed") is not False or boundary.get("p_vs_np") != "OPEN":
        raise AssertionError("forbidden complexity promotion")
    if (package.get("benchmark_protocol") or {}).get("weights_frozen_before_holdout") is not True:
        raise AssertionError("unfrozen holdout protocol")

    total = empty_comparison()
    suites: dict[str, dict[str, int]] = {}
    for case in package.get("cases", []):
        cnf = case["cnf"]
        nvars = int(case["nvars"])
        suite = case.get("suite")
        if suite not in {"CALIBRATION", "HOLDOUT_A", "HOLDOUT_B", "STRUCTURAL"}:
            raise AssertionError("unknown suite")
        for clause in cnf:
            if len(set(clause)) != len(clause) or any(literal == 0 or abs(literal) > nvars for literal in clause):
                raise AssertionError("malformed CNF")
        runs = case.get("runs") or {}
        baseline = runs.get("BASELINE")
        cheap = runs.get("HOMEOSTATIC_CHEAP")
        if baseline is None or cheap is None:
            raise AssertionError("missing paired run")
        verify_run(baseline, "BASELINE", cnf, nvars)
        verify_run(cheap, "HOMEOSTATIC_CHEAP", cnf, nvars)
        if baseline["result"] != case.get("expected") or cheap["result"] != case.get("expected"):
            raise AssertionError("expected result mismatch")
        suites.setdefault(str(suite), empty_comparison())
        add_pair(total, baseline, cheap)
        add_pair(suites[str(suite)], baseline, cheap)
    if package.get("comparison") != total or package.get("suite_comparison") != dict(sorted(suites.items())):
        raise AssertionError("summary mismatch")


def repair(package: dict[str, Any]) -> dict[str, Any]:
    for case in package.get("cases", []):
        for run in (case.get("runs") or {}).values():
            run["semantic_digest"] = v1.digest({k: value for k, value in run.items() if k != "semantic_digest"})
    package["semantic_digest"] = v1.digest({k: value for k, value in package.items() if k != "semantic_digest"})
    return package


def tamper_self_test(package: dict[str, Any]) -> None:
    mutants: list[tuple[str, dict[str, Any]]] = []
    a = copy.deepcopy(package)
    sat = next(case["runs"]["HOMEOSTATIC_CHEAP"] for case in a["cases"] if case["runs"]["HOMEOSTATIC_CHEAP"]["result"] == "SAT")
    key = sorted(sat["witness"], key=int)[0]
    sat["witness"][key] = not sat["witness"][key]
    mutants.append(("witness", repair(a)))
    b = copy.deepcopy(package)
    b["cases"][0]["runs"]["HOMEOSTATIC_CHEAP"]["events"][0]["selected_node_id"] = 999999
    mutants.append(("scheduler", repair(b)))
    c = copy.deepcopy(package)
    child = c["cases"][0]["runs"]["BASELINE"]["nodes"][1]
    key = next(iter(child["assignment"]))
    child["assignment"][key] = not child["assignment"][key]
    mutants.append(("node", repair(c)))
    d = copy.deepcopy(package)
    d["cases"][0]["runs"]["HOMEOSTATIC_CHEAP"]["audit"]["work"]["total"] += 1
    mutants.append(("work", repair(d)))
    for name, mutant in mutants:
        try:
            verify_package(mutant)
        except AssertionError:
            continue
        raise AssertionError(f"tamper accepted: {name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--tamper-self-test", action="store_true")
    args = parser.parse_args()
    package = json.loads(args.artifact.read_text())
    verify_package(package)
    if args.tamper_self_test:
        tamper_self_test(package)
    print(json.dumps({"verified": True, "tamper_self_test": bool(args.tamper_self_test), "comparison": package["comparison"], "semantic_digest": package["semantic_digest"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
