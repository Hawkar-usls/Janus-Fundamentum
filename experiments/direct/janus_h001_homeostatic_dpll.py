#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

SCHEMA = "JANUS-H001-HOMEOSTATIC-PROOF-SEARCH-v1"
TERMINAL = "P_VS_NP_OPEN"


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


@dataclass
class Ledger:
    counts: dict[str, int] = field(default_factory=dict)

    def charge(self, kind: str, amount: int = 1) -> None:
        if amount < 0:
            raise ValueError("negative work")
        self.counts[kind] = self.counts.get(kind, 0) + amount

    @property
    def total(self) -> int:
        return sum(self.counts.values())

    def snapshot(self) -> dict[str, Any]:
        return {"counts": dict(sorted(self.counts.items())), "total": self.total}


def validate_cnf(cnf: list[list[int]], nvars: int) -> None:
    if nvars < 0:
        raise ValueError("negative variable count")
    for clause in cnf:
        if not clause:
            continue
        seen: set[int] = set()
        for lit in clause:
            if lit == 0 or abs(lit) > nvars:
                raise ValueError("literal outside variable range")
            if lit in seen:
                raise ValueError("duplicate literal")
            seen.add(lit)


def literal_value(lit: int, assignment: dict[int, bool]) -> bool | None:
    var = abs(lit)
    if var not in assignment:
        return None
    value = assignment[var]
    return value if lit > 0 else not value


def clause_state(clause: list[int], assignment: dict[int, bool], ledger: Ledger) -> tuple[str, list[int]]:
    unassigned: list[int] = []
    for lit in clause:
        ledger.charge("LITERAL_EVALUATIONS")
        value = literal_value(lit, assignment)
        if value is True:
            return "SAT", []
        if value is None:
            unassigned.append(lit)
    if unassigned:
        return "OPEN", unassigned
    return "CONFLICT", []


def unit_propagate(
    cnf: list[list[int]],
    initial: dict[int, bool],
    ledger: Ledger,
) -> tuple[dict[int, bool], list[dict[str, Any]], str, int | None]:
    assignment = dict(initial)
    propagations: list[dict[str, Any]] = []
    while True:
        forced: tuple[int, bool, int] | None = None
        all_sat = True
        for clause_index, clause in enumerate(cnf):
            ledger.charge("CLAUSE_SCANS")
            state, unassigned = clause_state(clause, assignment, ledger)
            if state == "CONFLICT":
                return assignment, propagations, "CONFLICT", clause_index
            if state != "SAT":
                all_sat = False
            if state == "OPEN" and len(unassigned) == 1 and forced is None:
                lit = unassigned[0]
                forced = (abs(lit), lit > 0, clause_index)
        if all_sat:
            return assignment, propagations, "SAT", None
        if forced is None:
            return assignment, propagations, "OPEN", None
        var, value, clause_index = forced
        old = assignment.get(var)
        if old is not None and old != value:
            return assignment, propagations, "CONFLICT", clause_index
        if old is None:
            assignment[var] = value
            propagations.append({"variable": var, "value": value, "reason_clause": clause_index})
            ledger.charge("UNIT_PROPAGATIONS")


def unresolved_profile(
    cnf: list[list[int]], assignment: dict[int, bool], ledger: Ledger
) -> tuple[int, int, float, dict[int, int]]:
    unresolved = 0
    residual_literals = 0
    pressure = 0.0
    tight_occurrence: dict[int, int] = {}
    for clause in cnf:
        ledger.charge("PROFILE_CLAUSE_SCANS")
        state, unassigned = clause_state(clause, assignment, ledger)
        if state == "OPEN":
            unresolved += 1
            residual_literals += len(unassigned)
            pressure += 1.0 / max(1, len(unassigned))
            if len(unassigned) <= 3:
                for lit in unassigned:
                    var = abs(lit)
                    tight_occurrence[var] = tight_occurrence.get(var, 0) + 1
    return unresolved, residual_literals, pressure, tight_occurrence


def binary_entropy(p: float) -> float:
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return -(p * math.log2(p) + (1.0 - p) * math.log2(1.0 - p))


def branch_probe(
    cnf: list[list[int]], assignment: dict[int, bool], var: int, value: bool, ledger: Ledger
) -> dict[str, Any]:
    ledger.charge("BRANCH_PROBES")
    trial = dict(assignment)
    trial[var] = value
    propagated, steps, status, conflict_clause = unit_propagate(cnf, trial, ledger)
    unresolved, residual, pressure, _ = unresolved_profile(cnf, propagated, ledger)
    return {
        "value": value,
        "status": status,
        "conflict_clause": conflict_clause,
        "forced_count": len(steps),
        "assigned_count": len(propagated),
        "unresolved_clauses": unresolved,
        "residual_literals": residual,
        "pressure": round(pressure, 12),
    }


def probe_energy(probe: dict[str, Any], total_clauses: int) -> float:
    if probe["status"] == "CONFLICT":
        return float(total_clauses + 1)
    if probe["status"] == "SAT":
        return 0.0
    return float(probe["unresolved_clauses"]) + 0.01 * float(probe["residual_literals"])


def frontier_diversity(nodes: dict[int, dict[str, Any]], frontier: list[int], node_id: int, nvars: int) -> float:
    if len(frontier) <= 1 or nvars == 0:
        return 0.0
    target = {int(k): bool(v) for k, v in nodes[node_id]["assignment"].items()}
    distances: list[float] = []
    for other_id in frontier:
        if other_id == node_id:
            continue
        other = {int(k): bool(v) for k, v in nodes[other_id]["assignment"].items()}
        diff = 0
        compared = 0
        for var in range(1, nvars + 1):
            if var in target and var in other:
                compared += 1
                diff += target[var] != other[var]
            elif var in target or var in other:
                compared += 1
                diff += 1
        distances.append(diff / max(1, compared))
    return sum(distances) / max(1, len(distances))


def state_priority(
    node: dict[str, Any], nodes: dict[int, dict[str, Any]], frontier: list[int], nvars: int
) -> dict[str, Any]:
    diversity = frontier_diversity(nodes, frontier, int(node["node_id"]), nvars)
    unresolved = int(node["unresolved_clauses"])
    pressure = float(node["pressure"])
    depth = int(node["depth"])
    normalized_pressure = pressure / max(1.0, unresolved)
    score = normalized_pressure + 0.35 * diversity + 0.01 * depth
    return {
        "node_id": int(node["node_id"]),
        "score": round(score, 12),
        "normalized_pressure": round(normalized_pressure, 12),
        "diversity": round(diversity, 12),
        "depth": depth,
    }


def cheap_variable_rank(
    var: int,
    tight_occurrence: dict[int, int],
    conflict_activity: dict[int, int],
) -> tuple[int, int, int]:
    return (
        int(tight_occurrence.get(var, 0)),
        int(conflict_activity.get(var, 0)),
        -var,
    )


def choose_homeostatic_variable(
    cnf: list[list[int]],
    nvars: int,
    node: dict[str, Any],
    conflict_activity: dict[int, int],
    ledger: Ledger,
) -> tuple[int, dict[str, Any]]:
    assignment = {int(k): bool(v) for k, v in node["assignment"].items()}
    unassigned = [var for var in range(1, nvars + 1) if var not in assignment]
    if not unassigned:
        raise AssertionError("open node has no unassigned variable")
    _, _, pressure, tight_occurrence = unresolved_profile(cnf, assignment, ledger)
    stress = min(1.0, pressure / max(1.0, float(node["unresolved_clauses"])))
    probe_cap = min(len(unassigned), 1 + int(math.floor(2.0 * stress)))
    ranked = sorted(
        unassigned,
        key=lambda var: cheap_variable_rank(var, tight_occurrence, conflict_activity),
        reverse=True,
    )[:probe_cap]
    max_activity = max([conflict_activity.get(v, 0) for v in unassigned] + [1])
    max_tight = max([tight_occurrence.get(v, 0) for v in unassigned] + [1])
    evaluations: list[dict[str, Any]] = []
    for var in ranked:
        false_probe = branch_probe(cnf, assignment, var, False, ledger)
        true_probe = branch_probe(cnf, assignment, var, True, ledger)
        e0 = probe_energy(false_probe, len(cnf))
        e1 = probe_energy(true_probe, len(cnf))
        temperature = max(0.25, 1.0 - 0.5 * stress)
        z0 = math.exp(-e0 / max(1.0, len(cnf) * temperature))
        z1 = math.exp(-e1 / max(1.0, len(cnf) * temperature))
        p0 = z0 / (z0 + z1)
        entropy = binary_entropy(p0)
        contrast = abs(e0 - e1) / max(1.0, e0 + e1)
        activity = conflict_activity.get(var, 0) / max_activity
        tight = tight_occurrence.get(var, 0) / max_tight
        terminal_bonus = 1.0 if {false_probe["status"], true_probe["status"]} & {"SAT", "CONFLICT"} else 0.0
        score = entropy + 0.8 * contrast + 0.45 * activity + 0.35 * tight + 0.5 * terminal_bonus
        evaluations.append(
            {
                "variable": var,
                "score": round(score, 12),
                "entropy": round(entropy, 12),
                "contrast": round(contrast, 12),
                "activity": round(activity, 12),
                "tightness": round(tight, 12),
                "temperature": round(temperature, 12),
                "false_probe": false_probe,
                "true_probe": true_probe,
            }
        )
    evaluations.sort(key=lambda item: (-float(item["score"]), int(item["variable"])))
    selected = int(evaluations[0]["variable"])
    return selected, {
        "stress": round(stress, 12),
        "probe_cap": probe_cap,
        "candidate_variables": ranked,
        "evaluations": evaluations,
        "selected_variable": selected,
    }


def make_node(
    cnf: list[list[int]],
    nvars: int,
    node_id: int,
    parent_id: int | None,
    decision: dict[str, Any] | None,
    initial_assignment: dict[int, bool],
    depth: int,
    ledger: Ledger,
) -> dict[str, Any]:
    assignment, propagations, status, conflict_clause = unit_propagate(cnf, initial_assignment, ledger)
    unresolved, residual, pressure, _ = unresolved_profile(cnf, assignment, ledger)
    ledger.charge("NODES_CREATED")
    return {
        "node_id": node_id,
        "parent_id": parent_id,
        "decision": decision,
        "depth": depth,
        "input_assignment": {str(k): v for k, v in sorted(initial_assignment.items())},
        "assignment": {str(k): v for k, v in sorted(assignment.items())},
        "propagations": propagations,
        "status": status,
        "conflict_clause": conflict_clause,
        "unresolved_clauses": unresolved,
        "residual_literals": residual,
        "pressure": round(pressure, 12),
        "decision_variable": None,
        "children": [],
    }


def update_conflict_activity(cnf: list[list[int]], node: dict[str, Any], activity: dict[int, int]) -> None:
    if node["status"] != "CONFLICT":
        return
    index = node["conflict_clause"]
    if index is None:
        raise AssertionError("conflict lacks clause")
    for lit in cnf[int(index)]:
        var = abs(lit)
        activity[var] = activity.get(var, 0) + 1


def solve(
    cnf: list[list[int]],
    nvars: int,
    mode: str,
    max_nodes: int = 200000,
) -> dict[str, Any]:
    if mode not in {"BASELINE", "HOMEOSTATIC"}:
        raise ValueError("unknown mode")
    validate_cnf(cnf, nvars)
    ledger = Ledger()
    nodes: dict[int, dict[str, Any]] = {}
    root = make_node(cnf, nvars, 0, None, None, {}, 0, ledger)
    nodes[0] = root
    frontier: list[int] = []
    events: list[dict[str, Any]] = []
    conflict_activity: dict[int, int] = {}
    update_conflict_activity(cnf, root, conflict_activity)
    if root["status"] == "OPEN":
        frontier.append(0)
    terminal_node = 0 if root["status"] == "SAT" else None
    max_frontier = len(frontier)
    next_node_id = 1

    while frontier and terminal_node is None:
        if len(nodes) >= max_nodes:
            result = "OPEN_NODE_BUDGET"
            break
        frontier_before = list(frontier)
        if mode == "BASELINE":
            selected_id = min(frontier)
            node_priorities = []
        else:
            node_priorities = [state_priority(nodes[nid], nodes, frontier, nvars) for nid in frontier]
            node_priorities.sort(key=lambda item: (-float(item["score"]), int(item["node_id"])))
            selected_id = int(node_priorities[0]["node_id"])
            ledger.charge("STATE_PRIORITY_EVALUATIONS", len(frontier))
        frontier.remove(selected_id)
        node = nodes[selected_id]
        assignment = {int(k): bool(v) for k, v in node["assignment"].items()}
        if mode == "BASELINE":
            variable = min(var for var in range(1, nvars + 1) if var not in assignment)
            variable_receipt = {
                "selected_variable": variable,
                "rule": "MIN_UNASSIGNED",
            }
        else:
            variable, variable_receipt = choose_homeostatic_variable(
                cnf, nvars, node, conflict_activity, ledger
            )
        node["decision_variable"] = variable
        ledger.charge("NODE_EXPANSIONS")
        child_ids: list[int] = []
        for value in (False, True):
            child_assignment = dict(assignment)
            child_assignment[variable] = value
            child = make_node(
                cnf,
                nvars,
                next_node_id,
                selected_id,
                {"variable": variable, "value": value},
                child_assignment,
                int(node["depth"]) + 1,
                ledger,
            )
            nodes[next_node_id] = child
            child_ids.append(next_node_id)
            update_conflict_activity(cnf, child, conflict_activity)
            if child["status"] == "SAT" and terminal_node is None:
                terminal_node = next_node_id
            elif child["status"] == "OPEN":
                frontier.append(next_node_id)
            next_node_id += 1
        node["children"] = child_ids
        event = {
            "step": len(events),
            "frontier_before": frontier_before,
            "selected_node_id": selected_id,
            "node_priorities": node_priorities,
            "variable_receipt": variable_receipt,
            "child_ids": child_ids,
            "frontier_after": list(frontier),
            "conflict_activity_after": {str(k): v for k, v in sorted(conflict_activity.items())},
            "cumulative_work": ledger.total,
        }
        events.append(event)
        max_frontier = max(max_frontier, len(frontier))
    else:
        result = "SAT" if terminal_node is not None else "UNSAT"

    if terminal_node is not None:
        result = "SAT"
    elif not frontier:
        result = "UNSAT"
    witness = nodes[terminal_node]["assignment"] if terminal_node is not None else None
    artifact = {
        "mode": mode,
        "result": result,
        "nvars": nvars,
        "cnf": cnf,
        "cnf_digest": digest(cnf),
        "nodes": [nodes[index] for index in sorted(nodes)],
        "events": events,
        "terminal_node_id": terminal_node,
        "witness": witness,
        "remaining_frontier": list(frontier),
        "audit": {
            "node_count": len(nodes),
            "expansion_count": len(events),
            "conflict_count": sum(node["status"] == "CONFLICT" for node in nodes.values()),
            "max_frontier": max_frontier,
            "work": ledger.snapshot(),
        },
    }
    artifact["semantic_digest"] = digest({k: v for k, v in artifact.items() if k != "semantic_digest"})
    return artifact


def planted_3sat(nvars: int, clauses: int, seed: int) -> tuple[list[list[int]], dict[int, bool]]:
    rng = random.Random(seed)
    planted = {var: bool(rng.getrandbits(1)) for var in range(1, nvars + 1)}
    cnf: list[list[int]] = []
    seen: set[tuple[int, ...]] = set()
    while len(cnf) < clauses:
        vars_ = rng.sample(range(1, nvars + 1), 3)
        lits = [var if rng.getrandbits(1) else -var for var in vars_]
        if not any(literal_value(lit, planted) is True for lit in lits):
            pos = rng.randrange(3)
            var = abs(lits[pos])
            lits[pos] = var if planted[var] else -var
        clause = tuple(sorted(lits, key=lambda lit: (abs(lit), lit)))
        if clause in seen:
            continue
        seen.add(clause)
        cnf.append(list(clause))
    return cnf, planted


def pigeonhole(pigeons: int, holes: int) -> tuple[list[list[int]], int]:
    def var(p: int, h: int) -> int:
        return p * holes + h + 1

    cnf: list[list[int]] = []
    for p in range(pigeons):
        cnf.append([var(p, h) for h in range(holes)])
        for h1 in range(holes):
            for h2 in range(h1 + 1, holes):
                cnf.append([-var(p, h1), -var(p, h2)])
    for h in range(holes):
        for p1 in range(pigeons):
            for p2 in range(p1 + 1, pigeons):
                cnf.append([-var(p1, h), -var(p2, h)])
    return cnf, pigeons * holes


def contradiction_chain(length: int) -> tuple[list[list[int]], int]:
    # x1, (not xi or x{i+1}), and not x_length is unit-propagation UNSAT.
    cnf = [[1]]
    for var in range(1, length):
        cnf.append([-var, var + 1])
    cnf.append([-length])
    return cnf, length


def benchmark_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for seed in range(1, 21):
        cnf, planted = planted_3sat(14, 60, seed)
        cases.append(
            {
                "name": f"PLANTED_3SAT_14_60_SEED_{seed}",
                "nvars": 14,
                "cnf": cnf,
                "expected": "SAT",
                "planted_digest": digest(planted),
            }
        )
    for pigeons, holes in ((4, 3), (5, 4)):
        cnf, nvars = pigeonhole(pigeons, holes)
        cases.append(
            {
                "name": f"PIGEONHOLE_{pigeons}_{holes}",
                "nvars": nvars,
                "cnf": cnf,
                "expected": "UNSAT",
            }
        )
    cnf, nvars = contradiction_chain(20)
    cases.append({"name": "UNIT_CONTRADICTION_CHAIN_20", "nvars": nvars, "cnf": cnf, "expected": "UNSAT"})
    return cases


def build_package(max_nodes: int) -> dict[str, Any]:
    cases_out: list[dict[str, Any]] = []
    totals = {
        "BASELINE": {"nodes": 0, "work": 0, "closed": 0},
        "HOMEOSTATIC": {"nodes": 0, "work": 0, "closed": 0},
    }
    for case in benchmark_cases():
        runs = {}
        for mode in ("BASELINE", "HOMEOSTATIC"):
            run = solve(case["cnf"], case["nvars"], mode, max_nodes=max_nodes)
            runs[mode] = run
            totals[mode]["nodes"] += int(run["audit"]["node_count"])
            totals[mode]["work"] += int(run["audit"]["work"]["total"])
            totals[mode]["closed"] += run["result"] in {"SAT", "UNSAT"}
        cases_out.append(
            {
                "name": case["name"],
                "nvars": case["nvars"],
                "cnf": case["cnf"],
                "expected": case["expected"],
                "runs": runs,
            }
        )
    comparison = {
        "case_count": len(cases_out),
        "baseline_closed": totals["BASELINE"]["closed"],
        "homeostatic_closed": totals["HOMEOSTATIC"]["closed"],
        "baseline_nodes": totals["BASELINE"]["nodes"],
        "homeostatic_nodes": totals["HOMEOSTATIC"]["nodes"],
        "baseline_work": totals["BASELINE"]["work"],
        "homeostatic_work": totals["HOMEOSTATIC"]["work"],
    }
    package = {
        "schema": SCHEMA,
        "principle": {
            "persistent_hypotheses": "both decision children remain in the frontier; no branch is pruned heuristically",
            "cognitive_entropy": "binary Gibbs entropy of probed branch energies",
            "stress_allocation": "higher residual-clause pressure increases the number of variables probed",
            "rejected_hypotheses": "every conflict leaf updates a charged variable-activity map",
            "delayed_collapse": "selection order changes, exact branch coverage does not",
        },
        "cases": cases_out,
        "comparison": comparison,
        "strict_boundary": {
            "heuristic_component_novelty_claimed": False,
            "exactness_depends_on_independent_replay": True,
            "polynomial_worst_case_proved": False,
            "p_equals_np_claimed": False,
            "p_vs_np": "OPEN",
        },
    }
    package["semantic_digest"] = digest({k: v for k, v in package.items() if k != "semantic_digest"})
    return package


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-nodes", type=int, default=200000)
    args = parser.parse_args()
    package = build_package(args.max_nodes)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canonical_json(package) + b"\n")
    print(json.dumps(package["comparison"], indent=2, sort_keys=True))
    print("semantic_digest", package["semantic_digest"])


if __name__ == "__main__":
    main()
