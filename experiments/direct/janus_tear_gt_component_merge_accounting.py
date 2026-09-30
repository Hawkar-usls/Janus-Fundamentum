#!/usr/bin/env python3
"""Account graph-tautology component merges by each Policy-0A resource.

The historical Formula-Caching proof charges a novel branch when it compares two
vertices from different components of the current partial order.  Policy-0A may
also gain comparison assignments through unit propagation, including units made
available by its one-pass local Resolution rule.

This audit separates component reductions caused by:

- pre-state unit propagation inherited from the child residual;
- post-local-Resolution unit propagation inside the completed state;
- the explicit branch comparison itself.

A component reduction is a finite diagnostic, not proof that the historical
novelty measure has been preserved or violated asymptotically.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_critical_order_damage import pair_variables
from janus_tear_gt_novel_branch_audit_v2 import (
    add_units,
    comparison_closure,
    components,
)
from janus_tear_policy0a_fc_trace import FCTracePolicy, verify_fc_trace
from janus_tear_policy0a_graph_tautology_probe import graph_tautology_cnf


def component_count(n: int, assignment, pairs) -> tuple[int, bool]:
    closure = comparison_closure(n, assignment, pairs)
    return len(components(closure)), closure.acyclic


def audit(n: int):
    cnf, variable_count = graph_tautology_cnf(n)
    pairs = pair_variables(n)
    policy = FCTracePolicy()
    result, root_call = policy.solve(cnf, variable_count)
    assert result.answer is False
    assert root_call is not None
    assert verify_fc_trace(cnf, variable_count, policy, root_call) is False

    seen: set[int] = set()
    pre_unit_merges = 0
    post_unit_merges = 0
    branch_merges = 0
    novel_branches = 0
    nonnovel_branches = 0
    cyclic_entry_calls = 0
    cyclic_post_states = 0
    calls_with_pre_merge = 0
    states_with_post_merge = 0
    maximum_pre_merge = 0
    maximum_post_merge = 0
    maximum_branch_merge = 0
    pre_merge_histogram: Counter[int] = Counter()
    post_merge_histogram: Counter[int] = Counter()
    branch_merge_histogram: Counter[int] = Counter()
    merges_by_depth: Counter[tuple[str, int]] = Counter()

    def walk(call_id: int, incoming: dict[int, bool], depth: int) -> None:
        nonlocal pre_unit_merges, post_unit_merges, branch_merges
        nonlocal novel_branches, nonnovel_branches
        nonlocal cyclic_entry_calls, cyclic_post_states
        nonlocal calls_with_pre_merge, states_with_post_merge
        nonlocal maximum_pre_merge, maximum_post_merge, maximum_branch_merge

        if call_id in seen:
            return
        seen.add(call_id)
        call = policy.calls[call_id]

        before_count, before_acyclic = component_count(n, incoming, pairs)
        after_pre, _, _ = add_units(incoming, call.get("pre_units", []))
        pre_count, pre_acyclic = component_count(n, after_pre, pairs)
        pre_merge = max(0, before_count - pre_count)
        pre_unit_merges += pre_merge
        calls_with_pre_merge += pre_merge > 0
        maximum_pre_merge = max(maximum_pre_merge, pre_merge)
        pre_merge_histogram[pre_merge] += 1
        merges_by_depth[("pre_unit", depth)] += pre_merge
        cyclic_entry_calls += not pre_acyclic

        if call["terminal"] != "STATE":
            return
        state = policy.states[int(call["state"])]
        after_post, _, _ = add_units(after_pre, state.get("post_units", []))
        post_count, post_acyclic = component_count(n, after_post, pairs)
        post_merge = max(0, pre_count - post_count)
        post_unit_merges += post_merge
        states_with_post_merge += post_merge > 0
        maximum_post_merge = max(maximum_post_merge, post_merge)
        post_merge_histogram[post_merge] += 1
        merges_by_depth[("post_local_unit", depth)] += post_merge
        cyclic_post_states += not post_acyclic

        if state["terminal"] not in ("BRANCH_UNSAT", "BRANCH_SAT"):
            return

        variable = int(state["branch_var"])
        left, right = pairs[variable]
        post_closure = comparison_closure(n, after_post, pairs)
        post_parts = components(post_closure)
        index = {
            vertex: component_index
            for component_index, component in enumerate(post_parts)
            for vertex in component
        }
        is_novel = post_acyclic and index[left] != index[right]
        novel_branches += is_novel
        nonnovel_branches += not is_novel

        for child in state["children"]:
            if child["call"] is None:
                continue
            value = bool(child["value"])
            child_assignment = dict(after_post)
            child_assignment[variable] = value
            child_count, _ = component_count(n, child_assignment, pairs)
            branch_merge = max(0, post_count - child_count)
            branch_merges += branch_merge
            maximum_branch_merge = max(maximum_branch_merge, branch_merge)
            branch_merge_histogram[branch_merge] += 1
            merges_by_depth[("branch", depth)] += branch_merge
            walk(int(child["call"]), child_assignment, depth + 1)
            if child["result"]:
                break

    walk(root_call, {}, 0)
    assert len(seen) == len(policy.calls)

    return {
        "n": n,
        "calls": len(policy.calls),
        "states": len(policy.states),
        "cache_hits": result.cache_hits,
        "pre_unit_component_merges": pre_unit_merges,
        "post_local_unit_component_merges": post_unit_merges,
        "branch_component_merges": branch_merges,
        "novel_branches": novel_branches,
        "nonnovel_branches": nonnovel_branches,
        "calls_with_pre_merge": calls_with_pre_merge,
        "states_with_post_merge": states_with_post_merge,
        "maximum_pre_merge": maximum_pre_merge,
        "maximum_post_merge": maximum_post_merge,
        "maximum_branch_merge": maximum_branch_merge,
        "cyclic_entry_calls": cyclic_entry_calls,
        "cyclic_post_states": cyclic_post_states,
        "pre_merge_histogram": tuple(sorted(pre_merge_histogram.items())),
        "post_merge_histogram": tuple(sorted(post_merge_histogram.items())),
        "branch_merge_histogram": tuple(sorted(branch_merge_histogram.items())),
        "merges_by_depth": tuple(sorted(merges_by_depth.items())),
    }


def self_test() -> None:
    rows = []
    for n in range(4, 9):
        data = audit(n)
        rows.append(data)
        print(f"ORDER_SIZE = {n}")
        for key, value in data.items():
            if key != "n":
                print(f"  {key} = {value}")

    print("JANUS_GT_COMPONENT_MERGE_ACCOUNTING = PASS")
    print(f"rows = {tuple(rows)}")
    print("historical_charge = novel branch component merge")
    print("new_charge_candidates = pre-unit and post-local-Resolution unit component merges")
    print("claim_boundary = finite resource accounting; no transferred GT lower bound")


if __name__ == "__main__":
    self_test()
