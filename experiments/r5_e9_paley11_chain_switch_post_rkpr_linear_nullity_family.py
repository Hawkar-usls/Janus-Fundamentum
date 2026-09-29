#!/usr/bin/env python3
"""Exact regression checker for the Paley(11) chain-switch nullity family.

Requires sympy.  All ranks/nullspaces are over Q.
"""

from collections import deque
from itertools import combinations
import json
import sympy as sp

P = 11
RESIDUES = {1, 3, 4, 5, 9}
BASE_N = 55


def is_arc(u, v):
    return ((v - u) % P) in RESIDUES


def build_base():
    arcs = [(u, v) for u in range(P) for v in range(P) if u != v and is_arc(u, v)]
    arc_index = {e: i for i, e in enumerate(arcs)}

    triangles = []
    for tri in combinations(range(P), 3):
        out = {x: 0 for x in tri}
        tri_arcs = []
        for a, b in combinations(tri, 2):
            if is_arc(a, b):
                tri_arcs.append((a, b))
                out[a] += 1
            else:
                tri_arcs.append((b, a))
                out[b] += 1
        if sorted(out.values()) == [1, 1, 1]:
            triangles.append((tri, tuple(tri_arcs)))

    tri_index = {tri: i for i, (tri, _) in enumerate(triangles)}
    A = sp.zeros(len(triangles), len(arcs))
    for i, (_, tri_arcs) in enumerate(triangles):
        for e in tri_arcs:
            A[i, arc_index[e]] = 1

    return arcs, arc_index, triangles, tri_index, A


def row_supports(A):
    return [{j for j in range(A.cols) if A[i, j] != 0} for i in range(A.rows)]


def assert_linear(A):
    supp = row_supports(A)
    for i in range(A.rows):
        for j in range(i + 1, A.rows):
            assert len(supp[i] & supp[j]) <= 1, (i, j, supp[i] & supp[j])


def levi_connected(A):
    nrow, ncol = A.rows, A.cols
    adj = [[] for _ in range(nrow + ncol)]
    for i in range(nrow):
        for j in range(ncol):
            if A[i, j] != 0:
                adj[i].append(nrow + j)
                adj[nrow + j].append(i)
    seen = {0}
    q = deque([0])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                q.append(v)
    return len(seen) == nrow + ncol


def gradient_matrix(arcs):
    # p_0=0, columns correspond to p_1,...,p_10.
    G = sp.zeros(len(arcs), P - 1)
    for i, (u, v) in enumerate(arcs):
        if v != 0:
            G[i, v - 1] += 1
        if u != 0:
            G[i, u - 1] -= 1
    return G


def canonical_projective_row(row):
    vals = [sp.Rational(v) for v in list(row)]
    pivot = next((v for v in vals if v != 0), None)
    if pivot is None:
        return None
    return tuple(sp.cancel(v / pivot) for v in vals)


def projective_kernel_pairs(A):
    basis = A.nullspace()
    K = sp.Matrix.hstack(*basis)
    assert K.cols == A.cols - A.rank()
    seen = {}
    zero = []
    pairs = []
    for i in range(K.rows):
        key = canonical_projective_row(K.row(i))
        if key is None:
            zero.append(i)
        elif key in seen:
            pairs.append((seen[key], i))
        else:
            seen[key] = i
    return zero, pairs


def build_family(A0, t, r_right, c_right, r_left, c_left):
    A = sp.diag(*([A0] * t))
    for i in range(t - 1):
        R1 = i * BASE_N + r_right
        C1 = i * BASE_N + c_right
        R2 = (i + 1) * BASE_N + r_left
        C2 = (i + 1) * BASE_N + c_left
        assert A[R1, C1] == 1
        assert A[R2, C2] == 1
        assert A[R1, C2] == 0
        assert A[R2, C1] == 0
        A[R1, C1] = 0
        A[R2, C2] = 0
        A[R1, C2] = 1
        A[R2, C1] = 1
    return A


def main():
    arcs, arc_index, triangles, tri_index, A0 = build_base()

    assert len(arcs) == 55
    assert len(triangles) == 55
    assert A0.rows == A0.cols == 55
    assert {sum(A0[i, j] for j in range(55)) for i in range(55)} == {3}
    assert {sum(A0[i, j] for i in range(55)) for j in range(55)} == {3}
    assert_linear(A0)
    assert levi_connected(A0)

    G = gradient_matrix(arcs)
    assert G.rank() == 10
    assert A0 * G == sp.zeros(55, 10)
    assert A0.rank() == 45
    assert 55 - A0.rank() == 10

    # Left-null coordinate support: no row coordinate vanishes identically.
    left_basis = A0.T.nullspace()
    assert len(left_basis) == 10
    L = sp.Matrix.hstack(*left_basis)
    assert all(any(L[i, j] != 0 for j in range(L.cols)) for i in range(55))

    r_right = tri_index[(0, 1, 2)]
    c_right = arc_index[(0, 1)]
    r_left = tri_index[(0, 1, 6)]
    c_left = arc_index[(1, 6)]
    assert (r_right, c_right, r_left, c_left) == (0, 0, 1, 8)

    # Selected gradient functionals are nonzero and nonproportional.
    assert canonical_projective_row(G.row(c_right)) != canonical_projective_row(G.row(c_left))

    reports = []
    expected_values = {
        1: (55, 45, 10),
        2: (110, 91, 19),
        3: (165, 137, 28),
        4: (220, 183, 37),
    }

    for t in range(1, 5):
        A = build_family(A0, t, r_right, c_right, r_left, c_left)
        n = A.rows
        assert A.cols == n == 55 * t
        assert {sum(A[i, j] for j in range(n)) for i in range(n)} == {3}
        assert {sum(A[i, j] for i in range(n)) for j in range(n)} == {3}
        assert_linear(A)
        assert levi_connected(A)

        rank = A.rank()
        nullity = n - rank
        assert nullity == 9 * t + 1
        assert (n, rank, nullity) == expected_values[t]

        zero, pairs = projective_kernel_pairs(A)
        expected_pairs = [
            (i * 55 + c_right, (i + 1) * 55 + c_left)
            for i in range(t - 1)
        ]
        assert zero == []
        assert pairs == expected_pairs, (t, pairs, expected_pairs)

        reports.append(
            {
                "t": t,
                "n": n,
                "rank_Q": rank,
                "nullity_Q": nullity,
                "zero_kernel_rows": len(zero),
                "projective_pairs": pairs,
                "expected_rkpr_equalities": t - 1,
                "linear": True,
                "levi_connected": True,
            }
        )

    assert reports[2]["n"] % 3 == 0  # t=3 passes the global n mod 3 gate.

    print(json.dumps({
        "status": "PASS",
        "base": {
            "arcs": 55,
            "cyclic_triangles": 55,
            "rank_Q": 45,
            "nullity_Q": 10,
            "kernel": "vertex-potential gradients",
        },
        "family_formula": "nullity_Q(A_t)=9*t+1",
        "post_RKPR_quotient_classes": "q_t=54*t+1",
        "scope_firewall": "single-switch chain has nontrivial 2-edge interface cuts",
        "reports": reports,
        "P_VS_NP": "OPEN",
    }, indent=2))


if __name__ == "__main__":
    main()
