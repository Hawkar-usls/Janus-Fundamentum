#!/usr/bin/env python3
"""Strict preregistration-conformant runner for S𓂸ḥ gate-0.

The first implementation module is retained for audit.  This runner changes only
one implementation detail required by the already-frozen contract: every verified
size-1 separator evaluates BOTH False/True boundary valuations, and every claimed
component in each valuation is solved before branch closure.  No gate, budget,
fixture, threshold, or success criterion is changed.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import s_phallus_h_gate_0_articulation_decomposition as gate
from janus_c025_core import CNF, canonical_cnf, cnf_hash, cofactor, satisfies, variables


def strict_solve_recursive(formula: CNF, budget: int, base_engine, depth: int, counters: dict[str, Any]) -> dict[str, Any]:
    formula = canonical_cnf(formula)
    counters["recursive_component_calls"] += 1
    counters["max_recursion_depth"] = max(counters["max_recursion_depth"], depth)
    formula_hash = cnf_hash(formula)
    if depth > gate.MAX_DEPTH:
        return {"status": "UNKNOWN_BUDGET", "assignment": None, "tree": {"kind": "DEPTH_LIMIT", "formula_hash": formula_hash}}
    if not formula:
        return {"status": "SAT", "assignment": {}, "tree": {"kind": "EMPTY_SAT", "formula_hash": formula_hash}}
    if () in formula:
        return {"status": "UNSAT", "assignment": None, "tree": {"kind": "EMPTY_CLAUSE_UNSAT", "formula_hash": formula_hash}}

    residual, unit_assignment, unit_trail = gate.v2.unit_propagate(formula)
    counters["unit_propagations"] += len(unit_trail)
    residual = canonical_cnf(residual)
    if not residual:
        full = {v: False for v in variables(formula)}
        full.update(unit_assignment)
        ok = satisfies(formula, full)
        return {"status": "SAT" if ok else "UNKNOWN_BUDGET", "assignment": full if ok else None,
                "tree": {"kind": "UNIT_SAT", "formula_hash": formula_hash, "trail_digest": gate.digest(unit_trail), "verified": ok}}
    if () in residual:
        return {"status": "UNSAT", "assignment": None,
                "tree": {"kind": "UNIT_UNSAT", "formula_hash": formula_hash, "trail_digest": gate.digest(unit_trail)}}

    q0 = gate.v21.detect_pair_product(residual)
    counters["q0_detector_calls"] += 1
    if q0["matched"]:
        counters["q0_leaf_hits"] += 1
        assignment = {v: False for v in variables(formula)}
        assignment.update(unit_assignment)
        assignment.update(q0["assignment"] or {})
        ok = satisfies(formula, assignment)
        counters["q0_symbolic_states"] += int(q0["metrics"]["symbolic_states"])
        counters["q0_symbolic_transitions"] += int(q0["metrics"]["symbolic_transitions"])
        return {
            "status": "SAT" if ok else "UNKNOWN_BUDGET", "assignment": assignment if ok else None,
            "tree": {"kind": "Q0_PAIR_PRODUCT", "formula_hash": formula_hash,
                     "residual_hash": cnf_hash(residual), "certificate": q0["certificate_sha256"],
                     "symbolic_states": q0["metrics"]["symbolic_states"], "verified": ok},
        }

    detection = gate.detect_articulation(residual)
    counters["s_detector_calls"] += 1
    for key, value in detection.get("metrics", {}).items():
        if isinstance(value, int):
            counters["discovery_cost"][key] = counters["discovery_cost"].get(key, 0) + value

    if detection["matched"]:
        counters["separator_nodes"] += 1
        separator = int(detection["separator"])
        branch_rows = []
        sat_candidates: list[dict[int, bool]] = []

        # Frozen contract: EXACTLY BOTH boundary valuations, no early SAT exit.
        for value in (False, True):
            counters["boundary_valuations"] += 1
            restricted = canonical_cnf(cofactor(residual, separator, value))
            comps = gate.component_formulas(restricted)
            counters["component_partitions"] += len(comps)
            component_rows = []
            branch_assignment = {separator: value}
            branch_status = "SAT"

            # Frozen contract: solve EVERY claimed component before branch closure.
            for comp in comps:
                solved = strict_solve_recursive(comp, budget, base_engine, depth + 1, counters)
                component_rows.append({"formula_hash": cnf_hash(comp), "status": solved["status"], "tree": solved["tree"]})
                if solved["status"] == "UNSAT":
                    branch_status = "UNSAT"
                elif solved["status"] == "UNKNOWN_BUDGET" and branch_status != "UNSAT":
                    branch_status = "UNKNOWN_BUDGET"
                elif solved["status"] == "SAT" and solved["assignment"]:
                    branch_assignment.update(solved["assignment"])

            if branch_status == "SAT":
                full = {v: False for v in variables(formula)}
                full.update(unit_assignment)
                full.update(branch_assignment)
                verified = satisfies(formula, full)
                if verified:
                    sat_candidates.append(full)
                else:
                    branch_status = "UNKNOWN_BUDGET"
            branch_rows.append({"separator_value": value, "status": branch_status, "components": component_rows})

        tree_core = {
            "kind": "S_ARTICULATION", "formula_hash": formula_hash, "residual_hash": cnf_hash(residual),
            "separator": separator, "separator_certificate": detection["certificate_sha256"],
            "claimed_components": detection["components"], "branches": branch_rows,
        }
        tree_core["tree_sha256"] = gate.digest(tree_core)
        if sat_candidates:
            # Deterministic False-before-True boundary preference after BOTH were evaluated.
            return {"status": "SAT", "assignment": sat_candidates[0], "tree": tree_core}
        if len(branch_rows) == 2 and all(row["status"] == "UNSAT" for row in branch_rows):
            return {"status": "UNSAT", "assignment": None, "tree": tree_core}
        return {"status": "UNKNOWN_BUDGET", "assignment": None, "tree": tree_core}

    counters["generic_leaf_calls"] += 1
    order, _ = gate.v2.activity_order(residual)
    engine = base_engine(formula, residual, order, unit_assignment, budget)
    gate.add_engine_stats(counters, engine["stats"])
    return {
        "status": engine["status"], "assignment": engine.get("assignment"),
        "tree": {"kind": "GENERIC_LEAF", "formula_hash": formula_hash, "residual_hash": cnf_hash(residual),
                 "status": engine["status"], "root": engine.get("root"),
                 "engine_projection_sha256": gate.digest(gate.v2.engine_projection(engine))},
    }


def run() -> dict[str, Any]:
    # Runtime monkeypatch is deliberately local to this audit runner. All callers in
    # the imported gate module resolve its global solve_recursive dynamically.
    gate.solve_recursive = strict_solve_recursive
    result = gate.run()
    result["implementation_conformance"] = {
        "both_boundary_valuations_mandatory": True,
        "all_claimed_components_solved_per_boundary": True,
        "frozen_contract_unchanged": True,
    }
    # Recompute integrity because the conformance record is part of this final result.
    result.pop("integrity_sha256", None)
    result["integrity_sha256"] = gate.digest(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    result = run()
    text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    if args.self_test and not result["status"].startswith("PASS_KEEP"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
