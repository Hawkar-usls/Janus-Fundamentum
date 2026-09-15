from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from research.tools.apma_bucket_closed_two_factor import closed_two_factor_carrier as v1

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-BUCKET-UNIQUE-CORE-RESIDUAL-CLOSED-INTERNAL-TWO-FACTOR-F-FACTOR-CARRIER-2026-09-15-v1.1"
AUTHORITY = "CANDIDATE_IMPLEMENTATION_REPAIR__NO_SCIENTIFIC_PROMOTION"
VERDICT = v1.VERDICT

PREREG = Path("research/TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_CLOSED_INTERNAL_TWO_FACTOR_F_FACTOR_CARRIER_PREREGISTRATION_2026-09-15.json")
PREREG_BLOB = "1240d183461bfab4defe42df14ffdb2df31396da"
THEOREM = Path("research/TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_CLOSED_INTERNAL_TWO_FACTOR_F_FACTOR_CARRIER_THEOREM_CANDIDATE_2026-09-15.md")
THEOREM_BLOB = "3c3db06ec64f6f130deca98fef0e0f0f060ac562"
PARENT_STATE = Path("registry/TRUMP_CURRENT_STATE_2026-09-15_v3.17.json")
PARENT_STATE_BLOB = "bf871e4e574381373f8c4d207eca9a12c9175ea4"
V1_CANDIDATE = Path("research/tools/apma_bucket_closed_two_factor/closed_two_factor_carrier.py")
V1_CANDIDATE_BLOB = "2e81d4f908deea1c08a6e8c32b0ca26b7cb532eb"
COMPONENT = Path("research/tools/apma_bucket_closed_two_factor/two_factor_component.py")
COMPONENT_BLOB = "06a8980dc56d8d098618ddee0fe74e5b328dcac7"
MATCHING_CORE = Path("research/tools/apma_bucket_closed_two_factor/matching_core.py")
MATCHING_CORE_BLOB = "8a09164e2ff3277611dfd310331e5792157bf413"


def root() -> Path:
    return Path(__file__).resolve().parents[3]


def git_blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def source_guard() -> dict[str, Any]:
    r = root()
    checks = {
        "prereg_blob": git_blob(r / PREREG) == PREREG_BLOB,
        "theorem_candidate_blob": git_blob(r / THEOREM) == THEOREM_BLOB,
        "parent_v3_17_blob": git_blob(r / PARENT_STATE) == PARENT_STATE_BLOB,
        "immutable_v1_candidate_blob": git_blob(r / V1_CANDIDATE) == V1_CANDIDATE_BLOB,
        "component_blob": git_blob(r / COMPONENT) == COMPONENT_BLOB,
        "repaired_matching_core_blob": git_blob(r / MATCHING_CORE) == MATCHING_CORE_BLOB,
    }
    return {"ok": all(checks.values()), "checks": checks}


def explain(raw: dict[str, Any]) -> dict[str, Any]:
    guard = source_guard()
    if not guard["ok"]:
        return {
            "artifact_id": ARTIFACT_ID,
            "status": "HALT_SOURCE_GUARD",
            "source_guard": guard,
            "scientific_firewall": v1.firewall(),
        }
    try:
        v1.canonicalize_raw(raw)
    except v1.RawBasisInputError as exc:
        return {
            "artifact_id": ARTIFACT_ID,
            "authority": AUTHORITY,
            "status": "REJECT_RAW_INPUT",
            "reason": str(exc),
            "source_guard": guard,
            "scientific_firewall": v1.firewall(),
        }
    carrier = v1.build(raw)
    return {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "status": carrier["status"],
        "source_guard": guard,
        "carrier": carrier,
        "repair_receipt": {
            "immutable_v1_candidate_blob": V1_CANDIDATE_BLOB,
            "repaired_matching_core_blob": MATCHING_CORE_BLOB,
            "repair": "GALLAI_EDMONDS_H_MINUS_V_CALLS_FILTER_INCIDENT_EDGES_BEFORE_MATCHING",
            "preregistration_changed": False,
            "theorem_candidate_changed": False,
        },
        "scientific_firewall": v1.firewall(),
    }


def main() -> None:
    out = {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "source_guard": source_guard(),
        "positive_k5": explain(v1.positive_k5_control()),
        "unsat_cubic_three_bridge": explain(v1.cubic_three_bridge_unsat_control()),
        "malformed_relation": explain(v1.malformed_relation_control()),
        "invalid_incidence": explain(v1.invalid_incidence_control()),
        "boundary_bearing_unit": v1.boundary_bearing_unit_control(),
        "multiple_common_core": explain(v1.multiple_common_core_control()),
        "tampered_proposal": v1.tampered_proposal_control(),
        "tampered_sat_certificate": v1.tampered_sat_certificate_control(),
        "tampered_unsat_certificate": v1.tampered_unsat_certificate_control(),
        "repair_receipt": {
            "immutable_v1_candidate_blob": V1_CANDIDATE_BLOB,
            "repaired_matching_core_blob": MATCHING_CORE_BLOB,
            "repair": "FILTER_DELETED_VERTEX_INCIDENT_EDGES_IN_GALLAI_EDMONDS_SUBCALLS",
            "preregistration_changed": False,
        },
        "scientific_firewall": v1.firewall(),
    }
    print(json.dumps(out, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
