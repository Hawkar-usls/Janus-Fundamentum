#!/usr/bin/env python3
"""BABEL-21: source-syzygy search against unresolved exact kerT cokernel.

Scans unique full SOURCE degree-2 generators A_{r,u}, not just Koszul or
equal-column relations. A finite-field dependency with nonzero cokernel
response is a candidate only until its *integer* source identity is verified.
Never asserts degree-4 impossibility from a failed search.
"""
import argparse,json,gzip,time
from collections import defaultdict,Counter
from fractions import Fraction
from pathlib import Path
from crossbase_rank2 import setup
from exact_cokernel import SmallElimination
from janus_babel6_transfer import xor_labels

P=65521

def complement(base,seed):
    with gzip.open(f"babel20_{base}_seed{seed}_exact_Q_cokernel.json.gz","rt") as f:d=json.load(f)
    hs=[{int(i):int(v) for i,v in witness} for witness in d["exact_rational_annihilators"]]
    m=len(hs);assert m>0
    records=json.loads(Path(f"babel20_{base}_seed{seed}_koszul.json").read_text())
    extra=Path(f"babel20_{base}_seed{seed}_combined_syzygies.json")
    exact=SmallElimination(m)
    for x in records["selected"]:exact.add(x["response"],("koszul",x["r"],x["s"],x["t"]))
    if extra.exists():
        for x in json.loads(extra.read_text())["new_equal_column_witnesses"]:
            exact.add(x["response"],("equal",x["rowA"],x["rowB"]))
    alpha=exact.annihilators()
    print("BABEL21_COMPLEMENT",base,seed,"source_cokernel_dim",m,
          "known_source_syzygy_rank",len(exact.selected),"unexplained_dim",len(alpha),flush=True)
    return hs,alpha

def evaluate(base,seed):
    source,lift,labels,base_Q,Q,kernel,fibers,coord,active,orbits=setup(seed,base)
    hs,alpha=complement(base,seed)
    allh=[]
    for vector in alpha:
        combined=defaultdict(Fraction)
        for a,h in zip(vector,hs):
            if a:
                for i,v in h.items():combined[i]+=a*v
        allh.append({i:v for i,v in combined.items() if v})
    src_labels,srcQ,d=xor_labels(source)
    assert set(srcQ)==set(base_Q)
    cols={}
    response_count=0
    duplicates=0
    for r,row in enumerate(source):
        defects=(0,*(src_labels[j] for j in row))
        cover_defects=(0,*(labels[j] for j in lift[r]))
        for p in sorted(base_Q):
            sig=tuple(sorted(p^x for x in defects))
            u=fibers[p][0]
            cover_freq=[u^x for x in cover_defects]
            response=tuple(sum(h.get(coord[q],0) for q in cover_freq if q in coord) for h in allh)
            if any(response):response_count+=1
            if sig in cols:
                assert cols[sig][2]==response,("unseen exact equal-source relation!",r,p,cols[sig][0],cols[sig][1],response,cols[sig][2])
                duplicates+=1
            else:
                cols[sig]=(r,p,response)
    return source,src_labels,base_Q,list(sorted(cols.items(),key=lambda a:(not any(a[1][2]),a[0]))),len(alpha),response_count,duplicates

def mod_relations(base,seed,max_pivots,max_nnz):
    start=time.monotonic()
    source,src_labels,Q,cols,k,nonzero,dups=evaluate(base,seed)
    if k==0:return {"status":"SOURCE_KER_A_COMPLETE_ALREADY","base":base,"seed":seed}
    pivot={}  # pivot frequency -> (normalized sparse Fourier col, normalized response, history)
    found=[];rank_response=0;skipped=0;collisions=0
    for ix,(signature,(r,p,resp0)) in enumerate(cols):
        vec=Counter(signature)
        vec={q:v%P for q,v in vec.items() if v%P}
        response=[int(v.numerator*pow(v.denominator,-1,P)%P) for v in resp0]
        steps=[]
        while vec:
            at=min(vec)
            if at not in pivot:break
            basis,bresp,bhist=pivot[at]
            scale=vec[at]
            steps.append((at,scale))
            for q,v in basis.items():
                x=(vec.get(q,0)-scale*v)%P
                if x:vec[q]=x
                elif q in vec:del vec[q]
            for j,a in enumerate(bresp):response[j]=(response[j]-scale*a)%P
            if len(vec)>max_nnz:break
        if len(vec)>max_nnz:
            skipped+=1;continue
        if not vec:
            collisions+=1
            if any(response):
                print("BABEL21_MODULAR_SOURCE_SYZYGY_HIT",base,seed,
                      "generator",ix,"r",r,"p",p,
                      "response",response,"steps",len(steps),"rank",len(pivot),flush=True)
                found.append({"origin":[r,p],"original_signature":signature,
                   "response_modP":response,"source_rows_processed":ix+1,
                   "dependency_pivot_chain":len(steps)})
                break
        else:
            at=min(vec);inv=pow(vec[at],-1,P)
            b={q:v*inv%P for q,v in vec.items()}
            y=[v*inv%P for v in response]
            pivot[at]=(b,y,(r,p,steps,inv))
            if len(pivot)>=max_pivots:break
        if (ix+1)%15000==0:
            print("BABEL21_SOURCE_RANK_PROGRESS",base,seed,
                  "columns",ix+1,"source_rank",len(pivot),"skipped",skipped,
                  "seconds",round(time.monotonic()-start,1),flush=True)
    verdict={"gate":"BABEL21_SOURCE_KER_A_GENERAL_SEARCH",
      "base":base,"seed":seed,"unexplained_source_syzygy_dimension":k,
      "base_distinct_source_generators":len(cols),"base_generator_duplicates":dups,
      "canonical_lift_nonzero_responses":nonzero,
      "processed_base_generators":ix+1,"source_pivots_obtained":len(pivot),
      "source_columns_skipped_density_limit":skipped,
      "modular_source_syzygy_candidates":found,
      "exact_Q_source_syzygy_pass":False,
      "all_full_M2_columns_checked_for_negative":False,
      "P_equals_NP_proved":False,
      "status":"MODULAR_DIAGNOSTIC_ONLY"}
    Path(f"babel21_{base}_seed{seed}_source_kernel_probe.json").write_text(json.dumps(verdict,indent=2,sort_keys=True)+"\n")
    print("BABEL21_SOURCE_PROBE_RESULT",json.dumps({k:v for k,v in verdict.items() if k!="modular_source_syzygy_candidates"},sort_keys=True),flush=True)
    return verdict

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--base",default="SCL126_flip16")
    ap.add_argument("--seed",type=int,default=20);ap.add_argument("--max-pivots",type=int,default=10000)
    ap.add_argument("--max-nnz",type=int,default=500)
    args=ap.parse_args();mod_relations(args.base,args.seed,args.max_pivots,args.max_nnz)
