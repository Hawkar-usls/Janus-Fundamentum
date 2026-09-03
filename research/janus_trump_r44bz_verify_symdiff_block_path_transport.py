#!/usr/bin/env python3
from collections import Counter, defaultdict
from itertools import permutations, product

BASE = [
    [2,3,-4],[-1,2,4],[-2,-5,-6],[1,-3,-4],
    [1,-5,6],[-3,5,-6],[-2,3,6],[-1,4,5]
]
PIVOT = 2
LOCAL = [1,3,4,5,6]
# Used only to CONSTRUCT the test family. Recovery below never receives PI.
CONSTRUCTION_PI = {1:-3,3:-5,4:6,5:-1,6:-4}


def canon_clause(C):
    return tuple(sorted(set(C), key=lambda z:(abs(z), z)))


def vars_of(F):
    return {abs(l) for C in F for l in C}


def simplify(F, v, val):
    sat = v if val else -v
    false = -sat
    out = []
    for C in F:
        if sat in C:
            continue
        out.append([l for l in C if l != false])
    return out


def map_block(i):
    return {PIVOT:PIVOT, **{v:10*(i+1)+j+1 for j,v in enumerate(LOCAL)}}


def rename_clause(C, m):
    return [(1 if l>0 else -1)*m[abs(l)] for l in C]


def raw_parent(k):
    F=[]; maps=[]
    for i in range(k):
        m=map_block(i); maps.append(m)
        F.extend(rename_clause(C,m) for C in BASE)
    return F,maps


def construction_global_pi(maps):
    g={}
    for m in maps:
        for v in LOCAL:
            img=CONSTRUCTION_PI[v]
            g[m[v]]=(1 if img>0 else -1)*m[abs(img)]
    return g


def apply_lit(lit, pi):
    image=pi[abs(lit)]
    return image if lit>0 else -image


def apply_clause(C, pi):
    image={apply_lit(l,pi) for l in C}
    return image


def connector_orbit(m1,m2,g):
    seed=[m1[1],-m2[3],m1[4]]
    out=[]; seen=set(); cur=seed
    while canon_clause(cur) not in seen:
        cc=canon_clause(cur); seen.add(cc); out.append(list(cc))
        cur=[apply_lit(l,g) for l in cur]
    return out


def orbit_parent(k):
    F,maps=raw_parent(k); g=construction_global_pi(maps)
    for i in range(k-1):
        orb=connector_orbit(maps[i],maps[i+1],g)
        assert len(orb)==12
        F.extend(orb)
    return F


def max_matching_size(F):
    match={}
    def aug(ci, seen):
        for v in {abs(l) for l in F[ci]}:
            if v in seen: continue
            seen.add(v)
            if v not in match or aug(match[v], seen):
                match[v]=ci
                return True
        return False
    ans=0
    for ci in range(len(F)):
        if aug(ci,set()): ans+=1
    return ans


def maxdef(F):
    return len(F)-max_matching_size(F)


def symmetric_difference_clauses(A,B):
    ca=Counter(canon_clause(C) for C in A)
    cb=Counter(canon_clause(C) for C in B)
    out=[]
    for C in set(ca)|set(cb):
        for _ in range(abs(ca[C]-cb[C])):
            out.append(list(C))
    return out


def symdiff_components(A,B):
    D=symmetric_difference_clauses(A,B)
    V=vars_of(A)|vars_of(B)
    adj={v:set() for v in V}
    touched=set()
    for C in D:
        vs=sorted({abs(l) for l in C})
        touched.update(vs)
        for i,u in enumerate(vs):
            for w in vs[i+1:]:
                adj[u].add(w); adj[w].add(u)
    if touched != V:
        return None, D
    comps=[]; seen=set()
    for s in sorted(V):
        if s in seen: continue
        stack=[s]; comp=set()
        while stack:
            u=stack.pop()
            if u in comp: continue
            comp.add(u); seen.add(u); stack.extend(adj[u]-comp)
        comps.append(frozenset(comp))
    return comps,D


def tautological(image):
    return any(-l in image for l in image)


def clause_transport_ok(C, pi, source_sets):
    image=apply_clause(C,pi)
    if tautological(image): return True
    return any(D.issubset(image) for D in source_sets)


def signed_maps_on_block(block):
    block=tuple(sorted(block))
    for perm in permutations(block):
        for signs in product((1,-1), repeat=len(block)):
            yield {v:s*w for v,w,s in zip(block,perm,signs)}


def local_candidates(target,source,block):
    target_local=[C for C in target if vars_of([C]).issubset(block)]
    source_local=[set(C) for C in source if vars_of([C]).issubset(block)]
    out=[]
    for pi in signed_maps_on_block(block):
        if all(clause_transport_ok(C,pi,source_local) for C in target_local):
            out.append(pi)
    return out


def interaction_path(target,blocks):
    owner={v:i for i,B in enumerate(blocks) for v in B}
    edge_clauses=defaultdict(list)
    adj={i:set() for i in range(len(blocks))}
    for C in target:
        ids=sorted({owner[abs(l)] for l in C})
        if len(ids)<=1: continue
        if len(ids)!=2: return None,None,None
        e=tuple(ids)
        edge_clauses[e].append(C)
        adj[e[0]].add(e[1]); adj[e[1]].add(e[0])
    if len(blocks)==1:
        return [0],edge_clauses,owner
    if any(len(adj[i])>2 or len(adj[i])==0 for i in adj): return None,None,None
    if sum(len(x) for x in adj.values())//2 != len(blocks)-1: return None,None,None
    ends=[i for i in adj if len(adj[i])==1]
    if len(ends)!=2: return None,None,None
    order=[]; prev=None; cur=min(ends)
    while True:
        order.append(cur)
        nxt=[x for x in adj[cur] if x!=prev]
        if not nxt: break
        prev,cur=cur,nxt[0]
    if len(order)!=len(blocks): return None,None,None
    return order,edge_clauses,owner


def pair_compatible(target_cross, pi1, pi2, source_sets):
    pi=dict(pi1); pi.update(pi2)
    return all(clause_transport_ok(C,pi,source_sets) for C in target_cross)


def recover_block_path_transport(target,source,b=5):
    blocks,D=symdiff_components(target,source)
    if blocks is None or any(len(B)>b for B in blocks):
        return None,{"reason":"bad_symdiff_components"}
    order,edge_clauses,owner=interaction_path(target,blocks)
    if order is None:
        return None,{"reason":"interaction_not_path"}
    cands={i:local_candidates(target,source,blocks[i]) for i in range(len(blocks))}
    if any(not cands[i] for i in cands):
        return None,{"reason":"empty_local_candidate_set"}
    source_sets=[set(C) for C in source]
    parents={}
    reachable={j:None for j in range(len(cands[order[0]]))}
    for pos in range(1,len(order)):
        u=order[pos-1]; v=order[pos]
        e=tuple(sorted((u,v)))
        next_reach={}
        for j,pv in enumerate(cands[v]):
            for i in reachable:
                pu=cands[u][i]
                if pair_compatible(edge_clauses[e],pu,pv,source_sets):
                    next_reach[j]=i
                    parents[(pos,j)]=i
                    break
        if not next_reach:
            return None,{"reason":"path_dp_reject"}
        reachable=next_reach
    last=next(iter(reachable))
    choices=[None]*len(order); choices[-1]=last
    for pos in range(len(order)-1,0,-1):
        choices[pos-1]=parents[(pos,choices[pos])]
    pi={}
    for pos,bi in enumerate(order): pi.update(cands[bi][choices[pos]])
    if not all(clause_transport_ok(C,pi,source_sets) for C in target):
        raise AssertionError("assembled map failed global verification")
    info={
        "blocks":len(blocks),
        "block_sizes":[len(B) for B in blocks],
        "local_candidate_counts":[len(cands[i]) for i in range(len(blocks))],
        "interaction_order":order,
        "symdiff_clause_count":len(D),
    }
    return pi,info


def main():
    for k in (2,3,4):
        parent=orbit_parent(k)
        A=simplify(parent,PIVOT,False)
        B=simplify(parent,PIVOT,True)

        # Recovery is not given CONSTRUCTION_PI or block maps.
        found,info=recover_block_path_transport(A,B,b=5)  # source B -> target A
        assert found is not None
        assert info["blocks"]==k
        assert info["block_sizes"]==[5]*k
        assert info["symdiff_clause_count"]==4*k
        assert max(info["local_candidate_counts"]) <= 3840
        assert sum(found[v]!=v for v in found) >= k

        assert maxdef(parent)==15*k-13
        assert maxdef(A)==13*k-12
        assert maxdef(B)==13*k-12
        assert maxdef(parent)-maxdef(A)==2*k-1

    print("R44BZ EXACT RECOVERY REPLAY PASS")
    print("block_recovery=symmetric_difference_connected_components")
    print("block_size=5")
    print("local_search_bound=3840")
    print("interaction_graph=path")
    print("global_search=constant_state_path_DP")
    print("transport_generator_not_given_to_recovery=true")
    print("family_coverage=k2_k3_k4_replayed_general_proof_all_k")
    print("rank_drop=2k-1")
    print("TRUMP_finished=false")
    print("SAT_IN_P=NOT_PROVED")
    print("P_VS_NP=OPEN")


if __name__=='__main__':
    main()
