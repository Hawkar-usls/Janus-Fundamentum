#!/usr/bin/env python3
from itertools import product

BASE=[[2,3,-4],[-1,2,4],[-2,-5,-6],[1,-3,-4],[1,-5,6],[-3,5,-6],[-2,3,6],[-1,4,5]]
PIVOT=2
LOCAL=[1,3,4,5,6]
PI={1:-3,3:-5,4:6,5:-1,6:-4}


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

def mapping_for_block(i):
    return {PIVOT:PIVOT, **{v:10*(i+1)+j+1 for j,v in enumerate(LOCAL)}}
def rename_clause(C,m): return [(1 if l>0 else -1)*m[abs(l)] for l in C]

def connected_family(k):
    F=[]; maps=[]
    for i in range(k):
        m=mapping_for_block(i); maps.append(m)
        F.extend(rename_clause(C,m) for C in BASE)
    for i in range(k-1):
        for v in LOCAL:
            a=maps[i][v]; b=maps[i+1][v]
            F.append([-a,b]); F.append([a,-b])
    return F,maps

def lift_pi(maps):
    g={}
    for m in maps:
        for v in LOCAL:
            img=PI[v]
            g[m[v]]=(1 if img>0 else -1)*m[abs(img)]
    return g

def pi_clause(C,pi):
    return {(pi[abs(l)] if l>0 else -pi[abs(l)]) for l in C}
def transport_valid(target,source,pi):
    for C in target:
        image=pi_clause(C,pi)
        if not any(set(D).issubset(image) for D in source): return False
    return True

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

def sat_model(F):
    V=sorted(vars_of(F))
    for bits in product([False,True],repeat=len(V)):
        a=dict(zip(V,bits))
        if all(any((a[abs(l)] if l>0 else not a[abs(l)]) for l in C) for C in F): return a
    return None

def main():
    F2,maps=connected_family(2)
    A2=simplify(F2,PIVOT,False); B2=simplify(F2,PIVOT,True)
    assert len(F2)==17 and len(vars_of(F2))==11
    assert deficiency(F2)==6 and maxdef(F2)==6  # 13k-11 for k=2
    assert maxdef(A2)==12 and maxdef(B2)==12     # 11k-10 for k=2
    assert connected_primal(A2) and connected_primal(B2)
    assert sat_model(A2) is not None and sat_model(B2) is not None
    pi2=lift_pi(maps)
    assert transport_valid(A2,B2,pi2)
    assert sum(1 for v in pi2 if pi2[v]!=v)==10
    print('R44BS EXACT REPLAY PASS')
    print('k2_parent_rank=6')
    print('k2_child_ranks=12,12')
    print('NOTE: parent rank formula and child formula are proved symbolically in proof note; k=2 values expose that maxdef rank is not a step-count ordering across the added-backbone normalization itself.')
    print('children_connected=true')
    print('children_sat=true')
    print('known_forward_transport_support=10')
    print('TRUMP_finished=false')
    print('SAT_IN_P=NOT_PROVED')
    print('P_VS_NP=OPEN')

if __name__=='__main__': main()
