from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CANDIDATE_V2 = ROOT / "research/tools/trump_uf50_001_020_out_of_family_source_acquisition/candidate_v2.py"
ERRATUM = ROOT / "research/TRUMP_UF50_001_020_OUT_OF_FAMILY_SOURCE_ACQUISITION_VERIFICATION_PATH_ERRATUM_2026-09-18_v1.0.json"
ERRATUM_REVIEW = ROOT / "research/TRUMP_UF50_001_020_OUT_OF_FAMILY_SOURCE_ACQUISITION_VERIFICATION_PATH_ERRATUM_REVIEW_2026-09-18_v1.0.json"
EXPECTED = {
    CANDIDATE_V2: "82991d9f429c0f8582189d981920ae1cabc7e866",
    ERRATUM: "862e38d2e0e78e833ae59783201eb2c44e72596d",
    ERRATUM_REVIEW: "fb9893b2e5c02e02a45dde9465051c787193a436",
}
CANDIDATE_MODULE = "research.tools.trump_uf50_001_020_out_of_family_source_acquisition.candidate_v2"
PRIMARY_REPO = "Jany26/tree-aut-lib"
PRIMARY_COMMIT = "6cd58ade6de0a5c05511deb76c261ee75356ff31"
VERIFY_REPO = "dmeoli/NeuroSAT"
VERIFY_COMMIT = "568b022fc0c56e7e24fe08c012753ef29c60938e"
VERIFY_BASE = "data/uniform-random-3-sat/uf50-218"
ORDER = tuple(f"UF50_{i:03d}" for i in range(1, 21))


def blob_bytes(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def blob(path: Path) -> str:
    return blob_bytes(path.read_bytes())


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def token(n: int) -> str:
    return "0" + str(n)


def fetch(repo: str, commit: str, path: str) -> bytes:
    req = urllib.request.Request(
        f"https://raw.githubusercontent.com/{repo}/{commit}/{path}",
        headers={"User-Agent": "Janus-UF50-source-freeze-independent-v2/1.0"},
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()


def parse(data: bytes):
    nvars = nclauses = None
    clauses = []
    for raw in data.decode("utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("c") or line in {"%", "0"}:
            continue
        if line.startswith("p "):
            parts = line.split()
            if len(parts) != 4 or parts[:2] != ["p", "cnf"]:
                raise ValueError("bad header")
            nvars, nclauses = int(parts[2]), int(parts[3])
            continue
        vals = tuple(int(x) for x in line.split())
        if not vals or vals[-1] != 0:
            raise ValueError("unterminated clause")
        c = vals[:-1]
        if len(c) != 3 or len({abs(x) for x in c}) != 3 or any(not 1 <= abs(x) <= 50 for x in c):
            raise ValueError("3-CNF contract failure")
        clauses.append(c)
    if nvars != 50 or nclauses != 218 or len(clauses) != 218:
        raise ValueError("50/218 contract failure")
    canonical = "".join(" ".join(map(str, c)) + " 0\n" for c in clauses).encode("ascii")
    return clauses, sha256(canonical)


def main(candidate_json: Path):
    bindings = {str(p.relative_to(ROOT)): blob(p) == h for p, h in EXPECTED.items()}
    if not all(bindings.values()):
        return {"verdict": "HALT_INDEPENDENT_V2_AUTHORITY_BINDING_FAILURE", "bindings": bindings}
    if CANDIDATE_MODULE in sys.modules:
        return {"verdict": "HALT_INDEPENDENT_V2_CANDIDATE_IMPORT_VIOLATION"}
    cand = json.loads(candidate_json.read_text())
    if cand.get("verdict") != "PASS_UF50_001_020_DUAL_MIRROR_SOURCE_ACQUISITION_AND_FORMULA_FREEZE":
        return {"verdict": "HALT_V2_CANDIDATE_DID_NOT_PASS", "candidate_verdict": cand.get("verdict")}
    rows = cand.get("source_receipts", [])
    if len(rows) != 20 or tuple(r.get("source") for r in rows) != ORDER:
        return {"verdict": "FAIL_INDEPENDENT_V2_SOURCE_ORDER_OR_COUNT"}
    verified = []
    failures = []
    for row in rows:
        source = row["source"]
        n = int(source.split("_")[1])
        t = token(n)
        pp = f"benchmark/dimacs/dimacs-50var-218c/uf50-{t}.cnf"
        vp = f"{VERIFY_BASE}/uf50-{t}.cnf"
        try:
            primary = fetch(PRIMARY_REPO, PRIMARY_COMMIT, pp)
            verification = fetch(VERIFY_REPO, VERIFY_COMMIT, vp)
            staged = (ROOT / row["committed_copy_path"]).read_bytes()
            pc, ph = parse(primary)
            vc, vh = parse(verification)
            sc, sh = parse(staged)
            checks = {
                "ordered_three_way": pc == vc == sc,
                "formula_hash_three_way": ph == vh == sh == row.get("canonical_formula_sha256"),
                "primary_blob": blob_bytes(primary) == row.get("primary_git_blob"),
                "verification_blob": blob_bytes(verification) == row.get("verification_git_blob"),
                "staged_blob": blob_bytes(staged) == row.get("computed_committed_git_blob"),
                "primary_sha": sha256(primary) == row.get("primary_raw_sha256"),
                "verification_sha": sha256(verification) == row.get("verification_raw_sha256"),
                "verification_path_corrected": row.get("verification_path") == vp,
                "contract": row.get("variables") == 50 and row.get("clauses") == 218 and row.get("arity") == 3,
            }
            ok = all(checks.values())
            verified.append({"source": source, "checks": checks, "pass": ok, "committed_git_blob": blob_bytes(staged)})
            if not ok:
                failures.append(source)
        except Exception as exc:
            failures.append(source)
            verified.append({"source": source, "pass": False, "error": f"{type(exc).__name__}:{exc}"})
    rr = cand.get("resource_receipt", {})
    blind = {k: rr.get(k) == 0 for k in [
        "projected_raw_computations","pendant_target_computations","wl_computations",
        "direct_transposition_checks","full_transposition_searches","portfolio_replays",
        "e3_witness_computations","solver_invocations","external_truth_or_metrics_reads"
    ]}
    ok = not failures and all(blind.values()) and CANDIDATE_MODULE not in sys.modules
    return {
        "artifact_id": "JANUS-TRUMP-UF50-001-020-OUT-OF-FAMILY-SOURCE-ACQUISITION-INDEPENDENT-CHECK-V2-2026-09-18-v1.0",
        "candidate_imported": False,
        "sources_verified": sum(1 for r in verified if r.get("pass")),
        "verification_rows": verified,
        "failures": failures,
        "blind_barrier_checks": blind,
        "remote_source_fetches": 40,
        "verdict": "PASS_INDEPENDENT_UF50_001_020_SOURCE_FREEZE_VERIFICATION_V2" if ok else "FAIL_INDEPENDENT_UF50_001_020_SOURCE_FREEZE_VERIFICATION_V2",
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True)
    args = ap.parse_args()
    print(json.dumps(main(Path(args.candidate)), sort_keys=True, separators=(",", ":")))
