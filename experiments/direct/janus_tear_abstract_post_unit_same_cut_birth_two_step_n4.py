#!/usr/bin/env python3
"""Exhaust two sequential comparison contractions on four vertices.

The one-assignment four-vertex census found 6,336 same-cut births, all with at
least one unsafe source.  That search starts from singleton quotient components
and cannot see a directed two-cycle made from distinct original comparisons
between two already compound components.

This gate first applies one comparison assignment, simplifies the complete
abstract clause universe, and classifies the resulting source clauses on the
three-component quotient.  It then applies every consistent comparison joining
two distinct current components and searches for newly born same-cut
double-bridge pairs.

The decisive question is whether a birth can use two branch-safe source clauses
once compound components and parallel original comparisons are present.
"""

from __future__ import annotations

from collections import Counter
from itertools import product

from janus_tear_abstract_post_unit_same_cut_birth import SAFE_CLASSES, all_clauses
from janus_tear_abstract_post_unit_same_cut_birth_n4 import (
    clause_data,
    group_post_bridges,
    is_pre_same_cut,
    residual_sources,
    witness_key,
)
from janus_tear_gt_critical_order_damage import pair_variables
from janus_tear_gt_novel_branch_audit_v2 import comparison_closure, components


def component_index(n, assignment, pairs):
    closure = comparison_closure(n, assignment, pairs)
    if not closure.acyclic:
        return None, None
    parts = components(closure)
    index = {
        vertex: component_id
        for component_id, part in enumerate(parts)
        for vertex in part
    }
    return parts, index


def audit(n: int = 4):
    pairs = pair_variables(n)
    root_clauses = all_clauses(len(pairs))

    counts: Counter[str] = Counter()
    source_class_pairs: Counter[tuple[str, str]] = Counter()
    residual_width_pairs: Counter[tuple[int, int]] = Counter()
    residual_role_pairs: Counter[tuple[str, str]] = Counter()
    pre_component_shapes: Counter[tuple[int, ...]] = Counter()
    post_component_shapes: Counter[tuple[int, ...]] = Counter()
    transition_histogram: Counter[tuple[int, bool, int, bool]] = Counter()
    examples = []
    minimum_witnesses: dict[str, dict[str, object]] = {}

    for first_variable, first_value in product(pairs, (False, True)):
        pre_assignment = {first_variable: first_value}
        pre_parts, pre_index = component_index(n, pre_assignment, pairs)
        assert pre_parts is not None and pre_index is not None
        pre_component_shapes[
            tuple(sorted(len(part) for part in pre_parts))
        ] += 1

        pre_mapping = residual_sources(root_clauses, pre_assignment)
        pre_clauses = tuple(pre_mapping)
        pre_classes, pre_bridges = clause_data(
            n, pre_clauses, pre_assignment, pairs
        )

        for second_variable, second_value in product(pairs, (False, True)):
            if second_variable == first_variable:
                continue
            left_vertex, right_vertex = pairs[second_variable]
            if pre_index[left_vertex] == pre_index[right_vertex]:
                continue

            post_assignment = dict(pre_assignment)
            post_assignment[second_variable] = second_value
            post_parts, _post_index = component_index(
                n, post_assignment, pairs
            )
            if post_parts is None:
                counts["cyclic_second_assignments_skipped"] += 1
                continue

            counts["acyclic_cross_component_transitions"] += 1
            transition_histogram[(
                first_variable,
                first_value,
                second_variable,
                second_value,
            )] += 1
            post_component_shapes[
                tuple(sorted(len(part) for part in post_parts))
            ] += 1

            second_step = {second_variable: second_value}
            mapping = residual_sources(pre_clauses, second_step)
            post_clauses = tuple(mapping)
            _post_classes, post_bridges = clause_data(
                n, post_clauses, post_assignment, pairs
            )
            positive, negative = group_post_bridges(post_bridges)

            counts["post_clause_occurrences"] += len(post_clauses)
            counts["post_bridge_literal_occurrences"] += len(post_bridges)

            for pivot in sorted(set(positive) & set(negative)):
                if pivot in (first_variable, second_variable):
                    continue
                for cut in set(positive[pivot]) & set(negative[pivot]):
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

                        for left_source, right_source in product(
                            mapping[left_residual], mapping[right_residual]
                        ):
                            counts["source_combinations_checked"] += 1
                            if is_pre_same_cut(
                                left_source,
                                right_source,
                                pivot,
                                pre_bridges,
                            ):
                                counts[
                                    "preexisting_same_cut_source_combinations"
                                ] += 1
                                continue

                            counts["same_cut_births"] += 1
                            left_class = pre_classes[left_source]
                            right_class = pre_classes[right_source]
                            classes = tuple(sorted((
                                left_class, right_class
                            )))
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
                                len(left_residual),
                                len(right_residual),
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
                                "pre_assignment": (
                                    first_variable, first_value
                                ),
                                "second_assignment": (
                                    second_variable, second_value
                                ),
                                "pre_parts": pre_parts,
                                "post_parts": post_parts,
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
                            if len(examples) < 120:
                                examples.append(example)

                            labels = ["ALL_BIRTHS"]
                            labels.append(
                                "BOTH_SAFE"
                                if both_safe
                                else "HAS_UNSAFE_SOURCE"
                            )
                            labels.append(
                                "OPPOSITE_UNITS"
                                if opposite_units
                                else "NON_UNIT"
                            )
                            if both_safe and not opposite_units:
                                labels.append("BOTH_SAFE_NON_UNIT")
                            if not both_safe and not opposite_units:
                                labels.append("UNSAFE_SOURCE_NON_UNIT")
                            for label in labels:
                                incumbent = minimum_witnesses.get(label)
                                if (
                                    incumbent is None
                                    or witness_key({
                                        **example,
                                        "assignment": example[
                                            "second_assignment"
                                        ],
                                    })
                                    < witness_key({
                                        **incumbent,
                                        "assignment": incumbent[
                                            "second_assignment"
                                        ],
                                    })
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
        "root_clause_count": len(root_clauses),
        "counts": tuple(sorted(counts.items())),
        "source_class_pairs": tuple(sorted(source_class_pairs.items(), key=repr)),
        "residual_width_pairs": tuple(sorted(residual_width_pairs.items())),
        "residual_role_pairs": tuple(sorted(residual_role_pairs.items(), key=repr)),
        "pre_component_shapes": tuple(sorted(pre_component_shapes.items())),
        "post_component_shapes": tuple(sorted(post_component_shapes.items())),
        "transition_count": sum(transition_histogram.values()),
        "minimum_witnesses": tuple(sorted(minimum_witnesses.items())),
        "examples": tuple(examples),
    }


def self_test() -> None:
    data = audit(4)
    counts = Counter(dict(data["counts"]))
    assert data["root_clause_count"] == 728
    assert counts["acyclic_cross_component_transitions"] > 0
    assert counts["same_cut_births"] > 0

    print("JANUS_ABSTRACT_POST_UNIT_SAME_CUT_BIRTH_TWO_STEP_N4 = PASS")
    print(f"ORDER_SIZE = {data['n']}")
    print(f"VARIABLE_COUNT = {data['variable_count']}")
    print(f"ROOT_CLAUSE_COUNT = {data['root_clause_count']}")
    print(f"COUNTS = {data['counts']}")
    print(f"SOURCE_CLASS_PAIRS = {data['source_class_pairs']}")
    print(f"RESIDUAL_WIDTH_PAIRS = {data['residual_width_pairs']}")
    print(f"RESIDUAL_ROLE_PAIRS = {data['residual_role_pairs']}")
    print(f"PRE_COMPONENT_SHAPES = {data['pre_component_shapes']}")
    print(f"POST_COMPONENT_SHAPES = {data['post_component_shapes']}")
    print(f"TRANSITION_COUNT = {data['transition_count']}")
    print(f"MINIMUM_WITNESSES = {data['minimum_witnesses']}")
    print(f"EXAMPLES = {data['examples']}")
    print(
        "DECISIVE_COUNTS = "
        f"births:{counts['same_cut_births']} "
        f"both_safe:{counts['both_sources_safe']} "
        f"non_unit:{counts['non_unit_same_cut_births']} "
        f"both_safe_non_unit:{counts['both_safe_non_unit_births']} "
        f"unsafe_source_non_unit:{counts['unsafe_source_non_unit_births']}"
    )
    print(
        "claim_boundary = exhaustive two-step acyclic cross-component "
        "contractions on four original vertices; GT reachability absent"
    )


if __name__ == "__main__":
    self_test()
