#!/usr/bin/env python3
"""Test every possible root branch variable on every unshielded occurrence.

The deterministic root route is safe through GT_12.  This audit asks whether
that safety actually depends on the Policy-0A maximum-frequency selector.

For each immediate-local root post-result clause containing a component-
spanning non-tail bridge with singleton tail and head, every variable occurring
in the post-CNF is assigned in both polarities.  Full child unit closure is
replayed, and the tracked occurrence is classified as terminal/extinct,
non-bridge, tail-singleton safe, canonically root-shielded, or unsafe.

This is a hypothetical all-variable branch audit.  Nonselected choices are not
claimed to be reachable under Policy-0A; they test whether a selector theorem is
needed at all.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_bad_bridge_birth_lifecycle import endpoint_sizes
from janus_tear_gt_bridge_endpoint_profile import bridge_record
from janus_tear_gt_component_merge_sources import reduce_clause
from janus_tear_gt_component_tree_clause_audit import clause_component_graph
from janus_tear_gt_global_clause_shrink_census import unit_assignments
from janus_tear_gt_rank_safety_dichotomy import safety_class
from janus_tear_gt_root_unshielded_handoff_probe import (
    canonical_root_shield,
    root_stages,
)
from janus_tear_gt_same_cut_parent_ancestry import root_minimum_labels
from janus_tear_policy0t_trace_certificate import simplify_one, unit_trace


def classify_child(
    n,
    root_by_vertex,
    post,
    parent_assignment,
    pairs,
    clause,
    literal,
    variable,
    value,
):
    child = simplify_one(post, variable, value)
    if child is None:
        return "DIRECT_CONFLICT", None, None
    child_key, contradiction, events = unit_trace(child)
    if contradiction:
        return "PRE_UNIT_CONTRADICTION", None, None
    assert child_key is not None
    if not child_key:
        return "SAT_EMPTY_TERMINAL", None, None

    child_assignment = dict(parent_assignment)
    child_assignment[variable] = value
    child_assignment.update(unit_assignments(events))
    residual = reduce_clause(clause, child_assignment)
    if residual is None or literal not in residual:
        return "CLAUSE_EXTINCT", residual, None
    if residual not in child_key:
        return "NOT_IN_CHILD_KEY", residual, None

    classification = str(
        safety_class(n, residual, child_assignment, pairs)["classification"]
    )
    if classification != "COMPONENT_SPANNING":
        return classification, residual, None

    graph = clause_component_graph(n, residual, child_assignment, pairs)
    record = bridge_record(residual, graph, pairs, literal)
    if record is None:
        return "SPANNING_NONBRIDGE", residual, None
    if record["role"] == "TAIL_SINGLETON":
        return "TAIL_SINGLETON_SAFE", residual, None

    shield = canonical_root_shield(
        n,
        root_by_vertex,
        child_key,
        child_assignment,
        pairs,
        residual,
        literal,
    )
    if shield is not None:
        return "CANONICALLY_SHIELDED", residual, shield
    return "UNSAFE_UNSHIELDED_SURVIVES", residual, None


def audit(n: int):
    data = root_stages(n)
    root = tuple(data["root"])
    pairs = data["pairs"]
    post = tuple(data["post"])
    assignment = dict(data["post_assignment"])
    selected = int(data["selected"])
    minimum_labels = root_minimum_labels(n, pairs)
    root_by_vertex = {
        vertex: clause
        for clause, vertex in minimum_labels.items()
    }
    local_resolvents = {
        tuple(event["resolvent"])
        for event in data["events"]
    }
    variables = tuple(sorted({abs(literal) for clause in post for literal in clause}))

    counts: Counter[str] = Counter()
    selected_fates: Counter[str] = Counter()
    nonselected_fates: Counter[str] = Counter()
    unsafe_variables: Counter[int] = Counter()
    unsafe_selected: Counter[bool] = Counter()
    per_occurrence_unsafe: Counter[int] = Counter()
    examples = []

    occurrence_id = 0
    for clause in post:
        if not any(
            reduce_clause(antecedent, assignment) == clause
            for antecedent in local_resolvents
        ):
            continue
        if str(safety_class(n, clause, assignment, pairs)["classification"]) != "COMPONENT_SPANNING":
            continue
        graph = clause_component_graph(n, clause, assignment, pairs)

        for literal in clause:
            literal = int(literal)
            record = bridge_record(clause, graph, pairs, literal)
            if record is None or record["role"] == "TAIL_SINGLETON":
                continue
            sizes = endpoint_sizes(graph, literal, pairs)
            if int(sizes["tail_size"]) != 1 or int(sizes["head_size"]) != 1:
                continue

            counts["occurrences"] += 1
            occurrence_unsafe = 0
            for variable in variables:
                for value in (False, True):
                    counts["branch_polarity_trials"] += 1
                    fate, residual, shield = classify_child(
                        n,
                        root_by_vertex,
                        post,
                        assignment,
                        pairs,
                        clause,
                        literal,
                        variable,
                        value,
                    )
                    if variable == selected:
                        selected_fates[fate] += 1
                    else:
                        nonselected_fates[fate] += 1

                    if fate == "UNSAFE_UNSHIELDED_SURVIVES":
                        counts["unsafe_trials"] += 1
                        occurrence_unsafe += 1
                        unsafe_variables[variable] += 1
                        unsafe_selected[variable == selected] += 1
                        if len(examples) < 80:
                            examples.append(
                                {
                                    "n": n,
                                    "occurrence_id": occurrence_id,
                                    "selected": selected,
                                    "trial_variable": variable,
                                    "trial_value": value,
                                    "clause": clause,
                                    "literal": literal,
                                    "bad_bridge": record,
                                    "residual": residual,
                                    "shield": shield,
                                }
                            )
            per_occurrence_unsafe[occurrence_unsafe] += 1
            occurrence_id += 1

    assert counts["occurrences"] > 0
    assert selected_fates["UNSAFE_UNSHIELDED_SURVIVES"] == 0
    return {
        "n": n,
        "selected": selected,
        "variables": len(variables),
        "counts": tuple(sorted(counts.items())),
        "selected_fates": tuple(sorted(selected_fates.items())),
        "nonselected_fates": tuple(sorted(nonselected_fates.items())),
        "unsafe_variables": tuple(sorted(unsafe_variables.items())),
        "unsafe_selected": tuple(sorted(unsafe_selected.items())),
        "per_occurrence_unsafe": tuple(sorted(per_occurrence_unsafe.items())),
        "examples": tuple(examples),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_selected: Counter[str] = Counter()
    aggregate_nonselected: Counter[str] = Counter()
    aggregate_unsafe_variables: Counter[int] = Counter()
    aggregate_unsafe_selected: Counter[bool] = Counter()
    aggregate_occurrence_unsafe: Counter[int] = Counter()

    for n in range(4, 13):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_selected.update(dict(data["selected_fates"]))
        aggregate_nonselected.update(dict(data["nonselected_fates"]))
        aggregate_unsafe_variables.update(dict(data["unsafe_variables"]))
        aggregate_unsafe_selected.update(dict(data["unsafe_selected"]))
        aggregate_occurrence_unsafe.update(dict(data["per_occurrence_unsafe"]))
        print(f"ORDER_SIZE = {n}")
        print(f"  selected = {data['selected']}")
        print(f"  variables = {data['variables']}")
        print(f"  counts = {data['counts']}")
        print(f"  selected_fates = {data['selected_fates']}")
        print(f"  nonselected_fates = {data['nonselected_fates']}")
        print(f"  unsafe_variables = {data['unsafe_variables']}")
        print(f"  per_occurrence_unsafe = {data['per_occurrence_unsafe']}")
        print(f"  unsafe_examples = {data['examples']}")

    print("JANUS_GT_ROOT_ALL_VARIABLE_HANDOFF = PASS")
    print(f"AGGREGATE_COUNTS = {tuple(sorted(aggregate_counts.items()))}")
    print(f"AGGREGATE_SELECTED_FATES = {tuple(sorted(aggregate_selected.items()))}")
    print(f"AGGREGATE_NONSELECTED_FATES = {tuple(sorted(aggregate_nonselected.items()))}")
    print(
        "AGGREGATE_UNSAFE_VARIABLES = "
        f"{tuple(sorted(aggregate_unsafe_variables.items()))}"
    )
    print(
        "AGGREGATE_UNSAFE_SELECTED = "
        f"{tuple(sorted(aggregate_unsafe_selected.items()))}"
    )
    print(
        "AGGREGATE_PER_OCCURRENCE_UNSAFE = "
        f"{tuple(sorted(aggregate_occurrence_unsafe.items()))}"
    )
    print(
        "claim_boundary = exact hypothetical all-variable root handoff audit "
        "through GT_12; nonselected branches are not Policy-0A executions"
    )


if __name__ == "__main__":
    self_test()
