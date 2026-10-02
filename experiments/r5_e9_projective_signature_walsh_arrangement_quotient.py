#!/usr/bin/env python3
"""Finite regression for the exact projective-signature Walsh quotient.

The arbitrary-n proof is in the companion theorem. This file only replays the
frozen SAT/UNSAT controls and must never be promoted as a universal proof.
"""
from collections import Counter
from itertools import combinations
import json

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


def incidence(lines):
    n = len(lines)
    A = [[0] * n for _ in range(n)]
    for i, L in enumerate(lines):
        for p in L:
            A[i][p - 1] = 1
    return A


def row_bits(A):
    return [sum(v << j for j, v in enumerate(row)) for row in A]


def gf2_nullspace(A):
    rows = row_bits(A)[:]
    m, n = len(rows), len(A[0])
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
    free = [c for c in range(n) if c not in set(pivots)]
    basis = []
    for f in free:
        x = 1 << f
        for i, p in enumerate(pivots):
            if (rows[i] & x).bit_count() & 1:
                x |= 1 << p
        assert all(((rb & x).bit_count() & 1) == 0 for rb in row_bits(A))
        basis.append(x)
    return r, basis


def signatures(A):
    rank, basis = gf2_nullspace(A)
    n = len(A[0])
    S = []
    for j in range(n):
        s = 0
        for q, z in enumerate(basis):
            s |= (((z >> j) & 1) << q)
        S.append(s)
    return rank, basis, S


def direct_exactone(A):
    n = len(A)
    if n % 3:
        return []
    out = []
    for C in combinations(range(n), n // 3):
        if all(sum(A[i][j] for j in C) == 1 for i in range(n)):
            out.append(C)
    return out


def run(name, lines, expect_sat, expect_rank):
    A = incidence(lines)
    n = len(A)
    assert all(sum(row) == 3 for row in A)
    assert all(sum(A[i][j] for i in range(n)) == 3 for j in range(n))

    rank, basis, S = signatures(A)
    k = len(basis)
    assert rank == expect_rank
    assert len(set(S)) == n
    assert all(S)

    row_supports = [tuple(p - 1 for p in L) for L in lines]
    for a, b, c in row_supports:
        assert S[a] ^ S[b] ^ S[c] == 0

    qs = []
    ws = []
    for t in range(1 << k):
        w = sum(((s & t).bit_count() & 1) for s in S)
        q_direct = sum(
            all(((S[j] & t).bit_count() & 1) == 0 for j in R)
            for R in row_supports
        )
        walsh = sum(1 if ((s & t).bit_count() & 1) == 0 else -1 for s in S)
        assert 4 * q_direct == n + 3 * walsh
        assert 2 * q_direct == 2 * n - 3 * w
        qs.append(q_direct)
        ws.append(w)

    models = direct_exactone(A)
    sat_by_rows = bool(models)
    sat_by_walsh = max(ws) * 3 == 2 * n
    assert sat_by_rows == expect_sat == sat_by_walsh

    mean4 = 4 * sum(qs)
    # E[q]=n/4 over all 2^k characters.
    assert mean4 == n * len(qs)
    # Var(q)=9n/16: compare after clearing denominator 16*2^k.
    # 16 * sum (q-n/4)^2 = sum (4q-n)^2.
    lhs = sum((4 * q - n) ** 2 for q in qs)
    assert lhs == 9 * n * len(qs)

    return {
        "name": name,
        "n": n,
        "rank_F2": rank,
        "kernel_dimension": k,
        "distinct_nonzero_signatures": len(set(S)),
        "exactone_witness_count": len(models),
        "min_bad_lines": min(qs),
        "max_kernel_eval_weight": max(ws),
        "target_2n_over_3": 2 * n // 3,
        "q_distribution": dict(sorted(Counter(qs).items())),
    }


def main():
    out = [
        run("PG15_UNSAT_R13", UNSAT_LINES, False, 11),
        run("PG15_SAT_R11", SAT_LINES, True, 10),
    ]
    print(json.dumps({
        "status": "PASS_PROJECTIVE_SIGNATURE_WALSH_ARRANGEMENT_QUOTIENT",
        "scientific_ceiling": "FINITE_REGRESSION_ONLY__ARBITRARY_N_PROOF_IN_COMPANION_NOTE__NO_D1_PROMOTION__P_VS_NP_OPEN",
        "controls": out,
        "conclusion": "bad-line count equals Walsh point-set formula; SAT iff maximum kernel evaluation weight is 2n/3 on frozen controls",
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
