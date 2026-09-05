from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r45a_byte_pinned_ascent_descent_macro as r45a
import janus_trump_r50g4_prefix_closure_microstep_authority as r50g4
import janus_trump_r50g10_wide_fixpoint_forces_alternate_certified_door as r50g10
import janus_trump_r50g15_rup6_hub_bve_blockade_saturation as r50g15
import janus_trump_r50g16_v7_rup6_3x2_ancestry_pullback_door_audit as r50g16

GATE = "JANUS_TRUMP_R50G17_V6_WIDE6_ALL_VARIABLE_BVE_SATURATION_CAGE"


def canon(f):
    return r33.canonical_formula(f)


def resolve_oriented(same_clause, opposite_clause, lit: int):
    u = (set(same_clause) - {int(lit)}) | (set(opposite_clause) - {-int(lit)})
    if any(-x in u for x in u):
        return None
    return r33.canonical_clause(u)


def oriented_profile(formula, wide_clause, lit: int):
    f = canon(formula)
    R = r33.canonical_clause(wide_clause)
    l = int(lit)
    if l not in R:
        raise ValueError("literal must belong to wide clause")
    if len(R) != 6 or len({abs(x) for x in R}) != 6:
        raise ValueError("R50G17 requires an all-variable width-6 clause")
    if R not in f:
        raise ValueError("wide clause must be present in formula")

    same = [c for c in f if l in c]
    opposite = [c for c in f if -l in c]
    if not same or not opposite:
        return {
            "literal": l,
            "p": len(same),
            "n": len(opposite),
            "bipolar": False,
            "saturation_required": False,
        }

    target = r33.canonical_clause(x for x in R if x != l)
    r_row = set()
    row = []
    for d in opposite:
        rr = resolve_oriented(R, d, l)
        if rr is not None:
            if rr != target:
                raise AssertionError(("R50G17_WIDE_ROW_DID_NOT_COLLAPSE", R, l, d, rr, target))
            r_row.add(rr)
        row.append({"opposite_clause": list(d), "resolvent": None if rr is None else list(rr)})
    if len(r_row) > 1:
        raise AssertionError(("R50G17_WIDE_ROW_GT_ONE_DISTINCT", l, row))

    all_rr = sorted({
        rr
        for p in same
        for n in opposite
        for rr in [resolve_oriented(p, n, l)]
        if rr is not None
    })
    removed = set(same + opposite)
    base = [c for c in f if c not in removed]
    transformed = canon(base + all_rr)
    before = r33.measure(f)
    after = r33.measure(transformed)
    accepted = len(all_rr) <= len(removed) and after < before

    p = len(same)
    n = len(opposite)
    r = len(all_rr)
    row_upper = 1 + (p - 1) * n
    if r > row_upper:
        raise AssertionError(("R50G17_COUNTING_UPPER_BOUND_FAIL", l, p, n, r, row_upper))
    if not accepted and r < p + n:
        raise AssertionError(("R50G17_BVE_BLOCKED_WITH_STRICT_CLAUSE_COUNT_DESCENT", l, p, n, r, before, after))

    saturated = p >= 3 and n >= 2
    if not accepted and not saturated:
        raise AssertionError(("R50G17_BLOCKED_BVE_WITHOUT_3x2_SATURATION", l, p, n, r))

    minimal_boundary_requires_row = None
    if p == 3 and n == 2 and not accepted:
        minimal_boundary_requires_row = len(r_row) == 1
        if not minimal_boundary_requires_row:
            raise AssertionError(("R50G17_3x2_BOUNDARY_WITHOUT_WIDE_ROW_RESOLVENT", l, row, all_rr))

    return {
        "literal": l,
        "p": p,
        "n": n,
        "bipolar": True,
        "distinct_nontaut_resolvents": r,
        "wide_row_distinct_nontaut": len(r_row),
        "wide_row": row,
        "row_upper_bound": row_upper,
        "removed_clause_count": len(removed),
        "measure_before": list(before),
        "measure_after": list(after),
        "bve_accepted": bool(accepted),
        "saturated_3x2_or_stronger": saturated,
        "minimal_boundary_requires_wide_row_resolvent": minimal_boundary_requires_row,
    }


def six_variable_saturation_cage(formula, wide_clause):
    f = canon(formula)
    R = r33.canonical_clause(wide_clause)
    if set(r33.variables(f)) != {abs(x) for x in R} or len(R) != 6:
        raise ValueError("formula must have exactly the six variables of R")
    profiles = [oriented_profile(f, R, lit) for lit in R]
    blocked = [p for p in profiles if p.get("bipolar") and not p["bve_accepted"]]
    all_blocked = len(blocked) == 6
    if all_blocked:
        if not all(p["p"] >= 3 and p["n"] >= 2 for p in profiles):
            raise AssertionError("R50G17_SIXFOLD_BLOCKED_WITHOUT_SIXFOLD_SATURATION")
        literal_incidence = sum(len(c) for c in f)
        if literal_incidence < 30:
            raise AssertionError(("R50G17_SIXFOLD_SATURATION_LT30_LITERALS", literal_incidence))
    return {
        "all_six_variables_bve_blocked": all_blocked,
        "profiles": profiles,
        "formula_literal_incidence": sum(len(c) for c in f),
        "theorem_lower_bound_if_all_blocked": 30,
    }


def integer_boundary():
    feasible = []
    for p in range(1, 9):
        for n in range(1, 9):
            if 1 + (p - 1) * n >= p + n:
                feasible.append((p + n, p, n))
    minimum = min(feasible)
    if minimum != (5, 3, 2):
        raise AssertionError(("R50G17_INTEGER_BOUNDARY_DRIFT", minimum))
    return {
        "inequality": "1+(p-1)n >= p+n",
        "equivalent": "(p-2)(n-1) >= 1",
        "minimum_total_occurrences": 5,
        "minimum_oriented_pair": {"p": 3, "n": 2},
    }


def single_variable_boundary_control():
    old = r50g15.minimal_3x2_blockade_control()
    f = canon(old["formula"])
    R = r33.canonical_clause((1, 2, 3, 4, 5, 6))
    profile = oriented_profile(f, R, 6)
    if profile["p"] != 3 or profile["n"] != 2 or profile["bve_accepted"]:
        raise AssertionError(("R50G17_3x2_CONTROL_DRIFT", profile))
    if profile["wide_row_distinct_nontaut"] != 1:
        raise AssertionError(("R50G17_3x2_CONTROL_NO_COLLAPSED_ROW", profile))
    return profile


def r50g16_regression_forensics():
    preclean = 0
    forced_with_wide6 = 0
    all_six_saturated = 0
    first_rule_hist = Counter()
    first_bve_var_hist = Counter()
    terminal_hist = Counter()
    first_unsaturated_hist = Counter()
    saturation_count_hist = Counter()

    for source, _spec in r50g16.candidate_sources():
        f = canon(source)
        if not r50g10.exact_pre_bve_clean(f):
            continue
        direct = r50g4.first_r33_micro_candidate(f)
        if direct["kind"] != "PROPOSAL" or direct.get("rule") != "BOUNDED_VARIABLE_ELIMINATION" or int(direct.get("var", -1)) != 1:
            continue
        preclean += 1
        dp = r45a.exact_dp_record(f, 1)
        if dp is None:
            continue
        forced = canon(dp["transformed"])
        if r50g16.WIDE6 not in forced:
            continue
        forced_with_wide6 += 1

        sat = []
        first_unsat = None
        for lit in r50g16.WIDE6:
            p = oriented_profile(forced, r50g16.WIDE6, int(lit))
            yes = bool(p.get("bipolar") and p["p"] >= 3 and p["n"] >= 2)
            sat.append(yes)
            if not yes and first_unsat is None:
                first_unsat = abs(int(lit))
        saturation_count_hist[sum(sat)] += 1
        if all(sat):
            all_six_saturated += 1
        elif first_unsat is not None:
            first_unsaturated_hist[first_unsat] += 1

        reduced = r33.simplify(forced)
        terminal_hist[str(reduced["terminal"])] += 1
        if reduced["history"]:
            first = reduced["history"][0]
            first_rule_hist[first["rule"]] += 1
            if first["rule"] == "BOUNDED_VARIABLE_ELIMINATION":
                first_bve_var_hist[int(first["var"])] += 1
        else:
            first_rule_hist["NO_R33_HISTORY"] += 1

    return {
        "frozen_family_size": 3024,
        "pre_bve_clean_immediate_x_candidates": preclean,
        "forced_states_retaining_canonical_wide6": forced_with_wide6,
        "all_six_saturated_forced_states": all_six_saturated,
        "first_unsaturated_variable_histogram": {str(k): v for k, v in sorted(first_unsaturated_hist.items())},
        "number_of_saturated_variables_histogram": {str(k): v for k, v in sorted(saturation_count_hist.items())},
        "first_post_DP_R33_rule_histogram": dict(sorted(first_rule_hist.items())),
        "first_post_DP_BVE_variable_histogram": {str(k): v for k, v in sorted(first_bve_var_hist.items())},
        "post_DP_terminal_histogram": dict(sorted(terminal_hist.items())),
        "authority": "FINITE_REGRESSION_ONLY"
    }


def run():
    boundary = integer_boundary()
    control = single_variable_boundary_control()
    regression = r50g16_regression_forensics()
    return {
        "gate": GATE,
        "mode": "SOURCE_COUNTING_THEOREM_PLUS_R50G16_FROZEN_REGRESSION_FORENSICS",
        "proved_from_frozen_source_definitions": [
            "WIDTH6_ALL_VARIABLE_CLAUSE_ROW_COLLAPSES_TO_AT_MOST_ONE_DISTINCT_NONTAUT_RESOLVENT_FOR_EACH_OF_ITS_SIX_LITERALS",
            "BVE_FIXEDNESS_FOR_EACH_VARIABLE_FORCES_P_GE_3_AND_N_GE_2_ORIENTED_TO_THE_WIDE6_LITERAL",
            "SIXFOLD_BVE_FIXEDNESS_FORCES_EVERY_VARIABLE_OCCURRENCE_DEGREE_AT_LEAST_5",
            "SIXFOLD_BVE_FIXEDNESS_FORCES_TOTAL_LITERAL_INCIDENCE_AT_LEAST_30",
            "AT_EXACT_3x2_BOUNDARY_THE_WIDE6_ROW_MUST_SUPPLY_ITS_ONE_NONTAUT_RESOLVENT"
        ],
        "integer_boundary": boundary,
        "minimal_3x2_control": control,
        "r50g16_regression_forensics": regression,
        "critical_next_obligation": "PULL_THE_SIMULTANEOUS_SIX_VARIABLE_3x2_OR_STRONGER_SATURATION_CAGE_BACK_THROUGH_V7_W4_DP_ANCESTRY_AND_FORCE_AN_ALTERNATE_CERTIFIED_DOOR_OR_BUILD_AN_EXPLICIT_FULL_CAGE_REALIZER",
        "verdict": "SIXFOLD_BVE_SATURATION_CAGE_THEOREM_CLOSED__V7_RUP6_UNSAFE_TRACE_REQUIRES_AT_LEAST_30_PRE_RUP_LITERAL_INCIDENCES__FULL_CAGE_ANCESTRY_OPEN",
        "firewall": {
            "SIXFOLD_SATURATION_IMPLIES_V7_IMPOSSIBILITY": False,
            "RUP_BEARING_V7_HUB_CYCLE_ELIMINATED": False,
            "V7_IMMEDIATE_BVE_CASE_ELIMINATED": False,
            "IMMEDIATE_BVE_CASE_ELIMINATED": False,
            "U_MU": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_EQ_NP": "NOT_PROVED",
            "P_NE_NP": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False
        }
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
