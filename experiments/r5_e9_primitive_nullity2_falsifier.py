#!/usr/bin/env python3
"""Exact finite falsifier for naive kernel-nullity => block-system claims.

No third-party dependencies are required.  The checker verifies:
- the explicit I+P+Q carrier is cubic and linear;
- exact rational rank 10 / nullity 2;
- exhaustive Exact-One witnesses (one witness);
- transitivity of <p,q>;
- primitivity by exhaustive rejection of every possible nontrivial block
  containing point 0 (sizes 2,3,4,6 in degree 12).

This is a scoped falsifier only.  It says nothing by itself about an
omega(log n) nullity hypothesis.
"""

from collections import deque
from fractions import Fraction
from itertools import combinations, product


P = [9, 4, 6, 1, 10, 8, 7, 2, 0, 5, 11, 3]
Q = [3, 8, 4, 5, 0, 11, 10, 1, 7, 6, 9, 2]
N = 12
EXPECTED_WITNESS = (1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)


def inverse_perm(p):
    inv = [-1] * len(p)
    for i, j in enumerate(p):
        inv[j] = i
    assert sorted(inv) == list(range(len(p)))
    return inv


def build_matrix():
    A = [[0] * N for _ in range(N)]
    for i in range(N):
        A[i][i] = 1
        A[i][P[i]] = 1
        A[i][Q[i]] = 1
    return A


def validate_linear_cubic(A):
    assert sorted(P) == list(range(N))
    assert sorted(Q) == list(range(N))
    assert all(sum(row) == 3 for row in A)
    assert all(sum(A[r][c] for r in range(N)) == 3 for c in range(N))

    seen_pairs = set()
    for i, row in enumerate(A):
        support = [j for j, bit in enumerate(row) if bit]
        assert len(support) == 3
        assert len({i, P[i], Q[i]}) == 3
        assert set(support) == {i, P[i], Q[i]}
        for a, b in combinations(support, 2):
            pair = tuple(sorted((a, b)))
            assert pair not in seen_pairs, (i, pair)
            seen_pairs.add(pair)


def rank_q(M):
    a = [[Fraction(v) for v in row] for row in M]
    rows = len(a)
    cols = len(a[0])
    rank = 0
    for c in range(cols):
        pivot = next((r for r in range(rank, rows) if a[r][c] != 0), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        pv = a[rank][c]
        a[rank] = [v / pv for v in a[rank]]
        for r in range(rows):
            if r != rank and a[r][c] != 0:
                f = a[r][c]
                a[r] = [a[r][j] - f * a[rank][j] for j in range(cols)]
        rank += 1
        if rank == rows:
            break
    return rank


def exact_one(A, x):
    return all(sum(a * b for a, b in zip(row, x)) == 1 for row in A)


def orbit_of_point(start, generators):
    seen = {start}
    dq = deque([start])
    while dq:
        x = dq.popleft()
        for g in generators:
            y = g[x]
            if y not in seen:
                seen.add(y)
                dq.append(y)
    return seen


def image_of_set(S, g):
    return frozenset(g[x] for x in S)


def is_block(candidate, generators):
    """Exact block test by enumerating the orbit of the candidate subset."""
    B = frozenset(candidate)
    seen = {B}
    dq = deque([B])
    while dq:
        S = dq.popleft()
        # A block B requires every group translate to be B or disjoint from B.
        if S != B and (S & B):
            return False
        for g in generators:
            T = image_of_set(S, g)
            if T not in seen:
                seen.add(T)
                dq.append(T)
    return True


def verify_primitive():
    pinv = inverse_perm(P)
    qinv = inverse_perm(Q)
    generators = (P, Q, pinv, qinv)

    orbit = orbit_of_point(0, generators)
    assert len(orbit) == N, orbit

    # In a transitive action, block size divides the degree.  Every block
    # system can be represented by the unique block containing 0.
    candidate_sizes = [d for d in range(2, N) if N % d == 0]
    checked = 0
    surviving = []
    for d in candidate_sizes:
        for rest in combinations(range(1, N), d - 1):
            B = (0,) + rest
            checked += 1
            if is_block(B, generators):
                surviving.append(B)

    assert not surviving, surviving
    return checked


def main():
    A = build_matrix()
    validate_linear_cubic(A)

    rank = rank_q(A)
    nullity = N - rank
    assert rank == 10
    assert nullity == 2

    witnesses = [bits for bits in product((0, 1), repeat=N) if exact_one(A, bits)]
    assert witnesses == [EXPECTED_WITNESS], witnesses

    x = EXPECTED_WITNESS
    w = [3 * bit - 1 for bit in x]
    for i in range(N):
        assert w[i] + w[P[i]] + w[Q[i]] == 0
        assert sorted((w[i], w[P[i]], w[Q[i]])) == [-1, -1, 2]

    checked_blocks = verify_primitive()

    print("PASS: R5_E9_PRIMITIVE_NULLITY2_BLOCK_SYSTEM_FALSIFIER")
    print(f"n={N} rank_Q={rank} nullity_Q={nullity}")
    print(f"Exact-One witnesses={len(witnesses)} selected={[i for i,b in enumerate(x) if b]}")
    print(f"nontrivial candidate blocks rejected={checked_blocks}")
    print("<p,q> is transitive and primitive")
    print("FALSIFIED: nullity_Q(A)>=2 => imprimitive")
    print("NOT FALSIFIED: omega(log n) + extra hypotheses => quotient")
    print("E8_D1=EMPTY; P_VS_NP=OPEN")


if __name__ == "__main__":
    main()
