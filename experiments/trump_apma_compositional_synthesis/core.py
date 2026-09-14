from __future__ import annotations
from collections import defaultdict, deque
import hashlib, json, time

def canon(raw):
    out=set()
    for clause in raw:
        s=set(int(x) for x in clause)
        if any(-x in s for x in s):
            continue
        out.add(tuple(sorted(s,key=lambda z:(abs(z),z<0))))
    return [tuple(c) for c in sorted(out,key=lambda c:(len(c),tuple((abs(x),x<0) for x in c)))]

def replay(raw, assn):
    for c in raw:
        if not any((lit>0 and bool(assn.get(abs(int(lit)),False))) or (lit<0 and not bool(assn.get(abs(int(lit)),False))) for lit in c):
            return False
    return True

def q0(raw):
    cnf=canon(raw)
    pos=[tuple(c) for c in cnf if c and all(x>0 for x in c)]
    neg=[tuple(c) for c in cnf if len(c)==2 and all(x<0 for x in c)]
    if not pos or len(pos)+len(neg)!=len(cnf): return None
    owner={}
    for i,b in enumerate(pos):
        for x in b:
            if x in owner: return None
            owner[x]=i
    allv={abs(x) for c in cnf for x in c}
    if set(owner)!=allv: return None
    pairs={tuple(sorted((-a,-b))) for a,b in neg}
    for b in pos:
        xs=sorted(b)
        for i,a in enumerate(xs):
            for z in xs[i+1:]:
                if (min(a,z),max(a,z)) not in pairs: return None
    adj=defaultdict(set)
    for a,b in pairs:
        if owner[a]!=owner[b]: adj[a].add(b); adj[b].add(a)
    unseen=set(owner); comps=[]
    while unseen:
        s=min(unseen);unseen.remove(s);st=[s];cc={s}
        while st:
            x=st.pop()
            for y in adj[x]:
                if y in unseen: unseen.remove(y);cc.add(y);st.append(y)
        comps.append(tuple(sorted(cc)))
    co={x:i for i,c in enumerate(comps) for x in c}
    for c in comps:
        seen=set()
        for x in c:
            if owner[x] in seen:return None
            seen.add(owner[x])
        for i,a in enumerate(c):
            for b in c[i+1:]:
                if (min(a,b),max(a,b)) not in pairs:return None
    edges={i:sorted({co[x] for x in b}) for i,b in enumerate(pos)}
    return {'t':0,'blocks':[list(b) for b in pos],'components':[list(c) for c in comps],'edges':edges}

def r0(s):
    if not isinstance(s,dict) or s.get('t')!=0:return None
    blocks=s['blocks'];comps=s['components'];edges={int(k):list(v) for k,v in s['edges'].items()};mr={}
    def aug(u,seen):
        for v in edges[u]:
            if v in seen:continue
            seen.add(v)
            if v not in mr or aug(mr[v],seen):mr[v]=u;return True
        return False
    for u in range(len(blocks)):
        if not aug(u,set()):
            S={u};N=set();q=deque([u])
            while q:
                a=q.popleft()
                for v in edges[a]:
                    if v in N:continue
                    N.add(v)
                    if v in mr and mr[v] not in S:S.add(mr[v]);q.append(mr[v])
            return {'decision':'UNSAT','certificate':{'kind':'c0','S':sorted(S),'N':sorted(N)}}
    ml={u:v for v,u in mr.items()};ass={x:False for b in blocks for x in b};cs=[set(c) for c in comps]
    for u,v in ml.items():
        xs=[x for x in blocks[u] if x in cs[v]]
        if len(xs)!=1:return None
        ass[xs[0]]=True
    return {'decision':'SAT','assignment':ass,'certificate':{'kind':'c0s','pairs':sorted([[u,v] for u,v in ml.items()])}}

def q1(raw):
    cnf=canon(raw)
    if not cnf or any(len(c)>2 or len(c)==0 for c in cnf):return None
    return {'t':1,'cnf':[list(c) for c in cnf],'vars':sorted({abs(x) for c in cnf for x in c})}

def _path(g,a,b):
    q=deque([a]);prev={a:None}
    while q:
        x=q.popleft()
        if x==b:break
        for y in g.get(x,()):
            if y not in prev:prev[y]=x;q.append(y)
    if b not in prev:return None
    p=[];x=b
    while x is not None:p.append(x);x=prev[x]
    return list(reversed(p))

def r1(s):
    if not isinstance(s,dict) or s.get('t')!=1:return None
    cnf=[tuple(c) for c in s['cnf']];vs=list(s['vars']);g=defaultdict(set);rg=defaultdict(set)
    for c in cnf:
        arcs=[(-c[0],c[0])] if len(c)==1 else [(-c[0],c[1]),(-c[1],c[0])]
        for x,y in arcs:g[x].add(y);rg[y].add(x);g.setdefault(y,set());rg.setdefault(x,set())
    nodes=set(g)|set(rg)
    for v in vs:nodes|={v,-v}
    seen=set();order=[]
    def d1(x):
        seen.add(x)
        for y in g.get(x,()):
            if y not in seen:d1(y)
        order.append(x)
    for x in sorted(nodes,key=lambda z:(abs(z),z<0)):
        if x not in seen:d1(x)
    comp={};cid=0
    def d2(x):
        comp[x]=cid
        for y in rg.get(x,()):
            if y not in comp:d2(y)
    for x in reversed(order):
        if x not in comp:d2(x);cid+=1
    for v in vs:
        if comp[v]==comp[-v]:
            return {'decision':'UNSAT','certificate':{'kind':'c1','v':v,'p1':_path(g,v,-v),'p2':_path(g,-v,v)}}
    ass={v:(comp[v]>comp[-v]) for v in vs}
    if not replay(cnf,ass):ass={v:not ass[v] for v in vs}
    if not replay(cnf,ass):return None
    return {'decision':'SAT','assignment':ass,'certificate':{'kind':'c1s'}}

def q2(raw):
    cnf=canon(raw)
    if not cnf:return None
    rules=[]
    for c in cnf:
        pos=[x for x in c if x>0]
        if len(pos)>1:return None
        rules.append({'body':sorted(-x for x in c if x<0),'head':pos[0] if pos else None})
    return {'t':2,'rules':rules,'vars':sorted({abs(x) for c in cnf for x in c})}

def r2(s):
    if not isinstance(s,dict) or s.get('t')!=2:return None
    rules=s['rules'];true=set();trace=[];changed=True
    while changed:
        changed=False
        for i,r in enumerate(rules):
            if set(r['body']).issubset(true):
                if r['head'] is None:return {'decision':'UNSAT','certificate':{'kind':'c2','trace':trace+[i]}}
                if r['head'] not in true:true.add(r['head']);trace.append(i);changed=True
    return {'decision':'SAT','assignment':{v:(v in true) for v in s['vars']},'certificate':{'kind':'c2s','trace':trace}}

def _sat_local(clauses,vs,bits):
    a={v:bool((bits>>i)&1) for i,v in enumerate(vs)}
    return all(any((x>0 and a[abs(x)]) or (x<0 and not a[abs(x)]) for x in c) for c in clauses)

def q3(raw):
    cnf=canon(raw)
    if not cnf:return None
    groups=defaultdict(list)
    for c in cnf:
        if not (1<=len(c)<=3):return None
        key=tuple(sorted(abs(x) for x in c))
        if len(set(key))!=len(key):return None
        groups[key].append(c)
    rows=[]
    for key,clauses in sorted(groups.items()):
        k=len(key);allowed=[b for b in range(1<<k) if _sat_local(clauses,key,b)]
        if len(allowed)!=(1<<(k-1)):return None
        par={sum((b>>i)&1 for i in range(k))%2 for b in allowed}
        if len(par)!=1:return None
        rows.append({'vars':list(key),'rhs':next(iter(par))})
    return {'t':3,'rows':rows,'vars':sorted({v for r in rows for v in r['vars']})}

def r3(s):
    if not isinstance(s,dict) or s.get('t')!=3:return None
    rows=[[set(r['vars']),int(r['rhs']),{i}] for i,r in enumerate(s['rows'])];basis={}
    for S,b,p in rows:
        S=set(S);p=set(p)
        while S:
            v=min(S)
            if v not in basis:break
            T,c,q=basis[v];S^=T;b^=c;p^=q
        if not S:
            if b:return {'decision':'UNSAT','certificate':{'kind':'c3','rows':sorted(p)}}
            continue
        basis[min(S)]=(S,b,p)
    ass={v:False for v in s['vars']}
    for v in sorted(basis,reverse=True):
        S,b,_=basis[v];val=bool(b)
        for z in S:
            if z!=v and ass.get(z,False):val=not val
        ass[v]=val
    return {'decision':'SAT','assignment':ass,'certificate':{'kind':'c3s'}}

QS=[q0,q1,q2,q3];RS=[r0,r1,r2,r3]

def grammar():
    return [{'id':f'G{q}{r}','nodes':[f'P{q}',f'P{4+r}','P8'],'q':q,'r':r,'depth':3,'size':3} for q in range(4) for r in range(4)]

def run_program(raw,p):
    t0=time.perf_counter();s=QS[int(p['q'])](raw);t1=time.perf_counter()
    if s is None:return {'admitted':False,'decision':None,'certificate':None,'assignment':None,'timing':{'substrate_ms':(t1-t0)*1000,'carrier_ms':0.0,'verify_ms':0.0}}
    z=RS[int(p['r'])](s);t2=time.perf_counter()
    if z is None:return {'admitted':False,'decision':None,'certificate':None,'assignment':None,'timing':{'substrate_ms':(t1-t0)*1000,'carrier_ms':(t2-t1)*1000,'verify_ms':0.0}}
    ok=(z['decision']!='SAT') or replay(raw,z.get('assignment',{}));t3=time.perf_counter()
    if not ok:return {'admitted':False,'decision':None,'certificate':None,'assignment':None,'timing':{'substrate_ms':(t1-t0)*1000,'carrier_ms':(t2-t1)*1000,'verify_ms':(t3-t2)*1000}}
    return {'admitted':True,**z,'timing':{'substrate_ms':(t1-t0)*1000,'carrier_ms':(t2-t1)*1000,'verify_ms':(t3-t2)*1000}}

def program_hash(p):
    return hashlib.sha256(json.dumps(p,sort_keys=True,separators=(',',':')).encode()).hexdigest()
