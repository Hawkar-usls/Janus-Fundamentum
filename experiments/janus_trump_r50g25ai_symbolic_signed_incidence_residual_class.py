from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r50g25ah_raw_dp_reachability_induction as ah

GATE = "JANUS_TRUMP_R50G25AI_LIFT_AVERAGE_RAW_MASS_CERTIFICATE_TO_SYMBOLIC_RESIDUAL_CLASS"
PREREG_COMMIT = "cc230a79e9e2106d638f1ef9b3bcb2b55540eb11"
AH_RECEIPT_COMMIT = "2ea19315b1ec4a3bc96d3e1bb043bd9adae5de62"


def signed_incidence_record(formula, budget):
    f = r33.canonical_formula(formula)
    C, L, V = map(int, r33.measure(f))
    S = C + L
    vars_ = tuple(r33.variables(f))
    q2 = sum(len(c) * len(c) for c in f)
    W = max((len(c) for c in f), default=0)
    rows = []
    degrees = []
    p_hat = 0
    for x in vars_:
        pos = [c for c in f if x in c]
        neg = [c for c in f if -x in c]
        a = len(pos)
        b = len(neg)
        A = sum(len(c) for c in pos)
        Bx = sum(len(c) for c in neg)
        d = a + b
        degrees.append(d)
        local = b * A + a * Bx - a * b
        p_hat += local
        rows.append({
            "var": int(x), "a_pos": a, "b_neg": b,
            "A_pos_width_sum": A, "B_neg_width_sum": Bx,
            "degree": d, "signed_incidence_pair_mass_UB": int(local),
        })
    Delta = max(degrees, default=0)
    symbolic_sum_raw_ub = V * S - L - q2 + p_hat
    T = ah.math.isqrt(int(budget) * (V - 1)) if V > 1 else 0
    if V > 1:
        T = min(int(budget) // 2, T)
    class_pass = bool(V > 1 and symbolic_sum_raw_ub <= V * T)

    coarse_num = (2 * W - 1) * Delta * L if W > 0 else 0
    coarse_p_hat = coarse_num // 4
    coarse_sum_raw_ub = V * S - L - q2 + coarse_p_hat
    coarse_pass = bool(V > 1 and coarse_sum_raw_ub <= V * T)

    return {
        "CLV": [C, L, V], "S": S, "B": int(budget), "T": int(T),
        "Q2": int(q2), "W": int(W), "Delta": int(Delta),
        "P_hat_signed_incidence": int(p_hat),
        "symbolic_sum_RAW_S_UB": int(symbolic_sum_raw_ub),
        "V_times_T": int(V * T),
        "symbolic_class_pass": class_pass,
        "symbolic_class_slack": int(V * T - symbolic_sum_raw_ub),
        "coarse_width_degree_P_hat_UB": int(coarse_p_hat),
        "coarse_sum_RAW_S_UB": int(coarse_sum_raw_ub),
        "coarse_width_degree_pass": coarse_pass,
        "coarse_width_degree_slack": int(V * T - coarse_sum_raw_ub),
        "incidence_rows": rows,
    }


def run():
    parent = ah.run()
    if parent.get("verdict") != "AVERAGE_RAW_MASS_CERTIFICATE_CLOSES_REACHABLE_DOMAIN":
        return {
            "gate": GATE, "AI_preregistration_commit": PREREG_COMMIT,
            "parent_AH_receipt_commit": AH_RECEIPT_COMMIT,
            "verdict": "PARENT_AH_REPLAY_FAILURE",
            "parent_verdict": parent.get("verdict"),
            "firewall": {"P_VS_NP":"OPEN","SAT_IN_P":"NOT_PROVED","TRUMP_finished":False},
        }

    events = []
    soundness_failures = []
    coverage_gaps = []
    actual_no_pivot = []
    replay_failures = []
    coarse_gaps = []
    for root in parent.get("rows", []):
        root_id = root.get("rung")
        budget = int(root.get("budget", 0))
        for e in root.get("events", []):
            rec = signed_incidence_record(e["formula"], budget)
            actual_pair_mass = int(e["sum_pair_mass"])
            actual_sum_raw = int(e["sum_RAW_S"])
            rec.update({
                "root": root_id,
                "outer_round": int(e["outer_round"]),
                "residual_hash": e["residual_hash"],
                "actual_sum_pair_mass": actual_pair_mass,
                "actual_sum_RAW_S": actual_sum_raw,
                "actual_average_condition_pass": bool(e["average_condition_pass"]),
                "actual_admissible_raw_pivot_count": int(e["admissible_raw_pivot_count"]),
                "best_exact_replay_pass": bool(e["best_exact_replay_pass"]),
                "pair_mass_bound_sound": bool(actual_pair_mass <= rec["P_hat_signed_incidence"]),
                "aggregate_bound_sound": bool(actual_sum_raw <= rec["symbolic_sum_RAW_S_UB"]),
                "P_hat_overestimate": int(rec["P_hat_signed_incidence"] - actual_pair_mass),
            })
            events.append(rec)
            if not rec["pair_mass_bound_sound"] or not rec["aggregate_bound_sound"]:
                soundness_failures.append(rec)
            if not rec["symbolic_class_pass"]:
                coverage_gaps.append(rec)
            if rec["actual_admissible_raw_pivot_count"] <= 0:
                actual_no_pivot.append(rec)
            if not rec["best_exact_replay_pass"]:
                replay_failures.append(rec)
            if not rec["coarse_width_degree_pass"]:
                coarse_gaps.append(rec)

    semantic_mismatches = int(parent.get("semantic_mismatch_count", 0))
    if soundness_failures:
        verdict = "SIGNED_INCIDENCE_BOUND_UNSOUND"
    elif actual_no_pivot:
        verdict = "REACHABLE_NO_ADMISSIBLE_RAW_DP_PIVOT"
    elif replay_failures:
        verdict = "EXACT_DP_REPLAY_FAILURE"
    elif semantic_mismatches:
        verdict = "SEMANTIC_MISMATCH_ON_KNOWN_GPHP_UNSAT"
    elif coverage_gaps:
        verdict = "SYMBOLIC_CLASS_COVERAGE_GAP_ON_REACHABLE_RESIDUAL"
    else:
        verdict = "SIGNED_INCIDENCE_SYMBOLIC_CLASS_COVERS_AH_REACHABLE_DOMAIN"

    min_slack = min((e["symbolic_class_slack"] for e in events), default=0)
    max_slack = max((e["symbolic_class_slack"] for e in events), default=0)
    min_over = min((e["P_hat_overestimate"] for e in events), default=0)
    max_over = max((e["P_hat_overestimate"] for e in events), default=0)

    return {
        "gate": GATE,
        "AI_preregistration_commit": PREREG_COMMIT,
        "parent_AH_receipt_commit": AH_RECEIPT_COMMIT,
        "verdict": verdict,
        "symbolic_lemma": {
            "pair_mass_bound": "pair_mass_x <= b_x*A_x + a_x*B_x - a_x*b_x",
            "aggregate_bound": "sum_RAW_S <= V*S-L-Q2+P_hat",
            "class_condition": "V*S-L-Q2+P_hat <= V*T",
            "existence": "class_condition implies min_x RAW_S(x)<=T and therefore at least one frozen-invariant-preserving raw-DP pivot",
            "certificate_pair_enumeration_required": False,
            "certificate_truth_required": False,
        },
        "domain": parent.get("domain"),
        "root_reachable_residual_event_count": len(events),
        "signed_incidence_bound_soundness_failure_count": len(soundness_failures),
        "symbolic_class_coverage_gap_count": len(coverage_gaps),
        "reachable_no_admissible_raw_pivot_count": len(actual_no_pivot),
        "exact_DP_replay_failure_count": len(replay_failures),
        "semantic_mismatch_count": semantic_mismatches,
        "secondary_width_degree_gap_count": len(coarse_gaps),
        "symbolic_class_slack": {"min": int(min_slack), "max": int(max_slack)},
        "P_hat_overestimate": {"min": int(min_over), "max": int(max_over)},
        "first_soundness_failure": soundness_failures[0] if soundness_failures else None,
        "first_symbolic_class_coverage_gap": coverage_gaps[0] if coverage_gaps else None,
        "first_width_degree_gap": coarse_gaps[0] if coarse_gaps else None,
        "events": events,
        "recommended_next_gate": (
            "R50G25AJ_MINIMIZE_SIGNED_INCIDENCE_CLASS_COUNTEREXAMPLE" if coverage_gaps else
            "R50G25AJ_PROVE_REACHABILITY_INTO_SIGNED_INCIDENCE_CLASS_OR_FIND_COUNTEREXAMPLE"
        ),
        "firewall": {
            "P_VS_NP": "OPEN", "SAT_IN_P": "NOT_PROVED", "TRUMP_finished": False,
            "finite_AH_domain_coverage_is_not_global_reachability": True,
            "symbolic_class_membership_is_sufficient_not_necessary": True,
            "state_envelope_is_not_runtime_bound": True,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    result = run()
    p = Path(args.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    keys = [
        "gate","verdict","root_reachable_residual_event_count",
        "signed_incidence_bound_soundness_failure_count","symbolic_class_coverage_gap_count",
        "reachable_no_admissible_raw_pivot_count","exact_DP_replay_failure_count",
        "semantic_mismatch_count","secondary_width_degree_gap_count","symbolic_class_slack",
        "P_hat_overestimate","recommended_next_gate"
    ]
    print(json.dumps({k: result.get(k) for k in keys}, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
