from __future__ import annotations

import ast
import hashlib
import json
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from research.tools.apma_uf20_011_015_fresh_generic_pendant_wl_replication import candidate as fresh
from research.tools.apma_uf20_wl_historical_closed_control_falsifier import candidate as wl_ref
from research.tools.apma_unseen_local_invariant_orbit_count import candidate as orbit

SOURCE_FREEZE = ROOT / "research/TRUMP_WALL_MANTEQUILLA_UUF250_DEPTH_P4_061_080_SOURCE_FREEZE_AUTHORITY_2026-09-18_v1.0.json"
ORDER = tuple(f"UUF250_{i:03d}" for i in range(61, 81))

ALLOWED_IMPORT_MODULES = {
    "__future__",
    "ast",
    "hashlib",
    "json",
    "sys",
    "time",
    "collections",
    "pathlib",
    "typing",
    "research.tools.apma_uf20_011_015_fresh_generic_pendant_wl_replication",
    "research.tools.apma_uf20_wl_historical_closed_control_falsifier",
    "research.tools.apma_unseen_local_invariant_orbit_count",
}
FORBIDDEN_CALL_NAMES = {
    "canonical_residual",
    "residual_bdd",
    "constraint_bdd",
    "quotient_state_count",
    "assignment_from_counts",
}
FORBIDDEN_ATTRIBUTE_NAMES = {
    "run_candidate",
    "discover_generator_edges",
}


def csha(obj: Any) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def parse_dimacs(path: Path):
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
                raise ValueError(f"BAD_HEADER:{path.name}:{s}")
            nvars, nclauses = int(parts[2]), int(parts[3])
            continue
        for z in map(int, s.split()):
            if z == 0:
                if not buf:
                    raise ValueError(f"EMPTY_CLAUSE:{path.name}")
                clauses.append(tuple(buf))
                buf = []
            else:
                buf.append(z)
    if buf or (nvars, nclauses) != (250, 1065) or len(clauses) != 1065:
        raise ValueError(f"UUF250_SHAPE_MISMATCH:{path.name}")
    for clause in clauses:
        if len(clause) != 3 or len({abs(x) for x in clause}) != 3:
            raise ValueError(f"NON_CANONICAL_3CNF:{path.name}:{clause}")
        if any(abs(x) < 1 or abs(x) > 250 for x in clause):
            raise ValueError(f"VARIABLE_RANGE:{path.name}:{clause}")
    canonical = "".join(" ".join(map(str, c)) + " 0\n" for c in clauses).encode("ascii")
    return clauses, hashlib.sha256(canonical).hexdigest()


def nontrivial_classes(colors, keys, value_of):
    buckets = defaultdict(list)
    for key in keys:
        buckets[colors[key]].append(int(value_of(key)))
    out = [sorted(values) for values in buckets.values() if len(values) >= 2]
    out.sort(key=lambda x: (x[0], len(x), x))
    return out


def classify_cell(reduced: dict[str, Any], cell: list[int]):
    cell_set = set(cell)
    local = []
    boundary = set()
    for constraint in reduced["constraints"]:
        scope = [int(v) for v in constraint["scope"]]
        if not cell_set.intersection(scope):
            continue
        local.append(constraint)
        for v in scope:
            if v not in cell_set:
                boundary.add(v)
    bvars = sorted(boundary)
    if len(local) == 0:
        label = "NULL_EXACT_SYMMETRY"
    elif len(bvars) < 2:
        label = "ACTIVE_SINGLETON_BOUNDARY"
    else:
        label = "ACTIVE_EXACT_SYMMETRY_ELIGIBLE"
    return {
        "local_constraint_count": len(local),
        "boundary_variables": bvars,
        "boundary_variable_count": len(bvars),
        "classification": label,
        "eligible_correlated_panel": bool(len(local) > 0 and len(bvars) >= 2),
    }


def recompute_source(source: str, receipt: dict[str, Any]):
    path = ROOT / receipt["committed_path"]
    clauses, canonical_formula_sha256 = parse_dimacs(path)
    if canonical_formula_sha256 != receipt["canonical_formula_sha256"]:
        raise RuntimeError(f"CANONICAL_FORMULA_SHA_MISMATCH:{source}")

    projected = fresh.projection_identity.normalize_projection(source, clauses)[0]
    projected_sha = fresh.csha(projected)
    reduced, degree1_variables, target_constraints = fresh.generic_round(projected)
    reduced_sha = fresh.csha(reduced)

    nodes, adjacency, labels = wl_ref.incidence_structure(reduced)
    variable_nodes = [n for n in nodes if n[0] == "v"]
    colors1, rounds1 = wl_ref.wl1(nodes, adjacency, labels)
    classes1 = nontrivial_classes(colors1, variable_nodes, lambda n: n[1])

    if classes1:
        colors2, rounds2 = wl_ref.wl2(nodes, adjacency, labels)
        diagonal = [(v, v) for v in variable_nodes]
        classes2 = nontrivial_classes(colors2, diagonal, lambda p: p[0][1])
        wl2_status = "EXECUTED"
    else:
        classes2 = []
        rounds2 = 0
        wl2_status = "SKIPPED_LOGICALLY_IRRELEVANT_WL1_DISCRETE"

    c2 = {tuple(c) for c in classes2}
    shared = [c for c in classes1 if tuple(c) in c2]

    exact_cells = []
    direct_checks = 0
    normalized = orbit.validate_and_normalize(reduced) if shared else None
    for cell in shared:
        root = min(cell)
        star = [[root, v] for v in cell if v != root]
        checks = []
        for u, v in star:
            direct_checks += 1
            ok = bool(orbit.is_exact_transposition_automorphism(normalized, u, v))
            checks.append({"edge": [u, v], "exact": ok})
        if checks and all(x["exact"] for x in checks):
            exact_cells.append({
                "cell": cell,
                "cell_size": len(cell),
                "star_generators": star,
                "direct_exact_checks": checks,
                "certified_group": f"S_{len(cell)}",
                **classify_cell(reduced, cell),
                "current_mechanism_compatible_k2_or_k3": len(cell) in {2, 3},
            })

    return {
        "source": source,
        "source_git_blob": receipt["git_blob"],
        "canonical_formula_sha256": canonical_formula_sha256,
        "projected_raw_sha256": projected_sha,
        "reduced_raw_sha256": reduced_sha,
        "projected_variables": len(projected["variables"]),
        "projected_constraints": len(projected["constraints"]),
        "reduced_variables": len(reduced["variables"]),
        "reduced_constraints": len(reduced["constraints"]),
        "degree1_variables": degree1_variables,
        "target_constraints": target_constraints,
        "wl1_nontrivial_variable_classes": classes1,
        "wl2_nontrivial_diagonal_variable_classes": classes2,
        "wl1_rounds": rounds1,
        "wl2_rounds": rounds2,
        "wl2_status": wl2_status,
        "shared_wl_candidate_cells": shared,
        "detected_exact_cells": exact_cells,
        "direct_exact_transposition_checks": direct_checks,
        "residual_semantics_read": False,
    }


def summarize(rows):
    cells = [c for row in rows for c in row["detected_exact_cells"]]
    nulls = [c for c in cells if c["classification"] == "NULL_EXACT_SYMMETRY"]
    active = [c for c in cells if c["local_constraint_count"] > 0]
    b2 = [c for c in cells if c["eligible_correlated_panel"]]
    return {
        "N_sources": len(rows),
        "N_sources_WL1_nondiscrete": sum(bool(r["wl1_nontrivial_variable_classes"]) for r in rows),
        "N_sources_WL2_executed": sum(r["wl2_status"] == "EXECUTED" for r in rows),
        "N_shared_WL_candidate_cells": sum(len(r["shared_wl_candidate_cells"]) for r in rows),
        "N_detected_cells": len(cells),
        "N_null_cells": len(nulls),
        "N_active_cells": len(active),
        "N_boundary_ge2_cells": len(b2),
        "N_cells_k2": sum(c["cell_size"] == 2 for c in cells),
        "N_cells_k3": sum(c["cell_size"] == 3 for c in cells),
        "N_cells_k_gt3": sum(c["cell_size"] > 3 for c in cells),
        "N_eligible_current_mechanism_k2_or_k3": sum(
            c["eligible_correlated_panel"] and c["cell_size"] in {2, 3} for c in cells
        ),
        "N_eligible_unsupported_k_gt3": sum(
            c["eligible_correlated_panel"] and c["cell_size"] > 3 for c in cells
        ),
        "N_Mantequilla_routed_cells": 0,
        "N_Mantequilla_planned_after_census_freeze": sum(
            c["eligible_correlated_panel"] and c["cell_size"] in {2, 3} for c in cells
        ),
        "N_sources_with_detected_cells": sum(bool(r["detected_exact_cells"]) for r in rows),
        "N_sources_with_eligible_cells": sum(
            any(c["eligible_correlated_panel"] for c in r["detected_exact_cells"]) for r in rows
        ),
        "direct_exact_transposition_checks": sum(r["direct_exact_transposition_checks"] for r in rows),
    }


def audit_candidate_source(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports = []
    calls = []
    attrs = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calls.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                attrs.append(node.func.attr)
    unexpected_imports = sorted(set(imports) - ALLOWED_IMPORT_MODULES)
    forbidden_calls = sorted(set(calls) & FORBIDDEN_CALL_NAMES)
    forbidden_attrs = sorted(set(attrs) & FORBIDDEN_ATTRIBUTE_NAMES)
    imported_candidate = any(
        x.endswith("trump_wall_mantequilla_uuf250_structural_census.candidate")
        for x in imports
    )
    return {
        "imports": sorted(imports),
        "unexpected_imports": unexpected_imports,
        "forbidden_call_names": forbidden_calls,
        "forbidden_attribute_names": forbidden_attrs,
        "candidate_module_imported": imported_candidate,
        "pass": not unexpected_imports and not forbidden_calls and not forbidden_attrs and not imported_candidate,
    }


def strip_runtime(row):
    return {k: v for k, v in row.items() if k != "candidate_runtime_seconds"}


def main():
    if len(sys.argv) != 4:
        raise SystemExit("usage: independent_check.py CANDIDATE.json CANDIDATE_SOURCE.py OUTPUT.json")
    t0 = time.perf_counter()
    candidate_path = Path(sys.argv[1])
    candidate_source_path = Path(sys.argv[2])
    output_path = Path(sys.argv[3])

    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    source_freeze = json.loads(SOURCE_FREEZE.read_text(encoding="utf-8"))
    receipts = source_freeze["source_receipts"]
    if tuple(r["source"] for r in receipts) != ORDER:
        raise RuntimeError("SOURCE_ORDER_MISMATCH")

    source_audit = audit_candidate_source(candidate_source_path)
    rows = [recompute_source(r["source"], r) for r in receipts]
    summary = summarize(rows)
    candidate_rows = [strip_runtime(r) for r in candidate.get("rows", [])]
    expected_barrier = {
        "residual_constructions": 0,
        "robdd_operations": 0,
        "sat_solver_invocations": 0,
        "mantequilla_runs": 0,
        "boundary_cube_assignments_enumerated": 0,
    }

    checks = {
        "candidate_source_audit_pass": source_audit["pass"],
        "source_freeze_blob_matches": candidate.get("source_freeze_blob") == "54bb1d581bff164cf08633f66133e9e461a571e0",
        "panel_matches": candidate.get("panel") == list(ORDER),
        "phase_matches": candidate.get("phase") == "STRUCTURAL_CENSUS_ONLY__MANTEQUILLA_NOT_RUN",
        "row_count_20": len(candidate_rows) == 20,
        "rows_exact_match": candidate_rows == rows,
        "summary_exact_match": candidate.get("summary") == summary,
        "freeze_barrier_exact_match": candidate.get("freeze_barrier") == expected_barrier,
        "all_candidate_rows_residual_unread": all(r.get("residual_semantics_read") is False for r in candidate_rows),
        "no_mantequilla_routed_before_freeze": summary["N_Mantequilla_routed_cells"] == 0,
    }
    verified = all(checks.values())

    semantic_payload = {
        "panel": list(ORDER),
        "rows": rows,
        "summary": summary,
        "freeze_barrier": expected_barrier,
    }
    expected_candidate_digest = csha(semantic_payload)
    checks["candidate_semantic_digest_matches"] = (
        candidate.get("candidate_semantic_digest_sha256") == expected_candidate_digest
    )
    verified = all(checks.values())

    out = {
        "artifact_id": "JANUS-TRUMP-WALL-MANTEQUILLA-UUF250-DEPTH-P4-061-080-STRUCTURAL-CENSUS-INDEPENDENT-CHECK-v1",
        "date": "2026-09-18",
        "verdict": (
            "PASS_INDEPENDENT_UUF250_STRUCTURAL_ACTIVITY_CENSUS_VERIFICATION"
            if verified
            else "FAIL_INDEPENDENT_UUF250_STRUCTURAL_ACTIVITY_CENSUS_VERIFICATION"
        ),
        "candidate_imported": False,
        "candidate_source_audit": source_audit,
        "checks": checks,
        "independent_rows": rows,
        "independent_summary": summary,
        "independent_freeze_barrier": expected_barrier,
        "candidate_semantic_digest_expected": expected_candidate_digest,
        "claim_ceiling": "FINITE_UUF250_DEPTH_P4_061_080_STRUCTURAL_ACTIVITY_CENSUS_UNDER_PREREGISTERED_DETECTOR_ONLY",
        "independent_checker_runtime_seconds": time.perf_counter() - t0,
    }
    out["independent_semantic_digest_sha256"] = csha({
        "verdict": out["verdict"],
        "checks": checks,
        "independent_rows": rows,
        "independent_summary": summary,
        "independent_freeze_barrier": expected_barrier,
        "candidate_semantic_digest_expected": expected_candidate_digest,
    })

    output_path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "verdict": out["verdict"],
        "checks_passed": sum(bool(v) for v in checks.values()),
        "checks_total": len(checks),
        "summary": summary,
        "candidate_semantic_digest_expected": expected_candidate_digest,
        "independent_semantic_digest_sha256": out["independent_semantic_digest_sha256"],
    }, sort_keys=True))
    if not verified:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
