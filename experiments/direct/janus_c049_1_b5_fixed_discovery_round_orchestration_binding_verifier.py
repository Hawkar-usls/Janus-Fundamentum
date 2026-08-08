from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

CANDIDATE_SCHEMA = "janus.c049_1.b5.fixed_discovery_round_orchestration_binding_candidate.v1"
SPEC_SCHEMA = "janus.c049_1.b5.fixed_discovery_round_orchestration_binding_spec.v1"
PRE_SCHEMA = "janus.c049_1.b5.iterative_compression_preprocessing_binding_candidate.v1"


def cb(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def dg(value: Any) -> str:
    return hashlib.sha256(cb(value)).hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def verify(spec: dict[str, Any], pre: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    if spec.get("schema") != SPEC_SCHEMA or spec.get("status") != "SPEC_FROZEN_CANDIDATE_ONLY_NO_B5_PROMOTION":
        raise AssertionError("spec identity/status")
    if candidate.get("schema") != CANDIDATE_SCHEMA or candidate.get("semantic_digest_scope") != "proof_payload":
        raise AssertionError("candidate headers")
    cp = candidate.get("proof_payload")
    if not isinstance(cp, dict) or candidate.get("semantic_digest") != dg(cp):
        raise AssertionError("candidate semantic digest")
    if pre.get("schema") != PRE_SCHEMA or pre.get("semantic_digest_scope") != "proof_payload":
        raise AssertionError("preprocessing headers")
    pp = pre.get("proof_payload")
    if not isinstance(pp, dict) or pre.get("semantic_digest") != dg(pp):
        raise AssertionError("preprocessing semantic digest")
    original = pp.get("original_catalog")
    discovery = pp.get("discovery_catalog")
    if not isinstance(original, list) or not isinstance(discovery, list) or len(original) != len(discovery):
        raise AssertionError("dual catalog")
    if pp.get("original_catalog_semantic_digest") != dg(original):
        raise AssertionError("original catalog digest")
    if pp.get("discovery_catalog_semantic_digest") != dg(discovery):
        raise AssertionError("discovery catalog digest")

    by_o = {int(x["occurrence_index"]): x for x in original}
    by_d = {int(x["occurrence_index"]): x for x in discovery}
    expected_universe = set(range(len(discovery)))
    if set(by_o) != expected_universe or set(by_d) != expected_universe:
        raise AssertionError("occurrence universe")
    presentation = [int(x["presentation_index"]) for x in original]
    if sorted(presentation) != list(range(len(original))) or len(set(presentation)) != len(presentation):
        raise AssertionError("presentation index universe")
    schedule = [int(x["occurrence_index"]) for x in sorted(original, key=lambda x: int(x["presentation_index"]))]
    if set(schedule) != expected_universe or len(schedule) != len(set(schedule)):
        raise AssertionError("canonical schedule")

    if cp.get("gate") != spec.get("gate"):
        raise AssertionError("gate")
    if cp.get("status") != "CANDIDATE_PENDING_EXACT_HEAD_CI_AND_REVIEW":
        raise AssertionError("candidate status")
    if cp.get("preprocessing_semantic_digest") != pre.get("semantic_digest"):
        raise AssertionError("preprocessing subject rebinding")
    if cp.get("preprocessing_branch") != pp.get("preprocessing_branch"):
        raise AssertionError("preprocessing branch rebinding")
    if cp.get("ambient_dim") != int(pp["ambient_dim"]) or cp.get("k") != int(pp["k"]) or cp.get("theta") != int(pp["theta"]):
        raise AssertionError("parameter rebinding")
    if cp.get("original_catalog_semantic_digest") != pp.get("original_catalog_semantic_digest"):
        raise AssertionError("original catalog subject")
    if cp.get("fixed_discovery_catalog_semantic_digest") != pp.get("discovery_catalog_semantic_digest"):
        raise AssertionError("fixed discovery catalog subject")
    if cp.get("schedule_source") != "ORIGINAL_PRESENTATION_ORDER_RECOVERED_FROM_PREPROCESSING_ORIGINAL_CATALOG":
        raise AssertionError("schedule source")
    if cp.get("schedule_occurrence_indices") != schedule:
        raise AssertionError("schedule occurrence rebinding")
    if cp.get("schedule_factor_ids") != [by_d[i]["factor_id"] for i in schedule]:
        raise AssertionError("schedule factor rebinding")
    if cp.get("strict_boundary") != spec.get("strict_boundary"):
        raise AssertionError("strict boundary")
    if cp.get("completed_round_execution_count") != 0:
        raise AssertionError("execution promotion")
    if cp.get("orchestration_binding_status") != "FIXED_DISCOVERY_ROUND_PLAN_BOUND_EXECUTION_NOT_RUN":
        raise AssertionError("orchestration status")
    if cp.get("next_gate") != "C049.1_B5_FIXED_DISCOVERY_ROUND_EXECUTION_COMPOSITION":
        raise AssertionError("next gate")

    rounds = cp.get("rounds")
    if not isinstance(rounds, list) or len(rounds) != len(schedule):
        raise AssertionError("round count")
    previous_digest: str | None = None
    for r, (occ, record) in enumerate(zip(schedule, rounds), start=1):
        if not isinstance(record, dict):
            raise AssertionError("round record")
        prefix = schedule[:r]
        drec = by_d[occ]
        orec = by_o[occ]
        prefix_records = [by_d[i] for i in prefix]
        expected_prefix_digest = dg(prefix_records)
        expected = {
            "round_index": r,
            "prefix_occurrence_indices": prefix,
            "prefix_factor_ids": [by_d[i]["factor_id"] for i in prefix],
            "new_occurrence_index": occ,
            "new_factor_id": drec["factor_id"],
            "new_fixed_discovery_record_digest": dg(drec),
            "new_fixed_discovery_dimension": len(drec.get("normal_space", [])),
            "theta_2k": int(pp["theta"]),
            "local_dimension_at_most_2k": len(drec.get("normal_space", [])) <= int(pp["theta"]),
            "full_preprocessing_semantic_digest": pre["semantic_digest"],
            "fixed_discovery_catalog_semantic_digest": pp["discovery_catalog_semantic_digest"],
            "previous_prefix_semantic_digest": previous_digest,
            "prefix_semantic_digest": expected_prefix_digest,
            "round_execution_status": "PENDING_SEPARATE_B5_RUNTIME_COMPOSITION",
        }
        if record != expected:
            raise AssertionError(f"round {r} exact binding")
        if cb(drec.get("affine_offset")) != cb(orec.get("affine_offset")):
            raise AssertionError("affine identity conservation")
        previous_digest = expected_prefix_digest

    if cp.get("strict_boundary", {}).get("b5_complete") is not False:
        raise AssertionError("B5 promotion")
    if cp.get("strict_boundary", {}).get("c049_1_complete") is not False:
        raise AssertionError("C049.1 promotion")
    if cp.get("strict_boundary", {}).get("p_vs_np") != "OPEN":
        raise AssertionError("P vs NP promotion")

    return {
        "status": "PASS",
        "fixed_discovery_catalog": "BOUND",
        "schedule_occurrence_count": len(schedule),
        "round_plan_count": len(rounds),
        "round_execution": "NOT_RUN",
        "next_gate": cp["next_gate"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--preprocessing", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    args = parser.parse_args()
    report = verify(load(args.spec), load(args.preprocessing), load(args.candidate))
    print("JANUS_B5_FIXED_DISCOVERY_ROUND_BINDING_INDEPENDENT_VERIFIER = PASS")
    print("FIXED_DISCOVERY_CATALOG = BOUND")
    print("SCHEDULE_OCCURRENCE_COUNT =", report["schedule_occurrence_count"])
    print("ROUND_PLAN_COUNT =", report["round_plan_count"])
    print("ROUND_EXECUTION = NOT_RUN")
    print("NEXT_GATE =", report["next_gate"])
    print("B5_COMPLETE = FALSE")
    print("C049_1_COMPLETE = FALSE")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
