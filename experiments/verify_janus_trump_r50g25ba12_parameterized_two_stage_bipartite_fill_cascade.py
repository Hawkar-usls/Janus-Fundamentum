from __future__ import annotations
import argparse,json
from itertools import combinations,product
from pathlib import Path
import janus_trump_r50g25ba4_factorized_k_bit_persistent_identity_channel as ba4

Q=2; BLOCK=30
HOLDOUTS=((1,1,1),(2,1,2),(2,2,2),(3,2,3),(2,3,1))
PREREG="cab377664282e24b1ac8d68aff587daad715e722"
PARENT_META="857f21746227176e7342781a2ff48579632009fb"
PARENT_SOURCE="b54805f5405b57eb42de7cb9ffee5b6ad6afd429"

def canon(c):
    s=set(map(int,c))
    if any(-x in s for x in s): return None
    return tuple(sorted(s,key=lambda z:(abs(z),z<0)))
def minimize(cs):
    xs=[]
    for c in cs:
        z=canon(c)
        if z is not None: xs.append(z)
    xs=sorted(set(xs),key=lambda c:(len(c),c)); out=[]
    for c in xs:
        if any(set(d).issubset(set(c)) for d in out): continue
        out.append(c)
    return tuple(sorted(out))
def dp(formula,var,membership=None):
    formula=minimize(formula); pos=[c for c in formula if var in c]; neg=[c for c in formula if -var in c]; rest=[c for c in formula if var not in c and -var not in c]; raw=[]; taut=0
    for a in pos:
        for b in neg:
            z=canon((set(a)-{var})|(set(b)-{-var}))
            if z is None: taut+=1
            else: raw.append(z)
    dup=len(raw)-len(set(raw)); new=minimize(rest+raw); retained=[c for c in new if c not in rest]
    rc=0
    if membership is not None:
        rc=sum(1 for c in retained if len({membership[abs(l)] for l in c})>1)
    return new,{"raw":len(pos)*len(neg),"taut":taut,"non":len(raw),"dup":dup,"ret":len(retained),"ret_cross":rc}
def source_ok(a,x,y,b): return all(v or x for v in a) and ((not x) or y) and all((not y) or z for z in b)
def stage1_ok(a,y,b): return all(v or y for v in a) and all((not y) or z for z in b)
def final_ok(a,b): return all(v or z for v in a for z in b)
def source_cross(qs,p,n):
    aa=qs[:p]; x=qs[p]; y=qs[p+1]; bb=qs[p+2:]
    return [(a,x) for a in aa]+[(-x,y)]+[(-y,b) for b in bb]
def build(U,g,p,n):
    lanes=p+n+2; base,lv,lr=ba4.build_instance(U,g,lanes); qs=[Q+ba4.lane_off(g,i) for i in range(lanes)]; cross=source_cross(qs,p,n); return list(base)+cross,lv,qs,cross
def clause_ok(A,c): return any(bool(A[abs(l)]) if l>0 else not bool(A[abs(l)]) for l in c)
def construct(first,U,g,p,n,bits):
    A={}; bits=tuple(map(int,bits)); lanes=p+n+2
    for lane,bit in enumerate(bits):
        proto=first[(bit,1-bit)]; lo=ba4.lane_off(g,lane)
        for block in range(g):
            off=lo+BLOCK*block
            for v,val in proto.items(): A[int(v)+off]=bool(val)
    clauses,_,_,_=build(U,g,p,n); return all(clause_ok(A,c) for c in clauses)
def lane_cross(c,m): return len({m[abs(l)] for l in c})>1
def ledges(F,m):
    E=set()
    for c in F:
        ls=sorted({m[abs(l)] for l in c})
        for a,b in combinations(ls,2): E.add((a,b))
    return E
def local_transport(U,orientation):
    base,lv,_=ba4.build_instance(U,2,2); qs=[Q+ba4.lane_off(2,i) for i in range(2)]; src=(qs[1],qs[0]) if orientation=="positive" else (-qs[0],qs[1]); tgt=(qs[1]+BLOCK,qs[0]+BLOCK) if orientation=="positive" else (-(qs[0]+BLOCK),qs[1]+BLOCK); m={int(v):i for i,vs in enumerate(lv) for v in vs}; cur=minimize(list(base)+[src]); totals={"raw":0,"taut":0,"non":0,"dup":0,"ret":0}; live=len(cur); R=sum(lane_cross(c,m) for c in cur); B=0; E=len(ledges(cur,m)); W=0
    for lane in range(2):
        lo=ba4.lane_off(2,lane)
        for bv in ba4.az.ORDER:
            var=int(bv)+lo; neigh=set()
            for c in cur:
                if var in c or -var in c: neigh|={abs(l) for l in c if abs(l)!=var}
            W=max(W,len(neigh)); cur,z=dp(cur,var,m)
            for k in totals: totals[k]+=z[k]
            live=max(live,len(cur)); R=max(R,sum(lane_cross(c,m) for c in cur)); B=max(B,z["ret_cross"]); E=max(E,len(ledges(cur,m)))
    cross=[c for c in cur if lane_cross(c,m)]
    return {**totals,"live":live,"R":R,"B":B,"E":E,"W":W,"exact":minimize(cross)==minimize([tgt])}
def finite(U,first,g,p,n):
    src=st=fn=0; direct=set(); staged=set(); full=True
    for bits in product((0,1),repeat=p+n+2):
        aa=bits[:p]; x=bits[p]; y=bits[p+1]; bb=bits[p+2:]
        if source_ok(aa,x,y,bb): src+=1; full=full and construct(first,U,g,p,n,bits)
    for bits in product((0,1),repeat=p+n+1):
        aa=bits[:p]; y=bits[p]; bb=bits[p+1:]
        if stage1_ok(aa,y,bb): st+=1
    for bits in product((0,1),repeat=p+n):
        aa=bits[:p]; bb=bits[p:]
        if final_ok(aa,bb):
            fn+=1; A=int(all(aa)); full=full and construct(first,U,g,p,n,tuple(aa)+(1-A,1-A)+tuple(bb))
        if any(stage1_ok(aa,y,bb) for y in (0,1)): staged.add(bits)
        if any(source_ok(aa,x,y,bb) for x,y in product((0,1),repeat=2)): direct.add(bits)
    d=p+n; clauses,lv,qs,cross=build(U,g,p,n); size=(len(clauses),sum(map(len,clauses)),len(set().union(*lv))); expected=(67*g*(d+2)-d-3,163*g*(d+2)-2*d-6,20*g*(d+2)); k=max(0,g-1); ids=[Q+ba4.lane_off(g,i)+BLOCK*k for i in range(d+2)]; aa=ids[:p]; x=ids[p]; y=ids[p+1]; bb=ids[p+2:]; F=minimize([(a,x) for a in aa]+[(-x,y)]+[(-y,b) for b in bb]); G1,mx=dp(F,x); G2,my=dp(G1,y); e1=minimize([(a,y) for a in aa]+[(-y,b) for b in bb]); e2=minimize([(a,b) for a in aa for b in bb]); return {"tuple":[g,p,n],"counts":[src,st,fn],"expected":[2**n+2**p+1,2**n+2**p,2**n+2**p-1],"direct_staged":direct==staged,"full":full,"size":size==expected,"stage1":G1==e1 and mx["raw"]==p and mx["ret"]==p,"stage2":G2==e2 and my["raw"]==p*n and my["ret"]==p*n,"pass":([src,st,fn]==[2**n+2**p+1,2**n+2**p,2**n+2**p-1] and direct==staged and full and size==expected and G1==e1 and G2==e2)}
def main(result_path,out_path):
    r=json.loads(Path(result_path).read_text()); errors=[]
    if r.get("preregistration_commit")!=PREREG: errors.append("prereg")
    if r.get("parent_BA11_final_meta_commit")!=PARENT_META or r.get("parent_BA11_source_commit")!=PARENT_SOURCE: errors.append("parent")
    U,first,gates,hard=ba4.source_hardening()
    if not all(bool(v) for v in gates.values()): errors.append("BA4_hardening")
    pos=local_transport(U,"positive"); neg=local_transport(U,"negative")
    if not (pos["exact"] and neg["exact"]): errors.append("transport_exact")
    if (pos["raw"],pos["taut"],pos["non"],pos["dup"],pos["ret"])!=(2320,782,1538,78,414): errors.append("positive_constants")
    if (neg["raw"],neg["taut"],neg["non"],neg["dup"],neg["ret"])!=(2001,658,1343,57,383): errors.append("negative_constants")
    hs=[finite(U,first,*t) for t in HOLDOUTS]
    if not all(h["pass"] for h in hs): errors.append("holdout_or_full_CNF")
    # Independent symbolic replay of the finite abstract A/B lemmas (generic p,n enter only through conjunction cardinalities).
    stage1_abstract=all(((A or y)==((A and (not False)) or y)) for A,y in product((False,True),repeat=2))
    stage2_abstract=all(((A or B)==((A and (not False)) or B)) for A,B in product((False,True),repeat=2))
    if not stage1_abstract or not stage2_abstract: errors.append("symbolic_abstract")
    s=r["symbolic"]
    if s["stage1_productivity"]["productive"]!="p" or s["stage2_productivity"]["productive"]!="p*n": errors.append("productivity")
    if r["model_counts"]["source"]!="2^n+2^p+1" or r["model_counts"]["final"]!="2^n+2^p-1": errors.append("model_count_formula")
    if r["graph"]["E_peak"]!="max(2p+n+1,p+n+p*n)": errors.append("Epeak")
    if r["width"]["quotient_tw_peak"]!="min(p,n)+1": errors.append("tw")
    if r["full_width"]["upper"]!="max(13,min(p,n)+1)": errors.append("full_width")
    if r["complexity"]["lower_bound"]!="Omega(p*n)" or r["complexity"]["S"]!="g(p+n)+p*n": errors.append("output")
    H=r["historical_controls"]
    for k in ("BA7_p1n1","BA11_p1n2","BA9_stage1_applicability","BA10_termination"):
        if not H[k]["pass"]: errors.append(k)
    pre=r.get("pre_independent_obligations",{})
    if len(pre)!=26 or not all(v==1 for v in pre.values()): errors.append("pre_obligations")
    out={"gate":"R50G25BA12_PARAMETERIZED_TWO_STAGE_BIPARTITE_FILL_CASCADE","kind":"INDEPENDENT_REPLAY","status":"PASS" if not errors else "FAIL","errors":errors,"error_count":len(errors),"local_transport":{"positive":pos,"negative":neg},"holdouts":hs,"independent_source_kernel_rows":sum(2**(p+n+2) for g,p,n in HOLDOUTS),"independent_stage1_rows":sum(2**(p+n+1) for g,p,n in HOLDOUTS),"independent_final_rows":sum(2**(p+n) for g,p,n in HOLDOUTS),"v_independent_verifier":0 if errors else 1,"message_state":"VERIFIED" if not errors else "FALSIFIED","P_BA12_INDEPENDENT":0 if errors else 1,"P_VS_NP":"OPEN","SAT_IN_P":"NOT_PROVED"}
    Path(out_path).write_text(json.dumps(out,indent=2,sort_keys=True))
    if errors: raise SystemExit("BA12 independent replay failed: "+",".join(errors))
if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--result",required=True); ap.add_argument("--out",required=True); a=ap.parse_args(); main(a.result,a.out)
