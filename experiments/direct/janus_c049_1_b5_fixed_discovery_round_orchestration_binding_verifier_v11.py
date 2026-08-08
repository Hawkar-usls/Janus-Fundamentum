from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

CANDIDATE_SCHEMA = "janus.c049_1.b5.fixed_discovery_round_orchestration_binding_candidate.v1_1"
SPEC_SCHEMA = "janus.c049_1.b5.fixed_discovery_round_orchestration_binding_spec.v1_1"
PRE_SCHEMA = "janus.c049_1.b5.iterative_compression_preprocessing_binding_candidate.v1"


def cb(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def dg(value: Any) -> str:
    return hashlib.sha256(cb(value)).hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def verify(spec: dict[str, Any], pre: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    if spec.get("schema") != SPEC_SCHEMA or spec.get("status") != "SPEC_FROZEN_CANDIDATE_ONLY_NO_B5_PROMOTION":
        raise AssertionError("spec")
    if candidate.get("schema") != CANDIDATE_SCHEMA or candidate.get("semantic_digest_scope") != "proof_payload":
        raise AssertionError("candidate headers")
    cp = candidate.get("proof_payload")
    if not isinstance(cp, dict) or candidate.get("semantic_digest") != dg(cp):
        raise AssertionError("candidate digest")
    if pre.get("schema") != PRE_SCHEMA or pre.get("semantic_digest_scope") != "proof_payload":
        raise AssertionError("preprocessing headers")
    pp = pre.get("proof_payload")
    if not isinstance(pp, dict) or pre.get("semantic_digest") != dg(pp):
        raise AssertionError("preprocessing digest")
    original, discovery = pp.get("original_catalog"), pp.get("discovery_catalog")
    if not isinstance(original, list) or not isinstance(discovery, list) or len(original) != len(discovery):
        raise AssertionError("dual catalog")
    if pp.get("original_catalog_semantic_digest") != dg(original) or pp.get("discovery_catalog_semantic_digest") != dg(discovery):
        raise AssertionError("catalog digests")
    by_o = {int(x["occurrence_index"]): x for x in original}; by_d = {int(x["occurrence_index"]): x for x in discovery}
    universe = set(range(len(discovery)))
    if set(by_o) != universe or set(by_d) != universe:
        raise AssertionError("occurrence universe")
    presentation = [int(x["presentation_index"]) for x in original]
    if sorted(presentation) != list(range(len(original))) or len(set(presentation)) != len(presentation):
        raise AssertionError("presentation universe")
    schedule = [int(x["occurrence_index"]) for x in sorted(original, key=lambda x: int(x["presentation_index"]))]
    if set(schedule) != universe or len(schedule) != len(set(schedule)):
        raise AssertionError("schedule")
    if cp.get("gate") != spec["gate"] or cp.get("status") != "CANDIDATE_PENDING_EXACT_HEAD_CI_AND_REVIEW":
        raise AssertionError("gate/status")
    if cp.get("preprocessing_authority_version") != "V1_1_CANONICAL_RREF":
        raise AssertionError("preprocessing downgrade")
    if cp.get("preprocessing_semantic_digest") != pre["semantic_digest"] or cp.get("preprocessing_branch") != pp["preprocessing_branch"]:
        raise AssertionError("preprocessing subject")
    if (cp.get("ambient_dim"), cp.get("k"), cp.get("theta")) != (int(pp["ambient_dim"]), int(pp["k"]), int(pp["theta"])):
        raise AssertionError("parameters")
    if cp.get("original_catalog_semantic_digest") != pp["original_catalog_semantic_digest"] or cp.get("fixed_discovery_catalog_semantic_digest") != pp["discovery_catalog_semantic_digest"]:
        raise AssertionError("catalog subject")
    if cp.get("schedule_source") != "ORIGINAL_PRESENTATION_ORDER_RECOVERED_FROM_PREPROCESSING_ORIGINAL_CATALOG" or cp.get("schedule_occurrence_indices") != schedule:
        raise AssertionError("schedule binding")
    if cp.get("schedule_factor_ids") != [by_d[i]["factor_id"] for i in schedule]:
        raise AssertionError("factor schedule")
    if cp.get("strict_boundary") != spec["strict_boundary"] or cp.get("completed_round_execution_count") != 0:
        raise AssertionError("boundary/execution")
    if cp.get("orchestration_binding_status") != "FIXED_DISCOVERY_ROUND_PLAN_BOUND_EXECUTION_NOT_RUN" or cp.get("next_gate") != "C049.1_B5_FIXED_DISCOVERY_ROUND_EXECUTION_COMPOSITION":
        raise AssertionError("terminal binding")
    rounds = cp.get("rounds")
    if not isinstance(rounds, list) or len(rounds) != len(schedule):
        raise AssertionError("round count")
    previous = None
    for r, (occ, record) in enumerate(zip(schedule, rounds), start=1):
        prefix = schedule[:r]; drec = by_d[occ]; orec = by_o[occ]; prefix_digest = dg([by_d[i] for i in prefix])
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
            "previous_prefix_semantic_digest": previous,
            "prefix_semantic_digest": prefix_digest,
            "round_execution_status": "PENDING_SEPARATE_B5_RUNTIME_COMPOSITION",
        }
        if record != expected:
            raise AssertionError(f"round {r} exact binding")
        if cb(drec.get("affine_offset")) != cb(orec.get("affine_offset")):
            raise AssertionError("affine identity")
        previous = prefix_digest
    b = cp["strict_boundary"]
    if b.get("preprocessing_v1_1") != "ESTABLISHED_IN_CURRENT_TESTED_CANONICALIZATION_SCOPE" or b.get("preprocessing_global_completeness") != "NOT_ESTABLISHED":
        raise AssertionError("preprocessing ceiling")
    if b.get("b5_complete") is not False or b.get("c049_1_complete") is not False or b.get("p_vs_np") != "OPEN":
        raise AssertionError("claim promotion")
    return {"status":"PASS","fixed_discovery_catalog":"BOUND","schedule_occurrence_count":len(schedule),"round_plan_count":len(rounds),"next_gate":cp["next_gate"]}


def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument("--spec",type=Path,required=True); ap.add_argument("--preprocessing",type=Path,required=True); ap.add_argument("--candidate",type=Path,required=True); a=ap.parse_args()
    r=verify(load(a.spec),load(a.preprocessing),load(a.candidate))
    print("JANUS_B5_FIXED_DISCOVERY_ROUND_BINDING_V1_1_INDEPENDENT_VERIFIER = PASS"); print("PREPROCESSING_AUTHORITY_VERSION = V1_1_CANONICAL_RREF"); print("FIXED_DISCOVERY_CATALOG = BOUND")
    print("SCHEDULE_OCCURRENCE_COUNT =",r["schedule_occurrence_count"]); print("ROUND_PLAN_COUNT =",r["round_plan_count"]); print("ROUND_EXECUTION = NOT_RUN"); print("NEXT_GATE =",r["next_gate"])
    print("B5_COMPLETE = FALSE"); print("C049_1_COMPLETE = FALSE"); print("P_VS_NP = OPEN")


if __name__ == "__main__": main()
