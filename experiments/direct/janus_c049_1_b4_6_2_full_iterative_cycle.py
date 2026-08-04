#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence

import janus_c049_1_b4_5_bottom_up_scaffold_executor as b45
import janus_c049_1_b4_6_1_layout_reconstruction as b461
from janus_c049_1_b4_2_3k_scaffold import boundary, scaffold


SCHEMA = "C049.1-B4.6.2-FULL-ITERATIVE-COMPRESSION-CYCLE-v1"
ROUND_SCHEMA = "C049.1-B4.6.2-ROUND-SCAFFOLD-TRANSCRIPT-v1"
TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"
LOCAL_RESULT = "FULL_ITERATIVE_COMPRESSION_CYCLE_REPLAYED"
SOURCE_HEAD = "e6eefa6e8878c3a59d8b2e33f213c240571b6686"

FIXTURE = {
    "ambient_dimension": 2,
    "k": 1,
    "whole_factor_blocks": [[1], [2], [1]],
    "affine_offsets": [0, 1, 1],
    "initial_order": [0],
}


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def exact_cut_widths(blocks: Sequence[Sequence[int]], order: Sequence[int], d: int) -> list[dict]:
    if sorted(order) != list(range(len(blocks))):
        raise AssertionError("order is not a whole-factor permutation")
    cuts = []
    for cut in range(len(order) + 1):
        left_ids = list(order[:cut])
        right_ids = list(order[cut:])
        basis = boundary(
            [blocks[index] for index in left_ids],
            [blocks[index] for index in right_ids],
            d,
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


def make_range(start: int, end: int) -> dict:
    return {
        "first": start if end > start else None,
        "last": end - 1 if end > start else None,
        "count": end - start,
    }


def execute_scaffold_round(
    scaffold_record: dict,
    output_dir: Path,
    cumulative_start: int,
) -> dict:
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError("round output directory must be empty")
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "chunks").mkdir()

    if scaffold_record["terminal"] != "SCAFFOLD_3K_CERTIFIED":
        raise AssertionError("round scaffold is not certified")
    if not scaffold_record["proof_obligations"]["scaffold_width_at_most_3k"]:
        raise AssertionError("round scaffold exceeds 3k")

    capability = dict(b45.DEFAULT_CAPABILITY)
    topology = b45.derive_topology(scaffold_record)
    if len(topology["internal_nodes"]) > capability["max_internal_nodes"]:
        raise AssertionError("round topology exceeds node capability")

    ambient = int(scaffold_record["d"])
    k = int(scaffold_record["k"])
    blocks = [tuple(int(row) for row in block) for block in scaffold_record["whole_factor_blocks"]]
    offsets = [int(value) for value in scaffold_record["affine_offsets"]]

    cumulative = [int(cumulative_start)]
    scaffold_work = int(scaffold_record["charged_work"])
    cumulative[0] += scaffold_work
    scaffold_event = {
        "kind": "B4.2_SCAFFOLD_CONSTRUCTION",
        "work_delta": scaffold_work,
        "cumulative_work": cumulative[0],
        "semantic_digest": scaffold_record["semantic_digest"],
    }

    leaves = []
    leaf_work_events = []
    states: dict[int, dict] = {}
    for leaf_descriptor in topology["leaf_nodes"]:
        factor_id = int(leaf_descriptor["factor_id"])
        leaf_boundary = boundary(
            [blocks[factor_id]],
            [blocks[index] for index in range(len(blocks)) if index != factor_id],
            ambient,
        )
        leaf = b45.leaf_full_set(
            factor_id,
            blocks[factor_id],
            offsets[factor_id],
            leaf_boundary,
            ambient,
            k,
        )
        ledger = leaf["full_set"]["ledger"]
        breakdown = {
            "b2_discovery_work": int(ledger["discovery_work"]),
            "b2_work": int(ledger["work"]),
        }
        cumulative[0] += sum(breakdown.values())
        leaf_work_events.append(
            {
                "event_index": len(leaf_work_events),
                "node_id": factor_id,
                "kind": "LEAF_FULL_SET",
                "breakdown": breakdown,
                "work_delta": sum(breakdown.values()),
                "cumulative_work": cumulative[0],
            }
        )
        leaves.append(leaf)
        states[factor_id] = {
            "node_id": factor_id,
            "covered_factor_ids": [factor_id],
            "boundary": list(leaf_boundary),
            "closure": leaf["full_set"],
            "output_receipt": leaf["output_receipt"],
        }

    writers = {
        "PAIRS": b45.ChunkWriter(output_dir, "PAIRS", "pair_id", b45.PAIR_CHUNK_SIZE),
        "REFINEMENTS": b45.ChunkWriter(
            output_dir, "REFINEMENTS", "attempt_id", b45.REFINEMENT_CHUNK_SIZE
        ),
        "GENERATORS": b45.ChunkWriter(
            output_dir, "GENERATORS", "generator_id", b45.GENERATOR_CHUNK_SIZE
        ),
        "DELETIONS": b45.ChunkWriter(
            output_dir, "DELETIONS", "deletion_id", b45.DELETION_CHUNK_SIZE
        ),
    }

    node_results = []
    stop = None
    for sequence_index, descriptor in enumerate(topology["internal_nodes"]):
        left_state = states[int(descriptor["child_node_ids"][0])]
        right_state = states[int(descriptor["child_node_ids"][1])]
        result = b45.execute_node(
            descriptor,
            sequence_index,
            left_state,
            right_state,
            scaffold_record,
            writers,
            cumulative,
            capability,
        )
        if isinstance(result, dict):
            stop = result
            break
        node, state = result
        node_results.append(node)
        states[int(descriptor["node_id"])] = state
        if int(node["node_up_k"]["entry_count"]) == 0:
            stop = {
                "status": "OPEN_AT_NODE_EMPTY_FULL_SET",
                "node_id": descriptor["node_id"],
                "reason": "EMPTY_FULL_SET_IS_NOT_A_COMPLETENESS_PROOF",
                "required": None,
                "cap": None,
                "terminal": TERMINAL,
                "no_layout_at_cap": False,
            }
            break

    chunk_groups = {kind: writer.finish() for kind, writer in writers.items()}
    all_chunks = [item for group in chunk_groups.values() for item in group]
    complete = stop is None and len(node_results) == len(topology["internal_nodes"])
    root_receipt = (
        states[int(topology["root_node_id"])]["output_receipt"] if complete else None
    )

    audit = {
        "leaf_full_sets": len(leaves),
        "internal_nodes_processed": len(node_results),
        "child_pairs_processed": sum(
            node["audit"]["child_pairs_processed"] for node in node_results
        ),
        "lattice_paths_processed": sum(
            node["audit"]["lattice_paths_processed"] for node in node_results
        ),
        "successful_refinements": sum(
            node["audit"]["successful_refinements"] for node in node_results
        ),
        "failed_refinements": sum(
            node["audit"]["failed_refinements"] for node in node_results
        ),
        "raw_precompact_join_statistics": sum(
            node["audit"]["raw_precompact_join_statistics"] for node in node_results
        ),
        "unique_successful_generators": sum(
            node["audit"]["unique_successful_generators"] for node in node_results
        ),
        "duplicate_successful_outputs_deleted": sum(
            node["audit"]["duplicate_successful_outputs_deleted"] for node in node_results
        ),
        "b2_dominance_deletions": sum(
            node["audit"]["b2_dominance_deletions"] for node in node_results
        ),
        "retained_generators_across_nodes": sum(
            node["audit"]["retained_generators"] for node in node_results
        ),
        "root_up_k_entries": int(root_receipt["entry_count"]) if root_receipt else None,
        "cumulative_work": cumulative[0],
        "chunk_count": len(all_chunks),
        "failures": 0,
    }

    manifest = {
        "schema": ROUND_SCHEMA,
        "phase": "B4.6.2_ROUND_SCAFFOLD_EXECUTION",
        "source_head": SOURCE_HEAD,
        "scaffold_case": scaffold_record,
        "executor_contract": {
            "accepted_scaffold_type": "CATERPILLAR_APPEND_NEW_LEAF",
            "topology_derivation": "B4.2 leaves and spine nodes plus explicit root-close join",
            "node_kernel": "B3 expand/join/shrink then B2 dominance/up_k",
            "boundary_handoff": "parent output receipt becomes exact child input receipt",
            "capacity_stop_terminal": TERMINAL,
            "empty_full_set_terminal": TERMINAL,
            "no_layout_at_cap_enabled": False,
        },
        "capability": capability,
        "topology": topology,
        "leaf_full_sets": leaves,
        "node_results": node_results,
        "execution": {
            "status": "ROOT_FULL_SET_COMPUTED" if complete else stop["status"],
            "processed_internal_node_ids": [node["node_id"] for node in node_results],
            "stopped_node_id": None if complete else stop["node_id"],
            "stop": stop,
            "root_node_id": topology["root_node_id"],
            "root_full_set_receipt": root_receipt,
        },
        "chunking": {
            "compression": "DETERMINISTIC_GZIP_DEFLATE9_MTIME0_OS255",
            "record_chunk_sizes": {
                "PAIRS": b45.PAIR_CHUNK_SIZE,
                "REFINEMENTS": b45.REFINEMENT_CHUNK_SIZE,
                "GENERATORS": b45.GENERATOR_CHUNK_SIZE,
                "DELETIONS": b45.DELETION_CHUNK_SIZE,
            },
            "tail_chunk_may_be_short": True,
            "chunk_groups": chunk_groups,
            "transcript_root_digest": digest(chunk_groups),
            "chunk_count": len(all_chunks),
            "uncompressed_chunk_bytes": sum(item["uncompressed_bytes"] for item in all_chunks),
            "compressed_chunk_bytes": sum(item["compressed_bytes"] for item in all_chunks),
        },
        "work_ledger": {
            "cumulative_work_at_round_start": int(cumulative_start),
            "scaffold_event": scaffold_event,
            "leaf_full_set_events": leaf_work_events,
            "node_intervals": [
                {
                    "node_id": node["node_id"],
                    "start": node["work_ledger"]["cumulative_work_at_node_start"],
                    "end": node["work_ledger"]["cumulative_work_at_node_end"],
                }
                for node in node_results
            ],
            "cumulative_work_after_executor": cumulative[0],
            "monotone_by_construction": True,
        },
        "audit": audit,
        "strict_boundary": {
            "scope": "one iterative-compression round under explicit capability bounds",
            "all_selected_scaffold_nodes_processed": complete,
            "root_full_set_computed": complete,
            "root_layout_reconstructed": False,
            "terminal_completeness_proved": False,
            "found_layout_enabled": False,
            "no_layout_at_cap_enabled": False,
            "current_global_terminal": TERMINAL,
            "p_vs_np": "OPEN",
        },
    }
    manifest["manifest_digest"] = digest(manifest)
    (output_dir / "manifest.json").write_bytes(canonical_json(manifest) + b"\n")
    return manifest


def reconstruct_round(round_root: Path, manifest: dict) -> dict:
    if manifest["execution"]["status"] != "ROOT_FULL_SET_COMPUTED":
        return {
            "status": "OPEN_ROUND_WITHOUT_ROOT_FULL_SET",
            "terminal": TERMINAL,
            "found_layout": False,
            "no_layout_at_cap": False,
        }

    leaves = {int(item["node_id"]): item for item in manifest["leaf_full_sets"]}
    nodes = {int(item["node_id"]): item for item in manifest["node_results"]}
    generators = {
        int(item["generator_id"]): item
        for item in b461.all_records(round_root, manifest, "GENERATORS")
    }
    root_node_id = int(manifest["execution"]["root_node_id"])
    root_node = nodes[root_node_id]
    k = int(manifest["scaffold_case"]["k"])
    root_entry_index = b461.selected_entry_index(root_node, k)
    accepting_count = len(b461.accepting_root_entry_indices(root_node, k))

    ledger = b461.WorkLedger(int(manifest["audit"]["cumulative_work"]))
    ledger.charge("ROOT_ACCEPTANCE_TESTS", accepting_count, node_id=root_node_id)
    receipt = b461.trace_entry(
        root_node_id,
        root_entry_index,
        manifest,
        round_root,
        leaves,
        nodes,
        generators,
        ledger,
        set(),
    )
    order = [int(value) for value in receipt["order"]]
    cuts = b461.exact_cut_widths(manifest["scaffold_case"], order)
    ledger.charge("EXACT_LAYOUT_CUT_RECOMPUTATIONS", len(cuts), order=order)
    maximum_width = max(item["width"] for item in cuts)
    if maximum_width > k:
        raise AssertionError("round reconstruction exceeds k")

    blocks = manifest["scaffold_case"]["whole_factor_blocks"]
    offsets = manifest["scaffold_case"]["affine_offsets"]
    layout = [
        {
            "position": position,
            "factor_id": factor_id,
            "normal_space_block_rref": blocks[factor_id],
            "affine_offset": offsets[factor_id],
        }
        for position, factor_id in enumerate(order)
    ]
    reconstruction = {
        "status": "ROUND_LAYOUT_WITNESS_RECONSTRUCTED",
        "root_selection": {
            "accepting_root_entry_count": accepting_count,
            "selected_root_entry_index": root_entry_index,
            "rule": "MINIMUM_SHA256_THEN_ENTRY_INDEX_AMONG_EMPTY_BOUNDARY_WIDTH_AT_MOST_K",
        },
        "reconstruction_receipt": receipt,
        "reconstructed_factor_order": order,
        "reconstructed_layout": layout,
        "exact_cut_transcript": cuts,
        "exact_maximum_width": maximum_width,
        "reconstruction_work": ledger.total - int(manifest["audit"]["cumulative_work"]),
        "cumulative_work_after_reconstruction": ledger.total,
        "work_events": ledger.events,
        "found_layout": False,
        "no_layout_at_cap": False,
        "terminal": TERMINAL,
    }
    reconstruction["reconstruction_digest"] = digest(reconstruction)
    (round_root / "reconstruction.json").write_bytes(canonical_json(reconstruction) + b"\n")
    return reconstruction


def bind_artifact(artifact: dict, computational_work: int) -> dict:
    artifact = copy.deepcopy(artifact)
    artifact["manifest_digest"] = "0" * 64
    artifact["certificate_accounting"]["fixed_point_serialized_bytes"] = 0
    artifact["work_ledger"]["certificate_byte_charge"] = 0
    artifact["work_ledger"]["cumulative_work_final"] = computational_work
    for _ in range(64):
        body = copy.deepcopy(artifact)
        body.pop("manifest_digest", None)
        artifact["manifest_digest"] = digest(body)
        size = len(canonical_json(artifact)) + 1
        changed = False
        if artifact["certificate_accounting"]["fixed_point_serialized_bytes"] != size:
            artifact["certificate_accounting"]["fixed_point_serialized_bytes"] = size
            changed = True
        if artifact["work_ledger"]["certificate_byte_charge"] != size:
            artifact["work_ledger"]["certificate_byte_charge"] = size
            changed = True
        if artifact["work_ledger"]["cumulative_work_final"] != computational_work + size:
            artifact["work_ledger"]["cumulative_work_final"] = computational_work + size
            changed = True
        if not changed:
            body = copy.deepcopy(artifact)
            body.pop("manifest_digest", None)
            artifact["manifest_digest"] = digest(body)
            if len(canonical_json(artifact)) + 1 == size:
                return artifact
    raise AssertionError("cycle certificate fixed point did not converge")


def build(output_dir: Path) -> dict:
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError("output directory must be empty")
    output_dir.mkdir(parents=True, exist_ok=True)

    d = int(FIXTURE["ambient_dimension"])
    k = int(FIXTURE["k"])
    blocks = [tuple(int(row) for row in block) for block in FIXTURE["whole_factor_blocks"]]
    offsets = [int(value) for value in FIXTURE["affine_offsets"]]
    previous_order = [int(value) for value in FIXTURE["initial_order"]]

    initial_cuts = exact_cut_widths(blocks[:1], previous_order, d)
    initial_width = max(item["width"] for item in initial_cuts)
    if initial_width > k:
        raise AssertionError("initial one-factor layout exceeds k")
    cumulative = len(initial_cuts)
    initial_event = {
        "kind": "INITIAL_LAYOUT_REPLAY",
        "factor_order": previous_order,
        "exact_cut_transcript": initial_cuts,
        "work_delta": len(initial_cuts),
        "cumulative_work": cumulative,
    }

    rounds = []
    for round_size in range(2, len(blocks) + 1):
        round_scaffold = scaffold(
            blocks[:round_size],
            tuple(previous_order),
            round_size - 1,
            d,
            k,
            offsets[:round_size],
        )
        if round_scaffold["terminal"] != "SCAFFOLD_3K_CERTIFIED":
            raise AssertionError("frozen cycle hit local dimension obstruction")
        round_root = output_dir / f"round-{round_size:02d}"
        executor = execute_scaffold_round(round_scaffold, round_root, cumulative)
        reconstruction = reconstruct_round(round_root, executor)
        if reconstruction["status"] != "ROUND_LAYOUT_WITNESS_RECONSTRUCTED":
            raise AssertionError("frozen cycle failed to reconstruct a round layout")
        if reconstruction["exact_maximum_width"] > k:
            raise AssertionError("frozen cycle reconstructed an invalid layout")

        transition = {
            "round_index": round_size - 1,
            "round_size": round_size,
            "new_factor_id": round_size - 1,
            "previous_factor_order": previous_order,
            "previous_order_digest": digest(previous_order),
            "scaffold_semantic_digest": round_scaffold["semantic_digest"],
            "executor_manifest_digest": executor["manifest_digest"],
            "executor_transcript_root_digest": executor["chunking"]["transcript_root_digest"],
            "reconstruction_digest": reconstruction["reconstruction_digest"],
            "reconstructed_factor_order": reconstruction["reconstructed_factor_order"],
            "exact_maximum_width": reconstruction["exact_maximum_width"],
            "grouped_partition_preserved": True,
            "affine_offsets_preserved": True,
            "cumulative_work_at_round_start": executor["work_ledger"]["cumulative_work_at_round_start"],
            "cumulative_work_after_executor": executor["work_ledger"]["cumulative_work_after_executor"],
            "cumulative_work_after_reconstruction": reconstruction["cumulative_work_after_reconstruction"],
            "terminal": TERMINAL,
        }
        transition["transition_digest"] = digest(transition)
        rounds.append(
            {
                "round_index": round_size - 1,
                "round_size": round_size,
                "directory": round_root.name,
                "transition": transition,
                "executor_audit": executor["audit"],
                "reconstruction_summary": {
                    "root_selection": reconstruction["root_selection"],
                    "reconstructed_factor_order": reconstruction["reconstructed_factor_order"],
                    "exact_cut_transcript": reconstruction["exact_cut_transcript"],
                    "exact_maximum_width": reconstruction["exact_maximum_width"],
                    "reconstruction_work": reconstruction["reconstruction_work"],
                    "reconstruction_digest": reconstruction["reconstruction_digest"],
                },
            }
        )
        cumulative = int(reconstruction["cumulative_work_after_reconstruction"])
        previous_order = list(reconstruction["reconstructed_factor_order"])

    final_cuts = exact_cut_widths(blocks, previous_order, d)
    if max(item["width"] for item in final_cuts) > k:
        raise AssertionError("final cycle layout exceeds k")

    total_uncompressed = sum(
        json.loads((output_dir / item["directory"] / "manifest.json").read_text())["chunking"]["uncompressed_chunk_bytes"]
        for item in rounds
    )
    total_compressed = sum(
        json.loads((output_dir / item["directory"] / "manifest.json").read_text())["chunking"]["compressed_chunk_bytes"]
        for item in rounds
    )
    total_chunks = sum(item["executor_audit"]["chunk_count"] for item in rounds)
    computational_work = cumulative

    artifact = {
        "schema": SCHEMA,
        "phase": "B4.6.2_FULL_ITERATIVE_COMPRESSION_CYCLE",
        "source_head": SOURCE_HEAD,
        "fixture": FIXTURE,
        "initial_layout": initial_event,
        "rounds": rounds,
        "round_count": len(rounds),
        "all_rounds_executed": len(rounds) == len(blocks) - 1,
        "final_reconstructed_factor_order": previous_order,
        "final_exact_cut_transcript": final_cuts,
        "final_exact_maximum_width": max(item["width"] for item in final_cuts),
        "result": LOCAL_RESULT,
        "audit": {
            "rounds": len(rounds),
            "scaffolds_constructed": len(rounds),
            "root_full_sets_computed": len(rounds),
            "layouts_reconstructed": len(rounds),
            "child_pairs_processed": sum(item["executor_audit"]["child_pairs_processed"] for item in rounds),
            "lattice_paths_processed": sum(item["executor_audit"]["lattice_paths_processed"] for item in rounds),
            "failed_refinements": sum(item["executor_audit"]["failed_refinements"] for item in rounds),
            "successful_refinements": sum(item["executor_audit"]["successful_refinements"] for item in rounds),
            "raw_precompact_join_statistics": sum(item["executor_audit"]["raw_precompact_join_statistics"] for item in rounds),
            "chunk_count": total_chunks,
            "failures": 0,
        },
        "work_ledger": {
            "initial_layout_work": initial_event["work_delta"],
            "round_transitions": [item["transition"] for item in rounds],
            "cumulative_work_before_certificate": computational_work,
            "certificate_byte_charge": 0,
            "cumulative_work_final": computational_work,
            "monotone_across_rounds": True,
        },
        "certificate_accounting": {
            "round_chunk_count": total_chunks,
            "round_uncompressed_chunk_bytes": total_uncompressed,
            "round_compressed_chunk_bytes": total_compressed,
            "fixed_point_serialized_bytes": 0,
        },
        "strict_boundary": {
            "scope": "all iterative-compression rounds of one frozen grouped GF(2) arrangement",
            "all_rounds_executed": True,
            "every_round_scaffold_discovered_internally": True,
            "every_round_root_full_set_computed": True,
            "every_round_layout_reconstructed": True,
            "whole_factor_partition_preserved": True,
            "affine_offsets_preserved": True,
            "exact_width_at_most_k_verified_each_round": True,
            "terminal_completeness_proved": False,
            "found_layout_enabled": False,
            "no_layout_at_cap_enabled": False,
            "current_global_terminal": TERMINAL,
            "next_gate": "C049.1_B4.6.3_TERMINAL_COMPLETENESS",
            "p_vs_np": "OPEN",
        },
    }
    artifact = bind_artifact(artifact, computational_work)
    (output_dir / "artifact.json").write_bytes(canonical_json(artifact) + b"\n")

    print("JANUS_C049_1_B4_6_2_FULL_ITERATIVE_COMPRESSION_CYCLE = PASS")
    print("LOCAL_RESULT =", LOCAL_RESULT)
    print("ROUNDS =", artifact["round_count"])
    print("FINAL_ORDER =", artifact["final_reconstructed_factor_order"])
    print("FINAL_MAXIMUM_WIDTH =", artifact["final_exact_maximum_width"])
    print("FAILED_REFINEMENTS =", artifact["audit"]["failed_refinements"])
    print("CUMULATIVE_WORK =", artifact["work_ledger"]["cumulative_work_final"])
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
