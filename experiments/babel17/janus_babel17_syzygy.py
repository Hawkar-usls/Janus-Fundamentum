#!/usr/bin/env python3
"""BABEL-17 exact source-column syzygy compatibility probe; NOT full SOS4 proof."""
import json, sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from janus_babel14_antisector_augmented import prepare
from janus_babel6_transfer import make_projection
from janus_babel8_krylov_verify import input_data

def solve(A,b):
    if not A:
        return [] if not any(b) else None
    n=len(A[0]); m=len(A)
    rows=[[Fraction(v) for v in A[i]]+[Fraction(b[i])] for i in range(m)]
    pivot_rows=[]; cur=0
    for col in range(n):
        at=next((j for j in range(cur,m) if rows[j][col]),None)
        if at is None: return None
        rows[cur],rows[at]=rows[at],rows[cur]
        scale=rows[cur][col]; rows[cur]=[v/scale for v in rows[cur]]
        for j in range(m):
            if j!=cur and rows[j][col]:
                scale=rows[j][col];rows[j]=[x-scale*y for x,y in zip(rows[j],rows[cur])]
        pivot_rows.append(cur);cur+=1
    if any(not any(row[:-1]) and row[-1] for row in rows):
        return None
    x=[rows[p][-1] for p in pivot_rows]
    assert all(sum(Fraction(A[i][j])*x[j] for j in range(n)) == b[i] for i in range(m))
    return x

def run():
    source,lift,labels,Q,e,canonical,touched,active,missing=prepare(3)
    _,src_labels,src_basis,eq,origins=input_data(68)
    pi,_=make_projection(src_labels,labels,15,16)
    reps={}
    for u in sorted(Q): reps.setdefault(pi(u),u)
    sets=[frozenset([0]+[src_labels[i] for i in row]) for row in source]
    pairs=[]
    for r in range(len(source)):
        for s in range(r+1,len(source)):
            for t in sets[r]:
                if {a^t for a in sets[r]} == sets[s]:
                    pairs.append((r,s,t))
    print("SOURCE_EQUIVALENT_ROW_PAIRS",len(pairs),flush=True)
    rec=json.loads(Path("babel16_SEED3_EXACT_PAIRED_KERNEL.json").read_text())
    seven=[w[0][0] for w in rec["kernel_vectors_sparse"]]
    residual=json.loads(Path("babel16_SEED3_SOURCE_RESIDUAL.json").read_text())
    target={q:-int(residual["unrestricted_integer_residual"][str(q)]) for q in seven}
    seen=set();candidates=[];basis=[];echelon=[]
    def signature(r,u,s,v):
        d=defaultdict(int)
        for row,m,sgn in ((r,u,1),(s,v,-1)):
            for z in (m,*(m^labels[k] for k in lift[row])):
                q,orient=canonical(z)
                if q in target: d[q]+=sgn*orient
        return tuple(d[q] for q in seven)
    for r,s,t in pairs:
        proposals=[]
        for a,b in ((r,s),(s,r)):
            for q in seven:
                for z in (q,q^e):
                    for k in (None,*lift[a]):
                        u=z^(0 if k is None else labels[k])
                        if u in Q: proposals.append((a,u))
        for a,u in proposals:
            if a==r:
                v=reps.get(pi(u)^t)
                if v is None:continue
                key=(r,u,s,v)
            else:
                v=reps.get(pi(u)^t)
                if v is None:continue
                key=(r,v,s,u)
            if key in seen:continue
            seen.add(key)
            rr,uu,ss,vv=key
            assert {pi(uu)^x for x in sets[rr]}=={pi(vv)^x for x in sets[ss]}
            sg=signature(rr,uu,ss,vv)
            if not any(sg):continue
            candidates.append((key,sg))
            vector=[Fraction(z) for z in sg]
            for pivot,bv in echelon:
                if vector[pivot]:
                    scale=vector[pivot]
                    vector=[x-scale*y for x,y in zip(vector,bv)]
            pivot=next((i for i,x in enumerate(vector) if x),None)
            if pivot is not None:
                scale=vector[pivot]
                echelon.append((pivot,[v/scale for v in vector]))
                basis.append((key,sg))
    A=[[sg[i] for key,sg in basis] for i in range(7)]
    x=solve(A,[target[q] for q in seven])
    record={
       "gate":"BABEL17_SOURCE_SYZYGY_COMPATIBILITY",
       "source_equal_fourier_column_row_pairings":len(pairs),
       "nonzero_candidate_source_syzygies":len(candidates),
       "exact_rank_of_seven_coordinate_syzygy_image":len(basis),
       "invisible_frequencies":seven,
       "canonical_residual_cancel_target":{str(q):str(target[q]) for q in seven},
       "target_in_exact_rational_syzygy_span":x is not None,
       "selected_source_syzygies":[
           {"r":k[0],"u":k[1],"s":k[2],"v":k[3],
            "signature":list(sg),"coefficient":str(x[i]) if x is not None else None}
           for i,(k,sg) in enumerate(basis)],
       "scope":"Source-syzygy seven-frequency compatibility only; no complete SOS4."
    }
    print("SYZYGY_IMAGE_RANK",len(basis),"TARGET_IN_SPAN",x is not None,flush=True)
    print("SYZYGY_SUMMARY",json.dumps({k:v for k,v in record.items() if k!="selected_source_syzygies"},sort_keys=True),flush=True)
    Path("babel17_SEED3_SYZYGY_COMPATIBILITY.json").write_text(json.dumps(record,sort_keys=True,indent=2)+"\n")
    return record
if __name__=="__main__":run()
