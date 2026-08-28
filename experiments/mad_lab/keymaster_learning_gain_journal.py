#!/usr/bin/env python3
"""KEYMASTER Learning Gain Journal (KLGJ).

Append-only accounting for learning/search gains around the full JANUS loop.
The journal measures resource use and learning benefit; it has zero proof-state
authority.  P_VS_NP remains OPEN.

Important distinctions:
* physical CPU/RAM is never said to increase because a model learned;
* "effective capacity" means less measured work per equally-correct solved case;
* module boost claims require matched ablations/comparable baselines;
* training/calibration cost is counted against downstream savings;
* missing historical metrics stay missing instead of being estimated.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from pathlib import Path
from typing import Any, Iterable

SCHEMA = "JANUS/KEYMASTER/LEARNING-GAIN-JOURNAL/v1.0.0"
P_VS_NP = "OPEN"
PROTECTED_LOWER_IS_BETTER = [
    "exact_checks_attempted",
    "pair_work",
    "raw_units_sum",
    "peak_raw_units",
    "terminal_depth",
]
PROTECTED_HIGHER_IS_BETTER = [
    "overflow_avoidance_recall",
    "topk_exact_best_recall",
]


def sha(obj: object) -> str:
    s = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def read_jsonl(path: Path | None) -> list[dict[str, Any]]:
    if path is None or not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n" for r in rows), encoding="utf-8")


def comparable(a: dict[str, Any], b: dict[str, Any], *, wall_clock: bool = False) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    for key in ("formula_fingerprint", "measurement_scope", "exact_semantics_id", "resource_cap"):
        if a.get(key) != b.get(key):
            reasons.append(f"{key}_mismatch")
    if a.get("correctness_requirement") != b.get("correctness_requirement"):
        reasons.append("correctness_requirement_mismatch")
    if wall_clock and a.get("hardware_environment_id") != b.get("hardware_environment_id"):
        reasons.append("hardware_environment_mismatch")
    return (not reasons), reasons


def maybe_delta(base: dict[str, Any], cur: dict[str, Any], name: str) -> dict[str, float] | None:
    b = base.get("metrics", {}).get(name)
    c = cur.get("metrics", {}).get(name)
    if b is None or c is None:
        return None
    b = float(b); c = float(c)
    saved = b - c
    return {
        "baseline": b,
        "current": c,
        "saved": saved,
        "saved_fraction": saved / max(1.0, abs(b)),
        "capacity_multiplier": b / c if c > 0 else math.inf,
    }


def derive_against_baseline(base: dict[str, Any], cur: dict[str, Any]) -> dict[str, Any]:
    ok, reasons = comparable(base, cur)
    out: dict[str, Any] = {
        "baseline_event_id": base["event_id"],
        "comparable_for_search_gain": ok,
        "comparability_failures": reasons,
        "physical_resource_created": False,
    }
    if not ok:
        return out
    for name in PROTECTED_LOWER_IS_BETTER:
        d = maybe_delta(base, cur, name)
        if d is not None:
            out[name] = d
    wb = base.get("metrics", {}).get("wall_time_seconds")
    wc = cur.get("metrics", {}).get("wall_time_seconds")
    wall_ok, wall_reasons = comparable(base, cur, wall_clock=True)
    out["wall_clock_comparable"] = wall_ok
    out["wall_clock_comparability_failures"] = wall_reasons
    if wall_ok and wb is not None and wc is not None and float(wc) > 0:
        out["wall_clock_speedup_diagnostic"] = float(wb) / float(wc)
    return out


def add_event(existing: list[dict[str, Any]], event: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    required = [
        "run_id", "formula_fingerprint", "configuration_id", "measurement_scope",
        "exact_semantics_id", "resource_cap", "correctness_requirement", "metrics",
    ]
    missing = [k for k in required if k not in event]
    if missing:
        raise ValueError("missing required fields: " + ",".join(missing))
    event = dict(event)
    event["schema"] = SCHEMA
    event["P_VS_NP"] = P_VS_NP
    event["sequence_no"] = len(existing) + 1
    event.setdefault("recorded_at_utc", "UNSPECIFIED_BY_CALLER")
    event.setdefault("hardware_environment_id", None)
    event.setdefault("training_cost", {})
    event.setdefault("tags", [])
    event.setdefault("notes", [])
    event.setdefault("baseline_event_id", None)
    event.setdefault("parent_configuration_event_id", None)
    event["event_id"] = sha({
        "sequence_no": event["sequence_no"],
        "run_id": event["run_id"],
        "formula_fingerprint": event["formula_fingerprint"],
        "configuration_id": event["configuration_id"],
        "measurement_scope": event["measurement_scope"],
        "metrics": event["metrics"],
        "recorded_at_utc": event["recorded_at_utc"],
    })[:32]
    if any(x.get("event_id") == event["event_id"] for x in existing):
        raise ValueError("duplicate event_id")

    if event["baseline_event_id"]:
        base = next((x for x in existing if x.get("event_id") == event["baseline_event_id"]), None)
        if base is None:
            raise ValueError("baseline_event_id not found")
        event["derived_vs_baseline"] = derive_against_baseline(base, event)
    else:
        event["derived_vs_baseline"] = {"status": "NO_BASELINE_LINKED"}

    if event["parent_configuration_event_id"]:
        parent = next((x for x in existing if x.get("event_id") == event["parent_configuration_event_id"]), None)
        if parent is None:
            raise ValueError("parent_configuration_event_id not found")
        ok, reasons = comparable(parent, event)
        event["matched_ablation"] = {
            "comparable": ok,
            "comparability_failures": reasons,
            "parent_configuration_id": parent.get("configuration_id"),
            "child_configuration_id": event.get("configuration_id"),
            "changed_axis": event.get("changed_axis"),
        }
        if ok:
            event["matched_ablation"]["deltas"] = {
                name: maybe_delta(parent, event, name)
                for name in PROTECTED_LOWER_IS_BETTER
                if maybe_delta(parent, event, name) is not None
            }
    else:
        event["matched_ablation"] = {"status": "NO_PARENT_ABLATION_LINKED"}

    event["event_sha256"] = sha({k: v for k, v in event.items() if k != "event_sha256"})
    return existing + [event], event


def marginal_series(rows: list[dict[str, Any]], metric: str) -> list[float]:
    vals = []
    for r in rows:
        v = r.get("holdout", {}).get(metric)
        if v is not None:
            vals.append(float(v))
    return [vals[i] - vals[i-1] for i in range(1, len(vals))]


def plateau_status(rows: list[dict[str, Any]], window: int = 5, epsilon: float = 0.005, min_formulas: int = 5) -> dict[str, Any]:
    checkpoints = [r for r in rows if r.get("event_type") == "LEARNING_CHECKPOINT" and r.get("holdout")]
    if len(checkpoints) < window + 1:
        return {"status": "INSUFFICIENT_HISTORY", "checkpoint_count": len(checkpoints)}
    latest = checkpoints[-1]
    if int(latest.get("holdout", {}).get("distinct_formula_count", 0)) < min_formulas:
        return {"status": "INSUFFICIENT_HISTORY", "reason": "too_few_distinct_holdout_formulas"}
    a = marginal_series(checkpoints[-(window+1):], "exact_checks_saved_fraction")
    b = marginal_series(checkpoints[-(window+1):], "pair_work_saved_fraction")
    if len(a) < window or len(b) < window:
        return {"status": "INSUFFICIENT_HISTORY", "reason": "protected_metrics_missing"}
    ma = statistics.median(a); mb = statistics.median(b)
    overflow_delta = marginal_series(checkpoints[-(window+1):], "overflow_avoidance_recall")
    topk_delta = marginal_series(checkpoints[-(window+1):], "topk_exact_best_recall")
    aux = max([abs(x) for x in overflow_delta[-window:] + topk_delta[-window:]] or [0.0])
    if ma < -epsilon or mb < -epsilon:
        status = "REGRESSION"
    elif 0 <= ma < epsilon and 0 <= mb < epsilon:
        status = "SLOWING_CANDIDATE"
    elif abs(ma) < epsilon and abs(mb) < epsilon and aux < epsilon:
        status = "PLATEAU_CANDIDATE"
    else:
        status = "LEARNING_ACTIVE"
    return {
        "status": status,
        "window": window,
        "relative_gain_epsilon": epsilon,
        "median_marginal_exact_checks_saved_fraction": ma,
        "median_marginal_pair_work_saved_fraction": mb,
        "max_recent_aux_metric_change": aux,
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    spent_training_pair_work = sum(float(r.get("training_cost", {}).get("pair_work", 0) or 0) for r in rows)
    saved_pair_work = 0.0
    saved_checks = 0.0
    for r in rows:
        d = r.get("derived_vs_baseline", {})
        if d.get("comparable_for_search_gain"):
            if isinstance(d.get("pair_work"), dict):
                saved_pair_work += float(d["pair_work"]["saved"])
            if isinstance(d.get("exact_checks_attempted"), dict):
                saved_checks += float(d["exact_checks_attempted"]["saved"])
    net_pair_work = saved_pair_work - spent_training_pair_work
    return {
        "schema": "JANUS/KEYMASTER/LEARNING-GAIN-JOURNAL-SUMMARY/v1.0.0",
        "P_VS_NP": P_VS_NP,
        "event_count": len(rows),
        "distinct_formula_fingerprints": len({r.get("formula_fingerprint") for r in rows if r.get("formula_fingerprint")}),
        "distinct_configurations": len({r.get("configuration_id") for r in rows if r.get("configuration_id")}),
        "accounting": {
            "cumulative_exact_checks_saved_where_comparable": saved_checks,
            "cumulative_pair_work_saved_where_comparable": saved_pair_work,
            "cumulative_additional_training_pair_work_recorded": spent_training_pair_work,
            "net_pair_work_savings_after_recorded_training_cost": net_pair_work,
            "resource_positive_on_recorded_pair_work_horizon": net_pair_work > 0,
            "physical_resource_created": False,
        },
        "plateau_watch": plateau_status(rows),
        "laws": [
            "NO_BOOST_CLAIM_WITHOUT_COMPARABLE_BASELINE",
            "TRAINING_COST_IS_COUNTED",
            "EFFECTIVE_CAPACITY_IS_NOT_PHYSICAL_RESOURCE_CREATION",
            "REGRESSIONS_ARE_PRESERVED",
            "P_VS_NP_IS_OPEN",
        ],
    }


def historical_seed() -> list[dict[str, Any]]:
    # Only frozen metrics already established in exact receipts are included.
    # Missing total-exhaustive costs are deliberately absent, so no speedup is claimed.
    seeds = [
        {
            "event_type": "HISTORICAL_BACKFILL",
            "recorded_at_utc": "2026-08-28T00:00:00Z",
            "run_id": "33137658244",
            "formula_fingerprint": "6c2218ff36a9135092c8361d0d007a302052e2497a973e83c699c3f433996e6b",
            "configuration_id": "JUXTAPOSE_EXACT_25x25_CHAMPION",
            "measurement_scope": "FULL_ROUTE",
            "exact_semantics_id": "JANUS_C025_CANONICAL_ELIMINATION",
            "resource_cap": 3364,
            "correctness_requirement": "EXACT_TERMINAL_UNSAT",
            "metrics": {
                "orders_or_candidates_considered": 5040,
                "peak_raw_units": 718,
                "raw_units_sum": 1096,
                "pair_work": 803,
                "terminal_depth": 5,
            },
            "notes": ["Backfilled from frozen exact JUXTAPOSE receipt; exhaustive aggregate cost unknown, so no learning speedup claim."],
        },
        {
            "event_type": "HISTORICAL_BACKFILL",
            "recorded_at_utc": "2026-08-28T00:00:01Z",
            "run_id": "33138378591",
            "formula_fingerprint": "7f4d9340f5ae52be74488d0df37b3b3b76366236a9c906eb2b31b474f44640df",
            "configuration_id": "JUXTAPOSE_EXACT_250x250_CAP105_CHAMPION",
            "measurement_scope": "FULL_ROUTE",
            "exact_semantics_id": "JANUS_C025_CANONICAL_ELIMINATION",
            "resource_cap": 11025,
            "correctness_requirement": "EXACT_TERMINAL_UNSAT",
            "metrics": {
                "orders_or_candidates_considered": 40320,
                "peak_raw_units": 10787,
                "terminal_depth": 4,
            },
            "notes": ["Backfilled from frozen exact JUXTAPOSE receipt; missing aggregate pair-work/wall-time remain unknown."],
        },
        {
            "event_type": "CALIBRATION_BASELINE",
            "recorded_at_utc": "2026-08-28T00:00:02Z",
            "run_id": "33140328159",
            "formula_fingerprint": "MULTI_FORMULA_CALIBRATION_BASELINE",
            "configuration_id": "KEYMASTER_M2R_JGPT_SLIME_TOPA_DETECTIVE_PRE_GAIN_MEASUREMENT",
            "measurement_scope": "HOLDOUT_CORPUS",
            "exact_semantics_id": "JANUS_C025_CANONICAL_ELIMINATION",
            "resource_cap": "MIXED_BY_FORMULA",
            "correctness_requirement": "EXACT_REPLAY_EQUALITY",
            "metrics": {
                "exact_verified_training_episode_count": 15,
                "distinct_formula_fingerprint_count": 2,
            },
            "notes": ["Learning infrastructure exists, but no matched holdout speedup has yet been demonstrated. This is the zero point for future gain accounting."],
        },
    ]
    rows: list[dict[str, Any]] = []
    for s in seeds:
        rows, _ = add_event(rows, s)
    return rows


def self_test() -> None:
    rows: list[dict[str, Any]] = []
    base = {
        "event_type": "TEST",
        "run_id": "base", "formula_fingerprint": "F", "configuration_id": "A",
        "measurement_scope": "FULL_ROUTE", "exact_semantics_id": "E", "resource_cap": 100,
        "correctness_requirement": "EXACT", "hardware_environment_id": "H",
        "metrics": {"exact_checks_attempted": 100, "pair_work": 1000, "peak_raw_units": 80, "terminal_depth": 8, "wall_time_seconds": 10},
    }
    rows, b = add_event(rows, base)
    cur = {
        "event_type": "TEST",
        "run_id": "cur", "formula_fingerprint": "F", "configuration_id": "B",
        "measurement_scope": "FULL_ROUTE", "exact_semantics_id": "E", "resource_cap": 100,
        "correctness_requirement": "EXACT", "hardware_environment_id": "H",
        "baseline_event_id": b["event_id"], "parent_configuration_event_id": b["event_id"], "changed_axis": "M2R_PM",
        "metrics": {"exact_checks_attempted": 25, "pair_work": 250, "peak_raw_units": 70, "terminal_depth": 6, "wall_time_seconds": 4},
        "training_cost": {"pair_work": 100},
    }
    rows, c = add_event(rows, cur)
    assert c["derived_vs_baseline"]["exact_checks_attempted"]["capacity_multiplier"] == 4.0
    assert c["derived_vs_baseline"]["pair_work"]["saved"] == 750.0
    assert c["derived_vs_baseline"]["physical_resource_created"] is False
    s = summarize(rows)
    assert s["accounting"]["cumulative_pair_work_saved_where_comparable"] == 750.0
    assert s["accounting"]["net_pair_work_savings_after_recorded_training_cost"] == 650.0
    assert s["P_VS_NP"] == "OPEN"
    seeded = historical_seed()
    assert len(seeded) == 3
    assert summarize(seeded)["accounting"]["cumulative_pair_work_saved_where_comparable"] == 0.0


def main(argv: Iterable[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("self-test")
    pseed = sub.add_parser("seed")
    pseed.add_argument("--journal-out", type=Path, required=True)
    pseed.add_argument("--summary-out", type=Path, required=True)
    pappend = sub.add_parser("append")
    pappend.add_argument("--journal-in", type=Path, required=True)
    pappend.add_argument("--event", type=Path, required=True)
    pappend.add_argument("--journal-out", type=Path, required=True)
    pappend.add_argument("--summary-out", type=Path, required=True)
    psum = sub.add_parser("summarize")
    psum.add_argument("--journal-in", type=Path, required=True)
    psum.add_argument("--summary-out", type=Path, required=True)
    args = ap.parse_args(list(argv) if argv is not None else None)

    if args.cmd == "self-test":
        self_test()
        print(json.dumps({"status": "PASS", "schema": SCHEMA, "P_VS_NP": P_VS_NP}))
        return 0
    if args.cmd == "seed":
        rows = historical_seed()
        write_jsonl(args.journal_out, rows)
        args.summary_out.parent.mkdir(parents=True, exist_ok=True)
        args.summary_out.write_text(json.dumps(summarize(rows), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({"status": "PASS", "events": len(rows), "P_VS_NP": P_VS_NP}))
        return 0
    if args.cmd == "append":
        rows = read_jsonl(args.journal_in)
        event = json.loads(args.event.read_text(encoding="utf-8"))
        rows, added = add_event(rows, event)
        write_jsonl(args.journal_out, rows)
        args.summary_out.parent.mkdir(parents=True, exist_ok=True)
        args.summary_out.write_text(json.dumps(summarize(rows), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({"status": "PASS", "event_id": added["event_id"], "events": len(rows), "P_VS_NP": P_VS_NP}))
        return 0
    if args.cmd == "summarize":
        rows = read_jsonl(args.journal_in)
        args.summary_out.parent.mkdir(parents=True, exist_ok=True)
        args.summary_out.write_text(json.dumps(summarize(rows), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({"status": "PASS", "events": len(rows), "P_VS_NP": P_VS_NP}))
        return 0
    raise AssertionError(args.cmd)


if __name__ == "__main__":
    raise SystemExit(main())
