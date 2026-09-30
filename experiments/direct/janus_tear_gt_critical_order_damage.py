#!/usr/bin/env python3
"""Measure root local-resolvent damage to critical total orders of GT_n.

A permutation of the n vertices defines a total order assignment. It satisfies
all transitivity clauses and all non-minimality clauses except the clause for its
minimum vertex. These n! assignments are called critical orders here.

For every resolvent accepted by Policy-0A's root one-pass local Resolution rule,
we count the critical orders that falsify it. We also measure the union damage of
the complete pass, overlaps between positive-damage clauses, and damage inside
each minimum class.

The audit does not claim that critical-order counting is the historical proof
invariant or that root damage controls all residual states.
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations, permutations
from math import factorial

from janus_tear_policy0a_graph_tautology_probe import graph_tautology_cnf
from janus_tear_policy0t_trace_certificate import resolution_trace, unit_trace

Clause = tuple[int, ...]


def pair_variables(n: int) -> dict[int, tuple[int, int]]:
    result: dict[int, tuple[int, int]] = {}
    variable = 1
    for left in range(n):
        for right in range(left + 1, n):
            result[variable] = (left, right)
            variable += 1
    return result


def order_assignment(order: tuple[int, ...], pairs: dict[int, tuple[int, int]]):
    position = {vertex: index for index, vertex in enumerate(order)}
    return {
        variable: position[left] < position[right]
        for variable, (left, right) in pairs.items()
    }


def clause_satisfied(clause: Clause, assignment: dict[int, bool]) -> bool:
    return any(
        assignment[abs(literal)] if literal > 0 else not assignment[abs(literal)]
        for literal in clause
    )


def falsified_axioms(cnf, assignment) -> tuple[Clause, ...]:
    return tuple(
        clause for clause in cnf if not clause_satisfied(clause, assignment)
    )


def vertex_support(clause: Clause, pairs: dict[int, tuple[int, int]]) -> int:
    vertices: set[int] = set()
    for literal in clause:
        vertices.update(pairs[abs(literal)])
    return len(vertices)


def root_events(cnf):
    propagated, contradiction, _ = unit_trace(cnf)
    assert not contradiction and propagated is not None and propagated
    literal_count = sum(len(clause) for clause in propagated)
    width_limit = max(map(len, propagated)) + 1
    saturated, refuted, attempts, additions, events = resolution_trace(
        propagated,
        width_limit,
        max(64, 4 * literal_count),
        max(8, len(propagated) // 4),
    )
    assert not refuted
    assert additions == len(events)
    return saturated, attempts, events


def self_test() -> None:
    rows = []
    aggregate_damage_by_support: dict[int, list[int]] = {}

    for n in range(3, 9):
        cnf, variable_count = graph_tautology_cnf(n)
        pairs = pair_variables(n)
        assert len(pairs) == variable_count

        orders: list[tuple[int, ...]] = []
        assignments = []
        minimum_histogram: Counter[int] = Counter()
        for order in permutations(range(n)):
            assignment = order_assignment(order, pairs)
            failed = falsified_axioms(cnf, assignment)
            assert len(failed) == 1
            minimum = order[0]
            minimum_histogram[minimum] += 1
            orders.append(order)
            assignments.append(assignment)
        assert len(assignments) == factorial(n)
        assert set(minimum_histogram.values()) == {factorial(n - 1)}

        _, attempts, events = root_events(cnf)
        damage_values = []
        damage_sets: list[set[int]] = []
        positive_damage_sets: list[set[int]] = []
        support_histogram: Counter[int] = Counter()
        damage_histogram: Counter[int] = Counter()
        maximum_damage = 0
        maximum_clause: Clause | None = None
        maximum_support = 0

        for event in events:
            clause = tuple(event["resolvent"])
            damaged = {
                index
                for index, assignment in enumerate(assignments)
                if not clause_satisfied(clause, assignment)
            }
            damage = len(damaged)
            support = vertex_support(clause, pairs)
            damage_values.append(damage)
            damage_sets.append(damaged)
            if damaged:
                positive_damage_sets.append(damaged)
            support_histogram[support] += 1
            damage_histogram[damage] += 1
            aggregate_damage_by_support.setdefault(support, []).append(damage)
            if damage > maximum_damage:
                maximum_damage = damage
                maximum_clause = clause
                maximum_support = support

        assert damage_values
        critical_count = factorial(n)
        initial_minimum_clause_damage = factorial(n - 1)
        union_damage_set = set().union(*damage_sets)
        union_damage = len(union_damage_set)
        surviving_orders = critical_count - union_damage
        union_by_minimum = Counter(orders[index][0] for index in union_damage_set)
        survivor_by_minimum = tuple(
            factorial(n - 1) - union_by_minimum[vertex]
            for vertex in range(n)
        )
        maximum_pair_overlap = max(
            (len(left & right) for left, right in combinations(positive_damage_sets, 2)),
            default=0,
        )
        total_positive_damage = sum(map(len, positive_damage_sets))
        overlap_excess = total_positive_damage - union_damage

        rows.append(
            (
                n,
                critical_count,
                len(events),
                attempts,
                maximum_damage,
                union_damage,
                surviving_orders,
                maximum_support,
                maximum_clause,
                initial_minimum_clause_damage,
            )
        )

        print(f"ORDER_SIZE = {n}")
        print(f"  critical_orders = {critical_count}")
        print(f"  root_resolution_attempts = {attempts}")
        print(f"  accepted_root_resolvents = {len(events)}")
        print(f"  positive_damage_resolvents = {len(positive_damage_sets)}")
        print(f"  initial_minimum_clause_damage = {initial_minimum_clause_damage}")
        print(f"  maximum_resolvent_damage = {maximum_damage}")
        print(f"  maximum_damage_fraction = {maximum_damage}/{critical_count}")
        print(f"  complete_pass_union_damage = {union_damage}")
        print(f"  complete_pass_union_fraction = {union_damage}/{critical_count}")
        print(f"  surviving_critical_orders = {surviving_orders}")
        print(f"  survivors_by_minimum = {survivor_by_minimum}")
        print(f"  total_positive_damage_with_multiplicity = {total_positive_damage}")
        print(f"  overlap_excess = {overlap_excess}")
        print(f"  maximum_pair_overlap = {maximum_pair_overlap}")
        print(f"  maximum_damage_support = {maximum_support}")
        print(f"  maximum_damage_clause = {maximum_clause}")
        print(f"  support_histogram = {tuple(sorted(support_histogram.items()))}")
        print(f"  damage_histogram = {tuple(sorted(damage_histogram.items()))}")

    support_summary = tuple(
        (
            support,
            len(values),
            min(values),
            max(values),
            sum(values),
        )
        for support, values in sorted(aggregate_damage_by_support.items())
    )

    print("JANUS_GT_CRITICAL_ORDER_DAMAGE = PASS")
    print(f"rows = {tuple(rows)}")
    print(f"aggregate_support_damage = {support_summary}")
    print("candidate_measure = critical total orders")
    print("claim_boundary = root finite witness-damage audit; historical invariant and residual-state induction remain unproved")


if __name__ == "__main__":
    self_test()
