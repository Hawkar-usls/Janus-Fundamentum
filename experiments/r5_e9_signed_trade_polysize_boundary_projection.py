#!/usr/bin/env python3
"""Finite falsifier for the signed-trade polynomial boundary projection theorem.

This checker does NOT discover trades and is NOT an E8-D1 SAT solver.
It independently enumerates tiny original Exact-One blocks and compares them
with the spanning-tree projected representation, including repeated boundary
labels.
"""
from __future__ import annotations

from collections import defaultdict, deque
from itertools import product
import json


def spanning_tree(nodes, edges, root):
    # edge = (l,r,boundary_label), with canonical orientation l -> r
    adj = defaultdict(list)
    for i, (l, r, _label) in enumerate(edges):
        adj[l].append((r, i, +1))
        adj[r].append((l, i, -1))
    parent = {root: None}
    parent_edge = {}
    parent_dir = {}
    order = [root]
    q = deque([root])
    while q:
        u = q.popleft()
        for v, ei, direction in adj[u]:
            if v not in parent:
                parent[v] = u
                parent_edge[v] = ei
                parent_dir[v] = direction
                order.append(v)
                q.append(v)
    assert len(parent) == len(nodes)
    return parent, parent_edge, parent_dir, order, set(parent_edge.values())


def add_coeff(coeff, label, delta):
    out = dict(coeff)
    out[label] = out.get(label, 0) + delta
    if out[label] == 0:
        del out[label]
    return out


def path_potentials(nodes, edges, root):
    parent, pedge, pdir, order, tree_edges = spanning_tree(nodes, edges, root)
    p = {root: {}}
    for v in order[1:]:
        u = parent[v]
        ei = pedge[v]
        label = edges[ei][2]
        p[v] = add_coeff(p[u], label, pdir[v])
    return p, tree_edges


def eval_linear(coeff, boundary):
    return sum(c * boundary[label] for label, c in coeff.items())


def original_internal_states(L, R, edges, boundary):
    nodes = sorted(set(L) | set(R))
    out = []
    for bits in product((0, 1), repeat=len(nodes)):
        x = dict(zip(nodes, bits))
        if all(x[l] + x[r] + boundary[label] == 1 for l, r, label in edges):
            out.append(x)
    return out


def projected_q_states(L, R, edges, boundary):
    nodes = set(L) | set(R)
    root = L[0]
    p, tree_edges = path_potentials(nodes, edges, root)
    accepted = []
    for q in (0, 1):
        ok = True
        for i, (l, r, label) in enumerate(edges):
            if i not in tree_edges:
                if eval_linear(p[r], boundary) - eval_linear(p[l], boundary) != boundary[label]:
                    ok = False
                    break
        if ok:
            for v in nodes:
                y = q + eval_linear(p[v], boundary)
                if not 0 <= y <= 1:
                    ok = False
                    break
        if ok:
            accepted.append(q)
    return accepted, p


def reconstruct(L, R, p, boundary, q):
    x = {}
    for l in L:
        x[l] = q + eval_linear(p[l], boundary)
    for r in R:
        x[r] = 1 - q - eval_linear(p[r], boundary)
    return x


CONTROLS = {
    "C4_DISTINCT_BOUNDARY": (
        ["l0", "l1"], ["r0", "r1"],
        [
            ("l0", "r0", "z0"),
            ("l1", "r0", "z1"),
            ("l1", "r1", "z2"),
            ("l0", "r1", "z3"),
        ],
    ),
    "C4_REPEATED_BOUNDARY_LABEL": (
        ["l0", "l1"], ["r0", "r1"],
        [
            ("l0", "r0", "a"),
            ("l1", "r0", "b"),
            ("l1", "r1", "a"),
            ("l0", "r1", "c"),
        ],
    ),
    "C6": (
        ["l0", "l1", "l2"], ["r0", "r1", "r2"],
        [
            ("l0", "r0", "a"),
            ("l1", "r0", "b"),
            ("l1", "r1", "c"),
            ("l2", "r1", "d"),
            ("l2", "r2", "e"),
            ("l0", "r2", "f"),
        ],
    ),
    "K33": (
        ["l0", "l1", "l2"], ["r0", "r1", "r2"],
        [(f"l{i}", f"r{j}", f"z{i}{j}") for i in range(3) for j in range(3)],
    ),
}

rows = []
for name, (L, R, edges) in CONTROLS.items():
    labels = sorted({label for _l, _r, label in edges})
    compatible = 0
    max_fibre = 0
    nonzero_compatible_fibres = set()
    zero_fibre = None

    for bits in product((0, 1), repeat=len(labels)):
        boundary = dict(zip(labels, bits))
        original = original_internal_states(L, R, edges, boundary)
        qs, p = projected_q_states(L, R, edges, boundary)

        # Exact projection: one accepted q for each original internal state.
        assert len(original) == len(qs), (name, boundary, len(original), qs)

        reconstructed = []
        for q in qs:
            x = reconstruct(L, R, p, boundary, q)
            assert all(v in (0, 1) for v in x.values())
            assert all(x[l] + x[r] + boundary[label] == 1 for l, r, label in edges)
            reconstructed.append(tuple(x[v] for v in sorted(x)))
        assert sorted(reconstructed) == sorted(tuple(x[v] for v in sorted(x)) for x in original)

        if original:
            compatible += 1
            max_fibre = max(max_fibre, len(original))
            if any(bits):
                nonzero_compatible_fibres.add(len(original))
            else:
                zero_fibre = len(original)

    assert max_fibre <= 2
    assert zero_fibre == 2
    assert nonzero_compatible_fibres <= {1}
    rows.append({
        "control": name,
        "boundary_labels": len(labels),
        "compatible_boundary_patterns": compatible,
        "zero_boundary_fibre": zero_fibre,
        "nonzero_compatible_fibres": sorted(nonzero_compatible_fibres),
        "max_fibre": max_fibre,
        "projection_exact": True,
    })

print(json.dumps({
    "status": "PASS_SIGNED_TRADE_POLYSIZE_BOUNDARY_PROJECTION_CONTROLS",
    "controls": rows,
    "theorem_control": "SPANNING_TREE_PATH_POTENTIAL_PLUS_CHORD_EQUALITIES",
    "fixed_boundary_fibre_bound": 2,
    "nonzero_compatible_boundary_fibre": 1,
    "zero_boundary_fibre": 2,
    "repeated_boundary_labels": "PASS",
    "boundary_zero_requirement": "REMOVED_FOR_EXPLICIT_CONNECTED_TRADE",
    "trade_discovery": "OPEN",
    "mixed_carrier_global_closure": "OPEN",
    "role": "FINITE_REGRESSION_ONLY__NOT_D1_SOLVER",
    "E8_D1": "EMPTY",
    "P_VS_NP": "OPEN",
}, sort_keys=True))
