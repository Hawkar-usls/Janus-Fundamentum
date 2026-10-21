#!/usr/bin/env python3
"""BABEL19 exact Q cokernel of *ker(T) only*, seed16; never infer full SOS4 FAIL."""
import gzip,hashlib,json,math
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from crossbase_rank2 import setup,generate

class DSU:
    def __init__(self,n):
        self.par=list(range(n));self.w=[Fraction(1)]*n;self.zero=[False]*n
    def find(self,i):
        p=self.par[i]
        if p!=i:
            r,k=self.find(p);self.par[i]=r;self.w[i]*=k
        return self.par[i],self.w[i]
    def add(self,col):
        row=defaultdict(Fraction)
        for i,v in col:
            r,k=self.find(i)
            if not self.zero[r]:row[r]+=v*k
        row=[(r,v) for r,v in row.items() if v]
        assert len(row) in (1,2),("not exact independent pivot",len(row))
        if len(row)==1:self.zero[row[0][0]]=True
        else:
            (r,a),(s,b)=row
            self.par[r]=s;self.w[r]=-b/a
            self.zero[s]=self.zero[s] or self.zero[r]

def run():
    base="SCL126_flip68";seed=16
    src,lift,labels,base_Q,Q,kernel,fibers,coord,nactive,norbits=setup(seed,base)
    N=len(coord)
    path=Path("babel19_SCL126_flip68_seed16_p65521_modular_pivots.json.gz")
    with gzip.open(path,"rt") as f:proof=json.load(f)
    pivots=proof["pivots"]
    assert len(pivots)==N-1 and proof["base_name"]==base
    uf=DSU(N)
    for k,(r,su,rr,u) in enumerate(pivots):
        a=fibers[su][0];d=defaultdict(int)
        for q in (u,*(u^labels[j] for j in lift[rr])):d[q]+=1
        for q in (a,*(a^labels[j] for j in lift[r])):d[q]-=1
        uf.add([(coord[q],v) for q,v in d.items() if v and q in coord])
        if (k+1)%20000==0:print("EXACT_COKERNEL_PIVOTS",k+1,flush=True)
    survivors={uf.find(i)[0] for i in range(N) if not uf.zero[uf.find(i)[0]]}
    assert len(survivors)==1,("not 1D Q kernel",len(survivors))
    root=next(iter(survivors))
    h={}
    for i in range(N):
        r,w=uf.find(i)
        if r==root and w:h[i]=w
    den=math.lcm(*(v.denominator for v in h.values()))
    h={i:int(v*den) for i,v in h.items()}
    g=math.gcd(*h.values())
    h={i:v//g for i,v in h.items()}
    print("EXACT_COKERNEL_SUPPORT",len(h),"max_digits",max(len(str(abs(x))) for x in h.values()),flush=True)
    checked=0
    for r,su,rr,u,signature in generate(src,lift,labels,base_Q,fibers,coord):
        assert sum(h.get(i,0)*v for i,v in signature)==0,("Q witness violated",r,su,rr,u)
        checked+=1
        if checked%500000==0:print("EXACT_COKERNEL_GENERATORS",checked,flush=True)
    assert checked==2*len(src)*len(Q)-len(src)*len(base_Q)
    record={"format":"BABEL19_SEED16_EXACT_KERT_COKERNEL_V1","base":base,
            "seed":seed,"antisector_dimension":N,"rank_exact":len(pivots),
            "cokernel_dim_exact":1,"support":len(h),
            "all_generator_tests":checked,
            "proof_scope":"kerT only; source syzygies not tested; full SOS4 remains OPEN",
            "witness":[[i,str(v)] for i,v in sorted(h.items())]}
    out=Path("babel19_seed16_exact_kerT_cokernel.json.gz")
    with gzip.open(out,"wt",encoding="utf-8") as f:json.dump(record,f,sort_keys=True,separators=(",",":"))
    print("BABEL19_SEED16_EXACT_COKERNEL_PASS",json.dumps({
       "rank_exact":len(pivots),"dimension":N,"support":len(h),
       "checked":checked,"sha256":hashlib.sha256(out.read_bytes()).hexdigest()}),flush=True)

if __name__=="__main__":run()
