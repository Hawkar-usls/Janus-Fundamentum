#!/usr/bin/env python3
"""Replay the complete root ancestry of every non-root tail-wing parent.

The finite C024 handoff census finds three non-root unshielded P-occurrences,
all in one GT_8 state.  Their immediate producer is a frozen Resolution between
one root transitivity triangle and one inherited component-spanning
in-arborescence.  This checker follows that in-arborescence all the way back
through

    pre-unit reduction
    parent branch restriction
    parent post-unit reduction
    frozen local Resolution

to its root axioms.  It then checks the exact finite template suggested by the
trace:

1. the inherited parent is created at the root by one N/T Resolution;
2. the N-parent is a non-minimality star N_c;
3. the root resolvent differs from N_c by redirecting exactly one star edge
   child->c to child->middle while middle->c remains;
4. every later step before the non-root producer is only restriction of star
   leaves, never another Resolution of the lineage;
5. the non-root producer resolves the surviving middle->c edge with a root
   transitivity triangle and creates a bad edge whose tail wing is exactly
   {child,middle};
6. the selected branch variable is the redirected child->middle edge.

This is a proof-carrying finite ancestry certificate through GT_8.  The final
one-subdivision reachability statement for arbitrary n remains open.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from functools import lru_cache

from janus_tear_gt_component_merge_sources import reduce_clause
from janus_tear_gt_component_tree_clause_audit import execution_context
from janus_tear_gt_directed_component_clause_audit import orientation_class
from janus_tear_gt_nonroot_wing_provenance import audit as provenance_audit
from janus_tear_gt_rank_safety_dichotomy import safety_class
from janus_tear_gt_root_nonminimality_bridge_shield import original_direction
from janus_tear_gt_same_cut_parent_ancestry import (
    direct_root_labels,
    root_minimum_labels,
)

Clause = tuple[int, ...]


def unit_assignments(events) -> dict[int, bool]:
    result: dict[int, bool] = {}
    for event in events:
        if event["kind"] != "unit":
            continue
        literal = int(event["literal"])
        variable = abs(literal)
        value = literal > 0
        assert variable not in result or result[variable] == value
        result[variable] = value
    return result


def clause_edges(clause: Clause, pairs) -> frozenset[tuple[int, int]]:
    return frozenset(
        original_direction(int(literal), pairs)
        for literal in clause
    )


def build_parent_links(policy, root_call: int):
    links: dict[int, dict[str, object]] = {}
    seen: set[int] = set()

    def walk(call_id: int) -> None:
        assert call_id not in seen
        seen.add(call_id)
        call = policy.calls[call_id]
        if call["terminal"] != "STATE":
            return
        state = policy.states[int(call["state"])]
        if state["terminal"] not in ("BRANCH_UNSAT", "BRANCH_SAT"):
            return
        variable = int(state["branch_var"])
        for child in state["children"]:
            if child["call"] is None:
                continue
            child_call = int(child["call"])
            value = bool(child["value"])
            assert child_call not in links
            links[child_call] = {
                "parent_call": call_id,
                "parent_state": int(state["id"]),
                "branch_variable": variable,
                "branch_value": value,
                "branch_literal": variable if value else -variable,
            }
            walk(child_call)
            if child["result"]:
                break

    walk(root_call)
    assert len(seen) == len(policy.calls)
    return links


def audit(n: int):
    context = execution_context(n)
    policy = context["policy"]
    pairs = context["pairs"]
    root = tuple(context["root"])
    root_call = int(context["root_call"])
    minimum_labels = root_minimum_labels(n, pairs)
    parent_links = build_parent_links(policy, root_call)
    wing_data = provenance_audit(n)

    def local_events(state):
        grouped: dict[Clause, list[dict[str, object]]] = defaultdict(list)
        for index, event in enumerate(state.get("resolution_events", [])):
            payload = {
                "state_id": int(state["id"]),
                "event_index": index,
                "attempt": int(event["attempt"]),
                "pivot": int(event["pivot"]),
                "left": tuple(event["left"]),
                "right": tuple(event["right"]),
                "resolvent": tuple(event["resolvent"]),
            }
            grouped[payload["resolvent"]].append(payload)
        return {clause: tuple(items) for clause, items in grouped.items()}

    @lru_cache(maxsize=None)
    def proof_paths(call_id: int, key_clause: Clause):
        """Return exact root proof paths for one clause in a reached key."""
        call = policy.calls[call_id]
        assert call["terminal"] == "STATE"
        state = policy.states[int(call["state"])]
        assert key_clause in tuple(state["key"])

        pre_assignment = unit_assignments(call.get("pre_units", []))
        input_sources = tuple(
            clause
            for clause in tuple(call["input"])
            if reduce_clause(clause, pre_assignment) == key_clause
        )
        assert input_sources
        results = []

        for input_clause in input_sources:
            pre_step = {
                "kind": "PRE_UNIT_REDUCTION",
                "call_id": call_id,
                "from": input_clause,
                "to": key_clause,
                "assignment": tuple(sorted(pre_assignment.items())),
            }
            if call_id == root_call:
                assert input_clause in root
                labels = direct_root_labels(
                    root, input_clause, {}, minimum_labels
                )
                results.append({
                    "kind": "ROOT",
                    "clause": input_clause,
                    "labels": labels,
                    "local_resolution_count": 0,
                    "steps": (pre_step,),
                    "children": (),
                })
                continue

            link = parent_links[call_id]
            parent_call = int(link["parent_call"])
            parent_state = policy.states[int(link["parent_state"])]
            branch_assignment = {
                int(link["branch_variable"]): bool(link["branch_value"])
            }
            post_sources = tuple(
                clause
                for clause in tuple(parent_state["post_result"])
                if reduce_clause(clause, branch_assignment) == input_clause
            )
            assert post_sources
            post_assignment = unit_assignments(parent_state.get("post_units", []))
            output = tuple(parent_state["resolution_output"])
            event_map = local_events(parent_state)
            parent_key = tuple(parent_state["key"])

            for post_clause in post_sources:
                branch_step = {
                    "kind": "BRANCH_REDUCTION",
                    "parent_call": parent_call,
                    "parent_state": int(parent_state["id"]),
                    "branch_literal": int(link["branch_literal"]),
                    "from": post_clause,
                    "to": input_clause,
                }
                output_sources = tuple(
                    clause
                    for clause in output
                    if reduce_clause(clause, post_assignment) == post_clause
                )
                assert output_sources
                for output_clause in output_sources:
                    post_step = {
                        "kind": "POST_UNIT_REDUCTION",
                        "parent_call": parent_call,
                        "parent_state": int(parent_state["id"]),
                        "from": output_clause,
                        "to": post_clause,
                        "assignment": tuple(sorted(post_assignment.items())),
                    }

                    if output_clause in parent_key:
                        for ancestor in proof_paths(parent_call, output_clause):
                            results.append({
                                **ancestor,
                                "steps": tuple(ancestor["steps"])
                                + (post_step, branch_step, pre_step),
                            })

                    for event in event_map.get(output_clause, ()):
                        left_paths = proof_paths(parent_call, tuple(event["left"]))
                        right_paths = proof_paths(parent_call, tuple(event["right"]))
                        for left_path in left_paths:
                            for right_path in right_paths:
                                results.append({
                                    "kind": "LOCAL_RESOLUTION",
                                    "clause": output_clause,
                                    "event": event,
                                    "local_resolution_count": 1
                                    + int(left_path["local_resolution_count"])
                                    + int(right_path["local_resolution_count"]),
                                    "steps": (post_step, branch_step, pre_step),
                                    "children": (left_path, right_path),
                                })

        assert results
        unique = {}
        for result in results:
            key = repr(result)
            unique[key] = result
        return tuple(unique.values())

    def flatten_roots(node):
        if node["kind"] == "ROOT":
            return (node,)
        roots = []
        for child in node.get("children", ()):
            roots.extend(flatten_roots(child))
        return tuple(roots)

    counts: Counter[str] = Counter()
    root_event_shapes: Counter[tuple[int, int, int]] = Counter()
    branch_literal_sequences: Counter[tuple[int, ...]] = Counter()
    records = []

    for record in wing_data["records"]:
        state_id = int(record["state_id"])
        call_id = int(record["call_id"])
        state = policy.states[state_id]
        clause = tuple(record["clause"])
        bad_literal = int(record["bad_literal"])
        selected = int(record["selected"])
        producing = tuple(record["origins"])
        assert len(producing) == 1
        event = producing[0]

        left = tuple(event["left"])
        right = tuple(event["right"])
        before_assignment = context["call_after_pre"][call_id]
        left_class = str(
            safety_class(n, left, before_assignment, pairs)["classification"]
        )
        right_class = str(
            safety_class(n, right, before_assignment, pairs)["classification"]
        )
        assert {left_class, right_class} == {
            "DIRECTED_CYCLE",
            "COMPONENT_SPANNING",
        }
        spanning_parent = left if left_class == "COMPONENT_SPANNING" else right
        cycle_parent = right if spanning_parent == left else left

        paths = proof_paths(call_id, spanning_parent)
        minimum = min(int(path["local_resolution_count"]) for path in paths)
        shortest = tuple(
            path for path in paths
            if int(path["local_resolution_count"]) == minimum
        )
        assert shortest

        certified = []
        for path in shortest:
            if path["kind"] != "LOCAL_RESOLUTION":
                continue
            root_event = path["event"]
            root_children = tuple(path["children"])
            roots = tuple(
                root_node
                for child in root_children
                for root_node in flatten_roots(child)
            )
            labels = tuple(
                label
                for root_node in roots
                for label in root_node["labels"]
            )
            minimum_roots = tuple(
                root_node
                for root_node in roots
                if any(label[0] == "ROOT_NON_MINIMALITY" for label in root_node["labels"])
            )
            transitivity_roots = tuple(
                root_node
                for root_node in roots
                if any(label[0] == "ROOT_TRANSITIVITY" for label in root_node["labels"])
            )
            if len(minimum_roots) != 1 or len(transitivity_roots) != 1:
                continue

            minimum_root = minimum_roots[0]
            transitivity_root = transitivity_roots[0]
            owner_labels = tuple(
                int(label[1])
                for label in minimum_root["labels"]
                if label[0] == "ROOT_NON_MINIMALITY"
            )
            assert len(owner_labels) == 1
            owner = owner_labels[0]

            n_edges = clause_edges(tuple(minimum_root["clause"]), pairs)
            root_resolvent = tuple(root_event["resolvent"])
            r_edges = clause_edges(root_resolvent, pairs)
            removed = tuple(sorted(n_edges - r_edges))
            added = tuple(sorted(r_edges - n_edges))
            if len(removed) != 1 or len(added) != 1:
                continue
            child_vertex, removed_head = removed[0]
            added_tail, middle_vertex = added[0]
            if removed_head != owner or added_tail != child_vertex:
                continue
            if (middle_vertex, owner) not in n_edges:
                continue

            # Only restriction steps may occur after the root N/T event on the
            # chosen shortest ancestry path.
            later_steps = tuple(path["steps"])
            assert all(
                step["kind"] in {
                    "PRE_UNIT_REDUCTION",
                    "POST_UNIT_REDUCTION",
                    "BRANCH_REDUCTION",
                }
                for step in later_steps
            )
            nonempty_units = tuple(
                step
                for step in later_steps
                if step["kind"] != "BRANCH_REDUCTION"
                and step.get("assignment")
            )
            assert not nonempty_units
            branch_literals = tuple(
                int(step["branch_literal"])
                for step in later_steps
                if step["kind"] == "BRANCH_REDUCTION"
            )

            current_edges = clause_edges(spanning_parent, pairs)
            assert (child_vertex, middle_vertex) in current_edges
            assert (middle_vertex, owner) in current_edges
            assert all(
                head == owner or (tail, head) == (child_vertex, middle_vertex)
                for tail, head in current_edges
            )

            producer_pivot = int(event["pivot"])
            pivot_low, pivot_high = pairs[producer_pivot]
            pivot_edge = frozenset((int(pivot_low), int(pivot_high)))
            assert pivot_edge == frozenset((middle_vertex, owner))

            bad_tail, bad_head = original_direction(bad_literal, pairs)
            assert bad_tail == middle_vertex
            assert (child_vertex, middle_vertex) == original_direction(
                next(lit for lit in clause if abs(lit) == selected),
                pairs,
            )

            certified.append({
                "root_event": root_event,
                "root_labels": labels,
                "owner": owner,
                "redirected_child": child_vertex,
                "middle": middle_vertex,
                "removed_star_edge": removed[0],
                "added_redirected_edge": added[0],
                "branch_literals": branch_literals,
                "spanning_parent": spanning_parent,
                "spanning_parent_edges": tuple(sorted(current_edges)),
                "cycle_parent": cycle_parent,
                "producer_pivot": producer_pivot,
                "bad_literal": bad_literal,
                "bad_direction": (bad_tail, bad_head),
                "selected": selected,
            })

        assert certified
        witness = certified[0]
        counts["occurrences"] += 1
        counts["single_root_subdivision"] += 1
        counts["restriction_only_after_root_event"] += 1
        counts["producer_relocates_middle_center_edge"] += 1
        counts["selected_is_redirected_edge"] += 1
        root_event_shapes[(
            len(tuple(witness["root_event"]["left"])),
            len(tuple(witness["root_event"]["right"])),
            len(tuple(witness["root_event"]["resolvent"])),
        )] += 1
        branch_literal_sequences[tuple(witness["branch_literals"])] += 1
        records.append({
            "n": n,
            "state_id": state_id,
            "call_id": call_id,
            "clause": clause,
            "witness": witness,
            "path_count": len(paths),
            "minimum_local_resolution_count": minimum,
        })

    return {
        "n": n,
        "counts": tuple(sorted(counts.items())),
        "root_event_shapes": tuple(sorted(root_event_shapes.items())),
        "branch_literal_sequences": tuple(sorted(branch_literal_sequences.items())),
        "records": tuple(records),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_shapes: Counter[tuple[int, int, int]] = Counter()
    aggregate_branches: Counter[tuple[int, ...]] = Counter()
    all_records = []

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_shapes.update(dict(data["root_event_shapes"]))
        aggregate_branches.update(dict(data["branch_literal_sequences"]))
        all_records.extend(data["records"])
        print(f"ORDER_SIZE = {n}")
        print(f"  counts = {data['counts']}")
        print(f"  root_event_shapes = {data['root_event_shapes']}")
        print(f"  branch_literal_sequences = {data['branch_literal_sequences']}")
        print(f"  records = {data['records']}")

    expected = 3
    for name in (
        "occurrences",
        "single_root_subdivision",
        "restriction_only_after_root_event",
        "producer_relocates_middle_center_edge",
        "selected_is_redirected_edge",
    ):
        assert aggregate_counts[name] == expected, (name, aggregate_counts[name])
    assert len({(row["state_id"], row["call_id"]) for row in all_records}) == 1

    print("JANUS_GT_NONROOT_WING_RECURSIVE_ANCESTRY = PASS")
    print(f"AGGREGATE_COUNTS = {tuple(sorted(aggregate_counts.items()))}")
    print(f"AGGREGATE_ROOT_EVENT_SHAPES = {tuple(sorted(aggregate_shapes.items()))}")
    print(f"AGGREGATE_BRANCH_SEQUENCES = {tuple(sorted(aggregate_branches.items()))}")
    print(f"ALL_RECORDS = {tuple(all_records)}")
    print(
        "claim_boundary = exact recursive ancestry for the three GT_8 non-root "
        "wing occurrences; arbitrary-n one-subdivision reachability remains open"
    )


if __name__ == "__main__":
    self_test()
