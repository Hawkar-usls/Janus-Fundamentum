#!/usr/bin/env python3
"""Structured hostile family for HIGH_VOLUME_RESCUE_TOTALITY.

Build a balanced selector OR-tree whose leaves are disjoint 4-colorability CNFs
for K5.  Each K5 leaf is UNSAT, hence every selector composition is UNSAT:

    Sel_x(G,H) = (x OR every clause of G) AND (not x OR every clause of H)

and existentially eliminating x materializes the exact distributive product
G OR H = AND_{i,j}(G_i OR H_j).  This deliberately targets the representation
product debt that v2/v3 are supposed to rescue, while the frozen JANUS decision
core receives only the resulting CNF and no graph/tree family label.

The mathematical UNSAT label is used only as external finite-specimen metadata;
it never participates in the decision core.  P_VS_NP remains OPEN.
"""
from __future__ import annotations

import argparse
import json

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_pirc_decision_core_v0_4 as core
from experiments.direct import janus_colorability_totality_hostile_probe as color

P_VS_NP = "OPEN"


def relabel(cnf: base.CNF, mapping: dict[int, int]) -> base.CNF:
    return base.canon_cnf(
        tuple(mapping[abs(lit)] if lit > 0 else -mapping[abs(lit)] for lit in clause)
        for clause in cnf
    )


def k5_leaf_with_first_var(first_var: int) -> tuple[base.CNF, int]:
    """Return one disjoint K5 4-coloring leaf using first_var..last inclusive."""
    if first_var < 1:
        raise ValueError("first_var must be positive")
    edges = tuple((u, v) for u in range(5) for v in range(u + 1, 5))
    raw = color.color_cnf(5, 4, edges)
    vars0 = base.vars_of(raw)
    mapping = {old: first_var + i for i, old in enumerate(vars0)}
    out = relabel(raw, mapping)
    last_var = first_var + len(vars0) - 1
    if base.vars_of(out) != tuple(range(first_var, last_var + 1)):
        raise AssertionError("K5_LEAF_DENSE_RANGE_DRIFT")
    return out, last_var


def selector_join(selector: int, left: base.CNF, right: base.CNF) -> base.CNF:
    if selector in base.vars_of(left) or selector in base.vars_of(right):
        raise ValueError("selector must be fresh")
    rows = []
    rows.extend((selector, *clause) for clause in left)
    rows.extend((-selector, *clause) for clause in right)
    return base.canon_cnf(rows)


def build_tree(depth: int) -> base.CNF:
    if depth < 1:
        raise ValueError("depth must be >=1")
    leaves = 1 << depth
    selectors = leaves - 1

    # Reserve 1..selectors exclusively for selector variables.  Leaf variables
    # start at selectors+1, so no hostile-generator collision is possible.
    next_var = selectors + 1
    nodes = []
    leaf_ranges = []
    for _ in range(leaves):
        leaf, last = k5_leaf_with_first_var(next_var)
        nodes.append(leaf)
        leaf_ranges.append((next_var, last))
        next_var = last + 1

    selector_set = set(range(1, selectors + 1))
    leaf_var_set = set()
    for first, last in leaf_ranges:
        leaf_var_set.update(range(first, last + 1))
    if selector_set & leaf_var_set:
        raise AssertionError("SELECTOR_LEAF_ID_COLLISION")

    # Allocate selector ids bottom-up in descending order: depth=2 uses 3,2 at
    # the lower joins and 1 at the root.  Thus the top selector remains variable
    # 1 under dense canonical ordering, which is frozen hostile-test structure.
    selector_ids = list(range(selectors, 0, -1))
    cursor = 0
    while len(nodes) > 1:
        joined = []
        for i in range(0, len(nodes), 2):
            sid = selector_ids[cursor]
            cursor += 1
            joined.append(selector_join(sid, nodes[i], nodes[i + 1]))
        nodes = joined

    root = nodes[0]
    used = set(base.vars_of(root))
    if cursor != selectors:
        raise AssertionError("SELECTOR_COUNT_DRIFT")
    if selector_ids[cursor - 1] != 1:
        raise AssertionError("ROOT_SELECTOR_ORDER_DRIFT")
    if not selector_set.issubset(used):
        raise AssertionError("SELECTOR_SET_DRIFT")
    if not leaf_var_set.issubset(used):
        raise AssertionError("LEAF_SET_DRIFT")
    if len(used) != selectors + 20 * leaves:
        raise AssertionError("TOTAL_VARIABLE_COUNT_DRIFT")
    return root


def count_kind(events: list[dict], kind: str) -> int:
    return sum(1 for event in events if event.get("kind") == kind)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-depth", type=int, default=2)
    args = parser.parse_args()

    rows = []
    first_open = None
    first_macro = None
    for depth in range(1, args.max_depth + 1):
        cnf = build_tree(depth)
        result = core.solve_decision_core(cnf)
        events = result.get("events", [])
        row = {
            "depth": depth,
            "leaf_count": 1 << depth,
            "source_fingerprint": base.fingerprint(cnf),
            "source_variables": len(base.vars_of(cnf)),
            "source_clauses": len(cnf),
            "N": int(result["N"]),
            "state_cap": int(result["state_cap"]),
            "status": result["status"],
            "reason": result["reason"],
            "known_external_truth": "UNSAT",
            "truth_reason": "EVERY_K5_4_COLORING_LEAF_IS_UNSAT_AND_SELECTOR_JOIN_IS_SAT_IFF_LEFT_OR_RIGHT_IS_SAT",
            "max_state_units": int(result["ledger"]["max_state_units"]),
            "max_volume_ratio": int(result["ledger"]["max_state_units"]) / max(1, int(result["N"])),
            "ordinary_elimination_events": count_kind(events, "AKINATOR_EXACT_ELIMINATION"),
            "v2_macro_rescue_events": count_kind(events, "JEC_MACRO_RESTORE_CAP"),
            "v3_tail_rescue_events": count_kind(events, "JEC_EXTENSION_TAIL_DESCENT_V3"),
            "extension_count": int(result["ledger"]["extension_count"]),
            "missing_bridge": result.get("missing_bridge"),
            "residual_fingerprint": result["residual_fingerprint"],
            "residual_units": int(result["residual_units"]),
        }
        rows.append(row)
        if first_macro is None and (row["v2_macro_rescue_events"] + row["v3_tail_rescue_events"] > 0):
            first_macro = dict(row)
        if result["status"] == "OPEN":
            first_open = dict(row)
            break

    report = {
        "schema": "JANUS/C025/SELECTOR-PRODUCT-TOWER-HOSTILE-PROBE/v1",
        "status": "FINITE_OPEN_COUNTEREXAMPLE_FOUND" if first_open else "NO_OPEN_IN_EXECUTED_SELECTOR_TOWER_DEPTHS",
        "decision_core": "PIRC_DECISION_CORE_V0_4",
        "rows": rows,
        "first_macro_rescue": first_macro,
        "first_open": first_open,
        "scientific_boundary": {
            "structured_finite_hostile_family_only": True,
            "family_label_not_supplied_to_decision_core": True,
            "selector_product_targets_known_representation_debt": True,
            "known_truth_not_used_by_decision_core": True,
            "absence_of_open_is_not_totality_proof": True,
            "found_open_refutes_only_v0_4_totality": True,
            "HIGH_VOLUME_RESCUE_TOTALITY": "OPEN",
            "P_VS_NP": P_VS_NP,
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
