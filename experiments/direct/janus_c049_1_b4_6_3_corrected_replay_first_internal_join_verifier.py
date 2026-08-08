#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import copy
import gzip
import hashlib
import itertools
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any, Sequence

SCHEMA = "C049.1-B4.6.3-CORRECTED-FIRST-INTERNAL-JOIN-REPLAY-v1"
ENGINE_SCHEMA = "C049.1-B4.5-BOTTOM-UP-SCAFFOLD-EXECUTOR-MANIFEST-v1"
CHUNK_SCHEMA = "C049.1-B4.5-BOTTOM-UP-SCAFFOLD-EXECUTOR-CHUNK-v1"
TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"
PARENT_HEAD = "ddd18da87fd6c2721deb6b729acdea0af7cf5b6e"
PARENT_CORRECTION_SHA256 = "82e0f373eb713c82102d55f3ba1893681653920364f00d8372a275d09b562ffa"
PARENT_CORRECTION_SEMANTIC = "d28c6461d5a11cd9047ecc0090d4c368192adbe6da7720b2a5ba634c308ace31"
FIRST_INTERNAL_NODE_ID = 6
JOIN_STEPS = {(1, 0), (0, 1)}
FIXTURE_BLOCKS = [[2], [4], [6], [3], [5], [1]]


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ordinary_count(m: int, n: int) -> int:
    if m <= 0 or n <= 0:
        return 0
    return math.comb(m + n - 2, m - 1)


def xor_basis(rows: Sequence[int], d: int) -> tuple[int, ...]:
    table: dict[int, int] = {}
    for raw in rows:
        x = int(raw)
        if x < 0 or x >= (1 << d):
            raise AssertionError("vector outside ambient space")
        while x:
            pivot = x.bit_length() - 1
            if pivot in table:
                x ^= table[pivot]
                continue
            table[pivot] = x
            for other, row in list(table.items()):
                if other != pivot and ((row >> pivot) & 1):
                    table[other] = row ^ x
            break
    return tuple(table[pivot] for pivot in sorted(table, reverse=True))


def intersection_dimension(left: Sequence[int], right: Sequence[int], d: int) -> int:
    lb = xor_basis(left, d)
    rb = xor_basis(right, d)
    joined = xor_basis((*lb, *rb), d)
    return len(lb) + len(rb) - len(joined)


def exhaustive_oracle() -> dict:
    records = []
    for order in itertools.permutations(range(6)):
        vector = []
        for cut in range(1, 6):
            left = [row for factor in order[:cut] for row in FIXTURE_BLOCKS[factor]]
            right = [row for factor in order[cut:] for row in FIXTURE_BLOCKS[factor]]
            vector.append(intersection_dimension(left, right, 3))
        records.append(
            {
                "order": list(order),
                "maximum_width": max(vector),
                "width_vector": vector,
            }
        )
    minimum = min(item["maximum_width"] for item in records)
    accepting = sum(item["maximum_width"] <= 1 for item in records)
    previous = [0, 1, 2, 3, 4]
    previous_vector = []
    for cut in range(1, 5):
        left = [row for factor in previous[:cut] for row in FIXTURE_BLOCKS[factor]]
        right = [row for factor in previous[cut:] for row in FIXTURE_BLOCKS[factor]]
        previous_vector.append(intersection_dimension(left, right, 3))
    return {
        "permutation_count": 720,
        "minimum_width": minimum,
        "accepting_layout_count": accepting,
        "previous_width": max(previous_vector),
        "previous_width_vector": previous_vector,
        "all_layouts_digest": digest(records),
    }


def validate_parent(path: Path) -> dict:
    if file_sha256(path) != PARENT_CORRECTION_SHA256:
        raise AssertionError("parent correction byte digest mismatch")
    artifact = json.loads(path.read_text(encoding="utf-8"))
    if artifact.get("semantic_digest") != PARENT_CORRECTION_SEMANTIC:
        raise AssertionError("parent correction semantic digest mismatch")
    proof = artifact.get("proof_payload", {})
    if proof.get("admit_join_path_domain_correction") is not True:
        raise AssertionError("parent correction not admitted")
    if proof["path_domain_split"]["join_interleaving_steps"] != [[1, 0], [0, 1]]:
        raise AssertionError("parent ordinary domain mismatch")
    return artifact


def verify_record(record: dict) -> None:
    claimed = record.get("record_digest")
    payload = dict(record)
    payload.pop("record_digest", None)
    if claimed != digest(payload):
        raise AssertionError("record digest mismatch")


def read_chunks(root: Path, manifest: dict) -> dict[str, list[dict]]:
    groups = manifest["chunking"]["chunk_groups"]
    if manifest["chunking"]["transcript_root_digest"] != digest(groups):
        raise AssertionError("transcript root digest mismatch")
    records: dict[str, list[dict]] = {}
    for kind, metadata_group in groups.items():
        observed: list[dict] = []
        previous_digest = None
        expected_id = 0
        for index, metadata in enumerate(metadata_group):
            raw_compressed = (root / metadata["filename"]).read_bytes()
            if sha256_bytes(raw_compressed) != metadata["compressed_sha256"]:
                raise AssertionError("compressed chunk digest mismatch")
            payload = json.loads(gzip.decompress(raw_compressed))
            if payload.get("schema") != CHUNK_SCHEMA or payload.get("kind") != kind:
                raise AssertionError("chunk schema/kind mismatch")
            if int(payload["chunk_index"]) != index:
                raise AssertionError("chunk index mismatch")
            if payload.get("previous_chunk_digest") != previous_digest:
                raise AssertionError("chunk predecessor digest mismatch")
            payload_without_digest = dict(payload)
            claimed_payload_digest = payload_without_digest.pop("chunk_payload_digest")
            if claimed_payload_digest != digest(payload_without_digest):
                raise AssertionError("chunk payload digest mismatch")
            if claimed_payload_digest != metadata["chunk_payload_digest"]:
                raise AssertionError("chunk metadata payload digest mismatch")
            chunk_records = payload["records"]
            if len(chunk_records) != int(payload["record_count"]):
                raise AssertionError("chunk record count mismatch")
            id_field = payload["record_id_field"]
            for record in chunk_records:
                verify_record(record)
                if int(record[id_field]) != expected_id:
                    raise AssertionError("global record id discontinuity")
                expected_id += 1
            observed.extend(chunk_records)
            previous_digest = metadata["compressed_sha256"]
        records[kind] = observed
    return records


def path_steps(path: Sequence[Sequence[int]]) -> tuple[tuple[int, int], ...]:
    parsed = tuple((int(p[0]), int(p[1])) for p in path)
    return tuple((b[0] - a[0], b[1] - a[1]) for a, b in zip(parsed, parsed[1:]))


def summarize(root: Path, manifest: dict) -> dict:
    if manifest.get("schema") != ENGINE_SCHEMA:
        raise AssertionError("engine manifest schema mismatch")
    manifest_payload = copy.deepcopy(manifest)
    claimed_manifest_digest = manifest_payload.pop("manifest_digest")
    if claimed_manifest_digest != digest(manifest_payload):
        raise AssertionError("engine manifest digest mismatch")
    records = read_chunks(root, manifest)
    all_node_ids = {
        int(record["node_id"])
        for group in records.values()
        for record in group
    }
    if all_node_ids != {FIRST_INTERNAL_NODE_ID}:
        raise AssertionError("corrected stage contains records outside first internal join")

    pairs = records["PAIRS"]
    refinements = records["REFINEMENTS"]
    generators = records["GENERATORS"]
    deletions = records["DELETIONS"]
    if len(pairs) != 1296:
        raise AssertionError("first-join pair count mismatch")

    pair_dimensions: dict[int, tuple[int, int]] = {}
    expected_refinements = 0
    histogram: dict[str, int] = defaultdict(int)
    pair_range_sum = 0
    for pair in pairs:
        pair_id = int(pair["pair_id"])
        m = len(pair["left_expand"]["output_ambient"])
        n = len(pair["right_expand"]["output_ambient"])
        expected = ordinary_count(m, n)
        if int(pair["lattice_path_count"]) != expected:
            raise AssertionError("pair path count is not binomial")
        first = int(pair["first_attempt_id"])
        last = int(pair["last_attempt_id"])
        if last - first + 1 != expected:
            raise AssertionError("pair attempt range mismatch")
        expected_refinements += expected
        pair_range_sum += expected
        histogram[f"{m}x{n}:{expected}"] += 1
        pair_dimensions[pair_id] = (m, n)

    successful: set[int] = set()
    failed: set[int] = set()
    step_counts: dict[str, int] = defaultdict(int)
    path_vertices = 0
    for refinement in refinements:
        pair_id = int(refinement["pair_id"])
        m, n = pair_dimensions[pair_id]
        path = refinement["lattice_path"]
        if path[0] != [0, 0] or path[-1] != [m - 1, n - 1]:
            raise AssertionError("ordinary path endpoints mismatch")
        steps = path_steps(path)
        if any(step not in JOIN_STEPS for step in steps):
            raise AssertionError("non-H/V step found in corrected transcript")
        if len(path) != m + n - 1:
            raise AssertionError("ordinary path vertex count mismatch")
        for step in steps:
            step_counts[f"{step[0]},{step[1]}"] += 1
        path_vertices += len(path)
        attempt = int(refinement["attempt_id"])
        if refinement["status"] == "SUCCESS":
            successful.add(attempt)
        elif refinement["status"] == "FAILED_WIDTH_CAP":
            failed.add(attempt)
        else:
            raise AssertionError("unknown refinement status")

    provenance: list[int] = []
    for generator in generators:
        provenance.extend(int(x) for x in generator["provenance_attempt_ids"])
    removed = [int(item["removed_attempt_id"]) for item in deletions]

    if len(refinements) != expected_refinements or pair_range_sum != expected_refinements:
        raise AssertionError("ordinary refinement domain incomplete")
    if successful & failed or len(successful) + len(failed) != len(refinements):
        raise AssertionError("refinement partition invalid")
    if set(provenance) != successful or len(provenance) != len(successful):
        raise AssertionError("successful provenance invalid")
    if len(removed) != len(successful) - len(generators):
        raise AssertionError("duplicate deletion conservation invalid")

    return {
        "node_id": FIRST_INTERNAL_NODE_ID,
        "child_entry_counts": [36, 36],
        "child_pairs": len(pairs),
        "ordinary_refinements": len(refinements),
        "ordinary_refinements_from_pair_counts": expected_refinements,
        "successful_refinements": len(successful),
        "failed_refinements": len(failed),
        "unique_successful_generators": len(generators),
        "duplicate_successful_outputs_deleted": len(deletions),
        "ordinary_step_counts": dict(sorted(step_counts.items())),
        "diagonal_steps": 0,
        "path_vertices": path_vertices,
        "pair_path_histogram": dict(sorted(histogram.items())),
        "generator_family_digest": digest(
            sorted(
                (item["trajectory_parent_coordinates"] for item in generators),
                key=canonical_json,
            )
        ),
        "refinement_partition_complete": True,
        "successful_provenance_complete": True,
        "duplicate_deletion_conservation": True,
    }


def serialized_artifact(proof: dict) -> bytes:
    payload = copy.deepcopy(proof)
    payload["certificate_bytes"] = 0
    while True:
        artifact = {
            "schema": SCHEMA,
            "semantic_digest_scope": "proof_payload",
            "proof_payload": payload,
            "semantic_digest": digest(payload),
        }
        raw = json.dumps(artifact, indent=2, sort_keys=True).encode() + b"\n"
        if int(payload["certificate_bytes"]) == len(raw):
            return raw
        payload["certificate_bytes"] = len(raw)


def expected_proof(parent: dict, root: Path, manifest: dict) -> dict:
    receipt = summarize(root, manifest)
    execution = manifest["execution"]
    processed = [int(x) for x in execution["processed_internal_node_ids"]]
    stop = execution["stop"]
    if stop is None or stop.get("no_layout_at_cap") is not False:
        raise AssertionError("partial corrected replay terminal mismatch")
    node6_complete = FIRST_INTERNAL_NODE_ID in processed
    if node6_complete:
        if stop["status"] != "OPEN_AFTER_CORRECTED_FIRST_INTERNAL_JOIN":
            raise AssertionError("stage boundary mismatch after complete node 6")
        node6 = next(
            item for item in manifest["node_results"]
            if int(item["node_id"]) == FIRST_INTERNAL_NODE_ID
        )
        output_receipt = copy.deepcopy(node6["output_receipt"])
        retained = int(node6["audit"]["retained_generators"])
        entries = int(node6["audit"]["final_up_k_entries"])
        b2_open = None
        result = "CORRECTED_NODE6_FULL_SET_COMPUTED"
        next_gate = "C049.1_B4.6.3_CORRECTED_NODE7_PARENT_REFINEMENT"
    else:
        if stop["status"] != "OPEN_AT_CORRECTED_NODE6_B2_CAPABILITY":
            raise AssertionError("unexpected corrected node-6 stop")
        output_receipt = None
        retained = None
        entries = None
        b2_open = copy.deepcopy(stop)
        result = "HONEST_OPEN_AT_CORRECTED_NODE6_B2_CAPABILITY"
        next_gate = "C049.1_B4.6.3_CORRECTED_NODE6_UP_K_HARDENING"

    return {
        "source": {
            "parent_pr": 108,
            "parent_exact_head": PARENT_HEAD,
            "parent_correction_sha256": PARENT_CORRECTION_SHA256,
            "parent_correction_semantic_digest": PARENT_CORRECTION_SEMANTIC,
            "parent_correction_artifact_semantic_digest": parent["semantic_digest"],
        },
        "fixture_oracle": exhaustive_oracle(),
        "corrected_path_domain": {
            "join_interleaving_steps": [[1, 0], [0, 1]],
            "extension_preorder_diagonal_preserved": True,
            "ordinary_path_count_formula": "C(m+n-2,m-1)",
            "legacy_delannoy_join_domain_used": False,
        },
        "first_internal_join_receipt": receipt,
        "engine_manifest_digest": manifest["manifest_digest"],
        "engine_transcript_root_digest": manifest["chunking"]["transcript_root_digest"],
        "engine_execution": copy.deepcopy(execution),
        "node6_full_set_complete": node6_complete,
        "node6_output_receipt": output_receipt,
        "node6_retained_generators": retained,
        "node6_up_k_entries": entries,
        "node6_b2_open_receipt": b2_open,
        "legacy_inputs": {
            "legacy_node6_full_set_consumed": False,
            "legacy_node7_full_set_consumed": False,
            "legacy_node8_full_set_consumed": False,
            "legacy_node9_full_set_consumed": False,
            "supplied_layout_used_for_discovery": False,
        },
        "invariant_vector": {f"CRJ-INV-{i:02d}": "PASS" for i in range(1, 13)},
        "strict_boundary": {
            "pr108_join_path_domain_correction_admitted": True,
            "corrected_first_internal_join_replayed": True,
            "corrected_node6_parent_refinement_complete": True,
            "corrected_node6_parent_up_k_complete": node6_complete,
            "corrected_bottom_up_replay_complete": False,
            "root_structural_compression_admitted": False,
            "root_parent_refinement_complete": False,
            "root_full_set_computed": False,
            "root_empty_proved": False,
            "found_layout": "FORBIDDEN",
            "no_layout_at_cap": "FORBIDDEN",
            "current_global_terminal": TERMINAL,
            "p_vs_np": "OPEN",
        },
        "result": result,
        "next_gate": next_gate,
    }


def static_source_audit(path: Path) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
    forbidden_fragments = (
        "node6_up_k_integration",
        "node7_frontier",
        "node7_thirteen",
        "node8_frontier",
        "node8_up_k",
        "node9_frontier",
        "node9_up_k",
        "root_parent_frontier",
    )
    if any(fragment in name for name in imports for fragment in forbidden_fragments):
        raise AssertionError("producer imports a legacy downstream full-set theorem")
    if "janus_c049_1_b3_join_path_domain_corrected" not in imports:
        raise AssertionError("producer does not import the admitted corrected join API")


def verify(
    parent_path: Path,
    root: Path,
    certificate_path: Path,
    producer_source: Path | None = None,
    artifact_override: dict | None = None,
) -> dict:
    parent = validate_parent(parent_path)
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    expected = expected_proof(parent, root, manifest)
    artifact = artifact_override or json.loads(certificate_path.read_text(encoding="utf-8"))
    if artifact.get("schema") != SCHEMA:
        raise AssertionError("certificate schema mismatch")
    proof = artifact.get("proof_payload")
    candidate = copy.deepcopy(proof)
    candidate.pop("certificate_bytes", None)
    if candidate != expected:
        raise AssertionError("certificate proof payload differs from independent replay")
    expected_raw = serialized_artifact(expected)
    expected_artifact = json.loads(expected_raw)
    if artifact != expected_artifact:
        raise AssertionError("certificate fixed-point bytes or semantic digest mismatch")
    if certificate_path.exists() and artifact_override is None:
        if certificate_path.read_bytes() != expected_raw:
            raise AssertionError("certificate file bytes differ from independent construction")
    if producer_source is not None:
        static_source_audit(producer_source)
    return artifact


def repaired(candidate: dict) -> dict:
    proof = copy.deepcopy(candidate["proof_payload"])
    return json.loads(serialized_artifact(proof))


def tamper_self_test(
    parent_path: Path,
    root: Path,
    certificate_path: Path,
    producer_source: Path | None,
) -> None:
    original = json.loads(certificate_path.read_text(encoding="utf-8"))
    mutators = [
        lambda p: p["first_internal_join_receipt"].__setitem__("child_pairs", 1295),
        lambda p: p["first_internal_join_receipt"].__setitem__("ordinary_refinements", 1),
        lambda p: p["first_internal_join_receipt"].__setitem__("diagonal_steps", 1),
        lambda p: p["first_internal_join_receipt"].__setitem__("generator_family_digest", "0" * 64),
        lambda p: p["source"].__setitem__("parent_exact_head", "0" * 40),
        lambda p: p["legacy_inputs"].__setitem__("legacy_node6_full_set_consumed", True),
        lambda p: p["strict_boundary"].__setitem__("root_full_set_computed", True),
        lambda p: p["strict_boundary"].__setitem__("found_layout", "TRUE"),
        lambda p: p.__setitem__("next_gate", "ROOT_PARENT_FRONTIER_STRUCTURAL_COMPRESSION"),
        lambda p: p.__setitem__("result", "FOUND_LAYOUT"),
    ]
    rejected = 0
    for mutate in mutators:
        candidate = copy.deepcopy(original)
        mutate(candidate["proof_payload"])
        candidate = repaired(candidate)
        try:
            verify(
                parent_path,
                root,
                certificate_path,
                producer_source,
                artifact_override=candidate,
            )
        except AssertionError:
            rejected += 1
    if rejected != len(mutators):
        raise AssertionError("not every digest-repaired tamper was rejected")
    print(f"DIGEST_REPAIRED_TAMPERS_REJECTED = {rejected}/{len(mutators)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("parent_correction", type=Path)
    parser.add_argument("replay_root", type=Path)
    parser.add_argument("certificate", type=Path)
    parser.add_argument("--producer-source", type=Path)
    parser.add_argument("--tamper-self-test", action="store_true")
    args = parser.parse_args()
    artifact = verify(
        args.parent_correction,
        args.replay_root,
        args.certificate,
        args.producer_source,
    )
    if args.tamper_self_test:
        tamper_self_test(
            args.parent_correction,
            args.replay_root,
            args.certificate,
            args.producer_source,
        )
    proof = artifact["proof_payload"]
    receipt = proof["first_internal_join_receipt"]
    print("JANUS_C049_1_B4_6_3_CORRECTED_FIRST_INTERNAL_JOIN_VERIFIER = PASS")
    print("NODE6_CHILD_PAIRS =", receipt["child_pairs"])
    print("NODE6_ORDINARY_REFINEMENTS =", receipt["ordinary_refinements"])
    print("NODE6_DIAGONAL_STEPS =", receipt["diagonal_steps"])
    print("RESULT =", proof["result"])
    print("NEXT_GATE =", proof["next_gate"])


if __name__ == "__main__":
    main()
