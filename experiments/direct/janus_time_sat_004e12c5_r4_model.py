#!/usr/bin/env python3
"""JANUS E12C5 R4. Frozen past-only, cost-aware structural CNF prediction.

This module never solves an SAT instance while fitting or deciding. Proof of
exact XOR is only structural. All runtime results come from pre-R4 R1-R3.
The predictor is allowed to refuse GF2 whenever risk is unsupported.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from hashlib import sha1,sha256
import itertools
import json
import math
from pathlib import Path
import random
from statistics import median

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
import sys
sys.path.insert(0,str(HERE))
import janus_time_sat_004e12c5_profit_test as r1
import janus_time_sat_004e12c5_r2_selector as r2
import janus_time_sat_004e12c5_r3_selector as r3
import janus_time_sat_004d1_xor as xor
xor.MAX_LITERALS=160000
xor.MAX_ROWS=35000
xor.MAX_N=2500

PFILE=ROOT/"experiments/time_sat_004_external/E12C5_R4_PREREG.json"
FROZEN_BLOB="19a4cd0bec76c2f916cdf661edcaecccace1d7de"
PAST=[
("E12C5_R1_POSTRUN_REPORT.json","3457551135c85f45564cd9125d363aefc8de83f8"),
("E12C5_R2_POSTRUN_REPORT.json","41109aed354e5f627f7c5834adc4705fb5b878ac"),
("E12C5_R3_POSTRUN_REPORT.json","a9313a78b8929e7afc46a91cc384c0b1e7c78272")]
CASES=(
("r4_lo_13","LIGHTSOUT_PLANTED_SAT",13,202611031413),
("r4_lo_31","LIGHTSOUT_PLANTED_SAT",31,202611031431),
("r4_lo_43a","LIGHTSOUT_PLANTED_SAT",43,202611031443),
("r4_lo_43b","LIGHTSOUT_PLANTED_SAT",43,202611041443),
("r4_xor4_96","RANDOM_PLANTED_XOR_COMPLETE",96,202611031496),
("r4_xor5_128","RANDOM_PLANTED_XOR_COMPLETE",128,2026110315128),
("r4_partial_xor4","RANDOM_PLANTED_XOR_WITH_ONE_CLAUSE_REMOVED",96,202611031496),
("r4_planted3","PLANTED_3SAT_NON_XOR",96,2026110315396),
)
FEAT_KEYS=("log1p_n","log1p_clauses","log1p_literal_occurrences",
           "mean_original_clause_width","certified_equations_per_variable",
           "mean_certified_support_width","support_variable_degree_CV",
           "rhs_bias_from_half","is_proven_square_lightsout_topology")
SCALE=(2.,2.,2.,3.,2.,6.,2.,1.,1/3)
K=5
SAT="SAT_VERIFIED_ORIGINAL_CNF"

def canonical(value):
    return (json.dumps(value,sort_keys=True,separators=(",",":"))+"\n").encode()

def blob_sha(data):
    return sha1(b"blob "+str(len(data)).encode()+bytes([0])+data).hexdigest()

def load_frozen():
    data=PFILE.read_bytes()
    if blob_sha(data)!=FROZEN_BLOB:
        raise AssertionError("R4_FROZEN_PROTOCOL_BLOB_CHANGED")
    j=json.loads(data)
    if j["schema"]!="JANUS-E12C5-R4-PREREG-CNF-RISK-V1":
        raise AssertionError("R4_BAD_PROTOCOL")
    if tuple(j["training_policy"]["explicit_frozen_model"]["structural_features"])!=FEAT_KEYS:
        raise AssertionError("R4_FEATURE_SPEC_CHANGED")
    if [(q["id"],q["kind"],q.get("side",q.get("n")),q["seed"])
          for q in j["evaluation_cohort"]]!=list(CASES):
        raise AssertionError("R4_NEW_CASE_DEFINITION_DRIFT")
    if [(x["path"].rsplit("/",1)[-1],x["git_blob_sha1"])
        for x in j["training_sources"]]!=PAST:
        raise AssertionError("R4_TRAINING_COHORT_CHANGED")
    return j,sha256(data).hexdigest()

def load_prior():
    p,_=load_frozen()
    out=[]
    for name,expected in PAST:
        b=(ROOT/"experiments/time_sat_004_external"/name).read_bytes()
        if blob_sha(b)!=expected:
            raise AssertionError("R4_PRIOR_TRAINING_EVIDENCE_SHA_DRIFT "+name)
        out.append(json.loads(b))
    if (out[0]["original_gate"]["verdict"]!="NOT_PASSED"
        or out[1]["scientific_status"]!="FROZEN_R2_SELECTOR_GATE_NOT_PASSED"
        or out[2]["science_verdict"]!="NO_FROZEN_R3_STRUCTURAL_SELECTOR_GAIN_ESTABLISHED"):
        raise AssertionError("R4_HISTORY_NEGATIVE_OUTCOME_TAMPERED")
    return out

def grid(side,seed):
    if side not in (13,31,43) or not isinstance(seed,int):
        raise AssertionError("R4_NEW_GRID_NOT_REGISTERED")
    rng=random.Random(seed)
    n=side*side
    planted=[False]+[bool(rng.getrandbits(1)) for _ in range(n)]
    rows=[]
    for y in range(side):
        for x in range(side):
            neighbors=((y,x),(y-1,x),(y+1,x),(y,x-1),(y,x+1))
            support=sorted(1+yy*side+xx for yy,xx in neighbors
                           if 0<=yy<side and 0<=xx<side)
            rhs=sum(planted[v] for v in support)%2
            for bits in itertools.product((0,1),repeat=len(support)):
                if sum(bits)%2!=rhs:
                    rows.append([v if not sign else -v for v,sign in zip(support,bits)])
    witness=[i if planted[i] else -i for i in range(1,n+1)]
    if not r1.cnf_ok(rows,witness):
        raise AssertionError("R4_GRID_CONSTRUCTION_NOT_SAT")
    return n,rows

def parity_rows(support,rhs):
    rows=[]
    for signs in itertools.product((0,1),repeat=len(support)):
        if sum(signs)%2!=rhs:
            rows.append([v if not sign else -v for v,sign in zip(support,signs)])
    return rows

def planted_xor(n,width,num_equations,seed):
    rng=random.Random(seed)
    assignment=[False]+[bool(rng.getrandbits(1)) for _ in range(n)]
    seen=set()
    rows=[]
    for i in range(num_equations):
        for attempt in range(100):
            support=tuple(sorted(rng.sample(range(1,n+1),width)))
            if support not in seen:
                break
        else:raise AssertionError("R4_XOR_SOURCE_DUPLICATE_SUPPORTS")
        seen.add(support)
        rhs=sum(assignment[v] for v in support)%2
        rows.extend(parity_rows(support,rhs))
    witness=[i if assignment[i] else -i for i in range(1,n+1)]
    if not r1.cnf_ok(rows,witness):
        raise AssertionError("R4_RANDOM_XOR_SAT_WITNESS_INVALID")
    return n,rows

def planted_three_sat(n,m,seed):
    rng=random.Random(seed)
    assignment=[False]+[bool(rng.getrandbits(1)) for _ in range(n)]
    rows=[]
    for _ in range(m):
        vs=rng.sample(range(1,n+1),3)
        for attempt in range(100):
            clause=[v if rng.getrandbits(1) else -v for v in vs]
            if any(assignment[abs(l)]==(l>0) for l in clause):
                break
        else:raise AssertionError("R4_PLANTED_SAT_MISCONSTRUCTION")
        rows.append(clause)
    witness=[i if assignment[i] else -i for i in range(1,n+1)]
    if not r1.cnf_ok(rows,witness):
        raise AssertionError("R4_PLANTED_SAT_MODEL_INVALID")
    return n,rows

def source(case):
    rows_by_id={x[0]:x for x in CASES}
    if case not in rows_by_id:
        raise AssertionError("R4_UNKNOWN_TEST_SOURCE")
    name,kind,dim,seed=rows_by_id[case]
    if kind=="LIGHTSOUT_PLANTED_SAT":
        return grid(dim,seed)
    if kind=="PLANTED_3SAT_NON_XOR":
        return planted_three_sat(dim,288,seed)
    if kind in ("RANDOM_PLANTED_XOR_COMPLETE","RANDOM_PLANTED_XOR_WITH_ONE_CLAUSE_REMOVED"):
        width=5 if dim==128 else 4
        n,rows=planted_xor(dim,width,dim,seed)
        if kind.endswith("CLAUSE_REMOVED"):
            rows=rows[:-1]  # still SAT; no full XOR proof
        return n,rows
    raise AssertionError("R4_UNSUPPORTED_CASE")

def cnf_profile(rows,n):
    if (n>2500 or len(rows)>35000 or sum(len(x) for x in rows)>160000):
        raise AssertionError("R4_UNSUPPORTED_PROFILE_BUDGET")
    m=len(rows)
    lits=sum(len(x) for x in rows)
    if not rows or n<1 or any(len(x)>6 for x in rows):
        raise AssertionError("R4_BAD_CNF")
    cert=xor.group_parity_equations(rows,n)
    exact=cert["status"]=="EXACT_XOR_COVER_PASS"
    eq=cert["equations"] if exact else []
    widths=[len(v["variables"]) for v in eq]
    deg=[0]*(n+1)
    for item in eq:
        for v in item["variables"]:deg[v]+=1
    avg=(sum(deg[1:])/n) if n else 0
    cv=math.sqrt(sum((v-avg)**2 for v in deg[1:])/n)/avg if avg else 0
    side=math.isqrt(n)
    isgrid=int(exact and r3.verified_lightsout_supports(cert,n,side))
    fv={
      "log1p_n":math.log1p(n),
      "log1p_clauses":math.log1p(m),
      "log1p_literal_occurrences":math.log1p(lits),
      "mean_original_clause_width":lits/m,
      "certified_equations_per_variable":len(eq)/n,
      "mean_certified_support_width":sum(widths)/len(widths) if widths else 0,
      "support_variable_degree_CV":cv,
      "rhs_bias_from_half":abs(sum(x["rhs"] for x in eq)/len(eq)-0.5) if eq else 0,
      "is_proven_square_lightsout_topology":isgrid
    }
    if list(fv)!=list(FEAT_KEYS) or any(not math.isfinite(v) for v in fv.values()):
        raise AssertionError("R4_BAD_FEATURES")
    return fv,cert

def vector(feat):
    return tuple(feat[k]/s for k,s in zip(FEAT_KEYS,SCALE))

def distance(a,b):
    return math.sqrt(sum((x-y)**2 for x,y in zip(vector(a),vector(b))))

def historical_samples():
    r1doc,r2doc,r3doc=load_prior()
    result=[]
    def add(name,side,rows,n,source_sha,comparisons):
        orig=r1.original_sha(rows,n)
        if orig!=source_sha or len(comparisons)<2:
            raise AssertionError("R4_REBUILT_HISTORICAL_SOURCE_SHA_OR_HOSTS_DRIFT "+name)
        f,cover=cnf_profile(rows,n)
        if cover["status"]!="EXACT_XOR_COVER_PASS" or not f["is_proven_square_lightsout_topology"]:
            raise AssertionError("R4_TRAINING_INPUT_NOT_CERTIFIED_GRID "+name)
        gf2_times=[];comp_times=[]
        for times in comparisons:
            t=times.get("gf2")
            baselines=[times.get(x) for x in ("cms_native","cms_raw","cadical")]
            valid=[v for v in baselines if isinstance(v,(int,float)) and v>0]
            if not isinstance(t,(int,float)) or t<=0 or not valid:
                raise AssertionError("R4_TRAINING_BENCHMARK_LABEL_UNVERIFIED")
            gf2_times.append(t);comp_times.append(min(valid))
        result.append({
            "name":name,"side":side,"sha":orig,"features":f,
            "gf2_seconds":median(gf2_times),
            "fastest_verified_external_seconds":median(comp_times),
            "right_censored_controls_excluded":True,
            "training_historical_only":True
        })
    r1spec={"new_grid_19":(19,202611030519),"new_grid_25":(25,202611030525),"new_grid_37":(37,202611030537)}
    for name,(side,seed) in r1spec.items():
        n,rows,status=r1.generate_grid(side,seed)
        if status!="SAT":raise AssertionError("R1_SOURCE_NOT_SAT")
        add(name,side,rows,n,r1doc["source_sha256"][name],
            [z for z in r1doc["posthoc_rounded_median_seconds"] if z["case"]==name])
    for side in (21,23,29,39):
        name="new_r2_grid_"+str(side)
        n,rows=r2.source(name)
        entries=[z for z in r2doc["median_seconds_rounded"] if z["case"]==f"{side}x{side}"]
        if len(entries)!=1:raise AssertionError("R4_R2_TRAINING_MISSING")
        q=entries[0]
        add(name,side,rows,n,r2doc["source_hashes"][name],
            [q["ubuntu22"],q["ubuntu24"]])
    for name in ("r3_grid_17","r3_grid_27","r3_grid_33","r3_grid_35","r3_grid_41a","r3_grid_41b"):
        n,rows=r3.source(name)
        side=math.isqrt(n)
        entries=[]
        for host in r3doc["per_host_full_cold_medians_from_decoded_job_logs"]:
            by_arm=host["per_source"][name]["by_arm"]
            read=lambda key:by_arm[key]["median_full_cold_s_valid_only"]
            entries.append({
                "gf2":read("janus_gf2"),
                "cms_native":read("cryptominisat_native_xor"),
                "cms_raw":read("cryptominisat_original_cnf"),
                "cadical":read("cadical195_original_cnf")})
        add(name,side,rows,n,r3doc["new_original_source_SHA256"][name],entries)
    if len(result)!=13 or len(set(x["sha"] for x in result))!=13:
        raise AssertionError("R4_13_DISTINCT_TRAINING_SAMPLES_REQUIRED")
    return result

def group_historical(samples):
    by=defaultdict(list)
    for s in samples:by[s["side"]].append(s)
    groups=[]
    for side,values in sorted(by.items()):
        gf=math.exp(sum(math.log(x["gf2_seconds"]) for x in values)/len(values))
        ex=math.exp(sum(math.log(x["fastest_verified_external_seconds"]) for x in values)/len(values))
        groups.append({
            "side":side,"original_SHA256":[x["sha"] for x in values],
            "features":{k:sum(x["features"][k] for x in values)/len(values) for k in FEAT_KEYS},
            "gf2_seconds":gf,"external_seconds":ex,
            "observed_gain":ex/gf})
    if len(groups)!=12:
        raise AssertionError("R4_TRAINING_GROUPS_MUST_BE_12_DISTINCT_GRID_SIZES")
    return groups

def nearest(features,groups):
    ordered=sorted(groups,key=lambda x:(distance(features,x["features"]),x["side"]))
    return ordered[:K]

def predict(features,groups,penalty):
    if len(groups)<K:
        raise AssertionError("R4_INSUFFICIENT_DISTINCT_TRAINING_SIZES")
    neighbors=nearest(features,groups)
    ds=[distance(features,p["features"]) for p in neighbors]
    raw=[1/(0.03+d)**2 for d in ds]
    scale=sum(raw)
    weights=[x/scale for x in raw]
    pred_gf=math.exp(sum(w*math.log(q["gf2_seconds"]) for w,q in zip(weights,neighbors)))
    pred_ext=math.exp(sum(w*math.log(q["external_seconds"]) for w,q in zip(weights,neighbors)))
    ratio=pred_ext/pred_gf
    neighbor_observed=sorted(q["observed_gain"] for q in neighbors)
    lower=min(neighbor_observed[1],ratio*math.exp(-penalty))
    return {
        "predicted_gf2_full_cold_s":pred_gf,
        "predicted_fastest_external_full_cold_s":pred_ext,
        "predicted_gain":ratio,
        "risk_lower_bound_gain":lower,
        "neighbor_distinct_grid_sizes":[q["side"] for q in neighbors],
        "neighbor_distances":ds,
        "empirical_q25_nearest_gain":neighbor_observed[1],
        "leave_one_size_out_log_error_penalty":penalty
    }

def train():
    p,psha=load_frozen()
    samples=historical_samples()
    groups=group_historical(samples)
    residual=[]
    for g in groups:
        neigh=[x for x in groups if x["side"]!=g["side"]]
        pred=predict(g["features"],neigh,0)
        residual.append(abs(math.log(g["observed_gain"]/pred["predicted_gain"])))
    penalty=median(residual)
    fit={
        "schema":"JANUS-E12C5-R4-PAST-ONLY-CNF-FIT-V1",
        "prereg_sha256":psha,
        "training_sources_git_blob_SHA1":dict(PAST),
        "training_original_source_count":len(samples),
        "training_distinct_side_size_count":len(groups),
        "training_SHAs":sorted(x["sha"] for x in samples),
        "groups":groups,
        "K":K,"scale":SCALE,
        "leave_one_side_out_median_absolute_log_gain_error":penalty,
        "leave_one_side_out_absolute_log_residuals":residual,
        "gain_lower_bound_threshold":1.2,
        "estimated_gain_threshold":1.4,
        "FITTED_BEFORE_R4_RESULTS":True,
        "C023_UNCHANGED":True,
    }
    return fit

def choose(rows,n,fit):
    t0=__import__("time").perf_counter()
    profile,cover=cnf_profile(rows,n)
    elapsed=__import__("time").perf_counter()-t0
    if fit["schema"]!="JANUS-E12C5-R4-PAST-ONLY-CNF-FIT-V1" or fit["K"]!=K:
        raise AssertionError("R4_UNTRUSTED_FIT")
    if cover["status"]!="EXACT_XOR_COVER_PASS":
        return "cryptominisat_original_cnf",None,None,"NO_PROVEN_FULL_XOR",profile,elapsed
    if not profile["is_proven_square_lightsout_topology"]:
        return "cryptominisat_original_cnf",None,None,"OUT_OF_DOMAIN_NO_GRID_TRAINING",profile,elapsed
    pred=predict(profile,fit["groups"],
                 fit["leave_one_side_out_median_absolute_log_gain_error"])
    if (elapsed<=2.0 and pred["predicted_gain"]>=1.4
        and pred["risk_lower_bound_gain"]>=1.2):
        return "janus_gf2",cover,pred,"R4_SUPPORTED_LOWER_BOUND_GAIN",profile,elapsed
    return "cryptominisat_native_xor",cover,pred,"R4_ABSTAIN_GF2_NOT_CONFIDENT",profile,elapsed

def main():
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--fit-output",type=Path)
    ap.add_argument("--check",action="store_true")
    a=ap.parse_args()
    if a.fit_output:
        fit=train()
        a.fit_output.parent.mkdir(parents=True,exist_ok=True)
        a.fit_output.write_bytes(canonical(fit))
        print("R4_TRAINED_HISTORY_ONLY",sha256(a.fit_output.read_bytes()).hexdigest(),
              fit["training_original_source_count"],fit["training_distinct_side_size_count"])
    if a.check:
        fit=train()
        shas=[]
        for case,kind,dim,seed in CASES:
            n,rows=source(case)
            shas.append(r1.original_sha(rows,n))
            prof,cert=cnf_profile(rows,n)
            result=choose(rows,n,fit)
            if kind.startswith("RANDOM_") or kind.startswith("PLANTED_"):
                if result[0]!="cryptominisat_original_cnf":
                    raise AssertionError("R4_NON_GRID_UNJUSTIFIED_GF2_SELECTION")
            if kind=="LIGHTSOUT_PLANTED_SAT" and cert["status"]!="EXACT_XOR_COVER_PASS":
                raise AssertionError("R4_GRID_NOT_PROVEN_EXACT")
        if len(set(shas))!=len(shas) or set(shas)&set(fit["training_SHAs"]):
            raise AssertionError("R4_HELDOUT_LEAKAGE_OR_COLLISION")
        print("R4_FROZEN_SOURCE_PROOF_PASS",json.dumps(dict(zip((x[0] for x in CASES),shas)),sort_keys=True))
if __name__=="__main__":
    main()
