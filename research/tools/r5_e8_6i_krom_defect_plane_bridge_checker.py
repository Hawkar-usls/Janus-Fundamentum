#!/usr/bin/env python3
from __future__ import annotations

from itertools import combinations, product
import json


ZERO = (0, 0, 0)
POINTS = tuple(product((0, 1), repeat=3))
AND_GRAPH = frozenset({
    (0, 0, 0),
    (0, 1, 0),
    (1, 0, 0),
    (1, 1, 1),
})


def vxor(a, b):
    return tuple(x ^ y for x, y in zip(a, b))


def linear_span(vectors):
    s = {ZERO}
    for v in vectors:
        s |= {vxor(x, v) for x in tuple(s)}
    return frozenset(s)


def all_affine_subspaces():
    linear = set()
    nonzero = POINTS[1:]
    for r in range(4):
        for chosen in combinations(nonzero, r):
            linear.add(linear_span(chosen))

    affine = set()
    for u in linear:
        for a in POINTS:
            affine.add(frozenset(vxor(a, x) for x in u))
    return affine


def is_affine(s):
    if not s:
        return True
    a = next(iter(s))
    u = {vxor(a, x) for x in s}
    return (
        ZERO in u
        and all(vxor(x, y) in u for x in u for y in u)
    )


def plane_equation(t):
    assert len(t) == 4
    for normal in POINTS[1:]:
        values = {
            sum(a * b for a, b in zip(normal, x)) & 1
            for x in t
        }
        if len(values) == 1:
            return normal, next(iter(values))
    raise AssertionError("not an affine plane")


def clause_holds(kind, x, y):
    if kind == "notx_or_noty":
        return (not x) or (not y)
    if kind == "notx_or_y":
        return (not x) or bool(y)
    if kind == "x_or_noty":
        return bool(x) or (not y)
    if kind == "x_or_y":
        return bool(x) or bool(y)
    raise AssertionError(kind)


def verify():
    affine = all_affine_subspaces()
    assert len(affine) == 51

    bad = []
    histogram = {}

    for t in affine:
        g = t & AND_GRAPH
        key = (len(t), len(g), is_affine(g))
        histogram[str(key)] = histogram.get(str(key), 0) + 1
        if not is_affine(g):
            bad.append((t, g))

    assert len(bad) == 5

    full = [item for item in bad if len(item[0]) == 8]
    planes = [item for item in bad if len(item[0]) == 4]
    assert len(full) == 1
    assert len(planes) == 4
    assert full[0][0] == frozenset(POINTS)

    observed_planes = {
        plane_equation(t): frozenset(g)
        for t, g in planes
    }

    expected_normals = {
        ((0, 0, 1), 0),  # p=0
        ((1, 0, 1), 0),  # p=x
        ((0, 1, 1), 0),  # p=y
        ((1, 1, 1), 1),  # p=x+y+1
    }
    assert set(observed_planes) == expected_normals

    mappings = [
        (((0, 0, 1), 0), "notx_or_noty"),
        (((1, 0, 1), 0), "notx_or_y"),
        (((0, 1, 1), 0), "x_or_noty"),
        (((1, 1, 1), 1), "x_or_y"),
    ]

    for equation, clause in mappings:
        normal, rhs = equation
        plane = {
            q for q in POINTS
            if (sum(a * b for a, b in zip(normal, q)) & 1) == rhs
        }
        exact = plane & AND_GRAPH

        via_clause = {
            (x, y, p)
            for x, y, p in plane
            if clause_holds(clause, x, y)
        }
        assert via_clause == exact

    return {
        "status": "PASS",
        "affine_subspaces_enumerated": len(affine),
        "non_affine_intersections": len(bad),
        "hard_full_contexts": len(full),
        "hard_plane_contexts": len(planes),
        "hard_plane_equations": [
            "p=0",
            "p=x",
            "p=y",
            "p=x+y+1",
        ],
        "krom_mapping": {
            "p=0": "not x OR not y",
            "p=x": "not x OR y",
            "p=y": "x OR not y",
            "p=x+y+1": "x OR y",
        },
        "scientific_ceiling":
            "LOCAL_CLASSIFICATION_AND_POLY_SUBCLASS_ONLY__D1_EMPTY",
        "histogram": histogram,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
