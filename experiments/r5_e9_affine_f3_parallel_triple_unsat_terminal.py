#!/usr/bin/env python3
"""Exact F3 regression for the affine parallel-triple UNSAT terminal.

Finite controls only; the arbitrary-size terminal is proved symbolically in the
companion research note. All arithmetic is exact modulo 3.
"""

SAT15_ROWS = [
    (1,2,3),(1,10,11),(1,12,13),(2,9,11),(2,12,14),(3,4,7),
    (3,5,6),(4,9,13),(4,10,14),(5,8,13),(5,10,15),(6,8,14),
    (6,9,15),(7,8,15),(7,11,12),
]

UNSAT15_ROWS = [
    (0,5,12),(1,7,9),(2,9,14),(3,10,11),(3,4,13),
    (1,5,10),(6,7,14),(2,3,7),(1,4,8),(0,6,9),
    (2,10,12),(5,11,13),(6,8,12),(0,8,13),(4,11,14),
]

SAT18_ROWS = [
    (0,15,17),(1,4,12),(2,10,14),(3,4,11),(4,8,9),(3,5,13),
    (1,6,10),(2,7,15),(1,8,14),(3,7,9),(9,10,16),(7,11,13),
    (5,12,17),(0,13,16),(0,12,14),(5,8,15),(2,6,16),(6,11,17),
]


def matrix_from_rows(rows, n, one_based=False):
    A = [[0] * n for _ in range(len(rows))]
    for i, row in enumerate(rows):
        for j in row:
            A[i][j - 1 if one_based else j] = 1
    return A


def lift(A, pair):
    n = len(A)
    E = [[0] * n for _ in range(n)]
    for i, j in pair:
        assert A[i][j] == 1
        E[i][j] = 1
    P = [[A[i][j] - E[i][j] for j in range(n)] for i in range(n)]
    H = [[0] * (2 * n) for _ in range(2 * n)]
    for i in range(n):
        for j in range(n):
            H[i][j] = P[i][j]
            H[i][j + n] = E[i][j]
            H[i + n][j] = E[i][j]
            H[i + n][j + n] = P[i][j]
    return H


def affine_parameterization(A, p=3):
    m, n = len(A), len(A[0])
    M = [[A[i][j] % p for j in range(n)] + [1] for i in range(m)]
    pivots = []
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if M[i][c] % p), None)
        if pivot is None:
            continue
        M[r], M[pivot] = M[pivot], M[r]
        inv = pow(M[r][c] % p, -1, p)
        M[r] = [(x * inv) % p for x in M[r]]
        for i in range(m):
            if i != r and M[i][c] % p:
                f = M[i][c] % p
                M[i] = [(M[i][j] - f * M[r][j]) % p for j in range(n + 1)]
        pivots.append(c)
        r += 1
        if r == m:
            break

    if any(all(M[i][c] == 0 for c in range(n)) and M[i][n] != 0
           for i in range(m)):
        return None, None

    free = [j for j in range(n) if j not in pivots]
    r0 = [0] * n
    for i, c in enumerate(pivots):
        r0[c] = M[i][n]

    basis = []
    for f in free:
        v = [0] * n
        v[f] = 1
        for i, c in enumerate(pivots):
            v[c] = (-M[i][f]) % p
        basis.append(v)

    B = [[basis[t][i] for t in range(len(basis))] for i in range(n)]
    return r0, B


def normalize_hyperplane(row, r0i):
    first = next((x % 3 for x in row if x % 3), None)
    if first is None:
        return None
    inv = pow(first, -1, 3)
    normal = tuple((inv * x) % 3 for x in row)
    offset = (-inv * r0i) % 3
    return normal, offset


def terminal_summary(A):
    r0, B = affine_parameterization(A)
    if r0 is None:
        return {
            'inconsistent': True,
            'd': None,
            'projective_classes': 0,
            'full_classes': 0,
            'max_offsets': 0,
            'zero_normal_zero_offset': True,
        }

    d = len(B[0]) if B and B[0] else 0
    classes = {}
    zero_normal_zero_offset = False
    for i, row in enumerate(B):
        normalized = normalize_hyperplane(row, r0[i])
        if normalized is None:
            if r0[i] == 0:
                zero_normal_zero_offset = True
            continue
        normal, offset = normalized
        classes.setdefault(normal, {}).setdefault(offset, []).append(i)

    full = [entry for entry in classes.items() if set(entry[1]) == {0, 1, 2}]
    return {
        'inconsistent': False,
        'd': d,
        'projective_classes': len(classes),
        'full_classes': len(full),
        'max_offsets': max((len(v) for v in classes.values()), default=0),
        'zero_normal_zero_offset': zero_normal_zero_offset,
        'classes': classes,
        'r0': r0,
        'B': B,
    }


def assert_cubic(A):
    n = len(A)
    assert all(len(row) == n for row in A)
    assert all(sum(row) == 3 for row in A)
    assert all(sum(A[i][j] for i in range(n)) == 3 for j in range(n))


def assert_no_single_source_row_full_parallel(A, info):
    if info['inconsistent']:
        return
    r0, B = info['r0'], info['B']
    for row in A:
        ids = [j for j, a in enumerate(row) if a]
        assert len(ids) == 3
        normalized = [normalize_hyperplane(B[j], r0[j]) for j in ids]
        if any(x is None for x in normalized):
            continue
        normals = [x[0] for x in normalized]
        offsets = [x[1] for x in normalized]
        assert not (normals[0] == normals[1] == normals[2] and set(offsets) == {0, 1, 2})


def main():
    # SAT controls.
    pg15 = matrix_from_rows(SAT15_ROWS, 15, one_based=True)
    sat18 = matrix_from_rows(SAT18_ROWS, 18)
    sat36 = lift(sat18, ((0, 15), (1, 1)))

    for A in (pg15, sat18, sat36):
        assert_cubic(A)
        info = terminal_summary(A)
        assert not info['inconsistent']
        assert not info['zero_normal_zero_offset']
        assert info['full_classes'] == 0
        assert_no_single_source_row_full_parallel(A, info)

    pg = terminal_summary(pg15)
    s18 = terminal_summary(sat18)
    s36 = terminal_summary(sat36)
    assert (pg['d'], pg['projective_classes'], pg['max_offsets']) == (4, 11, 1)
    assert (s18['d'], s18['projective_classes'], s18['max_offsets']) == (2, 3, 2)
    assert (s36['d'], s36['projective_classes'], s36['max_offsets']) == (3, 5, 2)

    # UNSAT seed and recursive two-edge tower controls.
    A0 = matrix_from_rows(UNSAT15_ROWS, 15)
    assert_cubic(A0)
    u0 = terminal_summary(A0)
    assert (u0['d'], u0['full_classes']) == (1, 1)
    assert_no_single_source_row_full_parallel(A0, u0)

    # First lift uses the frozen seed pair; recursive levels use the frozen pair
    # from the prime-tower checker and its upper-right lifted copies.
    A = lift(A0, ((0, 12), (2, 9)))
    F = ((0, 5), (1, 1))
    expected = [(30, 2, 2), (60, 3, 3), (120, 5, 5), (240, 9, 9)]
    got = []
    for n_expected, d_expected, full_expected in expected:
        assert len(A) == n_expected
        assert_cubic(A)
        info = terminal_summary(A)
        got.append((len(A), info['d'], info['full_classes']))
        assert info['d'] == d_expected
        assert info['full_classes'] == full_expected
        assert info['max_offsets'] == 3
        assert_no_single_source_row_full_parallel(A, info)

        n = len(A)
        Anew = lift(A, F)
        F = ((F[0][0], F[0][1] + n), (F[1][0], F[1][1] + n))
        A = Anew

    assert got == expected

    print('PASS_AFFINE_F3_PARALLEL_TRIPLE_UNSAT_TERMINAL')
    print('SAT controls: PG15=(d=4,classes=11,full=0), unique18=(2,3,0), lift36=(3,5,0)')
    print('UNSAT seed: (n=15,d=1,full=1)')
    print('UNSAT tower:', got)
    print('single-source-row full parallel triple: IMPOSSIBLE on all controls and proved symbolically')
    print('E8_D1=EMPTY; P_VS_NP=OPEN')


if __name__ == '__main__':
    main()
