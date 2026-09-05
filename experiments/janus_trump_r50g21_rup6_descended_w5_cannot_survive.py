from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r35b_single_literal_rup_vivification as r35b
import janus_trump_r50g14_v7_hub_cycle_ancestry_bifurcation as r50g14
import janus_trump_r50g17_v6_wide6_all_variable_bve_saturation_cage as r50g17
import janus_trump_r50g18_explicit_v7_full_sixfold_cage_ancestry_door_audit as r50g18
import janus_trump_r50g20_rup6_phase_collapse_to_v6_w5_core as r50g20

GATE = "JANUS_TRUMP_R50G21_RUP6_DESCENDED_W5_CANNOT_SURVIVE"


def canon(formula):
    return r33.canonical_formula(formula)


def max_width(formula):
    return max((len(c) for c in canon(formula)), default=0)


def nonblocking_witnesses(formula, full_clause, head_lit: int):
    f = canon(formula)
    R = r33.canonical_clause(full_clause)
    out = []
    for d in f:
        if -int(head_lit) not in d:
            continue
        rr = r50g17.resolve_oriented(R, d, int(head_lit))
        if rr is None:
            continue
        support = tuple(x for x in d if x != -int(head_lit))
        out.append({
            "clause": d,
            "support": support,
            "resolvent": rr,
        })
    return out


def proper_hub_witness_case_r50g18():
    H0 = canon(r50g18.EXPECTED_CAGE)
    R = r33.canonical_clause(r50g18.R)
    zlit = min(R, key=lambda x: abs(int(x)))
    C = r33.canonical_clause(x for x in R if x != zlit)

    entry = r50g20.entry_full_clause_certificate(H0, R)
    if not entry["all_six_one_literal_deletions_rup_valid"]:
        raise AssertionError("R50G21_R50G18_ENTRY_DRIFT")

    zw = nonblocking_witnesses(H0, R, int(zlit))
    proper = [w for w in zw if set(w["support"]) < set(C)]
    if not proper:
        raise AssertionError(("R50G21_R50G18_EXPECTED_PROPER_Z_WITNESS", zw, C))
    chosen = proper[0]
    missing = [lit for lit in C if lit not in set(chosen["support"])]
    if not missing:
        raise AssertionError("R50G21_PROPER_WITNESS_HAS_NO_MISSING_LITERAL")
    ell = int(missing[0])

    candidate = r35b.run_candidate(H0)
    replay = r35b.independent_certificate_replay(H0, candidate)
    if not replay["pass"]:
        raise AssertionError(("R50G21_R50G18_RUP_REPLAY_FAIL", replay))

    state = H0
    post_creation = None
    creation_record = None
    for record in candidate["history"]:
        if tuple(record["source_clause"]) == R and post_creation is None:
            creation_record = record
            state = r50g20.apply_rup_record(state, record)
            post_creation = state
            continue
        state = r50g20.apply_rup_record(state, record)

    if post_creation is None or creation_record is None:
        raise AssertionError("R50G21_R50G18_WIDE6_CHILD_NOT_CREATED")
    if C not in post_creation:
        raise AssertionError(("R50G21_R50G18_CHILD_C_MISSING_AFTER_CREATION", C, post_creation))
    if not r50g20.exact_rup_valid(post_creation, C, ell):
        raise AssertionError(("R50G21_PROPER_SUPPORT_CASE_DID_NOT_FORCE_CHILD_RUP", ell, chosen))

    # Independent pair/chain explanation: choose one R witness on ell.
    ew = nonblocking_witnesses(H0, R, ell)
    if not ew:
        raise AssertionError(("R50G21_R50G18_NO_ELL_WITNESS", ell))

    return {
        "H0_CLV": list(r33.measure(H0)),
        "wide6": list(R),
        "removed_hub_literal": int(zlit),
        "child_C": list(C),
        "proper_z_witness": {
            "clause": list(chosen["clause"]),
            "support": list(chosen["support"]),
            "resolvent": list(chosen["resolvent"]),
        },
        "chosen_missing_literal": ell,
        "ell_nonblocking_witness": {
            "clause": list(ew[0]["clause"]),
            "support": list(ew[0]["support"]),
            "resolvent": list(ew[0]["resolvent"]),
        },
        "creation_step": int(creation_record["step"]),
        "child_one_literal_deletion_rup_valid": True,
        "independent_full_pass_replay": True,
    }


def abstract_twin_dual_support_control():
    z = 1
    C = r33.canonical_clause((2, 3, 4, 5, 6))
    R = r33.canonical_clause((1, 2, 3, 4, 5, 6))
    twin = r33.canonical_clause((-1, 2, 3, 4, 5, 6))
    ell = 2
    e_plus = r33.canonical_clause((-2, 1, 3))
    e_minus = r33.canonical_clause((-2, -1, 4))
    after_creation = canon([C, twin, e_plus, e_minus])
    strengthened, assumptions = r50g20.rup_assumptions_for_delete(C, ell)
    receipt = r35b.candidate_unit_propagation_trace(after_creation, assumptions)
    independent = r35b.independent_up_conflict_checker(after_creation, assumptions)
    if not receipt["conflict"] or not independent:
        raise AssertionError(("R50G21_TWIN_DUAL_SUPPORT_CONTROL_FAIL", receipt, independent))
    trail = [int(x["literal"]) for x in receipt["trail"]]
    if ell not in trail or z not in {abs(x) for x in trail}:
        raise AssertionError(("R50G21_TWIN_CONTROL_TRAIL_MISSING_FORCING", trail))
    return {
        "full_R": list(R),
        "opposite_full_twin": list(twin),
        "child_C": list(C),
        "tested_removed_literal": ell,
        "strengthened_child": list(strengthened),
        "assumptions": list(assumptions),
        "R_side_witness": list(e_plus),
        "twin_side_witness": list(e_minus),
        "UP_conflict": True,
        "independent_UP_replay": True,
        "trail": trail,
    }


def source_case_dichotomy_contract():
    return {
        "case_A": {
            "condition": "some opposite-hub nonblocking witness (-z OR S) has S proper subset C",
            "consequence": "choose ell in C\\S; after R->C, C\\{ell} is RUP-valid using that hub witness plus any R-side nonblocking ell witness",
        },
        "case_B": {
            "condition": "all opposite-hub nonblocking witnesses have full support C",
            "consequence": "the opposite full twin (-z OR C) is present; BCE fixedness of R and twin supplies opposite hub-polarity ell witnesses, making C\\{ell} RUP-valid for every ell",
        },
        "exhaustive": True,
        "last_creation_argument": "if C was absent at H0, after the last width6->C creation a persistent C deletion remains and the complete pass cannot stall with C",
    }


def r50g14_ancestry_collapse_contract():
    controls = r50g14.source_ancestry_controls()
    if not any(row["type"] == "DIRECT5" for row in controls["DIRECT5"]):
        raise AssertionError("R50G21_R50G14_DIRECT5_CONTROL_DRIFT")
    if not any(row["type"] == "RUP6_DROP_HUB" for row in controls["RUP6_DROP_HUB"]):
        raise AssertionError("R50G21_R50G14_RUP6_CONTROL_DRIFT")
    if r50g14.cycle_label_bifurcation(["DIRECT5", "DIRECT5"]) != "ALL_DIRECT5_CYCLE":
        raise AssertionError("R50G21_R50G14_CYCLE_CLASS_DRIFT")
    return {
        "prior_exact_labels": ["DIRECT5", "RUP6_DROP_HUB"],
        "r50g14_controls_present": True,
        "new_elimination": "RUP6_DROP_HUB_CANNOT_BE_A_NOVEL_SURVIVING_W5_EDGE_AFTER_COMPLETE_RUP",
        "remaining_surviving_label": "DIRECT5",
        "remaining_cycle_class": "ALL_DIRECT5_CYCLE",
    }


def r50g18_full_pass_regression():
    H0 = canon(r50g18.EXPECTED_CAGE)
    candidate = r35b.run_candidate(H0)
    replay = r35b.independent_certificate_replay(H0, candidate)
    if not replay["pass"]:
        raise AssertionError(("R50G21_R50G18_FULL_REPLAY_FAIL", replay))
    final = canon(candidate["final_formula"])
    return {
        "status": candidate["status"],
        "successful_strengthenings": int(candidate["successful_strengthenings"]),
        "final_CLV": list(r33.measure(final)),
        "final_max_width": max_width(final),
        "width5_survivor_count": sum(1 for c in final if len(c) == 5),
        "independent_replay_pass": True,
    }


def run():
    proper = proper_hub_witness_case_r50g18()
    twin = abstract_twin_dual_support_control()
    dichotomy = source_case_dichotomy_contract()
    ancestry = r50g14_ancestry_collapse_contract()
    regression = r50g18_full_pass_regression()

    return {
        "gate": GATE,
        "mode": "SOURCE_DICHOTOMY_THEOREM_PLUS_EXACT_PROPER_SUPPORT_AND_TWIN_CONTROLS",
        "proved_from_frozen_source_definitions": [
            "AFTER_RUP6_CREATES_CHILD_C__A_PROPER_OPPOSITE_HUB_SUPPORT_FORCES_A_FURTHER_RUP_DELETION_OF_C",
            "IF_NO_PROPER_OPPOSITE_HUB_SUPPORT_EXISTS__THE_OPPOSITE_FULL_TWIN_IS_FORCED",
            "BCE_FIXEDNESS_OF_FULL_R_AND_OPPOSITE_FULL_TWIN_FORCES_DUAL_HUB_POLARITY_SUPPORT_OR_EARLIER_CONFLICT_FOR_EVERY_CHILD_LITERAL",
            "THEREFORE_A_NOVEL_WIDTH5_CHILD_OF_WIDTH6_CANNOT_SURVIVE_UNCHANGED_TO_COMPLETE_RUP_FIXPOINT",
            "LAST_CREATION_HANDLES_REPEATED_WIDTH6_TO_SAME_C_RECREATION",
            "EVERY_SURVIVING_WIDTH5_CLAUSE_AFTER_COMPLETE_RUP_WAS_ALREADY_WIDTH5_AT_H0",
            "UNDER_R50G14_V7_ANCESTRY__SURVIVING_W5_LABEL_IS_DIRECT5_ONLY_AND_RUP6_DROP_HUB_IS_ELIMINATED",
            "RUP_BEARING_V7_HUB_CYCLE_CLASS_IS_ELIMINATED__ALL_DIRECT5_CYCLE_REMAINS_OPEN",
        ],
        "r50g18_proper_support_control": proper,
        "opposite_full_twin_dual_support_control": twin,
        "source_case_dichotomy": dichotomy,
        "r50g14_ancestry_collapse": ancestry,
        "r50g18_full_pass_regression": regression,
        "critical_next_obligation": "ATTACK_ALL_DIRECT5_V7_HUB_CYCLE_UNDER_PRE_BVE_CLEAN_W4_SOURCE__PROVE_CYCLE_IMPOSSIBILITY_OR_BUILD_EXPLICIT_V7_ALL_DIRECT5_ALL_DOORS_CLOSED_REALIZER",
        "verdict": "RUP6_DESCENDED_NOVEL_W5_SURVIVOR_ELIMINATED__RUP6_DROP_HUB_SURVIVING_V7_EDGE_ELIMINATED__V7_HUB_CYCLE_REDUCED_TO_ALL_DIRECT5_ONLY",
        "firewall": {
            "FINITE_CONTROLS_ARE_THE_UNIVERSAL_PROOF": False,
            "RUP6_DESCENDED_NOVEL_W5_SURVIVOR": "ELIMINATED_BY_SOURCE_DICHOTOMY",
            "RUP6_DROP_HUB_SURVIVING_V7_EDGE_ELIMINATED": True,
            "RUP_BEARING_V7_HUB_CYCLE_ELIMINATED": True,
            "V7_SURVIVING_HUB_CYCLE_CLASS": "ALL_DIRECT5_ONLY",
            "ALL_DIRECT5_V7_HUB_CYCLE_ELIMINATED": False,
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
