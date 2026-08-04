#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import janus_c049_1_b4_6_3_negative_root_engine_replay_verifier as base


def streaming_replay_prefix(root: Path, manifest: dict) -> dict:
    stop_node = int(manifest["execution"]["stop"]["node_id"])
    counts = defaultdict(int)
    paths = 0
    successful_ids = set()
    generator_provenance = []
    expected_duplicate_pairs = set()
    actual_duplicate_pairs = set()

    for pair in base.read_records(root, manifest, "PAIRS"):
        if int(pair["node_id"]) != stop_node:
            continue
        counts["pairs"] += 1
        paths += int(pair["lattice_path_count"])

    for refinement in base.read_records(root, manifest, "REFINEMENTS"):
        if int(refinement["node_id"]) != stop_node:
            continue
        counts["refinements"] += 1
        if refinement["status"] == "SUCCESS":
            counts["successful"] += 1
            successful_ids.add(int(refinement["attempt_id"]))
        elif refinement["status"] == "FAILED_WIDTH_CAP":
            counts["failed"] += 1
        else:
            raise AssertionError("unknown refinement terminal")

    for generator in base.read_records(root, manifest, "GENERATORS"):
        if int(generator["node_id"]) != stop_node:
            continue
        counts["generators"] += 1
        ids = [int(value) for value in generator["provenance_attempt_ids"]]
        if not ids or int(generator["canonical_retained_attempt_id"]) != ids[0]:
            raise AssertionError("generator canonical provenance mismatch")
        if generator["trajectory_digest"] != base.digest(
            generator["trajectory_parent_coordinates"]
        ):
            raise AssertionError("generator trajectory digest mismatch")
        generator_provenance.extend(ids)
        for removed in ids[1:]:
            expected_duplicate_pairs.add((int(generator["generator_id"]), removed))

    for deletion in base.read_records(root, manifest, "DELETIONS"):
        if int(deletion["node_id"]) != stop_node:
            continue
        counts["deletions"] += 1
        if deletion["reason"] != "IDENTICAL_REFINEMENT_OUTPUT":
            raise AssertionError("dominance deletion serialized before incomplete B2 closure")
        actual_duplicate_pairs.add(
            (int(deletion["generator_id"]), int(deletion["removed_attempt_id"]))
        )

    if expected_duplicate_pairs != actual_duplicate_pairs:
        raise AssertionError("duplicate deletion partition mismatch")

    return {
        "node_id": stop_node,
        "pair_records": counts["pairs"],
        "delannoy_paths_from_pairs": paths,
        "refinement_records": counts["refinements"],
        "successful_refinements": counts["successful"],
        "failed_refinements": counts["failed"],
        "generator_records": counts["generators"],
        "provenance_occurrences": len(generator_provenance),
        "distinct_provenance_attempts": len(set(generator_provenance)),
        "successful_attempt_ids_match_provenance": set(generator_provenance)
        == successful_ids,
        "duplicate_deletion_records": counts["deletions"],
        "duplicate_pairs_digest": base.digest(
            sorted([list(item) for item in actual_duplicate_pairs])
        ),
        "pair_path_equality": paths == counts["refinements"],
        "refinement_partition_equality": counts["refinements"]
        == counts["successful"] + counts["failed"],
        "provenance_partition_equality": len(generator_provenance)
        == len(set(generator_provenance))
        == counts["successful"]
        and set(generator_provenance) == successful_ids,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--tamper-self-test", action="store_true")
    args = parser.parse_args()

    base.replay_prefix = streaming_replay_prefix
    artifact = json.loads(
        (args.output_dir / "negative-root-artifact.json").read_text()
    )
    base.verify(args.output_dir, artifact)
    if args.tamper_self_test:
        base.tamper_self_test(args.output_dir, artifact)
    print("VERIFIED C049.1 B4.6.3 NEGATIVE ROOT ENGINE HONEST OPEN")
    print("STREAMING_REPLAY = TRUE")
    print("NEGATIVE_ROOT_REACHED = FALSE")
    print("NEXT_GATE = C049.1_B4.6.3_DIMENSION_TWO_UP_K_CAPABILITY_HARDENING")
    print("GLOBAL_TERMINAL =", base.TERMINAL)


if __name__ == "__main__":
    main()
