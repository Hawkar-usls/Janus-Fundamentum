#!/usr/bin/env python3
"""Exact structural checker for the R5 E12 RXC3 -> linear cubic Exact-One bridge.

Dependency-free checks:
  * exhaustively enumerates every local gadget exact-cover state;
  * verifies there are exactly eight such states;
  * verifies the only boundary signatures are EMPTY, C, C', C union C';
  * builds a nontrivial 6-element 3-uniform 3-regular RXC3 fixture;
  * applies the full reduction;
  * verifies target square / 3-uniform / 3-regular / linear properties.

The finite checker supports, but does not replace, the symbolic reduction proof.
"""

from collections import Counter
from itertools import combinations


def local_gadget(prefix="g"):
    """Return (triples, internal_elements, boundary_elements) for one gadget."""
    x = [f"{prefix}:x{i}" for i in range(1, 4)]
    xp = [f"{prefix}:xp{i}" for i in range(1, 4)]
    z = [f"{prefix}:z{i}" for i in range(1, 7)]
    zp = [f"{prefix}:zp{i}" for i in range(1, 7)]
    t = [f"{prefix}:t{i}" for i in range(1, 4)]

    triples = {
        "L1": {x[0], z[0], z[3]},
        "L2": {x[1], z[1], z[4]},
        "L3": {x[2], z[2], z[5]},
        "L4": {z[0], z[1], z[2]},
        "L5": {z[3], z[4], z[5]},
        "Lp1": {xp[0], zp[0], zp[3]},
        "Lp2": {xp[1], zp[1], zp[4]},
        "Lp3": {xp[2], zp[2], zp[5]},
        "Lp4": {zp[0], zp[1], zp[2]},
        "Lp5": {zp[3], zp[4], zp[5]},
        "D1": {z[1], z[5], t[0]},
        "D2": {z[2], z[3], t[1]},
        "D3": {z[0], z[4], t[2]},
        "D4": {zp[1], zp[5], t[1]},
        "D5": {zp[2], zp[3], t[2]},
        "D6": {zp[0], zp[4], t[0]},
        "D7": {t[0], t[1], t[2]},
    }
    internal = set(z + zp + t)
    boundary = set(x + xp)
    return triples, internal, boundary, tuple(x), tuple(xp)


def enumerate_local_states():
    triples, internal, boundary, x, xp = local_gadget()
    names = list(triples)
    states = []

    for mask in range(1 << len(names)):
        counts = Counter()
        chosen = []
        for j, name in enumerate(names):
            if (mask >> j) & 1:
                chosen.append(name)
                counts.update(triples[name])

        if not all(counts[e] == 1 for e in internal):
            continue
        if not all(counts[e] <= 1 for e in boundary):
            continue

        signature = frozenset(e for e in boundary if counts[e] == 1)
        states.append((tuple(chosen), signature))

    assert len(states) == 8

    allowed = {
        frozenset(),
        frozenset(x),
        frozenset(xp),
        frozenset(x + xp),
    }
    got = {sig for _, sig in states}
    assert got == allowed

    # Strong grouping property: no nonempty proper subset of either triple appears.
    for _, sig in states:
        ux = sig & set(x)
        up = sig & set(xp)
        assert len(ux) in (0, 3)
        assert len(up) in (0, 3)

    return states


def rx_fixture():
    """A 6x6 3-uniform, 3-regular source fixture."""
    q = 6
    sets = []
    for i in range(q):
        sets.append(((i + 0) % q, (i + 1) % q, (i + 3) % q))

    assert all(len(set(C)) == 3 for C in sets)
    deg = Counter(v for C in sets for v in C)
    assert set(deg) == set(range(q))
    assert all(deg[v] == 3 for v in range(q))
    assert len(sets) == q
    return q, sets


def transform_rx(q, source_sets):
    """Full R5 E12 construction as a set system."""
    target = []

    # Global boundary copies.
    x = [f"x:{i}" for i in range(q)]
    xp = [f"xp:{i}" for i in range(q)]

    for j, C in enumerate(source_sets):
        a, b, c = C
        bx = [x[a], x[b], x[c]]
        bxp = [xp[a], xp[b], xp[c]]
        z = [f"g{j}:z{i}" for i in range(1, 7)]
        zp = [f"g{j}:zp{i}" for i in range(1, 7)]
        t = [f"g{j}:t{i}" for i in range(1, 4)]

        L = [
            {bx[0], z[0], z[3]},
            {bx[1], z[1], z[4]},
            {bx[2], z[2], z[5]},
            {z[0], z[1], z[2]},
            {z[3], z[4], z[5]},
        ]
        Lp = [
            {bxp[0], zp[0], zp[3]},
            {bxp[1], zp[1], zp[4]},
            {bxp[2], zp[2], zp[5]},
            {zp[0], zp[1], zp[2]},
            {zp[3], zp[4], zp[5]},
        ]
        D = [
            {z[1], z[5], t[0]},
            {z[2], z[3], t[1]},
            {z[0], z[4], t[2]},
            {zp[1], zp[5], t[1]},
            {zp[2], zp[3], t[2]},
            {zp[0], zp[4], t[0]},
            {t[0], t[1], t[2]},
        ]
        target.extend(L + Lp + D)

    return target


def check_target_structure(q, source_sets, target):
    universe = set().union(*target)

    # 17q target elements and 17q target triples.
    assert len(universe) == 17 * q
    assert len(target) == 17 * q

    # 3-uniform.
    assert all(len(T) == 3 for T in target)

    # 3-regular.
    degree = Counter(v for T in target for v in T)
    assert set(degree) == universe
    assert all(degree[v] == 3 for v in universe)

    # Linear: no two target triples share two elements.
    for i, j in combinations(range(len(target)), 2):
        assert len(target[i] & target[j]) <= 1

    # Incidence double count sanity.
    assert sum(map(len, target)) == 3 * len(universe)


def main():
    states = enumerate_local_states()
    q, source = rx_fixture()
    target = transform_rx(q, source)
    check_target_structure(q, source, target)

    print("R5 E12 hardness-gadget controls: PASS")
    print(f"local exact-cover states = {len(states)}")
    print("boundary signatures = EMPTY / C / C' / C+C' only")
    print(
        f"fixture: source={q} elements/{q} triples -> "
        f"target={17*q} elements/{17*q} triples"
    )
    print("target invariants: 3-uniform, 3-regular, linear, square")


if __name__ == "__main__":
    main()
