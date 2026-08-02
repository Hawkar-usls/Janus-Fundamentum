#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, itertools, json, random
from collections import deque

Clause=tuple[int,...]
CNF=tuple[Clause,...]

def canon_clause(c:Clause):
    s=set(c)
    if any(-x in s for x in s): return None
    return tuple(sorted(s,key=lambda x:(abs(x),x<0)))

def normalize(f:CNF)->CNF:
    cs=[]
    for c in f:
        q=canon_clause(c)
        if q is not None: cs.append(q)
    cs=sorted(set(cs),key=lambda c:(len(c),c))
    keep=[]
    for c in cs:
        sc=set(c)
        if any(set(d)<=sc for d in keep): continue
        keep.append(c)
    return tuple(keep)

def variables(f:CNF): return sorted({abs(x) for c in f for x in c})
def evaluate(f:CNF,a:dict[int,bool]): return all(any(a.get(abs(x),False)==(x>0) for x in c) for c in f)
def is_horn(f:CNF): return all(sum(x>0 for x in c)<=1 for c in f)
def is_dual_horn(f:CNF): return all(sum(x<0 for x in c)<=1 for c in f)

def horn_solve(f:CNF):
    f=normalize(f); a={v:False for v in variables(f)}; trace=[]
    changed=True
    while changed:
        changed=False
        for i,c in enumerate(f):
            pos=[x for x in c if x>0]; body=[-x for x in c if x<0]
            if all(a[v] for v in body):
                if not pos: return False,None,trace+[("conflict",i)]
                h=pos[0]
                if not a[h]: a[h]=True;trace.append(("set",h,i));changed=True
    return True,a,trace

def dual_horn_solve(f:CNF):
    ok,b,tr=horn_solve(tuple(tuple(-x for x in c) for c in f))
    if not ok:return False,None,tr
    return True,{v:not z for v,z in b.items()},tr

def nest_order(f:CNF):
    edges=[set(abs(x) for x in c) for c in normalize(f)]
    vs=set().union(*edges) if edges else set(); out=[]
    while vs:
        hit=None
        for v in sorted(vs):
            inc=[e & vs for e in edges if v in e]
            if all(a<=b or b<=a for a in inc for b in inc): hit=v;break
        if hit is None:return None
        out.append(hit);vs.remove(hit)
    return out

def eliminate(f:CNF,x:int)->CNF:
    pos=[c for c in f if x in c];neg=[c for c in f if -x in c]
    rest=[c for c in f if x not in c and -x not in c];res=[]
    for p in pos:
        for n in neg:
            q=canon_clause(tuple(y for y in p if y!=x)+tuple(y for y in n if y!=-x))
            if q is not None:res.append(q)
    return normalize(tuple(rest+res))

def beta_solve(f:CNF):
    f=normalize(f);order=nest_order(f)
    if order is None:return "OPEN",None,[]
    cur=f;records=[]
    for x in order:
        nxt=eliminate(cur,x);records.append((x,cur,nxt));cur=nxt
    if () in cur:return False,None,records
    a={}
    for x,before,_ in reversed(records):
        choices=[]
        for xv in (False,True):
            good=True
            for c in before:
                if not any((xv if abs(l)==x else a.get(abs(l),False))==(l>0) for l in c):good=False;break
            if good:choices.append(xv)
        if not choices:return "INVALID",None,records
        a[x]=choices[0]
    return True,a,records

def solve(f:CNF):
    g=normalize(f)
    if is_horn(g):
        ans,w,cert=horn_solve(g);return {"status":"EXACT","class":"HORN","sat":ans,"witness":w,"certificate":cert,"normalized":g}
    if is_dual_horn(g):
        ans,w,cert=dual_horn_solve(g);return {"status":"EXACT","class":"DUAL_HORN","sat":ans,"witness":w,"certificate":cert,"normalized":g}
    ans,w,cert=beta_solve(g)
    if ans!="OPEN":return {"status":"EXACT","class":"BETA_ACYCLIC","sat":ans,"witness":w,"certificate_length":len(cert),"normalized":g}
    return {"status":"OPEN","class":None,"normalized":g}

def brute(f:CNF):
    vs=variables(f)
    for bits in itertools.product((False,True),repeat=len(vs)):
        a=dict(zip(vs,bits))
        if evaluate(f,a):return True,a
    return False,None

def run(seed=330033,cases=900):
    rng=random.Random(seed);exact=open_=mismatch=wfail=0;classes={}
    for _ in range(cases):
        n=rng.randint(1,8);m=rng.randint(0,12);f=[]
        mode=rng.randrange(4)
        for _ in range(m):
            width=rng.randint(1,min(4,n));vs=rng.sample(range(1,n+1),width)
            c=[]
            for j,v in enumerate(vs):
                if mode==0:c.append(v if j==0 else -v)
                elif mode==1:c.append(-v if j==0 else v)
                else:c.append(v if rng.getrandbits(1) else -v)
            f.append(tuple(c))
        f=tuple(f);r=solve(f);b,w=brute(normalize(f))
        if r['status']=='OPEN':open_+=1;continue
        exact+=1;classes[r['class']]=classes.get(r['class'],0)+1
        if bool(r['sat'])!=b:mismatch+=1
        if r['sat'] and (r['witness'] is None or not evaluate(normalize(f),r['witness'])):wfail+=1
    # Negative control: cyclic 4-edge hypergraph, with polarity chosen so the
    # dispatcher cannot accept it as Horn or dual-Horn before beta recognition.
    hard=((1,2),(-2,-3),(3,4),(-4,-1))
    assert not is_horn(hard) and not is_dual_horn(hard)
    assert nest_order(hard) is None and solve(hard)['status']=='OPEN'
    assert mismatch==0 and wfail==0
    out={'artifact_id':'C033-JANUS-PROOF-CARRYING-TRACTABLE-PORTFOLIO','status':'PASS','p_vs_np':'OPEN','seed':seed,'cases':cases,'exact':exact,'open':open_,'classes':classes,'mismatches':mismatch,'witness_failures':wfail,'negative_control':'OPEN_NON_HORN_NON_DUAL_HORN_CYCLIC','claim_boundary':'Polynomial sound portfolio for normalized Horn, dual-Horn and beta-acyclic CNF only; no universal SAT algorithm.'}
    out['integrity_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True,separators=(',',':')).encode()).hexdigest();return out

def main():
    p=argparse.ArgumentParser();p.add_argument('--self-test',action='store_true');a=p.parse_args();r=run();print(json.dumps(r,indent=2,sort_keys=True));assert not a.self_test or r['status']=='PASS'
if __name__=='__main__':main()
