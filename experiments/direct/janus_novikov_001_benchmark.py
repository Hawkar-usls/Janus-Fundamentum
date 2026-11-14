#!/usr/bin/env python3
"""NOVIKOV-001: same 60 frozen SAT/Exact-One instances as TACHYON-001.

Four fair, full-cost approaches:
  ordinary candidate-first / retrograde from the same raw hint, and
  greedy-consistency repaired-hint with each same fallback ordering.

The repairs are *ordinary deterministic local search*, not future signals.
No free preprocessing: all normalization, heuristic, repair, independent
trace replay and full SAT/UNSAT verification are inside measured search time.
The frozen suite is not externally blinded and times are microbenchmarks.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from hashlib import sha256
import json
import os
from pathlib import Path
import statistics

from janus_novikov_001 import guided_search, repair
from janus_tachyon_001 import initial_echo, search
from janus_tachyon_001_fair_holdout import (
    fixed_suite, exact_truth, source_sha,
)
from janus_ufr_001 import normalize

REPEATS = 3
VARIANTS = (
    "same_hint_candidate_first",
    "same_hint_retrograde",
    "consistency_repair_candidate_first",
    "consistency_repair_retrograde",
)


def run():
    fixtures = fixed_suite()
    rows_out = []
    for key, rows, n, kind, family in fixtures:
        expected = exact_truth(rows, n, kind)
        normalized = normalize(rows)
        hint = initial_echo(normalized, n)
        # Independent descriptive metadata, not counted in timed searches.
        proposal = repair(rows, n, kind, hint=hint)
        measured = defaultdict(list)
        # Interleave variants so a steady machine warmup favors none.
        for turn in range(REPEATS):
            order = VARIANTS if turn % 2 == 0 else tuple(reversed(VARIANTS))
            for variant in order:
                if variant == "same_hint_candidate_first":
                    candidate = search(rows, n, kind, strategy="candidate_first")
                    time_cost = candidate.elapsed_seconds
                    answer, model, nodes = candidate.answer, candidate.candidate, candidate.nodes
                    verified = candidate.result_verified
                    additional_steps = 0
                elif variant == "same_hint_retrograde":
                    candidate = search(rows, n, kind, strategy="retrograde")
                    time_cost = candidate.elapsed_seconds
                    answer, model, nodes = candidate.answer, candidate.candidate, candidate.nodes
                    verified = candidate.result_verified
                    additional_steps = 0
                else:
                    route = ("candidate_first" if variant.endswith("candidate_first")
                             else "retrograde")
                    candidate = guided_search(rows, n, kind, fallback=route)
                    time_cost = candidate.full_wall_seconds
                    answer, model, nodes = candidate.answer, candidate.candidate, candidate.nodes
                    verified = (candidate.independent_repair_audit_pass
                                and candidate.independent_search_verification_pass)
                    additional_steps = candidate.repair_steps
                if (answer != bool(expected)
                        or (model is not None) != bool(expected)
                        or (model is not None and model not in expected)
                        or not verified):
                    raise AssertionError(f"Novikov false verdict or candidate: {key} {variant}")
                measured[variant].append({
                    "elapsed_seconds": time_cost, "nodes": nodes,
                    "repair_steps": additional_steps,
                })
        result = {}
        for variant in VARIANTS:
            values = measured[variant]
            if len(values) != REPEATS:
                raise AssertionError("incomplete replay")
            result[variant] = {
                "full_wall_median_seconds": statistics.median(
                    v["elapsed_seconds"] for v in values),
                "full_wall_samples_seconds": [v["elapsed_seconds"] for v in values],
                "recursive_nodes": values[0]["nodes"],
                "repair_steps": values[0]["repair_steps"],
                "all_valid_against_independent_truth": True,
            }
        rows_out.append({
            "case": key, "family": family, "kind": kind, "n": n,
            "exact_number_of_solutions": len(expected),
            "initial_echo_violations": proposal.start_violations,
            "repair_final_violations": proposal.final_violations,
            "repair_status": proposal.status,
            "raw_hint_independently_satisfying": proposal.start_violations == 0,
            "repaired_hint_independently_satisfying": proposal.independently_verified,
            "metrics": result,
        })

    by_family = {}
    for family in sorted({x["family"] for x in rows_out}):
        cases = [x for x in rows_out if x["family"] == family]
        tests = []
        for prior, after in (
            ("same_hint_candidate_first", "consistency_repair_candidate_first"),
            ("same_hint_retrograde", "consistency_repair_retrograde"),
            ("consistency_repair_candidate_first", "consistency_repair_retrograde"),
        ):
            vals = [(c["metrics"][prior]["full_wall_median_seconds"],
                     c["metrics"][after]["full_wall_median_seconds"])
                    for c in cases]
            tests.append({
                "baseline": prior, "variant": after,
                "faster_cases": sum(new < old for old, new in vals),
                "slower_cases": sum(new > old for old, new in vals),
                "median_ratio_variant_over_baseline":
                    statistics.median(new / old for old, new in vals if old > 0),
                "count": len(vals),
            })
        by_family[family] = {
            "number_of_cases": len(cases),
            "sat_cases": sum(c["exact_number_of_solutions"] > 0 for c in cases),
            "unsat_cases": sum(c["exact_number_of_solutions"] == 0 for c in cases),
            "raw_hint_satisfies": sum(c["raw_hint_independently_satisfying"] for c in cases),
            "repaired_hint_satisfies": sum(c["repaired_hint_independently_satisfying"] for c in cases),
            "local_minima_not_accepted_as_UNSAT":
                sum(c["repair_status"] == "LOCAL_MINIMUM_NOT_UNSAT" for c in cases),
            "comparisons": tests,
        }
    return {
        "schema":"JANUS-NOVIKOV-001-CONSISTENCY-ABLATION-V1",
        "status":"BOUNDED_CLASSICAL_RESEARCH_ONLY",
        "provenance":{"sha":os.getenv("GITHUB_SHA","local"),
                      "run":os.getenv("GITHUB_RUN_ID","local")},
        "frozen_suite":{"source":"janus_tachyon_001_fair_holdout.fixed_suite",
                        "sha256":source_sha(fixtures),
                        "case_count":len(rows_out),
                        "repeats":REPEATS,
                        "instance_labels_hidden_from_candidate_solver":True},
        "controls":{
            "all_sat_unsat_labels_independently_enumerated":True,
            "same_hint_build_and_direct_validation":True,
            "same_cases_all_methods":True,
            "interleaved_order":True,
            "repair_energy_strictly_decreases":True,
            "local_minimum_never_assumed_UNSAT":True,
            "independently_replayed_repair_transcript":True,
            "measure_full_wall_including_preparation_trace_and_proof":True,
        },
        "aggregates_by_family":by_family,
        "cases":rows_out,
        "promotion_gate":"NOT_READY",
        "limitations":[
            "Mathematical analogy to Novikov self-consistency, not closed timelike curves",
            "Greedy 1-bit local energy descent is classical heuristic; local minimum does NOT imply UNSAT",
            "Only n<=10; UNSAT established with full 2^n independent enumeration, not Novikov principle",
            "Same known deterministic suite as previous benchmark, not external blind evaluation",
            "Tiny elapsed times subject to host jitter, no inferential significance",
            "Production C023 unchanged, no SAT complexity theorem, no physical tachyon detection",
        ],
    }


if __name__ == "__main__":
    cli = argparse.ArgumentParser()
    cli.add_argument("--out", type=Path,
                     default=Path("evidence/novikov-001.json"))
    args = cli.parse_args()
    result = run()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n",
                        encoding="utf-8")
    print(json.dumps({
        "schema":result["schema"],
        "status":result["status"],
        "frozen_suite":result["frozen_suite"],
        "aggregates_by_family":result["aggregates_by_family"],
    }, indent=2, sort_keys=True))
