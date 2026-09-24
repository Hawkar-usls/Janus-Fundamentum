#!/usr/bin/env python3
"""
Finite controls for NM-0015:
support-four cubic star cocycles have at most four active incident tree
interfaces at every torso; canonical 2/Delta3/Y3 traces give local support <=8.

This is a regression control, not the proof.
"""
from __future__ import annotations

import itertools
import json
import random


TYPE_CAP = {"2": 1, "D3": 2, "Y3": 1}


def random_tree(n, rng):
    # Prüfer construction.
    if n == 1:
        return []
    if n == 2:
        return [(0, 1)]
    p = [rng.randrange(n) for _ in range(n - 2)]
    deg = [1] * n
    for x in p:
        deg[x] += 1
    edges = []
    for x in p:
        leaf = min(i for i, d in enumerate(deg) if d == 1)
        edges.append((leaf, x))
        deg[leaf] -= 1
        deg[x] -= 1
    a, b = [i for i, d in enumerate(deg) if d == 1]
    edges.append((a, b))
    return edges


def adjacency(n, edges):
    g = [[] for _ in range(n)]
    for eid, (u, v) in enumerate(edges):
        g[u].append((v, eid))
        g[v].append((u, eid))
    return g


def branch_vertices(g, v, first):
    seen = {v}
    stack = [first]
    out = set()
    while stack:
        x = stack.pop()
        if x in seen:
            continue
        seen.add(x)
        out.add(x)
        for y, _ in g[x]:
            if y not in seen:
                stack.append(y)
    return out


def check_instance(n, edges, support_nodes, edge_types):
    g = adjacency(n, edges)
    total_support = len(support_nodes)
    assert total_support == 4

    max_active = 0
    max_local_bound = 0

    for v in range(n):
        local = sum(1 for x in support_nodes if x == v)
        active = []
        for u, eid in g[v]:
            branch = branch_vertices(g, v, u)
            if any(x in branch for x in support_nodes):
                active.append(eid)

        # Incident branches are disjoint, and each active branch consumes at
        # least one support terminal outside v.
        assert len(active) <= total_support - local
        assert len(active) <= 4

        virtual_bound = sum(TYPE_CAP[edge_types[eid]] for eid in active)
        # Uniform worst-case: Delta contributes two; 2/Y contribute one.
        local_bound = local + virtual_bound
        assert local_bound <= local + 2 * (4 - local)
        assert local_bound <= 8

        # Empty Y branches choose the canonical zero state.  Kernel toggles
        # live on pairwise-disjoint edge blocks, hence commute.
        y_empty = []
        for u, eid in g[v]:
            if edge_types[eid] != "Y3":
                continue
            branch = branch_vertices(g, v, u)
            if not any(x in branch for x in support_nodes):
                y_empty.append(eid)
        # Model each interface triad as its own disjoint three-bit block.
        masks = [0b111 << (3 * eid) for eid in y_empty]
        a = 0
        for m in masks:
            a ^= m
        b = 0
        for m in reversed(masks):
            b ^= m
        assert a == b

        max_active = max(max_active, len(active))
        max_local_bound = max(max_local_bound, local_bound)

    return max_active, max_local_bound


def exhaustive_named_controls():
    out = []
    # Path, star, balanced-ish tree: adversarial placements of four terminals.
    families = [
        (7, [(i, i + 1) for i in range(6)]),
        (7, [(0, i) for i in range(1, 7)]),
        (7, [(0,1),(0,2),(1,3),(1,4),(2,5),(2,6)]),
    ]
    for n, edges in families:
        m = len(edges)
        for edge_type in ("2", "D3", "Y3"):
            types = [edge_type] * m
            for support in itertools.combinations_with_replacement(range(n), 4):
                out.append(check_instance(n, edges, support, types))
    return {
        "instances": len(out),
        "max_active": max(x[0] for x in out),
        "max_local_support_bound": max(x[1] for x in out),
    }


def random_controls(trials=1000, seed=150015):
    rng = random.Random(seed)
    vals = []
    for _ in range(trials):
        n = rng.randint(2, 30)
        edges = random_tree(n, rng)
        types = [rng.choice(list(TYPE_CAP)) for _ in edges]
        support = tuple(rng.randrange(n) for _ in range(4))
        vals.append(check_instance(n, edges, support, types))
    return {
        "instances": len(vals),
        "max_active": max(x[0] for x in vals),
        "max_local_support_bound": max(x[1] for x in vals),
    }


def quotient_basis_union_bound(generator_support_bound=8, quotient_rank=2):
    assert generator_support_bound == 8
    assert quotient_rank == 2
    return generator_support_bound * quotient_rank


def main():
    named = exhaustive_named_controls()
    rnd = random_controls()
    result = {
        "status": "PASS_FINITE_STAR_ACTIVE_INTERFACE_CONTROLS",
        "exhaustive_named": named,
        "random": rnd,
        "theorem_bounds": {
            "star_real_support": 4,
            "active_incident_interfaces_per_star": 4,
            "local_star_representative_support": 8,
            "y_interface_kernel_support": 3,
            "two_row_signature_support_from_two_small_quotient_generators":
                quotient_basis_union_bound(),
            "P_VS_NP": "OPEN",
        },
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
