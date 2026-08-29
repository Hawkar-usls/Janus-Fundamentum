#!/usr/bin/env python3
"""Finite exact gate for the first operational successor move after L1/39100.

The admitted one-factor representation denotes

    U AND (P OR N)

with P and N conjunctions of committed clause atoms.  For a remaining root y,
this gate uses the exact identity

    EXISTS y [U AND (P OR N)]
      = EXISTS y [U AND P] OR EXISTS y [U AND N].

Each side is a flat CNF and is processed by the already admitted exact
resolution-product factor constructor when y occurs in both polarities.  There
is no positive-times-negative resolvent materialization and no Boolean extension
variable.  This is one local operational move only; nested closure, successor
totality, P2 and P vs NP remain OPEN.
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path
from typing import Any, Sequence

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.theorem_extraction import c025_adversarial_delta_pair_search as adv
from experiments.theorem_extraction import c025_exact_resolution_product_factor as factor

P_VS_NP = "OPEN"
OUT = Path("c025-successor-factor-or-lift-39100-gate.json")
TOP_OR_FIXED_UNITS = 32
EXPECTED_PRODUCT_FP = "037cbc224816408ca1c76c65c9bb78ad660d3b612c40ef91d1ac76943c7c79c3"
EXPECTED_N = 1102
EXPECTED_CAP = EXPECTED_N * EXPECTED_N


def as_cnf(rows: Sequence[Sequence[int]]) -> base.CNF:
    return tuple(tuple(int(lit) for lit in row) for row in rows)


def canonical_branch(rows: Sequence[base.Clause]) -> base.CNF:
    # This is intentionally the original exact canonicalizer.  v1 permits its
    # polynomial subset work; no resolvent cross-product is executed here.
    return base.canon_cnf(rows)


def drop_single_polarity(branch: base.CNF, pivot: int) -> base.CNF:
    has_pos = any(pivot in clause for clause in branch)
    has_neg = any(-pivot in clause for clause in branch)
    if has_pos and has_neg:
        raise ValueError("BOTH_POLARITIES_REQUIRE_FACTOR")
    if not has_pos and not has_neg:
        return branch
    satisfying = pivot if has_pos else -pivot
    # Existentially set the unique polarity to true.  Clauses containing it are
    # satisfied; all other clauses are untouched.
    return canonical_branch([clause for clause in branch if satisfying not in clause])


def branch_repr(branch: base.CNF, *, pivot: int, state_cap: int,
                roots: Sequence[int], subject: dict[str, Any], label: str) -> dict[str, Any]:
    has_pos = any(pivot in clause for clause in branch)
    has_neg = any(-pivot in clause for clause in branch)
    before_units = base.state_units(branch)
    if has_pos and has_neg:
        bundle = factor.construct_exact_resolution_product_factor(
            branch,
            pivot=pivot,
            state_cap=state_cap,
            root_variables=roots,
            subject={**subject, "or_lift_branch": label},
        )
        node = bundle["factor_node"]
        if any(abs(lit) == pivot for family in (
            node["unaffected_clauses"], node["positive_tail_family"], node["negative_tail_family"]
        ) for clause in family for lit in clause):
            raise AssertionError("TARGET_PIVOT_SURVIVED_CHILD_FACTOR")
        return {
            "kind": "EXACT_RESOLUTION_PRODUCT_FACTOR",
            "source_branch_units": before_units,
            "node": node,
            "certificate": bundle["certificate"],
            "resource_ledger": bundle["resource_ledger"],
        }
    reduced = drop_single_polarity(branch, pivot)
    if any(abs(lit) == pivot for clause in reduced for lit in clause):
        raise AssertionError("TARGET_PIVOT_SURVIVED_FLAT_BRANCH")
    return {
        "kind": "FLAT_CNF",
        "source_branch_units": before_units,
        "cnf": [list(c) for c in reduced],
        "state_units": base.state_units(reduced),
        "single_polarity_or_absent": True,
    }


def representation_structural_units(child: dict[str, Any]) -> int:
    if child["kind"] == "FLAT_CNF":
        return int(child["state_units"])
    return int(child["resource_ledger"]["combined_structural_units"])


def representation_bytes(child: dict[str, Any]) -> int:
    return len(factor.canonical_json_bytes(child))


def factor_or_lift(parent_bundle: dict[str, Any], *, pivot: int, state_cap: int,
                   remaining_roots: Sequence[int], subject: dict[str, Any]) -> dict[str, Any]:
    node = parent_bundle["factor_node"]
    if node.get("node_type") != "EXACT_RESOLUTION_PRODUCT_FACTOR":
        raise ValueError("PARENT_NOT_EXACT_RESOLUTION_PRODUCT_FACTOR")
    if pivot == int(node["pivot"]):
        raise ValueError("TARGET_EQUALS_REMOVED_PARENT_PIVOT")
    roots = tuple(sorted(set(int(v) for v in remaining_roots)))
    if tuple(remaining_roots) != roots or pivot not in roots:
        raise ValueError("REMAINING_ROOTS_NOT_CANONICAL_OR_TARGET_MISSING")

    U = as_cnf(node["unaffected_clauses"])
    P = as_cnf(node["positive_tail_family"])
    N = as_cnf(node["negative_tail_family"])

    # U AND (P OR N) == (U AND P) OR (U AND N).
    left_source = canonical_branch([*U, *P])
    right_source = canonical_branch([*U, *N])

    left = branch_repr(left_source, pivot=pivot, state_cap=state_cap,
                       roots=roots, subject=subject, label="U_AND_P")
    right = branch_repr(right_source, pivot=pivot, state_cap=state_cap,
                        roots=roots, subject=subject, label="U_AND_N")

    output_core = {
        "schema": "JANUS/C025/SUCCESSOR-FACTOR-OR-LIFT/NODE/v1",
        "node_type": "EXACT_FACTOR_OR_LIFT",
        "identity": "EXISTS_y[U_AND_(P_OR_N)]_EQUALS_EXISTS_y[U_AND_P]_OR_EXISTS_y[U_AND_N]",
        "parent_factor_fingerprint": node["factor_node_fingerprint"],
        "removed_pivot": pivot,
        "children": [left, right],
        "new_boolean_variables": 0,
        "subject": subject,
    }
    output_fp = factor.sha256_value(output_core)
    output = {**output_core, "node_fingerprint": output_fp}

    output_units = TOP_OR_FIXED_UNITS + sum(representation_structural_units(c) for c in (left, right))
    parent_units = int(parent_bundle["resource_ledger"]["combined_structural_units"])
    atomic_units = parent_units + output_units
    output_bytes = len(factor.canonical_json_bytes(output))
    child_bytes = sum(representation_bytes(c) for c in (left, right))
    avoided = sum(
        int(c.get("resource_ledger", {}).get("explicit_resolution_pairs_avoided", 0))
        for c in (left, right)
    )
    ledger = {
        "parent_combined_structural_units": parent_units,
        "left_branch_canonical_units": base.state_units(left_source),
        "right_branch_canonical_units": base.state_units(right_source),
        "output_structural_units": output_units,
        "atomic_parent_plus_output_units": atomic_units,
        "state_cap": state_cap,
        "output_under_cap": output_units <= state_cap,
        "atomic_parent_plus_output_under_cap": atomic_units <= state_cap,
        "output_serialized_bytes": output_bytes,
        "child_serialized_bytes_sum": child_bytes,
        "output_serialized_bytes_under_cap": output_bytes <= state_cap,
        "explicit_resolution_pairs_avoided_in_child_factors": avoided,
        "explicit_resolution_cross_product_materialized": False,
        "new_boolean_variables": 0,
        "progress_removed_root": pivot,
    }
    return {"output": output, "resource_ledger": ledger}


def clause_value(clause: Sequence[int], assignment: dict[int, bool]) -> bool:
    return any(assignment[abs(lit)] == (lit > 0) for lit in clause)


def cnf_value(cnf: Sequence[Sequence[int]], assignment: dict[int, bool]) -> bool:
    return all(clause_value(c, assignment) for c in cnf)


def factor_node_value(node: dict[str, Any], assignment: dict[int, bool]) -> bool:
    U = cnf_value(node["unaffected_clauses"], assignment)
    P = cnf_value(node["positive_tail_family"], assignment)
    N = cnf_value(node["negative_tail_family"], assignment)
    return U and (P or N)


def child_value(child: dict[str, Any], assignment: dict[int, bool]) -> bool:
    if child["kind"] == "FLAT_CNF":
        return cnf_value(child["cnf"], assignment)
    return factor_node_value(child["node"], assignment)


def lifted_value(lifted: dict[str, Any], assignment: dict[int, bool]) -> bool:
    return any(child_value(c, assignment) for c in lifted["output"]["children"])


def tiny_truth_table_regression() -> dict[str, Any]:
    source = base.canon_cnf([
        [1, 2, 3], [1, -2, 4], [-1, 2, 4], [-1, -2, 3],
        [2, 5], [-2, -5], [3, -4, 5]
    ])
    roots = tuple(base.vars_of(source))
    first = factor.construct_exact_resolution_product_factor(
        source, pivot=1, state_cap=100_000, root_variables=roots,
        subject={"gate": "TINY_TRUTH_TABLE"},
    )
    remaining = tuple(v for v in roots if v != 1)
    lifted = factor_or_lift(first, pivot=2, state_cap=100_000,
                            remaining_roots=remaining,
                            subject={"gate": "TINY_TRUTH_TABLE"})
    free_vars = [v for v in roots if v not in (1, 2)]
    checked = 0
    for bits in itertools.product((False, True), repeat=len(free_vars)):
        partial = dict(zip(free_vars, bits))
        explicit = False
        for x, y in itertools.product((False, True), repeat=2):
            a = {**partial, 1: x, 2: y}
            explicit = explicit or cnf_value(source, a)
        got = lifted_value(lifted, partial)
        if explicit != got:
            raise AssertionError(f"TINY_SEMANTIC_MISMATCH_{partial}_{explicit}_{got}")
        checked += 1
    return {"status": "PASS", "free_assignments_checked": checked}


def main() -> int:
    tiny = tiny_truth_table_regression()

    source, left_leaf, right_leaf = adv.build_selector_source(10, 90, 4, 39100)
    product = adv.direct_selector_product(left_leaf, right_leaf)
    N = base.input_size_units(source)
    if N != EXPECTED_N or N * N != EXPECTED_CAP:
        raise AssertionError("39100_N_OR_CAP_DRIFT")
    if base.fingerprint(product) != EXPECTED_PRODUCT_FP:
        raise AssertionError("39100_PRODUCT_FINGERPRINT_DRIFT")

    roots = tuple(base.vars_of(product))
    first = factor.construct_exact_resolution_product_factor(
        product,
        pivot=2,
        state_cap=EXPECTED_CAP,
        root_variables=roots,
        subject={"witness": 39100, "stage": "FIRST_FACTOR", "pivot": 2},
    )
    remaining = tuple(v for v in roots if v != 2)
    lifted = factor_or_lift(
        first,
        pivot=3,
        state_cap=EXPECTED_CAP,
        remaining_roots=remaining,
        subject={"witness": 39100, "stage": "SECOND_OPERATIONAL_MOVE", "pivot": 3},
    )

    ledger = lifted["resource_ledger"]
    children = lifted["output"]["children"]
    child_kinds = [c["kind"] for c in children]
    pivot_absent = all(
        all(abs(lit) != 3 for clause in (
            c["cnf"] if c["kind"] == "FLAT_CNF" else
            [*c["node"]["unaffected_clauses"], *c["node"]["positive_tail_family"], *c["node"]["negative_tail_family"]]
        ) for lit in clause)
        for c in children
    )
    if not pivot_absent:
        raise AssertionError("SECOND_PIVOT_SURVIVED")

    local_pass = bool(
        ledger["output_under_cap"] and
        ledger["atomic_parent_plus_output_under_cap"] and
        ledger["output_serialized_bytes_under_cap"] and
        not ledger["explicit_resolution_cross_product_materialized"] and
        pivot_absent
    )
    status = "ADMITTED_LOCAL_39100_SECOND_OPERATIONAL_MOVE" if local_pass else "LOCAL_39100_OPERATIONAL_MOVE_OVER_CAP_OR_INVALID"
    report = {
        "schema": "JANUS/C025/SUCCESSOR-FACTOR-OR-LIFT/39100-GATE/v1",
        "status": status,
        "P_VS_NP": P_VS_NP,
        "preregistration": "research/C025_SUCCESSOR_FACTOR_OR_LIFT_OPERATIONAL_GRAMMAR_V1_PREREGISTRATION_2026-08-29.json",
        "witness": {
            "seed": 39100,
            "N": N,
            "cap": EXPECTED_CAP,
            "product_fingerprint": base.fingerprint(product),
            "first_pivot": 2,
            "second_pivot": 3,
            "child_kinds": child_kinds,
            "second_pivot_absent_from_all_output_atoms": pivot_absent,
        },
        "tiny_independent_semantic_regression": tiny,
        "resource_ledger": ledger,
        "scientific_boundary": {
            "finite_local_operational_receipt_only": True,
            "nested_branch_growth_analyzed": False,
            "successor_nested_operational_closure": "OPEN",
            "successor_totality": "OPEN",
            "P2_REACHABLE_PRESERVATION": "OPEN",
            "ROOT_FREE_V3_TAIL": "OPEN",
            "P_VS_NP": P_VS_NP,
        },
        "next_gate": "FREEZE_NON_39100_REACHABLE_HOLDOUTS_AND_ATTACK_BRANCH_DAG_GROWTH" if local_pass else "REFINE_SUCCESSOR_OPERATION_WITHOUT_CHANGING_CAP_OR_REWRITING_FAILURE",
    }
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if local_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
