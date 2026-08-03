#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from typing import Any

import janus_c042_bounded_affine_intersection_support_core as core

Clause = tuple[int, ...]


def canon(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def sha(obj: Any) -> str:
    return hashlib.sha256(canon(obj).encode()).hexdigest()


def encoded_length(cnf: tuple[Clause, ...], rows: dict[int, int], dimension: int) -> int:
    return max(2, dimension + len(cnf) + sum(map(len, cnf)) + sum(m.bit_count() for m in rows.values()))


def cap(absolute: int, length: int, exponent: int) -> int:
    if absolute < 0 or exponent < 0:
        raise ValueError("negative capability")
    return min(absolute, length**exponent)


def solve(
    cnf: tuple[Clause, ...],
    rows: dict[int, int],
    constants: dict[int, int],
    dimension: int,
    *,
    support_exp: int = 2,
    work_exp: int = 4,
    cert_exp: int = 4,
    absolute_support: int = 200_000,
    absolute_work: int = 20_000_000,
    absolute_certificate: int = 20_000_000,
) -> dict[str, Any]:
    length = encoded_length(cnf, rows, dimension)
    support_limit = cap(absolute_support, length, support_exp)
    work_limit = cap(absolute_work, length, work_exp)
    cert_limit = cap(absolute_certificate, length, cert_exp)
    budgets = {
        "support_exp": support_exp,
        "work_exp": work_exp,
        "cert_exp": cert_exp,
        "absolute_support": absolute_support,
        "absolute_work": absolute_work,
        "absolute_certificate": absolute_certificate,
        "effective_support": support_limit,
        "effective_work": work_limit,
        "effective_certificate": cert_limit,
    }

    result = core.solve(
        cnf,
        rows,
        constants,
        dimension,
        capability_exponent=support_exp,
        absolute_closure_limit=support_limit,
        work_limit=work_limit,
        certificate_limit=cert_limit,
    )
    status = str(result.get("status", ""))
    terms = result.get("coefficient_terms", [])
    bit_lengths = [max(1, abs(int(t["coefficient"])).bit_length()) for t in terms]
    factors = int(result.get("factor_count", len(cnf)))
    accounting = {
        "factor_count": factors,
        "nonzero_terms": len(terms),
        "max_nonzero_terms": int(result.get("max_coefficient_terms", 0)),
        "transient_support_bound": int(result.get("max_coefficient_terms", 0)) + 1,
        "max_coefficient_bits": max(bit_lengths, default=0),
        "total_coefficient_bits": sum(bit_lengths),
        "proved_coefficient_bit_bound": factors + 1,
        "work_units": int(result.get("work", 0)),
        "intersection_calls": int(result.get("intersection_calls", 0)),
    }
    if accounting["max_coefficient_bits"] > factors + 1:
        raise AssertionError("coefficient bit bound")
    if not status.startswith("OPEN_"):
        if accounting["work_units"] > work_limit:
            raise AssertionError("accepted beyond work budget")
        if accounting["max_nonzero_terms"] > support_limit:
            raise AssertionError("accepted beyond support budget")

    envelope: dict[str, Any] = {
        "schema": "janus.c042.bounded_affine_intersection_support.v1",
        "status": status,
        "dimension": dimension,
        "encoding_length": length,
        "budgets": budgets,
        "accounting": accounting,
        "core_result": result,
        "p_vs_np": "OPEN",
    }
    size = len(canon(envelope).encode())
    if not status.startswith("OPEN_") and size > cert_limit:
        envelope = {
            "schema": "janus.c042.bounded_affine_intersection_support.v1",
            "status": "OPEN_CERTIFICATE_VOLUME",
            "dimension": dimension,
            "encoding_length": length,
            "budgets": budgets,
            "accounting": accounting,
            "core_status": status,
            "core_digest": sha(result),
            "observed_envelope_bytes": size,
            "p_vs_np": "OPEN",
        }
    envelope["integrity_sha256"] = sha(envelope)
    return envelope


def verify(cnf: tuple[Clause, ...], rows: dict[int, int], constants: dict[int, int], dimension: int, cert: dict[str, Any]) -> bool:
    claimed = cert.get("integrity_sha256")
    if not isinstance(claimed, str):
        return False
    body = dict(cert)
    body.pop("integrity_sha256", None)
    if sha(body) != claimed:
        return False
    b = cert.get("budgets")
    if not isinstance(b, dict):
        return False
    names = ("support_exp", "work_exp", "cert_exp", "absolute_support", "absolute_work", "absolute_certificate")
    if any(name not in b for name in names):
        return False
    replay = solve(
        cnf,
        rows,
        constants,
        dimension,
        support_exp=int(b["support_exp"]),
        work_exp=int(b["work_exp"]),
        cert_exp=int(b["cert_exp"]),
        absolute_support=int(b["absolute_support"]),
        absolute_work=int(b["absolute_work"]),
        absolute_certificate=int(b["absolute_certificate"]),
    )
    return replay == cert


def audit() -> dict[str, Any]:
    base = core.audit()
    assert base["status"] == "PASS" and base["mismatches"] == 0 and base["verification_failures"] == 0

    d = 64
    rows = {i: 1 << (i - 1) for i in range(1, d + 1)}
    constants = {i: 0 for i in rows}
    crossing_cnf = ((1,), (2,))
    crossing = solve(crossing_cnf, rows, constants, d)
    assert crossing["status"] == "SAT"
    assert crossing["accounting"]["max_nonzero_terms"] == 3
    assert verify(crossing_cnf, rows, constants, d, crossing)

    cover_cnf = tuple(core.prefix_clause(p) for p in ((0, 0), (0, 1), (1, 0), (1, 1)))
    cover = solve(cover_cnf, rows, constants, d)
    assert cover["status"] == "UNSAT" and verify(cover_cnf, rows, constants, d, cover)

    repeated = tuple((1,) if i % 2 == 0 else (2,) for i in range(200))
    repeated_cert = solve(repeated, rows, constants, d)
    assert repeated_cert["status"] == "SAT"
    assert repeated_cert["accounting"]["max_nonzero_terms"] <= 3
    assert verify(repeated, rows, constants, d, repeated_cert)

    hard_cnf, hard_rows, hard_constants = core.hard_image(24)
    hard = solve(hard_cnf, hard_rows, hard_constants, 24, absolute_support=20_000)
    assert hard["status"] == "OPEN_INTERSECTION_CLOSURE"
    assert verify(hard_cnf, hard_rows, hard_constants, 24, hard)

    work_open = solve(crossing_cnf, rows, constants, d, absolute_work=1)
    assert work_open["status"] == "OPEN_WORK_BUDGET"
    assert verify(crossing_cnf, rows, constants, d, work_open)

    cert_open = solve(crossing_cnf, rows, constants, d, absolute_certificate=128)
    assert cert_open["status"] == "OPEN_CERTIFICATE_VOLUME"
    assert verify(crossing_cnf, rows, constants, d, cert_open)

    corrupt = json.loads(json.dumps(cover))
    corrupt["accounting"]["work_units"] += 1
    assert not verify(cover_cnf, rows, constants, d, corrupt)
    budget_corrupt = json.loads(json.dumps(work_open))
    budget_corrupt["budgets"]["absolute_work"] = 2
    assert not verify(crossing_cnf, rows, constants, d, budget_corrupt)

    result = {
        "artifact_id": "C042-JANUS-BOUNDED-AFFINE-INTERSECTION-SUPPORT",
        "status": "PASS",
        "p_vs_np": "OPEN",
        "core_random_cases": base["random_cases"],
        "core_exact_cases": base["exact_cases"],
        "core_open_cases": base["open_cases"],
        "mismatches": base["mismatches"],
        "verification_failures": base["verification_failures"],
        "crossing_dimension": d,
        "crossing_terms": crossing["accounting"]["max_nonzero_terms"],
        "crossing_sat": crossing["status"],
        "crossing_unsat": cover["status"],
        "repeated_factors": len(repeated),
        "repeated_terms": repeated_cert["accounting"]["max_nonzero_terms"],
        "nand3_neq": hard["status"],
        "work_budget": work_open["status"],
        "certificate_budget": cert_open["status"],
        "corrupt_certificate": "REJECTED",
        "corrupt_budget": "REJECTED",
        "new_gate": "POLYNOMIAL_DECOMPOSITION_BEYOND_BOUNDED_SIGNED_INTERSECTION_SUPPORT",
    }
    result["integrity_sha256"] = sha(result)
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
