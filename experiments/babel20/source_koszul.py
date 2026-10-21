#!/usr/bin/env python3
"""BABEL-20 legal source Koszul image in exact rational ker(T) cokernel.

A positive full-rank Koszul response proves surjectivity of the *complete*
correction space, assuming an independent exact source certificate.
An incomplete Koszul response is NOT a full Fourier/SOS4 obstruction.
"""
import argparse,gzip,json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from crossbase_rank2 import setup
from exact_cokernel import SmallElimination
from janus_babel6_transfer import xor_labels

def audit(base,seed,max_candidates=500000):
    p=Path(f"babel20_{base}_seed{seed}_exact_Q_cokernel.json.gz")
    with gzip.open(p,"rt") as stream:data=json.load(stream)
    if "exact_rational_annihilators" not in data:
        print("BABEL20_KOSZUL_SKIPPED",base,seed,flush=True)
        return None
    hs=[{int(i):int(v) for i,v in h} for h in data["exact_rational_annihilators"]]
    m=len(hs)
    if m==0:
        verdict={"base":base,"seed":seed,"cokernel_Q_dim":0,"koszul_image_Q_rank":0,
                 "complete_correction_Q_rank_proved":True,
                 "full_fourier_degree2_certificate_exists_if_source_valid":True,
                 "selected":[]}
        Path(f"babel20_{base}_seed{seed}_koszul.json").write_text(json.dumps(verdict,indent=2,sort_keys=True)+"\n")
        return verdict
    source,lift,labels,base_Q,Q,kernel,fibers,coord,nactive,norbits=setup(seed,base)
    source_labels,src_Q,source_d=xor_labels(source)
    assert set(src_Q)==set(base_Q)
    defs=[(0,*(source_labels[j] for j in row)) for row in source]
    hidx={i:k for k,h in enumerate(hs) for i in h} # only used to count support
    touched={i for h in hs for i in h}
    values={}
    for r in range(len(source)):
        for p in sorted(base_Q):
            u=fibers[p][0]
            chars=(u,*(u^labels[j] for j in lift[r]))
            vec=tuple(sum(h.get(coord[q],0) for q in chars if q in coord) for h in hs)
            if any(vec):values[(r,p)]=vec
    print("BABEL20_KOSZUL_SOURCE_VALUES",base,seed,"nonzero",len(values),"cokernel_dim",m,flush=True)
    allkeys=set();basis=SmallElimination(m);count=0
    selected=[];zero=(0,)*m
    # All possible shifts generated from nonzero source coefficient responses.
    for r,p in sorted(values):
        if len(basis.selected)==m or count>=max_candidates:break
        for s in range(len(source)):
            if s==r:continue
            for a in defs[s]:
                t=p^a
                key=(min(r,s),max(r,s),t)
                if key in allkeys:continue
                allkeys.add(key);count+=1
                if count>max_candidates:break
                if any((t^x) not in base_Q for x in defs[r]):continue
                if any((t^x) not in base_Q for x in defs[s]):continue
                resp=[
                    sum(values.get((r,t^x),zero)[k] for x in defs[s]) -
                    sum(values.get((s,t^x),zero)[k] for x in defs[r])
                    for k in range(m)
                ]
                if not any(resp):continue
                terms=[(r,t^x,1) for x in defs[s]]+[(s,t^x,-1) for x in defs[r]]
                d=defaultdict(int)
                for rr,p0,sg in terms:
                    for a0 in defs[rr]:d[p0^a0]+=sg
                assert not any(d.values()),"candidate invalid source syzygy"
                if basis.add(resp,[r,s,t]):
                    selected.append({"r":r,"s":s,"t":t,"response":resp,
                                     "source_terms":terms})
                    print("BABEL20_KOSZUL_NEW_PIVOT",base,seed,
                          "rank",len(selected),"of",m,"r",r,"s",s,"t",t,flush=True)
                if len(selected)==m:break
            if len(selected)==m or count>max_candidates:break
    verdict={"gate":"BABEL20_EXACT_KOSZUL_SOURCE_SYZYGY_REPAIR",
       "base":base,"seed":seed,"exact_kerT_cokernel_dimension":m,
       "tested_source_koszul_candidates":count,
       "source_values_with_nonzero_cokernel_pairing":len(values),
       "independent_koszul_response_rank_over_Q":len(selected),
       "all_missing_directions_filled":len(selected)==m,
       "complete_correction_Q_rank_proved":len(selected)==m,
       "full_fourier_degree2_certificate_exists_if_source_valid":len(selected)==m,
       "selected":selected,
       "scope":"Only legal Koszul syzygies tested; incomplete does not prove full degree4 impossibility.",
       "universal_polynomial_bound_proved":False}
    Path(f"babel20_{base}_seed{seed}_koszul.json").write_text(json.dumps(verdict,sort_keys=True,indent=2)+"\n")
    print("BABEL20_KOSZUL_RESULT",json.dumps({k:v for k,v in verdict.items() if k!="selected"},sort_keys=True),flush=True)
    return verdict

if __name__=="__main__":
    a=argparse.ArgumentParser();a.add_argument("--base",required=True);a.add_argument("--seed",type=int,required=True)
    args=a.parse_args();audit(args.base,args.seed)
