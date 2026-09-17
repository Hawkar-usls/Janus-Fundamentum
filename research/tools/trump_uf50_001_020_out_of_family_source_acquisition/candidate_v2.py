from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research.tools.trump_uf50_001_020_out_of_family_source_acquisition import candidate as frozen_v1

ROOT = Path(__file__).resolve().parents[3]
ERRATUM = ROOT / "research/TRUMP_UF50_001_020_OUT_OF_FAMILY_SOURCE_ACQUISITION_VERIFICATION_PATH_ERRATUM_2026-09-18_v1.0.json"
ERRATUM_REVIEW = ROOT / "research/TRUMP_UF50_001_020_OUT_OF_FAMILY_SOURCE_ACQUISITION_VERIFICATION_PATH_ERRATUM_REVIEW_2026-09-18_v1.0.json"
V1 = ROOT / "research/tools/trump_uf50_001_020_out_of_family_source_acquisition/candidate.py"
EXPECTED = {
    frozen_v1.RESERVATION: "cb21ee36a96368ea7f7b8b1e2fdf17788cda8a65",
    frozen_v1.PREREG: "19e15c35aef3b1e89fc40fe17daf160923332d2f",
    frozen_v1.REVIEW: "fa67d3aa9e511f9938ec69150523f1f26780fef3",
    V1: "be1591ecb6b8fa7e7045fc5ddef6d1b4117e31ca",
    ERRATUM: "862e38d2e0e78e833ae59783201eb2c44e72596d",
    ERRATUM_REVIEW: "fb9893b2e5c02e02a45dde9465051c787193a436",
}
VERIFY_BASE = "data/uniform-random-3-sat/uf50-218"


def guard() -> dict[str, Any]:
    bindings = {str(p.relative_to(ROOT)): frozen_v1.blob(p) == h for p, h in EXPECTED.items()}
    erratum = json.loads(ERRATUM.read_text())
    review = json.loads(ERRATUM_REVIEW.read_text())
    base = frozen_v1.guard()
    checks = {
        "original_authorities": base["ok"],
        "v2_authority_bindings": all(bindings.values()),
        "erratum_status": erratum.get("status") == "FROZEN_PROVENANCE_PATH_BINDING_CORRECTION_ONLY",
        "erratum_authorized": erratum.get("authorization") == "REIMPLEMENT_ACQUISITION_CANDIDATE_AND_INDEPENDENT_CHECKER_WITH_ONLY_THE_CORRECTED_VERIFICATION_DIRECTORY_BINDING_AND_RERUN_THE_SAME_TWENTY_IDENTITIES",
        "review_authorized": review.get("review_verdict") == "PASS_CLEAN_UF50_VERIFICATION_PATH_ERRATUM__AUTHORIZED_TO_RERUN_ACQUISITION_WITH_UNSPLIT_VERIFICATION_DIRECTORY_ONLY",
        "same_order": frozen_v1.ORDER == tuple(f"UF50_{i:03d}" for i in range(1, 21)),
    }
    return {"ok": all(checks.values()), "checks": checks, "bindings": bindings, "original_guard": base}


def main() -> dict[str, Any]:
    authority = guard()
    if not authority["ok"]:
        return {"verdict": "HALT_V2_AUTHORITY_BINDING_FAILURE", "authority_guard": authority, "resource_receipt": frozen_v1.resource_receipt(0)}
    rows = []
    try:
        for source in frozen_v1.ORDER:
            n = int(source.split("_")[1])
            t = frozen_v1.token(n)
            primary_path = f"benchmark/dimacs/dimacs-50var-218c/uf50-{t}.cnf"
            verification_path = f"{VERIFY_BASE}/uf50-{t}.cnf"
            primary = frozen_v1.fetch(frozen_v1.PRIMARY_REPO, frozen_v1.PRIMARY_COMMIT, primary_path)
            verification = frozen_v1.fetch(frozen_v1.VERIFY_REPO, frozen_v1.VERIFY_COMMIT, verification_path)
            pc, ph = frozen_v1.parse(primary)
            vc, vh = frozen_v1.parse(verification)
            if pc != vc or ph != vh:
                return {
                    "verdict": "HALT_ORDERED_CLAUSE_OR_CANONICAL_FORMULA_MISMATCH",
                    "source": source,
                    "rows": rows,
                    "resource_receipt": frozen_v1.resource_receipt(len(rows) * 2 + 2),
                }
            output = ROOT / f"research/source_data/SATLIB_UF50_{n:03d}_2026-09-18.cnf"
            if output.exists():
                return {
                    "verdict": "HALT_COMMITTED_COPY_BINDING_FAILURE",
                    "source": source,
                    "reason": "TARGET_PATH_PREEXISTS",
                    "rows": rows,
                    "resource_receipt": frozen_v1.resource_receipt(len(rows) * 2 + 2),
                }
            output.write_bytes(primary)
            rows.append({
                "source": source,
                "numeric_index": n,
                "remote_filename": f"uf50-{t}.cnf",
                "committed_copy_path": str(output.relative_to(ROOT)),
                "variables": 50,
                "clauses": 218,
                "arity": 3,
                "primary_repo": frozen_v1.PRIMARY_REPO,
                "primary_commit": frozen_v1.PRIMARY_COMMIT,
                "primary_path": primary_path,
                "primary_git_blob": frozen_v1.blob_bytes(primary),
                "primary_raw_sha256": frozen_v1.sha256(primary),
                "verification_repo": frozen_v1.VERIFY_REPO,
                "verification_commit": frozen_v1.VERIFY_COMMIT,
                "verification_path": verification_path,
                "verification_git_blob": frozen_v1.blob_bytes(verification),
                "verification_raw_sha256": frozen_v1.sha256(verification),
                "canonical_formula_sha256": ph,
                "ordered_clause_sequence_equal": True,
                "raw_bytes_primary_equal_verification": primary == verification,
                "computed_committed_git_blob": frozen_v1.blob_bytes(primary),
                "independent_verified": False,
                "status": "SOURCE_STAGED_FOR_INDEPENDENT_VERIFICATION",
            })
    except Exception as exc:
        return {
            "verdict": "HALT_SOURCE_MISSING_OR_FETCH_FAILURE",
            "error": f"{type(exc).__name__}:{exc}",
            "rows": rows,
            "resource_receipt": frozen_v1.resource_receipt(len(rows) * 2),
        }
    return {
        "artifact_id": "JANUS-TRUMP-UF50-001-020-OUT-OF-FAMILY-SOURCE-ACQUISITION-CANDIDATE-V2-2026-09-18-v1.0",
        "verdict": "PASS_UF50_001_020_DUAL_MIRROR_SOURCE_ACQUISITION_AND_FORMULA_FREEZE",
        "authority_guard": authority,
        "verification_path_correction": "TRAIN_SPLIT_TO_UNSPLIT_DIRECTORY_ONLY",
        "source_receipts": rows,
        "resource_receipt": frozen_v1.resource_receipt(40),
        "scientific_firewall": {
            "STRUCTURAL_VALUES_COMPUTED": 0,
            "GENERAL_SAT_IN_P": "NOT_PROVED",
            "P_VS_NP": "OPEN",
        },
    }


if __name__ == "__main__":
    print(json.dumps(main(), sort_keys=True, separators=(",", ":")))
