from __future__ import annotations

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

SOURCE_FREEZE = ROOT / "research/TRUMP_WALL_MANTEQUILLA_UUF175_001_020_SOURCE_FREEZE_AUTHORITY_2026-09-18_v1.0.json"
ORDER = tuple(f"UUF175_{i:03d}" for i in range(1, 21))


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
                    raise ValueError(f"EMPTY_CLAUSE_BEFORE_TERMINATOR:{path.name}")
                clauses.append(tuple(buf))
                buf = []
            else:
                buf.append(z)
    if buf or (nvars, nclauses) != (175, 753) or len(clauses) != 753:
        raise ValueError(f"UUF175_SHAPE_MISMATCH:{path.name}:{nvars}:{nclauses}:{len(clauses)}")
    for clause in clauses:
        if len(clause) != 3 or len({abs(x) for x in clause}) != 3:
            raise ValueError(f"NON_CANONICAL_3CNF:{path.name}:{clause}")
        if any(abs(x) < 1 or abs(x) > 175 for x in clause):
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


def structural_metrics(reduced: dict[str, Any], cell: list[int]):
    cell_set = set(cell)
    local = [
        c for c in reduced["constraints"]
        if cell_set.intersection(int(v) for v in c["scope"])
    ]
    boundary = sorted({
        int(v)
        for c in local
        for v in c["scope"]
        if int(v) not in cell_set
    })
    local_count = len(local)
    bcount = len(boundary)
    if local_count == 0:
        classification = "NULL_EXACT_SYMMETRY"
    elif bcount < 2:
        classification = "ACTIVE_SINGLETON_BOUNDARY"
    else:
        classification = "ACTIVE_EXACT_SYMMETRY_ELIGIBLE"
    return {
        "local_constraint_count": local_count,
        "boundary_variables": boundary,
        "boundary_variable_count": bcount,
        "classification": classification,
        "eligible_correlated_panel": bool(local_count > 0 and bcount >= 2),
    }


def source_row(source: str, receipt: dict[str, Any]) -> dict[str, Any]:
    t0 = time.perf_counter()
    path = ROOT / receipt["committed_path"]
    clauses, canonical_formula_sha256 = parse_dimacs(path)
    if canonical_formula_sha256 != receipt["canonical_formula_sha256"]:
        raise RuntimeError(f"CANONICAL_FORMULA_SHA_MISMATCH:{source}")

    projected = fresh.projection_identity.normalize_projection(source, clauses)[0]
    projected_sha = fresh.csha(projected)
    reduced, degree1_variables, target_constraints = fresh.generic_round(projected)
    reduced_sha = fresh.csha(reduced)

    nodes, adjacency, labels = wl_ref.incidence_structure(reduced)
    variable_nodes = [node for node in nodes if node[0] == "v"]

    colors1, rounds1 = wl_ref.wl1(nodes, adjacency, labels)
    classes1 = nontrivial_classes(colors1, variable_nodes, lambda node: node[1])

    if not classes1:
        classes2 = []
        rounds2 = 0
        wl2_status = "SKIPPED_LOGICALLY_IRRELEVANT_WL1_DISCRETE"
    else:
        colors2, rounds2 = wl_ref.wl2(nodes, adjacency, labels)
        diagonal = [(v, v) for v in variable_nodes]
        classes2 = nontrivial_classes(colors2, diagonal, lambda pair: pair[0][1])
        wl2_status = "EXECUTED"

    classes2_set = {tuple(cell) for cell in classes2}
    shared = [cell for cell in classes1 if tuple(cell) in classes2_set]

    exact_cells = []
    direct_checks = 0
    formula = orbit.validate_and_normalize(reduced) if shared else None
    for cell in shared:
        root = min(cell)
        star = [[root, v] for v in cell if v != root]
        results = []
        for u, v in star:
            direct_checks += 1
            ok = orbit.is_exact_transposition_automorphism(formula, u, v)
            results.append({"edge": [u, v], "exact": bool(ok)})
        if all(item["exact"] for item in results):
            metrics = structural_metrics(reduced, cell)
            exact_cells.append({
                "cell": cell,
                "cell_size": len(cell),
                "star_generators": star,
                "direct_exact_checks": results,
                "certified_group": f"S_{len(cell)}",
                **metrics,
                "current_mechanism_compatible_k2_or_k3": len(cell) in {2, 3},
            })

    row = {
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
        "candidate_runtime_seconds": time.perf_counter() - t0,
    }
    return row


def summarize(rows):
    cells = [cell for row in rows for cell in row["detected_exact_cells"]]
    nulls = [c for c in cells if c["classification"] == "NULL_EXACT_SYMMETRY"]
    active = [c for c in cells if c["local_constraint_count"] > 0]
    b2 = [c for c in cells if c["eligible_correlated_panel"]]
    k2 = [c for c in cells if c["cell_size"] == 2]
    k3 = [c for c in cells if c["cell_size"] == 3]
    kgt3 = [c for c in cells if c["cell_size"] > 3]
    compatible = [c for c in b2 if c["cell_size"] in {2, 3}]
    unsupported = [c for c in b2 if c["cell_size"] > 3]
    return {
        "N_sources": len(rows),
        "N_sources_WL1_nondiscrete": sum(bool(r["wl1_nontrivial_variable_classes"]) for r in rows),
        "N_sources_WL2_executed": sum(r["wl2_status"] == "EXECUTED" for r in rows),
        "N_shared_WL_candidate_cells": sum(len(r["shared_wl_candidate_cells"]) for r in rows),
        "N_detected_cells": len(cells),
        "N_null_cells": len(nulls),
        "N_active_cells": len(active),
        "N_boundary_ge2_cells": len(b2),
        "N_cells_k2": len(k2),
        "N_cells_k3": len(k3),
        "N_cells_k_gt3": len(kgt3),
        "N_eligible_current_mechanism_k2_or_k3": len(compatible),
        "N_eligible_unsupported_k_gt3": len(unsupported),
        "N_Mantequilla_routed_cells": 0,
        "N_Mantequilla_planned_after_census_freeze": len(compatible),
        "N_sources_with_detected_cells": sum(bool(r["detected_exact_cells"]) for r in rows),
        "N_sources_with_eligible_cells": sum(
            any(c["eligible_correlated_panel"] for c in r["detected_exact_cells"])
            for r in rows
        ),
        "direct_exact_transposition_checks": sum(r["direct_exact_transposition_checks"] for r in rows),
    }


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: candidate.py OUTPUT.json")

    source_freeze = json.loads(SOURCE_FREEZE.read_text(encoding="utf-8"))
    receipts = source_freeze["source_receipts"]
    if tuple(r["source"] for r in receipts) != ORDER:
        raise RuntimeError("SOURCE_ORDER_MISMATCH")
    if source_freeze.get("independent_verification") != "PASS_INDEPENDENT_UUF175_001_020_SOURCE_FREEZE_VERIFICATION":
        raise RuntimeError("SOURCE_FREEZE_NOT_INDEPENDENTLY_VERIFIED")

    rows = [source_row(r["source"], r) for r in receipts]
    summary = summarize(rows)

    result = {
        "artifact_id": "JANUS-TRUMP-WALL-MANTEQUILLA-UUF175-001-020-STRUCTURAL-CENSUS-CANDIDATE-v1",
        "date": "2026-09-18",
        "phase": "STRUCTURAL_CENSUS_ONLY__MANTEQUILLA_NOT_RUN",
        "panel": list(ORDER),
        "source_freeze_blob": "65aefb3dd47d536b5d1dad9bea1f920e22ed8e00",
        "rows": rows,
        "summary": summary,
        "freeze_barrier": {
            "residual_constructions": 0,
            "robdd_operations": 0,
            "sat_solver_invocations": 0,
            "mantequilla_runs": 0,
            "boundary_cube_assignments_enumerated": 0,
        },
        "claim_ceiling": "FINITE_UUF175_001_020_STRUCTURAL_ACTIVITY_CENSUS_UNDER_PREREGISTERED_DETECTOR_ONLY",
        "scientific_firewall": {
            "DETECTOR_COMPLETENESS": "NOT_PROVED",
            "GENERAL_K_CLASS": "NOT_PROVED",
            "GENERAL_SAT_IN_P": "NOT_PROVED",
            "P_VS_NP": "OPEN",
        },
    }
    result["candidate_semantic_digest_sha256"] = csha({
        "panel": result["panel"],
        "rows": [
            {k: v for k, v in row.items() if k != "candidate_runtime_seconds"}
            for row in rows
        ],
        "summary": summary,
        "freeze_barrier": result["freeze_barrier"],
    })

    Path(sys.argv[1]).write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "candidate_semantic_digest_sha256": result["candidate_semantic_digest_sha256"],
        "summary": summary,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
