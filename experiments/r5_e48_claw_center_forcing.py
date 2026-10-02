#!/usr/bin/env python3
"""Exact finite controls for R5 E48 claw-center forcing.

Checks two square+cubic+linear carriers:
1) a 9-variable SAT control where the three non-claw-centers are exactly the
   unique displayed Exact-One witness {0,5,7};
2) the 7-variable Fano carrier where every vertex is a non-claw-center, so the
   E48 count obstruction immediately proves UNSAT.

P_VS_NP remains OPEN.
"""

from itertools import combinations


def incidence(rows, n):
    A = [[0] * n for _ in rows]
    for r, T in enumerate(rows):
        for v in T:
            A[r][v] = 1
    return A


def audit(rows, n):
    A = incidence(rows, n)
    assert len(rows) == n
    assert all(len(T) == 3 for T in rows)
    assert all(sum(A[r][c] for r in range(n)) == 3 for c in range(n))
    assert all(len(rows[i] & rows[j]) <= 1 for i, j in combinations(range(n), 2))
    return A


def conflict(A):
    n = len(A[0])
    adj = [set() for _ in range(n)]
    for row in A:
        vs = [i for i, a in enumerate(row) if a]
        for u, v in combinations(vs, 2):
            adj[u].add(v)
            adj[v].add(u)
    return adj


def claw_witness(adj, v):
    for T in combinations(sorted(adj[v]), 3):
        if all(b not in adj[a] for a, b in combinations(T, 2)):
            return T
    return None


def non_claw_centers(adj):
    return {v for v in range(len(adj)) if claw_witness(adj, v) is None}


def exact_one(rows, S):
    return all(len(T & S) == 1 for T in rows)


def main():
    sat_rows = [
        {0, 3, 6},
        {1, 2, 5},
        {0, 2, 8},
        {2, 3, 7},
        {0, 1, 4},
        {4, 5, 6},
        {1, 6, 7},
        {4, 7, 8},
        {3, 5, 8},
    ]
    A = audit(sat_rows, 9)
    G = conflict(A)
    assert all(len(G[v]) == 6 for v in range(9))
    F = non_claw_centers(G)
    assert F == {0, 5, 7}
    assert len(F) == 9 // 3
    assert all(v not in G[u] for u, v in combinations(sorted(F), 2))
    assert exact_one(sat_rows, F)

    fano_rows = [
        {0, 1, 3},
        {0, 2, 5},
        {0, 4, 6},
        {1, 2, 6},
        {1, 4, 5},
        {2, 3, 4},
        {3, 5, 6},
    ]
    A7 = audit(fano_rows, 7)
    G7 = conflict(A7)
    F7 = non_claw_centers(G7)
    assert F7 == set(range(7))
    assert len(F7) > 7 / 3

    print("R5 E48 claw-center forcing controls: PASS")
    print("SAT control: n=9, forced non-claw set={0,5,7}, exactly n/3, and is a witness")
    print("UNSAT control: Fano n=7, all 7 vertices are non-claw-centers, exceeding n/3")


if __name__ == "__main__":
    main()
