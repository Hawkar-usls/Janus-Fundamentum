#!/usr/bin/env python3
"""Optimized same-cut birth census on three and four quotient vertices.

The three-vertex exhaustive gate found 36 post-assignment same-cut births.  All
36 use at least one unsafe source clause and all 36 are immediate complementary
unit conflicts.  This file tests whether either pattern fails on four quotient
vertices.

For one assigned comparison, every surviving residual has at most two source
preimages: the residual itself and the residual plus the falsified assigned
literal.  The checker therefore indexes residual bridge cuts first and only
examines source combinations for residual pairs which are already same-cut
double bridges after contraction.

The census records, without assuming an answer:

- births with two branch-safe sources;
- births with at least one unsafe source;
- complementary-unit versus non-unit births;
- the intersections `both-safe + non-unit` and `unsafe-source + non-unit`;
- minimum-width witnesses for every nonempty class.

GT reachability and unit-reason provenance are intentionally absent.  This is a
pure quotient falsification gate for candidate T2a statements.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from itertools import product

from janus_tear_abstract_post_unit_same_cut_birth import (
    SAFE_CLASSES,
    all_clauses,
)
from janus_tear_gt_bridge_endpoint_profile import bridge_record
from janus_tear_gt_component_merge_sources import reduce_clause
from janus_tear_gt_component_tree_clause_audit import clause_component_graph
from janus_tear_gt_critical_order_damage import pair_variables
from janus_tear_gt_rank_safety_dichotomy import safety_class

Clause = tuple[int, ...]
Cut = tuple[tuple[int, ...], tuple[int, ...]]


def clause_data(
    n: int,
    clauses: tuple[Clause, ...],
    assignment: dict[int, bool],
    pairs: dict[int, tuple[int, int]],
):
    classes: dict[Clause, str] = {}
    bridges: dict[tuple[Clause, int], dict[str, object]] = {}

    for clause in clauses:
        structure = safety_class(n, clause, assignment, pairs)
        classification = str(structure["classification"])
        classes[clause] = classification
        if classification != "COMPONENT_SPANNING":
            continue
        graph = clause_component_graph(n, clause, assignment, pairs)
        for literal in clause:
            bridge = bridge_record(clause, graph, pairs, literal)
            if bridge is not None:
                bridges[(clause, literal)] = bridge

    return classes, bridges


def residual_sources(
    clauses: tuple[Clause, ...],
    assignment: dict[int, bool],
) -> dict[Clause, tuple[Clause, ...]]:
    result: dict[Clause, list[Clause]] = defaultdict(list)
    for source in clauses:
        residual = reduce_clause(source, assignment)
        if residual is None or residual == ():
            continue
        result[tuple(residual)].append(source)
    mapping = {
        residual: tuple(sources)
        for residual, sources in result.items()
    }
    assert all(1 <= len(sources) <= 2 for sources in mapping.values())
    return mapping


def group_post_bridges(
    bridges: dict[tuple[Clause, int], dict[str, object]],
):
    positive: dict[int, dict[Cut, list[Clause]]] = defaultdict(
        lambda: defaultdict(list)
    )
    negative: dict[int, dict[Cut, list[Clause]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for (clause, literal), bridge in bridges.items():
        cut = bridge["cut"]
        assert isinstance(cut, tuple)
        target = positive if literal > 0 else negative
        target[abs(literal)][cut].append(clause)
    return positive, negative


def is_pre_same_cut(
    left: Clause,
    right: Clause,
    pivot: int,
    pre_bridges: dict[tuple[Clause, int], dict[str, object]],
) -> bool:
    left_bridge = pre_bridges.get((left, pivot))
    right_bridge = pre_bridges.get((right, -pivot))
    return (
        left_bridge is not None
        and right_bridge is not None
        and left_bridge["cut"] == right_bridge["cut"]
    )


def witness_key(example: dict[str, object]):
    left_source = tuple(example["left_source"])
    right_source = tuple(example["right_source"])
    left_residual = tuple(example["left_residual"])
    right_residual = tuple(example["right_residual"])
    return (
        len(left_source) + len(right_source),
        len(left_residual) + len(right_residual),
        left_source,
        right_source,
        tuple(example["assignment"]),
        int(example["pivot"]),
    )


def audit(n: int):
    pairs = pair_variables(n)
    clauses = all_clauses(len(pairs))
    empty_assignment: dict[int, bool] = {}
    pre_classes, pre_bridges = clause_data(
        n, clauses, empty_assignment, pairs
    )

    counts: Counter[str] = Counter()
    source_class_pairs: Counter[tuple[str, str]] = Counter()
    residual_width_pairs: Counter[tuple[int, int]] = Counter()
    residual_role_pairs: Counter[tuple[str, str]] = Counter()
    source_preimage_sizes: Counter[tuple[int, int]] = Counter()
    assignment_histogram: Counter[tuple[int, bool]] = Counter()
    pivot_histogram: Counter[int] = Counter()
    examples = []
    minimum_witnesses: dict[str, dict[str, object]] = {}

    for assigned_variable, assigned_value in product(pairs, (False, True)):
        assignment = {assigned_variable: assigned_value}
        mapping = residual_sources(clauses, assignment)
        residuals = tuple(mapping)
        _post_classes, post_bridges = clause_data(
            n, residuals, assignment, pairs
        )
        positive, negative = group_post_bridges(post_bridges)

        counts["assignments"] += 1
        counts["residual_clause_occurrences"] += len(residuals)
        counts["post_bridge_literal_occurrences"] += len(post_bridges)

        for pivot in sorted(set(positive) & set(negative)):
            if pivot == assigned_variable:
                continue
            common_cuts = set(positive[pivot]) & set(negative[pivot])
            for cut in common_cuts:
                for left_residual, right_residual in product(
                    positive[pivot][cut], negative[pivot][cut]
                ):
                    counts["post_same_cut_residual_pairs"] += 1
                    left_bridge = post_bridges[(left_residual, pivot)]
                    right_bridge = post_bridges[(right_residual, -pivot)]
                    roles = tuple(sorted((
                        str(left_bridge["role"]),
                        str(right_bridge["role"]),
                    )))
                    residual_role_pairs[roles] += 1

                    left_sources = mapping[left_residual]
                    right_sources = mapping[right_residual]
                    source_preimage_sizes[(
                        len(left_sources), len(right_sources)
                    )] += 1

                    for left_source, right_source in product(
                        left_sources, right_sources
                    ):
                        counts["source_combinations_checked"] += 1
                        if is_pre_same_cut(
                            left_source,
                            right_source,
                            pivot,
                            pre_bridges,
                        ):
                            counts["preexisting_same_cut_source_combinations"] += 1
                            continue

                        counts["same_cut_births"] += 1
                        assignment_histogram[
                            (assigned_variable, assigned_value)
                        ] += 1
                        pivot_histogram[pivot] += 1

                        left_class = pre_classes[left_source]
                        right_class = pre_classes[right_source]
                        classes = tuple(sorted((left_class, right_class)))
                        source_class_pairs[classes] += 1
                        both_safe = (
                            left_class in SAFE_CLASSES
                            and right_class in SAFE_CLASSES
                        )
                        if both_safe:
                            counts["both_sources_safe"] += 1
                        else:
                            counts["has_unsafe_source"] += 1

                        widths = tuple(sorted((
                            len(left_residual), len(right_residual)
                        )))
                        residual_width_pairs[widths] += 1
                        opposite_units = (
                            left_residual == (pivot,)
                            and right_residual == (-pivot,)
                        )
                        if opposite_units:
                            counts["opposite_unit_conflicts"] += 1
                        else:
                            counts["non_unit_same_cut_births"] += 1
                        if both_safe and opposite_units:
                            counts["both_safe_unit_births"] += 1
                        if both_safe and not opposite_units:
                            counts["both_safe_non_unit_births"] += 1
                        if not both_safe and not opposite_units:
                            counts["unsafe_source_non_unit_births"] += 1

                        example = {
                            "n": n,
                            "assignment": (
                                assigned_variable, assigned_value
                            ),
                            "assignment_endpoints": pairs[assigned_variable],
                            "pivot": pivot,
                            "pivot_endpoints": pairs[pivot],
                            "left_source": left_source,
                            "right_source": right_source,
                            "left_residual": left_residual,
                            "right_residual": right_residual,
                            "source_classes": classes,
                            "both_sources_safe": both_safe,
                            "opposite_units": opposite_units,
                            "post_roles": roles,
                            "post_cut": cut,
                        }
                        if len(examples) < 100:
                            examples.append(example)

                        labels = ["ALL_BIRTHS"]
                        labels.append(
                            "BOTH_SAFE" if both_safe else "HAS_UNSAFE_SOURCE"
                        )
                        labels.append(
                            "OPPOSITE_UNITS" if opposite_units else "NON_UNIT"
                        )
                        if both_safe and not opposite_units:
                            labels.append("BOTH_SAFE_NON_UNIT")
                        if not both_safe and not opposite_units:
                            labels.append("UNSAFE_SOURCE_NON_UNIT")
                        for label in labels:
                            incumbent = minimum_witnesses.get(label)
                            if incumbent is None or witness_key(example) < witness_key(
                                incumbent
                            ):
                                minimum_witnesses[label] = example

    assert (
        counts["both_sources_safe"] + counts["has_unsafe_source"]
        == counts["same_cut_births"]
    )
    assert (
        counts["opposite_unit_conflicts"]
        + counts["non_unit_same_cut_births"]
        == counts["same_cut_births"]
    )

    return {
        "n": n,
        "variable_count": len(pairs),
        "clause_count": len(clauses),
        "counts": tuple(sorted(counts.items())),
        "source_class_pairs": tuple(sorted(source_class_pairs.items(), key=repr)),
        "residual_width_pairs": tuple(sorted(residual_width_pairs.items())),
        "residual_role_pairs": tuple(sorted(residual_role_pairs.items(), key=repr)),
        "source_preimage_sizes": tuple(sorted(source_preimage_sizes.items())),
        "assignment_histogram": tuple(sorted(assignment_histogram.items())),
        "pivot_histogram": tuple(sorted(pivot_histogram.items())),
        "minimum_witnesses": tuple(sorted(minimum_witnesses.items())),
        "examples": tuple(examples),
    }


def print_data(data) -> None:
    print(f"ORDER_SIZE = {data['n']}")
    print(f"VARIABLE_COUNT = {data['variable_count']}")
    print(f"CLAUSE_COUNT = {data['clause_count']}")
    print(f"COUNTS = {data['counts']}")
    print(f"SOURCE_CLASS_PAIRS = {data['source_class_pairs']}")
    print(f"RESIDUAL_WIDTH_PAIRS = {data['residual_width_pairs']}")
    print(f"RESIDUAL_ROLE_PAIRS = {data['residual_role_pairs']}")
    print(f"SOURCE_PREIMAGE_SIZES = {data['source_preimage_sizes']}")
    print(f"ASSIGNMENT_HISTOGRAM = {data['assignment_histogram']}")
    print(f"PIVOT_HISTOGRAM = {data['pivot_histogram']}")
    print(f"MINIMUM_WITNESSES = {data['minimum_witnesses']}")
    print(f"EXAMPLES = {data['examples']}")


def self_test() -> None:
    n3 = audit(3)
    print_data(n3)
    n3_counts = Counter(dict(n3["counts"]))
    assert n3["clause_count"] == 26
    assert n3_counts["same_cut_births"] == 36
    assert n3_counts["opposite_unit_conflicts"] == 36
    assert n3_counts["non_unit_same_cut_births"] == 0
    assert n3_counts["both_sources_safe"] == 0

    n4 = audit(4)
    print_data(n4)
    n4_counts = Counter(dict(n4["counts"]))
    assert n4["clause_count"] == 728
    assert n4_counts["same_cut_births"] > 0

    print("JANUS_ABSTRACT_POST_UNIT_SAME_CUT_BIRTH_N4 = PASS")
    print(
        "N4_DECISIVE_COUNTS = "
        f"births:{n4_counts['same_cut_births']} "
        f"both_safe:{n4_counts['both_sources_safe']} "
        f"non_unit:{n4_counts['non_unit_same_cut_births']} "
        f"both_safe_non_unit:{n4_counts['both_safe_non_unit_births']} "
        f"unsafe_source_non_unit:{n4_counts['unsafe_source_non_unit_births']}"
    )
    print(
        "claim_boundary = exhaustive one-assignment quotient search through "
        "four vertices; GT reachability and unit-reason semantics are absent"
    )


if __name__ == "__main__":
    self_test()
