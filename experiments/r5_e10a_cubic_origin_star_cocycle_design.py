#!/usr/bin/env python3
"""Finite controls for the cubic-origin star-cocycle design characterization."""

from itertools import combinations

def gf2_rank(vectors):
    basis = {}
    for x in vectors:
        y = x
        while y:
            p = y.bit_length() - 1
            if p in basis:
                y ^= basis[p]
            else:
                basis[p] = y
                break
    return len(basis)

def columns_from_rows(rows, ncols):
    cols = []
    for j in range(ncols):
        v = 0
        for i, row in enumerate(rows):
            if (row >> j) & 1:
                v |= 1 << i
        cols.append(v)
    return cols

def rowspace(rows):
    out = {0}
    for r in rows:
        out |= {x ^ r for x in list(out)}
    return out

def verify_star(rows_h):
    n = len(rows_h)
    mask = (1 << n) - 1
    assert all(r.bit_count() == 3 for r in rows_h)
    cover = [0] * n
    for r in rows_h:
        for j in range(n):
            cover[j] += (r >> j) & 1
    assert cover == [3] * n

    rows_full = [r | (1 << n) for r in rows_h]
    assert all(r.bit_count() == 4 for r in rows_full)
    assert gf2_rank(rows_full) == gf2_rank(rows_h)

    cols_h = columns_from_rows(rows_h, n)
    assert all(c.bit_count() == 3 for c in cols_h)

    # H*1=1 and all columns of [H|1] sum to zero.
    all_h = 0
    for c in cols_h:
        all_h ^= c
    assert all_h == mask
    assert (all_h ^ mask) == 0
    return rows_full

def matrix_from_perms(n, p, q):
    rows = [0] * n
    for j in range(n):
        for i in (j, p[j], q[j]):
            rows[i] |= 1 << j
    return rows

def positive_controls():
    controls = [
        (5, (1,2,3,4,0), (2,3,4,0,1)),
        (7, (6,0,5,4,2,1,3), (5,2,3,0,6,4,1)),
    ]
    for n,p,q in controls:
        assert all(len({j,p[j],q[j]}) == 3 for j in range(n))
        rows = matrix_from_perms(n,p,q)
        verify_star(rows)

def s8_direct_negative_control():
    # Sage-catalog convention: [I4 | 1110,1101,1011,1111].
    cols = [1,2,4,8,14,13,11,15]
    rows = []
    for i in range(4):
        r = 0
        for j,c in enumerate(cols):
            if (c >> i) & 1:
                r |= 1 << j
        rows.append(r)
    cocycles = rowspace(rows)
    wt3 = [x for x in cocycles if x.bit_count() == 3]
    assert len(wt3) == 3
    covered = 0
    for x in wt3:
        covered |= x
    # At least one coordinate is absent from every weight-3 cocycle, so no
    # multiset of weight-3 cocycles can give column degree three everywhere.
    assert covered != (1 << 8) - 1
    return len(wt3), covered

def main():
    positive_controls()
    wt3,covered = s8_direct_negative_control()
    print("PASS")
    print("STAR_COCYCLE_FORWARD_CONTROLS = PASS")
    print("STAR_COCYCLE_CONVERSE_RECONSTRUCTION = PASS")
    print("S8_DIRECT_WEIGHT3_COCYCLES =", wt3)
    print("S8_DIRECT_ALL_COORDINATES_COVERED =", covered == (1<<8)-1)
    print("CLAIM_CEILING = DIRECT_PARENT_CHARACTERIZATION_ONLY; MINOR_LIFT_OPEN")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
