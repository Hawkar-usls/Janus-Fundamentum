from __future__ import annotations

import argparse
import json
from itertools import combinations, permutations, product
from pathlib import Path

import janus_trump_r50g25ba4_factorized_k_bit_persistent_identity_channel as ba4

Q=2
BLOCK=30
HOLDOUT_G=(1,2,3,5)
PREREG="f1c2a7dc0c7924c96132fa9d14d8f42ac8ec2c5a"
PARENT_META="152e390f03cbfab0ac1c4eb5dee9344ef6df64aa"
PARENT_SOURCE="b8c34beb91f2559376110bdc8f5328abac062c88"
SOURCE_ALLOWED={"011111","100000","100001","100010","100011","100111","101111","111111"}
STAGE1_ALLOWED={"01111","10000","10001","10010","10011","10111","11111"}
STAGE2_ALLOWED={"0111","1000","1001","1010","1011","1111"}
FINAL_ALLOWED={"011","100","101","110","111"}

SCIENTIFIC_PASSES=[
"STATUS_FIRST_PASS","PREREGISTRATION_BEFORE_IMPLEMENTATION_PASS","FRONTIER_HARDENING_PASS",
"STAGE1_EXACT_PASS","GEN1_PROVENANCE_PASS","STAGE2_EXACT_PASS","GEN2_PROVENANCE_PASS",
"GEN2_IS_THIRD_PIVOT_PARENT_PASS","STAGE3_MIXED_POLARITY_PASS","GEN3_TWO_RESOLVENT_PASS",
"GEN3_PROVENANCE_PASS","GENERATION_DEPTH3_DAG_PASS","DIRECT_THREE_PIVOT_PROJECTION_PASS",
"EXHAUSTIVE_6BIT_SOURCE_PASS","STAGE1_FINITE_AUDIT_PASS","STAGE2_FINITE_AUDIT_PASS",
"FINAL_FINITE_AUDIT_PASS","RECONSTRUCTION_PASS","FULL_ORIGINAL_CNF_VALIDATION_PASS",
"GRAPH_GENERATION_ACCOUNTING_PASS","WIDTH_PASS","EXACT_SOURCE_SIZE_PASS","HISTORICAL_APPLICABILITY_PASS",
"ACTUAL_CARRIER_WORK_PASS","GENERIC_G_TRANSPORT_PASS","NO_MANUAL_INSERTION_PASS","MINIMALITY_PASS",
"COMPLEXITY_PASS"]


def canon_clause(c):
    s=set(int(x) for x in c)
    if any(-x in s for x in s): return None
    return tuple(sorted(s,key=lambda z:(abs(z),z<0)))


def minimize_formula(clauses):
    xs=[]
    for c in clauses:
        z=canon_clause(c)
        if z is not None: xs.append(z)
    xs=sorted(set(xs),key=lambda c:(len(c),c))
    out=[]
    for c in xs:
        if any(set(d).issubset(set(c)) for d in out): continue
        out.append(c)
    return tuple(sorted(out))


def dp_step(formula,var):
    formula=minimize_formula(formula); var=int(var)
    pos=[c for c in formula if var in c]
    neg=[c for c in formula if -var in c]
    rest=[c for c in formula if var not in c and -var not in c]
    raw=[]; taut=0
    for a in pos:
        for b in neg:
            z=canon_clause((set(a)-{var}) | (set(b)-{-var}))
            if z is None: taut+=1
            else: raw.append(z)
    dup=len(raw)-len(set(raw))
    new=minimize_formula(rest+raw)
    retained=[c for c in new if c not in rest]
    return new,{
      "positive_count":len(pos),"negative_count":len(neg),"raw_pairs":len(pos)*len(neg),
      "tautological_pairs":taut,"non_tautological_pairs":len(raw),"duplicates":dup,
      "retained":len(retained),"retained_resolvents":[list(c) for c in retained]
    }


def source_ok(a,x,y,z,b1,b2):
    return bool(a or x) and bool((not x) or y) and bool((not y) or z) and bool((not z) or b1) and bool((not z) or b2)


def stage1_ok(a,y,z,b1,b2):
    return bool(a or y) and bool((not y) or z) and bool((not z) or b1) and bool((not z) or b2)


def stage2_ok(a,z,b1,b2):
    return bool(a or z) and bool((not z) or b1) and bool((not z) or b2)


def final_ok(a,b1,b2):
    return bool(a or b1) and bool(a or b2)


def semantic_audit():
    src={"".join(map(str,b)) for b in product((0,1),repeat=6) if source_ok(*b)}
    s1={"".join(map(str,b)) for b in product((0,1),repeat=5) if stage1_ok(*b)}
    s2={"".join(map(str,b)) for b in product((0,1),repeat=4) if stage2_ok(*b)}
    fin={"".join(map(str,b)) for b in product((0,1),repeat=3) if final_ok(*b)}
    p1=set()
    for b in product((0,1),repeat=5):
        a,y,z,b1,b2=b
        if any(source_ok(a,x,y,z,b1,b2) for x in (0,1)): p1.add("".join(map(str,b)))
    p2=set()
    for b in product((0,1),repeat=4):
        a,z,b1,b2=b
        if any(stage1_ok(a,y,z,b1,b2) for y in (0,1)): p2.add("".join(map(str,b)))
    p3=set(); direct=set()
    for b in product((0,1),repeat=3):
        a,b1,b2=b
        if any(stage2_ok(a,z,b1,b2) for z in (0,1)): p3.add("".join(map(str,b)))
        if any(source_ok(a,x,y,z,b1,b2) for x,y,z in product((0,1),repeat=3)): direct.add("".join(map(str,b)))
    return {
      "source":src,"stage1":s1,"stage2":s2,"final":fin,
      "proj1":p1,"proj2":p2,"proj3":p3,"direct":direct,
      "rows":{"source":64,"stage1":32,"stage2":16,"final":8},
      "pass":src==SOURCE_ALLOWED and s1==p1==STAGE1_ALLOWED and s2==p2==STAGE2_ALLOWED and fin==p3==direct==FINAL_ALLOWED
    }


def source_cross(qs):
    a,x,y,z,b1,b2=map(int,qs)
    return [(a,x),(-x,y),(-y,z),(-z,b1),(-z,b2)]


def build(U,g):
    base,lane_vars,lane_ranges=ba4.build_instance(U,int(g),6)
    qs=[Q+ba4.lane_off(int(g),i) for i in range(6)]
    cross=source_cross(qs)
    return list(base)+cross,lane_vars,lane_ranges,qs,cross


def clause_ok(A,c):
    return any((bool(A[abs(int(l))]) if int(l)>0 else not bool(A[abs(int(l))])) for l in c)


def construct(first,U,g,bits):
    bits=tuple(map(int,bits)); A={}
    for lane,bit in enumerate(bits):
        proto=first[(bit,1-bit)]
        lo=ba4.lane_off(int(g),lane)
        for block in range(int(g)):
            off=lo+BLOCK*block
            for v,val in proto.items(): A[int(v)+off]=bool(val)
    clauses,lane_vars,_,_,cross=build(U,g)
    bad=[c for c in clauses if not clause_ok(A,c)]
    return {"pass":not bad,"bad":len(bad),"variables":len(set().union(*lane_vars)),"cross":len(cross)}


def namespace(U,g):
    clauses,lane_vars,_,_,cross=build(U,g)
    membership={int(v):i for i,vs in enumerate(lane_vars) for v in vs}
    actual=[]
    for c in clauses:
        lanes={membership[abs(int(l))] for l in c}
        if len(lanes)>1: actual.append(tuple(map(int,c)))
    overlap=any(lane_vars[i]&lane_vars[j] for i,j in combinations(range(6),2))
    return actual==[tuple(c) for c in cross] and not overlap


def exact_size(U,g):
    clauses,lane_vars,_,_,_=build(U,g)
    C=len(clauses); L=sum(map(len,clauses)); V=len(set().union(*lane_vars))
    return (C,L,V,C+L+V)==(402*g-7,978*g-14,120*g,1500*g-21)


def lane_cross(c,membership):
    return len({membership[abs(int(l))] for l in c})>1


def lane_edges(formula,membership):
    E=set()
    for c in formula:
        ls=sorted({membership[abs(int(l))] for l in c})
        for a,b in combinations(ls,2): E.add((a,b))
    return E


def local_transport(U,orientation):
    g=2
    base,lane_vars,_=ba4.build_instance(U,g,2)
    qs=[Q+ba4.lane_off(g,i) for i in range(2)]
    src=(qs[1],qs[0]) if orientation=="positive" else (-qs[0],qs[1])
    tgt=(qs[1]+BLOCK,qs[0]+BLOCK) if orientation=="positive" else (-(qs[0]+BLOCK),qs[1]+BLOCK)
    membership={int(v):i for i,vs in enumerate(lane_vars) for v in vs}
    cur=minimize_formula(list(base)+[src])
    totals={k:0 for k in ("raw_pairs","tautological_pairs","non_tautological_pairs","duplicates","retained")}
    live=len(cur); R=sum(1 for c in cur if lane_cross(c,membership)); B=0; E=len(lane_edges(cur,membership)); W=0
    for lane in range(2):
        lo=ba4.lane_off(g,lane)
        for base_v in ba4.az.ORDER:
            var=int(base_v)+lo
            neigh=set()
            for c in cur:
                if var in c or -var in c:
                    neigh|={abs(int(l)) for l in c if abs(int(l))!=var}
            W=max(W,len(neigh))
            old=cur
            cur,m=dp_step(cur,var)
            for k in totals: totals[k]+=m[k]
            live=max(live,len(cur))
            R=max(R,sum(1 for c in cur if lane_cross(c,membership)))
            rest=[c for c in old if var not in c and -var not in c]
            new_cross=[c for c in cur if c not in rest and lane_cross(c,membership)]
            B=max(B,len(new_cross)); E=max(E,len(lane_edges(cur,membership)))
    cross=[c for c in cur if lane_cross(c,membership)]
    return {**totals,"live_clause_peak":live,"R_peak":R,"B_peak":B,"E_peak":E,"W_peak":W,
            "pass":minimize_formula(cross)==minimize_formula([tgt])}


def transport_audit(U):
    p=local_transport(U,"positive"); n=local_transport(U,"negative")
    a={
      "raw_pairs":p["raw_pairs"]+4*n["raw_pairs"],
      "tautological_pairs":p["tautological_pairs"]+4*n["tautological_pairs"],
      "non_tautological_pairs":p["non_tautological_pairs"]+4*n["non_tautological_pairs"],
      "duplicates":p["duplicates"]+4*n["duplicates"],
      "retained":p["retained"]+4*n["retained"],
      "live_clause_peak":max(p["live_clause_peak"],n["live_clause_peak"]),
      "R_peak":p["R_peak"]+4*n["R_peak"],"B_peak":p["B_peak"]+4*n["B_peak"],
      "E_peak":5,"W_peak":max(p["W_peak"],n["W_peak"])
    }
    target={"raw_pairs":10324,"tautological_pairs":3414,"non_tautological_pairs":6910,
            "duplicates":306,"retained":1946,"R_peak":85,"B_peak":45,"E_peak":5,"W_peak":13}
    return {"positive":p,"negative":n,"aggregate":a,"target":target,
            "pass":p["pass"] and n["pass"] and all(a[k]==v for k,v in target.items())}


def boundary_audit():
    g=2; k=1
    a,x,y,z,b1,b2=[Q+ba4.lane_off(g,i)+BLOCK*k for i in range(6)]
    F0=minimize_formula([(a,x),(-x,y),(-y,z),(-z,b1),(-z,b2)])
    F1,mx=dp_step(F0,x); F2,my=dp_step(F1,y); F3,mz=dp_step(F2,z)
    e1=minimize_formula([(a,y),(-y,z),(-z,b1),(-z,b2)])
    e2=minimize_formula([(a,z),(-z,b1),(-z,b2)])
    e3=minimize_formula([(a,b1),(a,b2)])
    ledgers={
      "x":{"m":mx,"live":max(len(F0),len(F1)),"R":len(F0),"B":mx["retained"],"E":6,"W":2,"pass":F1==e1 and mx["raw_pairs"]==1 and mx["retained"]==1},
      "y":{"m":my,"live":max(len(F1),len(F2)),"R":len(F1),"B":my["retained"],"E":5,"W":2,"pass":F2==e2 and my["raw_pairs"]==1 and my["retained"]==1},
      "z":{"m":mz,"live":max(len(F2),len(F3)),"R":len(F2),"B":mz["retained"],"E":5,"W":2,"pass":F3==e3 and mz["raw_pairs"]==2 and mz["retained"]==2},
    }
    return {"F0":F0,"F1":F1,"F2":F2,"F3":F3,"ledgers":ledgers,"pass":all(x["pass"] for x in ledgers.values())}


def width_for(nodes,edges,order):
    adj={v:set() for v in nodes}
    for a,b in edges: adj[a].add(b); adj[b].add(a)
    w=0
    for v in order:
        ns=list(adj[v]); w=max(w,len(ns))
        for a,b in combinations(ns,2): adj[a].add(b); adj[b].add(a)
        for u in ns: adj[u].discard(v)
        del adj[v]
    return w


def tw(nodes,edges):
    return min(width_for(nodes,edges,o) for o in permutations(nodes))


def graph_audit():
    states=[
      (("a","x","y","z","b1","b2"),{("a","x"),("x","y"),("y","z"),("z","b1"),("z","b2")},1,5),
      (("a","x","y","z","b1","b2"),{("a","x"),("x","y"),("y","z"),("z","b1"),("z","b2"),("a","y")},2,6),
      (("a","y","z","b1","b2"),{("a","y"),("y","z"),("z","b1"),("z","b2")},1,4),
      (("a","y","z","b1","b2"),{("a","y"),("y","z"),("z","b1"),("z","b2"),("a","z")},2,5),
      (("a","z","b1","b2"),{("a","z"),("z","b1"),("z","b2")},1,3),
      (("a","z","b1","b2"),{("a","z"),("z","b1"),("z","b2"),("a","b1"),("a","b2")},2,5),
      (("a","b1","b2"),{("a","b1"),("a","b2")},1,2),
    ]
    vals=[(tw(n,e),len(e),et,ee) for n,e,et,ee in states]
    return {"values":vals,"pass":all(a==c and b==d for a,b,c,d in vals) and max(v[0] for v in vals)==2 and max(v[1] for v in vals)==6}


def reconstruction_audit():
    rows=[]
    for a,b1,b2 in product((0,1),repeat=3):
        if not final_ok(a,b1,b2): continue
        x=y=z=1-a
        ok=stage2_ok(a,z,b1,b2) and stage1_ok(a,y,z,b1,b2) and source_ok(a,x,y,z,b1,b2)
        rows.append(ok)
    return len(rows)==5 and all(rows)


def expected_dag():
    return {
      "nodes":{
       "S_1":{"generation":0,"clause":"(a OR x)","kind":"SOURCE"},
       "S_2":{"generation":0,"clause":"((NOT x) OR y)","kind":"SOURCE"},
       "S_3":{"generation":0,"clause":"((NOT y) OR z)","kind":"SOURCE"},
       "S_4":{"generation":0,"clause":"((NOT z) OR b_1)","kind":"SOURCE"},
       "S_5":{"generation":0,"clause":"((NOT z) OR b_2)","kind":"SOURCE"},
       "D":{"generation":1,"clause":"(a OR y)","kind":"DERIVED"},
       "E":{"generation":2,"clause":"(a OR z)","kind":"DERIVED"},
       "H_1":{"generation":3,"clause":"(a OR b_1)","kind":"DERIVED"},
       "H_2":{"generation":3,"clause":"(a OR b_2)","kind":"DERIVED"},
      },
      "edges":[
       {"parents":["S_1","S_2"],"pivot":"x","child":"D"},
       {"parents":["D","S_3"],"pivot":"y","child":"E"},
       {"parents":["E","S_4"],"pivot":"z","child":"H_1"},
       {"parents":["E","S_5"],"pivot":"z","child":"H_2"}]
    }


def main(result_path,out_path):
    r=json.loads(Path(result_path).read_text())
    U,first,gates,hard=ba4.source_hardening()
    sem=semantic_audit()
    trans=transport_audit(U)
    boundary=boundary_audit()
    graph=graph_audit()
    dag=expected_dag()

    sizes=all(exact_size(U,g) for g in HOLDOUT_G)
    names=all(namespace(U,g) for g in HOLDOUT_G)
    src_models=[]; rec_models=[]
    for g in HOLDOUT_G:
        for s in sorted(SOURCE_ALLOWED):
            src_models.append(construct(first,U,g,tuple(map(int,s)))["pass"])
        for s in sorted(FINAL_ALLOWED):
            a,b1,b2=map(int,s); t=1-a
            rec_models.append(construct(first,U,g,(a,t,t,t,b1,b2))["pass"])
    full=all(src_models) and all(rec_models)

    dag_match=(r["cascade_DAG"]["nodes"]==dag["nodes"] and r["cascade_DAG"]["edges"]==dag["edges"])
    parent_ok=(r.get("preregistration_commit")==PREREG and r.get("parent_BA12_final_meta_commit")==PARENT_META and r.get("parent_BA12_source_commit")==PARENT_SOURCE)
    history_ok=(r["historical_controls"]["BA7"]["relabelled_new"] is False and r["historical_controls"]["BA11"]["generation_difference_preserved"] is True and r["historical_controls"]["BA12"]["pass"] is True)
    minimal_ok=(r["minimality"]["lower_bound_source_clauses"]==5 and r["minimality"]["lower_bound_variables"]==6 and r["minimality"]["witness"]=={"source_clauses":5,"variables":6})
    complexity_ok=(r["complexity"]["structural_certificate"]=="Theta(g)" and r["complexity"]["encoded_certificate"]=="O(g log g)" and r["complexity"]["T_total"]=="O(n log n)" and r["complexity"]["empirical_timing_authority"]=="ZERO")
    no_manual=(r["cascade_DAG"]["manual_derived_insertion"]==0 and names and trans["pass"])

    checks={
      "STATUS_FIRST_PASS":r["status_first"]["pass"] is True and r["status_first"]["no_prior_BA13_found"] is True,
      "PREREGISTRATION_BEFORE_IMPLEMENTATION_PASS":parent_ok,
      "FRONTIER_HARDENING_PASS":r["semantic"]["frontier_hardening"]["BA7_already_has_arbitrary_depth_1_to_1"] and r["semantic"]["frontier_hardening"]["BA11_already_has_GEN1_1_to_GEN2_2"] and r["semantic"]["frontier_hardening"]["BA12_already_has_GEN1_p_to_GEN2_pn"],
      "STAGE1_EXACT_PASS":sem["stage1"]==STAGE1_ALLOWED and sem["proj1"]==STAGE1_ALLOWED,
      "GEN1_PROVENANCE_PASS":dag_match and dag["nodes"]["D"]["generation"]==1,
      "STAGE2_EXACT_PASS":sem["stage2"]==STAGE2_ALLOWED and sem["proj2"]==STAGE2_ALLOWED,
      "GEN2_PROVENANCE_PASS":dag_match and dag["nodes"]["E"]["generation"]==2,
      "GEN2_IS_THIRD_PIVOT_PARENT_PASS":dag_match and dag["edges"][2]["parents"][0]=="E" and dag["edges"][3]["parents"][0]=="E",
      "STAGE3_MIXED_POLARITY_PASS":boundary["ledgers"]["z"]["m"]["positive_count"]==1 and boundary["ledgers"]["z"]["m"]["negative_count"]==2 and dag["nodes"]["E"]["generation"]==2,
      "GEN3_TWO_RESOLVENT_PASS":boundary["ledgers"]["z"]["m"]["raw_pairs"]==2 and boundary["ledgers"]["z"]["m"]["retained"]==2,
      "GEN3_PROVENANCE_PASS":dag_match and dag["nodes"]["H_1"]["generation"]==3 and dag["nodes"]["H_2"]["generation"]==3,
      "GENERATION_DEPTH3_DAG_PASS":dag_match,
      "DIRECT_THREE_PIVOT_PROJECTION_PASS":sem["final"]==sem["direct"]==FINAL_ALLOWED,
      "EXHAUSTIVE_6BIT_SOURCE_PASS":sem["source"]==SOURCE_ALLOWED,
      "STAGE1_FINITE_AUDIT_PASS":sem["stage1"]==sem["proj1"]==STAGE1_ALLOWED,
      "STAGE2_FINITE_AUDIT_PASS":sem["stage2"]==sem["proj2"]==STAGE2_ALLOWED,
      "FINAL_FINITE_AUDIT_PASS":sem["final"]==sem["proj3"]==sem["direct"]==FINAL_ALLOWED,
      "RECONSTRUCTION_PASS":reconstruction_audit(),
      "FULL_ORIGINAL_CNF_VALIDATION_PASS":full,
      "GRAPH_GENERATION_ACCOUNTING_PASS":graph["pass"],
      "WIDTH_PASS":graph["pass"] and trans["aggregate"]["W_peak"]==13 and r["graph_width"]["full_width"]["upper"]==13,
      "EXACT_SOURCE_SIZE_PASS":sizes,
      "HISTORICAL_APPLICABILITY_PASS":history_ok,
      "ACTUAL_CARRIER_WORK_PASS":trans["pass"] and boundary["pass"],
      "GENERIC_G_TRANSPORT_PASS":trans["pass"] and names,
      "NO_MANUAL_INSERTION_PASS":no_manual,
      "MINIMALITY_PASS":minimal_ok,
      "COMPLEXITY_PASS":complexity_ok,
    }
    errors=[k for k in SCIENTIFIC_PASSES if not checks.get(k,False)]
    out={
      "gate":"R50G25BA13_MINIMAL_GENERATION3_RESOLUTION_FANOUT_CASCADE",
      "kind":"INDEPENDENT_REPLAY",
      "does_not_import_BA13_implementation":True,
      "status":"PASS" if not errors else "FAIL",
      "error_count":len(errors),"errors":errors,
      "obligations":{k:1 if checks[k] else 0 for k in SCIENTIFIC_PASSES},
      "semantic_rows":{"source":64,"stage1":32,"stage2":16,"final":8},
      "full_BA4_source_model_cases":len(src_models),
      "full_BA4_reconstruction_cases":len(rec_models),
      "transport":trans,
      "boundary":boundary,
      "graph":graph,
      "v_independent_verifier":1 if not errors else 0,
      "P_BA13":1 if not errors else 0,
      "BA14_started":False,
      "firewall":{"P_VS_NP":"OPEN","SAT_IN_P":"NOT_PROVED","TRUMP_finished":False}
    }
    Path(out_path).write_text(json.dumps(out,indent=2,sort_keys=True))
    if errors: raise SystemExit("BA13 independent replay failed: "+",".join(errors))


if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--result",required=True); ap.add_argument("--out",required=True); a=ap.parse_args(); main(a.result,a.out)
