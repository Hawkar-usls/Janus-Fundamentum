#!/usr/bin/env python3
from itertools import product

BASE=[[2,3,-4],[-1,2,4],[-2,-5,-6],[1,-3,-4],[1,-5,6],[-3,5,-6],[-2,3,6],[-1,4,5]]
PIVOT=2; LOCAL=[1,3,4,5,6]
PI={1:-3,3:-5,4:6,5:-1,6:-4}
COMMON={1:False,3:False,4:False,5:False,6:True}

def vars_of(F): return {abs(l) for C in F for l in C}
def simplify(F,v,val):
    sat=v if val else -v; false=-v if val else v; out=[]
    for C in F:
        if sat in C: continue
        out.append([l for l in C if l!=false])
    return out

def block_map(idx): return {PIVOT:PIVOT, **{v:10*(idx+1)+j+1 for j,v in enumerate(LOCAL)}}
def rename(C,m): return [(1 if l>0 else -1)*m[abs(l)] for l in C]
def gpi(maps):
    g={}
    for m in maps:
        for v in LOCAL:
            z=PI[v]; g[m[v]]=(1 if z>0 else -1)*m[abs(z)]
    return g

def image(C,g): return [(g[abs(l)] if l>0 else -g[abs(l)]) for l in C]
def canon(C): return tuple(sorted(set(C),key=lambda z:(abs(z),z)))
def orbit(seed,g):
    out=[]; seen=set(); cur=seed
    while canon(cur) not in seen:
        cc=canon(cur); seen.add(cc); out.append(list(cc)); cur=image(cur,g)
    return out

def grid_edges(r):
    out=[]
    for y in range(r):
        for x in range(r):
            u=y*r+x
            if x+1<r: out.append((u,u+1))
            if y+1<r: out.append((u,u+r))
    return out

def family(r):
    k=r*r; maps=[block_map(i) for i in range(k)]; F=[]
    for m in maps: F.extend(rename(C,m) for C in BASE)
    g=gpi(maps); con=[]
    for u,v in grid_edges(r):
        o=orbit([maps[u][1],-maps[v][3],maps[u][4]],g)
        assert len(o)==12; con.extend(o)
    return F+con,maps,g,con

def pi_clause(C,g): return set(image(C,g))
def transport(target,source,g):
    ss=[set(C) for C in source]
    return all(any(D.issubset(pi_clause(C,g)) for D in ss) for C in target)
def assignment(maps):
    a={}
    for m in maps:
        for v,b in COMMON.items(): a[m[v]]=b
    return a
def sat(F,a): return all(any(a[abs(l)] if l>0 else not a[abs(l)] for l in C) for C in F)
def binary_equivs(F):
    # exact implication-SCC check for variable equivalences only
    V=sorted(vars_of(F)); L=V+[-v for v in V]; adj={l:[] for l in L}; radj={l:[] for l in L}
    for C in F:
        if len(C)==2:
            a,b=C
            for u,v in [(-a,b),(-b,a)]: adj[u].append(v); radj[v].append(u)
    seen=set(); order=[]
    def dfs(u):
        seen.add(u)
        for v in adj[u]:
            if v not in seen: dfs(v)
        order.append(u)
    for l in L:
        if l not in seen: dfs(l)
    comp={}
    def rdfs(u,c):
        comp[u]=c
        for v in radj[u]:
            if v not in comp: rdfs(v,c)
    c=0
    for u in reversed(order):
        if u not in comp: rdfs(u,c); c+=1
    return [(u,v) for i,u in enumerate(V) for v in V[i+1:] if comp[u]==comp[v] or comp[u]==comp[-v]]

def main():
    for r in (2,3):
        F,maps,g,con=family(r); k=r*r; E=2*r*(r-1)
        assert len(con)==12*E==24*r*(r-1)
        assert len(F)==8*k+12*E
        assert len(vars_of(F))==5*k+1
        A=simplify(F,PIVOT,False); B=simplify(F,PIVOT,True)
        a=assignment(maps)
        assert sat(A,a) and sat(B,a)
        assert binary_equivs(A)==[] and binary_equivs(B)==[]
        assert transport(A,B,g)
        assert sum(g[v]!=v for v in g)==5*k
        # formula counts yield the symbolic full deficiencies
        assert len(F)-len(vars_of(F))==27*r*r-24*r-1
        assert len(A)-len(vars_of(A))==25*r*r-24*r
        assert len(B)-len(vars_of(B))==25*r*r-24*r
        assert len(grid_edges(r))==E
    print('R44BZ EXACT PREMISE REPLAY PASS')
    print('grid_connectors=12_per_grid_edge')
    print('parent_rank_formula=27r^2-24r-1 (criticality symbolic proof note)')
    print('child_rank_formula=25r^2-24r (upper-bound/full-deficiency proof note)')
    print('children_sat=true')
    print('binary_congruence_classes=singleton')
    print('known_transport_support=5r^2')
    print('grid_minor_certificate=one_connected_block_per_grid_vertex_and_cross_connector_per_grid_edge')
    print('TRUMP_finished=false')
    print('SAT_IN_P=NOT_PROVED')
    print('P_VS_NP=OPEN')

if __name__=='__main__': main()
