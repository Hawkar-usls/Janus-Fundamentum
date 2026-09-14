from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import importlib.util
import json

HERE = Path(__file__).resolve().parent
V11 = HERE.parent / "trump_apma_novel_composite_transfer"
RESULT_PATH = HERE / "MICRO_REVEALED_RESULT.json"

_spec = importlib.util.spec_from_file_location("candidate_structural_layer", HERE / "structural_layer.py")
sl = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(sl)


def direct_gyo_case(name, scopes, expect_alpha=True):
    gyo = sl.deterministic_gyo(scopes)
    ri = sl.running_intersection(scopes, gyo["edges"]) if gyo["alpha_acyclic"] else None
    passed = gyo["alpha_acyclic"] == expect_alpha
    if expect_alpha:
        passed = passed and bool(ri and ri["pass"]) and len(gyo["parents"]) == len(scopes)
    return {"name": name, "pass": passed, "alpha_acyclic": gyo["alpha_acyclic"], "running_intersection": ri, "gyo": gyo}


def run_micro():
    rows = []
    rows.append(direct_gyo_case("POS_SINGLE_VAR_SHARED_3", {"R0000": (1,), "R0001": (1,), "R0002": (1,)}))
    rows.append(direct_gyo_case("POS_WIDTH2_DUPLICATE_SCOPE", {"R0000": (1, 2), "R0001": (1, 2)}))
    rows.append(direct_gyo_case("POS_FRAGMENTED_PORT_PATH", {"R0000": (1,), "R0001": (1, 2), "R0002": (2, 3), "R0003": (3,)}))
    rows.append(direct_gyo_case("POS_ALPHA_MULTI_SEPARATOR", {"R0000": (1, 2), "R0001": (2, 3), "R0002": (3, 4), "R0003": (4, 5)}))
    rows.append(direct_gyo_case("NEG_CYCLE_XY_YZ_ZX", {"R0000": (1, 2), "R0001": (2, 3), "R0002": (1, 3)}, expect_alpha=False))
    width4_leaves = [
        [[1, 2, 3, 4]],
        [[-1]],
        [[-2]],
        [[-3]],
        [[-4]],
    ]
    _, width4_error, width4_detail = sl.complete_boundary_scopes(width4_leaves, 3)
    rows.append({"name": "NEG_BOUNDARY_WIDTH_4", "pass": width4_error == "COMPONENT_BOUNDARY_GT_3", "error": width4_error, "detail": width4_detail})

    ranking_root = [[1, 2], [2, 3], [3, 4], [4, 5]]
    alt_groups, alt_error = sl._split_by_separator(ranking_root, (2,))
    admitted_keys = set()
    if alt_groups is not None:
        admitted_keys = {tuple(tuple(c) for c in sl.tc.canon(group)) for group in alt_groups}

    def ranking_admitter(cnf):
        key = tuple(tuple(c) for c in sl.tc.canon(cnf))
        admitted = key in admitted_keys
        return admitted, {"admitted": admitted, "decision": "SAT" if admitted else None}

    _, ranking_error, ranking_trace = sl.discover_leaves(ranking_root, 1, test_only_admitter=ranking_admitter)
    selected = ranking_trace[0].get("separator") if ranking_trace else None
    alt_success = alt_error is None and all(ranking_admitter(group)[0] for group in alt_groups or [])
    rows.append({
        "name": "NEG_RANKING_TRAP_NO_BACKTRACKING",
        "pass": ranking_error is not None and selected == [3] and alt_success,
        "selected_separator": selected,
        "alternative_separator": [2],
        "alternative_would_finish_under_test_admitter": alt_success,
        "observed_error": ranking_error,
        "trace": ranking_trace,
    })
    zero_rel, zero_error = sl.tc.leaf_relation([[]], [])
    zero_graph = {"adj": {0: []}, "edges": []}
    zero_transfer = sl.tc.transfer_join([[]], [[[]]], zero_graph, [zero_rel] if zero_rel else []) if zero_rel is not None else {"decision": None}
    rows.append({
        "name": "NEG_ZERO_ARITY_UNSAT",
        "pass": zero_error is None and zero_rel is not None and zero_rel["boundary"] == [] and zero_rel["allowed"] == [] and zero_transfer["decision"] == "UNSAT",
        "relation": zero_rel,
        "transfer_decision": zero_transfer.get("decision"),
    })

    semantic_scopes = {"R0000": (1,), "R0001": (1,), "R0002": (1, 2)}
    semantic_gyo = sl.deterministic_gyo(semantic_scopes)
    semantic_ids = list(semantic_scopes)
    semantic_graph = sl._numeric_graph(semantic_ids, semantic_gyo)
    semantic_relations = [
        {"boundary": [1], "allowed": [{"tuple": [0], "witness": {1: False}}], "forbidden": []},
        {"boundary": [1], "allowed": [{"tuple": [1], "witness": {1: True}}], "forbidden": []},
        {"boundary": [1, 2], "allowed": [{"tuple": [0, 0], "witness": {1: False, 2: False}}, {"tuple": [1, 0], "witness": {1: True, 2: False}}], "forbidden": []},
    ]
    semantic_transfer = sl.tc.transfer_join([], [[], [], []], semantic_graph, semantic_relations)
    rows.append({
        "name": "NEG_DUPLICATE_SUBSET_RELATION_SEMANTICS",
        "pass": semantic_gyo["alpha_acyclic"] and len(semantic_gyo["parents"]) == 3 and semantic_transfer["decision"] == "UNSAT",
        "gyo": semantic_gyo,
        "transfer_decision": semantic_transfer["decision"],
    })
    sat_source = [[1]]
    sat_result = sl.solve_formula_candidate(sat_source, 3)
    tampered = deepcopy(sat_result)
    if tampered.get("assignment") is not None:
        tampered["assignment"][1] = False
    tamper_verify = sl.verify_candidate(sat_source, tampered) if sat_result.get("admitted") else {"pass": False, "reason": "BASE_NOT_ADMITTED"}
    rows.append({
        "name": "NEG_SOURCE_ROOT_REPLAY_TAMPER",
        "pass": sat_result.get("decision") == "SAT" and not tamper_verify.get("pass") and tamper_verify.get("reason") == "SOURCE_ROOT_REPLAY_FAIL",
        "verify": tamper_verify,
    })

    norm_source = [[1, -1, 2], [3, 3], [3], [-4, 5], [-4, 5]]
    norm, audit = sl.normalize_with_audit(norm_source)
    rows.append({
        "name": "POS_DUPLICATE_TAUTOLOGY_CANON_AUDIT",
        "pass": audit["source_clause_count"] == 5 and audit["normalized_clause_count"] == 2 and audit["tautology_count"] == 1 and audit["duplicate_count"] == 2,
        "normalized": norm,
        "audit": audit,
    })
    return rows


def run_revealed():
    data = json.loads((V11 / "calibration.json").read_text(encoding="utf-8"))
    cases = data["cases"]
    rows = []
    for case in cases:
        result = sl.solve_formula_candidate(case["cnf"], 3)
        verify = sl.verify_candidate(case["cnf"], result) if result.get("admitted") else {"pass": False, "reason": result.get("reason")}
        expected = case["truth"]
        rows.append({
            "id": case["id"],
            "expected": expected,
            "admitted": bool(result.get("admitted")),
            "decision": result.get("decision"),
            "reason": result.get("reason"),
            "leaf_count": result.get("leaf_count"),
            "verify_pass": bool(verify.get("pass")),
            "correct": bool(result.get("admitted")) and result.get("decision") == expected and bool(verify.get("pass")),
            "running_intersection": (result.get("certificate") or {}).get("running_intersection"),
            "gyo_trace": (result.get("certificate") or {}).get("gyo", {}).get("trace"),
        })
    return rows

def main():
    sl.assert_frozen_semantics()
    micro = run_micro()
    revealed = run_revealed()
    sat_rows = [row for row in revealed if row["expected"] == "SAT"]
    unsat_rows = [row for row in revealed if row["expected"] == "UNSAT"]
    report = {
        "artifact": "JANUS-TRUMP-APMA-ALPHA-ACYCLIC-JOIN-TREE-MICRO-REVEALED-v0.3",
        "authority": "DIAGNOSTIC_FREEZE_PREPARATION_ONLY__NON_SCIENTIFIC_AUTHORITY",
        "blind_population_generated": False,
        "historical_blind_admission_holdout_read": False,
        "late_v1_2_v1_3_used": False,
        "micro": micro,
        "micro_pass": sum(bool(row["pass"]) for row in micro),
        "micro_total": len(micro),
        "revealed": revealed,
        "revealed_correct": sum(bool(row["correct"]) for row in revealed),
        "revealed_total": len(revealed),
        "revealed_sat_correct": sum(bool(row["correct"]) for row in sat_rows),
        "revealed_sat_total": len(sat_rows),
        "revealed_unsat_correct": sum(bool(row["correct"]) for row in unsat_rows),
        "revealed_unsat_total": len(unsat_rows),
        "scientific_firewall": {
            "scientific_v1_1_verdict": "FAIL_NO_TRANSFER_RULE",
            "diagnostic_pass_is_theorem_evidence": False,
            "P_VS_NP": "OPEN",
            "APMA_UNSEEN_LOCAL_INVARIANT_INDUCTION_FALSIFIER_GATE": "LOCKED"
        }
    }
    report["overall"] = "PASS_FREEZE_PREP_CONTROLS" if report["micro_pass"] == report["micro_total"] and report["revealed_correct"] == report["revealed_total"] else "FAIL_OPEN_FREEZE_PREP_CONTROL"
    RESULT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("overall", "micro_pass", "micro_total", "revealed_correct", "revealed_total", "revealed_sat_correct", "revealed_unsat_correct")}, sort_keys=True))


if __name__ == "__main__":
    main()
