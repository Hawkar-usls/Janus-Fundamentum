#!/usr/bin/env python3
"""Adversarial theorem-candidate search for the C025 root-phase gap.

The search objective is NOT SAT hardness.  It searches deterministic disjoint
selector-product sources whose exact selector residual pressures *every* live
ordinary pivot against the original root-relative N^2 cap while keeping pair
reuse below the already-proved v2 sufficient threshold.

For a candidate residual F, define

  Delta(F) = min_v ( U(exists v.F) - N^2 )

where U is the exact raw-unique state-unit charge before optional subsumption,
matching eliminate_var_capped.  During search an overflowing pivot may stop as
soon as the raw stream first exceeds N^2: that crossing is already an exact
proof that its final U is > N^2.  Therefore when every pivot crosses the cap,
Delta(F)>0 is proved even though the full gigantic U values are not materialized.

A final candidate has theorem relevance only if the unmodified frozen
PIRC_DECISION_CORE_V0_4 reaches the identical residual fingerprint at the exact
ordinary-elimination callsite.  Search ranking itself has zero theorem authority.

P_VS_NP remains OPEN.
"""
from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from copy import deepcopy
from dataclasses import dataclass
from math import comb
from typing import Iterable

from experiments.direct import janus_pirc_decision_core_v0_4 as core
from experiments.direct import janus_unified_proof_carrying_akinator_jec as base

P_VS_NP = "OPEN"


class ReachableTarget(Exception):
    pass


def equal_width_canon(rows: Iterable[Iterable[int]]) -> base.CNF:
    """Exact canonicalization for a set of clauses known to have equal width.

    Equal-width distinct clauses cannot strictly subsume one another, so after
    tautology rejection canonical CNF is exactly the sorted unique clause set.
    """
    clean: set[base.Clause] = set()
    widths: set[int] = set()
    for row in rows:
        cc = base.canon_clause(row)
        if cc is None:
            continue
        clean.add(cc)
        widths.add(len(cc))
    if len(widths) > 1:
        raise AssertionError("EQUAL_WIDTH_CANON_PRECONDITION_FAILED")
    return tuple(sorted(clean, key=lambda c: (len(c), c)))


def random_fixed_width(nvars: int, nclauses: int, width: int, seed: int) -> base.CNF:
    rng = random.Random(seed)
    rows: set[base.Clause] = set()
    attempts = 0
    while len(rows) < nclauses:
        attempts += 1
        if attempts > 2_000_000:
            raise RuntimeError("CLAUSE_GENERATION_EXHAUSTED")
        support = sorted(rng.sample(range(1, nvars + 1), width))
        clause = tuple(v if rng.getrandbits(1) else -v for v in support)
        cc = base.canon_clause(clause)
        if cc is not None:
            rows.add(cc)
    return equal_width_canon(rows)


def relabel(cnf: base.CNF, mapping: dict[int, int]) -> base.CNF:
    return equal_width_canon(
        tuple(mapping[abs(l)] if l > 0 else -mapping[abs(l)] for l in clause)
        for clause in cnf
    )


def build_selector_source(
    leaf_nvars: int,
    leaf_clauses: int,
    leaf_width: int,
    seed: int,
) -> tuple[base.CNF, base.CNF, base.CNF]:
    left0 = random_fixed_width(leaf_nvars, leaf_clauses, leaf_width, seed)
    right0 = random_fixed_width(leaf_nvars, leaf_clauses, leaf_width, seed + 1_000_003)
    left_map = {v: 1 + v for v in range(1, leaf_nvars + 1)}
    right_map = {v: 1 + leaf_nvars + v for v in range(1, leaf_nvars + 1)}
    left = relabel(left0, left_map)
    right = relabel(right0, right_map)
    source = equal_width_canon(
        [(1, *c) for c in left] + [(-1, *c) for c in right]
    )
    expected_vars = tuple(range(1, 2 * leaf_nvars + 2))
    if base.vars_of(source) != expected_vars:
        raise AssertionError("DENSE_SELECTOR_SOURCE_DRIFT")
    return source, left, right


def direct_selector_product(left: base.CNF, right: base.CNF) -> base.CNF:
    # Left and right variable supports are disjoint, so every cross-union is
    # non-tautological and all product clauses have the same width.
    return equal_width_canon([(*a, *b) for a in left for b in right])


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
    pair, count = min(
        freq.items(),
        key=lambda kv: (-kv[1], tuple((abs(z), z < 0) for z in kv[0])),
    )
    return P, int(count), pair


def raw_units_probe(cnf: base.CNF, var: int, cap: int) -> dict:
    """Exact raw-unique stream with an allowed early stop immediately over cap."""
    pos = [c for c in cnf if var in c]
    neg = [c for c in cnf if -var in c]
    retained = [c for c in cnf if var not in c and -var not in c]
    raw: set[base.Clause] = set(retained)
    raw_units = 1 + len(raw) + sum(len(c) for c in raw)
    pairs = 0
    tautologies = 0
    if raw_units > cap:
        return {
            "pivot": var,
            "overflow": True,
            "raw_units_observed": raw_units,
            "delta_lower_bound": raw_units - cap,
            "pairs_examined": 0,
            "total_parent_pairs": len(pos) * len(neg),
            "positive": len(pos),
            "negative": len(neg),
            "tautologies": 0,
            "stopped_at_first_cap_crossing": True,
        }
    for p in pos:
        for n in neg:
            pairs += 1
            r = base.resolve_on_var(p, n, var)
            if r is None:
                tautologies += 1
                continue
            if r not in raw:
                raw.add(r)
                raw_units += 1 + len(r)
                if raw_units > cap:
                    return {
                        "pivot": var,
                        "overflow": True,
                        "raw_units_observed": raw_units,
                        "delta_lower_bound": raw_units - cap,
                        "pairs_examined": pairs,
                        "total_parent_pairs": len(pos) * len(neg),
                        "positive": len(pos),
                        "negative": len(neg),
                        "tautologies": tautologies,
                        "stopped_at_first_cap_crossing": True,
                    }
    return {
        "pivot": var,
        "overflow": False,
        "raw_units_observed": raw_units,
        "delta_exact": raw_units - cap,
        "pairs_examined": pairs,
        "total_parent_pairs": len(pos) * len(neg),
        "positive": len(pos),
        "negative": len(neg),
        "tautologies": tautologies,
        "stopped_at_first_cap_crossing": False,
    }


def selftest_raw_probe() -> None:
    cnf = base.canon_cnf([[1, 2, 3], [-1, 2, 4], [1, -3, 4], [-1, 3, -4]])
    for cap in (8, 20, 1000):
        for pivot in base.vars_of(cnf):
            out, stats = base.eliminate_var_capped(cnf, pivot, cap)
            mine = raw_units_probe(cnf, pivot, cap)
            assert mine["overflow"] == (out is None)
            assert int(mine["raw_units_observed"]) == int(stats["raw_units"])


def evaluate_candidate(source: base.CNF, left: base.CNF, right: base.CNF, meta: dict) -> dict:
    N = base.input_size_units(source)
    cap = N * N
    product = direct_selector_product(left, right)
    s = base.state_units(product)
    P, tmax, pair = pair_stats(product)
    n = len(base.vars_of(product))
    frequent_threshold = s - 2 * N + 11
    density_threshold = 2 * n * (n - 1) * frequent_threshold if n >= 2 else 0
    pivots = [raw_units_probe(product, v, cap) for v in base.vars_of(product)]
    all_overflow = all(row["overflow"] for row in pivots)
    if all_overflow:
        delta_kind = "POSITIVE_PROVED_BY_EXACT_CAP_CROSSING"
        delta_value = min(int(row["delta_lower_bound"]) for row in pivots)
    else:
        # Any overflowing pivot has positive final delta, so the minimum is
        # necessarily among the fully materialized fitting pivots.
        delta_kind = "EXACT_NONPOSITIVE"
        delta_value = min(
            int(row.get("delta_exact", row.get("delta_lower_bound", 1)))
            for row in pivots
        )
    return {
        "source_meta": deepcopy(meta),
        "source_fingerprint": base.fingerprint(source),
        "product_fingerprint": base.fingerprint(product),
        "N": N,
        "state_cap": cap,
        "product_state_units": s,
        "product_clause_count": len(product),
        "live_variables": n,
        "all_pivots_overflow": all_overflow,
        "Delta_status": delta_kind,
        "Delta_value_or_strict_lower_bound": delta_value,
        "pair_incidences_P": P,
        "max_pair_frequency": tmax,
        "max_pair": list(pair) if pair is not None else None,
        "frequent_pair_threshold": frequent_threshold,
        "pair_margin": tmax - frequent_threshold,
        "pair_density_threshold": density_threshold,
        "density_margin": P - density_threshold,
        "monster_target_met_structurally": bool(all_overflow and tmax < frequent_threshold),
        "pivot_rows": pivots,
        "_source": source,
        "_product": product,
    }


def public(row: dict) -> dict:
    return {k: deepcopy(v) for k, v in row.items() if not k.startswith("_")}


def rank_key(row: dict) -> tuple:
    return (
        int(bool(row["all_pivots_overflow"])),
        int(row["Delta_value_or_strict_lower_bound"]),
        -int(row["pair_margin"]),
        -int(row["density_margin"]),
        -int(row["N"]),
    )


def verify_reachable_callsite(source: base.CNF, product: base.CNF) -> dict:
    target_fp = base.fingerprint(product)
    original_first = base.first_capped_elimination
    hit: dict | None = None

    def wrapped_first(state: base.EngineState, cnf_arg=None, roots_only: bool = False):
        nonlocal hit
        if cnf_arg is None and not roots_only and base.fingerprint(state.residual) == target_fp:
            hit = {
                "reachable_state_fingerprint": target_fp,
                "N": int(state.N),
                "state_cap": int(state.state_cap),
                "state_units": int(base.state_units(state.residual)),
                "root_variables_live": sum(
                    1 for v in state.root_vars if v in set(base.vars_of(state.residual))
                ),
                "event_prefix": deepcopy(state.ledger.events),
            }
            raise ReachableTarget()
        return original_first(state, cnf_arg, roots_only)

    base.first_capped_elimination = wrapped_first
    try:
        try:
            terminal = core.solve_decision_core(source)
        except ReachableTarget:
            terminal = None
    finally:
        base.first_capped_elimination = original_first

    if hit is not None:
        return {
            "reachable_at_frozen_ordinary_callsite": True,
            "observation": hit,
            "terminal_before_target": None,
        }
    return {
        "reachable_at_frozen_ordinary_callsite": False,
        "observation": None,
        "terminal_before_target": {
            "status": terminal.get("status") if terminal else None,
            "reason": terminal.get("reason") if terminal else None,
            "residual_fingerprint": terminal.get("residual_fingerprint") if terminal else None,
        },
    }


def parse_int_list(text: str) -> list[int]:
    out = [int(x.strip()) for x in text.split(",") if x.strip()]
    if not out:
        raise ValueError("empty integer list")
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--leaf-nvars", type=int, default=8)
    parser.add_argument("--leaf-width", type=int, default=4)
    parser.add_argument("--leaf-clauses", default="64,72,80,88")
    parser.add_argument("--seeds-per-rung", type=int, default=1)
    parser.add_argument("--seed0", type=int, default=28100)
    args = parser.parse_args()
    if args.seeds_per_rung < 1:
        raise ValueError("seeds-per-rung must be positive")

    selftest_raw_probe()
    # Fast exact equivalence gate for equal-width canonicalization.
    tiny = random_fixed_width(6, 10, 3, 27001)
    assert tiny == base.canon_cnf(tiny)

    schedule = parse_int_list(args.leaf_clauses)
    rows: list[dict] = []
    first_monster: dict | None = None
    ordinal = 0
    for m in schedule:
        for offset in range(args.seeds_per_rung):
            seed = args.seed0 + 1000 * ordinal + offset
            meta = {
                "family": "DISJOINT_SELECTOR_PRODUCT",
                "leaf_nvars": args.leaf_nvars,
                "leaf_width": args.leaf_width,
                "leaf_clauses": m,
                "seed": seed,
                "schedule_ordinal": ordinal,
            }
            source, left, right = build_selector_source(
                args.leaf_nvars, m, args.leaf_width, seed
            )
            row = evaluate_candidate(source, left, right, meta)
            rows.append(row)
            if row["monster_target_met_structurally"]:
                first_monster = row
                break
        ordinal += 1
        if first_monster is not None:
            break

    champion = first_monster if first_monster is not None else max(rows, key=rank_key)
    reachability = verify_reachable_callsite(champion["_source"], champion["_product"])
    reachable_monster = bool(
        reachability["reachable_at_frozen_ordinary_callsite"]
        and champion["monster_target_met_structurally"]
    )
    l1a_refuted = reachable_monster
    l1b_refuted = bool(
        reachability["reachable_at_frozen_ordinary_callsite"]
        and champion["all_pivots_overflow"]
        and champion["density_margin"] < 0
    )

    report = {
        "schema": "JANUS/C025/ADVERSARIAL-DELTA-PAIR-SEARCH/v1",
        "status": (
            "REACHABLE_ALL_PIVOT_OVERFLOW_PAIR_DISPERSED_FOUND"
            if reachable_monster
            else "NO_REACHABLE_MONSTER_IN_FROZEN_SEARCH__NOT_PROOF"
        ),
        "fixed_algorithm": "PIRC_DECISION_CORE_V0_4",
        "frozen_schedule": {
            "leaf_nvars": args.leaf_nvars,
            "leaf_width": args.leaf_width,
            "leaf_clause_schedule": schedule,
            "seeds_per_rung": args.seeds_per_rung,
            "seed0": args.seed0,
            "stop_rule": "STOP_AT_FIRST_STRUCTURAL_MONSTER_THEN_REQUIRE_FROZEN_REACHABILITY_REPLAY",
        },
        "candidates_evaluated": len(rows),
        "candidates": [public(r) for r in rows],
        "champion": {
            **public(champion),
            "source_cnf": [list(c) for c in champion["_source"]],
            "reachable_product_cnf_included": False,
        },
        "reachability_replay": reachability,
        "candidate_results": {
            "L1A_ALL_PIVOT_OVERFLOW_FORCES_FREQUENT_PAIR": {
                "bounded_status": "REFUTED_BY_REACHABLE_WITNESS" if l1a_refuted else "NOT_REFUTED_BY_THIS_SEARCH__NOT_PROVED",
            },
            "L1B_ALL_PIVOT_OVERFLOW_FORCES_PAIR_DENSITY": {
                "bounded_status": "REFUTED_BY_REACHABLE_WITNESS" if l1b_refuted else "NOT_REFUTED_BY_THIS_SEARCH__NOT_PROVED",
            },
            "L1_ROOT_PHASE_POLYNOMIAL_GRAMMAR_TOTALITY": {
                "bounded_status": "NOT_DECIDED_HERE__EXACT_V2_GATE_REQUIRED_AFTER_MONSTER" if reachable_monster else "NOT_REFUTED_BY_THIS_SEARCH__NOT_PROVED",
            },
        },
        "next_gate": (
            "RUN_FROZEN_EXHAUSTIVE_V2_ON_REACHABLE_MONSTER"
            if reachable_monster
            else "EXPAND_ADVERSARIAL_SOURCE_FAMILY_OR_SCHEDULE_WITHOUT_CHANGING_THEOREM_TARGET"
        ),
        "scientific_boundary": {
            "bounded_finite_falsification_only": True,
            "search_ranking_has_theorem_authority": False,
            "Delta_positive_requires_all_exact_cap_crossings": True,
            "reachability_requires_frozen_core_callsite_replay": True,
            "L1_not_refuted_without_exact_v2_failure": True,
            "absence_of_monster_is_not_proof": True,
            "P2_REACHABLE_PRESERVATION": "OPEN",
            "P_VS_NP": P_VS_NP,
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
