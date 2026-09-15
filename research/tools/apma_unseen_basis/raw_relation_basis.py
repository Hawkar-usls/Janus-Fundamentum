from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from research.tools.apma_mixed_carrier_barrier.check_schaefer_barrier import (
    is_0_valid,
    is_1_valid,
    is_horn,
    is_dual_horn,
    is_bijunctive,
    is_affine,
)

ARTIFACT_ID = "JANUS-TRUMP-RAW-RELATION-SCHAEFER-BASIS-INDUCTION-CANDIDATE-2026-09-15-v1.0"
AUTHORITY = "CANDIDATE_IMPLEMENTATION__SCOPED_DISCOVERY_ONLY__NO_SCIENTIFIC_PROMOTION"
PREREG_REL = Path("research/TRUMP_RAW_RELATION_SCHAEFER_BASIS_INDUCTION_PREREGISTRATION_2026-09-15.json")
PREREG_COMMIT = "42c2929a9bfc3557ac1b2684ee1957ac0a94d398"
PREREG_GIT_BLOB_SHA1 = "92c6e6978f171a800db82bd6ae2e3c7112d65e22"
SEALED_PRIMITIVE_REL = Path("research/tools/apma_mixed_carrier_barrier/check_schaefer_barrier.py")
SEALED_PRIMITIVE_GIT_BLOB_SHA1 = "11fcacd5f0c550543f96648a7965734308509d22"

SELECTION_PRIORITY = (
    "AFFINE",
    "BIJUNCTIVE",
    "HORN",
    "DUAL_HORN",
    "ZERO_VALID",
    "ONE_VALID",
)

FORBIDDEN_TRUSTED_FIELDS = {
    "kind",
    "carrier",
    "class",
    "base_kind",
    "alien_kind",
    "affine",
    "horn",
    "bijunctive",
}

ALLOWED_TOP_LEVEL = {"variables", "constraints"}
ALLOWED_CONSTRAINT_FIELDS = {"id", "scope", "allowed"}


class RawBasisInputError(ValueError):
    pass


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def _tuple_key(bits: tuple[int, ...]) -> str:
    return "".join(str(int(x)) for x in bits)


def _relation_key(arity: int, rel: set[tuple[int, ...]]) -> tuple[int, tuple[str, ...]]:
    return int(arity), tuple(sorted(_tuple_key(t) for t in rel))


def _canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha256_obj(obj: Any) -> str:
    return hashlib.sha256(_canonical_json(obj)).hexdigest()


def canonicalize_raw(raw: dict) -> dict:
    if not isinstance(raw, dict):
        raise RawBasisInputError("RAW_OBJECT_NOT_DICT")
    unknown_top = set(raw) - ALLOWED_TOP_LEVEL
    if unknown_top:
        if unknown_top & FORBIDDEN_TRUSTED_FIELDS:
            raise RawBasisInputError("FORBIDDEN_TRUSTED_TOP_LEVEL_FIELD")
        raise RawBasisInputError("UNKNOWN_TOP_LEVEL_FIELD")

    variables = raw.get("variables")
    constraints = raw.get("constraints")
    if not isinstance(variables, list) or not variables or not all(isinstance(v, int) for v in variables):
        raise RawBasisInputError("VARIABLES_INVALID")
    if variables != sorted(set(variables)):
        raise RawBasisInputError("VARIABLES_MUST_BE_SORTED_UNIQUE")
    variable_set = set(variables)
    if not isinstance(constraints, list) or not constraints:
        raise RawBasisInputError("CONSTRAINTS_INVALID")

    canonical_constraints: list[dict] = []
    ids: set[str] = set()
    for row in constraints:
        if not isinstance(row, dict):
            raise RawBasisInputError("CONSTRAINT_NOT_DICT")
        fields = set(row)
        if fields & FORBIDDEN_TRUSTED_FIELDS:
            raise RawBasisInputError("FORBIDDEN_TRUSTED_CONSTRAINT_FIELD")
        if fields != ALLOWED_CONSTRAINT_FIELDS:
            raise RawBasisInputError("CONSTRAINT_FIELDS_MUST_BE_EXACT")
        rid = str(row["id"])
        if not rid or rid in ids:
            raise RawBasisInputError("CONSTRAINT_ID_INVALID_OR_DUPLICATE")
        ids.add(rid)
        scope = row["scope"]
        if not isinstance(scope, list) or not scope or not all(isinstance(v, int) for v in scope):
            raise RawBasisInputError("SCOPE_INVALID")
        if len(scope) != len(set(scope)) or any(v not in variable_set for v in scope):
            raise RawBasisInputError("SCOPE_DUPLICATE_OR_OUTSIDE_VARIABLES")
        allowed = row["allowed"]
        if not isinstance(allowed, list) or not allowed:
            raise RawBasisInputError("EMPTY_OR_INVALID_RELATION_OUTSIDE_FROZEN_SCOPE")
        tuples: set[tuple[int, ...]] = set()
        for t in allowed:
            if not isinstance(t, (list, tuple)) or len(t) != len(scope):
                raise RawBasisInputError("ALLOWED_TUPLE_ARITY_MISMATCH")
            if any(bit not in (0, 1) for bit in t):
                raise RawBasisInputError("ALLOWED_TUPLE_NON_BOOLEAN")
            tuples.add(tuple(int(bit) for bit in t))
        canonical_constraints.append(
            {
                "id": rid,
                "scope": [int(v) for v in scope],
                "allowed": [list(t) for t in sorted(tuples)],
            }
        )

    canonical_constraints.sort(
        key=lambda r: (
            tuple(r["scope"]),
            tuple(_tuple_key(tuple(t)) for t in r["allowed"]),
            r["id"],
        )
    )
    return {"variables": variables, "constraints": canonical_constraints}


def relation_surface(canonical_raw: dict) -> list[dict]:
    unique: dict[tuple[int, tuple[str, ...]], set[tuple[int, ...]]] = {}
    for row in canonical_raw["constraints"]:
        rel = {tuple(int(x) for x in t) for t in row["allowed"]}
        key = _relation_key(len(row["scope"]), rel)
        unique[key] = rel
    out = []
    for (arity, words), rel in sorted(unique.items()):
        out.append({
            "arity": arity,
            "allowed": list(words),
            "tuple_count": len(rel),
        })
    return out


def surface_to_relations(surface: list[dict]) -> list[set[tuple[int, ...]]]:
    return [
        {tuple(int(ch) for ch in word) for word in row["allowed"]}
        for row in surface
    ]


def classify_language(relations: list[set[tuple[int, ...]]]) -> dict[str, bool]:
    return {
        "ZERO_VALID": is_0_valid(relations),
        "ONE_VALID": is_1_valid(relations),
        "HORN": is_horn(relations),
        "DUAL_HORN": is_dual_horn(relations),
        "BIJUNCTIVE": is_bijunctive(relations),
        "AFFINE": is_affine(relations),
    }


def classify_each(surface: list[dict]) -> list[dict]:
    out: list[dict] = []
    for row in surface:
        rel = {tuple(int(ch) for ch in word) for word in row["allowed"]}
        fp = classify_language([rel])
        out.append({
            "relation_sha256": _sha256_obj({"arity": row["arity"], "allowed": row["allowed"]}),
            "arity": row["arity"],
            "tuple_count": row["tuple_count"],
            "fingerprint": fp,
        })
    return out


def complexity_receipt(surface: list[dict]) -> dict:
    binary = 0
    ternary = 0
    coordinate_ops = 0
    for row in surface:
        s = int(row["tuple_count"])
        a = int(row["arity"])
        binary += 2 * s * s
        ternary += 2 * s * s * s
        coordinate_ops += (2 * s * s + 2 * s * s * s) * a
    return {
        "binary_tuple_operation_calls": binary,
        "ternary_tuple_operation_calls": ternary,
        "coordinate_bit_operations_upper_bound": coordinate_ops,
        "asymptotic": "O(sum_R (s_R^3 * a_R)) for the frozen six-predicate fingerprint over explicit relation tables",
        "full_variable_assignments_enumerated": 0,
        "solver_invocations": 0,
        "carrier_executions": 0,
    }


def source_guard() -> dict:
    root = repo_root()
    prereg = root / PREREG_REL
    primitive = root / SEALED_PRIMITIVE_REL
    prereg_data = json.loads(prereg.read_text(encoding="utf-8"))
    checks = {
        "prereg_blob": git_blob_sha1(prereg) == PREREG_GIT_BLOB_SHA1,
        "prereg_status": prereg_data.get("status") == "FROZEN_BEFORE_CANDIDATE_IMPLEMENTATION",
        "prereg_artifact": prereg_data.get("artifact_id") == "JANUS-TRUMP-RAW-RELATION-SCHAEFER-BASIS-INDUCTION-PREREGISTRATION-2026-09-15-v1.0",
        "sealed_primitive_blob": git_blob_sha1(primitive) == SEALED_PRIMITIVE_GIT_BLOB_SHA1,
    }
    return {"ok": all(checks.values()), "checks": checks}


def induce_basis(raw: dict) -> dict:
    guard = source_guard()
    if not guard["ok"]:
        return {
            "artifact_id": ARTIFACT_ID,
            "authority": AUTHORITY,
            "status": "HALT_SOURCE_GUARD",
            "source_guard": guard,
            "scientific_firewall": scientific_firewall(),
        }

    try:
        canonical = canonicalize_raw(raw)
    except RawBasisInputError as exc:
        return {
            "artifact_id": ARTIFACT_ID,
            "authority": AUTHORITY,
            "status": "REJECT_RAW_INPUT",
            "reason": str(exc),
            "source_guard": guard,
            "metrics": {
                "solver_invocations": 0,
                "carrier_executions": 0,
                "full_variable_assignments_enumerated": 0,
            },
            "scientific_firewall": scientific_firewall(),
        }

    raw_hash = _sha256_obj(canonical)
    surface = relation_surface(canonical)
    surface_hash = _sha256_obj(surface)
    relations = surface_to_relations(surface)
    language_fp = classify_language(relations)
    per_relation = classify_each(surface)
    candidates = [name for name in SELECTION_PRIORITY if language_fp[name]]
    selected = candidates[0] if candidates else None
    metrics = complexity_receipt(surface)

    result = {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "prereg_commit": PREREG_COMMIT,
        "source_guard": guard,
        "raw_object_sha256": raw_hash,
        "semantic_surface_sha256": surface_hash,
        "semantic_surface": surface,
        "per_relation_fingerprint": per_relation,
        "language_fingerprint": language_fp,
        "candidate_bases": candidates,
        "selected_basis": selected,
        "abstraction_adequacy": "PASS_COMPLETE_SURFACE_CLOSURE" if selected else "NOT_ESTABLISHED",
        "metrics": metrics,
        "scientific_firewall": scientific_firewall(),
    }
    if selected is None:
        result["status"] = "OPEN_NO_SCHAEFER_BASIS"
        result["execution_authorized"] = False
    else:
        result["status"] = "ADMIT_EXACT_SCHAEFER_BASIS"
        result["execution_authorized"] = True
    return result


def scientific_firewall() -> dict:
    return {
        "P_VS_NP": "OPEN",
        "GENERAL_SAT_IN_P": "NOT_PROVED",
        "ARBITRARY_UNSEEN_INVARIANT_DISCOVERY": "NOT_PROVED",
        "SCOPE": "EXPLICIT_BOOLEAN_RELATION_TABLES_TO_FROZEN_SIX_SCHAEFER_BASES_ONLY",
        "SOLVER_EXECUTION_IN_THIS_GATE": "FORBIDDEN",
        "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE_PENDING_HQ_REVIEW",
    }


def raw_or2() -> dict:
    return {
        "variables": [0, 1],
        "constraints": [
            {"id": "opaque_7", "scope": [0, 1], "allowed": [[1, 1], [0, 1], [1, 0]]},
        ],
    }


def raw_even_xor3() -> dict:
    return {
        "variables": [0, 1, 2],
        "constraints": [
            {"id": "opaque_19", "scope": [0, 1, 2], "allowed": [[1, 1, 0], [0, 0, 0], [1, 0, 1], [0, 1, 1]]},
        ],
    }


def raw_mixed() -> dict:
    return {
        "variables": [0, 1, 2, 3],
        "constraints": [
            {"id": "opaque_a", "scope": [0, 1], "allowed": [[0, 1], [1, 0], [1, 1]]},
            {"id": "opaque_b", "scope": [1, 2, 3], "allowed": [[0, 0, 0], [0, 1, 1], [1, 0, 1], [1, 1, 0]]},
        ],
    }


def permuted(raw: dict) -> dict:
    rows = []
    for idx, row in enumerate(reversed(raw["constraints"])):
        rows.append({
            "id": f"renamed_{idx}",
            "scope": list(row["scope"]),
            "allowed": list(reversed(row["allowed"])),
        })
    return {"variables": list(raw["variables"]), "constraints": rows}


def label_injected() -> dict:
    x = raw_even_xor3()
    x["constraints"][0]["kind"] = "AFFINE"
    return x


def main() -> None:
    cases = {
        "raw_or2": induce_basis(raw_or2()),
        "raw_even_xor3": induce_basis(raw_even_xor3()),
        "raw_mixed": induce_basis(raw_mixed()),
        "raw_mixed_permuted": induce_basis(permuted(raw_mixed())),
        "label_injected": induce_basis(label_injected()),
    }
    print(json.dumps({
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "cases": cases,
        "scientific_firewall": scientific_firewall(),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
