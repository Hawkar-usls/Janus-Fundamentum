#!/usr/bin/env python3
"""Exact finite regressions for the cycle-kernel flow solver theorem.

Uses only the Python standard library and exact Fraction elimination.
"""

from fractions import Fraction
from itertools import product


def rank_q(rows):
    a = [[Fraction(x) for x in row] for row in rows]
    if not a:
        return 0
    m, n = len(a), len(a[0])
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if a[i][c] != 0), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        z = a[r][c]
        a[r] = [v / z for v in a[r]]
        for i in range(m):
            if i == r or a[i][c] == 0:
                continue
            z = a[i][c]
            a[i] = [a[i][j] - z * a[r][j] for j in range(n)]
        r += 1
        if r == m:
            break
    return r


def same_row_space(a, d):
    ra = rank_q(a)
    rd = rank_q(d)
    return ra == rd == rank_q(a + d)


def matvec(a, x):
    return [sum(row[j] * x[j] for j in range(len(x))) for row in a]


def incidence(nv, edges, drop=None):
    rows = [[0] * len(edges) for _ in range(nv)]
    for j, (u, v) in enumerate(edges):
        rows[u][j] -= 1
        rows[v][j] += 1
    if drop is not None:
        rows = [row for i, row in enumerate(rows) if i != drop]
    return rows


def check_k33_sat():
    left = range(3)
    right = range(3, 6)
    edges = [(u, v) for u in left for v in right]
    n = len(edges)

    # Unsigned vertex-edge incidence source: six weight-3 rows.
    A = [[0] * n for _ in range(6)]
    for j, (u, v) in enumerate(edges):
        A[u][j] = 1
        A[v][j] = 1
    assert all(sum(row) == 3 for row in A)

    # Directed left -> right; remove one redundant vertex row.
    D = incidence(6, edges, drop=5)
    assert rank_q(A) == 5
    assert rank_q(D) == 5
    assert same_row_space(A, D)

    d1 = matvec(D, [1] * n)
    assert all(v % 3 == 0 for v in d1)
    b = [v // 3 for v in d1]

    # Diagonal perfect matching.
    x = [0] * n
    for e in ((0, 3), (1, 4), (2, 5)):
        x[edges.index(e)] = 1
    assert matvec(A, x) == [1] * len(A)
    assert matvec(D, x) == b

    # Exhaustively replay the theorem on all 2^9 Boolean assignments.
    for bits in product((0, 1), repeat=n):
        exact_one = matvec(A, bits) == [1] * len(A)
        flow = matvec(D, bits) == b
        assert exact_one == flow

    return {
        "name": "K3,3",
        "rows": len(A),
        "variables": n,
        "rank": rank_q(A),
        "nullity": n - rank_q(A),
        "witness_weight": sum(x),
    }


def check_nonzero_cycle_unsat():
    edges = [(0, 3), (1, 2), (1, 3), (1, 4), (1, 5), (4, 5)]
    D = incidence(6, edges, drop=5)
    A = [
        [1, 1, 1, 0, 0, 0],
        [1, 0, 0, 1, 1, 0],
        [1, 0, 0, 0, 1, 1],
        [0, 1, 0, 1, 1, 0],
        [0, 0, 1, 1, 1, 0],
    ]

    assert all(sum(row) == 3 for row in A)
    assert rank_q(A) == 5
    assert rank_q(D) == 5
    assert same_row_space(A, D)
    assert len(A[0]) - rank_q(A) == 1

    d1 = matvec(D, [1] * len(edges))
    assert d1 == [-1, -4, 1, 2, 0]
    assert any(v % 3 != 0 for v in d1)

    witnesses = []
    for bits in product((0, 1), repeat=len(edges)):
        if matvec(A, bits) == [1] * len(A):
            witnesses.append(bits)
    assert not witnesses

    return {
        "name": "nonzero-cycle-unsat",
        "rows": len(A),
        "variables": len(edges),
        "rank": rank_q(A),
        "nullity": len(edges) - rank_q(A),
        "D1": d1,
    }


def main():
    sat = check_k33_sat()
    unsat = check_nonzero_cycle_unsat()

    print("Exact cycle-kernel flow router regression: PASS")
    print(
        f"SAT {sat['name']}: m={sat['rows']} n={sat['variables']} "
        f"rank={sat['rank']} nullity={sat['nullity']} "
        f"witness_weight={sat['witness_weight']}"
    )
    print(
        f"UNSAT {unsat['name']}: m={unsat['rows']} n={unsat['variables']} "
        f"rank={unsat['rank']} nullity={unsat['nullity']} D1={unsat['D1']}"
    )
    print("row(A)=row(D) exact equality controls: PASS")
    print("Ax=1 iff Dx=(D1)/3 on K3,3: PASS")
    print("nonintegral demand UNSAT certificate: PASS")


if __name__ == "__main__":
    main()
