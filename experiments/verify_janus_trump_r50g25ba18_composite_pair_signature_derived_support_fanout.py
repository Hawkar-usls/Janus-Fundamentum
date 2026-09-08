from __future__ import annotations
import argparse, json, hashlib
from itertools import product, combinations
from pathlib import Path
import janus_trump_r50g25ba4_factorized_k_bit_persistent_identity_channel as ba4
import janus_trump_r50g25ba16_compact_derived_support_intermediate_identity_collapse as ba16

PREREG="1670788c9e6c10d77c1ed7bf4f0ccf2a32471285"
PARENT_META="bd003cb6004d587e7d970b9b580c1e90fc6ad458"
HOLDOUTS=((1,1,1),(1,2,1),(1,2,2),(2,2,2),(2,3,2),(3,2,3))
Q=2;BLOCK=30

def canon(c):
    s=set(int(x) for x in c)
    if any(-x in s for x in s): return None
    return tuple(sorted(s,key=lambda z:(abs(z),z<0)))
def mini(cs):
    xs=sorted(set(x for x in (canon(c) for c in cs) if x is not None),key=lambda c:(len(c),c))
    out=[]
    for c in xs:
        if any(set(d).issubset(c) for d in out):continue
        out.append(c)
    return tuple(sorted(out))
def step(F,v):
    F=mini(F);p=[c for c in F if v in c];n=[c for c in F if -v in c]
    rest=mini([c for c in F if v not in c and -v not in c]);raw=[];taut=0
    for a in p:
        for b in n:
            z=canon((set(a)-{v})|(set(b)-{-v}))
            if z is None:taut+=1
            else:raw.append(z)
    rs=set(rest);newraw={z for z in set(raw) if z not in rs};new=mini(list(rest)+raw)
    return new,{"raw_pairs":len(p)*len(n),"NEW_DISTINCT":len(newraw),"duplicates":len(raw)-len(newraw),
                "tautological":taut,"non_tautological":len(raw),"retained":len([c for c in new if c not in rs])}
def ids(p,n,r):
    q=1;a=list(range(q,q+p));q+=p;x=q;q+=1;y=q;q+=1;b=list(range(q,q+n));q+=n;z=q;q+=1;t=list(range(q,q+n));q+=n;c=list(range(q,q+r))
    return a,x,y,b,z,t,c
def source(p,n,r):
    a,x,y,b,z,t,c=ids(p,n,r)
    return mini([(ai,x) for ai in a]+[(-x,y)]+[(-y,bj) for bj in b]+[(-b[j],t[j],z) for j in range(n)]+[(-z,ck) for ck in c]),(a,x,y,b,z,t,c)
def final_formula(p,n,r):
    a,x,y,b,z,t,c=ids(p,n,r)
    return mini([(ai,t[j],ck) for ai in a for j in range(n) for ck in c])
def abstract_replay(p,n,r):
    F,(a,x,y,b,z,t,c)=source(p,n,r);Fz,mz=step(F,z);Fx,mx=step(Fz,x);Fy,my=step(Fx,y)
    cur=Fy;raw=new=dup=0
    for bj in b:
        cur,m=step(cur,bj);raw+=m["raw_pairs"];new+=m["NEW_DISTINCT"];dup+=m["duplicates"]
    ff=final_formula(p,n,r)
    erased={canon([l for l in cl if l not in t]) for cl in ff};erased.discard(None)
    tid=max(c)+1;ident={canon([tid if l in t else l for l in cl]) for cl in ff};ident.discard(None)
    return {"p":p,"n":n,"r":r,"support":mz["NEW_DISTINCT"],"xraw":mx["raw_pairs"],"yraw":my["raw_pairs"],
            "braw":raw,"bnew":new,"bdup":dup,"final":len(cur),"erased":len(erased),"identified":len(ident),
            "pass":cur==ff and mz["NEW_DISTINCT"]==n*r and mx["raw_pairs"]==p and my["raw_pairs"]==p*n
                   and raw==p*n*r and new==p*n*r and dup==0 and len(cur)==p*n*r and len(erased)==p*r and len(ident)==p*r}
def carrier_step(F,v):
    F=mini(F);p=[c for c in F if v in c];n=[c for c in F if -v in c];rest=[c for c in F if v not in c and -v not in c]
    raw=[];taut=0
    for a in p:
        for b in n:
            z=canon((set(a)-{v})|(set(b)-{-v}))
            if z is None:taut+=1
            else:raw.append(z)
    dup=len(raw)-len(set(raw));new=mini(rest+raw);restm=mini(rest)
    ret=[c for c in new if c not in restm]
    return new,{"raw_pairs":len(p)*len(n),"tautological":taut,"non_tautological":len(raw),"duplicates":dup,"retained":len(ret)}
def cross(c,m):
    return len({m[abs(int(l))] for l in c})>1
def lane_edges(F,m):
    E=set()
    for c in F:
        ls=sorted({m[abs(int(l))] for l in c})
        for a,b in combinations(ls,2):E.add((a,b))
    return E
def carrier(U,n):
    g=2;L=2*n+1;base,lane_vars,_=ba4.build_instance(U,g,L);qs=[Q+ba4.lane_off(g,i) for i in range(L)]
    zlane=2*n;qz=qs[zlane];src=[(-qs[2*j],qs[2*j+1],qz) for j in range(n)]
    tgt=[(-(qs[2*j]+BLOCK),qs[2*j+1]+BLOCK,qz+BLOCK) for j in range(n)]
    m={int(v):i for i,vs in enumerate(lane_vars) for v in vs};groups={2*j:j for j in range(n)}|{2*j+1:j for j in range(n)}
    cur=mini(list(base)+src);tot={k:0 for k in ("raw_pairs","tautological","non_tautological","duplicates","retained")}
    live=len(cur);R=sum(1 for c in cur if cross(c,m));B=0;E=len(lane_edges(cur,m));W=0;mix=False
    for lane in list(range(2*n))+[zlane]:
        lo=ba4.lane_off(g,lane)
        for bv in ba4.az.ORDER:
            v=int(bv)+lo;ne=set()
            for c in cur:
                if v in c or -v in c:ne|={abs(int(l)) for l in c if abs(int(l))!=v}
            W=max(W,len(ne));old=cur;cur,mm=carrier_step(cur,v)
            for k in tot:tot[k]+=mm[k]
            live=max(live,len(cur));R=max(R,sum(1 for c in cur if cross(c,m)))
            rest=[c for c in old if v not in c and -v not in c]
            B=max(B,len([c for c in cur if c not in rest and cross(c,m)]));E=max(E,len(lane_edges(cur,m)))
            for c in cur:
                ps={groups[l] for l in {m[abs(int(x))] for x in c} if l in groups}
                mix |= len(ps)>1
    rem=[c for c in cur if cross(c,m)]
    return {"n":n,**tot,"live_clause_peak":live,"R_peak":R,"B_peak":B,"E_peak":E,"W_peak":W,
            "exact":mini(rem)==mini(tgt),"mix":mix,"pass":mini(rem)==mini(tgt) and not mix}
def base_lane(U):
    F,_,_=ba4.build_instance(U,2,1);F=mini(F);tot={k:0 for k in ("raw_pairs","tautological","non_tautological","duplicates","retained")}
    for bv in ba4.az.ORDER:
        F,m=carrier_step(F,int(bv))
        for k in tot:tot[k]+=m[k]
    return tot
def parts(bits,p,n,r):
    q=0;a=bits[q:q+p];q+=p;x=bits[q];y=bits[q+1];q+=2;b=bits[q:q+n];q+=n;z=bits[q];q+=1;t=bits[q:q+n];q+=n;c=bits[q:q+r]
    return a,x,y,b,z,t,c
def source_ok(bits,p,n,r):
    a,x,y,b,z,t,c=parts(tuple(map(int,bits)),p,n,r)
    return all(ai or x for ai in a) and ((not x) or y) and all((not y) or bj for bj in b) and all((not b[j]) or t[j] or z for j in range(n)) and all((not z) or ck for ck in c)
def final_ok(bits,p,n,r):
    bits=tuple(map(int,bits));a=bits[:p];t=bits[p:p+n];c=bits[p+n:]
    return all(ai or tj or ck for ai in a for tj in t for ck in c)
def reconstruct(bits,p,n,r):
    bits=tuple(map(int,bits));a=bits[:p];t=bits[p:p+n];c=bits[p+n:];A=int(all(a));T=int(all(t));h=1-A;z=h*(1-T)
    return tuple(a)+(h,h)+tuple([h]*n)+(z,)+tuple(t)+tuple(c)
def source_cross(qs,p,n,r):
    q=0;a=qs[q:q+p];q+=p;x=qs[q];y=qs[q+1];q+=2;b=qs[q:q+n];q+=n;z=qs[q];q+=1;t=qs[q:q+n];q+=n;c=qs[q:q+r]
    return [(ai,x) for ai in a]+[(-x,y)]+[(-y,bj) for bj in b]+[(-b[j],t[j],z) for j in range(n)]+[(-z,ck) for ck in c]
def build(U,g,p,n,r):
    D=p+2*n+r+3;base,lv,lr=ba4.build_instance(U,g,D);qs=[Q+ba4.lane_off(g,i) for i in range(D)];cr=source_cross(qs,p,n,r)
    return list(base)+cr,lv,qs
def clause_ok(a,c):
    return any((bool(a[abs(int(l))]) if int(l)>0 else not bool(a[abs(int(l))])) for l in c)
def validate_model(first,U,g,p,n,r,bits):
    a={}
    for lane,bit in enumerate(bits):
        proto=first[(int(bit),1-int(bit))];lo=ba4.lane_off(g,lane)
        for blk in range(g):
            off=lo+BLOCK*blk
            for v,val in proto.items():a[int(v)+off]=bool(val)
    F,lv,qs=build(U,g,p,n,r)
    return all(clause_ok(a,c) for c in F)
def size_replay(U,g,p,n,r):
    D=p+2*n+r+3;F,lv,qs=build(U,g,p,n,r)
    A={"C":len(F),"L":sum(len(c) for c in F),"V":len(set().union(*lv))};A["n_struct"]=sum(A.values())
    E={"C":67*g*D-p-2*n-r-5,"L":163*g*D-2*p-3*n-2*r-10,"V":20*g*D,"n_struct":250*g*D-3*p-5*n-3*r-15}
    return A==E
def source_width(p,n,r):
    A=[f"a{i}" for i in range(p)];B=[f"b{j}" for j in range(n)];T=[f"t{j}" for j in range(n)];C=[f"c{k}" for k in range(r)]
    E=set()
    def e(u,v):E.add(tuple(sorted((u,v))))
    for a in A:e(a,"x")
    e("x","y")
    for j,b in enumerate(B):e("y",b);e(b,T[j]);e(b,"z");e(T[j],"z")
    for c in C:e("z",c)
    adj={v:set() for v in A+B+T+C+["x","y","z"]}
    for u,v in E:adj[u].add(v);adj[v].add(u)
    w=0
    for v in A+C+T+B+["x","y","z"]:
        ns=list(adj[v]);w=max(w,len(ns))
        for u,q in combinations(ns,2):adj[u].add(q);adj[q].add(u)
        for u in ns:adj[u].discard(v)
        del adj[v]
    tri=all(tuple(sorted(x)) in E for x in [(B[0],T[0]),(B[0],"z"),(T[0],"z")])
    return w==2 and tri
def final_count(p,n,r):
    return 2**(n+r)+2**(p+r)+2**(p+n)-2**r-2**n-2**p+1

def main(result_path,out_path):
    r=json.loads(Path(result_path).read_text());errors=[]
    def ck(cond,msg):
        if not cond:errors.append(msg)
    ck(r["preregistration_commit"]==PREREG,"prereg")
    ck(r["parent_BA17_meta_commit"]==PARENT_META,"parent")
    ck(r["historical_immutability"]["BA16_F14"]=="PRESERVED_FOREVER","BA16 F14")
    ck(r["historical_immutability"]["P_BA16_A"]==0 and r["historical_immutability"]["P_BA16_MIXED"]==1,"BA16 mixed")
    absrows=[abstract_replay(*h) for h in HOLDOUTS];ck(all(x["pass"] for x in absrows),"abstract")
    ck(all(r["holdouts"][i]["whole_b"]["NEW_DISTINCT"]==absrows[i]["bnew"] for i in range(len(HOLDOUTS))),"holdout result mismatch")
    for p,n,r0 in HOLDOUTS:
        actual=sum(1 for bits in product((0,1),repeat=p+n+r0) if final_ok(bits,p,n,r0))
        ck(actual==final_count(p,n,r0),"model count")
        ck(source_width(p,n,r0),"source width")
        ck(r["width_certificates"][HOLDOUTS.index((p,n,r0))]["final"]["claimed"]==p+n+r0-max(p,n,r0),"final width")
    U,first,gates,hard=ba4.source_hardening()
    base=base_lane(U);car=[carrier(U,n) for n in (1,2,3)]
    ck(all(x["pass"] for x in car),"ternary carrier")
    keys=("raw_pairs","tautological","non_tautological","duplicates","retained")
    for x in car:
        n=x["n"];exp={k:base[k]+n*(car[0][k]-base[k]) for k in keys};ck(all(x[k]==exp[k] for k in keys),"carrier recurrence")
    kr=r["ternary_carrier"]["kernel_n1"]
    ck(all(kr[k]==car[0][k] for k in keys+("live_clause_peak","R_peak","B_peak","E_peak","W_peak")),"kernel ledger mismatch")
    recon=0
    for p,n,r0 in HOLDOUTS:
        for g in (1,2):
            ck(size_replay(U,g,p,n,r0),"size")
            for fb in product((0,1),repeat=p+n+r0):
                if not final_ok(fb,p,n,r0):continue
                rb=reconstruct(fb,p,n,r0);ck(source_ok(rb,p,n,r0),"reconstruction symbolic");ck(validate_model(first,U,g,p,n,r0,rb),"full BA4 reconstruction");recon+=1
    ck(r["symbolic"]["signature"]["NEW_VARIABLE_IDENTITY_COUNT"]==0,"new identity")
    ck(r["output_firewall"]["COMPOSITE_IDENTITY_FANOUT_NE_EXPONENTIAL_BLOWUP"] is True,"output firewall")
    out={"gate":"R50G25BA18_INDEPENDENT_REPLAY","status":"PASS" if not errors else "FAIL","error_count":len(errors),"errors":errors,
         "implementation_imported":False,"abstract_holdouts":absrows,"ternary_carrier_replay":car,
         "reconstruction_cases":recon,"P_BA18":1 if not errors else 0,
         "BA16_F14":"PRESERVED_FOREVER","P_BA16_A":0,"P_BA16_MIXED":1,
         "P_VS_NP":"OPEN","SAT_IN_P":"NOT_PROVED"}
    Path(out_path).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    if errors:raise SystemExit("BA18 independent replay failure: "+errors[0])
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--result",required=True);ap.add_argument("--out",required=True);a=ap.parse_args();main(a.result,a.out)
