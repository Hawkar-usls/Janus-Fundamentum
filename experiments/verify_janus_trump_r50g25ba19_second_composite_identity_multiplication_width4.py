from __future__ import annotations
import argparse, hashlib, json
from itertools import combinations, product
from pathlib import Path

import janus_trump_r50g25ba4_factorized_k_bit_persistent_identity_channel as ba4
import janus_trump_r50g25ba16_compact_derived_support_intermediate_identity_collapse as ba16

PREREG="d243eebfb3b9facfaf9bd67ff34fcea3ac57a556"
PARENT_META="d1d113efb6c1a22b34257b2a1982dc5a6ee3bba0"
Q=2
BLOCK=30
HOLDOUTS=((1,1,1,1),(1,1,2,2),(1,2,2,2),(2,2,2,2),(2,2,2,3),(2,3,2,2),(3,2,3,2))

def sha_obj(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def canon(c):
    s=set(map(int,c))
    if any(-x in s for x in s):return None
    return tuple(sorted(s,key=lambda z:(abs(z),z<0)))

def minimize(F):
    xs=[]
    for c in F:
        z=canon(c)
        if z is not None:xs.append(z)
    xs=sorted(set(xs),key=lambda c:(len(c),c));out=[]
    for c in xs:
        if any(set(d).issubset(c) for d in out):continue
        out.append(c)
    return tuple(sorted(out))

def dp(F,v):
    F=minimize(F);pos=[c for c in F if v in c];neg=[c for c in F if -v in c]
    rest=minimize([c for c in F if v not in c and -v not in c]);raw=[];taut=0
    for a in pos:
        for b in neg:
            z=canon((set(a)-{v})|(set(b)-{-v}))
            if z is None:taut+=1
            else:raw.append(z)
    unique=set(raw);rs=set(rest);newraw={z for z in unique if z not in rs}
    new=minimize(list(rest)+raw)
    return new,{"positive_count":len(pos),"negative_count":len(neg),"raw_pairs":len(pos)*len(neg),
               "tautological":taut,"non_tautological":len(raw),
               "duplicates":len(raw)-len(newraw),"NEW_DISTINCT":len(newraw)}

def ids(p,n,r,s):
    cur=1;A=list(range(cur,cur+p));cur+=p;x=cur;cur+=1;y=cur;cur+=1
    B=list(range(cur,cur+n));cur+=n;z=cur;cur+=1;T=list(range(cur,cur+n));cur+=n
    C=list(range(cur,cur+r));cur+=r;S=list(range(cur,cur+r));cur+=r;w=cur;cur+=1
    D=list(range(cur,cur+s));return A,x,y,B,z,T,C,S,w,D

def source(p,n,r,s):
    A,x,y,B,z,T,C,S,w,D=ids(p,n,r,s)
    F=[(a,x) for a in A]+[(-x,y)]+[(-y,b) for b in B]+[(-B[j],T[j],z) for j in range(n)]
    F += [(-z,c) for c in C]+[(-C[k],S[k],w) for k in range(r)]+[(-w,d) for d in D]
    return minimize(F),(A,x,y,B,z,T,C,S,w,D)

def final_formula(p,n,r,s):
    A,x,y,B,z,T,C,S,w,D=ids(p,n,r,s)
    return minimize([(a,T[j],S[k],d) for a in A for j in range(n) for k in range(r) for d in D])

def stage_replay(p,n,r,s):
    F,(A,x,y,B,z,T,C,S,w,D)=source(p,n,r,s)
    F,mz=dp(F,z);F,mx=dp(F,x);F,my=dp(F,y)
    rb=[]
    for b in B:F,m=dp(F,b);rb.append(m)
    F,mw=dp(F,w);rc=[]
    for c in C:F,m=dp(F,c);rc.append(m)
    fin=final_formula(p,n,r,s)
    er=set();ident=set();sid=max(D)+1
    for cl in fin:
        z0=canon([l for l in cl if abs(l) not in set(S)])
        if z0 is not None:er.add(z0)
        z1=canon([sid if l in S else l for l in cl])
        if z1 is not None:ident.add(z1)
    return {"p":p,"n":n,"r":r,"s":s,"z":mz,"x":mx,"y":my,"b":rb,"w":mw,"c":rc,
            "raw_b":sum(x["raw_pairs"] for x in rb),"new_b":sum(x["NEW_DISTINCT"] for x in rb),
            "raw_c":sum(x["raw_pairs"] for x in rc),"new_c":sum(x["NEW_DISTINCT"] for x in rc),
            "dup_c":sum(x["duplicates"] for x in rc),"final_exact":F==fin,
            "final_count":len(F),"erased":len(er),"identified":len(ident)}

def model_count(p,n,r,s):
    return (2**(n+r+s)+2**(p+r+s)+2**(p+n+s)+2**(p+n+r)
            -2**(r+s)-2**(n+s)-2**(n+r)-2**(p+s)-2**(p+r)-2**(p+n)
            +2**s+2**r+2**n+2**p-1)

def final_ok(bits,p,n,r,s):
    q=0;A=bits[q:q+p];q+=p;T=bits[q:q+n];q+=n;S=bits[q:q+r];q+=r;D=bits[q:q+s]
    return all(a or t or sk or d for a in A for t in T for sk in S for d in D)

def reconstruct(bits,p,n,r,s):
    q=0;A0=bits[q:q+p];q+=p;T0=bits[q:q+n];q+=n;S0=bits[q:q+r];q+=r;D0=bits[q:q+s]
    A=int(all(A0));T=int(all(T0));S=int(all(S0));h=int((not A) and (not T))
    return tuple(A0)+(1-A,1-A)+tuple([1-A]*n)+(h,)+tuple(T0)+tuple([h]*r)+tuple(S0)+(int(h and not S),)+tuple(D0)

def source_ok(bits,p,n,r,s):
    q=0;A=bits[q:q+p];q+=p;x=bits[q];y=bits[q+1];q+=2;B=bits[q:q+n];q+=n;z=bits[q];q+=1
    T=bits[q:q+n];q+=n;C=bits[q:q+r];q+=r;S=bits[q:q+r];q+=r;w=bits[q];q+=1;D=bits[q:q+s]
    return (all(a or x for a in A) and ((not x) or y) and all((not y) or b for b in B)
      and all((not B[j]) or T[j] or z for j in range(n)) and all((not z) or c for c in C)
      and all((not C[k]) or S[k] or w for k in range(r)) and all((not w) or d for d in D))

def source_cross(qs,p,n,r,s):
    q=0;A=list(qs[q:q+p]);q+=p;x=qs[q];y=qs[q+1];q+=2;B=list(qs[q:q+n]);q+=n;z=qs[q];q+=1
    T=list(qs[q:q+n]);q+=n;C=list(qs[q:q+r]);q+=r;S=list(qs[q:q+r]);q+=r;w=qs[q];q+=1;D=list(qs[q:q+s])
    return ([(a,x) for a in A]+[(-x,y)]+[(-y,b) for b in B]+[(-B[j],T[j],z) for j in range(n)]
            +[(-z,c) for c in C]+[(-C[k],S[k],w) for k in range(r)]+[(-w,d) for d in D])

def clause_ok(a,c):
    return any((bool(a[abs(int(l))]) if int(l)>0 else not bool(a[abs(int(l))])) for l in c)

def actual_reconstruction(U,first,g,p,n,r,s,limit=None):
    Dn=p+2*n+2*r+s+4;base,lane_vars,_=ba4.build_instance(U,g,Dn)
    qs=[Q+ba4.lane_off(g,i) for i in range(Dn)];clauses=list(base)+source_cross(qs,p,n,r,s)
    finals=[b for b in product((0,1),repeat=p+n+r+s) if final_ok(b,p,n,r,s)]
    if limit is not None:finals=finals[:limit]
    bad=0
    for fb in finals:
        rb=reconstruct(fb,p,n,r,s)
        if not source_ok(rb,p,n,r,s):bad+=1;continue
        a={}
        for lane,bit in enumerate(rb):
            proto=first[(int(bit),1-int(bit))];lo=ba4.lane_off(g,lane)
            for block in range(g):
                off=lo+BLOCK*block
                for v,val in proto.items():a[int(v)+off]=bool(val)
        if any(not clause_ok(a,c) for c in clauses):bad+=1
    return {"g":g,"p":p,"n":n,"r":r,"s":s,"cases":len(finals),"bad":bad,"pass":bad==0}

def carrier_metrics(U,q):
    g=2;lanes=2*q+1;base,lane_vars,_=ba4.build_instance(U,g,lanes)
    qs=[Q+ba4.lane_off(g,i) for i in range(lanes)];w_lane=2*q;qw=qs[w_lane]
    src=[(-qs[2*k],qs[2*k+1],qw) for k in range(q)]
    target=[(-(qs[2*k]+BLOCK),qs[2*k+1]+BLOCK,qw+BLOCK) for k in range(q)]
    membership={int(v):i for i,vs in enumerate(lane_vars) for v in vs}
    groups={2*k:k for k in range(q)}|{2*k+1:k for k in range(q)}
    cur=minimize(list(base)+src);tot={k:0 for k in ("raw_pairs","tautological","non_tautological","duplicates","retained")}
    live=len(cur);R=0;B=0;E=0;W=0;mix=False
    def cross(c):return len({membership[abs(int(l))] for l in c})>1
    def edges(F):
        E=set()
        for c in F:
            ls=sorted({membership[abs(int(l))] for l in c})
            for a,b in combinations(ls,2):E.add((a,b))
        return E
    R=sum(1 for c in cur if cross(c));E=len(edges(cur))
    for lane in list(range(2*q))+[w_lane]:
        lo=ba4.lane_off(g,lane)
        for bv in ba4.az.ORDER:
            v=int(bv)+lo
            neigh=set()
            for c in cur:
                if v in c or -v in c:neigh|={abs(int(l)) for l in c if abs(int(l))!=v}
            W=max(W,len(neigh));old=cur;cur,m=ba16.dp_step_carrier(cur,v)
            for k in tot:tot[k]+=m[k]
            live=max(live,len(cur));R=max(R,sum(1 for c in cur if cross(c)));E=max(E,len(edges(cur)))
            rest=[c for c in old if v not in c and -v not in c]
            B=max(B,sum(1 for c in cur if c not in rest and cross(c)))
            for c in cur:
                priv={groups[l] for l in {membership[abs(int(x))] for x in c} if l in groups}
                if len(priv)>1:mix=True
    remain=minimize([c for c in cur if cross(c)])
    return {"q":q,**tot,"live_clause_peak":live,"R_peak":R,"B_peak":B,"E_peak":E,"W_peak":W,
            "exact":remain==minimize(target),"no_private_group_mixing":not mix,
            "pass":remain==minimize(target) and not mix}

def exact_size(U,g,p,n,r,s):
    D=p+2*n+2*r+s+4;base,lane_vars,_=ba4.build_instance(U,g,D)
    qs=[Q+ba4.lane_off(g,i) for i in range(D)];clauses=list(base)+source_cross(qs,p,n,r,s)
    actual=(len(clauses),sum(len(c) for c in clauses),len(set().union(*lane_vars)))
    expected=(67*g*D-p-2*n-2*r-s-7,163*g*D-2*p-3*n-3*r-2*s-14,20*g*D)
    return actual==expected

def main(result_path,out_path):
    R=json.loads(Path(result_path).read_text());errs=[]
    def ck(x,m):
        if not x:errs.append(m)
    ck(R["preregistration_commit"]==PREREG,"prereg")
    ck(R["parent_BA18_meta_commit"]==PARENT_META,"parent")
    H=R["historical_immutability"]
    ck(H["BA16_F14"]=="PRESERVED_FOREVER" and H["P_BA16_A"]==0 and H["P_BA16_MIXED"]==1,"BA16")
    ck(H["BA17"]=="SEALED_AND_UNCHANGED" and H["BA18"]=="SEALED_AND_UNCHANGED","parents")
    replays=[]
    for h in HOLDOUTS:
        q=stage_replay(*h);replays.append(q);p,n,r,s=h
        ck(q["final_exact"],f"final {h}")
        ck(q["w"]["raw_pairs"]==r*s and q["w"]["NEW_DISTINCT"]==r*s,f"support {h}")
        ck(all(x["positive_count"]==p*n and x["negative_count"]==s for x in q["c"]),f"polarity {h}")
        ck(q["raw_c"]==p*n*r*s and q["new_c"]==p*n*r*s and q["dup_c"]==0,f"gen4 {h}")
        ck(q["erased"]==p*n*s and q["identified"]==p*n*s,f"controls {h}")
        actual=sum(1 for b in product((0,1),repeat=p+n+r+s) if final_ok(b,*h))
        ck(actual==model_count(*h),f"models {h}")
    U,first,gates,hard=ba4.source_hardening()
    carrier=[carrier_metrics(U,q) for q in (1,2,3,4)]
    ck(all(x["pass"] for x in carrier),"second ternary carrier")
    for h in HOLDOUTS:
        ck(exact_size(U,1,*h) and exact_size(U,2,*h),f"size {h}")
    actual_cases=[]
    for h in HOLDOUTS[:5]:
        x=actual_reconstruction(U,first,1,*h);actual_cases.append(x);ck(x["pass"],f"BA4 reconstruct {h}")
    S=R["symbolic"]
    ck(S["direct_final"]["compact"]=="A OR T OR S OR D" and S["direct_final"]["direct_equals_staged"],"direct")
    ck(S["signature"]["NEW_VARIABLE_IDENTITY_COUNT"]==0 and S["signature"]["composite_signature_count"]=="n*r*s","signature")
    ck(S["width_growth"]["BA18_final_clause_width"]==3 and S["width_growth"]["BA19_final_clause_width"]==4,"width")
    ck(all(not x["safe"]["tight_transient_claimed"] for x in R["width_certificates"]),"width firewall")
    ck(R["work_accounting"]["second_ternary_transport"]=="O(g*r^2), independently replayed under alpha-renaming","work")
    status="PASS" if not errs else "FAIL"
    out={"gate":"R50G25BA19_INDEPENDENT_REPLAY","status":status,"error_count":len(errs),"errors":errs,
         "implementation_imported":False,"holdout_stage_replays":replays,
         "second_ternary_carrier_replays":carrier,"actual_BA4_reconstruction_cases":actual_cases,
         "generic_model_count_formula":"4 singles - 6 pair intersections + 4 triple intersections - 1 quadruple intersection",
         "generic_transport_theorem":"PASS" if all(x["pass"] for x in carrier) else "FAIL",
         "P_BA19":1 if status=="PASS" else 0}
    Path(out_path).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    if errs:raise SystemExit("; ".join(errs))

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--result",required=True);ap.add_argument("--out",required=True)
    a=ap.parse_args();main(a.result,a.out)
