#!/usr/bin/env python3
from collections import Counter


def rows_to_cols(rows, n):
    cols = [0] * n
    for r, row in enumerate(rows):
        for j in row:
            cols[j] |= 1 << r
    return cols


def assert_linear_cubic(rows, n):
    assert len(rows) == n
    assert all(len(set(r)) == 3 for r in rows)
    deg = [0] * n
    seen = set()
    for row in rows:
        for j in row:
            deg[j] += 1
        for i in range(3):
            for j in range(i + 1, 3):
                p = tuple(sorted((row[i], row[j])))
                assert p not in seen
                seen.add(p)
    assert deg == [3] * n


def kernel_basis(cols):
    basis = {}
    out = []
    for j, v0 in enumerate(cols):
        v = v0
        comb = 1 << j
        while v:
            p = v.bit_length() - 1
            if p in basis:
                v ^= basis[p][0]
                comb ^= basis[p][1]
            else:
                basis[p] = (v, comb)
                break
        if not v:
            out.append(comb)
    return out


def kernel_words(basis):
    out = [0]
    for b in basis:
        out += [x ^ b for x in out]
    return out


def syndrome(cols, word):
    s = 0
    for j, c in enumerate(cols):
        if (word >> j) & 1:
            s ^= c
    return s


def stats(cols, S):
    n = len(cols)
    basis = kernel_basis(cols)
    words = kernel_words(basis)
    smask = sum(1 << i for i in S)
    target = (1 << n) - 1
    assert syndrome(cols, smask) == target

    masks = []
    for j in range(n):
        masks.append(sum(((b >> j) & 1) << q for q, b in enumerate(basis)))

    Sin = set(S)
    aS = sum(masks[i] != 0 for i in S)
    aO = sum(masks[i] != 0 for i in range(n) if i not in Sin)

    d = Counter()
    for i, a in enumerate(masks):
        if a:
            d[a] += 1 if i in Sin else -1

    H = []
    for w in words:
        inside = sum((w >> i) & 1 for i in S)
        outside = w.bit_count() - inside
        H.append(inside - outside)

    C = aS - aO
    mean2_num = C  # 2 E[H]
    second4_num = C * C + sum(v * v for v in d.values())  # 4 E[H^2]
    q4_num = sum(v * v for v in d.values()) + aS * aS - aO * aO

    den = len(H)
    assert 2 * sum(H) == den * mean2_num
    assert 4 * sum(h * h for h in H) == den * second4_num
    assert 4 * sum(h * (h + aO) for h in H) == den * q4_num

    min_coset = min((smask ^ w).bit_count() for w in words)
    min_external_improving = min(
        (sum((w >> i) & 1 for i in range(n) if i not in Sin)
         for w, h in zip(words, H) if h > 0),
        default=None,
    )
    return {
        "k": len(basis),
        "aS": aS,
        "aO": aO,
        "d2": sum(v * v for v in d.values()),
        "H": sorted(H),
        "q4": q4_num,
        "min_coset": min_coset,
        "min_ext": min_external_improving,
        "basis": basis,
    }


def cyclic_rows(n):
    return [[i, (i + 1) % n, (i + 5) % n] for i in range(n)]


def cyclic_control():
    baseS = {1, 2, 3, 6, 7, 9, 11, 17, 18, 19, 20}
    for m in (1, 2, 3, 4):
        n = 21 * m
        rows = cyclic_rows(n)
        assert_linear_cubic(rows, n)
        cols = rows_to_cols(rows, n)
        S = sorted({r + 21 * q for q in range(m) for r in baseS})
        st = stats(cols, S)
        assert st["k"] == 5
        assert len(S) == 11 * m
        assert st["min_coset"] == 7 * m
        assert st["aS"] == 11 * m
        assert st["aO"] == 10 * m
        assert st["min_ext"] == 3 * m
        # Every kernel word repeats its first 21 coordinates.
        for w in kernel_words(st["basis"]):
            block = w & ((1 << 21) - 1)
            expect = sum(block << (21 * q) for q in range(m))
            assert w == expect


ROWS_FIRST_NEG = [
    [0,7,9],[1,7,10],[2,5,8],[1,3,13],[0,4,16],[5,12,15],
    [1,6,15],[7,11,13],[6,8,14],[3,9,14],[8,10,16],[4,11,17],
    [10,11,12],[0,2,13],[5,14,17],[2,4,15],[9,12,16],[3,6,17],
]
S_FIRST_NEG = [0,1,4,5,11,14,16,17]

ROWS_SECOND_FAIL = [
    [0,11,14],[1,10,13],[2,5,14],[2,3,4],[4,6,7],[1,3,5],
    [6,15,16],[5,7,17],[1,7,8],[0,9,16],[0,3,10],[6,11,12],
    [8,9,12],[4,11,13],[8,14,15],[9,13,15],[2,16,17],[10,12,17],
]
S_SECOND_FAIL = [1,3,5,6,11,12,15,16]


def finite_controls():
    assert_linear_cubic(ROWS_FIRST_NEG, 18)
    a = stats(rows_to_cols(ROWS_FIRST_NEG, 18), S_FIRST_NEG)
    assert a["k"] == 2
    assert a["min_coset"] == 6
    assert (a["aS"], a["aO"]) == (6, 10)
    assert sum(a["H"]) / len(a["H"]) == -2
    assert a["q4"] == 24  # 4 E[Q] = 24 -> E[Q]=6
    assert max(a["H"]) > 0

    assert_linear_cubic(ROWS_SECOND_FAIL, 18)
    b = stats(rows_to_cols(ROWS_SECOND_FAIL, 18), S_SECOND_FAIL)
    assert b["k"] == 3
    assert b["min_coset"] == 6
    assert (b["aS"], b["aO"]) == (6, 10)
    assert b["H"] == [-10, -4, -2, -2, 0, 0, 0, 2]
    assert b["q4"] == -16  # 4 E[Q] = -16 -> E[Q]=-4
    assert max(b["H"]) == 2


if __name__ == "__main__":
    cyclic_control()
    finite_controls()
    print("PASS: kernel Walsh first/second-moment identities and hostile controls")
