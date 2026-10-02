#!/usr/bin/env python3
"""Exact finite regression for AF3-1 / AF3-2.

The arbitrary-size equivalence is proved symbolically in the companion note.
This checker uses only exact arithmetic modulo 3 and exhaustive enumeration of
small affine/kernel spaces for the frozen n=15 controls.
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


def rref_mod(M, p=P):
    A = [[v % p for v in row] for row in M]
    m = len(A)
    n = len(A[0]) if m else 0
    pivots = []
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if A[i][c] % p), None)
        if pivot is None:
            continue
        A[r], A[pivot] = A[pivot], A[r]
        inv = pow(A[r][c], -1, p)
        A[r] = [(v * inv) % p for v in A[r]]
        for i in range(m):
            if i != r and A[i][c] % p:
                f = A[i][c] % p
                A[i] = [(A[i][j] - f * A[r][j]) % p for j in range(n)]
        pivots.append(c)
        r += 1
        if r == m:
            break
    return A, pivots


def rank_mod(M, p=P):
    return len(rref_mod(M, p)[1])


def kernel_basis_mod(M, p=P):
    R, pivots = rref_mod(M, p)
    n = len(M[0])
    free = [j for j in range(n) if j not in pivots]
    basis = []
    for f in free:
        x = [0] * n
        x[f] = 1
        for i, c in enumerate(pivots):
            x[c] = (-R[i][f]) % p
        basis.append(x)
    return basis


def affine_parameterization(A, b, p=P):
    m = len(A)
    n = len(A[0])
    M = [[A[i][j] % p for j in range(n)] + [b[i] % p]
         for i in range(m)]

    r = 0
    pivots = []
    for c in range(n):
        pivot = next((i for i in range(r, m) if M[i][c]), None)
        if pivot is None:
            continue
        M[r], M[pivot] = M[pivot], M[r]
        inv = pow(M[r][c], -1, p)
        M[r] = [(v * inv) % p for v in M[r]]
        for i in range(m):
            if i != r and M[i][c]:
                f = M[i][c]
                M[i] = [(M[i][j] - f * M[r][j]) % p
                        for j in range(n + 1)]
        pivots.append(c)
        r += 1

    if any(all(row[j] == 0 for j in range(n)) and row[n] != 0
           for row in M):
        return None, []

    x0 = [0] * n
    for i, c in enumerate(pivots):
        x0[c] = M[i][n]
    return x0, kernel_basis_mod(A, p)


def enumerate_affine(A, b, p=P):
    x0, basis = affine_parameterization(A, b, p)
    if x0 is None:
        return []
    out = []
    for coeff in product(range(p), repeat=len(basis)):
        x = x0[:]
        for t, a in enumerate(coeff):
            if not a:
                continue
            for j in range(len(x)):
                x[j] = (x[j] + a * basis[t][j]) % p
        out.append(x)
    return out


def enumerate_linear_code(M, p=P):
    basis = kernel_basis_mod(M, p)
    n = len(M[0])
    out = []
    for coeff in product(range(p), repeat=len(basis)):
        x = [0] * n
        for t, a in enumerate(coeff):
            if not a:
                continue
            for j in range(n):
                x[j] = (x[j] + a * basis[t][j]) % p
        out.append(x)
    return out


def matvec_mod(A, x, p=P):
    return [sum(a * b for a, b in zip(row, x)) % p for row in A]


def witness_sets(A):
    n = len(A)
    if n % 3:
        return []
    out = []
    for C in combinations(range(n), n // 3):
        S = set(C)
        if all(sum(row[j] for j in S) == 1 for row in A):
            out.append(S)
    return out


def decode_nowhere_zero(r):
    assert all(v in (1, 2) for v in r)
    return [1 if v == 2 else 0 for v in r]


def check_control(name, A, expected_witnesses, expected_rank):
    n = len(A)
    assert all(sum(row) == 3 for row in A)
    assert all(sum(A[i][j] for i in range(n)) == 3 for j in range(n))

    witnesses = witness_sets(A)
    assert len(witnesses) == expected_witnesses
    assert rank_mod(A) == expected_rank

    affine = enumerate_affine(A, [1] * n)
    assert len(affine) == 3 ** (n - expected_rank)
    full = [r for r in affine if all(v != 0 for v in r)]
    assert len(full) == expected_witnesses

    decoded = set()
    for r in full:
        assert matvec_mod(A, r) == [1] * n
        x = decode_nowhere_zero(r)
        assert all(sum(row[j] * x[j] for j in range(n)) == 1 for row in A)
        decoded.add(tuple(i for i, v in enumerate(x) if v))
    assert len(decoded) == expected_witnesses

    # Exact forward map x -> r=1+x mod 3.
    for S in witnesses:
        x = [1 if i in S else 0 for i in range(n)]
        r = [(1 + v) % 3 for v in x]
        assert all(v != 0 for v in r)
        assert matvec_mod(A, r) == [1] * n

    # Augmented code C_A = ker_F3([A|-1]).
    Atilde = [row + [-1] for row in A]
    code = enumerate_linear_code(Atilde)
    full_code = [c for c in code if all(v != 0 for v in c)]
    assert len(full_code) == 2 * expected_witnesses

    normalized = []
    for c in full_code:
        t = c[-1]
        assert t in (1, 2)
        inv = pow(t, -1, 3)
        w = [(inv * v) % 3 for v in c]
        assert w[-1] == 1
        assert matvec_mod(A, w[:-1]) == [1] * n
        normalized.append(tuple(w))
    assert len(set(normalized)) == expected_witnesses

    print({
        'control': name,
        'rank_F3': expected_rank,
        'affine_solution_count': len(affine),
        'nowhere_zero_affine_count': len(full),
        'exactone_witness_count': len(witnesses),
        'augmented_full_support_codewords': len(full_code),
    })


def main():
    A_sat = matrix_from_rows(SAT_ROWS, 15)
    A_unsat = singular_unsat_matrix()

    check_control('PG15_SAT_R11', A_sat, expected_witnesses=4, expected_rank=11)
    check_control('SINGULAR_UNSAT_RANK14', A_unsat, expected_witnesses=0, expected_rank=14)

    # Direct missing-residue sanity on each SAT witness orbit.
    for S in witness_sets(A_sat):
        x = [1 if i in S else 0 for i in range(15)]
        r = [(1 + v) % 3 for v in x]  # omits residue 0
        for shift in range(3):
            q = [(v + shift) % 3 for v in r]
            assert matvec_mod(A_sat, q) == [1] * 15
            assert len(set(q)) == 2

    print('AF3 nowhere-zero Exact-One regression: PASS')
    print('P_VS_NP = OPEN')
    print('E8_D1 = EMPTY')


if __name__ == '__main__':
    main()
