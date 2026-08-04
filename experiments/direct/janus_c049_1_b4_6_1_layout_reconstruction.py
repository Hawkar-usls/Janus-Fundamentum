#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence

import janus_c049_1_b4_5_bottom_up_scaffold_executor as b45
from janus_c049_1_b4_2_3k_scaffold import boundary


SCHEMA = "C049.1-B4.6.1-LAYOUT-RECONSTRUCTION-v1"
TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"
LOCAL_RESULT = "LAYOUT_WITNESS_RECONSTRUCTED"


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def read_chunk(root: Path, metadata: dict) -> dict:
    path = root / metadata["filename"]
    raw = gzip.decompress(path.read_bytes())
    payload = json.loads(raw)
    if payload["kind"] != metadata["kind"]:
        raise AssertionError("chunk kind mismatch")
    if payload["chunk_index"] != metadata["chunk_index"]:
        raise AssertionError("chunk index mismatch")
    if payload["record_count"] != metadata["record_count"]:
        raise AssertionError("chunk record count mismatch")
    return payload


def record_by_id(
    root: Path,
    manifest: dict,
    kind: str,
    identifier: str,
    record_id: int,
) -> dict:
    metadata = manifest["chunking"]["chunk_groups"][kind]
    for item in metadata:
        if item["first_record_id"] <= record_id <= item["last_record_id"]:
            payload = read_chunk(root, item)
            offset = record_id - item["first_record_id"]
            record = payload["records"][offset]
            if record[identifier] != record_id:
                raise AssertionError("chunk record identifier mismatch")
            return record
    raise KeyError(f"missing {kind} record {record_id}")


def all_records(root: Path, manifest: dict, kind: str) -> list[dict]:
    out: list[dict] = []
    for item in manifest["chunking"]["chunk_groups"][kind]:
        out.extend(read_chunk(root, item)["records"])
    return out


def verify_b2_path(lower: Sequence[dict], upper: Sequence[dict], witness: dict) -> None:
    path = witness.get("path")
    if not isinstance(path, list) or not path:
        raise AssertionError("missing B2 extension path")
    parsed: list[tuple[int, int]] = []
    for cell in path:
        if not isinstance(cell, list) or len(cell) != 2:
            raise AssertionError("malformed B2 extension cell")
        i, j = cell
        if not isinstance(i, int) or not isinstance(j, int):
            raise AssertionError("noninteger B2 extension cell")
        if not (0 <= i < len(lower) and 0 <= j < len(upper)):
            raise AssertionError("B2 extension cell outside trajectory")
        parsed.append((i, j))
    if parsed[0] != (0, 0) or parsed[-1] != (len(lower) - 1, len(upper) - 1):
        raise AssertionError("B2 extension endpoints mismatch")
    for (i, j), (i2, j2) in zip(parsed, parsed[1:]):
        if (i2 - i, j2 - j) not in ((1, 0), (0, 1), (1, 1)):
            raise AssertionError("illegal B2 extension step")
    for i, j in parsed:
        a, b = lower[i], upper[j]
        if a["left"] != b["left"] or a["right"] != b["right"]:
            raise AssertionError("B2 extension subspace mismatch")
        if int(a["value"]) > int(b["value"]):
            raise AssertionError("B2 extension lambda mismatch")
    if witness.get("path_length") != len(parsed):
        raise AssertionError("B2 extension path length mismatch")


def trajectory_width(raw: Sequence[dict]) -> int:
    if not raw:
        raise AssertionError("empty trajectory")
    return max(int(item["value"]) for item in raw)


def accepting_root_entry_indices(root_node: dict, k: int) -> list[int]:
    accepted = []
    for index, entry in enumerate(root_node["node_up_k"]["entries"]):
        raw = entry["trajectory"]
        if trajectory_width(raw) > k:
            continue
        if any(item["left"] or item["right"] for item in raw):
            continue
        accepted.append(index)
    return accepted


def selected_entry_index(root_node: dict, k: int) -> int:
    accepted = accepting_root_entry_indices(root_node, k)
    if not accepted:
        raise AssertionError("root full set has no accepting empty-boundary entry")
    return min(
        accepted,
        key=lambda index: (digest(root_node["node_up_k"]["entries"][index]), index),
    )


def exact_cut_widths(scaffold: dict, order: Sequence[int]) -> list[dict]:
    ambient = int(scaffold["d"])
    blocks = [tuple(int(row) for row in block) for block in scaffold["whole_factor_blocks"]]
    if sorted(order) != list(range(len(blocks))):
        raise AssertionError("reconstructed order is not a whole-factor permutation")
    cuts = []
    for cut in range(len(order) + 1):
        left_ids = list(order[:cut])
        right_ids = list(order[cut:])
        basis = boundary(
            [blocks[index] for index in left_ids],
            [blocks[index] for index in right_ids],
            ambient,
        )
        cuts.append(
            {
                "cut": cut,
                "left_factor_ids": left_ids,
                "right_factor_ids": right_ids,
                "boundary_rref": list(basis),
                "width": len(basis),
            }
        )
    return cuts


class WorkLedger:
    def __init__(self, start: int) -> None:
        self.total = int(start)
        self.events: list[dict] = []

    def charge(self, kind: str, amount: int = 1, **context: Any) -> None:
        if amount < 0:
            raise ValueError("negative reconstruction charge")
        self.total += amount
        self.events.append(
            {
                "event_index": len(self.events),
                "kind": kind,
                "amount": amount,
                "cumulative_work": self.total,
                **context,
            }
        )


def trace_entry(
    node_id: int,
    entry_index: int,
    manifest: dict,
    transcript_root: Path,
    leaves: dict[int, dict],
    nodes: dict[int, dict],
    generators: dict[int, dict],
    ledger: WorkLedger,
    active: set[tuple[int, int]],
) -> dict:
    key = (node_id, entry_index)
    if key in active:
        raise AssertionError("cyclic reconstruction ancestry")
    active.add(key)
    ledger.charge("ENTRY_LOOKUP", node_id=node_id, entry_index=entry_index)

    if node_id in leaves:
        leaf = leaves[node_id]
        closure = leaf["full_set"]
        if not 0 <= entry_index < len(closure["entries"]):
            raise AssertionError("leaf entry index outside full set")
        entry = closure["entries"][entry_index]
        source_index = int(entry["source_generator_index"])
        source = closure["retained_generators"][source_index]
        verify_b2_path(source, entry["trajectory"], entry["witness"])
        ledger.charge(
            "B2_EXTENSION_PATH_VERTICES",
            int(entry["witness"]["path_length"]),
            node_id=node_id,
            entry_index=entry_index,
        )
        receipt = {
            "kind": "WHOLE_FACTOR_LEAF",
            "node_id": node_id,
            "factor_id": int(leaf["factor_id"]),
            "entry_index": entry_index,
            "entry_digest": digest(entry),
            "source_generator_index": source_index,
            "source_generator_digest": digest(source),
            "b2_extension_witness": entry["witness"],
            "factor_block_rref": leaf["factor_block_rref"],
            "affine_offset": int(leaf["affine_offset"]),
            "order": [int(leaf["factor_id"])],
        }
        receipt["receipt_digest"] = digest(receipt)
        active.remove(key)
        return receipt

    if node_id not in nodes:
        raise AssertionError("unknown reconstruction node")
    node = nodes[node_id]
    entries = node["node_up_k"]["entries"]
    if not 0 <= entry_index < len(entries):
        raise AssertionError("internal entry index outside full set")
    entry = entries[entry_index]
    source_index = int(entry["source_generator_index"])
    source = node["node_up_k"]["retained_generators"][source_index]
    verify_b2_path(source, entry["trajectory"], entry["witness"])
    ledger.charge(
        "B2_EXTENSION_PATH_VERTICES",
        int(entry["witness"]["path_length"]),
        node_id=node_id,
        entry_index=entry_index,
    )

    provenance = node["entry_provenance"][entry_index]
    if int(provenance["source_generator_index"]) != source_index:
        raise AssertionError("entry/source generator provenance mismatch")
    generator_id = int(provenance["generator_id"])
    generator = generators[generator_id]
    ledger.charge("GENERATOR_PROVENANCE_LOOKUP", node_id=node_id, generator_id=generator_id)
    if int(generator["node_id"]) != node_id:
        raise AssertionError("generator belongs to another node")
    if generator["trajectory_parent_coordinates"] != source:
        raise AssertionError("retained generator trajectory mismatch")

    attempt_id = int(generator["canonical_retained_attempt_id"])
    attempt = record_by_id(
        transcript_root, manifest, "REFINEMENTS", "attempt_id", attempt_id
    )
    ledger.charge("REFINEMENT_PROVENANCE_LOOKUP", node_id=node_id, attempt_id=attempt_id)
    if attempt["status"] != "SUCCESS" or int(attempt["node_id"]) != node_id:
        raise AssertionError("canonical reconstruction attempt is not successful")
    if attempt["output_parent_coordinates"] != source:
        raise AssertionError("successful attempt output/generator mismatch")
    if int(attempt["output_width"]) > int(manifest["scaffold_case"]["k"]):
        raise AssertionError("canonical reconstruction attempt exceeds k")

    pair_id = int(attempt["pair_id"])
    pair = record_by_id(transcript_root, manifest, "PAIRS", "pair_id", pair_id)
    ledger.charge("PAIR_PROVENANCE_LOOKUP", node_id=node_id, pair_id=pair_id)
    if int(pair["node_id"]) != node_id:
        raise AssertionError("pair belongs to another node")
    if int(pair["left_entry_index"]) != int(attempt["left_entry_index"]):
        raise AssertionError("left child entry provenance mismatch")
    if int(pair["right_entry_index"]) != int(attempt["right_entry_index"]):
        raise AssertionError("right child entry provenance mismatch")

    left_child, right_child = [int(value) for value in node["child_node_ids"]]
    left = trace_entry(
        left_child,
        int(pair["left_entry_index"]),
        manifest,
        transcript_root,
        leaves,
        nodes,
        generators,
        ledger,
        active,
    )
    right = trace_entry(
        right_child,
        int(pair["right_entry_index"]),
        manifest,
        transcript_root,
        leaves,
        nodes,
        generators,
        ledger,
        active,
    )
    order = list(left["order"]) + list(right["order"])
    ledger.charge("RECONSTRUCTION_BRANCH_COMBINE", node_id=node_id, amount=len(order))
    receipt = {
        "kind": "INTERNAL_RECONSTRUCTION",
        "node_id": node_id,
        "entry_index": entry_index,
        "entry_digest": digest(entry),
        "source_generator_index": source_index,
        "source_generator_digest": digest(source),
        "b2_extension_witness": entry["witness"],
        "generator_id": generator_id,
        "generator_digest": digest(generator),
        "canonical_attempt_id": attempt_id,
        "attempt_digest": digest(attempt),
        "pair_id": pair_id,
        "pair_digest": digest(pair),
        "lattice_path_digest": digest(attempt["lattice_path"]),
        "child_node_ids": [left_child, right_child],
        "left_receipt": left,
        "right_receipt": right,
        "order": order,
    }
    receipt["receipt_digest"] = digest(receipt)
    active.remove(key)
    return receipt


def bind_artifact(artifact: dict) -> dict:
    artifact = copy.deepcopy(artifact)
    artifact["manifest_digest"] = "0" * 64
    artifact["certificate_accounting"]["fixed_point_serialized_bytes"] = 0
    for _ in range(32):
        body = copy.deepcopy(artifact)
        body.pop("manifest_digest", None)
        artifact["manifest_digest"] = digest(body)
        size = len(canonical_json(artifact)) + 1
        if size == artifact["certificate_accounting"]["fixed_point_serialized_bytes"]:
            return artifact
        artifact["certificate_accounting"]["fixed_point_serialized_bytes"] = size
    raise AssertionError("certificate byte fixed point did not converge")


def build(output_dir: Path) -> dict:
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError("output directory must be empty")
    output_dir.mkdir(parents=True, exist_ok=True)
    transcript_root = output_dir / "b45"
    b45_manifest = b45.build(transcript_root)
    if b45_manifest["execution"]["status"] != "ROOT_FULL_SET_COMPUTED":
        raise AssertionError("B4.5 did not produce a root full set")

    leaves = {int(item["node_id"]): item for item in b45_manifest["leaf_full_sets"]}
    nodes = {int(item["node_id"]): item for item in b45_manifest["node_results"]}
    generators = {
        int(item["generator_id"]): item
        for item in all_records(transcript_root, b45_manifest, "GENERATORS")
    }
    root_node_id = int(b45_manifest["execution"]["root_node_id"])
    root_node = nodes[root_node_id]
    k = int(b45_manifest["scaffold_case"]["k"])
    root_entry_index = selected_entry_index(root_node, k)

    ledger = WorkLedger(int(b45_manifest["audit"]["cumulative_work"]))
    accepted_count = len(accepting_root_entry_indices(root_node, k))
    ledger.charge("ROOT_ACCEPTANCE_TESTS", accepted_count, node_id=root_node_id)
    reconstruction = trace_entry(
        root_node_id,
        root_entry_index,
        b45_manifest,
        transcript_root,
        leaves,
        nodes,
        generators,
        ledger,
        set(),
    )
    order = [int(value) for value in reconstruction["order"]]
    cuts = exact_cut_widths(b45_manifest["scaffold_case"], order)
    ledger.charge("EXACT_LAYOUT_CUT_RECOMPUTATIONS", len(cuts), order=order)
    maximum_width = max(item["width"] for item in cuts)
    if maximum_width > k:
        raise AssertionError("reconstructed layout exceeds k")

    blocks = b45_manifest["scaffold_case"]["whole_factor_blocks"]
    offsets = b45_manifest["scaffold_case"]["affine_offsets"]
    layout = [
        {
            "position": position,
            "factor_id": factor_id,
            "normal_space_block_rref": blocks[factor_id],
            "affine_offset": offsets[factor_id],
        }
        for position, factor_id in enumerate(order)
    ]
    artifact = {
        "schema": SCHEMA,
        "phase": "B4.6.1_ROOT_TRAJECTORY_LAYOUT_RECONSTRUCTION",
        "source": {
            "b45_manifest_digest": b45_manifest["manifest_digest"],
            "b45_transcript_root_digest": b45_manifest["chunking"]["transcript_root_digest"],
            "b45_root_full_set_receipt": b45_manifest["execution"]["root_full_set_receipt"],
            "supplied_scaffold_used_for_discovery": False,
            "supplied_full_set_used_for_discovery": False,
            "supplied_layout_used_for_discovery": False,
        },
        "selection": {
            "root_node_id": root_node_id,
            "accepting_root_entry_count": accepted_count,
            "selected_root_entry_index": root_entry_index,
            "rule": "MINIMUM_SHA256_THEN_ENTRY_INDEX_AMONG_EMPTY_BOUNDARY_WIDTH_AT_MOST_K",
        },
        "reconstruction_receipt": reconstruction,
        "reconstructed_layout": layout,
        "reconstructed_factor_order": order,
        "exact_cut_transcript": cuts,
        "exact_maximum_width": maximum_width,
        "k": k,
        "result": LOCAL_RESULT,
        "work_ledger": {
            "cumulative_work_before_reconstruction": int(
                b45_manifest["audit"]["cumulative_work"]
            ),
            "events": ledger.events,
            "reconstruction_work": ledger.total
            - int(b45_manifest["audit"]["cumulative_work"]),
            "cumulative_work_after_reconstruction": ledger.total,
            "monotone": True,
        },
        "certificate_accounting": {
            "fixed_point_serialized_bytes": 0,
            "b45_uncompressed_chunk_bytes": b45_manifest["chunking"][
                "uncompressed_chunk_bytes"
            ],
            "b45_compressed_chunk_bytes": b45_manifest["chunking"][
                "compressed_chunk_bytes"
            ],
        },
        "strict_boundary": {
            "scope": "one accepting root entry of the frozen B4.5 scaffold",
            "root_ancestry_replayed": True,
            "whole_factor_partition_preserved": True,
            "affine_offsets_preserved": True,
            "exact_width_at_most_k_verified": True,
            "all_iterative_compression_rounds_executed": False,
            "terminal_completeness_proved": False,
            "found_layout_enabled": False,
            "no_layout_at_cap_enabled": False,
            "current_global_terminal": TERMINAL,
            "next_gate": "C049.1_B4.6.2_FULL_ITERATIVE_COMPRESSION_CYCLE",
            "p_vs_np": "OPEN",
        },
    }
    artifact = bind_artifact(artifact)
    (output_dir / "artifact.json").write_bytes(canonical_json(artifact) + b"\n")
    print("JANUS_C049_1_B4_6_1_LAYOUT_RECONSTRUCTION = PASS")
    print("LOCAL_RESULT =", LOCAL_RESULT)
    print("ROOT_ENTRY_INDEX =", root_entry_index)
    print("RECONSTRUCTED_ORDER =", order)
    print("EXACT_MAXIMUM_WIDTH =", maximum_width)
    print("RECONSTRUCTION_WORK =", artifact["work_ledger"]["reconstruction_work"])
    print("CUMULATIVE_WORK =", artifact["work_ledger"]["cumulative_work_after_reconstruction"])
    print("CERTIFICATE_BYTES =", artifact["certificate_accounting"]["fixed_point_serialized_bytes"])
    print("MANIFEST_DIGEST =", artifact["manifest_digest"])
    print("GLOBAL_TERMINAL =", TERMINAL)
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    build(Path(args.output_dir))


if __name__ == "__main__":
    main()
