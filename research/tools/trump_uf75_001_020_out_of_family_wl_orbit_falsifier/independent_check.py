from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from research.tools.apma_uf20_011_015_fresh_generic_pendant_wl_replication import candidate as frozen
from research.tools.apma_uf20_wl_historical_closed_control_falsifier import candidate as wl_ref
from research.tools.apma_unseen_local_invariant_orbit_count import candidate as orbit

ROOT = Path(__file__).resolve().parents[3]
CANDIDATE = ROOT / "research/tools/trump_uf75_001_020_out_of_family_wl_orbit_falsifier/candidate.py"
PREREG = ROOT / "research/TRUMP_UF75_001_020_OUT_OF_FAMILY_WL_ORBIT_FALSIFIER_EVALUATION_PREREGISTRATION_2026-09-18_v1.0.json"
REVIEW = ROOT / "research/TRUMP_UF75_001_020_OUT_OF_FAMILY_WL_ORBIT_FALSIFIER_EVALUATION_REVIEW_2026-09-18_v1.0.json"
SOURCE_FREEZE = ROOT / "research/TRUMP_UF75_001_020_OUT_OF_FAMILY_SOURCE_FREEZE_AUTHORITY_2026-09-18_v1.0.json"
SCOPE_THEOREM = ROOT / "research/TRUMP_WL_DIRECT_EXACT_E3_SCOPE_BOUND_THEOREM_RESULT_2026-09-18_v1.0.json"
FRESH = ROOT / "research/tools/apma_uf20_011_015_fresh_generic_pendant_wl_replication/candidate.py"
PROJECTION = ROOT / "research/tools/apma_satlib_uf20_r000_r111_projected_core_replay/projection_identity.py"
WL = ROOT / "research/tools/apma_uf20_wl_historical_closed_control_falsifier/candidate.py"
ORBIT = ROOT / "research/tools/apma_unseen_local_invariant_orbit_count/candidate.py"
EXPECTED = {
    CANDIDATE: "019b8f4566652deb1fe8087da9ee8e76d55e722f",
    PREREG: "84787b2f4fce9a3b79dfc9ba92c7fd0b61f412c9",
    REVIEW: "884c5ae73cd31b9161165be155fce4640390f7ab",
    SOURCE_FREEZE: "102dedd7602f7f7f3044f0904591da282dc25eb2",
    SCOPE_THEOREM: "3cbf05cb0b0249ddf365bc43d176a06ddb7f72af",
    FRESH: "9ec365ae27a6caa7b936cd33040e542f183ded99",
    PROJECTION: "2ef48e73974a5f43d3f4fb4809ebd0c09c0f5be4",
    WL: "6b697fd8b3de4c83f8226b06399b6bad99953d4e",
    ORBIT: "a076cfc56d68aad0348415e313705da1f6b9cdcd",
}
CANDIDATE_MODULE = "research.tools.trump_uf75_001_020_out_of_family_wl_orbit_falsifier.candidate"
ORDER = tuple(f"UF75_{i:03d}" for i in range(1, 21))


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def canonical_sha(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def parse_uf75(path: Path):
    nvars = nclauses = None
    clauses = []
    buf = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        s = raw.strip()
        if not s or s.startswith("c") or s in {"%", "0"}:
            continue
        if s.startswith("p "):
            p = s.split()
            if len(p) != 4 or p[:2] != ["p", "cnf"]:
                raise ValueError("BAD_HEADER")
            nvars, nclauses = int(p[2]), int(p[3])
            continue
        for value in map(int, s.split()):
            if value == 0:
                if len(buf) != 3 or len({abs(x) for x in buf}) != 3 or any(not 1 <= abs(x) <= 75 for x in buf):
                    raise ValueError("BAD_3CNF_CLAUSE")
                clauses.append(tuple(buf))
                buf = []
            else:
                buf.append(value)
    if (nvars, nclauses) != (75, 325) or len(clauses) != 325 or buf:
        raise ValueError("UF75_CONTRACT_FAILURE")
    canonical = "".join(" ".join(map(str, c)) + " 0\\n" for c in clauses).encode("ascii")
    return clauses, hashlib.sha256(canonical).hexdigest()


def classes(colors, keys, value_of):
    groups = defaultdict(list)
    for key in keys:
        groups[colors[key]].append(int(value_of(key)))
    out = [sorted(values) for values in groups.values() if len(values) > 1]
    out.sort(key=lambda x: (len(x), x))
    return out


def prediction(reduced: dict[str, Any]):
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
    scope_n = scope_L = scope_bound = None
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


def outcome(summary):
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


def recompute():
    bindings = {str(path.relative_to(ROOT)): blob(path) == expected for path, expected in EXPECTED.items()}
    if not all(bindings.values()):
        return {"verdict": "HALT_INDEPENDENT_AUTHORITY_BINDING_FAILURE", "bindings": bindings}
    if CANDIDATE_MODULE in sys.modules:
        return {"verdict": "HALT_INDEPENDENT_CANDIDATE_IMPORT_VIOLATION"}

    review = json.loads(REVIEW.read_text())
    source_freeze = json.loads(SOURCE_FREEZE.read_text())
    theorem = json.loads(SCOPE_THEOREM.read_text())
    guard_checks = {
        "review_authorized": review.get("review_verdict") == "PASS_CLEAN_UF75_OUT_OF_FAMILY_WL_ORBIT_FALSIFIER_SPEC__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE",
        "source_freeze_independent": source_freeze.get("execution", {}).get("independent_verdict") == "PASS_INDEPENDENT_UF75_001_020_SOURCE_FREEZE_VERIFICATION",
        "source_order": tuple(r.get("source") for r in source_freeze.get("source_receipts", [])) == ORDER,
        "source_count": len(source_freeze.get("source_receipts", [])) == 20,
        "theorem_pass": theorem.get("scientific_outcome") == "PASS_SCOPE_BOUND_DIRECT_EXACT_TRANSPOSITION_WITNESS_SUFFICIENCY_FOR_FROZEN_E3",
    }
    if not all(guard_checks.values()):
        return {"verdict": "HALT_INDEPENDENT_GUARD_FAILURE", "guard_checks": guard_checks}

    ok, training = frozen.training_regression()
    if not ok:
        return {"verdict": "HALT_INDEPENDENT_TRAINING_REGRESSION_FAILURE", "training_regression": training}

    metadata = {row["source"]: row for row in source_freeze["source_receipts"]}
    predictions = []
    prepared = []
    direct_checks = 0
    for source in ORDER:
        meta = metadata[source]
        path = ROOT / meta["committed_copy_path"]
        source_blob = frozen.blob(path)
        clauses, formula_hash = parse_uf75(path)
        if source_blob != meta["committed_git_blob"] or formula_hash != meta["canonical_formula_sha256"]:
            return {"verdict": "HALT_INDEPENDENT_SOURCE_BINDING_FAILURE", "source": source}
        projected = frozen.projection_identity.normalize_projection(source, clauses)[0]
        reduced, D, T = frozen.generic_round(projected)
        pred = prediction(reduced)
        direct_checks += int(pred.pop("direct_checks"))
        predictions.append({
            "source": source,
            "source_git_blob": source_blob,
            "canonical_formula_sha256": formula_hash,
            "projected_raw_sha256": frozen.csha(projected),
            "projected_variables": len(projected["variables"]),
            "projected_constraints": len(projected["constraints"]),
            "degree1_variables": D,
            "target_constraints": T,
            "reduced_raw_sha256": frozen.csha(reduced),
            "reduced_variables": len(reduced["variables"]),
            "reduced_constraints": len(reduced["constraints"]),
            **pred,
        })
        prepared.append((source, reduced))

    if len(predictions) != 20:
        return {"verdict": "FAIL_INDEPENDENT_PREDICTION_COUNT"}
    digest = canonical_sha(predictions)
    pred_by = {row["source"]: row for row in predictions}

    e3_positive = []
    recovered = []
    misses = []
    theorem_falsifiers = []
    open_false_positives = []
    scope_exits = []
    portfolio_open = []
    portfolio_closed = []
    ground_truth = []
    for source, reduced in prepared:
        route = frozen.route_row(reduced)
        p = pred_by[source]
        e3 = route.get("E3", {})
        ep = bool(e3.get("solver_authority") is True and e3.get("status") in frozen.CLOSED_ORBIT)
        edges = [sorted(map(int, edge)) for edge in (e3.get("generator_edges") or [])]
        pair = p.get("wl_derived_pair")
        pp = p.get("prediction_positive") is True
        in_scope = p.get("scope_bound_holds") is True
        rec = bool(ep and pp and pair in edges)
        miss = bool(ep and not rec)
        tf = bool(pp and in_scope and not ep)
        is_open = route.get("label") == "PORTFOLIO_OPEN"
        fp = bool(pp and in_scope and is_open)
        exit_ = bool(pp and p.get("scope_bound_holds") is False)
        ground_truth.append({
            "source": source,
            "portfolio_label": route.get("label"),
            "e3_positive": ep,
            "e3_generator_edges": edges,
            "selector_recovered": rec,
            "selector_miss": miss,
            "in_scope_theorem_falsifier": tf,
            "in_scope_open_false_positive": fp,
            "resource_scope_exit": exit_,
        })
        if ep: e3_positive.append(source)
        if rec: recovered.append(source)
        if miss: misses.append(source)
        if tf: theorem_falsifiers.append(source)
        if fp: open_false_positives.append(source)
        if exit_: scope_exits.append(source)
        (portfolio_open if is_open else portfolio_closed).append(source)

    summary = {
        "prediction_positive_sources": [r["source"] for r in predictions if r["prediction_positive"]],
        "prediction_positive_count": sum(1 for r in predictions if r["prediction_positive"]),
        "in_scope_prediction_positive_sources": [r["source"] for r in predictions if r["prediction_positive"] and r["scope_bound_holds"] is True],
        "resource_scope_exits": scope_exits,
        "e3_positive_sources": e3_positive,
        "e3_positive_count": len(e3_positive),
        "selector_recovered_sources": recovered,
        "selector_misses": misses,
        "in_scope_theorem_falsifiers": theorem_falsifiers,
        "in_scope_open_false_positives": open_false_positives,
        "portfolio_open_sources": portfolio_open,
        "portfolio_closed_sources": portfolio_closed,
    }
    return {
        "verdict": "PASS_INDEPENDENT_UF75_OUT_OF_FAMILY_RECOMPUTATION",
        "scientific_outcome": outcome(summary),
        "candidate_imported": False,
        "prediction_stage_sha256": digest,
        "prediction_rows": predictions,
        "ground_truth_compact": ground_truth,
        "summary": summary,
        "direct_exact_checks": direct_checks,
        "prediction_full_transposition_searches": 0,
        "signed_route_invocations": 0,
    }


def main(candidate_json: Path):
    independent = recompute()
    if independent.get("verdict") != "PASS_INDEPENDENT_UF75_OUT_OF_FAMILY_RECOMPUTATION":
        return independent
    candidate = json.loads(candidate_json.read_text())
    cs = candidate.get("summary", {})
    ir = independent
    checks = {
        "candidate_not_imported": ir.get("candidate_imported") is False and CANDIDATE_MODULE not in sys.modules,
        "prediction_stage_count": candidate.get("prediction_stage_count") == 20,
        "prediction_completed_before_ground_truth": candidate.get("prediction_stage_completed_before_ground_truth") is True,
        "prediction_digest": candidate.get("prediction_stage_sha256") == ir.get("prediction_stage_sha256"),
        "prediction_positive_sources": cs.get("prediction_positive_sources") == ir["summary"]["prediction_positive_sources"],
        "in_scope_prediction_positive_sources": cs.get("in_scope_prediction_positive_sources") == ir["summary"]["in_scope_prediction_positive_sources"],
        "resource_scope_exits": cs.get("resource_scope_exits") == ir["summary"]["resource_scope_exits"],
        "e3_positive_sources": cs.get("e3_positive_sources") == ir["summary"]["e3_positive_sources"],
        "selector_recovered_sources": cs.get("selector_recovered_sources") == ir["summary"]["selector_recovered_sources"],
        "selector_misses": cs.get("selector_misses") == ir["summary"]["selector_misses"],
        "theorem_falsifiers": cs.get("in_scope_theorem_falsifiers") == ir["summary"]["in_scope_theorem_falsifiers"],
        "open_false_positives": cs.get("in_scope_open_false_positives") == ir["summary"]["in_scope_open_false_positives"],
        "portfolio_open_sources": cs.get("portfolio_open_sources") == ir["summary"]["portfolio_open_sources"],
        "portfolio_closed_sources": cs.get("portfolio_closed_sources") == ir["summary"]["portfolio_closed_sources"],
        "scientific_outcome": candidate.get("verdict") == ir.get("scientific_outcome"),
        "resource_no_prediction_search": candidate.get("resource_receipt", {}).get("prediction_full_transposition_searches") == 0,
        "resource_signed_route_zero": candidate.get("resource_receipt", {}).get("signed_route_invocations") == 0,
        "direct_checks_equal": candidate.get("resource_receipt", {}).get("prediction_direct_exact_checks") == ir.get("direct_exact_checks"),
        "external_metrics_zero": candidate.get("resource_receipt", {}).get("external_truth_or_metrics_reads") == 0,
    }
    return {
        **independent,
        "comparison_checks": checks,
        "candidate_verdict": candidate.get("verdict"),
        "verdict": "PASS_INDEPENDENT_UF75_OUT_OF_FAMILY_WL_ORBIT_FALSIFIER_VERIFICATION" if all(checks.values()) else "FAIL_INDEPENDENT_UF75_OUT_OF_FAMILY_WL_ORBIT_FALSIFIER_MISMATCH",
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True)
    args = ap.parse_args()
    print(json.dumps(main(Path(args.candidate)), sort_keys=True, separators=(",", ":")))
