#!/usr/bin/env python3
"""Classify root-axiom ancestry of every pre-unit GT component merge.

For each source-certified pre-unit component merge, reconstruct the complete
assignment immediately before the unit and test whether an original root clause
reduces exactly to that literal.  The result deliberately permits DERIVED_ONLY:
that class is the remaining object to trace through parent local-Resolution
provenance rather than an assertion failure to hide.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_component_merge_sources import audit as merge_source_audit, reduce_clause
from janus_tear_gt_critical_order_damage import pair_variables
from janus_tear_gt_novel_branch_audit_v2 import add_units
from janus_tear_policy0a_fc_trace import FCTracePolicy, verify_fc_trace
from janus_tear_policy0a_graph_tautology_probe import graph_tautology_cnf

Clause = tuple[int, ...]


def less_literal(left: int, right: int, inverse_pairs: dict[tuple[int, int], int]) -> int:
    return inverse_pairs[(left, right)] if left < right else -inverse_pairs[(right, left)]


def non_minimality_clauses(n: int, pairs: dict[int, tuple[int, int]]) -> set[Clause]:
    inverse = {pair: variable for variable, pair in pairs.items()}
    return {
        tuple(sorted(
            (less_literal(other, vertex, inverse) for other in range(n) if other != vertex),
            key=lambda literal: (abs(literal), literal < 0),
        ))
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
    assert result.answer is False and root_call is not None
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
                minimum_candidates = tuple(c for c in candidates if c in minimum_axioms)
                transitivity_candidates = tuple(c for c in candidates if c not in minimum_axioms)
                source_class = (
                    "ORIGINAL_NON_MINIMALITY" if minimum_candidates else
                    "ORIGINAL_TRANSITIVITY" if transitivity_candidates else
                    "DERIVED_ONLY"
                )
                classification[source_class] += 1
                ancestry_records.append({
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
                    "residual_source_clause": tuple(target_records[key]["source_clause"]),
                })
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
    assert sum(classification.values()) == len(target_records)
    assert classification["ORIGINAL_TRANSITIVITY"] == 0

    return {
        "n": n,
        "pre_unit_component_merges": len(target_records),
        "classification": tuple(sorted(classification.items())),
        "derived_only": classification["DERIVED_ONLY"],
        "original_non_minimality": classification["ORIGINAL_NON_MINIMALITY"],
        "records": tuple(ancestry_records),
    }


def self_test() -> None:
    rows = []
    total_derived = 0
    total_original = 0
    for n in range(4, 9):
        data = audit(n)
        total_derived += data["derived_only"]
        total_original += data["original_non_minimality"]
        rows.append((n, data["pre_unit_component_merges"], data["classification"]))
        print(f"ORDER_SIZE = {n}")
        print(f"  pre_unit_component_merges = {data['pre_unit_component_merges']}")
        print(f"  classification = {data['classification']}")
        print(f"  records = {data['records']}")

    print("JANUS_GT_UNIT_MERGE_ROOT_ANCESTRY = PASS")
    print(f"rows = {tuple(rows)}")
    print(f"original_non_minimality_total = {total_original}")
    print(f"derived_only_total = {total_derived}")
    print("claim_boundary = finite ancestry classification; DERIVED_ONLY events require parent-resolution tracing")


if __name__ == "__main__":
    self_test()
