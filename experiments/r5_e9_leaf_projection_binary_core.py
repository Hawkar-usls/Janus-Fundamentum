#!/usr/bin/env python3
"""Leaf-projection -> binary-core escape-selector solver.

Finite self-test compares the polynomial reduction against brute-force repair
masks on random small instances whenever the ternary core vanishes.
"""

from collections import deque
from itertools import product
import random

def nae(vals):
    return len(set(vals)) > 1

def repair_valid(y,edges,h):
    return all(nae(tuple(y[v]^h[v] for v in e)) for e in edges)

def local_relation(y,scope):
    return {
        bits for bits in product((0,1),repeat=len(scope))
        if nae(tuple(y[v]^b for v,b in zip(scope,bits)))
    }

def solve_2sat(n,clauses):
    N=2*n
    g=[[] for _ in range(N)]
    rg=[[] for _ in range(N)]

    def lit(v,positive):
        return 2*v + (0 if positive else 1)

    def neg(a):
        return a^1

    for c in clauses:
        if len(c)==1:
            a=lit(*c[0])
            g[neg(a)].append(a)
            rg[a].append(neg(a))
        else:
            a=lit(*c[0]); b=lit(*c[1])
            g[neg(a)].append(b); rg[b].append(neg(a))
            g[neg(b)].append(a); rg[a].append(neg(b))

    seen=[False]*N
    order=[]
    def dfs(u):
        seen[u]=True
        for w in g[u]:
            if not seen[w]:
                dfs(w)
        order.append(u)

    for u in range(N):
        if not seen[u]:
            dfs(u)

    comp=[-1]*N
    def rdfs(u,c):
        comp[u]=c
        for w in rg[u]:
            if comp[w]<0:
                rdfs(w,c)

    c=0
    for u in reversed(order):
        if comp[u]<0:
            rdfs(u,c)
            c+=1

    a=[0]*n
    for v in range(n):
        t=lit(v,True); f=lit(v,False)
        if comp[t]==comp[f]:
            return None
        a[v]=1 if comp[t]>comp[f] else 0

    assert all(any(a[v]==int(pol) for v,pol in cl) for cl in clauses)
    return a

def solve_if_binary_core(y,edges,p,A):
    n=len(y)
    domains=[{0,1} for _ in range(n)]
    domains[p]={1}
    for a in A:
        domains[a]&={0}
    if any(not d for d in domains):
        return None,False

    factors={}
    inc=[set() for _ in range(n)]
    for fid,e in enumerate(edges):
        factors[fid]=[tuple(e),local_relation(y,e)]
        for v in e:
            inc[v].add(fid)

    alive=[True]*n
    records=[]
    q=deque(range(n))
    queued=set(range(n))

    def filter_factor(fid):
        scope,rel=factors[fid]
        rel={
            t for t in rel
            if all(t[i] in domains[v] for i,v in enumerate(scope))
        }
        factors[fid][1]=rel
        return bool(rel)

    while q:
        v=q.popleft()
        queued.discard(v)
        if not alive[v]:
            continue
        inc[v]={f for f in inc[v] if f in factors}

        if len(inc[v])==0:
            val=min(domains[v])
            records.append(("free",v,val))
            alive[v]=False
            continue

        if len(inc[v])>1:
            continue

        fid=next(iter(inc[v]))
        if not filter_factor(fid):
            return None,False

        scope,rel=factors[fid]
        pos=scope.index(v)
        rem=tuple(w for w in scope if w!=v)
        mapping={}
        proj=set()

        for t in sorted(rel):
            key=tuple(t[i] for i,w in enumerate(scope) if w!=v)
            mapping.setdefault(key,t[pos])
            proj.add(key)

        records.append(("project",v,rem,mapping))

        inc[v].discard(fid)
        alive[v]=False
        for w in rem:
            inc[w].discard(fid)
        del factors[fid]

        if len(rem)==0:
            if not proj:
                return None,False
        elif len(rem)==1:
            w=rem[0]
            allowed={t[0] for t in proj}
            domains[w]&=allowed
            if not domains[w]:
                return None,False
            if w not in queued:
                q.append(w); queued.add(w)
        else:
            factors[fid]=[rem,proj]
            for w in rem:
                inc[w].add(fid)
                if w not in queued:
                    q.append(w); queued.add(w)

    if any(len(scope)>2 for scope,rel in factors.values()):
        return None,True

    clauses=[]
    for v,d in enumerate(domains):
        if alive[v]:
            if d=={0}: clauses.append(((v,False),))
            elif d=={1}: clauses.append(((v,True),))

    for scope,rel in factors.values():
        if len(scope)==1:
            v=scope[0]
            allowed={t[0] for t in rel}
            if 0 not in allowed: clauses.append(((v,True),))
            if 1 not in allowed: clauses.append(((v,False),))
        elif len(scope)==2:
            u,v=scope
            for a,b in product((0,1),repeat=2):
                if (a,b) not in rel:
                    clauses.append(((u,not bool(a)),(v,not bool(b))))

    h=solve_2sat(n,clauses)
    if h is None:
        return None,False

    for rec in reversed(records):
        if rec[0]=="free":
            _,v,val=rec
            h[v]=val
        else:
            _,v,rem,mapping=rec
            key=tuple(h[w] for w in rem)
            h[v]=mapping[key]

    assert h[p]==1
    assert all(h[a]==0 for a in A)
    assert repair_valid(y,edges,h)
    return tuple(h),False

def brute(y,edges,p,A):
    n=len(y)
    for h in product((0,1),repeat=n):
        if h[p]!=1 or any(h[a] for a in A):
            continue
        if repair_valid(y,edges,h):
            return h
    return None

def random_instance(rng,n,m):
    edges=[]
    seen=set()
    while len(edges)<m:
        e=tuple(sorted(rng.sample(range(n),3)))
        if e not in seen:
            seen.add(e)
            edges.append(e)
    for y in product((0,1),repeat=n):
        if all(nae(tuple(y[v] for v in e)) for e in edges):
            return y,edges
    return None,None

def main():
    rng=random.Random(0xB1C0)
    checked=0
    for n in range(3,9):
        for _ in range(200):
            m=rng.randint(1,min(8,n))
            y,edges=random_instance(rng,n,m)
            if y is None:
                continue
            p=rng.randrange(n)
            A={v for v in range(n) if v!=p and rng.random()<0.2}
            got,ternary=solve_if_binary_core(y,edges,p,A)
            if ternary:
                continue
            ref=brute(y,edges,p,A)
            assert (got is None)==(ref is None)
            checked+=1

    print("LEAF_PROJECTION_BINARY_CORE = PASS")
    print("BRUTE_FORCE_CROSSCHECKS =",checked)
    print("D1 = EMPTY")
    print("P_VS_NP = OPEN")

if __name__=="__main__":
    main()
