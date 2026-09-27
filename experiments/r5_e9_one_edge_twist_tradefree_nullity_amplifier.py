#!/usr/bin/env python3
"""Finite replay for the one-edge-twist trade-free nullity amplifier.

The arbitrary-n proof is in the companion research note. Enumeration here is
OFFLINE_FALSIFIER_ONLY / REGRESSION_ONLY and is not an E8-D1 solver.
"""
from __future__ import annotations

from collections import deque
from fractions import Fraction
import json

SEED_ROWS = [
    (0,15,17),(1,4,12),(2,10,14),(3,4,11),(4,8,9),(3,5,13),
    (1,6,10),(2,7,15),(1,8,14),(3,7,9),(9,10,16),(7,11,13),
    (5,12,17),(0,13,16),(0,12,14),(5,8,15),(2,6,16),(6,11,17),
]
SEED_MODEL = (1,1,1,0,0,1,0,0,0,1,0,1,0,0,0,0,0,0)


def matrix_from_rows(rows, n):
    A = [[0]*n for _ in range(n)]
    for i, row in enumerate(rows):
        for j in row:
            A[i][j] = 1
    return A


def rank_q(A):
    M = [[Fraction(x) for x in row] for row in A]
    m, n = len(M), len(M[0])
    r = 0
    for c in range(n):
        piv = next((i for i in range(r, m) if M[i][c]), None)
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        p = M[r][c]
        for j in range(c, n):
            M[r][j] /= p
        for i in range(r+1, m):
            if M[i][c]:
                f = M[i][c]
                for j in range(c, n):
                    M[i][j] -= f*M[r][j]
        r += 1
        if r == m:
            break
    return r


def gf2_nullspace_basis(A):
    M = [sum((v & 1) << j for j, v in enumerate(row)) for row in A]
    m, n = len(M), len(A[0])
    pivots = []
    r = 0
    for c in range(n):
        p = next((i for i in range(r, m) if (M[i] >> c) & 1), None)
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        for i in range(m):
            if i != r and ((M[i] >> c) & 1):
                M[i] ^= M[r]
        pivots.append(c)
        r += 1
        if r == m:
            break
    pivot_set = set(pivots)
    free = [c for c in range(n) if c not in pivot_set]
    basis = []
    for f in free:
        x = 1 << f
        for ri in range(len(pivots)-1, -1, -1):
            c = pivots[ri]
            parity = (M[ri] & x).bit_count() & 1
            if parity:
                x ^= 1 << c
        basis.append(x)
    return basis


def row_supports(A):
    return [tuple(j for j, v in enumerate(row) if v) for row in A]


def is_connected(A):
    n = len(A)
    rows = row_supports(A)
    col_rows = [[] for _ in range(n)]
    for i, row in enumerate(rows):
        for j in row:
            col_rows[j].append(i)
    seen_r, seen_c = {0}, set()
    q = deque([("r", 0)])
    while q:
        side, u = q.popleft()
        if side == "r":
            for j in rows[u]:
                if j not in seen_c:
                    seen_c.add(j)
                    q.append(("c", j))
        else:
            for i in col_rows[u]:
                if i not in seen_r:
                    seen_r.add(i)
                    q.append(("r", i))
    return len(seen_r) == n and len(seen_c) == n


def is_cubic_linear(A):
    n = len(A)
    rows = row_supports(A)
    assert all(len(r) == 3 for r in rows)
    coldeg = [0]*n
    for row in rows:
        for j in row:
            coldeg[j] += 1
    if any(d != 3 for d in coldeg):
        return False
    sets = [set(r) for r in rows]
    return all(len(sets[i] & sets[j]) <= 1 for i in range(n) for j in range(i))


def contracted_adj(A, support_mask):
    n = len(A)
    adj = {j: [] for j in range(n) if (support_mask >> j) & 1}
    for row in row_supports(A):
        hit = [j for j in row if (support_mask >> j) & 1]
        if len(hit) == 2:
            u, v = hit
            adj[u].append(v)
            adj[v].append(u)
        elif len(hit) not in (0, 2):
            raise AssertionError("non-kernel support")
    return adj


def is_bipartite(adj):
    color = {}
    for root in adj:
        if root in color:
            continue
        color[root] = 0
        q = deque([root])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if v in color:
                    if color[v] == color[u]:
                        return False
                else:
                    color[v] = 1-color[u]
                    q.append(v)
    return True


def has_signed_trade(A):
    basis = gf2_nullspace_basis(A)
    d = len(basis)
    for mask in range(1, 1 << d):
        z = 0
        for b, vec in enumerate(basis):
            if (mask >> b) & 1:
                z ^= vec
        adj = contracted_adj(A, z)
        unseen = set(adj)
        while unseen:
            root = next(iter(unseen))
            comp = {root}
            q = deque([root])
            unseen.remove(root)
            while q:
                u = q.popleft()
                for v in adj[u]:
                    if v in unseen:
                        unseen.remove(v)
                        comp.add(v)
                        q.append(v)
            sub = {u: [v for v in adj[u] if v in comp] for u in comp}
            if is_bipartite(sub):
                return True
    return False


def first_incidence(A):
    for i, row in enumerate(A):
        for j, v in enumerate(row):
            if v:
                return i, j
    raise AssertionError("empty incidence")


def one_edge_twist_lift(A, edge):
    n = len(A)
    i0, j0 = edge
    assert A[i0][j0] == 1
    L = [[0]*(2*n) for _ in range(2*n)]
    for i, row in enumerate(A):
        for j, v in enumerate(row):
            if not v:
                continue
            if (i, j) == edge:
                L[2*i][2*j+1] = 1
                L[2*i+1][2*j] = 1
            else:
                L[2*i][2*j] = 1
                L[2*i+1][2*j+1] = 1
    return L


def exact_one(A, x):
    return all(sum(x[j] for j, v in enumerate(row) if v) == 1 for row in A)


A = matrix_from_rows(SEED_ROWS, 18)
assert is_cubic_linear(A)
assert is_connected(A)
assert exact_one(A, SEED_MODEL)
assert rank_q(A) == 16
basis = gf2_nullspace_basis(A)
assert len(basis) == 2
assert not has_signed_trade(A)

expected = [
    (18, 2, 2),
    (36, 3, 4),
    (72, 5, 8),
]
levels = []
cur = A
model = list(SEED_MODEL)
for depth, (n_exp, kq_exp, k2_exp) in enumerate(expected):
    n = len(cur)
    kq = n-rank_q(cur)
    k2 = len(gf2_nullspace_basis(cur))
    assert (n, kq, k2) == (n_exp, kq_exp, k2_exp)
    assert is_cubic_linear(cur)
    assert is_connected(cur)
    assert not has_signed_trade(cur)
    assert exact_one(cur, model)
    lower = 1 + (n // 18)
    assert kq >= lower
    levels.append({
        "depth": depth,
        "n": n,
        "nullity_Q": kq,
        "nullity_F2": k2,
        "trade_free": True,
        "exact_one_seed_model_lift": True,
        "theorem_lower_bound": lower,
    })
    if depth + 1 < len(expected):
        cur = one_edge_twist_lift(cur, first_incidence(cur))
        model = [v for x in model for v in (x, x)]

out = {
    "status": "PASS_ONE_EDGE_TWIST_TRADEFREE_NULLITY_AMPLIFIER_REGRESSION",
    "seed": {
        "n": 18,
        "rank_Q": 16,
        "nullity_Q": 2,
        "nullity_F2": 2,
        "signed_trade_free": True,
        "exact_one_model": list(SEED_MODEL),
        "unique_model_reason": "SAT_PLUS_SIGNED_TRADE_FREE",
    },
    "levels": levels,
    "arbitrary_n_theorem": {
        "trade_free_preservation": "PROVED_IN_COMPANION_NOTE",
        "nullity_recurrence": "k_next >= 2*k-1",
        "n_recurrence": "n_next = 2*n",
        "family_bound": "k_t >= n_t/18 + 1",
        "route_A_trade_free_O_log_n": "FALSIFIED",
    },
    "enumeration_role": "OFFLINE_FALSIFIER_ONLY__FINITE_REGRESSION_NOT_THE_PROOF",
    "E8_D1": "EMPTY",
    "P_VS_NP": "OPEN",
    "P_EQ_NP": "NOT_PROVED",
}
print(json.dumps(out, sort_keys=True))
