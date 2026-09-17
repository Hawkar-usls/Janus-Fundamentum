from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
RESERVATION = ROOT / "research/TRUMP_UF50_001_020_OUT_OF_FAMILY_WL_ORBIT_FALSIFIER_PANEL_RESERVATION_PREREGISTRATION_2026-09-18_v1.0.json"
PREREG = ROOT / "research/TRUMP_UF50_001_020_OUT_OF_FAMILY_SOURCE_ACQUISITION_PREREGISTRATION_2026-09-18_v1.0.json"
REVIEW = ROOT / "research/TRUMP_UF50_001_020_OUT_OF_FAMILY_SOURCE_ACQUISITION_REVIEW_2026-09-18_v1.0.json"
EXPECTED = {
    RESERVATION: "cb21ee36a96368ea7f7b8b1e2fdf17788cda8a65",
    PREREG: "19e15c35aef3b1e89fc40fe17daf160923332d2f",
    REVIEW: "fa67d3aa9e511f9938ec69150523f1f26780fef3",
}
PRIMARY_REPO = "Jany26/tree-aut-lib"
PRIMARY_COMMIT = "6cd58ade6de0a5c05511deb76c261ee75356ff31"
VERIFY_REPO = "dmeoli/NeuroSAT"
VERIFY_COMMIT = "568b022fc0c56e7e24fe08c012753ef29c60938e"
ORDER = tuple(f"UF50_{i:03d}" for i in range(1, 21))


def token(n: int) -> str:
    return "0" + str(n)


def blob_bytes(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def blob(path: Path) -> str:
    return blob_bytes(path.read_bytes())


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch(repo: str, commit: str, path: str) -> bytes:
    req = urllib.request.Request(
        f"https://raw.githubusercontent.com/{repo}/{commit}/{path}",
        headers={"User-Agent": "Janus-Fundamentum-UF50-001-020-source-freeze/1.0"},
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()


def parse(data: bytes) -> tuple[list[list[int]], str]:
    nvars = nclauses = None
    clauses: list[list[int]] = []
    for raw in data.decode("utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("c") or line in {"%", "0"}:
            continue
        if line.startswith("p "):
            parts = line.split()
            assert parts[:2] == ["p", "cnf"] and len(parts) == 4
            nvars, nclauses = int(parts[2]), int(parts[3])
            continue
        values = [int(x) for x in line.split()]
        assert values and values[-1] == 0
        clause = values[:-1]
        assert len(clause) == 3
        assert len({abs(x) for x in clause}) == 3
        assert all(1 <= abs(x) <= 50 for x in clause)
        clauses.append(clause)
    assert nvars == 50 and nclauses == 218 and len(clauses) == 218
    canonical = "".join(" ".join(map(str, c)) + " 0\n" for c in clauses).encode("ascii")
    return clauses, sha256(canonical)


def resource_receipt(fetches: int) -> dict[str, int]:
    return {
        "remote_source_fetches": fetches,
        "sources_reserved": 20,
        "projected_raw_computations": 0,
        "pendant_target_computations": 0,
        "wl_computations": 0,
        "direct_transposition_checks": 0,
        "full_transposition_searches": 0,
        "portfolio_replays": 0,
        "e3_witness_computations": 0,
        "solver_invocations": 0,
        "external_truth_or_metrics_reads": 0,
    }


def guard() -> dict[str, Any]:
    bindings = {str(p.relative_to(ROOT)): blob(p) == h for p, h in EXPECTED.items()}
    reservation = json.loads(RESERVATION.read_text())
    prereg = json.loads(PREREG.read_text())
    review = json.loads(REVIEW.read_text())
    expected_indices = list(range(1, 21))
    checks = {
        "authority_bindings": all(bindings.values()),
        "reservation_status": reservation.get("status") == "FROZEN_BEFORE_SOURCE_CONTENT_ACQUISITION_OR_ANY_STRUCTURAL_VALUE_ON_THE_OUT_OF_FAMILY_PANEL",
        "family": reservation.get("panel", {}).get("family_label") == "SATLIB_UF50_218",
        "numeric_indices": reservation.get("panel", {}).get("numeric_indices") == expected_indices,
        "panel_size": reservation.get("panel", {}).get("panel_size") == 20,
        "prereg_status": prereg.get("status") == "FROZEN_BEFORE_FIRST_RESERVED_UF50_CNF_CONTENT_FETCH_IN_THIS_LINEAGE",
        "review_authorized": review.get("review_verdict") == "PASS_CLEAN_UF50_001_020_DUAL_MIRROR_SOURCE_ACQUISITION_SPEC__AUTHORIZED_TO_FETCH_FREEZE_AND_VERIFY_ALL_TWENTY_ONLY",
        "filename_examples": token(1) == "01" and token(10) == "010" and token(20) == "020",
    }
    return {"ok": all(checks.values()), "checks": checks, "bindings": bindings}


def main() -> dict[str, Any]:
    authority = guard()
    if not authority["ok"]:
        return {"verdict": "HALT_AUTHORITY_OR_RESERVATION_BINDING_FAILURE", "authority_guard": authority, "resource_receipt": resource_receipt(0)}

    rows: list[dict[str, Any]] = []
    try:
        for source in ORDER:
            n = int(source.split("_")[1])
            t = token(n)
            primary_path = f"benchmark/dimacs/dimacs-50var-218c/uf50-{t}.cnf"
            verification_path = f"data/uniform-random-3-sat/train/uf50-218/uf50-{t}.cnf"
            primary = fetch(PRIMARY_REPO, PRIMARY_COMMIT, primary_path)
            verification = fetch(VERIFY_REPO, VERIFY_COMMIT, verification_path)
            primary_clauses, primary_formula_hash = parse(primary)
            verification_clauses, verification_formula_hash = parse(verification)
            if primary_clauses != verification_clauses or primary_formula_hash != verification_formula_hash:
                return {
                    "verdict": "HALT_ORDERED_CLAUSE_OR_CANONICAL_FORMULA_MISMATCH",
                    "source": source,
                    "rows": rows,
                    "resource_receipt": resource_receipt(len(rows) * 2 + 2),
                }
            output = ROOT / f"research/source_data/SATLIB_UF50_{n:03d}_2026-09-18.cnf"
            if output.exists():
                return {
                    "verdict": "HALT_COMMITTED_COPY_BINDING_FAILURE",
                    "source": source,
                    "reason": "TARGET_PATH_PREEXISTS",
                    "rows": rows,
                    "resource_receipt": resource_receipt(len(rows) * 2 + 2),
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
                "primary_repo": PRIMARY_REPO,
                "primary_commit": PRIMARY_COMMIT,
                "primary_path": primary_path,
                "primary_git_blob": blob_bytes(primary),
                "primary_raw_sha256": sha256(primary),
                "verification_repo": VERIFY_REPO,
                "verification_commit": VERIFY_COMMIT,
                "verification_path": verification_path,
                "verification_git_blob": blob_bytes(verification),
                "verification_raw_sha256": sha256(verification),
                "canonical_formula_sha256": primary_formula_hash,
                "ordered_clause_sequence_equal": True,
                "raw_bytes_primary_equal_verification": primary == verification,
                "computed_committed_git_blob": blob_bytes(primary),
                "independent_verified": False,
                "status": "SOURCE_STAGED_FOR_INDEPENDENT_VERIFICATION",
            })
    except Exception as exc:
        return {
            "verdict": "HALT_SOURCE_MISSING_OR_FETCH_FAILURE",
            "error": f"{type(exc).__name__}:{exc}",
            "rows": rows,
            "resource_receipt": resource_receipt(len(rows) * 2),
        }

    return {
        "artifact_id": "JANUS-TRUMP-UF50-001-020-OUT-OF-FAMILY-SOURCE-ACQUISITION-CANDIDATE-2026-09-18-v1.0",
        "verdict": "PASS_UF50_001_020_DUAL_MIRROR_SOURCE_ACQUISITION_AND_FORMULA_FREEZE",
        "authority_guard": authority,
        "source_receipts": rows,
        "resource_receipt": resource_receipt(40),
        "scientific_firewall": {
            "STRUCTURAL_VALUES_COMPUTED": 0,
            "WL_SUFFICIENCY_WITHOUT_DIRECT_EXACT_CHECK": "NOT_PROVED",
            "GENERAL_SAT_IN_P": "NOT_PROVED",
            "P_VS_NP": "OPEN",
        },
    }


if __name__ == "__main__":
    print(json.dumps(main(), sort_keys=True, separators=(",", ":")))
