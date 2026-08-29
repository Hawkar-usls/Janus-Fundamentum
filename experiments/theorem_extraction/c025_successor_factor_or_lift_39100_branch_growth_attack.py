#!/usr/bin/env python3
"""Attack naive recursive FACTOR_OR_LIFT branch growth on frozen witness 39100.

This script does not invent a new compression rule.  It composes only the
preregistered local OR-lift move in canonical root order and stops at the first
unchanged-N^2 resource crossing.  A crossing refutes only this naive recursive
successor envelope on this finite witness.  P2 and P vs NP remain OPEN.
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path
from typing import Any, Sequence

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.theorem_extraction import c025_adversarial_delta_pair_search as adv
from experiments.theorem_extraction import c025_exact_resolution_product_factor as factor
from experiments.theorem_extraction import c025_successor_factor_or_lift_39100_gate as lift

P_VS_NP = "OPEN"
OUT = Path("c025-successor-factor-or-lift-39100-branch-growth-attack.json")
EXPECTED_FP = "037cbc224816408ca1c76c65c9bb78ad660d3b612c40ef91d1ac76943c7c79c3"
N = 1102
CAP = N * N
PIVOTS = [2, 3, 4, 5, 6, 7, 8]
TOP_OR_FIXED_UNITS = 32


def factor_child_from_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    return {
        "kind": "EXACT_RESOLUTION_PRODUCT_FACTOR",
        "source_branch_units": int(bundle["factor_node"]["source_state_units"]),
        "node": bundle["factor_node"],
        "certificate": bundle["certificate"],
        "resource_ledger": bundle["resource_ledger"],
    }


def child_to_parent_bundle(child: dict[str, Any]) -> dict[str, Any]:
    if child["kind"] != "EXACT_RESOLUTION_PRODUCT_FACTOR":
        raise ValueError("CHILD_NOT_FACTOR")
    return {
        "factor_node": child["node"],
        "certificate": child["certificate"],
        "resource_ledger": child["resource_ledger"],
    }


def child_atoms(child: dict[str, Any]) -> list[list[int]]:
    if child["kind"] == "FLAT_CNF":
        return child["cnf"]
    node = child["node"]
    return [
        *node["unaffected_clauses"],
        *node["positive_tail_family"],
        *node["negative_tail_family"],
    ]


def target_absent(children: Sequence[dict[str, Any]], pivot: int) -> bool:
    return all(abs(lit) != pivot for child in children for clause in child_atoms(child) for lit in clause)


def forest_structural_units(children: Sequence[dict[str, Any]]) -> int:
    return TOP_OR_FIXED_UNITS + sum(lift.representation_structural_units(c) for c in children)


def forest_bytes(children: Sequence[dict[str, Any]]) -> int:
    doc = {
        "schema": "JANUS/C025/SUCCESSOR-FACTOR-OR-LIFT/OR-FOREST/v1",
        "children": list(children),
    }
    return len(factor.canonical_json_bytes(doc))


def eliminate_child(child: dict[str, Any], *, pivot: int, roots: Sequence[int], subject: dict[str, Any]) -> list[dict[str, Any]]:
    if child["kind"] == "EXACT_RESOLUTION_PRODUCT_FACTOR":
        out = lift.factor_or_lift(
            child_to_parent_bundle(child),
            pivot=pivot,
            state_cap=CAP,
            remaining_roots=roots,
            subject=subject,
        )
        return list(out["output"]["children"])
    branch = tuple(tuple(int(lit) for lit in clause) for clause in child["cnf"])
    return [lift.branch_repr(
        branch,
        pivot=pivot,
        state_cap=CAP,
        roots=roots,
        subject=subject,
        label="FLAT_OR_CHILD",
    )]


def eliminate_forest(children: Sequence[dict[str, Any]], *, pivot: int,
                     roots: Sequence[int], subject: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for index, child in enumerate(children):
        out.extend(eliminate_child(
            child,
            pivot=pivot,
            roots=roots,
            subject={**subject, "parent_child_index": index},
        ))
    if not target_absent(out, pivot):
        raise AssertionError(f"PIVOT_{pivot}_SURVIVED_FOREST")
    return out


def forest_value(children: Sequence[dict[str, Any]], assignment: dict[int, bool]) -> bool:
    return any(lift.child_value(child, assignment) for child in children)


def tiny_recursive_regression() -> dict[str, Any]:
    source = base.canon_cnf([
        [1, 2, 3, 4], [1, -2, 3, -4], [-1, 2, -3, 4], [-1, -2, -3, -4],
        [2, 3, 5], [-2, -3, 5], [3, -4, 6], [-3, 4, -6]
    ])
    roots = tuple(base.vars_of(source))
    first = factor.construct_exact_resolution_product_factor(
        source, pivot=1, state_cap=100_000, root_variables=roots,
        subject={"gate": "TINY_RECURSIVE"},
    )
    children = [factor_child_from_bundle(first)]
    current_roots = tuple(v for v in roots if v != 1)
    for pivot in (2, 3):
        children = eliminate_forest(
            children, pivot=pivot, roots=current_roots,
            subject={"gate": "TINY_RECURSIVE", "pivot": pivot},
        )
        current_roots = tuple(v for v in current_roots if v != pivot)
    free_vars = [v for v in roots if v not in (1, 2, 3)]
    checked = 0
    for bits in itertools.product((False, True), repeat=len(free_vars)):
        partial = dict(zip(free_vars, bits))
        explicit = False
        for values in itertools.product((False, True), repeat=3):
            a = {**partial, 1: values[0], 2: values[1], 3: values[2]}
            explicit = explicit or lift.cnf_value(source, a)
        got = forest_value(children, partial)
        if explicit != got:
            raise AssertionError(f"TINY_RECURSIVE_MISMATCH_{partial}_{explicit}_{got}")
        checked += 1
    return {"status": "PASS", "free_assignments_checked": checked, "final_children": len(children)}


def count_kinds(children: Sequence[dict[str, Any]]) -> dict[str, int]:
    return {
        "factor": sum(c["kind"] == "EXACT_RESOLUTION_PRODUCT_FACTOR" for c in children),
        "flat": sum(c["kind"] == "FLAT_CNF" for c in children),
    }


def avoided_pairs(children: Sequence[dict[str, Any]]) -> int:
    return sum(int(c.get("resource_ledger", {}).get("explicit_resolution_pairs_avoided", 0)) for c in children)


def main() -> int:
    tiny = tiny_recursive_regression()
    source, left_leaf, right_leaf = adv.build_selector_source(10, 90, 4, 39100)
    product = adv.direct_selector_product(left_leaf, right_leaf)
    if base.input_size_units(source) != N or base.fingerprint(product) != EXPECTED_FP:
        raise AssertionError("39100_IDENTITY_DRIFT")
    roots = tuple(base.vars_of(product))

    first = factor.construct_exact_resolution_product_factor(
        product, pivot=2, state_cap=CAP, root_variables=roots,
        subject={"witness": 39100, "attack": "BRANCH_GROWTH", "pivot": 2},
    )
    children: list[dict[str, Any]] = [factor_child_from_bundle(first)]
    current_roots = tuple(v for v in roots if v != 2)
    previous_units = int(first["resource_ledger"]["combined_structural_units"])
    rows = [{
        "removed_pivot": 2,
        "child_count": 1,
        **count_kinds(children),
        "structural_units": previous_units,
        "serialized_bytes": forest_bytes(children),
        "atomic_previous_plus_next_units": int(first["resource_ledger"]["input_state_units"]) + previous_units,
        "under_cap": bool(first["resource_ledger"]["atomic_source_plus_factor_under_cap"]),
        "explicit_resolution_pairs_avoided": int(first["resource_ledger"]["explicit_resolution_pairs_avoided"]),
    }]

    crossing = None
    for pivot in PIVOTS[1:]:
        next_children = eliminate_forest(
            children,
            pivot=pivot,
            roots=current_roots,
            subject={"witness": 39100, "attack": "BRANCH_GROWTH", "pivot": pivot},
        )
        units = forest_structural_units(next_children)
        serialized = forest_bytes(next_children)
        atomic = previous_units + units
        kinds = count_kinds(next_children)
        row = {
            "removed_pivot": pivot,
            "child_count": len(next_children),
            **kinds,
            "structural_units": units,
            "serialized_bytes": serialized,
            "atomic_previous_plus_next_units": atomic,
            "structural_under_cap": units <= CAP,
            "serialized_under_cap": serialized <= CAP,
            "atomic_under_cap": atomic <= CAP,
            "under_cap": units <= CAP and serialized <= CAP and atomic <= CAP,
            "target_absent": target_absent(next_children, pivot),
            "explicit_resolution_pairs_avoided": avoided_pairs(next_children),
        }
        rows.append(row)
        if not row["under_cap"]:
            crossing = row
            break
        children = next_children
        previous_units = units
        current_roots = tuple(v for v in current_roots if v != pivot)

    if crossing is not None:
        status = "NAIVE_RECURSIVE_FACTOR_OR_LIFT_REFUTED_BY_39100_RESOURCE_CROSSING"
        verdict = "REFUTED_ON_39100"
        next_gate = "DESIGN_SHARED_OR_FOREST_FACTORIZATION_WITHOUT_CHANGING_CAP__PRESERVE_THIS_FAILURE"
    else:
        status = "NO_CROSSING_THROUGH_FROZEN_PIVOT_SCHEDULE__FINITE_ONLY"
        verdict = "NOT_REFUTED_IN_THIS_FINITE_SCHEDULE__NOT_PROVED"
        next_gate = "FREEZE_NON_39100_REACHABLE_HOLDOUTS_AND_CONTINUE_NESTED_ATTACK"

    report = {
        "schema": "JANUS/C025/SUCCESSOR-FACTOR-OR-LIFT/39100-BRANCH-GROWTH-ATTACK-RESULT/v1",
        "status": status,
        "P_VS_NP": P_VS_NP,
        "preregistration": "research/C025_SUCCESSOR_FACTOR_OR_LIFT_39100_BRANCH_GROWTH_ATTACK_PREREGISTRATION_2026-08-29.json",
        "witness": {"seed": 39100, "N": N, "cap": CAP, "product_fingerprint": EXPECTED_FP},
        "tiny_recursive_semantic_regression": tiny,
        "rows": rows,
        "first_crossing": crossing,
        "candidate_verdict": {
            "NAIVE_RECURSIVE_FACTOR_OR_LIFT_N2_ENVELOPE": verdict,
            "SUCCESSOR_NESTED_OPERATIONAL_CLOSURE": "OPEN",
            "SUCCESSOR_TOTALITY": "OPEN",
            "P2_REACHABLE_PRESERVATION": "OPEN",
            "P_VS_NP": "OPEN"
        },
        "scientific_boundary": {
            "crossing_if_present_refutes_only_naive_recursive_OR_lift": True,
            "local_2_to_3_pass_remains_immutable": True,
            "no_cap_change": True,
            "no_posthoc_branch_merge": True,
            "finite_survival_is_not_totality": True
        },
        "next_gate": next_gate,
    }
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
