from __future__ import annotations

import argparse
import hashlib
import json
from itertools import product, combinations, permutations
from pathlib import Path

import janus_trump_r50g25ba4_factorized_k_bit_persistent_identity_channel as ba4

PREREG="5eb4b97caf606d5a8ebe965dc72765a1627066dd"
HOLDOUTS=((1,1,1),(1,2,1),(1,2,2),(2,2,2),(2,3,2),(3,2,3))
Q=2
BLOCK=30

def canon(c):
    s=set(int(x) for x in c)
    if any(-x in s for x in s): return None
    return tuple(sorted(s,key=lambda z:(abs(z),z<0)))

def mini(cs):
    xs=[]
    for c in cs:
        z=canon(c)
        if z is not None: xs.append(z)
    xs=sorted(set(xs),key=lambda c:(len(c),c)); out=[]
    for c in xs:
        if any(set(d).issubset(set(c)) for d in out): continue
        out.append(c)
    return tuple(sorted(out))

def dp(F,v):
    F=mini(F); pos=[c for c in F if v in c]; neg=[c for c in F if -v in c]
    rest=mini([c for c in F if v not in c and -v not in c]); restset=set(rest)
    raw=[]; taut=0
    for a in pos:
        for b in neg:
            z=canon((set(a)-{v})|(set(b)-{-v}))
            if z is None: taut+=1
            else: raw.append(z)
    new_unique={z for z in set(raw) if z not in restset}
    return mini(list(rest)+raw),{
      "raw":len(pos)*len(neg),"taut":taut,"non":len(raw),
      "new":len(new_unique),"dup":len(raw)-len(new_unique)}

def var_ids(p,n,r):
    q=1; A=list(range(q,q+p));q+=p;x=q;q+=1;y=q;q+=1
    B=list(range(q,q+n));q+=n;z=q;q+=1;C=list(range(q,q+r))
    return A,x,y,B,z,C

def replay_abstract(p,n,r):
    A,x,y,B,z,C=var_ids(p,n,r)
    F=mini([(a,x) for a in A]+[(-x,y)]+[(-y,b) for b in B]+[(-b,z) for b in B]+[(-z,c) for c in C])
    F,mz=dp(F,z); support=mini([(-b,c) for b in B for c in C])
    expz=mini([(a,x) for a in A]+[(-x,y)]+[(-y,b) for b in B]+list(support))
    zpass=F==expz and mz["raw"]==n*r and mz["new"]==n*r
    F,mx=dp(F,x); expx=mini([(a,y) for a in A]+[(-y,b) for b in B]+list(support))
    xpass=F==expx and mx["raw"]==p
    F,my=dp(F,y); expy=mini([(a,b) for a in A for b in B]+list(support))
    ypass=F==expy and my["raw"]==p*n
    raw=new=dup=0; led=[]
    for j,b in enumerate(B,1):
        F,m=dp(F,b); raw+=m["raw"];new+=m["new"];dup+=m["dup"];led.append((j,m))
    final=mini([(a,c) for a in A for c in C])
    return {
      "p":p,"n":n,"r":r,"z":zpass,"x":xpass,"y":ypass,
      "raw":raw,"new":new,"dup":dup,
      "expected_raw":p*n*r,"expected_new":p*r,"expected_dup":p*r*(n-1),
      "first_new":led[0][1]["new"],"later_new":[m["new"] for _,m in led[1:]],
      "final_exact":F==final,"pass":zpass and xpass and ypass and raw==p*n*r and new==p*r and dup==p*r*(n-1) and F==final}

def elim_width(nodes,edges,order):
    adj={v:set() for v in nodes}
    for a,b in edges: adj[a].add(b);adj[b].add(a)
    w=0
    for v in order:
        ns=list(adj[v]);w=max(w,len(ns))
        for a,b in combinations(ns,2):adj[a].add(b);adj[b].add(a)
        for u in ns:adj[u].discard(v)
        del adj[v]
    return w

def exact_tw(nodes,edges):
    return min(elim_width(nodes,edges,o) for o in permutations(nodes))

def width_counterexample():
    p,n,r=1,2,1
    A=["a1"];B=["b1","b2"];C=["c1"]
    E={tuple(sorted(e)) for e in
       ({("a1","y")}|{("y",b) for b in B}|{(b,"c1") for b in B}|{("a1",b) for b in B})}
    nodes=A+["y"]+B+C
    ty=exact_tw(tuple(nodes),E)
    frozen=p+n+r-max(p,n,r)
    return {"p":p,"n":n,"r":r,"T_y_exact":ty,"frozen_candidate":frozen,
            "falsifies":ty!=frozen and ty==3 and frozen==2}

def corrected_width_formula(p,n,r):
    ty=min(n+1,p+r+1)
    tb=p+n+r-max(p,n,r)
    return max(ty,tb)

def source_size_replay():
    out=[]
    for p,n,r in HOLDOUTS:
        D=p+n+r+3
        for g in (1,2):
            C=D*(67*g-2)+(p+2*n+r+1)
            L=D*(163*g-4)+2*(p+2*n+r+1)
            V=20*g*D
            expected=(67*g*D-p-r-5,163*g*D-2*p-2*r-10,20*g*D,250*g*D-3*p-3*r-15)
            out.append({"p":p,"n":n,"r":r,"g":g,"actual":(C,L,V,C+L+V),"expected":expected,
                        "pass":(C,L,V,C+L+V)==expected})
    return out

def carrier_dp(F,v):
    F=mini(F); pos=[c for c in F if v in c];neg=[c for c in F if -v in c]
    rest=[c for c in F if v not in c and -v not in c];raw=[];taut=0
    for a in pos:
        for b in neg:
            z=canon((set(a)-{v})|(set(b)-{-v}))
            if z is None:taut+=1
            else:raw.append(z)
    dup=len(raw)-len(set(raw));new=mini(rest+raw);ret=[c for c in new if c not in rest]
    return new,{"raw_pairs":len(pos)*len(neg),"tautological":taut,"non_tautological":len(raw),"duplicates":dup,"retained":len(ret)}

def cross(c,m):
    return len({m[abs(int(l))] for l in c})>1

def carrier_local(U,orientation):
    base,lanes,_=ba4.build_instance(U,2,2)
    qs=[Q+ba4.lane_off(2,i) for i in range(2)]
    src=(qs[1],qs[0]) if orientation=="positive" else (-qs[0],qs[1])
    target=(qs[1]+BLOCK,qs[0]+BLOCK) if orientation=="positive" else (-(qs[0]+BLOCK),qs[1]+BLOCK)
    m={int(v):i for i,vs in enumerate(lanes) for v in vs};F=mini(list(base)+[src])
    totals={"raw_pairs":0,"tautological":0,"non_tautological":0,"duplicates":0,"retained":0}
    R=0;Bpk=0;W=0
    for lane in range(2):
        lo=ba4.lane_off(2,lane)
        for base_v in ba4.az.ORDER:
            v=int(base_v)+lo
            neigh=set()
            for c in F:
                if v in c or -v in c:neigh|={abs(int(l)) for l in c if abs(int(l))!=v}
            W=max(W,len(neigh));old=F;F,s=carrier_dp(F,v)
            for k in totals:totals[k]+=s[k]
            R=max(R,sum(1 for c in F if cross(c,m)))
            rest=[c for c in old if v not in c and -v not in c]
            Bpk=max(Bpk,len([c for c in F if c not in rest and cross(c,m)]))
    rem=mini([c for c in F if cross(c,m)])
    return {**totals,"R_peak":R,"B_peak":Bpk,"W_peak":W,"exact":rem==mini([target])}

def source_ok(bits,p,n,r):
    a=bits[:p];q=p;x=bits[q];y=bits[q+1];q+=2;b=bits[q:q+n];q+=n;z=bits[q];q+=1;c=bits[q:q+r]
    return all(ai or x for ai in a) and ((not x) or y) and all((not y) or bj for bj in b) and all((not bj) or z for bj in b) and all((not z) or ck for ck in c)

def final_ok(bits,p,r):
    a=bits[:p];c=bits[p:]
    return all(ai or ck for ai in a for ck in c)

def lift(bits,p,n,r):
    a=bits[:p];c=bits[p:];t=1-int(all(a))
    return tuple(a)+(t,t)+tuple([t]*n)+(t,)+tuple(c)

def ba4_model(first,U,g,p,n,r,bits):
    assignment={}
    for lane,bit in enumerate(bits):
        proto=first[(int(bit),1-int(bit))];lo=ba4.lane_off(g,lane)
        for block in range(g):
            off=lo+BLOCK*block
            for v,val in proto.items():assignment[int(v)+off]=bool(val)
    D=p+n+r+3;base,_,_=ba4.build_instance(U,g,D);qs=[Q+ba4.lane_off(g,i) for i in range(D)]
    q=0;A=qs[:p];q+=p;x=qs[q];y=qs[q+1];q+=2;B=qs[q:q+n];q+=n;z=qs[q];q+=1;C=qs[q:q+r]
    clauses=list(base)+[(a,x) for a in A]+[(-x,y)]+[(-y,b) for b in B]+[(-b,z) for b in B]+[(-z,c) for c in C]
    def sat(cl):
        return any(bool(assignment[abs(l)]) if l>0 else not bool(assignment[abs(l)]) for l in cl)
    return all(sat(c) for c in clauses)

def full_ba4_replay():
    U,first,_,_=ba4.source_hardening();cases=0
    for p,n,r in HOLDOUTS:
        for g in (1,2):
            for bits in product((0,1),repeat=p+n+r+3):
                if source_ok(bits,p,n,r):
                    cases+=1
                    if not ba4_model(first,U,g,p,n,r,bits): return False,cases
            for bits in product((0,1),repeat=p+r):
                if final_ok(bits,p,r):
                    cases+=1
                    if not ba4_model(first,U,g,p,n,r,lift(bits,p,n,r)): return False,cases
    return True,cases

def main(result_path,out_path):
    r=json.loads(Path(result_path).read_text())
    errs=[]; checks={}
    replay=[replay_abstract(*h) for h in HOLDOUTS]
    checks["abstract_resolution"]=all(x["pass"] for x in replay)
    checks["raw_vs_distinct"]=all(x["raw"]==x["expected_raw"] and x["new"]==x["expected_new"] and x["dup"]==x["expected_dup"] for x in replay)
    checks["fiber_generic"]=(r["symbolic"]["composition"]["fiber"]=="(i,j,k)->(i,k)" and r["symbolic"]["composition"]["fiber_size"]=="n")
    checks["variable_preservation"]=(r["symbolic"]["identity"]["arbitrary_encoding_claimed"] is False and "explicit binary-CNF" in r["symbolic"]["identity"]["scope"])
    wc=width_counterexample();checks["frozen_width_falsifier"]=wc["falsifies"]
    checks["corrected_width_matches_result"]=all(corrected_width_formula(x["p"],x["n"],x["r"])==x["corrected_peak"] for x in r["graph_holdouts"])
    sizes=source_size_replay();checks["source_size"]=all(x["pass"] for x in sizes)
    U,_,_,_=ba4.source_hardening();pos=carrier_local(U,"positive");neg=carrier_local(U,"negative")
    checks["carrier_positive"]=all(pos[k]==v for k,v in {"raw_pairs":2320,"tautological":782,"non_tautological":1538,"duplicates":78,"retained":414,"R_peak":17,"B_peak":9,"W_peak":13}.items()) and pos["exact"]
    checks["carrier_negative"]=all(neg[k]==v for k,v in {"raw_pairs":2001,"tautological":658,"non_tautological":1343,"duplicates":57,"retained":383,"R_peak":17,"B_peak":9,"W_peak":13}.items()) and neg["exact"]
    ba4ok,ba4cases=full_ba4_replay();checks["full_original_ba4"]=ba4ok
    checks["prereg"]=r["preregistration_commit"]==PREREG
    checks["mixed_outcome"]=r["scientific_mixed_result_pre_replay"] is True and r["failed_frozen_obligations"]==["QUOTIENT_WIDTH_PASS"]
    checks["BA16_A_forbidden"]=r["P_BA16_A"]==0 and r["success_label_BA16_A_permitted"] is False
    checks["modeB_no_generic_pnr_enumeration"]=r["certificate_modes"]["MODE_B_generic_pnr_path_records"]==0 and r["certificate_modes"]["MODE_B_algorithmic_speedup_claimed"] is False
    checks["firewalls"]=r["P_VS_NP"]=="OPEN" and r["SAT_IN_P"]=="NOT_PROVED" and r["TRUMP_finished"] is False
    for k,v in checks.items():
        if not v:errs.append(k)
    out={
      "gate":"R50G25BA16_INDEPENDENT_REPLAY",
      "status":"PASS" if not errs else "FAIL",
      "implementation_imported":False,
      "preregistration_commit":PREREG,
      "checks":checks,"error_count":len(errs),"errors":errs,
      "width_counterexample":wc,
      "abstract_holdouts":replay,
      "source_size_replay":sizes,
      "carrier":{"positive":pos,"negative":neg},
      "full_BA4_case_count":ba4cases,
      "generic_quotient_proof":{
        "statement":"RESOLVE_bj((a_i OR b_j),((-b_j) OR c_k))=(a_i OR c_k), syntactically independent of j",
        "fiber_cardinality":"for each fixed (i,k), j ranges over exactly n witnesses",
        "raw_paths":"p*n*r","distinct":"p*r","duplicates":"p*r*(n-1)",
        "triple_enumeration_used_for_generic_proof":0},
      "identity_proof":{
        "lemma":"resolvent literals are drawn only from the two parents after deleting the pivot",
        "induction":"every resolution-DAG variable occurs in source provenance",
        "scoped_lower_bound":"n*r pairwise-distinct canonical c_jk endpoint identities require at least n*r such source-provenance identities",
        "arbitrary_encoding_claimed":False},
      "v_independent_verifier":1 if not errs else 0,
      "P_BA16_MIXED":1 if not errs else 0,
      "P_BA16_A":0}
    Path(out_path).write_text(json.dumps(out,indent=2,sort_keys=True))
    if errs:raise SystemExit("independent replay failed: "+",".join(errs))

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--result",required=True);ap.add_argument("--out",required=True)
    a=ap.parse_args();main(a.result,a.out)
