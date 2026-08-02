#!/usr/bin/env python3
"""Finite falsification audit for a concrete JANUS Tear policy.

Policy-0A is deliberately explicit:

1. exact visible affine-block recognition at the root;
2. exhaustive unit propagation at every residual;
3. a polynomially budgeted one-step resolution pass;
4. deterministic most-frequent-variable branching, false first;
5. exact residual-CNF memoization.

The attack compares an explicit odd-charge Tseitin contradiction with the same
edge semantics hidden behind the local bijection

    x = b XOR (a AND c).

On cubic graphs the masking has constant-size overhead per vertex, so the CNF
size remains linear in the graph size.  The executable result is finite: it
falsifies this exact policy/envelope, not every possible Tear algorithm and not
P versus NP.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import product
from typing import Callable, Iterable, Sequence

Clause = tuple[int, ...]
CNF = tuple[Clause, ...]
Edge = tuple[int, int]


def canonical_clause(clause: Iterable[int]) -> Clause | None:
    literals = set(clause)
    if any(-literal in literals for literal in literals):
        return None
    return tuple(sorted(literals, key=lambda literal: (abs(literal), literal < 0)))


def canonical_cnf(clauses: Iterable[Iterable[int]]) -> CNF:
    normalized: set[Clause] = set()
    for clause in clauses:
        candidate = canonical_clause(clause)
        if candidate is not None:
            normalized.add(candidate)
    return tuple(sorted(normalized, key=lambda clause: (len(clause), clause)))


def simplify_one(cnf: CNF, variable: int, value: bool) -> CNF | None:
    true_literal = variable if value else -variable
    false_literal = -true_literal
    residual: list[Clause] = []

    for clause in cnf:
        if true_literal in clause:
            continue
        if false_literal in clause:
            reduced = tuple(literal for literal in clause if literal != false_literal)
            if not reduced:
                return None
            residual.append(reduced)
        else:
            residual.append(clause)

    return canonical_cnf(residual)


def unit_propagate(cnf: CNF) -> tuple[CNF | None, bool]:
    while True:
        units = [clause[0] for clause in cnf if len(clause) == 1]
        if not units:
            return cnf, False

        assignments: dict[int, bool] = {}
        for literal in units:
            variable = abs(literal)
            value = literal > 0
            if variable in assignments and assignments[variable] != value:
                return None, True
            assignments[variable] = value

        for variable, value in sorted(assignments.items()):
            cnf = simplify_one(cnf, variable, value)
            if cnf is None:
                return None, True
            if not cnf:
                return cnf, False


def limited_resolution(
    cnf: CNF,
    max_width: int,
    attempt_budget: int,
    addition_budget: int,
) -> tuple[CNF, bool, int, int]:
    """Try a deterministic polynomial number of resolution pairs.

    The budget is charged in attempted complementary pairs and added clauses.
    Newly added clauses are stored, but the current pass does not recursively
    re-index them.  This makes the exact policy and its cost boundary explicit.
    """

    clauses = set(cnf)
    positive: dict[int, list[Clause]] = defaultdict(list)
    negative: dict[int, list[Clause]] = defaultdict(list)

    for clause in sorted(clauses, key=lambda item: (len(item), item)):
        for literal in clause:
            target = positive if literal > 0 else negative
            target[abs(literal)].append(clause)

    attempts = 0
    additions = 0

    for pivot in sorted(set(positive) & set(negative)):
        for left in positive[pivot]:
            for right in negative[pivot]:
                attempts += 1
                if attempts > attempt_budget or additions >= addition_budget:
                    return canonical_cnf(clauses), False, attempts - 1, additions

                resolvent = (set(left) - {pivot}) | (set(right) - {-pivot})
                if any(-literal in resolvent for literal in resolvent):
                    continue
                if len(resolvent) > max_width:
                    continue

                normalized = canonical_clause(resolvent)
                if normalized is None:
                    continue
                if not normalized:
                    return canonical_cnf(clauses | {()}), True, attempts, additions + 1
                if normalized not in clauses:
                    clauses.add(normalized)
                    additions += 1

    return canonical_cnf(clauses), False, attempts, additions


def exact_relation_cnf(
    variables: Sequence[int],
    predicate: Callable[[tuple[int, ...]], bool],
) -> CNF:
    clauses: list[Clause] = []
    for bits in product((0, 1), repeat=len(variables)):
        if predicate(bits):
            continue
        clauses.append(
            tuple(-variable if bit else variable for variable, bit in zip(variables, bits))
        )
    return canonical_cnf(clauses)


def normalized_edges(edges: Iterable[Edge]) -> tuple[Edge, ...]:
    return tuple(sorted(tuple(sorted(edge)) for edge in edges))


def visible_tseitin_cnf(vertex_count: int, edges: Iterable[Edge]) -> tuple[CNF, int]:
    edge_list = normalized_edges(edges)
    edge_variable = {edge: index + 1 for index, edge in enumerate(edge_list)}
    charges = [1] + [0] * (vertex_count - 1)
    clauses: list[Clause] = []

    for vertex in range(vertex_count):
        incident = [edge_variable[edge] for edge in edge_list if vertex in edge]
        charge = charges[vertex]
        clauses.extend(
            exact_relation_cnf(
                incident,
                lambda bits, charge=charge: sum(bits) % 2 == charge,
            )
        )

    return canonical_cnf(clauses), len(edge_list)


def masked_tseitin_cnf(vertex_count: int, edges: Iterable[Edge]) -> tuple[CNF, int]:
    edge_list = normalized_edges(edges)
    triples: dict[Edge, tuple[int, int, int]] = {}
    next_variable = 1

    for edge in edge_list:
        triples[edge] = (next_variable, next_variable + 1, next_variable + 2)
        next_variable += 3

    charges = [1] + [0] * (vertex_count - 1)
    clauses: list[Clause] = []

    for vertex in range(vertex_count):
        incident = [edge for edge in edge_list if vertex in edge]
        variables = [variable for edge in incident for variable in triples[edge]]
        charge = charges[vertex]

        def relation(bits: tuple[int, ...], charge: int = charge) -> bool:
            parity = 0
            for offset in range(0, len(bits), 3):
                a, b, c = bits[offset : offset + 3]
                parity ^= b ^ (a & c)
            return parity == charge

        clauses.extend(exact_relation_cnf(variables, relation))

    return canonical_cnf(clauses), next_variable - 1


def exact_scope_relations(cnf: CNF, max_scope: int = 10):
    groups: dict[tuple[int, ...], list[Clause]] = defaultdict(list)
    for clause in cnf:
        scope = tuple(sorted(abs(literal) for literal in clause))
        if len(scope) == len(clause) and len(scope) <= max_scope:
            groups[scope].append(clause)

    for scope, clauses in sorted(groups.items()):
        forbidden: set[tuple[int, ...]] = set()
        for clause in clauses:
            signs = {abs(literal): int(literal < 0) for literal in clause}
            forbidden.add(tuple(signs[variable] for variable in scope))
        allowed = set(product((0, 1), repeat=len(scope))) - forbidden
        yield scope, allowed, len(clauses)


def affine_equations(scope: tuple[int, ...], allowed: set[tuple[int, ...]]):
    if not allowed:
        return [((), 1)]

    equations: list[tuple[tuple[int, ...], int]] = []
    width = len(scope)

    for mask in range(1, 1 << width):
        values = {
            sum(((mask >> index) & 1) * bits[index] for index in range(width)) % 2
            for bits in allowed
        }
        if len(values) == 1:
            rhs = next(iter(values))
            variables = tuple(
                scope[index] for index in range(width) if (mask >> index) & 1
            )
            equations.append((variables, rhs))

    reconstructed: set[tuple[int, ...]] = set()
    positions = {variable: index for index, variable in enumerate(scope)}
    for bits in product((0, 1), repeat=width):
        if all(
            sum(bits[positions[variable]] for variable in variables) % 2 == rhs
            for variables, rhs in equations
        ):
            reconstructed.add(bits)

    return equations if reconstructed == allowed else None


def gaussian_inconsistent(
    equations: Sequence[tuple[tuple[int, ...], int]],
    variable_count: int,
) -> bool:
    rows: list[list[int]] = []
    for variables, rhs in equations:
        mask = 0
        for variable in variables:
            mask ^= 1 << (variable - 1)
        rows.append([mask, rhs])

    pivot_row = 0
    for column in range(variable_count):
        source = next(
            (
                row
                for row in range(pivot_row, len(rows))
                if (rows[row][0] >> column) & 1
            ),
            None,
        )
        if source is None:
            continue
        rows[pivot_row], rows[source] = rows[source], rows[pivot_row]
        for row in range(len(rows)):
            if row != pivot_row and ((rows[row][0] >> column) & 1):
                rows[row][0] ^= rows[pivot_row][0]
                rows[row][1] ^= rows[pivot_row][1]
        pivot_row += 1

    return any(mask == 0 and rhs == 1 for mask, rhs in rows)


def visible_affine_root_decision(cnf: CNF, variable_count: int):
    equations: list[tuple[tuple[int, ...], int]] = []
    covered_clauses = 0

    for scope, allowed, clause_count in exact_scope_relations(cnf):
        relation_equations = affine_equations(scope, allowed)
        if relation_equations is None:
            continue
        equations.extend(relation_equations)
        covered_clauses += clause_count

    if covered_clauses != len(cnf):
        return None, 0

    return not gaussian_inconsistent(equations, variable_count), len(equations)


@dataclass
class PolicyResult:
    answer: bool | None
    cap_exceeded: bool
    residual_states: int
    memo_entries: int
    resolution_attempts: int
    resolution_additions: int
    affine_equations: int


class Policy0A:
    def __init__(self, state_cap: int | None = None):
        self.state_cap = state_cap

    def solve(self, cnf: CNF, variable_count: int) -> PolicyResult:
        self.states = 0
        self.memo: dict[CNF, bool] = {}
        self.resolution_attempts = 0
        self.resolution_additions = 0

        affine_answer, equation_count = visible_affine_root_decision(cnf, variable_count)
        self.affine_equation_count = equation_count
        if affine_answer is not None:
            return self.result(affine_answer, False)

        try:
            answer = self.search(cnf)
            return self.result(answer, False)
        except RuntimeError:
            return self.result(None, True)

    def result(self, answer: bool | None, cap_exceeded: bool) -> PolicyResult:
        return PolicyResult(
            answer=answer,
            cap_exceeded=cap_exceeded,
            residual_states=self.states,
            memo_entries=len(self.memo),
            resolution_attempts=self.resolution_attempts,
            resolution_additions=self.resolution_additions,
            affine_equations=self.affine_equation_count,
        )

    def search(self, cnf: CNF) -> bool:
        propagated, contradiction = unit_propagate(cnf)
        if contradiction:
            return False
        assert propagated is not None
        if not propagated:
            return True
        cnf = propagated

        if cnf in self.memo:
            return self.memo[cnf]

        self.states += 1
        if self.state_cap is not None and self.states > self.state_cap:
            raise RuntimeError("state cap exceeded")

        literal_count = sum(len(clause) for clause in cnf)
        width_limit = max(len(clause) for clause in cnf) + 1
        saturated, refuted, attempts, additions = limited_resolution(
            cnf,
            max_width=width_limit,
            attempt_budget=max(64, 4 * literal_count),
            addition_budget=max(8, len(cnf) // 4),
        )
        self.resolution_attempts += attempts
        self.resolution_additions += additions

        if refuted:
            self.memo[cnf] = False
            return False

        propagated, contradiction = unit_propagate(saturated)
        if contradiction:
            self.memo[cnf] = False
            return False
        assert propagated is not None
        if not propagated:
            self.memo[cnf] = True
            return True

        frequencies = Counter(
            abs(literal) for clause in propagated for literal in clause
        )
        maximum = max(frequencies.values())
        variable = min(
            candidate
            for candidate, frequency in frequencies.items()
            if frequency == maximum
        )

        for value in (False, True):
            child = simplify_one(propagated, variable, value)
            if child is not None and self.search(child):
                self.memo[cnf] = True
                return True

        self.memo[cnf] = False
        return False


K4_EDGES: tuple[Edge, ...] = (
    (0, 1),
    (0, 2),
    (0, 3),
    (1, 2),
    (1, 3),
    (2, 3),
)

K33_EDGES: tuple[Edge, ...] = tuple(
    (left, 3 + right) for left in range(3) for right in range(3)
)


def run_case(name: str, vertex_count: int, edges: Sequence[Edge], masked: bool, cap=None):
    generator = masked_tseitin_cnf if masked else visible_tseitin_cnf
    cnf, variable_count = generator(vertex_count, edges)
    result = Policy0A(state_cap=cap).solve(cnf, variable_count)
    print(f"CASE = {name}")
    print(f"  variables = {variable_count}")
    print(f"  clauses = {len(cnf)}")
    print(f"  maximum_width = {max(map(len, cnf))}")
    print(f"  answer = {result.answer}")
    print(f"  cap_exceeded = {str(result.cap_exceeded).lower()}")
    print(f"  residual_states = {result.residual_states}")
    print(f"  memo_entries = {result.memo_entries}")
    print(f"  affine_equations = {result.affine_equations}")
    print(f"  resolution_attempts = {result.resolution_attempts}")
    print(f"  resolution_additions = {result.resolution_additions}")
    return cnf, variable_count, result


def self_test() -> None:
    _, _, visible = run_case("VISIBLE_K4", 4, K4_EDGES, masked=False)
    assert visible.answer is False
    assert not visible.cap_exceeded
    assert visible.residual_states == 0
    assert visible.affine_equations == 4

    _, _, masked_k4 = run_case("MASKED_K4_EXACT", 4, K4_EDGES, masked=True)
    assert masked_k4.answer is False
    assert not masked_k4.cap_exceeded
    assert masked_k4.residual_states == 3842
    assert masked_k4.affine_equations == 0

    masked_k33_cnf, masked_k33_variables, _ = run_case(
        "MASKED_K33_QUADRATIC_CAP",
        6,
        K33_EDGES,
        masked=True,
        cap=4 * 27 * 27,
    )
    assert masked_k33_variables == 27
    assert len(masked_k33_cnf) == 1536
    capped = Policy0A(state_cap=4 * masked_k33_variables**2).solve(
        masked_k33_cnf,
        masked_k33_variables,
    )
    assert capped.answer is None
    assert capped.cap_exceeded
    assert capped.residual_states == 4 * masked_k33_variables**2 + 1

    print("JANUS_TEAR_POLICY0A_SELF_TEST = PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--case",
        choices=("visible-k4", "masked-k4", "masked-k33"),
        default="masked-k4",
    )
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return

    if args.case == "visible-k4":
        run_case("VISIBLE_K4", 4, K4_EDGES, masked=False)
    elif args.case == "masked-k4":
        run_case("MASKED_K4_EXACT", 4, K4_EDGES, masked=True)
    else:
        run_case(
            "MASKED_K33_QUADRATIC_CAP",
            6,
            K33_EDGES,
            masked=True,
            cap=4 * 27 * 27,
        )


if __name__ == "__main__":
    main()
