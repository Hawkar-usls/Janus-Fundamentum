#!/usr/bin/env python3
"""Localize dangerous singleton/singleton lineages before branch handoff.

The canonical N_a shield is already active when a dangerous bridge has a
singleton tail and a head component of size at least two.  This audit separates
the 42 immediate-local surviving lineages into:

- already shielded lineages with merged head;
- unshielded singleton-tail/singleton-head lineages.

It then checks whether every unshielded finite lineage is confined to the root
state, where the selected branch can be attacked by one explicit deterministic
root calculation rather than a recursive history theorem.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_component_tree_clause_audit import (
    clause_component_graph,
    execution_context,
)
from janus_tear_gt_root_nonminimality_bridge_shield import original_direction
from janus_tear_gt_surviving_branch_frequency_profile import (
    audit as lineage_audit,
    quotient_map,
    relation,
)


def audit(n: int):
    context = execution_context(n)
    policy = context["policy"]
    pairs = context["pairs"]
    levels = context["levels"]
    records = tuple(lineage_audit(n)["records"])

    counts: Counter[str] = Counter()
    selected_relations: Counter[str] = Counter()
    unshielded_selected_relations: Counter[str] = Counter()
    head_sizes: Counter[int] = Counter()
    root_selected_variables: Counter[int] = Counter()
    rows = []

    for item in records:
        counts["lineages"] += 1
        state_id = int(item["parent_state"])
        state = policy.states[state_id]
        call_id = int(state["entry_call"])
        assignment = context["state_after_post"][state_id]
        source = tuple(item["source"])
        bad_literal = int(item["bad_literal"])
        selected = int(item["selected_variable"])

        graph = clause_component_graph(n, source, assignment, pairs)
        vertex_component = quotient_map(graph, n)
        parts = tuple(tuple(part) for part in graph["parts"])
        tail_vertex, head_vertex = original_direction(bad_literal, pairs)
        tail_component = vertex_component[tail_vertex]
        head_component = vertex_component[head_vertex]
        tail_size = len(parts[tail_component])
        head_size = len(parts[head_component])
        assert tail_size == 1
        head_sizes[head_size] += 1

        low, high = pairs[selected]
        selected_relation = relation(
            (vertex_component[int(low)], vertex_component[int(high)]),
            tail_component,
            head_component,
        )
        selected_relations[selected_relation] += 1

        is_root = int(state["depth"]) == 0
        novelty = int(levels[call_id])
        if head_size == 1:
            counts["unshielded_lineages"] += 1
            unshielded_selected_relations[selected_relation] += 1
            if is_root:
                counts["unshielded_at_root"] += 1
                root_selected_variables[selected] += 1
            else:
                counts["unshielded_nonroot"] += 1
        else:
            counts["already_shielded_lineages"] += 1

        rows.append(
            {
                "n": n,
                "parent_state": state_id,
                "parent_call": call_id,
                "depth": int(state["depth"]),
                "novelty": novelty,
                "bad_literal": bad_literal,
                "tail_vertex": tail_vertex,
                "head_vertex": head_vertex,
                "tail_size": tail_size,
                "head_size": head_size,
                "selected": selected,
                "selected_literal": int(item["selected_literal"]),
                "selected_relation": selected_relation,
                "source": source,
            }
        )

    assert counts["unshielded_nonroot"] == 0
    assert counts["unshielded_lineages"] == counts["unshielded_at_root"]
    assert all(
        row["selected_relation"] in ("TAIL_HEAD", "TAIL_TO_OTHER", "HEAD_TO_OTHER")
        for row in rows
        if row["head_size"] == 1
    )
    return {
        "n": n,
        "counts": tuple(sorted(counts.items())),
        "head_sizes": tuple(sorted(head_sizes.items())),
        "selected_relations": tuple(sorted(selected_relations.items())),
        "unshielded_selected_relations": tuple(
            sorted(unshielded_selected_relations.items())
        ),
        "root_selected_variables": tuple(sorted(root_selected_variables.items())),
        "rows": tuple(rows),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_heads: Counter[int] = Counter()
    aggregate_relations: Counter[str] = Counter()
    aggregate_unshielded_relations: Counter[str] = Counter()
    aggregate_root_selected: Counter[int] = Counter()

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_heads.update(dict(data["head_sizes"]))
        aggregate_relations.update(dict(data["selected_relations"]))
        aggregate_unshielded_relations.update(
            dict(data["unshielded_selected_relations"])
        )
        aggregate_root_selected.update(dict(data["root_selected_variables"]))
        print(f"ORDER_SIZE = {n}")
        print(f"  counts = {data['counts']}")
        print(f"  head_sizes = {data['head_sizes']}")
        print(
            "  unshielded_selected_relations = "
            f"{data['unshielded_selected_relations']}"
        )
        print(f"  root_selected_variables = {data['root_selected_variables']}")
        print(
            "  unshielded_rows = "
            f"{tuple(row for row in data['rows'] if row['head_size'] == 1)}"
        )

    assert aggregate_counts["lineages"] == 42
    assert aggregate_counts["unshielded_lineages"] == 12
    assert aggregate_counts["unshielded_at_root"] == 12
    assert aggregate_counts["unshielded_nonroot"] == 0
    assert aggregate_counts["already_shielded_lineages"] == 30

    print("JANUS_GT_UNSHIELDED_LINEAGE_LOCALIZATION = PASS")
    print(f"AGGREGATE_COUNTS = {tuple(sorted(aggregate_counts.items()))}")
    print(f"AGGREGATE_HEAD_SIZES = {tuple(sorted(aggregate_heads.items()))}")
    print(
        "AGGREGATE_UNSHIELDED_RELATIONS = "
        f"{tuple(sorted(aggregate_unshielded_relations.items()))}"
    )
    print(
        "AGGREGATE_ROOT_SELECTED = "
        f"{tuple(sorted(aggregate_root_selected.items()))}"
    )
    print(
        "finite_result = every unshielded surviving dangerous lineage through "
        "GT_8 is confined to the root state"
    )
    print(
        "claim_boundary = finite root localization; arbitrary-n root/nonroot "
        "localization remains open"
    )


if __name__ == "__main__":
    self_test()
