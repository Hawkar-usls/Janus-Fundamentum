#!/usr/bin/env python3
"""Finite replay for the rational-kernel nullity FPT router.

This checker uses exact Fraction arithmetic.  Enumeration is confined to tiny
frozen controls and validates the arbitrary-size information-coordinate proof;
it is not a universal E8-D1 solver.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import product
import json


def matrix(edges, n):
    A = [[Fraction(0) for _ in range(n)] for _ in edges]
    for i, e in enumerate(edges):
        assert len(e) == 3 and len(set(e)) == 3
        for v in e:
            A[i][v] = Fraction(1)
    return A


def rref(M):
    A = [row[:] for row in M]
    m = len(A)
    n = len(A[0]) if m else 0
    pivots = []
    r = 0
    for c in range(n):
        p = next((i for i in range(r, m) if A[i][c] != 0), None)
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        q = A[r][c]
        A[r] = [v / q for v in A[r]]
        for i in range(m):
            if i != r and A[i][c] != 0:
                q = A[i][c]
                A[i] = [A[i][j] - q * A[r][j] for j in range(n)]
        pivots.append(c)
        r += 1
        if r == m:
            break
    return A, pivots


def nullspace_basis(A):
    R, pivots = rref(A)
    n = len(A[0])
    free = [j for j in range(n) if j not in pivots]
    basis = []
    for f in free:
        v = [Fraction(0) for _ in range(n)]
        v[f] = Fraction(1)
        for i, p in enumerate(pivots):
            v[p] = -R[i][f]
        basis.append(v)
    return basis, len(pivots)


def choose_information_rows(B):
    # B is n x k. Choose k linearly independent rows greedily.
    n = len(B)
    k = len(B[0]) if n else 0
    chosen = []
    rank = 0
    for i in range(n):
        trial = [B[j][:] for j in chosen + [i]]
        _, piv = rref(trial)
        if len(piv) > rank:
            chosen.append(i)
            rank += 1
            if rank == k:
                break
    assert rank == k
    return chosen


def solve_square(M, b):
    k = len(M)
    aug = [M[i][:] + [b[i]] for i in range(k)]
    R, piv = rref(aug)
    # Pivots in the first k columns must be all columns.
    assert all(c in piv for c in range(k))
    x = [Fraction(0)] * k
    for i, p in enumerate([c for c in piv if c < k]):
        x[p] = R[i][-1]
    return x


def exact_kernel_word_candidates(edges, n):
    A = matrix(edges, n)
    basis_cols, rank = nullspace_basis(A)
    k = n - rank
    if k == 0:
        return k, [], []
    # Convert list of k length-n basis columns to n x k matrix.
    B = [[basis_cols[j][i] for j in range(k)] for i in range(n)]
    I = choose_information_rows(B)
    BI = [B[i][:] for i in I]
    words = []
    for s in product((Fraction(-1), Fraction(2)), repeat=k):
        alpha = solve_square(BI, list(s))
        w = [sum(B[i][j] * alpha[j] for j in range(k)) for i in range(n)]
        if all(v in (Fraction(-1), Fraction(2)) for v in w):
            words.append(tuple(int(v) for v in w))
    return k, I, sorted(set(words))


def word_to_assignment(w):
    x = tuple((v + 1) // 3 for v in w)
    assert all(v in (0, 1) for v in x)
    return x


def verify_exact_one(edges, x):
    return all(sum(x[v] for v in e) == 1 for e in edges)


FANO7 = [
    (0, 1, 2), (0, 3, 4), (0, 5, 6),
    (1, 3, 5), (1, 4, 6), (2, 3, 6), (2, 4, 5),
]

AFFINE3X3 = []
for r in range(3):
    AFFINE3X3.append(tuple(3*r+c for c in range(3)))
for c in range(3):
    AFFINE3X3.append(tuple(3*r+c for r in range(3)))
for d in range(3):
    AFFINE3X3.append(tuple(3*r+((r+d) % 3) for r in range(3)))

UNSAT9 = [
    (3,6,7), (2,3,4), (0,3,8), (2,5,8), (0,4,7),
    (1,4,8), (1,5,7), (1,2,6), (0,5,6),
]


def run(name, edges, n):
    k, I, words = exact_kernel_word_candidates(edges, n)
    assignments = [word_to_assignment(w) for w in words]
    assert all(verify_exact_one(edges, x) for x in assignments)
    return {
        "name": name,
        "n": n,
        "rational_nullity": k,
        "information_coordinates": I,
        "enumerated_patterns": 1 << k,
        "exact_kernel_word_count": len(words),
        "exact_one_solution_count": len(assignments),
    }

controls = [
    run("FANO7", FANO7, 7),
    run("AFFINE_3X3", AFFINE3X3, 9),
    run("CONNECTED_LINEAR_CUBIC_UNSAT9", UNSAT9, 9),
]
by = {c["name"]: c for c in controls}
assert by["FANO7"]["rational_nullity"] == 0
assert by["FANO7"]["exact_one_solution_count"] == 0
assert by["CONNECTED_LINEAR_CUBIC_UNSAT9"]["rational_nullity"] == 0
assert by["CONNECTED_LINEAR_CUBIC_UNSAT9"]["exact_one_solution_count"] == 0
assert by["AFFINE_3X3"]["rational_nullity"] == 2
assert by["AFFINE_3X3"]["exact_one_solution_count"] == 3

print(json.dumps({
    "status": "PASS_RATIONAL_KERNEL_NULLITY_FPT_ROUTER_FINITE_REPLAY",
    "role": "OFFLINE_FALSIFIER_ONLY",
    "theorem": "EXACT_ONE_IN_2^k_POLY_FOR_k_EQ_NULLITY_Q",
    "controls": controls,
    "k_zero_terminal": "UNSAT",
    "k_log_n_terminal": "POLYNOMIAL",
    "high_nullity_core": "OPEN",
    "E8_D1": "EMPTY",
    "P_VS_NP": "OPEN",
}, sort_keys=True))
