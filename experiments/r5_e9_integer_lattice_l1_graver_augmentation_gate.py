#!/usr/bin/env python3
"""Exact regression checker for the integer-lattice L1 / Graver gate.

Stdlib only.  This checker verifies the theorem's scalar identity and the two
frozen PG15 controls.  It deliberately does NOT pretend to implement the open
Graver-best-step oracle.
"""

from itertools import combinations

SAT_LINES = [
    (1,2,3),(1,10,11),(1,12,13),(2,9,11),(2,12,14),
    (3,4,7),(3,5,6),(4,9,13),(4,10,14),(5,8,13),
    (5,10,15),(6,8,14),(6,9,15),(7,8,15),(7,11,12),
]

UNSAT_LINES = [
    (1,10,11),(1,12,13),(1,14,15),(2,4,6),(2,5,7),
    (2,12,14),(3,4,7),(3,8,11),(3,9,10),(4,11,15),
    (5,8,13),(5,9,12),(6,8,14),(6,9,15),(7,10,13),
]

SAT_SUPPORT_0 = {0, 4, 6, 8, 13}
UNSAT_INTEGER_WITNESS = [0,0,1,0,1,1,0,-1,0,0,1,0,1,1,0]


def incidence(lines, n=15):
    A = [[0] * n for _ in lines]
    for r, row in enumerate(lines):
        assert len(row) == 3 and len(set(row)) == 3
        for j in row:
            assert 1 <= j <= n
            A[r][j - 1] = 1
    return A


def matvec(A, x):
    return [sum(a * b for a, b in zip(row, x)) for row in A]


def F(z):
    return sum(abs(2 * t - 1) for t in z)


def check_cubic_linear(A):
    n = len(A)
    assert all(len(row) == n for row in A)
    assert all(sum(row) == 3 for row in A), "row degree must be 3"
    assert all(sum(A[r][c] for r in range(n)) == 3 for c in range(n)), \
        "column degree must be 3"
    supports = [{j for j, a in enumerate(row) if a} for row in A]
    assert all(len(supports[i] & supports[j]) <= 1
               for i in range(n) for j in range(i + 1, n)), \
        "source must be linear"


def exact_boolean_witnesses(A):
    n = len(A)
    # In a square cubic source, summing Ax=1 forces 3*|x|=n.
    assert n % 3 == 0
    target_weight = n // 3
    out = []
    for support in combinations(range(n), target_weight):
        S = set(support)
        x = [1 if i in S else 0 for i in range(n)]
        if matvec(A, x) == [1] * n:
            out.append(support)
    return out


def scalar_lemma_regression():
    for k in range(-20, 21):
        term = abs(2 * k - 1)
        assert term >= 1
        assert (term == 1) == (k in (0, 1))
        assert (term - 1) == 2 * min(abs(k), abs(k - 1))


def main():
    scalar_lemma_regression()

    A_sat = incidence(SAT_LINES)
    A_unsat = incidence(UNSAT_LINES)
    check_cubic_linear(A_sat)
    check_cubic_linear(A_unsat)

    x_sat = [1 if i in SAT_SUPPORT_0 else 0 for i in range(15)]
    assert matvec(A_sat, x_sat) == [1] * 15
    assert F(x_sat) == 15

    sat_witnesses = exact_boolean_witnesses(A_sat)
    assert tuple(sorted(SAT_SUPPORT_0)) in sat_witnesses
    assert sat_witnesses, "SAT control must have a Boolean witness"

    unsat_witnesses = exact_boolean_witnesses(A_unsat)
    assert not unsat_witnesses, "UNSAT control unexpectedly has a Boolean witness"

    z = UNSAT_INTEGER_WITNESS
    assert matvec(A_unsat, z) == [1] * 15, "integer lattice witness is invalid"
    assert F(z) == 17

    # Exact optimum certification for this frozen control:
    # no Boolean point => gap theorem gives OPT >= n+2 = 17;
    # displayed integer point has F=17 => OPT <= 17.
    lower_bound = 17
    upper_bound = F(z)
    assert lower_bound == upper_bound == 17

    # Finite-box lemma on the displayed point.
    F0 = F(z)
    lo_num, hi_num = 1 - F0, 1 + F0
    for value in z:
        assert 2 * value >= lo_num
        assert 2 * value <= hi_num

    print("PASS: scalar L1 identity")
    print(f"PASS: SAT PG15 witnesses={len(sat_witnesses)}, optimum=15")
    print("PASS: UNSAT PG15 exact Boolean enumeration empty")
    print("PASS: UNSAT PG15 integer lattice witness F=17 => exact optimum=17")
    print("OPEN: LINEAR_CUBIC_GRAVER_BEST_STEP_POLYTIME_GATE_V1")
    print("P_VS_NP=OPEN; E8_D1=EMPTY")


if __name__ == "__main__":
    main()
