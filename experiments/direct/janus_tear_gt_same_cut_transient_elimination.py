#!/usr/bin/env python3
"""Replay every raw same-cut double bridge through frozen eligibility.

Raw same-cut noncreation is false.  The pre-frontier GT_4,...,GT_8 traces
contain exactly two same-cut pairs in frozen Resolution outputs:

- GT_4: one entry clause plus one fresh resolvent.  It survives to the
  post-result, then one reached child is terminal while both residual clauses
  remain and the other child removes the fresh side by pre-unit closure.
- GT_5: two fresh complementary unit clauses.  They close immediately as a
  post-unit contradiction and never produce a post-result.

Neither transient reaches a later exact key as a co-eligible same-cut parent
pair.  This is a finite temporal-extinction certificate, not an arbitrary-n
proof.
"""

from __future__ import annotations

from collections import Counter

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
    post_outcomes: Counter[str] = Counter()
    child_outcomes: Counter[str] = Counter()
    terminal_labels: Counter[str] = Counter()
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

        for record in enumerate_double_bridges(n, output, assignment, pairs):
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

            raw_resolvent = resolve(left, right, pivot)
            if raw_resolvent is None:
                counts["tautological_raw_resolvents"] += 1
            else:
                counts["legal_raw_resolvents"] += 1

            fresh_sides = int("ENTRY_KEY" not in origins[left]) + int(
                "ENTRY_KEY" not in origins[right]
            )
            counts[f"raw_same_cut_with_{fresh_sides}_fresh_sides"] += 1
            assert fresh_sides > 0

            post_result = state.get("post_result")
            post_record: dict[str, object]
            child_records = []

            if post_result is None:
                counts["eliminated_before_post_result"] += 1
                post_outcomes["POST_UNIT_TERMINAL_EXTINCTION"] += 1
                terminal = str(state.get("terminal"))
                terminal_labels[terminal] += 1
                if left == (pivot,) and right == (-pivot,):
                    counts["complementary_unit_conflict_pairs"] += 1
                post_record = {
                    "outcome": "POST_UNIT_TERMINAL_EXTINCTION",
                    "terminal": terminal,
                    "post_unit_events": tuple(
                        (str(event["kind"]), event.get("literal"))
                        for event in state.get("post_units", ())
                    ),
                }
            else:
                post = tuple(tuple(clause) for clause in post_result)
                after_assignment = context["state_after_post"][state_id]
                post_same_cut = tuple(
                    pair_record
                    for pair_record in enumerate_double_bridges(
                        n, post, after_assignment, pairs
                    )
                    if pair_record["left_bridge"]["cut"]
                    == pair_record["right_bridge"]["cut"]
                )
                source_survives = any(
                    int(pair_record["pivot"]) == pivot
                    and tuple(pair_record["left"]) == left
                    and tuple(pair_record["right"]) == right
                    for pair_record in post_same_cut
                )
                assert source_survives
                counts["survives_to_post_result"] += 1
                post_outcomes["SURVIVES_TO_POST_RESULT"] += 1
                post_record = {
                    "outcome": "SURVIVES_TO_POST_RESULT",
                    "post_same_cut_count": len(post_same_cut),
                }

                children = tuple(
                    child
                    for child in state.get("children", ())
                    if child.get("call") is not None
                )
                counts["executed_child_transitions"] += len(children)

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

                    next_same_cut = ()
                    source_reappears = False
                    if next_key is not None:
                        next_assignment = context["call_after_pre"][child_call_id]
                        next_same_cut = tuple(
                            pair_record
                            for pair_record in enumerate_double_bridges(
                                n, next_key, next_assignment, pairs
                            )
                            if pair_record["left_bridge"]["cut"]
                            == pair_record["right_bridge"]["cut"]
                        )
                        counts["next_exact_key_same_cut_occurrences"] += len(
                            next_same_cut
                        )
                        source_reappears = any(
                            int(pair_record["pivot"]) == pivot
                            and tuple(pair_record["left"]) == left_residual
                            and tuple(pair_record["right"]) == right_residual
                            for pair_record in next_same_cut
                        )
                    if source_reappears:
                        counts["source_same_cut_reappears"] += 1
                    else:
                        counts["source_same_cut_eliminated_on_child"] += 1

                    child_records.append({
                        "child_call_id": child_call_id,
                        "branch_literal": branch_literal,
                        "child_pre_units": tuple(sorted(child_pre_units.items())),
                        "left_residual": left_residual,
                        "right_residual": right_residual,
                        "next_key_terminal": next_key is None,
                        "source_outcome": source_outcome,
                        "next_same_cut_count": len(next_same_cut),
                        "source_reappears": source_reappears,
                    })

            examples.append({
                "n": n,
                "state_id": state_id,
                "call_id": call_id,
                "novelty": novelty,
                "pivot": pivot,
                "left": left,
                "right": right,
                "origins": (left_origins, right_origins),
                "roles": roles,
                "cut": left_bridge["cut"],
                "resolvent": raw_resolvent,
                "fresh_sides": fresh_sides,
                "post": post_record,
                "children": tuple(child_records),
            })

    return {
        "n": n,
        "target": target,
        "counts": tuple(sorted(counts.items())),
        "origin_patterns": tuple(sorted(origin_patterns.items(), key=repr)),
        "role_patterns": tuple(sorted(role_patterns.items(), key=repr)),
        "post_outcomes": tuple(sorted(post_outcomes.items())),
        "child_outcomes": tuple(sorted(child_outcomes.items())),
        "terminal_labels": tuple(sorted(terminal_labels.items())),
        "examples": tuple(examples),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_origins: Counter[tuple[tuple[str, ...], tuple[str, ...]]] = Counter()
    aggregate_roles: Counter[tuple[str, str]] = Counter()
    aggregate_post_outcomes: Counter[str] = Counter()
    aggregate_child_outcomes: Counter[str] = Counter()
    aggregate_terminals: Counter[str] = Counter()
    rows = []

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_origins.update(dict(data["origin_patterns"]))
        aggregate_roles.update(dict(data["role_patterns"]))
        aggregate_post_outcomes.update(dict(data["post_outcomes"]))
        aggregate_child_outcomes.update(dict(data["child_outcomes"]))
        aggregate_terminals.update(dict(data["terminal_labels"]))
        rows.append((
            n,
            data["target"],
            data["counts"],
            data["origin_patterns"],
            data["role_patterns"],
            data["post_outcomes"],
            data["child_outcomes"],
        ))
        print(f"ORDER_SIZE = {n}")
        print(f"  target = {data['target']}")
        print(f"  counts = {data['counts']}")
        print(f"  origin_patterns = {data['origin_patterns']}")
        print(f"  role_patterns = {data['role_patterns']}")
        print(f"  post_outcomes = {data['post_outcomes']}")
        print(f"  child_outcomes = {data['child_outcomes']}")
        print(f"  terminal_labels = {data['terminal_labels']}")
        print(f"  examples = {data['examples']}")

    assert aggregate_counts["raw_same_cut_occurrences"] == 2
    assert aggregate_counts["legal_raw_resolvents"] == 2
    assert aggregate_counts["raw_same_cut_with_1_fresh_sides"] == 1
    assert aggregate_counts["raw_same_cut_with_2_fresh_sides"] == 1
    assert aggregate_counts["raw_same_cut_with_0_fresh_sides"] == 0
    assert aggregate_counts["complementary_unit_conflict_pairs"] == 1
    assert aggregate_counts["eliminated_before_post_result"] == 1
    assert aggregate_counts["survives_to_post_result"] == 1
    assert aggregate_counts["executed_child_transitions"] == 2
    assert aggregate_counts["next_exact_key_same_cut_occurrences"] == 0
    assert aggregate_counts["source_same_cut_reappears"] == 0
    assert aggregate_counts["source_same_cut_eliminated_on_child"] == 2
    assert aggregate_child_outcomes == Counter({
        "BOTH_SURVIVE_BUT_CHILD_TERMINAL": 1,
        "RIGHT_SOURCE_CLAUSE_REMOVED": 1,
    })
    assert aggregate_terminals == Counter({"POST_UNIT_CONTRADICTION": 1})

    print("JANUS_GT_SAME_CUT_TRANSIENT_ELIMINATION = PASS")
    print(f"ROWS = {tuple(rows)}")
    print(f"AGGREGATE_COUNTS = {tuple(sorted(aggregate_counts.items()))}")
    print(f"AGGREGATE_ORIGIN_PATTERNS = {tuple(sorted(aggregate_origins.items(), key=repr))}")
    print(f"AGGREGATE_ROLE_PATTERNS = {tuple(sorted(aggregate_roles.items(), key=repr))}")
    print(f"AGGREGATE_POST_OUTCOMES = {tuple(sorted(aggregate_post_outcomes.items()))}")
    print(f"AGGREGATE_CHILD_OUTCOMES = {tuple(sorted(aggregate_child_outcomes.items()))}")
    print(f"AGGREGATE_TERMINAL_LABELS = {tuple(sorted(aggregate_terminals.items()))}")
    print(
        "claim_boundary = exact finite extinction of both raw same-cut "
        "transients through GT_8 before frozen exact-key eligibility; "
        "arbitrary-n temporal exclusion remains open"
    )


if __name__ == "__main__":
    self_test()
