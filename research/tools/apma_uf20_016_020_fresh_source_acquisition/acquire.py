from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
SOURCES = [16, 17, 18, 19, 20]
PRIMARY_REPO = "Jany26/tree-aut-lib"
VERIFY_REPO = "dncarley/MolecularSimulation"
PRIMARY_PREFIX = "benchmark/dimacs/uf20"
VERIFY_PREFIX = "data/uf20-91"
REF = "master"
USER_AGENT = "Janus-Fundamentum-source-acquisition/1.0"


def fetch_bytes(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()


def resolve_ref(repo: str, ref: str) -> str:
    data = json.loads(fetch_bytes(f"https://api.github.com/repos/{repo}/commits/{ref}").decode("utf-8"))
    sha = str(data["sha"])
    if len(sha) != 40:
        raise RuntimeError(f"BAD_RESOLVED_REF:{repo}:{sha}")
    return sha


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
            if len(parts) != 4 or parts[0] != "p" or parts[1] != "cnf":
                raise RuntimeError(f"BAD_DIMACS_HEADER:{line}")
            if header is not None:
                raise RuntimeError("MULTIPLE_DIMACS_HEADERS")
            header = (int(parts[2]), int(parts[3]))
            continue
        tokens.extend(int(x) for x in line.split())
    if header != (20, 91):
        raise RuntimeError(f"BAD_DIMACS_COUNTS:{header}")
    clauses: list[list[int]] = []
    current: list[int] = []
    for value in tokens:
        if value == 0:
            if len(current) != 3:
                raise RuntimeError(f"NON_TERNARY_CLAUSE:{current}")
            if any(abs(lit) < 1 or abs(lit) > 20 for lit in current):
                raise RuntimeError(f"LITERAL_OUT_OF_RANGE:{current}")
            clauses.append(current)
            current = []
        else:
            current.append(value)
    if current:
        raise RuntimeError("UNTERMINATED_DIMACS_CLAUSE")
    if len(clauses) != 91:
        raise RuntimeError(f"BAD_CLAUSE_COUNT:{len(clauses)}")
    canonical = json.dumps(clauses, separators=(",", ":")).encode("utf-8")
    return {
        "variables": 20,
        "clauses": 91,
        "arity": 3,
        "ordered_clauses": clauses,
        "canonical_formula_sha256": sha256(canonical),
    }


def main() -> dict[str, Any]:
    primary_commit = resolve_ref(PRIMARY_REPO, REF)
    verification_commit = resolve_ref(VERIFY_REPO, REF)
    staged: list[tuple[Path, bytes]] = []
    receipts = []

    for index in SOURCES:
        filename = f"uf20-{index:03d}.cnf"
        primary_url = raw_url(PRIMARY_REPO, primary_commit, PRIMARY_PREFIX, filename)
        verify_url = raw_url(VERIFY_REPO, verification_commit, VERIFY_PREFIX, filename)
        primary = fetch_bytes(primary_url)
        verification = fetch_bytes(verify_url)
        p = parse_dimacs(primary)
        v = parse_dimacs(verification)
        ordered_equal = p["ordered_clauses"] == v["ordered_clauses"]
        if not ordered_equal:
            raise RuntimeError(f"MIRROR_CANONICAL_ORDERED_CLAUSE_MISMATCH:UF20_{index:03d}")

        destination = ROOT / f"research/source_data/SATLIB_UF20_{index:03d}_2026-09-17.cnf"
        staged.append((destination, primary))
        receipts.append({
            "source": f"UF20_{index:03d}",
            "upstream_filename": filename,
            "repository_path": str(destination.relative_to(ROOT)),
            "primary": {
                "repository": PRIMARY_REPO,
                "requested_ref": REF,
                "resolved_commit": primary_commit,
                "raw_url": primary_url,
                "size_bytes": len(primary),
                "git_blob_sha1": git_blob_sha1(primary),
                "raw_sha256": sha256(primary),
            },
            "verification": {
                "repository": VERIFY_REPO,
                "requested_ref": REF,
                "resolved_commit": verification_commit,
                "raw_url": verify_url,
                "size_bytes": len(verification),
                "git_blob_sha1": git_blob_sha1(verification),
                "raw_sha256": sha256(verification),
            },
            "dimacs": {"variables": 20, "clauses": 91, "arity": 3},
            "canonical_formula_sha256": p["canonical_formula_sha256"],
            "ordered_clause_sequence_equal_between_mirrors": True,
        })

    for destination, data in staged:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)

    return {
        "artifact_id": "JANUS-TRUMP-UF20-016-020-FRESH-SOURCE-ACQUISITION-CANDIDATE-2026-09-17-v1.0",
        "gate": "TRUMP_UF20_016_020_FRESH_SOURCE_ACQUISITION_AND_DUAL_MIRROR_FREEZE_GATE",
        "authority": "SOURCE_ACQUISITION_AND_PROVENANCE_FREEZE_ONLY__NO_WL_NO_PORTFOLIO_NO_SOLVER",
        "verdict": "PASS_FRESH_SOURCE_ACQUISITION_AND_DUAL_MIRROR_CANONICAL_FREEZE",
        "reserved_sources": [f"UF20_{i:03d}" for i in SOURCES],
        "primary_resolved_commit": primary_commit,
        "verification_resolved_commit": verification_commit,
        "source_receipts": receipts,
        "machine_receipt": {
            "source_count": len(receipts),
            "mirror_fetch_count": len(receipts) * 2,
            "wl_values_computed": 0,
            "portfolio_replays": 0,
            "solver_invocations": 0,
            "route_labels_computed": 0,
            "new_solver_rules": 0,
            "new_action_rules": 0,
            "new_carrier_mechanisms": 0,
            "new_reduction_mechanisms": 0,
        },
        "scientific_firewall": {
            "P_VS_NP": "OPEN",
            "GENERAL_SAT_IN_P": "NOT_PROVED",
            "CONNECTED_MIXED_CORE_SOLVED": "NO",
            "GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY": "NOT_PROVED",
        },
    }


if __name__ == "__main__":
    print(json.dumps(main(), sort_keys=True, separators=(",", ":")))
