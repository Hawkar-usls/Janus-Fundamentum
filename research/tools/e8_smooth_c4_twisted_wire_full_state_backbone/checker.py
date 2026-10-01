#!/usr/bin/env python3
"""Exact replay for E8 v7.9 full-state C4 twisted-wire transport."""

from collections import Counter
from functools import lru_cache
from itertools import combinations, permutations
from math import lcm

D = range(3)
S3 = list(permutations(D))
ID = (0, 1, 2)
REPS = ((0, 1, 0, 1), (0, 1, 0, 2), (0, 1, 2, 1))
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


def compose(a, b):
    """Permutation function composition a o b."""
    return tuple(a[b[i]] for i in D)


def inverse(p):
    out = [0, 0, 0]
    for i, x in enumerate(p):
        out[x] = i
    return tuple(out)


@lru_cache(maxsize=None)
def compatibility_masks(bundle):
    masks = []
    for _, _, left_colours in STATES:
        mask = 0
        for j, (_, _, right_colours) in enumerate(STATES):
            if all(left_colours[p] != right_colours[q] for p, q in bundle):
                mask |= 1 << j
        masks.append(mask)
    return tuple(masks)


def comp_tables(bundles):
    return {
        pair: compatibility_masks(tuple(sorted(edges)))
        for pair, edges in bundles.items()
    }


def orbit_relation_from_tables(comp):
    relation = set()
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
                    if comp[(0, 3)][s0] & comp[(1, 3)][s1] & comp[(2, 3)][s2]:
                        accepted = True
                        break
                if accepted:
                    break
            if accepted:
                relation.add((tau0, tau1))
    return frozenset(relation)


def right_terminal_fibres(comp):
    """For g0=id return exact feasible full RHS states for each input orbit tau0."""
    fibres = {}
    for tau0 in D:
        s0 = ROOT_STATE[tau0]
        feasible = []
        for s1 in range(18):
            if not ((comp[(0, 1)][s0] >> s1) & 1):
                continue
            possible_s2 = comp[(0, 2)][s0] & comp[(1, 2)][s1]
            accepted = False
            while possible_s2:
                bit = possible_s2 & -possible_s2
                s2 = bit.bit_length() - 1
                possible_s2 -= bit
                if comp[(0, 3)][s0] & comp[(1, 3)][s1] & comp[(2, 3)][s2]:
                    accepted = True
                    break
            if accepted:
                feasible.append(s1)
        fibres[tau0] = tuple(feasible)
    return fibres


def rooted_smooth_words():
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
    bundles = {pair: [] for pair in PAIRS}
    for i in range(16):
        j = (i + 1) % 16
        a, b = word[i], word[j]
        pa, pb = ports[i], ports[j]
        if a < b:
            bundles[(a, b)].append((pa, pb))
        else:
            bundles[(b, a)].append((pb, pa))
    return bundles


def opened_three_cut(full, omitted):
    omitted = set(omitted)
    out = {pair: list(edges) for pair, edges in full.items()}
    out[(0, 1)] = [
        edge for i, edge in enumerate(full[(0, 1)])
        if i not in omitted
    ]
    return out


def state_cycle_type(pi, relative_gains):
    # h = gY^{-1} gX, so gY = gX o h^{-1}.
    def step(state):
        tau, g = state
        return pi[tau], compose(g, inverse(relative_gains[tau]))

    all_states = [(tau, g) for tau in D for g in S3]
    seen = set()
    lengths = []
    for start in all_states:
        if start in seen:
            continue
        cur = start
        n = 0
        while cur not in seen:
            seen.add(cur)
            n += 1
            cur = step(cur)
        lengths.append(n)
    return tuple(sorted(lengths))


EXPECTED_SIGNATURES = Counter({
    ((1,0,2), ((0,2,1),(0,2,1),(1,2,0))): 4,
    ((2,0,1), ((1,2,0),(1,2,0),(1,2,0))): 4,
    ((2,1,0), ((2,1,0),(1,2,0),(2,1,0))): 4,
    ((1,2,0), ((1,0,2),(2,1,0),(2,0,1))): 4,
    ((2,1,0), ((0,1,2),(2,0,1),(0,1,2))): 2,
    ((1,0,2), ((0,1,2),(0,1,2),(2,0,1))): 4,
    ((2,1,0), ((0,1,2),(1,2,0),(0,1,2))): 2,
    ((1,2,0), ((2,0,1),(2,1,0),(1,0,2))): 2,
    ((2,0,1), ((1,0,2),(1,0,2),(0,1,2))): 4,
    ((1,2,0), ((2,0,1),(0,2,1),(1,0,2))): 2,
})

EXPECTED_ORDER_DISTRIBUTION = Counter({3: 14, 6: 16, 9: 2})


def main():
    wire_count = 0
    gauge_branching = []
    signatures = Counter()
    order_distribution = Counter()
    explicit_seen = False

    for word in rooted_smooth_words():
        full = bundles_from_word(word)
        terminal_edges = full[(0, 1)]
        if len(terminal_edges) < 3:
            continue

        for omitted in combinations(range(len(terminal_edges)), 3):
            opened = opened_three_cut(full, omitted)
            comp = comp_tables(opened)
            relation = orbit_relation_from_tables(comp)

            pi = None
            for p, graph in PERM_RELATIONS.items():
                if relation == graph:
                    pi = p
                    break
            if pi is None:
                continue

            wire_count += 1
            fibres = right_terminal_fibres(comp)
            gains = []
            for tau in D:
                if len(fibres[tau]) != 1:
                    gauge_branching.append((word, omitted, pi, fibres))
                    break
                s1 = fibres[tau][0]
                tau1, g1, _ = STATES[s1]
                assert tau1 == pi[tau]
                # With g0=id, relative gain h=g1^{-1}.
                gains.append(inverse(g1))
            else:
                signature = (pi, tuple(gains))
                signatures[signature] += 1
                ctype = state_cycle_type(pi, tuple(gains))
                order_distribution[lcm(*ctype)] += 1

                if (
                    word == (0,1,0,1,0,1,2,3,2,3,0,1,2,3,2,3)
                    and omitted == (0,4,5)
                ):
                    explicit_seen = True
                    assert pi == (1,0,2)
                    assert tuple(gains) == ((0,2,1),(0,2,1),(1,2,0))
                    assert ctype == (2,2,2,2,2,2,3,3)

    assert wire_count == 32
    assert not gauge_branching
    assert signatures == EXPECTED_SIGNATURES, signatures
    assert order_distribution == EXPECTED_ORDER_DISTRIBUTION, order_distribution
    assert explicit_seen

    print("PASS: all 32 smooth v7.7 orbit-bijective openings replayed")
    print("PASS: gauge-branching wires = 0")
    print("PASS: distinct full 18-state transport signatures = 10")
    print("PASS: transport-order distribution = {3:14, 6:16, 9:2}")
    print("PASS: explicit v7.7 control lifts to cycle type 2^6 + 3^2 and order 6")
    print("VERDICT: PURE_TWISTED_WIRE_NETWORK_IS_A_FINITE_PERMUTATION_BACKBONE; HARDNESS_MUST_ENTER_ELSEWHERE")
    print("P_VS_NP=OPEN; P_EQUALS_NP_ALGORITHM=NOT_CONSTRUCTED; E8_D1=EMPTY")


if __name__ == "__main__":
    main()
