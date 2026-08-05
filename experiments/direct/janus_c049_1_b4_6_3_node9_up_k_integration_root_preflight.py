#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence

import janus_c049_1_b4_6_3_node8_up_k_integration_node9_preflight as core

SCHEMA = "C049.1-B4.6.3-NODE9-UP-K-INTEGRATION-ROOT-PREFLIGHT-v1"
TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"
NODE9, ROOT = 9, 10
NODE9_INPUT, NODE9_RETAINED, NODE9_REMOVALS, NODE9_ENTRIES = 15, 2, 13, 252
ROOT_PAIRS, ROOT_REFINEMENTS = 9072, 4954128

NODE8_RECEIPT = "befcbb30de8d70ee9816bdf072b92e597cfd7052c7d7931d48190e8e53854b20"
LEAF4_RECEIPT = "44ae26d9a650353d6360027b08ad3738b9a0fed5bfd78fcfafb165e83dd0052f"
LEAF5_RECEIPT = "1e81398ee7d05a6312ea94154a7026df64e9bf739d3957180e2f11d723c9c528"
TRANSCRIPT_ROOT = "eb904e833b53cf5626af1eb28493f479f5f54f2066a8b5427cb7e3eb47f515d8"
NODE8_INTEGRATED_MANIFEST_DIGEST = "b46e56a20c714806b3475658aacd82f628c909c3b7dc1492db7adb504dcaf868"
NODE8_INTEGRATED_MANIFEST_SHA256 = "9553263dc70f7a962a7bd95af4d5d4eeea6e1cdab163c616817b97cfcc207d6b"

FRONTIER_SCHEMA = "C049.1-B4.6.3-NODE9-PARENT-FRONTIER-STRUCTURAL-COMPRESSION-v1"
FRONTIER_SHA = "6eefd8e31ba4808e5587475c2faa2c000fd0093da4de2c488db42d103c059890"
FRONTIER_SEM = "62e9178821fe56cbf094e8512dd20b687796c6fd87e08c0fea8ea833ef6c5e80"
UPK_SCHEMA = "C049.1-B4.6.3-NODE9-FIFTEEN-GENERATOR-UP-K-CLOSURE-v1"
UPK_SHA = "c6e369099ea2fdf6572409dab7ce6f5172d40543388b366ec37a821262c506e4"
UPK_SEM = "f90aa04716ca2fa9019449e19b5866ac443cf545253bb41ae212dd3c68212713"
INPUT_FAMILY_DIGEST = "027dcee32e45abb2864055877db5cc18d6402ae4361d4c2c276e87a2396f4d39"
RETAINED_FAMILY_DIGEST = "b8df3e1986bc8bd4d9058d6efc66aebe48153bfb43bd8b275e2b2f51f6752cb1"
REMOVALS_DIGEST = "9cf4385a49c4fddbc593fd8835ad791df36bf28d7170d100eb9b78c6826135a5"
REACHABLE_TRAJECTORIES_DIGEST = "d7970ed19cd149cd3d4609581cb592ef8e69d36739502bb4deb43c44df5092fe"
REACHABLE_RECORDS_DIGEST = "8a35d07ed7435b472ef2407dfc0c1e3a18d71c46d5efefbb72418eda3be26912"
REACHABLE_STREAM_SHA256 = "0c8a1aba19ecef370011a24c03059e73950c75fc849c0c995004e88641d010e6"


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def invariant_pass(vector: dict[str, Any], prefix: str) -> bool:
    return vector == {f"{prefix}-{index:02d}": "PASS" for index in range(1, 11)}


def trajectory_stream_digest(entries: Sequence[dict[str, Any]]) -> str:
    raw = b"".join(canonical_json(item["trajectory"]) + b"\n" for item in entries)
    return hashlib.sha256(raw).hexdigest()


def source_artifacts(frontier_path: Path, up_k_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    if file_sha256(frontier_path) != FRONTIER_SHA:
        raise AssertionError("node9 frontier byte binding")
    frontier = load(frontier_path)
    if frontier.get("schema") != FRONTIER_SCHEMA:
        raise AssertionError("node9 frontier schema")
    if frontier.get("semantic_digest_scope") != "proof_payload":
        raise AssertionError("node9 frontier semantic scope")
    if frontier.get("semantic_digest") != FRONTIER_SEM or digest(frontier["proof_payload"]) != FRONTIER_SEM:
        raise AssertionError("node9 frontier semantic binding")
    frontier_proof = frontier["proof_payload"]
    if frontier_proof.get("admit") is not True or not invariant_pass(frontier_proof.get("invariant_vector", {}), "N9-INV"):
        raise AssertionError("node9 frontier admission")
    if frontier_proof["source"]["integrated_manifest_digest"] != NODE8_INTEGRATED_MANIFEST_DIGEST:
        raise AssertionError("node9 frontier integrated manifest digest")
    if frontier_proof["source"]["integrated_manifest_file_sha256"] != NODE8_INTEGRATED_MANIFEST_SHA256:
        raise AssertionError("node9 frontier integrated manifest bytes")
    if frontier_proof["source"]["node8_output_receipt_digest"] != NODE8_RECEIPT:
        raise AssertionError("node9 frontier node8 receipt")
    quotient = frontier_proof["quotient_frontier"]
    if (
        quotient["post_shrink_successful_class_count"],
        quotient["successful_quotient_path_count"],
        quotient["universal_failed_quotient_path_count"],
        quotient["failed_refinement_partition_complete"],
    ) != (NODE9_INPUT, 118, 64, True):
        raise AssertionError("node9 frontier boundary")

    if file_sha256(up_k_path) != UPK_SHA:
        raise AssertionError("node9 up_k byte binding")
    up_k = load(up_k_path)
    if up_k.get("schema") != UPK_SCHEMA:
        raise AssertionError("node9 up_k schema")
    if up_k.get("semantic_digest_scope") != "proof_payload":
        raise AssertionError("node9 up_k semantic scope")
    if up_k.get("semantic_digest") != UPK_SEM or digest(up_k["proof_payload"]) != UPK_SEM:
        raise AssertionError("node9 up_k semantic binding")
    proof = up_k["proof_payload"]
    if proof.get("admit") is not True or not invariant_pass(proof.get("invariant_vector", {}), "N9U-INV"):
        raise AssertionError("node9 up_k admission")
    source = proof["source"]
    if (
        source["frontier_schema"],
        source["frontier_artifact_sha256"],
        source["frontier_semantic_digest"],
        source["frontier_generator_count"],
    ) != (FRONTIER_SCHEMA, FRONTIER_SHA, FRONTIER_SEM, NODE9_INPUT):
        raise AssertionError("node9 up_k source binding")
    family = proof["input_generator_family"]
    minimization = proof["minimization"]
    reachable = proof["reachable_closure"]
    if (family["generator_count"], family["generator_family_digest"], digest(family["generators"])) != (
        NODE9_INPUT,
        INPUT_FAMILY_DIGEST,
        INPUT_FAMILY_DIGEST,
    ):
        raise AssertionError("node9 input family")
    if (
        minimization["retained_generator_count"],
        minimization["direct_removal_count"],
        minimization["retained_family_digest"],
        digest(minimization["retained_generators"]),
        digest(minimization["direct_removals"]),
        minimization["every_removal_has_direct_retained_witness"],
        minimization["transitive_closure_used_for_removal"],
    ) != (
        NODE9_RETAINED,
        NODE9_REMOVALS,
        RETAINED_FAMILY_DIGEST,
        RETAINED_FAMILY_DIGEST,
        REMOVALS_DIGEST,
        True,
        False,
    ):
        raise AssertionError("node9 minimization")
    entries = reachable["entries"]
    if (
        reachable["complete_reachable_catalog"],
        reachable["reachable_entry_count"],
        reachable["reachable_entries_digest"],
        reachable["reachable_stream_sha256"],
        reachable["global_compact_universe_enumerated"],
        reachable["global_compact_universe_entry_count"],
        digest([item["trajectory"] for item in entries]),
        digest(entries),
        trajectory_stream_digest(entries),
    ) != (
        NODE9_ENTRIES,
        NODE9_ENTRIES,
        REACHABLE_TRAJECTORIES_DIGEST,
        REACHABLE_STREAM_SHA256,
        False,
        0,
        REACHABLE_TRAJECTORIES_DIGEST,
        REACHABLE_RECORDS_DIGEST,
        REACHABLE_STREAM_SHA256,
    ):
        raise AssertionError("node9 reachable closure")
    if proof["idempotence"].get("idempotent") is not True or proof["idempotence"]["repeated_closure_checks"] != 8400:
        raise AssertionError("node9 idempotence")
    return frontier_proof, proof


def certified_closure(proof: dict[str, Any], parent_basis: Sequence[int]) -> dict[str, Any]:
    if tuple(parent_basis) != (1,) or int(proof["ambient_dim"]) != 1 or int(proof["k"]) != 1:
        raise AssertionError("node9 parent coordinate binding")
    family = proof["input_generator_family"]
    minimization = proof["minimization"]
    reachable = proof["reachable_closure"]
    input_generators = [copy.deepcopy(item["trajectory"]) for item in family["generators"]]
    retained_generators = [copy.deepcopy(item["trajectory"]) for item in minimization["retained_generators"]]
    removals = copy.deepcopy(minimization["direct_removals"])
    entries = copy.deepcopy(reachable["entries"])
    for trajectory in (*input_generators, *retained_generators, *(item["trajectory"] for item in entries)):
        for statistic in trajectory:
            if any(int(value) != 1 for value in (*statistic["left"], *statistic["right"])):
                raise AssertionError("node9 trajectory outside parent coordinates")
    work_ledger = copy.deepcopy(proof["work_ledger"])
    work = sum(int(value) for value in work_ledger.values() if isinstance(value, int) and not isinstance(value, bool))
    closure = {
        "ambient_dim": 1,
        "k": 1,
        "input_generators": input_generators,
        "retained_generators": retained_generators,
        "removals": removals,
        "universe_size": NODE9_ENTRIES,
        "entries": entries,
        "entry_count": len(entries),
        "ledger": {
            "discovery_work": work,
            "work": 0,
            "certified_total_charged_operations": work,
        },
        "closure_method": "CERTIFIED_NODE9_TWO_GENERATOR_REACHABLE_CATALOG",
        "global_universe_enumerated": False,
        "complete_reachable_catalog_proved": True,
        "source_input_family_digest": INPUT_FAMILY_DIGEST,
        "source_retained_family_digest": RETAINED_FAMILY_DIGEST,
        "source_direct_removals_digest": REMOVALS_DIGEST,
        "frontier_artifact_sha256": FRONTIER_SHA,
        "up_k_artifact_sha256": UPK_SHA,
        "up_k_semantic_digest": UPK_SEM,
        "reachable_entries_digest": REACHABLE_TRAJECTORIES_DIGEST,
        "reachable_records_digest": REACHABLE_RECORDS_DIGEST,
        "reachable_catalog_stream_sha256": REACHABLE_STREAM_SHA256,
        "input_class_ids": [item["source_class_id"] for item in family["generators"]],
        "retained_class_ids": [item["source_class_id"] for item in minimization["retained_generators"]],
        "coordinate_parent_boundary_ambient": list(parent_basis),
        "coordinate_conversion": "IDENTITY_ALREADY_IN_NODE9_PARENT_COORDINATES",
        "invariant_vector": copy.deepcopy(proof["invariant_vector"]),
        "idempotence": copy.deepcopy(proof["idempotence"]),
        "admit": True,
    }
    if (
        len(input_generators),
        len(retained_generators),
        len(removals),
        len(entries),
    ) != (NODE9_INPUT, NODE9_RETAINED, NODE9_REMOVALS, NODE9_ENTRIES):
        raise AssertionError("node9 certified closure cardinality")
    return closure


def execute_node9(
    descriptor: dict[str, Any],
    sequence_index: int,
    left_state: dict[str, Any],
    right_state: dict[str, Any],
    scaffold_record: dict[str, Any],
    writers: dict[str, Any],
    cumulative: list[int],
    frontier_proof: dict[str, Any],
    up_k_proof: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    expected = {
        "node_id": 9,
        "kind": "SPINE_INTERNAL_JOIN",
        "edge_index": 3,
        "child_node_ids": [8, 4],
        "left_factor_ids": [0, 1, 2, 3],
        "right_factor_ids": [4],
        "covered_factor_ids": [0, 1, 2, 3, 4],
        "outside_factor_ids": [5],
    }
    if descriptor != expected or descriptor != frontier_proof["geometry"]["descriptor"]:
        raise AssertionError("node9 descriptor")
    if left_state["output_receipt"]["receipt_digest"] != NODE8_RECEIPT:
        raise AssertionError("node8 child receipt")
    if right_state["output_receipt"]["receipt_digest"] != LEAF4_RECEIPT:
        raise AssertionError("leaf4 child receipt")

    engine = core.engine
    ambient = int(scaffold_record["d"])
    blocks = [tuple(block) for block in scaffold_record["whole_factor_blocks"]]
    offsets = [int(value) for value in scaffold_record["affine_offsets"]]
    left_boundary = tuple(left_state["boundary"])
    right_boundary = tuple(right_state["boundary"])
    common = engine.xor_basis((*left_boundary, *right_boundary), ambient)
    parent = engine.boundary(
        [blocks[index] for index in descriptor["covered_factor_ids"]],
        [blocks[index] for index in descriptor["outside_factor_ids"]],
        ambient,
    )
    geometry = frontier_proof["geometry"]
    if [list(left_boundary), list(right_boundary), list(common), list(parent)] != [
        geometry["left_boundary"],
        geometry["right_boundary"],
        geometry["common_boundary"],
        geometry["parent_boundary"],
    ]:
        raise AssertionError("node9 geometry")
    if tuple(parent) != (1,) or geometry["shrink_is_identity"] is not False:
        raise AssertionError("node9 parent/shrink contract")

    partition = {
        "whole_factor_blocks": [list(block) for block in blocks],
        "affine_offsets": offsets,
        "scaffold_order": [int(value) for value in scaffold_record["scaffold_order"]],
        "child_node_ids": descriptor["child_node_ids"],
        "left_factor_ids": descriptor["left_factor_ids"],
        "right_factor_ids": descriptor["right_factor_ids"],
        "covered_factor_ids": descriptor["covered_factor_ids"],
        "outside_factor_ids": descriptor["outside_factor_ids"],
    }
    partition_digest = digest(partition)
    closure = certified_closure(up_k_proof, parent)
    starts = {kind: writer.record_count + len(writer.buffer) for kind, writer in writers.items()}
    work = int(closure["ledger"]["certified_total_charged_operations"])
    cumulative_start = cumulative[0]
    cumulative[0] += work
    receipt = engine.output_receipt(
        NODE9,
        descriptor["kind"],
        descriptor["covered_factor_ids"],
        parent,
        closure,
        partition_digest,
    )
    zero_ranges = {kind.lower(): engine.make_range(starts[kind], starts[kind]) for kind in writers}
    node = {
        "node_id": NODE9,
        "sequence_index": sequence_index,
        "kind": descriptor["kind"],
        "child_node_ids": descriptor["child_node_ids"],
        "left_factor_ids": descriptor["left_factor_ids"],
        "right_factor_ids": descriptor["right_factor_ids"],
        "covered_factor_ids": descriptor["covered_factor_ids"],
        "outside_factor_ids": descriptor["outside_factor_ids"],
        "covered_affine_offsets": [offsets[index] for index in descriptor["covered_factor_ids"]],
        "grouped_partition_preserved": True,
        "partition_receipt": partition,
        "partition_receipt_digest": partition_digest,
        "input_full_set_receipts": [copy.deepcopy(left_state["output_receipt"]), copy.deepcopy(right_state["output_receipt"])],
        "child_boundaries": {"left": list(left_boundary), "right": list(right_boundary)},
        "common_join_boundary": list(common),
        "parent_boundary": list(parent),
        "boundary_dimensions": {
            "children": [len(left_boundary), len(right_boundary)],
            "common": len(common),
            "parent": len(parent),
        },
        "transport_contracts": {
            "left_child_to_common": engine.boundary_transport(left_boundary, common, ambient),
            "right_child_to_common": engine.boundary_transport(right_boundary, common, ambient),
            "parent_in_common_for_shrink": engine.boundary_transport(parent, common, ambient),
        },
        "side_conditions": {
            "certified_by_frontier_artifact": True,
            "join_correction_counts_over_quotient_cells": copy.deepcopy(geometry["join_correction_counts_over_quotient_cells"]),
            "shrink_correction_counts_over_quotient_cells": copy.deepcopy(geometry["shrink_correction_counts_over_quotient_cells"]),
            "left_expand_identity": geometry["left_expand_identity"],
            "right_boundary_embedded_in_common": geometry["right_boundary_embedded_in_common"],
            "shrink_is_identity": geometry["shrink_is_identity"],
            "node9_parent_coordinate_identity_verified": True,
        },
        "record_ranges": zero_ranges,
        "node_up_k": closure,
        "input_generator_provenance": [
            {"input_generator_index": index, "source_class_id": class_id}
            for index, class_id in enumerate(closure["input_class_ids"])
        ],
        "retained_generator_provenance": [
            {"retained_generator_index": index, "source_class_id": class_id}
            for index, class_id in enumerate(closure["retained_class_ids"])
        ],
        "entry_provenance": [
            {
                "entry_index": index,
                "entry_id": entry["entry_id"],
                "source_retained_class_id": entry["source_retained_class_id"],
            }
            for index, entry in enumerate(closure["entries"])
        ],
        "output_receipt": receipt,
        "certified_structural_bridge": {
            "frontier_artifact_sha256": FRONTIER_SHA,
            "up_k_artifact_sha256": UPK_SHA,
            "frontier_classes": NODE9_INPUT,
            "retained_generators": NODE9_RETAINED,
            "direct_removals": NODE9_REMOVALS,
            "naive_child_pairs_covered": 574128,
            "naive_refinements_covered": 1284995408,
            "successful_quotient_paths": 118,
            "universal_failed_quotient_paths": 64,
            "generic_pair_records_materialized": 0,
            "generic_refinement_records_materialized": 0,
            "closure_entries_returned_to_executor": NODE9_ENTRIES,
            "reachable_trajectories_digest": REACHABLE_TRAJECTORIES_DIGEST,
            "reachable_records_digest": REACHABLE_RECORDS_DIGEST,
        },
        "work_ledger": {
            "cumulative_work_at_node_start": cumulative_start,
            "cumulative_work_before_node_b2": cumulative_start,
            "node_b2_breakdown": {"certified_node9_proof_work": work},
            "node_b2_work_delta": work,
            "cumulative_work_at_node_end": cumulative[0],
            "monotone_by_construction": True,
        },
        "audit": {
            "child_full_set_entries": [int(left_state["closure"]["entry_count"]), int(right_state["closure"]["entry_count"])],
            "child_pairs_processed": 0,
            "lattice_paths_processed": 0,
            "successful_refinements": 0,
            "failed_refinements": 0,
            "raw_precompact_join_statistics": 0,
            "unique_successful_generators": NODE9_INPUT,
            "duplicate_successful_outputs_deleted": 0,
            "b2_dominance_deletions": NODE9_REMOVALS,
            "retained_generators": NODE9_RETAINED,
            "final_up_k_entries": NODE9_ENTRIES,
            "cumulative_work_delta": work,
            "certified_child_pairs_covered": 574128,
            "certified_naive_refinements_covered": 1284995408,
            "certified_successful_quotient_paths": 118,
            "certified_universal_failed_quotient_paths": 64,
            "certified_reachability_witnesses": NODE9_ENTRIES,
        },
    }
    node["node_execution_digest"] = digest(node)
    state = {
        "node_id": NODE9,
        "covered_factor_ids": descriptor["covered_factor_ids"],
        "boundary": list(parent),
        "closure": closure,
        "output_receipt": receipt,
    }
    return node, state


def exact_refinements(left: Sequence[dict[str, Any]], right: Sequence[dict[str, Any]]) -> int:
    return sum(
        core.b44.delannoy_path_count(len(left_entry["trajectory"]), len(right_entry["trajectory"]))
        for left_entry in left
        for right_entry in right
    )


def length_histogram(entries: Sequence[dict[str, Any]]) -> dict[str, int]:
    result: dict[str, int] = {}
    for entry in entries:
        key = str(len(entry["trajectory"]))
        result[key] = result.get(key, 0) + 1
    return dict(sorted(result.items(), key=lambda item: int(item[0])))


def build(
    prefix_root: Path,
    hardening_path: Path,
    node7_frontier_path: Path,
    node7_up_k_path: Path,
    node8_frontier_path: Path,
    node8_up_k_path: Path,
    node9_frontier_path: Path,
    node9_up_k_path: Path,
    output_dir: Path,
    pair_cap: int = 10000,
    refinement_cap: int = 2000000,
) -> dict[str, Any]:
    prefix_manifest, hardening, hardening_records = core.node6.load_frozen_hardening(prefix_root, hardening_path)
    node7_frontier, node7_up_k = core.node7int.sources(node7_frontier_path, node7_up_k_path)
    node8_frontier, node8_up_k = core.source_artifacts(node8_frontier_path, node8_up_k_path)
    node9_frontier, node9_up_k = source_artifacts(node9_frontier_path, node9_up_k_path)

    engine = core.engine
    original_selected = engine.selected_scaffold
    original_up_k = engine.up_k_closure
    original_execute = engine.execute_node
    original_cap = engine.CAP
    original_capability = dict(engine.DEFAULT_CAPABILITY)
    calls: dict[str, list[str]] = {"node6": [], "node7": [], "node8": [], "node9": []}

    def patched_up_k(generators, ambient_dim, k, ledger):
        if int(ambient_dim) == 2 and int(k) == 1 and len(generators) == 468:
            if calls["node6"]:
                raise AssertionError("node6 certified closure called twice")
            closure = core.node6.certified_closure(generators, ambient_dim, k, hardening, hardening_records)
            calls["node6"].append(closure["reachable_entries_digest"])
            return closure
        return original_up_k(generators, ambient_dim, k, ledger)

    def patched_execute(descriptor, sequence_index, left_state, right_state, scaffold_record, writers, cumulative, capability):
        node_id = int(descriptor["node_id"])
        if node_id == 7:
            if calls["node7"]:
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
            calls["node7"].append(result[0]["output_receipt"]["receipt_digest"])
            return result
        if node_id == 8:
            if calls["node8"]:
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
            calls["node8"].append(result[0]["output_receipt"]["receipt_digest"])
            return result
        if node_id == 9:
            if calls["node9"]:
                raise AssertionError("node9 certified bridge called twice")
            result = execute_node9(
                descriptor,
                sequence_index,
                left_state,
                right_state,
                scaffold_record,
                writers,
                cumulative,
                node9_frontier,
                node9_up_k,
            )
            calls["node9"].append(result[0]["output_receipt"]["receipt_digest"])
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
        engine.DEFAULT_CAPABILITY["max_refinements_per_node"] = int(refinement_cap)
        manifest = engine.build(output_dir, max_refinements_per_node=int(refinement_cap))
    finally:
        engine.selected_scaffold = original_selected
        engine.up_k_closure = original_up_k
        engine.execute_node = original_execute
        engine.CAP = original_cap
        engine.DEFAULT_CAPABILITY.clear()
        engine.DEFAULT_CAPABILITY.update(original_capability)

    if {key: len(value) for key, value in calls.items()} != {"node6": 1, "node7": 1, "node8": 1, "node9": 1}:
        raise AssertionError("certified bridge call vector")
    execution = manifest["execution"]
    if execution["processed_internal_node_ids"] != [6, 7, 8, 9]:
        raise AssertionError("processed node vector")
    stop = execution["stop"]
    if (
        int(stop["node_id"]),
        stop["reason"],
        int(stop["required"]),
        int(stop["cap"]),
        stop["no_layout_at_cap"],
        stop["terminal"],
    ) != (ROOT, "REFINEMENT_CAP_EXCEEDED", ROOT_REFINEMENTS, int(refinement_cap), False, TERMINAL):
        raise AssertionError("root preflight stop")
    if manifest["chunking"]["transcript_root_digest"] != TRANSCRIPT_ROOT:
        raise AssertionError("transcript root changed")

    node9 = next(item for item in manifest["node_results"] if int(item["node_id"]) == NODE9)
    closure = node9["node_up_k"]
    if (
        closure["entry_count"],
        closure["reachable_entries_digest"],
        closure["reachable_records_digest"],
        len(closure["input_generators"]),
        len(closure["retained_generators"]),
        len(closure["removals"]),
    ) != (
        NODE9_ENTRIES,
        REACHABLE_TRAJECTORIES_DIGEST,
        REACHABLE_RECORDS_DIGEST,
        NODE9_INPUT,
        NODE9_RETAINED,
        NODE9_REMOVALS,
    ):
        raise AssertionError("node9 integrated state")
    if any(int(value["count"]) for value in node9["record_ranges"].values()):
        raise AssertionError("generic node9 transcript materialized")

    leaf5 = manifest["leaf_full_sets"][5]
    if leaf5["output_receipt"]["receipt_digest"] != LEAF5_RECEIPT:
        raise AssertionError("leaf5 receipt")
    left_entries = closure["entries"]
    right_entries = leaf5["full_set"]["entries"]
    pair_count = len(left_entries) * len(right_entries)
    refinement_count = exact_refinements(left_entries, right_entries)
    if (pair_count, refinement_count) != (ROOT_PAIRS, ROOT_REFINEMENTS):
        raise AssertionError("root exact frontier")

    topology_root = next(item for item in manifest["topology"]["internal_nodes"] if int(item["node_id"]) == ROOT)
    expected_root = {
        "node_id": 10,
        "kind": "SYNTHETIC_ROOT_CLOSE",
        "edge_index": 4,
        "child_node_ids": [9, 5],
        "left_factor_ids": [0, 1, 2, 3, 4],
        "right_factor_ids": [5],
        "covered_factor_ids": [0, 1, 2, 3, 4, 5],
        "outside_factor_ids": [],
    }
    if topology_root != expected_root:
        raise AssertionError("root descriptor")
    blocks = [tuple(block) for block in manifest["scaffold_case"]["whole_factor_blocks"]]
    left_boundary = tuple(node9["parent_boundary"])
    right_boundary = tuple(leaf5["boundary_rref_ambient"])
    common = engine.xor_basis((*left_boundary, *right_boundary), 3)
    parent = engine.boundary([blocks[index] for index in range(6)], [], 3)
    if (left_boundary, right_boundary, common, parent) != ((1,), (1,), (1,), ()):
        raise AssertionError("root geometry")

    summary = {
        "schema": SCHEMA,
        "source": {
            "prefix_manifest_digest": prefix_manifest["manifest_digest"],
            "hardening_artifact_sha256": core.node6.EXPECTED_HARDENING_SHA256,
            "node7_frontier_artifact_sha256": core.node7int.FRONTIER_SHA,
            "node7_up_k_artifact_sha256": core.node7int.UPK_SHA,
            "node8_frontier_artifact_sha256": core.FRONTIER_SHA,
            "node8_up_k_artifact_sha256": core.UPK_SHA,
            "node9_frontier_artifact_sha256": FRONTIER_SHA,
            "node9_frontier_semantic_digest": FRONTIER_SEM,
            "node9_up_k_artifact_sha256": UPK_SHA,
            "node9_up_k_semantic_digest": UPK_SEM,
        },
        "certified_calls": {key: 1 for key in sorted(calls)},
        "integrated_manifest_digest": manifest["manifest_digest"],
        "integrated_transcript_root_digest": manifest["chunking"]["transcript_root_digest"],
        "node9": {
            "node_execution_digest": node9["node_execution_digest"],
            "output_receipt_digest": node9["output_receipt"]["receipt_digest"],
            "input_generators": NODE9_INPUT,
            "retained_generators": NODE9_RETAINED,
            "direct_removals": NODE9_REMOVALS,
            "up_k_entries": NODE9_ENTRIES,
            "reachable_trajectories_digest": REACHABLE_TRAJECTORIES_DIGEST,
            "reachable_records_digest": REACHABLE_RECORDS_DIGEST,
            "generic_pair_records_materialized": 0,
            "generic_refinement_records_materialized": 0,
        },
        "root_preflight": {
            "root_node_id": ROOT,
            "left_child_node_id": NODE9,
            "right_child_node_id": 5,
            "left_entry_count": len(left_entries),
            "right_entry_count": len(right_entries),
            "child_pair_count": pair_count,
            "naive_refinement_count": refinement_count,
            "left_length_histogram": length_histogram(left_entries),
            "right_length_histogram": length_histogram(right_entries),
            "left_boundary": list(left_boundary),
            "right_boundary": list(right_boundary),
            "common_boundary": list(common),
            "parent_boundary": list(parent),
            "left_expand_identity": common == left_boundary,
            "right_expand_identity": common == right_boundary,
            "shrink_identity": common == parent,
            "pair_cap": int(pair_cap),
            "refinement_cap": int(refinement_cap),
            "pair_cap_exceeded": pair_count > int(pair_cap),
            "refinement_cap_exceeded": refinement_count > int(refinement_cap),
            "stop_reason": stop["reason"],
            "generic_root_pair_records_materialized": 0,
            "generic_root_refinement_records_materialized": 0,
            "no_layout_at_cap": False,
        },
        "execution": copy.deepcopy(execution),
        "result": "HONEST_OPEN_AT_ROOT_REFINEMENT_CAPACITY",
        "strict_boundary": {
            "node9_parent_up_k_admitted": True,
            "node9_integrated_into_bottom_up_executor": True,
            "node9_generic_cartesian_replay_required": False,
            "root_reached": True,
            "root_parent_refinement_started": True,
            "root_parent_refinement_complete": False,
            "root_parent_up_k_complete": False,
            "root_full_set_computed": False,
            "negative_root_reached": False,
            "terminal_completeness_proved": False,
            "found_layout_enabled": False,
            "no_layout_at_cap_enabled": False,
            "current_global_terminal": TERMINAL,
            "p_vs_np": "OPEN",
        },
        "next_gate": "C049.1_B4.6.3_ROOT_PARENT_FRONTIER_STRUCTURAL_COMPRESSION",
    }
    summary["semantic_digest"] = digest(summary)
    summary_path = output_dir / "node9-integration-root-preflight-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print("JANUS_C049_1_B4_6_3_NODE9_UP_K_INTEGRATION = PASS")
    print("PROCESSED_INTERNAL_NODE_IDS =", execution["processed_internal_node_ids"])
    print("NODE9_INPUT_GENERATORS =", NODE9_INPUT)
    print("NODE9_RETAINED_GENERATORS =", NODE9_RETAINED)
    print("NODE9_DIRECT_REMOVALS =", NODE9_REMOVALS)
    print("NODE9_UP_K_ENTRIES =", NODE9_ENTRIES)
    print("NODE9_OUTPUT_RECEIPT =", node9["output_receipt"]["receipt_digest"])
    print("ROOT_CHILD_PAIRS_REQUIRED =", pair_count)
    print("ROOT_NAIVE_REFINEMENTS_REQUIRED =", refinement_count)
    print("STOP_NODE =", stop["node_id"])
    print("STOP_REASON =", stop["reason"])
    print("MANIFEST_DIGEST =", manifest["manifest_digest"])
    print("SUMMARY_SEMANTIC_DIGEST =", summary["semantic_digest"])
    print("GLOBAL_TERMINAL =", TERMINAL)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("prefix_root", type=Path)
    parser.add_argument("hardening_artifact", type=Path)
    parser.add_argument("node7_frontier_artifact", type=Path)
    parser.add_argument("node7_up_k_artifact", type=Path)
    parser.add_argument("node8_frontier_artifact", type=Path)
    parser.add_argument("node8_up_k_artifact", type=Path)
    parser.add_argument("node9_frontier_artifact", type=Path)
    parser.add_argument("node9_up_k_artifact", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--root-pair-cap", type=int, default=10000)
    parser.add_argument("--root-refinement-cap", type=int, default=2000000)
    args = parser.parse_args()
    build(
        args.prefix_root,
        args.hardening_artifact,
        args.node7_frontier_artifact,
        args.node7_up_k_artifact,
        args.node8_frontier_artifact,
        args.node8_up_k_artifact,
        args.node9_frontier_artifact,
        args.node9_up_k_artifact,
        args.output_dir,
        args.root_pair_cap,
        args.root_refinement_cap,
    )


if __name__ == "__main__":
    main()
