#!/usr/bin/env python3
"""Finite regression for WSH-1.

This is NOT the proof.  The theorem is the symbolic factorization/rank argument
in the paired research note.  This checker only replays the compatibility
matrix and exact finite-field rank on small m.
"""

from __future__ import annotations


def compatibility_matrix(m: int) -> list[list[int]]:
    n = 1 << m
    # A complete sign assignment on the left and right is compatible iff equal.
    return [[1 if s == t else 0 for t in range(n)] for s in range(n)]


def rank_mod(mat: list[list[int]], p: int = 1_000_003) -> int:
    a = [[x % p for x in row] for row in mat]
    if not a:
        return 0
    rows, cols = len(a), len(a[0])
    r = 0
    for c in range(cols):
        pivot = next((i for i in range(r, rows) if a[i][c]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        inv = pow(a[r][c], p - 2, p)
        a[r] = [(x * inv) % p for x in a[r]]
        for i in range(rows):
            if i != r and a[i][c]:
                f = a[i][c]
                a[i] = [(x - f * y) % p for x, y in zip(a[i], a[r])]
        r += 1
        if r == rows:
            break
    return r


def conflict_free(s: int, t: int, m: int) -> bool:
    # bit 1 = PLUS, bit 0 = MINUS. Since each side chooses one sign per channel,
    # opposite choices at any coordinate create a polarity conflict.
    mask = (1 << m) - 1
    return ((s ^ t) & mask) == 0


def main() -> None:
    for m in range(1, 8):
        n = 1 << m
        H = compatibility_matrix(m)

        # Exact semantic replay.
        for s in range(n):
            for t in range(n):
                expected = 1 if conflict_free(s, t, m) else 0
                assert H[s][t] == expected

        # Exact finite-field rank replay. The symbolic theorem gives this over
        # every field because H is identity; here we independently eliminate.
        r = rank_mod(H)
        assert r == n, (m, r, n)
        print(f"m={m:2d} states={n:4d} rank={r:4d} PASS")

    print("WSH finite regression: PASS")
    print("Scientific ceiling: finite regression only; P_VS_NP remains OPEN")


if __name__ == "__main__":
    main()
