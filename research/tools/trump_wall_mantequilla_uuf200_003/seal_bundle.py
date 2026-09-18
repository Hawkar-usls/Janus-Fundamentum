from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from research.tools.apma_uf20_011_015_fresh_generic_pendant_wl_replication import candidate as frozen

SOURCE = ROOT / "research/source_data/SATLIB_UUF200_003_2026-09-18.cnf"
EXPECTED_SOURCE_BLOB = "d948c11b67224ae07aa9dace2d642aeb67d2e96c"
EXPECTED_FORMULA_SHA256 = "51a514945cec52bfbdaefbdd14c5cf2086522af9a7fd04b38265a7be0d4523b3"
EXPECTED_PROJECTED_SHA256 = "1f11f1054c412bd7122f19ee7082918957fd252f119d1cd19cca3f8dacbe2d99"
EXPECTED_REDUCED_SHA256 = "781c1584f797894e08e23a805ff3ddf197c5d1b3bcc3ff294711811b27fcc211"
PAIR = [162, 171]
BOUNDARY = [13, 169]


def csha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def git_blob(path: Path):
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def parse_uuf200(path: Path):
    nvars = nclauses = None
    clauses = []
    buf = []
    terminated = False
    for raw in path.read_text(encoding="ascii").splitlines():
        s = raw.strip()
        if not s or s.startswith("c"):
            continue
        if terminated:
            continue
        if s == "%":
            terminated = True
            continue
        if s == "0" and not buf and nclauses is not None and len(clauses) == nclauses:
            terminated = True
            continue
        if s.startswith("p "):
            parts = s.split()
            if len(parts) != 4 or parts[:2] != ["p", "cnf"]:
                raise ValueError("BAD_DIMACS_HEADER")
            nvars, nclauses = int(parts[2]), int(parts[3])
            continue
        for z in map(int, s.split()):
            if z == 0:
                if len(buf) != 3 or len({abs(x) for x in buf}) != 3:
                    raise ValueError("NON_CANONICAL_3CNF_CLAUSE")
                if any(abs(x) < 1 or abs(x) > 200 for x in buf):
                    raise ValueError("VARIABLE_OUT_OF_RANGE")
                clauses.append(tuple(buf))
                buf = []
            else:
                buf.append(z)
    if buf or (nvars, nclauses) != (200, 860) or len(clauses) != 860:
        raise ValueError("UUF200_SHAPE_MISMATCH")
    canonical = "".join(" ".join(map(str, c)) + " 0\n" for c in clauses).encode("ascii")
    return clauses, hashlib.sha256(canonical).hexdigest()


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: seal_bundle.py OUTPUT.json")
    out = Path(sys.argv[1])
    clauses, formula_sha = parse_uuf200(SOURCE)
    if git_blob(SOURCE) != EXPECTED_SOURCE_BLOB:
        raise RuntimeError("SOURCE_BLOB_MISMATCH")
    if formula_sha != EXPECTED_FORMULA_SHA256:
        raise RuntimeError("FORMULA_SHA_MISMATCH")
    projected = frozen.projection_identity.normalize_projection("UUF200_003", clauses)[0]
    if frozen.csha(projected) != EXPECTED_PROJECTED_SHA256:
        raise RuntimeError("PROJECTED_SHA_MISMATCH")
    reduced, degree1_variables, target_constraints = frozen.generic_round(projected)
    reduced_sha = frozen.csha(reduced)
    if reduced_sha != EXPECTED_REDUCED_SHA256:
        raise RuntimeError("REDUCED_SHA_MISMATCH")
    if len(reduced["variables"]) != 170 or len(reduced["constraints"]) != 192:
        raise RuntimeError("REDUCED_SHAPE_MISMATCH")
    payload = {
        "format":"MANTEQUILLA_UUF200_003_SEALED_REDUCED_CSP_v1",
        "source":{
            "source_id":"UUF200_003",
            "committed_path":"research/source_data/SATLIB_UUF200_003_2026-09-18.cnf",
            "git_blob":EXPECTED_SOURCE_BLOB,
            "canonical_formula_sha256":formula_sha
        },
        "preprocessing":{
            "projected_raw_sha256":EXPECTED_PROJECTED_SHA256,
            "reduced_raw_sha256":reduced_sha,
            "degree1_variables":degree1_variables,
            "target_constraints":target_constraints,
            "reduced_variables":170,
            "reduced_constraints":192
        },
        "frozen_witness":{
            "cell":PAIR,
            "group":"S_2",
            "generator_transposition":PAIR,
            "expected_local_constraint_count":2,
            "expected_boundary_variables":BOUNDARY,
            "authority":"UUF200 structural census commit c8008cca1667b097b6d3c7c511382911875f0b95"
        },
        "firewall":{
            "residual_semantics_not_computed_by_sealer":True,
            "candidate_may_read_only_this_bundle":True
        },
        "reduced_csp":reduced
    }
    payload_hash=csha(payload)
    sealed=dict(payload)
    sealed["payload_sha256"]=payload_hash
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(sealed, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    print(json.dumps({"sealed_bundle_payload_sha256":payload_hash,"reduced_raw_sha256":reduced_sha},sort_keys=True))


if __name__=="__main__":
    main()
