#!/usr/bin/env python3
"""Finite controls for the cubic-linear Exact-One matching-lean theorem.

The arbitrary-size theorem is the deficiency-count proof in the companion
research note. This script exhaustively checks the supported-subformula
maximum-deficiency criterion on two small cubic linear hypergraphs.
"""
from __future__ import annotations
import json


def exact_one_cnf(edges):
    clauses = set()
    for x, y, z in edges:
        clauses.add(frozenset((x, y, z)))
        clauses.add(frozenset((-x, -y)))
        clauses.add(frozenset((-x, -z)))
        clauses.add(frozenset((-y, -z)))
    return tuple(clauses)


def vars_of_clauses(F):
    return {abs(l) for C in F for l in C}


def deficiency(F):
    return len(F) - len(vars_of_clauses(F))


def max_supported_deficiency(F, vertices):
    vs = sorted(vertices)
    full_mask = (1 << len(vs)) - 1
    best_proper = None
    witness = None
    for mask in range(1 << len(vs)):
        S = {vs[i] for i in range(len(vs)) if mask & (1 << i)}
        sub = tuple(C for C in F if {abs(l) for l in C}.issubset(S))
        d = deficiency(sub)
        if mask != full_mask and (best_proper is None or d > best_proper):
            best_proper = d
            witness = sorted(S)
    return best_proper, witness


def check_hypergraph(name, vertices, edges):
    # cubic and linear
    deg = {v: 0 for v in vertices}
    for E in edges:
        assert len(set(E)) == 3
        for v in E:
            deg[v] += 1
    assert set(deg.values()) == {3}
    for i in range(len(edges)):
        for j in range(i+1, len(edges)):
            assert len(set(edges[i]) & set(edges[j])) <= 1

    F = exact_one_cnf(edges)
    n = len(vertices)
    assert len(edges) == n
    assert len(F) == 4*n
    full_d = deficiency(F)
    assert full_d == 3*n

    best_proper, support = max_supported_deficiency(F, vertices)
    assert best_proper < full_d
    return {
        "name": name,
        "variables": n,
        "clauses": len(F),
        "full_deficiency": full_d,
        "best_proper_supported_deficiency": best_proper,
        "best_proper_support": support,
        "matching_lean_criterion_control": True,
    }


fano_vertices = list(range(1, 8))
fano_edges = [
    (1,2,3), (1,4,5), (1,6,7),
    (2,4,6), (2,5,7), (3,4,7), (3,5,6),
]


def p(i, j):
    return 1 + 3*i + j


aff_vertices = list(range(1, 10))
aff_edges = []
for i in range(3):
    aff_edges.append(tuple(p(i,j) for j in range(3)))
for j in range(3):
    aff_edges.append(tuple(p(i,j) for i in range(3)))
for d in range(3):
    aff_edges.append(tuple(p(i,(i+d) % 3) for i in range(3)))

controls = [
    check_hypergraph("FANO", fano_vertices, fano_edges),
    check_hypergraph("Z3_AFFINE_3X3", aff_vertices, aff_edges),
]

out = {
    "status": "PASS_CUBIC_LINEAR_EXACT_ONE_MATCHING_LEAN_CONTROLS",
    "controls": controls,
    "general_theorem": "PROVED_IN_COMPANION_NOTE_BY_DEFICIENCY_COUNT",
    "R2_matching_autarky": "CLOSED_ON_CUBIC_LINEAR_EXACT_ONE",
    "R2_linear_autarky": "OPEN",
    "general_autarky": "OPEN",
    "D1": "EMPTY",
    "P_VS_NP": "OPEN",
    "P_EQ_NP": "NOT_PROVED",
}
print(json.dumps(out, sort_keys=True))
