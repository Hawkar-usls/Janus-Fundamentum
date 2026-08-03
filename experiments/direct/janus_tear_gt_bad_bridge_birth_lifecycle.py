#!/usr/bin/env python3
"""Trace the first birth mechanism of every pre-frontier non-tail bridge.

For each non-tail bridge occurrence in an exact child key, replay the actual
parent transition:

    parent post-result -> branch restriction -> child pre-units -> child key.

Every parent post-clause that reduces to the child clause is inspected at the
parent component quotient.  An occurrence is a first birth when none of its
parent sources already contains the same literal as a non-tail bridge.

The audit records whether birth coincides with a novel branch, whether child
pre-units were present, whether the clause was an immediate local resolvent of
the parent, and how the oriented endpoint component sizes changed.  It asserts
only the already certified singleton-tail/merged-head condition at the child;
the birth histogram is diagnostic finite evidence.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_bridge_endpoint_profile import bridge_record
from janus_tear_gt_component_merge_sources import reduce_clause
from janus_tear_gt_component_tree_clause_audit import (
    clause_component_graph,
    execution_context,
)
from janus_tear_gt_global_clause_shrink_census import unit_assignments
from janus_tear_gt_rank_safety_dichotomy import safety_class
from janus_tear_gt_root_nonminimality_bridge_shield import original_direction

Clause = tuple[int, ...]
EXPECTED_BAD = {4: 1, 5: 4, 6: 8, 7: 21, 8: 28}


def component_size_map(graph) -> tuple[dict[int, int], dict[int, int]]:
    vertex_component = {}
    sizes = {}
    for component_index, part in enumerate(graph["parts"]):
        sizes[int(component_index)] = len(part)
        for vertex in part:
            vertex_component[int(vertex)] = int(component_index)
    return vertex_component, sizes


def endpoint_sizes(graph, literal: int, pairs):
    vertex_component, sizes = component_size_map(graph)
    tail, head = original_direction(literal, pairs)
    tail_component = vertex_component[tail]
    head_component = vertex_component[head]
    return {
        "tail_vertex": tail,
        "head_vertex": head,
        "tail_component": tail_component,
        "head_component": head_component,
        "tail_size": sizes[tail_component],
        "head_size": sizes[head_component],
    }


def parent_map(policy):
    result = {}
    for state in policy.states.values():
        if state["terminal"] not in ("BRANCH_UNSAT", "BRANCH_SAT"):
            continue
        for child in state["children"]:
            if child["call"] is None:
                continue
            child_call = int(child["call"])
            assert child_call not in result
            result[child_call] = {
                "state_id": int(state["id"]),
                "parent_call": int(state["entry_call"]),
                "branch_literal": int(child["literal"]),
            }
            if child["result"]:
                break
    return result


def parent_source_classes(state, source_clause: Clause) -> tuple[str, ...]:
    post_assignment = unit_assignments(state.get("post_units", []))
    local_resolvents = {
        tuple(event["resolvent"])
        for event in state.get("resolution_events", [])
    }
    labels = set()
    for antecedent in tuple(state["resolution_output"]):
        if reduce_clause(tuple(antecedent), post_assignment) != source_clause:
            continue
        antecedent = tuple(antecedent)
        if antecedent in local_resolvents:
            labels.add("IMMEDIATE_LOCAL_RESOLVENT")
        elif antecedent in tuple(state["key"]):
            labels.add("INHERITED_KEY")
        else:
            labels.add("OTHER_OUTPUT")
    return tuple(sorted(labels or {"UNCLASSIFIED"}))


def audit(n: int):
    context = execution_context(n)
    policy = context["policy"]
    pairs = context["pairs"]
    levels = context["levels"]
    target = n - 2
    parents = parent_map(policy)

    counts: Counter[str] = Counter()
    birth_mechanisms: Counter[tuple[str, ...]] = Counter()
    novelty_histogram: Counter[int] = Counter()
    source_role_histogram: Counter[str] = Counter()
    source_class_histogram: Counter[tuple[str, ...]] = Counter()
    size_transition_histogram: Counter[tuple[int, int, int, int]] = Counter()
    first_birth_examples = []

    for state in policy.states.values():
        call_id = int(state["entry_call"])
        novelty = int(levels[call_id])
        if novelty > target:
            continue
        child_assignment = context["call_after_pre"][call_id]
        child_key = tuple(state["key"])
        child_graphs = {
            clause: clause_component_graph(n, clause, child_assignment, pairs)
            for clause in child_key
        }
        child_classes = {
            clause: str(safety_class(n, clause, child_assignment, pairs)["classification"])
            for clause in child_key
        }

        for clause in child_key:
            if child_classes[clause] != "COMPONENT_SPANNING":
                continue
            for literal in clause:
                literal = int(literal)
                child_bridge = bridge_record(clause, child_graphs[clause], pairs, literal)
                if child_bridge is None or child_bridge["role"] == "TAIL_SINGLETON":
                    continue

                counts["bad_occurrences"] += 1
                child_sizes = endpoint_sizes(child_graphs[clause], literal, pairs)
                assert child_sizes["tail_size"] == 1
                assert child_sizes["head_size"] >= 2

                assert call_id in parents
                edge = parents[call_id]
                parent_state = policy.states[int(edge["state_id"])]
                parent_call = int(edge["parent_call"])
                parent_level = int(levels[parent_call])
                novelty_increment = novelty - parent_level
                assert novelty_increment in (0, 1)
                parent_assignment = context["state_after_post"][int(edge["state_id"])]
                parent_post = tuple(tuple(item) for item in parent_state["post_result"])

                sources = [
                    source
                    for source in parent_post
                    if literal in source
                    and reduce_clause(source, child_assignment) == clause
                ]
                assert sources, (n, call_id, clause, literal, edge)

                source_records = []
                preexisting_bad = False
                for source in sources:
                    source_graph = clause_component_graph(
                        n, source, parent_assignment, pairs
                    )
                    source_class = str(
                        safety_class(n, source, parent_assignment, pairs)["classification"]
                    )
                    source_bridge = (
                        bridge_record(source, source_graph, pairs, literal)
                        if source_class == "COMPONENT_SPANNING"
                        else None
                    )
                    if source_bridge is None:
                        source_role = "NOT_SPANNING_BRIDGE"
                    else:
                        source_role = str(source_bridge["role"])
                        if source_role != "TAIL_SINGLETON":
                            preexisting_bad = True
                    source_role_histogram[source_role] += 1
                    source_classes = parent_source_classes(parent_state, source)
                    source_class_histogram[source_classes] += 1
                    source_sizes = endpoint_sizes(source_graph, literal, pairs)
                    source_records.append({
                        "source": source,
                        "class": source_class,
                        "bridge_role": source_role,
                        "source_classes": source_classes,
                        "sizes": source_sizes,
                        "width_drop": len(source) - len(clause),
                    })

                if preexisting_bad:
                    counts["inherited_bad_occurrences"] += 1
                    continue

                counts["first_birth_occurrences"] += 1
                child_pre_units = tuple(policy.calls[call_id].get("pre_units", []))
                source_label_union = tuple(sorted({
                    label
                    for record in source_records
                    for label in record["source_classes"]
                }))
                mechanism = (
                    "NOVEL_BRANCH" if novelty_increment else "NONNOVEL_BRANCH",
                    "WITH_PRE_UNITS" if child_pre_units else "NO_PRE_UNITS",
                    *source_label_union,
                )
                birth_mechanisms[mechanism] += 1
                novelty_histogram[novelty_increment] += 1

                for record in source_records:
                    source_sizes = record["sizes"]
                    size_transition_histogram[(
                        int(source_sizes["tail_size"]),
                        int(source_sizes["head_size"]),
                        int(child_sizes["tail_size"]),
                        int(child_sizes["head_size"]),
                    )] += 1

                if len(first_birth_examples) < 100:
                    first_birth_examples.append({
                        "n": n,
                        "child_call": call_id,
                        "child_state": int(state["id"]),
                        "parent_call": parent_call,
                        "parent_state": int(edge["state_id"]),
                        "parent_novelty": parent_level,
                        "child_novelty": novelty,
                        "novelty_increment": novelty_increment,
                        "branch_literal": int(edge["branch_literal"]),
                        "child_pre_units": child_pre_units,
                        "clause": clause,
                        "literal": literal,
                        "child_role": str(child_bridge["role"]),
                        "child_sizes": child_sizes,
                        "sources": tuple(source_records),
                        "mechanism": mechanism,
                    })

    expected = EXPECTED_BAD[n]
    assert counts["bad_occurrences"] == expected
    assert counts["first_birth_occurrences"] + counts["inherited_bad_occurrences"] == expected
    return {
        "n": n,
        "target": target,
        "counts": tuple(sorted(counts.items())),
        "birth_mechanisms": tuple(sorted(birth_mechanisms.items(), key=repr)),
        "novelty_histogram": tuple(sorted(novelty_histogram.items())),
        "source_role_histogram": tuple(sorted(source_role_histogram.items())),
        "source_class_histogram": tuple(sorted(source_class_histogram.items(), key=repr)),
        "size_transition_histogram": tuple(sorted(size_transition_histogram.items())),
        "first_birth_examples": tuple(first_birth_examples),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_mechanisms: Counter[tuple[str, ...]] = Counter()
    aggregate_novelty: Counter[int] = Counter()
    aggregate_roles: Counter[str] = Counter()
    aggregate_sources: Counter[tuple[str, ...]] = Counter()
    aggregate_sizes: Counter[tuple[int, int, int, int]] = Counter()

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_mechanisms.update(dict(data["birth_mechanisms"]))
        aggregate_novelty.update(dict(data["novelty_histogram"]))
        aggregate_roles.update(dict(data["source_role_histogram"]))
        aggregate_sources.update(dict(data["source_class_histogram"]))
        aggregate_sizes.update(dict(data["size_transition_histogram"]))
        print(f"ORDER_SIZE = {n}")
        print(f"  counts = {data['counts']}")
        print(f"  birth_mechanisms = {data['birth_mechanisms']}")
        print(f"  novelty_histogram = {data['novelty_histogram']}")
        print(f"  source_role_histogram = {data['source_role_histogram']}")
        print(f"  source_class_histogram = {data['source_class_histogram']}")
        print(f"  size_transition_histogram = {data['size_transition_histogram']}")
        print(f"  first_birth_examples = {data['first_birth_examples']}")

    assert aggregate_counts["bad_occurrences"] == 62
    assert aggregate_counts["first_birth_occurrences"] + aggregate_counts["inherited_bad_occurrences"] == 62
    print("JANUS_GT_BAD_BRIDGE_BIRTH_LIFECYCLE = PASS")
    print(f"aggregate_counts = {tuple(sorted(aggregate_counts.items()))}")
    print(f"aggregate_birth_mechanisms = {tuple(sorted(aggregate_mechanisms.items(), key=repr))}")
    print(f"aggregate_novelty_histogram = {tuple(sorted(aggregate_novelty.items()))}")
    print(f"aggregate_source_roles = {tuple(sorted(aggregate_roles.items()))}")
    print(f"aggregate_source_classes = {tuple(sorted(aggregate_sources.items(), key=repr))}")
    print(f"aggregate_size_transitions = {tuple(sorted(aggregate_sizes.items()))}")
    print(
        "claim_boundary = finite first-birth lifecycle through GT_8; "
        "arbitrary-n birth lemma remains open"
    )


if __name__ == "__main__":
    self_test()
