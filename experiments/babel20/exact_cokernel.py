#!/usr/bin/env python3
"""BABEL-20 exact small-cokernel audit for ALL ker(T) generators.

Uses rational arithmetic to reduce selected verified modular pivots, then scans
*every* legal difference with rational quotient elimination. When quotient
rank is incomplete, explicitly verifies rational annihilators on ALL columns.
This does not prove failure of the full degree-2 ideal system.
"""
import argparse,gzip,json,math
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from crossbase_rank2 import setup,generate
from rank2_geometry import restriction
from janus_babel6_transfer import xor_labels

class ExactForest:
    def __init__(self,n):
        self.par=list(range(n));self.weight=[Fraction(1)]*n;self.dead=[False]*n
    def find(self,i):
        p=self.par[i]
        if p!=i:
            r,v=self.find(p)
            self.par[i]=r;self.weight[i]*=v
        return self.par[i],self.weight[i]
    def reduce(self,terms):
        d=defaultdict(Fraction)
        for i,v in terms:
            r,w=self.find(i)
            if not self.dead[r]:d[r]+=w*v
        return {r:v for r,v in d.items() if v}
    def insert(self,terms):
        d=self.reduce(terms)
        assert 1<=len(d)<=2,("pivot not short over Q",len(d))
        if len(d)==1:
            r=next(iter(d));assert not self.dead[r];self.dead[r]=True
        else:
            (r,a),(s,b)=list(d.items())
            self.par[r]=s;self.weight[r]=-b/a
            self.dead[s]=self.dead[s] or self.dead[r]

def column_signature(r,su,rr,u,lift,labels,coord,fibers):
    a=fibers[su][0];d=defaultdict(int)
    for q in (u,*(u^labels[j] for j in lift[rr])):d[q]+=1
    for q in (a,*(a^labels[j] for j in lift[r])):d[q]-=1
    return [(coord[q],v) for q,v in d.items() if v and q in coord]

class SmallElimination:
    def __init__(self,dim):
        self.dim=dim;self.basis={}
        self.selected=[]
    def add(self,vec,metadata):
        d=dict((i,Fraction(v)) for i,v in enumerate(vec) if v)
        for p,row in sorted(self.basis.items()):
            if p in d:
                a=d.pop(p)
                for j,v in row.items():
                    if j!=p:
                        x=d.get(j,0)-a*v
                        if x:d[j]=x
                        elif j in d:del d[j]
        if not d:return False
        p=min(d)
        a=d[p]
        self.basis[p]={j:v/a for j,v in d.items()}
        self.selected.append(metadata)
        return True
    def annihilators(self):
        pivots=set(self.basis)
        out=[]
        for free in range(self.dim):
            if free in pivots:continue
            vec=[Fraction(0)]*self.dim
            vec[free]=1
            for p,row in sorted(self.basis.items(),reverse=True):
                vec[p]=-sum(v*vec[j] for j,v in row.items() if j!=p)
            out.append(vec)
        return out

def audit(base,seed,prime=65521,max_dim=32):
    src,lift,labels,base_Q,Q,kernel,fibers,coord,nactive,norbits=setup(seed,base)
    N=len(coord);n=len(src)
    witness_path=Path(f"babel19_{base}_seed{seed}_p{prime}_modular_pivots.json.gz")
    with gzip.open(witness_path,"rt") as f:doc=json.load(f)
    assert doc["base_name"]==base and doc["seed"]==seed and doc["antisector_dimension"]==N
    pivot_list=doc["pivots"]
    missing=N-len(pivot_list)
    if missing>max_dim:
        return {"base":base,"seed":seed,"status":"UNRESOLVED_HIGH_COKERNEL_UPPER_BOUND",
                "rank_Q_lower":len(pivot_list),"anti_dimension":N,
                "unresolved_upper":missing}
    uf=ExactForest(N)
    for k,(r,su,rr,u) in enumerate(pivot_list):
        uf.insert(column_signature(r,su,rr,u,lift,labels,coord,fibers))
    roots=sorted({uf.find(i)[0] for i in range(N) if not uf.dead[uf.find(i)[0]]})
    assert len(roots)==missing,(len(roots),missing)
    idmap={r:k for k,r in enumerate(roots)}
    small=SmallElimination(missing)
    total=0
    for r,su,rr,u,signature in generate(src,lift,labels,base_Q,fibers,coord):
        reduced=uf.reduce(signature)
        row=[0]*missing
        for root,v in reduced.items():row[idmap[root]]=v
        small.add(row,[r,su,rr,u])
        total+=1
    assert total==2*n*len(Q)-n*len(base_Q)
    exact_rank=len(pivot_list)+len(small.selected)
    null=small.annihilators()
    assert exact_rank+len(null)==N
    integer_witnesses=[]
    for vec in null:
        h={}
        for i in range(N):
            root,w=uf.find(i)
            if not uf.dead[root] and vec[idmap[root]]:
                h[i]=w*vec[idmap[root]]
        den=math.lcm(*(v.denominator for v in h.values()))
        ints={i:int(v*den) for i,v in h.items()}
        gcd=math.gcd(*ints.values())
        ints={i:v//gcd for i,v in ints.items()}
        assert ints
        integer_witnesses.append(ints)
    if null:
        count=0
        for r,su,rr,u,col in generate(src,lift,labels,base_Q,fibers,coord):
            for h in integer_witnesses:
                assert sum(h.get(i,0)*v for i,v in col)==0,("not genuine full kerT cokernel",r,su,rr,u)
            count+=1
        assert count==total
    result={"gate":"BABEL20_EXACT_SMALL_COKERNEL_ALL_COLUMNS",
      "base":base,"seed":seed,"anti_dimension":N,
      "original_rational_rank_lower":len(pivot_list),
      "new_long_column_Q_pivots":len(small.selected),
      "exact_Q_rank_of_all_kerT":exact_rank,
      "exact_Q_cokernel_dimension":len(null),
      "all_kerT_columns_tested":total,
      "candidate_long_pivots":small.selected,
      "exact_rational_annihilators":[[[i,str(v)] for i,v in sorted(h.items())] for h in integer_witnesses],
      "full_degree2_system_nonmembership":"NOT_TESTED",
      "scientific_scope":"Only B(kerT), not full B(kerT)+BS(kerA)."}
    path=Path(f"babel20_{base}_seed{seed}_exact_Q_cokernel.json.gz")
    with gzip.open(path,"wt",encoding="utf-8") as f:json.dump(result,f,sort_keys=True,separators=(",",":"))
    print("BABEL20_EXACT_COKERNEL",json.dumps({k:v for k,v in result.items() if k not in ("candidate_long_pivots","exact_rational_annihilators")},sort_keys=True),flush=True)
    return result

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--base",required=True)
    ap.add_argument("--seed",type=int,required=True)
    args=ap.parse_args()
    audit(args.base,args.seed)
