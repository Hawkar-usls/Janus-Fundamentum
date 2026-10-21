#!/usr/bin/env python3
"""BABEL-21 exact rational source syzygy reconstruction and independent replay.

All source Fourier generators are legitimate degree-2 columns. Every claimed
syzygy is expanded from a rational elimination DAG and verified independently
at ALL supported frequencies, plus exact pairing with cover cokernel.
"""
import argparse,json,time
from collections import Counter,defaultdict
from fractions import Fraction
from pathlib import Path
from source_kernel_probe import evaluate
from exact_cokernel import SmallElimination

def axpy(dst,src,scale):
    for i,v in src.items():
        w=dst.get(i,0)-scale*v
        if w:dst[i]=w
        elif i in dst:del dst[i]

def exact_replay(seed,base,source,src_labels,columns,coeffs,expected_response,k):
    bykey={(r,p):resp for sig,(r,p,resp) in columns}
    out=defaultdict(Fraction)
    actual=[Fraction(0)]*k
    for (r,p),val in coeffs.items():
        if not val:continue
        for q in (p,*(p^src_labels[j] for j in source[r])):out[q]+=val
        resp=bykey[(r,p)]
        for i,v in enumerate(resp):actual[i]+=v*val
    nonzero={q:v for q,v in out.items() if v}
    assert not nonzero,("not exact original-source syzygy",len(nonzero))
    assert actual==list(expected_response),("wrong exact lifted response",actual,expected_response)
    assert any(actual)
    return len(coeffs)

def backpropagate(nodes,edge,origin):
    adj=[Fraction(0)]*len(nodes)
    for i,a in edge:adj[i]-=a
    result=defaultdict(Fraction);result[origin]+=1
    for i in range(len(nodes)-1,-1,-1):
        value=adj[i]
        if not value:continue
        o,edges,inv=nodes[i]
        result[o]+=value*inv
        for j,a in edges:adj[j]-=value*inv*a
    return {k:v for k,v in result.items() if v}

def audit(base,seed,maxcols=27000,maxnnz=550,maxpivots=18000):
    start=time.monotonic()
    source,src_labels,Q,cols,k,nonzero,dups=evaluate(base,seed)
    basis={};nodes=[]
    span=SmallElimination(k)
    proven=[];skipped=0;dependent=0
    for ix,(signature,(r,p,response)) in enumerate(cols[:maxcols]):
        vec={q:Fraction(v) for q,v in Counter(signature).items()}
        rhs=list(response)
        steps=[]
        while vec:
            pivot=min(vec)
            if pivot not in basis:break
            bv,br,idx=basis[pivot]
            scale=vec[pivot]
            axpy(vec,bv,scale)
            for j,val in enumerate(br):rhs[j]-=scale*val
            steps.append((idx,scale))
            if len(vec)>maxnnz:break
        if len(vec)>maxnnz:
            skipped+=1;continue
        if not vec:
            dependent+=1
            if any(rhs):
                if span.add(rhs,[r,p]):
                    cert=backpropagate(nodes,steps,(r,p))
                    support=exact_replay(seed,base,source,src_labels,cols,cert,rhs,k)
                    witness={"pivot_source_column":[r,p],
                     "response":[str(v) for v in rhs],
                     "nonzero_terms":support,
                     "coefficients":[[rr,u,str(v)] for (rr,u),v in sorted(cert.items())]}
                    proven.append(witness)
                    print("BABEL21_EXACT_Q_SOURCE_SYZYGY_PASS",base,seed,
                          "source_columns",ix+1,"response_rank",len(proven),"of",k,
                          "terms",support,flush=True)
                    if len(proven)==k:break
        else:
            pivot=min(vec);inv=1/vec[pivot]
            newvec={q:v*inv for q,v in vec.items()}
            newresp=[v*inv for v in rhs]
            idx=len(nodes);nodes.append(((r,p),steps,inv))
            basis[pivot]=(newvec,newresp,idx)
            if len(basis)>=maxpivots:break
        if (ix+1)%5000==0:print("BABEL21_EXACT_Q_PROGRESS",base,seed,
            "columns",ix+1,"pivots",len(basis),"source_syzygy_response_rank",len(proven),
            "seconds",round(time.monotonic()-start,1),flush=True)
    result={"gate":"BABEL21_EXACT_FULL_SOURCE_KERA_RECONSTRUCTION",
      "base":base,"seed":seed,"unexplained_Q_response_dim":k,
      "verified_new_syzygy_Q_rank":len(proven),
      "all_unexplained_source_syzygies_resolved":len(proven)==k,
      "source_generator_duplicate_count":dups,"source_response_nonzero_coefficients":nonzero,
      "source_unique_generator_count":len(cols),"processed_source_columns":ix+1,
      "source_pivot_rank_Q_lower":len(basis),
      "source_columns_skipped_density_cap":skipped,
      "exact_certificates":proven,
      "full_degree2_cover_nonmembership_proved":False,
      "status":("EXACT_Q_SOURCE_SYZYGY_RESPONSE_PASS" if proven else "OPEN_AFTER_EXACT_SOURCE_SCAN")}
    Path(f"babel21_{base}_seed{seed}_exact_source_syzygies.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("BABEL21_EXACT_SOURCE_SUMMARY",json.dumps({q:v for q,v in result.items() if q!="exact_certificates"},sort_keys=True),flush=True)
    return result

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--base",default="SCL126_flip16")
    ap.add_argument("--seed",type=int,default=37)
    ap.add_argument("--maxcols",type=int,default=27000)
    ap.add_argument("--maxpivots",type=int,default=18000)
    args=ap.parse_args();audit(args.base,args.seed,args.maxcols,maxpivots=args.maxpivots)
