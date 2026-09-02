from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Sequence, Tuple

DEPTHS = (1, 2, 3, 4, 5, 6)
PARENT_R39 = "221887994664e8b1bb1de00dec29eaac49f86269"
SOURCE_FIXTURE = "Lvl6_pyr_1_6_trimmer.3mf"
SOURCE_FIXTURE_SIZE = 6283724

State = Dict[str, object]
Signature = Tuple[object, ...]


def canonical_json_sha256(obj: object) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def path_id(path: Sequence[int]) -> str:
    return ".".join(str(x) for x in path)


def generate_fixture(depth: int, mode: str) -> List[State]:
    if depth < 1:
        raise ValueError("depth must be >= 1")
    if mode not in {"symmetric", "broken", "boundary"}:
        raise ValueError(mode)

    states: List[State] = []
    broken_path = (3,) * depth
    for path in itertools.product(range(4), repeat=depth):
        local_property = not (mode == "broken" and path == broken_path)
        if mode == "boundary":
            boundary_signature = "path:" + path_id(path)
        else:
            boundary_signature = "shared"
        states.append(
            {
                "state_id": path_id(path),
                "path": list(path),
                "level": depth,
                "local_property": local_property,
                "boundary_signature": boundary_signature,
            }
        )
    return states


def safe_signature(state: State) -> Signature:
    return (
        int(state["level"]),
        bool(state["local_property"]),
        str(state["boundary_signature"]),
    )


def unsafe_level_only_signature(state: State) -> Signature:
    return (int(state["level"]),)


def transport_recheck(representative: State, member: State) -> bool:
    return (
        int(member["level"]) == int(representative["level"])
        and bool(member["local_property"]) == bool(representative["local_property"])
        and str(member["boundary_signature"]) == str(representative["boundary_signature"])
    )


def evaluate_partition(
    states: Sequence[State],
    signature_fn: Callable[[State], Signature],
    signature_name: str,
) -> dict:
    groups: Dict[Signature, List[State]] = defaultdict(list)
    for state in states:
        groups[signature_fn(state)].append(state)

    membership_count: Dict[str, int] = defaultdict(int)
    class_summaries = []
    F = 0
    transport_checks = 0
    representative_property_failures = 0
    first_transport_failure = None

    for signature in sorted(groups, key=lambda x: repr(x)):
        members = sorted(groups[signature], key=lambda s: str(s["state_id"]))
        representative = members[0]
        representative_property = bool(representative["local_property"])
        if not representative_property:
            representative_property_failures += 1

        transport_records = []
        class_failures = 0
        for member in members:
            sid = str(member["state_id"])
            membership_count[sid] += 1
            ok = transport_recheck(representative, member)
            transport_checks += 1
            transport_records.append({"member_id": sid, "ok": ok})
            if not ok:
                F += 1
                class_failures += 1
                if first_transport_failure is None:
                    first_transport_failure = {
                        "representative_id": str(representative["state_id"]),
                        "member_id": sid,
                        "representative": {
                            "level": representative["level"],
                            "local_property": representative["local_property"],
                            "boundary_signature": representative["boundary_signature"],
                        },
                        "member": {
                            "level": member["level"],
                            "local_property": member["local_property"],
                            "boundary_signature": member["boundary_signature"],
                        },
                    }

        class_summaries.append(
            {
                "signature_sha256": canonical_json_sha256(list(signature)),
                "representative_id": str(representative["state_id"]),
                "representative_property": representative_property,
                "member_count": len(members),
                "transport_checks": len(transport_records),
                "transport_failures": class_failures,
                "transport_certificate_sha256": canonical_json_sha256(transport_records),
            }
        )

    raw_ids = [str(s["state_id"]) for s in states]
    R = sum(1 for sid in raw_ids if membership_count[sid] != 1)
    N = len(states)
    K = len(groups)
    compression_observed = K < N
    representatives_property_all = representative_property_failures == 0
    finite_coverage_certified = (
        R == 0 and F == 0 and representatives_property_all
    )

    return {
        "signature": signature_name,
        "N_raw_states": N,
        "K_quotient_classes": K,
        "R_uncovered_or_nonexact_membership": R,
        "F_transport_failures": F,
        "compression_ratio_N_over_K": N / K if K else None,
        "QUOTIENT_COMPRESSION_OBSERVED": compression_observed,
        "FINITE_UNIVERSAL_COVERAGE_CERTIFIED": finite_coverage_certified,
        "representatives_property_all": representatives_property_all,
        "representative_property_failures": representative_property_failures,
        "transport_checks": transport_checks,
        "first_transport_failure": first_transport_failure,
        "class_certificate_count": len(class_summaries),
        "class_certificates_sha256": canonical_json_sha256(class_summaries),
        "class_certificates": class_summaries,
    }


def run_depth(depth: int) -> dict:
    symmetric_states = generate_fixture(depth, "symmetric")
    broken_states = generate_fixture(depth, "broken")
    boundary_states = generate_fixture(depth, "boundary")

    symmetric = evaluate_partition(
        symmetric_states, safe_signature, "SAFE_LEVEL_PROPERTY_BOUNDARY"
    )
    broken_safe = evaluate_partition(
        broken_states, safe_signature, "SAFE_LEVEL_PROPERTY_BOUNDARY"
    )
    broken_unsafe = evaluate_partition(
        broken_states, unsafe_level_only_signature, "UNSAFE_LEVEL_ONLY_NEGATIVE_CONTROL"
    )
    boundary = evaluate_partition(
        boundary_states, safe_signature, "SAFE_LEVEL_PROPERTY_BOUNDARY"
    )

    N = 4 ** depth
    expectations = {
        "symmetric_N_is_4_pow_n": symmetric["N_raw_states"] == N,
        "symmetric_K_is_1": symmetric["K_quotient_classes"] == 1,
        "symmetric_R0_F0": symmetric["R_uncovered_or_nonexact_membership"] == 0
        and symmetric["F_transport_failures"] == 0,
        "symmetric_compresses": symmetric["QUOTIENT_COMPRESSION_OBSERVED"] is True,
        "symmetric_finite_coverage": symmetric["FINITE_UNIVERSAL_COVERAGE_CERTIFIED"] is True,
        "broken_safe_splits_mutation": broken_safe["K_quotient_classes"] == 2,
        "broken_safe_transport_sound": broken_safe["R_uncovered_or_nonexact_membership"] == 0
        and broken_safe["F_transport_failures"] == 0,
        "broken_safe_rejects_universal_property": broken_safe["FINITE_UNIVERSAL_COVERAGE_CERTIFIED"] is False
        and broken_safe["representative_property_failures"] == 1,
        "broken_unsafe_detects_bad_transport": broken_unsafe["F_transport_failures"] > 0
        and broken_unsafe["FINITE_UNIVERSAL_COVERAGE_CERTIFIED"] is False,
        "boundary_K_equals_N": boundary["K_quotient_classes"] == N,
        "boundary_refuses_compression": boundary["QUOTIENT_COMPRESSION_OBSERVED"] is False,
        "boundary_still_has_exact_finite_coverage": boundary["R_uncovered_or_nonexact_membership"] == 0
        and boundary["F_transport_failures"] == 0
        and boundary["FINITE_UNIVERSAL_COVERAGE_CERTIFIED"] is True,
    }

    return {
        "depth_n": depth,
        "expected_raw_states_4_pow_n": N,
        "fixtures": {
            "PYRAMID_SYMMETRIC_4ARY": symmetric,
            "PYRAMID_BROKEN_BRANCH_SAFE": broken_safe,
            "PYRAMID_BROKEN_BRANCH_UNSAFE_NEGATIVE_CONTROL": broken_unsafe,
            "PYRAMID_BOUNDARY_DEPENDENCY": boundary,
        },
        "expectations": expectations,
        "pass": all(expectations.values()),
    }


def run_r40(depths: Iterable[int] = DEPTHS) -> dict:
    depth_results = [run_depth(int(depth)) for depth in depths]
    integrity_pass = all(item["pass"] for item in depth_results)

    positive_coverage = all(
        item["fixtures"]["PYRAMID_SYMMETRIC_4ARY"]["FINITE_UNIVERSAL_COVERAGE_CERTIFIED"]
        and item["fixtures"]["PYRAMID_BOUNDARY_DEPENDENCY"]["FINITE_UNIVERSAL_COVERAGE_CERTIFIED"]
        for item in depth_results
    )
    negative_controls_pass = all(
        not item["fixtures"]["PYRAMID_BROKEN_BRANCH_SAFE"]["FINITE_UNIVERSAL_COVERAGE_CERTIFIED"]
        and item["fixtures"]["PYRAMID_BROKEN_BRANCH_UNSAFE_NEGATIVE_CONTROL"]["F_transport_failures"] > 0
        for item in depth_results
    )
    quotient_compression_observed = all(
        item["fixtures"]["PYRAMID_SYMMETRIC_4ARY"]["QUOTIENT_COMPRESSION_OBSERVED"]
        for item in depth_results
    )
    boundary_exponential_identity_observed = all(
        item["fixtures"]["PYRAMID_BOUNDARY_DEPENDENCY"]["K_quotient_classes"]
        == item["fixtures"]["PYRAMID_BOUNDARY_DEPENDENCY"]["N_raw_states"]
        for item in depth_results
    )

    verdict = (
        "R40_FINITE_QUOTIENT_COVERAGE_CERTIFIED__POLYNOMIALITY_OPEN"
        if integrity_pass and positive_coverage and negative_controls_pass
        else "R40_FAIL_COVERAGE_OR_TRANSPORT"
    )

    return {
        "schema": "JANUS_TRUMP_R40_UNIVERSAL_QUOTIENT_COVERAGE_RESULT",
        "version": "1.0",
        "date": "2026-09-02",
        "source_git_commit": os.environ.get("GITHUB_SHA", "LOCAL_UNCOMMITTED"),
        "parent_R39_sealed_commit": PARENT_R39,
        "source_fixture": {
            "conversation_attachment": SOURCE_FIXTURE,
            "observed_size_bytes": SOURCE_FIXTURE_SIZE,
            "role": "ADVERSARIAL_DESIGN_REFERENCE_NOT_PROOF",
            "runtime_model": "DETERMINISTIC_ABSTRACT_4ARY_PYRAMID_STATE_GENERATOR",
        },
        "formal_mechanism": "REPRESENTATIVE -> PROPERTY -> TRANSPORT_CERTIFICATE -> TOTAL_COVERAGE -> UNIVERSAL_CLAIM",
        "depth_results": depth_results,
        "status": {
            "QUOTIENT_COMPRESSION_OBSERVED": quotient_compression_observed,
            "FINITE_UNIVERSAL_COVERAGE_CERTIFIED": positive_coverage,
            "NEGATIVE_CONTROL_UNIVERSAL_CLAIM_REJECTED": negative_controls_pass,
            "BOUNDARY_DEPENDENCY_BLOCKS_COMPRESSION": boundary_exponential_identity_observed,
            "POLYNOMIALITY_PROVEN": False,
        },
        "complexity_observations": {
            "finite_depths_only": list(int(d) for d in depths),
            "raw_enumeration_family": "N(n)=4^n",
            "symmetric_measured_K": [
                item["fixtures"]["PYRAMID_SYMMETRIC_4ARY"]["K_quotient_classes"]
                for item in depth_results
            ],
            "boundary_measured_K": [
                item["fixtures"]["PYRAMID_BOUNDARY_DEPENDENCY"]["K_quotient_classes"]
                for item in depth_results
            ],
            "symbolic_all_n_K_bound_proved": False,
            "polynomial_construction_cost_proved": False,
            "polynomial_verification_cost_proved": False,
            "finite_measurements_promoted_to_polynomiality": False,
        },
        "proof_ladder": {
            "highest_verified_level": "R40_FINITE_FIXTURE_QUOTIENT_TRANSPORT_COVERAGE_MECHANISM",
            "R39_UNIVERSAL_FIXPOINT_REMAINDER_OBLIGATION_CLOSED": False,
            "L2_UNIVERSAL_3CNF_COVERAGE": False,
            "L3_ONE_UNIFORM_TOTAL_TRUMP_RESOLVER": False,
            "L4_WORST_CASE_POLYNOMIAL_UNIFORM_TRUMP_RESOLVER": False,
        },
        "R31_obligation_impact": {"obligations_closed": 0},
        "captain_verdict": {
            "confirmed": "Finite witness-to-class transport plus exact total coverage can soundly lift representative properties over the explicitly generated finite universe, and the negative controls reject unsound quotienting.",
            "boundary_result": "Path-dependent boundaries preserve branch identity and force K=N in the adversarial boundary fixture, so compression is correctly refused.",
            "forbidden_promotion": "Finite compression observations do not prove polynomial quotient growth, universal 3-CNF coverage, SAT in P, or P=NP.",
            "next_gate": "R41_SYMBOLIC_ALL_N_QUOTIENT_GROWTH_AND_CERTIFICATE_COST_OBLIGATION",
        },
        "verdict": verdict,
        "TRUMP_finished": False,
        "SAT_IN_P": "NOT_PROVED",
        "P_VS_NP": "OPEN",
    }


def self_test() -> None:
    result = run_r40(DEPTHS)
    assert result["verdict"] == "R40_FINITE_QUOTIENT_COVERAGE_CERTIFIED__POLYNOMIALITY_OPEN"
    assert result["status"]["QUOTIENT_COMPRESSION_OBSERVED"] is True
    assert result["status"]["FINITE_UNIVERSAL_COVERAGE_CERTIFIED"] is True
    assert result["status"]["NEGATIVE_CONTROL_UNIVERSAL_CLAIM_REJECTED"] is True
    assert result["status"]["BOUNDARY_DEPENDENCY_BLOCKS_COMPRESSION"] is True
    assert result["status"]["POLYNOMIALITY_PROVEN"] is False
    for item in result["depth_results"]:
        n = item["depth_n"]
        N = 4 ** n
        assert item["fixtures"]["PYRAMID_SYMMETRIC_4ARY"]["N_raw_states"] == N
        assert item["fixtures"]["PYRAMID_SYMMETRIC_4ARY"]["K_quotient_classes"] == 1
        assert item["fixtures"]["PYRAMID_BROKEN_BRANCH_SAFE"]["K_quotient_classes"] == 2
        assert item["fixtures"]["PYRAMID_BROKEN_BRANCH_UNSAFE_NEGATIVE_CONTROL"]["F_transport_failures"] == 1
        assert item["fixtures"]["PYRAMID_BOUNDARY_DEPENDENCY"]["K_quotient_classes"] == N
    print("R40_SELF_TEST_PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return

    result = run_r40(DEPTHS)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "status": result["status"],
                "depths": [r["depth_n"] for r in result["depth_results"]],
                "P_VS_NP": result["P_VS_NP"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
