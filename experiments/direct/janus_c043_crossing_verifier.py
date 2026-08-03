#!/usr/bin/env python3
from __future__ import annotations

from typing import Any

from janus_c042_affine_core import (
    assignment_dict,
    canonical_factor_system,
    canonical_input,
    canonical_json,
    digest,
    encoded_length,
    evaluate_cnf,
    evaluate_equations,
    lift_coordinate_mask,
    normalize_cnf,
    rref_system,
    translate_clause,
    variables_in_affine,
    variables_in_cnf,
    xor_provenance,
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
    OPEN_CERTIFICATE_VOLUME,
    OPEN_INTERSECTION_CLOSURE,
    OPEN_WORK_BUDGET,
    SCHEMA,
    coefficient_bit_volume,
    coefficient_payload,
    count_signed,
    prefix_cell,
    system_key,
    system_payload,
)


def verify_basis_artifact(
    affine: tuple[Equation, ...],
    nvars: int,
    artifact: dict[str, Any],
    meter: CrossingMeter,
) -> bool:
    if artifact.get("status") == "UNSAT":
        provenance = int(artifact.get("conflict_provenance", "0"))
        return xor_provenance(affine, provenance) == (0, 1) and rref_system(affine, nvars, meter) is None
    if artifact.get("status") != "SAT":
        return False
    rows = artifact.get("rref")
    if not isinstance(rows, list):
        return False
    canonical = rref_system(affine, nvars, meter)
    if canonical is None:
        return False
    stated = tuple((int(row[0]), int(row[1])) for row in rows)
    if stated != canonical:
        return False
    for mask, rhs, provenance_text in rows:
        meter.charge("verifier_basis_provenance")
        if xor_provenance(affine, int(provenance_text)) != (int(mask), int(rhs)):
            return False
    pivots = {(mask & -mask).bit_length() for mask, _ in canonical}
    free = [int(variable) for variable in artifact.get("free_variables", [])]
    if free != [variable for variable in range(1, nvars + 1) if variable not in pivots]:
        return False
    particular = int(artifact.get("particular_mask", "-1"))
    basis = [int(vector) for vector in artifact.get("basis_masks", [])]
    if int(artifact.get("dimension", -1)) != len(free) or len(basis) != len(free):
        return False
    if not evaluate_equations(affine, particular):
        return False
    homogeneous = tuple((mask, 0) for mask, _ in affine)
    for index, vector in enumerate(basis):
        meter.charge("verifier_basis_vectors", max(1, nvars))
        if not evaluate_equations(homogeneous, vector):
            return False
        for free_index, variable in enumerate(free):
            if bool(vector & (1 << (variable - 1))) != (index == free_index):
                return False
    expected_forms: list[list[int]] = []
    for variable in range(1, nvars + 1):
        coordinate_mask = 0
        for index, vector in enumerate(basis):
            meter.charge("verifier_coordinate_forms")
            if vector & (1 << (variable - 1)):
                coordinate_mask |= 1 << index
        expected_forms.append(
            [coordinate_mask, int(bool(particular & (1 << (variable - 1))))]
        )
    return artifact.get("coordinate_forms") == expected_forms


def deterministic_factors(raw_factors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        [factor for factor in raw_factors if not factor["empty"]],
        key=lambda factor: (-len(canonical_factor_system(factor)), canonical_factor_system(factor), int(factor["clause_id"])),
    )


def verify_producer_ledger(certificate: dict[str, Any], capability: Capability) -> bool:
    ledger = certificate.get("producer_ledger")
    if not isinstance(ledger, dict):
        return False
    counters = ledger.get("counters")
    if not isinstance(counters, dict):
        return False
    if any(not isinstance(value, int) or value < 0 for value in counters.values()):
        return False
    total = int(ledger.get("total_work_units", -1))
    if total != sum(counters.values()):
        return False
    if int(ledger.get("max_support", -1)) < 0:
        return False
    if int(ledger.get("max_working_support", -1)) < int(ledger.get("max_support", -1)):
        return False
    if int(ledger.get("max_coefficient_bit_volume", -1)) < 0:
        return False
    status = certificate.get("status")
    if status == OPEN_WORK_BUDGET:
        evidence = certificate.get("overflow_evidence", {})
        return (
            total > capability.work_limit
            or int(evidence.get("coefficient_bit_volume", 0)) > capability.coefficient_bit_limit
        )
    return total <= capability.work_limit


def replay_transition(
    coefficients: Coefficients,
    factor: tuple[Equation, ...],
    factor_index: int,
    clause_id: int,
    dimension: int,
    record: dict[str, Any],
    meter: CrossingMeter,
    *,
    enforce_support: bool = True,
) -> tuple[Coefficients, int, int]:
    if record.get("step") != factor_index + 1:
        raise ValueError("transition step mismatch")
    if record.get("factor_index") != factor_index or record.get("clause_id") != clause_id:
        raise ValueError("factor order mismatch")
    if record.get("factor") != system_payload(factor):
        raise ValueError("factor system mismatch")
    if record.get("before_support") != len(coefficients):
        raise ValueError("before support mismatch")

    delta: Coefficients = {factor: 1}
    expected_operations: list[dict[str, Any]] = []
    for space, coefficient in sorted(coefficients.items(), key=lambda item: system_key(item[0])):
        meter.charge("verifier_signed_transition_terms")
        overlap = intersection(space, factor, dimension, meter)
        contribution = 0 if overlap is None else -coefficient
        expected_operations.append(
            {
                "source_space": system_payload(space),
                "source_coefficient": coefficient,
                "intersection": system_payload(overlap),
                "delta_coefficient": contribution,
            }
        )
        if overlap is not None:
            delta[overlap] = delta.get(overlap, 0) + contribution
            if delta[overlap] == 0:
                del delta[overlap]
    if record.get("intersection_operations") != expected_operations:
        raise ValueError("intersection operation mismatch")
    if record.get("delta_support") != len(delta):
        raise ValueError("delta support mismatch")

    updated = dict(coefficients)
    expected_merges: list[dict[str, Any]] = []
    for space, contribution in sorted(delta.items(), key=lambda item: system_key(item[0])):
        meter.charge("verifier_signed_delta_merges")
        old = updated.get(space, 0)
        new = old + contribution
        expected_merges.append(
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
    if record.get("merge_operations") != expected_merges:
        raise ValueError("merge operation mismatch")
    working_support = len(coefficients) + len(delta)
    bit_volume = coefficient_bit_volume(updated)
    if record.get("working_support") != working_support:
        raise ValueError("working support mismatch")
    if record.get("live_support") != len(updated):
        raise ValueError("live support mismatch")
    if record.get("coefficient_bit_volume") != bit_volume:
        raise ValueError("coefficient volume mismatch")
    if record.get("after_terms") != coefficient_payload(updated, dimension):
        raise ValueError("after terms mismatch")
    if enforce_support:
        meter.check_support(len(updated), factor_index + 1, working_support)
        meter.check_coefficient_volume(updated, factor_index + 1)
    return updated, working_support, bit_volume


def verify_exact_terminal(
    cnf: CNF,
    affine: tuple[Equation, ...],
    nvars: int,
    certificate: dict[str, Any],
    capability: Capability,
    meter: CrossingMeter,
) -> bool:
    basis = certificate.get("basis_artifact")
    if not isinstance(basis, dict) or digest(basis) != certificate.get("basis_digest"):
        return False
    if not verify_basis_artifact(affine, nvars, basis, meter):
        return False
    if basis.get("status") == "UNSAT":
        return certificate.get("status") == "UNSAT" and certificate.get("reason") == "AFFINE_CONTRADICTION"
    dimension = int(basis["dimension"])
    if int(certificate.get("dimension", -1)) != dimension:
        return False
    coordinate_forms = [(int(mask), int(constant)) for mask, constant in basis["coordinate_forms"]]
    expected_raw = [
        translate_clause(clause_id, clause, coordinate_forms, dimension, meter)
        for clause_id, clause in enumerate(cnf)
    ]
    if certificate.get("raw_factors") != expected_raw:
        return False
    factors = deterministic_factors(expected_raw)
    expected_order = [
        {
            "factor_index": index,
            "clause_id": int(factor["clause_id"]),
            "space": system_payload(canonical_factor_system(factor)),
        }
        for index, factor in enumerate(factors)
    ]
    if certificate.get("factor_order") != expected_order:
        return False
    transitions = certificate.get("signed_transitions")
    if not isinstance(transitions, list) or len(transitions) != len(factors):
        return False
    coefficients: Coefficients = {}
    meter.check_support(0, 0, 0)
    max_support = max_working = max_bits = 0
    for index, factor in enumerate(factors):
        coefficients, working, bit_volume = replay_transition(
            coefficients,
            canonical_factor_system(factor),
            index,
            int(factor["clause_id"]),
            dimension,
            transitions[index],
            meter,
        )
        max_support = max(max_support, len(coefficients))
        max_working = max(max_working, working)
        max_bits = max(max_bits, bit_volume)
    if certificate.get("final_terms") != coefficient_payload(coefficients, dimension):
        return False
    if int(certificate.get("max_live_support", -1)) != max_support:
        return False
    if int(certificate.get("max_working_support", -1)) != max_working:
        return False
    if int(certificate.get("max_coefficient_bit_volume", -1)) != max_bits:
        return False
    union_size, root_trace = count_signed(coefficients, (), dimension, meter)
    total_points = 1 << dimension
    if certificate.get("union_size") != str(union_size):
        return False
    if certificate.get("total_points") != str(total_points):
        return False
    if certificate.get("root_count_trace") != root_trace:
        return False

    status = certificate.get("status")
    if status == "UNSAT":
        return certificate.get("reason") == "EXACT_SIGNED_INTERSECTION_COVER" and union_size == total_points
    if status != "SAT" or not 0 <= union_size < total_points:
        return False
    trace = certificate.get("witness_trace")
    if not isinstance(trace, list) or len(trace) != dimension:
        return False
    prefix: tuple[Equation, ...] = ()
    lambda_mask = 0
    for variable, record in enumerate(trace, start=1):
        if record.get("variable") != variable:
            return False
        expected_branches: list[dict[str, Any]] = []
        first_undercovered: int | None = None
        cells: dict[int, tuple[Equation, ...]] = {}
        for bit in (0, 1):
            cell = prefix_cell(prefix, variable, bit, dimension, meter)
            cells[bit] = cell
            covered, count_trace = count_signed(coefficients, cell, dimension, meter)
            cell_points = 1 << system_dimension(cell, dimension)
            expected_branches.append(
                {
                    "bit": bit,
                    "cell": system_payload(cell),
                    "covered_points": str(covered),
                    "cell_points": str(cell_points),
                    "count_trace": count_trace,
                }
            )
            if first_undercovered is None and covered < cell_points:
                first_undercovered = bit
        if record.get("branches") != expected_branches:
            return False
        if record.get("chosen_bit") != first_undercovered or first_undercovered is None:
            return False
        if first_undercovered:
            lambda_mask |= 1 << (variable - 1)
        prefix = cells[first_undercovered]
    if certificate.get("lambda_witness_mask") != str(lambda_mask):
        return False
    if certificate.get("lambda_witness") != assignment_dict(lambda_mask, dimension):
        return False
    witness_mask = lift_coordinate_mask(lambda_mask, basis, nvars)
    if certificate.get("witness_mask") != str(witness_mask):
        return False
    if certificate.get("witness") != assignment_dict(witness_mask, nvars):
        return False
    if not evaluate_equations(affine, witness_mask) or not evaluate_cnf(cnf, witness_mask):
        return False
    return all(not evaluate_equations(canonical_factor_system(factor), lambda_mask) for factor in factors)


def verify_support_open(
    cnf: CNF,
    affine: tuple[Equation, ...],
    nvars: int,
    certificate: dict[str, Any],
    capability: Capability,
    meter: CrossingMeter,
) -> bool:
    basis = certificate.get("basis_artifact")
    raw = certificate.get("raw_factors")
    completed = certificate.get("completed_transitions")
    if not isinstance(basis, dict) or not isinstance(raw, list) or not isinstance(completed, list):
        return False
    if digest(basis) != certificate.get("basis_digest"):
        return False
    if not verify_basis_artifact(affine, nvars, basis, meter) or basis.get("status") != "SAT":
        return False
    dimension = int(basis["dimension"])
    forms = [(int(mask), int(constant)) for mask, constant in basis["coordinate_forms"]]
    expected_raw = [
        translate_clause(clause_id, clause, forms, dimension, meter)
        for clause_id, clause in enumerate(cnf)
    ]
    if raw != expected_raw:
        return False
    factors = deterministic_factors(expected_raw)
    if len(completed) >= len(factors):
        return False
    coefficients: Coefficients = {}
    meter.check_support(0, 0, 0)
    for index, record in enumerate(completed):
        factor = factors[index]
        coefficients, _, _ = replay_transition(
            coefficients,
            canonical_factor_system(factor),
            index,
            int(factor["clause_id"]),
            dimension,
            record,
            meter,
        )
    next_index = len(completed)
    factor = factors[next_index]
    delta: Coefficients = {canonical_factor_system(factor): 1}
    for space, coefficient in sorted(coefficients.items(), key=lambda item: system_key(item[0])):
        overlap = intersection(space, canonical_factor_system(factor), dimension, meter)
        if overlap is not None:
            delta[overlap] = delta.get(overlap, 0) - coefficient
            if delta[overlap] == 0:
                del delta[overlap]
    attempted = dict(coefficients)
    for space, contribution in delta.items():
        new = attempted.get(space, 0) + contribution
        if new == 0:
            attempted.pop(space, None)
        else:
            attempted[space] = new
    evidence = certificate.get("overflow_evidence", {})
    return (
        len(attempted) > capability.support_limit
        and int(evidence.get("factor_index", -1)) == next_index
        and int(evidence.get("attempted_support", -1)) == len(attempted)
        and int(evidence.get("support_limit", -1)) == capability.support_limit
        and evidence.get("factor") == system_payload(canonical_factor_system(factor))
        and evidence.get("before_terms") == coefficient_payload(coefficients, dimension)
    )


def verify_crossing_certificate(
    cnf: CNF,
    affine: tuple[Equation, ...],
    certificate: dict[str, Any],
    *,
    nvars_hint: int = 0,
) -> bool:
    try:
        cnf = normalize_cnf(cnf)
        nvars = max(nvars_hint, max(variables_in_cnf(cnf) | variables_in_affine(affine), default=0))
        if certificate.get("schema") != SCHEMA or certificate.get("p_vs_np") != "OPEN":
            return False
        body = dict(certificate)
        stated_digest = body.pop("integrity_sha256", None)
        if stated_digest is None or digest(body) != stated_digest:
            return False
        if certificate.get("input_digest") != digest(canonical_input(cnf, affine, nvars)):
            return False
        if int(certificate.get("nvars", -1)) != nvars:
            return False
        manifest = certificate.get("capability")
        if not isinstance(manifest, dict):
            return False
        capability = Capability.from_manifest(manifest)
        if capability.input_length != encoded_length(cnf, affine, nvars):
            return False
        if not verify_producer_ledger(certificate, capability):
            return False
        verifier_capability = Capability(
            capability.input_length,
            support_cap=capability.support_limit,
            coefficient_bit_cap=capability.coefficient_bit_limit,
        )
        meter = CrossingMeter(verifier_capability)
        status = certificate.get("status")
        if status == OPEN_INTERSECTION_CLOSURE:
            return verify_support_open(cnf, affine, nvars, certificate, capability, meter)
        if status == OPEN_WORK_BUDGET:
            evidence = certificate.get("overflow_evidence", {})
            if certificate.get("reason") == "coefficient_bit_volume":
                return int(evidence.get("coefficient_bit_volume", 0)) > capability.coefficient_bit_limit
            return int(certificate["producer_ledger"]["total_work_units"]) > capability.work_limit
        if status == OPEN_CERTIFICATE_VOLUME:
            evidence = certificate.get("overflow_evidence", {})
            return (
                int(evidence.get("attempted_certificate_bytes", 0)) > capability.certificate_limit
                and isinstance(evidence.get("semantic_payload_sha256"), str)
                and len(evidence["semantic_payload_sha256"]) == 64
            )
        if status not in {"SAT", "UNSAT"}:
            return False
        probe = dict(certificate)
        probe["integrity_sha256"] = "0" * 64
        if int(certificate.get("certificate_bytes", -1)) != len(canonical_json(probe).encode()):
            return False
        if int(certificate["producer_ledger"]["counters"].get("certificate_bytes", 0)) < int(certificate["certificate_bytes"]):
            return False
        return verify_exact_terminal(cnf, affine, nvars, certificate, capability, meter)
    except (CrossingOpen, KeyError, TypeError, ValueError, AssertionError):
        return False
