#!/usr/bin/env python3
"""Exhaust every perfect-matching normalization of AFFINE_3X3.

OFFLINE_FALSIFIER_ONLY.  The finite control falsifies the direct endpoint
projected-delta-matroid normalization route; it is not universal proof evidence.
"""

from __future__ import annotations

from itertools import product


def incidence(n: int, blocks: list[tuple[int, ...]]) -> list[list[int]]:
    A = [[0] * n for _ in blocks]
    for i, block in enumerate(blocks):
        for j in block:
            A[i][j] = 1
    return A


def all_perfect_matchings(A: list[list[int]]) -> list[tuple[int, ...]]:
    n = len(A)
    used = [False] * n
    cur = [-1] * n
    out: list[tuple[int, ...]] = []

    def rec(i: int) -> None:
        if i == n:
            out.append(tuple(cur))
            return
        for j in range(n):
            if A[i][j] and not used[j]:
                used[j] = True
                cur[i] = j
                rec(i + 1)
                used[j] = False

    rec(0)
    return out


def cycle_orders(adj: list[list[int]]) -> list[list[int]]:
    seen: set[int] = set()
    orders: list[list[int]] = []
    for s in range(len(adj)):
        if s in seen:
            continue
        order = [s]
        seen.add(s)
        prev = None
        cur = s
        while True:
            choices = [v for v in adj[cur] if v != prev]
            assert choices
            nxt = choices[0]
            if nxt == s:
                break
            assert nxt not in seen
            order.append(nxt)
            seen.add(nxt)
            prev, cur = cur, nxt
        orders.append(order)
    return orders


def dm_witness(feasible: list[frozenset[int]]):
    F = set(feasible)
    for X in F:
        for Y in F:
            diff = X ^ Y
            for e in diff:
                ok = False
                for f in diff:
                    toggle = {e} if e == f else {e, f}
                    if frozenset(set(X) ^ toggle) in F:
                        ok = True
                        break
                if not ok:
                    return X, Y, e
    return None


def normalized_endpoint_family(A: list[list[int]], matching: tuple[int, ...]):
    n = len(A)

    # New column j is the old matched column of row j, so identity is present.
    B = [[A[i][matching[j]] for j in range(n)] for i in range(n)]
    assert all(B[i][i] == 1 for i in range(n))

    adj = [[] for _ in range(n)]
    for i in range(n):
        pair = [j for j in range(n) if B[i][j] and j != i]
        assert len(pair) == 2
        u, v = pair
        adj[u].append(v)
        adj[v].append(u)

    assert all(len(a) == 2 for a in adj)
    assert all(len(set(a)) == 2 for a in adj), "linearity should make C_M simple"
    orders = cycle_orders(adj)

    models = []
    for x in product((0, 1), repeat=n):
        if all(sum(B[i][j] * x[j] for j in range(n)) == 1 for i in range(n)):
            models.append(x)
    assert len(models) == 3

    # Map each C_M vertex j to edge (j,next(j)) of an isomorphic cycle.
    nxt = {}
    for order in orders:
        for t, j in enumerate(order):
            nxt[j] = order[(t + 1) % len(order)]

    endpoints = []
    for x in models:
        E: set[int] = set()
        selected = [j for j, bit in enumerate(x) if bit]
        assert len(selected) == 3
        for j in selected:
            E.add(j)
            E.add(nxt[j])
        assert len(E) == 6
        endpoints.append(frozenset(E))

    return orders, endpoints


def main() -> None:
    affine: list[tuple[int, ...]] = []
    for r in range(3):
        affine.append(tuple(3 * r + c for c in range(3)))
    for c in range(3):
        affine.append(tuple(3 * r + c for r in range(3)))
    for b in range(3):
        affine.append(tuple(3 * r + ((r + b) % 3) for r in range(3)))

    A = incidence(9, affine)
    matchings = all_perfect_matchings(A)
    assert len(matchings) == 42

    types: dict[tuple[int, ...], int] = {}
    dm_count = 0
    witnesses = []

    for M in matchings:
        orders, endpoint_family = normalized_endpoint_family(A, M)
        typ = tuple(sorted(len(C) for C in orders))
        types[typ] = types.get(typ, 0) + 1
        w = dm_witness(endpoint_family)
        if w is None:
            dm_count += 1
        else:
            witnesses.append(w)

    assert types == {(9,): 36, (3, 3, 3): 6}, types
    assert dm_count == 0
    assert len(witnesses) == 42

    print("PASS_AFFINE9_ENDPOINT_DELTA_MATROID_NORMALIZATION_FALSIFIER")
    print("perfect_matchings=42")
    print("cycle_types=C9:36,C3+C3+C3:6")
    print("delta_matroid_endpoint_families=0")
    print("E8_D1=EMPTY")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    main()
