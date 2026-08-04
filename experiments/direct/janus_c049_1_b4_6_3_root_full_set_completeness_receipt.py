#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from collections import defaultdict
from pathlib import Path

SCHEMA = "C049.1-B4.6.3-ROOT-FULL-SET-COMPLETENESS-RECEIPT-v1"


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical_json(value)).hexdigest()


def iter_records(root: Path, manifest: dict, kind: str):
    for metadata in manifest["chunking"]["chunk_groups"][kind]:
        payload = json.loads(gzip.decompress((root / metadata["filename"]).read_bytes()))
        if payload["kind"] != kind or payload["record_count"] != metadata["record_count"]:
            raise AssertionError("chunk inventory mismatch")
        unsigned = {key: value for key, value in payload.items() if key != "chunk_payload_digest"}
        if digest(unsigned) != payload["chunk_payload_digest"]:
            raise AssertionError("chunk payload digest mismatch")
        yield from payload["records"]


def classify(inventory_complete: bool, semantic_complete: bool, accepting: bool, execution_open: bool) -> str:
    if execution_open or not inventory_complete or not semantic_complete:
        return "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"
    return "FOUND_LAYOUT_CANDIDATE" if accepting else "NO_LAYOUT_AT_CAP_CANDIDATE"


def build_receipt(root: Path) -> dict:
    manifest = json.loads((root / "manifest.json").read_text())
    stats = defaultdict(lambda: defaultdict(int))
    successful_attempt_ids = defaultdict(set)
    generator_provenance = defaultdict(list)

    for pair in iter_records(root, manifest, "PAIRS"):
        node_id = int(pair["node_id"])
        stats[node_id]["pairs"] += 1
        stats[node_id]["paths"] += int(pair["lattice_path_count"])

    for refinement in iter_records(root, manifest, "REFINEMENTS"):
        node_id = int(refinement["node_id"])
        stats[node_id]["refinements"] += 1
        if refinement["status"] == "SUCCESS":
            stats[node_id]["successful"] += 1
            successful_attempt_ids[node_id].add(int(refinement["attempt_id"]))
        else:
            stats[node_id]["failed"] += 1

    for generator in iter_records(root, manifest, "GENERATORS"):
        node_id = int(generator["node_id"])
        stats[node_id]["generators"] += 1
        provenance = [int(value) for value in generator["provenance_attempt_ids"]]
        if not provenance or int(generator["canonical_retained_attempt_id"]) != provenance[0]:
            raise AssertionError("generator canonical provenance mismatch")
        generator_provenance[node_id].extend(provenance)

    for deletion in iter_records(root, manifest, "DELETIONS"):
        stats[int(deletion["node_id"])]["deletions"] += 1

    node_receipts = []
    inventory_complete = True
    for node in manifest["node_results"]:
        node_id = int(node["node_id"])
        summary = stats[node_id]
        audit = node["audit"]
        expected_pairs = int(audit["child_full_set_entries"][0]) * int(audit["child_full_set_entries"][1])
        provenance = generator_provenance[node_id]
        provenance_set = set(provenance)

        checks = {
            "child_pairs": {
                "expected": expected_pairs,
                "replayed": summary["pairs"],
                "equal": expected_pairs == summary["pairs"] == int(audit["child_pairs_processed"]),
            },
            "delannoy_paths": {
                "expected_from_pairs": summary["paths"],
                "replayed_refinements": summary["refinements"],
                "equal": summary["paths"] == summary["refinements"] == int(audit["lattice_paths_processed"]),
            },
            "refinement_partition": {
                "total": summary["refinements"],
                "successful": summary["successful"],
                "failed": summary["failed"],
                "equal": summary["refinements"] == summary["successful"] + summary["failed"]
                and summary["successful"] == int(audit["successful_refinements"])
                and summary["failed"] == int(audit["failed_refinements"]),
            },
            "successful_provenance_partition": {
                "successful_attempts": summary["successful"],
                "provenance_occurrences": len(provenance),
                "distinct_provenance_attempts": len(provenance_set),
                "all_successful": provenance_set == successful_attempt_ids[node_id],
                "equal": len(provenance) == len(provenance_set) == summary["successful"]
                and provenance_set == successful_attempt_ids[node_id],
            },
            "generator_inventory": {
                "records": summary["generators"],
                "declared": int(audit["unique_successful_generators"]),
                "equal": summary["generators"] == int(audit["unique_successful_generators"]),
            },
            "deletion_inventory": {
                "records": summary["deletions"],
                "declared": int(audit["duplicate_successful_outputs_deleted"])
                + int(audit["b2_dominance_deletions"]),
                "equal": summary["deletions"]
                == int(audit["duplicate_successful_outputs_deleted"])
                + int(audit["b2_dominance_deletions"]),
            },
            "up_k_inventory": {
                "entry_count": int(node["node_up_k"]["entry_count"]),
                "entries_len": len(node["node_up_k"]["entries"]),
                "output_entry_count": int(node["output_receipt"]["entry_count"]),
                "equal": int(node["node_up_k"]["entry_count"])
                == len(node["node_up_k"]["entries"])
                == int(node["output_receipt"]["entry_count"]),
            },
        }
        node_complete = all(check["equal"] for check in checks.values())
        inventory_complete = inventory_complete and node_complete
        node_receipts.append(
            {
                "node_id": node_id,
                "checks": checks,
                "inventory_complete": node_complete,
                "semantic_up_k_replay": "REQUIRED_IN_INDEPENDENT_VERIFIER",
                "node_execution_digest": node["node_execution_digest"],
            }
        )

    root_node = next(
        node for node in manifest["node_results"]
        if int(node["node_id"]) == int(manifest["execution"]["root_node_id"])
    )
    k = int(manifest["scaffold_case"]["k"])
    accepting_indices = []
    for index, entry in enumerate(root_node["node_up_k"]["entries"]):
        trajectory = entry["trajectory"]
        if max(int(item["value"]) for item in trajectory) <= k and all(
            not item["left"] and not item["right"] for item in trajectory
        ):
            accepting_indices.append(index)

    execution_open = manifest["execution"]["status"] != "COMPLETE"
    semantic_complete = False
    receipt = {
        "schema": SCHEMA,
        "source_manifest_digest": manifest["manifest_digest"],
        "root_node_id": manifest["execution"]["root_node_id"],
        "node_receipts": node_receipts,
        "inventory_complete": inventory_complete,
        "semantic_up_k_replay_complete": semantic_complete,
        "execution_open": execution_open,
        "accepting_root_entry_indices": accepting_indices,
        "terminal_classifier": classify(
            inventory_complete,
            semantic_complete,
            bool(accepting_indices),
            execution_open,
        ),
        "strict_boundary": {
            "found_layout_enabled": False,
            "no_layout_at_cap_enabled": False,
            "terminal_completeness_proved": False,
            "current_global_terminal": "OPEN_TRAJECTORY_ENGINE_INCOMPLETE",
            "p_vs_np": "OPEN",
        },
    }
    receipt["receipt_digest"] = digest(receipt)
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("round_dir", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    receipt = build_receipt(args.round_dir)
    args.output.write_bytes(canonical_json(receipt) + b"\n")
    print(json.dumps({"receipt": str(args.output), "digest": receipt["receipt_digest"], "terminal": receipt["terminal_classifier"]}))


if __name__ == "__main__":
    main()
