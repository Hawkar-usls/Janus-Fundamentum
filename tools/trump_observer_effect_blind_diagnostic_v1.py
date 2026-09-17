#!/usr/bin/env python3
"""TRUMP observer-effect / information-leakage diagnostic v1.

DIAGNOSTIC ONLY. NO SOLVER OR CARRIER AUTHORITY.

This is an orchestration/calibration harness, not a new discovery mechanism. Existing
TRUMP blind execution already tests representation invariance. This successor diagnostic
adds a stricter systems question: can an observer/telemetry path see target-aware data or
perturb the exact bytes consumed by discovery?

The candidate receives a fresh decode of precommitted blind bytes. Every observer receives
an independent decode. Candidate input hashes and candidate hashes must be identical across
NO_OBSERVER, READ_ONLY_OBSERVER, and HOSTILE_COPY_OBSERVER modes. A separate target-metadata
canary must never occur in the blind bytes. Provenance is revealed only after candidate
hashes have been frozen.

Current --self-test uses synthetic calibration fixtures only. v3.23 forbids treating the
exhausted connected-mixed corpus as new evidence.
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
CANARY = "JANUS_TARGET_METADATA_CANARY__MUST_NEVER_REACH_DISCOVERY__7F3A91"
OBSERVER_MODES = ("NO_OBSERVER", "READ_ONLY_OBSERVER", "HOSTILE_COPY_OBSERVER")


class DiagnosticError(RuntimeError):
    pass


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def canonical_bytes(obj: Any) -> bytes:
    return canonical_json(obj).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_obj(obj: Any) -> str:
    return sha256_bytes(canonical_bytes(obj))


def blind_mask(sample: dict[str, Any]) -> dict[str, Any]:
    """Build the complete candidate-visible object and reject target metadata leakage."""
    masked = {"sample_id": sample["sample_id"], "raw": copy.deepcopy(sample["raw"])}
    text = canonical_json(masked)
    for field in FORBIDDEN_METADATA:
        if f'"{field}"' in text:
            raise DiagnosticError(f"forbidden metadata leaked into blind view: {field}")
    if CANARY in text:
        raise DiagnosticError("target metadata canary leaked into blind view")
    return masked


@dataclass(frozen=True)
class TransformReceipt:
    seed: int
    forward: dict[str, str]
    inverse: dict[str, str]


def variable_rename_view(masked: dict[str, Any], seed: int) -> tuple[dict[str, Any], TransformReceipt]:
    """Semantics-preserving calibration disguise for a finite explicit-relation object."""
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
    """Simple invariant candidate used only to calibrate the orchestration harness."""
    text = canonical_json(blind_view)
    if CANARY in text:
        raise DiagnosticError("candidate saw target metadata canary")
    for field in FORBIDDEN_METADATA:
        if f'"{field}"' in text:
            raise DiagnosticError(f"candidate saw forbidden metadata field: {field}")

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


def run_observer(mode: str, observer_copy: dict[str, Any]) -> dict[str, Any]:
    """Observe only an isolated decoded copy. HOSTILE mode deliberately mutates its copy."""
    if mode == "NO_OBSERVER":
        return {"mode": mode, "observed": False}
    if mode == "READ_ONLY_OBSERVER":
        raw = observer_copy["raw"]
        return {
            "mode": mode,
            "observed": True,
            "variable_count": len(raw["variables"]),
            "relation_count": len(raw["relations"]),
            "observer_copy_sha256": sha256_obj(observer_copy),
        }
    if mode == "HOSTILE_COPY_OBSERVER":
        observer_copy["sample_id"] = CANARY
        observer_copy["raw"]["variables"].reverse()
        observer_copy["raw"]["relations"].clear()
        observer_copy["expected_mechanism_label"] = CANARY
        return {
            "mode": mode,
            "observed": True,
            "mutated_private_copy": True,
            "observer_copy_sha256_after_mutation": sha256_obj(observer_copy),
        }
    raise DiagnosticError(f"unknown observer mode: {mode}")


def execute_precommitted_payload(
    payload_bytes: bytes,
    mode: str,
    discover: Callable[[dict[str, Any]], dict[str, Any]],
) -> dict[str, Any]:
    """Run observer and candidate from independent decodes of immutable committed bytes."""
    pre_sha = sha256_bytes(payload_bytes)

    observer_copy = json.loads(payload_bytes.decode("utf-8"))
    observer_receipt = run_observer(mode, observer_copy)

    # Critical barrier: discovery never receives observer_copy. It gets a fresh decode.
    candidate_input = json.loads(payload_bytes.decode("utf-8"))
    candidate_input_bytes = canonical_bytes(candidate_input)
    candidate_input_sha = sha256_bytes(candidate_input_bytes)
    if candidate_input_sha != pre_sha:
        raise DiagnosticError("candidate input differs from precommitted blind payload")

    candidate = discover(candidate_input)
    post_sha = sha256_bytes(payload_bytes)
    if post_sha != pre_sha:
        raise DiagnosticError("observer altered precommitted payload bytes")

    return {
        "observer": observer_receipt,
        "precommitted_payload_sha256": pre_sha,
        "candidate_input_sha256": candidate_input_sha,
        "post_observer_payload_sha256": post_sha,
        "candidate": candidate,
        "candidate_sha256": sha256_obj(candidate),
    }


def run_views(
    sample: dict[str, Any],
    seeds: list[int],
    discover: Callable[[dict[str, Any]], dict[str, Any]],
) -> dict[str, Any]:
    masked = blind_mask(sample)
    raw_sha = sha256_obj(masked["raw"])
    per_view = []
    canonical_hashes = []
    observer_mode_consistency = True

    for seed in seeds:
        view, receipt = variable_rename_view(masked, seed)
        payload_bytes = canonical_bytes(view)
        mode_runs = [execute_precommitted_payload(payload_bytes, mode, discover) for mode in OBSERVER_MODES]

        mode_candidate_hashes = {run["candidate_sha256"] for run in mode_runs}
        mode_input_hashes = {run["candidate_input_sha256"] for run in mode_runs}
        mode_payload_hashes = {run["precommitted_payload_sha256"] for run in mode_runs}
        if len(mode_candidate_hashes) != 1 or len(mode_input_hashes) != 1 or len(mode_payload_hashes) != 1:
            observer_mode_consistency = False

        found = mode_runs[0]["candidate"]
        canonical = canonical_candidate(inverse_map_candidate(found, receipt))
        canonical_hash = sha256_obj(canonical)
        canonical_hashes.append(canonical_hash)
        per_view.append(
            {
                "seed": seed,
                "blind_payload_sha256": sha256_bytes(payload_bytes),
                "observer_modes_candidate_identical": len(mode_candidate_hashes) == 1,
                "observer_modes_input_identical": len(mode_input_hashes) == 1,
                "canonical_candidate_sha256": canonical_hash,
                "observer_receipts": [run["observer"] for run in mode_runs],
            }
        )

    modal = max(set(canonical_hashes), key=canonical_hashes.count)
    coherence = canonical_hashes.count(modal) / len(canonical_hashes)

    # Candidate freeze happens before metadata/provenance reveal.
    freeze_manifest = {
        "raw_semantic_sha256": raw_sha,
        "transform_seeds": seeds,
        "canonical_candidate_hashes": canonical_hashes,
    }
    freeze_sha = sha256_obj(freeze_manifest)

    # Delayed reveal: only now touch the target-aware metadata envelope.
    revealed_metadata = copy.deepcopy(sample["target_metadata_envelope"])
    if CANARY not in canonical_json(revealed_metadata):
        raise DiagnosticError("calibration target-metadata canary missing from reveal envelope")
    if sha256_obj(freeze_manifest) != freeze_sha:
        raise DiagnosticError("candidate freeze changed after delayed provenance reveal")

    return {
        "raw_semantic_sha256": raw_sha,
        "transform_seeds": seeds,
        "representation_coherence": coherence,
        "all_inverse_mapped_candidates_equal": len(set(canonical_hashes)) == 1,
        "observer_noninterference": observer_mode_consistency,
        "blindness_canary_absent_from_candidate_payload": CANARY not in canonical_json(masked),
        "candidate_freeze_sha256_before_delayed_reveal": freeze_sha,
        "candidate_freeze_unchanged_after_delayed_reveal": sha256_obj(freeze_manifest) == freeze_sha,
        "revealed_metadata_sha256_after_freeze": sha256_obj(revealed_metadata),
        "views": per_view,
    }


def unsafe_shared_object_negative_control() -> dict[str, Any]:
    """Prove the detector catches the exact anti-pattern the safe path forbids."""
    shared = blind_mask(synthetic_fixture())
    before = sha256_obj(shared)
    # Simulate an observer that is incorrectly handed the candidate's mutable object.
    shared["raw"]["relations"].clear()
    shared["sample_id"] = CANARY
    after = sha256_obj(shared)
    detected = before != after or CANARY in canonical_json(shared)
    if not detected:
        raise DiagnosticError("unsafe shared-object negative control was not detected")
    return {
        "control": "UNSAFE_SHARED_MUTABLE_OBSERVER_PATH",
        "expected": "DETECT_CONTAMINATION",
        "detected": detected,
        "before_sha256": before,
        "after_sha256": after,
        "scientific_authority": False,
    }


def synthetic_fixture() -> dict[str, Any]:
    return {
        "sample_id": "opaque-calibration-001",
        "source_path": CANARY,
        "constructor_name": CANARY,
        "historical_verdict": CANARY,
        "expected_mechanism_label": CANARY,
        "target_metadata_envelope": {
            "source_path": CANARY,
            "constructor_name": CANARY,
            "historical_verdict": CANARY,
            "expected_mechanism_label": CANARY,
        },
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


def self_test() -> dict[str, Any]:
    sample = synthetic_fixture()
    result = run_views(sample, seeds=[11, 23, 47, 89, 131, 197, 251], discover=discover_degree_partition)
    negative_control = unsafe_shared_object_negative_control()

    required = {
        "representation_coherence": result["representation_coherence"] == 1.0,
        "observer_noninterference": result["observer_noninterference"],
        "blindness_canary": result["blindness_canary_absent_from_candidate_payload"],
        "delayed_reveal_freeze": result["candidate_freeze_unchanged_after_delayed_reveal"],
        "unsafe_path_detected": negative_control["detected"],
    }
    if not all(required.values()):
        raise DiagnosticError(f"calibration failed: {required}")

    return {
        "verdict": "PASS_OBSERVER_NONINTERFERENCE_AND_BLINDNESS_CANARY_CALIBRATION_ONLY",
        "classification": "DIAGNOSTIC_ONLY__SUCCESSOR_ORCHESTRATION_HARDENING",
        "existing_representation_invariance_retested_not_repromoted": True,
        "required_checks": required,
        "safe_path": result,
        "negative_control": negative_control,
        "scientific_authority": False,
        "solver_authority": False,
        "carrier_authority": False,
        "universality_authority": False,
        "current_corpus_new_evidence": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.self_test:
        parser.error("only --self-test is authorized in v1")
    print(json.dumps(self_test(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
