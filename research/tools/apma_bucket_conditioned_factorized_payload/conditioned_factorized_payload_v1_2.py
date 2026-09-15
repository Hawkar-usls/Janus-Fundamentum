from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path

from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw, RawBasisInputError
from research.tools.apma_bucket_common_core import common_core_semijoin_prefilter as cc_v1
from research.tools.apma_bucket_common_core import common_core_semijoin_prefilter_v1_1 as cc_v11
from research.tools.apma_bucket_conditioned_factorized_payload import conditioned_factorized_payload as v1

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-BUCKET-UNIQUE-CORE-CONDITIONED-FACTORIZED-PAYLOAD-CANDIDATE-2026-09-15-v1.2"
AUTHORITY = "CANDIDATE_SUCCESSOR_REPAIR__SCOPE_AUDIT_WRAPPER_ONLY__NO_SCIENTIFIC_PROMOTION"
PREREG = Path("research/TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_CONDITIONED_FACTORIZED_PAYLOAD_V1_2_PREREGISTRATION_2026-09-15.json")
PREREG_BLOB = "8e938e73b5ebec8deba25d4db05563988a560330"
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
        "v12_prereg_blob": blob(r / PREREG) == PREREG_BLOB,
        "v12_prereg_frozen": p.get("status") == "FROZEN_BEFORE_V1_2_SCOPE_AUDIT_WRAPPER",
        "repair_class": p.get("repair_class") == "INCOMPLETE_COVERAGE_OUT_OF_SCOPE_GUARD_TEST_RESCOPING_AFTER_TWO_RAW_CONTROL_REACHABILITY_FAILURES",
        "v1_candidate_blob": blob(r / V1) == V1_BLOB,
    }
    return {"ok": all(checks.values()), "checks": checks}


def firewall() -> dict:
    return v1.firewall()


def coverage_admission_guard(ready: dict) -> dict:
    bucket_ids = [str(f["id"]) for f in ready.get("bucket", [])]
    target_ids = [f"orig:{int(gi)}" for gi in ready.get("component", [])]
    if bucket_ids != target_ids:
        return {
            "status": "OPEN_INCOMPLETE_TARGET_COMPONENT_COVERAGE",
            "bucket_factor_ids": bucket_ids,
            "target_factor_ids": target_ids,
            "portfolio_construction_calls": 0,
            "bucket_cartesian_combinations_enumerated": 0,
            "scientific_promotion": False,
        }
    return {
        "status": "PASS_COMPLETE_TARGET_COMPONENT_COVERAGE_ADMISSION_PRECONDITION",
        "bucket_factor_ids": bucket_ids,
        "target_factor_ids": target_ids,
        "portfolio_construction_calls": 0,
        "bucket_cartesian_combinations_enumerated": 0,
        "scientific_promotion": False,
    }


def valid_and_forged_ready_receipts() -> dict:
    raw = cc_v1.filtered_still_overbudget_control()
    predecessor = cc_v11.explain(raw)
    valid = cc_v11.first_failed_original_bucket_v11(raw)
    if predecessor.get("status") != "OPEN_COMMON_CORE_FILTERED_BUCKET_STILL_OVER_L2" or valid.get("status") != "READY":
        return {"status": "HALT_VALID_STICKY_PREDECESSOR_NOT_AVAILABLE", "predecessor": predecessor.get("status"), "ready": valid.get("status")}
    canonical = valid["canonical"]
    outside = [gi for gi in range(len(canonical["constraints"])) if gi not in set(valid["component"])]
    if not outside:
        return {"status": "HALT_NO_OUTSIDE_CANONICAL_RELATION_FOR_FORGED_RECEIPT"}
    forged = deepcopy(valid)
    forged["component"] = list(valid["component"]) + [int(outside[0])]
    return {
        "status": "READY",
        "predecessor_status": predecessor.get("status"),
        "valid": valid,
        "forged": forged,
        "appended_existing_relation_index": int(outside[0]),
    }


def explain(raw: dict) -> dict:
    g = source_guard()
    if not g["ok"]:
        return {"artifact_id": ARTIFACT_ID, "status": "HALT_SOURCE_GUARD", "source_guard": g, "scientific_firewall": firewall()}
    try:
        canonicalize_raw(raw)
    except RawBasisInputError as exc:
        return {"artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "status": "REJECT_RAW_INPUT", "reason": str(exc), "source_guard": g, "scientific_firewall": firewall()}
    old = v1.explain(raw)
    return {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "status": old.get("status"),
        "source_guard": g,
        "frozen_v1_result": old,
        "scientific_firewall": firewall(),
    }


def main() -> None:
    receipts = valid_and_forged_ready_receipts()
    valid_guard = coverage_admission_guard(receipts["valid"]) if receipts.get("status") == "READY" else None
    forged_guard = coverage_admission_guard(receipts["forged"]) if receipts.get("status") == "READY" else None
    print(json.dumps({
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "source_guard": source_guard(),
        "receipt_status": receipts.get("status"),
        "predecessor_status": receipts.get("predecessor_status"),
        "valid_guard": valid_guard,
        "forged_guard": forged_guard,
        "positive_sticky": explain(cc_v1.filtered_still_overbudget_control()),
        "scientific_firewall": firewall(),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
