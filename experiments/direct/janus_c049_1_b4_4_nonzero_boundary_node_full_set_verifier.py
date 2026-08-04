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


SCHEMA = "C049.1-B4.4-NONZERO-BOUNDARY-NODE-MANIFEST-v1"
CHUNK_SCHEMA = "C049.1-B4.4-NONZERO-BOUNDARY-NODE-CHUNK-v1"
TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"
SOURCE_HEAD = "4287df8d9f5e3f18cd3ba41452cb494301c38ded"

EXPECTED_CHUNK_SIZES = {
    "PAIRS": 128,
    "REFINEMENTS": 4096,
    "GENERATORS": 128,
    "DELETIONS": 2048,
}
EXPECTED_CHUNK_COUNTS = {
    "PAIRS": 11,
    "REFINEMENTS": 40,
    "GENERATORS": 2,
    "DELETIONS": 6,
}
EXPECTED_RECORD_COUNTS = {
    "PAIRS": 1296,
    "REFINEMENTS": 163824,
    "GENERATORS": 252,
    "DELETIONS": 11821,
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


def trajectory_key(raw: Sequence[dict]) -> str:
    return canonical_json(raw).decode()


def span(blocks: Iterable[Sequence[int]], ambient_dim: int) -> tuple[int, ...]:
    return b3v.rref((row for block in blocks for row in block), ambient_dim)


def boundary(
    left: Sequence[Sequence[int]], right: Sequence[Sequence[int]], ambient_dim: int
) -> tuple[int, ...]:
    return b3v.inter(span(left, ambient_dim), span(right, ambient_dim), ambient_dim)


def expected_transport(
    child_boundary: Sequence[int], parent_boundary: Sequence[int], ambient_dim: int
) -> dict:
    child = b3v.rref(child_boundary, ambient_dim)
    parent = b3v.rref(parent_boundary, ambient_dim)
    if not b3v.has(parent, child):
        raise AssertionError("transport containment failed")
    return {
        "child_boundary": list(child),
        "parent_boundary": list(parent),
        "child_basis_in_parent_coordinates": [
            b3v.coord(row, parent) for row in child
        ],
    }


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
    return b3v.rref(rows, ambient_dim)


def ambient_space_to_coordinates(
    ambient_space: Iterable[int], ambient_basis: Sequence[int]
) -> tuple[int, ...]:
    return b3v.rref(
        (b3v.coord(int(row), ambient_basis) for row in ambient_space),
        len(tuple(ambient_basis)),
    )


def lift_raw(
    raw: Sequence[dict], boundary_basis: Sequence[int], ambient_dim: int
) -> list[dict]:
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
    return b3v.encg(b3v.parse(lifted, boundary_basis, ambient_dim, True))


def lower_raw(
    raw: Sequence[dict], boundary_basis: Sequence[int], ambient_dim: int
) -> list[dict]:
    parsed = b3v.parse(raw, boundary_basis, ambient_dim, True)
    lowered = [
        {
            "left": list(ambient_space_to_coordinates(stat.l, boundary_basis)),
            "right": list(ambient_space_to_coordinates(stat.r, boundary_basis)),
            "value": stat.v,
        }
        for stat in parsed
    ]
    b2v.trajectory(lowered, len(tuple(boundary_basis)))
    return lowered


def independent_compactification(
    raw: Sequence[dict], boundary_basis: Sequence[int], ambient_dim: int
) -> tuple[list[dict], list[dict]]:
    sequence = list(b3v.parse(raw, boundary_basis, ambient_dim, False))
    trace: list[dict] = []
    while True:
        changed = False
        for index in range(1, len(sequence)):
            if sequence[index - 1] != sequence[index]:
                continue
            before = len(sequence)
            removed = [b3v.enc(sequence[index])]
            del sequence[index]
            trace.append(
                {
                    "rule": "duplicate",
                    "start": index - 1,
                    "end": index,
                    "removed": removed,
                    "before_length": before,
                    "after_length": len(sequence),
                }
            )
            changed = True
            break
        if changed:
            continue
        for start in range(len(sequence)):
            for end in range(start + 2, len(sequence)):
                if (
                    sequence[start].l,
                    sequence[start].r,
                ) != (
                    sequence[end].l,
                    sequence[end].r,
                ):
                    continue
                values = [item.v for item in sequence[start : end + 1]]
                increasing = values[0] <= values[-1] and all(
                    values[0] <= value <= values[-1]
                    for value in values[1:-1]
                )
                decreasing = values[0] >= values[-1] and all(
                    values[0] >= value >= values[-1]
                    for value in values[1:-1]
                )
                if not increasing and not decreasing:
                    continue
                before = len(sequence)
                removed = [b3v.enc(item) for item in sequence[start + 1 : end]]
                del sequence[start + 1 : end]
                trace.append(
                    {
                        "rule": "interval",
                        "start": start,
                        "end": end,
                        "removed": removed,
                        "before_length": before,
                        "after_length": len(sequence),
                    }
                )
                changed = True
                break
            if changed:
                break
        if not changed:
            return b3v.encg(sequence), trace


def compaction_removed(trace: Sequence[dict]) -> int:
    return sum(len(step["removed"]) for step in trace)


def expected_refinement_work(join_receipt: dict, shrink_receipt: dict) -> dict:
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
        raise AssertionError("B2 ledger total drift")


def verify_manifest_integrity(manifest: dict) -> None:
    body = dict(manifest)
    claimed = body.pop("manifest_digest", None)
    if claimed != digest(body):
        raise AssertionError("manifest digest mismatch")
    if manifest.get("schema") != SCHEMA:
        raise AssertionError("manifest schema mismatch")
    if manifest.get("source_head") != SOURCE_HEAD:
        raise AssertionError("source head drift")
    chunking = manifest["chunking"]
    groups = chunking["chunk_groups"]
    if chunking["transcript_root_digest"] != digest(groups):
        raise AssertionError("transcript root digest mismatch")
    if set(groups) != set(EXPECTED_CHUNK_SIZES):
        raise AssertionError("chunk groups mismatch")
    total_chunks = 0
    total_uncompressed = 0
    total_compressed = 0
    for kind, metadata in groups.items():
        if len(metadata) != EXPECTED_CHUNK_COUNTS[kind]:
            raise AssertionError(f"{kind} chunk count mismatch")
        expected_record_id = 0
        for index, item in enumerate(metadata):
            if item["kind"] != kind or item["chunk_index"] != index:
                raise AssertionError("chunk index mismatch")
            if item["previous_chunk_index"] != (index - 1 if index else None):
                raise AssertionError("previous chunk index mismatch")
            if item["next_chunk_index"] != (
                index + 1 if index + 1 < len(metadata) else None
            ):
                raise AssertionError("next chunk index mismatch")
            expected_previous_digest = (
                metadata[index - 1]["compressed_sha256"] if index else None
            )
            expected_next_digest = (
                metadata[index + 1]["compressed_sha256"]
                if index + 1 < len(metadata)
                else None
            )
            if item["previous_chunk_digest"] != expected_previous_digest:
                raise AssertionError("previous chunk digest cross-reference mismatch")
            if item["next_chunk_digest"] != expected_next_digest:
                raise AssertionError("next chunk digest cross-reference mismatch")
            if item["first_record_id"] != expected_record_id:
                raise AssertionError("chunk record IDs not contiguous")
            if item["last_record_id"] != (
                item["first_record_id"] + item["record_count"] - 1
            ):
                raise AssertionError("chunk record range mismatch")
            if index + 1 < len(metadata):
                if item["record_count"] != EXPECTED_CHUNK_SIZES[kind]:
                    raise AssertionError("non-tail chunk is not fixed size")
            elif not (0 < item["record_count"] <= EXPECTED_CHUNK_SIZES[kind]):
                raise AssertionError("invalid tail chunk size")
            expected_record_id += item["record_count"]
            total_uncompressed += item["uncompressed_bytes"]
            total_compressed += item["compressed_bytes"]
        if expected_record_id != EXPECTED_RECORD_COUNTS[kind]:
            raise AssertionError(f"{kind} record count mismatch")
        total_chunks += len(metadata)
    if chunking["chunk_count"] != total_chunks != 59:
        raise AssertionError("total chunk count mismatch")
    if chunking["uncompressed_chunk_bytes"] != total_uncompressed:
        raise AssertionError("uncompressed certificate volume mismatch")
    if chunking["compressed_chunk_bytes"] != total_compressed:
        raise AssertionError("compressed certificate volume mismatch")


def safe_chunk_path(root: Path, filename: str) -> Path:
    candidate = (root / filename).resolve()
    resolved_root = root.resolve()
    if candidate != resolved_root and resolved_root not in candidate.parents:
        raise AssertionError("chunk path escapes transcript root")
    return candidate


def parse_and_verify_chunk(meta: dict, compressed: bytes) -> dict:
    if len(compressed) != meta["compressed_bytes"]:
        raise AssertionError("compressed chunk size mismatch")
    if sha256_bytes(compressed) != meta["compressed_sha256"]:
        raise AssertionError("compressed chunk digest mismatch")
    raw = gzip.decompress(compressed)
    if len(raw) != meta["uncompressed_bytes"]:
        raise AssertionError("uncompressed chunk size mismatch")
    if deterministic_gzip(raw) != compressed:
        raise AssertionError("chunk compression is not deterministic")
    payload = json.loads(raw)
    if canonical_json(payload) + b"\n" != raw:
        raise AssertionError("chunk is not canonical JSON")
    body = dict(payload)
    claimed = body.pop("chunk_payload_digest", None)
    if claimed != digest(body) or claimed != meta["chunk_payload_digest"]:
        raise AssertionError("chunk payload digest mismatch")
    for field in (
        "kind",
        "chunk_index",
        "previous_chunk_index",
        "next_chunk_index",
        "record_id_field",
        "record_count",
    ):
        if payload[field] != meta[field]:
            raise AssertionError(f"chunk header mismatch: {field}")
    if len(payload["records"]) != payload["record_count"]:
        raise AssertionError("chunk record count mismatch")
    identifier = payload["record_id_field"]
    for offset, record in enumerate(payload["records"]):
        expected_id = meta["first_record_id"] + offset
        if record.get(identifier) != expected_id:
            raise AssertionError("record identifier mismatch")
        record_body = dict(record)
        record_digest = record_body.pop("record_digest", None)
        if record_digest != digest(record_body):
            raise AssertionError("record digest mismatch")
    return payload


class ChunkReader:
    def __init__(self, root: Path, manifest: dict, kind: str) -> None:
        self.root = root
        self.kind = kind
        self.metadata = manifest["chunking"]["chunk_groups"][kind]

    def __iter__(self) -> Iterator[dict]:
        for meta in self.metadata:
            path = safe_chunk_path(self.root, meta["filename"])
            compressed = path.read_bytes()
            payload = parse_and_verify_chunk(meta, compressed)
            print(
                f"VERIFY_CHUNK {self.kind} "
                f"{meta['chunk_index'] + 1}/{len(self.metadata)} "
                f"records={meta['record_count']}",
                flush=True,
            )
            yield from payload["records"]


def verify_scaffold(manifest: dict) -> tuple[int, list[tuple[int, ...]], tuple[int, ...]]:
    scaffold = manifest["scaffold_case"]
    body = {key: value for key, value in scaffold.items() if key != "semantic_digest"}
    if scaffold.get("semantic_digest") != digest(body):
        raise AssertionError("scaffold semantic digest mismatch")
    ambient = int(scaffold["d"])
    if ambient != 4 or int(scaffold["k"]) != 1:
        raise AssertionError("wrong scaffold dimensions")
    blocks = [b3v.rref(block, ambient) for block in scaffold["whole_factor_blocks"]]
    order = tuple(int(index) for index in scaffold["scaffold_order"])
    if blocks != [(1,), (2,), (4,), (8,), (3,), (12,)]:
        raise AssertionError("wrong B4.2 block fixture")
    if order != (0, 4, 2, 3, 1, 5):
        raise AssertionError("wrong B4.2 scaffold order")
    work = 0
    expected_edges = []
    for cut in range(1, len(order)):
        left = [blocks[index] for index in order[:cut]]
        right = [blocks[index] for index in order[cut:]]
        cut_boundary = boundary(left, right, ambient)
        work += sum(len(block) for block in left + right) + len(cut_boundary) + 1
        expected_edges.append(
            {
                "edge_index": cut - 1,
                "left_leaf_ids": list(order[:cut]),
                "right_leaf_ids": list(order[cut:]),
                "boundary_rref": list(cut_boundary),
                "width": len(cut_boundary),
                "cumulative_work": work,
            }
        )
    if scaffold["candidate_edges"] != expected_edges:
        raise AssertionError("scaffold edge replay mismatch")
    if scaffold["charged_work"] != work or scaffold["next_terminal"] != TERMINAL:
        raise AssertionError("scaffold work/terminal mismatch")
    return ambient, blocks, order


def verify_node(
    manifest: dict,
    ambient: int,
    blocks: Sequence[Sequence[int]],
    order: Sequence[int],
) -> dict:
    node = manifest["node"]
    if node["node_id"] != 6 or node["kind"] != "SPINE_INTERNAL_JOIN":
        raise AssertionError("wrong internal node")
    if node["covered_factor_ids"] != [0, 4]:
        raise AssertionError("covered factors mismatch")
    if node["outside_factor_ids"] != [2, 3, 1, 5]:
        raise AssertionError("outside factors mismatch")
    if [b3v.rref(block, ambient) for block in node["whole_factor_blocks"]] != list(blocks):
        raise AssertionError("grouped blocks changed")
    if node["affine_offsets"] != manifest["scaffold_case"]["affine_offsets"]:
        raise AssertionError("affine offsets changed")
    if node["covered_affine_offsets"] != [0, 1]:
        raise AssertionError("covered offsets mismatch")
    if not node["grouped_partition_preserved"]:
        raise AssertionError("grouped partition lost")

    partition_payload = {
        "whole_factor_blocks": [list(block) for block in blocks],
        "affine_offsets": manifest["scaffold_case"]["affine_offsets"],
        "scaffold_order": list(order),
        "covered_factor_ids": [0, 4],
        "outside_factor_ids": [2, 3, 1, 5],
    }
    partition_digest = digest(partition_payload)
    if node["partition_receipt"] != partition_payload:
        raise AssertionError("partition receipt mismatch")
    if node["partition_receipt_digest"] != partition_digest:
        raise AssertionError("partition receipt digest mismatch")

    child_boundaries = {
        child: boundary(
            [blocks[child]],
            [blocks[index] for index in range(len(blocks)) if index != child],
            ambient,
        )
        for child in (0, 4)
    }
    common = b3v.rref((*child_boundaries[0], *child_boundaries[4]), ambient)
    parent = boundary(
        [blocks[0], blocks[4]],
        [blocks[index] for index in (2, 3, 1, 5)],
        ambient,
    )
    if child_boundaries != {0: (1,), 4: (3,)}:
        raise AssertionError("child boundary recomputation drift")
    if common != (2, 1) or parent != (2,):
        raise AssertionError("common/parent boundary drift")
    if node["child_boundaries"] != {"0": [1], "4": [3]}:
        raise AssertionError("recorded child boundaries mismatch")
    if node["common_join_boundary"] != [2, 1] or node["parent_boundary"] != [2]:
        raise AssertionError("recorded nonzero boundaries mismatch")
    if node["boundary_dimensions"] != {"children": [1, 1], "common": 2, "parent": 1}:
        raise AssertionError("boundary dimensions mismatch")
    if node["width_cap"] != 1:
        raise AssertionError("width cap drift")

    contracts = node["transport_contracts"]
    expected_contracts = {
        "left_child_to_common": expected_transport(child_boundaries[0], common, ambient),
        "right_child_to_common": expected_transport(child_boundaries[4], common, ambient),
        "parent_in_common_for_shrink": expected_transport(parent, common, ambient),
    }
    if contracts != expected_contracts:
        raise AssertionError("RREF transport contract mismatch")
    if contracts["left_child_to_common"]["child_basis_in_parent_coordinates"] != [2]:
        raise AssertionError("left transport is not nontrivial")
    if contracts["right_child_to_common"]["child_basis_in_parent_coordinates"] != [3]:
        raise AssertionError("right transport is not nontrivial")
    if contracts["parent_in_common_for_shrink"]["child_basis_in_parent_coordinates"] != [1]:
        raise AssertionError("shrink transport mismatch")

    side = node["side_conditions"]
    for child in (0, 4):
        arrangement = b3v.rref(blocks[child], ambient)
        intersection = b3v.inter(arrangement, common, ambient)
        expected = {
            "arrangement_span": list(arrangement),
            "intersection_with_common_boundary": list(intersection),
            "required_child_boundary": list(child_boundaries[child]),
            "satisfied": intersection == child_boundaries[child],
        }
        if side["expand"][str(child)] != expected or not expected["satisfied"]:
            raise AssertionError("expand side condition mismatch")
    left_augmented = b3v.sm(blocks[0], common, ambient)
    right_augmented = b3v.sm(blocks[4], common, ambient)
    join_intersection = b3v.inter(left_augmented, right_augmented, ambient)
    expected_join = {
        "left_augmented_span": list(left_augmented),
        "right_augmented_span": list(right_augmented),
        "intersection": list(join_intersection),
        "required_common_boundary": list(common),
        "satisfied": join_intersection == common,
    }
    if side["join"] != expected_join or not expected_join["satisfied"]:
        raise AssertionError("join side condition mismatch")
    expected_shrink = {
        "parent_contained_in_common": b3v.has(common, parent),
        "parent_basis_in_common_coordinates": [b3v.coord(row, common) for row in parent],
    }
    if side["shrink"] != expected_shrink or not expected_shrink["parent_contained_in_common"]:
        raise AssertionError("shrink side condition mismatch")
    return {
        "child_boundaries": child_boundaries,
        "common": common,
        "parent": parent,
        "partition_digest": partition_digest,
    }


def verify_leaves(
    manifest: dict,
    ambient: int,
    blocks: Sequence[Sequence[int]],
    node_context: dict,
) -> list[dict]:
    leaves = manifest["child_full_sets"]
    if [leaf["factor_id"] for leaf in leaves] != [0, 4]:
        raise AssertionError("leaf order mismatch")
    for leaf in leaves:
        factor = leaf["factor_id"]
        child_boundary = node_context["child_boundaries"][factor]
        if leaf["factor_block_rref"] != list(blocks[factor]):
            raise AssertionError("leaf factor block mismatch")
        if leaf["affine_offset"] != manifest["scaffold_case"]["affine_offsets"][factor]:
            raise AssertionError("leaf affine offset mismatch")
        if leaf["boundary_rref_ambient"] != list(child_boundary):
            raise AssertionError("leaf ambient boundary mismatch")
        if leaf["boundary_coordinate_dimension"] != 1:
            raise AssertionError("leaf coordinate dimension mismatch")
        if leaf["boundary_coordinate_rref"] != [1]:
            raise AssertionError("leaf coordinate RREF mismatch")
        expected_generator = [
            {"left": [], "right": [1], "value": 0},
            {"left": [1], "right": [], "value": 0},
        ]
        if leaf["leaf_generator_coordinates"] != expected_generator:
            raise AssertionError("leaf coordinate generator mismatch")
        if leaf["leaf_generator_ambient"] != lift_raw(
            expected_generator, child_boundary, ambient
        ):
            raise AssertionError("leaf ambient generator mismatch")
        if leaf["provenance"] != {
            "kind": "WHOLE_FACTOR_LEAF",
            "factor_id": factor,
            "generator_source": "canonical nonzero-boundary one-factor trajectory",
            "supplied_layout_used_for_discovery": False,
        }:
            raise AssertionError("leaf provenance mismatch")
        verify_b2_closure(leaf["full_set"], (12768, 11853))
        if leaf["full_set"]["entry_count"] != 36:
            raise AssertionError("leaf full-set cardinality mismatch")
    return leaves


def verify_pair_semantics(
    pair: dict,
    leaves: Sequence[dict],
    ambient: int,
    node_context: dict,
) -> tuple[tuple[b3v.S, ...], tuple[b3v.S, ...], dict]:
    pair_id = int(pair["pair_id"])
    expected_left_index = pair_id // 36
    expected_right_index = pair_id % 36
    if pair["left_entry_index"] != expected_left_index:
        raise AssertionError("left child index mismatch")
    if pair["right_entry_index"] != expected_right_index:
        raise AssertionError("right child index mismatch")
    left_entry = leaves[0]["full_set"]["entries"][expected_left_index]
    right_entry = leaves[1]["full_set"]["entries"][expected_right_index]
    if pair["left_input_coordinates"] != left_entry["trajectory"]:
        raise AssertionError("left child full-set provenance mismatch")
    if pair["right_input_coordinates"] != right_entry["trajectory"]:
        raise AssertionError("right child full-set provenance mismatch")
    left_boundary = node_context["child_boundaries"][0]
    right_boundary = node_context["child_boundaries"][4]
    common = node_context["common"]
    left_raw = lift_raw(left_entry["trajectory"], left_boundary, ambient)
    right_raw = lift_raw(right_entry["trajectory"], right_boundary, ambient)
    if pair["left_input_ambient"] != left_raw:
        raise AssertionError("left coordinate lift mismatch")
    if pair["right_input_ambient"] != right_raw:
        raise AssertionError("right coordinate lift mismatch")
    left = b3v.parse(left_raw, left_boundary, ambient, True)
    right = b3v.parse(right_raw, right_boundary, ambient, True)
    expected_left_transport = expected_transport(left_boundary, common, ambient)
    expected_right_transport = expected_transport(right_boundary, common, ambient)
    if pair["left_expand"] != {
        "output_ambient": b3v.encg(left),
        "transport": expected_left_transport,
    }:
        raise AssertionError("left expand/RREF transport mismatch")
    if pair["right_expand"] != {
        "output_ambient": b3v.encg(right),
        "transport": expected_right_transport,
    }:
        raise AssertionError("right expand/RREF transport mismatch")
    expected_stages = {
        "partition_receipt_digest": node_context["partition_digest"],
        "left_expand_factor_ids": [0],
        "right_expand_factor_ids": [4],
        "join_factor_ids": [0, 4],
        "shrink_factor_ids": [0, 4],
        "outside_factor_ids": [2, 3, 1, 5],
    }
    if pair["grouped_partition_stages"] != expected_stages:
        raise AssertionError("grouped partition stage receipt mismatch")
    breakdown = {
        "pair_enumerations": 1,
        "expanded_statistics": len(left) + len(right),
        "boundary_coordinate_changes": 2,
    }
    if pair["expand_work_breakdown"] != dict(sorted(breakdown.items())):
        raise AssertionError("pair expand work mismatch")
    expected_paths = len(b3v.paths(len(left), len(right)))
    if pair["lattice_path_count"] != expected_paths:
        raise AssertionError("pair lattice-path count mismatch")
    if pair["last_attempt_id"] - pair["first_attempt_id"] + 1 != expected_paths:
        raise AssertionError("pair attempt range mismatch")
    return left, right, breakdown


def verify_refinement_semantics(
    attempt: dict,
    pair: dict,
    left: Sequence[b3v.S],
    right: Sequence[b3v.S],
    ambient: int,
    node_context: dict,
) -> tuple[dict, str | None]:
    if attempt["record_kind"] != "REFINEMENT":
        raise AssertionError("wrong refinement record kind")
    if attempt["pair_id"] != pair["pair_id"]:
        raise AssertionError("attempt attached to wrong pair")
    if attempt["left_entry_index"] != pair["left_entry_index"]:
        raise AssertionError("attempt left provenance mismatch")
    if attempt["right_entry_index"] != pair["right_entry_index"]:
        raise AssertionError("attempt right provenance mismatch")
    if attempt["partition_receipt_digest"] != node_context["partition_digest"]:
        raise AssertionError("attempt partition cross-reference mismatch")

    common = node_context["common"]
    parent = node_context["parent"]
    expected_join = b3v.join(
        left, right, attempt["lattice_path"], common, ambient
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
    compact_join, join_trace = independent_compactification(
        attempt["join"]["raw_join"], common, ambient
    )
    if compact_join != attempt["join"]["compact_join"]:
        raise AssertionError("join compact output mismatch")
    if join_trace != attempt["join"]["compactification_trace"]:
        raise AssertionError("join compactification transcript mismatch")

    joined = b3v.parse(compact_join, common, ambient, True)
    projected, expected_shrink = b3v.projected(joined, parent, ambient)
    for field in (
        "target_boundary",
        "projected_precompact",
        "projection_receipts",
        "output",
    ):
        if attempt["shrink"][field] != expected_shrink[field]:
            raise AssertionError(f"B3 shrink mismatch: {field}")
    compact_shrink, shrink_trace = independent_compactification(
        attempt["shrink"]["projected_precompact"], parent, ambient
    )
    if compact_shrink != attempt["shrink"]["output"]:
        raise AssertionError("shrink compact output mismatch")
    if shrink_trace != attempt["shrink"]["compactification_trace"]:
        raise AssertionError("shrink compactification transcript mismatch")
    if attempt["output_ambient"] != b3v.encg(projected):
        raise AssertionError("ambient refinement output mismatch")
    expected_coordinates = lower_raw(b3v.encg(projected), parent, ambient)
    if attempt["output_parent_coordinates"] != expected_coordinates:
        raise AssertionError("shrink coordinate projection mismatch")

    output_width = max(stat.v for stat in projected)
    if attempt["output_width"] != output_width:
        raise AssertionError("output width mismatch")
    expected_status = "SUCCESS" if output_width <= 1 else "FAILED_WIDTH_CAP"
    if attempt["status"] != expected_status:
        raise AssertionError("refinement status mismatch")
    expected_reason = (
        None
        if expected_status == "SUCCESS"
        else f"output width {output_width} exceeds k=1"
    )
    if attempt["failure_reason"] != expected_reason:
        raise AssertionError("failed-refinement reason mismatch")
    breakdown = expected_refinement_work(attempt["join"], attempt["shrink"])
    if attempt["work_breakdown"] != dict(sorted(breakdown.items())):
        raise AssertionError("refinement work mismatch")
    key = trajectory_key(expected_coordinates) if expected_status == "SUCCESS" else None
    return breakdown, key


def verify_full_transcript(root: Path, manifest: dict) -> dict:
    verify_manifest_integrity(manifest)
    ambient, blocks, order = verify_scaffold(manifest)
    node_context = verify_node(manifest, ambient, blocks, order)
    leaves = verify_leaves(manifest, ambient, blocks, node_context)

    pairs = list(ChunkReader(root, manifest, "PAIRS"))
    if len(pairs) != 1296:
        raise AssertionError("pair transcript incomplete")
    for pair_id, pair in enumerate(pairs):
        if pair["record_kind"] != "PAIR" or pair["pair_id"] != pair_id:
            raise AssertionError("pair record order mismatch")

    ledger = manifest["work_ledger"]
    cumulative = 0
    expected_child_events = []
    for leaf in leaves:
        leaf_ledger = leaf["full_set"]["ledger"]
        breakdown = {
            "b2_discovery_work": leaf_ledger["discovery_work"],
            "b2_work": leaf_ledger["work"],
        }
        cumulative += sum(breakdown.values())
        expected_child_events.append(
            {
                "factor_id": leaf["factor_id"],
                "breakdown": breakdown,
                "work_delta": sum(breakdown.values()),
                "cumulative_work": cumulative,
            }
        )
    if ledger["child_full_set_events"] != expected_child_events:
        raise AssertionError("child full-set work ledger mismatch")

    attempts = iter(ChunkReader(root, manifest, "REFINEMENTS"))
    successful_groups: dict[str, list[int]] = defaultdict(list)
    successful = 0
    failed = 0
    raw_precompact = 0
    expected_attempt_id = 0

    for pair in pairs:
        left, right, expand_breakdown = verify_pair_semantics(
            pair, leaves, ambient, node_context
        )
        cumulative += sum(expand_breakdown.values())
        if pair["cumulative_work_after_expand"] != cumulative:
            raise AssertionError("pair cumulative work reset/decrease")
        if pair["first_attempt_id"] != expected_attempt_id:
            raise AssertionError("pair attempt range not contiguous")
        claimed_paths = []
        for _ in range(pair["lattice_path_count"]):
            try:
                attempt = next(attempts)
            except StopIteration as exc:
                raise AssertionError("missing refinement record") from exc
            if attempt["attempt_id"] != expected_attempt_id:
                raise AssertionError("attempt IDs not contiguous")
            breakdown, successful_key = verify_refinement_semantics(
                attempt, pair, left, right, ambient, node_context
            )
            cumulative += sum(breakdown.values())
            if attempt["cumulative_work"] != cumulative:
                raise AssertionError("cumulative work mismatch or decrease")
            claimed_paths.append(tuple(tuple(cell) for cell in attempt["lattice_path"]))
            raw_precompact += attempt["join"]["raw_length"]
            if successful_key is None:
                failed += 1
            else:
                successful += 1
                successful_groups[successful_key].append(expected_attempt_id)
            expected_attempt_id += 1
        if pair["last_attempt_id"] != expected_attempt_id - 1:
            raise AssertionError("pair final attempt mismatch")
        expected_paths = b3v.paths(len(left), len(right))
        if tuple(sorted(claimed_paths)) != expected_paths:
            raise AssertionError("lattice-path coverage mismatch")
    try:
        next(attempts)
    except StopIteration:
        pass
    else:
        raise AssertionError("extra refinement record")
    if expected_attempt_id != 163824:
        raise AssertionError("refinement transcript count mismatch")

    generators = list(ChunkReader(root, manifest, "GENERATORS"))
    expected_generator_records = []
    expected_deletions = []
    for generator_index, key in enumerate(sorted(successful_groups)):
        trajectory_coordinates = json.loads(key)
        ids = successful_groups[key]
        expected_generator_records.append(
            {
                "record_kind": "SUCCESSFUL_GENERATOR",
                "generator_index": generator_index,
                "trajectory_parent_coordinates": trajectory_coordinates,
                "trajectory_ambient": lift_raw(
                    trajectory_coordinates, node_context["parent"], ambient
                ),
                "trajectory_digest": digest(trajectory_coordinates),
                "provenance_attempt_ids": ids,
                "canonical_retained_attempt_id": ids[0],
            }
        )
        identity_path = [[index, index] for index in range(len(trajectory_coordinates))]
        for removed_id in ids[1:]:
            expected_deletions.append(
                {
                    "record_kind": "DUPLICATE_DELETION",
                    "deletion_id": len(expected_deletions),
                    "generator_index": generator_index,
                    "trajectory_digest": digest(trajectory_coordinates),
                    "removed_attempt_id": removed_id,
                    "retained_attempt_id": ids[0],
                    "witness": {
                        "path": identity_path,
                        "path_length": len(identity_path),
                    },
                    "reason": "IDENTICAL_REFINEMENT_OUTPUT",
                }
            )
    if len(generators) != len(expected_generator_records):
        raise AssertionError("generator record count mismatch")
    for actual, expected in zip(generators, expected_generator_records):
        body = dict(actual)
        body.pop("record_digest", None)
        if body != expected:
            raise AssertionError("successful generator/provenance mismatch")

    deletions = iter(ChunkReader(root, manifest, "DELETIONS"))
    for expected in expected_deletions:
        try:
            actual = next(deletions)
        except StopIteration as exc:
            raise AssertionError("missing duplicate deletion witness") from exc
        body = dict(actual)
        body.pop("record_digest", None)
        if body != expected:
            raise AssertionError("duplicate deletion witness mismatch")
    try:
        next(deletions)
    except StopIteration:
        pass
    else:
        raise AssertionError("extra duplicate deletion witness")

    node_closure = manifest["node_up_k"]
    verify_b2_closure(node_closure, (12984, 3445804))
    generator_index_by_key = {
        trajectory_key(record["trajectory_parent_coordinates"]): record[
            "generator_index"
        ]
        for record in expected_generator_records
    }
    expected_input_provenance = [
        {
            "input_generator_index": index,
            "generator_record_index": generator_index_by_key[trajectory_key(raw)],
        }
        for index, raw in enumerate(node_closure["input_generators"])
    ]
    if manifest["input_generator_provenance"] != expected_input_provenance:
        raise AssertionError("B2 input provenance mismatch")
    expected_retained_provenance = [
        {
            "retained_generator_index": index,
            "generator_record_index": generator_index_by_key[trajectory_key(raw)],
        }
        for index, raw in enumerate(node_closure["retained_generators"])
    ]
    if manifest["retained_generator_provenance"] != expected_retained_provenance:
        raise AssertionError("B2 retained provenance mismatch")
    expected_entry_provenance = [
        {
            "entry_index": index,
            "source_generator_index": int(entry["source_generator_index"]),
            "generator_record_index": expected_retained_provenance[
                int(entry["source_generator_index"])
            ]["generator_record_index"],
        }
        for index, entry in enumerate(node_closure["entries"])
    ]
    if manifest["entry_provenance"] != expected_entry_provenance:
        raise AssertionError("B2 entry provenance mismatch")

    if ledger["cumulative_work_before_node_b2"] != cumulative:
        raise AssertionError("pre-B2 cumulative work mismatch")
    expected_node_b2 = {
        "b2_discovery_work": node_closure["ledger"]["discovery_work"],
        "b2_work": node_closure["ledger"]["work"],
    }
    if ledger["node_b2_breakdown"] != expected_node_b2:
        raise AssertionError("node B2 work breakdown mismatch")
    if ledger["node_b2_work_delta"] != sum(expected_node_b2.values()):
        raise AssertionError("node B2 work delta mismatch")
    cumulative += sum(expected_node_b2.values())
    if ledger["cumulative_work_final"] != cumulative:
        raise AssertionError("final cumulative work mismatch")
    if ledger["monotone_by_construction"] is not True:
        raise AssertionError("work monotonicity claim missing")

    audit = manifest["audit"]
    expected_audit = {
        "child_full_set_entries": [36, 36],
        "child_pairs_processed": 1296,
        "lattice_paths_processed": expected_attempt_id,
        "successful_refinements": successful,
        "failed_refinements": failed,
        "raw_precompact_join_statistics": raw_precompact,
        "unique_successful_generators": len(expected_generator_records),
        "duplicate_successful_outputs_deleted": len(expected_deletions),
        "b2_dominance_deletions": len(node_closure["removals"]),
        "retained_generators": len(node_closure["retained_generators"]),
        "final_up_k_entries": node_closure["entry_count"],
        "cumulative_work": cumulative,
        "chunk_count": manifest["chunking"]["chunk_count"],
        "failures": 0,
    }
    if audit != expected_audit:
        raise AssertionError("audit mismatch")
    frozen_audit = {
        "child_full_set_entries": [36, 36],
        "child_pairs_processed": 1296,
        "lattice_paths_processed": 163824,
        "successful_refinements": 12073,
        "failed_refinements": 151751,
        "raw_precompact_join_statistics": 1297408,
        "unique_successful_generators": 252,
        "duplicate_successful_outputs_deleted": 11821,
        "b2_dominance_deletions": 250,
        "retained_generators": 2,
        "final_up_k_entries": 252,
        "cumulative_work": 7941294,
        "chunk_count": 59,
        "failures": 0,
    }
    if audit != frozen_audit:
        raise AssertionError("frozen audit constants drift")
    if manifest["chunking"]["uncompressed_chunk_bytes"] != 960692616:
        raise AssertionError("uncompressed certificate volume drift")
    if manifest["chunking"]["compressed_chunk_bytes"] != 21008111:
        raise AssertionError("compressed certificate volume drift")

    strict = manifest["strict_boundary"]
    if strict != {
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
    }:
        raise AssertionError("strict boundary drift")
    return {
        "pairs": len(pairs),
        "refinements": expected_attempt_id,
        "successful": successful,
        "failed": failed,
        "generators": len(expected_generator_records),
        "deletions": len(expected_deletions),
        "final_entries": node_closure["entry_count"],
        "cumulative_work": cumulative,
    }


def rebind_record(record: dict) -> None:
    record.pop("record_digest", None)
    record["record_digest"] = digest(record)


def rebind_chunk(payload: dict) -> tuple[bytes, bytes]:
    payload.pop("chunk_payload_digest", None)
    payload["chunk_payload_digest"] = digest(payload)
    raw = canonical_json(payload) + b"\n"
    return raw, deterministic_gzip(raw)


def rebind_manifest(manifest: dict) -> None:
    manifest["chunking"]["transcript_root_digest"] = digest(
        manifest["chunking"]["chunk_groups"]
    )
    manifest.pop("manifest_digest", None)
    manifest["manifest_digest"] = digest(manifest)


def transport_tamper_self_test(root: Path, manifest: dict) -> None:
    tampered_manifest = copy.deepcopy(manifest)
    metadata = tampered_manifest["chunking"]["chunk_groups"]["PAIRS"]
    first_meta = metadata[0]
    original_compressed = safe_chunk_path(root, first_meta["filename"]).read_bytes()
    payload = parse_and_verify_chunk(first_meta, original_compressed)
    pair = payload["records"][0]
    pair["left_expand"]["transport"][
        "child_basis_in_parent_coordinates"
    ] = [1]
    rebind_record(pair)
    raw, repaired_compressed = rebind_chunk(payload)

    old_uncompressed = first_meta["uncompressed_bytes"]
    old_compressed = first_meta["compressed_bytes"]
    first_meta["uncompressed_bytes"] = len(raw)
    first_meta["compressed_bytes"] = len(repaired_compressed)
    first_meta["chunk_payload_digest"] = payload["chunk_payload_digest"]
    first_meta["compressed_sha256"] = sha256_bytes(repaired_compressed)
    if len(metadata) > 1:
        first_meta["next_chunk_digest"] = metadata[1]["compressed_sha256"]
        metadata[1]["previous_chunk_digest"] = first_meta["compressed_sha256"]
    tampered_manifest["chunking"]["uncompressed_chunk_bytes"] += (
        len(raw) - old_uncompressed
    )
    tampered_manifest["chunking"]["compressed_chunk_bytes"] += (
        len(repaired_compressed) - old_compressed
    )
    rebind_manifest(tampered_manifest)
    verify_manifest_integrity(tampered_manifest)
    parse_and_verify_chunk(first_meta, repaired_compressed)

    ambient, blocks, order = verify_scaffold(tampered_manifest)
    node_context = verify_node(tampered_manifest, ambient, blocks, order)
    leaves = verify_leaves(tampered_manifest, ambient, blocks, node_context)
    try:
        verify_pair_semantics(pair, leaves, ambient, node_context)
    except AssertionError:
        return
    raise AssertionError("digest-repaired transport-matrix tamper accepted")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("transcript_dir")
    parser.add_argument("--tamper-self-test", action="store_true")
    args = parser.parse_args()
    root = Path(args.transcript_dir)
    with (root / "manifest.json").open(encoding="utf-8") as handle:
        manifest = json.load(handle)
    result = verify_full_transcript(root, manifest)
    if args.tamper_self_test:
        transport_tamper_self_test(root, manifest)
    print("VERIFIED C049.1 B4.4 NONZERO-BOUNDARY INTERNAL NODE FULL SET")
    print("PAIRS_REPLAYED =", result["pairs"])
    print("B3_REFINEMENTS_REPLAYED =", result["refinements"])
    print("FAILED_REFINEMENTS_REPLAYED =", result["failed"])
    print("B2_FULL_SET_ENTRIES_REPLAYED =", result["final_entries"])
    print("CUMULATIVE_WORK =", result["cumulative_work"])
    print("TRANSPORT_TAMPER_CONTROLS =", 1 if args.tamper_self_test else 0)
    print("TERMINAL =", TERMINAL)


if __name__ == "__main__":
    main()
