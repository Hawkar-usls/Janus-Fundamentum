#!/usr/bin/env python3
"""Characterize root unsafe variables geometrically and extend the structural gap.

For GT_4..GT_12, exact two-polarity replay defines the unsafe variable set U
for every root unshielded occurrence.  This audit compares U with:

A = variables whose edge is INTERNAL_HEAD relative to the bad bridge cut and
    whose literal is absent from the tracked clause;
B = A variables whose edge is also disjoint from the bad head endpoint
    component.

If U=B, unsafe semantics has a purely geometric description on the certified
frontier.  The cheaper structural class B is then evaluated through GT_18
without hypothetical child replay, measuring whether the exact selected
variable retains a strict frequency gap over every B-candidate.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_bad_bridge_birth_lifecycle import endpoint_sizes
from janus_tear_gt_bridge_endpoint_profile import bridge_record
from janus_tear_gt_component_merge_sources import reduce_clause
from janus_tear_gt_component_tree_clause_audit import clause_component_graph
from janus_tear_gt_rank_safety_dichotomy import safety_class
from janus_tear_gt_root_route_template_profile import selected_geometry
from janus_tear_gt_root_unsafe_selector_margin import audit as margin_audit
from janus_tear_gt_root_unshielded_handoff_probe import root_stages


def component_map(graph):
    mapping = {}
    for component_index, part in enumerate(graph["parts"]):
        for vertex in part:
            mapping[int(vertex)] = int(component_index)
    return mapping


def local_root_occurrences(n: int):
    stages = root_stages(n)
    root = tuple(stages["root"])
    post = tuple(stages["post"])
    pairs = stages["pairs"]
    assignment = dict(stages["post_assignment"])
    selected = int(stages["selected"])
    local_resolvents = {
        tuple(event["resolvent"])
        for event in stages["events"]
    }
    frequencies = Counter(
        abs(literal)
        for clause in post
        for literal in clause
    )
    variables = tuple(sorted(frequencies))

    occurrences = []
    for clause in post:
        if not any(
            reduce_clause(antecedent, assignment) == clause
            for antecedent in local_resolvents
        ):
            continue
        if str(safety_class(n, clause, assignment, pairs)["classification"]) != "COMPONENT_SPANNING":
            continue
        graph = clause_component_graph(n, clause, assignment, pairs)
        mapping = component_map(graph)

        for literal in clause:
            literal = int(literal)
            bad_bridge = bridge_record(clause, graph, pairs, literal)
            if bad_bridge is None or bad_bridge["role"] == "TAIL_SINGLETON":
                continue
            sizes = endpoint_sizes(graph, literal, pairs)
            if int(sizes["tail_size"]) != 1 or int(sizes["head_size"]) != 1:
                continue

            head_component = int(sizes["head_component"])
            clause_variables = {abs(candidate) for candidate in clause}
            class_a = []
            class_b = []
            for variable in variables:
                geometry = selected_geometry(
                    graph, bad_bridge, sizes, variable, pairs
                )
                if geometry != "INTERNAL_HEAD" or variable in clause_variables:
                    continue
                class_a.append(variable)
                low, high = pairs[variable]
                endpoint_components = {
                    mapping[int(low)],
                    mapping[int(high)],
                }
                if head_component not in endpoint_components:
                    class_b.append(variable)

            occurrences.append(
                {
                    "clause": clause,
                    "literal": literal,
                    "selected": selected,
                    "selected_frequency": frequencies[selected],
                    "selected_geometry": selected_geometry(
                        graph, bad_bridge, sizes, selected, pairs
                    ),
                    "head_component": head_component,
                    "class_a": tuple(class_a),
                    "class_b": tuple(class_b),
                    "class_a_frequencies": tuple(
                        frequencies[variable] for variable in class_a
                    ),
                    "class_b_frequencies": tuple(
                        frequencies[variable] for variable in class_b
                    ),
                }
            )

    return stages, frequencies, tuple(occurrences)


def audit(n: int, replay_unsafe: bool):
    stages, frequencies, occurrences = local_root_occurrences(n)
    selected = int(stages["selected"])

    counts: Counter[str] = Counter()
    class_a_sizes: Counter[int] = Counter()
    class_b_sizes: Counter[int] = Counter()
    class_b_gap_histogram: Counter[int] = Counter()
    class_a_minus_b: Counter[int] = Counter()
    equality_profiles: Counter[str] = Counter()
    rows = []

    unsafe_by_occurrence = None
    if replay_unsafe:
        margin = margin_audit(n)
        unsafe_by_occurrence = {
            (tuple(row["clause"]), int(row["literal"])): tuple(
                int(variable) for variable in row["unsafe_variables"]
            )
            for row in margin["rows"]
        }
        assert len(unsafe_by_occurrence) == len(occurrences)

    for item in occurrences:
        counts["occurrences"] += 1
        class_a = tuple(item["class_a"])
        class_b = tuple(item["class_b"])
        class_a_sizes[len(class_a)] += 1
        class_b_sizes[len(class_b)] += 1
        class_a_minus_b[len(class_a) - len(class_b)] += 1

        if class_b:
            maximum_b_frequency = max(
                frequencies[variable] for variable in class_b
            )
            gap = frequencies[selected] - maximum_b_frequency
            class_b_gap_histogram[gap] += 1
            if gap > 0:
                counts["class_b_strictly_below_selected"] += 1
            elif gap == 0:
                counts["class_b_ties_selected"] += 1
            else:
                counts["class_b_exceeds_selected"] += 1
        else:
            maximum_b_frequency = None
            gap = None
            counts["empty_class_b"] += 1

        unsafe = None
        if unsafe_by_occurrence is not None:
            unsafe = unsafe_by_occurrence[(
                tuple(item["clause"]),
                int(item["literal"]),
            )]
            if unsafe == class_b:
                equality = "U_EQUALS_B"
                counts["unsafe_equals_class_b"] += 1
            elif set(unsafe).issubset(set(class_b)):
                equality = "U_STRICT_SUBSET_B"
                counts["unsafe_strict_subset_class_b"] += 1
            elif set(class_b).issubset(set(unsafe)):
                equality = "B_STRICT_SUBSET_U"
                counts["class_b_strict_subset_unsafe"] += 1
            else:
                equality = "INCOMPARABLE"
                counts["unsafe_incomparable_class_b"] += 1
            equality_profiles[equality] += 1

        rows.append(
            {
                "n": n,
                "clause": tuple(item["clause"]),
                "literal": int(item["literal"]),
                "selected": selected,
                "selected_frequency": frequencies[selected],
                "selected_geometry": item["selected_geometry"],
                "class_a": class_a,
                "class_b": class_b,
                "unsafe": unsafe,
                "maximum_class_b_frequency": maximum_b_frequency,
                "class_b_gap": gap,
            }
        )

    return {
        "n": n,
        "selected": selected,
        "selected_frequency": frequencies[selected],
        "root_baseline": 2 * (n - 1),
        "resolution_attempts": int(stages["attempts"]),
        "resolution_additions": int(stages["additions"]),
        "counts": tuple(sorted(counts.items())),
        "class_a_sizes": tuple(sorted(class_a_sizes.items())),
        "class_b_sizes": tuple(sorted(class_b_sizes.items())),
        "class_a_minus_b": tuple(sorted(class_a_minus_b.items())),
        "class_b_gap_histogram": tuple(sorted(class_b_gap_histogram.items())),
        "equality_profiles": tuple(sorted(equality_profiles.items())),
        "rows": tuple(rows),
    }


def self_test() -> None:
    certified_counts: Counter[str] = Counter()
    certified_equalities: Counter[str] = Counter()
    extended_counts: Counter[str] = Counter()
    extended_gaps: Counter[int] = Counter()
    per_order = []

    for n in range(4, 19):
        replay = n <= 12
        data = audit(n, replay)
        if replay:
            certified_counts.update(dict(data["counts"]))
            certified_equalities.update(dict(data["equality_profiles"]))
        extended_counts.update(dict(data["counts"]))
        extended_gaps.update(dict(data["class_b_gap_histogram"]))
        per_order.append(
            (
                n,
                data["selected"],
                data["selected_frequency"],
                data["counts"],
                data["class_b_sizes"],
                data["class_b_gap_histogram"],
            )
        )
        print(f"ORDER_SIZE = {n}")
        print(f"  replay_unsafe = {replay}")
        print(f"  selected = {data['selected']} / frequency {data['selected_frequency']}")
        print(f"  root_baseline = {data['root_baseline']}")
        print(f"  resolution_attempts = {data['resolution_attempts']}")
        print(f"  resolution_additions = {data['resolution_additions']}")
        print(f"  counts = {data['counts']}")
        print(f"  class_a_sizes = {data['class_a_sizes']}")
        print(f"  class_b_sizes = {data['class_b_sizes']}")
        print(f"  class_a_minus_b = {data['class_a_minus_b']}")
        print(f"  class_b_gap_histogram = {data['class_b_gap_histogram']}")
        print(f"  equality_profiles = {data['equality_profiles']}")
        print(f"  obstruction_rows = {tuple(row for row in data['rows'] if row['class_b_gap'] is not None and row['class_b_gap'] <= 0)}")

    assert certified_counts["occurrences"] == 62
    assert certified_counts["unsafe_equals_class_b"] == 62
    assert certified_equalities == Counter({"U_EQUALS_B": 62})
    assert extended_counts["class_b_exceeds_selected"] == 0
    assert extended_counts["class_b_ties_selected"] == 0

    print("JANUS_GT_ROOT_UNSAFE_STRUCTURAL_CHARACTERIZATION = PASS")
    print(f"PER_ORDER = {tuple(per_order)}")
    print(f"CERTIFIED_COUNTS = {tuple(sorted(certified_counts.items()))}")
    print(f"CERTIFIED_EQUALITIES = {tuple(sorted(certified_equalities.items()))}")
    print(f"EXTENDED_COUNTS = {tuple(sorted(extended_counts.items()))}")
    print(f"EXTENDED_GAPS = {tuple(sorted(extended_gaps.items()))}")
    print(
        "finite_result = through GT_12 the exact unsafe set equals absent "
        "INTERNAL_HEAD comparisons disjoint from the bad head endpoint; the "
        "same structural class remains strictly below the selected frequency "
        "through GT_18"
    )
    print(
        "claim_boundary = exact unsafe-set characterization through GT_12 and "
        "structural frequency extension through GT_18; arbitrary-n theorem open"
    )


if __name__ == "__main__":
    self_test()
