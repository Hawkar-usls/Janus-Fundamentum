#!/usr/bin/env python3
"""Exact controls for the affine F3 nowhere-zero Exact-One normal form.

This checker uses only exact arithmetic over F3. It verifies:
  * Exact-One witness <-> nowhere-zero affine solution on frozen controls;
  * the augmented full-support-kernel count identity;
  * the missing-residue translation terminal;
  * PG15 SAT: 81 affine solutions, exactly 4 nowhere-zero;
  * frozen singular UNSAT: 3 affine solutions, none nowhere-zero.

Finite controls do not replace the symbolic theorem in the companion note.
"""

from itertools import product

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


def rref_aug(A, b, p=3):
    m, n = len(A), len(A[0])
    M = [[x % p for x in A[i]] + [b[i] % p] for i in range(m)]
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
    for i in range(r, m):
        if all(M[i][c] % p == 0 for c in range(n)) and M[i][n] % p:
            return None, None, None
    free = [c for c in range(n) if c not in pivots]
    x0 = [0] * n
    for i, c in enumerate(pivots):
        x0[c] = M[i][n] % p
    basis = []
    for f in free:
        v = [0] * n
        v[f] = 1
        for i, c in enumerate(pivots):
            v[c] = (-M[i][f]) % p
        basis.append(v)
    return x0, basis, pivots


def affine_solutions(A, b):
    x0, basis, _ = rref_aug(A, b, P)
    if x0 is None:
        return []
    out = []
    for coeff in product(range(P), repeat=len(basis)):
        x = x0[:]
        for a, v in zip(coeff, basis):
            for j in range(len(x)):
                x[j] = (x[j] + a * v[j]) % P
        out.append(x)
    return out


def matvec(A, x, p=None):
    y = [sum(a * b for a, b in zip(row, x)) for row in A]
    if p is not None:
        y = [v % p for v in y]
    return y


def exactone_witnesses(A):
    n = len(A[0])
    out = []
    for x in product((0, 1), repeat=n):
        if matvec(A, x) == [1] * len(A):
            out.append(x)
    return out


def nowhere_zero_affine(A):
    return [r for r in affine_solutions(A, [1] * len(A)) if all(v != 0 for v in r)]


def augmented_kernel_full_support(A):
    # [A | -1] c = 0 over F3.
    aug = [row + [2] for row in A]
    sols = affine_solutions(aug, [0] * len(A))
    return [c for c in sols if all(v != 0 for v in c)]


def check_mapping(A):
    exact = exactone_witnesses(A)
    nz = nowhere_zero_affine(A)

    exact_set = set(exact)
    decoded = set()
    for r in nz:
        assert matvec(A, r, 3) == [1] * len(A)
        x = tuple(int(v == 2) for v in r)
        assert x in exact_set
        decoded.add(x)

    for x in exact:
        r = tuple((1 + bit) % 3 for bit in x)
        assert all(v != 0 for v in r)
        assert matvec(A, r, 3) == [1] * len(A)
        assert r in set(map(tuple, nz))

    assert decoded == exact_set

    full = augmented_kernel_full_support(A)
    assert len(full) == 2 * len(exact)

    # Every full-support augmented word normalizes to (r,1).
    normalized = set()
    for c in full:
        t = c[-1]
        assert t in (1, 2)
        inv = pow(t, -1, 3)
        cn = tuple((inv * z) % 3 for z in c)
        assert cn[-1] == 1
        r = cn[:-1]
        assert all(v != 0 for v in r)
        assert matvec(A, r, 3) == [1] * len(A)
        normalized.add(r)
    assert len(normalized) == len(exact)


def check_missing_residue_terminal(A):
    for r in affine_solutions(A, [1] * len(A)):
        used = set(r)
        if len(used) <= 2:
            missing = next(a for a in range(3) if a not in used)
            # Add -missing globally so the omitted symbol becomes 0; because
            # A*1 = 0 mod 3, the affine equation is preserved.
            shift = (-missing) % 3
            rp = tuple((v + shift) % 3 for v in r)
            assert all(v != 0 for v in rp)
            assert matvec(A, rp, 3) == [1] * len(A)
            x = tuple(int(v == 2) for v in rp)
            assert matvec(A, x) == [1] * len(A)


def main():
    A_sat = matrix_from_rows(SAT_ROWS, 15)
    A_unsat = singular_unsat_matrix()

    assert all(sum(row) == 3 for row in A_sat)
    assert all(sum(row) == 3 for row in A_unsat)

    sat_aff = affine_solutions(A_sat, [1] * 15)
    unsat_aff = affine_solutions(A_unsat, [1] * 15)
    sat_nz = [r for r in sat_aff if all(v != 0 for v in r)]
    unsat_nz = [r for r in unsat_aff if all(v != 0 for v in r)]

    assert len(sat_aff) == 81
    assert len(sat_nz) == 4
    assert len(unsat_aff) == 3
    assert len(unsat_nz) == 0

    sat_exact = exactone_witnesses(A_sat)
    unsat_exact = exactone_witnesses(A_unsat)
    assert len(sat_exact) == 4
    assert len(unsat_exact) == 0

    check_mapping(A_sat)
    check_mapping(A_unsat)
    check_missing_residue_terminal(A_sat)
    check_missing_residue_terminal(A_unsat)

    sat_full = augmented_kernel_full_support(A_sat)
    unsat_full = augmented_kernel_full_support(A_unsat)
    assert len(sat_full) == 8
    assert len(unsat_full) == 0

    print("Affine F3 nowhere-zero Exact-One controls: PASS")
    print("PG15: affine=81, nowhere_zero=4, exact_one=4, augmented_full_support=8")
    print("singular UNSAT: affine=3, nowhere_zero=0, exact_one=0, augmented_full_support=0")
    print("E8_D1 = EMPTY")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
