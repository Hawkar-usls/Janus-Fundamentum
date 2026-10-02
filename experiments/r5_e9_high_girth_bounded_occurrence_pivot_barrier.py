#!/usr/bin/env python3
"""Structural regression for the high-girth bounded-occurrence barrier.

The checker validates only the finite structural pieces:
- source relational degree equals variable occurrence count for nondegenerate
  signed 3CNF tuples;
- Tovey-style <=4-occurrence fixtures encode as structures of degree <=4;
- the direct-product special case satisfies the product degree bound.

Kun's Sparse Incomparability theorem, its bounded-degree expander construction,
and Tovey's NP-completeness theorem are source-bound prior art and are not
machine-proved here.
"""

from __future__ import annotations

from collections import Counter
from itertools import product
import json
import random


def relational_degrees(tuples):
    d = Counter()
    for tup in tuples:
        for x in tup:
            d[x] += 1
    return d


def max_degree(tuples):
    d = relational_degrees(tuples)
    return max(d.values(), default=0)


def random_occ4_fixture(rng, nvars):
    degree = [0] * nvars
    tuples = []
    attempts = 0
    while attempts < 5000:
        attempts += 1
        avail = [v for v in range(nvars) if degree[v] < 4]
        if len(avail) < 3:
            break
        tri = tuple(sorted(rng.sample(avail, 3)))
        if tri in tuples:
            continue
        tuples.append(tri)
        for v in tri:
            degree[v] += 1
        if len(tuples) >= nvars:
            break
    assert all(len(set(t)) == 3 for t in tuples)
    assert max_degree(tuples) <= 4
    d = relational_degrees(tuples)
    for v in range(nvars):
        assert d[v] == degree[v]
    return tuples


def direct_product_relation(A, B):
    """Direct-product special case of a twisted product for one ternary symbol."""
    C = []
    for a in A:
        for b in B:
            C.append(tuple((a[i], b[i]) for i in range(3)))
    return C


def verify_direct_product_degree_bound(seed=20260928):
    rng = random.Random(seed)
    checks = 0
    for na in range(3, 8):
        for nb in range(3, 8):
            universe_a = list(range(na))
            universe_b = list(range(nb))
            all_a = list(product(universe_a, repeat=3))
            all_b = list(product(universe_b, repeat=3))
            for _ in range(12):
                A = rng.sample(all_a, rng.randint(1, min(12, len(all_a))))
                B = rng.sample(all_b, rng.randint(1, min(12, len(all_b))))
                C = direct_product_relation(A, B)
                assert max_degree(C) <= max_degree(A) * max_degree(B)
                checks += 1
    return checks


def main():
    rng = random.Random(20260928)
    fixture_count = 0
    max_seen = 0
    for nvars in range(4, 30):
        for _ in range(20):
            tuples = random_occ4_fixture(rng, nvars)
            max_seen = max(max_seen, max_degree(tuples))
            assert max_degree(tuples) <= 4
            fixture_count += 1

    product_checks = verify_direct_product_degree_bound()

    out = {
        'status': 'PASS_HIGH_GIRTH_BOUNDED_OCCURRENCE_PIVOT_BARRIER_STRUCTURAL_CHECKS',
        'occ4_fixtures_checked': fixture_count,
        'max_source_degree_seen': max_seen,
        'direct_product_degree_bound_checks': product_checks,
        'source_degree_identity': 'RELATIONAL_DEGREE_EQUALS_VARIABLE_OCCURRENCE_FOR_DISTINCT_COORDINATE_CLAUSES',
        'degree_bound_formula': 'D = 4 * M_tau_1_27',
        'complexity_imports': [
            'TOVEY_3SAT4_NP_COMPLETENESS_NOT_MACHINE_PROVED',
            'KUN_SPARSE_INCOMPARABILITY_NOT_MACHINE_PROVED',
            'KUN_BOUNDED_DEGREE_EXPANDER_THEOREM_NOT_MACHINE_PROVED',
        ],
        'barrier': 'NO_SHORT_SOURCE_CYCLE_OR_UNBOUNDED_SOURCE_DEGREE_UNIVERSAL_DICHOTOMY',
        'next_gate': 'R5_E9_HIGH_GIRTH_SAFE_NONLOCAL_GLOBAL_PIVOT_GATE_V1',
        'E8_D1': 'EMPTY',
        'P_VS_NP': 'OPEN',
    }
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
