#!/usr/bin/env python3
"""Exact replay for v7.6.1 smooth-C4 triangle source correction."""

from collections import Counter
from itertools import permutations, product

D = range(3)
S3 = list(permutations(D))
ID = (0, 1, 2)
REPS = {
    0: (0, 1, 0, 1),
    1: (0, 1, 0, 2),
    2: (0, 1, 2, 1),
}
EQ = frozenset((i, i) for i in D)
NEQ = frozenset((i, j) for i in D for j in D if i != j)


def smooth_words():
    word = [0]
    counts = [3, 4, 4]

    def rec():
        if sum(counts) == 0:
            if word[-1] != word[0]:
                yield tuple(word)
            return
        last = word[-1]
        for x in D:
            if counts[x] and x != last:
                counts[x] -= 1
                word.append(x)
                yield from rec()
                word.pop()
                counts[x] += 1

    yield from rec()


def bundles_from_word(word):
    occ = [0, 0, 0]
    ports = []
    for x in word:
        ports.append(occ[x])
        occ[x] += 1
    assert occ == [4, 4, 4]

    bundles = {(0, 1): [], (0, 2): [], (1, 2): []}
    for i in range(12):
        j = (i + 1) % 12
        a, b = word[i], word[j]
        assert a != b
        pa, pb = ports[i], ports[j]
        if a < b:
            bundles[(a, b)].append((pa, pb))
        else:
            bundles[(b, a)].append((pb, pa))
    return bundles


def sat_bundle(t_a, g_a, t_b, g_b, bundle):
    ca = tuple(g_a[x] for x in REPS[t_a])
    cb = tuple(g_b[x] for x in REPS[t_b])
    return all(ca[p] != cb[q] for p, q in bundle)


def terminal_relation(bundles):
    out = set()
    for t0, t1 in product(D, repeat=2):
        accepted = False
        for t2 in D:
            for g1, g2 in product(S3, repeat=2):
                if (
                    sat_bundle(t0, ID, t1, g1, bundles[(0, 1)])
                    and sat_bundle(t0, ID, t2, g2, bundles[(0, 2)])
                    and sat_bundle(t1, g1, t2, g2, bundles[(1, 2)])
                ):
                    accepted = True
                    break
            if accepted:
                break
        if accepted:
            out.add((t0, t1))
    return frozenset(out)


def full_colouring_count(word):
    bundles = bundles_from_word(word)
    count = 0
    for t0, t1, t2 in product(D, repeat=3):
        for g0, g1, g2 in product(S3, repeat=3):
            if (
                sat_bundle(t0, g0, t1, g1, bundles[(0, 1)])
                and sat_bundle(t0, g0, t2, g2, bundles[(0, 2)])
                and sat_bundle(t1, g1, t2, g2, bundles[(1, 2)])
            ):
                count += 1
    return count


def usage(bundles):
    out = {0: [0] * 4, 1: [0] * 4, 2: [0] * 4}
    for (a, b), edges in bundles.items():
        for p, q in edges:
            out[a][p] += 1
            out[b][q] += 1
    return {k: tuple(v) for k, v in out.items()}


def dihedral_orders():
    base = (0, 1, 2, 3)
    orders = set()
    for shift in range(4):
        orders.add(tuple(base[(i + shift) % 4] for i in range(4)))
        orders.add(tuple(base[(shift - i) % 4] for i in range(4)))
    return orders


def main():
    # v7.6 saturated EQ control is Hamiltonian but not smooth at X and Z.
    eq_cycle = [
        ("X", 0), ("Z", 0), ("X", 2), ("Y", 3),
        ("X", 3), ("Y", 2), ("Z", 2), ("X", 1),
        ("Y", 1), ("Z", 3), ("Y", 0), ("Z", 1),
    ]
    orders = {name: tuple(p for n, p in eq_cycle if n == name) for name in "XYZ"}
    d4 = dihedral_orders()
    assert orders == {"X": (0, 2, 3, 1), "Y": (3, 2, 1, 0), "Z": (0, 2, 3, 1)}
    assert orders["X"] not in d4 and orders["Z"] not in d4 and orders["Y"] in d4

    words = list(smooth_words())
    assert len(words) == 268
    rels = [terminal_relation(bundles_from_word(w)) for w in words]
    assert len(set(rels)) == 73
    assert EQ not in rels
    assert NEQ not in rels

    size_dist = Counter(map(len, rels))
    assert size_dist == Counter({2: 80, 0: 72, 4: 40, 1: 30, 7: 24, 3: 8, 8: 8, 9: 6})

    permutation_counts = {}
    for p in permutations(D):
        graph = frozenset((a, p[a]) for a in D)
        permutation_counts[p] = sum(r == graph for r in rels)
    assert permutation_counts == {
        (0, 1, 2): 0,
        (0, 2, 1): 0,
        (1, 0, 2): 2,
        (1, 2, 0): 2,
        (2, 0, 1): 2,
        (2, 1, 0): 2,
    }

    twisted_word = (0, 1, 0, 2, 1, 0, 1, 2, 0, 2, 1, 2)
    twisted_rel = terminal_relation(bundles_from_word(twisted_word))
    assert twisted_rel == frozenset({(0, 1), (1, 0), (2, 2)})
    assert full_colouring_count(twisted_word) == 24

    open_bundles = {
        (0, 1): [(0, 0), (1, 0), (1, 1)],
        (0, 2): [(2, 0), (3, 0)],
        (1, 2): [(2, 1), (2, 2), (3, 2), (3, 3)],
    }
    assert terminal_relation(open_bundles) == frozenset({(0, 2), (1, 0), (2, 1)})
    u = usage(open_bundles)
    assert u == {0: (1, 2, 1, 1), 1: (2, 1, 2, 2), 2: (2, 1, 2, 1)}
    free = {k: tuple(2 - x for x in v) for k, v in u.items()}
    assert free == {0: (1, 0, 1, 1), 1: (0, 1, 0, 0), 2: (0, 1, 0, 1)}

    print("PASS: v7.6 EQ control port orders X/Z are non-dihedral; smooth claim corrected")
    print("PASS: smooth rooted C12 words = 268; distinct terminal orbit relations = 73")
    print("PASS: saturated smooth three-C4 EQ_3/NEQ_3 are absent")
    print("PASS: exact bijective smooth controls = 8 rooted words across four nontrivial permutations")
    print("PASS: closed twisted witness has 24 proper 3-colourings")
    print("PASS: 9-edge open-port twisted relation = {(0,2),(1,0),(2,1)} with free half-edge totals 3/1/2")
    print("VERDICT: PRESERVE_NONSELFCROSSING_SOURCE_ORDER; FOURPLUS_SMOOTH_SPLICE_REQUIRED")
    print("P_VS_NP=OPEN; P_EQUALS_NP_ALGORITHM=NOT_CONSTRUCTED; E8_D1=EMPTY")


if __name__ == "__main__":
    main()
