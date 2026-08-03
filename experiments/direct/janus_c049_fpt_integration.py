#!/usr/bin/env python3
from __future__ import annotations

import argparse
import itertools
import json
import random
from typing import Any

from janus_c047_affine_trellis_core import linear_rref, normalize_factors
from janus_c049_fpt_integration_core import *
from janus_c049_fpt_integration_solver import solve_phase_a
from janus_c049_fpt_integration_verifier import verify


def brute_width(spaces: list[tuple[int, ...]], dimension: int) -> tuple[int, list[int]]:
    best_width = 10**9
    best_order: list[int] = []
    for order in itertools.permutations(range(len(spaces))):
        layout = layout_data_from_spaces(spaces, list(order), dimension)
        key = (layout["maximum_width"], layout["total_width"], list(order))
        if not best_order or key < (best_width, layout_data_from_spaces(spaces, best_order, dimension)["total_width"], best_order):
            best_width = layout["maximum_width"]
            best_order = list(order)
    return best_width if best_order else 0, best_order


def random_factor(rng: random.Random, dimension: int, factor_id: int) -> dict[str, Any]:
    vectors = [rng.randrange(1, 1 << dimension) for _ in range(rng.randint(1, min(3, dimension)))]
    basis = linear_rref(vectors, dimension)
    return {
        "factor_id": factor_id,
        "equations": [(vector, rng.getrandbits(1)) for vector in basis],
    }


def c046_pair(dimension: int, complementary: bool) -> list[dict[str, Any]]:
    factors: list[dict[str, Any]] = []
    factor_id = 0
    for bit in range(dimension):
        mask = 1 << bit
        factors.append({"factor_id": factor_id, "equations": [(mask, 0)]})
        factor_id += 1
        factors.append({"factor_id": factor_id, "equations": [(mask, 1 if complementary else 0)]})
        factor_id += 1
    return factors


def hidden_order_family(pairs: int) -> tuple[list[dict[str, Any]], int, list[int]]:
    dimension = pairs + 1
    z = 1 << pairs
    factors: list[dict[str, Any]] = []
    for i in range(pairs):
        factors.append({"factor_id": i, "equations": [(1 << i, 0)]})
    for i in range(pairs):
        factors.append({"factor_id": pairs + i, "equations": [((1 << i) | z, 0)]})
    interleaved: list[int] = []
    for i in range(pairs):
        interleaved.extend([i, pairs + i])
    return factors, dimension, interleaved


def local_obstruction_family() -> tuple[list[dict[str, Any]], int, int]:
    dimension = 3
    factors = [
        {"factor_id": 0, "equations": [(1, 0), (2, 0), (4, 0)]},
        {"factor_id": 1, "equations": [(1, 0)]},
        {"factor_id": 2, "equations": [(2, 0)]},
        {"factor_id": 3, "equations": [(4, 0)]},
    ]
    return factors, dimension, 1


def run_audit(seed: int = 490049) -> dict[str, Any]:
    rng = random.Random(seed)
    reduction_identity_cases = 90
    permutation_checks = 0
    reduction_failures = 0
    obstruction_soundness_failures = 0
    for _ in range(reduction_identity_cases):
        dimension = rng.randint(2, 6)
        count = rng.randint(1, 6)
        factors = [random_factor(rng, dimension, i) for i in range(count)]
        normalized = normalize_factors(factors, dimension)
        spaces = [normal_space(factor) for factor in normalized]
        dummy_cap = IntegrationCapability(max(2, input_length(normalized, dimension)), 2)
        meter = IntegrationMeter(dummy_cap)
        preprocessing = jko_column_reduction_skeleton(normalized, dimension, 2, meter)
        reduced = [tuple(space) for space in preprocessing["reduced_spaces"]]
        for order in itertools.permutations(range(len(spaces))):
            permutation_checks += 1
            if layout_data_from_spaces(spaces, list(order), dimension)["cut_widths"] != layout_data_from_spaces(
                reduced, list(order), dimension
            )["cut_widths"]:
                reduction_failures += 1
        obstruction = preprocessing["first_local_obstruction"]
        if obstruction is not None and len(spaces) <= 7:
            optimum, _ = brute_width(spaces, dimension)
            if optimum <= 2:
                obstruction_soundness_failures += 1

    obstruction_factors, obstruction_dimension, obstruction_k = local_obstruction_family()
    obstruction_result = solve_phase_a(obstruction_factors, obstruction_dimension, k=obstruction_k)
    assert obstruction_result["status"] == NO_LAYOUT_AT_CAP
    assert verify(obstruction_factors, obstruction_dimension, obstruction_result)

    duplicate = c046_pair(8, complementary=False)
    duplicate_result = solve_phase_a(duplicate, 8, k=1)
    assert duplicate_result["status"] == "SAT"
    assert verify(duplicate, 8, duplicate_result)

    complementary = c046_pair(8, complementary=True)
    complementary_result = solve_phase_a(complementary, 8, k=1)
    assert complementary_result["status"] == "UNSAT"
    assert verify(complementary, 8, complementary_result)

    hidden_factors, hidden_dimension, hidden_order = hidden_order_family(8)
    normalized_hidden = normalize_factors(hidden_factors, hidden_dimension)
    hidden_spaces = [normal_space(factor) for factor in normalized_hidden]
    hidden_layout = layout_data_from_spaces(hidden_spaces, hidden_order, hidden_dimension)
    hidden_transcript = make_found_layout_transcript(
        hidden_order,
        hidden_layout["cut_widths"],
        hidden_layout["cut_bases"],
        constructor_id="AUDIT_EXTERNAL_FOUND_LAYOUT_REPLAY_ONLY",
        discovery_claim=False,
        constructor_trace={"audit_only": True},
    )
    hidden_result = solve_phase_a(
        hidden_factors,
        hidden_dimension,
        k=2,
        constructor_transcript=hidden_transcript,
    )
    assert hidden_result["status"] == "SAT"
    assert hidden_result["discovery_claim"] is False
    assert verify(hidden_factors, hidden_dimension, hidden_result)

    bare_no_layout = {
        "schema": CONSTRUCTOR_SCHEMA,
        "terminal": "NO_LAYOUT_AT_CAP",
        "constructor_id": "BARE_REFUSAL",
        "discovery_claim": True,
        "order_positions": [],
        "cut_widths": [],
        "cut_bases": [],
        "constructor_trace": {},
    }
    bare_no_layout["transcript_digest"] = sha256_obj(bare_no_layout)
    bare_result = solve_phase_a(
        hidden_factors,
        hidden_dimension,
        k=2,
        constructor_transcript=bare_no_layout,
    )
    assert bare_result["status"] == OPEN_UNVERIFIED_NO_LAYOUT_TRANSCRIPT
    assert verify(hidden_factors, hidden_dimension, bare_result)

    tampered_transcript = json.loads(json.dumps(hidden_transcript))
    tampered_transcript["cut_widths"][1] ^= 1
    tampered_result = solve_phase_a(
        hidden_factors,
        hidden_dimension,
        k=2,
        constructor_transcript=tampered_transcript,
    )
    assert tampered_result["status"] == OPEN_INVALID_CONSTRUCTOR_TRANSCRIPT
    assert verify(hidden_factors, hidden_dimension, tampered_result)

    pending_factors, pending_dimension, _ = hidden_order_family(10)
    pending_result = solve_phase_a(pending_factors, pending_dimension, k=1)
    assert pending_result["status"] == OPEN_FPT_ENGINE_PENDING
    assert verify(pending_factors, pending_dimension, pending_result)

    discovery_exhaustion = solve_phase_a(duplicate, 8, k=1, discovery_cap=1)
    assert discovery_exhaustion["status"] == OPEN_DISCOVERY_BUDGET
    assert verify(duplicate, 8, discovery_exhaustion)

    certificate_exhaustion = solve_phase_a(duplicate, 8, k=1, certificate_cap=128)
    assert certificate_exhaustion["status"] == OPEN_CERTIFICATE_VOLUME
    assert verify(duplicate, 8, certificate_exhaustion)

    corrupt_open = json.loads(json.dumps(discovery_exhaustion))
    corrupt_open["overflow_evidence"]["discovery_limit"] += 1
    corrupt_open_body = dict(corrupt_open)
    corrupt_open_body.pop("integrity_sha256", None)
    corrupt_open["integrity_sha256"] = sha256_obj(corrupt_open_body)
    assert not verify(duplicate, 8, corrupt_open)

    corrupt = json.loads(json.dumps(hidden_result))
    corrupt["verified_layout"]["cut_widths"][1] ^= 1
    assert not verify(hidden_factors, hidden_dimension, corrupt)

    result = {
        "artifact_id": "C049-JANUS-JKO-FPT-LAYOUT-INTEGRATION-PHASE-A",
        "status": "PASS",
        "p_vs_np": "OPEN",
        "seed": seed,
        "implementation_status": "PHASE_A_PREPROCESSING_AND_LAYOUT_REPLAY_COMPLETE_FULL_B_TRAJECTORY_ENGINE_PENDING",
        "reduction_identity_cases": reduction_identity_cases,
        "permutation_checks": permutation_checks,
        "reduction_failures": reduction_failures,
        "obstruction_soundness_failures": obstruction_soundness_failures,
        "local_no_layout_certificate": {
            "status": obstruction_result["status"],
            "reason": obstruction_result["reason"],
            "reduced_dimension": obstruction_result["no_layout_certificate"]["reduced_dimension"],
            "threshold": obstruction_result["no_layout_certificate"]["threshold"],
        },
        "offset_controls": {
            "duplicate_offsets": duplicate_result["status"],
            "complementary_offsets": complementary_result["status"],
        },
        "found_layout_replay": {
            "status": hidden_result["status"],
            "maximum_width": hidden_result["verified_layout"]["maximum_width"],
            "discovery_claim": hidden_result["discovery_claim"],
        },
        "bare_no_layout_transcript": bare_result["status"],
        "tampered_transcript": tampered_result["status"],
        "pending_full_set_engine": pending_result["status"],
        "discovery_exhaustion": discovery_exhaustion["status"],
        "certificate_exhaustion": certificate_exhaustion["status"],
        "corrupt_certificate": "REJECTED",
        "corrupt_open_evidence": "REJECTED",
        "constructive_result": (
            "JKO Lemma 5.2 preprocessing is reimplemented for GF(2), its all-order cut-width preservation is audited, "
            "Proposition 2.2 yields a replayable local NO_LAYOUT_AT_CAP certificate, and every verified FOUND_LAYOUT composes exactly with C047 offset-aware trellis semantics."
        ),
        "surviving_gate": "REIMPLEMENT_B_TRAJECTORY_FULL_SET_ENGINE_AND_REPLAY_NO_LAYOUT_AT_CAP",
        "claim_boundary": (
            "This phase does not yet implement the published FPT full-set constructor. External FOUND_LAYOUT is replay-only and never counted as discovered; bare NO_LAYOUT is rejected."
        ),
    }
    result["integrity_sha256"] = sha256_obj(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--output")
    parser.add_argument("--seed", type=int, default=490049)
    args = parser.parse_args()
    result = run_audit(args.seed)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2, sort_keys=True)
            handle.write("\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.self_test:
        assert result["status"] == "PASS"
        assert result["reduction_failures"] == 0
        assert result["obstruction_soundness_failures"] == 0


if __name__ == "__main__":
    main()
