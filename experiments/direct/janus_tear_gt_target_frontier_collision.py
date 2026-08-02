#!/usr/bin/env python3
"""Test whether exact cache keys collapse the historical GT target frontier.

The historical Formula-Caching argument reaches at least 2^(n-2) distinct
partial-order restrictions after n-2 novel component-joining branches.  C024 has
verified through n=8 that unit-induced component merges occur only after this
novelty level is reached.  The remaining finite collapse mechanism is exact
residual caching: distinct historical restrictions might simplify to the same
canonical residual CNF before cache lookup.

For every first call occurrence reaching novelty level n-2, this audit records:

- the transitive-closure signature immediately after the target branch;
- the exact canonical residual key used by Policy-0A after pre-unit propagation;
- or a terminal pre-cache outcome when no cache key exists.

A cache collision is a single exact residual key reached from two distinct
historical restriction signatures.  Terminal pre-cache calls are never reused by
Policy-0A's memo table and are counted separately.
"""

from __future__ import annotations

from collections import Counter, defaultdict

from janus_tear_gt_critical_order_damage import pair_variables
from janus_tear_gt_novel_branch_audit_v2 import (
    add_units,
    comparison_closure,
    components,
    signature,
)
from janus_tear_policy0a_fc_trace import FCTracePolicy, verify_fc_trace
from janus_tear_policy0a_graph_tautology_probe import graph_tautology_cnf


def audit(n: int):
    cnf, variable_count = graph_tautology_cnf(n)
    pairs = pair_variables(n)
    policy = FCTracePolicy()
    result, root_call = policy.solve(cnf, variable_count)
    assert result.answer is False
    assert root_call is not None
    assert verify_fc_trace(cnf, variable_count, policy, root_call) is False

    target = n - 2
    seen: set[int] = set()
    frontier_records: list[dict[str, object]] = []

    def walk(
        call_id: int,
        incoming: dict[int, bool],
        novelty: int,
        target_seen: bool,
    ) -> None:
        assert call_id not in seen
        seen.add(call_id)
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
            child_level = novelty + increment
            reached_now = not target_seen and child_level >= target
            child_id = int(child["call"])

            if reached_now:
                child_closure = comparison_closure(n, child_assignment, pairs)
                assert child_closure.acyclic
                restriction = signature(child_closure)
                child_call = policy.calls[child_id]
                terminal = str(child_call["terminal"])
                key = child_call.get("key")
                cache_target = child_call.get("cache_target")
                frontier_records.append(
                    {
                        "call_id": child_id,
                        "restriction": restriction,
                        "terminal": terminal,
                        "has_cache_key": key is not None,
                        "cache_key": tuple(key) if key is not None else None,
                        "cache_target": cache_target,
                        "input": tuple(child_call["input"]),
                        "pre_unit_events": len(child_call.get("pre_units", [])),
                    }
                )

            walk(
                child_id,
                child_assignment,
                child_level,
                target_seen or reached_now,
            )
            if child["result"]:
                break

    walk(root_call, {}, 0, False)
    assert len(seen) == len(policy.calls)

    restriction_to_calls: dict[tuple, list[int]] = defaultdict(list)
    key_to_restrictions: dict[tuple, set[tuple]] = defaultdict(set)
    key_to_calls: dict[tuple, list[int]] = defaultdict(list)
    terminal_histogram: Counter[str] = Counter()
    target_cache_hits = 0

    for record in frontier_records:
        restriction = tuple(record["restriction"])
        call_id = int(record["call_id"])
        restriction_to_calls[restriction].append(call_id)
        terminal_histogram[str(record["terminal"])] += 1
        if record["terminal"] == "CACHE_HIT":
            target_cache_hits += 1
        key = record["cache_key"]
        if key is not None:
            canonical_key = tuple(tuple(clause) for clause in key)
            key_to_restrictions[canonical_key].add(restriction)
            key_to_calls[canonical_key].append(call_id)

    cross_restriction_collisions = tuple(
        {
            "key": key,
            "restriction_count": len(restrictions),
            "call_ids": tuple(key_to_calls[key]),
        }
        for key, restrictions in key_to_restrictions.items()
        if len(restrictions) > 1
    )
    repeated_key_groups = tuple(
        {
            "key": key,
            "call_ids": tuple(call_ids),
            "restriction_count": len(key_to_restrictions[key]),
        }
        for key, call_ids in key_to_calls.items()
        if len(call_ids) > 1
    )
    repeated_restriction_groups = tuple(
        (restriction, tuple(call_ids))
        for restriction, call_ids in restriction_to_calls.items()
        if len(call_ids) > 1
    )

    historical_target = 2 ** target
    distinct_restrictions = len(restriction_to_calls)
    assert distinct_restrictions >= historical_target
    assert not repeated_restriction_groups
    assert target_cache_hits == 0
    assert not cross_restriction_collisions

    return {
        "n": n,
        "calls": len(policy.calls),
        "states": len(policy.states),
        "global_cache_hits": result.cache_hits,
        "target_level": target,
        "historical_target": historical_target,
        "frontier_calls": len(frontier_records),
        "distinct_restrictions": distinct_restrictions,
        "frontier_with_cache_key": sum(record["has_cache_key"] for record in frontier_records),
        "frontier_pre_cache_terminal": sum(not record["has_cache_key"] for record in frontier_records),
        "distinct_cache_keys": len(key_to_restrictions),
        "target_cache_hits": target_cache_hits,
        "cross_restriction_cache_collisions": len(cross_restriction_collisions),
        "repeated_exact_key_groups": len(repeated_key_groups),
        "terminal_histogram": tuple(sorted(terminal_histogram.items())),
        "collision_records": cross_restriction_collisions,
        "repeated_key_records": repeated_key_groups,
    }


def self_test() -> None:
    rows = []
    for n in range(4, 9):
        data = audit(n)
        rows.append(
            (
                n,
                data["target_level"],
                data["historical_target"],
                data["frontier_calls"],
                data["distinct_restrictions"],
                data["frontier_with_cache_key"],
                data["frontier_pre_cache_terminal"],
                data["distinct_cache_keys"],
                data["target_cache_hits"],
                data["cross_restriction_cache_collisions"],
            )
        )
        print(f"ORDER_SIZE = {n}")
        for key, value in data.items():
            if key != "n":
                print(f"  {key} = {value}")

    print("JANUS_GT_TARGET_FRONTIER_COLLISION = PASS")
    print(f"rows = {tuple(rows)}")
    print("finite_result = distinct historical target restrictions are not identified by exact cache keys for n=4..8")
    print("claim_boundary = finite frontier collision audit; asymptotic injectivity remains unproved")


if __name__ == "__main__":
    self_test()
