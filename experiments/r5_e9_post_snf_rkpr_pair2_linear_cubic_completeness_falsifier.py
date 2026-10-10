#!/usr/bin/env python3
"""Exact checker for the post-SNF/RKPR pair2 completeness falsifier.

Standard-library only.  All lattice tests use exact integer gcd/minor arithmetic.
"""

from itertools import combinations, product
from math import gcd
from fractions import Fraction

P = [4, 2, 6, 9, 3, 8, 0, 10, 1, 11, 5, 7]
Q = [7, 0, 5, 6, 2, 1, 9, 11, 4, 8, 3, 10]

X0 = [0, 1, 0, 0, 1, 1, 0, 0, -1, 1, 0, 1]
K1 = [-1, 2, -1, -1, 2, 2, -1, -1, -4, 2, -1, 2]
K2 = [1, -1, 0, 1, -1, -1, 1, 0, 2, -2, 0, 0]
PAIR_CERT = [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1]

GADGET_ROWS = [
    (2, 5, 6),
    (1, 4, 7),
    (5, 7, 9),
    (0, 3, 7),
    (4, 6, 9),
    (2, 4, 8),
    (3, 8, 9),
    (0, 5, 8),
    (1, 3, 6),
]
TSET = (0, 1, 2, 9)
SSET = (3, 4, 5)
RSET = (6, 7, 8)


def mat_vec(A, x):
    return [sum(a * b for a, b in zip(row, x)) for row in A]


def mat_cols_product(A, K):
    if not K:
        return []
    d = len(K[0])
    return [[sum(A[i][j] * K[j][t] for j in range(len(K))) for t in range(d)]
            for i in range(len(A))]


def build_base():
    n = len(P)
    A = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in (i, P[i], Q[i]):
            A[i][j] += 1
    return A


def determinant_bareiss(M):
    A = [list(map(int, row)) for row in M]
    n = len(A)
    if n == 0:
        return 1
    sign = 1
    prev = 1
    for k in range(n - 1):
        if A[k][k] == 0:
            pivot = next((r for r in range(k + 1, n) if A[r][k] != 0), None)
            if pivot is None:
                return 0
            A[k], A[pivot] = A[pivot], A[k]
            sign *= -1
        pivot = A[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                A[i][j] = (A[i][j] * pivot - A[i][k] * A[k][j]) // prev
        for i in range(k + 1, n):
            A[i][k] = 0
        prev = pivot
    return sign * A[n - 1][n - 1]


def rank_mod_p(M, p):
    A = [[int(x) % p for x in row] for row in M]
    if not A:
        return 0
    m, n = len(A), len(A[0])
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if A[i][c]), None)
        if pivot is None:
            continue
        A[r], A[pivot] = A[pivot], A[r]
        inv = pow(A[r][c], -1, p)
        A[r] = [(v * inv) % p for v in A[r]]
        for i in range(m):
            if i != r and A[i][c]:
                f = A[i][c]
                A[i] = [(A[i][j] - f * A[r][j]) % p for j in range(n)]
        r += 1
        if r == m:
            break
    return r


def connected_bipartite(A):
    m, n = len(A), len(A[0])
    adj = [[] for _ in range(m + n)]
    for i in range(m):
        for j, a in enumerate(A[i]):
            if a:
                adj[i].append(m + j)
                adj[m + j].append(i)
    seen = {0}
    stack = [0]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return len(seen) == m + n


def is_linear(A):
    supports = [{j for j, a in enumerate(row) if a} for row in A]
    return all(len(supports[i] & supports[j]) <= 1
               for i in range(len(A)) for j in range(i + 1, len(A)))


def gcd_list(values):
    g = 0
    for v in values:
        g = gcd(g, abs(int(v)))
    return g


def one_coordinate_extend(row, rhs):
    g = gcd_list(row)
    return rhs == 0 if g == 0 else rhs % g == 0


def two_coordinate_extend(C, rhs):
    """Does C z = rhs have an integer solution for a 2xd integer matrix C?"""
    a, b = map(int, rhs)
    d = len(C[0]) if C else 0
    if d == 0:
        return a == 0 and b == 0
    r1 = list(map(int, C[0]))
    r2 = list(map(int, C[1]))

    # Rank two: gcd of maximal minors is the lattice index in Z^2.
    delta = 0
    for i, j in combinations(range(d), 2):
        delta = gcd(delta, abs(r1[i] * r2[j] - r1[j] * r2[i]))
    if delta:
        augmented_delta = delta
        for i in range(d):
            augmented_delta = gcd(augmented_delta, abs(r1[i] * b - r2[i] * a))
        return augmented_delta == delta

    # Rank zero or one.
    pivot = next((i for i in range(d) if r1[i] or r2[i]), None)
    if pivot is None:
        return a == 0 and b == 0

    c1, c2 = r1[pivot], r2[pivot]
    g0 = gcd(abs(c1), abs(c2))
    p1, p2 = c1 // g0, c2 // g0  # primitive direction
    if p1 * b - p2 * a:
        return False

    if p1:
        if a % p1:
            return False
        target_coeff = a // p1
        if p2 * target_coeff != b:
            return False
    else:
        if b % p2:
            return False
        target_coeff = b // p2

    coeffs = []
    for x, y in zip(r1, r2):
        if p1:
            if x % p1:
                return False
            c = x // p1
            if p2 * c != y:
                return False
        else:
            if y % p2:
                return False
            c = y // p2
        coeffs.append(c)
    step = gcd_list(coeffs)
    return target_coeff == 0 if step == 0 else target_coeff % step == 0


def certificate_is_pairwise_extendable(x0, K, cert):
    n = len(x0)
    d = len(K[0])
    for i in range(n):
        if not one_coordinate_extend(K[i], cert[i] - x0[i]):
            return False, ("unary", i)
    for i, j in combinations(range(n), 2):
        C = [K[i], K[j]]
        rhs = [cert[i] - x0[i], cert[j] - x0[j]]
        if not two_coordinate_extend(C, rhs):
            return False, ("pair", i, j)
    return True, None


def build_linearized(A):
    n = len(A)
    N = 10 * n
    rows = []
    for v in range(n):
        for triple in GADGET_ROWS:
            rows.append(tuple(10 * v + k for k in triple))

    occurrence = [0] * n
    for row in A:
        vars_ = [j for j, a in enumerate(row) if a]
        assert len(vars_) == 3
        new_row = []
        for v in vars_:
            k = occurrence[v]
            assert k < 3
            new_row.append(10 * v + k)
            occurrence[v] += 1
        rows.append(tuple(new_row))
    assert occurrence == [3] * n

    L = [[0] * N for _ in range(N)]
    for i, row in enumerate(rows):
        for j in row:
            L[i][j] = 1
    return L


def local_boolean_models():
    out = []
    for bits in product((0, 1), repeat=10):
        if all(sum(bits[k] for k in row) == 1 for row in GADGET_ROWS):
            out.append(bits)
    return out


def lifted_affine_family():
    n = 12
    d = 2
    N = 120
    Kbase = [[K1[v], K2[v]] for v in range(n)]
    x0L = [0] * N
    KL = [[0] * (d + n) for _ in range(N)]

    for v in range(n):
        q0 = X0[v]
        for k in TSET:
            idx = 10 * v + k
            x0L[idx] = q0
            KL[idx][0] = K1[v]
            KL[idx][1] = K2[v]
        for k in RSET:
            idx = 10 * v + k
            x0L[idx] = 0
            KL[idx][d + v] = 1
        for k in SSET:
            idx = 10 * v + k
            x0L[idx] = 1 - q0
            KL[idx][0] = -K1[v]
            KL[idx][1] = -K2[v]
            KL[idx][d + v] = -1
    return x0L, KL


def proportional_ratios(K):
    ratios = []
    zero_rows = []
    n = len(K)
    d = len(K[0])
    for i in range(n):
        if all(v == 0 for v in K[i]):
            zero_rows.append(i)
    for i in range(n):
        if i in zero_rows:
            continue
        for j in range(i + 1, n):
            if j in zero_rows:
                continue
        
            pivot = next((t for t in range(d) if K[j][t] != 0), None)
            if pivot is None:
                continue
            a, b = K[i][pivot], K[j][pivot]
            if all(K[i][t] * b == K[j][t] * a for t in range(d)):
                ratios.append(Fraction(a, b))
    return zero_rows, ratios


def main():
    A = build_base()
    n = 12

    assert all(a in (0, 1) for row in A for a in row)
    assert {sum(row) for row in A} == {3}
    assert {sum(A[i][j] for i in range(n)) for j in range(n)} == {3}
    assert connected_bipartite(A)

    Kbase = [[K1[i], K2[i]] for i in range(n)]
    assert mat_vec(A, X0) == [1] * n
    assert mat_cols_product(A, Kbase) == [[0, 0] for _ in range(n)]

    rows = list(range(10))
    cols = [0, 1, 2, 3, 4, 5, 6, 7, 8, 10]
    minor = [[A[i][j] for j in cols] for i in rows]
    assert determinant_bareiss(minor) == 4

    sat_gcd = 0
    for i, j in combinations(range(n), 2):
        sat_gcd = gcd(sat_gcd, abs(K1[i] * K2[j] - K1[j] * K2[i]))
    assert sat_gcd == 1

    # Symbolic Boolean contradiction described in the theorem.
    possible_a = [a for a in range(-2, 2) if -a in (0, 1) and 1 + 2 * a in (0, 1)]
    assert possible_a == [0]
    possible_b = [b for b in range(-1, 3) if b in (0, 1) and 1 - 2 * b in (0, 1)]
    assert possible_b == [0]
    assert -1 - 4 * possible_a[0] + 2 * possible_b[0] == -1

    ok, why = certificate_is_pairwise_extendable(X0, Kbase, PAIR_CERT)
    assert ok, why
    assert mat_vec(A, PAIR_CERT) != [1] * n

    L = build_linearized(A)
    N = 120
    assert len(L) == N and len(L[0]) == N
    assert {sum(row) for row in L} == {3}
    assert {sum(L[i][j] for i in range(N)) for j in range(N)} == {3}
    assert connected_bipartite(L)
    assert is_linear(L)

    models = local_boolean_models()
    assert models == [
        (0, 0, 0, 0, 0, 0, 1, 1, 1, 0),
        (0, 0, 0, 1, 1, 1, 0, 0, 0, 0),
        (1, 1, 1, 0, 0, 0, 0, 0, 0, 1),
    ]
    assert all(len({m[k] for k in TSET}) == 1 for m in models)
    assert {m[0] for m in models} == {0, 1}

    x0L, KL = lifted_affine_family()
    assert mat_vec(L, x0L) == [1] * N
    assert mat_cols_product(L, KL) == [[0] * 14 for _ in range(N)]
    assert rank_mod_p(L, 3) == 106
    assert rank_mod_p(KL, 3) == 14

    zeros, ratios = proportional_ratios(KL)
    assert zeros == []
    counts = {Fraction(1, 1): 0, Fraction(-1, 2): 0}
    for r in ratios:
        assert r in counts, ("illegal RKPR ratio", r)
        counts[r] += 1
    assert counts[Fraction(1, 1)] == 288
    assert counts[Fraction(-1, 2)] == 144

    block0 = [0, 0, 0, 1, 1, 1, 1, 1, 1, 0]
    block1 = [1] * 10
    certL = []
    for bit in PAIR_CERT:
        certL.extend(block1 if bit else block0)
    assert len(certL) == N

    ok, why = certificate_is_pairwise_extendable(x0L, KL, certL)
    assert ok, why
    assert mat_vec(L, certL) != [1] * N

    print("R5_E9_POST_SNF_RKPR_PAIR2_LINEAR_CUBIC_COMPLETENESS_FALSIFIER: PASS")
    print({
        "base_n": 12,
        "base_rank_Q": 10,
        "base_nullity_Q": 2,
        "base_integer_lattice_nonempty": True,
        "base_exact_one": "UNSAT_BY_TWO_PARAMETER_CERTIFICATE",
        "base_pair_projection_2CSP": "SAT",
        "linearized_n": 120,
        "linearized_connected_square_cubic_linear": True,
        "linearized_rank_Q": 106,
        "linearized_nullity_Q": 14,
        "linearized_integer_lattice_nonempty": True,
        "linearized_rkpr_zero_rows": 0,
        "linearized_rkpr_ratio_1_pairs": 288,
        "linearized_rkpr_ratio_minus_half_pairs": 144,
        "linearized_pair_projection_2CSP": "SAT",
        "linearized_exact_one": "UNSAT_BY_EQ3_SEMANTIC_TRANSFER",
        "pair2_completeness": "FALSIFIED",
        "P_VS_NP": "OPEN",
    })


if __name__ == "__main__":
    main()
