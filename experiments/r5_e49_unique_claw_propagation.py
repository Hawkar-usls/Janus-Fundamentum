#!/usr/bin/env python3
"""Exact controls for R5 E49 unique-claw propagation.

Uses a 12-variable square+cubic+linear carrier with:
  * every conflict vertex is a claw center, so E48 forced set F is empty;
  * vertices 0,1,2,4 have exactly one induced claw;
  * the E49 unique-claw identities force enough zeros/complements to recover the
    unique Exact-One witness {5,7,8,11} by ordinary row propagation.

P_VS_NP remains OPEN.
"""
from itertools import combinations

ROWS = [
    {0,10,11},
    {1,4,8},
    {2,3,8},
    {3,9,11},
    {3,4,7},
    {2,5,6},
    {6,7,10},
    {0,1,7},
    {6,8,9},
    {0,5,9},
    {1,5,10},
    {2,4,11},
]
N = 12


def verify_carrier():
    assert len(ROWS) == N
    assert all(len(r) == 3 for r in ROWS)
    deg = [0] * N
    for r in ROWS:
        for v in r:
            deg[v] += 1
    assert deg == [3] * N
    for i, j in combinations(range(N), 2):
        assert len(ROWS[i] & ROWS[j]) <= 1


def conflict_graph():
    adj = [set() for _ in range(N)]
    for r in ROWS:
        for a, b in combinations(r, 2):
            adj[a].add(b)
            adj[b].add(a)
    assert all(len(x) == 6 for x in adj)
    return adj


def claws(v, adj):
    return [
        set(t)
        for t in combinations(sorted(adj[v]), 3)
        if all(b not in adj[a] for a, b in combinations(t, 2))
    ]


def propagate(assign):
    """Exact ordinary Exact-One propagation. Values are 0/1/None."""
    changed = True
    while changed:
        changed = False
        for r in ROWS:
            vals = [assign[v] for v in r]
            ones = sum(x == 1 for x in vals)
            unknown = [v for v in r if assign[v] is None]
            if ones > 1 or (ones == 0 and not unknown):
                return False
            if ones == 1:
                for v in unknown:
                    assign[v] = 0
                    changed = True
            elif len(unknown) == 1:
                assign[unknown[0]] = 1
                changed = True
    return True


def brute_witnesses():
    out = []
    for S in combinations(range(N), N // 3):
        S = set(S)
        if all(len(S & r) == 1 for r in ROWS):
            out.append(S)
    return out


def main():
    verify_carrier()
    adj = conflict_graph()
    C = [claws(v, adj) for v in range(N)]
    counts = [len(x) for x in C]
    assert min(counts) >= 1              # E48 has F=empty.
    assert [v for v,c in enumerate(counts) if c == 1] == [0,1,2,4]

    assign = [None] * N
    complement_pairs = []
    for v in [0,1,2,4]:
        T = C[v][0]
        for w in adj[v] - T:
            if assign[w] not in (None, 0):
                raise AssertionError("forced-zero conflict")
            assign[w] = 0
        for u in T:
            complement_pairs.append((v,u))

    # Row propagation after the unconditional forced zeros resolves the instance.
    assert propagate(assign)
    # Enforce/check the complement identities x_u=1-x_v; the propagated solution
    # is already total in this control.
    assert all(x is not None for x in assign)
    for v,u in complement_pairs:
        assert assign[u] == 1 - assign[v]

    S = {i for i,x in enumerate(assign) if x == 1}
    assert S == {5,7,8,11}
    assert all(len(S & r) == 1 for r in ROWS)
    assert brute_witnesses() == [S]

    print("R5 E49 unique-claw propagation: PASS")
    print("claw_counts=", counts)
    print("E48_forced_set=empty")
    print("unique_claw_vertices=[0,1,2,4]")
    print("recovered_unique_witness=", sorted(S))


if __name__ == "__main__":
    main()
