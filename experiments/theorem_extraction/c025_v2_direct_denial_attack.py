#!/usr/bin/env python3
"""Direct bounded falsification attack on L1 root-phase grammar totality.

Starting from the frozen exact-reachable all-pivot-overflow witness, JUXTAPOSE
explores complementary sign-pair mutations that preserve the fixed chassis,
signed 15:15 profile and N=614.  Cheap exact-factorized DELTA is only a gate.
Every admitted DELTA>0 candidate is scored by the actual frozen exhaustive v2
macro discovery routine.  Search attempts to make v2 return no rescue; if it
does, a full frozen-core reachability replay is mandatory before L1 is refuted.

Search ordering/beam selection has no theorem authority. P_VS_NP remains OPEN.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_unified_macro_restore_v2 as v2
from experiments.theorem_extraction import c025_signed_regular_balanced_delta_attack as slow
from experiments.theorem_extraction import c025_signed_regular_balanced_delta_attack_fast as fast
from experiments.theorem_extraction import c025_sign_collision_local_delta_attack as local

P_VS_NP = "OPEN"
WITNESS = Path("research/C025_L1A_L1B_WITNESS_CNF_2026-08-28.json")
N = 614
CAP = 376996
EXPECTED_START_SOURCE = "03506158fa7d60deb18f1832f1733e27f511d354024aff21f7afd33e27935b0f"
EXPECTED_START_PRODUCT = "3559df2656aade8e446d3a5eeedd419578fcebcf07ebecd35b2556ae35f68089"
EXPECTED_START_DELTA = 141
EXPECTED_START_RESCUE_SLACK = 38816


def pair_frequency(cnf: base.CNF, a: int, b: int) -> int:
    return sum(1 for c in cnf if a in c and b in c)


def exact_v2_eval(left: slow.LeafFeature, right: slow.LeafFeature) -> dict:
    source = slow.v1.build_source(left.leaf, right.leaf)
    product = slow.v1.build_product_global(left.leaf, right.leaf)
    if base.input_size_units(source) != N:
        raise AssertionError("FIXED_N_DRIFT")
    state = base.EngineState(
        root=source,
        residual=product,
        fixed_assignment={},
        root_vars=base.vars_of(source),
        extension_defs=[],
        elimination_history=[],
        seen=set(),
        N=N,
        cap_exponent=2,
        extension_exponent=2,
        ledger=base.Ledger(),
    )
    result = v2.discover_macro_restore_v2(state)
    if result is None:
        return {
            "rescue_exists": False,
            "rescue_slack": None,
            "pair": None,
            "pair_frequency": None,
            "root_pivot": None,
            "macro_state_units": None,
            "raw_units": None,
            "after_state_units": None,
            "source_fingerprint": base.fingerprint(source),
            "product_fingerprint": base.fingerprint(product),
        }
    macro, root, after, cert, stats = result
    raw = int(stats["raw_units"])
    if raw > CAP:
        raise AssertionError("FROZEN_V2_RETURNED_OVER_CAP_RESCUE")
    a, b = (int(x) for x in cert["represents"])
    return {
        "rescue_exists": True,
        "rescue_slack": CAP - raw,
        "pair": [a, b],
        "pair_frequency": pair_frequency(product, a, b),
        "root_pivot": int(root),
        "macro_state_units": base.state_units(macro),
        "raw_units": raw,
        "after_state_units": base.state_units(after),
        "source_fingerprint": base.fingerprint(source),
        "product_fingerprint": base.fingerprint(product),
    }


def denial_rank(row: dict) -> tuple:
    # No rescue dominates every rescued candidate.  Otherwise smaller cap slack
    # is closer to denial.  DELTA only breaks ties among equally resilient v2 states.
    v = row["v2"]
    if not v["rescue_exists"]:
        return (1, 0, int(row["eval"]["delta"]))
    return (0, -int(v["rescue_slack"]), int(row["eval"]["delta"]))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--beam-width", type=int, default=3)
    ap.add_argument("--steps", type=int, default=5)
    ap.add_argument("--exact-v2-budget", type=int, default=160)
    args = ap.parse_args()
    if args.beam_width < 1 or args.steps < 1 or args.exact_v2_budget < 1:
        raise ValueError("positive beam/steps/budget required")

    # Shared exact factorization firewall.
    slow.v1.selftest_factorization()
    data = json.loads(WITNESS.read_text())
    left_leaf = base.canon_cnf(data["left_leaf"])
    right_leaf = base.canon_cnf(data["right_leaf"])
    left0 = local.feature_from_leaf(left_leaf, -1001)
    right0 = local.feature_from_leaf(right_leaf, -1002)
    start_eval = fast.fast_pair_evaluation(left0, right0)
    if start_eval["delta"] != EXPECTED_START_DELTA or not start_eval["all_pivot_overflow"]:
        raise AssertionError("START_DELTA_DRIFT")
    start_v2 = exact_v2_eval(left0, right0)
    if not start_v2["rescue_exists"] or start_v2["rescue_slack"] != EXPECTED_START_RESCUE_SLACK:
        raise AssertionError(("START_V2_RESCUE_DRIFT", start_v2))
    if start_v2["source_fingerprint"] != EXPECTED_START_SOURCE or start_v2["product_fingerprint"] != EXPECTED_START_PRODUCT:
        raise AssertionError("START_FINGERPRINT_DRIFT")

    leaf_cache = {left0.fp: left0, right0.fp: right0}
    pair_fast_cache = {}
    v2_cache = {(left0.fp, right0.fp): start_v2}
    next_tag = -2000

    def feat(leaf: base.CNF) -> slow.LeafFeature:
        nonlocal next_tag
        fp = base.fingerprint(leaf)
        if fp not in leaf_cache:
            leaf_cache[fp] = local.feature_from_leaf(leaf, next_tag)
            next_tag -= 1
        return leaf_cache[fp]

    def fast_eval(left: slow.LeafFeature, right: slow.LeafFeature) -> dict:
        key=(left.fp,right.fp)
        if key not in pair_fast_cache:
            pair_fast_cache[key]=fast.fast_pair_evaluation(left,right)
        return pair_fast_cache[key]

    exact_calls = 1
    beam = [{"left": left0, "right": right0, "eval": start_eval, "v2": start_v2}]
    best = beam[0]
    trace = [{
        "step": 0,
        "delta": start_eval["delta"],
        "rescue_exists": True,
        "rescue_slack": start_v2["rescue_slack"],
        "rescue_pair": start_v2["pair"],
        "rescue_root": start_v2["root_pivot"],
        "exact_v2_calls": exact_calls,
    }]

    for step in range(1, args.steps + 1):
        if exact_calls >= args.exact_v2_budget or not best["v2"]["rescue_exists"]:
            break
        cheap = {}
        for item in beam:
            # Keep current beam members eligible.
            cheap[(item["left"].fp,item["right"].fp)] = (item["left"],item["right"],item["eval"])
            for nl in local.sign_pair_neighbors(item["left"].leaf):
                lf=feat(nl); e=fast_eval(lf,item["right"])
                if e["all_pivot_overflow"] and e["pair_dispersed"]:
                    cheap[(lf.fp,item["right"].fp)] = (lf,item["right"],e)
            for nr in local.sign_pair_neighbors(item["right"].leaf):
                rf=feat(nr); e=fast_eval(item["left"],rf)
                if e["all_pivot_overflow"] and e["pair_dispersed"]:
                    cheap[(item["left"].fp,rf.fp)] = (item["left"],rf,e)

        # Candidate generation is allowed to use exact-factorized DELTA only as
        # a scheduling heuristic.  Final beam selection uses exact frozen v2.
        queued=[]
        for key,(lf,rf,e) in cheap.items():
            if key in v2_cache:
                queued.append({"left":lf,"right":rf,"eval":e,"v2":v2_cache[key]})
        unseen=[(key,*vals) for key,vals in cheap.items() if key not in v2_cache]
        unseen.sort(key=lambda x:(int(x[3]["delta"]), -int(x[3]["pair_rescue_margin"]), x[0]), reverse=True)
        remaining=args.exact_v2_budget-exact_calls
        per_step=max(args.beam_width*8, remaining//max(1,args.steps-step+1))
        for key,lf,rf,e in unseen[:min(remaining,per_step)]:
            ve=exact_v2_eval(lf,rf)
            v2_cache[key]=ve
            exact_calls+=1
            queued.append({"left":lf,"right":rf,"eval":e,"v2":ve})
            if not ve["rescue_exists"]:
                break
        if not queued:
            break
        queued.sort(key=denial_rank, reverse=True)
        beam=queued[:args.beam_width]
        if denial_rank(beam[0]) > denial_rank(best):
            best=beam[0]
        trace.append({
            "step":step,
            "delta":best["eval"]["delta"],
            "rescue_exists":best["v2"]["rescue_exists"],
            "rescue_slack":best["v2"]["rescue_slack"],
            "rescue_pair":best["v2"]["pair"],
            "rescue_pair_frequency":best["v2"]["pair_frequency"],
            "rescue_root":best["v2"]["root_pivot"],
            "rescue_raw_units":best["v2"]["raw_units"],
            "exact_v2_calls":exact_calls,
            "all_overflow_neighbors_seen":len(cheap),
        })
        if not best["v2"]["rescue_exists"]:
            break

    be=best["eval"]; bv=best["v2"]
    # Independent factorized confirmation of the final all-overflow landscape.
    confirm=slow.v1.evaluate(best["left"].leaf,best["right"].leaf)
    if confirm["delta"] != be["delta"] or confirm["pivot_rows"] != be["pivot_rows"]:
        raise AssertionError("FINAL_DELTA_CONFIRMATION_DRIFT")

    denial_candidate = bool(be["all_pivot_overflow"] and not bv["rescue_exists"])
    replay = slow.v1.exact_reachability_replay(best["left"].leaf,best["right"].leaf,confirm) if denial_candidate else None
    l1_refuted=bool(
        denial_candidate and replay
        and replay["selector_reaches_target"]
        and replay["target_seen_at_ordinary_callsite"]
        and replay["all_ordinary_pivots_overflow_at_target"] is True
        and replay["v2_called_on_target"]
        and replay["v2_rescue_exists"] is False
    )

    source=slow.v1.build_source(best["left"].leaf,best["right"].leaf)
    product=slow.v1.build_product_global(best["left"].leaf,best["right"].leaf)
    report={
      "schema":"JANUS/C025/V2-DIRECT-DENIAL-ATTACK/v1",
      "status":"L1_REFUTED_BY_EXACT_REACHABLE_WITNESS" if l1_refuted else "V2_DENIAL_CANDIDATE_REACHABILITY_FAILED" if denial_candidate else "NO_V2_DENIAL_IN_BOUNDED_SEARCH",
      "search":{
        "beam_width":args.beam_width,"steps_requested":args.steps,"steps_executed":trace[-1]["step"],
        "exact_v2_budget":args.exact_v2_budget,"exact_v2_calls":exact_calls,
        "leaf_states_cached":len(leaf_cache),"fast_pair_states_cached":len(pair_fast_cache),
        "factorized_delta_selftest":"PASS","trace":trace
      },
      "best_candidate":{
        "evaluation":be,"v2":bv,
        "source_fingerprint":base.fingerprint(source),"product_fingerprint":base.fingerprint(product),
        "left_leaf_fingerprint":best["left"].fp,"right_leaf_fingerprint":best["right"].fp,
        "left_leaf":[list(c) for c in best["left"].leaf],"right_leaf":[list(c) for c in best["right"].leaf],
        "source_cnf":[list(c) for c in source]
      },
      "exact_reachability_replay":replay,
      "candidate_results":{
        "L1_ROOT_PHASE_POLYNOMIAL_GRAMMAR_TOTALITY":"REFUTED_BY_EXACT_REACHABLE_WITNESS" if l1_refuted else "OPEN_NOT_PROVED",
        "L1A_ALL_PIVOT_OVERFLOW_FORCES_FREQUENT_PAIR":"REFUTED_PREVIOUS_GENERATION",
        "L1B_ALL_PIVOT_OVERFLOW_FORCES_PAIR_DENSITY":"REFUTED_PREVIOUS_GENERATION"
      },
      "scientific_boundary":{
        "beam_search_has_no_theorem_authority":True,
        "exact_v2_used_for_search_score_but_not_theorem_promotion":True,
        "final_L1_refutation_requires_full_frozen_core_reachability":True,
        "failure_to_find_v2_denial_is_not_L1_proof":True,
        "same_run_theorem_promotion":False,
        "P2_REACHABLE_PRESERVATION":"OPEN","P_VS_NP":P_VS_NP
      },
      "P_VS_NP":P_VS_NP
    }
    print(json.dumps(report,indent=2,sort_keys=True)); return 0

if __name__=="__main__": raise SystemExit(main())
