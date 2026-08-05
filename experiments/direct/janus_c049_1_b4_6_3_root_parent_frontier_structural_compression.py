#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from collections import Counter
from pathlib import Path
from typing import Any, Sequence

SCHEMA = "C049.1-B4.6.3-ROOT-PARENT-FRONTIER-STRUCTURAL-COMPRESSION-v1"
TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"

EXPECTED_FRONTIER_SHA256 = "6eefd8e31ba4808e5587475c2faa2c000fd0093da4de2c488db42d103c059890"
EXPECTED_FRONTIER_SEMANTIC = "62e9178821fe56cbf094e8512dd20b687796c6fd87e08c0fea8ea833ef6c5e80"
EXPECTED_UP_K_SHA256 = "c6e369099ea2fdf6572409dab7ce6f5172d40543388b366ec37a821262c506e4"
EXPECTED_UP_K_SEMANTIC = "f90aa04716ca2fa9019449e19b5866ac443cf545253bb41ae212dd3c68212713"
EXPECTED_MANIFEST_SHA256 = "563bc6d4148dfb94e7c5aa3c9b8e6ffa28e0b0e9cc6603fe0bffe39e71a636a9"
EXPECTED_MANIFEST_DIGEST = "cb124decfa45c2adfd58fe7bf86c9e8a7cd45afff84dde4ff90d4090721c74fd"
EXPECTED_TRANSCRIPT_ROOT = "eb904e833b53cf5626af1eb28493f479f5f54f2066a8b5427cb7e3eb47f515d8"
EXPECTED_NODE9_RECEIPT = "1a23cdd127a35932d8515c742034e67443ebf4c2a42ac06458f809d63d65ca5a"
EXPECTED_LEAF5_RECEIPT = "1e81398ee7d05a6312ea94154a7026df64e9bf739d3957180e2f11d723c9c528"
EXPECTED_LEFT_ENTRIES = 252
EXPECTED_RIGHT_ENTRIES = 36
EXPECTED_CHILD_PAIRS = 9072
EXPECTED_REFINEMENTS = 4_954_128
EXPECTED_RAW_STREAMS = 194_247
EXPECTED_COMPACT_CLASSES = 77
EXPECTED_SUCCESSFUL_REFINEMENTS = 7_825
EXPECTED_FAILED_REFINEMENTS = 4_946_303
EXPECTED_SUCCESSFUL_CLASSES = 6
EXPECTED_FAILED_CLASSES = 71
EXPECTED_WIDTH_HISTOGRAM = {0: 1, 1: 7_824, 2: 1_440_803, 3: 3_505_500}
EXPECTED_SUCCESS_MULTIPLICITIES = {
    (0,): 1,
    (0, 1): 1_898,
    (0, 1, 0): 1_351,
    (1,): 221,
    (1, 0): 1_898,
    (1, 0, 1): 2_456,
}


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def delannoy(m: int, n: int) -> int:
    return sum(math.comb(m, k) * math.comb(n, k) * (2**k) for k in range(min(m, n) + 1))


def compact_scalar(values: Sequence[int]) -> tuple[int, ...]:
    seq = [int(value) for value in values]
    if not seq or any(value < 0 for value in seq):
        raise AssertionError("invalid scalar trajectory")
    while True:
        changed = False
        for index in range(1, len(seq)):
            if seq[index - 1] == seq[index]:
                del seq[index]
                changed = True
                break
        if changed:
            continue
        for start in range(len(seq)):
            for end in range(start + 2, len(seq)):
                window = seq[start : end + 1]
                increasing = window[0] <= window[-1] and all(window[0] <= x <= window[-1] for x in window[1:-1])
                decreasing = window[0] >= window[-1] and all(window[0] >= x >= window[-1] for x in window[1:-1])
                if increasing or decreasing:
                    del seq[start + 1 : end]
                    changed = True
                    break
            if changed:
                break
        if not changed:
            return tuple(seq)


def decode_trajectory(raw: Sequence[dict[str, Any]]) -> tuple[tuple[bool, bool, int], ...]:
    out = []
    for item in raw:
        left = tuple(int(x) for x in item["left"])
        right = tuple(int(x) for x in item["right"])
        if left not in ((), (1,)) or right not in ((), (1,)):
            raise AssertionError("root child trajectory outside one-dimensional boundary")
        value = int(item["value"])
        if value not in (0, 1):
            raise AssertionError("root child trajectory outside width-one catalog")
        out.append((bool(left), bool(right), value))
    if not out:
        raise AssertionError("empty child trajectory")
    return tuple(out)


def cell_matrix(left: Sequence[tuple[bool, bool, int]], right: Sequence[tuple[bool, bool, int]]) -> tuple[tuple[int, ...], ...]:
    initial_intersection = int(left[0][1] and right[0][1])
    rows = []
    for left_l, left_r, left_value in left:
        row = []
        for right_l, right_r, right_value in right:
            current_intersection = int((left_l or left_r) and (right_l or right_r))
            join_correction = initial_intersection - current_intersection
            if join_correction < 0:
                raise AssertionError("negative root join correction")
            joined_left = left_l or right_l
            joined_right = left_r or right_r
            shrink_correction = int(joined_left and joined_right)
            row.append(left_value + right_value + join_correction + shrink_correction)
        rows.append(tuple(row))
    return tuple(rows)


def raw_stream_distribution(matrix: Sequence[Sequence[int]], work: Counter[str]) -> Counter[tuple[int, ...]]:
    rows, columns = len(matrix), len(matrix[0])
    table: list[list[Counter[tuple[int, ...]]]] = [[Counter() for _ in range(columns)] for _ in range(rows)]
    for i in range(rows):
        for j in range(columns):
            current: Counter[tuple[int, ...]] = Counter()
            value = int(matrix[i][j])
            if i == 0 and j == 0:
                current[(value,)] = 1
            else:
                for parent_i, parent_j in ((i - 1, j), (i, j - 1), (i - 1, j - 1)):
                    if parent_i < 0 or parent_j < 0:
                        continue
                    parent = table[parent_i][parent_j]
                    work["prefix_transition_source_states"] += len(parent)
                    for stream, multiplicity in parent.items():
                        current[stream + (value,)] += multiplicity
                        work["prefix_transition_additions"] += 1
            table[i][j] = current
            work["lattice_dp_cells"] += 1
            work["distinct_prefix_states_materialized"] += len(current)
    return table[-1][-1]


def normalize_sources(frontier_path: Path, up_k_path: Path, manifest_path: Path, order: str) -> tuple[dict, dict, dict, list, list]:
    if file_sha256(frontier_path) != EXPECTED_FRONTIER_SHA256:
        raise AssertionError("node9 frontier bytes")
    frontier = load(frontier_path)
    if frontier.get("semantic_digest") != EXPECTED_FRONTIER_SEMANTIC or digest(frontier["proof_payload"]) != EXPECTED_FRONTIER_SEMANTIC:
        raise AssertionError("node9 frontier semantics")

    if file_sha256(up_k_path) != EXPECTED_UP_K_SHA256:
        raise AssertionError("node9 up_k bytes")
    up_k = load(up_k_path)
    if up_k.get("semantic_digest") != EXPECTED_UP_K_SEMANTIC or digest(up_k["proof_payload"]) != EXPECTED_UP_K_SEMANTIC:
        raise AssertionError("node9 up_k semantics")

    if file_sha256(manifest_path) != EXPECTED_MANIFEST_SHA256:
        raise AssertionError("integration manifest bytes")
    manifest = load(manifest_path)
    if manifest.get("manifest_digest") != EXPECTED_MANIFEST_DIGEST:
        raise AssertionError("integration manifest semantics")
    if manifest["chunking"]["transcript_root_digest"] != EXPECTED_TRANSCRIPT_ROOT:
        raise AssertionError("transcript root")
    if manifest["execution"]["processed_internal_node_ids"] != [6, 7, 8, 9]:
        raise AssertionError("processed internal nodes")
    if manifest["execution"]["root_node_id"] != 10 or manifest["execution"]["root_full_set_receipt"] is not None:
        raise AssertionError("root preflight state")
    stop = manifest["execution"]["stop"]
    if (stop["node_id"], stop["reason"], stop["required"], stop["cap"], stop["no_layout_at_cap"]) != (
        10,
        "REFINEMENT_CAP_EXCEEDED",
        EXPECTED_REFINEMENTS,
        2_000_000,
        False,
    ):
        raise AssertionError("root preflight stop")

    node9 = next(item for item in manifest["node_results"] if int(item["node_id"]) == 9)
    leaf5 = next(item for item in manifest["leaf_full_sets"] if int(item["node_id"]) == 5)
    if node9["output_receipt"]["receipt_digest"] != EXPECTED_NODE9_RECEIPT:
        raise AssertionError("node9 receipt")
    if leaf5["output_receipt"]["receipt_digest"] != EXPECTED_LEAF5_RECEIPT:
        raise AssertionError("leaf5 receipt")
    if tuple(node9["parent_boundary"]) != (1,) or tuple(leaf5["boundary_rref_ambient"]) != (1,):
        raise AssertionError("root child boundaries")

    left_entries = list(node9["node_up_k"]["entries"])
    right_entries = list(leaf5["full_set"]["entries"])
    if (len(left_entries), len(right_entries)) != (EXPECTED_LEFT_ENTRIES, EXPECTED_RIGHT_ENTRIES):
        raise AssertionError("root child entry counts")
    if order == "reversed":
        left_entries.reverse()
        right_entries.reverse()
    elif order == "seeded-shuffle":
        rng = random.Random(0xC049110)
        rng.shuffle(left_entries)
        rng.shuffle(right_entries)
    elif order != "original":
        raise AssertionError("entry order")
    return frontier, up_k, manifest, left_entries, right_entries


def lower_envelope_attack(up_k: dict, manifest: dict) -> dict[str, Any]:
    retained = up_k["proof_payload"]["minimization"]["retained_generators"]
    leaf5 = next(item for item in manifest["leaf_full_sets"] if int(item["node_id"]) == 5)
    right = decode_trajectory(leaf5["leaf_generator_coordinates"])
    outputs: Counter[tuple[int, ...]] = Counter()
    path_count = 0
    for item in retained:
        left = decode_trajectory(item["trajectory"])
        matrix = cell_matrix(left, right)
        distribution = raw_stream_distribution(matrix, Counter())
        path_count += sum(distribution.values())
        for stream, multiplicity in distribution.items():
            outputs[compact_scalar(stream)] += multiplicity
    if path_count != 8 or outputs != Counter({(0, 1, 0): 7, (0,): 1}):
        raise AssertionError("lower-envelope attack drift")
    return {
        "retained_left_generators": 2,
        "right_zero_envelope_generators": 1,
        "quotient_paths": path_count,
        "all_lower_envelope_paths_width_at_most_k": True,
        "lower_envelope_outputs": [
            {"compact_scalar_sequence": list(sequence), "path_multiplicity": outputs[sequence]}
            for sequence in sorted(outputs)
        ],
        "reflection_to_complete_child_languages": False,
        "counterevidence": {
            "complete_failed_refinement_count": EXPECTED_FAILED_REFINEMENTS,
            "complete_successful_compact_sequences_missing_from_lower_envelopes": [
                [0, 1], [1], [1, 0], [1, 0, 1]
            ],
        },
        "forbidden_shortcut": "LOWER_ENVELOPE_SUCCESS_CANNOT_CLASSIFY_AN_ENTIRE_ROOT_QUOTIENT_PATH",
    }


def build(frontier_path: Path, up_k_path: Path, manifest_path: Path, order: str) -> dict[str, Any]:
    _, up_k, manifest, left_entries, right_entries = normalize_sources(frontier_path, up_k_path, manifest_path, order)
    left = [decode_trajectory(item["trajectory"]) for item in left_entries]
    right = [decode_trajectory(item["trajectory"]) for item in right_entries]

    work: Counter[str] = Counter()
    raw_global: Counter[tuple[int, ...]] = Counter()
    pair_terminal_stream_counts: Counter[int] = Counter()
    exact_refinements = 0
    for left_trajectory in left:
        for right_trajectory in right:
            work["child_pairs_processed"] += 1
            matrix = cell_matrix(left_trajectory, right_trajectory)
            work["root_scalar_matrix_cells"] += len(matrix) * len(matrix[0])
            distribution = raw_stream_distribution(matrix, work)
            pair_total = sum(distribution.values())
            expected_pair_total = delannoy(len(left_trajectory) - 1, len(right_trajectory) - 1)
            if pair_total != expected_pair_total:
                raise AssertionError("pair Delannoy multiplicity")
            exact_refinements += pair_total
            pair_terminal_stream_counts[len(distribution)] += 1
            raw_global.update(distribution)
            work["distinct_terminal_raw_streams_per_pair"] += len(distribution)

    if work["child_pairs_processed"] != EXPECTED_CHILD_PAIRS or exact_refinements != EXPECTED_REFINEMENTS:
        raise AssertionError("root exact frontier")
    if len(raw_global) != EXPECTED_RAW_STREAMS or sum(raw_global.values()) != EXPECTED_REFINEMENTS:
        raise AssertionError("root raw stream compression")

    compact_counts: Counter[tuple[int, ...]] = Counter()
    for stream, multiplicity in raw_global.items():
        compact_counts[compact_scalar(stream)] += multiplicity
        work["distinct_raw_streams_compactified"] += 1
    if len(compact_counts) != EXPECTED_COMPACT_CLASSES or sum(compact_counts.values()) != EXPECTED_REFINEMENTS:
        raise AssertionError("root compact partition")

    width_histogram: Counter[int] = Counter()
    successful = []
    failed = []
    successful_refinements = 0
    failed_refinements = 0
    for sequence in sorted(compact_counts):
        multiplicity = compact_counts[sequence]
        width = max(sequence)
        width_histogram[width] += multiplicity
        record = {
            "compact_scalar_sequence": list(sequence),
            "sequence_digest": digest(list(sequence)),
            "width": width,
            "refinement_multiplicity": multiplicity,
        }
        if width <= 1:
            successful.append(record)
            successful_refinements += multiplicity
        else:
            overflow_index = next(index for index, value in enumerate(sequence) if value > 1)
            record.update({
                "failure_kind": "UNIVERSAL_COMPACT_ROOT_WIDTH_CAP",
                "first_overflow_index": overflow_index,
                "first_overflow_value": sequence[overflow_index],
            })
            failed.append(record)
            failed_refinements += multiplicity

    if dict(width_histogram) != EXPECTED_WIDTH_HISTOGRAM:
        raise AssertionError("root width histogram")
    if (successful_refinements, failed_refinements, len(successful), len(failed)) != (
        EXPECTED_SUCCESSFUL_REFINEMENTS,
        EXPECTED_FAILED_REFINEMENTS,
        EXPECTED_SUCCESSFUL_CLASSES,
        EXPECTED_FAILED_CLASSES,
    ):
        raise AssertionError("root success/failure partition")
    if {tuple(item["compact_scalar_sequence"]): item["refinement_multiplicity"] for item in successful} != EXPECTED_SUCCESS_MULTIPLICITIES:
        raise AssertionError("root successful generator family")

    attack = lower_envelope_attack(up_k, manifest)
    invariant_vector = {f"R10-INV-{index:02d}": "PASS" for index in range(1, 13)}
    proof_payload: dict[str, Any] = {
        "source": {
            "node9_frontier_artifact_sha256": EXPECTED_FRONTIER_SHA256,
            "node9_frontier_semantic_digest": EXPECTED_FRONTIER_SEMANTIC,
            "node9_up_k_artifact_sha256": EXPECTED_UP_K_SHA256,
            "node9_up_k_semantic_digest": EXPECTED_UP_K_SEMANTIC,
            "integration_manifest_file_sha256": EXPECTED_MANIFEST_SHA256,
            "integration_manifest_digest": EXPECTED_MANIFEST_DIGEST,
            "transcript_root_digest": EXPECTED_TRANSCRIPT_ROOT,
            "node9_output_receipt_digest": EXPECTED_NODE9_RECEIPT,
            "leaf5_output_receipt_digest": EXPECTED_LEAF5_RECEIPT,
        },
        "node_id": 10,
        "ambient_dim": int(manifest["scaffold_case"]["d"]),
        "k": int(manifest["scaffold_case"]["k"]),
        "geometry": {
            "left_child_node_id": 9,
            "right_child_node_id": 5,
            "left_boundary": [1],
            "right_boundary": [1],
            "common_boundary": [1],
            "parent_boundary": [],
            "left_expand_identity": True,
            "right_expand_identity": True,
            "shrink_identity": False,
        },
        "child_languages": {
            "left_entry_count": len(left_entries),
            "right_entry_count": len(right_entries),
            "child_pair_count": EXPECTED_CHILD_PAIRS,
            "left_length_histogram": {str(k): v for k, v in sorted(Counter(map(len, left)).items())},
            "right_length_histogram": {str(k): v for k, v in sorted(Counter(map(len, right)).items())},
            "child_cartesian_pair_records_materialized": 0,
        },
        "structural_refinement_dp": {
            "method": "PAIRWISE_SCALAR_CELL_MATRIX_DISTINCT_PREFIX_STREAM_DYNAMIC_PROGRAM",
            "fine_lattice_paths_enumerated": 0,
            "fine_refinement_records_materialized": 0,
            "exact_refinement_multiplicity": exact_refinements,
            "global_distinct_raw_scalar_streams": len(raw_global),
            "global_compact_scalar_classes": len(compact_counts),
            "pair_terminal_distinct_stream_histogram": {str(k): v for k, v in sorted(pair_terminal_stream_counts.items())},
            "multiplicity_conservation": sum(raw_global.values()) == exact_refinements == sum(compact_counts.values()),
        },
        "lower_envelope_reflection_attack": attack,
        "root_frontier": {
            "successful_refinement_count": successful_refinements,
            "failed_refinement_count": failed_refinements,
            "successful_compact_generator_count": len(successful),
            "failed_compact_class_count": len(failed),
            "width_multiplicity_histogram": {str(k): v for k, v in sorted(width_histogram.items())},
            "successful_generators": successful,
            "failed_compact_partition": failed,
            "failed_refinement_partition_complete": True,
            "successful_refinement_partition_complete": True,
            "generator_frontier_complete": True,
        },
        "work_ledger": {key: int(work[key]) for key in sorted(work)},
        "invariant_vector": invariant_vector,
        "admit_root_parent_frontier_structural_compression": True,
        "strict_boundary": {
            "root_parent_generator_frontier_complete": True,
            "root_parent_refinement_complete": True,
            "root_parent_up_k_complete": False,
            "root_full_set_computed": False,
            "root_empty_proved": False,
            "terminal_completeness_proved": False,
            "found_layout": "FORBIDDEN",
            "no_layout_at_cap": "FORBIDDEN",
            "current_global_terminal": TERMINAL,
            "next_gate": "C049.1_B4.6.3_ROOT_SIX_GENERATOR_UP_K_CLOSURE",
            "p_vs_np": "OPEN",
        },
        "certificate_bytes": 0,
    }
    while True:
        outer = {
            "schema": SCHEMA,
            "semantic_digest_scope": "proof_payload",
            "proof_payload": proof_payload,
            "semantic_digest": digest(proof_payload),
        }
        raw = canonical_json(outer) + b"\n"
        if proof_payload["certificate_bytes"] == len(raw):
            return outer
        proof_payload["certificate_bytes"] = len(raw)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("frontier", type=Path)
    parser.add_argument("up_k", type=Path)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--entry-order", choices=("original", "reversed", "seeded-shuffle"), default="original")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    artifact = build(args.frontier, args.up_k, args.manifest, args.entry_order)
    args.output.write_bytes(canonical_json(artifact) + b"\n")
    proof = artifact["proof_payload"]
    summary = proof["root_frontier"]
    print(json.dumps({
        "artifact_bytes": args.output.stat().st_size,
        "artifact_sha256": file_sha256(args.output),
        "semantic_digest": artifact["semantic_digest"],
        "refinements": proof["structural_refinement_dp"]["exact_refinement_multiplicity"],
        "successful": summary["successful_refinement_count"],
        "failed": summary["failed_refinement_count"],
        "generators": summary["successful_compact_generator_count"],
        "lower_envelope_reflection": proof["lower_envelope_reflection_attack"]["reflection_to_complete_child_languages"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
