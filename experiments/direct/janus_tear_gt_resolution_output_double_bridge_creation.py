#!/usr/bin/env python3
"""Audit double-bridge creation in the raw frozen Resolution output.

The stage decomposition for C024 is:

    exact entry key K
      -> frozen one-pass Resolution output R
      -> post-unit residual P
      -> branch/child-preunit next exact key K'.

The corrected post-result audit found that every P-pair which already had a
pair source in R used two entry-key clauses, while 553 further P-pairs were
created by post-units.  That does not exclude a transient locally-created pair
inside R which is then deleted by post-units.

This checker closes that finite gap directly.  For every pre-frontier state of
GT_4,...,GT_8 it enumerates every complementary component-spanning
double-bridge pair in R and classifies the minimum number of clauses which are
available only as fresh one-pass resolvents:

    0 = both clauses already occur in K;
    1 = exactly one clause requires local Resolution;
    2 = both clauses require local Resolution.

For each locally-required side it records the frozen parent safety classes,
the eventual pivot-literal role in those parents, and whether the inference
pivot equals the eventual double-bridge pivot.  The checker asserts accounting
completeness only; any locally-created pair is printed rather than suppressed.
"""

from __future__ import annotations

from collections import Counter, defaultdict

from janus_tear_gt_component_tree_clause_audit import execution_context
from janus_tear_gt_double_bridge_local_creation import event_signature
from janus_tear_gt_double_bridge_transition_birth import enumerate_double_bridges

Clause = tuple[int, ...]


def output_origins(state) -> dict[Clause, frozenset[str]]:
    origins: dict[Clause, set[str]] = defaultdict(set)
    for clause in state["key"]:
        origins[tuple(clause)].add("ENTRY_KEY")
    for event in state.get("resolution_events", ()):
        origins[tuple(event["resolvent"])].add("LOCAL_RESOLVENT")
    assert set(state["resolution_output"]) == set(origins)
    return {
        clause: frozenset(labels)
        for clause, labels in origins.items()
    }


def events_by_resolvent(state) -> dict[Clause, tuple[dict[str, object], ...]]:
    events: dict[Clause, list[dict[str, object]]] = defaultdict(list)
    for event in state.get("resolution_events", ()):
        events[tuple(event["resolvent"])].append(event)
    return {
        clause: tuple(items)
        for clause, items in events.items()
    }


def audit(n: int):
    context = execution_context(n)
    policy = context["policy"]
    pairs = context["pairs"]
    levels = context["levels"]
    target = n - 2

    counts: Counter[str] = Counter()
    local_side_histogram: Counter[int] = Counter()
    origin_patterns: Counter[tuple[tuple[str, ...], tuple[str, ...]]] = Counter()
    role_pairs: Counter[tuple[str, str]] = Counter()
    cut_relation: Counter[str] = Counter()
    event_parent_classes: Counter[tuple[str, str]] = Counter()
    event_literal_roles: Counter[tuple[tuple[str, str], ...]] = Counter()
    event_pivot_relation: Counter[bool] = Counter()
    novelty_histogram: Counter[int] = Counter()
    locally_created_examples = []
    all_examples = []

    for state in policy.states.values():
        state_id = int(state["id"])
        call_id = int(state["entry_call"])
        novelty = int(levels[call_id])
        if novelty > target:
            continue

        assignment = context["call_after_pre"][call_id]
        output = tuple(tuple(clause) for clause in state["resolution_output"])
        origins = output_origins(state)
        event_index = events_by_resolvent(state)
        output_pairs = enumerate_double_bridges(n, output, assignment, pairs)

        for record in output_pairs:
            counts["resolution_output_double_bridge_occurrences"] += 1
            novelty_histogram[novelty] += 1
            pivot = int(record["pivot"])
            left = tuple(record["left"])
            right = tuple(record["right"])
            left_bridge = record["left_bridge"]
            right_bridge = record["right_bridge"]

            roles = tuple(sorted((
                str(left_bridge["role"]),
                str(right_bridge["role"]),
            )))
            role_pairs[roles] += 1
            same_cut = left_bridge["cut"] == right_bridge["cut"]
            cut_relation["SAME_CUT" if same_cut else "DIFFERENT_CUT"] += 1
            if same_cut:
                counts["same_cut"] += 1
            if roles == ("TAIL_SINGLETON", "TAIL_SINGLETON"):
                counts["tail_tail"] += 1
            else:
                counts["non_tail_pair"] += 1

            left_origins = tuple(sorted(origins[left]))
            right_origins = tuple(sorted(origins[right]))
            origin_patterns[(left_origins, right_origins)] += 1
            left_local_required = "ENTRY_KEY" not in origins[left]
            right_local_required = "ENTRY_KEY" not in origins[right]
            local_sides = int(left_local_required) + int(right_local_required)
            local_side_histogram[local_sides] += 1

            if local_sides == 0:
                counts["entry_inherited"] += 1
            elif local_sides == 1:
                counts["one_local_side"] += 1
            else:
                counts["two_local_sides"] += 1

            local_details = []
            for clause, eventual_literal, required in (
                (left, pivot, left_local_required),
                (right, -pivot, right_local_required),
            ):
                if not required:
                    continue
                assert clause in event_index
                signatures = []
                for event in event_index[clause]:
                    signature = event_signature(
                        n,
                        event,
                        eventual_literal,
                        assignment,
                        pairs,
                    )
                    signatures.append(signature)
                    event_parent_classes[signature["parent_classes"]] += 1
                    event_literal_roles[signature["literal_roles"]] += 1
                    event_pivot_relation[
                        bool(signature["event_pivot_equals_eventual"])
                    ] += 1
                local_details.append({
                    "clause": clause,
                    "eventual_literal": eventual_literal,
                    "signatures": tuple(signatures),
                })

            example = {
                "n": n,
                "state_id": state_id,
                "call_id": call_id,
                "novelty": novelty,
                "pivot": pivot,
                "left": left,
                "right": right,
                "roles": roles,
                "same_cut": same_cut,
                "origins": (left_origins, right_origins),
                "local_sides": local_sides,
                "local_details": tuple(local_details),
            }
            if len(all_examples) < 80:
                all_examples.append(example)
            if local_sides and len(locally_created_examples) < 120:
                locally_created_examples.append(example)

    assert counts["resolution_output_double_bridge_occurrences"] > 0
    assert (
        counts["entry_inherited"]
        + counts["one_local_side"]
        + counts["two_local_sides"]
        == counts["resolution_output_double_bridge_occurrences"]
    )

    return {
        "n": n,
        "target": target,
        "counts": tuple(sorted(counts.items())),
        "local_side_histogram": tuple(sorted(local_side_histogram.items())),
        "origin_patterns": tuple(sorted(origin_patterns.items(), key=repr)),
        "role_pairs": tuple(sorted(role_pairs.items(), key=repr)),
        "cut_relation": tuple(sorted(cut_relation.items())),
        "event_parent_classes": tuple(
            sorted(event_parent_classes.items(), key=repr)
        ),
        "event_literal_roles": tuple(
            sorted(event_literal_roles.items(), key=repr)
        ),
        "event_pivot_relation": tuple(sorted(event_pivot_relation.items())),
        "novelty_histogram": tuple(sorted(novelty_histogram.items())),
        "locally_created_examples": tuple(locally_created_examples),
        "all_examples": tuple(all_examples),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_local_sides: Counter[int] = Counter()
    aggregate_origins: Counter[tuple[tuple[str, ...], tuple[str, ...]]] = Counter()
    aggregate_roles: Counter[tuple[str, str]] = Counter()
    aggregate_cuts: Counter[str] = Counter()
    aggregate_parent_classes: Counter[tuple[str, str]] = Counter()
    aggregate_literal_roles: Counter[tuple[tuple[str, str], ...]] = Counter()
    aggregate_pivot_relation: Counter[bool] = Counter()
    aggregate_novelty: Counter[int] = Counter()
    rows = []

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_local_sides.update(dict(data["local_side_histogram"]))
        aggregate_origins.update(dict(data["origin_patterns"]))
        aggregate_roles.update(dict(data["role_pairs"]))
        aggregate_cuts.update(dict(data["cut_relation"]))
        aggregate_parent_classes.update(dict(data["event_parent_classes"]))
        aggregate_literal_roles.update(dict(data["event_literal_roles"]))
        aggregate_pivot_relation.update(dict(data["event_pivot_relation"]))
        aggregate_novelty.update(dict(data["novelty_histogram"]))
        rows.append((
            n,
            data["target"],
            data["counts"],
            data["local_side_histogram"],
            data["role_pairs"],
            data["cut_relation"],
            data["event_parent_classes"],
        ))
        print(f"ORDER_SIZE = {n}")
        print(f"  target = {data['target']}")
        print(f"  counts = {data['counts']}")
        print(f"  local_side_histogram = {data['local_side_histogram']}")
        print(f"  origin_patterns = {data['origin_patterns']}")
        print(f"  role_pairs = {data['role_pairs']}")
        print(f"  cut_relation = {data['cut_relation']}")
        print(f"  event_parent_classes = {data['event_parent_classes']}")
        print(f"  event_literal_roles = {data['event_literal_roles']}")
        print(f"  event_pivot_relation = {data['event_pivot_relation']}")
        print(f"  novelty_histogram = {data['novelty_histogram']}")
        print(f"  locally_created_examples = {data['locally_created_examples']}")
        print(f"  all_examples = {data['all_examples']}")

    assert aggregate_counts["resolution_output_double_bridge_occurrences"] > 0
    print("JANUS_GT_RESOLUTION_OUTPUT_DOUBLE_BRIDGE_CREATION = PASS")
    print(f"ROWS = {tuple(rows)}")
    print(f"AGGREGATE_COUNTS = {tuple(sorted(aggregate_counts.items()))}")
    print(f"AGGREGATE_LOCAL_SIDE_HISTOGRAM = {tuple(sorted(aggregate_local_sides.items()))}")
    print(f"AGGREGATE_ORIGIN_PATTERNS = {tuple(sorted(aggregate_origins.items(), key=repr))}")
    print(f"AGGREGATE_ROLE_PAIRS = {tuple(sorted(aggregate_roles.items(), key=repr))}")
    print(f"AGGREGATE_CUT_RELATION = {tuple(sorted(aggregate_cuts.items()))}")
    print(f"AGGREGATE_EVENT_PARENT_CLASSES = {tuple(sorted(aggregate_parent_classes.items(), key=repr))}")
    print(f"AGGREGATE_EVENT_LITERAL_ROLES = {tuple(sorted(aggregate_literal_roles.items(), key=repr))}")
    print(f"AGGREGATE_EVENT_PIVOT_RELATION = {tuple(sorted(aggregate_pivot_relation.items()))}")
    print(f"AGGREGATE_NOVELTY = {tuple(sorted(aggregate_novelty.items()))}")
    print(
        "claim_boundary = finite raw Resolution-output census through GT_8; "
        "no arbitrary-n local preservation theorem claimed"
    )


if __name__ == "__main__":
    self_test()
