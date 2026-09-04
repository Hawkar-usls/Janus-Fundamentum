from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47a3_post_subsumption_first_descent as r47a3
import janus_trump_r47f_small_reachable_fixpoint_full_macro_falsifier as r47f
import janus_trump_r47i_r47g_one_swap_macro_dead_complement_hunt as r47i
import janus_trump_r47m_post_dp_full_existing_stack_closure as r47m

GATE = "JANUS_TRUMP_R47Y_R47X_ALL_PIVOT_SURPLUS_OVER_SLACK_PROFILE"
R47K_RESULT = Path(__file__).resolve().parents[1] / "research" / "JANUS_TRUMP_R47K_EXPLICIT_REACHABLE_COUNTEREXAMPLE_TO_EXTENDED_NORMALIZATION_CLOSURE_RESULT_2026-09-03.json"
CENTER_ORIGINAL_HASH = "eb13be26c29c106cf172db0be435aaf852d1e1248fced151c5356791f70024da"
SOURCE = (-9, 11, -20)
REPLACEMENT = (-9, -11, -20)
ROOT_HASH = "ed330049538dc3fb487019c71bb49bde65494dc88453e50bed73b49d4ee17ca6"
ROOT_CLV = (75, 199, 22)
OBSTRUCTION_HASH = "a4f361a15ba24f9be4db6bf9ab31c0718f776981646d84938359b49b5ec532d2"
OBSTRUCTION_CLV = (75, 202, 21)
C0 = 75


def h(formula):
    return r47f.formula_hash(r33.canonical_formula(formula))


def load_obstruction():
    data = json.loads(R47K_RESULT.read_text())
    center = r33.canonical_formula(data["mutated_original"]["formula"])
    if h(center) != CENTER_ORIGINAL_HASH:
        raise AssertionError(("R47Y_CENTER_HASH_DRIFT", h(center)))
    mutated = r47i.mutate_one_clause(center, SOURCE, REPLACEMENT)
    if mutated is None:
        raise AssertionError("R47Y_TARGET_MUTATION_DUPLICATE")
    reached = r47f.reachable_fixpoint(mutated)
    if reached is None:
        raise AssertionError("R47Y_TARGET_NO_REACHABLE_FIXPOINT")
    root = r33.canonical_formula(reached["formula"])
    if h(root) != ROOT_HASH or r33.measure(root) != ROOT_CLV:
        raise AssertionError(("R47Y_ROOT_DRIFT", h(root), r33.measure(root)))
    c7 = r47m.macro_candidate_full_closure(root, 7)
    if c7 is None:
        raise AssertionError("R47Y_PIVOT7_DISAPPEARED")
    if not c7["DP_independent_replay_pass"] or not c7["polynomial_intermediate_envelope_pass"]:
        raise AssertionError("R47Y_PIVOT7_CERTIFICATE_FAIL")
    replay = r47m.independent_replay(root, c7)
    if not replay["pass"]:
        raise AssertionError(("R47Y_PIVOT7_FULL_REPLAY_FAIL", replay))
    obstruction = r33.canonical_formula(c7["normalization"]["final_formula"])
    if h(obstruction) != OBSTRUCTION_HASH or r33.measure(obstruction) != OBSTRUCTION_CLV:
        raise AssertionError(("R47Y_OBSTRUCTION_DRIFT", h(obstruction), r33.measure(obstruction)))
    return root, obstruction


def run():
    root, obstruction = load_obstruction()
    C = len(obstruction)
    sigma = C0 - C
    if sigma != 0:
        raise AssertionError(("R47Y_EXPECTED_ZERO_SLACK", sigma))

    rows = []
    for v in r33.variables(obstruction):
        raw = r47a3.post_subsumption_gain(obstruction, int(v))
        if raw is None:
            raise AssertionError(("R47Y_NON_BIPOLAR_PIVOT_IN_SEALED_OBSTRUCTION", v))
        d = int(raw["p"] + raw["n"])
        base_count = C - d
        s = int(raw["post_subsumption_clauses"] - base_count)
        g = int(raw["gain"])
        if g != d - s:
            raise AssertionError(("R47Y_G_EQUALS_D_MINUS_S_FAIL", v, g, d, s))
        surplus = s - d
        slack_safe = g >= -sigma
        rows.append({
            "var": int(v),
            "p": int(raw["p"]),
            "n": int(raw["n"]),
            "d_removed_parent_pressure": d,
            "base_clause_count": base_count,
            "raw_unique_resolvents": int(raw["raw_unique_resolvents"]),
            "pool_clauses": int(raw["pool_clauses"]),
            "post_subsumption_clauses": int(raw["post_subsumption_clauses"]),
            "g_clause_gain": g,
            "s_survivor_pressure": s,
            "surplus_s_minus_d": surplus,
            "sigma": sigma,
            "slack_safe_g_ge_minus_sigma": bool(slack_safe),
            "strict_post_subsumption_expansion": bool(g <= -1),
            "pair_checks": int(raw["pair_checks"]),
        })

    all_strict = all(r["strict_post_subsumption_expansion"] for r in rows)
    all_unsafe = all(not r["slack_safe_g_ge_minus_sigma"] for r in rows)
    if not all_strict or not all_unsafe:
        verdict = "R47Y_OR_R47X_REGRESSION_MISMATCH"
    else:
        verdict = "ALL_PIVOT_STRICT_POST_SUBSUMPTION_EXPANSION_CONFIRMED"

    best = max(rows, key=lambda r: (r["g_clause_gain"], -r["var"]))
    worst = min(rows, key=lambda r: (r["g_clause_gain"], r["var"]))
    histogram = {}
    for r in rows:
        histogram[str(r["surplus_s_minus_d"])] = histogram.get(str(r["surplus_s_minus_d"]), 0) + 1

    return {
        "gate": GATE,
        "verdict": verdict,
        "root": {"hash": ROOT_HASH, "CLV": list(ROOT_CLV), "C0": C0},
        "obstruction": {"hash": OBSTRUCTION_HASH, "CLV": list(OBSTRUCTION_CLV), "sigma": sigma},
        "pivot_count": len(rows),
        "all_pivots_strict_post_subsumption_expansion": all_strict,
        "all_pivots_fail_R47Y_slack_safe_test": all_unsafe,
        "minimum_required_pre_normalization_additive_slack": min(r["surplus_s_minus_d"] for r in rows),
        "best_pivot_by_gain": best,
        "worst_pivot_by_gain": worst,
        "surplus_histogram": histogram,
        "rows": rows,
        "interpretation": {
            "finite_profile_only": True,
            "minimum_pre_normalization_slack_is_not_necessarily_minimum_post_normalization_envelope_delta": True,
            "reason": "R47M normalization may repay clause overflow after forced exact DP.",
        },
        "firewall": {
            "UNIVERSAL_SLACK_SAFE_PIVOT_EXISTENCE": "NOT_PROVED",
            "UNIVERSAL_POLYNOMIAL_ENVELOPE_COVERAGE": "OPEN",
            "O4_UNIVERSAL_COVERAGE": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
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
        "pivot_count": d["pivot_count"],
        "minimum_required_pre_normalization_additive_slack": d["minimum_required_pre_normalization_additive_slack"],
        "best_pivot_by_gain": d["best_pivot_by_gain"],
        "worst_pivot_by_gain": d["worst_pivot_by_gain"],
        "surplus_histogram": d["surplus_histogram"],
        "firewall": d["firewall"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
