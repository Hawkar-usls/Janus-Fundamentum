#!/usr/bin/env python3
"""Deterministic balanced-pressure adversary for the root-free C025 v3 tail.

This is OFFLINE research instrumentation, not theorem runtime.  It uses the
proved integer degree-pressure condition to choose parameter regimes that are
not automatically discharged by an ordinary pivot, then generates deterministic
seeded width-3 states with high variable incidence but dispersed sign-aware
literal pairs.

A found local gap proves only that the frozen v3 grammar is not total over all
arbitrary synthetic root-free states under the supplied synthetic original-N
budget.  It is NOT a reachable-state counterexample until a frozen forward
trajectory from a legitimate root of the same original N is certified.

P_VS_NP remains OPEN.
"""
from __future__ import annotations

from collections import Counter
import json
import random
from itertools import combinations

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_unified_macro_restore_v2 as v2
from experiments.direct import janus_unified_macro_restore_v3 as v3
from experiments.direct import janus_v3_root_free_local_gap_probe as oldprobe
from experiments.direct import janus_v3_sequential_budget_local_gap_microscope as microscope

P_VS_NP = "OPEN"


def signaware_pair_counts(cnf: base.CNF) -> Counter[tuple[int, int]]:
    out: Counter[tuple[int, int]] = Counter()
    for c in cnf:
        for a, b in combinations(c, 2):
            if abs(a) == abs(b):
                continue
            pair = tuple(sorted((a, b), key=lambda z: (abs(z), z < 0)))
            out[pair] += 1
    return out


def macro_fit_scan(cnf: base.CNF, N: int) -> dict:
    cap = N * N
    fresh = max(base.vars_of(cnf), default=0) + 1
    rows = []
    for a, b in v2.all_or_pair_candidates(cnf):
        macro, cert = v2.apply_or_pair_v2(cnf, a, b, fresh)
        if not v2.verify_or_pair_v2(cnf, macro, cert):
            raise AssertionError("B2_MACRO_REPLAY_FAILED")
        units = base.state_units(macro)
        if units <= cap:
            rows.append({
                "pair": [a, b],
                "macro_units": units,
                "replaced_occurrences": int(cert["replaced_occurrences"]),
            })
    return {"count": len(rows), "first": rows[0] if rows else None}


def generated_state(N: int, seed: int) -> base.CNF:
    nvars = N
    # width=3 => state_units=1+4*m for a duplicate-free uniform-width CNF.
    m = (N * N - 1) // 4
    universe = oldprobe.width3_universe(nvars)
    if m > len(universe):
        raise ValueError("RUNG_HAS_TOO_FEW_DISTINCT_WIDTH3_CLAUSES")
    rng = random.Random((N << 32) ^ seed)
    rows = rng.sample(universe, m)
    cnf = base.canon_cnf(rows)
    if len(cnf) != m:
        raise AssertionError("UNEXPECTED_UNIFORM_WIDTH_CANONICAL_COLLAPSE")
    return cnf


def run_rung(N: int, seeds: int) -> dict:
    m = (N * N - 1) // 4
    totals = {
        "seeds": seeds,
        "full_connected": 0,
        "earlier_exact_lane": 0,
        "ordinary_pivot_exists": 0,
        "all_pivot_overflow": 0,
        "all_overflow_with_zero_macro_fit": 0,
        "sequential_certified": 0,
        "v3_plan_exists": 0,
        "true_local_v3_gap": 0,
    }
    first_all_overflow = None
    first_gap = None

    for seed in range(seeds):
        cnf = generated_state(N, seed)
        if not oldprobe.connected_and_full(cnf, N):
            continue
        totals["full_connected"] += 1
        if base.state_units(cnf) > N * N:
            raise AssertionError("GENERATED_STATE_EXCEEDS_FROZEN_CAP")

        lane = oldprobe.earlier_exact_local_lane(cnf)
        if lane is not None:
            totals["earlier_exact_lane"] += 1
            continue

        overflow, pivot_rows = oldprobe.all_pivots_overflow(cnf, N * N)
        if not overflow:
            totals["ordinary_pivot_exists"] += 1
            continue
        totals["all_pivot_overflow"] += 1

        pair_counts = signaware_pair_counts(cnf)
        max_pair_frequency = max(pair_counts.values(), default=0)
        macro_fit = macro_fit_scan(cnf, N)
        if macro_fit["count"] == 0:
            totals["all_overflow_with_zero_macro_fit"] += 1

        seq = microscope.sequential_certificate_scan(cnf, N)
        if seq["exists"]:
            totals["sequential_certified"] += 1

        state = oldprobe.make_state(cnf, N)
        plan = v3.discover_extension_tail_plan_v3(state)
        if plan is not None:
            totals["v3_plan_exists"] += 1
        else:
            totals["true_local_v3_gap"] += 1

        row = {
            "N": N,
            "seed": seed,
            "nvars": N,
            "clauses": m,
            "state_units": base.state_units(cnf),
            "state_cap": N * N,
            "headroom": N * N - base.state_units(cnf),
            "fingerprint": base.fingerprint(cnf),
            "cnf": cnf,
            "max_signaware_pair_frequency": max_pair_frequency,
            "macro_fit": macro_fit,
            "sequential_certificate": seq,
            "pivot_scan": pivot_rows,
            "v3_plan": None if plan is None else {
                "pair": plan.macro_cert.get("represents"),
                "pivots": list(plan.pivots),
                "macro_units": base.state_units(plan.macro_cnf),
                "after_units": base.state_units(plan.after),
            },
        }
        if first_all_overflow is None:
            first_all_overflow = row
        if plan is None:
            first_gap = {
                **row,
                "claim_ceiling": "ARBITRARY_SYNTHETIC_ROOT_FREE_LOCAL_GAP__REACHABILITY_NOT_ESTABLISHED",
            }
            break

    return {
        "parameters": {"N": N, "nvars": N, "clauses": m, "seeds": seeds},
        "totals": totals,
        "first_all_pivot_overflow": first_all_overflow,
        "first_true_local_v3_gap": first_gap,
        "status": "TRUE_LOCAL_V3_GAP_FOUND" if first_gap is not None else "NO_TRUE_LOCAL_V3_GAP_IN_SEEDED_RUNG",
    }


def main() -> int:
    # Frozen ladder.  Stop at the first exact local grammar gap.
    rungs = (
        (8, 256),
        (10, 256),
        (12, 256),
        (14, 128),
        (16, 128),
    )
    results = []
    for N, seeds in rungs:
        row = run_rung(N, seeds)
        results.append(row)
        if row["first_true_local_v3_gap"] is not None:
            break

    first_gap = next((r["first_true_local_v3_gap"] for r in results if r["first_true_local_v3_gap"] is not None), None)
    report = {
        "schema": "JANUS/C025/V3-BALANCED-PRESSURE-ADVERSARY-PROBE/v1",
        "rungs": results,
        "first_true_local_v3_gap": first_gap,
        "scientific_boundary": {
            "offline_generated_adversary_only": True,
            "deterministic_seeded": True,
            "synthetic_original_N_budget": True,
            "arbitrary_root_free_state": True,
            "reachability_from_legitimate_root_not_established": True,
            "found_local_gap_does_not_refute_reachable_totality": True,
            "no_gap_does_not_prove_availability": True,
            "generative_or_predictive_layer_has_theorem_authority": False,
            "V3_ROOT_FREE_TAIL_AVAILABILITY": "OPEN",
            "P_VS_NP": P_VS_NP,
        },
    }
    report["status"] = "TRUE_LOCAL_V3_GAP_FOUND" if first_gap is not None else "NO_TRUE_LOCAL_V3_GAP_IN_FROZEN_SEEDED_LADDER"
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
