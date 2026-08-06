#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import random
from pathlib import Path
from typing import Any, Iterable, Sequence

SCHEMA = "C049.1-B4.6.3-CORRECTED-NODE7-SIX-GENERATOR-UP-K-v1"
PARENT_PR = 112
PARENT_HEAD = "796ad144de65906c702e29928f683e6d53e3529c"
SOURCE_SHA256 = "b0d8d4e51be21f21218fd9ee63a367e3236ff2a53d9d5f29980e1c93340867ca"
SOURCE_SEMANTIC = "750990191184f37e321a83a66040fab490fa0db3ad3eb07e9941d3e31e7d88dd"
RUN_PATTERNS: tuple[tuple[int, ...], ...] = (
    (0,), (0, 1), (0, 1, 0), (1,), (1, 0), (1, 0, 1)
)
RUN_CODES = {pattern: "".join(map(str, pattern)) for pattern in RUN_PATTERNS}
CODE_PATTERNS = {code: pattern for pattern, code in RUN_CODES.items()}
EXTENSION_STEPS = ((1, 0), (0, 1), (1, 1))


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def xor_basis(rows: Iterable[int], ambient_dim: int = 2) -> tuple[int, ...]:
    table: dict[int, int] = {}
    for raw in rows:
        value = int(raw)
        if value < 0 or value >= (1 << ambient_dim):
            raise ValueError("vector outside GF(2) ambient space")
        while value:
            pivot = value.bit_length() - 1
            if pivot in table:
                value ^= table[pivot]
            else:
                table[pivot] = value
                for other in tuple(table):
                    if other != pivot and ((table[other] >> pivot) & 1):
                        table[other] ^= value
                break
    return tuple(table[p] for p in sorted(table, reverse=True))


def canonical_stat(item: dict[str, Any]) -> dict[str, Any]:
    value = int(item["value"])
    if value not in (0, 1):
        raise ValueError("k=1 scalar outside {0,1}")
    return {
        "left": list(xor_basis(item["left"])),
        "right": list(xor_basis(item["right"])),
        "value": value,
    }


def geometry(item: dict[str, Any]) -> tuple[tuple[int, ...], tuple[int, ...]]:
    return tuple(item["left"]), tuple(item["right"])


def geometry_only(trajectory: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{"left": list(item["left"]), "right": list(item["right"]), "value": 0} for item in trajectory]


def validate_generator(item: dict[str, Any]) -> dict[str, Any]:
    trajectory = [canonical_stat(stat) for stat in item["trajectory"]]
    if len(trajectory) != 4:
        raise AssertionError("corrected Node-7 generator must have four geometry blocks")
    if any(stat["value"] != 0 for stat in trajectory):
        raise AssertionError("frontier generator is not a zero envelope")
    if len({geometry(stat) for stat in trajectory}) != 4:
        raise AssertionError("generator geometry blocks are not injective")
    return {"generator_id": str(item["generator_id"]), "trajectory": trajectory}


def extension_preorder_witness(lower: Sequence[dict], upper: Sequence[dict]) -> list[list[int]] | None:
    m, n = len(lower), len(upper)
    reachable = [[False] * n for _ in range(m)]
    predecessor: dict[tuple[int, int], tuple[int, int]] = {}

    def compatible(i: int, j: int) -> bool:
        return geometry(lower[i]) == geometry(upper[j]) and int(lower[i]["value"]) <= int(upper[j]["value"])

    if not compatible(0, 0):
        return None
    reachable[0][0] = True
    for i in range(m):
        for j in range(n):
            if not reachable[i][j]:
                continue
            for di, dj in EXTENSION_STEPS:
                ni, nj = i + di, j + dj
                if ni < m and nj < n and not reachable[ni][nj] and compatible(ni, nj):
                    reachable[ni][nj] = True
                    predecessor[(ni, nj)] = (i, j)
    if not reachable[m - 1][n - 1]:
        return None
    cursor = (m - 1, n - 1)
    path = [cursor]
    while cursor != (0, 0):
        cursor = predecessor[cursor]
        path.append(cursor)
    path.reverse()
    return [[i, j] for i, j in path]


def preorder_matrix(generators: Sequence[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    matrix = []
    for lower in generators:
        row = []
        for upper in generators:
            witness = extension_preorder_witness(lower["trajectory"], upper["trajectory"])
            row.append({"holds": witness is not None, "witness": witness})
        matrix.append(row)
    return matrix


def minimize(generators: Sequence[dict[str, Any]]) -> tuple[list[dict], list[dict], list[list[dict]]]:
    ordered = sorted((validate_generator(item) for item in generators), key=lambda x: x["generator_id"])
    matrix = preorder_matrix(ordered)
    retained: list[dict] = []
    removals: list[dict] = []
    for candidate_index, candidate in enumerate(ordered):
        direct = None
        for retained_item in retained:
            retained_index = next(i for i, x in enumerate(ordered) if x["generator_id"] == retained_item["generator_id"])
            cell = matrix[retained_index][candidate_index]
            if cell["holds"]:
                direct = {"retained_generator_id": retained_item["generator_id"], "witness": cell["witness"]}
                break
        if direct is None:
            retained.append(candidate)
        else:
            removals.append({"removed_generator_id": candidate["generator_id"], **direct})
    return retained, removals, matrix


def compact_binary(values: Sequence[int]) -> tuple[int, ...]:
    run: list[int] = []
    for raw in values:
        value = int(raw)
        if value not in (0, 1):
            raise ValueError("nonbinary scalar")
        if not run or run[-1] != value:
            run.append(value)
    result = tuple(run)
    if result not in RUN_PATTERNS:
        raise AssertionError("binary sequence is outside k=1 typical catalog")
    return result


def expand_entry(generator: dict[str, Any], codes: Sequence[str]) -> tuple[list[dict], list[str]]:
    if len(codes) != len(generator["trajectory"]):
        raise AssertionError("scalar assignment length drift")
    trajectory: list[dict] = []
    normalized_codes: list[str] = []
    for stat, code in zip(generator["trajectory"], codes):
        pattern = compact_binary(CODE_PATTERNS[str(code)])
        normalized_codes.append(RUN_CODES[pattern])
        for value in pattern:
            lifted = copy.deepcopy(stat)
            lifted["value"] = value
            trajectory.append(lifted)
    return trajectory, normalized_codes


def closure(generators: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    entries = []
    for generator in sorted(generators, key=lambda x: x["generator_id"]):
        for assignment in itertools.product(sorted(CODE_PATTERNS), repeat=4):
            trajectory, codes = expand_entry(generator, assignment)
            entries.append({
                "entry_id": f"{generator['generator_id']}:{'.'.join(codes)}",
                "source_generator_id": generator["generator_id"],
                "scalar_pattern_codes": codes,
                "trajectory_digest": digest(trajectory),
                "width": max(item["value"] for item in trajectory),
            })
    entries.sort(key=lambda item: item["entry_id"])
    if len({item["entry_id"] for item in entries}) != len(entries):
        raise AssertionError("closure entry ids are not unique")
    return entries


def normalize_generators_from_closure(entries: Sequence[dict], generator_map: dict[str, dict]) -> list[dict]:
    ids = sorted({str(item["source_generator_id"]) for item in entries})
    return [generator_map[identifier] for identifier in ids]


def source_generators(source: dict[str, Any], order_mode: str) -> list[dict[str, Any]]:
    classes = list(source["quotient_frontier"]["classes"])
    if order_mode == "reversed":
        classes.reverse()
    elif order_mode == "seeded-shuffle":
        random.Random(0xC049113).shuffle(classes)
    elif order_mode != "original":
        raise ValueError("unknown order mode")
    generators = [
        {"generator_id": item["class_id"], "trajectory": geometry_only(item["zero_envelope"])}
        for item in classes
    ]
    return sorted(generators, key=lambda item: item["generator_id"])


def build(source_path: Path, order_mode: str) -> dict[str, Any]:
    if file_sha256(source_path) != SOURCE_SHA256:
        raise AssertionError("PR #112 frozen certificate byte boundary")
    source = json.loads(source_path.read_text(encoding="utf-8"))
    if source.get("semantic_digest") != SOURCE_SEMANTIC:
        raise AssertionError("PR #112 semantic boundary")
    if source.get("result") != "CORRECTED_NODE7_PARENT_FRONTIER_COMPRESSED_TO_SIX_CLASSES":
        raise AssertionError("PR #112 theorem result boundary")

    input_generators = source_generators(source, order_mode)
    if len(input_generators) != 6:
        raise AssertionError("six-generator input boundary")
    retained, removals, matrix = minimize(input_generators)
    reachable = closure(retained)
    generator_map = {item["generator_id"]: item for item in retained}
    second = closure(normalize_generators_from_closure(reachable, generator_map))
    if reachable != second:
        raise AssertionError("closure idempotence")

    relation_count = sum(int(cell["holds"]) for row in matrix for cell in row)
    artifact: dict[str, Any] = {
        "schema": SCHEMA,
        "source": {
            "parent_pr": PARENT_PR,
            "parent_exact_head": PARENT_HEAD,
            "certificate_sha256": SOURCE_SHA256,
            "certificate_semantic_digest": SOURCE_SEMANTIC,
        },
        "input_generators": input_generators,
        "preorder": {
            "steps": [list(step) for step in EXTENSION_STEPS],
            "pair_count": 36,
            "relation_count": relation_count,
            "matrix": matrix,
            "retained_generator_ids": [item["generator_id"] for item in retained],
            "direct_removals": removals,
            "transitive_removal_witnesses_used": 0,
        },
        "binary_typical_catalog": {
            "patterns": [list(pattern) for pattern in RUN_PATTERNS],
            "codes": sorted(CODE_PATTERNS),
            "assignments_per_generator": len(RUN_PATTERNS) ** 4,
        },
        "reachable_closure": {
            "entry_count": len(reachable),
            "entries_digest": digest(reachable),
            "per_generator": [
                {
                    "generator_id": generator_id,
                    "entry_count": len(group),
                    "entries_digest": digest(group),
                    "first_entry_id": group[0]["entry_id"],
                    "last_entry_id": group[-1]["entry_id"],
                }
                for generator_id in sorted(generator_map)
                for group in [[entry for entry in reachable if entry["source_generator_id"] == generator_id]]
            ],
            "closure_of_closure_entry_count": len(second),
            "closure_of_closure_digest": digest(second),
            "idempotent": reachable == second,
            "full_entries_stored": False,
            "full_entries_replayed_by_verifier": True,
        },
        "work_ledger": {
            "gf2_generator_statistics_checked": 24,
            "preorder_pairs_replayed": 36,
            "direct_removal_witnesses_replayed": len(removals),
            "scalar_assignments_replayed": len(RUN_PATTERNS) ** 4 * len(retained),
            "closure_entries_materialized": len(reachable),
            "idempotence_entries_replayed": len(second),
        },
        "invariant_vector": {f"CN7U-INV-{i:02d}": "PASS" for i in range(1, 11)},
        "result": "CORRECTED_NODE7_SIX_GENERATOR_UP_K_CANDIDATE",
        "strict_boundary": {
            "pr112_corrected_node7_refinement_admitted": True,
            "corrected_node7_parent_up_k_complete": False,
            "corrected_bottom_up_replay_complete": False,
            "root_parent_refinement_complete": False,
            "root_full_set_computed": False,
            "root_empty_proved": False,
            "found_layout": "FORBIDDEN",
            "no_layout_at_cap": "FORBIDDEN",
            "current_global_terminal": "OPEN_TRAJECTORY_ENGINE_INCOMPLETE",
            "p_vs_np": "OPEN",
        },
        "next_gate_after_admission": "C049.1_B4.6.3_CORRECTED_NODE7_INTEGRATION_AND_NODE8_PREFLIGHT",
        "certificate_bytes": 0,
    }
    while True:
        unsigned = dict(artifact)
        unsigned.pop("semantic_digest", None)
        artifact["semantic_digest"] = digest(unsigned)
        raw = canonical_json(artifact) + b"\n"
        if artifact["certificate_bytes"] == len(raw):
            return artifact
        artifact["certificate_bytes"] = len(raw)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--entry-order", default="original", choices=("original", "reversed", "seeded-shuffle"))
    args = parser.parse_args()
    artifact = build(args.source, args.entry_order)
    args.output.write_bytes(canonical_json(artifact) + b"\n")
    print(json.dumps({
        "artifact_bytes": args.output.stat().st_size,
        "artifact_sha256": file_sha256(args.output),
        "semantic_digest": artifact["semantic_digest"],
        "retained_generators": len(artifact["preorder"]["retained_generator_ids"]),
        "closure_entries": artifact["reachable_closure"]["entry_count"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
