from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47ad_standard_3cnf_pigeonhole_full_stack_intake as r47ad
import janus_trump_r47f_small_reachable_fixpoint_full_macro_falsifier as r47f
import janus_trump_r47m_post_dp_full_existing_stack_closure as r47m
import janus_trump_r47z_r47x_minimum_additive_envelope_slack_rescue as r47z

GATE = "JANUS_TRUMP_R47AE_PHP4_PERSISTED_ENVELOPE_PROFILE"
EXPECTED_INPUT_CLV = (70, 150, 45)
EXPECTED_RESIDUAL_HASH = "1553aa063ac6c771e7ac781fb69e5adafb056a1c20a8b157250565b03ed0ca64"
EXPECTED_RESIDUAL_CLV = (40, 120, 15)
C0 = 40
V0 = 15
MAX_DELTA = V0


def canon(formula):
    return r33.canonical_formula(formula)


def clv(formula):
    return r33.measure(canon(formula))


def formula_hash(formula):
    return r47f.formula_hash(canon(formula))


def load_target():
    php, counts = r47ad.standard_php_3cnf(4)
    if clv(php) != EXPECTED_INPUT_CLV:
        raise AssertionError(("R47AE_PHP4_INPUT_CLV_DRIFT", clv(php)))
    norm = r47m.normalize_full_existing_stack(php)
    if norm["terminal"] is not None:
        raise AssertionError(("R47AE_PHP4_BECAME_TERMINAL", norm["terminal"], norm["semantic_sat"]))
    residual = canon(norm["final_formula"])
    if formula_hash(residual) != EXPECTED_RESIDUAL_HASH:
        raise AssertionError(("R47AE_RESIDUAL_HASH_DRIFT", formula_hash(residual)))
    if clv(residual) != EXPECTED_RESIDUAL_CLV:
        raise AssertionError(("R47AE_RESIDUAL_CLV_DRIFT", clv(residual)))
    fix = r47ad.verify_nonterminal_joint_fixpoint(residual)
    if not fix["pass"]:
        raise AssertionError(("R47AE_RESIDUAL_FIXPOINT_INTEGRITY_FAIL", fix))
    return php, counts, norm, residual, fix


def run_chain(root, delta):
    old_c0, old_v0 = r47z.C0, r47z.V0
    try:
        r47z.C0 = C0
        r47z.V0 = V0
        result = r47z.run_envelope_chain(root, C0 + int(delta))
    finally:
        r47z.C0 = old_c0
        r47z.V0 = old_v0
    if result["delta"] != int(delta) or result["B"] != C0 + int(delta):
        raise AssertionError(("R47AE_DELTA_PARAMETER_DRIFT", result["delta"], result["B"], delta))
    if result["covered"] and result["terminal"]["semantic_sat"] is not False:
        raise AssertionError(("R47AE_UNSAT_TARGET_RETURNED_NONUNSAT_TERMINAL", result["terminal"]))
    return result


def compact(result):
    out = {
        "delta": int(result["delta"]),
        "B": int(result["B"]),
        "covered": bool(result["covered"]),
        "selected_pivots": [int(s["var"]) for s in result["selected_steps"]],
        "selected_step_count": len(result["selected_steps"]),
        "candidate_probe_count": int(result["candidate_probe_count"]),
        "rejected_probe_count": int(result["rejected_probe_count"]),
        "selected_steps": result["selected_steps"],
    }
    if result["covered"]:
        out["terminal"] = result["terminal"]
        out["SAT_root_reconstruction"] = result["SAT_root_reconstruction"]
    else:
        obstruction = result["obstruction"]
        best = obstruction.get("best_rejected")
        out["obstruction"] = {
            "state_hash": obstruction["state_hash"],
            "state_CLV": obstruction["state_CLV"],
            "candidate_count": int(obstruction["candidate_count"]),
            "best_rejected": None if best is None else {
                "var": int(best["var"]),
                "input_CLV": best["input_CLV"],
                "forced_DP_CLV": best["forced_DP_CLV"],
                "final_CLV": best["final_CLV"],
                "final_clause_overflow": int(best["final_clause_overflow"]),
                "normalization_clause_repayment": int(best["normalization_clause_repayment"]),
            },
        }
    return out


def run():
    php, counts, norm, residual, fix = load_target()
    ladder = []
    minimum = None
    minimum_full = None

    for delta in range(MAX_DELTA + 1):
        result = run_chain(residual, delta)
        ladder.append(compact(result))
        if result["covered"]:
            minimum = int(delta)
            minimum_full = result
            break

    verdict = (
        "PHP4_MINIMUM_ADDITIVE_PERSISTED_ENVELOPE_SLACK_FOUND"
        if minimum is not None
        else "PHP4_NO_RESCUE_FOR_DELTA_LE_V0__FINITE_LOWER_BOUND_ONLY"
    )

    max_forced_clauses = 0
    max_forced_literals = 0
    if minimum_full is not None:
        for s in minimum_full["selected_steps"]:
            max_forced_clauses = max(max_forced_clauses, int(s["forced_DP_CLV"][0]))
            max_forced_literals = max(max_forced_literals, int(s["forced_DP_CLV"][1]))

    return {
        "gate": GATE,
        "verdict": verdict,
        "sealed_target": {
            "family": "EPH_4^5",
            "generator_counts": counts,
            "input_hash": formula_hash(php),
            "input_CLV": list(clv(php)),
            "preprojection_normalization_segments": int(norm["segment_count"]),
            "preprojection_SA_BVE_applications": int(norm["SA_BVE_application_count"]),
            "residual_hash": formula_hash(residual),
            "residual_CLV": list(clv(residual)),
            "joint_fixpoint_integrity": fix,
            "C0": C0,
            "V0": V0,
            "expected_semantics": "UNSAT",
        },
        "delta_ladder": ladder,
        "minimum_delta": minimum,
        "minimum_envelope_B": None if minimum is None else C0 + minimum,
        "minimum_rescue": None if minimum_full is None else {
            "selected_pivots": [int(s["var"]) for s in minimum_full["selected_steps"]],
            "selected_step_count": len(minimum_full["selected_steps"]),
            "candidate_probe_count": int(minimum_full["candidate_probe_count"]),
            "rejected_probe_count": int(minimum_full["rejected_probe_count"]),
            "terminal": minimum_full["terminal"],
            "max_selected_forced_DP_clauses": int(max_forced_clauses),
            "max_selected_forced_DP_literals": int(max_forced_literals),
        },
        "interpretation": {
            "structured_family_calibration": True,
            "finite_minimum_delta_proves_universal_polynomial_envelope": False,
            "no_rescue_delta_le_V0_refutes_all_polynomial_envelopes": False,
            "sequence_enumeration_used": False,
            "next_if_rescued": "R47AF_PHP_SIZE_LADDER_DELTA_STAR_GROWTH",
            "next_if_unrescued": "PHP4_ENVELOPE_OBSTRUCTION_FORENSICS_AND_STRONGER_FIXED_POLYNOMIAL_B_TEST",
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
    d = run()
    if args.output:
        p = Path(args.output)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(d, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "gate": d["gate"],
        "verdict": d["verdict"],
        "sealed_target": {"residual_hash": d["sealed_target"]["residual_hash"], "residual_CLV": d["sealed_target"]["residual_CLV"]},
        "delta_ladder": [
            {
                "delta": x["delta"],
                "B": x["B"],
                "covered": x["covered"],
                "selected_pivots": x["selected_pivots"],
                "candidate_probe_count": x["candidate_probe_count"],
                "obstruction": x.get("obstruction"),
                "terminal": x.get("terminal"),
            }
            for x in d["delta_ladder"]
        ],
        "minimum_delta": d["minimum_delta"],
        "minimum_envelope_B": d["minimum_envelope_B"],
        "minimum_rescue": d["minimum_rescue"],
        "firewall": d["firewall"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
