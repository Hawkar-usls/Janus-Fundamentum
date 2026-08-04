#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence

import janus_c049_1_b3_expand_join_shrink_verifier as b3v
import janus_c049_1_b4_5_bottom_up_scaffold_executor_verifier as b45v


SCHEMA = "C049.1-B4.6.1-LAYOUT-RECONSTRUCTION-v1"
TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"
LOCAL_RESULT = "LAYOUT_WITNESS_RECONSTRUCTED"


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def record_body(record: dict) -> dict:
    body = dict(record)
    body.pop("record_digest", None)
    return body


def verify_artifact_integrity(artifact: dict) -> None:
    if artifact.get("schema") != SCHEMA:
        raise AssertionError("B4.6.1 schema mismatch")
    claimed = artifact.get("manifest_digest")
    body = copy.deepcopy(artifact)
    body.pop("manifest_digest", None)
    if claimed != digest(body):
        raise AssertionError("B4.6.1 manifest digest mismatch")
    expected_bytes = len(canonical_json(artifact)) + 1
    if artifact["certificate_accounting"]["fixed_point_serialized_bytes"] != expected_bytes:
        raise AssertionError("B4.6.1 fixed-point byte count mismatch")


def read_chunk(root: Path, metadata: dict) -> dict:
    raw = gzip.decompress((root / metadata["filename"]).read_bytes())
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
    for metadata in manifest["chunking"]["chunk_groups"][kind]:
        if metadata["first_record_id"] <= record_id <= metadata["last_record_id"]:
            records = read_chunk(root, metadata)["records"]
            record = records[record_id - metadata["first_record_id"]]
            if record[identifier] != record_id:
                raise AssertionError("record identifier mismatch")
            return record
    raise AssertionError(f"missing {kind} record {record_id}")


def all_generators(root: Path, manifest: dict) -> dict[int, dict]:
    out: dict[int, dict] = {}
    for metadata in manifest["chunking"]["chunk_groups"]["GENERATORS"]:
        for record in read_chunk(root, metadata)["records"]:
            generator_id = int(record["generator_id"])
            if generator_id in out:
                raise AssertionError("duplicate generator id")
            out[generator_id] = record
    return out


def verify_b2_path(lower: Sequence[dict], upper: Sequence[dict], witness: dict) -> None:
    path = witness.get("path")
    if not isinstance(path, list) or not path:
        raise AssertionError("missing B2 witness path")
    parsed: list[tuple[int, int]] = []
    for cell in path:
        if not isinstance(cell, list) or len(cell) != 2:
            raise AssertionError("malformed B2 witness cell")
        i, j = cell
        if not isinstance(i, int) or not isinstance(j, int):
            raise AssertionError("noninteger B2 witness cell")
        if not (0 <= i < len(lower) and 0 <= j < len(upper)):
            raise AssertionError("B2 witness cell outside trajectory")
        parsed.append((i, j))
    if parsed[0] != (0, 0) or parsed[-1] != (len(lower) - 1, len(upper) - 1):
        raise AssertionError("B2 witness endpoints mismatch")
    for first, second in zip(parsed, parsed[1:]):
        step = (second[0] - first[0], second[1] - first[1])
        if step not in ((1, 0), (0, 1), (1, 1)):
            raise AssertionError("illegal B2 witness step")
    for i, j in parsed:
        a, b = lower[i], upper[j]
        if a["left"] != b["left"] or a["right"] != b["right"]:
            raise AssertionError("B2 witness subspace mismatch")
        if int(a["value"]) > int(b["value"]):
            raise AssertionError("B2 witness lambda mismatch")
    if witness.get("path_length") != len(parsed):
        raise AssertionError("B2 witness path length mismatch")


def trajectory_width(raw: Sequence[dict]) -> int:
    if not raw:
        raise AssertionError("empty trajectory")
    return max(int(item["value"]) for item in raw)


def accepting_indices(root_node: dict, k: int) -> list[int]:
    accepted = []
    for index, entry in enumerate(root_node["node_up_k"]["entries"]):
        trajectory = entry["trajectory"]
        if trajectory_width(trajectory) <= k and not any(
            item["left"] or item["right"] for item in trajectory
        ):
            accepted.append(index)
    return accepted


def deterministic_root_index(root_node: dict, k: int) -> int:
    accepted = accepting_indices(root_node, k)
    if not accepted:
        raise AssertionError("no accepting root entry")
    return min(
        accepted,
        key=lambda index: (digest(root_node["node_up_k"]["entries"][index]), index),
    )


class ReplayLedger:
    def __init__(self, start: int) -> None:
        self.total = int(start)
        self.events: list[dict] = []

    def charge(self, kind: str, amount: int = 1, **context: Any) -> None:
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


def replay_entry(
    node_id: int,
    entry_index: int,
    b45_manifest: dict,
    b45_root: Path,
    leaves: dict[int, dict],
    nodes: dict[int, dict],
    generators: dict[int, dict],
    ledger: ReplayLedger,
    active: set[tuple[int, int]],
) -> dict:
    key = (node_id, entry_index)
    if key in active:
        raise AssertionError("cyclic ancestry")
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
        expected = {
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
        expected["receipt_digest"] = digest(expected)
        active.remove(key)
        return expected

    node = nodes.get(node_id)
    if node is None:
        raise AssertionError("unknown internal node")
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
        raise AssertionError("entry provenance source mismatch")
    generator_id = int(provenance["generator_id"])
    generator = generators[generator_id]
    ledger.charge("GENERATOR_PROVENANCE_LOOKUP", node_id=node_id, generator_id=generator_id)
    if int(generator["node_id"]) != node_id:
        raise AssertionError("generator node mismatch")
    if generator["trajectory_parent_coordinates"] != source:
        raise AssertionError("generator/source trajectory mismatch")

    attempt_id = int(generator["canonical_retained_attempt_id"])
    attempt = record_by_id(b45_root, b45_manifest, "REFINEMENTS", "attempt_id", attempt_id)
    ledger.charge("REFINEMENT_PROVENANCE_LOOKUP", node_id=node_id, attempt_id=attempt_id)
    if attempt["status"] != "SUCCESS" or int(attempt["node_id"]) != node_id:
        raise AssertionError("reconstruction attempt is not successful")
    if attempt["output_parent_coordinates"] != source:
        raise AssertionError("attempt output/source trajectory mismatch")
    if int(attempt["output_width"]) > int(b45_manifest["scaffold_case"]["k"]):
        raise AssertionError("reconstruction attempt exceeds k")

    pair_id = int(attempt["pair_id"])
    pair = record_by_id(b45_root, b45_manifest, "PAIRS", "pair_id", pair_id)
    ledger.charge("PAIR_PROVENANCE_LOOKUP", node_id=node_id, pair_id=pair_id)
    if int(pair["node_id"]) != node_id:
        raise AssertionError("pair node mismatch")
    for side in ("left", "right"):
        if int(pair[f"{side}_entry_index"]) != int(attempt[f"{side}_entry_index"]):
            raise AssertionError(f"{side} child provenance mismatch")

    left_node, right_node = [int(value) for value in node["child_node_ids"]]
    left = replay_entry(
        left_node,
        int(pair["left_entry_index"]),
        b45_manifest,
        b45_root,
        leaves,
        nodes,
        generators,
        ledger,
        active,
    )
    right = replay_entry(
        right_node,
        int(pair["right_entry_index"]),
        b45_manifest,
        b45_root,
        leaves,
        nodes,
        generators,
        ledger,
        active,
    )
    order = list(left["order"]) + list(right["order"])
    ledger.charge("RECONSTRUCTION_BRANCH_COMBINE", len(order), node_id=node_id)
    expected = {
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
        "child_node_ids": [left_node, right_node],
        "left_receipt": left,
        "right_receipt": right,
        "order": order,
    }
    expected["receipt_digest"] = digest(expected)
    active.remove(key)
    return expected


def independent_cut_transcript(scaffold: dict, order: Sequence[int]) -> list[dict]:
    ambient = int(scaffold["d"])
    blocks = [tuple(int(row) for row in block) for block in scaffold["whole_factor_blocks"]]
    if sorted(order) != list(range(len(blocks))):
        raise AssertionError("layout is not a whole-factor permutation")
    cuts = []
    for cut in range(len(order) + 1):
        left_ids = list(order[:cut])
        right_ids = list(order[cut:])
        left = b3v.rref(
            (row for factor_id in left_ids for row in blocks[factor_id]), ambient
        )
        right = b3v.rref(
            (row for factor_id in right_ids for row in blocks[factor_id]), ambient
        )
        basis = b3v.inter(left, right, ambient)
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


def verify(root: Path, artifact: dict) -> dict:
    verify_artifact_integrity(artifact)
    b45_root = root / "b45"
    b45_manifest = json.loads((b45_root / "manifest.json").read_text())
    b45_replay = b45v.verify_full_transcript(b45_root, b45_manifest, expect_frozen=True)
    if not b45_replay["complete"]:
        raise AssertionError("B4.5 source transcript is incomplete")

    source = artifact["source"]
    if source["b45_manifest_digest"] != b45_manifest["manifest_digest"]:
        raise AssertionError("B4.5 manifest binding mismatch")
    if source["b45_transcript_root_digest"] != b45_manifest["chunking"]["transcript_root_digest"]:
        raise AssertionError("B4.5 transcript binding mismatch")
    if source["b45_root_full_set_receipt"] != b45_manifest["execution"]["root_full_set_receipt"]:
        raise AssertionError("B4.5 root receipt binding mismatch")
    for field in (
        "supplied_scaffold_used_for_discovery",
        "supplied_full_set_used_for_discovery",
        "supplied_layout_used_for_discovery",
    ):
        if source[field] is not False:
            raise AssertionError("supplied discovery object accepted")

    leaves = {int(item["node_id"]): item for item in b45_manifest["leaf_full_sets"]}
    nodes = {int(item["node_id"]): item for item in b45_manifest["node_results"]}
    generators = all_generators(b45_root, b45_manifest)
    root_node_id = int(b45_manifest["execution"]["root_node_id"])
    root_node = nodes[root_node_id]
    k = int(b45_manifest["scaffold_case"]["k"])
    selected = deterministic_root_index(root_node, k)
    accepted = accepting_indices(root_node, k)
    expected_selection = {
        "root_node_id": root_node_id,
        "accepting_root_entry_count": len(accepted),
        "selected_root_entry_index": selected,
        "rule": "MINIMUM_SHA256_THEN_ENTRY_INDEX_AMONG_EMPTY_BOUNDARY_WIDTH_AT_MOST_K",
    }
    if artifact["selection"] != expected_selection:
        raise AssertionError("root entry selection mismatch")

    ledger = ReplayLedger(int(b45_manifest["audit"]["cumulative_work"]))
    ledger.charge("ROOT_ACCEPTANCE_TESTS", len(accepted), node_id=root_node_id)
    expected_receipt = replay_entry(
        root_node_id,
        selected,
        b45_manifest,
        b45_root,
        leaves,
        nodes,
        generators,
        ledger,
        set(),
    )
    if artifact["reconstruction_receipt"] != expected_receipt:
        raise AssertionError("reconstruction ancestry receipt mismatch")
    order = expected_receipt["order"]
    cuts = independent_cut_transcript(b45_manifest["scaffold_case"], order)
    ledger.charge("EXACT_LAYOUT_CUT_RECOMPUTATIONS", len(cuts), order=order)
    maximum_width = max(item["width"] for item in cuts)
    if maximum_width > k:
        raise AssertionError("reconstructed layout exceeds k")
    if artifact["reconstructed_factor_order"] != order:
        raise AssertionError("reconstructed order mismatch")
    if artifact["exact_cut_transcript"] != cuts:
        raise AssertionError("exact cut transcript mismatch")
    if artifact["exact_maximum_width"] != maximum_width or artifact["k"] != k:
        raise AssertionError("width result mismatch")

    blocks = b45_manifest["scaffold_case"]["whole_factor_blocks"]
    offsets = b45_manifest["scaffold_case"]["affine_offsets"]
    expected_layout = [
        {
            "position": position,
            "factor_id": factor_id,
            "normal_space_block_rref": blocks[factor_id],
            "affine_offset": offsets[factor_id],
        }
        for position, factor_id in enumerate(order)
    ]
    if artifact["reconstructed_layout"] != expected_layout:
        raise AssertionError("whole-factor/offset layout mismatch")
    if artifact["result"] != LOCAL_RESULT:
        raise AssertionError("local result mismatch")

    expected_work = {
        "cumulative_work_before_reconstruction": int(
            b45_manifest["audit"]["cumulative_work"]
        ),
        "events": ledger.events,
        "reconstruction_work": ledger.total
        - int(b45_manifest["audit"]["cumulative_work"]),
        "cumulative_work_after_reconstruction": ledger.total,
        "monotone": True,
    }
    if artifact["work_ledger"] != expected_work:
        raise AssertionError("reconstruction work ledger mismatch")
    accounting = artifact["certificate_accounting"]
    if accounting["b45_uncompressed_chunk_bytes"] != b45_manifest["chunking"]["uncompressed_chunk_bytes"]:
        raise AssertionError("raw certificate volume mismatch")
    if accounting["b45_compressed_chunk_bytes"] != b45_manifest["chunking"]["compressed_chunk_bytes"]:
        raise AssertionError("compressed certificate volume mismatch")

    expected_strict = {
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
    }
    if artifact["strict_boundary"] != expected_strict:
        raise AssertionError("strict claim boundary mismatch")
    return {
        "root_entry": selected,
        "order": order,
        "maximum_width": maximum_width,
        "reconstruction_work": expected_work["reconstruction_work"],
        "cumulative_work": ledger.total,
    }


def rebind_receipts(value: Any) -> None:
    if isinstance(value, list):
        for item in value:
            rebind_receipts(item)
    elif isinstance(value, dict):
        for key, item in list(value.items()):
            if key != "receipt_digest":
                rebind_receipts(item)
        if "receipt_digest" in value:
            value.pop("receipt_digest", None)
            value["receipt_digest"] = digest(value)


def rebind_artifact(artifact: dict) -> None:
    artifact["manifest_digest"] = "0" * 64
    for _ in range(32):
        body = copy.deepcopy(artifact)
        body.pop("manifest_digest", None)
        artifact["manifest_digest"] = digest(body)
        size = len(canonical_json(artifact)) + 1
        if size == artifact["certificate_accounting"]["fixed_point_serialized_bytes"]:
            return
        artifact["certificate_accounting"]["fixed_point_serialized_bytes"] = size
    raise AssertionError("tamper rebind fixed point did not converge")


def expect_rejection(label: str, root: Path, artifact: dict) -> None:
    rebind_receipts(artifact)
    rebind_artifact(artifact)
    try:
        verify(root, artifact)
    except AssertionError:
        return
    raise AssertionError(f"digest-repaired {label} tamper accepted")


def tamper_self_tests(root: Path, artifact: dict) -> int:
    selection = copy.deepcopy(artifact)
    selection["selection"]["selected_root_entry_index"] = (
        int(selection["selection"]["selected_root_entry_index"]) + 1
    ) % int(selection["selection"]["accepting_root_entry_count"])
    expect_rejection("root selection", root, selection)

    ancestry = copy.deepcopy(artifact)
    ancestry["reconstruction_receipt"]["canonical_attempt_id"] += 1
    expect_rejection("parent pointer", root, ancestry)

    offset = copy.deepcopy(artifact)
    offset["reconstructed_layout"][0]["affine_offset"] ^= 1
    expect_rejection("affine offset", root, offset)

    order = copy.deepcopy(artifact)
    order["reconstructed_factor_order"][0], order["reconstructed_factor_order"][1] = (
        order["reconstructed_factor_order"][1],
        order["reconstructed_factor_order"][0],
    )
    expect_rejection("layout order", root, order)
    return 4


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("transcript_dir")
    parser.add_argument("--tamper-self-test", action="store_true")
    args = parser.parse_args()
    root = Path(args.transcript_dir)
    artifact = json.loads((root / "artifact.json").read_text())
    result = verify(root, artifact)
    tamper_count = tamper_self_tests(root, artifact) if args.tamper_self_test else 0
    print("VERIFIED C049.1 B4.6.1 LAYOUT RECONSTRUCTION")
    print("ROOT_ENTRY_INDEX =", result["root_entry"])
    print("RECONSTRUCTED_ORDER =", result["order"])
    print("EXACT_MAXIMUM_WIDTH =", result["maximum_width"])
    print("RECONSTRUCTION_WORK =", result["reconstruction_work"])
    print("CUMULATIVE_WORK =", result["cumulative_work"])
    print("DIGEST_REPAIRED_TAMPER_CONTROLS =", tamper_count)
    print("GLOBAL_TERMINAL =", TERMINAL)


if __name__ == "__main__":
    main()
