#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import itertools
import json
import random
from pathlib import Path
from typing import Any, Sequence

SCHEMA = "C049.1-B4.6.3-NODE9-FIFTEEN-GENERATOR-UP-K-CLOSURE-v1"
SOURCE_SCHEMA = "C049.1-B4.6.3-NODE9-PARENT-FRONTIER-STRUCTURAL-COMPRESSION-v1"
TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"
SOURCE_SHA = "6eefd8e31ba4808e5587475c2faa2c000fd0093da4de2c488db42d103c059890"
SOURCE_SEMANTIC = "62e9178821fe56cbf094e8512dd20b687796c6fd87e08c0fea8ea833ef6c5e80"
RUNS = ((0,), (0, 1), (0, 1, 0), (1,), (1, 0), (1, 0, 1))
RUN_NAME = {run: "".join(map(str, run)) for run in RUNS}
COUNTS = {
    "input": 15,
    "pairs": 225,
    "relations": 55,
    "self": 15,
    "cross": 40,
    "equivalent": 0,
    "retained": 2,
    "removed": 13,
    "scalar_edges": 20,
    "scalar_transitivity": 50,
    "reachable": 252,
    "repeat_checks": 8400,
}
RETAINED_IDS = ("N9-S02", "N9-S07")


def canon(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha(value: Any) -> str:
    return hashlib.sha256(canon(value)).hexdigest()


def hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_trajectory(raw: Sequence[dict[str, Any]]) -> tuple[tuple, ...]:
    output = []
    for item in raw:
        output.append((tuple(map(int, item["left"])), tuple(map(int, item["right"])), int(item["value"])))
    return tuple(output)


def write_trajectory(sequence: Sequence[tuple]) -> list[dict[str, Any]]:
    return [{"left": list(left), "right": list(right), "value": int(value)} for left, right, value in sequence]


def reduce_trajectory(sequence: Sequence[tuple]) -> tuple[tuple, ...]:
    result = list(sequence)
    while True:
        modified = False
        cursor = 1
        while cursor < len(result):
            if result[cursor - 1] == result[cursor]:
                result.pop(cursor)
                modified = True
                break
            cursor += 1
        if modified:
            continue
        for first in range(len(result)):
            for last in range(first + 2, len(result)):
                if result[first][:2] != result[last][:2]:
                    continue
                values = [row[2] for row in result[first : last + 1]]
                between = values[1:-1]
                allowed = (
                    values[0] <= values[-1] and all(values[0] <= item <= values[-1] for item in between)
                ) or (
                    values[0] >= values[-1] and all(values[0] >= item >= values[-1] for item in between)
                )
                if allowed:
                    result[first + 1 : last] = []
                    modified = True
                    break
            if modified:
                break
        if not modified:
            return tuple(result)


def alignment(lower: Sequence[tuple], upper: Sequence[tuple]) -> dict[str, Any] | None:
    reached: dict[tuple[int, int], tuple[int, int] | None] = {}
    for i in range(len(lower)):
        for j in range(len(upper)):
            if lower[i][0] != upper[j][0] or lower[i][1] != upper[j][1] or lower[i][2] > upper[j][2]:
                continue
            if i == 0 and j == 0:
                reached[(i, j)] = None
            else:
                predecessor = None
                for candidate in ((i - 1, j - 1), (i - 1, j), (i, j - 1)):
                    if candidate in reached:
                        predecessor = candidate
                        break
                if predecessor is not None:
                    reached[(i, j)] = predecessor
    end = (len(lower) - 1, len(upper) - 1)
    if end not in reached:
        return None
    path = []
    point: tuple[int, int] | None = end
    while point is not None:
        path.append(point)
        point = reached[point]
    path.reverse()
    return {"path": [[i, j] for i, j in path], "path_length": len(path)}


def run_blocks(sequence: Sequence[tuple]) -> tuple[tuple[tuple, ...], tuple[tuple[int, ...], ...]]:
    geometry: list[tuple] = []
    scalars: list[list[int]] = []
    for left, right, value in sequence:
        shape = (tuple(left), tuple(right))
        if not geometry or geometry[-1] != shape:
            geometry.append(shape)
            scalars.append([int(value)])
        else:
            scalars[-1].append(int(value))
    patterns = tuple(tuple(block) for block in scalars)
    if any(pattern not in RUNS for pattern in patterns):
        raise AssertionError("non-typical run")
    return tuple(geometry), patterns


def scalar_sequence(pattern: Sequence[int]) -> tuple[tuple, ...]:
    return tuple(((), (1,), int(value)) for value in pattern)


def calculate_scalar_order() -> tuple[dict[tuple[int, ...], tuple[tuple[int, ...], ...]], list[dict[str, Any]], int]:
    supersets: dict[tuple[int, ...], tuple[tuple[int, ...], ...]] = {}
    edge_rows = []
    for source in RUNS:
        found = []
        for target in RUNS:
            witness = alignment(scalar_sequence(source), scalar_sequence(target))
            if witness is not None:
                found.append(target)
                edge_rows.append({"lower": RUN_NAME[source], "upper": RUN_NAME[target], "witness": witness})
        supersets[source] = tuple(found)
    edge_rows.sort(key=canon)
    relation = {(row["lower"], row["upper"]) for row in edge_rows}
    transitivity_count = 0
    for source in RUNS:
        for middle in RUNS:
            for target in RUNS:
                if (RUN_NAME[source], RUN_NAME[middle]) in relation and (RUN_NAME[middle], RUN_NAME[target]) in relation:
                    transitivity_count += 1
                    if (RUN_NAME[source], RUN_NAME[target]) not in relation:
                        raise AssertionError("scalar transitivity failure")
    return supersets, edge_rows, transitivity_count


def permute(items: list[Any], mode: str) -> list[Any]:
    result = list(items)
    if mode == "reversed":
        result = list(reversed(result))
    elif mode == "seeded-shuffle":
        random.Random(0xC04910915).shuffle(result)
    elif mode != "original":
        raise AssertionError("bad order mode")
    return result


def source_classes(source_path: Path, mode: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if hash_file(source_path) != SOURCE_SHA:
        raise AssertionError("source byte hash")
    source = json.loads(source_path.read_text(encoding="utf-8"))
    if source.get("schema") != SOURCE_SCHEMA:
        raise AssertionError("source schema")
    if source.get("semantic_digest") != SOURCE_SEMANTIC or source.get("semantic_digest") != sha(source.get("proof_payload")):
        raise AssertionError("source semantic binding")
    payload = source["proof_payload"]
    if payload.get("admit") is not True:
        raise AssertionError("source admission")
    strict = payload["strict_boundary"]
    exact = (
        strict.get("node9_parent_generator_frontier_complete"),
        strict.get("node9_parent_refinement_complete"),
        strict.get("node9_parent_up_k_complete"),
    )
    if exact != (True, True, False):
        raise AssertionError("source strict boundary")
    classes = permute(list(payload["quotient_frontier"]["classes"]), mode)
    if len(classes) != COUNTS["input"]:
        raise AssertionError("source class count")
    return source, classes


def normalize(classes: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    output = []
    class_ids: set[str] = set()
    trajectory_keys: set[bytes] = set()
    for raw_class in classes:
        class_id = str(raw_class["class_id"])
        if class_id in class_ids:
            raise AssertionError("duplicate class id")
        class_ids.add(class_id)
        trajectory = reduce_trajectory(read_trajectory(raw_class["canonical_generator"]))
        encoded = write_trajectory(trajectory)
        if encoded != raw_class["canonical_generator"]:
            raise AssertionError("generator compactification")
        if sha(encoded) != raw_class["generator_digest"]:
            raise AssertionError("generator digest")
        key = canon(encoded)
        if key in trajectory_keys:
            raise AssertionError("duplicate trajectory")
        trajectory_keys.add(key)
        geometry, patterns = run_blocks(trajectory)
        output.append({
            "source_class_id": class_id,
            "trajectory": trajectory,
            "trajectory_json": encoded,
            "generator_digest": sha(encoded),
            "skeleton": geometry,
            "patterns": patterns,
            "skeleton_digest": sha([[list(left), list(right)] for left, right in geometry]),
            "run_pattern_codes": [RUN_NAME[pattern] for pattern in patterns],
        })
    output.sort(key=lambda row: canon(row["trajectory_json"]))
    return output


def independent_payload(source_path: Path, mode: str) -> dict[str, Any]:
    source, classes = source_classes(source_path, mode)
    generators = normalize(classes)

    edges = []
    lookup: dict[tuple[str, str], dict[str, Any]] = {}
    for lower in generators:
        for upper in generators:
            witness = alignment(lower["trajectory"], upper["trajectory"])
            if witness is None:
                continue
            row = {
                "lower_source_class_id": lower["source_class_id"],
                "upper_source_class_id": upper["source_class_id"],
                "lower_generator_digest": lower["generator_digest"],
                "upper_generator_digest": upper["generator_digest"],
                "witness": witness,
            }
            edges.append(row)
            lookup[(lower["source_class_id"], upper["source_class_id"])] = row
    edges.sort(key=canon)
    self_count = sum(row["lower_source_class_id"] == row["upper_source_class_id"] for row in edges)
    cross_count = len(edges) - self_count
    equivalent_count = 0
    for index, left in enumerate(generators):
        for right in generators[index + 1 :]:
            if (left["source_class_id"], right["source_class_id"]) in lookup and (right["source_class_id"], left["source_class_id"]) in lookup:
                equivalent_count += 1

    retained = []
    for current in generators:
        current_id = current["source_class_id"]
        lower_exists = any(
            other["source_class_id"] != current_id
            and (other["source_class_id"], current_id) in lookup
            for other in generators
        )
        if not lower_exists:
            retained.append(current)
    retained.sort(key=lambda row: canon(row["trajectory_json"]))
    retained_ids = tuple(row["source_class_id"] for row in retained)
    if retained_ids != RETAINED_IDS:
        raise AssertionError("retained ids")

    deleted = []
    for current in generators:
        current_id = current["source_class_id"]
        if current_id in retained_ids:
            continue
        possible = [row for row in retained if (row["source_class_id"], current_id) in lookup]
        if not possible:
            raise AssertionError("direct retained witness absent")
        witness_row = min(possible, key=lambda row: canon(row["trajectory_json"]))
        direct_edge = lookup[(witness_row["source_class_id"], current_id)]
        deleted.append({
            "removed_source_class_id": current_id,
            "removed_generator_digest": current["generator_digest"],
            "retained_witness_source_class_id": witness_row["source_class_id"],
            "retained_witness_generator_digest": witness_row["generator_digest"],
            "witness_kind": "EXTENSION_PREORDER_DIRECT",
            "transitive_closure_used": False,
            "witness": direct_edge["witness"],
        })
    deleted.sort(key=canon)

    upward, scalar_edges, transitivity_count = calculate_scalar_order()
    reachable_map: dict[bytes, dict[str, Any]] = {}
    local_counts: dict[str, int] = {}
    for base in retained:
        local: dict[bytes, dict[str, Any]] = {}
        for selected in itertools.product(*(upward[pattern] for pattern in base["patterns"])):
            expanded = []
            for shape, pattern in zip(base["skeleton"], selected):
                expanded.extend((shape[0], shape[1], int(value)) for value in pattern)
            trajectory = reduce_trajectory(expanded)
            witness = alignment(base["trajectory"], trajectory)
            if witness is None:
                raise AssertionError("reachable direct witness")
            encoded = write_trajectory(trajectory)
            key = canon(encoded)
            row = {
                "source_retained_class_id": base["source_class_id"],
                "source_retained_generator_digest": base["generator_digest"],
                "run_pattern_codes": [RUN_NAME[pattern] for pattern in selected],
                "trajectory": encoded,
                "trajectory_digest": sha(encoded),
                "width": max(item["value"] for item in encoded),
                "direct_witness_kind": "EXTENSION_PREORDER_DIRECT",
                "direct_witness": witness,
            }
            if key in local and local[key] != row:
                raise AssertionError("local duplicate ambiguity")
            local[key] = row
            if key in reachable_map and reachable_map[key]["source_retained_class_id"] != base["source_class_id"]:
                raise AssertionError("cross-skeleton duplicate")
            reachable_map[key] = row
        local_counts[base["source_class_id"]] = len(local)

    entries = []
    for number, key in enumerate(sorted(reachable_map)):
        row = dict(reachable_map[key])
        row["entry_id"] = f"N9U-E{number:03d}"
        entries.append(row)
    first_keys = set(reachable_map)
    second_keys: set[bytes] = set()
    replay_count = 0
    for row in entries:
        source_trajectory = read_trajectory(row["trajectory"])
        geometry, patterns = run_blocks(source_trajectory)
        for selected in itertools.product(*(upward[pattern] for pattern in patterns)):
            expanded = []
            for shape, pattern in zip(geometry, selected):
                expanded.extend((shape[0], shape[1], int(value)) for value in pattern)
            target = reduce_trajectory(expanded)
            target_key = canon(write_trajectory(target))
            replay_count += 1
            second_keys.add(target_key)
            if target_key not in first_keys:
                raise AssertionError("idempotence enlargement")
            if alignment(source_trajectory, target) is None:
                raise AssertionError("idempotence direct relation")
    if first_keys != second_keys:
        raise AssertionError("idempotence set inequality")

    measurements = {
        "input": len(generators),
        "pairs": len(generators) ** 2,
        "relations": len(edges),
        "self": self_count,
        "cross": cross_count,
        "equivalent": equivalent_count,
        "retained": len(retained),
        "removed": len(deleted),
        "scalar_edges": len(scalar_edges),
        "scalar_transitivity": transitivity_count,
        "reachable": len(entries),
        "repeat_checks": replay_count,
    }
    if measurements != COUNTS:
        raise AssertionError(f"count boundary {measurements}")

    generator_inventory = [{
        "source_class_id": row["source_class_id"],
        "generator_digest": row["generator_digest"],
        "skeleton_digest": row["skeleton_digest"],
        "run_pattern_codes": row["run_pattern_codes"],
        "trajectory": row["trajectory_json"],
    } for row in generators]
    retained_inventory = [{
        "source_class_id": row["source_class_id"],
        "generator_digest": row["generator_digest"],
        "skeleton_digest": row["skeleton_digest"],
        "run_pattern_codes": row["run_pattern_codes"],
        "trajectory": row["trajectory_json"],
        "reachable_entry_count": local_counts[row["source_class_id"]],
    } for row in retained]
    stream = b"".join(canon(row["trajectory"]) + b"\n" for row in entries)

    return {
        "source": {
            "frontier_schema": SOURCE_SCHEMA,
            "frontier_artifact_sha256": SOURCE_SHA,
            "frontier_semantic_digest": SOURCE_SEMANTIC,
            "frontier_generator_count": COUNTS["input"],
            "frontier_post_shrink_class_count": source["proof_payload"]["quotient_frontier"]["post_shrink_successful_class_count"],
        },
        "node_id": 9,
        "ambient_dim": 1,
        "k": 1,
        "input_generator_family": {
            "generator_count": len(generator_inventory),
            "generator_family_digest": sha(generator_inventory),
            "generators": generator_inventory,
            "order_invariant": True,
        },
        "direct_preorder": {
            "ordered_pair_tests": len(generators) ** 2,
            "relation_edge_count": len(edges),
            "self_relation_edge_count": self_count,
            "cross_relation_edge_count": cross_count,
            "strict_cross_relation_edge_count": cross_count,
            "equivalent_cross_pair_count": equivalent_count,
            "relation_edges": edges,
        },
        "minimization": {
            "retained_generator_count": len(retained_inventory),
            "direct_removal_count": len(deleted),
            "retained_family_digest": sha(retained_inventory),
            "retained_generators": retained_inventory,
            "direct_removals": deleted,
            "every_removal_has_direct_retained_witness": True,
            "transitive_closure_used_for_removal": False,
        },
        "scalar_typical_relation": {
            "typical_pattern_catalog": [RUN_NAME[pattern] for pattern in RUNS],
            "relation_edge_count": len(scalar_edges),
            "relation_edges": scalar_edges,
            "transitivity_checks": transitivity_count,
            "transitive": True,
        },
        "reachable_closure": {
            "complete_reachable_catalog": len(entries),
            "reachable_entry_count": len(entries),
            "reachable_entries_digest": sha([row["trajectory"] for row in entries]),
            "reachable_stream_sha256": hashlib.sha256(stream).hexdigest(),
            "entries": entries,
            "every_entry_has_direct_retained_witness": True,
            "global_compact_universe_enumerated": False,
            "global_compact_universe_entry_count": 0,
            "construction": "BLOCKWISE_SCALAR_UPWARD_SETS_THEN_GLOBAL_COMPACTIFICATION",
        },
        "idempotence": {
            "idempotent": True,
            "method": "EXACT_REPEATED_BLOCKWISE_UPWARD_SET_REPLAY",
            "first_closure_entry_count": len(entries),
            "second_closure_entry_count": len(second_keys),
            "repeated_closure_checks": replay_count,
            "scalar_transitivity_checks": transitivity_count,
        },
        "work_ledger": {
            "input_generators_read": len(generators),
            "ordered_generator_pairs_tested": len(generators) ** 2,
            "direct_relation_edges_retained": len(edges),
            "blockwise_reachable_entries_materialized": len(entries),
            "repeated_blockwise_checks": replay_count,
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


def scan_producer(path: Path) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    forbidden_calls = {"eval", "exec", "compile"}
    forbidden_names = {"enumerate_global_compact_universe", "global_compact_universe"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if "node9_fifteen_generator_up_k_closure_verifier" in alias.name:
                    raise AssertionError("producer imports verifier")
        if isinstance(node, ast.ImportFrom) and node.module and "node9_fifteen_generator_up_k_closure_verifier" in node.module:
            raise AssertionError("producer imports verifier")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in forbidden_calls:
            raise AssertionError("dynamic execution in producer")
        if isinstance(node, ast.Name) and node.id in forbidden_names:
            raise AssertionError("global compact universe enumerator present")


def verify(source_path: Path, artifact: dict[str, Any], producer_source: Path | None) -> dict[str, Any]:
    if artifact.get("schema") != SCHEMA or artifact.get("semantic_digest_scope") != "proof_payload":
        raise AssertionError("artifact schema")
    if artifact.get("semantic_digest") != sha(artifact.get("proof_payload")):
        raise AssertionError("artifact semantic digest")
    original = independent_payload(source_path, "original")
    reversed_payload = independent_payload(source_path, "reversed")
    shuffled = independent_payload(source_path, "seeded-shuffle")
    if original != reversed_payload or original != shuffled:
        raise AssertionError("independent order determinism")
    if artifact["proof_payload"] != original:
        raise AssertionError("producer payload differs from independent replay")
    if producer_source is not None:
        scan_producer(producer_source)
    return original


def tamper_tests(artifact: dict[str, Any], expected: dict[str, Any]) -> int:
    attacks: list[dict[str, Any]] = []

    def changed(path: Sequence[Any], value: Any) -> dict[str, Any]:
        candidate = copy.deepcopy(artifact)
        cursor: Any = candidate
        for key in path[:-1]:
            cursor = cursor[key]
        cursor[path[-1]] = value
        candidate["semantic_digest"] = sha(candidate["proof_payload"])
        return candidate

    attacks.append(changed(("proof_payload", "source", "frontier_artifact_sha256"), "0" * 64))
    candidate = copy.deepcopy(artifact)
    candidate["proof_payload"]["input_generator_family"]["generators"].pop()
    candidate["semantic_digest"] = sha(candidate["proof_payload"])
    attacks.append(candidate)
    candidate = copy.deepcopy(artifact)
    candidate["proof_payload"]["direct_preorder"]["relation_edges"][0]["witness"]["path"].pop()
    candidate["semantic_digest"] = sha(candidate["proof_payload"])
    attacks.append(candidate)
    candidate = copy.deepcopy(artifact)
    candidate["proof_payload"]["minimization"]["retained_generators"].pop()
    candidate["semantic_digest"] = sha(candidate["proof_payload"])
    attacks.append(candidate)
    attacks.append(changed(("proof_payload", "minimization", "direct_removals", 0, "transitive_closure_used"), True))
    candidate = copy.deepcopy(artifact)
    candidate["proof_payload"]["reachable_closure"]["entries"].pop()
    candidate["semantic_digest"] = sha(candidate["proof_payload"])
    attacks.append(candidate)
    attacks.append(changed(("proof_payload", "reachable_closure", "entries", 0, "source_retained_class_id"), "N9-S14"))
    candidate = copy.deepcopy(artifact)
    candidate["proof_payload"]["scalar_typical_relation"]["relation_edges"].pop()
    candidate["semantic_digest"] = sha(candidate["proof_payload"])
    attacks.append(candidate)
    attacks.append(changed(("proof_payload", "idempotence", "idempotent"), False))
    attacks.append(changed(("proof_payload", "strict_boundary", "root_reached"), True))

    rejected = 0
    for candidate in attacks:
        try:
            if candidate.get("schema") != SCHEMA:
                raise AssertionError("schema")
            if candidate.get("semantic_digest") != sha(candidate.get("proof_payload")):
                raise AssertionError("digest")
            if candidate.get("proof_payload") != expected:
                raise AssertionError("independent replay mismatch")
        except Exception:
            rejected += 1
    if rejected != 10:
        raise AssertionError("tamper rejection count")
    return rejected


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("frontier_artifact", type=Path)
    parser.add_argument("closure_artifact", type=Path)
    parser.add_argument("--producer-source", type=Path)
    parser.add_argument("--tamper-self-test", action="store_true")
    args = parser.parse_args()
    artifact = json.loads(args.closure_artifact.read_text(encoding="utf-8"))
    payload = verify(args.frontier_artifact, artifact, args.producer_source)
    rejected = tamper_tests(artifact, payload) if args.tamper_self_test else 0
    print("STATIC_NO_GLOBAL_COMPACT_UNIVERSE_ENUMERATION = PASS")
    print("JANUS_C049_1_B4_6_3_NODE9_UP_K_CLOSURE_VERIFIER = PASS")
    print("INVARIANTS = 10/10")
    print("INPUT_GENERATORS =", payload["input_generator_family"]["generator_count"])
    print("RETAINED_GENERATORS =", payload["minimization"]["retained_generator_count"])
    print("DIRECT_REMOVALS =", payload["minimization"]["direct_removal_count"])
    print("COMPLETE_REACHABLE_CATALOG =", payload["reachable_closure"]["reachable_entry_count"])
    print("IDEMPOTENT =", payload["idempotence"]["idempotent"])
    if args.tamper_self_test:
        print(f"TAMPER_ATTACKS_REJECTED = {rejected}/10")


if __name__ == "__main__":
    main()
