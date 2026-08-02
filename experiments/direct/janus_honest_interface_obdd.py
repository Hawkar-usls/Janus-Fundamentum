#!/usr/bin/env python3
"""C022 honest semantic-interface compression: compact CI audit."""

from __future__ import annotations
import hashlib, itertools, json, random
from collections import Counter, deque

SEED = 9379992

def clause(xs):
    s=set(map(int,xs))
    if any(-x in s for x in s): return None
    return tuple(sorted(s,key=lambda x:(abs(x),x<0)))

def cnf(xs):
    return tuple(sorted({c for x in xs if (c:=clause(x)) is not None}))

def vars_(f): return sorted({abs(x) for c in f for x in c})

def sat(f,a):
    return all(any(a.get(abs(x),False)==(x>0) for x in c) for c in f)

def cof(f,v,b):
    t=v if b else -v; q=-t; out=[]
    for c in f:
        if t in c: continue
        out.append(tuple(x for x in c if x!=q))
    return cnf(out)

def brute(f):
    vs=vars_(f)
    for bits in itertools.product((False,True),repeat=len(vs)):
        a=dict(zip(vs,bits))
        if sat(f,a): return True,a
    return False,None

def horn(f): return all(sum(x>0 for x in c)<=1 for c in f)
def dual(f): return all(sum(x<0 for x in c)<=1 for c in f)

def horn_conflict(f):
    assert horn(f)
    rules=[]
    for c in f:
        p=[x for x in c if x>0]
        rules.append((frozenset(abs(x) for x in c if x<0),p[0] if p else None))
    true=set(); fired=[]; changed=True
    while changed:
        changed=False
        for i,(ant,cons) in enumerate(rules):
            if not ant<=true: continue
            if cons is None: return fired,i,tuple(sorted(true))
            if cons not in true:
                true.add(cons); fired.append(i); changed=True
    return None

def verify_horn(f,cert):
    if cert is None or not horn(f): return False
    fired,k,expect=cert; rules=[]
    for c in f:
        p=[x for x in c if x>0]
        rules.append((frozenset(abs(x) for x in c if x<0),p[0] if p else None))
    true=set()
    for i in fired:
        ant,cons=rules[i]
        if cons is None or not ant<=true: return False
        true.add(cons)
    ant,cons=rules[k]
    return cons is None and ant<=true and tuple(sorted(true))==expect

def conflict(f,lang):
    if lang=="H":
        c=horn_conflict(f)
        return c is not None and verify_horn(f,c)
    g=cnf(tuple(tuple(-x for x in c) for c in f))
    c=horn_conflict(g)
    return c is not None and verify_horn(g,c)

class Open(Exception): pass

class BDD:
    def __init__(self,order,budget):
        self.order=tuple(order); self.level={v:i for i,v in enumerate(order)}
        self.budget=budget; self.nodes={}; self.unique={}; self.next=2
    def mk(self,v,lo,hi):
        if lo==hi:return lo
        k=(v,lo,hi)
        if k in self.unique:return self.unique[k]
        if len(self.nodes)>=self.budget:raise Open
        i=self.next;self.next+=1;self.nodes[i]=k;self.unique[k]=i;return i
    def witness(self,r):
        if r==0:return None
        a={v:False for v in self.order}
        while r>1:
            v,lo,hi=self.nodes[r]
            if lo:a[v]=False;r=lo
            else:a[v]=True;r=hi
        return a if r==1 else None

def compile_(f,lang,order,budget):
    f=cnf(f); assert (horn(f) if lang=="H" else dual(f))
    assert set(vars_(f))<=set(order)
    b=BDD(order,budget); memo={}; work={"calls":0,"residuals":0,"certs":0}
    def rec(i,r):
        work["calls"]+=1;k=(i,r)
        if k in memo:return memo[k]
        work["residuals"]+=1
        if not r:memo[k]=1;return 1
        if () in r:memo[k]=0;return 0
        if conflict(r,lang):work["certs"]+=1;memo[k]=0;return 0
        if i==len(order):raise AssertionError
        v=order[i]
        if v not in vars_(r):z=rec(i+1,r)
        else:z=b.mk(v,rec(i+1,cof(r,v,False)),rec(i+1,cof(r,v,True)))
        memo[k]=z;return z
    try:return "EXACT",b,rec(0,f),work
    except Open:return "OPEN",None,None,work

def apply_and(a,ra,b,rb,budget):
    assert a.order==b.order
    out=BDD(a.order,budget); memo={}; calls=0
    def lev(d,u):return len(d.order)+1 if u<2 else d.level[d.nodes[u][0]]
    def split(d,u,v):
        if u<2:return u,u
        x,lo,hi=d.nodes[u]
        return (lo,hi) if x==v else (u,u)
    def rec(u,v):
        nonlocal calls;calls+=1
        if not u or not v:return 0
        if u==v==1:return 1
        k=(u,v)
        if k in memo:return memo[k]
        q=min(lev(a,u),lev(b,v)); x=a.order[q]
        u0,u1=split(a,u,x);v0,v1=split(b,v,x)
        z=out.mk(x,rec(u0,v0),rec(u1,v1));memo[k]=z;return z
    try:return "EXACT",out,rec(ra,rb),calls
    except Open:return "OPEN",None,None,calls

def graph(f):
    g={v:set() for v in vars_(f)}
    for c in f:
        vs=sorted({abs(x) for x in c})
        for i,a in enumerate(vs):
            for b in vs[i+1:]:g[a].add(b);g[b].add(a)
    return g

def orders(f):
    vs=vars_(f); occ=Counter(abs(x) for c in f for x in c); g=graph(f)
    bfs=[];un=set(vs)
    while un:
        q=deque([min(un)]);un.remove(q[0])
        while q:
            v=q.popleft();bfs.append(v)
            for w in sorted(g[v]):
                if w in un:un.remove(w);q.append(w)
    cand=[vs,sorted(vs,key=lambda v:(-occ[v],v)),bfs]
    out=[];seen=set()
    for x in cand:
        t=tuple(x)
        if t not in seen:seen.add(t);out.append(x)
    return out

def join(h,d,budget=5000):
    f=cnf(h+d); best=None; charged=0
    for o in orders(f):
        sh,bh,rh,wh=compile_(h,"H",o,budget)
        sd,bd,rd,wd=compile_(d,"D",o,budget)
        charged+=wh["calls"]+wd["calls"]
        if sh=="EXACT" and sd=="EXACT":
            sj,bj,rj,c=apply_and(bh,rh,bd,rd,budget);charged+=c
            if sj=="EXACT":
                w=bj.witness(rj)
                if w is not None:assert sat(f,w)
                score=len(bh.nodes)+len(bd.nodes)+len(bj.nodes)
                if best is None or score<best[0]:best=(score,rj!=0,w,o)
    return ("OPEN",None,None,charged) if best is None else ("EXACT",best[1],best[2],charged)

def equality(n):
    out=[]
    for i in range(1,n+1):
        out.extend([(-i,n+i),(i,-(n+i))])
    return cnf(out)

def project(f,sub):
    vs=vars_(f);rest=[v for v in vs if v not in sub];out=[]
    for bits in itertools.product((False,True),repeat=len(sub)):
        fixed=dict(zip(sub,bits))
        if any(sat(f,{**fixed,**dict(zip(rest,t))}) for t in itertools.product((False,True),repeat=len(rest))):
            out.append(bits)
    return tuple(out)

def local_collision():
    rows=[]
    for r in range(1,8):
        u=list(range(1,r+2));f=cnf([tuple(-v for v in u)]);t=cnf([])
        sf=[];st=[]
        for k in range(1,r+1):
            for s in itertools.combinations(u,k):sf.append(project(f,s));st.append(project(t,s))
        a={v:True for v in u}
        rows.append(sf==st and not sat(f,a) and sat(t,a))
    return all(rows)

def rand_clause(rng,vs,kind):
    w=rng.randint(1,min(4,len(vs)));q=rng.sample(vs,w)
    special=set(rng.sample(q,rng.choice((0,1))))
    return clause((v if v in special else -v) if kind=="H" else (-v if v in special else v) for v in q)

def rand3(rng,n,m):
    return cnf(clause(v if rng.random()<.5 else -v for v in rng.sample(range(1,n+1),3)) for _ in range(m))

def split3(f):
    return cnf(c for c in f if sum(x>0 for x in c)<=1),cnf(c for c in f if sum(x>0 for x in c)>1)

def main():
    assert local_collision()
    eqn=13;f=equality(eqn);blocked=list(range(1,eqn+1))+list(range(eqn+1,2*eqn+1));inter=[x for i in range(1,eqn+1) for x in (i,eqn+i)]
    sb,bb,rb,wb=compile_(f,"H",blocked,100000)
    si,bi,ri,wi=compile_(f,"H",inter,100000)
    assert sb==si=="EXACT" and len(bb.nodes)>len(bi.nodes)
    so,_,_,_=compile_(f,"H",blocked,1000); assert so=="OPEN"
    rng=random.Random(SEED); mism=0; cases=30
    for _ in range(cases):
        n=rng.randint(7,12);vs=list(range(1,n+1))
        h=cnf(rand_clause(rng,vs,"H") for _ in range(rng.randint(n,3*n)))
        d=cnf(rand_clause(rng,vs,"D") for _ in range(rng.randint(n,3*n)))
        status,ans,w,_=join(h,d)
        truth,_=brute(cnf(h+d))
        if status!="EXACT" or ans!=truth:mism+=1
    generic=20; gm=0
    for _ in range(generic):
        n=rng.randint(9,12);f=rand3(rng,n,rng.randint(3*n,5*n));h,d=split3(f)
        status,ans,w,_=join(h,d)
        truth,_=brute(f)
        if status!="EXACT" or ans!=truth:gm+=1
    result={"artifact_id":"C022-JANUS-HONEST-INTERFACE-OBDD-CI","status":"PASS" if mism==gm==0 else "FAIL","local_projection_collision":True,"equality":{"n":eqn,"blocked_nodes":len(bb.nodes),"interleaved_nodes":len(bi.nodes),"budget_open":so},"random_pairs":{"cases":cases,"mismatches":mism},"generic_3cnf":{"cases":generic,"mismatches":gm},"general_sat_oracle_called":False}
    print(json.dumps(result,indent=2))
    assert result["status"]=="PASS"

if __name__=="__main__":main()
