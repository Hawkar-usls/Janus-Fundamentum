from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

GATE = "JANUS_TRUMP_R50G25AC_SYMBOLIC_MIN_UB_EXISTENCE_INEQUALITY_OR_COUNTEREXAMPLE"
AC_PREREG_COMMIT = "ba2a085daccdd4ba0f1cb96a52f5448b22620345"
PARENT_AB_RUN = 34051293910
PARENT_AB_ARTIFACT_ID = 9994874097
PARENT_AB_PREREG = "af0ae06061797ec8149f42da9529e9ffab620fc1"
PARENT_AB_VERDICT = "PHI4_CANDIDATE_FALSIFIED_WITHOUT_SELECTOR_FAILURE"
EXPECTED_EVENT_COUNT = 239


def G_fraction(C: int, L: int, V: int) -> Fraction:
    C, L, V = int(C), int(L), int(V)
    if V <= 0:
        raise AssertionError(("AC_NONPOSITIVE_V", C, L, V))
    S = C + L
    return Fraction(S, 1) + Fraction((2 * V - 1) * S * S, 4 * V * V)


def verify_ub_identity_small_grid():
    # Executable side audit of the algebraic identity used in the paper proof.
    # Universality comes from symbolic algebra in the research note, not this finite grid.
    checks = 0
    for V in range(2, 9):
        for p in range(1, V + 1):
            for q in range(1, V + 1):
                for lp in (1, V):
                    for ln in (1, V):
                        SP = p * lp
                        SN = q * ln
                        C = p + q + 7
                        L = SP + SN + 11
                        ub_c = C - p - q + p * q
                        ub_l = L - SP - SN + q * (SP - p) + p * (SN - q)
                        identity = (C + L) - (p + q) - (SP + SN) + q * SP + p * SN - p * q
                        if ub_c + ub_l != identity:
                            raise AssertionError(("AC_UB_IDENTITY_FAIL", V, p, q, SP, SN, ub_c + ub_l, identity))
                        checks += 1
    return checks


def audit_parent(ab):
    if ab.get("AB_preregistration_commit") != PARENT_AB_PREREG:
        raise AssertionError(("AC_PARENT_AB_PREREG_DRIFT", ab.get("AB_preregistration_commit")))
    if ab.get("verdict") != PARENT_AB_VERDICT:
        raise AssertionError(("AC_PARENT_AB_VERDICT_DRIFT", ab.get("verdict")))
    if ab.get("domain", {}).get("total_case_count") != 20:
        raise AssertionError(("AC_PARENT_AB_DOMAIN_DRIFT", ab.get("domain")))
    if ab.get("total_exact_DP_materializations") != EXPECTED_EVENT_COUNT:
        raise AssertionError(("AC_PARENT_AB_MATERIALIZATION_COUNT_DRIFT", ab.get("total_exact_DP_materializations")))

    events = []
    for row in ab.get("rows", []):
        for event in row.get("residual_events", []):
            C, L, V = map(int, event["residual_CLV"])
            B = int(event["budget"])
            chosen = int(event["chosen_UB_S"])
            g = G_fraction(C, L, V)
            safe = g <= B
            chosen_bounded = Fraction(chosen, 1) <= g
            events.append({
                "case": row["name"],
                "source": row.get("source"),
                "outer_round": int(event["outer_round"]),
                "residual_hash": event["residual_hash"],
                "CLV": [C, L, V],
                "S": C + L,
                "B": B,
                "chosen_var": int(event["chosen_var"]),
                "chosen_UB_S": chosen,
                "G_num": g.numerator,
                "G_den": g.denominator,
                "G_float": float(g),
                "G_over_B": float(g / B),
                "safe_envelope_pass": bool(safe),
                "chosen_UB_le_G": bool(chosen_bounded),
                "B_minus_G_num": (Fraction(B, 1) - g).numerator,
                "B_minus_G_den": (Fraction(B, 1) - g).denominator,
                "B_minus_G_float": float(Fraction(B, 1) - g),
            })
    if len(events) != EXPECTED_EVENT_COUNT:
        raise AssertionError(("AC_EVENT_COUNT_DRIFT", len(events), EXPECTED_EVENT_COUNT))
    return events


def abstract_budget_only_countermodel():
    # This is deliberately NOT claimed to be a reachable CNF. It only proves that
    # the scalar invariant S<=B alone cannot algebraically imply G(S,V)<=B.
    V = 10
    B = 1000
    S = 1000
    g = Fraction(S, 1) + Fraction((2 * V - 1) * S * S, 4 * V * V)
    if not (S <= B and g > B):
        raise AssertionError(("AC_ABSTRACT_COUNTERMODEL_CONSTRUCTION_FAIL", S, V, B, g))
    return {
        "status": "ABSTRACT_NOT_CLAIMED_CNF_REALIZABLE_OR_REACHABLE",
        "S": S,
        "V": V,
        "B": B,
        "S_le_B": True,
        "G_num": g.numerator,
        "G_den": g.denominator,
        "G_float": float(g),
        "G_gt_B": True,
        "meaning": "The inherited scalar state budget S<=B alone is insufficient to derive the stronger safe-envelope condition. Additional reachability/structural invariants are required."
    }


def run(ab):
    identity_checks = verify_ub_identity_small_grid()
    events = audit_parent(ab)
    safe_fail = [e for e in events if not e["safe_envelope_pass"]]
    bound_fail = [e for e in events if not e["chosen_UB_le_G"]]

    max_ratio = max(events, key=lambda e: (e["G_over_B"], e["residual_hash"], e["outer_round"]))
    min_slack = min(events, key=lambda e: (e["B_minus_G_float"], e["residual_hash"], e["outer_round"]))
    max_chosen_to_g = max(events, key=lambda e: (e["chosen_UB_S"] / e["G_float"], e["residual_hash"], e["outer_round"]))

    if bound_fail:
        verdict = "AB_CHOSEN_UB_EXCEEDS_PROVED_G_BOUND"
    elif safe_fail:
        verdict = "AB_RECORDED_EVENT_VIOLATES_SAFE_ENVELOPE"
    else:
        verdict = "LOCAL_MIN_UB_SAFE_ENVELOPE_LEMMA_AND_239_OF_239_AUDIT_PASS"

    return {
        "gate": GATE,
        "AC_preregistration_commit": AC_PREREG_COMMIT,
        "parent_AB": {
            "run_id": PARENT_AB_RUN,
            "artifact_id": PARENT_AB_ARTIFACT_ID,
            "preregistration_commit": PARENT_AB_PREREG,
            "verdict": PARENT_AB_VERDICT,
        },
        "verdict": verdict,
        "local_lemma": {
            "status": "PAPER_PROOF_FROM_IMPLEMENTED_DEFINITIONS_PLUS_EXECUTABLE_ARTIFACT_AUDIT_NOT_PROOF_ASSISTANT_FORMALIZED",
            "claim": "For every canonical W residual, there exists x with UB_S(x)<=G(S,V)=S+(2V-1)S^2/(4V^2). Therefore G(S,V)<=B is sufficient for existence of a within-B analytic exact-DP fallback.",
            "ub_identity_finite_side_audit_checks": identity_checks,
            "proof_dependencies": [
                "minimum occurrence degree d<=L/V",
                "parent clause width <=V",
                "p*q<=(p+q)^2/4",
                "L<=S",
                "W residual has no pure variable"
            ]
        },
        "artifact_audit": {
            "event_count": len(events),
            "safe_envelope_pass_count": len(events) - len(safe_fail),
            "safe_envelope_failure_count": len(safe_fail),
            "chosen_UB_le_G_pass_count": len(events) - len(bound_fail),
            "chosen_UB_le_G_failure_count": len(bound_fail),
            "max_G_over_B_case": max_ratio,
            "minimum_B_minus_G_case": min_slack,
            "max_chosen_UB_over_G_case": {
                **max_chosen_to_g,
                "chosen_UB_over_G": max_chosen_to_g["chosen_UB_S"] / max_chosen_to_g["G_float"],
            },
            "safe_failures": safe_fail,
            "G_bound_failures": bound_fail,
        },
        "abstract_budget_only_countermodel": abstract_budget_only_countermodel(),
        "universal_obligation": {
            "status": "OPEN",
            "statement": "Prove or falsify that every root-reachable W residual generated by the hybrid scheduler before controlled fallback satisfies G(S,V)<=B.",
            "S_le_B_alone_is_sufficient": False,
            "finite_239_of_239_is_universal_proof": False,
        },
        "next_gate": "R50G25AD_RESIDUAL_SAFE_ENVELOPE_INVARIANT_OR_BOUNDED_DEGREE_PHP_COUNTEREXAMPLE" if verdict.endswith("AUDIT_PASS") else "R50G25AD_MINIMIZE_SAFE_ENVELOPE_OR_G_BOUND_COUNTEREXAMPLE",
        "firewall": {
            "P_VS_NP": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "TRUMP_finished": False,
            "local_lemma_is_conditional_not_global_completeness": True,
            "finite_artifact_audit_is_not_universal_coverage": True,
            "abstract_budget_countermodel_is_not_claimed_reachable_CNF": True,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifact-json", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    ab = json.loads(Path(args.artifact_json).read_text())
    result = run(ab)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "gate": result["gate"],
        "verdict": result["verdict"],
        "event_count": result["artifact_audit"]["event_count"],
        "safe_pass": result["artifact_audit"]["safe_envelope_pass_count"],
        "G_bound_pass": result["artifact_audit"]["chosen_UB_le_G_pass_count"],
        "max_G_over_B": result["artifact_audit"]["max_G_over_B_case"]["G_over_B"],
        "min_B_minus_G": result["artifact_audit"]["minimum_B_minus_G_case"]["B_minus_G_float"],
        "next_gate": result["next_gate"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
