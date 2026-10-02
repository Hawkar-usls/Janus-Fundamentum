#!/usr/bin/env python3
"""Exact F3 controls for the projective blocking-set / line terminal.

Checks:
  * affine parameter hyperplanes <-> projective dual points;
  * a complete PG(1,3) line blocks every projective hyperplane;
  * a four-hyperplane nonparallel pencil covers F3^2;
  * frozen singular UNSAT contains a full projective line;
  * frozen PG15 SAT contains no full projective line.
"""

from itertools import combinations, product

P = 3

SAT_ROWS = [
    (1,2,3),(1,10,11),(1,12,13),(2,9,11),(2,12,14),(3,4,7),
    (3,5,6),(4,9,13),(4,10,14),(5,8,13),(5,10,15),(6,8,14),
    (6,9,15),(7,8,15),(7,11,12),
]
PERM_P = [5,7,9,10,3,1,14,2,4,6,12,13,8,0,11]
PERM_Q = [12,9,14,11,13,10,7,3,1,0,2,5,6,8,4]


def matrix_from_rows(rows, n):
    return [[int(j + 1 in row) for j in range(n)] for row in rows]


def singular_unsat_matrix():
    n = 15
    A = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in (i, PERM_P[i], PERM_Q[i]):
            A[i][j] = 1
    return A


def affine_parameterization(A, b):
    m, n = len(A), len(A[0])
    M = [[A[i][j] % P for j in range(n)] + [b[i] % P] for i in range(m)]
    pivots = []
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if M[i][c]), None)
        if pivot is None:
            continue
        M[r], M[pivot] = M[pivot], M[r]
        inv = pow(M[r][c], -1, P)
        M[r] = [(x * inv) % P for x in M[r]]
        for i in range(m):
            if i != r and M[i][c]:
                f = M[i][c]
                M[i] = [(M[i][j] - f * M[r][j]) % P for j in range(n + 1)]
        pivots.append(c)
        r += 1
    for i in range(r, m):
        assert not (all(M[i][j] == 0 for j in range(n)) and M[i][n])

    free = [j for j in range(n) if j not in pivots]
    x0 = [0] * n
    for i, c in enumerate(pivots):
        x0[c] = M[i][n]

    basis = []
    for f in free:
        v = [0] * n
        v[f] = 1
        for i, c in enumerate(pivots):
            v[c] = (-M[i][f]) % P
        basis.append(v)

    coordinate_rows = [tuple(v[i] for v in basis) for i in range(n)]
    return tuple(x0), coordinate_rows


def canon_projective(v):
    v = tuple(x % P for x in v)
    first = next((i for i, x in enumerate(v) if x), None)
    if first is None:
        return None
    inv = pow(v[first], -1, P)
    return tuple((inv * x) % P for x in v)


def projective_line(u, v):
    pts = set()
    for a, b in product(range(P), repeat=2):
        if a == 0 and b == 0:
            continue
        w = tuple((a * u[i] + b * v[i]) % P for i in range(len(u)))
        pts.add(canon_projective(w))
    assert None not in pts
    assert len(pts) == 4
    return frozenset(pts)


def homogeneous_points(A):
    r0, rows = affine_parameterization(A, [1] * len(A))
    d = len(rows[0]) if rows else 0
    points = set()
    forced_zero = False
    for i, b in enumerate(rows):
        if not any(b):
            if r0[i] == 0:
                forced_zero = True
            continue
        points.add(canon_projective(tuple(b) + (r0[i],)))
    pinf = tuple([0] * d + [1])
    points.add(pinf)
    return r0, rows, points, pinf, forced_zero


def full_lines(points):
    pts = list(points)
    lines = set()
    for u, v in combinations(pts, 2):
        L = projective_line(u, v)
        if L <= points:
            lines.add(tuple(sorted(L)))
    return lines


def dot(u, v):
    return sum(a * b for a, b in zip(u, v)) % P


def test_synthetic_pencil():
    # PG(2,3) dual line avoiding p_infty.  Its four points correspond to four
    # affine lines covering all of F3^2 without a complete parallel class.
    p = (1, 0, 0)
    q = (0, 1, 1)
    pinf = (0, 0, 1)
    L = projective_line(p, q)
    assert pinf not in L

    for alpha in product(range(P), repeat=2):
        X = alpha + (1,)
        assert any(dot(h, X) == 0 for h in L)

    # No projective direction [a:b] occurs with all three affine offsets.
    by_normal = {}
    for h in L:
        normal = canon_projective(h[:2])
        by_normal.setdefault(normal, set()).add(h[2])
    assert max(len(offsets) for offsets in by_normal.values()) == 1


def test_control(name, A, expect_line, expect_unique_points):
    r0, rows, points, pinf, forced_zero = homogeneous_points(A)
    assert not forced_zero
    lines = full_lines(points)
    assert bool(lines) == expect_line
    # points includes p_infty, so source-coordinate projective point count is -1.
    assert len(points) - 1 == expect_unique_points

    if expect_line:
        # Every affine parameter point must be hit by the source-coordinate
        # members of a full line. If the line contains p_infty, the other
        # three points already form a complete parallel class.
        L = frozenset(lines[0])
        source_line_points = [p for p in L if p != pinf]
        d = len(pinf) - 1
        for alpha in product(range(P), repeat=d):
            X = alpha + (1,)
            assert any(dot(h, X) == 0 for h in source_line_points)

    print({
        "control": name,
        "affine_dimension": len(pinf) - 1,
        "unique_source_projective_points": len(points) - 1,
        "full_projective_lines": len(lines),
        "p_infty_line": any(pinf in L for L in map(frozenset, lines)),
    })


def main():
    test_synthetic_pencil()

    A_sat = matrix_from_rows(SAT_ROWS, 15)
    A_unsat = singular_unsat_matrix()

    test_control("SINGULAR_UNSAT_RANK14", A_unsat, True, 3)
    test_control("PG15_SAT_R11", A_sat, False, 11)

    print("Affine F3 projective blocking-line terminal regression: PASS")
    print("E8_D1 = EMPTY")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
