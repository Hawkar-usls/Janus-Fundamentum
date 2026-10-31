#!/usr/bin/env python3
"""Structural regression for the source-incidence C4 barrier.

This checker verifies the graph-theoretic equivalence used by the source audit:
for simple CNF supports, the variable-clause incidence graph contains a C4 iff
two clauses share at least two variables.  It does not machine-prove the cited
NP-completeness theorem; that part is source-bound prior art.
"""

from __future__ import annotations

from itertools import combinations
import json
import random


def pairwise_linear(clauses):
    return all(len(set(a) & set(b)) <= 1 for a, b in combinations(clauses, 2))


def incidence_has_c4(clauses):
    # In a simple bipartite incidence graph, a C4 is equivalent to two clause
    # vertices having at least two common variable neighbours.
    for a, b in combinations(clauses, 2):
        if len(set(a) & set(b)) >= 2:
            return True
    return False


def explicit_graph_c4(clauses):
    variables = sorted({x for c in clauses for x in c})
    neigh = {x: {i for i, c in enumerate(clauses) if x in c} for x in variables}
    for x, y in combinations(variables, 2):
        if len(neigh[x] & neigh[y]) >= 2:
            return True
    return False


def random_support_family(rng, nvars, nclauses):
    clauses = []
    seen = set()
    attempts = 0
    while len(clauses) < nclauses and attempts < 500:
        attempts += 1
        k = rng.choice((1, 2, 3))
        c = tuple(sorted(rng.sample(range(nvars), k)))
        if c not in seen:
            seen.add(c)
            clauses.append(c)
    return clauses


def main():
    controls = [
        # C4 positive: two clauses share x,y.
        [(0, 1, 2), (0, 1, 3)],
        # C4-free linear triangle in clause-intersection space.
        [(0, 1, 2), (2, 3, 4), (4, 5, 0)],
        # Disjoint.
        [(0, 1, 2), (3, 4, 5)],
    ]

    checked = 0
    for clauses in controls:
        a = incidence_has_c4(clauses)
        b = explicit_graph_c4(clauses)
        assert a == b
        assert pairwise_linear(clauses) == (not a)
        checked += 1

    rng = random.Random(20260928)
    for nvars in range(3, 11):
        for _ in range(250):
            clauses = random_support_family(rng, nvars, rng.randint(1, min(12, 2 * nvars)))
            a = incidence_has_c4(clauses)
            b = explicit_graph_c4(clauses)
            assert a == b
            assert pairwise_linear(clauses) == (not a)
            checked += 1

    out = {
        "status": "PASS_SOURCE_INCIDENCE_C4_FREE_PIVOT_BARRIER",
        "families_checked": checked,
        "structural_equivalence": "linear simple CNF iff source incidence graph is C4-free",
        "complexity_import": "SOURCE_BOUND_PRIOR_ART_NOT_MACHINE_PROVED",
        "universal_barrier": "SOURCE_C4_CANNOT_BE_MANDATORY_PROGRESS_TRIGGER",
        "next_gate": "R5_E9_C4_FREE_SAFE_MULTI_PATH_GLOBAL_PIVOT_GATE_V1",
        "E8_D1": "EMPTY",
        "P_VS_NP": "OPEN",
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
