from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from research.tools.apma_uf20_011_015_fresh_generic_pendant_wl_replication import candidate as frozen
from research.tools.apma_uf20_wl_historical_closed_control_falsifier import candidate as wl_ref
from research.tools.apma_unseen_local_invariant_orbit_count import candidate as orbit

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / "research/TRUMP_UF150_001_020_OUT_OF_FAMILY_WL_ORBIT_FALSIFIER_EVALUATION_PREREGISTRATION_2026-09-18_v1.0.json"
REVIEW = ROOT / "research/TRUMP_UF150_001_020_OUT_OF_FAMILY_WL_ORBIT_FALSIFIER_EVALUATION_REVIEW_2026-09-18_v1.0.json"
SOURCE_FREEZE = ROOT / "research/TRUMP_UF150_001_020_OUT_OF_FAMILY_SOURCE_FREEZE_AUTHORITY_2026-09-18_v1.0.json"\nRECONCILIATION = ROOT / "research/TRUMP_UF150_001_020_SOURCE_FREEZE_REENTRY_RECONCILIATION_2026-09-18_v1.0.json"
SCOPE_THEOREM = ROOT / "research/TRUMP_WL_DIRECT_EXACT_E3_SCOPE_BOUND_THEOREM_RESULT_2026-09-18_v1.0.json"
FRESH = ROOT / "research/tools/apma_uf20_011_015_fresh_generic_pendant_wl_replication/candidate.py"
PROJECTION = ROOT / "research/tools/apma_satlib_uf20_r000_r111_projected_core_replay/projection_identity.py"
WL = ROOT / "research/tools/apma_uf20_wl_historical_closed_control_falsifier/candidate.py"
ORBIT = ROOT / "research/tools/apma_unseen_local_invariant_orbit_count/candidate.py"
EXPECTED = {
    PREREG: "6d0a05eaeaf443f17450068cefe68bef99b93433",
    REVIEW: "0e0a17d60a2b0f6b5d880d682d741308a56b3dc9",
    SOURCE_FREEZE: "b9084a54414a930945e67d81e83698100d4ac417",\n    RECONCILIATION: "b01f9d9c2a5e78201b5d5d046837411f8d753610",
    SCOPE_THEOREM: "3cbf05cb0b0249ddf365bc43d176a06ddb7f72af",
    FRESH: "9ec365ae27a6caa7b936cd33040e542f183ded99",
    PROJECTION: "2ef48e73974a5f43d3f4fb4809ebd0c09c0f5be4",
    WL: "6b697fd8b3de4c83f8226b06399b6bad99953d4e",
    ORBIT: "a076cfc56d68aad0348415e313705da1f6b9cdcd",
}
ORDER = tuple(f"UF150_{i:03d}" for i in range(1, 21))


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def canonical_sha(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def parse_uf150(path: Path) -> tuple[list[tuple[int, int, int]], str]:
    nvars = nclauses = None
    clauses: list[tuple[int, int, int]] = []
    buf: list[int] = []
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
                if any(abs(x) < 1 or abs(x) > 150 for x in buf):
                    raise ValueError("VARIABLE_OUT_OF_RANGE")
                clauses.append((buf[0], buf[1], buf[2]))
                buf = []
            else:
                buf.append(value)
    if (nvars, nclauses) != (150, 645) or len(clauses) != 645 or buf:
        raise ValueError(f"UF150_CONTRACT_FAILURE header={(nvars,nclauses)} parsed={len(clauses)} trailing={buf}")
    canonical = "".join(" ".join(map(str, c)) + " 0\n" for c in clauses).encode("ascii")
    return clauses, hashlib.sha256(canonical).hexdigest()


def classes(colors, keys, value_of):
    groups = defaultdict(list)
    for key in keys:
        groups[colors[key]].append(int(value_of(key)))
    out = [sorted(values) for values in groups.values() if len(values) > 1]
    out.sort(key=lambda x: (len(x), x))
    return out


def prediction(reduced: dict[str, Any]) -> dict[str, Any]:
    nodes, adjacency, labels = wl_ref.incidence_structure(reduced)
    variables = [node for node in nodes if node[0] == "v"]
    colors1, rounds1 = wl_ref.wl1(nodes, adjacency, labels)
    colors2, rounds2 = wl_ref.wl2(nodes, adjacency, labels)
    classes1 = classes(colors1, variables, lambda node: node[1])
    diagonal = [(v, v) for v in variables]
    classes2 = classes(colors2, diagonal, lambda pair: pair[0][1])

    pair = None
    exact = None
    direct_checks = 0
    scope_n = None
    scope_L = None
    scope_bound = None
    if len(classes1) == 1 and len(classes1[0]) == 2 and len(classes2) == 1 and classes2[0] == classes1[0]:
        pair = classes1[0]
        formula = orbit.validate_and_normalize(reduced)
        scope_n = len(formula.variables)
        scope_L = formula.L
        scope_bound = bool(scope_n >= 2 and 3 * (2 ** (scope_n - 2)) <= scope_L * scope_L)
        direct_checks = 1
        exact = orbit.is_exact_transposition_automorphism(formula, pair[0], pair[1])

    return {
        "wl1_nontrivial_variable_classes": classes1,
        "wl2_nontrivial_diagonal_variable_classes": classes2,
        "wl_rounds": {"wl1": rounds1, "wl2": rounds2},
        "wl_derived_pair": pair,
        "direct_exact_transposition_automorphism": exact,
        "prediction_positive": bool(pair is not None and exact is True),
        "scope_n": scope_n,
        "scope_L": scope_L,
        "scope_bound_holds": scope_bound,
        "direct_checks": direct_checks,
    }


def guard() -> dict[str, Any]:
    bindings = {str(path.relative_to(ROOT)): blob(path) == expected for path, expected in EXPECTED.items()}
    prereg = json.loads(PREREG.read_text())
    review = json.loads(REVIEW.read_text())
    source_freeze = json.loads(SOURCE_FREEZE.read_text())
    theorem = json.loads(SCOPE_THEOREM.read_text())\n    reconciliation = json.loads(RECONCILIATION.read_text())
    receipts = source_freeze.get("source_receipts", [])
    blind = source_freeze.get("blind_barrier_receipt", {})
    checks = {
        "authority_bindings": all(bindings.values()),
        "prereg_blind": prereg.get("status") == "FROZEN_AFTER_SOURCE_FREEZE__BEFORE_FIRST_UF150_PROJECTION_PENDANT_WL_DIRECT_SWAP_OR_E3_VALUE",
        "review_authorized": review.get("review_verdict") == "PASS_CLEAN_UF150_OUT_OF_FAMILY_WL_ORBIT_FALSIFIER_SPEC__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE",
        "source_freeze_pass": source_freeze.get("verdict") == "PASS_UF150_001_020_DUAL_MIRROR_SOURCE_ACQUISITION_AND_FORMULA_FREEZE",
        "source_freeze_independent": source_freeze.get("execution", {}).get("independent_verdict") == "PASS_INDEPENDENT_UF150_001_020_SOURCE_FREEZE_VERIFICATION",
        "source_count": len(receipts) == 20,
        "source_order": tuple(row.get("source") for row in receipts) == ORDER,
        "sources_frozen": all(row.get("independent_verified") is True and row.get("status") == "SOURCE_FROZEN" for row in receipts),
        "source_blindness_zero": all(int(value) == 0 for value in blind.values()),
        "source_freeze_reconciled": reconciliation.get("authority_rule") == "FIRST_SUCCESSFUL_IMMUTABLE_FREEZE_dc503550_IS_THE_ONLY_UF150_SOURCE_FREEZE_AUTHORITY_FOR_SCIENTIFIC_EVALUATION;LATER_REENTRY_HALTS_ARE_DIAGNOSTIC_ONLY",\n        "scope_theorem_pass": theorem.get("scientific_outcome") == "PASS_SCOPE_BOUND_DIRECT_EXACT_TRANSPOSITION_WITNESS_SUFFICIENCY_FOR_FROZEN_E3",
        "scope_theorem_firewall": theorem.get("scientific_firewall", {}).get("P_VS_NP") == "OPEN",
    }
    return {"ok": all(checks.values()), "checks": checks, "bindings": bindings}


def outcome_from(summary: dict[str, Any]) -> str:
    if summary["in_scope_theorem_falsifiers"]:
        return "FALSIFIED_SCOPE_THEOREM_AT_LEAST_ONE_IN_SCOPE_POSITIVE_NOT_E3_ADMITTED"
    if summary["selector_misses"]:
        return "FALSIFIED_OUT_OF_FAMILY_SELECTOR_AT_LEAST_ONE_E3_POSITIVE_NOT_RECOVERED"
    if summary["in_scope_open_false_positives"]:
        return "FALSIFIED_OUT_OF_FAMILY_AT_LEAST_ONE_IN_SCOPE_PORTFOLIO_OPEN_FALSE_POSITIVE"
    if summary["resource_scope_exits"]:
        return "SURVIVED_WITH_RESOURCE_SCOPE_EXITS_AND_ZERO_PREDECLARED_ERRORS"
    if summary["e3_positive_sources"]:
        return "SURVIVED_OUT_OF_FAMILY_WITH_AT_LEAST_ONE_E3_POSITIVE_AND_ZERO_PREDECLARED_ERRORS"
    return "SURVIVED_OUT_OF_FAMILY_ZERO_E3_POSITIVE_COVERAGE"


def main() -> dict[str, Any]:
    authority = guard()
    if not authority["ok"]:
        return {
            "verdict": "HALT_AUTHORITY_SOURCE_OR_TRAINING_REGRESSION_FAILURE",
            "reason": "AUTHORITY_OR_SOURCE_BINDING",
            "authority_guard": authority,
            "new_panel_structural_reads": 0,
        }

    training_ok, training = frozen.training_regression()
    if not training_ok:
        return {
            "verdict": "HALT_AUTHORITY_SOURCE_OR_TRAINING_REGRESSION_FAILURE",
            "reason": "TRAINING_REGRESSION",
            "authority_guard": authority,
            "training_regression": training,
            "new_panel_structural_reads": 0,
        }

    source_freeze = json.loads(SOURCE_FREEZE.read_text())
    metadata = {row["source"]: row for row in source_freeze["source_receipts"]}
    prediction_rows: list[dict[str, Any]] = []
    prepared: list[tuple[str, dict[str, Any]]] = []
    direct_checks = 0

    # Strict blind barrier: construct every prediction row before any route_row/E1/E2/E3 ground-truth call.
    for source in ORDER:
        meta = metadata[source]
        path = ROOT / meta["committed_copy_path"]
        source_blob = frozen.blob(path)
        clauses, formula_hash = parse_uf150(path)
        if source_blob != meta["committed_git_blob"] or formula_hash != meta["canonical_formula_sha256"]:
            return {
                "verdict": "HALT_AUTHORITY_SOURCE_OR_TRAINING_REGRESSION_FAILURE",
                "reason": f"SOURCE_BINDING:{source}",
                "training_regression": training,
                "source_binding_diagnostic": {
                    "source": source,
                    "observed_source_git_blob": source_blob,
                    "expected_source_git_blob": meta["committed_git_blob"],
                    "source_blob_match": source_blob == meta["committed_git_blob"],
                    "observed_canonical_formula_sha256": formula_hash,
                    "expected_canonical_formula_sha256": meta["canonical_formula_sha256"],
                    "formula_hash_match": formula_hash == meta["canonical_formula_sha256"],
                },
                "new_panel_structural_reads": len(prediction_rows),
            }
        projected = frozen.projection_identity.normalize_projection(source, clauses)[0]
        reduced, degree1_variables, target_constraints = frozen.generic_round(projected)
        pred = prediction(reduced)
        direct_checks += int(pred.pop("direct_checks"))
        prediction_rows.append({
            "source": source,
            "source_git_blob": source_blob,
            "canonical_formula_sha256": formula_hash,
            "projected_raw_sha256": frozen.csha(projected),
            "projected_variables": len(projected["variables"]),
            "projected_constraints": len(projected["constraints"]),
            "degree1_variables": degree1_variables,
            "target_constraints": target_constraints,
            "reduced_raw_sha256": frozen.csha(reduced),
            "reduced_variables": len(reduced["variables"]),
            "reduced_constraints": len(reduced["constraints"]),
            **pred,
        })
        prepared.append((source, reduced))

    if len(prediction_rows) != 20:
        raise RuntimeError("PREDICTION_STAGE_COUNT_NOT_TWENTY")
    prediction_digest = canonical_sha(prediction_rows)
    pred_by = {row["source"]: row for row in prediction_rows}

    ground_truth_rows = []
    e3_positive_sources = []
    selector_misses = []
    in_scope_theorem_falsifiers = []
    in_scope_open_false_positives = []
    resource_scope_exits = []
    portfolio_open_sources = []
    portfolio_closed_sources = []
    recovered_sources = []

    # Ground truth begins only here, after all 20 predictions and their digest are fixed.
    for source, reduced in prepared:
        route = frozen.route_row(reduced)
        pred = pred_by[source]
        e3 = route.get("E3", {})
        e3_positive = bool(e3.get("solver_authority") is True and e3.get("status") in frozen.CLOSED_ORBIT)
        edges = [sorted(map(int, edge)) for edge in (e3.get("generator_edges") or [])]
        pair = pred.get("wl_derived_pair")
        prediction_positive = pred.get("prediction_positive") is True
        scope_bound_holds = pred.get("scope_bound_holds") is True
        selector_recovered = bool(e3_positive and prediction_positive and pair in edges)
        selector_miss = bool(e3_positive and not selector_recovered)
        theorem_falsifier = bool(prediction_positive and scope_bound_holds and not e3_positive)
        portfolio_open = route.get("label") == "PORTFOLIO_OPEN"
        open_false_positive = bool(prediction_positive and scope_bound_holds and portfolio_open)
        scope_exit = bool(prediction_positive and pred.get("scope_bound_holds") is False)

        ground_truth_rows.append({
            "source": source,
            "portfolio_label": route.get("label"),
            "closure": route.get("closure"),
            "E1": route.get("E1"),
            "E2": route.get("E2"),
            "E3": route.get("E3"),
            "e3_positive": e3_positive,
            "e3_generator_edges": edges,
            "selector_recovered": selector_recovered,
            "selector_miss": selector_miss,
            "in_scope_theorem_falsifier": theorem_falsifier,
            "in_scope_open_false_positive": open_false_positive,
            "resource_scope_exit": scope_exit,
        })
        if e3_positive:
            e3_positive_sources.append(source)
        if selector_recovered:
            recovered_sources.append(source)
        if selector_miss:
            selector_misses.append(source)
        if theorem_falsifier:
            in_scope_theorem_falsifiers.append(source)
        if open_false_positive:
            in_scope_open_false_positives.append(source)
        if scope_exit:
            resource_scope_exits.append(source)
        (portfolio_open_sources if portfolio_open else portfolio_closed_sources).append(source)

    summary = {
        "prediction_positive_sources": [row["source"] for row in prediction_rows if row["prediction_positive"]],
        "prediction_positive_count": sum(1 for row in prediction_rows if row["prediction_positive"]),
        "in_scope_prediction_positive_sources": [row["source"] for row in prediction_rows if row["prediction_positive"] and row["scope_bound_holds"] is True],
        "resource_scope_exits": resource_scope_exits,
        "e3_positive_sources": e3_positive_sources,
        "e3_positive_count": len(e3_positive_sources),
        "selector_recovered_sources": recovered_sources,
        "selector_misses": selector_misses,
        "in_scope_theorem_falsifiers": in_scope_theorem_falsifiers,
        "in_scope_open_false_positives": in_scope_open_false_positives,
        "portfolio_open_sources": portfolio_open_sources,
        "portfolio_closed_sources": portfolio_closed_sources,
    }
    outcome = outcome_from(summary)
    return {
        "artifact_id": "JANUS-TRUMP-UF150-001-020-OUT-OF-FAMILY-WL-ORBIT-FALSIFIER-CANDIDATE-2026-09-18-v1.0",
        "gate": "TRUMP_UF150_001_020_OUT_OF_FAMILY_WL_ORBIT_FALSIFIER_GATE",
        "verdict": outcome,
        "authority_guard": authority,
        "training_regression": training,
        "prediction_stage_completed_before_ground_truth": True,
        "prediction_stage_count": 20,
        "prediction_stage_sha256": prediction_digest,
        "prediction_rows": prediction_rows,
        "ground_truth_rows": ground_truth_rows,
        "summary": summary,
        "resource_receipt": {
            "new_panel_sources_read": 20,
            "generic_reduction_rounds_per_source": 1,
            "iterated_pendant_peeling_rounds": 0,
            "prediction_full_transposition_searches": 0,
            "prediction_direct_exact_checks": direct_checks,
            "prediction_sat_solver_invocations": 0,
            "existing_portfolio_replays": 20,
            "signed_route_invocations": 0,
            "new_solver_mechanisms": 0,
            "new_action_rules": 0,
            "new_carrier_mechanisms": 0,
            "posthoc_thresholds_or_pair_rules": 0,
            "external_truth_or_metrics_reads": 0,
        },
        "claim_ceiling": "FINITE_TWENTY_SOURCE_OUT_OF_FAMILY_FALSIFICATION_TEST_OF_THE_FROZEN_WL_PAIR_SELECTOR_AGAINST_EXISTING_E3_GROUND_TRUTH_WITH_THE_SCOPE_THEOREM_APPLIED_ONLY_INSIDE_ITS_EXPLICIT_RESOURCE_BOUND",
        "scientific_firewall": {
            "WL_SUFFICIENCY_WITHOUT_DIRECT_EXACT_CHECK": "NOT_PROVED",
            "ARBITRARY_RESIDUAL_SEPARATOR_TRACTABILITY": "NOT_PROVED",
            "GENERAL_SAT_IN_P": "NOT_PROVED",
            "P_VS_NP": "OPEN",
        },
    }


if __name__ == "__main__":
    print(json.dumps(main(), sort_keys=True, separators=(",", ":")))
