#!/usr/bin/env python3
"""Emit and independently replay a finite Policy-0T execution trace.

The trace format records unit batches, local resolvents, deterministic branches,
child restrictions, terminal statuses, and total search-tree consistency.  C022
uses it as the provenance substrate for the non-affine core simulation theorem.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from itertools import product
from typing import Iterable

Clause = tuple[int, ...]
CNF = tuple[Clause, ...]

UNSAT_FORMULA: CNF = (
    (-2, -3, -4),
    (-2, 3, -4),
    (-1, -3, -4),
    (-1, -2, 4),
    (-1, 3, -4),
    (1, -2, -4),
    (1, -2, 4),
    (1, 2, -4),
    (2, -3, 4),
    (2, 3, 4),
)
N_VARS = 4


def canonical_clause(clause: Iterable[int]) -> Clause | None:
    literals = set(clause)
    if any(-literal in literals for literal in literals):
        return None
    return tuple(sorted(literals, key=lambda literal: (abs(literal), literal < 0)))


def canonical_cnf(clauses: Iterable[Iterable[int]]) -> CNF:
    normalized = {
        clause
        for raw in clauses
        if (clause := canonical_clause(raw)) is not None
    }
    return tuple(sorted(normalized, key=lambda clause: (len(clause), clause)))


def simplify_one(cnf: CNF, variable: int, value: bool) -> CNF | None:
    true_literal = variable if value else -variable
    false_literal = -true_literal
    reduced: list[Clause] = []
    for clause in cnf:
        if true_literal in clause:
            continue
        residual = tuple(literal for literal in clause if literal != false_literal)
        if not residual:
            return None
        reduced.append(residual)
    return canonical_cnf(reduced)


def satisfies(cnf: CNF, assignment: tuple[int, ...]) -> bool:
    return all(
        any(
            (literal > 0 and assignment[literal - 1] == 1)
            or (literal < 0 and assignment[-literal - 1] == 0)
            for literal in clause
        )
        for clause in cnf
    )


def affine_equations(
    variables: tuple[int, ...],
    allowed: set[tuple[int, ...]],
) -> tuple[tuple[tuple[int, ...], int], ...] | None:
    if not allowed:
        return ()
    equations: list[tuple[tuple[int, ...], int]] = []
    dimension = len(variables)
    for mask in range(1, 1 << dimension):
        values = {
            sum(bit for index, bit in enumerate(bits) if mask & (1 << index)) % 2
            for bits in allowed
        }
        if len(values) == 1:
            indices = tuple(index for index in range(dimension) if mask & (1 << index))
            equations.append((indices, next(iter(values))))

    predicted = {
        bits
        for bits in product((0, 1), repeat=dimension)
        if all(
            sum(bits[index] for index in indices) % 2 == rhs
            for indices, rhs in equations
        )
    }
    if predicted != allowed:
        return None
    return tuple(equations)


def parity_consistent(equations: Iterable[tuple[int, int]]) -> bool:
    rows = list(equations)
    pivot = 0
    maximum_bit = max((mask.bit_length() for mask, _ in rows), default=0)
    for column in range(maximum_bit):
        selected = next(
            (index for index in range(pivot, len(rows)) if rows[index][0] & (1 << column)),
            None,
        )
        if selected is None:
            continue
        rows[pivot], rows[selected] = rows[selected], rows[pivot]
        pivot_mask, pivot_rhs = rows[pivot]
        for index in range(len(rows)):
            if index != pivot and rows[index][0] & (1 << column):
                mask, rhs = rows[index]
                rows[index] = (mask ^ pivot_mask, rhs ^ pivot_rhs)
        pivot += 1
    return not any(mask == 0 and rhs == 1 for mask, rhs in rows)


def visible_affine_root_decision(cnf: CNF, variable_count: int) -> tuple[bool | None, int]:
    groups: dict[tuple[int, ...], list[Clause]] = defaultdict(list)
    for clause in cnf:
        groups[tuple(sorted(abs(literal) for literal in clause))].append(clause)

    covered: set[Clause] = set()
    global_equations: list[tuple[int, int]] = []
    equation_count = 0

    for scope, clauses in sorted(groups.items()):
        scope_cnf = canonical_cnf(clauses)
        allowed = {
            bits
            for bits in product((0, 1), repeat=len(scope))
            if satisfies(scope_cnf, bits)
        }
        equations = affine_equations(scope, allowed)
        if equations is None:
            continue
        covered.update(scope_cnf)
        equation_count += len(equations)
        for indices, rhs in equations:
            mask = 0
            for index in indices:
                mask |= 1 << (scope[index] - 1)
            global_equations.append((mask, rhs))

    if len(covered) != len(cnf):
        return None, equation_count
    if not parity_consistent(global_equations):
        return False, equation_count
    return None, equation_count


def unit_trace(cnf: CNF):
    current = cnf
    events: list[dict[str, object]] = []
    batch = 0
    while True:
        units = [clause[0] for clause in current if len(clause) == 1]
        if not units:
            return current, False, events

        assignments: dict[int, bool] = {}
        for literal in units:
            variable = abs(literal)
            value = literal > 0
            if variable in assignments and assignments[variable] != value:
                events.append(
                    {
                        "batch": batch,
                        "kind": "opposite_units",
                        "units": tuple(sorted(units)),
                    }
                )
                return None, True, events
            assignments[variable] = value

        batch_cnf = current
        for variable, value in sorted(assignments.items()):
            literal = variable if value else -variable
            before = current
            current = simplify_one(current, variable, value)
            events.append(
                {
                    "batch": batch,
                    "kind": "unit",
                    "literal": literal,
                    "reason": (literal,),
                    "batch_cnf": batch_cnf,
                    "before": before,
                    "after": current,
                }
            )
            if current is None:
                return None, True, events
            if not current:
                return (), False, events
        batch += 1


def resolution_trace(
    cnf: CNF,
    max_width: int,
    attempt_budget: int,
    addition_budget: int,
):
    clauses = set(cnf)
    positive: dict[int, list[Clause]] = defaultdict(list)
    negative: dict[int, list[Clause]] = defaultdict(list)
    for clause in sorted(clauses, key=lambda item: (len(item), item)):
        for literal in clause:
            target = positive if literal > 0 else negative
            target[abs(literal)].append(clause)
    attempts = 0
    additions = 0
    events: list[dict[str, object]] = []
    for pivot in sorted(set(positive) & set(negative)):
        for left in positive[pivot]:
            for right in negative[pivot]:
                attempts += 1
                if attempts > attempt_budget or additions >= addition_budget:
                    return canonical_cnf(clauses), False, attempts - 1, additions, events
                resolvent = (set(left) - {pivot}) | (set(right) - {-pivot})
                if any(-literal in resolvent for literal in resolvent):
                    continue
                if len(resolvent) > max_width:
                    continue
                normalized = canonical_clause(resolvent)
                if normalized is None:
                    continue
                event = {
                    "left": left,
                    "right": right,
                    "pivot": pivot,
                    "resolvent": normalized,
                    "attempt": attempts,
                }
                if not normalized:
                    events.append(event)
                    return canonical_cnf(clauses | {()}), True, attempts, additions + 1, events
                if normalized not in clauses:
                    clauses.add(normalized)
                    additions += 1
                    events.append(event)
    return canonical_cnf(clauses), False, attempts, additions, events


def branch_variable(cnf: CNF) -> int:
    frequencies = Counter(abs(literal) for clause in cnf for literal in clause)
    maximum = max(frequencies.values())
    return min(
        variable for variable, frequency in frequencies.items() if frequency == maximum
    )


class TracePolicy:
    def __init__(self) -> None:
        self.nodes: dict[int, dict[str, object]] = {}
        self.next_id = 0

    def search(self, cnf: CNF, depth: int = 0) -> tuple[bool, int]:
        node_id = self.next_id
        self.next_id += 1
        node: dict[str, object] = {"id": node_id, "input": cnf, "depth": depth}
        self.nodes[node_id] = node

        propagated, contradiction, pre_events = unit_trace(cnf)
        node["pre_units"] = pre_events
        node["pre_result"] = propagated
        if contradiction:
            node["terminal"] = "UNIT_CONTRADICTION"
            node["result"] = False
            return False, node_id
        assert propagated is not None
        if not propagated:
            node["terminal"] = "SAT_EMPTY"
            node["result"] = True
            return True, node_id

        literal_count = sum(len(clause) for clause in propagated)
        width_limit = max(map(len, propagated)) + 1
        attempt_budget = max(64, 4 * literal_count)
        addition_budget = max(8, len(propagated) // 4)
        saturated, refuted, attempts, additions, resolution_events = resolution_trace(
            propagated, width_limit, attempt_budget, addition_budget
        )
        node.update(
            {
                "resolution_output": saturated,
                "resolution_refuted": refuted,
                "resolution_attempts": attempts,
                "resolution_additions": additions,
                "resolution_events": resolution_events,
                "width_limit": width_limit,
                "attempt_budget": attempt_budget,
                "addition_budget": addition_budget,
            }
        )
        if refuted:
            node["terminal"] = "RESOLUTION_CONTRADICTION"
            node["result"] = False
            return False, node_id

        propagated, contradiction, post_events = unit_trace(saturated)
        node["post_units"] = post_events
        node["post_result"] = propagated
        if contradiction:
            node["terminal"] = "POST_UNIT_CONTRADICTION"
            node["result"] = False
            return False, node_id
        assert propagated is not None
        if not propagated:
            node["terminal"] = "SAT_EMPTY"
            node["result"] = True
            return True, node_id

        variable = branch_variable(propagated)
        node["branch_var"] = variable
        node["children"] = []
        children = node["children"]
        assert isinstance(children, list)
        for value in (False, True):
            child = simplify_one(propagated, variable, value)
            if child is None:
                children.append(
                    {"value": value, "child": None, "result": False, "direct_conflict": True}
                )
                continue
            answer, child_id = self.search(child, depth + 1)
            children.append(
                {"value": value, "child": child_id, "result": answer, "direct_conflict": False}
            )
            if answer:
                node["terminal"] = "BRANCH_SAT"
                node["result"] = True
                return True, node_id
        node["terminal"] = "BRANCH_UNSAT"
        node["result"] = False
        return False, node_id


def verify_trace(nodes: dict[int, dict[str, object]], root: int, root_cnf: CNF) -> bool:
    seen: set[int] = set()
    variable_bound = max(
        (abs(literal) for clause in root_cnf for literal in clause),
        default=0,
    )

    def verify_node(node_id: int, expected_input: CNF) -> bool:
        assert node_id not in seen
        seen.add(node_id)
        node = nodes[node_id]
        assert node["input"] == expected_input
        assert int(node["depth"]) <= variable_bound

        propagated, contradiction, events = unit_trace(expected_input)
        assert events == node["pre_units"]
        assert propagated == node["pre_result"]
        if contradiction:
            assert node["result"] is False
            return False
        assert propagated is not None
        if not propagated:
            assert node["result"] is True
            return True

        saturated, refuted, attempts, additions, resolution_events = resolution_trace(
            propagated,
            int(node["width_limit"]),
            int(node["attempt_budget"]),
            int(node["addition_budget"]),
        )
        assert saturated == node["resolution_output"]
        assert refuted == node["resolution_refuted"]
        assert attempts == node["resolution_attempts"]
        assert additions == node["resolution_additions"]
        assert resolution_events == node["resolution_events"]
        initial = set(propagated)
        for event in resolution_events:
            left = event["left"]
            right = event["right"]
            pivot = int(event["pivot"])
            assert left in initial and right in initial
            assert pivot in left and -pivot in right
            raw = (set(left) - {pivot}) | (set(right) - {-pivot})
            assert canonical_clause(raw) == event["resolvent"]
        if refuted:
            assert node["result"] is False
            return False

        propagated, contradiction, events = unit_trace(saturated)
        assert events == node["post_units"]
        assert propagated == node["post_result"]
        if contradiction:
            assert node["result"] is False
            return False
        assert propagated is not None
        if not propagated:
            assert node["result"] is True
            return True

        variable = branch_variable(propagated)
        assert variable == node["branch_var"]
        results: list[bool] = []
        children = node["children"]
        assert isinstance(children, list)
        for child_record in children:
            assert isinstance(child_record, dict)
            value = bool(child_record["value"])
            child_cnf = simplify_one(propagated, variable, value)
            if child_cnf is None:
                assert child_record["child"] is None
                answer = False
            else:
                child_id = child_record["child"]
                assert isinstance(child_id, int)
                answer = verify_node(child_id, child_cnf)
            assert answer == child_record["result"]
            results.append(answer)
            if answer:
                break
        answer = any(results)
        assert answer == node["result"]
        return answer

    answer = verify_node(root, root_cnf)
    assert len(seen) == len(nodes)
    return answer


def self_test() -> None:
    root_cnf = canonical_cnf(UNSAT_FORMULA)
    affine_answer, affine_equations_count = visible_affine_root_decision(root_cnf, N_VARS)
    assert affine_answer is None
    assert affine_equations_count == 0

    policy = TracePolicy()
    answer, root = policy.search(root_cnf)
    assert answer is False
    assert verify_trace(policy.nodes, root, root_cnf) is False

    resolution_events = sum(
        len(node.get("resolution_events", [])) for node in policy.nodes.values()
    )
    unit_events = sum(
        len(node.get("pre_units", [])) + len(node.get("post_units", []))
        for node in policy.nodes.values()
    )
    maximum_depth = max(int(node["depth"]) for node in policy.nodes.values())

    assert len(policy.nodes) == 3
    assert resolution_events == 8
    assert unit_events == 4
    assert maximum_depth == 1

    print("JANUS_TEAR_POLICY0T_TRACE_CERTIFICATE = PASS")
    print("root_affine_shortcut = none")
    print(f"trace_nodes = {len(policy.nodes)}")
    print(f"resolution_events = {resolution_events}")
    print(f"unit_events = {unit_events}")
    print(f"maximum_branch_depth = {maximum_depth}")
    print("root_answer = UNSAT")
    print("claim_boundary = provenance trace; global proof emitted by the C022 translator")


if __name__ == "__main__":
    self_test()
