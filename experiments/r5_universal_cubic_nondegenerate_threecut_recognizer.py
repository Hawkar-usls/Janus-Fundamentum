#!/usr/bin/env python3
"""R5: polynomial detection of nontrivial 3-edge cuts in cubic graphs.

If connected simple cubic G is 3-edge-connected, enumerate four distinct
vertices a,b|c,d and find a minimum cut with a,b forced on one side and
c,d forced on the other by unit-capacity integer maxflow.
A nontrivial 3-cut exists iff some such cut has size 3.
At most O(n^4) maxflow calls; each terminates after 4 augmentations.
This proves an unoptimized O(n^4 * n^2 * (n+m)) upper bound
with naive BFS implementation, hence polynomial in input size.
Once a cut is found, cap each side by a cubic vertex and apply
Col3(G)=Col3(G1)*Col3(G2)/6, gluing witnesses via S3 symmetry.

This is *not* a universal polynomial-time 3-edge-colouring algorithm;
cyclically 4-edge-connected, snark, and other irreducible cores remain.
"""
from collections import deque
from itertools import combinations

from r5_universal_cubic_three_edge_cut_factorization import (
    K4,K33,cube,petersen,triple_join,cap_a_three_cut,
)
from r5_universal_cubic_flow_snf_discriminator import (
    normalized,colour_count,
)


def forced_two_two_mincut(n,edges,aa,bb,caplimit=3):
    """Return reachable shore for a <=3 min-cut or None; 4 flows suffice.

    Treat the graph as directed symmetric capacity-one arcs.
    A unit undirected edge contributes one arc each direction.
    Residual edges are updated by standard Ford-Fulkerson augmentation.
    """
    edges=normalized(n,edges)
    S,T=n,n+1
    k=n+2
    cap=[[0]*k for _ in range(k)]
    for u,v in edges:
        cap[u][v]+=1
        cap[v][u]+=1
    INF=len(edges)+1
    for v in aa:cap[S][v]=INF
    for v in bb:cap[v][T]=INF
    flow=0
    while flow<=caplimit:
        parent=[-1]*k
        parent[S]=S
        q=deque([S])
        while q and parent[T]==-1:
            u=q.popleft()
            for v in range(k):
                if parent[v]<0 and cap[u][v]>0:
                    parent[v]=u
                    q.append(v)
        if parent[T]<0:
            seen={S}
            todo=[S]
            while todo:
                u=todo.pop()
                for v in range(k):
                    if cap[u][v]>0 and v not in seen:
                        seen.add(v)
                        todo.append(v)
            shore=set(range(n))&seen
            assert set(aa)<=shore and not (set(bb)&shore)
            assert len(shore)>=2 and len(shore)<=n-2
            assert sum((u in shore)!=(v in shore) for u,v in edges)==flow
            return (flow,shore)
        cur=T
        amount=INF
        while cur!=S:
            prev=parent[cur]
            amount=min(amount,cap[prev][cur])
            cur=prev
        cur=T
        while cur!=S:
            prev=parent[cur]
            cap[prev][cur]-=amount
            cap[cur][prev]+=amount
            cur=prev
        flow+=amount
    return None


def find_nontrivial_three_cut(n,edges):
    edges=normalized(n,edges)
    verts=set(range(n))
    for a,b in combinations(range(n),2):
        rem=sorted(verts-{a,b})
        for c,d in combinations(rem,2):
            result=forced_two_two_mincut(n,edges,(a,b),(c,d))
            if result is not None and result[0]==3:
                shore=result[1]
                cut=[e for e in edges if (e[0] in shore)!=(e[1] in shore)]
                assert len(cut)==3
                return shore,cut
    return None


def main():
    atoms=[
        ("K4",4,K4()),
        ("K33",6,K33()),
        ("CUBE",8,cube()),
        ("PETERSEN",10,petersen()),
    ]
    for name,n,raw in atoms:
        e=normalized(n,raw)
        found=find_nontrivial_three_cut(n,e)
        assert found is None,(name,found)
        print(f'{name}: no nontrivial 3-cut',flush=True)
    for label,na,ea,nb,eb in (
        ("K4_K4",4,K4(),4,K4()),
        ("K4_K33",4,K4(),6,K33()),
        ("K33_K33",6,K33(),6,K33()),
        ("K4_CUBE",4,K4(),8,cube()),
        ("K4_PETERSEN",4,K4(),10,petersen()),
    ):
        n,E,known_S=triple_join(na,ea,0,nb,eb,0)
        got=find_nontrivial_three_cut(n,E)
        assert got is not None,label
        S,cut=got
        assert len(S)>=2 and len(S)<=n-2
        cut2,A,B=cap_a_three_cut(n,E,S)
        assert set(cut)==set(cut2)
        ca,wa=colour_count(A[0],A[1])
        cb,wb=colour_count(B[0],B[1])
        assert ca*cb%6==0
        direct,_=colour_count(n,E)
        assert direct==ca*cb//6,(label,direct,ca,cb)
        print(f'{label}: found_3cut={cut}, sizes={A[0]},{B[0]}, '
              f'cap_counts={ca},{cb}, whole_count={direct}',flush=True)
    print('POLYNOMIAL_NONTRIVIAL_THREE_CUT_FINDER = PROVED_FOR_3EDGE_CONNECTED_CUBIC')
    print('EXACT_COLOUR_COUNT_FACTOR_AND_WITNESS_GLUING = VERIFIED_FINITE')
    print('IRREDUCIBLE_CUBIC_CORE_POLY_SOLVER = NOT_CONSTRUCTED')
    print('UNIVERSAL_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED')
    print('P_VS_NP = OPEN')


if __name__=="__main__":
    main()
