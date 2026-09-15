from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from research.tools.apma_bucket_closed_two_factor import independent_checker as v1

VERDICT = v1.VERDICT

PREREG = Path("research/TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_CLOSED_INTERNAL_TWO_FACTOR_F_FACTOR_CARRIER_PREREGISTRATION_2026-09-15.json")
PREREG_BLOB = "1240d183461bfab4defe42df14ffdb2df31396da"
THEOREM = Path("research/TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_CLOSED_INTERNAL_TWO_FACTOR_F_FACTOR_CARRIER_THEOREM_CANDIDATE_2026-09-15.md")
THEOREM_BLOB = "3c3db06ec64f6f130deca98fef0e0f0f060ac562"
PARENT_STATE = Path("registry/TRUMP_CURRENT_STATE_2026-09-15_v3.17.json")
PARENT_STATE_BLOB = "bf871e4e574381373f8c4d207eca9a12c9175ea4"
V1_CHECKER = Path("research/tools/apma_bucket_closed_two_factor/independent_checker.py")
V1_CHECKER_BLOB = "88e9fd6358bca9aeb99cd27bfdfede8d755f33e5"
V1_CANDIDATE = Path("research/tools/apma_bucket_closed_two_factor/closed_two_factor_carrier.py")
V1_CANDIDATE_BLOB = "2e81d4f908deea1c08a6e8c32b0ca26b7cb532eb"
V1_1_CANDIDATE = Path("research/tools/apma_bucket_closed_two_factor/closed_two_factor_carrier_v1_1.py")
V1_1_CANDIDATE_BLOB = "0c4cc3e2798062ec85cfdc945034ead9b7ffbabd"
COMPONENT = Path("research/tools/apma_bucket_closed_two_factor/two_factor_component.py")
COMPONENT_BLOB = "06a8980dc56d8d098618ddee0fe74e5b328dcac7"
MATCHING = Path("research/tools/apma_bucket_closed_two_factor/matching_core.py")
MATCHING_BLOB = "8a09164e2ff3277611dfd310331e5792157bf413"


def root() -> Path:
    return Path(__file__).resolve().parents[3]


def git_blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def source_guard() -> dict[str, Any]:
    r = root()
    checks = {
        "prereg_blob": git_blob(r / PREREG) == PREREG_BLOB,
        "theorem_blob": git_blob(r / THEOREM) == THEOREM_BLOB,
        "parent_v3_17_blob": git_blob(r / PARENT_STATE) == PARENT_STATE_BLOB,
        "immutable_v1_checker_blob": git_blob(r / V1_CHECKER) == V1_CHECKER_BLOB,
        "immutable_v1_candidate_blob": git_blob(r / V1_CANDIDATE) == V1_CANDIDATE_BLOB,
        "v1_1_candidate_blob": git_blob(r / V1_1_CANDIDATE) == V1_1_CANDIDATE_BLOB,
        "component_blob": git_blob(r / COMPONENT) == COMPONENT_BLOB,
        "repaired_matching_core_blob": git_blob(r / MATCHING) == MATCHING_BLOB,
    }
    return {"ok": all(checks.values()), "checks": checks}


def check(candidate: dict[str, Any]) -> dict[str, Any]:
    guard = source_guard()
    old_guard = v1.source_guard
    try:
        v1.source_guard = lambda: guard
        out = v1.check(candidate)
    finally:
        v1.source_guard = old_guard
    out["repair_receipt"] = {
        "immutable_v1_checker_blob": V1_CHECKER_BLOB,
        "immutable_v1_candidate_blob": V1_CANDIDATE_BLOB,
        "v1_1_candidate_blob": V1_1_CANDIDATE_BLOB,
        "repaired_matching_core_blob": MATCHING_BLOB,
        "preregistration_changed": False,
        "candidate_helpers_imported": False,
    }
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-json", required=True)
    args = parser.parse_args()
    candidate = json.loads(Path(args.candidate_json).read_text(encoding="utf-8"))
    print(json.dumps(check(candidate), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
