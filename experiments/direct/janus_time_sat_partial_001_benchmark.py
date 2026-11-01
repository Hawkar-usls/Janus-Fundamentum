#!/usr/bin/env python3
"""TIME-SAT-PARTIAL-001: cold external CaDiCaL/Glucose control experiment.

Existing JANUS NOVIKOV-002 synthetic fixtures n=18/220/240 plus the exact
frozen 60-case SAT/Exact-One suite. No historical user CNFs or external blind
holdout are claimed. All preparation, audit, solver setup and independent SAT
candidate verification are charged to the proposal's end-to-end time.

No UNSAT portable proof is fabricated: two independent CDCL engines agree,
and MAJ3-K4 also has a previous independent serialized C023 proof outside
this experiment. The planned hidden-label independent evaluation is NOT
satisfied by this experiment.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
from hashlib import sha256
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import statistics

from janus_time_sat_partial_001 import one_run, canonical_sat_cnf, source_hash
from janus_novikov_002_benchmark import suite
from janus_tachyon_001_fair_holdout import exact_truth, fixed_suite, source_sha

SOLVERS=("cadical195","glucose4")
STAGES=("raw","forward","bidirectional")
REPEAT_SMALL=3
REPEAT_LARGE=2


def benchmark_case(case, reference=None):
    case_name,rows,n,kind,group=case
    cnf=canonical_sat_cnf(rows,n,kind)
    results={}
    for solver in SOLVERS:
        measured=defaultdict(list)
        trials=REPEAT_SMALL if group=="frozen_small" else REPEAT_LARGE
        # Rotate the order to mitigate, not eliminate, host warmup.
        for trial in range(trials):
            stage_order=STAGES if trial%2==0 else tuple(reversed(STAGES))
            for stage in stage_order:
                result=one_run(rows,n,kind,solver_name=solver,stage=stage,
                               max_visits=140000,probe_share=0.05,
                               max_goal_vars=8)
                if reference is not None:
                    actual=(result["answer"]=="SAT")
                    if actual != reference:
                        raise AssertionError(
                            f"External SAT result disagrees with independent truth {case_name}")
                measured[stage].append(result)
        for stage in STAGES:
            sample=measured[stage]
            answers=set(x["answer"] for x in sample)
            if len(answers)!=1:
                raise AssertionError("nonrepeatable CDCL answer "+case_name)
            result={
                "answer":sample[0]["answer"],
                "repetitions":len(sample),
                "full_wall_median_s":statistics.median(
                    x["full_pipeline_seconds"] for x in sample),
                "external_cdcl_only_median_s":statistics.median(
                    x["external_solver_only_seconds"] for x in sample),
                "preprocess_median_s":statistics.median(
                    x["preprocess_seconds"] for x in sample),
                "full_wall_all_s":[x["full_pipeline_seconds"] for x in sample],
                "units_added":[len(x["derived_units"]) for x in sample],
                "unit_values":[x["derived_units"] for x in sample],
                "unit_proof_audits":[x["independent_entailment_audits"] for x in sample],
                "probe_assumptions":[x["probe_assumptions"] for x in sample],
                "probe_clause_visits":[x["probe_clause_visits"] for x in sample],
                "propagation_clause_visits":[x["preprocess_clause_visits"] for x in sample],
                "quota_exhausted_any":any(x["probe_quota_exhausted"] for x in sample),
                "SAT_models_independently_verified_all":all(
                    x["model_independently_verified"] for x in sample
                    if x["answer"]=="SAT"),
                "UNSAT_certificate":"NOT_PRODUCED",
                "native_CDCL_stats":[x["CDCL_statistics"] for x in sample],
            }
            results[(solver,stage)]=result
    # Same instance same answer and same CNF source across stages, versions.
    answers={x["answer"] for x in results.values()}
    if len(answers)!=1:
        raise AssertionError("contradictory CDCL engines/augmentations on "+case_name)
    by_solver={}
    for solver in SOLVERS:
        plain=results[(solver,"raw")]["full_wall_median_s"]
        by_solver[solver]={
            stage:dict(results[(solver,stage)],
                 full_pipeline_ratio_vs_raw=(
                     results[(solver,stage)]["full_wall_median_s"]/plain
                     if plain>0 else None))
            for stage in STAGES
        }
    return {
        "id":case_name,"family":group,"n":n,"kind":kind,
        "original_rows":len(rows),"encoded_cnf_clauses":len(cnf),
        "encoded_cnf_sha256":source_hash(cnf,n),
        "reference_status":(
            "EXHAUSTIVE_REFERENCE" if reference is not None
            else "SYNTHETIC_CONSTRUCTION_OR_PREVIOUS_C023_PROOF"),
        "agreed_answer":next(iter(answers)),
        "solver_variants":by_solver,
    }


def run():
    small,larger=suite()
    # Source freeze prevents inadvertently replacing the earlier 60 tests.
    original_small=fixed_suite()
    original_hash=source_sha(original_small)
    assert len(small)==60 and len(larger)==5
    ref={}
    for c in small:
        ref[c[0]]=bool(exact_truth(c[1],c[2],c[3]))
    rows=[]
    for c in small+larger:
        rows.append(benchmark_case(c,ref.get(c[0])))
    families=sorted({r["family"] for r in rows})
    aggregate={}
    for family in families:
        family_cases=[r for r in rows if r["family"]==family]
        per_engine={}
        for solver in SOLVERS:
            data={}
            for stage in STAGES[1:]:
                ratio=[r["solver_variants"][solver][stage]
                       ["full_pipeline_ratio_vs_raw"] for r in family_cases]
                data[stage]={
                    "median_full_pipeline_ratio_vs_strong_CDCL_raw":
                        statistics.median(ratio),
                    "faster_cases":sum(x<1 for x in ratio),
                    "slower_cases":sum(x>1 for x in ratio),
                    "total_cases":len(ratio),
                    "total_derived_units":sum(
                        r["solver_variants"][solver][stage]["units_added"][0]
                        for r in family_cases),
                    "total_probe_clause_visits":sum(
                        r["solver_variants"][solver][stage]["probe_clause_visits"][0]
                        for r in family_cases),
                }
            per_engine[solver]=data
        aggregate[family]=per_engine
    return {
        "schema":"JANUS-TIME-SAT-PARTIAL-001-STRONG-CDCL-ABLATON-V1",
        "status":"RESEARCH_RESULTS_NO_EXTERNAL_HIDDEN_DATA",
        "run":{"github_sha":os.getenv("GITHUB_SHA","local"),
               "github_run_id":os.getenv("GITHUB_RUN_ID","local"),
               "runner":os.getenv("RUNNER_OS","local"),
               "platform":platform.platform(),
               "python_sat_version":importlib.metadata.version("python-sat")},
        "source":{
            "meta_registry_reference":"Hawkar-usls/janus-meta-registry/main/data/JANUS-ENTROPY-TIME-CAUSALITY-REGISTRY-SYNTHESIS-2026-11-01-v1.0.json",
            "meta_registry_main_merge_sha":"6335f51bbe57085411de36d3b34a9839cdeb3723",
            "frozen_60_suite_sha256":original_hash,
            "small_n_max":10,"large_names":[c[0] for c in larger],
            "all_inputs_source_bound_sha256":sha256(json.dumps(
                [(x["id"],x["encoded_cnf_sha256"]) for x in rows],
                separators=(",",":"),sort_keys=True).encode()).hexdigest(),
        },
        "method":{
            "solvers":["CaDiCaL 1.9.5 through PySAT","Glucose4 through PySAT"],
            "variants":[
                "cold raw external CDCL",
                "same CDCL plus forward unit propagation and independently entailed units",
                "same CDCL plus forward constraints and goal-ordered bounded failed-literal implications",
            ],
            "fair_end_to_end":"Includes formula encoding, partial-state preprocess, every derived-unit entailment check by an external CDCL, solver construction and external SAT candidate validation",
            "static_probe_quota":"5% of 140000 clause-visits plus at most one final visit",
            "preparation_probe_variables_max":8,
            "unit_implication_verifier":"Independent CaDiCaL assumption UNSAT for each source-implied unit",
            "small_repeats":REPEAT_SMALL,
            "large_repeats":REPEAT_LARGE,
            "timestamp_order":"Alternating ABBA-like stage order",
            "baseline_and_variants_same_exact_encoded_CNF":True,
            "hidden_future_answer_passed_to_solver":False,
            "unsat_certificates":"NOT PRODUCED by this benchmark",
            "rss":"NOT PER-RUN MEASURED — in-process native allocations cannot be reliably attributed to individual variants",
        },
        "aggregates":aggregate,
        "cases":rows,
        "scientific_limits":[
            "Standard failed-literal inference is classical forward-time CDCL preprocessing, not exotic physics",
            "A conforming partial assignment may still have no global model; no UNSAT from local consistency",
            "Small n<=10 truth labels independently exhaustively verified",
            "n18 MAJ3-K4 had a separately validated original C023 portable proof, not a new one here",
            "n220/240 formulas are deterministic generated controls, not the user's historical CNFs or external blind benchmark",
            "CaDiCaL/Glucose4 agreement on UNSAT is not itself an independent portable proof",
            "Three/two repeats on shared cloud hardware are insufficient to infer stable optimization",
            "No statistically preregistered external-hidden dataset, no per-case peak RSS, no signed external trust witness",
            "Production C023 unchanged, existing promotion gate NOT_READY, P vs NP open",
        ],
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    a=parser.parse_args()
    result=run()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "schema":result["schema"],"status":result["status"],
        "run":result["run"],"source":result["source"],
        "method":result["method"],
        "aggregates":result["aggregates"],
        "large_case_outcomes":[{
            "case":x["id"],"n":x["n"],"clauses":x["encoded_cnf_clauses"],
            "answer":x["agreed_answer"],
            "by_solver":{
                name:{
                    stage:{
                        "median_full_ms":round(a["full_wall_median_s"]*1000,4),
                        "raw_ratio":round(a["full_pipeline_ratio_vs_raw"],4),
                        "units":a["units_added"][0],
                        "probe_visits":a["probe_clause_visits"][0],
                    } for stage,a in x["solver_variants"][name].items()
                } for name in SOLVERS
            }
        } for x in result["cases"] if x["family"]!="frozen_small"],
    },sort_keys=True))
if __name__=="__main__":
    main()
