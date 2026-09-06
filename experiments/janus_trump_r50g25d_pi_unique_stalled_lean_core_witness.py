from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r50g25d_dynamic_replacement_after_source_normalized_minimum_joint_debt as r50g25d

GATE = "JANUS_TRUMP_R50G25D_PI_UNIQUE_STALLED_LEAN_CORE_WITNESS"
PIVOT = 1


def canon(formula):
    return r50g25d.canon(formula)


def run():
    parent = r50g25d.run()
    if parent["no_BCE_BVE_debt_after_lift_unique_count"] != 1:
        raise AssertionError(("R50G25D_PI_EXPECTED_UNIQUE_NO_DEBT_DRIFT", parent["no_BCE_BVE_debt_after_lift_unique_count"]))

    r50g25c = r50g25d.r50g25c
    r50g25b = r50g25c.r50g25b
    r50g25a = r50g25b.r50g25a
    r50g23 = r50g25a.r50g24.r50g23
    r47j = r50g23.r47j
    r42 = r47j.r45a.r42
    r33 = r50g23.r33

    _p, unique = r50g25b.rebuild_unique_states()
    skeletons = r50g23.clean_skeletons_from_frozen_r50g22()
    source_by_hash = {item["source_hash"]: item for item in skeletons}

    hits = []
    for _key, entry in sorted(unique.items(), key=lambda kv: (kv[1]["forced_CLV"], kv[0])):
        target = canon(entry["forced_formula"])
        cover = r50g25b.exact_minimum_cover(target)
        minimum = int(cover["minimum"])
        if minimum < 3:
            continue

        witness = entry["witness"]
        source_item = source_by_hash[witness["source_hash"]]
        source = canon(source_item["source"])
        c1 = tuple(int(x) for x in witness["first_clause"])
        c2 = tuple(int(x) for x in witness["second_clause"])
        lifted = [tuple(int(x) for x in clause) for clause in cover["clauses"]]
        lifted_source = canon(list(source) + [c1, c2] + lifted)

        dp = r47j.r45a.exact_dp_record(lifted_source, PIVOT)
        if dp is None:
            raise AssertionError(("R50G25D_PI_DP_RECORD_MISSING", witness))
        replay = r47j.r45a.independent_dp_replay(lifted_source, dp)
        if not replay.get("pass"):
            raise AssertionError(("R50G25D_PI_DP_REPLAY_FAIL", witness))

        actual = canon(dp["transformed"])
        expected = canon(list(target) + lifted)
        normalized_expected = canon(r42.subsumption_minimize(expected))
        if actual != expected and actual != normalized_expected:
            raise AssertionError(("R50G25D_PI_SOURCE_NORMAL_FORM_DRIFT", witness))

        bces = r50g25a.blocked_candidates(actual)
        bves = r50g25a.all_bve_candidates(actual)
        first_label, first_reduced = r50g25c.first_r33_label(actual)
        if bces or bves or first_label != "R33_TERMINAL:STALLED_STACK_LEAN_CORE":
            continue

        macro = r47j.macro_candidate_fixpoint(lifted_source, PIVOT)
        if macro is None:
            raise AssertionError(("R50G25D_PI_MACRO_MISSING", witness))
        macro_replay = r47j.independent_fixpoint_macro_replay(lifted_source, macro)
        if not macro_replay.get("pass"):
            raise AssertionError(("R50G25D_PI_MACRO_REPLAY_FAIL", witness))

        hits.append({
            "spec": source_item["spec"],
            "source_hash": source_item["source_hash"],
            "target_state_hash": r50g23.r50g4.fhash(target),
            "occurrence_count": int(entry["occurrence_count"]),
            "source_formula": [list(c) for c in source],
            "first_clause": list(c1),
            "second_clause": list(c2),
            "initial_forced_formula": [list(c) for c in target],
            "initial_forced_CLV": list(r33.measure(target)),
            "minimum_static_joint_debt_cover": minimum,
            "minimum_cover_clauses": [list(c) for c in lifted],
            "lifted_source_formula": [list(c) for c in lifted_source],
            "post_DP_formula": [list(c) for c in actual],
            "post_DP_hash": r50g23.r50g4.fhash(actual),
            "post_DP_CLV": list(r33.measure(actual)),
            "post_DP_exact_expected_match": actual == expected,
            "post_DP_subsumption_normalized_expected_match": actual == normalized_expected,
            "post_DP_BCE_candidate_count": len(bces),
            "post_DP_BVE_candidate_count": len(bves),
            "first_R33_label": first_label,
            "first_R33_terminal": first_reduced.get("terminal"),
            "full_R47J_terminal": macro["normalization"].get("terminal"),
            "full_R47J_round_count": int(macro["normalization"].get("round_count", 0)),
            "full_R47J_restart_count": int(macro["normalization"].get("restart_count", 0)),
            "full_R47J_normalization": macro["normalization"],
            "macro_candidate": macro,
            "macro_replay_pass": True,
        })

    if len(hits) != 1:
        raise AssertionError(("R50G25D_PI_STALLED_WITNESS_COUNT_DRIFT", len(hits)))

    hit = hits[0]
    return {
        "gate": GATE,
        "parent_gate": parent["gate"],
        "unique_stalled_lean_core_witness_count": 1,
        "witness": hit,
        "next_gate": "R50G25E_PI_STALLED_LEAN_CORE_ALTERNATE_DOOR_FORENSICS",
        "interpretation_contract": {
            "no_BCE_BVE_debt_means_no_R33_reduction_door": False,
            "stalled_stack_lean_core_is_not_R47J_terminal": True,
            "single_witness_does_not_generalize": True,
            "alternate_door_must_be_identified_from_replay_transcript": True,
        },
        "firewall": {
            "ALL_DIRECT5_V7_HUB_CYCLE_ELIMINATED": False,
            "U_MU": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    args = ap.parse_args()
    out = run()
    text = json.dumps(out, sort_keys=True, indent=2)
    if args.out:
        p = Path(args.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
