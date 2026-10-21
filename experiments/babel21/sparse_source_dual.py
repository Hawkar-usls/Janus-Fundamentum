#!/usr/bin/env python3
"""BABEL-21 sparse exact-Q dual test for unresolved full source ker(A).

For each remaining rational cokernel functional h on cover anti-coordinates,
form its canonical-lift source response c. Test c=A^T lambda using an exact
sparse source-rowspace solver on selected source Fourier frequencies. A solved
lambda is verified on *every* source degree2 generator. If lambda(0)!=h(0),
independently verify h-Pi^T lambda annihilates ALL cover degree2 generators:
this is a legitimate exact rational FULL-M2 lower-bound witness.
"""
import argparse,json
from fractions import Fraction
from collections import defaultdict
from pathlib import Path
from source_kernel_probe import evaluate,complement
from crossbase_rank2 import setup
from rank2_geometry import restriction
from janus_babel6_transfer import xor_labels

def axpy(dst,src,scale):
    for k,v in src.items():
        new=dst.get(k,0)-scale*v
        if new:dst[k]=new
        elif k in dst:del dst[k]

class RationalSpan:
    def __init__(self):
        self.basis={}
        self.used=[]
    def insert(self,label,raw):
        vec={k:Fraction(v) for k,v in raw.items() if v}
        rep={label:Fraction(1)}
        while vec:
            k=min(vec)
            if k not in self.basis:break
            bv,br=self.basis[k];a=vec[k]
            axpy(vec,bv,a);axpy(rep,br,a)
        if not vec:return False
        p=min(vec);inv=1/vec[p]
        self.basis[p]=({j:v*inv for j,v in vec.items()},
                       {j:v*inv for j,v in rep.items()})
        self.used.append(label)
        return True
    def solve(self,raw):
        vec={k:Fraction(v) for k,v in raw.items() if v}
        rep={}
        while vec:
            k=min(vec)
            if k not in self.basis:return None,k
            bv,br=self.basis[k];a=vec[k]
            axpy(vec,bv,a)
            for j,v in br.items():
                new=rep.get(j,0)+a*v
                if new:rep[j]=new
                elif j in rep:del rep[j]
        return rep,None

def run(base,seed,maxcandidates=750):
    src,labels,Q,cols,k,nz,dups=evaluate(base,seed)
    src_labels,_,d=xor_labels(src)
    source,cov,cover_labels,source_Q,cover_Q,kernel,fibers,coord,_,_=setup(seed,base)
    pi,_=restriction(src_labels,cover_labels,d,d+2)
    hs,alphas=complement(base,seed)
    combined=[]
    for alpha in alphas:
        h=defaultdict(Fraction)
        for a,witness in zip(alpha,hs):
            for i,v in witness.items():h[i]+=a*v
        combined.append({i:v for i,v in h.items() if v})
    bysig={sig:i for i,(sig,item) in enumerate(cols)}
    lookup=defaultdict(list)
    active=set()
    for i,(sig,(_,_,resp)) in enumerate(cols):
        for f in sig:lookup[f].append(i)
        if any(resp):active.update(sig)
    ordering=sorted(active)
    expanded=set(active)
    for f in ordering:
        for sid in lookup[f]:
            expanded.update(cols[sid][0])
    ordering+=sorted(expanded-set(ordering))
    ordering=ordering[:maxcandidates]
    span=RationalSpan()
    targets=[{i:item[2][j] for i,(sig,item) in enumerate(cols) if item[2][j]} for j in range(k)]
    for stage,frequency in enumerate(ordering):
        span.insert(frequency,{row:1 for row in lookup[frequency]})
        if stage%100==0 or stage==len(ordering)-1:
            print("BABEL21_SPARSE_DUAL_PROGRESS",base,seed,stage+1,
                  "rank",len(span.used),"target_dim",k,flush=True)
        if (stage+1)%16 and stage+1!=len(ordering):continue
        allsolved=True;provisional=[]
        for j in range(k):
            lam,fail=span.solve(targets[j])
            provisional.append(lam)
            if lam is None:allsolved=False
        if allsolved:break
    results=[]
    for j in range(k):
        lam,fail=span.solve(targets[j])
        if lam is None:
            results.append({"component":j,"status":"OPEN_SPARSE_DUAL_NOT_FOUND",
                            "first_unresolved_source_signature":list(cols[fail][0])})
            continue
        for i,(sig,(_,_,resp)) in enumerate(cols):
            assert sum(lam.get(f,0) for f in sig)==resp[j],("source-rowspace verification failed",i)
        h=combined[j]
        L0=h.get(coord.get(0,-1),0)-lam.get(0,0)
        rows_checked=0
        for r,row in enumerate(cov):
            for u in cover_Q:
                val=sum(h.get(coord.get(q,-1),0)-lam.get(pi(q),0)
                    for q in (u,*(u^cover_labels[v] for v in row)))
                assert val==0,("FULL COVER M2 DUAL FAILURE",r,u,val)
                rows_checked+=1
        result={"component":j,"status":("EXACT_Q_FULL_M2_NONMEMBERSHIP_PASS" if L0
                                      else "EXACT_Q_SOURCE_TARGET_COMPATIBLE_PASS"),
                "lambda_terms":[[f,str(v)] for f,v in sorted(lam.items())],
                "h_anti_terms":[[i,str(v)] for i,v in sorted(h.items())],
                "full_cover_degree2_generators_checked":rows_checked,
                "full_cover_dual_origin":str(L0),
                "source_generator_signatures_checked":len(cols),
                "full_cover_obstruction_proved":bool(L0)}
        results.append(result)
        print("BABEL21_SPARSE_DUAL_EXACT_Q_PASS",base,seed,j,
              "lambda_support",len(lam),"origin",str(L0),"checks",rows_checked,flush=True)
    report={"gate":"BABEL21_FULL_SOURCE_SPARSE_DUAL_Q_TEST","base":base,"seed":seed,
        "remaining_source_kera_dimension":k,"candidate_frequencies_tested":len(span.used),
        "exact_rational_source_rowspace_rank_lower":len(span.used),
        "source_base_distinct_generator_count":len(cols),"results":results,
        "full_degree2_obstruction_found":any(x.get("full_cover_obstruction_proved") for x in results),
        "scientific_scope":"Complete exact all-column negative only for components marked EXAC_Q_FULL_M2_NONMEMBERSHIP_PASS; sparse failure is not evidence of nonmembership."}
    path=Path(f"babel21_{base}_seed{seed}_sparse_dual_Q.json")
    path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("BABEL21_SPARSE_DUAL_SUMMARY",json.dumps({k:v for k,v in report.items() if k!="results"},sort_keys=True),flush=True)
    return report
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--base",default="SCL126_flip16")
    ap.add_argument("--seed",type=int,default=20);ap.add_argument("--maxcandidates",type=int,default=750)
    args=ap.parse_args();run(args.base,args.seed,args.maxcandidates)
