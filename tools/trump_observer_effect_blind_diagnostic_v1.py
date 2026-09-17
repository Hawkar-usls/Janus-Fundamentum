#!/usr/bin/env python3
"""TRUMP observer-effect / information-leakage diagnostic v1.

DIAGNOSTIC ONLY. NO SOLVER OR CARRIER AUTHORITY.

The harness checks an experimental-design invariant: a structural candidate should not
change merely because a semantics-preserving representation changes. It also verifies
that target-aware metadata is removed before the discovery callback sees a sample.

Current --self-test uses synthetic calibration fixtures only. This is deliberate:
v3.23 forbids treating the exhausted connected-mixed corpus as new evidence.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import random
from dataclasses import dataclass
from typing import Any, Callable

FORBIDDEN_METADATA = {
    "source_path",
    "constructor_name",
    "fixture_name",
    "historical_verdict",
    "expected_mechanism_label",
    "previous_solver_status",
    "human_target_description",
    "branch_name",
    "commit_name",
}


class DiagnosticError(RuntimeError):
    pass


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_obj(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()


def blind_mask(sample: dict[str, Any]) -> dict[str, Any]:
    """Return only opaque id + raw semantics; reject nested obvious target metadata."""
    masked = {
        "sample_id": sample["sample_id"],
        "raw": copy.deepcopy(sample["raw"]),
    }
    text = canonical_json(masked)
    for field in FORBIDDEN_METADATA:
        if f'"{field}"' in text:
            raise DiagnosticError(f"forbidden metadata leaked into blind view: {field}")
    return masked


@dataclass(frozen=True)
class TransformReceipt:
    seed: int
    forward: dict[str, str]
    inverse: dict[str, str]


def variable_rename_view(masked: dict[str, Any], seed: int) -> tuple[dict[str, Any], TransformReceipt]:
    """Rename variables and shuffle constraint/member order for a simple finite relation object.

    Expected raw schema for calibration:
      {"variables": [...], "relations": [{"scope": [...], "allowed": [[...], ...]}, ...]}

    The transform is semantics-preserving because only variable names and ordering of
    conjunction terms / allowed tuples are changed.
    """
    rng = random.Random(seed)
    raw = copy.deepcopy(masked["raw"])
    variables = list(raw["variables"])
    shuffled_names = [f"v{n:04d}" for n in range(len(variables))]
    rng.shuffle(shuffled_names)
    forward = dict(zip(variables, shuffled_names))
    inverse = {v: k for k, v in forward.items()}

    relations = []
    for rel in raw["relations"]:
        nr = copy.deepcopy(rel)
        nr["scope"] = [forward[v] for v in rel["scope"]]
        allowed = list(nr.get("allowed", []))
        rng.shuffle(allowed)
        nr["allowed"] = allowed
        relations.append(nr)
    rng.shuffle(relations)

    view = {
        "sample_id": masked["sample_id"],
        "raw": {"variables": [forward[v] for v in variables], "relations": relations},
    }
    return view, TransformReceipt(seed=seed, forward=forward, inverse=inverse)


def discover_degree_partition(blind_view: dict[str, Any]) -> dict[str, Any]:
    """Calibration discovery callback with no provenance access.

    It discovers the partition of variables by relation-incidence degree. This is not a
    solver; it is a deliberately simple representation-invariant structural candidate.
    """
    raw = blind_view["raw"]
    deg = {v: 0 for v in raw["variables"]}
    for rel in raw["relations"]:
        for v in rel["scope"]:
            deg[v] += 1
    cells: dict[int, list[str]] = {}
    for v, d in deg.items():
        cells.setdefault(d, []).append(v)
    return {
        "candidate_type": "VARIABLE_PARTITION_BY_RELATION_INCIDENCE_DEGREE",
        "cells": [sorted(vs) for _, vs in sorted(cells.items())],
    }


def inverse_map_candidate(candidate: dict[str, Any], receipt: TransformReceipt) -> dict[str, Any]:
    out = copy.deepcopy(candidate)
    out["cells"] = sorted(
        [sorted(receipt.inverse[v] for v in cell) for cell in candidate["cells"]],
        key=lambda cell: (len(cell), cell),
    )
    return out


def canonical_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(candidate)
    out["cells"] = sorted([sorted(cell) for cell in out["cells"]], key=lambda c: (len(c), c))
    return out


def run_views(
    sample: dict[str, Any],
    seeds: list[int],
    discover: Callable[[dict[str, Any]], dict[str, Any]],
) -> dict[str, Any]:
    masked = blind_mask(sample)
    raw_sha = sha256_obj(masked["raw"])
    candidates = []
    hashes = []
    for seed in seeds:
        view, receipt = variable_rename_view(masked, seed)
        found = discover(view)
        canonical = canonical_candidate(inverse_map_candidate(found, receipt))
        candidates.append(canonical)
        hashes.append(sha256_obj(canonical))
    modal = max(set(hashes), key=hashes.count)
    coherence = hashes.count(modal) / len(hashes)
    return {
        "raw_semantic_sha256": raw_sha,
        "transform_seeds": seeds,
        "candidate_hashes": hashes,
        "representation_coherence": coherence,
        "all_candidates_equal": len(set(hashes)) == 1,
        "candidate": candidates[0] if candidates else None,
    }


def synthetic_fixture() -> dict[str, Any]:
    return {
        "sample_id": "opaque-calibration-001",
        "source_path": "MUST_NOT_BE_VISIBLE",
        "constructor_name": "MUST_NOT_BE_VISIBLE",
        "historical_verdict": "MUST_NOT_BE_VISIBLE",
        "expected_mechanism_label": "MUST_NOT_BE_VISIBLE",
        "raw": {
            "variables": ["a", "b", "c", "d", "e"],
            "relations": [
                {"scope": ["a", "b"], "allowed": [[0, 0], [1, 1]]},
                {"scope": ["a", "c"], "allowed": [[0, 1], [1, 0]]},
                {"scope": ["a", "d"], "allowed": [[0, 0], [1, 1]]},
                {"scope": ["b", "e"], "allowed": [[0, 1], [1, 0]]},
            ],
        },
    }


def leaky_discover(blind_view: dict[str, Any]) -> dict[str, Any]:
    # This should never be able to see target metadata. If the mask failed, explode.
    text = canonical_json(blind_view)
    if "MUST_NOT_BE_VISIBLE" in text:
        raise DiagnosticError("target-aware metadata reached discovery")
    return discover_degree_partition(blind_view)


def self_test() -> dict[str, Any]:
    sample = synthetic_fixture()
    result = run_views(sample, seeds=[11, 23, 47, 89, 131, 197, 251], discover=leaky_discover)
    if result["representation_coherence"] != 1.0:
        raise DiagnosticError(f"representation coherence failed: {result['representation_coherence']}")
    result["verdict"] = "PASS_BLIND_REPRESENTATION_COHERENT_CALIBRATION_ONLY"
    result["scientific_authority"] = False
    result["solver_authority"] = False
    result["carrier_authority"] = False
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.self_test:
        parser.error("only --self-test is authorized in v1")
    result = self_test()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
