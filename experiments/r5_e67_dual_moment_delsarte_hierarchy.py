#!/usr/bin/env python3
"""R5 E67: orientation-sensitive dual-moment / Delsarte hierarchy.

This checker tests the post-E66 idea that low-order MacWilliams/Delsarte data
might certify the top-shell ceiling

    max_{k in ker_F2(A)} |k| < 2n/3

without enumerating the full kernel.

It proves two complementary facts.

POSITIVE RESULT (Tutte-12 UNSAT orientation):
The kernel weight support is exactly

    {0,16,24,28,32,36,40}.

Hence the degree-12 nonnegative annihilator

    P(w)=prod_{s in {16,24,28,32,36,40}} (w-s)^2

is determined by the first 12 Krawtchouk/MacWilliams moments.  Because the
actual code has A_0=1 and all positive support at roots of P,

    sum_w A_w P(w)=P(0).

Any nonnegative Delsarte-feasible weight distribution with the same first 12
dual moments must therefore also satisfy A_42=0, since P(42)>0.  Thus this is
an exact polynomially-checkable UNSAT certificate for this instance.

ANTI-LOOP RESULT (connected 2-lift):
A deterministic connected 2-lift of the same incidence carrier has

    n=126, girth=12, dim ker_F2=16, max kernel weight=80<84,

so it is Exact-One UNSAT.  Nevertheless an explicit rational pseudo weight
distribution matches the true dual moments B_0,...,B_12, satisfies every
remaining Delsarte nonnegativity inequality, and has positive mass at weight
84.  Therefore level 12 is not universal even on connected square-cubic-linear
girth-12 post-quotient carriers.

The frozen E17/E12 q=6 RXC3 quotient is also replayed as a sanity check; its
binary kernel is trivial, so its UNSAT certificate is immediate.

Scientific ceiling: this is a certificate hierarchy and a firewall, not a
universal polynomial algorithm.  P_VS_NP remains OPEN.
"""

from collections import Counter
from fractions import Fraction
from math import comb
import random

from r5_e64_connected_postquotient_nullity_firewall import (
    tutte12_incidence,
    verify_square_cubic_linear,
)


def gf2_kernel_basis(M):
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

    free = [c for c in range(n) if c not in pivots]
    basis = []
    for f in free:
        v = 1 << f
        for rr, p in enumerate(pivots):
            if (rows[rr] >> f) & 1:
                v |= 1 << p
        basis.append(v)
    return basis


def kernel_weight_enumerator(M):
    basis = gf2_kernel_basis(M)
    W = Counter()
    for mask in range(1 << len(basis)):
        v = 0
        for j, b in enumerate(basis):
            if (mask >> j) & 1:
                v ^= b
        W[v.bit_count()] += 1
    return len(basis), dict(sorted(W.items()))


def krawtchouk(n, j, w):
    return sum(
        (-1) ** a * comb(w, a) * comb(n - w, j - a)
        for a in range(max(0, j - (n - w)), min(j, w) + 1)
    )


def dual_coeff(W, n, j):
    size = sum(W.values())
    z = sum(A * krawtchouk(n, j, w) for w, A in W.items())
    assert z % size == 0
    return z // size


def solve_square_q(A, b):
    A = [
        [Fraction(x) for x in row] + [Fraction(bb)]
        for row, bb in zip(A, b)
    ]
    n = len(A)
    for c in range(n):
        p = next(i for i in range(c, n) if A[i][c])
        A[c], A[p] = A[p], A[c]
        z = A[c][c]
        A[c] = [x / z for x in A[c]]
        for i in range(n):
            if i != c and A[i][c]:
                f = A[i][c]
                A[i] = [x - f * y for x, y in zip(A[i], A[c])]
    return [A[i][-1] for i in range(n)]


def two_lift(M, seed=1):
    rng = random.Random(seed)
    n = len(M)
    L = [[0] * (2 * n) for _ in range(2 * n)]
    for i, row in enumerate(M):
        for j, v in enumerate(row):
            if not v:
                continue
            s = rng.getrandbits(1)
            if s == 0:
                L[2 * i][2 * j] = 1
                L[2 * i + 1][2 * j + 1] = 1
            else:
                L[2 * i][2 * j + 1] = 1
                L[2 * i + 1][2 * j] = 1
    return L


def base_certificate(R):
    d, W = kernel_weight_enumerator(R)
    expected = {
        0: 1,
        16: 126,
        24: 1596,
        28: 2880,
        32: 7497,
        36: 4032,
        40: 252,
    }
    assert d == 14
    assert W == expected

    roots = [16, 24, 28, 32, 36, 40]

    def P(w):
        z = 1
        for s in roots:
            z *= (w - s) ** 2
        return z

    # Degree-12 polynomial -> exact expansion in K_0,...,K_12.
    K = [[krawtchouk(63, j, w) for j in range(13)] for w in range(13)]
    coeff = solve_square_q(K, [P(w) for w in range(13)])
    for w in range(64):
        assert sum(coeff[j] * krawtchouk(63, j, w) for j in range(13)) == P(w)

    B = [dual_coeff(W, 63, j) for j in range(13)]
    moment = (1 << d) * sum(coeff[j] * B[j] for j in range(13))
    assert moment == P(0)
    assert P(42) > 0

    return d, W, B, P(0), P(42)


PSEUDO = {
    0: Fraction(1),
    16: Fraction(737230151, 299620750),
    18: Fraction(26942257, 8613000),
    34: Fraction(76605003, 309400),
    36: Fraction(122815463, 1128600),
    48: Fraction(627465703, 368550),
    50: Fraction(471740981, 90168),
    58: Fraction(23982821, 10725),
    60: Fraction(61545023, 2574),
    66: Fraction(221506487, 81000),
    68: Fraction(16388133883, 663000),
    74: Fraction(97590001, 35815),
    76: Fraction(745885853, 395850),
    84: Fraction(10158992251, 334748700),
}


def lift_firewall(R):
    L = two_lift(R, seed=1)
    verify_square_cubic_linear(L, expected_girth=12)

    d, W = kernel_weight_enumerator(L)
    expected = {
        0: 1,
        16: 4,
        28: 2,
        32: 160,
        40: 346,
        44: 190,
        48: 2800,
        52: 2796,
        56: 8396,
        60: 8770,
        64: 20531,
        68: 11380,
        72: 9034,
        76: 798,
        80: 328,
    }
    assert d == 16
    assert W == expected
    assert max(W) == 80
    assert 84 not in W

    size = 1 << d
    assert sum(PSEUDO.values()) == size
    assert PSEUDO[0] == 1
    assert PSEUDO[84] > 0

    B = [dual_coeff(W, 126, j) for j in range(127)]

    # Exact matching of the first 12 dual moments.
    for j in range(13):
        q = sum(
            a * krawtchouk(126, j, w)
            for w, a in PSEUDO.items()
        ) / size
        assert q == B[j]

    # Full Delsarte positivity beyond the frozen low moments.
    for j in range(13, 127):
        q = sum(
            a * krawtchouk(126, j, w)
            for w, a in PSEUDO.items()
        ) / size
        assert q >= 0
        assert q <= comb(126, j)

    return d, W, B


def e17_q6_sanity():
    q = 6
    source_sets = [
        tuple(sorted({i, (i + 1) % q, (i + 3) % q}))
        for i in range(q)
    ]
    M = [[0] * q for _ in range(q)]
    for j, C in enumerate(source_sets):
        for e in C:
            M[e][j] = 1

    d, W = kernel_weight_enumerator(M)
    assert d == 0
    assert W == {0: 1}
    return d, W


def main():
    R = tutte12_incidence()
    verify_square_cubic_linear(R, expected_girth=12)

    d, W, B, p0, p42 = base_certificate(R)
    dl, Wl, _Bl = lift_firewall(R)
    dq, Wq = e17_q6_sanity()

    print("R5 E67 dual-moment Delsarte hierarchy: PASS")
    print(
        "base Tutte-12: "
        f"dim={d}, nonzero weights={sorted(w for w in W if w)}, "
        "degree-12 annihilator certifies A_42=0"
    )
    print(f"base certificate: P(0)={p0}, P(42)={p42}, B_0..B_12={B}")
    print(
        "connected seed-1 2-lift: "
        f"n=126 dim={dl} max_kernel_weight={max(Wl)} < 84"
    )
    print(
        "level-12 Delsarte pseudodistribution has exact "
        f"A_84={PSEUDO[84]} > 0 while matching B_0..B_12 "
        "and all Delsarte positivity inequalities"
    )
    print(
        "frozen E17/E12 q=6 RXC3 quotient sanity: "
        f"dim_F2={dq}, W={Wq}, trivial UNSAT certificate"
    )
    print(
        "fixed level 12 is therefore not universal even on connected "
        "cubic-linear girth-12 post-quotient carriers"
    )
    print("P_VS_NP remains OPEN")


if __name__ == "__main__":
    main()
