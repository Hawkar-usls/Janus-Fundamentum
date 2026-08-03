#!/usr/bin/env python3
"""Certify that raw same-cut double bridges do not reach frozen eligibility.

The broad candidate lemma

    "one frozen local-Resolution pass never creates a same-cut double bridge"

is false.  On the finite pre-frontier GT_4,...,GT_8 trace there is one raw
same-cut pair in a Resolution output.  One parent is an entry-key clause and
the other is a fresh resolvent produced during that same frozen pass.  Hence the
pair is not co-eligible during the pass which creates it.

This checker follows every raw same-cut occurrence through the next executed
branch transition and child pre-unit closure.  It records whether both source
clauses survive, whether their complementary pivot survives, and whether any
same-cut double-bridge pair appears in the next exact key.

The finite target is temporal exclusion, not raw non-creation:

    raw same-cut transient exists;
    no raw same-cut transient becomes a frozen exact-key parent pair.

No arbitrary-n theorem is claimed.
"""

from __future__ import annotations

from collections import Counter, defaultdict

from janus_tear_gt_component_merge_sources import reduce_clause
from janus_tear_gt_component_tree_clause_audit import execution_context
from janus_tear_gt_double_bridge_transition_birth import (
    enumerate_double_bridges,
    unit_assignments,
)
from janus_tear_gt_resolution_output_double_bridge_creation import output_origins

Clause = tuple[int, ...]


def resolve(left: Clause, right: Clause, pivot: int) -> Clause | None:
    literals = (set(left) - {pivot}) | (set(right) - {-pivot})
    if any(-literal in literals for literal in literals):
        return None
    return tuple(sorted(literals, key=lambda literal: (abs(literal), literal < 0)))


def combine_assignments(*parts: dict[int, bool]) -> dict[int, bool]:
    result: dict[int, bool] = {}
    for part in parts:
        for variable, value in part.items():
            assert variable not in result or result[variable] == value
            result[variable] = value
    return result


def exact_key_for_call(policy, call_id: int) -> tuple[Clause, ...] | None:
    call = policy.calls[call_id]
    pre_result = call.get("pre_result")
    if pre_result is None or call["terminal"] != "STATE":
        return None
    return tuple(tuple(clause) for clause in pre_result)


def audit(n: int):
    context = execution_context(n)
    policy = context["policy"]
    pairs = context["pairs"]
    levels = context["levels"]
    target = n - 2

    counts: Counter[str] = Counter()
    origin_patterns: Counter[tuple[tuple[str, ...], tuple[str, ...]]] = Counter()
    role_patterns: Counter[tuple[str, str]] = Counter()
    child_outcomes: Counter[str] = Counter()
    elimination_causes: Counter[str] = Counter()
    examples = []

    for state in policy.states.values():
        state_id = int(state["id"])
        call_id = int(state["entry_call"])
        novelty = int(levels[call_id])
        if novelty > target:
            continue

        assignment = context["call_after_pre"][call_id]
        output = tuple(tuple(clause) for clause in state["resolution_output"])
        origins = output_origins(state)
        raw_pairs = enumerate_double_bridges(n, output, assignment, pairs)

        for record in raw_pairs:
            left_bridge = record["left_bridge"]
            right_bridge = record["right_bridge"]
            if left_bridge["cut"] != right_bridge["cut"]:
                continue

            counts["raw_same_cut_occurrences"] += 1
            pivot = int(record["pivot"])
            left = tuple(record["left"])
            right = tuple(record["right"])
            left_origins = tuple(sorted(origins[left]))
            right_origins = tuple(sorted(origins[right]))
            origin_patterns[(left_origins, right_origins)] += 1
            roles = tuple(sorted((
                str(left_bridge["role"]),
                str(right_bridge["role"]),
            )))
            role_patterns[roles] += 1

            resolvent = resolve(left, right, pivot)
            if resolvent is None:
                counts["tautological_raw_resolvents"] += 1
            else:
                counts["legal_raw_resolvents"] += 1

            fresh_sides = int("ENTRY_KEY" not in origins[left]) + int(
                "ENTRY_KEY" not in origins[right]
            )
            counts[f"raw_same_cut_with_{fresh_sides}_fresh_sides"] += 1
            assert fresh_sides > 0, (
                "a same-cut pair already co-eligible in the entry key would "
                "contradict the exact-key same-cut census"
            )

            children = tuple(
                child
                for child in state.get("children", ())
                if child.get("call") is not None
            )
            counts["executed_child_transitions"] += len(children)
            if not children:
                child_outcomes["NO_EXECUTED_CHILD"] += 1

            child_records = []
            for child in children:
                child_call_id = int(child["call"])
                branch_literal = int(child["literal"])
                branch_assignment = {
                    abs(branch_literal): branch_literal > 0
                }
                child_pre_units = unit_assignments(
                    policy.calls[child_call_id].get("pre_units", ())
                )
                transition_assignment = combine_assignments(
                    branch_assignment, child_pre_units
                )

                left_residual = reduce_clause(left, transition_assignment)
                right_residual = reduce_clause(right, transition_assignment)
                next_key = exact_key_for_call(policy, child_call_id)

                if left_residual is None and right_residual is None:
                    source_outcome = "BOTH_SOURCE_CLAUSES_REMOVED"
                elif left_residual is None:
                    source_outcome = "LEFT_SOURCE_CLAUSE_REMOVED"
                elif right_residual is None:
                    source_outcome = "RIGHT_SOURCE_CLAUSE_REMOVED"
                elif pivot not in left_residual or -pivot not in right_residual:
                    source_outcome = "COMPLEMENTARY_PIVOT_REMOVED"
                elif next_key is None:
                    source_outcome = "BOTH_SURVIVE_BUT_CHILD_TERMINAL"
                elif left_residual not in next_key or right_residual not in next_key:
                    source_outcome = "SOURCE_PAIR_NOT_BOTH_IN_NEXT_KEY"
                else:
                    source_outcome = "SOURCE_PAIR_BOTH_IN_NEXT_KEY"
                child_outcomes[source_outcome] += 1

                next_same_cut_pairs = ()
                source_pair_reappears = False
                if next_key is not None:
                    next_assignment = context["call_after_pre"][child_call_id]
                    next_pairs = enumerate_double_bridges(
                        n, next_key, next_assignment, pairs
                    )
                    next_same_cut_pairs = tuple(
                        pair_record
                        for pair_record in next_pairs
                        if pair_record["left_bridge"]["cut"]
                        == pair_record["right_bridge"]["cut"]
                    )
                    counts["next_exact_key_same_cut_occurrences"] += len(
                        next_same_cut_pairs
                    )
                    source_pair_reappears = any(
                        int(pair_record["pivot"]) == pivot
                        and tuple(pair_record["left"]) == left_residual
                        and tuple(pair_record["right"]) == right_residual
                        for pair_record in next_same_cut_pairs
                    )

                if source_pair_reappears:
                    counts["source_same_cut_reappears"] += 1
                else:
                    counts["source_same_cut_eliminated"] += 1
                    elimination_causes[source_outcome] += 1

                child_records.append({
                    "child_call_id": child_call_id,
                    "branch_literal": branch_literal,
                    "child_pre_units": tuple(sorted(child_pre_units.items())),
                    "left_residual": left_residual,
                    "right_residual": right_residual,
                    "next_key_terminal": next_key is None,
                    "source_outcome": source_outcome,
                    "next_same_cut_count": len(next_same_cut_pairs),
                    "source_pair_reappears": source_pair_reappears,
                })

            examples.append({
                "n": n,
                "state_id": state_id,
                "call_id": call_id,
                "novelty": novelty,
                "pivot": pivot,
                "left": left,
                "right": right,
                "left_origins": left_origins,
                "right_origins": right_origins,
                "roles": roles,
                "cut": left_bridge["cut"],
                "resolvent": resolvent,
                "fresh_sides": fresh_sides,
                "children": tuple(child_records),
            })

    return {
        "n": n,
        "target": target,
        "counts": tuple(sorted(counts.items())),
        "origin_patterns": tuple(sorted(origin_patterns.items(), key=repr)),
        "role_patterns": tuple(sorted(role_patterns.items(), key=repr)),
        "child_outcomes": tuple(sorted(child_outcomes.items())),
        "elimination_causes": tuple(sorted(elimination_causes.items())),
        "examples": tuple(examples),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_origins: Counter[tuple[tuple[str, ...], tuple[str, ...]]] = Counter()
    aggregate_roles: Counter[tuple[str, str]] = Counter()
    aggregate_outcomes: Counter[str] = Counter()
    aggregate_causes: Counter[str] = Counter()
    rows = []

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_origins.update(dict(data["origin_patterns"]))
        aggregate_roles.update(dict(data["role_patterns"]))
        aggregate_outcomes.update(dict(data["child_outcomes"]))
        aggregate_causes.update(dict(data["elimination_causes"]))
        rows.append((
            n,
            data["target"],
            data["counts"],
            data["origin_patterns"],
            data["role_patterns"],
            data["child_outcomes"],
        ))
        print(f"ORDER_SIZE = {n}")
        print(f"  target = {data['target']}")
        print(f"  counts = {data['counts']}")
        print(f"  origin_patterns = {data['origin_patterns']}")
        print(f"  role_patterns = {data['role_patterns']}")
        print(f"  child_outcomes = {data['child_outcomes']}")
        print(f"  elimination_causes = {data['elimination_causes']}")
        print(f"  examples = {data['examples']}")

    assert aggregate_counts["raw_same_cut_occurrences"] == 1
    assert aggregate_counts["legal_raw_resolvents"] == 1
    assert aggregate_counts["raw_same_cut_with_1_fresh_sides"] == 1
    assert aggregate_counts["raw_same_cut_with_0_fresh_sides"] == 0
    assert aggregate_counts["next_exact_key_same_cut_occurrences"] == 0
    assert aggregate_counts["source_same_cut_reappears"] == 0
    assert aggregate_counts["source_same_cut_eliminated"] == aggregate_counts[
        "executed_child_transitions"
    ]

    print("JANUS_GT_SAME_CUT_TRANSIENT_ELIMINATION = PASS")
    print(f"ROWS = {tuple(rows)}")
    print(f"AGGREGATE_COUNTS = {tuple(sorted(aggregate_counts.items()))}")
    print(f"AGGREGATE_ORIGIN_PATTERNS = {tuple(sorted(aggregate_origins.items(), key=repr))}")
    print(f"AGGREGATE_ROLE_PATTERNS = {tuple(sorted(aggregate_roles.items(), key=repr))}")
    print(f"AGGREGATE_CHILD_OUTCOMES = {tuple(sorted(aggregate_outcomes.items()))}")
    print(f"AGGREGATE_ELIMINATION_CAUSES = {tuple(sorted(aggregate_causes.items()))}")
    print(
        "claim_boundary = exact finite elimination of every raw same-cut "
        "transient through GT_8 before frozen exact-key eligibility; "
        "arbitrary-n temporal exclusion remains open"
    )


if __name__ == "__main__":
    self_test()
