#!/usr/bin/env python3
"""Exhaust the singleton-branch same-cut preservation theorem on 3/4 vertices.

Each abstract quotient component is one original vertex.  A legal clause chooses
for every comparison variable exactly one of

    absent / low->high / high->low,

so tautological opposite-literal pairs are excluded by construction.  For every
branch variable and both truth values, the checker applies exact CNF
restriction and contracts the selected singleton endpoints while retaining
parallel residual literals as distinct multigraph edges.

It verifies:

1. every surviving directed-cycle source still has an external directed cycle;
2. every surviving spanning source remains spanning;
3. every child bridge lifts to a source bridge with a unique cut lift;
4. no source family with no same-cut pair gains a same-cut pair after the
   singleton branch.

The theorem is proved separately in
`GT_SINGLETON_BRANCH_SAME_CUT_PRESERVATION.md`; this program is an exhaustive
small-instance falsification gate.
"""

from __future__ import annotations

from collections import Counter
from itertools import product

Literal = int
Clause = tuple[Literal, ...]


def variables(n: int):
    pairs = []
    variable = 1
    for low in range(n):
        for high in range(low + 1, n):
            pairs.append((variable, low, high))
            variable += 1
    return tuple(pairs)


def clauses(n: int):
    pairs = variables(n)
    result = []
    for choices in product((0, 1, -1), repeat=len(pairs)):
        clause = []
        for (variable, _low, _high), choice in zip(pairs, choices):
            if choice:
                clause.append(variable if choice > 0 else -variable)
        result.append(tuple(clause))
    return tuple(result)


def direction(literal: int, pair_by_variable):
    low, high = pair_by_variable[abs(literal)]
    return (low, high) if literal > 0 else (high, low)


def component_map(n: int, branch_pair):
    left, right = branch_pair
    groups = [{left, right}] + [
        {vertex}
        for vertex in range(n)
        if vertex not in (left, right)
    ]
    groups = sorted(groups, key=min)
    mapping = {
        vertex: component
        for component, group in enumerate(groups)
        for vertex in group
    }
    return mapping, tuple(frozenset(group) for group in groups)


def external_edges(clause: Clause, pair_by_variable, mapping=None):
    records = []
    for literal in clause:
        tail, head = direction(literal, pair_by_variable)
        if mapping is not None:
            tail = mapping[tail]
            head = mapping[head]
        if tail == head:
            continue
        records.append((tail, head, literal))
    return tuple(records)


def directed_cycle(vertex_count: int, records):
    adjacency = [[] for _ in range(vertex_count)]
    for tail, head, _literal in records:
        adjacency[tail].append(head)
    colour = [0] * vertex_count

    def visit(vertex: int):
        colour[vertex] = 1
        for neighbour in adjacency[vertex]:
            if colour[neighbour] == 1:
                return True
            if colour[neighbour] == 0 and visit(neighbour):
                return True
        colour[vertex] = 2
        return False

    return any(
        colour[vertex] == 0 and visit(vertex)
        for vertex in range(vertex_count)
    )


def components(vertex_count: int, records, removed_literal=None):
    adjacency = [set() for _ in range(vertex_count)]
    for left, right, literal in records:
        if literal == removed_literal:
            continue
        adjacency[left].add(right)
        adjacency[right].add(left)
    unseen = set(range(vertex_count))
    result = []
    while unseen:
        start = min(unseen)
        stack = [start]
        unseen.remove(start)
        part = {start}
        while stack:
            current = stack.pop()
            for neighbour in adjacency[current]:
                if neighbour not in unseen:
                    continue
                unseen.remove(neighbour)
                part.add(neighbour)
                stack.append(neighbour)
        result.append(frozenset(part))
    return tuple(sorted(result, key=lambda part: (len(part), tuple(sorted(part)))))


def classification(vertex_count: int, records):
    if directed_cycle(vertex_count, records):
        return "DIRECTED_CYCLE"
    if len(components(vertex_count, records)) == 1:
        return "COMPONENT_SPANNING"
    if not records:
        return "INTERNAL_ONLY"
    return "UNSAFE_ACYCLIC_LOW_RANK"


def bridge_cut(vertex_count: int, records, literal: int):
    matches = [record for record in records if record[2] == literal]
    if len(matches) != 1:
        return None
    parts = components(vertex_count, records, removed_literal=literal)
    if len(parts) != 2:
        return None
    return frozenset(parts)


def restrict_clause(clause: Clause, variable: int, value: bool):
    satisfying = variable if value else -variable
    falsified = -satisfying
    if satisfying in clause:
        return None
    return tuple(literal for literal in clause if literal != falsified)


def same_cut_pairs(vertex_count: int, clause_records):
    positive = Counter()
    negative = Counter()
    witnesses = []
    for clause, records in clause_records:
        if classification(vertex_count, records) != "COMPONENT_SPANNING":
            continue
        for _tail, _head, literal in records:
            cut = bridge_cut(vertex_count, records, literal)
            if cut is None:
                continue
            key = (abs(literal), cut)
            if literal > 0:
                positive[key] += 1
            else:
                negative[key] += 1
    for key in set(positive) & set(negative):
        witnesses.append((key, positive[key], negative[key]))
    return tuple(sorted(witnesses, key=repr))


def lifted_cut(child_cut, groups):
    return frozenset(
        frozenset(
            vertex
            for component in side
            for vertex in groups[component]
        )
        for side in child_cut
    )


def audit(n: int):
    all_clauses = clauses(n)
    pair_by_variable = {
        variable: (low, high)
        for variable, low, high in variables(n)
    }
    source_records = {
        clause: external_edges(clause, pair_by_variable)
        for clause in all_clauses
    }
    source_classes = {
        clause: classification(n, records)
        for clause, records in source_records.items()
    }
    safe_clauses = tuple(
        clause
        for clause in all_clauses
        if source_classes[clause] in {
            "DIRECTED_CYCLE",
            "COMPONENT_SPANNING",
            "INTERNAL_ONLY",
        }
    )

    counts: Counter[str] = Counter()
    child_classes: Counter[str] = Counter()
    violations = []

    for branch_variable, low, high in variables(n):
        mapping, groups = component_map(n, (low, high))
        child_vertex_count = len(groups)
        for value in (False, True):
            child_family = []
            source_same_cut = same_cut_pairs(
                n,
                tuple((clause, source_records[clause]) for clause in safe_clauses),
            )
            assert not source_same_cut

            for clause in safe_clauses:
                residual = restrict_clause(clause, branch_variable, value)
                if residual is None:
                    counts["satisfied_clauses"] += 1
                    continue
                child_records = external_edges(
                    residual,
                    pair_by_variable,
                    mapping=mapping,
                )
                child_class = classification(child_vertex_count, child_records)
                child_classes[child_class] += 1
                counts["surviving_clauses"] += 1
                child_family.append((residual, child_records))

                source_class = source_classes[clause]
                if source_class == "DIRECTED_CYCLE" and child_class != "DIRECTED_CYCLE":
                    violations.append({
                        "kind": "CYCLE_LOST",
                        "n": n,
                        "branch_variable": branch_variable,
                        "value": value,
                        "clause": clause,
                        "residual": residual,
                        "child_records": child_records,
                        "child_class": child_class,
                    })
                if source_class == "COMPONENT_SPANNING" and child_class not in {
                    "COMPONENT_SPANNING",
                    "DIRECTED_CYCLE",
                }:
                    violations.append({
                        "kind": "SPANNING_LOST",
                        "n": n,
                        "branch_variable": branch_variable,
                        "value": value,
                        "clause": clause,
                        "residual": residual,
                        "child_class": child_class,
                    })

                for _tail, _head, literal in child_records:
                    child_cut = bridge_cut(
                        child_vertex_count,
                        child_records,
                        literal,
                    )
                    if child_cut is None:
                        continue
                    counts["child_bridge_literals"] += 1
                    source_cut = bridge_cut(
                        n,
                        source_records[clause],
                        literal,
                    )
                    lifted = lifted_cut(child_cut, groups)
                    if source_cut != lifted:
                        violations.append({
                            "kind": "BRIDGE_OR_CUT_REFLECTION_FAILURE",
                            "n": n,
                            "branch_variable": branch_variable,
                            "value": value,
                            "clause": clause,
                            "literal": literal,
                            "source_cut": source_cut,
                            "child_cut": child_cut,
                            "lifted_cut": lifted,
                        })

            child_same_cut = same_cut_pairs(
                child_vertex_count,
                tuple(child_family),
            )
            counts["branch_instances"] += 1
            counts["child_same_cut_witnesses"] += len(child_same_cut)
            if child_same_cut:
                violations.append({
                    "kind": "NEW_SAME_CUT_PAIR",
                    "n": n,
                    "branch_variable": branch_variable,
                    "value": value,
                    "witnesses": child_same_cut,
                })

    return {
        "n": n,
        "clause_count": len(all_clauses),
        "safe_clause_count": len(safe_clauses),
        "counts": tuple(sorted(counts.items())),
        "child_classes": tuple(sorted(child_classes.items())),
        "violations": tuple(violations),
    }


def self_test():
    aggregate_counts: Counter[str] = Counter()
    aggregate_classes: Counter[str] = Counter()
    rows = []
    for n in (3, 4):
        data = audit(n)
        assert not data["violations"], data["violations"][:3]
        aggregate_counts.update(dict(data["counts"]))
        aggregate_classes.update(dict(data["child_classes"]))
        rows.append(data)
        print(f"VERTEX_COUNT = {n}")
        print(f"  clause_count = {data['clause_count']}")
        print(f"  safe_clause_count = {data['safe_clause_count']}")
        print(f"  counts = {data['counts']}")
        print(f"  child_classes = {data['child_classes']}")
        print(f"  violations = {data['violations']}")

    assert aggregate_counts["branch_instances"] > 0
    assert aggregate_counts["child_same_cut_witnesses"] == 0
    print("JANUS_ABSTRACT_SINGLETON_BRANCH_SAME_CUT = PASS")
    print(f"ROWS = {tuple(rows)}")
    print(f"AGGREGATE_COUNTS = {tuple(sorted(aggregate_counts.items()))}")
    print(f"AGGREGATE_CHILD_CLASSES = {tuple(sorted(aggregate_classes.items()))}")
    print(
        "claim_boundary = exhaustive legal-clause falsification gate on 3 and "
        "4 singleton quotient vertices; arbitrary-size theorem proved separately"
    )


if __name__ == "__main__":
    self_test()
