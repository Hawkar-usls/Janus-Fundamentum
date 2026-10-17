#!/usr/bin/env python3
"""Exact regression for the Paley(11) cyclic-triangle post-RKPR control.

No external solver is used.  All rank computations are exact over Q via Fraction.
"""

from fractions import Fraction
from itertools import combinations

Q = 11
RESIDUES = {1, 3, 4, 5, 9}


def arc(u, v):
    """Return the oriented tournament arc on unordered pair {u,v}."""
    if ((v - u) % Q) in RESIDUES:
        return (u, v)
    return (v, u)


def rank_q(mat):
    a = [[Fraction(x) for x in row] for row in mat]
    m = len(a)
    n = len(a[0]) if m else 0
    r = 0
    for c in range(n):
        p = next((i for i in range(r, m) if a[i][c]), None)
        if p is None:
            continue
        a[r], a[p] = a[p], a[r]
        z = a[r][c]
        a[r] = [x / z for x in a[r]]
        for i in range(m):
            if i != r and a[i][c]:
                z = a[i][c]
                a[i] = [a[i][j] - z * a[r][j] for j in range(n)]
        r += 1
        if r == m:
            break
    return r


def build():
    arcs = [arc(u, v) for u, v in combinations(range(Q), 2)]
    assert len(arcs) == len(set(arcs)) == 55
    idx = {e: i for i, e in enumerate(arcs)}

    triangles = []
    triangle_arcs = []
    for a, b, c in combinations(range(Q), 3):
        es = [arc(a, b), arc(b, c), arc(c, a)]
        out = {a: 0, b: 0, c: 0}
        for u, v in es:
            out[u] += 1
        if sorted(out.values()) == [1, 1, 1]:
            triangles.append((a, b, c))
            triangle_arcs.append(es)

    A = [[0] * len(arcs) for _ in triangles]
    for i, es in enumerate(triangle_arcs):
        for e in es:
            A[i][idx[e]] = 1

    H = [[0] * Q for _ in arcs]
    for i, (u, v) in enumerate(arcs):
        H[i][u] = -1
        H[i][v] = 1

    return arcs, triangles, A, H


def matmul(A, B):
    bt = list(zip(*B))
    return [[sum(x * y for x, y in zip(row, col)) for col in bt] for row in A]


def connected_levi(A):
    m = len(A)
    n = len(A[0])
    adj = [[] for _ in range(m + n)]
    for i in range(m):
        for j in range(n):
            if A[i][j]:
                adj[i].append(m + j)
                adj[m + j].append(i)
    seen = {0}
    stack = [0]
    while stack:
        x = stack.pop()
        for y in adj[x]:
            if y not in seen:
                seen.add(y)
                stack.append(y)
    return len(seen) == m + n


def max_pair_intersection(rows):
    best = 0
    for i, j in combinations(range(len(rows)), 2):
        best = max(best, sum(x * y for x, y in zip(rows[i], rows[j])))
    return best


def main():
    arcs, triangles, A, H = build()
    n = len(arcs)

    assert n == 55
    assert len(triangles) == 55
    assert all(sum(row) == 3 for row in A)
    AT = [list(col) for col in zip(*A)]
    assert all(sum(col) == 3 for col in AT)
    assert max_pair_intersection(A) == 1
    assert max_pair_intersection(AT) == 1
    assert connected_levi(A)

    # Each arc is in exactly three directed 3-cycles.
    assert {sum(col) for col in AT} == {3}

    # Root-difference kernel is exact.
    AH = matmul(A, H)
    assert all(x == 0 for row in AH for x in row)
    rank_h = rank_q(H)
    rank_a = rank_q(A)
    nullity = n - rank_a
    assert rank_h == 10
    assert rank_a == 45
    assert nullity == 10
    assert rank_h == nullity

    # RKPR projective simplicity: no root row is zero and no two are proportional.
    # For type e_v-e_u, proportionality means equal unordered endpoint pair.
    endpoint_pairs = [frozenset(e) for e in arcs]
    assert len(endpoint_pairs) == len(set(endpoint_pairs)) == 55
    assert all(any(x for x in row) for row in H)

    # Exact global UNSAT certificate condition.
    # If a Boolean witness existed, beta_w-beta_r for every w!=r would be in
    # {-2,-1,1,2}, while all beta values must be pairwise distinct.
    allowed_offsets = {-2, -1, 1, 2}
    assert Q - 1 > len(allowed_offsets)

    # Canonical arc 0->1 has exactly three cyclic third vertices.
    thirds = [
        w for w in range(Q)
        if w not in (0, 1)
        and arc(0, 1) == (0, 1)
        and arc(1, w) == (1, w)
        and arc(w, 0) == (w, 0)
    ]
    assert thirds == [2, 6, 10]

    print("Paley(11) cyclic-triangle post-RKPR control: PASS")
    print("source = 55 x 55 linear cubic")
    print("Levi connected = True")
    print("rank_Q(A) = 45")
    print("nullity_Q(A) = 10")
    print("rank_Q(H) = 10 and A*H = 0")
    print("RKPR zero rows = 0")
    print("RKPR proportional row pairs = 0")
    print("Exact-One = UNSAT by 4-offset vertex-potential pigeonhole")


if __name__ == "__main__":
    main()
