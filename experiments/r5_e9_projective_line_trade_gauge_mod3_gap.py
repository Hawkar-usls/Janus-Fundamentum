#!/usr/bin/env python3
"""Finite regression for projective line-trade gauge + mod-3 gap.

OFFLINE_FALSIFIER_ONLY: the finite PG(3,2) census is not an asymptotic theorem.
"""
from fractions import Fraction
from itertools import combinations, product
from collections import defaultdict

UNSAT = [
    (1,10,11),(1,12,13),(1,14,15),
    (2,4,6),(2,5,7),(2,12,14),
    (3,4,7),(3,8,11),(3,9,10),
    (4,11,15),(5,8,13),(5,9,12),
    (6,8,14),(6,9,15),(7,10,13),
]
TERMINAL_REMOVE = {(1,12,13),(3,8,11),(6,9,15)}
TERMINAL_ADD = {(1,8,9),(3,12,15),(6,11,13)}


def rows_matrix(rows, n=15):
    return [[1 if j + 1 in r else 0 for j in range(n)] for r in rows]


def gf2_rref(M):
    A = [row[:] for row in M]
    m, n = len(A), len(A[0])
    pivots = []
    r = 0
    for c in range(n):
        p = next((i for i in range(r, m) if A[i][c]), None)
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        for i in range(m):
            if i != r and A[i][c]:
                A[i] = [x ^ y for x, y in zip(A[i], A[r])]
        pivots.append(c)
        r += 1
    return A, pivots


def gf2_rank(M):
    return len(gf2_rref(M)[1])


def q_rank(M):
    A = [[Fraction(x) for x in row] for row in M]
    m, n = len(A), len(A[0])
    r = 0
    for c in range(n):
        p = next((i for i in range(r, m) if A[i][c] != 0), None)
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        piv = A[r][c]
        A[r] = [x / piv for x in A[r]]
        for i in range(m):
            if i != r and A[i][c] != 0:
                f = A[i][c]
                A[i] = [x - f*y for x, y in zip(A[i], A[r])]
        r += 1
    return r


def kernel_basis(M):
    R, pivots = gf2_rref(M)
    n = len(M[0])
    free = [j for j in range(n) if j not in pivots]
    out = []
    for f in free:
        x = [0] * n
        x[f] = 1
        for i, p in enumerate(pivots):
            x[p] = R[i][f]
        out.append(tuple(x))
    return out


def span(basis):
    out = set()
    for coeff in product((0,1), repeat=len(basis)):
        v = [0] * len(basis[0]) if basis else []
        for a, b in zip(coeff, basis):
            if a:
                v = [x ^ y for x, y in zip(v, b)]
        out.add(tuple(v))
    return out


def exact_one(rows, n=15):
    models = set()
    for mask in range(1 << n):
        if all(sum((mask >> (j-1)) & 1 for j in row) == 1 for row in rows):
            models.add(mask)
    return models


def degree_vector(rows, n=15):
    d = [0] * n
    for row in rows:
        for j in row:
            d[j-1] += 1
    return tuple(d)


def signatures(M):
    B = kernel_basis(M)
    sig = []
    for j in range(len(M[0])):
        value = 0
        for i, b in enumerate(B):
            value |= b[j] << i
        sig.append(value)
    return B, sig


def all_actual_projective_lines(sig):
    out = []
    for a,b,c in combinations(range(1, len(sig)+1), 3):
        if sig[a-1] ^ sig[b-1] ^ sig[c-1] == 0:
            out.append((a,b,c))
    return out


def rank_safe_3trades(old, all_lines):
    old = set(old)
    outside = sorted(set(all_lines) - old)
    old_rank = gf2_rank(rows_matrix(sorted(old)))
    removed_by_degree = defaultdict(list)
    for rem in combinations(sorted(old), 3):
        removed_by_degree[degree_vector(rem)].append(rem)
    trades = []
    for add in combinations(outside, 3):
        for rem in removed_by_degree.get(degree_vector(add), []):
            new = (old - set(rem)) | set(add)
            if gf2_rank(rows_matrix(sorted(new))) == old_rank:
                trades.append((rem, add, new))
    return trades


def main():
    old = {tuple(sorted(r)) for r in UNSAT}
    A = rows_matrix(sorted(old))
    B, sig = signatures(A)

    assert degree_vector(old) == (3,) * 15
    assert gf2_rank(A) == 11
    assert q_rank(A) == 13
    assert len(B) == 4
    assert len(set(sig)) == 15 and 0 not in sig
    assert exact_one(old) == set()

    all_lines = all_actual_projective_lines(sig)
    assert len(all_lines) == 35
    assert old <= set(all_lines)

    trades = rank_safe_3trades(old, all_lines)
    assert len(trades) == 31
    qrank_counts = defaultdict(int)
    for _, _, new in trades:
        qrank_counts[q_rank(rows_matrix(sorted(new)))] += 1
    assert dict(qrank_counts) == {13: 25, 15: 6}

    terminal_new = (old - TERMINAL_REMOVE) | TERMINAL_ADD
    Ap = rows_matrix(sorted(terminal_new))
    assert degree_vector(terminal_new) == (3,) * 15
    assert gf2_rank(Ap) == 11
    assert q_rank(Ap) == 15
    assert span(kernel_basis(A)) == span(kernel_basis(Ap))
    assert exact_one(terminal_new) == set()
    for a,b,c in TERMINAL_ADD:
        assert sig[a-1] ^ sig[b-1] ^ sig[c-1] == 0

    # Exhaustive Walsh/mod-3 replay over all t in F2^4.
    n = 15
    wmax = 0
    qmin = n
    for t in range(1 << 4):
        z = [((s & t).bit_count() & 1) for s in sig]
        w = sum(z)
        q = sum(all(z[j-1] == 0 for j in row) for row in old)
        assert 3 * w == 2 * (n - q)
        assert (q - n) % 3 == 0
        wmax = max(wmax, w)
        qmin = min(qmin, q)
    assert wmax == 8
    assert qmin == 3
    assert wmax == 2*n//3 - 2

    print({
        "status": "PASS_FINITE_PROJECTIVE_LINE_TRADE_GAUGE_MOD3_GAP",
        "all_projective_lines": len(all_lines),
        "rank_safe_3trades": len(trades),
        "rank_safe_qrank_census": dict(sorted(qrank_counts.items())),
        "old_rank_F2": gf2_rank(A),
        "new_rank_F2": gf2_rank(Ap),
        "old_rank_Q": q_rank(A),
        "terminal_exposing_rank_Q": q_rank(Ap),
        "wmax": wmax,
        "qmin": qmin,
    })


if __name__ == "__main__":
    main()
