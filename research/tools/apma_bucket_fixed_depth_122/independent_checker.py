from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

from research.tools.apma_bucket_fixed_depth_122 import fixed_depth_122 as cand
from research.tools.apma_bucket_residual_single_separator import residual_single_separator_factorized_payload as v38
from research.tools.apma_guarded_elimination import guarded_bounded_output_elimination as guarded

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-BUCKET-UNIQUE-CORE-RESIDUAL-FIXED-DEPTH-1-2-2-INDEPENDENT-CHECK-2026-09-15-v1.0"
VERDICT = "PASS_SCOPED_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_FIXED_DEPTH_1_2_2_SEPARATOR_PORTFOLIO_V1"
CAND = Path("research/tools/apma_bucket_fixed_depth_122/fixed_depth_122.py")
CAND_BLOB = "2e02bac1d78b751d22df2c50a01980ae06bd2751"
MAX_LEAVES = 32


def root(): return Path(__file__).resolve().parents[3]
def blob(p):
    d=p.read_bytes(); return hashlib.sha1(f"blob {len(d)}\0".encode()+d).hexdigest()

def rscope(f, core): return {int(v) for v in f["scope"] if int(v) not in set(core)}

def bfs_components(factors, core):
    scopes=[rscope(f,core) for f in factors]; n=len(scopes); adj={i:set() for i in range(n)}
    for i in range(n):
        for j in range(i+1,n):
            if scopes[i] & scopes[j]: adj[i].add(j); adj[j].add(i)
    seen=set(); out=[]
    for s in range(n):
        if s in seen: continue
        q=[s]; seen.add(s); c=[]
        while q:
            x=q.pop(0); c.append(x)
            for y in sorted(adj[x]):
                if y not in seen: seen.add(y); q.append(y)
        out.append(sorted(c))
    return sorted(out,key=lambda c:(c[0],len(c),c))

def restrict_one(f, assignment):
    scope=[int(v) for v in f["scope"]]; rows=[tuple(int(x) for x in r) for r in f["rows"]]
    pos=[(i,v) for i,v in enumerate(scope) if v in assignment]; keep=[i for i,v in enumerate(scope) if v not in assignment]
    root_scope=list(f.get("_root_origin_scope",scope)); old=f.get("_root_origin_witness",{r:r for r in rows}); witness={}
    for r in rows:
        if all(r[i]==int(assignment[v]) for i,v in pos):
            nr=tuple(r[i] for i in keep); witness.setdefault(nr,tuple(old.get(tuple(r),tuple(r))))
    if not witness: return None
    g={**f,"scope":[scope[i] for i in keep],"rows":sorted(witness),"_root_origin_scope":root_scope,"_root_origin_witness":witness}
    return g

def restrict_all(fs, assignment):
    out=[]
    for f in fs:
        z=restrict_one(f,assignment)
        if z is None: return None
        out.append(z)
    return out

def seed(fs):
    out=[]
    for f in fs:
        scope=[int(v) for v in f["scope"]]; rows=[tuple(int(x) for x in r) for r in f["rows"]]
        out.append({**f,"scope":scope,"rows":rows,"_root_origin_scope":scope,"_root_origin_witness":{r:r for r in rows}})
    return out

def gt2(fs,core): return [c for c in bfs_components(fs,core) if len(c)>2]
def disconnects(fs,core,comp,pair):
    ss=[rscope(fs[i],core) for i in comp]
    def comps_scopes(scopes):
        n=len(scopes); adj={i:set() for i in range(n)}
        for i in range(n):
            for j in range(i+1,n):
                if scopes[i]&scopes[j]: adj[i].add(j); adj[j].add(i)
        seen=set(); k=0
        for s in range(n):
            if s in seen: continue
            k+=1; q=[s]; seen.add(s)
            while q:
                x=q.pop(0)
                for y in adj[x]:
                    if y not in seen: seen.add(y); q.append(y)
        return k
    return comps_scopes([s-set(pair) for s in ss])>comps_scopes(ss)

def second_pair(fs,core,comp):
    vs=sorted(set().union(*(rscope(fs[i],core) for i in comp)))
    for p in itertools.combinations(vs,2):
        if not disconnects(fs,core,comp,p): continue
        ok=True
        for vals in ((0,0),(0,1),(1,0),(1,1)):
            rr=restrict_all(fs,{p[0]:vals[0],p[1]:vals[1]})
            if rr is None: continue
            if any(len(c)>2 for c in bfs_components(rr,core)): ok=False; break
        if ok: return list(p)
    return None

def first_pair_plan(fs,core):
    gs=gt2(fs,core)
    if not gs: return {"status":"DIRECT_LE2","pair":None,"branches":[]}
    if len(gs)!=1: return None
    comp=gs[0]; vs=sorted(set().union(*(rscope(fs[i],core) for i in comp)))
    for p in itertools.combinations(vs,2):
        if not disconnects(fs,core,comp,p): continue
        bs=[]; ok=True
        for vals in ((0,0),(0,1),(1,0),(1,1)):
            rr=restrict_all(fs,{p[0]:vals[0],p[1]:vals[1]})
            if rr is None: bs.append({"values":list(vals),"status":"EXACT_EMPTY","second_pair":None}); continue
            gs2=gt2(rr,core)
            if not gs2: bs.append({"values":list(vals),"status":"LE2","second_pair":None}); continue
            if len(gs2)!=1 or len(gs2[0])!=3: ok=False; break
            sp=second_pair(rr,core,gs2[0])
            if sp is None: ok=False; break
            bs.append({"values":list(vals),"status":"GT2_WITH_SECOND_PAIR","second_pair":sp})
        if ok: return {"status":"FIRST_PAIR_READY","pair":list(p),"branches":bs}
    return None

def independent_plan(prep):
    fs=seed(prep["conditioned"]); gs=gt2(fs,prep["core"])
    if len(gs)!=1: return None
    vs=sorted(set().union(*(rscope(fs[i],prep["core"]) for i in gs[0])))
    for v in vs:
        sb=[]; ok=True
        for bit in (0,1):
            rr=restrict_all(fs,{v:bit})
            if rr is None: sb.append({"value":bit,"status":"EXACT_EMPTY","first_pair":None}); continue
            fp=first_pair_plan(rr,prep["core"])
            if fp is None: ok=False; break
            sb.append({"value":bit,"status":"READY","first_pair":fp})
        if ok: return {"single_variable":v,"single_branches":sb}
    return None

def plan_signature(p):
    if p is None: return None
    out={"single_variable":int(p["single_variable"]),"branches":[]}
    for sb in p["single_branches"]:
        x={"value":int(sb["value"]),"status":sb["status"]}
        fp=sb.get("first_pair_plan") or sb.get("first_pair")
        if fp:
            pair=fp.get("first_pair",fp.get("pair")); x["first_pair"]=pair; x["first_pair_branches"]=[]
            for b in fp.get("branches",[]): x["first_pair_branches"].append({"values":b["values"],"status":b["status"],"second_pair":b.get("second_pair")})
        out["branches"].append(x)
    return out

def run():
    positive_raw=cand.positive_k4_control(); prep=v38._prepare(positive_raw)
    cp=cand.discover_plan(prep); ip=independent_plan(prep)
    positive=cand.explain(positive_raw); depth=cand.depth_cap_unit_control(); hint=cand.explain(cand.injected_hint_control()); tamper=cand.tampered_control()
    c_sig=plan_signature(cp); i_sig=plan_signature(ip)
    witness=positive.get("carrier",{}).get("witness") or positive.get("witness")
    witness_ok=bool(witness) and guarded.verify_original_assignment(prep["canonical"],{int(k):int(v) for k,v in witness.items()})
    checks={
      "G1_candidate_blob":blob(root()/CAND)==CAND_BLOB,
      "G1_candidate_guard":cand.source_guard()["ok"],
      "G2_parent_ready":prep.get("status")=="READY",
      "G3_independent_plan_exists":ip is not None,
      "G3_plan_signature_match":c_sig==i_sig,
      "G4_positive_terminal":positive.get("status")=="ADMIT_EXACT_UNIQUE_CORE_RESIDUAL_FIXED_DEPTH_1_2_2_SEPARATOR_PORTFOLIO",
      "G4_positive_witness_replay":witness_ok,
      "G5_leaf_cap":positive.get("carrier",{}).get("receipt",{}).get("maximum_logical_leaf_count")==MAX_LEAVES,
      "G5_leaf_coverage":positive.get("carrier",{}).get("receipt",{}).get("logical_leaf_equivalents_covered")==MAX_LEAVES,
      "G6_depth_cap_open":depth.get("status")=="OPEN_FIXED_DEPTH_1_2_2_SKELETON_NOT_FOUND",
      "G7_hint_reject":hint.get("status")=="REJECT_RAW_INPUT",
      "G7_tamper_reject":tamper.get("status")=="REJECT_TAMPERED_PROVENANCE",
      "G8_zero_ge3":positive.get("carrier",{}).get("receipt",{}).get("separator_sets_size_three_or_more")==0,
      "G8_zero_recursion":positive.get("carrier",{}).get("receipt",{}).get("unbounded_recursive_calls")==0,
      "G8_zero_join":positive.get("carrier",{}).get("receipt",{}).get("three_plus_join_chains_materialized")==0,
      "G8_zero_product":positive.get("carrier",{}).get("receipt",{}).get("global_residual_cartesian_products_materialized")==0,
      "FW_pvsnp":positive["scientific_firewall"]["P_VS_NP"]=="OPEN",
      "FW_sat":positive["scientific_firewall"]["GENERAL_SAT_IN_P"]=="NOT_PROVED",
      "FW_recursion":positive["scientific_firewall"]["GENERAL_RECURSIVE_SEPARATOR_TRACTABILITY"]=="NOT_PROVED",
    }
    verdict=VERDICT if all(checks.values()) else "FAIL_OR_OPEN_FIXED_DEPTH_1_2_2_INDEPENDENT_CHECK"
    return {"artifact_id":ARTIFACT_ID,"authority":"INDEPENDENT_CHECKER__SCOPED_ONLY","verdict":verdict,"checks":checks,"candidate_plan_signature":c_sig,"independent_plan_signature":i_sig,"controls":{"positive":positive.get("status"),"depth_cap":depth.get("status"),"hint":hint.get("status"),"tamper":tamper.get("status")},"independent_methods":{"componentization":"BFS","pair_discovery":"UNORDERED_PAIR_SCAN","candidate_plan_helpers_used":False,"witness":"FULL_ORIGINAL_RELATION_REPLAY"},"scientific_firewall":cand.firewall()}

def main(): print(json.dumps(run(),sort_keys=True))
if __name__=="__main__": main()
