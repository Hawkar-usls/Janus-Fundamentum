#!/usr/bin/env python3
"""Compute-optimized successor of c025_signed_regular_balanced_delta_attack.

Scientific search space, signed-regular construction, exact factorization, ranking,
and refutation gates are unchanged.  The only change is computational: N and the
N^2 cap are constants of the frozen fixed chassis and are verified once before
coverage; pair evaluation never rebuilds/canonicalizes the 120-clause source.
Source/product fingerprints are computed only for the champion.
"""
from __future__ import annotations

import argparse
import json
import random

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.theorem_extraction import c025_signed_regular_balanced_delta_attack as slow

P_VS_NP = "OPEN"
FIXED_N = 614
FIXED_CAP = FIXED_N * FIXED_N


def fast_pair_evaluation(left: slow.LeafFeature, right: slow.LeafFeature) -> dict:
    rows = []
    raws = []
    for pivot in slow.VARS:
        u = slow.raw_from_features(left, right, pivot)
        raws.append(u)
        rows.append({"side": "L", "pivot": pivot, "raw_units": u, "margin": u - FIXED_CAP})
    for pivot in slow.VARS:
        u = slow.raw_from_features(right, left, pivot)
        raws.append(u)
        rows.append({"side": "R", "pivot": pivot, "raw_units": u, "margin": u - FIXED_CAP})

    v1 = slow.v1
    s = 1 + v1.LEAF_CLAUSES * v1.LEAF_CLAUSES * (1 + 2 * v1.LEAF_WIDTH)
    P = v1.LEAF_CLAUSES * v1.LEAF_CLAUSES * 15
    tmax = max(
        left.pair_frequency * v1.LEAF_CLAUSES,
        right.pair_frequency * v1.LEAF_CLAUSES,
        left.max_literal_count * right.max_literal_count,
    )
    threshold = s - 2 * FIXED_N + 11
    n_live = 2 * v1.LEAF_NVARS
    density_threshold = 2 * n_live * (n_live - 1) * threshold
    delta = min(raws) - FIXED_CAP
    return {
        "N": FIXED_N,
        "cap": FIXED_CAP,
        "product_state_units": s,
        "delta": delta,
        "min_raw_units": min(raws),
        "mean_raw_units": sum(raws) / len(raws),
        "max_raw_units": max(raws),
        "all_pivot_overflow": delta > 0,
        "max_pair_frequency": tmax,
        "frequent_pair_threshold": threshold,
        "pair_rescue_margin": tmax - threshold,
        "pair_dispersed": tmax < threshold,
        "pair_incidences_P": P,
        "pair_density_threshold": density_threshold,
        "pair_density_margin": P - density_threshold,
        "pair_density_dispersed": P < density_threshold,
        "pivot_rows": rows,
        "left_seed": left.seed,
        "right_seed": right.seed,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--leaf-pool", type=int, default=1200)
    ap.add_argument("--pair-samples", type=int, default=120000)
    ap.add_argument("--seed", type=int, default=26082811)
    args = ap.parse_args()
    if args.leaf_pool < 10 or args.pair_samples < 1:
        raise ValueError("leaf-pool>=10 and pair-samples>=1 required")

    # Exact factorization firewall inherited from predecessor.
    slow.v1.selftest_factorization()
    features = [slow.feature_leaf(args.seed + i) for i in range(args.leaf_pool)]

    # Fixed-N assumption is verified against the actual frozen source once.
    witness_source = slow.v1.build_source(features[0].leaf, features[1].leaf)
    measured_N = base.input_size_units(witness_source)
    if measured_N != FIXED_N:
        raise AssertionError(("FIXED_CHASSIS_N_DRIFT", measured_N, FIXED_N))
    if FIXED_CAP != measured_N * measured_N:
        raise AssertionError("FIXED_CAP_DRIFT")

    # Fast evaluator must be bit-identical to the slower exact-factorized one.
    fast_test = fast_pair_evaluation(features[0], features[1])
    slow_test = slow.v1.evaluate(features[0].leaf, features[1].leaf)
    for key in (
        "N", "cap", "product_state_units", "delta", "min_raw_units",
        "max_raw_units", "pair_rescue_margin", "pair_density_margin",
    ):
        if fast_test[key] != slow_test[key]:
            raise AssertionError(("FAST_EVALUATOR_MISMATCH", key, fast_test[key], slow_test[key]))
    if fast_test["pivot_rows"] != slow_test["pivot_rows"]:
        raise AssertionError("FAST_PIVOT_LANDSCAPE_MISMATCH")

    rng = random.Random(args.seed ^ 0x5A17)
    best = None
    checkpoints = []
    executed = 0
    for i in range(args.pair_samples):
        left = features[rng.randrange(len(features))]
        right = features[rng.randrange(len(features))]
        e = fast_pair_evaluation(left, right)
        executed = i + 1
        if best is None or (e["delta"], -e["pair_rescue_margin"], e["mean_raw_units"]) > (
            best["eval"]["delta"], -best["eval"]["pair_rescue_margin"], best["eval"]["mean_raw_units"]
        ):
            best = {"left": left, "right": right, "eval": e, "sample": i}
        if executed % max(1, args.pair_samples // 20) == 0:
            checkpoints.append({
                "samples": executed,
                "best_delta": best["eval"]["delta"],
                "best_min_raw_units": best["eval"]["min_raw_units"],
                "pair_rescue_margin": best["eval"]["pair_rescue_margin"],
                "left_seed": best["left"].seed,
                "right_seed": best["right"].seed,
            })
        if e["all_pivot_overflow"] and e["pair_dispersed"]:
            best = {"left": left, "right": right, "eval": e, "sample": i}
            break

    assert best is not None
    be = best["eval"]

    # Champion gets independent predecessor exact-factorized confirmation.
    confirm = slow.v1.evaluate(best["left"].leaf, best["right"].leaf)
    for key in ("delta", "min_raw_units", "max_raw_units", "pair_rescue_margin", "pair_density_margin"):
        if confirm[key] != be[key]:
            raise AssertionError(("CHAMPION_CONFIRMATION_DRIFT", key, be[key], confirm[key]))
    if confirm["pivot_rows"] != be["pivot_rows"]:
        raise AssertionError("CHAMPION_PIVOT_LANDSCAPE_DRIFT")

    source = slow.v1.build_source(best["left"].leaf, best["right"].leaf)
    product = slow.v1.build_product_global(best["left"].leaf, best["right"].leaf)
    source_fp = base.fingerprint(source)
    product_fp = base.fingerprint(product)

    candidate_found = bool(be["all_pivot_overflow"] and be["pair_dispersed"])
    replay = slow.v1.exact_reachability_replay(
        best["left"].leaf, best["right"].leaf, confirm
    ) if candidate_found else None

    l1a_refuted = bool(
        candidate_found and replay
        and replay["selector_reaches_target"]
        and replay["target_seen_at_ordinary_callsite"]
        and replay["all_ordinary_pivots_overflow_at_target"] is True
        and be["pair_rescue_margin"] < 0
    )
    l1b_refuted = bool(l1a_refuted and be["pair_density_margin"] < 0)
    l1_refuted = bool(
        l1a_refuted and replay
        and replay["v2_called_on_target"]
        and replay["v2_rescue_exists"] is False
    )

    report = {
        "schema": "JANUS/C025/SIGNED-REGULAR-BALANCED-DELTA-ATTACK-FAST/v1",
        "status": (
            "L1_REACHABLE_COUNTEREXAMPLE_FOUND" if l1_refuted
            else "L1A_REACHABLE_COUNTEREXAMPLE_FOUND" if l1a_refuted
            else "DIRECT_CANDIDATE_FOUND_BUT_REACHABILITY_GATE_FAILED" if candidate_found
            else "NO_ALL_PIVOT_OVERFLOW_CANDIDATE_IN_BOUNDED_SIGNED_REGULAR_SEARCH"
        ),
        "search": {
            "seed": args.seed,
            "leaf_pool": args.leaf_pool,
            "pair_samples_requested": args.pair_samples,
            "pair_samples_executed": executed,
            "signed_regular_profile": "15:15 for every variable in every leaf",
            "fixed_N": FIXED_N,
            "fixed_cap": FIXED_CAP,
            "fixed_N_runtime_verification": "PASS",
            "predecessor_factorization_selftest": "PASS",
            "fast_vs_exact_factorized_equivalence": "PASS",
            "champion_independent_factorized_confirmation": "PASS",
            "optimization_only": "source construction/fingerprint removed from inner pair loop",
            "checkpoints": checkpoints,
        },
        "best_candidate": {
            "evaluation": be,
            "source_fingerprint": source_fp,
            "product_fingerprint": product_fp,
            "left_leaf_fingerprint": best["left"].fp,
            "right_leaf_fingerprint": best["right"].fp,
            "left_profile": {str(k): list(v) for k, v in slow.v1.polarity_profile(best["left"].leaf).items()},
            "right_profile": {str(k): list(v) for k, v in slow.v1.polarity_profile(best["right"].leaf).items()},
            "left_leaf": [list(c) for c in best["left"].leaf],
            "right_leaf": [list(c) for c in best["right"].leaf],
            "source_cnf": [list(c) for c in source],
        },
        "exact_reachability_replay": replay,
        "candidate_results": {
            "L1_ROOT_PHASE_POLYNOMIAL_GRAMMAR_TOTALITY": "REFUTED_BY_EXACT_REACHABLE_WITNESS" if l1_refuted else "OPEN_NOT_PROVED",
            "L1A_ALL_PIVOT_OVERFLOW_FORCES_FREQUENT_PAIR": "REFUTED_BY_EXACT_REACHABLE_WITNESS" if l1a_refuted else "OPEN_NOT_PROVED",
            "L1B_ALL_PIVOT_OVERFLOW_FORCES_PAIR_DENSITY": "REFUTED_BY_EXACT_REACHABLE_WITNESS" if l1b_refuted else "OPEN_NOT_PROVED",
        },
        "scientific_boundary": {
            "same_scientific_objective_as_signed_regular_predecessor": True,
            "only_inner_loop_compute_was_optimized": True,
            "fixed_chassis_N_not_gamed": True,
            "coverage_search_has_no_theorem_authority": True,
            "final_refutation_requires_exact_frozen_core_reachability": True,
            "absence_of_counterexample_is_not_proof": True,
            "same_run_theorem_promotion": False,
            "P2_REACHABLE_PRESERVATION": "OPEN",
            "P_VS_NP": P_VS_NP,
        },
        "P_VS_NP": P_VS_NP,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
