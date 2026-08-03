#!/usr/bin/env python3
"""Recursively trace inherited pre-unit merge clauses to root or local Resolution.

The one-generation C024 audit found that every derived pre-unit component merge
is created by branching on a binary parent clause.  Three such binary clauses
are immediate parent-local resolvents and nine are inherited in the parent key.

This checker follows an inherited key clause backwards through the exact stages:

  key <- pre-unit reduction <- call input
      <- parent branch reduction <- parent post CNF
      <- parent post-unit reduction <- parent resolution output

At each ancestor it stops at either:
- an original root clause, or
- an explicit local Resolution event whose resolvent is the antecedent clause.

All transformations are replayed from the serialized FC trace.  The result is a
finite first-origin provenance audit, not an asymptotic proof that such origins
cannot occur early for arbitrary n.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from functools import lru_cache

from janus_tear_gt_component_merge_sources import audit as merge_source_audit, reduce_clause
from janus_tear_policy0a_fc_trace import FCTracePolicy, verify_fc_trace
from janus_tear_policy0a_graph_tautology_probe import graph_tautology_cnf

Clause = tuple[int, ...]
CNF = tuple[Clause, ...]


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


def event_payload(state_id: int, index: int, event) -> dict[str, object]:
    return {
        "state_id": state_id,
        "event_index": index,
        "left": tuple(event["left"]),
        "right": tuple(event["right"]),
        "pivot": int(event["pivot"]),
        "resolvent": tuple(event["resolvent"]),
        "attempt": int(event["attempt"]),
    }


def audit(n: int):
    root, variable_count = graph_tautology_cnf(n)
    merge_data = merge_source_audit(n)
    targets = tuple(
        record for record in merge_data["records"] if record["stage"] == "pre"
    )

    policy = FCTracePolicy()
    result, root_call = policy.solve(root, variable_count)
    assert result.answer is False
    assert root_call is not None
    assert verify_fc_trace(root, variable_count, policy, root_call) is False

    parent_link: dict[int, dict[str, object]] = {}
    seen: set[int] = set()

    def build_links(call_id: int) -> None:
        assert call_id not in seen
        seen.add(call_id)
        call = policy.calls[call_id]
        if call["terminal"] != "STATE":
            return
        state_id = int(call["state"])
        state = policy.states[state_id]
        if state["terminal"] not in ("BRANCH_UNSAT", "BRANCH_SAT"):
            return
        variable = int(state["branch_var"])
        for child in state["children"]:
            if child["call"] is None:
                continue
            child_id = int(child["call"])
            value = bool(child["value"])
            parent_link[child_id] = {
                "parent_call_id": call_id,
                "parent_state_id": state_id,
                "branch_variable": variable,
                "branch_value": value,
                "branch_literal": variable if value else -variable,
            }
            build_links(child_id)
            if child["result"]:
                break

    build_links(root_call)
    assert len(seen) == len(policy.calls)

    def local_event_map(state) -> dict[Clause, tuple[dict[str, object], ...]]:
        grouped: dict[Clause, list[dict[str, object]]] = defaultdict(list)
        state_id = int(state["id"])
        for index, event in enumerate(state.get("resolution_events", [])):
            grouped[tuple(event["resolvent"])].append(
                event_payload(state_id, index, event)
            )
        return {clause: tuple(events) for clause, events in grouped.items()}

    @lru_cache(maxsize=None)
    def trace_key_clause(call_id: int, key_clause: Clause):
        """Return all first-origin paths for one clause in this call's key."""

        call = policy.calls[call_id]
        assert call["terminal"] == "STATE"
        state = policy.states[int(call["state"])]
        assert key_clause in tuple(state["key"])

        pre_assignment = unit_assignments(call.get("pre_units", []))
        input_antecedents = tuple(
            clause
            for clause in tuple(call["input"])
            if reduce_clause(clause, pre_assignment) == key_clause
        )
        assert input_antecedents, (n, call_id, key_clause, pre_assignment)

        paths = []
        for input_clause in input_antecedents:
            pre_step = {
                "kind": "PRE_UNIT_REDUCTION",
                "call_id": call_id,
                "from_clause": input_clause,
                "to_clause": key_clause,
                "unit_assignment": tuple(sorted(pre_assignment.items())),
            }

            if call_id == root_call:
                assert input_clause in root
                paths.append(
                    {
                        "origin": "ROOT_AXIOM",
                        "origin_clause": input_clause,
                        "origin_event": None,
                        "ancestor_hops": 0,
                        "steps": (pre_step,),
                    }
                )
                continue

            link = parent_link[call_id]
            parent_call_id = int(link["parent_call_id"])
            parent_state_id = int(link["parent_state_id"])
            parent_state = policy.states[parent_state_id]
            branch_assignment = {
                int(link["branch_variable"]): bool(link["branch_value"])
            }
            parent_post_clauses = tuple(
                clause
                for clause in tuple(parent_state["post_result"])
                if reduce_clause(clause, branch_assignment) == input_clause
            )
            assert parent_post_clauses, (
                n,
                call_id,
                key_clause,
                input_clause,
                link,
            )

            post_assignment = unit_assignments(parent_state.get("post_units", []))
            event_map = local_event_map(parent_state)
            parent_key: CNF = tuple(parent_state["key"])
            parent_output: CNF = tuple(parent_state["resolution_output"])

            for post_clause in parent_post_clauses:
                branch_step = {
                    "kind": "BRANCH_REDUCTION",
                    "parent_call_id": parent_call_id,
                    "parent_state_id": parent_state_id,
                    "branch_literal": int(link["branch_literal"]),
                    "from_clause": post_clause,
                    "to_clause": input_clause,
                }
                output_antecedents = tuple(
                    clause
                    for clause in parent_output
                    if reduce_clause(clause, post_assignment) == post_clause
                )
                assert output_antecedents, (
                    n,
                    call_id,
                    post_clause,
                    post_assignment,
                )

                for output_clause in output_antecedents:
                    post_step = {
                        "kind": "POST_UNIT_REDUCTION",
                        "parent_call_id": parent_call_id,
                        "parent_state_id": parent_state_id,
                        "from_clause": output_clause,
                        "to_clause": post_clause,
                        "unit_assignment": tuple(sorted(post_assignment.items())),
                    }
                    local_events = event_map.get(output_clause, ())
                    if local_events:
                        for event in local_events:
                            paths.append(
                                {
                                    "origin": "LOCAL_RESOLUTION",
                                    "origin_clause": output_clause,
                                    "origin_event": event,
                                    "ancestor_hops": 1,
                                    "steps": (post_step, branch_step, pre_step),
                                }
                            )

                    if output_clause in parent_key:
                        ancestor_paths = trace_key_clause(
                            parent_call_id, output_clause
                        )
                        for ancestor in ancestor_paths:
                            paths.append(
                                {
                                    "origin": ancestor["origin"],
                                    "origin_clause": ancestor["origin_clause"],
                                    "origin_event": ancestor["origin_event"],
                                    "ancestor_hops": int(
                                        ancestor["ancestor_hops"]
                                    )
                                    + 1,
                                    "steps": tuple(ancestor["steps"])
                                    + (post_step, branch_step, pre_step),
                                }
                            )

        assert paths, (n, call_id, key_clause)
        # Canonicalize duplicate paths caused by equivalent antecedent choices.
        unique = {}
        for path in paths:
            key = (
                path["origin"],
                tuple(path["origin_clause"]),
                repr(path["origin_event"]),
                repr(path["steps"]),
            )
            unique[key] = path
        return tuple(unique.values())

    def trace_child_unit(target):
        child_call_id = int(target["call_id"])
        literal = int(target["literal"])
        assert child_call_id in parent_link
        link = parent_link[child_call_id]
        parent_call_id = int(link["parent_call_id"])
        parent_state_id = int(link["parent_state_id"])
        parent_state = policy.states[parent_state_id]
        branch_assignment = {
            int(link["branch_variable"]): bool(link["branch_value"])
        }

        parent_post_clauses = tuple(
            clause
            for clause in tuple(parent_state["post_result"])
            if reduce_clause(clause, branch_assignment) == (literal,)
        )
        assert parent_post_clauses

        post_assignment = unit_assignments(parent_state.get("post_units", []))
        event_map = local_event_map(parent_state)
        parent_key: CNF = tuple(parent_state["key"])
        parent_output: CNF = tuple(parent_state["resolution_output"])
        paths = []

        for post_clause in parent_post_clauses:
            branch_step = {
                "kind": "FINAL_BRANCH_TO_UNIT",
                "parent_call_id": parent_call_id,
                "parent_state_id": parent_state_id,
                "branch_literal": int(link["branch_literal"]),
                "from_clause": post_clause,
                "to_clause": (literal,),
            }
            output_antecedents = tuple(
                clause
                for clause in parent_output
                if reduce_clause(clause, post_assignment) == post_clause
            )
            assert output_antecedents

            for output_clause in output_antecedents:
                post_step = {
                    "kind": "POST_UNIT_REDUCTION",
                    "parent_call_id": parent_call_id,
                    "parent_state_id": parent_state_id,
                    "from_clause": output_clause,
                    "to_clause": post_clause,
                    "unit_assignment": tuple(sorted(post_assignment.items())),
                }
                for event in event_map.get(output_clause, ()):
                    paths.append(
                        {
                            "origin": "LOCAL_RESOLUTION",
                            "origin_clause": output_clause,
                            "origin_event": event,
                            "ancestor_hops": 1,
                            "steps": (post_step, branch_step),
                        }
                    )
                if output_clause in parent_key:
                    for ancestor in trace_key_clause(
                        parent_call_id, output_clause
                    ):
                        paths.append(
                            {
                                "origin": ancestor["origin"],
                                "origin_clause": ancestor["origin_clause"],
                                "origin_event": ancestor["origin_event"],
                                "ancestor_hops": int(
                                    ancestor["ancestor_hops"]
                                )
                                + 1,
                                "steps": tuple(ancestor["steps"])
                                + (post_step, branch_step),
                            }
                        )

        assert paths
        minimum_hops = min(int(path["ancestor_hops"]) for path in paths)
        shortest = tuple(
            path for path in paths if int(path["ancestor_hops"]) == minimum_hops
        )
        return {
            "n": n,
            "child_call_id": child_call_id,
            "literal": literal,
            "pair": tuple(target["pair"]),
            "parent_call_id": parent_call_id,
            "parent_state_id": parent_state_id,
            "branch_literal": int(link["branch_literal"]),
            "all_path_count": len(paths),
            "minimum_ancestor_hops": minimum_hops,
            "shortest_origins": tuple(
                sorted({str(path["origin"]) for path in shortest})
            ),
            "shortest_paths": shortest,
        }

    records = tuple(trace_child_unit(target) for target in targets)
    origin_counts: Counter[str] = Counter()
    hop_histogram: Counter[int] = Counter()
    local_shapes: Counter[tuple[int, int, int]] = Counter()

    for record in records:
        hop_histogram[int(record["minimum_ancestor_hops"])] += 1
        for origin in record["shortest_origins"]:
            origin_counts[origin] += 1
        for path in record["shortest_paths"]:
            if path["origin"] != "LOCAL_RESOLUTION":
                continue
            event = path["origin_event"]
            assert event is not None
            local_shapes[
                (
                    len(tuple(event["left"])),
                    len(tuple(event["right"])),
                    len(tuple(event["resolvent"])),
                )
            ] += 1

    assert len(records) == len(targets)
    assert all(record["shortest_origins"] for record in records)

    return {
        "n": n,
        "pre_unit_component_merges": len(records),
        "origin_counts": tuple(sorted(origin_counts.items())),
        "hop_histogram": tuple(sorted(hop_histogram.items())),
        "maximum_minimum_hops": max(hop_histogram) if hop_histogram else 0,
        "local_resolution_shape_histogram": tuple(sorted(local_shapes.items())),
        "records": records,
    }


def self_test() -> None:
    rows = []
    aggregate_origins: Counter[str] = Counter()
    aggregate_hops: Counter[int] = Counter()
    maximum_hops = 0

    for n in range(4, 9):
        data = audit(n)
        aggregate_origins.update(dict(data["origin_counts"]))
        aggregate_hops.update(dict(data["hop_histogram"]))
        maximum_hops = max(maximum_hops, data["maximum_minimum_hops"])
        rows.append(
            (
                n,
                data["pre_unit_component_merges"],
                data["origin_counts"],
                data["hop_histogram"],
                data["maximum_minimum_hops"],
            )
        )
        print(f"ORDER_SIZE = {n}")
        print(f"  pre_unit_component_merges = {data['pre_unit_component_merges']}")
        print(f"  origin_counts = {data['origin_counts']}")
        print(f"  hop_histogram = {data['hop_histogram']}")
        print(f"  maximum_minimum_hops = {data['maximum_minimum_hops']}")
        print(
            "  local_resolution_shape_histogram = "
            f"{data['local_resolution_shape_histogram']}"
        )
        print(f"  records = {data['records']}")

    print("JANUS_GT_PRE_UNIT_RECURSIVE_PROVENANCE = PASS")
    print(f"rows = {tuple(rows)}")
    print(f"aggregate_origins = {tuple(sorted(aggregate_origins.items()))}")
    print(f"aggregate_hops = {tuple(sorted(aggregate_hops.items()))}")
    print(f"maximum_minimum_hops = {maximum_hops}")
    print("claim_boundary = exact finite first-origin provenance; no asymptotic bound on provenance depth")


if __name__ == "__main__":
    self_test()
