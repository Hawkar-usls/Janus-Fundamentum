#!/usr/bin/env python3
"""Test the component-spanning-tree criterion for frontier-dangerous clauses.

A clause literal x_(u,v) is viewed as an undirected edge between the current
Hasse components containing u and v.  The refined C024 hypothesis predicts that
a local resolvent capable of becoming a component-joining unit at the first
historical frontier is a spanning tree on the current components.  Falsifying a
literal contracts one tree edge, and the residual clause remains a spanning tree
on the contracted components.

This audit performs three independent checks for GT_4..GT_8:

1. every certified pre-unit provenance origin is a component-spanning tree;
2. every certified branch reduction contracts one tree edge and preserves the
   tree predicate;
3. among all immediate local resolvents created before novelty level n-2, no
   spanning-tree resolvent is strictly narrowed by a nonnovel branch.

The third check replaces the retrospective label “eventually dangerous” with a
structural over-approximation.  A failure is reported as a finite falsification,
not hidden behind an assertion.  Certified dangerous-path failures remain hard
assertions because they would contradict the existing provenance certificate.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_component_merge_sources import audit as merge_source_audit, reduce_clause
from janus_tear_gt_critical_order_damage import pair_variables
from janus_tear_gt_novel_branch_audit_v2 import add_units, comparison_closure, components
from janus_tear_gt_pre_unit_recursive_provenance import audit as provenance_audit
from janus_tear_policy0a_fc_trace import FCTracePolicy, verify_fc_trace
from janus_tear_policy0a_graph_tautology_probe import graph_tautology_cnf

Clause = tuple[int, ...]


class DSU:
    def __init__(self, size: int) -> None:
        self.parent = list(range(size))

    def find(self, item: int) -> int:
        while self.parent[item] != item:
            self.parent[item] = self.parent[self.parent[item]]
            item = self.parent[item]
        return item

    def union(self, left: int, right: int) -> bool:
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root == right_root:
            return False
        self.parent[right_root] = left_root
        return True


def unit_assignments(events) -> dict[int, bool]:
    result: dict[int, bool] = {}
    for event in events:
        if event["kind"] != "unit":
            continue
        literal = int(event["literal"])
        result[abs(literal)] = literal > 0
    return result


def clause_component_graph(
    n: int,
    clause: Clause,
    assignment: dict[int, bool],
    pairs: dict[int, tuple[int, int]],
) -> dict[str, object]:
    closure = comparison_closure(n, assignment, pairs)
    assert closure.acyclic
    parts = components(closure)
    index = {
        vertex: component_index
        for component_index, component in enumerate(parts)
        for vertex in component
    }

    dsu = DSU(len(parts))
    internal_literals = []
    external_edges = []
    cycle_edges = []
    touched = set()

    for literal in clause:
        left, right = pairs[abs(literal)]
        left_component = index[left]
        right_component = index[right]
        if left_component == right_component:
            internal_literals.append(literal)
            continue
        edge = (left_component, right_component, literal)
        external_edges.append(edge)
        touched.update((left_component, right_component))
        if not dsu.union(left_component, right_component):
            cycle_edges.append(edge)

    roots = {dsu.find(component) for component in range(len(parts))}
    connected = len(roots) == 1
    acyclic_edges = not cycle_edges
    all_external = not internal_literals
    spanning_tree = (
        all_external
        and acyclic_edges
        and connected
        and len(external_edges) == len(parts) - 1
    )

    if spanning_tree:
        classification = "SPANNING_TREE"
    elif internal_literals:
        classification = "HAS_INTERNAL_LITERAL"
    elif cycle_edges:
        classification = "EXTERNAL_CYCLE"
    elif acyclic_edges:
        classification = "EXTERNAL_FOREST"
    else:
        classification = "OTHER"

    return {
        "component_count": len(parts),
        "parts": parts,
        "clause_width": len(clause),
        "internal_literals": tuple(internal_literals),
        "external_edges": tuple(external_edges),
        "cycle_edges": tuple(cycle_edges),
        "touched_components": tuple(sorted(touched)),
        "connected": connected,
        "spanning_tree": spanning_tree,
        "classification": classification,
    }


def execution_context(n: int):
    root, variable_count = graph_tautology_cnf(n)
    pairs = pair_variables(n)
    policy = FCTracePolicy()
    result, root_call = policy.solve(root, variable_count)
    assert result.answer is False and root_call is not None
    assert verify_fc_trace(root, variable_count, policy, root_call) is False

    call_incoming: dict[int, dict[int, bool]] = {}
    call_after_pre: dict[int, dict[int, bool]] = {}
    state_after_post: dict[int, dict[int, bool]] = {}
    levels: dict[int, int] = {}
    seen: set[int] = set()

    def walk(call_id: int, incoming: dict[int, bool], novelty: int) -> None:
        assert call_id not in seen
        seen.add(call_id)
        call_incoming[call_id] = dict(incoming)
        levels[call_id] = novelty
        call = policy.calls[call_id]
        after_pre, _, _ = add_units(incoming, call.get("pre_units", []))
        call_after_pre[call_id] = dict(after_pre)
        if call["terminal"] != "STATE":
            return

        state_id = int(call["state"])
        state = policy.states[state_id]
        after_post, _, _ = add_units(after_pre, state.get("post_units", []))
        state_after_post[state_id] = dict(after_post)
        if state["terminal"] not in ("BRANCH_UNSAT", "BRANCH_SAT"):
            return

        variable = int(state["branch_var"])
        left, right = pairs[variable]
        closure = comparison_closure(n, after_post, pairs)
        parts = components(closure)
        index = {
            vertex: component_index
            for component_index, component in enumerate(parts)
            for vertex in component
        }
        increment = int(index[left] != index[right])

        for child in state["children"]:
            if child["call"] is None:
                continue
            value = bool(child["value"])
            child_assignment = dict(after_post)
            child_assignment[variable] = value
            walk(int(child["call"]), child_assignment, novelty + increment)
            if child["result"]:
                break

    walk(root_call, {}, 0)
    assert len(seen) == len(policy.calls)
    return {
        "root": root,
        "variable_count": variable_count,
        "pairs": pairs,
        "policy": policy,
        "result": result,
        "root_call": root_call,
        "call_incoming": call_incoming,
        "call_after_pre": call_after_pre,
        "state_after_post": state_after_post,
        "levels": levels,
    }


def audit(n: int):
    context = execution_context(n)
    pairs = context["pairs"]
    policy = context["policy"]
    levels = context["levels"]
    target = n - 2

    edge_by_literal: dict[tuple[int, int], int] = {}
    for state in policy.states.values():
        if state["terminal"] not in ("BRANCH_UNSAT", "BRANCH_SAT"):
            continue
        parent_call = int(state["entry_call"])
        for child in state["children"]:
            if child["call"] is None:
                continue
            edge_by_literal[(parent_call, int(child["literal"]))] = int(child["call"])

    provenance = provenance_audit(n)
    dangerous_origins = []
    dangerous_contractions = []

    for merge in provenance["records"]:
        assert merge["all_path_count"] == 1
        path = merge["shortest_paths"][0]
        origin_clause = tuple(path["origin_clause"])
        origin_event = path["origin_event"]
        assert origin_event is not None
        origin_state = int(origin_event["state_id"])
        origin_call = int(policy.states[origin_state]["entry_call"])
        origin_assignment = context["call_after_pre"][origin_call]
        origin_graph = clause_component_graph(
            n, origin_clause, origin_assignment, pairs
        )
        assert origin_graph["spanning_tree"], (
            n,
            merge["child_call_id"],
            origin_clause,
            origin_graph,
        )
        assert origin_graph["component_count"] == len(origin_clause) + 1
        dangerous_origins.append(
            {
                "child_call_id": int(merge["child_call_id"]),
                "origin_call_id": origin_call,
                "origin_state_id": origin_state,
                "origin_clause": origin_clause,
                "origin_novelty": levels[origin_call],
                "graph": origin_graph,
            }
        )

        for step in path["steps"]:
            if step["kind"] not in ("BRANCH_REDUCTION", "FINAL_BRANCH_TO_UNIT"):
                continue
            parent_call = int(step["parent_call_id"])
            parent_state = int(step["parent_state_id"])
            branch_literal = int(step["branch_literal"])
            child_call = edge_by_literal[(parent_call, branch_literal)]
            from_clause = tuple(step["from_clause"])
            to_clause = tuple(step["to_clause"])
            before_assignment = context["state_after_post"][parent_state]
            after_assignment = dict(before_assignment)
            after_assignment[abs(branch_literal)] = branch_literal > 0

            before_graph = clause_component_graph(
                n, from_clause, before_assignment, pairs
            )
            after_graph = clause_component_graph(
                n, to_clause, after_assignment, pairs
            )
            assert before_graph["spanning_tree"]
            assert after_graph["spanning_tree"]
            assert before_graph["component_count"] == after_graph["component_count"] + 1
            assert len(from_clause) == len(to_clause) + 1
            assert levels[child_call] == levels[parent_call] + 1
            dangerous_contractions.append(
                {
                    "parent_call": parent_call,
                    "child_call": child_call,
                    "branch_literal": branch_literal,
                    "from_clause": from_clause,
                    "to_clause": to_clause,
                    "before_components": before_graph["component_count"],
                    "after_components": after_graph["component_count"],
                }
            )

    merge_sources = merge_source_audit(n)
    direct_post_trees = []
    for record in merge_sources["records"]:
        if record["stage"] != "post":
            continue
        state_id = int(record["state_id"])
        call_id = int(policy.states[state_id]["entry_call"])
        unit_clause = (int(record["literal"]),)
        graph = clause_component_graph(
            n, unit_clause, context["call_after_pre"][call_id], pairs
        )
        assert graph["spanning_tree"]
        assert graph["component_count"] == 2
        direct_post_trees.append(
            {
                "call_id": call_id,
                "state_id": state_id,
                "unit_clause": unit_clause,
                "graph": graph,
            }
        )

    local_classification: Counter[str] = Counter()
    spanning_tree_resolvents = 0
    spanning_tree_post_unit_width_drops = 0
    spanning_tree_branch_shrinks = 0
    spanning_tree_nonnovel_shrinks = 0
    spanning_tree_nonnovel_examples = []

    for state in policy.states.values():
        call_id = int(state["entry_call"])
        if levels[call_id] >= target:
            continue
        create_assignment = context["call_after_pre"][call_id]
        post_assignment = unit_assignments(state.get("post_units", []))

        for event in state.get("resolution_events", []):
            clause = tuple(event["resolvent"])
            graph = clause_component_graph(n, clause, create_assignment, pairs)
            local_classification[str(graph["classification"])] += 1
            if not graph["spanning_tree"]:
                continue
            spanning_tree_resolvents += 1
            post_clause = reduce_clause(clause, post_assignment)
            if post_clause is None:
                continue
            if len(post_clause) < len(clause):
                spanning_tree_post_unit_width_drops += 1

            for child in state.get("children", []):
                if child["call"] is None:
                    continue
                child_call = int(child["call"])
                branch_literal = int(child["literal"])
                residual = reduce_clause(
                    post_clause,
                    {abs(branch_literal): branch_literal > 0},
                )
                if residual is None or len(residual) >= len(post_clause):
                    continue
                spanning_tree_branch_shrinks += 1
                increment = levels[child_call] - levels[call_id]
                assert increment in (0, 1)
                if increment == 0:
                    spanning_tree_nonnovel_shrinks += 1
                    if len(spanning_tree_nonnovel_examples) < 10:
                        spanning_tree_nonnovel_examples.append(
                            {
                                "call_id": call_id,
                                "child_call": child_call,
                                "novelty": levels[call_id],
                                "branch_literal": branch_literal,
                                "origin_clause": clause,
                                "post_clause": post_clause,
                                "residual": residual,
                                "origin_graph": graph,
                            }
                        )
                if child["result"]:
                    break

    structural_status = (
        "FALSIFIED_BY_SPANNING_TREE_NONNOVEL_SHRINK"
        if spanning_tree_nonnovel_shrinks
        else "SURVIVED_FINITE_CENSUS"
    )

    return {
        "n": n,
        "target": target,
        "dangerous_origin_count": len(dangerous_origins),
        "dangerous_contraction_count": len(dangerous_contractions),
        "direct_post_tree_count": len(direct_post_trees),
        "local_classification": tuple(sorted(local_classification.items())),
        "spanning_tree_resolvents": spanning_tree_resolvents,
        "spanning_tree_post_unit_width_drops": spanning_tree_post_unit_width_drops,
        "spanning_tree_branch_shrinks": spanning_tree_branch_shrinks,
        "spanning_tree_nonnovel_shrinks": spanning_tree_nonnovel_shrinks,
        "structural_status": structural_status,
        "dangerous_origins": tuple(dangerous_origins),
        "dangerous_contractions": tuple(dangerous_contractions),
        "direct_post_trees": tuple(direct_post_trees),
        "spanning_tree_nonnovel_examples": tuple(spanning_tree_nonnovel_examples),
    }


def self_test() -> None:
    rows = []
    aggregate_classification: Counter[str] = Counter()
    failures = []
    for n in range(4, 9):
        data = audit(n)
        aggregate_classification.update(dict(data["local_classification"]))
        if data["structural_status"].startswith("FALSIFIED"):
            failures.append(n)
        rows.append(
            (
                n,
                data["target"],
                data["dangerous_origin_count"],
                data["dangerous_contraction_count"],
                data["direct_post_tree_count"],
                data["spanning_tree_resolvents"],
                data["spanning_tree_branch_shrinks"],
                data["spanning_tree_nonnovel_shrinks"],
                data["structural_status"],
            )
        )
        print(f"ORDER_SIZE = {n}")
        print(f"  target = {data['target']}")
        print(f"  dangerous_origin_count = {data['dangerous_origin_count']}")
        print(f"  dangerous_contraction_count = {data['dangerous_contraction_count']}")
        print(f"  direct_post_tree_count = {data['direct_post_tree_count']}")
        print(f"  local_classification = {data['local_classification']}")
        print(f"  spanning_tree_resolvents = {data['spanning_tree_resolvents']}")
        print(
            "  spanning_tree_post_unit_width_drops = "
            f"{data['spanning_tree_post_unit_width_drops']}"
        )
        print(f"  spanning_tree_branch_shrinks = {data['spanning_tree_branch_shrinks']}")
        print(
            "  spanning_tree_nonnovel_shrinks = "
            f"{data['spanning_tree_nonnovel_shrinks']}"
        )
        print(f"  structural_status = {data['structural_status']}")
        print(f"  spanning_tree_nonnovel_examples = {data['spanning_tree_nonnovel_examples']}")

    print("JANUS_GT_COMPONENT_TREE_CLAUSE_AUDIT = PASS")
    print(f"rows = {tuple(rows)}")
    print(f"aggregate_classification = {tuple(sorted(aggregate_classification.items()))}")
    print(f"structural_failures = {tuple(failures)}")
    print("claim_boundary = finite structural audit; spanning-tree necessity for every asymptotically dangerous resolvent remains unproved")


if __name__ == "__main__":
    self_test()
