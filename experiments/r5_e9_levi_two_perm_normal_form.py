#!/usr/bin/env python3
"""Executable regression checker for the R5 E9 Levi / two-permutation theorem.

This checker is deliberately small and dependency-free.  It verifies the exact
bijections and normalization on a 9_3 linear configuration obtained from three
parallel classes of AG(2,3).  It is a regression certificate for the theorem,
not a proof of a polynomial solver for the open residual.
"""

from fractions import Fraction
from itertools import product
from collections import deque


def build_ag23_three_classes():
    pts = [(x, y) for x in range(3) for y in range(3)]
    rows = []
    # x = c
    for c in range(3):
        rows.append([i for i, (x, y) in enumerate(pts) if x == c])
    # y = c
    for c in range(3):
        rows.append([i for i, (x, y) in enumerate(pts) if y == c])
    # y - x = c
    for c in range(3):
        rows.append([i for i, (x, y) in enumerate(pts) if (y - x) % 3 == c])

    n = len(pts)
    A = [[0] * n for _ in range(n)]
    for r, cols in enumerate(rows):
        for c in cols:
            A[r][c] = 1
    return A


def supports(A):
    return [[j for j, v in enumerate(row) if v] for row in A]


def validate_carrier(A):
    n = len(A)
    assert all(len(row) == n for row in A)
    rs = supports(A)
    assert all(len(s) == 3 for s in rs)
    col_deg = [sum(A[r][c] for r in range(n)) for c in range(n)]
    assert col_deg == [3] * n
    # linearity: no pair of columns occurs in two rows
    seen = set()
    for s in rs:
        for i in range(3):
            for j in range(i + 1, 3):
                pair = tuple(sorted((s[i], s[j])))
                assert pair not in seen
                seen.add(pair)
    return rs


def exact_one(A, x):
    return all(sum(v * bit for v, bit in zip(row, x)) == 1 for row in A)


def levi_factor_condition(A, x):
    """Factor determined by x: all three incidences of a selected column."""
    n = len(A)
    left_deg = [0] * n
    right_deg = [0] * n
    for r in range(n):
        for c in range(n):
            if A[r][c] and x[c]:
                left_deg[r] += 1
                right_deg[c] += 1
    return all(d == 1 for d in left_deg) and all(d in (0, 3) for d in right_deg)


def dual_perfect_matching_condition(A, x):
    # Selected dual hyperedges are original columns; every dual vertex is an
    # original row and must be covered exactly once.
    n = len(A)
    cover = [sum(A[r][c] * x[c] for c in range(n)) for r in range(n)]
    return cover == [1] * n


def perfect_matching(adj, forbidden=None):
    """Kuhn augmenting-path matching from every left vertex to a right vertex."""
    n = len(adj)
    forbidden = forbidden or set()
    match_r = [-1] * n

    def dfs(u, seen):
        for v in adj[u]:
            if (u, v) in forbidden or seen[v]:
                continue
            seen[v] = True
            if match_r[v] == -1 or dfs(match_r[v], seen):
                match_r[v] = u
                return True
        return False

    for u in range(n):
        if not dfs(u, [False] * n):
            raise AssertionError("expected perfect matching in cubic bipartite Levi graph")

    left_to_right = [-1] * n
    for v, u in enumerate(match_r):
        left_to_right[u] = v
    assert sorted(left_to_right) == list(range(n))
    return left_to_right


def decompose_three_matchings(A):
    adj = supports(A)
    m0 = perfect_matching(adj)
    f0 = {(u, m0[u]) for u in range(len(A))}
    m1 = perfect_matching(adj, f0)
    f1 = {(u, m1[u]) for u in range(len(A))}
    m2 = []
    for u, nbrs in enumerate(adj):
        rem = [v for v in nbrs if (u, v) not in f0 and (u, v) not in f1]
        assert len(rem) == 1
        m2.append(rem[0])
    assert sorted(m2) == list(range(len(A)))
    return m0, m1, m2


def normalize_rows(A, m0, m1, m2):
    """Return row-reordered A' = P0^T A and permutations p,q.

    If original matching m0 maps row r -> column j, normalized row j is
    original row r.  Thus the identity matching is explicit.
    """
    n = len(A)
    inv0 = [-1] * n
    for r, c in enumerate(m0):
        inv0[c] = r
    Aprime = [A[inv0[j]][:] for j in range(n)]
    p = [m1[inv0[j]] for j in range(n)]
    q = [m2[inv0[j]] for j in range(n)]
    assert sorted(p) == list(range(n))
    assert sorted(q) == list(range(n))
    for i in range(n):
        assert len({i, p[i], q[i]}) == 3
        assert [j for j, bit in enumerate(Aprime[i]) if bit] == sorted([i, p[i], q[i]])
    return Aprime, p, q


def rank_q(M):
    a = [[Fraction(v) for v in row] for row in M]
    m = len(a)
    n = len(a[0]) if m else 0
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if a[i][c]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        pv = a[r][c]
        a[r] = [v / pv for v in a[r]]
        for i in range(m):
            if i != r and a[i][c]:
                f = a[i][c]
                a[i] = [a[i][j] - f * a[r][j] for j in range(n)]
        r += 1
        if r == m:
            break
    return r


def levi_connected(A):
    n = len(A)
    # vertices 0..n-1 are rows, n..2n-1 are columns
    graph = [[] for _ in range(2 * n)]
    for r in range(n):
        for c in range(n):
            if A[r][c]:
                graph[r].append(n + c)
                graph[n + c].append(r)
    seen = {0}
    dq = deque([0])
    while dq:
        u = dq.popleft()
        for v in graph[u]:
            if v not in seen:
                seen.add(v)
                dq.append(v)
    return len(seen) == 2 * n


def inverse_perm(p):
    inv = [-1] * len(p)
    for i, j in enumerate(p):
        inv[j] = i
    return inv


def generated_orbit(p, q, start=0):
    pinv, qinv = inverse_perm(p), inverse_perm(q)
    gens = (p, q, pinv, qinv)
    seen = {start}
    dq = deque([start])
    while dq:
        i = dq.popleft()
        for g in gens:
            j = g[i]
            if j not in seen:
                seen.add(j)
                dq.append(j)
    return seen


def verify_pair_linearity(Aprime, p, q):
    n = len(Aprime)
    seen = set()
    for i in range(n):
        triple = [i, p[i], q[i]]
        assert len(set(triple)) == 3
        for a in range(3):
            for b in range(a + 1, 3):
                pair = tuple(sorted((triple[a], triple[b])))
                assert pair not in seen
                seen.add(pair)


def main():
    A = build_ag23_three_classes()
    validate_carrier(A)
    n = len(A)

    # Exhaustively verify the two exact witness representations on all 2^9
    # Boolean assignments.
    witnesses = []
    for bits in product((0, 1), repeat=n):
        ex1 = exact_one(A, bits)
        assert ex1 == levi_factor_condition(A, bits)
        assert ex1 == dual_perfect_matching_condition(A, bits)
        if ex1:
            witnesses.append(bits)
    assert len(witnesses) == 3

    # Polynomial Levi decomposition A = P0 + P1 + P2 and exact normalization.
    m0, m1, m2 = decompose_three_matchings(A)
    for r in range(n):
        assert set((m0[r], m1[r], m2[r])) == set(supports(A)[r])

    Aprime, p, q = normalize_rows(A, m0, m1, m2)
    validate_carrier(Aprime)
    verify_pair_linearity(Aprime, p, q)

    # Row permutation preserves Exact-One assignments and rational nullity.
    for bits in product((0, 1), repeat=n):
        assert exact_one(A, bits) == exact_one(Aprime, bits)
    rank_A = rank_q(A)
    rank_Ap = rank_q(Aprime)
    assert rank_A == rank_Ap == 7
    assert n - rank_A == n - rank_Ap == 2

    # Connected Levi graph iff generated permutation group is transitive.
    conn = levi_connected(Aprime)
    orbit = generated_orbit(p, q)
    assert conn
    assert len(orbit) == n
    assert conn == (len(orbit) == n)

    # Check the two-valued rational-kernel law for every witness.
    for x in witnesses:
        w = [3 * bit - 1 for bit in x]
        for i in range(n):
            # Aprime = I + P + Q rowwise.
            assert w[i] + w[p[i]] + w[q[i]] == 0
            local = sorted((w[i], w[p[i]], w[q[i]]))
            assert local == [-1, -1, 2]

    print("PASS: R5_E9_LEVI_GENERAL_FACTOR_TWO_PERM_NORMAL_FORM")
    print(f"n={n} rank_Q={rank_A} nullity_Q={n-rank_A} witnesses={len(witnesses)}")
    print("A' = I + P + Q verified; <p,q> is transitive; local law=(-1,-1,2).")
    print("E8_D1=EMPTY; P_VS_NP=OPEN")


if __name__ == "__main__":
    main()
