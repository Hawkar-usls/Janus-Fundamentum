#!/usr/bin/env python3
"""BABEL-18B multi-pass exact finite-field rank lower bound for ALL ker(T) columns.

All integer Fourier generators are enumerated; each coefficient is reduced
using the current exact F_65521 linear quotient (unary and binary relations).
If all quotient variables vanish, full row rank is proved OVER Q. Otherwise
NO conclusion of SOS4 impossibility. No source syzygies are omitted from a
negative full-matrix claim because no such claim is made.
"""
import argparse,json,time,gzip,hashlib
from collections import Counter,defaultdict
from pathlib import Path
from full_kerT_sparse import WeightedDSU,P
from janus_babel10_degree_scan import frozen_instances
from janus_babel10_lift_family import make_lift
from janus_babel6_transfer import xor_labels
from janus_babel7_degree_audit import degree_witnesses
from rank2_geometry import restriction

def setup(seed):
    source=frozen_instances()["SCL126_flip68"]
    lift=make_lift(source,seed)[0]
    source_labels,base_Q,d=xor_labels(source)
    labels,Q,D=xor_labels(lift)
    pi,kernel=restriction(source_labels,labels,d,D)
    assert len(kernel)==2
    g=(0,kernel[0],kernel[1],kernel[0]^kernel[1])
    fibers=defaultdict(list)
    for q in sorted(Q):fibers[pi(q)].append(q)
    assert set(fibers)==set(base_Q)
    active=degree_witnesses(labels,3)
    orbits=defaultdict(list)
    for q in sorted(active):orbits[min(q^k for k in g)].append(q)
    coord={}
    for qs in orbits.values():
        first=qs[0]
        for q in qs[1:]:coord[q]=len(coord)
    assert len(coord)==len(active)-len(orbits)
    return source,lift,labels,base_Q,Q,kernel,fibers,coord,len(active),len(orbits)

def generate(source,lift,labels,base_Q,fibers,coord):
    n=len(source)
    for r in range(n):
        rowa=lift[r]
        rowb=lift[r+n]
        for source_u in sorted(base_Q):
            fiber=fibers[source_u]
            anchor=fiber[0]
            base=(anchor,*(anchor^labels[j] for j in rowa))
            for rr,row in ((r,rowa),(r+n,rowb)):
                for u in fiber:
                    if rr==r and u==anchor:continue
                    diff=defaultdict(int)
                    for q in (u,*(u^labels[j] for j in row)):diff[q]+=1
                    for q in base:diff[q]-=1
                    yield r,source_u,rr,u,tuple((coord[q],v) for q,v in diff.items()
                                 if v and q in coord)

def apply_short(uf,signature):
    if not signature:return 0
    reduced=defaultdict(int)
    for i,v in signature:
        root,weight=uf.find(i)
        if not uf.zero[root]:reduced[root]=(reduced[root]+v*weight)%P
    row=[(i,v) for i,v in reduced.items() if v]
    if len(row)==1:
        return int(uf.force_zero(row[0][0]))
    if len(row)==2:
        (i,a),(j,b)=row
        return int(uf.add(i,a,j,b))
    return 0

def audit(seed,passes=6):
    src,lift,labels,base_Q,Q,kernel,fibers,coord,nactive,norbits=setup(seed)
    dimension=len(coord)
    uf=WeightedDSU(dimension)
    output=[]
    pivots=[]
    started=time.monotonic()
    expected=2*len(src)*len(Q)-len(src)*len(base_Q)
    for phase in range(passes):
        before=uf.independent
        counts=Counter()
        enumerated=0
        for row_idx,source_u,rr,u,signature in generate(src,lift,labels,base_Q,fibers,coord):
            enumerated+=1
            if phase==0:
                counts["original_"+str(len(signature))]+=1
                # Initial generators >2 are not reduced before UF has context,
                # but immediately reducing them is safe and stronger.
            if signature:
                reduced=defaultdict(int)
                for i,v in signature:
                    root,weight=uf.find(i)
                    if not uf.zero[root]:reduced[root]=(reduced[root]+v*weight)%P
                row=[(i,v) for i,v in reduced.items() if v]
            else:row=[]
            previous_rank=uf.independent
            if len(row)==1:uf.force_zero(row[0][0])
            elif len(row)==2:
                (i,a),(j,b)=row
                uf.add(i,a,j,b)
            if uf.independent>previous_rank:
                assert uf.independent==previous_rank+1
                pivots.append([row_idx,source_u,rr,u])
            counts["reduced_"+str(len(row))]+=1
        assert enumerated==expected,(enumerated,expected)
        delta=uf.independent-before
        result={"pass":phase+1,"rank_lower":uf.independent,
                "co_kernel_dimension_at_most":uf.free,"new_independent_pivots":delta,
                "support_distribution":dict(sorted(counts.items())),
                "time_seconds":round(time.monotonic()-started,1)}
        output.append(result)
        print("BABEL18B_ITERATIVE_PASS",seed,json.dumps({k:v for k,v in result.items() if k!="support_distribution"},sort_keys=True),flush=True)
        if uf.free==0 or delta==0:break
    witness_path=Path(f"babel18b_seed{seed}_independent_modular_pivots.json.gz")
    with gzip.open(witness_path,"wt",encoding="utf-8",compresslevel=6) as f:
        json.dump({"format":"JANUS_BABEL18B_EXACT_MODULAR_ROW_RANK_WITNESS_V1",
                   "seed":seed,"prime":P,"antisector_dimension":dimension,
                   "pivots":pivots},f,separators=(",",":"),sort_keys=True)
    assert len(pivots)==uf.independent
    witness_sha256=hashlib.sha256(witness_path.read_bytes()).hexdigest()
    summary={"gate":"BABEL18B_ITERATIVE_MODULAR_SHORT_COLUMN_ELIMINATION",
        "seed":seed,"prime":P,"all_kerT_generators_per_pass":expected,
        "pivot_witness":str(witness_path),"pivot_witness_sha256":witness_sha256,
        "pivot_witness_length":len(pivots),
        "target_antisector_dimension":dimension,
        "exact_full_rank_over_Q_proved":uf.free==0,
        "rational_full_antisector_membership_for_arbitrary_base_certificate":uf.free==0,
        "final_rank_lower_bound_over_Q":uf.independent,
        "final_co_kernel_dimension_at_most":uf.free,
        "iterations":output,
        "scientific_limit":"Failure to reach full rank in these passes does NOT prove rational nonmembership or SOS4 lower bound; source syzygies are separate."}
    print("BABEL18B_ITERATIVE_RESULT",json.dumps({k:v for k,v in summary.items() if k!="iterations"},sort_keys=True),flush=True)
    return summary

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--passes",type=int,default=6)
    parser.add_argument("--seed",type=int,choices=(0,4))
    args=parser.parse_args()
    seeds=[args.seed] if args.seed is not None else [0,4]
    results=[audit(seed,args.passes) for seed in seeds]
    Path("babel18b_iterated_antisector_rank.json").write_text(json.dumps(results,indent=2,sort_keys=True)+"\n")
