#!/usr/bin/env python3
"""Replay root-axiom provenance of every pre-frontier double-bridge pair.

The finite co-resolvable certificate proves that every complementary
component-spanning double-bridge pair through GT_8 is tail/tail and has different
cuts.  This audit asks for the stronger inductive explanation.

It propagates exact root-clause provenance through the complete Policy-0A trace:

    root clause
      -> pre-unit reduction
      -> frozen one-pass Resolution
      -> post-unit reduction
      -> branch restriction
      -> child pre-units
      -> next exact key.

For each double-bridge occurrence it records which root non-minimality clauses
N_v and which root transitivity clauses occur in each parent's ancestry, and
compares the non-minimality owners with the directed head of the pivot literal.

No owner pattern is asserted a priori.  The only hard assertions are replay
completeness and the already independently certified tail/tail different-cut
property.  The output is a discovery certificate for the arbitrary-n induction.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Iterable

from janus_tear_gt_bridge_endpoint_profile import bridge_record
from janus_tear_gt_component_merge_sources import reduce_clause
from janus_tear_gt_component_tree_clause_audit import execution_context
from janus_tear_gt_rank_safety_dichotomy import safety_class
from janus_tear_gt_unit_merge_root_ancestry import non_minimality_clauses

Clause = tuple[int, ...]
RootSource = tuple[str, int | None, Clause]
Provenance = dict[Clause, frozenset[RootSource]]


def unit_assignments(events: Iterable[dict[str, object]]) -> dict[int, bool]:
    assignments: dict[int, bool] = {}
    for event in events:
        if event["kind"] != "unit":
            continue
        literal = int(event["literal"])
        variable = abs(literal)
        value = literal > 0
        assert variable not in assignments or assignments[variable] == value
        assignments[variable] = value
    return assignments


def reduce_provenance(
    clauses: Iterable[Clause],
    provenance: Provenance,
    assignments: dict[int, bool],
) -> Provenance:
    reduced: dict[Clause, set[RootSource]] = defaultdict(set)
    for clause in clauses:
        residual = reduce_clause(tuple(clause), assignments)
        if residual is None:
            continue
        reduced[tuple(residual)].update(provenance[tuple(clause)])
    return {
        clause: frozenset(sources)
        for clause, sources in reduced.items()
    }


def minimum_owner_labels(n: int, pairs, root: tuple[Clause, ...]) -> dict[Clause, int]:
    minimum = set(non_minimality_clauses(n, pairs))
    labels: dict[Clause, int] = {}
    for clause in root:
        if clause not in minimum:
            continue
        candidates = [
            vertex
            for vertex in range(n)
            if all(vertex in pairs[abs(literal)] for literal in clause)
        ]
        assert len(candidates) == 1
        labels[clause] = candidates[0]
    assert len(labels) == n
    return labels


def replay_provenance(n: int):
    context = execution_context(n)
    root = tuple(context["root"])
    policy = context["policy"]
    root_call = int(context["root_call"])
    minimum_labels = minimum_owner_labels(n, context["pairs"], root)

    root_provenance: Provenance = {}
    for clause in root:
        if clause in minimum_labels:
            source: RootSource = ("N", minimum_labels[clause], clause)
        else:
            source = ("T", None, clause)
        root_provenance[clause] = frozenset({source})

    state_key_provenance: dict[int, Provenance] = {}
    state_output_provenance: dict[int, Provenance] = {}
    state_post_provenance: dict[int, Provenance] = {}
    seen_calls: set[int] = set()

    def walk(call_id: int, input_cnf: tuple[Clause, ...], input_provenance: Provenance) -> None:
        assert call_id not in seen_calls
        seen_calls.add(call_id)
        call = policy.calls[call_id]
        assert tuple(call["input"]) == tuple(input_cnf)
        assert set(input_cnf) == set(input_provenance)

        pre_assignments = unit_assignments(call.get("pre_units", ()))
        pre_provenance = reduce_provenance(input_cnf, input_provenance, pre_assignments)
        pre_result = call.get("pre_result")
        if pre_result is None:
            return
        assert set(pre_result) == set(pre_provenance)

        if call["terminal"] != "STATE":
            return

        state_id = int(call["state"])
        state = policy.states[state_id]
        key = tuple(state["key"])
        assert set(key) == set(pre_provenance)
        state_key_provenance[state_id] = pre_provenance

        output_sources: dict[Clause, set[RootSource]] = defaultdict(set)
        for clause in key:
            output_sources[clause].update(pre_provenance[clause])

        for event in state.get("resolution_events", ()):
            left = tuple(event["left"])
            right = tuple(event["right"])
            resolvent = tuple(event["resolvent"])
            assert left in pre_provenance and right in pre_provenance
            output_sources[resolvent].update(pre_provenance[left])
            output_sources[resolvent].update(pre_provenance[right])

        output_provenance: Provenance = {
            clause: frozenset(sources)
            for clause, sources in output_sources.items()
        }
        resolution_output = tuple(state["resolution_output"])
        assert set(resolution_output) == set(output_provenance)
        state_output_provenance[state_id] = output_provenance

        post_result = state.get("post_result")
        if post_result is None:
            return
        post_assignments = unit_assignments(state.get("post_units", ()))
        post_provenance = reduce_provenance(
            resolution_output,
            output_provenance,
            post_assignments,
        )
        assert set(post_result) == set(post_provenance)
        state_post_provenance[state_id] = post_provenance

        if state["terminal"] not in ("BRANCH_UNSAT", "BRANCH_SAT"):
            return

        variable = int(state["branch_var"])
        for child in state.get("children", ()):
            child_call = child.get("call")
            if child_call is None:
                continue
            value = bool(child["value"])
            branch_assignment = {variable: value}
            child_input_provenance = reduce_provenance(
                tuple(post_result),
                post_provenance,
                branch_assignment,
            )
            child_input = tuple(policy.calls[int(child_call)]["input"])
            assert set(child_input) == set(child_input_provenance)
            walk(int(child_call), child_input, child_input_provenance)
            if child["result"]:
                break

    walk(root_call, root, root_provenance)
    assert len(seen_calls) == len(policy.calls)
    assert len(state_key_provenance) == len(policy.states)
    return context, minimum_labels, state_key_provenance


def owner_signature(sources: frozenset[RootSource]) -> tuple[tuple[int, ...], bool, int]:
    owners = tuple(sorted({int(owner) for kind, owner, _ in sources if kind == "N"}))
    has_transitivity = any(kind == "T" for kind, _owner, _clause in sources)
    return owners, has_transitivity, len(sources)


def audit(n: int):
    context, _minimum_labels, provenance = replay_provenance(n)
    policy = context["policy"]
    pairs = context["pairs"]
    levels = context["levels"]
    target = n - 2

    counts: Counter[str] = Counter()
    source_shapes: Counter[tuple[tuple[int, ...], bool, tuple[int, ...], bool]] = Counter()
    expected_owner_patterns: Counter[tuple[str, str]] = Counter()
    source_cardinality: Counter[tuple[int, int]] = Counter()
    novelty_histogram: Counter[int] = Counter()
    examples = []

    for state in policy.states.values():
        state_id = int(state["id"])
        call_id = int(state["entry_call"])
        novelty = int(levels[call_id])
        if novelty > target:
            continue
        assignment = context["call_after_pre"][call_id]
        key = tuple(state["key"])
        key_provenance = provenance[state_id]

        graphs = {
            clause: context_graph
            for clause in ()
            for context_graph in ()
        }
        # Build lazily because only component-spanning clauses are relevant.
        classes = {
            clause: str(safety_class(n, clause, assignment, pairs)["classification"])
            for clause in key
        }
        bridge_cache: dict[tuple[Clause, int], dict[str, object] | None] = {}

        positive: dict[int, list[Clause]] = defaultdict(list)
        negative: dict[int, list[Clause]] = defaultdict(list)
        for clause in key:
            if classes[clause] != "COMPONENT_SPANNING":
                continue
            for literal in clause:
                (positive if literal > 0 else negative)[abs(literal)].append(clause)

        from janus_tear_gt_component_tree_clause_audit import clause_component_graph

        graph_cache = {
            clause: clause_component_graph(n, clause, assignment, pairs)
            for clause in key
            if classes[clause] == "COMPONENT_SPANNING"
        }

        for pivot in sorted(set(positive) & set(negative)):
            for left in positive[pivot]:
                left_key = (left, pivot)
                if left_key not in bridge_cache:
                    bridge_cache[left_key] = bridge_record(
                        left, graph_cache[left], pairs, pivot
                    )
                left_bridge = bridge_cache[left_key]
                if left_bridge is None:
                    continue

                for right in negative[pivot]:
                    right_key = (right, -pivot)
                    if right_key not in bridge_cache:
                        bridge_cache[right_key] = bridge_record(
                            right, graph_cache[right], pairs, -pivot
                        )
                    right_bridge = bridge_cache[right_key]
                    if right_bridge is None:
                        continue

                    counts["double_bridge_occurrences"] += 1
                    novelty_histogram[novelty] += 1
                    left_role = str(left_bridge["role"])
                    right_role = str(right_bridge["role"])
                    if left_role == right_role == "TAIL_SINGLETON":
                        counts["tail_tail"] += 1
                    else:
                        counts["non_tail_tail_pair"] += 1
                    same_cut = left_bridge["cut"] == right_bridge["cut"]
                    counts["same_cut" if same_cut else "different_cut"] += 1

                    left_sources = key_provenance[left]
                    right_sources = key_provenance[right]
                    left_owners, left_has_t, left_size = owner_signature(left_sources)
                    right_owners, right_has_t, right_size = owner_signature(right_sources)
                    source_shapes[(
                        left_owners,
                        left_has_t,
                        right_owners,
                        right_has_t,
                    )] += 1
                    source_cardinality[(left_size, right_size)] += 1

                    low, high = pairs[pivot]
                    left_expected = high   # positive literal low -> high
                    right_expected = low   # negative literal high -> low
                    left_pattern = (
                        "EXPECTED_ONLY"
                        if left_owners == (left_expected,)
                        else "EXPECTED_PRESENT"
                        if left_expected in left_owners
                        else "EXPECTED_ABSENT"
                    )
                    right_pattern = (
                        "EXPECTED_ONLY"
                        if right_owners == (right_expected,)
                        else "EXPECTED_PRESENT"
                        if right_expected in right_owners
                        else "EXPECTED_ABSENT"
                    )
                    expected_owner_patterns[(left_pattern, right_pattern)] += 1
                    if left_expected in left_owners:
                        counts["left_expected_owner_present"] += 1
                    if right_expected in right_owners:
                        counts["right_expected_owner_present"] += 1
                    if (
                        left_expected in left_owners
                        and right_expected in right_owners
                    ):
                        counts["both_expected_owners_present"] += 1
                    if not left_owners:
                        counts["left_no_nonminimality_owner"] += 1
                    if not right_owners:
                        counts["right_no_nonminimality_owner"] += 1

                    if len(examples) < 80:
                        examples.append({
                            "n": n,
                            "state_id": state_id,
                            "call_id": call_id,
                            "novelty": novelty,
                            "pivot": pivot,
                            "pivot_endpoints": (low, high),
                            "left": left,
                            "right": right,
                            "left_bridge": left_bridge,
                            "right_bridge": right_bridge,
                            "same_cut": same_cut,
                            "left_owner_signature": (
                                left_owners, left_has_t, left_size
                            ),
                            "right_owner_signature": (
                                right_owners, right_has_t, right_size
                            ),
                            "expected_owner_pattern": (
                                left_pattern, right_pattern
                            ),
                        })

    assert counts["double_bridge_occurrences"] > 0
    assert counts["non_tail_tail_pair"] == 0
    assert counts["same_cut"] == 0
    assert counts["double_bridge_occurrences"] == counts["tail_tail"]
    assert counts["double_bridge_occurrences"] == counts["different_cut"]

    return {
        "n": n,
        "target": target,
        "counts": tuple(sorted(counts.items())),
        "source_shapes": tuple(sorted(source_shapes.items(), key=repr)),
        "expected_owner_patterns": tuple(
            sorted(expected_owner_patterns.items(), key=repr)
        ),
        "source_cardinality": tuple(sorted(source_cardinality.items())),
        "novelty_histogram": tuple(sorted(novelty_histogram.items())),
        "examples": tuple(examples),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_shapes: Counter[tuple[tuple[int, ...], bool, tuple[int, ...], bool]] = Counter()
    aggregate_patterns: Counter[tuple[str, str]] = Counter()
    aggregate_cardinality: Counter[tuple[int, int]] = Counter()
    aggregate_novelty: Counter[int] = Counter()
    rows = []

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_shapes.update(dict(data["source_shapes"]))
        aggregate_patterns.update(dict(data["expected_owner_patterns"]))
        aggregate_cardinality.update(dict(data["source_cardinality"]))
        aggregate_novelty.update(dict(data["novelty_histogram"]))
        rows.append((
            n,
            data["target"],
            data["counts"],
            data["expected_owner_patterns"],
            data["source_cardinality"],
            data["novelty_histogram"],
        ))
        print(f"ORDER_SIZE = {n}")
        print(f"  target = {data['target']}")
        print(f"  counts = {data['counts']}")
        print(f"  expected_owner_patterns = {data['expected_owner_patterns']}")
        print(f"  source_cardinality = {data['source_cardinality']}")
        print(f"  novelty_histogram = {data['novelty_histogram']}")
        print(f"  source_shapes = {data['source_shapes']}")
        print(f"  examples = {data['examples']}")

    assert aggregate_counts["double_bridge_occurrences"] == 611
    print("JANUS_GT_DOUBLE_BRIDGE_ROOT_OWNER_PROVENANCE = PASS")
    print(f"ROWS = {tuple(rows)}")
    print(f"AGGREGATE_COUNTS = {tuple(sorted(aggregate_counts.items()))}")
    print(f"AGGREGATE_EXPECTED_OWNER_PATTERNS = {tuple(sorted(aggregate_patterns.items(), key=repr))}")
    print(f"AGGREGATE_SOURCE_CARDINALITY = {tuple(sorted(aggregate_cardinality.items()))}")
    print(f"AGGREGATE_NOVELTY = {tuple(sorted(aggregate_novelty.items()))}")
    print(f"AGGREGATE_SOURCE_SHAPES = {tuple(sorted(aggregate_shapes.items(), key=repr))}")
    print(
        "claim_boundary = exact finite root-provenance replay through GT_8; "
        "owner pattern discovery is not an arbitrary-n induction"
    )


if __name__ == "__main__":
    self_test()
