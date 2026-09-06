from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r50g25ad_safe_envelope_reachability_gphp as ad

GATE = "JANUS_TRUMP_R50G25AF_RESOURCE_SAFE_PREFIX_LADDER_AND_SYMBOLIC_REACHABILITY_INVARIANT_PROOF_OR_COUNTEREXAMPLE"
PREREG_COMMIT = "03e59d28d169b5e12b05bdf80b4b0c43c3be6edb"
AE_RECEIPT_COMMIT = "29d9e58b8490f9d1b20ab91ca9ffc10724d03a1b"
ALLOWED_H = {24, 28, 32, 40}
ALLOWED_MODE = {"CYCLIC_MIX", "SEEDED_BALANCED"}


def run(h: int, mode: str):
    if h not in ALLOWED_H or mode not in ALLOWED_MODE:
        raise AssertionError(("AF_SCOPE_DRIFT", h, mode))
    chain = ad.r50g25g._chain()
    formula, meta = ad.graph_php(h, mode)
    row = ad.audit_case(formula, meta, chain)

    safe_failures = []
    simple_failures = []
    events = []
    for event in row.get("residual_events", []):
        S = int(event["S"])
        V = int(event["CLV"][2])
        B = int(event["B"])
        ev = dict(event)
        ev["simple_linear_pass"] = 2 * S <= B
        ev["simple_square_pass"] = S * S <= B * V
        ev["simple_invariant_pass"] = ev["simple_linear_pass"] and ev["simple_square_pass"]
        ev["twoS_over_B"] = (2 * S / B) if B else float("inf")
        ev["S2_over_BV"] = (S * S / (B * V)) if B and V else float("inf")
        events.append(ev)
        if not bool(event.get("safe_envelope_pass", False)):
            safe_failures.append(ev)
        if not ev["simple_invariant_pass"]:
            simple_failures.append(ev)

    selector_gap = row.get("selector_gap_event") is not None or row.get("status") == "SELECTOR_GAP"
    semantic_mismatch = bool(row.get("semantic_mismatch_on_known_GPHP_UNSAT"))
    implementation_failure = row.get("status") == "IMPLEMENTATION_FAILURE"
    residual_limit = row.get("status") == "RESIDUAL_LIMIT"

    if safe_failures:
        verdict = "SAFE_ENVELOPE_REACHABILITY_COUNTEREXAMPLE"
    elif simple_failures:
        verdict = "SIMPLE_REACHABILITY_INVARIANT_COUNTEREXAMPLE"
    elif selector_gap:
        verdict = "ANALYTIC_SELECTOR_BUDGET_GAP"
    elif semantic_mismatch:
        verdict = "SEMANTIC_MISMATCH_ON_KNOWN_GPHP_UNSAT"
    elif implementation_failure:
        verdict = "REPLAY_OR_BOUND_SOUNDNESS_FAILURE"
    elif residual_limit:
        verdict = "RESIDUAL_AFTER_AT_MOST_V0_FALLBACKS"
    else:
        verdict = "RUNG_PASS_NO_FROZEN_FALSIFIER"

    max_g = max((float(e["G_over_B"]) for e in events), default=None)
    max_linear = max((float(e["twoS_over_B"]) for e in events), default=None)
    max_square = max((float(e["S2_over_BV"]) for e in events), default=None)
    return {
        "gate": GATE,
        "AF_preregistration_commit": PREREG_COMMIT,
        "parent_AE_receipt_commit": AE_RECEIPT_COMMIT,
        "rung": {"holes": h, "mode": mode},
        "verdict": verdict,
        "meta": meta,
        "initial_CLV": row.get("initial_CLV"),
        "status": row.get("status"),
        "terminal_label": row.get("terminal_label"),
        "fallback_DP_count": int(row.get("fallback_DP_count", 0)),
        "budget": int(row.get("budget", 0)),
        "max_controlled_state_size": row.get("max_controlled_state_size"),
        "selector_bound_checks": int(row.get("selector_bound_checks", 0)),
        "exact_materializations": int(row.get("exact_materializations", 0)),
        "residual_event_count": len(events),
        "safe_envelope_counterexample_count": len(safe_failures),
        "simple_invariant_counterexample_count": len(simple_failures),
        "selector_gap": selector_gap,
        "semantic_mismatch": semantic_mismatch,
        "max_G_over_B": max_g,
        "max_twoS_over_B": max_linear,
        "max_S2_over_BV": max_square,
        "first_safe_counterexample": safe_failures[0] if safe_failures else None,
        "first_simple_counterexample": simple_failures[0] if simple_failures else None,
        "residual_events": events,
        "firewall": {
            "P_VS_NP": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "TRUMP_finished": False,
            "single_rung_pass_is_not_universal_proof": True,
            "known_GPHP_UNSAT_is_validation_only": True
        }
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--holes", type=int, required=True)
    ap.add_argument("--mode", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    result = run(args.holes, args.mode)
    p = Path(args.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in (
        "gate", "rung", "verdict", "status", "terminal_label", "fallback_DP_count",
        "residual_event_count", "safe_envelope_counterexample_count",
        "simple_invariant_counterexample_count", "max_G_over_B", "max_twoS_over_B", "max_S2_over_BV"
    )}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
