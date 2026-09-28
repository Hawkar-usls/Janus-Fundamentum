#!/usr/bin/env python3
"""Finite regression for R5 E9 projective line-trade gauge + mod-3 gap.

OFFLINE_FALSIFIER_ONLY: finite controls do not prove the universal theorem.
The theorem itself is proved in the companion research note.
"""
from itertools import combinations, product

UNSAT = [
    (1,10,11),(1,12,13),(1,14,15),
    (2,4,6),(2,5,7),(2,12,14),
    (3,4,7),(3,8,11),(3,9,10),
    (4,11,15),(5,8,13),(5,9,12),
    (6,8,14),(6,9,15),(7,10,13),
]
REMOVE = {(1,12,13),(2,4,6),(3,8,11)}
ADD = {(1,2,3),(4,8,12),(6,11,13)}


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


def rank(M):
    return len(gf2_rref(M)[1])


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
    return d


def signatures(M):
    B = kernel_basis(M)
    sig = []
    for j in range(len(M[0])):
        value = 0
        for i, b in enumerate(B):
            value |= b[j] << i
        sig.append(value)
    return B, sig


def main():
    old = {tuple(sorted(r)) for r in UNSAT}
    new = (old - REMOVE) | ADD
    A = rows_matrix(sorted(old))
    Ap = rows_matrix(sorted(new))

    assert degree_vector(old) == [3] * 15
    assert degree_vector(new) == [3] * 15
    assert rank(A) == 11
    assert rank(Ap) == 11
    assert span(kernel_basis(A)) == span(kernel_basis(Ap))
    assert exact_one(old) == exact_one(new) == set()

    _, sig = signatures(A)
    assert len(set(sig)) == 15 and 0 not in sig
    # Every added line must be a genuine line of the ACTUAL kernel signatures.
    for a,b,c in ADD:
        assert sig[a-1] ^ sig[b-1] ^ sig[c-1] == 0

    # Exhaustive Walsh/mod-3 replay over all t in F2^4.
    n = 15
    for t in range(1 << 4):
        z = [((s & t).bit_count() & 1) for s in sig]
        w = sum(z)
        q = 0
        for row in old:
            if all(z[j-1] == 0 for j in row):
                q += 1
        assert 3 * w == 2 * (n - q)
        assert (q - n) % 3 == 0
        assert q == n - 3 * w // 2
    wmax = max(sum(((s & t).bit_count() & 1) for s in sig) for t in range(1 << 4))
    assert wmax == 8
    assert wmax <= 2*n//3 - 2

    print({
        "status": "PASS_FINITE_PROJECTIVE_LINE_TRADE_GAUGE_MOD3_GAP",
        "rank_old": rank(A),
        "rank_new": rank(Ap),
        "kernel_dimension": len(kernel_basis(A)),
        "exact_one_models": len(exact_one(old)),
        "trade_removed": sorted(REMOVE),
        "trade_added": sorted(ADD),
        "wmax": wmax,
        "sat_threshold": 2*n//3,
    })


if __name__ == "__main__":
    main()
