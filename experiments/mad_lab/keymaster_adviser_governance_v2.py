#!/usr/bin/env python3
"""Keymaster adviser governance v2.

Controlled modification after the frozen PIPPI v1.2 race diagnosed
ADVISER_MONOCULTURE__SMALL_N_CALIBRATION. JGPT, Slime, M2R and Spider are not
changed here; only their voting/arbitration policy is changed.

Laws:
- no adviser receives 100% authority;
- tiny calibration cannot cause a sudden monopoly;
- authority rises gradually with independent calibration fingerprints;
- an adviser whose holdout top-1 deteriorates is de-rated;
- exact replay remains authority; adviser weights only reorder checks.

P_VS_NP=OPEN.
"""
from __future__ import annotations

import json
from typing import Any

from experiments.mad_lab import adaptive_pippi_pitstop_ladder as v1

P_VS_NP = "OPEN"
SCHEMA = "JANUS/KEYMASTER/ADVISER-GOVERNANCE/v2.0.0"
NAMES = ("JGPT", "SLIME", "M2R", "SPIDER")
DEFAULT = {"JGPT": 0.50, "SLIME": 0.25, "M2R": 0.25, "SPIDER": 0.00}


def grid_weights(step: int = 10) -> list[dict[str, float]]:
    out = []
    for a in range(step + 1):
        for b in range(step + 1 - a):
            for c in range(step + 1 - a - b):
                d = step - a - b - c
                out.append(dict(zip(NAMES, (a / step, b / step, c / step, d / step))))
    return out


def adviser_calibration_metrics(teacher, student, train, diverse, prior) -> dict[str, dict[str, float]]:
    rows = {k: {"hits": 0.0, "rank_sum": 0.0, "regret_sum": 0.0} for k in NAMES}
    for e in diverse:
        comp = v1.adviser_scores(teacher, student, train, e, prior)
        for k in NAMES:
            order = v1.ranking_order(comp[k], e)
            r = v1.best_rank(order, e)
            rows[k]["hits"] += float(r == 1)
            rows[k]["rank_sum"] += r
            rows[k]["regret_sum"] += e["raw"][order[0]] - min(e["raw"])
    n = max(1, len(diverse))
    out = {}
    for k in NAMES:
        hits = rows[k]["hits"]
        out[k] = {
            "top1": hits / n,
            "laplace_top1": (hits + 1.0) / (n + 2.0),
            "mean_rank": rows[k]["rank_sum"] / n,
            "mean_raw_regret": rows[k]["regret_sum"] / n,
            "independent_formulas": len(diverse),
        }
    return out


def global_cap(n: int) -> float:
    if n < 8:
        return 0.55
    if n < 16:
        return 0.65
    if n < 32:
        return 0.75
    return 0.85


def adviser_caps(n: int, metrics: dict[str, dict[str, float]], previous_metrics: dict[str, dict[str, float]] | None) -> tuple[dict[str, float], dict[str, Any]]:
    gcap = global_cap(n)
    caps = {}
    audit = {}
    previous_metrics = previous_metrics or {}
    for k in NAMES:
        m = metrics[k]
        cap = gcap
        reasons = []
        if n < 8:
            # Tiny-N can tune around the frozen prior but cannot seize control.
            cap = min(cap, DEFAULT[k] + 0.15)
            reasons.append("TINY_N_PRIOR_PLUS_0_15")
        if m["top1"] < 0.25:
            cap = min(cap, 0.35)
            reasons.append("LOW_TOP1_SUPPORT")
        old = previous_metrics.get(k)
        deterioration = None
        if old is not None:
            deterioration = float(old.get("top1", 0.0)) - m["top1"]
            if deterioration > 0.10:
                cap = min(cap, max(0.20, gcap * 0.65))
                reasons.append("PIPPI_HOLDOUT_DETERIORATION_DERATE")
        caps[k] = max(0.0, cap)
        audit[k] = {"cap": caps[k], "reasons": reasons, "top1": m["top1"], "previous_top1": None if old is None else old.get("top1"), "deterioration": deterioration}
    return caps, {"global_cap": gcap, "per_adviser": audit}


def feasible(w: dict[str, float], caps: dict[str, float]) -> bool:
    return all(w[k] <= caps[k] + 1e-12 for k in NAMES)


def renormalize_with_caps(w: dict[str, float], caps: dict[str, float]) -> dict[str, float]:
    """Project a nonnegative vector to sum=1 without exceeding adviser caps."""
    x = {k: max(0.0, float(w[k])) for k in NAMES}
    for _ in range(16):
        over = {k: max(0.0, x[k] - caps[k]) for k in NAMES}
        if max(over.values(), default=0.0) < 1e-12:
            break
        excess = sum(over.values())
        for k in NAMES:
            x[k] = min(x[k], caps[k])
        room = {k: max(0.0, caps[k] - x[k]) for k in NAMES}
        total_room = sum(room.values())
        if total_room <= 1e-12:
            break
        for k in NAMES:
            x[k] += excess * room[k] / total_room
    s = sum(x.values())
    if s <= 0:
        raise AssertionError("zero governance vector")
    x = {k: x[k] / s for k in NAMES}
    if not feasible(x, caps):
        # Final deterministic water-fill from zero, prioritizing requested weight.
        target = sorted(NAMES, key=lambda k: (-w[k], k))
        x = {k: 0.0 for k in NAMES}; remaining = 1.0
        for k in target:
            take = min(caps[k], remaining)
            x[k] = take; remaining -= take
        if remaining > 1e-9:
            raise AssertionError(("caps cannot sum to 1", caps))
    return x


def choose_fusion_governed(teacher, student, train, calib, prior,
                           previous_weights: dict[str, float] | None = None,
                           previous_metrics: dict[str, dict[str, float]] | None = None) -> tuple[dict[str, float], dict[str, Any]]:
    diverse = [e for e in calib if e["raw_span"] > 0]
    n = len(diverse)
    prev = previous_weights or DEFAULT
    if n == 0:
        return dict(DEFAULT), {"schema": SCHEMA, "status": "DEFAULT_NO_DIVERSE_CALIBRATION", "diverse_calibration": 0, "P_VS_NP": P_VS_NP}

    metrics = adviser_calibration_metrics(teacher, student, train, diverse, prior)
    caps, cap_audit = adviser_caps(n, metrics, previous_metrics)
    comps = [v1.adviser_scores(teacher, student, train, e, prior) for e in diverse]

    def obj(w: dict[str, float]):
        ranks = []; regrets = []; hits = 0
        for e, c in zip(diverse, comps):
            o = v1.ranking_order(v1.fuse(c, w), e)
            r = v1.best_rank(o, e)
            ranks.append(r); hits += int(r == 1)
            regrets.append(e["raw"][o[0]] - min(e["raw"]))
        return (sum(ranks) / len(ranks), -hits / len(ranks), sum(regrets) / len(regrets), tuple(w[k] for k in NAMES))

    candidates = [w for w in grid_weights(10) if feasible(w, caps)]
    if not candidates:
        raw_best = dict(DEFAULT)
        status = "DEFAULT_NO_FEASIBLE_GRID"
        q = obj(raw_best)
    else:
        raw_best = min(candidates, key=obj)
        q = obj(raw_best)
        status = "GOVERNED_CALIBRATION_GRID"

    # Authority changes gradually; tiny-N gets especially strong inertia.
    alpha = 0.25 if n < 8 else (0.45 if n < 16 else 0.65)
    blended = {k: (1.0 - alpha) * prev[k] + alpha * raw_best[k] for k in NAMES}
    governed = renormalize_with_caps(blended, caps)

    max_name = max(NAMES, key=lambda k: governed[k])
    audit = {
        "schema": SCHEMA,
        "status": status,
        "diverse_calibration": n,
        "adviser_metrics": metrics,
        "caps": caps,
        "cap_audit": cap_audit,
        "raw_grid_winner": raw_best,
        "previous_weights": prev,
        "inertia_alpha": alpha,
        "governed_weights": governed,
        "mean_best_rank": q[0],
        "top1_recall": -q[1],
        "mean_raw_regret": q[2],
        "candidate_count": len(candidates),
        "largest_adviser": max_name,
        "largest_weight": governed[max_name],
        "monoculture_prevented": governed[max_name] < 0.999999,
        "NO_ADVISER_100_PERCENT": True,
        "MODEL_PREDICTION_IS_NOT_PROOF": True,
        "P_VS_NP": P_VS_NP,
    }
    if governed[max_name] > 0.8500001:
        raise AssertionError(("governance cap violated", governed, caps))
    return governed, audit


def self_test() -> dict[str, Any]:
    caps = {k: 0.55 for k in NAMES}
    x = renormalize_with_caps({"JGPT": 0, "SLIME": 0, "M2R": 0, "SPIDER": 1}, caps)
    if max(x.values()) > 0.5500001 or abs(sum(x.values()) - 1.0) > 1e-9:
        raise AssertionError(x)
    return {"schema": SCHEMA + "/self-test", "status": "PASS", "projected_monopoly": x, "P_VS_NP": P_VS_NP}


if __name__ == "__main__":
    print(json.dumps(self_test(), indent=2, sort_keys=True))
