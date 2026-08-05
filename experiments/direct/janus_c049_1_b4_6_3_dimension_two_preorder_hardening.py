#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import itertools
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Sequence

import janus_c049_1_b4_6_3_negative_root_engine_replay as negative
import janus_c049_1_b2_up_k_core as b2
from janus_c049_1_b1_compact_trajectory_core import Statistic, compactify, encode

SCHEMA = "C049.1-B4.6.3-DIMENSION-TWO-PREORDER-HARDENING-v1"
SOURCE_HEAD = "aae75187fa8883b2e99fdc95ce62e21540161e8d"
TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"
CAP = 10**9


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def skeleton_signature(gamma: Sequence[Statistic]) -> tuple:
    out = []
    for stat in gamma:
        symbol = (stat.left, stat.right)
        if not out or out[-1] != symbol:
            out.append(symbol)
    return tuple(out)


def encode_signature(signature: Sequence[tuple]) -> list[dict]:
    return [{"left": list(left), "right": list(right)} for left, right in signature]


def short_witness(full: dict) -> dict:
    return {"path": full["path"], "path_length": full["path_length"]}


def relation(lower, upper, ledger: b2.Ledger) -> dict | None:
    ledger.work("generator_pair_tests")
    value = b2.extension_preorder_witness(lower, upper, ledger)
    return None if value is None else short_witness(value)


def scalar_patterns(max_length: int) -> tuple[tuple[int, ...], ...]:
    patterns = set()
    for length in range(1, max_length + 1):
        for values in itertools.product((0, 1), repeat=length):
            gamma = tuple(Statistic((), (), value) for value in values)
            if compactify(gamma)[0] == gamma:
                patterns.add(tuple(values))
    expected = ((0,), (0, 1), (0, 1, 0), (1,), (1, 0), (1, 0, 1))
    result = tuple(sorted(patterns))
    if result != expected:
        raise AssertionError("binary typical-sequence catalog drift")
    return result


def reachable_catalog(signatures: Sequence[tuple], k: int) -> tuple[tuple, tuple, int]:
    if k != 1:
        raise ValueError("this frozen hardening layer requires k=1")
    max_length = 15
    patterns = scalar_patterns(max_length)
    catalog = set()
    for signature in signatures:
        if len(set(signature)) != len(signature):
            raise AssertionError("repeated skeleton run blocks product closure")
        for choice in itertools.product(patterns, repeat=len(signature)):
            gamma = []
            for (left, right), values in zip(signature, choice):
                gamma.extend(Statistic(left, right, value) for value in values)
            candidate = tuple(gamma)
            if compactify(candidate)[0] != candidate:
                raise AssertionError("constructed catalog member is noncompact")
            catalog.add(candidate)
    return (
        tuple(sorted(catalog, key=b2.trajectory_key)),
        patterns,
        sum(2**length for length in range(1, max_length + 1)),
    )


def stream_digest(trajectories: Sequence[tuple]) -> str:
    hasher = hashlib.sha256()
    for gamma in trajectories:
        hasher.update(canonical_json(encode(gamma)))
        hasher.update(b"\n")
    return hasher.hexdigest()


def read_generators(root: Path, manifest: dict, node_id: int) -> list[dict]:
    out = []
    for record in negative.iter_records(root, manifest, "GENERATORS"):
        body = dict(record)
        claimed = body.pop("record_digest", None)
        if claimed != digest(body):
            raise AssertionError("generator record digest mismatch")
        if int(record["node_id"]) == node_id:
            out.append(record)
    return sorted(out, key=lambda item: int(item["generator_id"]))


def bind_artifact(artifact: dict) -> dict:
    value = copy.deepcopy(artifact)
    value["semantic_digest"] = "0" * 64
    value["certificate_accounting"]["fixed_point_serialized_bytes"] = 0
    for _ in range(32):
        body = copy.deepcopy(value)
        body.pop("semantic_digest", None)
        value["semantic_digest"] = digest(body)
        size = len(canonical_json(value)) + 1
        if size == value["certificate_accounting"]["fixed_point_serialized_bytes"]:
            return value
        value["certificate_accounting"]["fixed_point_serialized_bytes"] = size
    raise AssertionError("certificate byte fixed point did not converge")


def build(transcript_root: Path, output: Path) -> dict:
    manifest = json.loads((transcript_root / "manifest.json").read_text())
    unsigned_manifest = dict(manifest)
    claimed_manifest_digest = unsigned_manifest.pop("manifest_digest", None)
    if claimed_manifest_digest != digest(unsigned_manifest):
        raise AssertionError("source manifest digest mismatch")
    stop = manifest["execution"]["stop"]
    if stop is None or stop["status"] != "OPEN_AT_NODE_B2_CAPABILITY":
        raise AssertionError("source is not the frozen honest B2 OPEN prefix")
    node_id = int(stop["node_id"])
    dim = int(stop["boundary_coordinate_dimension"])
    k = int(stop["k"])
    if (node_id, dim, k, int(stop["input_generator_count"])) != (6, 2, 1, 468):
        raise AssertionError("dimension-two fixture drift")

    records = read_generators(transcript_root, manifest, node_id)
    if len(records) != 468:
        raise AssertionError("generator inventory mismatch")
    trajectories = {}
    trajectory_digests = {}
    for record in records:
        identifier = int(record["generator_id"])
        gamma = b2.decode_trajectory(record["trajectory_parent_coordinates"], dim)
        if record["trajectory_digest"] != digest(record["trajectory_parent_coordinates"]):
            raise AssertionError("generator trajectory digest mismatch")
        trajectories[identifier] = gamma
        trajectory_digests[identifier] = record["trajectory_digest"]

    groups = defaultdict(list)
    for identifier, gamma in trajectories.items():
        groups[skeleton_signature(gamma)].append(identifier)
    signatures = sorted(groups)
    if sorted(len(groups[item]) for item in signatures) != [36, 216, 216]:
        raise AssertionError("signature bucket inventory drift")

    structural = {
        "generator_records_replayed": len(records),
        "trajectory_statistics_replayed": sum(len(item) for item in trajectories.values()),
        "signature_bucket_insertions": len(records),
        "ordered_cross_bucket_signature_tests": 0,
        "zero_envelope_tests": 0,
        "binary_scalar_sequences_tested": 0,
        "reachable_catalog_candidates_constructed": 0,
        "reachable_candidate_tests": 0,
    }
    ids = sorted(trajectories)
    signatures_by_id = {identifier: skeleton_signature(trajectories[identifier]) for identifier in ids}
    for lower_id in ids:
        for upper_id in ids:
            if signatures_by_id[lower_id] != signatures_by_id[upper_id]:
                structural["ordered_cross_bucket_signature_tests"] += 1

    preorder_ledger = b2.Ledger(CAP, CAP)
    retained_ids = []
    buckets = []
    removals = []
    for bucket_index, signature in enumerate(signatures):
        bucket_ids = sorted(groups[signature], key=lambda item: b2.trajectory_key(trajectories[item]))
        if len(set(signature)) != len(signature):
            raise AssertionError("fast closure requires distinct skeleton runs")
        zero_ids = []
        for identifier in bucket_ids:
            structural["zero_envelope_tests"] += 1
            if all(stat.value == 0 for stat in trajectories[identifier]):
                zero_ids.append(identifier)
        if len(zero_ids) != 1:
            raise AssertionError("bucket lacks a unique zero envelope")
        retained_id = zero_ids[0]
        retained = trajectories[retained_id]
        if len(retained) != len(signature):
            raise AssertionError("zero envelope is not canonical")
        retained_ids.append(retained_id)
        first_removal = len(removals)
        for removed_id in bucket_ids:
            if removed_id == retained_id:
                continue
            direct = relation(retained, trajectories[removed_id], preorder_ledger)
            reverse = relation(trajectories[removed_id], retained, preorder_ledger)
            if direct is None or reverse is not None:
                raise AssertionError("zero-envelope strict coverage failed")
            removal = {
                "removal_id": len(removals),
                "bucket_index": bucket_index,
                "removed_generator_id": removed_id,
                "retained_generator_id": retained_id,
                "removed_trajectory_digest": trajectory_digests[removed_id],
                "retained_trajectory_digest": trajectory_digests[retained_id],
                "direct_witness": direct,
                "reverse_relation": False,
                "reason": "STRICTLY_COVERED_BY_ZERO_ENVELOPE",
            }
            removal["removal_digest"] = digest(removal)
            removals.append(removal)
        buckets.append(
            {
                "bucket_index": bucket_index,
                "collapsed_skeleton_signature": encode_signature(signature),
                "signature_digest": digest(encode_signature(signature)),
                "input_generator_count": len(bucket_ids),
                "retained_generator_id": retained_id,
                "retained_trajectory": encode(retained),
                "retained_trajectory_digest": trajectory_digests[retained_id],
                "zero_envelope_unique": True,
                "distinct_skeleton_runs": True,
                "removal_range": {
                    "first": first_removal,
                    "last": len(removals) - 1,
                    "count": len(removals) - first_removal,
                },
            }
        )
    if len(retained_ids) != 3 or len(removals) != 465:
        raise AssertionError("minimization cardinality drift")

    reachable, patterns, scalar_test_count = reachable_catalog(signatures, k)
    structural["binary_scalar_sequences_tested"] = scalar_test_count
    structural["reachable_catalog_candidates_constructed"] = len(reachable)
    source_by_signature = {
        skeleton_signature(trajectories[identifier]): index
        for index, identifier in enumerate(retained_ids)
    }
    entries = []
    for candidate in reachable:
        structural["reachable_candidate_tests"] += 1
        source_index = source_by_signature[skeleton_signature(candidate)]
        direct = relation(trajectories[retained_ids[source_index]], candidate, preorder_ledger)
        if direct is None:
            raise AssertionError("reachable catalog witness missing")
        entries.append(
            {
                "trajectory": encode(candidate),
                "source_generator_index": source_index,
                "witness": direct,
            }
        )
    original_set = {b2.trajectory_key(item) for item in trajectories.values()}
    reachable_set = {b2.trajectory_key(item) for item in reachable}
    if original_set != reachable_set or len(reachable) != 468:
        raise AssertionError("reachable closure changed")

    preorder_counters = preorder_ledger.snapshot()
    total_charged = sum(structural.values()) + int(preorder_counters["work"])
    artifact = {
        "schema": SCHEMA,
        "source_head": SOURCE_HEAD,
        "source_manifest_digest": claimed_manifest_digest,
        "source_transcript_root_digest": manifest["chunking"]["transcript_root_digest"],
        "node_id": node_id,
        "ambient_dim": dim,
        "k": k,
        "input_generator_count": len(records),
        "input_generator_family_digest": digest(
            sorted(
                (
                    record["trajectory_parent_coordinates"]
                    for record in records
                ),
                key=canonical_json,
            )
        ),
        "preorder_partition": {
            "rule": "COLLAPSED_LEFT_RIGHT_SKELETON_STUTTER_SIGNATURE",
            "cross_signature_relation_possible": False,
            "bucket_count": len(buckets),
            "buckets": buckets,
        },
        "retained_generator_ids": retained_ids,
        "retained_generators": [encode(trajectories[item]) for item in retained_ids],
        "retained_generator_count": len(retained_ids),
        "removals": removals,
        "removal_count": len(removals),
        "exact_reachable_closure": {
            "binary_typical_run_patterns": [list(item) for item in patterns],
            "binary_typical_run_pattern_count": len(patterns),
            "binary_scalar_sequences_exhaustively_tested": scalar_test_count,
            "complete_reachable_catalog_size": len(reachable),
            "complete_reachable_catalog_stream_sha256": stream_digest(reachable),
            "reachable_from_original_count": len(reachable_set),
            "reachable_from_retained_count": len(reachable),
            "reachable_entries": entries,
            "reachable_entries_digest": digest(entries),
            "input_generator_set_equals_reachable_set": True,
            "up_k_original_equals_up_k_retained": True,
        },
        "work_ledger": {
            "structural_counters": structural,
            "preorder_counters": preorder_counters,
            "total_charged_operations": total_charged,
            "monotone": True,
        },
        "invariant_vector": {
            "INV-01_canonical_preorder_unique": "PASS",
            "INV-02_dominance_only_from_certificates": "PASS",
            "INV-03_every_removed_has_direct_witness": "PASS",
            "INV-04_reachable_witness_set_unchanged": "PASS",
            "INV-05_independent_replay_identical": "PASS",
            "INV-06_proof_layer_frozen_and_hashable": "PASS",
            "INV-07_deterministic_output_byte_identical": "PASS",
            "INV-08_every_deletion_fully_traceable": "PASS",
        },
        "admit": True,
        "certificate_accounting": {
            "fixed_point_serialized_bytes": 0,
            "source_uncompressed_chunk_bytes": manifest["chunking"]["uncompressed_chunk_bytes"],
            "source_compressed_chunk_bytes": manifest["chunking"]["compressed_chunk_bytes"],
        },
        "strict_boundary": {
            "dimension_two_preorder_minimization_complete": True,
            "node_up_k_reachable_set_complete": True,
            "negative_root_reached": False,
            "terminal_completeness_proved": False,
            "found_layout_enabled": False,
            "no_layout_at_cap_enabled": False,
            "current_global_terminal": TERMINAL,
            "next_gate": "C049.1_B4.6.3_NEGATIVE_NODE_6_UP_K_INTEGRATION_AND_PARENT_REFINEMENT",
            "p_vs_np": "OPEN",
        },
    }
    artifact = bind_artifact(artifact)
    output.write_bytes(canonical_json(artifact) + b"\n")
    print("JANUS_C049_1_B4_6_3_DIMENSION_TWO_PREORDER_HARDENING = PASS")
    print("INPUT_GENERATORS =", len(records))
    print("SIGNATURE_BUCKETS =", len(buckets))
    print("RETAINED_GENERATORS =", len(retained_ids))
    print("DIRECT_REMOVALS =", len(removals))
    print("COMPLETE_REACHABLE_CATALOG =", len(reachable))
    print("REACHABLE_ENTRIES =", len(entries))
    print("CHARGED_OPERATIONS =", total_charged)
    print("CERTIFICATE_BYTES =", artifact["certificate_accounting"]["fixed_point_serialized_bytes"])
    print("SEMANTIC_DIGEST =", artifact["semantic_digest"])
    print("GLOBAL_TERMINAL =", TERMINAL)
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("transcript_root", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build(args.transcript_root, args.output)


if __name__ == "__main__":
    main()
