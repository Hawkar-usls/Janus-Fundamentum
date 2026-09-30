#!/usr/bin/env python3
"""Exact regression for the P0 principal-transversal coefficient carrier.

The companion theorem is symbolic.  This checker verifies:
  * every local block has exactly the claimed 0/1 principal-minor support;
  * the global block-diagonal determinant is 1 exactly for sign-consistent sets;
  * the full-clause transversal coefficient equals the number of sign-consistent
    one-occurrence-per-clause witnesses and is positive iff SAT;
  * clause aggregate rank never exceeds clause size (hence <=3);
  * the rank-one aggregate coefficient terminal on exact finite controls.
"""

from fractions import Fraction
from itertools import combinations, combinations_with_replacement, product


def det_int(A):
    n = len(A)
    if n == 0:
        return 1
    M = [list(map(int, row)) for row in A]
    sign = 1
    prev = 1
    for k in range(n - 1):
        pivot = next((r for r in range(k, n) if M[r][k] != 0), None)
        if pivot is None:
            return 0
        if pivot != k:
            M[k], M[pivot] = M[pivot], M[k]
            sign *= -1
        p = M[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                num = M[i][j] * p - M[i][k] * M[k][j]
                assert num % prev == 0
                M[i][j] = num // prev
        prev = p
        for i in range(k + 1, n):
            M[i][k] = 0
    return sign * M[n - 1][n - 1]


def rank_q(A):
    if not A:
        return 0
    M = [[Fraction(x) for x in row] for row in A]
    m, n = len(M), len(M[0])
    r = 0
    for c in range(n):
        p = next((i for i in range(r, m) if M[i][c]), None)
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        q = M[r][c]
        M[r] = [x / q for x in M[r]]
        for i in range(m):
            if i != r and M[i][c]:
                q = M[i][c]
                M[i] = [M[i][j] - q * M[r][j] for j in range(n)]
        r += 1
        if r == m:
            break
    return r


def principal_minor(K, S):
    ids = sorted(S)
    return det_int([[K[i][j] for j in ids] for i in ids])


def powerset(ids):
    ids = tuple(ids)
    for mask in range(1 << len(ids)):
        yield frozenset(ids[i] for i in range(len(ids)) if mask >> i & 1)


def local_checks():
    K3 = [
        [1, 1, -1],
        [1, 1, -1],
        [0, -1, 1],
    ]
    support3 = {
        frozenset(), frozenset({0}), frozenset({1}), frozenset({2}),
        frozenset({0, 2}),
    }
    for S in powerset(range(3)):
        d = principal_minor(K3, S)
        assert d in (0, 1)
        assert (d == 1) == (S in support3), (S, d)

    K2 = [[1, 1], [1, 1]]
    support2 = {frozenset(), frozenset({0}), frozenset({1})}
    for S in powerset(range(2)):
        d = principal_minor(K2, S)
        assert d in (0, 1)
        assert (d == 1) == (S in support2), (S, d)

    for d in (1, 2, 3):
        I = [[int(i == j) for j in range(d)] for i in range(d)]
        assert all(principal_minor(I, S) == 1 for S in powerset(range(d)))

    return 8 + 4 + (2 + 4 + 8)


def build_occurrence_matrix(formula):
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
        signs = [sgn for _, sgn in entries]
        d = len(entries)
        assert d <= 3

        if len(set(signs)) == 1:
            for oid in ids:
                K[oid][oid] = 1
            continue

        if d == 2:
            a, b = ids
            for i, oi in enumerate((a, b)):
                for j, oj in enumerate((a, b)):
                    K[oi][oj] = 1
            continue

        assert d == 3
        plus = [oid for oid, s in entries if s == 1]
        minus = [oid for oid, s in entries if s == -1]
        majority = plus if len(plus) == 2 else minus
        minority = minus[0] if len(minus) == 1 else plus[0]
        L, R = majority
        M = minority
        order = (L, M, R)
        B = [[1, 1, -1], [1, 1, -1], [0, -1, 1]]
        for i, oi in enumerate(order):
            for j, oj in enumerate(order):
                K[oi][oj] = B[i][j]

    return occ, clause_occ, by_var, K


def sign_consistent(S, occ):
    used = {}
    for oid in S:
        lit = occ[oid][2]
        used.setdefault(abs(lit), set()).add(1 if lit > 0 else -1)
    return all(len(v) <= 1 for v in used.values())


def verify_global_support(formula):
    occ, clause_occ, by_var, K = build_occurrence_matrix(formula)
    q = len(occ)
    if q <= 12:
        for S in powerset(range(q)):
            d = principal_minor(K, S)
            assert d in (0, 1)
            assert (d == 1) == sign_consistent(S, occ), (formula, S, d)

    # A_C = K D_C has only columns in C, so rank <= |C|. Check exactly.
    for ids in clause_occ:
        cols = set(ids)
        A = [[K[i][j] if j in cols else 0 for j in range(q)] for i in range(q)]
        assert rank_q(A) <= len(ids) <= 3

    return occ, clause_occ, K


def sat_bruteforce(formula):
    n = max((abs(lit) for C in formula for lit in C), default=0)
    for bits in product((False, True), repeat=n):
        if all(any((bits[abs(lit)-1] if lit > 0 else not bits[abs(lit)-1]) for lit in C)
               for C in formula):
            return True
    return False


def transversal_weight(formula):
    occ, clause_occ, K = verify_global_support(formula)
    total = 0
    for choice in product(*clause_occ):
        S = frozenset(choice)
        assert len(S) == len(formula)
        total += principal_minor(K, S)
    return total


def clause_catalog():
    out = []
    for k in (2, 3):
        for support in combinations((1, 2, 3), k):
            for signs in product((1, -1), repeat=k):
                out.append(tuple(s * v for s, v in zip(signs, support)))
    return out


def occ_ok(formula):
    count = {}
    for C in formula:
        for lit in C:
            count[abs(lit)] = count.get(abs(lit), 0) + 1
    return all(v <= 3 for v in count.values())


def small_formula_regression():
    clauses = clause_catalog()
    tested = satn = unsatn = 0
    weight_sum = 0
    for m in (1, 2, 3):
        for idxs in combinations_with_replacement(range(len(clauses)), m):
            F = tuple(clauses[i] for i in idxs)
            if not occ_ok(F):
                continue
            sat = sat_bruteforce(F)
            W = transversal_weight(F)
            assert (W > 0) == sat, (F, W, sat)
            tested += 1
            satn += int(sat)
            unsatn += int(not sat)
            weight_sum += W
    return tested, satn, unsatn, weight_sum


def frozen_controls():
    unsat = (
        (1, 2),
        (1, -2),
        (-1, 3),
        (-3, 4),
        (-3, -4),
    )
    sat = (
        (1, 2),
        (-1, 3),
        (-2, 4),
        (-3, -4),
    )
    assert occ_ok(unsat) and occ_ok(sat)
    Wu = transversal_weight(unsat)
    Ws = transversal_weight(sat)
    assert Wu == 0 and Ws > 0
    assert not sat_bruteforce(unsat) and sat_bruteforce(sat)
    return Wu, Ws


def rank1_terminal_regression():
    # For A_i=u_i v_i^T, [z1...zm] det(I+sum z_i A_i)=det(V^T U).
    # Verify on explicit integer controls by direct principal-transversal expansion.
    controls = [
        (
            [[1, 0], [0, 1]],
            [[1, 1], [1, -1]],
        ),
        (
            [[1, 2, 0], [0, 1, 1], [1, 0, 1]],
            [[2, 0, 1], [1, 1, 0], [0, 1, 1]],
        ),
    ]
    checked = 0
    for U, V in controls:
        # U,V are ambient_dim x m; coefficient is det(V^T U).
        ambient = len(U)
        m = len(U[0])
        VTU = [[sum(V[r][i] * U[r][j] for r in range(ambient)) for j in range(m)] for i in range(m)]
        rhs = det_int(VTU)

        # Direct multilinear coefficient: sum over permutations sigma of columns,
        # product_i v_i[row?] formulation is exactly det(V^T U); use determinant
        # of symbolic rank-one update evaluated by finite differences at {0,1}^m.
        coeff = 0
        for mask in range(1 << m):
            z = [(mask >> i) & 1 for i in range(m)]
            M = [[int(i == j) for j in range(ambient)] for i in range(ambient)]
            for c in range(m):
                if z[c]:
                    for i in range(ambient):
                        for j in range(ambient):
                            M[i][j] += U[i][c] * V[j][c]
            # Möbius extraction of full multilinear coefficient.
            coeff += ((-1) ** (m - sum(z))) * det_int(M)
        assert coeff == rhs, (coeff, rhs)
        checked += 1
    return checked


def main():
    local = local_checks()
    tested, satn, unsatn, weight_sum = small_formula_regression()
    Wu, Ws = frozen_controls()
    r1 = rank1_terminal_regression()

    print("PASS_P0_PRINCIPAL_TRANSVERSAL_COEFFICIENT_CARRIER")
    print(f"local_principal_minors_checked={local}")
    print(f"small_formulas_tested={tested}")
    print(f"small_sat={satn} small_unsat={unsatn}")
    print(f"aggregate_witness_weight={weight_sum}")
    print(f"frozen_unsat_weight={Wu} frozen_sat_weight={Ws}")
    print(f"rank1_terminal_controls={r1}")
    print("all_local_and_global_principal_minors=0_OR_1")
    print("clause_aggregate_rank<=3")
    print("E8_D1=EMPTY P_VS_NP=OPEN")


if __name__ == "__main__":
    main()
