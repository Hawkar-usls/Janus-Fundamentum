#!/usr/bin/env python3
"""Exact replay for v7.5 capacity-respecting C4 interaction-tree EQ/NEQ barrier."""

from collections import Counter, defaultdict
from itertools import combinations, permutations, product

D = range(3)
S3 = list(permutations(D))
REPS = {
    0: (0, 1, 0, 1),
    1: (0, 1, 0, 2),
    2: (0, 1, 2, 1),
}
PORT_PAIRS = [(p, q) for p in range(4) for q in range(4)]
PAIR_INDEX = {(a, b): 3 * a + b for a in D for b in D}
ALL_REL = (1 << 9) - 1
EQ = sum(1 << PAIR_INDEX[(a, a)] for a in D)
NEQ = ALL_REL ^ EQ
ALL_UNARY = (1 << 3) - 1
ZERO_USAGE = (0, 0, 0, 0)


def addv(a, b):
    return tuple(x + y for x, y in zip(a, b))


def fits(v):
    return all(x <= 2 for x in v)


def valid_bundle(bundle):
    left = Counter(p for p, _ in bundle)
    right = Counter(q for _, q in bundle)
    return max(left.values(), default=0) <= 2 and max(right.values(), default=0) <= 2


def usage(bundle, side):
    k = 0 if side == "left" else 1
    return tuple(sum(1 for e in bundle if e[k] == i) for i in range(4))


def allowed_gains(a, b, bundle):
    out = []
    for h in S3:
        if all(h[REPS[a][p]] != REPS[b][q] for p, q in bundle):
            out.append(h)
    return out


def relmask(bundle):
    m = 0
    for a in D:
        for b in D:
            if allowed_gains(a, b, bundle):
                m |= 1 << PAIR_INDEX[(a, b)]
    return m


def compose(r, s):
    out = 0
    for a in D:
        for c in D:
            if any(
                (r & (1 << PAIR_INDEX[(a, b)]))
                and (s & (1 << PAIR_INDEX[(b, c)]))
                for b in D
            ):
                out |= 1 << PAIR_INDEX[(a, c)]
    return out


def filter_left(r, S):
    out = 0
    for a in D:
        for b in D:
            if (S & (1 << a)) and (r & (1 << PAIR_INDEX[(a, b)])):
                out |= 1 << PAIR_INDEX[(a, b)]
    return out


def filter_right(r, S):
    out = 0
    for a in D:
        for b in D:
            if (S & (1 << b)) and (r & (1 << PAIR_INDEX[(a, b)])):
                out |= 1 << PAIR_INDEX[(a, b)]
    return out


def preimage(r, S):
    out = 0
    for a in D:
        if any((S & (1 << b)) and (r & (1 << PAIR_INDEX[(a, b)])) for b in D):
            out |= 1 << a
    return out


def catalog():
    bundles = []
    masks = set()
    types = {}
    for r in range(1, 9):
        for bundle in combinations(PORT_PAIRS, r):
            if not valid_bundle(bundle):
                continue
            bundles.append(bundle)
            ld, rd, m = usage(bundle, "left"), usage(bundle, "right"), relmask(bundle)
            masks.add(m)
            types.setdefault((ld, rd, m), bundle)
    return bundles, masks, [(ld, rd, m, b) for (ld, rd, m), b in types.items()]


def path_closure(edge_types):
    by_ld = defaultdict(dict)
    all_rd = set()
    for ld, rd, m, bundle in edge_types:
        by_ld[ld].setdefault((rd, m), bundle)
        all_rd.add(rd)

    out_by_prev = {}
    for rp in all_rd:
        outs = set()
        for ld, md in by_ld.items():
            if not fits(addv(rp, ld)):
                continue
            outs.update(md.keys())
        out_by_prev[rp] = outs

    reach = {rd: set() for rd in all_rd}
    for ld, rd, m, bundle in edge_types:
        reach[rd].add(m)

    counts = [sum(map(len, reach.values()))]
    assert not any(EQ in s or NEQ in s for s in reach.values())

    for _ in range(10):
        new = {rd: set(ms) for rd, ms in reach.items()}
        for rp, masks in reach.items():
            for rd2, m2 in out_by_prev[rp]:
                for m1 in masks:
                    new[rd2].add(compose(m1, m2))
        counts.append(sum(map(len, new.values())))
        assert not any(EQ in s or NEQ in s for s in new.values())
        if counts[-1] == counts[-2]:
            return counts, new
        reach = new
    raise AssertionError("path closure failed to stabilize")


def rooted_unary_closure(edge_types):
    states = {ZERO_USAGE: {ALL_UNARY}}
    iteration_counts = [1]

    for _ in range(20):
        branches = set()
        for ld, rd, m, bundle in edge_types:
            for uc, sets in states.items():
                if not fits(addv(rd, uc)):
                    continue
                for S in sets:
                    branches.add((ld, preimage(m, S)))

        combined = {ZERO_USAGE: {ALL_UNARY}}
        changed = True
        while changed:
            changed = False
            snapshot = [(u, S) for u, sets in combined.items() for S in sets]
            for u, S in snapshot:
                for du, T in branches:
                    nu = addv(u, du)
                    if not fits(nu):
                        continue
                    nS = S & T
                    slot = combined.setdefault(nu, set())
                    if nS not in slot:
                        slot.add(nS)
                        changed = True

        old = sum(len(v) for v in states.values())
        for u, sets in combined.items():
            states.setdefault(u, set()).update(sets)
        new = sum(len(v) for v in states.values())
        iteration_counts.append(new)
        if new == old:
            return iteration_counts, states
    raise AssertionError("rooted unary closure failed to stabilize")


def all_unaries_within(states, cap):
    out = set()
    for u, sets in states.items():
        if all(u[i] <= cap[i] for i in range(4)):
            out.update(sets)
    return out


def two_terminal_tree_closure(edge_types, root_states):
    unary_by_cap = {
        cap: all_unaries_within(root_states, cap)
        for cap in product(range(3), repeat=4)
    }
    all_rd = {rd for _, rd, _, _ in edge_types}

    reach = defaultdict(set)
    for ld, rd, m, bundle in edge_types:
        cap = tuple(2 - x for x in ld)
        for S0 in unary_by_cap[cap]:
            reach[rd].add(filter_left(m, S0))

    trans = {}
    for rin in all_rd:
        opts = set()
        for ld, rd2, m2, bundle in edge_types:
            if not fits(addv(rin, ld)):
                continue
            cap = tuple(2 - rin[i] - ld[i] for i in range(4))
            for S in unary_by_cap[cap]:
                opts.add((S, rd2, m2))
        trans[rin] = opts

    final_unaries = {
        rin: unary_by_cap[tuple(2 - x for x in rin)]
        for rin in all_rd
    }

    def assert_no_target(current):
        for rin, rels in current.items():
            for r in rels:
                for S in final_unaries[rin]:
                    terminal = filter_right(r, S)
                    assert terminal != EQ
                    assert terminal != NEQ

    counts = []
    for _ in range(10):
        counts.append(sum(map(len, reach.values())))
        assert_no_target(reach)
        new = {rd: set(ms) for rd, ms in reach.items()}
        for rin, rels in reach.items():
            for S, rd2, m2 in trans[rin]:
                for r in rels:
                    new[rd2].add(compose(filter_right(r, S), m2))
        newcount = sum(map(len, new.values()))
        if newcount == counts[-1]:
            counts.append(newcount)
            assert_no_target(new)
            return counts, new
        reach = new
    raise AssertionError("binary tree closure failed to stabilize")


def main():
    bundles, masks, edge_types = catalog()
    assert len(bundles) == 7342
    assert len(masks) == 159
    assert len(edge_types) == 3377
    assert EQ not in masks
    assert NEQ not in masks

    path_counts, _ = path_closure(edge_types)
    assert path_counts == [998, 1578, 2569, 2748, 2895, 2895]

    unary_counts, root_states = rooted_unary_closure(edge_types)
    assert unary_counts == [1, 219, 298, 323, 323]
    assert sum(len(v) for v in root_states.values()) == 323
    assert {S for sets in root_states.values() for S in sets} == set(range(8))

    tree_counts, _ = two_terminal_tree_closure(edge_types, root_states)
    assert tree_counts == [1640, 2777, 3049, 3083, 3109, 3109]

    print("PASS: valid C4-C4 capacity bundles = 7342")
    print("PASS: distinct direct orbit relations = 159; EQ_3/NEQ_3 absent")
    print("PASS: path closure counts =", path_counts, "; EQ_3/NEQ_3 absent")
    print("PASS: rooted unary closure counts =", unary_counts, "; all 8 unary subsets reachable")
    print("PASS: full two-terminal tree closure counts =", tree_counts)
    print("PASS: EQ_3/NEQ_3 absent from every relaxed capacity-respecting C4 interaction tree")
    print("VERDICT: TREE_REPAIR_OF_ABSTRACT_PP_EQ_NEQ_IS_BLOCKED; CYCLES/HOLONOMY_REQUIRED")
    print("P_VS_NP=OPEN; P_EQUALS_NP_ALGORITHM=NOT_CONSTRUCTED; E8_D1=EMPTY")


if __name__ == "__main__":
    main()
