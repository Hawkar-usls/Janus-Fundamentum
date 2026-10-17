#!/usr/bin/env python3
from __future__ import annotations

from collections import deque
from fractions import Fraction
from itertools import combinations
import json

GADGET = [
    (2, 5, 6),
    (1, 4, 7),
    (5, 7, 9),
    (0, 3, 7),
    (4, 6, 9),
    (2, 4, 8),
    (3, 8, 9),
    (0, 5, 8),
    (1, 3, 6),
]

LOCAL_GAUGE = (0, 0, 0, 1, 1, 1, 1, 1, 1, 0)

P = [5, 7, 9, 10, 3, 1, 14, 2, 4, 6, 12, 13, 8, 0, 11]
Q = [12, 9, 14, 11, 13, 10, 7, 3, 1, 0, 2, 5, 6, 8, 4]
SEED_ROWS = [tuple(sorted((i, P[i], Q[i]))) for i in range(15)]
SEED_Q_KERNEL = (1, 4, 1, 1, -2, -2, 1, -2, -2, -2, -2, 1, 1, 1, 1)


def rank_f2(rows: list[tuple[int, ...]], n: int) -> int:
    data = []
    for row in rows:
        z = 0
        for j in row:
            z ^= 1 << j
        data.append(z)
    rank = 0
    for c in range(n):
        pivot = next((i for i in range(rank, len(data)) if (data[i] >> c) & 1), None)
        if pivot is None:
            continue
        data[rank], data[pivot] = data[pivot], data[rank]
        for i in range(len(data)):
            if i != rank and ((data[i] >> c) & 1):
                data[i] ^= data[rank]
        rank += 1
    return rank


def rank_q(rows: list[tuple[int, ...]], n: int) -> int:
    matrix = [[Fraction(1 if j in row else 0) for j in range(n)] for row in rows]
    rank = 0
    for c in range(n):
        pivot = next((i for i in range(rank, len(matrix)) if matrix[i][c]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        z = matrix[rank][c]
        matrix[rank] = [v / z for v in matrix[rank]]
        for i in range(len(matrix)):
            if i == rank or matrix[i][c] == 0:
                continue
            z = matrix[i][c]
            matrix[i] = [matrix[i][j] - z * matrix[rank][j] for j in range(n)]
        rank += 1
    return rank


def check_cubic_linear(rows: list[tuple[int, ...]], n: int) -> None:
    assert len(rows) == n
    assert all(len(row) == 3 and len(set(row)) == 3 for row in rows)
    degree = [0] * n
    for row in rows:
        for v in row:
            degree[v] += 1
    assert set(degree) == {3}
    for a, b in combinations(rows, 2):
        assert len(set(a) & set(b)) <= 1


def levi_connected(rows: list[tuple[int, ...]], n: int) -> bool:
    adjacency = [[] for _ in range(n + len(rows))]
    for r, row in enumerate(rows):
        rr = n + r
        for v in row:
            adjacency[v].append(rr)
            adjacency[rr].append(v)
    seen = {0}
    queue = deque([0])
    while queue:
        u = queue.popleft()
        for v in adjacency[u]:
            if v not in seen:
                seen.add(v)
                queue.append(v)
    return len(seen) == n + len(rows)


def mat_vec(rows: list[tuple[int, ...]], vec: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sum(vec[j] for j in row) for row in rows)


def regularize(rows: list[tuple[int, ...]], n: int) -> tuple[list[tuple[int, ...]], int]:
    # Source is cubic: every variable has exactly three row occurrences.
    occurrences = {v: [] for v in range(n)}
    for r, row in enumerate(rows):
        for v in row:
            occurrences[v].append(r)
    assert all(len(rs) == 3 for rs in occurrences.values())

    terminal = {}
    for v, rs in occurrences.items():
        for k, r in enumerate(sorted(rs)):
            terminal[(r, v)] = 10 * v + k

    out: list[tuple[int, ...]] = []

    # Retained old clauses, now on occurrence-specific terminals.
    for r, row in enumerate(rows):
        out.append(tuple(sorted(terminal[(r, v)] for v in row)))

    # One disjoint EQ3 gadget per source variable.
    for v in range(n):
        base = 10 * v
        for clause in GADGET:
            out.append(tuple(base + j for j in clause))

    return out, 10 * n


def local_gauge_support(v: int) -> set[int]:
    base = 10 * v
    return {base + j for j, bit in enumerate(LOCAL_GAUGE) if bit}


# --- exact gadget controls ---
assert all(sum(LOCAL_GAUGE[j] for j in row) % 2 == 0 for row in GADGET)
assert LOCAL_GAUGE[:3] == (0, 0, 0)
assert rank_f2(GADGET, 10) == 7

# The gadget itself is linear and has terminal degree 2, auxiliary degree 3.
gadget_deg = [0] * 10
for row in GADGET:
    for v in row:
        gadget_deg[v] += 1
assert tuple(gadget_deg) == (2, 2, 2, 3, 3, 3, 3, 3, 3, 3)
for a, b in combinations(GADGET, 2):
    assert len(set(a) & set(b)) <= 1
assert levi_connected(GADGET, 10) is True

# --- exact seed controls ---
check_cubic_linear(SEED_ROWS, 15)
assert levi_connected(SEED_ROWS, 15)
assert rank_q(SEED_ROWS, 15) == 14
assert mat_vec(SEED_ROWS, SEED_Q_KERNEL) == (0,) * 15

# The one-dimensional rational kernel cannot contain {-1,2}^15.
# A coordinate with generator value 1 forces lambda in {-1,2};
# the coordinate with value 4 then becomes 4 or -8, neither admissible.
assert 1 in SEED_Q_KERNEL and 4 in SEED_Q_KERNEL
for lam in (-1, 2):
    assert lam * 4 not in (-1, 2)

# --- one full regularization: n=15 -> 150 ---
OUT, NOUT = regularize(SEED_ROWS, 15)
assert NOUT == 150
check_cubic_linear(OUT, NOUT)
assert levi_connected(OUT, NOUT)

# Every source variable contributes an independent, disjoint terminal-zero gauge vector.
supports = [local_gauge_support(v) for v in range(15)]
assert all(supports)
for a, b in combinations(supports, 2):
    assert a.isdisjoint(b)
for support in supports:
    for row in OUT:
        assert len(support & set(row)) % 2 == 0

rank_out = rank_f2(OUT, NOUT)
nullity_out = NOUT - rank_out
assert nullity_out >= 15 == NOUT // 10

# Exact semantics for all recursive levels follows from the already-proved
# EQ3 regularizer theorem.  The finite checker only validates the local mode,
# source seed, and first materialized level; it is not the arbitrary-t proof.

result = {
    "status": "PASS_EQ3_REGULARIZER_LINEAR_GF2_NULLITY_UNSAT_FAMILY",
    "gadget": {
        "rank_F2": 7,
        "nullity_F2": 3,
        "terminal_zero_gauge": list(LOCAL_GAUGE),
        "gauge_weight": sum(LOCAL_GAUGE),
    },
    "seed": {
        "n": 15,
        "rank_Q": 14,
        "exact_one": "UNSAT_BY_RATIONAL_KERNEL_CERTIFICATE",
        "connected": True,
        "linear_cubic": True,
    },
    "first_regularized_level": {
        "n": NOUT,
        "rank_F2": rank_out,
        "nullity_F2": nullity_out,
        "proved_lower_bound": NOUT // 10,
        "independent_local_gauges": 15,
        "connected": True,
        "linear_cubic": True,
        "exact_one": "UNSAT_BY_EXACT_REGULARIZER_EQUIVALENCE",
    },
    "family_theorem": {
        "n_t": "15*10^t",
        "for_t_ge_1": "nullity_F2 >= n_t/10",
        "SAT_status": "UNSAT_FOR_ALL_t",
    },
    "boundary": {
        "raw_F2_nullity_as_universal_progress_measure": "FALSIFIED",
        "universal_solver": "NOT_PROVED",
        "E8_D1": "EMPTY",
        "P_VS_NP": "OPEN",
    },
}
print(json.dumps(result, sort_keys=True))
