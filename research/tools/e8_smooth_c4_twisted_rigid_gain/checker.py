#!/usr/bin/env python3
"""Exact replay for v7.9 smooth-C4 twisted-orbit rigid S3 transducer."""

from itertools import permutations, product

D = range(3)
S3 = list(permutations(D))
ID = (0, 1, 2)
REPS = {
    0: (0, 1, 0, 1),
    1: (0, 1, 0, 2),
    2: (0, 1, 2, 1),
}
# Retained bundles of the explicit smooth v7.7 positive control.
BUNDLES = {
    (0, 1): [(1, 0), (1, 1), (2, 1)],
    (0, 2): [],
    (0, 3): [(3, 1), (0, 3)],
    (1, 2): [(2, 0), (3, 2)],
    (1, 3): [],
    (2, 3): [(0, 0), (1, 0), (1, 1), (2, 2), (3, 2), (3, 3)],
}
EXPECTED_ORBIT = {(0, 1), (1, 0), (2, 2)}
EXPECTED_G1 = {
    (0, 1): (0, 2, 1),
    (1, 0): (0, 2, 1),
    (2, 2): (2, 0, 1),
}
EXPECTED_H = {
    (0, 1): (0, 2, 1),
    (1, 0): (0, 2, 1),
    (2, 2): (1, 2, 0),
}
PI = {0: 1, 1: 0, 2: 2}


def compose(p, q):
    return tuple(p[q[i]] for i in D)


def inverse(p):
    out = [0, 0, 0]
    for i, v in enumerate(p):
        out[v] = i
    return tuple(out)


def bundle_ok(i, j, ti, tj, gi, gj):
    return all(
        gi[REPS[ti][p]] != gj[REPS[tj][q]]
        for p, q in BUNDLES[(i, j)]
    )


def exact_terminal_gain_sets():
    rows = {}
    extension_counts = {}
    for t0 in D:
        for t1 in D:
            gains = set()
            counts_by_g1 = {}
            g0 = ID
            for t2, t3 in product(D, repeat=2):
                for g1, g2, g3 in product(S3, repeat=3):
                    ts = [t0, t1, t2, t3]
                    gs = [g0, g1, g2, g3]
                    if not all(
                        bundle_ok(i, j, ts[i], ts[j], gs[i], gs[j])
                        for i, j in BUNDLES
                    ):
                        continue
                    gains.add(inverse(g1))  # h_01 = g1^{-1} g0, g0=id
                    counts_by_g1[g1] = counts_by_g1.get(g1, 0) + 1
            if gains:
                rows[(t0, t1)] = gains
                extension_counts[(t0, t1)] = counts_by_g1
    return rows, extension_counts


def transducer(state):
    tau, g = state
    h = EXPECTED_H[(tau, PI[tau])]
    return (PI[tau], compose(g, inverse(h)))


def cycle_lengths(mapping):
    unseen = set(mapping)
    lengths = []
    while unseen:
        x = next(iter(unseen))
        y = x
        n = 0
        while y in unseen:
            unseen.remove(y)
            n += 1
            y = mapping[y]
        assert y == x
        lengths.append(n)
    return sorted(lengths)


def power_state(state, k):
    out = state
    if k >= 0:
        for _ in range(k):
            out = transducer(out)
        return out
    # Invert by finite search; domain is constant and this is only a replay helper.
    invmap = {transducer(s): s for s in product(D, S3)}
    for _ in range(-k):
        out = invmap[out]
    return out


def main():
    rows, extension_counts = exact_terminal_gain_sets()
    assert set(rows) == EXPECTED_ORBIT
    for pair in EXPECTED_ORBIT:
        assert rows[pair] == {EXPECTED_H[pair]}
        assert set(extension_counts[pair]) == {EXPECTED_G1[pair]}
        assert extension_counts[pair][EXPECTED_G1[pair]] == 4

    states = list(product(D, S3))
    mapping = {s: transducer(s) for s in states}
    assert len(set(mapping.values())) == 18
    assert cycle_lengths(mapping) == [2] * 6 + [3] * 2
    assert all(power_state(s, 6) == s for s in states)
    assert any(power_state(s, 2) != s for s in states)
    assert any(power_state(s, 3) != s for s in states)

    fixed = {
        k: sum(power_state(s, k) == s for s in states)
        for k in range(1, 7)
    }
    assert fixed == {1: 0, 2: 12, 3: 6, 4: 12, 5: 0, 6: 18}

    print("PASS: projected orbit relation = {(0,1),(1,0),(2,2)}")
    print("PASS: every accepted orbit pair has one relative S3 gain")
    print("PASS: hidden extension count at forced terminal gain = 4 for every row")
    print("PASS: full 18-state factor is a permutation with cycle type 2^6 3^2")
    print("PASS: transducer order = 6; fixed-state counts k=1..6 =", fixed)
    print("VERDICT: SMOOTH_TWISTED_ORBIT_WIRE_IS_A_RIGID_ORDER6_GAIN_TRANSDUCER")
    print("P_VS_NP=OPEN; P_EQUALS_NP_ALGORITHM=NOT_CONSTRUCTED; E8_D1=EMPTY")


if __name__ == "__main__":
    main()
