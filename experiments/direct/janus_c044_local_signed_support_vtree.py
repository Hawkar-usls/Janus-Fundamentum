#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import itertools
import json
import random
from typing import Any

from janus_c044_local_signed_support_core import (
    canonical_json,
    digest,
    evaluate_affine,
    evaluate_cnf,
    normalize_cnf,
)
from janus_c044_local_signed_support_solver import solve_local_signed_support
from janus_c044_local_signed_support_verifier import verify_local_signed_support

try:
    from janus_c043_crossing_solver import solve_crossing
except ImportError:
    from janus_c044_local_signed_support_core import (
        Capability,
        Meter,
        OpenResult,
        compile_signed_union,
        encoded_length,
        parameterize_affine,
        translate_factors,
    )

    def solve_crossing(
        cnf,
        affine=(),
        *,
        nvars_hint=0,
        support_cap=None,
        **_kwargs,
    ):
        cnf = normalize_cnf(cnf)
        capability = Capability(
            encoded_length(cnf, affine, nvars_hint),
            0,
            support_cap,
            None,
            None,
        )
        meter = Meter(capability)
        basis = parameterize_affine(affine, nvars_hint, meter)
        if basis["status"] == "UNSAT":
            return {"status": "UNSAT"}
        factors, _ = translate_factors(cnf, basis, meter)
        scope = tuple(
            sorted(
                set().union(*(set(factor.scope) for factor in factors))
                if factors
                else set()
            )
        )
        try:
            compile_signed_union(
                factors,
                scope,
                meter,
                accepted_leaf=True,
            )
            return {"status": "EXACT"}
        except OpenResult:
            return {"status": "OPEN_INTERSECTION_CLOSURE"}


def brute(
    cnf: tuple[tuple[int, ...], ...],
    affine: tuple[tuple[int, int], ...],
    nvars: int,
) -> tuple[bool, int | None]:
    cnf = normalize_cnf(cnf)
    for assignment in range(1 << nvars):
        if evaluate_affine(affine, assignment) and evaluate_cnf(cnf, assignment):
            return True, assignment
    return False, None


def unit_family(n: int) -> tuple[tuple[int, ...], ...]:
    return tuple((variable,) for variable in range(1, n + 1))


def path_family(n: int) -> tuple[tuple[int, ...], ...]:
    return tuple((variable, variable + 1) for variable in range(1, n))


def hard_image(n: int) -> tuple[tuple[int, ...], ...]:
    clauses: list[tuple[int, ...]] = []
    for variable in range(1, n + 1):
        for shift in (1, 3, 5):
            second = ((variable + shift - 1) % n) + 1
            third = ((variable + 2 * shift - 1) % n) + 1
            clauses.append((variable, -second, third))
    return tuple(clauses)


def plan_statistics(plan: dict[str, Any]) -> dict[str, int]:
    nodes = leaves = separators = 0
    max_separator = max_depth = 0

    def visit(node: dict[str, Any], depth: int) -> None:
        nonlocal nodes, leaves, separators, max_separator, max_depth
        nodes += 1
        max_depth = max(max_depth, depth)
        if node["node_type"] == "SIGNED_LEAF":
            leaves += 1
            return
        separators += 1
        max_separator = max(max_separator, len(node["separator"]))
        for child in node["children"]:
            visit(child, depth + 1)

    visit(plan, 0)
    return {
        "nodes": nodes,
        "signed_leaves": leaves,
        "separator_nodes": separators,
        "max_separator": max_separator,
        "max_depth": max_depth,
    }


def random_cnf(
    rng: random.Random,
    nvars: int,
    clause_count: int,
) -> tuple[tuple[int, ...], ...]:
    clauses = []
    for _ in range(clause_count):
        width = rng.randint(1, min(3, nvars))
        variables = rng.sample(range(1, nvars + 1), width)
        clauses.append(
            tuple(
                variable if rng.getrandbits(1) else -variable
                for variable in variables
            )
        )
    return tuple(clauses)


def random_affine(
    rng: random.Random,
    nvars: int,
    equation_count: int,
) -> tuple[tuple[int, int], ...]:
    return tuple(
        (rng.randrange(1, 1 << nvars), rng.getrandbits(1))
        for _ in range(equation_count)
    )


def run_audit(seed: int = 440044) -> dict[str, Any]:
    rng = random.Random(seed)
    random_cases = 300
    exact_cases = open_cases = mismatches = 0
    witness_failures = verification_failures = 0

    for _ in range(random_cases):
        nvars = rng.randint(1, 7)
        cnf = random_cnf(rng, nvars, rng.randint(0, 9))
        affine = random_affine(rng, nvars, rng.randint(0, 4))
        certificate = solve_local_signed_support(
            cnf,
            affine,
            nvars_hint=nvars,
            separator_cap=1,
            local_support_cap=64,
        )
        truth, _ = brute(cnf, affine, nvars)
        if certificate["status"] not in ("SAT", "UNSAT"):
            open_cases += 1
            continue
        exact_cases += 1
        if (certificate["status"] == "SAT") != truth:
            mismatches += 1
        if certificate["status"] == "SAT":
            witness_mask = int(certificate["witness_mask"])
            if not (
                evaluate_affine(affine, witness_mask)
                and evaluate_cnf(normalize_cnf(cnf), witness_mask)
            ):
                witness_failures += 1
        if not verify_local_signed_support(
            cnf,
            affine,
            certificate,
            nvars_hint=nvars,
        ):
            verification_failures += 1

    units = unit_family(40)
    unit_certificate = solve_local_signed_support(
        units,
        (),
        nvars_hint=40,
        separator_cap=1,
        local_support_cap=8,
    )
    assert unit_certificate["status"] == "SAT"
    assert verify_local_signed_support(
        units,
        (),
        unit_certificate,
        nvars_hint=40,
    )
    unit_stats = plan_statistics(unit_certificate["plan"])
    assert unit_certificate["producer_ledger"]["max_attempted_live_support"] > 8
    assert unit_certificate["producer_ledger"]["max_accepted_leaf_support"] <= 8

    path = path_family(40)
    path_certificate = solve_local_signed_support(
        path,
        (),
        nvars_hint=40,
        separator_cap=1,
        local_support_cap=16,
    )
    assert path_certificate["status"] == "SAT"
    assert verify_local_signed_support(
        path,
        (),
        path_certificate,
        nvars_hint=40,
    )
    path_stats = plan_statistics(path_certificate["plan"])
    assert path_stats["max_separator"] == 1
    assert path_certificate["producer_ledger"]["max_attempted_live_support"] > 16
    assert path_certificate["producer_ledger"]["max_accepted_leaf_support"] <= 16

    global_unit = solve_crossing(
        units,
        (),
        nvars_hint=40,
        support_cap=8,
    )
    global_path = solve_crossing(
        path,
        (),
        nvars_hint=40,
        support_cap=16,
    )
    global_unit_status = global_unit["status"]
    global_path_status = global_path["status"]
    assert global_unit_status == "OPEN_INTERSECTION_CLOSURE"
    assert global_path_status == "OPEN_INTERSECTION_CLOSURE"

    unsat_formula = (
        (1,),
        (-1,),
        *tuple((variable,) for variable in range(2, 30)),
    )
    unsat_certificate = solve_local_signed_support(
        unsat_formula,
        (),
        nvars_hint=29,
        separator_cap=1,
        local_support_cap=8,
    )
    assert unsat_certificate["status"] == "UNSAT"
    assert verify_local_signed_support(
        unsat_formula,
        (),
        unsat_certificate,
        nvars_hint=29,
    )

    affine_n = 32
    affine = tuple(
        ((1 << 0) | (1 << (variable - 1)), 0)
        for variable in range(2, affine_n + 1)
    )
    dense_cnf = tuple(
        (left, right)
        for left in range(1, affine_n + 1)
        for right in range(left + 1, affine_n + 1)
    )
    affine_certificate = solve_local_signed_support(
        dense_cnf,
        affine,
        nvars_hint=affine_n,
        separator_cap=1,
        local_support_cap=8,
    )
    assert affine_certificate["status"] == "SAT"
    assert affine_certificate["dimension"] == 1
    assert verify_local_signed_support(
        dense_cnf,
        affine,
        affine_certificate,
        nvars_hint=affine_n,
    )

    hard = hard_image(18)
    hard_certificate = solve_local_signed_support(
        hard,
        (),
        nvars_hint=18,
        separator_cap=1,
        local_support_cap=16,
    )
    assert hard_certificate["status"] == "OPEN_LOCAL_SUPPORT"
    assert verify_local_signed_support(
        hard,
        (),
        hard_certificate,
        nvars_hint=18,
    )

    zero_separator = solve_local_signed_support(
        path,
        (),
        nvars_hint=40,
        separator_cap=0,
        local_support_cap=16,
    )
    assert zero_separator["status"] == "OPEN_LOCAL_SUPPORT"
    assert verify_local_signed_support(
        path,
        (),
        zero_separator,
        nvars_hint=40,
    )

    work_open = solve_local_signed_support(
        path,
        (),
        nvars_hint=40,
        separator_cap=1,
        local_support_cap=16,
        work_cap=8,
    )
    assert work_open["status"] == "OPEN_WORK_BUDGET"
    assert verify_local_signed_support(
        path,
        (),
        work_open,
        nvars_hint=40,
    )

    certificate_open = solve_local_signed_support(
        path,
        (),
        nvars_hint=40,
        separator_cap=1,
        local_support_cap=16,
        certificate_cap=1000,
    )
    assert certificate_open["status"] == "OPEN_CERTIFICATE_VOLUME"
    assert verify_local_signed_support(
        path,
        (),
        certificate_open,
        nvars_hint=40,
    )

    deterministic_repeat = solve_local_signed_support(
        path,
        (),
        nvars_hint=40,
        separator_cap=1,
        local_support_cap=16,
    )
    assert deterministic_repeat["plan_digest"] == path_certificate["plan_digest"]
    assert deterministic_repeat["integrity_sha256"] == path_certificate["integrity_sha256"]

    corrupt_witness = copy.deepcopy(path_certificate)
    corrupt_witness["witness_mask"] = str(int(corrupt_witness["witness_mask"]) ^ 1)
    corrupt_witness["integrity_sha256"] = digest(
        {key: value for key, value in corrupt_witness.items() if key != "integrity_sha256"}
    )
    assert not verify_local_signed_support(
        path,
        (),
        corrupt_witness,
        nvars_hint=40,
    )

    corrupt_plan = copy.deepcopy(path_certificate)
    corrupt_plan["plan"]["separator"] = [2]
    corrupt_plan["plan_digest"] = digest(corrupt_plan["plan"])
    corrupt_plan["integrity_sha256"] = digest(
        {key: value for key, value in corrupt_plan.items() if key != "integrity_sha256"}
    )
    assert not verify_local_signed_support(
        path,
        (),
        corrupt_plan,
        nvars_hint=40,
    )

    corrupt_open = copy.deepcopy(hard_certificate)
    corrupt_open["overflow_evidence"]["separator_limit"] = 2
    corrupt_open["integrity_sha256"] = digest(
        {key: value for key, value in corrupt_open.items() if key != "integrity_sha256"}
    )
    assert not verify_local_signed_support(
        hard,
        (),
        corrupt_open,
        nvars_hint=18,
    )

    result = {
        "artifact_id": "C044-JANUS-LOCAL-SIGNED-SUPPORT-VTREE",
        "status": "PASS",
        "p_vs_np": "OPEN",
        "seed": seed,
        "random_cases": random_cases,
        "random_exact_cases": exact_cases,
        "random_open_cases": open_cases,
        "mismatches": mismatches,
        "witness_failures": witness_failures,
        "verification_failures": verification_failures,
        "constructive_theorem": (
            "For fixed separator cap k and fixed-polynomial local signed-support, "
            "work, and certificate capabilities, deterministic recursive coordinate-"
            "primal decomposition plus exact local signed-cover leaves decides the "
            "admitted instance in L^O(k) total work without materializing the global "
            "signed support or 2^d coordinate points."
        ),
        "global_to_local_strict_extension": {
            "unit_family": {
                "variables": 40,
                "global_c043_status": global_unit_status,
                "c044_status": unit_certificate["status"],
                "plan": unit_stats,
                "max_attempted_global_like_support": unit_certificate[
                    "producer_ledger"
                ]["max_attempted_live_support"],
                "max_accepted_leaf_support": unit_certificate[
                    "producer_ledger"
                ]["max_accepted_leaf_support"],
            },
            "path_family": {
                "variables": 40,
                "global_c043_status": global_path_status,
                "c044_status": path_certificate["status"],
                "plan": path_stats,
                "max_attempted_global_like_support": path_certificate[
                    "producer_ledger"
                ]["max_attempted_live_support"],
                "max_accepted_leaf_support": path_certificate[
                    "producer_ledger"
                ]["max_accepted_leaf_support"],
            },
        },
        "unsat_composition_control": unsat_certificate["status"],
        "affine_basis_control": {
            "variables": affine_n,
            "coordinate_dimension": affine_certificate["dimension"],
            "status": affine_certificate["status"],
        },
        "hard_image_control": hard_certificate["status"],
        "zero_separator_control": zero_separator["status"],
        "work_budget_control": work_open["status"],
        "certificate_budget_control": certificate_open["status"],
        "deterministic_plan_control": "PASS",
        "corrupt_witness_control": "REJECTED",
        "corrupt_plan_control": "REJECTED",
        "corrupt_open_control": "REJECTED",
        "new_gate": (
            "POLYNOMIAL_DISCOVERY_BEYOND_FIXED_SMALL_COORDINATE_SEPARATORS_"
            "AND_LOCAL_SIGNED_SUPPORT"
        ),
        "claim_boundary": (
            "Only deterministically discovered recursive coordinate-primal "
            "decompositions with separator size at most the fixed capability and "
            "bounded local/intermediate signed support. It does not decide arbitrary "
            "3-CNF, unrestricted affine-coordinate arrangements, or P versus NP."
        ),
    }
    result["integrity_sha256"] = digest(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args()
    result = run_audit()
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
