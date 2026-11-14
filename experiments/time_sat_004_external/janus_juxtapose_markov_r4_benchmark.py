#!/usr/bin/env python3
"""Markov-chain x JUXTAPOSE, exact-proof SAT/XOR source search: R4.

Pure Python, standard library only. Markov memory is a first-order transition
table P(EXACT_rank_hit | PREVIOUS_VERIFIED_STATE, CURRENT_SOURCE_FEATURE_CLASS),
learned from 90 prior source-proved training probes per seed.
The variable ordering is only a suggestion; each discovered XOR is independently
replayed from original CNF by the existing resolution DAG proof checker.

Four entirely new, source-SHA-precommitted n15 OOD cohorts. Same admin
synthetic only. No SAT end-to-end solver, C023 changes, external blind claim,
P=NP or unverified UNSAT claim. Negative/unknown/censored are retained.
"""
from __future__ import annotations
from collections import defaultdict
from hashlib import sha256
import argparse
import json
import math
import random
import subprocess
import sys
from pathlib import Path
from time import perf_counter

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import janus_juxtapose67_sat_xor as exact
import janus_juxtapose_markov_r4_sources as new_sources
from janus_time_sat_004d4d_paged_support import extract_paged_mixed_xor
from time_sat_004d9b_up_cleanroom_baseline import baseline_case

PROTOCOL_BLOB="2801a70000022a76e2e0218a6172e4476f9c8d40"
MANIFEST_BLOB="be93c8ca88f4a0b58274f9f7f1807fefa43311ac"
PROTOCOL=HERE/"JUXTAPOSE_MARKOV_R4_FROZEN_PROTOCOL_20261115.json"
MANIFEST=HERE/"JUXTAPOSE_MARKOV_R4_ORIGINAL_SHA_MANIFEST_20261115.json"
SEEDS=(2026111551,2026111552,2026111553,2026111554)
TRAIN=45
HOLDOUT=30
SCHEMA="JANUS-JUXTAPOSE-MARKOV-R4-EXACT-SAT-XOR-CROSS-CONTROL-V1"
ARMS=("JUXTAPOSE_MARKOV_HYBRID","JUXTAPOSE_ORIGINAL",
      "MARKOV_ONLY","STATIC_FIRST_HIT","RANDOM_FIRST_HIT")

def git_blob(path):
    return subprocess.run(["git","hash-object",str(path)],capture_output=True,
                          check=True,text=True).stdout.strip()

def freeze():
    if git_blob(PROTOCOL)!=PROTOCOL_BLOB or git_blob(MANIFEST)!=MANIFEST_BLOB:
        raise AssertionError("PREREGISTRATION_SOURCE_SHA_MISMATCH")
    protocol=json.loads(PROTOCOL.read_text())
    locked=json.loads(MANIFEST.read_text())
    if (protocol["schema"]!="JANUS-JUXTAPOSE-MARKOV-R4-PROSPECTIVE-INTERNAL-STATISTICS-V1"
        or protocol["preregistered_seeds"]!=list(SEEDS)
        or protocol["train_cases"]!=TRAIN or protocol["holdout_per_seed"]!=HOLDOUT
        or protocol["holdout_source_count"]!=120):
        raise AssertionError("CHANGED_PREDECLARED_R4_TEST")
    if locked!=new_sources.manifest():
        raise AssertionError("NEW_CNF_SOURCE_SHA_DRIFT_AFTER_PRECOMMIT")
    return {(i["seed"],i["slot"]):i for i in locked["items"]}

def source_context(rows,n):
    source=extract_paged_mixed_xor(rows,n)
    if source["status"]!="SOURCE_PARTITION_VERIFIED":
        raise AssertionError("SOURCE_XOR_PARTITION_UNVERIFIED")
    known={(tuple(eq["variables"]),eq["rhs"]) for eq in source["equations"]}
    up=baseline_case(n,rows)
    if up["status"]!="UP_AND_COMPLETE_SIGNMASK_XOR_BASELINE_READY":
        raise AssertionError("ORIGINAL_UP_BASELINE_UNVERIFIED")
    up_keys={(tuple(x["variables"]),x["rhs"]) for x in up["baseline_equations"]}
    return known,up_keys

def verified_pivot(rows,n,pivot,known,up):
    f=exact.feature(rows,pivot)
    if any(len(clause)>4 for _,clause in f["pos"]+f["neg"]):
        return {"pivot":pivot,"status":"ABSTAIN_ORIGINAL_WIDTH",
                "rank_delta_over_UP":0,"pair_work":f["pair_work"],
                "new_keys":[]}
    result=exact.exact_probe(rows,n,pivot,known,up)
    if result["status"] not in (
        "EXACT_SOURCE_PROOF_REPLAY_PASS","ABSTAIN_INELIGIBLE_PIVOT",
        "ABSTAIN_RESOLVENT_BUDGET"):
        raise AssertionError("UNKNOWN_SOURCE_PROOF_STATUS:"+result["status"])
    return result

def pair_band(pairs):
    if pairs==0:return "0"
    if pairs<=2:return "1-2"
    if pairs<=6:return "3-6"
    if pairs<=16:return "7-16"
    return "17+"

def candidate_class(f):
    count_4=sum(len(c)==4 for _,c in f["pos"]+f["neg"])
    count_3=sum(len(c)==3 for _,c in f["pos"]+f["neg"])
    return "|".join([
        "eligible" if f["eligible"] else "ineligible",
        pair_band(f["pair_work"]),
        "width4" if count_4 else "no4",
        "width3" if count_3 else "no3",
        "balanced" if abs(len(f["pos"])-len(f["neg"]))<=1 else "imbalanced"
    ])

def verified_state(result):
    if result["status"]!="EXACT_SOURCE_PROOF_REPLAY_PASS":
        return "ABSTAIN:"+pair_band(result["pair_work"])
    if result["rank_delta_over_UP"]>0:
        return "HIT:"+pair_band(result["pair_work"])
    return "MISS:"+pair_band(result["pair_work"])

class MarkovMemory:
    """First-order, count-only; no transformer or pretrained network."""
    def __init__(self):
        self.transitions=defaultdict(lambda:[0,0])
        self.classes=defaultdict(lambda:[0,0])
    def observe(self,prev,f,exact_result):
        label=int(exact_result["rank_delta_over_UP"]>0)
        key=(prev,candidate_class(f))
        self.transitions[key][0]+=label
        self.transitions[key][1]+=1
        self.classes[candidate_class(f)][0]+=label
        self.classes[candidate_class(f)][1]+=1
    def predict(self,prev,f):
        key=(prev,candidate_class(f))
        h,n=self.transitions.get(key,(0,0))
        prior_h,prior_n=self.classes.get(candidate_class(f),(0,0))
        # Stronger global fallback on sparse transition states, no future labels.
        local=(h+1)/(n+3)
        global_p=(prior_h+1)/(prior_n+3)
        return (n*local+4*global_p)/(n+4)
    def snapshot(self,seed,train_shas):
        out={
          "schema":"JANUS-MARKOV-FIRST-ORDER-EXACT-RECEIPT-MEMORY-V1",
          "seed":seed,"training_source_SHA256":train_shas,
          "training_exact_receipts":sum(x[1] for x in self.transitions.values()),
          "transition_counts":[{"previous_verified_state":p,"next_source_class":c,
                                "positive":x[0],"observations":x[1]}
                               for (p,c),x in sorted(self.transitions.items())],
          "class_counts":[{"class":c,"positive":x[0],"observations":x[1]}
                          for c,x in sorted(self.classes.items())],
          "no_holdout_updates":True,
          "no_transformer_weights":True,
          "source_proof_authority":"EXACT_ORIGINAL_CNFS_AND_RESOLUTION_DAG_REPLAY",
          "production_activation":"FORBIDDEN"
        }
        return out,sha256(json.dumps(out,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def sort_for_arm(arm,remaining,features,experience,memory,previous):
    if arm=="JUXTAPOSE_ORIGINAL":
        return sorted(remaining,key=lambda p:exact.trained_rank(features[p-1],experience),reverse=True)[0]
    if arm=="STATIC_FIRST_HIT":return min(remaining)
    # RANDOM_FIRST_HIT has its own frozen order; never pass here.
    def score(p):
        f=features[p-1]
        p_m=memory.predict(previous,f)
        if arm=="MARKOV_ONLY":
            s=p_m
        elif arm=="JUXTAPOSE_MARKOV_HYBRID":
            k=exact.model_key(f)
            h,n=experience.get(k,(0,0))
            p_h=(h+1)/(n+2)
            s=(2*p_m+p_h)/3
        else:raise AssertionError("UNKNOWN_ARM")
        # Cost-aware, deterministic. No numeric pivot ID in learning features.
        numeric=int(round(1_000_000*s/math.sqrt(1+f["pair_work"])))
        return (int(f["eligible"]),numeric,f["priority"])
    return max(remaining,key=score)

def run_arm(arm,rows,n,seed,slot,features,experience,memory,known,up):
    started=perf_counter()
    if arm=="RANDOM_FIRST_HIT":
        frozen_order=list(range(1,n+1))
        random.Random(seed^(slot*1031+10007)).shuffle(frozen_order)
    else:
        frozen_order=[]
    pending=set(range(1,n+1))
    prior="START"
    steps=[]
    first_proof=None
    while pending:
        pivot=(frozen_order[len(steps)] if arm=="RANDOM_FIRST_HIT"
               else sort_for_arm(arm,pending,features,experience,memory,prior))
        pending.remove(pivot)
        result=verified_pivot(rows,n,pivot,known,up)
        steps.append({"pivot":pivot,"status":result["status"],
                      "pair_work":result["pair_work"],
                      "verified_independent_rank_gain":result["rank_delta_over_UP"]})
        if result["rank_delta_over_UP"]>0:
            if result["status"]!="EXACT_SOURCE_PROOF_REPLAY_PASS":
                raise AssertionError("UNVERIFIED_MARKOV_HIT")
            first_proof=result
            break
        prior=verified_state(result)
    return {
      "source_exact_first_hit_verified":int(first_proof is not None),
      "proof_delta_rank":first_proof["rank_delta_over_UP"] if first_proof else 0,
      "exact_probes":len(steps),
      "symbolic_parent_pair_work":sum(s["pair_work"] for s in steps),
      "source_replay_wall_seconds":perf_counter()-started,
      "all_attempt_statuses":steps,
      "complete_XOR_inventory":"NOT_CLAIMED"
    }

def run_seed(seed,freeze_map):
    old_seed=exact.SEED
    exact.SEED=seed
    try:
        memory=MarkovMemory()
        experience={}
        training_shas=[]
        train_pairs=0
        train_probes=0
        train_time=0.0
        train_context_time=0.0
        for i in range(TRAIN):
            source=exact.source_case(i)
            rows,n=source["rows"],source["n"]
            start=perf_counter()
            known,up=source_context(rows,n)
            features=[exact.feature(rows,p) for p in range(1,n+1)]
            train_context_time+=perf_counter()-start
            # Identical two labels for both JUXTAPOSE and first-order Markov;
            # scores predicted before observing the current proof.
            choices=sorted(range(1,n+1),
                    key=lambda p:exact.trained_rank(features[p-1],experience),reverse=True)
            first=choices[0]
            others=[p for p in range(1,n+1) if p!=first]
            second=others[random.Random(seed+i*4001).randrange(len(others))]
            previous="START"
            for pivot in (first,second):
                t=perf_counter()
                val=verified_pivot(rows,n,pivot,known,up)
                train_time+=perf_counter()-t
                if val["status"]=="ABSTAIN_ORIGINAL_WIDTH":
                    raise AssertionError("INVALID_TRAIN_SOURCE_PARENT")
                label=int(val["rank_delta_over_UP"]>0)
                f=features[pivot-1]
                memory.observe(previous,f,val)
                key=exact.model_key(f)
                h,count=experience.get(key,(0,0))
                experience[key]=(h+label,count+1)
                previous=verified_state(val)
                train_probes+=1
                train_pairs+=val["pair_work"]
            training_shas.append(source["original_source_logical_sha256"])
        if train_probes!=90:
            raise AssertionError("MARKOV_TRAIN_LABEL_BUDGET_VIOLATION")
        model,model_sha=memory.snapshot(seed,training_shas)
        if model["training_exact_receipts"]!=90:
            raise AssertionError("MARKOV_TRANSITION_COUNT_INCORRECT")
        learned_memory_size=len(model["transition_counts"])
        checkpoint_guard=model_sha
        episodes=[]
        ood_shas=[]
        input_context_time=0.0
        for slot in range(HOLDOUT):
            source=new_sources.generate(seed,slot)
            prereg=freeze_map[(seed,slot)]
            if (source["source_logical_sha256"]!=prereg["source_logical_sha256"]
                or source["family"]!=prereg["family"]):
                raise AssertionError("PRECOMMITTED_ORIGINAL_CNFS_NOT_IDENTICAL")
            rows,n=source["rows"],source["n"]
            t=perf_counter()
            known,up=source_context(rows,n)
            features=[exact.feature(rows,p) for p in range(1,n+1)]
            input_context_time+=perf_counter()-t
            outcomes={arm:run_arm(arm,rows,n,seed,slot,features,experience,memory,known,up)
                      for arm in ARMS}
            if len({v["source_exact_first_hit_verified"] for v in outcomes.values()})!=1:
                raise AssertionError("MARKOV_CHANGED_PROOF_EXISTENCE_COVERAGE")
            episodes.append({"slot":slot,"source_SHA256":source["source_logical_sha256"],
                 "family_for_reporting_only":source["family"],
                 "original_SAT_model_replayed":True,
                 "all_arms":outcomes,
                 "no_holdout_feedback_to_transition_table":True})
            ood_shas.append(source["source_logical_sha256"])
        if set(ood_shas).intersection(training_shas):
            raise AssertionError("HOLDOUT_SOURCE_LEAKAGE")
        _,unchanged_sha=memory.snapshot(seed,training_shas)
        if unchanged_sha!=checkpoint_guard:
            raise AssertionError("HOLDOUT_MODEL_MUTATION_DETECTED")
        aggregates={}
        for arm in ARMS:
            stats=[r["all_arms"][arm] for r in episodes]
            trained=arm in ("JUXTAPOSE_MARKOV_HYBRID","JUXTAPOSE_ORIGINAL","MARKOV_ONLY")
            pairs=sum(x["symbolic_parent_pair_work"] for x in stats)
            probes=sum(x["exact_probes"] for x in stats)
            seconds=sum(x["source_replay_wall_seconds"] for x in stats)
            aggregates[arm]={
              "holdout_exact_probes":probes,
              "holdout_pair_work":pairs,
              "holdout_verified_source_hit_cases":sum(x["source_exact_first_hit_verified"] for x in stats),
              "train_exact_probes_charged":train_probes if trained else 0,
              "train_pair_work_charged":train_pairs if trained else 0,
              "total_amortized_exact_probes":probes+(train_probes if trained else 0),
              "total_amortized_pair_work":pairs+(train_pairs if trained else 0),
              "holdout_exact_replay_wall_seconds":seconds,
              "amortized_train_and_holdout_exact_replay_wall_seconds":seconds+(train_time if trained else 0),
              "source_preprocessing_shared_seconds":input_context_time,
              "claim_full_SAT_solver_speedup":False
            }
        return {
          "seed":seed,"original_source_sha_manifest_blob":MANIFEST_BLOB,
          "training_source_shas":training_shas,
          "holdout_source_shas":ood_shas,
          "training_exact_label_count":train_probes,
          "training_symbolic_pair_work":train_pairs,
          "training_exact_replay_wall_seconds":train_time,
          "training_source_preprocessing_wall_seconds":train_context_time,
          "holdout_shared_source_preprocessing_wall_seconds":input_context_time,
          "markov_first_order_memory_checkpoint_sha256":model_sha,
          "markov_memory":model,
          "heldout_predictions_update_global_model":False,
          "markov_transitions_trained":learned_memory_size,
          "summaries":aggregates,
          "all_source_proof_receipts":episodes
        }
    finally:
        exact.SEED=old_seed

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--memory-dir",type=Path)
    args=p.parse_args()
    cohort=freeze()
    start=perf_counter()
    reports=[run_seed(s,cohort) for s in SEEDS]
    all_ood=[sha for r in reports for sha in r["holdout_source_shas"]]
    if len(all_ood)!=len(set(all_ood)) or len(all_ood)!=120:
        raise AssertionError("R4_PRECOMMITTED_ORIGINAL_CNF_DUPLICATE")
    assert set(all_ood)=={entry["source_logical_sha256"] for entry in cohort.values()}
    if args.memory_dir:
        args.memory_dir.mkdir(parents=True,exist_ok=True)
        for r in reports:
            (args.memory_dir/f"JUXTAPOSE_MARKOV_{r['seed']}.json").write_text(
                json.dumps(r["markov_memory"],sort_keys=True,indent=2)+"\n")
    result={
        "schema":SCHEMA,"frozen_protocol_blob":PROTOCOL_BLOB,
        "frozen_original_CNF_source_manifest_blob":MANIFEST_BLOB,
        "predeclared_seeds":list(SEEDS),"new_ood_cases":len(all_ood),
        "algorithm":"FIRST_ORDER_COUNT_MARKOV_OVER_VERIFIED_PIVOT_STATES_PLUS_JUXTAPOSE",
        "all_methods_math_source_replay":"YES",
        "all_methods_early_first_proof_only":"YES",
        "heldout_labels_never_used_to_update_models":"YES",
        "no_transformer":"YES",
        "external_blind_research":"NOT_DONE",
        "end_to_end_SAT_solver_time":"NOT_MEASURED",
        "production_C023":"UNCHANGED",
        "R6":"R6_FROZEN_SCIENCE_GATE_NOT_PASSED",
        "wall_total_experiment_seconds":perf_counter()-start,
        "reports":reports
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"status":"MARKOV_R4_PREDECLARED_120_CNF_COHORT_EVALUATED",
       "per_seed":[{"seed":r["seed"],
                    "markov_memory_sha":r["markov_first_order_memory_checkpoint_sha256"],
                    "transitions":r["markov_transitions_trained"],
                    "summaries":{k:{"hits":v["holdout_verified_source_hit_cases"],
                      "holdout_checks":v["holdout_exact_probes"],
                      "amortized_checks":v["total_amortized_exact_probes"],
                      "pair_work":v["total_amortized_pair_work"],
                      "measured_replay_seconds":round(v["amortized_train_and_holdout_exact_replay_wall_seconds"],5)}
                                 for k,v in r["summaries"].items()}}
                   for r in reports]},sort_keys=True))
if __name__=="__main__":
    main()
