#!/usr/bin/env python3
"""Finite controls for local odd-parity LP blindness.

The arbitrary-size theorem is in the companion research note. Exhaustive Boolean
enumeration is OFFLINE_FALSIFIER_ONLY and is not an admitted E8-D1 algorithm.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations, product
import json


def degrees(edges, n):
    d = [0] * n
    for e in edges:
        assert len(e) == 3
        assert len(set(e)) == 3
        for v in e:
            d[v] += 1
    return d


def is_linear(edges):
    return all(len(set(a) & set(b)) <= 1 for a, b in combinations(edges, 2))


def connected_incidence(edges, n):
    N = n + len(edges)
    adj = [[] for _ in range(N)]
    for j, e in enumerate(edges):
        ej = n + j
        for v in e:
            adj[v].append(ej)
            adj[ej].append(v)
    seen = {0}
    q = [0]
    for u in q:
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                q.append(v)
    return len(seen) == N


def parity_ok(edges, x):
    return all(sum(x[v] for v in e) % 2 == 1 for e in edges)


def exact_one(edges, x):
    return all(sum(x[v] for v in e) == 1 for e in edges)


def audit_boolean_control(name, edges, n):
    ds = degrees(edges, n)
    assert len(set(ds)) == 1
    d = ds[0]
    m = len(edges)
    assert d * n == 3 * m

    parity = []
    exact = []
    for x in product((0, 1), repeat=n):
        if parity_ok(edges, x):
            parity.append(x)
            if exact_one(edges, x):
                exact.append(x)

    # Uniform 1/3 point.  On every triple it is
    # (100 + 010 + 001)/3, hence lies in conv(ODD_3).
    u = tuple(Fraction(1, 3) for _ in range(n))
    assert all(sum(u[v] for v in e) == 1 for e in edges)
    lp_objective = sum(u)
    assert lp_objective == Fraction(n, 3)

    # Every point in a local odd-parity polytope has row sum >= 1.
    # Summed over a d-regular instance this proves the same global lower bound,
    # so the uniform point is an LP optimum.
    lower_bound = Fraction(m, d)
    assert lower_bound == Fraction(n, 3)

    return {
        "name": name,
        "n": n,
        "m": m,
        "degree": d,
        "linear": is_linear(edges),
        "connected_incidence": connected_incidence(edges, n),
        "parity_solution_count": len(parity),
        "integer_parity_min_weight": min(sum(x) for x in parity),
        "exact_one_solution_count": len(exact),
        "local_parity_lp_optimum": str(lp_objective),
        "uniform_pseudocodeword": "1/3_ON_EVERY_VARIABLE",
    }


# Connected, linear, cubic 9-vertex UNSAT control found by deterministic
# offline search and frozen here.  It is not rejected by n mod 3.
UNSAT9 = (
    (3, 6, 7),
    (2, 3, 4),
    (0, 3, 8),
    (2, 5, 8),
    (0, 4, 7),
    (1, 4, 8),
    (1, 5, 7),
    (1, 2, 6),
    (0, 5, 6),
)

# Satisfiable 3x3 affine control: rows + columns + one diagonal class.
AFFINE_3X3 = tuple(
    [(3 * r + 0, 3 * r + 1, 3 * r + 2) for r in range(3)]
    + [(0 + c, 3 + c, 6 + c) for c in range(3)]
    + [tuple(3 * r + ((r + b) % 3) for r in range(3)) for b in range(3)]
)

unsat = audit_boolean_control("CONNECTED_LINEAR_CUBIC_UNSAT9", UNSAT9, 9)
sat = audit_boolean_control("AFFINE_3X3_SAT", AFFINE_3X3, 9)

assert unsat["exact_one_solution_count"] == 0
assert unsat["integer_parity_min_weight"] == 9
assert unsat["local_parity_lp_optimum"] == "3"
assert sat["exact_one_solution_count"] == 3
assert sat["integer_parity_min_weight"] == 3
assert sat["local_parity_lp_optimum"] == "3"

out = {
    "status": "PASS_LOCAL_ODD_PARITY_LP_BLINDNESS",
    "controls": [unsat, sat],
    "arbitrary_size_theorem": "FOR_EVERY_3UNIFORM_DREGULAR_INSTANCE_LOCAL_PARITY_LP_OPTIMUM_EQUALS_N_OVER_3",
    "consequence": "BASIC_LOCAL_PARITY_LP_CANNOT_DISTINGUISH_EXACT_ONE_SAT_FROM_UNSAT",
    "offline_exhaustive_role": "FALSIFIER_ONLY__NOT_E8_D1",
    "E8_D1": "EMPTY",
    "P_VS_NP": "OPEN",
}
print(json.dumps(out, sort_keys=True))
