from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r35b_single_literal_rup_vivification as r35b
import janus_trump_r45a_byte_pinned_ascent_descent_macro as r45a
import janus_trump_r50g4_prefix_closure_microstep_authority as r50g4
import janus_trump_r50g10_wide_fixpoint_forces_alternate_certified_door as r50g10
import janus_trump_r50g17_v6_wide6_all_variable_bve_saturation_cage as r50g17

GATE = "JANUS_TRUMP_R50G18_EXPLICIT_V7_FULL_SIXFOLD_CAGE_ANCESTRY_AND_DOOR_AUDIT"
PIVOT = 1
R = r33.canonical_clause((2, 3, 4, 5, 6, 7))
SOURCE = r33.canonical_formula((
    (-4, -7), (-3, -6), (-2, -5),
    (-5, 6, 7), (-4, 5, 6), (-3, 4, 5), (-2, 3, 4),
    (2, -6, 7), (2, 3, -7),
    (-1, 5, 6, 7), (1, 2, 3, 4),
))
EXPECTED_CAGE = r33.canonical_formula((
    (-4, -7), (-3, -6), (-2, -5),
    (-5, 6, 7), (-4, 5, 6), (-3, 4, 5), (-2, 3, 4),
    (2, -6, 7), (2, 3, -7),
    (2, 3, 4, 5, 6, 7),
))


def max_width(f):
    return max((len(c) for c in r33.canonical_formula(f)), default=0)


def exact_construction_audit():
    f = SOURCE
    if list(r33.measure(f)) != [11, 32, 7]:
        raise AssertionError(("R50G18_SOURCE_MEASURE_DRIFT", r33.measure(f)))
    if set(r33.variables(f)) != set(range(1, 8)) or max_width(f) != 4:
        raise AssertionError(("R50G18_SOURCE_DOMAIN_DRIFT", r33.variables(f), max_width(f)))
    if not r50g10.exact_pre_bve_clean(f):
        raise AssertionError("R50G18_FIXED_SOURCE_NOT_PRE_BVE_CLEAN")

    micro = r50g4.micro_r33_status(f)
    if micro["status"] != "IMMEDIATE_BVE_W4_ESCAPE":
        raise AssertionError(("R50G18_NOT_IMMEDIATE_BVE_ESCAPE", micro))
    direct = r50g4.first_r33_micro_candidate(f)
    if direct.get("rule") != "BOUNDED_VARIABLE_ELIMINATION" or int(direct.get("var", -1)) != PIVOT:
        raise AssertionError(("R50G18_FIRST_BVE_NOT_PIVOT1", direct))
    if max_width(direct["after"]) != 6:
        raise AssertionError(("R50G18_BVE_ESCAPE_NOT_WIDTH6", max_width(direct["after"])))

    dp = r45a.exact_dp_record(f, PIVOT)
    if dp is None:
        raise AssertionError("R50G18_DP_RECORD_MISSING")
    replay = r45a.independent_dp_replay(f, dp)
    if not replay["pass"]:
        raise AssertionError(("R50G18_DP_REPLAY_FAIL", replay))
    forced = r33.canonical_formula(dp["transformed"])
    if forced != EXPECTED_CAGE:
        raise AssertionError(("R50G18_FORCED_CAGE_MISMATCH", forced, EXPECTED_CAGE))
    if list(r33.measure(forced)) != [10, 30, 6]:
        raise AssertionError(("R50G18_CAGE_MEASURE_DRIFT", r33.measure(forced)))

    cage = r50g17.six_variable_saturation_cage(forced, R)
    if not cage["all_six_variables_bve_blocked"]:
        raise AssertionError(("R50G18_NOT_FULL_SIXFOLD_CAGE", cage))
    for row in cage["profiles"]:
        if (int(row["p"]), int(row["n"])) != (3, 2):
            raise AssertionError(("R50G18_NOT_EXACT_3x2_FOR_ALL", row))
        if row["bve_accepted"]:
            raise AssertionError(("R50G18_CAGE_BVE_OPEN", row))

    reduced = r33.simplify(forced)
    after_r33 = r33.canonical_formula(reduced["final_formula"])
    if reduced["terminal"] != "STALLED_STACK_LEAN_CORE":
        raise AssertionError(("R50G18_CAGE_NOT_R33_STALLED", reduced["terminal"], reduced["history"]))
    if after_r33 != forced:
        raise AssertionError(("R50G18_R33_CHANGED_FULL_CAGE", reduced["history"]))

    rup = r35b.run_candidate(after_r33)
    rup_replay = r35b.independent_certificate_replay(after_r33, rup)
    if not rup_replay["pass"]:
        raise AssertionError(("R50G18_RUP_REPLAY_FAIL", rup_replay))

    return {
        "source": [list(c) for c in f],
        "source_hash": r50g4.fhash(f),
        "source_CLV": list(r33.measure(f)),
        "source_pre_bve_clean": True,
        "first_microstep": {
            "status": micro["status"],
            "rule": direct["rule"],
            "pivot": int(direct["var"]),
            "proposal_max_width": max_width(direct["after"]),
        },
        "forced_cage": [list(c) for c in forced],
        "forced_cage_hash": r50g4.fhash(forced),
        "forced_cage_CLV": list(r33.measure(forced)),
        "DP_independent_replay_pass": True,
        "sixfold_cage": cage,
        "R33_stalled_unchanged": True,
        "initial_RUP": {
            "status": rup["status"],
            "successful_strengthenings": int(rup["successful_strengthenings"]),
            "history": rup["history"],
            "final_formula": rup["final_formula"],
            "independent_replay_pass": True,
        },
    }


def exact_door_audit():
    same = r50g10.exact_door_row(SOURCE, PIVOT)
    alternate = r50g10.profile_all_alternate_doors(SOURCE, PIVOT)
    same_r47j_unsafe = not bool(same["r47j_safe"])
    all_alt_closed = bool(alternate["all_alternate_doors_closed"])
    return {
        "same_pivot": same,
        "same_pivot_R47J_unsafe": same_r47j_unsafe,
        "alternate": alternate,
        "all_doors_closed_local": bool(same_r47j_unsafe and all_alt_closed),
    }


def run():
    construction = exact_construction_audit()
    doors = exact_door_audit()

    if doors["all_doors_closed_local"]:
        verdict = "EXPLICIT_V7_FULL_CAGE_ANCESTRY_REALIZER_IS_LOCAL_ALL_DOORS_CLOSED_COUNTEREXAMPLE__REACHABILITY_NOT_ESTABLISHED"
    elif not doors["same_pivot_R47J_unsafe"]:
        verdict = "EXPLICIT_V7_FULL_CAGE_ANCESTRY_REALIZER_CONFIRMED__SAME_PIVOT_R47J_SAFE"
    else:
        verdict = "EXPLICIT_V7_FULL_CAGE_ANCESTRY_REALIZER_CONFIRMED__SAME_PIVOT_UNSAFE_BUT_CERTIFIED_ALTERNATE_DOOR_EXISTS"

    return {
        "gate": GATE,
        "mode": "SINGLE_FIXED_EXACT_CONSTRUCTION_PLUS_EXISTING_FROZEN_DOOR_AUDIT",
        "construction": construction,
        "door_audit": doors,
        "verdict": verdict,
        "critical_next_obligation": (
            "IF_SAME_PIVOT_SAFE__EXTRACT_THE_EXACT_RUP_R33_RESTART_MECHANISM_THAT_BREAKS_THE_FULL_CAGE_AND_PROVE_IT_FOR_ALL_EXACT_MINIMAL_CAGES;_"
            "IF_SAME_PIVOT_UNSAFE_WITH_ALT_DOOR__ISOLATE_THE_FORCED_ALTERNATE_DOOR_GEOMETRY;_"
            "IF_ALL_DOORS_CLOSED__ATTACK_REACHABILITY_SPECIFIC_EXCLUSION"
        ),
        "firewall": {
            "FULL_CAGE_ANCESTRY_IMPOSSIBILITY": "REFUTED_LOCAL" if construction else "OPEN",
            "FULL_CAGE_REALIZER_IMPLIES_REACHABLE_COUNTEREXAMPLE": False,
            "RUP_BEARING_V7_HUB_CYCLE_ELIMINATED": False,
            "V7_IMMEDIATE_BVE_CASE_ELIMINATED": False,
            "IMMEDIATE_BVE_CASE_ELIMINATED": False,
            "U_MU": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_EQ_NP": "NOT_PROVED",
            "P_NE_NP": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    out = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
