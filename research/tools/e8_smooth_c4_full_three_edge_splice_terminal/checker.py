#!/usr/bin/env python3
"""Exact replay for v8.1 full-three-edge-splice path/cycle terminal."""

from collections import Counter
from itertools import permutations, product

D = range(3)
S3 = list(permutations(D))
REPS = {
    0: (0, 1, 0, 1),
    1: (0, 1, 0, 2),
    2: (0, 1, 2, 1),
}
PORTS = (0, 2, 3)
PI = {0: 1, 1: 0, 2: 2}
H = {
    0: (0, 2, 1),
    1: (0, 2, 1),
    2: (1, 2, 0),
}
STATES = list(product(D, S3))
INDEX = {s: i for i, s in enumerate(STATES)}
N = len(STATES)
FULL_ROW = (1 << N) - 1


def compose_perm(p, q):
    return tuple(p[q[i]] for i in D)


def inverse_perm(p):
    out = [0, 0, 0]
    for i, v in enumerate(p):
        out[v] = i
    return tuple(out)


def F(state):
    tau, g = state
    return (PI[tau], compose_perm(g, inverse_perm(H[tau])))


def color(state, port):
    tau, g = state
    return g[REPS[tau][port]]


def permutation_relation(mapping):
    return tuple(1 << mapping[i] for i in range(N))


def transpose_relation(rel):
    out = [0] * N
    for i, row in enumerate(rel):
        x = row
        while x:
            low = x & -x
            j = low.bit_length() - 1
            out[j] |= 1 << i
            x -= low
    return tuple(out)


def compose_relation(first, second):
    """Existential composition: first then second."""
    out = []
    for row in first:
        z = 0
        x = row
        while x:
            low = x & -x
            j = low.bit_length() - 1
            z |= second[j]
            x -= low
        out.append(z)
    return tuple(out)


def relation_size(rel):
    return sum(row.bit_count() for row in rel)


def splice_relation(target_order):
    rows = [0] * N
    for i, left in enumerate(STATES):
        for j, right in enumerate(STATES):
            if all(
                color(left, p) != color(right, q)
                for p, q in zip(PORTS, target_order)
            ):
                rows[i] |= 1 << j
    return tuple(rows)


def build_generators():
    fmap = [INDEX[F(s)] for s in STATES]
    finv = [0] * N
    for i, j in enumerate(fmap):
        finv[j] = i
    F_rel = permutation_relation(fmap)
    Finv_rel = permutation_relation(finv)

    generators = []
    for target_order in permutations(PORTS):
        splice = splice_relation(target_order)
        for transfer in (F_rel, Finv_rel):
            step = compose_relation(splice, transfer)
            generators.append(step)
            generators.append(transpose_relation(step))
    return list(dict.fromkeys(generators))


def semigroup_closure(generators):
    seen = set(generators)
    frontier = list(generators)
    growth = [(0, len(seen), len(seen))]
    round_no = 0
    while frontier:
        round_no += 1
        new = []
        for a in frontier:
            for b in generators:
                for c in (compose_relation(a, b), compose_relation(b, a)):
                    if c not in seen:
                        seen.add(c)
                        new.append(c)
        growth.append((round_no, len(new), len(seen)))
        frontier = new
    return seen, growth


def main():
    assert N == 18
    generators = build_generators()
    assert len(generators) == 24
    assert Counter(map(relation_size, generators)) == Counter({84: 16, 132: 8})

    closure, growth = semigroup_closure(generators)
    assert growth == [
        (0, 24, 24),
        (1, 240, 264),
        (2, 8, 272),
        (3, 0, 272),
    ]
    assert len(closure) == 272

    expected_sizes = Counter({
        84: 16,
        132: 8,
        192: 40,
        240: 54,
        252: 80,
        264: 20,
        276: 40,
        300: 1,
        312: 6,
        318: 6,
        324: 1,
    })
    assert Counter(map(relation_size, closure)) == expected_sizes

    universal = tuple([FULL_ROW] * N)
    identity = tuple(1 << i for i in range(N))
    assert universal in closure
    assert identity not in closure

    fixed_diagonal = Counter(
        sum((rel[i] >> i) & 1 for i in range(N))
        for rel in closure
    )
    assert fixed_diagonal == Counter({18: 116, 6: 61, 12: 51, 0: 44})

    print("PASS: distinct oriented full-splice step generators = 24")
    print("PASS: generator size distribution = {84:16,132:8}")
    print("PASS: semigroup growth = 24 -> 264 -> 272 -> fixed point")
    print("PASS: exact closure size = 272")
    print("PASS: relation-size distribution =", dict(sorted(expected_sizes.items())))
    print("PASS: universal relation present; identity absent")
    print("PASS: cycle diagonal counts =", dict(sorted(fixed_diagonal.items())))
    print("VERDICT: FULL_THREE_EDGE_SPLICE_PATH_CYCLE_LANGUAGE_HAS_EXACT_POLYNOMIAL_TERMINAL")
    print("P_VS_NP=OPEN; P_EQUALS_NP_ALGORITHM=NOT_CONSTRUCTED; E8_D1=EMPTY")


if __name__ == "__main__":
    main()
