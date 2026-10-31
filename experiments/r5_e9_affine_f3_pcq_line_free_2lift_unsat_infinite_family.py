#!/usr/bin/env python3
"""Exact finite regression for the AF3 PCQ-fixed line-free 2-lift theorem.

The arbitrary-size statements are proved in the companion research note.  This
checker uses exact integer/F3 arithmetic and replays levels t=0..4.
"""

from itertools import combinations

P = 3
ROWS = [
    (0,1,2),(0,9,10),(0,11,12),(1,8,10),(1,11,13),
    (2,3,6),(2,4,5),(3,8,12),(3,9,13),(4,7,8),
    (4,9,14),(5,7,13),(5,12,14),(6,7,14),(6,10,11),
]
Y0 = [0,-1,1,1,-1,0,0,-1,1,0,0,0,0,0,0]


def matrix_from_rows(rows, n):
    A = [[0] * n for _ in range(n)]
    for i, row in enumerate(rows):
        for j in row:
            A[i][j] = 1
    return A


def rowsets(A):
    return [tuple(j for j, x in enumerate(row) if x) for row in A]


def assert_cubic_linear(A):
    n = len(A)
    assert all(sum(row) == 3 for row in A)
    assert all(sum(A[i][j] for i in range(n)) == 3 for j in range(n))
    rows = [set(r) for r in rowsets(A)]
    assert all(len(rows[i] & rows[j]) <= 1 for i in range(n) for j in range(i))


def graph_connected(A, removed=()):
    n = len(A)
    removed = set(removed)
    adj = [[] for _ in range(2 * n)]
    for i, row in enumerate(A):
        for j, x in enumerate(row):
            if x and (i, j) not in removed:
                adj[n + i].append(j)
                adj[j].append(n + i)
    start = next((u for u, nbr in enumerate(adj) if nbr), None)
    if start is None:
        return False
    stack = [start]
    seen = {start}
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return len(seen) == 2 * n


def left_kernel_check(A, y):
    n = len(A)
    assert len(y) == n
    return all(sum(A[i][j] * y[i] for i in range(n)) == 0 for j in range(n))


def exactone_count_weight_n_over_3(A):
    n = len(A)
    assert n % 3 == 0
    count = 0
    for C in combinations(range(n), n // 3):
        S = set(C)
        if all(sum(row[j] for j in S) == 1 for row in A):
            count += 1
    return count


def lift(A, pair):
    n = len(A)
    (i1, j1), (i2, j2) = pair
    assert i1 != i2 and j1 != j2
    assert A[i1][j1] == 1 and A[i2][j2] == 1

    E = [[0] * n for _ in range(n)]
    E[i1][j1] = 1
    E[i2][j2] = 1
    base = [[A[i][j] - E[i][j] for j in range(n)] for i in range(n)]

    H = [[0] * (2 * n) for _ in range(2 * n)]
    for i in range(n):
        for j in range(n):
            H[i][j] = base[i][j]
            H[i][j + n] = E[i][j]
            H[i + n][j] = E[i][j]
            H[i + n][j + n] = base[i][j]

    next_pair = ((i1, j1 + n), (i2, j2 + n))
    return H, next_pair


def affine_parameterization(A):
    n = len(A)
    M = [[x % P for x in A[i]] + [1] for i in range(n)]
    r = 0
    pivots = []
    for c in range(n):
        pivot = next((i for i in range(r, n) if M[i][c]), None)
        if pivot is None:
            continue
        M[r], M[pivot] = M[pivot], M[r]
        inv = pow(M[r][c], -1, P)
        M[r] = [(x * inv) % P for x in M[r]]
        for i in range(n):
            if i != r and M[i][c]:
                f = M[i][c]
                M[i] = [(M[i][j] - f * M[r][j]) % P for j in range(n + 1)]
        pivots.append(c)
        r += 1
        if r == n:
            break

    assert not any(
        all(M[i][j] == 0 for j in range(n)) and M[i][n]
        for i in range(r, n)
    ), "Ar=1 unexpectedly inconsistent over F3"

    free = [j for j in range(n) if j not in pivots]
    r0 = [0] * n
    for i, c in enumerate(pivots):
        r0[c] = M[i][n]

    basis = []
    for f in free:
        v = [0] * n
        v[f] = 1
        for i, c in enumerate(pivots):
            v[c] = (-M[i][f]) % P
        basis.append(v)

    brows = [[basis[k][i] for k in range(len(basis))] for i in range(n)]
    return r0, brows, len(pivots)


def canon(v):
    v = tuple(x % P for x in v)
    first = next((x for x in v if x), None)
    if first is None:
        return None
    inv = pow(first, -1, P)
    return tuple((inv * x) % P for x in v)


def pcq_groups(r0, brows):
    groups = {}
    for a, b in zip(r0, brows):
        assert any(b), "zero affine normal violates the claimed residual invariant"
        first = next(x for x in b if x)
        inv = pow(first, -1, P)
        normal = tuple((inv * x) % P for x in b)
        offset = (-a * inv) % P
        groups.setdefault(normal, set()).add(offset)
    return groups


def projective_line(u, v):
    d = len(u)
    out = set()
    for a in range(P):
        for b in range(P):
            if a == 0 and b == 0:
                continue
            w = tuple((a * u[k] + b * v[k]) % P for k in range(d))
            out.add(canon(w))
    assert None not in out and len(out) == 4
    return frozenset(out)


def blocking_points_and_line_test(r0, brows):
    d = len(brows[0])
    points = {canon(tuple(brows[i]) + (r0[i],)) for i in range(len(r0))}
    assert None not in points
    p_inf = (0,) * d + (1,)
    points.add(p_inf)
    pts = list(points)
    for u, v in combinations(pts, 2):
        if projective_line(u, v) <= points:
            return points, True
    return points, False


def main():
    A = matrix_from_rows(ROWS, 15)
    pair = ((0, 0), (1, 9))
    y = Y0[:]

    # The base UNSAT claim is independently replayed without a SAT oracle.
    assert exactone_count_weight_n_over_3(A) == 0

    expected_dims = [4, 6, 10, 18, 34]
    expected_dirs = [15, 27, 51, 99, 195]
    expected_points = [16, 28, 52, 100, 196]
    report = []

    for t in range(5):
        n = len(A)
        assert n == 15 * (2 ** t)
        assert_cubic_linear(A)
        assert graph_connected(A)
        assert graph_connected(A, pair), "G_t-F_t must remain connected"

        (i1, j1), (i2, j2) = pair
        assert i1 != i2 and j1 != j2
        assert A[i1][j1] == 1 and A[i2][j2] == 1
        assert left_kernel_check(A, y)
        assert y[i1] != y[i2]

        r0, brows, rank = affine_parameterization(A)
        d = n - rank
        assert d == expected_dims[t]
        assert d >= 2 + 2 ** (t + 1)

        groups = pcq_groups(r0, brows)
        assert len(groups) == expected_dirs[t]
        assert all(len(offsets) == 1 for offsets in groups.values())

        points, has_line = blocking_points_and_line_test(r0, brows)
        assert not has_line
        assert len(points) == expected_points[t]

        report.append({
            "t": t,
            "n": n,
            "rank_F3": rank,
            "affine_dimension": d,
            "pcq_projective_directions": len(groups),
            "pcq_pin_classes": 0,
            "pcq_three_offset_classes": 0,
            "blocking_points_with_pinf": len(points),
            "projective_line": False,
            "G_minus_F_connected": True,
            "left_separator": [y[i1], y[i2]],
        })

        if t < 4:
            A, pair = lift(A, pair)
            y = y + y

    for item in report:
        print(item)
    print("PASS_AFFINE_F3_PCQ_LINE_FREE_2LIFT_UNSAT_INFINITE_FAMILY_REGRESSION")
    print("Arbitrary-size statements are theorem-level; finite replay t=0..4 only.")
    print("E8_D1 = EMPTY")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
