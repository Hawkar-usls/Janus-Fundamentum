from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from research.tools.apma_uf20_011_015_fresh_generic_pendant_wl_replication import candidate as frozen

SOURCE = ROOT / "research/source_data/SATLIB_UF250_016_2026-09-18.cnf"
EXPECTED_SOURCE_BLOB = "01ceb79b347e4163f0ae57c62490c405e9c68418"
EXPECTED_FORMULA_SHA256 = "00845e351df291b16468b1c0b243905aa2abc936780573fc6e46047c4ce030d5"
EXPECTED_PROJECTED_SHA256 = "5e9692e6e138e5b1756666667bc28b4b4f930163da9199f61304d524c29512d7"
EXPECTED_REDUCED_SHA256 = "fae8a40cebba0229bd9ef542a28fec81e1f4efd3451f8ba1d5fe2e1b2de1e674"
CELL = [61, 91, 237]
GENERATORS = [[61, 91], [61, 237], [91, 237]]


def canonical_sha(obj) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def git_blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: seal_bundle.py OUTPUT.json")
    output = Path(sys.argv[1])

    observed_blob = git_blob(SOURCE)
    clauses, formula_sha = frozen.parse_and_formula_hash(SOURCE)
    if observed_blob != EXPECTED_SOURCE_BLOB:
        raise RuntimeError(f"SOURCE_BLOB_MISMATCH:{observed_blob}")
    if formula_sha != EXPECTED_FORMULA_SHA256:
        raise RuntimeError(f"FORMULA_SHA_MISMATCH:{formula_sha}")

    projected = frozen.projection_identity.normalize_projection("UF250_016", clauses)[0]
    projected_sha = frozen.csha(projected)
    if projected_sha != EXPECTED_PROJECTED_SHA256:
        raise RuntimeError(f"PROJECTED_SHA_MISMATCH:{projected_sha}")

    reduced, degree1_variables, target_constraints = frozen.generic_round(projected)
    reduced_sha = frozen.csha(reduced)
    if reduced_sha != EXPECTED_REDUCED_SHA256:
        raise RuntimeError(f"REDUCED_SHA_MISMATCH:{reduced_sha}")

    reduced_vars = set(map(int, reduced["variables"]))
    if not all(v in reduced_vars for v in CELL):
        raise RuntimeError("FROZEN_CELL_NOT_PRESENT_IN_REDUCED_FORMULA")

    payload = {
        "format": "MANTEQUILLA_NONTRIVIAL_CORRELATED_BOUNDARY_SEALED_CSP_v1",
        "source": {
            "source_id": "UF250_016",
            "committed_path": "research/source_data/SATLIB_UF250_016_2026-09-18.cnf",
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
            "group": "S3",
            "generator_transpositions": GENERATORS,
            "authority": "UF250 frozen result commit 24c723e9a35c46d131f53c24c72591452fb64d16",
        },
        "permitted_local_view": {
            "kind": "FULL_REDUCED_CSP_PLUS_FROZEN_S3_CELL",
            "note": "Detector/WL/E3 internals are absent. Post-seal code may only verify the three frozen generator transpositions directly on this CSP.",
        },
        "reduced_csp": reduced,
    }
    payload_sha = canonical_sha(payload)
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
        "frozen_cell": CELL,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
