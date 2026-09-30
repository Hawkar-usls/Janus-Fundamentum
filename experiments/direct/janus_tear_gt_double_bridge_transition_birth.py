#!/usr/bin/env python3
"""Classify the transition at which each GT double-bridge pair becomes eligible.

Static root-owner ancestry is not an invariant: local Resolution can replace the
expected non-minimality owner while the complementary bridge pair remains
safe.  The next candidate invariant is temporal.

For every pre-frontier exact-key double-bridge occurrence through GT_8 this
audit reconstructs the immediately preceding parent post-result and asks:

- did a complementary double-bridge source pair already exist after the parent
  local pass and post-units;
- or did the branch plus child pre-units create one or both bridge statuses;
- were the source clauses inherited key clauses or fresh local resolvents;
- was the transition novel;
- did the branch touch either of the two quotient vertices isolated by the
  child tail/tail bridges.

The program is a finite discovery certificate.  It asserts only exact replay,
the independently certified tail/tail different-cut property, and accounting
completeness; it does not assume a transition pattern in advance.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Iterable

from janus_tear_gt_bridge_endpoint_profile import bridge_record
from janus_tear_gt_component_merge_sources import reduce_clause
from janus_tear_gt_component_tree_clause_audit import (
    clause_component_graph,
    execution_context,
)
from janus_tear_gt_rank_safety_dichotomy import safety_class

Clause = tuple[int, ...]


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


def reduce_sources(
    clauses: Iterable[Clause], assignments: dict[int, bool]
) -> dict[Clause, tuple[Clause, ...]]:
    sources: dict[Clause, list[Clause]] = defaultdict(list)
    for clause in clauses:
        residual = reduce_clause(tuple(clause), assignments)
        if residual is None:
            continue
        sources[tuple(residual)].append(tuple(clause))
    return {
        residual: tuple(source_list)
        for residual, source_list in sources.items()
    }


def parent_post_source_kinds(state) -> dict[Clause, frozenset[str]]:
    post_result = state.get("post_result")
    if post_result is None:
        return {}
    post_assignments = unit_assignments(state.get("post_units", ()))
    kinds: dict[Clause, set[str]] = defaultdict(set)

    for clause in state["key"]:
        residual = reduce_clause(tuple(clause), post_assignments)
        if residual is not None:
            kinds[tuple(residual)].add("ENTRY_KEY")

    for event in state.get("resolution_events", ()):
        clause = tuple(event["resolvent"])
        residual = reduce_clause(clause, post_assignments)
        if residual is not None:
            kinds[tuple(residual)].add("LOCAL_RESOLVENT")

    assert set(post_result) == set(kinds)
    return {clause: frozenset(labels) for clause, labels in kinds.items()}


def enumerate_double_bridges(n: int, key, assignment, pairs):
    classes = {
        clause: str(safety_class(n, clause, assignment, pairs)["classification"])
        for clause in key
    }
    graph_cache = {
        clause: clause_component_graph(n, clause, assignment, pairs)
        for clause in key
        if classes[clause] == "COMPONENT_SPANNING"
    }
    positive: dict[int, list[Clause]] = defaultdict(list)
    negative: dict[int, list[Clause]] = defaultdict(list)
    for clause in key:
        if classes[clause] != "COMPONENT_SPANNING":
            continue
        for literal in clause:
            (positive if literal > 0 else negative)[abs(literal)].append(clause)

    bridge_cache: dict[tuple[Clause, int], dict[str, object] | None] = {}
    records = []
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
                records.append({
                    "pivot": pivot,
                    "left": left,
                    "right": right,
                    "left_bridge": left_bridge,
                    "right_bridge": right_bridge,
                    "left_graph": graph_cache[left],
                    "right_graph": graph_cache[right],
                })
    return tuple(records)


def source_bridge_status(n, clause, literal, assignment, pairs):
    structure = safety_class(n, clause, assignment, pairs)
    classification = str(structure["classification"])
    if classification != "COMPONENT_SPANNING":
        return classification, None
    graph = clause_component_graph(n, clause, assignment, pairs)
    bridge = bridge_record(clause, graph, pairs, literal)
    return classification, bridge


def audit(n: int):
    context = execution_context(n)
    policy = context["policy"]
    pairs = context["pairs"]
    levels = context["levels"]
    target = n - 2

    parent_transition: dict[int, dict[str, object]] = {}
    for parent_state in policy.states.values():
        if parent_state["terminal"] not in ("BRANCH_UNSAT", "BRANCH_SAT"):
            continue
        parent_call = int(parent_state["entry_call"])
        for child in parent_state.get("children", ()):
            if child.get("call") is None:
                continue
            child_call = int(child["call"])
            assert child_call not in parent_transition
            parent_transition[child_call] = {
                "parent_state": int(parent_state["id"]),
                "parent_call": parent_call,
                "branch_literal": int(child["literal"]),
            }
            if child["result"]:
                break

    counts: Counter[str] = Counter()
    birth_modes: Counter[str] = Counter()
    source_status_patterns: Counter[tuple[str, str]] = Counter()
    source_kind_patterns: Counter[tuple[tuple[str, ...], tuple[str, ...]]] = Counter()
    novelty_increment: Counter[int] = Counter()
    branch_touch_pattern: Counter[str] = Counter()
    pre_unit_histogram: Counter[int] = Counter()
    source_multiplicity: Counter[tuple[int, int]] = Counter()
    examples = []

    for state in policy.states.values():
        state_id = int(state["id"])
        call_id = int(state["entry_call"])
        novelty = int(levels[call_id])
        if novelty > target:
            continue
        assignment = context["call_after_pre"][call_id]
        key = tuple(state["key"])
        pairs_here = enumerate_double_bridges(n, key, assignment, pairs)

        for record in pairs_here:
            counts["double_bridge_occurrences"] += 1
            pivot = int(record["pivot"])
            left = tuple(record["left"])
            right = tuple(record["right"])
            left_bridge = record["left_bridge"]
            right_bridge = record["right_bridge"]
            assert left_bridge["role"] == right_bridge["role"] == "TAIL_SINGLETON"
            assert left_bridge["cut"] != right_bridge["cut"]

            if call_id == int(context["root_call"]):
                counts["root_occurrences"] += 1
                birth_modes["ROOT_AXIOM_PAIR"] += 1
                continue

            transition = parent_transition[call_id]
            parent_state_id = int(transition["parent_state"])
            parent_call = int(transition["parent_call"])
            branch_literal = int(transition["branch_literal"])
            parent_state = policy.states[parent_state_id]
            parent_post = tuple(parent_state["post_result"])
            parent_assignment = context["state_after_post"][parent_state_id]

            transition_assignments = {
                abs(branch_literal): branch_literal > 0
            }
            child_call = policy.calls[call_id]
            child_pre = unit_assignments(child_call.get("pre_units", ()))
            for variable, value in child_pre.items():
                assert (
                    variable not in transition_assignments
                    or transition_assignments[variable] == value
                )
                transition_assignments[variable] = value
            pre_unit_histogram[len(child_pre)] += 1

            source_map = reduce_sources(parent_post, transition_assignments)
            assert left in source_map and right in source_map
            left_sources = source_map[left]
            right_sources = source_map[right]
            source_multiplicity[(len(left_sources), len(right_sources))] += 1
            post_kinds = parent_post_source_kinds(parent_state)

            inherited_double_bridge = False
            best_status = None
            best_source_pair = None
            best_rank = -1

            for left_source in left_sources:
                left_class, left_parent_bridge = source_bridge_status(
                    n, left_source, pivot, parent_assignment, pairs
                )
                for right_source in right_sources:
                    right_class, right_parent_bridge = source_bridge_status(
                        n, right_source, -pivot, parent_assignment, pairs
                    )
                    left_status = (
                        "BRIDGE"
                        if left_parent_bridge is not None
                        else "SPANNING_NONBRIDGE"
                        if left_class == "COMPONENT_SPANNING"
                        else left_class
                    )
                    right_status = (
                        "BRIDGE"
                        if right_parent_bridge is not None
                        else "SPANNING_NONBRIDGE"
                        if right_class == "COMPONENT_SPANNING"
                        else right_class
                    )
                    source_status_patterns[(left_status, right_status)] += 1
                    rank = int(left_parent_bridge is not None) + int(
                        right_parent_bridge is not None
                    )
                    if rank > best_rank:
                        best_rank = rank
                        best_status = (left_status, right_status)
                        best_source_pair = (left_source, right_source)
                    if left_parent_bridge is not None and right_parent_bridge is not None:
                        inherited_double_bridge = True

            assert best_status is not None and best_source_pair is not None
            if inherited_double_bridge:
                mode = "INHERITED_DOUBLE_BRIDGE"
                counts["inherited_occurrences"] += 1
            elif best_rank == 1:
                mode = "ONE_BRIDGE_CREATED_BY_TRANSITION"
                counts["one_created_occurrences"] += 1
            else:
                mode = "TWO_BRIDGES_CREATED_BY_TRANSITION"
                counts["two_created_occurrences"] += 1
            birth_modes[mode] += 1

            left_source, right_source = best_source_pair
            left_kinds = tuple(sorted(post_kinds[left_source]))
            right_kinds = tuple(sorted(post_kinds[right_source]))
            source_kind_patterns[(left_kinds, right_kinds)] += 1
            if "LOCAL_RESOLVENT" in left_kinds or "LOCAL_RESOLVENT" in right_kinds:
                counts["transition_with_local_source"] += 1
            if left_kinds == right_kinds == ("ENTRY_KEY",):
                counts["entry_only_sources"] += 1

            increment = novelty - int(levels[parent_call])
            assert increment in (0, 1)
            novelty_increment[increment] += 1

            branch_variable = abs(branch_literal)
            branch_vertices = set(pairs[branch_variable])
            left_graph = record["left_graph"]
            right_graph = record["right_graph"]
            left_tail_vertices = set(
                left_graph["parts"][int(left_bridge["tail"])]
            )
            right_tail_vertices = set(
                right_graph["parts"][int(right_bridge["tail"])]
            )
            touches_left = bool(branch_vertices & left_tail_vertices)
            touches_right = bool(branch_vertices & right_tail_vertices)
            if touches_left and touches_right:
                touch = "TOUCHES_BOTH_TAIL_COMPONENTS"
            elif touches_left:
                touch = "TOUCHES_LEFT_TAIL_COMPONENT"
            elif touches_right:
                touch = "TOUCHES_RIGHT_TAIL_COMPONENT"
            else:
                touch = "TOUCHES_NEITHER_TAIL_COMPONENT"
            branch_touch_pattern[touch] += 1

            if len(examples) < 120:
                examples.append({
                    "n": n,
                    "state_id": state_id,
                    "call_id": call_id,
                    "novelty": novelty,
                    "parent_state_id": parent_state_id,
                    "parent_call": parent_call,
                    "parent_novelty": int(levels[parent_call]),
                    "branch_literal": branch_literal,
                    "branch_vertices": tuple(sorted(branch_vertices)),
                    "child_pre_units": tuple(sorted(child_pre.items())),
                    "pivot": pivot,
                    "left": left,
                    "right": right,
                    "mode": mode,
                    "best_parent_status": best_status,
                    "best_parent_sources": best_source_pair,
                    "source_kinds": (left_kinds, right_kinds),
                    "left_tail_vertices": tuple(sorted(left_tail_vertices)),
                    "right_tail_vertices": tuple(sorted(right_tail_vertices)),
                    "branch_touch": touch,
                    "novelty_increment": increment,
                })

    assert counts["double_bridge_occurrences"] > 0
    assert (
        counts["root_occurrences"]
        + counts["inherited_occurrences"]
        + counts["one_created_occurrences"]
        + counts["two_created_occurrences"]
        == counts["double_bridge_occurrences"]
    )

    return {
        "n": n,
        "target": target,
        "counts": tuple(sorted(counts.items())),
        "birth_modes": tuple(sorted(birth_modes.items())),
        "source_status_patterns": tuple(
            sorted(source_status_patterns.items(), key=repr)
        ),
        "source_kind_patterns": tuple(
            sorted(source_kind_patterns.items(), key=repr)
        ),
        "novelty_increment": tuple(sorted(novelty_increment.items())),
        "branch_touch_pattern": tuple(sorted(branch_touch_pattern.items())),
        "pre_unit_histogram": tuple(sorted(pre_unit_histogram.items())),
        "source_multiplicity": tuple(sorted(source_multiplicity.items())),
        "examples": tuple(examples),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_modes: Counter[str] = Counter()
    aggregate_status: Counter[tuple[str, str]] = Counter()
    aggregate_kinds: Counter[tuple[tuple[str, ...], tuple[str, ...]]] = Counter()
    aggregate_novelty: Counter[int] = Counter()
    aggregate_touch: Counter[str] = Counter()
    aggregate_pre_units: Counter[int] = Counter()
    aggregate_multiplicity: Counter[tuple[int, int]] = Counter()
    rows = []

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_modes.update(dict(data["birth_modes"]))
        aggregate_status.update(dict(data["source_status_patterns"]))
        aggregate_kinds.update(dict(data["source_kind_patterns"]))
        aggregate_novelty.update(dict(data["novelty_increment"]))
        aggregate_touch.update(dict(data["branch_touch_pattern"]))
        aggregate_pre_units.update(dict(data["pre_unit_histogram"]))
        aggregate_multiplicity.update(dict(data["source_multiplicity"]))
        rows.append((
            n,
            data["target"],
            data["counts"],
            data["birth_modes"],
            data["novelty_increment"],
            data["branch_touch_pattern"],
            data["pre_unit_histogram"],
        ))
        print(f"ORDER_SIZE = {n}")
        print(f"  target = {data['target']}")
        print(f"  counts = {data['counts']}")
        print(f"  birth_modes = {data['birth_modes']}")
        print(f"  source_status_patterns = {data['source_status_patterns']}")
        print(f"  source_kind_patterns = {data['source_kind_patterns']}")
        print(f"  novelty_increment = {data['novelty_increment']}")
        print(f"  branch_touch_pattern = {data['branch_touch_pattern']}")
        print(f"  pre_unit_histogram = {data['pre_unit_histogram']}")
        print(f"  source_multiplicity = {data['source_multiplicity']}")
        print(f"  examples = {data['examples']}")

    assert aggregate_counts["double_bridge_occurrences"] == 611
    assert aggregate_counts["root_occurrences"] == 80
    print("JANUS_GT_DOUBLE_BRIDGE_TRANSITION_BIRTH = PASS")
    print(f"ROWS = {tuple(rows)}")
    print(f"AGGREGATE_COUNTS = {tuple(sorted(aggregate_counts.items()))}")
    print(f"AGGREGATE_BIRTH_MODES = {tuple(sorted(aggregate_modes.items()))}")
    print(f"AGGREGATE_SOURCE_STATUS = {tuple(sorted(aggregate_status.items(), key=repr))}")
    print(f"AGGREGATE_SOURCE_KINDS = {tuple(sorted(aggregate_kinds.items(), key=repr))}")
    print(f"AGGREGATE_NOVELTY_INCREMENT = {tuple(sorted(aggregate_novelty.items()))}")
    print(f"AGGREGATE_BRANCH_TOUCH = {tuple(sorted(aggregate_touch.items()))}")
    print(f"AGGREGATE_PRE_UNITS = {tuple(sorted(aggregate_pre_units.items()))}")
    print(f"AGGREGATE_SOURCE_MULTIPLICITY = {tuple(sorted(aggregate_multiplicity.items()))}")
    print(
        "claim_boundary = finite immediate-parent transition census through GT_8; "
        "no arbitrary-n preservation theorem claimed"
    )


if __name__ == "__main__":
    self_test()
