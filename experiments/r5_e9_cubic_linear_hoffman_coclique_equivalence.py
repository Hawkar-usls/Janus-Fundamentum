#!/usr/bin/env python3
"""Finite regression checker for the cubic-linear Hoffman-coclique bridge.

The proof is in the companion research note.  Exhaustive enumeration here is
OFFLINE_FALSIFIER_ONLY and is never used as universal evidence.
"""

from fractions import Fraction
from itertools import product
import json


def incidence(n, blocks):
    A = [[0] * n for _ in blocks]
    for i, block in enumerate(blocks):
        for j in block:
            A[i][j] = 1
    return A


def transpose(A):
    return [list(col) for col in zip(*A)]


def matmul(A, B):
    BT = transpose(B)
    return [[sum(a * b for a, b in zip(row, col)) for col in BT] for row in A]


def matvec(A, x):
    return [sum(a * b for a, b in zip(row, x)) for row in A]


def rank_q(A):
    M = [[Fraction(v) for v in row] for row in A]
    m = len(M)
    n = len(M[0]) if m else 0
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if M[i][c]), None)
        if pivot is None:
            continue
        M[r], M[pivot] = M[pivot], M[r]
        p = M[r][c]
        M[r] = [v / p for v in M[r]]
        for i in range(m):
            if i != r and M[i][c]:
                q = M[i][c]
                M[i] = [u - q * v for u, v in zip(M[i], M[r])]
        r += 1
        if r == m:
            break
    return r


def conflict_graph(A):
    m = len(A)
    n = len(A[0])
    G = [[0] * n for _ in range(n)]
    for u in range(n):
        for v in range(u + 1, n):
            overlap = sum(A[i][u] * A[i][v] for i in range(m))
            assert overlap <= 1, (u, v, overlap)
            G[u][v] = G[v][u] = overlap
    return G


def check_carrier(name, A, expected_models, expected_rank):
    n = len(A)
    assert len(A) == len(A[0])
    assert all(sum(row) == 3 for row in A)
    assert all(sum(A[i][j] for i in range(n)) == 3 for j in range(n))

    G = conflict_graph(A)
    assert all(sum(row) == 6 for row in G)

    ATA = matmul(transpose(A), A)
    target = [[(3 if i == j else 0) + G[i][j] for j in range(n)] for i in range(n)]
    assert ATA == target

    rq = rank_q(A)
    assert rq == expected_rank, (name, rq, expected_rank)

    exact_models = []
    eigen_models = []
    equitable_models = []

    for x in product((0, 1), repeat=n):
        exact = matvec(A, x) == [1] * n

        w = [3 * b - 1 for b in x]
        eigen = matvec(G, w) == [-3 * b for b in w]

        S = {i for i, b in enumerate(x) if b}
        independent = all(not (G[u][v] and u in S and v in S)
                          for u in range(n) for v in range(u + 1, n))
        equitable = independent and all(
            sum(G[v][u] for u in S) == (0 if v in S else 3)
            for v in range(n)
        )

        assert exact == eigen, (name, x, "exact/eigen mismatch")
        assert exact == equitable, (name, x, "exact/equitable mismatch")

        if exact:
            exact_models.append(x)
        if eigen:
            eigen_models.append(x)
        if equitable:
            equitable_models.append(x)

    assert len(exact_models) == expected_models
    assert exact_models == eigen_models == equitable_models

    return {
        "name": name,
        "n": n,
        "rank_Q": rq,
        "nullity_Q": n - rq,
        "exact_models": len(exact_models),
        "gram_identity": True,
        "degree_conflict": 6,
        "exact_iff_two_valued_minus3_eigenvector": True,
        "exact_iff_equitable_0_6_3_3": True,
    }


def main():
    # Fano plane: cubic-linear, n not divisible by 3, no Exact-One model.
    fano = [
        (0, 1, 2),
        (0, 3, 4),
        (0, 5, 6),
        (1, 3, 5),
        (1, 4, 6),
        (2, 3, 6),
        (2, 4, 5),
    ]

    # Three parallel classes in the affine plane Z_3^2: rows, columns,
    # and slope +1.  The missing slope class gives the three Exact-One models.
    affine = []
    for r in range(3):
        affine.append(tuple(3 * r + c for c in range(3)))
    for c in range(3):
        affine.append(tuple(3 * r + c for r in range(3)))
    for b in range(3):
        affine.append(tuple(3 * r + ((r + b) % 3) for r in range(3)))

    results = [
        check_carrier("FANO_7", incidence(7, fano), expected_models=0, expected_rank=7),
        check_carrier("AFFINE_3X3", incidence(9, affine), expected_models=3, expected_rank=7),
    ]

    print(json.dumps({
        "status": "PASS_HOFFMAN_COCLIQUE_EQUIVALENCE_FINITE_REGRESSION",
        "authority": "OFFLINE_FALSIFIER_ONLY",
        "controls": results,
        "scientific_boundary": {
            "E8_D1": "EMPTY",
            "P_VS_NP": "OPEN",
        },
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
