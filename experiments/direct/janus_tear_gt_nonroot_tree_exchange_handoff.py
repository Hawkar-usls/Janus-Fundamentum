#!/usr/bin/env python3
"""Trace every exact non-root tree exchange into later parent eligibility.

The complete finite census through GT_8 finds 121 non-root
transitivity/arborescence events.  Every inherited tree parent is either a star
or a one-subdivision star, and 17 events are exact one-edge tree exchanges.

This checker asks the closure question needed for arbitrary-n reachability:

    can an exact exchange create a deeper or multi-subdivision in-arborescence
    which survives into a child exact key and becomes a future frozen parent?

For every exact exchange it records:

- source tree shape;
- raw result orientation and arborescence shape;
- post-unit fate;
- both executed branch-child fates;
- every child-key in-arborescence shape.

No closure theorem is assumed.  Any child-key in-arborescence with more than one
non-star edge or height greater than two is emitted as a finite normal-form
falsifier.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_component_merge_sources import reduce_clause
from janus_tear_gt_component_tree_clause_audit import (
    clause_component_graph,
    execution_context,
)
from janus_tear_gt_directed_component_clause_audit import orientation_class
from janus_tear_gt_nonroot_arborescence_exchange_census import (
    arborescence_profile,
    simple_external_edges,
)
from janus_tear_gt_rank_safety_dichotomy import safety_class


def tree_profile(n, clause, assignment, pairs):
    graph = clause_component_graph(n, clause, assignment, pairs)
    classification = str(
        safety_class(n, clause, assignment, pairs)["classification"]
    )
    orientation = str(orientation_class(clause, graph, pairs)["classification"])
    records, _edges, simple = simple_external_edges(clause, graph, pairs)
    profile = (
        arborescence_profile(records, int(graph["component_count"]))
        if classification == "COMPONENT_SPANNING"
        and orientation == "IN_ARBORESCENCE"
        and simple
        else None
    )
    return {
        "classification": classification,
        "orientation": orientation,
        "component_count": int(graph["component_count"]),
        "simple": bool(simple),
        "profile": profile,
    }


def shape(profile):
    if profile is None:
        return None
    return (
        int(profile["height"]),
        int(profile["nonstar_count"]),
        bool(profile["one_subdivision_star"]),
    )


def audit(n: int):
    context = execution_context(n)
    policy = context["policy"]
    pairs = context["pairs"]
    levels = context["levels"]
    target = n - 2

    counts: Counter[str] = Counter()
    source_shapes: Counter[tuple[int, int, bool]] = Counter()
    raw_result_shapes: Counter[tuple[int, int, bool]] = Counter()
    post_result_shapes: Counter[tuple[int, int, bool]] = Counter()
    child_key_shapes: Counter[tuple[int, int, bool]] = Counter()
    child_fates: Counter[str] = Counter()
    source_to_raw: Counter[
        tuple[tuple[int, int, bool], tuple[int, int, bool] | None]
    ] = Counter()
    deep_child_falsifiers = []
    records = []

    for state in policy.states.values():
        state_id = int(state["id"])
        call_id = int(state["entry_call"])
        depth = int(state["depth"])
        novelty = int(levels[call_id])
        if depth == 0 or novelty > target:
            continue
        assignment = context["call_after_pre"][call_id]

        for event_index, event in enumerate(state.get("resolution_events", ())):
            left = tuple(event["left"])
            right = tuple(event["right"])
            result = tuple(event["resolvent"])
            parent_profiles = [
                (clause, tree_profile(n, clause, assignment, pairs))
                for clause in (left, right)
            ]
            tree_parents = [
                (clause, profile)
                for clause, profile in parent_profiles
                if profile["profile"] is not None
            ]
            cycle_parents = [
                clause
                for clause, profile in parent_profiles
                if profile["orientation"] == "HAS_DIRECTED_CYCLE"
            ]
            if len(tree_parents) != 1 or len(cycle_parents) != 1:
                continue

            tree, tree_data = tree_parents[0]
            source_profile = tree_data["profile"]
            source_shape = shape(source_profile)
            assert source_shape is not None

            raw_data = tree_profile(n, result, assignment, pairs)
            raw_profile = raw_data["profile"]
            raw_shape = shape(raw_profile)

            # Exact exchange means a simple in-arborescence result with the
            # same number of external tree edges as the source.
            source_graph = clause_component_graph(n, tree, assignment, pairs)
            result_graph = clause_component_graph(n, result, assignment, pairs)
            source_external = tuple(source_graph["external_edges"])
            result_external = tuple(result_graph["external_edges"])
            exact_exchange = (
                raw_profile is not None
                and len(source_external) == len(result_external)
                and len(source_external)
                == int(source_graph["component_count"]) - 1
            )
            if not exact_exchange:
                continue

            counts["exact_exchange_events"] += 1
            source_shapes[source_shape] += 1
            raw_result_shapes[raw_shape] += 1
            source_to_raw[(source_shape, raw_shape)] += 1
            if raw_shape[0] > 2 or raw_shape[1] > 1:
                counts["raw_deep_or_multi_subdivision"] += 1

            post_assignment = context["state_after_post"][state_id]
            post_clause = reduce_clause(result, post_assignment)
            if post_clause is None:
                post_fate = "POST_EXTINCT"
                counts[post_fate] += 1
                post_data = None
                post_shape = None
            elif state.get("post_result") is None:
                post_fate = str(state["terminal"])
                counts["POST_TERMINAL"] += 1
                post_data = None
                post_shape = None
            elif post_clause not in tuple(state["post_result"]):
                post_fate = "POST_NOT_PRESENT"
                counts[post_fate] += 1
                post_data = None
                post_shape = None
            else:
                post_fate = "POST_PRESENT"
                counts[post_fate] += 1
                post_data = tree_profile(
                    n, post_clause, post_assignment, pairs
                )
                post_shape = shape(post_data["profile"])
                if post_shape is not None:
                    post_result_shapes[post_shape] += 1

            children = []
            if state["terminal"] in ("BRANCH_UNSAT", "BRANCH_SAT"):
                for child in state.get("children", ()):
                    child_call_id = child.get("call")
                    if child_call_id is None:
                        fate = "DIRECT_CONFLICT"
                        child_fates[fate] += 1
                        children.append({
                            "value": bool(child["value"]),
                            "call": None,
                            "fate": fate,
                        })
                        continue
                    child_call_id = int(child_call_id)
                    child_call = policy.calls[child_call_id]
                    child_key = child_call.get("key")
                    child_assignment = context["call_after_pre"][child_call_id]
                    residual = reduce_clause(result, child_assignment)
                    if residual is None:
                        fate = "CLAUSE_EXTINCT"
                        child_data = None
                        child_shape = None
                    elif child_key is None:
                        fate = str(child_call["terminal"])
                        child_data = None
                        child_shape = None
                    elif residual not in tuple(child_key):
                        fate = "NOT_IN_CHILD_KEY"
                        child_data = None
                        child_shape = None
                    else:
                        child_data = tree_profile(
                            n, residual, child_assignment, pairs
                        )
                        child_shape = shape(child_data["profile"])
                        fate = (
                            "CHILD_KEY_IN_ARBORESCENCE"
                            if child_shape is not None
                            else f"CHILD_KEY_{child_data['orientation']}"
                        )
                        if child_shape is not None:
                            child_key_shapes[child_shape] += 1
                            counts["child_key_in_arborescence"] += 1
                            if child_shape[0] > 2 or child_shape[1] > 1:
                                counts["deep_child_key_falsifiers"] += 1
                                deep_child_falsifiers.append({
                                    "n": n,
                                    "state_id": state_id,
                                    "call_id": call_id,
                                    "event_index": event_index,
                                    "source": tree,
                                    "result": result,
                                    "source_shape": source_shape,
                                    "raw_shape": raw_shape,
                                    "child_call": child_call_id,
                                    "residual": residual,
                                    "child_shape": child_shape,
                                })
                    child_fates[fate] += 1
                    children.append({
                        "value": bool(child["value"]),
                        "call": child_call_id,
                        "fate": fate,
                        "residual": residual,
                        "shape": child_shape,
                    })
                    if child["result"]:
                        break

            records.append({
                "n": n,
                "state_id": state_id,
                "call_id": call_id,
                "depth": depth,
                "novelty": novelty,
                "event_index": event_index,
                "pivot": int(event["pivot"]),
                "tree": tree,
                "cycle": cycle_parents[0],
                "result": result,
                "source_shape": source_shape,
                "raw_shape": raw_shape,
                "post_fate": post_fate,
                "post_clause": post_clause,
                "post_shape": post_shape,
                "children": tuple(children),
            })

    return {
        "n": n,
        "counts": tuple(sorted(counts.items())),
        "source_shapes": tuple(sorted(source_shapes.items(), key=repr)),
        "raw_result_shapes": tuple(sorted(raw_result_shapes.items(), key=repr)),
        "post_result_shapes": tuple(sorted(post_result_shapes.items(), key=repr)),
        "child_key_shapes": tuple(sorted(child_key_shapes.items(), key=repr)),
        "child_fates": tuple(sorted(child_fates.items())),
        "source_to_raw": tuple(sorted(source_to_raw.items(), key=repr)),
        "deep_child_falsifiers": tuple(deep_child_falsifiers),
        "records": tuple(records),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_sources: Counter[tuple[int, int, bool]] = Counter()
    aggregate_raw: Counter[tuple[int, int, bool]] = Counter()
    aggregate_post: Counter[tuple[int, int, bool]] = Counter()
    aggregate_child: Counter[tuple[int, int, bool]] = Counter()
    aggregate_fates: Counter[str] = Counter()
    aggregate_transitions: Counter[
        tuple[tuple[int, int, bool], tuple[int, int, bool] | None]
    ] = Counter()
    falsifiers = []

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_sources.update(dict(data["source_shapes"]))
        aggregate_raw.update(dict(data["raw_result_shapes"]))
        aggregate_post.update(dict(data["post_result_shapes"]))
        aggregate_child.update(dict(data["child_key_shapes"]))
        aggregate_fates.update(dict(data["child_fates"]))
        aggregate_transitions.update(dict(data["source_to_raw"]))
        falsifiers.extend(data["deep_child_falsifiers"])
        print(f"ORDER_SIZE = {n}")
        print(f"  counts = {data['counts']}")
        print(f"  source_shapes = {data['source_shapes']}")
        print(f"  raw_result_shapes = {data['raw_result_shapes']}")
        print(f"  post_result_shapes = {data['post_result_shapes']}")
        print(f"  child_key_shapes = {data['child_key_shapes']}")
        print(f"  child_fates = {data['child_fates']}")
        print(f"  source_to_raw = {data['source_to_raw']}")
        print(f"  deep_child_falsifiers = {data['deep_child_falsifiers']}")

    assert aggregate_counts["exact_exchange_events"] > 0
    assert not falsifiers
    print("JANUS_GT_NONROOT_TREE_EXCHANGE_HANDOFF = PASS")
    print(f"AGGREGATE_COUNTS = {tuple(sorted(aggregate_counts.items()))}")
    print(f"AGGREGATE_SOURCE_SHAPES = {tuple(sorted(aggregate_sources.items(), key=repr))}")
    print(f"AGGREGATE_RAW_RESULT_SHAPES = {tuple(sorted(aggregate_raw.items(), key=repr))}")
    print(f"AGGREGATE_POST_RESULT_SHAPES = {tuple(sorted(aggregate_post.items(), key=repr))}")
    print(f"AGGREGATE_CHILD_KEY_SHAPES = {tuple(sorted(aggregate_child.items(), key=repr))}")
    print(f"AGGREGATE_CHILD_FATES = {tuple(sorted(aggregate_fates.items()))}")
    print(f"AGGREGATE_SOURCE_TO_RAW = {tuple(sorted(aggregate_transitions.items(), key=repr))}")
    print(f"DEEP_CHILD_FALSIFIERS = {tuple(falsifiers)}")
    print(
        "claim_boundary = exact finite handoff of every non-root exact tree "
        "exchange through GT_8; arbitrary-n star/one-subdivision closure remains "
        "open"
    )


if __name__ == "__main__":
    self_test()
