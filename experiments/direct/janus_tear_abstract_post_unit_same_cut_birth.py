#!/usr/bin/env python3
"""Search the smallest quotient for post-assignment same-cut births.

C024 finite GT traces show zero double-bridge pairs created by post-unit
closure.  This script tests whether that fact can follow from a pure quotient-
graph theorem.

On three quotient vertices it exhausts every non-tautological clause pair and
every single comparison assignment.  Both clauses must survive the assignment.
For every complementary pivot it records cases where:

- the residual clauses form a same-cut double-bridge pair after contraction;
- the source clauses did not form a same-cut pair before contraction.

Births are split by source safety classes, residual widths, and whether the
residual pair is the immediate complementary-unit conflict `(p),(-p)`.

The audit is deliberately discovery-oriented.  A generic birth falsifies pure
post-unit noncreation; absence under stronger source classes identifies the
assumptions a GT-specific theorem must preserve.
"""

from __future__ import annotations

from collections import Counter
from itertools import product

from janus_tear_gt_bridge_endpoint_profile import bridge_record
from janus_tear_gt_component_merge_sources import reduce_clause
from janus_tear_gt_component_tree_clause_audit import clause_component_graph
from janus_tear_gt_critical_order_damage import pair_variables
from janus_tear_gt_rank_safety_dichotomy import safety_class

Clause = tuple[int, ...]
SAFE_CLASSES = {"DIRECTED_CYCLE", "COMPONENT_SPANNING", "INTERNAL_ONLY"}


def all_clauses(variable_count: int) -> tuple[Clause, ...]:
    clauses = []
    choices = tuple((-variable, 0, variable) for variable in range(1, variable_count + 1))
    for selection in product(*choices):
        clause = tuple(literal for literal in selection if literal)
        if clause:
            clauses.append(clause)
    return tuple(clauses)


def same_cut_record(
    n: int,
    left: Clause,
    right: Clause,
    pivot: int,
    assignment: dict[int, bool],
    pairs: dict[int, tuple[int, int]],
):
    if pivot not in left or -pivot not in right:
        return None
    left_structure = safety_class(n, left, assignment, pairs)
    right_structure = safety_class(n, right, assignment, pairs)
    if left_structure["classification"] != "COMPONENT_SPANNING":
        return None
    if right_structure["classification"] != "COMPONENT_SPANNING":
        return None
    left_graph = clause_component_graph(n, left, assignment, pairs)
    right_graph = clause_component_graph(n, right, assignment, pairs)
    left_bridge = bridge_record(left, left_graph, pairs, pivot)
    right_bridge = bridge_record(right, right_graph, pairs, -pivot)
    if left_bridge is None or right_bridge is None:
        return None
    if left_bridge["cut"] != right_bridge["cut"]:
        return None
    return {
        "left_bridge": left_bridge,
        "right_bridge": right_bridge,
        "cut": left_bridge["cut"],
    }


def audit(n: int = 3):
    pairs = pair_variables(n)
    clauses = all_clauses(len(pairs))
    empty_assignment: dict[int, bool] = {}

    counts: Counter[str] = Counter()
    source_class_pairs: Counter[tuple[str, str]] = Counter()
    residual_width_pairs: Counter[tuple[int, int]] = Counter()
    residual_role_pairs: Counter[tuple[str, str]] = Counter()
    assignment_histogram: Counter[tuple[int, bool]] = Counter()
    examples = []

    for assigned_variable, assigned_value in product(pairs, (False, True)):
        assignment = {assigned_variable: assigned_value}
        survivors = []
        for source in clauses:
            residual = reduce_clause(source, assignment)
            if residual is None or residual == ():
                continue
            survivors.append((source, tuple(residual)))

        for pivot in pairs:
            if pivot == assigned_variable:
                continue
            positive = [item for item in survivors if pivot in item[1]]
            negative = [item for item in survivors if -pivot in item[1]]

            for (left_source, left_residual), (right_source, right_residual) in product(
                positive, negative
            ):
                post_record = same_cut_record(
                    n,
                    left_residual,
                    right_residual,
                    pivot,
                    assignment,
                    pairs,
                )
                if post_record is None:
                    continue
                pre_record = same_cut_record(
                    n,
                    left_source,
                    right_source,
                    pivot,
                    empty_assignment,
                    pairs,
                )
                if pre_record is not None:
                    continue

                counts["same_cut_births"] += 1
                assignment_histogram[(assigned_variable, assigned_value)] += 1
                left_class = str(
                    safety_class(
                        n, left_source, empty_assignment, pairs
                    )["classification"]
                )
                right_class = str(
                    safety_class(
                        n, right_source, empty_assignment, pairs
                    )["classification"]
                )
                classes = tuple(sorted((left_class, right_class)))
                source_class_pairs[classes] += 1
                both_safe = left_class in SAFE_CLASSES and right_class in SAFE_CLASSES
                counts["both_sources_safe" if both_safe else "has_unsafe_source"] += 1

                widths = tuple(sorted((len(left_residual), len(right_residual))))
                residual_width_pairs[widths] += 1
                roles = tuple(sorted((
                    str(post_record["left_bridge"]["role"]),
                    str(post_record["right_bridge"]["role"]),
                )))
                residual_role_pairs[roles] += 1
                opposite_units = (
                    left_residual == (pivot,)
                    and right_residual == (-pivot,)
                )
                counts[
                    "opposite_unit_conflicts"
                    if opposite_units
                    else "non_unit_same_cut_births"
                ] += 1
                if both_safe and not opposite_units:
                    counts["safe_source_non_unit_births"] += 1

                if len(examples) < 80:
                    examples.append({
                        "n": n,
                        "assignment": (assigned_variable, assigned_value),
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
                        "post_cut": post_record["cut"],
                    })

    return {
        "n": n,
        "clause_count": len(clauses),
        "counts": tuple(sorted(counts.items())),
        "source_class_pairs": tuple(sorted(source_class_pairs.items(), key=repr)),
        "residual_width_pairs": tuple(sorted(residual_width_pairs.items())),
        "residual_role_pairs": tuple(sorted(residual_role_pairs.items(), key=repr)),
        "assignment_histogram": tuple(sorted(assignment_histogram.items())),
        "examples": tuple(examples),
    }


def self_test() -> None:
    data = audit(3)
    counts = Counter(dict(data["counts"]))
    assert data["clause_count"] == 26
    assert counts["same_cut_births"] > 0
    assert (
        counts["opposite_unit_conflicts"]
        + counts["non_unit_same_cut_births"]
        == counts["same_cut_births"]
    )
    assert (
        counts["both_sources_safe"]
        + counts["has_unsafe_source"]
        == counts["same_cut_births"]
    )

    print("JANUS_ABSTRACT_POST_UNIT_SAME_CUT_BIRTH = PASS")
    print(f"ORDER_SIZE = {data['n']}")
    print(f"CLAUSE_COUNT = {data['clause_count']}")
    print(f"COUNTS = {data['counts']}")
    print(f"SOURCE_CLASS_PAIRS = {data['source_class_pairs']}")
    print(f"RESIDUAL_WIDTH_PAIRS = {data['residual_width_pairs']}")
    print(f"RESIDUAL_ROLE_PAIRS = {data['residual_role_pairs']}")
    print(f"ASSIGNMENT_HISTOGRAM = {data['assignment_histogram']}")
    print(f"EXAMPLES = {data['examples']}")
    print(
        "claim_boundary = exhaustive one-assignment quotient search on three "
        "vertices; GT reachability and unit-reason semantics are not imposed"
    )


if __name__ == "__main__":
    self_test()
