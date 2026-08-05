#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence

import janus_c049_1_b4_4_nonzero_boundary_node_full_set as b44
import janus_c049_1_b4_5_bottom_up_scaffold_executor as engine
import janus_c049_1_b4_6_3_negative_root_engine_replay as negative
import janus_c049_1_b4_6_3_node6_up_k_integration_parent_refinement as node6
import janus_c049_1_b4_6_3_node7_up_k_integration_node8_preflight as node7int

SCHEMA = "C049.1-B4.6.3-NODE8-UP-K-INTEGRATION-NODE9-PREFLIGHT-v1"
TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"
N8, N9, ROOT = 8, 9, 10
N8_INPUT, N8_RETAINED, N8_REMOVALS, N8_ENTRIES = 61, 28, 33, 15948
N9_PAIRS, N9_REFINEMENTS = 574128, 1284995408

NODE7_RECEIPT = "838e4dfde9740585928b5498e18a5b0836f44da1d822c060d5c59b7d52177011"
LEAF3_RECEIPT = "80f424b87fd39e80013e1bb96b3dcec47d281a322f9964472b2ca32bd039e086"
LEAF4_RECEIPT = "44ae26d9a650353d6360027b08ad3738b9a0fed5bfd78fcfafb165e83dd0052f"
TRANSCRIPT_ROOT = "eb904e833b53f5626af1eb28493f479f5f54f2066a8b5427cb7e3eb47f515d8"
NODE7_INTEGRATED_MANIFEST_DIGEST = "c1b34fe2e47a1566b9cde045dd28fbdafdd30780de834b6d0bdb8731b11a00d6"

FRONTIER_SHA = "93dcd5610eb9df079823b172a4f824ce1c09859e759c6b771dc95b99af394d34"
FRONTIER_SEM = "209f5a013ec492b67066abc3dcf08af183d2ec5ec0000f3d8d03a033cb32f9db"
UPK_SHA = "e5202b9eb32ef44b1fdf493c6848ec82f8ce16fa502e623b7fbfdeb6bc735620"
UPK_SEM = "cf4794e6ccc4591e9bf57ccb4256a42c20bca8fba86658350f762f21f1019090"
INPUT_FAMILY_DIGEST = "7f4a73f3a6278de6f02c3b3eb9222bd420972be7f474bbecd6da9a5b6115a395"
RETAINED_FAMILY_DIGEST = "ed1e5ce272bc3202a8e3203fdb108dcbb9ef1dfe9f355e1f8229ba9bf498d298"
SOURCE_ENTRIES_DIGEST = "1f37d96c5c16684057253ad109db9488e726bb4aed65745c966af520d13ac609"
SOURCE_STREAM_DIGEST = "3cde1e7ef5274cdc3e94179533546263e4e0223050225560860adeb7e3a28483"
COORDINATE_ENTRIES_DIGEST = "6030bb93f1298bf26f4c76d00bbc392dc0a6dd69dd4c1552691c55382fba7468"
COORDINATE_STREAM_DIGEST = "ddfa4717bda8c177b2014ec22fed6882be985e1dfbfec46701f933b01d2232f4"
COORDINATE_INPUT_DIGEST = "b5653fad52b8ba2899c27000bf86a1b496ab9e3ec5cc858b283aa4c7156b841e"
COORDINATE_RETAINED_DIGEST = "2da701dffb5bad4872459d5c2ab21b370f04c92a8b9e01f5a06252bb68d5df39"
COORDINATE_REMOVALS_DIGEST = "70e7cf110e735d10dee3f3895e261ad45c53dd6ce4e79a5cae9ea38fdba41545"


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def pass10(vector: dict) -> bool:
    return len(vector) == 10 and set(vector.values()) == {"PASS"}


def source_artifacts(frontier_path: Path, up_k_path: Path) -> tuple[dict, dict]:
    frontier = load(frontier_path)
    up_k = load(up_k_path)
    if file_sha256(frontier_path) != FRONTIER_SHA:
        raise AssertionError("node8 frontier byte binding")
    if frontier.get("schema") != "C049.1-B4.6.3-NODE8-PARENT-FRONTIER-STRUCTURAL-COMPRESSION-v1":
        raise AssertionError("node8 frontier schema")
    if frontier.get("semantic_digest") != FRONTIER_SEM or frontier.get("semantic_digest_scope") != "proof_payload":
        raise AssertionError("node8 frontier semantic binding")
    frontier_proof = frontier["proof_payload"]
    if frontier_proof.get("admit") is not True or not pass10(frontier_proof.get("invariant_vector", {})):
        raise AssertionError("node8 frontier admission")
    if frontier_proof["quotient_frontier"]["post_shrink_class_count"] != N8_INPUT:
        raise AssertionError("node8 frontier cardinality")

    if file_sha256(up_k_path) != UPK_SHA:
        raise AssertionError("node8 up_k byte binding")
    if up_k.get("schema") != "C049.1-B4.6.3-NODE8-SIXTY-ONE-GENERATOR-UP-K-CLOSURE-v1":
        raise AssertionError("node8 up_k schema")
    if up_k.get("semantic_digest") != UPK_SEM or up_k.get("semantic_digest_scope") != "proof_payload":
        raise AssertionError("node8 up_k semantic binding")
    proof = up_k["proof_payload"]
    if proof.get("admit") is not True or not pass10(proof.get("invariant_vector", {})):
        raise AssertionError("node8 up_k admission")
    if proof["source"] != {
        "artifact_sha256": FRONTIER_SHA,
        "post_shrink_class_count": N8_INPUT,
        "schema": frontier["schema"],
        "semantic_digest": FRONTIER_SEM,
    }:
        raise AssertionError("node8 up_k source binding")
    family = proof["input_family"]
    minimization = proof["preorder_minimization"]
    reachable = proof["reachable_closure"]
    if (family["generator_count"], family["family_digest"]) != (N8_INPUT, INPUT_FAMILY_DIGEST):
        raise AssertionError("node8 input family")
    if (
        minimization["retained_generator_count"],
        minimization["direct_removal_count"],
        minimization["retained_family_digest"],
        minimization["all_removals_direct"],
        minimization["transitive_closure_used"],
    ) != (N8_RETAINED, N8_REMOVALS, RETAINED_FAMILY_DIGEST, True, False):
        raise AssertionError("node8 minimization")
    if (
        reachable["complete_reachable_catalog"],
        reachable["reachable_entry_count"],
        reachable["reachable_entries_digest"],
        reachable["reachable_stream_sha256"],
        reachable["global_compact_universe_enumerated"],
        reachable["global_universe_entries_enumerated"],
    ) != (N8_ENTRIES, N8_ENTRIES, SOURCE_ENTRIES_DIGEST, SOURCE_STREAM_DIGEST, False, 0):
        raise AssertionError("node8 reachable closure")
    if digest(reachable["entries"]) != SOURCE_ENTRIES_DIGEST:
        raise AssertionError("node8 reachable payload")
    return frontier_proof, proof


def ambient_vector_to_coordinate(vector: int, parent_basis: Sequence[int]) -> int:
    theta = len(parent_basis)
    for coordinate in range(1 << theta):
        ambient = 0
        for index, basis_vector in enumerate(parent_basis):
            if coordinate & (1 << (theta - 1 - index)):
                ambient ^= int(basis_vector)
        if ambient == int(vector):
            return coordinate
    raise AssertionError("ambient vector outside node8 parent boundary")


def coordinate_subspace(rows: Sequence[int], parent_basis: Sequence[int]) -> list[int]:
    theta = len(parent_basis)
    coordinates = [ambient_vector_to_coordinate(int(row), parent_basis) for row in rows]
    return list(engine.xor_basis(coordinates, theta))


def coordinate_trajectory(raw: Sequence[dict], parent_basis: Sequence[int]) -> list[dict]:
    return [
        {
            "left": coordinate_subspace(item["left"], parent_basis),
            "right": coordinate_subspace(item["right"], parent_basis),
            "value": int(item["value"]),
        }
        for item in raw
    ]


def coordinate_entry(entry: dict, parent_basis: Sequence[int]) -> dict:
    out = copy.deepcopy(entry)
    out["trajectory"] = coordinate_trajectory(entry["trajectory"], parent_basis)
    return out


def coordinate_removal(removal: dict, parent_basis: Sequence[int]) -> dict:
    out = copy.deepcopy(removal)
    out["removed_generator"] = coordinate_trajectory(removal["removed_generator"], parent_basis)
    out["retained_generator"] = coordinate_trajectory(removal["retained_generator"], parent_basis)
    return out


def coordinate_stream_digest(entries: Sequence[dict]) -> str:
    hasher = hashlib.sha256()
    for entry in entries:
        hasher.update(canonical_json(entry["trajectory"]))
        hasher.update(b"\n")
    return hasher.hexdigest()


def certified_closure(proof: dict, parent_basis: Sequence[int]) -> dict:
    family = proof["input_family"]
    minimization = proof["preorder_minimization"]
    reachable = proof["reachable_closure"]
    input_generators = [coordinate_trajectory(item["generator"], parent_basis) for item in family["generators"]]
    retained_generators = [coordinate_trajectory(item["generator"], parent_basis) for item in minimization["retained_generators"]]
    removals = [coordinate_removal(item, parent_basis) for item in minimization["removals"]]
    entries = [coordinate_entry(item, parent_basis) for item in reachable["entries"]]
    if digest(input_generators) != COORDINATE_INPUT_DIGEST:
        raise AssertionError("coordinate input digest")
    if digest(retained_generators) != COORDINATE_RETAINED_DIGEST:
        raise AssertionError("coordinate retained digest")
    if digest(removals) != COORDINATE_REMOVALS_DIGEST:
        raise AssertionError("coordinate removals digest")
    if digest(entries) != COORDINATE_ENTRIES_DIGEST:
        raise AssertionError("coordinate entries digest")
    if coordinate_stream_digest(entries) != COORDINATE_STREAM_DIGEST:
        raise AssertionError("coordinate stream digest")
    work = sum(int(value) for value in proof["work_ledger"].values())
    closure = {
        "ambient_dim": len(parent_basis),
        "k": 1,
        "input_generators": input_generators,
        "retained_generators": retained_generators,
        "removals": removals,
        "universe_size": N8_ENTRIES,
        "entries": entries,
        "entry_count": len(entries),
        "ledger": {"discovery_work": work, "work": 0, "certified_total_charged_operations": work},
        "closure_method": "CERTIFIED_NODE8_TWENTY_EIGHT_GENERATOR_REACHABLE_CATALOG",
        "global_universe_enumerated": False,
        "complete_reachable_catalog_proved": True,
        "source_input_family_digest": INPUT_FAMILY_DIGEST,
        "source_retained_family_digest": RETAINED_FAMILY_DIGEST,
        "frontier_artifact_sha256": FRONTIER_SHA,
        "up_k_artifact_sha256": UPK_SHA,
        "up_k_semantic_digest": UPK_SEM,
        "source_ambient_entries_digest": SOURCE_ENTRIES_DIGEST,
        "source_ambient_stream_sha256": SOURCE_STREAM_DIGEST,
        "reachable_entries_digest": COORDINATE_ENTRIES_DIGEST,
        "reachable_catalog_stream_sha256": COORDINATE_STREAM_DIGEST,
        "input_class_ids": [item["class_id"] for item in family["generators"]],
        "retained_class_ids": [item["class_id"] for item in minimization["retained_generators"]],
        "coordinate_parent_boundary_ambient": list(parent_basis),
        "coordinate_conversion": "CANONICAL_INVERSE_OF_ORDERED_PARENT_BOUNDARY_BASIS",
        "invariant_vector": copy.deepcopy(proof["invariant_vector"]),
        "idempotence": copy.deepcopy(proof["idempotence"]),
        "admit": True,
    }
    if (len(input_generators), len(retained_generators), len(removals), len(entries)) != (N8_INPUT, N8_RETAINED, N8_REMOVALS, N8_ENTRIES):
        raise AssertionError("coordinate closure cardinality")
    return closure


def execute_node8(descriptor: dict, sequence_index: int, left_state: dict, right_state: dict, scaffold_record: dict, writers: dict, cumulative: list[int], frontier_proof: dict, up_k_proof: dict) -> tuple[dict, dict]:
    expected = {
        "node_id": 8,
        "kind": "SPINE_INTERNAL_JOIN",
        "edge_index": 2,
        "child_node_ids": [7, 3],
        "left_factor_ids": [0, 1, 2],
        "right_factor_ids": [3],
        "covered_factor_ids": [0, 1, 2, 3],
        "outside_factor_ids": [4, 5],
    }
    if descriptor != expected or descriptor != frontier_proof["geometry"]["descriptor"]:
        raise AssertionError("node8 descriptor")
    if left_state["output_receipt"]["receipt_digest"] != NODE7_RECEIPT:
        raise AssertionError("node7 child receipt")
    if right_state["output_receipt"]["receipt_digest"] != LEAF3_RECEIPT:
        raise AssertionError("leaf3 child receipt")

    ambient = int(scaffold_record["d"])
    blocks = [tuple(block) for block in scaffold_record["whole_factor_blocks"]]
    offsets = [int(value) for value in scaffold_record["affine_offsets"]]
    left_boundary = tuple(left_state["boundary"])
    right_boundary = tuple(right_state["boundary"])
    common = engine.xor_basis((*left_boundary, *right_boundary), ambient)
    parent = engine.boundary([blocks[index] for index in descriptor["covered_factor_ids"]], [blocks[index] for index in descriptor["outside_factor_ids"]], ambient)
    geometry = frontier_proof["geometry"]
    if [list(left_boundary), list(right_boundary), list(common), list(parent)] != [geometry["left_boundary"], geometry["right_boundary"], geometry["common_boundary"], geometry["parent_boundary"]]:
        raise AssertionError("node8 geometry")
    if common == parent or geometry["shrink_is_identity"] is not False:
        raise AssertionError("node8 shrink must be nontrivial")

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
    work = closure["ledger"]["certified_total_charged_operations"]
    cumulative_start = cumulative[0]
    cumulative[0] += work
    receipt = engine.output_receipt(8, descriptor["kind"], descriptor["covered_factor_ids"], parent, closure, partition_digest)
    zero_ranges = {kind.lower(): engine.make_range(starts[kind], starts[kind]) for kind in writers}
    input_ids = closure["input_class_ids"]
    retained_ids = closure["retained_class_ids"]
    node = {
        "node_id": 8,
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
        "boundary_dimensions": {"children": [len(left_boundary), len(right_boundary)], "common": len(common), "parent": len(parent)},
        "transport_contracts": {
            "left_child_to_common": engine.boundary_transport(left_boundary, common, ambient),
            "right_child_to_common": engine.boundary_transport(right_boundary, common, ambient),
            "parent_in_common_for_shrink": engine.boundary_transport(parent, common, ambient),
        },
        "side_conditions": {
            "certified_by_frontier_artifact": True,
            "join_lambda_correction_identically_zero": geometry["join_lambda_correction_identically_zero"],
            "shrink_is_identity": geometry["shrink_is_identity"],
            "shrink_correction_counts_over_quotient_cells": copy.deepcopy(geometry["shrink_correction_counts_over_quotient_cells"]),
            "ambient_to_parent_coordinate_conversion_verified": True,
        },
        "record_ranges": zero_ranges,
        "node_up_k": closure,
        "input_generator_provenance": [{"input_generator_index": index, "class_id": class_id} for index, class_id in enumerate(input_ids)],
        "retained_generator_provenance": [{"retained_generator_index": index, "class_id": class_id} for index, class_id in enumerate(retained_ids)],
        "entry_provenance": [{"entry_index": index, "source_generator_index": int(entry["source_generator_index"]), "source_class_id": entry["source_class_id"]} for index, entry in enumerate(closure["entries"])],
        "output_receipt": receipt,
        "certified_structural_bridge": {
            "frontier_artifact_sha256": FRONTIER_SHA,
            "up_k_artifact_sha256": UPK_SHA,
            "frontier_classes": N8_INPUT,
            "retained_generators": N8_RETAINED,
            "direct_removals": N8_REMOVALS,
            "naive_child_pairs_covered": 327888,
            "naive_refinements_covered": 602017584,
            "generic_pair_records_materialized": 0,
            "generic_refinement_records_materialized": 0,
            "closure_entries_returned_to_executor": N8_ENTRIES,
            "source_ambient_entries_digest": SOURCE_ENTRIES_DIGEST,
            "coordinate_entries_digest": COORDINATE_ENTRIES_DIGEST,
        },
        "work_ledger": {
            "cumulative_work_at_node_start": cumulative_start,
            "cumulative_work_before_node_b2": cumulative_start,
            "node_b2_breakdown": {"certified_node8_proof_work": work},
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
            "unique_successful_generators": N8_INPUT,
            "duplicate_successful_outputs_deleted": 0,
            "b2_dominance_deletions": N8_REMOVALS,
            "retained_generators": N8_RETAINED,
            "final_up_k_entries": N8_ENTRIES,
            "cumulative_work_delta": work,
            "certified_child_pairs_covered": 327888,
            "certified_naive_refinements_covered": 602017584,
            "certified_reachability_witnesses": N8_ENTRIES,
        },
    }
    node["node_execution_digest"] = digest(node)
    state = {"node_id": 8, "covered_factor_ids": descriptor["covered_factor_ids"], "boundary": list(parent), "closure": closure, "output_receipt": receipt}
    return node, state


def exact_refinements(left: Sequence[dict], right: Sequence[dict]) -> int:
    return sum(b44.delannoy_path_count(len(a["trajectory"]), len(b["trajectory"])) for a in left for b in right)


def length_histogram(entries: Sequence[dict]) -> dict[str, int]:
    result: dict[str, int] = {}
    for entry in entries:
        key = str(len(entry["trajectory"]))
        result[key] = result.get(key, 0) + 1
    return dict(sorted(result.items(), key=lambda item: int(item[0])))


def build(prefix_root: Path, hardening_path: Path, node7_frontier_path: Path, node7_up_k_path: Path, node8_frontier_path: Path, node8_up_k_path: Path, output_dir: Path, pair_cap: int = 10000, refinement_cap: int = 2000000) -> dict:
    prefix_manifest, hardening, hardening_records = node6.load_frozen_hardening(prefix_root, hardening_path)
    node7_frontier, node7_up_k = node7int.sources(node7_frontier_path, node7_up_k_path)
    node8_frontier, node8_up_k = source_artifacts(node8_frontier_path, node8_up_k_path)
    if node8_frontier["source"]["integrated_manifest_digest"] != NODE7_INTEGRATED_MANIFEST_DIGEST:
        raise AssertionError("node8 frontier integrated manifest binding")
    if node8_frontier["source"]["node7_output_receipt_digest"] != NODE7_RECEIPT:
        raise AssertionError("node8 frontier node7 receipt binding")

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
            closure = node6.certified_closure(generators, ambient_dim, k, hardening, hardening_records)
            node6_calls.append(closure["reachable_entries_digest"])
            return closure
        return original_up_k(generators, ambient_dim, k, ledger)

    def patched_execute(descriptor, sequence_index, left_state, right_state, scaffold_record, writers, cumulative, capability):
        node_id = int(descriptor["node_id"])
        if node_id == 7:
            if node7_calls:
                raise AssertionError("node7 certified bridge called twice")
            result = node7int.execute7(descriptor, sequence_index, left_state, right_state, scaffold_record, writers, cumulative, node7_frontier, node7_up_k)
            node7_calls.append(result[0]["output_receipt"]["receipt_digest"])
            return result
        if node_id == 8:
            if node8_calls:
                raise AssertionError("node8 certified bridge called twice")
            result = execute_node8(descriptor, sequence_index, left_state, right_state, scaffold_record, writers, cumulative, node8_frontier, node8_up_k)
            node8_calls.append(result[0]["output_receipt"]["receipt_digest"])
            return result
        return original_execute(descriptor, sequence_index, left_state, right_state, scaffold_record, writers, cumulative, capability)

    try:
        engine.selected_scaffold = negative.selected_negative_scaffold
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

    if len(node6_calls) != 1 or len(node7_calls) != 1 or len(node8_calls) != 1:
        raise AssertionError("certified bridge call vector")
    execution = manifest["execution"]
    if execution["processed_internal_node_ids"] != [6, 7, 8]:
        raise AssertionError("processed node vector")
    stop = execution["stop"]
    if (int(stop["node_id"]), stop["reason"], int(stop["required"]), int(stop["cap"]), stop["no_layout_at_cap"], stop["terminal"]) != (N9, "CHILD_PAIR_CAP_EXCEEDED", N9_PAIRS, int(pair_cap), False, TERMINAL):
        raise AssertionError("node9 stop")
    if manifest["chunking"]["transcript_root_digest"] != TRANSCRIPT_ROOT:
        raise AssertionError("transcript root changed")

    node8 = next(item for item in manifest["node_results"] if int(item["node_id"]) == 8)
    closure = node8["node_up_k"]
    if (closure["entry_count"], closure["reachable_entries_digest"], len(closure["input_generators"]), len(closure["retained_generators"]), len(closure["removals"])) != (N8_ENTRIES, COORDINATE_ENTRIES_DIGEST, N8_INPUT, N8_RETAINED, N8_REMOVALS):
        raise AssertionError("node8 integrated state")
    if any(int(value["count"]) for value in node8["record_ranges"].values()):
        raise AssertionError("generic node8 transcript materialized")

    leaf4 = manifest["leaf_full_sets"][4]
    if leaf4["output_receipt"]["receipt_digest"] != LEAF4_RECEIPT:
        raise AssertionError("leaf4 receipt")
    left_entries = closure["entries"]
    right_entries = leaf4["full_set"]["entries"]
    pair_count = len(left_entries) * len(right_entries)
    refinement_count = exact_refinements(left_entries, right_entries)
    if (pair_count, refinement_count) != (N9_PAIRS, N9_REFINEMENTS):
        raise AssertionError("node9 exact frontier")

    blocks = [tuple(block) for block in manifest["scaffold_case"]["whole_factor_blocks"]]
    left_boundary = tuple(node8["parent_boundary"])
    right_boundary = tuple(leaf4["boundary_rref_ambient"])
    common = engine.xor_basis((*left_boundary, *right_boundary), 3)
    parent = engine.boundary([blocks[index] for index in [0, 1, 2, 3, 4]], [blocks[5]], 3)
    if (left_boundary, right_boundary, common, parent) != ((4, 1), (5,), (4, 1), (1,)):
        raise AssertionError("node9 geometry")

    summary = {
        "schema": SCHEMA,
        "source": {
            "prefix_manifest_digest": prefix_manifest["manifest_digest"],
            "hardening_artifact_sha256": node6.EXPECTED_HARDENING_SHA256,
            "node7_frontier_artifact_sha256": node7int.FRONTIER_SHA,
            "node7_up_k_artifact_sha256": node7int.UPK_SHA,
            "node8_frontier_artifact_sha256": FRONTIER_SHA,
            "node8_frontier_semantic_digest": FRONTIER_SEM,
            "node8_up_k_artifact_sha256": UPK_SHA,
            "node8_up_k_semantic_digest": UPK_SEM,
        },
        "certified_calls": {"node6": 1, "node7": 1, "node8": 1},
        "integrated_manifest_digest": manifest["manifest_digest"],
        "integrated_transcript_root_digest": manifest["chunking"]["transcript_root_digest"],
        "node8": {
            "node_execution_digest": node8["node_execution_digest"],
            "output_receipt_digest": node8["output_receipt"]["receipt_digest"],
            "input_generators": N8_INPUT,
            "retained_generators": N8_RETAINED,
            "direct_removals": N8_REMOVALS,
            "up_k_entries": N8_ENTRIES,
            "source_ambient_entries_digest": SOURCE_ENTRIES_DIGEST,
            "coordinate_entries_digest": COORDINATE_ENTRIES_DIGEST,
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
            "left_length_histogram": length_histogram(left_entries),
            "right_length_histogram": length_histogram(right_entries),
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
            "current_global_terminal": TERMINAL,
            "p_vs_np": "OPEN",
        },
        "next_gate": "C049.1_B4.6.3_NODE9_PARENT_FRONTIER_STRUCTURAL_COMPRESSION",
    }
    summary["semantic_digest"] = digest(summary)
    (output_dir / "node8-integration-node9-preflight-summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("JANUS_C049_1_B4_6_3_NODE8_UP_K_INTEGRATION = PASS")
    print("PROCESSED_INTERNAL_NODE_IDS =", execution["processed_internal_node_ids"])
    print("NODE8_INPUT_GENERATORS =", N8_INPUT)
    print("NODE8_RETAINED_GENERATORS =", N8_RETAINED)
    print("NODE8_DIRECT_REMOVALS =", N8_REMOVALS)
    print("NODE8_UP_K_ENTRIES =", N8_ENTRIES)
    print("NODE9_CHILD_PAIRS_REQUIRED =", pair_count)
    print("NODE9_NAIVE_REFINEMENTS_REQUIRED =", refinement_count)
    print("STOP_NODE =", stop["node_id"])
    print("STOP_REASON =", stop["reason"])
    print("ROOT_NODE =", ROOT)
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
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--node9-pair-cap", type=int, default=10000)
    parser.add_argument("--node9-refinement-cap", type=int, default=2000000)
    args = parser.parse_args()
    build(args.prefix_root, args.hardening_artifact, args.node7_frontier_artifact, args.node7_up_k_artifact, args.node8_frontier_artifact, args.node8_up_k_artifact, args.output_dir, args.node9_pair_cap, args.node9_refinement_cap)


if __name__ == "__main__":
    main()
