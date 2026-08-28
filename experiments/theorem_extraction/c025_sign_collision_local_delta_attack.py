#!/usr/bin/env python3
"""Local JUXTAPOSE attack on resolvent collision structure.

Starts from the frozen signed-regular champion of run 33189421237.  Every move
replaces one complementary sign-pair by another unused complementary sign-pair
on the same 3-variable support.  Therefore clause count, support multiset,
p(v)=q(v)=15, N=614 and the pair-dispersed chassis are invariant.  Only exact
resolvent tautology/collision/uniqueness geometry changes.

Search has no theorem authority.  Any DELTA>0 candidate must pass the predecessor
exact-factorized confirmation and frozen PIRC_DECISION_CORE_V0_4 reachability
replay before L1/L1A/L1B can be marked refuted.
"""
from __future__ import annotations

import argparse
import json

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.theorem_extraction import c025_signed_regular_balanced_delta_attack as slow
from experiments.theorem_extraction import c025_signed_regular_balanced_delta_attack_fast as fast

P_VS_NP = "OPEN"
START_LEFT_SEED = 26083720
START_RIGHT_SEED = 26083513
EXPECTED_START_DELTA = -21471


def feature_from_leaf(leaf: base.CNF, tag: int) -> slow.LeafFeature:
    if len(leaf) != slow.v1.LEAF_CLAUSES:
        raise AssertionError("LEAF_CLAUSE_COUNT_DRIFT")
    profile = slow.v1.polarity_profile(leaf)
    if any(p != 15 or q != 15 for p, q in profile.values()):
        raise AssertionError(("SIGNED_REGULARITY_DRIFT", profile))
    unions = slow.v1.pair_union_set(leaf)
    leaf_set = set(leaf)
    uorig = unions & leaf_set
    pivots = {}
    for pivot in slow.VARS:
        retained = {c for c in leaf if pivot not in c and -pivot not in c}
        rset = slow.v1.leaf_resolution_set(leaf, pivot)
        dup = rset & retained
        pivots[pivot] = slow.PivotFeature(
            retained_count=len(retained),
            retained_width=sum(map(len, retained)),
            resolvent_count=len(rset),
            resolvent_width=sum(map(len, rset)),
            duplicate_left_count=len(dup),
            duplicate_left_width=sum(map(len, dup)),
        )
    lit = slow.v1.literal_counts(leaf)
    return slow.LeafFeature(
        seed=tag,
        leaf=leaf,
        fp=base.fingerprint(leaf),
        union_count=len(unions),
        union_width=sum(map(len, unions)),
        union_original_count=len(uorig),
        union_original_width=sum(map(len, uorig)),
        pair_frequency=slow.v1.leaf_pair_frequency(leaf),
        max_literal_count=max(lit.values(), default=0),
        pivots=pivots,
    )


def support_of(clause: base.Clause) -> tuple[int, ...]:
    return tuple(sorted(abs(x) for x in clause))


def sign_pair_neighbors(leaf: base.CNF):
    rows = set(leaf)
    supports = sorted({support_of(c) for c in leaf})
    seen_fp = set()
    for support in supports:
        present = []
        pair_clauses = {}
        for pid in range(4):
            a, b = slow.complement_sign_pair(support, pid)
            pair_clauses[pid] = (a, b)
            if a in rows and b in rows:
                present.append(pid)
        if not present:
            raise AssertionError(("COMPLEMENT_PAIR_CLOSURE_BROKEN", support))
        absent = [pid for pid in range(4) if pid not in present]
        for old in present:
            oa, ob = pair_clauses[old]
            for new in absent:
                na, nb = pair_clauses[new]
                nr = set(rows)
                nr.remove(oa); nr.remove(ob)
                nr.add(na); nr.add(nb)
                out = tuple(sorted(nr, key=lambda c: (len(c), c)))
                if len(out) != len(leaf):
                    raise AssertionError("NEIGHBOR_SIZE_DRIFT")
                fp = base.fingerprint(out)
                if fp in seen_fp:
                    continue
                seen_fp.add(fp)
                profile = slow.v1.polarity_profile(out)
                if any(p != 15 or q != 15 for p, q in profile.values()):
                    raise AssertionError("NEIGHBOR_SIGNED_REGULARITY_DRIFT")
                yield out


def rank_eval(e: dict) -> tuple:
    return (int(e["delta"]), -int(e["pair_rescue_margin"]), float(e["mean_raw_units"]))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--beam-width", type=int, default=4)
    ap.add_argument("--steps", type=int, default=24)
    args = ap.parse_args()
    if args.beam_width < 1 or args.steps < 1:
        raise ValueError("beam-width>=1 and steps>=1 required")

    slow.v1.selftest_factorization()
    left0 = slow.feature_leaf(START_LEFT_SEED)
    right0 = slow.feature_leaf(START_RIGHT_SEED)
    start_eval = fast.fast_pair_evaluation(left0, right0)
    if start_eval["delta"] != EXPECTED_START_DELTA:
        raise AssertionError(("PREDECESSOR_CHAMPION_DRIFT", start_eval["delta"], EXPECTED_START_DELTA))
    exact_start = slow.v1.evaluate(left0.leaf, right0.leaf)
    if exact_start["pivot_rows"] != start_eval["pivot_rows"]:
        raise AssertionError("START_FAST_EXACT_FACTOR_DRIFT")

    leaf_cache = {left0.fp: left0, right0.fp: right0}
    pair_cache = {}
    next_tag = -1

    def get_feature(leaf: base.CNF):
        nonlocal next_tag
        fp = base.fingerprint(leaf)
        if fp not in leaf_cache:
            leaf_cache[fp] = feature_from_leaf(leaf, next_tag)
            next_tag -= 1
        return leaf_cache[fp]

    def eval_pair(left: slow.LeafFeature, right: slow.LeafFeature):
        key = (left.fp, right.fp)
        if key not in pair_cache:
            pair_cache[key] = fast.fast_pair_evaluation(left, right)
        return pair_cache[key]

    beam = [{"left": left0, "right": right0, "eval": start_eval}]
    best = beam[0]
    trace = [{
        "step": 0,
        "delta": start_eval["delta"],
        "pair_rescue_margin": start_eval["pair_rescue_margin"],
        "min_raw_units": start_eval["min_raw_units"],
        "left_fp": left0.fp,
        "right_fp": right0.fp,
    }]

    for step in range(1, args.steps + 1):
        candidates = {(x["left"].fp, x["right"].fp): x for x in beam}
        for item in beam:
            for nl in sign_pair_neighbors(item["left"].leaf):
                lf = get_feature(nl)
                e = eval_pair(lf, item["right"])
                candidates[(lf.fp, item["right"].fp)] = {"left": lf, "right": item["right"], "eval": e}
            for nr in sign_pair_neighbors(item["right"].leaf):
                rf = get_feature(nr)
                e = eval_pair(item["left"], rf)
                candidates[(item["left"].fp, rf.fp)] = {"left": item["left"], "right": rf, "eval": e}

        ordered = sorted(candidates.values(), key=lambda x: rank_eval(x["eval"]), reverse=True)
        beam = ordered[:args.beam_width]
        if rank_eval(beam[0]["eval"]) > rank_eval(best["eval"]):
            best = beam[0]
        be = best["eval"]
        trace.append({
            "step": step,
            "delta": be["delta"],
            "pair_rescue_margin": be["pair_rescue_margin"],
            "min_raw_units": be["min_raw_units"],
            "left_fp": best["left"].fp,
            "right_fp": best["right"].fp,
            "leaf_states_evaluated": len(leaf_cache),
            "pair_states_evaluated": len(pair_cache),
        })
        if be["all_pivot_overflow"] and be["pair_dispersed"]:
            break
        # If the entire beam is the same as the previous best neighborhood and
        # no one-step improvement exists, further identical expansion is useless.
        if step >= 2 and trace[-1]["delta"] == trace[-2]["delta"] and trace[-1]["left_fp"] == trace[-2]["left_fp"] and trace[-1]["right_fp"] == trace[-2]["right_fp"]:
            break

    be = best["eval"]
    confirm = slow.v1.evaluate(best["left"].leaf, best["right"].leaf)
    if confirm["pivot_rows"] != be["pivot_rows"] or confirm["delta"] != be["delta"]:
        raise AssertionError("CHAMPION_EXACT_FACTORIZATION_DRIFT")

    source = slow.v1.build_source(best["left"].leaf, best["right"].leaf)
    product = slow.v1.build_product_global(best["left"].leaf, best["right"].leaf)
    candidate_found = bool(be["all_pivot_overflow"] and be["pair_dispersed"])
    replay = slow.v1.exact_reachability_replay(best["left"].leaf, best["right"].leaf, confirm) if candidate_found else None

    l1a_refuted = bool(candidate_found and replay and replay["selector_reaches_target"] and replay["target_seen_at_ordinary_callsite"] and replay["all_ordinary_pivots_overflow_at_target"] is True and be["pair_rescue_margin"] < 0)
    l1b_refuted = bool(l1a_refuted and be["pair_density_margin"] < 0)
    l1_refuted = bool(l1a_refuted and replay and replay["v2_called_on_target"] and replay["v2_rescue_exists"] is False)

    report = {
        "schema": "JANUS/C025/SIGN-COLLISION-LOCAL-DELTA-ATTACK/v1",
        "status": "L1_REACHABLE_COUNTEREXAMPLE_FOUND" if l1_refuted else "L1A_REACHABLE_COUNTEREXAMPLE_FOUND" if l1a_refuted else "DIRECT_CANDIDATE_FOUND_BUT_REACHABILITY_GATE_FAILED" if candidate_found else "LOCAL_SIGN_COLLISION_SEARCH_NO_ALL_PIVOT_OVERFLOW",
        "search": {
            "beam_width": args.beam_width,
            "steps_requested": args.steps,
            "steps_executed": trace[-1]["step"],
            "start_left_seed": START_LEFT_SEED,
            "start_right_seed": START_RIGHT_SEED,
            "predecessor_delta_verified": "PASS",
            "exact_factorization_selftest": "PASS",
            "leaf_states_evaluated": len(leaf_cache),
            "pair_states_evaluated": len(pair_cache),
            "trace": trace,
        },
        "best_candidate": {
            "evaluation": be,
            "source_fingerprint": base.fingerprint(source),
            "product_fingerprint": base.fingerprint(product),
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
            "support_multiset_fixed": True,
            "signed_15_15_invariant": True,
            "N_and_cap_fixed": True,
            "only_sign_collision_geometry_changed": True,
            "search_score_is_not_proof": True,
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
