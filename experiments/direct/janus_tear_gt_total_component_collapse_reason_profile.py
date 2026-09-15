#!/usr/bin/env python3
"""Profile every reachable post-unit 2->1 relation-component collapse.

The exact GT_4,...,GT_8 trace contains ten component-merging post-unit events.
All occur at novelty n-2 and merge the last two relation components into the
single total component.  This checker keeps every unit-reason candidate rather
than selecting one convenient clause.

For each candidate it records entry/fresh origin, every producing frozen
Resolution event, parent geometry and safety, and exact root-axiom provenance
propagated through the full trace.
"""

from __future__ import annotations

from collections import Counter, defaultdict

from janus_tear_gt_component_merge_sources import reduce_clause, source_clauses
from janus_tear_gt_double_bridge_root_owner_provenance import replay_provenance
from janus_tear_gt_novel_branch_audit_v2 import comparison_closure, components
from janus_tear_gt_rank_safety_dichotomy import safety_class

Clause = tuple[int, ...]
RootSource = tuple[str, int | None, Clause]
EXPECTED_BY_N = {4: 0, 5: 4, 6: 1, 7: 2, 8: 3}


def partition(n: int, assignment, pairs):
    closure = comparison_closure(n, assignment, pairs)
    assert closure.acyclic
    parts = tuple(components(closure))
    index = {
        vertex: part_id
        for part_id, part in enumerate(parts)
        for vertex in part
    }
    return parts, index


def root_signature(sources: frozenset[RootSource]):
    owners = tuple(sorted({
        int(owner)
        for kind, owner, _clause in sources
        if kind == "N" and owner is not None
    }))
    transitivity = sum(
        1 for kind, _owner, _clause in sources if kind == "T"
    )
    return (owners, transitivity, len(sources))


def audit(n: int):
    context, _minimum_labels, key_provenance = replay_provenance(n)
    policy = context["policy"]
    pairs = context["pairs"]
    levels = context["levels"]
    target = n - 2

    counts: Counter[str] = Counter()
    novelty_histogram: Counter[int] = Counter()
    candidate_count_histogram: Counter[int] = Counter()
    origin_sets: Counter[tuple[tuple[str, ...], ...]] = Counter()
    candidate_widths: Counter[int] = Counter()
    root_shapes: Counter[tuple[tuple[int, ...], int, int]] = Counter()
    local_event_counts: Counter[int] = Counter()
    parent_widths: Counter[tuple[int, int]] = Counter()
    parent_safety: Counter[tuple[str, str]] = Counter()
    pivot_geometry: Counter[str] = Counter()
    pivot_equals_unit: Counter[bool] = Counter()
    endpoint_shapes: Counter[tuple[int, int]] = Counter()
    unit_positions: Counter[int] = Counter()
    rows = []

    for state in policy.states.values():
        state_id = int(state["id"])
        call_id = int(state["entry_call"])
        novelty = int(levels[call_id])
        if novelty > target:
            continue

        post_events = tuple(state.get("post_units", ()))
        if not post_events:
            continue

        key = tuple(tuple(clause) for clause in state["key"])
        key_set = set(key)
        output = tuple(tuple(clause) for clause in state["resolution_output"])
        output_set = set(output)
        assert key_set <= output_set
        key_sources = key_provenance[state_id]

        resolution_index: dict[Clause, list[dict[str, object]]] = defaultdict(list)
        output_sources: dict[Clause, set[RootSource]] = defaultdict(set)
        for clause in key:
            output_sources[clause].update(key_sources[clause])
        for resolution_event in state.get("resolution_events", ()):
            left = tuple(resolution_event["left"])
            right = tuple(resolution_event["right"])
            resolvent = tuple(resolution_event["resolvent"])
            assert left in key_sources and right in key_sources
            resolution_index[resolvent].append(resolution_event)
            output_sources[resolvent].update(key_sources[left])
            output_sources[resolvent].update(key_sources[right])
        assert set(output_sources) == output_set

        frozen_assignment = dict(context["call_after_pre"][call_id])
        frozen_parts, frozen_index = partition(n, frozen_assignment, pairs)
        current_assignment = dict(frozen_assignment)
        current_cnf = output
        stage_assignment: dict[int, bool] = {}
        unit_position = 0

        for event_index, event in enumerate(post_events):
            if event["kind"] != "unit":
                continue
            unit_position += 1
            literal = int(event["literal"])
            variable = abs(literal)
            value = literal > 0
            assert tuple(event["before"]) == current_cnf
            assert variable not in current_assignment

            before_parts, before_index = partition(
                n, current_assignment, pairs
            )
            after_assignment = dict(current_assignment)
            after_assignment[variable] = value
            after_parts, _after_index = partition(
                n, after_assignment, pairs
            )

            if len(after_parts) < len(before_parts):
                counts["component_merging_units"] += 1
                novelty_histogram[novelty] += 1
                unit_positions[unit_position] += 1
                assert len(before_parts) - len(after_parts) == 1

                low, high = pairs[variable]
                endpoint_shapes[tuple(sorted((
                    len(before_parts[before_index[low]]),
                    len(before_parts[before_index[high]]),
                )))] += 1

                candidates = tuple(
                    tuple(clause)
                    for clause in source_clauses(
                        output, stage_assignment, literal
                    )
                )
                assert candidates
                candidate_count_histogram[len(candidates)] += 1
                candidate_rows = []
                event_origins = []

                for candidate in candidates:
                    labels = []
                    if candidate in key_set:
                        labels.append("ENTRY_KEY")
                    if candidate in resolution_index:
                        labels.append("LOCAL_RESOLVENT")
                    assert labels
                    labels_tuple = tuple(labels)
                    event_origins.append(labels_tuple)
                    candidate_widths[len(candidate)] += 1

                    residual = reduce_clause(candidate, stage_assignment)
                    assert residual == (literal,)
                    source_signature = root_signature(
                        frozenset(output_sources[candidate])
                    )
                    root_shapes[source_signature] += 1

                    producing_rows = []
                    producing_events = tuple(
                        resolution_index.get(candidate, ())
                    )
                    local_event_counts[len(producing_events)] += 1
                    for producing_event in producing_events:
                        left = tuple(producing_event["left"])
                        right = tuple(producing_event["right"])
                        pivot = int(producing_event["pivot"])
                        widths = tuple(sorted((len(left), len(right))))
                        safety = tuple(sorted((
                            str(safety_class(
                                n, left, frozen_assignment, pairs
                            )["classification"]),
                            str(safety_class(
                                n, right, frozen_assignment, pairs
                            )["classification"]),
                        )))
                        parent_widths[widths] += 1
                        parent_safety[safety] += 1

                        pivot_low, pivot_high = pairs[pivot]
                        geometry = (
                            "INTERNAL"
                            if frozen_index[pivot_low]
                            == frozen_index[pivot_high]
                            else "EXTERNAL"
                        )
                        pivot_geometry[geometry] += 1
                        pivot_equals_unit[pivot == variable] += 1

                        producing_rows.append({
                            "attempt": int(producing_event["attempt"]),
                            "pivot": pivot,
                            "pivot_endpoints": pairs[pivot],
                            "pivot_geometry": geometry,
                            "pivot_equals_unit": pivot == variable,
                            "left": left,
                            "right": right,
                            "parent_widths": widths,
                            "parent_safety": safety,
                            "left_root": root_signature(key_sources[left]),
                            "right_root": root_signature(key_sources[right]),
                        })

                    candidate_rows.append({
                        "clause": candidate,
                        "origin": labels_tuple,
                        "width": len(candidate),
                        "root": source_signature,
                        "producing_events": tuple(producing_rows),
                    })

                normalized_origins = tuple(sorted(event_origins, key=repr))
                origin_sets[normalized_origins] += 1
                if all(
                    "LOCAL_RESOLVENT" in labels
                    for labels in event_origins
                ):
                    counts["all_candidates_local"] += 1
                if any("ENTRY_KEY" in labels for labels in event_origins):
                    counts["has_entry_candidate"] += 1
                if any(
                    "LOCAL_RESOLVENT" in labels
                    for labels in event_origins
                ):
                    counts["has_local_candidate"] += 1

                rows.append({
                    "n": n,
                    "state_id": state_id,
                    "call_id": call_id,
                    "novelty": novelty,
                    "target": target,
                    "event_index": event_index,
                    "unit_position": unit_position,
                    "literal": literal,
                    "endpoints": pairs[variable],
                    "before_parts": before_parts,
                    "after_parts": after_parts,
                    "frozen_parts": frozen_parts,
                    "candidate_count": len(candidates),
                    "candidates": tuple(candidate_rows),
                })

            current_assignment = after_assignment
            stage_assignment[variable] = value
            after_raw = event.get("after")
            if after_raw is None:
                break
            current_cnf = tuple(tuple(clause) for clause in after_raw)

    assert counts["component_merging_units"] == EXPECTED_BY_N[n]
    assert all(row["novelty"] == row["target"] for row in rows)
    assert all(len(row["before_parts"]) == 2 for row in rows)
    assert all(len(row["after_parts"]) == 1 for row in rows)

    return {
        "n": n,
        "target": target,
        "counts": tuple(sorted(counts.items())),
        "novelty_histogram": tuple(sorted(novelty_histogram.items())),
        "candidate_count_histogram": tuple(sorted(candidate_count_histogram.items())),
        "origin_sets": tuple(sorted(origin_sets.items(), key=repr)),
        "candidate_widths": tuple(sorted(candidate_widths.items())),
        "root_shapes": tuple(sorted(root_shapes.items(), key=repr)),
        "local_event_counts": tuple(sorted(local_event_counts.items())),
        "parent_widths": tuple(sorted(parent_widths.items())),
        "parent_safety": tuple(sorted(parent_safety.items(), key=repr)),
        "pivot_geometry": tuple(sorted(pivot_geometry.items())),
        "pivot_equals_unit": tuple(sorted(pivot_equals_unit.items())),
        "endpoint_shapes": tuple(sorted(endpoint_shapes.items())),
        "unit_positions": tuple(sorted(unit_positions.items())),
        "rows": tuple(rows),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_novelty: Counter[int] = Counter()
    aggregate_candidate_counts: Counter[int] = Counter()
    aggregate_origins: Counter[tuple[tuple[str, ...], ...]] = Counter()
    aggregate_widths: Counter[int] = Counter()
    aggregate_root_shapes: Counter = Counter()
    aggregate_local_counts: Counter[int] = Counter()
    aggregate_parent_widths: Counter[tuple[int, int]] = Counter()
    aggregate_parent_safety: Counter[tuple[str, str]] = Counter()
    aggregate_geometry: Counter[str] = Counter()
    aggregate_pivot_equals: Counter[bool] = Counter()
    aggregate_endpoint_shapes: Counter[tuple[int, int]] = Counter()
    aggregate_positions: Counter[int] = Counter()
    all_rows = []

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_novelty.update(dict(data["novelty_histogram"]))
        aggregate_candidate_counts.update(dict(data["candidate_count_histogram"]))
        aggregate_origins.update(dict(data["origin_sets"]))
        aggregate_widths.update(dict(data["candidate_widths"]))
        aggregate_root_shapes.update(dict(data["root_shapes"]))
        aggregate_local_counts.update(dict(data["local_event_counts"]))
        aggregate_parent_widths.update(dict(data["parent_widths"]))
        aggregate_parent_safety.update(dict(data["parent_safety"]))
        aggregate_geometry.update(dict(data["pivot_geometry"]))
        aggregate_pivot_equals.update(dict(data["pivot_equals_unit"]))
        aggregate_endpoint_shapes.update(dict(data["endpoint_shapes"]))
        aggregate_positions.update(dict(data["unit_positions"]))
        all_rows.extend(data["rows"])
        print(f"ORDER_SIZE = {n}")
        print(f"  target = {data['target']}")
        print(f"  counts = {data['counts']}")
        print(f"  novelty_histogram = {data['novelty_histogram']}")
        print(f"  candidate_count_histogram = {data['candidate_count_histogram']}")
        print(f"  origin_sets = {data['origin_sets']}")
        print(f"  candidate_widths = {data['candidate_widths']}")
        print(f"  root_shapes = {data['root_shapes']}")
        print(f"  local_event_counts = {data['local_event_counts']}")
        print(f"  parent_widths = {data['parent_widths']}")
        print(f"  parent_safety = {data['parent_safety']}")
        print(f"  pivot_geometry = {data['pivot_geometry']}")
        print(f"  pivot_equals_unit = {data['pivot_equals_unit']}")
        print(f"  endpoint_shapes = {data['endpoint_shapes']}")
        print(f"  unit_positions = {data['unit_positions']}")
        print(f"  rows = {data['rows']}")

    assert aggregate_counts["component_merging_units"] == 10
    print("JANUS_GT_TOTAL_COMPONENT_COLLAPSE_REASON_PROFILE = PASS")
    print(f"AGGREGATE_COUNTS = {tuple(sorted(aggregate_counts.items()))}")
    print(f"AGGREGATE_NOVELTY = {tuple(sorted(aggregate_novelty.items()))}")
    print(f"AGGREGATE_CANDIDATE_COUNTS = {tuple(sorted(aggregate_candidate_counts.items()))}")
    print(f"AGGREGATE_ORIGINS = {tuple(sorted(aggregate_origins.items(), key=repr))}")
    print(f"AGGREGATE_WIDTHS = {tuple(sorted(aggregate_widths.items()))}")
    print(f"AGGREGATE_ROOT_SHAPES = {tuple(sorted(aggregate_root_shapes.items(), key=repr))}")
    print(f"AGGREGATE_LOCAL_COUNTS = {tuple(sorted(aggregate_local_counts.items()))}")
    print(f"AGGREGATE_PARENT_WIDTHS = {tuple(sorted(aggregate_parent_widths.items()))}")
    print(f"AGGREGATE_PARENT_SAFETY = {tuple(sorted(aggregate_parent_safety.items(), key=repr))}")
    print(f"AGGREGATE_PIVOT_GEOMETRY = {tuple(sorted(aggregate_geometry.items()))}")
    print(f"AGGREGATE_PIVOT_EQUALS_UNIT = {tuple(sorted(aggregate_pivot_equals.items()))}")
    print(f"AGGREGATE_ENDPOINT_SHAPES = {tuple(sorted(aggregate_endpoint_shapes.items()))}")
    print(f"AGGREGATE_UNIT_POSITIONS = {tuple(sorted(aggregate_positions.items()))}")
    for row in all_rows:
        print(f"ROW = {row}")
    print(
        "claim_boundary = exact finite all-reason provenance profile for the "
        "ten reachable post-unit total-component collapses through GT_8; no "
        "arbitrary-n derived-unit localization theorem asserted"
    )


if __name__ == "__main__":
    self_test()
