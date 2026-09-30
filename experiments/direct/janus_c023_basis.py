"""C023 exact affine-basis language rewrite."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from janus_c023_primitives import *
from janus_c023_affine import *

# ---------------------------------------------------------------------------
# Basis-language rewrite: avoid 2^d when normalization exposes another P class
# ---------------------------------------------------------------------------

@dataclass
class BasisSolveResult:
    supported: bool
    sat: bool | None
    target_language: str | None
    assignment: dict[int, bool] | None
    solver_steps: int
    reason: str
    parameter_ids: tuple[int, ...]
    rewritten_formula: CNF | None


def dual_horn_solve(
    formula: CNF,
) -> tuple[bool, dict[int, bool] | None, int]:
    if not all(sum(1 for lit in clause if lit < 0) <= 1 for clause in formula):
        raise ValueError("formula is not dual-Horn")
    transformed = canonical_cnf(tuple(tuple(-lit for lit in clause) for clause in formula))
    result = horn_solve(transformed)
    if not result.sat:
        return False, None, result.rule_scans
    assert result.assignment is not None
    assignment = {v: not value for v, value in result.assignment.items()}
    if not satisfies_cnf(formula, assignment):
        raise AssertionError("dual-Horn witness failed")
    return True, assignment, result.rule_scans


def two_sat_solve(
    formula: CNF,
) -> tuple[bool, dict[int, bool] | None, int, dict[str, Any] | None]:
    if any(len(clause) > 2 for clause in formula):
        raise ValueError("formula is not 2-CNF")
    vars_ = cnf_variables(formula)
    adjacency: dict[int, list[int]] = {lit: [] for v in vars_ for lit in (v, -v)}
    reverse: dict[int, list[int]] = {lit: [] for v in vars_ for lit in (v, -v)}
    edges = 0

    def add_edge(a: int, b: int) -> None:
        nonlocal edges
        adjacency.setdefault(a, []).append(b)
        reverse.setdefault(b, []).append(a)
        adjacency.setdefault(b, [])
        reverse.setdefault(a, [])
        edges += 1

    for clause in formula:
        if len(clause) == 0:
            return False, None, edges, {"kind": "EMPTY_CLAUSE"}
        if len(clause) == 1:
            a = clause[0]
            add_edge(-a, a)
        else:
            a, b = clause
            add_edge(-a, b)
            add_edge(-b, a)

    seen: set[int] = set()
    order: list[int] = []

    def dfs1(start: int) -> None:
        stack = [(start, 0)]
        seen.add(start)
        while stack:
            node, index = stack[-1]
            if index < len(adjacency[node]):
                nxt = adjacency[node][index]
                stack[-1] = (node, index + 1)
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append((nxt, 0))
            else:
                order.append(node)
                stack.pop()

    for node in list(adjacency):
        if node not in seen:
            dfs1(node)

    component: dict[int, int] = {}
    cid = 0
    for start in reversed(order):
        if start in component:
            continue
        stack = [start]
        component[start] = cid
        while stack:
            node = stack.pop()
            for nxt in reverse[node]:
                if nxt not in component:
                    component[nxt] = cid
                    stack.append(nxt)
        cid += 1

    def path_inside(start: int, target: int, wanted: int) -> list[int]:
        queue = [start]
        parent = {start: None}
        for node in queue:
            if node == target:
                break
            for nxt in adjacency[node]:
                if component.get(nxt) != wanted or nxt in parent:
                    continue
                parent[nxt] = node
                queue.append(nxt)
        if target not in parent:
            return []
        path = []
        node: int | None = target
        while node is not None:
            path.append(node)
            node = parent[node]
        return list(reversed(path))

    for v in vars_:
        if component[v] == component[-v]:
            c = component[v]
            certificate = {
                "kind": "2SAT_SCC_CONTRADICTION",
                "variable": v,
                "path_positive_to_negative": path_inside(v, -v, c),
                "path_negative_to_positive": path_inside(-v, v, c),
            }
            return False, None, edges + len(order), certificate

    assignment_a = {v: component[v] > component[-v] for v in vars_}
    if satisfies_cnf(formula, assignment_a):
        return True, assignment_a, edges + len(order), None
    assignment_b = {v: not value for v, value in assignment_a.items()}
    if satisfies_cnf(formula, assignment_b):
        return True, assignment_b, edges + len(order), None
    raise AssertionError("2-SAT SCC assignment extraction failed")


def rewrite_horn_over_affine_basis(
    horn: CNF,
    fixed: dict[int, bool],
    affine: AffineSolution,
    projected: ProjectedAffine,
    interface: list[int],
) -> BasisSolveResult:
    residual = simplify_cnf(horn, fixed)
    if () in residual:
        return BasisSolveResult(
            True, False, "CONSTANT_CONTRADICTION", None, 1,
            "fixed values create an empty Horn clause", (), residual,
        )

    pos = {v: i for i, v in enumerate(affine.variables)}
    base = max(
        [0]
        + cnf_variables(residual)
        + list(interface)
        + list(affine.variables)
    )
    parameter_ids = tuple(base + 1 + i for i in range(projected.dimension))
    interface_set = set(interface)
    rewritten: list[Clause] = []

    for clause in residual:
        new_clause: list[int] = []
        clause_true = False
        for lit in clause:
            v = abs(lit)
            if v not in interface_set:
                new_clause.append(lit)
                continue

            bit = pos[v]
            constant = bool((projected.particular_full_mask >> bit) & 1)
            dependencies = [
                i
                for i, direction in enumerate(projected.direction_full_masks)
                if (direction >> bit) & 1
            ]
            if len(dependencies) > 1:
                return BasisSolveResult(
                    False, None, None, None, 0,
                    "interface variable depends on multiple affine basis bits",
                    parameter_ids, None,
                )

            if not dependencies:
                literal_value = constant if lit > 0 else (not constant)
                if literal_value:
                    clause_true = True
                    break
                continue

            parameter = parameter_ids[dependencies[0]]
            positive_maps_to_positive_t = not constant
            if lit < 0:
                positive_maps_to_positive_t = not positive_maps_to_positive_t
            new_clause.append(parameter if positive_maps_to_positive_t else -parameter)

        if clause_true:
            continue
        canonical = canonical_clause(new_clause)
        if canonical is None:
            continue
        rewritten.append(canonical)

    formula = canonical_cnf(rewritten)
    if not formula:
        return BasisSolveResult(
            True, True, "TRUE", {v: False for v in parameter_ids}, 1,
            "rewritten basis formula is TRUE", parameter_ids, formula,
        )
    if () in formula:
        return BasisSolveResult(
            True, False, "CONSTANT_CONTRADICTION", None, 1,
            "rewritten basis formula contains empty clause", parameter_ids, formula,
        )

    if is_horn(formula):
        result = horn_solve(formula)
        return BasisSolveResult(
            True, result.sat, "HORN", result.assignment, result.rule_scans,
            "basis formula is Horn", parameter_ids, formula,
        )

    if all(sum(1 for lit in clause if lit < 0) <= 1 for clause in formula):
        sat, assignment, steps = dual_horn_solve(formula)
        return BasisSolveResult(
            True, sat, "DUAL_HORN", assignment, steps,
            "basis formula is dual-Horn", parameter_ids, formula,
        )

    if all(len(clause) <= 2 for clause in formula):
        sat, assignment, steps, certificate = two_sat_solve(formula)
        return BasisSolveResult(
            True, sat, "2SAT", assignment, steps,
            "basis formula is 2-CNF", parameter_ids, formula,
        )

    return BasisSolveResult(
        False, None, None, None, 0,
        "basis formula is outside Horn, dual-Horn, and 2-SAT",
        parameter_ids, formula,
    )


def recover_basis_witness(
    result: BasisSolveResult,
    affine: AffineSolution,
    projected: ProjectedAffine,
    interface: list[int],
) -> dict[int, bool] | None:
    if not result.supported or not result.sat or result.assignment is None:
        return None
    full_mask = projected.particular_full_mask
    for i, parameter in enumerate(result.parameter_ids):
        if result.assignment.get(parameter, False):
            full_mask ^= projected.direction_full_masks[i]
    witness = affine.assignment_from_mask(full_mask)
    for v, value in result.assignment.items():
        if v not in result.parameter_ids:
            witness[v] = value
    return witness
