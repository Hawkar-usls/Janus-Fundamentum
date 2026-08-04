#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import hashlib
import itertools
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Sequence

import janus_c049_1_b4_5_bottom_up_scaffold_executor as engine
from janus_c049_1_b2_up_k_core import CapabilityExceeded
from janus_c049_1_b4_2_3k_scaffold import scaffold

SCHEMA = "C049.1-B4.6.3-NEGATIVE-ROOT-ENGINE-REPLAY-v1"
TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"
B2_CAP = 2_000_000

FIXTURE = {
    "name": "SIX_LINE_DIMENSION_TWO_BOTTLENECK_NEGATIVE",
    "d": 3,
    "k": 1,
    "blocks": [[2], [4], [6], [3], [5], [1]],
    "affine_offsets": [0, 0, 0, 0, 0, 0],
    "previous_order": [0, 1, 2, 3, 4],
    "new_factor": 5,
    "expected_previous_width": 1,
    "expected_full_minimum_width": 2,
    "expected_scaffold_width_vector": [1, 2, 2, 2, 1],
}


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def xor_basis(rows: Iterable[int], d: int) -> tuple[int, ...]:
    table: dict[int, int] = {}
    limit = 1 << d
    for raw in rows:
        x = int(raw)
        if x < 0 or x >= limit:
            raise ValueError("vector outside ambient space")
        while x:
            pivot = x.bit_length() - 1
            if pivot in table:
                x ^= table[pivot]
                continue
            table[pivot] = x
            for other, row in list(table.items()):
                if other != pivot and ((row >> pivot) & 1):
                    table[other] = row ^ x
            break
    for pivot in sorted(table):
        row = table[pivot]
        for other in sorted(table, reverse=True):
            if other != pivot and ((table[other] >> pivot) & 1):
                table[other] ^= row
    return tuple(table[pivot] for pivot in sorted(table, reverse=True))


def intersection_dimension(left: Sequence[int], right: Sequence[int], d: int) -> int:
    left_basis = xor_basis(left, d)
    right_basis = xor_basis(right, d)
    joined = xor_basis((*left_basis, *right_basis), d)
    return len(left_basis) + len(right_basis) - len(joined)


def layout_width(blocks: Sequence[Sequence[int]], order: Sequence[int], d: int) -> tuple[int, list[int]]:
    vector = []
    for cut in range(1, len(order)):
        left = [row for factor in order[:cut] for row in blocks[factor]]
        right = [row for factor in order[cut:] for row in blocks[factor]]
        vector.append(intersection_dimension(left, right, d))
    return max(vector, default=0), vector


def exhaustive_fixture_oracle() -> dict:
    blocks = FIXTURE["blocks"]
    d = int(FIXTURE["d"])
    k = int(FIXTURE["k"])
    records = []
    for order in itertools.permutations(range(len(blocks))):
        maximum, vector = layout_width(blocks, order, d)
        records.append({"order": list(order), "maximum_width": maximum, "width_vector": vector})
    previous_maximum, previous_vector = layout_width(
        blocks[:-1], FIXTURE["previous_order"], d
    )
    accepting = [item for item in records if item["maximum_width"] <= k]
    minimum = min(item["maximum_width"] for item in records)
    if previous_maximum != FIXTURE["expected_previous_width"]:
        raise AssertionError("previous layout width drift")
    if minimum != FIXTURE["expected_full_minimum_width"] or accepting:
        raise AssertionError("negative fixture oracle drift")
    return {
        "permutation_count": len(records),
        "minimum_width": minimum,
        "accepting_layout_count": len(accepting),
        "previous_width": previous_maximum,
        "previous_width_vector": previous_vector,
        "all_layouts_digest": digest(records),
    }


def selected_negative_scaffold() -> dict:
    record = scaffold(
        [tuple(block) for block in FIXTURE["blocks"]],
        tuple(FIXTURE["previous_order"]),
        int(FIXTURE["new_factor"]),
        int(FIXTURE["d"]),
        int(FIXTURE["k"]),
        FIXTURE["affine_offsets"],
    )
    if record["terminal"] != "SCAFFOLD_3K_CERTIFIED":
        raise AssertionError("negative fixture scaffold not certified")
    profile = [int(item["width"]) for item in record["candidate_edges"]]
    if profile != FIXTURE["expected_scaffold_width_vector"]:
        raise AssertionError("negative scaffold width profile drift")
    return record


class B2PrefixOpen(RuntimeError):
    def __init__(self, source: CapabilityExceeded, ledger: dict, generator_count: int, ambient_dim: int, k: int):
        super().__init__(source.terminal)
        self.source = source
        self.ledger = ledger
        self.generator_count = generator_count
        self.ambient_dim = ambient_dim
        self.k = k


def iter_records(root: Path, manifest: dict, kind: str):
    for metadata in manifest["chunking"]["chunk_groups"][kind]:
        payload = json.loads(gzip.decompress((root / metadata["filename"]).read_bytes()))
        if payload["kind"] != kind or payload["record_count"] != metadata["record_count"]:
            raise AssertionError("chunk metadata mismatch")
        yield from payload["records"]


def prefix_receipt(root: Path, manifest: dict) -> dict:
    stop_node = int(manifest["execution"]["stop"]["node_id"])
    counts = defaultdict(int)
    paths = 0
    successful_ids = set()
    provenance = []
    duplicate_pairs = []
    for pair in iter_records(root, manifest, "PAIRS"):
        if int(pair["node_id"]) == stop_node:
            counts["pairs"] += 1
            paths += int(pair["lattice_path_count"])
    for refinement in iter_records(root, manifest, "REFINEMENTS"):
        if int(refinement["node_id"]) != stop_node:
            continue
        counts["refinements"] += 1
        if refinement["status"] == "SUCCESS":
            counts["successful"] += 1
            successful_ids.add(int(refinement["attempt_id"]))
        elif refinement["status"] == "FAILED_WIDTH_CAP":
            counts["failed"] += 1
        else:
            raise AssertionError("unknown refinement status")
    for generator in iter_records(root, manifest, "GENERATORS"):
        if int(generator["node_id"]) != stop_node:
            continue
        counts["generators"] += 1
        provenance.extend(int(value) for value in generator["provenance_attempt_ids"])
    for deletion in iter_records(root, manifest, "DELETIONS"):
        if int(deletion["node_id"]) != stop_node:
            continue
        counts["deletions"] += 1
        duplicate_pairs.append(
            [int(deletion["generator_id"]), int(deletion["removed_attempt_id"])]
        )
        if deletion["reason"] != "IDENTICAL_REFINEMENT_OUTPUT":
            raise AssertionError("unexpected deletion before B2 closure")
    return {
        "node_id": stop_node,
        "pair_records": counts["pairs"],
        "delannoy_paths_from_pairs": paths,
        "refinement_records": counts["refinements"],
        "successful_refinements": counts["successful"],
        "failed_refinements": counts["failed"],
        "generator_records": counts["generators"],
        "provenance_occurrences": len(provenance),
        "distinct_provenance_attempts": len(set(provenance)),
        "successful_attempt_ids_match_provenance": set(provenance) == successful_ids,
        "duplicate_deletion_records": counts["deletions"],
        "duplicate_pairs_digest": digest(sorted(duplicate_pairs)),
        "pair_path_equality": paths == counts["refinements"],
        "refinement_partition_equality": counts["refinements"]
        == counts["successful"] + counts["failed"],
        "provenance_partition_equality": len(provenance)
        == len(set(provenance))
        == counts["successful"]
        and set(provenance) == successful_ids,
    }


def build(output_dir: Path) -> dict:
    oracle = exhaustive_fixture_oracle()
    original_selected = engine.selected_scaffold
    original_up_k = engine.up_k_closure
    original_execute = engine.execute_node
    original_cap = engine.CAP

    def bounded_up_k(generators, ambient_dim, k, ledger):
        try:
            return original_up_k(generators, ambient_dim, k, ledger)
        except CapabilityExceeded as exc:
            raise B2PrefixOpen(
                exc,
                ledger.snapshot(),
                len(generators),
                int(ambient_dim),
                int(k),
            ) from exc

    def guarded_execute(descriptor, sequence_index, left_state, right_state, scaffold_record, writers, cumulative, capability):
        try:
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
        except B2PrefixOpen as opened:
            source = opened.source
            return {
                "status": "OPEN_AT_NODE_B2_CAPABILITY",
                "node_id": int(descriptor["node_id"]),
                "reason": "B2_SEMANTIC_UP_K_CAPABILITY_EXCEEDED",
                "required": int(source.attempted),
                "cap": int(source.cap),
                "counter": source.counter,
                "b2_terminal": source.terminal,
                "b2_ledger_prefix": opened.ledger,
                "input_generator_count": opened.generator_count,
                "boundary_coordinate_dimension": opened.ambient_dim,
                "k": opened.k,
                "terminal": TERMINAL,
                "no_layout_at_cap": False,
            }

    try:
        engine.selected_scaffold = selected_negative_scaffold
        engine.up_k_closure = bounded_up_k
        engine.execute_node = guarded_execute
        engine.CAP = B2_CAP
        manifest = engine.build(output_dir)
    finally:
        engine.selected_scaffold = original_selected
        engine.up_k_closure = original_up_k
        engine.execute_node = original_execute
        engine.CAP = original_cap

    stop = manifest["execution"]["stop"]
    if stop is None or stop["status"] != "OPEN_AT_NODE_B2_CAPABILITY":
        raise AssertionError("negative engine probe did not reach the expected honest OPEN")
    if stop["no_layout_at_cap"] is not False or stop["terminal"] != TERMINAL:
        raise AssertionError("negative probe promoted an incomplete run")
    prefix = prefix_receipt(output_dir, manifest)
    artifact = {
        "schema": SCHEMA,
        "fixture": FIXTURE,
        "bounded_exhaustive_oracle": oracle,
        "engine_manifest_digest": manifest["manifest_digest"],
        "engine_execution": manifest["execution"],
        "scaffold_width_vector": [
            int(item["width"]) for item in manifest["scaffold_case"]["candidate_edges"]
        ],
        "prefix_receipt": prefix,
        "result": "OPEN_B2_SEMANTIC_UP_K_CAPABILITY",
        "attack_findings": {
            "no_trajectory_loss_before_b2": prefix["pair_path_equality"]
            and prefix["refinement_partition_equality"]
            and prefix["provenance_partition_equality"],
            "no_unsound_dominance_claim": True,
            "no_missing_root_entries_claim": "NOT_REACHED",
            "dimension_two_full_up_k_required": True,
        },
        "strict_boundary": {
            "negative_fixture_has_no_width_k_layout": True,
            "negative_root_reached": False,
            "terminal_completeness_proved": False,
            "found_layout_enabled": False,
            "no_layout_at_cap_enabled": False,
            "current_global_terminal": TERMINAL,
            "p_vs_np": "OPEN",
        },
        "next_gate": "C049.1_B4.6.3_DIMENSION_TWO_UP_K_CAPABILITY_HARDENING",
    }
    artifact["semantic_digest"] = digest(artifact)
    (output_dir / "negative-root-artifact.json").write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n"
    )
    print("JANUS_C049_1_B4_6_3_NEGATIVE_ROOT_ENGINE_REPLAY = HONEST_OPEN")
    print("PERMUTATIONS_REPLAYED =", oracle["permutation_count"])
    print("MINIMUM_WIDTH =", oracle["minimum_width"])
    print("STOP_NODE =", stop["node_id"])
    print("B2_TERMINAL =", stop["b2_terminal"])
    print("B2_COUNTER =", stop["counter"])
    print("B2_ATTEMPTED =", stop["required"])
    print("B2_CAP =", stop["cap"])
    print("GLOBAL_TERMINAL =", TERMINAL)
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    build(args.output_dir)


if __name__ == "__main__":
    main()
