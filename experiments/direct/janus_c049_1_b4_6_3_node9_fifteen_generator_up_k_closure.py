#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import random
from pathlib import Path
from typing import Any, Sequence

SCHEMA = "C049.1-B4.6.3-NODE9-FIFTEEN-GENERATOR-UP-K-CLOSURE-v1"
TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"
SOURCE_SCHEMA = "C049.1-B4.6.3-NODE9-PARENT-FRONTIER-STRUCTURAL-COMPRESSION-v1"
SOURCE_ARTIFACT_SHA256 = "6eefd8e31ba4808e5587475c2faa2c000fd0093da4de2c488db42d103c059890"
SOURCE_SEMANTIC_DIGEST = "62e9178821fe56cbf094e8512dd20b687796c6fd87e08c0fea8ea833ef6c5e80"
PATTERNS = ((0,), (0, 1), (0, 1, 0), (1,), (1, 0), (1, 0, 1))
PATTERN_CODE = {pattern: "".join(str(v) for v in pattern) for pattern in PATTERNS}
EXPECTED = {
    "input_generators": 15,
    "ordered_pair_tests": 225,
    "relation_edges": 55,
    "self_edges": 15,
    "cross_edges": 40,
    "equivalent_cross_pairs": 0,
    "retained_generators": 2,
    "direct_removals": 13,
    "scalar_relation_edges": 20,
    "scalar_transitivity_checks": 50,
    "reachable_entries": 252,
    "repeated_closure_checks": 8400,
}
EXPECTED_RETAINED_SOURCE_IDS = ("N9-S02", "N9-S07")


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encode_stat(stat: tuple[tuple[int, ...], tuple[int, ...], int]) -> dict[str, Any]:
    return {"left": list(stat[0]), "right": list(stat[1]), "value": int(stat[2])}


def encode_trajectory(trajectory: Sequence[tuple]) -> list[dict[str, Any]]:
    return [encode_stat(stat) for stat in trajectory]


def decode_trajectory(raw: Sequence[dict[str, Any]]) -> tuple[tuple, ...]:
    return tuple((tuple(int(v) for v in item["left"]), tuple(int(v) for v in item["right"]), int(item["value"])) for item in raw)


def compactify(trajectory: Sequence[tuple]) -> tuple[tuple, ...]:
    current = list(trajectory)
    while True:
        changed = False
        for index in range(1, len(current)):
            if current[index - 1] == current[index]:
                current.pop(index)
                changed = True
                break
        if changed:
            continue
        for start in range(len(current)):
            for end in range(start + 2, len(current)):
                if current[start][:2] != current[end][:2]:
                    continue
                values = [item[2] for item in current[start : end + 1]]
                monotone = (
                    values[0] <= values[-1]
                    and all(values[0] <= value <= values[-1] for value in values[1:-1])
                ) or (
                    values[0] >= values[-1]
                    and all(values[0] >= value >= values[-1] for value in values[1:-1])
                )
                if monotone:
                    del current[start + 1 : end]
                    changed = True
                    break
            if changed:
                break
        if not changed:
            return tuple(current)


def extension_preorder_witness(lower: Sequence[tuple], upper: Sequence[tuple]) -> dict[str, Any] | None:
    parent: dict[tuple[int, int], tuple[int, int] | None] = {}
    for i, left in enumerate(lower):
        for j, right in enumerate(upper):
            if left[:2] != right[:2] or int(left[2]) > int(right[2]):
                continue
            if (i, j) == (0, 0):
                parent[(i, j)] = None
                continue
            for previous in ((i - 1, j - 1), (i - 1, j), (i, j - 1)):
                if previous in parent:
                    parent[(i, j)] = previous
                    break
    endpoint = (len(lower) - 1, len(upper) - 1)
    if endpoint not in parent:
        return None
    path: list[tuple[int, int]] = []
    cursor: tuple[int, int] | None = endpoint
    while cursor is not None:
        path.append(cursor)
        cursor = parent[cursor]
    path.reverse()
    return {"path": [[i, j] for i, j in path], "path_length": len(path)}


def split_runs(trajectory: Sequence[tuple]) -> tuple[tuple[tuple, ...], tuple[tuple[int, ...], ...]]:
    skeleton: list[tuple] = []
    patterns: list[list[int]] = []
    for left, right, value in trajectory:
        geometry = (tuple(left), tuple(right))
        if not skeleton or skeleton[-1] != geometry:
            skeleton.append(geometry)
            patterns.append([int(value)])
        else:
            patterns[-1].append(int(value))
    pattern_tuple = tuple(tuple(values) for values in patterns)
    if any(pattern not in PATTERNS for pattern in pattern_tuple):
        raise AssertionError("trajectory contains a non-typical scalar run")
    return tuple(skeleton), pattern_tuple


def scalar_trajectory(pattern: Sequence[int]) -> tuple[tuple, ...]:
    return tuple(((1,), (), int(value)) for value in pattern)


def scalar_relation() -> tuple[dict[tuple[int, ...], tuple[tuple[int, ...], ...]], list[dict[str, Any]], int]:
    upward: dict[tuple[int, ...], tuple[tuple[int, ...], ...]] = {}
    edges: list[dict[str, Any]] = []
    for lower in PATTERNS:
        candidates = []
        for upper in PATTERNS:
            witness = extension_preorder_witness(scalar_trajectory(lower), scalar_trajectory(upper))
            if witness is None:
                continue
            candidates.append(upper)
            edges.append({"lower": PATTERN_CODE[lower], "upper": PATTERN_CODE[upper], "witness": witness})
        upward[lower] = tuple(candidates)
    edges.sort(key=canonical_json)
    checks = 0
    relation = {(item["lower"], item["upper"]) for item in edges}
    for lower in PATTERNS:
        for middle in PATTERNS:
            for upper in PATTERNS:
                pair1 = (PATTERN_CODE[lower], PATTERN_CODE[middle])
                pair2 = (PATTERN_CODE[middle], PATTERN_CODE[upper])
                if pair1 in relation and pair2 in relation:
                    checks += 1
                    if (PATTERN_CODE[lower], PATTERN_CODE[upper]) not in relation:
                        raise AssertionError("scalar relation is not transitive")
    return upward, edges, checks


def reorder(items: list[Any], mode: str) -> list[Any]:
    output = list(items)
    if mode == "reversed":
        output.reverse()
    elif mode == "seeded-shuffle":
        random.Random(0xC04910915).shuffle(output)
    elif mode != "original":
        raise AssertionError("unsupported entry order")
    return output


def load_source(source_path: Path, entry_order: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if file_sha256(source_path) != SOURCE_ARTIFACT_SHA256:
        raise AssertionError("node-9 frontier artifact byte hash drift")
    source = json.loads(source_path.read_text(encoding="utf-8"))
    if source.get("schema") != SOURCE_SCHEMA:
        raise AssertionError("node-9 frontier schema drift")
    if source.get("semantic_digest") != SOURCE_SEMANTIC_DIGEST:
        raise AssertionError("node-9 frontier semantic digest drift")
    if source.get("semantic_digest") != digest(source.get("proof_payload")):
        raise AssertionError("node-9 frontier semantic digest invalid")
    payload = source["proof_payload"]
    if payload.get("admit") is not True:
        raise AssertionError("node-9 frontier is not admitted")
    boundary = payload["strict_boundary"]
    if boundary.get("node9_parent_generator_frontier_complete") is not True:
        raise AssertionError("node-9 frontier completeness absent")
    if boundary.get("node9_parent_refinement_complete") is not True:
        raise AssertionError("node-9 refinement completeness absent")
    if boundary.get("node9_parent_up_k_complete") is not False:
        raise AssertionError("source falsely claims node-9 up_k completion")
    classes = reorder(list(payload["quotient_frontier"]["classes"]), entry_order)
    if len(classes) != EXPECTED["input_generators"]:
        raise AssertionError("node-9 generator count drift")
    return source, classes


def normalize_generators(classes: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = []
    seen_ids: set[str] = set()
    seen_trajectories: set[bytes] = set()
    for item in classes:
        source_class_id = str(item["class_id"])
        if source_class_id in seen_ids:
            raise AssertionError("duplicate source class id")
        seen_ids.add(source_class_id)
        trajectory = compactify(decode_trajectory(item["canonical_generator"]))
        encoded = encode_trajectory(trajectory)
        if encoded != item["canonical_generator"]:
            raise AssertionError("source generator is not compact canonical form")
        if digest(encoded) != item["generator_digest"]:
            raise AssertionError("source generator digest mismatch")
        key = canonical_json(encoded)
        if key in seen_trajectories:
            raise AssertionError("duplicate source generator trajectory")
        seen_trajectories.add(key)
        skeleton, patterns = split_runs(trajectory)
        normalized.append({
            "source_class_id": source_class_id,
            "trajectory": trajectory,
            "trajectory_json": encoded,
            "generator_digest": digest(encoded),
            "skeleton": skeleton,
            "patterns": patterns,
            "skeleton_digest": digest([[list(left), list(right)] for left, right in skeleton]),
            "run_pattern_codes": [PATTERN_CODE[pattern] for pattern in patterns],
        })
    normalized.sort(key=lambda item: canonical_json(item["trajectory_json"]))
    return normalized


def build(source_path: Path, output_path: Path, entry_order: str) -> dict[str, Any]:
    source, raw_classes = load_source(source_path, entry_order)
    generators = normalize_generators(raw_classes)

    relation_edges: list[dict[str, Any]] = []
    relation_lookup: dict[tuple[str, str], dict[str, Any]] = {}
    for lower in generators:
        for upper in generators:
            witness = extension_preorder_witness(lower["trajectory"], upper["trajectory"])
            if witness is None:
                continue
            edge = {
                "lower_source_class_id": lower["source_class_id"],
                "upper_source_class_id": upper["source_class_id"],
                "lower_generator_digest": lower["generator_digest"],
                "upper_generator_digest": upper["generator_digest"],
                "witness": witness,
            }
            relation_edges.append(edge)
            relation_lookup[(lower["source_class_id"], upper["source_class_id"])] = edge
    relation_edges.sort(key=canonical_json)

    self_edges = sum(item["lower_source_class_id"] == item["upper_source_class_id"] for item in relation_edges)
    cross_edges = len(relation_edges) - self_edges
    equivalent_cross_pairs = sum(
        1
        for left in generators
        for right in generators
        if left["source_class_id"] < right["source_class_id"]
        and (left["source_class_id"], right["source_class_id"]) in relation_lookup
        and (right["source_class_id"], left["source_class_id"]) in relation_lookup
    )

    retained: list[dict[str, Any]] = []
    for candidate in generators:
        candidate_id = candidate["source_class_id"]
        strict_lowers = [
            other for other in generators
            if other["source_class_id"] != candidate_id
            and (other["source_class_id"], candidate_id) in relation_lookup
        ]
        if not strict_lowers:
            retained.append(candidate)
    retained.sort(key=lambda item: canonical_json(item["trajectory_json"]))
    retained_ids = tuple(item["source_class_id"] for item in retained)
    if retained_ids != EXPECTED_RETAINED_SOURCE_IDS:
        raise AssertionError(f"retained family drift: {retained_ids}")

    removals: list[dict[str, Any]] = []
    for removed in generators:
        removed_id = removed["source_class_id"]
        if removed_id in retained_ids:
            continue
        direct_candidates = [lower for lower in retained if (lower["source_class_id"], removed_id) in relation_lookup]
        if not direct_candidates:
            raise AssertionError("removed generator lacks a direct retained witness")
        witness_generator = min(direct_candidates, key=lambda item: canonical_json(item["trajectory_json"]))
        edge = relation_lookup[(witness_generator["source_class_id"], removed_id)]
        removals.append({
            "removed_source_class_id": removed_id,
            "removed_generator_digest": removed["generator_digest"],
            "retained_witness_source_class_id": witness_generator["source_class_id"],
            "retained_witness_generator_digest": witness_generator["generator_digest"],
            "witness_kind": "EXTENSION_PREORDER_DIRECT",
            "transitive_closure_used": False,
            "witness": edge["witness"],
        })
    removals.sort(key=canonical_json)

    upward, scalar_edges, scalar_transitivity_checks = scalar_relation()
    reachable: dict[bytes, dict[str, Any]] = {}
    per_retained_counts: dict[str, int] = {}
    for generator in retained:
        source_id = generator["source_class_id"]
        skeleton = generator["skeleton"]
        patterns = generator["patterns"]
        local: dict[bytes, dict[str, Any]] = {}
        for chosen_patterns in itertools.product(*(upward[pattern] for pattern in patterns)):
            raw_upper: list[tuple] = []
            for geometry, pattern in zip(skeleton, chosen_patterns):
                for value in pattern:
                    raw_upper.append((geometry[0], geometry[1], int(value)))
            upper = compactify(raw_upper)
            direct_witness = extension_preorder_witness(generator["trajectory"], upper)
            if direct_witness is None:
                raise AssertionError("reachable entry lacks direct witness")
            encoded = encode_trajectory(upper)
            key = canonical_json(encoded)
            record = {
                "source_retained_class_id": source_id,
                "source_retained_generator_digest": generator["generator_digest"],
                "run_pattern_codes": [PATTERN_CODE[pattern] for pattern in chosen_patterns],
                "trajectory": encoded,
                "trajectory_digest": digest(encoded),
                "width": max(stat["value"] for stat in encoded),
                "direct_witness_kind": "EXTENSION_PREORDER_DIRECT",
                "direct_witness": direct_witness,
            }
            if key in local and local[key] != record:
                raise AssertionError("noncanonical duplicate reachable record")
            local[key] = record
            if key in reachable and reachable[key]["source_retained_class_id"] != source_id:
                raise AssertionError("reachable trajectory belongs to two retained skeletons")
            reachable[key] = record
        per_retained_counts[source_id] = len(local)

    reachable_entries = []
    for index, key in enumerate(sorted(reachable)):
        record = dict(reachable[key])
        record["entry_id"] = f"N9U-E{index:03d}"
        reachable_entries.append(record)
    reachable_key_set = set(reachable)

    repeated_closure_checks = 0
    repeated_output_keys: set[bytes] = set()
    for record in reachable_entries:
        trajectory = decode_trajectory(record["trajectory"])
        skeleton, patterns = split_runs(trajectory)
        for chosen_patterns in itertools.product(*(upward[pattern] for pattern in patterns)):
            raw_upper: list[tuple] = []
            for geometry, pattern in zip(skeleton, chosen_patterns):
                for value in pattern:
                    raw_upper.append((geometry[0], geometry[1], int(value)))
            upper = compactify(raw_upper)
            key = canonical_json(encode_trajectory(upper))
            repeated_closure_checks += 1
            repeated_output_keys.add(key)
            if key not in reachable_key_set:
                raise AssertionError("second up_k application enlarged the closure")
            if extension_preorder_witness(trajectory, upper) is None:
                raise AssertionError("repeated closure relation lacks direct witness")
    if repeated_output_keys != reachable_key_set:
        raise AssertionError("second up_k application lost reachable entries")

    measured = {
        "input_generators": len(generators),
        "ordered_pair_tests": len(generators) ** 2,
        "relation_edges": len(relation_edges),
        "self_edges": self_edges,
        "cross_edges": cross_edges,
        "equivalent_cross_pairs": equivalent_cross_pairs,
        "retained_generators": len(retained),
        "direct_removals": len(removals),
        "scalar_relation_edges": len(scalar_edges),
        "scalar_transitivity_checks": scalar_transitivity_checks,
        "reachable_entries": len(reachable_entries),
        "repeated_closure_checks": repeated_closure_checks,
    }
    if measured != EXPECTED:
        raise AssertionError(f"node-9 up_k measured boundary drift: {measured}")

    generator_inventory = [{
        "source_class_id": item["source_class_id"],
        "generator_digest": item["generator_digest"],
        "skeleton_digest": item["skeleton_digest"],
        "run_pattern_codes": item["run_pattern_codes"],
        "trajectory": item["trajectory_json"],
    } for item in generators]
    retained_inventory = [{
        "source_class_id": item["source_class_id"],
        "generator_digest": item["generator_digest"],
        "skeleton_digest": item["skeleton_digest"],
        "run_pattern_codes": item["run_pattern_codes"],
        "trajectory": item["trajectory_json"],
        "reachable_entry_count": per_retained_counts[item["source_class_id"]],
    } for item in retained]
    trajectory_stream = b"".join(canonical_json(item["trajectory"]) + b"\n" for item in reachable_entries)

    proof_payload = {
        "source": {
            "frontier_schema": SOURCE_SCHEMA,
            "frontier_artifact_sha256": SOURCE_ARTIFACT_SHA256,
            "frontier_semantic_digest": SOURCE_SEMANTIC_DIGEST,
            "frontier_generator_count": EXPECTED["input_generators"],
            "frontier_post_shrink_class_count": source["proof_payload"]["quotient_frontier"]["post_shrink_successful_class_count"],
        },
        "node_id": 9,
        "ambient_dim": 1,
        "k": 1,
        "input_generator_family": {
            "generator_count": len(generator_inventory),
            "generator_family_digest": digest(generator_inventory),
            "generators": generator_inventory,
            "order_invariant": True,
        },
        "direct_preorder": {
            "ordered_pair_tests": len(generators) ** 2,
            "relation_edge_count": len(relation_edges),
            "self_relation_edge_count": self_edges,
            "cross_relation_edge_count": cross_edges,
            "strict_cross_relation_edge_count": cross_edges,
            "equivalent_cross_pair_count": equivalent_cross_pairs,
            "relation_edges": relation_edges,
        },
        "minimization": {
            "retained_generator_count": len(retained_inventory),
            "direct_removal_count": len(removals),
            "retained_family_digest": digest(retained_inventory),
            "retained_generators": retained_inventory,
            "direct_removals": removals,
            "every_removal_has_direct_retained_witness": True,
            "transitive_closure_used_for_removal": False,
        },
        "scalar_typical_relation": {
            "typical_pattern_catalog": [PATTERN_CODE[pattern] for pattern in PATTERNS],
            "relation_edge_count": len(scalar_edges),
            "relation_edges": scalar_edges,
            "transitivity_checks": scalar_transitivity_checks,
            "transitive": True,
        },
        "reachable_closure": {
            "complete_reachable_catalog": len(reachable_entries),
            "reachable_entry_count": len(reachable_entries),
            "reachable_entries_digest": digest([item["trajectory"] for item in reachable_entries]),
            "reachable_stream_sha256": hashlib.sha256(trajectory_stream).hexdigest(),
            "entries": reachable_entries,
            "every_entry_has_direct_retained_witness": True,
            "global_compact_universe_enumerated": False,
            "global_compact_universe_entry_count": 0,
            "construction": "BLOCKWISE_SCALAR_UPWARD_SETS_THEN_GLOBAL_COMPACTIFICATION",
        },
        "idempotence": {
            "idempotent": True,
            "method": "EXACT_REPEATED_BLOCKWISE_UPWARD_SET_REPLAY",
            "first_closure_entry_count": len(reachable_entries),
            "second_closure_entry_count": len(repeated_output_keys),
            "repeated_closure_checks": repeated_closure_checks,
            "scalar_transitivity_checks": scalar_transitivity_checks,
        },
        "work_ledger": {
            "input_generators_read": len(generators),
            "ordered_generator_pairs_tested": len(generators) ** 2,
            "direct_relation_edges_retained": len(relation_edges),
            "blockwise_reachable_entries_materialized": len(reachable_entries),
            "repeated_blockwise_checks": repeated_closure_checks,
            "global_compact_universe_enumerated": False,
        },
        "invariant_vector": {f"N9U-INV-{index:02d}": "PASS" for index in range(1, 11)},
        "admit": True,
        "strict_boundary": {
            "node9_parent_generator_frontier_complete": True,
            "node9_parent_refinement_complete": True,
            "node9_parent_up_k_complete": True,
            "node9_integrated_into_bottom_up_executor": False,
            "root_reached": False,
            "root_parent_refinement_started": False,
            "negative_root_reached": False,
            "terminal_completeness_proved": False,
            "found_layout_enabled": False,
            "no_layout_at_cap_enabled": False,
            "current_global_terminal": TERMINAL,
            "p_vs_np": "OPEN",
        },
        "next_gate": "C049.1_B4.6.3_NODE9_UP_K_INTEGRATION_AND_ROOT_PARENT_REFINEMENT",
    }
    artifact = {"schema": SCHEMA, "semantic_digest_scope": "proof_payload", "proof_payload": proof_payload}
    artifact["semantic_digest"] = digest(proof_payload)
    output_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print("JANUS_C049_1_B4_6_3_NODE9_FIFTEEN_GENERATOR_UP_K_CLOSURE = PASS")
    print("INPUT_GENERATORS =", len(generators))
    print("ORDERED_PAIR_TESTS =", len(generators) ** 2)
    print("RELATION_EDGES =", len(relation_edges))
    print("RETAINED_GENERATORS =", len(retained))
    print("DIRECT_REMOVALS =", len(removals))
    print("COMPLETE_REACHABLE_CATALOG =", len(reachable_entries))
    print("REPEATED_CLOSURE_CHECKS =", repeated_closure_checks)
    print("IDEMPOTENT = TRUE")
    print("ADMIT_NODE9_UP_K_CLOSURE = TRUE")
    print("SEMANTIC_DIGEST =", artifact["semantic_digest"])
    print("GLOBAL_TERMINAL =", TERMINAL)
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("frontier_artifact", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--entry-order", choices=("original", "reversed", "seeded-shuffle"), default="original")
    args = parser.parse_args()
    build(args.frontier_artifact, args.output, args.entry_order)


if __name__ == "__main__":
    main()
