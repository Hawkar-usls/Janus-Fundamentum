#!/usr/bin/env python3
"""Exact regression for the Paley(19) post-RKPR gradient-kernel control.

No floating point is used.  Rational rank of A is certified by:
  * explicit 18-dimensional gradient kernel A G = 0, and
  * rank(A mod p)=153 for p=1_000_003.
Together these force rank_Q(A)=153 and nullity_Q(A)=18.
"""

from itertools import combinations
from collections import Counter

QMOD = 19
PRIME = 1_000_003
QR = {1, 4, 5, 6, 7, 9, 11, 16, 17}
QR_ORDER = (1, 4, 5, 6, 7, 9, 11, 16, 17)
REPS = (
    (0, 1, 2),
    (0, 1, 10),
    (0, 2, 4),
    (0, 3, 6),
    (0, 3, 11),
    (0, 4, 8),
    (0, 5, 10),
    (0, 5, 12),
    (0, 6, 12),
)


def is_arc(u, v):
    return ((v - u) % QMOD) in QR


def oriented_arc(u, v):
    return (u, v) if is_arc(u, v) else (v, u)


def cyclic_triangle(tri):
    verts = list(tri)
    outdeg = []
    for u in verts:
        outdeg.append(sum(is_arc(u, v) for v in verts if v != u))
    return outdeg == [1, 1, 1]


def translate_tri(tri, s):
    return tuple(sorted(((x + s) % QMOD for x in tri)))


def tri_arcs(tri):
    return [oriented_arc(u, v) for u, v in combinations(tri, 2)]


def rank_mod(mat, p):
    a = [[x % p for x in row] for row in mat]
    m = len(a)
    n = len(a[0]) if m else 0
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if a[i][c]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        inv = pow(a[r][c], p - 2, p)
        a[r] = [(x * inv) % p for x in a[r]]
        for i in range(m):
            if i != r and a[i][c]:
                f = a[i][c]
                a[i] = [(a[i][j] - f * a[r][j]) % p for j in range(n)]
        r += 1
        if r == m:
            break
    return r


def matmul_int(a, b):
    m, k, n = len(a), len(b), len(b[0])
    out = [[0] * n for _ in range(m)]
    for i in range(m):
        for t in range(k):
            if a[i][t] == 0:
                continue
            z = a[i][t]
            for j in range(n):
                if b[t][j]:
                    out[i][j] += z * b[t][j]
    return out


def proportional_int(u, v):
    # Exact proportionality over Q for nonzero integer vectors.
    iu = next((i for i, x in enumerate(u) if x), None)
    iv = next((i for i, x in enumerate(v) if x), None)
    if iu is None or iv is None:
        return iu is None and iv is None
    # Pick one coordinate where u is nonzero; proportionality requires v there nonzero.
    i = iu
    if v[i] == 0:
        return False
    a, b = u[i], v[i]
    return all(u[j] * b == v[j] * a for j in range(len(u)))


def main():
    # Tournament sanity.
    for u, v in combinations(range(QMOD), 2):
        assert is_arc(u, v) ^ is_arc(v, u)

    # Selected orbits.
    for rep in REPS:
        assert cyclic_triangle(rep), rep
    triangles = []
    for rep in REPS:
        triangles.extend(translate_tri(rep, s) for s in range(QMOD))
    assert len(triangles) == 171
    assert len(set(triangles)) == 171
    assert all(cyclic_triangle(t) for t in triangles)

    # Tournament arcs.
    arcs = []
    for u, v in combinations(range(QMOD), 2):
        arcs.append(oriented_arc(u, v))
    assert len(arcs) == 171
    assert len(set(arcs)) == 171
    arc_index = {e: i for i, e in enumerate(arcs)}

    # Source matrix A.
    n = 171
    A = [[0] * n for _ in range(n)]
    for i, tri in enumerate(triangles):
        for e in tri_arcs(tri):
            A[i][arc_index[e]] = 1

    assert all(sum(row) == 3 for row in A)
    coldeg = [sum(A[i][j] for i in range(n)) for j in range(n)]
    assert min(coldeg) == max(coldeg) == 3

    # Orbit-signature certificate: each Paley difference class gets degree 3.
    signature_sum = Counter()
    for rep in REPS:
        orbit = [translate_tri(rep, s) for s in range(QMOD)]
        c = Counter()
        for tri in orbit:
            for u, v in tri_arcs(tri):
                c[(v - u) % QMOD] += 1
        for d in QR_ORDER:
            assert c[d] % QMOD == 0
            signature_sum[d] += c[d] // QMOD
    assert tuple(signature_sum[d] for d in QR_ORDER) == (3,) * 9

    # Linearity: two distinct rows share at most one column.
    supports = [{j for j, x in enumerate(row) if x} for row in A]
    assert max(len(supports[i] & supports[j])
               for i, j in combinations(range(n), 2)) <= 1

    # Levi connectivity.
    adj = [[] for _ in range(2 * n)]
    for i, s in enumerate(supports):
        for j in s:
            adj[i].append(n + j)
            adj[n + j].append(i)
    seen = {0}
    stack = [0]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    assert len(seen) == 2 * n

    # Oriented arc-vertex incidence G.
    G = [[0] * QMOD for _ in range(n)]
    for i, (u, v) in enumerate(arcs):
        G[i][u] = -1
        G[i][v] = +1

    AG = matmul_int(A, G)
    assert all(x == 0 for row in AG for x in row)
    assert rank_mod(G, PRIME) == 18

    # Exact rank sandwich for A.
    rank_A_mod = rank_mod(A, PRIME)
    assert rank_A_mod == 153
    # AG=0 and rank(G)=18 => rank_Q(A)<=153.
    # rank mod p=153 => rank_Q(A)>=153.
    rank_Q_A = 153
    nullity_Q_A = n - rank_Q_A
    assert nullity_Q_A == 18

    # RKPR clean: gauge-fix p_18=0 and use the 18-dimensional coordinate rows.
    gradient_rows = []
    for (u, v) in arcs:
        row = [0] * 18
        if u != 18:
            row[u] -= 1
        if v != 18:
            row[v] += 1
        gradient_rows.append(row)
    assert all(any(x for x in row) for row in gradient_rows)
    prop_pairs = []
    for i, j in combinations(range(n), 2):
        if proportional_int(gradient_rows[i], gradient_rows[j]):
            prop_pairs.append((i, j))
    assert prop_pairs == []

    # The UNSAT proof is symbolic once ker(A)=im(G): a SAT word would give
    # p_v-p_u in {-1,2} for every tournament arc, hence every unordered pair
    # of 19 potentials has distance in {1,2}. Such a real set has size <=3.
    assert QMOD > 3

    print("Paley(19) gradient-kernel post-RKPR control: PASS")
    print("n = 171")
    print("row_degree = column_degree = 3")
    print("linear = True")
    print("Levi_connected_vertices = 342/342")
    print(f"rank_F_{PRIME}(A) = {rank_A_mod}")
    print("rank_Q(A) = 153")
    print("nullity_Q(A) = 18")
    print("ker_Q(A) = im_Q(G)")
    print("RKPR proportional pairs = 0")
    print("Exact-One status = UNSAT (potential-distance certificate)")


if __name__ == "__main__":
    main()
