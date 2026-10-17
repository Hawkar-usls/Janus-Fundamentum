#!/usr/bin/env python3
"""Exact finite replay for v7.4 rigid NEQ Euler/port capacity obstruction."""

from collections import Counter
from itertools import combinations, permutations

D = range(3)
S3 = list(permutations(D))
REPS = {
    0: (0, 1, 0, 1),
    1: (0, 1, 0, 2),
    2: (0, 1, 2, 1),
}
PORT_PAIRS = [(p, q) for p in range(4) for q in range(4)]
PAIR_INDEX = {(a, b): 3 * a + b for a in D for b in D}
ALL_MASK = (1 << 9) - 1
EQ_MASK = sum(1 << PAIR_INDEX[(a, a)] for a in D)
NEQ_MASK = ALL_MASK ^ EQ_MASK
EXPECTED_MIN_COST_PROFILE = {3: 1, 4: 27, 5: 56, 6: 26, 7: 8, 8: 2}
EXPECTED_PATH_STATE_COUNTS = {1: 120, 2: 62, 3: 105, 4: 110, 5: 110}


def valid_bundle(bundle):
    left = Counter(p for p, _ in bundle)
    right = Counter(q for _, q in bundle)
    return max(left.values(), default=0) <= 2 and max(right.values(), default=0) <= 2


def gains(ta, tb, bundle):
    out = []
    for hi, h in enumerate(S3):
        if all(h[REPS[ta][p]] != REPS[tb][q] for p, q in bundle):
            out.append(hi)
    return tuple(out)


def orbit_rigid(bundle):
    saw = False
    for a in D:
        for b in D:
            g = gains(a, b, bundle)
            if g:
                saw = True
                if len(g) != 1:
                    return False
    return saw


def relation_mask(bundle):
    mask = 0
    for a in D:
        for b in D:
            if gains(a, b, bundle):
                mask |= 1 << PAIR_INDEX[(a, b)]
    return mask


def compose(rmask, smask):
    out = 0
    for a in D:
        for c in D:
            if any(
                (rmask & (1 << PAIR_INDEX[(a, b)]))
                and (smask & (1 << PAIR_INDEX[(b, c)]))
                for b in D
            ):
                out |= 1 << PAIR_INDEX[(a, c)]
    return out


def minimum_rigid_costs():
    min_cost = {}
    example = {}
    for r in range(1, 9):
        for bundle in combinations(PORT_PAIRS, r):
            if not valid_bundle(bundle) or not orbit_rigid(bundle):
                continue
            rel = relation_mask(bundle)
            if rel not in min_cost or r < min_cost[rel]:
                min_cost[rel] = r
                example[rel] = bundle
    assert len(min_cost) == 120
    return min_cost, example


def three_atom_capacity_search(min_cost):
    items = list(min_cost.items())
    witnesses = []
    for rmask, cr in items:
        for smask, cs in items:
            if cr + cs > 8:
                continue
            for tmask, ct in items:
                if cr + ct > 8 or cs + ct > 8:
                    continue
                if (rmask & compose(smask, tmask)) == NEQ_MASK:
                    witnesses.append((rmask, smask, tmask, cr, cs, ct))
    return witnesses


def path_states(min_cost, length):
    # State key is (current composed relation, last atom cost).
    # The key contains everything needed for one further transition.
    level = {(rel, cost) for rel, cost in min_cost.items()}
    if length == 1:
        return level
    for _ in range(2, length + 1):
        nxt = set()
        for current, last_cost in level:
            for rel, cost in min_cost.items():
                if last_cost + cost <= 8:
                    nxt.add((compose(current, rel), cost))
        level = nxt
    return level


def main():
    min_cost, examples = minimum_rigid_costs()
    profile = Counter(min_cost.values())
    assert dict(sorted(profile.items())) == EXPECTED_MIN_COST_PROFILE

    # The displayed v7.3 certificate costs 4,6,6 and therefore loads its
    # three factor nodes by 10,10,12 > 8.
    assert 4 + 6 > 8 and 4 + 6 > 8 and 6 + 6 > 8

    witnesses = three_atom_capacity_search(min_cost)
    assert witnesses == []

    levels = {k: path_states(min_cost, k) for k in range(1, 6)}
    counts = {k: len(v) for k, v in levels.items()}
    assert counts == EXPECTED_PATH_STATE_COUNTS
    assert all(current != NEQ_MASK for current, _ in levels[1])
    assert all(current != NEQ_MASK for current, _ in levels[2])
    assert all(current != NEQ_MASK for current, _ in levels[3])
    assert all(current != NEQ_MASK for current, _ in levels[4])
    assert levels[4] == levels[5]

    # Since the transition operator depends only on the state key and the
    # fixed 120-atom catalog, equality L4=L5 proves this is a fixed point.
    one_more = set()
    for current, last_cost in levels[5]:
        for rel, cost in min_cost.items():
            if last_cost + cost <= 8:
                one_more.add((compose(current, rel), cost))
    assert one_more == levels[5]
    assert all(current != NEQ_MASK for current, _ in one_more)

    print("PASS: minimum rigid relation cost profile =", dict(sorted(profile.items())))
    print("PASS: no capacity-feasible R AND (S o T) certificate for NEQ_3")
    print("PASS: path state counts =", counts)
    print("PASS: path state set stabilizes at length 4 with no NEQ_3")
    print("VERDICT: ABSTRACT_RIGID_PP_COMPLETENESS_DOES_NOT_DIRECTLY_EMBED_THROUGH_C4_PORT_CAPACITY")
    print("FIREWALL: branching/cyclic/copy gadgets and non-rigid bundles remain open")
    print("P_VS_NP=OPEN; P_EQUALS_NP_ALGORITHM=NOT_CONSTRUCTED; E8_D1=EMPTY")


if __name__ == "__main__":
    main()
