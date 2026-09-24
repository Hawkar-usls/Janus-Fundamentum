#!/usr/bin/env python3
"""Finite controls for NM-0012 distinguished-torso restriction invariant."""

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

def scaffold(m):
    cols, meta = [], []
    for u in range(m):
        for v in range(u + 1, m):
            inc = 0
            if u:
                inc ^= 1 << (u - 1)
            if v:
                inc ^= 1 << (v - 1)
            for g in range(4):
                cols.append(inc | (g << (m - 1)))
                meta.append((u, v, g))
    return cols, meta

def cocycle_word(cols, y):
    w = 0
    for j, c in enumerate(cols):
        if (c & y).bit_count() & 1:
            w |= 1 << j
    return w

def linear_map(v, images):
    out = 0
    for i, image in enumerate(images):
        if (v >> i) & 1:
            out ^= image
    return out

def main():
    q4, meta = scaffold(4)
    assert len(q4) == 24
    assert len(set(q4)) == 24
    assert 0 not in q4
    assert gf2_rank(q4) == 5

    # Every nonzero cocycle of Q4 has weight 12 or 16.
    words = [cocycle_word(q4, y) for y in range(1, 1 << 5)]
    weights = sorted({w.bit_count() for w in words})
    assert weights == [12, 16]
    assert all(min(w.bit_count() for w in words if (w >> p) & 1) == 12
               for p in range(len(q4)))

    # Analytic 3-connectivity control.
    # Q4 is a simple rank-5 binary matroid.  If a 2-separation existed,
    # with ranks a,b >=2, then a+b<=6.  A simple rank-r binary set has
    # at most 2^r-1 elements.  The largest possible total is 3+15=18<24.
    max_bad_total = 0
    for a in range(2, 6):
        for b in range(2, 6):
            if a + b <= 6:
                max_bad_total = max(max_bad_total, (1 << a) - 1 + (1 << b) - 1)
    assert max_bad_total == 18 < len(q4)

    # Q4 contains the 12-element Q3 scaffold on vertices {0,1,2}.
    tri = [q4[i] for i, (u, v, g) in enumerate(meta) if u < 3 and v < 3]
    compressed = [(c & 0b11) | (((c >> 3) & 0b11) << 2) for c in tri]
    q3, _ = scaffold(3)
    assert set(compressed) == set(q3)

    # Exact S8 restriction certificate inside Q3.
    # Standard S8 columns [1,2,4,8,14,13,11,15].
    s8 = [1, 2, 4, 8, 14, 13, 11, 15]
    basis_images = [1, 2, 5, 9]
    assert gf2_rank(basis_images) == 4
    mapped = [linear_map(v, basis_images) for v in s8]
    assert mapped == [1, 2, 5, 9, 14, 13, 10, 15]
    assert all(v in q3 for v in mapped)

    # Growing complete-four-labelled family has the same obstruction.
    # For m>=4, nonzero cocycle weight is either 4*|cut| or m(m-1),
    # so cogirth is 4(m-1) > 4.
    for m in range(4, 9):
        cols, _ = scaffold(m)
        rank = m + 1
        observed = {cocycle_word(cols, y).bit_count() for y in range(1, 1 << rank)}
        expected = {4 * k * (m - k) for k in range(1, m)}
        expected.add(m * (m - 1))
        assert observed == expected
        assert min(observed) == 4 * (m - 1) > 4

    print("PASS")
    print("Q4_ELEMENTS = 24")
    print("Q4_RANK = 5")
    print("Q4_SIMPLE = PASS")
    print("Q4_3CONNECTED = PASS")
    print("Q4_S8_RESTRICTION = PASS")
    print("Q4_NONZERO_COCYCLE_WEIGHTS = [12, 16]")
    print("Q4_DISTINGUISHED_COCYCLE_MIN = 12 FOR EVERY p")
    print("CUBIC_TORSO_REAL_RESTRICTION_BOUND = p-CONTAINING SPANNING COCYCLES OF SIZE <= 4")
    print("PLACEMENT_UNIVERSALITY = FALSIFIED BY Q4")
    print("CLAIM_CEILING = PLACEMENT INVARIANT ONLY; D1 EMPTY; P_VS_NP OPEN")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
