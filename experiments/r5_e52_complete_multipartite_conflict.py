#!/usr/bin/env python3
"""Exact controls for R5 E52 complete-multipartite conflict rigidity.

Builds:
  * a 9-variable Latin-square carrier with conflict graph K_{3,3,3}; verifies
    square+cubic+linear, alpha=3=n/3, and witness one whole part;
  * the Fano 7-variable carrier with conflict graph K7 and alpha=1<7/3.

Also verifies that every vertex of K_{3,3,3} has exactly two claw triples, so this
SAT family lies beyond the E49 unique-claw regime.

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


def claw_count(adj, v):
    out = 0
    for T in combinations(sorted(adj[v]), 3):
        if all(b not in adj[a] for a, b in combinations(T, 2)):
            out += 1
    return out


def alpha_bruteforce(adj):
    n = len(adj)
    best = 0
    for mask in range(1 << n):
        if mask.bit_count() <= best:
            continue
        good = True
        for u in range(n):
            if not ((mask >> u) & 1):
                continue
            for v in adj[u]:
                if v > u and ((mask >> v) & 1):
                    good = False
                    break
            if not good:
                break
        if good:
            best = mask.bit_count()
    return best


def latin_k333_rows():
    # Parts A={0,1,2}, B={3,4,5}, C={6,7,8}; rows are the Z3 Latin square.
    rows = []
    for i in range(3):
        for j in range(3):
            rows.append({i, 3 + j, 6 + ((i + j) % 3)})
    return rows


def exact_one(rows, S):
    return all(len(T & S) == 1 for T in rows)


def main():
    rows = latin_k333_rows()
    A = audit(rows, 9)
    G = conflict(A)
    parts = [set(range(0, 3)), set(range(3, 6)), set(range(6, 9))]

    for v in range(9):
        own = next(P for P in parts if v in P)
        assert G[v] == set(range(9)) - own
        assert len(G[v]) == 6
        assert claw_count(G, v) == 2

    assert alpha_bruteforce(G) == 3
    assert exact_one(rows, parts[0])

    fano = [
        {0, 1, 3}, {0, 2, 5}, {0, 4, 6}, {1, 2, 6},
        {1, 4, 5}, {2, 3, 4}, {3, 5, 6},
    ]
    A7 = audit(fano, 7)
    G7 = conflict(A7)
    assert all(G7[v] == set(range(7)) - {v} for v in range(7))
    assert alpha_bruteforce(G7) == 1

    print("R5 E52 complete-multipartite conflict controls: PASS")
    print("K3,3,3 carrier: n=9, alpha=3=n/3, SAT, c(v)=2 for every vertex")
    print("K7 Fano carrier: n=7, alpha=1<7/3, UNSAT")


if __name__ == "__main__":
    main()
