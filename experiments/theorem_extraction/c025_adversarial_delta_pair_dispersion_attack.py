#!/usr/bin/env python3
"""Adversarial theorem-candidate search for the C025 root grammar gap.

Search objective is frozen before execution:

  DELTA(F) = min_v (U_raw(exists v . F) - N^2)  -> maximize
  PAIR_MARGIN(F) = t_max - (state_units(F)-2*N+11) -> minimize

The search uses a fixed selector-product chassis so N cannot be gamed by changing
input representation size.  Candidate generation is not theorem authority.  A
candidate can refute L1/L1A/L1B only after exact replay shows that the target
state is actually reached by frozen PIRC_DECISION_CORE_V0_4.

The factorized raw-unit formula used for search is exact for the selector-product
state and is self-tested against brute raw resolution before search.
P_VS_NP remains OPEN.
"""
from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from copy import deepcopy
from itertools import combinations_with_replacement
from math import comb

from experiments.direct import janus_pirc_decision_core_v0_4 as core
from experiments.direct import janus_unified_proof_carrying_akinator_jec as base

P_VS_NP = "OPEN"
LEAF_NVARS = 6
LEAF_CLAUSES = 60
LEAF_WIDTH = 3
MIN_POLARITY = 8
SELECTOR = 1
LEFT_FIRST = 2
RIGHT_FIRST = 2 + LEAF_NVARS
EXPECTED_SOURCE_VARS = 1 + 2 * LEAF_NVARS
EXPECTED_SOURCE_CLAUSES = 2 * LEAF_CLAUSES
EXPECTED_SOURCE_WIDTH = LEAF_WIDTH + 1


def random_clause(rng: random.Random) -> base.Clause:
    support = sorted(rng.sample(range(1, LEAF_NVARS + 1), LEAF_WIDTH))
    raw = tuple(v if rng.getrandbits(1) else -v for v in support)
    cc = base.canon_clause(raw)
    if cc is None:
        raise AssertionError("UNEXPECTED_TAUTOLOGY_FROM_DISTINCT_SUPPORT")
    return cc


def polarity_profile(leaf: base.CNF) -> dict[int, tuple[int, int]]:
    return {
        v: (
            sum(1 for c in leaf if v in c),
            sum(1 for c in leaf if -v in c),
        )
        for v in range(1, LEAF_NVARS + 1)
    }


def balanced_leaf(leaf: base.CNF) -> bool:
    if len(leaf) != LEAF_CLAUSES:
        return False
    if base.vars_of(leaf) != tuple(range(1, LEAF_NVARS + 1)):
        return False
    return all(p >= MIN_POLARITY and q >= MIN_POLARITY for p, q in polarity_profile(leaf).values())


def random_leaf(seed: int) -> base.CNF:
    rng = random.Random(seed)
    for _restart in range(100):
        rows: set[base.Clause] = set()
        while len(rows) < LEAF_CLAUSES:
            rows.add(random_clause(rng))
        leaf = tuple(sorted(rows, key=lambda c: (len(c), c)))
        if balanced_leaf(leaf):
            return leaf
    raise RuntimeError("FAILED_TO_GENERATE_BALANCED_FIXED_CHASSIS_LEAF")


def mutate_leaf(leaf: base.CNF, rng: random.Random, changes: int) -> base.CNF:
    rows = set(leaf)
    for _ in range(changes):
        old = rng.choice(tuple(rows))
        rows.remove(old)
        for _attempt in range(500):
            new = random_clause(rng)
            if new not in rows:
                rows.add(new)
                break
        else:
            raise RuntimeError("MUTATION_CLAUSE_GENERATION_EXHAUSTED")
    out = tuple(sorted(rows, key=lambda c: (len(c), c)))
    return out if balanced_leaf(out) else leaf


def relabel_leaf(leaf: base.CNF, first: int) -> base.CNF:
    mapping = {v: first + v - 1 for v in range(1, LEAF_NVARS + 1)}
    return tuple(
        tuple(sorted((mapping[abs(l)] if l > 0 else -mapping[abs(l)] for l in c), key=lambda z: (abs(z), z < 0)))
        for c in leaf
    )


def build_source(left: base.CNF, right: base.CNF) -> base.CNF:
    gl = relabel_leaf(left, LEFT_FIRST)
    gr = relabel_leaf(right, RIGHT_FIRST)
    rows = [(SELECTOR, *c) for c in gl]
    rows += [(-SELECTOR, *c) for c in gr]
    source = base.canon_cnf(rows)
    if len(source) != EXPECTED_SOURCE_CLAUSES:
        raise AssertionError("FIXED_CHASSIS_SOURCE_CLAUSE_COUNT_DRIFT")
    if len(base.vars_of(source)) != EXPECTED_SOURCE_VARS:
        raise AssertionError("FIXED_CHASSIS_SOURCE_VARIABLE_COUNT_DRIFT")
    if any(len(c) != EXPECTED_SOURCE_WIDTH for c in source):
        raise AssertionError("FIXED_CHASSIS_SOURCE_WIDTH_DRIFT")
    return source


def build_product_global(left: base.CNF, right: base.CNF) -> base.CNF:
    gl = relabel_leaf(left, LEFT_FIRST)
    gr = relabel_leaf(right, RIGHT_FIRST)
    rows = []
    for a in gl:
        for b in gr:
            cc = base.canon_clause((*a, *b))
            if cc is None:
                raise AssertionError("DISJOINT_PRODUCT_TAUTOLOGY")
            rows.append(cc)
    # All clauses have equal width and left/right projections are unique, hence
    # there are no duplicates or strict subsumptions.  This is canon_cnf exactly.
    out = tuple(sorted(rows, key=lambda c: (len(c), c)))
    if len(out) != len(left) * len(right):
        raise AssertionError("PRODUCT_UNIQUENESS_DRIFT")
    return out


def leaf_resolution_set(leaf: base.CNF, pivot: int) -> set[base.Clause]:
    pos = [c for c in leaf if pivot in c]
    neg = [c for c in leaf if -pivot in c]
    out: set[base.Clause] = set()
    for p in pos:
        for n in neg:
            r = base.resolve_on_var(p, n, pivot)
            if r is not None:
                out.add(r)
    return out


def pair_union_set(leaf: base.CNF) -> set[base.Clause]:
    out: set[base.Clause] = set()
    for a, b in combinations_with_replacement(leaf, 2):
        cc = base.canon_clause((*a, *b))
        if cc is not None:
            out.add(cc)
    return out


def factorized_raw_units_left_pivot(left: base.CNF, right: base.CNF, pivot: int,
                                    right_unions: set[base.Clause] | None = None) -> int:
    """Exact pre-subsumption raw units after eliminating a left-side pivot.

    Product state is L x R with disjoint variable sets.  Every non-tautological
    resolvent factors uniquely as r_L union u_R, where r_L is a unique leaf
    resolvent and u_R is a unique non-tautological union of two R clauses.
    """
    retained = {c for c in left if pivot not in c and -pivot not in c}
    rleft = leaf_resolution_set(left, pivot)
    uright = right_unions if right_unions is not None else pair_union_set(right)
    right_set = set(right)

    ret_count = len(retained) * len(right)
    ret_width = len(right) * sum(map(len, retained)) + len(retained) * sum(map(len, right))

    res_count = len(rleft) * len(uright)
    res_width = len(uright) * sum(map(len, rleft)) + len(rleft) * sum(map(len, uright))

    # A factorized resolvent duplicates a retained product clause iff both
    # projections duplicate their corresponding retained/original projections.
    dup_left = rleft & retained
    dup_right = uright & right_set
    dup_count = len(dup_left) * len(dup_right)
    dup_width = len(dup_right) * sum(map(len, dup_left)) + len(dup_left) * sum(map(len, dup_right))

    return 1 + (ret_count + res_count - dup_count) + (ret_width + res_width - dup_width)


def brute_raw_units(cnf: base.CNF, pivot: int) -> int:
    pos = [c for c in cnf if pivot in c]
    neg = [c for c in cnf if -pivot in c]
    raw: set[base.Clause] = {c for c in cnf if pivot not in c and -pivot not in c}
    for p in pos:
        for n in neg:
            r = base.resolve_on_var(p, n, pivot)
            if r is not None:
                raw.add(r)
    return 1 + len(raw) + sum(map(len, raw))


def direct_pair_stats(cnf: base.CNF) -> tuple[int, int]:
    freq: Counter[tuple[int, int]] = Counter()
    P = 0
    for c in cnf:
        P += comb(len(c), 2)
        for i in range(len(c)):
            for j in range(i + 1, len(c)):
                a, b = c[i], c[j]
                if abs(a) == abs(b):
                    continue
                pair = tuple(sorted((a, b), key=lambda z: (abs(z), z < 0)))
                freq[pair] += 1
    return P, max(freq.values(), default=0)


def leaf_pair_frequency(leaf: base.CNF) -> int:
    freq: Counter[tuple[int, int]] = Counter()
    for c in leaf:
        for i in range(len(c)):
            for j in range(i + 1, len(c)):
                pair = tuple(sorted((c[i], c[j]), key=lambda z: (abs(z), z < 0)))
                freq[pair] += 1
    return max(freq.values(), default=0)


def literal_counts(leaf: base.CNF) -> Counter[int]:
    out: Counter[int] = Counter()
    for c in leaf:
        out.update(c)
    return out


def factorized_product_pair_stats(left: base.CNF, right: base.CNF) -> tuple[int, int]:
    # Every product clause has width 2*LEAF_WIDTH.
    P = len(left) * len(right) * comb(2 * LEAF_WIDTH, 2)
    within_left = leaf_pair_frequency(left) * len(right)
    within_right = leaf_pair_frequency(right) * len(left)
    lc = literal_counts(left)
    rc = literal_counts(right)
    cross = max((a * b for a in lc.values() for b in rc.values()), default=0)
    return P, max(within_left, within_right, cross)


def selftest_factorization() -> None:
    # Smaller leafs make brute replay cheap while exercising identical algebra.
    rng = random.Random(7001701)
    def tiny() -> base.CNF:
        rows: set[base.Clause] = set()
        while len(rows) < 8:
            rows.add(random_clause(rng))
        return tuple(sorted(rows, key=lambda c: (len(c), c)))
    left, right = tiny(), tiny()
    gl = relabel_leaf(left, LEFT_FIRST)
    gr = relabel_leaf(right, RIGHT_FIRST)
    product = tuple(sorted((base.canon_clause((*a, *b)) for a in gl for b in gr), key=lambda c: (len(c), c)))
    ru = pair_union_set(right)
    lu = pair_union_set(left)
    for local_v in range(1, LEAF_NVARS + 1):
        got_left = factorized_raw_units_left_pivot(left, right, local_v, ru)
        want_left = brute_raw_units(product, LEFT_FIRST + local_v - 1)
        if got_left != want_left:
            raise AssertionError(("LEFT_FACTORIZATION_MISMATCH", local_v, got_left, want_left))
        got_right = factorized_raw_units_left_pivot(right, left, local_v, lu)
        want_right = brute_raw_units(product, RIGHT_FIRST + local_v - 1)
        if got_right != want_right:
            raise AssertionError(("RIGHT_FACTORIZATION_MISMATCH", local_v, got_right, want_right))
    got_pair = factorized_product_pair_stats(left, right)
    want_pair = direct_pair_stats(product)
    if got_pair != want_pair:
        raise AssertionError(("PAIR_FACTORIZATION_MISMATCH", got_pair, want_pair))


def evaluate(left: base.CNF, right: base.CNF) -> dict:
    source = build_source(left, right)
    N = base.input_size_units(source)
    cap = N * N
    product_units = 1 + len(left) * len(right) + len(left) * len(right) * (2 * LEAF_WIDTH)
    left_unions = pair_union_set(left)
    right_unions = pair_union_set(right)
    raws: list[int] = []
    rows = []
    for v in range(1, LEAF_NVARS + 1):
        u = factorized_raw_units_left_pivot(left, right, v, right_unions)
        raws.append(u)
        rows.append({"side": "L", "pivot": v, "raw_units": u, "margin": u - cap})
    for v in range(1, LEAF_NVARS + 1):
        u = factorized_raw_units_left_pivot(right, left, v, left_unions)
        raws.append(u)
        rows.append({"side": "R", "pivot": v, "raw_units": u, "margin": u - cap})
    P, tmax = factorized_product_pair_stats(left, right)
    frequent_threshold = product_units - 2 * N + 11
    n_live = 2 * LEAF_NVARS
    density_threshold = 2 * n_live * (n_live - 1) * frequent_threshold
    delta = min(raws) - cap
    pair_margin = tmax - frequent_threshold
    density_margin = P - density_threshold
    return {
        "N": N,
        "cap": cap,
        "product_state_units": product_units,
        "delta": delta,
        "min_raw_units": min(raws),
        "mean_raw_units": sum(raws) / len(raws),
        "max_raw_units": max(raws),
        "all_pivot_overflow": delta > 0,
        "pair_incidences_P": P,
        "max_pair_frequency": tmax,
        "frequent_pair_threshold": frequent_threshold,
        "pair_rescue_margin": pair_margin,
        "pair_dispersed": pair_margin < 0,
        "pair_density_threshold": density_threshold,
        "pair_density_margin": density_margin,
        "pair_density_dispersed": density_margin < 0,
        "pivot_rows": rows,
        "source_fingerprint": base.fingerprint(source),
    }


def rank_key(item: dict) -> tuple:
    e = item["eval"]
    # Primary objective is the maximin ordinary raw margin.  Pair dispersion is
    # secondary exactly as preregistered.  Mean pressure breaks remaining ties.
    return (int(e["delta"]), -int(e["pair_rescue_margin"]), float(e["mean_raw_units"]))


def exact_reachability_replay(left: base.CNF, right: base.CNF, expected: dict) -> dict:
    source = build_source(left, right)
    target = build_product_global(left, right)
    target_fp = base.fingerprint(target)
    original_first = base.first_capped_elimination
    original_v2 = core.v2.discover_macro_restore_v2
    observation = {
        "target_fingerprint": target_fp,
        "target_seen_at_ordinary_callsite": False,
        "all_ordinary_pivots_overflow_at_target": None,
        "v2_called_on_target": False,
        "v2_rescue_exists": None,
        "v2_rescue": None,
    }

    def wrapped_first(state: base.EngineState, cnf_arg=None, roots_only: bool = False):
        is_target = cnf_arg is None and not roots_only and base.fingerprint(state.residual) == target_fp
        if is_target:
            observation["target_seen_at_ordinary_callsite"] = True
        result = original_first(state, cnf_arg, roots_only)
        if is_target:
            observation["all_ordinary_pivots_overflow_at_target"] = result is None
        return result

    def wrapped_v2(state: base.EngineState):
        is_target = base.fingerprint(state.residual) == target_fp
        if is_target:
            observation["v2_called_on_target"] = True
        result = original_v2(state)
        if is_target:
            observation["v2_rescue_exists"] = result is not None
            if result is not None:
                macro_cnf, pivot, after, cert, stats = result
                observation["v2_rescue"] = {
                    "pair": list(cert.get("represents", [])),
                    "reused_occurrences": cert.get("reused_occurrences"),
                    "root_pivot": int(pivot),
                    "macro_state_units": base.state_units(macro_cnf),
                    "after_state_units": base.state_units(after),
                    "elimination_raw_units": int(stats.get("raw_units", 0)),
                }
        return result

    base.first_capped_elimination = wrapped_first
    core.v2.discover_macro_restore_v2 = wrapped_v2
    try:
        result = core.solve_decision_core(source)
    finally:
        base.first_capped_elimination = original_first
        core.v2.discover_macro_restore_v2 = original_v2

    first_selector_event = next(
        (e for e in result.get("events", []) if e.get("kind") == "AKINATOR_EXACT_ELIMINATION"),
        None,
    )
    observation.update({
        "core_status": result["status"],
        "core_reason": result["reason"],
        "core_missing_bridge": result.get("missing_bridge"),
        "first_exact_elimination": deepcopy(first_selector_event),
        "selector_reaches_target": bool(
            first_selector_event
            and int(first_selector_event.get("pivot", -1)) == SELECTOR
            and first_selector_event.get("after_fingerprint") == target_fp
        ),
        "event_kinds": [e.get("kind") for e in result.get("events", [])],
        "max_state_units": int(result["ledger"]["max_state_units"]),
    })
    if observation["target_seen_at_ordinary_callsite"] and expected["all_pivot_overflow"]:
        if observation["all_ordinary_pivots_overflow_at_target"] is not True:
            raise AssertionError("FACTORIZED_DELTA_DISAGREES_WITH_FROZEN_CAPPED_ELIMINATION")
    return observation


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--population", type=int, default=18)
    parser.add_argument("--generations", type=int, default=30)
    parser.add_argument("--seed", type=int, default=26082801)
    args = parser.parse_args()
    if args.population < 4 or args.generations < 1:
        raise ValueError("population>=4 and generations>=1 required")

    selftest_factorization()
    master = random.Random(args.seed)
    cache: dict[tuple[str, str], dict] = {}

    def leaf_fp(leaf: base.CNF) -> str:
        return base.fingerprint(leaf)

    def scored(left: base.CNF, right: base.CNF) -> dict:
        key = (leaf_fp(left), leaf_fp(right))
        if key not in cache:
            cache[key] = evaluate(left, right)
        return {"left": left, "right": right, "eval": cache[key]}

    population = []
    for i in range(args.population):
        population.append(scored(random_leaf(args.seed + 1000 + 2 * i), random_leaf(args.seed + 1001 + 2 * i)))

    trace = []
    best = None
    for gen in range(args.generations + 1):
        population.sort(key=rank_key, reverse=True)
        champion = population[0]
        if best is None or rank_key(champion) > rank_key(best):
            best = champion
        e = champion["eval"]
        trace.append({
            "generation": gen,
            "delta": int(e["delta"]),
            "min_raw_units": int(e["min_raw_units"]),
            "cap": int(e["cap"]),
            "pair_rescue_margin": int(e["pair_rescue_margin"]),
            "max_pair_frequency": int(e["max_pair_frequency"]),
            "pair_threshold": int(e["frequent_pair_threshold"]),
            "all_pivot_overflow": bool(e["all_pivot_overflow"]),
            "pair_dispersed": bool(e["pair_dispersed"]),
            "source_fingerprint": e["source_fingerprint"],
        })
        if e["all_pivot_overflow"] and e["pair_dispersed"]:
            best = champion
            break
        if gen == args.generations:
            break

        elites = population[: max(2, args.population // 4)]
        children = list(elites)
        while len(children) < args.population:
            parent = master.choice(elites)
            left, right = parent["left"], parent["right"]
            changes = 1 if gen < args.generations // 2 else 2
            if master.getrandbits(1):
                left = mutate_leaf(left, master, changes)
            else:
                right = mutate_leaf(right, master, changes)
            # Occasionally mutate both sides to escape local maximin plateaus.
            if master.random() < 0.20:
                left = mutate_leaf(left, master, 1)
                right = mutate_leaf(right, master, 1)
            children.append(scored(left, right))
        population = children

    assert best is not None
    be = best["eval"]
    candidate_found = bool(be["all_pivot_overflow"] and be["pair_dispersed"])
    replay = exact_reachability_replay(best["left"], best["right"], be) if candidate_found else None

    l1a_refuted = bool(
        candidate_found and replay
        and replay["selector_reaches_target"]
        and replay["target_seen_at_ordinary_callsite"]
        and replay["all_ordinary_pivots_overflow_at_target"] is True
        and be["pair_rescue_margin"] < 0
    )
    l1b_refuted = bool(
        l1a_refuted and be["pair_density_margin"] < 0
    )
    l1_refuted = bool(
        l1a_refuted and replay
        and replay["v2_called_on_target"]
        and replay["v2_rescue_exists"] is False
    )

    report = {
        "schema": "JANUS/C025/ADVERSARIAL-DELTA-PAIR-DISPERSION-ATTACK/v1",
        "status": (
            "L1_REACHABLE_COUNTEREXAMPLE_FOUND" if l1_refuted
            else "L1A_REACHABLE_COUNTEREXAMPLE_FOUND" if l1a_refuted
            else "DIRECT_CANDIDATE_FOUND_BUT_REACHABILITY_GATE_FAILED" if candidate_found
            else "NO_ALL_PIVOT_OVERFLOW_CANDIDATE_IN_BOUNDED_SEARCH"
        ),
        "fixed_algorithm": "PIRC_DECISION_CORE_V0_4",
        "search": {
            "population": args.population,
            "generations_requested": args.generations,
            "generations_executed": trace[-1]["generation"],
            "seed": args.seed,
            "unique_candidates_evaluated": len(cache),
            "fixed_chassis": {
                "leaf_variables": LEAF_NVARS,
                "leaf_clauses": LEAF_CLAUSES,
                "leaf_width": LEAF_WIDTH,
                "source_variables": EXPECTED_SOURCE_VARS,
                "source_clauses": EXPECTED_SOURCE_CLAUSES,
                "source_width": EXPECTED_SOURCE_WIDTH,
            },
            "factorized_exact_semantics_selftest": "PASS",
            "trace": trace,
        },
        "best_candidate": {
            "evaluation": be,
            "left_profile": {str(k): list(v) for k, v in polarity_profile(best["left"]).items()},
            "right_profile": {str(k): list(v) for k, v in polarity_profile(best["right"]).items()},
            "left_leaf": [list(c) for c in best["left"]],
            "right_leaf": [list(c) for c in best["right"]],
            "source_cnf": [list(c) for c in build_source(best["left"], best["right"])],
            "product_fingerprint": base.fingerprint(build_product_global(best["left"], best["right"])),
        },
        "exact_reachability_replay": replay,
        "candidate_results": {
            "L1_ROOT_PHASE_POLYNOMIAL_GRAMMAR_TOTALITY": "REFUTED_BY_EXACT_REACHABLE_WITNESS" if l1_refuted else "OPEN_NOT_PROVED",
            "L1A_ALL_PIVOT_OVERFLOW_FORCES_FREQUENT_PAIR": "REFUTED_BY_EXACT_REACHABLE_WITNESS" if l1a_refuted else "OPEN_NOT_PROVED",
            "L1B_ALL_PIVOT_OVERFLOW_FORCES_PAIR_DENSITY": "REFUTED_BY_EXACT_REACHABLE_WITNESS" if l1b_refuted else "OPEN_NOT_PROVED",
        },
        "scientific_boundary": {
            "search_score_is_not_proof": True,
            "factorized_direct_product_is_candidate_generation_only": True,
            "final_refutation_requires_frozen_core_reachability": True,
            "absence_of_counterexample_is_not_proof": True,
            "same_run_theorem_promotion": False,
            "models_or_heuristics_have_theorem_authority": False,
            "P2_REACHABLE_PRESERVATION": "OPEN",
            "P_VS_NP": P_VS_NP,
        },
        "P_VS_NP": P_VS_NP,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
