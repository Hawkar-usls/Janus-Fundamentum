#!/usr/bin/env python3
"""JANUS-TACHYON-001 adversarial re-audit, frozen deterministic finite suite.

Separates simple candidate-first verification from additional retrograde
variable/branch ordering. The former is NOT a novel "future" mechanism.
All variants run on the same SAT/Exact-One rows and are independently checked
against exact brute-force UFR verify_model semantics. Three full-cost timings
per variant, no post-hoc instance selection or general speedup claim.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
import os
from pathlib import Path
import random
from statistics import median

from janus_tachyon_001 import search
from janus_ufr_001 import normalize, verify_model

SEED = 20261101
CASES_PER_FAMILY = 12
REPEATS = 3
VARIANTS = (
    ("forward", "forward"),
    ("same_hint_candidate_first", "candidate_first"),
    ("tachyon_retrograde", "retrograde"),
)


def fixed_suite():
    rng = random.Random(SEED)
    cases = []
    for family in ("SAT_RANDOM", "SAT_PLANTED", "EXACT_ONE_RANDOM",
                   "EXACT_ONE_PLANTED", "SAT_CONTRADICTION"):
        for index in range(CASES_PER_FAMILY):
            n = (6, 8, 10)[index % 3]
            kind = "EXACT_ONE" if family.startswith("EXACT_ONE") else "SAT"
            planted = rng.randrange(1 << n)
            rows = []
            if family == "SAT_CONTRADICTION":
                v = rng.randrange(1, n+1)
                rows = [(v,), (-v,)]
            else:
                for _ in range(5 + (index % 9)):
                    variables = rng.sample(range(1, n+1), 3)
                    if family.endswith("PLANTED"):
                        selected = rng.randrange(3)
                        row = []
                        for i, v in enumerate(variables):
                            bit = ((planted >> (v-1)) & 1) == 1
                            positive = bit if kind == "SAT" or i == selected else not bit
                            row.append(v if positive else -v)
                    else:
                        row = [v if rng.randrange(2) else -v for v in variables]
                    rows.append(tuple(row))
            cases.append((f"{family}_{index:02d}", tuple(rows), n, kind, family))
    # SHA-independent, pinned list of instances before examining outcomes.
    return cases


def source_sha(cases):
    payload = [{"id":id,"n":n,"kind":kind,"rows":rows,"family":family}
               for id,rows,n,kind,family in cases]
    return sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()


def exact_truth(rows, n, kind):
    norm=normalize(rows)
    out=[]
    for x in range(1 << n):
        assignment={v:bool(x & (1 << (v-1))) for v in range(1,n+1)}
        if verify_model(norm,assignment,kind):
            out.append(x)
    return out


def run():
    cases=fixed_suite()
    reference_sha=source_sha(cases)
    results=[]
    for case_id,rows,n,kind,family in cases:
        expected=exact_truth(rows,n,kind)
        stats={}
        for name,strategy in VARIANTS:
            values=[search(rows,n,kind,strategy=strategy,gac=True)
                    for _ in range(REPEATS)]
            if any(v.answer!=bool(expected) or not v.result_verified or
                   (v.candidate is not None and v.candidate not in expected)
                   for v in values):
                raise AssertionError("Wrong answer, invalid model or broken UNSAT: "+case_id)
            stats[name]={
                "median_full_wall_seconds":median(x.elapsed_seconds for x in values),
                "recursive_nodes":values[-1].nodes,
                "hint_tested":values[-1].echoed_candidate_checked,
                "hint_directly_accepted":values[-1].echoed_candidate_accepted,
                "SAT_answer":values[-1].answer,
            }
        results.append({
            "id":case_id,"family":family,"n":n,"kind":kind,
            "solutions":len(expected),
            "same_hypothesis_comparison_is_fair":True,
            "variants":stats,
        })
    wins=Counter()
    by_family={}
    for family in sorted({x["family"] for x in results}):
        group=[c for c in results if c["family"]==family]
        def summary(baseline,variant):
            compare=[(
              x["variants"][baseline]["median_full_wall_seconds"],
              x["variants"][variant]["median_full_wall_seconds"],
            ) for x in group]
            return {
                "faster":sum(t<s for s,t in compare),
                "slower":sum(t>s for s,t in compare),
                "median_variant_over_baseline":median(
                    t/s for s,t in compare if s>0),
                "comparisons":len(compare),
            }
        by_family[family]={
            "count":len(group),
            "SAT_count":sum(c["solutions"]>0 for c in group),
            "UNSAT_count":sum(c["solutions"]==0 for c in group),
            "retrograde_vs_equal_candidate_baseline":
                summary("same_hint_candidate_first","tachyon_retrograde"),
            "candidate_first_vs_forward":
                summary("forward","same_hint_candidate_first"),
            "direct_echo_accepted":sum(c["variants"]["tachyon_retrograde"]
                                       ["hint_directly_accepted"] for c in group),
            "retrograde_tree_nodes_less_than_same_hint":
                sum(c["variants"]["tachyon_retrograde"]["recursive_nodes"]
                    < c["variants"]["same_hint_candidate_first"]["recursive_nodes"]
                    for c in group),
        }
    return {
        "schema":"JANUS-TACHYON-001-FAIR-HOLDOUT-ABLATION-V1",
        "status":"DETERMINISTIC_FINITE_SUITE_NOT_EXTERNAL_BLIND_HOLDOUT",
        "source":{"sha":os.getenv("GITHUB_SHA","local"),"run":os.getenv("GITHUB_RUN_ID","local")},
        "preregistration":{"seed":SEED,"cases_per_family":CASES_PER_FAMILY,
                           "suite_sha256":reference_sha,
                           "case_count":len(results),"repeats":REPEATS,
                           "evaluated_all_generated_cases":True},
        "comparison":{
            "candidate_first":"Uses EXACT SAME computed echo + direct candidate check, with ordinary forward branch order",
            "retrograde":"Same echo and direct check; on failure changes variable and branch order only",
            "forward":"No echoed candidate; left-to-right branching",
            "timing":"Full per-call formula parsing, echo synthesis when used, candidate check, proof/UNSAT exhaustive check",
            "reference":"Independent UFR verify_model evaluates every 2^n assignment",
        },
        "aggregates_by_family":by_family,
        "cases":results,
        "promotion_gate":"NOT_READY: no cross-size general speedup or independent blind test",
        "scientific_limits":[
            "No future signal: hypothesis computed from known clauses",
            "No information leakage permitted from planted witness to search",
            "Frozen pseudorandom suite is not independent secretly hidden benchmark",
            "Microsecond timings on GitHub runners are noisy: treat ratios as descriptive",
            "Unsat is independently verified by enumeration only for n<=10",
            "UFR and original production C023 unaffected; no promotion",
            "Physical tachyons/retrocausality, speculative archive associations and no-calibration probabilities remain unproven",
        ],
    }


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path("evidence/tachyon-001-fair-holdout.json"))
    args=p.parse_args()
    out=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"schema":out["schema"],"status":out["status"],
                     "preregistration":out["preregistration"],
                     "aggregates_by_family":out["aggregates_by_family"]},indent=2))
