#!/usr/bin/env python3
from itertools import product

BASE=[[2,3,-4],[-1,2,4],[-2,-5,-6],[1,-3,-4],[1,-5,6],[-3,5,-6],[-2,3,6],[-1,4,5]]
PIVOT=2
LOCAL=[1,3,4,5,6]
PI={1:-3,3:-5,4:6,5:-1,6:-4}
COMMON={1:False,3:False,4:False,5:False,6:True}


def vars_of(F): return {abs(l) for C in F for l in C}
def deficiency(F): return len(F)-len(vars_of(F))
def maxdef(F):
    best=-10**9
    for mask in range(1<<len(F)):
        sub=[F[i] for i in range(len(F)) if (mask>>i)&1]
        best=max(best,deficiency(sub))
    return best

def simplify(F,v,val):
    sat=v if val else -v; false=-v if val else v; out=[]
    for C in F:
        if sat in C: continue
        out.append([l for l in C if l!=false])
    return out

def map_block(i): return {PIVOT:PIVOT, **{v:10*(i+1)+j+1 for j,v in enumerate(LOCAL)}}
def rename_clause(C,m): return [(1 if l>0 else -1)*m[abs(l)] for l in C]
def raw_parent(k):
    F=[]; maps=[]
    for i in range(k):
        m=map_block(i); maps.append(m); F.extend(rename_clause(C,m) for C in BASE)
    return F,maps

def global_pi(maps):
    g={}
    for m in maps:
        for v in LOCAL:
            img=PI[v]
            g[m[v]]=(1 if img>0 else -1)*m[abs(img)]
    return g

def pi_clause(C,g):
    return [(g[abs(l)] if l>0 else -g[abs(l)]) for l in C]
def canon_clause(C): return tuple(sorted(set(C),key=lambda z:(abs(z),z)))
def connector_orbit(m1,m2,g):
    seed=[m1[1],-m2[3],m1[4]]
    out=[]; cur=seed
    seen=set()
    while canon_clause(cur) not in seen:
        cc=canon_clause(cur); seen.add(cc); out.append(list(cc)); cur=pi_clause(cur,g)
    return out

def orbit_family(k):
    F,maps=raw_parent(k); g=global_pi(maps); connectors=[]
    for i in range(k-1):
        orb=connector_orbit(maps[i],maps[i+1],g)
        assert len(orb)==12
        connectors.extend(orb)
    return F+connectors,maps,g,connectors

def transport_valid(target,source,g):
    src=[set(C) for C in source]
    for C in target:
        image=set(pi_clause(C,g))
        if not any(D.issubset(image) for D in src): return False
    return True

def assignment_for_maps(maps):
    a={PIVOT:False}
    for m in maps:
        for v,val in COMMON.items(): a[m[v]]=val
    return a

def sat(F,a): return all(any(a[abs(l)] if l>0 else not a[abs(l)] for l in C) for C in F)
def connected_primal(F):
    V=sorted(vars_of(F)); adj={v:set() for v in V}
    for C in F:
        vs=[abs(l) for l in C]
        for i,u in enumerate(vs):
            for w in vs[i+1:]: adj[u].add(w); adj[w].add(u)
    seen=set(); stack=[V[0]]
    while stack:
        u=stack.pop()
        if u in seen: continue
        seen.add(u); stack.extend(adj[u]-seen)
    return len(seen)==len(V)
def binary_equivalences(F):
    V=sorted(vars_of(F)); lits=V+[-v for v in V]
    adj={l:[] for l in lits}; radj={l:[] for l in lits}
    for C in F:
        if len(C)!=2: continue
        a,b=C
        for u,v in [(-a,b),(-b,a)]: adj[u].append(v); radj[v].append(u)
    seen=set(); order=[]
    def dfs(u):
        seen.add(u)
        for v in adj[u]:
            if v not in seen: dfs(v)
        order.append(u)
    for l in lits:
        if l not in seen: dfs(l)
    comp={}
    def rdfs(u,c):
        comp[u]=c
        for v in radj[u]:
            if v not in comp: rdfs(v,c)
    cid=0
    for u in reversed(order):
        if u not in comp: rdfs(u,cid); cid+=1
    eq=[]
    for i,u in enumerate(V):
        for v in V[i+1:]:
            if comp[u]==comp[v] or comp[u]==comp[-v]: eq.append((u,v))
    return eq

def main():
    raw,maps=raw_parent(2)
    assert maxdef(raw)==5
    Araw=simplify(raw,PIVOT,False); Braw=simplify(raw,PIVOT,True)
    assert maxdef(Araw)==2 and maxdef(Braw)==2

    F,maps,g,connectors=orbit_family(2)
    assert len(connectors)==12
    assert len(F)==28 and len(vars_of(F))==11 and deficiency(F)==17
    A=simplify(F,PIVOT,False); B=simplify(F,PIVOT,True)
    assert len(A)==24 and len(B)==24 and deficiency(A)==14 and deficiency(B)==14
    assert maxdef(Araw)+12==14 and maxdef(Braw)+12==14
    assert connected_primal(A) and connected_primal(B)
    assert binary_equivalences(A)==[] and binary_equivalences(B)==[]

    a=assignment_for_maps(maps); a[PIVOT]=False
    assert sat(A,a)
    # B uses the same nonpivot assignment; pivot has already been removed.
    assert sat(B,a)
    assert transport_valid(A,B,g)
    assert sum(1 for v in g if g[v]!=v)==10

    print('R44BX EXACT REPLAY PASS')
    print('connector_orbit_size=12')
    print('k2_parent_full_deficiency=17')
    print('k2_child_ranks=14,14')
    print('children_connected=true')
    print('binary_congruence_classes=singleton')
    print('common_model_satisfies_both=true')
    print('forward_transport_support=10')
    print('general_support_lower_bound=k_proved_symbolically')
    print('TRUMP_finished=false')
    print('SAT_IN_P=NOT_PROVED')
    print('P_VS_NP=OPEN')

if __name__=='__main__': main()
