from __future__ import annotations

import json
import math
import random
import time
from pathlib import Path
from statistics import mean, median

from sat_core import gen_planted, gen_unsat_core
from solvers import walksat, junction_base
from adaptive import adaptive_v03
from selective_swarm_v20 import selective_swarm_v20

SEED = 440224
OUT = Path(__file__).resolve().parent.parent / "reproduced_holdout_results.json"

SAT_CONFIGS = [
    (3, 32, round(4.26 * 32), 8),
    (3, 48, round(4.26 * 48), 8),
    (3, 64, round(4.26 * 64), 8),
    (3, 96, round(4.26 * 96), 8),
    (3, 128, round(4.26 * 128), 8),
    (3, 160, round(4.26 * 160), 8),
    (3, 192, round(4.26 * 192), 8),
    (3, 240, round(4.26 * 240), 8),
    (5, 64, round(6.1 * 64), 8),
    (5, 96, round(6.1 * 96), 8),
    (5, 128, round(6.1 * 128), 8),
]
UNSAT_CONFIGS = [
    (3, 32, round(4.26 * 32), 6),
    (3, 64, round(4.26 * 64), 6),
    (5, 64, round(6.1 * 64), 6),
]
METHODS = [
    ("walksat", walksat),
    ("junction_base", junction_base),
    ("adaptive_v03", adaptive_v03),
    ("swarm_v20", selective_swarm_v20),
]


def main() -> None:
    master = random.Random(SEED)
    records: list[dict] = []

    for k, n, m, trials in SAT_CONFIGS:
        for trial in range(trials):
            inst_seed = master.randrange(2**31)
            init_seed = master.randrange(2**31)
            inst = gen_planted(n, m, k, random.Random(inst_seed))
            init_rng = random.Random(init_seed)
            initial = [init_rng.randrange(2) for _ in range(n)]
            budget = 28 * n
            seeds = {
                "walksat": inst_seed ^ 0x13579BDF,
                "junction_base": inst_seed ^ 0x2468ACE0,
                "adaptive_v03": inst_seed ^ 0x9E3779B1,
                "swarm_v20": inst_seed ^ 0x9E3779B1,
            }
            for name, solver in METHODS:
                started = time.perf_counter()
                solved, steps, best, diag = solver(inst, initial, budget, random.Random(seeds[name]))
                records.append({
                    "suite": "holdout_sat",
                    "truth": "sat_known",
                    "seed": SEED,
                    "k": k,
                    "n": n,
                    "m": m,
                    "trial": trial,
                    "inst_seed": inst_seed,
                    "init_seed": init_seed,
                    "budget": budget,
                    "method": name,
                    "solved": solved,
                    "latency_steps": steps,
                    "best_ratio": best / m,
                    "ms": (time.perf_counter() - started) * 1000,
                    **diag,
                })
        print(f"completed SAT k={k} n={n}")

    for k, n, m, trials in UNSAT_CONFIGS:
        for trial in range(trials):
            inst_seed = master.randrange(2**31)
            init_seed = master.randrange(2**31)
            inst = gen_unsat_core(n, m, k, random.Random(inst_seed))
            init_rng = random.Random(init_seed)
            initial = [init_rng.randrange(2) for _ in range(n)]
            budget = 12 * n
            for name, solver in [("adaptive_v03", adaptive_v03), ("swarm_v20", selective_swarm_v20)]:
                started = time.perf_counter()
                solved, steps, best, diag = solver(inst, initial, budget, random.Random(inst_seed ^ 0x9E3779B1))
                records.append({
                    "suite": "unsat_core",
                    "truth": "unsat_known",
                    "seed": SEED,
                    "k": k,
                    "n": n,
                    "m": m,
                    "trial": trial,
                    "inst_seed": inst_seed,
                    "init_seed": init_seed,
                    "budget": budget,
                    "method": name,
                    "solved": solved,
                    "latency_steps": steps,
                    "best_ratio": best / m,
                    "ms": (time.perf_counter() - started) * 1000,
                    **diag,
                })
        print(f"completed UNSAT k={k} n={n}")

    def aggregate(method: str) -> dict:
        rows = [r for r in records if r["suite"] == "holdout_sat" and r["k"] == 3 and r["method"] == method]
        solved = [r for r in rows if r["solved"]]
        ordered = sorted(r["latency_steps"] for r in rows)
        return {
            "method": method,
            "trials": len(rows),
            "solved": len(solved),
            "solve_rate": len(solved) / len(rows),
            "median_latency": median(r["latency_steps"] for r in solved),
            "mean_latency": mean(r["latency_steps"] for r in rows),
            "p90_latency": ordered[math.ceil(0.9 * len(ordered)) - 1],
            "mean_ms": mean(r["ms"] for r in rows),
            "mean_total_work": mean(r.get("total_work", r["latency_steps"]) for r in rows),
        }

    output = {
        "experiment": "JANUS P-N Junction Selective Distributed Field v2.0",
        "holdout_seed": SEED,
        "parameter_freeze": "before holdout",
        "fairness": "same formulas and initial assignments; v0.3 and v2.0 use identical control-lane RNG state",
        "headline_3sat": [aggregate(name) for name, _ in METHODS],
        "detail": records,
    }
    OUT.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
