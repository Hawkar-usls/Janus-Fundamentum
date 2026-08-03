#!/usr/bin/env python3
from janus_c042_affine_core import *
from janus_c042_laminar_solver import decide
from janus_c042_laminar_verifier import verify_certificate, verify_certificate_report

def brute(cnf: CNF, affine: tuple[Equation, ...], nvars_hint: int = 0) -> tuple[bool, int | None]:
    cnf = normalize_cnf(cnf)
    nvars = max(nvars_hint, max(variables_in_cnf(cnf) | variables_in_affine(affine), default=0))
    for assignment_mask in range(1 << nvars):
        if evaluate_equations(affine, assignment_mask) and evaluate_cnf(cnf, assignment_mask):
            return True, assignment_mask
    return False, None


def prefix_clause(pattern: tuple[int, ...]) -> Clause:
    return tuple(index if bit == 0 else -index for index, bit in enumerate(pattern, start=1))


def random_laminar_formula(rng: random.Random, dimension: int, count: int) -> CNF:
    patterns = {
        tuple(rng.getrandbits(1) for _ in range(rng.randint(0, dimension)))
        for _ in range(count)
    }
    return normalize_cnf(tuple(prefix_clause(pattern) for pattern in patterns))


def c023_hard_image(n: int) -> tuple[CNF, tuple[Equation, ...], int]:
    if n < 6:
        raise ValueError("n must be at least 6")
    source: list[Clause] = [(1, -2, 3), (1, 4, -5)]
    for index in range(2, n - 1):
        literals = (index, (index % n) + 1, ((index + 2) % n) + 1)
        source.append(tuple(literal if (index + offset) % 2 else -literal
                            for offset, literal in enumerate(literals)))
    horn = []
    for clause in source:
        indicators = [n + abs(literal) if literal > 0 else abs(literal) for literal in clause]
        horn.append(tuple(-indicator for indicator in indicators))
    affine = tuple(
        ((1 << (variable - 1)) | (1 << (n + variable - 1)), 1)
        for variable in range(1, n + 1)
    )
    return normalize_cnf(tuple(horn)), affine, 2 * n


def hidden_large_clause_conflict(n: int) -> tuple[CNF, tuple[Equation, ...], int]:
    cnf = (tuple(range(1, n + 1)), tuple(-variable for variable in range(1, n + 1)))
    affine = tuple(((1 << 0) | (1 << (variable - 1)), 0) for variable in range(2, n + 1))
    return normalize_cnf(cnf), affine, n


def audit(seed: int = 420042) -> dict[str, Any]:
    rng = random.Random(seed)
    random_cases = 120
    mismatches = witness_failures = verification_failures = 0
    exact = opened = 0
    max_verifier_work = 0
    for _ in range(random_cases):
        dimension = rng.randint(0, 8)
        cnf = random_laminar_formula(rng, dimension, rng.randint(0, 14))
        certificate = decide(cnf, (), nvars_hint=dimension)
        truth, _ = brute(cnf, (), dimension)
        if certificate["status"].startswith("OPEN"):
            opened += 1
            continue
        exact += 1
        mismatches += int((certificate["status"] == "SAT") != truth)
        verified, verifier_ledger = verify_certificate_report(cnf, (), certificate, nvars_hint=dimension)
        verification_failures += int(not verified)
        max_verifier_work = max(max_verifier_work, int(verifier_ledger["total_work_units"]))
        if certificate["status"] == "SAT":
            witness_mask = int(certificate["witness_mask"])
            witness_failures += int(not evaluate_cnf(cnf, witness_mask))

    dimension = 128
    high_sat = decide((prefix_clause((0,)),), (), nvars_hint=dimension)
    high_unsat = decide((prefix_clause((0,)), prefix_clause((1,))), (), nvars_hint=dimension)
    nested_formula = tuple(prefix_clause(tuple(0 for _ in range(length))) for length in range(1, 25))
    nested = decide(nested_formula, (), nvars_hint=dimension)
    tight_nested = decide(nested_formula, (), nvars_hint=dimension, budget_cap=2_000)
    hidden_cnf, hidden_affine, hidden_n = hidden_large_clause_conflict(128)
    hidden = decide(hidden_cnf, hidden_affine, nvars_hint=hidden_n)

    hard_controls = {}
    for n in (24, 32, 48):
        hard_cnf, hard_affine, hard_n = c023_hard_image(n)
        hard_controls[str(n)] = decide(hard_cnf, hard_affine, nvars_hint=hard_n)["status"]

    crossing = decide(((1,), (2,)), (), nvars_hint=2)
    affine_bad = decide((), ((1, 0), (1, 1)), nvars_hint=1)
    corrupt = json.loads(json.dumps(high_sat))
    corrupt["witness_mask"] = str(int(corrupt["witness_mask"]) ^ 1)

    high_sat_ok, high_sat_verifier = verify_certificate_report(
        (prefix_clause((0,)),), (), high_sat, nvars_hint=dimension
    )
    high_unsat_ok, high_unsat_verifier = verify_certificate_report(
        (prefix_clause((0,)), prefix_clause((1,))), (), high_unsat, nvars_hint=dimension
    )
    nested_ok, nested_verifier = verify_certificate_report(
        nested_formula, (), nested, nvars_hint=dimension
    )
    tight_nested_ok, tight_nested_verifier = verify_certificate_report(
        nested_formula, (), tight_nested, nvars_hint=dimension
    )
    hidden_ok, hidden_verifier = verify_certificate_report(
        hidden_cnf, hidden_affine, hidden, nvars_hint=hidden_n
    )
    max_verifier_work = max(
        max_verifier_work,
        int(high_sat_verifier["total_work_units"]),
        int(high_unsat_verifier["total_work_units"]),
        int(nested_verifier["total_work_units"]),
        int(tight_nested_verifier["total_work_units"]),
        int(hidden_verifier["total_work_units"]),
    )
    assert high_sat["status"] == "SAT" and high_sat_ok
    assert high_unsat["status"] == "UNSAT" and high_unsat_ok
    assert nested["status"] == "SAT" and len(nested["maximal_indices"]) == 1 and nested_ok
    assert tight_nested["status"] == "OPEN_BUDGET" and tight_nested_ok
    assert hidden["status"] == "UNSAT" and hidden_ok
    assert all(status == "OPEN_NON_LAMINAR" for status in hard_controls.values())
    assert crossing["status"] == "OPEN_NON_LAMINAR" and verify_certificate(((1,), (2,)), (), crossing, nvars_hint=2)
    assert affine_bad["status"] == "UNSAT" and affine_bad["reason"] == "AFFINE_CONTRADICTION"
    assert verify_certificate((), ((1, 0), (1, 1)), affine_bad, nvars_hint=1)
    assert not verify_certificate((prefix_clause((0,)),), (), corrupt, nvars_hint=dimension)

    result = {
        "artifact_id": "C042-JANUS-LAMINAR-AFFINE-FORBIDDEN-COVER",
        "status": "PASS",
        "p_vs_np": "OPEN",
        "seed": seed,
        "schema": SCHEMA,
        "budget_exponent": BUDGET_EXPONENT,
        "budget_multiplier": BUDGET_MULTIPLIER,
        "random_cases": random_cases,
        "exact": exact,
        "open": opened,
        "mismatches": mismatches,
        "witness_failures": witness_failures,
        "verification_failures": verification_failures,
        "max_verifier_work_units": max_verifier_work,
        "constructive_theorem": (
            "CNF satisfiability inside an input affine GF(2) space is polynomially decidable with "
            "independently replayable SAT/UNSAT evidence when clause-falsifying affine subspaces are laminar."
        ),
        "basis_construction": "charged provenance-carrying Gaussian elimination",
        "high_dimension_sat": {"dimension": dimension, "status": high_sat["status"]},
        "high_dimension_unsat_cover": {"dimension": dimension, "status": high_unsat["status"]},
        "hidden_large_clause_conflict": {"variables": hidden_n, "status": hidden["status"]},
        "small_final_large_intermediate": {
            "input_factors": len(nested_formula),
            "maximal_factors": len(nested["maximal_indices"]),
            "normal_status": nested["status"],
            "tight_budget_status": tight_nested["status"],
        },
        "nand3_neq_controls": hard_controls,
        "crossing_control": crossing["status"],
        "affine_contradiction_control": affine_bad["status"],
        "corrupt_certificate_control": "REJECTED",
        "new_gate": "POLYNOMIAL_DECOMPOSITION_OF_CROSSING_AFFINE_FORBIDDEN_SUBSPACES",
        "claim_boundary": (
            "Laminar affine forbidden-subspace arrangements only. Crossing arrangements, arbitrary CNF, "
            "unrestricted Horn-affine composition, and P versus NP remain open."
        ),
    }
    result["integrity_sha256"] = digest(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--output")
    parser.add_argument("--seed", type=int, default=420042)
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
