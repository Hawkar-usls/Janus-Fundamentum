#!/usr/bin/env python3
"""Failure-tolerant overlay of the historical GT novel-branch measure.

Unlike the first audit, this version does not assume that every intermediate
comparison assignment is already a consistent partial order.  It records cycles,
branches on assigned variables, cache hits and contradictions as explicit events.

A branch has a historical novelty label only when the current comparison closure
is acyclic.  It is novel when the compared vertices lie in distinct connected
components of the undirected comparability graph (equivalently, of the Hasse
diagram for a partial order).

This finite overlay identifies where the historical Formula-Caching induction
needs an additional robustness lemma for Policy-0A local Resolution.  It is not
itself a lower bound.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass

from janus_tear_gt_critical_order_damage import pair_variables
from janus_tear_policy0a_fc_trace import FCTracePolicy, verify_fc_trace
from janus_tear_policy0a_graph_tautology_probe import graph_tautology_cnf


@dataclass(frozen=True)
class Closure:
    relation: tuple[tuple[bool, ...], ...]
    cycle_vertices: tuple[int, ...]

    @property
    def acyclic(self) -> bool:
        return not self.cycle_vertices


def add_units(assignment: dict[int, bool], events):
    result = dict(assignment)
    conflicts = 0
    repeated = 0
    for event in events:
        if event["kind"] != "unit":
            continue
        literal = int(event["literal"])
        variable = abs(literal)
        value = literal > 0
        if variable in result:
            repeated += 1
            if result[variable] != value:
                conflicts += 1
        else:
            result[variable] = value
    return result, repeated, conflicts


def comparison_closure(
    n: int,
    assignment: dict[int, bool],
    pairs: dict[int, tuple[int, int]],
) -> Closure:
    relation = [[False] * n for _ in range(n)]
    for vertex in range(n):
        relation[vertex][vertex] = True
    for variable, value in assignment.items():
        left, right = pairs[variable]
        lower, upper = (left, right) if value else (right, left)
        relation[lower][upper] = True

    for middle in range(n):
        for left in range(n):
            if not relation[left][middle]:
                continue
            for right in range(n):
                if relation[middle][right]:
                    relation[left][right] = True

    cycle_vertices = tuple(
        vertex
        for vertex in range(n)
        if any(
            other != vertex
            and relation[vertex][other]
            and relation[other][vertex]
            for other in range(n)
        )
    )
    return Closure(
        tuple(tuple(row) for row in relation),
        cycle_vertices,
    )


def components(closure: Closure) -> tuple[tuple[int, ...], ...]:
    relation = closure.relation
    n = len(relation)
    unseen = set(range(n))
    result = []
    while unseen:
        seed = min(unseen)
        stack = [seed]
        component = set()
        while stack:
            vertex = stack.pop()
            if vertex in component:
                continue
            component.add(vertex)
            unseen.discard(vertex)
            for other in range(n):
                if other not in component and (
                    relation[vertex][other] or relation[other][vertex]
                ):
                    stack.append(other)
        result.append(tuple(sorted(component)))
    return tuple(sorted(result))


def signature(closure: Closure) -> tuple[tuple[int, int], ...]:
    relation = closure.relation
    return tuple(
        (left, right)
        for left in range(len(relation))
        for right in range(len(relation))
        if left != right and relation[left][right]
    )


def audit(n: int):
    cnf, variable_count = graph_tautology_cnf(n)
    pairs = pair_variables(n)
    policy = FCTracePolicy()
    result, root_call = policy.solve(cnf, variable_count)
    assert result.answer is False
    assert root_call is not None
    assert verify_fc_trace(cnf, variable_count, policy, root_call) is False

    target = n - 2
    seen_calls: set[int] = set()
    novelty_histogram: Counter[int] = Counter()
    branch_kind: Counter[str] = Counter()
    terminal_by_level: Counter[tuple[str, int]] = Counter()
    cache_by_level: Counter[int] = Counter()
    cyclic_by_level: Counter[int] = Counter()
    restrictions_by_level: dict[int, set[tuple[tuple[int, int], ...]]] = defaultdict(set)
    target_restrictions: set[tuple[tuple[int, int], ...]] = set()
    target_entries = 0
    repeated_unit_assignments = 0
    conflicting_unit_assignments = 0
    rebranches_on_assigned_variables = 0
    early_cyclic_calls = 0
    early_conflicts = 0
    maximum_novelty = 0
    minimum_components = n

    def walk(
        call_id: int,
        incoming: dict[int, bool],
        novelty: int,
        target_seen: bool,
    ) -> None:
        nonlocal target_entries, repeated_unit_assignments
        nonlocal conflicting_unit_assignments, rebranches_on_assigned_variables
        nonlocal early_cyclic_calls, early_conflicts
        nonlocal maximum_novelty, minimum_components

        if call_id in seen_calls:
            branch_kind["REPEATED_CALL_ID"] += 1
            return
        seen_calls.add(call_id)
        call = policy.calls[call_id]
        after_pre, repeated, conflicts = add_units(
            incoming, call.get("pre_units", [])
        )
        repeated_unit_assignments += repeated
        conflicting_unit_assignments += conflicts

        closure = comparison_closure(n, after_pre, pairs)
        parts = components(closure)
        minimum_components = min(minimum_components, len(parts))
        maximum_novelty = max(maximum_novelty, novelty)
        novelty_histogram[novelty] += 1
        restrictions_by_level[novelty].add(signature(closure))
        if not closure.acyclic:
            cyclic_by_level[novelty] += 1
            if novelty < target:
                early_cyclic_calls += 1

        terminal = str(call["terminal"])
        if terminal == "CACHE_HIT":
            cache_by_level[novelty] += 1
            terminal_by_level[(terminal, novelty)] += 1
            return
        if terminal != "STATE":
            terminal_by_level[(terminal, novelty)] += 1
            if novelty < target:
                early_conflicts += int("CONTRADICTION" in terminal)
            return

        state = policy.states[int(call["state"])]
        after_post, repeated, conflicts = add_units(
            after_pre, state.get("post_units", [])
        )
        repeated_unit_assignments += repeated
        conflicting_unit_assignments += conflicts
        post_closure = comparison_closure(n, after_post, pairs)
        post_parts = components(post_closure)
        minimum_components = min(minimum_components, len(post_parts))

        state_terminal = str(state["terminal"])
        if state_terminal not in ("BRANCH_UNSAT", "BRANCH_SAT"):
            terminal_by_level[(state_terminal, novelty)] += 1
            if novelty < target:
                early_conflicts += int("CONTRADICTION" in state_terminal)
            return

        variable = int(state["branch_var"])
        left, right = pairs[variable]
        if variable in after_post:
            rebranches_on_assigned_variables += 1
            branch_kind["ASSIGNED_VARIABLE"] += 1
            novelty_increment = 0
        elif not post_closure.acyclic:
            branch_kind["CYCLIC_UNDEFINED"] += 1
            novelty_increment = 0
        else:
            index = {
                vertex: component_index
                for component_index, component in enumerate(post_parts)
                for vertex in component
            }
            is_novel = index[left] != index[right]
            novelty_increment = int(is_novel)
            branch_kind["NOVEL" if is_novel else "NON_NOVEL"] += 1

        for child in state["children"]:
            if child["call"] is None:
                if novelty < target:
                    early_conflicts += 1
                continue
            value = bool(child["value"])
            child_assignment = dict(after_post)
            if variable in child_assignment and child_assignment[variable] != value:
                branch_kind["INCONSISTENT_CHILD_VALUE"] += 1
            child_assignment[variable] = value
            child_level = novelty + novelty_increment
            reached_now = not target_seen and child_level >= target
            if reached_now:
                target_entries += 1
                target_restrictions.add(
                    signature(comparison_closure(n, child_assignment, pairs))
                )
            walk(
                int(child["call"]),
                child_assignment,
                child_level,
                target_seen or reached_now,
            )
            if child["result"]:
                break

    walk(root_call, {}, 0, False)

    return {
        "n": n,
        "calls": len(policy.calls),
        "states": len(policy.states),
        "cache_hits": result.cache_hits,
        "target_level": target,
        "historical_target": 2 ** target,
        "target_entries": target_entries,
        "target_distinct_restrictions": len(target_restrictions),
        "maximum_novelty": maximum_novelty,
        "minimum_components": minimum_components,
        "seen_calls": len(seen_calls),
        "unseen_calls": len(policy.calls) - len(seen_calls),
        "early_cyclic_calls": early_cyclic_calls,
        "early_conflicts": early_conflicts,
        "repeated_unit_assignments": repeated_unit_assignments,
        "conflicting_unit_assignments": conflicting_unit_assignments,
        "rebranches_on_assigned_variables": rebranches_on_assigned_variables,
        "branch_kind": tuple(sorted(branch_kind.items())),
        "novelty_histogram": tuple(sorted(novelty_histogram.items())),
        "cache_by_level": tuple(sorted(cache_by_level.items())),
        "cyclic_by_level": tuple(sorted(cyclic_by_level.items())),
        "terminal_by_level": tuple(sorted(terminal_by_level.items())),
        "distinct_restrictions_by_level": tuple(
            (level, len(items))
            for level, items in sorted(restrictions_by_level.items())
        ),
    }


def self_test() -> None:
    rows = []
    for n in range(4, 9):
        data = audit(n)
        rows.append(data)
        print(f"ORDER_SIZE = {n}")
        for key, value in data.items():
            if key != "n":
                print(f"  {key} = {value}")

    print("JANUS_GT_NOVEL_BRANCH_AUDIT_V2 = PASS")
    print(f"rows = {tuple(rows)}")
    print("historical_measure = novel comparisons connecting partial-order components")
    print("claim_boundary = finite failure-tolerant overlay; no transferred Formula-Caching lower bound")


if __name__ == "__main__":
    self_test()
