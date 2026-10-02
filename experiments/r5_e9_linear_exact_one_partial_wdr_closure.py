#!/usr/bin/env python3
"""Finite controls for the cubic linear Exact-One partial WDR-closure theorem.

The structural BCE/no-growth statements are proved in the companion note.
This checker validates the accounting and a satisfiable connected 3x3 affine
control. Exhaustive model enumeration is OFFLINE_FALSIFIER_ONLY.
"""
from __future__ import annotations
from itertools import product
import json


def exact_one_cnf(edges):
    clauses = set()
    for x, y, z in edges:
        clauses.add(frozenset((x, y, z)))
        clauses.add(frozenset((-x, -y)))
        clauses.add(frozenset((-x, -z)))
        clauses.add(frozenset((-y, -z)))
    return tuple(clauses)


def is_tautology(c):
    return any(-l in c for l in c)


def simplify(F, var, value):
    true_lit = var if value else -var
    false_lit = -true_lit
    out = set()
    for C in F:
        if true_lit in C:
            continue
        out.add(frozenset(l for l in C if l != false_lit))
    return tuple(out)


def unit_propagate(F):
    F = tuple(set(F))
    assignment = {}
    while True:
        if any(len(C) == 0 for C in F):
            return F, assignment, True
        units = [next(iter(C)) for C in F if len(C) == 1]
        if not units:
            return F, assignment, False
        lit = units[0]
        v, val = abs(lit), lit > 0
        if v in assignment and assignment[v] != val:
            return F, assignment, True
        assignment[v] = val
        F = simplify(F, v, val)


def failed_literal_up(F, var):
    _, _, c0 = unit_propagate(simplify(F, var, False))
    _, _, c1 = unit_propagate(simplify(F, var, True))
    if c0 and not c1:
        return 1
    if c1 and not c0:
        return 0
    if c0 and c1:
        return "UNSAT_BY_TWO_UP_BRANCHES"
    return None


def blocked_by(F, C, lit):
    for D in F:
        if -lit not in D:
            continue
        r = (set(C) - {lit}) | (set(D) - {-lit})
        if not is_tautology(r):
            return False
    return True


def blocked_clauses(F):
    out = []
    for C in F:
        for lit in C:
            if blocked_by(F, C, lit):
                out.append((C, lit))
    return out


def dp_charge(F, var):
    P = {C for C in F if var in C}
    N = {C for C in F if -var in C}
    R = set()
    for p in P:
        for n in N:
            r = (p - {var}) | (n - {-var})
            if not is_tautology(r):
                R.add(frozenset(r))
    return len(R) - len(P) - len(N)


def is_horn(F):
    return all(sum(l > 0 for l in C) <= 1 for C in F)


def is_dual_horn(F):
    return all(sum(l < 0 for l in C) <= 1 for C in F)


def is_krom(F):
    return all(len(C) <= 2 for C in F)


def vars_of(F):
    return sorted({abs(l) for C in F for l in C})


def eval_formula(F, assignment):
    return all(any(assignment[abs(l)] == (l > 0) for l in C) for C in F)


def brute_models(F):
    """OFFLINE FALSIFIER ONLY."""
    vs = vars_of(F)
    out = []
    for bits in product((False, True), repeat=len(vs)):
        a = dict(zip(vs, bits))
        if eval_formula(F, a):
            out.append(a)
    return out


# Points (i,j) of Z3^2, encoded 1..9. Hyperedges are 3 rows, 3 columns,
# and the 3 parallel diagonals j-i=d. This is cubic, 3-uniform, linear.
def point(i, j):
    return 1 + 3*i + j


edges = []
for i in range(3):
    edges.append(tuple(point(i, j) for j in range(3)))
for j in range(3):
    edges.append(tuple(point(i, j) for i in range(3)))
for d in range(3):
    edges.append(tuple(point(i, (i+d) % 3) for i in range(3)))

# Structural sanity.
deg = {v: 0 for v in range(1, 10)}
for E in edges:
    for v in E:
        deg[v] += 1
assert set(deg.values()) == {3}
for i in range(len(edges)):
    for j in range(i+1, len(edges)):
        assert len(set(edges[i]) & set(edges[j])) <= 1

F = exact_one_cnf(edges)
assert not any(len(C) == 1 for C in F)
for v in range(1, 10):
    assert any(v in C for C in F)
    assert any(-v in C for C in F)
assert blocked_clauses(F) == []
assert all(dp_charge(F, v) == 3 for v in range(1, 10))
assert not is_horn(F)
assert not is_dual_horn(F)
assert not is_krom(F)
assert all(failed_literal_up(F, v) is None for v in range(1, 10))

models = brute_models(F)
assert models
assert len(models) == 3
for v in range(1, 10):
    assert {a[v] for a in models} == {False, True}

out = {
    "status": "PASS_LINEAR_EXACT_ONE_PARTIAL_WDR_CLOSURE_CONTROL",
    "fixture": "Z3_3X3_ROWS_COLUMNS_ONE_DIAGONAL_CLASS",
    "connected_component_size": {"variables": 9, "constraints": 9},
    "cubic": True,
    "linear": True,
    "initial_units": 0,
    "pure_variables": 0,
    "blocked_clauses": 0,
    "dp_charge_all_variables": 3,
    "horn": False,
    "dual_horn": False,
    "krom": False,
    "failed_literal_UP_all_variables": "UNKNOWN",
    "offline_model_count": 3,
    "offline_each_variable_takes_both_values": True,
    "offline_enumeration_role": "OFFLINE_FALSIFIER_ONLY__FORBIDDEN_AS_E8_CORE",
    "closed_WDR_lanes": ["R0_UNIT_PURE", "R3_BCE", "R4_NO_GROWTH_VE", "R7_HORN_DUALHORN_KROM_DIRECT"],
    "open_WDR_lanes": ["R1_EQUIVALENCE", "R2_AUTARKY", "R5_STRUCTURAL_DOMINANCE", "R6_RANKED_SR_MACRO", "OTHER_POLY_REPRESENTATIONS"],
    "D1": "EMPTY",
    "P_VS_NP": "OPEN",
    "P_EQ_NP": "NOT_PROVED",
}
print(json.dumps(out, sort_keys=True))
