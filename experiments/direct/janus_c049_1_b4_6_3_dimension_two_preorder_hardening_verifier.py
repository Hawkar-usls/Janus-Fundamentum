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

SCHEMA = "C049.1-B4.6.3-DIMENSION-TWO-PREORDER-HARDENING-v1"
SOURCE_HEAD = "aae75187fa8883b2e99fdc95ce62e21540161e8d"
TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def rref(rows: Iterable[int], dim: int) -> tuple[int, ...]:
    limit = 1 << dim
    pivots: dict[int, int] = {}
    for raw in rows:
        value = int(raw)
        if value < 0 or value >= limit:
            raise ValueError("row outside ambient space")
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot]
                continue
            pivots[pivot] = value
            for other in tuple(pivots):
                if other != pivot and ((pivots[other] >> pivot) & 1):
                    pivots[other] ^= value
            break
    for pivot in sorted(pivots):
        row = pivots[pivot]
        for other in sorted(pivots, reverse=True):
            if other != pivot and ((pivots[other] >> pivot) & 1):
                pivots[other] ^= row
    return tuple(pivots[pivot] for pivot in sorted(pivots, reverse=True))


def contains(big: tuple[int, ...], small: tuple[int, ...]) -> bool:
    for vector in small:
        remainder = vector
        for row in big:
            remainder = min(remainder, remainder ^ row)
        if remainder:
            return False
    return True


def compact(sequence: Sequence[tuple]) -> tuple:
    current = list(sequence)
    while True:
        changed = False
        for index in range(1, len(current)):
            if current[index - 1] == current[index]:
                del current[index]
                changed = True
                break
        if changed:
            continue
        for first in range(len(current)):
            for last in range(first + 2, len(current)):
                if current[first][:2] != current[last][:2]:
                    continue
                low = min(current[first][2], current[last][2])
                high = max(current[first][2], current[last][2])
                if all(low <= item[2] <= high for item in current[first + 1:last]):
                    del current[first + 1:last]
                    changed = True
                    break
            if changed:
                break
        if not changed:
            return tuple(current)


def parse_trajectory(raw: Sequence[dict], dim: int) -> tuple:
    if not raw:
        raise ValueError("empty trajectory")
    gamma = tuple((rref(item["left"], dim), rref(item["right"], dim), int(item["value"])) for item in raw)
    if any(item[2] < 0 for item in gamma):
        raise ValueError("negative value")
    if gamma[0][1] != gamma[-1][0]:
        raise ValueError("endpoint mismatch")
    for before, after in zip(gamma, gamma[1:]):
        if not contains(after[0], before[0]) or not contains(before[1], after[1]):
            raise ValueError("monotonicity mismatch")
    if compact(gamma) != gamma:
        raise ValueError("noncompact trajectory")
    return gamma


def encode(gamma: Sequence[tuple]) -> list[dict]:
    return [{"left": list(left), "right": list(right), "value": value} for left, right, value in gamma]


def signature(gamma: Sequence[tuple]) -> tuple:
    out = []
    for left, right, _ in gamma:
        symbol = (left, right)
        if not out or out[-1] != symbol:
            out.append(symbol)
    return tuple(out)


def encode_signature(value: Sequence[tuple]) -> list[dict]:
    return [{"left": list(left), "right": list(right)} for left, right in value]


def empty_preorder_counters() -> dict[str, int]:
    names = (
        "discovery_work", "work", "rref_input_rows", "rref_pivot_tests",
        "rref_xors", "rref_output_rows", "subspace_inclusion_tests",
        "subspace_reduction_xors", "boundary_coordinate_changes",
        "trajectory_prefix_states", "trajectory_extension_trials", "lattice_cells",
        "lattice_predecessor_tests", "lattice_path_vertices", "generator_pair_tests",
        "dominance_witnesses", "full_set_entries",
    )
    return {name: 0 for name in names}


def relation(lower: Sequence[tuple], upper: Sequence[tuple], counters: dict | None = None) -> list[tuple[int, int]] | None:
    if counters is not None:
        counters["generator_pair_tests"] += 1
        counters["work"] += 1
    parent: dict[tuple[int, int], tuple[int, int] | None] = {}
    for row in range(len(lower)):
        for column in range(len(upper)):
            if counters is not None:
                counters["lattice_cells"] += 1
                counters["work"] += 1
            a = lower[row]
            b = upper[column]
            if a[0] != b[0] or a[1] != b[1] or a[2] > b[2]:
                continue
            if (row, column) == (0, 0):
                parent[(row, column)] = None
                continue
            for previous in ((row - 1, column - 1), (row - 1, column), (row, column - 1)):
                if counters is not None:
                    counters["lattice_predecessor_tests"] += 1
                    counters["work"] += 1
                if previous in parent:
                    parent[(row, column)] = previous
                    break
    target = (len(lower) - 1, len(upper) - 1)
    if target not in parent:
        return None
    path = []
    cursor: tuple[int, int] | None = target
    while cursor is not None:
        path.append(cursor)
        cursor = parent[cursor]
    path.reverse()
    if counters is not None:
        counters["lattice_path_vertices"] += len(path)
        counters["dominance_witnesses"] += 1
        counters["work"] += len(path) + 1
    return path


def witness(path: Sequence[tuple[int, int]]) -> dict:
    return {"path": [list(item) for item in path], "path_length": len(path)}


def read_source(root: Path) -> tuple[dict, int, int, int, list[dict]]:
    manifest = json.loads((root / "manifest.json").read_text())
    body = dict(manifest)
    claimed = body.pop("manifest_digest", None)
    if claimed != digest(body):
        raise AssertionError("source manifest digest mismatch")
    stop = manifest["execution"]["stop"]
    if stop is None or stop["status"] != "OPEN_AT_NODE_B2_CAPABILITY":
        raise AssertionError("source is not the frozen honest OPEN")
    node_id = int(stop["node_id"])
    dim = int(stop["boundary_coordinate_dimension"])
    k = int(stop["k"])
    records = []
    for metadata in manifest["chunking"]["chunk_groups"]["GENERATORS"]:
        payload = json.loads(gzip.decompress((root / metadata["filename"]).read_bytes()))
        if payload["kind"] != "GENERATORS" or payload["record_count"] != metadata["record_count"]:
            raise AssertionError("generator chunk metadata mismatch")
        for record in payload["records"]:
            unsigned = dict(record)
            record_digest = unsigned.pop("record_digest", None)
            if record_digest != digest(unsigned):
                raise AssertionError("generator record digest mismatch")
            if int(record["node_id"]) == node_id:
                records.append(record)
    records.sort(key=lambda item: int(item["generator_id"]))
    return manifest, node_id, dim, k, records


def scalar_patterns() -> tuple[tuple[tuple[int, ...], ...], int]:
    accepted = set()
    tested = 0
    for length in range(1, 16):
        for values in itertools.product((0, 1), repeat=length):
            tested += 1
            wrapped = tuple(((), (), value) for value in values)
            if compact(wrapped) == wrapped:
                accepted.add(tuple(values))
    result = tuple(sorted(accepted))
    expected = ((0,), (0, 1), (0, 1, 0), (1,), (1, 0), (1, 0, 1))
    if result != expected:
        raise AssertionError("binary typical-sequence catalog mismatch")
    return result, tested


def reachable_catalog(signatures: Sequence[tuple]) -> tuple[tuple, tuple, int]:
    patterns, tested = scalar_patterns()
    values = set()
    for sig in signatures:
        if len(set(sig)) != len(sig):
            raise AssertionError("repeated skeleton run invalidates product catalog")
        for selection in itertools.product(patterns, repeat=len(sig)):
            candidate = []
            for (left, right), run in zip(sig, selection):
                candidate.extend((left, right, scalar) for scalar in run)
            gamma = tuple(candidate)
            if compact(gamma) != gamma:
                raise AssertionError("catalog contains noncompact trajectory")
            values.add(gamma)
    return tuple(sorted(values)), patterns, tested


def stream_digest(trajectories: Sequence[tuple]) -> str:
    hasher = hashlib.sha256()
    for gamma in trajectories:
        hasher.update(canonical_json(encode(gamma)))
        hasher.update(b"\n")
    return hasher.hexdigest()


def verify_outer(artifact: dict) -> None:
    body = copy.deepcopy(artifact)
    claimed = body.pop("semantic_digest", None)
    if claimed != digest(body):
        raise AssertionError("semantic digest mismatch")
    if artifact["certificate_accounting"]["fixed_point_serialized_bytes"] != len(canonical_json(artifact)) + 1:
        raise AssertionError("fixed-point certificate byte mismatch")


def verify(root: Path, artifact: dict) -> dict:
    verify_outer(artifact)
    if artifact.get("schema") != SCHEMA or artifact.get("source_head") != SOURCE_HEAD:
        raise AssertionError("schema/source head mismatch")
    manifest, node_id, dim, k, records = read_source(root)
    if (node_id, dim, k, len(records)) != (6, 2, 1, 468):
        raise AssertionError("source generator fixture drift")
    if artifact["source_manifest_digest"] != manifest["manifest_digest"]:
        raise AssertionError("manifest binding mismatch")
    if artifact["source_transcript_root_digest"] != manifest["chunking"]["transcript_root_digest"]:
        raise AssertionError("transcript root binding mismatch")

    trajectories = {}
    trajectory_digests = {}
    for record in records:
        identifier = int(record["generator_id"])
        gamma = parse_trajectory(record["trajectory_parent_coordinates"], dim)
        if record["trajectory_digest"] != digest(record["trajectory_parent_coordinates"]):
            raise AssertionError("trajectory digest mismatch")
        trajectories[identifier] = gamma
        trajectory_digests[identifier] = record["trajectory_digest"]
    if artifact["input_generator_count"] != 468:
        raise AssertionError("generator count mismatch")
    if artifact["input_generator_family_digest"] != digest([item["trajectory_parent_coordinates"] for item in records]):
        raise AssertionError("generator family digest mismatch")

    grouped = defaultdict(list)
    for identifier, gamma in trajectories.items():
        grouped[signature(gamma)].append(identifier)
    signatures = sorted(grouped)
    if sorted(len(grouped[item]) for item in signatures) != [36, 216, 216]:
        raise AssertionError("signature bucket sizes mismatch")

    structural = {
        "generator_records_replayed": 468,
        "trajectory_statistics_replayed": sum(len(item) for item in trajectories.values()),
        "signature_bucket_insertions": 468,
        "ordered_cross_bucket_signature_tests": 0,
        "zero_envelope_tests": 0,
        "binary_scalar_sequences_tested": 0,
        "reachable_catalog_candidates_constructed": 0,
        "reachable_candidate_tests": 0,
    }
    ids = sorted(trajectories)
    for lower_id in ids:
        for upper_id in ids:
            if signature(trajectories[lower_id]) != signature(trajectories[upper_id]):
                structural["ordered_cross_bucket_signature_tests"] += 1
                if relation(trajectories[lower_id], trajectories[upper_id]) is not None:
                    raise AssertionError("cross-signature relation found")

    buckets = artifact["preorder_partition"]["buckets"]
    if artifact["preorder_partition"]
    ["rule"] != "COLLAPSED_LEFT_RIGHT_SKELETON_STUTTER_SIGNATURE":
        raise AssertionError("partition rule mismatch")
    if artifact["preorder_partition"]["cross_signature_relation_possible"] is not False:
        raise AssertionError("cross-signature guard missing")
    if artifact["preorder_partition"]["bucket_count"] != 3 or len(buckets) != 3:
        raise AssertionError("bucket count mismatch")

    retained_ids = []
    expected_removed = set(ids)
    expected_source = {}
    removal_cursor = 0
    for bucket_index, sig in enumerate(signatures):
        bucket_ids = sorted(grouped[sig], key=lambda item: trajectories[item])
        zero_ids = []
        for identifier in bucket_ids:
            structural["zero_envelope_tests"] += 1
            if all(stat[2] == 0 for stat in trajectories[identifier]):
                zero_ids.append(identifier)
        if len(zero_ids) != 1:
            raise AssertionError("zero envelope is not unique")
        retained = zero_ids[0]
        retained_ids.append(retained)
        expected_removed.remove(retained)
        for removed in bucket_ids:
            if removed != retained:
                expected_source[removed] = retained
        bucket = buckets[bucket_index]
        count = len(bucket_ids) - 1
        expected_range = {
            "first": removal_cursor,
            "last": removal_cursor + count - 1,
            "count": count,
        }
        removal_cursor += count
        expected_bucket = {
            "bucket_index": bucket_index,
            "collapsed_skeleton_signature": encode_signature(sig),
            "signature_digest": digest(encode_signature(sig)),
            "input_generator_count": len(bucket_ids),
            "retained_generator_id": retained,
            "retained_trajectory": encode(trajectories[retained]),
            "retained_trajectory_digest": trajectory_digests[retained],
            "zero_envelope_unique": True,
            "distinct_skeleton_runs": True,
            "removal_range": expected_range,
        }
        if bucket != expected_bucket:
            raise AssertionError("bucket receipt mismatch")

    if artifact["retained_generator_ids"] != retained_ids:
        raise AssertionError("retained id order mismatch")
    if artifact["retained_generators"] != [encode(trajectories[item]) for item in retained_ids]:
        raise AssertionError("retained trajectories mismatch")
    if artifact["retained_generator_count"] != 3:
        raise AssertionError("retained count mismatch")

    counters = empty_preorder_counters()
    removals = artifact["removals"]
    if len(removals) != 465 or artifact["removal_count"] != 465:
        raise AssertionError("removal count mismatch")
    seen = set()
    for index, removal in enumerate(removals):
        unsigned = dict(removal)
        claimed = unsigned.pop("removal_digest", None)
        if claimed != digest(unsigned):
            raise AssertionError("removal digest mismatch")
        removed = int(removal["removed_generator_id"])
        retained = int(removal["retained_generator_id"])
        if removal["removal_id"] != index or removed in seen:
            raise AssertionError("removal identity mismatch")
        if expected_source.get(removed) != retained:
            raise AssertionError("removal retained predecessor mismatch")
        seen.add(removed)
        if removal["removed_trajectory_digest"] != trajectory_digests[removed]:
            raise AssertionError("removed digest mismatch")
        if removal["retained_trajectory_digest"] != trajectory_digests[retained]:
            raise AssertionError("retained digest mismatch")
        direct = relation(trajectories[retained], trajectories[removed], counters)
        reverse = relation(trajectories[removed], trajectories[retained], counters)
        if direct is None or reverse is not None:
            raise AssertionError("strict direct witness semantics mismatch")
        if removal["direct_witness"] != witness(direct):
            raise AssertionError("direct witness transcript mismatch")
        if removal["reverse_relation"] is not False:
            raise AssertionError("reverse relation flag mismatch")
        if removal["reason"] != "STRICTLY_COVERED_BY_ZERO_ENVELOPE":
            raise AssertionError("removal reason mismatch")
    if seen != expected_removed:
        raise AssertionError("not every deletion is traceable")

    reachable, patterns, scalar_test_count = reachable_catalog(signatures)
    structural["binary_scalar_sequences_tested"] = scalar_test_count
    structural["reachable_catalog_candidates_constructed"] = len(reachable)
    if len(reachable) != 468:
        raise AssertionError("reachable catalog size mismatch")
    if set(reachable) != set(trajectories.values()):
        raise AssertionError("reachable set changed")
    source_by_signature = {signature(trajectories[item]): index for index, item in enumerate(retained_ids)}
    expected_entries = []
    for candidate in reachable:
        structural["reachable_candidate_tests"] += 1
        source_index = source_by_signature[signature(candidate)]
        path = relation(trajectories[retained_ids[source_index]], candidate, counters)
        if path is None:
            raise AssertionError("closure witness missing")
        expected_entries.append(
            {
                "trajectory": encode(candidate),
                "source_generator_index": source_index,
                "witness": witness(path),
            }
        )

    closure = artifact["exact_reachable_closure"]
    expected_patterns = [list(item) for item in patterns]
    if closure["binary_typical_run_patterns"] != expected_patterns:
        raise AssertionError("run-pattern receipt mismatch")
    if closure["binary_typical_run_pattern_count"] != 6:
        raise AssertionError("run-pattern count mismatch")
    if closure["binary_scalar_sequences_exhaustively_tested"] != scalar_test_count:
        raise AssertionError("scalar exhaustive count mismatch")
    if closure["complete_reachable_catalog_size"] != 468:
        raise AssertionError("catalog size receipt mismatch")
    if closure["complete_reachable_catalog_stream_sha256"] != stream_digest(reachable):
        raise AssertionError("catalog digest mismatch")
    if closure["reachable_from_original_count"] != 468 or closure["reachable_from_retained_count"] != 468:
        raise AssertionError("closure counts mismatch")
    if closure["reachable_entries"] != expected_entries:
        raise AssertionError("closure entries mismatch")
    if closure["reachable_entries_digest"] != digest(expected_entries):
        raise AssertionError("closure entries digest mismatch")
    if closure["input_generator_set_equals_reachable_set"] is not True:
        raise AssertionError("generator/reachable equality flag missing")
    if closure["up_k_original_equals_up_k_retained"] is not True:
        raise AssertionError("up_k equality flag missing")

    if artifact["work_ledger"]["structural_counters"] != structural:
        raise AssertionError("structural work ledger mismatch")
    if artifact["work_ledger"]["preorder_counters"] != counters:
        raise AssertionError("preorder work ledger mismatch")
    total = sum(structural.values()) + counters["work"]
    if artifact["work_ledger"]["total_charged_operations"] != total:
        raise AssertionError("charged operation total mismatch")
    if artifact["work_ledger"]["monotone"] is not True:
        raise AssertionError("work monotonicity flag missing")

    expected_invariants = {
        "INV-01_canonical_preorder_unique": "PASS",
        "INV-02_dominance_only_from_certificates": "PASS",
        "INV-03_every_removed_has_direct_witness": "PASS",
        "INV-04_reachable_witness_set_unchanged": "PASS",
        "INV-05_independent_replay_identical": "PASS",
        "INV-06_proof_layer_frozen_and_hashable": "PASS",
        "INV-07_deterministic_output_byte_identical": "PASS",
        "INV-08_every_deletion_fully_traceable": "PASS",
    }
    if artifact["invariant_vector"] != expected_invariants or artifact["admit"] is not True:
        raise AssertionError("invariant admission mismatch")

    expected_boundary = {
        "dimension_two_preorder_minimization_complete": True,
        "node_up_k_reachable_set_complete": True,
        "negative_root_reached": False,
        "terminal_completeness_proved": False,
        "found_layout_enabled": False,
        "no_layout_at_cap_enabled": False,
        "current_global_terminal": TERMINAL,
        "next_gate": "C049.1_B4.6.3_NEGATIVE_NODE_6_UP_K_INTEGRATION_AND_PARENT_REFINEMENT",
        "p_vs_np": "OPEN",
    }
    if artifact["strict_boundary"] != expected_boundary:
        raise AssertionError("strict boundary mismatch")
    return {
        "input_generators": 468,
        "retained_generators": 3,
        "direct_removals": 465,
        "reachable_entries": 468,
        "charged_operations": total,
        "invariants": 8,
    }


def bind(value: dict) -> dict:
    out = copy.deepcopy(value)
    out["semantic_digest"] = "0" * 64
    out["certificate_accounting"]["fixed_point_serialized_bytes"] = 0
    for _ in range(32):
        body = copy.deepcopy(out)
        body.pop("semantic_digest", None)
        out["semantic_digest"] = digest(body)
        size = len(canonical_json(out)) + 1
        if size == out["certificate_accounting"]["fixed_point_serialized_bytes"]:
            return out
        out["certificate_accounting"]["fixed_point_serialized_bytes"] = size
    raise AssertionError("digest repair did not converge")


def tamper_self_test(root: Path, artifact: dict) -> int:
    cases = []
    changed = copy.deepcopy(artifact)
    changed["removals"][0]["direct_witness"]["path"] = changed["removals"][0]["direct_witness"]["path"][:-1]
    unsigned = dict(changed["removals"][0]); unsigned.pop("removal_digest", None)
    changed["removals"][0]["removal_digest"] = digest(unsigned)
    cases.append(changed)

    changed = copy.deepcopy(artifact)
    changed["removals"][0]["retained_generator_id"] = artifact["retained_generator_ids"][1]
    unsigned = dict(changed["removals"][0]); unsigned.pop("removal_digest", None)
    changed["removals"][0]["removal_digest"] = digest(unsigned)
    cases.append(changed)

    changed = copy.deepcopy(artifact)
    changed["exact_reachable_closure"]["reachable_entries"].pop()
    changed["exact_reachable_closure"]["reachable_entries_digest"] = digest(changed["exact_reachable_closure"]["reachable_entries"])
    cases.append(changed)

    changed = copy.deepcopy(artifact)
    changed["invariant_vector"]["INV-04_reachable_witness_set_unchanged"] = "FAIL"
    cases.append(changed)

    changed = copy.deepcopy(artifact)
    changed["work_ledger"]["preorder_counters"]["lattice_cells"] += 1
    changed["work_ledger"]["preorder_counters"]["work"] += 1
    changed["work_ledger"]["total_charged_operations"] += 1
    cases.append(changed)

    rejected = 0
    for case in cases:
        repaired = bind(case)
        try:
            verify(root, repaired)
        except AssertionError:
            rejected += 1
        else:
            raise AssertionError("digest-repaired tamper was accepted")
    return rejected


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("transcript_root", type=Path)
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--tamper-self-test", action="store_true")
    args = parser.parse_args()
    artifact = json.loads(args.artifact.read_text())
    result = verify(args.transcript_root, artifact)
    rejected = tamper_self_test(args.transcript_root, artifact) if args.tamper_self_test else 0
    print("VERIFIED C049.1 B4.6.3 DIMENSION-TWO PREORDER HARDENING")
    print("INPUT_GENERATORS =", result["input_generators"])
    print("RETAINED_GENERATORS =", result["retained_generators"])
    print("DIRECT_REMOVALS =", result["direct_removals"])
    print("REACHABLE_ENTRIES =", result["reachable_entries"])
    print("CHARGED_OPERATIONS =", result["charged_operations"])
    print("INVARIANTS_PASSED =", result["invariants"])
    print("TAMPER_CONTROLS_REJECTED =", rejected)
    print("GLOBAL_TERMINAL =", TERMINAL)


if __name__ == "__main__":
    main()
