#!/usr/bin/env python3
"""JANUS / JUXTAPOSE x67: controlled adaptive exact-pivot search + XOR extraction.

Source lineage: JANUS_Adaptive_JUXTAPOSE_Proof_Search_v1.0.0_PLUS_ROOSTERS_v5.1.json
(canonical JUXTAPOSE SHA256 6eda78e9191417d91a76484dd8203de7622dfb7db353c8463d8ae8a36e483577).
The communication extension v5.1 is NOT a SAT algorithm; only general
search-governance principles transfer: COLD/WARM/HOT, exact receipts,
unknown->widen, delayed learning, preserve failed/null outcomes.

67 *separate*, deterministic synthetic original CNFs, with 45 development
episodes and 22 NEVER-TRAINED prospective internal holdout episodes.
Every candidate clause is the exact resolvent of source clauses and receives
an independent original-source resolution-DAG replay. No UNSAT assertions,
no external witness, no solver time/speedup claim, no P=NP claim.
"""
from __future__ import annotations
from collections import defaultdict
from hashlib import sha256
import argparse
import json
from pathlib import Path
import random
import sys

HERE=Path(__file__).resolve().parent
DIRECT=HERE.parent/"direct"
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(DIRECT))

from janus_time_sat_004d1_xor import source_digest
from janus_time_sat_004d4d_paged_support import extract_paged_mixed_xor
from janus_time_sat_004d6_bounded_resolution import exact_resolvent
from janus_time_sat_004d6_replay import replay_all
from janus_time_sat_004d6_rank_audit import derive_keys
from janus_time_sat_004d7_rank_gate import independence_record
from janus_time_sat_004d8_sat_gate import certified_model
from time_sat_004d9b_up_cleanroom_baseline import baseline_case,rank as clean_rank

SEED=20261114
CYCLES=67
TRAIN_CYCLES=45
MAX_PIVOTS=9
MAX_PAIRS_PER_PIVOT=64
MAX_RESOLVENTS=64
ALGORITHM_LINEAGE_SHA256="6eda78e9191417d91a76484dd8203de7622dfb7db353c8463d8ae8a36e483577"

def parity_clauses(variables,rhs):
    """Full standard CNF block for xor(variables) == rhs."""
    from itertools import product
    rows=[]
    for bits in product((0,1),repeat=len(variables)):
        if sum(bits)%2==rhs:continue
        rows.append([(-v if b else v) for v,b in zip(variables,bits)])
    return rows

def source_case(cycle):
    """Four related but distinct planted-SAT families, ID and sign shuffled."""
    rng=random.Random(SEED+cycle*27011)
    n=9
    pivots=rng.sample(list(range(1,n+1)),4)
    xyz=pivots[:3];guard=pivots[3]
    truth={v:bool(rng.randrange(2)) for v in range(1,n+1)}
    rhs=sum(int(truth[v]) for v in xyz)%2
    base=parity_clauses(xyz,rhs)
    kind=("HIDDEN_SWITCH","HIDDEN_SWITCH","GUARDED_UNIT","EXPLICIT_XOR","MIXED_SWITCH")[cycle%5]
    if kind in ("HIDDEN_SWITCH","MIXED_SWITCH"):
        rows=[[guard]+row for row in base]+[[-guard]+row for row in base]
    elif kind=="GUARDED_UNIT":
        # Guard false is forced by unit clause, so UP already recovers the XOR.
        truth[guard]=False
        rows=[[guard]+row for row in base]+[[-guard]]
    else:
        rows=[row[:] for row in base]
    decoys=[v for v in range(1,n+1) if v not in pivots]
    if kind=="MIXED_SWITCH":
        for _ in range(5):
            v=rng.sample(decoys,3)
            row=[x if rng.randrange(2) else -x for x in v]
            if not any(truth[abs(l)]==(l>0) for l in row):
                row[0] *= -1
            rows.append(row)
    rng.shuffle(rows)
    # Duplicate synthetic decoy clauses are removed deterministically while
    # the complete XOR source blocks remain intact; a repeated clause carries
    # no new logical information, and a duplicated ID is never used as evidence.
    unique={}
    for row in rows:
        canonical=tuple(sorted(set(row),key=lambda x:(abs(x),x<0)))
        unique.setdefault(canonical,None)
    rows=[list(row) for row in unique]
    sat=[v if truth[v] else -v for v in range(1,n+1)]
    if certified_model(rows,n,sat)["status"]!="SAT_VERIFIED_EVERY_ORIGINAL_CLAUSE":
        raise AssertionError("Synthetic source model invalid")
    return {"cycle":cycle,"family":kind,"n":n,"rows":rows,
            "SAT_model":sat,"original_source_logical_sha256":source_digest(rows,n)}

def feature(rows,pivot):
    pos=[(i,tuple(row)) for i,row in enumerate(rows) if pivot in row]
    neg=[(i,tuple(row)) for i,row in enumerate(rows) if -pivot in row]
    pair_work=len(pos)*len(neg)
    available=(bool(pos) and bool(neg) and pair_work<=MAX_PAIRS_PER_PIVOT
               and len(pos)<=8 and len(neg)<=8)
    len3plus=sum(len(c)>=3 for _,c in pos+neg)
    unit=sum(len(c)==1 for _,c in pos+neg)
    four=sum(len(c)==4 for _,c in pos+neg)
    bucket=(min(8,len(pos)),min(8,len(neg)),int(unit>0),min(8,four))
    # Unsigned structural data only. NEVER numeric pivot id or future labels.
    priority=(int(available),-abs(len(pos)-len(neg)),four,unit,-pair_work,len3plus)
    return {"pivot":pivot,"pos":pos,"neg":neg,"pair_work":pair_work,
            "eligible":available,"bucket":bucket,"priority":priority}

def exact_probe(rows,n,pivot,known,up_equations):
    f=feature(rows,pivot)
    raw_pairs=f["pair_work"]
    if not f["eligible"]:
        return {"pivot":pivot,"status":"ABSTAIN_INELIGIBLE_PIVOT",
                "pair_work":raw_pairs,"new_keys":[],"rank_delta":0,"rank_delta_over_UP":0}
    source_count=len(rows)
    seen={tuple(c) for c in rows}
    proof=[]
    for i,left in f["pos"]:
        for j,right in f["neg"]:
            # The source-proven JANUS exact resolver verifies every resolved clause.
            resolved=exact_resolvent(left,right,pivot)
            if resolved is None or resolved in seen:continue
            if len(proof)>=MAX_RESOLVENTS:
                return {"pivot":pivot,"status":"ABSTAIN_RESOLVENT_BUDGET",
                        "pair_work":raw_pairs,"new_keys":[],"rank_delta":0,"rank_delta_over_UP":0}
            seen.add(resolved)
            proof.append({"id":source_count+len(proof),"parents":[i,j],
                          "pivot":pivot,"clause":list(resolved)})
    evidence={
        "status":"SOURCE_RESOLUTION_BOUNDED_PASS","source_n":n,
        "source_clauses":source_count,"original_clause_count_retained":source_count,
        "source_logical_sha256":source_digest(rows,n),
        "resolution_proof_DAG":proof,"new_witness_examples":[]
    }
    candidates=derive_keys(rows,n,evidence,known)
    evidence["new_complete_xor_sign_mask_equations"]=len(candidates)
    if not replay_all(rows,n,evidence):
        raise AssertionError("Independent exact original-source proof DAG replay rejected pivot")
    r=independence_record(known,candidates,n)
    delta_up=clean_rank(up_equations|candidates,n)-clean_rank(up_equations,n)
    return {"pivot":pivot,"status":"EXACT_SOURCE_PROOF_REPLAY_PASS",
            "pair_work":raw_pairs,"new_resolvents":len(proof),
            "new_keys":[{"variables":list(v),"rhs":rhs} for v,rhs in sorted(candidates)],
            "rank_delta":r["independent_new_coefficient_rank"],
            "rank_delta_over_UP":delta_up}

def model_key(features):
    f=features
    return ",".join(str(z) for z in f["bucket"])

def trained_rank(features,experience):
    key=model_key(features)
    hits,total=experience.get(key,(0,0))
    # Laplace smoothing; cannot use the current cycle's exact label.
    confidence=(hits+1)/(total+2)
    return (confidence,features["priority"])

def run_order(rows,n,order,mode,known,up_equations,cache):
    steps=[]
    first=None
    for pivot in order:
        if pivot not in cache:
            cache[pivot]=exact_probe(rows,n,pivot,known,up_equations)
        result=cache[pivot]
        steps.append(result)
        if first is None and result["rank_delta_over_UP"]>0:
            first=result
            # In JUXTAPOSE COLD mode, all root directions are checked.
            if mode!="COLD":break
    return {"mode":mode,
            "exact_pivot_checks":len(steps),
            "symbolic_pair_work":sum(x["pair_work"] for x in steps),
            "new_rank_over_UP_first_hit":first["rank_delta_over_UP"] if first else 0,
            "first_hit_pivot":first["pivot"] if first else None,
            "steps":steps}

def experiment():
    experience={}   # only previous TRAIN episodes can update
    family_counts=defaultdict(int)
    records=[]
    for index in range(CYCLES):
        case=source_case(index)
        n,rows=case["n"],case["rows"]
        extractor=extract_paged_mixed_xor(rows,n)
        if extractor["status"]!="SOURCE_PARTITION_VERIFIED":
            raise AssertionError("Exact source extractor failed")
        known={(tuple(eq["variables"]),eq["rhs"]) for eq in extractor["equations"]}
        up=baseline_case(n,rows)
        if up["status"]!="UP_AND_COMPLETE_SIGNMASK_XOR_BASELINE_READY":
            raise AssertionError("Reference UP baseline failed unexpectedly")
        up_equations={(tuple(e["variables"]),e["rhs"]) for e in up["baseline_equations"]}
        features=[feature(rows,p) for p in range(1,n+1)]
        rng=random.Random(SEED^((index+1)*1117))
        random_order=list(range(1,n+1));rng.shuffle(random_order)
        # Side-effect-free ranked proposals; no present exact outcome in ranking.
        ranked=sorted(features,key=lambda f:trained_rank(f,experience),reverse=True)
        ranked_order=[x["pivot"] for x in ranked]
        fp=(len(rows),sum(len(row)==1 for row in rows),sum(len(row)==4 for row in rows))
        support=family_counts[fp]
        if support<3:mode="COLD"
        elif support<8:mode="WARM"
        else:mode="HOT"
        frozen=(index>=TRAIN_CYCLES)
        # Single independent mathematical proof per candidate, shared only for
        # diagnostic computation; virtual effort counts probes per policy.
        cache={}
        hybrid=run_order(rows,n,ranked_order,mode,known,up_equations,cache)
        static=run_order(rows,n,list(range(1,n+1)),"STATIC",known,up_equations,cache)
        random_ctrl=run_order(rows,n,random_order,"RANDOM",known,up_equations,cache)
        # EXACT mathematical equivalence: all proof DAGs source-bound. For each
        # policy, a discovered 'hit' cannot be merely a neural prediction.
        if (hybrid["new_rank_over_UP_first_hit"]>0)!=(static["new_rank_over_UP_first_hit"]>0):
            raise AssertionError("Fall-back exact completeness vs static changed")
        if not frozen:
            family_counts[fp]+=1
            for step in hybrid["steps"]:
                bucket=model_key(feature(rows,step["pivot"]))
                h,t=experience.get(bucket,(0,0))
                experience[bucket]=(h+int(step["rank_delta_over_UP"]>0),t+1)
        records.append({
            "cycle":index+1,"phase":"FROZEN_INTERNAL_HOLDOUT" if frozen else "DEVELOPMENT_TRAIN",
            "family_for_reporting_only":case["family"],
            "source_SHA256":case["original_source_logical_sha256"],
            "mode":mode,"fingerprint_support_before_current":support,
            "features_from_source_only":True,
            "actual_exact_results_used_for_ranking":False,
            "original_SAT_model_checked":True,
            "UP_reference_equation_count":len(up_equations),
            "hybrid":{k:v for k,v in hybrid.items() if k!="steps"},
            "static":{k:v for k,v in static.items() if k!="steps"},
            "random":{k:v for k,v in random_ctrl.items() if k!="steps"},
            "proof_steps":{str(p):{"status":x["status"],
                "derived_XOR_count":len(x["new_keys"]),
                "rank_increment_over_UP":x["rank_delta_over_UP"],
                "pair_work":x["pair_work"]}
                for p,x in cache.items()},
            "no_external_holdout_claim":True
        })
    assert len(records)==67
    assert len({r["source_SHA256"] for r in records})==67
    def summarize(seq,which):
        return {
            "cycles":len(seq),
            "exact_mathematical_hits":sum(r[which]["new_rank_over_UP_first_hit"]>0 for r in seq),
            "total_exact_pivot_checks":sum(r[which]["exact_pivot_checks"] for r in seq),
            "total_symbolic_pair_work":sum(r[which]["symbolic_pair_work"] for r in seq),
            "average_checks":sum(r[which]["exact_pivot_checks"] for r in seq)/len(seq),
        }
    slices={"train":records[:TRAIN_CYCLES],"holdout":records[TRAIN_CYCLES:]}
    summary={
        part:{arm:summarize(sub,arm) for arm in ("hybrid","static","random")}
        for part,sub in slices.items()
    }
    if any(summary[part]["hybrid"]["exact_mathematical_hits"]!=
           summary[part]["static"]["exact_mathematical_hits"] for part in summary):
        raise AssertionError("Exact hit coverage changed")
    # This exported fit contains data from cycles 1..45 ONLY. All holdout
    # evaluation messages are excluded from the solver's frozen policy.
    model={
        "schema":"JANUS-JUXTAPOSE67-PAST-ONLY-PIVOT-FIT-V1",
        "seed":SEED,"training_cycles":TRAIN_CYCLES,
        "training_source_shas":[r["source_SHA256"] for r in records[:TRAIN_CYCLES]],
        "experience":{key:list(value) for key,value in sorted(experience.items())},
        "family_counts":{",".join(map(str,key)):value for key,value in sorted(family_counts.items())},
        "heldout_cycle_results_in_fit":False,
        "prior_only_authority":True,
        "source_lineage_SHA256":ALGORITHM_LINEAGE_SHA256
    }
    return {
        "schema":"JANUS-JUXTAPOSE-X67-SAT-XOR-SYNTHETIC-SOURCE-BOUND-V1",
        "lineage":{
          "parent":"JANUS_Adaptive_JUXTAPOSE_Proof_Search_v1.0.0_PLUS_ROOSTERS_v5.1.json",
          "canonical_original_sha256":ALGORITHM_LINEAGE_SHA256,
          "transfer_scope":"SEARCH_POLICY_ONLY_NOT_COMMUNICATIONS_ADAPTER"
        },
        "cycles":CYCLES,"development":TRAIN_CYCLES,"internal_frozen_holdout":CYCLES-TRAIN_CYCLES,
        "current_episode_training":"FORBIDDEN","holdout_feedback_learning":"FORBIDDEN",
        "truth_authority":"EXACT_SOURCE_RESOLUTION_DAG_AND_INDEPENDENT_REPLAY",
        "baseline":"SOURCE_UNIT_PROPAGATION_PLUS_COMPLETE_SIGNMASK_XOR",
        "metrics":"SYMBOLIC_EXACT_CHECKS_AND_PAIR_WORK_NOT_WALL_TIME",
        "single_admin_synthetic":"YES",
        "external_science_gate":"OPEN",
        "R6_FROZEN_SCIENCE_GATE":"NOT_PASSED_UNCHANGED",
        "production_C023":"UNCHANGED",
        "summary":summary,
        "all_records":records,
        "frozen_model":model
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path)
    ap.add_argument("--model-out",type=Path)
    args=ap.parse_args()
    data=experiment()
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(data,sort_keys=True,indent=2)+"\n")
    if args.model_out:
        args.model_out.parent.mkdir(parents=True,exist_ok=True)
        args.model_out.write_text(json.dumps(data["frozen_model"],sort_keys=True,indent=2)+"\n")
    print(json.dumps({"status":"SYNTHETIC_67_CYCLES_PROOF_REPLAY_PASS",
                      "summary":data["summary"]},sort_keys=True))
if __name__=="__main__":
    main()
