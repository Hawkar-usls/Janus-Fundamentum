#!/usr/bin/env python3
from __future__ import annotations

from itertools import combinations

def powerset(items):
    items = tuple(items)
    for r in range(len(items) + 1):
        for combo in combinations(items, r):
            yield frozenset(combo)

def rail(universe, concrete, basis):
    learned = []
    seen = set()
    iterations = 0
    while True:
        iterations += 1
        abstract = [q for q in universe if all(q in cut for cut in learned)]
        if not abstract:
            return ("UNSAT", None, iterations, tuple(learned))
        q = min(abstract)
        if q in concrete:
            return ("SAT", q, iterations, tuple(learned))
        separator = next(
            (cut for cut in basis if q not in cut and cut not in seen),
            None,
        )
        if separator is None:
            return ("STUCK", q, iterations, tuple(learned))
        learned.append(separator)
        seen.add(separator)

def canonical_basis(universe, concrete):
    u = frozenset(universe)
    return tuple(u - {q} for q in universe if q not in concrete)

def verify(max_universe_size=7):
    cases = 0
    max_iterations = 0
    for n in range(1, max_universe_size + 1):
        universe = tuple(range(n))
        for concrete in powerset(universe):
            basis = canonical_basis(universe, concrete)
            verdict, witness, iterations, learned = rail(universe, concrete, basis)
            cases += 1
            max_iterations = max(max_iterations, iterations)

            if concrete:
                assert verdict == "SAT"
                assert witness in concrete
            else:
                assert verdict == "UNSAT"
                assert witness is None

            assert iterations <= len(basis) + 1
            assert len(learned) == len(set(learned))
            for cut in learned:
                assert concrete.issubset(cut)

    # Negative control: basis is not separation-complete.
    universe = (0, 1, 2)
    concrete = frozenset({2})
    incomplete_basis = (frozenset({1, 2}),)
    verdict, witness, _, _ = rail(universe, concrete, incomplete_basis)
    assert verdict == "STUCK"
    assert witness == 1

    return {
        "status": "PASS",
        "exhaustive_cases": cases,
        "max_universe_size": max_universe_size,
        "max_iterations_observed": max_iterations,
        "negative_control": "PASS_INCOMPLETE_BASIS_STUCK",
    }

if __name__ == "__main__":
    import json
    print(json.dumps(verify(), indent=2, sort_keys=True))
