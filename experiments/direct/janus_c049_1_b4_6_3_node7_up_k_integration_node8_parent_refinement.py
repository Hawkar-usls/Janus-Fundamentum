#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence

import janus_c049_1_b4_5_bottom_up_scaffold_executor as engine
import janus_c049_1_b4_6_3_negative_root_engine_replay as negative
import janus_c049_1_b4_6_3_node6_up_k_integration_parent_refinement as node6_integration
import janus_c049_1_b4_6_3_node7_parent_frontier_structural_compression as frontier

SCHEMA = "C049.1-B4.6.3-NODE7-UP-K-INTEGRATION-NODE8-PARENT-REFINEMENT-v1"
TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"

NODE6_ID = 6
NODE7_ID = 7
NODE8_ID = 8
EXPECTED_FRONTIER_SHA256 = "6a0748219d829434feeb5de2c5488e1fa3aeb1fab16ecbfee0c5629be90130a9"
EXPECTED_FRONTIER_SEMANTIC_DIGEST = "ed6b59821aaef10ac6bdb6286a72ffcafd15e2bbd2619e0edffc7f711a2b1103"
EXPECTED_UP_K_SHA256 = "c085a3bee4e0c92a01eb22715390079f9858c5704ebcbf8534f9de196087d189"
EXPECTED_UP_K_SEMANTIC_DIGEST = "23079901348590eb39d60d904d52dfd5004f8b287382a288ccbea688802b22f2"
EXPECTED_NODE7_DESCRIPTOR_DIGEST = "747cfdbdb19c445aecff38ee58359df7529420448169bfa0808208c5b83e2f2c"
EXPECTED_NODE6_RECEIPT_DIGEST = "88170c8f5ba5519908e88f1dba21bb2247218c0713dc6830e562a879edd3aad9"
EXPECTED_LEFT_TRAJECTORY_SET_DIGEST = "0d0ef7d96cc83d785909a679db310ac3b4b61db53397f8df4262dab2197c9733"
EXPECTED_RIGHT_TRAJECTORY_SET_DIGEST = "558d235c8b538640c7383302497a909e63208759602c2b66c890672c8770b707"
EXPECTED_INPUT_GENERATORS = 13
EXPECTED_RETAINED_GENERATORS = 13
EXPECTED_REMOVALS = 0
EXPECTED_ENTRIES = 9108
EXPECTED_NODE8_RIGHT_ENTRIES = 36
EXPECTED_NODE8_PAIRS = 327888
EXPECTED_NODE8_NAIVE_REFINEMENTS = 602017584
DEFAULT_PAIR_CAP = 10_000
DEFAULT_REFINEMENT_CAP = 2_000_000


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def delannoy_path_count(m: int, n: int) -> int:
    if m <= 0 or n <= 0:
        raise ValueError("trajectory lengths must be positive")
    table = [[0] * n for _ in range(m)]
    table[0][0] = 1
    for i in range(m):
        for j in range(n):
            if i == 0 and j == 0:
                continue
            value = 0
            if i:
                value += table[i - 1][j]
            if j:
                value += table[i][j - 1]
            if i and j:
                value += table[i - 1][j - 1]
            table[i][j] = value
    return table[-1][-1]


def load_artifacts(frontier_path: Path, up_k_path: Path) -> tuple[dict, dict]:
    if file_sha256(frontier_path) != EXPECTED_FRONTIER_SHA256:
        raise AssertionError("node-7 frontier artifact byte digest drift")
    if file_sha256(up_k_path) != EXPECTED_UP_K_SHA256:
        raise AssertionError("node-7 up_k artifact byte digest drift")
    frontier_artifact = json.loads(frontier_path.read_text(encoding="utf-8"))
    up_k_artifact = json.loads(up_k_path.read_text(encoding="utf-8"))
    if frontier_artifact.get("semantic_digest") != EXPECTED_FRONTIER_SEMANTIC_DIGEST:
        raise AssertionError("node-7 frontier semantic digest drift")
    if frontier_artifact.get("admit") is not True:
        raise AssertionError("node-7 frontier is not admitted")
    if set(frontier_artifact.get("invariant_vector", {}).values()) != {"PASS"}:
        raise AssertionError("node-7 frontier invariant vector is not green")
    if up_k_artifact.get("semantic_digest") != EXPECTED_UP_K_SEMANTIC_DIGEST:
        raise AssertionError("node-7 up_k semantic digest drift")
    proof = up_k_artifact.get("proof_payload", {})
    if proof.get("admit") is not True:
        raise AssertionError("node-7 up_k closure is not admitted")
    if set(proof.get("invariant_vector", {}).values()) != {"PASS"}:
        raise AssertionError("node-7 up_k invariant vector is not green")
    if proof.get("source", {}).get("node7_frontier_artifact_sha256") != EXPECTED_FRONTIER_SHA256:
        raise AssertionError("node-7 up_k source binding drift")
    if (
        int(proof.get("input_generator_count", -1)),
        int(proof.get("retained_generator_count", -1)),
        int(proof.get("preorder_minimization", {}).get("removal_count", -1)),
        int(proof.get("exact_reachable_closure", {}).get("complete_reachable_catalog_size", -1)),
    ) != (
        EXPECTED_INPUT_GENERATORS,
        EXPECTED_RETAINED_GENERATORS,
        EXPECTED_REMOVALS,
        EXPECTED_ENTRIES,
    ):
        raise AssertionError("node-7 up_k cardinality drift")
    return frontier_artifact, up_k_artifact


def canonical_trajectory_set_digest(entries: Sequence[dict]) -> str:
    return digest(
        sorted(
            (copy.deepcopy(item["trajectory"]) for item in entries),
            key=canonical_json,
        )
    )


def certified_node7_closure(up_k_artifact: dict) -> dict:
    proof = up_k_artifact["proof_payload"]
    closure_data = proof["exact_reachable_closure"]
    entries = copy.deepcopy(closure_data["reachable_entries"])
    work = {key: int(value) for key, value in proof["work_ledger"].items()}
    discovery_keys = (
        "binary_scalar_sequences_tested",
        "input_generators_replayed",
        "reachable_candidates_constructed",
        "retained_generators_replayed",
    )
    discovery_work = sum(work[key] for key in discovery_keys)
    total_work = sum(work.values())
    ledger = {
        "discovery_work": discovery_work,
        "work": total_work - discovery_work,
        "certified_total_charged_operations": total_work,
    }
    closure = {
        "ambient_dim": int(proof["ambient_dim"]),
        "k": int(proof["k"]),
        "input_generators": copy.deepcopy(proof["input_generators"]),
        "retained_generators": copy.deepcopy(proof["retained_generators"]),
        "removals": copy.deepcopy(proof["preorder_minimization"]["removals"]),
        "universe_size": int(closure_data["complete_reachable_catalog_size"]),
        "entries": entries,
        "entry_count": len(entries),
        "ledger": ledger,
        "closure_method": "CERTIFIED_NODE7_THIRTEEN_GENERATOR_REACHABLE_CATALOG",
        "global_universe_enumerated": False,
        "complete_reachable_catalog_proved": True,
        "input_generator_family_digest": proof["input_generator_family_digest"],
        "frontier_artifact_sha256": EXPECTED_FRONTIER_SHA256,
        "up_k_artifact_sha256": EXPECTED_UP_K_SHA256,
        "up_k_semantic_digest": EXPECTED_UP_K_SEMANTIC_DIGEST,
        "reachable_entries_digest": closure_data["reachable_entries_digest"],
        "reachable_catalog_stream_sha256": closure_data[
            "complete_reachable_catalog_stream_sha256"
        ],
        "invariant_vector": copy.deepcopy(proof["invariant_vector"]),
        "admit": True,
    }
    if digest(entries) != closure["reachable_entries_digest"]:
        raise AssertionError("node-7 certified reachable entries digest mismatch")
    if (
        len(closure["input_generators"]),
        len(closure["retained_generators"]),
        len(closure["removals"]),
        closure["entry_count"],
    ) != (
        EXPECTED_INPUT_GENERATORS,
        EXPECTED_RETAINED_GENERATORS,
        EXPECTED_REMOVALS,
        EXPECTED_ENTRIES,
    ):
        raise AssertionError("certified node-7 closure shape drift")
    return closure


def certified_node7_execute(
    descriptor: dict,
    sequence_index: int,
    left_state: dict,
    right_state: dict,
    scaffold_record: dict,
    writers: dict,
    cumulative: list[int],
    frontier_artifact: dict,
    up_k_artifact: dict,
) -> tuple[dict, dict]:
    if int(descriptor["node_id"]) != NODE7_ID:
        raise AssertionError("certified node-7 executor called on another node")
    if digest(descriptor) != EXPECTED_NODE7_DESCRIPTOR_DIGEST:
        raise AssertionError("node-7 topology descriptor drift")
    if left_state["output_receipt"]["receipt_digest"] != EXPECTED_NODE6_RECEIPT_DIGEST:
        raise AssertionError("node-7 left child receipt drift")
    if (
        len(left_state["closure"]["entries"]),
        len(right_state["closure"]["entries"]),
    ) != (468, 36):
        raise AssertionError("node-7 live child entry inventory drift")

    ambient = int(scaffold_record["d"])
    blocks = [tuple(block) for block in scaffold_record["whole_factor_blocks"]]
    offsets = [int(value) for value in scaffold_record["affine_offsets"]]
    order = tuple(int(value) for value in scaffold_record["scaffold_order"])
    left_ids = tuple(int(value) for value in descriptor["left_factor_ids"])
    right_ids = tuple(int(value) for value in descriptor["right_factor_ids"])
    covered_ids = tuple(int(value) for value in descriptor["covered_factor_ids"])
    outside_ids = tuple(int(value) for value in descriptor["outside_factor_ids"])
    left_boundary = tuple(left_state["boundary"])
    right_boundary = tuple(right_state["boundary"])
    common = engine.xor_basis((*left_boundary, *right_boundary), ambient)
    parent = engine.boundary(
        [blocks[index] for index in covered_ids],
        [blocks[index] for index in outside_ids],
        ambient,
    )
    if (
        list(left_boundary),
        list(right_boundary),
        list(common),
        list(parent),
    ) != ([4, 2], [6], [4, 2], [4, 2]):
        raise AssertionError("node-7 frozen boundary geometry drift")

    left_digest = canonical_trajectory_set_digest(left_state["closure"]["entries"])
    if left_digest != EXPECTED_LEFT_TRAJECTORY_SET_DIGEST:
        raise AssertionError("node-7 live left trajectory set drift")
    transported_right = [
        frontier.transport_trajectory(
            item["trajectory"], right_boundary, parent, ambient
        )
        for item in right_state["closure"]["entries"]
    ]
    right_digest = digest(sorted(transported_right, key=canonical_json))
    if right_digest != EXPECTED_RIGHT_TRAJECTORY_SET_DIGEST:
        raise AssertionError("node-7 live right trajectory set drift")

    closure = certified_node7_closure(up_k_artifact)
    proof = up_k_artifact["proof_payload"]
    zero_by_class = {
        item["class_id"]: copy.deepcopy(item["zero_envelope"])
        for item in frontier_artifact["quotient_frontier"]["classes"]
    }
    expected_generators = [
        zero_by_class[class_id] for class_id in proof["retained_class_ids"]
    ]
    if closure["input_generators"] != expected_generators:
        raise AssertionError("node-7 closure generators differ from frontier classes")

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
    left_transport = engine.boundary_transport(left_boundary, common, ambient)
    right_transport = engine.boundary_transport(right_boundary, common, ambient)
    shrink_transport = engine.boundary_transport(parent, common, ambient)
    left_augmented = engine.subspace_sum(
        engine.span_for_ids(blocks, left_ids, ambient), common, ambient
    )
    right_augmented = engine.subspace_sum(
        engine.span_for_ids(blocks, right_ids, ambient), common, ambient
    )
    join_intersection = engine.subspace_intersection(
        left_augmented, right_augmented, ambient
    )
    if join_intersection != common:
        raise AssertionError("node-7 certified join side condition drift")

    starts = {
        kind: writer.record_count + len(writer.buffer)
        for kind, writer in writers.items()
    }
    actual_frontier_work = sum(
        int(value)
        for key, value in frontier_artifact["work_ledger"].items()
        if key != "naive_work_avoided"
    )
    closure_work = int(closure["ledger"]["certified_total_charged_operations"])
    certified_work = actual_frontier_work + closure_work
    cumulative_start = cumulative[0]
    cumulative[0] += certified_work
    receipt = engine.output_receipt(
        NODE7_ID,
        descriptor["kind"],
        covered_ids,
        parent,
        closure,
        partition_digest,
    )
    ends = {
        kind: writer.record_count + len(writer.buffer)
        for kind, writer in writers.items()
    }
    input_provenance = [
        {
            "input_generator_index": index,
            "class_id": class_id,
            "frontier_zero_envelope_digest": frontier_artifact[
                "quotient_frontier"
            ]["classes"][index]["zero_envelope_digest"],
        }
        for index, class_id in enumerate(proof["retained_class_ids"])
    ]
    retained_provenance = [
        {
            "retained_generator_index": index,
            "class_id": class_id,
        }
        for index, class_id in enumerate(proof["retained_class_ids"])
    ]
    entry_provenance = [
        {
            "entry_index": index,
            "source_generator_index": int(item["source_generator_index"]),
            "source_class_id": item["source_class_id"],
        }
        for index, item in enumerate(closure["entries"])
    ]
    node = {
        "node_id": NODE7_ID,
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
            "left_child_to_common": left_transport,
            "right_child_to_common": right_transport,
            "parent_in_common_for_shrink": shrink_transport,
        },
        "side_conditions": {
            "expand": {
                "left": {
                    "required_child_boundary": list(left_boundary),
                    "satisfied": True,
                },
                "right": {
                    "required_child_boundary": list(right_boundary),
                    "satisfied": True,
                },
            },
            "join": {
                "left_augmented_span": list(left_augmented),
                "right_augmented_span": list(right_augmented),
                "intersection": list(join_intersection),
                "required_common_boundary": list(common),
                "satisfied": True,
            },
            "shrink": {
                "parent_contained_in_common": True,
                "parent_basis_in_common_coordinates": shrink_transport[
                    "child_basis_in_parent_coordinates"
                ],
            },
        },
        "record_ranges": {
            kind.lower(): engine.make_range(starts[kind], ends[kind])
            for kind in writers
        },
        "node_up_k": closure,
        "input_generator_provenance": input_provenance,
        "retained_generator_provenance": retained_provenance,
        "entry_provenance": entry_provenance,
        "output_receipt": receipt,
        "work_ledger": {
            "cumulative_work_at_node_start": cumulative_start,
            "cumulative_work_before_node_b2": cumulative_start + actual_frontier_work,
            "node_b2_breakdown": {
                "certified_frontier_structural_work": actual_frontier_work,
                "certified_node7_up_k_work": closure_work,
            },
            "node_b2_work_delta": certified_work,
            "cumulative_work_at_node_end": cumulative[0],
            "monotone_by_construction": True,
        },
        "audit": {
            "child_full_set_entries": [468, 36],
            "child_pairs_processed": 0,
            "lattice_paths_processed": 0,
            "successful_refinements": 0,
            "failed_refinements": 0,
            "raw_precompact_join_statistics": 0,
            "unique_successful_generators": EXPECTED_INPUT_GENERATORS,
            "duplicate_successful_outputs_deleted": 0,
            "b2_dominance_deletions": EXPECTED_REMOVALS,
            "retained_generators": EXPECTED_RETAINED_GENERATORS,
            "final_up_k_entries": EXPECTED_ENTRIES,
            "cumulative_work_delta": certified_work,
            "certified_naive_child_pairs_covered": 16848,
            "certified_naive_refinements_covered": 9744432,
            "certified_quotient_classes": 13,
            "certified_direct_reachable_entries": EXPECTED_ENTRIES,
            "generic_pair_enumeration_bypassed": True,
            "generic_fine_refinement_enumeration_bypassed": True,
        },
        "certified_bridge": {
            "frontier_artifact_sha256": EXPECTED_FRONTIER_SHA256,
            "frontier_semantic_digest": EXPECTED_FRONTIER_SEMANTIC_DIGEST,
            "up_k_artifact_sha256": EXPECTED_UP_K_SHA256,
            "up_k_semantic_digest": EXPECTED_UP_K_SEMANTIC_DIGEST,
            "source_node6_receipt_digest": EXPECTED_NODE6_RECEIPT_DIGEST,
            "left_trajectory_set_digest": left_digest,
            "right_trajectory_set_digest": right_digest,
            "executor_intercept_scope": "NODE_ID_7_ONLY",
        },
    }
    node["node_execution_digest"] = digest(node)
    state = {
        "node_id": NODE7_ID,
        "covered_factor_ids": list(covered_ids),
        "boundary": list(parent),
        "closure": closure,
        "output_receipt": receipt,
    }
    return node, state


def build(
    prefix_root: Path,
    node6_hardening_path: Path,
    frontier_path: Path,
    up_k_path: Path,
    output_dir: Path,
    parent_pair_cap: int = DEFAULT_PAIR_CAP,
    parent_refinement_cap: int = DEFAULT_REFINEMENT_CAP,
) -> dict:
    frontier_artifact, up_k_artifact = load_artifacts(frontier_path, up_k_path)
    prefix_manifest, node6_artifact, prefix_records = (
        node6_integration.load_frozen_hardening(
            prefix_root, node6_hardening_path
        )
    )

    original_selected = engine.selected_scaffold
    original_up_k = engine.up_k_closure
    original_execute = engine.execute_node
    original_cap = engine.CAP
    original_capability = dict(engine.DEFAULT_CAPABILITY)
    node6_calls: list[dict] = []
    node7_calls: list[dict] = []

    def integrated_up_k(generators, ambient_dim, k, ledger):
        if (
            int(ambient_dim) == node6_integration.EXPECTED_AMBIENT_DIM
            and int(k) == node6_integration.EXPECTED_K
            and len(generators) == node6_integration.EXPECTED_INPUT_GENERATORS
        ):
            if node6_calls:
                raise AssertionError("certified node-6 closure invoked more than once")
            closure = node6_integration.certified_closure(
                generators,
                ambient_dim,
                k,
                node6_artifact,
                prefix_records,
            )
            node6_calls.append(
                {
                    "node_id": NODE6_ID,
                    "entry_count": int(closure["entry_count"]),
                    "family_digest": closure["input_generator_family_digest"],
                }
            )
            return closure
        return original_up_k(generators, ambient_dim, k, ledger)

    def integrated_execute(
        descriptor,
        sequence_index,
        left_state,
        right_state,
        scaffold_record,
        writers,
        cumulative,
        capability,
    ):
        if int(descriptor["node_id"]) == NODE7_ID:
            if node7_calls:
                raise AssertionError("certified node-7 bridge invoked more than once")
            node, state = certified_node7_execute(
                descriptor,
                sequence_index,
                left_state,
                right_state,
                scaffold_record,
                writers,
                cumulative,
                frontier_artifact,
                up_k_artifact,
            )
            node7_calls.append(
                {
                    "node_id": NODE7_ID,
                    "entry_count": int(node["node_up_k"]["entry_count"]),
                    "output_receipt_digest": node["output_receipt"]["receipt_digest"],
                    "node_execution_digest": node["node_execution_digest"],
                }
            )
            return node, state
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
        engine.selected_scaffold = negative.selected_negative_scaffold
        engine.up_k_closure = integrated_up_k
        engine.execute_node = integrated_execute
        engine.CAP = node6_integration.GENERIC_B2_CAP
        engine.DEFAULT_CAPABILITY["max_child_pairs_per_node"] = int(parent_pair_cap)
        engine.DEFAULT_CAPABILITY["max_refinements_per_node"] = int(
            parent_refinement_cap
        )
        manifest = engine.build(
            output_dir,
            max_refinements_per_node=int(parent_refinement_cap),
        )
    finally:
        engine.selected_scaffold = original_selected
        engine.up_k_closure = original_up_k
        engine.execute_node = original_execute
        engine.CAP = original_cap
        engine.DEFAULT_CAPABILITY.clear()
        engine.DEFAULT_CAPABILITY.update(original_capability)

    if len(node6_calls) != 1 or len(node7_calls) != 1:
        raise AssertionError("certified bridge invocation count drift")
    if manifest["execution"]["processed_internal_node_ids"] != [NODE6_ID, NODE7_ID]:
        raise AssertionError("executor did not complete exactly nodes 6 and 7")
    stop = manifest["execution"]["stop"]
    if (
        int(stop["node_id"]),
        stop["reason"],
        int(stop["required"]),
        int(stop["cap"]),
        stop["no_layout_at_cap"],
    ) != (
        NODE8_ID,
        "CHILD_PAIR_CAP_EXCEEDED",
        EXPECTED_NODE8_PAIRS,
        int(parent_pair_cap),
        False,
    ):
        raise AssertionError("node-8 honest capacity boundary drift")
    node7 = next(
        item for item in manifest["node_results"] if int(item["node_id"]) == NODE7_ID
    )
    if node7["node_up_k"]["closure_method"] != (
        "CERTIFIED_NODE7_THIRTEEN_GENERATOR_REACHABLE_CATALOG"
    ):
        raise AssertionError("node-7 certified closure method missing")
    right_leaf = manifest["leaf_full_sets"][3]["full_set"]["entries"]
    if len(right_leaf) != EXPECTED_NODE8_RIGHT_ENTRIES:
        raise AssertionError("node-8 right leaf entry inventory drift")
    refinement_total = sum(
        delannoy_path_count(
            len(left["trajectory"]),
            len(right["trajectory"]),
        )
        for left in node7["node_up_k"]["entries"]
        for right in right_leaf
    )
    if refinement_total != EXPECTED_NODE8_NAIVE_REFINEMENTS:
        raise AssertionError("node-8 exact naive refinement count drift")

    summary = {
        "schema": SCHEMA,
        "source": {
            "prefix_manifest_digest": prefix_manifest["manifest_digest"],
            "node6_hardening_sha256": node6_integration.EXPECTED_HARDENING_SHA256,
            "node7_frontier_sha256": EXPECTED_FRONTIER_SHA256,
            "node7_frontier_semantic_digest": EXPECTED_FRONTIER_SEMANTIC_DIGEST,
            "node7_up_k_sha256": EXPECTED_UP_K_SHA256,
            "node7_up_k_semantic_digest": EXPECTED_UP_K_SEMANTIC_DIGEST,
        },
        "certified_calls": {
            "node6": node6_calls,
            "node7": node7_calls,
        },
        "integrated_manifest_digest": manifest["manifest_digest"],
        "integrated_transcript_root_digest": manifest["chunking"][
            "transcript_root_digest"
        ],
        "execution": copy.deepcopy(manifest["execution"]),
        "node7": {
            "node_execution_digest": node7["node_execution_digest"],
            "output_receipt": copy.deepcopy(node7["output_receipt"]),
            "input_generators": EXPECTED_INPUT_GENERATORS,
            "retained_generators": EXPECTED_RETAINED_GENERATORS,
            "removals": EXPECTED_REMOVALS,
            "up_k_entries": EXPECTED_ENTRIES,
        },
        "node8_preflight": {
            "left_entries": EXPECTED_ENTRIES,
            "right_entries": EXPECTED_NODE8_RIGHT_ENTRIES,
            "child_pairs_required": EXPECTED_NODE8_PAIRS,
            "naive_refinements_required": refinement_total,
            "configured_pair_cap": int(parent_pair_cap),
            "configured_refinement_cap": int(parent_refinement_cap),
            "parent_refinement_started": False,
            "no_layout_at_cap": False,
        },
        "result": "HONEST_OPEN_AT_NODE8_CHILD_PAIR_CAP_AFTER_CERTIFIED_NODE7_INTEGRATION",
        "strict_boundary": {
            "node7_parent_up_k_complete": True,
            "node7_integrated_into_bottom_up_executor": True,
            "node8_reached": True,
            "node8_parent_preflight_complete": True,
            "node8_parent_refinement_started": False,
            "negative_root_reached": False,
            "terminal_completeness_proved": False,
            "found_layout_enabled": False,
            "no_layout_at_cap_enabled": False,
            "current_global_terminal": TERMINAL,
            "p_vs_np": "OPEN",
        },
        "next_gate": "C049.1_B4.6.3_NODE8_PARENT_FRONTIER_STRUCTURAL_COMPRESSION",
    }
    summary["semantic_digest"] = digest(summary)
    (output_dir / "node7-integration-node8-preflight-summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print("JANUS_C049_1_B4_6_3_NODE7_UP_K_INTEGRATION = PASS")
    print("CERTIFIED_NODE6_CALLS =", len(node6_calls))
    print("CERTIFIED_NODE7_CALLS =", len(node7_calls))
    print("NODE7_UP_K_ENTRIES =", EXPECTED_ENTRIES)
    print("PROCESSED_INTERNAL_NODE_IDS =", manifest["execution"]["processed_internal_node_ids"])
    print("EXECUTION_STATUS =", manifest["execution"]["status"])
    print("STOP_NODE =", stop["node_id"])
    print("STOP_REASON =", stop["reason"])
    print("NODE8_CHILD_PAIRS_REQUIRED =", EXPECTED_NODE8_PAIRS)
    print("NODE8_NAIVE_REFINEMENTS_REQUIRED =", refinement_total)
    print("GLOBAL_TERMINAL =", TERMINAL)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("prefix_root", type=Path)
    parser.add_argument("node6_hardening", type=Path)
    parser.add_argument("node7_frontier", type=Path)
    parser.add_argument("node7_up_k", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--parent-pair-cap", type=int, default=DEFAULT_PAIR_CAP)
    parser.add_argument(
        "--parent-refinement-cap",
        type=int,
        default=DEFAULT_REFINEMENT_CAP,
    )
    args = parser.parse_args()
    build(
        args.prefix_root,
        args.node6_hardening,
        args.node7_frontier,
        args.node7_up_k,
        args.output_dir,
        args.parent_pair_cap,
        args.parent_refinement_cap,
    )


if __name__ == "__main__":
    main()
