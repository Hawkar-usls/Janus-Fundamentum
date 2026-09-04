from __future__ import annotations

import argparse
import json
from itertools import combinations
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r42_subsumption_aware_bve_successor as r42
import janus_trump_r47f_small_reachable_fixpoint_full_macro_falsifier as r47f
import janus_trump_r47m_post_dp_full_existing_stack_closure as r47m
import janus_trump_r48d_minimum_local_amortized_pressure_controller as r48d
import janus_trump_r48h_cyclic_bipolar_3x3_unit_weight_killer as r48h

GATE = "JANUS_TRUMP_R48I_CYCLIC_BIPOLAR_RXR_PRESSURE_SCALING_LAW"
R_VALUES = (3, 6, 9)


def canon(formula):
    return r33.canonical_formula(formula)


def clv(formula):
    return r33.measure(canon(formula))


def formula_hash(formula):
    return r47f.formula_hash(canon(formula))


def directed_differences(starter, n):
    return {
        (int(a) - int(b)) % int(n)
        for a in starter
        for b in starter
        if int(a) != int(b)
    }


def select_starters(n: int, r: int):
    if r % 3 != 0:
        raise ValueError("r must be divisible by 3")
    need = 2 * (r // 3)
    selected = []
    used = set()
    for a, b in combinations(range(1, n), 2):
        starter = (0, int(a), int(b))
        diffs = directed_differences(starter, n)
        if len(diffs) != 6:
            continue
        if diffs & used:
            continue
        selected.append(starter)
        used |= diffs
        if len(selected) == need:
            break
    return selected, used


def translated_clause(starter, shift, n, sign):
    vars_ = [((int(shift) + int(off)) % int(n)) + 1 for off in starter]
    return tuple(int(sign) * int(v) for v in vars_)


def cyclic_bipolar_rxr(r: int):
    n = 8 * int(r) + 1
    q = int(r) // 3
    starters, used = select_starters(n, r)
    if len(starters) != 2 * q:
        return None, {
            "r": int(r),
            "n": int(n),
            "required_starters": int(2 * q),
            "selected_starters": [list(s) for s in starters],
            "failure": "INSUFFICIENT_PAIRWISE_DISJOINT_DIRECTED_DIFFERENCE_STARTERS",
        }
    positive = starters[:q]
    negative = starters[q:]
    clauses = []
    for starter in positive:
        for shift in range(n):
            clauses.append(translated_clause(starter, shift, n, +1))
    for starter in negative:
        for shift in range(n):
            clauses.append(translated_clause(starter, shift, n, -1))
    f = canon(clauses)
    expected_c = 2 * n * int(r) // 3
    if len(f) != expected_c:
        raise AssertionError(("R48I_CLAUSE_COUNT_DRIFT", r, n, len(f), expected_c))
    if any(len(c) != 3 or r33.is_tautology(c) for c in f):
        raise AssertionError(("R48I_NOT_CLEAN_EXACT_3CNF", r, n))
    return f, {
        "r": int(r),
        "n": int(n),
        "q": int(q),
        "positive_starters": [list(s) for s in positive],
        "negative_starters": [list(s) for s in negative],
        "selected_starter_count": len(starters),
        "used_directed_difference_count": len(used),
        "pairwise_difference_disjoint": True,
        "expected_clause_count": int(expected_c),
    }


def structural_pivot_row(formula, var, r):
    f = canon(formula)
    pos, neg, resolvents, pair_checks = r42.all_dp_resolvents(f, int(var))
    overlaps = 0
    tautological = 0
    for p in pos:
        for q in neg:
            inter = set(abs(x) for x in p) & set(abs(x) for x in q)
            if inter != {int(var)}:
                overlaps += 1
            raw = (set(p) - {int(var)}) | (set(q) - {-int(var)})
            if any(-lit in raw for lit in raw):
                tautological += 1
    base = tuple(c for c in f if int(var) not in c and -int(var) not in c)
    pool = canon(list(base) + list(resolvents))
    dc = int(len(pool) - len(f))
    dl = int(clv(pool)[1] - clv(f)[1])
    expected_dc = int(r * (r - 2))
    expected_dl = int(4 * r * r - 6 * r)
    return {
        "var": int(var),
        "positive_parent_count": len(pos),
        "negative_parent_count": len(neg),
        "pair_checks": int(pair_checks),
        "cross_polarity_nonpivot_overlap_count": int(overlaps),
        "tautological_pair_count": int(tautological),
        "distinct_non_tautological_resolvent_count": len(resolvents),
        "raw_delta_C_before_subsumption": dc,
        "raw_delta_L_before_subsumption": dl,
        "expected_raw_delta_C": expected_dc,
        "expected_raw_delta_L": expected_dl,
        "law_pass": bool(
            len(pos) == r
            and len(neg) == r
            and pair_checks == r * r
            and overlaps == 0
            and tautological == 0
            and len(resolvents) == r * r
            and dc == expected_dc
            and dl == expected_dl
        ),
    }


def structural_profile(formula, r):
    rows = [structural_pivot_row(formula, v, int(r)) for v in r33.variables(formula)]
    return {
        "pivot_count": len(rows),
        "all_pivots_raw_pressure_law_pass": all(x["law_pass"] for x in rows),
        "raw_delta_C_expected": int(r * (r - 2)),
        "raw_delta_L_expected": int(4 * r * r - 6 * r),
        "pivot_rows": rows,
    }


def replay_pressure(state):
    rows, candidates, eligible, terminals, nonterm, a_star = r48h.scan_pressure_state(state)
    replayed = r48h.replay_all(state, rows, candidates)
    replay_eligible = [x for x in replayed if x.get("eligible", False)]
    replay_terminals = [x for x in replay_eligible if x.get("terminal") is not None]
    replay_nonterm = [
        x for x in replay_eligible
        if x.get("terminal") is None and x.get("a_req") is not None
    ]
    replay_a_star = 0 if replay_terminals else (
        min(int(x["a_req"]) for x in replay_nonterm) if replay_nonterm else None
    )
    if replay_a_star != a_star:
        raise AssertionError(("R48I_ASTAR_REPLAY_DRIFT", a_star, replay_a_star))
    return replayed, replay_eligible, replay_terminals, replay_nonterm, replay_a_star


def run_one(r):
    raw, construction = cyclic_bipolar_rxr(int(r))
    if raw is None:
        return {
            "r": int(r),
            "n": int(8 * r + 1),
            "classification": "CONSTRUCTION_GEOMETRY_FAIL",
            "construction": construction,
        }
    structure = structural_profile(raw, int(r))
    if not structure["all_pivots_raw_pressure_law_pass"]:
        return {
            "r": int(r),
            "n": int(8 * r + 1),
            "classification": "CONSTRUCTION_GEOMETRY_FAIL",
            "construction": construction,
            "raw_hash": formula_hash(raw),
            "raw_CLV": list(clv(raw)),
            "structural_profile": structure,
        }

    normalized = r47m.normalize_full_existing_stack(raw)
    residual = canon(normalized["final_formula"])
    out = {
        "r": int(r),
        "n": int(8 * r + 1),
        "classification": None,
        "construction": construction,
        "raw_hash": formula_hash(raw),
        "raw_CLV": list(clv(raw)),
        "structural_profile": structure,
        "preprojection_normalization": {
            "terminal": normalized["terminal"],
            "semantic_sat": normalized["semantic_sat"],
            "segment_count": int(normalized["segment_count"]),
            "SA_BVE_application_count": int(normalized["SA_BVE_application_count"]),
            "final_hash": formula_hash(residual),
            "final_CLV": list(clv(residual)),
        },
    }
    if normalized["terminal"] is not None:
        out["classification"] = "TERMINAL_BEFORE_PRESSURE_SCAN"
        out["pressure"] = None
        return out

    integrity = r48h.verify_joint_fixpoint(residual)
    if not integrity["pass"]:
        raise AssertionError(("R48I_RESIDUAL_NOT_JOINT_FIXPOINT", r, integrity))
    replayed, eligible, terminals, nonterm, a_star = replay_pressure(residual)
    residual_C = clv(residual)[0]
    normalized_delta_cs = [int(x["final_CLV"][0]) - int(residual_C) for x in nonterm]
    minimum_normalized_delta_C = min(normalized_delta_cs) if normalized_delta_cs else None
    raw_dc = int(structure["raw_delta_C_expected"])
    repayment = None if minimum_normalized_delta_C is None else int(raw_dc - minimum_normalized_delta_C)
    pressure = {
        "joint_fixpoint_integrity": integrity,
        "candidate_count": len(replayed),
        "eligible_count": len(eligible),
        "terminal_candidate_count": len(terminals),
        "a_star": a_star,
        "minimum_a_req": min((int(x["a_req"]) for x in nonterm), default=None),
        "maximum_a_req": max((int(x["a_req"]) for x in nonterm), default=None),
        "minimum_normalized_delta_C": minimum_normalized_delta_C,
        "raw_delta_C": raw_dc,
        "normalization_repayment_against_best_nonterminal_candidate": repayment,
        "a_star_over_raw_delta_C": None if a_star is None or raw_dc == 0 else float(a_star) / float(raw_dc),
        "candidate_rows": replayed,
    }
    out["pressure"] = pressure
    if not eligible:
        out["classification"] = "NO_VARIABLE_DECREASING_CANDIDATE"
    elif terminals:
        out["classification"] = "TERMINAL_CANDIDATE_EXISTS"
    else:
        out["classification"] = "NONTERMINAL_PRESSURE_MEASURED"
    return out


def run():
    rows = []
    geometry_failed = False
    strongest_no_candidate = False
    normalized_astars = []
    for r in R_VALUES:
        row = run_one(int(r))
        rows.append(row)
        if row["classification"] == "CONSTRUCTION_GEOMETRY_FAIL":
            geometry_failed = True
            break
        if row["classification"] == "NO_VARIABLE_DECREASING_CANDIDATE":
            strongest_no_candidate = True
            break
        p = row.get("pressure")
        if p is not None and p.get("a_star") is not None:
            normalized_astars.append(int(p["a_star"]))

    if geometry_failed:
        verdict = "RAW_RXR_CONSTRUCTION_GEOMETRY_FAILS_AT_FROZEN_PARAMETER"
    elif strongest_no_candidate:
        verdict = "STRONGER_NO_VARIABLE_DECREASING_CANDIDATE_FOUND"
    elif normalized_astars and max(normalized_astars) >= 3:
        verdict = "RAW_RXR_PRESSURE_LAW_CONFIRMED_WITH_NORMALIZED_PRESSURE_GROWTH_SIGNAL"
    else:
        verdict = "RAW_RXR_PRESSURE_LAW_CONFIRMED_BUT_FULL_NORMALIZATION_COLLAPSES_PRESSURE"

    return {
        "gate": GATE,
        "verdict": verdict,
        "r_values_frozen": list(R_VALUES),
        "rows": rows,
        "summary": {
            "all_completed_structural_rows_pass": all(
                x.get("classification") == "CONSTRUCTION_GEOMETRY_FAIL"
                or x.get("structural_profile", {}).get("all_pivots_raw_pressure_law_pass", False)
                for x in rows
            ),
            "normalized_a_stars": normalized_astars,
            "maximum_observed_normalized_a_star": max(normalized_astars) if normalized_astars else None,
            "strict_growth_observed_across_measured_nonterminal_rows": all(
                normalized_astars[i] < normalized_astars[i + 1]
                for i in range(len(normalized_astars) - 1)
            ) if len(normalized_astars) >= 2 else False,
        },
        "interpretation": {
            "raw_symbolic_law_is_separate_from_finite_measurement": True,
            "finite_r_ladder_proves_unbounded_a_star": False,
            "finite_r_ladder_proves_polynomial_a_star": False,
            "raw_pressure_growth_alone_refutes_polynomial_a_route": False,
            "full_R47M_normalized_successor_authority_decisive": True,
        },
        "firewall": {
            "UNIVERSAL_FIXED_a_LE_2_COVERAGE": "REFUTED_BY_R48G",
            "UNIVERSAL_POLYNOMIAL_a_EXISTS": "NOT_PROVED",
            "UNIVERSAL_POLYNOMIAL_ENVELOPE_COVERAGE": "OPEN",
            "O4_UNIVERSAL_COVERAGE": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_EQ_NP": "NOT_PROVED",
            "P_NE_NP": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    args = parser.parse_args()
    result = run()
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    compact = {
        "gate": result["gate"],
        "verdict": result["verdict"],
        "r_values_frozen": result["r_values_frozen"],
        "summary": result["summary"],
        "rows": [
            {
                "r": x["r"],
                "n": x["n"],
                "classification": x["classification"],
                "raw_CLV": x.get("raw_CLV"),
                "raw_delta_C": x.get("structural_profile", {}).get("raw_delta_C_expected"),
                "raw_law_pass": x.get("structural_profile", {}).get("all_pivots_raw_pressure_law_pass"),
                "normalized_final_CLV": x.get("preprojection_normalization", {}).get("final_CLV"),
                "preprojection_terminal": x.get("preprojection_normalization", {}).get("terminal"),
                "a_star": None if x.get("pressure") is None else x["pressure"].get("a_star"),
                "min_normalized_delta_C": None if x.get("pressure") is None else x["pressure"].get("minimum_normalized_delta_C"),
                "normalization_repayment": None if x.get("pressure") is None else x["pressure"].get("normalization_repayment_against_best_nonterminal_candidate"),
            }
            for x in result["rows"]
        ],
        "firewall": result["firewall"],
    }
    print(json.dumps(compact, sort_keys=True))


if __name__ == "__main__":
    main()
