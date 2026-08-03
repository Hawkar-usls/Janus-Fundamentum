#!/usr/bin/env python3
from __future__ import annotations

from typing import Any

from janus_c042_affine_core import (
    assignment_dict,
    canonical_factor_system,
    canonical_input,
    digest,
    encoded_length,
    evaluate_cnf,
    evaluate_equations,
    lift_coordinate_mask,
    normalize_cnf,
    parameterize_affine,
    solve_system,
    translate_clause,
    variables_in_affine,
    variables_in_cnf,
    intersection,
    system_dimension,
)
from janus_c043_crossing_core import (
    CNF,
    Equation,
    Capability,
    Coefficients,
    CrossingMeter,
    CrossingOpen,
    SCHEMA,
    coefficient_payload,
    compact_open_certificate,
    count_signed,
    finalize_or_raise,
    prefix_cell,
    system_key,
    system_payload,
)


def deterministic_factors(raw_factors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    nonempty = [factor for factor in raw_factors if not factor["empty"]]
    return sorted(
        nonempty,
        key=lambda factor: (-len(canonical_factor_system(factor)), canonical_factor_system(factor), int(factor["clause_id"])),
    )


def build_transition(
    coefficients: Coefficients,
    factor: tuple[Equation, ...],
    factor_index: int,
    clause_id: int,
    dimension: int,
    meter: CrossingMeter,
) -> tuple[Coefficients, dict[str, Any]]:
    before = dict(coefficients)
    delta: Coefficients = {factor: 1}
    operations: list[dict[str, Any]] = []
    for space, coefficient in sorted(before.items(), key=lambda item: system_key(item[0])):
        meter.charge("signed_transition_terms")
        overlap = intersection(space, factor, dimension, meter)
        contribution = 0 if overlap is None else -coefficient
        operations.append(
            {
                "source_space": system_payload(space),
                "source_coefficient": coefficient,
                "intersection": system_payload(overlap),
                "delta_coefficient": contribution,
            }
        )
        if overlap is not None:
            delta[overlap] = delta.get(overlap, 0) + contribution
            meter.charge("coefficient_addition_bits", max(1, abs(contribution).bit_length()))
            if delta[overlap] == 0:
                del delta[overlap]
    updated = dict(before)
    merges: list[dict[str, Any]] = []
    for space, contribution in sorted(delta.items(), key=lambda item: system_key(item[0])):
        meter.charge("signed_delta_merges")
        old = updated.get(space, 0)
        new = old + contribution
        meter.charge(
            "coefficient_addition_bits",
            max(1, abs(old).bit_length(), abs(contribution).bit_length(), abs(new).bit_length()),
        )
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
    working_support = len(before) + len(delta)
    meter.check_support(len(updated), factor_index + 1, working_support)
    bit_volume = meter.check_coefficient_volume(updated, factor_index + 1)
    transition = {
        "step": factor_index + 1,
        "factor_index": factor_index,
        "clause_id": clause_id,
        "factor": system_payload(factor),
        "before_support": len(before),
        "delta_support": len(delta),
        "working_support": working_support,
        "intersection_operations": operations,
        "merge_operations": merges,
        "after_terms": coefficient_payload(updated, dimension),
        "live_support": len(updated),
        "coefficient_bit_volume": bit_volume,
    }
    return updated, transition


def solve_crossing(
    cnf: CNF,
    affine: tuple[Equation, ...] = (),
    *,
    nvars_hint: int = 0,
    support_cap: int | None = None,
    work_cap: int | None = None,
    certificate_cap: int | None = None,
    coefficient_bit_cap: int | None = None,
) -> dict[str, Any]:
    cnf = normalize_cnf(cnf)
    nvars = max(nvars_hint, max(variables_in_cnf(cnf) | variables_in_affine(affine), default=0))
    input_object = canonical_input(cnf, affine, nvars)
    input_digest = digest(input_object)
    capability = Capability(
        encoded_length(cnf, affine, nvars),
        support_cap,
        work_cap,
        certificate_cap,
        coefficient_bit_cap,
    )
    meter = CrossingMeter(capability)
    basis: dict[str, Any] | None = None
    raw_factors: list[dict[str, Any]] | None = None
    transitions: list[dict[str, Any]] = []
    try:
        basis = parameterize_affine(affine, nvars, meter)
        base = {
            "schema": SCHEMA,
            "input_digest": input_digest,
            "nvars": nvars,
            "capability": capability.manifest(),
            "basis_artifact": basis,
            "basis_digest": digest(basis),
            "p_vs_np": "OPEN",
        }
        if basis["status"] == "UNSAT":
            return finalize_or_raise(
                {
                    **base,
                    "status": "UNSAT",
                    "reason": "AFFINE_CONTRADICTION",
                },
                meter,
            )

        dimension = int(basis["dimension"])
        coordinate_forms = [
            (int(mask), int(constant)) for mask, constant in basis["coordinate_forms"]
        ]
        raw_factors = [
            translate_clause(clause_id, clause, coordinate_forms, dimension, meter)
            for clause_id, clause in enumerate(cnf)
        ]
        factors = deterministic_factors(raw_factors)
        factor_order = [
            {
                "factor_index": index,
                "clause_id": int(factor["clause_id"]),
                "space": system_payload(canonical_factor_system(factor)),
            }
            for index, factor in enumerate(factors)
        ]

        coefficients: Coefficients = {}
        meter.check_support(0, 0, 0)
        for index, factor in enumerate(factors):
            space = canonical_factor_system(factor)
            try:
                coefficients, transition = build_transition(
                    coefficients,
                    space,
                    index,
                    int(factor["clause_id"]),
                    dimension,
                    meter,
                )
            except CrossingOpen as error:
                error.evidence.setdefault("factor_index", index)
                error.evidence.setdefault("clause_id", int(factor["clause_id"]))
                error.evidence.setdefault("factor", system_payload(space))
                error.evidence.setdefault("before_terms", coefficient_payload(coefficients, dimension))
                raise
            transitions.append(transition)

        union_size, root_count_trace = count_signed(coefficients, (), dimension, meter)
        total_points = 1 << dimension
        meter.charge("big_integer_bits", max(1, total_points.bit_length(), abs(union_size).bit_length()))
        if not 0 <= union_size <= total_points:
            raise AssertionError("signed union count outside ambient space")
        common = {
            **base,
            "dimension": dimension,
            "raw_factors": raw_factors,
            "factor_order": factor_order,
            "signed_transitions": transitions,
            "final_terms": coefficient_payload(coefficients, dimension),
            "max_live_support": meter.max_support,
            "max_working_support": meter.max_working_support,
            "max_coefficient_bit_volume": meter.max_coefficient_bit_volume,
            "union_size": str(union_size),
            "total_points": str(total_points),
            "root_count_trace": root_count_trace,
        }
        if union_size == total_points:
            return finalize_or_raise(
                {
                    **common,
                    "status": "UNSAT",
                    "reason": "EXACT_SIGNED_INTERSECTION_COVER",
                },
                meter,
            )

        prefix: tuple[Equation, ...] = ()
        witness_trace: list[dict[str, Any]] = []
        for variable in range(1, dimension + 1):
            branches: list[dict[str, Any]] = []
            chosen_bit: int | None = None
            chosen_cell: tuple[Equation, ...] | None = None
            for bit in (0, 1):
                cell = prefix_cell(prefix, variable, bit, dimension, meter)
                covered, count_trace = count_signed(coefficients, cell, dimension, meter)
                cell_points = 1 << system_dimension(cell, dimension)
                meter.charge(
                    "big_integer_bits",
                    max(1, cell_points.bit_length(), abs(covered).bit_length()),
                )
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
                raise AssertionError("conditional signed counting found no uncovered child")
            witness_trace.append(
                {
                    "variable": variable,
                    "chosen_bit": chosen_bit,
                    "branches": branches,
                }
            )
            prefix = chosen_cell

        lambda_mask = solve_system(prefix, dimension, meter)
        if lambda_mask is None:
            raise AssertionError("complete coordinate prefix is inconsistent")
        witness_mask = lift_coordinate_mask(lambda_mask, basis, nvars)
        meter.charge("witness_recovery_bits", max(1, dimension + nvars))
        if not evaluate_equations(affine, witness_mask) or not evaluate_cnf(cnf, witness_mask):
            raise AssertionError("lifted witness failed original instance")
        for factor in factors:
            if evaluate_equations(canonical_factor_system(factor), lambda_mask):
                raise AssertionError("coordinate witness remains inside a forbidden factor")
        return finalize_or_raise(
            {
                **common,
                "status": "SAT",
                "reason": "POINT_OUTSIDE_SIGNED_UNION",
                "witness_trace": witness_trace,
                "lambda_witness_mask": str(lambda_mask),
                "lambda_witness": assignment_dict(lambda_mask, dimension),
                "witness_mask": str(witness_mask),
                "witness": assignment_dict(witness_mask, nvars),
            },
            meter,
        )
    except CrossingOpen as error:
        include_trace = error.status != "OPEN_CERTIFICATE_VOLUME"
        return compact_open_certificate(
            input_digest=input_digest,
            nvars=nvars,
            capability=capability,
            meter=meter,
            status=error.status,
            stage=error.stage,
            evidence=error.evidence,
            basis_artifact=basis,
            raw_factors=raw_factors if include_trace else None,
            transitions=transitions if include_trace else None,
        )
