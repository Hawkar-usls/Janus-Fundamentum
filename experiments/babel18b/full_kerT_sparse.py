#!/usr/bin/env python3
"""BABEL-18B full rank-2 antisymmetric sparse-operator *structure* over F_p.

Enumerates ALL ker(T) generators exactly (no 2^d state enumeration) and proves
a modular rank lower bound from every 1- and 2-sparse correction column.
If all rows are killed, this also proves rational surjectivity for ker(T).
Otherwise remains a *lower bound only*. Full original source syzygies not yet
tested, so NO negative assertion about overall SOS4.
"""
import argparse,hashlib,json,time
from collections import Counter,defaultdict
from pathlib import Path
from janus_babel10_degree_scan import frozen_instances
from janus_babel10_lift_family import make_lift
from janus_babel6_transfer import xor_labels
from janus_babel7_degree_audit import degree_witnesses
from rank2_geometry import restriction

P=65521
class WeightedDSU:
    def __init__(self,n):
        self.parent=list(range(n));self.w=[1]*n;self.zero=[False]*n
        self.free=n;self.independent=0;self.conflicts=0;self.unions=0;self.unary=0
    def find(self,i):
        p=self.parent[i]
        if i!=p:
            r,w=self.find(p)
            self.w[i]=self.w[i]*w%P
            self.parent[i]=r
        return self.parent[i],self.w[i]
    def force_zero(self,i):
        r,_=self.find(i)
        if not self.zero[r]:
            self.zero[r]=True;self.free-=1;self.independent+=1;self.unary+=1
            return True
        return False
    def add(self,i,a,j,b):
        ri,wi=self.find(i);rj,wj=self.find(j)
        aa=a*wi%P;bb=b*wj%P
        if ri==rj:
            if (aa+bb)%P:
                self.conflicts+=1;return self.force_zero(i)
            return False
        self.parent[ri]=rj
        self.w[ri]=-bb*pow(aa,-1,P)%P
        self.zero[rj]=self.zero[rj] or self.zero[ri]
        if not (self.zero[ri] and self.zero[rj]):
            self.free-=1;self.independent+=1
        self.unions+=1
        return True

def audit(seed,limit=None):
    started=time.monotonic()
    source=frozen_instances()["SCL126_flip68"]
    lift=make_lift(source,seed)[0]
    source_labels,base_Q,d=xor_labels(source)
    labels,Q,D=xor_labels(lift)
    pi,kernel=restriction(source_labels,labels,d,D)
    assert len(kernel)==2
    G=[0,kernel[0],kernel[1],kernel[0]^kernel[1]]
    group=set(G)
    assert len(group)==4
    fibers=defaultdict(list)
    for q in sorted(Q):fibers[pi(q)].append(q)
    assert set(fibers)==set(base_Q)
    active=degree_witnesses(labels,3)
    orbits=defaultdict(list)
    for q in sorted(active):
        orbit=min(q^k for k in G)
        orbits[orbit].append(q)
    nonanchor={}
    for ql in orbits.values():
        first=min(ql)
        for q in ql:
            if q!=first:nonanchor[q]=len(nonanchor)
    dimension=len(nonanchor)
    assert dimension==len(active)-len(orbits)
    uf=WeightedDSU(dimension)
    counters=Counter()
    examples=[]
    digest=hashlib.sha256()
    n=len(source)
    total=0
    for r in range(n):
        for source_u in sorted(base_Q):
            fiber=fibers[source_u]
            anchor=fiber[0]
            ref=(anchor,*(anchor^labels[j] for j in lift[r]))
            for rr in (r,r+n):
                for u in fiber:
                    if rr==r and u==anchor:continue
                    accum=defaultdict(int)
                    for q in (u,*(u^labels[j] for j in lift[rr])):accum[q]+=1
                    for q in ref:accum[q]-=1
                    column=tuple(sorted((nonanchor[q],v) for q,v in accum.items()
                                        if v and q in nonanchor))
                    total+=1
                    counters["nnz_"+str(len(column))]+=1
                    if len(column)<=2:
                        if len(column)==1:
                            i,a=column[0]
                            if a%P:uf.force_zero(i)
                        elif len(column)==2:
                            (i,a),(j,b)=column
                            if a%P and b%P:uf.add(i,a,j,b)
                    if len(examples)<8 and column and len(column)<4:
                        examples.append({"base_row":r,"source_u":source_u,
                          "lift_row":rr,"u":u,"sparse_column":column})
                    digest.update(str((r,source_u,rr,u,column)).encode())
                    digest.update(b"\n")
                    if limit is not None and total>=limit:break
                if limit is not None and total>=limit:break
            if limit is not None and total>=limit:break
        if (r+1)%21==0:
            print("BABEL18B_PROGRESS",seed,r+1,"of",n,"columns",total,
                  "rank_lower",uf.independent,"target_dim",dimension,
                  "seconds",round(time.monotonic()-started,1),flush=True)
        if limit is not None and total>=limit:break
    if limit is None:
        expected=2*n*len(Q)-n*len(base_Q)
        assert total==expected,(total,expected)
    result={
       "gate":"BABEL18B_ANTISECTOR_SPARSE_OPERATOR",
       "seed":seed,"base_row_count":n,"cover_row_count":2*n,
       "additional_kernel_generators":kernel,
       "base_multiplier_types":len(base_Q),
       "lift_multiplier_types":len(Q),
       "all_full_kerT_generators_enumerated":limit is None,
       "enumerated_columns":total,
       "expected_columns":2*n*len(Q)-n*len(base_Q),
       "character_orbit_count":len(orbits),
       "active_degree3_rows":len(active),
       "antisymmetric_dimension":dimension,
       "column_support_distribution":dict(sorted(counters.items())),
       "rank_prime":P,"short_column_rank_lower_bound_over_Q":uf.independent,
       "short_column_co_kernel_dimension_at_most":uf.free,
       "short_column_modular_unions":uf.unions,
       "short_column_modular_frustration_events":uf.conflicts,
       "all_short_columns_cover_antisector":uf.free==0,
       "exact_int_column_sha256":digest.hexdigest(),
       "examples":examples,
       "all_source_syzygies_included":False,
       "complete_rational_membership":("PASS_VIA_FULL_RANK_CERTIFICATE" if uf.free==0
                                       else "NOT_DECIDED"),
       "scientific_limit":"If short-column rank deficient, full ker(T) and source syzygies could still resolve it. No false full SOS4 obstruction.",
       "elapsed_seconds":round(time.monotonic()-started,1)}
    print("BABEL18B_RESULT",json.dumps({k:v for k,v in result.items() if k!="examples"},sort_keys=True),flush=True)
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--seed",type=int,choices=(0,4))
    p.add_argument("--limit",type=int,default=None);p.add_argument("--output",type=Path,default=Path("babel18b_rank2_sparse_audit.json"))
    args=p.parse_args()
    seeds=[args.seed] if args.seed is not None else [0,4]
    records=[audit(s,args.limit) for s in seeds]
    args.output.write_text(json.dumps(records,indent=2,sort_keys=True)+"\n")
