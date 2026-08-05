#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from janus_c049_1_b3_expand_join_shrink_core import (
    Statistic,
    encode_trajectory,
    join_trajectory as legacy_join_trajectory,
    shrink_trajectory,
)
from janus_c049_1_b3_join_path_domain_corrected import (
    EXTENSION_PREORDER_STEPS,
    JOIN_INTERLEAVING_STEPS,
    extension_preorder_witness,
    join_trajectory,
    ordinary_join_paths,
    validate_ordinary_join_path,
)

SCHEMA = "C049.1-B4.6.3-JOIN-PATH-DOMAIN-CORRECTION-v1"
OBSTRUCTION_SHA256 = "bef0e67cb70c59d4b2f5b3b2a235416fe4121e9f4d1109600355d06cef42996c"
OBSTRUCTION_SEMANTIC = "44a6c9dadf2f0815f8f5d2be85bae2a23e8a5550cfb525f49adcf46061ef8980"


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def delannoy(a: int, b: int) -> int:
    return sum(math.comb(a, k) * math.comb(b, k) * 2**k for k in range(min(a, b) + 1))


def scalar_sequence(gamma) -> list[int]:
    return [int(stat.value) for stat in gamma]


def build(obstruction_path: Path, corrected_source: Path) -> dict[str, Any]:
    if file_sha256(obstruction_path) != OBSTRUCTION_SHA256:
        raise AssertionError("obstruction byte boundary")
    obstruction = json.loads(obstruction_path.read_text(encoding="utf-8"))
    if obstruction.get("semantic_digest") != OBSTRUCTION_SEMANTIC:
        raise AssertionError("obstruction semantic boundary")
    if digest(obstruction["proof_payload"]) != OBSTRUCTION_SEMANTIC:
        raise AssertionError("obstruction payload digest")
    decisive = obstruction["proof_payload"]["decisive_obstruction"]
    if decisive["root_acceptance_reflection_contradiction"] is not True:
        raise AssertionError("missing admitted contradiction")

    grid = []
    ordinary_total = 0
    diagonal_total = 0
    for m in range(1, 7):
        for n in range(1, 7):
            paths = tuple(ordinary_join_paths(m, n))
            ordinary_expected = math.comb(m + n - 2, m - 1)
            diagonal_expected = delannoy(m - 1, n - 1)
            if len(paths) != ordinary_expected:
                raise AssertionError("ordinary interleaving count")
            for path in paths:
                if validate_ordinary_join_path(path, m, n) != path:
                    raise AssertionError("ordinary path replay")
                if any((b[0] - a[0], b[1] - a[1]) not in JOIN_INTERLEAVING_STEPS for a, b in zip(path, path[1:])):
                    raise AssertionError("diagonal leaked into ordinary join")
            ordinary_total += ordinary_expected
            diagonal_total += diagonal_expected
            grid.append({
                "m": m,
                "n": n,
                "ordinary_interleavings": ordinary_expected,
                "diagonal_inclusive_paths": diagonal_expected,
                "removed_diagonal_domain_paths": diagonal_expected - ordinary_expected,
            })
    if (ordinary_total, diagonal_total) != (923, 4494):
        raise AssertionError("grid totals")

    start = Statistic((), (1,), 0)
    finish = Statistic((1,), (), 0)
    left = (start, finish)
    right = (start, finish)
    ordinary_paths = tuple(ordinary_join_paths(2, 2))
    if ordinary_paths != (
        ((0, 0), (1, 0), (1, 1)),
        ((0, 0), (0, 1), (1, 1)),
    ):
        raise AssertionError("2x2 ordinary paths")

    ordinary_outputs = []
    for path in ordinary_paths:
        joined, join_receipt = join_trajectory(left, right, path, (1,), 1)
        shrunk, shrink_receipt = shrink_trajectory(joined, (), 1)
        ordinary_outputs.append({
            "path": [list(point) for point in path],
            "joined": encode_trajectory(joined),
            "root_output": scalar_sequence(shrunk),
            "join_receipt_digest": digest(join_receipt),
            "shrink_receipt_digest": digest(shrink_receipt),
        })
    if [item["root_output"] for item in ordinary_outputs] != [[0, 1, 0], [0, 1, 0]]:
        raise AssertionError("ordinary root witness outputs")

    diagonal = ((0, 0), (1, 1))
    try:
        validate_ordinary_join_path(diagonal, 2, 2)
    except ValueError:
        diagonal_rejected = True
    else:
        diagonal_rejected = False
    if not diagonal_rejected:
        raise AssertionError("diagonal accepted by corrected validator")

    legacy_joined, _ = legacy_join_trajectory(left, right, diagonal, (1,), 1)
    legacy_root, _ = shrink_trajectory(legacy_joined, (), 1)
    if scalar_sequence(legacy_root) != [0]:
        raise AssertionError("legacy false zero drift")

    witness = extension_preorder_witness(left, left)
    if witness is None or witness["path"] != [[0, 0], [1, 1]]:
        raise AssertionError("extension preorder diagonal lost")

    proof_payload: dict[str, Any] = {
        "source": {
            "admitted_obstruction_sha256": OBSTRUCTION_SHA256,
            "admitted_obstruction_semantic_digest": OBSTRUCTION_SEMANTIC,
            "corrected_module_sha256": file_sha256(corrected_source),
        },
        "path_domain_split": {
            "join_interleaving_steps": [list(step) for step in JOIN_INTERLEAVING_STEPS],
            "extension_preorder_steps": [list(step) for step in EXTENSION_PREORDER_STEPS],
            "domains_are_distinct": JOIN_INTERLEAVING_STEPS != EXTENSION_PREORDER_STEPS,
        },
        "bounded_exhaustive_grid": {
            "m_range": [1, 6],
            "n_range": [1, 6],
            "cases": grid,
            "ordinary_interleavings": ordinary_total,
            "diagonal_inclusive_paths": diagonal_total,
            "removed_diagonal_domain_paths": diagonal_total - ordinary_total,
        },
        "false_zero_witness_correction": {
            "children": encode_trajectory(left),
            "illegal_diagonal_path": [list(point) for point in diagonal],
            "legacy_diagonal_root_output": scalar_sequence(legacy_root),
            "corrected_validator_rejects_diagonal": diagonal_rejected,
            "ordinary_join_paths": ordinary_outputs,
            "corrected_zero_root_outputs": 0,
        },
        "extension_preorder_preservation": {
            "witness": witness,
            "diagonal_step_preserved": witness["path"] == [[0, 0], [1, 1]],
        },
        "invariant_vector": {f"JPDC-INV-{i:02d}": "PASS" for i in range(1, 11)},
        "admit_join_path_domain_correction": True,
        "strict_boundary": {
            "b3_join_path_domain_corrected_api": True,
            "legacy_b3_join_artifacts_promotable": False,
            "corrected_bottom_up_replay_complete": False,
            "root_structural_compression_admitted": False,
            "root_parent_refinement_complete": False,
            "root_parent_up_k_complete": False,
            "root_full_set_computed": False,
            "root_empty_proved": False,
            "found_layout": "FORBIDDEN",
            "no_layout_at_cap": "FORBIDDEN",
            "current_global_terminal": "OPEN_TRAJECTORY_ENGINE_INCOMPLETE",
            "next_gate": "C049.1_B4.6.3_CORRECTED_REPLAY_FROM_FIRST_INTERNAL_JOIN",
            "p_vs_np": "OPEN",
        },
        "certificate_bytes": 0,
    }
    while True:
        outer = {
            "schema": SCHEMA,
            "semantic_digest_scope": "proof_payload",
            "proof_payload": proof_payload,
            "semantic_digest": digest(proof_payload),
        }
        raw = canonical_json(outer) + b"\n"
        if proof_payload["certificate_bytes"] == len(raw):
            return outer
        proof_payload["certificate_bytes"] = len(raw)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("obstruction", type=Path)
    parser.add_argument("corrected_source", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    artifact = build(args.obstruction, args.corrected_source)
    args.output.write_bytes(canonical_json(artifact) + b"\n")
    print(json.dumps({
        "artifact_bytes": args.output.stat().st_size,
        "artifact_sha256": file_sha256(args.output),
        "semantic_digest": artifact["semantic_digest"],
        "ordinary_interleavings": artifact["proof_payload"]["bounded_exhaustive_grid"]["ordinary_interleavings"],
        "diagonal_inclusive_paths": artifact["proof_payload"]["bounded_exhaustive_grid"]["diagonal_inclusive_paths"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
