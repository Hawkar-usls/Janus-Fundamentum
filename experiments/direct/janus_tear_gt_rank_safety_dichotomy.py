#!/usr/bin/env python3
"""Classify every pre-frontier clause by the cycle-or-spanning safety dichotomy.

The earlier sink-rooted directed class was too narrow: an arbitrarily oriented
component-spanning tree is still safe because every strict narrowing contracts a
novel component edge.  The corrected structural classes are:

- DIRECTED_CYCLE: falsifying all external literals would create a reverse cycle;
- COMPONENT_SPANNING: graphic rank equals current component count minus one;
- INTERNAL_ONLY: no external component edge;
- UNSAFE_ACYCLIC_LOW_RANK: no directed cycle and external graphic rank below
  the spanning threshold.

Only the last class can potentially become a component-joining unit without
carrying the full historical component-connectivity charge.
"""

from __future__ import annotations

from collections import Counter, defaultdict

from janus_tear_gt_component_tree_clause_audit import (
    DSU,
    clause_component_graph,
    execution_context,
)
from janus_tear_gt_directed_component_clause_audit import directed_edges, has_directed_cycle


def graphic_rank(component_count: int, external_edges) -> int:
    dsu = DSU(component_count)
    for left, right, _literal in external_edges:
        dsu.union(int(left), int(right))
    return component_count - len(
        {dsu.find(component) for component in range(component_count)}
    )


def safety_class(n, clause, assignment, pairs):
    graph = clause_component_graph(n, tuple(clause), assignment, pairs)
    external, internal = directed_edges(tuple(clause), graph, pairs)
    component_count = int(graph["component_count"])
    rank = graphic_rank(component_count, external)
    directed_cycle = has_directed_cycle(component_count, external)

    if directed_cycle:
        classification = "DIRECTED_CYCLE"
    elif rank == component_count - 1:
        classification = "COMPONENT_SPANNING"
    elif not external:
        classification = "INTERNAL_ONLY"
    else:
        classification = "UNSAFE_ACYCLIC_LOW_RANK"

    return {
        "classification": classification,
        "component_count": component_count,
        "graphic_rank": rank,
        "rank_deficit": component_count - 1 - rank,
        "directed_cycle": directed_cycle,
        "external_edges": external,
        "internal_literals": internal,
        "undirected_class": graph["classification"],
    }


def audit(n: int):
    context = execution_context(n)
    policy = context["policy"]
    pairs = context["pairs"]
    levels = context["levels"]
    target = n - 2

    stage_counts: dict[str, Counter[str]] = defaultdict(Counter)
    deficit_histogram: dict[str, Counter[int]] = defaultdict(Counter)
    width_histogram: dict[str, Counter[int]] = defaultdict(Counter)
    unsafe_examples = []
    unsafe_new_resolvents = 0
    total = 0

    def inspect(stage, state_id, call_id, novelty, clause, assignment):
        nonlocal total, unsafe_new_resolvents
        structure = safety_class(n, tuple(clause), assignment, pairs)
        classification = str(structure["classification"])
        stage_counts[stage][classification] += 1
        deficit_histogram[classification][int(structure["rank_deficit"])] += 1
        width_histogram[classification][len(tuple(clause))] += 1
        total += 1
        if classification == "UNSAFE_ACYCLIC_LOW_RANK":
            if stage == "NEW_RESOLVENT":
                unsafe_new_resolvents += 1
            if len(unsafe_examples) < 40:
                unsafe_examples.append(
                    {
                        "stage": stage,
                        "state_id": state_id,
                        "call_id": call_id,
                        "novelty": novelty,
                        "clause": tuple(clause),
                        "width": len(tuple(clause)),
                        "structure": structure,
                    }
                )

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

    unsafe_by_stage = tuple(
        (stage, histogram["UNSAFE_ACYCLIC_LOW_RANK"])
        for stage, histogram in sorted(stage_counts.items())
    )
    unsafe_total = sum(count for _stage, count in unsafe_by_stage)

    return {
        "n": n,
        "target": target,
        "total_clause_occurrences": total,
        "stage_counts": tuple(
            (stage, tuple(sorted(histogram.items())))
            for stage, histogram in sorted(stage_counts.items())
        ),
        "deficit_histogram": tuple(
            (classification, tuple(sorted(histogram.items())))
            for classification, histogram in sorted(deficit_histogram.items())
        ),
        "width_histogram": tuple(
            (classification, tuple(sorted(histogram.items())))
            for classification, histogram in sorted(width_histogram.items())
        ),
        "unsafe_by_stage": unsafe_by_stage,
        "unsafe_total": unsafe_total,
        "unsafe_new_resolvents": unsafe_new_resolvents,
        "unsafe_examples": tuple(unsafe_examples),
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
                data["unsafe_new_resolvents"],
                data["unsafe_by_stage"],
            )
        )
        print(f"ORDER_SIZE = {n}")
        print(f"  target = {data['target']}")
        print(f"  total_clause_occurrences = {data['total_clause_occurrences']}")
        print(f"  stage_counts = {data['stage_counts']}")
        print(f"  deficit_histogram = {data['deficit_histogram']}")
        print(f"  unsafe_total = {data['unsafe_total']}")
        print(f"  unsafe_new_resolvents = {data['unsafe_new_resolvents']}")
        print(f"  unsafe_by_stage = {data['unsafe_by_stage']}")
        print(f"  unsafe_examples = {data['unsafe_examples']}")

    print("JANUS_GT_RANK_SAFETY_DICHOTOMY = PASS")
    print(f"rows = {tuple(rows)}")
    print(
        "aggregate_stage_counts = "
        f"{tuple((stage, tuple(sorted(histogram.items()))) for stage, histogram in sorted(aggregate_stage.items()))}"
    )
    print(f"unsafe_sizes = {tuple(unsafe_sizes)}")
    print("claim_boundary = finite cycle-or-spanning classification; universal Resolution closure remains false")


if __name__ == "__main__":
    self_test()
