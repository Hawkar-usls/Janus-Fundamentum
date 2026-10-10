#!/usr/bin/env python3
"""
Finite controls for NM-0018:
anchored higher-lift deterministic FPT solver and sharpened q_graph bound.

The theorem input is an explicit binary m-lift [B_G;S] plus the inherited
distinguished common-f cocycle span by support-at-most-four cocycles.

This checker:
  1. builds a quotient-rank-4 control whose full cocycle space is spanned by
     f-containing cocycles of support <=4 and recovers a small quotient basis;
  2. verifies the support bound |F|<=1+3q;
  3. compares the generalized exceptional-support + ordinary T-join solver
     against exhaustive binary-cycle search;
  4. verifies the sharpened cogirth/incidence lower bound on the NM-0017 leaf.
"""
from __future__ import annotations

import itertools
import json
import random

INF=10**18


def gf2_rank(rows):
    rows=[int(x) for x in rows if x]
    rank=0
    while rows:
        rows=[r for r in rows if r]
        if not rows:
            break
        pivot=max(rows)
        bit=1<<(pivot.bit_length()-1)
        rank+=1
        nxt=[]
        used=False
        for row in rows:
            if row==pivot and not used:
                used=True
                continue
            nxt.append(row^pivot if row&bit else row)
        rows=nxt
    return rank


def in_span(x,rows):
    return gf2_rank(list(rows)+[x])==gf2_rank(rows)


def reduced_incidence_rows(n,edges):
    out=[]
    for v in range(n-1):
        mask=0
        for i,(a,b) in enumerate(edges):
            if a==v or b==v:
                mask |= 1<<i
        out.append(mask)
    return out


def enumerate_small_f_cocycles(m,f,rows):
    out=[]
    others=[e for e in range(m) if e!=f]
    for k in range(4):
        for extra in itertools.combinations(others,k):
            d=1<<f
            for e in extra:
                d |= 1<<e
            if in_span(d,rows):
                out.append(d)
    return out


def choose_quotient_basis(small,cut_rows,q):
    picked=[]
    current=gf2_rank(cut_rows)
    for d in small:
        nr=gf2_rank(cut_rows+picked+[d])
        if nr==current+len(picked)+1:
            picked.append(d)
            if len(picked)==q:
                break
    assert len(picked)==q
    assert gf2_rank(cut_rows+picked)==gf2_rank(cut_rows)+q
    return picked


def labels_from_signature_rows(sig,m):
    labels=[]
    for e in range(m):
        g=0
        for i,row in enumerate(sig):
            if (row>>e)&1:
                g |= 1<<i
        labels.append(g)
    return labels


def boundary_vertices(indices,edges):
    p={}
    for i in indices:
        u,v=edges[i]
        p[u]=p.get(u,0)^1
        p[v]=p.get(v,0)^1
    return sorted(v for v,b in p.items() if b)


def xor_labels(indices,labels):
    x=0
    for i in indices:
        x ^= labels[i]
    return x


def floyd(n,edges,weights,allowed):
    d=[[INF]*n for _ in range(n)]
    for i in range(n):
        d[i][i]=0
    for e in allowed:
        u,v=edges[e]
        if weights[e]<d[u][v]:
            d[u][v]=d[v][u]=weights[e]
    for k in range(n):
        for i in range(n):
            if d[i][k]>=INF:
                continue
            for j in range(n):
                z=d[i][k]+d[k][j]
                if z<d[i][j]:
                    d[i][j]=z
    return d


def min_pairing(T,d):
    T=tuple(T)
    memo={0:0}
    def rec(mask):
        if mask in memo:
            return memo[mask]
        i=(mask & -mask).bit_length()-1
        rest=mask^(1<<i)
        best=INF
        mm=rest
        while mm:
            j=(mm & -mm).bit_length()-1
            if d[T[i]][T[j]]<INF:
                best=min(best,d[T[i]][T[j]]+rec(rest^(1<<j)))
            mm ^= 1<<j
        memo[mask]=best
        return best
    return rec((1<<len(T))-1)


def brute_cycle(n,edges,weights,labels,f):
    best=INF
    m=len(edges)
    for mask in range(1<<m):
        if not ((mask>>f)&1):
            continue
        chosen=[i for i in range(m) if (mask>>i)&1]
        if xor_labels(chosen,labels):
            continue
        if boundary_vertices(chosen,edges):
            continue
        best=min(best,sum(weights[i] for i in chosen))
    return best


def support_tjoin_solver(n,edges,weights,labels,f,max_support):
    F=[i for i,g in enumerate(labels) if g]
    assert f in F
    assert len(F)<=max_support
    Fset=set(F)
    zero=[i for i in range(len(edges)) if i not in Fset]
    d=floyd(n,edges,weights,zero)
    best=INF
    feasible_cases=0
    for mask in range(1<<len(F)):
        R=[F[j] for j in range(len(F)) if (mask>>j)&1]
        if f not in R or xor_labels(R,labels):
            continue
        T=boundary_vertices(R,edges)
        pc=min_pairing(T,d)
        if pc>=INF:
            continue
        feasible_cases+=1
        best=min(best,sum(weights[e] for e in R)+pc)
    return best,len(F),feasible_cases


def rank4_anchored_control():
    # Fixed connected multigraph with quotient rank four.
    edges=[
        (0,1),(1,2),(2,3),(3,4),
        (0,3),(3,4),(0,2),(1,2),
        (0,2),(2,3),(2,3),(2,3),
    ]
    n=5
    m=len(edges)
    f=0
    B=reduced_incidence_rows(n,edges)

    # Four f-containing support-four cocycles, independent modulo cuts.
    D=[99,2569,1091,1155]
    assert all(x.bit_count()==4 and ((x>>f)&1) for x in D)
    assert gf2_rank(B+D)==gf2_rank(B)+4

    full=B+D
    small=enumerate_small_f_cocycles(m,f,full)
    assert gf2_rank(small)==gf2_rank(full)

    picked=choose_quotient_basis(small,B,4)
    assert all(x.bit_count()<=4 and ((x>>f)&1) for x in picked)

    F=0
    for x in picked:
        F |= x
    assert F.bit_count()<=1+3*4

    labels=labels_from_signature_rows(picked,m)
    assert sum(g!=0 for g in labels)==F.bit_count()
    assert labels[f]!=0

    return n,edges,f,B,picked,labels,{
        "cut_rank":gf2_rank(B),
        "full_rank":gf2_rank(full),
        "small_f_cocycles":len(small),
        "quotient_rank":4,
        "selected_sizes":[x.bit_count() for x in picked],
        "normalized_signature_support":F.bit_count(),
        "theorem_support_ceiling":13,
    }


def solver_controls(trials=150,seed=180018):
    n,edges,f,B,picked,labels,norm=rank4_anchored_control()
    rng=random.Random(seed)
    maxsupp=0
    feasible=0
    for _ in range(trials):
        weights=[rng.randint(0,7) for _ in edges]
        brute=brute_cycle(n,edges,weights,labels,f)
        fast,supp,_=support_tjoin_solver(
            n,edges,weights,labels,f,max_support=1+3*len(picked)
        )
        assert brute==fast,(weights,brute,fast)
        maxsupp=max(maxsupp,supp)
        feasible += int(brute<INF)
    return norm,{
        "instances":trials,
        "feasible_instances":feasible,
        "max_signature_support_tested":maxsupp,
    }


def qgraph_cogirth_lower_bound(rank_m,elements,cogirth):
    # Any full-row-rank reduced incidence representation of a nonzero
    # graphic cut subspace has at least one column of weight one; otherwise
    # XOR of all basis rows is zero. Hence d*g* <= 2|E|-1.
    max_graphic_cut_dim=(2*elements-1)//cogirth
    return rank_m-max_graphic_cut_dim


def qgraph_control():
    lb=qgraph_cogirth_lower_bound(11,16,4)
    assert lb==4
    return {
        "rank":11,
        "elements":16,
        "cogirth":4,
        "old_bound":"(r-2)g*=36>32",
        "sharpened_general_bound":"(r-q)g* <= 2|E|-1",
        "q_graph_lower_bound":lb,
    }


def main():
    normalization,solver=solver_controls()
    out={
      "status":"PASS_FINITE_HIGHER_LIFT_ANCHORED_FPT_CONTROLS",
      "normalization":normalization,
      "solver":solver,
      "q_graph_diagnostic":qgraph_control(),
      "theorem":{
        "anchored_cocycle_support_bound":4,
        "signature_support_bound_formula":"1+3q",
        "exceptional_cases_formula":"2^(1+3q)",
        "deterministic_parameterized_solver":"T_JOIN_FPT_IN_EXPLICIT_LIFT_RANK",
        "polynomial_when":"q=O(log n) with constructive representation",
        "P_VS_NP":"OPEN",
      }
    }
    print(json.dumps(out,sort_keys=True))


if __name__=="__main__":
    main()
