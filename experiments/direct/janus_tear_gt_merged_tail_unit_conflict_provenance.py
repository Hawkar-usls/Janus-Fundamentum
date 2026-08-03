#!/usr/bin/env python3
"""Trace exact post-unit conflict provenance of fresh merged-tail births.

Every fresh local non-tail bridge occurrence with a non-singleton oriented tail
is born in a state that terminates by post-local unit contradiction before any
child call.  This checker does not assume that the offending resolvent caused
the contradiction.  It reconstructs the complete acyclic unit-reason DAG from
the saturated CNF and classifies each of the 18 occurrences as:

- DIRECT_CONFLICT_SOURCE: the event resolvent is a source of a final opposing
  unit;
- ANCESTOR_CONFLICT_SOURCE: the event resolvent occurs earlier in the backward
  unit-reason closure;
- COLOCATED_NONCAUSAL: the state is contradictory but this event resolvent is
  absent from every reconstructed reason closure.

Terminal labels are recorded but not trusted.  Contradiction is certified from
the final post-unit event itself: either simultaneous opposite units or a unit
assignment producing the empty clause.

All candidate source clauses are retained, so causal membership is existential
and does not depend on an arbitrary chosen reason.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_component_merge_sources import source_clauses
from janus_tear_gt_component_tree_clause_audit import execution_context
from janus_tear_gt_local_resolution_bad_bridge_birth_v2 import audit as raw_audit

Clause = tuple[int, ...]


def assignment_literal(variable: int, value: bool) -> int:
    return int(variable) if value else -int(variable)


def semantic_conflict_kind(events) -> str:
    assert events
    last = events[-1]
    if last["kind"] == "opposite_units":
        units = tuple(int(value) for value in last["units"])
        unit_set = set(units)
        assert any(-literal in unit_set for literal in unit_set)
        return "OPPOSITE_UNITS"
    assert last["kind"] == "unit"
    assert last.get("after") is None
    return "EMPTY_ON_UNIT_ASSIGNMENT"


def build_reason_certificate(base_cnf, events):
    """Replay unit events and return all-source backward conflict closure."""

    assignments: dict[int, bool] = {}
    assignment_event: dict[int, int] = {}
    event_sources: dict[int, tuple[Clause, ...]] = {}
    event_prior_assignments: dict[int, dict[int, bool]] = {}
    conflict_root_events: set[int] = set()
    conflict_root_sources: set[Clause] = set()
    conflict_kind = None

    for event_index, event in enumerate(events):
        if event["kind"] == "opposite_units":
            conflict_kind = "OPPOSITE_UNITS"
            prior = dict(assignments)
            units = tuple(int(value) for value in event["units"])
            unit_set = set(units)
            assert any(-literal in unit_set for literal in unit_set)
            for literal in units:
                candidates = source_clauses(tuple(base_cnf), prior, literal)
                assert candidates, (
                    "opposite_units",
                    event_index,
                    literal,
                    prior,
                )
                conflict_root_sources.update(candidates)
            assert event_index == len(events) - 1
            break

        assert event["kind"] == "unit"
        literal = int(event["literal"])
        variable = abs(literal)
        value = literal > 0
        prior = dict(assignments)
        candidates = source_clauses(tuple(base_cnf), prior, literal)
        assert candidates, (event_index, literal, prior)

        event_sources[event_index] = candidates
        event_prior_assignments[event_index] = prior

        if event.get("after") is None:
            conflict_kind = "EMPTY_ON_UNIT_ASSIGNMENT"
            conflict_root_events.add(event_index)
            opposite_candidates = source_clauses(tuple(base_cnf), prior, -literal)
            assert opposite_candidates, (event_index, literal, prior)
            conflict_root_sources.update(candidates)
            conflict_root_sources.update(opposite_candidates)
            assert event_index == len(events) - 1
            break

        assignments[variable] = value
        assignment_event[variable] = event_index

    assert conflict_kind is not None
    assert conflict_kind == semantic_conflict_kind(events)

    closure_sources: set[Clause] = set(conflict_root_sources)
    closure_events: set[int] = set(conflict_root_events)
    agenda_events = list(conflict_root_events)

    def enqueue_dependencies(clause: Clause, prior: dict[int, bool]) -> None:
        for literal in clause:
            variable = abs(literal)
            if variable not in prior:
                continue
            value = prior[variable]
            true_literal = assignment_literal(variable, value)
            assert literal != true_literal, (clause, prior, literal)
            dependency_event = assignment_event.get(variable)
            if dependency_event is not None and dependency_event not in closure_events:
                closure_events.add(dependency_event)
                agenda_events.append(dependency_event)

    final_assignments = dict(assignments)
    for clause in tuple(conflict_root_sources):
        enqueue_dependencies(clause, final_assignments)

    while agenda_events:
        event_index = agenda_events.pop()
        prior = event_prior_assignments[event_index]
        for clause in event_sources[event_index]:
            closure_sources.add(clause)
            enqueue_dependencies(clause, prior)

    return {
        "conflict_kind": conflict_kind,
        "conflict_root_sources": tuple(sorted(conflict_root_sources, key=repr)),
        "closure_sources": tuple(sorted(closure_sources, key=repr)),
        "closure_events": tuple(sorted(closure_events)),
        "unit_event_count": len(event_sources),
        "closure_event_count": len(closure_events),
        "closure_source_count": len(closure_sources),
    }


def audit(n: int):
    context = execution_context(n)
    policy = context["policy"]
    raw = raw_audit(n)

    counts: Counter[str] = Counter()
    terminal_labels: Counter[str] = Counter()
    conflict_kinds: Counter[str] = Counter()
    unique_state_ids: set[int] = set()
    unique_origin_events: set[tuple[int, int]] = set()
    closure_source_counts: Counter[int] = Counter()
    closure_event_counts: Counter[int] = Counter()
    event_clause_multiplicity: Counter[int] = Counter()
    records = []

    certificate_cache = {}

    for example in raw["fresh_examples"]:
        tail_size, _ = tuple(example["endpoint_shape"])
        if int(tail_size) <= 1:
            continue

        counts["fresh_merged_tail_occurrences"] += 1
        state_id = int(example["state_id"])
        event_index = int(example["event_index"])
        event_clause = tuple(example["resolvent"])
        unique_state_ids.add(state_id)
        unique_origin_events.add((state_id, event_index))

        state = policy.states[state_id]
        terminal = str(state["terminal"])
        terminal_labels[terminal] += 1
        assert not state.get("children")
        post_events = tuple(state.get("post_units", []))
        semantic_kind = semantic_conflict_kind(post_events)

        if state_id not in certificate_cache:
            certificate_cache[state_id] = build_reason_certificate(
                tuple(state["resolution_output"]),
                post_events,
            )
        certificate = certificate_cache[state_id]
        assert certificate["conflict_kind"] == semantic_kind
        conflict_kinds[str(certificate["conflict_kind"])] += 1
        closure_source_counts[int(certificate["closure_source_count"])] += 1
        closure_event_counts[int(certificate["closure_event_count"])] += 1

        root_sources = set(certificate["conflict_root_sources"])
        closure_sources = set(certificate["closure_sources"])
        occurrences_in_output = sum(
            1 for clause in state["resolution_output"] if tuple(clause) == event_clause
        )
        event_clause_multiplicity[occurrences_in_output] += 1
        assert occurrences_in_output == 1

        if event_clause in root_sources:
            classification = "DIRECT_CONFLICT_SOURCE"
        elif event_clause in closure_sources:
            classification = "ANCESTOR_CONFLICT_SOURCE"
        else:
            classification = "COLOCATED_NONCAUSAL"
        counts[classification] += 1

        records.append({
            "n": n,
            "state_id": state_id,
            "call_id": int(example["call_id"]),
            "event_index": event_index,
            "pivot": int(example["pivot"]),
            "bad_literal": int(example["literal"]),
            "endpoint_shape": tuple(example["endpoint_shape"]),
            "event_clause": event_clause,
            "terminal_label": terminal,
            "classification": classification,
            "conflict_kind": certificate["conflict_kind"],
            "unit_event_count": certificate["unit_event_count"],
            "closure_event_count": certificate["closure_event_count"],
            "closure_source_count": certificate["closure_source_count"],
            "conflict_root_sources": certificate["conflict_root_sources"],
        })

    assert counts["fresh_merged_tail_occurrences"] == 18
    assert sum(
        counts[label]
        for label in (
            "DIRECT_CONFLICT_SOURCE",
            "ANCESTOR_CONFLICT_SOURCE",
            "COLOCATED_NONCAUSAL",
        )
    ) == 18

    return {
        "n": n,
        "counts": tuple(sorted(counts.items())),
        "terminal_labels": tuple(sorted(terminal_labels.items())),
        "conflict_kinds": tuple(sorted(conflict_kinds.items())),
        "unique_states": len(unique_state_ids),
        "unique_origin_events": len(unique_origin_events),
        "closure_source_counts": tuple(sorted(closure_source_counts.items())),
        "closure_event_counts": tuple(sorted(closure_event_counts.items())),
        "event_clause_multiplicity": tuple(sorted(event_clause_multiplicity.items())),
        "records": tuple(records),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_terminals: Counter[str] = Counter()
    aggregate_conflicts: Counter[str] = Counter()
    aggregate_closure_sources: Counter[int] = Counter()
    aggregate_closure_events: Counter[int] = Counter()
    aggregate_multiplicity: Counter[int] = Counter()
    rows = []

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_terminals.update(dict(data["terminal_labels"]))
        aggregate_conflicts.update(dict(data["conflict_kinds"]))
        aggregate_closure_sources.update(dict(data["closure_source_counts"]))
        aggregate_closure_events.update(dict(data["closure_event_counts"]))
        aggregate_multiplicity.update(dict(data["event_clause_multiplicity"]))
        rows.append({
            "n": n,
            "occurrences": dict(data["counts"]).get(
                "fresh_merged_tail_occurrences", 0
            ),
            "direct": dict(data["counts"]).get(
                "DIRECT_CONFLICT_SOURCE", 0
            ),
            "ancestor": dict(data["counts"]).get(
                "ANCESTOR_CONFLICT_SOURCE", 0
            ),
            "colocated": dict(data["counts"]).get(
                "COLOCATED_NONCAUSAL", 0
            ),
            "unique_states": data["unique_states"],
            "unique_origin_events": data["unique_origin_events"],
            "terminal_labels": dict(data["terminal_labels"]),
            "conflict_kinds": dict(data["conflict_kinds"]),
        })

    assert aggregate_counts["fresh_merged_tail_occurrences"] == 18
    print("JANUS_GT_MERGED_TAIL_UNIT_CONFLICT_PROVENANCE = PASS")
    for row in rows:
        print(f"ROW = {row}")
    print(f"COUNTS = {dict(aggregate_counts)}")
    print(f"TERMINAL_LABELS = {dict(aggregate_terminals)}")
    print(f"CONFLICT_KINDS = {dict(aggregate_conflicts)}")
    print(f"CLOSURE_SOURCE_COUNTS = {dict(sorted(aggregate_closure_sources.items()))}")
    print(f"CLOSURE_EVENT_COUNTS = {dict(sorted(aggregate_closure_events.items()))}")
    print(f"EVENT_CLAUSE_MULTIPLICITY = {dict(aggregate_multiplicity)}")
    print(
        "claim_boundary = exact finite all-source unit-reason provenance through GT_8; "
        "arbitrary-n merged-tail conflict theorem remains open"
    )


if __name__ == "__main__":
    self_test()
