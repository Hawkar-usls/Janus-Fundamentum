#!/usr/bin/env python3
"""Exact controls for R5 E24.

Verifies the integer-to-Boolean defect identity and the sharp PG15_UNSAT gap.

For any integer solution Ax=1 in a square cubic source:
    Phi(x)=sum_i x_i(x_i-1) is an even nonnegative integer,
    y=3x-1 lies in ker_Z(A), and
    ||y||^2 = 2n + 9 Phi(x).
Thus SAT iff the congruence kernel coset contains a vector of squared norm 2n;
integer-feasible UNSAT has squared norm at least 2n+18.

PG15_UNSAT attains the first possible gap exactly: Phi=2 and ||y||^2=2n+18.
P_VS_NP remains OPEN.
"""

PG15_P = [5,7,9,10,3,1,14,2,4,6,12,13,8,0,11]
PG15_Q = [12,9,14,11,13,10,7,3,1,0,2,5,6,8,4]
PG15_KERNEL = (1,4,1,1,-2,-2,1,-2,-2,-2,-2,1,1,1,1)


def matvec(A, x):
    return [sum(a*b for a,b in zip(row,x)) for row in A]


def pg15_unsat_matrix():
    n = 15
    A = [[0]*n for _ in range(n)]
    for i in range(n):
        for j in (i, PG15_P[i], PG15_Q[i]):
            A[i][j] = 1
    return A


def phi(x):
    return sum(v*(v-1) for v in x)


def centered(x):
    return [3*v-1 for v in x]


def norm2(v):
    return sum(x*x for x in v)


def check_pg15_sharp_gap():
    A = pg15_unsat_matrix()
    z = list(PG15_KERNEL)
    assert matvec(A, z) == [0]*15

    # One integral solution from R5 E23.
    x0 = [(1 + 2*v)//3 for v in z]
    assert matvec(A, x0) == [1]*15

    # Shift once along the primitive integer kernel generator.
    x = [x0[i] - z[i] for i in range(15)]
    expected = [0,-1,0,0,1,1,0,1,1,1,1,0,0,0,0]
    assert x == expected
    assert matvec(A, x) == [1]*15
    assert phi(x) == 2

    y = centered(x)
    assert matvec(A, y) == [0]*15
    assert all((v + 1) % 3 == 0 for v in y)
    assert sum(y) == 0
    assert norm2(y) == 2*15 + 18
    assert norm2(y) == 2*15 + 9*phi(x)

    # Along the one-dimensional integer solution lattice x+kz, verify that
    # k=0 for this chosen x is the exact nearest defect among a sufficiently
    # wide finite interval; the symbolic quadratic proof is in the note.
    vals = []
    for k in range(-20, 21):
        xx = [x[i] + k*z[i] for i in range(15)]
        vals.append((phi(xx), k))
    assert min(vals) == (2, 0)
    return x, y


def main():
    x, y = check_pg15_sharp_gap()
    print("R5 E24 integer-box energy-gap controls: PASS")
    print(f"PG15 nearest integer solution x*={x}")
    print("Phi(x*)=2 (first possible positive defect)")
    print(f"centered y*={y}")
    print("||y*||^2=48=2*15+18: universal additive gap 18 is sharp")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
