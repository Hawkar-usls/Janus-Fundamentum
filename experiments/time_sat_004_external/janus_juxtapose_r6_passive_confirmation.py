#!/usr/bin/env python3
"""JUXTAPOSE R6: fresh prospective fair end-to-end bounded proof-search test.

The candidate PASSSIVE_JUXTAPOSE_HISTORY is IDENTICAL to the R5 implementation;
its parameter-free passive memory learns only already necessary exact-proven
search attempts; no new model/tuning was selected after inspecting R5 outcomes.

240 original source CNF SHA digests frozen in a separate source-only CI, plus
the whole 45-formula natural search learning cost per seed. Six algorithms
tested on identical input with deterministic randomized algorithm execution
order to reduce time-of-run bias. This is not full SAT solver timing and not an
independently custodial blind dataset.
"""
from __future__ import annotations
import argparse
import json
import random
from pathlib import Path
import subprocess
import sys
from time import perf_counter

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import janus_juxtapose67_sat_xor as exact
import janus_juxtapose_r5_passive_benchmark as r5
import janus_juxtapose_r6_sources as future

PROTOCOL_FILE=HERE/"JUXTAPOSE_R6_PASSIVE_PROSPECTIVE_PROTOCOL_20261115.json"
PROTOCOL_GIT_BLOB="309c7b255e544024148ae13165a989cd9aaa7aea"
SOURCE_MANIFEST_FILE=HERE/"JUXTAPOSE_R6_FROZEN_240_SOURCE_MANIFEST_20261115.json"
SOURCE_MANIFEST_BLOB="a4a8f8c00046e5bdcea38ae7a19c416c1ca0412f"
SEEDS=(2026111661,2026111662,2026111663,2026111664)
TRAIN=45
HOLDOUT=60
ARMS=tuple(r5.ARMS)
MAIN="PASSIVE_JUXTAPOSE_HISTORY"
STATICS=("STATIC_NUMERIC","COST_GEOMETRY_NO_MEMORY")
SCHEMA="JANUS-JUXTAPOSE-R6-PREREGISTERED-PASSIVE-AMORTIZED-SAT-PROOF-RESULT-V1"

def git_blob(path):
    return subprocess.run(["git","hash-object",str(path)],capture_output=True,
                          text=True,check=True).stdout.strip()

def locked_sources():
    if (git_blob(PROTOCOL_FILE)!=PROTOCOL_GIT_BLOB
        or git_blob(SOURCE_MANIFEST_FILE)!=SOURCE_MANIFEST_BLOB):
        raise AssertionError("FROZEN_PROTOCOL_OR_ORIGINAL_SHA_MANIFEST_MISMATCH")
    p=json.loads(PROTOCOL_FILE.read_text())
    if (p["schema"]!="JANUS-JUXTAPOSE-R6-PASSIVE-SELF-AMORTIZED-FROZEN-20261115-V1"
        or p["heldout_seeds"]!=list(SEEDS)
        or p["training_sources_per_seed"]!=TRAIN
        or p["heldout_sources_per_seed"]!=HOLDOUT
        or p["preregistered_controls"]!=list(ARMS)
        or p["statistical_primary"].find("PASSIVE_JUXTAPOSE_HISTORY")<0):
        raise AssertionError("FROZEN_ACCEPTANCE_CHANGED_AFTER_PREREG")
    lock=json.loads(SOURCE_MANIFEST_FILE.read_text())
    if lock!=future.manifest() or lock["source_count"]!=240:
        raise AssertionError("SYNTHETIC_ORIGINAL_SOURCE_SHA_DRIFT")
    return {(x["seed"],x["slot"]):x for x in lock["items"]}

def one_seed(seed,lock):
    old_seed=exact.SEED
    exact.SEED=seed
    try:
        states={k:r5.State(k) for k in ARMS}
        full_search_wall={k:0.0 for k in ARMS}
        snapshot_wall={k:0.0 for k in ARMS}
        source_prep_wall=0.0
        original_gen_wall=0.0
        audit=[]
        freeze_snapshots=None
        for i in range(TRAIN+HOLDOUT):
            phase="TRAIN" if i<TRAIN else "FROZEN_HOLDOUT"
            t=perf_counter()
            if phase=="TRAIN":
                source=exact.source_case(i)
            else:
                slot=i-TRAIN
                source=future.source(seed,slot)
                fixed=lock[(seed,slot)]
                if (source["source_logical_sha256"]!=fixed["source_logical_sha256"]
                    or source["family"]!=fixed["family"] or source["n"]!=fixed["n"]):
                    raise AssertionError("UNREGISTERED_FUTURE_SOURCE")
            original_gen_wall+=perf_counter()-t
            prep_start=perf_counter()
            known,up=r5.source_context(source["rows"],source["n"])
            features=[exact.feature(source["rows"],p)
                      for p in range(1,source["n"]+1)]
            prep_seconds=perf_counter()-prep_start
            source_prep_wall+=prep_seconds
            randomized_order=list(ARMS)
            random.Random(seed*17 + i*100003).shuffle(randomized_order)
            outcomes={}
            for arm in randomized_order:
                t=perf_counter()
                evidence=r5.solve_source(
                    states[arm],seed,i,phase,source,(known,up,features))
                full_search_wall[arm]+=perf_counter()-t
                outcomes[arm]={
                    "first_verified_hit":evidence["first_source_entailed_positive_hit"],
                    "root_exact_probes":evidence["natural_search_probes"],
                    "extra_exact_training_probes":evidence["additional_training_probes_charged"],
                    "source_parent_pair_work":
                        evidence["natural_pairwork"]+evidence["extra_training_pairwork"],
                    "all_source_bound_proof_attempts":evidence["all_root_proof_attempts"],
                    "all_extra_train_proof_attempts":evidence["all_extra_train_proof_attempts"]
                }
            if len({x["first_verified_hit"] for x in outcomes.values()})!=1:
                raise AssertionError("EXACT_MATH_COVERAGE_CHANGED_BY_MEMORY")
            if i==TRAIN-1:
                freeze_snapshots={arm:states[arm].checkpoint()[1] for arm in ARMS}
            if phase=="FROZEN_HOLDOUT":
                if freeze_snapshots is None:
                    raise AssertionError("NO_PRECOMMITTED_LEARNED_MEMORY")
                if any(states[arm].checkpoint()[1]!=freeze_snapshots[arm] for arm in ARMS):
                    raise AssertionError("FUTURE_OUTCOME_USED_FOR_TRAINING")
            audit.append({
                "phase":phase,"source_original_sha256":source["source_logical_sha256"],
                "family_reporting_only":source["family"],
                "unmodified_source_SAT_model_verified":True,
                "one_proof_exists_not_complete_XOR_inventory":True,
                "shared_preprocess_elapsed_seconds":prep_seconds,
                "source_generation_elapsed_seconds":perf_counter()-t if False else None,
                "randomized_arm_order_seeded_without_outcome":randomized_order,
                "all_arms":outcomes
            })
        result={}
        checkpoints={}
        for arm in ARMS:
            state=states[arm]
            t=perf_counter()
            memory,memsha=state.checkpoint()
            serialized=json.dumps(memory,sort_keys=True,separators=(",",":"))
            mem_bytes=len(serialized.encode())
            snapshot_wall[arm]+=perf_counter()-t
            if memsha!=freeze_snapshots[arm]:
                raise AssertionError("MUTATED_MEMORY_DURING_HOLDOUT")
            if arm.startswith("PASSIVE_") and state.extra_training_probes:
                raise AssertionError("PASSIVE_MODEL_PAID_EXTRA_LABELS")
            checkpoints[arm]={"sha256":memsha,"memory":memory,"bytes_json_compact":mem_bytes}
            result[arm]={
                "train_exact_probes":state.train_probes,
                "holdout_exact_probes":state.test_probes,
                "train_extra_probes":state.extra_training_probes,
                "total_lifetime_exact_probes":state.train_probes+state.test_probes,
                "train_source_parent_pair_work":state.train_pairwork,
                "holdout_source_parent_pair_work":state.test_pairwork,
                "total_lifetime_source_parent_pair_work":state.train_pairwork+state.test_pairwork,
                "train_math_hit_cases":state.train_positive,
                "holdout_math_hit_cases":state.test_positive,
                "measured_lifetime_search_update_wall_seconds":full_search_wall[arm],
                "measured_lifetime_memory_snapshot_seconds":snapshot_wall[arm],
                "measured_common_original_source_preprocess_seconds":source_prep_wall,
                "measured_total_bounded_search_wall_seconds_including_shared_preprocess":
                    full_search_wall[arm]+snapshot_wall[arm]+source_prep_wall,
                "measured_synthetic_source_generation_wall_seconds_shared":original_gen_wall,
                "memory_bytes":mem_bytes,"memory_sha256":memsha
            }
        heldout_shas=[x["source_original_sha256"] for x in audit if x["phase"]=="FROZEN_HOLDOUT"]
        train_shas=[x["source_original_sha256"] for x in audit if x["phase"]=="TRAIN"]
        if len(heldout_shas)!=HOLDOUT or len(set(heldout_shas))!=HOLDOUT:
            raise AssertionError("REUSED_HOLDOUT")
        if set(heldout_shas)&set(train_shas):
            raise AssertionError("TRAIN_HOLDOUT_ORIGINAL_OVERLAP")
        if len({result[arm]["holdout_math_hit_cases"] for arm in ARMS})!=1:
            raise AssertionError("MATH_HIT_COVERAGE_NOT_IDENTICAL")
        return {"seed":seed,"frozen_memory_SHA_before_holdout":freeze_snapshots,
                "original_source_shas_training":train_shas,
                "original_source_shas_holdout":heldout_shas,
                "statistics":result,
                "memory_checkpoints":checkpoints,
                "per_case":audit}
    finally:
        exact.SEED=old_seed

def science_gate(reports):
    primary=MAIN
    metrics={}
    for arm in ARMS:
        metrics[arm]={
            "total_exact_probes":sum(r["statistics"][arm]["total_lifetime_exact_probes"] for r in reports),
            "total_pair_work":sum(r["statistics"][arm]["total_lifetime_source_parent_pair_work"] for r in reports),
            "total_inclusive_bounded_search_wall_seconds":sum(
                r["statistics"][arm]["measured_total_bounded_search_wall_seconds_including_shared_preprocess"]
                for r in reports),
            "original_sha_bound_hit_cases":sum(r["statistics"][arm]["holdout_math_hit_cases"] for r in reports)
        }
    p=metrics[primary]
    s=metrics["STATIC_NUMERIC"]
    geom=metrics["COST_GEOMETRY_NO_MEMORY"]
    lower_wall_5pct=all(
        p["total_inclusive_bounded_search_wall_seconds"]<=0.95*metrics[arm]["total_inclusive_bounded_search_wall_seconds"]
        for arm in STATICS)
    cohort_wins=sum(
        all(r["statistics"][primary]["measured_total_bounded_search_wall_seconds_including_shared_preprocess"]
            <r["statistics"][arm]["measured_total_bounded_search_wall_seconds_including_shared_preprocess"]
            for arm in STATICS)
        for r in reports)
    no_big_regret=all(
        r["statistics"][primary]["measured_total_bounded_search_wall_seconds_including_shared_preprocess"]
        <=1.05*r["statistics"][arm]["measured_total_bounded_search_wall_seconds_including_shared_preprocess"]
        for r in reports for arm in STATICS)
    no_pair_regret=p["total_pair_work"]<=s["total_pair_work"]
    math_equal=len({v["original_sha_bound_hit_cases"] for v in metrics.values()})==1
    gate=(lower_wall_5pct and cohort_wins>=3 and no_big_regret
          and no_pair_regret and math_equal)
    return {"status":"PASS_INTERNAL_PROSPECTIVE" if gate else "FAIL_INTERNAL_PROSPECTIVE",
        "gates":{"aggregate_min_5percent_wall_speedup_vs_both_untrained":lower_wall_5pct,
                "wins_against_both_untrained_at_least_3of4":cohort_wins>=3,
                "all_cohorts_no_more_than_5percent_wall_regret":no_big_regret,
                "aggregate_pair_work_no_regret_vs_static":no_pair_regret,
                "every_original_CNF_same_proof_positive_coverage":math_equal},
        "per_cohort_both_untrained_wall_win_count":cohort_wins,
        "metrics":metrics,"external_science_validation":"OPEN"}

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--out",type=Path,required=True)
    a.add_argument("--checkpoint-dir",type=Path)
    args=a.parse_args()
    manifest=locked_sources()
    reports=[one_seed(seed,manifest) for seed in SEEDS]
    all_sources=[h for r in reports for h in r["original_source_shas_holdout"]]
    if len(all_sources)!=len(set(all_sources))!=240:
        raise AssertionError("UNEXPECTED_HOLDOUT_SOURCE_SHA_REUSE")
    if set(all_sources)!={x["source_logical_sha256"] for x in manifest.values()}:
        raise AssertionError("FROZEN_SOURCE_MANIFEST_NOT_FULLY_CONSUMED")
    summary=science_gate(reports)
    if args.checkpoint_dir:
        args.checkpoint_dir.mkdir(parents=True,exist_ok=True)
        for r in reports:
            for arm,ck in r["memory_checkpoints"].items():
                (args.checkpoint_dir/f"{r['seed']}_{arm}.json").write_text(
                    json.dumps(ck["memory"],sort_keys=True,indent=2)+"\n")
    payload={
        "schema":SCHEMA,"protocol_blob":PROTOCOL_GIT_BLOB,
        "precommitted_original_CNF_manifest_blob":SOURCE_MANIFEST_BLOB,
        "source_only_provenance":"GitHub Actions 43653443929 before any R6 evaluation",
        "candidate_is_original_passive_JUXTAPOSE_from_R5":True,
        "unseen_original_CNF_sha_count":len(all_sources),
        "seeds":list(SEEDS),"train_cases_per_seed":TRAIN,
        "holdout_cases_per_seed":HOLDOUT,
        "scientific_gate":summary,
        "no_learning_during_holdout":True,
        "no_additional_passive_training_exact_probes":True,
        "no_neural_weights_or_markov":True,
        "full_SAT_solver_walls":"NOT_MEASURED",
        "external_independent_validation":"NOT_PERFORMED",
        "frozen_TIME_SAT_R6":"R6_FROZEN_SCIENCE_GATE_NOT_PASSED",
        "production_C023":"UNCHANGED",
        "reports":reports
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(payload,sort_keys=True,indent=2)+"\n")
    print(json.dumps({
      "status":"R6_PASSIVE_MEMORY_PROSPECTIVE_EVALUATION_COMPLETE",
      "science_gate":summary,
      "all_source_sha_unique":True,
      "per_seed":[{"seed":r["seed"],
          "passive_checks":r["statistics"][MAIN]["total_lifetime_exact_probes"],
          "static_checks":r["statistics"]["STATIC_NUMERIC"]["total_lifetime_exact_probes"],
          "passive_wall":round(r["statistics"][MAIN]["measured_total_bounded_search_wall_seconds_including_shared_preprocess"],6),
          "static_wall":round(r["statistics"]["STATIC_NUMERIC"]["measured_total_bounded_search_wall_seconds_including_shared_preprocess"],6),
          "passive_model_SHA":r["statistics"][MAIN]["memory_sha256"]}
         for r in reports]},sort_keys=True))
if __name__=="__main__":
    main()
