#!/usr/bin/env python3
"""Finite exact controls for the rooted MFMC syndrome terminal.

This script is a regression/falsifier only.  The polynomial theorem is source-bound
to Seymour/Truemper and the JANUS Exact-One -> rooted shortest-circuit identity.
"""
from itertools import combinations
import json


def rank_f2(rows):
    rows = [sum((int(v) & 1) << j for j, v in enumerate(row)) for row in rows]
    r = 0
    bit = 0
    while bit < max((x.bit_length() for x in rows), default=0):
        p = next((i for i in range(r, len(rows)) if (rows[i] >> bit) & 1), None)
        if p is not None:
            rows[r], rows[p] = rows[p], rows[r]
            for i in range(len(rows)):
                if i != r and ((rows[i] >> bit) & 1):
                    rows[i] ^= rows[r]
            r += 1
        bit += 1
    return r


def column(matrix, j):
    return tuple(row[j] & 1 for row in matrix)


def dependent(matrix, subset):
    s = [0] * len(matrix)
    for j in subset:
        c = column(matrix, j)
        s = [a ^ b for a, b in zip(s, c)]
    return not any(s)


def circuits(matrix):
    n = len(matrix[0])
    out = []
    for k in range(1, n + 1):
        for S in combinations(range(n), k):
            if not dependent(matrix, S):
                continue
            if all(not dependent(matrix, T)
                   for q in range(1, k)
                   for T in combinations(S, q)):
                out.append(S)
    return out


def nullspace_basis(matrix):
    """Return a row basis of {x: matrix*x=0} over F2."""
    m = len(matrix)
    n = len(matrix[0])
    A = [[matrix[i][j] & 1 for j in range(n)] for i in range(m)]
    pivots = []
    r = 0
    for c in range(n):
        p = next((i for i in range(r, m) if A[i][c]), None)
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        for i in range(m):
            if i != r and A[i][c]:
                A[i] = [x ^ y for x, y in zip(A[i], A[r])]
        pivots.append(c)
        r += 1
        if r == m:
            break
    free = [c for c in range(n) if c not in pivots]
    basis = []
    for f in free:
        x = [0] * n
        x[f] = 1
        for i in range(len(pivots) - 1, -1, -1):
            p = pivots[i]
            x[p] = sum(A[i][j] * x[j] for j in range(p + 1, n)) & 1
        basis.append(x)
    return basis


def shortest_through(matrix, e, weights=None):
    if weights is None:
        weights = [1] * len(matrix[0])
    cs = [C for C in circuits(matrix) if e in C]
    if not cs:
        return None, None
    C = min(cs, key=lambda S: sum(weights[j] for j in S))
    return sum(weights[j] for j in C), C


def matmul_vec_f2(A, x):
    return [sum(a * b for a, b in zip(row, x)) & 1 for row in A]


def min_coset_weight(A):
    n = len(A[0])
    b = [1] * len(A)
    best = None
    bestx = None
    for mask in range(1 << n):
        x = [(mask >> j) & 1 for j in range(n)]
        if matmul_vec_f2(A, x) == b:
            w = sum(x)
            if best is None or w < best:
                best, bestx = w, x
    return best, bestx


def augmented(A):
    return [row[:] + [1] for row in A]


def main():
    # Standard F7 representation: all nonzero vectors of F2^3.
    cols = [
        (1,0,0), (0,1,0), (0,0,1),
        (1,1,0), (1,0,1), (0,1,1), (1,1,1),
    ]
    F7 = [[cols[j][i] for j in range(7)] for i in range(3)]
    F7star = nullspace_basis(F7)
    assert rank_f2(F7) == 3
    assert rank_f2(F7star) == 4

    f7_len, f7_C = shortest_through(F7, 0)
    f7s_len, f7s_C = shortest_through(F7star, 0)
    assert f7_len == 3
    assert f7s_len == 4

    # F7 cannot contain an F7* minor on the same seven-element ground set:
    # a seven-element minor of a seven-element matroid performs no deletion or
    # contraction, while ranks(F7), ranks(F7*) are 3 and 4.
    assert len(F7[0]) == len(F7star[0]) == 7
    assert rank_f2(F7) != rank_f2(F7star)

    # Tiny SAT cubic control: J3.  [A|1] has only four elements, so no F7*
    # minor is possible.  Rooted shortest-circuit weight equals mu(A)=1=n/3.
    J3 = [[1,1,1] for _ in range(3)]
    mu3, x3 = min_coset_weight(J3)
    A3p = augmented(J3)
    w3, C3 = shortest_through(A3p, 3, [1,1,1,0])
    assert mu3 == w3 == 1
    assert 3 * mu3 == 3
    assert matmul_vec_f2(J3, x3) == [1,1,1]

    # Tiny cubic UNSAT control: J4-I4.  The unique parity solution is 1111,
    # so mu=4; [A|1] has five elements and is automatically rooted-F7*-free.
    A4 = [[0 if i == j else 1 for j in range(4)] for i in range(4)]
    mu4, x4 = min_coset_weight(A4)
    A4p = augmented(A4)
    w4, C4 = shortest_through(A4p, 4, [1,1,1,1,0])
    assert mu4 == w4 == 4
    assert 3 * mu4 != 4
    assert matmul_vec_f2(A4, x4) == [1,1,1,1]

    out = {
        "status": "PASS_FINITE_ROOTED_MFMC_SYNDROME_CONTROLS",
        "scientific_ceiling": "FINITE_REGRESSION_ONLY__THEOREM_SOURCE_BOUND__P_VS_NP_OPEN",
        "F7": {
            "rank": 3,
            "shortest_circuit_through_special": f7_len,
            "example": list(f7_C),
            "rooted_F7star_obstruction": False,
            "reason": "same-size rank mismatch; F7 itself is the nonregular MFMC building block"
        },
        "F7star": {
            "rank": 4,
            "shortest_circuit_through_special": f7s_len,
            "example": list(f7s_C),
            "rooted_F7star_obstruction": True
        },
        "J3_sat": {"mu": mu3, "n_over_3": 1, "circuit": list(C3)},
        "J4_minus_I4_unsat": {"mu": mu4, "n_over_3": "4/3", "circuit": list(C4)}
    }
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
