#!/usr/bin/env python3
"""Exact exhaustive replay for E8 v7.7 smooth four-C4 open orbit wires."""

from collections import Counter
from functools import lru_cache
from itertools import combinations, permutations

D = range(3)
S3 = list(permutations(D))
ID = (0, 1, 2)
REPS = (
    (0, 1, 0, 1),
    (0, 1, 0, 2),
    (0, 1, 2, 1),
)
PAIRS = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))

STATES = []
for tau in D:
    for g in S3:
        STATES.append((tau, g, tuple(g[c] for c in REPS[tau])))

STATE_BY_TAU = {
    tau: tuple(i for i, (t, _, _) in enumerate(STATES) if t == tau)
    for tau in D
}
ROOT_STATE = {
    tau: next(i for i, (t, g, _) in enumerate(STATES) if t == tau and g == ID)
    for tau in D
}
PERM_RELATIONS = {
    p: frozenset((a, p[a]) for a in D)
    for p in permutations(D)
}


@lru_cache(maxsize=None)
def compatibility_masks(bundle):
    """For a fixed oriented port bundle, bitmask compatible RHS states per LHS state."""
    masks = []
    for _, _, left_colours in STATES:
        mask = 0
        for j, (_, _, right_colours) in enumerate(STATES):
            if all(left_colours[p] != right_colours[q] for p, q in bundle):
                mask |= 1 << j
        masks.append(mask)
    return tuple(masks)


def exact_terminal_relation(bundles):
    comp = {
        pair: compatibility_masks(tuple(sorted(edges)))
        for pair, edges in bundles.items()
    }
    relation = set()

    # Global S3 colour symmetry lets us fix component 0 gauge to identity.
    for tau0 in D:
        s0 = ROOT_STATE[tau0]
        for tau1 in D:
            accepted = False
            for s1 in STATE_BY_TAU[tau1]:
                if not ((comp[(0, 1)][s0] >> s1) & 1):
                    continue

                possible_s2 = comp[(0, 2)][s0] & comp[(1, 2)][s1]
                while possible_s2:
                    bit = possible_s2 & -possible_s2
                    s2 = bit.bit_length() - 1
                    possible_s2 -= bit

                    possible_s3 = (
                        comp[(0, 3)][s0]
                        & comp[(1, 3)][s1]
                        & comp[(2, 3)][s2]
                    )
                    if possible_s3:
                        accepted = True
                        break

                if accepted:
                    break

            if accepted:
                relation.add((tau0, tau1))

    return frozenset(relation)


def rooted_smooth_words():
    """All rooted smooth C16 component words, multiplicity four per component."""
    word = [0]
    remaining = [3, 4, 4, 4]

    def rec():
        if sum(remaining) == 0:
            if word[-1] != word[0]:
                yield tuple(word)
            return

        last = word[-1]
        for x in range(4):
            if remaining[x] and x != last:
                remaining[x] -= 1
                word.append(x)
                yield from rec()
                word.pop()
                remaining[x] += 1

    yield from rec()


def bundles_from_word(word):
    occurrence = [0, 0, 0, 0]
    ports = []
    for x in word:
        ports.append(occurrence[x])
        occurrence[x] += 1
    assert occurrence == [4, 4, 4, 4]

    bundles = {pair: [] for pair in PAIRS}
    for i in range(16):
        j = (i + 1) % 16
        a, b = word[i], word[j]
        assert a != b
        pa, pb = ports[i], ports[j]
        if a < b:
            bundles[(a, b)].append((pa, pb))
        else:
            bundles[(b, a)].append((pb, pa))
    return bundles


def opened_bundles(full_bundles, omitted_indices):
    omitted = set(omitted_indices)
    out = {pair: list(edges) for pair, edges in full_bundles.items()}
    out[(0, 1)] = [
        edge for i, edge in enumerate(full_bundles[(0, 1)])
        if i not in omitted
    ]
    return out


def classify_all():
    stats = {
        k: {
            "tested": 0,
            "sizes": Counter(),
            "relations": set(),
            "perms": Counter(),
        }
        for k in range(2, 8)
    }
    word_count = 0

    for word in rooted_smooth_words():
        word_count += 1
        full = bundles_from_word(word)
        terminal_edges = full[(0, 1)]

        for k in range(2, min(7, len(terminal_edges)) + 1):
            bucket = stats[k]
            for omitted in combinations(range(len(terminal_edges)), k):
                relation = exact_terminal_relation(opened_bundles(full, omitted))
                bucket["tested"] += 1
                bucket["sizes"][len(relation)] += 1
                bucket["relations"].add(relation)
                for p, graph in PERM_RELATIONS.items():
                    if relation == graph:
                        bucket["perms"][p] += 1

    return word_count, stats


def verify_positive_control():
    word = (0, 1, 0, 1, 0, 1, 2, 3, 2, 3, 0, 1, 2, 3, 2, 3)
    full = bundles_from_word(word)
    assert full[(0, 1)] == [
        (0, 0),
        (1, 0),
        (1, 1),
        (2, 1),
        (2, 2),
        (3, 3),
    ]

    opened = opened_bundles(full, (0, 4, 5))
    assert opened == {
        (0, 1): [(1, 0), (1, 1), (2, 1)],
        (0, 2): [],
        (0, 3): [(3, 1), (0, 3)],
        (1, 2): [(2, 0), (3, 2)],
        (1, 3): [],
        (2, 3): [(0, 0), (1, 0), (1, 1), (2, 2), (3, 2), (3, 3)],
    }
    assert exact_terminal_relation(opened) == PERM_RELATIONS[(1, 0, 2)]

    # Every removed 0--1 edge gives one free H half-edge at each terminal.
    free = {0: [0, 0, 0, 0], 1: [0, 0, 0, 0]}
    for i in (0, 4, 5):
        p, q = full[(0, 1)][i]
        free[0][p] += 1
        free[1][q] += 1
    assert free == {0: [1, 0, 1, 1], 1: [1, 0, 1, 1]}

    # Hidden components are saturated because no deleted edge touches 2 or 3.
    usage = {2: [0, 0, 0, 0], 3: [0, 0, 0, 0]}
    for (a, b), edges in opened.items():
        for p, q in edges:
            if a in usage:
                usage[a][p] += 1
            if b in usage:
                usage[b][q] += 1
    assert usage == {2: [2, 2, 2, 2], 3: [2, 2, 2, 2]}


EXPECTED = {
    2: {
        "tested": 1227600,
        "sizes": {0:3760,1:4224,2:12384,3:32944,4:28136,5:54256,6:83744,7:167128,8:171728,9:669296},
        "perms": {},
    },
    3: {
        "tested": 596016,
        "sizes": {0:3760,1:608,2:1328,3:6592,4:4688,5:11632,6:16864,7:42320,8:39696,9:468528},
        "unique": 300,
        "perms": {(1,0,2):8,(1,2,0):8,(2,0,1):8,(2,1,0):8},
    },
    4: {
        "tested": 145824,
        "sizes": {0:2960,3:528,4:480,5:1296,6:2240,7:4628,8:3360,9:130332},
        "unique": 86,
        "perms": {},
    },
    5: {
        "tested": 17424,
        "sizes": {0:1296,4:64,6:160,8:160,9:15744},
        "unique": 14,
        "perms": {},
    },
    6: {
        "tested": 912,
        "sizes": {0:272,9:640},
        "unique": 2,
        "perms": {},
    },
    7: {
        "tested": 16,
        "sizes": {0:16},
        "unique": 1,
        "perms": {},
    },
}


def main():
    verify_positive_control()
    word_count, stats = classify_all()
    assert word_count == 455058

    for k, expected in EXPECTED.items():
        actual = stats[k]
        assert actual["tested"] == expected["tested"], (k, actual["tested"])
        assert dict(sorted(actual["sizes"].items())) == expected["sizes"], k
        assert dict(actual["perms"]) == expected["perms"], (k, actual["perms"])
        if "unique" in expected:
            assert len(actual["relations"]) == expected["unique"], (k, len(actual["relations"]))

    print("PASS: rooted smooth four-C4 Hamiltonian words = 455058")
    print("PASS: k=2 openings = 1227600 and exact orbit bijections = 0")
    print("PASS: k=3 openings = 596016; exact orbit bijections = 32")
    print("PASS: k=3 bijections are 8 copies each of four nontrivial permutations")
    print("PASS: k=4..7 exact orbit bijections = 0 with frozen relation catalogs")
    print("PASS: explicit smooth positive control has relation {(0,1),(1,0),(2,2)}")
    print("PASS: explicit control leaves three H half-edges free on each terminal and saturates both hidden C4s")
    print("VERDICT: THREE_CUT_SMOOTH_OPEN_TWISTED_ORBIT_WIRE_EXISTS; SPLICE_PRESERVATION_OPEN")
    print("P_VS_NP=OPEN; P_EQUALS_NP_ALGORITHM=NOT_CONSTRUCTED; E8_D1=EMPTY")


if __name__ == "__main__":
    main()
