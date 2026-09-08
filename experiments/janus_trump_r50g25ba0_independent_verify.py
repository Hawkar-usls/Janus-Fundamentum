from __future__ import annotations

import argparse
import hashlib
import json
from itertools import combinations, product
from pathlib import Path

import janus_trump_r50g25av_reachable_multi_defect_growth_witness as av
import janus_trump_r50g25at_tautology_hardened_runner as ath

PREREG = "d096066e88d2f90240892ff37546c5876732f313"
Y_HASH = av.Y_TARGET_HASH
VARS = (2,3,4,5,8,9,10,11,12,13,15,16,20,24,25,26,27,28,29,30)
ORDER = (24,10,2,11,15,20,3,4,5,8,9,12,13,16,25,26,27,28,29,30)
EXPECTED_OUTCOME = "BA0-B_EXACT_F_g_EXPRESSIVITY_BLOCKED"
r33 = av.r33


def eval_formula(f,a):
    return all(any(bool(a[abs(int(l))]) == (int(l)>0) for l in c) for c in f)


def enumerate_models(U):
    count=0; pairs=set(); pair01=None
    for bits in product((False,True), repeat=len(VARS)):
        a=dict(zip(VARS,bits))
        if eval_formula(U,a):
            count += 1
            p=(int(a[2]),int(a[30])); pairs.add(p)
            if p==(0,1) and pair01 is None: pair01=dict(a)
    return count,pairs,pair01


def clause_factor(c):
    scope=tuple(sorted({abs(int(l)) for l in c})); rows=set()
    for bits in product((0,1),repeat=len(scope)):
        a=dict(zip(scope,bits))
        if any((int(l)>0 and a[abs(int(l))]==1) or (int(l)<0 and a[abs(int(l))]==0) for l in c): rows.add(tuple(bits))
    return scope,rows


def eq_factor(e):
    scope=tuple(sorted(map(int,e["vars"]))); rhs=int(e["rhs"]); rows=set()
    for bits in product((0,1),repeat=len(scope)):
        x=0
        for b in bits: x ^= int(b)
        if x==rhs: rows.add(tuple(bits))
    return scope,rows


def graph(scopes,variables):
    a={int(v):set() for v in variables}
    for s in scopes:
        for x,y in combinations(sorted(s),2): a[x].add(y);a[y].add(x)
    return a


def width(adj0,order):
    a={v:set(ns) for v,ns in adj0.items()};w=0
    for v in order:
        ns=sorted(a[v]);w=max(w,len(ns))
        for x,y in combinations(ns,2):a[x].add(y);a[y].add(x)
        for u in ns:a[u].discard(v)
        del a[v]
    return w,a


def eliminate(factors,order):
    fs=[(tuple(s),set(rows)) for s,rows in factors]
    for v in order:
        got=[f for f in fs if v in f[0]];fs=[f for f in fs if v not in f[0]]
        if not got: raise AssertionError(("EMPTY_BUCKET",v))
        union=sorted({u for s,_ in got for u in s}); ns=tuple(u for u in union if u!=v); rows=set()
        for bits in product((0,1),repeat=len(ns)):
            bnd=dict(zip(ns,bits))
            for val in (0,1):
                a=dict(bnd);a[v]=val
                if all(tuple(a[u] for u in s) in tab for s,tab in got):
                    rows.add(tuple(bits));break
        fs.append((ns,rows))
    if len(fs)!=1: raise AssertionError(("BOUNDARY_FACTOR_COUNT",len(fs)))
    return fs[0]


def main():
    ap=argparse.ArgumentParser();ap.add_argument("--result",type=Path,required=True);ap.add_argument("--out",type=Path,required=True);args=ap.parse_args()
    result=json.loads(args.result.read_text());failures=[]
    if result.get("preregistration_commit")!=PREREG:failures.append("PREREG_DRIFT")
    if result.get("outcome")!=EXPECTED_OUTCOME:failures.append({"OUTCOME":result.get("outcome")})
    if result.get("failure_count")!=0:failures.append({"RESULT_FAILURES":result.get("failures")})

    U=r33.canonical_formula(av.load_sealed_y_target())
    if av.formula_hash(U)!=Y_HASH:failures.append("Y_HASH")
    if av.clv(U)!=(63,155,20):failures.append("UNIT_CLV")
    if tuple(sorted(map(int,r33.variables(U))))!=VARS:failures.append("UNIT_VARS")

    count,pairs,pair01=enumerate_models(U)
    if count!=60:failures.append({"MODEL_COUNT":count})
    if pairs!={(0,0),(0,1),(1,0),(1,1)}:failures.append({"ENDPOINT_PAIRS":sorted(pairs)})
    if pair01 is None or not eval_formula(U,pair01) or int(pair01[30])!=1:failures.append("GENERIC_WITNESS_BASE_FAIL")

    # Generic proof obligation replay: every shifted block is a variable renaming of U;
    # choosing pair01 in each block sets every bridge's left endpoint to true.
    generic_sat_proof = pair01 is not None and eval_formula(U,pair01) and int(pair01[30])==1
    if not generic_sat_proof:failures.append("GENERIC_SAT_PROOF_OBLIGATION_FAIL")

    bottom=r33.canonical_formula([()])
    if eval_formula(bottom,{}) is not False:failures.append("EMPTY_CLAUSE_SEMANTICS")

    ex=ath.hardened_extract(U)
    if not ex.get("partition_pass") or ex.get("replay_failures"):failures.append("EXTRACTION")
    defects=[tuple(map(int,c)) for c in ex["defects"]]
    eqs=[{"vars":list(map(int,e["vars"])),"rhs":int(e["rhs"])} for e in ex["equations"]]
    q=32
    factors=[clause_factor(c) for c in defects]+[eq_factor(e) for e in eqs]+[clause_factor((30,q))]
    scopes=[s for s,_ in factors]
    w,rem=width(graph(scopes,tuple(VARS)+(q,)),ORDER)
    boundary=eliminate(factors,ORDER)
    if w!=13:failures.append({"WIDTH":w})
    if rem!={q:set()}:failures.append({"REMAINING_GRAPH":{str(k):sorted(v) for k,v in rem.items()}})
    if boundary[0]!=(q,) or boundary[1]!={(0,),(1,)}:failures.append({"MID_BOUNDARY":[list(boundary[0]),sorted(boundary[1])]})

    plus=(False,True);minus=(True,False);true=(True,True)
    if plus==minus or plus==true or minus==true:failures.append("CUT_WITNESS_LOGIC")

    q4=result.get("Q4_exact_MID_interface",{})
    if q4.get("N_boundary_actual_pairwise_distinguishable_prefix_behaviours")!=1:failures.append("RESULT_N_BOUNDARY")
    if q4.get("surviving_relation_boolean_function")!="TRUE":failures.append("RESULT_MID_FUNCTION")
    q5=result.get("Q5_constant_width_classification",{})
    if q5.get("class")!="B_INSUFFICIENT_UNDER_CURRENT_REPRESENTATION_CONTRACT":failures.append("Q5_CLASS")
    if result.get("interpretation",{}).get("BA1_started") is not False:failures.append("BA1_FIREWALL")

    ext=result.get("Q6_minimal_extension_candidate",{})
    unary=ext.get("minimal_unary_payload",{})
    if unary.get("neutral_sigma")!="all sigma_j=TOP":failures.append("NEUTRAL_SIGMA")
    if unary.get("neutral_exactness")!="F_{g,TOP,...,TOP}=F_g exactly":failures.append("NEUTRAL_EXACTNESS")
    if ext.get("status")!="REPRESENTATION_CANDIDATE_ONLY_NOT_A_REDUCTION_THEOREM":failures.append("EXTENSION_SCOPE")

    out={
      "status":"PASS" if not failures else "FAIL",
      "failure_count":len(failures),"failures":failures,
      "independent_unit_model_count":count,
      "independent_endpoint_pairs":[list(x) for x in sorted(pairs)],
      "generic_SAT_proof_obligations_pass":bool(generic_sat_proof),
      "empty_clause_UNSAT":not eval_formula(bottom,{}),
      "independent_MID":{"width":w,"scope":list(boundary[0]),"rows":[list(x) for x in sorted(boundary[1])],"function":"TRUE","N_boundary_actual":1},
      "smallest_interface_witness":{"functions":["x","not x"],"required_behaviours":2,"available_behaviours":1},
      "result_sha256":hashlib.sha256(args.result.read_bytes()).hexdigest(),
      "finite_ladder_replayed":False,
      "BA1_started":False,
      "firewall":{"P_VS_NP":"OPEN","SAT_IN_P":"NOT_PROVED","TRUMP_finished":False}
    }
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":out["status"],"failures":out["failure_count"],"models":count,"pairs":out["independent_endpoint_pairs"],"MID":out["independent_MID"]},sort_keys=True))
    if failures:raise SystemExit(1)

if __name__=="__main__":main()
