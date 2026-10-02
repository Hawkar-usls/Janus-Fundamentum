#!/usr/bin/env python3
"""Exact finite controls for R5 E22.

Verifies the abstract strict hierarchy family

    K_s = { y in Q^s : sum_i y_i = 0 }

against the alphabet Sigma={-1,2}.

For every s not divisible by 3:
  * every proper coordinate projection of K_s is full;
  * K_s cap Sigma^s is empty;
  * the unique minimal row dependency has support s.

This is an abstract rational-kernel firewall.  It does NOT assert that every K_s
is realizable as the full kernel of a square+cubic+linear Exact-One carrier.
P_VS_NP remains OPEN.
"""

from fractions import Fraction
from itertools import combinations, product

SIGMA = (-1, 2)


def rank_q(M):
    A = [[Fraction(x) for x in row] for row in M]
    if not A:
        return 0
    m, n = len(A), len(A[0])
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if A[i][c]), None)
        if pivot is None:
            continue
        A[r], A[pivot] = A[pivot], A[r]
        z = A[r][c]
        A[r] = [x / z for x in A[r]]
        for i in range(m):
            if i != r and A[i][c]:
                f = A[i][c]
                A[i] = [A[i][j] - f * A[r][j] for j in range(n)]
        r += 1
        if r == m:
            break
    return r


def basis_rows(s):
    # Basis matrix B in Q^{s x (s-1)} for K_s.
    # Parameter t=(t_1,...,t_{s-1}) gives
    # y_i=t_i for i<s and y_s=-sum_i t_i.
    B = []
    for i in range(s - 1):
        row = [0] * (s - 1)
        row[i] = 1
        B.append(row)
    B.append([-1] * (s - 1))
    return B


def alphabet_points(s):
    return [p for p in product(SIGMA, repeat=s) if sum(p) == 0]


def check_s(s):
    B = basis_rows(s)
    assert rank_q(B) == s - 1

    # Every proper coordinate projection is full.  It is enough for the finite
    # checker to verify every subset cardinality; the note gives the direct proof.
    for k in range(1, s):
        for T in combinations(range(s), k):
            assert rank_q([B[i] for i in T]) == k

    pts = alphabet_points(s)
    expected = [] if s % 3 else None
    if expected == []:
        assert pts == []
    else:
        # sum(-1/2 alphabet) = -s + 3*m, so zero iff exactly s/3 entries are 2.
        from math import comb
        assert len(pts) == comb(s, s // 3)

    # The s row vectors have rank s-1, while every proper subset is independent:
    # the unique matroid circuit has support exactly s.
    assert rank_q(B) == s - 1
    for omitted in range(s):
        rows = [B[i] for i in range(s) if i != omitted]
        assert rank_q(rows) == s - 1

    return len(pts)


def main():
    rows = []
    for s in range(2, 15):
        count = check_s(s)
        rows.append((s, count))

    print("R5 E22 abstract KLOC strict-hierarchy controls: PASS")
    for s, count in rows:
        verdict = "GLOBAL_EMPTY" if count == 0 else f"GLOBAL_POINTS={count}"
        print(f"  s={s}: every proper projection full; {verdict}")


if __name__ == "__main__":
    main()
