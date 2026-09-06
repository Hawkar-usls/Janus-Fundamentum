from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import janus_trump_r50g25ad_safe_envelope_reachability_gphp as ad

GATE = "JANUS_TRUMP_R50G25AE_SCALE_BOUNDED_DEGREE_GPHP_AND_DERIVE_REACHABILITY_INVARIANT_CANDIDATE"
AE_PREREG_COMMIT = "d086333294ee92efe6bd968fce6402010d7266c8"
AD_RECEIPT_COMMIT = "0c9cca17c8b36639479870c817d0192061930c03"
HOLE_SIZES = (24, 28, 32, 40)
MODES = ("CYCLIC_MIX", "SEEDED_BALANCED")


def run():
    chain = ad.r50g25g._chain()
    rows = []
    simple_failures = []
    safe_failures = []
    selector_gaps = []
    semantic_mismatches = []
    implementation_failures = []
    residual_limits = []
    max_g_ratio = None
    max_linear_ratio = None
    max_square_ratio = None

    for h in HOLE_SIZES:
        for mode in MODES:
            formula, meta = ad.graph_php(h, mode)
            row = ad.audit_case(formula, meta, chain)
            augmented_events = []
            for event in row.get("residual_events", []):
                S = int(event["S"])
                V = int(event["CLV"][2])
                B = int(event["B"])
                two_s = 2 * S
                s2 = S * S
                bv = B * V
                simple_linear_pass = two_s <= B
                simple_square_pass = s2 <= bv
                simple_pass = simple_linear_pass and simple_square_pass
                ev = dict(event)
                ev.update({
                    "simple_linear_pass": simple_linear_pass,
                    "simple_square_pass": simple_square_pass,
                    "simple_invariant_pass": simple_pass,
                    "twoS_over_B": (two_s / B) if B else float("inf"),
                    "S2_over_BV": (s2 / bv) if bv else float("inf"),
                })
                augmented_events.append(ev)
                if not event.get("safe_envelope_pass", False):
                    safe_failures.append({"meta": meta, "event": ev})
                if not simple_pass:
                    simple_failures.append({"meta": meta, "event": ev})
                g_key = float(event["G_over_B"])
                l_key = float(ev["twoS_over_B"])
                q_key = float(ev["S2_over_BV"])
                if max_g_ratio is None or g_key > max_g_ratio[0]:
                    max_g_ratio = (g_key, meta, ev)
                if max_linear_ratio is None or l_key > max_linear_ratio[0]:
                    max_linear_ratio = (l_key, meta, ev)
                if max_square_ratio is None or q_key > max_square_ratio[0]:
                    max_square_ratio = (q_key, meta, ev)
            row = dict(row)
            row["residual_events"] = augmented_events
            rows.append(row)
            if row.get("selector_gap_event") is not None or row.get("status") == "SELECTOR_GAP":
                selector_gaps.append(row)
            if row.get("semantic_mismatch_on_known_GPHP_UNSAT"):
                semantic_mismatches.append(row)
            if row.get("status") == "IMPLEMENTATION_FAILURE":
                implementation_failures.append(row)
            if row.get("status") == "RESIDUAL_LIMIT":
                residual_limits.append(row)

    if safe_failures:
        verdict = "SAFE_ENVELOPE_REACHABILITY_COUNTEREXAMPLE"
    elif simple_failures:
        verdict = "SIMPLE_REACHABILITY_INVARIANT_COUNTEREXAMPLE"
    elif selector_gaps:
        verdict = "ANALYTIC_SELECTOR_BUDGET_GAP"
    elif semantic_mismatches:
        verdict = "SEMANTIC_MISMATCH_ON_KNOWN_GPHP_UNSAT"
    elif implementation_failures:
        verdict = "REPLAY_OR_BOUND_SOUNDNESS_FAILURE"
    elif residual_limits:
        verdict = "RESIDUAL_AFTER_AT_MOST_V0_FALLBACKS"
    else:
        verdict = "SIMPLE_SUFFICIENT_REACHABILITY_INVARIANT_SURVIVES_SCALED_GPHP"

    status_hist = Counter(str(r.get("status")) for r in rows)
    terminal_hist = Counter(str(r.get("terminal_label")) for r in rows if r.get("status") == "TERMINAL")
    total_events = sum(len(r.get("residual_events", [])) for r in rows)

    def pack_max(item):
        if item is None:
            return None
        value, meta, event = item
        return {"value": value, "meta": meta, "event": event}

    return {
        "gate": GATE,
        "AE_preregistration_commit": AE_PREREG_COMMIT,
        "parent_AD_receipt_commit": AD_RECEIPT_COMMIT,
        "verdict": verdict,
        "domain": {
            "case_count": len(rows),
            "hole_sizes": list(HOLE_SIZES),
            "modes": list(MODES),
            "all_left_degree": 3,
            "truth_used_for_generation_or_pivot_selection": False,
            "semantic_UNSAT_known_by_pigeonhole_counting": True,
        },
        "candidate_invariant": {
            "name": "SIMPLE_HALF_BUDGET_SQUARE_ROOT_ENVELOPE",
            "conditions": ["2*S <= B", "S*S <= B*V"],
            "sufficiency_derivation": "G=S+(2V-1)S^2/(4V^2) < S+S^2/(2V) <= B/2+B/2=B",
            "coefficient_frozen_before_execution": True,
        },
        "status_partition": dict(sorted(status_hist.items())),
        "terminal_partition": dict(sorted(terminal_hist.items())),
        "residual_event_count": total_events,
        "safe_envelope_counterexample_count": len(safe_failures),
        "simple_invariant_counterexample_count": len(simple_failures),
        "selector_gap_count": len(selector_gaps),
        "semantic_mismatch_count": len(semantic_mismatches),
        "implementation_failure_count": len(implementation_failures),
        "residual_limit_count": len(residual_limits),
        "max_G_over_B": pack_max(max_g_ratio),
        "max_twoS_over_B": pack_max(max_linear_ratio),
        "max_S2_over_BV": pack_max(max_square_ratio),
        "first_simple_counterexample": simple_failures[0] if simple_failures else None,
        "first_safe_counterexample": safe_failures[0] if safe_failures else None,
        "rows": rows,
        "next_gate": (
            "R50G25AF_MINIMIZE_REACHABILITY_INVARIANT_COUNTEREXAMPLE"
            if (safe_failures or simple_failures)
            else "R50G25AF_PROVE_SIMPLE_REACHABILITY_INVARIANT_FOR_CONTROLLED_SCHEDULER_OR_COUNTEREXAMPLE"
        ),
        "firewall": {
            "P_VS_NP": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "TRUMP_finished": False,
            "finite_scaled_GPHP_pass_is_not_universal_proof": True,
            "simple_invariant_sufficiency_is_not_global_reachability": True,
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
    print(json.dumps({
        "gate": result["gate"],
        "verdict": result["verdict"],
        "domain": result["domain"],
        "status_partition": result["status_partition"],
        "terminal_partition": result["terminal_partition"],
        "residual_events": result["residual_event_count"],
        "safe_counterexamples": result["safe_envelope_counterexample_count"],
        "simple_counterexamples": result["simple_invariant_counterexample_count"],
        "selector_gaps": result["selector_gap_count"],
        "next_gate": result["next_gate"],
    }, indent=2, sort_keys=True))
    print("MAX_G_OVER_B", json.dumps(result["max_G_over_B"], sort_keys=True))
    print("MAX_TWO_S_OVER_B", json.dumps(result["max_twoS_over_B"], sort_keys=True))
    print("MAX_S2_OVER_BV", json.dumps(result["max_S2_over_BV"], sort_keys=True))


if __name__ == "__main__":
    main()
