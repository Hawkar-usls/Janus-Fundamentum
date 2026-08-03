#!/usr/bin/env python3
"""Audit reachability of the minimal abstract merged-tail counterexample.

The abstract signed-clause search finds a three-component witness:

    T = {0->1, 0->2, 1->2}
    C = {0->1, 1->2, 2->0}

Resolving on 0->2 / 2->0 yields {0->1, 1->2}; the shared edge 0->1
changes from non-bridge in both parents to a bridge in the resolvent.

This checker searches every parent-eligible exact key of GT_4,...,GT_8 for all
quotient-isomorphic copies of that mechanism.  It distinguishes:

- transitive K3 clause occurrences;
- directed-cycle K3 clause occurrences;
- co-resident pairs on the same quotient triple;
- pairs with an actual complementary Resolution pivot;
- pairs whose resolvent is unsafe acyclic low-rank.

The result is finite reachability evidence only.  Absence through GT_8 is not an
arbitrary-n closure theorem.
"""

from __future__ import annotations

from collections import Counter, defaultdict

from janus_tear_gt_component_tree_clause_audit import (
    clause_component_graph,
    execution_context,
)
from janus_tear_gt_directed_component_clause_audit import (
    directed_edges,
    has_directed_cycle,
)
from janus_tear_gt_rank_safety_dichotomy import safety_class
from janus_tear_policy0t_trace_certificate import canonical_clause


def triangle_record(n, clause, assignment, pairs):
    clause = tuple(clause)
    if len(clause) != 3:
        return None
    graph = clause_component_graph(n, clause, assignment, pairs)
    external, internal = directed_edges(clause, graph, pairs)
    if internal or len(external) != 3:
        return None
    vertices = frozenset(
        component
        for tail, head, _literal in external
        for component in (int(tail), int(head))
    )
    undirected = frozenset(
        tuple(sorted((int(tail), int(head))))
        for tail, head, _literal in external
    )
    if len(vertices) != 3 or len(undirected) != 3:
        return None
    kind = (
        "DIRECTED_CYCLE_K3"
        if has_directed_cycle(int(graph["component_count"]), external)
        else "TRANSITIVE_K3"
    )
    edge_by_literal = {
        int(literal): (int(tail), int(head))
        for tail, head, literal in external
    }
    return {
        "kind": kind,
        "vertices": vertices,
        "edge_by_literal": edge_by_literal,
        "graph": graph,
    }


def audit(n: int):
    context = execution_context(n)
    policy = context["policy"]
    pairs = context["pairs"]
    levels = context["levels"]
    root = set(tuple(clause) for clause in context["root"])
    target = n - 2

    counts: Counter[str] = Counter()
    by_level: Counter[tuple[int, str]] = Counter()
    result_classes: Counter[str] = Counter()
    transitive_sources: Counter[str] = Counter()
    examples = []

    for state in policy.states.values():
        call_id = int(state["entry_call"])
        novelty = int(levels[call_id])
        if novelty > target:
            continue
        counts["states"] += 1
        assignment = context["call_after_pre"][call_id]
        key = tuple(tuple(clause) for clause in state["key"])

        triangles = []
        for clause in key:
            record = triangle_record(n, clause, assignment, pairs)
            if record is None:
                continue
            record = dict(record)
            record["clause"] = clause
            triangles.append(record)
            kind = str(record["kind"])
            counts[kind] += 1
            by_level[(novelty, kind)] += 1
            if kind == "TRANSITIVE_K3":
                source = "ROOT" if clause in root else "DERIVED_OR_RESTRICTED"
                transitive_sources[source] += 1

        transitive = [r for r in triangles if r["kind"] == "TRANSITIVE_K3"]
        cyclic = [r for r in triangles if r["kind"] == "DIRECTED_CYCLE_K3"]
        if transitive and cyclic:
            counts["states_with_both_triangle_kinds"] += 1

        for left in transitive:
            for right in cyclic:
                if left["vertices"] != right["vertices"]:
                    continue
                counts["same_triple_pairs"] += 1
                left_clause = tuple(left["clause"])
                right_clause = tuple(right["clause"])
                common_literals = set(left_clause).intersection(right_clause)
                if common_literals:
                    counts["same_triple_pairs_with_shared_literal"] += 1

                for pivot in left_clause:
                    if -pivot not in right_clause:
                        continue
                    counts["complementary_pivot_pairs"] += 1
                    resolvent_set = (set(left_clause) - {pivot}) | (
                        set(right_clause) - {-pivot}
                    )
                    if any(-literal in resolvent_set for literal in resolvent_set):
                        counts["tautological_resolvents"] += 1
                        continue
                    resolvent = canonical_clause(resolvent_set)
                    if resolvent is None or not resolvent:
                        counts["rejected_or_empty_resolvents"] += 1
                        continue
                    structure = safety_class(n, resolvent, assignment, pairs)
                    classification = str(structure["classification"])
                    result_classes[classification] += 1
                    counts["legal_resolvents"] += 1

                    shared_nonbridge = []
                    for bad in common_literals:
                        if bad == pivot:
                            continue
                        left_graph = left["graph"]
                        right_graph = right["graph"]
                        left_edges = left["edge_by_literal"]
                        right_edges = right["edge_by_literal"]
                        if bad not in left_edges or bad not in right_edges:
                            continue
                        # On K3 every edge is non-bridge in each parent.
                        shared_nonbridge.append(bad)

                    if classification == "UNSAFE_ACYCLIC_LOW_RANK":
                        counts["reachable_abstract_witnesses"] += 1
                        if len(examples) < 20:
                            examples.append({
                                "n": n,
                                "state_id": int(state["id"]),
                                "call_id": call_id,
                                "novelty": novelty,
                                "left": left_clause,
                                "right": right_clause,
                                "pivot": pivot,
                                "shared_nonbridge": tuple(sorted(shared_nonbridge)),
                                "resolvent": resolvent,
                                "structure": structure,
                            })

    return {
        "n": n,
        "target": target,
        "counts": tuple(sorted(counts.items())),
        "by_level": tuple(sorted(by_level.items())),
        "result_classes": tuple(sorted(result_classes.items())),
        "transitive_sources": tuple(sorted(transitive_sources.items())),
        "examples": tuple(examples),
    }


def self_test() -> None:
    aggregate: Counter[str] = Counter()
    aggregate_results: Counter[str] = Counter()
    aggregate_sources: Counter[str] = Counter()
    rows = []

    for n in range(4, 9):
        data = audit(n)
        aggregate.update(dict(data["counts"]))
        aggregate_results.update(dict(data["result_classes"]))
        aggregate_sources.update(dict(data["transitive_sources"]))
        rows.append((
            n,
            data["target"],
            data["counts"],
            data["result_classes"],
            data["transitive_sources"],
        ))
        print(f"ORDER_SIZE = {n}")
        print(f"  target = {data['target']}")
        print(f"  counts = {data['counts']}")
        print(f"  by_level = {data['by_level']}")
        print(f"  result_classes = {data['result_classes']}")
        print(f"  transitive_sources = {data['transitive_sources']}")
        print(f"  examples = {data['examples']}")

    assert aggregate["reachable_abstract_witnesses"] == 0
    print("JANUS_GT_TRANSITIVE_CYCLE_PAIR_REACHABILITY = PASS")
    print(f"ROWS = {tuple(rows)}")
    print(f"AGGREGATE_COUNTS = {tuple(sorted(aggregate.items()))}")
    print(f"AGGREGATE_RESULT_CLASSES = {tuple(sorted(aggregate_results.items()))}")
    print(f"AGGREGATE_TRANSITIVE_SOURCES = {tuple(sorted(aggregate_sources.items()))}")
    print(
        "claim_boundary = finite exact-key reachability audit through GT_8; "
        "absence is not an arbitrary-n theorem"
    )


if __name__ == "__main__":
    self_test()
