#!/usr/bin/env python3
"""Exact v8.5.4 checker: collapse all edge zero/free states to chi_M(3)."""

from collections import Counter
from itertools import permutations, product

VP = (1, 1, 0, 1, 1, 0)
VM = (1, 2, 0, 2, 0, 1)


def mod3(x):
    return x % 3


def wire_state(c, s, q):
    # Canonical exposed-port order: L0,L2,L3,R0,R2,R3.
    return (
        mod3(c + s),
        mod3(c + s * q),
        mod3(c),
        mod3(c + s * q),
        mod3(c - s * (1 + q)),
        mod3(c + s * (q - 1)),
    )


WIRE6 = sorted(
    {
        wire_state(c, s, q)
        for c in range(3)
        for s in (1, 2)
        for q in (1, 2)
    }
)
assert len(WIRE6) == 12


def gf3_rref_basis(rows, ncols):
    a = [[x % 3 for x in row] for row in rows if any(x % 3 for x in row)]
    r = 0
    c = 0
    while r < len(a) and c < ncols:
        pivot = next((i for i in range(r, len(a)) if a[i][c] % 3), None)
        if pivot is None:
            c += 1
            continue
        a[r], a[pivot] = a[pivot], a[r]
        inv = 1 if a[r][c] == 1 else 2
        a[r] = [(inv * x) % 3 for x in a[r]]
        for i in range(len(a)):
            if i == r or a[i][c] == 0:
                continue
            f = a[i][c]
            a[i] = [(x - f * y) % 3 for x, y in zip(a[i], a[r])]
        r += 1
        c += 1
    return a[:r]


def gf3_rank(rows, ncols):
    return len(gf3_rref_basis(rows, ncols))


def direct_closed_count(pi):
    z = 0
    for x in WIRE6:
        for y in WIRE6:
            if all(x[j] != y[pi[j]] for j in range(6)):
                z += 1
    return z


def matrix_for_tau(pi, t1, t2):
    """Rows A_tau in the six oriented splice-current coordinates.

    Local state 0 adds no VP/VM row, + adds VP, - adds VM.
    The two conservation rows are retained even though they are dependent in a
    two-wire closure; exact rank takes care of that automatically.
    """
    n = 6
    rows = [[1] * n, [2] * n]
    lp1 = list(VP)
    lm1 = list(VM)
    lp2 = [(-VP[pi[j]]) % 3 for j in range(n)]
    lm2 = [(-VM[pi[j]]) % 3 for j in range(n)]

    for t, lp, lm in ((t1, lp1, lm1), (t2, lp2, lm2)):
        if t == 1:
            rows.append(lp)
        elif t == 2:
            rows.append(lm)
    return rows


def characteristic_at_three(rows, ncols):
    """chi_M(3) for the column matroid represented by rows."""
    r_full = gf3_rank(rows, ncols)
    chi = 0
    for mask in range(1 << ncols):
        cols = [j for j in range(ncols) if (mask >> j) & 1]
        if cols:
            restricted = [[row[j] for j in cols] for row in rows]
            r_u = gf3_rank(restricted, len(cols))
        else:
            r_u = 0
        chi += ((-1) ** len(cols)) * (3 ** (r_full - r_u))
    return chi, r_full


def full_support_rowspace_count(rows, ncols):
    """Count row-space vectors whose every coordinate is nonzero."""
    basis = gf3_rref_basis(rows, ncols)
    total = 0
    for coeff in product(range(3), repeat=len(basis)):
        word = [
            sum(coeff[i] * basis[i][j] for i in range(len(basis))) % 3
            for j in range(ncols)
        ]
        if all(word):
            total += 1
    return total


def collapsed_closed_count(pi):
    """Evaluate only 3^2 local tau states; edge subset sum is analytic.

    For fixed tau and E=6 edge-current variables,

      sum_S (-1)^(E-|S|) 3^|S| 3^(E-rank([A_tau; I_S]))
        = 3^(E-r(M_tau)) * chi_{M_tau}(3).

    This is the exact collapse of all 2^E edge zero/free states.
    """
    n = 6
    total = 0
    local_states = 0
    for t1 in range(3):
        for t2 in range(3):
            rows = matrix_for_tau(pi, t1, t2)
            chi3, r_full = characteristic_at_three(rows, n)

            # Independent finite control of the representable-matroid identity:
            # chi_M(3) = number of full-support codewords in Row(A_tau).
            assert chi3 == full_support_rowspace_count(rows, n)

            w1 = -2 if t1 == 0 else 3
            w2 = -2 if t2 == 0 else 3
            total += w1 * w2 * (3 ** (n - r_full)) * chi3
            local_states += 1

    assert local_states == 3 ** 2 == 9
    assert total % (3 ** 4) == 0
    return total // (3 ** 4)


count_profile = Counter()
for pi in permutations(range(6)):
    direct = direct_closed_count(pi)
    collapsed = collapsed_closed_count(pi)
    assert collapsed == direct
    count_profile[direct] += 1

expected = Counter({0: 96, 6: 180, 12: 168, 18: 168, 24: 80, 30: 20, 36: 8})
assert count_profile == expected

print("PASS: fixed-tau 2^E edge zero/free expansion collapses exactly to 3^(E-r(M_tau))*chi_M_tau(3)")
print("PASS: chi_M_tau(3) independently equals the number of full-support GF(3) row-space codewords")
print("PASS: only 3^2=9 explicit local tau states remain per two-wire closure")
print("PASS: characteristic-collapse evaluation matches direct 12-state counting for all 6!=720 port matchings")
print("DIRECT_COUNT_PROFILE=0:96,6:180,12:168,18:168,24:80,30:20,36:8")
print("EXPLICIT_STATE_REDUCTION=24^m_TO_3^m_CHARACTERISTIC_TERMS")
print("VERDICT: EXACT_EDGE_STATE_CHARACTERISTIC_POLYNOMIAL_COLLAPSE_ESTABLISHED")
print("FRONTIER: COMPRESS_THE_3^m_LOCAL_TRANSITION_SUM_AND_EVALUATE_THE_SPECIAL_CHI_M_TAU_3_FAMILY_WITH_WITNESS_RECONSTRUCTION")
print("P_VS_NP=OPEN; P_EQUALS_NP_ALGORITHM=NOT_CONSTRUCTED; E8_D1=EMPTY")
