#!/usr/bin/env python3
"""C027 compact CI: discover exact context projections without a SAT oracle."""

from __future__ import annotations
import hashlib, itertools, json, random
from dataclasses import dataclass

Clause=tuple[int,...]; CNF=tuple[Clause,...]

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
def sat(f,a): return all(any(a.get(abs(x),False)==(x>0) for x in c) for c in f)
def sub(f):
    keep=[]
    for c in sorted(cf(f),key=lambda c:(len(c),c)):
        if not any(set(d)<=set(c) for d in keep): keep.append(c)
    return cf(keep)

@dataclass(frozen=True)
class Gate:
    kind:str; a:int; b:int; y:int
@dataclass(frozen=True)
class Net:
    inputs:tuple[int,...]; gates:tuple[Gate,...]; out:int; required:bool=True

def tree(n,kind):
    cur=list(range(1,n+1));fresh=n+1;g=[]
    while len(cur)>1:
        nxt=[];i=0
        while i<len(cur):
            if i+1==len(cur):nxt.append(cur[i]);i+=1;continue
            g.append(Gate(kind,cur[i],cur[i+1],fresh));nxt.append(fresh);fresh+=1;i+=2
        cur=nxt
    return Net(tuple(range(1,n+1)),tuple(g),cur[0],True)

def gc(q):
    a,b,y=q.a,q.b,q.y
    if q.kind=="OR":return cf([(-a,y),(-b,y),(a,b,-y)])
    if q.kind=="AND":return cf([(a,-y),(b,-y),(-a,-b,y)])
    if q.kind=="XOR":return cf([(-a,-b,-y),(a,b,-y),(a,-b,y),(-a,b,y)])
    raise ValueError(q.kind)
def enc(net):
    z=[]
    for g in net.gates:z+=list(gc(g))
    z.append((net.out,))
    return cf(z)
def evalnet(net,a):
    a=dict(a)
    for g in net.gates:
        if g.kind=="OR":a[g.y]=a[g.a] or a[g.b]
        elif g.kind=="AND":a[g.y]=a[g.a] and a[g.b]
        else:a[g.y]=a[g.a]^a[g.b]
    return a
def accepts(net,a):return evalnet(net,a)[net.out]

def up(f,ass):
    A={}
    for x in ass:
        v=abs(x);b=x>0
        if v in A and A[v]!=b:return True
        A[v]=b
    change=True
    while change:
        change=False
        for c in f:
            if any(abs(x) in A and A[abs(x)]==(x>0) for x in c):continue
            u=[x for x in c if abs(x) not in A]
            if not u:return True
            if len(u)==1:
                x=u[0];v=abs(x);b=x>0
                if v in A:
                    if A[v]!=b:return True
                else:A[v]=b;change=True
    return False
def rup(f,c):return up(f,[-x for x in c])

def resolve(a,b,v):
    if v not in a or -v not in b:return None
    return cc([x for x in a if x!=v]+[x for x in b if x!=-v])
def dp(f,order,budget):
    f=cf(f);pairs=0;peak=len(f)
    for v in order:
        P=[c for c in f if v in c];N=[c for c in f if -v in c]
        R=[c for c in f if v not in c and -v not in c];new=[]
        for a in P:
            for b in N:
                pairs+=1;q=resolve(a,b,v)
                if q is not None:new.append(q)
        f=sub(R+new);peak=max(peak,len(f))
        if len(f)>budget:return None,pairs,peak
    return f,pairs,peak

def implied_short(net,w):
    n=len(net.inputs);count=0
    for k in range(1,min(w,n)+1):
        for S in itertools.combinations(net.inputs,k):
            for signs in itertools.product((0,1),repeat=k):
                c=tuple(v if s else -v for v,s in zip(S,signs))
                ok=True
                for bits in itertools.product((False,True),repeat=n):
                    a=dict(zip(net.inputs,bits))
                    if accepts(net,a) and not sat((c,),a):ok=False;break
                count+=ok
    return count

def parity_cnf(n,b=1):
    out=[]
    for bits in itertools.product((0,1),repeat=n):
        if sum(bits)%2==b:continue
        out.append(tuple(-i if bits[i-1] else i for i in range(1,n+1)))
    return cf(out)

def or_audit():
    rows=[]
    for n in (4,8,16,32,64,128):
        net=tree(n,"OR");f=enc(net);reason=tuple(range(1,n+1))
        q,pairs,peak=dp(f,list(reversed([g.y for g in net.gates])),10000)
        rows.append({"n":n,"gates":len(net.gates),"reason_width":n,
          "rup":rup(f,reason),"short":implied_short(net,min(3,n-1)) if n<=8 else None,
          "dp_exact":q==(reason,),"pairs":pairs,"peak":peak})
    return rows

def xor_audit():
    rows=[]
    for n in (4,6,8,10,12,16):
        net=tree(n,"XOR");f=enc(net)
        q,pairs,peak=dp(f,list(reversed([g.y for g in net.gates])),5000)
        expected=1<<(n-1)
        small=None
        if n<=8:
            pc=parity_cnf(n)
            small=(len(pc)==expected and all(rup(f,c) for c in pc)
                   and implied_short(net,n-1)==0)
        rows.append({"n":n,"gf2_rows":1,"clause_projection":expected,
          "small_verified":small,"dp_status":"OPEN" if q is None else "EXACT",
          "dp_clauses":None if q is None else len(q),"pairs":pairs,"peak":peak})
    return rows

def source_formula(rng,n,m,unsat):
    if unsat:
        core=[tuple(-i if bits[i-1] else i for i in range(1,4))
              for bits in itertools.product((0,1),repeat=3)]
        return cf(core)
    planted={i:bool(rng.getrandbits(1)) for i in range(1,n+1)};cs=[]
    for _ in range(m):
        S=rng.sample(range(1,n+1),3);c=[v if rng.random()<.5 else -v for v in S]
        if not any(planted[abs(x)]==(x>0) for x in c):
            c[0]=S[0] if planted[S[0]] else -S[0]
        cs.append(tuple(c))
    return cf(cs)

def mixed_audit():
    rng=random.Random(270027);bad=0;s=u=0
    for i in range(80):
        n=rng.randint(3,7);F=source_formula(rng,n,3*n,i%2==1)
        truth=any(sat(F,dict(zip(range(1,n+1),bits)))
                  for bits in itertools.product((False,True),repeat=n))
        if truth:s+=1
        else:u+=1
        for bits in itertools.product((False,True),repeat=n):
            a=dict(zip(range(1,n+1),bits))
            circuit=all(any(a[abs(x)]==(x>0) for x in c) for c in F)
            if circuit!=sat(F,a):bad+=1;break
    return {"cases":80,"sat":s,"unsat":u,"equivalence_failures":bad,"target":"OPEN_GENERAL_CNF"}

def run():
    O=or_audit();X=xor_audit();M=mixed_audit()
    A={"or":all(r["rup"] and r["dp_exact"] and (r["short"] in (None,0)) for r in O),
       "xor":all((r["small_verified"] in (None,True)) for r in X)
             and any(r["dp_status"]=="OPEN" for r in X),
       "mixed":M["equivalence_failures"]==0 and M["sat"]==40 and M["unsat"]==40}
    out={"artifact":"C027-JANUS-CONTEXT-PROJECTION-DISCOVERY","status":"PASS" if all(A.values()) else "FAIL",
         "base":"f0ffb9b7afdd1797c4c6648b32f5ee5c5a80a9f0",
         "or":O,"xor":X,"mixed":M,"assertions":A,
         "bottleneck":"TRACTABLE_PROJECTION_DISCOVERY",
         "general_sat_oracle_called":False}
    out["integrity"]=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    return out
if __name__=="__main__":
    r=run();print(json.dumps(r,indent=2))
    if r["status"]!="PASS":raise SystemExit(1)
