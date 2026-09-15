#!/usr/bin/env python3
"""Profile the exact bridge-cut geometry of pre-frontier GT residual clauses.

The previous same-cut audit found no same-cut double-bridge pair through GT_8.
That makes the earlier directed-cycle statement vacuous on the observed traces.
This checker searches for the stronger per-parent structure that could explain
why equal cuts never arise.

For every component-spanning clause in every pre-frontier exact cache key it:

1. finds every literal whose component edge is a bridge;
2. removes that edge and classifies the induced bipartition relative to the
   directed tail/head of the literal;
3. classifies every complementary double-bridge parent pair by the two bridge
   roles and verifies that their cuts differ.

The endpoint-role census is exploratory finite evidence.  Only consistency and
the already observed absence of same-cut pairs are asserted.
"""

from __future__ import annotations

from collections import Counter, defaultdict

from janus_tear_gt_component_tree_clause_audit import (
    DSU,
    clause_component_graph,
    execution_context,
)
from janus_tear_gt_directed_component_clause_audit import (
    directed_edges,
    orientation_class,
)
from janus_tear_gt_rank_safety_dichotomy import safety_class
from janus_tear_gt_same_cut_pivot_audit import canonical_cut


def graph_rank(component_count: int, edges) -> int:
    dsu = DSU(component_count)
    for left, right in edges:
        dsu.union(int(left), int(right))
    return component_count - len(
        {dsu.find(vertex) for vertex in range(component_count)}
    )


def bridge_record(clause, graph, pairs, literal):
    component_count = int(graph["component_count"])
    external = tuple(
        (int(left), int(right), int(edge_literal))
        for left, right, edge_literal in graph["external_edges"]
    )
    before_rank = graph_rank(
        component_count, tuple((left, right) for left, right, _ in external)
    )
    remainder = tuple(
        (left, right)
        for left, right, edge_literal in external
        if edge_literal != literal
    )
    after_rank = graph_rank(component_count, remainder)
    if after_rank != before_rank - 1:
        return None

    cut = canonical_cut(component_count, remainder)
    assert cut is not None
    directed = {
        int(edge_literal): (int(tail), int(head))
        for tail, head, edge_literal in directed_edges(clause, graph, pairs)[0]
    }
    tail, head = directed[literal]
    left, right = cut

    if len(left) == 1 and len(right) == 1:
        role = "BOTH_ENDPOINTS_SINGLETON" if {left[0], right[0]} == {tail, head} else "BOTH_SINGLETON_OTHER"
        isolated = tuple(sorted((left[0], right[0])))
    elif len(left) == 1:
        isolated = (left[0],)
        if left[0] == tail:
            role = "TAIL_SINGLETON"
        elif left[0] == head:
            role = "HEAD_SINGLETON"
        else:
            role = "OTHER_SINGLETON"
    elif len(right) == 1:
        isolated = (right[0],)
        if right[0] == tail:
            role = "TAIL_SINGLETON"
        elif right[0] == head:
            role = "HEAD_SINGLETON"
        else:
            role = "OTHER_SINGLETON"
    else:
        isolated = ()
        role = "NON_SINGLETON_CUT"

    return {
        "literal": literal,
        "tail": tail,
        "head": head,
        "cut": cut,
        "role": role,
        "isolated": isolated,
        "before_rank": before_rank,
        "after_rank": after_rank,
    }


def audit(n: int):
    context = execution_context(n)
    policy = context["policy"]
    pairs = context["pairs"]
    levels = context["levels"]
    target = n - 2

    bridge_roles: Counter[str] = Counter()
    bridge_orientation_roles: Counter[tuple[str, str]] = Counter()
    pair_roles: Counter[tuple[str, str]] = Counter()
    pair_orientation_roles: Counter[tuple[str, str, str, str]] = Counter()
    counts: Counter[str] = Counter()
    examples = []

    for state in policy.states.values():
        call_id = int(state["entry_call"])
        novelty = int(levels[call_id])
        if novelty > target:
            continue
        assignment = context["call_after_pre"][call_id]
        key = tuple(state["key"])

        graphs = {
            clause: clause_component_graph(n, clause, assignment, pairs)
            for clause in key
        }
        classes = {
            clause: str(safety_class(n, clause, assignment, pairs)["classification"])
            for clause in key
        }
        orientations = {
            clause: str(orientation_class(clause, graphs[clause], pairs)["classification"])
            for clause in key
        }
        bridge_by_clause = {}

        for clause in key:
            if classes[clause] != "COMPONENT_SPANNING":
                continue
            counts["spanning_clause_occurrences"] += 1
            records = {}
            for literal in clause:
                record = bridge_record(clause, graphs[clause], pairs, int(literal))
                if record is None:
                    continue
                records[int(literal)] = record
                bridge_roles[str(record["role"])] += 1
                bridge_orientation_roles[(orientations[clause], str(record["role"]))] += 1
                counts["spanning_bridge_literals"] += 1
            bridge_by_clause[clause] = records

        positive: dict[int, list[tuple[int, ...]]] = defaultdict(list)
        negative: dict[int, list[tuple[int, ...]]] = defaultdict(list)
        for clause in key:
            if classes[clause] != "COMPONENT_SPANNING":
                continue
            for literal in clause:
                (positive if literal > 0 else negative)[abs(literal)].append(clause)

        for pivot in sorted(set(positive) & set(negative)):
            for left in positive[pivot]:
                for right in negative[pivot]:
                    left_record = bridge_by_clause.get(left, {}).get(pivot)
                    right_record = bridge_by_clause.get(right, {}).get(-pivot)
                    if left_record is None or right_record is None:
                        continue
                    counts["double_bridge_pairs"] += 1
                    left_role = str(left_record["role"])
                    right_role = str(right_record["role"])
                    pair_roles[(left_role, right_role)] += 1
                    pair_orientation_roles[(
                        orientations[left], left_role,
                        orientations[right], right_role,
                    )] += 1
                    same_cut = left_record["cut"] == right_record["cut"]
                    counts["same_cut_pairs" if same_cut else "different_cut_pairs"] += 1
                    if len(examples) < 40:
                        examples.append({
                            "n": n,
                            "state_id": int(state["id"]),
                            "call_id": call_id,
                            "novelty": novelty,
                            "pivot": pivot,
                            "left": left,
                            "right": right,
                            "left_orientation": orientations[left],
                            "right_orientation": orientations[right],
                            "left_bridge": left_record,
                            "right_bridge": right_record,
                            "same_cut": same_cut,
                        })

    assert counts["same_cut_pairs"] == 0
    assert counts["double_bridge_pairs"] == counts["different_cut_pairs"]
    return {
        "n": n,
        "target": target,
        "counts": tuple(sorted(counts.items())),
        "bridge_roles": tuple(sorted(bridge_roles.items())),
        "bridge_orientation_roles": tuple(sorted(bridge_orientation_roles.items())),
        "pair_roles": tuple(sorted(pair_roles.items())),
        "pair_orientation_roles": tuple(sorted(pair_orientation_roles.items())),
        "examples": tuple(examples),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_bridge_roles: Counter[str] = Counter()
    aggregate_bridge_orientation_roles: Counter[tuple[str, str]] = Counter()
    aggregate_pair_roles: Counter[tuple[str, str]] = Counter()
    aggregate_pair_orientation_roles: Counter[tuple[str, str, str, str]] = Counter()

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_bridge_roles.update(dict(data["bridge_roles"]))
        aggregate_bridge_orientation_roles.update(dict(data["bridge_orientation_roles"]))
        aggregate_pair_roles.update(dict(data["pair_roles"]))
        aggregate_pair_orientation_roles.update(dict(data["pair_orientation_roles"]))
        print(f"ORDER_SIZE = {n}")
        print(f"  target = {data['target']}")
        print(f"  counts = {data['counts']}")
        print(f"  bridge_roles = {data['bridge_roles']}")
        print(f"  bridge_orientation_roles = {data['bridge_orientation_roles']}")
        print(f"  pair_roles = {data['pair_roles']}")
        print(f"  pair_orientation_roles = {data['pair_orientation_roles']}")
        print(f"  examples = {data['examples']}")

    print("JANUS_GT_BRIDGE_ENDPOINT_PROFILE = PASS")
    print(f"aggregate_counts = {tuple(sorted(aggregate_counts.items()))}")
    print(f"aggregate_bridge_roles = {tuple(sorted(aggregate_bridge_roles.items()))}")
    print(f"aggregate_bridge_orientation_roles = {tuple(sorted(aggregate_bridge_orientation_roles.items()))}")
    print(f"aggregate_pair_roles = {tuple(sorted(aggregate_pair_roles.items()))}")
    print(f"aggregate_pair_orientation_roles = {tuple(sorted(aggregate_pair_orientation_roles.items()))}")
    print("claim_boundary = finite endpoint-role census through GT_8; inductive closure remains open")


if __name__ == "__main__":
    self_test()
