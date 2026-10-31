#!/usr/bin/env python3
"""Exact dependency-free replay for R5 E9 rank-1 stitched TD(3,3).

Checks the explicit family A_m for m=1..8:
- square cubic row/column degrees;
- linearity;
- connected Levi graph;
- exact Q-rank = 8m-1 and nullity = m+1;
- base TD(3,3) rank remains 7 after deleting L00, L01, or both;
- every stitch is the declared 2-switch and exposes exactly two cross incidences.

This is a regression certificate for the family theorem, not a universal solver.
"""

from collections import deque
from fractions import Fraction


def td33_block():
    # columns 0..2 = X, 3..5 = Y, 6..8 = Z
    rows = []
    for i in range(3):
        for j in range(3):
            row = [0] * 9
            row[i] = 1
            row[3 + j] = 1
            row[6 + ((i + j) % 3)] = 1
            rows.append(row)
    return rows


def rank_q(matrix):
    a = [[Fraction(v) for v in row] for row in matrix]
    m = len(a)
    n = len(a[0]) if m else 0
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if a[i][c]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        p = a[r][c]
        a[r] = [v / p for v in a[r]]
        for i in range(m):
            if i != r and a[i][c]:
                f = a[i][c]
                a[i] = [a[i][j] - f * a[r][j] for j in range(n)]
        r += 1
        if r == m:
            break
    return r


def stitched(m):
    n = 9 * m
    b = td33_block()
    a = [[0] * n for _ in range(n)]
    for t in range(m):
        for r in range(9):
            for c in range(9):
                a[9 * t + r][9 * t + c] = b[r][c]

    # Row numbering L_ij = 3*i+j.  Thus L00=0, L01=1.
    # Column x0=0, y1=4 inside one block.
    for t in range(m - 1):
        r1 = 9 * t + 1
        c1 = 9 * t + 4
        r2 = 9 * (t + 1)
        c2 = 9 * (t + 1)
        assert a[r1][c1] == 1
        assert a[r2][c2] == 1
        assert a[r1][c2] == 0
        assert a[r2][c1] == 0
        a[r1][c1] = 0
        a[r2][c2] = 0
        a[r1][c2] = 1
        a[r2][c1] = 1
    return a


def supports(row):
    return [i for i, v in enumerate(row) if v]


def validate_cubic_linear(a):
    n = len(a)
    assert all(len(row) == n for row in a)
    assert [sum(row) for row in a] == [3] * n
    assert [sum(a[r][c] for r in range(n)) for c in range(n)] == [3] * n

    seen = set()
    for row in a:
        s = supports(row)
        assert len(s) == 3
        for i in range(3):
            for j in range(i + 1, 3):
                pair = tuple(sorted((s[i], s[j])))
                assert pair not in seen
                seen.add(pair)


def levi_connected(a):
    n = len(a)
    g = [[] for _ in range(2 * n)]
    for r in range(n):
        for c, bit in enumerate(a[r]):
            if bit:
                g[r].append(n + c)
                g[n + c].append(r)
    seen = {0}
    q = deque([0])
    while q:
        u = q.popleft()
        for v in g[u]:
            if v not in seen:
                seen.add(v)
                q.append(v)
    return len(seen) == 2 * n


def cross_edges(a, boundary):
    """Count Levi incidences crossing block boundary boundary|boundary+1."""
    n = len(a)
    cut = 9 * (boundary + 1)
    count = 0
    for r in range(n):
        for c, bit in enumerate(a[r]):
            if bit and ((r < cut <= c) or (c < cut <= r)):
                count += 1
    return count


def validate_local_rank():
    b = td33_block()
    assert rank_q(b) == 7
    for removed in ((0,), (1,), (0, 1)):
        reduced = [row for i, row in enumerate(b) if i not in removed]
        assert rank_q(reduced) == 7


def main():
    validate_local_rank()
    receipt = []
    for m in range(1, 9):
        a = stitched(m)
        n = 9 * m
        validate_cubic_linear(a)
        assert levi_connected(a)
        rank = rank_q(a)
        nullity = n - rank
        assert rank == 8 * m - 1
        assert nullity == m + 1
        for boundary in range(m - 1):
            # For an interior chain cut this counts only the two explicit
            # cross incidences between the prefix and suffix.
            assert cross_edges(a, boundary) == 2
        receipt.append((m, n, rank, nullity))

    print("R5_E9_RANK1_STITCHED_TD33_HIGH_NULLITY = PASS")
    for m, n, rank, nullity in receipt:
        print(f"m={m:2d} n={n:2d} rank_Q={rank:2d} nullity_Q={nullity:2d}")
    print("E8_D1 = EMPTY")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
