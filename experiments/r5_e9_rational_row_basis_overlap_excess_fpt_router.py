#!/usr/bin/env python3
"""Finite replay for the rational row-basis overlap-excess FPT router.

The arbitrary-size theorem is algebraic/combinatorial.  Exhaustive enumeration
below is confined to tiny frozen controls and is an OFFLINE_FALSIFIER_ONLY,
never an E8-D1 SAT oracle.
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
    assert len(A) == n
    assert all(sum(row) == 3 for row in A)
    assert all(sum(A[i][j] for i in range(n)) == 3 for j in range(n))
    return A


def rank_q(M):
    A = [row[:] for row in M]
    m = len(A)
    n = len(A[0]) if m else 0
    r = 0
    for c in range(n):
        p = next((i for i in range(r, m) if A[i][c] != 0), None)
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        q = A[r][c]
        A[r] = [v / q for v in A[r]]
        for i in range(r + 1, m):
            if A[i][c] != 0:
                q = A[i][c]
                A[i] = [A[i][j] - q * A[r][j] for j in range(n)]
        r += 1
        if r == m:
            break
    return r


def actual_row_basis(A):
    chosen = []
    current_rank = 0
    for i in range(len(A)):
        trial = [A[j][:] for j in chosen + [i]]
        rr = rank_q(trial)
        if rr > current_rank:
            chosen.append(i)
            current_rank = rr
    assert current_rank == rank_q(A)
    return chosen


def verify_exact_one(edges, x):
    return all(sum(x[v] for v in e) == 1 for e in edges)


def overlap_router(edges, n):
    A = matrix(edges, n)
    basis_rows = actual_row_basis(A)
    r = len(basis_rows)
    k = n - r
    delta = 3 * r - n
    assert delta == 2 * n - 3 * k
    assert delta >= 0

    multiplicity = [0] * n
    for bi in basis_rows:
        for j, a in enumerate(A[bi]):
            if a:
                multiplicity[j] += 1

    # Every column must occur in at least one actual basis row.  Otherwise every
    # row in their span would be zero in that column, contradicting col-weight 3.
    assert all(m >= 1 for m in multiplicity)
    assert sum(m - 1 for m in multiplicity) == delta

    shared = [j for j, m in enumerate(multiplicity) if m >= 2]
    private = [j for j, m in enumerate(multiplicity) if m == 1]
    assert len(shared) <= delta

    shared_pos = {v: i for i, v in enumerate(shared)}
    solutions = []

    for bits in product((0, 1), repeat=len(shared)):
        x = [None] * n
        for v in shared:
            x[v] = bits[shared_pos[v]]

        ok = True
        for bi in basis_rows:
            row_vars = [j for j, a in enumerate(A[bi]) if a]
            svars = [j for j in row_vars if multiplicity[j] >= 2]
            pvars = [j for j in row_vars if multiplicity[j] == 1]
            s = sum(x[j] for j in svars)
            if s > 1:
                ok = False
                break
            if s == 1:
                for j in pvars:
                    x[j] = 0
            else:
                if not pvars:
                    ok = False
                    break
                # Private variables occur in exactly one basis row, so choosing
                # one canonical private variable cannot interfere with any other
                # basis equation.
                x[pvars[0]] = 1
                for j in pvars[1:]:
                    x[j] = 0

        if not ok:
            continue
        assert all(v in (0, 1) for v in x)
        xt = tuple(int(v) for v in x)
        # This assertion finite-replays the row-span theorem Bx=1 => Ax=1.
        assert verify_exact_one(edges, xt)
        solutions.append(xt)

    return {
        "n": n,
        "rank_Q": r,
        "nullity_Q": k,
        "delta": delta,
        "basis_rows": basis_rows,
        "multiplicity": multiplicity,
        "shared_variables": shared,
        "shared_count": len(shared),
        "private_count": len(private),
        "enumerated_shared_patterns": 1 << len(shared),
        "delta_upper_bound_patterns": 1 << delta,
        "witness": solutions[0] if solutions else None,
        "sat": bool(solutions),
    }


def brute_exact_one(edges, n):
    for x in product((0, 1), repeat=n):
        if verify_exact_one(edges, x):
            return tuple(x)
    return None


FANO7 = [
    (0, 1, 2), (0, 3, 4), (0, 5, 6),
    (1, 3, 5), (1, 4, 6), (2, 3, 6), (2, 4, 5),
]

AFFINE3X3 = []
for rr in range(3):
    AFFINE3X3.append(tuple(3 * rr + c for c in range(3)))
for c in range(3):
    AFFINE3X3.append(tuple(3 * rr + c for rr in range(3)))
for d in range(3):
    AFFINE3X3.append(tuple(3 * rr + ((rr + d) % 3) for rr in range(3)))

UNSAT9 = [
    (3, 6, 7), (2, 3, 4), (0, 3, 8), (2, 5, 8), (0, 4, 7),
    (1, 4, 8), (1, 5, 7), (1, 2, 6), (0, 5, 6),
]

# Extremal nullity control: J_3 has row/column weight 3, rank 1=n/3,
# nullity 2n/3 and delta=0. Duplicate rows are allowed in the general cubic
# matrix theorem; this control is not claimed linear.
J3 = [(0, 1, 2), (0, 1, 2), (0, 1, 2)]

controls_in = [
    ("FANO7", FANO7, 7),
    ("AFFINE_3X3", AFFINE3X3, 9),
    ("CONNECTED_LINEAR_CUBIC_UNSAT9", UNSAT9, 9),
    ("J3_MAX_NULLITY", J3, 3),
]

controls = []
for name, edges, n in controls_in:
    got = overlap_router(edges, n)
    brute = brute_exact_one(edges, n)
    assert got["sat"] == (brute is not None)
    if got["witness"] is not None:
        assert verify_exact_one(edges, got["witness"])
    got["name"] = name
    got["brute_reference_sat"] = brute is not None
    controls.append(got)

by = {c["name"]: c for c in controls}
assert by["J3_MAX_NULLITY"]["delta"] == 0
assert by["J3_MAX_NULLITY"]["nullity_Q"] == 2
assert by["J3_MAX_NULLITY"]["sat"] is True
assert by["FANO7"]["sat"] is False
assert by["CONNECTED_LINEAR_CUBIC_UNSAT9"]["sat"] is False
assert by["AFFINE_3X3"]["sat"] is True

print(json.dumps({
    "status": "PASS_RATIONAL_ROW_BASIS_OVERLAP_EXCESS_FPT_ROUTER_FINITE_REPLAY",
    "role": "OFFLINE_FALSIFIER_ONLY",
    "theorem": "EXACT_ONE_IN_2^delta_POLY_FOR_delta_EQ_3rankQ_minus_n_EQ_2n_minus_3nullityQ",
    "controls": controls,
    "max_nullity_terminal": "k_EQ_2n_OVER_3_IMPLIES_SAT",
    "low_delta_terminal": "delta_O_LOG_N_IMPLIES_POLYNOMIAL",
    "combined_residual": "k_OMEGA_LOG_N_AND_delta_OMEGA_LOG_N",
    "E8_D1": "EMPTY",
    "P_VS_NP": "OPEN",
}, sort_keys=True))
