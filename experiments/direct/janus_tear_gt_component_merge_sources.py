#!/usr/bin/env python3
"""Trace exact clause sources of unit-induced GT component merges.

C024 separates Hasse-component reductions caused by explicit novel branches from
reductions caused by pre-state and post-local-Resolution unit propagation.  This
audit refines the latter two categories to individual, independently replayed
unit events and identifies a concrete source clause for each event.

For a unit literal l in a propagation stage, a source clause is any clause in the
stage's base CNF that reduces exactly to (l,) under the earlier units of that
same stage.  Post-stage sources are classified as entry clauses or as explicit
resolvents emitted by Policy-0A's one-pass local Resolution trace.

Only acyclic-to-acyclic component reductions count as historical component
merges.  Units that close a directed cycle are recorded as terminal conflict
events, not as legitimate partial-order merges.
"""

from __future__ import annotations

from collections import Counter, defaultdict

from janus_tear_gt_critical_order_damage import pair_variables
from janus_tear_gt_novel_branch_audit_v2 import comparison_closure, components
from janus_tear_policy0a_fc_trace import FCTracePolicy, verify_fc_trace
from janus_tear_policy0a_graph_tautology_probe import graph_tautology_cnf

Clause = tuple[int, ...]
CNF = tuple[Clause, ...]


def literal_true(literal: int, value: bool) -> bool:
    return value if literal > 0 else not value


def reduce_clause(clause: Clause, assignments: dict[int, bool]) -> Clause | None:
    residual = []
    for literal in clause:
        variable = abs(literal)
        if variable not in assignments:
            residual.append(literal)
            continue
        if literal_true(literal, assignments[variable]):
            return None
    return tuple(residual)


def source_clauses(
    base_cnf: CNF,
    stage_assignments: dict[int, bool],
    literal: int,
) -> tuple[Clause, ...]:
    return tuple(
        clause
        for clause in base_cnf
        if reduce_clause(clause, stage_assignments) == (literal,)
    )


def relation_component_count(n: int, assignment, pairs) -> tuple[int, bool]:
    closure = comparison_closure(n, assignment, pairs)
    return len(components(closure)), closure.acyclic


def clause_vertices(clause: Clause, pairs: dict[int, tuple[int, int]]):
    vertices: set[int] = set()
    for literal in clause:
        vertices.update(pairs[abs(literal)])
    return tuple(sorted(vertices))


def audit(n: int):
    cnf, variable_count = graph_tautology_cnf(n)
    pairs = pair_variables(n)
    policy = FCTracePolicy()
    result, root_call = policy.solve(cnf, variable_count)
    assert result.answer is False
    assert root_call is not None
    assert verify_fc_trace(cnf, variable_count, policy, root_call) is False

    seen: set[int] = set()
    records: list[dict[str, object]] = []
    stage_counts: Counter[str] = Counter()
    source_kind_counts: Counter[str] = Counter()
    merge_vertices: Counter[int] = Counter()
    merge_variables: Counter[int] = Counter()
    cycle_units: Counter[str] = Counter()
    maximum_unit_merges_on_path = 0
    terminal_path_histogram: Counter[int] = Counter()

    def process_units(
        *,
        stage: str,
        call_id: int,
        state_id: int | None,
        depth: int,
        assignment: dict[int, bool],
        base_cnf: CNF,
        events,
        resolution_events=(),
        path_unit_merges: int,
    ) -> tuple[dict[int, bool], int]:
        nonlocal maximum_unit_merges_on_path

        current = dict(assignment)
        stage_assignments: dict[int, bool] = {}
        resolution_sources: dict[Clause, list[tuple[int, dict[str, object]]]] = defaultdict(list)
        for index, event in enumerate(resolution_events):
            resolution_sources[tuple(event["resolvent"])].append((index, event))

        for event_index, event in enumerate(events):
            if event["kind"] != "unit":
                continue
            literal = int(event["literal"])
            variable = abs(literal)
            value = literal > 0
            assert variable not in current or current[variable] == value

            candidates = source_clauses(base_cnf, stage_assignments, literal)
            assert candidates, (stage, call_id, state_id, event_index, literal)

            before_count, before_acyclic = relation_component_count(n, current, pairs)
            after = dict(current)
            after[variable] = value
            after_count, after_acyclic = relation_component_count(n, after, pairs)

            if before_acyclic and not after_acyclic:
                cycle_units[stage] += 1
            elif before_acyclic and after_acyclic and after_count < before_count:
                assert before_count - after_count == 1
                pair = pairs[variable]
                local_candidates = tuple(
                    clause for clause in candidates if clause in resolution_sources
                )
                source_kind = (
                    "LOCAL_RESOLVENT"
                    if stage == "post" and local_candidates
                    else "ENTRY_OR_RESIDUAL_CLAUSE"
                )
                chosen = local_candidates[0] if local_candidates else candidates[0]
                resolution_payload = None
                if chosen in resolution_sources:
                    resolution_index, resolution_event = resolution_sources[chosen][0]
                    resolution_payload = {
                        "event_index": resolution_index,
                        "left": tuple(resolution_event["left"]),
                        "right": tuple(resolution_event["right"]),
                        "pivot": int(resolution_event["pivot"]),
                        "resolvent": tuple(resolution_event["resolvent"]),
                        "attempt": int(resolution_event["attempt"]),
                    }

                record = {
                    "n": n,
                    "stage": stage,
                    "call_id": call_id,
                    "state_id": state_id,
                    "depth": depth,
                    "event_index": event_index,
                    "batch": int(event["batch"]),
                    "literal": literal,
                    "variable": variable,
                    "pair": pair,
                    "touches_vertex_zero": 0 in pair,
                    "before_components": before_count,
                    "after_components": after_count,
                    "source_kind": source_kind,
                    "source_clause": chosen,
                    "source_width": len(chosen),
                    "source_vertices": clause_vertices(chosen, pairs),
                    "candidate_source_count": len(candidates),
                    "resolution": resolution_payload,
                }
                records.append(record)
                stage_counts[stage] += 1
                source_kind_counts[source_kind] += 1
                merge_variables[variable] += 1
                merge_vertices.update(pair)
                path_unit_merges += 1
                maximum_unit_merges_on_path = max(
                    maximum_unit_merges_on_path, path_unit_merges
                )

            current = after
            stage_assignments[variable] = value

        return current, path_unit_merges

    def walk(
        call_id: int,
        incoming: dict[int, bool],
        depth: int,
        path_unit_merges: int,
    ) -> None:
        nonlocal maximum_unit_merges_on_path
        assert call_id not in seen
        seen.add(call_id)
        call = policy.calls[call_id]

        after_pre, path_after_pre = process_units(
            stage="pre",
            call_id=call_id,
            state_id=None,
            depth=depth,
            assignment=incoming,
            base_cnf=tuple(call["input"]),
            events=call.get("pre_units", []),
            path_unit_merges=path_unit_merges,
        )

        if call["terminal"] != "STATE":
            terminal_path_histogram[path_after_pre] += 1
            maximum_unit_merges_on_path = max(
                maximum_unit_merges_on_path, path_after_pre
            )
            return

        state_id = int(call["state"])
        state = policy.states[state_id]
        after_post, path_after_post = process_units(
            stage="post",
            call_id=call_id,
            state_id=state_id,
            depth=depth,
            assignment=after_pre,
            base_cnf=tuple(state["resolution_output"]),
            events=state.get("post_units", []),
            resolution_events=state.get("resolution_events", []),
            path_unit_merges=path_after_pre,
        )

        if state["terminal"] not in ("BRANCH_UNSAT", "BRANCH_SAT"):
            terminal_path_histogram[path_after_post] += 1
            maximum_unit_merges_on_path = max(
                maximum_unit_merges_on_path, path_after_post
            )
            return

        variable = int(state["branch_var"])
        for child in state["children"]:
            if child["call"] is None:
                terminal_path_histogram[path_after_post] += 1
                continue
            value = bool(child["value"])
            child_assignment = dict(after_post)
            child_assignment[variable] = value
            walk(
                int(child["call"]),
                child_assignment,
                depth + 1,
                path_after_post,
            )
            if child["result"]:
                break

    walk(root_call, {}, 0, 0)
    assert len(seen) == len(policy.calls)

    return {
        "n": n,
        "calls": len(policy.calls),
        "states": len(policy.states),
        "cache_hits": result.cache_hits,
        "unit_component_merges": len(records),
        "stage_counts": tuple(sorted(stage_counts.items())),
        "source_kind_counts": tuple(sorted(source_kind_counts.items())),
        "cycle_units": tuple(sorted(cycle_units.items())),
        "maximum_unit_merges_on_path": maximum_unit_merges_on_path,
        "terminal_path_histogram": tuple(sorted(terminal_path_histogram.items())),
        "merge_variables": tuple(sorted(merge_variables.items())),
        "merge_vertices": tuple(sorted(merge_vertices.items())),
        "records": tuple(records),
    }


def self_test() -> None:
    rows = []
    for n in range(4, 9):
        data = audit(n)
        rows.append(
            (
                n,
                data["calls"],
                data["states"],
                data["unit_component_merges"],
                data["stage_counts"],
                data["source_kind_counts"],
                data["maximum_unit_merges_on_path"],
            )
        )
        print(f"ORDER_SIZE = {n}")
        print(f"  calls = {data['calls']}")
        print(f"  states = {data['states']}")
        print(f"  cache_hits = {data['cache_hits']}")
        print(f"  unit_component_merges = {data['unit_component_merges']}")
        print(f"  stage_counts = {data['stage_counts']}")
        print(f"  source_kind_counts = {data['source_kind_counts']}")
        print(f"  cycle_units = {data['cycle_units']}")
        print(
            "  maximum_unit_merges_on_path = "
            f"{data['maximum_unit_merges_on_path']}"
        )
        print(f"  terminal_path_histogram = {data['terminal_path_histogram']}")
        print(f"  merge_variables = {data['merge_variables']}")
        print(f"  merge_vertices = {data['merge_vertices']}")
        print(f"  records = {data['records']}")

    print("JANUS_GT_COMPONENT_MERGE_SOURCES = PASS")
    print(f"rows = {tuple(rows)}")
    print("charge = every acyclic unit merge has a replayed source clause")
    print("claim_boundary = finite event provenance; no asymptotic bound on unit merges")


if __name__ == "__main__":
    self_test()
