#!/usr/bin/env python3
"""Audit the historical graph-tautology novel-branch measure on Policy-0A.

The Formula-Caching lower-bound proof calls a branch on x_{i,j} novel when i and
j lie in different connected components of the Hasse diagram of the partial
order fixed so far. Connectivity is the same in the Hasse diagram and the
undirected comparability graph of the transitive closure, so this audit computes
components from all recorded decision and unit comparison assignments.

For each actual call occurrence we record novelty level, early contradictions,
cache hits, and the distinct transitive-closure restrictions first reached at
level n-2. This is a finite diagnostic, not a reconstruction of the complete
historical induction under Policy-0A local Resolution.
"""

from __future__ import annotations

from collections import Counter, defaultdict

from janus_tear_gt_critical_order_damage import pair_variables
from janus_tear_policy0a_fc_trace import FCTracePolicy, verify_fc_trace
from janus_tear_policy0a_graph_tautology_probe import graph_tautology_cnf


def add_units(assignment: dict[int, bool], events) -> dict[int, bool]:
    result = dict(assignment)
    for event in events:
        if event["kind"] != "unit":
            continue
        literal = int(event["literal"])
        variable = abs(literal)
        value = literal > 0
        assert variable not in result or result[variable] == value
        result[variable] = value
    return result


def directed_relations(
    n: int,
    assignment: dict[int, bool],
    pairs: dict[int, tuple[int, int]],
) -> list[list[bool]]:
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

    for left in range(n):
        for right in range(n):
            if left != right:
                assert not (relation[left][right] and relation[right][left])
    return relation


def components(relation: list[list[bool]]) -> tuple[tuple[int, ...], ...]:
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


def closure_signature(relation: list[list[bool]]) -> tuple[tuple[int, int], ...]:
    return tuple(
        (left, right)
        for left in range(len(relation))
        for right in range(len(relation))
        if left != right and relation[left][right]
    )


def component_index(parts: tuple[tuple[int, ...], ...]) -> dict[int, int]:
    return {
        vertex: index
        for index, component in enumerate(parts)
        for vertex in component
    }


def possible_tops(
    component: tuple[int, ...], relation: list[list[bool]]
) -> tuple[int, ...]:
    # A top/maximal element has no known greater element inside its component.
    return tuple(
        vertex
        for vertex in component
        if not any(
            relation[vertex][other]
            for other in component
            if other != vertex
        )
    )


def audit(n: int):
    cnf, variable_count = graph_tautology_cnf(n)
    pairs = pair_variables(n)
    assert len(pairs) == variable_count

    policy = FCTracePolicy()
    result, root_call = policy.solve(cnf, variable_count)
    assert result.answer is False
    assert root_call is not None
    assert verify_fc_trace(cnf, variable_count, policy, root_call) is False

    seen_calls: set[int] = set()
    novelty_histogram: Counter[int] = Counter()
    branch_novelty_histogram: Counter[bool] = Counter()
    terminal_by_novelty: Counter[tuple[str, int]] = Counter()
    cache_hits_by_novelty: Counter[int] = Counter()
    level_signatures: dict[int, set[tuple[tuple[int, int], ...]]] = defaultdict(set)
    first_target_signatures: set[tuple[tuple[int, int], ...]] = set()
    first_target_calls = 0
    early_cache_hits = 0
    early_contradictions = 0
    maximum_novelty = 0
    minimum_component_count = n
    maximum_prune = 0
    novel_branch_records = []

    target_level = n - 2

    def walk(
        call_id: int,
        incoming: dict[int, bool],
        novelty: int,
        already_reached_target: bool,
    ) -> None:
        nonlocal first_target_calls, early_cache_hits, early_contradictions
        nonlocal maximum_novelty, minimum_component_count, maximum_prune

        assert call_id not in seen_calls
        seen_calls.add(call_id)
        call = policy.calls[call_id]
        after_pre = add_units(incoming, call.get("pre_units", []))
        relation = directed_relations(n, after_pre, pairs)
        parts = components(relation)
        minimum_component_count = min(minimum_component_count, len(parts))
        maximum_novelty = max(maximum_novelty, novelty)
        novelty_histogram[novelty] += 1
        level_signatures[novelty].add(closure_signature(relation))

        terminal = str(call["terminal"])
        if terminal == "CACHE_HIT":
            cache_hits_by_novelty[novelty] += 1
            terminal_by_novelty[(terminal, novelty)] += 1
            if novelty < target_level:
                early_cache_hits += 1
            return
        if terminal != "STATE":
            terminal_by_novelty[(terminal, novelty)] += 1
            if terminal in ("PRE_UNIT_CONTRADICTION",) and novelty < target_level:
                early_contradictions += 1
            return

        state = policy.states[int(call["state"])]
        after_post = add_units(after_pre, state.get("post_units", []))
        relation = directed_relations(n, after_post, pairs)
        parts = components(relation)
        indices = component_index(parts)
        minimum_component_count = min(minimum_component_count, len(parts))
        for component in parts:
            maximum_prune = max(
                maximum_prune,
                max(0, len(possible_tops(component, relation)) - 1),
            )

        state_terminal = str(state["terminal"])
        if state_terminal not in ("BRANCH_UNSAT", "BRANCH_SAT"):
            terminal_by_novelty[(state_terminal, novelty)] += 1
            if state_terminal in (
                "RESOLUTION_CONTRADICTION",
                "POST_UNIT_CONTRADICTION",
            ) and novelty < target_level:
                early_contradictions += 1
            return

        variable = int(state["branch_var"])
        left, right = pairs[variable]
        is_novel = indices[left] != indices[right]
        branch_novelty_histogram[is_novel] += 1
        novel_branch_records.append(
            (
                novelty,
                is_novel,
                len(parts),
                left,
                right,
                tuple(len(possible_tops(component, relation)) for component in parts),
            )
        )

        children = state["children"]
        assert isinstance(children, list)
        for child in children:
            if child["call"] is None:
                if novelty < target_level:
                    early_contradictions += 1
                continue
            value = bool(child["value"])
            child_assignment = dict(after_post)
            assert variable not in child_assignment
            child_assignment[variable] = value
            child_novelty = novelty + int(is_novel)
            reached_now = not already_reached_target and child_novelty >= target_level
            if reached_now:
                child_relation = directed_relations(n, child_assignment, pairs)
                first_target_signatures.add(closure_signature(child_relation))
                first_target_calls += 1
            walk(
                int(child["call"]),
                child_assignment,
                child_novelty,
                already_reached_target or reached_now,
            )
            if child["result"]:
                break

    walk(root_call, {}, 0, False)
    assert len(seen_calls) == len(policy.calls)

    return {
        "result": result,
        "calls": len(policy.calls),
        "states": len(policy.states),
        "target_level": target_level,
        "historical_target": 2 ** target_level,
        "first_target_calls": first_target_calls,
        "first_target_distinct_restrictions": len(first_target_signatures),
        "maximum_novelty": maximum_novelty,
        "minimum_component_count": minimum_component_count,
        "maximum_prune": maximum_prune,
        "novel_branches": branch_novelty_histogram[True],
        "non_novel_branches": branch_novelty_histogram[False],
        "early_cache_hits": early_cache_hits,
        "early_contradictions": early_contradictions,
        "novelty_histogram": tuple(sorted(novelty_histogram.items())),
        "cache_hits_by_novelty": tuple(sorted(cache_hits_by_novelty.items())),
        "terminal_by_novelty": tuple(sorted(terminal_by_novelty.items())),
        "level_distinct_restrictions": tuple(
            (level, len(signatures))
            for level, signatures in sorted(level_signatures.items())
        ),
        "branch_records": tuple(novel_branch_records),
    }


def self_test() -> None:
    rows = []
    for n in range(4, 9):
        data = audit(n)
        result = data["result"]
        rows.append(
            (
                n,
                data["calls"],
                data["states"],
                result.cache_hits,
                data["target_level"],
                data["historical_target"],
                data["first_target_calls"],
                data["first_target_distinct_restrictions"],
                data["maximum_novelty"],
                data["early_cache_hits"],
                data["early_contradictions"],
            )
        )

        print(f"ORDER_SIZE = {n}")
        print(f"  calls = {data['calls']}")
        print(f"  unique_states = {data['states']}")
        print(f"  cache_hits = {result.cache_hits}")
        print(f"  target_novelty_level = {data['target_level']}")
        print(f"  historical_distinct_restriction_target = {data['historical_target']}")
        print(f"  first_target_calls = {data['first_target_calls']}")
        print(
            "  first_target_distinct_restrictions = "
            f"{data['first_target_distinct_restrictions']}"
        )
        print(f"  maximum_novelty_reached = {data['maximum_novelty']}")
        print(f"  novel_branches = {data['novel_branches']}")
        print(f"  non_novel_branches = {data['non_novel_branches']}")
        print(f"  early_cache_hits = {data['early_cache_hits']}")
        print(f"  early_contradictions = {data['early_contradictions']}")
        print(f"  minimum_component_count = {data['minimum_component_count']}")
        print(f"  maximum_prune = {data['maximum_prune']}")
        print(f"  novelty_histogram = {data['novelty_histogram']}")
        print(f"  cache_hits_by_novelty = {data['cache_hits_by_novelty']}")
        print(
            "  level_distinct_restrictions = "
            f"{data['level_distinct_restrictions']}"
        )

    print("JANUS_GT_NOVEL_BRANCH_AUDIT = PASS")
    print(f"rows = {tuple(rows)}")
    print("historical_measure = novel branches connecting Hasse components")
    print("claim_boundary = finite execution overlay; full historical lower-bound induction under local Resolution remains unproved")


if __name__ == "__main__":
    self_test()
