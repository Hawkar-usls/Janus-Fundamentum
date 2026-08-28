#!/usr/bin/env python3
"""JANUS 50:50 Cycle-2: previous PIPPI/Spider mirror feeds Keymaster.

Controlled changes from Cycle-1:
- known exact formula pool grows 24 -> 32 fingerprints;
- the JGPT/Slime architectures themselves are held fixed;
- adviser scores are normalized per formula before fusion;
- fusion weights are selected ONLY on six calibration fingerprints;
- the frozen Cycle-1 Spider attention mirror is available as a fourth adviser;
- final evaluation uses eight NEW formula fingerprints.

This isolates whether more exact experience + calibrated fusion + prior-cycle
attention improve search ordering. It does not prove a general learning law.
P_VS_NP remains OPEN.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path
from typing import Any

import torch

from experiments.mad_lab import keymaster_50x50_cycle1_teacher_slime as c1

P_VS_NP = "OPEN"
SCHEMA = "JANUS/KEYMASTER/50x50-CYCLE2-PIPPI-MIRROR/v1.0.0"


def normalize(v: list[float]) -> list[float]:
    lo, hi = min(v), max(v)
    if hi - lo < 1e-12:
        return [0.5] * len(v)
    return [(x - lo) / (hi - lo) for x in v]


def pattern_key(row: dict[str, Any], i: int) -> str:
    summary = row["tokens"][i][-1]
    key = tuple(int(round(summary[j] * 40)) for j in range(3))
    return "pattern:" + "-".join(map(str, key))


def load_attention_prior(path: Path) -> dict[str, dict[str, float]]:
    d = json.loads(path.read_text(encoding="utf-8"))
    assert d["status"].startswith("FROZEN_AFTER_HOLDOUT_SCORING")
    out: dict[str, dict[str, float]] = {}
    for e in d["edge_attention"]:
        out.setdefault(e["pattern"], {})[e["outcome"]] = float(e["attention_weight"])
    return out


def spider_scores(row: dict[str, Any], prior: dict[str, dict[str, float]]) -> list[float]:
    vals = []
    for i in range(7):
        q = prior.get(pattern_key(row, i), {})
        safe = q.get("SAFE_FIRST", 0.0)
        over = q.get("OVERFLOW_FIRST", 0.0)
        vals.append(0.5 + over - safe)  # lower is preferred
    return normalize(vals)


def component_scores(rows, teacher, student, m2r_memory, prior):
    t = c1.evaluate_model_scores(teacher, rows)
    s = c1.evaluate_model_scores(student, rows)
    m = [c1.m2r_scores(m2r_memory, r) for r in rows]
    a = [spider_scores(r, prior) for r in rows]
    return {
        "JGPT": [normalize(list(x)) for x in t],
        "SLIME": [normalize(list(x)) for x in s],
        "M2R": [normalize(list(x)) for x in m],
        "SPIDER": a,
    }


def fused_scores(components: dict[str, list[list[float]]], weights: dict[str, float], j: int) -> list[float]:
    return [sum(weights[k] * components[k][j][i] for k in weights) for i in range(7)]


def score_ranking(scores: list[float], row: dict[str, Any]) -> tuple[int, int]:
    order = c1.rank_from_scores(scores, row)
    rank = order.index(row["best_index"]) + 1
    regret = row["raw"][order[0]] - min(row["raw"])
    return rank, regret


def calibration_objective(rows, comps, weights):
    ranks=[]; regrets=[]; hits=0
    for j,r in enumerate(rows):
        rank, regret=score_ranking(fused_scores(comps,weights,j),r)
        ranks.append(rank); regrets.append(regret); hits += int(rank==1)
    return (sum(ranks)/len(ranks), -hits/len(rows), sum(regrets)/len(regrets), tuple(weights[k] for k in ("JGPT","SLIME","M2R","SPIDER")))


def grid_weights(include_spider: bool) -> list[dict[str,float]]:
    names=("JGPT","SLIME","M2R","SPIDER")
    out=[]
    for a in range(11):
      for b in range(11-a):
       for c in range(11-a-b):
        d=10-a-b-c
        if not include_spider and d!=0: continue
        w=dict(zip(names,(a/10,b/10,c/10,d/10)))
        out.append(w)
    return out


def choose_weights(rows, comps, include_spider: bool):
    cand=grid_weights(include_spider)
    best=min(cand,key=lambda w:calibration_objective(rows,comps,w))
    obj=calibration_objective(rows,comps,best)
    return best,{"mean_exact_best_rank":obj[0],"top1_exact_best_recall":-obj[1],"mean_top1_raw_regret":obj[2],"grid_candidates":len(cand)}


def aggregate_policy(rows, rankings):
    vals=[]
    for r,order in zip(rows,rankings):
        rt=c1.exact_runtime_policy(r,order)
        rank=order.index(r["best_index"])+1
        vals.append((rank,rt))
    return {
        "holdout_formulas":len(vals),
        "top1_exact_best_recall":sum(int(rank==1) for rank,_ in vals)/len(vals),
        "mean_exact_best_rank":sum(rank for rank,_ in vals)/len(vals),
        "exact_checks_attempted":sum(rt["exact_checks_attempted"] for _,rt in vals),
        "pair_work":sum(rt["pair_work"] for _,rt in vals),
        "raw_units_sum":sum(rt["raw_units_sum"] for _,rt in vals),
        "peak_raw_units_max":max(rt["peak_raw_units"] for _,rt in vals),
        "terminal_unsat_count":sum(int(rt["terminal_unsat"]) for _,rt in vals),
    }


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--corpus",type=Path,required=True)
    ap.add_argument("--attention-seed",type=Path,required=True)
    ap.add_argument("--json-out",type=Path,required=True)
    ap.add_argument("--spider-edge-out",type=Path,required=True)
    a=ap.parse_args()
    c1.set_seed(505050)
    corpus=json.loads(a.corpus.read_text(encoding="utf-8"))
    assert corpus["selection"]["train_formulas"]==32 and corpus["selection"]["holdout_formulas"]==8
    ex=c1.build_examples(corpus)
    train32=[r for r in ex if r["split"]=="TRAIN"]
    hold=[r for r in ex if r["split"]=="HOLDOUT"]
    model_train=train32[:26]; calib=train32[26:]
    assert len(model_train)==26 and len(calib)==6 and len(hold)==8

    teacher,ta=c1.train_teacher(model_train,calib)
    student,sa=c1.train_student(model_train,calib,teacher)
    qaudit=c1.quantize_int8_inplace(student)
    prior=load_attention_prior(a.attention_seed)

    calcomps=component_scores(calib,teacher,student,model_train,prior)
    w_no_spider,cal_no=choose_weights(calib,calcomps,False)
    w_with_spider,cal_sp=choose_weights(calib,calcomps,True)

    hcomps=component_scores(hold,teacher,student,model_train,prior)
    policies={}
    policies["STATIC_NUMERIC_NEGATIVE_CONTROL"]=[list(range(7)) for _ in hold]
    for name,key in [("JGPT_TEACHER","JGPT"),("PIVOT_SLIME_INT8","SLIME"),("M2R_PM_ONLY","M2R"),("PIPPI_SPIDER_PRIOR_ONLY","SPIDER")]:
        policies[name]=[c1.rank_from_scores(hcomps[key][j],r) for j,r in enumerate(hold)]
    fixed={"JGPT":0.5,"SLIME":0.3,"M2R":0.2,"SPIDER":0.0}
    policies["KEYMASTER_CYCLE1_FIXED_FUSION_NORMALIZED"]=[c1.rank_from_scores(fused_scores(hcomps,fixed,j),r) for j,r in enumerate(hold)]
    policies["KEYMASTER_CALIBRATED_NO_SPIDER"]=[c1.rank_from_scores(fused_scores(hcomps,w_no_spider,j),r) for j,r in enumerate(hold)]
    policies["KEYMASTER_CALIBRATED_WITH_PIPPI_SPIDER"]=[c1.rank_from_scores(fused_scores(hcomps,w_with_spider,j),r) for j,r in enumerate(hold)]
    policies["ORACLE_LOWER_BOUND"]=[[r["best_index"]]+[i for i in range(7) if i!=r["best_index"]] for r in hold]
    agg={name:aggregate_policy(hold,orders) for name,orders in policies.items()}

    baseline=agg["STATIC_NUMERIC_NEGATIVE_CONTROL"]
    key=agg["KEYMASTER_CALIBRATED_WITH_PIPPI_SPIDER"]
    delta={
      "baseline":"STATIC_NUMERIC_NEGATIVE_CONTROL",
      "scope":"8_NEW_FINGERPRINT_HOLDOUT__SAME_50x50_GENERATOR_FAMILY",
      "exact_checks_saved":baseline["exact_checks_attempted"]-key["exact_checks_attempted"],
      "exact_checks_saved_fraction":(baseline["exact_checks_attempted"]-key["exact_checks_attempted"])/max(1,baseline["exact_checks_attempted"]),
      "pair_work_saved":baseline["pair_work"]-key["pair_work"],
      "pair_work_saved_fraction":(baseline["pair_work"]-key["pair_work"])/max(1,baseline["pair_work"]),
      "raw_work_saved":baseline["raw_units_sum"]-key["raw_units_sum"],
      "raw_work_saved_fraction":(baseline["raw_units_sum"]-key["raw_units_sum"])/max(1,baseline["raw_units_sum"]),
    }

    # Same-generator but different holdout cohort: useful learning-curve signal,
    # not a matched causal delta against Cycle1.
    progress={
      "status":"CROSS_HOLDOUT_COHORT_DIAGNOSTIC__NOT_MATCHED_CAUSAL_DELTA",
      "cycle1_known_fused":{"exact_checks":80,"pair_work":88377,"top1":0.125,"mean_rank":4.0},
      "cycle2_current_fused":{"exact_checks":key["exact_checks_attempted"],"pair_work":key["pair_work"],"top1":key["top1_exact_best_recall"],"mean_rank":key["mean_exact_best_rank"]},
      "same_generator_family":true,
      "different_formula_fingerprints":true
    }

    # New train-only relations are produced after holdout scoring and update the
    # Spider ecology for Cycle3, not retroactively for Cycle2.
    edges=c1.attention_edges(train32)
    a.spider_edge_out.parent.mkdir(parents=True,exist_ok=True)
    a.spider_edge_out.write_text("".join(json.dumps(e,sort_keys=True,separators=(",",":"))+"\n" for e in edges),encoding="utf-8")

    per=[]
    for j,r in enumerate(hold):
        per.append({"seed":r["seed"],"fingerprint":r["fingerprint"],"best_pivot_local":r["best_pivot_local"],"cap":r["cap"],"policy_best_ranks":{name:orders[j].index(r["best_index"])+1 for name,orders in policies.items()},"structural_patterns":[pattern_key(r,i) for i in range(7)]})

    out={
      "schema":SCHEMA,"status":"CYCLE2_FRESH_HOLDOUT_MEASURED__PIPPI_MIRROR_USED_ADVISORY","P_VS_NP":P_VS_NP,
      "controlled_change":{"known_formula_pool":"24->32","model_architecture_changed":false,"score_normalization_added":true,"fusion_calibrated_on_six_fingerprints":true,"previous_pippi_spider_attention_used":true},
      "split":{"model_train":26,"calibration":6,"fresh_holdout":8,"by_formula_fingerprint":true},
      "teacher_audit":ta,"student_audit":sa,"student_int8_quantization":qaudit,
      "calibration_selected_weights":{"without_spider":{"weights":w_no_spider,"metrics":cal_no},"with_pippi_spider":{"weights":w_with_spider,"metrics":cal_sp}},
      "aggregate_exact_runtime":agg,"PIPPI_DELTA2":delta,"progress_vs_cycle1":progress,"per_holdout_formula":per,
      "new_train_relation_edges_for_next_cycle":len(edges),
      "firewall":{"FRESH_HOLDOUT_NOT_USED_FOR_TRAINING":true,"PRIOR_SPIDER_STATE_FROZEN_BEFORE_FRESH_HOLDOUT":true,"CURRENT_CYCLE_SPIDER_UPDATE_NOT_USED_RETROACTIVELY":true,"PIVOT_NUMERIC_ID_NOT_MODEL_FEATURE":true,"ATTENTION_NOT_EXACT_LABEL":true,"SPIDER_EDGE_NOT_CAUSATION":true,"CROSS_HOLDOUT_PROGRESS_NOT_CAUSAL_PROOF":true,"P_VS_NP":P_VS_NP}
    }
    a.json_out.parent.mkdir(parents=True,exist_ok=True)
    a.json_out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":out["status"],"weights":out["calibration_selected_weights"],"delta2":delta,"keymaster":key,"teacher":agg["JGPT_TEACHER"],"slime":agg["PIVOT_SLIME_INT8"],"spider":agg["PIPPI_SPIDER_PRIOR_ONLY"],"P_VS_NP":P_VS_NP},indent=2,sort_keys=True))
    return 0

if __name__=="__main__": raise SystemExit(main())
