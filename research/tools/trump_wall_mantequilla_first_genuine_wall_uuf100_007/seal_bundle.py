from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from research.tools.apma_uf20_011_015_fresh_generic_pendant_wl_replication import candidate as frozen

SOURCE = ROOT / "research/source_data/SATLIB_UUF100_007_2026-09-18.cnf"
EXPECTED_SOURCE_BLOB = "701fa19d23472142aaa440b430a0a1447b52c3b7"
EXPECTED_FORMULA_SHA256 = "a94745aae1b47dc2950b9c437420af305e7a30664a73b5219e8a984a6df639ad"
EXPECTED_PROJECTED_SHA256 = "385a72020f421fae378008c515d34c5865db4424f4e45bef7a6b424368b76477"
EXPECTED_REDUCED_SHA256 = "a6eebedf602f7f11095fae8189b76f6d1283ae86cf0247dc5240462569a0141e"
CELL = [12, 83]


def csha(obj) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def git_blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def parse_uuf100(path: Path):
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
        if s.startswith("p "):
            parts = s.split()
            if len(parts) != 4 or parts[:2] != ["p", "cnf"]:
                raise ValueError("BAD_DIMACS_HEADER")
            nvars, nclauses = int(parts[2]), int(parts[3])
            continue
        for value in map(int, s.split()):
            if value == 0:
                if not buf:
                    raise ValueError("EMPTY_CLAUSE")
                clauses.append(tuple(buf))
                buf = []
            else:
                buf.append(value)
    if buf or (nvars, nclauses) != (100, 430) or len(clauses) != 430:
        raise ValueError("UUF100_SHAPE_MISMATCH")
    for clause in clauses:
        if len(clause) != 3 or len({abs(x) for x in clause}) != 3:
            raise ValueError("NON_CANONICAL_3CNF")
        if any(abs(x) < 1 or abs(x) > 100 for x in clause):
            raise ValueError("VARIABLE_OUT_OF_RANGE")
    canonical = "".join(" ".join(map(str, c)) + " 0\n" for c in clauses).encode("ascii")
    return clauses, hashlib.sha256(canonical).hexdigest()


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: seal_bundle.py OUTPUT.json")
    output = Path(sys.argv[1])

    observed_blob = git_blob(SOURCE)
    clauses, formula_sha = parse_uuf100(SOURCE)
    if observed_blob != EXPECTED_SOURCE_BLOB:
        raise RuntimeError(f"SOURCE_BLOB_MISMATCH:{observed_blob}")
    if formula_sha != EXPECTED_FORMULA_SHA256:
        raise RuntimeError(f"FORMULA_SHA_MISMATCH:{formula_sha}")

    projected = frozen.projection_identity.normalize_projection("UUF100_007", clauses)[0]
    projected_sha = frozen.csha(projected)
    if projected_sha != EXPECTED_PROJECTED_SHA256:
        raise RuntimeError(f"PROJECTED_SHA_MISMATCH:{projected_sha}")

    reduced, degree1_variables, target_constraints = frozen.generic_round(projected)
    reduced_sha = frozen.csha(reduced)
    if reduced_sha != EXPECTED_REDUCED_SHA256:
        raise RuntimeError(f"REDUCED_SHA_MISMATCH:{reduced_sha}")

    reduced_vars = set(map(int, reduced["variables"]))
    if not all(v in reduced_vars for v in CELL):
        raise RuntimeError("FROZEN_CELL_NOT_PRESENT")

    cell = set(CELL)
    local_count = sum(
        bool(cell.intersection(int(v) for v in c["scope"]))
        for c in reduced["constraints"]
    )
    boundary = sorted({
        int(v)
        for c in reduced["constraints"]
        if cell.intersection(int(x) for x in c["scope"])
        for v in c["scope"]
        if int(v) not in cell
    })
    if local_count != 2 or boundary != [14, 58]:
        raise RuntimeError(f"STRUCTURAL_ELIGIBILITY_MISMATCH:{local_count}:{boundary}")

    payload = {
        "format": "MANTEQUILLA_FIRST_GENUINE_WALL_SEALED_REDUCED_CSP_v1",
        "source": {
            "source_id": "UUF100_007",
            "committed_path": "research/source_data/SATLIB_UUF100_007_2026-09-18.cnf",
            "git_blob": observed_blob,
            "canonical_formula_sha256": formula_sha,
        },
        "preprocessing": {
            "projected_raw_sha256": projected_sha,
            "degree1_variables": degree1_variables,
            "target_constraints": target_constraints,
            "reduced_raw_sha256": reduced_sha,
            "reduced_variables": len(reduced["variables"]),
            "reduced_constraints": len(reduced["constraints"]),
        },
        "frozen_witness": {
            "cell": CELL,
            "group": "S2",
            "generator_transpositions": [CELL],
            "structural_eligibility": {
                "local_constraint_count": local_count,
                "boundary_variables": boundary,
                "boundary_variable_count": len(boundary),
                "classification": "ACTIVE_EXACT_SYMMETRY_ELIGIBLE",
            },
            "authority": "UUF100 census freeze commit 2d72a000f67b815fde41b552366cbdfe35a7e4c0",
        },
        "permitted_local_view": {
            "kind": "FULL_REDUCED_CSP_PLUS_FROZEN_S2_CELL",
            "note": "No WL/E3/detector artifacts are present. Candidate may directly verify only the frozen swap [12,83].",
        },
        "reduced_csp": reduced,
    }
    payload_sha = csha(payload)
    sealed = dict(payload)
    sealed["payload_sha256"] = payload_sha
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(sealed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "sealed_bundle_payload_sha256": payload_sha,
        "source_blob": observed_blob,
        "formula_sha256": formula_sha,
        "projected_sha256": projected_sha,
        "reduced_sha256": reduced_sha,
        "reduced_variables": len(reduced["variables"]),
        "reduced_constraints": len(reduced["constraints"]),
        "local_constraint_count": local_count,
        "boundary_variables": boundary,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
