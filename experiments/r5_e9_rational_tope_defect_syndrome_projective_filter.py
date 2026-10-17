#!/usr/bin/env python3
"""Exact finite regression for the rational-tope defect-syndrome projective filter.

No floating-point LP is used.  The PG15 positive control is certified entirely
with integer / GF(2) arithmetic:

* defect syndrome d = 1 + A x is checked row-by-row;
* G=A R has rank 7 and affine nullity 4;
* all 16 parity-compatible projective toggles are enumerated;
* four are realized by exact integer alpha witnesses;
* the other twelve have exact Gordan-style infeasibility certificates: three
  desired signed projective normals sum to zero.
"""

from itertools import product


ROWS = [
    (1, 2, 3),
    (1, 10, 11),
    (1, 12, 13),
    (2, 9, 11),
    (2, 12, 14),
    (3, 4, 7),
    (3, 5, 6),
    (4, 9, 13),
    (4, 10, 14),
    (5, 8, 13),
    (5, 10, 15),
    (6, 8, 14),
    (6, 9, 15),
    (7, 8, 15),
    (7, 11, 12),
]

B = [
    (-1, -1, 0, 0),
    (-1, 0, -1, 0),
    (2, 1, 1, 0),
    (-1, -1, -1, 1),
    (-1, -1, 0, 0),
    (-1, 0, -1, 0),
    (-1, 0, 0, -1),
    (1, 0, 0, 0),
    (1, 0, 1, -1),
    (1, 1, 0, -1),
    (0, 0, 0, 1),
    (1, 0, 0, 0),
    (0, 1, 0, 0),
    (0, 0, 1, 0),
    (0, 0, 0, 1),
]

# 0-based coordinate classes; every pair here consists of exactly equal rows.
CLASSES = [
    (0, 4),
    (1, 5),
    (2,),
    (3,),
    (6,),
    (7, 11),
    (8,),
    (9,),
    (10, 14),
    (12,),
    (13,),
]

ALPHA0 = (-1, 2, 2, -2)

# flip-set (1-based class labels) -> exact alpha realizing that projective sign
# pattern.  These are the four known PG15 Exact-One boundary topes.
REALIZABLE = {
    (5, 7, 8, 9): (-1, 2, 2, 2),
    (5, 6, 10, 11): (2, -1, -1, -1),
    (2, 3, 7, 11): (-1, 2, -1, -1),
    (1, 3, 8, 10): (-1, -1, 2, -1),
}

# flip-set -> three 1-based projective-class normals whose desired signed
# versions sum exactly to zero.  If all desired strict inequalities were
# positive at one alpha, their sum could not have dot product zero.
INFEASIBLE_CERTS = {
    (4,): (3, 4, 5),
    (4, 6, 7, 8, 9, 10, 11): (3, 4, 5),
    (2, 3, 6, 8, 9, 10): (2, 6, 11),
    (2, 3, 4, 5, 8, 9, 11): (2, 7, 9),
    (2, 3, 4, 5, 6, 7, 10): (2, 6, 11),
    (1, 3, 6, 7, 9, 11): (1, 6, 10),
    (1, 3, 4, 5, 7, 9, 10): (1, 8, 9),
    (1, 3, 4, 5, 6, 8, 11): (1, 6, 10),
    (1, 2, 5, 9, 10, 11): (1, 2, 3),
    (1, 2, 5, 6, 7, 8): (1, 2, 3),
    (1, 2, 4, 7, 8, 10, 11): (1, 2, 3),
    (1, 2, 4, 6, 9): (1, 2, 3),
}


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def matvec(M, v):
    return [dot(row, v) for row in M]


def xor_matvec(M, v):
    return [sum(a * b for a, b in zip(row, v)) & 1 for row in M]


def gf2_rank(M):
    a = [list(map(lambda x: x & 1, row)) for row in M]
    if not a:
        return 0
    m, n = len(a), len(a[0])
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if a[i][c]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        for i in range(m):
            if i != r and a[i][c]:
                a[i] = [x ^ y for x, y in zip(a[i], a[r])]
        r += 1
        if r == m:
            break
    return r


def build_A():
    A = [[0] * 15 for _ in range(15)]
    for r, triple in enumerate(ROWS):
        for j in triple:
            A[r][j - 1] = 1
    return A


def build_R():
    R = [[0] * len(CLASSES) for _ in range(15)]
    for j, cls in enumerate(CLASSES):
        for i in cls:
            R[i][j] = 1
    return R


def gf2_matmul(A, R):
    out = [[0] * len(R[0]) for _ in range(len(A))]
    for i in range(len(A)):
        for j in range(len(R[0])):
            out[i][j] = sum(A[i][k] * R[k][j] for k in range(len(R))) & 1
    return out


def raw_sign_bits(alpha):
    y = matvec(B, alpha)
    assert all(v != 0 for v in y)
    return y, [1 if v > 0 else 0 for v in y]


def projective_base_signs(alpha):
    reps = [B[cls[0]] for cls in CLASSES]
    vals = [dot(h, alpha) for h in reps]
    assert all(v != 0 for v in vals)
    return reps, [1 if v > 0 else -1 for v in vals]


def desired_signed_normal(reps, base_signs, flips, j):
    # j is 0-based class index.
    s = base_signs[j] * (-1 if (j + 1) in flips else 1)
    return tuple(s * x for x in reps[j])


def main():
    A = build_A()
    R = build_R()

    # Cubic square source and exact rational-kernel basis checks.
    assert all(sum(row) == 3 for row in A)
    assert all(sum(A[i][j] for i in range(15)) == 3 for j in range(15))
    for col in range(4):
        assert all(v == 0 for v in matvec(A, [B[i][col] for i in range(15)]))

    # Projective classes are exact equal-row classes on this positive control.
    covered = sorted(i for cls in CLASSES for i in cls)
    assert covered == list(range(15))
    for cls in CLASSES:
        rep = B[cls[0]]
        for i in cls:
            assert B[i] == rep

    y0, x0 = raw_sign_bits(ALPHA0)
    p0 = sum(x0)
    assert p0 == 6

    # d0 = 1 + A x0; it must exactly identify the ++- rows.
    Ax0_mod2 = xor_matvec(A, x0)
    d0 = [1 ^ bit for bit in Ax0_mod2]
    defect_rows = []
    for r, triple in enumerate(ROWS):
        count = sum(x0[j - 1] for j in triple)
        assert count in (1, 2)
        assert d0[r] == (1 if count == 2 else 0)
        if count == 2:
            defect_rows.append(r)
    assert len(defect_rows) == 3 * p0 - 15 == 3

    G = gf2_matmul(A, R)
    rank_G = gf2_rank(G)
    q = len(CLASSES)
    kappa = q - rank_G
    assert q == 11
    assert rank_G == 7
    assert kappa == 4

    reps, base_signs = projective_base_signs(ALPHA0)

    candidates = []
    for bits in product((0, 1), repeat=q):
        if xor_matvec(G, bits) == d0:
            flips = tuple(i + 1 for i, bit in enumerate(bits) if bit)
            candidates.append(flips)
    assert len(candidates) == 2 ** kappa == 16

    assert set(candidates) == set(REALIZABLE) | set(INFEASIBLE_CERTS)
    assert set(REALIZABLE).isdisjoint(INFEASIBLE_CERTS)

    # Four exact feasible boundary candidates.
    recovered_supports = set()
    for flips, alpha in REALIZABLE.items():
        y, x = raw_sign_bits(alpha)
        for j in range(q):
            desired = base_signs[j] * (-1 if (j + 1) in flips else 1)
            assert (1 if dot(reps[j], alpha) > 0 else -1) == desired
        assert xor_matvec(A, x) == [1] * 15
        # Since y is in ker_Q(A), odd parity forces exactly one positive per row.
        for triple in ROWS:
            assert sum(x[j - 1] for j in triple) == 1
        assert sum(x) == 5
        recovered_supports.add(tuple(i + 1 for i, bit in enumerate(x) if bit))

    expected_supports = {
        (1, 5, 7, 9, 14),
        (2, 6, 7, 10, 13),
        (3, 8, 9, 10, 12),
        (3, 11, 13, 14, 15),
    }
    assert recovered_supports == expected_supports

    # Twelve exact infeasibility certificates.  Each certificate is a positive
    # dependence of desired signed normals with coefficients (1,1,1).
    for flips, triple in INFEASIBLE_CERTS.items():
        normals = [
            desired_signed_normal(reps, base_signs, flips, j - 1)
            for j in triple
        ]
        total = tuple(sum(v[c] for v in normals) for c in range(4))
        assert total == (0, 0, 0, 0), (flips, triple, normals, total)

    print("PASS: rational-tope defect syndrome projective filter")
    print(f"q={q} rank_F2(G)={rank_G} kappa={kappa}")
    print(f"parity_candidates={len(candidates)}")
    print(f"exact_realizable_boundary_topes={len(REALIZABLE)}")
    print(f"exact_infeasible_sign_certificates={len(INFEASIBLE_CERTS)}")
    print("E8_D1=EMPTY")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    main()
