from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47f_small_reachable_fixpoint_full_macro_falsifier as r47f
import janus_trump_r47i_r47g_one_swap_macro_dead_complement_hunt as r47i
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r47m_post_dp_full_existing_stack_closure as r47m

R47K_RESULT = Path(__file__).resolve().parents[1] / "research" / "JANUS_TRUMP_R47K_EXPLICIT_REACHABLE_COUNTEREXAMPLE_TO_EXTENDED_NORMALIZATION_CLOSURE_RESULT_2026-09-03.json"
CENTER_ORIGINAL_HASH = "eb13be26c29c106cf172db0be435aaf852d1e1248fced151c5356791f70024da"
CENTER_FIXPOINT_HASH = "9a84c02f1570e752ac0c017037b8a4a40c2599b53faf51bcd6d957f40aa81dde"
CENTER_FIXPOINT_CLV = [77, 206, 22]
EXPECTED_R47J_ACCEPTED = ()
EXPECTED_R47M_FIRST_ACCEPT = 20
EXPECTED_R47M_FINAL_CLV = [76, 209, 20]


def validate_exact_3cnf(formula) -> None:
    f = r33.canonical_formula(formula)
    if not f:
        raise AssertionError("R47N_EMPTY_FORMULA")
    for clause in f:
        if len(clause) != 3:
            raise AssertionError(("R47N_NOT_EXACT_3CNF", clause))
        if r33.is_tautology(clause):
            raise AssertionError(("R47N_TAUTOLOGICAL_CLAUSE", clause))


def load_center_original():
    data = json.loads(R47K_RESULT.read_text())
    formula = r33.canonical_formula(data["mutated_original"]["formula"])
    validate_exact_3cnf(formula)
    if r47f.formula_hash(formula) != CENTER_ORIGINAL_HASH:
        raise AssertionError(("R47N_CENTER_ORIGINAL_HASH_DRIFT", r47f.formula_hash(formula)))
    return data, formula


def compact_candidate(candidate, replay_pass: Optional[bool] = None) -> dict:
    segments = candidate["normalization"]["segments"]
    sa_bve_sequence = [int(s["SA_BVE_var"]) for s in segments if s.get("SA_BVE_applied")]
    return {
        "var": int(candidate["var"]),
        "input_CLV": candidate["input_CLV"],
        "forced_DP_CLV": candidate["DP"]["measure_after_forced_DP"],
        "final_CLV": candidate["final_CLV"],
        "terminal": candidate["normalization"]["terminal"],
        "segment_count": int(candidate["normalization"]["segment_count"]),
        "SA_BVE_application_count": int(candidate["normalization"]["SA_BVE_application_count"]),
        "SA_BVE_sequence": sa_bve_sequence,
        "net_CLV_descent": bool(candidate["net_CLV_descent"]),
        "accepted": bool(candidate["accepted"]),
        "DP_independent_replay_pass": bool(candidate["DP_independent_replay_pass"]),
        "polynomial_intermediate_envelope_pass": bool(candidate["polynomial_intermediate_envelope_pass"]),
        "independent_full_replay_pass": replay_pass,
    }


def first_r47m_accept(fixpoint) -> dict:
    before = r33.canonical_formula(fixpoint)
    rows = []
    checked = 0
    for var in r33.variables(before):
        checked += 1
        candidate = r47m.macro_candidate_full_closure(before, int(var))
        if candidate is None:
            rows.append({"var": int(var), "candidate": False, "accepted": False})
            continue
        if not candidate["DP_independent_replay_pass"] or not candidate["polynomial_intermediate_envelope_pass"]:
            raise AssertionError(("R47N_CANDIDATE_INTEGRITY_FAIL", var))
        if candidate["accepted"]:
            replay = r47m.independent_replay(before, candidate)
            if not replay["pass"]:
                raise AssertionError(("R47N_ACCEPTED_FULL_REPLAY_FAIL", var, replay))
            row = compact_candidate(candidate, True)
            rows.append(row)
            return {
                "covered": True,
                "variables_checked": checked,
                "total_variables": len(r33.variables(before)),
                "selected_var": int(var),
                "selected": row,
                "rows_prefix": rows,
            }
        rows.append(compact_candidate(candidate, None))
    return {
        "covered": False,
        "variables_checked": checked,
        "total_variables": len(r33.variables(before)),
        "selected_var": None,
        "selected": None,
        "rows_prefix": rows,
    }


def r47j_accepted_pivots(fixpoint):
    before = r33.canonical_formula(fixpoint)
    out = []
    for var in r33.variables(before):
        candidate = r47j.macro_candidate_fixpoint(before, int(var))
        if candidate is not None and candidate["accepted"]:
            replay = r47j.independent_fixpoint_macro_replay(before, candidate)
            if not replay["pass"]:
                raise AssertionError(("R47N_R47J_REPLAY_DRIFT", var))
            out.append(int(var))
    return out


def frontier(center_original):
    p20 = [c for c in center_original if any(abs(l) == 20 for l in c)]
    p11 = [c for c in center_original if c not in p20 and any(abs(l) == 11 for l in c)]
    rest = [c for c in center_original if c not in p20 and c not in p11]
    for phase, sources in (
        ("CLAUSES_TOUCHING_RESCUE_ROOT_PIVOT_20", p20),
        ("CLAUSES_TOUCHING_EXPOSED_SA_BVE_PIVOT_11_NOT_ALREADY_IN_PHASE1", p11),
        ("REMAINING_CLAUSES", rest),
    ):
        for source in sources:
            for replacement in r47i.signed_same_support_variants(source):
                mutated = r47i.mutate_one_clause(center_original, source, replacement)
                yield phase, source, replacement, mutated


def compact_record(ordinal, phase, source, replacement, mutated, reached, scan):
    fixpoint = r33.canonical_formula(reached["formula"])
    return {
        "frontier_ordinal": int(ordinal),
        "phase": phase,
        "source_clause": list(source),
        "replacement_clause": list(replacement),
        "mutated_original_hash": r47f.formula_hash(mutated),
        "mutated_original_CLV": list(r33.measure(mutated)),
        "fixpoint_hash": r47f.formula_hash(fixpoint),
        "fixpoint_CLV": list(r33.measure(fixpoint)),
        "variables_checked_to_first_accept": int(scan["variables_checked"]),
        "total_fixpoint_variables": int(scan["total_variables"]),
        "selected_var": scan["selected_var"],
        "selected": scan["selected"],
        "rows_prefix": scan["rows_prefix"],
        "trajectory": reached["trajectory"],
    }


def hardness_key(record):
    return (
        int(record["variables_checked_to_first_accept"]),
        int(record["total_fixpoint_variables"]),
        str(record["fixpoint_hash"]),
    )


def run() -> dict:
    sealed, center = load_center_original()

    center_reached = r47f.reachable_fixpoint(center)
    if center_reached is None:
        raise AssertionError("R47N_CENTER_NO_REACHABLE_FIXPOINT")
    center_fixpoint = r33.canonical_formula(center_reached["formula"])
    if r47f.formula_hash(center_fixpoint) != CENTER_FIXPOINT_HASH:
        raise AssertionError(("R47N_CENTER_FIXPOINT_HASH_DRIFT", r47f.formula_hash(center_fixpoint)))
    if list(r33.measure(center_fixpoint)) != CENTER_FIXPOINT_CLV:
        raise AssertionError(("R47N_CENTER_FIXPOINT_CLV_DRIFT", list(r33.measure(center_fixpoint))))

    old_accept = r47j_accepted_pivots(center_fixpoint)
    if tuple(old_accept) != EXPECTED_R47J_ACCEPTED:
        raise AssertionError(("R47N_R47J_REGRESSION_DRIFT", old_accept))
    center_scan = first_r47m_accept(center_fixpoint)
    if not center_scan["covered"]:
        raise AssertionError("R47N_R47M_CENTER_NOT_COVERED")
    if center_scan["selected_var"] != EXPECTED_R47M_FIRST_ACCEPT:
        raise AssertionError(("R47N_R47M_CENTER_SELECTED_VAR_DRIFT", center_scan["selected_var"]))
    if center_scan["selected"]["final_CLV"] != EXPECTED_R47M_FINAL_CLV:
        raise AssertionError(("R47N_R47M_CENTER_FINAL_CLV_DRIFT", center_scan["selected"]["final_CLV"]))

    metrics = {
        "frontier_positions": 0,
        "mutants_generated": 0,
        "mutants_skipped_duplicate": 0,
        "semantic_or_nonfixpoint_mutants": 0,
        "reachable_fixpoints": 0,
        "unique_reachable_fixpoints": 0,
        "R47M_covered_fixpoints": 0,
        "R47M_macro_dead_fixpoints": 0,
        "phase": {},
    }
    seen_fixpoints = set()
    first_counterexample = None
    hardest_covered = None

    for ordinal, (phase, source, replacement, mutated) in enumerate(frontier(center), 1):
        metrics["frontier_positions"] += 1
        pm = metrics["phase"].setdefault(phase, {
            "frontier_positions": 0,
            "mutants_generated": 0,
            "reachable_fixpoints": 0,
            "unique_reachable_fixpoints": 0,
            "R47M_covered": 0,
            "R47M_macro_dead": 0,
        })
        pm["frontier_positions"] += 1
        if mutated is None:
            metrics["mutants_skipped_duplicate"] += 1
            continue
        validate_exact_3cnf(mutated)
        metrics["mutants_generated"] += 1
        pm["mutants_generated"] += 1

        reached = r47f.reachable_fixpoint(mutated)
        if reached is None:
            metrics["semantic_or_nonfixpoint_mutants"] += 1
            continue
        metrics["reachable_fixpoints"] += 1
        pm["reachable_fixpoints"] += 1
        fixpoint = r33.canonical_formula(reached["formula"])
        fh = r47f.formula_hash(fixpoint)
        if fh in seen_fixpoints:
            continue
        seen_fixpoints.add(fh)
        metrics["unique_reachable_fixpoints"] += 1
        pm["unique_reachable_fixpoints"] += 1

        scan = first_r47m_accept(fixpoint)
        record = compact_record(ordinal, phase, source, replacement, mutated, reached, scan)
        if not scan["covered"]:
            metrics["R47M_macro_dead_fixpoints"] += 1
            pm["R47M_macro_dead"] += 1
            record["mutated_original_formula"] = [list(c) for c in mutated]
            record["fixpoint_formula"] = [list(c) for c in fixpoint]
            record["all_R47M_macro_rows"] = scan["rows_prefix"]
            first_counterexample = record
            break

        metrics["R47M_covered_fixpoints"] += 1
        pm["R47M_covered"] += 1
        if hardest_covered is None or hardness_key(record) > hardness_key(hardest_covered):
            hardest_covered = record

    verdict = (
        "EXPLICIT_REACHABLE_COUNTEREXAMPLE_TO_R47M_JOINT_EXISTING_STACK_CLOSURE_FOUND"
        if first_counterexample is not None
        else "NO_COUNTEREXAMPLE_IN_FROZEN_R47K_CENTERED_ONE_SWAP_FRONTIER__R47M_O4_STILL_OPEN"
    )

    return {
        "gate": "JANUS_TRUMP_R47N_R47M_JOINT_STACK_CLOSURE_ONE_SWAP_FALSIFIER",
        "verdict": verdict,
        "regression": {
            "center_original_hash": CENTER_ORIGINAL_HASH,
            "center_fixpoint_hash": CENTER_FIXPOINT_HASH,
            "center_fixpoint_CLV": CENTER_FIXPOINT_CLV,
            "R47J_accepted_pivots": old_accept,
            "R47M_first_accepted_pivot": center_scan["selected_var"],
            "R47M_first_accepted_final_CLV": center_scan["selected"]["final_CLV"],
            "R47M_first_accepted_SA_BVE_sequence": center_scan["selected"]["SA_BVE_sequence"],
        },
        "metrics": metrics,
        "first_counterexample": first_counterexample,
        "hardest_covered": hardest_covered,
        "interpretation": {
            "finite_falsification_frontier_only": True,
            "no_counterexample_does_not_prove_O4": True,
            "counterexample_if_found_refutes_R47M_grammar_only": True,
            "depth3_or_unbounded_DP_authorized": False,
            "runtime_selection_policy": "FIRST_CERTIFIED_ACCEPTED_PIVOT",
        },
        "firewall": {
            "O4_UNIVERSAL_COVERAGE_FOR_R47M": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_EQ_NP": "NOT_PROVED",
            "P_NE_NP": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    args = parser.parse_args()
    result = run()
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    compact = {
        "gate": result["gate"],
        "verdict": result["verdict"],
        "regression": result["regression"],
        "metrics": result["metrics"],
        "counterexample_summary": None if result["first_counterexample"] is None else {
            k: result["first_counterexample"][k]
            for k in (
                "frontier_ordinal", "phase", "source_clause", "replacement_clause",
                "mutated_original_hash", "fixpoint_hash", "fixpoint_CLV",
                "variables_checked_to_first_accept", "total_fixpoint_variables"
            )
        },
        "firewall": result["firewall"],
    }
    print(json.dumps(compact, sort_keys=True))


if __name__ == "__main__":
    main()
