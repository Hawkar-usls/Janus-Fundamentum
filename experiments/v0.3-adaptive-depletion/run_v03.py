from __future__ import annotations

import csv
import json
import random
import time
from pathlib import Path
from statistics import mean, median
from typing import Callable

from adaptive import AdaptiveFlags, adaptive_v03
from sat_core import SATInstance, gen_planted, gen_unsat_core
from solvers import junction_base, junction_tunnel_v02, walksat

def summarize(records: list[dict], group_keys: tuple[str, ...]) -> list[dict]:
    buckets: dict[tuple, list[dict]] = {}
    for rec in records:
        key = tuple(rec[k] for k in group_keys)
        buckets.setdefault(key, []).append(rec)
    rows = []
    for key, vals in buckets.items():
        sol = [x for x in vals if x["solved"]]
        row = {k: v for k, v in zip(group_keys, key)}
        row.update(
            trials=len(vals),
            solve_rate=mean(float(x["solved"]) for x in vals),
            median_steps_solved=median(x["steps"] for x in sol) if sol else None,
            mean_steps_all=mean(x["steps"] for x in vals),
            mean_best_ratio=mean(x["best_ratio"] for x in vals),
            mean_ms=mean(x["ms"] for x in vals),
            median_ms=median(x["ms"] for x in vals),
            mean_escapes=mean(x["escapes"] for x in vals),
            mean_escape_attempts=mean(x["escape_attempts"] for x in vals),
            escape_acceptance=(sum(x["escapes"] for x in vals) / max(1, sum(x["escape_attempts"] for x in vals))),
            immediate_escape_improvement_rate=(sum(x["immediate_improving_escapes"] for x in vals) / max(1, sum(x["escapes"] for x in vals))),
            mean_uphill=mean(x["accepted_uphill"] for x in vals),
            mean_max_depth=mean(x["max_depth"] for x in vals),
            mean_depth=mean(x["mean_depth"] for x in vals),
        )
        rows.append(row)
    return rows


def timed_run(name: str, fn: Callable, inst: SATInstance, initial: list[int], budget: int, seed: int, extra: dict | None = None):
    rng = random.Random(seed)
    t0 = time.perf_counter()
    solved, steps, best, diag = fn(inst, initial, budget, rng)
    ms = (time.perf_counter() - t0) * 1000.0
    rec = {
        "method": name,
        "solved": bool(solved),
        "steps": int(steps),
        "best_ratio": best / len(inst.clauses),
        "ms": ms,
        **diag,
    }
    if extra:
        rec.update(extra)
    return rec


def run_suite() -> dict:
    holdout_seed = 440223
    master = random.Random(holdout_seed)
    budget_factor = 28
    main_trials = 16
    unsat_trials = 4
    ablation_trials = 10

    methods = [
        ("walksat", walksat),
        ("junction_base", junction_base),
        ("junction_tunnel_v02", junction_tunnel_v02),
        ("junction_adaptive_v03", adaptive_v03),
    ]
    main_configs = [
        (3, 32, round(4.26 * 32)),
        (3, 48, round(4.26 * 48)),
        (3, 64, round(4.26 * 64)),
        (3, 96, round(4.26 * 96)),
        (3, 128, round(4.26 * 128)),
        (5, 48, round(6.10 * 48)),
        (5, 64, round(6.10 * 64)),
        (5, 96, round(6.10 * 96)),
    ]

    detail: list[dict] = []
    for k, n, m in main_configs:
        for trial in range(main_trials):
            inst_seed = master.randrange(2**31)
            init_seed = master.randrange(2**31)
            inst = gen_planted(n, m, k, random.Random(inst_seed))
            initial = [random.Random(init_seed + v * 104729).randrange(2) for v in range(n)]
            budget = budget_factor * n
            for mi, (name, fn) in enumerate(methods):
                rec = timed_run(name, fn, inst, initial, budget, inst_seed ^ (0x9E3779B1 + mi * 1000003))
                rec.update(suite="main_sat", truth="sat_known", k=k, n=n, m=m, alpha=m / n, trial=trial,
                           inst_seed=inst_seed, init_seed=init_seed, budget=budget)
                detail.append(rec)

    unsat_configs = [(3, 32, round(4.26 * 32)), (3, 64, round(4.26 * 64)), (3, 96, round(4.26 * 96)), (5, 64, round(6.10 * 64))]
    for k, n, m in unsat_configs:
        for trial in range(unsat_trials):
            inst_seed = master.randrange(2**31)
            init_seed = master.randrange(2**31)
            inst = gen_unsat_core(n, m, k, random.Random(inst_seed))
            initial = [random.Random(init_seed + v * 104729).randrange(2) for v in range(n)]
            budget = budget_factor * n
            for mi, (name, fn) in enumerate(methods):
                rec = timed_run(name, fn, inst, initial, budget, inst_seed ^ (0x85EBCA77 + mi * 1000003))
                rec.update(suite="unsat_core_stress", truth="unsat_known_core", k=k, n=n, m=m, alpha=m / n,
                           trial=trial, inst_seed=inst_seed, init_seed=init_seed, budget=budget)
                detail.append(rec)

    ablations = [
        ("adaptive_full", AdaptiveFlags()),
        ("adaptive_no_repeat", AdaptiveFlags(repeat=False)),
        ("adaptive_no_oscillation", AdaptiveFlags(oscillation=False)),
        ("adaptive_no_charge", AdaptiveFlags(charge=False)),
        ("adaptive_no_avalanche", AdaptiveFlags(avalanche=False)),
    ]
    for n in (32, 64, 96):
        k, m = 3, round(4.26 * n)
        for trial in range(ablation_trials):
            inst_seed = master.randrange(2**31)
            init_seed = master.randrange(2**31)
            inst = gen_planted(n, m, k, random.Random(inst_seed))
            initial = [random.Random(init_seed + v * 104729).randrange(2) for v in range(n)]
            budget = budget_factor * n
            for ai, (name, flags) in enumerate(ablations):
                fn = lambda i, a, b, r, f=flags: adaptive_v03(i, a, b, r, f)
                rec = timed_run(name, fn, inst, initial, budget, inst_seed ^ (0xC2B2AE3D + ai * 1000003))
                rec.update(suite="ablation", truth="sat_known", k=k, n=n, m=m, alpha=m / n, trial=trial,
                           inst_seed=inst_seed, init_seed=init_seed, budget=budget)
                detail.append(rec)

    main_rows = summarize([x for x in detail if x["suite"] == "main_sat"], ("suite", "truth", "k", "n", "m", "alpha", "method"))
    unsat_rows = summarize([x for x in detail if x["suite"] == "unsat_core_stress"], ("suite", "truth", "k", "n", "m", "alpha", "method"))
    ablation_rows = summarize([x for x in detail if x["suite"] == "ablation"], ("suite", "truth", "k", "n", "m", "alpha", "method"))

    result = {
        "experiment": "JANUS P-N Junction v0.3 adaptive depletion-depth detector",
        "holdout_seed": holdout_seed,
        "parameter_freeze": "Detector coefficients and thresholds were fixed in source before executing the holdout suite.",
        "fairness": "Every method received the same SAT instance and identical initial assignment per trial; method RNG streams were deterministic and method-specific.",
        "budget_factor_steps_per_variable": budget_factor,
        "main_trials_per_point": main_trials,
        "unsat_trials_per_point": unsat_trials,
        "ablation_trials_per_point": ablation_trials,
        "unsat_boundary": "UNSAT tests contain a guaranteed contradictory k-CNF core. They test false-solve safety and behavior without recombination, not general UNSAT certification.",
        "main_rows": main_rows,
        "unsat_rows": unsat_rows,
        "ablation_rows": ablation_rows,
        "detail": detail,
    }

    out_dir = Path(__file__).resolve().parent
    with open(out_dir / "results_full.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    for path, rows in [
        (out_dir / "main.csv", main_rows),
        (out_dir / "unsat_core_stress.csv", unsat_rows),
        (out_dir / "ablation.csv", ablation_rows),
    ]:
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    return result


if __name__ == "__main__":
    result = run_suite()
    print(json.dumps({
        "status": "completed",
        "experiment": result["experiment"],
        "holdout_seed": result["holdout_seed"],
        "detail_records": len(result["detail"]),
        "outputs": [
            "results_full.json",
            "main.csv",
            "unsat_core_stress.csv",
            "ablation.csv"
        ]
    }, indent=2))
