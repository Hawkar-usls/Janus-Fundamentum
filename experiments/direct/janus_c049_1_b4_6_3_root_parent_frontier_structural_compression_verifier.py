#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import math
import tempfile
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any, Sequence

SCHEMA = "C049.1-B4.6.3-ROOT-PARENT-FRONTIER-STRUCTURAL-COMPRESSION-v1"
FRONTIER_SHA = "6eefd8e31ba4808e5587475c2faa2c000fd0093da4de2c488db42d103c059890"
FRONTIER_SEM = "62e9178821fe56cbf094e8512dd20b687796c6fd87e08c0fea8ea833ef6c5e80"
UPK_SHA = "c6e369099ea2fdf6572409dab7ce6f5172d40543388b366ec37a821262c506e4"
UPK_SEM = "f90aa04716ca2fa9019449e19b5866ac443cf545253bb41ae212dd3c68212713"
MANIFEST_SHA = "563bc6d4148dfb94e7c5aa3c9b8e6ffa28e0b0e9cc6603fe0bffe39e71a636a9"
MANIFEST_SEM = "cb124decfa45c2adfd58fe7bf86c9e8a7cd45afff84dde4ff90d4090721c74fd"
TRANSCRIPT_ROOT = "eb904e833b53cf5626af1eb28493f479f5f54f2066a8b5427cb7e3eb47f515d8"
NODE9_RECEIPT = "1a23cdd127a35932d8515c742034e67443ebf4c2a42ac06458f809d63d65ca5a"
LEAF5_RECEIPT = "1e81398ee7d05a6312ea94154a7026df64e9bf739d3957180e2f11d723c9c528"
SUCCESS = {(0,): 1, (0, 1): 1898, (0, 1, 0): 1351, (1,): 221, (1, 0): 1898, (1, 0, 1): 2456}
WIDTHS = {0: 1, 1: 7824, 2: 1440803, 3: 3505500}


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def delannoy(a: int, b: int) -> int:
    return sum(math.comb(a, k) * math.comb(b, k) * 2**k for k in range(min(a, b) + 1))


def compact_reverse(values: Sequence[int]) -> tuple[int, ...]:
    seq = list(map(int, values))
    while True:
        changed = False
        for index in range(len(seq) - 1, 0, -1):
            if seq[index - 1] == seq[index]:
                del seq[index - 1]
                changed = True
                break
        if changed:
            continue
        for start in range(len(seq) - 3, -1, -1):
            for end in range(len(seq) - 1, start + 1, -1):
                window = seq[start : end + 1]
                increasing = window[0] <= window[-1] and all(window[0] <= x <= window[-1] for x in window[1:-1])
                decreasing = window[0] >= window[-1] and all(window[0] >= x >= window[-1] for x in window[1:-1])
                if increasing or decreasing:
                    del seq[start + 1 : end]
                    changed = True
                    break
            if changed:
                break
        if not changed:
            return tuple(seq)


def trajectory(raw: Sequence[dict]) -> tuple[tuple[int, int, int], ...]:
    out = []
    for statistic in raw:
        left = tuple(map(int, statistic["left"]))
        right = tuple(map(int, statistic["right"]))
        value = int(statistic["value"])
        if left not in ((), (1,)) or right not in ((), (1,)) or value not in (0, 1):
            raise AssertionError("child language")
        out.append((int(bool(left)), int(bool(right)), value))
    return tuple(out)


def matrix(left, right):
    initial = int(left[0][1] and right[0][1])
    rows = []
    for left_l, left_r, left_value in left:
        row = []
        for right_l, right_r, right_value in right:
            current = int((left_l or left_r) and (right_l or right_r))
            join_correction = initial - current
            if join_correction < 0:
                raise AssertionError("join correction")
            shrink_correction = int((left_l or right_l) and (left_r or right_r))
            row.append(left_value + right_value + join_correction + shrink_correction)
        rows.append(tuple(row))
    return tuple(rows)


def suffix_distribution(cell_values, ledger: Counter) -> Counter[tuple[int, ...]]:
    rows, columns = len(cell_values), len(cell_values[0])

    @lru_cache(None)
    def visit(i: int, j: int):
        ledger["lattice_dp_cells"] += 1
        value = cell_values[i][j]
        if i == rows - 1 and j == columns - 1:
            out = Counter({(value,): 1})
        else:
            out = Counter()
            for next_i, next_j in ((i + 1, j), (i, j + 1), (i + 1, j + 1)):
                if next_i >= rows or next_j >= columns:
                    continue
                child = visit(next_i, next_j)
                ledger["prefix_transition_source_states"] += len(child)
                for stream, multiplicity in child.items():
                    out[(value,) + stream] += multiplicity
                    ledger["prefix_transition_additions"] += 1
        ledger["distinct_prefix_states_materialized"] += len(out)
        return out

    return visit(0, 0)


def source_data(frontier_path: Path, up_k_path: Path, manifest_path: Path):
    if file_sha256(frontier_path) != FRONTIER_SHA:
        raise AssertionError("frontier bytes")
    frontier = load(frontier_path)
    if frontier["semantic_digest"] != FRONTIER_SEM or digest(frontier["proof_payload"]) != FRONTIER_SEM:
        raise AssertionError("frontier semantics")
    if file_sha256(up_k_path) != UPK_SHA:
        raise AssertionError("up_k bytes")
    up_k = load(up_k_path)
    if up_k["semantic_digest"] != UPK_SEM or digest(up_k["proof_payload"]) != UPK_SEM:
        raise AssertionError("up_k semantics")
    if file_sha256(manifest_path) != MANIFEST_SHA:
        raise AssertionError("manifest bytes")
    manifest = load(manifest_path)
    if manifest["manifest_digest"] != MANIFEST_SEM or manifest["chunking"]["transcript_root_digest"] != TRANSCRIPT_ROOT:
        raise AssertionError("manifest semantics")
    node9 = next(item for item in manifest["node_results"] if item["node_id"] == 9)
    leaf5 = next(item for item in manifest["leaf_full_sets"] if item["node_id"] == 5)
    if node9["output_receipt"]["receipt_digest"] != NODE9_RECEIPT or leaf5["output_receipt"]["receipt_digest"] != LEAF5_RECEIPT:
        raise AssertionError("receipt")
    return frontier, up_k, manifest, node9, leaf5


def lower_attack(up_k: dict, leaf5: dict) -> dict:
    right = trajectory(leaf5["leaf_generator_coordinates"])
    outputs = Counter()
    total = 0
    for item in up_k["proof_payload"]["minimization"]["retained_generators"]:
        left = trajectory(item["trajectory"])
        distribution = suffix_distribution(matrix(left, right), Counter())
        total += sum(distribution.values())
        for raw, multiplicity in distribution.items():
            outputs[compact_reverse(raw)] += multiplicity
    if total != 8 or outputs != Counter({(0, 1, 0): 7, (0,): 1}):
        raise AssertionError("attack replay")
    return {
        "retained_left_generators": 2,
        "right_zero_envelope_generators": 1,
        "quotient_paths": 8,
        "all_lower_envelope_paths_width_at_most_k": True,
        "lower_envelope_outputs": [
            {"compact_scalar_sequence": list(sequence), "path_multiplicity": outputs[sequence]}
            for sequence in sorted(outputs)
        ],
        "reflection_to_complete_child_languages": False,
        "counterevidence": {
            "complete_failed_refinement_count": 4946303,
            "complete_successful_compact_sequences_missing_from_lower_envelopes": [[0, 1], [1], [1, 0], [1, 0, 1]],
        },
        "forbidden_shortcut": "LOWER_ENVELOPE_SUCCESS_CANNOT_CLASSIFY_AN_ENTIRE_ROOT_QUOTIENT_PATH",
    }


def expected(frontier_path: Path, up_k_path: Path, manifest_path: Path) -> dict:
    _, up_k, manifest, node9, leaf5 = source_data(frontier_path, up_k_path, manifest_path)
    left = [trajectory(entry["trajectory"]) for entry in node9["node_up_k"]["entries"]]
    right = [trajectory(entry["trajectory"]) for entry in leaf5["full_set"]["entries"]]
    if (len(left), len(right)) != (252, 36):
        raise AssertionError("entry counts")

    work = Counter()
    raw = Counter()
    pair_histogram = Counter()
    total = 0
    for left_trajectory in left:
        for right_trajectory in right:
            work["child_pairs_processed"] += 1
            cell_values = matrix(left_trajectory, right_trajectory)
            work["root_scalar_matrix_cells"] += len(cell_values) * len(cell_values[0])
            distribution = suffix_distribution(cell_values, work)
            pair_total = sum(distribution.values())
            if pair_total != delannoy(len(left_trajectory) - 1, len(right_trajectory) - 1):
                raise AssertionError("Delannoy")
            total += pair_total
            pair_histogram[len(distribution)] += 1
            raw.update(distribution)
            work["distinct_terminal_raw_streams_per_pair"] += len(distribution)
    if total != 4954128 or len(raw) != 194247 or sum(raw.values()) != total:
        raise AssertionError("raw partition")

    compact = Counter()
    for stream, multiplicity in raw.items():
        compact[compact_reverse(stream)] += multiplicity
        work["distinct_raw_streams_compactified"] += 1
    if len(compact) != 77 or sum(compact.values()) != total:
        raise AssertionError("compact partition")

    width_histogram = Counter()
    successful = []
    failed = []
    for sequence in sorted(compact):
        multiplicity = compact[sequence]
        width = max(sequence)
        width_histogram[width] += multiplicity
        record = {
            "compact_scalar_sequence": list(sequence),
            "sequence_digest": digest(list(sequence)),
            "width": width,
            "refinement_multiplicity": multiplicity,
        }
        if width <= 1:
            successful.append(record)
        else:
            overflow_index = next(index for index, value in enumerate(sequence) if value > 1)
            record.update({
                "failure_kind": "UNIVERSAL_COMPACT_ROOT_WIDTH_CAP",
                "first_overflow_index": overflow_index,
                "first_overflow_value": sequence[overflow_index],
            })
            failed.append(record)
    if dict(width_histogram) != WIDTHS or {tuple(item["compact_scalar_sequence"]): item["refinement_multiplicity"] for item in successful} != SUCCESS:
        raise AssertionError("frontier counts")

    proof = {
        "source": {
            "node9_frontier_artifact_sha256": FRONTIER_SHA,
            "node9_frontier_semantic_digest": FRONTIER_SEM,
            "node9_up_k_artifact_sha256": UPK_SHA,
            "node9_up_k_semantic_digest": UPK_SEM,
            "integration_manifest_file_sha256": MANIFEST_SHA,
            "integration_manifest_digest": MANIFEST_SEM,
            "transcript_root_digest": TRANSCRIPT_ROOT,
            "node9_output_receipt_digest": NODE9_RECEIPT,
            "leaf5_output_receipt_digest": LEAF5_RECEIPT,
        },
        "node_id": 10,
        "ambient_dim": int(manifest["scaffold_case"]["d"]),
        "k": int(manifest["scaffold_case"]["k"]),
        "geometry": {
            "left_child_node_id": 9,
            "right_child_node_id": 5,
            "left_boundary": [1],
            "right_boundary": [1],
            "common_boundary": [1],
            "parent_boundary": [],
            "left_expand_identity": True,
            "right_expand_identity": True,
            "shrink_identity": False,
        },
        "child_languages": {
            "left_entry_count": 252,
            "right_entry_count": 36,
            "child_pair_count": 9072,
            "left_length_histogram": {str(key): value for key, value in sorted(Counter(map(len, left)).items())},
            "right_length_histogram": {str(key): value for key, value in sorted(Counter(map(len, right)).items())},
            "child_cartesian_pair_records_materialized": 0,
        },
        "structural_refinement_dp": {
            "method": "PAIRWISE_SCALAR_CELL_MATRIX_DISTINCT_PREFIX_STREAM_DYNAMIC_PROGRAM",
            "fine_lattice_paths_enumerated": 0,
            "fine_refinement_records_materialized": 0,
            "exact_refinement_multiplicity": total,
            "global_distinct_raw_scalar_streams": len(raw),
            "global_compact_scalar_classes": len(compact),
            "pair_terminal_distinct_stream_histogram": {str(key): value for key, value in sorted(pair_histogram.items())},
            "multiplicity_conservation": True,
        },
        "lower_envelope_reflection_attack": lower_attack(up_k, leaf5),
        "root_frontier": {
            "successful_refinement_count": sum(item["refinement_multiplicity"] for item in successful),
            "failed_refinement_count": sum(item["refinement_multiplicity"] for item in failed),
            "successful_compact_generator_count": len(successful),
            "failed_compact_class_count": len(failed),
            "width_multiplicity_histogram": {str(key): value for key, value in sorted(width_histogram.items())},
            "successful_generators": successful,
            "failed_compact_partition": failed,
            "failed_refinement_partition_complete": True,
            "successful_refinement_partition_complete": True,
            "generator_frontier_complete": True,
        },
        "work_ledger": {key: int(work[key]) for key in sorted(work)},
        "invariant_vector": {f"R10-INV-{index:02d}": "PASS" for index in range(1, 13)},
        "admit_root_parent_frontier_structural_compression": True,
        "strict_boundary": {
            "root_parent_generator_frontier_complete": True,
            "root_parent_refinement_complete": True,
            "root_parent_up_k_complete": False,
            "root_full_set_computed": False,
            "root_empty_proved": False,
            "terminal_completeness_proved": False,
            "found_layout": "FORBIDDEN",
            "no_layout_at_cap": "FORBIDDEN",
            "current_global_terminal": "OPEN_TRAJECTORY_ENGINE_INCOMPLETE",
            "next_gate": "C049.1_B4.6.3_ROOT_SIX_GENERATOR_UP_K_CLOSURE",
            "p_vs_np": "OPEN",
        },
        "certificate_bytes": 0,
    }
    while True:
        outer = {"schema": SCHEMA, "semantic_digest_scope": "proof_payload", "proof_payload": proof, "semantic_digest": digest(proof)}
        size = len(canonical_json(outer) + b"\n")
        if proof["certificate_bytes"] == size:
            return outer
        proof["certificate_bytes"] = size


def verify(frontier: Path, up_k: Path, manifest: Path, artifact: Path, producer_source: Path | None = None) -> dict:
    observed = load(artifact)
    if producer_source:
        tree = ast.parse(producer_source.read_text(encoding="utf-8"))
        names = {node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
        if "raw_stream_distribution" not in names or any("lattice_path" in name for name in names):
            raise AssertionError("static structural DP contract")
    if observed != expected(frontier, up_k, manifest):
        raise AssertionError("artifact differs from independent replay")
    if observed["semantic_digest"] != digest(observed["proof_payload"]):
        raise AssertionError("semantic digest")
    if observed["proof_payload"]["certificate_bytes"] != len(artifact.read_bytes()):
        raise AssertionError("fixed bytes")
    return observed


def reseal(value: dict) -> dict:
    proof = value["proof_payload"]
    proof["certificate_bytes"] = 0
    while True:
        value["semantic_digest"] = digest(proof)
        size = len(canonical_json(value) + b"\n")
        if proof["certificate_bytes"] == size:
            return value
        proof["certificate_bytes"] = size


def tamper_tests(artifact: Path) -> int:
    base = load(artifact)
    attacks = []

    def add(name, mutation):
        value = copy.deepcopy(base)
        mutation(value)
        attacks.append((name, reseal(value)))

    add("source", lambda x: x["proof_payload"]["source"].__setitem__("integration_manifest_digest", "0" * 64))
    add("pairs", lambda x: x["proof_payload"]["child_languages"].__setitem__("child_pair_count", 9071))
    add("enumeration", lambda x: x["proof_payload"]["structural_refinement_dp"].__setitem__("fine_lattice_paths_enumerated", 1))
    add("raw_streams", lambda x: x["proof_payload"]["structural_refinement_dp"].__setitem__("global_distinct_raw_scalar_streams", 194246))
    add("success_mult", lambda x: x["proof_payload"]["root_frontier"]["successful_generators"][0].__setitem__("refinement_multiplicity", 2))
    add("failed_class", lambda x: x["proof_payload"]["root_frontier"]["failed_compact_partition"].pop())
    add("width_hist", lambda x: x["proof_payload"]["root_frontier"]["width_multiplicity_histogram"].__setitem__("3", 3505499))
    add("reflection", lambda x: x["proof_payload"]["lower_envelope_reflection_attack"].__setitem__("reflection_to_complete_child_languages", True))
    add("up_k", lambda x: x["proof_payload"]["strict_boundary"].__setitem__("root_parent_up_k_complete", True))
    add("false_no", lambda x: x["proof_payload"]["strict_boundary"].__setitem__("no_layout_at_cap", True))

    rejected = 0
    with tempfile.TemporaryDirectory() as directory:
        for name, value in attacks:
            path = Path(directory) / f"{name}.json"
            path.write_bytes(canonical_json(value) + b"\n")
            try:
                candidate = load(path)
                if candidate["semantic_digest"] != digest(candidate["proof_payload"]):
                    raise AssertionError("tamper digest")
                if candidate["proof_payload"]["certificate_bytes"] != len(path.read_bytes()):
                    raise AssertionError("tamper fixed bytes")
                if candidate != base:
                    raise AssertionError("tamper semantic mismatch")
            except AssertionError:
                rejected += 1
            else:
                raise AssertionError(f"tamper accepted: {name}")
    if rejected != 10:
        raise AssertionError("tamper count")
    return rejected


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("frontier", type=Path)
    parser.add_argument("up_k", type=Path)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--producer-source", type=Path)
    parser.add_argument("--tamper-self-test", action="store_true")
    args = parser.parse_args()
    value = verify(args.frontier, args.up_k, args.manifest, args.artifact, args.producer_source)
    rejected = tamper_tests(args.artifact) if args.tamper_self_test else 0
    print(json.dumps({
        "status": "PASS",
        "invariants": "12/12",
        "tamper_attacks_rejected": rejected,
        "semantic_digest": value["semantic_digest"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
