#!/usr/bin/env python3
from __future__ import annotations
from janus_c037_2_horn_affine_hull_core import *

def meter_payload(meter: Meter) -> dict:
    return {
        "work_units": meter.work_units,
        "horn_calls": meter.horn_calls,
        "horn_clause_scans": meter.horn_clause_scans,
        "equality_pair_queries": meter.equality_pair_queries,
        "basis_extractions": meter.basis_extractions,
        "affine_row_xors": meter.affine_row_xors,
        "self_reduction_tests": meter.self_reduction_tests,
    }


def reverse_horn_to_affine_inclusion(
    formula: CNF,
    affine_rows: tuple[Equation, ...],
    variable_count: int,
    work_budget: int = 10_000_000,
):
    formula = normalize(formula)
    if not is_horn(formula):
        return {
            "schema": SCHEMA,
            "policy": POLICY,
            "terminal": {"status": "OPEN_LANGUAGE"},
        }

    meter = Meter(work_budget)
    certificate = {
        "schema": SCHEMA,
        "policy": POLICY,
        "variable_count": variable_count,
        "horn": [list(clause) for clause in formula],
        "affine_rows": [list(row) for row in affine_rows],
        "basis": None,
        "row_events": [],
    }
    try:
        basis_certificate = extract_affine_consequence_basis(
            formula, variable_count, {}, meter
        )
        certificate["basis"] = basis_certificate
        if basis_certificate["status"] == "UNSAT":
            certificate["terminal"] = {
                "status": "HORN_EMPTY_SUBSET",
                "relation": "MODELS(HORN) SUBSET MODELS(AFFINE)",
            }
            certificate["cost"] = meter_payload(meter)
            certificate["integrity_sha256"] = digest(certificate)
            return certificate

        elimination = build_augmented_elimination(
            basis_certificate["rows"], variable_count, meter
        )
        for row_index, row in enumerate(affine_rows):
            residual, provenance = reduce_augmented_row(
                row, variable_count, elimination, meter
            )
            if residual:
                assignment, decisions = recover_horn_countermodel(
                    formula, variable_count, row, meter
                )
                certificate["terminal"] = {
                    "status": "SEPARATOR",
                    "direction": "HORN_NOT_AFFINE",
                    "row_index": row_index,
                    "assignment": {
                        str(variable): int(value)
                        for variable, value in sorted(assignment.items())
                    },
                    "self_reduction": decisions,
                }
                certificate["cost"] = meter_payload(meter)
                certificate["integrity_sha256"] = digest(certificate)
                return certificate
            certificate["row_events"].append(
                {
                    "kind": "HORN_ENTAILS_AFFINE_ROW",
                    "row_index": row_index,
                    "basis_provenance": provenance,
                }
            )

        certificate["terminal"] = {
            "status": "DIRECTED_INCLUSION",
            "relation": "MODELS(HORN) SUBSET MODELS(AFFINE)",
        }
        certificate["cost"] = meter_payload(meter)
        certificate["integrity_sha256"] = digest(certificate)
        return certificate
    except BudgetExceeded:
        certificate["terminal"] = {
            "status": "OPEN_BUDGET",
            "budget": work_budget,
        }
        certificate["cost"] = meter_payload(meter)
        certificate["integrity_sha256"] = digest(certificate)
        return certificate


def replay_certificate(certificate: dict) -> bool:
    terminal = certificate.get("terminal", {})
    if terminal.get("status") in {"OPEN_LANGUAGE", "OPEN_BUDGET"}:
        return True

    variable_count = int(certificate["variable_count"])
    formula = normalize(
        tuple(tuple(int(literal) for literal in clause) for clause in certificate["horn"])
    )
    affine_rows = tuple(
        (int(row[0]), int(row[1])) for row in certificate["affine_rows"]
    )

    if terminal["status"] == "SEPARATOR":
        assignment = {
            int(variable): bool(value)
            for variable, value in terminal["assignment"].items()
        }
        row_index = int(terminal["row_index"])
        return (
            eval_cnf(formula, assignment)
            and not eval_row(affine_rows[row_index], assignment)
        )

    verifier_meter = Meter(10**12)
    recomputed = extract_affine_consequence_basis(
        formula, variable_count, {}, verifier_meter
    )
    if terminal["status"] == "HORN_EMPTY_SUBSET":
        return recomputed["status"] == "UNSAT"
    if terminal["status"] != "DIRECTED_INCLUSION":
        return False
    if recomputed["status"] != "SAT":
        return False
    elimination = build_augmented_elimination(
        recomputed["rows"], variable_count, verifier_meter
    )
    return all(
        reduce_augmented_row(row, variable_count, elimination)[0] == 0
        for row in affine_rows
    )


def affine_inconsistency_provenance(
    rows: list[Equation], variable_count: int, meter: Meter
):
    basis: dict[int, tuple[int, int, int]] = {}
    for row_index, (mask, rhs) in enumerate(rows):
        provenance = 1 << row_index
        current_mask = mask
        current_rhs = rhs
        while current_mask:
            pivot = current_mask.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = (current_mask, current_rhs, provenance)
                break
            pivot_mask, pivot_rhs, pivot_provenance = basis[pivot]
            current_mask ^= pivot_mask
            current_rhs ^= pivot_rhs
            provenance ^= pivot_provenance
            meter.affine_row_xors += 1
            meter.charge()
        if current_mask == 0 and current_rhs == 1:
            return provenance
    return None


def complete_affine_consequence_negotiation(
    formula: CNF,
    affine_rows: tuple[Equation, ...],
    variable_count: int,
    work_budget: int = 10_000_000,
):
    formula = normalize(formula)
    if not is_horn(formula):
        return {
            "schema": SCHEMA,
            "policy": "COMPLETE_HORN_AFFINE_CONSEQUENCE_NEGOTIATION_V1",
            "terminal": {"status": "OPEN_LANGUAGE"},
        }
    meter = Meter(work_budget)
    result = {
        "schema": SCHEMA,
        "policy": "COMPLETE_HORN_AFFINE_CONSEQUENCE_NEGOTIATION_V1",
        "variable_count": variable_count,
        "horn": [list(clause) for clause in formula],
        "affine_rows": [list(row) for row in affine_rows],
    }
    try:
        basis = extract_affine_consequence_basis(
            formula, variable_count, {}, meter
        )
        result["basis"] = basis
        if basis["status"] == "UNSAT":
            result["terminal"] = {
                "status": "CERTIFIED_CONFLICT",
                "module": "HORN",
                "native_proof": basis["native_proof"],
            }
        else:
            combined = list(basis["rows"]) + list(affine_rows)
            provenance = affine_inconsistency_provenance(
                combined, variable_count, meter
            )
            if provenance is not None:
                result["terminal"] = {
                    "status": "CERTIFIED_CONFLICT",
                    "module": "AFFINE_GF2",
                    "combined_row_provenance": provenance,
                    "basis_row_count": len(basis["rows"]),
                }
            else:
                result["terminal"] = {
                    "status": "OPEN_AFFINE_CONSEQUENCE_COMPLETE",
                    "reason": (
                        "all unconditional affine consequences of the Horn module "
                        "have been injected; compatibility is not certified"
                    ),
                }
        result["cost"] = meter_payload(meter)
        result["integrity_sha256"] = digest(result)
        return result
    except BudgetExceeded:
        result["terminal"] = {
            "status": "OPEN_BUDGET",
            "budget": work_budget,
        }
        result["cost"] = meter_payload(meter)
        result["integrity_sha256"] = digest(result)
        return result
