#!/usr/bin/env python3
"""Charge recursively inherited pre-unit merges to historical novel branches.

The recursive provenance audit found that all pre-unit component merges through
GT_8 originate in a local Resolution clause and are later narrowed by branch
restrictions until they become unit.  This audit checks whether those narrowing
steps are exactly the novel component-joining branches counted by the historical
Formula-Caching lower bound.

For every shortest provenance path it verifies, when true in the tested range:
- the origin is one explicit local Resolution event;
- each branch step removes exactly one clause literal;
- no hidden pre/post unit reduction removes provenance literals;
- each branch step increases the historical novelty level by one;
- origin clause width = number of novel narrowing branches + 1;
- origin novelty + novel narrowing branches = n-2.

This is a finite charge certificate, not an asymptotic proof that every possible
Policy-0A derived clause has this form.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_pre_unit_recursive_provenance import audit as provenance_audit
from janus_tear_gt_unit_merge_timing import novelty_map
from janus_tear_policy0a_fc_trace import FCTracePolicy, verify_fc_trace
from janus_tear_policy0a_graph_tautology_probe import graph_tautology_cnf


def audit(n: int):
    provenance = provenance_audit(n)
    levels, calls, states, cache_hits = novelty_map(n)

    root, variable_count = graph_tautology_cnf(n)
    policy = FCTracePolicy()
    result, root_call = policy.solve(root, variable_count)
    assert result.answer is False and root_call is not None
    assert verify_fc_trace(root, variable_count, policy, root_call) is False
    assert calls == len(policy.calls)
    assert states == len(policy.states)
    assert cache_hits == result.cache_hits

    edge_by_literal: dict[tuple[int, int], int] = {}
    for state in policy.states.values():
        if state["terminal"] not in ("BRANCH_UNSAT", "BRANCH_SAT"):
            continue
        parent_call = int(state["entry_call"])
        for child in state["children"]:
            if child["call"] is None:
                continue
            key = (parent_call, int(child["literal"]))
            assert key not in edge_by_literal
            edge_by_literal[key] = int(child["call"])

    target = n - 2
    records = []
    origin_width_histogram: Counter[int] = Counter()
    novel_step_histogram: Counter[int] = Counter()
    origin_novelty_histogram: Counter[int] = Counter()
    resolution_shape_histogram: Counter[tuple[int, int, int]] = Counter()

    for merge in provenance["records"]:
        assert merge["all_path_count"] == 1
        assert merge["shortest_origins"] == ("LOCAL_RESOLUTION",)
        assert len(merge["shortest_paths"]) == 1
        path = merge["shortest_paths"][0]
        event = path["origin_event"]
        assert event is not None
        origin_clause = tuple(path["origin_clause"])
        origin_state_id = int(event["state_id"])
        origin_call_id = int(policy.states[origin_state_id]["entry_call"])
        origin_novelty = levels[origin_call_id]

        branch_steps = tuple(
            step
            for step in path["steps"]
            if step["kind"] in ("BRANCH_REDUCTION", "FINAL_BRANCH_TO_UNIT")
        )
        unit_steps = tuple(
            step
            for step in path["steps"]
            if step["kind"] in ("PRE_UNIT_REDUCTION", "POST_UNIT_REDUCTION")
        )

        novel_steps = 0
        nonnovel_steps = 0
        edge_records = []
        for step in branch_steps:
            parent_call_id = int(step["parent_call_id"])
            branch_literal = int(step["branch_literal"])
            child_call_id = edge_by_literal[(parent_call_id, branch_literal)]
            increment = levels[child_call_id] - levels[parent_call_id]
            assert increment in (0, 1)
            if increment:
                novel_steps += 1
            else:
                nonnovel_steps += 1

            from_clause = tuple(step["from_clause"])
            to_clause = tuple(step["to_clause"])
            assert len(from_clause) == len(to_clause) + 1
            assert abs(branch_literal) in {abs(literal) for literal in from_clause}
            assert abs(branch_literal) not in {abs(literal) for literal in to_clause}
            edge_records.append(
                {
                    "parent_call_id": parent_call_id,
                    "child_call_id": child_call_id,
                    "branch_literal": branch_literal,
                    "novelty_before": levels[parent_call_id],
                    "novelty_after": levels[child_call_id],
                    "novel": bool(increment),
                    "from_width": len(from_clause),
                    "to_width": len(to_clause),
                }
            )

        hidden_unit_reductions = 0
        for step in unit_steps:
            assignments = tuple(step["unit_assignment"])
            from_clause = tuple(step["from_clause"])
            to_clause = tuple(step["to_clause"])
            if len(from_clause) != len(to_clause):
                hidden_unit_reductions += len(from_clause) - len(to_clause)
            assert not assignments
            assert from_clause == to_clause

        origin_width = len(origin_clause)
        assert nonnovel_steps == 0
        assert hidden_unit_reductions == 0
        assert origin_width == novel_steps + 1
        assert novel_steps == len(branch_steps)
        assert origin_novelty + novel_steps == target
        assert int(merge["minimum_ancestor_hops"]) == novel_steps

        left = tuple(event["left"])
        right = tuple(event["right"])
        resolvent = tuple(event["resolvent"])
        assert resolvent == origin_clause
        shape = (len(left), len(right), len(resolvent))
        resolution_shape_histogram[shape] += 1
        origin_width_histogram[origin_width] += 1
        novel_step_histogram[novel_steps] += 1
        origin_novelty_histogram[origin_novelty] += 1

        records.append(
            {
                "n": n,
                "child_call_id": int(merge["child_call_id"]),
                "literal": int(merge["literal"]),
                "pair": tuple(merge["pair"]),
                "origin_call_id": origin_call_id,
                "origin_state_id": origin_state_id,
                "origin_clause": origin_clause,
                "origin_width": origin_width,
                "origin_novelty": origin_novelty,
                "target_novelty": target,
                "novel_narrowing_steps": novel_steps,
                "nonnovel_narrowing_steps": nonnovel_steps,
                "hidden_unit_reductions": hidden_unit_reductions,
                "resolution_shape": shape,
                "edges": tuple(edge_records),
            }
        )

    assert len(records) == provenance["pre_unit_component_merges"]

    return {
        "n": n,
        "pre_unit_component_merges": len(records),
        "target_novelty": target,
        "origin_width_histogram": tuple(sorted(origin_width_histogram.items())),
        "novel_step_histogram": tuple(sorted(novel_step_histogram.items())),
        "origin_novelty_histogram": tuple(sorted(origin_novelty_histogram.items())),
        "resolution_shape_histogram": tuple(sorted(resolution_shape_histogram.items())),
        "maximum_novel_narrowing_steps": max(novel_step_histogram) if novel_step_histogram else 0,
        "records": tuple(records),
    }


def self_test() -> None:
    rows = []
    aggregate_steps: Counter[int] = Counter()
    aggregate_widths: Counter[int] = Counter()
    maximum_steps = 0

    for n in range(4, 9):
        data = audit(n)
        aggregate_steps.update(dict(data["novel_step_histogram"]))
        aggregate_widths.update(dict(data["origin_width_histogram"]))
        maximum_steps = max(maximum_steps, data["maximum_novel_narrowing_steps"])
        rows.append(
            (
                n,
                data["target_novelty"],
                data["pre_unit_component_merges"],
                data["origin_width_histogram"],
                data["novel_step_histogram"],
                data["origin_novelty_histogram"],
            )
        )
        print(f"ORDER_SIZE = {n}")
        print(f"  target_novelty = {data['target_novelty']}")
        print(f"  pre_unit_component_merges = {data['pre_unit_component_merges']}")
        print(f"  origin_width_histogram = {data['origin_width_histogram']}")
        print(f"  novel_step_histogram = {data['novel_step_histogram']}")
        print(f"  origin_novelty_histogram = {data['origin_novelty_histogram']}")
        print(f"  resolution_shape_histogram = {data['resolution_shape_histogram']}")
        print(
            "  maximum_novel_narrowing_steps = "
            f"{data['maximum_novel_narrowing_steps']}"
        )
        print(f"  records = {data['records']}")

    print("JANUS_GT_PRE_UNIT_NOVEL_CHARGE = PASS")
    print(f"rows = {tuple(rows)}")
    print(f"aggregate_steps = {tuple(sorted(aggregate_steps.items()))}")
    print(f"aggregate_widths = {tuple(sorted(aggregate_widths.items()))}")
    print(f"maximum_steps = {maximum_steps}")
    print("finite_result = every observed inherited unit is a local resolvent narrowed only by novel branches, one literal per join")
    print("claim_boundary = finite charge certificate for n=4..8; general derived-clause invariant remains unproved")


if __name__ == "__main__":
    self_test()
