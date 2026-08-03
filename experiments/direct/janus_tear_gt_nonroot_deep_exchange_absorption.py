#!/usr/bin/env python3
"""Classify the finite deep raw tree exchanges that disappear before child keys.

The non-root tree-exchange handoff census finds exactly three GT_8 events whose
raw/post resolvent is an in-arborescence of height three with two non-star
edges.  None survives as an in-arborescence in a child exact key.

This script does not promote that finite fact to arbitrary n.  It emits the
selected branch geometry and both child fates so the next proof obligation can
be stated as an exact absorption lemma rather than the false claim that local
Resolution never creates deeper trees.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_component_tree_clause_audit import (
    clause_component_graph,
    execution_context,
)
from janus_tear_gt_nonroot_tree_exchange_handoff import audit as handoff_audit


def component_index(parts):
    return {
        int(vertex): component
        for component, part in enumerate(parts)
        for vertex in part
    }


def classify(n: int):
    context = execution_context(n)
    policy = context["policy"]
    pairs = context["pairs"]
    rows = []
    fates: Counter[str] = Counter()
    size_pairs: Counter[tuple[int, int]] = Counter()
    selected_relations: Counter[str] = Counter()
    literal_signatures: Counter[tuple[int, ...]] = Counter()

    for record in handoff_audit(n)["records"]:
        raw_shape = record["raw_shape"]
        if raw_shape is None or not (raw_shape[0] > 2 or raw_shape[1] > 1):
            continue

        state_id = int(record["state_id"])
        state = policy.states[state_id]
        selected = int(state["branch_var"])
        post_clause = record["post_clause"]
        assert post_clause is not None
        post_assignment = context["state_after_post"][state_id]
        graph = clause_component_graph(
            n, tuple(post_clause), post_assignment, pairs
        )
        parts = tuple(tuple(sorted(int(v) for v in part)) for part in graph["parts"])
        index = component_index(parts)
        left, right = (int(x) for x in pairs[selected])
        left_component = index[left]
        right_component = index[right]
        relation = (
            "INTERNAL_COMPONENT"
            if left_component == right_component
            else "EXTERNAL_COMPONENT_PAIR"
        )
        selected_relations[relation] += 1
        component_sizes = tuple(sorted((
            len(parts[left_component]),
            len(parts[right_component]),
        )))
        size_pairs[component_sizes] += 1

        selected_literals = tuple(
            int(literal)
            for literal in post_clause
            if abs(int(literal)) == selected
        )
        literal_signatures[selected_literals] += 1

        child_rows = []
        for child in record["children"]:
            fate = str(child["fate"])
            fates[fate] += 1
            assert fate != "CHILD_KEY_IN_ARBORESCENCE"
            child_rows.append({
                "value": bool(child["value"]),
                "call": child["call"],
                "fate": fate,
                "residual": child.get("residual"),
                "shape": child.get("shape"),
            })

        rows.append({
            "n": n,
            "state_id": state_id,
            "call_id": int(record["call_id"]),
            "depth": int(record["depth"]),
            "event_index": int(record["event_index"]),
            "pivot": int(record["pivot"]),
            "selected": selected,
            "selected_endpoints": (left, right),
            "selected_components": (left_component, right_component),
            "selected_component_sizes": component_sizes,
            "selected_relation": relation,
            "selected_literals": selected_literals,
            "source_shape": record["source_shape"],
            "raw_shape": raw_shape,
            "post_shape": record["post_shape"],
            "tree": record["tree"],
            "cycle": record["cycle"],
            "result": record["result"],
            "post_clause": post_clause,
            "parts": parts,
            "children": tuple(child_rows),
        })

    return {
        "n": n,
        "rows": tuple(rows),
        "fates": tuple(sorted(fates.items())),
        "selected_component_sizes": tuple(sorted(size_pairs.items())),
        "selected_relations": tuple(sorted(selected_relations.items())),
        "literal_signatures": tuple(sorted(literal_signatures.items(), key=repr)),
    }


def self_test() -> None:
    all_rows = []
    aggregate_fates: Counter[str] = Counter()
    aggregate_sizes: Counter[tuple[int, int]] = Counter()
    aggregate_relations: Counter[str] = Counter()
    aggregate_literals: Counter[tuple[int, ...]] = Counter()

    for n in range(4, 9):
        data = classify(n)
        all_rows.extend(data["rows"])
        aggregate_fates.update(dict(data["fates"]))
        aggregate_sizes.update(dict(data["selected_component_sizes"]))
        aggregate_relations.update(dict(data["selected_relations"]))
        aggregate_literals.update(dict(data["literal_signatures"]))
        print(f"ORDER_SIZE = {n}")
        print(f"  rows = {data['rows']}")
        print(f"  fates = {data['fates']}")
        print(f"  selected_component_sizes = {data['selected_component_sizes']}")
        print(f"  selected_relations = {data['selected_relations']}")
        print(f"  literal_signatures = {data['literal_signatures']}")

    assert len(all_rows) == 3, len(all_rows)
    assert {row["n"] for row in all_rows} == {8}
    assert all(row["raw_shape"] == (3, 2, False) for row in all_rows)
    assert all(row["post_shape"] == (3, 2, False) for row in all_rows)
    assert sum(aggregate_fates.values()) > 0

    print("JANUS_GT_NONROOT_DEEP_EXCHANGE_ABSORPTION = PASS")
    print(f"ROWS = {tuple(all_rows)}")
    print(f"AGGREGATE_FATES = {tuple(sorted(aggregate_fates.items()))}")
    print(f"AGGREGATE_SELECTED_COMPONENT_SIZES = {tuple(sorted(aggregate_sizes.items()))}")
    print(f"AGGREGATE_SELECTED_RELATIONS = {tuple(sorted(aggregate_relations.items()))}")
    print(f"AGGREGATE_LITERAL_SIGNATURES = {tuple(sorted(aggregate_literals.items(), key=repr))}")
    print(
        "claim_boundary = exact finite classifier for the three GT_8 deep raw "
        "tree exchanges; arbitrary-n deep-exchange absorption and singleton "
        "reachability remain open"
    )


if __name__ == "__main__":
    self_test()
