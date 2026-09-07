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
import janus_trump_r50g25aj_signed_incidence_reachability_closure as aj

GATE = "JANUS_TRUMP_R50G25AK_SYMBOLIC_SELF_PRESERVING_PIVOT_EXISTENCE_OR_REACHABLE_COUNTEREXAMPLE"
PREREG_COMMIT = "21a180bb250e2b7d6c9ed999b1466f40af050fbe"
AJ_RECEIPT_COMMIT = "ecf18c41dc1af7311085f87a5dc4a4909c044aa5"
DOMAIN = ah.DOMAIN


def parent_only_child_certificate(formula, budget, var):
    f = r33.canonical_formula(formula)
    C, L, V = map(int, r33.measure(f))
    if V <= 2:
        return None
    local = aj.local_signed_incidence_bound(f, budget, int(var))
    if local is None or not local["envelope_admissible"]:
        return None

    pos_x = [c for c in f if var in c]
    neg_x = [c for c in f if -var in c]
    outside = [c for c in f if var not in c and -var not in c]
    a = len(pos_x)
    b = len(neg_x)
    A = sum(len(c) for c in pos_x)
    Bx = sum(len(c) for c in neg_x)

    child_rows = []
    p_hat_child_ub = 0
    operation_ledger = 0
    for z in r33.variables(f):
        if z == var:
            continue
        sign_data = {}
        for lit, label in ((z, "pos"), (-z, "neg")):
            outside_hit = [c for c in outside if lit in c]
            p_hit = [c for c in pos_x if lit in c]
            n_hit = [c for c in neg_x if lit in c]
            outside_count = len(outside_hit)
            outside_width = sum(len(c) for c in outside_hit)
            cp = len(p_hit)
            cn = len(n_hit)
            wp = sum(len(c) for c in p_hit)
            wn = sum(len(c) for c in n_hit)
            generated_count_ub = cp * b + cn * a
            generated_width_ub = (
                b * wp + cp * Bx - 2 * cp * b
                + a * wn + cn * A - 2 * cn * a
            )
            count_ub = outside_count + generated_count_ub
            width_ub = outside_width + generated_width_ub
            sign_data[label] = {
                "count_UB": int(count_ub),
                "width_sum_UB": int(width_ub),
                "outside_count": int(outside_count),
                "generated_count_UB": int(generated_count_ub),
            }
            operation_ledger += len(outside) + len(pos_x) + len(neg_x)

        a_pos_ub = sign_data["pos"]["count_UB"]
        b_neg_ub = sign_data["neg"]["count_UB"]
        A_pos_ub = sign_data["pos"]["width_sum_UB"]
        B_neg_ub = sign_data["neg"]["width_sum_UB"]
        # Safe but intentionally coarse: drop the negative -a*b term.
        local_p_hat_ub = b_neg_ub * A_pos_ub + a_pos_ub * B_neg_ub
        p_hat_child_ub += local_p_hat_ub
        child_rows.append({
            "var": int(z),
            "positive": sign_data["pos"],
            "negative": sign_data["neg"],
            "P_hat_local_UB_without_negative_product": int(local_p_hat_ub),
        })

    child_v_assumed = V - 1
    child_s_ub = int(local["RAW_S_UB"])
    child_t = min(int(budget) // 2, math.isqrt(int(budget) * (child_v_assumed - 1)))
    # Dropping -L'-Q2' is conservative, so this is a genuine upper bound if
    # exactly one variable disappears under exact DP.
    child_class_lhs_ub = child_v_assumed * child_s_ub + p_hat_child_ub
    child_class_rhs = child_v_assumed * child_t
    certificate_pass = child_class_lhs_ub <= child_class_rhs

    return {
        "var": int(var),
        "parent_CLV": [C, L, V],
        "parent_local_RAW_S_UB": child_s_ub,
        "parent_local_T": int(local["T"]),
        "child_V_assumed": int(child_v_assumed),
        "child_T": int(child_t),
        "child_S_UB": int(child_s_ub),
        "child_P_hat_UB": int(p_hat_child_ub),
        "child_class_LHS_UB": int(child_class_lhs_ub),
        "child_class_RHS": int(child_class_rhs),
        "symbolic_self_preservation_pass": bool(certificate_pass),
        "symbolic_slack": int(child_class_rhs - child_class_lhs_ub),
        "operation_ledger_upper": int(operation_ledger),
        "child_rows": child_rows,
    }


def actual_landing(core, budget, var, chain):
    exact = y.exact_dp_record(core, int(var))
    if exact is None or not exact.get("replay_pass"):
        return {"ok": False, "class": "EXACT_DP_REPLAY_FAILURE", "var": int(var)}
    transformed = r33.canonical_formula(exact["transformed"])
    raw_clv = list(r33.measure(transformed))
    raw_si = ai.signed_incidence_record(transformed, budget) if raw_clv[2] > 1 else None
    child = y.policy_replay(transformed, chain)
    if child["kind"] in {"TERMINAL", "AFFINE"}:
        return {
            "ok": True,
            "self_preserving": True,
            "terminal": True,
            "terminal_label": aj.terminal_label(child),
            "exact_CLV_after": list(exact["CLV_after"]),
            "raw_child_CLV": raw_clv,
            "raw_child_AI_class_pass": None if raw_si is None else bool(raw_si["symbolic_class_pass"]),
        }
    if child["kind"] != "RESIDUAL":
        return {"ok": False, "class": "UNEXPECTED_CHILD_POLICY_KIND", "kind": child.get("kind")}
    child_core = r33.canonical_formula(child["state"])
    child_si = ai.signed_incidence_record(child_core, budget)
    return {
        "ok": True,
        "self_preserving": bool(child_si["symbolic_class_pass"]),
        "terminal": False,
        "exact_CLV_after": list(exact["CLV_after"]),
        "raw_child_CLV": raw_clv,
        "raw_child_AI_class_pass": None if raw_si is None else bool(raw_si["symbolic_class_pass"]),
        "child_residual_hash": y.canonical_hash(child_core),
        "child_residual_CLV": list(r33.measure(child_core)),
        "child_symbolic_class_pass": bool(child_si["symbolic_class_pass"]),
        "child_symbolic_class_slack": int(child_si["symbolic_class_slack"]),
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
            label = aj.terminal_label(w)
            return {
                "rung": {"holes": h, "mode": mode},
                "status": "TERMINAL",
                "terminal_label": label,
                "semantic_mismatch": not ("UNSAT" in str(label) or "EMPTY_CLAUSE" in str(label)),
                "initial_CLV": [c0, l0, v0],
                "budget": int(budget),
                "events": events,
            }
        if w["kind"] != "RESIDUAL":
            return {"rung": {"holes": h, "mode": mode}, "status": "FAILURE", "class": "UNEXPECTED_POLICY_KIND", "events": events}

        core = r33.canonical_formula(w["state"])
        C, L, V = map(int, r33.measure(core))
        parent_si = ai.signed_incidence_record(core, budget)
        if not parent_si["symbolic_class_pass"]:
            return {
                "rung": {"holes": h, "mode": mode}, "status": "COUNTEREXAMPLE",
                "class": "PARENT_OUTSIDE_AI_CLASS", "outer_round": outer,
                "residual_hash": y.canonical_hash(core), "CLV": [C, L, V],
                "formula": [list(c) for c in core], "events": events,
            }

        admissible = []
        for var in r33.variables(core):
            b = aj.local_signed_incidence_bound(core, budget, int(var))
            if b is not None and b["envelope_admissible"]:
                admissible.append(b)
        admissible.sort(key=lambda r: (r["RAW_S_UB"], r["var"]))
        if not admissible:
            return {
                "rung": {"holes": h, "mode": mode}, "status": "COUNTEREXAMPLE",
                "class": "NO_ENVELOPE_ADMISSIBLE_PIVOT", "outer_round": outer,
                "residual_hash": y.canonical_hash(core), "CLV": [C, L, V],
                "formula": [list(c) for c in core], "events": events,
            }

        symbolic_rows = []
        chosen_symbolic = None
        for b in admissible:
            cert = parent_only_child_certificate(core, budget, int(b["var"]))
            if cert is None:
                continue
            symbolic_rows.append(cert)
            if cert["symbolic_self_preservation_pass"]:
                chosen_symbolic = cert
                break

        if chosen_symbolic is not None:
            var = int(chosen_symbolic["var"])
            actual = actual_landing(core, budget, var, chain)
            if not actual.get("ok"):
                return {"rung": {"holes": h, "mode": mode}, "status": "COUNTEREXAMPLE", "class": actual.get("class"), "outer_round": outer, "events": events}
            # Soundness check of the parent-only certificate. Its proof assumes
            # one eliminated variable and claims raw exact-DP child class membership.
            if int(actual["exact_CLV_after"][2]) != V - 1 or actual.get("raw_child_AI_class_pass") is not True:
                return {
                    "rung": {"holes": h, "mode": mode}, "status": "COUNTEREXAMPLE",
                    "class": "PARENT_ONLY_CHILD_BOUND_UNSOUND", "outer_round": outer,
                    "residual_hash": y.canonical_hash(core), "CLV": [C, L, V],
                    "certificate": chosen_symbolic, "actual": actual,
                    "formula": [list(c) for c in core], "events": events,
                }
            if not actual["self_preserving"]:
                return {
                    "rung": {"holes": h, "mode": mode}, "status": "COUNTEREXAMPLE",
                    "class": "NO_ACTUAL_SELF_PRESERVING_PIVOT", "outer_round": outer,
                    "residual_hash": y.canonical_hash(core), "certificate": chosen_symbolic,
                    "actual": actual, "formula": [list(c) for c in core], "events": events,
                }
            chosen = chosen_symbolic
            route_kind = "SYMBOLIC_CERTIFIED"
        else:
            # Freeze the proof gap before checking whether the solver still has
            # an actual AJ self-preserving door. This distinguishes theorem-gap
            # from machine counterexample.
            actual_door = None
            actual_attempts = []
            for b in admissible:
                var = int(b["var"])
                actual = actual_landing(core, budget, var, chain)
                actual_attempts.append({"var": var, "RAW_S_UB": int(b["RAW_S_UB"]), "actual": actual})
                if actual.get("ok") and actual.get("self_preserving"):
                    actual_door = (b, actual)
                    break
            if actual_door is None:
                return {
                    "rung": {"holes": h, "mode": mode}, "status": "COUNTEREXAMPLE",
                    "class": "NO_ACTUAL_SELF_PRESERVING_PIVOT", "outer_round": outer,
                    "residual_hash": y.canonical_hash(core), "CLV": [C, L, V],
                    "symbolic_certificates": symbolic_rows, "actual_attempts": actual_attempts,
                    "formula": [list(c) for c in core], "events": events,
                }
            b, actual = actual_door
            return {
                "rung": {"holes": h, "mode": mode}, "status": "SYMBOLIC_GAP",
                "class": "SYMBOLIC_SELF_PRESERVATION_CERTIFICATE_GAP_BUT_ACTUAL_DOOR_EXISTS",
                "outer_round": outer, "residual_hash": y.canonical_hash(core),
                "CLV": [C, L, V], "budget": int(budget),
                "parent_symbolic_class_slack": int(parent_si["symbolic_class_slack"]),
                "admissible_pivot_count": len(admissible),
                "symbolic_certificates": symbolic_rows,
                "first_actual_self_preserving_var": int(b["var"]),
                "first_actual_self_preserving": actual,
                "formula": [list(c) for c in core], "events": events,
            }

        event = {
            "outer_round": outer,
            "residual_hash": y.canonical_hash(core),
            "CLV": [C, L, V],
            "parent_symbolic_class_slack": int(parent_si["symbolic_class_slack"]),
            "admissible_pivot_count": len(admissible),
            "symbolic_candidates_tested": len(symbolic_rows),
            "chosen_var": int(chosen["var"]),
            "chosen_symbolic_slack": int(chosen["symbolic_slack"]),
            "route_kind": route_kind,
        }
        events.append(event)
        exact = y.exact_dp_record(core, int(chosen["var"]))
        state = r33.canonical_formula(exact["transformed"])

    return {"rung": {"holes": h, "mode": mode}, "status": "RESOURCE_LIMIT", "events": events}


def run():
    chain = r50g25g._chain()
    rows = []
    for h, mode in DOMAIN:
        row = audit_case(h, mode, chain)
        rows.append(row)
        if row.get("status") in {"COUNTEREXAMPLE", "SYMBOLIC_GAP", "FAILURE", "RESOURCE_LIMIT"}:
            break

    events = [e for r in rows for e in r.get("events", [])]
    first_nonterminal = next((r for r in rows if r.get("status") not in {"TERMINAL"}), None)
    semantic = [r for r in rows if r.get("semantic_mismatch")]

    if first_nonterminal is None and not semantic:
        verdict = "PARENT_ONLY_SYMBOLIC_SELF_PRESERVATION_CERTIFICATE_COVERS_FROZEN_DOMAIN"
    elif first_nonterminal and first_nonterminal.get("class") == "SYMBOLIC_SELF_PRESERVATION_CERTIFICATE_GAP_BUT_ACTUAL_DOOR_EXISTS":
        verdict = "SYMBOLIC_SELF_PRESERVATION_CERTIFICATE_GAP_BUT_ACTUAL_DOOR_EXISTS"
    elif first_nonterminal and first_nonterminal.get("class") == "PARENT_ONLY_CHILD_BOUND_UNSOUND":
        verdict = "PARENT_ONLY_CHILD_BOUND_UNSOUND"
    elif first_nonterminal and first_nonterminal.get("class") == "NO_ACTUAL_SELF_PRESERVING_PIVOT":
        verdict = "NO_ACTUAL_SELF_PRESERVING_PIVOT"
    elif semantic:
        verdict = "SEMANTIC_MISMATCH"
    elif first_nonterminal and first_nonterminal.get("status") == "RESOURCE_LIMIT":
        verdict = "RESOURCE_LIMIT"
    else:
        verdict = first_nonterminal.get("class", "IMPLEMENTATION_FAILURE") if first_nonterminal else "IMPLEMENTATION_FAILURE"

    return {
        "gate": GATE,
        "AK_preregistration_commit": PREREG_COMMIT,
        "parent_AJ_receipt_commit": AJ_RECEIPT_COMMIT,
        "verdict": verdict,
        "root_count_completed_or_attempted": len(rows),
        "symbolically_certified_residual_event_count": len(events),
        "semantic_mismatch_count": len(semantic),
        "minimum_symbolic_slack": min((e["chosen_symbolic_slack"] for e in events), default=0),
        "maximum_symbolic_candidates_tested": max((e["symbolic_candidates_tested"] for e in events), default=0),
        "first_nonterminal_result": first_nonterminal,
        "rows": rows,
        "recommended_next_gate": (
            "R50G25AL_DERIVE_TIGHTER_CHILD_SIGNED_INCIDENCE_BOUND" if verdict == "SYMBOLIC_SELF_PRESERVATION_CERTIFICATE_GAP_BUT_ACTUAL_DOOR_EXISTS" else
            "R50G25AL_LIFT_PARENT_ONLY_SELF_PRESERVATION_TO_SYMBOLIC_CLASS" if verdict.startswith("PARENT_ONLY_SYMBOLIC") else
            "R50G25AL_MINIMIZE_AK_COUNTEREXAMPLE"
        ),
        "firewall": {
            "P_VS_NP": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "TRUMP_finished": False,
            "finite_pass_is_not_universal_symbolic_proof": True,
            "symbolic_certificate_gap_is_not_solver_counterexample": True,
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
        "gate", "verdict", "root_count_completed_or_attempted",
        "symbolically_certified_residual_event_count", "semantic_mismatch_count",
        "minimum_symbolic_slack", "maximum_symbolic_candidates_tested", "recommended_next_gate"
    ]
    print(json.dumps({k: result.get(k) for k in keys}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
