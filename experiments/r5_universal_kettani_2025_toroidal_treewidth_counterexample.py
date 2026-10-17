#!/usr/bin/env python3
"""Audited exact-class counterexample to a published tw<=6 P=NP claim.

External reference:
Omar Kettani, 'Cubic Monotone 1-in-3 SAT Problem is Polynomial Time
Solvable', IJMTT 71(9):36-46 (2025), Proposition 4, pages 39-40,
doi:10.14445/22315373/IJMTT-V71I9P105.

For each L>=9 divisible by three, form the *linear* cubic n=L^2
Exact-One carrier on Z_L^2 with checks
    (i,j), (i+1,j), (i,j+1).
Its conflict graph is 6-regular, induced-K1,4-free, every variable
is in >=3 triangles, but contains the ordinary LxL grid as a
subgraph and has treewidth >=L-1. This refutes the claimed
universal bound tw<=6 even on SAT members of the exact JANUS class.

The treewidth inequality is a mathematical bramble/Helly theorem,
not inferred from an empirical treewidth heuristic or SAT solver.
"""
from __future__ import annotations

from collections import Counter
from itertools import combinations


def ident(i,j,L):
    return (i%L)*L+(j%L)


def toroidal_triangular_carrier(L):
    assert L>=4
    return [
        tuple(sorted((
            ident(i,j,L),
            ident(i+1,j,L),
            ident(i,j+1,L),
        )))
        for i in range(L) for j in range(L)
    ]


def verified_conflict_graph(rows,L):
    n=L*L
    assert len(rows)==n
    assert len(set(rows))==n
    coldegree=Counter()
    edge_owner={}
    G=[set() for _ in range(n)]
    for ri,row in enumerate(rows):
        assert len(row)==3 and len(set(row))==3
        for v in row:
            coldegree[v]+=1
        for u,v in combinations(row,2):
            assert (u,v) not in edge_owner, (ri,edge_owner.get((u,v)),(u,v))
            edge_owner[(u,v)]=ri
            G[u].add(v)
            G[v].add(u)
    assert len(coldegree)==n and set(coldegree.values())=={3}
    assert len(edge_owner)==3*n
    assert all(len(x)==6 for x in G)

    # A variable is incident to precisely three clauses. Each clause
    # contributes an edge between a pair of its six distinct neighbors.
    # These three disjoint pairs cover N(v). Hence alpha(G[N(v)])<=3,
    # proving NO induced K_{1,4} at ANY center.
    incidences=[[] for _ in range(n)]
    for row in rows:
        for v in row:
            incidences[v].append(row)
    for v in range(n):
        assert len(incidences[v])==3
        neighbor_pairs=[
            set(row)-{v}
            for row in incidences[v]
        ]
        assert all(len(pair)==2 for pair in neighbor_pairs)
        assert len(set.union(*neighbor_pairs))==6
        assert set.union(*neighbor_pairs)==G[v]
        assert all(pair<=G[v] for pair in neighbor_pairs)
        # Three distinct clause triangles through v:
        assert len({frozenset(row) for row in incidences[v]})==3
    # Each underlying non-wrap grid edge is explicitly present.
    for i in range(L):
        for j in range(L):
            v=ident(i,j,L)
            if i+1<L:
                assert ident(i+1,j,L) in G[v]
            if j+1<L:
                assert ident(i,j+1,L) in G[v]

    # The conflict graph's LxL ordinary grid is connected, hence G is.
    reached={0}
    work=[0]
    while work:
        for w in G[work.pop()]:
            if w not in reached:
                reached.add(w)
                work.append(w)
    assert len(reached)==n
    return G


def verify_bramble_crosses(L):
    """Finite witness of the CROSS bramble for the grid subgraph.

    Cross(i,j) = (entire row i) union (entire column j).
    Any two crosses intersect (the vertex (i,j') lies in both).
    Every hitting set with <L vertices misses some row and some column,
    therefore misses their union cross. Cross family order >=L.
    Helly for subtrees of any tree decomposition => bag size >=L,
    so tw(conflict graph) >= L-1.

    Code checks construction/pairwise intersection and exhibits a
    size L hitting set, but does NOT use brute-force enumerations
    of all hitting sets or pretend to compute treewidth numerically.
    """
    crosses=[
        {ident(i,t,L) for t in range(L)}
        | {ident(t,j,L) for t in range(L)}
        for i in range(L) for j in range(L)
    ]
    assert len(crosses)==L*L
    assert all(len(c)==2*L-1 for c in crosses)
    assert all(not c.isdisjoint(d) for c,d in combinations(crosses,2))
    upper_hitting={ident(0,j,L) for j in range(L)}
    assert len(upper_hitting)==L
    assert all(upper_hitting&c for c in crosses)
    return L-1


def verify_sat_assignments(rows,L):
    assert L%3==0
    found=[]
    for phase in (0,1,2):
        x=[int((i-j-phase)%3==0) for i in range(L) for j in range(L)]
        assert sum(x)==L*L//3
        assert all(sum(x[v] for v in clause)==1 for clause in rows)
        found.append(tuple(x))
    assert len(set(found))==3



def bareiss_determinant(M):
    """Exact integer O(n^3) fraction-free elimination, tiny frozen fixture."""
    n=len(M)
    a=[list(map(int,row)) for row in M]
    assert all(len(row)==n for row in a)
    sign=1
    divisor=1
    for k in range(n-1):
        if not a[k][k]:
            pivot=next((i for i in range(k+1,n) if a[i][k]),None)
            if pivot is None:
                return 0
            a[k],a[pivot]=a[pivot],a[k]
            sign=-sign
        pivot=a[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                numerator=pivot*a[i][j]-a[i][k]*a[k][j]
                assert numerator%divisor==0
                a[i][j]=numerator//divisor
            a[i][k]=0
        divisor=pivot
    return sign*a[-1][-1]


def verify_invertible_nonboolean_counterexample():
    """Independent failure in paper's Algorithm 2 determinant shortcut.

    For EVERY square cubic A, A(1/3*1)=1. If det A !=0,
    it is the UNIQUE rational solution, which is NOT Boolean:
    contrary to the paper's Step 2 treating A^-1 1 as Exact-One.
    """
    n=9
    rows=[
        tuple(sorted((i,(i+1)%n,(i+3)%n)))
        for i in range(n)
    ]
    pairs=[tuple(sorted(p)) for row in rows for p in combinations(row,2)]
    assert len(set(pairs))==3*n
    assert all(sum(j in row for row in rows)==3 for j in range(n))
    assert all(len(row)==3 for row in rows)
    M=[[int(j in row) for j in range(n)] for row in rows]
    determinant=bareiss_determinant(M)
    assert determinant==27
    # The actual n=9 Exact-One problem is UNSAT: any Boolean solution
    # would equal the unique rational solution (1/3,...,1/3).
    assert all(sum(row)==3 for row in M)
    print(
        "Published Algorithm 2 Step 2 failure: n=9, circulant "
        "{0,1,3}; det(A)=27, unique rational solution "
        "x=(1/3)*1, Boolean SAT=FALSE"
    )

def main():
    verify_invertible_nonboolean_counterexample()
    for L in (9,12,15):
        rows=toroidal_triangular_carrier(L)
        G=verified_conflict_graph(rows,L)
        verify_sat_assignments(rows,L)
        lower=verify_bramble_crosses(L)
        assert lower>=8>6
        print(
            f"L={L} n={L*L} checked={len(rows)}: "
            "square/cubic/linear/connected; 6-regular; K1,4-free;"
            f" >=3 triangles/vertex; explicit 3 SAT witnesses; "
            f"tw(G)>={lower}>6"
        )
    print("PUBLISHED_TW_LE_6_FOR_ASSOCIATED_GRAPH = REFUTED")
    print("PUBLISHED_DET_NONZERO_IMPLICATION_OF_BOOLEAN_SAT = REFUTED")
    print("PUBLISHED_P_EQ_NP_PROOF_VIA_CONSTANT_TW = NOT_VALIDATED")
    print("THIS_IS_A_PROOF_AUDIT_NOT_A_PROOF_OF_P_NE_NP")
    print("JANUS_UNIVERSAL_SOLVER = NOT_CONSTRUCTED; P_VS_NP = OPEN")


if __name__=="__main__":
    main()
