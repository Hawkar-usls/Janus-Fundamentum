#!/usr/bin/env python3
"""BABEL-18: exact rank-2 character restriction geometry, seed0 and seed4."""
import hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
from janus_babel10_degree_scan import frozen_instances
from janus_babel10_lift_family import make_lift
from janus_babel6_transfer import xor_labels, assert_valid_double_cover

def restriction(base_labels,lift_labels,d,D):
    n=len(base_labels)
    pivot={}
    for j,x0 in enumerate(lift_labels):
        x,y=x0,base_labels[j%n]
        while x:
            k=x.bit_length()-1
            if k not in pivot:
                pivot[k]=(x,y)
                break
            a,b=pivot[k]
            x^=a;y^=b
        else:
            assert not y,"inconsistent diagonal source projection"
    assert len(pivot)==D
    def pi(x):
        y=0
        while x:
            a,b=pivot[x.bit_length()-1]
            x^=a;y^=b
        return y
    assert all(pi(x)==base_labels[j%n] for j,x in enumerate(lift_labels))
    reduced={};kernel=[]
    for bit in range(D):
        x,y=1<<bit,pi(1<<bit)
        while y:
            p=y.bit_length()-1
            if p not in reduced:
                reduced[p]=(y,x)
                break
            oy,ox=reduced[p]
            y^=oy;x^=ox
        else:
            kernel.append(x)
    assert len(kernel)==D-d and all(pi(v)==0 for v in kernel)
    return pi,kernel

def audit(seed):
    source=frozen_instances()["SCL126_flip68"]
    lift=make_lift(source,seed)[0]
    assert_valid_double_cover(source,lift)
    src_labels,src_Q,d=xor_labels(source)
    labels,Q,D=xor_labels(lift)
    pi,kernel=restriction(src_labels,labels,d,D)
    fibers=defaultdict(list)
    for u in Q:fibers[pi(u)].append(u)
    distribution=Counter(len(fibers.get(p,[])) for p in src_Q)
    allkernel={0}
    for e in kernel:allkernel.update({x^e for x in list(allkernel)})
    assert len(allkernel)==1<<len(kernel)
    assert all(pi(x)==0 for x in allkernel)
    projected_degree1_ok=True
    for x in [0,*labels]:
        if pi(x) not in {0,*src_labels}:projected_degree1_ok=False
    result={"seed":seed,"source":"SCL126_flip68","source_rows":len(source),
       "cover_rows":len(lift),"legal_double_cover_verified":True,
       "base_gf2_kernel_dimension":d,"cover_gf2_kernel_dimension":D,
       "additional_character_kernel_dimension":len(kernel),
       "kernel_generators":kernel,"kernel_group_order":len(allkernel),
       "degree2_cover_character_count":len(Q),
       "degree2_source_character_count":len(src_Q),
       "source_degree2_projection_fiber_distribution":{str(k):v for k,v in sorted(distribution.items())},
       "source_degree2_characters_without_legal_lift":distribution.get(0,0),
       "projection_preserves_degree1":projected_degree1_ok,
       "rank1_transfer_assumptions_valid":D==d+1,
       "status":"EXACT_RANK2_KERNEL_GEOMETRY_PASS" if D-d==2 else "OBSERVED_DIFFERENT_KERNEL_DIMENSION",
       "scientific_limit":"No seed-specific exact upper Fourier identity or polynomial-time result proved."}
    return result
if __name__=="__main__":
    outputs=[]
    for seed in (0,4):
        record=audit(seed)
        print("BABEL18_RANK_GEOMETRY",json.dumps(record,sort_keys=True),flush=True)
        outputs.append(record)
    Path("babel18_seed0_seed4_exact_geometry.json").write_text(json.dumps(outputs,indent=2,sort_keys=True)+"\n")
