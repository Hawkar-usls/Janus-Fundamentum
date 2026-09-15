from __future__ import annotations

import hashlib
import json
from pathlib import Path

from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw, RawBasisInputError
from research.tools.apma_bucket_common_core import common_core_semijoin_prefilter as cc_v1
from research.tools.apma_bucket_common_core import common_core_semijoin_prefilter_v1_1 as cc_v11
from research.tools.apma_bucket_conditioned_factorized_payload import conditioned_factorized_payload as v1

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-BUCKET-UNIQUE-CORE-CONDITIONED-FACTORIZED-PAYLOAD-CANDIDATE-2026-09-15-v1.1"
AUTHORITY = "CANDIDATE_SUCCESSOR_REPAIR__CONTROL_DESIGN_ONLY__NO_SCIENTIFIC_PROMOTION"
PREREG = Path("research/TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_CONDITIONED_FACTORIZED_PAYLOAD_V1_1_PREREGISTRATION_2026-09-15.json")
PREREG_BLOB = "PLACEHOLDER_PREREG_BLOB"
V1 = Path("research/tools/apma_bucket_conditioned_factorized_payload/conditioned_factorized_payload.py")
V1_BLOB = "c07cc8c12fa6f7a9b8f2560095caa4bdcc235480"


def root() -> Path:
    return Path(__file__).resolve().parents[3]


def blob(path: Path) -> str:
    d = path.read_bytes()
    return hashlib.sha1(f"blob {len(d)}\0".encode("ascii") + d).hexdigest()


def source_guard() -> dict:
    r = root()
    p = json.loads((r / PREREG).read_text(encoding="utf-8"))
    checks = {
        "v11_prereg_blob": blob(r / PREREG) == PREREG_BLOB,
        "v11_prereg_frozen": p.get("status") == "FROZEN_BEFORE_V1_1_CONTROL_REPAIR",
        "v1_candidate_blob": blob(r / V1) == V1_BLOB,
        "repair_class": p.get("repair_class") == "INCOMPLETE_TARGET_COMPONENT_COVERAGE_NEGATIVE_CONTROL_DESIGN_ONLY",
    }
    return {"ok": all(checks.values()), "checks": checks}


def firewall() -> dict:
    return v1.firewall()


def corrected_incomplete_target_coverage_control() -> dict:
    raw = cc_v1.filtered_still_overbudget_control()
    sticky0 = next(r for r in raw["constraints"] if r["id"] == "sticky_0")
    common_core = set(range(20, 40))
    payload = [int(v) for v in sticky0["scope"] if int(v) not in common_core]
    if len(payload) < 1:
        raise AssertionError("STICKY_0_HAS_NO_FACTOR_LOCAL_PAYLOAD")
    u = payload[0]
    p_new = max(int(v) for v in raw["variables"]) + 1
    raw["variables"].append(p_new)
    raw["constraints"].insert(-1, {
        "id": "nonbucket_same_component_v11",
        "scope": [u, p_new],
        "allowed": [[0, 0], [1, 1]],
    })
    return raw


def corrected_incomplete_precondition() -> dict:
    raw = corrected_incomplete_target_coverage_control()
    predecessor = cc_v11.explain(raw)
    ready = cc_v11.first_failed_original_bucket_v11(raw)
    return {
        "predecessor_status": predecessor.get("status"),
        "failed_variable": ready.get("failed_variable"),
        "ready_status": ready.get("status"),
        "failed_bucket_enumerations": predecessor.get("carrier", {}).get("receipt", {}).get("handoff_failed_bucket_enumerations"),
        "candidate_terminal": v1.explain(raw).get("status"),
    }


def explain(raw: dict) -> dict:
    g = source_guard()
    if not g["ok"]:
        return {"artifact_id": ARTIFACT_ID, "status": "HALT_SOURCE_GUARD", "source_guard": g, "scientific_firewall": firewall()}
    try:
        canonicalize_raw(raw)
    except RawBasisInputError as exc:
        return {"artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "status": "REJECT_RAW_INPUT", "reason": str(exc), "source_guard": g, "scientific_firewall": firewall()}
    out = v1.explain(raw)
    return {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "status": out.get("status"),
        "source_guard": g,
        "frozen_v1_result": out,
        "scientific_firewall": firewall(),
    }


def main() -> None:
    raw = corrected_incomplete_target_coverage_control()
    print(json.dumps({
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "corrected_incomplete_precondition": corrected_incomplete_precondition(),
        "corrected_incomplete": explain(raw),
        "positive_sticky": explain(cc_v1.filtered_still_overbudget_control()),
        "scientific_firewall": firewall(),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
