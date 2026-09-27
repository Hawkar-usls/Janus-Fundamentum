#!/usr/bin/env python3
"""Controls for the R5 E9 A-irreducible bounded-width terminal.

Executable scope:
- exact rational full-rank check for cyclic D(n): A=I+S+S^3, n=7..36;
- brute-force UNSAT confirmation for small D(n), n=7..15;
- exact 3-bit interface transfer-DP sanity check for cyclic module chains.

The Boben A-irreducible classification itself is source-bound mathematics and is
not reproved by this finite regression.
"""

from fractions import Fraction
from itertools import product


def rank_q(M):
    a = [[Fraction(v) for v in row] for row in M]
    m = len(a)
    n = len(a[0]) if m else 0
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if a[i][c]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        pv = a[r][c]
        a[r] = [v / pv for v in a[r]]
        for i in range(m):
            if i != r and a[i][c]:
                f = a[i][c]
                a[i] = [a[i][j] - f * a[r][j] for j in range(n)]
        r += 1
        if r == m:
            break
    return r


def d_matrix(n):
    A = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in (i, (i + 1) % n, (i + 3) % n):
            A[i][j] = 1
    return A


def exact_one(A, x):
    return all(sum(A[i][j] * x[j] for j in range(len(x))) == 1 for i in range(len(A)))


def check_d_family():
    for n in range(7, 37):
        A = d_matrix(n)
        assert rank_q(A) == n, n
    for n in range(7, 16):
        A = d_matrix(n)
        count = sum(1 for x in product((0, 1), repeat=n) if exact_one(A, x))
        assert count == 0, (n, count)


def compose_relation(R, S):
    # Boolean composition of relations on the fixed 8-state 3-bit interface.
    out = [[False] * 8 for _ in range(8)]
    for i in range(8):
        for k in range(8):
            out[i][k] = any(R[i][j] and S[j][k] for j in range(8))
    return out


def power_relation(R, n):
    I = [[i == j for j in range(8)] for i in range(8)]
    B = [row[:] for row in R]
    while n:
        if n & 1:
            I = compose_relation(I, B)
        B = compose_relation(B, B)
        n //= 2
    return I


def check_three_bit_transfer():
    # A deliberately nontrivial fixed module relation.  The point is to verify
    # the exact constant-state cyclic-transfer mechanism used by a repeated
    # 3-edge-interface family; this is not the source-specific T_i table.
    R = [[False] * 8 for _ in range(8)]
    for a in range(8):
        bits = ((a >> 0) & 1, (a >> 1) & 1, (a >> 2) & 1)
        # deterministic rotation plus one optional toggle when parity is even
        b = ((bits[1] << 0) | (bits[2] << 1) | (bits[0] << 2))
        R[a][b] = True
        if sum(bits) % 2 == 0:
            R[a][b ^ 1] = True

    for n in range(1, 9):
        P = power_relation(R, n)
        matrix_cycle = any(P[s][s] for s in range(8))

        brute = False
        for seq in product(range(8), repeat=n):
            if all(R[seq[i]][seq[(i + 1) % n]] for i in range(n)):
                brute = True
                break
        assert matrix_cycle == brute


def main():
    check_d_family()
    check_three_bit_transfer()
    print('PASS R5_E9_A_IRREDUCIBLE_TERMINAL_CONTROLS')
    print('D(n), n=7..36: rank_Q(A_n)=n')
    print('D(n), n=7..15: Boolean Exact-One witness count=0')
    print('3-bit cyclic transfer DP = exact on frozen control relation')
    print('BOBEN_CLASSIFICATION = SOURCE_BOUND_NOT_FINITE_REPROVED')
    print('P_VS_NP = OPEN')


if __name__ == '__main__':
    main()
