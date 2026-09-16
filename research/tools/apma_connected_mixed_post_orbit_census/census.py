from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

from research.tools.apma_unseen_basis import raw_relation_basis as raw_basis
from research.tools.apma_unseen_basis import compositional_basis
from research.tools.apma_log_alien_transfer import log_alien_transfer
from research.tools.apma_inverted_pyramid import inverted_pyramid
from research.tools.apma_unseen_local_invariant_orbit_count import candidate as orbit_candidate
from research.tools.apma_unseen_local_invariant_orbit_count import independent_checker as orbit_checker


ARTIFACT_ID = "JANUS-TRUMP-SOURCE-AUTHORIZED-CONNECTED-MIXED-RAW-POST-ORBIT-PORTFOLIO-OBSTRUCTION-CENSUS-CANDIDATE-2026-09-16-v1.0"
AUTHORITY = "DIAGNOSTIC_CANDIDATE__NO_NEW_SOLVER_OR_CARRIER"
PREREG = Path("research/TRUMP_SOURCE_AUTHORIZED_CONNECTED_MIXED_RAW_POST_ORBIT_PORTFOLIO_OBSTRUCTION_CENSUS_PREREGISTRATION_2026-09-16.json")
CLARIFICATION = Path("research/TRUMP_SOURCE_AUTHORIZED_CONNECTED_MIXED_RAW_POST_ORBIT_PORTFOLIO_OBSTRUCTION_CENSUS_PREREGISTRATION_CLARIFICATION_2026-09-16.json")
PREREG_BLOB = "d06e91e29455b333f2264e745b179c9fb61bbc3c"
CLARIFICATION_BLOB = "9af2b16a112b83817a9cb15d0e20301c0fc20a61"

SOURCE_BLOBS = {
    "research/tools/apma_unseen_basis/raw_relation_basis.py": "63490c05ef3e91a4f682f75da26ff2af811839a6",
    "research/TRUMP_RAW_RELATION_SCHAEFER_BASIS_INDUCTION_PREREGISTRATION_2026-09-15.json": "92c6e6978f171a800db82bd6ae2e3c7112d65e22",
    "research/tools/apma_unseen_basis/compositional_basis.py": "fdc83a3368a4ad362f00d3ee8aad958f06f8d264",
    "research/TRUMP_RAW_COMPOSITIONAL_BASIS_INDUCTION_PREREGISTRATION_2026-09-15.json": "212eeb78a08b8a558248873f50a776bed61a7748",
    "research/tools/apma_log_alien_transfer/log_alien_transfer.py": "d20cd94fa2e0324e301f55211152c2d410099425",
    "research/TRUMP_LOG_ALIEN_CONSTRAINT_EXACT_TRANSFER_PREREGISTRATION_2026-09-15.json": "99223e98059a00ad48ef6acda75450dc0ef029b7",
    "research/tools/apma_inverted_pyramid/inverted_pyramid.py": "879e60703ef200ac12a4ec1d71218cd958dcc0c8",
    "research/TRUMP_INVERTED_PYRAMID_ADMISSION_V2_PREREGISTRATION_2026-09-15.json": "6f25ed436f19fac2b9d77adb45e48392f41362a8",
    "research/tools/apma_mixed_carrier_barrier/check_schaefer_barrier.py": "11fcacd5f0c550543f96648a7965734308509d22",
    "research/TRUMP_CONNECTED_MIXED_CARRIER_SCHAEFER_BARRIER_PREREGISTRATION_2026-09-15.json": "1b86e6f4be243ad64dc5933721cbead89ec81046",
    "research/tools/apma_unseen_local_invariant_orbit_count/candidate.py": "a076cfc56d68aad0348415e313705da1f6b9cdcd",
    "research/tools/apma_unseen_local_invariant_orbit_count/independent_checker.py": "0e12304d843ef0bcce6b6c032fd2af2c68abcd14",
    "research/TRUMP_APMA_UNSEEN_LOCAL_INVARIANT_STAGE_C_BLIND_EXECUTION_RESULT_2026-09-16.json": "e9c819a90ae9b6a55936c5062067a6c636695237",
    "registry/TRUMP_CURRENT_STATE_2026-09-16_v3.22.json": "a8cd4e3fe62f4db59cbd43588b877ecfca4c7517",
    "registry/TRUMP_APMA_UNSEEN_LOCAL_INVARIANT_STAGE_C_AUTHORITY_AUDIT_2026-09-16.json": "4cc517e25420287f61c26042495182b32efac3e4",
}

ORBIT_ADMIT = {"ADMIT_ORBIT_COUNT_QUOTIENT_SAT", "ADMIT_ORBIT_COUNT_QUOTIENT_UNSAT"}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    h = hashlib.sha1()
    h.update(f"blob {len(data)}\0".encode("ascii"))
    h.update(data)
    return h.hexdigest()


def source_guard() -> dict[str, Any]:
    root = repo_root()
    observed = {
        "prereg_blob": git_blob_sha1(root / PREREG),
        "clarification_blob": git_blob_sha1(root / CLARIFICATION),
    }
    expected = {"prereg_blob": PREREG_BLOB, "clarification_blob": CLARIFICATION_BLOB}
    checks: dict[str, bool] = {k: observed[k] == expected[k] for k in expected}
    for rel, want in SOURCE_BLOBS.items():
        checks[rel] = git_blob_sha1(root / rel) == want
    prereg = json.loads((root / PREREG).read_text(encoding="utf-8"))
    clarification = json.loads((root / CLARIFICATION).read_text(encoding="utf-8"))
    checks["prereg_status"] = prereg.get("status") == "FROZEN_BEFORE_CENSUS_IMPLEMENTATION"
    checks["clarification_status"] = clarification.get("status") == "FROZEN_BEFORE_CENSUS_IMPLEMENTATION__NO_RESULT_DATA_OBSERVED"
    return {"ok": all(checks.values()), "checks": checks, **observed}


def _bits(row: Any) -> tuple[int, ...]:
    if isinstance(row, str):
        return tuple(int(ch) for ch in row)
    return tuple(int(x) for x in row)


def diagonal_restrict(scope: list[int], allowed: list[Any]) -> tuple[list[int], list[list[int]]]:
    unique: list[int] = []
    seen: set[int] = set()
    for v in scope:
        v = int(v)
        if v not in seen:
            seen.add(v)
            unique.append(v)
    allowed_positional = {_bits(row) for row in allowed}
    if any(len(row) != len(scope) for row in allowed_positional):
        raise ValueError("SOURCE_ALLOWED_ARITY_MISMATCH")
    kept: list[list[int]] = []
    for assignment in itertools.product((0, 1), repeat=len(unique)):
        mapping = dict(zip(unique, assignment, strict=True))
        positional = tuple(mapping[int(v)] for v in scope)
        if positional in allowed_positional:
            kept.append(list(assignment))
    return unique, kept


def is_universal(scope: list[int], allowed: list[list[int]]) -> bool:
    return len({tuple(row) for row in allowed}) == (1 << len(scope))


def normalize_constraint(scope: list[int], allowed: list[Any]) -> tuple[list[int], list[list[int]]] | None:
    unique, rows = diagonal_restrict([int(v) for v in scope], allowed)
    rows = [list(row) for row in sorted({tuple(row) for row in rows})]
    if is_universal(unique, rows):
        return None
    return unique, rows


def affine_allowed(ob: dict[str, Any]) -> tuple[list[int], list[list[int]]]:
    coefficients: dict[int, int] = {}
    for raw_v, raw_bit in ob.get("coeff", {}).items():
        v = int(raw_v)
        coefficients[v] = coefficients.get(v, 0) ^ (int(raw_bit) & 1)
    scope = [int(v) for v in ob.get("scope", []) if coefficients.get(int(v), 0)]
    dedup_scope: list[int] = []
    seen: set[int] = set()
    for v in scope:
        if v not in seen:
            seen.add(v)
            dedup_scope.append(v)
    rhs = int(ob.get("rhs", 0)) & 1
    rows: list[list[int]] = []
    for assignment in itertools.product((0, 1), repeat=len(dedup_scope)):
        mapping = dict(zip(dedup_scope, assignment, strict=True))
        total = 0
        for v, bit in coefficients.items():
            if bit:
                total ^= mapping.get(v, 0)
        if total == rhs:
            rows.append(list(assignment))
    return dedup_scope, rows


def canonical_raw_from_constraints(constraints: list[tuple[list[int], list[Any]]]) -> dict[str, Any]:
    normalized: list[tuple[tuple[int, ...], tuple[tuple[int, ...], ...]]] = []
    for scope, allowed in constraints:
        reduced = normalize_constraint(scope, allowed)
        if reduced is None:
            continue
        rscope, rows = reduced
        normalized.append((tuple(rscope), tuple(tuple(int(x) for x in row) for row in rows)))
    normalized.sort()
    variables = sorted({v for scope, _ in normalized for v in scope})
    raw_constraints = [
        {"id": f"c{i:03d}", "scope": list(scope), "allowed": [list(row) for row in rows]}
        for i, (scope, rows) in enumerate(normalized)
    ]
    raw = {"variables": variables, "constraints": raw_constraints}
    # The sealed V1 normalizer is the canonical semantic-hash authority.
    formula = orbit_candidate.validate_and_normalize(raw)
    return {
        "raw": raw,
        "semantic_sha256": formula.semantic_sha256,
        "semantic_bytes_L": formula.L,
    }


def normalize_raw_object(raw: dict[str, Any]) -> dict[str, Any]:
    rows = [(list(c["scope"]), list(c["allowed"])) for c in raw["constraints"]]
    return canonical_raw_from_constraints(rows)


def normalize_log_alien(instance: dict[str, Any]) -> dict[str, Any]:
    rows: list[tuple[list[int], list[Any]]] = []
    for c in list(instance["base_constraints"]) + list(instance["alien_constraints"]):
        kind = str(c["kind"])
        if kind not in log_alien_transfer.RELATIONS:
            raise ValueError(f"UNKNOWN_FROZEN_RELATION_KIND:{kind}")
        rows.append((list(c["scope"]), [list(t) for t in log_alien_transfer.RELATIONS[kind]]))
    return canonical_raw_from_constraints(rows)


def normalize_feedback_case(case: dict[str, Any]) -> dict[str, Any]:
    instance = case["payload"]["instance"]
    rows: list[tuple[list[int], list[Any]]] = []
    for ob in instance["obligations"]:
        kind = ob.get("kind")
        if kind == "raw_table":
            rows.append((list(ob["scope"]), [_bits(x) for x in ob["allowed"]]))
        elif kind == "affine_eq":
            scope, allowed = affine_allowed(ob)
            rows.append((scope, allowed))
        else:
            raise ValueError(f"UNSUPPORTED_SOURCE_OBLIGATION_KIND:{kind}")
    return canonical_raw_from_constraints(rows)


def build_sources() -> list[dict[str, Any]]:
    p1 = log_alien_transfer.connected_or2_xor_sat()
    p2 = log_alien_transfer.connected_or2_xor_unsat()
    p3 = log_alien_transfer.connected_affine_or2_sat()
    unsupported = inverted_pyramid.unsupported_connected_mixed_feedback_case()
    overbudget = inverted_pyramid.alien_over_budget_case()
    overbudget_instance = overbudget["payload"]["instance"]
    return [
        {"source_id": "RAW_RELATION_BASIS__RAW_MIXED", "normalized": normalize_raw_object(raw_basis.raw_mixed())},
        {"source_id": "COMPOSITIONAL_BASIS__CONNECTED_MIXED", "normalized": normalize_raw_object(compositional_basis.connected_mixed())},
        {"source_id": "COMPOSITIONAL_BASIS__BRIDGED_MIXED", "normalized": normalize_raw_object(compositional_basis.bridged_mixed())},
        {"source_id": "LOG_ALIEN__CONNECTED_OR2_XOR_SAT", "normalized": normalize_log_alien(p1), "log_instance": p1},
        {"source_id": "LOG_ALIEN__CONNECTED_OR2_XOR_UNSAT", "normalized": normalize_log_alien(p2), "log_instance": p2},
        {"source_id": "LOG_ALIEN__CONNECTED_AFFINE_OR2_SAT", "normalized": normalize_log_alien(p3), "log_instance": p3},
        {"source_id": "INVERTED_PYRAMID__UNSUPPORTED_CONNECTED_MIXED_FEEDBACK", "normalized": normalize_feedback_case(unsupported), "inverted_case": unsupported},
        {"source_id": "INVERTED_PYRAMID__ALIEN_OVER_BUDGET_ALIAS", "normalized": normalize_log_alien(overbudget_instance), "log_instance": overbudget_instance, "inverted_case": overbudget},
    ]


def connected_incidence(raw: dict[str, Any]) -> bool:
    constraints = raw["constraints"]
    if not constraints:
        return False
    parent = list(range(len(constraints)))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            if ra > rb:
                ra, rb = rb, ra
            parent[rb] = ra

    first: dict[int, int] = {}
    for i, c in enumerate(constraints):
        for v in c["scope"]:
            if v in first:
                union(i, first[v])
            else:
                first[v] = i
    return len({find(i) for i in range(len(constraints))}) == 1


def replay_log_aliases(aliases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    receipts: list[dict[str, Any]] = []
    for alias in sorted(aliases, key=lambda x: x["source_id"]):
        if "log_instance" not in alias:
            continue
        result = log_alien_transfer.solve_instance(alias["log_instance"])
        receipts.append({
            "source_id": alias["source_id"],
            "status": result.get("status"),
            "L": result.get("L"),
            "q": result.get("q"),
            "k": result.get("k"),
            "q_pow_k": result.get("q_pow_k"),
            "exact_replay": result.get("exact_replay"),
            "complete_branch_accounting": result.get("complete_branch_accounting"),
            "metrics": result.get("metrics", {}),
        })
    return receipts


def replay_inverted_aliases(aliases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    receipts: list[dict[str, Any]] = []
    for alias in sorted(aliases, key=lambda x: x["source_id"]):
        if "inverted_case" not in alias:
            continue
        result = inverted_pyramid.route(alias["inverted_case"])
        receipts.append({
            "source_id": alias["source_id"],
            "status": result.get("status"),
            "admission": result.get("admission", {}),
            "metrics": result.get("metrics", {}),
        })
    return receipts


def classify_unique_row(sha: str, aliases: list[dict[str, Any]]) -> dict[str, Any]:
    raw = aliases[0]["normalized"]["raw"]
    basis = raw_basis.induce_basis(raw)
    if basis.get("status") == "HALT_SOURCE_GUARD":
        return {"classification": "HALT_SOURCE_GUARD", "basis": basis}
    connected = connected_incidence(raw)
    mixed = basis.get("status") == "OPEN_NO_SCHAEFER_BASIS"
    base = {
        "raw_semantic_sha256": sha,
        "source_aliases": sorted(a["source_id"] for a in aliases),
        "normalized_raw": raw,
        "variables_n": len(raw["variables"]),
        "constraints": len(raw["constraints"]),
        "connected": connected,
        "mixed_after_exact_normalization": mixed,
        "basis_status": basis.get("status"),
        "basis_selected": basis.get("selected_basis"),
        "language_fingerprint": basis.get("language_fingerprint"),
    }
    if not connected or not mixed:
        return {
            **base,
            "classification": "EXCLUDED_AFTER_EXACT_NORMALIZATION_NOT_CONNECTED_MIXED",
            "sealed_receipts": {"raw_basis": basis},
        }

    compositional = compositional_basis.induce_compositional_basis(raw)
    log_receipts = replay_log_aliases(aliases)
    log_closed = [r for r in log_receipts if r["status"] in {"SAT", "UNSAT"}]
    inverted_receipts = replay_inverted_aliases(aliases)

    orbit = orbit_candidate.run_candidate(raw)
    orbit_check: dict[str, Any] | None = None
    if orbit.get("status") in ORBIT_ADMIT:
        orbit_check = orbit_checker.verify(raw, orbit)
        if orbit_check.get("verified") is not True:
            return {
                **base,
                "classification": "FAIL_EXACT_REPLAY_OR_CERTIFICATE",
                "sealed_receipts": {"orbit": orbit, "orbit_check": orbit_check},
            }

    receipts = {
        "raw_basis": basis,
        "compositional": {
            "status": compositional.get("status"),
            "open_component_count": compositional.get("open_component_count"),
            "component_count": compositional.get("component_count"),
        },
        "log_alien": log_receipts,
        "inverted_pyramid": inverted_receipts,
        "orbit_count": orbit,
        "orbit_count_independent_check": orbit_check,
    }

    # Frozen precedence from preregistration. Connected-mixed eligibility has already
    # ruled out a common raw Schaefer basis and variable-disjoint compositional closure.
    if log_closed:
        return {
            **base,
            "classification": "CLOSED_BY_SEALED_LOG_ALIEN_TRANSFER",
            "closing_receipt": sorted(log_closed, key=lambda r: r["source_id"])[0],
            "sealed_receipts": receipts,
        }
    routed = [r for r in inverted_receipts if r.get("status") == "ROUTED"]
    if routed:
        return {
            **base,
            "classification": "CLOSED_BY_SEALED_INVERTED_PYRAMID_DOOR",
            "closing_receipt": sorted(routed, key=lambda r: r["source_id"])[0],
            "sealed_receipts": receipts,
        }
    if orbit.get("status") in ORBIT_ADMIT and orbit_check and orbit_check.get("verified") is True:
        return {
            **base,
            "classification": "CLOSED_BY_SEALED_ORBIT_COUNT_V1",
            "closing_receipt": {
                "status": orbit.get("status"),
                "Q": orbit.get("quotient_states_Q"),
                "cells": orbit.get("cells"),
                "certificate_type": orbit.get("certificate", {}).get("type"),
            },
            "sealed_receipts": receipts,
        }
    return {
        **base,
        "classification": "REMAINS_OPEN_SOURCE_AUTHORIZED_CONNECTED_MIXED_RAW_POST_ORBIT",
        "open_profile": {
            "compositional_status": compositional.get("status"),
            "log_alien_statuses": [r.get("status") for r in log_receipts],
            "inverted_statuses": [r.get("status") for r in inverted_receipts],
            "orbit_status": orbit.get("status"),
            "orbit_cells": orbit.get("cells"),
            "orbit_Q": orbit.get("quotient_states_Q"),
        },
        "sealed_receipts": receipts,
    }


def run_census() -> dict[str, Any]:
    guard = source_guard()
    if not guard["ok"]:
        return {
            "artifact_id": ARTIFACT_ID,
            "authority": AUTHORITY,
            "verdict": "FAIL_SOURCE_OR_CLASSIFICATION_MISMATCH",
            "source_guard": guard,
            "scientific_firewall": firewall(),
        }

    sources = build_sources()
    groups: dict[str, list[dict[str, Any]]] = {}
    source_ledger: list[dict[str, Any]] = []
    for entry in sources:
        sha = entry["normalized"]["semantic_sha256"]
        groups.setdefault(sha, []).append(entry)
        source_ledger.append({
            "source_id": entry["source_id"],
            "raw_semantic_sha256": sha,
            "normalized_variables_n": len(entry["normalized"]["raw"]["variables"]),
            "normalized_constraints": len(entry["normalized"]["raw"]["constraints"]),
        })

    rows = [classify_unique_row(sha, groups[sha]) for sha in sorted(groups)]
    fail_rows = [r for r in rows if r["classification"] in {"HALT_SOURCE_GUARD", "FAIL_EXACT_REPLAY_OR_CERTIFICATE"}]
    open_rows = [r for r in rows if r["classification"] == "REMAINS_OPEN_SOURCE_AUTHORIZED_CONNECTED_MIXED_RAW_POST_ORBIT"]
    eligible_rows = [r for r in rows if r.get("connected") is True and r.get("mixed_after_exact_normalization") is True]
    first_open = open_rows[0] if open_rows else None

    if fail_rows:
        verdict = "FAIL_EXACT_REPLAY_OR_CERTIFICATE"
    elif open_rows:
        verdict = "PASS_DIAGNOSTIC_SOURCE_AUTHORIZED_CONNECTED_MIXED_RAW_POST_ORBIT_OBSTRUCTION_FOUND_AND_FROZEN"
    else:
        verdict = "PASS_DIAGNOSTIC_NO_SOURCE_AUTHORIZED_CONNECTED_MIXED_RAW_POST_ORBIT_OBSTRUCTION_FOUND"

    counts: dict[str, int] = {}
    for row in rows:
        counts[row["classification"]] = counts.get(row["classification"], 0) + 1

    return {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "gate": "TRUMP_SOURCE_AUTHORIZED_CONNECTED_MIXED_RAW_POST_ORBIT_PORTFOLIO_OBSTRUCTION_CENSUS",
        "source_guard": guard,
        "source_entry_count": len(source_ledger),
        "unique_raw_count": len(rows),
        "eligible_connected_mixed_unique_raw_count": len(eligible_rows),
        "open_post_orbit_obstruction_count": len(open_rows),
        "classification_counts": counts,
        "source_ledger": sorted(source_ledger, key=lambda x: x["source_id"]),
        "rows": rows,
        "first_open_obstruction": first_open,
        "verdict": verdict,
        "resource_receipt": {
            "new_solver_mechanisms": 0,
            "new_carrier_semantics": 0,
            "separator_ge3_boolean_branches": 0,
            "size4_boolean_separator_assignments": 0,
            "new_unbounded_recursion": 0,
            "new_three_plus_join_chains": 0,
            "global_residual_cartesian_products_materialized": 0,
            "budget_raise": False,
            "full_global_variable_cube_fallback": 0,
        },
        "scientific_firewall": firewall(),
    }


def firewall() -> dict[str, Any]:
    return {
        "P_VS_NP": "OPEN",
        "GENERAL_SAT_IN_P": "NOT_PROVED",
        "CONNECTED_MIXED_CORE_SOLVED": "NO",
        "GENERAL_CONNECTED_MIXED_TRACTABILITY": "NOT_PROVED",
        "ARBITRARY_UNSEEN_INVARIANT_DISCOVERY": "NOT_PROVED",
        "GENERAL_GT2_TRACTABILITY": "NOT_PROVED",
        "GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY": "NOT_PROVED",
        "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE_UNTIL_POST_RESULT_HQ_REVIEW",
    }


def main() -> None:
    print(json.dumps(run_census(), sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
