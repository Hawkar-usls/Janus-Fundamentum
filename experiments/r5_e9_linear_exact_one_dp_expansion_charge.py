#!/usr/bin/env python3
"""Finite checker for the linear Exact-One Davis-Putnam charge theorem.

The arbitrary-d identity is proved combinatorially in the companion theorem
note. This script checks the clause-accounting implementation on the Fano plane,
a cubic linear 3-uniform finite control.
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
    return clauses


def is_tautology(clause):
    return any(-lit in clause for lit in clause)


def dp_charge(clauses, var):
    P = {c for c in clauses if var in c}
    N = {c for c in clauses if -var in c}
    R = set()
    for p in P:
        for n in N:
            r = (p - {var}) | (n - {-var})
            if not is_tautology(r):
                R.add(frozenset(r))
    chi = len(R) - len(P) - len(N)
    removed_literals = sum(map(len, P)) + sum(map(len, N))
    created_literals = sum(map(len, R))
    literal_charge = created_literals - removed_literals
    return {
        "P": len(P),
        "N": len(N),
        "R": len(R),
        "chi": chi,
        "removed_literals": removed_literals,
        "created_literals": created_literals,
        "literal_charge": literal_charge,
    }


# Fano plane: 3-uniform, 3-regular, linear.
edges = [
    (1, 2, 3),
    (1, 4, 5),
    (1, 6, 7),
    (2, 4, 6),
    (2, 5, 7),
    (3, 4, 7),
    (3, 5, 6),
]

# Explicitly check linearity and degree 3.
deg = {v: 0 for v in range(1, 8)}
for e in edges:
    for v in e:
        deg[v] += 1
assert set(deg.values()) == {3}
for i in range(len(edges)):
    for j in range(i + 1, len(edges)):
        assert len(set(edges[i]) & set(edges[j])) <= 1

clauses = exact_one_cnf(edges)
results = {v: dp_charge(clauses, v) for v in range(1, 8)}

for v, r in results.items():
    assert (r["P"], r["N"], r["R"]) == (3, 6, 12), (v, r)
    assert r["chi"] == 3, (v, r)
    assert r["removed_literals"] == 21, (v, r)
    assert r["created_literals"] == 36, (v, r)
    assert r["literal_charge"] == 15, (v, r)

# Closed-form checks for a few d values. These are arithmetic controls only;
# existence of a corresponding regular linear hypergraph is not asserted here.
for d in range(1, 17):
    P = d
    N = 2 * d
    R = 2 * d * (d - 1)
    assert R - P - N == d * (2 * d - 5)
    assert 3 * R - (3 * d + 2 * (2 * d)) == d * (6 * d - 13)

out = {
    "status": "PASS_LINEAR_EXACT_ONE_DP_EXPANSION_CHARGE",
    "finite_control": "FANO_PLANE",
    "hypergraph": {
        "vertices": 7,
        "edges": 7,
        "uniformity": 3,
        "regular_degree": 3,
        "linear": True,
    },
    "per_variable_expected": {
        "P": 3,
        "N": 6,
        "R": 12,
        "clause_charge": 3,
        "removed_literals": 21,
        "created_literals": 36,
        "literal_charge": 15,
    },
    "all_seven_variables_pass": True,
    "general_formula": {
        "resolvents": "2*d*(d-1)",
        "clause_charge": "d*(2*d-5)",
        "literal_charge": "d*(6*d-13)",
    },
    "scope": "FINITE_ACCOUNTING_CHECK_PLUS_COMPANION_COMBINATORIAL_PROOF",
    "D1": "EMPTY",
    "P_VS_NP": "OPEN",
    "P_EQ_NP": "NOT_PROVED",
}
print(json.dumps(out, sort_keys=True))
