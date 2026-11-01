#!/usr/bin/env python3
"""TIME-SAT-PARTIAL-002: pre-frozen public controls and four-arm CDCL trial.

This is a deterministic **public development experiment**, NOT an external
blind holdout and NOT a proof-producing UNSAT solver. No thresholds are fitted
to these outcomes. Same source CNF and same CDCL per compared arm.
The gate never sees reference labels, solver runtimes or probe results.

Paired bootstrap resamples INSTANCE ratios, not runs as independent samples.
It is descriptive on an already-known public suite, not generalization proof.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import random
import resource
import statistics

from janus_time_sat_partial_001 import canonical_sat_cnf, source_hash
from janus_time_sat_partial_002 import ARMS, run_arm
from janus_novikov_002_benchmark import suite as previous_suite
from janus_tachyon_001_fair_holdout import exact_truth, fixed_suite, source_sha

SOLVERS=("cadical195","glucose4")
SMALL_REPEATS=3
LARGE_REPEATS=2
BOOTSTRAP_SEED=20261102
BOOTSTRAP_REPLICATES=2000


def fixed_controls():
    small,large=previous_suite()
    # Only positive mechanism controls; never cherry-pick results into
    # claims of performance improvement on the existing development set.
    mechanism=[
        ("WEDGE_SAT_3",((-1,2),(-1,-2),(1,3)),3,"SAT","mechanism"),
        ("WEDGE_UNSAT_3",((-1,2),(-1,-2),(1,3),(1,-3)),3,"SAT","mechanism"),
        ("WEDGE_EXACT_ONE_3",((-1,2),(-1,-2)),3,"EXACT_ONE","mechanism"),
    ]
    return small,large,mechanism


def percentile(values,p):
    a=sorted(values)
    j=(len(a)-1)*p
    lo=int(j)
    hi=min(lo+1,len(a)-1)
    return a[lo]*(hi-j)+a[hi]*(j-lo)


def paired_interval(ratios):
    """Bootstrap median paired per-instance runtime ratio, 95% descriptive."""
    if not ratios:return None
    rng=random.Random(BOOTSTRAP_SEED+len(ratios))
    n=len(ratios)
    stats=[]
    for _ in range(BOOTSTRAP_REPLICATES):
        subset=[ratios[rng.randrange(n)] for __ in range(n)]
        stats.append(statistics.median(subset))
    return {
        "median":statistics.median(ratios),
        "ci95_low":percentile(stats,0.025),
        "ci95_high":percentile(stats,0.975),
        "faster_instances":sum(x<1 for x in ratios),
        "slower_instances":sum(x>1 for x in ratios),
        "equal_instances":sum(x==1 for x in ratios),
        "n":n,
        "bootstrap_resamples":BOOTSTRAP_REPLICATES,
        "bootstrap_seed":BOOTSTRAP_SEED+len(ratios),
    }


def one_case(case, *, gold=None):
    case_id,rows,n,kind,family=case
    cnf=canonical_sat_cnf(rows,n,kind)
    by_engine={}
    reps=SMALL_REPEATS if family=="frozen_small" or family=="mechanism" else LARGE_REPEATS
    for solver in SOLVERS:
        measured=defaultdict(list)
        for repeat in range(reps):
            # Deterministic rotation balances some warmup effects.
            order=ARMS if repeat%2==0 else tuple(reversed(ARMS))
            for arm in order:
                result=run_arm(rows,n,kind,solver_name=solver,arm=arm)
                if gold is not None and (result["answer"]=="SAT")!=gold:
                    raise AssertionError("original truth mismatch "+case_id)
                measured[arm].append(result)
        answers={r["answer"] for samples in measured.values() for r in samples}
        if len(answers)!=1:
            raise AssertionError("disagreement between arms "+case_id)
        raw_median=statistics.median(r["whole_pipeline_seconds"]
                                     for r in measured["raw"])
        stages={}
        for arm in ARMS:
            observations=measured[arm]
            full=statistics.median(r["whole_pipeline_seconds"] for r in observations)
            first=observations[0]
            # Structural features are stable, and adding units can never be
            # accepted without separately checking original-source entailment.
            if any(r["derived_units"]!=first["derived_units"] or
                   (r["gate"] or {}).get("admitted")!=(first["gate"] or {}).get("admitted")
                   for r in observations):
                raise AssertionError("nonreproducible gate/inference "+case_id)
            stages[arm]={
                "answer":first["answer"],
                "median_full_wall_seconds":full,
                "full_wall_samples_seconds":[r["whole_pipeline_seconds"] for r in observations],
                "median_ratio_to_raw":full/raw_median if raw_median else None,
                "median_external_only_seconds":statistics.median(
                    r["cold_external_solver_seconds"] for r in observations),
                "gate":first["gate"],
                "probe_ran":first["probe_ran"],
                "derived_units":first["derived_units"],
                "independent_unit_checks":first["independent_unit_checks"],
                "probe_clause_visits":first["probe_clause_visits"],
                "preprocessor_fallback":first["preprocessor_fallback"],
                "native_cdcl_stats":first["native_cdcl_stats"],
                "portable_unsat_proof":"NOT_PRODUCED",
            }
        by_engine[solver]=stages
    return {
        "case_id":case_id,"family":family,"kind":kind,"n":n,
        "original_clauses":len(rows),"encoded_clauses":len(cnf),
        "source_cnf_sha256":source_hash(cnf,n),
        "agreed_result":by_engine[SOLVERS[0]]["raw"]["answer"],
        "gold_reference":("EXHAUSTIVE_N<=10" if gold is not None
                          else "DETERMINISTIC_SYNTHETIC_OR_PRIOR_C023"),
        "engines":by_engine,
    }


def run():
    small,large,mechanism=fixed_controls()
    cases=[]
    for case in small+large+mechanism:
        n=case[2]
        gold=(bool(exact_truth(case[1],n,case[3]))
              if n<=10 else None)
        cases.append(one_case(case,gold=gold))
    by_family={}
    for family in sorted({case["family"] for case in cases}):
        subset=[case for case in cases if case["family"]==family]
        by_solver={}
        for solver in SOLVERS:
            interval={}
            for arm in ARMS[1:]:
                xs=[c["engines"][solver][arm]["median_ratio_to_raw"] for c in subset]
                interval[arm]=paired_interval(xs)
            admitted=sum(c["engines"][solver]["adaptive"]["gate"]["admitted"]
                         for c in subset)
            probed=sum(c["engines"][solver]["adaptive"]["probe_ran"]
                       for c in subset)
            yield_count=sum(bool(c["engines"][solver]["adaptive"]["derived_units"])
                            for c in subset)
            # Hindsight oracle is a diagnostic only; it is not an implementable
            # valid arm because it has seen test timing information.
            best_hindsight=[min(c["engines"][solver]["raw"]["median_full_wall_seconds"],
                                c["engines"][solver]["unconditional"]["median_full_wall_seconds"])
                             /c["engines"][solver]["raw"]["median_full_wall_seconds"]
                            for c in subset]
            missed=sum(
                (not c["engines"][solver]["adaptive"]["gate"]["admitted"]) and
                bool(c["engines"][solver]["unconditional"]["derived_units"])
                for c in subset)
            false_positive=sum(
                c["engines"][solver]["adaptive"]["gate"]["admitted"] and
                not bool(c["engines"][solver]["adaptive"]["derived_units"])
                for c in subset)
            by_solver[solver]={
                "gate_admissions":admitted,"gate_skips":len(subset)-admitted,
                "actual_probes":probed,"productive_admissions":yield_count,
                "admissions_with_zero_derived_units":false_positive,
                "skipped_cases_with_counterfactual_derived_units":missed,
                "ratio_intervals":interval,
                "unattainable_hindsight_best_median_ratio":
                    statistics.median(best_hindsight),
            }
        by_family[family]={"cases":len(subset),"engines":by_solver}
    return {
        "schema":"JANUS-TIME-SAT-PARTIAL-002-ADAPTIVE-GATE-EXPLORATORY-V1",
        "status":"PUBLIC_EXPLORATORY_NOT_EXTERNAL_BLIND",
        "source":{
            "github_sha":os.getenv("GITHUB_SHA","local"),
            "github_run_id":os.getenv("GITHUB_RUN_ID","local"),
            "python_version":platform.python_version(),
            "platform":platform.platform(),
            "baseline_input_suite_sha256":source_sha(fixed_suite()),
            "input_manifest_sha256":sha256(json.dumps(
                [(c["case_id"],c["source_cnf_sha256"]) for c in cases],
                sort_keys=True,separators=(",",":")).encode()).hexdigest(),
        },
        "precommitted_gate":{
            "n_at_most":32,"clauses_at_most":512,
            "no_initial_unit_clauses":True,
            "required_complementary_binary_wedge_count":1,
            "min_binary_clause_density":0.25,
            "source_only":True,
            "not_fitted_on_current_suite":True,
            "max_failed_literal_variables":8,
            "max_probe_clause_visits":7000,
            "no_probe_on_skip":True,
        },
        "four_arms":{
            "raw":"Only strong original cold CDCL",
            "feature_only":"Compute admission features, then raw CDCL, NEVER probe",
            "unconditional":"Original TIME-SAT-001 always-probe preprocessor, then same CDCL",
            "adaptive":"Same source-only features; probe only when precommitted admission holds; otherwise original cold CDCL",
        },
        "test_design":{
            "strong_solvers":["CaDiCaL195","Glucose4"],
            "public_fixed_cases":len(small),
            "synthetic_larger_cases":len(large),
            "mechanism_positive_controls":len(mechanism),
            "small_repetitions":SMALL_REPEATS,
            "large_repetitions":LARGE_REPEATS,
            "time":"Per-case total monotonic wall including features, conditional lookahead, independent implication checks, cold CDCL and SAT witness check",
            "memory":"Process-wide getrusage ru_maxrss is reported as an upper bound on whole job, NOT per variant RSS",
            "paired_CI":"2,000 paired-instance bootstrap medians on fixed public suite, descriptive, not external generalization",
            "UNSAT":"NO NEW PORTABLE UNSAT PROOFS, CaDiCaL/Glucose agreement is not proof replay",
            "Demiurge_admission":"NOT_CONNECTED; rule tested as isolated module, no live autonomous authority",
        },
        "batch_peak_rss_kib_process_wide":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "by_family":by_family,"cases":cases,
        "hard_gates":{
            "soundness":"All SAT models independently checked; derived units independently entailed via CaDiCaL",
            "baseline_cost":"Equal original CNF and cold same solver; any gate overhead charged",
            "external_blind":"NOT_DONE",
            "portable_new_UNSAT_proof":"NOT_DONE",
            "variant_peak_RSS":"NOT_DONE",
            "C023_production":"UNCHANGED",
            "P_equals_NP":"OPEN",
            "promote":"NOT_READY",
        },
    }


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    summary=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(summary,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "schema":summary["schema"],"status":summary["status"],
        "source":summary["source"],"precommitted_gate":summary["precommitted_gate"],
        "by_family":summary["by_family"],
        "selected_cases":[{
            "id":x["case_id"],"n":x["n"],"result":x["agreed_result"],
            "engine":{s:{a:{
                "time_ms":round(v["median_full_wall_seconds"]*1000,4),
                "ratio":round(v["median_ratio_to_raw"],4),
                "probed":v["probe_ran"],
                "units":len(v["derived_units"]),
            } for a,v in arms.items()} for s,arms in x["engines"].items()}
        } for x in summary["cases"] if x["family"]!="frozen_small"],
        "hard_gates":summary["hard_gates"],
    },sort_keys=True))
