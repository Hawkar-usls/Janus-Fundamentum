#!/usr/bin/env python3
"""Census every unshielded local lineage at the P-to-K' branch handoff.

Post-unit safety is handled separately by T2a.  This checker starts from every
immediate-local clause that survives into a parent post-result P and contains a
component-spanning non-tail bridge whose tail and head components are both
singletons.  It follows that exact clause/literal occurrence through every
executed branch child and child pre-unit closure.

Child outcomes are classified as terminal/extinct, structurally nonbad,
canonically root-shielded, or an unsafe unshielded survivor.  The canonical
shield is independently replayed through the original N_a residual and a
parallel quotient edge; component sizes alone are not trusted.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_bad_bridge_birth_lifecycle import (
    endpoint_sizes,
    parent_source_classes,
)
from janus_tear_gt_bridge_endpoint_profile import bridge_record
from janus_tear_gt_component_merge_sources import reduce_clause
from janus_tear_gt_component_tree_clause_audit import (
    clause_component_graph,
    execution_context,
)
from janus_tear_gt_rank_safety_dichotomy import safety_class
from janus_tear_gt_root_unshielded_handoff_probe import canonical_root_shield
from janus_tear_gt_same_cut_parent_ancestry import root_minimum_labels
from janus_tear_gt_surviving_branch_frequency_profile import quotient_map, relation


def audit(n: int):
    context = execution_context(n)
    root = tuple(context["root"])
    policy = context["policy"]
    pairs = context["pairs"]
    levels = context["levels"]
    target = n - 2

    minimum_labels = root_minimum_labels(n, pairs)
    root_by_vertex = {
        vertex: clause
        for clause, vertex in minimum_labels.items()
    }
    assert set(root_by_vertex) == set(range(n))
    assert set(root_by_vertex.values()).issubset(set(root))

    counts: Counter[str] = Counter()
    parent_depths: Counter[int] = Counter()
    selected_relations: Counter[str] = Counter()
    child_fates: Counter[str] = Counter()
    shield_multiplicity: Counter[int] = Counter()
    rows = []

    for state in policy.states.values():
        if state["terminal"] not in ("BRANCH_UNSAT", "BRANCH_SAT"):
            continue
        call_id = int(state["entry_call"])
        novelty = int(levels[call_id])
        if novelty > target:
            continue

        parent_assignment = context["state_after_post"][int(state["id"])]
        post = tuple(tuple(clause) for clause in state["post_result"])
        selected = int(state["branch_var"])

        for clause in post:
            if "IMMEDIATE_LOCAL_RESOLVENT" not in parent_source_classes(
                state, clause
            ):
                continue
            parent_class = str(
                safety_class(n, clause, parent_assignment, pairs)["classification"]
            )
            if parent_class != "COMPONENT_SPANNING":
                continue
            parent_graph = clause_component_graph(
                n, clause, parent_assignment, pairs
            )
            vertex_component = quotient_map(parent_graph, n)

            for literal in clause:
                literal = int(literal)
                parent_bridge = bridge_record(
                    clause, parent_graph, pairs, literal
                )
                if parent_bridge is None or parent_bridge["role"] == "TAIL_SINGLETON":
                    continue
                sizes = endpoint_sizes(parent_graph, literal, pairs)
                if int(sizes["tail_size"]) != 1 or int(sizes["head_size"]) != 1:
                    continue

                counts["unshielded_parent_occurrences"] += 1
                depth = int(state["depth"])
                parent_depths[depth] += 1
                counts["root_parent_occurrences" if depth == 0 else "nonroot_parent_occurrences"] += 1

                selected_pair = pairs[selected]
                selected_relation = relation(
                    (
                        vertex_component[int(selected_pair[0])],
                        vertex_component[int(selected_pair[1])],
                    ),
                    int(sizes["tail_component"]),
                    int(sizes["head_component"]),
                )
                selected_relations[selected_relation] += 1

                child_rows = []
                for child in state["children"]:
                    value = bool(child["value"])
                    child_call_id = child["call"]
                    if child_call_id is None:
                        fate = "DIRECT_CONFLICT"
                        child_fates[fate] += 1
                        child_rows.append(
                            {
                                "value": value,
                                "call": None,
                                "fate": fate,
                                "residual": None,
                                "shield": None,
                            }
                        )
                        continue

                    child_call_id = int(child_call_id)
                    child_call = policy.calls[child_call_id]
                    child_key = child_call.get("key")
                    if child_key is None:
                        fate = str(child_call["terminal"])
                        child_fates[fate] += 1
                        child_rows.append(
                            {
                                "value": value,
                                "call": child_call_id,
                                "fate": fate,
                                "residual": None,
                                "shield": None,
                            }
                        )
                        continue

                    child_key = tuple(tuple(item) for item in child_key)
                    child_assignment = context["call_after_pre"][child_call_id]
                    residual = reduce_clause(clause, child_assignment)
                    shield = None
                    if residual is None or literal not in residual:
                        fate = "CLAUSE_EXTINCT"
                    elif residual not in child_key:
                        fate = "NOT_IN_CHILD_KEY"
                    else:
                        child_class = str(
                            safety_class(
                                n, residual, child_assignment, pairs
                            )["classification"]
                        )
                        if child_class != "COMPONENT_SPANNING":
                            fate = child_class
                        else:
                            child_graph = clause_component_graph(
                                n, residual, child_assignment, pairs
                            )
                            child_bridge = bridge_record(
                                residual, child_graph, pairs, literal
                            )
                            if child_bridge is None:
                                fate = "SPANNING_NONBRIDGE"
                            elif child_bridge["role"] == "TAIL_SINGLETON":
                                fate = "TAIL_SINGLETON_SAFE"
                            else:
                                shield = canonical_root_shield(
                                    n,
                                    root_by_vertex,
                                    child_key,
                                    child_assignment,
                                    pairs,
                                    residual,
                                    literal,
                                )
                                fate = (
                                    "CANONICALLY_SHIELDED"
                                    if shield is not None
                                    else "UNSAFE_UNSHIELDED_SURVIVES"
                                )

                    child_fates[fate] += 1
                    if fate == "CANONICALLY_SHIELDED":
                        counts["canonically_shielded_children"] += 1
                        shield_multiplicity[len(shield["parallel_literals"])] += 1
                    if fate == "UNSAFE_UNSHIELDED_SURVIVES":
                        counts["unsafe_unshielded_children"] += 1
                        if depth == 0:
                            counts["unsafe_root_children"] += 1
                        else:
                            counts["unsafe_nonroot_children"] += 1
                        if selected_relation == "DISJOINT":
                            counts["unsafe_disjoint_children"] += 1

                    child_rows.append(
                        {
                            "value": value,
                            "call": child_call_id,
                            "terminal": str(child_call["terminal"]),
                            "fate": fate,
                            "residual": residual,
                            "shield": shield,
                        }
                    )

                rows.append(
                    {
                        "n": n,
                        "state_id": int(state["id"]),
                        "call_id": call_id,
                        "depth": depth,
                        "novelty": novelty,
                        "selected": selected,
                        "selected_pair": selected_pair,
                        "selected_relation": selected_relation,
                        "clause": clause,
                        "literal": literal,
                        "tail_vertex": int(sizes["tail_vertex"]),
                        "head_vertex": int(sizes["head_vertex"]),
                        "children": tuple(child_rows),
                    }
                )

    assert counts["unsafe_unshielded_children"] == 0
    return {
        "n": n,
        "target": target,
        "counts": tuple(sorted(counts.items())),
        "parent_depths": tuple(sorted(parent_depths.items())),
        "selected_relations": tuple(sorted(selected_relations.items())),
        "child_fates": tuple(sorted(child_fates.items())),
        "shield_multiplicity": tuple(sorted(shield_multiplicity.items())),
        "rows": tuple(rows),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_depths: Counter[int] = Counter()
    aggregate_relations: Counter[str] = Counter()
    aggregate_fates: Counter[str] = Counter()
    aggregate_shields: Counter[int] = Counter()

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_depths.update(dict(data["parent_depths"]))
        aggregate_relations.update(dict(data["selected_relations"]))
        aggregate_fates.update(dict(data["child_fates"]))
        aggregate_shields.update(dict(data["shield_multiplicity"]))
        nonroot_rows = tuple(
            row for row in data["rows"] if row["depth"] > 0
        )
        print(f"ORDER_SIZE = {n}")
        print(f"  counts = {data['counts']}")
        print(f"  parent_depths = {data['parent_depths']}")
        print(f"  selected_relations = {data['selected_relations']}")
        print(f"  child_fates = {data['child_fates']}")
        print(f"  shield_multiplicity = {data['shield_multiplicity']}")
        print(f"  nonroot_rows = {nonroot_rows}")

    print("JANUS_GT_UNSHIELDED_BIRTH_HANDOFF_CENSUS = PASS")
    print(f"AGGREGATE_COUNTS = {tuple(sorted(aggregate_counts.items()))}")
    print(f"AGGREGATE_DEPTHS = {tuple(sorted(aggregate_depths.items()))}")
    print(f"AGGREGATE_RELATIONS = {tuple(sorted(aggregate_relations.items()))}")
    print(f"AGGREGATE_FATES = {tuple(sorted(aggregate_fates.items()))}")
    print(f"AGGREGATE_SHIELDS = {tuple(sorted(aggregate_shields.items()))}")
    print(
        "finite_result = every unshielded local clause/literal occurrence in P "
        "is terminal, extinct, structurally nonbad, or canonically shielded "
        "before the next exact key through GT_8"
    )
    print(
        "claim_boundary = exact finite all-birth handoff census; arbitrary-n "
        "nonroot extinction/shield theorem remains open"
    )


if __name__ == "__main__":
    self_test()
