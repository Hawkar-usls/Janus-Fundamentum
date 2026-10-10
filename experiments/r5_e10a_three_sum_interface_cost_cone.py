#!/usr/bin/env python3
"""
Finite controls for:
1) the unit-graphic realization of every positive integer metric triple as a
   3-sum separator conditioned-cost triple;
2) exact preservation of GF(2)^2 prescribed-label simple-path optima under
   positive-integer edge-weight -> unit-series expansion.

This is a regression checker, not the proof.
"""
from collections import deque
from itertools import combinations
import random

LABELS = [(0,0),(0,1),(1,0),(1,1)]

def xor(a,b):
    return (a[0]^b[0], a[1]^b[1])

def add_edge(adj,u,v,label=(0,0),weight=1):
    adj.setdefault(u,[]).append((v,label,weight))
    adj.setdefault(v,[]).append((u,label,weight))

def add_unit_path(adj,u,v,length,label=(0,0),prefix="p"):
    assert length >= 1
    prev=u
    for i in range(length):
        nxt=v if i==length-1 else (prefix,i)
        lab=label if i==0 else (0,0)
        add_edge(adj,prev,nxt,lab,1)
        prev=nxt

def bfs_distance(adj,s,t):
    q=deque([(s,0)])
    seen={s}
    while q:
        v,d=q.popleft()
        if v==t:
            return d
        for w,_,_ in adj.get(v,[]):
            if w not in seen:
                seen.add(w)
                q.append((w,d+1))
    return None

def metric_triple_control(limit=8):
    tested=0
    for a in range(1,limit+1):
        for b in range(1,limit+1):
            for c in range(1,limit+1):
                if a>b+c or b>a+c or c>a+b:
                    continue
                adj={}
                add_unit_path(adj,"A","B",a,prefix=("AB",a,b,c))
                add_unit_path(adj,"B","C",b,prefix=("BC",a,b,c))
                add_unit_path(adj,"C","A",c,prefix=("CA",a,b,c))
                got=(bfs_distance(adj,"A","B"),
                     bfs_distance(adj,"B","C"),
                     bfs_distance(adj,"C","A"))
                assert got==(a,b,c),(a,b,c,got)
                tested+=1
    return tested

def enumerate_simple_path_optima(adj,s,t):
    best={g:None for g in LABELS}
    stack=[(s,{s},(0,0),0)]
    while stack:
        v,seen,lab,cost=stack.pop()
        if v==t:
            cur=best[lab]
            if cur is None or cost<cur:
                best[lab]=cost
            continue
        for w,elab,ew in adj.get(v,[]):
            if w in seen:
                continue
            stack.append((w,seen|{w},xor(lab,elab),cost+ew))
    return best

def expand_to_unit_series(edges):
    adj={}
    fresh=0
    for u,v,label,w in edges:
        assert isinstance(w,int) and w>=1
        prev=u
        for i in range(w):
            if i==w-1:
                nxt=v
            else:
                nxt=("sub",fresh)
                fresh+=1
            add_edge(adj,prev,nxt,label if i==0 else (0,0),1)
            prev=nxt
    return adj

def weighted_adj(edges):
    adj={}
    for u,v,label,w in edges:
        add_edge(adj,u,v,label,w)
    return adj

def series_expansion_control(trials=200,seed=510):
    rng=random.Random(seed)
    vertices=list(range(5))
    pairs=list(combinations(vertices,2))
    passed=0
    for _ in range(trials):
        chosen=rng.sample(pairs,rng.randint(5,8))
        edges=[]
        for u,v in chosen:
            edges.append((u,v,rng.choice(LABELS),rng.randint(1,5)))
        s,t=0,4
        a=enumerate_simple_path_optima(weighted_adj(edges),s,t)
        b=enumerate_simple_path_optima(expand_to_unit_series(edges),s,t)
        assert a==b,(edges,a,b)
        passed+=1
    return passed

def explicit_strict_max_completion_control():
    # Hidden target graph H: only a long 11 route is supplied here.
    # Three cheap branches certify strict-max; expensive completion edges can
    # be unitized without changing label-class path costs below their bound.
    s,t="s","t"
    edges=[]
    prev=s
    for i in range(8):
        nxt=t if i==7 else ("h",i)
        edges.append((prev,nxt,(1,1) if i==0 else (0,0),1))
        prev=nxt
    # lower labels 00,01,10 with costs 1,2,3
    edges.append((s,t,(0,0),1))
    add_specs=[((0,1),2,"b01"),((1,0),3,"b10")]
    for lab,L,pfx in add_specs:
        prev=s
        for i in range(L):
            nxt=t if i==L-1 else (pfx,i)
            edges.append((prev,nxt,lab if i==0 else (0,0),1))
            prev=nxt
    # one expensive auxiliary edge; enough for regression of unitization.
    edges.append((s,("aux",0),(0,1),20))
    edges.append((("aux",0),t,(1,0),20))
    weighted=enumerate_simple_path_optima(weighted_adj(edges),s,t)
    unit=enumerate_simple_path_optima(expand_to_unit_series(edges),s,t)
    assert weighted==unit
    assert weighted[(1,1)]==8
    assert max(weighted[g] for g in LABELS if g!=(1,1))<8
    return weighted

def main():
    m=metric_triple_control()
    s=series_expansion_control()
    ex=explicit_strict_max_completion_control()
    print("PASS")
    print("metric_triples_tested=",m)
    print("series_instances_tested=",s)
    print("strict_max_costs=",ex)

if __name__=="__main__":
    main()
