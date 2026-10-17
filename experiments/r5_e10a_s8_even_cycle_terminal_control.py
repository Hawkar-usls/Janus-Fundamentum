#!/usr/bin/env python3
"""Finite source-bound control: explicit S8 -> even-cycle representation."""

from __future__ import annotations

import itertools
import json


def mat_vec(rows: list[list[int]], x: int) -> tuple[int, ...]:
    n = len(rows[0])
    return tuple(
        sum(rows[r][c] for c in range(n) if (x >> c) & 1) & 1
        for r in range(len(rows))
    )


def popcount(x: int) -> int:
    return x.bit_count()


A = [
    [1,0,0,0,0,1,1,1],
    [0,1,0,0,1,0,1,1],
    [0,0,1,0,1,1,0,1],
    [0,0,0,1,1,1,1,1],
]

# r1'=r4; r2'=r3+r4; r3'=r1+r2; r4'=r2
B = [
    A[3][:],
    [a ^ b for a,b in zip(A[2],A[3])],
    [a ^ b for a,b in zip(A[0],A[1])],
    A[1][:],
]

TARGET = [
    [0,0,0,1,1,1,1,1],
    [0,0,1,1,0,0,1,0],
    [1,1,0,0,1,1,0,0],
    [0,1,0,0,1,0,1,1],
]

assert B == TARGET

inc = B[:3]
sig = B[3]
weights = [sum(inc[r][c] for r in range(3)) for c in range(8)]
assert all(w in (1,2) for w in weights)

# Reduced incidence graph on vertices 0,1,2 plus omitted vertex 3.
edges: list[tuple[int,int]] = []
for c in range(8):
    support = [r for r in range(3) if inc[r][c]]
    if len(support) == 1:
        edges.append((support[0],3))
    else:
        edges.append((support[0],support[1]))

sigma = [i for i,b in enumerate(sig) if b]

# Row operations preserve every dependency. Independently check that the
# transformed matrix dependency test equals:
# graph boundary zero + signature parity zero.
for mask in range(1 << 8):
    dep_A = all(v == 0 for v in mat_vec(A,mask))
    boundary = [0,0,0,0]
    parity = 0
    for e,(u,v) in enumerate(edges):
        if (mask >> e) & 1:
            boundary[u] ^= 1
            boundary[v] ^= 1
            parity ^= sig[e]
    dep_graph_lift = boundary == [0,0,0,0] and parity == 0
    assert dep_A == dep_graph_lift

# Verify the distinguished-edge reduction by brute force for every f:
# min dependency containing f equals
# 1 + min J with boundary endpoints(f) and signature parity sig[f].
shortest = {}
for f,(u,v) in enumerate(edges):
    best_dep = 99
    best_join = 99
    for mask in range(1 << 8):
        if (mask >> f) & 1 and all(z == 0 for z in mat_vec(A,mask)):
            best_dep = min(best_dep,popcount(mask))
        if (mask >> f) & 1:
            continue
        boundary = [0,0,0,0]
        parity = 0
        for e,(a,b) in enumerate(edges):
            if (mask >> e) & 1:
                boundary[a] ^= 1
                boundary[b] ^= 1
                parity ^= sig[e]
        target = [0,0,0,0]
        target[u] ^= 1
        target[v] ^= 1
        if boundary == target and parity == sig[f]:
            best_join = min(best_join,popcount(mask))
    assert best_dep == 1 + best_join
    shortest[str(f)] = {"shortest_circuit":best_dep,"join_without_f":best_join}

print(json.dumps({
    "status":"PASS",
    "standard_S8_matrix":"VERIFIED",
    "row_transform":"VERIFIED",
    "reduced_incidence_column_weights":weights,
    "edges":edges,
    "signature_edges":sigma,
    "all_dependency_masks_checked":256,
    "distinguished_edge_reduction_checked_for_all_f":shortest,
    "claim_ceiling":"FINITE_S8_EVEN_CYCLE_CERTIFICATE_ONLY"
},indent=2))
