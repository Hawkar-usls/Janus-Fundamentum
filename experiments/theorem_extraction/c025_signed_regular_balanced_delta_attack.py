#!/usr/bin/env python3
"""Signed-regular successor attack on the C025 all-pivot-overflow gap.

Every leaf has exactly 60 distinct width-3 clauses over 6 variables and satisfies
p(v)=q(v)=15 for every variable.  The source chassis therefore keeps N fixed at
the predecessor value while removing signed-degree imbalance as a cheap-pivot
escape.  Search is broad JUXTAPOSE coverage over independently generated exact-
balanced designs.  Search output has no theorem authority; exact frozen-core
reachability replay is mandatory before any candidate can refute L1/L1A/L1B.
"""
from __future__ import annotations

import argparse
import json
import random
from dataclasses import dataclass
from itertools import combinations

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.theorem_extraction import c025_adversarial_delta_pair_dispersion_attack as v1

P_VS_NP = "OPEN"
VARS = tuple(range(1, v1.LEAF_NVARS + 1))
ALL_SUPPORTS = tuple(combinations(VARS, v1.LEAF_WIDTH))


def complement_support(s: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(v for v in VARS if v not in set(s))


def support_partitions() -> tuple[tuple[tuple[int, ...], tuple[int, ...]], ...]:
    out = []
    seen = set()
    for s in ALL_SUPPORTS:
        t = complement_support(s)
        key = tuple(sorted((s, t)))
        if key in seen:
            continue
        seen.add(key)
        out.append((key[0], key[1]))
    if len(out) != 10:
        raise AssertionError("EXPECTED_TEN_3_PLUS_3_PARTITIONS")
    return tuple(out)


PARTITIONS = support_partitions()


def complement_sign_pair(support: tuple[int, ...], pair_id: int) -> tuple[base.Clause, base.Clause]:
    if pair_id not in range(4):
        raise ValueError("pair_id must be in 0..3")
    # Representatives with first sign bit fixed to 0 enumerate the four pairs
    # modulo global sign complement.
    bits = (0, (pair_id >> 1) & 1, pair_id & 1)
    a = tuple(v if bit else -v for v, bit in zip(support, bits))
    b = tuple(-lit for lit in a)
    ca, cb = base.canon_clause(a), base.canon_clause(b)
    if ca is None or cb is None:
        raise AssertionError("COMPLEMENT_PAIR_TAUTOLOGY")
    return ca, cb


def balanced_design_leaf(seed: int) -> base.CNF:
    rng = random.Random(seed)
    chosen = rng.sample(PARTITIONS, 5)
    support_instances = list(ALL_SUPPORTS)
    for a, b in chosen:
        support_instances.extend((a, b))
    if len(support_instances) != 30:
        raise AssertionError("SUPPORT_INSTANCE_COUNT_DRIFT")

    by_support: dict[tuple[int, ...], int] = {}
    rows: set[base.Clause] = set()
    for support in support_instances:
        occurrence = by_support.get(support, 0)
        by_support[support] = occurrence + 1
        used = set()
        # Recover pair ids already used on this support from rows by direct trial.
        for pid in range(4):
            x, y = complement_sign_pair(support, pid)
            if x in rows or y in rows:
                used.add(pid)
        choices = [pid for pid in range(4) if pid not in used]
        if not choices:
            raise AssertionError("SIGN_PAIR_CAPACITY_EXHAUSTED")
        pid = rng.choice(choices)
        x, y = complement_sign_pair(support, pid)
        rows.add(x)
        rows.add(y)

    leaf = tuple(sorted(rows, key=lambda c: (len(c), c)))
    if len(leaf) != v1.LEAF_CLAUSES:
        raise AssertionError("BALANCED_DESIGN_CLAUSE_COUNT_DRIFT")
    profile = v1.polarity_profile(leaf)
    if any(p != 15 or q != 15 for p, q in profile.values()):
        raise AssertionError(("SIGNED_REGULARITY_FAILED", profile))
    return leaf


@dataclass(frozen=True)
class PivotFeature:
    retained_count: int
    retained_width: int
    resolvent_count: int
    resolvent_width: int
    duplicate_left_count: int
    duplicate_left_width: int


@dataclass
class LeafFeature:
    seed: int
    leaf: base.CNF
    fp: str
    union_count: int
    union_width: int
    union_original_count: int
    union_original_width: int
    pair_frequency: int
    max_literal_count: int
    pivots: dict[int, PivotFeature]


def feature_leaf(seed: int) -> LeafFeature:
    leaf = balanced_design_leaf(seed)
    unions = v1.pair_union_set(leaf)
    leaf_set = set(leaf)
    uorig = unions & leaf_set
    pivots: dict[int, PivotFeature] = {}
    for pivot in VARS:
        retained = {c for c in leaf if pivot not in c and -pivot not in c}
        rset = v1.leaf_resolution_set(leaf, pivot)
        dup = rset & retained
        pivots[pivot] = PivotFeature(
            retained_count=len(retained),
            retained_width=sum(map(len, retained)),
            resolvent_count=len(rset),
            resolvent_width=sum(map(len, rset)),
            duplicate_left_count=len(dup),
            duplicate_left_width=sum(map(len, dup)),
        )
    lit = v1.literal_counts(leaf)
    return LeafFeature(
        seed=seed,
        leaf=leaf,
        fp=base.fingerprint(leaf),
        union_count=len(unions),
        union_width=sum(map(len, unions)),
        union_original_count=len(uorig),
        union_original_width=sum(map(len, uorig)),
        pair_frequency=v1.leaf_pair_frequency(leaf),
        max_literal_count=max(lit.values(), default=0),
        pivots=pivots,
    )


def raw_from_features(left: LeafFeature, right: LeafFeature, pivot: int) -> int:
    p = left.pivots[pivot]
    m = v1.LEAF_CLAUSES
    right_width_sum = v1.LEAF_CLAUSES * v1.LEAF_WIDTH
    ret_count = p.retained_count * m
    ret_width = m * p.retained_width + p.retained_count * right_width_sum
    res_count = p.resolvent_count * right.union_count
    res_width = right.union_count * p.resolvent_width + p.resolvent_count * right.union_width
    dup_count = p.duplicate_left_count * right.union_original_count
    dup_width = (
        right.union_original_count * p.duplicate_left_width
        + p.duplicate_left_count * right.union_original_width
    )
    return 1 + (ret_count + res_count - dup_count) + (ret_width + res_width - dup_width)


def pair_evaluation(left: LeafFeature, right: LeafFeature) -> dict:
    source = v1.build_source(left.leaf, right.leaf)
    N = base.input_size_units(source)
    cap = N * N
    rows = []
    raws = []
    for pivot in VARS:
        u = raw_from_features(left, right, pivot)
        raws.append(u)
        rows.append({"side": "L", "pivot": pivot, "raw_units": u, "margin": u - cap})
    for pivot in VARS:
        u = raw_from_features(right, left, pivot)
        raws.append(u)
        rows.append({"side": "R", "pivot": pivot, "raw_units": u, "margin": u - cap})

    s = 1 + v1.LEAF_CLAUSES * v1.LEAF_CLAUSES * (1 + 2 * v1.LEAF_WIDTH)
    P = v1.LEAF_CLAUSES * v1.LEAF_CLAUSES * 15
    tmax = max(
        left.pair_frequency * v1.LEAF_CLAUSES,
        right.pair_frequency * v1.LEAF_CLAUSES,
        left.max_literal_count * right.max_literal_count,
    )
    threshold = s - 2 * N + 11
    density_threshold = 2 * (2 * v1.LEAF_NVARS) * (2 * v1.LEAF_NVARS - 1) * threshold
    delta = min(raws) - cap
    return {
        "N": N,
        "cap": cap,
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
        "source_fingerprint": base.fingerprint(source),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--leaf-pool", type=int, default=1200)
    parser.add_argument("--pair-samples", type=int, default=120000)
    parser.add_argument("--seed", type=int, default=26082811)
    args = parser.parse_args()
    if args.leaf_pool < 10 or args.pair_samples < 1:
        raise ValueError("leaf-pool>=10 and pair-samples>=1 required")

    # Reuse predecessor algebra self-test, then independently test compact
    # feature evaluation against predecessor exact factorization on one pair.
    v1.selftest_factorization()
    features = [feature_leaf(args.seed + i) for i in range(args.leaf_pool)]
    test_eval = pair_evaluation(features[0], features[1])
    exact_eval = v1.evaluate(features[0].leaf, features[1].leaf)
    for key in ("delta", "min_raw_units", "max_raw_units", "pair_rescue_margin", "pair_density_margin"):
        if test_eval[key] != exact_eval[key]:
            raise AssertionError(("COMPACT_FEATURE_MISMATCH", key, test_eval[key], exact_eval[key]))

    rng = random.Random(args.seed ^ 0x5A17)
    best = None
    checkpoints = []
    for i in range(args.pair_samples):
        a = features[rng.randrange(len(features))]
        b = features[rng.randrange(len(features))]
        e = pair_evaluation(a, b)
        if best is None or (e["delta"], -e["pair_rescue_margin"], e["mean_raw_units"]) > (
            best["eval"]["delta"], -best["eval"]["pair_rescue_margin"], best["eval"]["mean_raw_units"]
        ):
            best = {"left": a, "right": b, "eval": e, "sample": i}
        if (i + 1) % max(1, args.pair_samples // 20) == 0:
            checkpoints.append({
                "samples": i + 1,
                "best_delta": best["eval"]["delta"],
                "best_min_raw_units": best["eval"]["min_raw_units"],
                "pair_rescue_margin": best["eval"]["pair_rescue_margin"],
                "left_seed": best["left"].seed,
                "right_seed": best["right"].seed,
            })
        if e["all_pivot_overflow"] and e["pair_dispersed"]:
            best = {"left": a, "right": b, "eval": e, "sample": i}
            break

    assert best is not None
    be = best["eval"]
    # Confirm compact algebra with predecessor factorized exact evaluator.
    confirm = v1.evaluate(best["left"].leaf, best["right"].leaf)
    if confirm["delta"] != be["delta"] or confirm["pivot_rows"] != be["pivot_rows"]:
        raise AssertionError("CHAMPION_FACTOR_ABSTRACTION_DRIFT")

    candidate_found = bool(be["all_pivot_overflow"] and be["pair_dispersed"])
    replay = v1.exact_reachability_replay(best["left"].leaf, best["right"].leaf, confirm) if candidate_found else None
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
        "schema": "JANUS/C025/SIGNED-REGULAR-BALANCED-DELTA-ATTACK/v1",
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
            "pair_samples_executed": best["sample"] + 1 if candidate_found else args.pair_samples,
            "signed_regular_profile": "15:15 for every variable in every leaf",
            "predecessor_factorization_selftest": "PASS",
            "compact_feature_equivalence": "PASS",
            "checkpoints": checkpoints,
        },
        "best_candidate": {
            "evaluation": be,
            "left_leaf_fingerprint": best["left"].fp,
            "right_leaf_fingerprint": best["right"].fp,
            "left_profile": {str(k): list(v) for k, v in v1.polarity_profile(best["left"].leaf).items()},
            "right_profile": {str(k): list(v) for k, v in v1.polarity_profile(best["right"].leaf).items()},
            "left_leaf": [list(c) for c in best["left"].leaf],
            "right_leaf": [list(c) for c in best["right"].leaf],
            "source_cnf": [list(c) for c in v1.build_source(best["left"].leaf, best["right"].leaf)],
            "product_fingerprint": base.fingerprint(v1.build_product_global(best["left"].leaf, best["right"].leaf)),
        },
        "exact_reachability_replay": replay,
        "candidate_results": {
            "L1_ROOT_PHASE_POLYNOMIAL_GRAMMAR_TOTALITY": "REFUTED_BY_EXACT_REACHABLE_WITNESS" if l1_refuted else "OPEN_NOT_PROVED",
            "L1A_ALL_PIVOT_OVERFLOW_FORCES_FREQUENT_PAIR": "REFUTED_BY_EXACT_REACHABLE_WITNESS" if l1a_refuted else "OPEN_NOT_PROVED",
            "L1B_ALL_PIVOT_OVERFLOW_FORCES_PAIR_DENSITY": "REFUTED_BY_EXACT_REACHABLE_WITNESS" if l1b_refuted else "OPEN_NOT_PROVED",
        },
        "scientific_boundary": {
            "fixed_chassis_N_not_gamed": True,
            "signed_regular_constraint_frozen_before_results": True,
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
