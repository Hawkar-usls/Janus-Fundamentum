#!/usr/bin/env python3
"""R5 E10Q exact checker: rational-kernel terminal and source-face controls.

Claims checked with exact arithmetic:
  * square linear-cubic incidence invariants;
  * A SAT iff ker_Q(A) intersects {-1,2}^n, with witness map y=3x-1;
  * PG15 SAT has rank_Q=11, nullity_Q=4 and exactly four alphabet-kernel words;
  * canonical hostile PG15 UNSAT has rank_Q=13, nullity_Q=2,
    nullity_F2=4, alpha=4, no alphabet-kernel word, three-spread
    projective geometry and 3-lines-per-hyperplane invariants;
  * the source-face identity on finite controls:
        STAB(G_A) cap {z: A z = 1}
      has vertices exactly the Exact-One witnesses;
  * connected witness-preserving linear 2-switch chains of k PG15 SAT
    blocks have nullity_Q = 3k+1 for k=1..6, disproving any
    "connected => logarithmic nullity" route.

No P=NP claim is made.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations, product
import json


SAT_ROWS = [
    (1, 2, 3), (1, 10, 11), (1, 12, 13), (2, 9, 11), (2, 12, 14),
    (3, 4, 7), (3, 5, 6), (4, 9, 13), (4, 10, 14), (5, 8, 13),
    (5, 10, 15), (6, 8, 14), (6, 9, 15), (7, 8, 15), (7, 11, 12),
]

# Canonical representative of the reconstructed hostile PG(3,2) orbit.
HOSTILE_ROWS = [
    (1, 2, 3), (1, 4, 5), (1, 6, 7), (2, 8, 10), (2, 12, 14),
    (3, 9, 10), (3, 13, 14), (4, 8, 12), (4, 11, 15), (5, 8, 13),
    (5, 10, 15), (6, 9, 15), (6, 11, 13), (7, 9, 14), (7, 11, 12),
]

SAT_WITNESS = {3, 11, 13, 14, 15}


def matrix_from_rows(rows, n=15):
    return [[int(j + 1 in row) for j in range(n)] for row in rows]


def matvec(A, x):
    return [sum(a * b for a, b in zip(row, x)) for row in A]


def rref_q(A):
    M = [[Fraction(x) for x in row] for row in A]
    m, n = len(M), len(M[0])
    pivots = []
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if M[i][c]), None)
        if pivot is None:
            continue
        M[r], M[pivot] = M[pivot], M[r]
        q = M[r][c]
        M[r] = [x / q for x in M[r]]
        for i in range(m):
            if i != r and M[i][c]:
                q = M[i][c]
                M[i] = [M[i][j] - q * M[r][j] for j in range(n)]
        pivots.append(c)
        r += 1
        if r == m:
            break
    return M, pivots


def null_basis_q(A):
    R, pivots = rref_q(A)
    n = len(A[0])
    free = [j for j in range(n) if j not in pivots]
    basis = []
    for f in free:
        v = [Fraction(0) for _ in range(n)]
        v[f] = Fraction(1)
        for i, p in enumerate(pivots):
            v[p] = -R[i][f]
        basis.append(v)
    return basis, pivots, free


def rank_mod2(A):
    M = [[x & 1 for x in row] for row in A]
    m, n = len(M), len(M[0])
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if M[i][c]), None)
        if pivot is None:
            continue
        M[r], M[pivot] = M[pivot], M[r]
        for i in range(m):
            if i != r and M[i][c]:
                M[i] = [a ^ b for a, b in zip(M[i], M[r])]
        r += 1
        if r == m:
            break
    return r


def kernel_alphabet_words(A):
    basis, _, free = null_basis_q(A)
    out = []
    for values in product((-1, 2), repeat=len(basis)):
        y = [
            sum(Fraction(values[k]) * basis[k][i] for k in range(len(basis)))
            for i in range(len(A[0]))
        ]
        if all(v in (Fraction(-1), Fraction(2)) for v in y):
            out.append(tuple(int(v) for v in y))
    return out, free


def decode_y(y):
    return tuple((v + 1) // 3 for v in y)


def exactone_witnesses(A):
    n = len(A[0])
    out = []
    for bits in product((0, 1), repeat=n):
        if matvec(A, bits) == [1] * len(A):
            out.append(bits)
    return out


def linear_cubic_check(A):
    m, n = len(A), len(A[0])
    assert m == n
    assert all(sum(row) == 3 for row in A)
    assert all(sum(A[i][j] for i in range(m)) == 3 for j in range(n))
    supports = [
        {i for i in range(m) if A[i][j]}
        for j in range(n)
    ]
    assert all(
        len(supports[a] & supports[b]) <= 1
        for a, b in combinations(range(n), 2)
    )


def graph_from_A(A):
    n = len(A[0])
    adj = [set() for _ in range(n)]
    for row in A:
        cols = [j for j, x in enumerate(row) if x]
        for a, b in combinations(cols, 2):
            adj[a].add(b)
            adj[b].add(a)
    return adj


def is_stable(adj, mask):
    n = len(adj)
    for v in range(n):
        if (mask >> v) & 1:
            if any(((mask >> u) & 1) for u in adj[v] if u > v):
                return False
    return True


def stable_stats(A):
    adj = graph_from_A(A)
    n = len(adj)
    alpha = 0
    exact_stable = []
    for mask in range(1 << n):
        if not is_stable(adj, mask):
            continue
        size = mask.bit_count()
        alpha = max(alpha, size)
        x = tuple((mask >> j) & 1 for j in range(n))
        # Every stable set meets each source row in at most one column.
        assert all(v in (0, 1) for v in matvec(A, x))
        if matvec(A, x) == [1] * len(A):
            exact_stable.append(x)
    return alpha, exact_stable


def f2_dot(a, b):
    return ((a & b).bit_count()) & 1


def projective_hostile_checks(rows):
    # Points are nonzero 4-bit vectors 1..15. In PG(3,2), the line
    # through a,b is {a,b,a xor b}; HOSTILE_ROWS use exactly this coding.
    for row in rows:
        a, b, c = row
        assert a ^ b == c or a ^ c == b or b ^ c == a

    selected = [frozenset(r) for r in rows]

    # Every hyperplane h*x=0, h !=0, contains exactly three selected lines.
    hp_counts = []
    for h in range(1, 16):
        count = 0
        for L in selected:
            if all(f2_dot(h, p) == 0 for p in L):
                count += 1
        hp_counts.append(count)
    assert hp_counts == [3] * 15

    # Enumerate spreads among the 15 selected lines and verify a partition
    # of them into three disjoint spreads of five.
    spreads = []
    for inds in combinations(range(15), 5):
        union = set()
        ok = True
        for i in inds:
            if union & set(selected[i]):
                ok = False
                break
            union |= set(selected[i])
        if ok and len(union) == 15:
            spreads.append(frozenset(inds))

    partition = None
    all_idx = frozenset(range(15))
    for a_i in range(len(spreads)):
        A = spreads[a_i]
        for b_i in range(a_i + 1, len(spreads)):
            B = spreads[b_i]
            if A & B:
                continue
            C = all_idx - A - B
            if C in spreads:
                partition = (sorted(A), sorted(B), sorted(C))
                break
        if partition:
            break
    assert partition is not None
    return len(spreads), partition


def block_diag(base, k):
    n = len(base)
    A = [[0] * (n * k) for _ in range(n * k)]
    for b in range(k):
        for i in range(n):
            for j in range(n):
                A[b * n + i][b * n + j] = base[i][j]
    return A


def two_switch(A, r1, c1, r2, c2):
    assert A[r1][c1] == A[r2][c2] == 1
    assert A[r1][c2] == A[r2][c1] == 0
    A[r1][c1] = 0
    A[r2][c2] = 0
    A[r1][c2] = 1
    A[r2][c1] = 1


def support_connected(A):
    m, n = len(A), len(A[0])
    adj = [[] for _ in range(m + n)]
    for i in range(m):
        for j in range(n):
            if A[i][j]:
                adj[i].append(m + j)
                adj[m + j].append(i)
    seen = {0}
    stack = [0]
    while stack:
        v = stack.pop()
        for u in adj[v]:
            if u not in seen:
                seen.add(u)
                stack.append(u)
    return len(seen) == m + n


def switch_chain(k):
    base = matrix_from_rows(SAT_ROWS)
    n = 15
    A = block_diag(base, k)
    x = [0] * (n * k)
    for b in range(k):
        for c in SAT_WITNESS:
            x[b * n + c - 1] = 1

    # For each adjacent pair of blocks use selected ports:
    # right block-b port (row 2, column 11),
    # left block-(b+1) port (row 1, column 3).
    for b in range(k - 1):
        r1, c1 = b * n + 1, b * n + 10
        r2, c2 = (b + 1) * n + 0, (b + 1) * n + 2
        two_switch(A, r1, c1, r2, c2)

    linear_cubic_check(A)
    assert support_connected(A)
    assert matvec(A, x) == [1] * len(A)
    rank = len(rref_q(A)[1])
    return len(A) - rank


def main():
    A_sat = matrix_from_rows(SAT_ROWS)
    A_unsat = matrix_from_rows(HOSTILE_ROWS)
    linear_cubic_check(A_sat)
    linear_cubic_check(A_unsat)

    sat_basis, sat_piv, sat_free = null_basis_q(A_sat)
    uns_basis, uns_piv, uns_free = null_basis_q(A_unsat)

    assert len(sat_piv) == 11
    assert len(sat_basis) == 4
    assert len(uns_piv) == 13
    assert len(uns_basis) == 2
    assert 15 - rank_mod2(A_unsat) == 4

    sat_words, sat_enum_free = kernel_alphabet_words(A_sat)
    uns_words, uns_enum_free = kernel_alphabet_words(A_unsat)
    assert len(sat_words) == 4
    assert len(uns_words) == 0

    sat_decoded = [decode_y(y) for y in sat_words]
    assert all(matvec(A_sat, x) == [1] * 15 for x in sat_decoded)

    sat_exact = exactone_witnesses(A_sat)
    uns_exact = exactone_witnesses(A_unsat)
    assert set(sat_decoded) == set(sat_exact)
    assert len(sat_exact) == 4
    assert len(uns_exact) == 0

    sat_alpha, sat_face_vertices = stable_stats(A_sat)
    uns_alpha, uns_face_vertices = stable_stats(A_unsat)
    assert sat_alpha == 5
    assert uns_alpha == 4
    assert set(sat_face_vertices) == set(sat_exact)
    assert uns_face_vertices == []

    spread_count, spread_partition = projective_hostile_checks(HOSTILE_ROWS)

    chain = {}
    for k in range(1, 7):
        d = switch_chain(k)
        assert d == 3 * k + 1
        chain[k] = d

    report = {
        "status": "PASS",
        "claim_ceiling": "P_VS_NP_OPEN",
        "rational_kernel_theorem": "SAT iff ker_Q(A) intersects {-1,2}^n",
        "algorithm": "O(2^d poly(n)), d=nullity_Q(A)",
        "PG15_SAT": {
            "rank_Q": 11,
            "nullity_Q": 4,
            "alpha": sat_alpha,
            "alphabet_kernel_words": len(sat_words),
            "exactone_witnesses": len(sat_exact),
            "free_coordinates_1based": [i + 1 for i in sat_enum_free],
        },
        "PG15_HOSTILE_UNSAT": {
            "rank_Q": 13,
            "nullity_Q": 2,
            "nullity_F2": 4,
            "alpha": uns_alpha,
            "alphabet_kernel_words": 0,
            "exactone_witnesses": 0,
            "free_coordinates_1based": [i + 1 for i in uns_enum_free],
            "selected_spreads_inside_canonical_rep": spread_count,
            "one_three_spread_partition_line_indices_1based": [
                [i + 1 for i in part] for part in spread_partition
            ],
            "hyperplane_selected_line_counts": [3] * 15,
        },
        "source_face_control": {
            "SAT_face_vertices": len(sat_face_vertices),
            "UNSAT_face_vertices": len(uns_face_vertices),
        },
        "connected_switch_chain_nullity_Q": chain,
        "negative_result": (
            "connected square linear-cubic SAT sources can have nullity_Q linear in n"
        ),
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
