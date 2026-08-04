#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
import zlib
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Sequence

from janus_c049_1_b1_compact_trajectory_core import encode as b2_encode
from janus_c049_1_b2_up_k_core import (
    Ledger,
    decode_trajectory as b2_decode_trajectory,
    up_k_closure,
)
from janus_c049_1_b3_expand_join_shrink_core import (
    boundary_transport,
    coordinate_vector,
    decode_trajectory as b3_decode_trajectory,
    encode_trajectory as b3_encode_trajectory,
    expand_trajectory,
    join_trajectory,
    lattice_paths,
    shrink_trajectory,
    subspace_intersection,
    subspace_sum,
    width,
    xor_basis,
)
from janus_c049_1_b4_2_3k_scaffold import boundary, cases as scaffold_cases


SCHEMA = "C049.1-B4.4-NONZERO-BOUNDARY-NODE-MANIFEST-v1"
CHUNK_SCHEMA = "C049.1-B4.4-NONZERO-BOUNDARY-NODE-CHUNK-v1"
TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"
SOURCE_HEAD = "4287df8d9f5e3f18cd3ba41452cb494301c38ded"
K = 1
CAP = 10**9

PAIR_CHUNK_SIZE = 128
REFINEMENT_CHUNK_SIZE = 4096
GENERATOR_CHUNK_SIZE = 128
DELETION_CHUNK_SIZE = 2048


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def deterministic_gzip(raw: bytes) -> bytes:
    compressor = zlib.compressobj(level=9, wbits=-zlib.MAX_WBITS)
    body = compressor.compress(raw) + compressor.flush()
    header = b"\x1f\x8b\x08\x00\x00\x00\x00\x00\x02\xff"
    trailer = struct.pack("<II", zlib.crc32(raw) & 0xFFFFFFFF, len(raw) & 0xFFFFFFFF)
    return header + body + trailer


def bind_record(record: dict) -> dict:
    out = dict(record)
    out.pop("record_digest", None)
    out["record_digest"] = digest(out)
    return out


def trajectory_key(raw: Sequence[dict]) -> str:
    return canonical_json(raw).decode()


def compaction_removed(trace: Sequence[dict]) -> int:
    return sum(len(step["removed"]) for step in trace)


def refinement_work(join_receipt: dict, shrink_receipt: dict) -> dict[str, int]:
    join_trace = join_receipt["compactification_trace"]
    shrink_trace = shrink_receipt["compactification_trace"]
    return {
        "lattice_path_trials": 1,
        "join_stat_constructions": int(join_receipt["raw_length"]),
        "join_intersection_corrections": len(join_receipt["stat_receipts"]),
        "join_compaction_steps": len(join_trace),
        "join_compaction_removed_statistics": compaction_removed(join_trace),
        "shrink_projection_statistics": len(shrink_receipt["projection_receipts"]),
        "shrink_compaction_steps": len(shrink_trace),
        "shrink_compaction_removed_statistics": compaction_removed(shrink_trace),
        "width_tests": 1,
    }


def delannoy_path_count(m: int, n: int) -> int:
    table = [[0] * n for _ in range(m)]
    table[0][0] = 1
    for i in range(m):
        for j in range(n):
            if (i, j) == (0, 0):
                continue
            table[i][j] = (
                (table[i - 1][j] if i else 0)
                + (table[i][j - 1] if j else 0)
                + (table[i - 1][j - 1] if i and j else 0)
            )
    return table[-1][-1]


def selected_scaffold_case() -> dict:
    matches = [
        case
        for case in scaffold_cases()
        if int(case["d"]) == 4
        and int(case["k"]) == 1
        and case["whole_factor_blocks"] == [[1], [2], [4], [8], [3], [12]]
        and case["scaffold_order"] == [0, 4, 2, 3, 1, 5]
    ]
    if len(matches) != 1:
        raise AssertionError("B4.2 nonzero-boundary fixture not unique")
    return matches[0]


def coordinate_space_to_ambient(
    coordinate_space: Iterable[int], ambient_basis: Sequence[int], ambient_dim: int
) -> tuple[int, ...]:
    rows = []
    for mask in coordinate_space:
        value = 0
        for index, row in enumerate(ambient_basis):
            if (int(mask) >> index) & 1:
                value ^= int(row)
        rows.append(value)
    return xor_basis(rows, ambient_dim)


def ambient_space_to_coordinates(
    ambient_space: Iterable[int], ambient_basis: Sequence[int]
) -> tuple[int, ...]:
    theta = len(tuple(ambient_basis))
    masks = [coordinate_vector(int(row), ambient_basis) for row in ambient_space]
    return xor_basis(masks, theta)


def lift_trajectory(
    raw: Sequence[dict], boundary_basis: Sequence[int], ambient_dim: int
):
    lifted = [
        {
            "left": list(
                coordinate_space_to_ambient(item["left"], boundary_basis, ambient_dim)
            ),
            "right": list(
                coordinate_space_to_ambient(item["right"], boundary_basis, ambient_dim)
            ),
            "value": int(item["value"]),
        }
        for item in raw
    ]
    return b3_decode_trajectory(lifted, boundary_basis, ambient_dim)


def lower_trajectory(
    raw: Sequence[dict], boundary_basis: Sequence[int], ambient_dim: int
) -> list[dict]:
    parsed = b3_decode_trajectory(raw, boundary_basis, ambient_dim)
    return [
        {
            "left": list(ambient_space_to_coordinates(stat.left, boundary_basis)),
            "right": list(ambient_space_to_coordinates(stat.right, boundary_basis)),
            "value": int(stat.value),
        }
        for stat in parsed
    ]


def leaf_full_set(
    factor_id: int,
    factor_block: Sequence[int],
    affine_offset: int,
    boundary_basis: Sequence[int],
    ambient_dim: int,
) -> dict:
    theta = len(tuple(boundary_basis))
    if theta != 1:
        raise AssertionError("B4.4 bounded leaf fixture must have dimension one")
    full_coordinate_boundary = [1]
    generator_raw = [
        {"left": [], "right": full_coordinate_boundary, "value": 0},
        {"left": full_coordinate_boundary, "right": [], "value": 0},
    ]
    generator = b2_decode_trajectory(generator_raw, theta)
    ledger = Ledger(CAP, CAP)
    closure = up_k_closure([generator], theta, K, ledger)
    if closure["entry_count"] != 36 or closure["universe_size"] != 552:
        raise AssertionError("unexpected dimension-one leaf full set")
    lifted_generator = b3_encode_trajectory(
        lift_trajectory(generator_raw, boundary_basis, ambient_dim)
    )
    return {
        "factor_id": factor_id,
        "factor_block_rref": list(xor_basis(factor_block, ambient_dim)),
        "affine_offset": int(affine_offset),
        "boundary_rref_ambient": list(xor_basis(boundary_basis, ambient_dim)),
        "boundary_coordinate_dimension": theta,
        "boundary_coordinate_rref": full_coordinate_boundary,
        "leaf_generator_coordinates": b2_encode(generator),
        "leaf_generator_ambient": lifted_generator,
        "full_set": closure,
        "provenance": {
            "kind": "WHOLE_FACTOR_LEAF",
            "factor_id": factor_id,
            "generator_source": "canonical nonzero-boundary one-factor trajectory",
            "supplied_layout_used_for_discovery": False,
        },
    }


class ChunkWriter:
    def __init__(
        self,
        output_dir: Path,
        kind: str,
        record_id_field: str,
        chunk_size: int,
        total_records: int,
    ) -> None:
        self.output_dir = output_dir
        self.kind = kind
        self.record_id_field = record_id_field
        self.chunk_size = chunk_size
        self.total_records = total_records
        self.total_chunks = math.ceil(total_records / chunk_size) if total_records else 0
        self.buffer: list[dict] = []
        self.chunk_index = 0
        self.written_records = 0
        self.metadata: list[dict] = []

    def add(self, record: dict) -> None:
        self.buffer.append(bind_record(record))
        if len(self.buffer) == self.chunk_size:
            self._flush()

    def _flush(self) -> None:
        if not self.buffer:
            return
        index = self.chunk_index
        if index >= self.total_chunks:
            raise AssertionError("chunk count overflow")
        payload = {
            "schema": CHUNK_SCHEMA,
            "kind": self.kind,
            "chunk_index": index,
            "previous_chunk_index": index - 1 if index else None,
            "next_chunk_index": index + 1 if index + 1 < self.total_chunks else None,
            "record_id_field": self.record_id_field,
            "record_count": len(self.buffer),
            "records": self.buffer,
        }
        payload["chunk_payload_digest"] = digest(payload)
        raw = canonical_json(payload) + b"\n"
        compressed = deterministic_gzip(raw)
        filename = f"{self.kind.lower()}-{index:05d}.json.gz"
        path = self.output_dir / "chunks" / filename
        with path.open("wb") as handle:
            handle.write(compressed)
        first_id = int(self.buffer[0][self.record_id_field])
        last_id = int(self.buffer[-1][self.record_id_field])
        self.metadata.append(
            {
                "kind": self.kind,
                "chunk_index": index,
                "filename": f"chunks/{filename}",
                "record_id_field": self.record_id_field,
                "record_count": len(self.buffer),
                "first_record_id": first_id,
                "last_record_id": last_id,
                "uncompressed_bytes": len(raw),
                "compressed_bytes": len(compressed),
                "chunk_payload_digest": payload["chunk_payload_digest"],
                "compressed_sha256": sha256_bytes(compressed),
                "previous_chunk_index": payload["previous_chunk_index"],
                "next_chunk_index": payload["next_chunk_index"],
            }
        )
        self.written_records += len(self.buffer)
        self.chunk_index += 1
        self.buffer = []
        print(
            f"CHUNK {self.kind} {index + 1}/{self.total_chunks} "
            f"records={self.metadata[-1]['record_count']} "
            f"compressed={len(compressed)}",
            flush=True,
        )

    def finish(self) -> list[dict]:
        self._flush()
        if self.written_records != self.total_records:
            raise AssertionError(
                f"{self.kind} record count drift: "
                f"{self.written_records} != {self.total_records}"
            )
        if self.chunk_index != self.total_chunks:
            raise AssertionError("chunk inventory drift")
        for index, item in enumerate(self.metadata):
            item["previous_chunk_digest"] = (
                self.metadata[index - 1]["compressed_sha256"] if index else None
            )
            item["next_chunk_digest"] = (
                self.metadata[index + 1]["compressed_sha256"]
                if index + 1 < len(self.metadata)
                else None
            )
        return self.metadata


def build(output_dir: Path) -> dict:
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError("output directory must be empty")
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "chunks").mkdir()

    scaffold = selected_scaffold_case()
    ambient = int(scaffold["d"])
    blocks = [tuple(block) for block in scaffold["whole_factor_blocks"]]
    order = tuple(int(index) for index in scaffold["scaffold_order"])
    child_ids = (0, 4)
    outside_ids = tuple(order[2:])

    child_boundaries = {
        child: boundary(
            [blocks[child]],
            [blocks[index] for index in range(len(blocks)) if index != child],
            ambient,
        )
        for child in child_ids
    }
    common_boundary = xor_basis(
        (*child_boundaries[child_ids[0]], *child_boundaries[child_ids[1]]),
        ambient,
    )
    parent_boundary = boundary(
        [blocks[index] for index in child_ids],
        [blocks[index] for index in outside_ids],
        ambient,
    )
    if child_boundaries != {0: (1,), 4: (3,)}:
        raise AssertionError("child boundary fixture drift")
    if common_boundary != (2, 1) or parent_boundary != (2,):
        raise AssertionError("nonzero common/parent boundary fixture drift")

    left_transport_contract = boundary_transport(
        child_boundaries[0], common_boundary, ambient
    )
    right_transport_contract = boundary_transport(
        child_boundaries[4], common_boundary, ambient
    )
    shrink_transport_contract = boundary_transport(
        parent_boundary, common_boundary, ambient
    )
    if left_transport_contract["child_basis_in_parent_coordinates"] != [2]:
        raise AssertionError("left nontrivial transport drift")
    if right_transport_contract["child_basis_in_parent_coordinates"] != [3]:
        raise AssertionError("right nontrivial transport drift")
    if shrink_transport_contract["child_basis_in_parent_coordinates"] != [1]:
        raise AssertionError("shrink transport drift")

    expand_conditions = {}
    for child in child_ids:
        arrangement_span = xor_basis(blocks[child], ambient)
        intersection = subspace_intersection(
            arrangement_span, common_boundary, ambient
        )
        if intersection != child_boundaries[child]:
            raise AssertionError("expand side condition failed")
        expand_conditions[str(child)] = {
            "arrangement_span": list(arrangement_span),
            "intersection_with_common_boundary": list(intersection),
            "required_child_boundary": list(child_boundaries[child]),
            "satisfied": True,
        }
    left_augmented = subspace_sum(blocks[0], common_boundary, ambient)
    right_augmented = subspace_sum(blocks[4], common_boundary, ambient)
    join_intersection = subspace_intersection(
        left_augmented, right_augmented, ambient
    )
    if join_intersection != common_boundary:
        raise AssertionError("join side condition failed")

    partition_payload = {
        "whole_factor_blocks": [list(block) for block in blocks],
        "affine_offsets": list(scaffold["affine_offsets"]),
        "scaffold_order": list(order),
        "covered_factor_ids": list(child_ids),
        "outside_factor_ids": list(outside_ids),
    }
    partition_receipt_digest = digest(partition_payload)

    leaves = [
        leaf_full_set(
            child,
            blocks[child],
            scaffold["affine_offsets"][child],
            child_boundaries[child],
            ambient,
        )
        for child in child_ids
    ]
    left_entries = leaves[0]["full_set"]["entries"]
    right_entries = leaves[1]["full_set"]["entries"]
    pair_total = len(left_entries) * len(right_entries)
    refinement_total = sum(
        delannoy_path_count(
            len(left_entry["trajectory"]), len(right_entry["trajectory"])
        )
        for left_entry in left_entries
        for right_entry in right_entries
    )
    if pair_total != 1296 or refinement_total != 163824:
        raise AssertionError("full child-product volume drift")

    pair_writer = ChunkWriter(
        output_dir, "PAIRS", "pair_id", PAIR_CHUNK_SIZE, pair_total
    )
    refinement_writer = ChunkWriter(
        output_dir,
        "REFINEMENTS",
        "attempt_id",
        REFINEMENT_CHUNK_SIZE,
        refinement_total,
    )

    cumulative_work = 0

    def charge(breakdown: dict[str, int]) -> int:
        nonlocal cumulative_work
        if any(int(value) < 0 for value in breakdown.values()):
            raise ValueError("negative work charge")
        cumulative_work += sum(int(value) for value in breakdown.values())
        return cumulative_work

    child_work_events = []
    for leaf in leaves:
        ledger = leaf["full_set"]["ledger"]
        breakdown = {
            "b2_discovery_work": int(ledger["discovery_work"]),
            "b2_work": int(ledger["work"]),
        }
        child_work_events.append(
            {
                "factor_id": leaf["factor_id"],
                "breakdown": breakdown,
                "work_delta": sum(breakdown.values()),
                "cumulative_work": charge(breakdown),
            }
        )

    successful_by_trajectory: dict[str, list[int]] = defaultdict(list)
    attempt_id = 0
    pair_id = 0
    successful = 0
    failed = 0
    raw_precompact_statistics = 0

    stage_partition_receipt = {
        "partition_receipt_digest": partition_receipt_digest,
        "left_expand_factor_ids": [0],
        "right_expand_factor_ids": [4],
        "join_factor_ids": [0, 4],
        "shrink_factor_ids": [0, 4],
        "outside_factor_ids": list(outside_ids),
    }

    for left_index, left_entry in enumerate(left_entries):
        left_coordinates = left_entry["trajectory"]
        left = lift_trajectory(
            left_coordinates, child_boundaries[child_ids[0]], ambient
        )
        for right_index, right_entry in enumerate(right_entries):
            right_coordinates = right_entry["trajectory"]
            right = lift_trajectory(
                right_coordinates, child_boundaries[child_ids[1]], ambient
            )
            expanded_left, left_transport = expand_trajectory(
                left, child_boundaries[child_ids[0]], common_boundary, ambient
            )
            expanded_right, right_transport = expand_trajectory(
                right, child_boundaries[child_ids[1]], common_boundary, ambient
            )
            expand_breakdown = {
                "pair_enumerations": 1,
                "expanded_statistics": len(expanded_left) + len(expanded_right),
                "boundary_coordinate_changes": len(
                    left_transport["child_basis_in_parent_coordinates"]
                )
                + len(right_transport["child_basis_in_parent_coordinates"]),
            }
            cumulative_after_expand = charge(expand_breakdown)
            first_attempt_id = attempt_id
            pair_paths = 0

            for path in lattice_paths(len(expanded_left), len(expanded_right)):
                joined, join_receipt = join_trajectory(
                    expanded_left, expanded_right, path, common_boundary, ambient
                )
                shrunk, shrink_receipt = shrink_trajectory(
                    joined, parent_boundary, ambient
                )
                output_ambient = b3_encode_trajectory(shrunk)
                output_coordinates = lower_trajectory(
                    output_ambient, parent_boundary, ambient
                )
                output_width = width(shrunk)
                accepted = output_width <= K
                breakdown = refinement_work(join_receipt, shrink_receipt)
                cumulative_after_attempt = charge(breakdown)
                record = {
                    "record_kind": "REFINEMENT",
                    "attempt_id": attempt_id,
                    "pair_id": pair_id,
                    "left_entry_index": left_index,
                    "right_entry_index": right_index,
                    "lattice_path": [list(cell) for cell in path],
                    "join": join_receipt,
                    "shrink": shrink_receipt,
                    "output_ambient": output_ambient,
                    "output_parent_coordinates": output_coordinates,
                    "output_width": output_width,
                    "status": "SUCCESS" if accepted else "FAILED_WIDTH_CAP",
                    "failure_reason": None
                    if accepted
                    else f"output width {output_width} exceeds k={K}",
                    "partition_receipt_digest": partition_receipt_digest,
                    "work_breakdown": dict(sorted(breakdown.items())),
                    "cumulative_work": cumulative_after_attempt,
                }
                refinement_writer.add(record)
                raw_precompact_statistics += int(join_receipt["raw_length"])
                if accepted:
                    successful += 1
                    successful_by_trajectory[
                        trajectory_key(output_coordinates)
                    ].append(attempt_id)
                else:
                    failed += 1
                attempt_id += 1
                pair_paths += 1

            pair_writer.add(
                {
                    "record_kind": "PAIR",
                    "pair_id": pair_id,
                    "left_entry_index": left_index,
                    "right_entry_index": right_index,
                    "left_input_coordinates": left_coordinates,
                    "right_input_coordinates": right_coordinates,
                    "left_input_ambient": b3_encode_trajectory(left),
                    "right_input_ambient": b3_encode_trajectory(right),
                    "left_expand": {
                        "output_ambient": b3_encode_trajectory(expanded_left),
                        "transport": left_transport,
                    },
                    "right_expand": {
                        "output_ambient": b3_encode_trajectory(expanded_right),
                        "transport": right_transport,
                    },
                    "grouped_partition_stages": stage_partition_receipt,
                    "lattice_path_count": pair_paths,
                    "first_attempt_id": first_attempt_id,
                    "last_attempt_id": attempt_id - 1,
                    "expand_work_breakdown": dict(sorted(expand_breakdown.items())),
                    "cumulative_work_after_expand": cumulative_after_expand,
                }
            )
            pair_id += 1

    if attempt_id != refinement_total or pair_id != pair_total:
        raise AssertionError("full child-product traversal incomplete")
    if successful != 12073 or failed != 151751:
        raise AssertionError("success/failure profile drift")
    if raw_precompact_statistics != 1297408:
        raise AssertionError("raw precompact work drift")

    pair_chunks = pair_writer.finish()
    refinement_chunks = refinement_writer.finish()

    generator_records = []
    deletion_records = []
    for generator_index, key in enumerate(sorted(successful_by_trajectory)):
        trajectory_coordinates = json.loads(key)
        provenance_ids = successful_by_trajectory[key]
        canonical_attempt = provenance_ids[0]
        ambient_trajectory = b3_encode_trajectory(
            lift_trajectory(trajectory_coordinates, parent_boundary, ambient)
        )
        generator_records.append(
            {
                "record_kind": "SUCCESSFUL_GENERATOR",
                "generator_index": generator_index,
                "trajectory_parent_coordinates": trajectory_coordinates,
                "trajectory_ambient": ambient_trajectory,
                "trajectory_digest": digest(trajectory_coordinates),
                "provenance_attempt_ids": provenance_ids,
                "canonical_retained_attempt_id": canonical_attempt,
            }
        )
        identity_path = [
            [index, index] for index in range(len(trajectory_coordinates))
        ]
        for removed_attempt in provenance_ids[1:]:
            deletion_records.append(
                {
                    "record_kind": "DUPLICATE_DELETION",
                    "deletion_id": len(deletion_records),
                    "generator_index": generator_index,
                    "trajectory_digest": digest(trajectory_coordinates),
                    "removed_attempt_id": removed_attempt,
                    "retained_attempt_id": canonical_attempt,
                    "witness": {
                        "path": identity_path,
                        "path_length": len(identity_path),
                    },
                    "reason": "IDENTICAL_REFINEMENT_OUTPUT",
                }
            )
    if len(generator_records) != 252 or len(deletion_records) != 11821:
        raise AssertionError("generator/deletion profile drift")

    generator_writer = ChunkWriter(
        output_dir,
        "GENERATORS",
        "generator_index",
        GENERATOR_CHUNK_SIZE,
        len(generator_records),
    )
    for record in generator_records:
        generator_writer.add(record)
    generator_chunks = generator_writer.finish()

    deletion_writer = ChunkWriter(
        output_dir,
        "DELETIONS",
        "deletion_id",
        DELETION_CHUNK_SIZE,
        len(deletion_records),
    )
    for record in deletion_records:
        deletion_writer.add(record)
    deletion_chunks = deletion_writer.finish()

    b2_generators = [
        b2_decode_trajectory(record["trajectory_parent_coordinates"], len(parent_boundary))
        for record in generator_records
    ]
    b2_ledger = Ledger(CAP, CAP)
    node_closure = up_k_closure(
        b2_generators, len(parent_boundary), K, b2_ledger
    )
    cumulative_before_node_b2 = cumulative_work
    node_b2_breakdown = {
        "b2_discovery_work": int(node_closure["ledger"]["discovery_work"]),
        "b2_work": int(node_closure["ledger"]["work"]),
    }
    charge(node_b2_breakdown)

    generator_index_by_key = {
        trajectory_key(record["trajectory_parent_coordinates"]): record[
            "generator_index"
        ]
        for record in generator_records
    }
    input_generator_provenance = [
        {
            "input_generator_index": index,
            "generator_record_index": generator_index_by_key[trajectory_key(raw)],
        }
        for index, raw in enumerate(node_closure["input_generators"])
    ]
    retained_generator_provenance = [
        {
            "retained_generator_index": index,
            "generator_record_index": generator_index_by_key[trajectory_key(raw)],
        }
        for index, raw in enumerate(node_closure["retained_generators"])
    ]
    entry_provenance = [
        {
            "entry_index": index,
            "source_generator_index": int(entry["source_generator_index"]),
            "generator_record_index": retained_generator_provenance[
                int(entry["source_generator_index"])
            ]["generator_record_index"],
        }
        for index, entry in enumerate(node_closure["entries"])
    ]

    chunk_groups = {
        "PAIRS": pair_chunks,
        "REFINEMENTS": refinement_chunks,
        "GENERATORS": generator_chunks,
        "DELETIONS": deletion_chunks,
    }
    transcript_root_digest = digest(chunk_groups)
    all_chunks = [item for group in chunk_groups.values() for item in group]
    manifest = {
        "schema": SCHEMA,
        "phase": "B4.4_NONZERO_BOUNDARY_INTERNAL_NODE_FULL_SET",
        "source_head": SOURCE_HEAD,
        "scaffold_case": scaffold,
        "node": {
            "node_id": 6,
            "kind": "SPINE_INTERNAL_JOIN",
            "covered_factor_ids": list(child_ids),
            "outside_factor_ids": list(outside_ids),
            "whole_factor_blocks": [list(block) for block in blocks],
            "affine_offsets": list(scaffold["affine_offsets"]),
            "covered_affine_offsets": [
                scaffold["affine_offsets"][index] for index in child_ids
            ],
            "grouped_partition_preserved": True,
            "partition_receipt": partition_payload,
            "partition_receipt_digest": partition_receipt_digest,
            "child_boundaries": {
                str(key): list(value) for key, value in child_boundaries.items()
            },
            "common_join_boundary": list(common_boundary),
            "parent_boundary": list(parent_boundary),
            "boundary_dimensions": {
                "children": [len(child_boundaries[index]) for index in child_ids],
                "common": len(common_boundary),
                "parent": len(parent_boundary),
            },
            "transport_contracts": {
                "left_child_to_common": left_transport_contract,
                "right_child_to_common": right_transport_contract,
                "parent_in_common_for_shrink": shrink_transport_contract,
            },
            "side_conditions": {
                "expand": expand_conditions,
                "join": {
                    "left_augmented_span": list(left_augmented),
                    "right_augmented_span": list(right_augmented),
                    "intersection": list(join_intersection),
                    "required_common_boundary": list(common_boundary),
                    "satisfied": True,
                },
                "shrink": {
                    "parent_contained_in_common": True,
                    "parent_basis_in_common_coordinates": shrink_transport_contract[
                        "child_basis_in_parent_coordinates"
                    ],
                },
            },
            "width_cap": K,
        },
        "child_full_sets": leaves,
        "chunking": {
            "compression": "DETERMINISTIC_GZIP_DEFLATE9_MTIME0_OS255",
            "pair_records_per_chunk": PAIR_CHUNK_SIZE,
            "refinement_records_per_chunk": REFINEMENT_CHUNK_SIZE,
            "generator_records_per_chunk": GENERATOR_CHUNK_SIZE,
            "deletion_records_per_chunk": DELETION_CHUNK_SIZE,
            "tail_chunk_may_be_short": True,
            "chunk_groups": chunk_groups,
            "transcript_root_digest": transcript_root_digest,
            "chunk_count": len(all_chunks),
            "uncompressed_chunk_bytes": sum(
                item["uncompressed_bytes"] for item in all_chunks
            ),
            "compressed_chunk_bytes": sum(
                item["compressed_bytes"] for item in all_chunks
            ),
        },
        "node_up_k": node_closure,
        "input_generator_provenance": input_generator_provenance,
        "retained_generator_provenance": retained_generator_provenance,
        "entry_provenance": entry_provenance,
        "work_ledger": {
            "child_full_set_events": child_work_events,
            "cumulative_work_before_node_b2": cumulative_before_node_b2,
            "node_b2_breakdown": node_b2_breakdown,
            "node_b2_work_delta": sum(node_b2_breakdown.values()),
            "cumulative_work_final": cumulative_work,
            "monotone_by_construction": True,
        },
        "audit": {
            "child_full_set_entries": [
                leaf["full_set"]["entry_count"] for leaf in leaves
            ],
            "child_pairs_processed": pair_total,
            "lattice_paths_processed": refinement_total,
            "successful_refinements": successful,
            "failed_refinements": failed,
            "raw_precompact_join_statistics": raw_precompact_statistics,
            "unique_successful_generators": len(generator_records),
            "duplicate_successful_outputs_deleted": len(deletion_records),
            "b2_dominance_deletions": len(node_closure["removals"]),
            "retained_generators": len(node_closure["retained_generators"]),
            "final_up_k_entries": int(node_closure["entry_count"]),
            "cumulative_work": cumulative_work,
            "chunk_count": len(all_chunks),
            "failures": 0,
        },
        "strict_boundary": {
            "scope": "one nonzero-boundary internal scaffold node only",
            "full_iterative_compression_cycle": False,
            "all_scaffold_nodes_processed": False,
            "root_full_set_computed": False,
            "complete_branch_refinement": False,
            "no_layout_at_cap_enabled": False,
            "empty_full_set_terminal": TERMINAL,
            "current_global_terminal": TERMINAL,
            "next_gate": "C049.1_B4.5_UNIVERSAL_BOTTOM_UP_SCAFFOLD_EXECUTOR",
            "p_vs_np": "OPEN",
        },
    }
    manifest["manifest_digest"] = digest(manifest)
    raw_manifest = canonical_json(manifest) + b"\n"
    with (output_dir / "manifest.json").open("wb") as handle:
        handle.write(raw_manifest)
    print("JANUS_C049_1_B4_4_NONZERO_BOUNDARY_NODE_FULL_SET = PASS")
    print("CHILD_PAIRS =", pair_total)
    print("LATTICE_PATHS =", refinement_total)
    print("SUCCESSFUL_REFINEMENTS =", successful)
    print("FAILED_REFINEMENTS =", failed)
    print("UNIQUE_GENERATORS =", len(generator_records))
    print("FINAL_UP_K_ENTRIES =", node_closure["entry_count"])
    print("CUMULATIVE_WORK =", cumulative_work)
    print("CHUNKS =", len(all_chunks))
    print("MANIFEST_BYTES =", len(raw_manifest))
    print("MANIFEST_DIGEST =", manifest["manifest_digest"])
    print("TRANSCRIPT_ROOT_DIGEST =", transcript_root_digest)
    print("TERMINAL =", TERMINAL)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    build(Path(args.output_dir))


if __name__ == "__main__":
    main()
