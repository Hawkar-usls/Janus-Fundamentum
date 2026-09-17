from __future__ import annotations

import hashlib
import itertools
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / "research/TRUMP_UF20_FRESH_SOURCE_INDEPENDENT_PREPROCESSING_PREREGISTRATION_2026-09-17.json"
REVIEW = ROOT / "research/TRUMP_UF20_FRESH_SOURCE_INDEPENDENT_PREPROCESSING_PREREGISTRATION_REVIEW_2026-09-17.json"
EXPECTED_AUTHORITY_BLOBS = {
    PREREG: "afff1551b0653dc70d942dcb81f9821ef9579785",
    REVIEW: "38db57a6ea7d2e0763c854d94cc4374e52caf659",
}


def git_blob(path: Path) -> str:
    body = path.read_bytes()
    return hashlib.sha1(("blob %d\0" % len(body)).encode("ascii") + body).hexdigest()


def packed(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def obj_sha(obj: Any) -> str:
    return hashlib.sha256(packed(obj)).hexdigest()


def canonicalize(raw: dict) -> dict:
    variables = [int(v) for v in raw["variables"]]
    if variables != sorted(set(variables)):
        raise ValueError("VARIABLE_CANONICALITY_FAILURE")
    vset = set(variables)
    rows: list[dict] = []
    ids: set[str] = set()
    for c in raw["constraints"]:
        cid = str(c["id"])
        scope = [int(v) for v in c["scope"]]
        if not cid or cid in ids or len(scope) != len(set(scope)) or any(v not in vset for v in scope):
            raise ValueError("CONSTRAINT_CANONICALITY_FAILURE")
        ids.add(cid)
        allowed = sorted({tuple(int(x) for x in t) for t in c["allowed"]})
        if not allowed or any(len(t) != len(scope) or any(x not in (0, 1) for x in t) for t in allowed):
            raise ValueError("RELATION_CANONICALITY_FAILURE")
        rows.append({"id": cid, "scope": scope, "allowed": [list(t) for t in allowed]})
    if not rows:
        raise ValueError("EMPTY_RAW")
    rows.sort(key=lambda r: (tuple(r["scope"]), tuple("".join(map(str, t)) for t in r["allowed"]), r["id"]))
    return {"variables": variables, "constraints": rows}


def parse_independently(path: Path) -> list[tuple[int, int, int]]:
    header = None
    clauses: list[tuple[int, int, int]] = []
    current: list[int] = []
    for raw_line in path.read_bytes().decode("utf-8").split("\n"):
        line = raw_line.strip()
        if not line or line[:1] == "c":
            continue
        if line[:1] == "%":
            break
        parts = line.split()
        if parts and parts[0] == "p":
            if parts[:2] != ["p", "cnf"] or len(parts) != 4:
                raise ValueError("BAD_HEADER")
            header = (int(parts[2]), int(parts[3]))
            continue
        for word in parts:
            value = int(word)
            if value:
                current.append(value)
                continue
            if len(current) != 3 or len({abs(x) for x in current}) != 3:
                raise ValueError("BAD_CLAUSE")
            clauses.append((current[0], current[1], current[2]))
            current.clear()
    if current or header != (20, 91) or len(clauses) != 91:
        raise ValueError("DIMACS_CONTRACT_FAILURE")
    return clauses


def sign_word(clause: tuple[int, int, int]) -> str:
    ordered = sorted(clause, key=lambda literal: abs(literal))
    return "".join("0" if literal > 0 else "1" for literal in ordered)


def build_projection(source: str, clauses: list[tuple[int, int, int]]) -> tuple[dict, list[int]]:
    keep: list[tuple[int, tuple[int, int, int]]] = []
    for idx, clause in enumerate(clauses, start=1):
        if sign_word(clause) == "000" or sign_word(clause) == "111":
            keep.append((idx, clause))
    if not keep:
        raise ValueError("EMPTY_PROJECTION")
    variables = sorted({abs(lit) for _, clause in keep for lit in clause})
    constraints = []
    for idx, clause in keep:
        scope = sorted(abs(lit) for lit in clause)
        relation = []
        for assignment_tuple in itertools.product((0, 1), repeat=3):
            assignment = {scope[i]: assignment_tuple[i] for i in range(3)}
            clause_true = False
            for lit in clause:
                bit = assignment[abs(lit)]
                clause_true = clause_true or (bit == 1 if lit > 0 else bit == 0)
            if clause_true:
                relation.append(list(assignment_tuple))
        constraints.append({
            "id": "satlib_%s_c%03d" % (source.lower(), idx),
            "scope": scope,
            "allowed": relation,
        })
    return canonicalize({"variables": variables, "constraints": constraints}), [idx for idx, _ in keep]


def derive_expected(source_row: dict) -> dict:
    source = str(source_row["source"])
    path = ROOT / source_row["path"]
    clauses = parse_independently(path)
    original, ordinals = build_projection(source, clauses)
    incidence: Counter[int] = Counter(v for c in original["constraints"] for v in c["scope"])
    eligible = []
    for c in original["constraints"]:
        scope = [int(v) for v in c["scope"]]
        unique = [v for v in scope if incidence[v] == 1]
        if len(scope) != 3 or len(unique) != 1:
            continue
        leaf = unique[0]
        gateway = sorted(set(scope) - {leaf})
        if len(gateway) != 2:
            continue
        allowed = {tuple(int(x) for x in t) for t in c["allowed"]}
        witness = {}
        universal = True
        for left in (0, 1):
            for right in (0, 1):
                possible = []
                for leaf_value in (0, 1):
                    a = {gateway[0]: left, gateway[1]: right, leaf: leaf_value}
                    if tuple(a[v] for v in scope) in allowed:
                        possible.append(leaf_value)
                if not possible:
                    universal = False
                    break
                witness[f"{left}{right}"] = possible[0]
            if not universal:
                break
        if universal and set(witness) == {"00", "01", "10", "11"}:
            eligible.append({
                "constraint_id": c["id"],
                "leaf": leaf,
                "gateway": gateway,
                "boundary_support_count": 4,
                "canonical_witnesses": witness,
            })
    eligible.sort(key=lambda x: x["constraint_id"])
    removed_ids = {x["constraint_id"] for x in eligible}
    removed_leaves = {int(x["leaf"]) for x in eligible}
    reduced = canonicalize({
        "variables": [int(v) for v in original["variables"] if int(v) not in removed_leaves],
        "constraints": [c for c in original["constraints"] if c["id"] not in removed_ids],
    })
    semantics = {
        "all_removed_leaves_absent_from_retained_constraints": all(
            not (removed_leaves & set(int(v) for v in c["scope"])) for c in reduced["constraints"]
        ),
        "all_witness_tables_complete_4_of_4": all(
            set(x["canonical_witnesses"]) == {"00", "01", "10", "11"} for x in eligible
        ),
        "all_removed_leaves_had_original_global_incidence_one": all(
            incidence[int(x["leaf"])] == 1 for x in eligible
        ),
    }
    semantics["all_and_only_target_constraints_removed"] = (
        {c["id"] for c in reduced["constraints"]}
        == {c["id"] for c in original["constraints"] if c["id"] not in removed_ids}
    )
    semantics["reverse_extension_independent_by_unique_leaf_incidence"] = semantics[
        "all_removed_leaves_had_original_global_incidence_one"
    ]
    semantics["exact_existential_projection_equivalence"] = all(semantics.values())
    return {
        "source": source,
        "selected_clause_ordinals": ordinals,
        "original_projected_raw_sha256": obj_sha(original),
        "original_variable_count": len(original["variables"]),
        "original_constraint_count": len(original["constraints"]),
        "original_incidence_counts": {str(k): int(v) for k, v in sorted(incidence.items())},
        "eligible_attachments": eligible,
        "eligible_attachment_count": len(eligible),
        "removed_constraint_ids": sorted(removed_ids),
        "removed_leaves": sorted(removed_leaves),
        "reduced_raw_sha256": obj_sha(reduced),
        "reduced_variable_count": len(reduced["variables"]),
        "reduced_constraint_count": len(reduced["constraints"]),
        "semantics_certificate": semantics,
        "source_pass": semantics["exact_existential_projection_equivalence"],
    }


def authority_guard(pre: dict, review: dict) -> dict:
    authority = {str(p.relative_to(ROOT)): git_blob(p) == sha for p, sha in EXPECTED_AUTHORITY_BLOBS.items()}
    rows = pre.get("frozen_fresh_source_manifest", [])
    source_bindings = {}
    for row in rows:
        p = ROOT / row["path"]
        source_bindings[row["source"]] = (
            p.is_file()
            and p.stat().st_size == int(row["size_bytes"])
            and git_blob(p) == row["git_blob_sha1"]
        )
    return {
        "authority_bindings": authority,
        "source_bindings": source_bindings,
        "review_authorized": review.get("review_verdict") == "PASS_CLEAN_REVIEW_GENERIC_PREPROCESSING_EXECUTION_AUTHORIZED_ON_FROZEN_FIVE_SOURCE_PANEL_ONLY",
        "ok": all(authority.values()) and len(source_bindings) == 5 and all(source_bindings.values()),
    }


def main(candidate_path: Path) -> dict:
    pre = json.loads(PREREG.read_text(encoding="utf-8"))
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    guard = authority_guard(pre, review)
    if not guard["ok"]:
        return {"verdict": "FAIL_INDEPENDENT_AUTHORITY_GUARD", "guard": guard}

    # Critical anti-leak ordering: independently compute the complete expected rows
    # before reading any candidate-selected target IDs or candidate result values.
    expected_rows = [derive_expected(row) for row in pre["frozen_fresh_source_manifest"]]
    expected_total = sum(row["eligible_attachment_count"] for row in expected_rows)
    expected_verdict = (
        "PASS_GENERIC_PREPROCESSING_NO_ELIGIBLE_PENDANTS"
        if expected_total == 0
        else "PASS_GENERIC_SOURCE_INDEPENDENT_ONE_ROUND_PREPROCESSING"
    )

    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    candidate_rows = candidate.get("rows", [])
    by_source = {row.get("source"): row for row in candidate_rows}
    comparisons = {}
    fields = [
        "selected_clause_ordinals",
        "original_projected_raw_sha256",
        "original_variable_count",
        "original_constraint_count",
        "original_incidence_counts",
        "eligible_attachments",
        "eligible_attachment_count",
        "removed_constraint_ids",
        "removed_leaves",
        "reduced_raw_sha256",
        "reduced_variable_count",
        "reduced_constraint_count",
        "semantics_certificate",
        "source_pass",
    ]
    for expected in expected_rows:
        source = expected["source"]
        actual = by_source.get(source)
        comparisons[source] = {
            field: actual is not None and actual.get(field) == expected.get(field)
            for field in fields
        }
    receipt = candidate.get("resource_receipt", {})
    forbidden_zero = {
        "WL_values_computed": receipt.get("WL_values_computed") == 0,
        "portfolio_replays": receipt.get("portfolio_replays") == 0,
        "solver_invocations": receipt.get("solver_invocations") == 0,
        "route_labels_computed": receipt.get("route_labels_computed") == 0,
        "automorphism_tests": receipt.get("automorphism_tests") == 0,
        "group_searches": receipt.get("group_searches") == 0,
        "new_carrier_mechanisms": receipt.get("new_carrier_mechanisms") == 0,
        "new_adapter_mechanisms": receipt.get("new_adapter_mechanisms") == 0,
        "new_quotient_mechanisms": receipt.get("new_quotient_mechanisms") == 0,
    }
    all_rows_equal = len(candidate_rows) == 5 and all(
        all(checks.values()) for checks in comparisons.values()
    )
    verdict_match = candidate.get("verdict") == expected_verdict
    pass_all = all_rows_equal and verdict_match and all(forbidden_zero.values())
    return {
        "artifact_id": "JANUS-TRUMP-UF20-FRESH-GENERIC-PREPROCESSING-INDEPENDENT-CHECK-2026-09-17-v1.0",
        "verdict": "PASS_INDEPENDENT_GENERIC_PREPROCESSING_VERIFICATION" if pass_all else "FAIL_INDEPENDENT_PREPROCESSING_DISAGREEMENT",
        "guard": guard,
        "independent_expected_verdict": expected_verdict,
        "independent_total_eligible_attachments": expected_total,
        "comparisons": comparisons,
        "candidate_verdict_match": verdict_match,
        "forbidden_resource_receipt_zero": forbidden_zero,
        "candidate_module_imported": False,
        "candidate_target_ids_read_before_independent_computation": False,
        "resource_receipt": {
            "WL_values_computed": 0,
            "portfolio_replays": 0,
            "solver_invocations": 0,
            "route_labels_computed": 0,
        },
        "scientific_firewall": {
            "P_VS_NP": "OPEN",
            "GENERAL_SAT_IN_P": "NOT_PROVED",
            "GENERAL_GT2_TRACTABILITY": "NOT_PROVED",
            "CONNECTED_MIXED_CORE_SOLVED": "NO",
        },
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: independent_check.py CANDIDATE_RESULT.json")
    print(json.dumps(main(Path(sys.argv[1])), sort_keys=True, separators=(",", ":")))
