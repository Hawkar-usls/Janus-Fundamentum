#!/usr/bin/env python3
"""Hostile local search against the pivot-involving v2 rescue candidate L1C.

For the fixed signed-regular selector-product chassis, generator intersections
factor exactly across the disjoint leaf and opposite-block union factors.  This
script computes the weighted unique-new resolvent mass with EMPTY oriented
positive/negative generator intersection, validates that factorization against a
full 3600-clause brute exact product replay on the frozen witness, then searches
near that witness for all-pivot-overflow states with more unfactorable mass.

Search score has no theorem authority.  The final champion is evaluated by the
actual frozen exhaustive v2 routine, and any v2-denial candidate requires full
frozen-core reachability replay before L1 can be refuted.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_unified_macro_restore_v2 as v2
from experiments.theorem_extraction import c025_adversarial_delta_pair_dispersion_attack as build
from experiments.theorem_extraction import c025_signed_regular_balanced_delta_attack as slow
from experiments.theorem_extraction import c025_signed_regular_balanced_delta_attack_fast as fast
from experiments.theorem_extraction import c025_sign_collision_local_delta_attack as local

P_VS_NP = "OPEN"
WITNESS_PATH = Path("research/C025_L1A_L1B_WITNESS_CNF_2026-08-28.json")
N = 614
CAP = N * N
EXPECTED_SOURCE = "03506158fa7d60deb18f1832f1733e27f511d354024aff21f7afd33e27935b0f"
EXPECTED_PRODUCT = "3559df2656aade8e446d3a5eeedd419578fcebcf07ebecd35b2556ae35f68089"


@dataclass(frozen=True)
class MassSummary:
    count: int
    width_sum: int
    retained_count: int
    retained_width_sum: int


@dataclass
class GeneratorFeature:
    leaf: base.CNF
    fp: str
    standard: slow.LeafFeature
    union_all: MassSummary
    union_empty: MassSummary
    pivots: dict[tuple[int, bool], tuple[MassSummary, MassSummary]]
    # pivots[(v,orientation)] = (all_resolvents, empty_intersection_resolvents)


def intersect_update(old: set[int] | None, current: set[int]) -> set[int]:
    return set(current) if old is None else old & current


def oriented_leaf_resolvent_intersections(leaf: base.CNF, pivot: int, positive: bool) -> dict[base.Clause, frozenset[int]]:
    lit = pivot if positive else -pivot
    anti = -lit
    oriented = [c for c in leaf if lit in c]
    opposite = [c for c in leaf if anti in c]
    intersections: dict[base.Clause, set[int] | None] = {}
    for p in oriented:
        co = set(p) - {lit}
        for n in opposite:
            r = base.resolve_on_var(p, n, pivot)
            if r is None:
                continue
            intersections[r] = intersect_update(intersections.get(r), co)
    return {r: frozenset(xs or ()) for r, xs in intersections.items()}


def union_generator_intersections(leaf: base.CNF) -> dict[base.Clause, frozenset[int]]:
    intersections: dict[base.Clause, set[int] | None] = {}
    # Ordered pairs matter: the first clause belongs to the oriented product parent.
    for a in leaf:
        aset = set(a)
        for b in leaf:
            u = base.canon_clause((*a, *b))
            if u is None:
                continue
            intersections[u] = intersect_update(intersections.get(u), aset)
    return {u: frozenset(xs or ()) for u, xs in intersections.items()}


def summarize(rows: set[base.Clause], retained: set[base.Clause]) -> MassSummary:
    overlap = rows & retained
    return MassSummary(
        count=len(rows),
        width_sum=sum(map(len, rows)),
        retained_count=len(overlap),
        retained_width_sum=sum(map(len, overlap)),
    )


def standard_feature_from_leaf(leaf: base.CNF, tag: int) -> slow.LeafFeature:
    return local.feature_from_leaf(leaf, tag)


def generator_feature(leaf: base.CNF, tag: int) -> GeneratorFeature:
    std = standard_feature_from_leaf(leaf, tag)
    unions = union_generator_intersections(leaf)
    uall = set(unions)
    uempty = {u for u, inter in unions.items() if not inter}
    leaf_set = set(leaf)
    pivots = {}
    for pivot in slow.VARS:
        retained = {c for c in leaf if pivot not in c and -pivot not in c}
        for positive in (True, False):
            rmap = oriented_leaf_resolvent_intersections(leaf, pivot, positive)
            rall = set(rmap)
            rempty = {r for r, inter in rmap.items() if not inter}
            pivots[(pivot, positive)] = (summarize(rall, retained), summarize(rempty, retained))
    return GeneratorFeature(
        leaf=leaf,
        fp=base.fingerprint(leaf),
        standard=std,
        union_all=summarize(uall, leaf_set),
        union_empty=summarize(uempty, leaf_set),
        pivots=pivots,
    )


def cartesian_weight(a_count: int, a_width: int, b_count: int, b_width: int) -> int:
    return a_count * b_count + b_count * a_width + a_count * b_width


def product_unique_new_mass(a: MassSummary, b: MassSummary) -> tuple[int, int]:
    total_count = a.count * b.count - a.retained_count * b.retained_count
    total_mass = cartesian_weight(a.count, a.width_sum, b.count, b.width_sum)
    duplicate_mass = cartesian_weight(
        a.retained_count, a.retained_width_sum,
        b.retained_count, b.retained_width_sum,
    )
    return total_count, total_mass - duplicate_mass


def factorized_orientation_mass(pivot_leaf: GeneratorFeature, other_leaf: GeneratorFeature,
                                pivot: int, positive: bool) -> dict:
    rall, rempty = pivot_leaf.pivots[(pivot, positive)]
    total_count, total_mass = product_unique_new_mass(rall, other_leaf.union_all)
    empty_count, empty_mass = product_unique_new_mass(rempty, other_leaf.union_empty)
    if empty_mass > total_mass or empty_count > total_count:
        raise AssertionError("UNFACTORABLE_MASS_EXCEEDS_TOTAL")
    return {
        "local_pivot": pivot,
        "orientation": "+" if positive else "-",
        "unique_new_resolvent_count": total_count,
        "unique_new_resolvent_mass": total_mass,
        "empty_intersection_count": empty_count,
        "empty_intersection_mass": empty_mass,
        "factorable_mass": total_mass - empty_mass,
        "empty_fraction": empty_mass / max(1, total_mass),
    }


def pair_generator_landscape(left: GeneratorFeature, right: GeneratorFeature) -> dict:
    rows = []
    for pivot in slow.VARS:
        for positive in (True, False):
            row = factorized_orientation_mass(left, right, pivot, positive)
            row["side"] = "L"
            rows.append(row)
    for pivot in slow.VARS:
        for positive in (True, False):
            row = factorized_orientation_mass(right, left, pivot, positive)
            row["side"] = "R"
            rows.append(row)
    return {
        "rows": rows,
        "min_empty_mass": min(r["empty_intersection_mass"] for r in rows),
        "max_empty_mass": max(r["empty_intersection_mass"] for r in rows),
        "mean_empty_mass": sum(r["empty_intersection_mass"] for r in rows) / len(rows),
        "min_empty_fraction": min(r["empty_fraction"] for r in rows),
        "max_factorable_mass": max(r["factorable_mass"] for r in rows),
        "mean_factorable_mass": sum(r["factorable_mass"] for r in rows) / len(rows),
    }


def brute_product_orientation(product: base.CNF, pivot: int, positive: bool) -> dict:
    lit = pivot if positive else -pivot
    anti = -lit
    oriented = [c for c in product if lit in c]
    opposite = [c for c in product if anti in c]
    retained = {c for c in product if pivot not in c and -pivot not in c}
    inter: dict[base.Clause, set[int] | None] = {}
    for p in oriented:
        co = set(p) - {lit}
        for n in opposite:
            r = base.resolve_on_var(p, n, pivot)
            if r is None:
                continue
            inter[r] = intersect_update(inter.get(r), co)
    unique_new = {r for r in inter if r not in retained}
    empty = {r for r in unique_new if not (inter[r] or set())}
    return {
        "unique_new_resolvent_count": len(unique_new),
        "unique_new_resolvent_mass": sum(1 + len(r) for r in unique_new),
        "empty_intersection_count": len(empty),
        "empty_intersection_mass": sum(1 + len(r) for r in empty),
    }


def exact_v2_eval(left: GeneratorFeature, right: GeneratorFeature) -> dict:
    source = build.build_source(left.leaf, right.leaf)
    product = build.build_product_global(left.leaf, right.leaf)
    if base.input_size_units(source) != N:
        raise AssertionError("FIXED_N_DRIFT")
    state = base.EngineState(
        root=source, residual=product, fixed_assignment={}, root_vars=base.vars_of(source),
        extension_defs=[], elimination_history=[], seen=set(), N=N,
        cap_exponent=2, extension_exponent=2, ledger=base.Ledger(),
    )
    out = v2.discover_macro_restore_v2(state)
    if out is None:
        return {"rescue_exists": False, "rescue_slack": None, "pair": None, "root_pivot": None, "raw_units": None}
    macro, root, after, cert, stats = out
    raw = int(stats["raw_units"])
    return {
        "rescue_exists": True,
        "rescue_slack": CAP - raw,
        "pair": list(cert["represents"]),
        "root_pivot": int(root),
        "raw_units": raw,
        "macro_state_units": base.state_units(macro),
        "after_state_units": base.state_units(after),
    }


def rank_row(row: dict) -> tuple:
    e = row["eval"]
    g = row["generator"]
    # Final candidates must remain all-overflow.  Within that region, make every
    # orientation as unfactorable as possible: minimize the largest factorable
    # mass, then maximize the smallest/mean empty mass.  Delta breaks ties.
    return (
        int(e["all_pivot_overflow"]),
        -int(g["max_factorable_mass"]),
        int(g["min_empty_mass"]),
        float(g["mean_empty_mass"]),
        int(e["delta"]),
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--beam-width", type=int, default=5)
    ap.add_argument("--steps", type=int, default=8)
    args = ap.parse_args()
    if args.beam_width < 1 or args.steps < 1:
        raise ValueError("positive beam/steps required")

    data = json.loads(WITNESS_PATH.read_text())
    left_leaf = base.canon_cnf(data["left_leaf"])
    right_leaf = base.canon_cnf(data["right_leaf"])
    source = build.build_source(left_leaf, right_leaf)
    product = build.build_product_global(left_leaf, right_leaf)
    if base.fingerprint(source) != EXPECTED_SOURCE or base.fingerprint(product) != EXPECTED_PRODUCT:
        raise AssertionError("FROZEN_WITNESS_FINGERPRINT_DRIFT")
    if base.input_size_units(source) != N:
        raise AssertionError("FROZEN_N_DRIFT")

    leaf_cache: dict[str, GeneratorFeature] = {}
    next_tag = -5000
    def feat(leaf: base.CNF) -> GeneratorFeature:
        nonlocal next_tag
        fp = base.fingerprint(leaf)
        if fp not in leaf_cache:
            leaf_cache[fp] = generator_feature(leaf, next_tag)
            next_tag -= 1
        return leaf_cache[fp]

    left0, right0 = feat(left_leaf), feat(right_leaf)
    start_eval = fast.fast_pair_evaluation(left0.standard, right0.standard)
    if start_eval["delta"] != 141 or not start_eval["all_pivot_overflow"]:
        raise AssertionError("FROZEN_WITNESS_DELTA_DRIFT")
    start_gen = pair_generator_landscape(left0, right0)

    # Full product brute exact validation on both orientations of frozen root 2.
    for positive in (True, False):
        fact = factorized_orientation_mass(left0, right0, 1, positive)
        brute = brute_product_orientation(product, build.LEFT_FIRST, positive)
        for key in ("unique_new_resolvent_count", "unique_new_resolvent_mass", "empty_intersection_count", "empty_intersection_mass"):
            if fact[key] != brute[key]:
                raise AssertionError(("GENERATOR_FACTORIZATION_MISMATCH", positive, key, fact[key], brute[key]))

    pair_cache = {}
    def scored(left: GeneratorFeature, right: GeneratorFeature) -> dict:
        key = (left.fp, right.fp)
        if key not in pair_cache:
            pair_cache[key] = {
                "left": left, "right": right,
                "eval": fast.fast_pair_evaluation(left.standard, right.standard),
                "generator": pair_generator_landscape(left, right),
            }
        return pair_cache[key]

    beam = [scored(left0, right0)]
    best = beam[0]
    trace = [{
        "step": 0,
        "delta": best["eval"]["delta"],
        "max_factorable_mass": best["generator"]["max_factorable_mass"],
        "min_empty_mass": best["generator"]["min_empty_mass"],
        "mean_empty_mass": best["generator"]["mean_empty_mass"],
    }]

    for step in range(1, args.steps + 1):
        candidates = {(r["left"].fp, r["right"].fp): r for r in beam}
        for item in beam:
            for nl in local.sign_pair_neighbors(item["left"].leaf):
                lf = feat(nl)
                candidates[(lf.fp, item["right"].fp)] = scored(lf, item["right"])
            for nr in local.sign_pair_neighbors(item["right"].leaf):
                rf = feat(nr)
                candidates[(item["left"].fp, rf.fp)] = scored(item["left"], rf)
        ordered = sorted(candidates.values(), key=rank_row, reverse=True)
        beam = ordered[:args.beam_width]
        if rank_row(beam[0]) > rank_row(best):
            best = beam[0]
        trace.append({
            "step": step,
            "delta": best["eval"]["delta"],
            "all_pivot_overflow": best["eval"]["all_pivot_overflow"],
            "max_factorable_mass": best["generator"]["max_factorable_mass"],
            "min_empty_mass": best["generator"]["min_empty_mass"],
            "mean_empty_mass": best["generator"]["mean_empty_mass"],
            "leaf_states": len(leaf_cache),
            "pair_states": len(pair_cache),
        })
        if step >= 2 and trace[-1]["max_factorable_mass"] == trace[-2]["max_factorable_mass"] and trace[-1]["delta"] == trace[-2]["delta"]:
            break

    be = best["eval"]
    bg = best["generator"]
    # Independent exact factorized Delta confirmation.
    confirm = slow.v1.evaluate(best["left"].leaf, best["right"].leaf)
    if confirm["delta"] != be["delta"] or confirm["pivot_rows"] != be["pivot_rows"]:
        raise AssertionError("FINAL_DELTA_CONFIRMATION_DRIFT")

    v2_result = exact_v2_eval(best["left"], best["right"]) if be["all_pivot_overflow"] else None
    denial_candidate = bool(be["all_pivot_overflow"] and v2_result and not v2_result["rescue_exists"])
    replay = slow.v1.exact_reachability_replay(best["left"].leaf, best["right"].leaf, confirm) if denial_candidate else None
    l1_refuted = bool(
        denial_candidate and replay
        and replay["selector_reaches_target"]
        and replay["target_seen_at_ordinary_callsite"]
        and replay["all_ordinary_pivots_overflow_at_target"] is True
        and replay["v2_called_on_target"]
        and replay["v2_rescue_exists"] is False
    )

    final_source = build.build_source(best["left"].leaf, best["right"].leaf)
    final_product = build.build_product_global(best["left"].leaf, best["right"].leaf)
    report = {
        "schema": "JANUS/C025/GENERATOR-INTERSECTION-HOSTILE-SEARCH/v1",
        "status": "L1_REFUTED_BY_EXACT_REACHABLE_WITNESS" if l1_refuted else "NO_V2_DENIAL_FROM_GENERATOR_INTERSECTION_CHAMPION",
        "search": {
            "beam_width": args.beam_width,
            "steps_requested": args.steps,
            "steps_executed": trace[-1]["step"],
            "factorization_brute_product_selftest": "PASS",
            "leaf_states_evaluated": len(leaf_cache),
            "pair_states_evaluated": len(pair_cache),
            "trace": trace,
        },
        "frozen_witness_generator_landscape": start_gen,
        "best_candidate": {
            "evaluation": be,
            "generator_landscape": bg,
            "v2": v2_result,
            "source_fingerprint": base.fingerprint(final_source),
            "product_fingerprint": base.fingerprint(final_product),
            "left_leaf_fingerprint": best["left"].fp,
            "right_leaf_fingerprint": best["right"].fp,
            "left_leaf": [list(c) for c in best["left"].leaf],
            "right_leaf": [list(c) for c in best["right"].leaf],
        },
        "exact_reachability_replay": replay,
        "candidate_results": {
            "L1_ROOT_PHASE_POLYNOMIAL_GRAMMAR_TOTALITY": "REFUTED_BY_EXACT_REACHABLE_WITNESS" if l1_refuted else "OPEN_NOT_PROVED",
            "L1C_PIVOT_INVOLVING_POSITIVE_RELIEF_EXISTS": "NOT_REFUTED_BY_THIS_SEARCH__NOT_PROVED"
        },
        "scientific_boundary": {
            "selector_product_factorization_is_family_specific": True,
            "generator_intersection_search_score_has_no_theorem_authority": True,
            "final_v2_evaluation_is_exact": True,
            "final_L1_refutation_requires_full_frozen_core_reachability": True,
            "absence_of_denial_is_not_L1_or_L1C_proof": True,
            "L1A": "REFUTED", "L1B": "REFUTED", "L1": "OPEN" if not l1_refuted else "REFUTED",
            "P2_REACHABLE_PRESERVATION": "OPEN",
            "P_VS_NP": P_VS_NP,
        },
        "P_VS_NP": P_VS_NP,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
