#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

EXPECTED_SCHEMA = "JANUS-H001-HOMEOSTATIC-PROOF-SEARCH-v1"


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


@dataclass
class AuditCounter:
    counts: dict[str, int] = field(default_factory=dict)

    def add(self, name: str, amount: int = 1) -> None:
        if amount < 0:
            raise AssertionError("negative accounting")
        self.counts[name] = self.counts.get(name, 0) + amount

    @property
    def total(self) -> int:
        return sum(self.counts.values())


def lit_value(lit: int, assignment: dict[int, bool]) -> bool | None:
    value = assignment.get(abs(lit))
    if value is None:
        return None
    return value if lit > 0 else not value


def inspect_clause(
    clause: list[int], assignment: dict[int, bool], counter: AuditCounter
) -> tuple[str, list[int]]:
    residual: list[int] = []
    for literal in clause:
        counter.add("LITERAL_EVALUATIONS")
        value = lit_value(literal, assignment)
        if value is True:
            return "SAT", []
        if value is None:
            residual.append(literal)
    return ("OPEN", residual) if residual else ("CONFLICT", [])


def canonical_propagation(
    cnf: list[list[int]], seed: dict[int, bool], counter: AuditCounter
) -> tuple[dict[int, bool], list[dict[str, Any]], str, int | None]:
    assignment = dict(seed)
    receipt: list[dict[str, Any]] = []
    while True:
        first_unit: tuple[int, bool, int] | None = None
        all_satisfied = True
        for clause_id, clause in enumerate(cnf):
            counter.add("CLAUSE_SCANS")
            state, residual = inspect_clause(clause, assignment, counter)
            if state == "CONFLICT":
                return assignment, receipt, "CONFLICT", clause_id
            if state != "SAT":
                all_satisfied = False
            if state == "OPEN" and len(residual) == 1 and first_unit is None:
                literal = residual[0]
                first_unit = (abs(literal), literal > 0, clause_id)
        if all_satisfied:
            return assignment, receipt, "SAT", None
        if first_unit is None:
            return assignment, receipt, "OPEN", None
        variable, value, clause_id = first_unit
        previous = assignment.get(variable)
        if previous is not None and previous != value:
            return assignment, receipt, "CONFLICT", clause_id
        if previous is None:
            assignment[variable] = value
            receipt.append({"variable": variable, "value": value, "reason_clause": clause_id})
            counter.add("UNIT_PROPAGATIONS")


def profile(
    cnf: list[list[int]], assignment: dict[int, bool], counter: AuditCounter
) -> tuple[int, int, float, dict[int, int]]:
    unresolved = 0
    literals = 0
    pressure = 0.0
    tight: dict[int, int] = {}
    for clause in cnf:
        counter.add("PROFILE_CLAUSE_SCANS")
        state, residual = inspect_clause(clause, assignment, counter)
        if state != "OPEN":
            continue
        unresolved += 1
        literals += len(residual)
        pressure += 1.0 / max(1, len(residual))
        if len(residual) <= 3:
            for literal in residual:
                variable = abs(literal)
                tight[variable] = tight.get(variable, 0) + 1
    return unresolved, literals, pressure, tight


def parse_assignment(raw: dict[str, Any]) -> dict[int, bool]:
    return {int(key): bool(value) for key, value in raw.items()}


def verify_node(
    cnf: list[list[int]], nvars: int, node: dict[str, Any], counter: AuditCounter
) -> None:
    seed = parse_assignment(node["input_assignment"])
    if any(variable < 1 or variable > nvars for variable in seed):
        raise AssertionError("node assignment outside variable range")
    propagated, receipt, status, conflict = canonical_propagation(cnf, seed, counter)
    unresolved, residual, pressure, _ = profile(cnf, propagated, counter)
    counter.add("NODES_CREATED")
    expected = {
        "assignment": {str(k): v for k, v in sorted(propagated.items())},
        "propagations": receipt,
        "status": status,
        "conflict_clause": conflict,
        "unresolved_clauses": unresolved,
        "residual_literals": residual,
        "pressure": round(pressure, 12),
    }
    for key, value in expected.items():
        if node.get(key) != value:
            raise AssertionError(f"node {node.get('node_id')} mismatch in {key}")


def entropy(p: float) -> float:
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return -(p * math.log2(p) + (1.0 - p) * math.log2(1.0 - p))


def probe(
    cnf: list[list[int]], assignment: dict[int, bool], variable: int, value: bool, counter: AuditCounter
) -> dict[str, Any]:
    counter.add("BRANCH_PROBES")
    trial = dict(assignment)
    trial[variable] = value
    closed, receipt, status, conflict = canonical_propagation(cnf, trial, counter)
    unresolved, residual, pressure, _ = profile(cnf, closed, counter)
    return {
        "value": value,
        "status": status,
        "conflict_clause": conflict,
        "forced_count": len(receipt),
        "assigned_count": len(closed),
        "unresolved_clauses": unresolved,
        "residual_literals": residual,
        "pressure": round(pressure, 12),
    }


def energy(item: dict[str, Any], clause_count: int) -> float:
    if item["status"] == "CONFLICT":
        return float(clause_count + 1)
    if item["status"] == "SAT":
        return 0.0
    return float(item["unresolved_clauses"]) + 0.01 * float(item["residual_literals"])


def independent_variable_receipt(
    cnf: list[list[int]],
    nvars: int,
    node: dict[str, Any],
    conflict_activity: dict[int, int],
    counter: AuditCounter,
) -> dict[str, Any]:
    assignment = parse_assignment(node["assignment"])
    unassigned = [v for v in range(1, nvars + 1) if v not in assignment]
    if not unassigned:
        raise AssertionError("open node without decision variable")
    _, _, raw_pressure, tight = profile(cnf, assignment, counter)
    stress = min(1.0, raw_pressure / max(1.0, float(node["unresolved_clauses"])))
    probe_cap = min(len(unassigned), 1 + int(math.floor(2.0 * stress)))
    ranked = sorted(
        unassigned,
        key=lambda variable: (
            int(tight.get(variable, 0)),
            int(conflict_activity.get(variable, 0)),
            -variable,
        ),
        reverse=True,
    )[:probe_cap]
    max_activity = max([conflict_activity.get(v, 0) for v in unassigned] + [1])
    max_tight = max([tight.get(v, 0) for v in unassigned] + [1])
    evaluations: list[dict[str, Any]] = []
    for variable in ranked:
        false_result = probe(cnf, assignment, variable, False, counter)
        true_result = probe(cnf, assignment, variable, True, counter)
        e0 = energy(false_result, len(cnf))
        e1 = energy(true_result, len(cnf))
        temperature = max(0.25, 1.0 - 0.5 * stress)
        z0 = math.exp(-e0 / max(1.0, len(cnf) * temperature))
        z1 = math.exp(-e1 / max(1.0, len(cnf) * temperature))
        p0 = z0 / (z0 + z1)
        branch_entropy = entropy(p0)
        contrast = abs(e0 - e1) / max(1.0, e0 + e1)
        activity = conflict_activity.get(variable, 0) / max_activity
        tightness = tight.get(variable, 0) / max_tight
        terminal_bonus = 1.0 if {false_result["status"], true_result["status"]} & {"SAT", "CONFLICT"} else 0.0
        score = branch_entropy + 0.8 * contrast + 0.45 * activity + 0.35 * tightness + 0.5 * terminal_bonus
        evaluations.append(
            {
                "variable": variable,
                "score": round(score, 12),
                "entropy": round(branch_entropy, 12),
                "contrast": round(contrast, 12),
                "activity": round(activity, 12),
                "tightness": round(tightness, 12),
                "temperature": round(temperature, 12),
                "false_probe": false_result,
                "true_probe": true_result,
            }
        )
    evaluations.sort(key=lambda item: (-float(item["score"]), int(item["variable"])))
    selected = int(evaluations[0]["variable"])
    return {
        "stress": round(stress, 12),
        "probe_cap": probe_cap,
        "candidate_variables": ranked,
        "evaluations": evaluations,
        "selected_variable": selected,
    }


def diversity(nodes: dict[int, dict[str, Any]], frontier: list[int], node_id: int, nvars: int) -> float:
    if len(frontier) <= 1 or nvars == 0:
        return 0.0
    target = parse_assignment(nodes[node_id]["assignment"])
    distances: list[float] = []
    for other_id in frontier:
        if other_id == node_id:
            continue
        other = parse_assignment(nodes[other_id]["assignment"])
        different = 0
        compared = 0
        for variable in range(1, nvars + 1):
            if variable in target and variable in other:
                compared += 1
                different += target[variable] != other[variable]
            elif variable in target or variable in other:
                compared += 1
                different += 1
        distances.append(different / max(1, compared))
    return sum(distances) / max(1, len(distances))


def state_receipt(
    node: dict[str, Any], nodes: dict[int, dict[str, Any]], frontier: list[int], nvars: int
) -> dict[str, Any]:
    novelty = diversity(nodes, frontier, int(node["node_id"]), nvars)
    unresolved = int(node["unresolved_clauses"])
    normalized_pressure = float(node["pressure"]) / max(1.0, unresolved)
    depth = int(node["depth"])
    score = normalized_pressure + 0.35 * novelty + 0.01 * depth
    return {
        "node_id": int(node["node_id"]),
        "score": round(score, 12),
        "normalized_pressure": round(normalized_pressure, 12),
        "diversity": round(novelty, 12),
        "depth": depth,
    }


def add_conflict(cnf: list[list[int]], node: dict[str, Any], activity: dict[int, int]) -> None:
    if node["status"] != "CONFLICT":
        return
    clause_id = node["conflict_clause"]
    if clause_id is None:
        raise AssertionError("conflict without reason")
    for literal in cnf[int(clause_id)]:
        variable = abs(literal)
        activity[variable] = activity.get(variable, 0) + 1


def verify_run(run: dict[str, Any], expected_mode: str, expected_cnf: list[list[int]], expected_nvars: int) -> None:
    if run.get("mode") != expected_mode:
        raise AssertionError("mode mismatch")
    if run.get("cnf") != expected_cnf or int(run.get("nvars")) != expected_nvars:
        raise AssertionError("run input mismatch")
    if run.get("cnf_digest") != digest(expected_cnf):
        raise AssertionError("CNF digest mismatch")
    run_without_digest = {k: v for k, v in run.items() if k != "semantic_digest"}
    if run.get("semantic_digest") != digest(run_without_digest):
        raise AssertionError("run semantic digest mismatch")

    raw_nodes = run.get("nodes")
    if not isinstance(raw_nodes, list) or not raw_nodes:
        raise AssertionError("missing nodes")
    nodes = {int(node["node_id"]): node for node in raw_nodes}
    if sorted(nodes) != list(range(len(nodes))):
        raise AssertionError("non-contiguous node ids")
    # First validate each frozen node in isolation. Accounting is replayed below in producer order.
    for node_id in sorted(nodes):
        node = nodes[node_id]
        verify_node(expected_cnf, expected_nvars, node, AuditCounter())
        parent_id = node.get("parent_id")
        decision = node.get("decision")
        if node_id == 0:
            if parent_id is not None or decision is not None or node.get("depth") != 0:
                raise AssertionError("malformed root")
        else:
            if parent_id not in nodes or not isinstance(decision, dict):
                raise AssertionError("malformed child link")
            parent = nodes[int(parent_id)]
            variable = int(decision["variable"])
            value = bool(decision["value"])
            if node.get("depth") != int(parent["depth"]) + 1:
                raise AssertionError("depth mismatch")
            inherited = parse_assignment(parent["assignment"])
            inherited[variable] = value
            if node.get("input_assignment") != {str(k): v for k, v in sorted(inherited.items())}:
                raise AssertionError("child seed mismatch")

    counter = AuditCounter()
    verify_node(expected_cnf, expected_nvars, nodes[0], counter)
    generated: set[int] = {0}
    frontier = [0] if nodes[0]["status"] == "OPEN" else []
    conflict_activity: dict[int, int] = {}
    add_conflict(expected_cnf, nodes[0], conflict_activity)
    expanded: set[int] = set()
    for step, event in enumerate(run.get("events", [])):
        if event.get("step") != step or event.get("frontier_before") != frontier:
            raise AssertionError("frontier transcript mismatch")
        if not frontier:
            raise AssertionError("event after frontier exhaustion")
        if expected_mode == "BASELINE":
            selected = min(frontier)
            expected_priorities: list[dict[str, Any]] = []
        else:
            expected_priorities = [state_receipt(nodes[node_id], nodes, frontier, expected_nvars) for node_id in frontier]
            expected_priorities.sort(key=lambda item: (-float(item["score"]), int(item["node_id"])))
            selected = int(expected_priorities[0]["node_id"])
            counter.add("STATE_PRIORITY_EVALUATIONS", len(frontier))
        if event.get("node_priorities") != expected_priorities:
            raise AssertionError("node-priority receipt mismatch")
        if event.get("selected_node_id") != selected:
            raise AssertionError("scheduler selected wrong node")
        frontier.remove(selected)
        node = nodes[selected]
        assignment = parse_assignment(node["assignment"])
        if expected_mode == "BASELINE":
            variable = min(v for v in range(1, expected_nvars + 1) if v not in assignment)
            expected_variable_receipt = {"selected_variable": variable, "rule": "MIN_UNASSIGNED"}
        else:
            expected_variable_receipt = independent_variable_receipt(
                expected_cnf, expected_nvars, node, conflict_activity, counter
            )
            variable = int(expected_variable_receipt["selected_variable"])
        if event.get("variable_receipt") != expected_variable_receipt:
            raise AssertionError("variable receipt mismatch")
        if node.get("decision_variable") != variable:
            raise AssertionError("node decision variable mismatch")
        child_ids = event.get("child_ids")
        if not isinstance(child_ids, list) or len(child_ids) != 2 or node.get("children") != child_ids:
            raise AssertionError("binary branch coverage mismatch")
        counter.add("NODE_EXPANSIONS")
        if child_ids != [len(generated), len(generated) + 1]:
            raise AssertionError("non-canonical child allocation")
        for expected_value, child_id in zip((False, True), child_ids):
            if child_id not in nodes or child_id in generated:
                raise AssertionError("missing or duplicate child")
            child = nodes[int(child_id)]
            verify_node(expected_cnf, expected_nvars, child, counter)
            generated.add(int(child_id))
            decision = child.get("decision")
            if child.get("parent_id") != selected or decision != {"variable": variable, "value": expected_value}:
                raise AssertionError("child decision mismatch")
            add_conflict(expected_cnf, child, conflict_activity)
            if child["status"] == "OPEN":
                frontier.append(int(child_id))
        if event.get("frontier_after") != frontier:
            raise AssertionError("frontier-after mismatch")
        expected_activity = {str(k): v for k, v in sorted(conflict_activity.items())}
        if event.get("conflict_activity_after") != expected_activity:
            raise AssertionError("conflict activity mismatch")
        if event.get("cumulative_work") != counter.total:
            raise AssertionError("cumulative work mismatch")
        expanded.add(selected)

    if generated != set(nodes):
        raise AssertionError("unreachable frozen nodes")

    terminal = run.get("terminal_node_id")
    result = run.get("result")
    remaining = run.get("remaining_frontier")
    if remaining != frontier:
        raise AssertionError("final frontier mismatch")
    if result == "SAT":
        if terminal not in nodes or nodes[int(terminal)]["status"] != "SAT":
            raise AssertionError("invalid SAT terminal")
        witness = parse_assignment(run.get("witness") or {})
        for clause in expected_cnf:
            if not any(lit_value(literal, witness) is True for literal in clause):
                raise AssertionError("false SAT witness")
    elif result == "UNSAT":
        if terminal is not None or frontier:
            raise AssertionError("incomplete UNSAT tree")
        if any(node["status"] == "OPEN" and node_id not in expanded for node_id, node in nodes.items()):
            raise AssertionError("unexpanded open leaf in UNSAT certificate")
    elif result == "OPEN_NODE_BUDGET":
        if not frontier:
            raise AssertionError("budget terminal without remaining frontier")
    else:
        raise AssertionError("unknown result")

    expected_audit = {
        "node_count": len(nodes),
        "expansion_count": len(run.get("events", [])),
        "conflict_count": sum(node["status"] == "CONFLICT" for node in nodes.values()),
        "max_frontier": max([0] + [len(event["frontier_before"]) for event in run.get("events", [])] + [len(frontier)]),
        "work": {"counts": dict(sorted(counter.counts.items())), "total": counter.total},
    }
    if run.get("audit") != expected_audit:
        raise AssertionError("run audit mismatch")


def verify_package(package: dict[str, Any]) -> None:
    if package.get("schema") != EXPECTED_SCHEMA:
        raise AssertionError("schema mismatch")
    without_digest = {k: v for k, v in package.items() if k != "semantic_digest"}
    if package.get("semantic_digest") != digest(without_digest):
        raise AssertionError("package semantic digest mismatch")
    boundary = package.get("strict_boundary") or {}
    if boundary.get("p_equals_np_claimed") is not False or boundary.get("p_vs_np") != "OPEN":
        raise AssertionError("forbidden P versus NP promotion")
    if boundary.get("polynomial_worst_case_proved") is not False:
        raise AssertionError("forbidden complexity promotion")

    computed = {
        "case_count": 0,
        "baseline_closed": 0,
        "homeostatic_closed": 0,
        "baseline_nodes": 0,
        "homeostatic_nodes": 0,
        "baseline_work": 0,
        "homeostatic_work": 0,
    }
    for case in package.get("cases", []):
        cnf = case["cnf"]
        nvars = int(case["nvars"])
        for clause in cnf:
            if len(set(clause)) != len(clause) or any(lit == 0 or abs(lit) > nvars for lit in clause):
                raise AssertionError("malformed benchmark CNF")
        runs = case.get("runs") or {}
        baseline = runs.get("BASELINE")
        homeostatic = runs.get("HOMEOSTATIC")
        if baseline is None or homeostatic is None:
            raise AssertionError("missing paired runs")
        verify_run(baseline, "BASELINE", cnf, nvars)
        verify_run(homeostatic, "HOMEOSTATIC", cnf, nvars)
        expected = case.get("expected")
        if baseline["result"] != expected or homeostatic["result"] != expected:
            raise AssertionError("benchmark expected result mismatch")
        computed["case_count"] += 1
        computed["baseline_closed"] += baseline["result"] in {"SAT", "UNSAT"}
        computed["homeostatic_closed"] += homeostatic["result"] in {"SAT", "UNSAT"}
        computed["baseline_nodes"] += int(baseline["audit"]["node_count"])
        computed["homeostatic_nodes"] += int(homeostatic["audit"]["node_count"])
        computed["baseline_work"] += int(baseline["audit"]["work"]["total"])
        computed["homeostatic_work"] += int(homeostatic["audit"]["work"]["total"])
    if package.get("comparison") != computed:
        raise AssertionError("comparison mismatch")


def repaired(package: dict[str, Any]) -> dict[str, Any]:
    for case in package.get("cases", []):
        for run in (case.get("runs") or {}).values():
            run["semantic_digest"] = digest({k: v for k, v in run.items() if k != "semantic_digest"})
    package["semantic_digest"] = digest({k: v for k, v in package.items() if k != "semantic_digest"})
    return package


def tamper_self_test(package: dict[str, Any]) -> None:
    mutations = []

    a = copy.deepcopy(package)
    sat_run = next(
        case["runs"]["HOMEOSTATIC"] for case in a["cases"] if case["runs"]["HOMEOSTATIC"]["result"] == "SAT"
    )
    key = sorted(sat_run["witness"], key=int)[0]
    sat_run["witness"][key] = not sat_run["witness"][key]
    mutations.append(("witness", repaired(a)))

    b = copy.deepcopy(package)
    event = next(case["runs"]["HOMEOSTATIC"]["events"][0] for case in b["cases"] if case["runs"]["HOMEOSTATIC"]["events"])
    event["selected_node_id"] = 999999
    mutations.append(("scheduler", repaired(b)))

    c = copy.deepcopy(package)
    run = next(case["runs"]["BASELINE"] for case in c["cases"] if len(case["runs"]["BASELINE"]["nodes"]) > 1)
    child = run["nodes"][1]
    variable = next(iter(child["assignment"]))
    child["assignment"][variable] = not child["assignment"][variable]
    mutations.append(("node", repaired(c)))

    d = copy.deepcopy(package)
    d["cases"][0]["runs"]["HOMEOSTATIC"]["audit"]["work"]["total"] += 1
    mutations.append(("work", repaired(d)))

    for name, mutant in mutations:
        try:
            verify_package(mutant)
        except AssertionError:
            continue
        raise AssertionError(f"tamper class accepted: {name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--tamper-self-test", action="store_true")
    args = parser.parse_args()
    package = json.loads(args.artifact.read_text())
    verify_package(package)
    if args.tamper_self_test:
        tamper_self_test(package)
    print(
        json.dumps(
            {
                "verified": True,
                "tamper_self_test": bool(args.tamper_self_test),
                "comparison": package["comparison"],
                "semantic_digest": package["semantic_digest"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
