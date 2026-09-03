#!/usr/bin/env python3
from itertools import permutations, product
from collections import defaultdict

BASE=[[2,3,-4],[-1,2,4],[-2,-5,-6],[1,-3,-4],[1,-5,6],[-3,5,-6],[-2,3,6],[-1,4,5]]
PIVOT=2; LOCAL=[1,3,4,5,6]
PI0_LOCAL={1:-3,3:-5,4:6,5:-1,6:-4}

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
            z=PI0_LOCAL[v]; g[m[v]]=(1 if z>0 else -1)*m[abs(z)]
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
    k=r*r; maps=[block_map(i) for i in range(k)]; F=[]; gp=gpi(maps)
    for m in maps: F.extend(rename(C,m) for C in BASE)
    for u,v in grid_edges(r): F.extend(orbit([maps[u][1],-maps[v][3],maps[u][4]],gp))
    return simplify(F,PIVOT,False), simplify(F,PIVOT,True), maps, gp

def joint_binary_components(A,B):
    V=sorted(vars_of(A)|vars_of(B)); adj={v:set() for v in V}
    for F in (A,B):
        for C in F:
            if len(C)==2:
                u,v=map(abs,C); adj[u].add(v); adj[v].add(u)
    comps=[]; seen=set()
    for s in V:
        if s in seen: continue
        stack=[s]; comp=set()
        while stack:
            u=stack.pop()
            if u in seen: continue
            seen.add(u); comp.add(u); stack.extend(adj[u]-seen)
        comps.append(frozenset(comp))
    return sorted(comps,key=lambda c:min(c))

def clauses_inside(F,comp): return [C for C in F if set(map(abs,C)).issubset(comp)]
def pi_clause(C,pi): return {pi[abs(l)] if l>0 else -pi[abs(l)] for l in C}
def transport_valid(target,source,pi):
    src=[set(C) for C in source]
    return all(any(D.issubset(pi_clause(C,pi)) for D in src) for C in target)
def local_domain(A,B,comp):
    T=clauses_inside(A,comp); S=clauses_inside(B,comp); vs=sorted(comp); out=[]
    for perm in permutations(vs):
        rho=dict(zip(vs,perm))
        for signs in product([1,-1],repeat=len(vs)):
            pi={v:s*rho[v] for v,s in zip(vs,signs)}
            if transport_valid(T,S,pi): out.append(pi)
    return out

def cross_groups(F,comps):
    owner={v:i for i,c in enumerate(comps) for v in c}; groups=defaultdict(list)
    for C in F:
        ids=sorted({owner[abs(l)] for l in C})
        if len(ids)>=2: groups[tuple(ids)].append(C)
    return groups

def combine_maps(p,q): return {**p,**q}
def edge_compatible(target_clauses,source_clauses,p,q):
    return transport_valid(target_clauses,source_clauses,combine_maps(p,q))

def recover(A,B):
    comps=joint_binary_components(A,B)
    assert all(len(c)==5 for c in comps)
    domains=[local_domain(A,B,c) for c in comps]
    assert all(len(d)==2 for d in domains)
    GA=cross_groups(A,comps); GB=cross_groups(B,comps)
    assert set(GA)==set(GB)
    allowed={}
    for e in GA:
        u,v=e
        pairs=[]
        for i,p in enumerate(domains[u]):
            for j,q in enumerate(domains[v]):
                if edge_compatible(GA[e],GB[e],p,q): pairs.append((i,j))
        allowed[e]=pairs
        assert len(pairs)==1
    # Every edge fixes one local candidate at each endpoint; connectedness makes it global.
    chosen={}
    for (u,v),pairs in allowed.items():
        i,j=pairs[0]
        assert u not in chosen or chosen[u]==i; chosen[u]=i
        assert v not in chosen or chosen[v]==j; chosen[v]=j
    assert len(chosen)==len(comps)
    gp={}
    for b,i in chosen.items(): gp.update(domains[b][i])
    assert transport_valid(A,B,gp)
    return comps,domains,allowed,gp

def main():
    for r in (2,3):
        A,B,maps,known=family(r)
        comps,domains,allowed,gp=recover(A,B)
        assert len(comps)==r*r
        assert len(allowed)==2*r*(r-1)
        assert all(len(v)==1 for v in allowed.values())
        assert gp==known
    print('R44CA EXACT REPLAY PASS')
    print('joint_binary_components=recover_exact_blocks')
    print('local_signed_transport_domain_size=2')
    print('edge_compatibility_relation_size=1')
    print('recovered_global_transport=known_pi_on_every_block')
    print('discovery=polynomial_constant_local_enumeration_plus_graph_propagation')
    print('TRUMP_finished=false')
    print('SAT_IN_P=NOT_PROVED')
    print('P_VS_NP=OPEN')

if __name__=='__main__': main()
