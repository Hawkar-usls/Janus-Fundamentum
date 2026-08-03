#!/usr/bin/env python3
"""Measure the lexicographic margin between the selected root variable and all unsafe alternatives.

For each immediate-local root unshielded clause/literal occurrence through
GT_12, every post-CNF variable is tested in both polarities using the exact
child unit replay from janus_tear_gt_root_all_variable_handoff.  A variable is
unsafe for the occurrence if at least one polarity leaves the tracked lineage
as an admitted unshielded non-tail bridge.

The audit then compares the exact Policy-0A selected score

    (-frequency(variable), variable_index)

with every unsafe score.  It separates strict frequency exclusion from genuine
minimum-index tie exclusion and records whether unsafe variables ever attain
the global maximum frequency.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_bad_bridge_birth_lifecycle import endpoint_sizes
from janus_tear_gt_bridge_endpoint_profile import bridge_record
from janus_tear_gt_component_merge_sources import reduce_clause
from janus_tear_gt_component_tree_clause_audit import clause_component_graph
from janus_tear_gt_rank_safety_dichotomy import safety_class
from janus_tear_gt_root_all_variable_handoff import classify_child
from janus_tear_gt_root_route_template_profile import selected_geometry
from janus_tear_gt_root_unshielded_handoff_probe import root_stages
from janus_tear_gt_same_cut_parent_ancestry import root_minimum_labels


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
    frequencies = Counter(
        abs(literal)
        for clause in post
        for literal in clause
    )
    maximum_frequency = max(frequencies.values())
    maximum_variables = tuple(sorted(
        variable
        for variable, frequency in frequencies.items()
        if frequency == maximum_frequency
    ))
    assert selected == maximum_variables[0]

    counts: Counter[str] = Counter()
    unsafe_count_histogram: Counter[int] = Counter()
    unsafe_max_frequency_gap: Counter[int] = Counter()
    unsafe_max_index_gap: Counter[int] = Counter()
    unsafe_maximum_count: Counter[int] = Counter()
    selected_geometry_histogram: Counter[str] = Counter()
    unsafe_geometry_histogram: Counter[str] = Counter()
    unsafe_occurrence_histogram: Counter[str] = Counter()
    exclusion_modes: Counter[str] = Counter()
    rows = []

    variables = tuple(sorted(frequencies))
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
            bad_bridge = bridge_record(clause, graph, pairs, literal)
            if bad_bridge is None or bad_bridge["role"] == "TAIL_SINGLETON":
                continue
            sizes = endpoint_sizes(graph, literal, pairs)
            if int(sizes["tail_size"]) != 1 or int(sizes["head_size"]) != 1:
                continue

            counts["occurrences"] += 1
            selected_template = selected_geometry(
                graph, bad_bridge, sizes, selected, pairs
            )
            selected_geometry_histogram[selected_template] += 1

            unsafe_variables = []
            unsafe_details = []
            for variable in variables:
                fates = []
                for value in (False, True):
                    fate, _residual, _shield = classify_child(
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
                    fates.append(fate)
                is_unsafe = "UNSAFE_UNSHIELDED_SURVIVES" in fates
                if not is_unsafe:
                    continue

                unsafe_variables.append(variable)
                geometry = selected_geometry(
                    graph, bad_bridge, sizes, variable, pairs
                )
                unsafe_geometry_histogram[geometry] += 1
                variable_literals = tuple(
                    candidate
                    for candidate in clause
                    if abs(candidate) == variable
                )
                if not variable_literals:
                    occurrence_class = "ABSENT"
                elif variable_literals[0] > 0:
                    occurrence_class = "PRESENT_POS"
                else:
                    occurrence_class = "PRESENT_NEG"
                unsafe_occurrence_histogram[occurrence_class] += 1
                unsafe_details.append(
                    {
                        "variable": variable,
                        "frequency": frequencies[variable],
                        "geometry": geometry,
                        "occurrence": occurrence_class,
                        "fates": tuple(fates),
                    }
                )

            assert selected not in unsafe_variables
            unsafe_count_histogram[len(unsafe_variables)] += 1
            if not unsafe_variables:
                counts["occurrences_without_unsafe_variables"] += 1
                rows.append(
                    {
                        "n": n,
                        "clause": clause,
                        "literal": literal,
                        "selected": selected,
                        "selected_frequency": frequencies[selected],
                        "selected_geometry": selected_template,
                        "unsafe_variables": (),
                        "exclusion_mode": "VACUOUS",
                    }
                )
                continue

            counts["occurrences_with_unsafe_variables"] += 1
            unsafe_max_frequency = max(
                frequencies[variable] for variable in unsafe_variables
            )
            unsafe_max_variables = tuple(sorted(
                variable
                for variable in unsafe_variables
                if frequencies[variable] == unsafe_max_frequency
            ))
            frequency_gap = frequencies[selected] - unsafe_max_frequency
            assert frequency_gap >= 0
            unsafe_max_frequency_gap[frequency_gap] += 1
            unsafe_maximum_count[len(unsafe_max_variables)] += 1

            unsafe_at_global_maximum = tuple(
                variable
                for variable in unsafe_max_variables
                if frequencies[variable] == maximum_frequency
            )
            if frequency_gap > 0:
                mode = "STRICT_FREQUENCY"
                counts["unsafe_excluded_by_strict_frequency"] += 1
            else:
                assert unsafe_at_global_maximum
                assert selected < min(unsafe_at_global_maximum)
                mode = "MIN_INDEX_TIE_BREAK"
                counts["unsafe_excluded_by_min_index"] += 1
                index_gap = min(unsafe_at_global_maximum) - selected
                unsafe_max_index_gap[index_gap] += 1
            exclusion_modes[mode] += 1

            selected_score = (-frequencies[selected], selected)
            for variable in unsafe_variables:
                unsafe_score = (-frequencies[variable], variable)
                assert selected_score < unsafe_score
                counts["unsafe_score_comparisons"] += 1

            rows.append(
                {
                    "n": n,
                    "clause": clause,
                    "literal": literal,
                    "selected": selected,
                    "selected_frequency": frequencies[selected],
                    "selected_geometry": selected_template,
                    "maximum_variables": maximum_variables,
                    "unsafe_variables": tuple(unsafe_variables),
                    "unsafe_max_frequency": unsafe_max_frequency,
                    "unsafe_max_variables": unsafe_max_variables,
                    "frequency_gap": frequency_gap,
                    "exclusion_mode": mode,
                    "unsafe_details": tuple(unsafe_details),
                }
            )

    return {
        "n": n,
        "selected": selected,
        "selected_frequency": frequencies[selected],
        "maximum_variables": maximum_variables,
        "counts": tuple(sorted(counts.items())),
        "unsafe_count_histogram": tuple(sorted(unsafe_count_histogram.items())),
        "unsafe_max_frequency_gap": tuple(sorted(unsafe_max_frequency_gap.items())),
        "unsafe_max_index_gap": tuple(sorted(unsafe_max_index_gap.items())),
        "unsafe_maximum_count": tuple(sorted(unsafe_maximum_count.items())),
        "selected_geometry": tuple(sorted(selected_geometry_histogram.items())),
        "unsafe_geometry": tuple(sorted(unsafe_geometry_histogram.items())),
        "unsafe_occurrence": tuple(sorted(unsafe_occurrence_histogram.items())),
        "exclusion_modes": tuple(sorted(exclusion_modes.items())),
        "rows": tuple(rows),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_unsafe_counts: Counter[int] = Counter()
    aggregate_frequency_gaps: Counter[int] = Counter()
    aggregate_index_gaps: Counter[int] = Counter()
    aggregate_unsafe_maximum_counts: Counter[int] = Counter()
    aggregate_selected_geometry: Counter[str] = Counter()
    aggregate_unsafe_geometry: Counter[str] = Counter()
    aggregate_unsafe_occurrence: Counter[str] = Counter()
    aggregate_modes: Counter[str] = Counter()

    for n in range(4, 13):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_unsafe_counts.update(dict(data["unsafe_count_histogram"]))
        aggregate_frequency_gaps.update(dict(data["unsafe_max_frequency_gap"]))
        aggregate_index_gaps.update(dict(data["unsafe_max_index_gap"]))
        aggregate_unsafe_maximum_counts.update(dict(data["unsafe_maximum_count"]))
        aggregate_selected_geometry.update(dict(data["selected_geometry"]))
        aggregate_unsafe_geometry.update(dict(data["unsafe_geometry"]))
        aggregate_unsafe_occurrence.update(dict(data["unsafe_occurrence"]))
        aggregate_modes.update(dict(data["exclusion_modes"]))
        tie_rows = tuple(
            row
            for row in data["rows"]
            if row["exclusion_mode"] == "MIN_INDEX_TIE_BREAK"
        )
        print(f"ORDER_SIZE = {n}")
        print(f"  selected = {data['selected']} / frequency {data['selected_frequency']}")
        print(f"  maximum_variables = {data['maximum_variables']}")
        print(f"  counts = {data['counts']}")
        print(f"  unsafe_count_histogram = {data['unsafe_count_histogram']}")
        print(f"  unsafe_max_frequency_gap = {data['unsafe_max_frequency_gap']}")
        print(f"  unsafe_max_index_gap = {data['unsafe_max_index_gap']}")
        print(f"  exclusion_modes = {data['exclusion_modes']}")
        print(f"  unsafe_geometry = {data['unsafe_geometry']}")
        print(f"  unsafe_occurrence = {data['unsafe_occurrence']}")
        print(f"  tie_rows = {tie_rows}")

    assert aggregate_counts["occurrences"] == 62
    assert aggregate_counts["occurrences_with_unsafe_variables"] == 62
    assert aggregate_counts["occurrences_without_unsafe_variables"] == 0
    assert aggregate_counts["unsafe_score_comparisons"] > 0
    assert sum(aggregate_modes.values()) == 62

    print("JANUS_GT_ROOT_UNSAFE_SELECTOR_MARGIN = PASS")
    print(f"AGGREGATE_COUNTS = {tuple(sorted(aggregate_counts.items()))}")
    print(f"AGGREGATE_UNSAFE_COUNTS = {tuple(sorted(aggregate_unsafe_counts.items()))}")
    print(f"AGGREGATE_FREQUENCY_GAPS = {tuple(sorted(aggregate_frequency_gaps.items()))}")
    print(f"AGGREGATE_INDEX_GAPS = {tuple(sorted(aggregate_index_gaps.items()))}")
    print(
        "AGGREGATE_UNSAFE_MAXIMUM_COUNTS = "
        f"{tuple(sorted(aggregate_unsafe_maximum_counts.items()))}"
    )
    print(
        "AGGREGATE_SELECTED_GEOMETRY = "
        f"{tuple(sorted(aggregate_selected_geometry.items()))}"
    )
    print(
        "AGGREGATE_UNSAFE_GEOMETRY = "
        f"{tuple(sorted(aggregate_unsafe_geometry.items()))}"
    )
    print(
        "AGGREGATE_UNSAFE_OCCURRENCE = "
        f"{tuple(sorted(aggregate_unsafe_occurrence.items()))}"
    )
    print(f"AGGREGATE_EXCLUSION_MODES = {tuple(sorted(aggregate_modes.items()))}")
    print(
        "claim_boundary = exact unsafe-set lexicographic selector margins "
        "through GT_12; arbitrary-n selected-template reachability remains open"
    )


if __name__ == "__main__":
    self_test()
