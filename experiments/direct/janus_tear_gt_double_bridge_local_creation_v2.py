#!/usr/bin/env python3
"""Failure-tolerant local creation census for GT double-bridge pairs.

Version 1 incorrectly promoted the exact-key tail/tail invariant to raw
`post_result`.  Raw local output may contain non-tail complementary bridge pairs;
the temporal question is precisely whether those pairs become frozen parents in
the next exact key.

This version keeps the three stages separate:

    entry key K
      -> frozen one-pass Resolution output R
      -> post-unit residual P.

For every double-bridge pair in P it records bridge roles and cut equality,
then determines whether:

- a double-bridge source pair already existed in R;
- post-units created the pair;
- the R-pair was inherited from K;
- one or two locally generated clauses were required.

Required local clauses are traced to their frozen Resolution parents.  No
particular role/cut pattern is asserted in advance.
"""

from __future__ import annotations

from collections import Counter
from itertools import product

from janus_tear_gt_double_bridge_local_creation import (
    event_signature,
    is_double_bridge_source,
    local_events_by_resolvent,
    raw_origin_labels,
    residual_sources,
)
from janus_tear_gt_double_bridge_transition_birth import (
    enumerate_double_bridges,
    unit_assignments,
)
from janus_tear_gt_component_tree_clause_audit import execution_context


def audit(n: int):
    context = execution_context(n)
    policy = context["policy"]
    pairs = context["pairs"]
    levels = context["levels"]
    target = n - 2

    counts: Counter[str] = Counter()
    stage_modes: Counter[str] = Counter()
    post_role_pairs: Counter[tuple[str, str]] = Counter()
    post_cut_relation: Counter[str] = Counter()
    source_role_pairs: Counter[tuple[str, str]] = Counter()
    source_cut_relation: Counter[str] = Counter()
    required_local_sides: Counter[int] = Counter()
    origin_patterns: Counter[tuple[tuple[str, ...], tuple[str, ...]]] = Counter()
    event_parent_classes: Counter[tuple[str, str]] = Counter()
    event_literal_roles: Counter[tuple[tuple[str, str], ...]] = Counter()
    event_pivot_relation: Counter[bool] = Counter()
    post_unit_count_on_pair_states: Counter[int] = Counter()
    novelty_histogram: Counter[int] = Counter()
    source_multiplicity: Counter[tuple[int, int]] = Counter()
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
        resolution_output = tuple(
            tuple(clause) for clause in state["resolution_output"]
        )
        post = tuple(tuple(clause) for clause in post_result)
        post_units = unit_assignments(state.get("post_units", ()))

        post_pairs = enumerate_double_bridges(n, post, after_assignment, pairs)
        if not post_pairs:
            continue
        post_unit_count_on_pair_states[len(post_units)] += len(post_pairs)

        raw_sources = residual_sources(resolution_output, post_units)
        assert set(post) == set(raw_sources)
        origins = raw_origin_labels(state)
        events_by_resolvent = local_events_by_resolvent(state)

        for pair_record in post_pairs:
            counts["post_double_bridge_occurrences"] += 1
            novelty_histogram[novelty] += 1
            pivot = int(pair_record["pivot"])
            post_left = tuple(pair_record["left"])
            post_right = tuple(pair_record["right"])
            left_post_bridge = pair_record["left_bridge"]
            right_post_bridge = pair_record["right_bridge"]
            post_roles = tuple(sorted((
                str(left_post_bridge["role"]),
                str(right_post_bridge["role"]),
            )))
            post_role_pairs[post_roles] += 1
            post_same_cut = left_post_bridge["cut"] == right_post_bridge["cut"]
            post_cut_relation["SAME_CUT" if post_same_cut else "DIFFERENT_CUT"] += 1
            if post_same_cut:
                counts["post_same_cut"] += 1
            if post_roles == ("TAIL_SINGLETON", "TAIL_SINGLETON"):
                counts["post_tail_tail"] += 1
            else:
                counts["post_non_tail_pair"] += 1

            left_sources = raw_sources[post_left]
            right_sources = raw_sources[post_right]
            source_multiplicity[(len(left_sources), len(right_sources))] += 1

            source_pairs = []
            for left_source, right_source in product(left_sources, right_sources):
                source_pair = is_double_bridge_source(
                    n,
                    left_source,
                    right_source,
                    pivot,
                    before_assignment,
                    pairs,
                )
                if source_pair is not None:
                    source_pairs.append((left_source, right_source, source_pair))

            if not source_pairs:
                mode = "CREATED_BY_POST_UNITS"
                counts["post_unit_created"] += 1
                stage_modes[mode] += 1
                if len(examples) < 120:
                    examples.append({
                        "n": n,
                        "state_id": state_id,
                        "call_id": call_id,
                        "novelty": novelty,
                        "mode": mode,
                        "pivot": pivot,
                        "post_roles": post_roles,
                        "post_same_cut": post_same_cut,
                        "post_left": post_left,
                        "post_right": post_right,
                        "post_units": tuple(sorted(post_units.items())),
                        "left_sources": left_sources,
                        "right_sources": right_sources,
                    })
                continue

            def local_cost(item):
                left_source, right_source, _record = item
                left_required = "ENTRY_KEY" not in origins[left_source]
                right_required = "ENTRY_KEY" not in origins[right_source]
                return (
                    int(left_required) + int(right_required),
                    left_source,
                    right_source,
                )

            left_source, right_source, source_pair = min(
                source_pairs, key=local_cost
            )
            left_source_bridge = source_pair["left_bridge"]
            right_source_bridge = source_pair["right_bridge"]
            source_roles = tuple(sorted((
                str(left_source_bridge["role"]),
                str(right_source_bridge["role"]),
            )))
            source_role_pairs[source_roles] += 1
            source_same_cut = (
                left_source_bridge["cut"] == right_source_bridge["cut"]
            )
            source_cut_relation[
                "SAME_CUT" if source_same_cut else "DIFFERENT_CUT"
            ] += 1

            left_origin = tuple(sorted(origins[left_source]))
            right_origin = tuple(sorted(origins[right_source]))
            origin_patterns[(left_origin, right_origin)] += 1
            left_local_required = "ENTRY_KEY" not in origins[left_source]
            right_local_required = "ENTRY_KEY" not in origins[right_source]
            local_sides = int(left_local_required) + int(right_local_required)
            required_local_sides[local_sides] += 1

            if local_sides == 0:
                mode = "INHERITED_FROM_ENTRY_KEY"
                counts["entry_inherited"] += 1
            elif local_sides == 1:
                mode = "CREATED_WITH_ONE_LOCAL_SIDE"
                counts["one_local_side"] += 1
            else:
                mode = "CREATED_WITH_TWO_LOCAL_SIDES"
                counts["two_local_sides"] += 1
            stage_modes[mode] += 1

            local_event_details = []
            for source, eventual_literal, required in (
                (left_source, pivot, left_local_required),
                (right_source, -pivot, right_local_required),
            ):
                if not required:
                    continue
                assert source in events_by_resolvent
                signatures = []
                for event in events_by_resolvent[source]:
                    signature = event_signature(
                        n,
                        event,
                        eventual_literal,
                        before_assignment,
                        pairs,
                    )
                    signatures.append(signature)
                    event_parent_classes[signature["parent_classes"]] += 1
                    event_literal_roles[signature["literal_roles"]] += 1
                    event_pivot_relation[
                        bool(signature["event_pivot_equals_eventual"])
                    ] += 1
                local_event_details.append({
                    "source": source,
                    "eventual_literal": eventual_literal,
                    "signatures": tuple(signatures),
                })

            if len(examples) < 120:
                examples.append({
                    "n": n,
                    "state_id": state_id,
                    "call_id": call_id,
                    "novelty": novelty,
                    "mode": mode,
                    "pivot": pivot,
                    "post_roles": post_roles,
                    "post_same_cut": post_same_cut,
                    "post_left": post_left,
                    "post_right": post_right,
                    "post_units": tuple(sorted(post_units.items())),
                    "source_left": left_source,
                    "source_right": right_source,
                    "source_roles": source_roles,
                    "source_same_cut": source_same_cut,
                    "origins": (left_origin, right_origin),
                    "local_events": tuple(local_event_details),
                })

    assert counts["post_double_bridge_occurrences"] > 0
    assert (
        counts["entry_inherited"]
        + counts["one_local_side"]
        + counts["two_local_sides"]
        + counts["post_unit_created"]
        == counts["post_double_bridge_occurrences"]
    )

    return {
        "n": n,
        "target": target,
        "counts": tuple(sorted(counts.items())),
        "stage_modes": tuple(sorted(stage_modes.items())),
        "post_role_pairs": tuple(sorted(post_role_pairs.items(), key=repr)),
        "post_cut_relation": tuple(sorted(post_cut_relation.items())),
        "source_role_pairs": tuple(sorted(source_role_pairs.items(), key=repr)),
        "source_cut_relation": tuple(sorted(source_cut_relation.items())),
        "required_local_sides": tuple(sorted(required_local_sides.items())),
        "origin_patterns": tuple(sorted(origin_patterns.items(), key=repr)),
        "event_parent_classes": tuple(
            sorted(event_parent_classes.items(), key=repr)
        ),
        "event_literal_roles": tuple(
            sorted(event_literal_roles.items(), key=repr)
        ),
        "event_pivot_relation": tuple(sorted(event_pivot_relation.items())),
        "post_unit_count_on_pair_states": tuple(
            sorted(post_unit_count_on_pair_states.items())
        ),
        "novelty_histogram": tuple(sorted(novelty_histogram.items())),
        "source_multiplicity": tuple(sorted(source_multiplicity.items())),
        "examples": tuple(examples),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_modes: Counter[str] = Counter()
    aggregate_post_roles: Counter[tuple[str, str]] = Counter()
    aggregate_post_cuts: Counter[str] = Counter()
    aggregate_source_roles: Counter[tuple[str, str]] = Counter()
    aggregate_source_cuts: Counter[str] = Counter()
    aggregate_local_sides: Counter[int] = Counter()
    aggregate_origins: Counter[tuple[tuple[str, ...], tuple[str, ...]]] = Counter()
    aggregate_parent_classes: Counter[tuple[str, str]] = Counter()
    aggregate_literal_roles: Counter[tuple[tuple[str, str], ...]] = Counter()
    aggregate_pivot_relation: Counter[bool] = Counter()
    aggregate_post_units: Counter[int] = Counter()
    aggregate_novelty: Counter[int] = Counter()
    aggregate_multiplicity: Counter[tuple[int, int]] = Counter()
    rows = []

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_modes.update(dict(data["stage_modes"]))
        aggregate_post_roles.update(dict(data["post_role_pairs"]))
        aggregate_post_cuts.update(dict(data["post_cut_relation"]))
        aggregate_source_roles.update(dict(data["source_role_pairs"]))
        aggregate_source_cuts.update(dict(data["source_cut_relation"]))
        aggregate_local_sides.update(dict(data["required_local_sides"]))
        aggregate_origins.update(dict(data["origin_patterns"]))
        aggregate_parent_classes.update(dict(data["event_parent_classes"]))
        aggregate_literal_roles.update(dict(data["event_literal_roles"]))
        aggregate_pivot_relation.update(dict(data["event_pivot_relation"]))
        aggregate_post_units.update(dict(data["post_unit_count_on_pair_states"]))
        aggregate_novelty.update(dict(data["novelty_histogram"]))
        aggregate_multiplicity.update(dict(data["source_multiplicity"]))
        rows.append((
            n,
            data["target"],
            data["counts"],
            data["stage_modes"],
            data["post_role_pairs"],
            data["post_cut_relation"],
            data["event_parent_classes"],
        ))
        print(f"ORDER_SIZE = {n}")
        print(f"  target = {data['target']}")
        print(f"  counts = {data['counts']}")
        print(f"  stage_modes = {data['stage_modes']}")
        print(f"  post_role_pairs = {data['post_role_pairs']}")
        print(f"  post_cut_relation = {data['post_cut_relation']}")
        print(f"  source_role_pairs = {data['source_role_pairs']}")
        print(f"  source_cut_relation = {data['source_cut_relation']}")
        print(f"  required_local_sides = {data['required_local_sides']}")
        print(f"  origin_patterns = {data['origin_patterns']}")
        print(f"  event_parent_classes = {data['event_parent_classes']}")
        print(f"  event_literal_roles = {data['event_literal_roles']}")
        print(f"  event_pivot_relation = {data['event_pivot_relation']}")
        print(f"  post_unit_count_on_pair_states = {data['post_unit_count_on_pair_states']}")
        print(f"  novelty_histogram = {data['novelty_histogram']}")
        print(f"  source_multiplicity = {data['source_multiplicity']}")
        print(f"  examples = {data['examples']}")

    assert aggregate_counts["post_double_bridge_occurrences"] > 0
    print("JANUS_GT_DOUBLE_BRIDGE_LOCAL_CREATION_V2 = PASS")
    print(f"ROWS = {tuple(rows)}")
    print(f"AGGREGATE_COUNTS = {tuple(sorted(aggregate_counts.items()))}")
    print(f"AGGREGATE_STAGE_MODES = {tuple(sorted(aggregate_modes.items()))}")
    print(f"AGGREGATE_POST_ROLE_PAIRS = {tuple(sorted(aggregate_post_roles.items(), key=repr))}")
    print(f"AGGREGATE_POST_CUT_RELATION = {tuple(sorted(aggregate_post_cuts.items()))}")
    print(f"AGGREGATE_SOURCE_ROLE_PAIRS = {tuple(sorted(aggregate_source_roles.items(), key=repr))}")
    print(f"AGGREGATE_SOURCE_CUT_RELATION = {tuple(sorted(aggregate_source_cuts.items()))}")
    print(f"AGGREGATE_REQUIRED_LOCAL_SIDES = {tuple(sorted(aggregate_local_sides.items()))}")
    print(f"AGGREGATE_ORIGIN_PATTERNS = {tuple(sorted(aggregate_origins.items(), key=repr))}")
    print(f"AGGREGATE_EVENT_PARENT_CLASSES = {tuple(sorted(aggregate_parent_classes.items(), key=repr))}")
    print(f"AGGREGATE_EVENT_LITERAL_ROLES = {tuple(sorted(aggregate_literal_roles.items(), key=repr))}")
    print(f"AGGREGATE_EVENT_PIVOT_RELATION = {tuple(sorted(aggregate_pivot_relation.items()))}")
    print(f"AGGREGATE_POST_UNITS = {tuple(sorted(aggregate_post_units.items()))}")
    print(f"AGGREGATE_NOVELTY = {tuple(sorted(aggregate_novelty.items()))}")
    print(f"AGGREGATE_SOURCE_MULTIPLICITY = {tuple(sorted(aggregate_multiplicity.items()))}")
    print(
        "claim_boundary = finite raw post-output/local-creation census through "
        "GT_8; exact-key eligibility remains a separate temporal layer"
    )


if __name__ == "__main__":
    self_test()
