#!/usr/bin/env python3
"""Exact regressions for the bidirected cycle-kernel / binet router.

The controls use unsigned cubic graph incidence matrices.  Interpreting every
edge as a two-head bidirected link makes the bidirected incidence D equal to A.
Thus Exact-One is exactly perfect matching / unit-capacity b-matching.

Only the Python standard library is used.  Rational elimination uses Fraction.
"""

from fractions import Fraction
from functools import lru_cache
from itertools import combinations


def rank_q(rows):
    a = [[Fraction(x) for x in row] for row in rows]
    if not a:
        return 0
    m, n = len(a), len(a[0])
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if a[i][c] != 0), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        z = a[r][c]
        a[r] = [v / z for v in a[r]]
        for i in range(m):
            if i == r or a[i][c] == 0:
                continue
            z = a[i][c]
            a[i] = [a[i][j] - z * a[r][j] for j in range(n)]
        r += 1
        if r == m:
            break
    return r


def inverse_q(a):
    n = len(a)
    aug = [
        [Fraction(x) for x in row]
        + [Fraction(int(i == j)) for j in range(n)]
        for i, row in enumerate(a)
    ]
    for c in range(n):
        pivot = next((i for i in range(c, n) if aug[i][c] != 0), None)
        assert pivot is not None
        aug[c], aug[pivot] = aug[pivot], aug[c]
        z = aug[c][c]
        aug[c] = [v / z for v in aug[c]]
        for i in range(n):
            if i == c or aug[i][c] == 0:
                continue
            z = aug[i][c]
            aug[i] = [aug[i][j] - z * aug[c][j] for j in range(2 * n)]
    return [row[n:] for row in aug]


def matmul(a, b):
    return [
        [sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0]))]
        for i in range(len(a))
    ]


def pivot_normalize_full_row_rank(A):
    r = rank_q(A)
    assert r == len(A)
    pivots = []
    cur = 0
    for j in range(len(A[0])):
        candidate = [[row[k] for k in pivots + [j]] for row in A]
        rr = rank_q(candidate)
        if rr > cur:
            pivots.append(j)
            cur = rr
            if cur == r:
                break
    assert len(pivots) == r
    B = [[A[i][j] for j in pivots] for i in range(r)]
    F = matmul(inverse_q(B), [[Fraction(x) for x in row] for row in A])
    return pivots, F


def det3(M):
    return (
        M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1])
        - M[0][1] * (M[1][0] * M[2][2] - M[1][2] * M[2][0])
        + M[0][2] * (M[1][0] * M[2][1] - M[1][1] * M[2][0])
    )


def first_non_tu_minor(F, max_order=3):
    m, n = len(F), len(F[0])
    for k in range(2, max_order + 1):
        for rs in combinations(range(m), k):
            for cs in combinations(range(n), k):
                sub = [[F[i][j] for j in cs] for i in rs]
                if k == 2:
                    det = sub[0][0] * sub[1][1] - sub[0][1] * sub[1][0]
                else:
                    det = det3(sub)
                if abs(det) > 1:
                    return k, rs, cs, det
    return None


def unsigned_incidence(nv, edges):
    A = [[0] * len(edges) for _ in range(nv)]
    for j, (u, v) in enumerate(edges):
        assert u != v
        A[u][j] = 1
        A[v][j] = 1
    return A


def degrees(nv, edges):
    d = [0] * nv
    for u, v in edges:
        d[u] += 1
        d[v] += 1
    return d


def perfect_matching_exists(nv, edges):
    adj = [0] * nv
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u

    @lru_cache(None)
    def rec(mask):
        if mask == 0:
            return True
        u = (mask & -mask).bit_length() - 1
        nbrs = adj[u] & mask
        while nbrs:
            bit = nbrs & -nbrs
            v = bit.bit_length() - 1
            if rec(mask & ~(1 << u) & ~(1 << v)):
                return True
            nbrs -= bit
        return False

    return rec((1 << nv) - 1)


def components_after_delete(nv, edges, deleted):
    adj = [[] for _ in range(nv)]
    for u, v in edges:
        if u == deleted or v == deleted:
            continue
        adj[u].append(v)
        adj[v].append(u)
    seen = {deleted}
    sizes = []
    for s in range(nv):
        if s in seen:
            continue
        stack = [s]
        seen.add(s)
        count = 0
        while stack:
            u = stack.pop()
            count += 1
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        sizes.append(count)
    return sorted(sizes)


def check_petersen_sat():
    # Outer 5-cycle, five spokes, inner 5-star.
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 4), (4, 0),
        (0, 5), (1, 6), (2, 7), (3, 8), (4, 9),
        (5, 7), (7, 9), (9, 6), (6, 8), (8, 5),
    ]
    nv = 10
    assert degrees(nv, edges) == [3] * nv
    A = unsigned_incidence(nv, edges)
    assert rank_q(A) == 10
    assert len(edges) - rank_q(A) == 5

    # D=A as all-two-head bidirected incidence.  Hence D1/3 = 1 exactly.
    assert [sum(row) for row in A] == [3] * nv

    # Explicit perfect matching: all five spokes.
    spoke_set = {(0, 5), (1, 6), (2, 7), (3, 8), (4, 9)}
    x = [int(e in spoke_set) for e in edges]
    assert [sum(row[j] * x[j] for j in range(len(edges))) for row in A] == [1] * nv
    assert perfect_matching_exists(nv, edges)

    # Strictness: exact pivot normalization is not ordinary network/TU.
    pivots, F = pivot_normalize_full_row_rank(A)
    bad = first_non_tu_minor(F, max_order=3)
    assert bad is not None and abs(bad[3]) == 2

    return {
        "name": "Petersen",
        "n_vertices": nv,
        "n_edges": len(edges),
        "rank": rank_q(A),
        "nullity": len(edges) - rank_q(A),
        "pivots": pivots,
        "bad_minor": bad,
    }


def check_three_balloon_unsat():
    # Same 16-vertex graph as the theorem, with a fixed edge order chosen so
    # the deterministic pivot-normalization strictness control is reproducible.
    # Vertex 0 is central; vertices 5,10,15 are subdivision/bridge vertices.
    edges = [
        (1, 3), (1, 4), (1, 5), (3, 2), (3, 4), (4, 2), (2, 5), (5, 0),
        (0, 10), (0, 15),
        (6, 8), (6, 9), (6, 10), (8, 7), (8, 9), (9, 7), (7, 10),
        (11, 13), (11, 14), (11, 15), (13, 12), (13, 14), (14, 12), (12, 15),
    ]
    nv = 16
    assert degrees(nv, edges) == [3] * nv
    A = unsigned_incidence(nv, edges)
    assert rank_q(A) == 16
    assert len(edges) - rank_q(A) == 8
    assert [sum(row) for row in A] == [3] * nv

    # Exact Tutte/parity certificate at S={0}: three odd components of size 5.
    comps = components_after_delete(nv, edges, 0)
    assert comps == [5, 5, 5]
    assert len(comps) > 1

    # Independent exact recursive replay.
    assert not perfect_matching_exists(nv, edges)

    # Strictness: normalized [I|N] has a determinant-2 minor, hence is not TU/network.
    pivots, F = pivot_normalize_full_row_rank(A)
    bad = first_non_tu_minor(F, max_order=2)
    assert bad is not None and abs(bad[3]) == 2

    return {
        "name": "G16-three-balloon",
        "n_vertices": nv,
        "n_edges": len(edges),
        "rank": rank_q(A),
        "nullity": len(edges) - rank_q(A),
        "odd_components_after_center": comps,
        "pivots": pivots,
        "bad_minor": bad,
    }


def main():
    sat = check_petersen_sat()
    unsat = check_three_balloon_unsat()

    print("Exact bidirected cycle-kernel / binet router regression: PASS")
    print(
        f"SAT {sat['name']}: V={sat['n_vertices']} E={sat['n_edges']} "
        f"rank={sat['rank']} nullity={sat['nullity']} bad_minor={sat['bad_minor']}"
    )
    print(
        f"UNSAT {unsat['name']}: V={unsat['n_vertices']} E={unsat['n_edges']} "
        f"rank={unsat['rank']} nullity={unsat['nullity']} "
        f"odd_components={unsat['odd_components_after_center']} "
        f"bad_minor={unsat['bad_minor']}"
    )
    print("D=A all-two-head bidirected representation: PASS")
    print("ordinary network/TU strictness: PASS")
    print("perfect-matching positive/negative replay: PASS")


if __name__ == "__main__":
    main()
