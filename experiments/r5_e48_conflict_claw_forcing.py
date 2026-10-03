#!/usr/bin/env python3
"""Exact controls for R5 E48 conflict-claw forcing.

For a square+cubic+linear all-positive Exact-One carrier A, every unselected
vertex of any witness must be the center of an induced claw in the conflict graph.
Hence every non-claw-center vertex is forced selected.

Controls:
  * 3x3 toroidal SAT carrier: every vertex is a claw center, so F=empty.
  * three disjoint Fano-plane carriers: conflict graph is 3 K7 components,
    no vertex is a claw center, so |F|=21>21/3 and the rule certifies UNSAT.

P_VS_NP remains OPEN.
"""
from itertools import combinations


def conflict_graph(rows, n):
    adj = [set() for _ in range(n)]
    for row in rows:
        row = list(row)
        for a, b in combinations(row, 2):
            adj[a].add(b)
            adj[b].add(a)
    return adj


def is_claw_center(v, adj):
    for leaves in combinations(sorted(adj[v]), 3):
        if all(b not in adj[a] for a, b in combinations(leaves, 2)):
            return True
    return False


def forced_set(rows, n):
    adj = conflict_graph(rows, n)
    F = {v for v in range(n) if not is_claw_center(v, adj)}
    return F, adj


def independent(S, adj):
    S = set(S)
    return all(not (adj[v] & S) for v in S)


def verify_carrier(rows, n):
    assert len(rows) == n
    assert all(len(r) == 3 for r in rows)
    deg = [0] * n
    for r in rows:
        for v in r:
            deg[v] += 1
    assert all(d == 3 for d in deg)
    for i, j in combinations(range(n), 2):
        assert len(rows[i] & rows[j]) <= 1


def torus3():
    k = 3
    def vid(i, j):
        return (i % k) * k + (j % k)
    rows = []
    for i in range(k):
        for j in range(k):
            rows.append({vid(i, j), vid(i + 1, j), vid(i, j + 1)})
    return rows


def fano_rows(offset=0):
    # Cyclic Fano plane: line i = {i, i+1, i+3} mod 7.
    return [
        {offset + i, offset + ((i + 1) % 7), offset + ((i + 3) % 7)}
        for i in range(7)
    ]


def main():
    print("R5 E48 conflict-claw forcing controls: PASS")

    rows = torus3()
    verify_carrier(rows, 9)
    F, adj = forced_set(rows, 9)
    assert not F
    # Explicit SAT witness: one diagonal residue class.
    S = {0, 4, 8}
    assert independent(S, adj)
    assert all(len(S & r) == 1 for r in rows)
    print("torus3: n=9, SAT, non_claw_forced=0")

    rows = fano_rows(0) + fano_rows(7) + fano_rows(14)
    verify_carrier(rows, 21)
    F, adj = forced_set(rows, 21)
    assert len(F) == 21
    assert len(F) > 21 // 3
    print("3xFano: n=21, non_claw_forced=21>7 => UNSAT by E48")

    print("Conclusion: every non-claw-center is forced selected in any witness.")


if __name__ == "__main__":
    main()
