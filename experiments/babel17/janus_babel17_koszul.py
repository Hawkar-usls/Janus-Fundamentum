#!/usr/bin/env python3
"""BABEL-17: exact Koszul row-syzygy image on 7 invisible seed3 frequencies."""
import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from janus_babel14_antisector_augmented import prepare
from janus_babel6_transfer import make_projection
from janus_babel8_krylov_verify import input_data
from janus_babel17_syzygy import solve

def run():
    source,lift,labels,Q,e,canonical,*_=prepare(3)
    rows,src_labels,src_basis,eq,origins=input_data(68)
    assert rows==source
    pi,_=make_projection(src_labels,labels,15,16)
    reps={}
    for u in sorted(Q): reps.setdefault(pi(u),u)
    sets=[tuple(sorted([0]+[src_labels[i] for i in row])) for row in source]
    kernel=json.loads(Path("babel16_SEED3_EXACT_PAIRED_KERNEL.json").read_text())
    seven=[w[0][0] for w in kernel["kernel_vectors_sparse"]]
    residual=json.loads(Path("babel16_SEED3_SOURCE_RESIDUAL.json").read_text())
    target=tuple(-int(residual["unrestricted_integer_residual"][str(q)]) for q in seven)
    qi={q:i for i,q in enumerate(seven)}
    toucher=[]
    for r in range(len(source)):
        ps=set()
        for q in seven:
            for z in (q,q^e):
                for k in (None,*lift[r]):
                    u=z^(0 if k is None else labels[k])
                    if u in Q:ps.add(pi(u))
        rowmap={}
        for p in ps:
            u=reps[p]
            vec=[0]*7
            for z in (u,*(u^labels[k] for k in lift[r])):
                q,sgn=canonical(z)
                if q in qi:vec[qi[q]]+=sgn
            if any(vec):rowmap[p]=tuple(vec)
        toucher.append(rowmap)
    zeros=(0,)*7
    echelon=[];basis=[];nonzero=0;tested=0
    for r in range(len(source)):
        setr=sets[r]; tr=toucher[r]
        for s in range(r+1,len(source)):
            sets_=sets[s];ts=toucher[s]
            tset={p^w for p in tr for w in sets_}
            tset.update(p^w for p in ts for w in setr)
            for t in sorted(tset):
                if any((t^w) not in reps for w in (*setr,*sets_)):continue
                tested+=1
                vec=[0]*7
                for w in sets_:
                    for j,v in enumerate(tr.get(t^w,zeros)):vec[j]+=v
                for w in setr:
                    for j,v in enumerate(ts.get(t^w,zeros)):vec[j]-=v
                if not any(vec):continue
                nonzero+=1
                red=[Fraction(x) for x in vec]
                for pivot,bv in echelon:
                    if red[pivot]:
                        scale=red[pivot];red=[x-scale*y for x,y in zip(red,bv)]
                p=next((j for j,z in enumerate(red) if z),None)
                if p is None:continue
                scale=red[p]
                echelon.append((p,[z/scale for z in red]))
                basis.append((r,s,t,tuple(vec)))
                print("KOSZUL_BASIS",len(basis),"r",r,"s",s,"t",t,"vector",vec,flush=True)
    A=[[w[3][i] for w in basis] for i in range(7)]
    coeff=solve(A,target)
    witness=[]
    for k,(r,s,t,signature) in enumerate(basis):
        terms=[]
        for w in sets[s]:terms.append([r,reps[t^w],1])
        for w in sets[r]:terms.append([s,reps[t^w],-1])
        # Exact zero under source projection for every Fourier coordinate
        check=defaultdict(int)
        for rr,u,sgn in terms:
            p=pi(u)
            for a in sets[rr]:check[p^a]+=sgn
        assert not any(check.values())
        witness.append({"r":r,"s":s,"shift":t,"signature":signature,
                        "source_zero_terms":terms,
                        "coefficient":str(coeff[k]) if coeff is not None else None})
    record={"gate":"BABEL17_KOSZUL_SEED3_COMPATIBILITY",
            "source_rows":len(source),"eligible_source_characters":len(reps),
            "seven_invisible_frequencies":seven,"source_residual_cancel_target":list(map(str,target)),
            "tested_candidate_shifts":tested,"nonzero_syzygy_signatures":nonzero,
            "exact_koszul_syzygy_image_rank":len(basis),
            "cancel_target_in_exact_span":coeff is not None,
            "basis_witnesses":witness,
            "scope":"Only seven-coordinate Koszul source compatibility; not full degree-2 multiplier certificate."}
    Path("babel17_SEED3_KOSZUL_COMPATIBILITY.json").write_text(json.dumps(record,indent=2,sort_keys=True)+"\n")
    print("KOSZUL_SUMMARY",json.dumps({k:v for k,v in record.items() if k not in ("basis_witnesses","source_residual_cancel_target")},sort_keys=True),flush=True)
    return record
if __name__=="__main__":run()
