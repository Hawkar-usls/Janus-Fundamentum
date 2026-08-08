from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMA = "janus.c049_1.b5.fixed_discovery_round_orchestration_binding_candidate.v1_1"
SPEC_SCHEMA = "janus.c049_1.b5.fixed_discovery_round_orchestration_binding_spec.v1_1"
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
    if pre.get("schema") != PRE_SCHEMA or pre.get("semantic_digest_scope") != "proof_payload":
        raise AssertionError("preprocessing headers")
    payload = pre.get("proof_payload")
    if not isinstance(payload, dict) or pre.get("semantic_digest") != dg(payload):
        raise AssertionError("preprocessing semantic digest")
    if payload.get("discovery_catalog_semantic_digest") != dg(payload.get("discovery_catalog")):
        raise AssertionError("discovery catalog digest")
    if payload.get("original_catalog_semantic_digest") != dg(payload.get("original_catalog")):
        raise AssertionError("original catalog digest")
    return payload


def canonical_schedule(payload: dict[str, Any]) -> list[int]:
    original = payload["original_catalog"]
    discovery = payload["discovery_catalog"]
    if len(original) != len(discovery):
        raise AssertionError("dual catalog length")
    by_occ = {int(x["occurrence_index"]): x for x in original}
    if set(by_occ) != set(range(len(original))):
        raise AssertionError("occurrence universe")
    schedule = [int(x["occurrence_index"]) for x in sorted(original, key=lambda x: int(x["presentation_index"]))]
    if sorted(schedule) != list(range(len(discovery))) or len(set(schedule)) != len(schedule):
        raise AssertionError("schedule permutation")
    return schedule


def build(spec: dict[str, Any], pre: dict[str, Any]) -> dict[str, Any]:
    if spec.get("schema") != SPEC_SCHEMA or spec.get("status") != "SPEC_FROZEN_CANDIDATE_ONLY_NO_B5_PROMOTION":
        raise AssertionError("spec")
    p = validate_preprocessing(pre)
    discovery = p["discovery_catalog"]
    original = p["original_catalog"]
    by_d = {int(x["occurrence_index"]): x for x in discovery}
    by_o = {int(x["occurrence_index"]): x for x in original}
    schedule = canonical_schedule(p)
    rounds = []
    previous = None
    for r, occ in enumerate(schedule, start=1):
        prefix = schedule[:r]
        drec, orec = by_d[occ], by_o[occ]
        if cb(drec.get("affine_offset")) != cb(orec.get("affine_offset")):
            raise AssertionError("affine identity")
        prefix_digest = dg([by_d[i] for i in prefix])
        rounds.append({
            "round_index": r,
            "prefix_occurrence_indices": prefix,
            "prefix_factor_ids": [by_d[i]["factor_id"] for i in prefix],
            "new_occurrence_index": occ,
            "new_factor_id": drec["factor_id"],
            "new_fixed_discovery_record_digest": dg(drec),
            "new_fixed_discovery_dimension": len(drec.get("normal_space", [])),
            "theta_2k": int(p["theta"]),
            "local_dimension_at_most_2k": len(drec.get("normal_space", [])) <= int(p["theta"]),
            "full_preprocessing_semantic_digest": pre["semantic_digest"],
            "fixed_discovery_catalog_semantic_digest": p["discovery_catalog_semantic_digest"],
            "previous_prefix_semantic_digest": previous,
            "prefix_semantic_digest": prefix_digest,
            "round_execution_status": "PENDING_SEPARATE_B5_RUNTIME_COMPOSITION",
        })
        previous = prefix_digest
    payload = {
        "gate": spec["gate"],
        "status": "CANDIDATE_PENDING_EXACT_HEAD_CI_AND_REVIEW",
        "preprocessing_authority_version": "V1_1_CANONICAL_RREF",
        "preprocessing_semantic_digest": pre["semantic_digest"],
        "preprocessing_branch": p["preprocessing_branch"],
        "ambient_dim": int(p["ambient_dim"]), "k": int(p["k"]), "theta": int(p["theta"]),
        "original_catalog_semantic_digest": p["original_catalog_semantic_digest"],
        "fixed_discovery_catalog_semantic_digest": p["discovery_catalog_semantic_digest"],
        "schedule_source": "ORIGINAL_PRESENTATION_ORDER_RECOVERED_FROM_PREPROCESSING_ORIGINAL_CATALOG",
        "schedule_occurrence_indices": schedule,
        "schedule_factor_ids": [by_d[i]["factor_id"] for i in schedule],
        "rounds": rounds,
        "completed_round_execution_count": 0,
        "orchestration_binding_status": "FIXED_DISCOVERY_ROUND_PLAN_BOUND_EXECUTION_NOT_RUN",
        "next_gate": "C049.1_B5_FIXED_DISCOVERY_ROUND_EXECUTION_COMPOSITION",
        "strict_boundary": spec["strict_boundary"],
    }
    artifact = {"schema": SCHEMA, "semantic_digest_scope": "proof_payload", "proof_payload": payload}
    artifact["semantic_digest"] = dg(payload)
    return artifact


def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("--spec", type=Path, required=True); ap.add_argument("--preprocessing", type=Path, required=True); ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args(); artifact = build(load(a.spec), load(a.preprocessing)); save(artifact, a.output); p = artifact["proof_payload"]
    print("FIXED_DISCOVERY_ROUND_ORCHESTRATION_BINDING_V1_1 = CANDIDATE")
    print("PREPROCESSING_AUTHORITY_VERSION = V1_1_CANONICAL_RREF")
    print("SCHEDULE_OCCURRENCE_COUNT =", len(p["schedule_occurrence_indices"])); print("ROUND_PLAN_COUNT =", len(p["rounds"])); print("ROUND_EXECUTION = NOT_RUN")
    print("B5_COMPLETE = FALSE"); print("C049_1_COMPLETE = FALSE"); print("P_VS_NP = OPEN")


if __name__ == "__main__": main()
