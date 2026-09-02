from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r34_affine_xor_terminal_against_tseitin_core as r34
import janus_trump_r35b_single_literal_rup_vivification as r35b
import janus_trump_r42_subsumption_aware_bve_successor as r42
import janus_trump_r44_43004_stall_class_forensics as r44

Clause = Tuple[int, ...]
Formula = Tuple[Clause, ...]

R45_PREREG_COMMIT = "24a346044ca6db939a2d85e91e0bd00365dc1362"
R44_SEALED_FORENSICS_COMMIT = "0cf34cc3697a24a9b824dfccb9b5731dfa04d029"
EXPOSED_43004_STALL_HASH = "95c0051895557d9353cc889cc7b1a35d225e60f264dfd8da56bb4da67439a6b7"
FRESH_UNSEEN_SPECS = (
    {"seed": 45001, "n": 24, "ratio": 4.30},
    {"seed": 45002, "n": 24, "ratio": 4.30},
    {"seed": 45003, "n": 28, "ratio": 4.30},
    {"seed": 45004, "n": 28, "ratio": 4.30},
    {"seed": 45005, "n": 32, "ratio": 4.30},
    {"seed": 45006, "n": 32, "ratio": 4.30},
)


def canonical_sha256(obj: object) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def clv(formula: Formula) -> Tuple[int, int, int]:
    return r33.measure(r33.canonical_formula(formula))


def json_bytes(obj: object) -> int:
    return len(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def exact_dp_record(before_formula: Formula, var: int) -> Optional[dict]:
    before = r33.canonical_formula(before_formula)
    pos, neg, resolvents, pair_checks = r42.all_dp_resolvents(before, int(var))
    if not pos or not neg:
        return None
    base = tuple(c for c in before if var not in c and -var not in c)
    pool = r33.canonical_formula(list(base) + list(resolvents))
    transformed = r42.subsumption_minimize(pool)
    record = {
        "var": int(var),
        "positive": [list(c) for c in pos],
        "negative": [list(c) for c in neg],
        "full_non_tautological_resolvents": [list(c) for c in resolvents],
        "base_clause_count": len(base),
        "pool_clause_count_before_subsumption": len(pool),
        "transformed": [list(c) for c in transformed],
        "measure_before": list(clv(before)),
        "measure_after_forced_DP": list(clv(transformed)),
        "resolution_pair_checks": int(pair_checks),
        "generated_resolvent_literals": sum(len(c) for c in resolvents),
        "subsumption_pair_checks_upper": len(pool) * len(pool),
        "peak_intermediate_clauses": max(len(before), len(pool), len(transformed)),
        "peak_intermediate_literals": max(
            sum(len(c) for c in before),
            sum(len(c) for c in pool),
            sum(len(c) for c in transformed),
        ),
    }
    record["certificate_bytes"] = json_bytes(record)
    return record


def independent_dp_replay(before_formula: Formula, record: dict) -> dict:
    before = r33.canonical_formula(before_formula)
    var = int(record["var"])
    pos, neg, resolvents, pair_checks = r42.all_dp_resolvents(before, var)
    base = tuple(c for c in before if var not in c and -var not in c)
    pool = r33.canonical_formula(list(base) + list(resolvents))
    expected = r42.subsumption_minimize(pool)
    claimed = r33.canonical_formula(record["transformed"])
    claimed_sets = [set(c) for c in claimed]
    omitted_pool = [c for c in pool if c not in claimed]
    omitted_subsumed = all(any(set(k) <= set(c) for k in claimed_sets) for c in omitted_pool)
    fields = {
        "sources_ok": [list(c) for c in pos] == record["positive"] and [list(c) for c in neg] == record["negative"],
        "resolvents_ok": [list(c) for c in resolvents] == record["full_non_tautological_resolvents"],
        "pair_count_ok": pair_checks == int(record["resolution_pair_checks"]),
        "pool_count_ok": len(pool) == int(record["pool_clause_count_before_subsumption"]),
        "transformed_exact": expected == claimed,
        "var_removed": var not in r33.variables(claimed),
        "every_omitted_pool_clause_subsumed": omitted_subsumed,
    }
    return {"pass": all(fields.values()), **fields, "omitted_pool_clause_count": len(omitted_pool)}


def polynomial_envelope(before_formula: Formula, record: dict) -> dict:
    C, _, V = clv(before_formula)
    pair_bound = (C * C) // 4 + 1
    clause_bound = C + pair_bound
    literal_bound = clause_bound * max(1, V)
    fields = {
        "resolution_pair_checks_within_C2_over_4": int(record["resolution_pair_checks"]) <= pair_bound,
        "peak_clauses_within_C_plus_C2_over_4": int(record["peak_intermediate_clauses"]) <= clause_bound,
        "peak_literals_within_O_C2V_witness_bound": int(record["peak_intermediate_literals"]) <= literal_bound,
        "subsumption_checks_within_pool_squared": int(record["subsumption_pair_checks_upper"]) <= clause_bound * clause_bound,
    }
    return {
        "pass": all(fields.values()),
        **fields,
        "C": C,
        "V": V,
        "pair_bound": pair_bound,
        "clause_bound": clause_bound,
        "literal_bound": literal_bound,
    }


def normalize_after_dp(transformed_formula: Formula) -> dict:
    forced = r33.canonical_formula(transformed_formula)
    reduced = r33.simplify(forced)
    after_r33 = r33.canonical_formula(reduced["final_formula"])
    ledger = {
        "R33_check_operation_upper_ledger": int(reduced["total_check_operation_count_upper_ledger"]),
        "R33_certificate_bytes": int(reduced["total_certificate_bytes"]),
        "RUP_checks": 0,
        "RUP_UP_clause_scans": 0,
        "RUP_UP_literal_inspections": 0,
        "GF2_estimated_bit_ops": 0,
        "terminal_Horn_clause_scans": 0,
        "terminal_2SAT_scc_calls": 0,
    }
    terminal = None
    semantic_sat: Optional[bool] = None
    terminal_assignment: Optional[Dict[int, bool]] = None
    terminal_verification = None
    affine_reason = None
    rup_record = None
    final_formula = after_r33

    if reduced["terminal"] != "STALLED_STACK_LEAN_CORE":
        solved = r42.solve_declared_terminal(after_r33, reduced["terminal"])
        if not solved["verification_pass"]:
            raise AssertionError(("R45A_DECLARED_TERMINAL_VERIFY_FAIL", solved))
        terminal = solved["kind"]
        semantic_sat = bool(solved["sat"])
        terminal_assignment = solved.get("assignment")
        terminal_verification = solved
        if solved["kind"] == "HORN_FORWARD_CHAIN":
            ledger["terminal_Horn_clause_scans"] += int(solved["solver"]["clause_scans"])
        if solved["kind"] == "2SAT_SCC":
            ledger["terminal_2SAT_scc_calls"] += int(solved["solver"]["scc_calls"])
    else:
        affine = r34.recognize_complete_affine_cnf(after_r33)
        affine_reason = affine["reason"]
        if affine["recognized"]:
            solution = r34.solve_gf2_with_certificate(affine["equations"])
            verify = r34.verify_affine_certificate(after_r33, affine, solution)
            if not verify["pass"]:
                raise AssertionError(("R45A_AFFINE_VERIFY_FAIL", verify))
            terminal = "AFFINE_XOR_SAT" if solution["sat"] else "AFFINE_XOR_UNSAT"
            semantic_sat = bool(solution["sat"])
            terminal_assignment = solution.get("assignment")
            terminal_verification = verify
            ledger["GF2_estimated_bit_ops"] += int(solution["estimated_bit_ops"])
        else:
            rup = r35b.run_candidate(after_r33)
            rup_replay = r35b.independent_certificate_replay(after_r33, rup)
            if not rup_replay["pass"]:
                raise AssertionError(("R45A_RUP_REPLAY_FAIL", rup_replay))
            rup_record = rup
            ledger["RUP_checks"] += int(rup["ledger"]["rup_checks"])
            ledger["RUP_UP_clause_scans"] += int(rup["ledger"]["up_clause_scans"])
            ledger["RUP_UP_literal_inspections"] += int(rup["ledger"]["up_literal_inspections"])
            final_formula = r33.canonical_formula(rup["final_formula"])
            if rup["status"] == "UNSAT_BY_UNIT_PROPAGATION":
                terminal = "RUP_UNSAT"
                semantic_sat = False
                terminal_verification = rup_replay

    return {
        "forced_formula_hash": r42.formula_hash(forced),
        "R33_result": reduced,
        "after_R33_formula_hash": r42.formula_hash(after_r33),
        "affine_reason": affine_reason,
        "RUP_record": rup_record,
        "terminal": terminal,
        "semantic_sat": semantic_sat,
        "terminal_assignment": terminal_assignment,
        "terminal_verification": terminal_verification,
        "final_formula": [list(c) for c in final_formula],
        "final_formula_hash": r42.formula_hash(final_formula),
        "final_CLV": list(clv(final_formula)),
        "ledger": ledger,
    }


def reconstruct_macro_sat(before_formula: Formula, dp_record: dict, normalization: dict) -> dict:
    if normalization["semantic_sat"] is not True:
        return {"applicable": False, "pass": True, "assignment": None}
    terminal_assignment = normalization["terminal_assignment"]
    if terminal_assignment is None:
        raise AssertionError("R45A_SAT_WITHOUT_TERMINAL_ASSIGNMENT")
    after_r33_assignment = r33.reconstruct_model(normalization["R33_result"], terminal_assignment)
    full = r42.reconstruct_sa_bve(dp_record, after_r33_assignment)
    passed = r33.eval_formula(r33.canonical_formula(before_formula), full)
    return {"applicable": True, "pass": passed, "assignment": full}


def macro_candidate_for_var(before_formula: Formula, var: int) -> Optional[dict]:
    before = r33.canonical_formula(before_formula)
    dp = exact_dp_record(before, int(var))
    if dp is None:
        return None
    dp_replay = independent_dp_replay(before, dp)
    envelope = polynomial_envelope(before, dp)
    if not dp_replay["pass"] or not envelope["pass"]:
        raise AssertionError(("R45A_DP_OR_ENVELOPE_FAIL", var, dp_replay, envelope))
    forced = r33.canonical_formula(dp["transformed"])
    normalization = normalize_after_dp(forced)
    final_formula = r33.canonical_formula(normalization["final_formula"])
    sat_reconstruction = reconstruct_macro_sat(before, dp, normalization)
    if not sat_reconstruction["pass"]:
        raise AssertionError(("R45A_SAT_RECONSTRUCTION_FAIL", var))
    accepted = normalization["terminal"] is not None or clv(final_formula) < clv(before)
    terminal_priority = 0 if normalization["terminal"] is not None else 1
    record = {
        "var": int(var),
        "input_formula_hash": r42.formula_hash(before),
        "input_CLV": list(clv(before)),
        "DP": dp,
        "DP_independent_replay": dp_replay,
        "polynomial_intermediate_envelope": envelope,
        "normalization": normalization,
        "SAT_reconstruction": sat_reconstruction,
        "temporary_internal_ascent": clv(forced) > clv(before),
        "immediate_DP_CLV_descent": clv(forced) < clv(before),
        "final_CLV": list(clv(final_formula)),
        "net_CLV_descent": clv(final_formula) < clv(before),
        "semantic_terminal_verified": normalization["terminal"] is not None,
        "accepted": accepted,
        "selection_key": [terminal_priority, list(clv(final_formula)), int(var)],
    }
    record["macro_certificate_bytes"] = json_bytes(record)
    return record


def independent_macro_replay(before_formula: Formula, claimed: dict) -> dict:
    before = r33.canonical_formula(before_formula)
    var = int(claimed["var"])
    recomputed = macro_candidate_for_var(before, var)
    if recomputed is None:
        return {"pass": False, "reason": "VARIABLE_NO_LONGER_HAS_BOTH_POLARITIES"}
    fields = {
        "input_hash_ok": claimed["input_formula_hash"] == r42.formula_hash(before),
        "dp_replay_pass": independent_dp_replay(before, claimed["DP"])["pass"],
        "var_ok": int(recomputed["var"]) == var,
        "final_hash_ok": recomputed["normalization"]["final_formula_hash"] == claimed["normalization"]["final_formula_hash"],
        "terminal_ok": recomputed["normalization"]["terminal"] == claimed["normalization"]["terminal"],
        "semantic_sat_ok": recomputed["normalization"]["semantic_sat"] == claimed["normalization"]["semantic_sat"],
        "net_descent_ok": recomputed["net_CLV_descent"] == claimed["net_CLV_descent"],
        "accepted_ok": recomputed["accepted"] == claimed["accepted"],
        "sat_reconstruction_ok": recomputed["SAT_reconstruction"]["pass"],
        "envelope_ok": recomputed["polynomial_intermediate_envelope"]["pass"],
    }
    return {"pass": all(fields.values()), **fields}


def select_macro(before_formula: Formula) -> dict:
    before = r33.canonical_formula(before_formula)
    C, _, V = clv(before)
    rows = []
    aggregate = {
        "variables_checked": 0,
        "variables_with_both_polarities": 0,
        "resolution_pair_checks": 0,
        "generated_resolvent_literals": 0,
        "subsumption_pair_checks_upper": 0,
        "R33_check_operation_upper_ledger": 0,
        "R33_certificate_bytes": 0,
        "RUP_checks": 0,
        "RUP_UP_clause_scans": 0,
        "RUP_UP_literal_inspections": 0,
        "GF2_estimated_bit_ops": 0,
        "terminal_Horn_clause_scans": 0,
        "terminal_2SAT_scc_calls": 0,
        "certificate_bytes": 0,
        "peak_intermediate_clauses": C,
        "peak_intermediate_literals": sum(len(c) for c in before),
    }
    for var in r33.variables(before):
        aggregate["variables_checked"] += 1
        row = macro_candidate_for_var(before, int(var))
        if row is None:
            continue
        aggregate["variables_with_both_polarities"] += 1
        dp = row["DP"]
        aggregate["resolution_pair_checks"] += int(dp["resolution_pair_checks"])
        aggregate["generated_resolvent_literals"] += int(dp["generated_resolvent_literals"])
        aggregate["subsumption_pair_checks_upper"] += int(dp["subsumption_pair_checks_upper"])
        aggregate["certificate_bytes"] += int(row["macro_certificate_bytes"])
        aggregate["peak_intermediate_clauses"] = max(aggregate["peak_intermediate_clauses"], int(dp["peak_intermediate_clauses"]))
        aggregate["peak_intermediate_literals"] = max(aggregate["peak_intermediate_literals"], int(dp["peak_intermediate_literals"]))
        for key, value in row["normalization"]["ledger"].items():
            aggregate[key] += int(value)
        rows.append(row)

    acceptable = [r for r in rows if r["accepted"]]
    acceptable.sort(key=lambda r: (r["selection_key"][0], tuple(r["selection_key"][1]), r["selection_key"][2]))
    selected = acceptable[0] if acceptable else None
    selected_replay = independent_macro_replay(before, selected) if selected is not None else None
    if selected_replay is not None and not selected_replay["pass"]:
        raise AssertionError(("R45A_SELECTED_MACRO_REPLAY_FAIL", selected_replay))

    global_bounds = {
        "all_variable_resolution_pair_checks_bound": V * (((C * C) // 4) + 1),
        "all_variable_scan_is_at_most_V": aggregate["variables_checked"] <= V,
        "resolution_pair_checks_within_polynomial_scan_bound": aggregate["resolution_pair_checks"] <= V * (((C * C) // 4) + 1),
    }
    global_bounds["pass"] = all(v for k, v in global_bounds.items() if k != "all_variable_resolution_pair_checks_bound")
    return {
        "input_formula_hash": r42.formula_hash(before),
        "input_CLV": list(clv(before)),
        "candidate_count": len(rows),
        "acceptable_candidate_count": len(acceptable),
        "selected": selected,
        "selected_independent_replay": selected_replay,
        "resource_ledger": aggregate,
        "global_polynomial_scan_bounds": global_bounds,
        "candidate_digest_sha256": canonical_sha256([
            {
                "var": r["var"],
                "accepted": r["accepted"],
                "terminal": r["normalization"]["terminal"],
                "final_CLV": r["final_CLV"],
                "certificate_sha256": canonical_sha256(r),
            }
            for r in rows
        ]),
    }


def exposed_43004_regression() -> dict:
    replay = r44.replay_to_r42_stall()
    stall = r33.canonical_formula(replay["formula"])
    if r42.formula_hash(stall) != EXPOSED_43004_STALL_HASH:
        raise AssertionError("R45A_43004_STALL_HASH_DRIFT")
    scan = select_macro(stall)
    selected = scan["selected"]
    return {
        "stall_hash": r42.formula_hash(stall),
        "stall_CLV": list(clv(stall)),
        "candidate_count": scan["candidate_count"],
        "acceptable_candidate_count": scan["acceptable_candidate_count"],
        "selected_var": selected["var"] if selected else None,
        "selected_terminal": selected["normalization"]["terminal"] if selected else None,
        "selected_final_CLV": selected["final_CLV"] if selected else None,
        "selected_temporary_internal_ascent": selected["temporary_internal_ascent"] if selected else None,
        "selected_replay_pass": bool(scan["selected_independent_replay"] and scan["selected_independent_replay"]["pass"]),
        "scan": scan,
        "pass": selected is not None and bool(scan["selected_independent_replay"] and scan["selected_independent_replay"]["pass"]),
    }


def fresh_unseen_suite() -> dict:
    rows = []
    uncovered_stalls = []
    for spec in FRESH_UNSEEN_SPECS:
        formula = r33.deterministic_random_3cnf(int(spec["seed"]), n=int(spec["n"]), ratio=float(spec["ratio"]))
        label = f"R45A_FRESH_{spec['seed']}_N{spec['n']}_R{spec['ratio']}"
        inherited = r42.run_fixed_successor(formula, label)
        row = {
            "spec": spec,
            "input_hash": r42.formula_hash(formula),
            "R42_terminal_status": inherited["terminal_status"],
            "R42_semantic_decided": inherited["semantic_decided"],
            "R42_semantic_sat": inherited["semantic_sat"],
            "macro_probe": None,
        }
        if not inherited["semantic_decided"]:
            terminal_formula_hash = inherited["terminal_formula_hash"]
            # Reproduce the terminal state by following the deterministic controller cycles.
            state = formula
            for _ in range(inherited["cycle_count"] + 2):
                before = state
                reduced = r33.simplify(before)
                after_r33 = r33.canonical_formula(reduced["final_formula"])
                if reduced["terminal"] != "STALLED_STACK_LEAN_CORE":
                    break
                affine = r34.recognize_complete_affine_cnf(after_r33)
                if affine["recognized"]:
                    break
                rup = r35b.run_candidate(after_r33)
                if rup["status"] == "UNSAT_BY_UNIT_PROPAGATION":
                    break
                after_rup = r33.canonical_formula(rup["final_formula"])
                bve, _ = r42.best_sa_bve_candidate(after_rup)
                after_bve = r33.canonical_formula(bve["transformed"]) if bve is not None else after_rup
                if after_bve == before:
                    state = after_bve
                    break
                state = after_bve
            if r42.formula_hash(state) != terminal_formula_hash:
                raise AssertionError(("R45A_FRESH_STALL_REPLAY_HASH_DRIFT", spec, r42.formula_hash(state), terminal_formula_hash))
            scan = select_macro(state)
            selected = scan["selected"]
            row["macro_probe"] = {
                "stall_hash": terminal_formula_hash,
                "stall_CLV": list(clv(state)),
                "candidate_count": scan["candidate_count"],
                "acceptable_candidate_count": scan["acceptable_candidate_count"],
                "selected_var": selected["var"] if selected else None,
                "selected_terminal": selected["normalization"]["terminal"] if selected else None,
                "selected_final_CLV": selected["final_CLV"] if selected else None,
                "selected_replay_pass": bool(scan["selected_independent_replay"] and scan["selected_independent_replay"]["pass"]),
                "resource_ledger": scan["resource_ledger"],
                "global_polynomial_scan_bounds": scan["global_polynomial_scan_bounds"],
            }
            if selected is None:
                uncovered_stalls.append(int(spec["seed"]))
        rows.append(row)
    return {
        "specs": list(FRESH_UNSEEN_SPECS),
        "rows": rows,
        "fresh_case_count": len(rows),
        "fresh_R42_stall_count": sum(1 for r in rows if not r["R42_semantic_decided"]),
        "uncovered_stall_seeds": uncovered_stalls,
        "candidate_survives_fresh_suite": not uncovered_stalls,
        "rows_sha256": canonical_sha256(rows),
    }


def run_r45a() -> dict:
    exposed = exposed_43004_regression()
    fresh = fresh_unseen_suite()
    implementation_sound = exposed["pass"] and all(
        r["macro_probe"] is None or r["macro_probe"]["selected_replay_pass"]
        for r in fresh["rows"]
    )
    candidate_survives = implementation_sound and fresh["candidate_survives_fresh_suite"]
    verdict = (
        "R45A_BYTE_PINNED_MACRO_IMPLEMENTED__FRESH_SUITE_SURVIVED__UNIVERSAL_COVERAGE_OPEN"
        if candidate_survives
        else "R45A_MACRO_CANDIDATE_REFUTED_BY_FRESH_STALL"
    )
    return {
        "schema": "JANUS_TRUMP_R45A_BYTE_PINNED_ASCENT_DESCENT_MACRO_RESULT",
        "version": "1.0",
        "date": "2026-09-02",
        "source_git_commit": os.environ.get("GITHUB_SHA", "LOCAL_UNCOMMITTED"),
        "lineage": {
            "R45_prereg_commit": R45_PREREG_COMMIT,
            "R44_sealed_forensics_commit": R44_SEALED_FORENSICS_COMMIT,
            "macro_id": "EXACT_DP_NORMALIZE_NET_DESCENT_MACRO_v1",
        },
        "exposed_43004_regression": exposed,
        "fresh_unseen_suite": fresh,
        "status": {
            "MACRO_IMPLEMENTATION_SOUND_ON_EXECUTED_CASES": implementation_sound,
            "LOCAL_POLYNOMIAL_INTERMEDIATE_ENVELOPE_CHECKED": True,
            "EXPOSED_43004_MACRO_ESCAPE_CERTIFIED": exposed["pass"],
            "FRESH_SUITE_CANDIDATE_SURVIVES": fresh["candidate_survives_fresh_suite"],
            "UNIVERSAL_STALL_COVERAGE_PROVEN": False,
            "FULL_ALGORITHM_POLYNOMIALITY_PROVEN": False,
        },
        "claim_ceiling": {
            "R42_remains_refuted": True,
            "L2_UNIVERSAL_3CNF_COVERAGE": False,
            "L3_ONE_UNIFORM_TOTAL_TRUMP_RESOLVER": False,
            "L4_WORST_CASE_POLYNOMIAL_UNIFORM_TRUMP_RESOLVER": False,
            "SAT_IN_P": "NOT_PROVED",
            "P_VS_NP": "OPEN",
        },
        "next_gate": (
            "R45B_FROZEN_26_STALL_QUOTIENT_MACRO_COVERAGE_AUDIT"
            if candidate_survives
            else "RETURN_TO_CAPTAIN_WITH_FRESH_UNCOVERED_STALL"
        ),
        "verdict": verdict,
        "TRUMP_finished": False,
        "SAT_IN_P": "NOT_PROVED",
        "P_VS_NP": "OPEN",
        "runtime_authority": False,
    }


def self_test() -> None:
    sat_formula = r33.canonical_formula([(1, 2), (-1, 2)])
    sat = macro_candidate_for_var(sat_formula, 1)
    assert sat is not None
    assert sat["DP_independent_replay"]["pass"]
    assert sat["polynomial_intermediate_envelope"]["pass"]
    assert sat["SAT_reconstruction"]["pass"]

    unsat_formula = r33.canonical_formula([(1, 2), (1, -2), (-1, 2), (-1, -2)])
    unsat = macro_candidate_for_var(unsat_formula, 1)
    assert unsat is not None
    assert unsat["DP_independent_replay"]["pass"]
    assert unsat["semantic_terminal_verified"]
    assert unsat["normalization"]["semantic_sat"] is False

    tampered = json.loads(json.dumps(sat["DP"]))
    tampered["full_non_tautological_resolvents"] = []
    assert independent_dp_replay(sat_formula, tampered)["pass"] is False
    print("R45A_SELF_TEST_PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    result = run_r45a()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "verdict": result["verdict"],
        "status": result["status"],
        "43004_selected_var": result["exposed_43004_regression"]["selected_var"],
        "fresh_stalls": result["fresh_unseen_suite"]["fresh_R42_stall_count"],
        "fresh_uncovered": result["fresh_unseen_suite"]["uncovered_stall_seeds"],
        "next_gate": result["next_gate"],
        "P_VS_NP": result["P_VS_NP"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
