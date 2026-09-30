#!/usr/bin/env python3
"""Census every pre-frontier clause-width decrease on Policy-0A GT traces.

The certified C024 provenance paths that actually produce component-joining
units lose one literal only on novel branches.  A stronger conjecture would say
that this holds for every locally derived clause.  This audit tries to falsify
that stronger statement.

For every actual branch edge whose parent novelty is below n-2, it reduces every
parent post-propagation clause under the branch assignment and records every
strict width decrease.  Events are classified by:

- novel versus nonnovel branch;
- immediate parent-local-resolvent versus inherited/other source;
- membership in one of the exact provenance paths that later produces a
  component-joining unit.

The script does not fail merely because harmless clauses shrink on nonnovel
branches.  Such events falsify the universal potential and motivate the narrower
frontier-dangerous-clause invariant.  It does fail if a certified dangerous
provenance edge is absent from the census or is nonnovel.
"""

from __future__ import annotations

from collections import Counter, defaultdict

from janus_tear_gt_component_merge_sources import reduce_clause
from janus_tear_gt_pre_unit_recursive_provenance import audit as provenance_audit
from janus_tear_gt_unit_merge_timing import novelty_map
from janus_tear_policy0a_fc_trace import FCTracePolicy, verify_fc_trace
from janus_tear_policy0a_graph_tautology_probe import graph_tautology_cnf

Clause = tuple[int, ...]
CNF = tuple[Clause, ...]


def unit_assignments(events) -> dict[int, bool]:
    result: dict[int, bool] = {}
    for event in events:
        if event["kind"] != "unit":
            continue
        literal = int(event["literal"])
        result[abs(literal)] = literal > 0
    return result


def audit(n: int):
    root, variable_count = graph_tautology_cnf(n)
    policy = FCTracePolicy()
    result, root_call = policy.solve(root, variable_count)
    assert result.answer is False and root_call is not None
    assert verify_fc_trace(root, variable_count, policy, root_call) is False

    levels, calls, states, cache_hits = novelty_map(n)
    assert calls == len(policy.calls)
    assert states == len(policy.states)
    assert cache_hits == result.cache_hits
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

    dangerous_events: set[tuple[int, int, Clause, Clause]] = set()
    provenance = provenance_audit(n)
    for merge in provenance["records"]:
        for path in merge["shortest_paths"]:
            for step in path["steps"]:
                if step["kind"] not in ("BRANCH_REDUCTION", "FINAL_BRANCH_TO_UNIT"):
                    continue
                parent_call = int(step["parent_call_id"])
                branch_literal = int(step["branch_literal"])
                child_call = edge_by_literal[(parent_call, branch_literal)]
                dangerous_events.add(
                    (
                        parent_call,
                        child_call,
                        tuple(step["from_clause"]),
                        tuple(step["to_clause"]),
                    )
                )

    counts: Counter[str] = Counter()
    width_drop_histogram: Counter[int] = Counter()
    local_width_drop_histogram: Counter[int] = Counter()
    novelty_transition_histogram: Counter[tuple[int, int]] = Counter()
    source_class_histogram: Counter[str] = Counter()
    nonnovel_examples = []
    local_nonnovel_examples = []
    dangerous_seen: set[tuple[int, int, Clause, Clause]] = set()

    for state in policy.states.values():
        if state["terminal"] not in ("BRANCH_UNSAT", "BRANCH_SAT"):
            continue
        parent_call = int(state["entry_call"])
        parent_level = levels[parent_call]
        if parent_level >= target:
            continue

        post_cnf: CNF = tuple(state["post_result"])
        post_assignment = unit_assignments(state.get("post_units", []))
        resolution_output: CNF = tuple(state["resolution_output"])
        local_resolvents = {
            tuple(event["resolvent"])
            for event in state.get("resolution_events", [])
        }

        post_source_classes: dict[Clause, set[str]] = defaultdict(set)
        for post_clause in post_cnf:
            for antecedent in resolution_output:
                if reduce_clause(antecedent, post_assignment) != post_clause:
                    continue
                if antecedent in local_resolvents:
                    post_source_classes[post_clause].add("IMMEDIATE_LOCAL_RESOLVENT")
                elif antecedent in tuple(state["key"]):
                    post_source_classes[post_clause].add("INHERITED_KEY")
                else:
                    post_source_classes[post_clause].add("OTHER_OUTPUT")

        for child in state["children"]:
            if child["call"] is None:
                continue
            child_call = int(child["call"])
            branch_literal = int(child["literal"])
            branch_assignment = {abs(branch_literal): branch_literal > 0}
            increment = levels[child_call] - parent_level
            assert increment in (0, 1)
            novelty_transition_histogram[(parent_level, levels[child_call])] += 1

            for clause in post_cnf:
                residual = reduce_clause(clause, branch_assignment)
                if residual is None or len(residual) >= len(clause):
                    continue

                drop = len(clause) - len(residual)
                assert drop == 1
                event_key = (parent_call, child_call, clause, residual)
                is_dangerous = event_key in dangerous_events
                if is_dangerous:
                    dangerous_seen.add(event_key)

                source_classes = post_source_classes.get(clause, {"UNCLASSIFIED"})
                immediate_local = "IMMEDIATE_LOCAL_RESOLVENT" in source_classes
                source_label = "+".join(sorted(source_classes))
                source_class_histogram[source_label] += 1
                counts["all_shrinks"] += 1
                counts["novel_shrinks" if increment else "nonnovel_shrinks"] += 1
                counts["dangerous_shrinks" if is_dangerous else "harmless_or_untracked_shrinks"] += 1
                counts["immediate_local_shrinks" if immediate_local else "nonlocal_shrinks"] += 1
                if immediate_local:
                    local_width_drop_histogram[len(clause)] += 1
                width_drop_histogram[len(clause)] += 1

                if is_dangerous:
                    assert increment == 1
                    counts["dangerous_novel_shrinks"] += 1
                    if immediate_local:
                        counts["dangerous_immediate_local_shrinks"] += 1
                elif increment == 0:
                    example = {
                        "n": n,
                        "parent_call": parent_call,
                        "child_call": child_call,
                        "parent_novelty": parent_level,
                        "child_novelty": levels[child_call],
                        "branch_literal": branch_literal,
                        "clause": clause,
                        "residual": residual,
                        "source_classes": tuple(sorted(source_classes)),
                    }
                    if len(nonnovel_examples) < 8:
                        nonnovel_examples.append(example)
                    if immediate_local and len(local_nonnovel_examples) < 8:
                        local_nonnovel_examples.append(example)
                    if immediate_local:
                        counts["immediate_local_nonnovel_shrinks"] += 1

            if child["result"]:
                break

    assert dangerous_seen == dangerous_events, (
        len(dangerous_seen),
        len(dangerous_events),
        dangerous_events - dangerous_seen,
    )
    assert counts["dangerous_novel_shrinks"] == len(dangerous_events)

    universal_status = (
        "FALSIFIED_BY_IMMEDIATE_LOCAL_NONNOVEL_SHRINK"
        if counts["immediate_local_nonnovel_shrinks"]
        else "SURVIVED_FINITE_CENSUS"
    )
    dangerous_status = "SURVIVED_FINITE_CENSUS"

    return {
        "n": n,
        "calls": len(policy.calls),
        "states": len(policy.states),
        "target": target,
        "counts": tuple(sorted(counts.items())),
        "dangerous_event_count": len(dangerous_events),
        "dangerous_seen_count": len(dangerous_seen),
        "width_drop_histogram": tuple(sorted(width_drop_histogram.items())),
        "local_width_drop_histogram": tuple(sorted(local_width_drop_histogram.items())),
        "novelty_transition_histogram": tuple(sorted(novelty_transition_histogram.items())),
        "source_class_histogram": tuple(sorted(source_class_histogram.items())),
        "universal_potential_status": universal_status,
        "dangerous_clause_potential_status": dangerous_status,
        "nonnovel_examples": tuple(nonnovel_examples),
        "immediate_local_nonnovel_examples": tuple(local_nonnovel_examples),
    }


def self_test() -> None:
    rows = []
    aggregate: Counter[str] = Counter()
    universal_failures = []
    for n in range(4, 9):
        data = audit(n)
        aggregate.update(dict(data["counts"]))
        if data["universal_potential_status"].startswith("FALSIFIED"):
            universal_failures.append(n)
        rows.append(
            (
                n,
                data["target"],
                data["dangerous_event_count"],
                data["counts"],
                data["universal_potential_status"],
                data["dangerous_clause_potential_status"],
            )
        )
        print(f"ORDER_SIZE = {n}")
        print(f"  target = {data['target']}")
        print(f"  counts = {data['counts']}")
        print(f"  dangerous_event_count = {data['dangerous_event_count']}")
        print(f"  width_drop_histogram = {data['width_drop_histogram']}")
        print(f"  local_width_drop_histogram = {data['local_width_drop_histogram']}")
        print(f"  source_class_histogram = {data['source_class_histogram']}")
        print(f"  universal_potential_status = {data['universal_potential_status']}")
        print(f"  dangerous_clause_potential_status = {data['dangerous_clause_potential_status']}")
        print(f"  nonnovel_examples = {data['nonnovel_examples']}")
        print(
            "  immediate_local_nonnovel_examples = "
            f"{data['immediate_local_nonnovel_examples']}"
        )

    print("JANUS_GT_GLOBAL_CLAUSE_SHRINK_CENSUS = PASS")
    print(f"rows = {tuple(rows)}")
    print(f"aggregate_counts = {tuple(sorted(aggregate.items()))}")
    print(f"universal_potential_failures = {tuple(universal_failures)}")
    print("claim_boundary = finite branch-shrink census; dangerous-clause status is execution-relative, not an asymptotic theorem")


if __name__ == "__main__":
    self_test()
