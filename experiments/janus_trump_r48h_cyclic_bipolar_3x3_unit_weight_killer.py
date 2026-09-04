from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r34_affine_xor_terminal_against_tseitin_core as r34
import janus_trump_r35b_single_literal_rup_vivification as r35b
import janus_trump_r42_subsumption_aware_bve_successor as r42
import janus_trump_r47f_small_reachable_fixpoint_full_macro_falsifier as r47f
import janus_trump_r47m_post_dp_full_existing_stack_closure as r47m
import janus_trump_r48d_minimum_local_amortized_pressure_controller as r48d

GATE = "JANUS_TRUMP_R48H_CYCLIC_BIPOLAR_3X3_UNIT_WEIGHT_KILLER"
N_VALUES = (13, 17, 19, 23)


def canon(formula):
    return r33.canonical_formula(formula)


def clv(formula):
    return r33.measure(canon(formula))


def formula_hash(formula):
    return r47f.formula_hash(canon(formula))


def x(i: int, n: int) -> int:
    return (i % n) + 1


def cyclic_bipolar_3x3(n: int):
    clauses = []
    for i in range(n):
        clauses.append((x(i, n), x(i + 1, n), x(i + 3, n)))
        clauses.append((-x(i, n), -x(i + 4, n), -x(i + 9, n)))
    f = canon(clauses)
    if len(f) != 2 * n:
        raise AssertionError(("R48H_CLAUSE_COUNT_DRIFT", n, len(f), 2 * n))
    if clv(f) != (2 * n, 6 * n, n):
        raise AssertionError(("R48H_CLV_DRIFT", n, clv(f)))
    if any(len(c) != 3 for c in f):
        raise AssertionError(("R48H_NOT_EXACT_3CNF", n))
    if any(r33.is_tautology(c) for c in f):
        raise AssertionError(("R48H_TAUTOLOGY_IN_GENERATOR", n))
    return f


def structural_pivot_row(formula, var):
    f = canon(formula)
    pos, neg, resolvents, pair_checks = r42.all_dp_resolvents(f, int(var))
    overlaps = []
    tautological_pair_count = 0
    manual_non_taut = set()
    for p in pos:
        for q in neg:
            inter = sorted(set(abs(l) for l in p) & set(abs(l) for l in q))
            if inter != [int(var)]:
                overlaps.append({"positive": list(p), "negative": list(q), "support_intersection": inter})
            raw = (set(p) - {int(var)}) | (set(q) - {-int(var)})
            if any(-lit in raw for lit in raw):
                tautological_pair_count += 1
                continue
            manual_non_taut.add(r33.canonical_clause(raw))
    if tuple(sorted(manual_non_taut)) != tuple(sorted(resolvents)):
        raise AssertionError(("R48H_RESOLVENT_RECONSTRUCTION_DRIFT", var))
    base = tuple(c for c in f if int(var) not in c and -int(var) not in c)
    pool = canon(list(base) + list(resolvents))
    raw_delta_c = len(pool) - len(f)
    raw_delta_l = clv(pool)[1] - clv(f)[1]
    resolvents_already_in_base = [list(r) for r in resolvents if r in base]
    return {
        "var": int(var),
        "positive_parent_count": len(pos),
        "negative_parent_count": len(neg),
        "pair_checks": int(pair_checks),
        "cross_polarity_second_variable_overlap_count": len(overlaps),
        "cross_polarity_overlap_examples": overlaps[:5],
        "tautological_pair_count": int(tautological_pair_count),
        "distinct_non_tautological_resolvent_count": len(resolvents),
        "resolvents_already_in_unaffected_base_count": len(resolvents_already_in_base),
        "forced_pool_CLV_before_subsumption": list(clv(pool)),
        "raw_delta_C_before_subsumption": int(raw_delta_c),
        "raw_delta_L_before_subsumption": int(raw_delta_l),
        "clean_3x3_geometry": bool(
            len(pos) == 3
            and len(neg) == 3
            and pair_checks == 9
            and not overlaps
            and tautological_pair_count == 0
            and len(resolvents) == 9
            and not resolvents_already_in_base
            and raw_delta_c == 3
        ),
    }


def structural_precheck(formula):
    rows = [structural_pivot_row(formula, v) for v in r33.variables(formula)]
    return {
        "all_variables_p3_n3": all(r["positive_parent_count"] == 3 and r["negative_parent_count"] == 3 for r in rows),
        "all_pair_checks_9": all(r["pair_checks"] == 9 for r in rows),
        "all_cross_polarity_overlap_free": all(r["cross_polarity_second_variable_overlap_count"] == 0 for r in rows),
        "all_tautological_pair_count_zero": all(r["tautological_pair_count"] == 0 for r in rows),
        "all_distinct_resolvents_9": all(r["distinct_non_tautological_resolvent_count"] == 9 for r in rows),
        "all_resolvents_new_vs_base": all(r["resolvents_already_in_unaffected_base_count"] == 0 for r in rows),
        "all_raw_delta_C_plus_3": all(r["raw_delta_C_before_subsumption"] == 3 for r in rows),
        "all_clean_3x3_geometry": all(r["clean_3x3_geometry"] for r in rows),
        "pivot_rows": rows,
    }


def verify_joint_fixpoint(formula):
    f = canon(formula)
    simp = r33.simplify(f)
    after_r33 = canon(simp["final_formula"])
    affine = r34.recognize_complete_affine_cnf(after_r33)
    rup = r35b.run_candidate(after_r33)
    rup_replay = r35b.independent_certificate_replay(after_r33, rup)
    if not rup_replay["pass"]:
        raise AssertionError("R48H_RUP_REPLAY_FAIL")
    after_rup = canon(rup["final_formula"])
    bve, bve_ledger = r42.best_sa_bve_candidate(after_rup)
    passed = (
        simp["terminal"] == "STALLED_STACK_LEAN_CORE"
        and simp["total_rule_applications"] == 0
        and after_r33 == f
        and not affine["recognized"]
        and rup["status"] != "UNSAT_BY_UNIT_PROPAGATION"
        and len(rup.get("history", [])) == 0
        and after_rup == f
        and bve is None
    )
    return {
        "pass": bool(passed),
        "R33_terminal": simp["terminal"],
        "R33_rule_applications": int(simp["total_rule_applications"]),
        "affine_recognized": bool(affine["recognized"]),
        "affine_reason": affine.get("reason"),
        "RUP_status": rup["status"],
        "RUP_history_count": len(rup.get("history", [])),
        "RUP_independent_replay_pass": bool(rup_replay["pass"]),
        "SA_BVE_candidate_present": bve is not None,
        "SA_BVE_variables_checked": int(bve_ledger["variables_checked"]),
    }


def scan_pressure_state(state):
    state = canon(state)
    rows = []
    candidates = {}
    for var in r33.variables(state):
        candidate = r47m.macro_candidate_full_closure(state, int(var))
        if candidate is None:
            rows.append({"var": int(var), "candidate": False, "eligible": False, "terminal": None, "a_req": None})
            continue
        if not candidate["DP_independent_replay_pass"]:
            raise AssertionError(("R48H_DP_REPLAY_FAIL", var))
        if not candidate["polynomial_intermediate_envelope_pass"]:
            raise AssertionError(("R48H_POLY_ENVELOPE_FAIL", var))
        row = r48d.candidate_row(state, candidate, None)
        rows.append(row)
        candidates[int(var)] = candidate
    eligible = [r for r in rows if r.get("eligible", False)]
    terminals = [r for r in eligible if r["terminal"] is not None]
    nonterm = [r for r in eligible if r["terminal"] is None and r["a_req"] is not None]
    a_star = 0 if terminals else (min(int(r["a_req"]) for r in nonterm) if nonterm else None)
    return rows, candidates, eligible, terminals, nonterm, a_star


def replay_all(state, rows, candidates):
    replayed = []
    for row in rows:
        var = int(row["var"])
        candidate = candidates.get(var)
        if candidate is None:
            replayed.append(row)
            continue
        replay = r47m.independent_replay(state, candidate)
        if not replay["pass"]:
            raise AssertionError(("R48H_COUNTEREXAMPLE_FULL_REPLAY_FAIL", var, replay))
        replayed.append(r48d.candidate_row(state, candidate, True))
    return replayed


def run_one(n):
    raw = cyclic_bipolar_3x3(n)
    structure = structural_precheck(raw)
    normalized = r47m.normalize_full_existing_stack(raw)
    residual = canon(normalized["final_formula"])
    row = {
        "n": int(n),
        "raw_hash": formula_hash(raw),
        "raw_CLV": list(clv(raw)),
        "structural_precheck": structure,
        "preprojection_normalization": {
            "segment_count": int(normalized["segment_count"]),
            "SA_BVE_application_count": int(normalized["SA_BVE_application_count"]),
            "terminal": normalized["terminal"],
            "semantic_sat": normalized["semantic_sat"],
            "final_hash": formula_hash(residual),
            "final_CLV": list(clv(residual)),
        },
    }
    if normalized["terminal"] is not None:
        row["classification"] = "TERMINAL_BY_EXISTING_STACK_BEFORE_PRESSURE_ATTACK"
        row["pressure_attack"] = None
        return row, None

    integrity = verify_joint_fixpoint(residual)
    if not integrity["pass"]:
        raise AssertionError(("R48H_NONTERMINAL_NOT_JOINT_FIXPOINT", n, integrity))
    rows, candidates, eligible, terminals, nonterm, a_star = scan_pressure_state(residual)
    pressure = {
        "residual_hash": formula_hash(residual),
        "residual_CLV": list(clv(residual)),
        "joint_fixpoint_integrity": integrity,
        "candidate_count": len(rows),
        "eligible_count": len(eligible),
        "terminal_candidate_count": len(terminals),
        "a_star": a_star,
        "candidate_rows": rows,
    }
    row["classification"] = "NONTERMINAL_JOINT_FIXPOINT_PRESSURE_MEASURED"
    row["pressure_attack"] = pressure

    if not terminals and (a_star is None or int(a_star) >= 2):
        replayed = replay_all(residual, rows, candidates)
        replay_eligible = [r for r in replayed if r.get("eligible", False)]
        replay_terminals = [r for r in replay_eligible if r["terminal"] is not None]
        replay_nonterm = [r for r in replay_eligible if r["terminal"] is None and r["a_req"] is not None]
        if replay_terminals:
            raise AssertionError(("R48H_COUNTEREXAMPLE_REPLAY_FOUND_TERMINAL", n))
        if a_star is None:
            if replay_eligible:
                raise AssertionError(("R48H_NO_CANDIDATE_REPLAY_FOUND_ELIGIBLE", n))
            kind = "NO_VARIABLE_DECREASING_CANDIDATE"
            replay_a_star = None
        else:
            if not replay_nonterm:
                raise AssertionError(("R48H_ASTAR_REPLAY_LOST_NONTERMINAL", n))
            replay_a_star = min(int(r["a_req"]) for r in replay_nonterm)
            if replay_a_star < 2:
                raise AssertionError(("R48H_ASTAR_REPLAY_DROPPED", n, replay_a_star))
            kind = "A_STAR_GE_2"
        counterexample = {
            "kind": kind,
            "n": int(n),
            "raw_hash": formula_hash(raw),
            "raw_CLV": list(clv(raw)),
            "raw_formula": [list(c) for c in raw],
            "residual_hash": formula_hash(residual),
            "residual_CLV": list(clv(residual)),
            "residual_formula": [list(c) for c in residual],
            "a_star": replay_a_star,
            "candidate_rows": replayed,
            "joint_fixpoint_integrity": integrity,
        }
        row["pressure_attack"]["candidate_rows"] = replayed
        row["pressure_attack"]["a_star"] = replay_a_star
        return row, counterexample
    return row, None


def run():
    rows = []
    counterexample = None
    for n in N_VALUES:
        row, found = run_one(n)
        rows.append(row)
        if found is not None:
            counterexample = found
            break
    if counterexample is None:
        verdict = "ALL_FROZEN_CYCLIC_BIPOLAR_INSTANCES_HAVE_a_star_LE_1_OR_TERMINAL__FINITE_ONLY"
    elif counterexample["kind"] == "NO_VARIABLE_DECREASING_CANDIDATE":
        verdict = "STRONGER_CYCLIC_BIPOLAR_NO_VARIABLE_DECREASING_R47M_CANDIDATE_FOUND"
    else:
        verdict = "EXPLICIT_CYCLIC_BIPOLAR_UNIT_WEIGHT_COUNTEREXAMPLE_a_star_GE_2_FOUND"
    return {
        "gate": GATE,
        "verdict": verdict,
        "n_values_frozen": list(N_VALUES),
        "rows": rows,
        "sealed_counterexample": counterexample,
        "interpretation": {
            "explicit_family_not_random_search": True,
            "clean_raw_3x3_pressure_alone_is_not_counterexample": True,
            "full_R47M_normalized_successor_authority_decisive": True,
            "finite_no_counterexample_proves_unit_weight_coverage": False,
            "explicit_a_star_ge_2_refutes_unit_weight_special_case_only": True,
            "explicit_a_star_ge_2_refutes_general_polynomial_a_route": False,
        },
        "firewall": {
            "UNIVERSAL_UNIT_WEIGHT_COVERAGE": "NOT_PROVED",
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
    d = run()
    if args.output:
        p = Path(args.output)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(d, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    compact_rows = []
    for r in d["rows"]:
        p = r["pressure_attack"]
        compact_rows.append({
            "n": r["n"],
            "raw_CLV": r["raw_CLV"],
            "all_clean_3x3_geometry": r["structural_precheck"]["all_clean_3x3_geometry"],
            "all_raw_delta_C_plus_3": r["structural_precheck"]["all_raw_delta_C_plus_3"],
            "preprojection_terminal": r["preprojection_normalization"]["terminal"],
            "preprojection_final_CLV": r["preprojection_normalization"]["final_CLV"],
            "classification": r["classification"],
            "pressure": None if p is None else {
                "residual_hash": p["residual_hash"],
                "residual_CLV": p["residual_CLV"],
                "terminal_candidate_count": p["terminal_candidate_count"],
                "eligible_count": p["eligible_count"],
                "a_star": p["a_star"],
            },
        })
    c = d["sealed_counterexample"]
    print(json.dumps({
        "gate": d["gate"],
        "verdict": d["verdict"],
        "rows": compact_rows,
        "sealed_counterexample": None if c is None else {
            "kind": c["kind"],
            "n": c["n"],
            "raw_hash": c["raw_hash"],
            "raw_CLV": c["raw_CLV"],
            "residual_hash": c["residual_hash"],
            "residual_CLV": c["residual_CLV"],
            "a_star": c["a_star"],
            "candidate_rows": c["candidate_rows"],
        },
        "firewall": d["firewall"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
