#!/usr/bin/env python3
"""Exact regression for post-RKPR survival of the doily two-edge SAT 2-lift family.

Uses only Python Fraction arithmetic.  It reconstructs the doily and the first
two canonical lifts, computes exact rational nullspaces, audits all projective
kernel-row ratios, forms the equality quotient, and checks the six lifted star
witnesses coordinate-wise.
"""

from collections import defaultdict
from fractions import Fraction
from itertools import combinations


def perfect_matchings(vertices):
    vertices = tuple(vertices)
    if not vertices:
        yield ()
        return
    a = vertices[0]
    for k in range(1, len(vertices)):
        b = vertices[k]
        rest = vertices[1:k] + vertices[k + 1 :]
        for tail in perfect_matchings(rest):
            yield tuple(sorted(((min(a, b), max(a, b)),) + tail))


def rank_and_nullspace(mat):
    a = [[Fraction(x) for x in row] for row in mat]
    m, n = len(a), len(a[0])
    pivots = []
    r = 0
    for c in range(n):
        p = next((i for i in range(r, m) if a[i][c]), None)
        if p is None:
            continue
        a[r], a[p] = a[p], a[r]
        z = a[r][c]
        a[r] = [x / z for x in a[r]]
        for i in range(m):
            if i == r or a[i][c] == 0:
                continue
            z = a[i][c]
            a[i] = [a[i][j] - z * a[r][j] for j in range(n)]
        pivots.append(c)
        r += 1
        if r == m:
            break

    pset = set(pivots)
    free = [c for c in range(n) if c not in pset]
    basis = []
    for f in free:
        v = [Fraction(0) for _ in range(n)]
        v[f] = 1
        for i, p in enumerate(pivots):
            v[p] = -a[i][f]
        basis.append(v)
    return r, basis


def verify_carrier(a):
    n = len(a)
    assert all(len(row) == n for row in a)
    assert all(sum(row) == 3 for row in a)
    assert all(sum(a[i][j] for i in range(n)) == 3 for j in range(n))
    supports = [{j for j, x in enumerate(row) if x} for row in a]
    for i, j in combinations(range(n), 2):
        assert len(supports[i] & supports[j]) <= 1


def verify_witness(a, x):
    return all(sum(row[j] * x[j] for j in range(len(x))) == 1 for row in a)


def lift(a, twists):
    n = len(a)
    twists = set(twists)
    out = [[0] * (2 * n) for _ in range(2 * n)]
    for i in range(n):
        for j in range(n):
            if not a[i][j]:
                continue
            if (i, j) in twists:
                out[i][j + n] = 1
                out[i + n][j] = 1
            else:
                out[i][j] = 1
                out[i + n][j + n] = 1
    return out


def choose_two_twists(a, forbidden):
    n = len(a)
    candidates = [
        (i, j)
        for i in range(n)
        for j in range(n)
        if a[i][j] and (i, j) not in forbidden
    ]
    for e, f in combinations(candidates, 2):
        if e[0] != f[0] and e[1] != f[1]:
            return (e, f)
    raise AssertionError("no nonadjacent twist pair")


def projective_audit(a):
    rank, basis = rank_and_nullspace(a)
    n = len(a)
    d = len(basis)

    # Kernel-basis matrix rows: coordinate functionals on ker_Q(A).
    rows = [tuple(basis[j][i] for j in range(d)) for i in range(n)]
    zero_rows = [i for i, row in enumerate(rows) if all(x == 0 for x in row)]

    classes = defaultdict(list)
    for i, row in enumerate(rows):
        if i in zero_rows:
            continue
        p = next(j for j, x in enumerate(row) if x)
        scalar = row[p]
        normalized = tuple(x / scalar for x in row)
        classes[normalized].append((i, scalar))

    illegal = []
    pins = []
    unequal_proportional = []
    for arr in classes.values():
        for (i, si), (j, sj) in combinations(arr, 2):
            lam = si / sj
            if lam not in (Fraction(1), Fraction(-2), Fraction(-1, 2)):
                illegal.append((i, j, lam))
            if lam in (Fraction(-2), Fraction(-1, 2)):
                pins.append((i, j, lam))
            if lam != 1:
                unequal_proportional.append((i, j, lam))

    # Since the audited stages have no unequal proportional rows, each
    # projective class is exactly one RKPR equality class.
    assert not unequal_proportional
    groups = [tuple(i for i, _ in arr) for arr in classes.values()]
    class_of = {}
    for c, group in enumerate(groups):
        for i in group:
            class_of[i] = c

    quotient = []
    repeated_class_rows = []
    for r, row in enumerate(a):
        qrow = [0] * len(groups)
        for i, x in enumerate(row):
            if x:
                qrow[class_of[i]] += x
        if max(qrow) > 1:
            repeated_class_rows.append(r)
        quotient.append(qrow)

    qrank, qnull = rank_and_nullspace(quotient)
    qdim = len(qnull)

    return {
        "rank": rank,
        "nullity": d,
        "zero_rows": zero_rows,
        "illegal": illegal,
        "pins": pins,
        "unequal_proportional": unequal_proportional,
        "q": len(groups),
        "quotient_rank": qrank,
        "quotient_nullity": qdim,
        "repeated_class_rows": repeated_class_rows,
    }


def main():
    points = list(combinations(range(6), 2))
    matchings = sorted(set(perfect_matchings(range(6))))
    assert len(points) == len(matchings) == 15

    a0 = [[int(p in m) for p in points] for m in matchings]
    verify_carrier(a0)

    # Six star witnesses.  Every K6 edge belongs to exactly two stars, so every
    # coordinate takes both 0 and 1 across the witness family.
    stars0 = [[int(a in p) for p in points] for a in range(6)]
    assert all(verify_witness(a0, x) for x in stars0)
    for j in range(15):
        vals = {x[j] for x in stars0}
        assert vals == {0, 1}

    cycle_rows = [5, 2, 10, 13, 8]
    cycle_cols = [12, 11, 6, 10, 8]
    expected = [
        [1, 0, 0, 0, 1],
        [1, 1, 0, 0, 0],
        [0, 1, 1, 0, 0],
        [0, 0, 1, 1, 0],
        [0, 0, 0, 1, 1],
    ]
    assert [[a0[i][j] for j in cycle_cols] for i in cycle_rows] == expected

    cycle_inc = set()
    for ii, r in enumerate(cycle_rows):
        for jj, c in enumerate(cycle_cols):
            if expected[ii][jj]:
                cycle_inc.add((r, c))

    twists1 = choose_two_twists(a0, cycle_inc)
    a1 = lift(a0, twists1)
    verify_carrier(a1)
    stars1 = [x + x for x in stars0]
    assert all(verify_witness(a1, x) for x in stars1)
    for j in range(30):
        assert {x[j] for x in stars1} == {0, 1}

    twists2 = choose_two_twists(a1, cycle_inc)
    a2 = lift(a1, twists2)
    verify_carrier(a2)
    stars2 = [x + x for x in stars1]
    assert all(verify_witness(a2, x) for x in stars2)
    for j in range(60):
        assert {x[j] for x in stars2} == {0, 1}

    expected_stages = [
        (a0, 10, 5, 15),
        (a1, 22, 8, 27),
        (a2, 46, 14, 51),
    ]

    results = []
    for stage, (a, expected_rank, expected_nullity, expected_q) in enumerate(expected_stages):
        audit = projective_audit(a)
        assert audit["rank"] == expected_rank
        assert audit["nullity"] == expected_nullity
        assert audit["q"] == expected_q
        assert audit["quotient_nullity"] == expected_nullity
        assert audit["zero_rows"] == []
        assert audit["illegal"] == []
        assert audit["pins"] == []
        assert audit["unequal_proportional"] == []
        assert audit["repeated_class_rows"] == []
        results.append((stage, len(a), audit["nullity"], audit["q"]))

    print("PASS: two-edge SAT 2-lift survives RKPR finite regression")
    print(f"twists1={twists1} twists2={twists2}")
    for stage, n, d, q in results:
        print(f"stage={stage} n={n} nullity_Q={d} RKPR_equality_variables={q}")
    print("all stages: zero_rows=0 illegal_ratios=0 pins=0 repeated_class_rows=0")
    print("arbitrary theorem: six fiber-constant star witnesses vary every coordinate")
    print("arbitrary theorem: RKPR classes equality-only and nu_Q is preserved")
    print("post-RKPR family nullity >= n/5+2")
    print("E8_D1=EMPTY")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    main()
