#!/usr/bin/env python3
"""Exact controls for R5 E50 two-claw overlap propagation.

The 12-variable carrier below is square+cubic+linear and has no zero-claw or
unique-claw vertices, so E48/E49 do not fire. Several vertices have exactly two
claws with nonempty overlap. E50 forces unconditional zeros from the complement of
the union; ordinary Exact-One propagation then proves UNSAT.

P_VS_NP remains OPEN.
"""
from itertools import combinations

ROWS = [
    {0,1,11},
    {1,7,9},
    {2,6,10},
    {3,4,8},
    {1,2,4},
    {5,10,11},
    {0,6,9},
    {2,7,8},
    {0,5,8},
    {3,5,9},
    {3,7,10},
    {4,6,11},
]
N = 12


def verify_carrier():
    assert len(ROWS) == N
    assert all(len(r) == 3 for r in ROWS)
    deg = [0]*N
    for r in ROWS:
        for v in r:
            deg[v] += 1
    assert deg == [3]*N
    for i,j in combinations(range(N),2):
        assert len(ROWS[i] & ROWS[j]) <= 1


def conflict_graph():
    adj=[set() for _ in range(N)]
    for r in ROWS:
        for a,b in combinations(r,2):
            adj[a].add(b); adj[b].add(a)
    assert all(len(a)==6 for a in adj)
    return adj


def claws(v,adj):
    return [set(t) for t in combinations(sorted(adj[v]),3)
            if all(b not in adj[a] for a,b in combinations(t,2))]


def propagate(assign):
    changed=True
    while changed:
        changed=False
        for r in ROWS:
            ones=sum(assign[v] == 1 for v in r)
            unk=[v for v in r if assign[v] is None]
            if ones>1 or (ones==0 and not unk):
                return False
            if ones==1:
                for v in unk:
                    assign[v]=0; changed=True
            elif len(unk)==1:
                assign[unk[0]]=1; changed=True
    return True


def main():
    verify_carrier()
    adj=conflict_graph()
    C=[claws(v,adj) for v in range(N)]
    counts=[len(c) for c in C]
    assert min(counts) >= 2  # E48/E49 are inactive.
    assert counts == [3,2,2,3,3,2,3,2,3,3,2,2]

    assign=[None]*N
    overlap_vertices=[]
    for v,c in enumerate(C):
        if len(c)==2 and (c[0] & c[1]):
            overlap_vertices.append(v)
            I=c[0] & c[1]
            Z=adj[v] - (c[0] | c[1])
            assert I and Z
            for w in Z:
                assign[w]=0

    assert overlap_vertices == [2,5,7]
    # The unconditional E50 zeros already make ordinary row propagation refute.
    assert not propagate(assign)

    print("R5 E50 two-claw overlap propagation: PASS")
    print("claw_counts=", counts)
    print("zero_or_unique_claw_vertices=none")
    print("overlap_two_claw_vertices=", overlap_vertices)
    print("E50_forced_zeros_then_row_propagation => UNSAT")


if __name__ == "__main__":
    main()
