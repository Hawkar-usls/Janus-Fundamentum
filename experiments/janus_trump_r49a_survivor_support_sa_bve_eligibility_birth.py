from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r47m_post_dp_full_existing_stack_closure as r47m
import janus_trump_r48z_pivot10_survivor_sa_bve_causal_forensics as r48z

GATE = "JANUS_TRUMP_R49A_SURVIVOR_SUPPORT_SA_BVE_ELIGIBILITY_BIRTH"
SUPPORT = [15, 20, 24, 27, 28]
SURVIVOR = tuple(r48z.SURVIVOR)
EXPECTED_BVE_SEQUENCE = [26, 12, 14, 30, 23, 29, 27, 18]
REMOVAL_OUTER = 6


def canon(f):
    return r33.canonical_formula(f)


def clv(f):
    return r33.measure(canon(f))


def fhash(f):
    return r48z.fhash(canon(f))


def raw_var_profile(formula, var, rank_map):
    before = canon(formula)
    before_m = clv(before)
    pos, neg, resolvents, pair_checks = r47m.r42.all_dp_resolvents(before, int(var))
    profile = {
        "var": int(var),
        "present": int(var) in r33.variables(before),
        "positive_parent_count": len(pos),
        "negative_parent_count": len(neg),
        "resolution_pair_checks": int(pair_checks),
        "non_tautological_distinct_resolvent_count": len(resolvents),
        "pool_clause_count_before_subsumption": None,
        "transformed_CLV": None,
        "delta_C": None,
        "delta_L": None,
        "delta_V": None,
        "eligible": False,
        "ineligibility_reason": None,
        "rank_among_all_eligible_candidates_if_eligible": None,
    }
    if not pos or not neg:
        profile["ineligibility_reason"] = "NOT_BIPOLAR"
        return profile
    base = tuple(c for c in before if int(var) not in c and -int(var) not in c)
    pool = r33.canonical_formula(list(base) + list(resolvents))
    transformed = r47m.r42.subsumption_minimize(pool)
    after_m = clv(transformed)
    eligible = bool(after_m < before_m)
    profile.update({
        "pool_clause_count_before_subsumption": len(pool),
        "transformed_CLV": list(after_m),
        "delta_C": int(after_m[0] - before_m[0]),
        "delta_L": int(after_m[1] - before_m[1]),
        "delta_V": int(after_m[2] - before_m[2]),
        "eligible": eligible,
        "ineligibility_reason": None if eligible else "NO_STRICT_CLV_DESCENT",
        "rank_among_all_eligible_candidates_if_eligible": rank_map.get(int(var)),
    })
    return profile


def eligible_candidates(formula):
    candidates = []
    for var in r33.variables(formula):
        c = r47m.r42.sa_bve_candidate_for_var(formula, int(var))
        if c is not None:
            candidates.append(c)
    candidates.sort(key=lambda x: (tuple(x["measure_after"]), int(x["var"])))
    return candidates


def bool_flaps(seq):
    compact = []
    for x in seq:
        if not compact or compact[-1] != x:
            compact.append(x)
    return len(compact) >= 3


def run():
    _, predecessor, _ = r48z.reconstruct_predecessor()
    claimed = r47m.macro_candidate_full_closure(predecessor, r48z.PIVOT)
    if claimed is None:
        raise AssertionError("R49A_PIVOT10_MISSING")
    replay = r47m.independent_replay(predecessor, claimed)
    if not replay["pass"]:
        raise AssertionError(("R49A_PIVOT10_REPLAY_FAIL", replay))
    forced = canon(claimed["DP"]["transformed"])
    state = forced
    rows = []
    observed_sequence = []

    for outer in range(len(EXPECTED_BVE_SEQUENCE) + 1):
        before = canon(state)
        norm = r47j.normalize_to_certified_fixpoint(before)
        after_norm = canon(norm["final_formula"])
        survivor_present = SURVIVOR in after_norm
        if norm["terminal"] is not None:
            rows.append({
                "outer": int(outer),
                "state_hash_after_R47J": fhash(after_norm),
                "state_CLV_after_R47J": list(clv(after_norm)),
                "survivor_present": bool(survivor_present),
                "terminal": norm["terminal"],
                "all_eligible_candidate_count": 0,
                "legacy_chosen_var": None,
                "support_profiles": [],
            })
            state = after_norm
            break

        all_candidates = eligible_candidates(after_norm)
        rank_map = {int(c["var"]): i + 1 for i, c in enumerate(all_candidates)}
        best, ledger = r47m.r42.best_sa_bve_candidate(after_norm)
        if best is None:
            raise AssertionError(("R49A_LEGACY_BVE_MISSING", outer))
        best_var = int(best["var"])
        if outer >= len(EXPECTED_BVE_SEQUENCE) or best_var != EXPECTED_BVE_SEQUENCE[outer]:
            raise AssertionError(("R49A_LEGACY_SEQUENCE_DRIFT", outer, best_var, EXPECTED_BVE_SEQUENCE))
        brep = r47m.r42.independent_sa_bve_replay(after_norm, best)
        if not brep["pass"]:
            raise AssertionError(("R49A_SELECTED_BVE_REPLAY_FAIL", outer, best_var, brep))
        support_profiles = [raw_var_profile(after_norm, v, rank_map) for v in SUPPORT]
        chosen_rank = rank_map.get(best_var)
        if chosen_rank != 1:
            raise AssertionError(("R49A_BEST_RANK_DRIFT", outer, best_var, chosen_rank))
        rows.append({
            "outer": int(outer),
            "state_hash_after_R47J": fhash(after_norm),
            "state_CLV_after_R47J": list(clv(after_norm)),
            "survivor_present": bool(survivor_present),
            "terminal": None,
            "all_eligible_candidate_count": len(all_candidates),
            "eligible_candidate_order": [int(c["var"]) for c in all_candidates],
            "legacy_chosen_var": best_var,
            "legacy_chosen_CLV_after": list(best["measure_after"]),
            "legacy_variables_checked": int(ledger["variables_checked"]),
            "support_profiles": support_profiles,
        })
        observed_sequence.append(best_var)
        state = canon(best["transformed"])

    if observed_sequence != EXPECTED_BVE_SEQUENCE:
        raise AssertionError(("R49A_FINAL_SEQUENCE_MISMATCH", observed_sequence))
    if fhash(state) != claimed["normalization"]["final_formula_hash"]:
        raise AssertionError(("R49A_FINAL_HASH_MISMATCH", fhash(state), claimed["normalization"]["final_formula_hash"]))
    if rows[-1]["terminal"] != "DIRECT_EMPTY_CNF":
        raise AssertionError(("R49A_TERMINAL_DRIFT", rows[-1]["terminal"]))

    active_rows = [r for r in rows if r["terminal"] is None and r["outer"] <= REMOVAL_OUTER]
    any_support_seq = []
    var27_seq = []
    earliest_support = None
    earliest_support_vars = []
    earliest27 = None
    for row in active_rows:
        elig = [p["var"] for p in row["support_profiles"] if p["eligible"]]
        any_support_seq.append(bool(elig))
        p27 = next(p for p in row["support_profiles"] if p["var"] == 27)
        var27_seq.append(bool(p27["eligible"]))
        if elig and earliest_support is None:
            earliest_support = int(row["outer"])
            earliest_support_vars = elig
        if p27["eligible"] and earliest27 is None:
            earliest27 = int(row["outer"])

    flaps = bool_flaps(any_support_seq) or bool_flaps(var27_seq)
    if flaps:
        classification = "SUPPORT_SA_BVE_ELIGIBILITY_FLAPS_BEFORE_REMOVAL"
    elif earliest_support == 0:
        classification = "SUPPORT_SA_BVE_AVAILABLE_IMMEDIATELY__LEGACY_RANKING_DELAY"
    elif earliest27 is not None and earliest27 < REMOVAL_OUTER:
        classification = "VAR27_AVAILABLE_EARLIER_BUT_OTHER_SUPPORT_PIVOT_BIRTH_DIFFERS"
    elif earliest_support is not None and earliest_support <= REMOVAL_OUTER:
        classification = "SUPPORT_SA_BVE_BECOMES_AVAILABLE_AFTER_EXTERNAL_PREREQUISITES"
    else:
        classification = "UNEXPECTED_PROFILE_REGRESSION"

    var27_timeline = []
    for row in active_rows:
        p = next(p for p in row["support_profiles"] if p["var"] == 27)
        var27_timeline.append({"outer": row["outer"], **p})

    return {
        "gate": GATE,
        "classification": classification,
        "survivor": list(SURVIVOR),
        "support": SUPPORT,
        "legacy_SA_BVE_sequence": observed_sequence,
        "rows": rows,
        "summary": {
            "earliest_outer_with_any_support_eligible": earliest_support,
            "support_vars_at_first_eligibility": earliest_support_vars,
            "earliest_outer_with_var27_eligible": earliest27,
            "actual_survivor_removal_outer": REMOVAL_OUTER,
            "actual_survivor_removal_var": 27,
            "any_support_eligibility_sequence_through_removal": any_support_seq,
            "var27_eligibility_sequence_through_removal": var27_seq,
            "eligibility_flaps": flaps,
        },
        "var27_timeline": var27_timeline,
        "interpretation": {
            "finite_single_path_profile_only": True,
            "support_first_controller_justified_for_experiment": earliest_support == 0,
            "eligibility_debt_route_motivated": earliest_support not in (None, 0),
            "universal_support_availability_proved": False,
        },
        "firewall": {
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
    print(json.dumps({
        "gate": d["gate"],
        "classification": d["classification"],
        "summary": d["summary"],
        "var27_timeline": [{
            "outer": x["outer"],
            "pos": x["positive_parent_count"],
            "neg": x["negative_parent_count"],
            "resolvents": x["non_tautological_distinct_resolvent_count"],
            "pool": x["pool_clause_count_before_subsumption"],
            "after_CLV": x["transformed_CLV"],
            "delta_C": x["delta_C"],
            "delta_L": x["delta_L"],
            "delta_V": x["delta_V"],
            "eligible": x["eligible"],
            "reason": x["ineligibility_reason"],
            "rank": x["rank_among_all_eligible_candidates_if_eligible"],
        } for x in d["var27_timeline"]],
        "chosen": [{"outer": r["outer"], "var": r["legacy_chosen_var"], "eligible_order": r.get("eligible_candidate_order")} for r in d["rows"] if r["terminal"] is None],
        "firewall": d["firewall"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
