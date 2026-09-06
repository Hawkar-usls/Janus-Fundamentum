from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r50g25g_micro_rup_restart_replay_source_lift_family as r50g25g
import janus_trump_r50g25y_minimal_w_policy_counterexample_forensics as y
import janus_trump_r50g25ab_analytic_ub_pivot_selector_amortized_potential as ab
import janus_trump_r50g25ad_safe_envelope_reachability_gphp as ad

GATE = "JANUS_TRUMP_R50G25AG_STRONGER_EXACT_DP_TRANSITION_BOUND_OR_REACHABLE_COUNTEREXAMPLE"
PREREG_COMMIT = "f21d2f1ac2eeb808a44d6bddf38609410c64b174"
AF_RECEIPT_COMMIT = "22fca8d3d6249892b3169533fdcd18461c366c29"
DOMAIN = ((24, "CYCLIC_MIX"), (24, "SEEDED_BALANCED"), (28, "CYCLIC_MIX"))


def raw_dp_bound(formula, var):
    formula = r33.canonical_formula(formula)
    pos = tuple(c for c in formula if var in c)
    neg = tuple(c for c in formula if -var in c)
    if not pos or not neg:
        return None
    base = tuple(c for c in formula if var not in c and -var not in c)
    raw_resolvents = []
    pair_checks = 0
    tautological_pairs = 0
    for p in pos:
        for n in neg:
            pair_checks += 1
            merged = (set(p) - {var}) | (set(n) - {-var})
            if any(-lit in merged for lit in merged):
                tautological_pairs += 1
                continue
            raw_resolvents.append(r33.canonical_clause(merged))
    raw_c = len(base) + len(raw_resolvents)
    raw_l = sum(len(c) for c in base) + sum(len(c) for c in raw_resolvents)
    return {
        "var": int(var),
        "positive_parent_count": len(pos),
        "negative_parent_count": len(neg),
        "pair_checks": pair_checks,
        "tautological_pair_count": tautological_pairs,
        "non_tautological_pair_count": len(raw_resolvents),
        "base_clause_count": len(base),
        "RAW_C": int(raw_c),
        "RAW_L": int(raw_l),
        "RAW_S": int(raw_c + raw_l),
    }


def terminal_label(w):
    if w.get("kind") == "AFFINE":
        return str(w["route"][-1].get("stop", "AFFINE")) if w.get("route") else "AFFINE"
    if w.get("kind") == "TERMINAL":
        return str(w["route"][-1].get("R33_terminal", "TERMINAL")) if w.get("route") else "TERMINAL"
    return None


def audit_rung(h, mode, chain):
    initial, meta = ad.graph_php(h, mode)
    initial = r33.canonical_formula(initial)
    c0, l0, v0 = r33.measure(initial)
    budget = (c0 + l0) * ((v0 + 1) ** 2)
    state = initial
    events = []
    soundness_failures = []
    invariant_failures = []
    replay_failures = []
    selector_failures = []
    old_selector_mismatch = []

    for outer in range(v0 + 1):
        w = y.policy_replay(state, chain)
        if w["kind"] in {"TERMINAL", "AFFINE"}:
            label = terminal_label(w)
            semantic_mismatch = not ("UNSAT" in label or "EMPTY_CLAUSE" in label)
            return {
                "rung": {"holes": h, "mode": mode},
                "meta": meta,
                "initial_CLV": [c0, l0, v0],
                "budget": budget,
                "status": "TERMINAL",
                "terminal_label": label,
                "semantic_mismatch": semantic_mismatch,
                "residual_event_count": len(events),
                "events": events,
                "raw_bound_soundness_failure_count": len(soundness_failures),
                "reachable_post_invariant_counterexample_count": len(invariant_failures),
                "exact_DP_replay_failure_count": len(replay_failures),
                "selector_failure_count": len(selector_failures),
                "old_selector_replay_mismatch_count": len(old_selector_mismatch),
                "first_raw_bound_soundness_failure": soundness_failures[0] if soundness_failures else None,
                "first_reachable_post_invariant_counterexample": invariant_failures[0] if invariant_failures else None,
                "first_exact_DP_replay_failure": replay_failures[0] if replay_failures else None,
            }
        if w["kind"] != "RESIDUAL":
            return {
                "rung": {"holes": h, "mode": mode},
                "meta": meta,
                "initial_CLV": [c0, l0, v0],
                "budget": budget,
                "status": "IMPLEMENTATION_FAILURE",
                "class": "UNEXPECTED_POLICY_KIND",
                "kind": w["kind"],
                "events": events,
            }

        core = r33.canonical_formula(w["state"])
        before = r33.measure(core)
        C, L, V = map(int, before)
        if V <= 0:
            return {"status": "IMPLEMENTATION_FAILURE", "class": "NONPOSITIVE_RESIDUAL_V", "rung": {"holes": h, "mode": mode}}

        raw_rows = []
        for var in r33.variables(core):
            rec = raw_dp_bound(core, int(var))
            if rec is None:
                continue
            rec["post_linear_pass"] = bool(2 * rec["RAW_S"] <= budget)
            rec["post_square_pass"] = bool(rec["RAW_S"] * rec["RAW_S"] <= budget * (V - 1)) if V > 1 else False
            rec["post_invariant_pass"] = rec["post_linear_pass"] and rec["post_square_pass"]
            raw_rows.append(rec)
        raw_rows.sort(key=lambda r: (r["RAW_S"], r["var"]))
        if not raw_rows:
            fail = {"outer_round": outer, "residual_hash": y.canonical_hash(core), "CLV": list(before), "class": "SELECTOR_HAS_NO_RAW_BOUND_PIVOT"}
            selector_failures.append(fail)
            return {"status": "SELECTOR_FAILURE", "rung": {"holes": h, "mode": mode}, "events": events, "failure": fail}

        admissible = [r for r in raw_rows if r["post_invariant_pass"]]
        best_raw = raw_rows[0]
        best_admissible = admissible[0] if admissible else None

        # Independent exact-DP materialization for the strongest raw-bound candidate.
        exact_best = y.exact_dp_record(core, best_raw["var"])
        if exact_best is None:
            return {"status": "IMPLEMENTATION_FAILURE", "class": "RAW_PIVOT_NO_EXACT_RECORD", "rung": {"holes": h, "mode": mode}}
        exact_after_s = int(exact_best["CLV_after"][0] + exact_best["CLV_after"][1])
        sound = exact_after_s <= int(best_raw["RAW_S"])
        replay_ok = bool(exact_best["replay_pass"])
        if not sound:
            soundness_failures.append({"outer_round": outer, "residual_hash": y.canonical_hash(core), "CLV": list(before), "raw": best_raw, "exact_CLV_after": exact_best["CLV_after"], "exact_S_after": exact_after_s})
        if not replay_ok:
            replay_failures.append({"outer_round": outer, "residual_hash": y.canonical_hash(core), "var": best_raw["var"]})
        if best_admissible is None:
            invariant_failures.append({
                "outer_round": outer,
                "residual_hash": y.canonical_hash(core),
                "CLV": list(before),
                "formula": [list(c) for c in core],
                "budget": budget,
                "best_raw": best_raw,
                "raw_pivot_count": len(raw_rows),
            })

        old_bounds = ab.selector_bounds(core)
        if not old_bounds:
            selector_failures.append({"outer_round": outer, "residual_hash": y.canonical_hash(core), "CLV": list(before), "class": "OLD_AF_SELECTOR_NO_PIVOT"})
            return {"status": "SELECTOR_FAILURE", "rung": {"holes": h, "mode": mode}, "events": events, "failure": selector_failures[-1]}
        old_var = int(old_bounds[0]["var"])
        old_exact = exact_best if old_var == best_raw["var"] else y.exact_dp_record(core, old_var)
        if old_exact is None or not old_exact.get("replay_pass"):
            old_selector_mismatch.append({"outer_round": outer, "residual_hash": y.canonical_hash(core), "old_var": old_var})
            return {"status": "IMPLEMENTATION_FAILURE", "class": "OLD_AF_SELECTOR_REPLAY_FAILURE", "rung": {"holes": h, "mode": mode}, "events": events}

        event = {
            "outer_round": outer,
            "residual_hash": y.canonical_hash(core),
            "CLV": list(before),
            "S": C + L,
            "V": V,
            "budget": budget,
            "raw_pivot_count": len(raw_rows),
            "admissible_raw_pivot_count": len(admissible),
            "best_RAW_S": int(best_raw["RAW_S"]),
            "best_raw_var": int(best_raw["var"]),
            "best_raw_exact_S_after": exact_after_s,
            "best_raw_sound": sound,
            "best_raw_replay_pass": replay_ok,
            "best_admissible_var": None if best_admissible is None else int(best_admissible["var"]),
            "best_admissible_RAW_S": None if best_admissible is None else int(best_admissible["RAW_S"]),
            "old_AF_var": old_var,
            "old_AF_UB_S": int(old_bounds[0]["UB_S"]),
            "raw_improvement_over_old_UB": int(old_bounds[0]["UB_S"] - best_raw["RAW_S"]),
            "post_invariant_exists": best_admissible is not None,
        }
        events.append(event)
        state = r33.canonical_formula(old_exact["transformed"])

    return {
        "rung": {"holes": h, "mode": mode},
        "meta": meta,
        "initial_CLV": [c0, l0, v0],
        "budget": budget,
        "status": "RESIDUAL_LIMIT",
        "events": events,
    }


def run():
    chain = r50g25g._chain()
    rows = [audit_rung(h, mode, chain) for h, mode in DOMAIN]
    soundness = sum(int(r.get("raw_bound_soundness_failure_count", 0)) for r in rows)
    invariant = sum(int(r.get("reachable_post_invariant_counterexample_count", 0)) for r in rows)
    replay = sum(int(r.get("exact_DP_replay_failure_count", 0)) for r in rows)
    selector = sum(int(r.get("selector_failure_count", 0)) for r in rows)
    semantic = sum(1 for r in rows if r.get("semantic_mismatch"))
    implementation = sum(1 for r in rows if r.get("status") == "IMPLEMENTATION_FAILURE")
    residual_limit = sum(1 for r in rows if r.get("status") == "RESIDUAL_LIMIT")
    total_events = sum(int(r.get("residual_event_count", len(r.get("events", [])))) for r in rows)
    all_events = [e for r in rows for e in r.get("events", [])]
    min_admissible = min((e["admissible_raw_pivot_count"] for e in all_events), default=0)
    max_improvement = max((e["raw_improvement_over_old_UB"] for e in all_events), default=0)
    min_improvement = min((e["raw_improvement_over_old_UB"] for e in all_events), default=0)

    if soundness:
        verdict = "RAW_BOUND_UNSOUND"
    elif invariant:
        verdict = "REACHABLE_POST_INVARIANT_COUNTEREXAMPLE"
    elif replay:
        verdict = "EXACT_DP_REPLAY_FAILURE"
    elif selector:
        verdict = "SELECTOR_HAS_NO_RAW_BOUND_PIVOT"
    elif semantic:
        verdict = "SEMANTIC_MISMATCH_ON_KNOWN_GPHP_UNSAT"
    elif implementation or residual_limit:
        verdict = "IMPLEMENTATION_OR_RESIDUAL_LIMIT"
    else:
        verdict = "STRUCTURE_AWARE_RAW_DP_BOUND_CLOSES_FROZEN_INVARIANT_ON_AF_REACHABLE_PREFIX"

    return {
        "gate": GATE,
        "AG_preregistration_commit": PREREG_COMMIT,
        "parent_AF_receipt_commit": AF_RECEIPT_COMMIT,
        "verdict": verdict,
        "domain": {"rungs": [{"holes": h, "mode": m} for h, m in DOMAIN], "truth_used_for_generation_or_pivot_selection": False},
        "root_reachable_residual_event_count": total_events,
        "raw_bound_soundness_failure_count": soundness,
        "reachable_post_invariant_counterexample_count": invariant,
        "exact_DP_replay_failure_count": replay,
        "selector_failure_count": selector,
        "semantic_mismatch_count": semantic,
        "implementation_failure_count": implementation,
        "residual_limit_count": residual_limit,
        "minimum_admissible_raw_pivots_per_residual": min_admissible,
        "raw_bound_improvement_over_old_UB": {"min": min_improvement, "max": max_improvement},
        "rows": rows,
        "next_gate": "R50G25AH_DERIVE_RAW_DP_BOUND_REACHABILITY_INDUCTION_OR_COUNTEREXAMPLE" if verdict.startswith("STRUCTURE_AWARE") else "R50G25AH_MINIMIZE_AG_REACHABLE_COUNTEREXAMPLE",
        "firewall": {
            "P_VS_NP": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "TRUMP_finished": False,
            "finite_AF_prefix_pass_is_not_universal_proof": True,
            "raw_bound_soundness_is_not_global_reachability": True,
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
        "root_reachable_residual_event_count": result["root_reachable_residual_event_count"],
        "raw_bound_soundness_failure_count": result["raw_bound_soundness_failure_count"],
        "reachable_post_invariant_counterexample_count": result["reachable_post_invariant_counterexample_count"],
        "exact_DP_replay_failure_count": result["exact_DP_replay_failure_count"],
        "selector_failure_count": result["selector_failure_count"],
        "semantic_mismatch_count": result["semantic_mismatch_count"],
        "minimum_admissible_raw_pivots_per_residual": result["minimum_admissible_raw_pivots_per_residual"],
        "raw_bound_improvement_over_old_UB": result["raw_bound_improvement_over_old_UB"],
        "next_gate": result["next_gate"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
