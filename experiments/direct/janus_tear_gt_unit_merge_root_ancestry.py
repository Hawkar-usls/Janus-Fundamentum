#!/usr/bin/env python3
"""Trace every pre-unit component merge back to original smart-GT axioms.

The symbolic C024 unit-safety lemma proves:
- a transitivity axiom can only produce an internal comparison unit;
- a non-minimality axiom can join components only after at least n-2 joins.

This audit cross-checks the exact Policy-0A traces.  For each source-certified
pre-unit component merge, it reconstructs the full assignment immediately before
the unit and asks which original root clauses reduce exactly to that unit.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_component_merge_sources import (
    audit as merge_source_audit,
    reduce_clause,
)
from janus_tear_gt_critical_order_damage import pair_variables
from janus_tear_gt_novel_branch_audit_v2 import add_units
from janus_tear_policy0a_fc_trace import FCTracePolicy, verify_fc_trace
from janus_tear_policy0a_graph_tautology_probe import graph_tautology_cnf

Clause = tuple[int, ...]


def less_literal(
    left: int,
    right: int,
    inverse_pairs: dict[tuple[int, int], int],
) -> int:
    if left < right:
        return inverse_pairs[(left, right)]
    return -inverse_pairs[(right, left)]


def non_minimality_clauses(n: int, pairs: dict[int, tuple[int, int]]) -> set[Clause]:
    inverse = {pair: variable for variable, pair in pairs.items()}
    return {
        tuple(
            sorted(
                (less_literal(other, vertex, inverse) for other in range(n) if other != vertex),
                key=lambda literal: (abs(literal), literal < 0),
            )
        )
        for vertex in range(n)
    }


def audit(n: int):
    root, variable_count = graph_tautology_cnf(n)
    pairs = pair_variables(n)
    minimum_axioms = non_minimality_clauses(n, pairs)
    assert minimum_axioms.issubset(set(root))

    merge_data = merge_source_audit(n)
    target_records = {
        (int(record["call_id"]), int(record["event_index"])): record
        for record in merge_data["records"]
        if record["stage"] == "pre"
    }

    policy = FCTracePolicy()
    result, root_call = policy.solve(root, variable_count)
    assert result.answer is False
    assert root_call is not None
    assert verify_fc_trace(root, variable_count, policy, root_call) is False

    seen: set[int] = set()
    ancestry_records = []
    classification: Counter[str] = Counter()

    def walk(call_id: int, incoming: dict[int, bool]) -> None:
        assert call_id not in seen
        seen.add(call_id)
        call = policy.calls[call_id]

        current = dict(incoming)
        for event_index, event in enumerate(call.get("pre_units", [])):
            if event["kind"] != "unit":
                continue
            literal = int(event["literal"])
            key = (call_id, event_index)
            if key in target_records:
                candidates = tuple(
                    clause for clause in root if reduce_clause(clause, current) == (literal,)
                )
                minimum_candidates = tuple(
                    clause for clause in candidates if clause in minimum_axioms
                )
                transitivity_candidates = tuple(
                    clause for clause in candidates if clause not in minimum_axioms
                )
                source_class = (
                    "ORIGINAL_NON_MINIMALITY"
                    if minimum_candidates
                    else (
                        "ORIGINAL_TRANSITIVITY"
                        if transitivity_candidates
                        else "DERIVED_ONLY"
                    )
                )
                classification[source_class] += 1
                ancestry_records.append(
                    {
                        "n": n,
                        "call_id": call_id,
                        "event_index": event_index,
                        "literal": literal,
                        "pair": pairs[abs(literal)],
                        "source_class": source_class,
                        "root_candidate_count": len(candidates),
                        "minimum_candidate_count": len(minimum_candidates),
                        "transitivity_candidate_count": len(transitivity_candidates),
                        "minimum_candidates": minimum_candidates,
                        "transitivity_candidates": transitivity_candidates,
                    }
                )

            current[abs(literal)] = literal > 0

        if call["terminal"] != "STATE":
            return

        state = policy.states[int(call["state"])]
        after_post, _, _ = add_units(current, state.get("post_units", []))
        if state["terminal"] not in ("BRANCH_UNSAT", "BRANCH_SAT"):
            return

        variable = int(state["branch_var"])
        for child in state["children"]:
            if child["call"] is None:
                continue
            child_assignment = dict(after_post)
            child_assignment[variable] = bool(child["value"])
            walk(int(child["call"]), child_assignment)
            if child["result"]:
                break

    walk(root_call, {})
    assert len(seen) == len(policy.calls)
    assert len(ancestry_records) == len(target_records)
    assert classification["DERIVED_ONLY"] == 0
    assert classification["ORIGINAL_TRANSITIVITY"] == 0
    assert classification["ORIGINAL_NON_MINIMALITY"] == len(target_records)

    return {
        "n": n,
        "pre_unit_component_merges": len(target_records),
        "classification": tuple(sorted(classification.items())),
        "records": tuple(ancestry_records),
    }


def self_test() -> None:
    rows = []
    for n in range(4, 9):
        data = audit(n)
        rows.append((n, data["pre_unit_component_merges"], data["classification"]))
        print(f"ORDER_SIZE = {n}")
        print(f"  pre_unit_component_merges = {data['pre_unit_component_merges']}")
        print(f"  classification = {data['classification']}")
        print(f"  records = {data['records']}")

    print("JANUS_GT_UNIT_MERGE_ROOT_ANCESTRY = PASS")
    print(f"rows = {tuple(rows)}")
    print("finite_result = every observed pre-unit component merge is directly licensed by an original non-minimality axiom")
    print("claim_boundary = finite root-ancestry cross-check; derived-only early units remain the asymptotic danger")


if __name__ == "__main__":
    self_test()
