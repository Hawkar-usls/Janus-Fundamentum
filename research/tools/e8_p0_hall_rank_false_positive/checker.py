#!/usr/bin/env python3
"""Exact regression for the P0 Hall-rank false-positive theorem.

Frozen bounded-occurrence UNSAT formula:
  (x1 v x2) & (x1 v ~x2) & (~x1 v x3) & (~x3 v x4) & (~x3 v ~x4)

The checker builds the v2.8 P0 principal-minor carrier K, verifies the full
clause-transversal coefficient is zero, then exhausts all 31 nonempty clause
subsets and checks

    rank_Q(sum_{C in S} A_C) >= |S| + 1,

where A_C = K D_C and D_C projects onto occurrence columns of clause C.
"""

from fractions import Fraction
from itertools import combinations, product


def rank_q(A):
    if not A:
        return 0
    M = [[Fraction(x) for x in row] for row in A]
    m, n = len(M), len(M[0])
    r = 0
    for c in range(n):
        p = next((i for i in range(r, m) if M[i][c] != 0), None)
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        pivot = M[r][c]
        M[r] = [x / pivot for x in M[r]]
        for i in range(m):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [M[i][j] - f * M[r][j] for j in range(n)]
        r += 1
        if r == m:
            break
    return r


def det_int(A):
    n = len(A)
    if n == 0:
        return 1
    M = [list(map(int, row)) for row in A]
    sign = 1
    prev = 1
    for k in range(n - 1):
        p = next((i for i in range(k, n) if M[i][k] != 0), None)
        if p is None:
            return 0
        if p != k:
            M[k], M[p] = M[p], M[k]
            sign *= -1
        pivot = M[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                num = M[i][j] * pivot - M[i][k] * M[k][j]
                assert num % prev == 0
                M[i][j] = num // prev
        prev = pivot
        for i in range(k + 1, n):
            M[i][k] = 0
    return sign * M[n - 1][n - 1]


def principal_minor(K, S):
    ids = sorted(S)
    return det_int([[K[i][j] for j in ids] for i in ids])


def sat_bruteforce(formula):
    n = max(abs(lit) for C in formula for lit in C)
    for bits in product((False, True), repeat=n):
        if all(any(bits[abs(lit)-1] if lit > 0 else not bits[abs(lit)-1]
                   for lit in C) for C in formula):
            return True
    return False


def build_carrier(formula):
    occ = []
    clause_occ = []
    by_var = {}
    for ci, C in enumerate(formula):
        ids = []
        for pi, lit in enumerate(C):
            oid = len(occ)
            occ.append((ci, pi, lit))
            ids.append(oid)
            by_var.setdefault(abs(lit), []).append((oid, 1 if lit > 0 else -1))
        clause_occ.append(tuple(ids))

    q = len(occ)
    K = [[0] * q for _ in range(q)]

    for entries in by_var.values():
        ids = [oid for oid, _ in entries]
        signs = [s for _, s in entries]
        d = len(entries)
        assert d <= 3

        if len(set(signs)) == 1:
            for oid in ids:
                K[oid][oid] = 1
            continue

        if d == 2:
            a, b = ids
            K[a][a] = K[a][b] = K[b][a] = K[b][b] = 1
            continue

        assert d == 3
        plus = [oid for oid, s in entries if s == 1]
        minus = [oid for oid, s in entries if s == -1]
        majority = plus if len(plus) == 2 else minus
        minority = minus[0] if len(minus) == 1 else plus[0]
        L, R = majority
        M = minority
        order = (L, M, R)
        block = [
            [1, 1, -1],
            [1, 1, -1],
            [0, -1, 1],
        ]
        for i, oi in enumerate(order):
            for j, oj in enumerate(order):
                K[oi][oj] = block[i][j]

    return occ, clause_occ, K


def transversal_weight(formula, clause_occ, K):
    total = 0
    for choice in product(*clause_occ):
        total += principal_minor(K, frozenset(choice))
    return total


def clause_aggregate(K, clause_occ, chosen_clauses):
    q = len(K)
    cols = set()
    for ci in chosen_clauses:
        cols.update(clause_occ[ci])
    # sum A_C = K * sum D_C; D_C have disjoint clause-occurrence supports.
    return [[K[i][j] if j in cols else 0 for j in range(q)] for i in range(q)]


def main():
    formula = (
        (1, 2),
        (1, -2),
        (-1, 3),
        (-3, 4),
        (-3, -4),
    )

    assert not sat_bruteforce(formula)
    occ, clause_occ, K = build_carrier(formula)
    assert len(occ) == 10
    assert len(clause_occ) == 5

    W = transversal_weight(formula, clause_occ, K)
    assert W == 0

    census = {}
    checked = 0
    for s in range(1, len(clause_occ) + 1):
        ranks = []
        for S in combinations(range(len(clause_occ)), s):
            r = rank_q(clause_aggregate(K, clause_occ, S))
            assert r >= s + 1, (S, r, s)
            ranks.append(r)
            checked += 1
        census[s] = (len(ranks), min(ranks), max(ranks))

    assert checked == 31
    assert census == {
        1: (5, 2, 2),
        2: (10, 3, 4),
        3: (10, 4, 6),
        4: (5, 5, 6),
        5: (1, 6, 6),
    }

    print("PASS_P0_HALL_RANK_CRITERION_FALSE_POSITIVE")
    print("frozen_formula_unsat=True")
    print("target_coefficient_W=0")
    print("nonempty_clause_subsets_checked=31")
    for s in sorted(census):
        count, rmin, rmax = census[s]
        print(f"subset_size={s} count={count} min_rank={rmin} max_rank={rmax}")
    print("all_subset_rank_inequalities=rank>=|S|+1")
    print("PSD_HALL_STYLE_EXTENSION_TO_THIS_P0_CLASS=FALSE")
    print("E8_D1=EMPTY P_VS_NP=OPEN")


if __name__ == "__main__":
    main()
