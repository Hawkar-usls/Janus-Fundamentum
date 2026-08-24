#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OdontoForge P≟NP EXP — exact SAT transient-state laboratory.

Odonto anatomy:
  pulp    = immutable SAT instance fingerprint
  tubule  = exact-search branch
  dentin  = partial assignment
  enamel  = independently verified SAT certificate
  vitality= branch consistency
  growth  = decision + unit propagation
  exit    = SAT certificate / conflict / exact closure / UNKNOWN_BUDGET

Scientific boundary:
  This program does NOT prove P=NP or P!=NP.
  Finite benchmarks measure tested instances only.
  SAT requires independent assignment verification.
  UNSAT is returned only after exact frontier exhaustion.
  Budget exhaustion returns UNKNOWN_BUDGET, never UNSAT.
"""

from __future__ import annotations
import argparse, hashlib, heapq, json, math, random, statistics, time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

VERSION = "0.1.0-odontoforge-pnp-exp"
Clause = Tuple[int, ...]

def canonical(x): return json.dumps(x, sort_keys=True, separators=(",", ":"))
def sha(x): return hashlib.sha256(canonical(x).encode()).hexdigest()

@dataclass(frozen=True)
class SAT:
    n: int
    clauses: Tuple[Clause, ...]
    name: str = "instance"
    source: str = "manual"
    @property
    def fingerprint(self):
        return sha({"n": self.n, "clauses": self.clauses, "name": self.name, "source": self.source})
    @property
    def pulp(self):
        return int(self.fingerprint[:2], 16)

def parse_dimacs(path: Path) -> SAT:
    n = 0; clauses=[]; cur=[]
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        s=raw.strip()
        if not s or s.startswith("c"): continue
        if s.startswith("p"):
            p=s.split()
            if len(p)<4 or p[1].lower()!="cnf": raise ValueError("expected: p cnf V C")
            n=int(p[2]); continue
        for tok in s.split():
            lit=int(tok)
            if lit==0: clauses.append(tuple(cur)); cur=[]
            else: cur.append(lit)
    if cur: raise ValueError("unterminated DIMACS clause")
    if n==0: n=max((abs(l) for c in clauses for l in c), default=0)
    return SAT(n, tuple(clauses), path.stem, str(path))

def generate_3sat(n:int, m:int, seed:int, planted:bool=False) -> SAT:
    if n < 3: raise ValueError("n >= 3 required")
    r=random.Random(seed); target=r.getrandbits(n) if planted else None; cs=[]
    while len(cs)<m:
        vs=r.sample(range(1,n+1),3)
        c=[v if r.random()<.5 else -v for v in vs]
        if target is not None:
            def ok(l):
                b=bool((target>>(abs(l)-1))&1)
                return b if l>0 else not b
            if not any(ok(l) for l in c): c[r.randrange(3)] *= -1
        cs.append(tuple(c))
    return SAT(n, tuple(cs), f"3sat_n{n}_m{m}_s{seed}", f"synthetic:{seed}:{planted}")

def verify(inst: SAT, bits:int) -> bool:
    if bits < 0 or bits >= (1<<inst.n): return False
    for c in inst.clauses:
        sat=False
        for lit in c:
            b=bool((bits>>(abs(lit)-1))&1)
            if (b if lit>0 else not b): sat=True; break
        if not sat: return False
    return True

@dataclass
class Tubule:
    pulp:int
    dentin:int=0
    mask:int=0
    vitality:int=100
    depth:int=0
    path:str=""
    def clone(self): return Tubule(self.pulp,self.dentin,self.mask,self.vitality,self.depth,self.path)
    def assigned(self,v): return bool(self.mask & (1<<(v-1)))
    def value(self,v): return bool(self.dentin & (1<<(v-1)))
    def grow(self,v,enamel):
        bit=1<<(v-1)
        if self.mask & bit:
            if self.value(v)!=bool(enamel): self.vitality=0
            return
        self.mask |= bit
        if enamel: self.dentin |= bit
        else: self.dentin &= ~bit
        self.depth=self.mask.bit_count()
        self.path += f"{v}{'T' if enamel else 'F'};"

def evaluate(inst:SAT,t:Tubule):
    satisfied=0; unresolved=0; units=[]; activity={}
    for c in inst.clauses:
        true=False; un=[]
        for lit in c:
            v=abs(lit)
            if t.assigned(v):
                val=t.value(v)
                if val if lit>0 else not val:
                    true=True; break
            else:
                un.append(lit); activity[v]=activity.get(v,0)+1
        if true: satisfied += 1; continue
        if not un: return True,satisfied,0,[],activity
        unresolved += 1
        if len(un)==1: units.append(un[0])
    return False,satisfied,unresolved,units,activity

def propagate(inst:SAT,t:Tubule):
    p=0
    while True:
        conflict,sat,unres,units,activity=evaluate(inst,t)
        if conflict: t.vitality=0; return False,(sat,unres,activity),p
        if not units: return True,(sat,unres,activity),p
        progress=False
        for lit in units:
            v=abs(lit); req=1 if lit>0 else 0
            if t.assigned(v):
                if t.value(v)!=bool(req): t.vitality=0; return False,(sat,unres,activity),p
            else:
                t.grow(v,req); p+=1; progress=True
        if not progress: return True,(sat,unres,activity),p

class BioRegulator:
    def __init__(self,seed=0):
        self.r=random.Random(seed); self.entropy=.10; self.stagnation=0; self.best=-10**9
    def choose(self,inst,t,activity):
        xs=[v for v in range(1,inst.n+1) if not t.assigned(v)]
        if not xs: return 0
        return max(xs,key=lambda v:(activity.get(v,0)+self.r.random()*self.entropy,-v))
    def order(self):
        return (1,0) if self.r.random()<self.entropy else (0,1)
    def adapt(self,score):
        if score>self.best:
            self.best=score; self.stagnation=0; self.entropy=max(.01,self.entropy-.02); return "CRYSTALLIZE"
        self.stagnation+=1
        if self.stagnation>5:
            self.stagnation=0; self.entropy=min(.5,self.entropy+.05); return "INJECT_CHAOS"
        return "STABLE"

@dataclass
class Result:
    status:str
    solver:str
    fingerprint:str
    n:int
    m:int
    nodes:int
    conflicts:int
    propagations:int
    elapsed_s:float
    assignment:Optional[int]=None
    certificate_verified:bool=False
    budget:Optional[int]=None
    best_score:int=-10**9

def brute(inst:SAT,budget:Optional[int]=None) -> Result:
    t0=time.perf_counter(); nodes=0
    for a in range(1<<inst.n):
        if budget is not None and nodes>=budget:
            return Result("UNKNOWN_BUDGET","brute_2^n",inst.fingerprint,inst.n,len(inst.clauses),nodes,nodes,0,time.perf_counter()-t0,budget=budget)
        nodes+=1
        if verify(inst,a):
            return Result("SAT","brute_2^n",inst.fingerprint,inst.n,len(inst.clauses),nodes,nodes-1,0,time.perf_counter()-t0,a,True,budget)
    return Result("UNSAT","brute_2^n",inst.fingerprint,inst.n,len(inst.clauses),nodes,nodes,0,time.perf_counter()-t0,budget=budget)

def odonto(inst:SAT,seed=0,budget:Optional[int]=None) -> Result:
    t0=time.perf_counter(); reg=BioRegulator(seed); serial=0
    q=[(0,0,serial,Tubule(inst.pulp))]; seen=set()
    nodes=conflicts=props=0; best=-10**9
    while q:
        if budget is not None and nodes>=budget:
            return Result("UNKNOWN_BUDGET","odontoforge_exact",inst.fingerprint,inst.n,len(inst.clauses),nodes,conflicts,props,time.perf_counter()-t0,budget=budget,best_score=best)
        _,_,_,t=heapq.heappop(q)
        key=(t.mask,t.dentin&t.mask)
        if key in seen: continue
        seen.add(key); nodes+=1
        alive,(sat,unres,activity),p=propagate(inst,t); props+=p
        if not alive:
            conflicts+=1; continue
        score=sat*4-unres; best=max(best,score); reg.adapt(score)
        if unres==0:
            a=t.dentin & ((1<<inst.n)-1)
            if not verify(inst,a): raise AssertionError("enamel verifier rejected SAT")
            return Result("SAT","odontoforge_exact",inst.fingerprint,inst.n,len(inst.clauses),nodes,conflicts,props,time.perf_counter()-t0,a,True,budget,best)
        v=reg.choose(inst,t,activity)
        if v==0: conflicts+=1; continue
        for enamel in reg.order():
            c=t.clone(); c.grow(v,enamel)
            cc,ss,uu,_,_=evaluate(inst,c)
            pri=-float(ss*4-uu) if not cc else 1e9
            serial+=1; heapq.heappush(q,(pri,-c.depth,serial,c))
    return Result("UNSAT","odontoforge_exact",inst.fingerprint,inst.n,len(inst.clauses),nodes,conflicts,props,time.perf_counter()-t0,best_score=best)

def fit_slope(points:Sequence[Tuple[int,float]]):
    if len(points)<2: return {"slope":None,"r2":None}
    xs=[float(n) for n,_ in points]; ys=[math.log2(max(1,x)+1) for _,x in points]
    xm=statistics.mean(xs); ym=statistics.mean(ys); sxx=sum((x-xm)**2 for x in xs)
    b=sum((x-xm)*(y-ym) for x,y in zip(xs,ys))/sxx; a=ym-b*xm
    ssr=sum((y-(a+b*x))**2 for x,y in zip(xs,ys)); sst=sum((y-ym)**2 for y in ys)
    return {"slope":b,"intercept":a,"r2":1-ssr/sst if sst else 1.0}

def sweep(lo,hi,step,trials,ratio,seed,brute_max,out:Path):
    r=random.Random(seed); rows=[]; op=[]; bp=[]
    out.mkdir(parents=True,exist_ok=True)
    for n in range(lo,hi+1,step):
        on=[]; bn=[]
        for tr in range(trials):
            s=r.randrange(1<<31); inst=generate_3sat(n,round(ratio*n),s)
            o=odonto(inst,s); on.append(o.nodes)
            b=brute(inst) if n<=brute_max else None
            if b and b.status!=o.status: raise AssertionError("solver disagreement")
            if b: bn.append(b.nodes)
            rows.append({"n":n,"trial":tr,"seed":s,"status":o.status,"odonto_nodes":o.nodes,
                         "brute_nodes":b.nodes if b else None,"ratio_vs_2n":o.nodes/float(1<<n)})
        op.append((n,statistics.median(on)))
        if bn: bp.append((n,statistics.median(bn)))
    report={"version":VERSION,"P_VS_NP":"OPEN","rows":rows,
            "growth":{"odontoforge":fit_slope(op),"brute":fit_slope(bp)},
            "boundary":{"finite_benchmark_is_not_proof":True,"sub1_slope_is_not_polynomial_proof":True}}
    (out/"sweep_report.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report["growth"],indent=2))

def selftest():
    sat=SAT(2,((1,),(2,-1)),"sat","selftest")
    uns=SAT(1,((1,),(-1,)),"unsat","selftest")
    for inst,expect in [(sat,"SAT"),(uns,"UNSAT")]:
        a=odonto(inst,123); b=brute(inst)
        assert a.status==b.status==expect
        if expect=="SAT": assert a.assignment is not None and verify(inst,a.assignment)
    r=random.Random(20260825)
    for n in range(3,9):
        for _ in range(8):
            s=r.randrange(1<<30); inst=generate_3sat(n,round(4.2*n),s)
            a=odonto(inst,s); b=brute(inst)
            assert a.status==b.status
            if a.status=="SAT": assert verify(inst,a.assignment or 0)
    limited=odonto(generate_3sat(10,43,99),99,budget=1)
    assert limited.status in {"SAT","UNKNOWN_BUDGET"}
    print("PASS: OdontoForge P≟NP EXP selftest")

def main():
    p=argparse.ArgumentParser()
    sub=p.add_subparsers(dest="cmd",required=True)
    sub.add_parser("selftest")
    d=sub.add_parser("demo"); d.add_argument("--vars",type=int,default=18); d.add_argument("--clauses",type=int,default=76); d.add_argument("--seed",type=int,default=42); d.add_argument("--budget",type=int)
    s=sub.add_parser("solve"); s.add_argument("--dimacs",type=Path,required=True); s.add_argument("--seed",type=int,default=0); s.add_argument("--budget",type=int)
    w=sub.add_parser("sweep"); w.add_argument("--min-vars",type=int,default=8); w.add_argument("--max-vars",type=int,default=18); w.add_argument("--step",type=int,default=2); w.add_argument("--trials",type=int,default=5); w.add_argument("--ratio",type=float,default=4.26); w.add_argument("--seed",type=int,default=20260825); w.add_argument("--brute-max-vars",type=int,default=18); w.add_argument("--out",type=Path,default=Path("odontoforge_pnp_runs"))
    a=p.parse_args()
    if a.cmd=="selftest": selftest()
    elif a.cmd=="demo":
        inst=generate_3sat(a.vars,a.clauses,a.seed); print(json.dumps(asdict(odonto(inst,a.seed,a.budget)),indent=2))
    elif a.cmd=="solve":
        inst=parse_dimacs(a.dimacs); print(json.dumps(asdict(odonto(inst,a.seed,a.budget)),indent=2))
    else: sweep(a.min_vars,a.max_vars,a.step,a.trials,a.ratio,a.seed,a.brute_max_vars,a.out)

if __name__=="__main__": main()
