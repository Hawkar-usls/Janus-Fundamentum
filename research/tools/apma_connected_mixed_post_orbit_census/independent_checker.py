from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

from research.tools.apma_unseen_basis import raw_relation_basis as raw_basis
from research.tools.apma_unseen_basis import compositional_basis
from research.tools.apma_log_alien_transfer import log_alien_transfer
from research.tools.apma_inverted_pyramid import inverted_pyramid
from research.tools.apma_unseen_local_invariant_orbit_count import candidate as sealed_orbit_candidate
from research.tools.apma_unseen_local_invariant_orbit_count import independent_checker as sealed_orbit_checker


ARTIFACT_ID = "JANUS-TRUMP-SOURCE-AUTHORIZED-CONNECTED-MIXED-RAW-POST-ORBIT-PORTFOLIO-OBSTRUCTION-CENSUS-INDEPENDENT-CHECKER-2026-09-16-v1.0"
PREREG = Path("research/TRUMP_SOURCE_AUTHORIZED_CONNECTED_MIXED_RAW_POST_ORBIT_PORTFOLIO_OBSTRUCTION_CENSUS_PREREGISTRATION_2026-09-16.json")
CLARIFICATION = Path("research/TRUMP_SOURCE_AUTHORIZED_CONNECTED_MIXED_RAW_POST_ORBIT_PORTFOLIO_OBSTRUCTION_CENSUS_PREREGISTRATION_CLARIFICATION_2026-09-16.json")
CANDIDATE = Path("research/tools/apma_connected_mixed_post_orbit_census/census.py")
EXPECTED = {
    str(PREREG): "d06e91e29455b333f2264e745b179c9fb61bbc3c",
    str(CLARIFICATION): "9af2b16a112b83817a9cb15d0e20301c0fc20a61",
    str(CANDIDATE): "e8557cc316903f58d59c28c2c75f68f4e0d40473",
    "research/tools/apma_unseen_basis/raw_relation_basis.py": "63490c05ef3e91a4f682f75da26ff2af811839a6",
    "research/tools/apma_unseen_basis/compositional_basis.py": "fdc83a3368a4ad362f00d3ee8aad958f06f8d264",
    "research/tools/apma_log_alien_transfer/log_alien_transfer.py": "d20cd94fa2e0324e301f55211152c2d410099425",
    "research/tools/apma_inverted_pyramid/inverted_pyramid.py": "879e60703ef200ac12a4ec1d71218cd958dcc0c8",
    "research/tools/apma_unseen_local_invariant_orbit_count/candidate.py": "a076cfc56d68aad0348415e313705da1f6b9cdcd",
    "research/tools/apma_unseen_local_invariant_orbit_count/independent_checker.py": "0e12304d843ef0bcce6b6c032fd2af2c68abcd14",
}
ORBIT_ADMIT = {"ADMIT_ORBIT_COUNT_QUOTIENT_SAT", "ADMIT_ORBIT_COUNT_QUOTIENT_UNSAT"}


def root() -> Path:
    return Path(__file__).resolve().parents[3]


def blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def source_guard() -> dict[str, Any]:
    observed = {rel: blob_sha(root() / rel) for rel in EXPECTED}
    checks = {rel: observed[rel] == want for rel, want in EXPECTED.items()}
    return {
        "ok": all(checks.values()),
        "checks": checks,
        "observed": observed,
        "candidate_helpers_imported": False,
    }


def parse_tuple(value: Any) -> tuple[int, ...]:
    if isinstance(value, str):
        return tuple(int(ch) for ch in value)
    return tuple(int(x) for x in value)


def exact_diagonal(scope: list[int], allowed: list[Any]) -> tuple[list[int], list[list[int]]]:
    distinct: list[int] = []
    for raw_v in scope:
        v = int(raw_v)
        if v not in distinct:
            distinct.append(v)
    rel = {parse_tuple(t) for t in allowed}
    if any(len(t) != len(scope) for t in rel):
        raise AssertionError("SOURCE_ARITY_MISMATCH")
    rows: list[list[int]] = []
    for bits in itertools.product((0, 1), repeat=len(distinct)):
        a = dict(zip(distinct, bits, strict=True))
        positional = tuple(a[int(v)] for v in scope)
        if positional in rel:
            rows.append(list(bits))
    return distinct, rows


def reduce_relation(scope: list[int], allowed: list[Any]) -> tuple[list[int], list[list[int]]] | None:
    s, rows = exact_diagonal(scope, allowed)
    rows = [list(t) for t in sorted({tuple(r) for r in rows})]
    if len(rows) == (1 << len(s)):
        return None
    return s, rows


def exact_affine_table(ob: dict[str, Any]) -> tuple[list[int], list[list[int]]]:
    coeff: dict[int, int] = {}
    for raw_v, raw_bit in ob.get("coeff", {}).items():
        v = int(raw_v)
        coeff[v] = coeff.get(v, 0) ^ (int(raw_bit) & 1)
    scope: list[int] = []
    for raw_v in ob.get("scope", []):
        v = int(raw_v)
        if coeff.get(v, 0) and v not in scope:
            scope.append(v)
    rhs = int(ob.get("rhs", 0)) & 1
    rows: list[list[int]] = []
    for bits in itertools.product((0, 1), repeat=len(scope)):
        a = dict(zip(scope, bits, strict=True))
        lhs = 0
        for v, bit in coeff.items():
            if bit:
                lhs ^= a.get(v, 0)
        if lhs == rhs:
            rows.append(list(bits))
    return scope, rows


def canonical_raw(relations: list[tuple[list[int], list[Any]]]) -> tuple[dict[str, Any], str]:
    canon: list[tuple[tuple[int, ...], tuple[tuple[int, ...], ...]]] = []
    for scope, allowed in relations:
        reduced = reduce_relation([int(v) for v in scope], allowed)
        if reduced is None:
            continue
        s, rows = reduced
        canon.append((tuple(s), tuple(tuple(int(x) for x in row) for row in rows)))
    canon.sort()
    variables = sorted({v for s, _ in canon for v in s})
    raw = {
        "variables": variables,
        "constraints": [
            {"id": f"i{i:03d}", "scope": list(s), "allowed": [list(t) for t in rows]}
            for i, (s, rows) in enumerate(canon)
        ],
    }
    formula = sealed_orbit_checker.normalize(raw)
    return raw, formula.semantic_sha256


def raw_from_native(raw: dict[str, Any]) -> tuple[dict[str, Any], str]:
    return canonical_raw([(list(c["scope"]), list(c["allowed"])) for c in raw["constraints"]])


def raw_from_alien(instance: dict[str, Any]) -> tuple[dict[str, Any], str]:
    rows: list[tuple[list[int], list[Any]]] = []
    for c in list(instance["base_constraints"]) + list(instance["alien_constraints"]):
        kind = str(c["kind"])
        rows.append((list(c["scope"]), [list(t) for t in log_alien_transfer.RELATIONS[kind]]))
    return canonical_raw(rows)


def raw_from_feedback(case: dict[str, Any]) -> tuple[dict[str, Any], str]:
    rows: list[tuple[list[int], list[Any]]] = []
    for ob in case["payload"]["instance"]["obligations"]:
        if ob["kind"] == "raw_table":
            rows.append((list(ob["scope"]), [parse_tuple(t) for t in ob["allowed"]]))
        elif ob["kind"] == "affine_eq":
            rows.append(exact_affine_table(ob))
        else:
            raise AssertionError(f"UNEXPECTED_OBLIGATION_KIND:{ob['kind']}")
    return canonical_raw(rows)


def rebuild_sources() -> list[dict[str, Any]]:
    p1 = log_alien_transfer.connected_or2_xor_sat()
    p2 = log_alien_transfer.connected_or2_xor_unsat()
    p3 = log_alien_transfer.connected_affine_or2_sat()
    fb = inverted_pyramid.unsupported_connected_mixed_feedback_case()
    ob = inverted_pyramid.alien_over_budget_case()
    ob_instance = ob["payload"]["instance"]

    def native(source_id: str, obj: dict[str, Any]) -> dict[str, Any]:
        raw, sha = raw_from_native(obj)
        return {"source_id": source_id, "raw": raw, "sha": sha}

    def alien(source_id: str, instance: dict[str, Any], *, case: dict[str, Any] | None = None) -> dict[str, Any]:
        raw, sha = raw_from_alien(instance)
        out = {"source_id": source_id, "raw": raw, "sha": sha, "log_instance": instance}
        if case is not None:
            out["inverted_case"] = case
        return out

    fb_raw, fb_sha = raw_from_feedback(fb)
    return [
        native("RAW_RELATION_BASIS__RAW_MIXED", raw_basis.raw_mixed()),
        native("COMPOSITIONAL_BASIS__CONNECTED_MIXED", compositional_basis.connected_mixed()),
        native("COMPOSITIONAL_BASIS__BRIDGED_MIXED", compositional_basis.bridged_mixed()),
        alien("LOG_ALIEN__CONNECTED_OR2_XOR_SAT", p1),
        alien("LOG_ALIEN__CONNECTED_OR2_XOR_UNSAT", p2),
        alien("LOG_ALIEN__CONNECTED_AFFINE_OR2_SAT", p3),
        {"source_id": "INVERTED_PYRAMID__UNSUPPORTED_CONNECTED_MIXED_FEEDBACK", "raw": fb_raw, "sha": fb_sha, "inverted_case": fb},
        alien("INVERTED_PYRAMID__ALIEN_OVER_BUDGET_ALIAS", ob_instance, case=ob),
    ]


def is_connected(raw: dict[str, Any]) -> bool:
    rows = raw["constraints"]
    if not rows:
        return False
    parent = list(range(len(rows)))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        a, b = find(a), find(b)
        if a != b:
            if a > b:
                a, b = b, a
            parent[b] = a

    owner: dict[int, int] = {}
    for i, row in enumerate(rows):
        for v in row["scope"]:
            if v in owner:
                union(i, owner[v])
            else:
                owner[v] = i
    return len({find(i) for i in range(len(rows))}) == 1


def log_receipts(aliases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for a in sorted(aliases, key=lambda x: x["source_id"]):
        if "log_instance" not in a:
            continue
        r = log_alien_transfer.solve_instance(a["log_instance"])
        out.append({"source_id": a["source_id"], "status": r.get("status")})
    return out


def inverted_receipts(aliases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for a in sorted(aliases, key=lambda x: x["source_id"]):
        if "inverted_case" not in a:
            continue
        r = inverted_pyramid.route(a["inverted_case"])
        out.append({"source_id": a["source_id"], "status": r.get("status")})
    return out


def classify(sha: str, aliases: list[dict[str, Any]]) -> dict[str, Any]:
    raw = aliases[0]["raw"]
    basis = raw_basis.induce_basis(raw)
    connected = is_connected(raw)
    mixed = basis.get("status") == "OPEN_NO_SCHAEFER_BASIS"
    if not connected or not mixed:
        return {
            "raw_semantic_sha256": sha,
            "source_aliases": sorted(a["source_id"] for a in aliases),
            "normalized_raw": raw,
            "connected": connected,
            "mixed_after_exact_normalization": mixed,
            "basis_status": basis.get("status"),
            "classification": "EXCLUDED_AFTER_EXACT_NORMALIZATION_NOT_CONNECTED_MIXED",
        }

    comp = compositional_basis.induce_compositional_basis(raw)
    logs = log_receipts(aliases)
    inv = inverted_receipts(aliases)
    orbit = sealed_orbit_candidate.run_candidate(raw)
    orbit_check = None
    if orbit.get("status") in ORBIT_ADMIT:
        orbit_check = sealed_orbit_checker.verify(raw, orbit)
        if orbit_check.get("verified") is not True:
            raise AssertionError("SEALED_ORBIT_CERTIFICATE_FAILED")

    if any(r["status"] in {"SAT", "UNSAT"} for r in logs):
        classification = "CLOSED_BY_SEALED_LOG_ALIEN_TRANSFER"
    elif any(r["status"] == "ROUTED" for r in inv):
        classification = "CLOSED_BY_SEALED_INVERTED_PYRAMID_DOOR"
    elif orbit.get("status") in ORBIT_ADMIT and orbit_check and orbit_check.get("verified") is True:
        classification = "CLOSED_BY_SEALED_ORBIT_COUNT_V1"
    else:
        classification = "REMAINS_OPEN_SOURCE_AUTHORIZED_CONNECTED_MIXED_RAW_POST_ORBIT"

    return {
        "raw_semantic_sha256": sha,
        "source_aliases": sorted(a["source_id"] for a in aliases),
        "normalized_raw": raw,
        "connected": connected,
        "mixed_after_exact_normalization": mixed,
        "basis_status": basis.get("status"),
        "compositional_status": comp.get("status"),
        "log_statuses": [r["status"] for r in logs],
        "inverted_statuses": [r["status"] for r in inv],
        "orbit_status": orbit.get("status"),
        "orbit_verified": None if orbit_check is None else orbit_check.get("verified"),
        "classification": classification,
    }


def independent_result() -> dict[str, Any]:
    entries = rebuild_sources()
    groups: dict[str, list[dict[str, Any]]] = {}
    for e in entries:
        groups.setdefault(e["sha"], []).append(e)
    rows = [classify(sha, groups[sha]) for sha in sorted(groups)]
    open_rows = [r for r in rows if r["classification"] == "REMAINS_OPEN_SOURCE_AUTHORIZED_CONNECTED_MIXED_RAW_POST_ORBIT"]
    eligible = [r for r in rows if r["connected"] and r["mixed_after_exact_normalization"]]
    verdict = (
        "PASS_DIAGNOSTIC_SOURCE_AUTHORIZED_CONNECTED_MIXED_RAW_POST_ORBIT_OBSTRUCTION_FOUND_AND_FROZEN"
        if open_rows
        else "PASS_DIAGNOSTIC_NO_SOURCE_AUTHORIZED_CONNECTED_MIXED_RAW_POST_ORBIT_OBSTRUCTION_FOUND"
    )
    return {
        "source_entry_count": len(entries),
        "unique_raw_count": len(rows),
        "eligible_connected_mixed_unique_raw_count": len(eligible),
        "open_post_orbit_obstruction_count": len(open_rows),
        "rows": rows,
        "first_open_sha": open_rows[0]["raw_semantic_sha256"] if open_rows else None,
        "verdict": verdict,
    }


def verify_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    guard = source_guard()
    independent = independent_result()
    crows = {r["raw_semantic_sha256"]: r for r in candidate.get("rows", [])}
    irows = {r["raw_semantic_sha256"]: r for r in independent["rows"]}
    row_checks: dict[str, bool] = {}
    if set(crows) == set(irows):
        for sha in sorted(irows):
            cr, ir = crows[sha], irows[sha]
            row_checks[sha] = (
                cr.get("source_aliases") == ir.get("source_aliases")
                and cr.get("normalized_raw") == ir.get("normalized_raw")
                and cr.get("connected") == ir.get("connected")
                and cr.get("mixed_after_exact_normalization") == ir.get("mixed_after_exact_normalization")
                and cr.get("basis_status") == ir.get("basis_status")
                and cr.get("classification") == ir.get("classification")
            )
    checks = {
        "source_guard": guard["ok"],
        "candidate_helpers_imported_false": guard["candidate_helpers_imported"] is False,
        "source_entry_count": candidate.get("source_entry_count") == independent["source_entry_count"],
        "unique_raw_count": candidate.get("unique_raw_count") == independent["unique_raw_count"],
        "eligible_count": candidate.get("eligible_connected_mixed_unique_raw_count") == independent["eligible_connected_mixed_unique_raw_count"],
        "open_count": candidate.get("open_post_orbit_obstruction_count") == independent["open_post_orbit_obstruction_count"],
        "verdict": candidate.get("verdict") == independent["verdict"],
        "row_sha_set": set(crows) == set(irows),
        "all_rows_match": bool(row_checks) and all(row_checks.values()),
        "first_open": (
            None if candidate.get("first_open_obstruction") is None else candidate["first_open_obstruction"].get("raw_semantic_sha256")
        ) == independent["first_open_sha"],
    }
    return {
        "artifact_id": ARTIFACT_ID,
        "verified": all(checks.values()),
        "checks": checks,
        "row_checks": row_checks,
        "independent": independent,
        "source_guard": guard,
        "candidate_helpers_imported": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-json", required=True)
    args = parser.parse_args()
    candidate = json.loads(Path(args.candidate_json).read_text(encoding="utf-8").strip().splitlines()[-1])
    out = verify_candidate(candidate)
    print(json.dumps(out, sort_keys=True, separators=(",", ":")))
    if not out["verified"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
