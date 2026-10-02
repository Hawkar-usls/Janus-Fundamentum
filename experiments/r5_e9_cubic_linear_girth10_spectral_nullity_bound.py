#!/usr/bin/env python3
"""Exact regression for the cubic-linear / girth>=10 spectral nullity bound.

This is a theorem regression, not an E8-D1 solver.  It checks exact arithmetic
identities used by the proof and small frozen incidence controls.  It does not
replace the arbitrary-n proof in the companion research note.
"""
from __future__ import annotations

from fractions import Fraction
import json


def tree_closed_walk_moments(d: int, max_len: int) -> list[int]:
    """Aggregate distance-state walk recurrence on the infinite d-regular tree."""
    states = {0: 1}
    out = [1]
    for _ in range(max_len):
        nxt: dict[int, int] = {}
        for dist, count in states.items():
            if dist == 0:
                nxt[1] = nxt.get(1, 0) + d * count
            else:
                nxt[dist - 1] = nxt.get(dist - 1, 0) + count
                nxt[dist + 1] = nxt.get(dist + 1, 0) + (d - 1) * count
        states = nxt
        out.append(states.get(0, 0))
    return out


def poly_square(coeffs: list[Fraction]) -> list[Fraction]:
    out = [Fraction(0) for _ in range(2 * len(coeffs) - 1)]
    for i, a in enumerate(coeffs):
        for j, b in enumerate(coeffs):
            out[i + j] += a * b
    return out


def rank_q(A: list[list[int]]) -> int:
    M = [[Fraction(x) for x in row] for row in A]
    rows = len(M)
    cols = len(M[0]) if rows else 0
    r = 0
    for c in range(cols):
        pivot = next((i for i in range(r, rows) if M[i][c] != 0), None)
        if pivot is None:
            continue
        M[r], M[pivot] = M[pivot], M[r]
        p = M[r][c]
        M[r] = [x / p for x in M[r]]
        for i in range(rows):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [M[i][j] - f * M[r][j] for j in range(cols)]
        r += 1
        if r == rows:
            break
    return r


def incidence(n: int, edges: list[tuple[int, ...]]) -> list[list[int]]:
    return [[1 if j in e else 0 for j in range(n)] for e in edges]


def transpose(A: list[list[int]]) -> list[list[int]]:
    return [list(row) for row in zip(*A)]


def matmul(A: list[list[int]], B: list[list[int]]) -> list[list[int]]:
    return [
        [sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))]
        for i in range(len(A))
    ]


def trace(A: list[list[int]]) -> int:
    return sum(A[i][i] for i in range(len(A)))


def verify_cubic_linear_control(A: list[list[int]]) -> dict[str, int]:
    n = len(A)
    assert n and all(len(row) == n for row in A)
    assert all(sum(row) == 3 for row in A)
    assert all(sum(A[i][j] for i in range(n)) == 3 for j in range(n))
    for i in range(n):
        for j in range(i + 1, n):
            assert sum(A[i][c] * A[j][c] for c in range(n)) <= 1

    M = matmul(A, transpose(A))
    M2 = matmul(M, M)
    assert trace(M) == 3 * n
    assert trace(M2) == 15 * n

    r = rank_q(A)
    k = n - r
    assert k * (5 * n - 27) <= 2 * n * (n - 7)
    return {"n": n, "rank_Q": r, "nullity_Q": k}


# Infinite cubic-tree moments through the girth-10 certificate order.
moments = tree_closed_walk_moments(3, 8)
assert [moments[i] for i in (0, 2, 4, 6, 8)] == [1, 3, 15, 87, 543]

# q(t)=1 - 9/16 t^2 + 1/16 t^4.  Store as polynomial in u=t^2.
q = [Fraction(1), Fraction(-9, 16), Fraction(1, 16)]
q2 = poly_square(q)
assert q2 == [
    Fraction(1),
    Fraction(-9, 8),
    Fraction(113, 256),
    Fraction(-9, 128),
    Fraction(1, 256),
]

mean_q2 = sum(q2[j] * moments[2 * j] for j in range(5))
assert mean_q2 == Fraction(1, 4)


def q_eval(t: int) -> Fraction:
    u = Fraction(t * t)
    return q[0] + q[1] * u + q[2] * u * u


assert q_eval(0) == 1
assert q_eval(3) == 1
assert q_eval(-3) == 1

# Frozen cubic-linear rational controls.
fano_edges = [
    (0, 1, 2),
    (0, 3, 4),
    (0, 5, 6),
    (1, 3, 5),
    (1, 4, 6),
    (2, 3, 6),
    (2, 4, 5),
]
fano = verify_cubic_linear_control(incidence(7, fano_edges))
assert fano == {"n": 7, "rank_Q": 7, "nullity_Q": 0}

affine_edges: list[tuple[int, ...]] = []
for r in range(3):
    affine_edges.append(tuple(3 * r + c for c in range(3)))
for c in range(3):
    affine_edges.append(tuple(3 * r + c for r in range(3)))
for d in range(3):
    affine_edges.append(tuple(3 * r + ((r + d) % 3) for r in range(3)))
affine = verify_cubic_linear_control(incidence(9, affine_edges))
assert affine == {"n": 9, "rank_Q": 7, "nullity_Q": 2}

# Symbolic endpoint accounting for a connected bipartite cubic Tanner graph:
# 2k zero eigenvalues + the simple +/-3 endpoints contribute at least 2k+2.
# trace q(C)^2 = n/2, hence 2k+2 <= n/2 and k <= n/4 - 1.
for n in range(4, 401, 2):
    max_k = (n - 4) // 4
    assert 2 * max_k + 2 <= Fraction(n, 2)
    assert max_k <= Fraction(n, 4) - 1

out = {
    "status": "PASS_CUBIC_LINEAR_GIRTH10_SPECTRAL_NULLITY_REGRESSION",
    "tree_degree": 3,
    "tree_moments_even_0_to_8": [1, 3, 15, 87, 543],
    "q_coefficients_in_t2": ["1", "-9/16", "1/16"],
    "mean_q_squared": "1/4",
    "endpoint_values": {"q(0)": "1", "q(+3)": "1", "q(-3)": "1"},
    "general_bound": "k*(5*n-27) <= 2*n*(n-7)",
    "girth10_bound": "k <= n/4 - 1",
    "frozen_controls": {"FANO7": fano, "AFFINE3X3": affine},
    "proof_role": "EXACT_IDENTITY_AND_SMALL_CONTROL_REGRESSION_ONLY",
    "theorem_status": "DERIVED_THEOREM_CANDIDATE",
    "E8_D1": "EMPTY",
    "P_VS_NP": "OPEN",
    "P_EQ_NP": "NOT_PROVED",
}
print(json.dumps(out, sort_keys=True))
