#!/usr/bin/env python3
"""Exact checker for R5_E9_PALEY_VOLTAGE_POST_RKPR_LINEAR_NULLITY_FAMILY.

The checker reconstructs the finite seed and repaired 3-cover using exact
integer/rational arithmetic.  The infinite-family step is algebraic and uses
only the checked finite premises recorded at the end.
"""

from collections import Counter, deque
from itertools import combinations

import sympy as sp


RESIDUES = {1, 3, 4, 5, 9}
VOLTAGES = {
    (14, 50): 1,
    (13, 4): 1,
    (43, 44): 1,
    (44, 21): 1,
    (12, 3): 2,
    (41, 52): 1,
    (8, 35): 2,
    (30, 27): 2,
}


def paley11():
    vertices = list(range(11))
    arcs = [
        (i, j)
        for i in vertices
        for j in vertices
        if i != j and ((j - i) % 11) in RESIDUES
    ]
    arcset = set(arcs)

    cyclic = []
    for tri in combinations(vertices, 3):
        out = {v: 0 for v in tri}
        for u, v in combinations(tri, 2):
            if (u, v) in arcset:
                out[u] += 1
            else:
                out[v] += 1
        if sorted(out.values()) == [1, 1, 1]:
            cyclic.append(tri)

    idx = {e: i for i, e in enumerate(arcs)}
    A = sp.zeros(len(cyclic), len(arcs))
    for r, tri in enumerate(cyclic):
        for u, v in combinations(tri, 2):
            e = (u, v) if (u, v) in arcset else (v, u)
            A[r, idx[e]] = 1
    return A, cyclic, arcs


def cyclic_lift(A, k, voltages):
    n = A.rows
    M = sp.zeros(n * k, n * k)
    for r in range(n):
        for c in range(n):
            if A[r, c] == 0:
                continue
            shift = voltages.get((r, c), 0) % k
            for t in range(k):
                M[r * k + t, c * k + ((t + shift) % k)] = 1
    return M


def rank_mod_p(M, p):
    a = [[int(M[i, j]) % p for j in range(M.cols)] for i in range(M.rows)]
    r = 0
    for c in range(M.cols):
        pivot = next((i for i in range(r, M.rows) if a[i][c] % p), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        inv = pow(a[r][c], -1, p)
        a[r] = [(x * inv) % p for x in a[r]]
        for i in range(M.rows):
            if i == r or a[i][c] == 0:
                continue
            f = a[i][c]
            a[i] = [(a[i][j] - f * a[r][j]) % p for j in range(M.cols)]
        r += 1
        if r == M.rows:
            break
    return r


def supports(M):
    return [tuple(c for c in range(M.cols) if M[r, c]) for r in range(M.rows)]


def is_linear_cubic(M):
    rs = supports(M)
    assert all(len(s) == 3 for s in rs)
    col_deg = [sum(1 for r in range(M.rows) if M[r, c]) for c in range(M.cols)]
    assert all(d == 3 for d in col_deg)
    sets = [set(s) for s in rs]
    assert all(len(sets[i] & sets[j]) <= 1 for i in range(len(sets)) for j in range(i + 1, len(sets)))


def levi_connected(M, removed_edge=None):
    n = M.rows
    adj = [[] for _ in range(2 * n)]
    for r in range(n):
        for c in range(n):
            if M[r, c]:
                u, v = r, n + c
                if removed_edge is not None and {u, v} == set(removed_edge):
                    continue
                adj[u].append(v)
                adj[v].append(u)
    seen = {0}
    q = deque([0])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                q.append(v)
    return len(seen) == 2 * n


def kernel_projective_classes(M):
    ns = M.nullspace()
    K = sp.Matrix.hstack(*ns)
    rows = [tuple(K[i, j] for j in range(K.cols)) for i in range(K.rows)]
    assert all(any(x != 0 for x in row) for row in rows)

    normalized = []
    for row in rows:
        first = next(x for x in row if x != 0)
        normalized.append(tuple(sp.cancel(x / first) for x in row))

    buckets = {}
    for i, key in enumerate(normalized):
        buckets.setdefault(key, []).append(i)

    # Every non-singleton projective class in this base must be literal equality,
    # not merely another scalar ratio.
    for members in buckets.values():
        if len(members) > 1:
            ref = rows[members[0]]
            assert all(rows[i] == ref for i in members[1:])

    return K, list(buckets.values())


def main():
    A0, cyclic, arcs = paley11()
    assert A0.shape == (55, 55)
    assert len(cyclic) == len(arcs) == 55
    is_linear_cubic(A0)
    assert levi_connected(A0)
    assert A0.rank() == 45
    K0, cls0 = kernel_projective_classes(A0)
    assert K0.cols == 10
    assert all(len(g) == 1 for g in cls0)

    expected_semantic_voltages = {
        (14, cyclic[14], 50, arcs[50], 1),
        (13, cyclic[13], 4, arcs[4], 1),
        (43, cyclic[43], 44, arcs[44], 1),
        (44, cyclic[44], 21, arcs[21], 1),
        (12, cyclic[12], 3, arcs[3], 2),
        (41, cyclic[41], 52, arcs[52], 1),
        (8, cyclic[8], 35, arcs[35], 2),
        (30, cyclic[30], 27, arcs[27], 2),
    }
    assert expected_semantic_voltages == {
        (14, (0, 9, 10), 50, (10, 0), 1),
        (13, (0, 7, 9), 4, (0, 9), 1),
        (43, (3, 8, 9), 44, (8, 9), 1),
        (44, (4, 5, 6), 21, (4, 5), 1),
        (12, (0, 5, 10), 3, (0, 5), 2),
        (41, (3, 6, 10), 52, (10, 3), 1),
        (8, (0, 4, 7), 35, (7, 0), 2),
        (30, (2, 5, 8), 27, (5, 8), 2),
    }

    B = cyclic_lift(A0, 3, VOLTAGES)
    assert B.shape == (165, 165)
    is_linear_cubic(B)
    assert levi_connected(B)

    rank_q = B.rank()
    assert rank_q == 149
    assert B.cols - rank_q == 16

    one = sp.ones(B.rows, 1)
    for p, expected in ((2, 149), (3, 148)):
        r = rank_mod_p(B, p)
        ra = rank_mod_p(B.row_join(one), p)
        assert (r, ra) == (expected, expected)

    K, classes = kernel_projective_classes(B)
    assert K.cols == 16
    sizes = Counter(len(g) for g in classes)
    assert sizes == Counter({1: 81, 3: 28})

    class_of = {}
    for j, members in enumerate(classes):
        for c in members:
            class_of[c] = j
    assert len(classes[class_of[0]]) == 1  # c* is singleton

    # Equality quotient creates no repeated variable inside a source row.
    for row in supports(B):
        assert len({class_of[c] for c in row}) == 3

    # e_{r*} is not in col_Q(B): this is the key exact-kernel premise.
    e0 = sp.zeros(B.rows, 1)
    e0[0] = 1
    assert B.row_join(e0).rank() == 150

    # The distinguished incidence is on a cycle: after deleting it, its two
    # endpoints remain connected.  Hence voltage 1 generates a connected
    # cyclic m-cover for every m.
    assert B[0, 0] == 1
    n = B.rows
    # A full connectedness check after deleting the edge is stronger than needed.
    assert levi_connected(B, removed_edge=(0, n + 0))

    # Checked premises imply for every m >= 1:
    #   N_m = 165m,
    #   nullity_Q(C_m) = 16m-(m-1) = 15m+1,
    #   q_RKPR(C_m) = 28m + 80m + 1 = 108m+1,
    # with only equality projective classes.  Repeating an F2/F3 base solution
    # on all sheets proves parity/phase consistency of every C_m.

    print("PASS R5_E9_PALEY_VOLTAGE_POST_RKPR_LINEAR_NULLITY_FAMILY")
    print("A0: n=55 rank_Q=45 nullity_Q=10 projectively_simple=true")
    print("B : n=165 rank_Q=149 nullity_Q=16 rank_F2=149 rank_F3=148")
    print("B RKPR: 28 equality triples + 81 singletons; no pins/illegal ratios")
    print("family: N=165m nullity_Q=15m+1=N/11+1 q_RKPR=108m+1")


if __name__ == "__main__":
    main()
