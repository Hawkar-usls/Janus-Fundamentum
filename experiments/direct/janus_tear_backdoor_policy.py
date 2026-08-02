#!/usr/bin/env python3
"""JANUS Tear strong-backdoor policy audit.

A strong 2-SAT backdoor is a variable set B such that every assignment to B
reduces the remaining CNF to 2-CNF (or immediate contradiction). Enumerating B
and solving every residual by implication-graph SCC gives an exact SAT solver
with work O(2^|B| poly(L)).

This audit treats each contradictory residual's SCC path pair as one Tear.
It demonstrates:

- a genuinely 3-CNF, non-XOR guarded family with a one-variable backdoor and
  constant branch count;
- a disjoint positive 3-clause family whose minimum strong 2-SAT backdoor is
  linear even though the formula is trivially satisfiable;
- exact agreement with brute force on deterministic random small CNFs.

The result gives a parameterized route, not a P=NP proof.
"""

from __future__ import annotations

import argparse
import json
import random
from collections import deque
from itertools import combinations, product
from typing import Sequence


Clause = tuple[int, ...]
Formula = tuple[Clause, ...]


def variables(formula: Formula) -> tuple[int, ...]:
    return tuple(sorted({abs(literal) for clause in formula for literal in clause}))


def simplify(formula: Formula, assignment: dict[int, bool]) -> Formula | None:
    residual: list[Clause] = []
    for clause in formula:
        kept: list[int] = []
        satisfied = False
        for literal in clause:
            value = assignment.get(abs(literal))
            if value is None:
                kept.append(literal)
                continue
            literal_value = value if literal > 0 else not value
            if literal_value:
                satisfied = True
                break
        if satisfied:
            continue
        if not kept:
            return None
        residual.append(tuple(kept))
    return tuple(residual)


def is_2cnf(formula: Formula | None) -> bool:
    return formula is None or all(len(clause) <= 2 for clause in formula)


def literal_index(literal: int, variable_count: int) -> int:
    variable = abs(literal) - 1
    return 2 * variable + int(literal < 0)


def index_literal(index: int) -> int:
    variable = index // 2 + 1
    return -variable if index % 2 else variable


def implication_graph(
    formula: Formula,
    variable_count: int,
) -> tuple[list[list[int]], list[list[int]]]:
    graph = [[] for _ in range(2 * variable_count)]
    reverse = [[] for _ in range(2 * variable_count)]

    def add_edge(left: int, right: int) -> None:
        graph[left].append(right)
        reverse[right].append(left)

    for clause in formula:
        if len(clause) == 1:
            literal = clause[0]
            left = literal_index(-literal, variable_count)
            right = literal_index(literal, variable_count)
            add_edge(left, right)
        elif len(clause) == 2:
            left_literal, right_literal = clause
            add_edge(
                literal_index(-left_literal, variable_count),
                literal_index(right_literal, variable_count),
            )
            add_edge(
                literal_index(-right_literal, variable_count),
                literal_index(left_literal, variable_count),
            )
        else:
            raise ValueError("formula is not 2-CNF")
    return graph, reverse


def finish_order(graph: Sequence[Sequence[int]]) -> list[int]:
    visited = [False] * len(graph)
    order: list[int] = []
    for start in range(len(graph)):
        if visited[start]:
            continue
        stack: list[tuple[int, int]] = [(start, 0)]
        visited[start] = True
        while stack:
            node, next_index = stack[-1]
            if next_index < len(graph[node]):
                neighbor = graph[node][next_index]
                stack[-1] = (node, next_index + 1)
                if not visited[neighbor]:
                    visited[neighbor] = True
                    stack.append((neighbor, 0))
            else:
                stack.pop()
                order.append(node)
    return order


def strongly_connected_components(
    graph: Sequence[Sequence[int]],
    reverse: Sequence[Sequence[int]],
) -> list[int]:
    order = finish_order(graph)
    component = [-1] * len(graph)
    component_count = 0
    for start in reversed(order):
        if component[start] != -1:
            continue
        stack = [start]
        component[start] = component_count
        while stack:
            node = stack.pop()
            for neighbor in reverse[node]:
                if component[neighbor] == -1:
                    component[neighbor] = component_count
                    stack.append(neighbor)
        component_count += 1
    return component


def implication_path(
    graph: Sequence[Sequence[int]],
    start: int,
    target: int,
    allowed_component: int,
    component: Sequence[int],
) -> list[int]:
    parent: dict[int, int | None] = {start: None}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        if node == target:
            break
        for neighbor in graph[node]:
            if component[neighbor] != allowed_component or neighbor in parent:
                continue
            parent[neighbor] = node
            queue.append(neighbor)
    if target not in parent:
        raise AssertionError("SCC path missing")
    result: list[int] = []
    cursor: int | None = target
    while cursor is not None:
        result.append(index_literal(cursor))
        cursor = parent[cursor]
    result.reverse()
    return result


def satisfies(formula: Formula, assignment: dict[int, bool]) -> bool:
    return all(
        any(
            assignment.get(abs(literal), False)
            if literal > 0
            else not assignment.get(abs(literal), False)
            for literal in clause
        )
        for clause in formula
    )


def solve_2sat(
    formula: Formula | None,
    variable_count: int,
) -> dict[str, object]:
    if formula is None:
        return {
            "status": "UNSAT",
            "certificate": {"kind": "empty_clause"},
        }
    if not is_2cnf(formula):
        raise ValueError("formula is not 2-CNF")

    graph, reverse = implication_graph(formula, variable_count)
    component = strongly_connected_components(graph, reverse)

    for variable in range(1, variable_count + 1):
        positive = literal_index(variable, variable_count)
        negative = literal_index(-variable, variable_count)
        if component[positive] == component[negative]:
            identifier = component[positive]
            return {
                "status": "UNSAT",
                "certificate": {
                    "kind": "scc_cycle_tear",
                    "variable": variable,
                    "positive_to_negative": implication_path(
                        graph,
                        positive,
                        negative,
                        identifier,
                        component,
                    ),
                    "negative_to_positive": implication_path(
                        graph,
                        negative,
                        positive,
                        identifier,
                        component,
                    ),
                },
            }

    assignment = {
        variable: (
            component[literal_index(variable, variable_count)]
            > component[literal_index(-variable, variable_count)]
        )
        for variable in range(1, variable_count + 1)
    }
    if not satisfies(formula, assignment):
        assignment = {
            variable: (
                component[literal_index(variable, variable_count)]
                < component[literal_index(-variable, variable_count)]
            )
            for variable in range(1, variable_count + 1)
        }
    if not satisfies(formula, assignment):
        raise AssertionError("2-SAT witness recovery failed")
    return {"status": "SAT", "assignment": assignment}


def strong_2sat_backdoor(formula: Formula, backdoor: Sequence[int]) -> bool:
    chosen = tuple(backdoor)
    for bits in product((False, True), repeat=len(chosen)):
        assignment = dict(zip(chosen, bits))
        if not is_2cnf(simplify(formula, assignment)):
            return False
    return True


def minimum_strong_2sat_backdoor(formula: Formula) -> tuple[int, ...]:
    candidates = variables(formula)
    for size in range(len(candidates) + 1):
        for subset in combinations(candidates, size):
            if strong_2sat_backdoor(formula, subset):
                return subset
    raise AssertionError("all variables must form a backdoor")


def solve_via_backdoor(
    formula: Formula,
    backdoor: Sequence[int],
) -> dict[str, object]:
    if not strong_2sat_backdoor(formula, backdoor):
        raise ValueError("supplied set is not a strong 2-SAT backdoor")
    variable_count = max(variables(formula), default=0)
    branch_tears: list[dict[str, object]] = []
    explored = 0

    for bits in product((False, True), repeat=len(backdoor)):
        prefix = dict(zip(backdoor, bits))
        residual = simplify(formula, prefix)
        explored += 1
        result = solve_2sat(residual, variable_count)
        if result["status"] == "SAT":
            witness = dict(result["assignment"])
            witness.update(prefix)
            if not satisfies(formula, witness):
                raise AssertionError("backdoor witness does not satisfy original CNF")
            return {
                "status": "SAT",
                "backdoor": tuple(backdoor),
                "explored_branches": explored,
                "maximum_branches": 2 ** len(backdoor),
                "witness": witness,
                "rejected_branch_tears": branch_tears,
            }
        branch_tears.append(
            {
                "prefix": prefix,
                "residual_certificate": result["certificate"],
            }
        )

    return {
        "status": "UNSAT",
        "backdoor": tuple(backdoor),
        "explored_branches": explored,
        "maximum_branches": 2 ** len(backdoor),
        "branch_tears": branch_tears,
    }


def guarded_3cnf_family(blocks: int) -> tuple[Formula, int]:
    """A non-XOR 3-CNF family with one selector backdoor z=1."""
    if blocks < 1:
        raise ValueError("blocks must be positive")
    z = 1
    clauses: list[Clause] = []
    next_variable = 2
    for _ in range(blocks):
        a, b, c, d = range(next_variable, next_variable + 4)
        next_variable += 4
        clauses.append((z, a, b))
        clauses.append((-z, c, d))
        clauses.extend(((-a, c), (-c, a), (-b, d), (-d, b)))
    return tuple(clauses), z


def disjoint_positive_3clauses(blocks: int) -> Formula:
    if blocks < 1:
        raise ValueError("blocks must be positive")
    return tuple(
        (3 * index + 1, 3 * index + 2, 3 * index + 3)
        for index in range(blocks)
    )


def brute_force_status(formula: Formula) -> str:
    vars_ = variables(formula)
    for bits in product((False, True), repeat=len(vars_)):
        assignment = dict(zip(vars_, bits))
        if satisfies(formula, assignment):
            return "SAT"
    return "UNSAT"


def random_formula(
    rng: random.Random,
    variable_count: int,
    clause_count: int,
) -> Formula:
    clauses: list[Clause] = []
    for _ in range(clause_count):
        width = rng.choice((1, 2, 3))
        selected = rng.sample(range(1, variable_count + 1), k=width)
        clauses.append(
            tuple(variable if rng.getrandbits(1) else -variable for variable in selected)
        )
    return tuple(clauses)


def run_audit() -> dict[str, object]:
    guarded_records = []
    for blocks in (1, 2, 4, 8, 16, 32):
        formula, selector = guarded_3cnf_family(blocks)
        backdoor = minimum_strong_2sat_backdoor(formula)
        result = solve_via_backdoor(formula, backdoor)
        guarded_records.append(
            {
                "blocks": blocks,
                "variables": len(variables(formula)),
                "clauses": len(formula),
                "minimum_backdoor": backdoor,
                "branch_bound": 2 ** len(backdoor),
                "status": result["status"],
                "explored_branches": result["explored_branches"],
                "selector": selector,
            }
        )

    disjoint_records = []
    for blocks in range(1, 6):
        formula = disjoint_positive_3clauses(blocks)
        backdoor = minimum_strong_2sat_backdoor(formula)
        disjoint_records.append(
            {
                "blocks": blocks,
                "variables": 3 * blocks,
                "minimum_backdoor_size": len(backdoor),
                "expected": blocks,
                "status": brute_force_status(formula),
            }
        )

    rng = random.Random(9379992)
    fuzz_cases = 60
    matches = 0
    backdoor_sizes: list[int] = []
    for _ in range(fuzz_cases):
        variable_count = rng.randint(3, 7)
        formula = random_formula(
            rng,
            variable_count,
            rng.randint(variable_count, 2 * variable_count + 3),
        )
        backdoor = minimum_strong_2sat_backdoor(formula)
        result = solve_via_backdoor(formula, backdoor)
        expected = brute_force_status(formula)
        matches += int(result["status"] == expected)
        backdoor_sizes.append(len(backdoor))

    return {
        "artifact": "JANUS-TEAR-STRONG-2SAT-BACKDOOR-AUDIT",
        "status": "EXPLORATORY_SOFTWARE_ONLY",
        "exact_complexity": "O(2^k poly(L)) for supplied backdoor size k",
        "guarded_non_xor_3cnf": guarded_records,
        "linear_backdoor_easy_family": disjoint_records,
        "random_fuzz": {
            "seed": 9379992,
            "cases": fuzz_cases,
            "matches": matches,
            "minimum_backdoor_sizes": backdoor_sizes,
        },
        "conclusions": {
            "positive": (
                "A one-variable Tear gateway can reduce arbitrarily large "
                "guarded 3-CNF instances to two polynomial 2-SAT branches."
            ),
            "negative": (
                "A fixed 2-SAT backdoor language is not universal: even disjoint "
                "easy positive 3-clauses require one backdoor variable per clause."
            ),
            "conditional_route": (
                "If every CNF had an efficiently found O(log L) backdoor to a "
                "polynomial Tear language, SAT would be in P."
            ),
            "remaining_problem": (
                "Choose or synthesize the tractable language as well as the "
                "backdoor without hiding exponential search."
            ),
        },
        "claim_boundary": "This is a parameterized solver result, not P=NP.",
    }


def self_test() -> None:
    for blocks in range(1, 11):
        formula, selector = guarded_3cnf_family(blocks)
        backdoor = minimum_strong_2sat_backdoor(formula)
        assert len(backdoor) == 1
        assert selector in backdoor
        result = solve_via_backdoor(formula, backdoor)
        assert result["status"] == "SAT"
        assert result["maximum_branches"] == 2

    for blocks in range(1, 6):
        formula = disjoint_positive_3clauses(blocks)
        backdoor = minimum_strong_2sat_backdoor(formula)
        assert len(backdoor) == blocks
        assert brute_force_status(formula) == "SAT"

    audit = run_audit()
    assert audit["random_fuzz"]["matches"] == audit["random_fuzz"]["cases"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--guarded-blocks", type=int)
    parser.add_argument("--disjoint-blocks", type=int)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        self_test()
        print("JANUS_TEAR_STRONG_2SAT_BACKDOOR_SELF_TEST = PASS")
        print("GUARDED_3CNF_MIN_BACKDOOR = 1")
        print("DISJOINT_3CLAUSE_MIN_BACKDOOR = clause_count")
        print("RANDOM_FUZZ = 60/60")
        return 0
    if args.guarded_blocks is not None:
        formula, _ = guarded_3cnf_family(args.guarded_blocks)
        backdoor = minimum_strong_2sat_backdoor(formula)
        print(json.dumps(solve_via_backdoor(formula, backdoor), indent=2))
        return 0
    if args.disjoint_blocks is not None:
        formula = disjoint_positive_3clauses(args.disjoint_blocks)
        backdoor = minimum_strong_2sat_backdoor(formula)
        print(
            json.dumps(
                {
                    "blocks": args.disjoint_blocks,
                    "minimum_backdoor": backdoor,
                    "minimum_backdoor_size": len(backdoor),
                },
                indent=2,
            )
        )
        return 0
    if args.json:
        print(json.dumps(run_audit(), indent=2))
        return 0
    raise SystemExit(
        "use --self-test, --json, --guarded-blocks N, or --disjoint-blocks N"
    )


if __name__ == "__main__":
    raise SystemExit(main())
