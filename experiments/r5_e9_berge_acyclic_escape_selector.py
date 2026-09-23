#!/usr/bin/env python3
"""Exact factor-tree synthesis for Berge-acyclic NAE repair selectors.

The checker compares the dynamic program against brute force on many small
random incidence-tree instances.
"""

from itertools import product
import random

def nae(vals):
    return len(set(vals)) > 1

def edge_orientation(y,e):
    vals=[y[v] for v in e]
    assert nae(vals)
    # minority has the value occurring once
    for i,v in enumerate(e):
        if vals.count(vals[i]) == 1:
            m=v
            majors=tuple(w for w in e if w != v)
            return m,majors[0],majors[1]
    raise AssertionError

def repair_valid(y,edges,h):
    return all(nae(tuple(y[v]^h[v] for v in e)) for e in edges)

def incidence_forest(n,edges):
    # bipartite graph: variable ids 0..n-1, factor ids n..n+m-1
    N=n+len(edges)
    adj=[[] for _ in range(N)]
    for ei,e in enumerate(edges):
        f=n+ei
        for v in e:
            adj[v].append(f); adj[f].append(v)
    seen=set()
    for s in range(N):
        if not adj[s] or s in seen:
            continue
        stack=[(s,-1)]
        seen.add(s)
        while stack:
            u,p=stack.pop()
            for w in adj[u]:
                if w==p:
                    continue
                if w in seen:
                    return False
                seen.add(w)
                stack.append((w,u))
    return True

def synthesize(y,edges,p,A):
    n=len(y)
    if p in A:
        return None,None
    assert incidence_forest(n,edges)

    # Work only in p's connected incidence component.
    adj=[[] for _ in range(n+len(edges))]
    for ei,e in enumerate(edges):
        f=n+ei
        for v in e:
            adj[v].append(f); adj[f].append(v)

    parent={p:-1}
    order=[p]
    for u in order:
        for w in adj[u]:
            if w not in parent:
                parent[w]=u
                order.append(w)

    msg={}
    witness={}
    domains=[]
    for v in range(n):
        if v==p: domains.append({1})
        elif v in A: domains.append({0})
        else: domains.append({0,1})

    for u in reversed(order):
        par=parent[u]
        if u < n:
            allowed=set(domains[u])
            for f in adj[u]:
                if parent.get(f)==u:
                    allowed &= msg[(f,u)]
            if par!=-1:
                msg[(u,par)]=allowed
        else:
            ei=u-n
            e=edges[ei]
            pv=par
            assert pv in e
            others=[v for v in e if v!=pv]
            out=set()
            for b in (0,1):
                found=None
                for vals in product((0,1),repeat=2):
                    assign={pv:b,others[0]:vals[0],others[1]:vals[1]}
                    if any(assign[ov] not in msg[(ov,u)] for ov in others):
                        continue
                    if nae(tuple(y[v]^assign[v] for v in e)):
                        found=(vals[0],vals[1])
                        break
                if found is not None:
                    out.add(b)
                    witness[(u,pv,b)]=found
            msg[(u,pv)]=out

    root_allowed=set(domains[p])
    for f in adj[p]:
        if parent.get(f)==p:
            root_allowed &= msg[(f,p)]
    if 1 not in root_allowed:
        return None,None

    h=[0]*n
    h[p]=1

    def descend_var(v):
        for f in adj[v]:
            if parent.get(f)!=v:
                continue
            ei=f-n
            e=edges[ei]
            others=[w for w in e if w!=v]
            vals=witness[(f,v,h[v])]
            for ov,val in zip(others,vals):
                h[ov]=val
                descend_var(ov)

    descend_var(p)
    assert repair_valid(y,edges,h)
    assert h[p]==1
    assert all(h[a]==0 for a in A)

    W={i for i,b in enumerate(h) if b}
    sigma={}
    for ei,e in enumerate(edges):
        m,u,v=edge_orientation(y,e)
        if m in W:
            choices=[q for q in (u,v) if q in W]
            assert choices
            sigma[ei]=min(choices)
        else:
            sigma[ei]=min(u,v)

    # Monotone closure.
    S={p}
    changed=True
    while changed:
        changed=False
        for ei,e in enumerate(edges):
            m,u,v=edge_orientation(y,e)
            if m in S and sigma[ei] not in S:
                S.add(sigma[ei]); changed=True
            if u in S and v in S and m not in S:
                S.add(m); changed=True
    assert S <= W
    assert not (S & set(A))
    return h,sigma

def brute_exists(y,edges,p,A):
    n=len(y)
    for h in product((0,1),repeat=n):
        if h[p]!=1 or any(h[a] for a in A):
            continue
        if repair_valid(y,edges,h):
            return True
    return False

def random_tree_instance(rng,n_edges):
    # Grow a linear 3-uniform Berge-acyclic hypergraph by attaching
    # each new edge through exactly one existing variable and two fresh ones.
    edges=[(0,1,2)]
    n=3
    for _ in range(1,n_edges):
        attach=rng.randrange(n)
        edges.append((attach,n,n+1))
        n+=2
    # random model; reject until every edge is NAE
    while True:
        y=[rng.randrange(2) for _ in range(n)]
        if all(nae(tuple(y[v] for v in e)) for e in edges):
            return y,edges

def main():
    rng=random.Random(0xBAE5)
    checked=0
    for m in range(1,6):
        for _ in range(100):
            y,edges=random_tree_instance(rng,m)
            n=len(y)
            p=rng.randrange(n)
            A={v for v in range(n) if v!=p and rng.random()<0.25}
            brute=brute_exists(y,edges,p,A)
            h,sigma=synthesize(y,edges,p,A)
            assert (h is not None)==brute
            checked+=1
    print("BERGE_ACYCLIC_ESCAPE_SELECTOR_DP = PASS")
    print("BRUTE_FORCE_CROSSCHECKS =",checked)
    print("D1 = EMPTY")
    print("P_VS_NP = OPEN")

if __name__=="__main__":
    main()
