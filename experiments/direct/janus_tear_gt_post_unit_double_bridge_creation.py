#!/usr/bin/env python3
"""Audit post-unit action on GT double-bridge pairs.

An earlier draft misread extra raw pairs as 553 pairs created by post-unit
propagation.  Exact replay falsifies that interpretation.

For a reached state write:

    R = frozen one-pass Resolution output
    P = residual after post-unit closure

Across the finite pre-frontier GT_4,...,GT_8 trace, post-units create no
new double-bridge pair.  One raw same-cut fresh/fresh unit pair in GT_5 closes
immediately and therefore has no P.  Every pair-bearing state with a surviving
P has an empty post-unit batch and R=P.

This checker counts all R pairs, including terminal post-unit states, and then
matches every surviving P pair to an R source pair.  It certifies finite
noncreation plus one terminal extinction; it does not claim arbitrary-n
post-unit vacuity.
"""

from __future__ import annotations

from collections import Counter
from itertools import product

from janus_tear_gt_component_merge_sources import reduce_clause
from janus_tear_gt_component_tree_clause_audit import execution_context
from janus_tear_gt_double_bridge_local_creation import is_double_bridge_source
from janus_tear_gt_double_bridge_transition_birth import (
    enumerate_double_bridges,
    unit_assignments,
)

Clause = tuple[int, ...]


def residual_sources(
    clauses: tuple[Clause, ...], assignments: dict[int, bool]
) -> dict[Clause, tuple[Clause, ...]]:
    sources: dict[Clause, list[Clause]] = {}
    for clause in clauses:
        residual = reduce_clause(clause, assignments)
        if residual is None:
            continue
        sources.setdefault(tuple(residual), []).append(clause)
    return {
        residual: tuple(raw_sources)
        for residual, raw_sources in sources.items()
    }


def unit_event_literals(state) -> tuple[int, ...]:
    return tuple(
        int(event["literal"])
        for event in state.get("post_units", ())
        if event["kind"] == "unit"
    )


def audit(n: int):
    context = execution_context(n)
    policy = context["policy"]
    pairs = context["pairs"]
    levels = context["levels"]
    target = n - 2

    counts: Counter[str] = Counter()
    all_state_unit_histogram: Counter[int] = Counter()
    output_pair_state_unit_histogram: Counter[int] = Counter()
    surviving_pair_state_unit_histogram: Counter[int] = Counter()
    output_cut_relation: Counter[str] = Counter()
    post_cut_relation: Counter[str] = Counter()
    terminal_eliminated_cut_relation: Counter[str] = Counter()
    terminal_labels: Counter[str] = Counter()
    examples = []

    for state in policy.states.values():
        state_id = int(state["id"])
        call_id = int(state["entry_call"])
        novelty = int(levels[call_id])
        if novelty > target:
            continue

        before_assignment = context["call_after_pre"][call_id]
        output = tuple(tuple(clause) for clause in state["resolution_output"])
        output_pairs = enumerate_double_bridges(
            n, output, before_assignment, pairs
        )
        unit_literals = unit_event_literals(state)
        all_state_unit_histogram[len(unit_literals)] += 1

        counts["resolution_output_pair_occurrences"] += len(output_pairs)
        if output_pairs:
            counts["resolution_output_pair_bearing_states"] += 1
            output_pair_state_unit_histogram[len(unit_literals)] += 1

        for record in output_pairs:
            same_cut = (
                record["left_bridge"]["cut"]
                == record["right_bridge"]["cut"]
            )
            output_cut_relation[
                "SAME_CUT" if same_cut else "DIFFERENT_CUT"
            ] += 1

        post_result = state.get("post_result")
        if post_result is None:
            if output_pairs:
                counts["output_pair_occurrences_eliminated_before_post"] += len(
                    output_pairs
                )
                counts["output_pair_bearing_terminal_states"] += 1
                terminal = str(state.get("terminal"))
                terminal_labels[terminal] += 1
                for record in output_pairs:
                    same_cut = (
                        record["left_bridge"]["cut"]
                        == record["right_bridge"]["cut"]
                    )
                    terminal_eliminated_cut_relation[
                        "SAME_CUT" if same_cut else "DIFFERENT_CUT"
                    ] += 1
                if len(examples) < 30:
                    examples.append({
                        "n": n,
                        "state_id": state_id,
                        "call_id": call_id,
                        "novelty": novelty,
                        "kind": "TERMINAL_POST_UNIT_EXTINCTION",
                        "terminal": terminal,
                        "unit_literals": unit_literals,
                        "output_pairs": output_pairs,
                    })
            continue

        post_units = unit_assignments(state.get("post_units", ()))
        after_assignment = context["state_after_post"][state_id]
        post = tuple(tuple(clause) for clause in post_result)
        post_pairs = enumerate_double_bridges(
            n, post, after_assignment, pairs
        )
        counts["post_result_pair_occurrences"] += len(post_pairs)

        for record in post_pairs:
            same_cut = (
                record["left_bridge"]["cut"]
                == record["right_bridge"]["cut"]
            )
            post_cut_relation[
                "SAME_CUT" if same_cut else "DIFFERENT_CUT"
            ] += 1

        if output_pairs or post_pairs:
            counts["surviving_pair_stage_states"] += 1
            surviving_pair_state_unit_histogram[len(post_units)] += 1
            if post_units:
                counts["surviving_pair_stage_states_with_post_units"] += 1
            if output != post:
                counts["surviving_pair_stage_states_with_formula_change"] += 1

        sources = residual_sources(output, post_units)
        assert set(post) == set(sources)

        for record in post_pairs:
            pivot = int(record["pivot"])
            left = tuple(record["left"])
            right = tuple(record["right"])
            has_source_pair = any(
                is_double_bridge_source(
                    n,
                    left_source,
                    right_source,
                    pivot,
                    before_assignment,
                    pairs,
                )
                is not None
                for left_source, right_source in product(
                    sources[left], sources[right]
                )
            )
            if not has_source_pair:
                counts["post_unit_created_pair_occurrences"] += 1
                if len(examples) < 30:
                    examples.append({
                        "n": n,
                        "state_id": state_id,
                        "call_id": call_id,
                        "novelty": novelty,
                        "kind": "POST_UNIT_CREATED_PAIR",
                        "post_units": tuple(sorted(post_units.items())),
                        "pivot": pivot,
                        "left": left,
                        "right": right,
                        "left_sources": sources[left],
                        "right_sources": sources[right],
                    })

    return {
        "n": n,
        "target": target,
        "counts": tuple(sorted(counts.items())),
        "all_state_unit_histogram": tuple(sorted(all_state_unit_histogram.items())),
        "output_pair_state_unit_histogram": tuple(
            sorted(output_pair_state_unit_histogram.items())
        ),
        "surviving_pair_state_unit_histogram": tuple(
            sorted(surviving_pair_state_unit_histogram.items())
        ),
        "output_cut_relation": tuple(sorted(output_cut_relation.items())),
        "post_cut_relation": tuple(sorted(post_cut_relation.items())),
        "terminal_eliminated_cut_relation": tuple(
            sorted(terminal_eliminated_cut_relation.items())
        ),
        "terminal_labels": tuple(sorted(terminal_labels.items())),
        "examples": tuple(examples),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_all_units: Counter[int] = Counter()
    aggregate_output_pair_units: Counter[int] = Counter()
    aggregate_surviving_pair_units: Counter[int] = Counter()
    aggregate_output_cuts: Counter[str] = Counter()
    aggregate_post_cuts: Counter[str] = Counter()
    aggregate_eliminated_cuts: Counter[str] = Counter()
    aggregate_terminals: Counter[str] = Counter()
    rows = []

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_all_units.update(dict(data["all_state_unit_histogram"]))
        aggregate_output_pair_units.update(
            dict(data["output_pair_state_unit_histogram"])
        )
        aggregate_surviving_pair_units.update(
            dict(data["surviving_pair_state_unit_histogram"])
        )
        aggregate_output_cuts.update(dict(data["output_cut_relation"]))
        aggregate_post_cuts.update(dict(data["post_cut_relation"]))
        aggregate_eliminated_cuts.update(
            dict(data["terminal_eliminated_cut_relation"])
        )
        aggregate_terminals.update(dict(data["terminal_labels"]))
        rows.append((
            n,
            data["target"],
            data["counts"],
            data["output_pair_state_unit_histogram"],
            data["surviving_pair_state_unit_histogram"],
            data["output_cut_relation"],
            data["post_cut_relation"],
            data["terminal_eliminated_cut_relation"],
        ))
        print(f"ORDER_SIZE = {n}")
        print(f"  target = {data['target']}")
        print(f"  counts = {data['counts']}")
        print(f"  all_state_unit_histogram = {data['all_state_unit_histogram']}")
        print(f"  output_pair_state_unit_histogram = {data['output_pair_state_unit_histogram']}")
        print(f"  surviving_pair_state_unit_histogram = {data['surviving_pair_state_unit_histogram']}")
        print(f"  output_cut_relation = {data['output_cut_relation']}")
        print(f"  post_cut_relation = {data['post_cut_relation']}")
        print(f"  terminal_eliminated_cut_relation = {data['terminal_eliminated_cut_relation']}")
        print(f"  terminal_labels = {data['terminal_labels']}")
        print(f"  examples = {data['examples']}")

    assert aggregate_counts["post_unit_created_pair_occurrences"] == 0
    assert aggregate_counts["resolution_output_pair_occurrences"] == 1391
    assert aggregate_counts["post_result_pair_occurrences"] == 1390
    assert aggregate_counts["output_pair_occurrences_eliminated_before_post"] == 1
    assert aggregate_counts["output_pair_bearing_terminal_states"] == 1
    assert aggregate_counts["surviving_pair_stage_states_with_post_units"] == 0
    assert aggregate_counts["surviving_pair_stage_states_with_formula_change"] == 0
    assert aggregate_output_cuts == Counter({"DIFFERENT_CUT": 1389, "SAME_CUT": 2})
    assert aggregate_post_cuts == Counter({"DIFFERENT_CUT": 1389, "SAME_CUT": 1})
    assert aggregate_eliminated_cuts == Counter({"SAME_CUT": 1})
    assert aggregate_surviving_pair_units == Counter({
        0: aggregate_counts["surviving_pair_stage_states"]
    })

    print("JANUS_GT_POST_UNIT_DOUBLE_BRIDGE_NONCREATION = PASS")
    print(f"ROWS = {tuple(rows)}")
    print(f"AGGREGATE_COUNTS = {tuple(sorted(aggregate_counts.items()))}")
    print(f"AGGREGATE_ALL_STATE_UNITS = {tuple(sorted(aggregate_all_units.items()))}")
    print(f"AGGREGATE_OUTPUT_PAIR_UNITS = {tuple(sorted(aggregate_output_pair_units.items()))}")
    print(f"AGGREGATE_SURVIVING_PAIR_UNITS = {tuple(sorted(aggregate_surviving_pair_units.items()))}")
    print(f"AGGREGATE_OUTPUT_CUT_RELATION = {tuple(sorted(aggregate_output_cuts.items()))}")
    print(f"AGGREGATE_POST_CUT_RELATION = {tuple(sorted(aggregate_post_cuts.items()))}")
    print(f"AGGREGATE_ELIMINATED_CUT_RELATION = {tuple(sorted(aggregate_eliminated_cuts.items()))}")
    print(f"AGGREGATE_TERMINAL_LABELS = {tuple(sorted(aggregate_terminals.items()))}")
    print(
        "claim_boundary = exact finite post-unit noncreation plus one "
        "terminal same-cut extinction through GT_8; arbitrary-n open"
    )


if __name__ == "__main__":
    self_test()
