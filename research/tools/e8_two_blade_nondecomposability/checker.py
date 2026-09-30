from itertools import combinations
from fractions import Fraction


def wedge_basis_with_form(j, form, n):
    out = {}
    for mask, coeff in form.items():
        if (mask >> j) & 1:
            continue
        lower = (mask & ((1 << j) - 1)).bit_count()
        sign = -1 if lower % 2 else 1
        nm = mask | (1 << j)
        out[nm] = out.get(nm, 0) + sign * coeff
    return {m: c for m, c in out.items() if c}


def map_matrix(d):
    n = 2 * d
    A = sum(1 << j for j in range(d))
    B = sum(1 << j for j in range(d, 2 * d))
    omega = {A: 1, B: 1}
    rows = [sum(1 << j for j in comb) for comb in combinations(range(n), d + 1)]
    ridx = {m: i for i, m in enumerate(rows)}
    M = [[0] * n for _ in rows]
    for j in range(n):
        col = wedge_basis_with_form(j, omega, n)
        for m, c in col.items():
            M[ridx[m]][j] = c
    return M


def rank_mod(M, p):
    A = [[x % p for x in row] for row in M]
    m = len(A); n = len(A[0]) if m else 0
    r = 0
    for c in range(n):
        q = next((i for i in range(r, m) if A[i][c] % p), None)
        if q is None:
            continue
        A[r], A[q] = A[q], A[r]
        inv = pow(A[r][c], -1, p)
        A[r] = [(x * inv) % p for x in A[r]]
        for i in range(m):
            if i != r and A[i][c] % p:
                f = A[i][c] % p
                A[i] = [(A[i][j] - f * A[r][j]) % p for j in range(n)]
        r += 1
    return r


def rank_q(M):
    A = [[Fraction(x) for x in row] for row in M]
    m = len(A); n = len(A[0]) if m else 0
    r = 0
    for c in range(n):
        q = next((i for i in range(r, m) if A[i][c]), None)
        if q is None:
            continue
        A[r], A[q] = A[q], A[r]
        piv = A[r][c]
        A[r] = [x / piv for x in A[r]]
        for i in range(m):
            if i != r and A[i][c]:
                f = A[i][c]
                A[i] = [A[i][j] - f * A[r][j] for j in range(n)]
        r += 1
    return r


def main():
    for d in range(2, 6):
        M = map_matrix(d)
        target = 2 * d
        rq = rank_q(M)
        r2 = rank_mod(M, 2)
        r3 = rank_mod(M, 3)
        assert rq == r2 == r3 == target, (d, rq, r2, r3)
        print(f'd={d} ambient={2*d} wedge_annihilator_dimension=0 ranks(Q,F2,F3)=({rq},{r2},{r3}) PASS')
    print('PASS_TWO_BLADE_NONDECOMPOSABILITY')
    print('INVERTIBLE_BASIS_CHANGE_CANNOT_CREATE_SINGLE_BLADE')
    print('AUXILIARY_NONLOCAL_CANCELLATION=OPEN')
    print('P_VS_NP=OPEN E8_D1=EMPTY')


if __name__ == '__main__':
    main()
