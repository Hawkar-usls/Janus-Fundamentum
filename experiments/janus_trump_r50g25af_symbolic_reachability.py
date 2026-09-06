from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

GATE = "JANUS_TRUMP_R50G25AF_RESOURCE_SAFE_PREFIX_LADDER_AND_SYMBOLIC_REACHABILITY_INVARIANT_PROOF_OR_COUNTEREXAMPLE"
PREREG_COMMIT = "03e59d28d169b5e12b05bdf80b4b0c43c3be6edb"
AE_RECEIPT_COMMIT = "29d9e58b8490f9d1b20ab91ca9ffc10724d03a1b"


def G(S: int, V: int) -> Fraction:
    return Fraction(S, 1) + Fraction((2 * V - 1) * S * S, 4 * V * V)


def run():
    # Frozen sufficient invariant: 2S<=B and S^2<=BV => G(S,V)<B.
    # Test whether the only available coarse transition statement S'<=G,
    # V'=V-1 is strong enough to make that invariant inductive.
    witness = {
        "root_parameterization": {"S0": 4, "V0": 4, "B": 100},
        "pre": {"S": 14, "V": 2, "B": 100},
        "candidate_post": {"S_prime": 50, "V_prime": 1, "B": 100},
    }
    S = witness["pre"]["S"]
    V = witness["pre"]["V"]
    B = witness["pre"]["B"]
    Sp = witness["candidate_post"]["S_prime"]
    Vp = witness["candidate_post"]["V_prime"]
    g = G(S, V)

    checks = {
        "root_budget_matches": witness["root_parameterization"]["S0"] * (witness["root_parameterization"]["V0"] + 1) ** 2 == B,
        "pre_linear": 2 * S <= B,
        "pre_square": S * S <= B * V,
        "coarse_transition_bound": Fraction(Sp, 1) <= g,
        "variable_drop": Vp == V - 1,
        "post_linear": 2 * Sp <= B,
        "post_square": Sp * Sp <= B * Vp,
    }
    assert all(checks[k] for k in ("root_budget_matches", "pre_linear", "pre_square", "coarse_transition_bound", "variable_drop", "post_linear"))
    assert checks["post_square"] is False

    return {
        "gate": GATE,
        "AF_preregistration_commit": PREREG_COMMIT,
        "parent_AE_receipt_commit": AE_RECEIPT_COMMIT,
        "symbolic_result": "COARSE_TRANSITION_BOUND_NONINDUCTIVE_FOR_FROZEN_CANDIDATE",
        "sufficiency_derivation": "2*S<=B and S*S<=B*V imply G=S+(2V-1)S^2/(4V^2) < S+S^2/(2V) <= B",
        "induction_gap_witness": {
            **witness,
            "G_num": g.numerator,
            "G_den": g.denominator,
            "G_float": float(g),
            "checks": checks,
        },
        "interpretation": {
            "what_is_refuted": "The coarse proof rule consisting only of the frozen invariant plus S_prime<=G(S,V) and V_prime=V-1 is insufficient to re-establish S_prime^2<=B*V_prime.",
            "what_is_not_refuted": "No reachable CNF formula is supplied by this algebraic witness, so this is not a scheduler reachability counterexample and not a safe-envelope counterexample.",
            "remaining_obligation": "Use stronger transition structure or a reachable formula witness; do not retrofit invariant coefficients after seeing ladder outcomes."
        },
        "firewall": {
            "P_VS_NP": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "TRUMP_finished": False,
            "symbolic_noninductivity_is_not_reachability_counterexample": True,
            "finite_empirical_ladder_is_separate": True
        }
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = run()
    p = Path(args.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
