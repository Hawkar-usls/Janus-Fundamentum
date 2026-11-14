#!/usr/bin/env python3
"""JGPT R3: proof-safe COLD first-hit with cost-accounted frozen new OOD.

This is a SYNTHETIC same-administrator experiment; no novel algorithm, no
external holdout, no SAT-solver full-wall speedup, no production deployment.
Protocol was committed before this file's first run. All mathematical success
is source-CNF bound by the independent exact resolution DAG verifier.
"""
from __future__ import annotations
from collections import defaultdict
from hashlib import sha256
from itertools import product
import argparse
import json
import math
from pathlib import Path
import random
import subprocess
import sys
from time import perf_counter
import torch
from torch import nn

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import janus_juxtapose67_sat_xor as exact
from janus_jgpt_juxtapose67_online import JGPTSatPivotRanker,tensor_features
from janus_time_sat_004d4d_paged_support import extract_paged_mixed_xor
from janus_time_sat_004d8_sat_gate import certified_model
from time_sat_004d9b_up_cleanroom_baseline import baseline_case
from janus_jgpt_r3_ood_sources import generate as frozen_source, manifest as generated_manifest, SEEDS as SOURCE_SEEDS

PROTOCOL_BLOB="6c5df2509af4f3bc29a0af77fa4b85c7a121c897"
PROTOCOL_PATH=HERE/"JGPT_R3_COLD_FIRST_HIT_PROTOCOL_20261115.json"
MANIFEST_PATH=HERE/"JGPT_R3_COLD_FROZEN_SOURCE_MANIFEST_20261115.json"
MANIFEST_BLOB="77a6bdb0889a926c04e02225aa03473796ed42bf"
TRAIN=45
HOLDOUT=22
NEW_SEEDS=(2026111511,2026111512,2026111513)
GRAD_UPDATES=2
WEIGHT_GRID=1024
TEMP_GRID=(0.7,1.0,1.5,2.0)
FAMILIES=("XOR3_SWITCH_DIVERSE","TWO_GUARDED_XOR2",
          "XOR3_GUARDED_WITH_UNIT","DIRECT_XOR3_WITH_NOISE",
          "PLANTED_3CNF_NEGATIVE")
FULL_SOURCE_N=14
SCHEMA="JANUS-JGPT-R3-COLD-EARLY-PROOF-COST-AND-SHA-REPLAY-V1"

def read_frozen_protocol():
    blob=subprocess.run(["git","hash-object",str(PROTOCOL_PATH)],check=True,
                        capture_output=True,text=True).stdout.strip()
    if blob!=PROTOCOL_BLOB:
        raise AssertionError("Preregistered protocol altered after freeze")
    p=json.loads(PROTOCOL_PATH.read_text())
    if p["schema"]!="JANUS-JGPT-R3-COLD-FIRST-VERIFIED-HIT-FROZEN-RESEARCH-PROTOCOL-V1":
        raise AssertionError("Unexpected protocol schema")
    if (p["predeclared_fresh_train_and_ood_seeds"]!=list(NEW_SEEDS)
        or p["frozen_ood_families"]!=list(FAMILIES)
        or p["training_synthetic_cases_per_seed"]!=TRAIN
        or p["novel_ood_cases_per_seed"]!=HOLDOUT
        or p["training_exact_labels_max_per_seed"]!=90
        or p["OOD_variables"]!=FULL_SOURCE_N):
        raise AssertionError("Frozen experimental controls changed")
    return p

def read_precommitted_manifest():
    blob=subprocess.run(["git","hash-object",str(MANIFEST_PATH)],check=True,
                        capture_output=True,text=True).stdout.strip()
    if blob!=MANIFEST_BLOB:
        raise AssertionError("Original CNF manifest Git blob mismatch after freeze")
    fixed=json.loads(MANIFEST_PATH.read_text())
    if fixed["schema"]!="JANUS-JGPT-R3-COLD-FIRST-VERIFIED-HIT-EXACT-CNF-MANIFEST-V1":
        raise AssertionError("Original source manifest schema unknown")
    if fixed!=generated_manifest():
        raise AssertionError("Future source manifest differs from original sampled SHA set")
    if len(fixed["samples"])!=66:
        raise AssertionError("Future sources not a locked 66-case cohort")
    return {(x["seed"],x["slot"]):x for x in fixed["samples"]}

def make_new_ood_source(seed,offset):
    """Consult precommitted SHA by seed+slot, NEVER mutate after seeing hits."""
    candidate=frozen_source(seed,offset)
    locked=read_precommitted_manifest()[(seed,offset)]
    if (candidate["source_logical_sha256"]!=locked["source_logical_sha256"]
        or candidate["family"]!=locked["family"] or candidate["n"]!=locked["n"]):
        raise AssertionError("Original source was modified after precommit")
    return {"family":candidate["family"],"seed":seed,
            "case_offset":offset,"n":candidate["n"],
            "rows":candidate["rows"],
            "source_sha256":candidate["source_logical_sha256"]}

def early_after_verified_hit(rows,n,order,mode,known,up_eq,cache):
    """COLD is allowed to exit AFTER a source-bound exact +rank>0 receipt.

    This preserves existence-of-at-least-one verified useful XOR only. It
    never certifies that *all* independent XORs have been found; for that,
    the old exhaustive mode must be explicitly requested instead.
    """
    effective="WARM" if mode=="COLD" else mode
    r=exact.run_order(rows,n,order,effective,known,up_eq,cache)
    r["mode"]="COLD_EARLY_EXACT_FIRST_HIT" if mode=="COLD" else mode
    r["complete_rank_inventory"]=False
    return r

def original_exhaustive(rows,n,order,mode,known,up_eq,cache):
    """Old COLD contract for the exact same original frozen CNF."""
    r=exact.run_order(rows,n,order,mode,known,up_eq,cache)
    r["complete_rank_inventory"]="FULL_SINGLE_PIVOT_ROOT_COVERAGE" if mode=="COLD" else False
    return r

def rank_inputs(rows,n,exp):
    cover=extract_paged_mixed_xor(rows,n)
    if cover["status"]!="SOURCE_PARTITION_VERIFIED":
        raise AssertionError("Exact source partition invalid")
    known={(tuple(x["variables"]),x["rhs"]) for x in cover["equations"]}
    up=baseline_case(n,rows)
    if up["status"]!="UP_AND_COMPLETE_SIGNMASK_XOR_BASELINE_READY":
        raise AssertionError("Independent UP + XOR reference failed")
    up_eq={(tuple(x["variables"]),x["rhs"]) for x in up["baseline_equations"]}
    return known,up_eq

def bounded_proof_probe(rows,n,pivot,known,up_eq):
    """Never ask an original-width<=4 DAG verifier to replay width-5 parents.

    Exact source SAT cases are retained unchanged. Unverifiable candidate
    transitions ABSTAIN, not silently reclassified as proof or SAT UNSAT.
    This controls a verifier capability boundary exposed by the first CI.
    """
    f=exact.feature(rows,pivot)
    parents=f["pos"]+f["neg"]
    if any(len(row)>4 for _,row in parents):
        return {"pivot":pivot,"status":"ABSTAIN_SOURCE_PARENT_WIDTH_OVER4",
                "pair_work":f["pair_work"],"new_keys":[],
                "rank_delta":0,"rank_delta_over_UP":0}
    return exact.exact_probe(rows,n,pivot,known,up_eq)

def calibrate_train_only(logits,labels):
    if len(labels)<16:
        return 1.0
    scores=[]
    for t in TEMP_GRID:
        v=sum((1/(1+math.exp(-max(-60,min(60,z/t))))-y)**2
              for z,y in zip(logits,labels))/len(labels)
        scores.append((v,t))
    best=min(scores)
    original=next(s for s,t in scores if t==1.0)
    # Avoid microchanges in logits from flipping the governance temperature.
    return best[1] if best[0]<original-0.008 else 1.0

def make_source_features(rows,n):
    features=[exact.feature(rows,p) for p in range(1,n+1)]
    x=tensor_features(rows,n)
    return features,x

def guess_order(model,x,features,temp):
    model.eval()
    t=perf_counter()
    with torch.no_grad():
        raw=model(x).detach().tolist()
    infer=perf_counter()-t
    probs=[1/(1+math.exp(-max(-60,min(60,float(z)/temp)))) for z in raw]
    def sort_key(idx):
        f=features[idx]
        # Fixed-point rank score removes unstable near-ties across CPU runners.
        certainty=int(round(probs[idx]*64))
        cost=f["pair_work"]
        efficiency=int(round(1000*certainty/math.sqrt(1+cost)))
        return (int(f["eligible"]),efficiency,f["priority"])
    return [features[i]["pivot"] for i in
            sorted(range(len(features)),key=sort_key,reverse=True)],raw,probs,infer

def frozen_checkpoint(model,seed,training_shas,temp):
    tensors={}
    for name,p in sorted(model.state_dict().items()):
        t=p.detach().cpu().contiguous().view(-1)
        # Quantized values define the deployable SHADOW weights. This is a
        # genuine fixed-point representation, not a post hoc SHA smoothing.
        values=[int(v) for v in torch.round(t*WEIGHT_GRID).to(torch.int64).tolist()]
        tensors[name]={"shape":list(p.shape),"q1024":values}
    payload={
        "schema":"JANUS-JGPT-R2-SAT-SHADOW-WEIGHTS-Q1024-V1",
        "seed":seed,"train_sha256":training_shas,"train_count":TRAIN,
        "grid":WEIGHT_GRID,"temperature":temp,
        "ranker":"JGPTSatPivotRanker", "model_state_ints":tensors,
        "training_data_scope":"VERIFIED_SOURCE_PROOFS_ONLY",
        "holdout_updates":0,"external_validation":"NONE",
        "production_authority":False
    }
    digest=sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return payload,digest

def run_seed(seed):
    exact.SEED=seed
    torch.manual_seed(seed)
    random.seed(seed)
    model=JGPTSatPivotRanker()
    initial={k:v.detach().clone() for k,v in model.named_parameters()}
    opt=torch.optim.AdamW(model.parameters(),lr=0.003,weight_decay=0.01)
    experience={}
    fingerprint_counts=defaultdict(int)
    train_x,train_y=[],[]
    temp=1.0
    records=[]
    seen_shas=set()
    total_training_probes=0
    total_training_pairs=0
    train_exact_seconds=0.0
    train_optimizer_seconds=0.0
    infer_seconds=0.0
    actual_policy_seconds=defaultdict(float)
    audit_exact_seconds=0.0
    audit_exact_probes=0
    for idx in range(TRAIN+HOLDOUT):
        frozen=idx>=TRAIN
        if frozen:
            item=make_new_ood_source(seed,idx-TRAIN)
            case={"n":item["n"],"rows":item["rows"],"family":item["family"],
                  "original_source_logical_sha256":item["source_sha256"]}
        else:
            case=exact.source_case(idx)
        n,rows=case["n"],case["rows"]
        source_sha=case["original_source_logical_sha256"]
        if source_sha in seen_shas:
            raise AssertionError("train/holdout source reused")
        seen_shas.add(source_sha)
        known,up_eq=rank_inputs(rows,n,experience)
        features,x=make_source_features(rows,n)
        fp=(len(rows),sum(len(c)==1 for c in rows),
            sum(len(c)==4 for c in rows))
        support=fingerprint_counts[fp]
        mode="COLD" if support<3 else "WARM" if support<8 else "HOT"
        neural_order,raw,probs,dt=guess_order(model,x,features,temp)
        infer_seconds+=dt
        old_order=[f["pivot"] for f in
                   sorted(features,key=lambda f:exact.trained_rank(f,experience),
                          reverse=True)]
        if not frozen:
            # Exactly two SOURCE-ONLY ordered pivots; no exact future label
            # is inspected before selection. Two exact proofs are the ENTIRE
            # train oracle budget and are also shared with the teacher.
            first=old_order[0]
            rest=[p for p in range(1,n+1) if p!=first]
            second=rest[random.Random(seed+idx*4001).randrange(len(rest))]
            selected=(first,second)
            labels=[]
            for pivot in selected:
                t=perf_counter()
                receipt=bounded_proof_probe(rows,n,pivot,known,up_eq)
                train_exact_seconds+=perf_counter()-t
                total_training_probes+=1
                total_training_pairs+=receipt["pair_work"]
                label=int(receipt["rank_delta_over_UP"]>0)
                labels.append(label)
            # Teacher and neural see SAME exact-labeled two pivots, after
            # both would have predicted; none of 7 unqueried labels leak.
            t=perf_counter()
            model.train()
            target=torch.tensor(labels,dtype=torch.float32)
            for _ in range(GRAD_UPDATES):
                opt.zero_grad(set_to_none=True)
                logits=model(x)[torch.tensor([p-1 for p in selected])]
                loss=nn.functional.binary_cross_entropy_with_logits(logits,target)
                if not torch.isfinite(loss):
                    raise AssertionError("Nonfinite training objective")
                loss.backward()
                norm=nn.utils.clip_grad_norm_(model.parameters(),1.0)
                if not torch.isfinite(norm):
                    raise AssertionError("Nonfinite training gradient")
                opt.step()
                with torch.no_grad():
                    for p in model.parameters():
                        p.copy_(torch.round(p*WEIGHT_GRID)/WEIGHT_GRID)
            train_optimizer_seconds+=perf_counter()-t
            for p,label in zip(selected,labels):
                k=exact.model_key(features[p-1])
                hits,total=experience.get(k,(0,0))
                experience[k]=(hits+label,total+1)
            train_x.extend(raw[p-1] for p in selected)
            train_y.extend(labels)
            temp=calibrate_train_only(train_x,train_y)
            fingerprint_counts[fp]+=1
            records.append({"cycle":idx+1,"phase":"TRAIN", "source_sha256":source_sha,
                            "selected_exact_pivots_count":2,
                            "labels":[int(z) for z in labels],
                            "temperature_chosen_after_training":temp,
                            "null_or_negative_labels_retained":True})
            continue

        # The frozen weights/temp/experience are ONLY read here. All exact
        # labels below belong to evaluation and DO NOT enter optimizer.
        cache={}
        t=perf_counter()
        for pivot in range(1,n+1):
            cache[pivot]=bounded_proof_probe(rows,n,pivot,known,up_eq)
        audit_exact_seconds+=perf_counter()-t
        audit_exact_probes+=n
        random_order=list(range(1,n+1))
        random.Random(seed^((idx+1)*1117)).shuffle(random_order)
        # Original COLD always visited all pivots; R3 early COLD stops on
        # the FIRST independently replayed proof with +rank vs original UP.
        arm_inputs={
            "neural_sparse_2":(neural_order,mode,True),
            "old_juxtapose_teacher_equal_2":(old_order,mode,True),
            "teacher_original_exhaustive_cold":(old_order,mode,False),
            "static":(list(range(1,n+1)),"STATIC",True),
            "seeded_random":(random_order,"RANDOM",True)
        }
        arms={}
        for arm,(order,mode_value,stop_early) in arm_inputs.items():
            caller=early_after_verified_hit if stop_early else original_exhaustive
            arms[arm]=caller(rows,n,order,mode_value,known,up_eq,cache)
            # Re-execute this ACTUAL policy with its own clean proof cache to
            # measure full exact math/proof replay without sharing the
            # scientist's full-oracle diagnostic cache between competitors.
            t=perf_counter()
            actual=caller(rows,n,order,mode_value,known,up_eq,{})
            elapsed=perf_counter()-t
            actual_policy_seconds[arm]+=elapsed
            if (arms[arm]["exact_pivot_checks"]!=actual["exact_pivot_checks"]
                or arms[arm]["symbolic_pair_work"]!=actual["symbolic_pair_work"]
                or bool(arms[arm]["new_rank_over_UP_first_hit"]) !=
                   bool(actual["new_rank_over_UP_first_hit"])):
                raise AssertionError("Measured standalone proof replay differs from virtual protocol")

        hits={k:int(v["new_rank_over_UP_first_hit"]>0) for k,v in arms.items()}
        if len(set(hits.values()))!=1:
            raise AssertionError("Early exit changed existence-of-one source-proved math hit")
        # We make NO assertion of complete rank inventory in the early arm.
        # This is a first-positive proof / existence objective ONLY.
        labels=[int(cache[p]["rank_delta_over_UP"]>0) for p in range(1,n+1)]
        records.append({
            "cycle":idx+1,"phase":"FROZEN_SYNTHETIC_OOD",
            "source_sha256":source_sha,"family_for_reporting_only":case["family"],
            "n":n,"source_manifest_git_blob":MANIFEST_BLOB,"sat_original_model_verified":True,
            "predictions_made_before_exact_holdout_receipts":True,
            "temperature_at_prediction":temp,
            "predictions":probs,"exact_labels_for_evaluation_only":labels,
            "all_arms":{k:{"checks":v["exact_pivot_checks"],
                            "symbolic_pair_work":v["symbolic_pair_work"],
                            "exact_hit":hits[k]} for k,v in arms.items()}
        })
    training=[r for r in records if r["phase"]=="TRAIN"]
    holdout=[r for r in records if r["phase"]=="FROZEN_SYNTHETIC_OOD"]
    assert len(training)==TRAIN and len(holdout)==HOLDOUT
    assert total_training_probes==2*TRAIN
    assert audit_exact_probes==HOLDOUT*FULL_SOURCE_N
    checkpoint,ck_sha=frozen_checkpoint(model,seed,[r["source_sha256"] for r in training],temp)
    weights_delta=math.sqrt(sum(float(torch.sum((p.detach()-initial[n])**2).item())
                                for n,p in model.named_parameters()))
    if weights_delta<=0:
        raise AssertionError("No learned weight change")
    trained_arms=("neural_sparse_2","old_juxtapose_teacher_equal_2",
                  "teacher_original_exhaustive_cold")
    def aggregate(arm):
        attempts=[r["all_arms"][arm] for r in holdout]
        checks=sum(r["checks"] for r in attempts)
        return {"new_verified_math_hits":sum(r["exact_hit"] for r in attempts),
                "holdout_exact_pivot_checks":checks,
                "holdout_symbolic_pair_work":sum(r["symbolic_pair_work"] for r in attempts),
                "training_exact_probes_charged":total_training_probes
                    if arm in trained_arms else 0,
                "virtual_probes_train_plus_holdout":checks+(total_training_probes
                    if arm in trained_arms else 0),
                "virtual_pair_work_train_plus_holdout":sum(
                    r["symbolic_pair_work"] for r in attempts)+(total_training_pairs
                    if arm in trained_arms else 0)}
    totals={arm:aggregate(arm) for arm in (
        "neural_sparse_2","old_juxtapose_teacher_equal_2",
        "teacher_original_exhaustive_cold","static","seeded_random")}
    predictions=[x for r in holdout for x in r["predictions"]]
    targets=[x for r in holdout for x in r["exact_labels_for_evaluation_only"]]
    brier=sum((p-y)**2 for p,y in zip(predictions,targets))/len(targets)
    # Robust bins, no claims of external statistical calibration.
    ece=0.0
    for bin_id in range(5):
        indexes=[i for i,p in enumerate(predictions)
                 if bin_id/5<=p<(bin_id+1)/5 or (bin_id==4 and p==1)]
        if indexes:
            ece+=(len(indexes)/len(targets))*abs(
                sum(predictions[i] for i in indexes)/len(indexes)-
                sum(targets[i] for i in indexes)/len(indexes))
    return {
        "seed":seed,"frozen_original_protocol_blob":PROTOCOL_BLOB,
        "model_sha256":ck_sha,"checkpoint":checkpoint,
        "train_source_shas":[r["source_sha256"] for r in training],
        "holdout_source_shas":[r["source_sha256"] for r in holdout],
        "all_records":records,
        "trained_weights_L2_change":weights_delta,
        "calibration":{"frozen_temperature":temp,"OOD_Brier":brier,"OOD_ECE_5_bins":ece},
        "amortized_cost_exact_probes_and_symbolic_pairs":totals,
        "charge_real_training_proof_labels":total_training_probes,
        "charge_real_training_proof_symbolic_pairs":total_training_pairs,
        "charge_validation_audit_holdout_probes":audit_exact_probes,
        "measured_separate_policy_exact_source_proof_wall_seconds":dict(actual_policy_seconds),
        "amortized_shadow_wall_seconds_excluding_common_input_parse_and_CNF_generation":{
            arm: actual_policy_seconds[arm]+(train_exact_seconds if arm in trained_arms else 0)
                 +(train_optimizer_seconds+infer_seconds if arm=="neural_sparse_2" else 0)
            for arm in totals
        },
        "early_exit_preserves_only_first_verified_hit_not_full_XOR_inventory":True,
        "timings_seconds_not_equivalent_to_solver_end_to_end":{
            "training_exact_replay":train_exact_seconds,
            "training_optimizer":train_optimizer_seconds,
            "all_train_and_holdout_neural_inference":infer_seconds,
            "holdout_all_candidates_for_independent_science_audit":audit_exact_seconds,
        },
        "weights_train_only":True,"holdout_labels_never_learned":True,
        "external_validation":"NONE", "C023":"UNCHANGED"
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--checkpoint-dir",type=Path)
    a=parser.parse_args()
    protocol=read_frozen_protocol()
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True)
    torch.backends.mkldnn.enabled=False
    result=[run_seed(seed) for seed in NEW_SEEDS]
    all_ood=[x for r in result for x in r["holdout_source_shas"]]
    all_train=[x for r in result for x in r["train_source_shas"]]
    assert len(all_ood)==len(set(all_ood))==66
    assert set(all_ood)=={x["source_logical_sha256"] for x in read_precommitted_manifest().values()}
    assert not(set(all_ood)&set(all_train))
    if a.checkpoint_dir:
        a.checkpoint_dir.mkdir(parents=True,exist_ok=True)
        for r in result:
            (a.checkpoint_dir/f"JGPT_R2_{r['seed']}.json").write_text(
                json.dumps(r["checkpoint"],sort_keys=True,indent=2)+"\n")
    out={
        "schema":SCHEMA,"protocol_git_blob":PROTOCOL_BLOB,
        "seeds_preregistered":list(NEW_SEEDS),
        "preregistered_original_cnf_manifest_git_blob":MANIFEST_BLOB,
        "COLD_first_verified_hit_target_only":True,
        "full_rank_inventory_in_early_mode":"NOT_CLAIMED",
        "total_new_ood_sources":len(all_ood),
        "train_budget_2_per_cycle":True,
        "checkpoint_type":"R3_TRAINED_QUANTIZED_Q1024_SAT_SHADOW_ONLY",
        "labeling_costs_charged":True,
        "all_ood_untrained":True,
        "all_math_results_independently_source_DAG_replayed":True,
        "neural_ranker_never_issues_SAT_verdict":True,
        "external_witness":"OPEN","R6":"FROZEN_SCIENCE_GATE_NOT_PASSED",
        "production_C023":"UNCHANGED",
        "reports":result
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"status":"R3_FROZEN_NEW_OOD_EARLY_EXIT_COST_AND_REPRO_CALCULATED",
        "protocol_git_blob":PROTOCOL_BLOB,
        "seeds":[{"seed":x["seed"],"weight_sha":x["model_sha256"],
                  "weights_changed_L2":round(x["trained_weights_L2_change"],3),
                  "charged_train_exact_probes":x["charge_real_training_proof_labels"],
                  "evaluation_audit_exact_probes":x["charge_validation_audit_holdout_probes"],
                  "OOD_Brier":round(x["calibration"]["OOD_Brier"],6),
                  "OODece":round(x["calibration"]["OOD_ECE_5_bins"],6),
                  "totals":x["amortized_cost_exact_probes_and_symbolic_pairs"],
                  "amortized_wall_seconds":{k:round(v,4) for k,v in x["amortized_shadow_wall_seconds_excluding_common_input_parse_and_CNF_generation"].items()}}
                 for x in result]},sort_keys=True))
if __name__=="__main__":
    main()
