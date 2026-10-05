#!/usr/bin/env python3
"""R5 E71 exact controls: ternary / fixed-prime rank-nullity envelope.

For every cubic 0/1 row and Boolean x, the integer row sum s belongs to
{0,1,2,3}.  Hence for every prime p >= 3,

    s == 1 as an integer  <=>  s == 1 (mod p).

Therefore Exact-One is exactly the Boolean subset-sum problem

    A x = 1 over F_p,   x in {0,1}^n.

Let r_p = rank_Fp(A), d_p=n-r_p.  Two exact algorithms follow:

  rank side:    subset-sum DP over F_p^{r_p}: O(n p^{r_p} poly(r_p));
  nullity side: enumerate the affine solution space: p^{d_p} poly(n).

Thus for every fixed prime p>=3:

    T_p(A) = p^min(r_p,d_p) poly(n).

This is combined with E70's binary envelope, not substituted for it.  The
checker verifies the theorem on small exact controls and freezes stress ranks on
E12, E64, and E69 families.  In particular E69's binary-large-nullity torus
controls can have tiny ternary nullity, while E64 and the E12 hardness target do
not universally collapse.

Scientific ceiling: P_VS_NP remains OPEN.
"""

from itertools import product

from r5_e61_two_level_kernel_hoffman_regular_set import (
    P_SAT, Q_SAT, P_UNSAT, Q_UNSAT, build_A,
)
from r5_e17_hardness_kernel_quotient import (
    rx_fixture, source_matrix, transform_rx, natural_target_matrix,
)
from r5_e64_connected_postquotient_nullity_firewall import (
    tutte_coxeter_incidence, tutte12_incidence,
)
from r5_e69_nullity_structure_torus_firewall import torus_row_supports


def rref_aug(A, b, p):
    """RREF of [A|b] over F_p; return matrix, pivots, inconsistency."""
    m = len(A)
    n = len(A[0]) if m else 0
    M = [[v % p for v in row] + [b[i] % p] for i, row in enumerate(A)]
    pivots = []
    r = 0
    for c in range(n):
        q = next((i for i in range(r, m) if M[i][c] % p), None)
        if q is None:
            continue
        M[r], M[q] = M[q], M[r]
        inv = pow(M[r][c], -1, p)
        M[r] = [(v * inv) % p for v in M[r]]
        for i in range(m):
            if i != r and M[i][c] % p:
                f = M[i][c] % p
                M[i] = [(M[i][j] - f * M[r][j]) % p for j in range(n + 1)]
        pivots.append(c)
        r += 1
        if r == m:
            break

    inconsistent = any(
        all(M[i][j] % p == 0 for j in range(n)) and M[i][n] % p != 0
        for i in range(m)
    )
    return M, pivots, inconsistent


def rank_nullity(A, p):
    M, pivots, _ = rref_aug(A, [0] * len(A), p)
    del M
    return len(pivots), len(A[0]) - len(pivots)


def affine_basis(A, b, p):
    """Return x0, kernel basis, rank for A x=b over F_p, or None if inconsistent."""
    M, pivots, inconsistent = rref_aug(A, b, p)
    if inconsistent:
        return None
    n = len(A[0])
    free = [c for c in range(n) if c not in pivots]
    x0 = [0] * n
    for rr, pc in enumerate(pivots):
        x0[pc] = M[rr][n] % p

    basis = []
    for f in free:
        v = [0] * n
        v[f] = 1
        for rr, pc in enumerate(pivots):
            v[pc] = (-M[rr][f]) % p
        basis.append(v)
    return x0, basis, len(pivots)


def affine_boolean_witness(A, p):
    """Exact p^d search for a Boolean point of A x=1 over F_p."""
    data = affine_basis(A, [1] * len(A), p)
    if data is None:
        return None, None, None
    x0, basis, r = data
    n = len(A[0])
    d = len(basis)
    for coeffs in product(range(p), repeat=d):
        x = x0[:]
        for c, v in zip(coeffs, basis):
            if c:
                for j in range(n):
                    x[j] = (x[j] + c * v[j]) % p
        if all(v in (0, 1) for v in x):
            return x, r, d
    return None, r, d


def encode(vec, p):
    z = 0
    mul = 1
    for v in vec:
        z += (v % p) * mul
        mul *= p
    return z


def add_encoded(a, b, r, p):
    out = 0
    mul = 1
    for _ in range(r):
        da, db = a % p, b % p
        out += ((da + db) % p) * mul
        a //= p
        b //= p
        mul *= p
    return out


def rank_subset_dp(A, p):
    """Exact O(n p^r poly(r)) Boolean subset-sum DP after row reduction."""
    m = len(A)
    n = len(A[0])
    M, pivots, inconsistent = rref_aug(A, [1] * m, p)
    if inconsistent:
        return False, len(pivots)
    r = len(pivots)

    sigs = []
    for j in range(n):
        sigs.append(encode([M[i][j] for i in range(r)], p))
    target = encode([M[i][n] for i in range(r)], p)

    size = p ** r
    dp = bytearray(size)
    dp[0] = 1
    for s in sigs:
        old = dp[:]
        for state in range(size):
            if old[state]:
                dp[add_encoded(state, s, r, p)] = 1
    return bool(dp[target]), r


def exact_one_bruteforce(A):
    n = len(A[0])
    for mask in range(1 << n):
        ok = True
        for row in A:
            s = sum(((mask >> j) & 1) for j, a in enumerate(row) if a)
            if s != 1:
                ok = False
                break
        if ok:
            return True
    return False


def torus_matrix(m):
    supports = torus_row_supports(m)
    n = m * m
    A = [[0] * n for _ in range(n)]
    for i, S in enumerate(supports):
        for j in S:
            A[i][j] = 1
    return A


def check_small(name, A, p, expected_r, expected_d, expected_sat, run_rank_dp=True):
    w, r, d = affine_boolean_witness(A, p)
    assert r == expected_r
    assert d == expected_d
    sat_affine = w is not None
    sat_direct = exact_one_bruteforce(A) if len(A[0]) <= 15 else expected_sat
    assert sat_affine == sat_direct == expected_sat
    if w is not None:
        assert all(v in (0, 1) for v in w)
        assert all(sum(a * x for a, x in zip(row, w)) == 1 for row in A)
    if run_rank_dp:
        sat_dp, rr = rank_subset_dp(A, p)
        assert rr == r
        assert sat_dp == expected_sat
    print(f"{name}: p={p} n={len(A[0])} rank={r} nullity={d} sat={expected_sat}")


def check_stress_rank(name, A, p, expected_r, expected_d):
    r, d = rank_nullity(A, p)
    assert (r, d) == (expected_r, expected_d)
    print(f"{name}: p={p} n={len(A[0])} rank={r} nullity={d}")


def main():
    sat12 = build_A(P_SAT, Q_SAT)
    unsat12 = build_A(P_UNSAT, Q_UNSAT)
    q, source_sets = rx_fixture()
    src6 = source_matrix(q, source_sets)

    # Exact theorem controls over F3.
    check_small("SAT12", sat12, 3, 10, 2, True)
    check_small("UNSAT12_E57", unsat12, 3, 10, 2, False)
    check_small("E17_RXC3_SOURCE_Q6", src6, 3, 5, 1, False)
    check_small("E69_TORUS_M3", torus_matrix(3), 3, 6, 3, True)

    # Prime-general sanity: p=5 also isolates integer row sum exactly one.
    check_small("SAT12_P5", sat12, 5, 11, 1, True, run_rank_dp=False)
    check_small("UNSAT12_P5", unsat12, 5, 11, 1, False, run_rank_dp=False)

    # E69: binary nullity grows as m-1, while ternary nullity is tiny here.
    check_small("E69_TORUS_M7", torus_matrix(7), 3, 48, 1, False, run_rank_dp=False)
    check_small("E69_TORUS_M15", torus_matrix(15), 3, 222, 3, True, run_rank_dp=False)

    # Stress controls: ternary nullity does NOT universally collapse.
    check_stress_rank("E64_GQ22", tutte_coxeter_incidence(), 3, 10, 5)
    check_stress_rank("E64_GH22", tutte12_incidence(), 3, 49, 14)

    target = natural_target_matrix(transform_rx(q, source_sets))
    check_stress_rank("E12_TARGET_Q6", target, 3, 82, 20)

    # Structural rank floor for simple columns over F_p: n <= p^r-1.
    for name, A in [("SAT12", sat12), ("UNSAT12", unsat12), ("GQ22", tutte_coxeter_incidence())]:
        r, _ = rank_nullity(A, 3)
        cols = [tuple(A[i][j] for i in range(len(A))) for j in range(len(A[0]))]
        assert all(any(c) for c in cols)
        assert len(set(cols)) == len(cols)
        assert len(cols) <= 3 ** r - 1

    print("R5 E71 ternary/fixed-prime rank-nullity envelope: PASS")
    print("theorem: for every fixed prime p>=3, Exact-One iff A x=1 over F_p for Boolean x")
    print("algorithm: p^min(rank_Fp(A), nullity_Fp(A)) * poly(n)")
    print("combined with E70: choose binary weight-envelope or ternary Boolean-envelope per instance")
    print("E69 controls: d3(m=3,7,15)=(3,1,3), so binary-large nullity can collapse over F3")
    print("E64 GH22: d3=14; E12 q6 target: d3=20, so ternary nullity is not universally small")
    print("P_VS_NP remains OPEN")


if __name__ == "__main__":
    main()
