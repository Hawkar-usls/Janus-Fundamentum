from __future__ import annotations
import hashlib, json
from pathlib import Path
from research.tools.apma_bucket_common_core import common_core_semijoin_prefilter as cc_v1
from research.tools.apma_bucket_common_core import common_core_semijoin_prefilter_v1_1 as cc_v11
from research.tools.apma_bucket_residual_single_separator import residual_single_separator_factorized_payload as cand
from research.tools.apma_guarded_elimination import guarded_bounded_output_elimination as guarded

ARTIFACT_ID="JANUS-TRUMP-BICAMERAL-BUCKET-UNIQUE-CORE-RESIDUAL-SINGLE-VARIABLE-SEPARATOR-FACTORIZED-PAYLOAD-INDEPENDENT-CHECK-2026-09-15-v1.0"
VERDICT="PASS_SCOPED_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_SINGLE_VARIABLE_SEPARATOR_FACTORIZED_PAYLOAD_V1"
CANDIDATE=Path("research/tools/apma_bucket_residual_single_separator/residual_single_separator_factorized_payload.py")
CANDIDATE_BLOB="cd17292b7451b03b966dbcf62d1b6e4c767f7ac0"

def root(): return Path(__file__).resolve().parents[3]
def blob(p):
    d=p.read_bytes(); return hashlib.sha1(f"blob {len(d)}\0".encode()+d).hexdigest()

def base(raw):
    pred=cc_v11.explain(raw); ready=cc_v11.first_failed_original_bucket_v11(raw)
    if pred.get("status")!="OPEN_COMMON_CORE_FILTERED_BUCKET_STILL_OVER_L2" or ready.get("status")!="READY": return {"status":"OUT_OF_SCOPE"}
    core=[int(v) for v in ready["common_core"]]; sf=cc_v1.support_and_filter(ready["canonical"],ready["bucket"],core); common=sorted(sf["common"])
    if len(common)!=1: return {"status":"OPEN_NONUNIQUE_COMMON_CORE_SUPPORT"}
    state=tuple(int(x) for x in common[0]); factors=[]
    for f in ready["bucket"]:
        rows=[tuple(int(x) for x in r) for r in f["rows"] if cc_v1._projection(f,core,r)==state]; factors.append({**f,"rows":rows})
    return {"status":"READY","ready":ready,"core":core,"factors":factors}

def scopes(factors,core):
    C=set(core); return [{int(v) for v in f["scope"] if int(v) not in C} for f in factors]

def comps(ss):
    n=len(ss); adj={i:[] for i in range(n)}
    for i in range(n):
        for j in range(i+1,n):
            if ss[i]&ss[j]: adj[i].append(j); adj[j].append(i)
    seen=set(); out=[]
    for s in range(n):
        if s in seen: continue
        seen.add(s); q=[s]; c=[]
        while q:
            u=q.pop(0); c.append(u)
            for w in adj[u]:
                if w not in seen: seen.add(w); q.append(w)
        out.append(sorted(c))
    return sorted(out,key=lambda x:(x[0],len(x),x))

def restrict(f,v,b):
    sc=[int(x) for x in f["scope"]]; rows=[tuple(int(x) for x in r) for r in f["rows"]]
    if v not in sc: return {**f,"scope":sc,"rows":rows}
    p=sc.index(v); nr=sorted({r[:p]+r[p+1:] for r in rows if r[p]==b})
    return None if not nr else {**f,"scope":sc[:p]+sc[p+1:],"rows":nr}

def independent(raw):
    x=base(raw)
    if x.get("status")!="READY": return x
    ss=scopes(x["factors"],x["core"]); base_n=len(comps(ss)); vars_=sorted(set().union(*ss) if ss else set()); cs=[]
    for v in vars_:
        if len(comps([s-{v} for s in ss]))<=base_n: continue
        sts=[]; ok=True
        for b in (0,1):
            rf=[]; empty=False
            for f in x["factors"]:
                z=restrict(f,v,b)
                if z is None: empty=True; break
                rf.append(z)
            if empty: sts.append("EXACT_UNSAT_BY_EMPTY_SEPARATOR_RESTRICTION"); continue
            cc=comps(scopes(rf,x["core"])); bad=any(len(c)>2 for c in cc); sts.append("OPEN_BRANCH_RESIDUAL_COMPONENT_GT2" if bad else "READY_BRANCH_LE2"); ok &= not bad
        cs.append({"variable":v,"branch_statuses":sts,"structural_ok":ok})
    good=[c for c in cs if c["structural_ok"]]
    return {"status":"READY" if good else "OPEN_NO_ADMISSIBLE_RESIDUAL_SINGLE_VARIABLE_SEPARATOR","selected":good[0]["variable"] if good else None,"candidates":cs,"canonical":x["ready"]["canonical"]}

def carrier(o): return o.get("carrier",{})
def statuses(o): return [b.get("status") for b in carrier(o).get("branches",[])]
def witness_ok(raw,o):
    w=carrier(o).get("witness"); b=base(raw)
    return isinstance(w,dict) and b.get("status")=="READY" and guarded.verify_original_assignment(b["ready"]["canonical"],{int(k):int(v) for k,v in w.items()})

def run():
    raws={"pos":cand.positive_separator_control(),"one":cand.one_branch_unsat_one_sat_control(),"both":cand.both_branches_unsat_control(),"no":cand.no_single_variable_articulation_control(),"gt2":cand.branch_still_gt2_control()}
    ind={k:independent(v) for k,v in raws.items()}; out={k:cand.explain(v) for k,v in raws.items()}; hint=cand.explain(cand.injected_hint_control()); tamper=cand.tampered_control(); pc=carrier(out["pos"])
    checks={
      "G1_candidate_blob":blob(root()/CANDIDATE)==CANDIDATE_BLOB,"G1_source_guard":cand.source_guard()["ok"] is True,
      "G2_independent_separator_47":ind["pos"].get("selected")==47,"G2_candidate_separator_47":pc.get("receipt",{}).get("separator_variable")==47,
      "G3_positive_sat":out["pos"].get("status")=="ADMIT_EXACT_UNIQUE_CORE_RESIDUAL_SINGLE_VARIABLE_SEPARATOR_FACTORIZED_PAYLOAD","G3_positive_witness":witness_ok(raws["pos"],out["pos"]),
      "G4_two_branches":[b.get("value") for b in pc.get("branches",[])]==[0,1],
      "G5_one_branch":out["one"].get("status")=="ADMIT_EXACT_UNIQUE_CORE_RESIDUAL_SINGLE_VARIABLE_SEPARATOR_FACTORIZED_PAYLOAD" and "EXACT_UNSAT_BY_EMPTY_SEPARATOR_RESTRICTION" in statuses(out["one"]),
      "G6_both_unsat":out["both"].get("status")=="EXACT_UNSAT_BY_BOTH_SEPARATOR_BRANCHES",
      "G7_no_articulation":ind["no"].get("status")=="OPEN_NO_ADMISSIBLE_RESIDUAL_SINGLE_VARIABLE_SEPARATOR" and out["no"].get("status")=="OPEN_NO_ADMISSIBLE_RESIDUAL_SINGLE_VARIABLE_SEPARATOR",
      "G8_branch_gt2":ind["gt2"].get("status")=="OPEN_NO_ADMISSIBLE_RESIDUAL_SINGLE_VARIABLE_SEPARATOR" and out["gt2"].get("status")=="OPEN_NO_ADMISSIBLE_RESIDUAL_SINGLE_VARIABLE_SEPARATOR",
      "G9_hint":hint.get("status")=="REJECT_RAW_INPUT","G9_tamper":tamper.get("status")=="REJECT_TAMPERED_PROVENANCE",
      "G10_zero_join":pc.get("receipt",{}).get("three_plus_join_chains_materialized")==0,"G10_zero_product":pc.get("receipt",{}).get("global_residual_cartesian_products_materialized")==0,
      "FW_pvsnp":cand.firewall()["P_VS_NP"]=="OPEN","FW_sat":cand.firewall()["GENERAL_SAT_IN_P"]=="NOT_PROVED","FW_separator":cand.firewall()["GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY"]=="NOT_PROVED"}
    verdict=VERDICT if all(checks.values()) else "FAIL_OR_OPEN_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_SINGLE_VARIABLE_SEPARATOR_FACTORIZED_PAYLOAD_V1"
    return {"artifact_id":ARTIFACT_ID,"authority":"INDEPENDENT_CHECKER__SCOPED_ONLY","checks":checks,"controls":{"positive":out["pos"].get("status"),"positive_separator":pc.get("receipt",{}).get("separator_variable"),"positive_branch_statuses":statuses(out["pos"]),"one":out["one"].get("status"),"one_statuses":statuses(out["one"]),"both":out["both"].get("status"),"both_statuses":statuses(out["both"]),"no":out["no"].get("status"),"gt2":out["gt2"].get("status"),"hint":hint.get("status"),"tamper":tamper.get("status")},"independent_methods":{"componentization":"BFS","candidate_componentization":"UNION_FIND","candidate_separator_helpers_used":False,"witness":"FULL_ORIGINAL_RELATION_REPLAY"},"scientific_firewall":cand.firewall(),"verdict":verdict}

def main(): print(json.dumps(run(),sort_keys=True))
if __name__=="__main__": main()
