from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from research.tools.apma_uf20_011_015_fresh_generic_pendant_wl_replication import candidate as frozen

SOURCE = ROOT / "research/source_data/SATLIB_UUF175_018_2026-09-18.cnf"
EXPECTED_SOURCE_BLOB = "abbc0db2364550a23a300db374983d00268f9844"
EXPECTED_FORMULA_SHA256 = "bb98ac49e98e886012d643732ef2fb4b832e5b9deaf5adf5c1c1ed6c526f773c"
EXPECTED_PROJECTED_SHA256 = "b5ad55f63dfc47ac1925360a9f4e5e02ae5ae0bf75758ce3270ac124074c23cc"
EXPECTED_REDUCED_SHA256 = "d0196006827015ac37e03a4f3f16e9ebafab560e402aca011f5f1352e53d6dcf"
PAIR = [2, 171]
BOUNDARY = [17, 120]


def csha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def git_blob(path: Path):
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def parse_uuf175(path: Path):
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
                if any(abs(x) < 1 or abs(x) > 175 for x in buf):
                    raise ValueError("VARIABLE_OUT_OF_RANGE")
                clauses.append(tuple(buf))
                buf = []
            else:
                buf.append(z)
    if buf or (nvars, nclauses) != (175, 753) or len(clauses) != 753:
        raise ValueError("UUF175_SHAPE_MISMATCH")
    canonical = "".join(" ".join(map(str, c)) + " 0\n" for c in clauses).encode("ascii")
    return clauses, hashlib.sha256(canonical).hexdigest()


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: seal_bundle.py OUTPUT.json")
    out = Path(sys.argv[1])
    clauses, formula_sha = parse_uuf175(SOURCE)
    if git_blob(SOURCE) != EXPECTED_SOURCE_BLOB:
        raise RuntimeError("SOURCE_BLOB_MISMATCH")
    if formula_sha != EXPECTED_FORMULA_SHA256:
        raise RuntimeError("FORMULA_SHA_MISMATCH")
    projected = frozen.projection_identity.normalize_projection("UUF175_018", clauses)[0]
    if frozen.csha(projected) != EXPECTED_PROJECTED_SHA256:
        raise RuntimeError("PROJECTED_SHA_MISMATCH")
    reduced, degree1_variables, target_constraints = frozen.generic_round(projected)
    reduced_sha = frozen.csha(reduced)
    if reduced_sha != EXPECTED_REDUCED_SHA256:
        raise RuntimeError("REDUCED_SHA_MISMATCH")
    if len(reduced["variables"]) != 147 or len(reduced["constraints"]) != 149:
        raise RuntimeError("REDUCED_SHAPE_MISMATCH")
    payload = {
        "format":"MANTEQUILLA_UUF175_018_A_SEALED_REDUCED_CSP_v1",
        "source":{
            "source_id":"UUF175_018",
            "committed_path":"research/source_data/SATLIB_UUF175_018_2026-09-18.cnf",
            "git_blob":EXPECTED_SOURCE_BLOB,
            "canonical_formula_sha256":formula_sha
        },
        "preprocessing":{
            "projected_raw_sha256":EXPECTED_PROJECTED_SHA256,
            "reduced_raw_sha256":reduced_sha,
            "degree1_variables":degree1_variables,
            "target_constraints":target_constraints,
            "reduced_variables":147,
            "reduced_constraints":149
        },
        "frozen_witness":{
            "cell":PAIR,
            "group":"S_2",
            "generator_transposition":PAIR,
            "expected_local_constraint_count":2,
            "expected_boundary_variables":BOUNDARY,
            "authority":"UUF175 structural census commit f392ffc8669dd471220be81b23344f6af37f3064"
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
