#!/usr/bin/env python3
"""R5 E65 exact controls: transpose asymmetry + quantized parity defect.

This checker works on the genuine post-quotient Tutte 12-cage incidence matrix
from E64.  It proves two independent facts.

1. Transpose asymmetry.
   For the E64 orientation R (q=63), Exact-One is UNSAT, while R^T is SAT.
   Thus rank, nullity, singular values, Smith-normal-form data, determinant,
   uncoloured Levi graph, girth, and every other transpose-invariant datum are
   insufficient by themselves to decide Exact-One.

2. Quantized parity defect.
   For any square cubic matrix with n divisible by 3 and any binary x with

       R x = 1 (mod 2),

   every row has selected count 1 or 3.  If t3 is the number of 3-rows, then

       3 |x| = n + 2 t3,
       t3 = 3 m,
       |x| = n/3 + 2 m,
       ||R x - 1||_2^2 = 12 m,

   for an integer m >= 0.

For the UNSAT Tutte-12 orientation the lower nonzero level is attained exactly:
   * min parity weight = 23 = 63/3 + 2;
   * t3 = 3 and energy = 12;
   * there are 252 minimum parity solutions;
   * their three triple-covered rows form exactly the support of one selected
     column;
   * all 63 columns occur, with exactly four minimum solutions per column.

So even the smallest possible, maximally localized parity defect need not be
repairable to an Exact-One solution.

Scientific ceiling: this is a post-quotient anti-loop / structural theorem, not
a universal polynomial algorithm.  P_VS_NP remains OPEN.
"""

from collections import Counter

from r5_e64_connected_postquotient_nullity_firewall import (
    tutte12_incidence,
    two_level_kernel_count,
    verify_square_cubic_linear,
)


def transpose(M):
    return [list(col) for col in zip(*M)]


def gf2_rref_basis(M):
    """Return a bit-packed basis for ker_F2(M)."""
    m = len(M)
    n = len(M[0])
    rows = []
    for row in M:
        z = 0
        for j, v in enumerate(row):
            if v & 1:
                z |= 1 << j
        rows.append(z)

    pivots = []
    r = 0
    for c in range(n):
        p = next((i for i in range(r, m) if (rows[i] >> c) & 1), None)
        if p is None:
            continue
        rows[r], rows[p] = rows[p], rows[r]
        for i in range(m):
            if i != r and ((rows[i] >> c) & 1):
                rows[i] ^= rows[r]
        pivots.append(c)
        r += 1
        if r == m:
            break

    free = [c for c in range(n) if c not in pivots]
    basis = []
    for f in free:
        v = 1 << f
        for rr, p in enumerate(pivots):
            if (rows[rr] >> f) & 1:
                v |= 1 << p
        basis.append(v)

    return pivots, free, basis


def row_sums(M, xbits):
    return [
        sum(v for j, v in enumerate(row) if (xbits >> j) & 1)
        for row in M
    ]


def parity_coset_solutions(M):
    """Enumerate R x = 1 mod 2 using x=1+k, k in ker_F2(R)."""
    n = len(M)
    _, free, basis = gf2_rref_basis(M)
    ones = (1 << n) - 1
    out = []
    for mask in range(1 << len(basis)):
        k = 0
        for j, b in enumerate(basis):
            if (mask >> j) & 1:
                k ^= b
        x = ones ^ k
        sums = row_sums(M, x)
        assert all(s in (1, 3) for s in sums)
        out.append((x, sums))
    return len(free), out


def verify_quantization(M, solutions):
    n = len(M)
    assert n % 3 == 0
    for x, sums in solutions:
        w = x.bit_count()
        t3 = sum(s == 3 for s in sums)
        energy = sum((s - 1) ** 2 for s in sums)

        assert 3 * w == n + 2 * t3
        assert t3 % 3 == 0
        m = t3 // 3
        assert w == n // 3 + 2 * m
        assert energy == 4 * t3 == 12 * m


def common_support_column(M, bad_rows):
    cols = [
        j
        for j in range(len(M[0]))
        if all(M[i][j] for i in bad_rows)
    ]
    assert len(cols) == 1
    return cols[0]


def main():
    R = tutte12_incidence()
    RT = transpose(R)
    q = len(R)
    assert q == 63

    # Both orientations are genuine connected square-cubic-linear quotients
    # with the same uncoloured Levi graph / girth.
    verify_square_cubic_linear(R, expected_girth=12)
    verify_square_cubic_linear(RT, expected_girth=12)

    dR, two_R = two_level_kernel_count(R)
    dT, two_T = two_level_kernel_count(RT)
    assert dR == dT == 14
    assert two_R == 0
    assert two_T == 36

    # Exact transpose firewall.
    print(
        f"transpose pair: q={q} nullity={dR}; "
        f"R two_level={two_R} SAT={bool(two_R)}; "
        f"R^T two_level={two_T} SAT={bool(two_T)}"
    )

    # Enumerate the complete binary parity coset of the UNSAT orientation.
    d2, sol = parity_coset_solutions(R)
    assert d2 == 14
    assert len(sol) == 1 << 14
    verify_quantization(R, sol)

    min_w = min(x.bit_count() for x, _ in sol)
    mins = [(x, sums) for x, sums in sol if x.bit_count() == min_w]

    assert min_w == 23 == q // 3 + 2
    assert len(mins) == 252

    support_counter = Counter()
    unique_bad_supports = set()
    for x, sums in mins:
        bad = tuple(i for i, s in enumerate(sums) if s == 3)
        assert len(bad) == 3
        assert sum((s - 1) ** 2 for s in sums) == 12

        c = common_support_column(R, bad)
        # The column whose support is exactly the 3-row defect star is selected.
        assert (x >> c) & 1
        col_support = tuple(i for i in range(q) if R[i][c])
        assert tuple(sorted(bad)) == tuple(sorted(col_support))

        unique_bad_supports.add(tuple(sorted(bad)))
        support_counter[c] += 1

    assert len(unique_bad_supports) == 63
    assert set(support_counter) == set(range(63))
    assert set(support_counter.values()) == {4}

    # The transpose SAT orientation must hit the m=0 level.
    d2T, solT = parity_coset_solutions(RT)
    assert d2T == 14
    verify_quantization(RT, solT)
    min_w_T = min(x.bit_count() for x, _ in solT)
    exact_T = [x for x, sums in solT if all(s == 1 for s in sums)]
    assert min_w_T == 21
    assert len(exact_T) == 36 == two_T

    print(
        "UNSAT orientation nearest parity layer: "
        "weight=23, t3=3, energy=12, minimizers=252"
    )
    print(
        "localized defect classification: 63 column-support stars, "
        "4 nearest parity solutions per star"
    )
    print("transpose SAT orientation: exact parity/Exact-One solutions=36 at weight=21")
    print("R5 E65 transpose asymmetry / quantized parity-defect theorem: PASS")
    print("P_VS_NP remains OPEN")


if __name__ == "__main__":
    main()
