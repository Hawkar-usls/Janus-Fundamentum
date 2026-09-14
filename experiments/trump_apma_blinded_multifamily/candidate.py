from __future__ import annotations
from collections import defaultdict, deque
from pathlib import Path
import json, time

ROOT=Path(__file__).resolve().parent

def canon(cnf):
    out=set()
    for clause in cnf:
        s=set(int(x) for x in clause)
        if any(-x in s for x in s):
            continue
        out.add(tuple(sorted(s,key=lambda x:(abs(x),x<0))))
    return [tuple(c) for c in sorted(out,key=lambda c:(len(c),tuple((abs(x),x<0) for x in c)))]

def subsume(cnf):
    cs=[frozenset(c) for c in canon(cnf)]
    keep=[]
    for i,c in enumerate(cs):
        if any(j!=i and d < c for j,d in enumerate(cs)):
            continue
        keep.append(tuple(c))
    return canon(keep)

def contract_aux_pairs(cnf):
    cs=canon(cnf)
    while True:
        occ=defaultdict(int)
        for c in cs:
            for x in c: occ[abs(x)]+=1
        lookup={frozenset(c):i for i,c in enumerate(cs)}
        used=set(); add=[]; changed=False
        for i,c in enumerate(cs):
            if i in used: continue
            sc=set(c)
            for lit in list(c):
                v=abs(lit)
                if occ[v]!=2: continue
                mate=frozenset((sc-{lit})|{-lit})
                j=lookup.get(mate)
                if j is not None and j!=i and j not in used:
                    used|={i,j}; add.append(tuple(sc-{lit})); changed=True; break
        if not changed: return subsume(cs)
        cs=subsume([c for i,c in enumerate(cs) if i not in used]+add)

def collapse_equiv(cnf,raw_vars):
    cs=canon(cnf); parent={v:v for v in raw_vars}
    def f(x):
        parent.setdefault(x,x)
        while parent[x]!=x:
            parent[x]=parent[parent[x]]; x=parent[x]
        return x
    def u(a,b):
        a,b=f(a),f(b)
        if a!=b:
            if a>b: a,b=b,a
            parent[b]=a
    changed=True
    while changed:
        changed=False; imp=set()
        for c in cs:
            if len(c)==2:
                a,b=c
                if a<0<b: imp.add((-a,b))
                if b<0<a: imp.add((-b,a))
        pairs=[]
        for a,b in imp:
            if (b,a) in imp and f(a)!=f(b): pairs.append((a,b))
        if pairs:
            changed=True
            for a,b in pairs:u(a,b)
            mapped=[]
            for c in cs:
                z=[]
                for lit in c:
                    r=f(abs(lit)); z.append(r if lit>0 else -r)
                mapped.append(z)
            cs=contract_aux_pairs(mapped)
    return cs,{v:f(v) for v in raw_vars}

def normalize(raw):
    raw_vars=sorted({abs(x) for c in raw for x in c})
    cs=contract_aux_pairs(raw)
    cs,reps=collapse_equiv(cs,raw_vars)
    cs=contract_aux_pairs(cs)
    return cs,reps

def p0(cnf):
    pos=[frozenset(c) for c in cnf if c and all(x>0 for x in c)]
    neg=[frozenset(c) for c in cnf if len(c)==2 and all(x<0 for x in c)]
    if not pos:return None
    owner={}
    for i,b in enumerate(pos):
        for x in b:
            if x in owner:return None
            owner[x]=i
    allv={abs(x) for c in cnf for x in c}
    if set(owner)!=allv:return None
    pairs={tuple(sorted(-x for x in c)) for c in neg}
    for b in pos:
        xs=sorted(b)
        for i,a in enumerate(xs):
            for z in xs[i+1:]:
                if (a,z) not in pairs:return None
    adj=defaultdict(set)
    for a,b in pairs:
        if owner[a]!=owner[b]:adj[a].add(b);adj[b].add(a)
    unseen=set(owner); comps=[]
    while unseen:
        s=min(unseen);unseen.remove(s);q=[s];cc={s}
        while q:
            x=q.pop()
            for y in adj[x]:
                if y in unseen:unseen.remove(y);cc.add(y);q.append(y)
        comps.append(frozenset(cc))
    ci={x:i for i,c in enumerate(comps) for x in c}
    for cc in comps:
        xs=sorted(cc); seen=set()
        for x in xs:
            if owner[x] in seen:return None
            seen.add(owner[x])
        for i,a in enumerate(xs):
            for b in xs[i+1:]:
                if (a,b) not in pairs:return None
    if any(frozenset(c) not in set(pos)|set(neg) for c in cnf):return None
    edges={i:set() for i in range(len(pos))}
    for x,b in owner.items():edges[b].add(ci[x])
    return {'slot':0,'blocks':pos,'components':comps,'edges':edges}

def p1(cnf):
    if not cnf or any(len(c)>2 for c in cnf):return None
    return {'slot':1,'cnf':cnf}

def p2(cnf):
    if not cnf or not any(len(c)>=3 for c in cnf):return None
    if any(sum(x>0 for x in c)>1 for c in cnf):return None
    rules=[]
    for i,c in enumerate(cnf):
        head=next((x for x in c if x>0),None)
        ant=tuple(sorted(-x for x in c if x<0))
        rules.append((ant,head,i))
    return {'slot':2,'rules':rules,'cnf':cnf}

def p3(cnf):
    if not cnf or any(len(c)!=3 for c in cnf):return None
    groups=defaultdict(list)
    for c in cnf:groups[tuple(sorted(abs(x) for x in c))].append(tuple(c))
    eq=[]
    for scope,clauses in sorted(groups.items()):
        if len(clauses)!=4:return None
        good=[]
        for bits in range(8):
            val={scope[i]:bool((bits>>i)&1) for i in range(3)}
            if all(any(val[abs(x)] if x>0 else not val[abs(x)] for x in c) for c in clauses):good.append(bits)
        if len(good)!=4:return None
        par={((b>>0)&1)^((b>>1)&1)^((b>>2)&1) for b in good}
        if len(par)!=1:return None
        eq.append((scope,next(iter(par))))
    return {'slot':3,'equations':eq,'cnf':cnf}

def discover(cnf):
    probes=(p0,p1,p2,p3)
    for probe in probes:
        candidate=probe(cnf)
        if candidate is not None:
            return candidate
    return None

def solve0(c):
    mr={}
    def aug(u,seen):
        for v in sorted(c['edges'][u]):
            if v in seen:continue
            seen.add(v)
            if v not in mr or aug(mr[v],seen):mr[v]=u;return True
        return False
    for u in range(len(c['blocks'])):
        if not aug(u,set()):
            S={u};N=set();q=deque([u])
            while q:
                a=q.popleft()
                for v in sorted(c['edges'][a]):
                    if v in N:continue
                    N.add(v)
                    if v in mr and mr[v] not in S:S.add(mr[v]);q.append(mr[v])
            return 'UNSAT',None,{'S':sorted(S),'N':sorted(N)}
    ml={u:v for v,u in mr.items()}; ass={x:False for b in c['blocks'] for x in b}
    ci={x:i for i,cc in enumerate(c['components']) for x in cc}
    for u,v in ml.items():
        xs=[x for x in c['blocks'][u] if ci[x]==v]
        if len(xs)!=1:raise RuntimeError('nonunique edge')
        ass[xs[0]]=True
    return 'SAT',ass,{'pairs':sorted((u,v) for u,v in ml.items())}

def implication_graph(cnf):
    g=defaultdict(set); rg=defaultdict(set); vars_=sorted({abs(x) for c in cnf for x in c})
    for v in vars_:g[v];g[-v];rg[v];rg[-v]
    for c in cnf:
        if len(c)==0:return g,rg,vars_,True
        if len(c)==1: pairs=[(-c[0],c[0])]
        else:
            a,b=c;pairs=[(-a,b),(-b,a)]
        for a,b in pairs:g[a].add(b);rg[b].add(a)
    return g,rg,vars_,False

def solve1(c):
    g,rg,vars_,empty=implication_graph(c['cnf'])
    if empty:return 'UNSAT',None,{'empty_clause':True}
    seen=set();order=[]
    def d1(s):
        stack=[(s,0)];seen.add(s)
        while stack:
            x,i=stack[-1]; ns=sorted(g[x])
            if i<len(ns):
                y=ns[i];stack[-1]=(x,i+1)
                if y not in seen:seen.add(y);stack.append((y,0))
            else:order.append(x);stack.pop()
    for x in sorted(g,key=lambda z:(abs(z),z<0)):
        if x not in seen:d1(x)
    comp={};cid=0
    for s in reversed(order):
        if s in comp:continue
        q=[s];comp[s]=cid
        while q:
            x=q.pop()
            for y in rg[x]:
                if y not in comp:comp[y]=cid;q.append(y)
        cid+=1
    bad=next((v for v in vars_ if comp[v]==comp[-v]),None)
    def path(a,b):
        q=deque([a]);pre={a:None}
        while q:
            x=q.popleft()
            if x==b:break
            for y in sorted(g[x],key=lambda z:(abs(z),z<0)):
                if y not in pre:pre[y]=x;q.append(y)
        if b not in pre:return []
        out=[];x=b
        while x is not None:out.append(x);x=pre[x]
        return list(reversed(out))
    if bad is not None:return 'UNSAT',None,{'var':bad,'path_pos_neg':path(bad,-bad),'path_neg_pos':path(-bad,bad)}
    ass={v:(comp[v]>comp[-v]) for v in vars_}
    return 'SAT',ass,{'components':cid}

def solve2(c):
    true=set();trace=[];changed=True
    while changed:
        changed=False
        for ant,head,i in c['rules']:
            if all(x in true for x in ant):
                if head is None:return 'UNSAT',None,{'trace':trace,'sink_clause':i}
                if head not in true:true.add(head);trace.append([i,head]);changed=True
    vars_={abs(x) for cl in c['cnf'] for x in cl};ass={v:(v in true) for v in vars_}
    return 'SAT',ass,{'trace':trace}

def solve3(c):
    vars_=sorted({v for scope,_ in c['equations'] for v in scope});vi={v:i for i,v in enumerate(vars_)}
    rows=[]
    for i,(scope,rhs) in enumerate(c['equations']):
        mask=0
        for v in scope:mask^=1<<vi[v]
        rows.append([mask,int(rhs),1<<i])
    rank=0;piv=[]
    for col in range(len(vars_)):
        j=next((j for j in range(rank,len(rows)) if (rows[j][0]>>col)&1),None)
        if j is None:continue
        rows[rank],rows[j]=rows[j],rows[rank]
        for k in range(len(rows)):
            if k!=rank and ((rows[k][0]>>col)&1):
                rows[k][0]^=rows[rank][0];rows[k][1]^=rows[rank][1];rows[k][2]^=rows[rank][2]
        piv.append((rank,col));rank+=1
    for mask,rhs,prov in rows:
        if mask==0 and rhs:
            ids=[i for i in range(len(c['equations'])) if (prov>>i)&1]
            return 'UNSAT',None,{'equation_indices':ids}
    bits=[0]*len(vars_)
    for r,col in reversed(piv):
        mask,rhs,_=rows[r];s=0
        for j in range(col+1,len(vars_)):
            if (mask>>j)&1:s^=bits[j]
        bits[col]=rhs^s
    return 'SAT',{v:bool(bits[vi[v]]) for v in vars_},{'rank':rank}

def replay(raw,ass):
    return all(any((x>0 and ass.get(abs(x),False)) or (x<0 and not ass.get(abs(x),False)) for x in c) for c in raw)

def process_case(case):
    raw=[tuple(c) for c in case['cnf']]; t0=time.perf_counter();norm,reps=normalize(raw);t1=time.perf_counter();cand=discover(norm);t2=time.perf_counter()
    base={'case_id':case['case_id'],'normalized_nvars':len({abs(x) for c in norm for x in c}),'normalized_nclauses':len(norm),'t_normalize_ms':(t1-t0)*1000,'t_discovery_ms':(t2-t1)*1000}
    if cand is None:return base|{'candidate':'NO_CANDIDATE','decision':None,'root_replay':None,'certificate':None,'t_carrier_ms':0.0,'t_root_verify_ms':0.0}
    t3=time.perf_counter();dec,ass,cert=(solve0(cand) if cand['slot']==0 else solve1(cand) if cand['slot']==1 else solve2(cand) if cand['slot']==2 else solve3(cand));t4=time.perf_counter()
    root_ass=None;ok=None;tv=0.0
    if dec=='SAT':
        raw_vars={abs(x) for c in raw for x in c};root_ass={v:bool(ass.get(reps.get(v,v),False)) for v in raw_vars};q=time.perf_counter();ok=replay(raw,root_ass);tv=(time.perf_counter()-q)*1000
    return base|{'candidate':f'CANDIDATE_{cand["slot"]}','decision':dec,'root_replay':ok,'certificate':cert,'assignment':root_ass,'t_carrier_ms':(t4-t3)*1000,'t_root_verify_ms':tv}

def main():
    inp=json.loads((ROOT/'hidden_inputs.json').read_text(encoding='utf-8'))
    rows=[process_case(c) for c in inp['cases']]
    print(json.dumps({'artifact':'APMA_BLINDED_MULTI_FAMILY_CARRIER_ROUTING_FALSIFIER_GATE','rows':rows},sort_keys=True,separators=(',',':')))
if __name__=='__main__':main()
