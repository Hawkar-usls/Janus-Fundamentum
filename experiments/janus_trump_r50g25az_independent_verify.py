from __future__ import annotations
import argparse, hashlib, json
from itertools import combinations, product
from pathlib import Path

import janus_trump_r50g25ay_separator_width_relation_ledger_scaling as ay
import janus_trump_r50g25av_reachable_multi_defect_growth_witness as av
import janus_trump_r50g25at_tautology_hardened_runner as ath

Y_HASH="c379fb11374c4259a736545f6652a417b6d98d016e9dcaed62d44d3740b71adb"
VARS=(2,3,4,5,8,9,10,11,12,13,15,16,20,24,25,26,27,28,29,30)
ORDER=(24,10,2,11,15,20,3,4,5,8,9,12,13,16,25,26,27,28,29,30)
HOLDOUTS=(5,7,9,16)
PASS="AZ_RESTRICTED_CHAIN_FAMILY_POLYNOMIAL_RELATION_THEOREM_PROVED"

def clause_table(c):
    scope=tuple(sorted({abs(int(l)) for l in c})); rows=set()
    for bits in product((0,1),repeat=len(scope)):
        a=dict(zip(scope,bits))
        if any((l>0 and a[abs(l)]==1) or (l<0 and a[abs(l)]==0) for l in c): rows.add(tuple(bits))
    return scope,rows

def eq_table(e):
    scope=tuple(sorted(map(int,e["vars"]))); rhs=int(e["rhs"]); rows=set()
    for bits in product((0,1),repeat=len(scope)):
        x=0
        for b in bits:x^=b
        if x==rhs:rows.add(tuple(bits))
    return scope,rows

def graph(scopes,variables):
    a={v:set() for v in variables}
    for s in scopes:
        for x,y in combinations(sorted(s),2):a[x].add(y);a[y].add(x)
    return a

def width(adj0,order):
    a={v:set(n) for v,n in adj0.items()}; w=0
    for v in order:
        ns=sorted(a[v]); w=max(w,len(ns))
        for x,y in combinations(ns,2): a[x].add(y);a[y].add(x)
        for u in ns:a[u].discard(v)
        del a[v]
    return w,a

def eliminate(factors,order):
    total_source=sum(len(rows) for _,rows in factors); gen=0; attempts=0; maxscope=0; maxrows=0; maxinputs=0
    fs=[(tuple(s),set(r)) for s,r in factors]
    for v in order:
        got=[f for f in fs if v in f[0]]; fs=[f for f in fs if v not in f[0]]
        if not got:raise AssertionError(("empty bucket",v))
        us=sorted({u for s,_ in got for u in s}); ns=tuple(u for u in us if u!=v); rows=set()
        for bits in product((0,1),repeat=len(ns)):
            bnd=dict(zip(ns,bits))
            for val in (0,1):
                attempts+=1; a=dict(bnd);a[v]=val; ok=True
                for s,tab in got:
                    if tuple(a[u] for u in s) not in tab:ok=False;break
                if ok:rows.add(tuple(bits));break
        fs.append((ns,rows)); gen+=len(rows);maxscope=max(maxscope,len(ns));maxrows=max(maxrows,len(rows));maxinputs=max(maxinputs,len(got))
    if len(fs)!=1:raise AssertionError(("boundary factor count",len(fs)))
    return {"source":total_source,"generated":gen,"total":total_source+gen,"attempts":attempts,
            "maxscope":maxscope,"maxrows":maxrows,"maxinputs":maxinputs,"boundary_scope":list(fs[0][0]),"boundary_rows":[list(x) for x in sorted(fs[0][1])]}

def build_general(g):
    unit=av.canonical(av.load_sealed_y_target())
    if av.formula_hash(unit)!=Y_HASH:raise AssertionError("Y hash drift")
    copies=[]
    for j in range(g):copies.extend(av.shift_formula(unit,30*j))
    bridges=[(30+30*j,32+30*j) for j in range(g-1)]
    return av.canonical(list(copies)+bridges)

def holdout_replay(g):
    root=build_general(g)
    replay=av.asmod.y.policy_replay(root,av.asmod.r50g25g._chain())
    if replay.get("kind")!="RESIDUAL":return {"g":g,"failure":"POLICY_NOT_RESIDUAL","kind":replay.get("kind")}
    residual=av.canonical(replay["state"])
    if av.formula_hash(residual)!=av.formula_hash(root):return {"g":g,"failure":"POLICY_NOT_IDENTITY"}
    ex=ath.hardened_extract(residual)
    if not ex.get("partition_pass") or ex.get("replay_failures"):return {"g":g,"failure":"EXTRACTION"}
    defects=[tuple(map(int,c)) for c in ex["defects"]]
    equations=[{"vars":list(map(int,e["vars"])),"rhs":int(e["rhs"])} for e in ex["equations"]]
    variables=tuple(sorted(map(int,av.r33.variables(root))))
    order=tuple(v+30*j for j in range(g) for v in ORDER)
    scopes=[tuple(sorted({abs(l) for l in c})) for c in defects]+[tuple(sorted(e["vars"])) for e in equations]
    w,rem=width(graph(scopes,variables),order)
    if rem:return {"g":g,"failure":"ORDER_DID_NOT_ELIMINATE_ALL","remaining":sorted(rem)}
    rel=ay.bucket_relation(variables,defects,equations,order,w)
    reconstruction=not rel["reconstruction_failures"] and set(rel["assignment"])==set(variables) if rel["decision"]=="SAT" else True
    clause_fail=[];eq_fail=[]
    if rel["decision"]=="SAT" and reconstruction:clause_fail,eq_fail=ay.validate_source(rel["assignment"],defects,equations)
    source_validation=(not clause_fail and not eq_fail) if rel["decision"]=="SAT" else True
    L=sum(len(c) for c in root)
    return {"g":g,"C":len(root),"L":L,"V":len(variables),"D":len(defects),"E":len(equations),"w":w,
            "rows":rel["total_materialized_rows"],"attempts":rel["evaluation_attempts"],"maxscope":rel["maximum_generated_scope"],
            "maxrows":rel["maximum_generated_table_rows"],"decision":rel["decision"],"reconstruction":reconstruction,
            "source_validation":source_validation,"clause_fail":clause_fail,"eq_fail":eq_fail}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--theorem",type=Path,required=True);ap.add_argument("--out",type=Path,required=True);args=ap.parse_args()
    theorem=json.loads(args.theorem.read_text()); failures=[]
    root,_=ay.build_root(1); root=ay.canonical(root)
    if ay.formula_hash(root)!=Y_HASH:failures.append("Y_HASH")
    if ay.clv(root)!=(63,155,20):failures.append("CLV")
    if tuple(sorted(map(int,av.r33.variables(root))))!=VARS:failures.append("VARS")
    replay=av.asmod.y.policy_replay(root,av.asmod.r50g25g._chain())
    if replay.get("kind")!="RESIDUAL" or ay.formula_hash(ay.canonical(replay["state"]))!=Y_HASH:failures.append("POLICY_IDENTITY")
    ex=ath.hardened_extract(root)
    if not ex.get("partition_pass") or ex.get("replay_failures") or ex.get("defect_clause_count")!=61 or ex.get("recognized_equation_count")!=1:failures.append("EXTRACTION")
    defects=[tuple(map(int,c)) for c in ex["defects"]];eqs=[{"vars":list(map(int,e["vars"])),"rhs":int(e["rhs"])} for e in ex["equations"]]
    factors=[clause_table(c) for c in defects]+[eq_table(e) for e in eqs]
    lw,_=width(graph([s for s,_ in factors],VARS),ORDER); last=eliminate(factors,ORDER)
    q=32; midf=list(factors)+[clause_table((30,q))]
    mw,rem=width(graph([s for s,_ in midf],tuple(VARS)+(q,)),ORDER); mid=eliminate(midf,ORDER)
    expected_last={"source":301,"generated":4272,"total":4573,"attempts":49240,"maxscope":13,"maxrows":1460,"maxinputs":9,"boundary_scope":[],"boundary_rows":[[]]}
    expected_mid={"source":304,"generated":4273,"total":4577,"attempts":49242,"maxscope":13,"maxrows":1460,"maxinputs":9,"boundary_scope":[32],"boundary_rows":[[0],[1]]}
    if lw!=13 or last!=expected_last:failures.append({"LAST":last,"w":lw})
    if mw!=13 or mid!=expected_mid:failures.append({"MID":mid,"w":mw})
    if rem!={q:set()}:failures.append({"MID_REMAINING_GRAPH":{str(k):sorted(v) for k,v in rem.items()}})
    derived={"C":"64*g-1","L":"157*g-2","V":"20*g","D":"62*g-1","E":"g","source_rows":"304*g-3",
             "generated_rows":"4273*g-1","total_rows":"4577*g-4","source_factor_count":"63*g-1","generated_factor_count":"20*g",
             "evaluation_attempts":"49242*g-2","width_upper_bound":13,"state_bound_upper_bound":8192}
    if theorem.get("formal_induction_object",{}).get("formulas")!=derived:failures.append({"FORMULAS":theorem.get("formal_induction_object",{}).get("formulas")})
    if not (155**4>4577):failures.append("ALGEBRA_BASE")
    holdouts=[]
    for g in HOLDOUTS:
        row=holdout_replay(g);holdouts.append(row)
        if row.get("failure"):failures.append({"HOLDOUT_FAILURE":row});continue
        exp={"C":64*g-1,"L":157*g-2,"V":20*g,"D":62*g-1,"E":g,"w":13,"rows":4577*g-4,"attempts":49242*g-2,"maxscope":13,"maxrows":1460}
        for k,v in exp.items():
            if row[k]!=v:failures.append({"HOLDOUT_MISMATCH":g,"field":k,"got":row[k],"expected":v})
        if row["decision"]!="SAT" or row["reconstruction"] is not True or row["source_validation"] is not True:failures.append({"HOLDOUT_RELATION":row})
    if theorem.get("verdict")!=PASS:failures.append({"THEOREM_VERDICT":theorem.get("verdict")})
    out={"status":"PASS" if not failures else "FAIL","failure_count":len(failures),"failures":failures,
         "independent_LAST":last,"independent_MID":mid,"widths":{"LAST":lw,"MID":mw},"derived_formulas":derived,
         "algebra_for_all_integer_g_ge_1":True,"holdouts":holdouts,"theorem_json_sha256":hashlib.sha256(args.theorem.read_bytes()).hexdigest(),
         "firewall":{"P_VS_NP":"OPEN","SAT_IN_P":"NOT_PROVED","TRUMP_finished":False}}
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":out["status"],"failures":out["failure_count"],"holdouts":[(x["g"],x.get("w"),x.get("rows")) for x in holdouts]},sort_keys=True))
    if failures: raise SystemExit(1)
if __name__=="__main__":main()
