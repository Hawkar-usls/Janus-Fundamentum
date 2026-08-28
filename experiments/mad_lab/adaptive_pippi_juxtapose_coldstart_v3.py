#!/usr/bin/env python3
"""JANUS PIPPI GAUNTLET v3 — learned warm start + instinctive JUXTAPOSE coverage.

The system does NOT forget prior lessons. Before any new fingerprint is scored it
replays the frozen exact curriculum already earned in previous runs:
- 24 historical 50:50 exact witnesses;
- the v2.4 ruthless track history: 1:1, 11:11, 21:21, 31:31, failed 44:47,
  three fresh 31:31 recoveries;
- four hard 250:250 exact-min boss witnesses.
The previous final adviser-governance vector is also loaded as the initial prior.

Only after that warm start does the new exam begin. New fingerprints remain
strictly unseen until they are scored.

New architecture change under test:
  LEARNING MAY REDUCE SEARCH, BUT MAY NEVER REMOVE THE ABILITY TO SEARCH.

If pre-exact prediction confidence is low, Keymaster falls back to JUXTAPOSE
coverage. COLD mode launches one exact clone for every currently available root
pivot. WARM/HOT modes launch smaller ranked waves. If a partial wave contains no
safe transition the field expands until an exact-safe transition is found.

Two costs are kept separate:
- TOTAL_COMPUTE: sum of all clone exact work (never treated as free);
- PARALLEL_LATENCY_PROXY: max exact work inside each clone wave, summed across
  waves (a scheduling proxy, not measured wall time).
The controller uses a balanced operational score (60% compute efficiency, 40%
parallel-latency proxy) so parallelism cannot silently erase compute cost.

Every counted transition is exact. Models/Spider only rank or set coverage.
P_VS_NP remains OPEN.
"""
from __future__ import annotations

import collections
import copy
import json
import math
from pathlib import Path
from typing import Any

from experiments.mad_lab import adaptive_pippi_pitstop_ladder as v1
from experiments.mad_lab import adaptive_pippi_gauntlet_v2 as v2
from experiments.mad_lab import adaptive_pippi_gauntlet_v2_4 as v24
from experiments.mad_lab import asymmetric_pq_track_relabelled as relabel
from experiments.mad_lab import keymaster_scalable_exact_root_labels as sl
from experiments.mad_lab import keymaster_scalable_exact_2cnf_transition as st
from experiments.mad_lab import keymaster_adviser_governance_v2 as gov

P_VS_NP = "OPEN"
SCHEMA = "JANUS/PIPPI/JUXTAPOSE-COLDSTART-GAUNTLET/v3.0.0"
BRANCH_RESULT = Path("data/keymaster/PIPPI_RUTHLESS_GAUNTLET_V2_4_RESULT_2026-08-28.json")
ORIGINAL_BOOTSTRAP = v1.bootstrap_50

# Exact prior v2.4 stage serials. They are replayed before the new exam and are
# never scored as v3 holdout. New v3 generation sees their fingerprints in the
# `used` set and therefore deterministically advances to fresh j-values.
PRIOR_TRACK = [
    (1, 1, 1, 4, "V2_4_FORMATION"),
    (11, 11, 2, 4, "V2_4_ACCEPTED"),
    (21, 21, 3, 4, "V2_4_ACCEPTED"),
    (31, 31, 4, 4, "V2_4_ACCEPTED"),
    (44, 47, 5, 4, "V2_4_FAILED_ASYMMETRIC_SHOCK"),
    (31, 31, 6, 4, "V2_4_RECOVERY_1"),
    (31, 31, 7, 4, "V2_4_RECOVERY_2"),
    (31, 31, 8, 4, "V2_4_RECOVERY_3"),
    (250, 250, 9, 4, "V2_4_HARD_BOSS"),
]


def _seed_for(p: int, q: int, stage_serial: int, j: int) -> int:
    return 1_300_000_000 + stage_serial * 100_003 + p * 1019 + q * 1031 + j * 43


def _load_prior_result() -> dict[str, Any]:
    p = json.loads(BRANCH_RESULT.read_text(encoding="utf-8"))
    assert p["P_VS_NP"] == "OPEN"
    assert p["canonical_run"]["workflow_conclusion"] == "SUCCESS"
    assert p["canonical_run"]["scientific_firewall"] == "PASS"
    assert p["failed_stage"]["p"] == 44 and p["failed_stage"]["q"] == 47
    assert p["hard_boss_250x250"]["aggregate"]["KEYMASTER"]["exact_checks"] == 161.0
    return p


def warm_history_bootstrap(used: set[str]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Reconstruct old exact lessons before any new exam fingerprint is created."""
    prior = _load_prior_result()
    memory, base_audit = ORIGINAL_BOOTSTRAP(used)
    old_50 = len(memory)
    added = []
    per_group = []
    for p, q, serial, count, lesson in PRIOR_TRACK:
        group = []
        for j in range(count):
            seed = _seed_for(p, q, serial, j)
            cnf, meta = relabel.construct_relabelled(p, q, seed)
            e = sl.exact_track_episode_fast(cnf, p, q, seed, f"WARM_HISTORY::{lesson}", serial)
            if lesson == "V2_4_HARD_BOSS":
                cap = min(e["raw"])
                e["local_stress_cap"] = cap
                e["safe_indices"] = [i for i, x in enumerate(e["raw"]) if x <= cap]
                e["historical_cap_policy"] = "EXACT_MIN_RAW_ONLY"
            if e["fingerprint"] in used:
                raise AssertionError(("historical fingerprint collision before insertion", lesson, e["fingerprint"]))
            used.add(e["fingerprint"])
            memory.append(e); added.append(e); group.append(e["fingerprint"])
        per_group.append({"lesson": lesson, "p": p, "q": q, "stage_serial": serial, "formulas": count, "fingerprints": group})

    # Preserve the learned governance prior from the frozen v2.4 checkpoint.
    prior_weights = {k: float(v) for k, v in prior["final_fusion_weights"].items()}
    if abs(sum(prior_weights.values()) - 1.0) > 1e-8:
        raise AssertionError(prior_weights)
    gov.DEFAULT.clear(); gov.DEFAULT.update(prior_weights)

    return memory, {
        "status": "WARM_HISTORY_REPLAYED_BEFORE_NEW_EXAM",
        "historical_50x50_formulas": old_50,
        "historical_v2_4_track_formulas": len(added),
        "total_exact_lesson_formulas": len(memory),
        "v2_4_prior_groups": per_group,
        "initial_governance_prior": prior_weights,
        "source_v2_4_run": prior["canonical_run"]["workflow_run_id"],
        "source_v2_4_artifact_digest": prior["canonical_run"]["artifact_digest"],
        "new_exam_fingerprints_seen_during_bootstrap": 0,
        "historical_negative_lessons_preserved": ["44:47_FAILURE", "31:31_RECOVERY_NOT_ENOUGH"],
        "base_50_audit": base_audit,
        "P_VS_NP": P_VS_NP,
    }


def _difficulty_novelty(train: list[dict[str, Any]], e: dict[str, Any]) -> float:
    p, q = int(e.get("p", e.get("d", 0))), int(e.get("q", e.get("d", 0)))
    coords = []
    for x in train:
        if "p" in x and "q" in x:
            coords.append((int(x["p"]), int(x["q"])))
        elif "d" in x:
            coords.append((int(x["d"]), int(x["d"])))
    if not coords:
        return 1.0
    scale = max(4.0, float(max(p, q)))
    d = min(math.hypot(p-a, q-b) / scale for a, b in coords)
    return min(1.0, d * 3.0)


def _pattern_known_fraction(train: list[dict[str, Any]], e: dict[str, Any]) -> float:
    known = set()
    for x in train[-64:]:
        for tok in x["tokens"]:
            known.add(v1.pattern_key(tok))
    pats = [v1.pattern_key(tok) for tok in e["tokens"]]
    if not pats:
        return 0.0
    return sum(p in known for p in pats) / len(pats)


def uncertainty_policy(comp: dict[str, list[float]], fused: list[float], train: list[dict[str, Any]], e: dict[str, Any]) -> dict[str, Any]:
    top = [v1.ranking_order(scores, e)[0] for scores in comp.values()]
    cnt = collections.Counter(top)
    top1_agreement = max(cnt.values()) / max(1, len(top))
    s = sorted(float(x) for x in fused)
    margin = (s[1] - s[0]) if len(s) > 1 else 1.0
    margin_signal = min(1.0, max(0.0, margin * 4.0))
    known = _pattern_known_fraction(train, e)
    novelty = _difficulty_novelty(train, e)
    confidence = 0.35 * top1_agreement + 0.20 * margin_signal + 0.25 * known + 0.20 * (1.0 - novelty)

    forced_cold = top1_agreement <= 0.25 or (margin < 0.02 and novelty > 0.20)
    if forced_cold or confidence < 0.45:
        mode, frac = "COLD_JUXTAPOSE", 1.0
    elif confidence < 0.70:
        mode, frac = "WARM_JUXTAPOSE", 0.50
    else:
        mode, frac = "HOT_PREDICTIVE", 0.20
    return {
        "mode": mode, "initial_coverage_fraction": frac, "confidence": confidence,
        "top1_adviser_agreement": top1_agreement, "fused_margin": margin,
        "margin_signal": margin_signal, "known_pattern_fraction": known,
        "difficulty_novelty": novelty, "forced_cold": forced_cold,
        "authority": "PRE_EXACT_COVERAGE_POLICY_ONLY__NOT_TRUTH",
    }


def coverage_runtime(e: dict[str, Any], learned_order: list[int], policy: dict[str, Any]) -> dict[str, Any]:
    n = len(learned_order)
    frac = float(policy["initial_coverage_fraction"])
    initial = n if frac >= 0.999999 else max(2, min(n, math.ceil(n * frac)))
    chunks = [learned_order[:initial]]
    remaining = learned_order[initial:]
    # Partial modes expand in equal-size ranked waves. COLD has exactly one full-field wave.
    while remaining:
        chunks.append(remaining[:initial]); remaining = remaining[initial:]

    total_checks = total_pairs = total_raw = 0
    wave_pair_latency = wave_raw_latency = 0
    attempts = []; chosen = None; chosen_index = None; waves_used = 0
    cap = int(e["local_stress_cap"])
    for wi, wave in enumerate(chunks, 1):
        waves_used += 1; wave_rows = []; safe_rows = []
        for idx in wave:
            pivot = e["vars"][idx]
            out, stats = st.eliminate_var_capped_2cnf_exact(e["cnf"], pivot, cap)
            raw = int(stats["raw_units"]); pairs = int(stats.get("pairs", 0)); fit = out is not None
            if fit:
                if not st.verify_transition_2cnf_exact(e["cnf"], pivot, out, cap):
                    raise AssertionError("coverage exact transition replay failed")
                safe_rows.append((raw, idx, pivot))
            row = {"wave": wi, "pivot_local_for_audit": pivot, "candidate_index": idx, "raw_units": raw, "pair_work": pairs, "fit": fit}
            wave_rows.append(row); attempts.append(row)
        total_checks += len(wave_rows)
        total_pairs += sum(r["pair_work"] for r in wave_rows)
        total_raw += sum(r["raw_units"] for r in wave_rows)
        wave_pair_latency += max((r["pair_work"] for r in wave_rows), default=0)
        wave_raw_latency += max((r["raw_units"] for r in wave_rows), default=0)
        if safe_rows:
            raw, chosen_index, chosen = min(safe_rows, key=lambda z: (z[0], learned_order.index(z[1])))
            break
    if chosen is None:
        raise AssertionError("full JUXTAPOSE expansion exhausted without safe root pivot")
    return {
        "exact_checks": total_checks,
        "pair_work": total_pairs,
        "raw_units_sum": total_raw,
        "peak_raw_units": max([e["root_units"]] + [r["raw_units"] for r in attempts]),
        "chosen_first_pivot_local_for_audit": chosen,
        "chosen_candidate_index": chosen_index,
        "root_attempts": attempts,
        "exact_transition_verified": True,
        "coverage_mode": policy["mode"],
        "coverage_ratio": total_checks / max(1, n),
        "initial_coverage_ratio": initial / max(1, n),
        "clone_count": total_checks,
        "available_pivots": n,
        "waves_used": waves_used,
        "parallel_pair_work_latency_proxy": wave_pair_latency,
        "parallel_raw_units_latency_proxy": wave_raw_latency,
        "parallel_exact_wave_latency_proxy": waves_used,
        "total_compute_is_not_free": True,
        "parallel_latency_is_proxy_not_walltime": True,
    }


def _score_ratio(static: dict[str, Any], learned: dict[str, Any]) -> float:
    return v2.efficiency_score(static, learned)


def coverage_stage_score(stage_eps: list[dict[str, Any]], teacher, student, train_pool, prior, weights) -> dict[str, Any]:
    totals = collections.defaultdict(lambda: collections.defaultdict(float))
    latency_totals = collections.defaultdict(float)
    top1 = 0; ranks = []; regrets = []; per = []; label_pair_work = 0
    mode_counts = collections.Counter(); coverage_ratios = []; confidences = []

    for e in stage_eps:
        comp = v1.adviser_scores(teacher, student, train_pool, e, prior)
        fused = v1.fuse(comp, weights)
        learned_order = v1.ranking_order(fused, e)
        static_order = sorted(range(len(e["vars"])), key=lambda i: e["vars"][i])
        oracle_order = e["oracle_root_order"]
        policy = uncertainty_policy(comp, fused, train_pool, e)

        static_rt = st.root_runtime_fast(e, static_order)
        learned_rt = coverage_runtime(e, learned_order, policy)
        oracle_rt = st.root_runtime_fast(e, oracle_order)
        rt = {"STATIC": static_rt, "KEYMASTER": learned_rt, "ORACLE": oracle_rt}

        br = v1.best_rank(learned_order, e); ranks.append(br); top1 += int(br == 1)
        regrets.append(e["raw"][learned_order[0]] - min(e["raw"]))
        label_pair_work += sum(int(x) for x in e["pair_labels"])
        for name, r in rt.items():
            for k in ("exact_checks", "pair_work", "raw_units_sum"):
                totals[name][k] += r[k]
            totals[name]["peak_raw_units"] = max(totals[name]["peak_raw_units"], r["peak_raw_units"])
        latency_totals["pair_work"] += learned_rt["parallel_pair_work_latency_proxy"]
        latency_totals["raw_units_sum"] += learned_rt["parallel_raw_units_latency_proxy"]
        latency_totals["exact_checks"] += learned_rt["parallel_exact_wave_latency_proxy"]
        latency_totals["peak_raw_units"] = max(latency_totals["peak_raw_units"], learned_rt["peak_raw_units"])
        mode_counts[policy["mode"]] += 1; coverage_ratios.append(learned_rt["coverage_ratio"]); confidences.append(policy["confidence"])
        per.append({
            "fingerprint": e["fingerprint"], "p": e["p"], "q": e["q"], "seed": e["seed"],
            "n": len(e["vars"]), "raw_span": e["raw_span"], "cap": e["local_stress_cap"],
            "best_rank": br, "uncertainty": policy,
            "static": static_rt, "keymaster_coverage": learned_rt, "oracle": oracle_rt,
            "adviser_top1_local_index": {k: v1.ranking_order(v, e)[0] for k, v in comp.items()},
        })

    agg = {k: dict(v) for k, v in totals.items()}
    latency = dict(latency_totals)
    compute_score = _score_ratio(agg["STATIC"], agg["KEYMASTER"])
    latency_score = _score_ratio(agg["STATIC"], latency)
    operational = math.exp(0.60 * math.log(max(1e-12, compute_score)) + 0.40 * math.log(max(1e-12, latency_score)))
    return {
        "performance_index": operational,
        "compute_efficiency_index": compute_score,
        "parallel_latency_proxy_index": latency_score,
        "operational_index_definition": "geometric blend: 60% total-compute efficiency + 40% idealized parallel-wave latency proxy",
        "aggregate": agg,
        "parallel_latency_proxy_aggregate": latency,
        "top1_best_recall": top1 / len(stage_eps),
        "topk_exact_best_recall": sum(1 for x in per if x["best_rank"] <= min(3, len(stage_eps[0]["vars"]))) / len(stage_eps),
        "mean_best_rank": sum(ranks) / len(ranks),
        "mean_top1_raw_regret": sum(regrets) / len(regrets),
        "oracle_label_pair_work": label_pair_work,
        "coverage": {
            "mean_coverage_ratio": sum(coverage_ratios) / len(coverage_ratios),
            "mean_confidence": sum(confidences) / len(confidences),
            "mode_counts": dict(mode_counts),
            "all_clone_compute_charged": True,
            "parallel_latency_is_not_walltime": True,
        },
        "per_formula": per,
    }


def main() -> int:
    # Warm-start data and governance are installed before v2.4 starts its normal
    # exact self-consistent training/pit-stop loop.
    v1.bootstrap_50 = warm_history_bootstrap
    v2.stage_score = coverage_stage_score

    rc = v24.main()
    if rc != 0:
        return rc

    # v2.4 already hardens/post-processes the boss. Add v3-specific provenance.
    out_dir = v24._out_dir_from_argv()
    if out_dir is None:
        raise AssertionError("--out-dir required")
    path = out_dir / "gauntlet-result.json"
    result = json.loads(path.read_text(encoding="utf-8"))
    result["schema"] = SCHEMA
    result["architecture_change_v3"] = {
        "name": "UNCERTAINTY_TO_JUXTAPOSE_COVERAGE",
        "JGPT_changed": False, "SLIME_changed": False, "M2R_changed": False, "SPIDER_changed": False,
        "prior_lessons_replayed_before_exam": True,
        "new_exam_fingerprints_learned_before_scoring": False,
        "cold_mode": "all root pivots exact-cloned in one full-field wave",
        "warm_mode": "ranked 50% waves with exact expansion if needed",
        "hot_mode": "ranked 20% waves with exact expansion if needed",
        "laws": [
            "LEARNING_MAY_REDUCE_SEARCH_BUT_MAY_NEVER_REMOVE_ABILITY_TO_SEARCH",
            "LOW_CONFIDENCE_RESTORES_JUXTAPOSE_COVERAGE",
            "PARALLELISM_IS_NOT_FREE_COMPUTE",
            "PARALLEL_LATENCY_PROXY_IS_NOT_MEASURED_WALLTIME",
            "MODEL_PREDICTION_IS_NOT_PROOF",
            "EXACT_REPLAY_REMAINS_AUTHORITY",
        ],
    }
    result["warm_start_provenance"] = result.get("bootstrap", {})
    result["scientific_firewall"]["WARM_HISTORY_LOADED_BEFORE_NEW_EXAM"] = True
    result["scientific_firewall"]["JUXTAPOSE_COLD_MODE_COVERS_ALL_ROOT_PIVOTS"] = True
    result["scientific_firewall"]["ALL_CLONE_COMPUTE_IS_CHARGED"] = True
    result["scientific_firewall"]["PARALLEL_LATENCY_PROXY_IS_NOT_WALLTIME"] = True
    result["scientific_firewall"]["P_VS_NP"] = P_VS_NP
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "V3_POSTPROCESS": "PASS",
        "official_frontier": result.get("official_frontier"),
        "stop_reason": result.get("stop_reason"),
        "boss_score": None if result.get("boss_250x250") is None else result["boss_250x250"].get("score"),
        "warm_lessons": result.get("bootstrap", {}).get("total_exact_lesson_formulas"),
        "P_VS_NP": P_VS_NP,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
