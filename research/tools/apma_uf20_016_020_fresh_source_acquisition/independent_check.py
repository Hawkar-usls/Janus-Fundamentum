from __future__ import annotations

import argparse
import hashlib
import json
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
PRIMARY_REPO = "Jany26/tree-aut-lib"
VERIFY_REPO = "dncarley/MolecularSimulation"
PRIMARY_PREFIX = "benchmark/dimacs/uf20"
VERIFY_PREFIX = "data/uf20-91"
USER_AGENT = "Janus-Fundamentum-source-acquisition-independent-check/1.0"


def fetch_bytes(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()


def raw_url(repo: str, commit: str, prefix: str, filename: str) -> str:
    return f"https://raw.githubusercontent.com/{repo}/{commit}/{prefix}/{filename}"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def parse_dimacs(data: bytes) -> dict[str, Any]:
    text = data.decode("utf-8")
    header = None
    tokens: list[int] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("c"):
            continue
        if line.startswith("p"):
            parts = line.split()
            if len(parts) != 4 or parts[:2] != ["p", "cnf"] or header is not None:
                raise RuntimeError(f"BAD_HEADER:{line}")
            header = (int(parts[2]), int(parts[3]))
        else:
            tokens.extend(int(x) for x in line.split())
    if header != (20, 91):
        raise RuntimeError(f"BAD_COUNTS:{header}")
    clauses: list[tuple[int, int, int]] = []
    current: list[int] = []
    for x in tokens:
        if x == 0:
            if len(current) != 3 or any(abs(y) < 1 or abs(y) > 20 for y in current):
                raise RuntimeError(f"BAD_CLAUSE:{current}")
            clauses.append(tuple(current))
            current.clear()
        else:
            current.append(x)
    if current or len(clauses) != 91:
        raise RuntimeError(f"BAD_CLAUSE_STREAM:{len(clauses)}:{current}")
    canonical = json.dumps([list(c) for c in clauses], separators=(",", ":")).encode()
    return {"clauses": clauses, "canonical_formula_sha256": sha256(canonical)}


def check(candidate: dict[str, Any]) -> dict[str, Any]:
    primary_commit = str(candidate["primary_resolved_commit"])
    verification_commit = str(candidate["verification_resolved_commit"])
    expected_sources = [f"UF20_{i:03d}" for i in range(16, 21)]
    candidate_rows = {row["source"]: row for row in candidate["source_receipts"]}
    checks: dict[str, bool] = {
        "candidate_verdict": candidate.get("verdict") == "PASS_FRESH_SOURCE_ACQUISITION_AND_DUAL_MIRROR_CANONICAL_FREEZE",
        "exact_reserved_source_set": sorted(candidate_rows) == expected_sources,
        "source_count_five": len(candidate_rows) == 5,
        "candidate_no_wl": candidate.get("machine_receipt", {}).get("wl_values_computed") == 0,
        "candidate_no_portfolio": candidate.get("machine_receipt", {}).get("portfolio_replays") == 0,
        "candidate_no_solver": candidate.get("machine_receipt", {}).get("solver_invocations") == 0,
        "candidate_no_routes": candidate.get("machine_receipt", {}).get("route_labels_computed") == 0,
    }
    independently_recomputed = []

    for index in range(16, 21):
        source = f"UF20_{index:03d}"
        filename = f"uf20-{index:03d}.cnf"
        row = candidate_rows[source]
        purl = raw_url(PRIMARY_REPO, primary_commit, PRIMARY_PREFIX, filename)
        vurl = raw_url(VERIFY_REPO, verification_commit, VERIFY_PREFIX, filename)
        primary = fetch_bytes(purl)
        verification = fetch_bytes(vurl)
        p = parse_dimacs(primary)
        v = parse_dimacs(verification)
        local_path = ROOT / f"research/source_data/SATLIB_UF20_{index:03d}_2026-09-17.cnf"
        local = local_path.read_bytes()
        recomputed = {
            "source": source,
            "primary_size_bytes": len(primary),
            "primary_git_blob_sha1": git_blob_sha1(primary),
            "primary_raw_sha256": sha256(primary),
            "verification_size_bytes": len(verification),
            "verification_git_blob_sha1": git_blob_sha1(verification),
            "verification_raw_sha256": sha256(verification),
            "canonical_formula_sha256": p["canonical_formula_sha256"],
            "ordered_clause_sequence_equal_between_mirrors": p["clauses"] == v["clauses"],
            "local_primary_bytes_exact": local == primary,
        }
        independently_recomputed.append(recomputed)
        checks[f"{source}_primary_hashes"] = (
            row["primary"]["size_bytes"] == len(primary)
            and row["primary"]["git_blob_sha1"] == git_blob_sha1(primary)
            and row["primary"]["raw_sha256"] == sha256(primary)
            and row["primary"]["resolved_commit"] == primary_commit
            and row["primary"]["raw_url"] == purl
        )
        checks[f"{source}_verification_hashes"] = (
            row["verification"]["size_bytes"] == len(verification)
            and row["verification"]["git_blob_sha1"] == git_blob_sha1(verification)
            and row["verification"]["raw_sha256"] == sha256(verification)
            and row["verification"]["resolved_commit"] == verification_commit
            and row["verification"]["raw_url"] == vurl
        )
        checks[f"{source}_dimacs_20_91_3"] = row["dimacs"] == {"variables": 20, "clauses": 91, "arity": 3}
        checks[f"{source}_canonical_hash"] = row["canonical_formula_sha256"] == p["canonical_formula_sha256"] == v["canonical_formula_sha256"]
        checks[f"{source}_mirror_ordered_equal"] = p["clauses"] == v["clauses"] and row["ordered_clause_sequence_equal_between_mirrors"] is True
        checks[f"{source}_local_primary_exact"] = local == primary

    ok = all(checks.values())
    return {
        "artifact_id": "JANUS-TRUMP-UF20-016-020-FRESH-SOURCE-ACQUISITION-INDEPENDENT-CHECK-2026-09-17-v1.0",
        "verdict": "PASS_INDEPENDENT_FRESH_SOURCE_ACQUISITION_VERIFICATION" if ok else "FAIL_INDEPENDENT_FRESH_SOURCE_ACQUISITION_VERIFICATION",
        "checks": checks,
        "independently_recomputed": independently_recomputed,
        "candidate_imported": False,
        "wl_values_computed": 0,
        "portfolio_replays": 0,
        "solver_invocations": 0,
        "route_labels_computed": 0,
        "scientific_firewall": {"P_VS_NP": "OPEN", "GENERAL_SAT_IN_P": "NOT_PROVED"},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True)
    args = parser.parse_args()
    candidate = json.loads(Path(args.candidate).read_text())
    result = check(candidate)
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    raise SystemExit(0 if result["verdict"].startswith("PASS_") else 1)


if __name__ == "__main__":
    main()
