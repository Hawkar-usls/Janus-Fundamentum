#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import itertools
import json
import random
from typing import Any

from janus_c042_affine_core import digest, evaluate_cnf, evaluate_equations, normalize_cnf
from janus_c043_crossing_solver import solve_crossing
from janus_c043_crossing_verifier import verify_crossing_certificate

Equation = tuple[int, int]
Clause = tuple[int, ...]
CNF = tuple[Clause, ...]


def brute(cnf: CNF, affine: tuple[Equation, ...], nvars: int) -> tuple[bool, int | None]:
    cnf = normalize_cnf(cnf)
    for assignment in range(1 << nvars):
        if evaluate_equations(affine, assignment) and evaluate_cnf(cnf, assignment):
            return True, assignment
    return False, None


def prefix_clause(pattern: tuple[int, ...]) -> Clause:
    return tuple(index if bit == 0 else -index for index, bit in enumerate(pattern, start=1))


def rehash(certificate: dict[str, Any]) -> dict[str, Any]:
    certificate["integrity_sha256"] = digest(
        {key: value for key, value in certificate.items() if key != "integrity_sha256"}
    )
    return certificate


def c023_hard_image(n: int) -> tuple[CNF, tuple[Equation, ...], int]:
    source: list[Clause] = [(1, -2, 3), (1, 4, -5)]
    for index in range(2, n - 1):
        literals = (index, (index % n) + 1, ((index + 2) % n) + 1)
        source.append(
            tuple(
                literal if (index + offset) % 2 else -literal
                for offset, literal in enumerate(literals)
            )
        )
    horn = []
    for clause in source:
        indicators = [n + abs(literal) if literal > 0 else abs(literal) for literal in clause]
        horn.append(tuple(-indicator for indicator in indicators))
    affine = tuple(
        ((1 << (variable - 1)) | (1 << (n + variable - 1)), 1)
        for variable in range(1, n + 1)
    )
    return normalize_cnf(tuple(horn)), affine, 2 * n


def audit(seed: int = 430043) -> dict[str, Any]:
    rng = random.Random(seed)
    random_cases = 120
    exact = opened = mismatches = verification_failures = witness_failures = 0
    max_live_support = max_verifier_certificate_bytes = 0

    for _ in range(random_cases):
        dimension = rng.randint(1, 7)
        clauses: list[Clause] = []
        for _index in range(rng.randint(0, 9)):
            width = rng.randint(1, min(3, dimension))
            variables = rng.sample(range(1, dimension + 1), width)
            clauses.append(tuple(variable if rng.getrandbits(1) else -variable for variable in variables))
        cnf = tuple(clauses)
        certificate = solve_crossing(cnf, (), nvars_hint=dimension, support_cap=1_000)
        truth, _ = brute(cnf, (), dimension)
        if certificate["status"].startswith("OPEN_"):
            opened += 1
            continue
        exact += 1
        mismatches += int((certificate["status"] == "SAT") != truth)
        verified = verify_crossing_certificate(cnf, (), certificate, nvars_hint=dimension)
        verification_failures += int(not verified)
        max_live_support = max(max_live_support, int(certificate.get("max_live_support", 0)))
        max_verifier_certificate_bytes = max(
            max_verifier_certificate_bytes, int(certificate.get("certificate_bytes", 0))
        )
        if certificate["status"] == "SAT":
            witness = int(certificate["witness_mask"])
            witness_failures += int(not evaluate_cnf(normalize_cnf(cnf), witness))

    crossing_cnf = ((1,), (2,))
    crossing = solve_crossing(crossing_cnf, (), nvars_hint=64)
    assert crossing["status"] == "SAT" and crossing["max_live_support"] == 3
    assert verify_crossing_certificate(crossing_cnf, (), crossing, nvars_hint=64)

    cover_cnf = tuple(
        prefix_clause(pattern) for pattern in ((0, 0), (0, 1), (1, 0), (1, 1))
    )
    cover = solve_crossing(cover_cnf, (), nvars_hint=64)
    assert cover["status"] == "UNSAT"
    assert verify_crossing_certificate(cover_cnf, (), cover, nvars_hint=64)

    affine_cnf = ((1,), (2,))
    affine = ((0b11, 1),)
    affine_cover = solve_crossing(affine_cnf, affine, nvars_hint=2)
    assert affine_cover["status"] == "UNSAT"
    assert verify_crossing_certificate(affine_cnf, affine, affine_cover, nvars_hint=2)

    pressure_dimension = 5
    small_final_cnf = tuple(
        prefix_clause(pattern)
        for pattern in itertools.product((0, 1), repeat=pressure_dimension)
    ) + ((),)
    small_final = solve_crossing(small_final_cnf, (), nvars_hint=pressure_dimension)
    assert small_final["status"] == "UNSAT"
    assert len(small_final["final_terms"]) == 1
    assert small_final["max_live_support"] == 32
    assert verify_crossing_certificate(
        small_final_cnf, (), small_final, nvars_hint=pressure_dimension
    )
    hidden_spike = solve_crossing(
        small_final_cnf, (), nvars_hint=pressure_dimension, support_cap=8
    )
    assert hidden_spike["status"] == "OPEN_INTERSECTION_CLOSURE"
    assert verify_crossing_certificate(
        small_final_cnf, (), hidden_spike, nvars_hint=pressure_dimension
    )

    coefficient_cnf = ((1,), (2,), (3,))
    coefficient_affine = ((0b111, 0),)
    coefficient_open = solve_crossing(
        coefficient_cnf,
        coefficient_affine,
        nvars_hint=3,
        coefficient_bit_cap=4,
    )
    assert coefficient_open["status"] == "OPEN_WORK_BUDGET"
    assert coefficient_open["reason"] == "coefficient_bit_volume"
    assert verify_crossing_certificate(
        coefficient_cnf, coefficient_affine, coefficient_open, nvars_hint=3
    )

    hard_controls: dict[str, str] = {}
    for n in (18, 24, 30):
        hard_cnf, hard_affine, hard_nvars = c023_hard_image(n)
        hard = solve_crossing(
            hard_cnf,
            hard_affine,
            nvars_hint=hard_nvars,
            support_cap=64,
        )
        hard_controls[str(n)] = hard["status"]
        assert hard["status"] == "OPEN_INTERSECTION_CLOSURE"
        assert verify_crossing_certificate(
            hard_cnf, hard_affine, hard, nvars_hint=hard_nvars
        )

    tampered_basis = copy.deepcopy(affine_cover)
    tampered_basis["basis_artifact"]["particular_mask"] = str(
        int(tampered_basis["basis_artifact"]["particular_mask"]) ^ 1
    )
    tampered_basis["basis_digest"] = digest(tampered_basis["basis_artifact"])
    rehash(tampered_basis)
    assert not verify_crossing_certificate(
        affine_cnf, affine, tampered_basis, nvars_hint=2
    )

    changed_order = copy.deepcopy(crossing)
    changed_order["factor_order"][0], changed_order["factor_order"][1] = (
        changed_order["factor_order"][1],
        changed_order["factor_order"][0],
    )
    rehash(changed_order)
    assert not verify_crossing_certificate(
        crossing_cnf, (), changed_order, nvars_hint=64
    )

    corrupt_cancellation = copy.deepcopy(crossing)
    operation = corrupt_cancellation["signed_transitions"][1]["intersection_operations"][0]
    operation["delta_coefficient"] = -2
    rehash(corrupt_cancellation)
    assert not verify_crossing_certificate(
        crossing_cnf, (), corrupt_cancellation, nvars_hint=64
    )

    corrupt_witness = copy.deepcopy(crossing)
    corrupt_witness["witness"]["1"] = not corrupt_witness["witness"]["1"]
    rehash(corrupt_witness)
    assert not verify_crossing_certificate(
        crossing_cnf, (), corrupt_witness, nvars_hint=64
    )

    corrupt_cover = copy.deepcopy(cover)
    corrupt_cover["union_size"] = str(int(corrupt_cover["union_size"]) - 1)
    rehash(corrupt_cover)
    assert not verify_crossing_certificate(cover_cnf, (), corrupt_cover, nvars_hint=64)

    result = {
        "artifact_id": "C043-JANUS-BOUNDED-LIVE-SIGNED-SUPPORT",
        "schema": "janus.c043.bounded_live_signed_support.v2",
        "status": "PASS",
        "admission_status": "FULL_IMPLEMENTATION_CANDIDATE",
        "p_vs_np": "OPEN",
        "seed": seed,
        "random_cases": random_cases,
        "exact": exact,
        "open": opened,
        "mismatches": mismatches,
        "witness_failures": witness_failures,
        "verification_failures": verification_failures,
        "max_live_support_random": max_live_support,
        "max_certificate_bytes_random": max_verifier_certificate_bytes,
        "basis_contract": "C042 provenance-carrying affine artifact inherited and independently checked",
        "verifier_contract": "separate module; solve_crossing is never invoked",
        "crossing_sat": {
            "dimension": 64,
            "max_live_support": crossing["max_live_support"],
            "status": crossing["status"],
        },
        "crossing_unsat_cover": {
            "dimension": 64,
            "max_live_support": cover["max_live_support"],
            "status": cover["status"],
        },
        "small_final_large_intermediate": {
            "final_terms": len(small_final["final_terms"]),
            "max_live_support": small_final["max_live_support"],
            "tight_support_status": hidden_spike["status"],
        },
        "coefficient_bit_volume_control": coefficient_open["status"],
        "nand3_neq_controls": hard_controls,
        "tampered_basis": "REJECTED",
        "changed_factor_order": "REJECTED",
        "corrupt_cancellation_trace": "REJECTED",
        "corrupt_sat_witness": "REJECTED",
        "corrupt_signed_unsat_cover": "REJECTED",
        "new_gate": "POLYNOMIAL_LOCALIZATION_OF_SUPERPOLYNOMIAL_GLOBAL_INTERSECTION_SUPPORT",
        "claim_boundary": (
            "Global bounded maximum live signed support only. Local vtree composition, arbitrary CNF, "
            "unrestricted Horn-affine composition, and P versus NP remain open."
        ),
    }
    result["integrity_sha256"] = digest(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--seed", type=int, default=430043)
    parser.add_argument("--output")
    args = parser.parse_args()
    result = audit(args.seed)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2, sort_keys=True)
            handle.write("\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.self_test:
        assert result["status"] == "PASS"
        assert result["mismatches"] == 0
        assert result["witness_failures"] == 0
        assert result["verification_failures"] == 0


if __name__ == "__main__":
    main()
