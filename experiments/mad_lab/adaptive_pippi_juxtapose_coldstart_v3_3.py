#!/usr/bin/env python3
"""JANUS PIPPI v3.3 — evolutionary warm start + sentinel-first JUXTAPOSE.

This generation honors the accumulated curriculum instead of resetting to the
v2.4 checkpoint. Before a fresh v3.3 fingerprint is generated, it reconstructs
and exact-replays:
  * the original 60 lessons used by v3.0-v3.2;
  * all scored ordinary stages and hard 250:250 bosses from v3.0;
  * all scored ordinary stages and hard 250:250 bosses from v3.1;
  * all scored ordinary stages and hard 250:250 bosses from v3.2.
Total warm exact episodes: 160. Negative/regression episodes are retained.

Controlled behavioral correction learned from v3.2:
  COLD  -> full-field JUXTAPOSE immediately (unchanged instinct).
  HOT   -> one ranked exact pivot at a time (unchanged from v3.2).
  WARM  -> FIRST send one exact sentinel pivot. If it fits, cancel insurance
           before the other clones launch. Only a failed sentinel opens a
           diversified JUXTAPOSE wave, which then expands geometrically.

Thus JUXTAPOSE is a fallback for inability to predict, not a tax paid before we
know prediction failed. All clone compute remains charged. Parallel latency is
only a proxy. New v3.3 exam seeds live in a disjoint namespace.

Exact replay remains authority. P_VS_NP=OPEN.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

from experiments.mad_lab import adaptive_pippi_juxtapose_coldstart_v3 as v31
from experiments.mad_lab import adaptive_pippi_gauntlet_v2 as v2
from experiments.mad_lab import adaptive_pippi_pitstop_ladder as v1
from experiments.mad_lab import asymmetric_pq_track_relabelled as relabel
from experiments.mad_lab import keymaster_scalable_exact_root_labels as sl
from experiments.mad_lab import keymaster_scalable_exact_2cnf_transition as st
from experiments.mad_lab import keymaster_adviser_governance_v2 as gov

P_VS_NP = "OPEN"
SCHEMA = "JANUS/PIPPI/JUXTAPOSE-COLDSTART-GAUNTLET/v3.3.0"
FRESH_V33_BASE = 6_300_000_000
BASE_WARM_BOOTSTRAP = v31.warm_history_bootstrap

LATEST_V32_WEIGHTS = {
    "JGPT": 0.12932364784374833,
    "M2R": 0.004719558238860325,
    "SLIME": 0.3297363101880152,
    "SPIDER": 0.5362204837293763,
}

# generation, seed base, list of (p,q,serial,count,j_start,lesson)
PRIOR_GENERATION_SPECS = [
    ("V3_0", 3_700_000_000, [
        (1,1,1,4,0,"FORMATION"),(11,11,2,4,0,"RACE"),(21,21,3,4,0,"RACE"),
        (31,31,4,4,0,"RACE"),(44,47,5,4,0,"RACE"),(54,57,6,4,0,"FAILED_RACE"),
        (44,47,7,4,0,"RECOVERY_1"),(44,47,8,4,0,"RECOVERY_2"),(44,47,9,4,0,"RECOVERY_3"),
        (54,57,10,4,0,"FAILED_RETRY"),(250,250,11,4,0,"HARD_BOSS")
    ]),
    ("V3_1", 1_300_000_000, [
        # first three levels reused v2.4 serial/geometry, so j=0..3 were already in the 60-lesson warm set;
        # v3.1 generator skipped them and scored j=4..7.
        (1,1,1,4,4,"FORMATION"),(11,11,2,4,4,"RACE"),(21,21,3,4,4,"FAILED_RACE"),
        (11,11,4,4,0,"RECOVERY"),(21,21,5,4,0,"FAILED_RETRY"),(250,250,6,4,0,"HARD_BOSS")
    ]),
    ("V3_2", 4_900_000_000, [
        (1,1,1,4,0,"FORMATION"),(11,11,2,4,0,"RACE"),(21,21,3,4,0,"FAILED_RACE"),
        (11,11,4,4,0,"RECOVERY_1"),(11,11,5,4,0,"RECOVERY_2"),(11,11,6,4,0,"RECOVERY_3"),
        (21,21,7,4,0,"FAILED_RETRY"),(250,250,8,4,0,"HARD_BOSS")
    ]),
]


def _seed(base: int, p: int, q: int, serial: int, j: int) -> int:
    return base + serial * 100_003 + p * 1019 + q * 1031 + j * 43


def evolutionary_warm_bootstrap(used: set[str]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    memory, audit = BASE_WARM_BOOTSTRAP(used)
    if len(memory) != 60:
        raise AssertionError(("expected 60 base warm lessons", len(memory)))
    added = []
    generation_counts = {}
    duplicates = []
    for generation, seed_base, specs in PRIOR_GENERATION_SPECS:
        n0 = len(added)
        for p, q, serial, count, j_start, lesson in specs:
            for j in range(j_start, j_start + count):
                seed = _seed(seed_base, p, q, serial, j)
                cnf, _ = relabel.construct_relabelled(p, q, seed)
                e = sl.exact_track_episode_fast(cnf, p, q, seed, f"EVOLUTIONARY_HISTORY::{generation}::{lesson}", serial)
                if lesson == "HARD_BOSS":
                    cap = min(e["raw"])
                    e["local_stress_cap"] = cap
                    e["safe_indices"] = [i for i, x in enumerate(e["raw"]) if x <= cap]
                    e["historical_cap_policy"] = "EXACT_MIN_RAW_ONLY"
                if e["fingerprint"] in used:
                    duplicates.append({"generation": generation, "lesson": lesson, "seed": seed, "fingerprint": e["fingerprint"]})
                    continue
                used.add(e["fingerprint"]); memory.append(e); added.append(e)
        generation_counts[generation] = len(added) - n0

    # All expected scored episodes are new relative to the base 60.
    expected = {"V3_0": 44, "V3_1": 24, "V3_2": 32}
    if generation_counts != expected:
        raise AssertionError((generation_counts, expected, duplicates[:5]))
    if len(memory) != 160:
        raise AssertionError(("expected full 160-episode evolutionary warm start", len(memory)))

    gov.DEFAULT.clear(); gov.DEFAULT.update(LATEST_V32_WEIGHTS)
    audit = dict(audit)
    audit.update({
        "status": "EVOLUTIONARY_WARM_HISTORY_160_EXACT_EPISODES",
        "base_lessons": 60,
        "added_generation_lessons": generation_counts,
        "total_exact_lesson_formulas": len(memory),
        "duplicate_prior_lessons_skipped": len(duplicates),
        "latest_governance_prior_source": "V3_2_FINAL_WEIGHTS",
        "latest_governance_prior": dict(LATEST_V32_WEIGHTS),
        "negative_lessons_preserved": True,
        "new_exam_fingerprints_seen_during_bootstrap": 0,
        "P_VS_NP": P_VS_NP,
    })
    return memory, audit


def make_pq_stage_v33(p: int, q: int, stage_serial: int, count: int, used: set[str], source: str = "RUTHLESS_PQ_TRACK"):
    import time
    out=[]; metas=[]; j=0; t0=time.perf_counter()
    while len(out)<count:
        seed=_seed(FRESH_V33_BASE,p,q,stage_serial,j)
        cnf,meta=relabel.construct_relabelled(p,q,seed)
        e=v2.exact_pq_episode(cnf,p,q,seed,source,stage_serial)
        j+=1
        if e["fingerprint"] in used: continue
        used.add(e["fingerprint"]); out.append(e); metas.append(meta)
    return out,{"generation_wall_seconds":time.perf_counter()-t0,"metas":metas,"seed_namespace":FRESH_V33_BASE}


def _run_exact_wave(e: dict[str,Any], indices:list[int], wave:int) -> dict[str,Any]:
    cap=int(e["local_stress_cap"]); rows=[]; safe=[]
    for idx in indices:
        pivot=e["vars"][idx]
        out,stats=st.eliminate_var_capped_2cnf_exact(e["cnf"],pivot,cap)
        raw=int(stats["raw_units"]); pairs=int(stats.get("pairs",0)); fit=out is not None
        if fit:
            if not st.verify_transition_2cnf_exact(e["cnf"],pivot,out,cap): raise AssertionError("v3.3 exact replay failed")
            safe.append((raw,v1.stable_hash(e["tokens"][idx]),idx,pivot))
        rows.append({"wave":wave,"pivot_local_for_audit":pivot,"candidate_index":idx,"raw_units":raw,"pair_work":pairs,"fit":fit})
    chosen=min(safe)[2] if safe else None
    return {"rows":rows,"chosen_index":chosen,"checks":len(rows),"pairs":sum(x["pair_work"] for x in rows),"raw":sum(x["raw_units"] for x in rows),"lat_pairs":max((x["pair_work"] for x in rows),default=0),"lat_raw":max((x["raw_units"] for x in rows),default=0)}


def coverage_runtime_v33(e:dict[str,Any], learned_order:list[int], policy:dict[str,Any])->dict[str,Any]:
    n=len(learned_order); mode=policy["mode"]; confidence=float(policy["confidence"])
    if n==0: raise AssertionError("empty field")
    waves=[]
    if mode=="COLD_JUXTAPOSE":
        waves=[learned_order]
    elif mode=="HOT_PREDICTIVE":
        waves=[[i] for i in learned_order]
    elif mode=="WARM_JUXTAPOSE":
        # Sentinel first. Insurance does not launch unless exact says the leader failed.
        waves=[[learned_order[0]]]
        remaining=learned_order[1:]
        if remaining:
            t=max(0.0,min(1.0,(0.70-confidence)/0.25))
            frac=0.08+0.17*t  # after sentinel, first insurance wave 8-25% rather than v3.2's 8-30%
            size=max(2,min(len(remaining),math.ceil(n*frac)))
            cursor=0
            while cursor<len(remaining):
                take=min(len(remaining)-cursor,size)
                waves.append(remaining[cursor:cursor+take]); cursor+=take; size=max(size+1,size*2)
    else: raise AssertionError(mode)

    attempts=[]; total_checks=total_pairs=total_raw=0; lat_pairs=lat_raw=0; chosen_idx=None; used_waves=0
    for wi,indices in enumerate(waves,1):
        w=_run_exact_wave(e,indices,wi); used_waves+=1; attempts.extend(w["rows"])
        total_checks+=w["checks"]; total_pairs+=w["pairs"]; total_raw+=w["raw"]
        lat_pairs+=w["lat_pairs"]; lat_raw+=w["lat_raw"]
        if w["chosen_index"] is not None:
            chosen_idx=w["chosen_index"]; break
    if chosen_idx is None: raise AssertionError("field exhausted without safe pivot")
    return {
        "exact_checks":total_checks,"pair_work":total_pairs,"raw_units_sum":total_raw,
        "peak_raw_units":max([e["root_units"]]+[x["raw_units"] for x in attempts]),
        "chosen_first_pivot_local_for_audit":e["vars"][chosen_idx],"chosen_candidate_index":chosen_idx,
        "root_attempts":attempts,"exact_transition_verified":True,"coverage_mode":mode,
        "coverage_ratio":total_checks/n,"initial_coverage_ratio":len(waves[0])/n,
        "clone_count":total_checks,"available_pivots":n,"waves_used":used_waves,
        "parallel_pair_work_latency_proxy":lat_pairs,"parallel_raw_units_latency_proxy":lat_raw,
        "parallel_exact_wave_latency_proxy":used_waves,"total_compute_is_not_free":True,
        "parallel_latency_is_proxy_not_walltime":True,
        "sentinel_first":mode=="WARM_JUXTAPOSE",
        "insurance_launched":mode=="WARM_JUXTAPOSE" and used_waves>1,
        "scheduler_v33":{"HOT":"SEQUENTIAL_TOP1","WARM":"ONE_SENTINEL_THEN_INSURANCE_ON_EXACT_FAILURE","COLD":"FULL_FIELD_IMMEDIATE"}
    }


def _out_dir()->Path:
    if "--out-dir" not in sys.argv: raise AssertionError("--out-dir required")
    return Path(sys.argv[sys.argv.index("--out-dir")+1])


def main()->int:
    v31.warm_history_bootstrap=evolutionary_warm_bootstrap
    v31.coverage_runtime=coverage_runtime_v33
    v2.make_pq_stage=make_pq_stage_v33
    rc=v31.main()
    if rc!=0:return rc
    path=_out_dir()/"gauntlet-result.json"; result=json.loads(path.read_text())
    result["schema"]=SCHEMA
    result["controlled_change_v3_3"]={
        "evolutionary_not_clean_single_variable_AB":True,
        "warm_exact_lessons":160,
        "new_prior_lessons_include_v3_0_v3_1_v3_2":True,
        "WARM":"one exact sentinel then insurance only on sentinel failure",
        "HOT":"sequential top-1",
        "COLD":"immediate full-field JUXTAPOSE",
        "fresh_seed_namespace":FRESH_V33_BASE,
        "JGPT_architecture_changed":False,"SLIME_architecture_changed":False,"M2R_algorithm_changed":False,"SPIDER_algorithm_changed":False,
        "accounting_changed":False,"P_VS_NP":P_VS_NP,
    }
    fw=result["scientific_firewall"]
    fw["EVOLUTIONARY_WARM_START_160_EXACT_LESSONS"]=True
    fw["WARM_SENTINEL_BEFORE_INSURANCE"]=True
    fw["COLD_FULL_FIELD_REFLEX_PRESERVED"]=True
    fw["ALL_CLONE_COMPUTE_IS_CHARGED"]=True
    fw["P_VS_NP"]=P_VS_NP
    path.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"V3_3_POSTPROCESS":"PASS","frontier":result.get("official_frontier"),"stop_reason":result.get("stop_reason"),"boss_score":result.get("boss_250x250",{}).get("score"),"warm_lessons":result.get("bootstrap",{}).get("total_exact_lesson_formulas"),"P_VS_NP":P_VS_NP},indent=2,sort_keys=True))
    return 0

if __name__=="__main__": raise SystemExit(main())
