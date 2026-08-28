#!/usr/bin/env python3
"""Bounded exact falsifier for the C025 root-phase polynomial pivot grammar.

This is NOT a theorem prover.  It instruments the already-frozen deterministic
PIRC_DECISION_CORE_V0_4 without changing any transition return value.

At the exact call site where ordinary capped elimination is attempted, it freezes
reachable root-phase states for which *every* canonical ordinary pivot overflows
the original root-relative N^2 cap.  It then observes the unmodified frozen v2
macro discovery result on the same state.

Three candidate statements are attacked:

  L1  : ordinary exact pivot OR exact v2 root rescue always exists in root phase.
  L1A : all-pivot overflow forces the proved frequent-pair threshold.
  L1B : all-pivot overflow forces the stronger pair-density threshold.

Finding a reachable witness refutes the corresponding candidate.  Failing to
find one in this bounded search proves nothing.  P_VS_NP remains OPEN.
"""
from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from copy import deepcopy
from math import comb
from typing import Iterable

from experiments.direct import janus_pirc_decision_core_v0_4 as core
from experiments.direct import janus_unified_proof_carrying_akinator_jec as base

P_VS_NP = "OPEN"


def pair_stats(cnf: base.CNF) -> tuple[int, int, tuple[int, int] | None]:
    freq: Counter[tuple[int, int]] = Counter()
    incidences = 0
    for clause in cnf:
        incidences += comb(len(clause), 2)
        for i in range(len(clause)):
            for j in range(i + 1, len(clause)):
                a, b = clause[i], clause[j]
                if abs(a) == abs(b):
                    continue
                pair = tuple(sorted((a, b), key=lambda z: (abs(z), z < 0)))
                freq[pair] += 1
    if not freq:
        return incidences, 0, None
    pair, count = min(
        freq.items(),
        key=lambda kv: (-kv[1], tuple((abs(z), z < 0) for z in kv[0])),
    )
    return incidences, count, pair


def random_width_cnf(nvars: int, nclauses: int, width: int, seed: int) -> base.CNF:
    if width > nvars:
        raise ValueError("width exceeds variable count")
    rng = random.Random(seed)
    rows: set[base.Clause] = set()
    attempts = 0
    while len(rows) < nclauses:
        attempts += 1
        if attempts > 500000:
            raise RuntimeError("CLAUSE_GENERATION_EXHAUSTED")
        support = sorted(rng.sample(range(1, nvars + 1), width))
        clause = tuple(v if rng.getrandbits(1) else -v for v in support)
        cc = base.canon_clause(clause)
        if cc is not None:
            rows.add(cc)
    return base.canon_cnf(rows)


def relabel(cnf: base.CNF, mapping: dict[int, int]) -> base.CNF:
    return base.canon_cnf(
        tuple(mapping[abs(l)] if l > 0 else -mapping[abs(l)] for l in clause)
        for clause in cnf
    )


def selector_product_case(
    leaf_nvars: int,
    leaf_clauses: int,
    width: int,
    seed: int,
) -> base.CNF:
    left0 = random_width_cnf(leaf_nvars, leaf_clauses, width, seed)
    right0 = random_width_cnf(leaf_nvars, leaf_clauses, width, seed + 1000003)
    left_map = {v: 1 + v for v in range(1, leaf_nvars + 1)}
    right_map = {v: 1 + leaf_nvars + v for v in range(1, leaf_nvars + 1)}
    left = relabel(left0, left_map)
    right = relabel(right0, right_map)
    rows: list[Iterable[int]] = [(1, *c) for c in left]
    rows.extend((-1, *c) for c in right)
    return base.canon_cnf(rows)


def public_observation(row: dict) -> dict:
    return {k: deepcopy(v) for k, v in row.items() if not k.startswith("_")}


def witness_from(row: dict | None) -> dict | None:
    if row is None:
        return None
    out = public_observation(row)
    out["normalized_root_cnf"] = [list(c) for c in row["_root_cnf"]]
    out["reachable_state_cnf"] = [list(c) for c in row["_state_cnf"]]
    out["event_prefix"] = deepcopy(row["_event_prefix"])
    return out


def choose_min(rows: list[dict], predicate) -> dict | None:
    hits = [r for r in rows if predicate(r)]
    if not hits:
        return None
    return min(
        hits,
        key=lambda r: (
            int(r["state_units"]),
            int(r["live_variables"]),
            int(r["root_variables_live"]),
            r["reachable_state_fingerprint"],
        ),
    )


def run_case(cnf: base.CNF, meta: dict, observations: list[dict]) -> dict:
    original_first = base.first_capped_elimination
    original_v2 = core.v2.discover_macro_restore_v2
    pending: dict[str, list[dict]] = {}

    def wrapped_first(state: base.EngineState, cnf_arg=None, roots_only: bool = False):
        result = original_first(state, cnf_arg, roots_only)
        # Only the theorem core's ordinary transition on the live residual.
        # Calls from inside v2 pass an explicit macro CNF and roots_only=True.
        if cnf_arg is None and not roots_only and result is None:
            live = set(base.vars_of(state.residual))
            roots_live = sorted(v for v in state.root_vars if v in live)
            if roots_live:
                s = base.state_units(state.residual)
                n = len(live)
                P, tmax, pair = pair_stats(state.residual)
                frequent_threshold = s - 2 * state.N + 11
                density_threshold = 2 * n * (n - 1) * frequent_threshold if n >= 2 else 0
                fp = base.fingerprint(state.residual)
                row = {
                    "source_case": deepcopy(meta),
                    "normalized_root_fingerprint": base.fingerprint(state.root),
                    "reachable_state_fingerprint": fp,
                    "N": int(state.N),
                    "state_cap": int(state.state_cap),
                    "state_units": int(s),
                    "volume_ratio_to_N": s / max(1, state.N),
                    "live_variables": n,
                    "root_variables_live": len(roots_live),
                    "all_ordinary_pivots_overflow": True,
                    "pair_incidences_P": int(P),
                    "max_pair_frequency": int(tmax),
                    "max_pair": list(pair) if pair is not None else None,
                    "frequent_pair_threshold": int(frequent_threshold),
                    "pair_density_threshold": int(density_threshold),
                    "L1A_frequent_pair_forced": bool(tmax >= frequent_threshold),
                    "L1B_pair_density_forced": bool(P >= density_threshold),
                    "v2_rescue_exists": None,
                    "v2_rescue": None,
                    "_root_cnf": state.root,
                    "_state_cnf": state.residual,
                    "_event_prefix": deepcopy(state.ledger.events),
                }
                observations.append(row)
                pending.setdefault(fp, []).append(row)
        return result

    def wrapped_v2(state: base.EngineState):
        fp = base.fingerprint(state.residual)
        result = original_v2(state)
        for row in pending.get(fp, []):
            row["v2_rescue_exists"] = result is not None
            if result is not None:
                macro_cnf, pivot, after, macro_cert, elim_stats = result
                row["v2_rescue"] = {
                    "pair": list(macro_cert.get("represents", [])),
                    "reused_occurrences": macro_cert.get("reused_occurrences"),
                    "root_pivot": int(pivot),
                    "macro_state_units": base.state_units(macro_cnf),
                    "after_state_units": base.state_units(after),
                    "after_fingerprint": base.fingerprint(after),
                    "elimination_raw_units": int(elim_stats.get("raw_units", 0)),
                }
        return result

    base.first_capped_elimination = wrapped_first
    core.v2.discover_macro_restore_v2 = wrapped_v2
    try:
        result = core.solve_decision_core(cnf)
    finally:
        base.first_capped_elimination = original_first
        core.v2.discover_macro_restore_v2 = original_v2

    return {
        "case": deepcopy(meta),
        "source_fingerprint": base.fingerprint(cnf),
        "N": int(result["N"]),
        "status": result["status"],
        "reason": result["reason"],
        "missing_bridge": result.get("missing_bridge"),
        "max_state_units": int(result["ledger"]["max_state_units"]),
        "event_kinds": [e.get("kind") for e in result.get("events", [])],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases-per-rung", type=int, default=1)
    args = parser.parse_args()
    if args.cases_per_rung < 1:
        raise ValueError("cases-per-rung must be positive")

    observations: list[dict] = []
    cases: list[dict] = []

    random_rungs = [
        ("RANDOM_W4_N10_M30", 10, 30, 4, 18100),
        ("RANDOM_W4_N14_M56", 14, 56, 4, 18200),
        ("RANDOM_W5_N14_M70", 14, 70, 5, 18300),
        ("RANDOM_W5_N16_M96", 16, 96, 5, 18400),
        ("RANDOM_W6_N18_M120", 18, 120, 6, 18500),
    ]
    selector_rungs = [
        ("SELECTOR_W4_N8_M40", 8, 40, 4, 19100),
        ("SELECTOR_W4_N8_M50", 8, 50, 4, 19200),
        ("SELECTOR_W4_N8_M60", 8, 60, 4, 19300),
    ]

    for rung, nvars, nclauses, width, seed0 in random_rungs:
        for offset in range(args.cases_per_rung):
            meta = {
                "family": "RANDOM_WIDTH",
                "rung": rung,
                "seed": seed0 + offset,
                "nvars": nvars,
                "nclauses": nclauses,
                "width": width,
            }
            cnf = random_width_cnf(nvars, nclauses, width, seed0 + offset)
            cases.append(run_case(cnf, meta, observations))

    for rung, nvars, nclauses, width, seed0 in selector_rungs:
        for offset in range(args.cases_per_rung):
            meta = {
                "family": "SELECTOR_PRODUCT",
                "rung": rung,
                "seed": seed0 + offset,
                "leaf_nvars": nvars,
                "leaf_clauses": nclauses,
                "leaf_width": width,
            }
            cnf = selector_product_case(nvars, nclauses, width, seed0 + offset)
            cases.append(run_case(cnf, meta, observations))

    l1a_counter = choose_min(observations, lambda r: not r["L1A_frequent_pair_forced"])
    l1b_counter = choose_min(observations, lambda r: not r["L1B_pair_density_forced"])
    l1_counter = choose_min(observations, lambda r: r.get("v2_rescue_exists") is False)

    report = {
        "schema": "JANUS/C025/ROOT-PIVOT-GRAMMAR-FALSIFIER/v1",
        "status": "L1_ROOT_GRAMMAR_COUNTEREXAMPLE_FOUND" if l1_counter else "NO_L1_COUNTEREXAMPLE_IN_BOUNDED_SEARCH",
        "fixed_algorithm": "PIRC_DECISION_CORE_V0_4",
        "cases_per_rung": args.cases_per_rung,
        "cases_examined": len(cases),
        "ordinary_all_pivot_overflow_reachable_states": len(observations),
        "cases": cases,
        "reachable_gap_observations": [public_observation(r) for r in observations],
        "candidate_results": {
            "L1_ROOT_PHASE_POLYNOMIAL_GRAMMAR_TOTALITY": {
                "bounded_status": "REFUTED_BY_REACHABLE_WITNESS" if l1_counter else "NOT_REFUTED_IN_BOUNDED_SEARCH__NOT_PROVED",
                "counterexample": witness_from(l1_counter),
            },
            "L1A_ALL_PIVOT_OVERFLOW_FORCES_FREQUENT_PAIR": {
                "bounded_status": "REFUTED_BY_REACHABLE_WITNESS" if l1a_counter else "NOT_REFUTED_IN_BOUNDED_SEARCH__NOT_PROVED",
                "counterexample": witness_from(l1a_counter),
            },
            "L1B_ALL_PIVOT_OVERFLOW_FORCES_PAIR_DENSITY": {
                "bounded_status": "REFUTED_BY_REACHABLE_WITNESS" if l1b_counter else "NOT_REFUTED_IN_BOUNDED_SEARCH__NOT_PROVED",
                "counterexample": witness_from(l1b_counter),
            },
        },
        "scientific_boundary": {
            "bounded_finite_falsification_only": True,
            "only_states_reachable_at_frozen_core_callsite_are_tested": True,
            "instrumentation_does_not_change_transition_return_values": True,
            "absence_of_counterexample_is_not_proof": True,
            "models_or_heuristics_used_for_theorem_promotion": False,
            "root_free_v3_tail_addressed": False,
            "P2_REACHABLE_PRESERVATION": "OPEN",
            "P_VS_NP": P_VS_NP,
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
