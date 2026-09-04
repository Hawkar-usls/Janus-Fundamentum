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

GATE = "JANUS_TRUMP_R47AD_STANDARD_3CNF_PIGEONHOLE_FULL_STACK_INTAKE"
PHP_NS = (2, 3, 4, 5, 6, 7)
TSEITIN_NS = (8, 12, 16)


def canon(formula):
    return r33.canonical_formula(formula)


def clv(formula):
    return r33.measure(canon(formula))


def formula_hash(formula):
    return r47f.formula_hash(canon(formula))


def standard_php_3cnf(n: int):
    if n < 1:
        raise ValueError(n)
    next_var = 1
    p = {}
    for i in range(1, n + 2):
        for j in range(1, n + 1):
            p[(i, j)] = next_var
            next_var += 1
    y = {}
    for i in range(1, n + 2):
        for j in range(0, n + 1):
            y[(i, j)] = next_var
            next_var += 1

    clauses = []
    for i in range(1, n + 2):
        clauses.append((-y[(i, 0)],))
        for j in range(1, n + 1):
            clauses.append((y[(i, j - 1)], p[(i, j)], -y[(i, j)]))
        clauses.append((y[(i, n)],))

    for i in range(1, n + 2):
        for k in range(i + 1, n + 2):
            for j in range(1, n + 1):
                clauses.append((-p[(i, j)], -p[(k, j)]))

    f = canon(clauses)
    expected_p = n * (n + 1)
    expected_y = (n + 1) * (n + 1)
    expected_vars = expected_p + expected_y
    expected_ep_clauses = (n + 1) * (n + 2)
    expected_collision = n * ((n + 1) * n // 2)
    expected_clauses = expected_ep_clauses + expected_collision
    if len(r33.variables(f)) != expected_vars:
        raise AssertionError(("R47AD_PHP_VAR_COUNT_DRIFT", n, len(r33.variables(f)), expected_vars))
    if len(f) != expected_clauses:
        raise AssertionError(("R47AD_PHP_CLAUSE_COUNT_DRIFT", n, len(f), expected_clauses))
    if any(len(c) > 3 or len(c) < 1 for c in f):
        raise AssertionError(("R47AD_NOT_3CNF", n))
    if any(len(set(abs(l) for l in c)) != len(c) for c in f):
        raise AssertionError(("R47AD_REPEATED_VAR_CLAUSE", n))
    return f, {
        "holes": n,
        "pigeons": n + 1,
        "p_variables": expected_p,
        "y_variables": expected_y,
        "total_variables": expected_vars,
        "EP_clauses": expected_ep_clauses,
        "collision_clauses": expected_collision,
        "total_clauses": expected_clauses,
    }


def verify_php_encoding_structure(n: int, formula):
    expected, counts = standard_php_3cnf(n)
    passed = canon(formula) == expected
    return {
        "pass": passed,
        "counts": counts,
        "logical_contract": "Each EP_i chain with not-y_i0 and y_in forces at least one p_i,j; all pairwise same-hole collision clauses enforce an injection of n+1 pigeons into n holes, which is impossible.",
    }


def verify_nonterminal_joint_fixpoint(formula):
    f = canon(formula)
    r33_result = r33.simplify(f)
    after_r33 = canon(r33_result["final_formula"])
    affine = r34.recognize_complete_affine_cnf(after_r33)
    rup = r35b.run_candidate(after_r33)
    rup_replay = r35b.independent_certificate_replay(after_r33, rup)
    if not rup_replay["pass"]:
        raise AssertionError("R47AD_RUP_REPLAY_FAIL")
    after_rup = canon(rup["final_formula"])
    bve, bve_ledger = r42.best_sa_bve_candidate(after_rup)
    passed = (
        r33_result["terminal"] == "STALLED_STACK_LEAN_CORE"
        and r33_result["total_rule_applications"] == 0
        and after_r33 == f
        and not affine["recognized"]
        and rup["status"] != "UNSAT_BY_UNIT_PROPAGATION"
        and not rup.get("history", [])
        and after_rup == f
        and bve is None
    )
    return {
        "pass": passed,
        "R33_terminal": r33_result["terminal"],
        "R33_rule_applications": int(r33_result["total_rule_applications"]),
        "affine_recognized": bool(affine["recognized"]),
        "affine_reason": affine.get("reason"),
        "RUP_status": rup["status"],
        "RUP_history_count": len(rup.get("history", [])),
        "RUP_independent_replay_pass": bool(rup_replay["pass"]),
        "SA_BVE_candidate_present": bve is not None,
        "SA_BVE_variables_checked": int(bve_ledger["variables_checked"]),
    }


def run_tseitin_negative_controls():
    rows = []
    for n in TSEITIN_NS:
        f = canon(r33.prism_tseitin(n))
        policy = r34.apply_extended_policy(f)
        row = {
            "n_vertices": n,
            "input_hash": formula_hash(f),
            "input_CLV": list(clv(f)),
            "terminal": policy["terminal"],
            "recognized": bool(policy.get("recognition", {}).get("recognized", False)),
            "equation_count": policy.get("recognition", {}).get("equation_count"),
            "solution_sat": policy.get("solution", {}).get("sat"),
            "certificate_pass": policy.get("verification", {}).get("pass"),
            "certificate_kind": policy.get("verification", {}).get("kind"),
        }
        if not (
            row["terminal"] == "AFFINE_XOR_UNSAT"
            and row["recognized"]
            and row["solution_sat"] is False
            and row["certificate_pass"] is True
        ):
            raise AssertionError(("R47AD_TSEITIN_NEGATIVE_CONTROL_FAIL", row))
        rows.append(row)
    return rows


def run():
    tseitin = run_tseitin_negative_controls()
    php_rows = []
    first_fixpoint = None

    for n in PHP_NS:
        f, counts = standard_php_3cnf(n)
        structure = verify_php_encoding_structure(n, f)
        if not structure["pass"]:
            raise AssertionError(("R47AD_PHP_STRUCTURE_FAIL", n))

        normalization = r47m.normalize_full_existing_stack(f)
        final_formula = canon(normalization["final_formula"])
        row = {
            "n_holes": n,
            "n_pigeons": n + 1,
            "generator_counts": counts,
            "input_hash": formula_hash(f),
            "input_CLV": list(clv(f)),
            "segment_count": int(normalization["segment_count"]),
            "SA_BVE_application_count": int(normalization["SA_BVE_application_count"]),
            "terminal": normalization["terminal"],
            "semantic_sat": normalization["semantic_sat"],
            "terminal_verification": normalization["terminal_verification"],
            "final_hash": formula_hash(final_formula),
            "final_CLV": list(clv(final_formula)),
        }

        if normalization["terminal"] is not None:
            if normalization["semantic_sat"] is not False:
                raise AssertionError(("R47AD_UNSAT_PHP_RETURNED_NONUNSAT_TERMINAL", n, normalization["terminal"], normalization["semantic_sat"]))
            row["classification"] = "CERTIFIED_UNSAT_TERMINAL_BY_EXISTING_STACK"
            php_rows.append(row)
            continue

        fix = verify_nonterminal_joint_fixpoint(final_formula)
        if not fix["pass"]:
            raise AssertionError(("R47AD_NONTERMINAL_NOT_TRUE_JOINT_FIXPOINT", n, fix))
        row["classification"] = "CERTIFIED_NONAFFINE_JOINT_FIXPOINT"
        row["joint_fixpoint_integrity"] = fix
        row["residual_formula"] = [list(c) for c in final_formula]
        php_rows.append(row)
        first_fixpoint = row
        break

    verdict = (
        "FIRST_STANDARD_3CNF_PHP_NONAFFINE_JOINT_FIXPOINT_FOUND"
        if first_fixpoint is not None
        else "ALL_FROZEN_STANDARD_3CNF_PHP_TERMINALIZED_BY_EXISTING_STACK__FINITE_ONLY"
    )
    return {
        "gate": GATE,
        "verdict": verdict,
        "literature_family": {
            "name": "EPH_n^{n+1} standard nondeterministic 3-CNF pigeonhole extension",
            "source": "Atserias-Dalmau ECCC TR02-035 Section 5",
            "bare_resolution_lower_bound_transfer_to_TRUMP": False,
        },
        "negative_control": {
            "family": "cubic prism Tseitin contradictions",
            "rows": tseitin,
            "all_affine_unsat_certified": True,
        },
        "php_rows": php_rows,
        "first_nonterminal_fixpoint": first_fixpoint,
        "interpretation": {
            "no_new_inference_rule": True,
            "finite_terminalization_is_not_universal": True,
            "fixpoint_if_found_is_not_yet_envelope_counterexample": True,
            "next_if_fixpoint": "R47AE_PROFILE_PERSISTED_ENVELOPE_ON_SEALED_STANDARD_3CNF_PHP_FIXPOINT",
        },
        "firewall": {
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
        p = Path(args.output)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "gate": result["gate"],
        "verdict": result["verdict"],
        "negative_control": result["negative_control"],
        "php_rows": [
            {
                "n_holes": r["n_holes"],
                "input_CLV": r["input_CLV"],
                "terminal": r["terminal"],
                "semantic_sat": r["semantic_sat"],
                "final_CLV": r["final_CLV"],
                "classification": r["classification"],
                "final_hash": r["final_hash"],
            }
            for r in result["php_rows"]
        ],
        "firewall": result["firewall"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
