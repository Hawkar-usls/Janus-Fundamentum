#!/usr/bin/env python3
"""Test a directed safety dichotomy on every pre-frontier Policy-0A clause.

Quotient a clause by the current Hasse components and ignore internal literals.
The candidate GT clause classes are:

- DIRECTED_CYCLE: the external graph contains a directed cycle;
- ROOT_REACHING: some component root is reachable by a directed path from every
  current component;
- INTERNAL_ONLY: no external edge remains, so the clause cannot itself be a
  component-joining unit.

A clause outside all three classes is UNSAFE_DIRECTED_FOREST.  Such a clause
could in principle narrow to an early external unit on only a proper subset of
components.  This audit checks every clause in the exact state key, every clause
in the one-pass Resolution output, every post-unit residual clause, and every
new local resolvent before novelty level n-2.
"""

from __future__ import annotations

from collections import Counter, defaultdict

from janus_tear_gt_component_tree_clause_audit import (
    clause_component_graph,
    execution_context,
)
from janus_tear_gt_directed_component_clause_audit import directed_edges, has_directed_cycle


def roots_reachable_from_all(component_count, edges):
    reverse = defaultdict(list)
    for tail, head, _literal in edges:
        reverse[head].append(tail)

    roots = []
    for root in range(component_count):
        seen = set()
        stack = [root]
        while stack:
            vertex = stack.pop()
            if vertex in seen:
                continue
            seen.add(vertex)
            stack.extend(reverse.get(vertex, ()))
        if len(seen) == component_count:
            roots.append(root)
    return tuple(roots)


def safety_class(n, clause, assignment, pairs):
    graph = clause_component_graph(n, clause, assignment, pairs)
    external, internal = directed_edges(clause, graph, pairs)
    component_count = int(graph["component_count"])
    directed_cycle = has_directed_cycle(component_count, external)
    roots = roots_reachable_from_all(component_count, external)

    if directed_cycle:
        classification = "DIRECTED_CYCLE"
    elif roots:
        classification = "ROOT_REACHING"
    elif not external:
        classification = "INTERNAL_ONLY"
    else:
        classification = "UNSAFE_DIRECTED_FOREST"

    return {
        "classification": classification,
        "roots": roots,
        "directed_cycle": directed_cycle,
        "external_edges": external,
        "internal_literals": internal,
        "component_count": component_count,
        "undirected_class": graph["classification"],
    }


def audit(n: int):
    context = execution_context(n)
    policy = context["policy"]
    pairs = context["pairs"]
    levels = context["levels"]
    target = n - 2

    stage_counts: dict[str, Counter[str]] = defaultdict(Counter)
    width_counts: dict[str, Counter[int]] = defaultdict(Counter)
    unsafe_examples = []
    selected_rooted_examples = []
    selected_cycle_examples = []
    total_occurrences = 0

    def inspect(stage, state_id, call_id, novelty, clause, assignment):
        nonlocal total_occurrences
        result = safety_class(n, tuple(clause), assignment, pairs)
        classification = str(result["classification"])
        stage_counts[stage][classification] += 1
        width_counts[classification][len(tuple(clause))] += 1
        total_occurrences += 1
        record = {
            "stage": stage,
            "state_id": state_id,
            "call_id": call_id,
            "novelty": novelty,
            "clause": tuple(clause),
            "width": len(tuple(clause)),
            "classification": classification,
            "roots": result["roots"],
            "component_count": result["component_count"],
            "undirected_class": result["undirected_class"],
            "external_edges": result["external_edges"],
            "internal_literals": result["internal_literals"],
        }
        if classification == "UNSAFE_DIRECTED_FOREST" and len(unsafe_examples) < 30:
            unsafe_examples.append(record)
        elif classification == "ROOT_REACHING" and len(selected_rooted_examples) < 10:
            selected_rooted_examples.append(record)
        elif classification == "DIRECTED_CYCLE" and len(selected_cycle_examples) < 10:
            selected_cycle_examples.append(record)

    for state in policy.states.values():
        state_id = int(state["id"])
        call_id = int(state["entry_call"])
        novelty = int(levels[call_id])
        if novelty > target:
            continue
        before_assignment = context["call_after_pre"][call_id]
        after_assignment = context["state_after_post"].get(
            state_id, before_assignment
        )

        for clause in tuple(state["key"]):
            inspect("KEY", state_id, call_id, novelty, clause, before_assignment)
        for clause in tuple(state["resolution_output"]):
            inspect(
                "RESOLUTION_OUTPUT",
                state_id,
                call_id,
                novelty,
                clause,
                before_assignment,
            )
        for clause in tuple(state.get("post_result") or ()):
            inspect("POST_RESULT", state_id, call_id, novelty, clause, after_assignment)
        for event in state.get("resolution_events", []):
            inspect(
                "NEW_RESOLVENT",
                state_id,
                call_id,
                novelty,
                tuple(event["resolvent"]),
                before_assignment,
            )

    unsafe_total = sum(
        histogram["UNSAFE_DIRECTED_FOREST"]
        for histogram in stage_counts.values()
    )

    return {
        "n": n,
        "target": target,
        "total_clause_occurrences": total_occurrences,
        "stage_counts": tuple(
            (stage, tuple(sorted(histogram.items())))
            for stage, histogram in sorted(stage_counts.items())
        ),
        "width_counts": tuple(
            (classification, tuple(sorted(histogram.items())))
            for classification, histogram in sorted(width_counts.items())
        ),
        "unsafe_total": unsafe_total,
        "unsafe_examples": tuple(unsafe_examples),
        "rooted_examples": tuple(selected_rooted_examples),
        "cycle_examples": tuple(selected_cycle_examples),
    }


def self_test() -> None:
    rows = []
    aggregate_stage: dict[str, Counter[str]] = defaultdict(Counter)
    unsafe_sizes = []

    for n in range(4, 9):
        data = audit(n)
        for stage, histogram in data["stage_counts"]:
            aggregate_stage[stage].update(dict(histogram))
        if data["unsafe_total"]:
            unsafe_sizes.append(n)
        rows.append(
            (
                n,
                data["target"],
                data["total_clause_occurrences"],
                data["unsafe_total"],
                data["stage_counts"],
            )
        )
        print(f"ORDER_SIZE = {n}")
        print(f"  target = {data['target']}")
        print(f"  total_clause_occurrences = {data['total_clause_occurrences']}")
        print(f"  stage_counts = {data['stage_counts']}")
        print(f"  width_counts = {data['width_counts']}")
        print(f"  unsafe_total = {data['unsafe_total']}")
        print(f"  unsafe_examples = {data['unsafe_examples']}")
        print(f"  rooted_examples = {data['rooted_examples']}")
        print(f"  cycle_examples = {data['cycle_examples']}")

    print("JANUS_GT_DIRECTED_SAFETY_DICHOTOMY = PASS")
    print(f"rows = {tuple(rows)}")
    print(
        "aggregate_stage_counts = "
        f"{tuple((stage, tuple(sorted(histogram.items()))) for stage, histogram in sorted(aggregate_stage.items()))}"
    )
    print(f"unsafe_sizes = {tuple(unsafe_sizes)}")
    print("claim_boundary = finite clause-occurrence classification; Resolution closure of the dichotomy remains unproved")


if __name__ == "__main__":
    self_test()
