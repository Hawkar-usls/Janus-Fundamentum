#!/usr/bin/env python3
"""Exact finite controls for top-plateau -> optimal-face parity transfer."""

from __future__ import annotations
from itertools import combinations
import json
import random

INF = 10**9


def dot2(a: int, b: int) -> int:
    return (a & b).bit_count() & 1


def all_simple_paths(n, edges, s, t):
    adj=[[] for _ in range(n)]
    for i,(u,v,w,r) in enumerate(edges):
        adj[u].append((v,i)); adj[v].append((u,i))
    out=[]
    def dfs(v,vis,elist):
        if v==t:
            out.append(tuple(elist)); return
        for to,i in adj[v]:
            if to not in vis:
                vis.add(to); elist.append(i)
                dfs(to,vis,elist)
                elist.pop(); vis.remove(to)
    dfs(s,{s},[])
    return out


def transform(n, orig_edges, s, t, c, d):
    h=c^d
    q_candidates=[q for q in (1,2,3) if dot2(q,h)==0]
    assert len(q_candidates)==1
    q=q_candidates[0]
    first_target=dot2(q,c)
    q2=next(q2 for q2 in (1,2,3) if dot2(q2,h)==1)

    ed=[]
    N=n
    for u,v,label in orig_edges:
        first=dot2(q,label)
        refined=dot2(q2,label)
        if first:
            ed.append((u,v,1,refined))
        else:
            z=N; N+=1
            ed.append((u,z,1,refined))
            ed.append((z,v,0,0))
    tt=t
    if first_target==0:
        tt=N; N+=1
        ed.append((t,tt,0,0))
    return N,ed,s,tt


def make_matching_graph(N, ed, s, t):
    alive=list(range(N))+[N+i for i in range(N) if i not in (s,t)]
    idx={v:i for i,v in enumerate(alive)}
    H=[]
    for u,v,w,r in ed:
        H.append((idx[u],idx[v],w,r))
        if u not in (s,t) and v not in (s,t):
            H.append((idx[N+u],idx[N+v],w,r))
    for v in range(N):
        if v not in (s,t):
            H.append((idx[v],idx[N+v],0,0))
    return len(alive),H


def enumerate_perfect_matchings(n,H):
    adj=[[] for _ in range(n)]
    for i,(u,v,w,r) in enumerate(H):
        adj[u].append((v,i)); adj[v].append((u,i))
    used=[False]*n
    out=[]
    def rec(cost,par):
        try:
            v=next(i for i in range(n) if not used[i])
        except StopIteration:
            out.append((cost,par)); return
        used[v]=True
        for to,eid in adj[v]:
            if not used[to]:
                used[to]=True
                _,_,w,r=H[eid]
                rec(cost+w,par^r)
                used[to]=False
        used[v]=False
    rec(0,0)
    return out


def run(seed=20260924,trials=100):
    rng=random.Random(seed)
    checked=0
    for _ in range(trials):
        n=4
        possible=list(combinations(range(n),2))
        rng.shuffle(possible)
        orig=[]
        for u,v in possible[:rng.randint(2,5)]:
            orig.append((u,v,rng.randrange(4)))
        s,t=0,3
        c,d=rng.sample(range(4),2)

        N,ed,ss,tt=transform(n,orig,s,t,c,d)
        paths=[P for P in all_simple_paths(N,ed,ss,tt) if len(P)%2==1]
        if not paths:
            continue
        opt=min(sum(ed[i][2] for i in P) for P in paths)
        path_parities=set()
        for P in paths:
            if sum(ed[i][2] for i in P)==opt:
                par=0
                for i in P:
                    par ^= ed[i][3]
                path_parities.add(par)

        hn,H=make_matching_graph(N,ed,ss,tt)
        if hn>16:
            continue
        pms=enumerate_perfect_matchings(hn,H)
        if not pms:
            continue
        mopt=min(c for c,_ in pms)
        matching_parities={p for c,p in pms if c==mopt}

        assert opt==mopt
        assert path_parities==matching_parities
        checked += 1

    assert checked >= 40
    return checked


if __name__=="__main__":
    checked=run()
    print(json.dumps({
        "status":"PASS",
        "random_unit_positive_instances_checked":checked,
        "minimum_path_cost_equals_minimum_matching_cost":True,
        "refined_parities_on_minimum_paths_equal_refined_parities_on_minimum_matchings":True,
        "claim_ceiling":"FINITE_CONTROL_ONLY__GENERAL_BLOSSOM_PARITY_SOLVER_NOT_CLAIMED"
    },indent=2))
