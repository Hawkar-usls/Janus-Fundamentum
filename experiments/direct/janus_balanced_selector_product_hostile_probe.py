#!/usr/bin/env python3
"""Prestructured hostile probe aimed at an actual all-pivot cap failure.

Two disjoint deterministic random width-4 blocks are connected by one fresh
selector x:

  Sel_x(G,H) = AND_i (x OR G_i) AND_j (not x OR H_j).

Each leaf is selected by a *structural-only* balance rule fixed before JANUS is
run: 8 variables, 40 width-4 clauses, every variable occurs at least 6 times in
each polarity, and the primal graph is connected.  This prevents the sparse
leaf-variable escape that weakened the K5 selector product while using no solver
outcome to choose a specimen.

Eliminating x exactly materializes 40*40=1600 disjoint-support product clauses.
The frozen v0.4 core receives only the CNF, never the construction/family label.
After the core returns, exhaustive 8-variable leaf truth tables are allowed only
as an independent finite soundness label.  They have zero theorem authority.

P_VS_NP remains OPEN.
"""
from __future__ import annotations

import json
import random
from itertools import combinations, product

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_pirc_decision_core_v0_4 as core

P_VS_NP = "OPEN"
NVARS = 8
NCLAUSES = 40
WIDTH = 4
MIN_EACH_POLARITY = 6
LEFT_BASE_SEED = 6100
RIGHT_BASE_SEED = 7100
MAX_STRUCTURAL_SEED_SCAN = 10000


def primal_connected(cnf: base.CNF) -> bool:
    variables = base.vars_of(cnf)
    if not variables:
        return False
    adj = {v: set() for v in variables}
    for clause in cnf:
        scope = sorted({abs(lit) for lit in clause})
        for a, b in combinations(scope, 2):
            adj[a].add(b)
            adj[b].add(a)
    seen = {variables[0]}
    stack = [variables[0]]
    while stack:
        v = stack.pop()
        for w in adj[v]:
            if w not in seen:
                seen.add(w)
                stack.append(w)
    return len(seen) == len(variables)


def random_width4(seed: int) -> base.CNF:
    rng = random.Random(seed)
    rows = set()
    while len(rows) < NCLAUSES:
        support = sorted(rng.sample(range(1, NVARS + 1), WIDTH))
        clause = tuple(v if rng.getrandbits(1) else -v for v in support)
        canon = base.canon_clause(clause)
        if canon is not None:
            rows.add(canon)
    return base.canon_cnf(rows)


def polarity_profile(cnf: base.CNF) -> dict[int, tuple[int, int]]:
    profile = {}
    for v in base.vars_of(cnf):
        pos = sum(1 for clause in cnf if v in clause)
        neg = sum(1 for clause in cnf if -v in clause)
        profile[v] = (pos, neg)
    return profile


def structurally_balanced(cnf: base.CNF) -> bool:
    if len(cnf) != NCLAUSES or base.vars_of(cnf) != tuple(range(1, NVARS + 1)):
        return False
    if not primal_connected(cnf):
        return False
    return all(pos >= MIN_EACH_POLARITY and neg >= MIN_EACH_POLARITY
               for pos, neg in polarity_profile(cnf).values())


def first_structural_seed(base_seed: int) -> tuple[int, base.CNF]:
    for seed in range(base_seed, base_seed + MAX_STRUCTURAL_SEED_SCAN):
        cnf = random_width4(seed)
        if structurally_balanced(cnf):
            return seed, cnf
    raise RuntimeError("NO_STRUCTURALLY_BALANCED_LEAF_IN_FROZEN_SCAN")


def relabel(cnf: base.CNF, first_var: int) -> base.CNF:
    mapping = {v: first_var + v - 1 for v in range(1, NVARS + 1)}
    return base.canon_cnf(
        tuple(mapping[abs(lit)] if lit > 0 else -mapping[abs(lit)] for lit in clause)
        for clause in cnf
    )


def selector_product(left: base.CNF, right: base.CNF, selector: int = 1) -> base.CNF:
    if selector in base.vars_of(left) or selector in base.vars_of(right):
        raise ValueError("selector collision")
    if set(base.vars_of(left)) & set(base.vars_of(right)):
        raise ValueError("leaf variable sets must be disjoint")
    rows = [(selector, *clause) for clause in left]
    rows += [(-selector, *clause) for clause in right]
    return base.canon_cnf(rows)


def exact_leaf_truth(cnf: base.CNF) -> str:
    variables = base.vars_of(cnf)
    for bits in product((0, 1), repeat=len(variables)):
        if base.verify_total_assignment(cnf, dict(zip(variables, bits))):
            return "SAT"
    return "UNSAT"


def event_count(events: list[dict], kind: str) -> int:
    return sum(1 for e in events if e.get("kind") == kind)


def main() -> int:
    left_seed, left0 = first_structural_seed(LEFT_BASE_SEED)
    right_seed, right0 = first_structural_seed(RIGHT_BASE_SEED)
    left = relabel(left0, 2)
    right = relabel(right0, 2 + NVARS)
    source = selector_product(left, right, selector=1)

    # These are construction checks, not SAT-solving shortcuts.
    if base.vars_of(source) != tuple(range(1, 2 * NVARS + 2)):
        raise AssertionError("DENSE_SOURCE_ID_DRIFT")
    expected_N = base.input_size_units(source)
    if len(source) != 2 * NCLAUSES:
        raise AssertionError("SOURCE_CLAUSE_COUNT_DRIFT")

    result = core.solve_decision_core(source)
    events = result.get("events", [])

    # External labels are computed only now, after the theorem core returned.
    left_truth = exact_leaf_truth(left)
    right_truth = exact_leaf_truth(right)
    external_truth = "SAT" if "SAT" in {left_truth, right_truth} else "UNSAT"
    if result["status"] in {"SAT", "UNSAT"} and result["status"] != external_truth:
        raise AssertionError("FINITE_SOUNDNESS_FAILURE_ON_BALANCED_SELECTOR_PRODUCT")

    row = {
        "left_structural_seed": left_seed,
        "right_structural_seed": right_seed,
        "left_profile": {str(k): list(v) for k, v in polarity_profile(left0).items()},
        "right_profile": {str(k): list(v) for k, v in polarity_profile(right0).items()},
        "source_fingerprint": base.fingerprint(source),
        "source_variables": len(base.vars_of(source)),
        "source_clauses": len(source),
        "N": int(result["N"]),
        "expected_N": int(expected_N),
        "state_cap": int(result["state_cap"]),
        "status": result["status"],
        "reason": result["reason"],
        "missing_bridge": result.get("missing_bridge"),
        "max_state_units": int(result["ledger"]["max_state_units"]),
        "max_volume_ratio": int(result["ledger"]["max_state_units"]) / max(1, int(result["N"])),
        "ordinary_elimination_events": event_count(events, "AKINATOR_EXACT_ELIMINATION"),
        "v2_macro_rescue_events": event_count(events, "JEC_MACRO_RESTORE_CAP"),
        "v3_tail_rescue_events": event_count(events, "JEC_EXTENSION_TAIL_DESCENT_V3"),
        "extension_count": int(result["ledger"]["extension_count"]),
        "left_external_truth": left_truth,
        "right_external_truth": right_truth,
        "source_external_truth": external_truth,
        "external_truth_method": "EXHAUSTIVE_8_VARIABLE_LEAF_TABLES_AFTER_CORE_RETURN",
        "residual_units": int(result["residual_units"]),
        "residual_fingerprint": result["residual_fingerprint"],
    }
    report = {
        "schema": "JANUS/C025/BALANCED-SELECTOR-PRODUCT-HOSTILE-PROBE/v1",
        "status": "FINITE_OPEN_COUNTEREXAMPLE_FOUND" if result["status"] == "OPEN" else "FINITE_DECISIVE_RESULT",
        "decision_core": "PIRC_DECISION_CORE_V0_4",
        "structural_selection": {
            "nvars_per_leaf": NVARS,
            "clauses_per_leaf": NCLAUSES,
            "width": WIDTH,
            "minimum_each_polarity": MIN_EACH_POLARITY,
            "left_base_seed": LEFT_BASE_SEED,
            "right_base_seed": RIGHT_BASE_SEED,
            "max_seed_scan": MAX_STRUCTURAL_SEED_SCAN,
            "solver_outcome_used_in_selection": False,
        },
        "result": row,
        "scientific_boundary": {
            "single_frozen_structurally_selected_specimen": True,
            "family_label_not_supplied_to_decision_core": True,
            "leaf_truth_not_used_to_select_structural_seed": True,
            "external_truth_computed_only_after_core_return": True,
            "finite_decisive_result_is_not_totality_proof": True,
            "found_open_refutes_only_frozen_v0_4_totality": True,
            "HIGH_VOLUME_RESCUE_TOTALITY": "OPEN",
            "P_VS_NP": P_VS_NP,
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
