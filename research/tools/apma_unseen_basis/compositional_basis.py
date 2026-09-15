from __future__ import annotations

import hashlib
import json
from pathlib import Path

from research.tools.apma_unseen_basis.raw_relation_basis import (
    canonicalize_raw,
    induce_basis,
    RawBasisInputError,
)

ARTIFACT_ID = "JANUS-TRUMP-RAW-COMPOSITIONAL-BASIS-INDUCTION-CANDIDATE-2026-09-15-v1.0"
AUTHORITY = "CANDIDATE_IMPLEMENTATION__SCOPED_COMPOSITIONAL_DISCOVERY_ONLY"
PREREG_REL = Path("research/TRUMP_RAW_COMPOSITIONAL_BASIS_INDUCTION_PREREGISTRATION_2026-09-15.json")
PREREG_COMMIT = "4139e1f15cf9fcc2355ba14cb8138e36c2dae60d"
PREREG_GIT_BLOB_SHA1 = "212eeb78a08b8a558248873f50a776bed61a7748"
PARENT_REL = Path("research/tools/apma_unseen_basis/raw_relation_basis.py")
PARENT_GIT_BLOB_SHA1 = "63490c05ef3e91a4f682f75da26ff2af811839a6"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def source_guard() -> dict:
    root = repo_root()
    p = root / PREREG_REL
    parent = root / PARENT_REL
    prereg = json.loads(p.read_text(encoding="utf-8"))
    checks = {
        "prereg_blob": git_blob_sha1(p) == PREREG_GIT_BLOB_SHA1,
        "prereg_status": prereg.get("status") == "FROZEN_BEFORE_CANDIDATE_IMPLEMENTATION",
        "prereg_artifact": prereg.get("artifact_id") == "JANUS-TRUMP-RAW-COMPOSITIONAL-BASIS-INDUCTION-PREREGISTRATION-2026-09-15-v1.0",
        "parent_basis_blob": git_blob_sha1(parent) == PARENT_GIT_BLOB_SHA1,
    }
    return {"ok": all(checks.values()), "checks": checks}


def canonical_constraint_components(canonical_raw: dict) -> list[list[int]]:
    rows = canonical_raw["constraints"]
    n = len(rows)
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra == rb:
            return
        if ra > rb:
            ra, rb = rb, ra
        parent[rb] = ra

    first_by_var: dict[int, int] = {}
    for i, row in enumerate(rows):
        for v in row["scope"]:
            if v in first_by_var:
                union(i, first_by_var[v])
            else:
                first_by_var[v] = i

    groups: dict[int, list[int]] = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)

    def component_key(indices: list[int]):
        variables = sorted({v for i in indices for v in rows[i]["scope"]})
        semantic_rows = sorted(
            (
                tuple(rows[i]["scope"]),
                tuple("".join(str(int(x)) for x in t) for t in rows[i]["allowed"]),
            )
            for i in indices
        )
        return (variables, semantic_rows)

    return sorted((sorted(xs) for xs in groups.values()), key=component_key)


def component_raw(canonical_raw: dict, indices: list[int]) -> dict:
    rows = canonical_raw["constraints"]
    selected = [rows[i] for i in indices]
    variables = sorted({v for row in selected for v in row["scope"]})
    return {
        "variables": variables,
        "constraints": [
            {"id": row["id"], "scope": list(row["scope"]), "allowed": [list(t) for t in row["allowed"]]}
            for row in selected
        ],
    }


def semantic_component_signature(component: dict) -> dict:
    local = component["local_basis_certificate"]
    return {
        "variables": list(component["variables"]),
        "constraint_scopes": [list(x) for x in component["constraint_scopes"]],
        "semantic_surface_sha256": local.get("semantic_surface_sha256"),
        "language_fingerprint": local.get("language_fingerprint"),
        "selected_basis": local.get("selected_basis"),
        "local_status": local.get("status"),
    }


def induce_compositional_basis(raw: dict) -> dict:
    guard = source_guard()
    if not guard["ok"]:
        return {"artifact_id": ARTIFACT_ID, "status": "HALT_SOURCE_GUARD", "source_guard": guard, "scientific_firewall": firewall()}
    try:
        canonical = canonicalize_raw(raw)
    except RawBasisInputError as exc:
        return {
            "artifact_id": ARTIFACT_ID,
            "status": "REJECT_RAW_INPUT",
            "reason": str(exc),
            "source_guard": guard,
            "metrics": {"cartesian_products_materialized": 0, "full_variable_assignments_enumerated": 0, "solver_invocations": 0},
            "scientific_firewall": firewall(),
        }

    groups = canonical_constraint_components(canonical)
    rows = canonical["constraints"]
    portfolio = []
    seen_variables: set[int] = set()
    total_incidence = 0
    open_components = 0

    for component_id, indices in enumerate(groups):
        local_raw = component_raw(canonical, indices)
        local_vars = set(local_raw["variables"])
        if seen_variables & local_vars:
            raise AssertionError("COMPONENT_VARIABLE_OVERLAP")
        seen_variables |= local_vars
        total_incidence += sum(len(row["scope"]) for row in local_raw["constraints"])
        cert = induce_basis(local_raw)
        if cert.get("status") != "ADMIT_EXACT_SCHAEFER_BASIS":
            open_components += 1
        portfolio.append({
            "component_id": component_id,
            "variables": sorted(local_vars),
            "constraint_ids": sorted(row["id"] for row in local_raw["constraints"]),
            "constraint_scopes": sorted([list(row["scope"]) for row in local_raw["constraints"]]),
            "local_basis_certificate": cert,
        })

    semantic_portfolio = [semantic_component_signature(c) for c in portfolio]
    raw_hash = hashlib.sha256(json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    semantic_hash = hashlib.sha256(json.dumps(semantic_portfolio, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    status = "ADMIT_COMPOSITIONAL_BASIS_PORTFOLIO" if open_components == 0 else "OPEN_COMPONENT_WITHOUT_SCHAEFER_BASIS"
    return {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "prereg_commit": PREREG_COMMIT,
        "source_guard": guard,
        "raw_object_sha256": raw_hash,
        "semantic_portfolio_sha256": semantic_hash,
        "status": status,
        "execution_authorized": False,
        "component_count": len(portfolio),
        "open_component_count": open_components,
        "portfolio": portfolio,
        "semantic_portfolio": semantic_portfolio,
        "exact_decomposition_certificate": {
            "rule": "VARIABLE_SHARING_CONNECTED_COMPONENTS",
            "pairwise_disjoint_component_variables": True,
            "covered_constraint_count": sum(len(g) for g in groups),
            "input_constraint_count": len(rows),
        },
        "metrics": {
            "scope_incidence_entries": total_incidence,
            "portfolio_records": len(portfolio),
            "cartesian_products_materialized": 0,
            "full_variable_assignments_enumerated": 0,
            "solver_invocations": 0,
            "carrier_executions": 0,
        },
        "scientific_firewall": firewall(),
    }


def firewall() -> dict:
    return {
        "P_VS_NP": "OPEN",
        "GENERAL_SAT_IN_P": "NOT_PROVED",
        "CONNECTED_MIXED_CORE_SOLVED": "NO",
        "ARBITRARY_UNSEEN_INVARIANT_DISCOVERY": "NOT_PROVED",
        "SCOPE": "VARIABLE_DISJOINT_COMPOSITION_OF_LOCALLY_RECOGNIZED_FROZEN_SCHAEFER_BASES",
        "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE_PENDING_HQ_REVIEW",
    }


def disconnected_mixed() -> dict:
    return {
        "variables": [0, 1, 2, 3, 4],
        "constraints": [
            {"id": "opaque_or", "scope": [0, 1], "allowed": [[0, 1], [1, 0], [1, 1]]},
            {"id": "opaque_xor", "scope": [2, 3, 4], "allowed": [[0, 0, 0], [0, 1, 1], [1, 0, 1], [1, 1, 0]]},
        ],
    }


def connected_mixed() -> dict:
    return {
        "variables": [0, 1, 2, 3],
        "constraints": [
            {"id": "opaque_or", "scope": [0, 1], "allowed": [[0, 1], [1, 0], [1, 1]]},
            {"id": "opaque_xor", "scope": [1, 2, 3], "allowed": [[0, 0, 0], [0, 1, 1], [1, 0, 1], [1, 1, 0]]},
        ],
    }


def bridged_mixed() -> dict:
    raw = disconnected_mixed()
    raw["constraints"].append({
        "id": "opaque_bridge",
        "scope": [1, 2],
        "allowed": [[0, 0], [1, 1]],
    })
    return raw


def many_components(count: int = 8) -> dict:
    variables = []
    constraints = []
    cursor = 0
    for i in range(count):
        if i % 2 == 0:
            vs = [cursor, cursor + 1]
            variables.extend(vs)
            constraints.append({"id": f"opaque_or_{i}", "scope": vs, "allowed": [[0, 1], [1, 0], [1, 1]]})
            cursor += 2
        else:
            vs = [cursor, cursor + 1, cursor + 2]
            variables.extend(vs)
            constraints.append({"id": f"opaque_xor_{i}", "scope": vs, "allowed": [[0, 0, 0], [0, 1, 1], [1, 0, 1], [1, 1, 0]]})
            cursor += 3
    return {"variables": sorted(variables), "constraints": constraints}


def permuted(raw: dict) -> dict:
    return {
        "variables": list(raw["variables"]),
        "constraints": [
            {"id": f"renamed_{i}", "scope": list(row["scope"]), "allowed": list(reversed(row["allowed"]))}
            for i, row in enumerate(reversed(raw["constraints"]))
        ],
    }


def main() -> None:
    out = {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "disconnected": induce_compositional_basis(disconnected_mixed()),
        "connected": induce_compositional_basis(connected_mixed()),
        "bridged": induce_compositional_basis(bridged_mixed()),
        "many": induce_compositional_basis(many_components()),
        "scientific_firewall": firewall(),
    }
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
