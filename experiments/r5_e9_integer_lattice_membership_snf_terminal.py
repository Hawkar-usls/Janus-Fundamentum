#!/usr/bin/env python3
"""Exact controls for the integer-lattice / Smith terminal."""

from math import prod

import sympy as sp
from sympy.matrices.normalforms import smith_normal_form
from sympy.polys.domains import ZZ

from r5_e9_paley_voltage_post_rkpr_linear_nullity_family import (
    VOLTAGES,
    cyclic_lift,
    paley11,
    rank_mod_p,
)


MOD9_CERT = [
    4,1,7,1,1,1,4,7,1,5,5,5,0,3,6,8,8,8,2,5,8,8,5,2,1,1,1,3,3,3,
    0,0,0,7,1,4,5,2,8,6,3,0,0,0,0,1,1,1,4,7,1,3,6,0,5,2,8,5,2,8,
    6,6,6,7,1,4,3,3,3,3,0,6,0,0,0,8,8,8,0,0,0,4,4,4,4,4,4,0,0,0,
    2,8,5,0,6,3,7,4,1,0,0,0,0,0,0,3,6,0,2,5,8,3,6,0,2,8,5,3,6,0,
    1,1,1,0,0,0,4,7,1,6,0,3,0,0,0,6,3,0,0,0,0,3,6,0,0,0,0,0,0,0,
    6,3,0,0,0,0,0,0,0,6,3,0,0,0,0,
]

PG15_ROWS = [
    (1,2,3),(1,10,11),(1,12,13),(2,9,11),(2,12,14),(3,4,7),
    (3,5,6),(4,9,13),(4,10,14),(5,8,13),(5,10,15),(6,8,14),
    (6,9,15),(7,8,15),(7,11,12),
]
P = [5,7,9,10,3,1,14,2,4,6,12,13,8,0,11]
Q = [12,9,14,11,13,10,7,3,1,0,2,5,6,8,4]


def matrix_from_rows(rows, n):
    return sp.Matrix([[int(j + 1 in row) for j in range(n)] for row in rows])


def singular_unsat_matrix():
    A = sp.zeros(15, 15)
    for i in range(15):
        for j in (i, P[i], Q[i]):
            A[i, j] = 1
    return A


def nonzero_snf_invariants(M):
    D = smith_normal_form(M, domain=ZZ)
    return [abs(int(D[i, i])) for i in range(min(D.rows, D.cols)) if D[i, i] != 0]


def lattice_index_witness(A, b):
    d = nonzero_snf_invariants(A)
    da = nonzero_snf_invariants(A.row_join(b))
    assert len(d) == len(da)  # same rational span in these controls
    return d, da, prod(d) // prod(da)


def main():
    A0, _, _ = paley11()
    B = cyclic_lift(A0, 3, VOLTAGES)
    one = sp.ones(165, 1)

    # Old field screens both pass.
    assert rank_mod_p(B, 2) == rank_mod_p(B.row_join(one), 2) == 149
    assert rank_mod_p(B, 3) == rank_mod_p(B.row_join(one), 3) == 148

    d, da, index = lattice_index_witness(B, one)
    assert len(d) == len(da) == 149
    assert d[-1] == 9
    assert da[-1] == 3
    assert prod(d) == 9
    assert prod(da) == 3
    assert index == 3

    # Direct short certificate: y^T B = 0 mod 9 but y^T 1 = 6 mod 9.
    assert len(MOD9_CERT) == 165
    y = sp.Matrix(MOD9_CERT)
    lhs = (y.T * B)
    assert all(int(lhs[0, j]) % 9 == 0 for j in range(B.cols))
    assert sum(MOD9_CERT) % 9 == 6

    # Positive control: a known SAT source must pass integer-lattice membership.
    PG15 = matrix_from_rows(PG15_ROWS, 15)
    pg_d, pg_da, pg_index = lattice_index_witness(PG15, sp.ones(15, 1))
    assert pg_index == 1
    assert prod(pg_d) == prod(pg_da) == 2

    # Negative residual control: this frozen rank-14 UNSAT source also passes the
    # lattice test.  Therefore the Smith terminal is useful but not complete.
    SING = singular_unsat_matrix()
    s_d, s_da, s_index = lattice_index_witness(SING, sp.ones(15, 1))
    assert s_index == 1
    assert prod(s_d) == prod(s_da) == 1

    print("PASS R5_E9_INTEGER_LATTICE_MEMBERSHIP_SNF_TERMINAL")
    print("Paley-voltage B: F2=PASS F3=PASS integer-lattice=FAIL index=3")
    print("explicit mod9 certificate: y^T B=0, y^T 1=6 (mod 9)")
    print("PG15 SAT: lattice index=1")
    print("rank-14 UNSAT residual: lattice index=1 (Boolean obstruction remains)")
    print("P_VS_NP=OPEN E8_D1=EMPTY")


if __name__ == "__main__":
    main()
