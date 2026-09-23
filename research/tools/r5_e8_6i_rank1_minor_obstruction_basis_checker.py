#!/usr/bin/env python3
from __future__ import annotations

from itertools import product


def gf2_rank(rows):
    rows = [list(map(int, row)) for row in rows]
    if not rows:
        return 0
    m = len(rows)
    n = len(rows[0])
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if rows[i][c]), None)
        if pivot is None:
            continue
        rows[r], rows[pivot] = rows[pivot], rows[r]
        for i in range(m):
            if i != r and rows[i][c]:
                rows[i] = [a ^ b for a, b in zip(rows[i], rows[r])]
        r += 1
    return r


def matrix_rank_f2(z):
    return gf2_rank(z)


def symmetric_anchored_matrix(n, bits):
    size = n + 1
    z = [[0] * size for _ in range(size)]
    z[0][0] = 1
    k = 0

    for i in range(1, size):
        z[0][i] = z[i][0] = bits[k]
        k += 1

    for i in range(1, size):
        for j in range(i, size):
            z[i][j] = z[j][i] = bits[k]
            k += 1

    assert k == len(bits)
    return z


def anchored_rank1_identities_hold(z):
    size = len(z)
    return all(
        z[i][j] == (z[0][i] & z[0][j])
        for i in range(1, size)
        for j in range(i, size)
    )


def first_violated_cut(z):
    size = len(z)
    for i in range(1, size):
        for j in range(i, size):
            if z[i][j] != (z[0][i] & z[0][j]):
                return (i, j)
    return None


def phi_degree2(x):
    n = len(x)
    out = list(x)
    for i in range(n):
        for j in range(i + 1, n):
            out.append(x[i] & x[j])
    return out


def verify(max_matrix_n=4, max_hull_n=7):
    matrix_cases = 0
    per_n = []

    for n in range(1, max_matrix_n + 1):
        free = n + n * (n + 1) // 2
        rank1_count = 0
        basis_accept_count = 0

        for bits in product((0, 1), repeat=free):
            z = symmetric_anchored_matrix(n, bits)
            matrix_cases += 1

            rank1 = matrix_rank_f2(z) == 1
            basis_accept = anchored_rank1_identities_hold(z)

            assert rank1 == basis_accept

            if rank1:
                rank1_count += 1
                assert first_violated_cut(z) is None
            else:
                assert first_violated_cut(z) is not None

            if basis_accept:
                basis_accept_count += 1

        assert rank1_count == 2 ** n
        assert basis_accept_count == 2 ** n
        per_n.append(
            {
                "n": n,
                "free_symmetric_anchored_entries": free,
                "rank1_matrices": rank1_count,
                "basis_accept_matrices": basis_accept_count,
            }
        )

    hull = []
    for n in range(1, max_hull_n + 1):
        points = [phi_degree2(x) for x in product((0, 1), repeat=n)]
        expected = n + n * (n - 1) // 2
        observed = gf2_rank(points)
        assert observed == expected
        hull.append(
            {
                "n": n,
                "reduced_moment_dimension": expected,
                "affine_hull_dimension": observed,
            }
        )

    spurious = [0, 0, 1]
    assert spurious not in [
        phi_degree2(x) for x in product((0, 1), repeat=2)
    ]

    return {
        "status": "PASS",
        "matrix_cases": matrix_cases,
        "max_matrix_n": max_matrix_n,
        "per_n": per_n,
        "affine_hull_checks": hull,
        "negative_control": "PASS_SPURIOUS_POINT_IN_FULL_AFFINE_HULL_AMBIENT",
        "scientific_ceiling": "R5_OBSTRUCTION_BASIS_ONLY__MINOR_ABSORPTION_OPEN",
    }


if __name__ == "__main__":
    import json

    print(json.dumps(verify(), indent=2, sort_keys=True))
