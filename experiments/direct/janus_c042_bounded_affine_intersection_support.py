#!/usr/bin/env python3
"""C042 proof-carrying bounded signed-intersection support envelope.

The imported core maintains an exact signed indicator representation

    1_(union U_i) = sum_S c_S 1_S

for clause-falsifying affine subspaces. This canonical envelope strengthens
budget binding and coefficient-volume accounting: every capability exponent,
absolute cap, effective cap, and certificate digest is committed and replayed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from typing import Any

import janus_c042_bounded_affine_intersection_support_core as core

Clause = tuple[int, ...]


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def digest(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj).encode()).hexdigest()


def input_length(
    cnf: tuple[Clause, ...],
    coordinate_rows: dict[int, int],
    dimension: int,
) -> int:
    return max(
        2,
        dimension
        + len(cnf)
        + sum(len(clause) for clause in cnf)
        + sum(mask.bit_count() for mask in coordinate_rows.values()),
    )


def _effective_cap(absolute: int, length: int, exponent: int) -> int:
    if absolute < 0 or exponent < 0:
        raise ValueError("budget caps and exponents must be nonnegative")
    return min(absolute, length**exponent)


def solve(
    cnf: tuple[Clause, ...],
    coordinate_rows: dict[int, int],
    coordinate_constants: dict[int, int],
    dimension: int,
    *,
    closure_exponent: int = 2,
    work_exponent: int = 4,
    certificate_exponent: int = 4,
    absolute_closure_limit: int = 200_000,
    absolute_work_limit: int = 20_000_000,
    absolute_certificate_limit: int = 20_000_000,
) -> dict[str, Any]:
    length = input_length(cnf, coordinate_rows, dimension)
    closure_limit = _effective_cap(absolute_closure_limit, length, closure_exponent)
    work_limit = _effective_cap(absolute_work_limit, length, work_exponent)
    certificate_limit = _effective_cap(
        absolute_certificate_limit, length, certificate_exponent
    )

    budgets = {
        "closure_exponent": closure_exponent,
        "work_exponent": work_exponent,
        "certificate_exponent": certificate_exponent,
        "absolute_closure_limit": absolute_closure_limit,
        "absolute_work_limit": absolute_work_limit,
        "absolute_certificate_limit": absolute_certificate_limit,
        "effective_closure_limit": closure_limit,
        "effective_work_limit": work_limit,
        "effective_certificate_limit": certificate_limit,
    }

    result = core.solve(
        cnf,
        coordinate_rows,
        coordinate_constants,
        dimension,
        capability_exponent=closure_exponent,
        absolute_closure_limit=closure_limit,
        work_limit=work_limit,
        certificate_limit=certificate_limit,
    )

    terms = result.get("coefficient_terms", [])
    coefficient_bits = [
        max(1, abs(int(term["coefficient"])).bit_length()) for term in terms
    ]
    factor_count = int(result.get("factor_count", len(cnf)))
    accounting = {
        "factor_count": factor_count,
        "nonzero_signed_terms": len(terms),
        "max_nonzero_signed_terms": int(result.get("max_coefficient_terms", 0)),
        "transient_support_bound": int(result.get("max_coefficient_terms", 0)) + 1,
        "max_coefficient_bit_length": max(coefficient_bits, default=0),
        "total_coefficient_bit_length": sum(coefficient_bits),
        "proved_coefficient_bit_bound": factor_count + 1,
        "core_work_units": int(result.get("work", 0)),
        "core_intersection_calls": int(result.get("intersection_calls", 0)),
    }

    if accounting["max_coefficient_bit_length"] > accounting["proved_coefficient_bit_bound"]:
        raise AssertionError("coefficient bit bound violated")
    if accounting["core_work_units"] > work_limit:
        raise AssertionError("core accepted beyond committed work limit")
    if accounting["max_nonzero_signed_terms"] > closure_limit:
        raise AssertionError("core accepted beyond committed support limit")

    envelope: dict[str, Any] = {
        "schema": "janus.c042.bounded_affine_intersection_support.v1",
        "status": result.get("status"),
        "dimension": dimension,
        "encoding_length": length,
        "budgets": budgets,
        "accounting": accounting,
        "core_schema": result.get("schema"),
        "core_result": result,
        "p_vs_np": "OPEN",
    }

    encoded_without_digest = len(canonical_json(envelope).encode())
    if (
        not str(result.get("status", "")).startswith("OPEN_")
        and encoded_without_digest > certificate_limit
    ):
        envelope = {
            "schema": "janus.c042.bounded_affine_intersection_support.v1",
            "status": "OPEN_CERTIFICATE_VOLUME",
            "dimension": dimension,
            "encoding_length": length,
            "budgets": budgets,
            "accounting": accounting,
            "core_status": result.get("status"),
            "core_digest": digest(result),
            "observed_envelope_bytes": encoded_without_digest,
            "p_vs_np": "OPEN",
        }

    envelope["integrity_sha256"] = digest(envelope)
    return envelope


def verify(
    cnf: tuple[Clause, ...],
    coordinate_rows: dict[int, int],
    coordinate_constants: dict[int, int],
    dimension: int,
    certificate: dict[str, Any],
) -> bool:
    integrity = certificate.get("integrity_sha256")
    if not isinstance(integrity, str):
        return False
    body = dict(certificate)
    body.pop("integrity_sha256", None)
    if digest(body) != integrity:
        return False

    budgets = certificate.get("budgets")
    if not isinstance(budgets, dict):
        return False
    required = {
        "closure_exponent",
        "work_exponent",
        "certificate_exponent",
        "absolute_closure_limit",
        "absolute_work_limit",
        "absolute_certificate_limit",
    }
    if not required <= set(budgets):
        return False

    replay = solve(
        cnf,
        coordinate_rows,
        coordinate_constants,
        dimension,
        closure_exponent=int(budgets["closure_exponent"]),
        work_exponent=int(budgets["work_exponent"]),
        certificate_exponent=int(budgets["certificate_exponent"]),
        absolute_closure_limit=int(budgets["absolute_closure_limit"]),
        absolute_work_limit=int(budgets["absolute_work_limit"]),
        absolute_certificate_limit=int(budgets["absolute_certificate_limit"]),
    )
    return replay == certificate


def audit() -> dict[str, Any]:
    core_result = core.audit()
    assert core_result["status"] == "PASS"
    assert core_result["mismatches"] == 0
    assert core_result["verification_failures"] == 0

    dimension = 64
    rows = {i: 1 << (i - 1) for i in range(1, dimension + 1)}
    constants = {i: 0 for i in rows}

    crossing_cnf = ((1,), (2,))
    crossing = solve(crossing_cnf, rows, constants, dimension)
    assert crossing["status"] == "SAT"
    assert crossing["accounting"]["max_nonzero_signed_terms"] == 3
    assert verify(crossing_cnf, rows, constants, dimension, crossing)

    cover_cnf = tuple(
        core.prefix_clause(pattern)
        for pattern in ((0, 0), (0, 1), (1, 0), (1, 1))
    )
    cover = solve(cover_cnf, rows, constants, dimension)
    assert cover["status"] == "UNSAT"
    assert verify(cover_cnf, rows, constants, dimension, cover)

    repeated = tuple((1,) if i % 2 == 0 else (2,) for i in range(200))
    repeated_result = solve(repeated, rows, constants, dimension)
    assert repeated_result["status"] == "SAT"
    assert repeated_result["accounting"]["max_nonzero_signed_terms"] <= 3
    assert repeated_result["accounting"]["max_coefficient_bit_length"] <= 201
    assert verify(repeated, rows, constants, dimension, repeated_result)

    hard_cnf, hard_rows, hard_constants = core.hard_image(24)
    hard = solve(
        hard_cnf,
        hard_rows,
        hard_constants,
        24,
        closure_exponent=2,
        absolute_closure_limit=20_000,
    )
    assert hard["status"] == "OPEN_INTERSECTION_CLOSURE"
    assert verify(hard_cnf, hard_rows, hard_constants, 24, hard)

    work_open = solve(
        crossing_cnf,
        rows,
        constants,
        dimension,
        absolute_work_limit=1,
    )
    assert work_open["status"] == "OPEN_WORK_BUDGET"
    assert verify(crossing_cnf, rows, constants, dimension, work_open)

    certificate_open = solve(
        crossing_cnf,
        rows,
        constants,
        dimension,
        absolute_certificate_limit=128,
    )
    assert certificate_open["status"] == "OPEN_CERTIFICATE_VOLUME"
    assert verify(crossing_cnf, rows, constants, dimension, certificate_open)

    corrupt = json.loads(json.dumps(cover))
    corrupt["accounting"]["core_work_units"] += 1
    assert not verify(cover_cnf, rows, constants, dimension, corrupt)

    budget_corrupt = json.loads(json.dumps(work_open))
    budget_corrupt["budgets"]["absolute_work_limit"] = 2
    assert not verify(crossing_cnf, rows, constants, dimension, budget_corrupt)

    result = {
        "artifact_id": "C042-JANUS-BOUNDED-AFFINE-INTERSECTION-SUPPORT",
        "status": "PASS",
        "p_vs_np": "OPEN",
        "core_random_cases": core_result["random_cases"],
        "core_exact_cases": core_result["exact_cases"],
        "core_open_cases": core_result["open_cases"],
        "core_mismatches": core_result["mismatches"],
        "core_verification_failures": core_result["verification_failures"],
        "crossing_dimension": dimension,
        "crossing_signed_terms": crossing["accounting"]["max_nonzero_signed_terms"],
        "crossing_sat": crossing["status"],
        "crossing_unsat_cover": cover["status"],
        "repeated_factor_count": len(repeated),
        "repeated_signed_terms": repeated_result["accounting"]["max_nonzero_signed_terms"],
        "nand3_neq_control": hard["status"],
        "work_budget_binding": work_open["status"],
        "certificate_budget_binding": certificate_open["status"],
        "corrupt_certificate_control": "REJECTED",
        "corrupt_budget_control": "REJECTED",
        "constructive_theorem": (
            "Affine-coordinate CNF is exactly decidable in polynomial total work "
            "whenever the deterministic nonzero signed-intersection support remains "
            "within one fixed polynomial capability."
        ),
        "new_gate": "POLYNOMIAL_DECOMPOSITION_BEYOND_BOUNDED_SIGNED_INTERSECTION_SUPPORT",
        "claim_boundary": (
            "This is an output-sensitive exact compiler for bounded signed support. "
            "It does not decide arbitrary CNF, prove that all arrangements have "
            "polynomial support, or resolve P versus NP."
        ),
    }
    result["integrity_sha256"] = digest(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args()
    result = audit()
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2, sort_keys=True)
            handle.write("\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.self_test:
        assert result["status"] == "PASS"


if __name__ == "__main__":
    main()
