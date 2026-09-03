#!/usr/bin/env python3
from collections import Counter, defaultdict
from itertools import permutations, product

BASE=[[2,3,-4],[-1,2,4],[-2,-5,-6],[1,-3,-4],[1,-5,6],[-3,5,-6],[-2,3,6],[-1,4,5]]
PIVOT=2; LOCAL=[1,3,4,5,6]
# Construction-only generator. The recovery procedure below is not given it.
CONSTRUCTION_PI={1:-3,3:-5,4:6,5:-1,6:-4}


def canon(C): return tuple(sorted(set(C),key=lambda z:(abs(z),z)))
def vars_clause(C): return {abs(l) for l in C}
def vars_of(F): return {abs(l) for C in F for l in C}

def simplify(F,v,val):
    sat=v if val else -v; false=-sat; out=[]
    for C in F:
        if sat in C: continue
        out.append([l for l in C if l!=false])
    return out

def block_map(idx): return {PIVOT:PIVOT, **{v:10*(idx+1)+j+1 for j,v in enumerate(LOCAL)}}
def rename(C,m): return [(1 if l>0 else -1)*m[abs(l)] for l in C]
def renamed_pi(local_pi,m):
    out={}
    for v,img in local_pi.items():
        out[m[v]]=(1 if img>0 else -1)*m[abs(img)]
    return out

def construction_global_pi(maps):
    g={}
    for m in maps: g.update(renamed_pi(CONSTRUCTION_PI,m))
    return g

def apply_clause(C,pi):
    out=set()
    for l in C:
        z=pi[abs(l)]; out.add(z if l>0 else -z)
    return out

def orbit(seed,g):
    out=[]; seen=set(); cur=seed
    while canon(cur) not in seen:
        cc=canon(cur); seen.add(cc); out.append(list(cc))
        cur=[(g[abs(l)] if l>0 else -g[abs(l)]) for l in cur]
    return out

def grid_edges(r):
    out=[]
    for y in range(r):
        for x in range(r):
            u=y*r+x
            if x+1<r: out.append((u,u+1))
            if y+1<r: out.append((u,u+r))
    return out

def grid_family(r):
    k=r*r; maps=[block_map(i) for i in range(k)]; F=[]
    for m in maps: F.extend(rename(C,m) for C in BASE)
    g=construction_global_pi(maps)
    for u,v in grid_edges(r):
        o=orbit([maps[u][1],-maps[v][3],maps[u][4]],g)
        assert len(o)==12; F.extend(o)
    return F


def max_matching_size(F):
    match={}
    def aug(ci,seen):
        for v in vars_clause(F[ci]):
            if v in seen: continue
            seen.add(v)
            if v not in match or aug(match[v],seen):
                match[v]=ci; return True
        return False
    total=0
    for ci in range(len(F)):
        if aug(ci,set()): total+=1
    return total

def maxdef(F): return len(F)-max_matching_size(F)


def symdiff(A,B):
    a=Counter(canon(C) for C in A); b=Counter(canon(C) for C in B); out=[]
    for C in set(a)|set(b):
        out.extend([list(C)]*abs(a[C]-b[C]))
    return out

def recover_blocks(A,B,bound=5):
    D=symdiff(A,B); V=vars_of(A)|vars_of(B); adj={v:set() for v in V}; touched=set()
    for C in D:
        vs=list(vars_clause(C)); touched.update(vs)
        for i,u in enumerate(vs):
            for w in vs[i+1:]: adj[u].add(w); adj[w].add(u)
    if touched!=V: return None,D
    comps=[]; seen=set()
    for s in sorted(V):
        if s in seen: continue
        stack=[s]; comp=set()
        while stack:
            u=stack.pop()
            if u in comp: continue
            comp.add(u); seen.add(u); stack.extend(adj[u]-comp)
        if len(comp)>bound: return None,D
        comps.append(frozenset(comp))
    return comps,D

def taut(image): return any(-l in image for l in image)
def transport_clause_ok(C,pi,source_sets):
    im=apply_clause(C,pi)
    return taut(im) or any(D.issubset(im) for D in source_sets)
def signed_maps(block):
    B=tuple(sorted(block))
    for perm in permutations(B):
        for signs in product((1,-1),repeat=len(B)):
            yield {v:s*w for v,w,s in zip(B,perm,signs)}
def local_candidates(target,source,block):
    T=[C for C in target if vars_clause(C).issubset(block)]
    S=[set(C) for C in source if vars_clause(C).issubset(block)]
    return [pi for pi in signed_maps(block) if all(transport_clause_ok(C,pi,S) for C in T)]

def interaction_constraints(target,blocks):
    owner={v:i for i,B in enumerate(blocks) for v in B}
    edge_clauses=defaultdict(list)
    for C in target:
        ids=tuple(sorted({owner[abs(l)] for l in C}))
        if len(ids)<=1: continue
        if len(ids)!=2: return None
        edge_clauses[ids].append(C)
    return edge_clauses

# 2-SAT utilities. Literal is (variable_index, required_boolean_value).
def solve_2sat(n,clauses):
    N=2*n; adj=[[] for _ in range(N)]; radj=[[] for _ in range(N)]
    def node(v,val): return 2*v+(1 if val else 0)
    def add_imp(a,b):
        u=node(*a); v=node(*b); adj[u].append(v); radj[v].append(u)
    def neg(l): return (l[0],not l[1])
    for c in clauses:
        if len(c)==1:
            a=c[0]; add_imp(neg(a),a)
        else:
            a,b=c; add_imp(neg(a),b); add_imp(neg(b),a)
    seen=set(); order=[]
    def dfs(u):
        seen.add(u)
        for v in adj[u]:
            if v not in seen: dfs(v)
        order.append(u)
    for u in range(N):
        if u not in seen: dfs(u)
    comp=[-1]*N
    def rdfs(u,c):
        comp[u]=c
        for v in radj[u]:
            if comp[v]<0: rdfs(v,c)
    c=0
    for u in reversed(order):
        if comp[u]<0: rdfs(u,c); c+=1
    ans=[False]*n
    for v in range(n):
        if comp[node(v,False)]==comp[node(v,True)]: return None
        ans[v]=comp[node(v,True)]>comp[node(v,False)]
    return ans

def recover_boolean_block_transport(target,source):
    blocks,D=recover_blocks(target,source,5)
    if blocks is None: return None,{"reason":"bad_blocks"}
    cands=[local_candidates(target,source,B) for B in blocks]
    if any(len(C)==0 or len(C)>2 for C in cands): return None,{"reason":"domain_not_boolean","counts":[len(C) for C in cands]}
    edges=interaction_constraints(target,blocks)
    if edges is None: return None,{"reason":"nonbinary_interaction"}
    source_sets=[set(C) for C in source]
    cnf=[]
    # Boolean False indexes candidate 0; True indexes candidate 1.
    for i,C in enumerate(cands):
        if len(C)==1: cnf.append([(i,False)])
    for (i,j),clauses_ij in edges.items():
        for ai,pi in enumerate(cands[i]):
            for bj,pj in enumerate(cands[j]):
                merged=dict(pi); merged.update(pj)
                ok=all(transport_clause_ok(C,merged,source_sets) for C in clauses_ij)
                if not ok:
                    # forbid Xi=bool(ai), Xj=bool(bj)
                    cnf.append([(i, ai==0),(j, bj==0)])
    assignment=solve_2sat(len(blocks),cnf)
    if assignment is None: return None,{"reason":"compatibility_unsat"}
    pi={}
    for i,B in enumerate(blocks):
        idx=1 if assignment[i] and len(cands[i])==2 else 0
        pi.update(cands[i][idx])
    if not all(transport_clause_ok(C,pi,source_sets) for C in target):
        raise AssertionError('global transport verification failed')
    return pi,{"blocks":len(blocks),"sizes":[len(B) for B in blocks],"counts":[len(C) for C in cands],"edges":len(edges),"symdiff":len(D)}


def main():
    for r in (2,3):
        parent=grid_family(r); k=r*r
        A=simplify(parent,PIVOT,False); B=simplify(parent,PIVOT,True)
        found,info=recover_boolean_block_transport(A,B) # source B -> target A
        assert found is not None
        assert info['blocks']==k and info['sizes']==[5]*k
        assert set(info['counts'])=={2}
        assert info['edges']==len(grid_edges(r))
        assert info['symdiff']==4*k
        assert sum(found[v]!=v for v in found)==5*k
        assert maxdef(parent)==27*r*r-24*r-1
        assert maxdef(A)==25*r*r-24*r
        assert maxdef(B)==25*r*r-24*r
        assert maxdef(parent)-maxdef(A)==2*r*r-1

    print('R44CA EXACT RECOVERY REPLAY PASS')
    print('symdiff_block_size=5')
    print('local_valid_candidate_count=2')
    print('compatibility_solver=2SAT')
    print('interaction_treewidth_requirement=NONE')
    print('grid_r2_r3_recovered_without_supplied_generator=true')
    print('recovered_support=5r^2')
    print('rank_drop=2r^2-1')
    print('TRUMP_finished=false')
    print('SAT_IN_P=NOT_PROVED')
    print('P_VS_NP=OPEN')

if __name__=='__main__': main()
