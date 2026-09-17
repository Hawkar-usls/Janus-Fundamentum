from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CANDIDATE = ROOT / "research/tools/trump_uf50_001_020_out_of_family_source_acquisition/candidate.py"
RESERVATION = ROOT / "research/TRUMP_UF50_001_020_OUT_OF_FAMILY_WL_ORBIT_FALSIFIER_PANEL_RESERVATION_PREREGISTRATION_2026-09-18_v1.0.json"
PREREG = ROOT / "research/TRUMP_UF50_001_020_OUT_OF_FAMILY_SOURCE_ACQUISITION_PREREGISTRATION_2026-09-18_v1.0.json"
REVIEW = ROOT / "research/TRUMP_UF50_001_020_OUT_OF_FAMILY_SOURCE_ACQUISITION_REVIEW_2026-09-18_v1.0.json"
EXPECTED = {
    CANDIDATE: "be1591ecb6b8fa7e7045fc5ddef6d1b4117e31ca",
    RESERVATION: "cb21ee36a96368ea7f7b8b1e2fdf17788cda8a65",
    PREREG: "19e15c35aef3b1e89fc40fe17daf160923332d2f",
    REVIEW: "fa67d3aa9e511f9938ec69150523f1f26780fef3",
}
CANDIDATE_MODULE = "research.tools.trump_uf50_001_020_out_of_family_source_acquisition.candidate"
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
        headers={"User-Agent": "Janus-UF50-independent-source-freeze-check/1.0"},
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()


def parse(data: bytes):
    variables = clauses_declared = None
    clauses = []
    for raw in data.decode("utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("c") or line in {"%", "0"}:
            continue
        if line.startswith("p "):
            p = line.split()
            if len(p) != 4 or p[0] != "p" or p[1] != "cnf":
                raise ValueError("bad DIMACS header")
            variables, clauses_declared = int(p[2]), int(p[3])
            continue
        vals = tuple(int(x) for x in line.split())
        if not vals or vals[-1] != 0:
            raise ValueError("unterminated clause")
        clause = vals[:-1]
        if len(clause) != 3 or len({abs(x) for x in clause}) != 3 or any(abs(x) < 1 or abs(x) > 50 for x in clause):
            raise ValueError("not canonical 3-CNF clause")
        clauses.append(clause)
    if variables != 50 or clauses_declared != 218 or len(clauses) != 218:
        raise ValueError(f"contract mismatch variables={variables} declared={clauses_declared} parsed={len(clauses)}")
    canonical = "".join(" ".join(map(str, c)) + " 0\n" for c in clauses).encode("ascii")
    return clauses, sha256(canonical)


def main(candidate_json: Path):
    bindings = {str(p.relative_to(ROOT)): blob(p) == h for p, h in EXPECTED.items()}
    if not all(bindings.values()):
        return {"verdict": "HALT_INDEPENDENT_AUTHORITY_BINDING_FAILURE", "bindings": bindings}
    if CANDIDATE_MODULE in sys.modules:
        return {"verdict": "HALT_INDEPENDENT_CANDIDATE_IMPORT_VIOLATION"}

    candidate = json.loads(candidate_json.read_text())
    if candidate.get("verdict") != "PASS_UF50_001_020_DUAL_MIRROR_SOURCE_ACQUISITION_AND_FORMULA_FREEZE":
        return {"verdict": "HALT_CANDIDATE_DID_NOT_PASS", "candidate_verdict": candidate.get("verdict")}
    rows = candidate.get("source_receipts", [])
    if tuple(r.get("source") for r in rows) != ORDER or len(rows) != 20:
        return {"verdict": "FAIL_INDEPENDENT_SOURCE_ORDER_OR_COUNT_MISMATCH"}

    verified = []
    failures = []
    for row in rows:
        source = row["source"]
        n = int(source.split("_")[1])
        t = token(n)
        primary_path = f"benchmark/dimacs/dimacs-50var-218c/uf50-{t}.cnf"
        verification_path = f"data/uniform-random-3-sat/train/uf50-218/uf50-{t}.cnf"
        try:
            primary = fetch(PRIMARY_REPO, PRIMARY_COMMIT, primary_path)
            verification = fetch(VERIFY_REPO, VERIFY_COMMIT, verification_path)
            pc, ph = parse(primary)
            vc, vh = parse(verification)
            staged_path = ROOT / row["committed_copy_path"]
            staged = staged_path.read_bytes()
            sc, sh = parse(staged)
            checks = {
                "ordered_primary_verification": pc == vc,
                "ordered_primary_staged": pc == sc,
                "formula_hash_three_way": ph == vh == sh == row.get("canonical_formula_sha256"),
                "primary_blob": blob_bytes(primary) == row.get("primary_git_blob"),
                "verification_blob": blob_bytes(verification) == row.get("verification_git_blob"),
                "staged_blob": blob_bytes(staged) == row.get("computed_committed_git_blob"),
                "primary_sha256": sha256(primary) == row.get("primary_raw_sha256"),
                "verification_sha256": sha256(verification) == row.get("verification_raw_sha256"),
                "contract": row.get("variables") == 50 and row.get("clauses") == 218 and row.get("arity") == 3,
                "paths": row.get("primary_path") == primary_path and row.get("verification_path") == verification_path,
            }
            ok = all(checks.values())
            verified.append({"source": source, "checks": checks, "pass": ok, "committed_git_blob": blob_bytes(staged)})
            if not ok:
                failures.append(source)
        except Exception as exc:
            failures.append(source)
            verified.append({"source": source, "pass": False, "error": f"{type(exc).__name__}:{exc}"})

    rr = candidate.get("resource_receipt", {})
    blind = {
        "projected_raw_computations": rr.get("projected_raw_computations") == 0,
        "pendant_target_computations": rr.get("pendant_target_computations") == 0,
        "wl_computations": rr.get("wl_computations") == 0,
        "direct_transposition_checks": rr.get("direct_transposition_checks") == 0,
        "full_transposition_searches": rr.get("full_transposition_searches") == 0,
        "portfolio_replays": rr.get("portfolio_replays") == 0,
        "e3_witness_computations": rr.get("e3_witness_computations") == 0,
        "solver_invocations": rr.get("solver_invocations") == 0,
        "external_truth_or_metrics_reads": rr.get("external_truth_or_metrics_reads") == 0,
    }
    ok = not failures and all(blind.values()) and CANDIDATE_MODULE not in sys.modules
    return {
        "artifact_id": "JANUS-TRUMP-UF50-001-020-OUT-OF-FAMILY-SOURCE-ACQUISITION-INDEPENDENT-CHECK-2026-09-18-v1.0",
        "candidate_imported": False,
        "sources_verified": len(verified) - len(failures),
        "verification_rows": verified,
        "failures": failures,
        "blind_barrier_checks": blind,
        "remote_source_fetches": 40,
        "verdict": "PASS_INDEPENDENT_UF50_001_020_SOURCE_FREEZE_VERIFICATION" if ok else "FAIL_INDEPENDENT_UF50_001_020_SOURCE_FREEZE_VERIFICATION",
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True)
    args = ap.parse_args()
    print(json.dumps(main(Path(args.candidate)), sort_keys=True, separators=(",", ":")))
