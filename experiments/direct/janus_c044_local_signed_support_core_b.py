#!/usr/bin/env python3
from __future__ import annotations
from janus_c044_local_signed_support_core_a import *

def compile_signed_union(
    factors: list[Factor],
    scope: tuple[int, ...],
    meter: Meter,
    *,
    accepted_leaf: bool,
) -> dict[str, Any]:
    local_factors = [
        (factor.factor_id, remap_space(factor.space, scope))
        for factor in factors
    ]
    local_factors.sort(key=lambda item: (-len(item[1]), item[1], item[0]))
    coefficients: dict[Subspace, int] = {}
    transitions: list[dict[str, Any]] = []
    meter.check_support(
        0,
        0,
        accepted_leaf=accepted_leaf,
        factor_step=0,
    )
    for step, (factor_id, factor_space) in enumerate(local_factors, 1):
        before = dict(coefficients)
        delta: dict[Subspace, int] = {factor_space: 1}
        intersection_operations: list[dict[str, Any]] = []
        for source_space, source_coefficient in sorted(before.items()):
            meter.charge("signed_transition_term")
            overlap = intersection(
                source_space,
                factor_space,
                len(scope),
                meter,
            )
            contribution = 0 if overlap is None else -source_coefficient
            intersection_operations.append(
                {
                    "source_space": system_payload(source_space),
                    "source_coefficient": source_coefficient,
                    "intersection": system_payload(overlap),
                    "delta_coefficient": contribution,
                }
            )
            if overlap is not None:
                delta[overlap] = delta.get(overlap, 0) + contribution
                if delta[overlap] == 0:
                    del delta[overlap]

        working_support = len(before) + len(delta)
        updated = dict(before)
        merges: list[dict[str, Any]] = []
        for space, contribution in sorted(delta.items()):
            meter.charge("signed_delta_merge")
            old = updated.get(space, 0)
            new = old + contribution
            merges.append(
                {
                    "space": system_payload(space),
                    "old_coefficient": old,
                    "delta_coefficient": contribution,
                    "new_coefficient": new,
                    "deleted_zero": new == 0,
                }
            )
            if new == 0:
                updated.pop(space, None)
            else:
                updated[space] = new
        meter.check_support(
            len(updated),
            working_support,
            accepted_leaf=accepted_leaf,
            factor_step=step,
        )
        transitions.append(
            {
                "step": step,
                "factor_id": factor_id,
                "factor": system_payload(factor_space),
                "before_terms": coefficient_payload(before, len(scope)),
                "intersection_operations": intersection_operations,
                "delta_terms": coefficient_payload(delta, len(scope)),
                "merge_operations": merges,
                "after_terms": coefficient_payload(updated, len(scope)),
                "live_support": len(updated),
                "working_support": working_support,
            }
        )
        coefficients = updated

    return {
        "scope": list(scope),
        "factor_order": [factor_id for factor_id, _ in local_factors],
        "transitions": transitions,
        "terms": coefficient_payload(coefficients, len(scope)),
        "live_support": len(coefficients),
    }


def count_signed_union(
    terms: dict[Subspace, int],
    condition: Subspace,
    dimension: int,
    meter: Meter,
) -> tuple[int, list[dict[str, Any]]]:
    total = 0
    trace: list[dict[str, Any]] = []
    for space, coefficient in sorted(terms.items()):
        meter.charge("conditional_count_term")
        overlap = intersection(space, condition, dimension, meter)
        points = 0 if overlap is None else 1 << system_dimension(overlap, dimension)
        total += coefficient * points
        trace.append(
            {
                "space": system_payload(space),
                "coefficient": coefficient,
                "intersection": system_payload(overlap),
                "points": str(points),
            }
        )
    return total, trace


def graph_components(
    active: set[int],
    factors: list[Factor],
    removed: set[int] | None = None,
) -> list[set[int]]:
    remaining = set(active) - set(removed or ())
    graph = {variable: set() for variable in remaining}
    for factor in factors:
        scope = [variable for variable in factor.scope if variable in remaining]
        for index, left in enumerate(scope):
            for right in scope[index + 1 :]:
                graph[left].add(right)
                graph[right].add(left)
    components: list[set[int]] = []
    while graph:
        start = min(graph)
        stack = [start]
        component: set[int] = set()
        while stack:
            variable = stack.pop()
            if variable in component:
                continue
            component.add(variable)
            stack.extend(graph[variable] - component)
        for variable in component:
            graph.pop(variable, None)
        components.append(component)
    components.sort(key=lambda component: (min(component), len(component)))
    return components


def partition_factors(
    factors: list[Factor],
    active: set[int],
    separator: set[int],
    components: list[set[int]],
) -> tuple[list[Factor], list[list[Factor]]]:
    local: list[Factor] = []
    buckets: list[list[Factor]] = [[] for _ in components]
    for factor in factors:
        remainder = (set(factor.scope) & active) - separator
        if not remainder:
            local.append(factor)
            continue
        hits = [
            index
            for index, component in enumerate(components)
            if remainder <= component
        ]
        if len(hits) != 1:
            raise AssertionError("factor crosses discovered components")
        buckets[hits[0]].append(factor)
    return local, buckets


def find_separator(
    factors: list[Factor],
    active: set[int],
    separator_limit: int,
    meter: Meter,
) -> dict[str, Any] | None:
    components = graph_components(active, factors)
    meter.separator_candidates += 1
    meter.charge("separator_candidate")
    if len(components) >= 2:
        local, buckets = partition_factors(
            factors,
            active,
            set(),
            components,
        )
        return {
            "separator": (),
            "components": components,
            "local": local,
            "buckets": buckets,
            "candidates_tested": 1,
            "kind": "DISCONNECTED",
        }

    tested = 1
    active_size = len(active)
    for size in range(1, min(separator_limit, active_size) + 1):
        for candidate in combinations(sorted(active), size):
            tested += 1
            meter.separator_candidates += 1
            meter.charge("separator_candidate")
            separator = set(candidate)
            components = graph_components(active, factors, separator)
            largest = max((len(component) for component in components), default=0)
            if largest * 3 > max(1, 2 * active_size):
                continue
            local, buckets = partition_factors(
                factors,
                active,
                separator,
                components,
            )
            return {
                "separator": candidate,
                "components": components,
                "local": local,
                "buckets": buckets,
                "candidates_tested": tested,
                "kind": "BALANCED",
            }
    return None


def local_condition(
    assignment: dict[int, bool],
    scope: tuple[int, ...],
) -> Subspace:
    equations = [
        (1 << (index - 1), int(assignment[variable]))
        for index, variable in enumerate(scope, 1)
        if variable in assignment
    ]
    condition = rref_system(equations, len(scope))[0]
    if condition is None:
        raise AssertionError("boundary assignment is inconsistent")
    return condition


def combine_assignments(
    left: dict[int, bool],
    right: dict[int, bool],
) -> dict[int, bool]:
    combined = dict(left)
    for variable, value in right.items():
        if variable in combined and combined[variable] != value:
            raise AssertionError("assignment clash")
        combined[variable] = value
    return combined


def evaluate_cnf(cnf: CNF, assignment_mask: int) -> bool:
    return all(
        any(
            bool(assignment_mask & (1 << (abs(literal) - 1))) == (literal > 0)
            for literal in clause
        )
        for clause in cnf
    )


def evaluate_affine(
    affine: tuple[Equation, ...],
    assignment_mask: int,
) -> bool:
    return all(
        ((mask & assignment_mask).bit_count() & 1) == rhs
        for mask, rhs in affine
    )


def lift_coordinate_assignment(
    coordinate_assignment: dict[int, bool],
    basis: dict[str, Any],
) -> int:
    packed = sum(
        1 << (variable - 1)
        for variable, value in coordinate_assignment.items()
        if value
    )
    assignment_mask = 0
    for variable, (mask, constant) in enumerate(
        basis["coordinate_forms"],
        1,
    ):
        value = int(constant) ^ ((int(mask) & packed).bit_count() & 1)
        if value:
            assignment_mask |= 1 << (variable - 1)
    return assignment_mask


def fixed_point_certificate(
    body: dict[str, Any],
    capability: Capability,
    meter: Meter,
) -> dict[str, Any]:
    charged = 0
    stated = 0
    for _ in range(20):
        body["producer_ledger"] = meter.snapshot()
        body["certificate_bytes"] = stated
        probe = dict(body)
        probe["integrity_sha256"] = "0" * 64
        size = len(canonical_json(probe).encode())
        if size > capability.certificate_limit:
            raise OpenResult(
                OPEN_CERTIFICATE_VOLUME,
                "certificate_bytes",
                {
                    "attempted_certificate_bytes": size,
                    "certificate_limit": capability.certificate_limit,
                    "semantic_payload_sha256": digest(body),
                },
            )
        if size > charged:
            meter.charge("certificate_bytes", size - charged)
            charged = size
        if size == stated:
            break
        stated = size
    body["producer_ledger"] = meter.snapshot()
    body["certificate_bytes"] = stated
    body["integrity_sha256"] = digest(body)
    return body
