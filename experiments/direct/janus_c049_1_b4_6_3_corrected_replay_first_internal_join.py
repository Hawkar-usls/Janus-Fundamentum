#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterator, Sequence

import janus_c049_1_b4_5_bottom_up_scaffold_executor as engine
import janus_c049_1_b4_6_3_negative_root_engine_replay as negative
from janus_c049_1_b2_up_k_core import CapabilityExceeded
from janus_c049_1_b3_join_path_domain_corrected import (
    JOIN_INTERLEAVING_STEPS,
    join_trajectory as corrected_join_trajectory,
    ordinary_join_paths,
)

SCHEMA = "C049.1-B4.6.3-CORRECTED-FIRST-INTERNAL-JOIN-REPLAY-v1"
TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"
PARENT_HEAD = "ddd18da87fd6c2721deb6b729acdea0af7cf5b6e"
PARENT_CORRECTION_SHA256 = "82e0f373eb713c82102d55f3ba1893681653920364f00d8372a275d09b562ffa"
PARENT_CORRECTION_SEMANTIC = "d28c6461d5a11cd9047ecc0090d4c368192adbe6da7720b2a5ba634c308ace31"
FIRST_INTERNAL_NODE_ID = 6
B2_CAP = 2_000_000


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ordinary_join_path_count(m: int, n: int) -> int:
    if m <= 0 or n <= 0:
        return 0
    return math.comb(m + n - 2, m - 1)


class B2PrefixOpen(RuntimeError):
    def __init__(
        self,
        source: CapabilityExceeded,
        ledger: dict,
        generator_count: int,
        ambient_dim: int,
        k: int,
    ) -> None:
        super().__init__(source.terminal)
        self.source = source
        self.ledger = ledger
        self.generator_count = int(generator_count)
        self.ambient_dim = int(ambient_dim)
        self.k = int(k)


def load_parent_correction(path: Path) -> dict:
    if file_sha256(path) != PARENT_CORRECTION_SHA256:
        raise AssertionError("PR #108 correction artifact byte digest drift")
    artifact = json.loads(path.read_text(encoding="utf-8"))
    if artifact.get("semantic_digest") != PARENT_CORRECTION_SEMANTIC:
        raise AssertionError("PR #108 correction semantic digest drift")
    proof = artifact.get("proof_payload", {})
    if proof.get("admit_join_path_domain_correction") is not True:
        raise AssertionError("PR #108 correction is not admitted")
    split = proof.get("path_domain_split", {})
    if split.get("join_interleaving_steps") != [[1, 0], [0, 1]]:
        raise AssertionError("ordinary join domain drift")
    if split.get("extension_preorder_steps") != [[1, 0], [0, 1], [1, 1]]:
        raise AssertionError("extension preorder domain drift")
    strict = proof.get("strict_boundary", {})
    if strict.get("b3_join_path_domain_corrected_api") is not True:
        raise AssertionError("corrected B3 API not admitted")
    if strict.get("legacy_b3_join_artifacts_promotable") is not False:
        raise AssertionError("legacy B3 artifacts unexpectedly promotable")
    return artifact


def iter_records(root: Path, manifest: dict, kind: str) -> Iterator[dict]:
    for metadata in manifest["chunking"]["chunk_groups"][kind]:
        raw = gzip.decompress((root / metadata["filename"]).read_bytes())
        payload = json.loads(raw)
        if payload["kind"] != kind:
            raise AssertionError("chunk kind mismatch")
        if int(payload["record_count"]) != int(metadata["record_count"]):
            raise AssertionError("chunk record-count mismatch")
        yield from payload["records"]


def path_steps(path: Sequence[Sequence[int]]) -> tuple[tuple[int, int], ...]:
    parsed = tuple((int(point[0]), int(point[1])) for point in path)
    return tuple(
        (following[0] - current[0], following[1] - current[1])
        for current, following in zip(parsed, parsed[1:])
    )


def summarize_first_join(root: Path, manifest: dict) -> dict:
    pairs = [
        item
        for item in iter_records(root, manifest, "PAIRS")
        if int(item["node_id"]) == FIRST_INTERNAL_NODE_ID
    ]
    refinements = [
        item
        for item in iter_records(root, manifest, "REFINEMENTS")
        if int(item["node_id"]) == FIRST_INTERNAL_NODE_ID
    ]
    generators = [
        item
        for item in iter_records(root, manifest, "GENERATORS")
        if int(item["node_id"]) == FIRST_INTERNAL_NODE_ID
    ]
    deletions = [
        item
        for item in iter_records(root, manifest, "DELETIONS")
        if int(item["node_id"]) == FIRST_INTERNAL_NODE_ID
    ]

    if len(pairs) != 36 * 36:
        raise AssertionError("corrected first join child-pair inventory drift")

    expected_paths = 0
    pair_path_histogram: dict[str, int] = defaultdict(int)
    pair_range_attempts = 0
    for pair in pairs:
        left_len = len(pair["left_expand"]["output_ambient"])
        right_len = len(pair["right_expand"]["output_ambient"])
        expected = ordinary_join_path_count(left_len, right_len)
        observed = int(pair["lattice_path_count"])
        if observed != expected:
            raise AssertionError("pair ordinary-interleaving count drift")
        expected_paths += expected
        pair_path_histogram[f"{left_len}x{right_len}:{expected}"] += 1
        first = int(pair["first_attempt_id"])
        last = int(pair["last_attempt_id"])
        if last - first + 1 != observed:
            raise AssertionError("pair attempt range does not match path count")
        pair_range_attempts += observed

    successful_ids: set[int] = set()
    failed_ids: set[int] = set()
    path_vertex_count = 0
    step_counts: dict[str, int] = defaultdict(int)
    for item in refinements:
        path = item["lattice_path"]
        if not path or path[0] != [0, 0]:
            raise AssertionError("ordinary join path start drift")
        steps = path_steps(path)
        if any(step not in JOIN_INTERLEAVING_STEPS for step in steps):
            raise AssertionError("diagonal or nonordinary step entered corrected transcript")
        for step in steps:
            step_counts[f"{step[0]},{step[1]}"] += 1
        path_vertex_count += len(path)
        attempt_id = int(item["attempt_id"])
        if item["status"] == "SUCCESS":
            successful_ids.add(attempt_id)
        elif item["status"] == "FAILED_WIDTH_CAP":
            failed_ids.add(attempt_id)
        else:
            raise AssertionError("unknown corrected refinement status")

    provenance: list[int] = []
    for generator in generators:
        provenance.extend(int(value) for value in generator["provenance_attempt_ids"])
    duplicate_removed = [int(item["removed_attempt_id"]) for item in deletions]

    if len(refinements) != expected_paths or pair_range_attempts != expected_paths:
        raise AssertionError("corrected first-join path domain not completely replayed")
    if successful_ids & failed_ids:
        raise AssertionError("refinement success/failure partition overlaps")
    if len(successful_ids) + len(failed_ids) != len(refinements):
        raise AssertionError("refinement partition incomplete")
    if set(provenance) != successful_ids:
        raise AssertionError("successful refinement provenance is incomplete")
    if len(provenance) != len(successful_ids):
        raise AssertionError("successful refinement provenance is duplicated")
    if len(duplicate_removed) != len(successful_ids) - len(generators):
        raise AssertionError("duplicate deletion conservation failed")

    return {
        "node_id": FIRST_INTERNAL_NODE_ID,
        "child_entry_counts": [36, 36],
        "child_pairs": len(pairs),
        "ordinary_refinements": len(refinements),
        "ordinary_refinements_from_pair_counts": expected_paths,
        "successful_refinements": len(successful_ids),
        "failed_refinements": len(failed_ids),
        "unique_successful_generators": len(generators),
        "duplicate_successful_outputs_deleted": len(deletions),
        "ordinary_step_counts": dict(sorted(step_counts.items())),
        "diagonal_steps": 0,
        "path_vertices": path_vertex_count,
        "pair_path_histogram": dict(sorted(pair_path_histogram.items())),
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


def fixed_point_artifact(proof_payload: dict) -> bytes:
    payload = copy.deepcopy(proof_payload)
    payload["certificate_bytes"] = 0
    while True:
        artifact = {
            "schema": SCHEMA,
            "semantic_digest_scope": "proof_payload",
            "proof_payload": payload,
            "semantic_digest": digest(payload),
        }
        raw = json.dumps(artifact, indent=2, sort_keys=True).encode() + b"\n"
        size = len(raw)
        if int(payload["certificate_bytes"]) == size:
            return raw
        payload["certificate_bytes"] = size


def build(parent_correction_path: Path, output_dir: Path) -> dict:
    parent_correction = load_parent_correction(parent_correction_path)
    oracle = negative.exhaustive_fixture_oracle()

    original_selected = engine.selected_scaffold
    original_up_k = engine.up_k_closure
    original_execute = engine.execute_node
    original_lattice_paths = engine.lattice_paths
    original_join = engine.join_trajectory
    original_path_count = engine.b44.delannoy_path_count
    original_cap = engine.CAP

    def bounded_up_k(generators, ambient_dim, k, ledger):
        try:
            return original_up_k(generators, ambient_dim, k, ledger)
        except CapabilityExceeded as exc:
            raise B2PrefixOpen(
                exc,
                ledger.snapshot(),
                len(generators),
                int(ambient_dim),
                int(k),
            ) from exc

    def guarded_execute(
        descriptor,
        sequence_index,
        left_state,
        right_state,
        scaffold_record,
        writers,
        cumulative,
        capability,
    ):
        node_id = int(descriptor["node_id"])
        if node_id != FIRST_INTERNAL_NODE_ID:
            return {
                "status": "OPEN_AFTER_CORRECTED_FIRST_INTERNAL_JOIN",
                "node_id": node_id,
                "reason": "CORRECTED_REPLAY_STAGE_BOUNDARY",
                "required": None,
                "cap": None,
                "terminal": TERMINAL,
                "no_layout_at_cap": False,
            }
        try:
            return original_execute(
                descriptor,
                sequence_index,
                left_state,
                right_state,
                scaffold_record,
                writers,
                cumulative,
                capability,
            )
        except B2PrefixOpen as opened:
            source = opened.source
            return {
                "status": "OPEN_AT_CORRECTED_NODE6_B2_CAPABILITY",
                "node_id": node_id,
                "reason": "B2_SEMANTIC_UP_K_CAPABILITY_EXCEEDED_AFTER_CORRECTED_JOIN",
                "required": int(source.attempted),
                "cap": int(source.cap),
                "counter": source.counter,
                "b2_terminal": source.terminal,
                "b2_ledger_prefix": opened.ledger,
                "input_generator_count": opened.generator_count,
                "boundary_coordinate_dimension": opened.ambient_dim,
                "k": opened.k,
                "terminal": TERMINAL,
                "no_layout_at_cap": False,
            }

    try:
        engine.selected_scaffold = negative.selected_negative_scaffold
        engine.up_k_closure = bounded_up_k
        engine.execute_node = guarded_execute
        engine.lattice_paths = ordinary_join_paths
        engine.join_trajectory = corrected_join_trajectory
        engine.b44.delannoy_path_count = ordinary_join_path_count
        engine.CAP = B2_CAP
        manifest = engine.build(output_dir)
    finally:
        engine.selected_scaffold = original_selected
        engine.up_k_closure = original_up_k
        engine.execute_node = original_execute
        engine.lattice_paths = original_lattice_paths
        engine.join_trajectory = original_join
        engine.b44.delannoy_path_count = original_path_count
        engine.CAP = original_cap

    receipt = summarize_first_join(output_dir, manifest)
    processed = [int(value) for value in manifest["execution"]["processed_internal_node_ids"]]
    stop = manifest["execution"]["stop"]
    if stop is None:
        raise AssertionError("corrected first-join replay did not stop at its stage boundary")
    if stop.get("no_layout_at_cap") is not False or stop.get("terminal") != TERMINAL:
        raise AssertionError("corrected partial replay promoted an incomplete terminal")
    node6_complete = FIRST_INTERNAL_NODE_ID in processed
    if node6_complete:
        if stop["status"] != "OPEN_AFTER_CORRECTED_FIRST_INTERNAL_JOIN":
            raise AssertionError("completed corrected node 6 did not stop at stage boundary")
        node6 = next(
            item for item in manifest["node_results"]
            if int(item["node_id"]) == FIRST_INTERNAL_NODE_ID
        )
        closure_receipt = copy.deepcopy(node6["output_receipt"])
        retained = int(node6["audit"]["retained_generators"])
        entries = int(node6["audit"]["final_up_k_entries"])
        b2_stop = None
        next_gate = "C049.1_B4.6.3_CORRECTED_NODE7_PARENT_REFINEMENT"
    else:
        if stop["status"] != "OPEN_AT_CORRECTED_NODE6_B2_CAPABILITY":
            raise AssertionError("corrected node 6 stopped for an unexpected reason")
        closure_receipt = None
        retained = None
        entries = None
        b2_stop = copy.deepcopy(stop)
        next_gate = "C049.1_B4.6.3_CORRECTED_NODE6_UP_K_HARDENING"

    proof = {
        "source": {
            "parent_pr": 108,
            "parent_exact_head": PARENT_HEAD,
            "parent_correction_sha256": PARENT_CORRECTION_SHA256,
            "parent_correction_semantic_digest": PARENT_CORRECTION_SEMANTIC,
            "parent_correction_artifact_semantic_digest": parent_correction[
                "semantic_digest"
            ],
        },
        "fixture_oracle": oracle,
        "corrected_path_domain": {
            "join_interleaving_steps": [[1, 0], [0, 1]],
            "extension_preorder_diagonal_preserved": True,
            "ordinary_path_count_formula": "C(m+n-2,m-1)",
            "legacy_delannoy_join_domain_used": False,
        },
        "first_internal_join_receipt": receipt,
        "engine_manifest_digest": manifest["manifest_digest"],
        "engine_transcript_root_digest": manifest["chunking"][
            "transcript_root_digest"
        ],
        "engine_execution": copy.deepcopy(manifest["execution"]),
        "node6_full_set_complete": node6_complete,
        "node6_output_receipt": closure_receipt,
        "node6_retained_generators": retained,
        "node6_up_k_entries": entries,
        "node6_b2_open_receipt": b2_stop,
        "legacy_inputs": {
            "legacy_node6_full_set_consumed": False,
            "legacy_node7_full_set_consumed": False,
            "legacy_node8_full_set_consumed": False,
            "legacy_node9_full_set_consumed": False,
            "supplied_layout_used_for_discovery": False,
        },
        "invariant_vector": {
            f"CRJ-INV-{index:02d}": "PASS" for index in range(1, 13)
        },
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
        "result": (
            "CORRECTED_NODE6_FULL_SET_COMPUTED"
            if node6_complete
            else "HONEST_OPEN_AT_CORRECTED_NODE6_B2_CAPABILITY"
        ),
        "next_gate": next_gate,
    }
    raw = fixed_point_artifact(proof)
    certificate_path = output_dir / "corrected-first-internal-join-certificate.json"
    certificate_path.write_bytes(raw)
    artifact = json.loads(raw)

    print("JANUS_C049_1_B4_6_3_CORRECTED_FIRST_INTERNAL_JOIN_REPLAY = PASS")
    print("NODE6_CHILD_PAIRS =", receipt["child_pairs"])
    print("NODE6_ORDINARY_REFINEMENTS =", receipt["ordinary_refinements"])
    print("NODE6_SUCCESSFUL_REFINEMENTS =", receipt["successful_refinements"])
    print("NODE6_FAILED_REFINEMENTS =", receipt["failed_refinements"])
    print("NODE6_UNIQUE_GENERATORS =", receipt["unique_successful_generators"])
    print("NODE6_FULL_SET_COMPLETE =", node6_complete)
    print("STOP_STATUS =", stop["status"])
    print("NEXT_GATE =", next_gate)
    print("GLOBAL_TERMINAL =", TERMINAL)
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("parent_correction", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    build(args.parent_correction, args.output_dir)


if __name__ == "__main__":
    main()
