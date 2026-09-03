from __future__ import annotations

import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r35b_single_literal_rup_vivification as r35b
import janus_trump_r42_subsumption_aware_bve_successor as r42
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j

ROOT = Path(__file__).resolve().parents[1]
R47K_RESULT = ROOT / "research" / "JANUS_TRUMP_R47K_EXPLICIT_REACHABLE_COUNTEREXAMPLE_TO_EXTENDED_NORMALIZATION_CLOSURE_RESULT_2026-09-03.json"
EXPECTED_HASH = "9a84c02f1570e752ac0c017037b8a4a40c2599b53faf51bcd6d957f40aa81dde"
EXPECTED_CLV = (77, 206, 22)


def canon(xs):
    return r33.canonical_formula(xs)


def clv(f):
    return r33.measure(canon(f))


def clause_lists(fs):
    return [list(c) for c in sorted(canon(fs))]


def diff(a, b):
    A, B = set(canon(a)), set(canon(b))
    return {
        "removed": clause_lists(A - B),
        "added": clause_lists(B - A),
        "removed_count": len(A - B),
        "added_count": len(B - A),
    }


def load_f():
    d = json.loads(R47K_RESULT.read_text())
    f = canon(d["genuine_residual_fixpoint"]["formula"])
    if r42.formula_hash(f) != EXPECTED_HASH or clv(f) != EXPECTED_CLV:
        raise AssertionError(("R47T_SEALED_DRIFT", r42.formula_hash(f), clv(f)))
    return f


def parent_stats(dp):
    pos = canon(dp["positive"])
    neg = canon(dp["negative"])
    res = canon(dp["full_non_tautological_resolvents"])
    transformed = canon(dp["transformed"])
    return {
        "p": len(pos),
        "n": len(neg),
        "p_times_n": len(pos) * len(neg),
        "resolution_pair_checks": int(dp["resolution_pair_checks"]),
        "distinct_non_tautological_resolvents": len(res),
        "resolvent_literal_mass": sum(len(c) for c in res),
        "pool_clause_count_before_subsumption": int(dp["pool_clause_count_before_subsumption"]),
        "forced_DP_CLV": list(clv(transformed)),
        "positive_parents": clause_lists(pos),
        "negative_parents": clause_lists(neg),
        "resolvents": clause_lists(res),
    }


def occurrence_profile(formula, focus_vars):
    f = canon(formula)
    out = {}
    for v in sorted(set(int(x) for x in focus_vars)):
        pos = [c for c in f if v in c]
        neg = [c for c in f if -v in c]
        out[str(v)] = {"positive": len(pos), "negative": len(neg), "total": len(pos)+len(neg)}
    return out


def exact_rup_diff(formula):
    before = canon(formula)
    rup = r35b.run_candidate(before)
    replay = r35b.independent_certificate_replay(before, rup)
    if not replay["pass"]:
        raise AssertionError("R47T_RUP_REPLAY_FAIL")
    after = canon(rup["final_formula"])
    return {
        "status": rup["status"],
        "successful_strengthenings": int(rup["successful_strengthenings"]),
        "history_count": len(rup.get("history", [])),
        "before_CLV": list(clv(before)),
        "after_CLV": list(clv(after)),
        "clause_diff": diff(before, after),
        "history": rup.get("history", []),
        "independent_replay_pass": True,
        "final_formula": after,
    }


def normalization_forensics(input_formula, candidate):
    dp_formula = canon(candidate["DP"]["transformed"])
    state = dp_formula
    rounds = []
    for round_index in range(candidate["normalization"]["round_count"]):
        before = state
        reduced = r33.simplify(before)
        after_r33 = canon(reduced["final_formula"])
        row = {
            "round": round_index,
            "before_CLV": list(clv(before)),
            "R33_rule_counts": reduced["rule_counts"],
            "R33_history": reduced["history"],
            "after_R33_CLV": list(clv(after_r33)),
            "R33_clause_diff": diff(before, after_r33),
            "R33_terminal": reduced["terminal"],
        }
        if reduced["terminal"] != "STALLED_STACK_LEAN_CORE":
            rounds.append(row)
            state = after_r33
            break
        rupinfo = exact_rup_diff(after_r33)
        row["RUP_status"] = rupinfo["status"]
        row["RUP_successful_strengthenings"] = rupinfo["successful_strengthenings"]
        row["RUP_history_count"] = rupinfo["history_count"]
        row["RUP_history"] = rupinfo["history"]
        row["RUP_clause_diff"] = rupinfo["clause_diff"]
        row["after_RUP_CLV"] = rupinfo["after_CLV"]
        rounds.append(row)
        state = rupinfo["final_formula"]
        if state == after_r33:
            break
    claimed = canon(candidate["normalization"]["final_formula"])
    if state != claimed:
        raise AssertionError(("R47T_NORMALIZATION_REPLAY_DRIFT", clv(state), clv(claimed)))
    return {
        "input_CLV": list(clv(input_formula)),
        "forced_DP_CLV": candidate["DP"]["measure_after_forced_DP"],
        "rounds": rounds,
        "final_CLV": list(clv(state)),
        "final_formula": state,
        "total_clause_diff_from_forced_DP": diff(dp_formula, state),
    }


def run():
    F = load_f()
    c20_before = r47j.macro_candidate_fixpoint(F, 20)
    c11 = r47j.macro_candidate_fixpoint(F, 11)
    if c20_before is None or c11 is None:
        raise AssertionError("R47T_REQUIRED_CANDIDATE_MISSING")
    if c20_before["accepted"] or c11["accepted"]:
        raise AssertionError("R47T_DEPTH1_STATUS_DRIFT")
    r11 = r47j.independent_fixpoint_macro_replay(F, c11)
    r20b = r47j.independent_fixpoint_macro_replay(F, c20_before)
    if not r11["pass"] or not r20b["pass"]:
        raise AssertionError("R47T_DEPTH1_REPLAY_FAIL")

    G1 = canon(c11["normalization"]["final_formula"])
    if clv(G1) != (77,210,21):
        raise AssertionError(("R47T_G1_CLV_DRIFT", clv(G1)))
    c20_after = r47j.macro_candidate_fixpoint(G1, 20)
    if c20_after is None or not c20_after["accepted"]:
        raise AssertionError("R47T_UNLOCKED_V20_NO_LONGER_ACCEPTED")
    r20a = r47j.independent_fixpoint_macro_replay(G1, c20_after)
    if not r20a["pass"]:
        raise AssertionError("R47T_UNLOCKED_REPLAY_FAIL")
    G2 = canon(c20_after["normalization"]["final_formula"])
    if clv(G2) != (76,209,20):
        raise AssertionError(("R47T_G2_CLV_DRIFT", clv(G2)))

    s_before = parent_stats(c20_before["DP"])
    s_after = parent_stats(c20_after["DP"])
    n_before = normalization_forensics(F, c20_before)
    n_after = normalization_forensics(G1, c20_after)

    parent_before = canon(c20_before["DP"]["positive"] + c20_before["DP"]["negative"])
    parent_after = canon(c20_after["DP"]["positive"] + c20_after["DP"]["negative"])
    res_before = canon(c20_before["DP"]["full_non_tautological_resolvents"])
    res_after = canon(c20_after["DP"]["full_non_tautological_resolvents"])
    changed_vars = sorted({abs(l) for c in set(F).symmetric_difference(set(G1)) for l in c})

    # Identify the first strict clause-count drop unique to the successful post-v11 v20 path.
    successful_clause_drop_events = []
    for row in n_after["rounds"]:
        before_c = row["before_CLV"][0]
        r33_c = row["after_R33_CLV"][0]
        if r33_c < before_c:
            successful_clause_drop_events.append({
                "round": row["round"], "stage": "R33", "from_C": before_c, "to_C": r33_c,
                "rule_counts": row["R33_rule_counts"], "clause_diff": row["R33_clause_diff"],
            })
        if "after_RUP_CLV" in row and row["after_RUP_CLV"][0] < r33_c:
            successful_clause_drop_events.append({
                "round": row["round"], "stage": "RUP", "from_C": r33_c, "to_C": row["after_RUP_CLV"][0],
                "successful_strengthenings": row["RUP_successful_strengthenings"], "clause_diff": row["RUP_clause_diff"],
            })

    explanations = {
        "v11_reduces_v20_parent_pair_product": s_after["p_times_n"] < s_before["p_times_n"],
        "v11_reduces_v20_distinct_resolvent_count": s_after["distinct_non_tautological_resolvents"] < s_before["distinct_non_tautological_resolvents"],
        "v11_reduces_v20_forced_DP_clause_count": s_after["forced_DP_CLV"][0] < s_before["forced_DP_CLV"][0],
        "v11_creates_extra_post_v20_clause_drop": n_after["final_CLV"][0] < n_before["final_CLV"][0],
        "successful_path_has_explicit_clause_drop_event": bool(successful_clause_drop_events),
    }

    out = {
        "gate": "JANUS_TRUMP_R47T_DEPTH2_PIVOT_UNLOCKING_FORENSICS",
        "verdict": "FORMULA_LEVEL_UNLOCKING_MECHANISM_EXTRACTED__FINITE_WITNESS_ONLY",
        "sealed": {"F_hash": EXPECTED_HASH, "F_CLV": list(EXPECTED_CLV), "pair": [11,20]},
        "v11_layer": {
            "F_to_G1_CLV": [list(clv(F)), list(clv(G1))],
            "formula_diff": diff(F, G1),
            "changed_variable_occurrence_profile_F": occurrence_profile(F, changed_vars),
            "changed_variable_occurrence_profile_G1": occurrence_profile(G1, changed_vars),
            "changed_variables": changed_vars,
            "independent_replay_pass": True,
        },
        "v20_before_v11": {
            "DP": s_before,
            "normalization": {k:v for k,v in n_before.items() if k != "final_formula"},
            "accepted": bool(c20_before["accepted"]),
            "independent_replay_pass": True,
        },
        "v20_after_v11": {
            "DP": s_after,
            "normalization": {k:v for k,v in n_after.items() if k != "final_formula"},
            "accepted": bool(c20_after["accepted"]),
            "independent_replay_pass": True,
        },
        "v20_parent_set_diff": diff(parent_before, parent_after),
        "v20_resolvent_set_diff": diff(res_before, res_after),
        "delta": {
            "parent_pair_product": s_after["p_times_n"] - s_before["p_times_n"],
            "distinct_resolvents": s_after["distinct_non_tautological_resolvents"] - s_before["distinct_non_tautological_resolvents"],
            "forced_DP_clauses": s_after["forced_DP_CLV"][0] - s_before["forced_DP_CLV"][0],
            "forced_DP_literals": s_after["forced_DP_CLV"][1] - s_before["forced_DP_CLV"][1],
            "normalized_final_clauses": n_after["final_CLV"][0] - n_before["final_CLV"][0],
            "normalized_final_literals": n_after["final_CLV"][1] - n_before["final_CLV"][1],
        },
        "successful_clause_drop_events": successful_clause_drop_events,
        "candidate_explanations": explanations,
        "interpretation": {
            "finite_witness_only": True,
            "selector_promoted": False,
            "universal_unlocking_theorem": "NOT_PROVED",
        },
        "firewall": {
            "K_EQUALS_2": "NOT_PROVED",
            "O4_UNIVERSAL_COVERAGE": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }
    print(json.dumps(out, sort_keys=True))
    return out


if __name__ == "__main__":
    run()
