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
    OPEN_WORK_BUDGET,
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
    factor_scope,
    find_separator,
    fixed_point_certificate,
    graph_components,
    intersection,
    lift_coordinate_assignment,
    local_condition,
    normalize_cnf,
    parameterize_affine,
    parse_coefficients,
    parse_system,
    partition_factors,
    satisfies_space,
    system_dimension,
    system_payload,
    translate_factors,
    variables_in_affine,
    variables_in_cnf,
)


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


def build_plan(
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
        return {
            "node_type": "SIGNED_LEAF",
            "active": sorted(active),
            "boundary": sorted(boundary),
            "factor_ids": [factor.factor_id for factor in factors],
            "leaf": leaf,
        }
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
    child_descriptors: list[dict[str, Any]] = []
    for component, bucket in zip(
        separator_data["components"],
        separator_data["buckets"],
    ):
        if not bucket:
            continue
        child_scope = set().union(*(set(factor.scope) for factor in bucket))
        child_boundary = (boundary | separator) & child_scope
        child = build_plan(
            bucket,
            set(component),
            set(child_boundary),
            capability,
            meter,
        )
        child_index = len(children)
        children.append(child)
        child_descriptors.append(
            {
                "child_index": child_index,
                "component": sorted(component),
                "factor_ids": [factor.factor_id for factor in bucket],
                "boundary": sorted(child_boundary),
            }
        )

    return {
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
        "child_descriptors": child_descriptors,
        "children": children,
    }


def solve_leaf(
    leaf: dict[str, Any],
    incoming: dict[int, bool],
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
        return {
            "node_type": "SIGNED_LEAF",
            "status": "UNSAT",
            "reason": "LEAF_FULL_COVER",
            "condition": system_payload(condition),
            "covered_points": str(covered_points),
            "total_points": str(total_points),
            "root_count_trace": root_trace,
        }
    if not 0 <= covered_points < total_points:
        raise AssertionError("leaf signed count outside its boundary cell")

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
        bit_mask = 1 << (local_index[variable] - 1)
        for bit in (0, 1):
            cell = intersection(
                prefix,
                ((bit_mask, bit),),
                dimension,
                meter,
            )
            if cell is None:
                raise AssertionError("leaf branch cell became inconsistent")
            covered, count_trace = count_signed_union(
                terms,
                cell,
                dimension,
                meter,
            )
            cell_points = 1 << system_dimension(cell, dimension)
            branch = {
                "bit": bit,
                "cell": system_payload(cell),
                "covered_points": str(covered),
                "cell_points": str(cell_points),
                "count_trace": count_trace,
            }
            branches.append(branch)
            if chosen_bit is None and covered < cell_points:
                chosen_bit = bit
                chosen_cell = cell
        if chosen_bit is None or chosen_cell is None:
            raise AssertionError("leaf witness recovery found no uncovered child")
        assignment[variable] = bool(chosen_bit)
        prefix = chosen_cell
        witness_trace.append(
            {
                "variable": variable,
                "chosen_bit": chosen_bit,
                "branches": branches,
            }
        )

    for space in terms:
        local_assignment = {
            index + 1: assignment[variable]
            for index, variable in enumerate(scope)
        }
        if satisfies_space(space, local_assignment):
            pass

    return {
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
    }


def solve_plan(
    plan: dict[str, Any],
    factors_by_id: dict[int, Factor],
    incoming: dict[int, bool],
    meter: Meter,
) -> dict[str, Any]:
    if plan["node_type"] == "SIGNED_LEAF":
        result = solve_leaf(plan["leaf"], incoming, meter)
        result["factor_ids"] = list(plan["factor_ids"])
        return result

    meter.result_nodes += 1
    meter.charge("separator_result")
    separator = [int(variable) for variable in plan["separator"]]
    rejected_branches: list[dict[str, Any]] = []
    for bits in product((0, 1), repeat=len(separator)):
        branch_assignment = dict(incoming)
        branch_assignment.update(
            {
                variable: bool(bit)
                for variable, bit in zip(separator, bits)
            }
        )

        local_blocker: dict[str, Any] | None = None
        for factor_id in plan["local_factor_ids"]:
            factor = factors_by_id[int(factor_id)]
            meter.charge("local_factor_check")
            if satisfies_space(factor.space, branch_assignment):
                local_blocker = {
                    "blocker_type": "LOCAL_FORBIDDEN_FACTOR",
                    "factor_id": int(factor_id),
                }
                break
        if local_blocker is not None:
            rejected_branches.append(
                {
                    "separator_bits": list(bits),
                    "status": "UNSAT",
                    "blocker": local_blocker,
                }
            )
            continue

        combined = dict(branch_assignment)
        child_records: list[dict[str, Any]] = []
        branch_blocker: dict[str, Any] | None = None
        for child_index, child in enumerate(plan["children"]):
            child_incoming = {
                int(variable): combined[int(variable)]
                for variable in child["boundary"]
            }
            child_result = solve_plan(
                child,
                factors_by_id,
                child_incoming,
                meter,
            )
            child_records.append(child_result)
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
            return {
                "node_type": "SEPARATOR",
                "status": "SAT",
                "separator": separator,
                "chosen_separator_bits": list(bits),
                "assignment": {
                    str(variable): bool(value)
                    for variable, value in sorted(combined.items())
                },
                "child_results": child_records,
                "rejected_prior_branches": rejected_branches,
            }

        rejected_branches.append(
            {
                "separator_bits": list(bits),
                "status": "UNSAT",
                "blocker": branch_blocker,
                "child_results": child_records,
            }
        )

    return {
        "node_type": "SEPARATOR",
        "status": "UNSAT",
        "separator": separator,
        "branches": rejected_branches,
    }


def compact_open(
    *,
    base: dict[str, Any],
    capability: Capability,
    meter: Meter,
    error: OpenResult,
    basis: dict[str, Any] | None,
    raw_factors: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    body = {
        **base,
        "status": error.status,
        "reason": error.stage,
        "overflow_evidence": error.evidence,
        "capability": capability.manifest(),
        "producer_ledger": meter.snapshot(),
        "p_vs_np": "OPEN",
    }
    if basis is not None:
        body["basis_artifact"] = basis
        body["basis_digest"] = digest(basis)
    if raw_factors is not None and error.status != OPEN_CERTIFICATE_VOLUME:
        body["raw_factors"] = raw_factors
    body["integrity_sha256"] = digest(body)
    return body


def solve_local_signed_support(
    cnf: CNF,
    affine: tuple[Equation, ...] = (),
    *,
    nvars_hint: int = 0,
    separator_cap: int = 1,
    local_support_cap: int | None = None,
    work_cap: int | None = None,
    certificate_cap: int | None = None,
) -> dict[str, Any]:
    cnf = normalize_cnf(cnf)
    nvars = max(
        nvars_hint,
        max(
            variables_in_cnf(cnf) | variables_in_affine(affine),
            default=0,
        ),
    )
    input_object = canonical_input(cnf, affine, nvars)
    input_digest = digest(input_object)
    capability = Capability(
        encoded_length(cnf, affine, nvars),
        separator_cap,
        local_support_cap,
        work_cap,
        certificate_cap,
    )
    meter = Meter(capability)
    base = {
        "schema": SCHEMA,
        "input_digest": input_digest,
        "nvars": nvars,
        "p_vs_np": "OPEN",
    }
    basis: dict[str, Any] | None = None
    raw_factors: list[dict[str, Any]] | None = None

    try:
        basis = parameterize_affine(affine, nvars, meter)
        if basis["status"] == "UNSAT":
            return fixed_point_certificate(
                {
                    **base,
                    "status": "UNSAT",
                    "reason": "AFFINE_CONTRADICTION",
                    "capability": capability.manifest(),
                    "basis_artifact": basis,
                    "basis_digest": digest(basis),
                },
                capability,
                meter,
            )

        factors, raw_factors = translate_factors(cnf, basis, meter)
        active = (
            set().union(*(set(factor.scope) for factor in factors))
            if factors
            else set()
        )
        plan = build_plan(
            factors,
            set(active),
            set(),
            capability,
            meter,
        )
        factors_by_id = {factor.factor_id: factor for factor in factors}
        result = solve_plan(plan, factors_by_id, {}, meter)
        body: dict[str, Any] = {
            **base,
            "status": result["status"],
            "reason": (
                "LOCAL_SIGNED_SUPPORT_VTREE_SAT"
                if result["status"] == "SAT"
                else "LOCAL_SIGNED_SUPPORT_VTREE_UNSAT"
            ),
            "capability": capability.manifest(),
            "basis_artifact": basis,
            "basis_digest": digest(basis),
            "dimension": int(basis["dimension"]),
            "raw_factors": raw_factors,
            "factors": factors_payload(factors),
            "plan": plan,
            "plan_digest": digest(plan),
            "result": result,
        }
        if result["status"] == "SAT":
            coordinate_assignment = {
                int(variable): bool(value)
                for variable, value in result["assignment"].items()
            }
            witness_mask = lift_coordinate_assignment(
                coordinate_assignment,
                basis,
            )
            meter.charge("witness_lift", max(1, nvars + int(basis["dimension"])))
            if not evaluate_affine(affine, witness_mask):
                raise AssertionError("lifted witness violates affine equations")
            if not evaluate_cnf(cnf, witness_mask):
                raise AssertionError("lifted witness violates CNF")
            body["lambda_witness"] = result["assignment"]
            body["witness_mask"] = str(witness_mask)
            body["witness"] = {
                str(variable): bool(witness_mask & (1 << (variable - 1)))
                for variable in range(1, nvars + 1)
            }
        return fixed_point_certificate(body, capability, meter)
    except OpenResult as error:
        return compact_open(
            base=base,
            capability=capability,
            meter=meter,
            error=error,
            basis=basis,
            raw_factors=raw_factors,
        )
