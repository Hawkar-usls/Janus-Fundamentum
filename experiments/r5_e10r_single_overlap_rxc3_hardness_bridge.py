#!/usr/bin/env python3
"""R5 E10R — exact hardness bridge into square linear-cubic Exact-One.

Clean-room verification of a constant gadget reduction from RX3C to the
restricted Exact-One source class used by the Gram/Hoffman frontier:

    square incidence matrix
    every row has weight 3
    every column has weight 3
    any two columns overlap in at most one row

The local gadget is adapted from the SINGLE OVERLAP RX3C construction
posted by Marzio De Biasi, but all properties used here are rechecked
independently by exact enumeration and by explicit source/target replay.

Claim ceiling: this establishes NP-hardness of the target source class
assuming the standard NP-completeness of RX3C.  It does NOT establish a
polynomial solver and therefore does NOT establish P=NP.
"""

from __future__ import annotations

from itertools import combinations, product
import json


def gadget_edges(j, old=("a", "b", "c")):
    x1, x2, x3 = [("x", u) for u in old]
    p1, p2, p3 = [("xp", u) for u in old]
    z = [("z", j, i) for i in range(1, 7)]
    zp = [("zp", j, i) for i in range(1, 7)]
    t = [("t", j, i) for i in range(1, 4)]

    return {
        "L1": {x1, z[0], z[3]},
        "L2": {x2, z[1], z[4]},
        "L3": {x3, z[2], z[5]},
        "L4": {z[0], z[1], z[2]},
        "L5": {z[3], z[4], z[5]},
        "L1p": {p1, zp[0], zp[3]},
        "L2p": {p2, zp[1], zp[4]},
        "L3p": {p3, zp[2], zp[5]},
        "L4p": {zp[0], zp[1], zp[2]},
        "L5p": {zp[3], zp[4], zp[5]},
        "D1": {z[1], z[5], t[0]},
        "D2": {z[2], z[3], t[1]},
        "D3": {z[0], z[4], t[2]},
        "D4": {zp[1], zp[5], t[1]},
        "D5": {zp[2], zp[3], t[2]},
        "D6": {zp[0], zp[4], t[0]},
        "D7": {t[0], t[1], t[2]},
    }


def local_internal_vertices(j=0):
    return (
        {("z", j, i) for i in range(1, 7)}
        | {("zp", j, i) for i in range(1, 7)}
        | {("t", j, i) for i in range(1, 4)}
    )


def enumerate_local_internal_covers():
    E = gadget_edges(0)
    names = list(E)
    I = local_internal_vertices(0)
    out = []
    for mask in range(1 << len(names)):
        count = {v: 0 for v in I}
        chosen = []
        ok = True
        for k, name in enumerate(names):
            if not ((mask >> k) & 1):
                continue
            chosen.append(name)
            for v in E[name] & I:
                count[v] += 1
                if count[v] > 1:
                    ok = False
                    break
            if not ok:
                break
        if ok and all(c == 1 for c in count.values()):
            out.append(tuple(chosen))
    return out


def local_mode(chosen):
    C = set(chosen)
    return (
        tuple(int(f"L{i}" in C) for i in (1, 2, 3)),
        tuple(int(f"L{i}p" in C) for i in (1, 2, 3)),
    )


def transform_rxc3(universe, triples):
    universe = tuple(universe)
    triples = [tuple(e) for e in triples]
    # RX3C preconditions used by the reduction.
    assert all(len(set(e)) == 3 for e in triples)
    assert len(triples) == len(universe)
    degree = {u: 0 for u in universe}
    for e in triples:
        for u in e:
            degree[u] += 1
    assert set(degree.values()) == {3}

    target_edges = []
    provenance = []
    for j, e in enumerate(triples):
        G = gadget_edges(j, e)
        for name, edge in G.items():
            target_edges.append(frozenset(edge))
            provenance.append((j, name))

    vertices = set().union(*target_edges)
    return vertices, target_edges, provenance


def exact_cover(edges, vertices):
    """One exact cover by recursive minimum-column branching, or None."""
    incidence = {v: [] for v in vertices}
    for i, e in enumerate(edges):
        for v in e:
            incidence[v].append(i)

    active_vertices = set(vertices)
    active_edges = set(range(len(edges)))

    def rec(V, E, chosen):
        if not V:
            return tuple(chosen)
        v = min(V, key=lambda x: sum(i in E for i in incidence[x]))
        options = [i for i in incidence[v] if i in E]
        if not options:
            return None
        for i in options:
            e = edges[i]
            if not e <= V:
                continue
            conflict = set()
            for u in e:
                conflict.update(j for j in incidence[u] if j in E)
            ans = rec(V - set(e), E - conflict, chosen + [i])
            if ans is not None:
                return ans
        return None

    return rec(active_vertices, active_edges, [])


def source_exact_cover(universe, triples):
    universe = set(universe)
    for r in range(len(triples) + 1):
        for idxs in combinations(range(len(triples)), r):
            covered = set()
            good = True
            for i in idxs:
                e = set(triples[i])
                if covered & e:
                    good = False
                    break
                covered |= e
            if good and covered == universe:
                return tuple(idxs)
    return None


def target_class_checks(vertices, edges):
    assert all(len(e) == 3 for e in edges)
    deg = {v: 0 for v in vertices}
    for e in edges:
        for v in e:
            deg[v] += 1
    assert set(deg.values()) == {3}
    assert len(vertices) == len(edges)
    assert all(len(edges[i] & edges[j]) <= 1
               for i, j in combinations(range(len(edges)), 2))


def decode_original_cover(edges, provenance, cover):
    selected = set(cover)
    chosen_gadgets = []
    by_gadget = {}
    for i in selected:
        j, name = provenance[i]
        by_gadget.setdefault(j, set()).add(name)
    for j, names in by_gadget.items():
        bits = tuple(int(f"L{i}" in names) for i in (1, 2, 3))
        assert bits in ((0, 0, 0), (1, 1, 1))
        if bits == (1, 1, 1):
            chosen_gadgets.append(j)
    return tuple(sorted(chosen_gadgets))


def replay_instance(universe, triples):
    src = source_exact_cover(universe, triples)
    V, E, P = transform_rxc3(universe, triples)
    target_class_checks(V, E)
    tgt = exact_cover(E, V)
    assert (src is not None) == (tgt is not None)
    decoded = None
    if tgt is not None:
        decoded = decode_original_cover(E, P, tgt)
        covered = set()
        for j in decoded:
            assert not (covered & set(triples[j]))
            covered |= set(triples[j])
        assert covered == set(universe)
    return {
        "source_yes": src is not None,
        "source_cover": src,
        "target_yes": tgt is not None,
        "decoded_cover": decoded,
        "source_vertices": len(universe),
        "target_vertices": len(V),
        "target_edges": len(E),
    }


def main():
    # Exact constant-gadget truth table over all 2^17 local edge selections.
    covers = enumerate_local_internal_covers()
    assert len(covers) == 8
    modes = [local_mode(c) for c in covers]
    assert all(a in ((0, 0, 0), (1, 1, 1)) for a, _ in modes)
    assert all(b in ((0, 0, 0), (1, 1, 1)) for _, b in modes)
    assert set(modes) == {
        ((0, 0, 0), (0, 0, 0)),
        ((0, 0, 0), (1, 1, 1)),
        ((1, 1, 1), (0, 0, 0)),
        ((1, 1, 1), (1, 1, 1)),
    }

    # Two nontrivial RX3C controls on six elements: one YES, one NO.
    U = tuple(range(6))
    yes = [
        (0, 1, 2), (0, 1, 3), (0, 1, 4),
        (2, 3, 5), (2, 4, 5), (3, 4, 5),
    ]
    no = [
        (0, 1, 2), (0, 1, 3), (0, 4, 5),
        (1, 4, 5), (2, 3, 4), (2, 3, 5),
    ]
    yes_report = replay_instance(U, yes)
    no_report = replay_instance(U, no)
    assert yes_report["source_yes"] and yes_report["target_yes"]
    assert not no_report["source_yes"] and not no_report["target_yes"]

    # For an RX3C source with N elements/sets, the target has 17N of each.
    assert yes_report["target_vertices"] == 17 * len(U)
    assert yes_report["target_edges"] == 17 * len(U)

    print(json.dumps({
        "status": "PASS",
        "claim_ceiling": "P_VS_NP_OPEN",
        "bridge": "RX3C_TO_SQUARE_LINEAR_CUBIC_EXACT_ONE",
        "local_gadget_internal_exact_covers": len(covers),
        "local_port_modes": sorted(set(map(str, modes))),
        "all_or_none_unprimed": True,
        "all_or_none_primed": True,
        "target_properties": {
            "uniformity": 3,
            "regularity": 3,
            "linear": True,
            "square": True,
        },
        "blowup": "N -> 17N vertices and 17N triples",
        "YES_control": yes_report,
        "NO_control": no_report,
        "consequence": (
            "A polynomial solver for this exact target class would imply P=NP; "
            "no such solver is established here."
        ),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
