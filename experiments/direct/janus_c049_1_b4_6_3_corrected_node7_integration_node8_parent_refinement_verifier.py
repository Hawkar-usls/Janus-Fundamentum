#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

SCHEMA = "C049.1-B4.6.3-CORRECTED-NODE7-INTEGRATION-NODE8-ATTACK-BOOTSTRAP-v1"
BASE_EXACT_HEAD = "024afebb322c67953f310af48818d3386fdcfc27"
UPK_SHA256 = "924e55a651518ce004964f5d7c5ea30e67424ca34507f18eb568341fc96528e0"
UPK_SEMANTIC = "cfd99ea716076414847749fb98185cea63c2cf44e9ceaa659bf37eb9e8fc366a"
CLOSURE_DIGEST = "99a702ea7005e4a41d99fc4454040314ab106632672b267bffb5f59e29afa728"
LEAF3_HISTOGRAM = {"2": 4, "3": 8, "4": 12, "5": 8, "6": 4}
EXPECTED_PAIRS = 279936
EXPECTED_REFINEMENTS = 70875648


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def seal(value: dict[str, Any]) -> dict[str, Any]:
    value = copy.deepcopy(value)
    value["certificate_bytes"] = 0
    while True:
        unsigned = dict(value)
        unsigned.pop("semantic_digest", None)
        value["semantic_digest"] = digest(unsigned)
        raw = canonical_json(value) + b"\n"
        if int(value["certificate_bytes"]) == len(raw):
            return value
        value["certificate_bytes"] = len(raw)


def expected_left_histogram() -> dict[str, int]:
    distribution = Counter({0: 1})
    for _ in range(4):
        next_distribution: Counter[int] = Counter()
        for subtotal, multiplicity in distribution.items():
            for length in (1, 2, 3):
                next_distribution[subtotal + length] += multiplicity * 2
        distribution = next_distribution
    return {str(length): int(count * 6) for length, count in sorted(distribution.items())}


def exact_hv_refinements(left: dict[str, int], right: dict[str, int]) -> int:
    return sum(
        int(left_count)
        * int(right_count)
        * math.comb(int(left_length) + int(right_length) - 2, int(left_length) - 1)
        for left_length, left_count in left.items()
        for right_length, right_count in right.items()
    )


def verify(upk_path: Path, artifact: dict[str, Any]) -> None:
    if file_sha256(upk_path) != UPK_SHA256:
        raise AssertionError("source up_k byte digest")
    upk = json.loads(upk_path.read_text(encoding="utf-8"))
    if upk.get("semantic_digest") != UPK_SEMANTIC:
        raise AssertionError("source up_k semantic digest")
    if upk.get("reachable_closure", {}).get("entries_digest") != CLOSURE_DIGEST:
        raise AssertionError("source closure digest")

    if artifact.get("schema") != SCHEMA or artifact.get("status") != "DRAFT_ATTACK_BOOTSTRAP":
        raise AssertionError("candidate schema/status")
    claimed = artifact.get("semantic_digest")
    unsigned = dict(artifact)
    unsigned.pop("semantic_digest", None)
    if claimed != digest(unsigned):
        raise AssertionError("candidate semantic digest")
    if int(artifact.get("certificate_bytes", -1)) != len(canonical_json(artifact) + b"\n"):
        raise AssertionError("candidate fixed-point byte count")

    source = artifact["source"]
    if (
        source["base_pr"],
        source["base_exact_head"],
        source["corrected_node7_up_k_sha256"],
        source["corrected_node7_up_k_semantic_digest"],
        source["corrected_node7_closure_digest"],
    ) != (113, BASE_EXACT_HEAD, UPK_SHA256, UPK_SEMANTIC, CLOSURE_DIGEST):
        raise AssertionError("exact stack binding")

    left_histogram = expected_left_histogram()
    reconstructed = artifact["corrected_node7_reconstruction"]
    if reconstructed["length_histogram"] != left_histogram:
        raise AssertionError("left histogram")
    if (
        reconstructed["input_generators"],
        reconstructed["retained_generators"],
        reconstructed["direct_removals"],
        reconstructed["closure_entries"],
        reconstructed["assignments_per_generator"],
    ) != (6, 6, 0, 7776, 1296):
        raise AssertionError("Node-7 reconstruction cardinalities")

    preflight = artifact["node8_attack_preflight"]
    pairs = sum(left_histogram.values()) * sum(LEAF3_HISTOGRAM.values())
    refinements = exact_hv_refinements(left_histogram, LEAF3_HISTOGRAM)
    if pairs != EXPECTED_PAIRS or refinements != EXPECTED_REFINEMENTS:
        raise AssertionError("independent expected count drift")
    if (
        preflight["left_entry_count"],
        preflight["right_entry_count"],
        preflight["child_pairs"],
        preflight["ordinary_join_steps"],
        preflight["diagonal_join_steps"],
        preflight["ordinary_hv_refinements"],
        preflight["generic_node8_pair_records_materialized"],
        preflight["generic_node8_refinement_records_materialized"],
    ) != (7776, 36, pairs, [[1, 0], [0, 1]], 0, refinements, 0, 0):
        raise AssertionError("Node-8 preflight contract")
    if not preflight["pair_cap_exceeded"] or not preflight["refinement_cap_exceeded"]:
        raise AssertionError("cap boundary")

    boundary = artifact["admission_boundary"]
    forbidden_true = (
        "corrected_node7_executor_integration_implemented",
        "corrected_node7_integration_admitted",
        "corrected_node8_parent_refinement_started",
        "corrected_node8_parent_refinement_complete",
        "corrected_node8_parent_up_k_complete",
        "corrected_bottom_up_replay_complete",
        "root_parent_refinement_complete",
        "root_full_set_computed",
        "root_empty_proved",
    )
    if any(boundary[name] is not False for name in forbidden_true):
        raise AssertionError("premature admission or terminal promotion")
    if boundary["found_layout"] != "FORBIDDEN" or boundary["no_layout_at_cap"] != "FORBIDDEN":
        raise AssertionError("layout terminal enabled")
    if boundary["p_vs_np"] != "OPEN":
        raise AssertionError("P vs NP boundary")
    if artifact["next_gate_status"] != "CLOSED_PENDING_CURRENT_GATE_EXACT_HEAD_ADMISSION":
        raise AssertionError("next gate opened prematurely")


def tamper_self_test(upk_path: Path, artifact: dict[str, Any]) -> None:
    attacks = []

    candidate = copy.deepcopy(artifact)
    candidate["source"]["base_exact_head"] = "0" * 40
    attacks.append(candidate)

    candidate = copy.deepcopy(artifact)
    candidate["corrected_node7_reconstruction"]["length_histogram"]["8"] -= 1
    attacks.append(candidate)

    candidate = copy.deepcopy(artifact)
    candidate["node8_attack_preflight"]["child_pairs"] += 1
    attacks.append(candidate)

    candidate = copy.deepcopy(artifact)
    candidate["node8_attack_preflight"]["ordinary_join_steps"].append([1, 1])
    attacks.append(candidate)

    candidate = copy.deepcopy(artifact)
    candidate["admission_boundary"]["corrected_node7_integration_admitted"] = True
    attacks.append(candidate)

    rejected = 0
    for candidate in attacks:
        repaired = seal(candidate)
        try:
            verify(upk_path, repaired)
        except AssertionError:
            rejected += 1
    if rejected != len(attacks):
        raise AssertionError(f"tamper rejection drift: {rejected}/{len(attacks)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("upk", type=Path)
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--tamper-self-test", action="store_true")
    args = parser.parse_args()
    artifact = json.loads(args.artifact.read_text(encoding="utf-8"))
    verify(args.upk, artifact)
    if args.tamper_self_test:
        tamper_self_test(args.upk, artifact)
    print(
        json.dumps(
            {
                "result": "PASS",
                "node8_child_pairs": artifact["node8_attack_preflight"]["child_pairs"],
                "node8_ordinary_hv_refinements": artifact["node8_attack_preflight"]["ordinary_hv_refinements"],
                "tamper_attacks_rejected": 5 if args.tamper_self_test else 0,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
