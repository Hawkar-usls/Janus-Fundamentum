#!/usr/bin/env python3
"""Finite replay for the cubic-kernel circuit-contraction theorem.

This checker is deliberately tiny and exhaustive.  Enumeration is used only on
frozen finite controls; it is NOT an E8-D1 algorithm and is never invoked as a
SAT/Exact-One oracle on arbitrary input.
"""
from __future__ import annotations

from itertools import product
import json


def matrix_from_edges(n: int, edges: list[tuple[int, int, int]]) -> list[list[int]]:
    A = [[0] * n for _ in edges]
    for i, e in enumerate(edges):
        assert len(set(e)) == 3
        for j in e:
            A[i][j] = 1
    assert all(sum(row) == 3 for row in A)
    assert all(sum(A[i][j] for i in range(len(A))) == 3 for j in range(n))
    return A


def syndrome(A: list[list[int]], z: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sum(a * b for a, b in zip(row, z)) & 1 for row in A)


def support(z: tuple[int, ...]) -> frozenset[int]:
    return frozenset(i for i, b in enumerate(z) if b)


def kernel_vectors(A: list[list[int]]) -> list[tuple[int, ...]]:
    n = len(A[0])
    return [z for z in product((0, 1), repeat=n) if any(z) and not any(syndrome(A, z))]


def parity_points(A: list[list[int]]) -> list[tuple[int, ...]]:
    n = len(A[0])
    one = (1,) * len(A)
    return [x for x in product((0, 1), repeat=n) if syndrome(A, x) == one]


def contracted_components(A: list[list[int]], z: tuple[int, ...]):
    """Contract every active degree-2 check to an edge on selected variables."""
    S = set(support(z))
    assert S
    adj: dict[int, list[tuple[int, int]]] = {v: [] for v in S}
    active_rows = 0

    for r, row in enumerate(A):
        hit = [v for v in S if row[v]]
        # Az=0 and row weight 3 force intersection size 0 or 2.
        assert len(hit) in (0, 2), (r, hit)
        if len(hit) == 2:
            active_rows += 1
            u, v = hit
            adj[u].append((v, r))
            adj[v].append((u, r))

    # Column weight 3 makes the contracted multigraph cubic.
    assert all(len(adj[v]) == 3 for v in S)
    assert 2 * active_rows == 3 * len(S)

    unseen = set(S)
    comps: list[frozenset[int]] = []
    while unseen:
        root = min(unseen)
        unseen.remove(root)
        stack = [root]
        C = {root}
        while stack:
            u = stack.pop()
            for v, _ in adj[u]:
                if v in unseen:
                    unseen.remove(v)
                    C.add(v)
                    stack.append(v)
        comps.append(frozenset(C))
    return adj, comps


def indicator(n: int, S: frozenset[int]) -> tuple[int, ...]:
    return tuple(1 if i in S else 0 for i in range(n))


def is_circuit(A: list[list[int]], z: tuple[int, ...], kernels=None) -> bool:
    if not any(z) or any(syndrome(A, z)):
        return False
    if kernels is None:
        kernels = kernel_vectors(A)
    S = support(z)
    return not any(support(y) < S for y in kernels)


def charge(x: tuple[int, ...], z: tuple[int, ...]) -> int:
    # |x xor z|-|x| = sum_{j:z_j=1}(1-2x_j)
    return sum((1 - 2 * x[j]) for j, b in enumerate(z) if b)


def replay(name: str, A: list[list[int]]) -> dict:
    n = len(A[0])
    kernels = kernel_vectors(A)
    points = parity_points(A)
    assert kernels
    assert points

    circuit_count = 0
    disconnected_count = 0
    max_components = 0

    for z in kernels:
        _, comps = contracted_components(A, z)
        connected = len(comps) == 1
        circuit = is_circuit(A, z, kernels)
        assert circuit == connected
        max_components = max(max_components, len(comps))
        circuit_count += int(circuit)
        disconnected_count += int(not connected)

        # Every contracted connected component is itself a minimal kernel support.
        reconstructed = []
        for C in comps:
            c = indicator(n, C)
            assert not any(syndrome(A, c))
            assert is_circuit(A, c, kernels)
            reconstructed.append(c)

        # Components partition the support exactly.
        union = frozenset().union(*comps)
        assert union == support(z)
        assert sum(len(C) for C in comps) == len(support(z))

        for x in points:
            component_charge = sum(charge(x, c) for c in reconstructed)
            assert component_charge == charge(x, z)
            if charge(x, z) < 0:
                assert any(charge(x, c) < 0 for c in reconstructed)

    # Exact existential equivalence for every affine point in each frozen control.
    for x in points:
        has_negative_kernel = any(charge(x, z) < 0 for z in kernels)
        has_negative_circuit = any(
            is_circuit(A, z, kernels) and charge(x, z) < 0 for z in kernels
        )
        assert has_negative_kernel == has_negative_circuit

    return {
        "name": name,
        "n": n,
        "kernel_nonzero_count": len(kernels),
        "circuit_count": circuit_count,
        "disconnected_kernel_count": disconnected_count,
        "max_contracted_components": max_components,
        "parity_point_count": len(points),
        "circuit_iff_connected": True,
        "negative_kernel_iff_negative_circuit": True,
    }


FANO_7 = [
    (0, 1, 2),
    (0, 3, 4),
    (0, 5, 6),
    (1, 3, 5),
    (1, 4, 6),
    (2, 3, 6),
    (2, 4, 5),
]


def affine_3x3_edges() -> list[tuple[int, int, int]]:
    idx = lambda r, c: 3 * r + c
    edges: list[tuple[int, int, int]] = []
    for r in range(3):
        edges.append(tuple(idx(r, c) for c in range(3)))
    for c in range(3):
        edges.append(tuple(idx(r, c) for r in range(3)))
    for d in range(3):
        edges.append(tuple(idx(r, (r + d) % 3) for r in range(3)))
    return edges


controls = [
    replay("FANO_7", matrix_from_edges(7, FANO_7)),
    replay("AFFINE_3X3", matrix_from_edges(9, affine_3x3_edges())),
]

out = {
    "status": "PASS_CUBIC_KERNEL_CIRCUIT_CONTRACTION_FINITE_REPLAY",
    "controls": controls,
    "theorem_scope": "ROW3_COLUMN3_BINARY_INCIDENCE",
    "negative_circuit_reduction": "EXISTS_NEGATIVE_CIRCUIT_IFF_EXISTS_NEGATIVE_NONZERO_KERNEL_VECTOR",
    "arbitrary_input_solver": "NOT_SUPPLIED",
    "E8_D1": "EMPTY",
    "P_VS_NP": "OPEN",
}
print(json.dumps(out, sort_keys=True))
