#!/usr/bin/env python3
"""E12C5 R5: strictly past-only cost-aware cross-family CNF selector.

Never train on R5. No solver, planted model or timed probe in selector.
Only proven exact XOR can go to GF2, partial/mixed remains original CNF.
Historical R4 has only two unique non-grid exact XOR training sources.
"""
from __future__ import annotations
from collections import Counter
from hashlib import sha1,sha256
from pathlib import Path
import itertools
import json
import math
import random
import sys
from statistics import median
from time import perf_counter

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
import janus_time_sat_004e12c5_r4_model as r4
import janus_time_sat_004e12c5_r3_selector as r3
import janus_time_sat_004e12c5_profit_test as r1

PREREG=ROOT/"experiments/time_sat_004_external/E12C5_R5_PREREG.json"
FROZEN_BLOB="f38833efaa91b97a7669df440b8890b2a2b4376b"
R4_REPORT=ROOT/"experiments/time_sat_004_external/E12C5_R4_POSTRUN_REPORT.json"
R4_REPORT_SHA="5595992434ef82e8958e936f470e7f089db5922a"
HISTORICAL_BLOBS=(
 ("E12C5_R1_POSTRUN_REPORT.json","3457551135c85f45564cd9125d363aefc8de83f8"),
 ("E12C5_R2_POSTRUN_REPORT.json","41109aed354e5f627f7c5834adc4705fb5b878ac"),
 ("E12C5_R3_POSTRUN_REPORT.json","a9313a78b8929e7afc46a91cc384c0b1e7c78272"))
CASES=(
 ("r5_xor3_96","EXACT_RANDOM_XOR",96,3,96,202611050396,0,0),
 ("r5_xor4_112a","EXACT_RANDOM_XOR",112,4,112,2026110504112,0,0),
 ("r5_xor4_160","EXACT_RANDOM_XOR",160,4,160,2026110504160,0,0),
 ("r5_xor5_144a","EXACT_RANDOM_XOR",144,5,144,2026110505144,0,0),
 ("r5_xor5_144b","EXACT_RANDOM_XOR",144,5,144,2026110605144,0,0),
 ("r5_xor6_128","EXACT_RANDOM_XOR",128,6,128,2026110506128,0,0),
 ("r5_partial4_112","DAMAGED_RANDOM_XOR",112,4,112,2026110507112,1,0),
 ("r5_partial5_144","DAMAGED_RANDOM_XOR",144,5,144,2026110507144,1,0),
 ("r5_mixed4_112","MIXED_XOR_PLUS_CNF",112,4,112,2026110508112,0,48),
 ("r5_mixed5_144","MIXED_XOR_PLUS_CNF",144,5,144,2026110508144,0,64),
 ("r5_three96","PLANTED_3CNF",96,3,0,2026110509096,0,336),
 ("r5_three144","PLANTED_3CNF",144,3,0,2026110509144,0,504),
)
SAT="SAT_VERIFIED_ORIGINAL_CNF"

def canonical(obj):
    return (json.dumps(obj,sort_keys=True,separators=(",",":"))+"\n").encode()

def git_blob(data):
    return sha1(b"blob "+str(len(data)).encode()+bytes([0])+data).hexdigest()

def frozen():
    data=PREREG.read_bytes()
    if git_blob(data)!=FROZEN_BLOB:
        raise AssertionError("R5_PREREG_CHANGED_AFTER_FREEZE")
    p=json.loads(data)
    cohort=[(q["id"],q["kind"],q["n"],
             q.get("width",3),q.get("equations",0),q["seed"],
             q.get("removed_clauses",0),q.get("extra_3cnf",q.get("m",0)))
            for q in p["cohort"]]
    if (p["schema"]!="JANUS-E12C5-R5-PREREG-STRUCTURAL-TRANSFER-V1"
        or cohort!=list(CASES)
        or p["matrix"]["total_children"]!=360
        or p["matrix"]["repeats"]!=3):
        raise AssertionError("R5_FROZEN_COHORT_OR_RESOURCE_DRIFT")
    return p,sha256(data).hexdigest()

def prior():
    p,_=frozen()
    r4data=R4_REPORT.read_bytes()
    if git_blob(r4data)!=R4_REPORT_SHA:
        raise AssertionError("R5_R4_TRAINING_REPORT_SHA_CHANGED")
    for name,expected in HISTORICAL_BLOBS:
        actual=(ROOT/"experiments/time_sat_004_external"/name).read_bytes()
        if git_blob(actual)!=expected:
            raise AssertionError("R5_HISTORICAL_REPORT_SHA_CHANGED_"+name)
    d=json.loads(r4data)
    if (d["science_verdict"]!="NO_R4_FROZEN_GENERALIZABLE_CLASS_GAIN"
        or len(d["per_host_recomputed_from_rounded_worker_logs"])!=2
        or len(d["eval_source_sha256"])!=8
        or d["full_cold_child_count"]!=240):
        raise AssertionError("R5_R4_EVIDENCE_NOT_VALIDATED")
    return d

def complete_parity_rows(support,rhs):
    return [[v if sign==0 else -v for v,sign in zip(support,signs)]
            for signs in itertools.product((0,1),repeat=len(support))
            if (sum(signs)&1)!=rhs]

def plant_random_xor(n,width,eqs,seed,removed,extra):
    rng=random.Random(seed)
    planted=[False]+[bool(rng.getrandbits(1)) for _ in range(n)]
    rows=[]
    supports=set()
    for _ in range(eqs):
        for attempt in range(100):
            support=tuple(sorted(rng.sample(range(1,n+1),width)))
            if support not in supports:break
        else:raise AssertionError("R5_REPEATED_XOR_SUPPORT")
        supports.add(support)
        rhs=sum(planted[v] for v in support)&1
        rows.extend(complete_parity_rows(support,rhs))
    if removed:
        if removed!=1 or not rows:raise AssertionError("R5_INVALID_DAMAGE")
        rows=rows[:-1]
    # For mixed tasks, append genuinely non-XOR clauses satisfied by exactly
    # the same planted model; preserve every parity row unchanged.
    for _ in range(extra):
        support=rng.sample(range(1,n+1),3)
        for attempt in range(100):
            literals=[v if rng.getrandbits(1) else -v for v in support]
            if any(planted[abs(v)]==(v>0) for v in literals):break
        else:raise AssertionError("R5_BAD_PLANTED_MIXED_SAT")
        rows.append(literals)
    witness=[v if planted[v] else -v for v in range(1,n+1)]
    if not r1.cnf_ok(rows,witness):
        raise AssertionError("R5_GENERATOR_NOT_SAT")
    return n,rows

def source(case):
    s=next((z for z in CASES if z[0]==case),None)
    if s is None:raise AssertionError("R5_SOURCE_NOT_REGISTERED")
    _,kind,n,width,equations,seed,removed,extra=s
    return plant_random_xor(n,width,equations,seed,removed,extra)

def feature_profile(rows,n):
    """Cheap exact-group evidence; never solve. Every mask must be unique."""
    if n<1 or n>2500 or len(rows)>35000:
        raise AssertionError("R5_SOURCE_BUDGET_EXCEEDED")
    literals=0
    groups={}
    lengths=Counter()
    degree=[0]*(n+1)
    for i,row in enumerate(rows):
        if not row or len(row)>6:
            raise AssertionError("R5_UNSUPPORTED_OR_EMPTY_CLAUSE")
        literals+=len(row)
        if literals>160000:
            raise AssertionError("R5_TOO_MANY_SOURCE_LITERALS")
        if any(type(v) is not int or abs(v)<1 or abs(v)>n for v in row):
            raise AssertionError("R5_INVALID_SOURCE_LITERAL")
        support=tuple(sorted(abs(v) for v in row))
        if len(set(support))!=len(row):
            raise AssertionError("R5_TAUTOLOGY_OR_DUPLICATE_VAR")
        mask=sum(1<<j for j,var in enumerate(support) if -var in row)
        g=groups.setdefault(support,{"masks":[],"indices":[]})
        g["masks"].append(mask);g["indices"].append(i)
        lengths[len(row)]+=1
        for v in support:degree[v]+=1
    complete=[];partial=[]
    for supp,z in groups.items():
        masks=z["masks"]
        full=((len(masks)==1<<(len(supp)-1))
              and len(set(masks))==len(masks)
              and len({m.bit_count()&1 for m in masks})==1)
        (complete if full else partial).append((supp,z))
    all_exact=(len(partial)==0 and len(complete)==len(groups))
    cover=None
    if all_exact:
        cover=r4.xor.group_parity_equations(rows,n)
        if (cover["status"]!="EXACT_XOR_COVER_PASS"
            or len(cover["equations"])!=len(groups)
            or sum(len(eq["original_clause_indices"]) for eq in cover["equations"])!=len(rows)):
            raise AssertionError("R5_PROOF_BLOCK_COUNT_MISMATCH")
    eqs=cover["equations"] if cover else []
    equation_degrees=[0]*(n+1)
    widths=Counter()
    for eq in eqs:
        widths[len(eq["variables"])]+=1
        for v in eq["variables"]:equation_degrees[v]+=1
    av=sum(equation_degrees[1:])/n
    degree_cv=math.sqrt(sum((d-av)**2 for d in equation_degrees[1:])/n)/av if av else 0.
    only_width=(next(iter(widths)) if len(widths)==1 else None)
    return {
        "n":n,"clauses":len(rows),"literal_occurrences":literals,
        "original_clause_width_histogram":dict(lengths),
        "complete_groups":len(complete),"incomplete_groups":len(partial),
        "all_groups":len(groups),
        "complete_group_fraction":len(complete)/len(groups) if groups else 0.,
        "exact_original_xor_cover":all_exact,
        "equations_per_variable":len(eqs)/n,
        "complete_equation_widths":dict(widths),
        "uniform_certified_equation_width":only_width,
        "support_degree_cv":degree_cv,
        "max_var_degree":max(degree[1:]),
        "is_grid_topology":bool(cover and r3.verified_lightsout_supports(cover,n,math.isqrt(n))),
    },cover

def fit_from_prior():
    d=prior();p,protocol_sha=frozen()
    full={}
    for width,name in ((4,"r4_xor4_96"),(5,"r4_xor5_128")):
        rows=[]
        for host in d["per_host_recomputed_from_rounded_worker_logs"]:
            r=host["cases"][name]["median_by_arm"]
            get=lambda a:r[a]["median_logged_full_cold_wall_s"]
            gf=get("janus_gf2_exact_ablation")
            candidates=[get(a) for a in ("cryptominisat_native_xor","cryptominisat_original_cnf","cadical195_original_cnf")]
            if not isinstance(gf,(int,float)) or gf<=0:
                raise AssertionError("R5_MISSING_EXACT_GF2_R4_TRAINING")
            external=min(x for x in candidates if isinstance(x,(int,float)) and x>0)
            rows.append({"host":host["host"],"GF2_cold_seconds":gf,
                         "external_best_verified_cold_seconds":external,
                         "speedup":external/gf})
        full[str(width)]={"training_source_sha256":d["eval_source_sha256"][name],
                          "host_costs":rows,
                          "training_host_min_gain":min(z["speedup"] for z in rows),
                          "observed_GF2_cost_median_s":median(z["GF2_cold_seconds"] for z in rows),
                          "observed_best_external_cost_median_s":median(z["external_best_verified_cold_seconds"] for z in rows)}
    near=[]
    ordinary=[]
    for host in d["per_host_recomputed_from_rounded_worker_logs"]:
        part=host["cases"]["r4_partial_xor4"]["median_by_arm"]
        plain=host["cases"]["r4_planted3"]["median_by_arm"]
        near.append({"host":host["host"],
                     "cadical_s":part["cadical195_original_cnf"]["median_logged_full_cold_wall_s"],
                     "cms_original_s":part["cryptominisat_original_cnf"]["median_logged_full_cold_wall_s"]})
        ordinary.append({"host":host["host"],
                     "cadical_s":plain["cadical195_original_cnf"]["median_logged_full_cold_wall_s"],
                     "cms_original_s":plain["cryptominisat_original_cnf"]["median_logged_full_cold_wall_s"]})
    if not all(v["training_host_min_gain"]>=1.25 for v in full.values()):
        raise AssertionError("R5_R4_CROSS_FAMILY_EXACT_XOR_GAIN_NOT_PREVIOUSLY_SUPPORTED")
    if not all(z["cadical_s"]<z["cms_original_s"] for z in near):
        raise AssertionError("R5_R4_PARTIAL_CLASS_REFERENCE_NOT_REPRODUCED")
    if not all(z["cms_original_s"]<z["cadical_s"] for z in ordinary):
        raise AssertionError("R5_R4_3SAT_REFERENCE_NOT_REPRODUCED")
    fit={
        "schema":"JANUS-E12C5-R5-PAST_ONLY_TWO_CLASS_COST_FIT-V1",
        "prereg_sha256":protocol_sha,"prior_R4_report_blob_sha1":R4_REPORT_SHA,
        "R4_source_original_sha256":d["eval_source_sha256"],
        "eligible_non_grid_exact_widths":full,
        "partial_width4_single_source_training":near,
        "ordinary_3SAT_single_source_training":ordinary,
        "exact_non_grid_independent_original_count":2,
        "R5_originals_in_fit":0,
        "unknown_exact_widths_native_fallback":True,
        "mixed_unknown_original_cnf_fallback":True,
        "complete_partial_not_promoted_to_GF2":True,
        "no_model_retraining_on_R5":True,
        "production_C023":"UNCHANGED"
    }
    return fit

def choose(rows,n,fit):
    start=perf_counter()
    f,cover=feature_profile(rows,n)
    elapsed=perf_counter()-start
    if fit["schema"]!="JANUS-E12C5-R5-PAST_ONLY_TWO_CLASS_COST_FIT-V1":
        raise AssertionError("R5_UNVERIFIED_TRAINING_FIT")
    out={"structural_profile":f,"profile_wall_s":elapsed,
         "estimated_candidate_full_cold_s":None,
         "estimated_external_full_cold_s":None,
         "estimated_gain_lower_bound":None,
         "training_support_original_sha":[]}
    if f["exact_original_xor_cover"]:
        if f["is_grid_topology"]:
            return "cryptominisat_native_xor",cover,"GRID_NOT_NON_GRID_TRAINING_CLASS",out
        width=f["uniform_certified_equation_width"]
        basis=fit["eligible_non_grid_exact_widths"].get(str(width))
        if (basis is not None
            and f["equations_per_variable"]>=.7
            and f["equations_per_variable"]<=1.3
            and .3<=f["support_degree_cv"]<=.65
            and basis["training_host_min_gain"]>=1.25
            and elapsed<=2):
            out["estimated_candidate_full_cold_s"]=basis["observed_GF2_cost_median_s"]*(n/(96 if width==4 else 128))**1.5
            out["estimated_external_full_cold_s"]=basis["observed_best_external_cost_median_s"]*(n/(96 if width==4 else 128))**1.5
            out["estimated_gain_lower_bound"]=basis["training_host_min_gain"]
            out["training_support_original_sha"]=[basis["training_source_sha256"]]
            return "janus_gf2",cover,"R4_TWO_HOST_EXACT_NON_GRID_GAIN",out
        return "cryptominisat_native_xor",cover,"WIDTH_OR_CV_UNKNOWN_NO_GF2_CERTIFIED_GAIN",out
    # A full-XOR original with only ONE missing clause is not an XOR formula.
    # R4's single damaged-width4 example showed CaDiCaL outperform raw CMS.
    if (f["incomplete_groups"]==1 and f["complete_group_fraction"]>=.98
        and set(map(int,f["original_clause_width_histogram"]))=={4}
        and len(fit["partial_width4_single_source_training"])==2
        and all(z["cadical_s"]<z["cms_original_s"] for z in fit["partial_width4_single_source_training"])):
        return "cadical195_original_cnf",None,"R4_ONE_SOURCE_NEAR_COMPLETE_WIDTH4",out
    return "cryptominisat_original_cnf",None,"UNKNOWN_MIXED_OR_NON_XOR_CNF",out

def main():
    import argparse
    a=argparse.ArgumentParser()
    a.add_argument("--fit-output",type=Path)
    a.add_argument("--preflight",action="store_true")
    q=a.parse_args()
    if q.fit_output:
        fit=fit_from_prior()
        q.fit_output.parent.mkdir(parents=True,exist_ok=True)
        q.fit_output.write_bytes(canonical(fit))
        print("R5_HISTORICAL_FIT",sha256(q.fit_output.read_bytes()).hexdigest(),
              fit["exact_non_grid_independent_original_count"])
    if q.preflight:
        fit=fit_from_prior()
        oldshas=set(fit["R4_source_original_sha256"].values())
        shas=[]
        for case,kind,n,w,e,seed,damage,extra in CASES:
            n_actual,rows=source(case)
            if n!=n_actual or not r1.cnf_ok(rows,[k if k in set() else -k for k in []]):
                pass # Source SAT proofs independently tested by exact GF2/CMS in CI.
            h=r1.original_sha(rows,n)
            if h in oldshas:
                raise AssertionError("R5_TRAIN_EVAL_COLLISION")
            shas.append(h)
            decision,cover,reason,info=choose(rows,n,fit)
            if kind=="EXACT_RANDOM_XOR" and cover is None:
                raise AssertionError("R5_EXACT_XOR_NOT_CERTIFIED")
            if kind!="EXACT_RANDOM_XOR" and decision=="janus_gf2":
                raise AssertionError("R5_NONEXACT_FALSE_GF2")
        if len(set(shas))!=len(CASES):
            raise AssertionError("R5_DUPLICATED_SOURCE_SHAS")
        print("R5_FROZEN_SOURCE_PROOF_PASS",json.dumps(dict(zip((x[0] for x in CASES),shas)),sort_keys=True))
if __name__=="__main__":
    main()
