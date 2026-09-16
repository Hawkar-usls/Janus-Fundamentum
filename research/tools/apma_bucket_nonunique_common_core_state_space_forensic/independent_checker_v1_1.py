from __future__ import annotations

import argparse
import json
from pathlib import Path

from research.tools.apma_bucket_nonunique_common_core_state_space_forensic import independent_checker as v1

ARTIFACT_ID = "JANUS-TRUMP-NONUNIQUE-COMMON-CORE-STATE-SPACE-FORENSIC-INDEPENDENT-CHECK-2026-09-16-v1.1"
AUTHORITY = "INDEPENDENT_DIAGNOSTIC_CHECK_REPAIR__NO_SCIENTIFIC_PROMOTION"
V1_CHECKER_BLOB = "79c51eaa784b538a3184cdbe1c2bc4c72a5823f8"
IMMUTABLE_FIRST_FAILURE_RUN = 35042004343
IMMUTABLE_FIRST_FAILURE_JOB = 104623675436
IMMUTABLE_FIRST_FAILURE_REASON = "BOOLEAN_POLARITY_BUG__candidate_helpers_imported_FALSE_WAS_FED_DIRECTLY_TO_all_checks_values"


def _v1_blob_ok() -> bool:
    path = Path(v1.__file__).resolve()
    return v1.blob(path) == V1_CHECKER_BLOB


def check(candidate: dict) -> dict:
    base = v1.check(candidate)
    checks = dict(base.get("checks", {}))
    imported_flag = checks.pop("candidate_helpers_imported", None)
    checks["candidate_helpers_not_imported"] = (
        imported_flag is False
        and base.get("candidate_helpers_imported") is False
    )
    checks["v1_checker_blob_frozen"] = _v1_blob_ok()

    out = dict(base)
    out["artifact_id"] = ARTIFACT_ID
    out["authority"] = AUTHORITY
    out["checks"] = checks
    out["repair"] = {
        "class": "IMPLEMENTATION_ONLY_BOOLEAN_POLARITY_REPAIR",
        "v1_checker_blob": V1_CHECKER_BLOB,
        "immutable_first_failure_run": IMMUTABLE_FIRST_FAILURE_RUN,
        "immutable_first_failure_job": IMMUTABLE_FIRST_FAILURE_JOB,
        "immutable_first_failure_reason": IMMUTABLE_FIRST_FAILURE_REASON,
        "candidate_changed": False,
        "preregistration_changed": False,
        "fixture_census_changed": False,
        "scientific_outcome_changed": False,
    }
    out["verdict"] = candidate.get("verdict") if all(checks.values()) else v1.FAIL
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-json", required=True)
    args = parser.parse_args()
    candidate = json.loads(Path(args.candidate_json).read_text(encoding="utf-8").strip().splitlines()[-1])
    print(json.dumps(check(candidate), sort_keys=True))


if __name__ == "__main__":
    main()
