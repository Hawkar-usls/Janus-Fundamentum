#!/usr/bin/env python3
from __future__ import annotations
from janus_c044_local_signed_support_verifier_a import *

def construct_plan_independent(
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
    descriptors: list[dict[str, Any]] = []
    for component, bucket in zip(
        separator_data["components"],
        separator_data["buckets"],
    ):
        if not bucket:
            continue
        child_scope = set().union(*(set(factor.scope) for factor in bucket))
        child_boundary = (boundary | separator) & child_scope
        child = construct_plan_independent(
            bucket,
            set(component),
            set(child_boundary),
            capability,
            meter,
        )
        child_index = len(children)
        children.append(child)
        descriptors.append(
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
        "child_descriptors": descriptors,
        "children": children,
    }


def construct_leaf_result_independent(
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
        raise AssertionError("leaf signed count outside cell")

    assignment = dict(incoming)
    prefix = condition
    witness_trace: list[dict[str, Any]] = []
    local_index = {
        variable: index + 1 for index, variable in enumerate(scope)
    }
    for variable in scope:
        if variable in assignment:
            continue
        variable_mask = 1 << (local_index[variable] - 1)
        branches: list[dict[str, Any]] = []
        chosen_bit = None
        chosen_cell = None
        for bit in (0, 1):
            cell = intersection(
                prefix,
                ((variable_mask, bit),),
                dimension,
                meter,
            )
            if cell is None:
                raise AssertionError("inconsistent leaf cell")
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
            raise AssertionError("no uncovered leaf branch")
        assignment[variable] = bool(chosen_bit)
        prefix = chosen_cell
        witness_trace.append(
            {
                "variable": variable,
                "chosen_bit": chosen_bit,
                "branches": branches,
            }
        )
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


def construct_result_independent(
    plan: dict[str, Any],
    factors_by_id: dict[int, Factor],
    incoming: dict[int, bool],
    meter: Meter,
) -> dict[str, Any]:
    if plan["node_type"] == "SIGNED_LEAF":
        result = construct_leaf_result_independent(
            plan["leaf"],
            incoming,
            meter,
        )
        result["factor_ids"] = list(plan["factor_ids"])
        return result

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
        blocker = None
        for factor_id in plan["local_factor_ids"]:
            factor = factors_by_id[int(factor_id)]
            meter.charge("local_factor_check")
            if satisfies_space(factor.space, assignment):
                blocker = {
                    "blocker_type": "LOCAL_FORBIDDEN_FACTOR",
                    "factor_id": int(factor_id),
                }
                break
        if blocker is not None:
            rejected.append(
                {
                    "separator_bits": list(bits),
                    "status": "UNSAT",
                    "blocker": blocker,
                }
            )
            continue

        combined = dict(assignment)
        child_results: list[dict[str, Any]] = []
        branch_blocker = None
        for child_index, child in enumerate(plan["children"]):
            child_incoming = {
                int(variable): combined[int(variable)]
                for variable in child["boundary"]
            }
            child_result = construct_result_independent(
                child,
                factors_by_id,
                child_incoming,
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
            return {
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

        rejected.append(
            {
                "separator_bits": list(bits),
                "status": "UNSAT",
                "blocker": branch_blocker,
                "child_results": child_results,
            }
        )
    return {
        "node_type": "SEPARATOR",
        "status": "UNSAT",
        "separator": separator,
        "branches": rejected,
    }


def construct_terminal_independent(
    cnf: CNF,
    affine: tuple[Equation, ...],
    nvars: int,
    capability: Capability,
) -> dict[str, Any]:
    meter = Meter(capability)
    input_object = canonical_input(cnf, affine, nvars)
    base = {
        "schema": SCHEMA,
        "input_digest": digest(input_object),
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
        plan = construct_plan_independent(
            factors,
            set(active),
            set(),
            capability,
            meter,
        )
        factors_by_id = {factor.factor_id: factor for factor in factors}
        result = construct_result_independent(plan, factors_by_id, {}, meter)
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
                raise AssertionError("independent witness violates affine")
            if not evaluate_cnf(cnf, witness_mask):
                raise AssertionError("independent witness violates CNF")
            body["lambda_witness"] = result["assignment"]
            body["witness_mask"] = str(witness_mask)
            body["witness"] = {
                str(variable): bool(witness_mask & (1 << (variable - 1)))
                for variable in range(1, nvars + 1)
            }
        return fixed_point_certificate(body, capability, meter)
    except OpenResult as error:
        compact = {
            **base,
            "status": error.status,
            "reason": error.stage,
            "overflow_evidence": error.evidence,
            "capability": capability.manifest(),
            "producer_ledger": meter.snapshot(),
            "p_vs_np": "OPEN",
        }
        if basis is not None:
            compact["basis_artifact"] = basis
            compact["basis_digest"] = digest(basis)
        if raw_factors is not None and error.status != OPEN_CERTIFICATE_VOLUME:
            compact["raw_factors"] = raw_factors
        compact["integrity_sha256"] = digest(compact)
        return compact


def verify_local_signed_support(
    cnf: CNF,
    affine: tuple[Equation, ...],
    certificate: dict[str, Any],
    *,
    nvars_hint: int = 0,
) -> bool:
    try:
        if certificate.get("schema") != SCHEMA:
            return False
        integrity = certificate.get("integrity_sha256")
        if not isinstance(integrity, str):
            return False
        body = dict(certificate)
        body.pop("integrity_sha256", None)
        if digest(body) != integrity:
            return False

        cnf = normalize_cnf(cnf)
        nvars = max(
            nvars_hint,
            max(
                variables_in_cnf(cnf) | variables_in_affine(affine),
                default=0,
            ),
        )
        input_object = canonical_input(cnf, affine, nvars)
        if certificate.get("input_digest") != digest(input_object):
            return False
        if int(certificate.get("nvars", -1)) != nvars:
            return False

        capability = Capability.from_manifest(certificate["capability"])
        if capability.input_length != encoded_length(cnf, affine, nvars):
            return False

        expected = construct_terminal_independent(
            cnf,
            affine,
            nvars,
            capability,
        )
        return expected == certificate
    except (KeyError, TypeError, ValueError, AssertionError, OpenResult):
        return False
