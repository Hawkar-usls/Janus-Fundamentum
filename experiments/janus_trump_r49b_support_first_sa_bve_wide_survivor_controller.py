from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r47m_post_dp_full_existing_stack_closure as r47m
import janus_trump_r48z_pivot10_survivor_sa_bve_causal_forensics as r48z

GATE = "JANUS_TRUMP_R49B_SUPPORT_FIRST_SA_BVE_WIDE_SURVIVOR_CONTROLLER"
SURVIVOR = tuple(r48z.SURVIVOR)
LEGACY_BVE_COUNT = 8
LEGACY_REMOVAL_OUTER = 6
EXPECTED_FIRST_SUPPORT_OUTER = 2
EXPECTED_FIRST_SUPPORT_VAR = 20
WIDTH_CAP = 4


def canon(f):
    return r33.canonical_formula(f)


def clv(f):
    return r33.measure(canon(f))


def fhash(f):
    return r48z.fhash(canon(f))


def maxw(f):
    x = canon(f)
    return max((len(c) for c in x), default=0)


def wide_clauses(f):
    return [tuple(c) for c in canon(f) if len(c) > WIDTH_CAP]


def wide_support(f):
    return sorted({abs(int(l)) for c in wide_clauses(f) for l in c})


def support_candidates(formula, support):
    candidates = []
    ledger = {"variables_checked": 0, "resolution_pair_checks": 0, "subsumption_pair_upper_ledger": 0}
    vars_present = set(r33.variables(formula))
    for var in sorted(int(v) for v in support if int(v) in vars_present):
        ledger["variables_checked"] += 1
        _, _, _, pair_checks = r47m.r42.all_dp_resolvents(formula, var)
        ledger["resolution_pair_checks"] += int(pair_checks)
        c = r47m.r42.sa_bve_candidate_for_var(formula, var)
        if c is not None:
            ledger["subsumption_pair_upper_ledger"] += int(c["subsumption_pair_upper_ledger"])
            candidates.append(c)
    candidates.sort(key=lambda x: (tuple(x["measure_after"]), int(x["var"])))
    return candidates, ledger


def select_bve(formula):
    formula = canon(formula)
    wides = wide_clauses(formula)
    support = wide_support(formula)
    if wides:
        candidates, ledger = support_candidates(formula, support)
        if candidates:
            return candidates[0], {
                "mode": "SUPPORT_FIRST",
                "wide_clause_count": len(wides),
                "wide_clauses": [list(c) for c in wides],
                "wide_support": support,
                "support_eligible_vars": [int(c["var"]) for c in candidates],
                **ledger,
            }
    best, ledger = r47m.r42.best_sa_bve_candidate(formula)
    return best, {
        "mode": "GLOBAL_FALLBACK" if wides else "GLOBAL_WIDTH_LE_4",
        "wide_clause_count": len(wides),
        "wide_clauses": [list(c) for c in wides],
        "wide_support": support,
        "support_eligible_vars": [],
        **ledger,
    }


def support_first_normalize(transformed_formula):
    forced = canon(transformed_formula)
    state = forced
    bound = r47m.outer_height_bound(forced)
    segments = []
    reconstruction_events = []
    bve_sequence = []
    terminal = None
    semantic_sat = None
    terminal_assignment = None
    terminal_verification = None
    survivor_removal_outer = None
    survivor_removal_var = None
    first_support_outer = None
    first_support_var = None
    total_rup_checks = 0
    total_candidate_var_checks = 0
    total_resolution_pair_checks = 0
    total_subsumption_upper = 0
    max_segment_width = maxw(forced)

    for outer in range(bound + 1):
        before = canon(state)
        before_clv = clv(before)
        norm = r47j.normalize_to_certified_fixpoint(before)
        after_norm = canon(norm["final_formula"])
        after_norm_clv = clv(after_norm)
        if after_norm != before and not after_norm_clv < before_clv:
            raise AssertionError(("R49B_R47J_NOT_STRICT_DESCENT", outer, before_clv, after_norm_clv))
        for rr in norm["R33_reconstruction_results"]:
            reconstruction_events.append({"kind": "R33", "result": rr})
        total_rup_checks += int(norm["ledger"]["RUP_checks"])
        max_segment_width = max(max_segment_width, maxw(after_norm))
        survivor_before = SURVIVOR in after_norm
        row = {
            "outer": int(outer),
            "before_hash": fhash(before),
            "before_CLV": list(before_clv),
            "after_R47J_hash": fhash(after_norm),
            "after_R47J_CLV": list(after_norm_clv),
            "after_R47J_width": maxw(after_norm),
            "R47J_round_count": int(norm["round_count"]),
            "R47J_restart_count": int(norm["restart_count"]),
            "R47J_RUP_checks": int(norm["ledger"]["RUP_checks"]),
            "R47J_terminal": norm["terminal"],
            "survivor_present_after_R47J": bool(survivor_before),
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

        bve, selection = select_bve(after_norm)
        total_candidate_var_checks += int(selection["variables_checked"])
        total_resolution_pair_checks += int(selection["resolution_pair_checks"])
        total_subsumption_upper += int(selection["subsumption_pair_upper_ledger"])
        row["selection"] = selection
        if bve is None:
            row["SA_BVE_applied"] = False
            row["stop"] = "CERTIFIED_SUPPORT_FIRST_FULL_STACK_FIXPOINT"
            segments.append(row)
            state = after_norm
            break

        if selection["mode"] == "SUPPORT_FIRST" and first_support_outer is None:
            first_support_outer = int(outer)
            first_support_var = int(bve["var"])

        replay = r47m.r42.independent_sa_bve_replay(after_norm, bve)
        if not replay["pass"]:
            raise AssertionError(("R49B_SA_BVE_REPLAY_FAIL", outer, bve["var"], replay))
        after_bve = canon(bve["transformed"])
        after_bve_clv = clv(after_bve)
        if not after_bve_clv < after_norm_clv:
            raise AssertionError(("R49B_BVE_NOT_STRICT_DESCENT", outer, after_norm_clv, after_bve_clv))
        if not after_bve_clv < before_clv:
            raise AssertionError(("R49B_OUTER_NOT_STRICT_DESCENT", outer, before_clv, after_bve_clv))
        survivor_after = SURVIVOR in after_bve
        if survivor_before and not survivor_after and survivor_removal_outer is None:
            survivor_removal_outer = int(outer)
            survivor_removal_var = int(bve["var"])
        reconstruction_events.append({"kind": "SA_BVE", "record": bve})
        bve_sequence.append(int(bve["var"]))
        max_segment_width = max(max_segment_width, maxw(after_bve))
        row.update({
            "SA_BVE_applied": True,
            "SA_BVE_var": int(bve["var"]),
            "SA_BVE_before_CLV": list(bve["measure_before"]),
            "SA_BVE_after_CLV": list(bve["measure_after"]),
            "SA_BVE_replay_pass": True,
            "survivor_present_after_SA_BVE": bool(survivor_after),
            "after_SA_BVE_hash": fhash(after_bve),
            "after_SA_BVE_width": maxw(after_bve),
            "restart": True,
        })
        segments.append(row)
        state = after_bve
    else:
        raise AssertionError(("R49B_HEIGHT_BOUND_EXHAUSTED", bound))

    return {
        "forced_formula_hash": fhash(forced),
        "forced_CLV": list(clv(forced)),
        "segments": segments,
        "segment_count": len(segments),
        "SA_BVE_application_count": len(bve_sequence),
        "SA_BVE_sequence": bve_sequence,
        "terminal": terminal,
        "semantic_sat": semantic_sat,
        "terminal_assignment": terminal_assignment,
        "terminal_verification": terminal_verification,
        "final_formula": [list(c) for c in state],
        "final_formula_hash": fhash(state),
        "final_CLV": list(clv(state)),
        "reconstruction_events": reconstruction_events,
        "survivor_removal_outer": survivor_removal_outer,
        "survivor_removal_var": survivor_removal_var,
        "first_support_outer": first_support_outer,
        "first_support_var": first_support_var,
        "max_segment_width": int(max_segment_width),
        "ledger": {
            "RUP_checks": int(total_rup_checks),
            "candidate_variable_checks": int(total_candidate_var_checks),
            "resolution_pair_checks": int(total_resolution_pair_checks),
            "subsumption_pair_upper_ledger": int(total_subsumption_upper),
        },
    }


def exact_replay(forced, claimed):
    recomputed = support_first_normalize(forced)
    fields = {
        "final_hash_ok": recomputed["final_formula_hash"] == claimed["final_formula_hash"],
        "final_CLV_ok": recomputed["final_CLV"] == claimed["final_CLV"],
        "terminal_ok": recomputed["terminal"] == claimed["terminal"],
        "semantic_sat_ok": recomputed["semantic_sat"] == claimed["semantic_sat"],
        "BVE_sequence_ok": recomputed["SA_BVE_sequence"] == claimed["SA_BVE_sequence"],
        "segments_ok": recomputed["segments"] == claimed["segments"],
        "removal_ok": (recomputed["survivor_removal_outer"], recomputed["survivor_removal_var"]) == (claimed["survivor_removal_outer"], claimed["survivor_removal_var"]),
    }
    return {"pass": all(fields.values()), **fields}


def polarity(terminal, semantic_sat):
    if terminal is None:
        return None
    if semantic_sat is True:
        return "SAT"
    if semantic_sat is False:
        return "UNSAT"
    return "UNKNOWN"


def run():
    _, predecessor, _ = r48z.reconstruct_predecessor()
    legacy = r47m.macro_candidate_full_closure(predecessor, r48z.PIVOT)
    if legacy is None:
        raise AssertionError("R49B_LEGACY_PIVOT10_MISSING")
    legacy_replay = r47m.independent_replay(predecessor, legacy)
    if not legacy_replay["pass"]:
        raise AssertionError(("R49B_LEGACY_REPLAY_FAIL", legacy_replay))
    if legacy["normalization"]["terminal"] != "DIRECT_EMPTY_CNF" or legacy["normalization"]["semantic_sat"] is not True:
        raise AssertionError(("R49B_LEGACY_TERMINAL_DRIFT", legacy["normalization"]["terminal"], legacy["normalization"]["semantic_sat"]))
    if int(legacy["normalization"]["SA_BVE_application_count"]) != LEGACY_BVE_COUNT:
        raise AssertionError(("R49B_LEGACY_BVE_COUNT_DRIFT", legacy["normalization"]["SA_BVE_application_count"]))

    forced = canon(legacy["DP"]["transformed"])
    optimized = support_first_normalize(forced)
    replay = exact_replay(forced, optimized)
    if not replay["pass"]:
        raise AssertionError(("R49B_OPTIMIZED_EXACT_REPLAY_FAIL", replay))

    if optimized["first_support_outer"] != EXPECTED_FIRST_SUPPORT_OUTER or optimized["first_support_var"] != EXPECTED_FIRST_SUPPORT_VAR:
        raise AssertionError(("R49B_R49A_SUPPORT_BIRTH_DRIFT", optimized["first_support_outer"], optimized["first_support_var"]))

    sat_reconstruction = r47m.reconstruct_sat(predecessor, legacy["DP"], optimized)
    if optimized["semantic_sat"] is True and not sat_reconstruction["pass"]:
        raise AssertionError(("R49B_SAT_RECONSTRUCTION_FAIL", sat_reconstruction))

    legacy_polarity = polarity(legacy["normalization"]["terminal"], legacy["normalization"]["semantic_sat"])
    optimized_polarity = polarity(optimized["terminal"], optimized["semantic_sat"])
    removed_earlier = optimized["survivor_removal_outer"] is not None and optimized["survivor_removal_outer"] < LEGACY_REMOVAL_OUTER

    if optimized["terminal"] is not None and optimized_polarity != legacy_polarity:
        verdict = "SUPPORT_FIRST_TERMINAL_POLARITY_MISMATCH"
    elif removed_earlier and optimized["terminal"] == legacy["normalization"]["terminal"] and optimized_polarity == legacy_polarity:
        verdict = "SUPPORT_FIRST_REMOVES_WIDE_SURVIVOR_EARLIER_AND_REACHES_SAME_TERMINAL"
    elif removed_earlier and optimized["terminal"] is not None and optimized_polarity == legacy_polarity:
        verdict = "SUPPORT_FIRST_REMOVES_SURVIVOR_EARLIER_BUT_REACHES_DIFFERENT_CERTIFIED_SAME_POLARITY_TERMINAL"
    elif removed_earlier and optimized["terminal"] is None:
        verdict = "SUPPORT_FIRST_REMOVES_SURVIVOR_BUT_LATER_STALLS_NONTERMINAL"
    else:
        verdict = "SUPPORT_FIRST_DOES_NOT_REMOVE_SURVIVOR_EARLIER"

    legacy_rup_checks = 0
    legacy_candidate_checks = 0
    legacy_resolution_checks = 0
    for seg in legacy["normalization"]["segments"]:
        legacy_candidate_checks += int(seg.get("SA_BVE_variables_checked", 0))
        legacy_resolution_checks += int(seg.get("SA_BVE_resolution_pair_checks", 0))
    # Deterministically reconstruct legacy R47J ledgers over the selected BVE sequence.
    state = forced
    for _ in range(LEGACY_BVE_COUNT + 1):
        norm = r47j.normalize_to_certified_fixpoint(state)
        legacy_rup_checks += int(norm["ledger"]["RUP_checks"])
        after_norm = canon(norm["final_formula"])
        if norm["terminal"] is not None:
            break
        bve, _ = r47m.r42.best_sa_bve_candidate(after_norm)
        if bve is None:
            break
        state = canon(bve["transformed"])

    return {
        "gate": GATE,
        "verdict": verdict,
        "legacy": {
            "terminal": legacy["normalization"]["terminal"],
            "semantic_sat": legacy["normalization"]["semantic_sat"],
            "polarity": legacy_polarity,
            "final_hash": legacy["normalization"]["final_formula_hash"],
            "final_CLV": legacy["normalization"]["final_CLV"],
            "SA_BVE_application_count": int(legacy["normalization"]["SA_BVE_application_count"]),
            "survivor_removal_outer": LEGACY_REMOVAL_OUTER,
            "SA_BVE_sequence": [26, 12, 14, 30, 23, 29, 27, 18],
            "RUP_checks": int(legacy_rup_checks),
            "candidate_variable_checks": int(legacy_candidate_checks),
            "resolution_pair_checks": int(legacy_resolution_checks),
            "independent_replay_pass": True,
        },
        "support_first": {
            **optimized,
            "polarity": optimized_polarity,
            "exact_independent_replay_pass": True,
            "SAT_predecessor_reconstruction": sat_reconstruction,
        },
        "comparison": {
            "survivor_removed_earlier": bool(removed_earlier),
            "removal_outer_delta": None if optimized["survivor_removal_outer"] is None else int(optimized["survivor_removal_outer"] - LEGACY_REMOVAL_OUTER),
            "BVE_count_delta": int(optimized["SA_BVE_application_count"] - LEGACY_BVE_COUNT),
            "same_terminal_kind": optimized["terminal"] == legacy["normalization"]["terminal"],
            "same_terminal_polarity": optimized_polarity == legacy_polarity,
            "same_final_hash": optimized["final_formula_hash"] == legacy["normalization"]["final_formula_hash"],
            "RUP_check_delta": int(optimized["ledger"]["RUP_checks"] - legacy_rup_checks),
            "candidate_variable_check_delta": int(optimized["ledger"]["candidate_variable_checks"] - legacy_candidate_checks),
            "resolution_pair_check_delta": int(optimized["ledger"]["resolution_pair_checks"] - legacy_resolution_checks),
            "performance_is_diagnostic_only": True,
        },
        "interpretation": {
            "new_inference_rule_added": False,
            "proof_authority_changed": False,
            "single_witness_only": True,
            "universal_support_first_safety_proved": False,
            "universal_width4_coverage_proved": False,
        },
        "firewall": {
            "UNIVERSAL_SUPPORT_FIRST_SA_BVE_SAFETY": "NOT_PROVED",
            "UNIVERSAL_SURVIVOR_SUPPORT_SA_BVE_LAW": "NOT_PROVED",
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
    p = argparse.ArgumentParser()
    p.add_argument("--output")
    a = p.parse_args()
    d = run()
    if a.output:
        path = Path(a.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(d, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    s = d["support_first"]
    print(json.dumps({
        "gate": d["gate"],
        "verdict": d["verdict"],
        "legacy": d["legacy"],
        "support_first": {
            "terminal": s["terminal"],
            "semantic_sat": s["semantic_sat"],
            "polarity": s["polarity"],
            "final_hash": s["final_formula_hash"],
            "final_CLV": s["final_CLV"],
            "first_support_outer": s["first_support_outer"],
            "first_support_var": s["first_support_var"],
            "survivor_removal_outer": s["survivor_removal_outer"],
            "survivor_removal_var": s["survivor_removal_var"],
            "SA_BVE_application_count": s["SA_BVE_application_count"],
            "SA_BVE_sequence": s["SA_BVE_sequence"],
            "max_segment_width": s["max_segment_width"],
            "ledger": s["ledger"],
            "SAT_predecessor_reconstruction_pass": s["SAT_predecessor_reconstruction"]["pass"],
        },
        "comparison": d["comparison"],
        "firewall": d["firewall"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
