#!/usr/bin/env python3
"""Measurement-only exact pressure microscope on the frozen balanced product state.

Reconstruct the already-frozen balanced-selector source (fingerprint fixed by
workflow 33058094058), verify that v0.4's first ordinary transition is exact
elimination of selector 1, replay that transition independently, and then test
EVERY remaining pivot on that one reachable residual under the same N^2 cap.

No grammar, pivot order, cap, or decision rule is changed.  This tool cannot
advance the theorem machine.  It only exposes where ordinary exact elimination
still has slack and where it overflows.  P_VS_NP remains OPEN.
"""
from __future__ import annotations

import json
from collections import Counter
from math import comb

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_pirc_decision_core_v0_4 as core
from experiments.direct import janus_balanced_selector_product_hostile_probe as src

P_VS_NP = "OPEN"
FROZEN_SOURCE_FINGERPRINT = "f74f9d5c53197a3035c498dbfe911d5c22cb6831a22f4dc77943e13f05453b5b"
FROZEN_LEFT_SEED = 6100
FROZEN_RIGHT_SEED = 7103


def build_frozen_source() -> base.CNF:
    left_seed, left0 = src.first_structural_seed(src.LEFT_BASE_SEED)
    right_seed, right0 = src.first_structural_seed(src.RIGHT_BASE_SEED)
    if (left_seed, right_seed) != (FROZEN_LEFT_SEED, FROZEN_RIGHT_SEED):
        raise AssertionError("STRUCTURAL_SEED_DRIFT")
    left = src.relabel(left0, 2)
    right = src.relabel(right0, 2 + src.NVARS)
    source = src.selector_product(left, right, selector=1)
    if base.fingerprint(source) != FROZEN_SOURCE_FINGERPRINT:
        raise AssertionError("FROZEN_BALANCED_SOURCE_FINGERPRINT_DRIFT")
    return source


def pair_stats(cnf: base.CNF) -> tuple[int, int, tuple[int, int] | None]:
    freq: Counter[tuple[int, int]] = Counter()
    P = 0
    for clause in cnf:
        P += comb(len(clause), 2)
        for i in range(len(clause)):
            for j in range(i + 1, len(clause)):
                a, b = clause[i], clause[j]
                if abs(a) == abs(b):
                    continue
                pair = tuple(sorted((a, b), key=lambda z: (abs(z), z < 0)))
                freq[pair] += 1
    if not freq:
        return P, 0, None
    pair, t = min(freq.items(), key=lambda kv: (-kv[1], tuple((abs(z), z < 0) for z in kv[0])))
    return P, t, pair


def main() -> int:
    source = build_frozen_source()
    result = core.solve_decision_core(source)
    ordinary_events = [e for e in result.get("events", []) if e.get("kind") == "AKINATOR_EXACT_ELIMINATION"]
    if not ordinary_events:
        raise AssertionError("FROZEN_RUN_NO_LONGER_HAS_ORDINARY_EVENT")
    first = ordinary_events[0]
    if int(first.get("pivot")) != 1:
        raise AssertionError("FIRST_ORDINARY_PIVOT_DRIFT")

    N = int(result["N"])
    cap = int(result["state_cap"])
    product_state, selector_stats = base.eliminate_var_capped(source, 1, cap)
    if product_state is None:
        raise AssertionError("SELECTOR_REPLAY_UNEXPECTEDLY_OVER_CAP")
    if base.fingerprint(product_state) != first.get("after_fingerprint"):
        raise AssertionError("SELECTOR_PRODUCT_REPLAY_FINGERPRINT_MISMATCH")

    rows = []
    fit = 0
    overflow = 0
    first_fit = None
    first_overflow = None
    for pivot in base.vars_of(product_state):
        out, stats = base.eliminate_var_capped(product_state, pivot, cap)
        status = "FIT" if out is not None else "OVERFLOW"
        if out is not None:
            fit += 1
            if first_fit is None:
                first_fit = pivot
        else:
            overflow += 1
            if first_overflow is None:
                first_overflow = pivot
        rows.append({
            "pivot": pivot,
            "status": status,
            "positive": stats.get("positive"),
            "negative": stats.get("negative"),
            "pairs_examined": int(stats.get("pairs", 0)),
            "tautologies": int(stats.get("tautologies", 0)),
            "raw_units_at_return": int(stats.get("raw_units", 0)),
            "canonical_units": stats.get("canonical_units"),
            "aborted": bool(stats.get("aborted", False)),
        })

    P, tmax, pair = pair_stats(product_state)
    s = base.state_units(product_state)
    n = len(base.vars_of(product_state))
    frequent_threshold = s - 2 * N + 11
    density_threshold = 2 * n * (n - 1) * frequent_threshold if n >= 2 else 0

    report = {
        "schema": "JANUS/C025/BALANCED-PRODUCT-PRESSURE-MICROSCOPE/v1",
        "status": "ALL_PIVOTS_OVERFLOW" if fit == 0 else "ORDINARY_ESCAPE_REMAINS",
        "source_fingerprint": base.fingerprint(source),
        "source_decision_status": result["status"],
        "source_decision_reason": result["reason"],
        "N": N,
        "state_cap": cap,
        "selector_replay": {
            "pivot": 1,
            "stats": selector_stats,
            "product_fingerprint": base.fingerprint(product_state),
            "product_state_units": s,
            "product_volume_ratio": s / max(1, N),
        },
        "pivot_pressure": {
            "live_variables": n,
            "fit_count": fit,
            "overflow_count": overflow,
            "first_fit_pivot": first_fit,
            "first_overflow_pivot": first_overflow,
            "rows": rows,
        },
        "pair_pressure": {
            "pair_incidences_P": P,
            "max_pair_frequency": tmax,
            "max_pair": list(pair) if pair is not None else None,
            "frequent_pair_sufficient_threshold": frequent_threshold,
            "pair_density_sufficient_threshold": density_threshold,
            "frequent_pair_v2_theorem_triggers": tmax >= frequent_threshold,
            "pair_density_corollary_triggers": P >= density_threshold,
        },
        "scientific_boundary": {
            "measurement_only": True,
            "one_previously_frozen_reachable_state": True,
            "does_not_change_decision_core": True,
            "ordinary_escape_remaining_is_not_totality_proof": True,
            "all_pivots_overflow_if_found_would_still_require_v2_v3_test": True,
            "HIGH_VOLUME_RESCUE_TOTALITY": "OPEN",
            "P_VS_NP": P_VS_NP,
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
