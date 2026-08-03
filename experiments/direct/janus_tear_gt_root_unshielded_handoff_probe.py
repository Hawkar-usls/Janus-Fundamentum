#!/usr/bin/env python3
"""Probe exact root endpoint-or-shield-or-extinction handoff through GT_12.

This script executes only the deterministic root stages of Policy-0A:

    root unit closure -> frozen Resolution -> post-units -> selected branch.

Every immediate-local component-spanning bridge with singleton tail and
singleton head is followed through both branch polarities and child pre-unit
closure.  A surviving non-tail bridge is accepted only after independently
replaying the canonical root N_a shield: the residual root clause must be in the
child exact key, contain the complementary literal, remain spanning, and make
that complement a non-bridge via an explicit parallel quotient edge.

Orders 4..8 are regression-certified against the complete recursive trace.
Orders 9..12 are an exploratory exact root extension, not an asymptotic theorem.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_bad_bridge_birth_lifecycle import endpoint_sizes
from janus_tear_gt_bridge_endpoint_profile import bridge_record
from janus_tear_gt_component_merge_sources import reduce_clause
from janus_tear_gt_component_tree_clause_audit import clause_component_graph
from janus_tear_gt_critical_order_damage import pair_variables
from janus_tear_gt_global_clause_shrink_census import unit_assignments
from janus_tear_gt_rank_safety_dichotomy import safety_class
from janus_tear_gt_root_nonminimality_bridge_shield import original_direction
from janus_tear_gt_same_cut_parent_ancestry import root_minimum_labels
from janus_tear_gt_surviving_branch_frequency_profile import quotient_map, relation
from janus_tear_policy0a_graph_tautology_probe import graph_tautology_cnf
from janus_tear_policy0t_trace_certificate import (
    branch_variable,
    resolution_trace,
    simplify_one,
    unit_trace,
)


def root_stages(n: int):
    root, variable_count = graph_tautology_cnf(n)
    pairs = pair_variables(n)
    key, contradiction, pre_events = unit_trace(root)
    assert not contradiction and key is not None and not pre_events

    literal_count = sum(len(clause) for clause in key)
    width_limit = max(map(len, key)) + 1
    attempt_budget = max(64, 4 * literal_count)
    addition_budget = max(8, len(key) // 4)
    saturated, refuted, attempts, additions, events = resolution_trace(
        key,
        width_limit,
        attempt_budget,
        addition_budget,
    )
    assert not refuted
    post, contradiction, post_events = unit_trace(saturated)
    assert not contradiction and post is not None and post
    selected = branch_variable(post)
    return {
        "root": tuple(root),
        "pairs": pairs,
        "events": tuple(events),
        "post": tuple(post),
        "post_events": tuple(post_events),
        "post_assignment": unit_assignments(post_events),
        "selected": int(selected),
        "attempts": attempts,
        "additions": additions,
        "variable_count": variable_count,
    }


def canonical_root_shield(
    n: int,
    root_by_vertex,
    child_key,
    child_assignment,
    pairs,
    residual,
    literal: int,
):
    residual_graph = clause_component_graph(
        n, residual, child_assignment, pairs
    )
    residual_bridge = bridge_record(
        residual, residual_graph, pairs, literal
    )
    if residual_bridge is None:
        return None

    sizes = endpoint_sizes(residual_graph, literal, pairs)
    if int(sizes["tail_size"]) != 1 or int(sizes["head_size"]) < 2:
        return None

    tail_vertex, _head_vertex = original_direction(literal, pairs)
    root_clause = root_by_vertex[tail_vertex]
    root_residual = reduce_clause(root_clause, child_assignment)
    assert root_residual is not None
    assert root_residual in child_key
    assert -literal in root_residual
    root_class = str(
        safety_class(n, root_residual, child_assignment, pairs)["classification"]
    )
    assert root_class == "COMPONENT_SPANNING"
    root_graph = clause_component_graph(
        n, root_residual, child_assignment, pairs
    )
    assert bridge_record(root_residual, root_graph, pairs, -literal) is None

    vertex_component = quotient_map(root_graph, n)
    low, high = pairs[abs(literal)]
    pivot_edge = tuple(sorted((
        vertex_component[int(low)],
        vertex_component[int(high)],
    )))
    parallel_literals = tuple(sorted(
        int(edge_literal)
        for left, right, edge_literal in root_graph["external_edges"]
        if int(edge_literal) != -literal
        and tuple(sorted((int(left), int(right)))) == pivot_edge
    ))
    assert parallel_literals
    return {
        "root_clause": root_clause,
        "root_residual": root_residual,
        "parallel_literals": parallel_literals,
        "tail_size": int(sizes["tail_size"]),
        "head_size": int(sizes["head_size"]),
    }


def audit(n: int):
    data = root_stages(n)
    root = data["root"]
    pairs = data["pairs"]
    post = data["post"]
    selected = data["selected"]
    assignment = dict(data["post_assignment"])
    minimum_labels = root_minimum_labels(n, pairs)
    root_by_vertex = {
        vertex: clause
        for clause, vertex in minimum_labels.items()
    }
    assert set(root_by_vertex) == set(range(n))
    assert set(root_by_vertex.values()).issubset(set(root))

    local_antecedents = {
        tuple(event["resolvent"])
        for event in data["events"]
    }

    counts: Counter[str] = Counter()
    relation_histogram: Counter[str] = Counter()
    child_fates: Counter[str] = Counter()
    shield_multiplicity: Counter[int] = Counter()
    records = []

    for clause in post:
        local_sources = tuple(
            antecedent
            for antecedent in local_antecedents
            if reduce_clause(antecedent, assignment) == clause
        )
        if not local_sources:
            continue
        classification = str(
            safety_class(n, clause, assignment, pairs)["classification"]
        )
        if classification != "COMPONENT_SPANNING":
            continue
        graph = clause_component_graph(n, clause, assignment, pairs)
        vertex_component = quotient_map(graph, n)

        for literal in clause:
            literal = int(literal)
            bridge = bridge_record(clause, graph, pairs, literal)
            if bridge is None or bridge["role"] == "TAIL_SINGLETON":
                continue
            sizes = endpoint_sizes(graph, literal, pairs)
            if int(sizes["tail_size"]) != 1 or int(sizes["head_size"]) != 1:
                continue

            counts["unshielded_local_bridge_occurrences"] += 1
            tail_component = int(sizes["tail_component"])
            head_component = int(sizes["head_component"])
            selected_pair = pairs[selected]
            label = relation(
                (
                    vertex_component[int(selected_pair[0])],
                    vertex_component[int(selected_pair[1])],
                ),
                tail_component,
                head_component,
            )
            relation_histogram[label] += 1
            if label == "DISJOINT":
                counts["disjoint_selected_occurrences"] += 1
            else:
                counts["endpoint_selected_occurrences"] += 1

            fates = []
            for value in (False, True):
                child = simplify_one(post, selected, value)
                if child is None:
                    fate = "DIRECT_CONFLICT"
                    fates.append((value, fate, None, None))
                    child_fates[fate] += 1
                    continue

                child_key, child_contradiction, child_events = unit_trace(child)
                if child_contradiction:
                    fate = "PRE_UNIT_CONTRADICTION"
                    fates.append((value, fate, None, None))
                    child_fates[fate] += 1
                    continue
                assert child_key is not None
                if not child_key:
                    fate = "SAT_EMPTY_TERMINAL"
                    fates.append((value, fate, None, None))
                    child_fates[fate] += 1
                    continue

                child_assignment = dict(assignment)
                child_assignment[selected] = value
                child_assignment.update(unit_assignments(child_events))
                residual = reduce_clause(clause, child_assignment)
                shield = None
                if residual is None or literal not in residual:
                    fate = "CLAUSE_EXTINCT"
                elif residual not in child_key:
                    fate = "NOT_IN_CHILD_KEY"
                else:
                    residual_class = str(
                        safety_class(
                            n, residual, child_assignment, pairs
                        )["classification"]
                    )
                    if residual_class != "COMPONENT_SPANNING":
                        fate = residual_class
                    else:
                        residual_graph = clause_component_graph(
                            n, residual, child_assignment, pairs
                        )
                        residual_bridge = bridge_record(
                            residual, residual_graph, pairs, literal
                        )
                        if residual_bridge is None:
                            fate = "SPANNING_NONBRIDGE"
                        elif residual_bridge["role"] == "TAIL_SINGLETON":
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

                fates.append((value, fate, residual, shield))
                child_fates[fate] += 1
                if fate == "CANONICALLY_SHIELDED":
                    counts["canonically_shielded_descendants"] += 1
                    shield_multiplicity[len(shield["parallel_literals"])] += 1
                if fate == "UNSAFE_UNSHIELDED_SURVIVES":
                    counts["unsafe_child_descendants"] += 1
                    if label == "DISJOINT":
                        counts["disjoint_unsafe_child_descendants"] += 1

            records.append(
                {
                    "n": n,
                    "selected": selected,
                    "selected_pair": selected_pair,
                    "selected_relation": label,
                    "clause": clause,
                    "literal": literal,
                    "tail_vertex": int(sizes["tail_vertex"]),
                    "head_vertex": int(sizes["head_vertex"]),
                    "local_source_count": len(local_sources),
                    "fates": tuple(fates),
                }
            )

    if n <= 8:
        assert counts["unsafe_child_descendants"] == 0
        assert counts["disjoint_unsafe_child_descendants"] == 0
    return {
        "n": n,
        "root_clauses": len(root),
        "resolution_attempts": data["attempts"],
        "resolution_additions": data["additions"],
        "selected": selected,
        "selected_pair": pairs[selected],
        "counts": tuple(sorted(counts.items())),
        "relations": tuple(sorted(relation_histogram.items())),
        "child_fates": tuple(sorted(child_fates.items())),
        "shield_multiplicity": tuple(sorted(shield_multiplicity.items())),
        "records": tuple(records),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    first_disjoint = None
    first_unsafe_descendant = None
    first_disjoint_unsafe_descendant = None

    for n in range(4, 13):
        data = audit(n)
        row_counts = dict(data["counts"])
        aggregate_counts.update(row_counts)
        if row_counts.get("disjoint_selected_occurrences", 0):
            first_disjoint = first_disjoint or n
        if row_counts.get("unsafe_child_descendants", 0):
            first_unsafe_descendant = first_unsafe_descendant or n
        if row_counts.get("disjoint_unsafe_child_descendants", 0):
            first_disjoint_unsafe_descendant = (
                first_disjoint_unsafe_descendant or n
            )

        disjoint_records = tuple(
            record
            for record in data["records"]
            if record["selected_relation"] == "DISJOINT"
        )
        unsafe_records = tuple(
            record
            for record in data["records"]
            if any(
                fate == "UNSAFE_UNSHIELDED_SURVIVES"
                for _value, fate, _residual, _shield in record["fates"]
            )
        )
        print(f"ORDER_SIZE = {n}")
        print(f"  root_clauses = {data['root_clauses']}")
        print(f"  resolution_attempts = {data['resolution_attempts']}")
        print(f"  resolution_additions = {data['resolution_additions']}")
        print(f"  selected = {data['selected']} / pair {data['selected_pair']}")
        print(f"  counts = {data['counts']}")
        print(f"  relations = {data['relations']}")
        print(f"  child_fates = {data['child_fates']}")
        print(f"  shield_multiplicity = {data['shield_multiplicity']}")
        print(f"  disjoint_records = {disjoint_records[:8]}")
        print(f"  unsafe_records = {unsafe_records[:8]}")

    print("JANUS_GT_ROOT_UNSHIELDED_HANDOFF_PROBE = PASS")
    print(f"AGGREGATE_COUNTS = {tuple(sorted(aggregate_counts.items()))}")
    print(f"FIRST_DISJOINT_SELECTED_ORDER = {first_disjoint}")
    print(f"FIRST_UNSAFE_CHILD_DESCENDANT_ORDER = {first_unsafe_descendant}")
    print(
        "FIRST_DISJOINT_UNSAFE_CHILD_DESCENDANT_ORDER = "
        f"{first_disjoint_unsafe_descendant}"
    )
    print(
        "claim_boundary = exact root-only endpoint-or-shield-or-extinction "
        "probe through GT_12; no arbitrary-n root handoff theorem asserted"
    )


if __name__ == "__main__":
    self_test()
