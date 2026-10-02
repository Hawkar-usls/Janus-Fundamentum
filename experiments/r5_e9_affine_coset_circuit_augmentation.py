#!/usr/bin/env python3
"""Finite hostile replay for affine-coset circuit augmentation.

The arbitrary-size proof is in the companion research note.  This checker uses
exhaustive enumeration only on tiny frozen controls and is therefore
OFFLINE_FALSIFIER_ONLY, not an E8-D1 algorithm.
"""
from __future__ import annotations

import json
from itertools import product


def row_masks(edges, n):
    out = []
    for e in edges:
        assert len(e) == 3 and len(set(e)) == 3
        m = 0
        for v in e:
            assert 0 <= v < n
            m |= 1 << v
        out.append(m)
    return out


def in_kernel(rows, z):
    return all(((r & z).bit_count() & 1) == 0 for r in rows)


def in_odd_coset(rows, x):
    return all(((r & x).bit_count() & 1) == 1 for r in rows)


def exact_one(rows, x):
    return all((r & x).bit_count() == 1 for r in rows)


def all_kernel(rows, n):
    return [z for z in range(1 << n) if in_kernel(rows, z)]


def all_coset(rows, n):
    return [x for x in range(1 << n) if in_odd_coset(rows, x)]


def is_circuit(rows, z):
    if z == 0 or not in_kernel(rows, z):
        return False
    # A proper nonzero kernel sub-support would witness nonminimality.
    sub = (z - 1) & z
    while sub:
        if in_kernel(rows, sub):
            return False
        sub = (sub - 1) & z
    return True


def all_circuits(rows, n):
    return [z for z in range(1, 1 << n) if is_circuit(rows, z)]


def delta(x, z):
    return (x ^ z).bit_count() - x.bit_count()


def greedy_descent(rows, n, circuits):
    # All ones is always in the odd coset for 3-uniform rows.
    x = (1 << n) - 1
    path = [x.bit_count()]
    while True:
        improving = [c for c in circuits if delta(x, c) < 0]
        if not improving:
            return x, path
        # Frozen deterministic tie-break: integer encoding.
        c = min(improving)
        x ^= c
        path.append(x.bit_count())
        assert path[-1] < path[-2]
        assert len(path) <= n + 1


def check(name, n, edges):
    rows = row_masks(edges, n)

    # Frozen controls here are cubic as well as 3-uniform.
    degrees = [0] * n
    for e in edges:
        for v in e:
            degrees[v] += 1
    assert all(d == 3 for d in degrees)

    kernel = all_kernel(rows, n)
    coset = all_coset(rows, n)
    circuits = all_circuits(rows, n)
    assert coset
    assert (1 << n) - 1 in coset

    optimum = min(x.bit_count() for x in coset)

    # Exhaustively replay CAD-2 on every affine point of the tiny control:
    # globally minimum iff there is no negative circuit.
    for x in coset:
        has_negative_circuit = any(delta(x, c) < 0 for c in circuits)
        globally_minimal = x.bit_count() == optimum
        assert globally_minimal == (not has_negative_circuit)

    final, path = greedy_descent(rows, n, circuits)
    assert final.bit_count() == optimum
    assert not any(delta(final, c) < 0 for c in circuits)

    exact = [x for x in coset if exact_one(rows, x)]
    if n % 3 == 0:
        assert bool(exact) == (optimum == n // 3)
    else:
        assert not exact

    return {
        "name": name,
        "n": n,
        "kernel_size": len(kernel),
        "circuit_count": len(circuits),
        "coset_size": len(coset),
        "coset_min_weight": optimum,
        "exact_one_solution_count": len(exact),
        "greedy_weight_path": path,
        "circuit_local_iff_global_checked_on_all_coset_points": True,
    }


FANO7 = [
    (0, 1, 2),
    (0, 3, 4),
    (0, 5, 6),
    (1, 3, 5),
    (1, 4, 6),
    (2, 3, 6),
    (2, 4, 5),
]

AFFINE3X3 = []
for r in range(3):
    AFFINE3X3.append(tuple(3 * r + c for c in range(3)))
for c in range(3):
    AFFINE3X3.append(tuple(3 * r + c for r in range(3)))
for k in range(3):
    AFFINE3X3.append(tuple(3 * r + ((r + k) % 3) for r in range(3)))

UNSAT9 = [
    (3, 6, 7),
    (2, 3, 4),
    (0, 3, 8),
    (2, 5, 8),
    (0, 4, 7),
    (1, 4, 8),
    (1, 5, 7),
    (1, 2, 6),
    (0, 5, 6),
]

controls = [
    check("FANO7", 7, FANO7),
    check("AFFINE_3X3", 9, AFFINE3X3),
    check("CONNECTED_LINEAR_CUBIC_UNSAT9", 9, UNSAT9),
]

by = {c["name"]: c for c in controls}
assert by["AFFINE_3X3"]["coset_min_weight"] == 3
assert by["AFFINE_3X3"]["exact_one_solution_count"] == 3
assert by["CONNECTED_LINEAR_CUBIC_UNSAT9"]["coset_min_weight"] == 9
assert by["CONNECTED_LINEAR_CUBIC_UNSAT9"]["exact_one_solution_count"] == 0
assert by["FANO7"]["coset_min_weight"] == 3

print(json.dumps({
    "status": "PASS_AFFINE_COSET_CIRCUIT_AUGMENTATION_FINITE_REPLAY",
    "role": "OFFLINE_FALSIFIER_ONLY",
    "theorem_under_test": "GLOBAL_MINIMUM_IFF_NO_NEGATIVE_CIRCUIT",
    "controls": controls,
    "universal_solver_reduction": "SIGNED_NEGATIVE_CIRCUIT_SYNTHESIS",
    "negative_circuit_polynomial_algorithm": "OPEN",
    "E8_D1": "EMPTY",
    "P_VS_NP": "OPEN",
}, sort_keys=True))
