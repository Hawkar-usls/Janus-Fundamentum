#!/usr/bin/env python3
from __future__ import annotations
import argparse
import copy
import json
import random

from janus_c047_affine_trellis_core import *
from janus_c047_affine_functional_trellis import brute, random_factor, hard_image
from janus_c047_affine_trellis_solver import compile_trellis
from janus_c048_layout_solver import solve_with_layout_portfolio
from janus_c048_layout_verifier import verify


def hidden_order_family(d: int) -> tuple[list[dict[str, object]], int]:
    dimension = d + 1
    z = 1 << d
    factors: list[dict[str, object]] = []
    for i in range(d):
        factors.append({"factor_id": i, "equations": [(1 << i, 0)]})
    for i in range(d):
        factors.append({"factor_id": d + i, "equations": [((1 << i) | z, 0)]})
    return factors, dimension


def run(seed: int = 480048) -> dict[str, object]:
    rng = random.Random(seed)
    random_cases = 180
    exact = opened = mismatches = witness_failures = verification_failures = 0
    for _ in range(random_cases):
        dimension = rng.randint(1, 7)
        factors = [random_factor(rng, dimension, i) for i in range(rng.randint(0, 9))]
        certificate = solve_with_layout_portfolio(
            factors,
            dimension,
            requested_width_cap=4,
        )
        truth, _ = brute(factors, dimension)
        if certificate["status"] in ("SAT", "UNSAT"):
            exact += 1
            if (certificate["status"] == "SAT") != truth:
                mismatches += 1
            if certificate["status"] == "SAT":
                point = int(certificate["ambient_witness"])
                if any(point_in_factor(point, factor["equations"]) for factor in normalize_factors(factors, dimension)):
                    witness_failures += 1
        else:
            opened += 1
        if not verify(factors, dimension, certificate):
            verification_failures += 1

    hidden_factors, hidden_dimension = hidden_order_family(20)
    baseline = compile_trellis(hidden_factors, hidden_dimension, requested_width_cap=2)
    selected = solve_with_layout_portfolio(hidden_factors, hidden_dimension, requested_width_cap=2)
    assert baseline["status"] == OPEN_CUT_WIDTH
    assert max(baseline["cut_widths"]) == 19
    assert selected["status"] == "SAT"
    assert selected["selected_probe"]["order_policy"] == "GREEDY_MIN_FRONTIER"
    assert max(selected["selected_probe"]["cut_widths"]) == 2
    assert verify(hidden_factors, hidden_dimension, selected)

    hard_factors = hard_image(24)
    hard = solve_with_layout_portfolio(hard_factors, 24, requested_width_cap=3)
    assert hard["status"] == "OPEN_PORTFOLIO_EXHAUSTED"
    assert verify(hard_factors, 24, hard)

    discovery_open = solve_with_layout_portfolio(
        hidden_factors,
        hidden_dimension,
        requested_width_cap=2,
        discovery_cap=1,
    )
    assert discovery_open["status"] == "OPEN_DISCOVERY_BUDGET"
    assert verify(hidden_factors, hidden_dimension, discovery_open)

    certificate_open = solve_with_layout_portfolio(
        hidden_factors,
        hidden_dimension,
        requested_width_cap=2,
        selector_certificate_cap=512,
    )
    assert certificate_open["status"] == OPEN_CERTIFICATE_VOLUME
    assert verify(hidden_factors, hidden_dimension, certificate_open)

    corrupt = copy.deepcopy(selected)
    corrupt["manifest"]["unique_candidates"][0]["order_positions"] = list(reversed(corrupt["manifest"]["unique_candidates"][0]["order_positions"]))
    corrupt["integrity_sha256"] = digest({k: v for k, v in corrupt.items() if k != "integrity_sha256"})
    assert not verify(hidden_factors, hidden_dimension, corrupt)

    result: dict[str, object] = {
        "artifact_id": "C048-JANUS-PROOF-CARRYING-AFFINE-LAYOUT-DISCOVERY",
        "status": "PASS",
        "p_vs_np": "OPEN",
        "seed": seed,
        "random_cases": random_cases,
        "random_exact": exact,
        "random_open": opened,
        "mismatches": mismatches,
        "witness_failures": witness_failures,
        "independent_verification_failures": verification_failures,
        "constructive_theorem": "A fixed polynomial assignment-independent portfolio of affine-subspace layout constructors can be frozen, fully probed by C047, and selected in polynomial total work relative to the charged probes. Selection is sound but the portfolio is not universally complete.",
        "hidden_order_separation": {
            "dimension": hidden_dimension,
            "factors": len(hidden_factors),
            "baseline_status": baseline["status"],
            "baseline_first_overflow_width": baseline["overflow_width"],
            "baseline_max_width": max(baseline["cut_widths"]),
            "selected_status": selected["status"],
            "selected_constructor": selected["selected_probe"]["order_policy"],
            "selected_width": max(selected["selected_probe"]["cut_widths"]),
        },
        "hard_image_control": {
            "variables": 24,
            "status": hard["status"],
            "candidate_count": hard["manifest"]["candidate_count"],
        },
        "discovery_refusal": discovery_open["status"],
        "certificate_refusal": certificate_open["status"],
        "tampered_manifest": "REJECTED",
        "new_gate": "POLYNOMIAL_LAYOUT_PORTFOLIO_COMPLETENESS_OR_FIXED_WIDTH_BRANCH_DECOMPOSITION_DISCOVERY",
        "claim_boundary": "The frozen four-constructor portfolio strictly extends C047 on a hidden-order family but is not complete for arbitrary arrangements and does not solve NAND3+NEQ or P versus NP.",
    }
    result["integrity_sha256"] = digest(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--output")
    parser.add_argument("--seed", type=int, default=480048)
    args = parser.parse_args()
    result = run(args.seed)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(text)
    else:
        print(text, end="")
    if args.self_test:
        assert result["status"] == "PASS"
        assert result["mismatches"] == 0
        assert result["witness_failures"] == 0
        assert result["independent_verification_failures"] == 0


if __name__ == "__main__":
    main()
