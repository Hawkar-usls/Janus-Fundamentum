#!/usr/bin/env python3
from __future__ import annotations

from itertools import product
from typing import Any

from janus_c044_local_signed_support_core import (
    CNF,
    Equation,
    Factor,
    Capability,
    Meter,
    OpenResult,
    SCHEMA,
    OPEN_LOCAL_SUPPORT,
    OPEN_CERTIFICATE_VOLUME,
    canonical_input,
    canonical_json,
    combine_assignments,
    compile_signed_union,
    count_signed_union,
    digest,
    encoded_length,
    evaluate_affine,
    evaluate_cnf,
    find_separator,
    fixed_point_certificate,
    intersection,
    lift_coordinate_assignment,
    local_condition,
    normalize_cnf,
    parameterize_affine,
    parse_coefficients,
    parse_system,
    satisfies_space,
    system_dimension,
    system_payload,
    translate_factors,
    variables_in_affine,
    variables_in_cnf,
)


def parse_factors(payload: list[dict[str, Any]]) -> list[Factor]:
    factors: list[Factor] = []
    for item in payload:
        factors.append(
            Factor(
                int(item["factor_id"]),
                tuple(int(literal) for literal in item["clause"]),
                parse_system(item["space"]),
                tuple(int(variable) for variable in item["scope"]),
            )
        )
    return factors


def factors_payload(factors: list[Factor]) -> list[dict[str, Any]]:
    return [
        {
            "factor_id": factor.factor_id,
            "clause": list(factor.clause),
            "space": system_payload(factor.space),
            "scope": list(factor.scope),
        }
        for factor in factors
    ]


def replay_plan(
    supplied: dict[str, Any],
    factors: list[Factor],
    active: set[int],
    boundary: set[int],
    capability: Capability,
    meter: Meter,
) -> dict[str, Any]:
    meter.plan_nodes += 1
    meter.charge("plan_node")
    scope = tuple(
        sorted(
            set().union(*(set(factor.scope) for factor in factors))
            if factors
            else set()
        )
    )

    try:
        leaf = compile_signed_union(
            factors,
            scope,
            meter,
            accepted_leaf=True,
        )
        expected = {
            "node_type": "SIGNED_LEAF",
            "active": sorted(active),
            "boundary": sorted(boundary),
            "factor_ids": [factor.factor_id for factor in factors],
            "leaf": leaf,
        }
        if supplied != expected:
            raise ValueError("leaf plan mismatch")
        return expected
    except OpenResult as error:
        if error.status != OPEN_LOCAL_SUPPORT:
            raise
        local_overflow = {
            "status": error.status,
            "stage": error.stage,
            "evidence": error.evidence,
        }

    separator_data = find_separator(
        factors,
        active,
        capability.separator_limit,
        meter,
    )
    if separator_data is None:
        raise OpenResult(
            OPEN_LOCAL_SUPPORT,
            "no_admitted_separator",
            {
                "active": sorted(active),
                "boundary": sorted(boundary),
                "factor_ids": [factor.factor_id for factor in factors],
                "local_overflow": local_overflow,
                "separator_limit": capability.separator_limit,
            },
        )

    separator = set(separator_data["separator"])
    children: list[dict[str, Any]] = []
    descriptors: list[dict[str, Any]] = []
    supplied_children = supplied.get("children")
    if not isinstance(supplied_children, list):
        raise ValueError("missing supplied children")

    child_cursor = 0
    for component, bucket in zip(
        separator_data["components"],
        separator_data["buckets"],
    ):
        if not bucket:
            continue
        if child_cursor >= len(supplied_children):
            raise ValueError("missing child plan")
        child_scope = set().union(*(set(factor.scope) for factor in bucket))
        child_boundary = (boundary | separator) & child_scope
        child = replay_plan(
            supplied_children[child_cursor],
            bucket,
            set(component),
            set(child_boundary),
            capability,
            meter,
        )
        children.append(child)
        descriptors.append(
            {
                "child_index": child_cursor,
                "component": sorted(component),
                "factor_ids": [factor.factor_id for factor in bucket],
                "boundary": sorted(child_boundary),
            }
        )
        child_cursor += 1
    if child_cursor != len(supplied_children):
        raise ValueError("extra child plan")

    expected = {
        "node_type": "SEPARATOR",
        "active": sorted(active),
        "boundary": sorted(boundary),
        "separator": list(separator_data["separator"]),
        "separator_kind": separator_data["kind"],
        "separator_candidates_tested": separator_data["candidates_tested"],
        "local_overflow": local_overflow,
        "local_factor_ids": [
            factor.factor_id for factor in separator_data["local"]
        ],
        "child_descriptors": descriptors,
        "children": children,
    }
    if supplied != expected:
        raise ValueError("separator plan mismatch")
    return expected


def replay_leaf_result(
    leaf: dict[str, Any],
    incoming: dict[int, bool],
    supplied: dict[str, Any],
    meter: Meter,
) -> dict[str, Any]:
    meter.result_nodes += 1
    meter.charge("leaf_result")
    scope = tuple(int(variable) for variable in leaf["scope"])
    terms = parse_coefficients(leaf["terms"])
    dimension = len(scope)
    condition = local_condition(incoming, scope)
    fixed = sum(variable in incoming for variable in scope)
    total_points = 1 << (dimension - fixed)
    covered_points, root_trace = count_signed_union(
        terms,
        condition,
        dimension,
        meter,
    )
    if covered_points == total_points:
        expected = {
            "node_type": "SIGNED_LEAF",
            "status": "UNSAT",
            "reason": "LEAF_FULL_COVER",
            "condition": system_payload(condition),
            "covered_points": str(covered_points),
            "total_points": str(total_points),
            "root_count_trace": root_trace,
            "factor_ids": supplied.get("factor_ids"),
        }
        if supplied != expected:
            raise ValueError("leaf UNSAT result mismatch")
        return expected

    if not 0 <= covered_points < total_points:
        raise ValueError("invalid leaf signed count")

    assignment = dict(incoming)
    prefix = condition
    witness_trace: list[dict[str, Any]] = []
    local_index = {
        variable: index + 1 for index, variable in enumerate(scope)
    }
    for variable in scope:
        if variable in assignment:
            continue
        branches: list[dict[str, Any]] = []
        chosen_bit: int | None = None
        chosen_cell = None
        variable_mask = 1 << (local_index[variable] - 1)
        for bit in (0, 1):
            cell = intersection(
                prefix,
                ((variable_mask, bit),),
                dimension,
                meter,
            )
            if cell is None:
                raise ValueError("inconsistent leaf branch")
            covered, count_trace = count_signed_union(
                terms,
                cell,
                dimension,
                meter,
            )
            cell_points = 1 << system_dimension(cell, dimension)
            branches.append(
                {
                    "bit": bit,
                    "cell": system_payload(cell),
                    "covered_points": str(covered),
                    "cell_points": str(cell_points),
                    "count_trace": count_trace,
                }
            )
            if chosen_bit is None and covered < cell_points:
                chosen_bit = bit
                chosen_cell = cell
        if chosen_bit is None or chosen_cell is None:
            raise ValueError("no uncovered leaf child")
        assignment[variable] = bool(chosen_bit)
        prefix = chosen_cell
        witness_trace.append(
            {
                "variable": variable,
                "chosen_bit": chosen_bit,
                "branches": branches,
            }
        )

    expected = {
        "node_type": "SIGNED_LEAF",
        "status": "SAT",
        "reason": "LEAF_UNCOVERED_EXTENSION",
        "condition": system_payload(condition),
        "covered_points": str(covered_points),
        "total_points": str(total_points),
        "root_count_trace": root_trace,
        "assignment": {
            str(variable): bool(value)
            for variable, value in sorted(assignment.items())
        },
        "witness_trace": witness_trace,
        "factor_ids": supplied.get("factor_ids"),
    }
    if supplied != expected:
        raise ValueError("leaf SAT result mismatch")
    return expected


def replay_plan_result(
    plan: dict[str, Any],
    factors_by_id: dict[int, Factor],
    incoming: dict[int, bool],
    supplied: dict[str, Any],
    meter: Meter,
) -> dict[str, Any]:
    if plan["node_type"] == "SIGNED_LEAF":
        if supplied.get("factor_ids") != plan["factor_ids"]:
            raise ValueError("leaf factor IDs mismatch")
        return replay_leaf_result(plan["leaf"], incoming, supplied, meter)

    meter.result_nodes += 1
    meter.charge("separator_result")
    separator = [int(variable) for variable in plan["separator"]]
    rejected: list[dict[str, Any]] = []
    for bits in product((0, 1), repeat=len(separator)):
        assignment = dict(incoming)
        assignment.update(
            {
                variable: bool(bit)
                for variable, bit in zip(separator, bits)
            }
        )

        local_blocker: dict[str, Any] | None = None
        for factor_id in plan["local_factor_ids"]:
            factor = factors_by_id[int(factor_id)]
            meter.charge("local_factor_check")
            if satisfies_space(factor.space, assignment):
                local_blocker = {
                    "blocker_type": "LOCAL_FORBIDDEN_FACTOR",
                    "factor_id": int(factor_id),
                }
                break
        if local_blocker is not None:
            rejected.append(
                {
                    "separator_bits": list(bits),
                    "status": "UNSAT",
                    "blocker": local_blocker,
                }
            )
            continue

        combined = dict(assignment)
        child_results: list[dict[str, Any]] = []
        branch_blocker: dict[str, Any] | None = None

        supplied_child_records: list[dict[str, Any]]
        if supplied.get("status") == "SAT":
            chosen_bits = supplied.get("chosen_separator_bits")
            if list(bits) == chosen_bits:
                supplied_child_records = supplied.get("child_results", [])
            else:
                prior = supplied.get("rejected_prior_branches", [])
                index = len(rejected)
                if index >= len(prior):
                    raise ValueError("missing rejected prior branch")
                branch_payload = prior[index]
                if branch_payload.get("separator_bits") != list(bits):
                    raise ValueError("prior branch order mismatch")
                supplied_child_records = branch_payload.get("child_results", [])
        else:
            branches = supplied.get("branches", [])
            index = len(rejected)
            if index >= len(branches):
                raise ValueError("missing UNSAT branch")
            branch_payload = branches[index]
            if branch_payload.get("separator_bits") != list(bits):
                raise ValueError("UNSAT branch order mismatch")
            supplied_child_records = branch_payload.get("child_results", [])

        for child_index, child in enumerate(plan["children"]):
            if child_index >= len(supplied_child_records):
                raise ValueError("missing child result")
            child_incoming = {
                int(variable): combined[int(variable)]
                for variable in child["boundary"]
            }
            child_result = replay_plan_result(
                child,
                factors_by_id,
                child_incoming,
                supplied_child_records[child_index],
                meter,
            )
            child_results.append(child_result)
            if child_result["status"] == "UNSAT":
                branch_blocker = {
                    "blocker_type": "CHILD_UNSAT",
                    "child_index": child_index,
                }
                break
            child_assignment = {
                int(variable): bool(value)
                for variable, value in child_result["assignment"].items()
            }
            combined = combine_assignments(combined, child_assignment)

        if branch_blocker is None:
            expected = {
                "node_type": "SEPARATOR",
                "status": "SAT",
                "separator": separator,
                "chosen_separator_bits": list(bits),
                "assignment": {
                    str(variable): bool(value)
                    for variable, value in sorted(combined.items())
                },
                "child_results": child_results,
                "rejected_prior_branches": rejected,
            }
            if supplied != expected:
                raise ValueError("separator SAT result mismatch")
            return expected

        rejected.append(
            {
                "separator_bits": list(bits),
                "status": "UNSAT",
                "blocker": branch_blocker,
                "child_results": child_results,
            }
        )

    expected = {
        "node_type": "SEPARATOR",
        "status": "UNSAT",
        "separator": separator,
        "branches": rejected,
    }
    if supplied != expected:
        raise ValueError("separator UNSAT result mismatch")
    return expected
