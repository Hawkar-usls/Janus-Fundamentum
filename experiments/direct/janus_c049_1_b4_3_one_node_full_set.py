#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from typing import Any, Sequence

from janus_c049_1_b1_compact_trajectory_core import encode as b2_encode
from janus_c049_1_b2_up_k_core import (
    Ledger,
    decode_trajectory as b2_decode_trajectory,
    up_k_closure,
)
from janus_c049_1_b3_expand_join_shrink_core import (
    decode_trajectory as b3_decode_trajectory,
    encode_trajectory as b3_encode_trajectory,
    expand_trajectory,
    join_trajectory,
    lattice_paths,
    shrink_trajectory,
    width,
    xor_basis,
)
from janus_c049_1_b4_2_3k_scaffold import boundary, cases as scaffold_cases


SCHEMA = "C049.1-B4.3-ONE-NODE-FULL-SET-v1"
TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"
K = 1
CAP = 10**9


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def trajectory_key(raw: Sequence[dict]) -> str:
    return canonical_json(raw).decode()


def ledger_total(ledger: dict) -> int:
    return int(ledger["discovery_work"]) + int(ledger["work"])


def selected_scaffold_case() -> dict:
    matches = [
        case
        for case in scaffold_cases()
        if int(case["d"]) == 3
        and int(case["k"]) == 1
        and case["whole_factor_blocks"] == [[1], [2], [4]]
        and case["scaffold_order"] == [1, 0, 2]
    ]
    if len(matches) != 1:
        raise AssertionError("B4.2 internal-node fixture not unique")
    return matches[0]


def child_full_set(factor_id: int) -> dict:
    generator_raw = [{"left": [], "right": [], "value": 0}]
    generator = b2_decode_trajectory(generator_raw, 0)
    ledger = Ledger(CAP, CAP)
    closure = up_k_closure([generator], 0, K, ledger)
    if closure["entry_count"] != 6:
        raise AssertionError("unexpected zero-boundary leaf full set")
    return {
        "factor_id": factor_id,
        "boundary_rref": [],
        "leaf_generator": b2_encode(generator),
        "full_set": closure,
        "provenance": {
            "kind": "WHOLE_FACTOR_LEAF",
            "factor_id": factor_id,
            "generator_source": "canonical zero-boundary one-factor trajectory",
        },
    }


def compaction_removed(trace: Sequence[dict]) -> int:
    return sum(len(step["removed"]) for step in trace)


def refinement_work(join_receipt: dict, shrink_receipt: dict) -> dict[str, int]:
    join_trace = join_receipt["compactification_trace"]
    shrink_trace = shrink_receipt["compactification_trace"]
    return {
        "lattice_path_trials": 1,
        "join_stat_constructions": int(join_receipt["raw_length"]),
        "join_intersection_corrections": len(join_receipt["stat_receipts"]),
        "join_compaction_steps": len(join_trace),
        "join_compaction_removed_statistics": compaction_removed(join_trace),
        "shrink_projection_statistics": len(shrink_receipt["projection_receipts"]),
        "shrink_compaction_steps": len(shrink_trace),
        "shrink_compaction_removed_statistics": compaction_removed(shrink_trace),
        "width_tests": 1,
    }


def build() -> dict:
    scaffold = selected_scaffold_case()
    ambient = int(scaffold["d"])
    blocks = [tuple(block) for block in scaffold["whole_factor_blocks"]]
    child_ids = (1, 0)
    outside_ids = (2,)

    child_boundaries = {
        child: boundary(
            [blocks[child]],
            [blocks[index] for index in range(len(blocks)) if index != child],
            ambient,
        )
        for child in child_ids
    }
    common_boundary = xor_basis(
        (*child_boundaries[child_ids[0]], *child_boundaries[child_ids[1]]),
        ambient,
    )
    parent_boundary = boundary(
        [blocks[index] for index in child_ids],
        [blocks[index] for index in outside_ids],
        ambient,
    )
    if child_boundaries != {1: (), 0: ()} or common_boundary or parent_boundary:
        raise AssertionError("selected node lost its bounded zero-boundary fixture")

    leaves = [child_full_set(child) for child in child_ids]
    work_events: list[dict] = []
    cumulative_work = 0

    def charge(kind: str, reference: str, breakdown: dict[str, int]) -> None:
        nonlocal cumulative_work
        if any(int(value) < 0 for value in breakdown.values()):
            raise ValueError("negative work charge")
        delta = sum(int(value) for value in breakdown.values())
        cumulative_work += delta
        work_events.append(
            {
                "event_index": len(work_events),
                "kind": kind,
                "reference": reference,
                "breakdown": dict(sorted(breakdown.items())),
                "work_delta": delta,
                "cumulative_work": cumulative_work,
            }
        )

    for leaf in leaves:
        ledger = leaf["full_set"]["ledger"]
        charge(
            "CHILD_FULL_SET",
            f"factor:{leaf['factor_id']}",
            {
                "b2_discovery_work": int(ledger["discovery_work"]),
                "b2_work": int(ledger["work"]),
            },
        )

    pairs: list[dict] = []
    attempts: list[dict] = []
    successful_by_trajectory: dict[str, list[int]] = defaultdict(list)

    left_entries = leaves[0]["full_set"]["entries"]
    right_entries = leaves[1]["full_set"]["entries"]
    for left_index, left_entry in enumerate(left_entries):
        left = b3_decode_trajectory(
            left_entry["trajectory"], child_boundaries[child_ids[0]], ambient
        )
        for right_index, right_entry in enumerate(right_entries):
            right = b3_decode_trajectory(
                right_entry["trajectory"], child_boundaries[child_ids[1]], ambient
            )
            expanded_left, left_transport = expand_trajectory(
                left, child_boundaries[child_ids[0]], common_boundary, ambient
            )
            expanded_right, right_transport = expand_trajectory(
                right, child_boundaries[child_ids[1]], common_boundary, ambient
            )
            pair_id = len(pairs)
            pair_attempt_ids: list[int] = []
            expand_breakdown = {
                "pair_enumerations": 1,
                "expanded_statistics": len(expanded_left) + len(expanded_right),
                "boundary_coordinate_changes": len(
                    left_transport["child_basis_in_parent_coordinates"]
                )
                + len(right_transport["child_basis_in_parent_coordinates"]),
            }
            charge("PAIR_EXPAND", f"pair:{pair_id}", expand_breakdown)

            for path in lattice_paths(len(expanded_left), len(expanded_right)):
                joined, join_receipt = join_trajectory(
                    expanded_left, expanded_right, path, common_boundary, ambient
                )
                shrunk, shrink_receipt = shrink_trajectory(
                    joined, parent_boundary, ambient
                )
                output_raw = b3_encode_trajectory(shrunk)
                output_width = width(shrunk)
                accepted = output_width <= K
                attempt_id = len(attempts)
                breakdown = refinement_work(join_receipt, shrink_receipt)
                charge("REFINEMENT", f"attempt:{attempt_id}", breakdown)
                payload = {
                    "attempt_id": attempt_id,
                    "pair_id": pair_id,
                    "left_entry_index": left_index,
                    "right_entry_index": right_index,
                    "lattice_path": [list(cell) for cell in path],
                    "join": join_receipt,
                    "shrink": shrink_receipt,
                    "output": output_raw,
                    "output_width": output_width,
                    "status": "SUCCESS" if accepted else "FAILED_WIDTH_CAP",
                    "failure_reason": None
                    if accepted
                    else f"output width {output_width} exceeds k={K}",
                    "work_breakdown": dict(sorted(breakdown.items())),
                    "cumulative_work": cumulative_work,
                }
                payload["transcript_digest"] = digest(payload)
                attempts.append(payload)
                pair_attempt_ids.append(attempt_id)
                if accepted:
                    successful_by_trajectory[trajectory_key(output_raw)].append(
                        attempt_id
                    )

            pairs.append(
                {
                    "pair_id": pair_id,
                    "left_entry_index": left_index,
                    "right_entry_index": right_index,
                    "left_input": b3_encode_trajectory(left),
                    "right_input": b3_encode_trajectory(right),
                    "left_expand": {
                        "output": b3_encode_trajectory(expanded_left),
                        "transport": left_transport,
                    },
                    "right_expand": {
                        "output": b3_encode_trajectory(expanded_right),
                        "transport": right_transport,
                    },
                    "lattice_path_count": len(pair_attempt_ids),
                    "attempt_ids": pair_attempt_ids,
                    "expand_work_breakdown": dict(sorted(expand_breakdown.items())),
                }
            )

    unique_generators: list[dict] = []
    duplicate_deletions: list[dict] = []
    for raw_key in sorted(successful_by_trajectory):
        raw = json.loads(raw_key)
        provenance_ids = successful_by_trajectory[raw_key]
        retained_attempt = provenance_ids[0]
        unique_generators.append(
            {
                "trajectory": raw,
                "provenance_attempt_ids": provenance_ids,
                "canonical_retained_attempt_id": retained_attempt,
            }
        )
        identity_path = [
            [index, index] for index in range(len(raw))
        ]
        for removed_attempt in provenance_ids[1:]:
            duplicate_deletions.append(
                {
                    "removed_attempt_id": removed_attempt,
                    "retained_attempt_id": retained_attempt,
                    "trajectory": raw,
                    "witness": {
                        "path": identity_path,
                        "path_length": len(identity_path),
                    },
                    "reason": "IDENTICAL_REFINEMENT_OUTPUT",
                }
            )

    b2_generators = [
        b2_decode_trajectory(item["trajectory"], 0)
        for item in unique_generators
    ]
    b2_ledger = Ledger(CAP, CAP)
    node_closure = up_k_closure(b2_generators, 0, K, b2_ledger)
    charge(
        "NODE_B2_UP_K",
        "node:3",
        {
            "b2_discovery_work": int(node_closure["ledger"]["discovery_work"]),
            "b2_work": int(node_closure["ledger"]["work"]),
        },
    )

    provenance_by_key = {
        trajectory_key(item["trajectory"]): item["provenance_attempt_ids"]
        for item in unique_generators
    }
    input_generator_provenance = [
        {
            "trajectory": raw,
            "provenance_attempt_ids": provenance_by_key[trajectory_key(raw)],
        }
        for raw in node_closure["input_generators"]
    ]
    retained_generator_provenance = [
        {
            "retained_generator_index": index,
            "trajectory": raw,
            "provenance_attempt_ids": provenance_by_key[trajectory_key(raw)],
        }
        for index, raw in enumerate(node_closure["retained_generators"])
    ]
    entry_provenance = [
        {
            "entry_index": index,
            "source_generator_index": int(entry["source_generator_index"]),
            "source_provenance_attempt_ids": retained_generator_provenance[
                int(entry["source_generator_index"])
            ]["provenance_attempt_ids"],
        }
        for index, entry in enumerate(node_closure["entries"])
    ]

    successful = sum(item["status"] == "SUCCESS" for item in attempts)
    failed = len(attempts) - successful
    artifact = {
        "schema": SCHEMA,
        "phase": "B4.3_FIRST_INTERNAL_NODE_FULL_SET",
        "source_head": "5646f8a0c323c2061ff4d6e9bfd94cb42edc238d",
        "scaffold_case": scaffold,
        "node": {
            "node_id": 3,
            "kind": "SPINE_INTERNAL_JOIN",
            "covered_factor_ids": list(child_ids),
            "outside_factor_ids": list(outside_ids),
            "whole_factor_blocks": [list(block) for block in blocks],
            "affine_offsets": list(scaffold["affine_offsets"]),
            "covered_affine_offsets": [
                scaffold["affine_offsets"][index] for index in child_ids
            ],
            "grouped_partition_preserved": True,
            "child_boundaries": {
                str(key): list(value) for key, value in child_boundaries.items()
            },
            "common_join_boundary": list(common_boundary),
            "parent_boundary": list(parent_boundary),
            "width_cap": K,
        },
        "child_full_sets": leaves,
        "pairs": pairs,
        "refinement_attempts": attempts,
        "successful_output_generators": unique_generators,
        "duplicate_deletions": duplicate_deletions,
        "node_up_k": node_closure,
        "input_generator_provenance": input_generator_provenance,
        "retained_generator_provenance": retained_generator_provenance,
        "entry_provenance": entry_provenance,
        "work_events": work_events,
        "audit": {
            "child_full_set_entries": [
                leaf["full_set"]["entry_count"] for leaf in leaves
            ],
            "child_pairs_processed": len(pairs),
            "lattice_paths_processed": len(attempts),
            "successful_refinements": successful,
            "failed_refinements": failed,
            "raw_precompact_join_statistics": sum(
                item["join"]["raw_length"] for item in attempts
            ),
            "unique_successful_generators": len(unique_generators),
            "duplicate_successful_outputs_deleted": len(duplicate_deletions),
            "b2_dominance_deletions": len(node_closure["removals"]),
            "retained_generators": len(node_closure["retained_generators"]),
            "final_up_k_entries": int(node_closure["entry_count"]),
            "cumulative_work": cumulative_work,
            "failures": 0,
        },
        "strict_boundary": {
            "scope": "one internal scaffold node only",
            "full_iterative_compression_cycle": False,
            "complete_branch_refinement": False,
            "no_layout_at_cap_enabled": False,
            "empty_full_set_terminal": TERMINAL,
            "current_global_terminal": TERMINAL,
            "p_vs_np": "OPEN",
        },
    }
    artifact["artifact_digest"] = digest(artifact)
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    args = parser.parse_args()
    artifact = build()
    raw = canonical_json(artifact) + b"\n"
    if args.output:
        with open(args.output, "wb") as handle:
            handle.write(raw)
    audit = artifact["audit"]
    print("JANUS_C049_1_B4_3_ONE_NODE_FULL_SET = PASS")
    print("CHILD_PAIRS =", audit["child_pairs_processed"])
    print("LATTICE_PATHS =", audit["lattice_paths_processed"])
    print("SUCCESSFUL_REFINEMENTS =", audit["successful_refinements"])
    print("FAILED_REFINEMENTS =", audit["failed_refinements"])
    print("CUMULATIVE_WORK =", audit["cumulative_work"])
    print("FINAL_UP_K_ENTRIES =", audit["final_up_k_entries"])
    print("BYTES =", len(raw), "DIGEST =", artifact["artifact_digest"])
    print("TERMINAL =", TERMINAL)


if __name__ == "__main__":
    main()
