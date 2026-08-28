#!/usr/bin/env python3
"""Exact-rho minimax attack on the pivot-involving v2 rescue candidate L1C.

For the frozen signed-regular selector-product family, every pivot-involving pair
score rho=E-H-(U-N^2) is computed exactly by disjoint-factor algebra.  The search
minimizes MAX_RHO over all roots, both polarities, and all repeated co-literals,
while keeping every ordinary pivot over cap.  Representative same-block and
cross-block rho values are self-tested against full macro+uncapped elimination.

If MAX_RHO becomes negative, all pivot-involving rescues are independently
replayed with the frozen exact macro/elimination semantics before L1C may be
refuted.  Full frozen v2 and full-core reachability are then checked for L1.
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
from experiments.theorem_extraction import c025_generator_intersection_hostile_search as gen

P_VS_NP = "OPEN"
WITNESS = Path("research/C025_L1A_L1B_WITNESS_CNF_2026-08-28.json")
N = 614
CAP = N * N
FRESH = 14
EXPECTED_SOURCE = "03506158fa7d60deb18f1832f1733e27f511d354024aff21f7afd33e27935b0f"
EXPECTED_PRODUCT = "3559df2656aade8e446d3a5eeedd419578fcebcf07ebecd35b2556ae35f68089"


@dataclass
class OrientationDetail:
    pivot: int
    positive: bool
    resolvents: dict[base.Clause, frozenset[int]]
    retained: set[base.Clause]
    all_summary: gen.MassSummary
    by_literal: dict[int, gen.MassSummary]
    oriented_parents: tuple[base.Clause, ...]
    opposite_parents: tuple[base.Clause, ...]


@dataclass
class RhoLeaf:
    leaf: base.CNF
    fp: str
    standard: slow.LeafFeature
    union_all: gen.MassSummary
    union_by_literal: dict[int, gen.MassSummary]
    orientations: dict[tuple[int, bool], OrientationDetail]


def literal_universe() -> tuple[int, ...]:
    return tuple([*range(-slow.v1.LEAF_NVARS, 0), *range(1, slow.v1.LEAF_NVARS + 1)])


def make_summary(rows: set[base.Clause], retained: set[base.Clause]) -> gen.MassSummary:
    return gen.summarize(rows, retained)


def rho_leaf(leaf: base.CNF, tag: int) -> RhoLeaf:
    standard = local.feature_from_leaf(leaf, tag)
    union_map = gen.union_generator_intersections(leaf)
    union_set = set(union_map)
    leaf_set = set(leaf)
    union_by = {}
    for b in literal_universe():
        rows = {u for u, inter in union_map.items() if b in inter}
        union_by[b] = make_summary(rows, leaf_set)

    orientations = {}
    for pivot in slow.VARS:
        for positive in (True, False):
            lit = pivot if positive else -pivot
            anti = -lit
            rmap = gen.oriented_leaf_resolvent_intersections(leaf, pivot, positive)
            retained = {c for c in leaf if pivot not in c and -pivot not in c}
            oriented = tuple(c for c in leaf if lit in c)
            opposite = tuple(c for c in leaf if anti in c)
            by = {}
            for b in literal_universe():
                if abs(b) == pivot:
                    continue
                rows = {r for r, inter in rmap.items() if b in inter}
                by[b] = make_summary(rows, retained)
            orientations[(pivot, positive)] = OrientationDetail(
                pivot=pivot, positive=positive, resolvents=rmap, retained=retained,
                all_summary=make_summary(set(rmap), retained), by_literal=by,
                oriented_parents=oriented, opposite_parents=opposite,
            )
    return RhoLeaf(
        leaf=leaf, fp=base.fingerprint(leaf), standard=standard,
        union_all=make_summary(union_set, leaf_set), union_by_literal=union_by,
        orientations=orientations,
    )


def mass_of_product(a: set[base.Clause], b: set[base.Clause]) -> int:
    return gen.cartesian_weight(len(a), sum(map(len, a)), len(b), sum(map(len, b)))


def pair_frequency_same(detail: OrientationDetail, b: int, other_clause_count: int) -> int:
    return sum(1 for p in detail.oriented_parents if b in p) * other_clause_count


def pair_frequency_cross(detail: OrientationDetail, other_leaf: base.CNF, b: int) -> int:
    return len(detail.oriented_parents) * sum(1 for c in other_leaf if b in c)


def H_same(detail: OrientationDetail, other_leaf: base.CNF, b: int) -> int:
    lit = detail.pivot if detail.positive else -detail.pivot
    anti = -lit
    e = 100
    minus: set[base.Clause] = set()
    plus: set[base.Clause] = set()
    for p in detail.oriented_parents:
        body = [l for l in p if l != lit and (b not in p or l != b)]
        c = base.canon_clause([-e, *body])
        if c is not None:
            minus.add(c)
    for n in detail.opposite_parents:
        c = base.canon_clause([e, b, *[l for l in n if l != anti]])
        if c is not None:
            plus.add(c)
    # +/-e separate the two Cartesian star families; the definition clause has
    # no opposite-block literals and cannot collide with either family.
    return mass_of_product(minus, set(other_leaf)) + mass_of_product(plus, set(other_leaf)) + 3


def H_cross(detail: OrientationDetail, other_leaf: base.CNF, b: int) -> int:
    lit = detail.pivot if detail.positive else -detail.pivot
    anti = -lit
    e = 100
    pminus = {base.canon_clause([-e, *[l for l in p if l != lit]]) for p in detail.oriented_parents}
    pminus.discard(None)
    nplus = {base.canon_clause([e, *[l for l in n if l != anti]]) for n in detail.opposite_parents}
    nplus.discard(None)

    rminus: set[base.Clause] = set()
    for r in other_leaf:
        if b in r:
            c = base.canon_clause([l for l in r if l != b])
        else:
            c = r
        if c is not None:
            rminus.add(c)
    rplus: set[base.Clause] = set()
    for r in other_leaf:
        c = base.canon_clause([b, *r])
        if c is not None:
            rplus.add(c)
    return mass_of_product(set(pminus), rminus) + mass_of_product(set(nplus), rplus) + 3


def local_to_global(side: str, lit: int) -> int:
    first = build.LEFT_FIRST if side == "L" else build.RIGHT_FIRST
    g = first + abs(lit) - 1
    return g if lit > 0 else -g


def exact_rho_landscape(left: RhoLeaf, right: RhoLeaf, ordinary_eval: dict) -> dict:
    raw_by = {}
    for row in ordinary_eval["pivot_rows"]:
        raw_by[(row["side"], int(row["pivot"]))] = int(row["raw_units"])
    rows = []

    def one_side(side: str, pivot_leaf: RhoLeaf, other_leaf: RhoLeaf):
        for pivot in slow.VARS:
            U = raw_by[(side, pivot)]
            overflow = U - CAP
            if overflow <= 0:
                raise AssertionError("RHO_LANDSCAPE_REQUIRES_ALL_PIVOT_OVERFLOW")
            for positive in (True, False):
                detail = pivot_leaf.orientations[(pivot, positive)]
                pivot_local_lit = pivot if positive else -pivot
                pivot_global_lit = local_to_global(side, pivot_local_lit)
                # Same-block co-literals.
                for b in literal_universe():
                    if abs(b) == pivot:
                        continue
                    freq = pair_frequency_same(detail, b, len(other_leaf.leaf))
                    if freq < 2:
                        continue
                    E = gen.product_unique_new_mass(detail.by_literal[b], other_leaf.union_all)[1]
                    H = H_same(detail, other_leaf.leaf, b)
                    rho = E - H - overflow
                    rows.append({
                        "side": side, "pivot": pivot, "pivot_literal": pivot_global_lit,
                        "orientation": "+" if positive else "-", "co_literal": local_to_global(side, b),
                        "co_literal_block": "SAME", "pair_frequency": freq,
                        "ordinary_raw_units": U, "overflow_excess": overflow,
                        "E": E, "H": H, "J": E-H, "rho": rho,
                    })
                # Opposite-block co-literals.
                other_side = "R" if side == "L" else "L"
                for b in literal_universe():
                    freq = pair_frequency_cross(detail, other_leaf.leaf, b)
                    if freq < 2:
                        continue
                    E = gen.product_unique_new_mass(detail.all_summary, other_leaf.union_by_literal[b])[1]
                    H = H_cross(detail, other_leaf.leaf, b)
                    rho = E - H - overflow
                    rows.append({
                        "side": side, "pivot": pivot, "pivot_literal": pivot_global_lit,
                        "orientation": "+" if positive else "-", "co_literal": local_to_global(other_side, b),
                        "co_literal_block": "CROSS", "pair_frequency": freq,
                        "ordinary_raw_units": U, "overflow_excess": overflow,
                        "E": E, "H": H, "J": E-H, "rho": rho,
                    })

    one_side("L", left, right)
    one_side("R", right, left)
    if not rows:
        raise AssertionError("NO_ELIGIBLE_PIVOT_INVOLVING_PAIRS")
    return {
        "rows": rows,
        "max_rho": max(r["rho"] for r in rows),
        "min_rho": min(r["rho"] for r in rows),
        "nonnegative_rho_count": sum(1 for r in rows if r["rho"] >= 0),
        "positive_rho_sum": sum(max(0, r["rho"]) for r in rows),
        "best_pair": max(rows, key=lambda r: (r["rho"], -abs(r["co_literal"]), r["co_literal"])),
    }


def brute_rho(product: base.CNF, pivot_literal: int, b: int) -> int:
    macro, cert = v2.apply_or_pair_v2(product, pivot_literal, b, FRESH)
    if not v2.verify_or_pair_v2(product, macro, cert):
        raise AssertionError("BRUTE_MACRO_VERIFY_FAILED")
    raw = build.brute_raw_units(macro, abs(pivot_literal))
    return CAP - raw


def exact_v2_eval(left: RhoLeaf, right: RhoLeaf) -> dict:
    source = build.build_source(left.leaf, right.leaf)
    product = build.build_product_global(left.leaf, right.leaf)
    state = base.EngineState(
        root=source, residual=product, fixed_assignment={}, root_vars=base.vars_of(source),
        extension_defs=[], elimination_history=[], seen=set(), N=N,
        cap_exponent=2, extension_exponent=2, ledger=base.Ledger(),
    )
    result = v2.discover_macro_restore_v2(state)
    if result is None:
        return {"rescue_exists": False, "pair": None, "root_pivot": None, "raw_units": None, "slack": None}
    macro, root, after, cert, stats = result
    raw = int(stats["raw_units"])
    return {
        "rescue_exists": True, "pair": list(cert["represents"]), "root_pivot": int(root),
        "raw_units": raw, "slack": CAP-raw, "macro_state_units": base.state_units(macro),
        "after_state_units": base.state_units(after),
    }


def verify_all_pivot_pairs_exact(left: RhoLeaf, right: RhoLeaf, landscape: dict) -> dict:
    product = build.build_product_global(left.leaf, right.leaf)
    checked = 0
    unexpected_fit = None
    for r in landscape["rows"]:
        macro, cert = v2.apply_or_pair_v2(product, int(r["pivot_literal"]), int(r["co_literal"]), FRESH)
        if not v2.verify_or_pair_v2(product, macro, cert):
            raise AssertionError("FINAL_PAIR_MACRO_VERIFY_FAILED")
        out, stats = base.eliminate_var_capped(macro, abs(int(r["pivot_literal"])), CAP)
        checked += 1
        expected_fit = r["rho"] >= 0
        actual_fit = out is not None
        if expected_fit != actual_fit:
            raise AssertionError(("RHO_CAP_VERDICT_DRIFT", r, stats))
        if actual_fit and landscape["max_rho"] < 0:
            unexpected_fit = {"row": r, "stats": stats}
            break
    return {"pairs_checked": checked, "unexpected_fit": unexpected_fit, "status": "PASS"}


def rank_item(item: dict) -> tuple:
    e = item["eval"]
    if not e["all_pivot_overflow"]:
        return (0, -10**30, -10**30, -10**30, int(e["delta"]))
    r = item["rho"]
    return (
        1,
        -int(r["max_rho"]),
        -int(r["nonnegative_rho_count"]),
        -int(r["positive_rho_sum"]),
        int(e["delta"]),
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--beam-width", type=int, default=5)
    ap.add_argument("--steps", type=int, default=10)
    args = ap.parse_args()
    if args.beam_width < 1 or args.steps < 1:
        raise ValueError("positive beam/steps required")

    data = json.loads(WITNESS.read_text())
    left_leaf = base.canon_cnf(data["left_leaf"])
    right_leaf = base.canon_cnf(data["right_leaf"])
    source = build.build_source(left_leaf, right_leaf)
    product = build.build_product_global(left_leaf, right_leaf)
    if base.fingerprint(source) != EXPECTED_SOURCE or base.fingerprint(product) != EXPECTED_PRODUCT:
        raise AssertionError("WITNESS_FINGERPRINT_DRIFT")

    cache: dict[str, RhoLeaf] = {}
    next_tag = -8000
    def feat(leaf: base.CNF) -> RhoLeaf:
        nonlocal next_tag
        fp = base.fingerprint(leaf)
        if fp not in cache:
            cache[fp] = rho_leaf(leaf, next_tag)
            next_tag -= 1
        return cache[fp]

    pair_cache = {}
    def scored(left: RhoLeaf, right: RhoLeaf) -> dict:
        key=(left.fp,right.fp)
        if key not in pair_cache:
            e=fast.fast_pair_evaluation(left.standard,right.standard)
            rho=exact_rho_landscape(left,right,e) if e["all_pivot_overflow"] else None
            pair_cache[key]={"left":left,"right":right,"eval":e,"rho":rho}
        return pair_cache[key]

    left0,right0=feat(left_leaf),feat(right_leaf)
    start=scored(left0,right0)
    if start["eval"]["delta"] != 141:
        raise AssertionError("START_DELTA_DRIFT")
    # Algebra-vs-full-exact representative selftests: same/cross block, both pivot signs.
    tests=[(2,3),(2,8),(-2,-3),(-2,-8)]
    for plit,b in tests:
        row=next((r for r in start["rho"]["rows"] if r["pivot_literal"]==plit and r["co_literal"]==b),None)
        if row is None:
            raise AssertionError(("SELFTEST_PAIR_NOT_ELIGIBLE",plit,b))
        brute=brute_rho(product,plit,b)
        if brute != row["rho"]:
            raise AssertionError(("RHO_FACTORIZATION_MISMATCH",plit,b,row["rho"],brute))
    win=next(r for r in start["rho"]["rows"] if r["pivot_literal"]==2 and r["co_literal"]==3)
    if win["E"] != 55840 or win["H"] != 11643 or win["rho"] != 38816:
        raise AssertionError(("FROZEN_WINNING_RHO_DRIFT",win))

    beam=[start]; best=start
    trace=[{
        "step":0,"delta":start["eval"]["delta"],"max_rho":start["rho"]["max_rho"],
        "nonnegative_rho_count":start["rho"]["nonnegative_rho_count"],
        "positive_rho_sum":start["rho"]["positive_rho_sum"],
        "best_pair":start["rho"]["best_pair"],
    }]
    for step in range(1,args.steps+1):
        candidates={(x["left"].fp,x["right"].fp):x for x in beam}
        for item in beam:
            for nl in local.sign_pair_neighbors(item["left"].leaf):
                lf=feat(nl); x=scored(lf,item["right"]); candidates[(lf.fp,item["right"].fp)]=x
            for nr in local.sign_pair_neighbors(item["right"].leaf):
                rf=feat(nr); x=scored(item["left"],rf); candidates[(item["left"].fp,rf.fp)]=x
        ordered=sorted(candidates.values(),key=rank_item,reverse=True)
        beam=ordered[:args.beam_width]
        if rank_item(beam[0]) > rank_item(best): best=beam[0]
        br=best["rho"]
        trace.append({
            "step":step,"delta":best["eval"]["delta"],"all_pivot_overflow":best["eval"]["all_pivot_overflow"],
            "max_rho":br["max_rho"],"nonnegative_rho_count":br["nonnegative_rho_count"],
            "positive_rho_sum":br["positive_rho_sum"],"best_pair":br["best_pair"],
            "leaf_states":len(cache),"pair_states":len(pair_cache),
        })
        if br["max_rho"] < 0: break
        if step>=2 and trace[-1]["max_rho"]==trace[-2]["max_rho"] and trace[-1]["delta"]==trace[-2]["delta"]: break

    be=best["eval"]; br=best["rho"]
    confirm=slow.v1.evaluate(best["left"].leaf,best["right"].leaf)
    if confirm["delta"]!=be["delta"] or confirm["pivot_rows"]!=be["pivot_rows"]:
        raise AssertionError("FINAL_DELTA_CONFIRMATION_DRIFT")

    l1c_candidate=bool(be["all_pivot_overflow"] and br["max_rho"]<0)
    pair_verification=verify_all_pivot_pairs_exact(best["left"],best["right"],br) if l1c_candidate else None
    full_v2=exact_v2_eval(best["left"],best["right"])
    replay=slow.v1.exact_reachability_replay(best["left"].leaf,best["right"].leaf,confirm) if l1c_candidate else None
    l1c_refuted=bool(
        l1c_candidate and pair_verification and pair_verification["status"]=="PASS"
        and replay and replay["selector_reaches_target"] and replay["target_seen_at_ordinary_callsite"]
        and replay["all_ordinary_pivots_overflow_at_target"] is True
    )
    l1_refuted=bool(l1c_refuted and replay["v2_called_on_target"] and replay["v2_rescue_exists"] is False)

    final_source=build.build_source(best["left"].leaf,best["right"].leaf)
    final_product=build.build_product_global(best["left"].leaf,best["right"].leaf)
    report={
        "schema":"JANUS/C025/EXACT-RHO-MINIMAX-ATTACK/v1",
        "status":"L1_REFUTED_BY_EXACT_REACHABLE_WITNESS" if l1_refuted else "L1C_REFUTED_BUT_FULL_V2_RESCUES" if l1c_refuted else "NO_NEGATIVE_MAX_RHO_IN_BOUNDED_SEARCH",
        "search":{
            "beam_width":args.beam_width,"steps_requested":args.steps,"steps_executed":trace[-1]["step"],
            "representative_full_exact_rho_selftests":"PASS","winning_pair_rho_fixture":"PASS",
            "leaf_states_evaluated":len(cache),"pair_states_evaluated":len(pair_cache),"trace":trace
        },
        "start":{
            "delta":start["eval"]["delta"],"max_rho":start["rho"]["max_rho"],
            "nonnegative_rho_count":start["rho"]["nonnegative_rho_count"],"positive_rho_sum":start["rho"]["positive_rho_sum"],
            "winning_pair_2_3":win
        },
        "best_candidate":{
            "evaluation":be,"rho_landscape":br,"full_v2":full_v2,
            "source_fingerprint":base.fingerprint(final_source),"product_fingerprint":base.fingerprint(final_product),
            "left_leaf_fingerprint":best["left"].fp,"right_leaf_fingerprint":best["right"].fp,
            "left_leaf":[list(c) for c in best["left"].leaf],"right_leaf":[list(c) for c in best["right"].leaf]
        },
        "all_pivot_involving_exact_verification":pair_verification,
        "exact_reachability_replay":replay,
        "candidate_results":{
            "L1C_PIVOT_INVOLVING_POSITIVE_RELIEF_EXISTS":"REFUTED_BY_EXACT_REACHABLE_WITNESS" if l1c_refuted else "OPEN_NOT_PROVED",
            "L1_ROOT_PHASE_POLYNOMIAL_GRAMMAR_TOTALITY":"REFUTED_BY_EXACT_REACHABLE_WITNESS" if l1_refuted else "OPEN_NOT_PROVED",
            "L1A_ALL_PIVOT_OVERFLOW_FORCES_FREQUENT_PAIR":"REFUTED_PREVIOUS_GENERATION",
            "L1B_ALL_PIVOT_OVERFLOW_FORCES_PAIR_DENSITY":"REFUTED_PREVIOUS_GENERATION"
        },
        "scientific_boundary":{
            "rho_factorization_is_family_specific_but_exact_for_fixed_pair":True,
            "search_minimax_has_no_theorem_authority":True,
            "negative_MAX_RHO_requires_independent_all_pair_exact_replay":True,
            "final_L1C_and_L1_refutation_require_full_core_reachability":True,
            "failure_to_find_negative_MAX_RHO_is_not_L1C_proof":True,
            "L1A":"REFUTED","L1B":"REFUTED","L1":"REFUTED" if l1_refuted else "OPEN",
            "P2_REACHABLE_PRESERVATION":"OPEN","P_VS_NP":P_VS_NP
        },
        "P_VS_NP":P_VS_NP
    }
    print(json.dumps(report,indent=2,sort_keys=True)); return 0

if __name__=="__main__": raise SystemExit(main())
