"""C023 component dispatcher and heterogeneous backdoor checker."""
from __future__ import annotations
import hashlib
import itertools
import json
from collections import deque
from typing import Any
from janus_c023_primitives import canonical_cnf, horn_solve
from janus_c023_affine import affine_solve
from janus_c023_basis import dual_horn_solve, two_sat_solve
from janus_c023_polymorphism_core import *

def common_fingerprint(component: list[Constraint]) -> frozenset[str]:
    if any(not c.relation.tuples for c in component):
        return frozenset()
    common = set(OPS)
    for constraint in component:
        common &= set(fingerprint(constraint.relation))
    return frozenset(common)


def dispatch_component(component: list[Constraint]) -> DispatchResult:
    if any(not c.relation.tuples for c in component):
        return DispatchResult(
            "EXACT", False, None, ["EMPTY"], len(component), 1,
            "EMPTY_RELATION",
        )

    vars_ = sorted({v for c in component for v in c.scope})
    common = common_fingerprint(component)
    if not common:
        return DispatchResult(
            "OPEN", None, None, [], 0, 0,
            "NO_COMMON_SCHAEFER_POLYMORPHISM",
        )

    if "ZERO" in common:
        assignment = {v: False for v in vars_}
        if not instance_satisfied(component, assignment):
            raise AssertionError("ZERO fingerprint produced invalid witness")
        return DispatchResult(
            "EXACT", True, assignment, ["ZERO"], len(component), len(vars_),
            "ALL_ZERO_WITNESS",
        )
    if "ONE" in common:
        assignment = {v: True for v in vars_}
        if not instance_satisfied(component, assignment):
            raise AssertionError("ONE fingerprint produced invalid witness")
        return DispatchResult(
            "EXACT", True, assignment, ["ONE"], len(component), len(vars_),
            "ALL_ONE_WITNESS",
        )

    if "AND" in common:
        clauses: list[Clause] = []
        for constraint in component:
            local = compile_horn_relation(constraint.relation)
            clauses.extend(map_local_clause(c, constraint.scope) for c in local)
        formula = canonical_cnf(clauses)
        result = horn_solve(formula)
        if result.sat:
            assert result.assignment is not None
            assignment = {v: result.assignment.get(v, False) for v in vars_}
            if not instance_satisfied(component, assignment):
                raise AssertionError("Horn dispatch witness failed")
            return DispatchResult(
                "EXACT", True, assignment, ["AND"], len(component),
                result.rule_scans, "HORN_WITNESS",
            )
        return DispatchResult(
            "EXACT", False, None, ["AND"], len(component),
            result.rule_scans, "HORN_TEAR",
        )

    if "OR" in common:
        clauses = []
        for constraint in component:
            local = compile_dual_horn_relation(constraint.relation)
            clauses.extend(map_local_clause(c, constraint.scope) for c in local)
        formula = canonical_cnf(clauses)
        sat, assignment, steps = dual_horn_solve(formula)
        if sat:
            assert assignment is not None
            normalized = {v: assignment.get(v, True) for v in vars_}
            if not instance_satisfied(component, normalized):
                raise AssertionError("dual-Horn dispatch witness failed")
            return DispatchResult(
                "EXACT", True, normalized, ["OR"], len(component), steps,
                "DUAL_HORN_WITNESS",
            )
        return DispatchResult(
            "EXACT", False, None, ["OR"], len(component), steps,
            "DUAL_HORN_TEAR",
        )

    if "MAJ" in common:
        clauses = []
        for constraint in component:
            local = compile_bijunctive_relation(constraint.relation)
            clauses.extend(map_local_clause(c, constraint.scope) for c in local)
        formula = canonical_cnf(clauses)
        sat, assignment, steps, certificate = two_sat_solve(formula)
        if sat:
            assert assignment is not None
            normalized = {v: assignment.get(v, False) for v in vars_}
            if not instance_satisfied(component, normalized):
                raise AssertionError("2-SAT dispatch witness failed")
            return DispatchResult(
                "EXACT", True, normalized, ["MAJ"], len(component), steps,
                "2SAT_WITNESS",
            )
        return DispatchResult(
            "EXACT", False, None, ["MAJ"], len(component), steps,
            "2SAT_SCC_TEAR",
        )

    if "XOR3" in common:
        equations = []
        for constraint in component:
            local = compile_affine_relation(constraint.relation)
            for local_vars, rhs in local:
                equations.append(
                    (tuple(constraint.scope[i - 1] for i in local_vars), rhs)
                )
        solution = affine_solve(equations, vars_, {})
        steps = solution.row_operations + len(equations)
        if solution.consistent:
            assert solution.particular_mask is not None
            assignment = solution.assignment_from_mask(solution.particular_mask)
            if not instance_satisfied(component, assignment):
                raise AssertionError("affine dispatch witness failed")
            return DispatchResult(
                "EXACT", True, assignment, ["XOR3"], len(component), steps,
                "AFFINE_WITNESS",
            )
        return DispatchResult(
            "EXACT", False, None, ["XOR3"], len(component), steps,
            "AFFINE_ZERO_EQUALS_ONE_TEAR",
        )

    raise AssertionError(common)


def dispatch_instance(constraints: list[Constraint]) -> DispatchResult:
    assignments: dict[int, bool] = {}
    targets: list[str] = []
    compiled = 0
    proof_steps = 0

    for component in components(constraints):
        result = dispatch_component(component)
        if result.status != "EXACT":
            return DispatchResult(
                "OPEN", None, None, targets, compiled, proof_steps,
                result.reason,
            )
        targets.extend(result.component_targets)
        compiled += result.compiled_constraints
        proof_steps += result.proof_steps
        if result.sat is False:
            return DispatchResult(
                "EXACT", False, None, targets, compiled, proof_steps,
                result.reason,
            )
        assert result.assignment is not None
        for v, value in result.assignment.items():
            if v in assignments and assignments[v] != value:
                raise AssertionError("component assignments overlap inconsistently")
            assignments[v] = value

    if not instance_satisfied(constraints, assignments):
        raise AssertionError("merged component witness failed")
    return DispatchResult(
        "EXACT", True, assignments, targets, compiled, proof_steps,
        "COMPONENT_WITNESS",
    )


def restrict_constraint(
    constraint: Constraint,
    fixed: dict[int, bool],
) -> Constraint | None:
    remaining_indices = [i for i, v in enumerate(constraint.scope) if v not in fixed]
    remaining_scope = tuple(constraint.scope[i] for i in remaining_indices)
    accepted = set()

    for row in constraint.relation.tuples:
        if any(
            bool(row[i]) != fixed[v]
            for i, v in enumerate(constraint.scope)
            if v in fixed
        ):
            continue
        accepted.add(tuple(row[i] for i in remaining_indices))

    if not remaining_scope:
        if () in accepted:
            return None
        return Constraint(Relation("EMPTY0", 0, frozenset()), ())

    full = set(all_tuples(len(remaining_scope)))
    if accepted == full:
        return None
    name_data = json.dumps(
        [constraint.relation.name, sorted(accepted)],
        sort_keys=True,
    )
    name = "R_" + hashlib.sha256(name_data.encode()).hexdigest()[:12]
    relation = Relation(name, len(remaining_scope), frozenset(accepted))
    return Constraint(relation, remaining_scope)


def restrict_instance(
    constraints: list[Constraint],
    fixed: dict[int, bool],
) -> list[Constraint]:
    out = []
    for constraint in constraints:
        residual = restrict_constraint(constraint, fixed)
        if residual is not None:
            out.append(residual)
    return out


def is_strong_polymorphism_backdoor(
    constraints: list[Constraint],
    backdoor: tuple[int, ...],
) -> bool:
    for bits in itertools.product((False, True), repeat=len(backdoor)):
        residual = restrict_instance(constraints, dict(zip(backdoor, bits)))
        result = dispatch_instance(residual)
        if result.status != "EXACT":
            return False
    return True


def minimum_strong_backdoor(
    constraints: list[Constraint],
    max_size: int,
) -> tuple[int, ...] | None:
    vars_ = instance_variables(constraints)
    for size in range(max_size + 1):
        for candidate in itertools.combinations(vars_, size):
            if is_strong_polymorphism_backdoor(constraints, candidate):
                return candidate
    return None
