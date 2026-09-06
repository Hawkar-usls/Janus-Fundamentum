from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r50g25g_micro_rup_restart_replay_source_lift_family as r50g25g
import janus_trump_r50g25y_minimal_w_policy_counterexample_forensics as y
import janus_trump_r50g25ab_analytic_ub_pivot_selector_amortized_potential as ab
import janus_trump_r50g25ad_safe_envelope_reachability_gphp as ad

GATE = "JANUS_TRUMP_R50G25AH_DERIVE_RAW_DP_BOUND_REACHABILITY_INDUCTION_OR_COUNTEREXAMPLE"
PREREG_COMMIT = "b8a40ed136228d0ad5cae04454e79b6bfc93eb9d"
AG_RECEIPT_COMMIT = "5357a82bc3cfa069728b15449adaad20ff15fffc"
DOMAIN = tuple((h, m) for h in (6, 8, 10, 12, 16, 20) for m in ("CYCLIC_MIX", "SEEDED_BALANCED")) + (
    (24, "CYCLIC_MIX"),
    (24, "SEEDED_BALANCED"),
    (28, "CYCLIC_MIX"),
)


def terminal_label(w):
    if w.get("kind") == "AFFINE":
        return str(w["route"][-1].get("stop", "AFFINE")) if w.get("route") else "AFFINE"
    if w.get("kind") == "TERMINAL":
        return str(w["route"][-1].get("R33_terminal", "TERMINAL")) if w.get("route") else "TERMINAL"
    return None


def raw_mass_record(formula, var):
    formula = r33.canonical_formula(formula)
    C, L, V = map(int, r33.measure(formula))
    S = C + L

    # The AH identity is stated for tautology-free canonical clauses with one
    # occurrence per absolute variable in each clause.
    for clause in formula:
        av = [abs(int(l)) for l in clause]
        if len(av) != len(set(av)):
            return {"var": int(var), "identity_precondition_failure": True, "clause": list(clause)}

    pos = tuple(c for c in formula if var in c)
    neg = tuple(c for c in formula if -var in c)
    if not pos or not neg:
        return None

    base = tuple(c for c in formula if var not in c and -var not in c)
    base_mass = len(base) + sum(len(c) for c in base)
    removed_parent_mass = len(pos) + len(neg) + sum(len(c) for c in pos) + sum(len(c) for c in neg)

    pair_checks = 0
    tautological_pairs = 0
    pair_mass = 0
    non_tautological_pairs = 0
    for p in pos:
        for n in neg:
            pair_checks += 1
            merged = (set(p) - {var}) | (set(n) - {-var})
            if any(-lit in merged for lit in merged):
                tautological_pairs += 1
                continue
            resolvent = r33.canonical_clause(merged)
            non_tautological_pairs += 1
            pair_mass += 1 + len(resolvent)

    raw_s = base_mass + pair_mass
    local_identity_rhs = S - removed_parent_mass + pair_mass
    return {
        "var": int(var),
        "C": C,
        "L": L,
        "V": V,
        "S": S,
        "positive_parent_count": len(pos),
        "negative_parent_count": len(neg),
        "pair_checks": pair_checks,
        "tautological_pair_count": tautological_pairs,
        "non_tautological_pair_count": non_tautological_pairs,
        "removed_parent_mass": int(removed_parent_mass),
        "pair_mass": int(pair_mass),
        "base_mass": int(base_mass),
        "RAW_S": int(raw_s),
        "local_identity_rhs": int(local_identity_rhs),
        "local_identity_pass": bool(raw_s == local_identity_rhs),
        "identity_precondition_failure": False,
    }


def audit_residual(core, budget, outer):
    core = r33.canonical_formula(core)
    C, L, V = map(int, r33.measure(core))
    S = C + L
    residual_hash = y.canonical_hash(core)

    raw_rows = []
    for var in r33.variables(core):
        row = raw_mass_record(core, int(var))
        if row is not None:
            raw_rows.append(row)
    raw_rows.sort(key=lambda r: (int(r.get("RAW_S", 10**30)), int(r["var"])))

    identity_precondition_failure = any(bool(r.get("identity_precondition_failure")) for r in raw_rows)
    local_identity_failure = any(not bool(r.get("local_identity_pass", False)) for r in raw_rows)
    all_vars_have_bipolar_pivot = len(raw_rows) == V

    q2 = sum(len(c) * len(c) for c in core)
    sum_removed = sum(int(r.get("removed_parent_mass", 0)) for r in raw_rows)
    sum_pair_mass = sum(int(r.get("pair_mass", 0)) for r in raw_rows)
    sum_raw_s = sum(int(r.get("RAW_S", 0)) for r in raw_rows)
    expected_removed = L + q2
    aggregate_rhs = V * S - L - q2 + sum_pair_mass
    aggregate_identity_pass = bool(
        all_vars_have_bipolar_pivot
        and not identity_precondition_failure
        and not local_identity_failure
        and sum_removed == expected_removed
        and sum_raw_s == aggregate_rhs
    )

    T = 0 if V <= 1 else min(int(budget) // 2, math.isqrt(int(budget) * (V - 1)))
    average_condition_pass = bool(aggregate_identity_pass and sum_raw_s <= V * T)

    admissible = [
        r for r in raw_rows
        if not r.get("identity_precondition_failure")
        and 2 * int(r["RAW_S"]) <= int(budget)
        and int(r["RAW_S"]) * int(r["RAW_S"]) <= int(budget) * (V - 1)
    ] if V > 1 else []
    best = raw_rows[0] if raw_rows else None
    best_admissible = admissible[0] if admissible else None

    exact_soundness_pass = False
    exact_replay_pass = False
    exact_after_s = None
    if best is not None and not best.get("identity_precondition_failure"):
        exact = y.exact_dp_record(core, int(best["var"]))
        if exact is not None:
            exact_after_s = int(exact["CLV_after"][0] + exact["CLV_after"][1])
            exact_soundness_pass = bool(exact_after_s <= int(best["RAW_S"]))
            exact_replay_pass = bool(exact.get("replay_pass"))

    pre_invariant_pass = bool(2 * S <= int(budget) and S * S <= int(budget) * V)

    return {
        "outer_round": int(outer),
        "residual_hash": residual_hash,
        "CLV": [C, L, V],
        "S": S,
        "B": int(budget),
        "pre_invariant_pass": pre_invariant_pass,
        "raw_pivot_count": len(raw_rows),
        "all_variables_bipolar": all_vars_have_bipolar_pivot,
        "sum_clause_width_squared": int(q2),
        "sum_removed_parent_mass": int(sum_removed),
        "expected_sum_removed_L_plus_Q2": int(expected_removed),
        "sum_pair_mass": int(sum_pair_mass),
        "sum_RAW_S": int(sum_raw_s),
        "aggregate_identity_rhs": int(aggregate_rhs),
        "aggregate_identity_pass": aggregate_identity_pass,
        "local_identity_failure": local_identity_failure,
        "identity_precondition_failure": identity_precondition_failure,
        "T": int(T),
        "V_times_T": int(V * T),
        "average_condition_pass": average_condition_pass,
        "average_slack": int(V * T - sum_raw_s),
        "admissible_raw_pivot_count": len(admissible),
        "best_RAW_S": None if best is None else int(best["RAW_S"]),
        "best_raw_var": None if best is None else int(best["var"]),
        "best_admissible_RAW_S": None if best_admissible is None else int(best_admissible["RAW_S"]),
        "best_admissible_var": None if best_admissible is None else int(best_admissible["var"]),
        "best_exact_S_after": exact_after_s,
        "best_exact_soundness_pass": exact_soundness_pass,
        "best_exact_replay_pass": exact_replay_pass,
        "formula": [list(c) for c in core],
    }


def audit_case(h, mode, chain):
    initial, meta = ad.graph_php(h, mode)
    initial = r33.canonical_formula(initial)
    c0, l0, v0 = map(int, r33.measure(initial))
    budget = (c0 + l0) * ((v0 + 1) ** 2)
    state = initial
    events = []

    for outer in range(v0 + 1):
        w = y.policy_replay(state, chain)
        if w["kind"] in {"TERMINAL", "AFFINE"}:
            label = terminal_label(w)
            semantic_mismatch = not ("UNSAT" in label or "EMPTY_CLAUSE" in label)
            return {
                "rung": {"holes": h, "mode": mode},
                "meta": meta,
                "initial_CLV": [c0, l0, v0],
                "budget": int(budget),
                "status": "TERMINAL",
                "terminal_label": label,
                "semantic_mismatch": semantic_mismatch,
                "residual_event_count": len(events),
                "events": events,
            }
        if w["kind"] != "RESIDUAL":
            return {
                "rung": {"holes": h, "mode": mode},
                "meta": meta,
                "initial_CLV": [c0, l0, v0],
                "budget": int(budget),
                "status": "IMPLEMENTATION_FAILURE",
                "class": "UNEXPECTED_POLICY_KIND",
                "kind": w["kind"],
                "events": events,
            }

        core = r33.canonical_formula(w["state"])
        event = audit_residual(core, budget, outer)
        events.append(event)

        # Preserve the AB/AD/AF route exactly: old analytic UB selector chooses
        # the continuation pivot; AH's all-pivot audit does not alter reachability.
        old_bounds = ab.selector_bounds(core)
        if not old_bounds:
            return {
                "rung": {"holes": h, "mode": mode},
                "meta": meta,
                "initial_CLV": [c0, l0, v0],
                "budget": int(budget),
                "status": "IMPLEMENTATION_FAILURE",
                "class": "LEGACY_SELECTOR_HAS_NO_PIVOT",
                "events": events,
            }
        old_var = int(old_bounds[0]["var"])
        exact_old = y.exact_dp_record(core, old_var)
        if exact_old is None or not exact_old.get("replay_pass"):
            return {
                "rung": {"holes": h, "mode": mode},
                "meta": meta,
                "initial_CLV": [c0, l0, v0],
                "budget": int(budget),
                "status": "IMPLEMENTATION_FAILURE",
                "class": "LEGACY_SELECTOR_EXACT_DP_REPLAY_FAILURE",
                "events": events,
            }
        event["legacy_route_var"] = old_var
        event["legacy_route_UB_S"] = int(old_bounds[0]["UB_S"])
        state = r33.canonical_formula(exact_old["transformed"])

    return {
        "rung": {"holes": h, "mode": mode},
        "meta": meta,
        "initial_CLV": [c0, l0, v0],
        "budget": int(budget),
        "status": "RESOURCE_OR_RESIDUAL_LIMIT",
        "events": events,
    }


def run():
    chain = r50g25g._chain()
    rows = [audit_case(h, mode, chain) for h, mode in DOMAIN]
    events = [e for row in rows for e in row.get("events", [])]

    actual_no_pivot = [e for e in events if int(e.get("admissible_raw_pivot_count", 0)) == 0]
    identity_or_soundness = [
        e for e in events
        if not bool(e.get("aggregate_identity_pass"))
        or not bool(e.get("best_exact_soundness_pass"))
        or not bool(e.get("pre_invariant_pass"))
    ]
    replay_failures = [e for e in events if not bool(e.get("best_exact_replay_pass"))]
    average_gaps = [
        e for e in events
        if not bool(e.get("average_condition_pass")) and int(e.get("admissible_raw_pivot_count", 0)) > 0
    ]
    semantic_mismatches = [row for row in rows if row.get("semantic_mismatch")]
    implementation_failures = [row for row in rows if row.get("status") == "IMPLEMENTATION_FAILURE"]
    resource_limits = [row for row in rows if row.get("status") == "RESOURCE_OR_RESIDUAL_LIMIT"]

    if actual_no_pivot:
        verdict = "REACHABLE_NO_ADMISSIBLE_RAW_DP_PIVOT"
    elif identity_or_soundness or implementation_failures:
        verdict = "RAW_IDENTITY_OR_SOUNDNESS_FAILURE"
    elif replay_failures:
        verdict = "EXACT_DP_REPLAY_FAILURE"
    elif semantic_mismatches:
        verdict = "SEMANTIC_MISMATCH_ON_KNOWN_GPHP_UNSAT"
    elif average_gaps:
        verdict = "AVERAGE_CERTIFICATE_GAP_BUT_ADMISSIBLE_RAW_PIVOT_EXISTS"
    elif resource_limits:
        verdict = "RESOURCE_LIMIT"
    else:
        verdict = "AVERAGE_RAW_MASS_CERTIFICATE_CLOSES_REACHABLE_DOMAIN"

    min_admissible = min((int(e["admissible_raw_pivot_count"]) for e in events), default=0)
    min_average_slack = min((int(e["average_slack"]) for e in events), default=0)
    max_average_slack = max((int(e["average_slack"]) for e in events), default=0)

    return {
        "gate": GATE,
        "AH_preregistration_commit": PREREG_COMMIT,
        "parent_AG_receipt_commit": AG_RECEIPT_COMMIT,
        "verdict": verdict,
        "domain": {
            "root_count": len(rows),
            "roots": [{"holes": h, "mode": mode} for h, mode in DOMAIN],
            "truth_used_for_generation_or_pivot_selection": False,
            "legacy_route_preserved": True,
        },
        "root_reachable_residual_event_count": len(events),
        "average_certificate_gap_count": len(average_gaps),
        "reachable_no_admissible_raw_pivot_count": len(actual_no_pivot),
        "raw_identity_or_soundness_failure_count": len(identity_or_soundness),
        "exact_DP_replay_failure_count": len(replay_failures),
        "semantic_mismatch_count": len(semantic_mismatches),
        "implementation_failure_count": len(implementation_failures),
        "resource_limit_count": len(resource_limits),
        "minimum_admissible_raw_pivots_per_residual": min_admissible,
        "average_certificate_slack": {"min": min_average_slack, "max": max_average_slack},
        "first_average_gap": average_gaps[0] if average_gaps else None,
        "first_reachable_no_admissible_raw_pivot": actual_no_pivot[0] if actual_no_pivot else None,
        "first_identity_or_soundness_failure": identity_or_soundness[0] if identity_or_soundness else None,
        "rows": rows,
        "recommended_next_gate": (
            "R50G25AI_MINIMIZE_REACHABLE_NO_RAW_PIVOT_COUNTEREXAMPLE" if actual_no_pivot else
            "R50G25AI_STRENGTHEN_AVERAGE_CERTIFICATE_WITH_RESIDUAL_INCIDENCE_STRUCTURE" if average_gaps else
            "R50G25AI_LIFT_AVERAGE_RAW_MASS_CERTIFICATE_TO_SYMBOLIC_RESIDUAL_CLASS"
        ),
        "firewall": {
            "P_VS_NP": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "TRUMP_finished": False,
            "finite_reachable_pass_is_not_universal_induction": True,
            "average_certificate_is_sufficient_not_necessary": True,
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
        "average_certificate_gap_count": result["average_certificate_gap_count"],
        "reachable_no_admissible_raw_pivot_count": result["reachable_no_admissible_raw_pivot_count"],
        "raw_identity_or_soundness_failure_count": result["raw_identity_or_soundness_failure_count"],
        "exact_DP_replay_failure_count": result["exact_DP_replay_failure_count"],
        "semantic_mismatch_count": result["semantic_mismatch_count"],
        "minimum_admissible_raw_pivots_per_residual": result["minimum_admissible_raw_pivots_per_residual"],
        "average_certificate_slack": result["average_certificate_slack"],
        "recommended_next_gate": result["recommended_next_gate"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
