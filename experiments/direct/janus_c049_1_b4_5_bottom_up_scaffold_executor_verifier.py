#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import json
import struct
import zlib
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence

import janus_c049_1_b2_full_transcript_verifier as b2v
import janus_c049_1_b3_expand_join_shrink_verifier as b3v
import janus_c049_1_b4_4_nonzero_boundary_node_full_set_verifier as b44v


SCHEMA = "C049.1-B4.5-BOTTOM-UP-SCAFFOLD-EXECUTOR-MANIFEST-v1"
CHUNK_SCHEMA = "C049.1-B4.5-BOTTOM-UP-SCAFFOLD-EXECUTOR-CHUNK-v1"
TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"
SOURCE_HEAD = "6483e54aa5326ad7c34209bc45cad08affd8d967"

EXPECTED_CHUNK_SIZES = {
    "PAIRS": 128,
    "REFINEMENTS": 4096,
    "GENERATORS": 128,
    "DELETIONS": 2048,
}
EXPECTED_FROZEN_CHUNK_COUNTS = {
    "PAIRS": 11,
    "REFINEMENTS": 41,
    "GENERATORS": 1,
    "DELETIONS": 2,
}
EXPECTED_FROZEN_RECORD_COUNTS = {
    "PAIRS": 1368,
    "REFINEMENTS": 164072,
    "GENERATORS": 18,
    "DELETIONS": 3077,
}
EXPECTED_FROZEN_AUDIT = {
    "leaf_full_sets": 4,
    "internal_nodes_processed": 3,
    "child_pairs_processed": 1368,
    "lattice_paths_processed": 164072,
    "successful_refinements": 3095,
    "failed_refinements": 160977,
    "raw_precompact_join_statistics": 1298304,
    "unique_successful_generators": 18,
    "duplicate_successful_outputs_deleted": 3077,
    "b2_dominance_deletions": 15,
    "retained_generators_across_nodes": 3,
    "root_up_k_entries": 6,
    "cumulative_work": 5288362,
    "chunk_count": 55,
    "failures": 0,
}
EXPECTED_FROZEN_NODE_AUDITS = [
    {
        "child_full_set_entries": [36, 36],
        "child_pairs_processed": 1296,
        "lattice_paths_processed": 163824,
        "successful_refinements": 3025,
        "failed_refinements": 160799,
        "raw_precompact_join_statistics": 1297408,
        "unique_successful_generators": 6,
        "duplicate_successful_outputs_deleted": 3019,
        "b2_dominance_deletions": 5,
        "retained_generators": 1,
        "final_up_k_entries": 6,
        "cumulative_work_delta": 5234138,
    },
    {
        "child_full_set_entries": [6, 6],
        "child_pairs_processed": 36,
        "lattice_paths_processed": 124,
        "successful_refinements": 35,
        "failed_refinements": 89,
        "raw_precompact_join_statistics": 448,
        "unique_successful_generators": 6,
        "duplicate_successful_outputs_deleted": 29,
        "b2_dominance_deletions": 5,
        "retained_generators": 1,
        "final_up_k_entries": 6,
        "cumulative_work_delta": 2398,
    },
    {
        "child_full_set_entries": [6, 6],
        "child_pairs_processed": 36,
        "lattice_paths_processed": 124,
        "successful_refinements": 35,
        "failed_refinements": 89,
        "raw_precompact_join_statistics": 448,
        "unique_successful_generators": 6,
        "duplicate_successful_outputs_deleted": 29,
        "b2_dominance_deletions": 5,
        "retained_generators": 1,
        "final_up_k_entries": 6,
        "cumulative_work_delta": 2398,
    },
]


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


def trajectory_key(raw: Sequence[dict]) -> str:
    return canonical_json(raw).decode()


def span(
    blocks: Sequence[Sequence[int]], factor_ids: Sequence[int], ambient: int
) -> tuple[int, ...]:
    return b3v.rref(
        (row for factor_id in factor_ids for row in blocks[factor_id]), ambient
    )


def boundary(
    blocks: Sequence[Sequence[int]],
    left_ids: Sequence[int],
    right_ids: Sequence[int],
    ambient: int,
) -> tuple[int, ...]:
    return b3v.inter(
        span(blocks, left_ids, ambient), span(blocks, right_ids, ambient), ambient
    )


def full_coordinate_boundary(theta: int) -> list[int]:
    return list(b3v.rref((1 << index for index in range(theta)), theta))


def record_body(record: dict) -> dict:
    body = dict(record)
    body.pop("record_digest", None)
    return body


def verify_receipt(
    receipt: dict,
    node_id: int,
    producer_kind: str,
    covered_ids: Sequence[int],
    boundary_basis: Sequence[int],
    closure: dict,
    partition_digest: str,
) -> None:
    body = dict(receipt)
    claimed = body.pop("receipt_digest", None)
    expected = {
        "node_id": node_id,
        "producer_kind": producer_kind,
        "covered_factor_ids": list(covered_ids),
        "boundary_rref_ambient": list(boundary_basis),
        "boundary_coordinate_dimension": len(tuple(boundary_basis)),
        "full_set_digest": digest(closure),
        "entries_digest": digest(closure["entries"]),
        "entry_count": int(closure["entry_count"]),
        "grouped_partition_digest": partition_digest,
    }
    if body != expected or claimed != digest(expected):
        raise AssertionError("full-set output receipt mismatch")


def verify_b2_closure(closure: dict, expected_ledger: tuple[int, int]) -> None:
    expected = b2v.expected_closure(closure)
    for field in (
        "retained_generators",
        "removals",
        "universe_size",
        "entries",
        "entry_count",
    ):
        if closure[field] != expected[field]:
            raise AssertionError(f"B2 closure mismatch: {field}")
    ledger = closure["ledger"]
    if any(not isinstance(value, int) or value < 0 for value in ledger.values()):
        raise AssertionError("invalid B2 ledger")
    if (ledger.get("discovery_work"), ledger.get("work")) != expected_ledger:
        raise AssertionError("B2 frozen work ledger drift")


def verify_manifest_integrity(manifest: dict) -> None:
    body = dict(manifest)
    claimed = body.pop("manifest_digest", None)
    if claimed != digest(body):
        raise AssertionError("manifest digest mismatch")
    if manifest.get("schema") != SCHEMA:
        raise AssertionError("manifest schema mismatch")
    if manifest.get("source_head") != SOURCE_HEAD:
        raise AssertionError("source head mismatch")
    chunking = manifest["chunking"]
    if chunking["record_chunk_sizes"] != EXPECTED_CHUNK_SIZES:
        raise AssertionError("chunk sizes changed")
    groups = chunking["chunk_groups"]
    if set(groups) != set(EXPECTED_CHUNK_SIZES):
        raise AssertionError("chunk groups mismatch")
    if chunking["transcript_root_digest"] != digest(groups):
        raise AssertionError("transcript root digest mismatch")
    total_chunks = 0
    total_uncompressed = 0
    total_compressed = 0
    for kind, metadata in groups.items():
        expected_record_id = 0
        for index, item in enumerate(metadata):
            if item["kind"] != kind or item["chunk_index"] != index:
                raise AssertionError("chunk index mismatch")
            if item["record_id_field"] not in {
                "pair_id",
                "attempt_id",
                "generator_id",
                "deletion_id",
            }:
                raise AssertionError("chunk record id field mismatch")
            if item["first_record_id"] != expected_record_id:
                raise AssertionError("chunk global record range gap")
            if item["last_record_id"] != (
                item["first_record_id"] + item["record_count"] - 1
            ):
                raise AssertionError("chunk record range mismatch")
            if item["record_count"] <= 0 or item["record_count"] > EXPECTED_CHUNK_SIZES[kind]:
                raise AssertionError("invalid chunk record count")
            if index + 1 < len(metadata) and item["record_count"] != EXPECTED_CHUNK_SIZES[kind]:
                raise AssertionError("short non-tail chunk")
            previous = metadata[index - 1] if index else None
            following = metadata[index + 1] if index + 1 < len(metadata) else None
            if item["previous_chunk_index"] != (index - 1 if previous else None):
                raise AssertionError("previous chunk index mismatch")
            if item["previous_chunk_digest"] != (
                previous["compressed_sha256"] if previous else None
            ):
                raise AssertionError("previous chunk digest mismatch")
            if item["next_chunk_index"] != (index + 1 if following else None):
                raise AssertionError("next chunk index mismatch")
            if item["next_chunk_digest"] != (
                following["compressed_sha256"] if following else None
            ):
                raise AssertionError("next chunk digest mismatch")
            expected_record_id += int(item["record_count"])
            total_uncompressed += int(item["uncompressed_bytes"])
            total_compressed += int(item["compressed_bytes"])
        total_chunks += len(metadata)
    if chunking["chunk_count"] != total_chunks:
        raise AssertionError("chunk count mismatch")
    if chunking["uncompressed_chunk_bytes"] != total_uncompressed:
        raise AssertionError("uncompressed chunk volume mismatch")
    if chunking["compressed_chunk_bytes"] != total_compressed:
        raise AssertionError("compressed chunk volume mismatch")


def safe_chunk_path(root: Path, filename: str) -> Path:
    path = (root / filename).resolve()
    root_resolved = root.resolve()
    if root_resolved not in path.parents:
        raise AssertionError("chunk path escapes transcript root")
    return path


def parse_and_verify_chunk(meta: dict, compressed: bytes) -> dict:
    if len(compressed) != meta["compressed_bytes"]:
        raise AssertionError("compressed chunk length mismatch")
    if sha256_bytes(compressed) != meta["compressed_sha256"]:
        raise AssertionError("compressed chunk digest mismatch")
    raw = gzip.decompress(compressed)
    if len(raw) != meta["uncompressed_bytes"]:
        raise AssertionError("uncompressed chunk length mismatch")
    if deterministic_gzip(raw) != compressed:
        raise AssertionError("chunk compression is not deterministic")
    payload = json.loads(raw)
    if raw != canonical_json(payload) + b"\n":
        raise AssertionError("chunk JSON is not canonical")
    body = dict(payload)
    claimed = body.pop("chunk_payload_digest", None)
    if claimed != digest(body) or claimed != meta["chunk_payload_digest"]:
        raise AssertionError("chunk payload digest mismatch")
    for field in (
        "schema",
        "kind",
        "chunk_index",
        "previous_chunk_index",
        "previous_chunk_digest",
        "record_id_field",
        "record_count",
    ):
        expected = CHUNK_SCHEMA if field == "schema" else meta[field]
        if payload[field] != expected:
            raise AssertionError(f"chunk payload/manifest mismatch: {field}")
    if len(payload["records"]) != payload["record_count"]:
        raise AssertionError("chunk record count mismatch")
    identifier = payload["record_id_field"]
    for offset, record in enumerate(payload["records"]):
        if record.get(identifier) != meta["first_record_id"] + offset:
            raise AssertionError("record identifier mismatch")
        body = dict(record)
        record_digest = body.pop("record_digest", None)
        if record_digest != digest(body):
            raise AssertionError("record digest mismatch")
    return payload


class ChunkReader:
    def __init__(self, root: Path, manifest: dict, kind: str) -> None:
        self.root = root
        self.kind = kind
        self.metadata = manifest["chunking"]["chunk_groups"][kind]

    def __iter__(self) -> Iterator[dict]:
        for meta in self.metadata:
            compressed = safe_chunk_path(self.root, meta["filename"]).read_bytes()
            payload = parse_and_verify_chunk(meta, compressed)
            print(
                f"VERIFY_CHUNK {self.kind} {meta['chunk_index']} "
                f"records={meta['record_count']}",
                flush=True,
            )
            yield from payload["records"]


def recompute_edges(
    blocks: Sequence[Sequence[int]], order: Sequence[int], ambient: int
) -> tuple[list[dict], int]:
    edges = []
    work = 0
    for cut in range(1, len(order)):
        left_ids = order[:cut]
        right_ids = order[cut:]
        cut_boundary = boundary(blocks, left_ids, right_ids, ambient)
        work += sum(len(blocks[index]) for index in order) + len(cut_boundary) + 1
        edges.append(
            {
                "edge_index": cut - 1,
                "left_leaf_ids": list(left_ids),
                "right_leaf_ids": list(right_ids),
                "boundary_rref": list(cut_boundary),
                "width": len(cut_boundary),
                "cumulative_work": work,
            }
        )
    return edges, work


def expected_topology(scaffold: dict) -> dict:
    order = [int(value) for value in scaffold["scaffold_order"]]
    leaves = [
        {
            "node_id": factor_id,
            "kind": "LEAF",
            "factor_id": factor_id,
            "covered_factor_ids": [factor_id],
        }
        for factor_id in order
    ]
    spines = sorted(
        (item for item in scaffold["nodes"] if item["kind"] == "SPINE"),
        key=lambda item: int(item["edge_index"]),
    )
    internal = []
    previous = order[0]
    for index, spine in enumerate(spines):
        right = order[index + 1]
        covered = order[: index + 2]
        internal.append(
            {
                "node_id": int(spine["node_id"]),
                "kind": "SPINE_INTERNAL_JOIN",
                "edge_index": index,
                "child_node_ids": [previous, right],
                "left_factor_ids": order[: index + 1],
                "right_factor_ids": [right],
                "covered_factor_ids": covered,
                "outside_factor_ids": [value for value in order if value not in covered],
            }
        )
        previous = int(spine["node_id"])
    root = max(int(item["node_id"]) for item in scaffold["nodes"]) + 1
    internal.append(
        {
            "node_id": root,
            "kind": "SYNTHETIC_ROOT_CLOSE",
            "edge_index": len(order) - 2,
            "child_node_ids": [previous, order[-1]],
            "left_factor_ids": order[:-1],
            "right_factor_ids": [order[-1]],
            "covered_factor_ids": order,
            "outside_factor_ids": [],
        }
    )
    return {
        "traversal": "DETERMINISTIC_BOTTOM_UP_TOPOLOGICAL_ORDER",
        "scaffold_node_ids": [int(item["node_id"]) for item in scaffold["nodes"]],
        "synthetic_root_close_node_id": root,
        "leaf_nodes": leaves,
        "internal_nodes": internal,
        "topological_order": [item["node_id"] for item in leaves]
        + [item["node_id"] for item in internal],
        "root_node_id": root,
    }


def verify_scaffold_and_topology(
    manifest: dict,
) -> tuple[int, int, list[tuple[int, ...]], list[int], dict]:
    scaffold = manifest["scaffold_case"]
    body = {key: value for key, value in scaffold.items() if key != "semantic_digest"}
    if scaffold.get("semantic_digest") != digest(body):
        raise AssertionError("scaffold semantic digest mismatch")
    ambient = int(scaffold["d"])
    k = int(scaffold["k"])
    blocks = [b3v.rref(block, ambient) for block in scaffold["whole_factor_blocks"]]
    offsets = [int(value) for value in scaffold["affine_offsets"]]
    order = [int(value) for value in scaffold["scaffold_order"]]
    if (ambient, k) != (3, 1):
        raise AssertionError("wrong frozen scaffold dimensions")
    if blocks != [(1,), (1,), (2,), (4,)]:
        raise AssertionError("wrong frozen grouped factor blocks")
    if offsets != [0, 1, 0, 1]:
        raise AssertionError("affine offset fixture drift")
    if scaffold["previous_order"] != [0, 1, 2] or scaffold["new_leaf"] != 3:
        raise AssertionError("B4.2 compression round drift")
    if order != [0, 1, 2, 3]:
        raise AssertionError("scaffold order drift")
    previous_widths = [
        len(boundary(blocks, order[:cut], order[cut:3], ambient))
        for cut in range(1, 3)
    ]
    if scaffold["previous_width_vector"] != previous_widths or previous_widths != [1, 0]:
        raise AssertionError("previous layout replay mismatch")
    edges, charged_work = recompute_edges(blocks, order, ambient)
    if scaffold["candidate_edges"] != edges:
        raise AssertionError("B4.2 edge replay mismatch")
    if [edge["width"] for edge in edges] != [1, 0, 0]:
        raise AssertionError("B4.2 edge width drift")
    if scaffold["charged_work"] != charged_work:
        raise AssertionError("B4.2 work replay mismatch")
    expected_nodes = [
        {"node_id": factor_id, "kind": "LEAF", "factor_id": factor_id}
        for factor_id in order
    ] + [
        {"node_id": 4, "kind": "SPINE", "edge_index": 0},
        {"node_id": 5, "kind": "SPINE", "edge_index": 1},
    ]
    if scaffold["nodes"] != expected_nodes:
        raise AssertionError("B4.2 node inventory drift")
    if scaffold["terminal"] != "SCAFFOLD_3K_CERTIFIED":
        raise AssertionError("scaffold certification terminal drift")
    topology = expected_topology(scaffold)
    if manifest["topology"] != topology:
        raise AssertionError("bottom-up topology derivation mismatch")
    return ambient, k, blocks, offsets, topology


def verify_leaves(
    manifest: dict,
    ambient: int,
    k: int,
    blocks: Sequence[Sequence[int]],
    offsets: Sequence[int],
    topology: dict,
) -> tuple[dict[int, dict], int, list[dict]]:
    leaves = manifest["leaf_full_sets"]
    if len(leaves) != len(topology["leaf_nodes"]):
        raise AssertionError("leaf full-set inventory mismatch")
    states = {}
    cumulative = 0
    work_events = []
    all_ids = list(range(len(blocks)))
    for event_index, (descriptor, leaf) in enumerate(
        zip(topology["leaf_nodes"], leaves)
    ):
        factor_id = int(descriptor["factor_id"])
        if leaf["node_id"] != factor_id or leaf["factor_id"] != factor_id:
            raise AssertionError("leaf identity mismatch")
        leaf_boundary = boundary(
            blocks,
            [factor_id],
            [index for index in all_ids if index != factor_id],
            ambient,
        )
        theta = len(leaf_boundary)
        coordinate_boundary = full_coordinate_boundary(theta)
        if theta:
            generator = [
                {"left": [], "right": coordinate_boundary, "value": 0},
                {"left": coordinate_boundary, "right": [], "value": 0},
            ]
            source = "canonical full-boundary whole-factor trajectory"
            ledger_expected = (12768, 11853)
        else:
            generator = [{"left": [], "right": [], "value": 0}]
            source = "canonical zero-boundary whole-factor trajectory"
            ledger_expected = (29, 64)
        partition = {
            "factor_id": factor_id,
            "factor_block_rref": list(blocks[factor_id]),
            "affine_offset": offsets[factor_id],
        }
        partition_digest = digest(partition)
        expected_scalars = {
            "factor_block_rref": list(blocks[factor_id]),
            "affine_offset": offsets[factor_id],
            "boundary_rref_ambient": list(leaf_boundary),
            "boundary_coordinate_dimension": theta,
            "boundary_coordinate_rref": coordinate_boundary,
            "leaf_generator_coordinates": generator,
            "leaf_generator_ambient": b44v.lift_raw(generator, leaf_boundary, ambient),
            "partition_receipt": partition,
            "partition_receipt_digest": partition_digest,
            "provenance": {
                "kind": "WHOLE_FACTOR_LEAF",
                "factor_id": factor_id,
                "generator_source": source,
                "supplied_layout_used_for_discovery": False,
            },
        }
        for field, expected in expected_scalars.items():
            if leaf[field] != expected:
                raise AssertionError(f"leaf replay mismatch: {field}")
        verify_b2_closure(leaf["full_set"], ledger_expected)
        verify_receipt(
            leaf["output_receipt"],
            factor_id,
            "WHOLE_FACTOR_LEAF",
            [factor_id],
            leaf_boundary,
            leaf["full_set"],
            partition_digest,
        )
        ledger = leaf["full_set"]["ledger"]
        breakdown = {
            "b2_discovery_work": ledger["discovery_work"],
            "b2_work": ledger["work"],
        }
        cumulative += sum(breakdown.values())
        work_events.append(
            {
                "event_index": event_index,
                "node_id": factor_id,
                "kind": "LEAF_FULL_SET",
                "breakdown": breakdown,
                "work_delta": sum(breakdown.values()),
                "cumulative_work": cumulative,
            }
        )
        states[factor_id] = {
            "node_id": factor_id,
            "covered_factor_ids": [factor_id],
            "boundary": list(leaf_boundary),
            "closure": leaf["full_set"],
            "output_receipt": leaf["output_receipt"],
        }
    if manifest["work_ledger"]["leaf_full_set_events"] != work_events:
        raise AssertionError("leaf cumulative work ledger mismatch")
    return states, cumulative, work_events


def expected_node_context(
    descriptor: dict,
    left_state: dict,
    right_state: dict,
    ambient: int,
    blocks: Sequence[Sequence[int]],
    offsets: Sequence[int],
    order: Sequence[int],
) -> dict:
    left_ids = descriptor["left_factor_ids"]
    right_ids = descriptor["right_factor_ids"]
    covered_ids = descriptor["covered_factor_ids"]
    outside_ids = descriptor["outside_factor_ids"]
    if left_state["covered_factor_ids"] != left_ids:
        raise AssertionError("left bottom-up state mismatch")
    if right_state["covered_factor_ids"] != right_ids:
        raise AssertionError("right bottom-up state mismatch")
    left_boundary = tuple(left_state["boundary"])
    right_boundary = tuple(right_state["boundary"])
    common = b3v.rref((*left_boundary, *right_boundary), ambient)
    parent = boundary(blocks, covered_ids, outside_ids, ambient)
    partition = {
        "whole_factor_blocks": [list(block) for block in blocks],
        "affine_offsets": list(offsets),
        "scaffold_order": list(order),
        "child_node_ids": descriptor["child_node_ids"],
        "left_factor_ids": left_ids,
        "right_factor_ids": right_ids,
        "covered_factor_ids": covered_ids,
        "outside_factor_ids": outside_ids,
    }
    partition_digest = digest(partition)
    transports = {
        "left_child_to_common": b44v.expected_transport(
            left_boundary, common, ambient
        ),
        "right_child_to_common": b44v.expected_transport(
            right_boundary, common, ambient
        ),
        "parent_in_common_for_shrink": b44v.expected_transport(
            parent, common, ambient
        ),
    }
    expand = {}
    for side, ids, child_boundary in (
        ("left", left_ids, left_boundary),
        ("right", right_ids, right_boundary),
    ):
        arrangement = span(blocks, ids, ambient)
        intersection = b3v.inter(arrangement, common, ambient)
        expand[side] = {
            "arrangement_span": list(arrangement),
            "intersection_with_common_boundary": list(intersection),
            "required_child_boundary": list(child_boundary),
            "satisfied": intersection == child_boundary,
        }
        if not expand[side]["satisfied"]:
            raise AssertionError("independent expand side condition failed")
    left_augmented = b3v.sm(span(blocks, left_ids, ambient), common, ambient)
    right_augmented = b3v.sm(span(blocks, right_ids, ambient), common, ambient)
    intersection = b3v.inter(left_augmented, right_augmented, ambient)
    side_conditions = {
        "expand": expand,
        "join": {
            "left_augmented_span": list(left_augmented),
            "right_augmented_span": list(right_augmented),
            "intersection": list(intersection),
            "required_common_boundary": list(common),
            "satisfied": intersection == common,
        },
        "shrink": {
            "parent_contained_in_common": b3v.has(common, parent),
            "parent_basis_in_common_coordinates": [
                b3v.coord(row, common) for row in parent
            ],
        },
    }
    if not side_conditions["join"]["satisfied"]:
        raise AssertionError("independent join side condition failed")
    if not side_conditions["shrink"]["parent_contained_in_common"]:
        raise AssertionError("independent shrink side condition failed")
    return {
        "left_boundary": left_boundary,
        "right_boundary": right_boundary,
        "common": common,
        "parent": parent,
        "partition": partition,
        "partition_digest": partition_digest,
        "transports": transports,
        "side_conditions": side_conditions,
    }


def verify_node_header(
    node: dict,
    descriptor: dict,
    sequence_index: int,
    left_state: dict,
    right_state: dict,
    ambient: int,
    blocks: Sequence[Sequence[int]],
    offsets: Sequence[int],
    order: Sequence[int],
    cumulative: int,
) -> dict:
    body = dict(node)
    claimed = body.pop("node_execution_digest", None)
    if claimed != digest(body):
        raise AssertionError("node execution digest mismatch")
    for field in (
        "node_id",
        "kind",
        "child_node_ids",
        "left_factor_ids",
        "right_factor_ids",
        "covered_factor_ids",
        "outside_factor_ids",
    ):
        if node[field] != descriptor[field]:
            raise AssertionError(f"node topology mismatch: {field}")
    if node["sequence_index"] != sequence_index:
        raise AssertionError("node sequence index mismatch")
    if node["covered_affine_offsets"] != [
        offsets[index] for index in descriptor["covered_factor_ids"]
    ]:
        raise AssertionError("grouped affine offsets changed")
    if node["grouped_partition_preserved"] is not True:
        raise AssertionError("grouped partition claim missing")
    if node["input_full_set_receipts"] != [
        left_state["output_receipt"],
        right_state["output_receipt"],
    ]:
        raise AssertionError("full-set handoff receipt mismatch")
    context = expected_node_context(
        descriptor,
        left_state,
        right_state,
        ambient,
        blocks,
        offsets,
        order,
    )
    if node["partition_receipt"] != context["partition"]:
        raise AssertionError("grouped partition receipt mismatch")
    if node["partition_receipt_digest"] != context["partition_digest"]:
        raise AssertionError("grouped partition digest mismatch")
    if node["child_boundaries"] != {
        "left": list(context["left_boundary"]),
        "right": list(context["right_boundary"]),
    }:
        raise AssertionError("child boundary handoff mismatch")
    if node["common_join_boundary"] != list(context["common"]):
        raise AssertionError("common join boundary mismatch")
    if node["parent_boundary"] != list(context["parent"]):
        raise AssertionError("parent boundary mismatch")
    if node["boundary_dimensions"] != {
        "children": [len(context["left_boundary"]), len(context["right_boundary"])],
        "common": len(context["common"]),
        "parent": len(context["parent"]),
    }:
        raise AssertionError("boundary dimension mismatch")
    if node["transport_contracts"] != context["transports"]:
        raise AssertionError("RREF transport contract mismatch")
    if node["side_conditions"] != context["side_conditions"]:
        raise AssertionError("B3 side-condition receipt mismatch")
    if node["work_ledger"]["cumulative_work_at_node_start"] != cumulative:
        raise AssertionError("cumulative work reset at node handoff")
    return context


def verify_pair(
    pair: dict,
    node: dict,
    context: dict,
    left_state: dict,
    right_state: dict,
    ambient: int,
    expected_pair_id: int,
    local_pair_index: int,
) -> tuple[tuple[b3v.S, ...], tuple[b3v.S, ...], dict]:
    left_entries = left_state["closure"]["entries"]
    right_entries = right_state["closure"]["entries"]
    left_index = local_pair_index // len(right_entries)
    right_index = local_pair_index % len(right_entries)
    expected_fields = {
        "record_kind": "PAIR",
        "node_id": node["node_id"],
        "pair_id": expected_pair_id,
        "local_pair_index": local_pair_index,
        "left_entry_index": left_index,
        "right_entry_index": right_index,
    }
    for field, expected in expected_fields.items():
        if pair[field] != expected:
            raise AssertionError(f"pair identity mismatch: {field}")
    left_coordinates = left_entries[left_index]["trajectory"]
    right_coordinates = right_entries[right_index]["trajectory"]
    if pair["left_input_coordinates"] != left_coordinates:
        raise AssertionError("left child full-set provenance mismatch")
    if pair["right_input_coordinates"] != right_coordinates:
        raise AssertionError("right child full-set provenance mismatch")
    left_raw = b44v.lift_raw(left_coordinates, context["left_boundary"], ambient)
    right_raw = b44v.lift_raw(right_coordinates, context["right_boundary"], ambient)
    if pair["left_input_ambient"] != left_raw:
        raise AssertionError("left boundary coordinate lift mismatch")
    if pair["right_input_ambient"] != right_raw:
        raise AssertionError("right boundary coordinate lift mismatch")
    left = b3v.parse(left_raw, context["left_boundary"], ambient, True)
    right = b3v.parse(right_raw, context["right_boundary"], ambient, True)
    expected_left_expand = {
        "output_ambient": b3v.encg(left),
        "transport": context["transports"]["left_child_to_common"],
    }
    expected_right_expand = {
        "output_ambient": b3v.encg(right),
        "transport": context["transports"]["right_child_to_common"],
    }
    if pair["left_expand"] != expected_left_expand:
        raise AssertionError("left B3 expand/transport mismatch")
    if pair["right_expand"] != expected_right_expand:
        raise AssertionError("right B3 expand/transport mismatch")
    expected_stages = {
        "partition_receipt_digest": context["partition_digest"],
        "left_expand_factor_ids": node["left_factor_ids"],
        "right_expand_factor_ids": node["right_factor_ids"],
        "join_factor_ids": node["covered_factor_ids"],
        "shrink_factor_ids": node["covered_factor_ids"],
        "outside_factor_ids": node["outside_factor_ids"],
    }
    if pair["grouped_partition_stages"] != expected_stages:
        raise AssertionError("grouped partition stage receipt mismatch")
    breakdown = {
        "pair_enumerations": 1,
        "expanded_statistics": len(left) + len(right),
        "boundary_coordinate_changes": len(
            context["transports"]["left_child_to_common"][
                "child_basis_in_parent_coordinates"
            ]
        )
        + len(
            context["transports"]["right_child_to_common"][
                "child_basis_in_parent_coordinates"
            ]
        ),
    }
    if pair["expand_work_breakdown"] != dict(sorted(breakdown.items())):
        raise AssertionError("pair expand work mismatch")
    expected_paths = b3v.paths(len(left), len(right))
    if pair["lattice_path_count"] != len(expected_paths):
        raise AssertionError("pair lattice path count mismatch")
    return left, right, breakdown


def verify_refinement(
    attempt: dict,
    pair: dict,
    node: dict,
    context: dict,
    left: Sequence[b3v.S],
    right: Sequence[b3v.S],
    ambient: int,
    k: int,
    expected_attempt_id: int,
    local_attempt_index: int,
) -> tuple[dict, str | None]:
    expected_fields = {
        "record_kind": "REFINEMENT",
        "node_id": node["node_id"],
        "attempt_id": expected_attempt_id,
        "local_attempt_index": local_attempt_index,
        "pair_id": pair["pair_id"],
        "left_entry_index": pair["left_entry_index"],
        "right_entry_index": pair["right_entry_index"],
        "partition_receipt_digest": context["partition_digest"],
    }
    for field, expected in expected_fields.items():
        if attempt[field] != expected:
            raise AssertionError(f"refinement identity mismatch: {field}")
    expected_join = b3v.join(
        left, right, attempt["lattice_path"], context["common"], ambient
    )
    for field in (
        "boundary",
        "path",
        "raw_join",
        "raw_length",
        "raw_width",
        "stat_receipts",
        "compact_join",
        "compact_length",
        "compact_width",
    ):
        if attempt["join"][field] != expected_join[field]:
            raise AssertionError(f"B3 join mismatch: {field}")
    compact_join, join_trace = b44v.independent_compactification(
        attempt["join"]["raw_join"], context["common"], ambient
    )
    if compact_join != attempt["join"]["compact_join"]:
        raise AssertionError("join compact output mismatch")
    if join_trace != attempt["join"]["compactification_trace"]:
        raise AssertionError("join compactification transcript mismatch")
    joined = b3v.parse(compact_join, context["common"], ambient, True)
    projected, expected_shrink = b3v.projected(joined, context["parent"], ambient)
    for field in (
        "target_boundary",
        "projected_precompact",
        "projection_receipts",
        "output",
    ):
        if attempt["shrink"][field] != expected_shrink[field]:
            raise AssertionError(f"B3 shrink mismatch: {field}")
    compact_shrink, shrink_trace = b44v.independent_compactification(
        attempt["shrink"]["projected_precompact"], context["parent"], ambient
    )
    if compact_shrink != attempt["shrink"]["output"]:
        raise AssertionError("shrink compact output mismatch")
    if shrink_trace != attempt["shrink"]["compactification_trace"]:
        raise AssertionError("shrink compactification transcript mismatch")
    output_ambient = b3v.encg(projected)
    if attempt["output_ambient"] != output_ambient:
        raise AssertionError("ambient shrink output mismatch")
    output_coordinates = b44v.lower_raw(
        output_ambient, context["parent"], ambient
    )
    if attempt["output_parent_coordinates"] != output_coordinates:
        raise AssertionError("parent coordinate shrink output mismatch")
    output_width = max(stat.v for stat in projected)
    if attempt["output_width"] != output_width:
        raise AssertionError("refinement width mismatch")
    expected_status = "SUCCESS" if output_width <= k else "FAILED_WIDTH_CAP"
    if attempt["status"] != expected_status:
        raise AssertionError("refinement status mismatch")
    expected_reason = (
        None
        if expected_status == "SUCCESS"
        else f"output width {output_width} exceeds k={k}"
    )
    if attempt["failure_reason"] != expected_reason:
        raise AssertionError("failed refinement reason mismatch")
    breakdown = b44v.expected_refinement_work(attempt["join"], attempt["shrink"])
    if attempt["work_breakdown"] != dict(sorted(breakdown.items())):
        raise AssertionError("refinement work mismatch")
    key = trajectory_key(output_coordinates) if expected_status == "SUCCESS" else None
    return breakdown, key


def range_values(raw: dict, expected_first: int, expected_count: int) -> range:
    expected = {
        "first": expected_first if expected_count else None,
        "last": expected_first + expected_count - 1 if expected_count else None,
        "count": expected_count,
    }
    if raw != expected:
        raise AssertionError("node global record range mismatch")
    return range(expected_first, expected_first + expected_count)


def verify_node_output(
    node: dict,
    context: dict,
    successful_groups: dict[str, list[int]],
    generators: Sequence[dict],
    deletions: Sequence[dict],
    generator_cursor: int,
    deletion_cursor: int,
    ambient: int,
    k: int,
    cumulative: int,
) -> tuple[dict, int, int, int, dict]:
    expected_generators = []
    expected_deletions = []
    for local_index, key in enumerate(sorted(successful_groups)):
        raw = json.loads(key)
        provenance = successful_groups[key]
        generator_id = generator_cursor + local_index
        expected_generators.append(
            {
                "record_kind": "SUCCESSFUL_GENERATOR",
                "node_id": node["node_id"],
                "generator_id": generator_id,
                "local_generator_index": local_index,
                "trajectory_parent_coordinates": raw,
                "trajectory_ambient": b44v.lift_raw(raw, context["parent"], ambient),
                "trajectory_digest": digest(raw),
                "provenance_attempt_ids": provenance,
                "canonical_retained_attempt_id": provenance[0],
            }
        )
        identity_path = [[index, index] for index in range(len(raw))]
        for removed_attempt in provenance[1:]:
            expected_deletions.append(
                {
                    "record_kind": "DUPLICATE_DELETION",
                    "node_id": node["node_id"],
                    "deletion_id": deletion_cursor + len(expected_deletions),
                    "local_deletion_index": len(expected_deletions),
                    "generator_id": generator_id,
                    "local_generator_index": local_index,
                    "trajectory_digest": digest(raw),
                    "removed_attempt_id": removed_attempt,
                    "retained_attempt_id": provenance[0],
                    "witness": {
                        "path": identity_path,
                        "path_length": len(identity_path),
                    },
                    "reason": "IDENTICAL_REFINEMENT_OUTPUT",
                }
            )
    gen_range = range_values(
        node["record_ranges"]["generators"], generator_cursor, len(expected_generators)
    )
    del_range = range_values(
        node["record_ranges"]["deletions"], deletion_cursor, len(expected_deletions)
    )
    for actual, expected in zip((generators[index] for index in gen_range), expected_generators):
        if record_body(actual) != expected:
            raise AssertionError("successful generator provenance mismatch")
    for actual, expected in zip((deletions[index] for index in del_range), expected_deletions):
        if record_body(actual) != expected:
            raise AssertionError("duplicate deletion witness mismatch")

    closure = node["node_up_k"]
    expected_inputs = [
        item["trajectory_parent_coordinates"] for item in expected_generators
    ]
    if len(closure["input_generators"]) != len(expected_inputs) or sorted(
        trajectory_key(raw) for raw in closure["input_generators"]
    ) != sorted(trajectory_key(raw) for raw in expected_inputs):
        raise AssertionError("B3 generators not passed exactly into B2")
    verify_b2_closure(closure, (29, 503))
    generator_by_key = {
        trajectory_key(item["trajectory_parent_coordinates"]): item
        for item in expected_generators
    }
    expected_input_provenance = [
        {
            "input_generator_index": index,
            "generator_id": generator_by_key[trajectory_key(raw)]["generator_id"],
            "local_generator_index": generator_by_key[trajectory_key(raw)][
                "local_generator_index"
            ],
        }
        for index, raw in enumerate(closure["input_generators"])
    ]
    if node["input_generator_provenance"] != expected_input_provenance:
        raise AssertionError("B2 input generator provenance mismatch")
    expected_retained_provenance = [
        {
            "retained_generator_index": index,
            "generator_id": generator_by_key[trajectory_key(raw)]["generator_id"],
            "local_generator_index": generator_by_key[trajectory_key(raw)][
                "local_generator_index"
            ],
        }
        for index, raw in enumerate(closure["retained_generators"])
    ]
    if node["retained_generator_provenance"] != expected_retained_provenance:
        raise AssertionError("B2 retained generator provenance mismatch")
    expected_entry_provenance = [
        {
            "entry_index": index,
            "source_generator_index": int(entry["source_generator_index"]),
            "generator_id": expected_retained_provenance[
                int(entry["source_generator_index"])
            ]["generator_id"],
        }
        for index, entry in enumerate(closure["entries"])
    ]
    if node["entry_provenance"] != expected_entry_provenance:
        raise AssertionError("B2 final entry provenance mismatch")
    if node["work_ledger"]["cumulative_work_before_node_b2"] != cumulative:
        raise AssertionError("pre-B2 cumulative work mismatch")
    b2_breakdown = {
        "b2_discovery_work": closure["ledger"]["discovery_work"],
        "b2_work": closure["ledger"]["work"],
    }
    if node["work_ledger"]["node_b2_breakdown"] != b2_breakdown:
        raise AssertionError("node B2 work breakdown mismatch")
    if node["work_ledger"]["node_b2_work_delta"] != sum(b2_breakdown.values()):
        raise AssertionError("node B2 work delta mismatch")
    cumulative += sum(b2_breakdown.values())
    if node["work_ledger"]["cumulative_work_at_node_end"] != cumulative:
        raise AssertionError("node final cumulative work mismatch")
    if node["work_ledger"]["monotone_by_construction"] is not True:
        raise AssertionError("node work monotonicity claim missing")
    verify_receipt(
        node["output_receipt"],
        node["node_id"],
        node["kind"],
        node["covered_factor_ids"],
        context["parent"],
        closure,
        context["partition_digest"],
    )
    state = {
        "node_id": node["node_id"],
        "covered_factor_ids": node["covered_factor_ids"],
        "boundary": list(context["parent"]),
        "closure": closure,
        "output_receipt": node["output_receipt"],
    }
    return (
        state,
        generator_cursor + len(expected_generators),
        deletion_cursor + len(expected_deletions),
        cumulative,
        {
            "unique_generators": len(expected_generators),
            "duplicate_deletions": len(expected_deletions),
        },
    )


def expected_capacity_stop(
    descriptor: dict,
    left_state: dict,
    right_state: dict,
    capability: dict,
    ambient: int,
    blocks: Sequence[Sequence[int]],
) -> dict | None:
    common = b3v.rref((*left_state["boundary"], *right_state["boundary"]), ambient)
    parent = boundary(
        blocks,
        descriptor["covered_factor_ids"],
        descriptor["outside_factor_ids"],
        ambient,
    )
    required_dim = max(
        len(left_state["boundary"]),
        len(right_state["boundary"]),
        len(common),
        len(parent),
    )
    if required_dim > capability["max_boundary_coordinate_dimension"]:
        reason, required, cap = (
            "BOUNDARY_COORDINATE_DIMENSION_CAP_EXCEEDED",
            required_dim,
            capability["max_boundary_coordinate_dimension"],
        )
    else:
        left_entries = left_state["closure"]["entries"]
        right_entries = right_state["closure"]["entries"]
        pairs = len(left_entries) * len(right_entries)
        refinements = sum(
            len(b3v.paths(len(left["trajectory"]), len(right["trajectory"])))
            for left in left_entries
            for right in right_entries
        )
        if pairs > capability["max_child_pairs_per_node"]:
            reason, required, cap = (
                "CHILD_PAIR_CAP_EXCEEDED",
                pairs,
                capability["max_child_pairs_per_node"],
            )
        elif refinements > capability["max_refinements_per_node"]:
            reason, required, cap = (
                "REFINEMENT_CAP_EXCEEDED",
                refinements,
                capability["max_refinements_per_node"],
            )
        else:
            return None
    return {
        "status": "OPEN_AT_NODE_CAPACITY",
        "node_id": descriptor["node_id"],
        "reason": reason,
        "required": required,
        "cap": cap,
        "terminal": TERMINAL,
        "no_layout_at_cap": False,
    }


def verify_execution_terminal(
    manifest: dict,
    topology: dict,
    states: dict[int, dict],
    blocks: Sequence[Sequence[int]],
    ambient: int,
) -> bool:
    execution = manifest["execution"]
    processed = [node["node_id"] for node in manifest["node_results"]]
    if execution["processed_internal_node_ids"] != processed:
        raise AssertionError("processed node list mismatch")
    if execution["root_node_id"] != topology["root_node_id"]:
        raise AssertionError("root node id mismatch")
    complete = len(processed) == len(topology["internal_nodes"])
    if complete:
        root_state = states[topology["root_node_id"]]
        if execution != {
            "status": "ROOT_FULL_SET_COMPUTED",
            "processed_internal_node_ids": processed,
            "stopped_node_id": None,
            "stop": None,
            "root_node_id": topology["root_node_id"],
            "root_full_set_receipt": root_state["output_receipt"],
        }:
            raise AssertionError("root execution terminal mismatch")
        return True
    next_descriptor = topology["internal_nodes"][len(processed)]
    if processed and states[processed[-1]]["closure"]["entry_count"] == 0:
        expected_stop = {
            "status": "OPEN_AT_NODE_EMPTY_FULL_SET",
            "node_id": processed[-1],
            "reason": "EMPTY_FULL_SET_IS_NOT_A_COMPLETENESS_PROOF",
            "required": None,
            "cap": None,
            "terminal": TERMINAL,
            "no_layout_at_cap": False,
        }
    else:
        expected_stop = expected_capacity_stop(
            next_descriptor,
            states[next_descriptor["child_node_ids"][0]],
            states[next_descriptor["child_node_ids"][1]],
            manifest["capability"],
            ambient,
            blocks,
        )
    if expected_stop is None:
        raise AssertionError("executor stopped without a certified open condition")
    if execution != {
        "status": expected_stop["status"],
        "processed_internal_node_ids": processed,
        "stopped_node_id": expected_stop["node_id"],
        "stop": expected_stop,
        "root_node_id": topology["root_node_id"],
        "root_full_set_receipt": None,
    }:
        raise AssertionError("open execution terminal mismatch")
    return False


def verify_full_transcript(
    root: Path, manifest: dict, expect_frozen: bool = False
) -> dict:
    verify_manifest_integrity(manifest)
    ambient, k, blocks, offsets, topology = verify_scaffold_and_topology(manifest)
    if manifest["executor_contract"] != {
        "accepted_scaffold_type": "CATERPILLAR_APPEND_NEW_LEAF",
        "topology_derivation": "B4.2 leaves and spine nodes plus explicit root-close join",
        "node_kernel": "B3 expand/join/shrink then B2 dominance/up_k",
        "boundary_handoff": "parent output receipt becomes exact child input receipt",
        "capacity_stop_terminal": TERMINAL,
        "empty_full_set_terminal": TERMINAL,
        "no_layout_at_cap_enabled": False,
    }:
        raise AssertionError("executor contract drift")
    capability = manifest["capability"]
    if set(capability) != {
        "max_internal_nodes",
        "max_child_pairs_per_node",
        "max_refinements_per_node",
        "max_boundary_coordinate_dimension",
    }:
        raise AssertionError("capability contract mismatch")
    if any(not isinstance(value, int) or value < 0 for value in capability.values()):
        raise AssertionError("invalid capability value")
    if len(topology["internal_nodes"]) > capability["max_internal_nodes"]:
        raise AssertionError("topology exceeds claimed node capability")

    states, cumulative, leaf_events = verify_leaves(
        manifest, ambient, k, blocks, offsets, topology
    )
    pairs = list(ChunkReader(root, manifest, "PAIRS"))
    generators = list(ChunkReader(root, manifest, "GENERATORS"))
    deletions = list(ChunkReader(root, manifest, "DELETIONS"))
    for kind, records, identifier in (
        ("PAIR", pairs, "pair_id"),
        ("SUCCESSFUL_GENERATOR", generators, "generator_id"),
        ("DUPLICATE_DELETION", deletions, "deletion_id"),
    ):
        for index, record in enumerate(records):
            if record[identifier] != index or record["record_kind"] != kind:
                raise AssertionError("global chunk record ordering mismatch")
    attempts = iter(ChunkReader(root, manifest, "REFINEMENTS"))

    pair_cursor = 0
    attempt_cursor = 0
    generator_cursor = 0
    deletion_cursor = 0
    node_intervals = []
    computed_node_audits = []
    for sequence_index, node in enumerate(manifest["node_results"]):
        descriptor = topology["internal_nodes"][sequence_index]
        left_state = states[descriptor["child_node_ids"][0]]
        right_state = states[descriptor["child_node_ids"][1]]
        context = verify_node_header(
            node,
            descriptor,
            sequence_index,
            left_state,
            right_state,
            ambient,
            blocks,
            offsets,
            manifest["scaffold_case"]["scaffold_order"],
            cumulative,
        )
        left_entries = left_state["closure"]["entries"]
        right_entries = right_state["closure"]["entries"]
        pair_count = len(left_entries) * len(right_entries)
        pair_range = range_values(node["record_ranges"]["pairs"], pair_cursor, pair_count)
        successful_groups: dict[str, list[int]] = defaultdict(list)
        successful = 0
        failed = 0
        raw_precompact = 0
        node_attempt_start = attempt_cursor
        for local_pair_index, pair_index in enumerate(pair_range):
            pair = pairs[pair_index]
            left, right, expand_breakdown = verify_pair(
                pair,
                node,
                context,
                left_state,
                right_state,
                ambient,
                pair_index,
                local_pair_index,
            )
            cumulative += sum(expand_breakdown.values())
            if pair["cumulative_work_after_expand"] != cumulative:
                raise AssertionError("pair cumulative work mismatch")
            if pair["first_attempt_id"] != attempt_cursor:
                raise AssertionError("pair attempt range gap")
            claimed_paths = []
            for _ in range(pair["lattice_path_count"]):
                try:
                    attempt = next(attempts)
                except StopIteration as exc:
                    raise AssertionError("missing refinement record") from exc
                if attempt["attempt_id"] != attempt_cursor:
                    raise AssertionError("global refinement id gap")
                breakdown, successful_key = verify_refinement(
                    attempt,
                    pair,
                    node,
                    context,
                    left,
                    right,
                    ambient,
                    k,
                    attempt_cursor,
                    attempt_cursor - node_attempt_start,
                )
                cumulative += sum(breakdown.values())
                if attempt["cumulative_work"] != cumulative:
                    raise AssertionError("refinement cumulative work mismatch")
                claimed_paths.append(
                    tuple(tuple(cell) for cell in attempt["lattice_path"])
                )
                raw_precompact += int(attempt["join"]["raw_length"])
                if successful_key is None:
                    failed += 1
                else:
                    successful += 1
                    successful_groups[successful_key].append(attempt_cursor)
                attempt_cursor += 1
            if pair["last_attempt_id"] != attempt_cursor - 1:
                raise AssertionError("pair final refinement id mismatch")
            if tuple(sorted(claimed_paths)) != b3v.paths(len(left), len(right)):
                raise AssertionError("lattice path coverage mismatch")
        pair_cursor += pair_count
        attempt_count = attempt_cursor - node_attempt_start
        range_values(
            node["record_ranges"]["refinements"], node_attempt_start, attempt_count
        )
        cumulative_before_b2 = cumulative
        state, generator_cursor, deletion_cursor, cumulative, output_counts = (
            verify_node_output(
                node,
                context,
                successful_groups,
                generators,
                deletions,
                generator_cursor,
                deletion_cursor,
                ambient,
                k,
                cumulative,
            )
        )
        states[node["node_id"]] = state
        audit = {
            "child_full_set_entries": [len(left_entries), len(right_entries)],
            "child_pairs_processed": pair_count,
            "lattice_paths_processed": attempt_count,
            "successful_refinements": successful,
            "failed_refinements": failed,
            "raw_precompact_join_statistics": raw_precompact,
            "unique_successful_generators": output_counts["unique_generators"],
            "duplicate_successful_outputs_deleted": output_counts[
                "duplicate_deletions"
            ],
            "b2_dominance_deletions": len(node["node_up_k"]["removals"]),
            "retained_generators": len(node["node_up_k"]["retained_generators"]),
            "final_up_k_entries": int(node["node_up_k"]["entry_count"]),
            "cumulative_work_delta": cumulative
            - node["work_ledger"]["cumulative_work_at_node_start"],
        }
        if node["audit"] != audit:
            raise AssertionError("node frozen audit replay mismatch")
        computed_node_audits.append(audit)
        node_intervals.append(
            {
                "node_id": node["node_id"],
                "start": node["work_ledger"]["cumulative_work_at_node_start"],
                "end": cumulative,
            }
        )

    try:
        next(attempts)
    except StopIteration:
        pass
    else:
        raise AssertionError("extra refinement records")
    if pair_cursor != len(pairs):
        raise AssertionError("extra pair records")
    if generator_cursor != len(generators):
        raise AssertionError("extra generator records")
    if deletion_cursor != len(deletions):
        raise AssertionError("extra deletion records")
    complete = verify_execution_terminal(manifest, topology, states, blocks, ambient)

    work_ledger = manifest["work_ledger"]
    if work_ledger != {
        "leaf_full_set_events": leaf_events,
        "node_intervals": node_intervals,
        "cumulative_work_final": cumulative,
        "monotone_by_construction": True,
    }:
        raise AssertionError("global cumulative work ledger mismatch")
    root_receipt = manifest["execution"]["root_full_set_receipt"]
    audit = {
        "leaf_full_sets": len(manifest["leaf_full_sets"]),
        "internal_nodes_processed": len(manifest["node_results"]),
        "child_pairs_processed": sum(
            item["child_pairs_processed"] for item in computed_node_audits
        ),
        "lattice_paths_processed": sum(
            item["lattice_paths_processed"] for item in computed_node_audits
        ),
        "successful_refinements": sum(
            item["successful_refinements"] for item in computed_node_audits
        ),
        "failed_refinements": sum(
            item["failed_refinements"] for item in computed_node_audits
        ),
        "raw_precompact_join_statistics": sum(
            item["raw_precompact_join_statistics"] for item in computed_node_audits
        ),
        "unique_successful_generators": sum(
            item["unique_successful_generators"] for item in computed_node_audits
        ),
        "duplicate_successful_outputs_deleted": sum(
            item["duplicate_successful_outputs_deleted"]
            for item in computed_node_audits
        ),
        "b2_dominance_deletions": sum(
            item["b2_dominance_deletions"] for item in computed_node_audits
        ),
        "retained_generators_across_nodes": sum(
            item["retained_generators"] for item in computed_node_audits
        ),
        "root_up_k_entries": root_receipt["entry_count"] if root_receipt else None,
        "cumulative_work": cumulative,
        "chunk_count": manifest["chunking"]["chunk_count"],
        "failures": 0,
    }
    if manifest["audit"] != audit:
        raise AssertionError("global frozen audit mismatch")
    strict = manifest["strict_boundary"]
    if strict != {
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
    }:
        raise AssertionError("strict claim boundary mismatch")
    if expect_frozen:
        if not complete:
            raise AssertionError("frozen acceptance instance did not reach root")
        if manifest["capability"] != {
            "max_internal_nodes": 16,
            "max_child_pairs_per_node": 2000,
            "max_refinements_per_node": 250000,
            "max_boundary_coordinate_dimension": 3,
        }:
            raise AssertionError("frozen capability drift")
        if audit != EXPECTED_FROZEN_AUDIT:
            raise AssertionError("frozen global constants drift")
        if computed_node_audits != EXPECTED_FROZEN_NODE_AUDITS:
            raise AssertionError("frozen node constants drift")
        if {
            kind: len(metadata)
            for kind, metadata in manifest["chunking"]["chunk_groups"].items()
        } != EXPECTED_FROZEN_CHUNK_COUNTS:
            raise AssertionError("frozen chunk inventory drift")
        record_counts = {
            "PAIRS": len(pairs),
            "REFINEMENTS": attempt_cursor,
            "GENERATORS": len(generators),
            "DELETIONS": len(deletions),
        }
        if record_counts != EXPECTED_FROZEN_RECORD_COUNTS:
            raise AssertionError("frozen record inventory drift")
        if manifest["chunking"]["uncompressed_chunk_bytes"] != 950019171:
            raise AssertionError("frozen raw certificate volume drift")
        if manifest["chunking"]["compressed_chunk_bytes"] != 21292955:
            raise AssertionError("frozen compressed certificate volume drift")
        if manifest["manifest_digest"] != "bc435391247fd136209428cbf002aa9dfacea85044cbc88d9fc671f092d07914":
            raise AssertionError("frozen manifest digest drift")
        if manifest["chunking"]["transcript_root_digest"] != "2506f09d907682b4397365abc39d317103a20c72fe00b27ac82717f114fbbc1a":
            raise AssertionError("frozen transcript root digest drift")
    return {
        "complete": complete,
        "nodes": len(manifest["node_results"]),
        "pairs": pair_cursor,
        "refinements": attempt_cursor,
        "failed": audit["failed_refinements"],
        "root_entries": audit["root_up_k_entries"],
        "cumulative_work": cumulative,
    }


def rebind_receipt(receipt: dict) -> None:
    receipt.pop("receipt_digest", None)
    receipt["receipt_digest"] = digest(receipt)


def rebind_node(node: dict) -> None:
    node.pop("node_execution_digest", None)
    node["node_execution_digest"] = digest(node)


def rebind_manifest(manifest: dict) -> None:
    manifest.pop("manifest_digest", None)
    manifest["manifest_digest"] = digest(manifest)


def tamper_context(manifest: dict) -> tuple:
    ambient, k, blocks, offsets, topology = verify_scaffold_and_topology(manifest)
    states, cumulative, _ = verify_leaves(
        manifest, ambient, k, blocks, offsets, topology
    )
    return ambient, blocks, offsets, topology, states, cumulative


def expect_header_rejection(label: str, manifest: dict, target_index: int) -> None:
    verify_manifest_integrity(manifest)
    ambient, blocks, offsets, topology, states, cumulative = tamper_context(manifest)
    for index in range(target_index + 1):
        node = manifest["node_results"][index]
        descriptor = topology["internal_nodes"][index]
        left_state = states[descriptor["child_node_ids"][0]]
        right_state = states[descriptor["child_node_ids"][1]]
        try:
            context = verify_node_header(
                node,
                descriptor,
                index,
                left_state,
                right_state,
                ambient,
                blocks,
                offsets,
                manifest["scaffold_case"]["scaffold_order"],
                cumulative,
            )
        except AssertionError:
            if index == target_index:
                return
            raise
        closure = node["node_up_k"]
        verify_b2_closure(closure, (29, 503))
        verify_receipt(
            node["output_receipt"],
            node["node_id"],
            node["kind"],
            node["covered_factor_ids"],
            context["parent"],
            closure,
            context["partition_digest"],
        )
        cumulative = node["work_ledger"]["cumulative_work_at_node_end"]
        states[node["node_id"]] = {
            "node_id": node["node_id"],
            "covered_factor_ids": node["covered_factor_ids"],
            "boundary": list(context["parent"]),
            "closure": closure,
            "output_receipt": node["output_receipt"],
        }
    raise AssertionError(f"digest-repaired {label} tamper accepted")


def tamper_self_tests(manifest: dict) -> int:
    handoff = copy.deepcopy(manifest)
    receipt = handoff["node_results"][1]["input_full_set_receipts"][0]
    receipt["full_set_digest"] = "0" * 64
    rebind_receipt(receipt)
    rebind_node(handoff["node_results"][1])
    rebind_manifest(handoff)
    expect_header_rejection("full-set handoff", handoff, 1)

    transport = copy.deepcopy(manifest)
    transport["node_results"][0]["transport_contracts"][
        "left_child_to_common"
    ]["child_basis_in_parent_coordinates"] = [0]
    rebind_node(transport["node_results"][0])
    rebind_manifest(transport)
    expect_header_rejection("transport matrix", transport, 0)

    grouped = copy.deepcopy(manifest)
    grouped["node_results"][0]["covered_affine_offsets"] = [0, 0]
    rebind_node(grouped["node_results"][0])
    rebind_manifest(grouped)
    expect_header_rejection("grouped partition", grouped, 0)

    cumulative = copy.deepcopy(manifest)
    cumulative["node_results"][0]["work_ledger"][
        "cumulative_work_at_node_start"
    ] += 1
    rebind_node(cumulative["node_results"][0])
    rebind_manifest(cumulative)
    expect_header_rejection("cumulative work reset", cumulative, 0)
    return 4


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("transcript_dir")
    parser.add_argument("--expect-frozen", action="store_true")
    parser.add_argument("--tamper-self-test", action="store_true")
    args = parser.parse_args()
    root = Path(args.transcript_dir)
    manifest = json.loads((root / "manifest.json").read_text())
    result = verify_full_transcript(root, manifest, args.expect_frozen)
    tamper_count = tamper_self_tests(manifest) if args.tamper_self_test else 0
    print("VERIFIED C049.1 B4.5 UNIVERSAL BOTTOM-UP SCAFFOLD EXECUTOR")
    print("NODES_REPLAYED =", result["nodes"])
    print("PAIRS_REPLAYED =", result["pairs"])
    print("B3_REFINEMENTS_REPLAYED =", result["refinements"])
    print("FAILED_REFINEMENTS_REPLAYED =", result["failed"])
    print("ROOT_UP_K_ENTRIES_REPLAYED =", result["root_entries"])
    print("CUMULATIVE_WORK =", result["cumulative_work"])
    print("DIGEST_REPAIRED_TAMPER_CONTROLS =", tamper_count)
    print("TERMINAL =", TERMINAL)


if __name__ == "__main__":
    main()
