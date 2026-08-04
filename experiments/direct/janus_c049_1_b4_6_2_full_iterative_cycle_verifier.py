#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Sequence

import janus_c049_1_b2_full_transcript_verifier as b2v
import janus_c049_1_b3_expand_join_shrink_verifier as b3v
import janus_c049_1_b4_4_nonzero_boundary_node_full_set_verifier as b44v
import janus_c049_1_b4_5_bottom_up_scaffold_executor_verifier as b45v


SCHEMA = "C049.1-B4.6.2-FULL-ITERATIVE-COMPRESSION-CYCLE-v1"
ROUND_SCHEMA = "C049.1-B4.6.2-ROUND-SCAFFOLD-TRANSCRIPT-v1"
TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"
LOCAL_RESULT = "FULL_ITERATIVE_COMPRESSION_CYCLE_REPLAYED"
SOURCE_HEAD = "e6eefa6e8878c3a59d8b2e33f213c240571b6686"
EXPECTED_CHUNK_SIZES = {
    "PAIRS": 128,
    "REFINEMENTS": 4096,
    "GENERATORS": 128,
    "DELETIONS": 2048,
}
EXPECTED_FIXTURE = {
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


def verify_object_digest(obj: dict, field: str) -> None:
    body = copy.deepcopy(obj)
    claimed = body.pop(field, None)
    if claimed != digest(body):
        raise AssertionError(f"{field} mismatch")


def verify_b2_closure(closure: dict) -> None:
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
    if any(not isinstance(value, int) or value < 0 for value in ledger.items() for value in [value[1]]):
        raise AssertionError("invalid B2 ledger")


def exact_cut_widths(blocks: Sequence[Sequence[int]], order: Sequence[int], d: int) -> list[dict]:
    if sorted(order) != list(range(len(blocks))):
        raise AssertionError("order is not a whole-factor permutation")
    cuts = []
    for cut in range(len(order) + 1):
        left_ids = list(order[:cut])
        right_ids = list(order[cut:])
        basis = b45v.boundary(blocks, left_ids, right_ids, d)
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


def verify_round_manifest_integrity(manifest: dict) -> None:
    verify_object_digest(manifest, "manifest_digest")
    if manifest.get("schema") != ROUND_SCHEMA or manifest.get("source_head") != SOURCE_HEAD:
        raise AssertionError("round schema/source mismatch")
    chunking = manifest["chunking"]
    if chunking["record_chunk_sizes"] != EXPECTED_CHUNK_SIZES:
        raise AssertionError("round chunk sizes changed")
    groups = chunking["chunk_groups"]
    if set(groups) != set(EXPECTED_CHUNK_SIZES):
        raise AssertionError("round chunk groups changed")
    if chunking["transcript_root_digest"] != digest(groups):
        raise AssertionError("round transcript root mismatch")
    total_chunks = total_raw = total_compressed = 0
    for kind, metadata in groups.items():
        expected_id = 0
        for index, item in enumerate(metadata):
            if item["kind"] != kind or item["chunk_index"] != index:
                raise AssertionError("round chunk identity mismatch")
            if item["first_record_id"] != expected_id:
                raise AssertionError("round chunk range gap")
            if item["last_record_id"] != expected_id + item["record_count"] - 1:
                raise AssertionError("round chunk range mismatch")
            if item["record_count"] <= 0 or item["record_count"] > EXPECTED_CHUNK_SIZES[kind]:
                raise AssertionError("round chunk size violation")
            if index + 1 < len(metadata) and item["record_count"] != EXPECTED_CHUNK_SIZES[kind]:
                raise AssertionError("short non-tail round chunk")
            previous = metadata[index - 1] if index else None
            following = metadata[index + 1] if index + 1 < len(metadata) else None
            if item["previous_chunk_index"] != (index - 1 if previous else None):
                raise AssertionError("round previous chunk index mismatch")
            if item["previous_chunk_digest"] != (previous["compressed_sha256"] if previous else None):
                raise AssertionError("round previous chunk digest mismatch")
            if item["next_chunk_index"] != (index + 1 if following else None):
                raise AssertionError("round next chunk index mismatch")
            if item["next_chunk_digest"] != (following["compressed_sha256"] if following else None):
                raise AssertionError("round next chunk digest mismatch")
            expected_id += item["record_count"]
            total_raw += item["uncompressed_bytes"]
            total_compressed += item["compressed_bytes"]
        total_chunks += len(metadata)
    if chunking["chunk_count"] != total_chunks:
        raise AssertionError("round chunk count mismatch")
    if chunking["uncompressed_chunk_bytes"] != total_raw:
        raise AssertionError("round raw byte mismatch")
    if chunking["compressed_chunk_bytes"] != total_compressed:
        raise AssertionError("round compressed byte mismatch")


def verify_scaffold(manifest: dict, blocks: list[tuple[int, ...]], offsets: list[int], previous_order: list[int], d: int, k: int) -> dict:
    scaffold = manifest["scaffold_case"]
    body = {key: value for key, value in scaffold.items() if key != "semantic_digest"}
    if scaffold.get("semantic_digest") != digest(body):
        raise AssertionError("scaffold semantic digest mismatch")
    round_size = len(blocks)
    expected_order = list(previous_order) + [round_size - 1]
    if scaffold["terminal"] != "SCAFFOLD_3K_CERTIFIED":
        raise AssertionError("round scaffold is not certified")
    if int(scaffold["d"]) != d or int(scaffold["k"]) != k:
        raise AssertionError("round scaffold dimensions changed")
    canonical_blocks = [b3v.rref(block, d) for block in blocks]
    if [tuple(item) for item in scaffold["whole_factor_blocks"]] != canonical_blocks:
        raise AssertionError("round grouped blocks changed")
    if scaffold["affine_offsets"] != offsets:
        raise AssertionError("round affine offsets changed")
    if scaffold["previous_order"] != previous_order:
        raise AssertionError("round previous order changed")
    if scaffold["new_leaf"] != round_size - 1 or scaffold["scaffold_order"] != expected_order:
        raise AssertionError("round append discipline changed")
    previous_cuts = exact_cut_widths(canonical_blocks[:-1], previous_order, d)
    previous_widths = [item["width"] for item in previous_cuts[1:-1]]
    if scaffold["previous_width_vector"] != previous_widths:
        raise AssertionError("round previous width replay mismatch")
    edges, charged = b45v.recompute_edges(canonical_blocks, expected_order, d)
    if scaffold["candidate_edges"] != edges or scaffold["charged_work"] != charged:
        raise AssertionError("round scaffold edge/work replay mismatch")
    if scaffold["scaffold_width"] != max((item["width"] for item in edges), default=0):
        raise AssertionError("round scaffold width mismatch")
    obligations = scaffold["proof_obligations"]
    if obligations != {
        "previous_width_at_most_k": max(previous_widths, default=0) <= k,
        "new_dimension_at_most_2k": len(canonical_blocks[-1]) <= 2 * k,
        "all_edges_retained": len(edges) == len(expected_order) - 1,
        "scaffold_width_at_most_3k": scaffold["scaffold_width"] <= 3 * k,
    }:
        raise AssertionError("round scaffold obligations mismatch")
    topology = b45v.expected_topology(scaffold)
    if manifest["topology"] != topology:
        raise AssertionError("round topology mismatch")
    return topology


def verify_leaves(manifest: dict, blocks: list[tuple[int, ...]], offsets: list[int], topology: dict, d: int, k: int, cumulative: int) -> tuple[dict[int, dict], int, list[dict]]:
    leaves = manifest["leaf_full_sets"]
    if len(leaves) != len(topology["leaf_nodes"]):
        raise AssertionError("round leaf inventory mismatch")
    states: dict[int, dict] = {}
    events = []
    all_ids = list(range(len(blocks)))
    for event_index, (descriptor, leaf) in enumerate(zip(topology["leaf_nodes"], leaves)):
        factor_id = int(descriptor["factor_id"])
        leaf_boundary = b45v.boundary(blocks, [factor_id], [index for index in all_ids if index != factor_id], d)
        theta = len(leaf_boundary)
        coordinate_boundary = list(b3v.rref((1 << index for index in range(theta)), theta))
        generator = (
            [
                {"left": [], "right": coordinate_boundary, "value": 0},
                {"left": coordinate_boundary, "right": [], "value": 0},
            ]
            if theta
            else [{"left": [], "right": [], "value": 0}]
        )
        source = (
            "canonical full-boundary whole-factor trajectory"
            if theta
            else "canonical zero-boundary whole-factor trajectory"
        )
        partition = {
            "factor_id": factor_id,
            "factor_block_rref": list(blocks[factor_id]),
            "affine_offset": offsets[factor_id],
        }
        partition_digest = digest(partition)
        expected = {
            "node_id": factor_id,
            "factor_id": factor_id,
            "factor_block_rref": list(blocks[factor_id]),
            "affine_offset": offsets[factor_id],
            "boundary_rref_ambient": list(leaf_boundary),
            "boundary_coordinate_dimension": theta,
            "boundary_coordinate_rref": coordinate_boundary,
            "leaf_generator_coordinates": generator,
            "leaf_generator_ambient": b44v.lift_raw(generator, leaf_boundary, d),
            "partition_receipt": partition,
            "partition_receipt_digest": partition_digest,
            "provenance": {
                "kind": "WHOLE_FACTOR_LEAF",
                "factor_id": factor_id,
                "generator_source": source,
                "supplied_layout_used_for_discovery": False,
            },
        }
        for field, value in expected.items():
            if leaf[field] != value:
                raise AssertionError(f"round leaf mismatch: {field}")
        verify_b2_closure(leaf["full_set"])
        b45v.verify_receipt(
            leaf["output_receipt"],
            factor_id,
            "WHOLE_FACTOR_LEAF",
            [factor_id],
            leaf_boundary,
            leaf["full_set"],
            partition_digest,
        )
        ledger = leaf["full_set"]["ledger"]
        breakdown = {
            "b2_discovery_work": ledger["discovery_work"],
            "b2_work": ledger["work"],
        }
        cumulative += sum(breakdown.values())
        events.append(
            {
                "event_index": event_index,
                "node_id": factor_id,
                "kind": "LEAF_FULL_SET",
                "breakdown": breakdown,
                "work_delta": sum(breakdown.values()),
                "cumulative_work": cumulative,
            }
        )
        states[factor_id] = {
            "node_id": factor_id,
            "covered_factor_ids": [factor_id],
            "boundary": list(leaf_boundary),
            "closure": leaf["full_set"],
            "output_receipt": leaf["output_receipt"],
        }
    if manifest["work_ledger"]["leaf_full_set_events"] != events:
        raise AssertionError("round leaf work ledger mismatch")
    return states, cumulative, events


def verify_node_output(node: dict, context: dict, successful_groups: dict[str, list[int]], generators: Sequence[dict], deletions: Sequence[dict], generator_cursor: int, deletion_cursor: int, d: int, k: int, cumulative: int) -> tuple[dict, int, int, int, dict]:
    expected_generators = []
    expected_deletions = []
    for local_index, key in enumerate(sorted(successful_groups)):
        raw = json.loads(key)
        provenance = successful_groups[key]
        generator_id = generator_cursor + local_index
        expected_generators.append(
            {
                "record_kind": "SUCCESSFUL_GENERATOR",
                "node_id": node["node_id"],
                "generator_id": generator_id,
                "local_generator_index": local_index,
                "trajectory_parent_coordinates": raw,
                "trajectory_ambient": b44v.lift_raw(raw, context["parent"], d),
                "trajectory_digest": digest(raw),
                "provenance_attempt_ids": provenance,
                "canonical_retained_attempt_id": provenance[0],
            }
        )
        identity_path = [[index, index] for index in range(len(raw))]
        for removed_attempt in provenance[1:]:
            expected_deletions.append(
                {
                    "record_kind": "DUPLICATE_DELETION",
                    "node_id": node["node_id"],
                    "deletion_id": deletion_cursor + len(expected_deletions),
                    "local_deletion_index": len(expected_deletions),
                    "generator_id": generator_id,
                    "local_generator_index": local_index,
                    "trajectory_digest": digest(raw),
                    "removed_attempt_id": removed_attempt,
                    "retained_attempt_id": provenance[0],
                    "witness": {"path": identity_path, "path_length": len(identity_path)},
                    "reason": "IDENTICAL_REFINEMENT_OUTPUT",
                }
            )
    gen_range = b45v.range_values(node["record_ranges"]["generators"], generator_cursor, len(expected_generators))
    del_range = b45v.range_values(node["record_ranges"]["deletions"], deletion_cursor, len(expected_deletions))
    for actual, expected in zip((generators[index] for index in gen_range), expected_generators):
        if b45v.record_body(actual) != expected:
            raise AssertionError("round generator provenance mismatch")
    for actual, expected in zip((deletions[index] for index in del_range), expected_deletions):
        if b45v.record_body(actual) != expected:
            raise AssertionError("round deletion provenance mismatch")

    closure = node["node_up_k"]
    expected_inputs = [item["trajectory_parent_coordinates"] for item in expected_generators]
    if sorted(b45v.trajectory_key(raw) for raw in closure["input_generators"]) != sorted(b45v.trajectory_key(raw) for raw in expected_inputs):
        raise AssertionError("round B3 outputs not passed exactly into B2")
    verify_b2_closure(closure)
    generator_by_key = {b45v.trajectory_key(item["trajectory_parent_coordinates"]): item for item in expected_generators}
    expected_input_provenance = [
        {
            "input_generator_index": index,
            "generator_id": generator_by_key[b45v.trajectory_key(raw)]["generator_id"],
            "local_generator_index": generator_by_key[b45v.trajectory_key(raw)]["local_generator_index"],
        }
        for index, raw in enumerate(closure["input_generators"])
    ]
    expected_retained_provenance = [
        {
            "retained_generator_index": index,
            "generator_id": generator_by_key[b45v.trajectory_key(raw)]["generator_id"],
            "local_generator_index": generator_by_key[b45v.trajectory_key(raw)]["local_generator_index"],
        }
        for index, raw in enumerate(closure["retained_generators"])
    ]
    expected_entry_provenance = [
        {
            "entry_index": index,
            "source_generator_index": int(entry["source_generator_index"]),
            "generator_id": expected_retained_provenance[int(entry["source_generator_index"])]["generator_id"],
        }
        for index, entry in enumerate(closure["entries"])
    ]
    if node["input_generator_provenance"] != expected_input_provenance:
        raise AssertionError("round B2 input provenance mismatch")
    if node["retained_generator_provenance"] != expected_retained_provenance:
        raise AssertionError("round B2 retained provenance mismatch")
    if node["entry_provenance"] != expected_entry_provenance:
        raise AssertionError("round B2 entry provenance mismatch")
    if node["work_ledger"]["cumulative_work_before_node_b2"] != cumulative:
        raise AssertionError("round pre-B2 cumulative mismatch")
    breakdown = {
        "b2_discovery_work": closure["ledger"]["discovery_work"],
        "b2_work": closure["ledger"]["work"],
    }
    if node["work_ledger"]["node_b2_breakdown"] != breakdown:
        raise AssertionError("round B2 work breakdown mismatch")
    cumulative += sum(breakdown.values())
    if node["work_ledger"]["cumulative_work_at_node_end"] != cumulative:
        raise AssertionError("round node cumulative mismatch")
    b45v.verify_receipt(
        node["output_receipt"],
        node["node_id"],
        node["kind"],
        node["covered_factor_ids"],
        context["parent"],
        closure,
        context["partition_digest"],
    )
    state = {
        "node_id": node["node_id"],
        "covered_factor_ids": node["covered_factor_ids"],
        "boundary": list(context["parent"]),
        "closure": closure,
        "output_receipt": node["output_receipt"],
    }
    return state, generator_cursor + len(expected_generators), deletion_cursor + len(expected_deletions), cumulative, {
        "unique_generators": len(expected_generators),
        "duplicate_deletions": len(expected_deletions),
    }


def verify_round(root: Path, manifest: dict, blocks: list[tuple[int, ...]], offsets: list[int], previous_order: list[int], d: int, k: int, expected_start: int) -> dict:
    verify_round_manifest_integrity(manifest)
    topology = verify_scaffold(manifest, blocks, offsets, previous_order, d, k)
    if manifest["work_ledger"]["cumulative_work_at_round_start"] != expected_start:
        raise AssertionError("round cumulative start mismatch")
    scaffold_work = int(manifest["scaffold_case"]["charged_work"])
    cumulative = expected_start + scaffold_work
    if manifest["work_ledger"]["scaffold_event"] != {
        "kind": "B4.2_SCAFFOLD_CONSTRUCTION",
        "work_delta": scaffold_work,
        "cumulative_work": cumulative,
        "semantic_digest": manifest["scaffold_case"]["semantic_digest"],
    }:
        raise AssertionError("round scaffold work event mismatch")
    states, cumulative, leaf_events = verify_leaves(manifest, blocks, offsets, topology, d, k, cumulative)

    pairs = list(b45v.ChunkReader(root, manifest, "PAIRS"))
    generators = list(b45v.ChunkReader(root, manifest, "GENERATORS"))
    deletions = list(b45v.ChunkReader(root, manifest, "DELETIONS"))
    attempts = iter(b45v.ChunkReader(root, manifest, "REFINEMENTS"))
    pair_cursor = attempt_cursor = generator_cursor = deletion_cursor = 0
    node_intervals = []
    node_audits = []
    attempts_by_id = {}
    pairs_by_id = {int(item["pair_id"]): item for item in pairs}
    generators_by_id = {int(item["generator_id"]): item for item in generators}

    for sequence_index, node in enumerate(manifest["node_results"]):
        descriptor = topology["internal_nodes"][sequence_index]
        left_state = states[int(descriptor["child_node_ids"][0])]
        right_state = states[int(descriptor["child_node_ids"][1])]
        context = b45v.verify_node_header(
            node,
            descriptor,
            sequence_index,
            left_state,
            right_state,
            d,
            blocks,
            offsets,
            manifest["scaffold_case"]["scaffold_order"],
            cumulative,
        )
        left_entries = left_state["closure"]["entries"]
        right_entries = right_state["closure"]["entries"]
        pair_count = len(left_entries) * len(right_entries)
        pair_range = b45v.range_values(node["record_ranges"]["pairs"], pair_cursor, pair_count)
        successful_groups: dict[str, list[int]] = defaultdict(list)
        successful = failed = raw_precompact = 0
        node_attempt_start = attempt_cursor
        for local_pair_index, pair_index in enumerate(pair_range):
            pair = pairs[pair_index]
            left, right, expand_breakdown = b45v.verify_pair(
                pair,
                node,
                context,
                left_state,
                right_state,
                d,
                pair_index,
                local_pair_index,
            )
            cumulative += sum(expand_breakdown.values())
            if pair["cumulative_work_after_expand"] != cumulative:
                raise AssertionError("round pair cumulative mismatch")
            claimed_paths = []
            for _ in range(pair["lattice_path_count"]):
                try:
                    attempt = next(attempts)
                except StopIteration as exc:
                    raise AssertionError("missing round refinement") from exc
                if int(attempt["attempt_id"]) != attempt_cursor:
                    raise AssertionError("round refinement id gap")
                breakdown, successful_key = b45v.verify_refinement(
                    attempt,
                    pair,
                    node,
                    context,
                    left,
                    right,
                    d,
                    k,
                    attempt_cursor,
                    attempt_cursor - node_attempt_start,
                )
                cumulative += sum(breakdown.values())
                if attempt["cumulative_work"] != cumulative:
                    raise AssertionError("round refinement cumulative mismatch")
                attempts_by_id[attempt_cursor] = attempt
                claimed_paths.append(tuple(tuple(cell) for cell in attempt["lattice_path"]))
                raw_precompact += int(attempt["join"]["raw_length"])
                if successful_key is None:
                    failed += 1
                else:
                    successful += 1
                    successful_groups[successful_key].append(attempt_cursor)
                attempt_cursor += 1
            if tuple(sorted(claimed_paths)) != b3v.paths(len(left), len(right)):
                raise AssertionError("round lattice path coverage mismatch")
        pair_cursor += pair_count
        attempt_count = attempt_cursor - node_attempt_start
        b45v.range_values(node["record_ranges"]["refinements"], node_attempt_start, attempt_count)
        state, generator_cursor, deletion_cursor, cumulative, counts = verify_node_output(
            node,
            context,
            successful_groups,
            generators,
            deletions,
            generator_cursor,
            deletion_cursor,
            d,
            k,
            cumulative,
        )
        states[int(node["node_id"])] = state
        audit = {
            "child_full_set_entries": [len(left_entries), len(right_entries)],
            "child_pairs_processed": pair_count,
            "lattice_paths_processed": attempt_count,
            "successful_refinements": successful,
            "failed_refinements": failed,
            "raw_precompact_join_statistics": raw_precompact,
            "unique_successful_generators": counts["unique_generators"],
            "duplicate_successful_outputs_deleted": counts["duplicate_deletions"],
            "b2_dominance_deletions": len(node["node_up_k"]["removals"]),
            "retained_generators": len(node["node_up_k"]["retained_generators"]),
            "final_up_k_entries": int(node["node_up_k"]["entry_count"]),
            "cumulative_work_delta": cumulative - node["work_ledger"]["cumulative_work_at_node_start"],
        }
        if node["audit"] != audit:
            raise AssertionError("round node audit mismatch")
        node_audits.append(audit)
        node_intervals.append({
            "node_id": node["node_id"],
            "start": node["work_ledger"]["cumulative_work_at_node_start"],
            "end": cumulative,
        })
    try:
        next(attempts)
    except StopIteration:
        pass
    else:
        raise AssertionError("extra round refinements")
    if pair_cursor != len(pairs) or generator_cursor != len(generators) or deletion_cursor != len(deletions):
        raise AssertionError("extra round transcript records")
    if len(manifest["node_results"]) != len(topology["internal_nodes"]):
        raise AssertionError("frozen round stopped before root")
    root_state = states[int(topology["root_node_id"])]
    expected_execution = {
        "status": "ROOT_FULL_SET_COMPUTED",
        "processed_internal_node_ids": [item["node_id"] for item in manifest["node_results"]],
        "stopped_node_id": None,
        "stop": None,
        "root_node_id": topology["root_node_id"],
        "root_full_set_receipt": root_state["output_receipt"],
    }
    if manifest["execution"] != expected_execution:
        raise AssertionError("round execution terminal mismatch")
    if manifest["work_ledger"] != {
        "cumulative_work_at_round_start": expected_start,
        "scaffold_event": manifest["work_ledger"]["scaffold_event"],
        "leaf_full_set_events": leaf_events,
        "node_intervals": node_intervals,
        "cumulative_work_after_executor": cumulative,
        "monotone_by_construction": True,
    }:
        raise AssertionError("round global work ledger mismatch")
    audit = {
        "leaf_full_sets": len(manifest["leaf_full_sets"]),
        "internal_nodes_processed": len(manifest["node_results"]),
        "child_pairs_processed": sum(item["child_pairs_processed"] for item in node_audits),
        "lattice_paths_processed": sum(item["lattice_paths_processed"] for item in node_audits),
        "successful_refinements": sum(item["successful_refinements"] for item in node_audits),
        "failed_refinements": sum(item["failed_refinements"] for item in node_audits),
        "raw_precompact_join_statistics": sum(item["raw_precompact_join_statistics"] for item in node_audits),
        "unique_successful_generators": sum(item["unique_successful_generators"] for item in node_audits),
        "duplicate_successful_outputs_deleted": sum(item["duplicate_successful_outputs_deleted"] for item in node_audits),
        "b2_dominance_deletions": sum(item["b2_dominance_deletions"] for item in node_audits),
        "retained_generators_across_nodes": sum(item["retained_generators"] for item in node_audits),
        "root_up_k_entries": int(root_state["output_receipt"]["entry_count"]),
        "cumulative_work": cumulative,
        "chunk_count": manifest["chunking"]["chunk_count"],
        "failures": 0,
    }
    if manifest["audit"] != audit:
        raise AssertionError("round global audit mismatch")
    strict = manifest["strict_boundary"]
    if strict["terminal_completeness_proved"] or strict["found_layout_enabled"] or strict["no_layout_at_cap_enabled"]:
        raise AssertionError("round terminal boundary overclaimed")
    return {
        "topology": topology,
        "states": states,
        "pairs": pairs_by_id,
        "attempts": attempts_by_id,
        "generators": generators_by_id,
        "cumulative_after_executor": cumulative,
        "audit": audit,
    }


def verify_b2_witness(lower_raw: Sequence[dict], upper_raw: Sequence[dict], witness: dict, dim: int) -> None:
    lower = b2v.trajectory(lower_raw, dim)
    upper = b2v.trajectory(upper_raw, dim)
    path = b2v.canonical_path(lower, upper)
    expected = None if path is None else b2v.witness_payload(path)
    if witness != expected:
        raise AssertionError("reconstruction B2 witness mismatch")


def accepting_root_indices(root_node: dict, k: int) -> list[int]:
    out = []
    for index, entry in enumerate(root_node["node_up_k"]["entries"]):
        trajectory = entry["trajectory"]
        if max(int(item["value"]) for item in trajectory) > k:
            continue
        if any(item["left"] or item["right"] for item in trajectory):
            continue
        out.append(index)
    return out


def trace_entry(node_id: int, entry_index: int, manifest: dict, transcript: dict, active: set[tuple[int, int]], work: list[int], events: list[dict]) -> dict:
    key = (node_id, entry_index)
    if key in active:
        raise AssertionError("cyclic reconstruction ancestry")
    active.add(key)
    work[0] += 1
    events.append({
        "event_index": len(events),
        "kind": "ENTRY_LOOKUP",
        "amount": 1,
        "cumulative_work": work[0],
        "node_id": node_id,
        "entry_index": entry_index,
    })
    leaves = {int(item["node_id"]): item for item in manifest["leaf_full_sets"]}
    nodes = {int(item["node_id"]): item for item in manifest["node_results"]}
    if node_id in leaves:
        leaf = leaves[node_id]
        closure = leaf["full_set"]
        entry = closure["entries"][entry_index]
        source_index = int(entry["source_generator_index"])
        source = closure["retained_generators"][source_index]
        verify_b2_witness(source, entry["trajectory"], entry["witness"], int(closure["ambient_dim"]))
        amount = int(entry["witness"]["path_length"])
        work[0] += amount
        events.append({
            "event_index": len(events),
            "kind": "B2_EXTENSION_PATH_VERTICES",
            "amount": amount,
            "cumulative_work": work[0],
            "node_id": node_id,
            "entry_index": entry_index,
        })
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

    node = nodes[node_id]
    entry = node["node_up_k"]["entries"][entry_index]
    source_index = int(entry["source_generator_index"])
    source = node["node_up_k"]["retained_generators"][source_index]
    verify_b2_witness(source, entry["trajectory"], entry["witness"], int(node["node_up_k"]["ambient_dim"]))
    amount = int(entry["witness"]["path_length"])
    work[0] += amount
    events.append({
        "event_index": len(events),
        "kind": "B2_EXTENSION_PATH_VERTICES",
        "amount": amount,
        "cumulative_work": work[0],
        "node_id": node_id,
        "entry_index": entry_index,
    })
    provenance = node["entry_provenance"][entry_index]
    generator_id = int(provenance["generator_id"])
    generator = transcript["generators"][generator_id]
    work[0] += 1
    events.append({
        "event_index": len(events),
        "kind": "GENERATOR_PROVENANCE_LOOKUP",
        "amount": 1,
        "cumulative_work": work[0],
        "node_id": node_id,
        "generator_id": generator_id,
    })
    if generator["trajectory_parent_coordinates"] != source:
        raise AssertionError("reconstruction retained generator mismatch")
    attempt_id = int(generator["canonical_retained_attempt_id"])
    attempt = transcript["attempts"][attempt_id]
    work[0] += 1
    events.append({
        "event_index": len(events),
        "kind": "REFINEMENT_PROVENANCE_LOOKUP",
        "amount": 1,
        "cumulative_work": work[0],
        "node_id": node_id,
        "attempt_id": attempt_id,
    })
    if attempt["status"] != "SUCCESS" or attempt["output_parent_coordinates"] != source:
        raise AssertionError("reconstruction canonical attempt mismatch")
    pair_id = int(attempt["pair_id"])
    pair = transcript["pairs"][pair_id]
    work[0] += 1
    events.append({
        "event_index": len(events),
        "kind": "PAIR_PROVENANCE_LOOKUP",
        "amount": 1,
        "cumulative_work": work[0],
        "node_id": node_id,
        "pair_id": pair_id,
    })
    left_child, right_child = [int(value) for value in node["child_node_ids"]]
    left = trace_entry(left_child, int(pair["left_entry_index"]), manifest, transcript, active, work, events)
    right = trace_entry(right_child, int(pair["right_entry_index"]), manifest, transcript, active, work, events)
    order = list(left["order"]) + list(right["order"])
    work[0] += len(order)
    events.append({
        "event_index": len(events),
        "kind": "RECONSTRUCTION_BRANCH_COMBINE",
        "amount": len(order),
        "cumulative_work": work[0],
        "node_id": node_id,
    })
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


def verify_reconstruction(reconstruction: dict, manifest: dict, transcript: dict, blocks: list[tuple[int, ...]], offsets: list[int], d: int, k: int) -> dict:
    verify_object_digest(reconstruction, "reconstruction_digest")
    root_id = int(manifest["execution"]["root_node_id"])
    root_node = next(item for item in manifest["node_results"] if int(item["node_id"]) == root_id)
    accepted = accepting_root_indices(root_node, k)
    selected = min(accepted, key=lambda index: (digest(root_node["node_up_k"]["entries"][index]), index))
    expected_selection = {
        "accepting_root_entry_count": len(accepted),
        "selected_root_entry_index": selected,
        "rule": "MINIMUM_SHA256_THEN_ENTRY_INDEX_AMONG_EMPTY_BOUNDARY_WIDTH_AT_MOST_K",
    }
    if reconstruction["root_selection"] != expected_selection:
        raise AssertionError("round root selection mismatch")
    work = [int(manifest["audit"]["cumulative_work"])]
    events: list[dict] = []
    receipt = trace_entry(root_id, selected, manifest, transcript, set(), work, events)
    order = [int(value) for value in receipt["order"]]
    cuts = exact_cut_widths(blocks, order, d)
    work[0] += len(cuts)
    events.append({
        "event_index": len(events),
        "kind": "EXACT_LAYOUT_CUT_RECOMPUTATIONS",
        "amount": len(cuts),
        "cumulative_work": work[0],
        "order": order,
    })
    maximum_width = max(item["width"] for item in cuts)
    layout = [
        {
            "position": position,
            "factor_id": factor_id,
            "normal_space_block_rref": list(blocks[factor_id]),
            "affine_offset": offsets[factor_id],
        }
        for position, factor_id in enumerate(order)
    ]
    expected = {
        "status": "ROUND_LAYOUT_WITNESS_RECONSTRUCTED",
        "root_selection": expected_selection,
        "reconstruction_receipt": receipt,
        "reconstructed_factor_order": order,
        "reconstructed_layout": layout,
        "exact_cut_transcript": cuts,
        "exact_maximum_width": maximum_width,
        "reconstruction_work": work[0] - int(manifest["audit"]["cumulative_work"]),
        "cumulative_work_after_reconstruction": work[0],
        "work_events": events,
        "found_layout": False,
        "no_layout_at_cap": False,
        "terminal": TERMINAL,
    }
    body = copy.deepcopy(reconstruction)
    body.pop("reconstruction_digest", None)
    if body != expected:
        raise AssertionError("round reconstruction transcript mismatch")
    if maximum_width > k:
        raise AssertionError("round reconstructed order exceeds k")
    return expected


def verify_cycle(root: Path, artifact: dict) -> dict:
    verify_object_digest(artifact, "manifest_digest")
    if artifact.get("schema") != SCHEMA or artifact.get("source_head") != SOURCE_HEAD:
        raise AssertionError("cycle schema/source mismatch")
    if artifact["fixture"] != EXPECTED_FIXTURE:
        raise AssertionError("cycle fixture changed")
    if artifact["result"] != LOCAL_RESULT:
        raise AssertionError("cycle local result changed")
    certificate_bytes = len(canonical_json(artifact)) + 1
    if artifact["certificate_accounting"]["fixed_point_serialized_bytes"] != certificate_bytes:
        raise AssertionError("cycle fixed-point byte mismatch")
    computational_work = artifact["work_ledger"]["cumulative_work_before_certificate"]
    if artifact["work_ledger"]["certificate_byte_charge"] != certificate_bytes:
        raise AssertionError("cycle certificate byte charge mismatch")
    if artifact["work_ledger"]["cumulative_work_final"] != computational_work + certificate_bytes:
        raise AssertionError("cycle final work mismatch")

    d = int(EXPECTED_FIXTURE["ambient_dimension"])
    k = int(EXPECTED_FIXTURE["k"])
    all_blocks = [b3v.rref(block, d) for block in EXPECTED_FIXTURE["whole_factor_blocks"]]
    all_offsets = [int(value) for value in EXPECTED_FIXTURE["affine_offsets"]]
    previous_order = [0]
    initial_cuts = exact_cut_widths(all_blocks[:1], previous_order, d)
    initial_event = {
        "kind": "INITIAL_LAYOUT_REPLAY",
        "factor_order": previous_order,
        "exact_cut_transcript": initial_cuts,
        "work_delta": len(initial_cuts),
        "cumulative_work": len(initial_cuts),
    }
    if artifact["initial_layout"] != initial_event:
        raise AssertionError("cycle initial layout mismatch")
    cumulative = len(initial_cuts)
    round_summaries = []
    total_raw = total_compressed = total_chunks = 0
    totals = defaultdict(int)

    if artifact["round_count"] != len(all_blocks) - 1 or len(artifact["rounds"]) != artifact["round_count"]:
        raise AssertionError("cycle round inventory mismatch")
    for round_size, summary in zip(range(2, len(all_blocks) + 1), artifact["rounds"]):
        if summary["round_index"] != round_size - 1 or summary["round_size"] != round_size:
            raise AssertionError("cycle round identity mismatch")
        round_root = root / summary["directory"]
        manifest = json.loads((round_root / "manifest.json").read_text())
        reconstruction = json.loads((round_root / "reconstruction.json").read_text())
        blocks = all_blocks[:round_size]
        offsets = all_offsets[:round_size]
        transcript = verify_round(round_root, manifest, blocks, offsets, previous_order, d, k, cumulative)
        expected_reconstruction = verify_reconstruction(reconstruction, manifest, transcript, blocks, offsets, d, k)
        expected_transition = {
            "round_index": round_size - 1,
            "round_size": round_size,
            "new_factor_id": round_size - 1,
            "previous_factor_order": previous_order,
            "previous_order_digest": digest(previous_order),
            "scaffold_semantic_digest": manifest["scaffold_case"]["semantic_digest"],
            "executor_manifest_digest": manifest["manifest_digest"],
            "executor_transcript_root_digest": manifest["chunking"]["transcript_root_digest"],
            "reconstruction_digest": reconstruction["reconstruction_digest"],
            "reconstructed_factor_order": expected_reconstruction["reconstructed_factor_order"],
            "exact_maximum_width": expected_reconstruction["exact_maximum_width"],
            "grouped_partition_preserved": True,
            "affine_offsets_preserved": True,
            "cumulative_work_at_round_start": cumulative,
            "cumulative_work_after_executor": transcript["cumulative_after_executor"],
            "cumulative_work_after_reconstruction": expected_reconstruction["cumulative_work_after_reconstruction"],
            "terminal": TERMINAL,
        }
        expected_transition["transition_digest"] = digest(expected_transition)
        if summary["transition"] != expected_transition:
            raise AssertionError("cycle transition receipt mismatch")
        expected_summary = {
            "round_index": round_size - 1,
            "round_size": round_size,
            "directory": summary["directory"],
            "transition": expected_transition,
            "executor_audit": transcript["audit"],
            "reconstruction_summary": {
                "root_selection": expected_reconstruction["root_selection"],
                "reconstructed_factor_order": expected_reconstruction["reconstructed_factor_order"],
                "exact_cut_transcript": expected_reconstruction["exact_cut_transcript"],
                "exact_maximum_width": expected_reconstruction["exact_maximum_width"],
                "reconstruction_work": expected_reconstruction["reconstruction_work"],
                "reconstruction_digest": reconstruction["reconstruction_digest"],
            },
        }
        if summary != expected_summary:
            raise AssertionError("cycle round summary mismatch")
        round_summaries.append(expected_summary)
        cumulative = expected_reconstruction["cumulative_work_after_reconstruction"]
        previous_order = list(expected_reconstruction["reconstructed_factor_order"])
        total_raw += manifest["chunking"]["uncompressed_chunk_bytes"]
        total_compressed += manifest["chunking"]["compressed_chunk_bytes"]
        total_chunks += manifest["chunking"]["chunk_count"]
        for field in (
            "child_pairs_processed",
            "lattice_paths_processed",
            "failed_refinements",
            "successful_refinements",
            "raw_precompact_join_statistics",
        ):
            totals[field] += transcript["audit"][field]

    final_cuts = exact_cut_widths(all_blocks, previous_order, d)
    if artifact["rounds"] != round_summaries:
        raise AssertionError("cycle round list mismatch")
    if artifact["all_rounds_executed"] is not True:
        raise AssertionError("cycle all-round claim missing")
    if artifact["final_reconstructed_factor_order"] != previous_order:
        raise AssertionError("cycle final order mismatch")
    if artifact["final_exact_cut_transcript"] != final_cuts:
        raise AssertionError("cycle final cut replay mismatch")
    if artifact["final_exact_maximum_width"] != max(item["width"] for item in final_cuts):
        raise AssertionError("cycle final width mismatch")
    expected_audit = {
        "rounds": len(round_summaries),
        "scaffolds_constructed": len(round_summaries),
        "root_full_sets_computed": len(round_summaries),
        "layouts_reconstructed": len(round_summaries),
        "child_pairs_processed": totals["child_pairs_processed"],
        "lattice_paths_processed": totals["lattice_paths_processed"],
        "failed_refinements": totals["failed_refinements"],
        "successful_refinements": totals["successful_refinements"],
        "raw_precompact_join_statistics": totals["raw_precompact_join_statistics"],
        "chunk_count": total_chunks,
        "failures": 0,
    }
    if artifact["audit"] != expected_audit:
        raise AssertionError("cycle audit mismatch")
    expected_work = {
        "initial_layout_work": initial_event["work_delta"],
        "round_transitions": [item["transition"] for item in round_summaries],
        "cumulative_work_before_certificate": cumulative,
        "certificate_byte_charge": certificate_bytes,
        "cumulative_work_final": cumulative + certificate_bytes,
        "monotone_across_rounds": True,
    }
    if artifact["work_ledger"] != expected_work:
        raise AssertionError("cycle work ledger mismatch")
    expected_certificate = {
        "round_chunk_count": total_chunks,
        "round_uncompressed_chunk_bytes": total_raw,
        "round_compressed_chunk_bytes": total_compressed,
        "fixed_point_serialized_bytes": certificate_bytes,
    }
    if artifact["certificate_accounting"] != expected_certificate:
        raise AssertionError("cycle certificate accounting mismatch")
    strict = artifact["strict_boundary"]
    if strict != {
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
    }:
        raise AssertionError("cycle strict boundary mismatch")
    return {
        "rounds": len(round_summaries),
        "final_order": previous_order,
        "final_width": max(item["width"] for item in final_cuts),
        "failed_refinements": expected_audit["failed_refinements"],
        "cumulative_work": artifact["work_ledger"]["cumulative_work_final"],
    }


def rebind_artifact(artifact: dict) -> dict:
    out = copy.deepcopy(artifact)
    computational = int(out["work_ledger"]["cumulative_work_before_certificate"])
    out["manifest_digest"] = "0" * 64
    out["certificate_accounting"]["fixed_point_serialized_bytes"] = 0
    out["work_ledger"]["certificate_byte_charge"] = 0
    out["work_ledger"]["cumulative_work_final"] = computational
    for _ in range(64):
        body = copy.deepcopy(out)
        body.pop("manifest_digest", None)
        out["manifest_digest"] = digest(body)
        size = len(canonical_json(out)) + 1
        changed = False
        for container, field, value in (
            (out["certificate_accounting"], "fixed_point_serialized_bytes", size),
            (out["work_ledger"], "certificate_byte_charge", size),
            (out["work_ledger"], "cumulative_work_final", computational + size),
        ):
            if container[field] != value:
                container[field] = value
                changed = True
        if not changed:
            body = copy.deepcopy(out)
            body.pop("manifest_digest", None)
            out["manifest_digest"] = digest(body)
            if len(canonical_json(out)) + 1 == size:
                return out
    raise AssertionError("tamper artifact fixed point failed")


def expect_rejection(label: str, root: Path, artifact: dict) -> None:
    try:
        verify_cycle(root, artifact)
    except AssertionError:
        return
    raise AssertionError(f"digest-repaired {label} tamper accepted")


def tamper_self_tests(root: Path, artifact: dict) -> int:
    final_order = copy.deepcopy(artifact)
    final_order["final_reconstructed_factor_order"] = list(reversed(final_order["final_reconstructed_factor_order"]))
    expect_rejection("final order", root, rebind_artifact(final_order))

    transition = copy.deepcopy(artifact)
    transition["rounds"][1]["transition"]["cumulative_work_at_round_start"] += 1
    transition["rounds"][1]["transition"].pop("transition_digest", None)
    transition["rounds"][1]["transition"]["transition_digest"] = digest(transition["rounds"][1]["transition"])
    transition["work_ledger"]["round_transitions"] = [item["transition"] for item in transition["rounds"]]
    expect_rejection("round cumulative reset", root, rebind_artifact(transition))

    offsets = copy.deepcopy(artifact)
    offsets["fixture"]["affine_offsets"][2] ^= 1
    expect_rejection("affine offset", root, rebind_artifact(offsets))

    terminal = copy.deepcopy(artifact)
    terminal["strict_boundary"]["found_layout_enabled"] = True
    expect_rejection("premature FOUND_LAYOUT", root, rebind_artifact(terminal))
    return 4


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("cycle_dir")
    parser.add_argument("--tamper-self-test", action="store_true")
    args = parser.parse_args()
    root = Path(args.cycle_dir)
    artifact = json.loads((root / "artifact.json").read_text())
    result = verify_cycle(root, artifact)
    tamper_count = tamper_self_tests(root, artifact) if args.tamper_self_test else 0
    print("VERIFIED C049.1 B4.6.2 FULL ITERATIVE COMPRESSION CYCLE")
    print("ROUNDS_REPLAYED =", result["rounds"])
    print("FINAL_ORDER =", result["final_order"])
    print("FINAL_WIDTH =", result["final_width"])
    print("FAILED_REFINEMENTS_REPLAYED =", result["failed_refinements"])
    print("CUMULATIVE_WORK =", result["cumulative_work"])
    print("DIGEST_REPAIRED_TAMPER_CONTROLS =", tamper_count)
    print("GLOBAL_TERMINAL =", TERMINAL)


if __name__ == "__main__":
    main()
