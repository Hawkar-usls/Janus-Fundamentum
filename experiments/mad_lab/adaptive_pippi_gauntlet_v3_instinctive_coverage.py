#!/usr/bin/env python3
"""JANUS PIPPI gauntlet v3 — warm memory + instinctive JUXTAPOSE coverage.

Purpose
=======
Generation 3 starts with lessons already earned by earlier exact experiments,
not with an epistemically blank model.  Past holdouts are now historical
experience and may be replayed into TRAIN/CALIBRATION because the new race uses
a disjoint deterministic seed namespace.

Warm lessons imported before the first fresh stage:
- the frozen 24-formula exact 50:50 bootstrap;
- all eight scored stages from ruthless v2.4, including the failed 44:47 shock
  and three 31:31 recovery laps;
- all four corrected strict-min 250:250 boss formulas from v2.4;
- v1.2's ADVISER_MONOCULTURE__SMALL_N_CALIBRATION lesson through unchanged
  Keymaster governance v2;
- the permanent v2.4 KLGJ events are loaded before new events are appended.

New controlled capability
=========================
Learning never removes the ability to search.  Before inspecting exact labels
of a fresh formula, Keymaster estimates prediction authority from ONLY:
- historical geometry lessons;
- adviser agreement;
- fused-score margin;
- amount of nearby exact historical support.

Three modes follow:
  COLD_JUXTAPOSE_FULL: all available root pivots receive exact clone probes.
  WARM_JUXTAPOSE_HYBRID: a structurally diversified field subset is probed in
    one parallel wave; if no safe root is found, the untouched field is opened.
  HOT_PREDICTIVE: advisers only order normal sequential exact checks.

A coverage wave has two ledgers.  Latency proxy assumes ideal parallel clones
and charges the maximum probe work in each wave.  Total compute charges EVERY
clone.  The race controller uses latency proxy because the proposed mechanism
is parallel field coverage; PIPPI/KLGJ keeps total compute so parallelism is
never misreported as free computation.

Every clone probe uses the exact width<=2 replay engine that is self-tested for
bit/accounting equality against canonical JANUS elimination semantics.  Models,
attention, geometry priors and uncertainty never decide truth. P_VS_NP=OPEN.
"""
from __future__ import annotations

import copy
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from experiments.mad_lab import adaptive_pippi_pitstop_ladder as v1
from experiments.mad_lab import adaptive_pippi_gauntlet_v2 as v2
from experiments.mad_lab import asymmetric_pq_track_relabelled as relabel
from experiments.mad_lab import keymaster_scalable_feature_tokens as sf
from experiments.mad_lab import keymaster_scalable_exact_root_labels as sl
from experiments.mad_lab import keymaster_scalable_exact_2cnf_transition as st
from experiments.mad_lab import keymaster_adviser_governance_v2 as gov
from experiments.mad_lab import keymaster_learning_gain_journal as klgj

P_VS_NP = "OPEN"
SCHEMA = "JANUS/PIPPI/WARM-INSTINCTIVE-JUXTAPOSE-GAUNTLET/v3.0.0"
HIST_BASE = 1_300_000_000
FRESH_BASE = 3_700_000_000
BOSS_COUNT = 4

V2_RESULT = Path("data/keymaster/PIPPI_RUTHLESS_GAUNTLET_V2_4_RESULT_2026-08-28.json")
V1_RESULT = Path("data/keymaster/PIPPI_ADAPTIVE_PITSTOP_LADDER_RESULT_2026-08-28_v1.0.json")
V2_EVENTS = Path("data/keymaster/journal/PIPPI_RUTHLESS_GAUNTLET_V2_4_KLGJ_EVENTS_2026-08-28.jsonl")
SEED_JOURNAL_NAME = "KEYMASTER_LEARNING_GAIN_JOURNAL_SEED_v1.0.jsonl"

ORIG_BOOTSTRAP_50 = v1.bootstrap_50
ORIG_TRAIN_MODELS = v1.train_models
ORIG_READ_JSONL = klgj.read_jsonl
ORIG_CHOOSE_GOVERNED = gov.choose_fusion_governed

WARM_AUDIT: dict[str, Any] = {}
COVERAGE_STAGE_AUDIT: list[dict[str, Any]] = []
LESSON_POINTS: list[dict[str, Any]] = []
BOSS_FPS: list[str] = []
BOSS_SAFE_COUNTS: list[int] = []
BOSS_RAW_HISTS: list[dict[str, int]] = []
FIRST_GOVERNANCE_CALL = True
PRIOR_V2: dict[str, Any] = {}
PRIOR_V1: dict[str, Any] = {}


def clip(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, float(x)))


def _pq(label: str) -> tuple[int, int]:
    a, b = label.split(":", 1)
    return int(a), int(b)


def _lesson_authority(score: float, top1: float | None, regression: bool = False) -> float:
    perf = clip((float(score) - 80.0) / 20.0)
    t = 0.5 if top1 is None else clip(top1)
    a = 0.75 * perf + 0.25 * t
    if regression:
        a = min(a, 0.35)
    return clip(a)


def load_prior_lessons() -> None:
    global PRIOR_V2, PRIOR_V1, LESSON_POINTS
    PRIOR_V2 = json.loads(V2_RESULT.read_text())
    PRIOR_V1 = json.loads(V1_RESULT.read_text())
    pts: list[dict[str, Any]] = []

    for h in PRIOR_V2.get("history", []):
        p, q = _pq(h["difficulty"])
        pts.append({
            "p": p, "q": q, "authority": _lesson_authority(h["score"], h.get("top1"), h.get("score", 100.0) < 80.0),
            "score": float(h["score"]), "top1": h.get("top1"),
            "source": "FROZEN_RUTHLESS_V2_4", "pre_learning_prediction": True,
        })

    for h in PRIOR_V1.get("race_history", []):
        p, q = _pq(h["difficulty"])
        regression = "REGRESSION" in str(h.get("state", ""))
        pts.append({
            "p": p, "q": q,
            "authority": _lesson_authority(h["score"], h.get("top1_best_recall"), regression),
            "score": float(h["score"]), "top1": h.get("top1_best_recall"),
            "source": "FROZEN_PITSTOP_V1_2", "pre_learning_prediction": True,
        })

    boss = PRIOR_V2["hard_boss_250x250"] if "hard_boss_250x250" in PRIOR_V2 else PRIOR_V2.get("boss_250x250")
    if boss is None:
        # Canonical frozen summary stores hard boss under hard_boss_250x250.
        boss = PRIOR_V2.get("hard_boss_250x250")
    if boss:
        agg = boss.get("aggregate", {})
        kchecks = float(agg.get("KEYMASTER", {}).get("exact_checks", 161.0))
        formulas = max(1.0, float(boss.get("formula_count", 4)))
        n = max(1.0, float(boss.get("n", 252)))
        mean_rank = float(boss.get("mean_best_rank", kchecks / formulas))
        top1 = float(boss.get("top1_best_recall", 0.0))
        rank_quality = clip(1.0 - max(0.0, mean_rank - 1.0) / max(1.0, n - 1.0))
        authority = min(0.70, 0.45 + 0.25 * rank_quality + 0.30 * top1)
        pts.append({
            "p": 250, "q": 250, "authority": authority,
            "score": float(boss.get("score", 100.0)), "top1": top1,
            "source": "FROZEN_HARD_BOSS_250x250_V2_4", "pre_learning_prediction": True,
        })

    LESSON_POINTS = pts


def geometry_vector(p: int, q: int) -> tuple[float, float, float]:
    s = math.log1p(p + q)
    asym = abs(p - q) / max(1.0, float(p + q))
    ratio = abs(math.log((p + 1.0) / (q + 1.0)))
    return s, asym, ratio


def geometry_distance(p: int, q: int, a: int, b: int) -> float:
    x = geometry_vector(p, q); y = geometry_vector(a, b)
    return abs(x[0] - y[0]) / 1.5 + 4.0 * abs(x[1] - y[1]) + 0.75 * abs(x[2] - y[2])


def geometry_prior(p: int, q: int) -> tuple[float, dict[str, Any]]:
    exact = [x for x in LESSON_POINTS if x["p"] == p and x["q"] == q]
    if exact:
        vals = [float(x["authority"]) for x in exact]
        # Conservative aggregation preserves remembered regressions.
        value = 0.70 * (sum(vals) / len(vals)) + 0.30 * min(vals)
        return clip(value), {"kind": "EXACT_GEOMETRY_HISTORY", "matches": len(exact), "authorities": vals}
    if not LESSON_POINTS:
        return 0.0, {"kind": "NO_HISTORY"}
    ranked = sorted(
        ((geometry_distance(p, q, x["p"], x["q"]), x) for x in LESSON_POINTS),
        key=lambda z: (z[0], z[1]["p"], z[1]["q"], z[1]["source"]),
    )[:5]
    weighted = []
    for d, x in ranked:
        sim = math.exp(-d)
        weighted.append((sim, float(x["authority"]), x))
    den = sum(s for s, _, _ in weighted)
    value = sum(s * a for s, a, _ in weighted) / den if den > 1e-12 else 0.0
    return clip(value), {
        "kind": "NEAREST_GEOMETRY_HISTORY",
        "neighbors": [{"p": x["p"], "q": x["q"], "distance": d, "authority": x["authority"], "source": x["source"]} for d, x in ranked],
    }


def historical_support(train_pool: list[dict[str, Any]], p: int, q: int) -> tuple[float, int]:
    near = 0
    for e in train_pool:
        ep, eq = int(e.get("p", e.get("d", 0))), int(e.get("q", e.get("d", 0)))
        if geometry_distance(p, q, ep, eq) <= 0.18:
            near += 1
    return clip(math.log1p(near) / math.log(13.0)), near


def prediction_authority(e: dict[str, Any], comp: dict[str, list[float]], weights: dict[str, float], train_pool: list[dict[str, Any]]) -> dict[str, Any]:
    p, q = int(e["p"]), int(e["q"])
    gp, gaudit = geometry_prior(p, q)
    tops = [v1.ranking_order(comp[k], e)[0] for k in gov.NAMES]
    counts = Counter(tops)
    agreement = max(counts.values()) / len(gov.NAMES)
    fused = v1.fuse(comp, weights)
    vals = sorted(float(x) for x in fused)
    if len(vals) <= 1:
        margin_conf = 1.0
    else:
        spread = max(vals[-1] - vals[0], 1e-9)
        margin_conf = clip((vals[1] - vals[0]) / spread * 4.0)
    support, support_n = historical_support(train_pool, p, q)
    authority = 0.45 * gp + 0.25 * agreement + 0.15 * margin_conf + 0.15 * support
    # A remembered exact-geometry failure forces wide eyes even if advisers agree.
    exact_low = [x for x in LESSON_POINTS if x["p"] == p and x["q"] == q and x["authority"] < 0.20]
    if exact_low:
        authority = min(authority, 0.40)
    authority = clip(authority)
    return {
        "authority": authority,
        "geometry_prior": gp,
        "geometry_audit": gaudit,
        "adviser_top1_agreement": agreement,
        "adviser_top1_indices": tops,
        "fused_margin_confidence": margin_conf,
        "nearby_exact_support": support_n,
        "nearby_support_score": support,
    }


def diversified_subset(pred_order: list[int], e: dict[str, Any], k: int) -> list[int]:
    n = len(pred_order); k = max(1, min(n, k))
    chosen: list[int] = []
    # Half exploitation, half structural field anchors. No raw/oracle labels are used.
    exploit = max(1, (k + 1) // 2)
    chosen.extend(pred_order[:exploit])
    structural = sorted(range(n), key=lambda i: v1.stable_hash(e["tokens"][i]))
    need = k - len(set(chosen))
    if need > 0:
        if need == 1:
            anchors = [structural[len(structural) // 2]]
        else:
            anchors = [structural[round(j * (len(structural) - 1) / max(1, need - 1))] for j in range(need)]
        chosen.extend(anchors)
    out = []
    seen = set()
    for i in chosen + structural:
        if i not in seen:
            seen.add(i); out.append(i)
        if len(out) >= k:
            break
    return out


def exact_clone_wave(e: dict[str, Any], indices: list[int]) -> dict[str, Any]:
    cap = int(e["local_stress_cap"])
    probes = []
    safe = []
    total_pairs = 0; total_raw = 0; max_pairs = 0; max_raw = 0
    for idx in indices:
        pivot = e["vars"][idx]
        out, stats = st.eliminate_var_capped_2cnf_exact(e["cnf"], pivot, cap)
        raw = int(stats["raw_units"]); pairs = int(stats.get("pairs", 0))
        fit = out is not None
        if fit:
            if not st.verify_transition_2cnf_exact(e["cnf"], pivot, out, cap):
                raise AssertionError("coverage clone exact transition verification failed")
            safe.append((raw, v1.stable_hash(e["tokens"][idx]), idx, pivot))
        probes.append({"index": idx, "pivot_local_for_audit": pivot, "raw_units": raw, "pair_work": pairs, "fit": fit})
        total_pairs += pairs; total_raw += raw; max_pairs = max(max_pairs, pairs); max_raw = max(max_raw, raw)
    chosen = min(safe)[2] if safe else None
    return {
        "indices": list(indices), "probes": probes, "chosen_index": chosen,
        "compute_exact_checks": len(indices), "compute_pair_work": total_pairs, "compute_raw_units_sum": total_raw,
        "latency_exact_waves": 1, "latency_pair_work": max_pairs, "latency_raw_units": max_raw,
        "safe_found": chosen is not None,
    }


def instinctive_runtime(e: dict[str, Any], pred_order: list[int], auth: dict[str, Any]) -> dict[str, Any]:
    n = len(pred_order); authority = float(auth["authority"])
    if authority < 0.42:
        mode = "COLD_JUXTAPOSE_FULL"
        waves = [exact_clone_wave(e, list(range(n)))]
    elif authority < 0.70:
        mode = "WARM_JUXTAPOSE_HYBRID"
        # Authority gradually shrinks the first field wave from 65% to 22%.
        frac = 0.65 - ((authority - 0.42) / 0.28) * 0.43
        k = max(2, min(n, int(math.ceil(n * clip(frac, 0.22, 0.65)))))
        first = diversified_subset(pred_order, e, k)
        waves = [exact_clone_wave(e, first)]
        if not waves[0]["safe_found"]:
            remaining = [i for i in range(n) if i not in set(first)]
            waves.append(exact_clone_wave(e, remaining))
    else:
        mode = "HOT_PREDICTIVE"
        rt = st.root_runtime_fast(e, pred_order)
        return {
            "mode": mode,
            "latency": dict(rt),
            "compute": dict(rt),
            "coverage_ratio": rt["exact_checks"] / max(1, n),
            "parallel_clone_count": 1,
            "waves": [],
            "chosen_index": e["vars"].index(rt["chosen_first_pivot_local_for_audit"]),
            "authority_audit": auth,
        }

    chosen_candidates = []
    for w in waves:
        if w["chosen_index"] is not None:
            idx = int(w["chosen_index"])
            chosen_candidates.append((e["raw"][idx], v1.stable_hash(e["tokens"][idx]), idx))
            break  # earliest successful parallel wave wins latency semantics.
    if not chosen_candidates:
        raise AssertionError("JUXTAPOSE coverage exhausted field without a safe root pivot")
    chosen_idx = min(chosen_candidates)[2]
    total_checks = sum(w["compute_exact_checks"] for w in waves)
    total_pairs = sum(w["compute_pair_work"] for w in waves)
    total_raw = sum(w["compute_raw_units_sum"] for w in waves)
    latency_waves = len(waves)
    latency_pairs = sum(w["latency_pair_work"] for w in waves)
    latency_raw = sum(w["latency_raw_units"] for w in waves)
    latency = {
        "exact_checks": latency_waves,
        "pair_work": latency_pairs,
        "raw_units_sum": latency_raw,
        "peak_raw_units": max([e["root_units"]] + [w["latency_raw_units"] for w in waves]),
        "chosen_first_pivot_local_for_audit": e["vars"][chosen_idx],
        "exact_transition_verified": True,
        "metric_semantics": "IDEAL_PARALLEL_CLONE_WAVE_LATENCY_PROXY",
    }
    compute = {
        "exact_checks": total_checks,
        "pair_work": total_pairs,
        "raw_units_sum": total_raw,
        "peak_raw_units": max([e["root_units"]] + [max((p["raw_units"] for p in w["probes"]), default=0) for w in waves]),
        "chosen_first_pivot_local_for_audit": e["vars"][chosen_idx],
        "exact_transition_verified": True,
        "metric_semantics": "TOTAL_EXACT_CLONE_COMPUTE",
    }
    return {
        "mode": mode, "latency": latency, "compute": compute,
        "coverage_ratio": total_checks / max(1, n),
        "parallel_clone_count": max((w["compute_exact_checks"] for w in waves), default=1),
        "waves": waves, "chosen_index": chosen_idx, "authority_audit": auth,
    }


def stage_score_instinctive(stage_eps: list[dict[str, Any]], teacher, student, train_pool, prior, weights) -> dict[str, Any]:
    compute_totals = defaultdict(lambda: defaultdict(float))
    latency_totals = defaultdict(lambda: defaultdict(float))
    top1 = 0; ranks = []; regrets = []; per = []; label_pair_work = 0
    modes = Counter(); coverage_ratios = []; clone_compute_pairs = 0; clone_compute_checks = 0
    predictive_stage_rows = []

    for e in stage_eps:
        comp = v1.adviser_scores(teacher, student, train_pool, e, prior)
        learned_order = v1.ranking_order(v1.fuse(comp, weights), e)
        static_order = sorted(range(len(e["vars"])), key=lambda i: e["vars"][i])
        oracle_order = e["oracle_root_order"]
        authority = prediction_authority(e, comp, weights, train_pool)
        inst = instinctive_runtime(e, learned_order, authority)
        rt_static = st.root_runtime_fast(e, static_order)
        rt_oracle = st.root_runtime_fast(e, oracle_order)
        rt_compute = inst["compute"]; rt_latency = inst["latency"]

        br = v1.best_rank(learned_order, e)
        ranks.append(br); top1 += int(br == 1)
        regrets.append(e["raw"][learned_order[0]] - min(e["raw"]))
        predictive_stage_rows.append({"rank": br, "n": len(e["vars"]), "top1": br == 1})
        label_pair_work += sum(int(x) for x in e["pair_labels"])
        modes[inst["mode"]] += 1; coverage_ratios.append(float(inst["coverage_ratio"]))
        clone_compute_pairs += int(rt_compute["pair_work"]); clone_compute_checks += int(rt_compute["exact_checks"])

        for name, r in (("STATIC", rt_static), ("KEYMASTER", rt_compute), ("ORACLE", rt_oracle)):
            for k in ("exact_checks", "pair_work", "raw_units_sum"):
                compute_totals[name][k] += float(r[k])
            compute_totals[name]["peak_raw_units"] = max(compute_totals[name]["peak_raw_units"], float(r["peak_raw_units"]))
        for name, r in (("STATIC", rt_static), ("KEYMASTER", rt_latency), ("ORACLE", rt_oracle)):
            for k in ("exact_checks", "pair_work", "raw_units_sum"):
                latency_totals[name][k] += float(r[k])
            latency_totals[name]["peak_raw_units"] = max(latency_totals[name]["peak_raw_units"], float(r["peak_raw_units"]))

        per.append({
            "fingerprint": e["fingerprint"], "p": e["p"], "q": e["q"], "seed": e["seed"],
            "n": len(e["vars"]), "raw_span": e["raw_span"], "cap": e["local_stress_cap"],
            "predictive_best_rank_before_exact_coverage": br,
            "static": rt_static, "keymaster_total_compute": rt_compute,
            "keymaster_latency_proxy": rt_latency, "oracle": rt_oracle,
            "instinctive_mode": inst["mode"], "coverage_ratio": inst["coverage_ratio"],
            "parallel_clone_count": inst["parallel_clone_count"], "authority": inst["authority_audit"],
            "coverage_waves": inst["waves"],
            "adviser_top1_local_index": {k: v1.ranking_order(v, e)[0] for k, v in comp.items()},
        })

    agg_compute = {k: dict(v) for k, v in compute_totals.items()}
    agg_latency = {k: dict(v) for k, v in latency_totals.items()}
    score = v2.efficiency_score(agg_latency["STATIC"], agg_latency["KEYMASTER"])

    # Only PRE-learning predictive quality becomes a lesson point. Coverage success
    # itself does not grant prediction authority; the next fresh formula must earn it.
    if stage_eps:
        p = int(stage_eps[0]["p"]); q = int(stage_eps[0]["q"])
        mean_rank_frac = sum((r["rank"] - 1) / max(1, r["n"] - 1) for r in predictive_stage_rows) / len(predictive_stage_rows)
        pred_top1 = sum(int(r["top1"]) for r in predictive_stage_rows) / len(predictive_stage_rows)
        rank_quality = clip(1.0 - mean_rank_frac)
        observed_authority = clip(0.65 * pred_top1 + 0.35 * rank_quality)
        LESSON_POINTS.append({
            "p": p, "q": q, "authority": observed_authority,
            "score": score, "top1": pred_top1,
            "source": "V3_FRESH_PRE_LEARNING_PREDICTION", "pre_learning_prediction": True,
        })

    audit = {
        "p": int(stage_eps[0]["p"]) if stage_eps else None,
        "q": int(stage_eps[0]["q"]) if stage_eps else None,
        "difficulty": stage_eps[0]["difficulty"] if stage_eps else None,
        "formula_count": len(stage_eps), "performance_index_latency_proxy": score,
        "mode_counts": dict(modes), "mean_coverage_ratio": sum(coverage_ratios) / max(1, len(coverage_ratios)),
        "total_clone_compute_exact_checks": clone_compute_checks,
        "total_clone_compute_pair_work": clone_compute_pairs,
        "latency_proxy": agg_latency.get("KEYMASTER", {}), "total_compute": agg_compute.get("KEYMASTER", {}),
        "predictive_top1_before_coverage": top1 / max(1, len(stage_eps)),
        "predictive_mean_best_rank_before_coverage": sum(ranks) / max(1, len(ranks)),
    }
    COVERAGE_STAGE_AUDIT.append(audit)

    return {
        "performance_index": score,
        "aggregate": agg_compute,
        "latency_proxy_aggregate": agg_latency,
        "top1_best_recall": top1 / len(stage_eps),
        "topk_exact_best_recall": sum(1 for x in per if x["predictive_best_rank_before_exact_coverage"] <= min(3, len(stage_eps[0]["vars"]))) / len(stage_eps),
        "mean_best_rank": sum(ranks) / len(ranks),
        "mean_top1_raw_regret": sum(regrets) / len(regrets),
        "oracle_label_pair_work": label_pair_work,
        "coverage": audit,
        "per_formula": per,
    }


def hist_seed(p: int, q: int, serial: int, j: int) -> int:
    return HIST_BASE + serial * 100_003 + p * 1019 + q * 1031 + j * 43


def fresh_seed(p: int, q: int, serial: int, j: int) -> int:
    return FRESH_BASE + serial * 100_003 + p * 1019 + q * 1031 + j * 43


def exact_episode(cnf, p: int, q: int, seed: int, source: str, stage_serial: int) -> dict[str, Any]:
    e = sl.exact_track_episode_fast(cnf, p, q, seed, source, stage_serial)
    if "MANDATORY_BLIND_250x250_BOSS" in source:
        cap = min(e["raw"])
        e["local_stress_cap"] = cap
        e["safe_indices"] = [i for i, x in enumerate(e["raw"]) if x <= cap]
        e["boss_cap_policy"] = "EXACT_MIN_RAW_ONLY"
        if source.startswith("MANDATORY_BLIND"):
            BOSS_FPS.append(e["fingerprint"])
            BOSS_SAFE_COUNTS.append(len(e["safe_indices"]))
            hist: dict[str, int] = {}
            for x in e["raw"]:
                hist[str(x)] = hist.get(str(x), 0) + 1
            BOSS_RAW_HISTS.append(hist)
    return e


def make_fresh_stage(p: int, q: int, stage_serial: int, count: int, used: set[str], source: str = "RUTHLESS_PQ_TRACK"):
    if "MANDATORY_BLIND_250x250_BOSS" in source:
        count = BOSS_COUNT
    out = []; metas = []; j = 0
    import time
    t0 = time.perf_counter()
    while len(out) < count:
        seed = fresh_seed(p, q, stage_serial, j)
        cnf, meta = relabel.construct_relabelled(p, q, seed)
        e = exact_episode(cnf, p, q, seed, source, stage_serial)
        j += 1
        if e["fingerprint"] in used:
            continue
        used.add(e["fingerprint"]); out.append(e); metas.append(meta)
    return out, {"generation_wall_seconds": time.perf_counter() - t0, "metas": metas, "seed_namespace": FRESH_BASE}


def historical_episode(p: int, q: int, serial: int, j: int, source: str, strict_boss: bool = False) -> dict[str, Any]:
    seed = hist_seed(p, q, serial, j)
    cnf, _ = relabel.construct_relabelled(p, q, seed)
    e = sl.exact_track_episode_fast(cnf, p, q, seed, source, serial)
    if strict_boss:
        cap = min(e["raw"])
        e["local_stress_cap"] = cap
        e["safe_indices"] = [i for i, x in enumerate(e["raw"]) if x <= cap]
        e["boss_cap_policy"] = "EXACT_MIN_RAW_ONLY"
    return e


def warm_bootstrap(used: set[str]):
    memory, base_audit = ORIG_BOOTSTRAP_50(used)
    replayed = []
    specs = [(1, 1), (11, 11), (21, 21), (31, 31), (44, 47), (31, 31), (31, 31), (31, 31)]
    for serial, (p, q) in enumerate(specs, start=1):
        for j in range(4):
            e = historical_episode(p, q, serial, j, "HISTORICAL_RUTHLESS_V2_4_REPLAY")
            if e["fingerprint"] in used:
                continue
            used.add(e["fingerprint"]); memory.append(e); replayed.append(e)
    boss_replayed = []
    for j in range(BOSS_COUNT):
        e = historical_episode(250, 250, 9, j, "HISTORICAL_MANDATORY_BLIND_250x250_BOSS", strict_boss=True)
        if e["fingerprint"] in used:
            continue
        used.add(e["fingerprint"]); memory.append(e); replayed.append(e); boss_replayed.append(e["fingerprint"])

    expected_boss = set(PRIOR_V2["hard_boss_250x250"]["fresh_fingerprints"])
    if set(boss_replayed) != expected_boss:
        raise AssertionError({"historical_boss_replay_mismatch": {"expected": sorted(expected_boss), "actual": sorted(boss_replayed)}})

    WARM_AUDIT.update({
        "base_50_exact_formulas": base_audit["formulas"],
        "replayed_ruthless_stage_formulas": len(replayed) - len(boss_replayed),
        "replayed_hard_boss_250_formulas": len(boss_replayed),
        "warm_exact_episode_total": len(memory),
        "previous_v2_4_boss_fingerprints_replayed": True,
        "v1_2_governance_lesson_imported": "ADVISER_MONOCULTURE__SMALL_N_CALIBRATION",
        "new_seed_namespace": FRESH_BASE,
        "historical_seed_namespace": HIST_BASE,
        "route_exhaustive_replay_performed": False,
    })
    return memory, {**base_audit, **WARM_AUDIT, "source": "WARM_HISTORY_50_PLUS_V2_4_EXACT_REPLAY"}


def warm_train_models(teacher, teacher_opt, student, train_pool, focus_patterns, max_eps: int = 48):
    # Do not throw away earned lessons merely because v1 used a small recent window.
    return ORIG_TRAIN_MODELS(teacher, teacher_opt, student, train_pool, focus_patterns, max_eps=96)


def warm_read_jsonl(path: Path):
    rows = ORIG_READ_JSONL(path)
    if path.name == SEED_JOURNAL_NAME and V2_EVENTS.exists():
        old = ORIG_READ_JSONL(V2_EVENTS)
        by_id = {r.get("event_id"): r for r in rows if r.get("event_id")}
        for r in old:
            eid = r.get("event_id")
            if eid and eid not in by_id:
                rows.append(r); by_id[eid] = r
        WARM_AUDIT["prior_klgj_events_loaded"] = len(rows)
        WARM_AUDIT["prior_v2_4_events_merged"] = len(old)
    return rows


def warm_choose_governed(teacher, student, train, calib, prior, previous_weights=None, previous_metrics=None):
    global FIRST_GOVERNANCE_CALL
    if FIRST_GOVERNANCE_CALL:
        FIRST_GOVERNANCE_CALL = False
        previous_weights = dict(PRIOR_V2["final_fusion_weights"])
        previous_metrics = copy.deepcopy(PRIOR_V2["final_adviser_metrics"])
    return ORIG_CHOOSE_GOVERNED(
        teacher, student, train, calib, prior,
        previous_weights=previous_weights,
        previous_metrics=previous_metrics,
    )


def _out_dir_from_argv() -> Path | None:
    if "--out-dir" not in sys.argv:
        return None
    i = sys.argv.index("--out-dir")
    return Path(sys.argv[i + 1]) if i + 1 < len(sys.argv) else None


def postprocess(out: Path) -> None:
    path = out / "gauntlet-result.json"
    result = json.loads(path.read_text())
    boss = result.get("boss_250x250")
    if boss is None:
        raise AssertionError("v3 requires completed boss receipt")
    boss["formula_count"] = len(BOSS_FPS)
    boss["fresh_fingerprints"] = list(BOSS_FPS)
    boss["strict_min_raw_cap"] = True
    boss["cap_policy"] = "EXACT_MIN_RAW_ONLY"
    boss["safe_pivot_counts_per_formula"] = list(BOSS_SAFE_COUNTS)
    boss["raw_unit_histograms_per_formula"] = list(BOSS_RAW_HISTS)
    boss["numeric_static_baseline_decorrelated_by_seeded_isomorphic_relabelling"] = True

    warm_fps = set(PRIOR_V2["hard_boss_250x250"]["fresh_fingerprints"])
    fresh_boss = set(BOSS_FPS)
    modes = Counter()
    coverage_values = []
    total_compute = 0; total_latency = 0; total_checks = 0
    for x in COVERAGE_STAGE_AUDIT:
        modes.update(x["mode_counts"])
        coverage_values.append(x["mean_coverage_ratio"])
        total_compute += float(x["total_clone_compute_pair_work"])
        total_latency += float(x["latency_proxy"].get("pair_work", 0.0))
        total_checks += int(x["total_clone_compute_exact_checks"])

    result["schema"] = SCHEMA
    result["warm_start"] = dict(WARM_AUDIT)
    result["warm_start"]["previous_v2_4_frontier"] = PRIOR_V2["official_frontier"]
    result["warm_start"]["previous_v1_2_frontier"] = PRIOR_V1["frontier"]
    result["warm_start"]["previous_final_fusion_weights"] = PRIOR_V2["final_fusion_weights"]
    result["warm_start"]["previous_final_adviser_metrics"] = PRIOR_V2["final_adviser_metrics"]
    result["warm_start"]["new_boss_fingerprints_disjoint_from_previous_boss"] = warm_fps.isdisjoint(fresh_boss)
    result["instinctive_juxtapose"] = {
        "policy": {
            "COLD": "authority<0.42 -> exact clone on every available root pivot",
            "WARM": "0.42<=authority<0.70 -> diversified partial field wave, then widen if needed",
            "HOT": "authority>=0.70 -> predictive sequential exact checks",
            "authority_inputs": ["historical geometry only", "adviser agreement", "fused-score margin", "nearby exact historical support"],
            "current_fresh_exact_labels_used_to_choose_mode": False,
        },
        "stage_telemetry": COVERAGE_STAGE_AUDIT,
        "mode_counts": dict(modes),
        "mean_stage_coverage_ratio": sum(coverage_values) / max(1, len(coverage_values)),
        "total_clone_compute_exact_checks": total_checks,
        "total_clone_compute_pair_work": total_compute,
        "total_parallel_latency_pair_work_proxy": total_latency,
        "latency_proxy_assumption": "IDEAL_PARALLEL_CLONES__NOT_GITHUB_WALL_TIME",
        "total_compute_is_not_free": True,
    }
    result["generation_comparison"] = {
        "v1_2_frontier": PRIOR_V1["frontier"]["difficulty"],
        "v2_4_frontier": f"{PRIOR_V2['official_frontier']['p']}:{PRIOR_V2['official_frontier']['q']}",
        "v3_frontier": f"{result['official_frontier']['p']}:{result['official_frontier']['q']}",
        "frontier_difference_is_not_clean_single-variable_causal_AB": True,
        "reason": "v3 starts with earned historical lessons and adds uncertainty-triggered coverage; it is a next-generation test, not a blank-state ablation.",
    }
    fw = result["scientific_firewall"]
    fw.update({
        "WARM_START_USES_ONLY_PREVIOUSLY_SCORED_EXACT_LESSONS": True,
        "NEW_RACE_FINGERPRINTS_USE_DISJOINT_SEED_NAMESPACE": True,
        "NEW_BOSS_FINGERPRINTS_DISJOINT_FROM_PREVIOUS_BOSS": warm_fps.isdisjoint(fresh_boss),
        "UNCERTAINTY_MODE_DOES_NOT_READ_CURRENT_EXACT_LABELS": True,
        "ALL_COVERAGE_PROBES_USE_EXACT_WIDTH2_REPLAY": True,
        "CHOSEN_COVERAGE_TRANSITIONS_EXACT_VERIFIED": True,
        "LATENCY_PROXY_SEPARATE_FROM_TOTAL_COMPUTE": True,
        "PARALLELISM_IS_NOT_FREE_COMPUTE": True,
        "LEARNING_MAY_REDUCE_SEARCH_BUT_NOT_REMOVE_SEARCH": True,
        "BOSS_REQUIRES_EXACT_MIN_RAW_PIVOT": True,
        "BOSS_FORMULA_COUNT": BOSS_COUNT,
        "P_VS_NP": P_VS_NP,
    })
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "V3_POSTPROCESS": "PASS",
        "warm_exact_episodes": WARM_AUDIT.get("warm_exact_episode_total"),
        "mode_counts": dict(modes),
        "previous_frontier": PRIOR_V2["official_frontier"],
        "new_frontier": result["official_frontier"],
        "boss_score": boss.get("score"),
        "boss_safe_counts": BOSS_SAFE_COUNTS,
        "P_VS_NP": P_VS_NP,
    }, indent=2, sort_keys=True))


def main() -> int:
    load_prior_lessons()
    # Exact scalable semantics and corrected benchmark geometry from v2.4.
    v1.candidate_tokens = sf.candidate_tokens_fast
    v2.exact_pq_episode = exact_episode
    v2.pqtrack.construct = relabel.construct_relabelled
    v2.root_runtime = st.root_runtime_fast
    v2.make_pq_stage = make_fresh_stage
    v2.stage_score = stage_score_instinctive

    # Warm-start state reconstruction.
    v1.bootstrap_50 = warm_bootstrap
    v1.train_models = warm_train_models
    klgj.read_jsonl = warm_read_jsonl
    gov.choose_fusion_governed = warm_choose_governed

    rc = v2.main()
    out = _out_dir_from_argv()
    if rc == 0 and out is not None:
        postprocess(out)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
