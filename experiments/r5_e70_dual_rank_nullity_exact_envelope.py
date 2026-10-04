#!/usr/bin/env python3
"""R5 E70 exact controls: dual binary-rank/nullity exact envelope.

Let A be an n x n square-cubic binary incidence matrix,

    r = rank_F2(A),
    d = n-r.

E56 identifies Exact-One with the minimum-weight solution of

    A x = 1 (mod 2):

Exact-One SAT iff that minimum weight is n/3 (and necessarily 3|n).

Two exact algorithms are then available.

NULLITY SIDE (E58):
Every parity solution is x=1+k with k in ker_F2(A).  Enumerate all 2^d kernel
words and maximize |k| / minimize |1+k|.

RANK SIDE (E70):
Choose r independent original rows.  Each column gives an r-bit syndrome
signature.  A subset of columns solves the full syndrome iff the XOR of its
signatures is the all-ones r-bit target.  Standard subset DP over the 2^r
syndrome states computes the minimum selected cardinality in O(n 2^r).

Therefore Exact-One is decidable exactly in

    2^min(r,d) * poly(n).

This is polynomial whenever min(r,d)=O(log n).  It is NOT universal: the
middle-rank band can have both r and d superlogarithmic.

For a simple square-cubic-linear carrier, all n columns are distinct nonzero
vectors.  Compression to any row basis is injective on columns, hence

    n <= 2^r - 1,

so r >= ceil(log2(n+1)).  Thus the low-rank polynomial edge is near the smallest
rank compatible with n distinct columns.

Controls compare rank-DP, kernel enumeration, and direct Exact-One brute force
on frozen E61 SAT12/UNSAT12, the frozen E17 q=6 RXC3 source, and E69 torus m=3.

Scientific ceiling: this shrinks the unresolved rank/nullity region but does not
supply a universal polynomial algorithm.  P_VS_NP remains OPEN.
"""

from math import ceil, log2

from r5_e61_two_level_kernel_hoffman_regular_set import (
    P_SAT,
    Q_SAT,
    P_UNSAT,
    Q_UNSAT,
    build_A,
)
from r5_e69_nullity_structure_torus_firewall import torus_row_supports


def rows_to_bits(A):
    out = []
    for row in A:
        z = 0
        for j, v in enumerate(row):
            if v & 1:
                z |= 1 << j
        out.append(z)
    return out


def gf2_rref_rows(A):
    """Return RREF bit rows, pivot columns, and rank."""
    m = len(A)
    n = len(A[0])
    rows = rows_to_bits(A)
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
    return rows, pivots, r


def independent_original_rows(A):
    """Greedily choose independent ORIGINAL rows, preserving RHS=1 on each."""
    n = len(A[0])
    basis_by_pivot = {}
    chosen = []
    for i, row in enumerate(A):
        v = 0
        for j, a in enumerate(row):
            if a & 1:
                v |= 1 << j
        z = v
        for p in sorted(basis_by_pivot):
            if (z >> p) & 1:
                z ^= basis_by_pivot[p]
        if z == 0:
            continue
        p = (z & -z).bit_length() - 1
        # Clear this pivot from existing basis rows so later reductions remain stable.
        for q in list(basis_by_pivot):
            if (basis_by_pivot[q] >> p) & 1:
                basis_by_pivot[q] ^= z
        basis_by_pivot[p] = z
        chosen.append(i)
    return chosen


def gf2_kernel_basis(A):
    R, pivots, rank = gf2_rref_rows(A)
    n = len(A[0])
    free = [c for c in range(n) if c not in pivots]
    basis = []
    for f in free:
        v = 1 << f
        for rr, p in enumerate(pivots):
            if (R[rr] >> f) & 1:
                v |= 1 << p
        basis.append(v)
    assert len(basis) == n - rank
    return basis, rank


def kernel_min_parity_weight(A):
    """Exact 2^d side: x=1+k, so min |x| = n-max |k|."""
    n = len(A)
    basis, rank = gf2_kernel_basis(A)
    d = len(basis)
    v = 0
    maxw = 0
    prev_gray = 0
    for mask in range(1, 1 << d):
        gray = mask ^ (mask >> 1)
        diff = gray ^ prev_gray
        bit = diff.bit_length() - 1
        v ^= basis[bit]
        maxw = max(maxw, v.bit_count())
        prev_gray = gray
    return n - maxw, rank, d


def rank_syndrome_min_weight(A):
    """Exact O(n 2^r) subset DP over compressed syndrome states."""
    n = len(A)
    chosen = independent_original_rows(A)
    r = len(chosen)

    # Independent ORIGINAL equations all have RHS 1.  Every omitted row is a
    # combination of chosen rows; since every cubic row has dot(1)=1, the
    # coefficient sum of that combination is automatically 1, so satisfying
    # the chosen equations is equivalent to satisfying all A x = 1 equations.
    signatures = []
    for j in range(n):
        s = 0
        for b, i in enumerate(chosen):
            if A[i][j] & 1:
                s |= 1 << b
        signatures.append(s)

    # In a simple square-cubic carrier all full columns are nonzero and distinct.
    # Restriction to a row basis is injective: equal compressed signatures would
    # imply equal entries on every row, hence equal full columns.
    assert all(s != 0 for s in signatures)
    assert len(set(signatures)) == n
    assert n <= (1 << r) - 1

    INF = n + 1
    dp = [INF] * (1 << r)
    dp[0] = 0
    for s in signatures:
        old = dp
        new = old.copy()
        for state, w in enumerate(old):
            if w <= n:
                t = state ^ s
                if w + 1 < new[t]:
                    new[t] = w + 1
        dp = new

    target = (1 << r) - 1
    return dp[target], r


def direct_exact_one(A):
    n = len(A)
    if n % 3:
        return False
    want = n // 3
    for x in range(1 << n):
        if x.bit_count() != want:
            continue
        if all(sum((x >> j) & 1 for j, a in enumerate(row) if a) == 1 for row in A):
            return True
    return False


def source_q6():
    q = 6
    source_sets = [tuple(sorted({i, (i + 1) % q, (i + 3) % q})) for i in range(q)]
    A = [[0] * q for _ in range(q)]
    for i, S in enumerate(source_sets):
        for j in S:
            A[i][j] = 1
    return A


def torus_m3():
    m = 3
    supports = torus_row_supports(m)
    n = m * m
    A = [[0] * n for _ in range(n)]
    for i, S in enumerate(supports):
        for j in S:
            A[i][j] = 1
    return A


def check_case(name, A, expected_rank, expected_nullity, expected_sat):
    n = len(A)
    assert all(len(row) == n for row in A)
    assert all(sum(row) == 3 for row in A)
    assert all(sum(A[i][j] for i in range(n)) == 3 for j in range(n))

    min_rank, r = rank_syndrome_min_weight(A)
    min_kernel, rr, d = kernel_min_parity_weight(A)
    assert r == rr == expected_rank
    assert d == expected_nullity == n - r
    assert min_rank == min_kernel

    sat_from_min = (n % 3 == 0 and min_rank == n // 3)
    sat_direct = direct_exact_one(A)
    assert sat_from_min == sat_direct == expected_sat

    assert r >= ceil(log2(n + 1))
    print(
        f"{name}: n={n} rank={r} nullity={d} min_parity={min_rank} "
        f"exact_one_sat={sat_direct} envelope_exp={min(r,d)}"
    )


def main():
    check_case("SAT12", build_A(P_SAT, Q_SAT), 10, 2, True)
    check_case("UNSAT12_E57", build_A(P_UNSAT, Q_UNSAT), 11, 1, False)
    check_case("E17_RXC3_Q6", source_q6(), 6, 0, False)
    check_case("E69_TORUS_M3", torus_m3(), 7, 2, True)

    print("R5 E70 dual binary-rank/nullity exact envelope: PASS")
    print("theorem: Exact-One decidable in 2^min(rank_F2(A), nullity_F2(A)) * poly(n)")
    print("rank side: O(n 2^r) minimum-weight syndrome DP; nullity side: E58 kernel enumeration")
    print("simple carrier bound: n <= 2^r-1, hence rank_F2(A) >= ceil(log2(n+1))")
    print("polynomial edges: min(r,n-r)=O(log n); unresolved band has both rank and nullity superlogarithmic")
    print("P_VS_NP remains OPEN")


if __name__ == "__main__":
    main()
