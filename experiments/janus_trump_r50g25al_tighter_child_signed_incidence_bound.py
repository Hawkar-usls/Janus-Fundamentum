from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r42_subsumption_aware_bve_successor as r42
import janus_trump_r50g25g_micro_rup_restart_replay_source_lift_family as r50g25g
import janus_trump_r50g25y_minimal_w_policy_counterexample_forensics as y
import janus_trump_r50g25ad_safe_envelope_reachability_gphp as ad
import janus_trump_r50g25ah_raw_dp_reachability_induction as ah
import janus_trump_r50g25ai_symbolic_signed_incidence_residual_class as ai
import janus_trump_r50g25aj_signed_incidence_reachability_closure as aj
import janus_trump_r50g25ak_symbolic_self_preserving_pivot as ak

GATE = "JANUS_TRUMP_R50G25AL_DERIVE_TIGHTER_CHILD_SIGNED_INCIDENCE_BOUND"
PREREG_COMMIT = "5def09c9bb8f5fda3751a6b555beb941723e4cd8"
AK_RECEIPT_COMMIT = "9536aa9e0d4bebe02d18450c9942ad7b8046d480"
AK_CONTROL_HASH = "04c6f85371b1ef841196d4230a7fcade3484f1d433fb2a851cfe904469e40241"
DOMAIN = ah.DOMAIN


def pairwise_compatible_raw_child_certificate(formula, budget, var):
    """Parent-computable upper certificate frozen in R50G25AL preregistration.

    Build the exact deduplicated non-tautological DP pool *before* subsumption.
    The normalized exact-DP child is a clause-deletion subset of this pool.
    S and AI P_hat are monotone non-increasing under clause deletion, while
    dropping -L-Q2 is conservative for an upper bound on the AI class LHS.
    """
    f = r33.canonical_formula(formula)
    C, L, V = map(int, r33.measure(f))
    if V <= 2:
        return None
    local = aj.local_signed_incidence_bound(f, budget, int(var))
    if local is None or not local["envelope_admissible"]:
        return None

    pos = tuple(c for c in f if var in c)
    neg = tuple(c for c in f if -var in c)
    base = tuple(c for c in f if var not in c and -var not in c)
    if not pos or not neg:
        return None

    unique_resolvents = set()
    pair_attempts = 0
    non_tautological_pair_count = 0
    tautology_skips = 0
    pair_literal_work = 0
    for p in pos:
        for n in neg:
            pair_attempts += 1
            pair_literal_work += len(p) + len(n)
            raw = (set(p) - {int(var)}) | (set(n) - {-int(var)})
            if any(-lit in raw for lit in raw):
                tautology_skips += 1
                continue
            non_tautological_pair_count += 1
            unique_resolvents.add(r33.canonical_clause(raw))

    # Independent compatibility check against the already frozen R42 resolver.
    p2, n2, resolvents2, pair_checks2 = r42.all_dp_resolvents(f, int(var))
    resolver_replay_pass = bool(
        pos == p2 and neg == n2 and pair_attempts == pair_checks2
        and tuple(sorted(unique_resolvents)) == resolvents2
    )

    pool = r33.canonical_formula(list(base) + list(unique_resolvents))
    pool_C, pool_L, pool_V = map(int, r33.measure(pool))
    pool_si = ai.signed_incidence_record(pool, budget) if pool_V > 1 else None
    if pool_si is None:
        return None

    child_v_assumed = V - 1
    child_t = min(int(budget) // 2, math.isqrt(int(budget) * (child_v_assumed - 1)))
    p_hat_tilde = int(pool_si["P_hat_signed_incidence"])
    s_tilde = int(pool_C + pool_L)
    lhs_ub = int(child_v_assumed * s_tilde + p_hat_tilde)
    rhs = int(child_v_assumed * child_t)
    certificate_pass = bool(resolver_replay_pass and lhs_ub <= rhs)

    max_parent_width = max((len(c) for c in f), default=0)
    pair_literal_work_ub = int(pair_attempts * 2 * max_parent_width)
    incidence_scan_work = int(pool_C * max(pool_V, 1))
    polynomial_ledger_pass = bool(pair_literal_work <= pair_literal_work_ub)

    return {
        "var": int(var),
        "parent_CLV": [C, L, V],
        "child_V_assumed": int(child_v_assumed),
        "child_T": int(child_t),
        "child_S_tilde_UB": int(s_tilde),
        "child_P_hat_tilde_UB": int(p_hat_tilde),
        "child_class_LHS_UB": int(lhs_ub),
        "child_class_RHS": int(rhs),
        "symbolic_self_preservation_pass": bool(certificate_pass),
        "symbolic_slack": int(rhs - lhs_ub),
        "resolver_replay_pass": bool(resolver_replay_pass),
        "pool_CLV_before_subsumption": [pool_C, pool_L, pool_V],
        "ledger": {
            "pair_attempts": int(pair_attempts),
            "non_tautological_pair_count": int(non_tautological_pair_count),
            "tautology_skips": int(tautology_skips),
            "unique_resolvent_count": int(len(unique_resolvents)),
            "duplicate_resolvent_pair_count": int(non_tautological_pair_count - len(unique_resolvents)),
            "base_clause_count": int(len(base)),
            "pool_clause_count": int(pool_C),
            "pool_literal_count": int(pool_L),
            "base_or_resolvent_dedup_count": int(len(base) + len(unique_resolvents) - pool_C),
            "pair_literal_work": int(pair_literal_work),
            "pair_literal_work_UB": int(pair_literal_work_ub),
            "incidence_scan_work": int(incidence_scan_work),
            "polynomial_ledger_pass": bool(polynomial_ledger_pass),
        },
    }


def verify_selected(core, budget, cert, chain):
    var = int(cert["var"])
    before = r33.canonical_formula(core)
    _C, _L, V = map(int, r33.measure(before))
    if not cert.get("resolver_replay_pass"):
        return {"ok": False, "class": "PAIRWISE_RAW_CHILD_BOUND_UNSOUND", "reason": "RESOLVER_REPLAY_MISMATCH"}
    if not cert.get("ledger", {}).get("polynomial_ledger_pass"):
        return {"ok": False, "class": "POLYNOMIAL_LEDGER_FAILURE"}

    exact = y.exact_dp_record(before, var)
    if exact is None or not exact.get("replay_pass"):
        return {"ok": False, "class": "EXACT_DP_REPLAY_FAILURE", "var": var}
    transformed = r33.canonical_formula(exact["transformed"])
    actual_C, actual_L, actual_V = map(int, r33.measure(transformed))
    if actual_V != V - 1:
        return {
            "ok": False,
            "class": "CHILD_VARIABLE_DROP_ASSUMPTION_FAILURE",
            "var": var,
            "expected_V": int(V - 1),
            "actual_V": int(actual_V),
            "exact_CLV_after": list(exact["CLV_after"]),
        }

    exact_si = ai.signed_incidence_record(transformed, budget)
    actual_S = int(actual_C + actual_L)
    actual_p_hat = int(exact_si["P_hat_signed_incidence"])
    component_sound = bool(
        actual_S <= int(cert["child_S_tilde_UB"])
        and actual_p_hat <= int(cert["child_P_hat_tilde_UB"])
    )
    if not component_sound or not exact_si["symbolic_class_pass"]:
        return {
            "ok": False,
            "class": "PAIRWISE_RAW_CHILD_BOUND_UNSOUND",
            "var": var,
            "certificate_S_UB": int(cert["child_S_tilde_UB"]),
            "actual_S": actual_S,
            "certificate_P_hat_UB": int(cert["child_P_hat_tilde_UB"]),
            "actual_P_hat": actual_p_hat,
            "actual_symbolic_class_pass": bool(exact_si["symbolic_class_pass"]),
            "actual_symbolic_class_slack": int(exact_si["symbolic_class_slack"]),
        }

    landing = ak.actual_landing(before, budget, var, chain)
    if not landing.get("ok"):
        return {"ok": False, "class": landing.get("class", "IMPLEMENTATION_FAILURE"), "var": var}
    return {
        "ok": True,
        "var": var,
        "self_preserving": bool(landing.get("self_preserving")),
        "terminal": bool(landing.get("terminal", False)),
        "exact_CLV_after": list(exact["CLV_after"]),
        "actual_S": actual_S,
        "actual_P_hat": actual_p_hat,
        "actual_symbolic_class_pass": bool(exact_si["symbolic_class_pass"]),
        "actual_symbolic_class_slack": int(exact_si["symbolic_class_slack"]),
        "component_soundness_pass": True,
        "landing": landing,
        "transformed": transformed,
    }


def audit_case(h, mode, chain):
    initial, _meta = ad.graph_php(h, mode)
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
            return {"rung": {"holes": h, "mode": mode}, "status": "FAILURE", "class": "IMPLEMENTATION_FAILURE", "events": events}

        core = r33.canonical_formula(w["state"])
        C, L, V = map(int, r33.measure(core))
        residual_hash = y.canonical_hash(core)
        parent_si = ai.signed_incidence_record(core, budget)
        if not parent_si["symbolic_class_pass"]:
            return {
                "rung": {"holes": h, "mode": mode}, "status": "COUNTEREXAMPLE",
                "class": "PARENT_OUTSIDE_AI_CLASS", "outer_round": outer,
                "residual_hash": residual_hash, "CLV": [C, L, V],
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
                "residual_hash": residual_hash, "CLV": [C, L, V],
                "formula": [list(c) for c in core], "events": events,
            }

        symbolic_rows = []
        chosen = None
        for b in admissible:
            cert = pairwise_compatible_raw_child_certificate(core, budget, int(b["var"]))
            if cert is None:
                continue
            symbolic_rows.append(cert)
            if cert["symbolic_self_preservation_pass"]:
                chosen = cert
                break

        if chosen is None:
            actual_door = None
            actual_attempts = []
            for b in admissible:
                var = int(b["var"])
                actual = ak.actual_landing(core, budget, var, chain)
                actual_attempts.append({"var": var, "RAW_S_UB": int(b["RAW_S_UB"]), "actual": actual})
                if actual.get("ok") and actual.get("self_preserving"):
                    actual_door = (b, actual)
                    break
            if actual_door is not None:
                b, actual = actual_door
                return {
                    "rung": {"holes": h, "mode": mode}, "status": "SYMBOLIC_GAP",
                    "class": "TIGHT_CHILD_SYMBOLIC_CERTIFICATE_GAP_BUT_ACTUAL_DOOR_EXISTS",
                    "outer_round": outer, "residual_hash": residual_hash,
                    "CLV": [C, L, V], "budget": int(budget),
                    "parent_symbolic_class_slack": int(parent_si["symbolic_class_slack"]),
                    "admissible_pivot_count": len(admissible),
                    "symbolic_certificates": symbolic_rows,
                    "first_actual_self_preserving_var": int(b["var"]),
                    "first_actual_self_preserving": actual,
                    "formula": [list(c) for c in core], "events": events,
                }
            return {
                "rung": {"holes": h, "mode": mode}, "status": "COUNTEREXAMPLE",
                "class": "NO_ACTUAL_SELF_PRESERVING_PIVOT", "outer_round": outer,
                "residual_hash": residual_hash, "CLV": [C, L, V],
                "symbolic_certificates": symbolic_rows, "actual_attempts": actual_attempts,
                "formula": [list(c) for c in core], "events": events,
            }

        verified = verify_selected(core, budget, chosen, chain)
        if not verified.get("ok"):
            return {
                "rung": {"holes": h, "mode": mode}, "status": "COUNTEREXAMPLE",
                "class": verified.get("class", "IMPLEMENTATION_FAILURE"),
                "outer_round": outer, "residual_hash": residual_hash,
                "CLV": [C, L, V], "certificate": chosen,
                "verification": verified, "formula": [list(c) for c in core],
                "events": events,
            }
        if not verified["self_preserving"]:
            return {
                "rung": {"holes": h, "mode": mode}, "status": "COUNTEREXAMPLE",
                "class": "NO_ACTUAL_SELF_PRESERVING_PIVOT", "outer_round": outer,
                "residual_hash": residual_hash, "CLV": [C, L, V],
                "certificate": chosen, "verification": verified,
                "formula": [list(c) for c in core], "events": events,
            }

        event = {
            "outer_round": int(outer),
            "residual_hash": residual_hash,
            "CLV": [C, L, V],
            "parent_symbolic_class_slack": int(parent_si["symbolic_class_slack"]),
            "admissible_pivot_count": len(admissible),
            "symbolic_candidates_tested": len(symbolic_rows),
            "chosen_var": int(chosen["var"]),
            "chosen_symbolic_slack": int(chosen["symbolic_slack"]),
            "child_S_tilde_UB": int(chosen["child_S_tilde_UB"]),
            "child_P_hat_tilde_UB": int(chosen["child_P_hat_tilde_UB"]),
            "actual_child_symbolic_slack": int(verified["actual_symbolic_class_slack"]),
            "ledger": chosen["ledger"],
            "AK_control_witness": bool(residual_hash == AK_CONTROL_HASH),
        }
        events.append(event)
        state = r33.canonical_formula(verified["transformed"])

    return {"rung": {"holes": h, "mode": mode}, "status": "RESOURCE_LIMIT", "events": events}


def run():
    chain = r50g25g._chain()
    rows = []
    for h, mode in DOMAIN:
        row = audit_case(h, mode, chain)
        rows.append(row)
        if row.get("status") in {"COUNTEREXAMPLE", "SYMBOLIC_GAP", "FAILURE", "RESOURCE_LIMIT"}:
            break

    events = [e for row in rows for e in row.get("events", [])]
    first_nonterminal = next((r for r in rows if r.get("status") != "TERMINAL"), None)
    semantic = [r for r in rows if r.get("semantic_mismatch")]
    control = next((e for e in events if e.get("AK_control_witness")), None)

    if first_nonterminal is None and not semantic and len(rows) == len(DOMAIN):
        verdict = "PAIRWISE_COMPATIBLE_RAW_CHILD_BOUND_COVERS_FROZEN_DOMAIN"
    elif semantic:
        verdict = "SEMANTIC_MISMATCH"
    elif first_nonterminal is None:
        verdict = "IMPLEMENTATION_FAILURE"
    else:
        verdict = first_nonterminal.get("class", first_nonterminal.get("status", "IMPLEMENTATION_FAILURE"))

    ledgers = [e.get("ledger", {}) for e in events]
    max_pair_attempts = max((int(x.get("pair_attempts", 0)) for x in ledgers), default=0)
    max_pair_literal_work = max((int(x.get("pair_literal_work", 0)) for x in ledgers), default=0)
    max_pool_clauses = max((int(x.get("pool_clause_count", 0)) for x in ledgers), default=0)
    min_positive_slack = min((int(e["chosen_symbolic_slack"]) for e in events if int(e["chosen_symbolic_slack"]) >= 0), default=0)
    max_candidates = max((int(e["symbolic_candidates_tested"]) for e in events), default=0)

    next_gate = (
        "R50G25AM_PAIRWISE_COMPATIBLE_CHILD_BOUND_REACHABILITY_INDUCTION_OR_COUNTEREXAMPLE"
        if verdict == "PAIRWISE_COMPATIBLE_RAW_CHILD_BOUND_COVERS_FROZEN_DOMAIN"
        else "R50G25AM_MINIMIZE_TIGHT_CHILD_CERTIFICATE_GAP_OR_POLICY_OBSTRUCTION"
    )

    return {
        "gate": GATE,
        "AL_preregistration_commit": PREREG_COMMIT,
        "parent_AK_receipt_commit": AK_RECEIPT_COMMIT,
        "verdict": verdict,
        "domain": DOMAIN,
        "root_count_completed_or_attempted": len(rows),
        "symbolically_certified_residual_event_count": len(events),
        "semantic_mismatch_count": len(semantic),
        "maximum_symbolic_candidates_tested": int(max_candidates),
        "minimum_nonnegative_symbolic_slack": int(min_positive_slack),
        "maximum_pair_attempts_per_chosen_certificate": int(max_pair_attempts),
        "maximum_pair_literal_work_per_chosen_certificate": int(max_pair_literal_work),
        "maximum_raw_pool_clause_count": int(max_pool_clauses),
        "AK_control_witness_reached": bool(control is not None),
        "AK_control_witness_result": control,
        "first_nonterminal_result": first_nonterminal,
        "rows": rows,
        "recommended_next_gate": next_gate,
        "firewall": {
            "P_VS_NP": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "TRUMP_finished": False,
            "finite_pass_is_not_universal_symbolic_proof": True,
            "symbolic_certificate_gap_is_not_solver_counterexample": True,
            "pairwise_raw_child_envelope_is_not_global_runtime_bound": True,
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
        "maximum_symbolic_candidates_tested", "minimum_nonnegative_symbolic_slack",
        "maximum_pair_attempts_per_chosen_certificate", "maximum_raw_pool_clause_count",
        "AK_control_witness_reached", "recommended_next_gate",
    ]
    print(json.dumps({k: result.get(k) for k in keys}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
