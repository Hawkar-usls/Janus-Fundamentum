from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from research.tools.apma_uf20_011_015_fresh_generic_pendant_wl_replication import candidate as frozen

SOURCE = ROOT / "research/source_data/SATLIB_UF250_020_2026-09-18.cnf"
EXPECTED_SOURCE_BLOB = "3229f9d21dc62173f3061b9003200e96f9c32ff9"
EXPECTED_FORMULA_SHA256 = "a77fdaf3fee1baf361aa13f93389d83659d22672dcc7cce59e1af3f8aa7ce389"
EXPECTED_REDUCED_SHA256 = "c218857e3e51a60840f569960513a0c01ec939d138aa8d8c6a5cd871ad32f401"
PAIR = [40, 240]


def canonical_sha(obj) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def git_blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def parse_uf250(path: Path):
    nvars = nclauses = None
    clauses = []
    buf = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        s = raw.strip()
        if not s or s.startswith("c") or s in {"%", "0"}:
            continue
        if s.startswith("p "):
            parts = s.split()
            if len(parts) != 4 or parts[:2] != ["p", "cnf"]:
                raise ValueError("BAD_DIMACS_HEADER")
            nvars, nclauses = int(parts[2]), int(parts[3])
            continue
        for value in map(int, s.split()):
            if value == 0:
                if len(buf) != 3 or len({abs(x) for x in buf}) != 3:
                    raise ValueError("NON_CANONICAL_3CNF_CLAUSE")
                if any(abs(x) < 1 or abs(x) > 250 for x in buf):
                    raise ValueError("VARIABLE_OUT_OF_RANGE")
                clauses.append((buf[0], buf[1], buf[2]))
                buf = []
            else:
                buf.append(value)
    if (nvars, nclauses) != (250, 1065) or len(clauses) != 1065 or buf:
        raise ValueError(
            f"UF250_CONTRACT_FAILURE header={(nvars,nclauses)} parsed={len(clauses)} trailing={buf}"
        )
    canonical = "".join(" ".join(map(str, c)) + " 0\n" for c in clauses).encode("ascii")
    return clauses, hashlib.sha256(canonical).hexdigest()


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: seal_bundle.py OUTPUT.json")
    output = Path(sys.argv[1])

    observed_blob = git_blob(SOURCE)
    clauses, formula_sha = parse_uf250(SOURCE)
    if observed_blob != EXPECTED_SOURCE_BLOB:
        raise RuntimeError(f"SOURCE_BLOB_MISMATCH:{observed_blob}")
    if formula_sha != EXPECTED_FORMULA_SHA256:
        raise RuntimeError(f"FORMULA_SHA_MISMATCH:{formula_sha}")

    projected = frozen.projection_identity.normalize_projection("UF250_020", clauses)[0]
    reduced, degree1_variables, target_constraints = frozen.generic_round(projected)
    reduced_sha = frozen.csha(reduced)
    if reduced_sha != EXPECTED_REDUCED_SHA256:
        raise RuntimeError(f"REDUCED_SHA_MISMATCH:{reduced_sha}")
    if not all(v in set(map(int, reduced["variables"])) for v in PAIR):
        raise RuntimeError("PAIR_NOT_PRESENT_IN_REDUCED_FORMULA")

    payload = {
        "format": "MANTEQUILLA_SEALED_REDUCED_CSP_BUNDLE_v1",
        "source": {
            "source_id": "UF250_020",
            "committed_path": "research/source_data/SATLIB_UF250_020_2026-09-18.cnf",
            "git_blob": observed_blob,
            "canonical_formula_sha256": formula_sha,
        },
        "preprocessing": {
            "projected_raw_sha256": frozen.csha(projected),
            "degree1_variables": degree1_variables,
            "target_constraints": target_constraints,
            "reduced_raw_sha256": reduced_sha,
            "reduced_variables": len(reduced["variables"]),
            "reduced_constraints": len(reduced["constraints"]),
        },
        "frozen_witness": {
            "cell": PAIR,
            "authority": "UF250 frozen scientific result commit 24c723e9a35c46d131f53c24c72591452fb64d16",
            "direct_exact_transposition_automorphism": True,
        },
        "permitted_local_view": {
            "kind": "FULL_REDUCED_CSP_PLUS_FROZEN_CELL",
            "note": "Detector/WL/E3 internals are intentionally absent. Candidate may derive only local/exterior/boundary structure from this reduced CSP."
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
        "reduced_sha256": reduced_sha,
        "reduced_variables": len(reduced["variables"]),
        "reduced_constraints": len(reduced["constraints"]),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
