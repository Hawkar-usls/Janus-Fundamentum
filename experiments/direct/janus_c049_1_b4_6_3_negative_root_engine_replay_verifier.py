#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import itertools
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Sequence

SCHEMA = "C049.1-B4.6.3-NEGATIVE-ROOT-ENGINE-REPLAY-v1"
TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def rref(rows: Iterable[int], d: int) -> tuple[int, ...]:
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
    left_basis = rref(left, d)
    right_basis = rref(right, d)
    joined = rref((*left_basis, *right_basis), d)
    return len(left_basis) + len(right_basis) - len(joined)


def layout_width(blocks: Sequence[Sequence[int]], order: Sequence[int], d: int) -> tuple[int, list[int]]:
    vector = []
    for cut in range(1, len(order)):
        left = [row for factor in order[:cut] for row in blocks[factor]]
        right = [row for factor in order[cut:] for row in blocks[factor]]
        vector.append(intersection_dimension(left, right, d))
    return max(vector, default=0), vector


def read_records(root: Path, manifest: dict, kind: str):
    previous_digest = None
    expected_id = 0
    for index, metadata in enumerate(manifest["chunking"]["chunk_groups"][kind]):
        raw_compressed = (root / metadata["filename"]).read_bytes()
        if hashlib.sha256(raw_compressed).hexdigest() != metadata["compressed_sha256"]:
            raise AssertionError("compressed chunk digest mismatch")
        payload = json.loads(gzip.decompress(raw_compressed))
        unsigned = {key: value for key, value in payload.items() if key != "chunk_payload_digest"}
        if digest(unsigned) != payload["chunk_payload_digest"]:
            raise AssertionError("chunk payload digest mismatch")
        if payload["kind"] != kind or payload["chunk_index"] != index:
            raise AssertionError("chunk ordering mismatch")
        if payload["previous_chunk_digest"] != previous_digest:
            raise AssertionError("chunk chain mismatch")
        if payload["record_count"] != len(payload["records"]):
            raise AssertionError("chunk record count mismatch")
        field = payload["record_id_field"]
        for record in payload["records"]:
            if int(record[field]) != expected_id:
                raise AssertionError("global record id gap")
            unsigned_record = {key: value for key, value in record.items() if key != "record_digest"}
            if digest(unsigned_record) != record["record_digest"]:
                raise AssertionError("record digest mismatch")
            expected_id += 1
            yield record
        previous_digest = metadata["compressed_sha256"]


def recompute_oracle(fixture: dict) -> dict:
    blocks = fixture["blocks"]
    d = int(fixture["d"])
    k = int(fixture["k"])
    records = []
    for order in itertools.permutations(range(len(blocks))):
        maximum, vector = layout_width(blocks, order, d)
        records.append({"order": list(order), "maximum_width": maximum, "width_vector": vector})
    previous_maximum, previous_vector = layout_width(
        blocks[:-1], fixture["previous_order"], d
    )
    accepting = [item for item in records if item["maximum_width"] <= k]
    return {
        "permutation_count": len(records),
        "minimum_width": min(item["maximum_width"] for item in records),
        "accepting_layout_count": len(accepting),
        "previous_width": previous_maximum,
        "previous_width_vector": previous_vector,
        "all_layouts_digest": digest(records),
    }


def replay_prefix(root: Path, manifest: dict) -> dict:
    stop_node = int(manifest["execution"]["stop"]["node_id"])
    counts = defaultdict(int)
    paths = 0
    successful_ids = set()
    generator_provenance = []
    expected_duplicate_pairs = set()
    actual_duplicate_pairs = set()

    pairs = list(read_records(root, manifest, "PAIRS"))
    refinements = list(read_records(root, manifest, "REFINEMENTS"))
    generators = list(read_records(root, manifest, "GENERATORS"))
    deletions = list(read_records(root, manifest, "DELETIONS"))

    for pair in pairs:
        if int(pair["node_id"]) != stop_node:
            continue
        counts["pairs"] += 1
        paths += int(pair["lattice_path_count"])
    for refinement in refinements:
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
    for generator in generators:
        if int(generator["node_id"]) != stop_node:
            continue
        counts["generators"] += 1
        ids = [int(value) for value in generator["provenance_attempt_ids"]]
        if not ids or int(generator["canonical_retained_attempt_id"]) != ids[0]:
            raise AssertionError("generator canonical provenance mismatch")
        if generator["trajectory_digest"] != digest(generator["trajectory_parent_coordinates"]):
            raise AssertionError("generator trajectory digest mismatch")
        generator_provenance.extend(ids)
        for removed in ids[1:]:
            expected_duplicate_pairs.add((int(generator["generator_id"]), removed))
    for deletion in deletions:
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
        "successful_attempt_ids_match_provenance": set(generator_provenance) == successful_ids,
        "duplicate_deletion_records": counts["deletions"],
        "duplicate_pairs_digest": digest(sorted([list(item) for item in actual_duplicate_pairs])),
        "pair_path_equality": paths == counts["refinements"],
        "refinement_partition_equality": counts["refinements"]
        == counts["successful"] + counts["failed"],
        "provenance_partition_equality": len(generator_provenance)
        == len(set(generator_provenance))
        == counts["successful"]
        and set(generator_provenance) == successful_ids,
    }


def verify(root: Path, artifact: dict) -> None:
    if artifact.get("schema") != SCHEMA:
        raise AssertionError("wrong artifact schema")
    claimed = artifact.get("semantic_digest")
    body = {key: value for key, value in artifact.items() if key != "semantic_digest"}
    if claimed != digest(body):
        raise AssertionError("outer semantic digest mismatch")

    manifest = json.loads((root / "manifest.json").read_text())
    manifest_claimed = manifest.get("manifest_digest")
    manifest_body = {key: value for key, value in manifest.items() if key != "manifest_digest"}
    if manifest_claimed != digest(manifest_body):
        raise AssertionError("engine manifest digest mismatch")
    if artifact["engine_manifest_digest"] != manifest_claimed:
        raise AssertionError("outer/engine manifest binding mismatch")

    fixture = artifact["fixture"]
    oracle = recompute_oracle(fixture)
    if artifact["bounded_exhaustive_oracle"] != oracle:
        raise AssertionError("bounded exhaustive oracle mismatch")
    if oracle["permutation_count"] != 720 or oracle["accepting_layout_count"] != 0:
        raise AssertionError("negative permutation space mismatch")
    if oracle["minimum_width"] != 2 or oracle["previous_width"] != 1:
        raise AssertionError("negative fixture width mismatch")

    scaffold_case = manifest["scaffold_case"]
    if scaffold_case["whole_factor_blocks"] != fixture["blocks"]:
        raise AssertionError("engine fixture block mismatch")
    if scaffold_case["previous_order"] != fixture["previous_order"]:
        raise AssertionError("engine previous order mismatch")
    profile = [int(item["width"]) for item in scaffold_case["candidate_edges"]]
    if profile != fixture["expected_scaffold_width_vector"]:
        raise AssertionError("scaffold width profile mismatch")
    if artifact["scaffold_width_vector"] != profile:
        raise AssertionError("outer scaffold profile mismatch")

    execution = manifest["execution"]
    stop = execution["stop"]
    if execution["status"] != "OPEN_AT_NODE_B2_CAPABILITY":
        raise AssertionError("negative engine did not preserve OPEN")
    if stop["reason"] != "B2_SEMANTIC_UP_K_CAPABILITY_EXCEEDED":
        raise AssertionError("unexpected negative engine stop reason")
    if stop["b2_terminal"] not in ("OPEN_DISCOVERY_BUDGET", "OPEN_WORK_BUDGET"):
        raise AssertionError("invalid B2 capability terminal")
    if int(stop["required"]) != int(stop["cap"]) + 1:
        raise AssertionError("B2 capability edge mismatch")
    if int(stop["boundary_coordinate_dimension"]) != 2 or int(stop["k"]) != 1:
        raise AssertionError("negative engine did not reach the dimension-two up_k gate")
    if stop["terminal"] != TERMINAL or stop["no_layout_at_cap"] is not False:
        raise AssertionError("incomplete negative run promoted to NO")
    if execution["root_full_set_receipt"] is not None:
        raise AssertionError("root receipt exists despite incomplete negative run")

    prefix = replay_prefix(root, manifest)
    if artifact["prefix_receipt"] != prefix:
        raise AssertionError("negative prefix receipt mismatch")
    if not prefix["pair_path_equality"]:
        raise AssertionError("trajectory path inventory incomplete before B2")
    if not prefix["refinement_partition_equality"]:
        raise AssertionError("refinement partition incomplete before B2")
    if not prefix["provenance_partition_equality"]:
        raise AssertionError("successful trajectory provenance incomplete before B2")

    if artifact["result"] != "OPEN_B2_SEMANTIC_UP_K_CAPABILITY":
        raise AssertionError("negative probe result drift")
    findings = artifact["attack_findings"]
    if findings["no_trajectory_loss_before_b2"] is not True:
        raise AssertionError("trajectory-loss finding drift")
    if findings["no_unsound_dominance_claim"] is not True:
        raise AssertionError("unsound dominance conclusion")
    if findings["no_missing_root_entries_claim"] != "NOT_REACHED":
        raise AssertionError("missing-root claim issued before root")
    if findings["dimension_two_full_up_k_required"] is not True:
        raise AssertionError("dimension-two gate not registered")

    strict = artifact["strict_boundary"]
    if strict["negative_root_reached"] is not False:
        raise AssertionError("negative root falsely claimed")
    if strict["terminal_completeness_proved"] is not False:
        raise AssertionError("terminal completeness falsely claimed")
    if strict["found_layout_enabled"] is not False or strict["no_layout_at_cap_enabled"] is not False:
        raise AssertionError("global terminal enabled prematurely")
    if strict["current_global_terminal"] != TERMINAL or strict["p_vs_np"] != "OPEN":
        raise AssertionError("strict global boundary drift")


def repair(artifact: dict) -> None:
    artifact.pop("semantic_digest", None)
    artifact["semantic_digest"] = digest(artifact)


def tamper_self_test(root: Path, artifact: dict) -> None:
    controls = []

    promoted = copy.deepcopy(artifact)
    promoted["result"] = "NO_LAYOUT_AT_CAP"
    promoted["strict_boundary"]["no_layout_at_cap_enabled"] = True
    controls.append(promoted)

    altered_oracle = copy.deepcopy(artifact)
    altered_oracle["bounded_exhaustive_oracle"]["minimum_width"] = 1
    controls.append(altered_oracle)

    missing_refinement = copy.deepcopy(artifact)
    missing_refinement["prefix_receipt"]["refinement_records"] -= 1
    controls.append(missing_refinement)

    false_root = copy.deepcopy(artifact)
    false_root["strict_boundary"]["negative_root_reached"] = True
    false_root["attack_findings"]["no_missing_root_entries_claim"] = True
    controls.append(false_root)

    for control in controls:
        repair(control)
        try:
            verify(root, control)
        except Exception:
            continue
        raise AssertionError("digest-repaired negative-root tamper accepted")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--tamper-self-test", action="store_true")
    args = parser.parse_args()
    artifact = json.loads((args.output_dir / "negative-root-artifact.json").read_text())
    verify(args.output_dir, artifact)
    if args.tamper_self_test:
        tamper_self_test(args.output_dir, artifact)
    print("VERIFIED C049.1 B4.6.3 NEGATIVE ROOT ENGINE HONEST OPEN")
    print("NEGATIVE_ROOT_REACHED = FALSE")
    print("NEXT_GATE = C049.1_B4.6.3_DIMENSION_TWO_UP_K_CAPABILITY_HARDENING")
    print("GLOBAL_TERMINAL =", TERMINAL)


if __name__ == "__main__":
    main()
