#!/usr/bin/env python3
"""JGPT-CODEX-inspired online transformer teacher for JANUS/JUXTAPOSE67.

A compact PyTorch attention model learns ONLY from previously completed,
original-source-DAG-replayed XOR/rank receipts. Prior JGPT_CODEX(2).py
(proprietor-supplied MIT file) provided architecture pattern:
TransformerEncoderLayer/AdamW, gradient clipping, prequential EMA, checkpoint.
The original BYTE-LM weights are NOT loaded: SAT structural numeric feature
space is incompatible. These weights are newly trained, same-administrator.

TWO predeclared synthetic seed cohorts x67 each:
45 exact-labeled online TRAIN episodes; 22 future HOLDOUT with weights and
temperature frozen. The model RANKS source-only pivot choices, but cannot
make SAT claims or bypass independent exact proof replay or the UP baseline.
No hidden label/pivot ID/family or post-outcome metrics in model inputs.
No auto-deploy, production C023, external admin, paid Rowan or NAS writes.
"""
from __future__ import annotations
from collections import defaultdict
from hashlib import sha256
import argparse
import copy
import json
import math
from pathlib import Path
import random
import sys
from time import perf_counter
import torch
from torch import nn

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import janus_juxtapose67_sat_xor as exact
from janus_time_sat_004d4d_paged_support import extract_paged_mixed_xor
from time_sat_004d9b_up_cleanroom_baseline import baseline_case

TRAIN=45
HOLDOUT=22
SEEDS=(20261114,20261117)
HIDDEN=32
HEADS=4
LR=0.003
STEPS_PER_EPISODE=2
TEMPERATURES=(0.7,1.0,1.3,1.7,2.3)
BATCH_TOTAL=9
MODEL_LINEAGE="JGPT_CODEX(2).py / ByteTransformer / MIT / architecture-inspired fresh SAT weights"
SCHEMA="JANUS-JGPT-JUXTAPOSE67-ONLINE-PROSPECTIVE-SYNTHETIC-V1"

def tensor_features(rows,n):
    """Order-independent, no pivot-ID or target labels, only source geometry."""
    out=[]
    for pivot in range(1,n+1):
        f=exact.feature(rows,pivot)
        out.append([
            min(8,len(f["pos"]))/8.0,
            min(8,len(f["neg"]))/8.0,
            math.log1p(f["pair_work"])/math.log(65),
            float(f["eligible"]),
            min(16,sum(len(r)==1 for _,r in f["pos"]+f["neg"]))/16.0,
            min(16,sum(len(r)==2 for _,r in f["pos"]+f["neg"]))/16.0,
            min(16,sum(len(r)==3 for _,r in f["pos"]+f["neg"]))/16.0,
            min(16,sum(len(r)==4 for _,r in f["pos"]+f["neg"]))/16.0,
            min(16,f["priority"][-1])/16.0,
            abs(len(f["pos"])-len(f["neg"]))/8.0,
            min(30,len(rows))/30.0,
            1.0,
        ])
    return torch.tensor(out,dtype=torch.float32)

class JGPTSatPivotRanker(nn.Module):
    """One attention encoder + source-position-free pivot scoring head."""
    def __init__(self):
        super().__init__()
        self.embed=nn.Linear(12,HIDDEN)
        enc=nn.TransformerEncoderLayer(
            d_model=HIDDEN,nhead=HEADS,dim_feedforward=HIDDEN*2,
            dropout=0.0,activation="gelu",batch_first=True,norm_first=True
        )
        self.attention=nn.TransformerEncoder(enc,num_layers=1,
                                             enable_nested_tensor=False)
        self.norm=nn.LayerNorm(HIDDEN)
        self.head=nn.Linear(HIDDEN,1)
    def forward(self,x):
        z=self.embed(x)
        z=self.attention(z.unsqueeze(0)).squeeze(0)
        return self.head(self.norm(z)).squeeze(-1)

def probs_from_logits(logits,temp):
    return torch.sigmoid(torch.tensor(logits,dtype=torch.float64)/temp).tolist()

def brier(p,y):
    return sum((a-b)**2 for a,b in zip(p,y))/max(1,len(y))

def ece(p,y,bins=5):
    total=0.0
    for k in range(bins):
        ids=[i for i,v in enumerate(p) if k/bins<=v<(k+1)/bins or (k==bins-1 and v==1)]
        if ids:
            confidence=sum(p[i] for i in ids)/len(ids)
            accuracy=sum(y[i] for i in ids)/len(ids)
            total+=abs(confidence-accuracy)*len(ids)/len(p)
    return total

def choose_temperature(prior_logits,prior_labels):
    if len(prior_labels)<27:
        return 1.0
    scores=[(brier(probs_from_logits(prior_logits,t),prior_labels),t)
            for t in TEMPERATURES]
    return min(scores)[1]

def model_order(model,features,source,experience,temp,train_seen):
    with torch.no_grad():
        logits=model(features).tolist()
    probs=probs_from_logits(logits,temp)
    # Never trust the untrained net. A bounded structural JUXTAPOSE teacher
    # orders before >=10 completed TRAIN episodes.
    if train_seen<10:
        return [f["pivot"] for f in
                sorted(source,key=lambda x:exact.trained_rank(x,experience),reverse=True)],logits,probs
    def score(i):
        f=source[i]
        cost=1.0 + f["pair_work"]
        # Cost-aware expected exact-rank yield per limited search effort.
        # The model does not assert that the expected yield is true.
        return (float(f["eligible"]),
                probs[i]/math.sqrt(cost),
                exact.trained_rank(f,experience))
    return [source[i]["pivot"] for i in
            sorted(range(len(source)),key=score,reverse=True)],logits,probs

def run_seed(seed):
    old_seed=exact.SEED
    exact.SEED=seed
    try:
        torch.manual_seed(seed)
        random.seed(seed)
        torch.set_num_threads(1)
        model=JGPTSatPivotRanker()
        opt=torch.optim.AdamW(model.parameters(),lr=LR,weight_decay=0.01)
        experience={}
        fingerprints=defaultdict(int)
        train_logits=[]
        train_labels=[]
        train_checkpoints=[]
        train_ema=None
        temp=1.0
        train_seconds=0.0
        infer_seconds=0.0
        rows_out=[]
        for idx in range(TRAIN+HOLDOUT):
            case=exact.source_case(idx)
            rows,n=case["rows"],case["n"]
            verify=extract_paged_mixed_xor(rows,n)
            assert verify["status"]=="SOURCE_PARTITION_VERIFIED"
            known={(tuple(v["variables"]),v["rhs"]) for v in verify["equations"]}
            up=baseline_case(n,rows)
            assert up["status"]=="UP_AND_COMPLETE_SIGNMASK_XOR_BASELINE_READY"
            up_eq={(tuple(x["variables"]),x["rhs"]) for x in up["baseline_equations"]}
            features=[exact.feature(rows,p) for p in range(1,n+1)]
            x=tensor_features(rows,n)
            fingerprint=(len(rows),sum(len(c)==1 for c in rows),
                        sum(len(c)==4 for c in rows))
            prior_support=fingerprints[fingerprint]
            mode="COLD" if prior_support<3 else "WARM" if prior_support<8 else "HOT"
            inf_start=perf_counter()
            order,logits,probs=model_order(model,x,features,experience,temp,min(TRAIN,idx))
            infer_seconds+=perf_counter()-inf_start
            # The oracle below is a retained exact independent source replay,
            # never a network call or speculative label.
            cache={}
            for pivot in range(1,n+1):
                cache[pivot]=exact.exact_probe(rows,n,pivot,known,up_eq)
            labels=[int(cache[p]["rank_delta_over_UP"]>0) for p in range(1,n+1)]
            # One first-run partial policy, with safe COLD full coverage.
            neural=exact.run_order(rows,n,order,mode,known,up_eq,cache)
            teacher_order=[p for p in
                           sorted(range(1,n+1),
                                  key=lambda p:exact.trained_rank(features[p-1],experience),
                                  reverse=True)]
            teacher=exact.run_order(rows,n,teacher_order,mode,known,up_eq,cache)
            static=exact.run_order(rows,n,list(range(1,n+1)),"STATIC",known,up_eq,cache)
            rseed=random.Random(seed^((idx+1)*1117))
            random_order=list(range(1,n+1))
            rseed.shuffle(random_order)
            random_ctrl=exact.run_order(rows,n,random_order,"RANDOM",known,up_eq,cache)
            if not (bool(neural["new_rank_over_UP_first_hit"]) ==
                    bool(static["new_rank_over_UP_first_hit"]) ==
                    bool(teacher["new_rank_over_UP_first_hit"]) ==
                    bool(random_ctrl["new_rank_over_UP_first_hit"])):
                raise AssertionError("Neural proposal changed exact source-proof coverage")
            entry={
                "cycle":idx+1,
                "phase":"FROZEN_HOLDOUT" if idx>=TRAIN else "ONLINE_TRAIN",
                "source_sha256":case["original_source_logical_sha256"],
                "source_family_REPORT_ONLY":case["family"],
                "source_model_checked":True,
                "temperature_at_prediction":temp,
                "probabilities_before_exact_results":probs,
                "exact_labels_after_prediction":labels,
                "predicted_order":order,
                "new_rank_positive_pivots":sum(labels),
                "frozen_before_holdout":idx>=TRAIN,
                "neural":{k:v for k,v in neural.items() if k!="steps"},
                "teacher":{k:v for k,v in teacher.items() if k!="steps"},
                "static":{k:v for k,v in static.items() if k!="steps"},
                "random":{k:v for k,v in random_ctrl.items() if k!="steps"},
                "Brier_before_update":brier(probs,labels),
            }
            rows_out.append(entry)
            if idx<TRAIN:
                start=perf_counter()
                model.train()
                y=torch.tensor(labels,dtype=torch.float32)
                for step in range(STEPS_PER_EPISODE):
                    opt.zero_grad(set_to_none=True)
                    z=model(x)
                    loss=nn.functional.binary_cross_entropy_with_logits(z,y)
                    if not torch.isfinite(loss):
                        raise AssertionError("Nonfinite online JGPT loss")
                    loss.backward()
                    grad_norm=torch.nn.utils.clip_grad_norm_(model.parameters(),1.0)
                    if not torch.isfinite(grad_norm):
                        raise AssertionError("Nonfinite online JGPT gradient")
                    opt.step()
                train_seconds+=perf_counter()-start
                train_ema=float(loss.detach()) if train_ema is None else 0.9*train_ema+0.1*float(loss.detach())
                # *All* labels used only AFTER the current prediction was frozen,
                # and only from independently proof-replayed exact probes.
                train_logits+=logits
                train_labels+=labels
                temp=choose_temperature(train_logits,train_labels)
                fingerprints[fingerprint]+=1
                for f,label in zip(features,labels):
                    key=exact.model_key(f)
                    hits,total=experience.get(key,(0,0))
                    experience[key]=(hits+label,total+1)
                train_checkpoints.append({
                    "after_train_cycle":idx+1,
                    "EMA_BCE_train":train_ema,
                    "temperature_after_past_exact_receipts":temp,
                    "prior_exact_label_count":len(train_labels),
                    "snapshot_gradients_finite":True,
                })
            else:
                # No weight/optimizer/temp update here; exact outcomes are
                # used *only* for evaluation and not appended to memory.
                assert len(train_checkpoints)==TRAIN
        def metrics(seq,arm):
            return {"cases":len(seq),
                    "hits":sum(r[arm]["new_rank_over_UP_first_hit"]>0 for r in seq),
                    "checks":sum(r[arm]["exact_pivot_checks"] for r in seq),
                    "pair_work":sum(r[arm]["symbolic_pair_work"] for r in seq)}
        ho=rows_out[TRAIN:]
        summary={arm:metrics(ho,arm) for arm in ("neural","teacher","static","random")}
        hp=[p for r in ho for p in r["probabilities_before_exact_results"]]
        hy=[y for r in ho for y in r["exact_labels_after_prediction"]]
        summary["calibration"]={
            "prequential_holdout_brier":brier(hp,hy),
            "prequential_holdout_ECE_5bin":ece(hp,hy),
            "holdout_positive_rate":sum(hy)/len(hy),
            "frozen_temperature":temp,
            "prediction_count":len(hp)
        }
        state={name:{
                    "shape":list(t.shape),
                    "values":[float(x) for x in t.detach().cpu().flatten().tolist()]}
               for name,t in sorted(model.state_dict().items())}
        checkpoint={
            "schema":"JANUS-JGPT-SAT-CANDIDATE-WEIGHT-CHECKPOINT-V1",
            "source_model_architecture":MODEL_LINEAGE,
            "training_seed":seed,
            "trained_only_on_first_cycles":TRAIN,
            "train_source_sha256":[r["source_sha256"] for r in rows_out[:TRAIN]],
            "holdout_source_sha256":[r["source_sha256"] for r in ho],
            "trained_on_holdout":False,
            "temperature_calibrated_on_training_only":temp,
            "attention_heads":HEADS,
            "hidden_units":HIDDEN,
            "layers":1,
            "optimizer":"AdamW",
            "learning_rate":LR,
            "model_state":state,
            "promotion_authorized":False
        }
        raw=json.dumps(checkpoint,sort_keys=True,separators=(",",":")).encode()
        state_sha=sha256(raw).hexdigest()
        assert len({r["source_sha256"] for r in rows_out})==TRAIN+HOLDOUT
        assert all(r["phase"]=="FROZEN_HOLDOUT" for r in ho)
        report={
            "seed":seed,
            "checkpoint_sha256":state_sha,
            "summary":summary,
            "train_wall_seconds":train_seconds,
            "inference_wall_seconds_all67":infer_seconds,
            "number_of_parameters":sum(p.numel() for p in model.parameters()),
            "online_exact_train_updates":TRAIN*STEPS_PER_EPISODE,
            "prequential_history":train_checkpoints,
            "records":rows_out,
            "checkpoint":checkpoint
        }
        return report
    finally:
        exact.SEED=old_seed

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--checkpoint-dir",type=Path)
    args=ap.parse_args()
    reports=[run_seed(s) for s in SEEDS]
    for report in reports:
        s=report["summary"]
        assert all(s[a]["hits"]==s["static"]["hits"] for a in ("neural","teacher","random"))
        assert report["checkpoint"]["trained_on_holdout"] is False
        if args.checkpoint_dir:
            args.checkpoint_dir.mkdir(parents=True,exist_ok=True)
            fp=args.checkpoint_dir/f"JGPT_SAT_SEED_{report['seed']}.json"
            fp.write_text(json.dumps(report["checkpoint"],sort_keys=True,indent=2)+"\n")
    out={
      "schema":SCHEMA,
      "run_intent":"PROSPECTIVE_INTERNAL_ADAPTIVE_EXACT_RANK_LEARNING_ONLY",
      "source_model_lineage":MODEL_LINEAGE,
      "original_JGPT_byteLM_weights_imported":False,
      "seeds_predeclared":list(SEEDS),
      "cycles_each":TRAIN+HOLDOUT,"train_each":TRAIN,"holdout_each":HOLDOUT,
      "prediction_before_current_source_exact_labels":True,
      "current_training_updates_only_from_already_verified_source_proofs":True,
      "heldout_weights_and_temperature_frozen":True,
      "SAT_solver_wall_time_comparison":"NOT_RUN",
      "external_independent_validation":"OPEN",
      "R6_science_gate":"NOT_PASSED_UNCHANGED",
      "production_C023":"UNCHANGED",
      "reports":reports
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    print(json.dumps({
      "status":"JGPT_SAT_ONLINE_WEIGHTS_TRAINED_FROZEN_HOLDOUT_EVALUATED",
      "results":[{
        "seed":r["seed"],"params":r["number_of_parameters"],
        "train_updates":r["online_exact_train_updates"],
        "checkpoint_sha256":r["checkpoint_sha256"],
        "train_seconds":round(r["train_wall_seconds"],3),
        "inference_seconds":round(r["inference_wall_seconds_all67"],3),
        "holdout":r["summary"]
      } for r in reports]
    },sort_keys=True))
if __name__=="__main__":
    main()
