#!/usr/bin/env python3
"""Classify the fate of every fresh local non-tail bridge with merged tail.

The raw local census through GT_8 contains 18 fresh non-tail bridge literals
whose oriented tail Hasse component has size greater than one.  None appears in
the later exact-key survivor census.  This diagnostic checker determines why:
terminal state, post-unit elimination, branch satisfaction, child terminality,
or absence from every child exact key.

The first version records the exact finite fate histogram and only asserts that
all 18 lineages fail to become a later exact-key bad occurrence.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_component_merge_sources import reduce_clause
from janus_tear_gt_component_tree_clause_audit import (
    clause_component_graph,
    execution_context,
)
from janus_tear_gt_global_clause_shrink_census import unit_assignments
from janus_tear_gt_local_resolution_bad_bridge_birth_v2 import audit as raw_audit
from janus_tear_gt_bridge_endpoint_profile import bridge_record
from janus_tear_gt_rank_safety_dichotomy import safety_class


def child_contains_bad(
    n: int,
    child_state,
    event_literal: int,
    pairs,
    child_assignment,
) -> bool:
    for clause in tuple(child_state["key"]):
        if event_literal not in clause:
            continue
        classification = str(
            safety_class(n, clause, child_assignment, pairs)["classification"]
        )
        if classification != "COMPONENT_SPANNING":
            continue
        graph = clause_component_graph(n, clause, child_assignment, pairs)
        record = bridge_record(clause, graph, pairs, event_literal)
        if record is not None and record["role"] != "TAIL_SINGLETON":
            return True
    return False


def audit(n: int):
    context = execution_context(n)
    policy = context["policy"]
    pairs = context["pairs"]
    levels = context["levels"]
    raw = raw_audit(n)
    call_to_state = {
        int(state["entry_call"]): int(state["id"])
        for state in policy.states.values()
    }

    counts: Counter[str] = Counter()
    novelty_histogram: Counter[int] = Counter()
    terminal_histogram: Counter[str] = Counter()
    post_unit_histogram: Counter[int] = Counter()
    post_clause_widths: Counter[int] = Counter()
    child_outcomes: Counter[str] = Counter()
    examples = []

    for example in raw["fresh_examples"]:
        tail_size, head_size = tuple(example["endpoint_shape"])
        if int(tail_size) <= 1:
            continue

        counts["fresh_merged_tail_occurrences"] += 1
        state_id = int(example["state_id"])
        call_id = int(example["call_id"])
        literal = int(example["literal"])
        event_clause = tuple(example["resolvent"])
        state = policy.states[state_id]
        novelty = int(levels[call_id])
        novelty_histogram[novelty] += 1
        terminal = str(state["terminal"])
        terminal_histogram[terminal] += 1

        post_units = tuple(state.get("post_units", []))
        post_unit_histogram[len(post_units)] += 1
        post_assignment = unit_assignments(post_units)
        post_clause = reduce_clause(event_clause, post_assignment)
        if post_clause is None:
            counts["satisfied_by_post_units"] += 1
            fate = "SATISFIED_BY_POST_UNITS"
        elif not post_clause:
            counts["emptied_by_post_units"] += 1
            fate = "EMPTIED_BY_POST_UNITS"
        else:
            post_clause_widths[len(post_clause)] += 1
            children = [
                child
                for child in state.get("children", [])
                if child.get("call") is not None
            ]
            if not children:
                counts["no_child_call"] += 1
                fate = f"TERMINAL_{terminal}"
            else:
                surviving_bad_children = 0
                terminal_children = 0
                absent_children = 0
                for child in children:
                    child_call = int(child["call"])
                    child_state_id = call_to_state.get(child_call)
                    if child_state_id is None:
                        terminal_children += 1
                        child_outcomes["NO_EXACT_KEY"] += 1
                        continue
                    child_state = policy.states[child_state_id]
                    child_assignment = context["call_after_pre"][child_call]
                    if child_contains_bad(
                        n,
                        child_state,
                        literal,
                        pairs,
                        child_assignment,
                    ):
                        surviving_bad_children += 1
                        child_outcomes["BAD_EXACT_KEY"] += 1
                    else:
                        absent_children += 1
                        child_outcomes["ABSENT_OR_SAFE"] += 1

                assert surviving_bad_children == 0
                counts["branching_without_bad_child"] += 1
                fate = (
                    f"BRANCH_CHILDREN_terminal={terminal_children}_"
                    f"absent_or_safe={absent_children}"
                )

        if len(examples) < 40:
            examples.append({
                "n": n,
                "state_id": state_id,
                "call_id": call_id,
                "novelty": novelty,
                "target": n - 2,
                "event_index": int(example["event_index"]),
                "pivot": int(example["pivot"]),
                "literal": literal,
                "event_clause": event_clause,
                "endpoint_shape": (int(tail_size), int(head_size)),
                "result_role": str(example["result_role"]),
                "terminal": terminal,
                "post_units": post_units,
                "post_clause": post_clause,
                "fate": fate,
            })

    return {
        "n": n,
        "counts": tuple(sorted(counts.items())),
        "novelty_histogram": tuple(sorted(novelty_histogram.items())),
        "terminal_histogram": tuple(sorted(terminal_histogram.items())),
        "post_unit_histogram": tuple(sorted(post_unit_histogram.items())),
        "post_clause_widths": tuple(sorted(post_clause_widths.items())),
        "child_outcomes": tuple(sorted(child_outcomes.items())),
        "examples": tuple(examples),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_novelty: Counter[tuple[int, int]] = Counter()
    aggregate_terminal: Counter[str] = Counter()
    aggregate_post_units: Counter[int] = Counter()
    aggregate_widths: Counter[int] = Counter()
    aggregate_children: Counter[str] = Counter()

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        for novelty, count in data["novelty_histogram"]:
            aggregate_novelty[(n, novelty)] += count
        aggregate_terminal.update(dict(data["terminal_histogram"]))
        aggregate_post_units.update(dict(data["post_unit_histogram"]))
        aggregate_widths.update(dict(data["post_clause_widths"]))
        aggregate_children.update(dict(data["child_outcomes"]))
        print(f"ORDER_SIZE = {n}")
        print(f"  counts = {data['counts']}")
        print(f"  novelty_histogram = {data['novelty_histogram']}")
        print(f"  terminal_histogram = {data['terminal_histogram']}")
        print(f"  post_unit_histogram = {data['post_unit_histogram']}")
        print(f"  post_clause_widths = {data['post_clause_widths']}")
        print(f"  child_outcomes = {data['child_outcomes']}")
        print(f"  examples = {data['examples']}")

    assert aggregate_counts["fresh_merged_tail_occurrences"] == 18
    assert aggregate_children.get("BAD_EXACT_KEY", 0) == 0
    print("JANUS_GT_MERGED_TAIL_FATE_CENSUS = PASS")
    print(f"aggregate_counts = {tuple(sorted(aggregate_counts.items()))}")
    print(f"aggregate_novelty = {tuple(sorted(aggregate_novelty.items()))}")
    print(f"aggregate_terminal = {tuple(sorted(aggregate_terminal.items()))}")
    print(f"aggregate_post_units = {tuple(sorted(aggregate_post_units.items()))}")
    print(f"aggregate_post_clause_widths = {tuple(sorted(aggregate_widths.items()))}")
    print(f"aggregate_child_outcomes = {tuple(sorted(aggregate_children.items()))}")
    print(
        "claim_boundary = finite merged-tail fate census through GT_8; "
        "arbitrary-n extinction proof remains open"
    )


if __name__ == "__main__":
    self_test()
