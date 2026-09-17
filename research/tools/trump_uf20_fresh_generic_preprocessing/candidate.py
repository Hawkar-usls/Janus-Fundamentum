from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Any

from research.tools.apma_unseen_basis import raw_relation_basis as raw_basis

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / "research/TRUMP_UF20_FRESH_SOURCE_INDEPENDENT_PREPROCESSING_PREREGISTRATION_2026-09-17.json"
REVIEW = ROOT / "research/TRUMP_UF20_FRESH_SOURCE_INDEPENDENT_PREPROCESSING_PREREGISTRATION_REVIEW_2026-09-17.json"
RAW_BASIS = ROOT / "research/tools/apma_unseen_basis/raw_relation_basis.py"
EXPECTED_AUTHORITY_BLOBS = {
    PREREG: "afff1551b0653dc70d942dcb81f9821ef9579785",
    REVIEW: "38db57a6ea7d2e0763c854d94cc4374e52caf659",
    RAW_BASIS: "63490c05ef3e91a4f682f75da26ff2af811839a6",
}
CORE = {"000", "111"}


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_obj(obj: Any) -> str:
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()


def firewall() -> dict:
    return {
        "P_VS_NP": "OPEN",
        "GENERAL_SAT_IN_P": "NOT_PROVED",
        "GENERAL_GT2_TRACTABILITY": "NOT_PROVED",
        "CONNECTED_MIXED_CORE_SOLVED": "NO",
        "WL_COMPUTED": False,
        "SEALED_PORTFOLIO_REPLAYED": False,
        "SOLVER_INVOKED": False,
        "ROUTE_LABELS_COMPUTED": False,
    }


def parse_dimacs(path: Path) -> tuple[tuple[int, int], list[tuple[int, int, int]]]:
    text = path.read_bytes().decode("utf-8")
    header: tuple[int, int] | None = None
    clauses: list[tuple[int, int, int]] = []
    buf: list[int] = []
    for raw in text.splitlines():
        s = raw.strip()
        if not s or s.startswith("c"):
            continue
        if s.startswith("%"):
            break
        if s.startswith("p "):
            parts = s.split()
            if len(parts) != 4 or parts[1] != "cnf":
                raise ValueError("DIMACS_HEADER_INVALID")
            header = (int(parts[2]), int(parts[3]))
            continue
        for token in s.split():
            z = int(token)
            if z == 0:
                if len(buf) != 3 or len({abs(v) for v in buf}) != 3:
                    raise ValueError("DIMACS_CLAUSE_NOT_DISTINCT_ARITY_3")
                clauses.append(tuple(buf))
                buf = []
            else:
                buf.append(z)
    if buf:
        raise ValueError("DIMACS_UNTERMINATED_CLAUSE")
    if header != (20, 91) or len(clauses) != 91:
        raise ValueError("DIMACS_20_91_CONTRACT_FAILURE")
    return header, clauses


def relation_id(clause: tuple[int, int, int]) -> str:
    return "".join("0" if lit > 0 else "1" for lit in sorted(clause, key=lambda x: abs(x)))


def project_r000_r111(source: str, clauses: list[tuple[int, int, int]]) -> tuple[dict, list[int]]:
    selected = [(ordinal, clause) for ordinal, clause in enumerate(clauses, 1) if relation_id(clause) in CORE]
    if not selected:
        raise ValueError("EMPTY_R000_R111_PROJECTION")
    variables = sorted({abs(lit) for _, clause in selected for lit in clause})
    constraints: list[dict] = []
    prefix = source.lower()
    for ordinal, clause in selected:
        scope = sorted(abs(lit) for lit in clause)
        allowed: list[list[int]] = []
        for bits in itertools.product((0, 1), repeat=3):
            assignment = dict(zip(scope, bits, strict=True))
            satisfied = any(
                assignment[abs(lit)] == 1 if lit > 0 else assignment[abs(lit)] == 0
                for lit in clause
            )
            if satisfied:
                allowed.append(list(bits))
        constraints.append({
            "id": f"satlib_{prefix}_c{ordinal:03d}",
            "scope": scope,
            "allowed": allowed,
        })
    raw = raw_basis.canonicalize_raw({"variables": variables, "constraints": constraints})
    return raw, [ordinal for ordinal, _ in selected]


def incidence_counts(raw: dict) -> Counter[int]:
    counts: Counter[int] = Counter()
    for c in raw["constraints"]:
        for v in c["scope"]:
            counts[int(v)] += 1
    return counts


def eligible_pendant(c: dict, incidence: Counter[int]) -> dict | None:
    scope = [int(v) for v in c["scope"]]
    if len(scope) != 3:
        return None
    leaves = [v for v in scope if incidence[v] == 1]
    if len(leaves) != 1:
        return None
    leaf = leaves[0]
    gateway = sorted(v for v in scope if v != leaf)
    allowed = {tuple(int(x) for x in row) for row in c["allowed"]}
    witnesses: dict[str, int] = {}
    for gbits in itertools.product((0, 1), repeat=2):
        satisfying_leaf_values: list[int] = []
        for leaf_bit in (0, 1):
            assignment = {gateway[0]: gbits[0], gateway[1]: gbits[1], leaf: leaf_bit}
            row = tuple(assignment[v] for v in scope)
            if row in allowed:
                satisfying_leaf_values.append(leaf_bit)
        if not satisfying_leaf_values:
            return None
        witnesses[f"{gbits[0]}{gbits[1]}"] = min(satisfying_leaf_values)
    if set(witnesses) != {"00", "01", "10", "11"}:
        return None
    return {
        "constraint_id": c["id"],
        "leaf": leaf,
        "gateway": gateway,
        "boundary_support_count": 4,
        "canonical_witnesses": witnesses,
    }


def source_guard(pre: dict, review: dict) -> dict:
    authority_bindings = {
        str(path.relative_to(ROOT)): git_blob_sha1(path) == expected
        for path, expected in EXPECTED_AUTHORITY_BLOBS.items()
    }
    manifest_rows = pre.get("frozen_fresh_source_manifest", [])
    source_checks: dict[str, dict] = {}
    for row in manifest_rows:
        path = ROOT / row["path"]
        source_checks[row["source"]] = {
            "exists": path.is_file(),
            "blob": path.is_file() and git_blob_sha1(path) == row["git_blob_sha1"],
            "size": path.is_file() and path.stat().st_size == int(row["size_bytes"]),
        }
    review_ok = (
        review.get("review_verdict")
        == "PASS_CLEAN_REVIEW_GENERIC_PREPROCESSING_EXECUTION_AUTHORIZED_ON_FROZEN_FIVE_SOURCE_PANEL_ONLY"
        and review.get("reviewed_preregistration_commit") == "2e49ba739608326c4e12403bfb0ce9714f710a81"
    )
    exact_manifest = [r.get("source") for r in manifest_rows] == [
        "UF20_016", "UF20_017", "UF20_018", "UF20_019", "UF20_020"
    ]
    ok = (
        all(authority_bindings.values())
        and review_ok
        and exact_manifest
        and len(source_checks) == 5
        and all(all(x.values()) for x in source_checks.values())
    )
    return {
        "ok": ok,
        "authority_bindings": authority_bindings,
        "review_authorized": review_ok,
        "exact_manifest": exact_manifest,
        "source_checks": source_checks,
    }


def process_source(row: dict) -> dict:
    source = str(row["source"])
    path = ROOT / row["path"]
    _, clauses = parse_dimacs(path)
    original, ordinals = project_r000_r111(source, clauses)
    incidence = incidence_counts(original)
    eligible = [x for c in original["constraints"] if (x := eligible_pendant(c, incidence)) is not None]
    eligible.sort(key=lambda x: x["constraint_id"])
    remove_ids = {x["constraint_id"] for x in eligible}
    remove_leaves = {int(x["leaf"]) for x in eligible}
    remaining_constraints = [c for c in original["constraints"] if c["id"] not in remove_ids]
    remaining_variables = [int(v) for v in original["variables"] if int(v) not in remove_leaves]
    if not remaining_constraints:
        raise ValueError("REDUCTION_WOULD_EMPTY_ALL_CONSTRAINTS")
    reduced = raw_basis.canonicalize_raw({
        "variables": remaining_variables,
        "constraints": remaining_constraints,
    })
    leaves_absent = all(not (remove_leaves & set(int(v) for v in c["scope"])) for c in reduced["constraints"])
    witnesses_complete = all(set(x["canonical_witnesses"]) == {"00", "01", "10", "11"} for x in eligible)
    exact_original_incidence = all(incidence[int(x["leaf"])] == 1 for x in eligible)
    retained_ids = {c["id"] for c in reduced["constraints"]}
    unchanged_ids = retained_ids == {c["id"] for c in original["constraints"] if c["id"] not in remove_ids}
    semantics_ok = leaves_absent and witnesses_complete and exact_original_incidence and unchanged_ids
    return {
        "source": source,
        "selected_clause_ordinals": ordinals,
        "original_projected_raw_sha256": sha256_obj(original),
        "original_variable_count": len(original["variables"]),
        "original_constraint_count": len(original["constraints"]),
        "original_incidence_counts": {str(k): int(v) for k, v in sorted(incidence.items())},
        "eligible_attachments": eligible,
        "eligible_attachment_count": len(eligible),
        "removed_constraint_ids": sorted(remove_ids),
        "removed_leaves": sorted(remove_leaves),
        "reduced_raw_sha256": sha256_obj(reduced),
        "reduced_variable_count": len(reduced["variables"]),
        "reduced_constraint_count": len(reduced["constraints"]),
        "semantics_certificate": {
            "all_removed_leaves_absent_from_retained_constraints": leaves_absent,
            "all_witness_tables_complete_4_of_4": witnesses_complete,
            "all_removed_leaves_had_original_global_incidence_one": exact_original_incidence,
            "all_and_only_target_constraints_removed": unchanged_ids,
            "reverse_extension_independent_by_unique_leaf_incidence": exact_original_incidence,
            "exact_existential_projection_equivalence": semantics_ok,
        },
        "source_pass": semantics_ok,
    }


def main() -> dict:
    pre = json.loads(PREREG.read_text(encoding="utf-8"))
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    guard = source_guard(pre, review)
    if not guard["ok"]:
        return {
            "artifact_id": "JANUS-TRUMP-UF20-FRESH-GENERIC-PREPROCESSING-CANDIDATE-2026-09-17-v1.0",
            "verdict": "FAIL_FROZEN_SOURCE_MANIFEST_MISMATCH",
            "source_guard": guard,
            "scientific_firewall": firewall(),
        }
    try:
        rows = [process_source(row) for row in pre["frozen_fresh_source_manifest"]]
    except Exception as exc:
        return {
            "artifact_id": "JANUS-TRUMP-UF20-FRESH-GENERIC-PREPROCESSING-CANDIDATE-2026-09-17-v1.0",
            "verdict": "FAIL_GENERIC_PROJECTION_CONTRACT",
            "reason": f"{type(exc).__name__}:{exc}",
            "source_guard": guard,
            "scientific_firewall": firewall(),
        }
    all_ok = all(row["source_pass"] for row in rows)
    total_targets = sum(int(row["eligible_attachment_count"]) for row in rows)
    if not all_ok:
        verdict = "FAIL_EXACT_PENDANT_PROJECTION_SEMANTICS"
    elif total_targets == 0:
        verdict = "PASS_GENERIC_PREPROCESSING_NO_ELIGIBLE_PENDANTS"
    else:
        verdict = "PASS_GENERIC_SOURCE_INDEPENDENT_ONE_ROUND_PREPROCESSING"
    return {
        "artifact_id": "JANUS-TRUMP-UF20-FRESH-GENERIC-PREPROCESSING-CANDIDATE-2026-09-17-v1.0",
        "authority": "FRESH_SOURCE_BOUND_R000_R111_PROJECTED_RAW_PREPROCESSING_ONLY",
        "verdict": verdict,
        "source_guard": guard,
        "rows": rows,
        "totals": {
            "sources": len(rows),
            "eligible_attachments": total_targets,
            "reduction_rounds": 1,
            "post_round_target_discoveries": 0,
        },
        "resource_receipt": {
            "fresh_source_structural_reads": len(rows),
            "WL_values_computed": 0,
            "portfolio_replays": 0,
            "solver_invocations": 0,
            "route_labels_computed": 0,
            "automorphism_tests": 0,
            "group_searches": 0,
            "new_carrier_mechanisms": 0,
            "new_adapter_mechanisms": 0,
            "new_quotient_mechanisms": 0,
        },
        "scientific_firewall": firewall(),
    }


if __name__ == "__main__":
    print(json.dumps(main(), sort_keys=True, separators=(",", ":")))
