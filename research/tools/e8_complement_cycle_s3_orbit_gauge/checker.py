#!/usr/bin/env python3
from itertools import product, permutations
from math import comb

COLORS = (0, 1, 2)
S3 = tuple(permutations(COLORS))


def proper_cycle(c):
    k = len(c)
    return all(c[i] != c[(i + 1) % k] for i in range(k))


def cycle_colorings(k):
    return [c for c in product(COLORS, repeat=k) if proper_cycle(c)]


def act(g, c):
    return tuple(g[x] for x in c)


def orbit(c):
    return frozenset(act(g, c) for g in S3)


def orbit_partition(colorings):
    unseen = set(colorings)
    out = []
    while unseen:
        c = min(unseen)
        o = orbit(c)
        assert o <= set(colorings)
        out.append(o)
        unseen -= o
    return out


def find_unique_decomposition(c, reps):
    hits = []
    for t, r in enumerate(reps):
        for g in S3:
            if act(g, r) == c:
                hits.append((t, g))
    return hits


def main():
    # Chromatic-polynomial count and S3 orbit formula on several controls.
    for k in range(3, 9):
        cols = cycle_colorings(k)
        expected = 2**k + 2 * ((-1) ** k)
        assert len(cols) == expected, (k, len(cols), expected)
        parts = orbit_partition(cols)
        assert all(len(o) == 6 for o in parts), (k, [len(o) for o in parts])
        assert len(parts) == expected // 6, (k, len(parts), expected // 6)

    assert len(orbit_partition(cycle_colorings(3))) == 1
    assert len(orbit_partition(cycle_colorings(4))) == 3

    reps = [
        (0, 1, 0, 1),
        (0, 1, 0, 2),
        (0, 1, 2, 1),
    ]
    assert all(proper_cycle(r) for r in reps)
    rep_orbits = [orbit(r) for r in reps]
    assert len(set(rep_orbits)) == 3
    assert set().union(*map(set, rep_orbits)) == set(cycle_colorings(4))

    # Every proper C4 coloring has a unique (orbit type, S3 gauge) decomposition.
    for c in cycle_colorings(4):
        hits = find_unique_decomposition(c, reps)
        assert len(hits) == 1, (c, hits)

    # Equality-pattern classification of the three C4 orbit representatives.
    signatures = []
    for r in reps:
        signatures.append((r[0] == r[2], r[1] == r[3]))
    assert signatures == [(True, True), (True, False), (False, True)]

    # Tension view: every proper oriented C4 has exactly two +1 and two -1 edges.
    for c in cycle_colorings(4):
        diffs = [((c[(i + 1) % 4] - c[i]) % 3) for i in range(4)]
        assert set(diffs) <= {1, 2}
        assert diffs.count(1) == 2 and diffs.count(2) == 2, (c, diffs)

    # Relative-gauge edge constraint h(a) != b forbids exactly |Stab(a)|=2 gauges.
    for a in COLORS:
        for b in COLORS:
            forbidden = [g for g in S3 if g[a] == b]
            allowed = [g for g in S3 if g[a] != b]
            assert len(forbidden) == 2
            assert len(allowed) == 4

    print("PASS: complement-cycle S3 orbit-gauge quotient controls")
    print("C3 orbit count = 1")
    print("C4 orbit count = 3")
    print("C4 proper colorings = 18 = 3 types * 6 gauges")
    print("relative-gauge edge constraint: 2 forbidden / 4 allowed elements of S3")


if __name__ == "__main__":
    main()
