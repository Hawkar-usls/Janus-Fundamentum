#!/usr/bin/env python3
"""Trace unsafe low-rank local resolvents across one Policy-0A state boundary.

A generic safe-parent Resolution inference can create an acyclic low-rank clause.
Policy-0A cannot reuse a fresh resolvent in the same pass, so the clause matters
only if it survives:

  local output -> post-unit reduction -> chosen child branch -> child pre-units
  -> exact child key.

For every unsafe new pre-frontier resolvent this audit classifies every actual
child edge as satisfied, terminal before key, absent from the key, inherited but
structurally safe after contraction, or inherited and still unsafe.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_component_merge_sources import reduce_clause
from janus_tear_gt_component_tree_clause_audit import execution_context
from janus_tear_gt_rank_safety_dichotomy import safety_class


def unit_assignments(events) -> dict[int, bool]:
    result: dict[int, bool] = {}
    for event in events:
        if event["kind"] != "unit":
            continue
        literal = int(event["literal"])
        result[abs(literal)] = literal > 0
    return result


def reduce_under(clause, assignments):
    residual = tuple(clause)
    for variable, value in sorted(assignments.items()):
        result = reduce_clause(residual, {variable: value})
        if result is None:
            return None
        residual = result
    return residual


def audit(n: int):
    context = execution_context(n)
    policy = context["policy"]
    pairs = context["pairs"]
    levels = context["levels"]
    target = n - 2

    counts: Counter[str] = Counter()
    birth_deficit_histogram: Counter[int] = Counter()
    child_outcome_histogram: Counter[str] = Counter()
    inherited_class_histogram: Counter[str] = Counter()
    examples = []

    for state in policy.states.values():
        state_id = int(state["id"])
        call_id = int(state["entry_call"])
        novelty = int(levels[call_id])
        if novelty > target:
            continue
        birth_assignment = context["call_after_pre"][call_id]
        post_assignment = unit_assignments(state.get("post_units", []))

        unsafe_births = []
        for event_index, event in enumerate(state.get("resolution_events", [])):
            clause = tuple(event["resolvent"])
            structure = safety_class(n, clause, birth_assignment, pairs)
            if structure["classification"] != "UNSAFE_ACYCLIC_LOW_RANK":
                continue
            unsafe_births.append((event_index, clause, structure))
            counts["unsafe_births"] += 1
            birth_deficit_histogram[int(structure["rank_deficit"])] += 1

        if not unsafe_births:
            continue

        for event_index, clause, birth_structure in unsafe_births:
            post_clause = reduce_under(clause, post_assignment)
            if post_clause is None:
                counts["killed_by_post_units"] += 1
                child_outcome_histogram["KILLED_BY_POST_UNITS"] += 1
                continue

            if state["terminal"] not in ("BRANCH_UNSAT", "BRANCH_SAT"):
                counts["born_in_terminal_state"] += 1
                child_outcome_histogram["TERMINAL_STATE"] += 1
                continue

            for child in state["children"]:
                if child["call"] is None:
                    counts["direct_conflict_child"] += 1
                    child_outcome_histogram["DIRECT_CONFLICT_CHILD"] += 1
                    continue

                child_call_id = int(child["call"])
                branch_literal = int(child["literal"])
                branch_assignment = {abs(branch_literal): branch_literal > 0}
                branch_clause = reduce_clause(post_clause, branch_assignment)
                if branch_clause is None:
                    outcome = "SATISFIED_BY_BRANCH"
                    counts["satisfied_by_branch"] += 1
                    child_outcome_histogram[outcome] += 1
                    continue

                child_call = policy.calls[child_call_id]
                pre_assignment = unit_assignments(child_call.get("pre_units", []))
                child_clause = reduce_under(branch_clause, pre_assignment)
                if child_clause is None:
                    outcome = "SATISFIED_BY_CHILD_UNITS"
                    counts["satisfied_by_child_units"] += 1
                    child_outcome_histogram[outcome] += 1
                    continue

                if child_call.get("key") is None:
                    outcome = "CHILD_TERMINAL_BEFORE_KEY"
                    counts["child_terminal_before_key"] += 1
                    child_outcome_histogram[outcome] += 1
                    continue

                child_key = tuple(child_call["key"])
                if child_clause not in child_key:
                    outcome = "ABSENT_FROM_CHILD_KEY"
                    counts["absent_from_child_key"] += 1
                    child_outcome_histogram[outcome] += 1
                    continue

                child_assignment = context["call_after_pre"][child_call_id]
                child_structure = safety_class(
                    n, child_clause, child_assignment, pairs
                )
                child_class = str(child_structure["classification"])
                inherited_class_histogram[child_class] += 1
                counts["inherited_into_child_key"] += 1
                if child_class == "UNSAFE_ACYCLIC_LOW_RANK":
                    outcome = "INHERITED_STILL_UNSAFE"
                    counts["inherited_still_unsafe"] += 1
                else:
                    outcome = "INHERITED_BECAME_SAFE"
                    counts["inherited_became_safe"] += 1
                child_outcome_histogram[outcome] += 1

                if len(examples) < 40:
                    examples.append(
                        {
                            "n": n,
                            "birth_state": state_id,
                            "birth_call": call_id,
                            "birth_novelty": novelty,
                            "event_index": event_index,
                            "birth_clause": clause,
                            "birth_structure": birth_structure,
                            "post_clause": post_clause,
                            "branch_literal": branch_literal,
                            "child_call": child_call_id,
                            "child_novelty": int(levels[child_call_id]),
                            "child_clause": child_clause,
                            "child_structure": child_structure,
                            "outcome": outcome,
                        }
                    )

                if child["result"]:
                    break

    return {
        "n": n,
        "target": target,
        "counts": tuple(sorted(counts.items())),
        "birth_deficit_histogram": tuple(sorted(birth_deficit_histogram.items())),
        "child_outcome_histogram": tuple(sorted(child_outcome_histogram.items())),
        "inherited_class_histogram": tuple(sorted(inherited_class_histogram.items())),
        "examples": tuple(examples),
    }


def self_test() -> None:
    rows = []
    aggregate: Counter[str] = Counter()
    aggregate_outcomes: Counter[str] = Counter()
    aggregate_inherited: Counter[str] = Counter()

    for n in range(4, 9):
        data = audit(n)
        aggregate.update(dict(data["counts"]))
        aggregate_outcomes.update(dict(data["child_outcome_histogram"]))
        aggregate_inherited.update(dict(data["inherited_class_histogram"]))
        rows.append(
            (
                n,
                data["target"],
                data["counts"],
                data["birth_deficit_histogram"],
                data["child_outcome_histogram"],
            )
        )
        print(f"ORDER_SIZE = {n}")
        print(f"  target = {data['target']}")
        print(f"  counts = {data['counts']}")
        print(f"  birth_deficit_histogram = {data['birth_deficit_histogram']}")
        print(f"  child_outcome_histogram = {data['child_outcome_histogram']}")
        print(f"  inherited_class_histogram = {data['inherited_class_histogram']}")
        print(f"  examples = {data['examples']}")

    print("JANUS_GT_UNSAFE_CLAUSE_ONE_GENERATION = PASS")
    print(f"rows = {tuple(rows)}")
    print(f"aggregate_counts = {tuple(sorted(aggregate.items()))}")
    print(f"aggregate_outcomes = {tuple(sorted(aggregate_outcomes.items()))}")
    print(f"aggregate_inherited_classes = {tuple(sorted(aggregate_inherited.items()))}")
    print("claim_boundary = finite one-generation lifecycle; recursive unsafe provenance remains open")


if __name__ == "__main__":
    self_test()
