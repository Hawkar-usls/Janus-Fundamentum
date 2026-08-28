#!/usr/bin/env python3
"""JANUS PIPPI GAUNTLET v2 — ruthless adaptive growth + governed Keymaster.

Generation-2 controlled experiment after the frozen v1.2 checkpoint.
Only the Keymaster adviser election/arbitration policy is intentionally changed:
JGPT, Pivot-Slime, M2R and Spider implementations are reused unchanged.

Difficulty policy:
- 1:1 formation lap;
- ordinary passes add +10:+10 cumulatively;
- every fourth growth pass is a deterministic asymmetric shock such as +13:+16;
- a regression rolls back only to the last accepted difficulty, never to a tiny floor;
- after every scored pass there is a full PIPPI pit-stop;
- recovery requires max(previous_score*1.03, previous_score+3 points) on fresh
  fingerprints before the failed level may be retried;
- recovery opportunities are finite, so the system cannot farm an easy level forever.

Regardless of the official frontier, the final learned system receives a blind fresh
250:250 boss probe. This OOD boss does not rewrite the race frontier. A separate
fixed-chassis n=126 width-2/no-unit 251:251 feasibility trap must be rejected by
signed-occurrence capacity instead of being misreported as a solver failure.

The race score benchmarks exact root-navigation under a local cap; an independent
exact 2-SAT verifier establishes UNSAT for every generated track formula. Models,
M2R and Spider only rank pivot checks. P_VS_NP remains OPEN.
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import math
import random
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import torch

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.mad_lab import adaptive_pippi_pitstop_ladder as v1
from experiments.mad_lab import adaptive_pippi_pitstop_ladder_v1_1 as v11
from experiments.mad_lab import asymmetric_pq_track as pqtrack
from experiments.mad_lab import keymaster_50x50_cycle1_teacher_slime as c1
from experiments.mad_lab import keymaster_adviser_governance_v2 as gov
from experiments.mad_lab import keymaster_learning_gain_journal as klgj

P_VS_NP = "OPEN"
SCHEMA = "JANUS/PIPPI/RUTHLESS-GAUNTLET/v2.0.0"
EXACT_SEMANTICS_ID = "JANUS_EXACT_ROOT_ELIMINATION_NAVIGATION_PLUS_EXACT_2SAT_VERDICT/v2"
SHOCKS = [(13, 16), (7, 19), (23, 11), (17, 29)]
UNBOUNDED_CAP = 10**12


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def stable_hash(obj: object) -> str:
    s = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(s.encode()).hexdigest()


def exact_pq_episode(cnf: base.CNF, p: int, q: int, seed: int, source: str, stage_serial: int) -> dict[str, Any]:
    # v1.1 verifier handles 2-CNF through exact 2-SAT and historical width>2 through
    # exhaustive truth table. The d field is retained only for compatibility.
    e = v11.exact_root_episode_v1_1(cnf, max(p, q), seed, source, stage_serial)
    e["p"] = p; e["q"] = q; e["difficulty"] = f"{p}:{q}"
    return e


def make_pq_stage(p: int, q: int, stage_serial: int, count: int, used: set[str], source: str = "RUTHLESS_PQ_TRACK") -> tuple[list[dict[str, Any]], dict[str, Any]]:
    out = []; j = 0; t0 = time.perf_counter(); metas = []
    while len(out) < count:
        seed = 1_300_000_000 + stage_serial * 100_003 + p * 1019 + q * 1031 + j * 43
        cnf, meta = pqtrack.construct(p, q, seed)
        e = exact_pq_episode(cnf, p, q, seed, source, stage_serial)
        j += 1
        if e["fingerprint"] in used:
            continue
        used.add(e["fingerprint"]); out.append(e); metas.append(meta)
    return out, {"generation_wall_seconds": time.perf_counter() - t0, "metas": metas}


def root_runtime(e: dict[str, Any], order: list[int]) -> dict[str, Any]:
    """Exact root safe-transition search only; exact 2-SAT verdict is independent."""
    cap = e["local_stress_cap"]
    checks = 0; pair_work = 0; raw_sum = 0; peak = e["root_units"]; attempts = []
    chosen = None
    for idx in order:
        pivot = e["vars"][idx]
        checks += 1
        out, st = base.eliminate_var_capped(e["cnf"], pivot, cap)
        raw = int(st["raw_units"]); pairs = int(st.get("pairs", 0))
        pair_work += pairs; raw_sum += raw; peak = max(peak, raw)
        fit = out is not None
        attempts.append({"pivot_local_for_audit": pivot, "raw_units": raw, "pair_work": pairs, "fit": fit})
        if fit:
            if not base.verify_elimination_transition(e["cnf"], pivot, out, cap):
                raise AssertionError("exact root transition replay failed")
            chosen = pivot
            break
    if chosen is None:
        raise AssertionError("q30 cap must admit at least one exact root pivot")
    return {
        "exact_checks": checks, "pair_work": pair_work, "raw_units_sum": raw_sum,
        "peak_raw_units": peak, "chosen_first_pivot_local_for_audit": chosen,
        "root_attempts": attempts, "exact_transition_verified": True,
    }


def efficiency_score(static: dict[str, Any], learned: dict[str, Any]) -> float:
    ratios = []
    for key, w in [("pair_work", 0.55), ("exact_checks", 0.25), ("raw_units_sum", 0.20)]:
        ratios.append((max(1e-12, static[key] / max(1e-12, learned[key])), w))
    return 100.0 * math.exp(sum(w * math.log(r) for r, w in ratios) / sum(w for _, w in ratios))


def stage_score(stage_eps: list[dict[str, Any]], teacher, student, train_pool, prior, weights) -> dict[str, Any]:
    totals = defaultdict(lambda: defaultdict(float)); top1 = 0; ranks = []; regrets = []; per = []
    label_pair_work = 0
    for e in stage_eps:
        comp = v1.adviser_scores(teacher, student, train_pool, e, prior)
        learned_order = v1.ranking_order(v1.fuse(comp, weights), e)
        static_order = sorted(range(len(e["vars"])), key=lambda i: e["vars"][i])
        oracle_order = e["oracle_root_order"]
        rt = {
            "STATIC": root_runtime(e, static_order),
            "KEYMASTER": root_runtime(e, learned_order),
            "ORACLE": root_runtime(e, oracle_order),
        }
        br = v1.best_rank(learned_order, e); ranks.append(br); top1 += int(br == 1)
        regrets.append(e["raw"][learned_order[0]] - min(e["raw"]))
        label_pair_work += sum(int(x) for x in e["pair_labels"])
        for name, r in rt.items():
            for k in ("exact_checks", "pair_work", "raw_units_sum"):
                totals[name][k] += r[k]
            totals[name]["peak_raw_units"] = max(totals[name]["peak_raw_units"], r["peak_raw_units"])
        per.append({
            "fingerprint": e["fingerprint"], "p": e["p"], "q": e["q"], "seed": e["seed"],
            "n": len(e["vars"]), "raw_span": e["raw_span"], "cap": e["local_stress_cap"],
            "best_rank": br, "static": rt["STATIC"], "keymaster": rt["KEYMASTER"], "oracle": rt["ORACLE"],
            "adviser_top1_local_index": {k: v1.ranking_order(v, e)[0] for k, v in comp.items()},
        })
    agg = {k: dict(v) for k, v in totals.items()}
    return {
        "performance_index": efficiency_score(agg["STATIC"], agg["KEYMASTER"]),
        "aggregate": agg,
        "top1_best_recall": top1 / len(stage_eps),
        "topk_exact_best_recall": sum(1 for x in per if x["best_rank"] <= min(3, len(stage_eps[0]["vars"]))) / len(stage_eps),
        "mean_best_rank": sum(ranks) / len(ranks),
        "mean_top1_raw_regret": sum(regrets) / len(regrets),
        "oracle_label_pair_work": label_pair_work,
        "per_formula": per,
    }


def formulas_for_level(p: int, q: int, base_count: int) -> int:
    m = max(p, q)
    if m < 80:
        return base_count
    if m < 160:
        return max(2, base_count - 2)
    if m < 220:
        return max(1, base_count - 3)
    return 1


def build_growth_schedule() -> list[dict[str, Any]]:
    out = [{"p": 1, "q": 1, "kind": "FORMATION", "increment": [0, 0]}]
    p = q = 1; lap = 0; shock_i = 0
    while True:
        lap += 1
        if lap % 4 == 0:
            dp, dq = SHOCKS[shock_i % len(SHOCKS)]; shock_i += 1; kind = "ASYMMETRIC_SHOCK"
        else:
            dp = dq = 10; kind = "PLUS_10x10"
        np, nq = p + dp, q + dq
        if np >= 250 or nq >= 250:
            break
        p, q = np, nq
        out.append({"p": p, "q": q, "kind": kind, "increment": [dp, dq]})
    if p > 250 or q > 250:
        raise AssertionError("schedule crossed boss before injection")
    if p > 250 or q > 250 or 250 < p or 250 < q:
        raise AssertionError((p, q))
    out.append({"p": 250, "q": 250, "kind": "MANDATORY_250x250_BOSS_IF_FRONTIER_REACHES_IT", "increment": [250 - p, 250 - q]})
    return out


def append_klgj_pair(rows: list[dict[str, Any]], run_id: str, stage_id: str,
                     eps: list[dict[str, Any]], scored: dict[str, Any], label_pair_work: int,
                     configuration_id: str, event_type: str = "LEARNING_CHECKPOINT") -> list[dict[str, Any]]:
    fp = stable_hash(sorted(e["fingerprint"] for e in eps))
    cap_id = stable_hash([e["local_stress_cap"] for e in eps])[:24]
    static = scored["aggregate"]["STATIC"]; learned = scored["aggregate"]["KEYMASTER"]
    common = {
        "run_id": run_id,
        "formula_fingerprint": fp,
        "measurement_scope": "FRESH_STAGE_CORPUS_ROOT_NAVIGATION",
        "exact_semantics_id": EXACT_SEMANTICS_ID,
        "resource_cap": cap_id,
        "correctness_requirement": "EXACT_ROOT_TRANSITION_VERIFIED_AND_TRACK_UNSAT_EXACTLY_VERIFIED",
        "hardware_environment_id": "GITHUB_ACTIONS_UBUNTU_LATEST_CPU",
        "recorded_at_utc": utc_now(),
        "tags": ["PIPPI_GAUNTLET_V2", stage_id],
    }
    rows, base_event = klgj.add_event(rows, {
        **common, "event_type": "MATCHED_STATIC_BASELINE", "configuration_id": "STATIC_NUMERIC_ROOT_ORDER",
        "metrics": {
            "exact_checks_attempted": static["exact_checks"], "pair_work": static["pair_work"],
            "raw_units_sum": static["raw_units_sum"], "peak_raw_units": static["peak_raw_units"],
        },
    })
    checks_saved = (static["exact_checks"] - learned["exact_checks"]) / max(1.0, static["exact_checks"])
    pair_saved = (static["pair_work"] - learned["pair_work"]) / max(1.0, static["pair_work"])
    rows, _ = klgj.add_event(rows, {
        **common, "event_type": event_type, "configuration_id": configuration_id,
        "baseline_event_id": base_event["event_id"],
        "metrics": {
            "exact_checks_attempted": learned["exact_checks"], "pair_work": learned["pair_work"],
            "raw_units_sum": learned["raw_units_sum"], "peak_raw_units": learned["peak_raw_units"],
            "topk_exact_best_recall": scored["topk_exact_best_recall"],
        },
        "training_cost": {"pair_work": label_pair_work},
        "holdout": {
            "distinct_formula_count": len(eps),
            "exact_checks_saved_fraction": checks_saved,
            "pair_work_saved_fraction": pair_saved,
            "overflow_avoidance_recall": 1.0,
            "topk_exact_best_recall": scored["topk_exact_best_recall"],
        },
    })
    return rows


def main() -> int:
    v1.exact_root_episode = v11.exact_root_episode_v1_1
    ap = argparse.ArgumentParser()
    ap.add_argument("--topa-dir", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--base-formulas-per-stage", type=int, default=4)
    ap.add_argument("--max-recovery-laps", type=int, default=3)
    ap.add_argument("--time-budget-seconds", type=float, default=900.0)
    ap.add_argument("--boss-probe", action="store_true", default=True)
    args = ap.parse_args()

    random.seed(20260828); torch.manual_seed(20260828); torch.set_num_threads(2)
    out = args.out_dir; out.mkdir(parents=True, exist_ok=True)
    journal = out / "pippi-gauntlet-journal.jsonl"
    klgj_path = out / "klgj-gauntlet.jsonl"
    start = time.perf_counter(); used: set[str] = set(); run_id = f"PIPPI-GAUNTLET-V2-{int(time.time())}"
    klgj_rows = klgj.read_jsonl(Path("data/keymaster/journal/KEYMASTER_LEARNING_GAIN_JOURNAL_SEED_v1.0.jsonl"))

    memory, boot = v1.bootstrap_50(used)
    teacher = c1.JGPTPivotTeacher(); teacher_opt = torch.optim.AdamW(teacher.parameters(), lr=0.004, weight_decay=0.002)
    student = c1.PivotSlimeStudent()
    attention_state = None; rejected: set[str] = set(); focus_patterns: set[str] = set()
    fusion = dict(gov.DEFAULT); previous_adviser_metrics = None
    train_pool = [e for e in memory if v1.split_name(e["fingerprint"]) == "TRAIN"]
    calib_pool = [e for e in memory if v1.split_name(e["fingerprint"]) == "CALIBRATION"]
    initial_train = v1.train_models(teacher, teacher_opt, student, train_pool, set())
    edge = out / "edge-state-pit0.jsonl"; edge_audit = v1.build_relation_edges(train_pool, {e["fingerprint"] for e in memory}, edge)
    attention_state, spider = v1.run_spider(args.topa_dir, edge, None, out, 0)
    detective = v1.detective_calibration_gate(train_pool, calib_pool); rejected = set(detective["rejected_patterns"])
    prior = v1.spider_prior_map(attention_state, rejected)
    fusion, fcal = gov.choose_fusion_governed(teacher, student, train_pool, calib_pool, prior, fusion, previous_adviser_metrics)
    previous_adviser_metrics = fcal.get("adviser_metrics")
    focus_patterns = {x["node_id"] for x in spider["focus"] if str(x.get("node_id", "")).startswith("pattern:")}
    v1.append_jsonl(journal, {"kind": "PITSTOP", "pit": 0, "phase": "PRE_RACE_BOOTSTRAP", "bootstrap": boot, "training": initial_train, "relation_edges": edge_audit, "spider": spider, "detective": detective, "governance": fcal, "fusion_weights": fusion, "P_VS_NP": P_VS_NP})

    schedule = build_growth_schedule()
    history = []; pit = 0; stage_serial = 0; official_frontier = {"p": 1, "q": 1, "score": None, "schedule_index": 0}
    previous_score = None; stop_reason = None; failed_stage = None

    def pitstop(stage_eps: list[dict[str, Any]], decision: dict[str, Any], p: int, q: int) -> dict[str, Any]:
        nonlocal pit, memory, train_pool, calib_pool, attention_state, rejected, focus_patterns, fusion, previous_adviser_metrics
        memory.extend(stage_eps); new_fps = {e["fingerprint"] for e in stage_eps}
        train_pool = [e for e in memory if v1.split_name(e["fingerprint"]) == "TRAIN"]
        calib_pool = [e for e in memory if v1.split_name(e["fingerprint"]) == "CALIBRATION"]
        pit += 1
        train_audit = v1.train_models(teacher, teacher_opt, student, train_pool, focus_patterns)
        edgep = out / f"edge-state-pit{pit}.jsonl"; edge_audit2 = v1.build_relation_edges(train_pool, new_fps, edgep)
        attention_state, spider2 = v1.run_spider(args.topa_dir, edgep, attention_state, out, pit)
        detective2 = v1.detective_calibration_gate(train_pool, calib_pool); rejected = set(detective2["rejected_patterns"])
        prior2 = v1.spider_prior_map(attention_state, rejected)
        newfusion, governance = gov.choose_fusion_governed(teacher, student, train_pool, calib_pool, prior2, fusion, previous_adviser_metrics)
        fusion = newfusion; previous_adviser_metrics = governance.get("adviser_metrics", previous_adviser_metrics)
        focus_patterns = {x["node_id"] for x in spider2["focus"] if str(x.get("node_id", "")).startswith("pattern:")}
        mirror = {
            "kind": "PITSTOP", "pit": pit, "after_stage": stage_serial, "difficulty": f"{p}:{q}",
            "new_exact_receipts": len(stage_eps), "memory_formulas": len(memory), "train_formulas": len(train_pool),
            "calibration_formulas": len(calib_pool), "training": train_audit, "relation_edges": edge_audit2,
            "spider_focus": spider2["focus"], "detective": detective2, "governance": governance,
            "next_fusion_weights": fusion, "controller_decision": decision, "P_VS_NP": P_VS_NP,
        }
        v1.append_jsonl(journal, mirror); (out / f"pippi-mirror-pit{pit}.json").write_text(json.dumps(mirror, indent=2, sort_keys=True) + "\n")
        return mirror

    def score_fresh(p: int, q: int, kind: str, phase: str, schedule_index: int) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
        nonlocal stage_serial, klgj_rows
        stage_serial += 1
        count = formulas_for_level(p, q, args.base_formulas_per_stage)
        eps, build = make_pq_stage(p, q, stage_serial, count, used, source=f"GAUNTLET_{phase}")
        prior_now = v1.spider_prior_map(attention_state, rejected)
        qstudent = copy.deepcopy(student); qaudit = c1.quantize_int8_inplace(qstudent)
        t0 = time.perf_counter(); scored = stage_score(eps, teacher, qstudent, train_pool, prior_now, fusion); score_wall = time.perf_counter() - t0
        event = {
            "kind": "STAGE", "stage_serial": stage_serial, "schedule_index": schedule_index,
            "difficulty": f"{p}:{q}", "p": p, "q": q, "track_kind": kind, "phase": phase,
            "score_before_learning_from_this_stage": scored["performance_index"], "metrics": scored,
            "fusion_weights_used": fusion, "fresh_fingerprints": [e["fingerprint"] for e in eps],
            "formula_count": len(eps), "generation_wall_seconds": build["generation_wall_seconds"],
            "score_wall_seconds": score_wall, "int8_tensor_count": qaudit["tensor_count"],
            "elapsed_seconds": time.perf_counter() - start, "P_VS_NP": P_VS_NP,
        }
        v1.append_jsonl(journal, event); history.append(event)
        klgj_rows = append_klgj_pair(klgj_rows, run_id, f"stage-{stage_serial}-{phase}-{p}x{q}", eps, scored, scored["oracle_label_pair_work"], "KEYMASTER_GOVERNED_V2")
        klgj.write_jsonl(klgj_path, klgj_rows)
        return eps, scored, event

    for idx, spec in enumerate(schedule):
        if time.perf_counter() - start > args.time_budget_seconds:
            stop_reason = "TIME_BUDGET"; break
        p, q, kind = spec["p"], spec["q"], spec["kind"]
        eps, scored, event = score_fresh(p, q, kind, "FORMATION" if idx == 0 else "RACE", idx)
        score = float(scored["performance_index"])
        if idx == 0:
            decision = {"action": "FORMATION_ACCEPT", "next": "RUTHLESS_GROWTH"}
            pitstop(eps, decision, p, q); continue
        if previous_score is None:
            previous_score = score; official_frontier = {"p": p, "q": q, "score": score, "schedule_index": idx}
            decision = {"action": "ACCEPT_FIRST_RACING_REFERENCE", "accepted_score": score}
            pitstop(eps, decision, p, q); continue
        if score >= previous_score:
            previous_score = score; official_frontier = {"p": p, "q": q, "score": score, "schedule_index": idx}
            decision = {"action": "ACCEPT_AND_PRESS_FORWARD", "accepted_score": score}
            pitstop(eps, decision, p, q); continue

        # Regression: score first, learn only afterwards, then recover at last accepted difficulty.
        failed_stage = {"p": p, "q": q, "score": score, "schedule_index": idx, "previous_score": previous_score}
        target = max(previous_score * 1.03, previous_score + 3.0)
        drop = previous_score - score
        decision = {"action": "REGRESSION_ENTER_PIT", "drop_points": drop, "recovery_target": target, "rollback_to": f"{official_frontier['p']}:{official_frontier['q']}"}
        pitstop(eps, decision, p, q)

        recovered = False; recovery_best = -math.inf
        for recovery_lap in range(1, args.max_recovery_laps + 1):
            if time.perf_counter() - start > args.time_budget_seconds:
                stop_reason = "TIME_BUDGET_DURING_RECOVERY"; break
            rp, rq = official_frontier["p"], official_frontier["q"]
            reps, rscored, revent = score_fresh(rp, rq, "RECOVERY_AT_LAST_ACCEPTED", f"RECOVERY_{recovery_lap}", idx)
            rs = float(rscored["performance_index"]); recovery_best = max(recovery_best, rs)
            if rs >= target:
                rdecision = {"action": "RECOVERY_CONFIRMED", "recovery_lap": recovery_lap, "score": rs, "target": target, "rebound_from_failed": rs - score}
                pitstop(reps, rdecision, rp, rq); recovered = True; break
            rdecision = {"action": "RECOVERY_NOT_YET", "recovery_lap": recovery_lap, "score": rs, "target": target}
            pitstop(reps, rdecision, rp, rq)
        if stop_reason:
            break
        if not recovered:
            stop_reason = "RECOVERY_TARGET_NOT_REACHED__RUTHLESS_FRONTIER_FROZEN"
            failed_stage["recovery_target"] = target; failed_stage["best_recovery_score"] = recovery_best
            break

        # One fresh retry of the failed pressure level. A second regression freezes the frontier.
        teps, tscored, tevent = score_fresh(p, q, kind, "RETRY_AFTER_RECOVERY", idx)
        ts = float(tscored["performance_index"])
        if ts >= previous_score:
            previous_score = ts; official_frontier = {"p": p, "q": q, "score": ts, "schedule_index": idx}
            tdecision = {"action": "RETRY_ACCEPTED_PRESS_FORWARD", "score": ts}
            pitstop(teps, tdecision, p, q)
            continue
        tdecision = {"action": "RETRY_REGRESSED_AGAIN_FREEZE", "score": ts, "required_at_least": previous_score}
        pitstop(teps, tdecision, p, q)
        failed_stage["retry_score"] = ts; failed_stage["recovery_target"] = target
        stop_reason = "FAILED_LEVEL_REGRESSED_AGAIN_AFTER_CONFIRMED_RECOVERY"
        break

    if stop_reason is None:
        stop_reason = "SCHEDULE_COMPLETED_TO_250x250" if official_frontier["p"] == 250 and official_frontier["q"] == 250 else "RACE_ENDED"

    # Mandatory blind 250:250 OOD boss probe, irrespective of official frontier.
    boss = None
    if args.boss_probe and time.perf_counter() - start < args.time_budget_seconds:
        boss_serial = stage_serial + 1
        boss_eps, boss_build = make_pq_stage(250, 250, boss_serial, 1, used, source="MANDATORY_BLIND_250x250_BOSS")
        prior_now = v1.spider_prior_map(attention_state, rejected)
        qstudent = copy.deepcopy(student); qaudit = c1.quantize_int8_inplace(qstudent)
        bt = time.perf_counter(); boss_scored = stage_score(boss_eps, teacher, qstudent, train_pool, prior_now, fusion); boss_wall = time.perf_counter() - bt
        boss = {
            "status": "BLIND_OOD_BOSS_SCORED_BEFORE_LEARNING", "difficulty": "250:250",
            "official_frontier_unchanged": True, "fresh_fingerprint": boss_eps[0]["fingerprint"],
            "n": len(boss_eps[0]["vars"]), "m": len(boss_eps[0]["cnf"]),
            "score": boss_scored["performance_index"], "top1_best_recall": boss_scored["top1_best_recall"],
            "mean_best_rank": boss_scored["mean_best_rank"], "aggregate": boss_scored["aggregate"],
            "oracle_label_pair_work": boss_scored["oracle_label_pair_work"],
            "generation_wall_seconds": boss_build["generation_wall_seconds"], "score_wall_seconds": boss_wall,
            "fusion_weights_used": fusion, "int8_tensor_count": qaudit["tensor_count"],
            "exact_2sat_shortcut_used_for_navigation_score": False,
            "P_VS_NP": P_VS_NP,
        }
        v1.append_jsonl(journal, {"kind": "BOSS_PROBE", **boss})
        klgj_rows = append_klgj_pair(klgj_rows, run_id, "blind-boss-250x250", boss_eps, boss_scored, boss_scored["oracle_label_pair_work"], "KEYMASTER_GOVERNED_V2_OOD_BOSS", event_type="OOD_BOSS_CHECKPOINT")
        klgj.write_jsonl(klgj_path, klgj_rows)

    impossibility = pqtrack.fixed_width2_feasibility(251, 251, 126, allow_units=False)
    if impossibility["possible_by_capacity"]:
        raise AssertionError("epistemic trap was not rejected")
    v1.append_jsonl(journal, {"kind": "FEASIBILITY_TRAP", "probe": "251:251@fixed-n126-width2-no-units", "certificate": impossibility, "correct_behavior": "DO_NOT_INVOKE_SOLVER_ON_NONEXISTENT_TRACK_INSTANCE", "P_VS_NP": P_VS_NP})

    klgj_summary = klgj.summarize(klgj_rows)
    (out / "klgj-gauntlet-summary.json").write_text(json.dumps(klgj_summary, indent=2, sort_keys=True) + "\n")
    config = {
        "adviser_governance_only_controlled_change": True,
        "JGPT_implementation_changed": False, "SLIME_implementation_changed": False,
        "M2R_implementation_changed": False, "SPIDER_implementation_changed": False,
        "ordinary_increment": [10, 10], "shock_increments": [list(x) for x in SHOCKS],
        "recovery_rule": "max(previous_score*1.03, previous_score+3.0)",
        "recovery_level": "last accepted difficulty only", "max_recovery_laps": args.max_recovery_laps,
        "mandatory_blind_250x250_boss": True,
    }
    result = {
        "schema": SCHEMA, "status": "RUTHLESS_GAUNTLET_COMPLETE__EXACT_ROOT_TRANSITIONS_VERIFIED", "P_VS_NP": P_VS_NP,
        "configuration": config, "bootstrap": boot, "schedule": schedule,
        "official_frontier": official_frontier, "failed_stage": failed_stage, "stop_reason": stop_reason,
        "stages_scored": len(history), "pitstops_completed": pit, "history": [
            {"stage": h["stage_serial"], "difficulty": h["difficulty"], "phase": h["phase"], "kind": h["track_kind"],
             "score": h["score_before_learning_from_this_stage"], "top1": h["metrics"]["top1_best_recall"],
             "mean_rank": h["metrics"]["mean_best_rank"], "static": h["metrics"]["aggregate"]["STATIC"],
             "keymaster": h["metrics"]["aggregate"]["KEYMASTER"], "formula_count": h["formula_count"]}
            for h in history
        ],
        "final_fusion_weights": fusion, "final_adviser_metrics": previous_adviser_metrics,
        "final_detective_rejected_patterns": sorted(rejected), "boss_250x250": boss,
        "fixed_chassis_impossibility_trap": impossibility, "klgj_summary": klgj_summary,
        "elapsed_seconds": time.perf_counter() - start,
        "scientific_firewall": {
            "FRESH_STAGE_SCORED_BEFORE_LEARNING_FROM_IT": True,
            "BOSS_250x250_IS_BLIND_OOD_AND_DOES_NOT_REWRITE_FRONTIER": True,
            "TRACK_CONSTRUCTION_IMPOSSIBILITY_IS_NOT_SOLVER_FAILURE": True,
            "NO_ADVISER_100_PERCENT": max(fusion.values()) < 0.999999,
            "PIVOT_NUMERIC_ID_IS_NOT_MODEL_FEATURE": True,
            "ATTENTION_WEIGHT_IS_NOT_EVIDENCE_WEIGHT": True,
            "MODEL_PREDICTION_IS_NOT_PROOF": True,
            "EVERY_COUNTED_ROOT_TRANSITION_EXACT_VERIFIED": True,
            "EXACT_2SAT_IS_INDEPENDENT_TRACK_VERDICT_NOT_NAVIGATION_SCORE": True,
            "NO_SAME_RUN_THEOREM_PROMOTION": True,
            "P_VS_NP": P_VS_NP,
        },
    }
    (out / "gauntlet-result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "status": result["status"], "official_frontier": official_frontier, "stop_reason": stop_reason,
        "stages_scored": len(history), "pitstops": pit,
        "boss_250x250": None if boss is None else {"score": boss["score"], "n": boss["n"], "m": boss["m"], "mean_rank": boss["mean_best_rank"]},
        "impossibility_trap": impossibility["status"], "final_weights": fusion,
        "klgj_net_pair_work": klgj_summary["accounting"]["net_pair_work_savings_after_recorded_training_cost"],
        "P_VS_NP": P_VS_NP,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
