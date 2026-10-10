#!/usr/bin/env python3
"""Exact finite regression for the binary-kernel signature / series theorem.

This checker is deliberately stdlib-only.  It verifies two frozen PG(3,2)-built
15_3 controls, one SAT and one UNSAT.  The companion research note contains the
arbitrary-n proof.  Finite regression is not promoted to a P-vs-NP claim.
"""
from fractions import Fraction
from itertools import combinations
import json


def incidence_from_lines(lines):
    n = 15
    A = [[0] * n for _ in range(n)]
    for r, line in enumerate(lines):
        for p in line:
            A[r][p - 1] = 1
    return A


def rational_rank(A):
    M = [[Fraction(v) for v in row] for row in A]
    m = len(M)
    n = len(M[0]) if m else 0
    r = 0
    for c in range(n):
        piv = next((i for i in range(r, m) if M[i][c]), None)
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
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


def row_bits(A):
    out = []
    for row in A:
        x = 0
        for j, v in enumerate(row):
            if v:
                x |= 1 << j
        out.append(x)
    return out


def col_bits(A):
    m = len(A)
    n = len(A[0])
    out = []
    for j in range(n):
        x = 0
        for i in range(m):
            if A[i][j]:
                x |= 1 << i
        out.append(x)
    return out


def gf2_rank(vecs):
    basis = {}
    for x0 in vecs:
        x = x0
        while x:
            p = x.bit_length() - 1
            if p in basis:
                x ^= basis[p]
            else:
                basis[p] = x
                break
    return len(basis)


def gf2_nullspace_basis(A):
    rows = row_bits(A)
    m = len(rows)
    n = len(A[0])
    rows = rows[:]
    pivot_cols = []
    r = 0
    for c in range(n):
        piv = next((i for i in range(r, m) if (rows[i] >> c) & 1), None)
        if piv is None:
            continue
        rows[r], rows[piv] = rows[piv], rows[r]
        for i in range(m):
            if i != r and ((rows[i] >> c) & 1):
                rows[i] ^= rows[r]
        pivot_cols.append(c)
        r += 1
        if r == m:
            break
    pivset = set(pivot_cols)
    free = [c for c in range(n) if c not in pivset]
    basis = []
    for f in free:
        x = 1 << f
        for i, p in enumerate(pivot_cols):
            # RREF equation: x_p + sum_free row[f]*x_f = 0.
            if ((rows[i] & x).bit_count() & 1):
                x |= 1 << p
        # verify
        assert all(((rb & x).bit_count() & 1) == 0 for rb in row_bits(A))
        basis.append(x)
    return basis


def kernel_signatures(A):
    basis = gf2_nullspace_basis(A)
    n = len(A[0])
    sig = []
    for j in range(n):
        s = 0
        for q, z in enumerate(basis):
            if (z >> j) & 1:
                s |= 1 << q
        sig.append(s)
    return basis, sig


def is_two_cocircuit(cols, a, b):
    r = gf2_rank(cols)
    without_pair = [v for i, v in enumerate(cols) if i not in {a, b}]
    if gf2_rank(without_pair) != r - 1:
        return False
    for e in (a, b):
        without_one = [v for i, v in enumerate(cols) if i != e]
        if gf2_rank(without_one) != r:
            return False
    return True


def direct_series_pairs(A):
    n = len(A)
    cols = col_bits(A) + [(1 << n) - 1]
    return {
        (a, b)
        for a, b in combinations(range(n + 1), 2)
        if is_two_cocircuit(cols, a, b)
    }


def predicted_series_pairs(A):
    basis, sig = kernel_signatures(A)
    n = len(sig)
    root = n
    ans = set()
    for i, j in combinations(range(n), 2):
        if sig[i] == sig[j]:
            ans.add((i, j))
    for j in range(n):
        if sig[j] == 0:
            ans.add((j, root))
    return basis, sig, ans


def row_supports(A):
    return [tuple(j for j, v in enumerate(row) if v) for row in A]


def exactone_witnesses(A):
    n = len(A)
    if n % 3:
        return []
    out = []
    for C in combinations(range(n), n // 3):
        if all(sum(A[i][j] for j in C) == 1 for i in range(n)):
            out.append(C)
    return out


def projective_parameter_witnesses(A, sig, k):
    rows = row_supports(A)
    good = []
    for t in range(1 << k):
        ok = True
        for a, b, c in rows:
            za = (sig[a] & t).bit_count() & 1
            zb = (sig[b] & t).bit_count() & 1
            zc = (sig[c] & t).bit_count() & 1
            assert za ^ zb ^ zc == 0
            if (za, zb, zc) == (0, 0, 0):
                ok = False
                break
        if ok:
            x = tuple(j for j, s in enumerate(sig) if ((s & t).bit_count() & 1) == 0)
            good.append((t, x))
    return good


def validate_source(A):
    n = len(A)
    assert n == len(A[0])
    assert all(sum(row) == 3 for row in A)
    assert all(sum(A[i][j] for i in range(n)) == 3 for j in range(n))
    supports = row_supports(A)
    for R, S in combinations(supports, 2):
        assert len(set(R) & set(S)) <= 1


def run_control(name, lines, expected_q_rank, expected_f2_rank, expected_witnesses):
    A = incidence_from_lines(lines)
    validate_source(A)

    rq = rational_rank(A)
    cols = col_bits(A)
    r2 = gf2_rank(cols)
    basis, sig, predicted = predicted_series_pairs(A)
    direct = direct_series_pairs(A)
    assert direct == predicted

    # These frozen controls are series-irreducible.
    assert direct == set()
    assert len(set(sig)) == 15
    assert all(s != 0 for s in sig)

    # Every source row is a projective line in signature space.
    for a, b, c in row_supports(A):
        assert sig[a] ^ sig[b] ^ sig[c] == 0
        assert len({sig[a], sig[b], sig[c]}) == 3

    direct_models = exactone_witnesses(A)
    param_models = projective_parameter_witnesses(A, sig, len(basis))
    param_supports = sorted({x for _, x in param_models})
    assert sorted(direct_models) == param_supports

    assert rq == expected_q_rank
    assert r2 == expected_f2_rank
    assert sorted(direct_models) == sorted(expected_witnesses)

    return {
        "name": name,
        "rank_Q": rq,
        "rank_F2": r2,
        "kernel_dimension_F2": len(basis),
        "series_pairs": 0,
        "distinct_nonzero_signatures": len(set(sig)),
        "exactone_witness_count": len(direct_models),
        "exactone_witnesses_1based": [
            [j + 1 for j in C] for C in direct_models
        ],
        "projective_parameter_count": len(param_models),
    }


UNSAT_LINES = [
    (1,10,11),(1,12,13),(1,14,15),(2,4,6),(2,5,7),
    (2,12,14),(3,4,7),(3,8,11),(3,9,10),(4,11,15),
    (5,8,13),(5,9,12),(6,8,14),(6,9,15),(7,10,13),
]

SAT_LINES = [
    (1,2,3),(1,10,11),(1,12,13),(2,9,11),(2,12,14),
    (3,4,7),(3,5,6),(4,9,13),(4,10,14),(5,8,13),
    (5,10,15),(6,8,14),(6,9,15),(7,8,15),(7,11,12),
]


def main():
    unsat = run_control(
        "PG15_UNSAT_R13",
        UNSAT_LINES,
        expected_q_rank=13,
        expected_f2_rank=11,
        expected_witnesses=[],
    )
    sat = run_control(
        "PG15_SAT_R11",
        SAT_LINES,
        expected_q_rank=11,
        expected_f2_rank=10,
        expected_witnesses=[(0,4,6,8,13)],
    )
    print(json.dumps({
        "status": "PASS_BINARY_KERNEL_SIGNATURE_SERIES_PROJECTIVE_AVOIDANCE",
        "scientific_ceiling": "FINITE_REGRESSION_ONLY__ARBITRARY_N_PROOF_IN_COMPANION_NOTE__NO_D1_PROMOTION__P_VS_NP_OPEN",
        "controls": [unsat, sat],
        "conclusion": "series classes equal kernel-signature classes on controls; projective hyperplane-avoidance parameterization is exact",
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
