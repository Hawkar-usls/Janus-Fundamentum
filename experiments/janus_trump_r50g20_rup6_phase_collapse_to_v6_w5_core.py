from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r35b_single_literal_rup_vivification as r35b
import janus_trump_r50g12_v6_rup_external_support_elimination as r50g12
import janus_trump_r50g17_v6_wide6_all_variable_bve_saturation_cage as r50g17
import janus_trump_r50g18_explicit_v7_full_sixfold_cage_ancestry_door_audit as r50g18

GATE = "JANUS_TRUMP_R50G20_RUP6_PHASE_COLLAPSE_TO_V6_W5_CORE"


def canon(formula):
    return r33.canonical_formula(formula)


def max_width(formula):
    return max((len(c) for c in canon(formula)), default=0)


def rup_assumptions_for_delete(clause, removed_literal: int):
    c = r33.canonical_clause(clause)
    l = int(removed_literal)
    if l not in c:
        raise ValueError("removed literal not in clause")
    strengthened = tuple(x for x in c if x != l)
    return strengthened, tuple(-x for x in strengthened)


def exact_rup_valid(formula, clause, removed_literal: int) -> bool:
    _strengthened, assumptions = rup_assumptions_for_delete(clause, removed_literal)
    return bool(r35b.independent_up_conflict_checker(canon(formula), assumptions))


def entry_full_clause_certificate(formula, wide_clause):
    """Frozen-source certificate for the H0 full-clause lemma.

    This executable checker is a control for the source proof.  Universality is
    supplied by the proof note, not by enumerating formulas here.
    """
    f = canon(formula)
    R = r33.canonical_clause(wide_clause)
    rvars = {abs(int(x)) for x in R}
    if len(R) != 6 or len(rvars) != 6:
        raise AssertionError(("R50G20_NOT_WIDTH6_ALL_VARIABLE_CLAUSE", R))
    if R not in f:
        raise AssertionError(("R50G20_WIDE_CLAUSE_MISSING", R))
    if set(r33.variables(f)) != rvars:
        raise AssertionError(("R50G20_H0_NOT_EXACTLY_SIX_R_VARIABLES", r33.variables(f), R))

    simp = r33.simplify(f)
    if simp["terminal"] != "STALLED_STACK_LEAN_CORE" or simp["history"]:
        raise AssertionError(("R50G20_H0_NOT_R33_FIXED", simp["terminal"], simp["history"][:1]))

    rows = []
    for lit in R:
        witnesses = []
        for d in f:
            if -int(lit) not in d:
                continue
            rr = r50g17.resolve_oriented(R, d, int(lit))
            if rr is None:
                continue
            support = tuple(x for x in d if x != -int(lit))
            if any(x not in R for x in support):
                raise AssertionError(("R50G20_NONTAUT_SUPPORT_NOT_R_POLARITY", lit, d, support, R))
            pair = canon([R, d])
            _strengthened, assumptions = rup_assumptions_for_delete(R, int(lit))
            if not r35b.independent_up_conflict_checker(pair, assumptions):
                raise AssertionError(("R50G20_PAIR_WITNESS_DID_NOT_FORCE_UP_CONFLICT", lit, d, assumptions))
            witnesses.append({
                "opposite_clause": list(d),
                "support_literals": list(support),
                "resolvent": list(rr),
            })
        if not witnesses:
            raise AssertionError(("R50G20_BCE_FIXED_FULL_CLAUSE_WITHOUT_NONBLOCKING_WITNESS", lit, R))
        if not exact_rup_valid(f, R, int(lit)):
            raise AssertionError(("R50G20_ENTRY_DELETION_NOT_RUP_VALID", lit, R))
        rows.append({
            "literal": int(lit),
            "rup_valid_at_H0": True,
            "first_nonblocking_witness": witnesses[0],
            "nonblocking_witness_count": len(witnesses),
        })

    return {
        "H0_CLV": list(r33.measure(f)),
        "H0_R33_fixed": True,
        "wide_clause": list(R),
        "minimum_variable": min(abs(int(x)) for x in R),
        "all_six_one_literal_deletions_rup_valid": True,
        "per_literal": rows,
    }


def apply_rup_record(formula, record):
    f = canon(formula)
    source = tuple(record["source_clause"])
    strengthened = tuple(record["strengthened_clause"])
    if source not in f:
        raise AssertionError(("R50G20_REPLAY_SOURCE_MISSING", source))
    if tuple(x for x in source if x != int(record["removed_literal"])) != strengthened:
        raise AssertionError(("R50G20_REPLAY_NOT_ONE_LITERAL_DELETE", record))
    return r35b.replace_clause_with_subclause(f, source, strengthened)


def first_wide_clause_touch(formula, wide_clause):
    f = canon(formula)
    R = r33.canonical_clause(wide_clause)
    entry = entry_full_clause_certificate(f, R)
    candidate = r35b.run_candidate(f)
    replay = r35b.independent_certificate_replay(f, candidate)
    if not replay["pass"]:
        raise AssertionError(("R50G20_RUP_INDEPENDENT_REPLAY_FAIL", replay))

    state = f
    persistence_checks = 0
    touch = None
    for record in candidate["history"]:
        if R in state:
            for lit in R:
                if not exact_rup_valid(state, R, int(lit)):
                    raise AssertionError(("R50G20_RUP_VALIDITY_NOT_PERSISTENT_IN_CONTROL", record["step"], lit))
                persistence_checks += 1
        if tuple(record["source_clause"]) == R and touch is None:
            removed = int(record["removed_literal"])
            expected_min = min(abs(int(x)) for x in R)
            if abs(removed) != expected_min:
                raise AssertionError(("R50G20_FROZEN_SELECTOR_NOT_MIN_VARIABLE", removed, expected_min, R))
            touch = {
                "step": int(record["step"]),
                "removed_literal": removed,
                "minimum_variable": expected_min,
                "source_clause": list(R),
                "strengthened_clause": list(record["strengthened_clause"]),
                "measure_before": record["measure_before"],
                "measure_after": record["measure_after"],
            }
        state = apply_rup_record(state, record)

    final = canon(candidate["final_formula"])
    if candidate["status"] == "STALLED_RUP_CORE" and max_width(final) > 5:
        raise AssertionError(("R50G20_NONTERMINAL_RUP_FIXPOINT_RETAINS_WIDTH6", final))
    if candidate["status"] == "STALLED_RUP_CORE" and touch is None:
        raise AssertionError("R50G20_COMPLETE_NONTERMINAL_PASS_NEVER_TOUCHED_FULL_CLAUSE")

    return {
        "entry": entry,
        "candidate_status": candidate["status"],
        "successful_strengthenings": int(candidate["successful_strengthenings"]),
        "persistence_checks_before_and_at_touch": persistence_checks,
        "first_wide_clause_touch": touch,
        "final_CLV": list(r33.measure(final)),
        "final_max_width": max_width(final),
        "independent_replay_pass": True,
    }


def r50g18_scope_correction_and_selector_control():
    H0 = canon(r50g18.EXPECTED_CAGE)
    R = r33.canonical_clause(r50g18.R)
    cage = r50g17.six_variable_saturation_cage(H0, R)
    if not cage["all_six_variables_bve_blocked"]:
        raise AssertionError("R50G20_R50G18_ENTRY_CAGE_DRIFT")
    if not all((int(p["p"]), int(p["n"])) == (3, 2) for p in cage["profiles"]):
        raise AssertionError(("R50G20_R50G18_ENTRY_NOT_EXACT_3x2", cage))

    candidate = r35b.run_candidate(H0)
    replay = r35b.independent_certificate_replay(H0, candidate)
    if not replay["pass"]:
        raise AssertionError(("R50G20_R50G18_REPLAY_FAIL", replay))

    state = H0
    touch_state = None
    touch_record = None
    for record in candidate["history"]:
        if tuple(record["source_clause"]) == R and touch_state is None:
            touch_state = state
            touch_record = record
        state = apply_rup_record(state, record)

    if touch_state is None or touch_record is None:
        raise AssertionError("R50G20_R50G18_FULL_CLAUSE_NEVER_TOUCHED")
    profile = r50g17.oriented_profile(touch_state, R, 2)
    expected = {
        "p": 2,
        "n": 1,
        "distinct_nontaut_resolvents": 1,
        "measure_before": [10, 24, 6],
        "measure_after": [8, 16, 5],
    }
    for key, value in expected.items():
        if profile[key] != value:
            raise AssertionError(("R50G20_SCOPE_CORRECTION_DRIFT", key, profile[key], value, profile))
    if not profile["bve_accepted"]:
        raise AssertionError(("R50G20_INTERNAL_Ht_EXPECTED_BVE_OPEN", profile))
    if int(touch_record["step"]) != 7 or int(touch_record["removed_literal"]) != 2:
        raise AssertionError(("R50G20_R50G18_SELECTOR_DRIFT", touch_record))

    full = first_wide_clause_touch(H0, R)
    if full["final_max_width"] > 5:
        raise AssertionError(("R50G20_R50G18_WIDTH_COLLAPSE_FAIL", full))

    return {
        "H0_exact_3x2_all_six": True,
        "internal_touch_step": 7,
        "internal_Ht_literal2_profile": profile,
        "internal_Ht_BVE_already_open": True,
        "scope_correction": "3x2_CERTIFICATE_IS_H0_ONLY_NOT_ARBITRARY_INTERNAL_Ht",
        "selector_and_collapse": full,
    }


def transform_literal(lit: int, mapping, flips):
    old = abs(int(lit))
    sign = 1 if int(lit) > 0 else -1
    if old in flips:
        sign *= -1
    return sign * int(mapping[old])


def transform_formula(formula, mapping, flips):
    return canon([
        tuple(transform_literal(lit, mapping, flips) for lit in clause)
        for clause in canon(formula)
    ])


def transformed_selector_controls():
    base = canon(r50g18.EXPECTED_CAGE)
    R0 = r33.canonical_clause(r50g18.R)
    specs = [
        ("IDENTITY", {v: v for v in range(2, 8)}, set()),
        ("REVERSED_IDS", {2: 7, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2}, set()),
        ("SPARSE_IDS", {2: 13, 3: 2, 4: 11, 5: 5, 6: 17, 7: 7}, set()),
        ("SPARSE_IDS_WITH_SIGN_FLIPS", {2: 19, 3: 3, 4: 23, 5: 11, 6: 5, 7: 17}, {2, 4, 7}),
    ]
    out = []
    for name, mapping, flips in specs:
        f = transform_formula(base, mapping, flips)
        R = r33.canonical_clause(transform_literal(lit, mapping, flips) for lit in R0)
        audit = first_wide_clause_touch(f, R)
        if audit["candidate_status"] != "STALLED_RUP_CORE":
            raise AssertionError(("R50G20_TRANSFORM_CONTROL_UNEXPECTED_TERMINAL", name, audit))
        if audit["final_max_width"] > 5:
            raise AssertionError(("R50G20_TRANSFORM_WIDTH6_SURVIVED", name, audit))
        touch = audit["first_wide_clause_touch"]
        if touch is None or abs(int(touch["removed_literal"])) != min(abs(x) for x in R):
            raise AssertionError(("R50G20_TRANSFORM_SELECTOR_FAIL", name, R, touch))
        out.append({
            "name": name,
            "mapping": {str(k): int(v) for k, v in sorted(mapping.items())},
            "sign_flips_on_old_variables": sorted(int(v) for v in flips),
            "transformed_wide_clause": list(R),
            "audit": audit,
        })
    return out


def v7_corollary_contract():
    boundary = r50g12.v7_boundary_normal_form()
    if boundary["derived_final_variable_count"] != 6 or boundary["derived_final_max_width"] != 5:
        raise AssertionError(("R50G20_R50G12_BOUNDARY_DRIFT", boundary))
    return {
        "prior_closed_boundary": boundary,
        "after_R33_fixed_V6_W6_RUP_entry": "UNSAT_OR_COMPLETE_RUP_FINAL_WIDTH_LE_5",
        "if_later_variable_elimination_occurs": "FINAL_UNSAFE_WIDE_CORE_IMPOSSIBLE_BY_R50G12_V_GE_W_PLUS_1",
        "surviving_unsafe_descendant": {"variables": 6, "max_width": 5},
        "ancestry_firewall": "RUP6_DESCENDED_W5_IS_NOT_AUTOMATICALLY_HISTORICAL_DIRECT5",
    }


def run():
    scope = r50g18_scope_correction_and_selector_control()
    transforms = transformed_selector_controls()
    corollary = v7_corollary_contract()
    return {
        "gate": GATE,
        "mode": "SOURCE_THEOREM_PLUS_FROZEN_IMPLEMENTATION_CONTROLS",
        "proved_from_frozen_source_definitions": [
            "R50G17_3x2_SATURATION_CERTIFICATE_IS_SCOPED_TO_R33_FIXED_RUP_ENTRY_H0",
            "BCE_FIXED_ALL_VARIABLE_WIDTH6_CLAUSE_HAS_NONBLOCKING_R_POLARITY_WITNESS_FOR_EVERY_LITERAL",
            "EVERY_ONE_LITERAL_DELETION_OF_SUCH_A_WIDTH6_CLAUSE_IS_RUP_VALID_AT_H0",
            "UNIT_PROPAGATION_CONFLICT_IS_MONOTONE_UNDER_CLAUSE_STRENGTHENING",
            "UNCHANGED_WIDTH6_CLAUSE_CANNOT_DISAPPEAR_BEFORE_ITS_OWN_RUP_TOUCH_IN_A_SIX_VARIABLE_TAUTOLOGY_FREE_FORMULA",
            "COMPLETE_FROZEN_RUP_PASS_CANNOT_STALL_WITH_ANY_WIDTH6_CLAUSE_UNCHANGED",
            "FIRST_TOUCH_OF_AN_UNCHANGED_WIDTH6_CLAUSE_REMOVES_THE_MINIMUM_VARIABLE_LITERAL_UNDER_FROZEN_lit_key",
            "NONTERMINAL_COMPLETE_RUP_PASS_FROM_R33_FIXED_V6_W6_ENTRY_HAS_FINAL_WIDTH_LE_5",
            "UNSAFE_V7_DESCENDANT_AFTER_SUCH_A_RUP6_PHASE_IS_REDUCED_TO_V6_W5_OR_ELSE_IS_SAFE_TERMINAL",
        ],
        "r50g18_scope_correction_and_selector_control": scope,
        "sign_and_variable_renaming_controls": transforms,
        "v7_corollary": corollary,
        "critical_next_obligation": "ATTACK_THE_SURVIVING_SIX_VARIABLE_WIDTH5_CORE_WITH_ANCESTRY_EXPLICITLY_SPLIT_INTO_DIRECT5_AND_RUP6_DESCENDED_W5__PROVE_CERTIFIED_DOOR_OR_BUILD_EXACT_ALL_DOORS_CLOSED_COUNTEREXAMPLE",
        "verdict": "RUP6_PHASE_ENTRY_WIDTH_COLLAPSE_THEOREM_CLOSED__WIDTH6_CANNOT_BE_TERMINAL_V7_RUP_OBSTRUCTION__UNSAFE_DESCENDANT_REDUCED_TO_V6_W5_CORE",
        "firewall": {
            "FINITE_CONTROLS_ARE_THE_UNIVERSAL_PROOF": False,
            "RUP6_PHASE_ENTRY_WIDTH_COLLAPSE": "PROVED_FROM_FROZEN_SOURCE_DEFINITIONS",
            "RUP6_AS_TERMINAL_WIDTH6_V7_OBSTRUCTION_ELIMINATED": True,
            "V7_UNSAFE_DESCENDANT_AFTER_RUP6": "V6_W5_OR_SAFE",
            "RUP6_DESCENDED_W5_EQUALS_HISTORICAL_DIRECT5": False,
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
