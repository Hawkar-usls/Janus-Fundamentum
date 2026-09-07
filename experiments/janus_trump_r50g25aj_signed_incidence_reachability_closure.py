from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r50g25g_micro_rup_restart_replay_source_lift_family as r50g25g
import janus_trump_r50g25y_minimal_w_policy_counterexample_forensics as y
import janus_trump_r50g25ad_safe_envelope_reachability_gphp as ad
import janus_trump_r50g25ah_raw_dp_reachability_induction as ah
import janus_trump_r50g25ai_symbolic_signed_incidence_residual_class as ai

GATE = "JANUS_TRUMP_R50G25AJ_PROVE_REACHABILITY_INTO_SIGNED_INCIDENCE_CLASS_OR_FIND_COUNTEREXAMPLE"
PREREG_COMMIT = "6bfd79052f91c0b08348f9f4bc5f1e359c651389"
AI_RECEIPT_COMMIT = "f7c722b875e822c7c223a40571e375852616e4eb"
DOMAIN = ah.DOMAIN


def terminal_label(w):
    if w.get("kind") == "AFFINE":
        return str(w["route"][-1].get("stop", "AFFINE")) if w.get("route") else "AFFINE"
    if w.get("kind") == "TERMINAL":
        return str(w["route"][-1].get("R33_terminal", "TERMINAL")) if w.get("route") else "TERMINAL"
    return None


def local_signed_incidence_bound(formula, budget, var):
    f = r33.canonical_formula(formula)
    C, L, V = map(int, r33.measure(f))
    S = C + L
    pos = [c for c in f if var in c]
    neg = [c for c in f if -var in c]
    if not pos or not neg or V <= 1:
        return None
    a = len(pos)
    b = len(neg)
    A = sum(len(c) for c in pos)
    Bx = sum(len(c) for c in neg)
    removed_parent_mass = a + b + A + Bx
    pair_mass_ub = b * A + a * Bx - a * b
    raw_s_ub = S - removed_parent_mass + pair_mass_ub
    T = min(int(budget) // 2, math.isqrt(int(budget) * (V - 1)))
    return {
        "var": int(var),
        "a_pos": int(a),
        "b_neg": int(b),
        "A_pos_width_sum": int(A),
        "B_neg_width_sum": int(Bx),
        "removed_parent_mass": int(removed_parent_mass),
        "pair_mass_UB": int(pair_mass_ub),
        "RAW_S_UB": int(raw_s_ub),
        "T": int(T),
        "envelope_admissible": bool(raw_s_ub <= T),
    }


def audit_case(h, mode, chain):
    initial, meta = ad.graph_php(h, mode)
    initial = r33.canonical_formula(initial)
    c0, l0, v0 = map(int, r33.measure(initial))
    budget = (c0 + l0) * ((v0 + 1) ** 2)
    state = initial
    events = []
    total_candidates_tested = 0
    max_candidates_tested = 0

    for outer in range(v0 + 1):
        w = y.policy_replay(state, chain)
        if w["kind"] in {"TERMINAL", "AFFINE"}:
            label = terminal_label(w)
            semantic_mismatch = not ("UNSAT" in str(label) or "EMPTY_CLAUSE" in str(label))
            return {
                "rung": {"holes": h, "mode": mode},
                "meta": meta,
                "initial_CLV": [c0, l0, v0],
                "budget": int(budget),
                "status": "TERMINAL",
                "terminal_label": label,
                "semantic_mismatch": semantic_mismatch,
                "residual_event_count": len(events),
                "total_candidates_tested": total_candidates_tested,
                "max_candidates_tested_per_residual": max_candidates_tested,
                "events": events,
            }
        if w["kind"] != "RESIDUAL":
            return {
                "rung": {"holes": h, "mode": mode},
                "status": "IMPLEMENTATION_FAILURE",
                "class": "UNEXPECTED_POLICY_KIND",
                "kind": w.get("kind"),
                "events": events,
            }

        core = r33.canonical_formula(w["state"])
        C, L, V = map(int, r33.measure(core))
        parent_class = ai.signed_incidence_record(core, budget)
        if not parent_class["symbolic_class_pass"]:
            return {
                "rung": {"holes": h, "mode": mode},
                "status": "COUNTEREXAMPLE",
                "class": "PARENT_RESIDUAL_OUTSIDE_SIGNED_INCIDENCE_CLASS",
                "outer_round": outer,
                "residual_hash": y.canonical_hash(core),
                "CLV": [C, L, V],
                "budget": int(budget),
                "signed_incidence": parent_class,
                "formula": [list(c) for c in core],
                "events": events,
            }

        bounds = []
        for var in r33.variables(core):
            rec = local_signed_incidence_bound(core, budget, int(var))
            if rec is not None and rec["envelope_admissible"]:
                bounds.append(rec)
        bounds.sort(key=lambda r: (r["RAW_S_UB"], r["var"]))
        if not bounds:
            return {
                "rung": {"holes": h, "mode": mode},
                "status": "COUNTEREXAMPLE",
                "class": "NO_ENVELOPE_ADMISSIBLE_SIGNED_INCIDENCE_PIVOT",
                "outer_round": outer,
                "residual_hash": y.canonical_hash(core),
                "CLV": [C, L, V],
                "budget": int(budget),
                "signed_incidence": parent_class,
                "formula": [list(c) for c in core],
                "events": events,
            }

        tested = []
        chosen = None
        for bound in bounds:
            var = int(bound["var"])
            exact = y.exact_dp_record(core, var)
            if exact is None or not exact.get("replay_pass"):
                return {
                    "rung": {"holes": h, "mode": mode},
                    "status": "COUNTEREXAMPLE",
                    "class": "EXACT_DP_REPLAY_FAILURE",
                    "outer_round": outer,
                    "residual_hash": y.canonical_hash(core),
                    "var": var,
                    "events": events,
                }
            exact_after_s = int(exact["CLV_after"][0] + exact["CLV_after"][1])
            if exact_after_s > int(bound["RAW_S_UB"]):
                return {
                    "rung": {"holes": h, "mode": mode},
                    "status": "IMPLEMENTATION_FAILURE",
                    "class": "SIGNED_INCIDENCE_LOCAL_BOUND_UNSOUND",
                    "outer_round": outer,
                    "residual_hash": y.canonical_hash(core),
                    "bound": bound,
                    "exact_CLV_after": exact["CLV_after"],
                    "events": events,
                }
            if int(exact["CLV_after"][2]) >= V:
                return {
                    "rung": {"holes": h, "mode": mode},
                    "status": "IMPLEMENTATION_FAILURE",
                    "class": "DP_DOES_NOT_DECREASE_VARIABLE_COUNT",
                    "outer_round": outer,
                    "residual_hash": y.canonical_hash(core),
                    "var": var,
                    "events": events,
                }

            child = y.policy_replay(r33.canonical_formula(exact["transformed"]), chain)
            child_terminal = child["kind"] in {"TERMINAL", "AFFINE"}
            child_class_pass = False
            child_hash = None
            child_clv = None
            child_slack = None
            child_label = None
            if child_terminal:
                child_label = terminal_label(child)
                child_class_pass = True
            elif child["kind"] == "RESIDUAL":
                child_core = r33.canonical_formula(child["state"])
                child_hash = y.canonical_hash(child_core)
                child_clv = list(r33.measure(child_core))
                child_si = ai.signed_incidence_record(child_core, budget)
                child_class_pass = bool(child_si["symbolic_class_pass"])
                child_slack = int(child_si["symbolic_class_slack"])
            else:
                return {
                    "rung": {"holes": h, "mode": mode},
                    "status": "IMPLEMENTATION_FAILURE",
                    "class": "UNEXPECTED_CHILD_POLICY_KIND",
                    "outer_round": outer,
                    "kind": child.get("kind"),
                    "events": events,
                }

            attempt = {
                "var": var,
                "RAW_S_UB": int(bound["RAW_S_UB"]),
                "T": int(bound["T"]),
                "exact_CLV_after": list(exact["CLV_after"]),
                "exact_S_after": exact_after_s,
                "child_kind": child["kind"],
                "child_terminal_label": child_label,
                "child_residual_hash": child_hash,
                "child_residual_CLV": child_clv,
                "child_symbolic_class_pass": bool(child_class_pass),
                "child_symbolic_class_slack": child_slack,
            }
            tested.append(attempt)
            if child_class_pass:
                chosen = (bound, exact, attempt)
                break

        total_candidates_tested += len(tested)
        max_candidates_tested = max(max_candidates_tested, len(tested))
        if len(tested) > V:
            return {
                "rung": {"holes": h, "mode": mode},
                "status": "COUNTEREXAMPLE",
                "class": "POLYNOMIAL_LEDGER_FAILURE",
                "outer_round": outer,
                "tested": len(tested),
                "V": V,
                "events": events,
            }
        if chosen is None:
            return {
                "rung": {"holes": h, "mode": mode},
                "status": "COUNTEREXAMPLE",
                "class": "NO_SELF_PRESERVING_SIGNED_INCIDENCE_PIVOT",
                "outer_round": outer,
                "residual_hash": y.canonical_hash(core),
                "CLV": [C, L, V],
                "budget": int(budget),
                "signed_incidence": parent_class,
                "admissible_pivot_count": len(bounds),
                "tested": tested,
                "formula": [list(c) for c in core],
                "events": events,
            }

        bound, exact, attempt = chosen
        event = {
            "outer_round": outer,
            "residual_hash": y.canonical_hash(core),
            "CLV": [C, L, V],
            "budget": int(budget),
            "parent_symbolic_class_slack": int(parent_class["symbolic_class_slack"]),
            "envelope_admissible_pivot_count": len(bounds),
            "candidates_tested_before_self_preserving": len(tested),
            "chosen_var": int(bound["var"]),
            "chosen_RAW_S_UB": int(bound["RAW_S_UB"]),
            "chosen_T": int(bound["T"]),
            "chosen_exact_CLV_after": list(exact["CLV_after"]),
            "landing": attempt,
        }
        events.append(event)
        state = r33.canonical_formula(exact["transformed"])

    return {
        "rung": {"holes": h, "mode": mode},
        "status": "RESIDUAL_LIMIT",
        "initial_CLV": [c0, l0, v0],
        "budget": int(budget),
        "events": events,
    }


def run():
    chain = r50g25g._chain()
    rows = [audit_case(h, mode, chain) for h, mode in DOMAIN]
    failures = [r for r in rows if r.get("status") in {"COUNTEREXAMPLE", "IMPLEMENTATION_FAILURE", "RESIDUAL_LIMIT"}]
    semantic = [r for r in rows if r.get("semantic_mismatch")]
    events = [e for r in rows for e in r.get("events", [])]

    classes = {}
    for r in failures:
        classes[r.get("class", r.get("status", "UNKNOWN"))] = classes.get(r.get("class", r.get("status", "UNKNOWN")), 0) + 1

    if any(r.get("class") == "PARENT_RESIDUAL_OUTSIDE_SIGNED_INCIDENCE_CLASS" for r in failures):
        verdict = "PARENT_RESIDUAL_OUTSIDE_SIGNED_INCIDENCE_CLASS"
    elif any(r.get("class") == "NO_ENVELOPE_ADMISSIBLE_SIGNED_INCIDENCE_PIVOT" for r in failures):
        verdict = "NO_ENVELOPE_ADMISSIBLE_SIGNED_INCIDENCE_PIVOT"
    elif any(r.get("class") == "NO_SELF_PRESERVING_SIGNED_INCIDENCE_PIVOT" for r in failures):
        verdict = "NO_SELF_PRESERVING_SIGNED_INCIDENCE_PIVOT"
    elif any(r.get("class") == "EXACT_DP_REPLAY_FAILURE" for r in failures):
        verdict = "EXACT_DP_REPLAY_FAILURE"
    elif semantic:
        verdict = "SEMANTIC_MISMATCH"
    elif any(r.get("class") == "POLYNOMIAL_LEDGER_FAILURE" for r in failures):
        verdict = "POLYNOMIAL_LEDGER_FAILURE"
    elif failures:
        verdict = "IMPLEMENTATION_OR_RESOURCE_FAILURE"
    else:
        verdict = "SELF_PRESERVING_SIGNED_INCIDENCE_PIVOT_EXISTS_ON_FROZEN_REACHABLE_DOMAIN"

    return {
        "gate": GATE,
        "AJ_preregistration_commit": PREREG_COMMIT,
        "parent_AI_receipt_commit": AI_RECEIPT_COMMIT,
        "verdict": verdict,
        "domain": {
            "root_count": len(rows),
            "roots": [{"holes": h, "mode": m} for h, m in DOMAIN],
            "truth_used_for_generation_or_pivot_selection": False,
            "route": "AJ self-preserving signed-incidence selector",
        },
        "root_reachable_residual_event_count": len(events),
        "failure_count": len(failures),
        "failure_classes": classes,
        "semantic_mismatch_count": len(semantic),
        "minimum_envelope_admissible_pivots_per_residual": min((e["envelope_admissible_pivot_count"] for e in events), default=0),
        "maximum_candidates_tested_before_self_preserving": max((e["candidates_tested_before_self_preserving"] for e in events), default=0),
        "total_candidates_tested": sum(int(r.get("total_candidates_tested", 0)) for r in rows),
        "first_failure": failures[0] if failures else None,
        "rows": rows,
        "interpretation": {
            "what_success_means": "On the frozen 15-root domain, the polynomially enumerable signed-incidence admissible pivot set contains a self-preserving exact-DP door at every AJ-reachable residual; the AJ route therefore remains inside the AI class until terminal.",
            "what_success_does_not_mean": "This finite inductive replay is not a universal proof for arbitrary CNF. A symbolic theorem that every arbitrary-CNF reachable residual has a self-preserving signed-incidence pivot remains open.",
        },
        "recommended_next_gate": "R50G25AK_SYMBOLIC_SELF_PRESERVING_PIVOT_EXISTENCE_OR_REACHABLE_COUNTEREXAMPLE" if verdict.startswith("SELF_PRESERVING") else "R50G25AK_MINIMIZE_AJ_COUNTEREXAMPLE",
        "firewall": {
            "P_VS_NP": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "TRUMP_finished": False,
            "finite_closure_pass_is_not_universal_reachability_proof": True,
            "class_membership_is_sufficient_not_necessary": True,
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
        "gate", "verdict", "root_reachable_residual_event_count", "failure_count",
        "failure_classes", "semantic_mismatch_count",
        "minimum_envelope_admissible_pivots_per_residual",
        "maximum_candidates_tested_before_self_preserving", "total_candidates_tested",
        "recommended_next_gate",
    ]
    print(json.dumps({k: result.get(k) for k in keys}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
