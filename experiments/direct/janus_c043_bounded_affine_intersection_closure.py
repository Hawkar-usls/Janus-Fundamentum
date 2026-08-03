#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import random
from dataclasses import dataclass
from typing import Any, Iterable

Equation = tuple[int, int]
Clause = tuple[int, ...]
Subspace = tuple[Equation, ...]


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def digest(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj).encode()).hexdigest()


@dataclass
class Row:
    mask: int
    rhs: int

    def clone(self) -> "Row":
        return Row(self.mask, self.rhs)

    def xor(self, other: "Row") -> None:
        self.mask ^= other.mask
        self.rhs ^= other.rhs


@dataclass
class Meter:
    work_limit: int
    closure_limit: int
    certificate_limit: int
    work: int = 0
    intersections: int = 0
    max_terms: int = 0

    def charge(self, amount: int = 1) -> None:
        self.work += amount
        if self.work > self.work_limit:
            raise RuntimeError("OPEN_WORK_BUDGET")

    def closure(self, size: int) -> None:
        self.max_terms = max(self.max_terms, size)
        if size > self.closure_limit:
            raise RuntimeError("OPEN_INTERSECTION_CLOSURE")

    def certificate(self, obj: Any) -> None:
        if len(canonical_json(obj).encode()) > self.certificate_limit:
            raise RuntimeError("OPEN_CERTIFICATE_VOLUME")


def rref(equations: Iterable[Equation], dimension: int, meter: Meter | None = None) -> tuple[Subspace | None, int]:
    rows = [Row(mask, rhs & 1) for mask, rhs in equations]
    rank = 0
    for variable in range(1, dimension + 1):
        bit = 1 << (variable - 1)
        pivot = next((i for i in range(rank, len(rows)) if rows[i].mask & bit), None)
        if meter:
            meter.charge(max(1, len(rows) - rank))
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(len(rows)):
            if i != rank and rows[i].mask & bit:
                rows[i].xor(rows[rank])
                if meter:
                    meter.charge()
        rank += 1
    out: list[Equation] = []
    for row in rows:
        if meter:
            meter.charge()
        if row.mask == 0:
            if row.rhs:
                return None, rank
        else:
            out.append((row.mask, row.rhs))
    out.sort(key=lambda eq: ((eq[0] & -eq[0]).bit_length(), eq[0], eq[1]))
    return tuple(out), len(out)


def intersect(a: Subspace, b: Subspace, dimension: int, meter: Meter | None = None) -> Subspace | None:
    if meter:
        meter.intersections += 1
    return rref(a + b, dimension, meter)[0]


def subspace_dimension(space: Subspace, dimension: int) -> int:
    return dimension - len(space)


def satisfies_space(space: Subspace, assignment: dict[int, bool]) -> bool:
    packed = sum(1 << (v - 1) for v, value in assignment.items() if value)
    return all(((mask & packed).bit_count() & 1) == rhs for mask, rhs in space)


def clause_forbidden(
    clause: Clause,
    coordinate_rows: dict[int, int],
    coordinate_constants: dict[int, int],
    dimension: int,
    meter: Meter | None = None,
) -> Subspace | None:
    equations: list[Equation] = []
    for literal in clause:
        variable = abs(literal)
        if variable not in coordinate_rows:
            raise ValueError(f"missing coordinate row for variable {variable}")
        mask = coordinate_rows[variable]
        constant = coordinate_constants.get(variable, 0) & 1
        false_value = 0 if literal > 0 else 1
        equations.append((mask, false_value ^ constant))
    return rref(equations, dimension, meter)[0]


def translate(
    cnf: tuple[Clause, ...],
    coordinate_rows: dict[int, int],
    coordinate_constants: dict[int, int],
    dimension: int,
    meter: Meter,
) -> list[dict[str, Any]]:
    factors: list[dict[str, Any]] = []
    for clause_id, clause in enumerate(cnf):
        meter.charge(max(1, len(clause)))
        space = clause_forbidden(clause, coordinate_rows, coordinate_constants, dimension, meter)
        if space is not None:
            factors.append({"clause_id": clause_id, "space": space})
    return factors


def add_union_factor(
    coefficients: dict[Subspace, int],
    factor: Subspace,
    dimension: int,
    meter: Meter,
) -> dict[Subspace, int]:
    updated = dict(coefficients)
    delta: dict[Subspace, int] = {factor: 1}
    for space, coefficient in coefficients.items():
        meter.charge()
        meet = intersect(space, factor, dimension, meter)
        if meet is not None:
            delta[meet] = delta.get(meet, 0) - coefficient
    for space, coefficient in delta.items():
        meter.charge()
        updated[space] = updated.get(space, 0) + coefficient
        if updated[space] == 0:
            del updated[space]
    meter.closure(len(updated))
    return updated


def build_union_coefficients(
    factors: list[dict[str, Any]],
    dimension: int,
    meter: Meter,
) -> dict[Subspace, int]:
    coefficients: dict[Subspace, int] = {}
    for factor in factors:
        coefficients = add_union_factor(coefficients, factor["space"], dimension, meter)
    return coefficients


def covered_count(
    coefficients: dict[Subspace, int],
    condition: Subspace,
    dimension: int,
    meter: Meter,
) -> tuple[int, list[dict[str, Any]]]:
    total = 0
    trace: list[dict[str, Any]] = []
    for space, coefficient in sorted(coefficients.items()):
        meter.charge()
        meet = intersect(space, condition, dimension, meter)
        count = 0 if meet is None else 1 << subspace_dimension(meet, dimension)
        total += coefficient * count
        trace.append(
            {
                "space": [[m, r] for m, r in space],
                "coefficient": coefficient,
                "intersection_size": count,
            }
        )
    return total, trace


def solve(
    cnf: tuple[Clause, ...],
    coordinate_rows: dict[int, int],
    coordinate_constants: dict[int, int],
    dimension: int,
    *,
    capability_exponent: int = 2,
    absolute_closure_limit: int = 200_000,
    work_limit: int = 20_000_000,
    certificate_limit: int = 20_000_000,
) -> dict[str, Any]:
    if capability_exponent < 0:
        raise ValueError("capability exponent must be fixed and nonnegative")
    encoding_length = max(
        2,
        dimension
        + len(cnf)
        + sum(len(clause) for clause in cnf)
        + sum(mask.bit_count() for mask in coordinate_rows.values()),
    )
    closure_limit = min(absolute_closure_limit, encoding_length**capability_exponent)
    meter = Meter(work_limit, closure_limit, certificate_limit)
    base = {
        "schema": "janus.c043.bounded_affine_intersection_closure.v1",
        "dimension": dimension,
        "encoding_length": encoding_length,
        "capability_exponent": capability_exponent,
        "closure_limit": closure_limit,
        "p_vs_np": "OPEN",
    }
    try:
        factors = translate(cnf, coordinate_rows, coordinate_constants, dimension, meter)
        coefficients = build_union_coefficients(factors, dimension, meter)
        coefficient_payload = [
            {
                "space": [[m, r] for m, r in space],
                "dimension": subspace_dimension(space, dimension),
                "coefficient": coefficient,
            }
            for space, coefficient in sorted(coefficients.items())
        ]
        union_size, root_trace = covered_count(coefficients, (), dimension, meter)
        total_points = 1 << dimension
        common = {
            **base,
            "factor_count": len(factors),
            "coefficient_terms": coefficient_payload,
            "union_size": union_size,
            "total_points": total_points,
            "work": meter.work,
            "intersection_calls": meter.intersections,
            "max_coefficient_terms": meter.max_terms,
        }
        if union_size == total_points:
            certificate = {
                **common,
                "status": "UNSAT",
                "certificate": "EXACT_SIGNED_INTERSECTION_COVER",
                "root_count_trace": root_trace,
            }
            meter.certificate(certificate)
            certificate["integrity_sha256"] = digest(certificate)
            return certificate
        if not 0 <= union_size < total_points:
            raise AssertionError("signed union count outside ambient size")

        prefix: Subspace = ()
        witness: dict[int, bool] = {}
        witness_trace: list[dict[str, Any]] = []
        for variable in range(1, dimension + 1):
            chosen: int | None = None
            for bit in (0, 1):
                condition, _ = rref(prefix + ((1 << (variable - 1), bit),), dimension, meter)
                assert condition is not None
                covered, count_trace = covered_count(coefficients, condition, dimension, meter)
                cell_size = 1 << (dimension - variable)
                if covered < cell_size:
                    chosen = bit
                    witness_trace.append(
                        {
                            "variable": variable,
                            "bit": bit,
                            "covered": covered,
                            "cell_size": cell_size,
                            "count_trace": count_trace,
                        }
                    )
                    prefix = condition
                    witness[variable] = bool(bit)
                    break
            if chosen is None:
                raise AssertionError("conditional counting failed to find uncovered child")

        assert not any(satisfies_space(factor["space"], witness) for factor in factors)
        certificate = {
            **common,
            "status": "SAT",
            "witness": {str(v): value for v, value in witness.items()},
            "witness_trace": witness_trace,
        }
        meter.certificate(certificate)
        certificate["integrity_sha256"] = digest(certificate)
        return certificate
    except RuntimeError as error:
        return {
            **base,
            "status": str(error),
            "work": meter.work,
            "intersection_calls": meter.intersections,
            "max_coefficient_terms": meter.max_terms,
            "p_vs_np": "OPEN",
        }


def verify(
    cnf: tuple[Clause, ...],
    coordinate_rows: dict[int, int],
    coordinate_constants: dict[int, int],
    dimension: int,
    certificate: dict[str, Any],
) -> bool:
    status = certificate.get("status", "")
    replay = solve(
        cnf,
        coordinate_rows,
        coordinate_constants,
        dimension,
        capability_exponent=int(certificate.get("capability_exponent", 2)),
        absolute_closure_limit=int(certificate.get("closure_limit", 200_000)),
        work_limit=20_000_000,
        certificate_limit=20_000_000,
    )
    if status.startswith("OPEN_"):
        return replay.get("status") == status
    return replay == certificate


def eval_cnf(
    cnf: tuple[Clause, ...],
    coordinate_rows: dict[int, int],
    coordinate_constants: dict[int, int],
    coordinate_assignment: dict[int, bool],
) -> bool:
    packed = sum(1 << (v - 1) for v, value in coordinate_assignment.items() if value)
    original = {
        variable: bool(
            (coordinate_constants.get(variable, 0) & 1)
            ^ ((mask & packed).bit_count() & 1)
        )
        for variable, mask in coordinate_rows.items()
    }
    return all(any(original[abs(lit)] == (lit > 0) for lit in clause) for clause in cnf)


def brute(
    cnf: tuple[Clause, ...],
    coordinate_rows: dict[int, int],
    coordinate_constants: dict[int, int],
    dimension: int,
) -> bool:
    for bits in itertools.product((False, True), repeat=dimension):
        assignment = {i + 1: bits[i] for i in range(dimension)}
        if eval_cnf(cnf, coordinate_rows, coordinate_constants, assignment):
            return True
    return False


def prefix_clause(pattern: tuple[int, ...]) -> Clause:
    return tuple((i + 1 if bit == 0 else -(i + 1)) for i, bit in enumerate(pattern))


def hard_image(n: int) -> tuple[tuple[Clause, ...], dict[int, int], dict[int, int]]:
    clauses: list[Clause] = []
    for i in range(1, n + 1):
        for shift in (1, 3, 5):
            a = i
            b = ((i + shift - 1) % n) + 1
            c = ((i + 2 * shift - 1) % n) + 1
            clauses.append((a, -b, c))
    rows = {i: 1 << (i - 1) for i in range(1, n + 1)}
    constants = {i: 0 for i in rows}
    return tuple(clauses), rows, constants


def audit(seed: int = 430043) -> dict[str, Any]:
    rng = random.Random(seed)
    random_cases = 300
    mismatch = verification_failures = open_cases = exact_cases = 0

    for _ in range(random_cases):
        d = rng.randint(1, 8)
        rows = {i: 1 << (i - 1) for i in range(1, d + 1)}
        constants = {i: 0 for i in rows}
        clause_count = rng.randint(0, 8)
        clauses: list[Clause] = []
        for _j in range(clause_count):
            width = rng.randint(1, min(3, d))
            variables = rng.sample(range(1, d + 1), width)
            clauses.append(tuple(v if rng.getrandbits(1) else -v for v in variables))
        cnf = tuple(clauses)
        certificate = solve(
            cnf,
            rows,
            constants,
            d,
            capability_exponent=4,
            absolute_closure_limit=10_000,
            work_limit=5_000_000,
            certificate_limit=10_000_000,
        )
        truth = brute(cnf, rows, constants, d)
        if certificate["status"].startswith("OPEN_"):
            open_cases += 1
            continue
        exact_cases += 1
        if (certificate["status"] == "SAT") != truth:
            mismatch += 1
        if not verify(cnf, rows, constants, d, certificate):
            verification_failures += 1

    d = 64
    rows = {i: 1 << (i - 1) for i in range(1, d + 1)}
    constants = {i: 0 for i in rows}
    crossing_cnf = ((1,), (2,))
    crossing = solve(crossing_cnf, rows, constants, d)
    assert crossing["status"] == "SAT"
    assert crossing["max_coefficient_terms"] == 3
    assert verify(crossing_cnf, rows, constants, d, crossing)

    cover_cnf = tuple(prefix_clause(pattern) for pattern in ((0, 0), (0, 1), (1, 0), (1, 1)))
    cover = solve(cover_cnf, rows, constants, d)
    assert cover["status"] == "UNSAT"
    assert cover["union_size"] == 1 << d
    assert verify(cover_cnf, rows, constants, d, cover)

    repeated = tuple((1,) if i % 2 == 0 else (2,) for i in range(200))
    repeated_cert = solve(repeated, rows, constants, d)
    assert repeated_cert["status"] == "SAT"
    assert repeated_cert["max_coefficient_terms"] <= 3

    hard_cnf, hard_rows, hard_constants = hard_image(24)
    hard = solve(
        hard_cnf,
        hard_rows,
        hard_constants,
        24,
        capability_exponent=2,
        absolute_closure_limit=20_000,
        work_limit=20_000_000,
    )
    assert hard["status"] == "OPEN_INTERSECTION_CLOSURE"

    tiny = solve(
        crossing_cnf,
        rows,
        constants,
        d,
        capability_exponent=2,
        absolute_closure_limit=1,
    )
    assert tiny["status"] == "OPEN_INTERSECTION_CLOSURE"

    corrupt = json.loads(json.dumps(cover))
    corrupt["union_size"] -= 1
    assert not verify(cover_cnf, rows, constants, d, corrupt)

    result = {
        "artifact_id": "C043-JANUS-BOUNDED-AFFINE-INTERSECTION-CLOSURE",
        "status": "PASS",
        "p_vs_np": "OPEN",
        "seed": seed,
        "random_cases": random_cases,
        "exact_cases": exact_cases,
        "open_cases": open_cases,
        "mismatches": mismatch,
        "verification_failures": verification_failures,
        "constructive_theorem": (
            "Affine-coordinate CNF is polynomially decidable whenever the deterministic "
            "signed inclusion-exclusion construction has polynomially bounded distinct "
            "nonempty intersection support. Exact union counting yields UNSAT covers; "
            "conditional counts recover a SAT witness."
        ),
        "crossing_sat_control": {
            "dimension": d,
            "coefficient_terms": crossing["max_coefficient_terms"],
            "status": crossing["status"],
        },
        "crossing_unsat_cover": {
            "dimension": d,
            "input_factors": 4,
            "status": cover["status"],
        },
        "repeated_crossing_compression": {
            "input_factors": len(repeated),
            "coefficient_terms": repeated_cert["max_coefficient_terms"],
            "status": repeated_cert["status"],
        },
        "nand3_neq_control": hard["status"],
        "budget_control": tiny["status"],
        "corrupt_certificate_control": "REJECTED",
        "new_gate": "POLYNOMIAL_DECOMPOSITION_BEYOND_BOUNDED_INTERSECTION_SUPPORT",
        "claim_boundary": (
            "Only arrangements whose charged signed intersection support remains within "
            "one fixed polynomial capability. Exponential intersection closure, arbitrary "
            "3-CNF, unrestricted Horn-affine composition, and P versus NP remain open."
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
        assert result["mismatches"] == 0
        assert result["verification_failures"] == 0


if __name__ == "__main__":
    main()
