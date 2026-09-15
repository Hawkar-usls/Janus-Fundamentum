#!/usr/bin/env python3
"""C028 compact CI: decomposability, deterministic 3-CNF embedding, overlap defect."""

from __future__ import annotations
import hashlib, itertools, json, random
from dataclasses import dataclass

Clause=tuple[int,...];CNF=tuple[Clause,...]

def cc(xs):
    s=set(xs)
    if any(-x in s for x in s):return None
    return tuple(sorted(s,key=lambda x:(abs(x),x<0)))
def cf(cs):
    out=set()
    for c in cs:
        q=cc(c)
        if q is not None:out.add(q)
    return tuple(sorted(out,key=lambda c:(len(c),c)))
def satcnf(f,a):return all(any(a.get(abs(x),False)==(x>0) for x in c) for c in f)

@dataclass(frozen=True)
class N:
    k:str
    x:int=0
    ch:tuple["N",...]=()
T=N("C",1);F=N("C",0)
def L(x):return N("L",x)
def A(*z):
    q=[]
    for x in z:
        if x.k=="C":
            if not x.x:return F
        elif x.k=="A":q+=x.ch
        else:q.append(x)
    return T if not q else q[0] if len(q)==1 else N("A",0,tuple(q))
def O(*z):
    q=[]
    for x in z:
        if x.k=="C":
            if x.x:return T
        elif x.k=="O":q+=x.ch
        else:q.append(x)
    return F if not q else q[0] if len(q)==1 else N("O",0,tuple(q))
def ev(n,a):
    if n.k=="C":return bool(n.x)
    if n.k=="L":return a.get(abs(n.x),False)==(n.x>0)
    if n.k=="A":return all(ev(c,a) for c in n.ch)
    return any(ev(c,a) for c in n.ch)
def sup(n,m=None):
    m={} if m is None else m
    if n in m:return m[n]
    if n.k=="C":r=frozenset()
    elif n.k=="L":r=frozenset({abs(n.x)})
    else:r=frozenset().union(*(sup(c,m) for c in n.ch))
    m[n]=r;return r
def decomp(n):
    m={}
    if n.k=="A":
        seen=set()
        for c in n.ch:
            s=set(sup(c,m))
            if seen&s:return False
            seen|=s
    return all(decomp(c) for c in n.ch)
def overlap(n):
    m={};D=set()
    def rec(q):
        if q.k=="A":
            seen=set()
            for c in q.ch:
                s=set(sup(c,m));D.update(seen&s);seen|=s
        for c in q.ch:rec(c)
    rec(n);return sorted(D)
def simp(n,a):
    if n.k=="C":return n
    if n.k=="L":return n if abs(n.x) not in a else (T if a[abs(n.x)]==(n.x>0) else F)
    z=[simp(c,a) for c in n.ch]
    return A(*z) if n.k=="A" else O(*z)
def dsolve(n):
    if not decomp(n):return "OPEN",None
    def rec(q):
        if q.k=="C":return bool(q.x),{}
        if q.k=="L":return True,{abs(q.x):q.x>0}
        if q.k=="O":
            for c in q.ch:
                ok,w=rec(c)
                if ok:return True,w
            return False,None
        w={}
        for c in q.ch:
            ok,u=rec(c)
            if not ok:return False,None
            for v,b in u.items():
                if v in w:raise AssertionError("overlap")
                w[v]=b
        return True,w
    ok,w=rec(n)
    if ok and not ev(n,w):raise AssertionError("bad witness")
    return "EXACT",(ok,w)
def defectsolve(n,budget):
    D=overlap(n)
    if 1<<len(D)>budget:return "OPEN",None,len(D),0
    seen=0
    for bits in itertools.product((False,True),repeat=len(D)):
        seen+=1;a=dict(zip(D,bits));r=simp(n,a)
        if not decomp(r):raise AssertionError("conditioning failed")
        st,z=dsolve(r)
        if st!="EXACT":raise AssertionError("residual open")
        ok,w=z
        if ok:
            w={**a,**w}
            if not ev(n,w):raise AssertionError("defect witness")
            return "EXACT",(True,w),len(D),seen
    return "EXACT",(False,None),len(D),seen

def detcl(c):
    a,b,d=map(L,c)
    return O(a,A(L(-a.x),b),A(L(-a.x),L(-b.x),d))
def dcircuit(f):return A(*(detcl(c) for c in f))
def direct(f):return A(*(O(*(L(x) for x in c)) for c in f))
def altern(n,prev=None):
    cur=n.k if n.k in ("A","O") else prev
    add=int(prev is not None and n.k in ("A","O") and n.k!=prev)
    return add+(max((altern(c,cur) for c in n.ch),default=0))
def deterministic(n):
    for q in ors(n):
        V=sorted(sup(q))
        for bits in itertools.product((False,True),repeat=len(V)):
            a=dict(zip(V,bits))
            if sum(ev(c,a) for c in q.ch)>1:return False
    return True
def ors(n):
    z=[n] if n.k=="O" else []
    for c in n.ch:z+=ors(c)
    return z
def brute(n):
    V=sorted(sup(n))
    for bits in itertools.product((False,True),repeat=len(V)):
        a=dict(zip(V,bits))
        if ev(n,a):return True,a
    return False,None
def planted(r,n,m):
    a={i:bool(r.getrandbits(1)) for i in range(1,n+1)};cs=[]
    for _ in range(m):
        S=r.sample(range(1,n+1),3);c=[x if r.random()<.5 else -x for x in S]
        if not any(a[abs(x)]==(x>0) for x in c):c[0]=S[0] if a[S[0]] else -S[0]
        cs.append(tuple(c))
    return cf(cs)
def core():
    return cf(tuple(-i if b[i-1] else i for i in range(1,4))
              for b in itertools.product((0,1),repeat=3))
def randd(r,V,d):
    if d==0 or len(V)==1:
        x=r.choice(V);return L(x if r.random()<.5 else -x)
    if r.random()<.5:
        W=list(V);r.shuffle(W);k=r.randint(1,len(W)-1)
        return A(randd(r,tuple(W[:k]),d-1),randd(r,tuple(W[k:]),d-1))
    return O(randd(r,V,d-1),randd(r,V,d-1))
def large(d,blocks=20):
    z=[];v=d+1
    for s in range(1,d+1):
        for _ in range(blocks):
            factors=[L(s)]
            for _ in range(3):
                factors.append(O(L(v),L(-v)));v+=1
            z.append(A(*factors))
    return A(*z),v-1

def run(seed=280028):
    r=random.Random(seed);dm=dw=0;nondet=0
    for _ in range(120):
        n=r.randint(1,8);c=randd(r,tuple(range(1,n+1)),r.randint(1,4))
        if not decomp(c):raise AssertionError()
        st,z=dsolve(c);t,_=brute(c)
        if st!="EXACT" or z[0]!=t:dm+=1
        if not deterministic(c):nondet+=1
        if z[0] and not ev(c,z[1]):dw+=1
    ef=df=tf=sf=0;sat=unsat=0;C=core()
    for i in range(80):
        n=r.randint(3,8);f=planted(r,n,r.randint(n,4*n)) if i%2==0 else cf(C+planted(r,n,max(1,n))[0:0])
        if i%2: f=C
        c=dcircuit(f)
        for bits in itertools.product((False,True),repeat=n):
            a=dict(zip(range(1,n+1),bits))
            if ev(c,a)!=satcnf(f,a):ef+=1;break
        if not deterministic(c):df+=1
        if altern(c)>2:tf+=1
        if dsolve(c)[0]!="OPEN":sf+=1
        t=any(satcnf(f,dict(zip(range(1,n+1),b))) for b in itertools.product((False,True),repeat=n))
        sat+=t;unsat+=not t
    xm=xw=xo=0
    for i in range(100):
        n=r.randint(3,8);f=planted(r,n,r.randint(n,4*n)) if i%2==0 else C
        c=direct(f);st,z,d,k=defectsolve(c,1<<n)
        t=any(satcnf(f,dict(zip(range(1,n+1),b))) for b in itertools.product((False,True),repeat=n))
        if st=="OPEN":xo+=1
        elif z[0]!=t:xm+=1
        elif z[0] and not ev(c,z[1]):xw+=1
    scale=[]
    for d in (2,4,6,8):
        c,n=large(d,30);st,z,q,k=defectsolve(c,1<<d)
        scale.append((d,n,st,z[0],q,k))
    A0={"dnnf":dm==dw==0 and nondet>0,
        "embedding":ef==df==tf==sf==0 and sat==unsat==40,
        "defect":xm==xw==xo==0,
        "scale":all(st=="EXACT" and ok and q==d for d,n,st,ok,q,k in scale)}
    out={"artifact":"C028-JANUS-MIXED-CONE-INVARIANTS",
         "status":"PASS" if all(A0.values()) else "FAIL","seed":seed,
         "dnnf":{"mismatches":dm,"witness_failures":dw,"nondeterministic_tractable":nondet},
         "embedding":{"sat":sat,"unsat":unsat,"equivalence_failures":ef,
                      "determinism_failures":df,"alternation_failures":tf,"false_admissions":sf},
         "defect":{"mismatches":xm,"witness_failures":xw,"open":xo},
         "scale":[{"d":d,"variables":n,"status":st,"sat":ok,"detected_d":q,"branches":k}
                  for d,n,st,ok,q,k in scale],
         "assertions":A0,"bottleneck":"SEMANTIC_SUPPORT_OVERLAP",
         "general_sat_oracle_called":False}
    out["integrity"]=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    return out
if __name__=="__main__":
    x=run();print(json.dumps(x,indent=2))
    if x["status"]!="PASS":raise SystemExit(1)
