#!/usr/bin/env python3
"""Independent finite-field rank-witness replay for BABEL-18B.

No dependency on the producer's DSU, pivot selection, or image generation.
A complete set of independent integer columns modulo p proves full rank
over Q and hence surjectivity of B(ker T) on the anti-sector.
"""
import argparse,gzip,hashlib,json
from collections import defaultdict
from pathlib import Path
from janus_babel10_degree_scan import frozen_instances
from janus_babel10_lift_family import make_lift
from janus_babel6_transfer import xor_labels
from janus_babel7_degree_audit import degree_witnesses
from rank2_geometry import restriction
P=65521

class IndependentLinearVerifier:
    def __init__(self,n):
        self.parent=list(range(n))
        self.factor=[1]*n
        self.dead=[False]*n
        self.rank=0
    def find(self,i):
        parent=self.parent[i]
        if parent==i:return i,1
        root,f=self.find(parent)
        self.factor[i]=self.factor[i]*f%P
        self.parent[i]=root
        return root,self.factor[i]
    def insert_new_pivot(self,terms):
        table=defaultdict(int)
        for i,coef in terms:
            root,k=self.find(i)
            if not self.dead[root]:
                table[root]=(table[root]+coef*k)%P
        relation=[(i,k) for i,k in table.items() if k]
        if len(relation)==1:
            root,_=relation[0]
            assert not self.dead[root],"certificate pivot was linearly dependent"
            self.dead[root]=True
        elif len(relation)==2:
            (r,a),(s,b)=relation
            assert r!=s and not (self.dead[r] and self.dead[s])
            # Enforce a*y_r + b*y_s = 0, over exactly F_p.
            self.parent[r]=s
            self.factor[r]=(-b*pow(a,-1,P))%P
            self.dead[s]=self.dead[s] or self.dead[r]
        else:
            raise AssertionError(("pivot is not independent 1/2-term constraint",len(relation)))
        self.rank+=1

def verify(path):
    with gzip.open(path,"rt",encoding="utf-8") as f:doc=json.load(f)
    assert doc["format"]=="JANUS_BABEL18B_EXACT_MODULAR_ROW_RANK_WITNESS_V1"
    global P
    P=doc["prime"]
    seed=doc["seed"]
    source=frozen_instances()[doc["base_name"]]
    lift=make_lift(source,seed)[0]
    src_labels,src_Q,d=xor_labels(source)
    labels,Q,D=xor_labels(lift)
    pi,kernel=restriction(src_labels,labels,d,D)
    assert len(kernel)==2
    group=(0,kernel[0],kernel[1],kernel[0]^kernel[1])
    fibers=defaultdict(list)
    for q in sorted(Q):fibers[pi(q)].append(q)
    assert set(fibers)==set(src_Q)
    orbits=defaultdict(list)
    for q in sorted(degree_witnesses(labels,3)):
        orbits[min(q^g for g in group)].append(q)
    coord={}
    for members in orbits.values():
        for q in members[1:]:coord[q]=len(coord)
    n=len(coord)
    assert n==doc["antisector_dimension"] and len(doc["pivots"])<=n
    validator=IndependentLinearVerifier(n)
    rows_checked=0
    for r,src_u,rr,u in doc["pivots"]:
        assert 0<=r<len(source) and rr in (r,r+len(source))
        assert src_u in src_Q and u in Q and pi(u)==src_u
        anchor=fibers[src_u][0]
        assert (rr,u)!=(r,anchor)
        raw=defaultdict(int)
        for j in (u,*(u^labels[k] for k in lift[rr])):raw[j]+=1
        for j in (anchor,*(anchor^labels[k] for k in lift[r])):raw[j]-=1
        projected=defaultdict(int)
        for freq,c in raw.items():
            if c:projected[pi(freq)]+=c
        assert not any(projected.values()),"not a source-zero column"
        signature=[(coord[freq],c) for freq,c in raw.items() if c and freq in coord]
        validator.insert_new_pivot(signature)
        rows_checked+=1
        if rows_checked%15000==0:
            print("BABEL18B_INDEPENDENT_RANK_PROGRESS",seed,rows_checked,"of",n,flush=True)
    assert validator.rank==len(doc["pivots"])
    if len(doc["pivots"])==n:
        assert all(validator.dead[validator.find(i)[0]] for i in range(n)), "uneliminated anti coordinate"
    verdict={"status":("EXACT_Q_FULL_ANTISECTOR_RANK_VIA_MODULAR_NONZERO_MINOR_PASS" if len(doc["pivots"])==n else "INDEPENDENT_MODULAR_RANK_LOWER_BOUND_ONLY"),
       "seed":seed,"source":doc["base_name"],"prime":P,"independent_generators_checked":rows_checked,
       "anti_dimension":n,"rational_rank_lower_bound":len(doc["pivots"]), "full_rational_rank_proved":len(doc["pivots"])==n,
       "all_generators_source_zero_verified":True,
       "full_degree2_lifted_identity_exists":len(doc["pivots"])==n,
       "degree2_identity_explicitly_expanded":False,
       "proof_type":"modular full row rank implies rational full rank; exact integer source identity exists from BABEL17",
       "proof_sha256":hashlib.sha256(Path(path).read_bytes()).hexdigest(),
       "standard_psd_sos_equivalence_proved":False,
       "P_equals_NP_proved":False}
    print("BABEL18B_INDEPENDENT_VERDICT",json.dumps(verdict,sort_keys=True),flush=True)
    return verdict

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("proof",type=Path,nargs="+");args=ap.parse_args()
    reports=[verify(p) for p in args.proof]
    Path("babel18b_independent_rank_verdicts.json").write_text(json.dumps(reports,indent=2,sort_keys=True)+"\n")
