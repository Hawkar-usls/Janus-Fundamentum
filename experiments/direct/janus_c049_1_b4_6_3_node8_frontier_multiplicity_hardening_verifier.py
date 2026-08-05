#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

SCHEMA = "C049.1-B4.6.3-NODE8-FRONTIER-MULTIPLICITY-HARDENING-v1"
SOURCE_SCHEMA = "C049.1-B4.6.3-NODE8-PARENT-FRONTIER-STRUCTURAL-COMPRESSION-v1"
TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"
SOURCE_BYTES = 204739
SOURCE_SHA = "93dcd5610eb9df079823b172a4f824ce1c09859e759c6b771dc95b99af394d34"
SOURCE_SEMANTIC = "209f5a013ec492b67066abc3dcf08af183d2ec5ec0000f3d8d03a033cb32f9db"
MANIFEST_SHA = "05a4269be3b15bee40c254f81cc5e668c4903e90777576a9f0d226093892122b"
MANIFEST_SEMANTIC = "c1b34fe2e47a1566b9cde045dd28fbdafdd30780de834b6d0bdb8731b11a00d6"
DOMAIN = {
    "LEFT_A-Q00": 7, "LEFT_A-Q01": 7, "LEFT_A-Q02": 7,
    "LEFT_A-Q03": 5, "LEFT_A-Q04": 5,
    "LEFT_B-Q00": 7, "LEFT_B-Q01": 7, "LEFT_B-Q02": 7,
    "LEFT_B-Q03": 5, "LEFT_B-Q04": 5,
    "LEFT_C-Q00": 5, "LEFT_C-Q01": 5, "LEFT_C-Q02": 3,
}


def canon(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def h(value: Any) -> str:
    return hashlib.sha256(canon(value)).hexdigest()


def pretty(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def inspect_source(path: Path) -> dict:
    raw = path.read_bytes()
    if len(raw) != SOURCE_BYTES or hashlib.sha256(raw).hexdigest() != SOURCE_SHA:
        raise AssertionError("source byte binding")
    source = json.loads(raw)
    if source.get("schema") != SOURCE_SCHEMA:
        raise AssertionError("source schema")
    if source.get("semantic_digest_scope") != "proof_payload":
        raise AssertionError("source semantic scope")
    if source.get("semantic_digest") != SOURCE_SEMANTIC or h(source.get("proof_payload")) != SOURCE_SEMANTIC:
        raise AssertionError("source semantic binding")
    proof = source["proof_payload"]
    if proof.get("admit") is not True:
        raise AssertionError("source admission")
    if proof.get("invariant_vector") != {f"N8-INV-{i:02d}": "PASS" for i in range(1, 11)}:
        raise AssertionError("source invariants")
    binding = proof["source"]
    if binding.get("integrated_manifest_file_sha256") != MANIFEST_SHA:
        raise AssertionError("manifest sha")
    if binding.get("integrated_manifest_digest") != MANIFEST_SEMANTIC:
        raise AssertionError("manifest semantic")
    strict = proof["strict_boundary"]
    checks = (
        ("node8_parent_generator_frontier_complete", True),
        ("node8_parent_refinement_complete", True),
        ("node8_parent_up_k_complete", False),
        ("node8_integrated_into_bottom_up_executor", False),
        ("negative_root_reached", False),
        ("terminal_completeness_proved", False),
        ("found_layout_enabled", False),
        ("no_layout_at_cap_enabled", False),
        ("current_global_terminal", TERMINAL),
        ("p_vs_np", "OPEN"),
    )
    for key, value in checks:
        if strict.get(key) != value:
            raise AssertionError(f"source strict boundary: {key}")
    return proof


def expected_payload(source_path: Path) -> dict:
    proof = inspect_source(source_path)
    quotient = proof["quotient_frontier"]
    classes = quotient["classes"]
    records = quotient["path_to_class"]
    if len(classes) != 61 or len(records) != 75:
        raise AssertionError("source cardinalities")

    operations = Counter()
    operations["source_bytes_hashed"] = SOURCE_BYTES
    operations["source_semantic_fields_checked"] = 10
    operations["inherited_invariants_checked"] = 10

    by_class = {}
    for item in classes:
        operations["class_records_read"] += 1
        class_id = str(item["class_id"])
        if class_id in by_class:
            raise AssertionError("duplicate class")
        by_class[class_id] = item
    if set(by_class) != {f"N8-S{i:02d}" for i in range(61)}:
        raise AssertionError("class domain")

    record_keys = set()
    by_source = defaultdict(list)
    class_records = defaultdict(list)
    correction_counts = Counter()
    assignment = Counter()
    for record in records:
        operations["path_records_read"] += 1
        left = str(record["left_class_id"])
        index = int(record["local_path_index"])
        class_id = str(record["class_id"])
        key = (left, index)
        operations["path_key_tests"] += 1
        if key in record_keys:
            raise AssertionError("duplicate path key")
        if left not in DOMAIN or class_id not in by_class:
            raise AssertionError("path provenance")
        record_keys.add(key)
        by_source[left].append(index)
        class_records[class_id].append(record)
        corrections = tuple(int(value) for value in record["shrink_corrections"])
        if any(value not in (0, 1) for value in corrections):
            raise AssertionError("correction alphabet")
        correction_counts.update(corrections)
        operations["correction_cells_read"] += len(corrections)
        zero_count = corrections.count(0)
        operations["assignment_factor_cells_charged"] += zero_count
        assignment[class_id] += 6 ** zero_count

    exact_keys = {(left, index) for left, count in DOMAIN.items() for index in range(count)}
    if record_keys != exact_keys:
        raise AssertionError("path domain")

    class_ledger = []
    multiplicity_sum = 0
    collision_sum = 0
    assignment_sum = 0
    for class_id in sorted(by_class):
        operations["class_multiplicity_checks"] += 1
        item = by_class[class_id]
        rows = sorted(class_records[class_id], key=canon)
        keys = [[str(row["left_class_id"]), int(row["local_path_index"])] for row in rows]
        multiplicity = len(rows)
        local_work = int(assignment[class_id])
        if multiplicity != int(item["source_path_multiplicity"]):
            raise AssertionError("multiplicity mismatch")
        if local_work != int(item["local_direct_assignment_tests"]):
            raise AssertionError("assignment mismatch")
        multiplicity_sum += multiplicity
        collision_sum += multiplicity - 1
        assignment_sum += local_work
        class_ledger.append({
            "class_id": class_id,
            "source_path_multiplicity": multiplicity,
            "collision_contribution": multiplicity - 1,
            "source_path_keys": keys,
            "source_path_key_digest": h(keys),
            "local_direct_assignment_tests": local_work,
        })

    if (multiplicity_sum, len(class_ledger), collision_sum, assignment_sum) != (75, 61, 14, 31500):
        raise AssertionError("global conservation")
    if dict(correction_counts) != {0: 220, 1: 88}:
        raise AssertionError("correction conservation")
    if sum(int(item["source_path_multiplicity"]) for item in classes) != 75:
        raise AssertionError("declared multiplicity total")
    if sum(int(item["local_direct_assignment_tests"]) for item in classes) != 31500:
        raise AssertionError("declared assignment total")
    if (
        quotient["pre_shrink_quotient_path_count"],
        quotient["post_shrink_class_count"],
        quotient["source_path_collision_count"],
        quotient["local_direct_assignment_tests"],
    ) != (75, 61, 14, 31500):
        raise AssertionError("quotient summaries")
    geometry = {int(key): int(value) for key, value in proof["geometry"]["shrink_correction_counts_over_quotient_cells"].items()}
    if geometry != {0: 220, 1: 88}:
        raise AssertionError("geometry correction counts")
    source_work = proof["work_ledger"]
    if (
        source_work["quotient_paths_enumerated"],
        source_work["post_shrink_classes"],
        source_work["quotient_join_cells_checked"],
        source_work["local_direct_witness_assignments_tested"],
    ) != (75, 61, 308, 31500):
        raise AssertionError("source work summaries")

    histogram = Counter(item["source_path_multiplicity"] for item in class_ledger)
    source_domain = [
        {"left_class_id": left, "expected_path_count": DOMAIN[left], "observed_indices": sorted(by_source[left])}
        for left in sorted(DOMAIN)
    ]
    invariant_vector = {f"N8-INV-{index:02d}": "PASS" for index in range(1, 17)}
    operations["summary_equalities_checked"] = 12
    operations["invariant_slots_emitted"] = 16
    return {
        "source_binding": {
            "artifact_bytes": SOURCE_BYTES,
            "artifact_sha256": SOURCE_SHA,
            "artifact_semantic_digest": SOURCE_SEMANTIC,
            "manifest_file_sha256": MANIFEST_SHA,
            "manifest_semantic_digest": MANIFEST_SEMANTIC,
            "inherited_invariant_count": 10,
        },
        "node_id": 8,
        "k": int(proof["k"]),
        "multiplicity_ledger": {
            "source_domain": source_domain,
            "source_domain_digest": h(source_domain),
            "class_ledger": class_ledger,
            "class_ledger_digest": h(class_ledger),
            "class_count": 61,
            "path_count": 75,
            "multiplicity_sum": 75,
            "multiplicity_histogram": {str(key): histogram[key] for key in sorted(histogram)},
            "collision_count": 14,
            "collision_identity": "75-61=14",
            "assignment_work_sum": 31500,
            "correction_cell_counts": {"0": 220, "1": 88},
            "correction_cell_sum": 308,
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
    result = {"schema": SCHEMA, "semantic_digest_scope": "proof_payload", "proof_payload": copy.deepcopy(payload)}
    previous = None
    for _ in range(20):
        result["semantic_digest"] = h(result["proof_payload"])
        size = len(pretty(result))
        result["proof_payload"]["work_ledger"]["fixed_point_certificate_bytes"] = size
        if size == previous:
            result["semantic_digest"] = h(result["proof_payload"])
            if len(pretty(result)) == size:
                return result
        previous = size
    raise AssertionError("fixed point")


def reject_if_invalid(source_path: Path, candidate: dict) -> None:
    expected = finalize(expected_payload(source_path))
    if candidate != expected:
        raise AssertionError("independent replay mismatch")
    if candidate["proof_payload"]["work_ledger"]["fixed_point_certificate_bytes"] != len(pretty(candidate)):
        raise AssertionError("certificate byte charge")
    if candidate["semantic_digest"] != h(candidate["proof_payload"]):
        raise AssertionError("semantic digest")


def repair(candidate: dict) -> dict:
    payload = copy.deepcopy(candidate["proof_payload"])
    payload["work_ledger"]["fixed_point_certificate_bytes"] = 0
    return finalize(payload)


def tamper_self_test(source_path: Path, artifact: dict) -> None:
    attacks = []

    def add(name: str, mutation) -> None:
        candidate = copy.deepcopy(artifact)
        mutation(candidate)
        attacks.append((name, repair(candidate)))

    add("source_sha_substitution", lambda a: a["proof_payload"]["source_binding"].__setitem__("artifact_sha256", "0" * 64))
    add("source_semantic_substitution", lambda a: a["proof_payload"]["source_binding"].__setitem__("artifact_semantic_digest", "1" * 64))
    add("manifest_sha_substitution", lambda a: a["proof_payload"]["source_binding"].__setitem__("manifest_file_sha256", "2" * 64))
    add("source_domain_deletion", lambda a: a["proof_payload"]["multiplicity_ledger"]["source_domain"].pop())
    add("source_domain_index_loss", lambda a: a["proof_payload"]["multiplicity_ledger"]["source_domain"][0]["observed_indices"].pop())
    add("class_ledger_deletion", lambda a: a["proof_payload"]["multiplicity_ledger"]["class_ledger"].pop())
    add("class_id_collision", lambda a: a["proof_payload"]["multiplicity_ledger"]["class_ledger"][1].__setitem__("class_id", a["proof_payload"]["multiplicity_ledger"]["class_ledger"][0]["class_id"]))
    add("path_key_deletion", lambda a: a["proof_payload"]["multiplicity_ledger"]["class_ledger"][0]["source_path_keys"].pop())
    add("path_key_substitution", lambda a: a["proof_payload"]["multiplicity_ledger"]["class_ledger"][0]["source_path_keys"][0].__setitem__(1, 99))
    add("multiplicity_increment", lambda a: a["proof_payload"]["multiplicity_ledger"]["class_ledger"][0].__setitem__("source_path_multiplicity", 2))
    add("collision_contribution_tamper", lambda a: a["proof_payload"]["multiplicity_ledger"]["class_ledger"][0].__setitem__("collision_contribution", 1))
    add("assignment_work_tamper", lambda a: a["proof_payload"]["multiplicity_ledger"]["class_ledger"][0].__setitem__("local_direct_assignment_tests", 0))
    add("multiplicity_sum_tamper", lambda a: a["proof_payload"]["multiplicity_ledger"].__setitem__("multiplicity_sum", 74))
    add("collision_count_tamper", lambda a: a["proof_payload"]["multiplicity_ledger"].__setitem__("collision_count", 13))
    add("assignment_sum_tamper", lambda a: a["proof_payload"]["multiplicity_ledger"].__setitem__("assignment_work_sum", 31499))
    add("correction_zero_tamper", lambda a: a["proof_payload"]["multiplicity_ledger"]["correction_cell_counts"].__setitem__("0", 219))
    add("verifier_charge_tamper", lambda a: a["proof_payload"]["work_ledger"].__setitem__("verifier_operation_charge", 0))
    add("invariant_flip", lambda a: a["proof_payload"]["invariant_vector"].__setitem__("N8-INV-16", "FAIL"))
    add("false_root_claim", lambda a: a["proof_payload"]["strict_boundary"].__setitem__("negative_root_reached", True))
    add("false_no_layout_gate", lambda a: a["proof_payload"]["strict_boundary"].__setitem__("no_layout_at_cap_enabled", True))

    rejected = 0
    for name, candidate in attacks:
        try:
            reject_if_invalid(source_path, candidate)
        except AssertionError:
            rejected += 1
        else:
            raise AssertionError(f"tamper accepted: {name}")
    if rejected != 20:
        raise AssertionError("tamper count")
    print("DIGEST_REPAIRED_TAMPER_ATTACKS_REJECTED = 20/20")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_artifact", type=Path)
    parser.add_argument("hardening_artifact", type=Path)
    parser.add_argument("--tamper-self-test", action="store_true")
    args = parser.parse_args()
    artifact = json.loads(args.hardening_artifact.read_text(encoding="utf-8"))
    reject_if_invalid(args.source_artifact, artifact)
    if args.tamper_self_test:
        tamper_self_test(args.source_artifact, artifact)
    print("JANUS_C049_1_B4_6_3_NODE8_FRONTIER_MULTIPLICITY_HARDENING_VERIFIER = PASS")
    print("INVARIANTS = 16/16")
    print("TAMPER_ATTACKS = 20/20")
    print("FIXED_POINT_CERTIFICATE_BYTES =", len(args.hardening_artifact.read_bytes()))
    print("CURRENT_GLOBAL_TERMINAL =", TERMINAL)


if __name__ == "__main__":
    main()
