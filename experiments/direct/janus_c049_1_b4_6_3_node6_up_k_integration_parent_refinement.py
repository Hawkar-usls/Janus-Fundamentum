#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence

import janus_c049_1_b2_up_k_core as b2
import janus_c049_1_b4_5_bottom_up_scaffold_executor as engine
import janus_c049_1_b4_6_3_dimension_two_preorder_hardening as hardening
import janus_c049_1_b4_6_3_negative_root_engine_replay as negative
from janus_c049_1_b1_compact_trajectory_core import encode

SCHEMA = "C049.1-B4.6.3-NODE6-UP-K-INTEGRATION-PARENT-REFINEMENT-v1"
TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"
EXPECTED_NODE_ID = 6
EXPECTED_AMBIENT_DIM = 2
EXPECTED_K = 1
EXPECTED_INPUT_GENERATORS = 468
EXPECTED_RETAINED_GENERATORS = 3
EXPECTED_REMOVALS = 465
EXPECTED_ENTRIES = 468
EXPECTED_FAMILY_DIGEST = "0d0ef7d96cc83d785909a679db310ac3b4b61db53397f8df4262dab2197c9733"
EXPECTED_HARDENING_SHA256 = "a68ea1957382bfa89386a09ab501a052057b1cc5de8db7191a6ab3a26e1d2af9"
EXPECTED_HARDENING_SEMANTIC_DIGEST = "f453a0fd07c1757b106e242aea105a0cc9c1093532428f0e502e92e494987ec5"
GENERIC_B2_CAP = 2_000_000
DEFAULT_PARENT_PAIR_CAP = 10_000
DEFAULT_PARENT_REFINEMENT_CAP = 2_000_000


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_frozen_hardening(prefix_root: Path, artifact_path: Path) -> tuple[dict, dict, list[dict]]:
    manifest = json.loads((prefix_root / "manifest.json").read_text(encoding="utf-8"))
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if file_sha256(artifact_path) != EXPECTED_HARDENING_SHA256:
        raise AssertionError("dimension-two hardening artifact byte digest drift")
    if artifact.get("semantic_digest") != EXPECTED_HARDENING_SEMANTIC_DIGEST:
        raise AssertionError("dimension-two hardening semantic digest drift")
    if artifact.get("admit") is not True:
        raise AssertionError("dimension-two hardening is not admitted")
    if set(artifact.get("invariant_vector", {}).values()) != {"PASS"}:
        raise AssertionError("dimension-two hardening invariant vector is not fully green")
    if artifact.get("source_manifest_digest") != manifest.get("manifest_digest"):
        raise AssertionError("hardening artifact is not bound to the supplied prefix")
    stop = manifest["execution"]["stop"]
    if stop is None or int(stop["node_id"]) != EXPECTED_NODE_ID:
        raise AssertionError("prefix does not stop at the frozen node-6 capability boundary")
    records = hardening.read_generators(prefix_root, manifest, EXPECTED_NODE_ID)
    if len(records) != EXPECTED_INPUT_GENERATORS:
        raise AssertionError("frozen node-6 generator inventory drift")
    return manifest, artifact, records


def certified_closure(
    generators: Sequence[tuple],
    ambient_dim: int,
    k: int,
    artifact: dict,
    prefix_records: Sequence[dict],
) -> dict:
    if (int(ambient_dim), int(k), len(generators)) != (
        EXPECTED_AMBIENT_DIM,
        EXPECTED_K,
        EXPECTED_INPUT_GENERATORS,
    ):
        raise AssertionError("certified closure called on the wrong family")

    ordered_generators = tuple(sorted(generators, key=b2.trajectory_key))
    encoded_generators = [encode(gamma) for gamma in ordered_generators]
    prefix_encoded = [record["trajectory_parent_coordinates"] for record in prefix_records]
    if encoded_generators != prefix_encoded:
        raise AssertionError("live node-6 family differs from the frozen certified family")
    family_digest = digest(sorted(encoded_generators, key=canonical_json))
    if family_digest != EXPECTED_FAMILY_DIGEST:
        raise AssertionError("live node-6 family digest drift")
    if artifact["input_generator_family_digest"] != family_digest:
        raise AssertionError("hardening artifact family binding mismatch")

    by_id = {
        int(record["generator_id"]): record["trajectory_parent_coordinates"]
        for record in prefix_records
    }
    retained_ids = [int(value) for value in artifact["retained_generator_ids"]]
    retained = [copy.deepcopy(by_id[identifier]) for identifier in retained_ids]
    if retained != artifact["retained_generators"]:
        raise AssertionError("retained generator binding drift")

    removals = []
    for item in artifact["removals"]:
        removed_id = int(item["removed_generator_id"])
        retained_id = int(item["retained_generator_id"])
        removals.append(
            {
                "removed": copy.deepcopy(by_id[removed_id]),
                "retained": copy.deepcopy(by_id[retained_id]),
                "witness": copy.deepcopy(item["direct_witness"]),
                "reason": "STRICTLY_COVERED",
                "certified_removal_id": int(item["removal_id"]),
                "certified_removal_digest": item["removal_digest"],
            }
        )

    structural = {
        key: int(value)
        for key, value in artifact["work_ledger"]["structural_counters"].items()
    }
    ledger = {
        key: int(value)
        for key, value in artifact["work_ledger"]["preorder_counters"].items()
    }
    structural_total = sum(structural.values())
    ledger["discovery_work"] = structural_total
    ledger["certified_structural_work"] = structural_total
    ledger["certified_total_charged_operations"] = int(
        artifact["work_ledger"]["total_charged_operations"]
    )
    if ledger["discovery_work"] + ledger["work"] != ledger["certified_total_charged_operations"]:
        raise AssertionError("certified work ledger accounting mismatch")

    closure_data = artifact["exact_reachable_closure"]
    entries = copy.deepcopy(closure_data["reachable_entries"])
    closure = {
        "ambient_dim": int(ambient_dim),
        "k": int(k),
        "input_generators": encoded_generators,
        "retained_generators": retained,
        "removals": removals,
        "universe_size": int(closure_data["complete_reachable_catalog_size"]),
        "entries": entries,
        "entry_count": len(entries),
        "ledger": dict(sorted(ledger.items())),
        "closure_method": "CERTIFIED_DIMENSION_TWO_REACHABLE_CATALOG",
        "global_universe_enumerated": False,
        "complete_reachable_catalog_proved": True,
        "input_generator_family_digest": family_digest,
        "hardening_artifact_sha256": EXPECTED_HARDENING_SHA256,
        "hardening_semantic_digest": EXPECTED_HARDENING_SEMANTIC_DIGEST,
        "reachable_entries_digest": closure_data["reachable_entries_digest"],
        "reachable_catalog_stream_sha256": closure_data[
            "complete_reachable_catalog_stream_sha256"
        ],
        "invariant_vector": copy.deepcopy(artifact["invariant_vector"]),
        "admit": True,
    }
    if (
        len(closure["retained_generators"]),
        len(closure["removals"]),
        closure["entry_count"],
    ) != (EXPECTED_RETAINED_GENERATORS, EXPECTED_REMOVALS, EXPECTED_ENTRIES):
        raise AssertionError("certified closure cardinality drift")
    if digest(closure["entries"]) != closure["reachable_entries_digest"]:
        raise AssertionError("certified reachable entries digest mismatch")
    return closure


def build(
    prefix_root: Path,
    hardening_artifact_path: Path,
    output_dir: Path,
    parent_pair_cap: int = DEFAULT_PARENT_PAIR_CAP,
    parent_refinement_cap: int = DEFAULT_PARENT_REFINEMENT_CAP,
) -> dict:
    if parent_pair_cap < 0 or parent_refinement_cap < 0:
        raise ValueError("negative parent capability")
    prefix_manifest, artifact, prefix_records = load_frozen_hardening(
        prefix_root, hardening_artifact_path
    )

    original_selected = engine.selected_scaffold
    original_up_k = engine.up_k_closure
    original_cap = engine.CAP
    original_capability = dict(engine.DEFAULT_CAPABILITY)
    certified_calls: list[dict] = []

    def integrated_up_k(generators, ambient_dim, k, ledger):
        if (
            int(ambient_dim) == EXPECTED_AMBIENT_DIM
            and int(k) == EXPECTED_K
            and len(generators) == EXPECTED_INPUT_GENERATORS
        ):
            if certified_calls:
                raise AssertionError("certified node-6 closure invoked more than once")
            closure = certified_closure(
                generators, ambient_dim, k, artifact, prefix_records
            )
            certified_calls.append(
                {
                    "call_index": 0,
                    "node_id": EXPECTED_NODE_ID,
                    "input_generator_count": len(generators),
                    "retained_generator_count": len(closure["retained_generators"]),
                    "removal_count": len(closure["removals"]),
                    "entry_count": int(closure["entry_count"]),
                    "input_generator_family_digest": closure[
                        "input_generator_family_digest"
                    ],
                    "reachable_entries_digest": closure["reachable_entries_digest"],
                    "hardening_artifact_sha256": closure[
                        "hardening_artifact_sha256"
                    ],
                }
            )
            return closure
        return original_up_k(generators, ambient_dim, k, ledger)

    try:
        engine.selected_scaffold = negative.selected_negative_scaffold
        engine.up_k_closure = integrated_up_k
        engine.CAP = GENERIC_B2_CAP
        engine.DEFAULT_CAPABILITY["max_child_pairs_per_node"] = int(parent_pair_cap)
        engine.DEFAULT_CAPABILITY["max_refinements_per_node"] = int(
            parent_refinement_cap
        )
        manifest = engine.build(
            output_dir, max_refinements_per_node=int(parent_refinement_cap)
        )
    finally:
        engine.selected_scaffold = original_selected
        engine.up_k_closure = original_up_k
        engine.CAP = original_cap
        engine.DEFAULT_CAPABILITY.clear()
        engine.DEFAULT_CAPABILITY.update(original_capability)

    if len(certified_calls) != 1:
        raise AssertionError("certified node-6 closure was not integrated exactly once")
    processed_ids = [int(value) for value in manifest["execution"]["processed_internal_node_ids"]]
    if EXPECTED_NODE_ID not in processed_ids:
        raise AssertionError("executor did not complete node 6 after certified integration")
    node6 = next(
        node for node in manifest["node_results"] if int(node["node_id"]) == EXPECTED_NODE_ID
    )
    if node6["node_up_k"].get("closure_method") != "CERTIFIED_DIMENSION_TWO_REACHABLE_CATALOG":
        raise AssertionError("node 6 did not carry the certified closure method")
    if node6["audit"]["final_up_k_entries"] != EXPECTED_ENTRIES:
        raise AssertionError("node-6 integrated entry count drift")
    if node6["audit"]["retained_generators"] != EXPECTED_RETAINED_GENERATORS:
        raise AssertionError("node-6 integrated retained count drift")
    if node6["audit"]["b2_dominance_deletions"] != EXPECTED_REMOVALS:
        raise AssertionError("node-6 integrated deletion count drift")

    stop = manifest["execution"]["stop"]
    complete = manifest["execution"]["status"] == "ROOT_FULL_SET_COMPUTED"
    if stop is not None:
        if int(stop["node_id"]) == EXPECTED_NODE_ID:
            raise AssertionError("executor remained stuck at the closed node-6 gate")
        if stop.get("no_layout_at_cap") is not False:
            raise AssertionError("incomplete parent run promoted no-layout")
        if stop.get("terminal") != TERMINAL:
            raise AssertionError("incomplete parent run terminal drift")

    summary = {
        "schema": SCHEMA,
        "source_prefix_manifest_digest": prefix_manifest["manifest_digest"],
        "source_prefix_transcript_root_digest": prefix_manifest["chunking"][
            "transcript_root_digest"
        ],
        "source_hardening_artifact_sha256": EXPECTED_HARDENING_SHA256,
        "source_hardening_semantic_digest": EXPECTED_HARDENING_SEMANTIC_DIGEST,
        "certified_calls": certified_calls,
        "node6_execution_digest": node6["node_execution_digest"],
        "node6_output_receipt": node6["output_receipt"],
        "integrated_manifest_digest": manifest["manifest_digest"],
        "integrated_transcript_root_digest": manifest["chunking"][
            "transcript_root_digest"
        ],
        "execution": copy.deepcopy(manifest["execution"]),
        "audit": copy.deepcopy(manifest["audit"]),
        "capability": {
            "generic_b2_cap": GENERIC_B2_CAP,
            "max_child_pairs_per_node": int(parent_pair_cap),
            "max_refinements_per_node": int(parent_refinement_cap),
        },
        "result": "ROOT_FULL_SET_COMPUTED"
        if complete
        else "HONEST_OPEN_AFTER_CERTIFIED_NODE6_INTEGRATION",
        "strict_boundary": {
            "dimension_two_hardening_admitted": True,
            "certified_node6_up_k_integrated": True,
            "node6_old_b2_capability_stop_removed": True,
            "parent_execution_started": len(processed_ids) > 1 or (
                stop is not None and int(stop["node_id"]) > EXPECTED_NODE_ID
            ),
            "negative_root_reached": complete,
            "terminal_completeness_proved": False,
            "found_layout_enabled": False,
            "no_layout_at_cap_enabled": False,
            "current_global_terminal": TERMINAL,
            "p_vs_np": "OPEN",
        },
        "next_gate": "C049.1_B4.6.3_PARENT_CAPABILITY_OR_ROOT_ANALYSIS",
    }
    summary["semantic_digest"] = digest(summary)
    (output_dir / "node6-integration-summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print("JANUS_C049_1_B4_6_3_NODE6_UP_K_INTEGRATION = PASS")
    print("CERTIFIED_CALLS =", len(certified_calls))
    print("NODE6_RETAINED_GENERATORS =", node6["audit"]["retained_generators"])
    print("NODE6_DELETION_WITNESSES =", node6["audit"]["b2_dominance_deletions"])
    print("NODE6_UP_K_ENTRIES =", node6["audit"]["final_up_k_entries"])
    print("PROCESSED_INTERNAL_NODE_IDS =", processed_ids)
    print("EXECUTION_STATUS =", manifest["execution"]["status"])
    print("STOP_NODE =", None if stop is None else stop["node_id"])
    print("STOP_REASON =", None if stop is None else stop["reason"])
    print("ROOT_UP_K_ENTRIES =", manifest["audit"]["root_up_k_entries"])
    print("GLOBAL_TERMINAL =", TERMINAL)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("prefix_root", type=Path)
    parser.add_argument("hardening_artifact", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--parent-pair-cap", type=int, default=DEFAULT_PARENT_PAIR_CAP
    )
    parser.add_argument(
        "--parent-refinement-cap",
        type=int,
        default=DEFAULT_PARENT_REFINEMENT_CAP,
    )
    args = parser.parse_args()
    build(
        args.prefix_root,
        args.hardening_artifact,
        args.output_dir,
        args.parent_pair_cap,
        args.parent_refinement_cap,
    )


if __name__ == "__main__":
    main()
