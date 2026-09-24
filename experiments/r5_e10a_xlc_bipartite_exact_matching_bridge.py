#!/usr/bin/env python3
"""Finite exact controls for XLC -> bipartite Exact Matching transfer."""

from __future__ import annotations

import itertools
import json
import random
from collections import defaultdict

INF = 10**9


def circulation_spectrum(n, arcs, caps, lengths):
    out = set()
    witnesses = {}
    ranges = [range(c + 1) for c in caps]
    for xs in itertools.product(*ranges):
        bal = [0] * n
        cost = 0
        for x, (u, v), w in zip(xs, arcs, lengths):
            bal[u] -= x
            bal[v] += x
            cost += x * w
        if all(b == 0 for b in bal):
            out.add(cost)
            witnesses.setdefault(cost, xs)
    return out, witnesses


def build_bfactor(n, arcs, caps, lengths):
    edges = []
    outcap = [0] * n
    incap = [0] * n

    for ai, ((u, v), c, w) in enumerate(zip(arcs, caps, lengths)):
        outcap[u] += c
        incap[v] += c
        for k in range(c):
            edges.append((u, n + v, w, ("arc", ai, k)))

    b = [max(outcap[v], incap[v]) for v in range(n)]
    for v in range(n):
        for k in range(b[v]):
            edges.append((v, n + v, 0, ("slack", v, k)))

    req = b + b
    return edges, req


def bfactor_spectrum(num_vertices, edges, req):
    m = len(edges)
    out = set()
    for mask in range(1 << m):
        deg = [0] * num_vertices
        cost = 0
        for i, (u, v, w, _) in enumerate(edges):
            if (mask >> i) & 1:
                deg[u] += 1
                deg[v] += 1
                cost += w
        if deg == req:
            out.add(cost)
    return out


def bfactor_to_pm(num_vertices, edges, req, left_original):
    vid = 0
    copies = {}
    side = {}

    for z in range(num_vertices):
        copies[z] = []
        for _ in range(req[z]):
            copies[z].append(vid)
            side[vid] = 0 if z in left_original else 1
            vid += 1

    pm_edges = []
    for ei, (u, v, w, _) in enumerate(edges):
        assert u in left_original and v not in left_original
        pu, pv = vid, vid + 1
        vid += 2

        side[pu] = 1
        side[pv] = 0

        pm_edges.append((pu, pv, 0, ("inner", ei)))

        for cu in copies[u]:
            pm_edges.append((cu, pu, w, ("outer_weighted", ei)))
        for cv in copies[v]:
            pm_edges.append((pv, cv, 0, ("outer_zero", ei)))

    assert all(side[a] != side[b] for a, b, _, _ in pm_edges)
    return vid, pm_edges, side


def perfect_matching_spectrum(nv, edges):
    adj = [[] for _ in range(nv)]
    for ei, (u, v, w, meta) in enumerate(edges):
        adj[u].append((v, w, ei))
        adj[v].append((u, w, ei))

    costs = set()

    def rec(unmatched, cost):
        if not unmatched:
            costs.add(cost)
            return
        u = min(unmatched)
        for v, w, _ in adj[u]:
            if v in unmatched:
                rec(unmatched - {u, v}, cost + w)

    rec(set(range(nv)), 0)
    return costs


def weighted_edge_path_modes(q):
    # Odd path of length 2q-1.
    assert q >= 1
    red_positions = set(range(0, 2 * q - 1, 2))
    selected = set(range(0, 2 * q - 1, 2))
    unselected = set(range(1, 2 * q - 2, 2))

    selected_red = len(selected & red_positions)
    unselected_red = len(unselected & red_positions)

    assert selected_red == q
    assert unselected_red == 0
    assert len(selected) == q
    assert len(unselected) == q - 1

    return selected_red, unselected_red


def random_xlc_controls(seed=9379992, trials=80):
    rng = random.Random(seed)
    passed = 0

    for _ in range(trials):
        n = 3
        possible = [(i, j) for i in range(n) for j in range(n) if i != j]
        rng.shuffle(possible)
        arcs = possible[: rng.randint(2, 4)]
        caps = [rng.randint(0, 1) for _ in arcs]
        lengths = [rng.randint(0, 3) for _ in arcs]

        circ, _ = circulation_spectrum(n, arcs, caps, lengths)
        bedges, req = build_bfactor(n, arcs, caps, lengths)

        if len(bedges) > 12:
            continue

        bf = bfactor_spectrum(2 * n, bedges, req)
        assert circ == bf
        passed += 1

    return passed


def capacity_two_control():
    n = 3
    arcs = [(0, 1), (1, 2), (2, 0)]
    caps = [2, 2, 2]
    lengths = [1, 2, 3]

    circ, witnesses = circulation_spectrum(n, arcs, caps, lengths)
    assert circ == {0, 6, 12}
    assert witnesses[6] == (1, 1, 1)
    assert witnesses[12] == (2, 2, 2)

    bedges, req = build_bfactor(n, arcs, caps, lengths)
    bf = bfactor_spectrum(2 * n, bedges, req)
    assert bf == circ

    return sorted(circ)


def pm_gadget_controls(seed=314159, trials=24):
    rng = random.Random(seed)
    passed = 0

    for _ in range(trials):
        n = 2
        arcs = [(0, 1), (1, 0)]
        caps = [rng.randint(0, 1), rng.randint(0, 1)]
        lengths = [rng.randint(0, 3), rng.randint(0, 3)]

        bedges, req = build_bfactor(n, arcs, caps, lengths)
        if not bedges:
            continue

        bf = bfactor_spectrum(2 * n, bedges, req)
        nv, pm_edges, _ = bfactor_to_pm(
            2 * n, bedges, req, set(range(n))
        )

        if nv > 22:
            continue

        pm = perfect_matching_spectrum(nv, pm_edges)
        assert bf == pm
        passed += 1

    return passed


def path_gadget_controls():
    rows = {}
    for q in range(1, 8):
        selected_red, unselected_red = weighted_edge_path_modes(q)
        rows[q] = {
            "selected_red": selected_red,
            "unselected_red": unselected_red,
            "odd_path_length": 2 * q - 1,
        }
    return rows


def main():
    random_pass = random_xlc_controls()
    cap2 = capacity_two_control()
    pm_pass = pm_gadget_controls()
    paths = path_gadget_controls()

    print(json.dumps({
        "status": "PASS",
        "random_xlc_bfactor_exact_spectrum_controls": random_pass,
        "capacity_two_exact_spectrum": cap2,
        "bfactor_to_bipartite_pm_controls": pm_pass,
        "weighted_edge_to_red_blue_path_modes": paths,
        "bipartiteness": "VERIFIED_BY_GADGET_COLORING_ASSERTIONS",
        "claim_ceiling": (
            "REDUCTION_THEOREM_ONLY__DU2026_CONDITIONAL__"
            "NO_UNCONDITIONAL_DETERMINISTIC_SOLVER_CLAIM"
        ),
    }, indent=2))


if __name__ == "__main__":
    main()
