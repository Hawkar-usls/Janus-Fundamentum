#!/usr/bin/env python3
"""Falsifiable tiny SAT/Exact-One comparison: forward vs "future-echo" DPLL.

Classical computation ONLY. The benchmark independently exhaustive-verifies
SAT/UNSAT on all n<=10 input assignments and includes time spent validating
this proof. Echo is not a time signal or quantum interaction; no P=NP claim.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import statistics

from janus_deutsch_001_benchmark import experiments
from janus_tachyon_001 import evaluate, initial_echo, search
from janus_ufr_001 import normalize, verify_model

REPEATS = 5
CONF = (
    ("baseline_unit", "forward", False),
    ("baseline_exact_support", "forward", True),
    ("tachyon_echo_exact_support", "retrograde", True),
)


def run():
    cases = []
    for label, rows, n, kind in experiments():
        normalized = normalize(rows)
        hint = initial_echo(normalized, n)
        variants = []
        # Independent reference semantics: UFR literal-count evaluator, not
        # the Tachyon module's own Boolean evaluator.
        global_answers = [
            x for x in range(1 << n)
            if verify_model(normalized, {
                v: bool((x >> (v-1)) & 1) for v in range(1, n+1)
            }, kind)
        ]
        for variant, strategy, gac in CONF:
            measurements = [
                search(rows, n, kind, strategy=strategy, gac=gac)
                for _ in range(REPEATS)
            ]
            if any(v.answer != bool(global_answers) or
                   not v.result_verified or
                   (v.candidate is not None and v.candidate not in global_answers)
                   for v in measurements):
                raise AssertionError(f"contradictory search evidence on {label}")
            variants.append({
                "variant": variant,
                "answer": measurements[-1].answer,
                "nodes": measurements[-1].nodes,
                "end_to_end_seconds_median_including_parsing_echo_and_model_or_exhaustive_check":
                    statistics.median(v.elapsed_seconds for v in measurements),
                "untrusted_echo_candidate_tested": measurements[-1].echoed_candidate_checked,
                "untrusted_echo_accepted_after_direct_model_check":
                    measurements[-1].echoed_candidate_accepted,
                "independently_verified": True,
            })
        wrong = tuple(1 - bit for bit in hint)
        counter = search(rows, n, kind, echo=wrong, strategy="retrograde", gac=True)
        if counter.answer != bool(global_answers) or not counter.result_verified:
            raise AssertionError("reversed-future negative control changed truth")
        cases.append({
            "case": label, "variables": n, "kind": kind,
            "rows": len(rows),
            "source_sha256": sha256(json.dumps(
                {"n": n, "kind": kind, "rows": normalized},
                separators=(",", ":"), sort_keys=True
            ).encode()).hexdigest(),
            "exact_full_truth_solution_count": len(global_answers),
            "echo_model": list(hint),
            "echo_precomputation_is_inside_timed_search": True,
            "reversed_echo_still_complete": True,
            "compared": variants,
        })
    return {
        "schema": "JANUS-TACHYON-001-FINITE-EVIDENCE-V1",
        "head_sha": os.getenv("GITHUB_SHA", "local"),
        "run_id": os.getenv("GITHUB_RUN_ID", "local"),
        "conclusion": "FALLIBLE_RETROGRADE_HINT_ONLY_NO_CAUSAL_REVERSAL",
        "claims": [
            "Future echo is a heuristic guess from known input clauses, not information from future",
            "It can order branches and offer a directly checked SAT candidate only",
            "Independent exhaustive verification n<=10 protects SAT and UNSAT answers",
            "Local generalized arc consistency is a standard sound constraint operation; on Boolean variables the unit and GAC support reductions can coincide",
            "All timings are tiny noisy classical measurements, no claimed speedup",
            "Experimental module leaves proof-producing production C023 untouched",
            "PENROSE-003 prohibits any real FINAL_GATE -> UFR_PRODUCE causal dependency",
            "Not tested on MAJ3-K4 n18; cannot compare these microcases to that workload",
        ],
        "cases": cases,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="")
    args = parser.parse_args()
    out = json.dumps(run(), indent=2, sort_keys=True) + "\n"
    if args.out:
        p = Path(args.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(out, encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
