#!/usr/bin/env python3
"""Audit the post-unit stage for GT double-bridge pairs.

An earlier draft misread the difference between entry-key pairs and raw
post-result pairs as 553 pairs created by post-unit propagation.  Exact replay
shows that interpretation is false: every pre-frontier state containing a raw
post-result double-bridge pair has an empty post-unit batch.  The extra raw
pairs are created by the frozen local-Resolution pass, not by units.

This checker keeps the operational stages separate:

    K = exact entry key
    R = frozen one-pass Resolution output
    P = post-unit residual

For GT_4,...,GT_8 up to novelty level n-2 it records:

- all double-bridge occurrences in R and P;
- all states in which either stage contains such a pair;
- whether a nonempty post-unit batch acts on a pair-bearing R;
- whether a P-pair lacks a double-bridge source pair in R;
- whether R and P differ in any pair-bearing state.

The finite regression target is post-unit vacuity on the observed pair-bearing
frontier.  This does not prove arbitrary-n vacuity and does not forbid units in
other Policy-0A states.
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


def audit(n: int):
    context = execution_context(n)
    policy = context["policy"]
    pairs = context["pairs"]
    levels = context["levels"]
    target = n - 2

    counts: Counter[str] = Counter()
    post_unit_histogram: Counter[int] = Counter()
    pair_state_unit_histogram: Counter[int] = Counter()
    output_cut_relation: Counter[str] = Counter()
    post_cut_relation: Counter[str] = Counter()
    examples = []

    for state in policy.states.values():
        state_id = int(state["id"])
        call_id = int(state["entry_call"])
        novelty = int(levels[call_id])
        if novelty > target:
            continue

        post_result = state.get("post_result")
        if post_result is None:
            continue

        before_assignment = context["call_after_pre"][call_id]
        after_assignment = context["state_after_post"][state_id]
        output = tuple(tuple(clause) for clause in state["resolution_output"])
        post = tuple(tuple(clause) for clause in post_result)
        post_units = unit_assignments(state.get("post_units", ()))
        post_unit_histogram[len(post_units)] += 1

        output_pairs = enumerate_double_bridges(
            n, output, before_assignment, pairs
        )
        post_pairs = enumerate_double_bridges(
            n, post, after_assignment, pairs
        )
        counts["resolution_output_pair_occurrences"] += len(output_pairs)
        counts["post_result_pair_occurrences"] += len(post_pairs)

        for record in output_pairs:
            same_cut = record["left_bridge"]["cut"] == record["right_bridge"]["cut"]
            output_cut_relation[
                "SAME_CUT" if same_cut else "DIFFERENT_CUT"
            ] += 1
        for record in post_pairs:
            same_cut = record["left_bridge"]["cut"] == record["right_bridge"]["cut"]
            post_cut_relation[
                "SAME_CUT" if same_cut else "DIFFERENT_CUT"
            ] += 1

        if not output_pairs and not post_pairs:
            continue

        counts["pair_bearing_states"] += 1
        pair_state_unit_histogram[len(post_units)] += 1
        if post_units:
            counts["pair_bearing_states_with_post_units"] += 1
        if output != post:
            counts["pair_bearing_states_with_formula_change"] += 1

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
                if len(examples) < 40:
                    examples.append({
                        "n": n,
                        "state_id": state_id,
                        "call_id": call_id,
                        "novelty": novelty,
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
        "post_unit_histogram": tuple(sorted(post_unit_histogram.items())),
        "pair_state_unit_histogram": tuple(
            sorted(pair_state_unit_histogram.items())
        ),
        "output_cut_relation": tuple(sorted(output_cut_relation.items())),
        "post_cut_relation": tuple(sorted(post_cut_relation.items())),
        "examples": tuple(examples),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_post_units: Counter[int] = Counter()
    aggregate_pair_state_units: Counter[int] = Counter()
    aggregate_output_cuts: Counter[str] = Counter()
    aggregate_post_cuts: Counter[str] = Counter()
    rows = []

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_post_units.update(dict(data["post_unit_histogram"]))
        aggregate_pair_state_units.update(dict(data["pair_state_unit_histogram"]))
        aggregate_output_cuts.update(dict(data["output_cut_relation"]))
        aggregate_post_cuts.update(dict(data["post_cut_relation"]))
        rows.append((
            n,
            data["target"],
            data["counts"],
            data["pair_state_unit_histogram"],
            data["output_cut_relation"],
            data["post_cut_relation"],
        ))
        print(f"ORDER_SIZE = {n}")
        print(f"  target = {data['target']}")
        print(f"  counts = {data['counts']}")
        print(f"  post_unit_histogram = {data['post_unit_histogram']}")
        print(f"  pair_state_unit_histogram = {data['pair_state_unit_histogram']}")
        print(f"  output_cut_relation = {data['output_cut_relation']}")
        print(f"  post_cut_relation = {data['post_cut_relation']}")
        print(f"  examples = {data['examples']}")

    assert aggregate_counts["post_unit_created_pair_occurrences"] == 0
    assert aggregate_counts["pair_bearing_states_with_post_units"] == 0
    assert aggregate_counts["pair_bearing_states_with_formula_change"] == 0
    assert aggregate_counts["resolution_output_pair_occurrences"] == 1390
    assert aggregate_counts["post_result_pair_occurrences"] == 1390
    assert aggregate_pair_state_units == Counter({0: aggregate_counts["pair_bearing_states"]})
    assert aggregate_output_cuts == Counter({"DIFFERENT_CUT": 1389, "SAME_CUT": 1})
    assert aggregate_post_cuts == aggregate_output_cuts

    print("JANUS_GT_POST_UNIT_DOUBLE_BRIDGE_VACUITY = PASS")
    print(f"ROWS = {tuple(rows)}")
    print(f"AGGREGATE_COUNTS = {tuple(sorted(aggregate_counts.items()))}")
    print(f"AGGREGATE_POST_UNITS = {tuple(sorted(aggregate_post_units.items()))}")
    print(f"AGGREGATE_PAIR_STATE_UNITS = {tuple(sorted(aggregate_pair_state_units.items()))}")
    print(f"AGGREGATE_OUTPUT_CUT_RELATION = {tuple(sorted(aggregate_output_cuts.items()))}")
    print(f"AGGREGATE_POST_CUT_RELATION = {tuple(sorted(aggregate_post_cuts.items()))}")
    print(
        "claim_boundary = exact finite post-unit vacuity on pair-bearing "
        "GT_4,...,GT_8 states through novelty n-2; arbitrary-n open"
    )


if __name__ == "__main__":
    self_test()
