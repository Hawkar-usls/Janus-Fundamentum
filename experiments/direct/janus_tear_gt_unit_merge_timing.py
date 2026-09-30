#!/usr/bin/env python3
"""Locate every unit-induced component merge relative to novelty level n-2.

The historical graph-tautology Formula-Caching argument obtains 2^(n-2)
distinct restrictions when search first reaches n-2 novel component-joining
branches.  A unit-induced component merge could threaten that count only if it
occurs before this target and thereby replaces a required binary novel branch.

This audit independently reconstructs the novelty level of every exact Policy-0A
call and cross-checks it against the source-certified merge records emitted by
janus_tear_gt_component_merge_sources.py.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_component_merge_sources import audit as source_audit
from janus_tear_gt_critical_order_damage import pair_variables
from janus_tear_gt_novel_branch_audit_v2 import (
    add_units,
    comparison_closure,
    components,
)
from janus_tear_policy0a_fc_trace import FCTracePolicy, verify_fc_trace
from janus_tear_policy0a_graph_tautology_probe import graph_tautology_cnf


def novelty_map(n: int):
    cnf, variable_count = graph_tautology_cnf(n)
    pairs = pair_variables(n)
    policy = FCTracePolicy()
    result, root_call = policy.solve(cnf, variable_count)
    assert result.answer is False
    assert root_call is not None
    assert verify_fc_trace(cnf, variable_count, policy, root_call) is False

    levels: dict[int, int] = {}
    seen: set[int] = set()

    def walk(call_id: int, incoming: dict[int, bool], novelty: int) -> None:
        assert call_id not in seen
        seen.add(call_id)
        levels[call_id] = novelty
        call = policy.calls[call_id]

        after_pre, _, _ = add_units(incoming, call.get("pre_units", []))
        if call["terminal"] != "STATE":
            return

        state = policy.states[int(call["state"])]
        after_post, _, _ = add_units(after_pre, state.get("post_units", []))
        if state["terminal"] not in ("BRANCH_UNSAT", "BRANCH_SAT"):
            return

        variable = int(state["branch_var"])
        left, right = pairs[variable]
        closure = comparison_closure(n, after_post, pairs)
        parts = components(closure)
        if variable in after_post or not closure.acyclic:
            increment = 0
        else:
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
    return levels, len(policy.calls), len(policy.states), result.cache_hits


def audit(n: int):
    sources = source_audit(n)
    levels, calls, states, cache_hits = novelty_map(n)
    assert calls == sources["calls"]
    assert states == sources["states"]
    assert cache_hits == sources["cache_hits"]

    target = n - 2
    timing_histogram: Counter[str] = Counter()
    novelty_histogram: Counter[int] = Counter()
    margins = []
    timed_records = []

    for record in sources["records"]:
        call_id = int(record["call_id"])
        novelty = levels[call_id]
        margin = novelty - target
        timing = "BEFORE_TARGET" if margin < 0 else (
            "AT_TARGET" if margin == 0 else "AFTER_TARGET"
        )
        timing_histogram[timing] += 1
        novelty_histogram[novelty] += 1
        margins.append(margin)
        timed_records.append(
            {
                "call_id": call_id,
                "stage": record["stage"],
                "literal": record["literal"],
                "pair": record["pair"],
                "source_kind": record["source_kind"],
                "before_components": record["before_components"],
                "after_components": record["after_components"],
                "novelty_level": novelty,
                "target_level": target,
                "margin": margin,
                "timing": timing,
            }
        )

    before_target = timing_histogram["BEFORE_TARGET"]
    assert before_target == 0
    assert all(int(record["before_components"]) == 2 for record in sources["records"])
    assert all(int(record["after_components"]) == 1 for record in sources["records"])

    return {
        "n": n,
        "calls": calls,
        "states": states,
        "cache_hits": cache_hits,
        "target_level": target,
        "unit_component_merges": len(timed_records),
        "merges_before_target": before_target,
        "merges_at_target": timing_histogram["AT_TARGET"],
        "merges_after_target": timing_histogram["AFTER_TARGET"],
        "timing_histogram": tuple(sorted(timing_histogram.items())),
        "novelty_histogram": tuple(sorted(novelty_histogram.items())),
        "minimum_margin": min(margins) if margins else None,
        "maximum_margin": max(margins) if margins else None,
        "records": tuple(timed_records),
    }


def self_test() -> None:
    rows = []
    for n in range(4, 9):
        data = audit(n)
        rows.append(
            (
                n,
                data["target_level"],
                data["unit_component_merges"],
                data["merges_before_target"],
                data["merges_at_target"],
                data["merges_after_target"],
                data["minimum_margin"],
                data["maximum_margin"],
            )
        )
        print(f"ORDER_SIZE = {n}")
        print(f"  target_level = {data['target_level']}")
        print(f"  unit_component_merges = {data['unit_component_merges']}")
        print(f"  merges_before_target = {data['merges_before_target']}")
        print(f"  merges_at_target = {data['merges_at_target']}")
        print(f"  merges_after_target = {data['merges_after_target']}")
        print(f"  timing_histogram = {data['timing_histogram']}")
        print(f"  novelty_histogram = {data['novelty_histogram']}")
        print(f"  minimum_margin = {data['minimum_margin']}")
        print(f"  maximum_margin = {data['maximum_margin']}")
        print(f"  records = {data['records']}")

    print("JANUS_GT_UNIT_MERGE_TIMING = PASS")
    print(f"rows = {tuple(rows)}")
    print("finite_result = no unit-induced component merge occurs before novelty level n-2 for n=4..8")
    print("claim_boundary = finite timing audit; asymptotic preservation remains unproved")


if __name__ == "__main__":
    self_test()
