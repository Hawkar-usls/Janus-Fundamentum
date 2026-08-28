#!/usr/bin/env python3
"""PIPPI 50:50 Cycle0 cached-resource re-audit.

Separates two different quantities that must not be conflated:
1. route-equivalent exhaustive work: sum of pair/check work over every logical
   route replay (useful as a no-cache counterfactual / search-space measure);
2. actual unique-transition work under the implemented exact cache: each
   (canonical_state, pivot, cap) elimination is computed and exact-verified once.

The second quantity is the appropriate pair-work charge for the implemented
Cycle0 label generator. Model-training wall time is a separate unit and is not
silently converted into pair-work. Therefore GLOBAL_RESOURCE_POSITIVE remains
UNKNOWN unless a common normalized resource unit is declared.

P_VS_NP remains OPEN.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
from typing import Any

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.mad_lab import juxtapose_50x50_multiformula_corpus as corpus_mod

P_VS_NP = "OPEN"
UNBOUNDED_CAP = 10**9
PIVOTS = tuple(range(1, 8))


def audit_formula(seed: int, stress_cap: int) -> dict[str, Any]:
    root = corpus_mod.construct(seed)
    cache: dict[tuple[base.CNF, int, int], tuple[base.CNF | None, dict[str, Any]]] = {}
    unique_pairs = 0
    unique_raw_units = 0
    exact_verified_outputs = 0
    overflow_transitions = 0

    def transition(state: base.CNF, pivot: int, cap: int):
        nonlocal unique_pairs, unique_raw_units, exact_verified_outputs, overflow_transitions
        key = (state, pivot, cap)
        if key in cache:
            return cache[key]
        out, st = base.eliminate_var_capped(state, pivot, cap)
        unique_pairs += int(st.get("pairs", 0))
        unique_raw_units += int(st.get("raw_units", 0))
        if out is None:
            overflow_transitions += 1
        else:
            assert base.verify_elimination_transition(state, pivot, out, cap)
            exact_verified_outputs += 1
        cache[key] = (out, st)
        return out, st

    def replay(order: tuple[int, ...], cap: int):
        state = root
        for p in order:
            if state == ((),):
                break
            if p not in set(base.vars_of(state)):
                continue
            out, _ = transition(state, p, cap)
            if out is None:
                return False
            state = out
        return state == ((),)

    # The original Cycle0 determines the stress cap from the unbounded
    # exhaustive landscape, then exhausts the landscape again at stress cap.
    for order in itertools.permutations(PIVOTS):
        assert replay(order, UNBOUNDED_CAP)
    safe = 0
    for order in itertools.permutations(PIVOTS):
        safe += int(replay(order, stress_cap))
    assert safe > 0

    return {
        "seed": seed,
        "stress_cap": stress_cap,
        "unique_transition_count": len(cache),
        "actual_unique_transition_pair_work": unique_pairs,
        "actual_unique_transition_raw_units_sum": unique_raw_units,
        "exact_verified_nonoverflow_transitions": exact_verified_outputs,
        "unique_overflow_transitions": overflow_transitions,
        "safe_orders_at_stress_cap": safe,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--cycle1", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    corpus = json.loads(args.corpus.read_text(encoding="utf-8"))
    cycle1 = json.loads(args.cycle1.read_text(encoding="utf-8"))
    train = [f for f in corpus["formulas"] if f["split"] == "TRAIN"]
    assert len(train) == 24

    rows = [audit_formula(int(f["seed"]), int(f["stress"]["cap"])) for f in train]
    actual_pairs = sum(r["actual_unique_transition_pair_work"] for r in rows)
    actual_transitions = sum(r["unique_transition_count"] for r in rows)
    actual_verified = sum(r["exact_verified_nonoverflow_transitions"] for r in rows)
    actual_overflow = sum(r["unique_overflow_transitions"] for r in rows)
    equivalent_pairs = sum(int(f["stress"]["exhaustive_pair_work"]) for f in train)
    equivalent_checks = sum(int(f["stress"]["exhaustive_exact_checks"]) for f in train)
    cache_misses_recorded = sum(int(f["stress"]["transition_cache"]["misses_exact_verified"]) for f in train)
    assert actual_transitions == cache_misses_recorded

    saved_pairs = int(cycle1["PIPPI_DELTA1"]["pair_work_saved"])
    saved_checks = int(cycle1["PIPPI_DELTA1"]["exact_checks_saved"])
    model_seconds = float(cycle1["teacher_audit"]["training_seconds"]) + float(cycle1["student_audit"]["training_seconds"])

    pair_net = saved_pairs - actual_pairs
    # The exact-transition cache requires one elimination computation per miss;
    # only non-overflow transitions invoke verify_elimination_transition. We
    # report both rather than pretending they are identical costs.
    payload = {
        "schema": "JANUS/PIPPI/50x50-CYCLE0-RESOURCE-REAUDIT/v1.0.0",
        "status": "PASS__RESOURCE_UNITS_SEPARATED",
        "P_VS_NP": P_VS_NP,
        "scope": "24_TRAIN_FINGERPRINTS_USED_BY_CYCLE1",
        "route_equivalent_counterfactual": {
            "exhaustive_exact_route_checks": equivalent_checks,
            "exhaustive_pair_work": equivalent_pairs,
            "interpretation": "Logical sum over all stressed routes; NOT actual compute after transition caching.",
        },
        "implemented_cached_generator": {
            "unique_transition_computations": actual_transitions,
            "exact_verified_nonoverflow_transitions": actual_verified,
            "unique_overflow_transitions": actual_overflow,
            "actual_unique_transition_pair_work": actual_pairs,
            "cache_reuse_factor_by_transition_count": equivalent_checks / max(1, actual_transitions),
            "cache_reuse_factor_by_pair_work": equivalent_pairs / max(1, actual_pairs),
        },
        "cycle1_downstream_holdout_savings_vs_static_numeric_control": {
            "exact_checks_saved": saved_checks,
            "pair_work_saved": saved_pairs,
            "holdout_formulas": 8,
        },
        "pair_work_accounting_horizon": {
            "actual_cached_training_pair_work_charge": actual_pairs,
            "downstream_pair_work_saved_so_far": saved_pairs,
            "net_pair_work_after_actual_cached_generation_charge": pair_net,
            "PAIR_WORK_RESOURCE_POSITIVE": pair_net > 0,
            "estimated_break_even_additional_holdout_like_formulas_if_gain_rate_stays_constant": (actual_pairs - saved_pairs) / max(1e-12, saved_pairs / 8.0) if pair_net < 0 and saved_pairs > 0 else 0.0,
            "warning": "Break-even projection is diagnostic only; gain rate is not assumed to remain constant.",
        },
        "separate_model_training_resource": {
            "teacher_plus_student_training_wall_seconds_on_GitHub_runner": model_seconds,
            "pair_work_conversion_declared": False,
            "energy_measurement_available": False,
        },
        "global_resource_statement": {
            "GLOBAL_RESOURCE_POSITIVE": "UNKNOWN",
            "reason": "Pair-work and neural training wall-time/energy are different units; no common normalized resource budget has been declared.",
        },
        "per_formula": rows,
        "firewall": {
            "DO_NOT_CALL_ROUTE_EQUIVALENT_WORK_ACTUAL_COMPUTE": True,
            "DO_NOT_ADD_PAIR_WORK_AND_SECONDS": True,
            "CACHE_DOES_NOT_CHANGE_EXACT_SEMANTICS": True,
            "MODEL_PREDICTION_IS_NOT_PROOF": True,
            "P_VS_NP": P_VS_NP,
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "equivalent_pair_work": equivalent_pairs,
        "actual_cached_pair_work": actual_pairs,
        "unique_transitions": actual_transitions,
        "pair_work_net": pair_net,
        "global_resource_positive": "UNKNOWN",
        "P_VS_NP": P_VS_NP,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
