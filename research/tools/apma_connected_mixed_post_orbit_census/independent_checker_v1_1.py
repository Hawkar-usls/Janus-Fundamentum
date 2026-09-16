from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from research.tools.apma_connected_mixed_post_orbit_census import independent_checker as base


ARTIFACT_ID = "JANUS-TRUMP-SOURCE-AUTHORIZED-CONNECTED-MIXED-RAW-POST-ORBIT-PORTFOLIO-OBSTRUCTION-CENSUS-INDEPENDENT-CHECKER-2026-09-16-v1.1"
BASE_CHECKER = Path("research/tools/apma_connected_mixed_post_orbit_census/independent_checker.py")
BASE_CHECKER_BLOB = "786db65a4b1e24529b09abb9af11d760bafdae0e"


def root() -> Path:
    return Path(__file__).resolve().parents[3]


def blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def semantic_raw(raw: dict[str, Any]) -> tuple[Any, ...]:
    rows = []
    for c in raw.get("constraints", []):
        rows.append((
            tuple(int(v) for v in c["scope"]),
            tuple(sorted(tuple(int(x) for x in t) for t in c["allowed"])),
        ))
    return tuple(sorted(rows))


def verify(candidate: dict[str, Any]) -> dict[str, Any]:
    guard = base.source_guard()
    base_blob_ok = blob_sha(root() / BASE_CHECKER) == BASE_CHECKER_BLOB
    independent = base.independent_result()
    crows = {r["raw_semantic_sha256"]: r for r in candidate.get("rows", [])}
    irows = {r["raw_semantic_sha256"]: r for r in independent["rows"]}
    row_checks: dict[str, bool] = {}
    if set(crows) == set(irows):
        for sha in sorted(irows):
            cr, ir = crows[sha], irows[sha]
            row_checks[sha] = (
                cr.get("source_aliases") == ir.get("source_aliases")
                and semantic_raw(cr.get("normalized_raw", {})) == semantic_raw(ir.get("normalized_raw", {}))
                and cr.get("connected") == ir.get("connected")
                and cr.get("mixed_after_exact_normalization") == ir.get("mixed_after_exact_normalization")
                and cr.get("basis_status") == ir.get("basis_status")
                and cr.get("classification") == ir.get("classification")
            )
    candidate_first = None if candidate.get("first_open_obstruction") is None else candidate["first_open_obstruction"].get("raw_semantic_sha256")
    checks = {
        "base_checker_blob": base_blob_ok,
        "source_guard": guard["ok"],
        "candidate_helpers_imported_false": guard["candidate_helpers_imported"] is False,
        "source_entry_count": candidate.get("source_entry_count") == independent["source_entry_count"],
        "unique_raw_count": candidate.get("unique_raw_count") == independent["unique_raw_count"],
        "eligible_count": candidate.get("eligible_connected_mixed_unique_raw_count") == independent["eligible_connected_mixed_unique_raw_count"],
        "open_count": candidate.get("open_post_orbit_obstruction_count") == independent["open_post_orbit_obstruction_count"],
        "verdict": candidate.get("verdict") == independent["verdict"],
        "row_sha_set": set(crows) == set(irows),
        "all_rows_match_semantically": bool(row_checks) and all(row_checks.values()),
        "first_open": candidate_first == independent["first_open_sha"],
    }
    return {
        "artifact_id": ARTIFACT_ID,
        "verified": all(checks.values()),
        "checks": checks,
        "row_checks": row_checks,
        "independent": independent,
        "source_guard": guard,
        "candidate_helpers_imported": False,
        "comparison_rule": "CANONICAL_SEMANTIC_SHA_AND_SCOPE_ALLOWED_TABLES__CONSTRAINT_IDS_IGNORED",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-json", required=True)
    args = parser.parse_args()
    candidate = json.loads(Path(args.candidate_json).read_text(encoding="utf-8").strip().splitlines()[-1])
    out = verify(candidate)
    print(json.dumps(out, sort_keys=True, separators=(",", ":")))
    if not out["verified"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
