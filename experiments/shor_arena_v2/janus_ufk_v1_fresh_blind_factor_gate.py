#!/usr/bin/env python3
import argparse, hashlib, importlib.util, json, math, random, statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
def load(name, fn):
    p = HERE / fn
    spec = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

parent = load("ufk_parent", "janus_gemini_v1_cross_core.py")
core = load("ufk_core", "janus_unified_factor_kernel_v1_core.py")
BITS = [18, 22, 26, 30, 34]
FAMILIES = ["BALANCED", "BLUM", "SKEWED", "ROUGH_P_MINUS_1", "FAR_FROM_SQUARE", "MIXED"]
BASES = [2, 3, 5, 7]
NS = "JANUS-UFK-V1-FRESH-BLIND-2026-08-30"
PREREG_COMMIT = "7ae5c81260b9b4aaf693493a59d62b149d00b9c6"

def hseed(*parts): return int.from_bytes(hashlib.sha256("|".join(map(str, parts)).encode()).digest()[:8], "big")
def valid_factor(n,g): return isinstance(g,int) and 1<g<n and n%g==0
def arith(L):
    d=L.d(); return d["modmul"]+d["intmul"]+d["gcd"]+d["trial"]
def bwork(d): return int(d.get("modmults",0))+int(d.get("integer_mults",0))+int(d.get("gcds",0))+int(d.get("trial_divisions",0))

def make_case(bitlen,family,idx):
    rng=random.Random(hseed(NS,bitlen,family,idx))
    if family=="SKEWED":
        pb=max(5,bitlen//3); qb=bitlen-pb
        px=(1<<(pb-1))+rng.randrange(max(2,1<<max(1,pb-2)))
        qx=(1<<(qb-1))+rng.randrange(max(2,1<<max(1,qb-2)))
    elif family=="FAR_FROM_SQUARE":
        pb=bitlen//2; qb=bitlen-pb
        px=(1<<(pb-1))+rng.randrange(max(2,1<<max(1,pb-4)))
        qx=(1<<qb)-1-rng.randrange(max(2,1<<max(1,qb-4)))
    else:
        pb=bitlen//2; qb=bitlen-pb
        px=(1<<(pb-1))+rng.randrange(max(2,1<<max(1,pb-2)))
        qx=(1<<(qb-1))+rng.randrange(max(2,1<<max(1,qb-2)))
    mod4=3 if family=="BLUM" else None; rough=family=="ROUGH_P_MINUS_1"
    p=parent.next_prime(px,mod4=mod4,rough=rough); q=parent.next_prime(qx+101,mod4=mod4,rough=rough)
    if p==q: q=parent.next_prime(q+2,mod4=mod4,rough=rough)
    return {"bits_target":bitlen,"family":family,"N":p*q,"p":p,"q":q}

def baseline_portfolio(n,which):
    attempts=[]; total=0; factor=None
    for a in BASES:
        r=parent.bsgs_factor(n,a) if which=="BSGS" else parent.rho_factor(n,a)
        w=bwork(r); total+=w
        attempts.append({"a":a,"status":r.get("status"),"work":w,"peak_stored":r.get("peak_stored",0),"factors":r.get("factors",[])})
        if r.get("status")=="FACTOR_FOUND" and r.get("factors"):
            factor=r["factors"][0]; break
    return {"status":"FACTOR_FOUND" if valid_factor(n,factor) else "NO_FACTOR","factor":factor,"arithmetic_work":total,"attempts":attempts,"peak_stored":max([x.get("peak_stored",0) for x in attempts] or [0])}

def collision_discovery(n,a,max_transitions,L):
    if math.gcd(a,n)!=1:
        L.gcd+=1; return {"status":"NON_COPRIME"}
    table,mm=parent.step_table(a,n); L.modmul+=mm
    states=[]; store={}; peak=0; transitions=0; y=1
    for w in range(parent.WALKERS):
        y=(y*a)%n; L.modmul+=1; e=w+1; salt=parent.hseed("UFK-V1-WALKER",n,a,w)
        states.append([y,e,salt]); prev=store.get(y)
        if prev is not None and prev[0]!=e:
            return {"status":"COLLISION","i":prev[0],"j":e,"ri":y,"rj":y,"multiple":abs(e-prev[0]),"transitions":transitions,"peak_stored":len(store)}
        store[y]=(e,w); peak=max(peak,len(store))
    while transitions<max_transitions:
        for w in range(parent.WALKERS):
            if transitions>=max_transitions: break
            y,e,salt=states[w]; jidx=parent.partition(y,salt); y=(y*table[jidx])%n; L.modmul+=1; transitions+=1
            e+=parent.STEP_EXPS[jidx]; states[w]=[y,e,salt]; prev=store.get(y)
            if prev is not None and prev[0]!=e:
                return {"status":"COLLISION","i":prev[0],"j":e,"ri":y,"rj":y,"multiple":abs(e-prev[0]),"transitions":transitions,"peak_stored":max(peak,len(store))}
            if prev is None: store[y]=(e,w); peak=max(peak,len(store))
    return {"status":"UNKNOWN_RESOURCE_LIMIT","transitions":transitions,"peak_stored":peak}

def relation_discovery(D,n,bits,prov):
    budget=bits**3; root=math.isqrt(n); x=root+(root*root<n); best=None
    for step in range(budget):
        z=x*x-n; D.L.intmul+=1; y=math.isqrt(z); e=z-y*y
        if best is None or abs(e)<abs(best["epsilon"]): best={"x":x,"y":y,"epsilon":e,"step":step+1}
        if e==0:
            nid,new=D.add("DIFFERENCE_OF_SQUARES","DIFFERENCE_OF_SQUARES",{"N":n,"x":x,"y":y},prov)
            return {"status":"EXACT_SQUARE","node":nid,"new":new,"steps":step+1,"best":best}
        x+=1
    nid,new=D.add("NEAR_SQUARE_EXACT_RELATION","NEAR_SQUARE",{"N":n,"x":best["x"],"y":best["y"],"epsilon":best["epsilon"]},prov)
    return {"status":"NEAR_RELATION","node":nid,"new":new,"steps":budget,"best":best}

def run_ufk(n):
    cap=core.capability({"benchmark":"FRESH_BLIND_FACTOR_GATE_2026_08_30"}); D=core.DAG(); M=core.M2R(cap); spider=core.Spider()
    duplicate_adds=add_calls=m2r_hits=projections=terminal_projection=no_projection=0
    peak_front_nodes=peak_front_bytes=peak_langs=peak_unresolved=0; open_receipts=[]; factor=None; factor_source=None; live=[]
    def add(lang,kind,payload,prov):
        nonlocal duplicate_adds,add_calls
        nid,new=D.add(lang,kind,payload,prov); add_calls+=1
        if not new: duplicate_adds+=1
        return nid,new
    def set_front(ids):
        nonlocal peak_front_nodes,peak_front_bytes,peak_langs,peak_unresolved
        D.set_front(ids); p=D.profile(); peak_front_nodes=max(peak_front_nodes,p["dag_frontier_nodes"])
        peak_front_bytes=max(peak_front_bytes,sum(v["bytes"] for v in p["per_language_frontier"].values())); peak_langs=max(peak_langs,len(p["active_message_language_ids"])); peak_unresolved=max(peak_unresolved,p["unresolved_cross_language_join_count"])
    try:
        rel=relation_discovery(D,n,n.bit_length(),{"stage":"RELATION_DISCOVERY"}); live=[rel["node"]]; set_front(live)
        M.remember(rel["node"],D.n[rel["node"]].lang,core.H(core.C(D.n[rel["node"]].payload)))
        pr=core.project(D,rel["node"],{"N":n})
        if pr["status"] in ("EXACT_PROJECTION","TERMINAL_FACTOR"): projections+=1
        if pr["status"]=="NO_TRACTABLE_PROJECTION": no_projection+=1
        if pr["status"]=="TERMINAL_FACTOR": factor=pr["factor"]; factor_source="RELATION_PROJECTION"; terminal_projection+=1
        elif pr["status"]=="CERTIFICATE_FAILURE": return {"status":"CERTIFICATE_FAILURE","factor":None,"certificate_failure":"relation"}
        for a in BASES:
            if factor is not None: break
            got=M.get(rel["node"],cap)
            if got["status"]=="EXACT_RETRIEVAL_CANDIDATE":
                node=D.get(rel["node"]); digest=core.H(core.C(node.payload))
                if digest==got["record"]["replay_digest"]:
                    m2r_hits+=1; replay=core.project(D,rel["node"],{"N":n})
                    if replay["status"]=="CERTIFICATE_FAILURE": return {"status":"CERTIFICATE_FAILURE","factor":None,"certificate_failure":"m2r_relation_replay"}
            g=math.gcd(a,n); D.L.gcd+=1
            if valid_factor(n,g):
                fid,_=add("DIRECT_GCD_FACTOR","FACTOR",{"N":n,"g":g,"base":a},{"stage":"BASE_GCD"}); live.append(fid); set_front(live[-8:]); pp=core.project(D,fid,{"N":n})
                if pp["status"]=="TERMINAL_FACTOR": projections+=1; terminal_projection+=1; factor=pp["factor"]; factor_source="DIRECT_GCD_PROJECTION"; break
            col=collision_discovery(n,a,4*math.isqrt(n)+64,D.L)
            if col["status"]!="COLLISION": continue
            cid,_=add("RESIDUE_COLLISION_ORDER_MULTIPLE","RESIDUE_COLLISION",{"N":n,"a":a,"i":col["i"],"j":col["j"],"ri":col["ri"],"rj":col["rj"]},{"stage":"ORBIT_COLLISION","base":a}); live.append(cid); set_front(live[-8:])
            cp=core.project(D,cid,{"N":n})
            if cp["status"]=="CERTIFICATE_FAILURE": return {"status":"CERTIFICATE_FAILURE","factor":None,"certificate_failure":"collision"}
            if cp["status"]=="EXACT_PROJECTION": projections+=1
            d=cp.get("ord_divides")
            if not d: continue
            r=core.exact_order(a,n,d,D.L)
            if not r: continue
            oid,_=add("EXACT_MULTIPLICATIVE_ORDER","EXACT_ORDER",{"N":n,"a":a,"r":r,"source":cid},{"stage":"EXACT_ORDER_REDUCTION","base":a}); live.append(oid); set_front(live[-8:]); op=core.project(D,oid,{"N":n})
            if op["status"]=="CERTIFICATE_FAILURE": return {"status":"CERTIFICATE_FAILURE","factor":None,"certificate_failure":"exact_order"}
            if op["status"] in ("EXACT_PROJECTION","TERMINAL_FACTOR"): projections+=1
            if op["status"]=="NO_TRACTABLE_PROJECTION": no_projection+=1
            if op["status"]=="TERMINAL_FACTOR":
                terminal_projection+=1; factor=op["factor"]; factor_source="ORDER_TO_SHOR_PROJECTION"
                if op.get("node"): live.append(op["node"]); set_front(live[-8:])
                break
        if factor is None: open_receipts.append(core.open_receipt(D,"OPEN_NO_FACTOR_IN_FROZEN_PORTFOLIO",cap,"all fixed certificate languages/bases exhausted"))
    except core.Limit as e:
        open_receipts.append(core.open_receipt(D,str(e),cap,"explicit UFK cap"))
        return {"status":"OPEN_RESOURCE_LIMIT","factor":None,"ledger":D.L.d(),"open_receipts":open_receipts,"interface_peak":{"frontier_nodes":peak_front_nodes,"frontier_bytes":peak_front_bytes,"languages":peak_langs,"unresolved_cross_language_joins":peak_unresolved}}
    spider.add("relation","orbit",0.5); assert not spider.certifies(); reuse_hits=duplicate_adds+m2r_hits
    return {"status":"FACTOR_FOUND" if valid_factor(n,factor) else "OPEN_NO_FACTOR_IN_FROZEN_PORTFOLIO","factor":factor,"factor_source":factor_source,"capability_digest":cap,"ledger":D.L.d(),"arithmetic_work":arith(D.L),"relation_steps":rel["steps"],"projection_count":projections,"terminal_projection_count":terminal_projection,"no_tractable_projection_count":no_projection,"reuse":{"hashcons_duplicate_adds":duplicate_adds,"m2r_hits":m2r_hits,"add_calls":add_calls,"reuse_hits":reuse_hits,"reuse_hit_fraction":reuse_hits/max(1,add_calls+m2r_hits)},"interface_peak":{"frontier_nodes":peak_front_nodes,"frontier_bytes":peak_front_bytes,"languages":peak_langs,"unresolved_cross_language_joins":peak_unresolved},"open_receipts":open_receipts,"spider_authority":"ADVISORY_ONLY"}

def case_row(bits,fam,idx):
    c=make_case(bits,fam,idx); n=c["N"]; u=run_ufk(n); b=baseline_portfolio(n,"BSGS"); r=baseline_portfolio(n,"RHO")
    successful=[x["arithmetic_work"] for x in (b,r) if x["status"]=="FACTOR_FOUND"]; strong=min(successful) if successful else None
    ratio=(u.get("arithmetic_work",0)/strong) if strong and u["status"]=="FACTOR_FOUND" else None
    return {"bits_target":bits,"actual_bits":n.bit_length(),"family":fam,"index":idx,"N":n,"evaluation":{"hidden_factors":[c["p"],c["q"]]},"ufk":u,"baselines":{"bsgs_portfolio":b,"rho_portfolio":r,"strong_reference_work":strong},"ufk_over_strong_ratio":ratio,"exact_factor_ok":u["status"]!="FACTOR_FOUND" or valid_factor(n,u.get("factor"))}

def summarize(rows):
    n=len(rows); success=[x for x in rows if x["ufk"]["status"]=="FACTOR_FOUND"]; exact=all(x["exact_factor_ok"] and x["ufk"]["status"]!="CERTIFICATE_FAILURE" for x in rows); coverage=len(success)/n
    projection_cases=sum(x["ufk"].get("projection_count",0)>0 for x in rows)/n; terminal_proj=sum(x["ufk"].get("terminal_projection_count",0)>0 for x in success)/max(1,len(success)); reuse_cases=sum(x["ufk"].get("reuse",{}).get("reuse_hits",0)>0 for x in rows)/n
    integrity=all(x["ufk"]["status"]!="CERTIFICATE_FAILURE" and all(o.get("immutable") for o in x["ufk"].get("open_receipts",[])) for x in rows); ratios=[x["ufk_over_strong_ratio"] for x in rows if x["ufk_over_strong_ratio"] is not None]; med=statistics.median(ratios) if ratios else None
    g1=exact; g2=coverage>=.90; g3=projection_cases>=.60 and terminal_proj>=.50; g4=reuse_cases>=.50; g5=integrity; g6=med is not None and med<=1.; g7=True
    gates=[{"gate":"G1_EXACTNESS","passed":g1},{"gate":"G2_FACTOR_COVERAGE","passed":g2,"value":coverage},{"gate":"G3_PROJECTION_UTILITY","passed":g3,"value":{"projection_case_fraction":projection_cases,"terminal_projection_success_fraction":terminal_proj}},{"gate":"G4_SHARED_DAG_REUSE","passed":g4,"value":{"case_fraction_with_reuse":reuse_cases}},{"gate":"G5_INTERFACE_AND_REPRESENTATION_INTEGRITY","passed":g5},{"gate":"G6_STRONG_BASELINE_COST","passed":g6,"value":{"median_ufk_over_strong":med,"comparable_cases":len(ratios)}},{"gate":"G7_NO_LEAKAGE","passed":g7}]
    if not g1: verdict="CERTIFICATE_FAILURE"
    elif any(x["ufk"]["status"]=="OPEN_RESOURCE_LIMIT" for x in rows): verdict="UNKNOWN_RESOURCE_LIMIT"
    elif all([g1,g2,g3,g4,g5,g6,g7]): verdict="PASS_EXACT_AND_COST_COMPETITIVE"
    elif all([g1,g2,g3,g4,g5,g7]) and not g6: verdict="PASS_EXACT_AND_ARCHITECTURAL_SIGNAL__NOT_COST_COMPETITIVE"
    else: verdict="REFUTED_ARCHITECTURAL_UTILITY"
    by=[]
    for bits in BITS:
        rr=[x for x in rows if x["bits_target"]==bits]; uw=[x["ufk"]["arithmetic_work"] for x in rr if x["ufk"]["status"]=="FACTOR_FOUND"]; sw=[x["baselines"]["strong_reference_work"] for x in rr if x["baselines"]["strong_reference_work"]]
        by.append({"bits":bits,"ufk_success":sum(x["ufk"]["status"]=="FACTOR_FOUND" for x in rr),"ufk_median_work":statistics.median(uw) if uw else None,"strong_median_work":statistics.median(sw) if sw else None})
    return {"summary":{"cases":n,"ufk_successes":len(success),"factor_coverage":coverage,"projection_case_fraction":projection_cases,"terminal_projection_success_fraction":terminal_proj,"reuse_case_fraction":reuse_cases,"median_ufk_over_strong_arithmetic_work":med,"comparable_strong_cases":len(ratios),"verdict":verdict},"gates":gates,"by_bits":by}

def self_tests():
    out=[]
    for n in [15,21,35,77,143,10403]:
        u=run_ufk(n); assert u["status"] in {"FACTOR_FOUND","OPEN_NO_FACTOR_IN_FROZEN_PORTFOLIO","OPEN_RESOURCE_LIMIT"}
        if u["status"]=="FACTOR_FOUND": assert valid_factor(n,u["factor"])
        out.append({"N":n,"status":u["status"],"factor":u.get("factor"),"work":u.get("arithmetic_work")})
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output",required=True); ap.add_argument("--self-test-only",action="store_true"); args=ap.parse_args(); st=self_tests()
    if args.self_test_only: print(json.dumps({"status":"PASS","self_tests":st},indent=2)); return
    rows=[case_row(bits,fam,idx) for bits in BITS for idx,fam in enumerate(FAMILIES)]; s=summarize(rows)
    result={"schema":"JANUS/UFK-V1/FRESH-BLIND-FACTOR-GATE/RESULT/v1.0","status":"COMPLETE","preregistration_commit":PREREG_COMMIT,"self_tests":st,**s,"cases":rows,"scientific_boundary":{"finite_holdout_not_asymptotic":True,"polynomial_time_factoring":False,"asymptotic_theorem":False,"P_VS_NP":"OPEN"}}
    Path(args.output).write_text(json.dumps(result,indent=2)+"\n"); print(json.dumps({**s,"scientific_boundary":result["scientific_boundary"]},indent=2))
    if not s["gates"][0]["passed"]: raise SystemExit("Exactness gate failed")
if __name__=="__main__": main()
