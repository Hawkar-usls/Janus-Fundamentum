#!/usr/bin/env python3
"""C026 compact CI audit: proof-carrying residual merge certificate portfolio."""

from __future__ import annotations
import collections, hashlib, itertools, json, math
from dataclasses import dataclass

Clause = tuple[int, ...]
CNF = tuple[Clause, ...]
Equation = tuple[int, int]

def cc(xs):
    s=set(xs)
    if any(-x in s for x in s): return None
    return tuple(sorted(s,key=lambda x:(abs(x),x<0)))

def cf(cs):
    out=set()
    for c in cs:
        q=cc(c)
        if q is not None: out.add(q)
    return tuple(sorted(out,key=lambda c:(len(c),c)))

def vs(f): return sorted({abs(x) for c in f for x in c})
def sat(f,a): return all(any(a.get(abs(x),False)==(x>0) for x in c) for c in f)
def h(f): return hashlib.sha256(json.dumps(f,separators=(",",":")).encode()).hexdigest()

def subsume(f):
    keep=[]
    for c in sorted(cf(f),key=lambda c:(len(c),c)):
        if not any(set(d)<=set(c) for d in keep): keep.append(c)
    return cf(keep)

# ------------------------------ 2-SAT ---------------------------------

def graph(f):
    if any(len(c)>2 for c in f): raise ValueError("not 2-CNF")
    g={x:set() for v in vs(f) for x in (v,-v)}
    for c in f:
        if not c: continue
        if len(c)==1: g[-c[0]].add(c[0])
        else:
            a,b=c; g[-a].add(b); g[-b].add(a)
    return g

def path(g,s,t):
    q=collections.deque([s]); p={s:None}
    while q:
        x=q.popleft()
        if x==t: break
        for y in sorted(g.get(x,())):
            if y not in p: p[y]=x; q.append(y)
    if t not in p:return None
    z=[]; x=t
    while x is not None:z.append(x);x=p[x]
    return tuple(reversed(z))

def path_ok(g,p):
    return bool(p) and all(b in g.get(a,set()) for a,b in zip(p,p[1:]))

def closure2(f):
    f=cf(f)
    if () in f:return ((),),{"unsat":True,"paths":[]}
    g=graph(f); V=vs(f)
    for v in V:
        p=path(g,v,-v);q=path(g,-v,v)
        if p and q:return ((),),{"unsat":True,"paths":[p,q]}
    out=[]; cert={}
    L=[x for v in V for x in (v,-v)]
    for a in L:
        p=path(g,-a,a)
        if p: out.append((a,));cert[(a,)]=(p,)
    for i,a in enumerate(L):
        for b in L[i+1:]:
            if abs(a)==abs(b):continue
            c=cc((a,b))
            if c is None:continue
            p=path(g,-a,b);q=path(g,-b,a)
            if p and q:out.append(c);cert[c]=(p,q)
    return cf(out),{"unsat":False,"paths":cert}

def verify2(f,out,cert):
    f=cf(f);out=cf(out)
    if () in f:return cert["unsat"] and out==((),)
    g=graph(f)
    if cert["unsat"]:
        return out==((),) and len(cert["paths"])==2 and all(path_ok(g,p) for p in cert["paths"])
    if not all(c in out for c in f):return False
    for c in out:
        ps=cert["paths"].get(c)
        if not ps:return False
        if len(c)==1:
            if len(ps)!=1 or ps[0][0]!=-c[0] or ps[0][-1]!=c[0] or not path_ok(g,ps[0]):return False
        else:
            a,b=c
            if {(p[0],p[-1]) for p in ps}!={(-a,b),(-b,a)} or not all(path_ok(g,p) for p in ps):return False
    return True

# ------------------------------- GF2 ----------------------------------

def rref(rows,n):
    a=[list(x) for x in sorted(set(rows))];ops=[];r=0
    for col in range(n):
        p=next((i for i in range(r,len(a)) if a[i][0]>>col&1),None)
        if p is None:continue
        if p!=r:a[p],a[r]=a[r],a[p];ops.append(("S",p,r))
        for i in range(len(a)):
            if i!=r and a[i][0]>>col&1:
                a[i][0]^=a[r][0];a[i][1]^=a[r][1];ops.append(("X",i,r))
        r+=1
    out=((0,1),) if any(m==0 and b for m,b in a) else tuple(sorted({(m,b) for m,b in a if m}))
    return out,(tuple(sorted(set(rows))),tuple(ops))

def verify_rref(out,cert):
    rows=[list(x) for x in cert[0]]
    for op,i,j in cert[1]:
        if op=="S":rows[i],rows[j]=rows[j],rows[i]
        elif op=="X":rows[i][0]^=rows[j][0];rows[i][1]^=rows[j][1]
        else:return False
    exp=((0,1),) if any(m==0 and b for m,b in rows) else tuple(sorted({(m,b) for m,b in rows if m}))
    return exp==out

# ----------------------- bounded Resolution ---------------------------

def res(a,b,p):
    if p not in a or -p not in b:return None
    return cc([x for x in a if x!=p]+[x for x in b if x!=-p])

def wclosure(f,w):
    known=set(cf(f));proof=[];changed=True
    while changed:
        changed=False;s=sorted(known,key=lambda c:(len(c),c))
        for i,a in enumerate(s):
            for b in s[i+1:]:
                for p in sorted({abs(x) for x in a if -x in b}|{abs(x) for x in b if -x in a}):
                    x,y=(a,b) if p in a else (b,a);c=res(x,y,p)
                    if c is not None and len(c)<=w and c not in known:
                        known.add(c);proof.append((x,y,p,c));changed=True
    keep=[];delete=[]
    for c in sorted(known,key=lambda c:(len(c),c)):
        d=next((d for d in keep if set(d)<=set(c)),None)
        if d is None:keep.append(c)
        else:delete.append((c,d))
    return cf(keep),(tuple(proof),tuple(delete))

def verify_w(f,out,w,cert):
    known=set(cf(f))
    for a,b,p,c in cert[0]:
        if a not in known or b not in known or len(c)>w or res(a,b,p)!=c:return False
        known.add(c)
    removed=set()
    for c,d in cert[1]:
        if c not in known or d not in known or not set(d)<=set(c):return False
        removed.add(c)
    return cf(x for x in known if x not in removed)==out

# ------------------------------- RUP ----------------------------------

def up(f,ass):
    A={}
    for x in ass:
        v=abs(x);b=x>0
        if v in A and A[v]!=b:return True,(),()
        A[v]=b
    steps=[];change=True
    while change:
        change=False
        for c in f:
            if any(abs(x) in A and A[abs(x)]==(x>0) for x in c):continue
            u=[x for x in c if abs(x) not in A]
            if not u:return True,tuple(steps),c
            if len(u)==1:
                x=u[0];v=abs(x);b=x>0
                if v in A:
                    if A[v]!=b:return True,tuple(steps),c
                else:A[v]=b;steps.append((x,c));change=True
    return False,tuple(steps),None

def rup(f,learn):
    work=cf(f);steps=[]
    for c in learn:
        c=cc(c)
        if c in work:continue
        bad,trail,conf=up(work,[-x for x in c])
        if not bad:raise AssertionError("not RUP")
        steps.append((c,trail,conf));work=cf(work+(c,))
    return subsume(work),tuple(steps)

def verify_rup(f,out,steps):
    work=cf(f)
    for c,trail,conf in steps:
        bad,t,k=up(work,[-x for x in c])
        if not bad or t!=trail or k!=conf:return False
        work=cf(work+(c,))
    return subsume(work)==out

# ------------------------------ families ------------------------------

def family2(m=8):
    n=m+2;base=[(-i,i+1) for i in range(1,n)];opt=[]
    for d in range(2,n):
        for i in range(1,n-d+1):
            opt.append((-i,i+d))
            if len(opt)==m:return cf(base),tuple(opt)

def familyg(m=8):
    n=m+3;base=[]
    for i in range(n-1):base.append(((1<<i)|(1<<(i+1)),i&1))
    opt=[]
    for i in range(m):
        a=base[i%len(base)];b=base[(i+2)%len(base)]
        opt.append((a[0]^b[0],a[1]^b[1]))
    return tuple(base),tuple(opt),n

def familyw(m=8):
    base=[];opt=[];v=1
    for _ in range(m):
        p,a,b,c=v,v+1,v+2,v+3;v+=4
        base+= [(p,a,b),(-p,c)];opt.append((a,b,c))
    return cf(base),tuple(opt)

def familyrup(m=8):
    base=[];learn=[];v=1
    for _ in range(m):
        broad=tuple(range(v,v+4));q=v+4;v+=5
        base.append(broad);base += [(-x,q) for x in broad];learn.append((q,))
    return cf(base),tuple(learn)

def equality(n=12):
    return cf([c for i in range(1,n+1) for c in ((-i,n+i),(i,-(n+i)))])

def restrict(f,fixed):
    for v,b in fixed.items():
        t=v if b else -v;z=-t;out=[]
        for c in f:
            if t in c:continue
            out.append(tuple(x for x in c if x!=z))
        f=cf(out)
    return f

def run():
    m=8
    b,o=family2(m); raw=set();sub=set();cl=set()
    for mask in range(1<<m):
        f=cf(b+tuple(o[i] for i in range(m) if mask>>i&1))
        raw.add(f);sub.add(subsume(f));x,c=closure2(f);assert verify2(f,x,c);cl.add(x)
    two={"raw":len(raw),"subsumption":len(sub),"closure":len(cl)}

    b,o,n=familyg(m);raw=set();rr=set()
    for mask in range(1<<m):
        f=tuple(sorted(set(b+tuple(o[i] for i in range(m) if mask>>i&1))))
        raw.add(f);x,c=rref(f,n);assert verify_rref(x,c);rr.add(x)
    gf={"raw":len(raw),"rref":len(rr)}

    b,o=familyw(m);raw=set();w2=set();w3=set()
    for mask in range(1<<m):
        f=cf(b+tuple(o[i] for i in range(m) if mask>>i&1));raw.add(f)
        x,c=wclosure(f,2);assert verify_w(f,x,2,c);w2.add(x)
        x,c=wclosure(f,3);assert verify_w(f,x,3,c);w3.add(x)
    wr={"raw":len(raw),"width2":len(w2),"width3":len(w3)}

    b,o=familyrup(m);raw=set();w3=set();rt=set()
    for mask in range(1<<m):
        f=cf(b+tuple(o[i] for i in range(m) if mask>>i&1));raw.add(f)
        x,c=wclosure(f,3);assert verify_w(f,x,3,c);w3.add(x)
        x,c=rup(f,o);assert verify_rup(f,x,c);rt.add(x)
    rp={"raw":len(raw),"width3":len(w3),"rup":len(rt),"candidates":str(3**40-1)}

    eq=equality();states=set()
    for bits in itertools.product((False,True),repeat=12):
        f=restrict(eq,dict(zip(range(1,13),bits)));x,c=closure2(f);assert verify2(f,x,c);states.add(x)
    out={"status":"PASS","two_sat":two,"gf2":gf,"resolution":wr,"rup":rp,
         "equality_states":len(states),"assertions":{
         "two":two=={"raw":256,"subsumption":256,"closure":1},
         "gf":gf=={"raw":256,"rref":1},
         "width":wr=={"raw":256,"width2":256,"width3":1},
         "rup":rp["raw"]==256 and rp["width3"]==256 and rp["rup"]==1,
         "equality":len(states)==4096}}
    out["status"]="PASS" if all(out["assertions"].values()) else "FAIL"
    out["integrity"]=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    return out

if __name__=="__main__":
    r=run();print(json.dumps(r,indent=2))
    if r["status"]!="PASS":raise SystemExit(1)
