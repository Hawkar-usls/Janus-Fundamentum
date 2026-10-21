#!/usr/bin/env python3
"""BABEL-21 fast modular elimination-DAG -> bounded Q reconstruction.

The Fp dependency is only a locator. PASS is emitted EXCLUSIVELY after
integer/rational replay A z=0 and nonzero rational source-cokernel response.
"""
import argparse,json,time,math
from collections import Counter,defaultdict
from fractions import Fraction
from pathlib import Path
from source_kernel_probe import evaluate
from exact_cokernel import SmallElimination
P=65521

def mod_sub(vec,src,factor):
    for i,v in src.items():
        x=(vec.get(i,0)-factor*v)%P
        if x:vec[i]=x
        elif i in vec:del vec[i]

def lift_coeffs(nodes,origin,edges):
    adj=[0]*len(nodes)
    for j,a in edges:adj[j]=(adj[j]-a)%P
    sums=defaultdict(int);sums[origin]=1
    for i in range(len(nodes)-1,-1,-1):
        v=adj[i]
        if not v:continue
        oldorigin,oldedges,inv=nodes[i]
        scale=v*inv%P
        sums[oldorigin]=(sums[oldorigin]+scale)%P
        for j,a in oldedges:adj[j]=(adj[j]-scale*a)%P
    return {i:v for i,v in sums.items() if v}

def rational_coeff(a,bound=512):
    signed=a if a<=P//2 else a-P
    if abs(signed)<=bound:return Fraction(signed)
    for den in range(2,bound+1):
        n=a*den%P
        if n>P//2:n-=P
        if abs(n)<=bound and math.gcd(n,den)==1:return Fraction(n,den)
    return None

def check_exact(source,src_labels,bykey,combo,expected,k):
    out=defaultdict(Fraction);actual=[Fraction(0)]*k
    for (r,p),val in combo.items():
        if not val:continue
        for q in (p,*(p^src_labels[j] for j in source[r])):out[q]+=val
        for j,v in enumerate(bykey[(r,p)]):actual[j]+=v*val
    return not any(out.values()) and actual==list(expected) and any(actual)

def search(base,seed,maxcols,maxpivots,maxnnz,bound):
    t0=time.monotonic()
    source,labels,Q,cols,k,nonzero,dups=evaluate(base,seed)
    bykey={(r,p):resp for sig,(r,p,resp) in cols}
    piv={};nodes=[];mod_hits=0;try_q=0;proven=[];span=SmallElimination(k)
    for ix,(sig,(r,p,resp)) in enumerate(cols[:maxcols]):
        vec={q:v%P for q,v in Counter(sig).items()}
        rhs=[int(x.numerator*pow(x.denominator,-1,P)%P) for x in resp]
        edges=[]
        while vec:
            at=min(vec)
            if at not in piv:break
            basis,br,idx=piv[at];a=vec[at]
            edges.append((idx,a));mod_sub(vec,basis,a)
            for j,v in enumerate(br):rhs[j]=(rhs[j]-a*v)%P
            if len(vec)>maxnnz:break
        if len(vec)>maxnnz:continue
        if not vec:
            if any(rhs):
                mod_hits+=1
                modular=lift_coeffs(nodes,(r,p),edges)
                candidate={}
                for key,a in modular.items():
                    f=rational_coeff(a,bound)
                    if f is None:break
                    candidate[key]=f
                else:
                    try_q+=1
                    observed=[sum(bykey[key][j]*v for key,v in candidate.items()) for j in range(k)]
                    if check_exact(source,labels,bykey,candidate,observed,k):
                        if span.add(observed,(r,p)):
                            certificate={"pivot":[r,p],"terms":[[rr,u,str(c)] for (rr,u),c in sorted(candidate.items())],
                              "source_response":[str(x) for x in observed],
                              "nonzero_terms":len(candidate)}
                            proven.append(certificate)
                            print("BABEL21_MOD_CRT_EXACT_Q_PASS",base,seed,"columns",ix+1,
                              "support",len(candidate),"new_response_rank",len(proven),"of",k,flush=True)
                            if len(proven)==k:break
                if mod_hits<=4:
                    print("BABEL21_MOD_CRT_CANDIDATE",base,seed,"columns",ix+1,
                          "mod_support",len(modular),"attempted_Q",try_q,flush=True)
        else:
            at=min(vec);inv=pow(vec[at],-1,P);idx=len(nodes)
            nodes.append(((r,p),edges,inv))
            piv[at]=({q:v*inv%P for q,v in vec.items()},
                     [v*inv%P for v in rhs],idx)
            if len(piv)>=maxpivots:break
        if (ix+1)%15000==0:print("BABEL21_MOD_CRT_PROGRESS",base,seed,
          "columns",ix+1,"pivots",len(piv),"mod_hits",mod_hits,
          "Q_proofs",len(proven),"seconds",round(time.monotonic()-t0,1),flush=True)
    result={"gate":"BABEL21_MODULAR_LOCATOR_RATIONAL_SOURCE_REPLAY",
      "base":base,"seed":seed,"source_kerA_response_dim":k,
      "exact_source_syzygy_response_rank":len(proven),
      "verified_exact_source_syzygies":proven,
      "modular_source_dependencies_found":mod_hits,
      "bounded_rational_reconstructions_attempted":try_q,
      "source_generators_processed":ix+1,
      "scientific_status":("EXACT_Q_NEW_SYZYGY_PASS" if proven else "OPEN_MODULAR_ONLY"),
      "full_degree2_cover_negative_proved":False}
    Path(f"babel21_{base}_seed{seed}_modloc_exactQ.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("BABEL21_MODLOC_Q_SUMMARY",json.dumps({k:v for k,v in result.items() if k!="verified_exact_source_syzygies"},sort_keys=True),flush=True)
    return result
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--base",default="SCL126_flip16")
    p.add_argument("--seed",type=int,required=True);p.add_argument("--maxcols",type=int,default=43000)
    p.add_argument("--maxpivots",type=int,default=19000)
    p.add_argument("--maxnnz",type=int,default=1000);p.add_argument("--bound",type=int,default=512)
    args=p.parse_args();search(args.base,args.seed,args.maxcols,args.maxpivots,args.maxnnz,args.bound)
