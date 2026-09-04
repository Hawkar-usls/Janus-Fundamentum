from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Optional

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r47m_post_dp_full_existing_stack_closure as r47m
import janus_trump_r48o_width4_first_certified_chain_falsifier as r48o
import janus_trump_r48x_wide_first_rup_width_discharge_controller as r48x

GATE = "JANUS_TRUMP_R48Y_WIDE_FIRST_PREPASS_R48O_PRODUCTION_REGRESSION"
WIDTH_CAP = 4
EXPECTED_ROOT = "3f05812b68eec1a2c16b099d5542dcc53fce66a0cb47679a1594134a0a553750"
EXPECTED_LEGACY_PATH = [2, 4, 5, 7, 9, 10]


def canon(f):
    return r33.canonical_formula(f)


def clv(f):
    return r33.measure(canon(f))


def fhash(f):
    return r48o.formula_hash(canon(f))


def maxw(f):
    x = canon(f)
    return max((len(c) for c in x), default=0)


def sat_polarity(terminal, semantic_sat):
    if terminal is None:
        return None
    if semantic_sat is True:
        return "SAT"
    if semantic_sat is False:
        return "UNSAT"
    return "UNKNOWN"


def optimized_r47j(transformed_formula):
    forced = canon(transformed_formula)
    state = forced
    height_bound = r47j.restart_height_bound(forced)
    rounds = []
    r33_reconstruction_results = []
    terminal = None
    semantic_sat: Optional[bool] = None
    terminal_assignment: Optional[Dict[int, bool]] = None
    terminal_verification = None
    ledger = {
        "R33_check_operation_upper_ledger": 0,
        "R33_certificate_bytes": 0,
        "WIDE_RUP_checks": 0,
        "WIDE_RUP_UP_clause_scans": 0,
        "WIDE_RUP_UP_literal_inspections": 0,
        "WIDE_RUP_successful_strengthenings": 0,
        "WIDE_RUP_invocations": 0,
        "WIDE_RUP_stalls": 0,
        "GENERAL_RUP_checks": 0,
        "GENERAL_RUP_UP_clause_scans": 0,
        "GENERAL_RUP_UP_literal_inspections": 0,
        "GENERAL_RUP_successful_strengthenings": 0,
        "GF2_estimated_bit_ops": 0,
        "restart_count": 0,
    }

    for round_index in range(height_bound + 1):
        before = state
        before_clv = clv(before)
        reduced = r33.simplify(before)
        after_r33 = canon(reduced["final_formula"])
        after_r33_clv = clv(after_r33)
        if after_r33 != before and not after_r33_clv < before_clv:
            raise AssertionError(("R48Y_R33_NOT_STRICT_DESCENT", round_index, before_clv, after_r33_clv))
        if reduced["history"]:
            r33_reconstruction_results.append(reduced)
        ledger["R33_check_operation_upper_ledger"] += int(reduced["total_check_operation_count_upper_ledger"])
        ledger["R33_certificate_bytes"] += int(reduced["total_certificate_bytes"])
        row = {
            "round": int(round_index),
            "before_hash": fhash(before),
            "before_CLV": list(before_clv),
            "before_width": maxw(before),
            "R33_apps": int(reduced["total_rule_applications"]),
            "after_R33_hash": fhash(after_r33),
            "after_R33_CLV": list(after_r33_clv),
            "after_R33_width": maxw(after_r33),
            "R33_terminal": reduced["terminal"],
        }
        if reduced["terminal"] != "STALLED_STACK_LEAN_CORE":
            solved = r47j.r42.solve_declared_terminal(after_r33, reduced["terminal"])
            if not solved["verification_pass"]:
                raise AssertionError(("R48Y_DECLARED_TERMINAL_VERIFY_FAIL", solved))
            terminal = solved["kind"]
            semantic_sat = bool(solved["sat"])
            terminal_assignment = solved.get("assignment")
            terminal_verification = solved
            row["stop"] = terminal
            rounds.append(row)
            state = after_r33
            break

        affine = r47j.r34.recognize_complete_affine_cnf(after_r33)
        row["affine_recognized"] = bool(affine["recognized"])
        if affine["recognized"]:
            solution = r47j.r34.solve_gf2_with_certificate(affine["equations"])
            verify = r47j.r34.verify_affine_certificate(after_r33, affine, solution)
            if not verify["pass"]:
                raise AssertionError(("R48Y_AFFINE_VERIFY_FAIL", verify))
            terminal = "AFFINE_XOR_SAT" if solution["sat"] else "AFFINE_XOR_UNSAT"
            semantic_sat = bool(solution["sat"])
            terminal_assignment = solution.get("assignment")
            terminal_verification = verify
            ledger["GF2_estimated_bit_ops"] += int(solution["estimated_bit_ops"])
            row["stop"] = terminal
            rounds.append(row)
            state = after_r33
            break

        pre_general = after_r33
        wide = None
        if maxw(after_r33) > WIDTH_CAP:
            wide = r48x.run_wide_first(after_r33, WIDTH_CAP)
            if not wide["resource_bound_pass"]:
                raise AssertionError(("R48Y_WIDE_RESOURCE_FAIL", round_index))
            if any(not h["independent_up_conflict_pass"] for h in wide["history"]):
                raise AssertionError(("R48Y_WIDE_REPLAY_FAIL", round_index))
            pre_general = canon(wide["final_formula"])
            ledger["WIDE_RUP_invocations"] += 1
            ledger["WIDE_RUP_checks"] += int(wide["ledger"]["rup_checks"])
            ledger["WIDE_RUP_UP_clause_scans"] += int(wide["ledger"]["up_clause_scans"])
            ledger["WIDE_RUP_UP_literal_inspections"] += int(wide["ledger"]["up_literal_inspections"])
            ledger["WIDE_RUP_successful_strengthenings"] += int(wide["successful_strengthenings"])
            if wide["status"] == "WIDE_RUP_STALL":
                ledger["WIDE_RUP_stalls"] += 1
            if pre_general != after_r33 and not clv(pre_general) < after_r33_clv:
                raise AssertionError(("R48Y_WIDE_NOT_DESCENT", round_index, after_r33_clv, clv(pre_general)))
            row["wide_first"] = {
                "status": wide["status"],
                "initial_E4": int(wide["initial_E4"]),
                "final_E4": int(wide["final_E4"]),
                "successful_strengthenings": int(wide["successful_strengthenings"]),
                "rup_checks": int(wide["ledger"]["rup_checks"]),
                "final_hash": fhash(pre_general),
                "final_CLV": list(clv(pre_general)),
                "final_width": maxw(pre_general),
                "surviving_wide_clauses": wide["surviving_wide_clauses"],
            }
        else:
            row["wide_first"] = {"status": "SKIPPED_WIDTH_LE_4", "rup_checks": 0, "successful_strengthenings": 0}

        rup = r47j.r35b.run_candidate(pre_general)
        rup_replay = r47j.r35b.independent_certificate_replay(pre_general, rup)
        if not rup_replay["pass"]:
            raise AssertionError(("R48Y_GENERAL_RUP_REPLAY_FAIL", round_index, rup_replay))
        after_rup = canon(rup["final_formula"])
        after_rup_clv = clv(after_rup)
        ledger["GENERAL_RUP_checks"] += int(rup["ledger"]["rup_checks"])
        ledger["GENERAL_RUP_UP_clause_scans"] += int(rup["ledger"]["up_clause_scans"])
        ledger["GENERAL_RUP_UP_literal_inspections"] += int(rup["ledger"]["literal_inspections"] if "literal_inspections" in rup["ledger"] else rup["ledger"]["up_literal_inspections"])
        ledger["GENERAL_RUP_successful_strengthenings"] += int(rup["successful_strengthenings"])
        row.update({
            "general_RUP_status": rup["status"],
            "general_RUP_history_count": len(rup.get("history", [])),
            "general_RUP_checks": int(rup["ledger"]["rup_checks"]),
            "general_RUP_replay_pass": True,
            "after_RUP_hash": fhash(after_rup),
            "after_RUP_CLV": list(after_rup_clv),
            "after_RUP_width": maxw(after_rup),
        })

        if rup["status"] == "UNSAT_BY_UNIT_PROPAGATION":
            terminal = "RUP_UNSAT"
            semantic_sat = False
            terminal_verification = rup_replay
            row["stop"] = terminal
            rounds.append(row)
            state = after_rup
            break

        if after_rup != after_r33:
            if not after_rup_clv < after_r33_clv:
                raise AssertionError(("R48Y_COMBINED_RUP_CHANGE_NOT_STRICT_DESCENT", round_index, after_r33_clv, after_rup_clv))
            if not after_rup_clv < before_clv:
                raise AssertionError(("R48Y_RESTART_STATE_NOT_STRICT_DESCENT", round_index, before_clv, after_rup_clv))
            ledger["restart_count"] += 1
            row["restart"] = True
            rounds.append(row)
            state = after_rup
            continue

        row["stop"] = "CERTIFIED_NORMALIZATION_FIXPOINT"
        rounds.append(row)
        state = after_rup
        break
    else:
        raise AssertionError(("R48Y_RESTART_HEIGHT_BOUND_EXHAUSTED", height_bound))

    return {
        "forced_formula_hash": fhash(forced),
        "forced_CLV": list(clv(forced)),
        "height_bound": int(height_bound),
        "rounds": rounds,
        "round_count": len(rounds),
        "restart_count": int(ledger["restart_count"]),
        "terminal": terminal,
        "semantic_sat": semantic_sat,
        "terminal_assignment": terminal_assignment,
        "terminal_verification": terminal_verification,
        "final_formula": [list(c) for c in state],
        "final_formula_hash": fhash(state),
        "final_CLV": list(clv(state)),
        "R33_reconstruction_results": r33_reconstruction_results,
        "ledger": ledger,
    }


def optimized_full(transformed_formula):
    forced = canon(transformed_formula)
    state = forced
    bound = r47m.outer_height_bound(forced)
    segments = []
    reconstruction_events = []
    total_sa_bve = 0
    terminal = None
    semantic_sat = None
    terminal_assignment = None
    terminal_verification = None
    total_ledger = {"WIDE_RUP_checks": 0, "GENERAL_RUP_checks": 0, "WIDE_RUP_successful_strengthenings": 0, "GENERAL_RUP_successful_strengthenings": 0}

    for outer_index in range(bound + 1):
        before = state
        before_clv = clv(before)
        norm = optimized_r47j(before)
        after_norm = canon(norm["final_formula"])
        if after_norm != before and not clv(after_norm) < before_clv:
            raise AssertionError(("R48Y_OPT_SEGMENT_NOT_DESCENT", outer_index, before_clv, clv(after_norm)))
        for rr in norm["R33_reconstruction_results"]:
            reconstruction_events.append({"kind": "R33", "result": rr})
        for k in total_ledger:
            total_ledger[k] += int(norm["ledger"][k])
        row = {
            "outer": int(outer_index),
            "before_CLV": list(before_clv),
            "optimized_R47J_final_CLV": list(clv(after_norm)),
            "optimized_R47J_round_count": int(norm["round_count"]),
            "optimized_R47J_restart_count": int(norm["restart_count"]),
            "optimized_R47J_terminal": norm["terminal"],
            "WIDE_RUP_checks": int(norm["ledger"]["WIDE_RUP_checks"]),
            "GENERAL_RUP_checks": int(norm["ledger"]["GENERAL_RUP_checks"]),
        }
        if norm["terminal"] is not None:
            terminal = norm["terminal"]
            semantic_sat = norm["semantic_sat"]
            terminal_assignment = norm["terminal_assignment"]
            terminal_verification = norm["terminal_verification"]
            row["stop"] = terminal
            segments.append(row)
            state = after_norm
            break

        bve, bve_ledger = r47m.r42.best_sa_bve_candidate(after_norm)
        row["SA_BVE_variables_checked"] = int(bve_ledger["variables_checked"])
        if bve is None:
            row["SA_BVE_applied"] = False
            row["stop"] = "CERTIFIED_FULL_EXISTING_STACK_FIXPOINT"
            segments.append(row)
            state = after_norm
            break
        bve_replay = r47m.r42.independent_sa_bve_replay(after_norm, bve)
        if not bve_replay["pass"]:
            raise AssertionError(("R48Y_SA_BVE_REPLAY_FAIL", outer_index, bve_replay))
        after_bve = canon(bve["transformed"])
        if not clv(after_bve) < clv(after_norm) or not clv(after_bve) < before_clv:
            raise AssertionError(("R48Y_SA_BVE_DESCENT_FAIL", outer_index))
        reconstruction_events.append({"kind": "SA_BVE", "record": bve})
        total_sa_bve += 1
        row.update({"SA_BVE_applied": True, "SA_BVE_var": int(bve["var"]), "SA_BVE_replay_pass": True, "restart": True})
        segments.append(row)
        state = after_bve
    else:
        raise AssertionError(("R48Y_OUTER_BOUND_EXHAUSTED", bound))

    return {
        "forced_formula_hash": fhash(forced),
        "forced_CLV": list(clv(forced)),
        "height_bound": int(bound),
        "segments": segments,
        "segment_count": len(segments),
        "SA_BVE_application_count": int(total_sa_bve),
        "terminal": terminal,
        "semantic_sat": semantic_sat,
        "terminal_assignment": terminal_assignment,
        "terminal_verification": terminal_verification,
        "final_formula": [list(c) for c in state],
        "final_formula_hash": fhash(state),
        "final_CLV": list(clv(state)),
        "reconstruction_events": reconstruction_events,
        "ledger": total_ledger,
    }


def optimized_candidate(before_formula, var):
    before = canon(before_formula)
    dp = r47m.r45a.exact_dp_record(before, int(var))
    if dp is None:
        return None
    dp_replay = r47m.r45a.independent_dp_replay(before, dp)
    envelope = r47m.r45a.polynomial_envelope(before, dp)
    if not dp_replay["pass"] or not envelope["pass"]:
        raise AssertionError(("R48Y_DP_ENVELOPE_FAIL", var, dp_replay, envelope))
    norm = optimized_full(dp["transformed"])
    final = canon(norm["final_formula"])
    sat_recon = r47m.reconstruct_sat(before, dp, norm)
    if not sat_recon["pass"]:
        raise AssertionError(("R48Y_SAT_RECON_FAIL", var))
    return {
        "var": int(var),
        "input_hash": fhash(before),
        "input_CLV": list(clv(before)),
        "DP": dp,
        "DP_independent_replay_pass": True,
        "polynomial_intermediate_envelope_pass": True,
        "normalization": norm,
        "SAT_reconstruction": sat_recon,
        "final_CLV": list(clv(final)),
        "accepted": bool(norm["terminal"] is not None or clv(final) < clv(before)),
    }


def optimized_replay(before_formula, claimed):
    c = optimized_candidate(before_formula, int(claimed["var"]))
    fields = {
        "exists": c is not None,
        "final_hash_ok": c is not None and c["normalization"]["final_formula_hash"] == claimed["normalization"]["final_formula_hash"],
        "final_CLV_ok": c is not None and c["final_CLV"] == claimed["final_CLV"],
        "terminal_ok": c is not None and c["normalization"]["terminal"] == claimed["normalization"]["terminal"],
        "segments_ok": c is not None and c["normalization"]["segments"] == claimed["normalization"]["segments"],
        "accepted_ok": c is not None and c["accepted"] == claimed["accepted"],
    }
    return {"pass": all(fields.values()), **fields}


def candidate_row(current, candidate, replay_pass):
    final = canon(candidate["normalization"]["final_formula"])
    before_vars = set(r33.variables(current))
    after_vars = set(r33.variables(final))
    terminal = candidate["normalization"]["terminal"]
    delta_v = len(before_vars) - len(after_vars)
    no_fresh = after_vars <= before_vars
    eligible = bool(terminal is not None or (delta_v >= 1 and no_fresh))
    return {
        "var": int(candidate["var"]),
        "final_hash": fhash(final),
        "final_CLV": list(clv(final)),
        "terminal": terminal,
        "semantic_sat": candidate["normalization"]["semantic_sat"],
        "delta_V_eliminated": int(delta_v),
        "no_fresh_variables": bool(no_fresh),
        "eligible": eligible,
        "final_max_width": maxw(final),
        "width4_safe": bool(terminal is not None or (eligible and maxw(final) <= WIDTH_CAP)),
        "independent_replay_pass": bool(replay_pass),
        "WIDE_RUP_checks": int(candidate["normalization"]["ledger"]["WIDE_RUP_checks"]),
        "GENERAL_RUP_checks": int(candidate["normalization"]["ledger"]["GENERAL_RUP_checks"]),
    }


def optimized_scan(current):
    rows = []
    candidates = {}
    for v in r33.variables(current):
        c = optimized_candidate(current, int(v))
        if c is None:
            rows.append({"var": int(v), "candidate": False, "eligible": False, "width4_safe": False})
            continue
        rep = optimized_replay(current, c)
        if not rep["pass"]:
            raise AssertionError(("R48Y_OPT_REPLAY_FAIL", v, rep))
        candidates[int(v)] = c
        rows.append(candidate_row(current, c, True))
    return rows, candidates


def legacy_path_regression(root):
    current = canon(root)
    rows = []
    legacy_total_checks = 0
    optimized_wide_checks = 0
    optimized_general_checks = 0
    all_safe = True
    exact_hash_matches = 0
    for step, var in enumerate(EXPECTED_LEGACY_PATH, 1):
        legacy = r47m.macro_candidate_full_closure(current, int(var))
        opt = optimized_candidate(current, int(var))
        if legacy is None or opt is None:
            return {"pass": False, "failure": {"step": step, "var": var, "kind": "CANDIDATE_MISSING"}, "rows": rows}
        lrep = r47m.independent_replay(current, legacy)
        orep = optimized_replay(current, opt)
        if not lrep["pass"] or not orep["pass"]:
            raise AssertionError(("R48Y_SELECTED_REPLAY_FAIL", step, var, lrep, orep))
        legacy_final = canon(legacy["normalization"]["final_formula"])
        opt_final = canon(opt["normalization"]["final_formula"])
        orow = candidate_row(current, opt, True)
        safe = bool(orow["width4_safe"])
        all_safe = all_safe and safe
        if fhash(legacy_final) == fhash(opt_final):
            exact_hash_matches += 1
        lt = legacy["normalization"]["terminal"]
        ot = opt["normalization"]["terminal"]
        if lt is not None and ot is not None:
            lp = sat_polarity(lt, legacy["normalization"]["semantic_sat"])
            op = sat_polarity(ot, opt["normalization"]["semantic_sat"])
            if lp != op:
                raise AssertionError(("R48Y_TERMINAL_POLARITY_MISMATCH", step, var, lp, op))
        # Re-run each legacy R47J segment only for its exact ledger; validate by final hash through the frozen candidate itself.
        forced = canon(legacy["DP"]["transformed"])
        state = forced
        lchecks = 0
        for seg in legacy["normalization"]["segments"]:
            norm = r47j.normalize_to_certified_fixpoint(state)
            lchecks += int(norm["ledger"]["RUP_checks"])
            after = canon(norm["final_formula"])
            if norm["terminal"] is not None:
                state = after
                break
            bve, _ = r47m.r42.best_sa_bve_candidate(after)
            if bve is None:
                state = after
                break
            brep = r47m.r42.independent_sa_bve_replay(after, bve)
            if not brep["pass"]:
                raise AssertionError(("R48Y_LEGACY_LEDGER_BVE_REPLAY_FAIL", step, var))
            state = canon(bve["transformed"])
        if fhash(state) != fhash(legacy_final):
            raise AssertionError(("R48Y_LEGACY_LEDGER_RECONSTRUCTION_DRIFT", step, var, fhash(state), fhash(legacy_final)))
        legacy_total_checks += lchecks
        optimized_wide_checks += int(opt["normalization"]["ledger"]["WIDE_RUP_checks"])
        optimized_general_checks += int(opt["normalization"]["ledger"]["GENERAL_RUP_checks"])
        rows.append({
            "step": int(step), "var": int(var),
            "legacy_final_hash": fhash(legacy_final), "optimized_final_hash": fhash(opt_final),
            "exact_final_hash_match": fhash(legacy_final) == fhash(opt_final),
            "legacy_final_CLV": list(clv(legacy_final)), "optimized_final_CLV": list(clv(opt_final)),
            "legacy_terminal": lt, "optimized_terminal": ot,
            "optimized_safe": safe, "optimized_final_width": maxw(opt_final),
            "legacy_RUP_checks": int(lchecks),
            "optimized_WIDE_RUP_checks": int(opt["normalization"]["ledger"]["WIDE_RUP_checks"]),
            "optimized_GENERAL_RUP_checks": int(opt["normalization"]["ledger"]["GENERAL_RUP_checks"]),
        })
        if lt is not None:
            break
        current = legacy_final
    return {
        "pass": bool(all_safe),
        "failure": None if all_safe else {"kind": "LEGACY_SELECTED_PIVOT_LOST_WIDTH4_SAFETY"},
        "rows": rows,
        "exact_hash_matches": int(exact_hash_matches),
        "legacy_total_RUP_checks": int(legacy_total_checks),
        "optimized_total_WIDE_RUP_checks": int(optimized_wide_checks),
        "optimized_total_GENERAL_RUP_checks": int(optimized_general_checks),
        "optimized_total_RUP_checks": int(optimized_wide_checks + optimized_general_checks),
    }


def optimized_chain(root):
    current = canon(root)
    V0 = clv(root)[2]
    selected = []
    total_probes = 0
    max_persisted_width = maxw(root)
    total_wide_checks = 0
    total_general_checks = 0
    selected_full = []
    for state_index in range(V0 + 1):
        if state_index >= V0:
            raise AssertionError(("R48Y_OPT_STEP_CAP_EXHAUSTED", clv(current)))
        if maxw(current) > WIDTH_CAP:
            raise AssertionError(("R48Y_OPT_PERSISTED_WIDTH_DRIFT", state_index, maxw(current)))
        rows, candidates = optimized_scan(current)
        total_probes += len(rows)
        if total_probes > V0 * V0:
            raise AssertionError(("R48Y_OPT_PROBE_CAP_EXCEEDED", total_probes, V0 * V0))
        safe = [r for r in rows if r.get("width4_safe", False)]
        if not safe:
            return {
                "verdict": "OPTIMIZED_WIDTH4_CHAIN_OBSTRUCTION_FOUND",
                "selected": selected,
                "obstruction": {"state_hash": fhash(current), "state_CLV": list(clv(current)), "state_width": maxw(current), "rows": rows},
                "terminal": None,
                "candidate_probe_count": total_probes,
                "max_persisted_width": max_persisted_width,
                "total_WIDE_RUP_checks": total_wide_checks,
                "total_GENERAL_RUP_checks": total_general_checks,
            }
        chosen_row = min(safe, key=lambda r: int(r["var"]))
        chosen = candidates[int(chosen_row["var"])]
        selected_full.append((current, chosen))
        total_wide_checks += int(chosen_row["WIDE_RUP_checks"])
        total_general_checks += int(chosen_row["GENERAL_RUP_checks"])
        selected.append({"step": len(selected)+1, "state_hash": fhash(current), "state_CLV": list(clv(current)), "state_width": maxw(current), **chosen_row})
        final = canon(chosen["normalization"]["final_formula"])
        if chosen_row["terminal"] is not None:
            sat_lift = r48o.r48g.lift_sat_root(root, selected_full, chosen)
            if not sat_lift["pass"]:
                raise AssertionError("R48Y_OPT_SAT_ROOT_LIFT_FAIL")
            return {
                "verdict": "OPTIMIZED_CHAIN_TERMINAL",
                "selected": selected,
                "obstruction": None,
                "terminal": {"kind": chosen_row["terminal"], "semantic_sat": chosen_row["semantic_sat"], "final_hash": fhash(final), "final_CLV": list(clv(final)), "SAT_root_reconstruction_pass": True},
                "candidate_probe_count": total_probes,
                "max_persisted_width": max(max_persisted_width, maxw(current)),
                "total_WIDE_RUP_checks": total_wide_checks,
                "total_GENERAL_RUP_checks": total_general_checks,
            }
        max_persisted_width = max(max_persisted_width, maxw(final))
        current = final
    raise AssertionError("R48Y_OPT_UNREACHABLE")


def run():
    _, _, root = r48o.reconstruct_root()
    root = canon(root)
    if fhash(root) != EXPECTED_ROOT or maxw(root) > WIDTH_CAP:
        raise AssertionError(("R48Y_ROOT_DRIFT", fhash(root), maxw(root)))
    legacy_sealed = r48o.run()
    if [int(x["var"]) for x in legacy_sealed["selected_path"]] != EXPECTED_LEGACY_PATH:
        raise AssertionError(("R48Y_LEGACY_PATH_DRIFT", [x["var"] for x in legacy_sealed["selected_path"]]))
    regression = legacy_path_regression(root)
    if not regression["pass"]:
        verdict = "OPTIMIZED_LEGACY_SELECTED_PIVOT_REGRESSION_FAILURE"
        opt_chain = None
    else:
        opt_chain = optimized_chain(root)
        if opt_chain["verdict"] == "OPTIMIZED_WIDTH4_CHAIN_OBSTRUCTION_FOUND":
            verdict = "OPTIMIZED_WIDTH4_CHAIN_OBSTRUCTION_FOUND"
        else:
            opt_pivots = [int(x["var"]) for x in opt_chain["selected"]]
            verdict = (
                "OPTIMIZED_WIDE_FIRST_R47M_PRESERVES_R48O_WIDTH4_CHAIN_AND_TERMINAL__FINITE_ONLY"
                if opt_pivots == EXPECTED_LEGACY_PATH
                else "OPTIMIZED_CHAIN_DIFFERS_BUT_REMAINS_CERTIFIED_WIDTH4_AND_TERMINAL__FINITE_ONLY"
            )
    return {
        "gate": GATE,
        "verdict": verdict,
        "root": {"hash": fhash(root), "CLV": list(clv(root)), "max_width": maxw(root)},
        "legacy_sealed": {"selected_pivots": EXPECTED_LEGACY_PATH, "terminal": legacy_sealed["terminal"], "candidate_probe_count": legacy_sealed["candidate_probe_count"]},
        "legacy_selected_pivot_regression": regression,
        "optimized_chain": opt_chain,
        "performance": None if not regression["pass"] else {
            "legacy_selected_path_RUP_checks": regression["legacy_total_RUP_checks"],
            "optimized_same_pivots_WIDE_RUP_checks": regression["optimized_total_WIDE_RUP_checks"],
            "optimized_same_pivots_GENERAL_RUP_checks": regression["optimized_total_GENERAL_RUP_checks"],
            "optimized_same_pivots_total_RUP_checks": regression["optimized_total_RUP_checks"],
            "check_ratio_legacy_over_optimized": None if regression["optimized_total_RUP_checks"] == 0 else regression["legacy_total_RUP_checks"] / regression["optimized_total_RUP_checks"],
            "diagnostic_only": True,
        },
        "interpretation": {
            "new_inference_rule_added": False,
            "proof_authority_changed": False,
            "byte_identical_fixpoint_required": False,
            "all_new_RUP_steps_independently_checked": True,
            "finite_R48O_regression_only": True,
            "universal_width4_proved": False,
        },
        "firewall": {
            "UNIVERSAL_WIDTH_RESET_LEMMA": "NOT_PROVED",
            "UNIVERSAL_WIDTH_4_COVERAGE": "NOT_PROVED",
            "UNIVERSAL_CONSTANT_WIDTH_COVERAGE": "NOT_PROVED",
            "O4_UNIVERSAL_COVERAGE": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_EQ_NP": "NOT_PROVED",
            "P_NE_NP": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }


def main():
    p = argparse.ArgumentParser(); p.add_argument("--output"); a = p.parse_args()
    d = run()
    if a.output:
        path = Path(a.output); path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(d, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "gate": d["gate"], "verdict": d["verdict"], "root": d["root"],
        "regression_pass": d["legacy_selected_pivot_regression"]["pass"],
        "legacy_exact_hash_matches": d["legacy_selected_pivot_regression"].get("exact_hash_matches"),
        "optimized_pivots": None if d["optimized_chain"] is None else [x["var"] for x in d["optimized_chain"]["selected"]],
        "optimized_terminal": None if d["optimized_chain"] is None else d["optimized_chain"]["terminal"],
        "performance": d["performance"], "firewall": d["firewall"]
    }, sort_keys=True))


if __name__ == "__main__":
    main()
