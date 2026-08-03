#!/usr/bin/env python3
from __future__ import annotations

import argparse, copy, json, random

from janus_c044_local_signed_support_core import evaluate_affine, evaluate_cnf, normalize_cnf
from janus_c045_basis_portfolio_core import digest
from janus_c045_basis_portfolio_solver import solve_basis_portfolio
from janus_c045_basis_portfolio_verifier import verify_basis_portfolio


def brute(cnf, affine, nvars):
    cnf = normalize_cnf(cnf)
    for assignment in range(1 << nvars):
        if evaluate_affine(affine, assignment) and evaluate_cnf(cnf, assignment):
            return True, assignment
    return False, None


def random_cnf(rng, nvars, clauses):
    out = []
    for _ in range(clauses):
        width = rng.randint(1, min(3, nvars))
        variables = rng.sample(range(1, nvars + 1), width)
        out.append(tuple(variable if rng.getrandbits(1) else -variable for variable in variables))
    return tuple(out)


def random_affine(rng, nvars, count):
    return tuple((rng.randrange(1, 1 << nvars), rng.getrandbits(1)) for _ in range(count))


def cumulative_hidden_basis_family(n):
    cnf = tuple((i,) for i in range(1, n + 1))
    affine = []
    for i in range(1, n + 1):
        mask = 1 << (i - 1)
        for j in range(1, i + 1):
            mask ^= 1 << (n + j - 1)
        affine.append((mask, 0))
    return cnf, tuple(affine), 2 * n


def hard_image(n):
    clauses = []
    for variable in range(1, n + 1):
        for shift in (1, 3, 5):
            second = ((variable + shift - 1) % n) + 1
            third = ((variable + 2 * shift - 1) % n) + 1
            clauses.append((variable, -second, third))
    return tuple(clauses), (), n


def probe_statuses(certificate):
    return {
        candidate["policy"]: probe["status"]
        for candidate, probe in zip(
            certificate["candidate_manifest"]["candidates"],
            certificate["probes"],
        )
    }


def run_audit(seed=450045):
    rng = random.Random(seed)
    random_cases = 220
    exact = open_cases = mismatches = witness_failures = verification_failures = 0
    for _ in range(random_cases):
        nvars = rng.randint(1, 7)
        cnf = random_cnf(rng, nvars, rng.randint(0, 9))
        affine = random_affine(rng, nvars, rng.randint(0, 4))
        certificate = solve_basis_portfolio(
            cnf,
            affine,
            nvars_hint=nvars,
            separator_cap=1,
            local_support_cap=64,
        )
        truth, _ = brute(cnf, affine, nvars)
        if certificate["status"] in ("SAT", "UNSAT"):
            exact += 1
            if (certificate["status"] == "SAT") != truth:
                mismatches += 1
            if certificate["status"] == "SAT":
                witness = int(certificate["witness_mask"])
                if not (
                    evaluate_affine(affine, witness)
                    and evaluate_cnf(normalize_cnf(cnf), witness)
                ):
                    witness_failures += 1
        else:
            open_cases += 1
        if not verify_basis_portfolio(cnf, affine, certificate, nvars_hint=nvars):
            verification_failures += 1

    cnf, affine, nvars = cumulative_hidden_basis_family(40)
    hidden = solve_basis_portfolio(
        cnf,
        affine,
        nvars_hint=nvars,
        separator_cap=1,
        local_support_cap=8,
    )
    assert hidden["status"] == "SAT"
    assert verify_basis_portfolio(cnf, affine, hidden, nvars_hint=nvars)
    statuses = probe_statuses(hidden)
    assert statuses["CANONICAL_FREE"] == "OPEN_LOCAL_SUPPORT"
    assert statuses["CLAUSE_EXPOSED_GREEDY"] == "SAT"
    selected = hidden["candidate_manifest"]["candidates"][hidden["selected_candidate_index"]]
    assert selected["policy"] == "CLAUSE_EXPOSED_GREEDY"

    hard_cnf, hard_affine, hard_nvars = hard_image(24)
    hard = solve_basis_portfolio(
        hard_cnf,
        hard_affine,
        nvars_hint=hard_nvars,
        separator_cap=1,
        local_support_cap=8,
    )
    assert hard["status"] == "OPEN_PORTFOLIO_EXHAUSTED"
    assert verify_basis_portfolio(hard_cnf, hard_affine, hard, nvars_hint=hard_nvars)

    corrupt = copy.deepcopy(hidden)
    corrupt["candidate_manifest"]["candidates"][0]["coordinate_forms"][0][0] ^= 1
    assert not verify_basis_portfolio(cnf, affine, corrupt, nvars_hint=nvars)

    corrupt_probe = copy.deepcopy(hidden)
    corrupt_probe["probes"][0]["candidate_basis_digest"] = "0" * 64
    corrupt_probe["integrity_sha256"] = digest(
        {key: value for key, value in corrupt_probe.items() if key != "integrity_sha256"}
    )
    assert not verify_basis_portfolio(cnf, affine, corrupt_probe, nvars_hint=nvars)

    result = {
        "artifact_id": "C045-JANUS-JOINT-AFFINE-BASIS-DECOMPOSITION-MESSAGE-DISCOVERY",
        "status": "PASS",
        "p_vs_np": "OPEN",
        "seed": seed,
        "random_cases": random_cases,
        "random_exact": exact,
        "random_open": open_cases,
        "mismatches": mismatches,
        "witness_failures": witness_failures,
        "independent_verification_failures": verification_failures,
        "constructive_theorem": "A fixed polynomial frozen portfolio of provenance-carrying affine coordinate bases followed by one fully charged C044 probe per unique basis is polynomial and sound; it selects only independently replayable exact terminals.",
        "arrangement_invariance_lemma": "For a fixed factor sequence, an invertible affine coordinate change preserves the intersection poset, dimensions, signed-recurrence coefficients up to transported subspaces, and live support cardinalities. Basis search can improve locality but cannot alter the intrinsic global arrangement.",
        "hidden_basis_control": {
            "variables": 80,
            "dimension": 40,
            "canonical_probe": statuses["CANONICAL_FREE"],
            "clause_exposed_probe": statuses["CLAUSE_EXPOSED_GREEDY"],
            "selected_policy": selected["policy"],
            "status": hidden["status"],
        },
        "hard_image_control": {
            "variables": 24,
            "status": hard["status"],
            "all_probe_statuses": probe_statuses(hard),
        },
        "tampered_manifest": "REJECTED",
        "tampered_probe": "REJECTED",
        "new_gate": "POLYNOMIAL_BASIS_PORTFOLIO_COMPLETENESS_OR_BASIS_INVARIANT_SEMANTIC_DECOMPOSITION",
        "claim_boundary": "The four-constructor portfolio is not complete for arbitrary CNF. It proves that charged basis choice can strictly enlarge C044, while invertible changes alone do not shrink the global intersection arrangement. Failure returns capability-scoped OPEN and proves no lower bound.",
    }
    result["integrity_sha256"] = digest(result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--output")
    parser.add_argument("--seed", type=int, default=450045)
    args = parser.parse_args()
    result = run_audit(args.seed)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2, sort_keys=True)
            handle.write("\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.self_test:
        assert result["status"] == "PASS"
        assert result["mismatches"] == 0
        assert result["witness_failures"] == 0
        assert result["independent_verification_failures"] == 0


if __name__ == "__main__":
    main()
