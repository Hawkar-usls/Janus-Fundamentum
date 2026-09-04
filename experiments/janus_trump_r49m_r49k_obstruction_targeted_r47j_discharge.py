from __future__ import annotations

import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r49i_bipolar_nontauto_cross_union_width5_core_hunt as r49i
import janus_trump_r49k_safe_only_width4_chain_52roots as r49k

GATE = "JANUS_TRUMP_R49M_R49K_OBSTRUCTION_TARGETED_R47J_DISCHARGE"
WIDTH_CAP = 4


def canon(f):
    return r33.canonical_formula(f)


def max_width(f):
    return max((len(c) for c in canon(f)), default=0)


def recreate_core():
    root, provenance = r49i.collect_roots()[0]
    rec = r49k.run_root(root, provenance, 1)
    if rec["covered"]:
        raise AssertionError("R49M_R49K_OBSTRUCTION_DISAPPEARED")
    pivots = [int(x["pivot"]) for x in rec["steps"]]
    if pivots != [2, 5, 11, 25]:
        raise AssertionError(("R49M_R49K_PATH_DRIFT", pivots))
    core = canon(rec["obstruction"]["formula"])
    if r49i.fhash(core) != rec["obstruction"]["state_hash"]:
        raise AssertionError("R49M_CORE_HASH_DRIFT")
    return root, rec, core


def candidate_row(core, var, profile):
    c = r47j.macro_candidate_fixpoint(core, int(var))
    if c is None:
        return {"var": int(var), "chi_star": int(profile["chi_star"]), "candidate": False, "width4_safe": False}, None
    if not c["DP_independent_replay_pass"] or not c["polynomial_intermediate_envelope_pass"]:
        raise AssertionError(("R49M_CANDIDATE_INTEGRITY_FAIL", var))
    final = canon(c["normalization"]["final_formula"])
    before_vars = set(r33.variables(core))
    after_vars = set(r33.variables(final))
    terminal = c["normalization"]["terminal"]
    delta_v = len(before_vars) - len(after_vars)
    no_fresh = after_vars <= before_vars
    w = max_width(final)
    eligible = bool(terminal is not None or (delta_v >= 1 and no_fresh))
    safe = bool(terminal is not None or (eligible and w <= WIDTH_CAP))
    return {
        "var": int(var),
        "chi_star": int(profile["chi_star"]),
        "positive_parent_count": int(profile["positive_parent_count"]),
        "negative_parent_count": int(profile["negative_parent_count"]),
        "retained_nontautological_pair_count": int(profile["retained_nontautological_pair_count"]),
        "candidate": True,
        "forced_DP_CLV": list(c["DP"]["measure_after_forced_DP"]),
        "final_CLV": list(r49i.clv(final)),
        "final_hash": r49i.fhash(final),
        "terminal": terminal,
        "semantic_sat": c["normalization"]["semantic_sat"],
        "delta_V_eliminated": int(delta_v),
        "no_fresh_variables": bool(no_fresh),
        "final_max_width": int(w),
        "width4_safe": bool(safe),
        "R47J_legacy_CLV_accepted_flag": bool(c["accepted"]),
        "R47J_round_count": int(c["normalization"]["round_count"]),
        "R47J_restart_count": int(c["normalization"]["restart_count"]),
        "R47J_RUP_checks": int(c["normalization"]["ledger"]["RUP_checks"]),
    }, c


def run():
    root, rec, core = recreate_core()
    profiles = [r49i.variable_profile(core, int(v)) for v in r33.variables(core)]
    ordered = sorted(profiles, key=lambda p: (int(p["chi_star"]), int(p["retained_nontautological_pair_count"]), int(p["var"])))
    rows = []
    winner = None
    for profile in ordered:
        row, c = candidate_row(core, int(profile["var"]), profile)
        rows.append(row)
        if row.get("width4_safe", False):
            replay = r47j.independent_fixpoint_macro_replay(core, c)
            if not replay["pass"]:
                raise AssertionError(("R49M_WINNER_REPLAY_FAIL", row["var"], replay))
            row["R47J_independent_replay_pass"] = True
            winner = row
            break

    return {
        "gate": GATE,
        "verdict": "R49K_EXPLICIT_HARD_CORE_DISCHARGED_BY_R47J_WIDTH4_SUCCESSOR" if winner is not None else "R49K_EXPLICIT_HARD_CORE_SURVIVES_ALL_PARTIAL_R47J_PIVOTS",
        "source": {
            "root_hash": r49i.fhash(root),
            "root_CLV": list(r49i.clv(root)),
            "safe_only_path": [int(x["pivot"]) for x in rec["steps"]],
            "core_hash": r49i.fhash(core),
            "core_CLV": list(r49i.clv(core)),
            "core_max_width": max_width(core),
        },
        "ordered_pivot_profiles": [{"var": int(p["var"]), "chi_star": int(p["chi_star"]), "pairs": int(p["retained_nontautological_pair_count"])} for p in ordered],
        "candidates_attempted": rows,
        "winner": winner,
        "interpretation": {
            "R49K_refutes_easy_only_chain": True,
            "winner_if_present_is_independently_replayed": winner is not None,
            "this_is_finite_explicit_core_only": True,
        },
        "firewall": {
            "UNIVERSAL_EASY_LANE_EXISTENCE": "REFUTED_BY_EXPLICIT_REACHABLE_R49K_CORE",
            "R49K_CORE_PARTIAL_R47J_DISCHARGE": "FOUND" if winner is not None else "NOT_FOUND",
            "DIRECT_W4_STEP_COVERAGE": "OPEN",
            "O4_UNIVERSAL_COVERAGE": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_EQ_NP": "NOT_PROVED",
            "P_NE_NP": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False
        }
    }


def main():
    out = run()
    path = Path("artifacts/JANUS_TRUMP_R49M_R49K_OBSTRUCTION_TARGETED_R47J_DISCHARGE_RESULT.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"gate": out["gate"], "verdict": out["verdict"], "source": out["source"], "winner": out["winner"], "attempted": len(out["candidates_attempted"]), "firewall": out["firewall"]}, sort_keys=True))


if __name__ == "__main__":
    main()
