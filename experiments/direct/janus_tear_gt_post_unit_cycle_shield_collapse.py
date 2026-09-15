#!/usr/bin/env python3
"""Audit every reachable post-unit cycle-shield transition through GT_8.

The pure quotient theorem isolates the only branch-safe birth route:

    a DIRECTED_CYCLE source loses its final cycle shield under contraction,
    and the residual participates in a newly born same-cut bridge pair.

Exact GT replay reveals a stronger finite barrier.  Every post-unit event which
merges relation components starts with exactly two components and merges them
into the single component containing all n vertices.  Directed-cycle shields do
collapse, but their residuals have zero bridge literals because no nontrivial
quotient cut remains.

This checker replays every individual post-unit event before novelty n-2 in the
exact Policy-0A GT_4,...,GT_8 traces and records:

- current and next relation-component shapes;
- every directed-cycle source whose residual is no longer cycle-protected;
- the residual safety class and bridge count of each collapsed source;
- every same-cut pair before and after the unit;
- whether any newly born pair uses a collapsed cycle source;
- terminal opposite-unit conflicts.

The finite target is discovery plus regression.  No arbitrary-n total-component
collapse theorem is claimed here.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from itertools import product

from janus_tear_abstract_post_unit_same_cut_birth_n4 import (
    clause_data,
    is_pre_same_cut,
)
from janus_tear_gt_component_merge_sources import reduce_clause
from janus_tear_gt_component_tree_clause_audit import execution_context
from janus_tear_gt_double_bridge_transition_birth import enumerate_double_bridges
from janus_tear_gt_novel_branch_audit_v2 import comparison_closure, components
from janus_tear_gt_rank_safety_dichotomy import safety_class

Clause = tuple[int, ...]


def component_shape(n: int, assignment, pairs) -> tuple[int, ...]:
    closure = comparison_closure(n, assignment, pairs)
    assert closure.acyclic
    return tuple(sorted(len(part) for part in components(closure)))


def residual_sources(
    clauses: tuple[Clause, ...], assignment: dict[int, bool]
) -> dict[Clause, tuple[Clause, ...]]:
    result: dict[Clause, list[Clause]] = defaultdict(list)
    for source in clauses:
        residual = reduce_clause(source, assignment)
        if residual is None:
            continue
        result[tuple(residual)].append(source)
    return {
        residual: tuple(sources)
        for residual, sources in result.items()
    }


def same_cut_pairs(n, clauses, assignment, pairs):
    return tuple(
        record
        for record in enumerate_double_bridges(
            n, clauses, assignment, pairs
        )
        if record["left_bridge"]["cut"]
        == record["right_bridge"]["cut"]
    )


def bridge_literal_count(n, clause, assignment, pairs) -> int:
    _classes, bridges = clause_data(n, (clause,), assignment, pairs)
    return sum(1 for (candidate, _literal) in bridges if candidate == clause)


def audit(n: int):
    context = execution_context(n)
    policy = context["policy"]
    pairs = context["pairs"]
    levels = context["levels"]
    target = n - 2

    counts: Counter[str] = Counter()
    transition_shapes: Counter[tuple[tuple[int, ...], tuple[int, ...]]] = Counter()
    collapse_classes: Counter[str] = Counter()
    collapse_bridge_counts: Counter[int] = Counter()
    collapse_false_literal: Counter[bool] = Counter()
    collapse_source_widths: Counter[int] = Counter()
    collapse_residual_widths: Counter[int] = Counter()
    birth_source_classes: Counter[tuple[str, str]] = Counter()
    opposite_unit_shapes: Counter[tuple[int, ...]] = Counter()
    examples = []

    for state in policy.states.values():
        state_id = int(state["id"])
        call_id = int(state["entry_call"])
        novelty = int(levels[call_id])
        if novelty > target:
            continue

        events = tuple(state.get("post_units", ()))
        if not events:
            continue

        counts["states_with_post_unit_events"] += 1
        current_assignment = dict(context["call_after_pre"][call_id])
        current_cnf = tuple(tuple(clause) for clause in state["resolution_output"])

        for event_index, event in enumerate(events):
            kind = str(event["kind"])
            if kind == "opposite_units":
                counts["opposite_unit_events"] += 1
                units = tuple(int(literal) for literal in event["units"])
                positive_variables = {literal for literal in units if literal > 0}
                negative_variables = {-literal for literal in units if literal < 0}
                assert positive_variables & negative_variables
                shape = component_shape(n, current_assignment, pairs)
                opposite_unit_shapes[shape] += 1
                raw_same_cut = same_cut_pairs(
                    n, current_cnf, current_assignment, pairs
                )
                counts["same_cut_pairs_at_opposite_unit_terminal"] += len(
                    raw_same_cut
                )
                if len(examples) < 80:
                    examples.append({
                        "n": n,
                        "state_id": state_id,
                        "call_id": call_id,
                        "novelty": novelty,
                        "event_index": event_index,
                        "kind": kind,
                        "units": units,
                        "component_shape": shape,
                        "same_cut_pairs": raw_same_cut,
                    })
                continue

            assert kind == "unit"
            counts["unit_events"] += 1
            literal = int(event["literal"])
            variable = abs(literal)
            value = literal > 0
            assert tuple(event["before"]) == current_cnf

            before_assignment = dict(current_assignment)
            after_assignment = dict(current_assignment)
            assert variable not in after_assignment
            after_assignment[variable] = value
            before_shape = component_shape(n, before_assignment, pairs)
            after_shape = component_shape(n, after_assignment, pairs)
            transition_shapes[(before_shape, after_shape)] += 1
            if before_shape == after_shape:
                counts["internal_or_redundant_unit_events"] += 1
            else:
                counts["component_merging_unit_events"] += 1
                if len(before_shape) == 2 and after_shape == (n,):
                    counts["total_component_collapse_events"] += 1
                else:
                    counts["non_total_component_merge_events"] += 1

            after_raw = event.get("after")
            after_cnf = (
                None
                if after_raw is None
                else tuple(tuple(clause) for clause in after_raw)
            )
            pre_classes, pre_bridges = clause_data(
                n, current_cnf, before_assignment, pairs
            )
            pre_same_cut = same_cut_pairs(
                n, current_cnf, before_assignment, pairs
            )
            counts["pre_unit_same_cut_pair_occurrences"] += len(pre_same_cut)

            false_literal = -literal
            collapsed_sources = []
            if after_cnf is not None:
                source_map = residual_sources(current_cnf, {variable: value})
                assert set(after_cnf) == set(source_map)
                for residual, sources in source_map.items():
                    for source in sources:
                        if pre_classes[source] != "DIRECTED_CYCLE":
                            continue
                        post_class = str(
                            safety_class(
                                n, residual, after_assignment, pairs
                            )["classification"]
                        )
                        if post_class == "DIRECTED_CYCLE":
                            continue
                        counts["cycle_shield_collapses"] += 1
                        collapse_classes[post_class] += 1
                        collapse_source_widths[len(source)] += 1
                        collapse_residual_widths[len(residual)] += 1
                        collapse_false_literal[false_literal in source] += 1
                        bridges = bridge_literal_count(
                            n, residual, after_assignment, pairs
                        )
                        collapse_bridge_counts[bridges] += 1
                        if post_class == "COMPONENT_SPANNING":
                            counts["cycle_to_spanning_collapses"] += 1
                        if bridges:
                            counts["collapsed_sources_with_bridge"] += 1
                        collapsed_sources.append({
                            "source": source,
                            "residual": residual,
                            "post_class": post_class,
                            "bridge_literals": bridges,
                            "contains_false_literal": false_literal in source,
                        })

                post_same_cut = same_cut_pairs(
                    n, after_cnf, after_assignment, pairs
                )
                counts["post_unit_same_cut_pair_occurrences"] += len(
                    post_same_cut
                )

                collapsed_source_set = {
                    item["source"] for item in collapsed_sources
                }
                for record in post_same_cut:
                    pivot = int(record["pivot"])
                    left = tuple(record["left"])
                    right = tuple(record["right"])
                    source_pairs = tuple(product(
                        source_map[left], source_map[right]
                    ))
                    has_pre_same_cut = any(
                        is_pre_same_cut(
                            left_source,
                            right_source,
                            pivot,
                            pre_bridges,
                        )
                        for left_source, right_source in source_pairs
                    )
                    if has_pre_same_cut:
                        counts["transmitted_same_cut_pairs"] += 1
                        continue

                    counts["new_same_cut_births"] += 1
                    birth_has_collapse = False
                    for left_source, right_source in source_pairs:
                        classes = tuple(sorted((
                            pre_classes[left_source],
                            pre_classes[right_source],
                        )))
                        birth_source_classes[classes] += 1
                        if (
                            left_source in collapsed_source_set
                            or right_source in collapsed_source_set
                        ):
                            birth_has_collapse = True
                    if birth_has_collapse:
                        counts["births_using_collapsed_cycle_source"] += 1
                    else:
                        counts["births_without_collapsed_cycle_source"] += 1

                if collapsed_sources and len(examples) < 80:
                    examples.append({
                        "n": n,
                        "state_id": state_id,
                        "call_id": call_id,
                        "novelty": novelty,
                        "event_index": event_index,
                        "kind": kind,
                        "literal": literal,
                        "reason": event.get("reason"),
                        "before_shape": before_shape,
                        "after_shape": after_shape,
                        "collapsed_sources": tuple(collapsed_sources),
                        "pre_same_cut_count": len(pre_same_cut),
                        "post_same_cut_count": len(post_same_cut),
                    })
            else:
                counts["unit_events_causing_formula_contradiction"] += 1

            current_assignment = after_assignment
            if after_cnf is None:
                break
            current_cnf = after_cnf

    assert counts["new_same_cut_births"] == 0
    assert counts["births_without_collapsed_cycle_source"] == 0

    return {
        "n": n,
        "target": target,
        "counts": tuple(sorted(counts.items())),
        "transition_shapes": tuple(sorted(transition_shapes.items(), key=repr)),
        "collapse_classes": tuple(sorted(collapse_classes.items())),
        "collapse_bridge_counts": tuple(sorted(collapse_bridge_counts.items())),
        "collapse_false_literal": tuple(sorted(collapse_false_literal.items())),
        "collapse_source_widths": tuple(sorted(collapse_source_widths.items())),
        "collapse_residual_widths": tuple(sorted(collapse_residual_widths.items())),
        "birth_source_classes": tuple(sorted(birth_source_classes.items(), key=repr)),
        "opposite_unit_shapes": tuple(sorted(opposite_unit_shapes.items())),
        "examples": tuple(examples),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_shapes: Counter[tuple[tuple[int, ...], tuple[int, ...]]] = Counter()
    aggregate_classes: Counter[str] = Counter()
    aggregate_bridge_counts: Counter[int] = Counter()
    aggregate_false_literal: Counter[bool] = Counter()
    aggregate_source_widths: Counter[int] = Counter()
    aggregate_residual_widths: Counter[int] = Counter()
    aggregate_birth_classes: Counter[tuple[str, str]] = Counter()
    aggregate_opposite_shapes: Counter[tuple[int, ...]] = Counter()
    rows = []

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_shapes.update(dict(data["transition_shapes"]))
        aggregate_classes.update(dict(data["collapse_classes"]))
        aggregate_bridge_counts.update(dict(data["collapse_bridge_counts"]))
        aggregate_false_literal.update(dict(data["collapse_false_literal"]))
        aggregate_source_widths.update(dict(data["collapse_source_widths"]))
        aggregate_residual_widths.update(dict(data["collapse_residual_widths"]))
        aggregate_birth_classes.update(dict(data["birth_source_classes"]))
        aggregate_opposite_shapes.update(dict(data["opposite_unit_shapes"]))
        rows.append((
            n,
            data["target"],
            data["counts"],
            data["collapse_classes"],
            data["collapse_bridge_counts"],
            data["transition_shapes"],
        ))
        print(f"ORDER_SIZE = {n}")
        print(f"  target = {data['target']}")
        print(f"  counts = {data['counts']}")
        print(f"  transition_shapes = {data['transition_shapes']}")
        print(f"  collapse_classes = {data['collapse_classes']}")
        print(f"  collapse_bridge_counts = {data['collapse_bridge_counts']}")
        print(f"  collapse_false_literal = {data['collapse_false_literal']}")
        print(f"  collapse_source_widths = {data['collapse_source_widths']}")
        print(f"  collapse_residual_widths = {data['collapse_residual_widths']}")
        print(f"  birth_source_classes = {data['birth_source_classes']}")
        print(f"  opposite_unit_shapes = {data['opposite_unit_shapes']}")
        print(f"  examples = {data['examples']}")

    assert aggregate_counts["unit_events"] == 33
    assert aggregate_counts["component_merging_unit_events"] == 10
    assert aggregate_counts["total_component_collapse_events"] == 10
    assert aggregate_counts["non_total_component_merge_events"] == 0
    assert aggregate_counts["internal_or_redundant_unit_events"] == 23
    assert aggregate_counts["cycle_shield_collapses"] == 385
    assert aggregate_counts["cycle_to_spanning_collapses"] == 385
    assert aggregate_counts["collapsed_sources_with_bridge"] == 0
    assert aggregate_counts["pre_unit_same_cut_pair_occurrences"] == 0
    assert aggregate_counts["post_unit_same_cut_pair_occurrences"] == 0
    assert aggregate_counts["new_same_cut_births"] == 0
    assert aggregate_counts["births_without_collapsed_cycle_source"] == 0
    assert aggregate_counts["opposite_unit_events"] == 4
    assert aggregate_counts["same_cut_pairs_at_opposite_unit_terminal"] == 1
    assert aggregate_bridge_counts == Counter({0: 385})

    print("JANUS_GT_POST_UNIT_CYCLE_SHIELD_COLLAPSE = PASS")
    print(f"ROWS = {tuple(rows)}")
    print(f"AGGREGATE_COUNTS = {tuple(sorted(aggregate_counts.items()))}")
    print(f"AGGREGATE_TRANSITION_SHAPES = {tuple(sorted(aggregate_shapes.items(), key=repr))}")
    print(f"AGGREGATE_COLLAPSE_CLASSES = {tuple(sorted(aggregate_classes.items()))}")
    print(f"AGGREGATE_COLLAPSE_BRIDGE_COUNTS = {tuple(sorted(aggregate_bridge_counts.items()))}")
    print(f"AGGREGATE_COLLAPSE_FALSE_LITERAL = {tuple(sorted(aggregate_false_literal.items()))}")
    print(f"AGGREGATE_COLLAPSE_SOURCE_WIDTHS = {tuple(sorted(aggregate_source_widths.items()))}")
    print(f"AGGREGATE_COLLAPSE_RESIDUAL_WIDTHS = {tuple(sorted(aggregate_residual_widths.items()))}")
    print(f"AGGREGATE_BIRTH_SOURCE_CLASSES = {tuple(sorted(aggregate_birth_classes.items(), key=repr))}")
    print(f"AGGREGATE_OPPOSITE_UNIT_SHAPES = {tuple(sorted(aggregate_opposite_shapes.items()))}")
    print(
        "claim_boundary = exact reachable post-unit total-component-collapse "
        "census through GT_8 before novelty n-2; arbitrary-n barrier open"
    )


if __name__ == "__main__":
    self_test()
