#!/usr/bin/env python3
"""Falsify quotient-component factorization of Policy-0A branch frequency.

The singleton-tail handoff profile shows that the selected branch avoids every
dangerous tail on the finite GT frontier.  This audit tests the tempting
explanation that comparison-variable frequency depends only on the unordered
pair of current relation components containing its endpoints.

For every pre-frontier branch state through GT_8, variables are grouped by that
component pair.  The audit records frequency spreads inside every group and in
the selected group.  Surviving dangerous lineages are counted both as lineage
occurrences and as unique parent states; these are different populations.

The result is an obstruction certificate: component-pair factorization is
false, including on dangerous parent states.  Any arbitrary-n handoff proof
must retain clause history, polarity, and vertex identity.
"""

from __future__ import annotations

from collections import Counter, defaultdict

from janus_tear_gt_component_tree_clause_audit import execution_context
from janus_tear_gt_novel_branch_audit_v2 import comparison_closure, components
from janus_tear_gt_surviving_branch_frequency_profile import audit as lineage_audit


def quotient_partition(n: int, assignment, pairs):
    closure = comparison_closure(n, assignment, pairs)
    assert closure.acyclic
    parts = tuple(components(closure))
    index = {
        vertex: component_id
        for component_id, part in enumerate(parts)
        for vertex in part
    }
    return parts, index


def component_pair(index, endpoints):
    left, right = endpoints
    return tuple(sorted((index[int(left)], index[int(right)])))


def state_profile(n: int, state_id: int, context):
    policy = context["policy"]
    pairs = context["pairs"]
    state = policy.states[state_id]
    cnf = tuple(tuple(clause) for clause in state["post_result"])
    assignment = context["state_after_post"][state_id]
    parts, index = quotient_partition(n, assignment, pairs)
    frequencies = Counter(abs(literal) for clause in cnf for literal in clause)
    selected = int(state["branch_var"])
    maximum = max(frequencies.values())
    assert frequencies[selected] == maximum

    groups: dict[tuple[int, int], list[int]] = defaultdict(list)
    for variable in frequencies:
        groups[component_pair(index, pairs[int(variable)])].append(int(variable))

    rows = []
    for pair, variables in sorted(groups.items()):
        values = tuple(sorted(frequencies[variable] for variable in variables))
        rows.append(
            {
                "component_pair": pair,
                "variables": tuple(sorted(variables)),
                "frequencies": values,
                "spread": max(values) - min(values),
                "uniform": len(set(values)) == 1,
                "contains_selected": selected in variables,
            }
        )

    selected_pair = component_pair(index, pairs[selected])
    selected_group = next(
        row for row in rows if row["component_pair"] == selected_pair
    )
    return {
        "state_id": state_id,
        "parts": parts,
        "selected": selected,
        "selected_frequency": maximum,
        "selected_group": selected_group,
        "groups": tuple(rows),
        "all_groups_uniform": all(row["uniform"] for row in rows),
    }


def audit(n: int):
    context = execution_context(n)
    policy = context["policy"]
    levels = context["levels"]
    target = n - 2
    lineage_records = tuple(lineage_audit(n)["records"])
    lineage_states = {
        int(record["parent_state"])
        for record in lineage_records
    }

    counts: Counter[str] = Counter()
    counts["dangerous_lineage_occurrences"] = len(lineage_records)
    group_spreads: Counter[int] = Counter()
    selected_group_spreads: Counter[int] = Counter()
    lineage_group_spreads: Counter[int] = Counter()
    lineage_selected_group_spreads: Counter[int] = Counter()
    examples = []

    for state in policy.states.values():
        state_id = int(state["id"])
        call_id = int(state["entry_call"])
        if int(levels[call_id]) > target:
            continue
        if state["terminal"] not in ("BRANCH_UNSAT", "BRANCH_SAT"):
            continue

        counts["branch_states"] += 1
        profile = state_profile(n, state_id, context)
        if profile["all_groups_uniform"]:
            counts["states_all_component_pairs_uniform"] += 1
        else:
            counts["states_with_nonuniform_component_pair"] += 1

        selected_group = profile["selected_group"]
        if selected_group["uniform"]:
            counts["selected_component_pair_uniform"] += 1
        else:
            counts["selected_component_pair_nonuniform"] += 1
        selected_group_spreads[int(selected_group["spread"])] += 1

        for row in profile["groups"]:
            counts["component_pair_groups"] += 1
            counts[
                "uniform_component_pair_groups"
                if row["uniform"]
                else "nonuniform_component_pair_groups"
            ] += 1
            group_spreads[int(row["spread"])] += 1

        if state_id in lineage_states:
            counts["dangerous_lineage_states"] += 1
            lineage_selected_group_spreads[int(selected_group["spread"])] += 1
            for row in profile["groups"]:
                lineage_group_spreads[int(row["spread"])] += 1
            if not selected_group["uniform"] and len(examples) < 2:
                examples.append(
                    {
                        "state_id": state_id,
                        "parts": profile["parts"],
                        "selected": profile["selected"],
                        "selected_frequency": profile["selected_frequency"],
                        "selected_group": selected_group,
                    }
                )

    assert counts["dangerous_lineage_states"] == len(lineage_states)
    return {
        "n": n,
        "target": target,
        "counts": tuple(sorted(counts.items())),
        "group_spreads": tuple(sorted(group_spreads.items())),
        "selected_group_spreads": tuple(sorted(selected_group_spreads.items())),
        "lineage_group_spreads": tuple(sorted(lineage_group_spreads.items())),
        "lineage_selected_group_spreads": tuple(
            sorted(lineage_selected_group_spreads.items())
        ),
        "examples": tuple(examples),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_group_spreads: Counter[int] = Counter()
    aggregate_selected_spreads: Counter[int] = Counter()
    aggregate_lineage_spreads: Counter[int] = Counter()
    aggregate_lineage_selected: Counter[int] = Counter()

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_group_spreads.update(dict(data["group_spreads"]))
        aggregate_selected_spreads.update(dict(data["selected_group_spreads"]))
        aggregate_lineage_spreads.update(dict(data["lineage_group_spreads"]))
        aggregate_lineage_selected.update(
            dict(data["lineage_selected_group_spreads"])
        )
        print(f"ORDER_SIZE = {n}")
        print(f"  target = {data['target']}")
        print(f"  counts = {data['counts']}")
        print(
            "  dangerous_selected_group_spreads = "
            f"{data['lineage_selected_group_spreads']}"
        )
        print(f"  obstruction_examples = {data['examples']}")

    expected = {
        "branch_states": 604,
        "component_pair_groups": 1851,
        "dangerous_lineage_occurrences": 42,
        "dangerous_lineage_states": 16,
        "uniform_component_pair_groups": 718,
        "nonuniform_component_pair_groups": 1133,
        "selected_component_pair_uniform": 141,
        "selected_component_pair_nonuniform": 463,
    }
    for key, value in expected.items():
        assert aggregate_counts[key] == value, (key, aggregate_counts[key], value)

    assert aggregate_counts["nonuniform_component_pair_groups"] > 0
    assert aggregate_counts["selected_component_pair_nonuniform"] > 0
    assert sum(
        count
        for spread, count in aggregate_lineage_selected.items()
        if spread > 0
    ) > 0

    print("JANUS_GT_BRANCH_FREQUENCY_COMPONENT_LAW = PASS")
    print("COMPONENT_PAIR_FREQUENCY_FACTORIZATION = FALSIFIED")
    print(f"AGGREGATE_COUNTS = {tuple(sorted(aggregate_counts.items()))}")
    print(
        "AGGREGATE_SELECTED_SPREADS = "
        f"{tuple(sorted(aggregate_selected_spreads.items()))}"
    )
    print(
        "AGGREGATE_DANGEROUS_SELECTED_SPREADS = "
        f"{tuple(sorted(aggregate_lineage_selected.items()))}"
    )
    print(
        "claim_boundary = exact finite obstruction through GT_8; "
        "history-sensitive lexicographic tail exclusion remains open"
    )


if __name__ == "__main__":
    self_test()
