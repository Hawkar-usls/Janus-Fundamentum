#!/usr/bin/env python3
"""Classify every exact root ancestry of the non-root tail-wing tree parent.

A previous candidate asserted that the inherited component-spanning parent had
one canonical root N/T subdivision ancestry.  The first exact-head run rejected
that assertion before producing a witness.  This hardened version does not
repair the assertion by selecting a convenient non-minimal path.  It enumerates
all exact root proof paths and records:

* the minimum number of local Resolution events;
* every minimum-path kind and root-label signature;
* whether a one-Resolution N/T subdivision path exists;
* whether that path is minimum and whether it is unique.

Thus the transcript distinguishes an obligatory producer normal form from a
merely alternative derivation.  The arbitrary-n reachability theorem remains
open regardless of the finite classification.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from functools import lru_cache

from janus_tear_gt_component_merge_sources import reduce_clause
from janus_tear_gt_component_tree_clause_audit import execution_context
from janus_tear_gt_nonroot_wing_provenance import audit as provenance_audit
from janus_tear_gt_rank_safety_dichotomy import safety_class
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
                results.append({
                    "kind": "ROOT",
                    "clause": input_clause,
                    "labels": direct_root_labels(
                        root, input_clause, {}, minimum_labels
                    ),
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
        return tuple({repr(item): item for item in results}.values())

    def flatten_roots(node):
        if node["kind"] == "ROOT":
            return (node,)
        roots = []
        for child in node.get("children", ()):
            roots.extend(flatten_roots(child))
        return tuple(roots)

    def label_signature(path):
        labels = []
        for root_node in flatten_roots(path):
            labels.extend(str(label[0]) for label in root_node["labels"])
        return tuple(sorted(labels))

    counts: Counter[str] = Counter()
    path_histogram: Counter[tuple[str, int]] = Counter()
    minimum_histogram: Counter[int] = Counter()
    minimum_signature_histogram: Counter[tuple[str, ...]] = Counter()
    one_subdivision_signature_histogram: Counter[tuple[str, ...]] = Counter()
    records = []

    for record in wing_data["records"]:
        call_id = int(record["call_id"])
        event = tuple(record["origins"])[0]
        left = tuple(event["left"])
        right = tuple(event["right"])
        assignment = context["call_after_pre"][call_id]
        left_class = str(
            safety_class(n, left, assignment, pairs)["classification"]
        )
        right_class = str(
            safety_class(n, right, assignment, pairs)["classification"]
        )
        assert {left_class, right_class} == {
            "DIRECTED_CYCLE",
            "COMPONENT_SPANNING",
        }
        spanning_parent = left if left_class == "COMPONENT_SPANNING" else right

        paths = proof_paths(call_id, spanning_parent)
        assert paths
        counts["occurrences_analyzed"] += 1
        counts["proof_paths"] += len(paths)

        for path in paths:
            path_histogram[(
                str(path["kind"]),
                int(path["local_resolution_count"]),
            )] += 1

        minimum = min(int(path["local_resolution_count"]) for path in paths)
        minimum_paths = tuple(
            path
            for path in paths
            if int(path["local_resolution_count"]) == minimum
        )
        minimum_histogram[minimum] += 1
        for path in minimum_paths:
            minimum_signature_histogram[label_signature(path)] += 1

        subdivision_paths = []
        for path in paths:
            if path["kind"] != "LOCAL_RESOLUTION":
                continue
            if int(path["local_resolution_count"]) != 1:
                continue
            signature = label_signature(path)
            if signature.count("ROOT_NON_MINIMALITY") != 1:
                continue
            if signature.count("ROOT_TRANSITIVITY") != 1:
                continue
            subdivision_paths.append(path)
            one_subdivision_signature_histogram[signature] += 1

        if subdivision_paths:
            counts["one_subdivision_exists"] += 1
        if subdivision_paths and minimum == 1:
            counts["one_subdivision_is_minimum"] += 1
        if len(paths) == 1 and len(subdivision_paths) == 1:
            counts["one_subdivision_is_unique"] += 1
        if not subdivision_paths:
            counts["one_subdivision_absent"] += 1
        if minimum == 0:
            counts["zero_resolution_minimum"] += 1

        records.append({
            "n": n,
            "state_id": int(record["state_id"]),
            "call_id": call_id,
            "clause": tuple(record["clause"]),
            "spanning_parent": spanning_parent,
            "path_count": len(paths),
            "minimum_local_resolution_count": minimum,
            "minimum_paths": tuple(
                {
                    "kind": str(path["kind"]),
                    "signature": label_signature(path),
                    "step_kinds": tuple(step["kind"] for step in path["steps"]),
                }
                for path in minimum_paths
            ),
            "one_subdivision_path_count": len(subdivision_paths),
            "one_subdivision_signatures": tuple(
                label_signature(path) for path in subdivision_paths
            ),
        })

    return {
        "n": n,
        "counts": tuple(sorted(counts.items())),
        "path_histogram": tuple(sorted(path_histogram.items(), key=repr)),
        "minimum_histogram": tuple(sorted(minimum_histogram.items())),
        "minimum_signature_histogram": tuple(
            sorted(minimum_signature_histogram.items(), key=repr)
        ),
        "one_subdivision_signature_histogram": tuple(
            sorted(one_subdivision_signature_histogram.items(), key=repr)
        ),
        "records": tuple(records),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_paths: Counter[tuple[str, int]] = Counter()
    aggregate_minima: Counter[int] = Counter()
    aggregate_min_signatures: Counter[tuple[str, ...]] = Counter()
    aggregate_subdivision_signatures: Counter[tuple[str, ...]] = Counter()
    all_records = []

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_paths.update(dict(data["path_histogram"]))
        aggregate_minima.update(dict(data["minimum_histogram"]))
        aggregate_min_signatures.update(
            dict(data["minimum_signature_histogram"])
        )
        aggregate_subdivision_signatures.update(
            dict(data["one_subdivision_signature_histogram"])
        )
        all_records.extend(data["records"])
        print(f"ORDER_SIZE = {n}")
        print(f"  counts = {data['counts']}")
        print(f"  path_histogram = {data['path_histogram']}")
        print(f"  minimum_histogram = {data['minimum_histogram']}")
        print(
            f"  minimum_signature_histogram = "
            f"{data['minimum_signature_histogram']}"
        )
        print(
            f"  one_subdivision_signature_histogram = "
            f"{data['one_subdivision_signature_histogram']}"
        )
        print(f"  records = {data['records']}")

    assert aggregate_counts["occurrences_analyzed"] == 3
    assert aggregate_counts["proof_paths"] >= 3
    assert len({(row["state_id"], row["call_id"]) for row in all_records}) == 1

    print("JANUS_GT_NONROOT_WING_RECURSIVE_ANCESTRY_CLASSIFIER = PASS")
    print(f"AGGREGATE_COUNTS = {tuple(sorted(aggregate_counts.items()))}")
    print(f"AGGREGATE_PATH_HISTOGRAM = {tuple(sorted(aggregate_paths.items(), key=repr))}")
    print(f"AGGREGATE_MINIMUM_HISTOGRAM = {tuple(sorted(aggregate_minima.items()))}")
    print(
        "AGGREGATE_MINIMUM_SIGNATURES = "
        f"{tuple(sorted(aggregate_min_signatures.items(), key=repr))}"
    )
    print(
        "AGGREGATE_ONE_SUBDIVISION_SIGNATURES = "
        f"{tuple(sorted(aggregate_subdivision_signatures.items(), key=repr))}"
    )
    print(f"ALL_RECORDS = {tuple(all_records)}")
    print(
        "claim_boundary = exact finite ancestry classification; canonical or "
        "arbitrary-n one-subdivision reachability is not assumed"
    )


if __name__ == "__main__":
    self_test()
