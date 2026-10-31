#!/usr/bin/env python3
"""Structural regression for the high-girth Sparse-Incomparability barrier.

Machine-checked here:
- the fixed signed-3SAT CSP template has eight ternary relations;
- each relation has exactly seven Boolean tuples and one falsifier;
- tuple membership is exactly signed-clause satisfaction;
- CNF satisfaction equals homomorphism into the fixed target on random small instances;
- relational cycle length m corresponds to incidence alternating cycle length 2m
  on nondegenerate sample structures.

NOT machine-proved here:
- Kun's deterministic Sparse Incomparability theorem;
- the resulting NP-hardness statement.
Those are source-bound prior art / theorem specialization in the companion note.
"""

from __future__ import annotations

from collections import deque
from itertools import product
import json
import random

BITS = tuple(product((0, 1), repeat=3))
SIGNS = BITS


def literal_value(x: int, negated: int) -> int:
    return 1 - x if negated else x


def clause_value(values, signs) -> bool:
    return any(literal_value(x, s) for x, s in zip(values, signs))


def target_relation(signs):
    # The unique falsifier is exactly the sign vector:
    # positive literal (s=0) is false at x=0;
    # negative literal (s=1) is false at x=1.
    return {a for a in BITS if clause_value(a, signs)}


def verify_target_template():
    relations = {}
    for s in SIGNS:
        rel = target_relation(s)
        assert len(rel) == 7
        assert s not in rel
        for a in BITS:
            assert ((a in rel) == clause_value(a, s))
        relations[''.join(map(str, s))] = {
            'size': len(rel),
            'unique_falsifier': ''.join(map(str, s)),
        }
    assert len(relations) == 8
    return relations


def formula_satisfied(assignment, constraints):
    for vars_, signs in constraints:
        values = tuple(assignment[v] for v in vars_)
        if not clause_value(values, signs):
            return False
    return True


def homomorphism_to_target(assignment, constraints):
    for vars_, signs in constraints:
        values = tuple(assignment[v] for v in vars_)
        if values not in target_relation(signs):
            return False
    return True


def verify_formula_csp_equivalence(seed=20260928):
    rng = random.Random(seed)
    checked_assignments = 0
    checked_instances = 0
    for nvars in range(3, 8):
        for _ in range(80):
            constraints = []
            for _ in range(rng.randint(1, 10)):
                vars_ = tuple(rng.sample(range(nvars), 3))
                signs = tuple(rng.randint(0, 1) for _ in range(3))
                constraints.append((vars_, signs))
            for bits in product((0, 1), repeat=nvars):
                assert formula_satisfied(bits, constraints) == homomorphism_to_target(bits, constraints)
                checked_assignments += 1
            checked_instances += 1
    return checked_instances, checked_assignments


def incidence_shortest_cycle_edges(constraints):
    """Shortest cycle length in the natural variable-constraint incidence graph.

    constraints is a list of variable tuples. Repeated coordinates are treated
    separately by relational_girth below as a degenerate relational 1-cycle.
    """
    vars_all = sorted({v for tup in constraints for v in tup})
    vnodes = [('v', v) for v in vars_all]
    cnodes = [('c', i) for i in range(len(constraints))]
    adj = {u: set() for u in vnodes + cnodes}
    for i, tup in enumerate(constraints):
        c = ('c', i)
        for v in tup:
            u = ('v', v)
            adj[u].add(c)
            adj[c].add(u)

    best = None
    # Standard unweighted shortest-cycle BFS from every start.
    for start in adj:
        dist = {start: 0}
        parent = {start: None}
        q = deque([start])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if v not in dist:
                    dist[v] = dist[u] + 1
                    parent[v] = u
                    q.append(v)
                elif parent[u] != v:
                    length = dist[u] + dist[v] + 1
                    if best is None or length < best:
                        best = length
    return best


def relational_girth(constraints):
    # Kun's degenerate length-1 cycle: repeated coordinate in one tuple.
    if any(len(set(tup)) < len(tup) for tup in constraints):
        return 1
    inc = incidence_shortest_cycle_edges(constraints)
    if inc is None:
        return None  # infinity / forest
    assert inc % 2 == 0
    return inc // 2


def verify_cycle_correspondence():
    samples = [
        # Two constraints share two variables: incidence C4, relational girth 2.
        ([(0, 1, 2), (0, 1, 3)], 2, 4),
        # Three constraints form a Berge/relational 3-cycle: incidence C6.
        ([(0, 1, 4), (1, 2, 5), (2, 0, 6)], 3, 6),
        # Acyclic incidence forest.
        ([(0, 1, 2), (2, 3, 4), (4, 5, 6)], None, None),
        # Degenerate relational tuple.
        ([(0, 0, 1)], 1, None),
    ]
    out = []
    for constraints, expected_rg, expected_inc in samples:
        rg = relational_girth(constraints)
        inc = incidence_shortest_cycle_edges(constraints)
        assert rg == expected_rg
        if expected_rg != 1:
            assert inc == expected_inc
            if rg is not None:
                assert inc == 2 * rg
        out.append({'relational_girth': rg, 'incidence_cycle_edges': inc})
    return out


def main():
    relations = verify_target_template()
    ninst, nassign = verify_formula_csp_equivalence()
    cycle_samples = verify_cycle_correspondence()

    out = {
        'status': 'PASS_SPARSE_INCOMPARABILITY_HIGH_GIRTH_PIVOT_BARRIER',
        'fixed_target_domain_size': 2,
        'signed_clause_relation_count': 8,
        'each_relation_size': 7,
        'relations': relations,
        'formula_csp_instances_checked': ninst,
        'formula_csp_assignments_checked': nassign,
        'cycle_correspondence_samples': cycle_samples,
        'structural_encoding': 'SIGNED_3SAT_EXACT_FIXED_BOOLEAN_CSP',
        'complexity_import': 'SOURCE_BOUND_SPARSE_INCOMPARABILITY_NOT_MACHINE_PROVED',
        'barrier': 'NO_FIXED_BOUNDED_LENGTH_SOURCE_CYCLE_CAN_BE_MANDATORY_UNIVERSAL_PROGRESS_TRIGGER',
        'next_gate': 'R5_E9_HIGH_GIRTH_SAFE_NONLOCAL_GLOBAL_PIVOT_GATE_V1',
        'E8_D1': 'EMPTY',
        'P_VS_NP': 'OPEN',
    }
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
