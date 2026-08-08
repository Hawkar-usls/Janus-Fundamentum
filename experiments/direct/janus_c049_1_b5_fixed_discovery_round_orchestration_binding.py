from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMA = "janus.c049_1.b5.fixed_discovery_round_orchestration_binding_candidate.v1"
SPEC_SCHEMA = "janus.c049_1.b5.fixed_discovery_round_orchestration_binding_spec.v1"
PRE_SCHEMA = "janus.c049_1.b5.iterative_compression_preprocessing_binding_candidate.v1"


def cb(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def dg(value: Any) -> str:
    return hashlib.sha256(cb(value)).hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def save(value: Any, path: Path) -> None:
    path.write_bytes(cb(value) + b"\n")


def validate_preprocessing(pre: dict[str, Any]) -> dict[str, Any]:
    if pre.get("schema") != PRE_SCHEMA:
        raise AssertionError("preprocessing schema")
    if pre.get("semantic_digest_scope") != "proof_payload":
        raise AssertionError("preprocessing digest scope")
    payload = pre.get("proof_payload")
    if not isinstance(payload, dict) or pre.get("semantic_digest") != dg(payload):
        raise AssertionError("preprocessing semantic digest")
    if payload.get("preprocessing_branch") not in {
        "PREPROCESSING_BOUND",
        "TRIVIAL_SINGLETON_INPUT",
        "TRIVIAL_EMPTY_INPUT",
        "LOCAL_NO_LAYOUT_SOURCE_CANDIDATE_PENDING_REVIEW",
    }:
        raise AssertionError("preprocessing branch")
    if payload.get("discovery_catalog_semantic_digest") != dg(payload.get("discovery_catalog")):
        raise AssertionError("discovery catalog digest")
    if payload.get("original_catalog_semantic_digest") != dg(payload.get("original_catalog")):
        raise AssertionError("original catalog digest")
    return payload


def canonical_schedule(pre_payload: dict[str, Any]) -> list[int]:
    original = pre_payload.get("original_catalog")
    discovery = pre_payload.get("discovery_catalog")
    if not isinstance(original, list) or not isinstance(discovery, list) or len(original) != len(discovery):
        raise AssertionError("dual catalog length")
    by_occ = {int(x["occurrence_index"]): x for x in original}
    if set(by_occ) != set(range(len(original))):
        raise AssertionError("original occurrence universe")
    schedule = [
        int(x["occurrence_index"])
        for x in sorted(original, key=lambda x: int(x["presentation_index"]))
    ]
    if sorted(schedule) != list(range(len(discovery))) or len(set(schedule)) != len(schedule):
        raise AssertionError("schedule exact occurrence permutation")
    return schedule


def build(spec: dict[str, Any], pre: dict[str, Any]) -> dict[str, Any]:
    if spec.get("schema") != SPEC_SCHEMA:
        raise AssertionError("spec schema")
    if spec.get("status") != "SPEC_FROZEN_CANDIDATE_ONLY_NO_B5_PROMOTION":
        raise AssertionError("spec status")
    p = validate_preprocessing(pre)
    discovery = p["discovery_catalog"]
    original = p["original_catalog"]
    by_discovery = {int(x["occurrence_index"]): x for x in discovery}
    by_original = {int(x["occurrence_index"]): x for x in original}
    schedule = canonical_schedule(p)
    rounds: list[dict[str, Any]] = []
    previous_prefix_digest: str | None = None
    for r, occurrence_index in enumerate(schedule, start=1):
        prefix = schedule[:r]
        record = by_discovery[occurrence_index]
        source = by_original[occurrence_index]
        if cb(record.get("affine_offset")) != cb(source.get("affine_offset")):
            raise AssertionError("affine offset identity")
        prefix_records = [by_discovery[i] for i in prefix]
        prefix_digest = dg(prefix_records)
        rounds.append({
            "round_index": r,
            "prefix_occurrence_indices": prefix,
            "prefix_factor_ids": [by_discovery[i]["factor_id"] for i in prefix],
            "new_occurrence_index": occurrence_index,
            "new_factor_id": record["factor_id"],
            "new_fixed_discovery_record_digest": dg(record),
            "new_fixed_discovery_dimension": len(record.get("normal_space", [])),
            "theta_2k": int(p["theta"]),
            "local_dimension_at_most_2k": len(record.get("normal_space", [])) <= int(p["theta"]),
            "full_preprocessing_semantic_digest": pre["semantic_digest"],
            "fixed_discovery_catalog_semantic_digest": p["discovery_catalog_semantic_digest"],
            "previous_prefix_semantic_digest": previous_prefix_digest,
            "prefix_semantic_digest": prefix_digest,
            "round_execution_status": "PENDING_SEPARATE_B5_RUNTIME_COMPOSITION",
        })
        previous_prefix_digest = prefix_digest

    payload = {
        "gate": spec["gate"],
        "status": "CANDIDATE_PENDING_EXACT_HEAD_CI_AND_REVIEW",
        "preprocessing_semantic_digest": pre["semantic_digest"],
        "preprocessing_branch": p["preprocessing_branch"],
        "ambient_dim": int(p["ambient_dim"]),
        "k": int(p["k"]),
        "theta": int(p["theta"]),
        "original_catalog_semantic_digest": p["original_catalog_semantic_digest"],
        "fixed_discovery_catalog_semantic_digest": p["discovery_catalog_semantic_digest"],
        "schedule_source": "ORIGINAL_PRESENTATION_ORDER_RECOVERED_FROM_PREPROCESSING_ORIGINAL_CATALOG",
        "schedule_occurrence_indices": schedule,
        "schedule_factor_ids": [by_discovery[i]["factor_id"] for i in schedule],
        "rounds": rounds,
        "completed_round_execution_count": 0,
        "orchestration_binding_status": "FIXED_DISCOVERY_ROUND_PLAN_BOUND_EXECUTION_NOT_RUN",
        "next_gate": "C049.1_B5_FIXED_DISCOVERY_ROUND_EXECUTION_COMPOSITION",
        "strict_boundary": spec["strict_boundary"],
    }
    artifact = {
        "schema": SCHEMA,
        "semantic_digest_scope": "proof_payload",
        "proof_payload": payload,
    }
    artifact["semantic_digest"] = dg(payload)
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--preprocessing", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    artifact = build(load(args.spec), load(args.preprocessing))
    save(artifact, args.output)
    p = artifact["proof_payload"]
    print("FIXED_DISCOVERY_ROUND_ORCHESTRATION_BINDING = CANDIDATE")
    print("SCHEDULE_OCCURRENCE_COUNT =", len(p["schedule_occurrence_indices"]))
    print("ROUND_PLAN_COUNT =", len(p["rounds"]))
    print("ROUND_EXECUTION = NOT_RUN")
    print("B5_COMPLETE = FALSE")
    print("C049_1_COMPLETE = FALSE")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
