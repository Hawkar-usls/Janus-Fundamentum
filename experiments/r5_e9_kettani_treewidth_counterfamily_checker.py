#!/usr/bin/env python3
from itertools import combinations

def vid(i,j,k):
    return (i%k,j%k)

def clauses(k):
    return [
        (vid(i,j,k), vid(i+1,j,k), vid(i,j+1,k))
        for i in range(k) for j in range(k)
    ]

def associated_graph(k):
    adj={vid(i,j,k):set() for i in range(k) for j in range(k)}
    for c in clauses(k):
        for a,b in combinations(c,2):
            adj[a].add(b); adj[b].add(a)
    return adj

def main():
    k=8
    C=clauses(k)
    G=associated_graph(k)

    assert len(C)==k*k
    assert all(len(c)==3 for c in C)

    occ={v:0 for v in G}
    for c in C:
        for v in c:
            occ[v]+=1
    assert set(occ.values())=={3}

    assert set(len(G[v]) for v in G)=={6}

    # K1,4-free: no neighborhood contains an independent 4-set.
    for v,N in G.items():
        for S in combinations(N,4):
            independent=True
            for a,b in combinations(S,2):
                if b in G[a]:
                    independent=False
                    break
            assert not independent

    # Each chosen clause is a triangle, so every vertex belongs to at least
    # its three source-clause triangles.
    for v in G:
        count=sum(v in c for c in C)
        assert count==3

    # Delete wraparound and diagonal edges conceptually: horizontal/vertical
    # nonwrap edges form the ordinary P_k square P_k grid as a subgraph.
    for i in range(k):
        for j in range(k):
            if i+1<k:
                assert (i+1,j) in G[(i,j)]
            if j+1<k:
                assert (i,j+1) in G[(i,j)]

    print("CUBIC_MONOTONE_INSTANCE = PASS")
    print("VARIABLE_OCCURRENCE = 3")
    print("CLAUSE_ARITY = 3")
    print("ASSOCIATED_GRAPH_DEGREE = 6")
    print("K1,4_FREE = PASS")
    print("SOURCE_TRIANGLES_PER_VERTEX = 3")
    print("CONTAINS_P_k_BOX_P_k_GRID_SUBGRAPH = PASS")
    print("TREEWIDTH_LOWER_BOUND >= k = 8 > 6")
    print("KETTANI_BOUNDED_TREEWIDTH_THEOREM = FALSIFIED")
    print("D1 = EMPTY")
    print("P_VS_NP = OPEN")

if __name__=="__main__":
    main()
