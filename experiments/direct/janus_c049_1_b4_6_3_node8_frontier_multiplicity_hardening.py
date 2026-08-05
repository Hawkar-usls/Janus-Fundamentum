#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

SCHEMA = "C049.1-B4.6.3-NODE8-FRONTIER-MULTIPLICITY-HARDENING-v1"
SOURCE_SCHEMA = "C049.1-B4.6.3-NODE8-PARENT-FRONTIER-STRUCTURAL-COMPRESSION-v1"
TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"
EXPECTED_SOURCE_BYTES = 204739
EXPECTED_SOURCE_SHA256 = "93dcd5610eb9df079823b172a4f824ce1c09859e759c6b771dc95b99af394d34"
EXPECTED_SOURCE_SEMANTIC_DIGEST = "209f5a013ec492b67066abc3dcf08af183d2ec5ec0000f3d8d03a033cb32f9db"
EXPECTED_MANIFEST_SHA256 = "05a4269be3b15bee40c254f81cc5e668c4903e90777576a9f0d226093892122b"
EXPECTED_MANIFEST_DIGEST = "c1b34fe2e47a1566b9cde045dd28fbdafdd30780de834b6d0bdb8731b11a00d6"
EXPECTED_CLASS_COUNT = 61
EXPECTED_PATH_COUNT = 75
EXPECTED_COLLISION_COUNT = 14
EXPECTED_ASSIGNMENT_COUNT = 31500
EXPECTED_CORRECTION_COUNTS = {0: 220, 1: 88}
EXPECTED_PATH_DOMAIN = {
    "LEFT_A-Q00": 7, "LEFT_A-Q01": 7, "LEFT_A-Q02": 7,
    "LEFT_A-Q03": 5, "LEFT_A-Q04": 5,
    "LEFT_B-Q00": 7, "LEFT_B-Q01": 7, "LEFT_B-Q02": 7,
    "LEFT_B-Q03": 5, "LEFT_B-Q04": 5,
    "LEFT_C-Q00": 5, "LEFT_C-Q01": 5, "LEFT_C-Q02": 3,
}


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pretty_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def reorder(items: list[dict], mode: str, seed: int) -> list[dict]:
    result = copy.deepcopy(items)
    if mode == "reversed":
        result.reverse()
    elif mode == "seeded-shuffle":
        random.Random(seed).shuffle(result)
    elif mode != "original":
        raise AssertionError("record order mode")
    return result


def source_checks(source_path: Path, source: dict) -> dict:
    if len(source_path.read_bytes()) != EXPECTED_SOURCE_BYTES:
        raise AssertionError("source artifact byte drift")
    if file_sha256(source_path) != EXPECTED_SOURCE_SHA256:
        raise AssertionError("source artifact file sha drift")
    if source.get("schema") != SOURCE_SCHEMA:
        raise AssertionError("source schema drift")
    if source.get("semantic_digest_scope") != "proof_payload":
        raise AssertionError("source semantic scope drift")
    if source.get("semantic_digest") != EXPECTED_SOURCE_SEMANTIC_DIGEST:
        raise AssertionError("source semantic digest drift")
    if digest(source.get("proof_payload")) != EXPECTED_SOURCE_SEMANTIC_DIGEST:
        raise AssertionError("source semantic digest mismatch")
    proof = source["proof_payload"]
    if proof.get("admit") is not True:
        raise AssertionError("source admission drift")
    inherited = proof.get("invariant_vector")
    if inherited != {f"N8-INV-{index:02d}": "PASS" for index in range(1, 11)}:
        raise AssertionError("source invariant vector drift")
    source_info = proof["source"]
    if source_info["integrated_manifest_file_sha256"] != EXPECTED_MANIFEST_SHA256:
        raise AssertionError("manifest file binding drift")
    if source_info["integrated_manifest_digest"] != EXPECTED_MANIFEST_DIGEST:
        raise AssertionError("manifest semantic binding drift")
    strict = proof["strict_boundary"]
    required = {
        "node8_parent_generator_frontier_complete": True,
        "node8_parent_refinement_complete": True,
        "node8_parent_up_k_complete": False,
        "node8_integrated_into_bottom_up_executor": False,
        "negative_root_reached": False,
        "terminal_completeness_proved": False,
        "found_layout_enabled": False,
        "no_layout_at_cap_enabled": False,
        "current_global_terminal": TERMINAL,
        "p_vs_np": "OPEN",
    }
    for key, expected in required.items():
        if strict.get(key) != expected:
            raise AssertionError(f"strict boundary drift: {key}")
    return proof


def build_payload(source_path: Path, source: dict, mode: str) -> dict:
    proof = source_checks(source_path, source)
    quotient = proof["quotient_frontier"]
    classes = reorder(quotient["classes"], mode, 0xC049193)
    paths = reorder(quotient["path_to_class"], mode, 0xC049194)

    operations = Counter()
    operations["source_bytes_hashed"] = EXPECTED_SOURCE_BYTES
    operations["source_semantic_fields_checked"] = 10
    operations["inherited_invariants_checked"] = 10

    if len(classes) != EXPECTED_CLASS_COUNT or len(paths) != EXPECTED_PATH_COUNT:
        raise AssertionError("class/path count drift")

    class_by_id: dict[str, dict] = {}
    for item in classes:
        operations["class_records_read"] += 1
        class_id = str(item["class_id"])
        if class_id in class_by_id:
            raise AssertionError("duplicate class id")
        class_by_id[class_id] = item
    expected_class_ids = {f"N8-S{index:02d}" for index in range(EXPECTED_CLASS_COUNT)}
    if set(class_by_id) != expected_class_ids:
        raise AssertionError("class id domain drift")

    path_by_key: dict[tuple[str, int], dict] = {}
    paths_by_source: dict[str, list[int]] = defaultdict(list)
    paths_by_class: dict[str, list[dict]] = defaultdict(list)
    correction_counts: Counter[int] = Counter()
    assignment_by_class: Counter[str] = Counter()

    for record in paths:
        operations["path_records_read"] += 1
        source_class = str(record["left_class_id"])
        local_index = int(record["local_path_index"])
        class_id = str(record["class_id"])
        key = (source_class, local_index)
        operations["path_key_tests"] += 1
        if key in path_by_key:
            raise AssertionError("duplicate path key")
        if source_class not in EXPECTED_PATH_DOMAIN:
            raise AssertionError("unknown source quotient class")
        if class_id not in class_by_id:
            raise AssertionError("path points outside class catalog")
        path_by_key[key] = record
        paths_by_source[source_class].append(local_index)
        paths_by_class[class_id].append(record)

        corrections = [int(value) for value in record["shrink_corrections"]]
        if any(value not in (0, 1) for value in corrections):
            raise AssertionError("invalid shrink correction")
        operations["correction_cells_read"] += len(corrections)
        correction_counts.update(corrections)
        zero_count = corrections.count(0)
        operations["assignment_factor_cells_charged"] += zero_count
        assignment_by_class[class_id] += 6 ** zero_count

    expected_domain_keys = {
        (source, index)
        for source, count in EXPECTED_PATH_DOMAIN.items()
        for index in range(count)
    }
    if set(path_by_key) != expected_domain_keys:
        raise AssertionError("path domain is not exact")

    class_ledger = []
    multiplicity_total = 0
    collision_total = 0
    assignment_total = 0
    for class_id in sorted(class_by_id):
        operations["class_multiplicity_checks"] += 1
        item = class_by_id[class_id]
        records = sorted(paths_by_class[class_id], key=canonical_json)
        path_keys = [[str(r["left_class_id"]), int(r["local_path_index"])] for r in records]
        multiplicity = len(records)
        declared_multiplicity = int(item["source_path_multiplicity"])
        if multiplicity != declared_multiplicity:
            raise AssertionError("class source multiplicity mismatch")
        assignment_work = int(assignment_by_class[class_id])
        if assignment_work != int(item["local_direct_assignment_tests"]):
            raise AssertionError("class assignment-work mismatch")
        multiplicity_total += multiplicity
        collision_total += multiplicity - 1
        assignment_total += assignment_work
        class_ledger.append({
            "class_id": class_id,
            "source_path_multiplicity": multiplicity,
            "collision_contribution": multiplicity - 1,
            "source_path_keys": path_keys,
            "source_path_key_digest": digest(path_keys),
            "local_direct_assignment_tests": assignment_work,
        })

    if multiplicity_total != EXPECTED_PATH_COUNT:
        raise AssertionError("global multiplicity conservation failed")
    if collision_total != EXPECTED_COLLISION_COUNT:
        raise AssertionError("collision conservation failed")
    if assignment_total != EXPECTED_ASSIGNMENT_COUNT:
        raise AssertionError("assignment-work conservation failed")
    if dict(correction_counts) != EXPECTED_CORRECTION_COUNTS:
        raise AssertionError("correction-cell conservation failed")

    if sum(int(item["source_path_multiplicity"]) for item in classes) != multiplicity_total:
        raise AssertionError("declared multiplicity total drift")
    if sum(int(item["local_direct_assignment_tests"]) for item in classes) != assignment_total:
        raise AssertionError("declared assignment total drift")
    if quotient["pre_shrink_quotient_path_count"] != multiplicity_total:
        raise AssertionError("quotient path summary drift")
    if quotient["post_shrink_class_count"] != len(class_ledger):
        raise AssertionError("post-shrink class summary drift")
    if quotient["source_path_collision_count"] != collision_total:
        raise AssertionError("collision summary drift")
    if quotient["local_direct_assignment_tests"] != assignment_total:
        raise AssertionError("assignment summary drift")
    geometry_counts = {int(key): int(value) for key, value in proof["geometry"]["shrink_correction_counts_over_quotient_cells"].items()}
    if geometry_counts != EXPECTED_CORRECTION_COUNTS:
        raise AssertionError("geometry correction summary drift")
    work = proof["work_ledger"]
    if work["quotient_paths_enumerated"] != multiplicity_total:
        raise AssertionError("work path count drift")
    if work["post_shrink_classes"] != len(class_ledger):
        raise AssertionError("work class count drift")
    if work["quotient_join_cells_checked"] != sum(correction_counts.values()):
        raise AssertionError("work correction-cell drift")
    if work["local_direct_witness_assignments_tested"] != assignment_total:
        raise AssertionError("work assignment count drift")

    multiplicity_histogram = Counter(item["source_path_multiplicity"] for item in class_ledger)
    source_domain_ledger = [
        {
            "left_class_id": source,
            "expected_path_count": EXPECTED_PATH_DOMAIN[source],
            "observed_indices": sorted(paths_by_source[source]),
        }
        for source in sorted(EXPECTED_PATH_DOMAIN)
    ]
    invariant_vector = {f"N8-INV-{index:02d}": "PASS" for index in range(1, 17)}
    operations["summary_equalities_checked"] = 12
    operations["invariant_slots_emitted"] = len(invariant_vector)

    return {
        "source_binding": {
            "artifact_bytes": EXPECTED_SOURCE_BYTES,
            "artifact_sha256": EXPECTED_SOURCE_SHA256,
            "artifact_semantic_digest": EXPECTED_SOURCE_SEMANTIC_DIGEST,
            "manifest_file_sha256": EXPECTED_MANIFEST_SHA256,
            "manifest_semantic_digest": EXPECTED_MANIFEST_DIGEST,
            "inherited_invariant_count": 10,
        },
        "node_id": 8,
        "k": int(proof["k"]),
        "multiplicity_ledger": {
            "source_domain": source_domain_ledger,
            "source_domain_digest": digest(source_domain_ledger),
            "class_ledger": class_ledger,
            "class_ledger_digest": digest(class_ledger),
            "class_count": len(class_ledger),
            "path_count": multiplicity_total,
            "multiplicity_sum": multiplicity_total,
            "multiplicity_histogram": {str(key): multiplicity_histogram[key] for key in sorted(multiplicity_histogram)},
            "collision_count": collision_total,
            "collision_identity": f"{multiplicity_total}-{len(class_ledger)}={collision_total}",
            "assignment_work_sum": assignment_total,
            "correction_cell_counts": {str(key): correction_counts[key] for key in sorted(correction_counts)},
            "correction_cell_sum": sum(correction_counts.values()),
            "path_key_bijection_complete": True,
            "class_multiplicity_conserved": True,
            "collision_multiplicity_conserved": True,
            "assignment_work_conserved": True,
            "correction_cells_conserved": True,
        },
        "work_ledger": {
            **{key: operations[key] for key in sorted(operations)},
            "verifier_operation_charge": sum(operations.values()),
            "fixed_point_certificate_bytes": 0,
        },
        "invariant_vector": invariant_vector,
        "tamper_contract": {
            "digest_repaired_attacks_required": 20,
            "all_source_and_ledger_fields_replayed": True,
        },
        "admit": True,
        "strict_boundary": {
            "node8_frontier_original_theorem_bound": True,
            "node8_frontier_multiplicity_hardened": True,
            "node8_parent_up_k_complete": False,
            "node8_integrated_into_bottom_up_executor": False,
            "node9_parent_refinement_started": False,
            "negative_root_reached": False,
            "terminal_completeness_proved": False,
            "found_layout_enabled": False,
            "no_layout_at_cap_enabled": False,
            "current_global_terminal": TERMINAL,
            "p_vs_np": "OPEN",
        },
        "next_gate": "REPLAY_AND_REBIND_PR94_TO_NODE8_MULTIPLICITY_HARDENED_HEAD",
    }


def finalize(payload: dict) -> dict:
    payload = copy.deepcopy(payload)
    artifact = {"schema": SCHEMA, "semantic_digest_scope": "proof_payload", "proof_payload": payload}
    previous = None
    for _ in range(20):
        artifact["semantic_digest"] = digest(artifact["proof_payload"])
        size = len(pretty_bytes(artifact))
        artifact["proof_payload"]["work_ledger"]["fixed_point_certificate_bytes"] = size
        if size == previous:
            artifact["semantic_digest"] = digest(artifact["proof_payload"])
            final_size = len(pretty_bytes(artifact))
            if final_size != size:
                previous = size
                continue
            return artifact
        previous = size
    raise AssertionError("certificate byte fixed point did not converge")


def build(source_path: Path, output_path: Path, mode: str) -> dict:
    source = json.loads(source_path.read_text(encoding="utf-8"))
    artifact = finalize(build_payload(source_path, source, mode))
    output_path.write_bytes(pretty_bytes(artifact))
    print("JANUS_C049_1_B4_6_3_NODE8_FRONTIER_MULTIPLICITY_HARDENING = PASS")
    print("INVARIANTS = 16/16")
    print("CLASS_COUNT =", artifact["proof_payload"]["multiplicity_ledger"]["class_count"])
    print("PATH_COUNT =", artifact["proof_payload"]["multiplicity_ledger"]["path_count"])
    print("COLLISION_COUNT =", artifact["proof_payload"]["multiplicity_ledger"]["collision_count"])
    print("ASSIGNMENT_WORK_SUM =", artifact["proof_payload"]["multiplicity_ledger"]["assignment_work_sum"])
    print("FIXED_POINT_CERTIFICATE_BYTES =", len(output_path.read_bytes()))
    print("SEMANTIC_DIGEST =", artifact["semantic_digest"])
    print("GLOBAL_TERMINAL =", TERMINAL)
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_artifact", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--record-order", choices=("original", "reversed", "seeded-shuffle"), default="original")
    args = parser.parse_args()
    build(args.source_artifact, args.output, args.record_order)


if __name__ == "__main__":
    main()
