#!/usr/bin/env python3
"""Profile exact reasons for every reachable post-unit 2->1 component collapse.

The reachable GT_4,...,GT_8 census found ten post-unit assignments which merge
relation components.  Every one occurs at novelty n-2 and maps the last two
components to the single total component.  This checker determines why those
units exist without choosing an arbitrary reason clause.

For every merge event it records all clauses in the frozen Resolution output
which reduce to the propagated unit under earlier units of the same post batch.
For every such candidate it records:

- whether the clause is inherited in the exact entry key, freshly emitted by
  the frozen local pass, or both;
- every local Resolution event producing it;
- frozen parent widths, safety classes, and inference-pivot geometry;
- exact root-axiom provenance propagated through the complete trace;
- non-minimality owners and transitivity ancestry;
- the relation-component shapes before and after the unit.

The checker is a finite proof-carrying profile.  It asserts replay completeness,
the already observed ten 2->1 collapses, and no particular reason template.
"""

from __future__ import annotations

from collections import Counter, defaultdict

from janus_tear_gt_component_merge_sources import reduce_clause, source_clauses
from janus_tear_gt_component_tree_clause_audit import execution_context
from janus_tear_gt_double_bridge_root_owner_provenance import replay_provenance
from janus_tear_gt_novel_branch_audit_v2 import comparison_closure, components
from janus_tear_gt_rank_safety_dichotomy import safety_class

Clause = tuple[int, ...]
RootSource = tuple[str, int | None, Clause]


def component_partition(n: int, assignment, pairs):
    closure = comparison_closure(n, assignment, pairs)
    assert closure.acyclic
    parts = components(closure)
    index = {
        vertex: component_id
        for component_id, part in enumerate(parts)
        for vertex in part
    }
    return tuple(parts), index


def root_signature(sources: frozenset[RootSource]):
    owners = tuple(sorted({
        int(owner)
        for kind, owner, _clause in sources
        if kind == "N" and owner is not None
    }))
    transitivity_count = sum(
        1 for kind, _owner, _clause in sources if kind == "T"
    )
    return {
        "nonminimality_owners": owners,
        "transitivity_count": transitivity_count,
        "root_source_count": len(sources),
    }


def origin_labels(clause: Clause, key_set, event_index):
    labels = []
    if clause in key_set:
        labels.append("ENTRY_KEY")
    if clause in event_index:
        labels.append("LOCAL_RESOLVENT")
    assert labels
    return tuple(labels)


def audit(n: int):
    context, _minimum_labels, key_provenance = replay_provenance(n)
    policy = context["policy"]
    pairs = context["pairs"]
    levels = context["levels"]
    target = n - 2

    counts: Counter[str] = Counter()
    novelty_histogram: Counter[int] = Counter()
    candidate_count_histogram: Counter[int] = Counter()
    candidate_origin_sets: Counter[tuple[tuple[str, ...], ...]] = Counter()
    candidate_widths: Counter[int] = Counter()
    candidate_residual_widths: Counter[int] = Counter()
    candidate_root_shapes: Counter[tuple[int, int, int]] = Counter()
    local_event_count_histogram: Counter[int] = Counter()
    local_parent_width_pairs: Counter[tuple[int, int]] = Counter()
    local_parent_safety_pairs: Counter[tuple[str, str]] = Counter()
    local_pivot_geometry: Counter[str] = Counter()
    local_pivot_equals_unit: Counter[bool] = Counter()
    merge_endpoint_shapes: Counter[tuple[int, int]] = Counter()
    unit_position_histogram: Counter[int] = Counter()
    rows = []

    for state in policy.states.values():
        state_id = int(state["id"])
        call_id = int(state["entry_call"])
        novelty = int(levels[call_id])
        if novelty > target:
            continue

        events = tuple(state.get("post_units", ()))
        if not events:
            continue

        key = tuple(tuple(clause) for clause in state["key"])
        key_set = set(key)
        output = tuple(tuple(clause) for clause in state["resolution_output"])
        output_set = set(output)
        assert key_set <= output_set
        entry_provenance = key_provenance[state_id]

        resolution_index: dict[Clause, list[dict[str, object]]] = defaultdict(list)
        output_provenance: dict[Clause, set[RootSource]] = defaultdict(set)
        for clause in key:
            output_provenance[clause].update(entry_provenance[clause])
        for event in state.get("resolution_events", ()):
            left = tuple(event["left"])
            right = tuple(event["right"])
            resolvent = tuple(event["resolvent"])
            assert left in entry_provenance and right in entry_provenance
            resolution_index[resolvent].append(event)
            output_provenance[resolvent].update(entry_provenance[left])
            output_provenance[resolvent].update(entry_provenance[right])
        assert set(output_provenance) == output_set

        frozen_assignment = dict(context["call_after_pre"][call_id])
        current_assignment = dict(frozen_assignment)
        current_cnf = output
        stage_assignments: dict[int, bool] = {}
        unit_position = 0

        for event_index, event in enumerate(events):
            if event["kind"] != "unit":
                continue
            unit_position += 1
            literal = int(event["literal"])
            variable = abs(literal)
            value = literal > 0
            assert tuple(event["before"]) == current_cnf
            assert variable not in current_assignment

            before_parts, before_index = component_partition(
                n, current_assignment, pairs
            )
            after_assignment = dict(current_assignment)
            after_assignment[variable] = value
            after_parts, _after_index = component_partition(
                n, after_assignment, pairs
            )

            if len(after_parts) >= len(before_parts):
                current_assignment = after_assignment
                stage_assignments[variable] = value
                after_raw = event.get("after")
                if after_raw is None:
                    break
                current_cnf = tuple(tuple(clause) for clause in after_raw)
                continue

            counts["component_merging_units"] += 1
            novelty_histogram[novelty] += 1
            unit_position_histogram[unit_position] += 1
            assert len(before_parts) - len(after_parts) == 1

            endpoint_low, endpoint_high = pairs[variable]
            left_size = len(before_parts[before_index[endpoint_low]])
            right_size = len(before_parts[before_index[endpoint_high]])
            merge_endpoint_shapes[tuple(sorted((left_size, right_size)))] += 1

            candidates = source_clauses(output, stage_assignments, literal)
            assert candidates
            candidate_count_histogram[len(candidates)] += 1

            candidate_rows = []
            origin_set = []
            for candidate in candidates:
                candidate = tuple(candidate)
                labels = origin_labels(candidate, key_set, resolution_index)
                origin_set.append(labels)
                candidate_widths[len(candidate)] += 1
                residual = reduce_clause(candidate, stage_assignments)
                assert residual == (literal,)
                candidate_residual_widths[len(residual)] += 1

                roots = frozenset(output_provenance[candidate])
                root_info = root_signature(roots)
                candidate_root_shapes[(
                    len(root_info["nonminimality_owners"]),
                    int(root_info["transitivity_count"]),
                    int(root_info["root_source_count"]),
                )] += 1

                local_rows = []
                local_events = tuple(resolution_index.get(candidate, ()))
                local_event_count_histogram[len(local_events)] += 1
                for producing_event in local_events:
                    left = tuple(producing_event["left"])
                    right = tuple(producing_event["right"])
                    pivot = int(producing_event["pivot"])
                    parent_widths = tuple(sorted((len(left), len(right))))
                    parent_safety = tuple(sorted((
                        str(safety_class(
                            n, left, frozen_assignment, pairs
                        )["classification"]),
                        str(safety_class(
                            n, right, frozen_assignment, pairs
                        )["classification"]),
                    )))
                    local_parent_width_pairs[parent_widths] += 1
                    local_parent_safety_pairs[parent_safety] += 1

                    pivot_low, pivot_high = pairs[pivot]
                    frozen_parts, frozen_index = component_partition(
                        n, frozen_assignment, pairs
                    )
                    pivot_geometry = (
                        "INTERNAL"
                        if frozen_index[pivot_low] == frozen_index[pivot_high]
                        else "EXTERNAL"
                    )
                    local_pivot_geometry[pivot_geometry] += 1
                    local_pivot_equals_unit[pivot == variable] += 1

                    local_rows.append({
                        "attempt": int(producing_event["attempt"]),
                        "pivot": pivot,
                        "pivot_endpoints": pairs[pivot],
                        "pivot_geometry": pivot_geometry,
                        "pivot_equals_unit_variable": pivot == variable,
                        "left": left,
                        "right": right,
                        "parent_widths": parent_widths,
                        "parent_safety": parent_safety,
                        "left_root": root_signature(
                            entry_provenance[left]
                        ),
                        "right_root": root_signature(
                            entry_provenance[right]
                        ),
                        "frozen_component_shape": tuple(sorted(
                            len(part) for part in frozen_parts
                        )),
                    })

                candidate_rows.append({
                    "clause": candidate,
                    "origin": labels,
                    "source_width": len(candidate),
                    "root": root_info,
                    "local_event_count": len(local_events),
                    "local_events": tuple(local_rows),
                })

            normalized_origins = tuple(sorted(origin_set, key=repr))
            candidate_origin_sets[normalized_origins] += 1
            if all("LOCAL_RESOLVENT" in labels for labels in origin_set):
                counts["all_candidates_local_resolvents"] += 1
            if any("ENTRY_KEY" in labels for labels in origin_set):
                counts["has_entry_key_candidate"] += 1
            if any("LOCAL_RESOLVENT" in labels for labels in origin_set):
                counts["has_local_resolvent_candidate"] += 1

            rows.append({
                "n": n,
                "state_id": state_id,
                "call_id": call_id,
                "novelty": novelty,
                "target": target,
                "event_index": event_index,
                "unit_position": unit_position,
                "literal": literal,
                "variable": variable,
                "endpoints": pairs[variable],
                "before_parts": before_parts,
                "after_parts": after_parts,
                "before_component_count": len(before_parts),
                "after_component_count": len(after_parts),
                "candidate_count": len(candidates),
                "candidates": tuple(candidate_rows),
            })

            current_assignment = after_assignment
            stage_assignments[variable] = value
            after_raw = event.get("after")
            if after_raw is None:
                break
            current_cnf = tuple(tuple(clause) for clause in after_raw)

    assert counts["component_merging_units"] == 10
    assert all(int(row["novelty"]) == int(row["target"]) for row in rows)
    assert all(int(row["before_component_count"]) == 2 for row in rows)
    assert all(int(row["after_component_count"]) == 1 for row in rows)

    return {
        "n": n,
        "target": target,
        "counts": tuple(sorted(counts.items())),
        "novelty_histogram": tuple(sorted(novelty_histogram.items())),
        "candidate_count_histogram": tuple(sorted(candidate_count_histogram.items())),
        "candidate_origin_sets": tuple(sorted(candidate_origin_sets.items(), key=repr)),
        "candidate_widths": tuple(sorted(candidate_widths.items())),
        "candidate_residual_widths": tuple(sorted(candidate_residual_widths.items())),
        "candidate_root_shapes": tuple(sorted(candidate_root_shapes.items())),
        "local_event_count_histogram": tuple(sorted(local_event_count_histogram.items())),
        "local_parent_width_pairs": tuple(sorted(local_parent_width_pairs.items())),
        "local_parent_safety_pairs": tuple(sorted(local_parent_safety_pairs.items(), key=repr)),
        "local_pivot_geometry": tuple(sorted(local_pivot_geometry.items())),
        "local_pivot_equals_unit": tuple(sorted(local_pivot_equals_unit.items())),
        "merge_endpoint_shapes": tuple(sorted(merge_endpoint_shapes.items())),
        "unit_position_histogram": tuple(sorted(unit_position_histogram.items())),
        "rows": tuple(rows),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_novelty: Counter[int] = Counter()
    aggregate_candidate_counts: Counter[int] = Counter()
    aggregate_origins: Counter[tuple[tuple[str, ...], ...]] = Counter()
    aggregate_widths: Counter[int] = Counter()
    aggregate_residual_widths: Counter[int] = Counter()
    aggregate_root_shapes: Counter[tuple[int, int, int]] = Counter()
    aggregate_local_counts: Counter[int] = Counter()
    aggregate_parent_widths: Counter[tuple[int, int]] = Counter()
    aggregate_parent_safety: Counter[tuple[str, str]] = Counter()
    aggregate_pivot_geometry: Counter[str] = Counter()
    aggregate_pivot_equals_unit: Counter[bool] = Counter()
    aggregate_endpoint_shapes: Counter[tuple[int, int]] = Counter()
    aggregate_positions: Counter[int] = Counter()
    all_rows = []

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_novelty.update(dict(data["novelty_histogram"]))
        aggregate_candidate_counts.update(dict(data["candidate_count_histogram"]))
        aggregate_origins.update(dict(data["candidate_origin_sets"]))
        aggregate_widths.update(dict(data["candidate_widths"]))
        aggregate_residual_widths.update(dict(data["candidate_residual_widths"]))
        aggregate_root_shapes.update(dict(data["candidate_root_shapes"]))
        aggregate_local_counts.update(dict(data["local_event_count_histogram"]))
        aggregate_parent_widths.update(dict(data["local_parent_width_pairs"]))
        aggregate_parent_safety.update(dict(data["local_parent_safety_pairs"]))
        aggregate_pivot_geometry.update(dict(data["local_pivot_geometry"]))
        aggregate_pivot_equals_unit.update(dict(data["local_pivot_equals_unit"]))
        aggregate_endpoint_shapes.update(dict(data["merge_endpoint_shapes"]))
        aggregate_positions.update(dict(data["unit_position_histogram"]))
        all_rows.extend(data["rows"])
        print(f"ORDER_SIZE = {n}")
        print(f"  target = {data['target']}")
        print(f"  counts = {data['counts']}")
        print(f"  novelty_histogram = {data['novelty_histogram']}")
        print(f"  candidate_count_histogram = {data['candidate_count_histogram']}")
        print(f"  candidate_origin_sets = {data['candidate_origin_sets']}")
        print(f"  candidate_widths = {data['candidate_widths']}")
        print(f"  candidate_root_shapes = {data['candidate_root_shapes']}")
        print(f"  local_event_count_histogram = {data['local_event_count_histogram']}")
        print(f"  local_parent_width_pairs = {data['local_parent_width_pairs']}")
        print(f"  local_parent_safety_pairs = {data['local_parent_safety_pairs']}")
        print(f"  local_pivot_geometry = {data['local_pivot_geometry']}")
        print(f"  local_pivot_equals_unit = {data['local_pivot_equals_unit']}")
        print(f"  merge_endpoint_shapes = {data['merge_endpoint_shapes']}")
        print(f"  unit_position_histogram = {data['unit_position_histogram']}")
        print(f"  rows = {data['rows']}")

    assert aggregate_counts["component_merging_units"] == 10
    print("JANUS_GT_TOTAL_COMPONENT_COLLAPSE_REASON_PROFILE = PASS")
    print(f"AGGREGATE_COUNTS = {tuple(sorted(aggregate_counts.items()))}")
    print(f"AGGREGATE_NOVELTY = {tuple(sorted(aggregate_novelty.items()))}")
    print(f"AGGREGATE_CANDIDATE_COUNTS = {tuple(sorted(aggregate_candidate_counts.items()))}")
    print(f"AGGREGATE_ORIGINS = {tuple(sorted(aggregate_origins.items(), key=repr))}")
    print(f"AGGREGATE_WIDTHS = {tuple(sorted(aggregate_widths.items()))}")
    print(f"AGGREGATE_RESIDUAL_WIDTHS = {tuple(sorted(aggregate_residual_widths.items()))}")
    print(f"AGGREGATE_ROOT_SHAPES = {tuple(sorted(aggregate_root_shapes.items()))}")
    print(f"AGGREGATE_LOCAL_COUNTS = {tuple(sorted(aggregate_local_counts.items()))}")
    print(f"AGGREGATE_PARENT_WIDTHS = {tuple(sorted(aggregate_parent_widths.items()))}")
    print(f"AGGREGATE_PARENT_SAFETY = {tuple(sorted(aggregate_parent_safety.items(), key=repr))}")
    print(f"AGGREGATE_PIVOT_GEOMETRY = {tuple(sorted(aggregate_pivot_geometry.items()))}")
    print(f"AGGREGATE_PIVOT_EQUALS_UNIT = {tuple(sorted(aggregate_pivot_equals_unit.items()))}")
    print(f"AGGREGATE_ENDPOINT_SHAPES = {tuple(sorted(aggregate_endpoint_shapes.items()))}")
    print(f"AGGREGATE_UNIT_POSITIONS = {tuple(sorted(aggregate_positions.items()))}")
    for row in all_rows:
        print(f"ROW = {row}")
    print(
        "claim_boundary = exact finite reason/provenance profile for all ten "
        "reachable post-unit total-component collapses through GT_8; no "
        "arbitrary-n derived-unit localization theorem asserted"
    )


if __name__ == "__main__":
    self_test()
