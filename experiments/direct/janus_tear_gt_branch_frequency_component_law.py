#!/usr/bin/env python3
"""Test whether Policy-0A branch frequency factors through quotient components.

The surviving singleton-tail handoff profile shows that the selected branch
never touches the dangerous tail: 39 choices join the head to another
component and three are disjoint after the head is already merged.  The open
proof question is whether this follows from a component-level frequency law or
from finer clause-history information.

For every pre-frontier branch state through GT_8, this audit groups every
present comparison variable by the unordered pair of current relation
components containing its endpoints.  It records:

- whether all original comparisons between the same two components have equal
  absolute-literal frequency;
- the frequency spread inside each component-pair group;
- whether the selected variable's group is uniform;
- whether different component pairs with the same size profile have equal
  maximum frequencies;
- the same statistics on the 42 surviving dangerous lineages.

A universal uniformity result would support a quotient-component selector
lemma.  Any violation is printed as a proof obstruction rather than hidden.
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
    frequencies = Counter(
        abs(literal) for clause in cnf for literal in clause
    )
    selected = int(state["branch_var"])
    maximum = max(frequencies.values())
    assert frequencies[selected] == maximum

    groups: dict[tuple[int, int], list[int]] = defaultdict(list)
    for variable in frequencies:
        groups[component_pair(index, pairs[int(variable)])].append(int(variable))

    group_rows = []
    for pair, variables in sorted(groups.items()):
        values = tuple(sorted(frequencies[variable] for variable in variables))
        sizes = tuple(sorted((
            len(parts[pair[0]]),
            len(parts[pair[1]]),
        )))
        group_rows.append({
            "component_pair": pair,
            "component_sizes": sizes,
            "variables": tuple(sorted(variables)),
            "frequencies": values,
            "minimum": min(values),
            "maximum": max(values),
            "spread": max(values) - min(values),
            "uniform": len(set(values)) == 1,
            "contains_selected": selected in variables,
        })

    selected_pair = component_pair(index, pairs[selected])
    selected_group = next(
        row for row in group_rows if row["component_pair"] == selected_pair
    )

    size_profile_maxima: dict[tuple[int, int], list[int]] = defaultdict(list)
    for row in group_rows:
        size_profile_maxima[row["component_sizes"]].append(int(row["maximum"]))
    size_rows = tuple({
        "component_sizes": sizes,
        "pair_maxima": tuple(sorted(values)),
        "uniform_across_pairs": len(set(values)) == 1,
        "spread": max(values) - min(values),
    } for sizes, values in sorted(size_profile_maxima.items()))

    return {
        "state_id": state_id,
        "parts": parts,
        "selected": selected,
        "selected_frequency": maximum,
        "selected_pair": selected_pair,
        "selected_group": selected_group,
        "groups": tuple(group_rows),
        "size_rows": size_rows,
        "all_groups_uniform": all(row["uniform"] for row in group_rows),
        "all_size_profiles_uniform": all(
            row["uniform_across_pairs"] for row in size_rows
        ),
    }


def audit(n: int):
    context = execution_context(n)
    policy = context["policy"]
    levels = context["levels"]
    target = n - 2
    lineage_states = {
        int(record["parent_state"])
        for record in lineage_audit(n)["records"]
    }

    counts: Counter[str] = Counter()
    group_spreads: Counter[int] = Counter()
    selected_group_spreads: Counter[int] = Counter()
    size_profile_spreads: Counter[int] = Counter()
    group_size_histogram: Counter[int] = Counter()
    selected_group_size_histogram: Counter[int] = Counter()
    lineage_group_spreads: Counter[int] = Counter()
    lineage_selected_group_spreads: Counter[int] = Counter()
    examples = []
    lineage_examples = []

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
        if profile["all_size_profiles_uniform"]:
            counts["states_all_size_profiles_uniform"] += 1
        else:
            counts["states_with_nonuniform_size_profile"] += 1

        selected_group = profile["selected_group"]
        if selected_group["uniform"]:
            counts["selected_component_pair_uniform"] += 1
        else:
            counts["selected_component_pair_nonuniform"] += 1
        selected_group_spreads[int(selected_group["spread"])] += 1
        selected_group_size_histogram[len(selected_group["variables"])] += 1

        for row in profile["groups"]:
            counts["component_pair_groups"] += 1
            counts[
                "uniform_component_pair_groups"
                if row["uniform"]
                else "nonuniform_component_pair_groups"
            ] += 1
            group_spreads[int(row["spread"])] += 1
            group_size_histogram[len(row["variables"])] += 1

        for row in profile["size_rows"]:
            size_profile_spreads[int(row["spread"])] += 1

        if not profile["all_groups_uniform"] and len(examples) < 60:
            examples.append(profile)

        if state_id in lineage_states:
            counts["dangerous_lineage_states"] += 1
            lineage_selected_group_spreads[
                int(selected_group["spread"])
            ] += 1
            for row in profile["groups"]:
                lineage_group_spreads[int(row["spread"])] += 1
            if (
                not profile["all_groups_uniform"]
                or not selected_group["uniform"]
            ) and len(lineage_examples) < 60:
                lineage_examples.append(profile)

    assert counts["dangerous_lineage_states"] == len(lineage_states)
    return {
        "n": n,
        "target": target,
        "counts": tuple(sorted(counts.items())),
        "group_spreads": tuple(sorted(group_spreads.items())),
        "selected_group_spreads": tuple(sorted(selected_group_spreads.items())),
        "size_profile_spreads": tuple(sorted(size_profile_spreads.items())),
        "group_size_histogram": tuple(sorted(group_size_histogram.items())),
        "selected_group_size_histogram": tuple(
            sorted(selected_group_size_histogram.items())
        ),
        "lineage_group_spreads": tuple(sorted(lineage_group_spreads.items())),
        "lineage_selected_group_spreads": tuple(
            sorted(lineage_selected_group_spreads.items())
        ),
        "examples": tuple(examples),
        "lineage_examples": tuple(lineage_examples),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_group_spreads: Counter[int] = Counter()
    aggregate_selected_spreads: Counter[int] = Counter()
    aggregate_size_spreads: Counter[int] = Counter()
    aggregate_group_sizes: Counter[int] = Counter()
    aggregate_selected_sizes: Counter[int] = Counter()
    aggregate_lineage_spreads: Counter[int] = Counter()
    aggregate_lineage_selected: Counter[int] = Counter()
    examples = []
    lineage_examples = []

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_group_spreads.update(dict(data["group_spreads"]))
        aggregate_selected_spreads.update(dict(data["selected_group_spreads"]))
        aggregate_size_spreads.update(dict(data["size_profile_spreads"]))
        aggregate_group_sizes.update(dict(data["group_size_histogram"]))
        aggregate_selected_sizes.update(dict(data["selected_group_size_histogram"]))
        aggregate_lineage_spreads.update(dict(data["lineage_group_spreads"]))
        aggregate_lineage_selected.update(
            dict(data["lineage_selected_group_spreads"])
        )
        examples.extend(data["examples"])
        lineage_examples.extend(data["lineage_examples"])
        print(f"ORDER_SIZE = {n}")
        print(f"  target = {data['target']}")
        print(f"  counts = {data['counts']}")
        print(f"  group_spreads = {data['group_spreads']}")
        print(f"  selected_group_spreads = {data['selected_group_spreads']}")
        print(f"  size_profile_spreads = {data['size_profile_spreads']}")
        print(f"  group_size_histogram = {data['group_size_histogram']}")
        print(f"  selected_group_size_histogram = {data['selected_group_size_histogram']}")
        print(f"  lineage_group_spreads = {data['lineage_group_spreads']}")
        print(f"  lineage_selected_group_spreads = {data['lineage_selected_group_spreads']}")
        print(f"  examples = {data['examples']}")
        print(f"  lineage_examples = {data['lineage_examples']}")

    assert aggregate_counts["dangerous_lineage_states"] == 42
    print("JANUS_GT_BRANCH_FREQUENCY_COMPONENT_LAW = PASS")
    print(f"AGGREGATE_COUNTS = {tuple(sorted(aggregate_counts.items()))}")
    print(f"AGGREGATE_GROUP_SPREADS = {tuple(sorted(aggregate_group_spreads.items()))}")
    print(f"AGGREGATE_SELECTED_SPREADS = {tuple(sorted(aggregate_selected_spreads.items()))}")
    print(f"AGGREGATE_SIZE_SPREADS = {tuple(sorted(aggregate_size_spreads.items()))}")
    print(f"AGGREGATE_GROUP_SIZES = {tuple(sorted(aggregate_group_sizes.items()))}")
    print(f"AGGREGATE_SELECTED_SIZES = {tuple(sorted(aggregate_selected_sizes.items()))}")
    print(f"AGGREGATE_LINEAGE_SPREADS = {tuple(sorted(aggregate_lineage_spreads.items()))}")
    print(f"AGGREGATE_LINEAGE_SELECTED = {tuple(sorted(aggregate_lineage_selected.items()))}")
    print(f"NONUNIFORM_EXAMPLES = {tuple(examples)}")
    print(f"LINEAGE_NONUNIFORM_EXAMPLES = {tuple(lineage_examples)}")
    print(
        "claim_boundary = exact finite quotient-component frequency-law audit "
        "through GT_8; no uniformity theorem assumed"
    )


if __name__ == "__main__":
    self_test()
