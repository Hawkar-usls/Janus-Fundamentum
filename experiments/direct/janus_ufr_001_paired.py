#!/usr/bin/env python3
"""UFR-001 paired independent-worker comparison with bounded cloud spend.

Each measurement runs in a fresh Python process. Uses ru_maxrss (Linux RSS)
rather than Python tracemalloc alone. Alternates method order per replicate.
This code creates EVIDENCE ONLY: it never merges PRs or changes production.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import resource
import statistics
import subprocess
import sys
import time

from janus_ufr_001_adversarial import fixtures, run_case

MAIN = "MAJ3_K4"
CONTROLS = ("GT5", "TSEITIN_K4_NONAFFINE_WRAPPED",
            "INDEPENDENT_3SAT_SEED_173", "INDEPENDENT_EXACT_ONE_SEED_271")


def worker(fixture: str, method: str, state_cap: int):
    all_fixtures = dict(fixtures(extended=True))
    if fixture not in all_fixtures:
        raise ValueError(f"unknown fixture: {fixture}")
    if method not in ("EXACT_C023", "CERTIFIED_UFR_C023"):
        raise ValueError(f"unknown method: {method}")
    cnf, n = all_fixtures[fixture]
    started = time.perf_counter()
    result = run_case(cnf, n, method, state_cap)
    result["end_to_end_seconds"] = round(time.perf_counter() - started, 6)
    # ru_maxrss on Linux is KiB (peak from startup, solve AND replay).
    result["peak_rss_bytes"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
    result["method"] = method
    result["fixture"] = fixture
    result["variables"] = n
    result["clauses"] = len(cnf)
    return result


def subprocess_measure(fixture: str, method: str, state_cap: int):
    cmd = [sys.executable, str(Path(__file__).resolve()), "--worker",
           "--fixture", fixture, "--method", method, "--state-cap", str(state_cap)]
    wall_start = time.perf_counter()
    result = subprocess.run(cmd, text=True, capture_output=True, timeout=180,
                            check=True)
    data = json.loads(result.stdout)
    data["process_wall_seconds"] = round(time.perf_counter() - wall_start, 6)
    return data


def assert_pair(fixture: str, baseline: dict, ufr: dict):
    if baseline["status"] != "PASS_REPLAY" or ufr["status"] != "PASS_REPLAY":
        raise AssertionError(f"{fixture}: both independent proof replays required")
    if type(baseline["answer"]) is not bool or baseline["answer"] != ufr["answer"]:
        raise AssertionError(f"{fixture}: disagreeing or non-Boolean solutions")
    if fixture == MAIN:
        if baseline["calls"] != 4117 or baseline["unique_states"] != 2427:
            raise AssertionError("baseline C023 reference unexpectedly changed")
        if ufr["isomorphic_cache_hits"] < 165 or ufr["unique_states"] > 2354:
            raise AssertionError("165-hit structural regression gate FAILED")


def record_pair(fixture: str, index: int, cap: int):
    # Reverse order to control host drift / CPU warmup.
    methods = ("EXACT_C023", "CERTIFIED_UFR_C023") if index % 2 == 0 else (
        "CERTIFIED_UFR_C023", "EXACT_C023")
    results = {method: subprocess_measure(fixture, method, cap) for method in methods}
    baseline, ufr = results["EXACT_C023"], results["CERTIFIED_UFR_C023"]
    assert_pair(fixture, baseline, ufr)
    return {
        "fixture": fixture, "replicate": index + 1,
        "run_order": list(methods), "baseline": baseline, "ufr": ufr,
        "solve_ratio": round(ufr["wall_seconds"] / baseline["wall_seconds"], 6),
        "end_to_end_ratio": round(
            ufr["end_to_end_seconds"] / baseline["end_to_end_seconds"], 6),
        "rss_ratio": round(ufr["peak_rss_bytes"] / baseline["peak_rss_bytes"], 6)
    }


def run_suite(rounds: int, cap: int, output: Path):
    if rounds < 3 or rounds > 7:
        raise ValueError("require 3-7 paired MAJ3 repetitions")
    pairs = []
    for i in range(rounds):
        row = record_pair(MAIN, i, cap)
        pairs.append(row)
        print(json.dumps({"pair": MAIN, "replicate": i + 1,
                          "solve_ratio": row["solve_ratio"],
                          "rss_ratio": row["rss_ratio"],
                          "iso_hits": row["ufr"]["isomorphic_cache_hits"]}),
              flush=True)
    for i, name in enumerate(CONTROLS):
        row = record_pair(name, i, cap)
        pairs.append(row)
        print(json.dumps({"control": name, "solve_ratio": row["solve_ratio"]}),
              flush=True)
    main_pairs = [row for row in pairs if row["fixture"] == MAIN]
    summary = {
        "maj3_solve_median_ratio": statistics.median(x["solve_ratio"] for x in main_pairs),
        "maj3_end_to_end_median_ratio": statistics.median(
            x["end_to_end_ratio"] for x in main_pairs),
        "maj3_rss_median_ratio": statistics.median(x["rss_ratio"] for x in main_pairs),
        "maj3_solve_worst_ratio": max(x["solve_ratio"] for x in main_pairs),
        "maj3_rss_worst_ratio": max(x["rss_ratio"] for x in main_pairs),
        "control_solve_worst_ratio": max(
            x["solve_ratio"] for x in pairs if x["fixture"] != MAIN),
    }
    evidence = {
        "schema": "JANUS-UFR-PAIRED-RSS-V1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "MEASURED_NOT_AUTOMATICALLY_PROMOTED",
        "source": {"repository": "Hawkar-usls/Janus-Fundamentum",
                   "head_sha": os.getenv("GITHUB_SHA", "local"),
                   "run_id": os.getenv("GITHUB_RUN_ID", "local"),
                   "runner": os.getenv("RUNNER_NAME", "local"),
                   "os_label": os.getenv("UFR_RUNNER_OS", platform.platform()),
                   "python": sys.version.split()[0]},
        "state_cap": cap,
        "repetitions": rounds,
        "summary": summary,
        "pairs": pairs,
        "boundaries": ["Each result is independently replayed",
                       "Peak RSS from fresh Linux subprocess",
                       "Single job is not independent of itself",
                       "Independent operating-system matrix required",
                       "No automatic promotion on one-run wins"],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"summary": summary, "evidence": str(output)}, indent=2))
    return evidence


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--fixture", default=MAIN)
    parser.add_argument("--method", default="EXACT_C023")
    parser.add_argument("--state-cap", type=int, default=3000)
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--out", default="ufr-paired.json")
    args = parser.parse_args()
    if platform.system() != "Linux":
        raise RuntimeError("Linux runner required for ru_maxrss comparability")
    if args.worker:
        print(json.dumps(worker(args.fixture, args.method, args.state_cap)))
        return
    run_suite(args.rounds, args.state_cap, Path(args.out))


if __name__ == "__main__":
    main()
