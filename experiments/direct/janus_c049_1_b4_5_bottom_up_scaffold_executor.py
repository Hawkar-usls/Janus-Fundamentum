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
from janus_c049_1_b4_2_3k_scaffold import boundary, scaffold
import janus_c049_1_b4_4_nonzero_boundary_node_full_set as b44


SCHEMA = "C049.1-B4.5-BOTTOM-UP-SCAFFOLD-EXECUTOR-MANIFEST-v1"
CHUNK_SCHEMA = "C049.1-B4.5-BOTTOM-UP-SCAFFOLD-EXECUTOR-CHUNK-v1"
TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"
SOURCE_HEAD = "6483e54aa5326ad7c34209bc45cad08affd8d967"

PAIR_CHUNK_SIZE = 128
REFINEMENT_CHUNK_SIZE = 4096
GENERATOR_CHUNK_SIZE = 128
DELETION_CHUNK_SIZE = 2048
CAP = 10**9

DEFAULT_CAPABILITY = {
    "max_internal_nodes": 16,
    "max_child_pairs_per_node": 2_000,
    "max_refinements_per_node": 250_000,
    "max_boundary_coordinate_dimension": 3,
}


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


def selected_scaffold() -> dict:
    record = scaffold(
        [(1,), (1,), (2,), (4,)],
        (0, 1, 2),
        3,
        3,
        1,
        [0, 1, 0, 1],
    )
    if record["terminal"] != "SCAFFOLD_3K_CERTIFIED":
        raise AssertionError("selected B4.2 scaffold is not certified")
    if record["scaffold_order"] != [0, 1, 2, 3]:
        raise AssertionError("selected scaffold order drift")
    if [edge["width"] for edge in record["candidate_edges"]] != [1, 0, 0]:
        raise AssertionError("selected scaffold width profile drift")
    return record


def span_for_ids(
    blocks: Sequence[Sequence[int]], factor_ids: Sequence[int], ambient: int
) -> tuple[int, ...]:
    return xor_basis(
        (row for factor_id in factor_ids for row in blocks[factor_id]), ambient
    )


def derive_topology(scaffold_record: dict) -> dict:
    if scaffold_record["scaffold_type"] != "CATERPILLAR_APPEND_NEW_LEAF":
        raise ValueError("unsupported scaffold type")
    order = tuple(int(value) for value in scaffold_record["scaffold_order"])
    if not order:
        raise ValueError("empty scaffold")
    leaf_nodes = [
        {
            "node_id": int(item["node_id"]),
            "kind": "LEAF",
            "factor_id": int(item["factor_id"]),
            "covered_factor_ids": [int(item["factor_id"])],
        }
        for item in scaffold_record["nodes"]
        if item["kind"] == "LEAF"
    ]
    if [item["factor_id"] for item in leaf_nodes] != list(order):
        raise AssertionError("B4.2 leaf topology/order mismatch")

    spine_nodes = sorted(
        (item for item in scaffold_record["nodes"] if item["kind"] == "SPINE"),
        key=lambda item: int(item["edge_index"]),
    )
    if len(spine_nodes) != max(0, len(order) - 2):
        raise AssertionError("B4.2 spine inventory mismatch")
    internal_nodes = []
    previous_node_id = int(order[0])
    for index, spine in enumerate(spine_nodes):
        if int(spine["edge_index"]) != index:
            raise AssertionError("B4.2 spine edge order mismatch")
        right_factor = int(order[index + 1])
        covered = list(order[: index + 2])
        internal_nodes.append(
            {
                "node_id": int(spine["node_id"]),
                "kind": "SPINE_INTERNAL_JOIN",
                "edge_index": index,
                "child_node_ids": [previous_node_id, right_factor],
                "left_factor_ids": list(order[: index + 1]),
                "right_factor_ids": [right_factor],
                "covered_factor_ids": covered,
                "outside_factor_ids": [value for value in order if value not in covered],
            }
        )
        previous_node_id = int(spine["node_id"])

    if len(order) >= 2:
        root_id = max(int(item["node_id"]) for item in scaffold_record["nodes"]) + 1
        right_factor = int(order[-1])
        left_factors = list(order[:-1])
        internal_nodes.append(
            {
                "node_id": root_id,
                "kind": "SYNTHETIC_ROOT_CLOSE",
                "edge_index": len(order) - 2,
                "child_node_ids": [previous_node_id, right_factor],
                "left_factor_ids": left_factors,
                "right_factor_ids": [right_factor],
                "covered_factor_ids": list(order),
                "outside_factor_ids": [],
            }
        )
    else:
        root_id = int(order[0])

    return {
        "traversal": "DETERMINISTIC_BOTTOM_UP_TOPOLOGICAL_ORDER",
        "scaffold_node_ids": [int(item["node_id"]) for item in scaffold_record["nodes"]],
        "synthetic_root_close_node_id": root_id if len(order) >= 2 else None,
        "leaf_nodes": leaf_nodes,
        "internal_nodes": internal_nodes,
        "topological_order": [item["node_id"] for item in leaf_nodes]
        + [item["node_id"] for item in internal_nodes],
        "root_node_id": root_id,
    }


def full_coordinate_boundary(theta: int) -> list[int]:
    return list(xor_basis((1 << index for index in range(theta)), theta))


def output_receipt(
    node_id: int,
    producer_kind: str,
    covered_factor_ids: Sequence[int],
    boundary_basis: Sequence[int],
    closure: dict,
    partition_digest: str,
) -> dict:
    receipt = {
        "node_id": int(node_id),
        "producer_kind": producer_kind,
        "covered_factor_ids": list(covered_factor_ids),
        "boundary_rref_ambient": list(boundary_basis),
        "boundary_coordinate_dimension": len(tuple(boundary_basis)),
        "full_set_digest": digest(closure),
        "entries_digest": digest(closure["entries"]),
        "entry_count": int(closure["entry_count"]),
        "grouped_partition_digest": partition_digest,
    }
    receipt["receipt_digest"] = digest(receipt)
    return receipt


def leaf_full_set(
    factor_id: int,
    factor_block: Sequence[int],
    affine_offset: int,
    boundary_basis: Sequence[int],
    ambient: int,
    k: int,
) -> dict:
    theta = len(tuple(boundary_basis))
    coordinate_boundary = full_coordinate_boundary(theta)
    if theta:
        generator_raw = [
            {"left": [], "right": coordinate_boundary, "value": 0},
            {"left": coordinate_boundary, "right": [], "value": 0},
        ]
        source = "canonical full-boundary whole-factor trajectory"
    else:
        generator_raw = [{"left": [], "right": [], "value": 0}]
        source = "canonical zero-boundary whole-factor trajectory"
    generator = b2_decode_trajectory(generator_raw, theta)
    ledger = Ledger(CAP, CAP)
    closure = up_k_closure([generator], theta, k, ledger)
    partition = {
        "factor_id": factor_id,
        "factor_block_rref": list(xor_basis(factor_block, ambient)),
        "affine_offset": int(affine_offset),
    }
    partition_digest = digest(partition)
    receipt = output_receipt(
        factor_id,
        "WHOLE_FACTOR_LEAF",
        [factor_id],
        boundary_basis,
        closure,
        partition_digest,
    )
    return {
        "node_id": factor_id,
        "factor_id": factor_id,
        "factor_block_rref": partition["factor_block_rref"],
        "affine_offset": int(affine_offset),
        "boundary_rref_ambient": list(boundary_basis),
        "boundary_coordinate_dimension": theta,
        "boundary_coordinate_rref": coordinate_boundary,
        "leaf_generator_coordinates": b2_encode(generator),
        "leaf_generator_ambient": b3_encode_trajectory(
            b44.lift_trajectory(generator_raw, boundary_basis, ambient)
        ),
        "full_set": closure,
        "partition_receipt": partition,
        "partition_receipt_digest": partition_digest,
        "output_receipt": receipt,
        "provenance": {
            "kind": "WHOLE_FACTOR_LEAF",
            "factor_id": factor_id,
            "generator_source": source,
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
    ) -> None:
        self.output_dir = output_dir
        self.kind = kind
        self.record_id_field = record_id_field
        self.chunk_size = chunk_size
        self.buffer: list[dict] = []
        self.metadata: list[dict] = []
        self.record_count = 0

    def add(self, record: dict) -> None:
        expected = self.record_count + len(self.buffer)
        if int(record[self.record_id_field]) != expected:
            raise AssertionError(f"{self.kind} global record id drift")
        self.buffer.append(bind_record(record))
        if len(self.buffer) == self.chunk_size:
            self._flush()

    def _flush(self) -> None:
        if not self.buffer:
            return
        index = len(self.metadata)
        previous_digest = self.metadata[-1]["compressed_sha256"] if index else None
        payload = {
            "schema": CHUNK_SCHEMA,
            "kind": self.kind,
            "chunk_index": index,
            "previous_chunk_index": index - 1 if index else None,
            "previous_chunk_digest": previous_digest,
            "record_id_field": self.record_id_field,
            "record_count": len(self.buffer),
            "records": self.buffer,
        }
        payload["chunk_payload_digest"] = digest(payload)
        raw = canonical_json(payload) + b"\n"
        compressed = deterministic_gzip(raw)
        filename = f"{self.kind.lower()}-{index:05d}.json.gz"
        path = self.output_dir / "chunks" / filename
        path.write_bytes(compressed)
        self.metadata.append(
            {
                "kind": self.kind,
                "chunk_index": index,
                "filename": f"chunks/{filename}",
                "record_id_field": self.record_id_field,
                "record_count": len(self.buffer),
                "first_record_id": int(self.buffer[0][self.record_id_field]),
                "last_record_id": int(self.buffer[-1][self.record_id_field]),
                "uncompressed_bytes": len(raw),
                "compressed_bytes": len(compressed),
                "chunk_payload_digest": payload["chunk_payload_digest"],
                "compressed_sha256": sha256_bytes(compressed),
                "previous_chunk_index": payload["previous_chunk_index"],
                "previous_chunk_digest": previous_digest,
                "next_chunk_index": None,
                "next_chunk_digest": None,
            }
        )
        self.record_count += len(self.buffer)
        self.buffer = []
        print(
            f"CHUNK {self.kind} {index} records={self.metadata[-1]['record_count']} "
            f"compressed={len(compressed)}",
            flush=True,
        )

    def finish(self) -> list[dict]:
        self._flush()
        for index, item in enumerate(self.metadata[:-1]):
            item["next_chunk_index"] = index + 1
            item["next_chunk_digest"] = self.metadata[index + 1]["compressed_sha256"]
        return self.metadata


def make_range(start: int, end: int) -> dict:
    return {
        "first": start if end > start else None,
        "last": end - 1 if end > start else None,
        "count": end - start,
    }


def execute_node(
    descriptor: dict,
    sequence_index: int,
    left_state: dict,
    right_state: dict,
    scaffold_record: dict,
    writers: dict[str, ChunkWriter],
    cumulative: list[int],
    capability: dict,
) -> tuple[dict, dict] | dict:
    ambient = int(scaffold_record["d"])
    k = int(scaffold_record["k"])
    blocks = [tuple(block) for block in scaffold_record["whole_factor_blocks"]]
    offsets = [int(value) for value in scaffold_record["affine_offsets"]]
    order = tuple(int(value) for value in scaffold_record["scaffold_order"])
    left_ids = tuple(int(value) for value in descriptor["left_factor_ids"])
    right_ids = tuple(int(value) for value in descriptor["right_factor_ids"])
    covered_ids = tuple(int(value) for value in descriptor["covered_factor_ids"])
    outside_ids = tuple(int(value) for value in descriptor["outside_factor_ids"])
    if tuple(left_state["covered_factor_ids"]) != left_ids:
        raise AssertionError("left state/topology handoff mismatch")
    if tuple(right_state["covered_factor_ids"]) != right_ids:
        raise AssertionError("right state/topology handoff mismatch")

    left_boundary = tuple(left_state["boundary"])
    right_boundary = tuple(right_state["boundary"])
    common = xor_basis((*left_boundary, *right_boundary), ambient)
    parent = boundary(
        [blocks[index] for index in covered_ids],
        [blocks[index] for index in outside_ids],
        ambient,
    )
    dimensions = [len(left_boundary), len(right_boundary), len(common), len(parent)]
    if max(dimensions, default=0) > int(capability["max_boundary_coordinate_dimension"]):
        return {
            "status": "OPEN_AT_NODE_CAPACITY",
            "node_id": descriptor["node_id"],
            "reason": "BOUNDARY_COORDINATE_DIMENSION_CAP_EXCEEDED",
            "required": max(dimensions),
            "cap": int(capability["max_boundary_coordinate_dimension"]),
            "terminal": TERMINAL,
            "no_layout_at_cap": False,
        }

    left_entries = left_state["closure"]["entries"]
    right_entries = right_state["closure"]["entries"]
    pair_total = len(left_entries) * len(right_entries)
    refinement_total = sum(
        b44.delannoy_path_count(
            len(left_entry["trajectory"]), len(right_entry["trajectory"])
        )
        for left_entry in left_entries
        for right_entry in right_entries
    )
    if pair_total > int(capability["max_child_pairs_per_node"]):
        return {
            "status": "OPEN_AT_NODE_CAPACITY",
            "node_id": descriptor["node_id"],
            "reason": "CHILD_PAIR_CAP_EXCEEDED",
            "required": pair_total,
            "cap": int(capability["max_child_pairs_per_node"]),
            "terminal": TERMINAL,
            "no_layout_at_cap": False,
        }
    if refinement_total > int(capability["max_refinements_per_node"]):
        return {
            "status": "OPEN_AT_NODE_CAPACITY",
            "node_id": descriptor["node_id"],
            "reason": "REFINEMENT_CAP_EXCEEDED",
            "required": refinement_total,
            "cap": int(capability["max_refinements_per_node"]),
            "terminal": TERMINAL,
            "no_layout_at_cap": False,
        }

    partition_payload = {
        "whole_factor_blocks": [list(block) for block in blocks],
        "affine_offsets": offsets,
        "scaffold_order": list(order),
        "child_node_ids": list(descriptor["child_node_ids"]),
        "left_factor_ids": list(left_ids),
        "right_factor_ids": list(right_ids),
        "covered_factor_ids": list(covered_ids),
        "outside_factor_ids": list(outside_ids),
    }
    partition_digest = digest(partition_payload)
    stage_partition_receipt = {
        "partition_receipt_digest": partition_digest,
        "left_expand_factor_ids": list(left_ids),
        "right_expand_factor_ids": list(right_ids),
        "join_factor_ids": list(covered_ids),
        "shrink_factor_ids": list(covered_ids),
        "outside_factor_ids": list(outside_ids),
    }

    left_transport_contract = boundary_transport(left_boundary, common, ambient)
    right_transport_contract = boundary_transport(right_boundary, common, ambient)
    shrink_transport_contract = boundary_transport(parent, common, ambient)
    expand_conditions = {}
    for side, factor_ids, child_boundary in (
        ("left", left_ids, left_boundary),
        ("right", right_ids, right_boundary),
    ):
        arrangement_span = span_for_ids(blocks, factor_ids, ambient)
        intersection = subspace_intersection(arrangement_span, common, ambient)
        if intersection != child_boundary:
            raise AssertionError("expand side condition failed")
        expand_conditions[side] = {
            "arrangement_span": list(arrangement_span),
            "intersection_with_common_boundary": list(intersection),
            "required_child_boundary": list(child_boundary),
            "satisfied": True,
        }
    left_augmented = subspace_sum(span_for_ids(blocks, left_ids, ambient), common, ambient)
    right_augmented = subspace_sum(span_for_ids(blocks, right_ids, ambient), common, ambient)
    join_intersection = subspace_intersection(left_augmented, right_augmented, ambient)
    if join_intersection != common:
        raise AssertionError("join side condition failed")

    starts = {kind: writer.record_count + len(writer.buffer) for kind, writer in writers.items()}
    cumulative_start = cumulative[0]
    successful_by_trajectory: dict[str, list[int]] = defaultdict(list)
    successful = 0
    failed = 0
    raw_precompact_statistics = 0
    local_pair_index = 0
    local_attempt_index = 0

    for left_index, left_entry in enumerate(left_entries):
        left = b44.lift_trajectory(left_entry["trajectory"], left_boundary, ambient)
        for right_index, right_entry in enumerate(right_entries):
            right = b44.lift_trajectory(right_entry["trajectory"], right_boundary, ambient)
            expanded_left, left_transport = expand_trajectory(
                left, left_boundary, common, ambient
            )
            expanded_right, right_transport = expand_trajectory(
                right, right_boundary, common, ambient
            )
            pair_id = writers["PAIRS"].record_count + len(writers["PAIRS"].buffer)
            first_attempt_id = writers["REFINEMENTS"].record_count + len(
                writers["REFINEMENTS"].buffer
            )
            expand_breakdown = {
                "pair_enumerations": 1,
                "expanded_statistics": len(expanded_left) + len(expanded_right),
                "boundary_coordinate_changes": len(
                    left_transport["child_basis_in_parent_coordinates"]
                )
                + len(right_transport["child_basis_in_parent_coordinates"]),
            }
            cumulative[0] += sum(expand_breakdown.values())
            cumulative_after_expand = cumulative[0]
            pair_paths = 0

            for path in lattice_paths(len(expanded_left), len(expanded_right)):
                attempt_id = writers["REFINEMENTS"].record_count + len(
                    writers["REFINEMENTS"].buffer
                )
                joined, join_receipt = join_trajectory(
                    expanded_left, expanded_right, path, common, ambient
                )
                shrunk, shrink_receipt = shrink_trajectory(joined, parent, ambient)
                output_ambient = b3_encode_trajectory(shrunk)
                output_coordinates = b44.lower_trajectory(
                    output_ambient, parent, ambient
                )
                output_width = width(shrunk)
                accepted = output_width <= k
                breakdown = b44.refinement_work(join_receipt, shrink_receipt)
                cumulative[0] += sum(breakdown.values())
                writers["REFINEMENTS"].add(
                    {
                        "record_kind": "REFINEMENT",
                        "node_id": descriptor["node_id"],
                        "attempt_id": attempt_id,
                        "local_attempt_index": local_attempt_index,
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
                        else f"output width {output_width} exceeds k={k}",
                        "partition_receipt_digest": partition_digest,
                        "work_breakdown": dict(sorted(breakdown.items())),
                        "cumulative_work": cumulative[0],
                    }
                )
                raw_precompact_statistics += int(join_receipt["raw_length"])
                if accepted:
                    successful += 1
                    successful_by_trajectory[trajectory_key(output_coordinates)].append(
                        attempt_id
                    )
                else:
                    failed += 1
                local_attempt_index += 1
                pair_paths += 1

            last_attempt_id = writers["REFINEMENTS"].record_count + len(
                writers["REFINEMENTS"].buffer
            ) - 1
            writers["PAIRS"].add(
                {
                    "record_kind": "PAIR",
                    "node_id": descriptor["node_id"],
                    "pair_id": pair_id,
                    "local_pair_index": local_pair_index,
                    "left_entry_index": left_index,
                    "right_entry_index": right_index,
                    "left_input_coordinates": left_entry["trajectory"],
                    "right_input_coordinates": right_entry["trajectory"],
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
                    "last_attempt_id": last_attempt_id,
                    "expand_work_breakdown": dict(sorted(expand_breakdown.items())),
                    "cumulative_work_after_expand": cumulative_after_expand,
                }
            )
            local_pair_index += 1

    if local_pair_index != pair_total or local_attempt_index != refinement_total:
        raise AssertionError("node child-product traversal incomplete")

    generator_start = writers["GENERATORS"].record_count + len(
        writers["GENERATORS"].buffer
    )
    deletion_start = writers["DELETIONS"].record_count + len(
        writers["DELETIONS"].buffer
    )
    generator_records = []
    for local_generator_index, key in enumerate(sorted(successful_by_trajectory)):
        trajectory_coordinates = json.loads(key)
        provenance_ids = successful_by_trajectory[key]
        generator_id = writers["GENERATORS"].record_count + len(
            writers["GENERATORS"].buffer
        )
        record = {
            "record_kind": "SUCCESSFUL_GENERATOR",
            "node_id": descriptor["node_id"],
            "generator_id": generator_id,
            "local_generator_index": local_generator_index,
            "trajectory_parent_coordinates": trajectory_coordinates,
            "trajectory_ambient": b3_encode_trajectory(
                b44.lift_trajectory(trajectory_coordinates, parent, ambient)
            ),
            "trajectory_digest": digest(trajectory_coordinates),
            "provenance_attempt_ids": provenance_ids,
            "canonical_retained_attempt_id": provenance_ids[0],
        }
        writers["GENERATORS"].add(record)
        generator_records.append(record)
        identity_path = [
            [index, index] for index in range(len(trajectory_coordinates))
        ]
        for removed_attempt in provenance_ids[1:]:
            deletion_id = writers["DELETIONS"].record_count + len(
                writers["DELETIONS"].buffer
            )
            writers["DELETIONS"].add(
                {
                    "record_kind": "DUPLICATE_DELETION",
                    "node_id": descriptor["node_id"],
                    "deletion_id": deletion_id,
                    "local_deletion_index": deletion_id - deletion_start,
                    "generator_id": generator_id,
                    "local_generator_index": local_generator_index,
                    "trajectory_digest": digest(trajectory_coordinates),
                    "removed_attempt_id": removed_attempt,
                    "retained_attempt_id": provenance_ids[0],
                    "witness": {
                        "path": identity_path,
                        "path_length": len(identity_path),
                    },
                    "reason": "IDENTICAL_REFINEMENT_OUTPUT",
                }
            )

    b2_generators = [
        b2_decode_trajectory(record["trajectory_parent_coordinates"], len(parent))
        for record in generator_records
    ]
    b2_ledger = Ledger(CAP, CAP)
    node_closure = up_k_closure(b2_generators, len(parent), k, b2_ledger)
    cumulative_before_b2 = cumulative[0]
    b2_breakdown = {
        "b2_discovery_work": int(node_closure["ledger"]["discovery_work"]),
        "b2_work": int(node_closure["ledger"]["work"]),
    }
    cumulative[0] += sum(b2_breakdown.values())

    generator_by_key = {
        trajectory_key(record["trajectory_parent_coordinates"]): record
        for record in generator_records
    }
    input_provenance = [
        {
            "input_generator_index": index,
            "generator_id": generator_by_key[trajectory_key(raw)]["generator_id"],
            "local_generator_index": generator_by_key[trajectory_key(raw)][
                "local_generator_index"
            ],
        }
        for index, raw in enumerate(node_closure["input_generators"])
    ]
    retained_provenance = [
        {
            "retained_generator_index": index,
            "generator_id": generator_by_key[trajectory_key(raw)]["generator_id"],
            "local_generator_index": generator_by_key[trajectory_key(raw)][
                "local_generator_index"
            ],
        }
        for index, raw in enumerate(node_closure["retained_generators"])
    ]
    entry_provenance = [
        {
            "entry_index": index,
            "source_generator_index": int(entry["source_generator_index"]),
            "generator_id": retained_provenance[
                int(entry["source_generator_index"])
            ]["generator_id"],
        }
        for index, entry in enumerate(node_closure["entries"])
    ]

    node_partition_digest = partition_digest
    receipt = output_receipt(
        descriptor["node_id"],
        descriptor["kind"],
        covered_ids,
        parent,
        node_closure,
        node_partition_digest,
    )
    ends = {kind: writer.record_count + len(writer.buffer) for kind, writer in writers.items()}
    node = {
        "node_id": descriptor["node_id"],
        "sequence_index": sequence_index,
        "kind": descriptor["kind"],
        "child_node_ids": list(descriptor["child_node_ids"]),
        "left_factor_ids": list(left_ids),
        "right_factor_ids": list(right_ids),
        "covered_factor_ids": list(covered_ids),
        "outside_factor_ids": list(outside_ids),
        "covered_affine_offsets": [offsets[index] for index in covered_ids],
        "grouped_partition_preserved": True,
        "partition_receipt": partition_payload,
        "partition_receipt_digest": partition_digest,
        "input_full_set_receipts": [
            left_state["output_receipt"],
            right_state["output_receipt"],
        ],
        "child_boundaries": {
            "left": list(left_boundary),
            "right": list(right_boundary),
        },
        "common_join_boundary": list(common),
        "parent_boundary": list(parent),
        "boundary_dimensions": {
            "children": [len(left_boundary), len(right_boundary)],
            "common": len(common),
            "parent": len(parent),
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
                "required_common_boundary": list(common),
                "satisfied": True,
            },
            "shrink": {
                "parent_contained_in_common": True,
                "parent_basis_in_common_coordinates": shrink_transport_contract[
                    "child_basis_in_parent_coordinates"
                ],
            },
        },
        "record_ranges": {
            kind.lower(): make_range(starts[kind], ends[kind]) for kind in writers
        },
        "node_up_k": node_closure,
        "input_generator_provenance": input_provenance,
        "retained_generator_provenance": retained_provenance,
        "entry_provenance": entry_provenance,
        "output_receipt": receipt,
        "work_ledger": {
            "cumulative_work_at_node_start": cumulative_start,
            "cumulative_work_before_node_b2": cumulative_before_b2,
            "node_b2_breakdown": b2_breakdown,
            "node_b2_work_delta": sum(b2_breakdown.values()),
            "cumulative_work_at_node_end": cumulative[0],
            "monotone_by_construction": True,
        },
        "audit": {
            "child_full_set_entries": [
                int(left_state["closure"]["entry_count"]),
                int(right_state["closure"]["entry_count"]),
            ],
            "child_pairs_processed": pair_total,
            "lattice_paths_processed": refinement_total,
            "successful_refinements": successful,
            "failed_refinements": failed,
            "raw_precompact_join_statistics": raw_precompact_statistics,
            "unique_successful_generators": len(generator_records),
            "duplicate_successful_outputs_deleted": ends["DELETIONS"]
            - deletion_start,
            "b2_dominance_deletions": len(node_closure["removals"]),
            "retained_generators": len(node_closure["retained_generators"]),
            "final_up_k_entries": int(node_closure["entry_count"]),
            "cumulative_work_delta": cumulative[0] - cumulative_start,
        },
    }
    node["node_execution_digest"] = digest(node)
    state = {
        "node_id": descriptor["node_id"],
        "covered_factor_ids": list(covered_ids),
        "boundary": list(parent),
        "closure": node_closure,
        "output_receipt": receipt,
    }
    return node, state


def build(
    output_dir: Path,
    max_refinements_per_node: int = DEFAULT_CAPABILITY["max_refinements_per_node"],
) -> dict:
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError("output directory must be empty")
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "chunks").mkdir()
    capability = dict(DEFAULT_CAPABILITY)
    capability["max_refinements_per_node"] = int(max_refinements_per_node)
    if any(not isinstance(value, int) or value < 0 for value in capability.values()):
        raise ValueError("invalid executor capability")

    scaffold_record = selected_scaffold()
    topology = derive_topology(scaffold_record)
    if len(topology["internal_nodes"]) > capability["max_internal_nodes"]:
        raise AssertionError("frozen topology exceeds internal-node capability")
    ambient = int(scaffold_record["d"])
    k = int(scaffold_record["k"])
    blocks = [tuple(block) for block in scaffold_record["whole_factor_blocks"]]
    offsets = [int(value) for value in scaffold_record["affine_offsets"]]

    cumulative = [0]
    leaf_work_events = []
    leaves = []
    states: dict[int, dict] = {}
    for leaf_descriptor in topology["leaf_nodes"]:
        factor_id = int(leaf_descriptor["factor_id"])
        leaf_boundary = boundary(
            [blocks[factor_id]],
            [blocks[index] for index in range(len(blocks)) if index != factor_id],
            ambient,
        )
        leaf = leaf_full_set(
            factor_id,
            blocks[factor_id],
            offsets[factor_id],
            leaf_boundary,
            ambient,
            k,
        )
        ledger = leaf["full_set"]["ledger"]
        breakdown = {
            "b2_discovery_work": int(ledger["discovery_work"]),
            "b2_work": int(ledger["work"]),
        }
        cumulative[0] += sum(breakdown.values())
        leaf_work_events.append(
            {
                "event_index": len(leaf_work_events),
                "node_id": factor_id,
                "kind": "LEAF_FULL_SET",
                "breakdown": breakdown,
                "work_delta": sum(breakdown.values()),
                "cumulative_work": cumulative[0],
            }
        )
        leaves.append(leaf)
        states[factor_id] = {
            "node_id": factor_id,
            "covered_factor_ids": [factor_id],
            "boundary": list(leaf_boundary),
            "closure": leaf["full_set"],
            "output_receipt": leaf["output_receipt"],
        }

    writers = {
        "PAIRS": ChunkWriter(output_dir, "PAIRS", "pair_id", PAIR_CHUNK_SIZE),
        "REFINEMENTS": ChunkWriter(
            output_dir, "REFINEMENTS", "attempt_id", REFINEMENT_CHUNK_SIZE
        ),
        "GENERATORS": ChunkWriter(
            output_dir, "GENERATORS", "generator_id", GENERATOR_CHUNK_SIZE
        ),
        "DELETIONS": ChunkWriter(
            output_dir, "DELETIONS", "deletion_id", DELETION_CHUNK_SIZE
        ),
    }
    node_results = []
    stop = None
    for sequence_index, descriptor in enumerate(topology["internal_nodes"]):
        left_state = states[int(descriptor["child_node_ids"][0])]
        right_state = states[int(descriptor["child_node_ids"][1])]
        result = execute_node(
            descriptor,
            sequence_index,
            left_state,
            right_state,
            scaffold_record,
            writers,
            cumulative,
            capability,
        )
        if isinstance(result, dict):
            stop = result
            break
        node, state = result
        node_results.append(node)
        states[int(descriptor["node_id"])] = state
        if int(node["node_up_k"]["entry_count"]) == 0:
            stop = {
                "status": "OPEN_AT_NODE_EMPTY_FULL_SET",
                "node_id": descriptor["node_id"],
                "reason": "EMPTY_FULL_SET_IS_NOT_A_COMPLETENESS_PROOF",
                "required": None,
                "cap": None,
                "terminal": TERMINAL,
                "no_layout_at_cap": False,
            }
            break

    chunk_groups = {kind: writer.finish() for kind, writer in writers.items()}
    all_chunks = [item for group in chunk_groups.values() for item in group]
    complete = stop is None and len(node_results) == len(topology["internal_nodes"])
    root_receipt = (
        states[int(topology["root_node_id"])]["output_receipt"] if complete else None
    )
    totals = {
        "leaf_full_sets": len(leaves),
        "internal_nodes_processed": len(node_results),
        "child_pairs_processed": sum(
            node["audit"]["child_pairs_processed"] for node in node_results
        ),
        "lattice_paths_processed": sum(
            node["audit"]["lattice_paths_processed"] for node in node_results
        ),
        "successful_refinements": sum(
            node["audit"]["successful_refinements"] for node in node_results
        ),
        "failed_refinements": sum(
            node["audit"]["failed_refinements"] for node in node_results
        ),
        "raw_precompact_join_statistics": sum(
            node["audit"]["raw_precompact_join_statistics"] for node in node_results
        ),
        "unique_successful_generators": sum(
            node["audit"]["unique_successful_generators"] for node in node_results
        ),
        "duplicate_successful_outputs_deleted": sum(
            node["audit"]["duplicate_successful_outputs_deleted"]
            for node in node_results
        ),
        "b2_dominance_deletions": sum(
            node["audit"]["b2_dominance_deletions"] for node in node_results
        ),
        "retained_generators_across_nodes": sum(
            node["audit"]["retained_generators"] for node in node_results
        ),
        "root_up_k_entries": int(root_receipt["entry_count"]) if root_receipt else None,
        "cumulative_work": cumulative[0],
        "chunk_count": len(all_chunks),
        "failures": 0,
    }
    manifest = {
        "schema": SCHEMA,
        "phase": "B4.5_UNIVERSAL_BOTTOM_UP_SCAFFOLD_EXECUTOR",
        "source_head": SOURCE_HEAD,
        "scaffold_case": scaffold_record,
        "executor_contract": {
            "accepted_scaffold_type": "CATERPILLAR_APPEND_NEW_LEAF",
            "topology_derivation": "B4.2 leaves and spine nodes plus explicit root-close join",
            "node_kernel": "B3 expand/join/shrink then B2 dominance/up_k",
            "boundary_handoff": "parent output receipt becomes exact child input receipt",
            "capacity_stop_terminal": TERMINAL,
            "empty_full_set_terminal": TERMINAL,
            "no_layout_at_cap_enabled": False,
        },
        "capability": capability,
        "topology": topology,
        "leaf_full_sets": leaves,
        "node_results": node_results,
        "execution": {
            "status": "ROOT_FULL_SET_COMPUTED" if complete else stop["status"],
            "processed_internal_node_ids": [node["node_id"] for node in node_results],
            "stopped_node_id": None if complete else stop["node_id"],
            "stop": stop,
            "root_node_id": topology["root_node_id"],
            "root_full_set_receipt": root_receipt,
        },
        "chunking": {
            "compression": "DETERMINISTIC_GZIP_DEFLATE9_MTIME0_OS255",
            "record_chunk_sizes": {
                "PAIRS": PAIR_CHUNK_SIZE,
                "REFINEMENTS": REFINEMENT_CHUNK_SIZE,
                "GENERATORS": GENERATOR_CHUNK_SIZE,
                "DELETIONS": DELETION_CHUNK_SIZE,
            },
            "tail_chunk_may_be_short": True,
            "chunk_groups": chunk_groups,
            "transcript_root_digest": digest(chunk_groups),
            "chunk_count": len(all_chunks),
            "uncompressed_chunk_bytes": sum(
                item["uncompressed_bytes"] for item in all_chunks
            ),
            "compressed_chunk_bytes": sum(item["compressed_bytes"] for item in all_chunks),
        },
        "work_ledger": {
            "leaf_full_set_events": leaf_work_events,
            "node_intervals": [
                {
                    "node_id": node["node_id"],
                    "start": node["work_ledger"]["cumulative_work_at_node_start"],
                    "end": node["work_ledger"]["cumulative_work_at_node_end"],
                }
                for node in node_results
            ],
            "cumulative_work_final": cumulative[0],
            "monotone_by_construction": True,
        },
        "audit": totals,
        "strict_boundary": {
            "scope": "one complete B4.2 scaffold execution under explicit capability bounds",
            "universal_kernel_implemented": True,
            "all_selected_scaffold_nodes_processed": complete,
            "root_full_set_computed": complete,
            "root_layout_reconstructed": False,
            "full_iterative_compression_cycle": False,
            "no_layout_at_cap_enabled": False,
            "found_layout_enabled": False,
            "current_global_terminal": TERMINAL,
            "next_gate": "C049.1_B4.6_FULL_ITERATIVE_COMPRESSION_CYCLE",
            "p_vs_np": "OPEN",
        },
    }
    manifest["manifest_digest"] = digest(manifest)
    raw = canonical_json(manifest) + b"\n"
    (output_dir / "manifest.json").write_bytes(raw)
    print("JANUS_C049_1_B4_5_BOTTOM_UP_SCAFFOLD_EXECUTOR = PASS")
    print("EXECUTION_STATUS =", manifest["execution"]["status"])
    print("NODES_PROCESSED =", len(node_results))
    print("ROOT_UP_K_ENTRIES =", totals["root_up_k_entries"])
    print("PAIRS =", totals["child_pairs_processed"])
    print("LATTICE_PATHS =", totals["lattice_paths_processed"])
    print("FAILED_REFINEMENTS =", totals["failed_refinements"])
    print("CUMULATIVE_WORK =", cumulative[0])
    print("CHUNKS =", len(all_chunks))
    print("UNCOMPRESSED_CHUNK_BYTES =", manifest["chunking"]["uncompressed_chunk_bytes"])
    print("COMPRESSED_CHUNK_BYTES =", manifest["chunking"]["compressed_chunk_bytes"])
    print("MANIFEST_DIGEST =", manifest["manifest_digest"])
    print("TRANSCRIPT_ROOT_DIGEST =", manifest["chunking"]["transcript_root_digest"])
    print("TERMINAL =", TERMINAL)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    parser.add_argument(
        "--max-refinements-per-node",
        type=int,
        default=DEFAULT_CAPABILITY["max_refinements_per_node"],
    )
    args = parser.parse_args()
    build(Path(args.output_dir), args.max_refinements_per_node)


if __name__ == "__main__":
    main()
