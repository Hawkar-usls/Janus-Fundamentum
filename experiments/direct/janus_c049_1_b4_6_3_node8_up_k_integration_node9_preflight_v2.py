#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import janus_c049_1_b4_6_3_node8_up_k_integration_node9_preflight as core


def build(
    prefix_root: Path,
    hardening_path: Path,
    node7_frontier_path: Path,
    node7_up_k_path: Path,
    node8_frontier_path: Path,
    node8_up_k_path: Path,
    output_dir: Path,
    pair_cap: int = 10000,
    refinement_cap: int = 2000000,
) -> dict:
    prefix_manifest, hardening, hardening_records = core.node6.load_frozen_hardening(
        prefix_root, hardening_path
    )
    node7_frontier, node7_up_k = core.node7int.sources(
        node7_frontier_path, node7_up_k_path
    )
    node8_frontier, node8_up_k = core.source_artifacts(
        node8_frontier_path, node8_up_k_path
    )
    if (
        node8_frontier["source"]["integrated_manifest_digest"]
        != core.NODE7_INTEGRATED_MANIFEST_DIGEST
    ):
        raise AssertionError("node8 frontier integrated manifest binding")
    if (
        node8_frontier["source"]["node7_output_receipt_digest"]
        != core.NODE7_RECEIPT
    ):
        raise AssertionError("node8 frontier node7 receipt binding")

    engine = core.engine
    original_selected = engine.selected_scaffold
    original_up_k = engine.up_k_closure
    original_execute = engine.execute_node
    original_cap = engine.CAP
    original_capability = dict(engine.DEFAULT_CAPABILITY)
    node6_calls: list[str] = []
    node7_calls: list[str] = []
    node8_calls: list[str] = []

    def patched_up_k(generators, ambient_dim, k, ledger):
        if int(ambient_dim) == 2 and int(k) == 1 and len(generators) == 468:
            if node6_calls:
                raise AssertionError("node6 certified closure called twice")
            closure = core.node6.certified_closure(
                generators,
                ambient_dim,
                k,
                hardening,
                hardening_records,
            )
            node6_calls.append(closure["reachable_entries_digest"])
            return closure
        return original_up_k(generators, ambient_dim, k, ledger)

    def patched_execute(
        descriptor,
        sequence_index,
        left_state,
        right_state,
        scaffold_record,
        writers,
        cumulative,
        capability,
    ):
        node_id = int(descriptor["node_id"])
        if node_id == 7:
            if node7_calls:
                raise AssertionError("node7 certified bridge called twice")
            result = core.node7int.execute7(
                descriptor,
                sequence_index,
                left_state,
                right_state,
                scaffold_record,
                writers,
                cumulative,
                node7_frontier,
                node7_up_k,
            )
            node7_calls.append(result[0]["output_receipt"]["receipt_digest"])
            return result
        if node_id == 8:
            if node8_calls:
                raise AssertionError("node8 certified bridge called twice")
            result = core.execute_node8(
                descriptor,
                sequence_index,
                left_state,
                right_state,
                scaffold_record,
                writers,
                cumulative,
                node8_frontier,
                node8_up_k,
            )
            node8_calls.append(result[0]["output_receipt"]["receipt_digest"])
            return result
        return original_execute(
            descriptor,
            sequence_index,
            left_state,
            right_state,
            scaffold_record,
            writers,
            cumulative,
            capability,
        )

    try:
        engine.selected_scaffold = core.negative.selected_negative_scaffold
        engine.up_k_closure = patched_up_k
        engine.execute_node = patched_execute
        engine.CAP = 2000000
        engine.DEFAULT_CAPABILITY["max_child_pairs_per_node"] = int(pair_cap)
        engine.DEFAULT_CAPABILITY["max_refinements_per_node"] = int(
            refinement_cap
        )
        manifest = engine.build(
            output_dir, max_refinements_per_node=int(refinement_cap)
        )
    finally:
        engine.selected_scaffold = original_selected
        engine.up_k_closure = original_up_k
        engine.execute_node = original_execute
        engine.CAP = original_cap
        engine.DEFAULT_CAPABILITY.clear()
        engine.DEFAULT_CAPABILITY.update(original_capability)

    if (len(node6_calls), len(node7_calls), len(node8_calls)) != (1, 1, 1):
        raise AssertionError("certified bridge call vector")
    execution = manifest["execution"]
    if execution["processed_internal_node_ids"] != [6, 7, 8]:
        raise AssertionError("processed node vector")
    stop = execution["stop"]
    if (
        int(stop["node_id"]),
        stop["reason"],
        int(stop["required"]),
        int(stop["cap"]),
        stop["no_layout_at_cap"],
        stop["terminal"],
    ) != (
        core.N9,
        "CHILD_PAIR_CAP_EXCEEDED",
        core.N9_PAIRS,
        int(pair_cap),
        False,
        core.TERMINAL,
    ):
        raise AssertionError("node9 stop")

    transcript_root = str(manifest["chunking"]["transcript_root_digest"])
    if bytes.fromhex(transcript_root) != bytes.fromhex(core.TRANSCRIPT_ROOT):
        raise AssertionError(
            f"transcript root changed: {transcript_root!r}"
        )

    node8 = next(
        item for item in manifest["node_results"] if int(item["node_id"]) == 8
    )
    closure = node8["node_up_k"]
    if (
        closure["entry_count"],
        closure["reachable_entries_digest"],
        len(closure["input_generators"]),
        len(closure["retained_generators"]),
        len(closure["removals"]),
    ) != (
        core.N8_ENTRIES,
        core.COORDINATE_ENTRIES_DIGEST,
        core.N8_INPUT,
        core.N8_RETAINED,
        core.N8_REMOVALS,
    ):
        raise AssertionError("node8 integrated state")
    if any(int(value["count"]) for value in node8["record_ranges"].values()):
        raise AssertionError("generic node8 transcript materialized")

    leaf4 = manifest["leaf_full_sets"][4]
    if leaf4["output_receipt"]["receipt_digest"] != core.LEAF4_RECEIPT:
        raise AssertionError("leaf4 receipt")
    left_entries = closure["entries"]
    right_entries = leaf4["full_set"]["entries"]
    pair_count = len(left_entries) * len(right_entries)
    refinement_count = core.exact_refinements(left_entries, right_entries)
    if (pair_count, refinement_count) != (
        core.N9_PAIRS,
        core.N9_REFINEMENTS,
    ):
        raise AssertionError("node9 exact frontier")

    blocks = [
        tuple(block)
        for block in manifest["scaffold_case"]["whole_factor_blocks"]
    ]
    left_boundary = tuple(node8["parent_boundary"])
    right_boundary = tuple(leaf4["boundary_rref_ambient"])
    common = engine.xor_basis((*left_boundary, *right_boundary), 3)
    parent = engine.boundary(
        [blocks[index] for index in [0, 1, 2, 3, 4]],
        [blocks[5]],
        3,
    )
    if (left_boundary, right_boundary, common, parent) != (
        (4, 1),
        (5,),
        (4, 1),
        (1,),
    ):
        raise AssertionError("node9 geometry")

    summary = {
        "schema": core.SCHEMA,
        "source": {
            "prefix_manifest_digest": prefix_manifest["manifest_digest"],
            "hardening_artifact_sha256": core.node6.EXPECTED_HARDENING_SHA256,
            "node7_frontier_artifact_sha256": core.node7int.FRONTIER_SHA,
            "node7_up_k_artifact_sha256": core.node7int.UPK_SHA,
            "node8_frontier_artifact_sha256": core.FRONTIER_SHA,
            "node8_frontier_semantic_digest": core.FRONTIER_SEM,
            "node8_up_k_artifact_sha256": core.UPK_SHA,
            "node8_up_k_semantic_digest": core.UPK_SEM,
        },
        "certified_calls": {"node6": 1, "node7": 1, "node8": 1},
        "integrated_manifest_digest": manifest["manifest_digest"],
        "integrated_transcript_root_digest": transcript_root,
        "node8": {
            "node_execution_digest": node8["node_execution_digest"],
            "output_receipt_digest": node8["output_receipt"]["receipt_digest"],
            "input_generators": core.N8_INPUT,
            "retained_generators": core.N8_RETAINED,
            "direct_removals": core.N8_REMOVALS,
            "up_k_entries": core.N8_ENTRIES,
            "source_ambient_entries_digest": core.SOURCE_ENTRIES_DIGEST,
            "coordinate_entries_digest": core.COORDINATE_ENTRIES_DIGEST,
            "generic_pair_records_materialized": 0,
            "generic_refinement_records_materialized": 0,
        },
        "node9_preflight": {
            "left_child_node_id": 8,
            "right_child_node_id": 4,
            "left_entry_count": len(left_entries),
            "right_entry_count": len(right_entries),
            "child_pair_count": pair_count,
            "naive_refinement_count": refinement_count,
            "left_length_histogram": core.length_histogram(left_entries),
            "right_length_histogram": core.length_histogram(right_entries),
            "left_boundary": list(left_boundary),
            "right_boundary": list(right_boundary),
            "common_boundary": list(common),
            "parent_boundary": list(parent),
            "left_expand_identity": common == left_boundary,
            "shrink_identity": common == parent,
            "pair_cap": int(pair_cap),
            "refinement_cap": int(refinement_cap),
            "stop_reason": stop["reason"],
            "no_layout_at_cap": False,
        },
        "execution": copy.deepcopy(execution),
        "result": "HONEST_OPEN_AT_NODE9_PARENT_FRONTIER",
        "strict_boundary": {
            "node8_up_k_admitted": True,
            "node8_integrated_into_bottom_up_executor": True,
            "node8_generic_cartesian_replay_required": False,
            "node9_parent_refinement_started": True,
            "node9_parent_refinement_complete": False,
            "node9_parent_up_k_complete": False,
            "negative_root_reached": False,
            "terminal_completeness_proved": False,
            "found_layout_enabled": False,
            "no_layout_at_cap_enabled": False,
            "current_global_terminal": core.TERMINAL,
            "p_vs_np": "OPEN",
        },
        "next_gate": "C049.1_B4.6.3_NODE9_PARENT_FRONTIER_STRUCTURAL_COMPRESSION",
    }
    summary["semantic_digest"] = core.digest(summary)
    (output_dir / "node8-integration-node9-preflight-summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print("JANUS_C049_1_B4_6_3_NODE8_UP_K_INTEGRATION = PASS")
    print("PROCESSED_INTERNAL_NODE_IDS =", execution["processed_internal_node_ids"])
    print("NODE8_INPUT_GENERATORS =", core.N8_INPUT)
    print("NODE8_RETAINED_GENERATORS =", core.N8_RETAINED)
    print("NODE8_DIRECT_REMOVALS =", core.N8_REMOVALS)
    print("NODE8_UP_K_ENTRIES =", core.N8_ENTRIES)
    print("NODE9_CHILD_PAIRS_REQUIRED =", pair_count)
    print("NODE9_NAIVE_REFINEMENTS_REQUIRED =", refinement_count)
    print("STOP_NODE =", stop["node_id"])
    print("STOP_REASON =", stop["reason"])
    print("ROOT_NODE =", core.ROOT)
    print("GLOBAL_TERMINAL =", core.TERMINAL)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("prefix_root", type=Path)
    parser.add_argument("hardening_artifact", type=Path)
    parser.add_argument("node7_frontier_artifact", type=Path)
    parser.add_argument("node7_up_k_artifact", type=Path)
    parser.add_argument("node8_frontier_artifact", type=Path)
    parser.add_argument("node8_up_k_artifact", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--node9-pair-cap", type=int, default=10000)
    parser.add_argument("--node9-refinement-cap", type=int, default=2000000)
    args = parser.parse_args()
    build(
        args.prefix_root,
        args.hardening_artifact,
        args.node7_frontier_artifact,
        args.node7_up_k_artifact,
        args.node8_frontier_artifact,
        args.node8_up_k_artifact,
        args.output_dir,
        args.node9_pair_cap,
        args.node9_refinement_cap,
    )


if __name__ == "__main__":
    main()
