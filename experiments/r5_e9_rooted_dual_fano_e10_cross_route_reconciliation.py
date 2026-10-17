#!/usr/bin/env python3
"""Exact finite regression for the n=15 E10 / rooted-dual-Fano reconciliation.

This checker verifies explicit rooted F7 and F7* minors in A=I+P+P^4,
and verifies that the same cubic source is full rank over Q and has no
Exact-One witness.  Finite regression only; no universal P=NP promotion.
"""
from itertools import combinations
from fractions import Fraction
import json

N = 15


def gf2_rank(vecs):
    basis = {}
    for x in vecs:
        y = x
        while y:
            p = y.bit_length() - 1
            if p in basis:
                y ^= basis[p]
            else:
                basis[p] = y
                break
    return len(basis)


def columns():
    out = []
    # Column j of I+P+P^4; cyclic orientation choice is immaterial.
    for j in range(N):
        rows = (j, (j - 1) % N, (j - 4) % N)
        v = 0
        for r in rows:
            v |= 1 << r
        out.append(v)
    return out


def minor_cycle_weights(allcols, contract, keep):
    base = [allcols[i] for i in contract]
    r0 = gf2_rank(base)
    r = gf2_rank(base + [allcols[i] for i in keep]) - r0
    weights = []
    for mask in range(1, 1 << len(keep)):
        x = 0
        for t, idx in enumerate(keep):
            if (mask >> t) & 1:
                x ^= allcols[idx]
        if gf2_rank(base + [x]) == r0:
            weights.append(mask.bit_count())
    return r, sorted(weights)


def is_simple_rank3(allcols, contract, keep):
    base = [allcols[i] for i in contract]
    r0 = gf2_rank(base)
    if gf2_rank(base + [allcols[i] for i in keep]) - r0 != 3:
        return False
    for i in keep:
        if gf2_rank(base + [allcols[i]]) == r0:
            return False
    for i, j in combinations(keep, 2):
        if gf2_rank(base + [allcols[i], allcols[j]]) - r0 != 2:
            return False
    return True


def rational_rank_and_det(cols):
    # Build integer matrix row-major then fraction Gaussian elimination.
    a = [[Fraction((cols[j] >> i) & 1) for j in range(N)] for i in range(N)]
    det = Fraction(1)
    rank = 0
    for c in range(N):
        pivot = next((r for r in range(rank, N) if a[r][c]), None)
        if pivot is None:
            continue
        if pivot != rank:
            a[rank], a[pivot] = a[pivot], a[rank]
            det *= -1
        pv = a[rank][c]
        det *= pv
        for j in range(c, N):
            a[rank][j] /= pv
        for r in range(rank + 1, N):
            if a[r][c]:
                q = a[r][c]
                for j in range(c, N):
                    a[r][j] -= q * a[rank][j]
        rank += 1
    if rank < N:
        det = Fraction(0)
    return rank, int(det)


def exactone_models(cols):
    full = (1 << N) - 1
    models = []
    # Any exact cover selects exactly N/3=5 columns.
    for chosen in combinations(range(N), N // 3):
        used = 0
        ok = True
        for j in chosen:
            if used & cols[j]:
                ok = False
                break
            used |= cols[j]
        if ok and used == full:
            models.append(chosen)
    return models


def main():
    cols = columns()
    b = (1 << N) - 1
    allcols = cols + [b]
    root = N

    # Rooted F7* certificate.
    keep_f7s = [0, 1, 2, 3, 4, 5, root]
    con_f7s = [6, 7, 8, 11, 12, 13, 14]
    r_f7s, cw_f7s = minor_cycle_weights(allcols, con_f7s, keep_f7s)
    assert r_f7s == 4
    assert cw_f7s == [4] * 7

    # Rooted F7 certificate: simple rank-3 on seven elements is F7.
    keep_f7 = [0, 1, 2, 4, 5, 8, root]
    con_f7 = [3, 6, 7, 9, 10, 11, 12, 13]
    assert is_simple_rank3(allcols, con_f7, keep_f7)
    r_f7, cw_f7 = minor_cycle_weights(allcols, con_f7, keep_f7)
    assert r_f7 == 3

    rank_q, det_q = rational_rank_and_det(cols)
    assert rank_q == N
    assert abs(det_q) == 144

    models = exactone_models(cols)
    assert models == []

    out = {
        "status": "PASS_ROOTED_DUAL_FANO_E10_CROSS_ROUTE_RECONCILIATION",
        "scientific_ceiling": "FINITE_EXACT_CONTROL_ONLY__NO_D1_PROMOTION__P_VS_NP_OPEN",
        "n": N,
        "rooted_F7star": {
            "keep_original": [0,1,2,3,4,5],
            "contract": con_f7s,
            "delete": [9,10],
            "minor_rank": r_f7s,
            "nonzero_cycle_weights": cw_f7s,
        },
        "rooted_F7": {
            "keep_original": [0,1,2,4,5,8],
            "contract": con_f7,
            "delete": [14],
            "minor_rank": r_f7,
        },
        "rational_rank": rank_q,
        "rational_nullity": N-rank_q,
        "det_abs": abs(det_q),
        "exactone_models": len(models),
        "commuting_normal_form": "Q=P^4, hence PQ=QP",
        "conclusion": "rooted dual-Fano + S8/high-q structural obstruction does not imply semantic hardness",
    }
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
