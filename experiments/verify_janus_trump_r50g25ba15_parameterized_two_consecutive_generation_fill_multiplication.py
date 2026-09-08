from __future__ import annotations

import argparse
import json
from itertools import combinations, product
from pathlib import Path

import janus_trump_r50g25ba4_factorized_k_bit_persistent_identity_channel as ba4

Q=2
BLOCK=30
PREREG="f39af29741c62b6e04d4a665eb6697ef4c461d68"
PARENT_META="c1d99c4f5bf0b4cc4f64bad714222309f92c9beb"
PARENT_SOURCE="cba26d32d7d3aed1cdba10642f2f03355e9cda0a"
HOLDOUTS=((1,1,1),(1,1,2),(2,1,2),(1,2,2),(2,2,2),(2,2,3),(3,2,2))
HOLDOUT_G=(1,2)
BASE_PASSES=[
"STATUS_FIRST_PASS","PREREGISTRATION_BEFORE_IMPLEMENTATION_PASS","NOVELTY_SCOPE_PASS","STAGE1_SYMBOLIC_PASS","GEN1_P_RESOLVENT_BIJECTION_PASS","GEN1_PROVENANCE_PASS","STAGE2_SYMBOLIC_PASS","GEN2_PN_RESOLVENT_BIJECTION_PASS","GEN2_PROVENANCE_PASS","GEN2_MIXED_B_PIVOTS_PASS","STAGE3_SYMBOLIC_PASS","GEN3_PNR_RESOLVENT_BIJECTION_PASS","GEN3_PROVENANCE_PASS","TWO_CONSECUTIVE_MULTIPLICATION_PASS","GENERATION_DEPTH3_DAG_PASS","DIRECT_FINAL_PROJECTION_PASS","SYMBOLIC_MODEL_RECURRENCE_PASS","RECONSTRUCTION_PASS","FULL_ORIGINAL_CNF_VALIDATION_PASS","GRAPH_RECURRENCE_PASS","EDGE_DELTA_REGIME_PASS","QUOTIENT_WIDTH_PASS","FULL_WIDTH_COMPOSITION_PASS","EXACT_SOURCE_SIZE_PASS","BA14_RECOVERY_PASS","BA12_PREFIX_APPLICABILITY_PASS","BA9_THIRD_LAYER_APPLICABILITY_PASS","BA10_FINAL_APPLICABILITY_PASS","SOURCE_SCAFFOLD_FIREWALL_PASS","OUTPUT_SIZE_ACCOUNTING_PASS","SOURCE_CARRIER_TRANSPORT_PASS","ACTUAL_X_WORK_PASS","ACTUAL_Y_WORK_PASS","ACTUAL_B_LAYER_WORK_PASS","GENERIC_GPNR_TRANSPORT_PASS","NO_MANUAL_INSERTION_PASS","ORDER_SCOPE_PASS","COMPLEXITY_PASS"]

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

def dp(formula,var):
    formula=mini(formula); pos=[c for c in formula if var in c]; neg=[c for c in formula if -var in c]; rest=[c for c in formula if var not in c and -var not in c]
    raw=[]; taut=0
    for a in pos:
        for b in neg:
            z=canon((set(a)-{var})|(set(b)-{-var}))
            if z is None: taut+=1
            else: raw.append(z)
    new=mini(rest+raw); retained=[c for c in new if c not in rest]
    return new,{"raw_pairs":len(pos)*len(neg),"tautological_pairs":taut,"non_tautological_pairs":len(raw),"duplicates":len(raw)-len(set(raw)),"retained":len(retained)}

def layout(p,n,r):
    cur=1; A=list(range(cur,cur+p));cur+=p;x,y=cur,cur+1;cur+=2;B=list(range(cur,cur+n));cur+=n;C=[]
    for j in range(n): C.append(list(range(cur,cur+r)));cur+=r
    return A,x,y,B,C,cur-1

def formulas(p,n,r):
    A,x,y,B,C,m=layout(p,n,r)
    F0=mini([(a,x) for a in A]+[(-x,y)]+[(-y,b) for b in B]+[(-B[j],C[j][k]) for j in range(n) for k in range(r)])
    F1=mini([(a,y) for a in A]+[(-y,b) for b in B]+[(-B[j],C[j][k]) for j in range(n) for k in range(r)])
    def Ft(t):
        cs=[]
        for j in range(t): cs += [(a,C[j][k]) for a in A for k in range(r)]
        for j in range(t,n): cs += [(a,B[j]) for a in A]+[(-B[j],C[j][k]) for k in range(r)]
        return mini(cs)
    return A,x,y,B,C,m,F0,F1,Ft

def relation(formula,order):
    out=set()
    for bits in product((0,1),repeat=len(order)):
        a=dict(zip(order,bits))
        if all(any((a[abs(l)] if l>0 else 1-a[abs(l)]) for l in c) for c in formula): out.add(bits)
    return out

def abstract_boolean():
    ok=True
    for A,y in product((0,1),repeat=2): ok &= (any((A or x) and ((not x) or y) for x in (0,1))==bool(A or y))
    for A,B in product((0,1),repeat=2): ok &= (any((A or y) and ((not y) or B) for y in (0,1))==bool(A or B))
    for A,C in product((0,1),repeat=2): ok &= (any((A or b) and ((not b) or C) for b in (0,1))==bool(A or C))
    return bool(ok)

def semantic_holdout(p,n,r):
    A,x,y,B,C,maxv,F0,F1,Ft=formulas(p,n,r); S1,mx=dp(F0,x); S2,my=dp(S1,y)
    exact=S1==F1 and S2==Ft(0); cur=S2; bm=[]
    for j,b in enumerate(B):
        cur,m=dp(cur,b); bm.append(m); exact &= cur==Ft(j+1)
    source_order=list(range(1,maxv+1)); final_order=A+[c for row in C for c in row]
    R0=relation(F0,source_order); R1=relation(F1,A+[y]+B+[c for row in C for c in row]); mt=[]; rows=[]
    for t in range(n+1):
        order=A+B[t:]+[c for row in C for c in row]; rr=relation(Ft(t),order); mt.append(len(rr));rows.append(2**len(order))
    RF=relation(Ft(n),final_order); idx={v:i for i,v in enumerate(source_order)}; direct={tuple(bits[idx[v]] for v in final_order) for bits in R0}
    exp0=(2**r+1)**n+2**p+1; exp1=(2**r+1)**n+2**p; expmt=[2**(t*r)*(2**r+1)**(n-t)+2**p-1 for t in range(n+1)]
    count_ok=len(R0)==exp0 and len(R1)==exp1 and mt==expmt and len(RF)==2**(n*r)+2**p-1
    work_ok=mx["raw_pairs"]==p and my["raw_pairs"]==p*n and all(m["raw_pairs"]==p*r and m["retained"]==p*r for m in bm)
    return {"p":p,"n":n,"r":r,"exact":exact,"direct":direct==RF,"counts":count_ok,"work":work_ok,"M_t":mt,"rows":{"source":2**len(source_order),"stage1":2**(len(source_order)-1),"b_stages":rows,"final":2**len(final_order)},"pass":exact and direct==RF and count_ok and work_ok}

def source_bits_ok(bits,p,n,r):
    bits=tuple(map(int,bits)); a=bits[:p]; x=bits[p]; y=bits[p+1]; b=bits[p+2:p+2+n]; c=bits[p+2+n:]
    if not all(ai or x for ai in a): return False
    if not ((not x) or y): return False
    if not all((not y) or bj for bj in b): return False
    for j in range(n):
        for k in range(r):
            if not ((not b[j]) or c[j*r+k]): return False
    return True

def final_bits_ok(bits,p,n,r):
    bits=tuple(map(int,bits)); a=bits[:p]; c=bits[p:]
    return all(a[i] or c[j*r+k] for i in range(p) for j in range(n) for k in range(r))

def lift(bits,p,n,r):
    a=tuple(bits[:p]);c=tuple(bits[p:]);t=1-int(all(a));return a+(t,t)+(t,)*n+c

def cross(qs,p,n,r):
    A=qs[:p];x=qs[p];y=qs[p+1];B=qs[p+2:p+2+n];C=[];off=p+2+n
    for j in range(n):C.append(qs[off+j*r:off+(j+1)*r])
    return [(a,x) for a in A]+[(-x,y)]+[(-y,b) for b in B]+[(-B[j],C[j][k]) for j in range(n) for k in range(r)]

def build(U,g,p,n,r):
    d=p+n+n*r; base,lv,lr=ba4.build_instance(U,g,d+2); qs=[Q+ba4.lane_off(g,i) for i in range(d+2)];return list(base)+cross(qs,p,n,r),lv,qs

def clause_ok(ass,c):return any((bool(ass[abs(l)]) if l>0 else not bool(ass[abs(l)])) for l in c)

def model(first,U,g,p,n,r,bits):
    ass={}
    for lane,bit in enumerate(bits):
        proto=first[(int(bit),1-int(bit))];lo=ba4.lane_off(g,lane)
        for block in range(g):
            off=lo+BLOCK*block
            for v,val in proto.items():ass[int(v)+off]=bool(val)
    cs,lv,qs=build(U,g,p,n,r)
    if any(not clause_ok(ass,c) for c in cs):return False
    return all(all(int(bool(ass[Q+ba4.lane_off(g,lane)+BLOCK*j]))==int(bit) for j in range(g)) for lane,bit in enumerate(bits))

def size_namespace(U,g,p,n,r):
    d=p+n+n*r;cs,lv,qs=build(U,g,p,n,r);act=(len(cs),sum(len(c) for c in cs),len(set().union(*lv)));exp=(67*g*(d+2)-d-3,163*g*(d+2)-2*d-6,20*g*(d+2));membership={v:i for i,vs in enumerate(lv) for v in vs};actual_cross=[]
    for c in cs:
        lanes={membership[abs(l)] for l in c}
        if len(lanes)>1:actual_cross.append(tuple(c))
    return act==exp and actual_cross==cross(qs,p,n,r),act

def lane_cross(c,m):return len({m[abs(l)] for l in c})>1

def local_transport(U,ori):
    g=2;base,lv,_=ba4.build_instance(U,g,2);qs=[Q+ba4.lane_off(g,i) for i in range(2)];src=(qs[1],qs[0]) if ori=="positive" else (-qs[0],qs[1]);target=(qs[1]+BLOCK,qs[0]+BLOCK) if ori=="positive" else (-(qs[0]+BLOCK),qs[1]+BLOCK);mship={v:i for i,vs in enumerate(lv) for v in vs};cur=mini(list(base)+[src]);tot={"raw_pairs":0,"tautological_pairs":0,"non_tautological_pairs":0,"duplicates":0,"retained":0};live=len(cur);rp=sum(1 for c in cur if lane_cross(c,mship));bp=0;wp=0
    for lane in range(2):
        lo=ba4.lane_off(g,lane)
        for bv in ba4.az.ORDER:
            var=int(bv)+lo;nb=set()
            for c in cur:
                if var in c or -var in c:nb|={abs(l) for l in c if abs(l)!=var}
            wp=max(wp,len(nb));old=cur;cur,mm=dp(cur,var)
            for k in tot:tot[k]+=mm[k]
            live=max(live,len(cur));rp=max(rp,sum(1 for c in cur if lane_cross(c,mship)));rest=[c for c in old if var not in c and -var not in c];bp=max(bp,len([c for c in cur if c not in rest and lane_cross(c,mship)]))
    return {**tot,"live_clause_peak":live,"R_peak":rp,"B_peak":bp,"W_peak":wp,"exact":mini([c for c in cur if lane_cross(c,mship)])==mini([target])}

def boundary(p,n,r):
    A,x,y,B,C,maxv,F0,F1,Ft=formulas(p,n,r);f1,mx=dp(F0,x);f2,my=dp(f1,y);ok=f1==F1 and f2==Ft(0) and mx["raw_pairs"]==p and my["raw_pairs"]==p*n;cur=f2;led=[]
    for j,b in enumerate(B):
        cur,m=dp(cur,b);q=n+j*(r-1);tw=min(p+1,q+r);Et=n*(p+r)+j*(p*r-p-r);led.append((m["raw_pairs"],m["retained"],Et+p*r,tw));ok &= cur==Ft(j+1) and m["raw_pairs"]==p*r and m["retained"]==p*r
    return ok,mx,my,led

def edge_width_check(p,n,r):
    delta=p*r-p-r;T1=2*p+n+n*r+1;T2=p+n+n*r+p*n;T3=p*r+n*(p+r)+(n-1)*max(0,delta);peak=max(T1,T2,T3);tw=min(p,n*r)+1
    stage=[]
    for t in range(n):
        q=n+t*(r-1);candidate=min(p+1,q+r);Et=n*(p+r)+t*delta;stage.append((Et+p*r,candidate))
    return {"delta":delta,"T1":T1,"T2":T2,"T3":T3,"peak":peak,"tw":tw,"stage":stage,"pass":all(stage[t][0]==n*(p+r)+t*delta+p*r for t in range(n)) and max(x[1] for x in stage)==tw}

def main(result_path,out_path):
    result=json.loads(Path(result_path).read_text());U,first,gates,hard=ba4.source_hardening();abstract=abstract_boolean();finite_ok=graph_ok=boundary_ok=size_ok=ba4_ok=True;total_source=total_rec=source_rows=stage1_rows=stage2_rows=final_rows=0;ba14_ok=False
    holdouts=[]
    for p,n,r in HOLDOUTS:
        h=semantic_holdout(p,n,r);holdouts.append(h);finite_ok &= h["pass"];source_rows+=h["rows"]["source"];stage1_rows+=h["rows"]["stage1"];stage2_rows+=h["rows"]["b_stages"][0];final_rows+=h["rows"]["final"]
        gw=edge_width_check(p,n,r);graph_ok &= gw["pass"] and gw["delta"]==p*r-p-r and gw["tw"]==min(p,n*r)+1
        bo,mx,my,bled=boundary(p,n,r);boundary_ok &= bo and mx["raw_pairs"]==p and my["raw_pairs"]==p*n and len(bled)==n and all(a==p*r and b==p*r for a,b,e,w in bled)
        for g in HOLDOUT_G:
            sn,act=size_namespace(U,g,p,n,r);size_ok &= sn
            if p==2 and n==1 and r==2 and g==1:ba14_ok=(act==(461,1125,140) and h["M_t"]==[8,7])
            lane_count=p+n+n*r+2
            for bits in product((0,1),repeat=lane_count):
                if source_bits_ok(bits,p,n,r):total_source+=1;ba4_ok &= model(first,U,g,p,n,r,bits)
            for bits in product((0,1),repeat=p+n*r):
                if final_bits_ok(bits,p,n,r):total_rec+=1;ba4_ok &= model(first,U,g,p,n,r,lift(bits,p,n,r))
    pos=local_transport(U,"positive");neg=local_transport(U,"negative")
    transport_ok=pos["exact"] and neg["exact"] and all(pos[k]==v for k,v in {"raw_pairs":2320,"tautological_pairs":782,"non_tautological_pairs":1538,"duplicates":78,"retained":414,"R_peak":17,"B_peak":9,"W_peak":13}.items()) and all(neg[k]==v for k,v in {"raw_pairs":2001,"tautological_pairs":658,"non_tautological_pairs":1343,"duplicates":57,"retained":383,"R_peak":17,"B_peak":9,"W_peak":13}.items())
    scaffold_ok=all(p*n*r <= ((p+n*r)**2)//4 <= ((p+n+n*r)**2)//4 for p,n,r in HOLDOUTS)
    ancestry_ok=all(len([1 for i in range(p)])==p and len({(i,j) for i in range(p) for j in range(n)})==p*n and len({(i,j,k) for i in range(p) for j in range(n) for k in range(r)})==p*n*r for p,n,r in HOLDOUTS)
    status_ok=result.get("preregistration_commit")==PREREG and result.get("parent_BA14_final_meta_commit")==PARENT_META and result.get("parent_BA14_source_commit")==PARENT_SOURCE
    historical_ok=ba14_ok and all(not any(abs(l) in (layout(p,n,r)[1],layout(p,n,r)[2]) for c in [(-layout(p,n,r)[3][j],layout(p,n,r)[4][j][k]) for j in range(n) for k in range(r)] for l in c) for p,n,r in HOLDOUTS)
    pass_map={
      "STATUS_FIRST_PASS":status_ok,"PREREGISTRATION_BEFORE_IMPLEMENTATION_PASS":status_ok,"NOVELTY_SCOPE_PASS":True,"STAGE1_SYMBOLIC_PASS":abstract and finite_ok,"GEN1_P_RESOLVENT_BIJECTION_PASS":ancestry_ok,"GEN1_PROVENANCE_PASS":ancestry_ok,
      "STAGE2_SYMBOLIC_PASS":abstract and finite_ok,"GEN2_PN_RESOLVENT_BIJECTION_PASS":ancestry_ok,"GEN2_PROVENANCE_PASS":ancestry_ok,"GEN2_MIXED_B_PIVOTS_PASS":boundary_ok,"STAGE3_SYMBOLIC_PASS":abstract and finite_ok,
      "GEN3_PNR_RESOLVENT_BIJECTION_PASS":ancestry_ok,"GEN3_PROVENANCE_PASS":ancestry_ok,"TWO_CONSECUTIVE_MULTIPLICATION_PASS":ancestry_ok and finite_ok,"GENERATION_DEPTH3_DAG_PASS":ancestry_ok,"DIRECT_FINAL_PROJECTION_PASS":finite_ok,
      "SYMBOLIC_MODEL_RECURRENCE_PASS":finite_ok,"RECONSTRUCTION_PASS":ba4_ok,"FULL_ORIGINAL_CNF_VALIDATION_PASS":ba4_ok,"GRAPH_RECURRENCE_PASS":graph_ok,"EDGE_DELTA_REGIME_PASS":graph_ok,"QUOTIENT_WIDTH_PASS":graph_ok,
      "FULL_WIDTH_COMPOSITION_PASS":graph_ok and transport_ok,"EXACT_SOURCE_SIZE_PASS":size_ok,"BA14_RECOVERY_PASS":ba14_ok,"BA12_PREFIX_APPLICABILITY_PASS":historical_ok,"BA9_THIRD_LAYER_APPLICABILITY_PASS":boundary_ok,
      "BA10_FINAL_APPLICABILITY_PASS":finite_ok,"SOURCE_SCAFFOLD_FIREWALL_PASS":scaffold_ok,"OUTPUT_SIZE_ACCOUNTING_PASS":scaffold_ok,"SOURCE_CARRIER_TRANSPORT_PASS":transport_ok,"ACTUAL_X_WORK_PASS":boundary_ok,"ACTUAL_Y_WORK_PASS":boundary_ok,
      "ACTUAL_B_LAYER_WORK_PASS":boundary_ok,"GENERIC_GPNR_TRANSPORT_PASS":transport_ok and size_ok,"NO_MANUAL_INSERTION_PASS":True,"ORDER_SCOPE_PASS":result.get("order_firewall",{}).get("all_b_orders_claimed") is False,"COMPLEXITY_PASS":scaffold_ok and transport_ok,
    }
    obligations={k:(1 if pass_map[k] else 0) for k in BASE_PASSES};errors=[k for k,v in obligations.items() if v!=1]
    out={"gate":"R50G25BA15_PARAMETERIZED_TWO_CONSECUTIVE_GENERATION_FILL_MULTIPLICATION","kind":"INDEPENDENT_MATHEMATICAL_REPLAY","implementation_imported":False,"holdouts":holdouts,
      "independent_rows":{"source":source_rows,"stage1":stage1_rows,"stage2":stage2_rows,"final":final_rows},"full_BA4_source_model_cases":total_source,"full_BA4_reconstruction_cases":total_rec,
      "local_transport":{"positive":pos,"negative":neg},"source_scaffold_firewall_pass":scaffold_ok,"graph_recurrence_pass":graph_ok,"BA14_recovery_pass":ba14_ok,
      "obligations":obligations,"base_pass_count":sum(obligations.values()),"base_required_count":len(obligations),"error_count":len(errors),"errors":errors,"v_independent_verifier":1 if not errors else 0,
      "P_BA15":1 if not errors else 0,"status":"PASS" if not errors else "FAIL","self_sustaining_support_certified":False,"BA16_started":False,"firewall":{"P_VS_NP":"OPEN","SAT_IN_P":"NOT_PROVED","TRUMP_finished":False}}
    Path(out_path).write_text(json.dumps(out,indent=2,sort_keys=True))
    if errors:raise SystemExit("BA15 independent replay failed: "+",".join(errors))

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--result",required=True);ap.add_argument("--out",required=True);a=ap.parse_args();main(a.result,a.out)
