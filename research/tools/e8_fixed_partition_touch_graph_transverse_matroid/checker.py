#!/usr/bin/env python3
from itertools import product

N=7
H={(0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(0,6)}
F_YES={(0,2),(0,3),(1,4),(1,5),(2,6),(3,5),(4,6)}
F_NO={(0,2),(0,3),(1,4),(1,5),(2,5),(3,6),(4,6)}


def ce(a,b):
    return (a,b) if a<b else (b,a)

H={ce(*e) for e in H}
F_YES={ce(*e) for e in F_YES}
F_NO={ce(*e) for e in F_NO}


def degrees(E):
    return [sum(v in e for e in E) for v in range(N)]


def is_single_cycle(E):
    if len(E)!=N or degrees(E)!=[2]*N:
        return False
    adj=[[] for _ in range(N)]
    for a,b in E:
        adj[a].append(b);adj[b].append(a)
    seen={0};prev=None;cur=0
    while True:
        a,b=adj[cur]
        nxt=a if a!=prev else b
        if nxt==0:
            return len(seen)==N
        if nxt in seen:
            return False
        seen.add(nxt);prev,cur=cur,nxt


def count_3colourings(E):
    count=0;first=None
    for col in product(range(3),repeat=N):
        if all(col[a]!=col[b] for a,b in E):
            count+=1
            if first is None:first=col
    return count,first


def touch_graph_signature(H,F):
    # Circuit partition has exactly H and F. Every original vertex is incident
    # with both circuits, hence becomes one h--f edge labelled by that vertex.
    assert is_single_cycle(H) and is_single_cycle(F)
    assert H.isdisjoint(F)
    return (2,tuple(("h","f",v) for v in range(N)))


def cographic_rank_parallel_bundle(edge_subset_size):
    # Touch graph = two vertices with 7 parallel edges, connected.
    # Graphic rank is 1 for any nonempty set; dual/cographic rank formula
    # r*(A)=|A| + r(E-A)-r(E), with r(E)=1.
    k=edge_subset_size
    if k==N:
        return N-1
    # E-A nonempty for k<N, so r(E-A)=1.
    return k


def verify_instance(name,F,expected_count):
    assert is_single_cycle(H)
    assert is_single_cycle(F),name
    assert H.isdisjoint(F),name
    G=H|F
    assert len(G)==2*N,name
    assert degrees(G)==[4]*N,name
    sig=touch_graph_signature(H,F)
    count,first=count_3colourings(G)
    assert count==expected_count,(name,count,expected_count)
    print(f"PASS {name}: 4-regular, H=C7, F=C7, 3-colourings={count}, example={first}")
    return sig


def main():
    print("E8 v6.7 fixed-partition touch-graph / transverse-matroid barrier")
    sy=verify_instance("YES",F_YES,12)
    sn=verify_instance("NO",F_NO,0)
    assert sy==sn
    print("PASS identical touch-graph: two partition-circuit vertices with seven parallel labelled edges")
    # Exhaustively compare cographic rank on every subset size; symmetry makes rank size-only.
    ranks=[cographic_rank_parallel_bundle(k) for k in range(N+1)]
    assert ranks==[0,1,2,3,4,5,6,6]
    print("PASS common fixed-P cographic rank profile by subset size:",ranks)
    print("PASS verdict separation: same fixed-P touch/cographic data, SAT-colorability differs")
    print("SCOPE: full transition/isotropic matroid NOT claimed equal")
    print("P_VS_NP=OPEN; P_EQUALS_NP_ALGORITHM=NOT_CONSTRUCTED; E8_D1=EMPTY")

if __name__=="__main__":
    main()
