#!/usr/bin/env python3
"""Trace each derived pre-unit component merge to its parent clause provenance.

Every pre-unit component merge observed by C024 is DERIVED_ONLY with respect to
direct simplification of the original GT_n axioms.  This audit moves one exact
execution level backward.

For a child pre-unit literal l:
1. find every parent post-propagation clause that becomes (l,) under the branch
   assignment creating the child;
2. find every parent resolution-output clause that becomes that post clause
   under the parent's post-unit assignments;
3. classify each antecedent as an explicit local resolvent of the parent state
   or as a clause inherited in the parent's residual key.

The checker replays the exact FC trace and requires every observed child unit to
have at least one parent-clause witness.  It reports rather than assumes whether
that witness is locally derived or inherited.
"""

from __future__ import annotations

from collections import Counter, defaultdict

from janus_tear_gt_component_merge_sources import (
    audit as merge_source_audit,
    reduce_clause,
)
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
        variable = abs(literal)
        value = literal > 0
        assert variable not in result or result[variable] == value
        result[variable] = value
    return result


def event_payload(index: int, event) -> dict[str, object]:
    return {
        "event_index": index,
        "left": tuple(event["left"]),
        "right": tuple(event["right"]),
        "pivot": int(event["pivot"]),
        "resolvent": tuple(event["resolvent"]),
        "attempt": int(event["attempt"]),
    }


def audit(n: int):
    root, variable_count = graph_tautology_cnf(n)
    merge_data = merge_source_audit(n)
    targets = {
        int(record["call_id"]): record
        for record in merge_data["records"]
        if record["stage"] == "pre"
    }

    policy = FCTracePolicy()
    result, root_call = policy.solve(root, variable_count)
    assert result.answer is False
    assert root_call is not None
    assert verify_fc_trace(root, variable_count, policy, root_call) is False

    parent_link: dict[int, dict[str, object]] = {}
    seen: set[int] = set()

    def walk(call_id: int) -> None:
        assert call_id not in seen
        seen.add(call_id)
        call = policy.calls[call_id]
        if call["terminal"] != "STATE":
            return

        state_id = int(call["state"])
        state = policy.states[state_id]
        if state["terminal"] not in ("BRANCH_UNSAT", "BRANCH_SAT"):
            return

        branch_variable = int(state["branch_var"])
        for child in state["children"]:
            child_id = child["call"]
            if child_id is None:
                continue
            child_id = int(child_id)
            assert child_id not in parent_link
            branch_value = bool(child["value"])
            parent_link[child_id] = {
                "parent_call_id": call_id,
                "parent_state_id": state_id,
                "branch_variable": branch_variable,
                "branch_value": branch_value,
                "branch_literal": branch_variable if branch_value else -branch_variable,
            }
            walk(child_id)
            if child["result"]:
                break

    walk(root_call)
    assert len(seen) == len(policy.calls)

    classification: Counter[str] = Counter()
    records: list[dict[str, object]] = []
    parent_clause_widths: Counter[int] = Counter()
    resolution_antecedent_widths: Counter[int] = Counter()
    pivot_variables: Counter[int] = Counter()

    for child_call_id, target in sorted(targets.items()):
        assert child_call_id in parent_link
        link = parent_link[child_call_id]
        parent_call = policy.calls[int(link["parent_call_id"])]
        parent_state = policy.states[int(link["parent_state_id"])]
        literal = int(target["literal"])

        branch_assignment = {
            int(link["branch_variable"]): bool(link["branch_value"])
        }
        parent_post: CNF = tuple(parent_state["post_result"])
        parent_clauses = tuple(
            clause
            for clause in parent_post
            if reduce_clause(clause, branch_assignment) == (literal,)
        )
        assert parent_clauses, (
            n,
            child_call_id,
            literal,
            link,
            tuple(policy.calls[child_call_id]["input"]),
        )

        post_assignment = unit_assignments(parent_state.get("post_units", []))
        resolution_output: CNF = tuple(parent_state["resolution_output"])
        key: CNF = tuple(parent_state["key"])
        resolution_events = parent_state.get("resolution_events", [])
        resolvent_map: dict[Clause, list[tuple[int, object]]] = defaultdict(list)
        for index, event in enumerate(resolution_events):
            resolvent_map[tuple(event["resolvent"])].append((index, event))

        clause_records = []
        local_witnesses = 0
        inherited_witnesses = 0
        unresolved_witnesses = 0

        for parent_clause in parent_clauses:
            parent_clause_widths[len(parent_clause)] += 1
            antecedents = tuple(
                clause
                for clause in resolution_output
                if reduce_clause(clause, post_assignment) == parent_clause
            )
            assert antecedents, (
                n,
                child_call_id,
                literal,
                parent_clause,
                post_assignment,
            )

            antecedent_records = []
            for antecedent in antecedents:
                local_events = resolvent_map.get(antecedent, [])
                in_key = antecedent in key
                if local_events:
                    kind = "PARENT_LOCAL_RESOLVENT"
                    local_witnesses += 1
                elif in_key:
                    kind = "PARENT_INHERITED_KEY"
                    inherited_witnesses += 1
                else:
                    kind = "UNRESOLVED_PARENT_OUTPUT"
                    unresolved_witnesses += 1

                event_records = tuple(
                    event_payload(index, event)
                    for index, event in local_events
                )
                for payload in event_records:
                    resolution_antecedent_widths[len(antecedent)] += 1
                    pivot_variables[int(payload["pivot"])] += 1

                antecedent_records.append(
                    {
                        "antecedent": antecedent,
                        "kind": kind,
                        "in_parent_key": in_key,
                        "local_resolution_events": event_records,
                    }
                )

            clause_records.append(
                {
                    "parent_post_clause": parent_clause,
                    "parent_post_width": len(parent_clause),
                    "antecedents": tuple(antecedent_records),
                }
            )

        if unresolved_witnesses:
            event_class = "HAS_UNRESOLVED_OUTPUT"
        elif local_witnesses and inherited_witnesses:
            event_class = "MIXED_LOCAL_AND_INHERITED"
        elif local_witnesses:
            event_class = "PARENT_LOCAL_RESOLVENT"
        elif inherited_witnesses:
            event_class = "PARENT_INHERITED_KEY"
        else:
            raise AssertionError((n, child_call_id, literal, clause_records))

        classification[event_class] += 1
        records.append(
            {
                "n": n,
                "child_call_id": child_call_id,
                "child_literal": literal,
                "child_pair": tuple(target["pair"]),
                "child_depth": int(target["depth"]),
                "parent_call_id": int(link["parent_call_id"]),
                "parent_state_id": int(link["parent_state_id"]),
                "branch_literal": int(link["branch_literal"]),
                "event_class": event_class,
                "parent_clause_count": len(parent_clauses),
                "parent_clauses": tuple(clause_records),
            }
        )

    assert len(records) == len(targets)
    assert classification["HAS_UNRESOLVED_OUTPUT"] == 0

    return {
        "n": n,
        "pre_unit_component_merges": len(targets),
        "classification": tuple(sorted(classification.items())),
        "parent_clause_widths": tuple(sorted(parent_clause_widths.items())),
        "resolution_antecedent_widths": tuple(
            sorted(resolution_antecedent_widths.items())
        ),
        "pivot_variables": tuple(sorted(pivot_variables.items())),
        "records": tuple(records),
    }


def self_test() -> None:
    rows = []
    aggregate: Counter[str] = Counter()
    for n in range(4, 9):
        data = audit(n)
        aggregate.update(dict(data["classification"]))
        rows.append(
            (
                n,
                data["pre_unit_component_merges"],
                data["classification"],
                data["parent_clause_widths"],
            )
        )
        print(f"ORDER_SIZE = {n}")
        print(f"  pre_unit_component_merges = {data['pre_unit_component_merges']}")
        print(f"  classification = {data['classification']}")
        print(f"  parent_clause_widths = {data['parent_clause_widths']}")
        print(
            "  resolution_antecedent_widths = "
            f"{data['resolution_antecedent_widths']}"
        )
        print(f"  pivot_variables = {data['pivot_variables']}")
        print(f"  records = {data['records']}")

    print("JANUS_GT_PRE_UNIT_PARENT_PROVENANCE = PASS")
    print(f"rows = {tuple(rows)}")
    print(f"aggregate_classification = {tuple(sorted(aggregate.items()))}")
    print("claim_boundary = exact one-generation provenance; inherited witnesses still require recursive tracing")


if __name__ == "__main__":
    self_test()
