from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r50g25g_micro_rup_restart_replay_source_lift_family as r50g25g
import janus_trump_r50g25y_minimal_w_policy_counterexample_forensics as y
import janus_trump_r50g25ad_safe_envelope_reachability_gphp as ad
import janus_trump_r50g25ah_raw_dp_reachability_induction as ah
import janus_trump_r50g25ai_symbolic_signed_incidence_residual_class as ai
import janus_trump_r50g25aj_signed_incidence_reachability_closure as aj
import janus_trump_r50g25ak_symbolic_self_preserving_pivot as ak

GATE = "JANUS_TRUMP_R50G25AM_POST_DP_CHEAP_CONTRACTION_CERTIFICATE_OR_REACHABLE_COUNTEREXAMPLE"
PREREG_COMMIT = "fa96bbede4d0e01f363f1bb146c8aef1642444cc"
AL_RECEIPT_COMMIT = "eead993fec81fe471cb8496bf67747cf180ce041"
AL_GAP_HASH = "a28b56a47bf70487dfde4616b120d8ed68c4719546ff3d2756d12cf9b77d51cc"
AL_GAP_PIVOT = 9
DOMAIN = ah.DOMAIN
ALLOWED_R33_RULES = {
    "TAUTOLOGY_DELETION",
    "UNIT_PROPAGATION_WITH_RECONSTRUCTION_TRACE",
    "PURE_LITERAL_AUTARKY",
    "SUBSUMPTION",
    "BLOCKED_CLAUSE_ELIMINATION",
    "BOUNDED_VARIABLE_ELIMINATION",
}
DECLARED_R33_TERMINALS = {"EMPTY_CLAUSE_UNSAT", "EMPTY_CNF_SAT", "2CNF", "HORN"}


def post_dp_r33_certificate(core, budget, var, r34):
    before = r33.canonical_formula(core)
    C, L, V = map(int, r33.measure(before))
    exact1 = y.exact_dp_record(before, int(var))
    exact2 = y.exact_dp_record(before, int(var))
    if exact1 is None or exact2 is None or not exact1.get("replay_pass") or not exact2.get("replay_pass"):
        return {"ok": False, "class": "EXACT_DP_REPLAY_FAILURE", "var": int(var)}
    child1 = r33.canonical_formula(exact1["transformed"])
    child2 = r33.canonical_formula(exact2["transformed"])
    if child1 != child2 or exact1["CLV_after"] != exact2["CLV_after"]:
        return {"ok": False, "class": "EXACT_DP_REPLAY_FAILURE", "var": int(var), "reason": "DOUBLE_REPLAY_DRIFT"}

    simp1 = r33.simplify(child1)
    simp2 = r33.simplify(child1)
    final1 = r33.canonical_formula(simp1["final_formula"])
    final2 = r33.canonical_formula(simp2["final_formula"])
    if final1 != final2 or simp1["terminal"] != simp2["terminal"] or simp1["history"] != simp2["history"]:
        return {"ok": False, "class": "R33_REPLAY_FAILURE", "var": int(var)}
    rules = set(simp1.get("rule_counts", {}))
    if not rules <= ALLOWED_R33_RULES or not bool(simp1.get("strict_progress", False)):
        return {
            "ok": False, "class": "R33_CERTIFICATE_FAILURE", "var": int(var),
            "unexpected_rules": sorted(rules - ALLOWED_R33_RULES),
            "strict_progress": bool(simp1.get("strict_progress", False)),
        }
    if simp1["terminal"] == "FAIL_STEP_LIMIT":
        return {"ok": False, "class": "RESOURCE_LIMIT", "var": int(var), "reason": "R33_STEP_LIMIT"}

    pair_checks = int(exact1.get("pair_checks", 0))
    pair_bound = int(C * C)
    ledger_pass = bool(pair_checks <= pair_bound and int(simp1.get("total_check_operation_count_upper_ledger", 0)) >= 0)
    if not ledger_pass:
        return {"ok": False, "class": "POLYNOMIAL_LEDGER_FAILURE", "var": int(var)}

    final_CLV = list(r33.measure(final1))
    terminal = str(simp1["terminal"])
    cert_kind = None
    class_record = None
    if terminal in DECLARED_R33_TERMINALS:
        cert_kind = "R33_TERMINAL"
        passes = True
    elif terminal != "STALLED_STACK_LEAN_CORE":
        return {"ok": False, "class": "R33_CERTIFICATE_FAILURE", "var": int(var), "terminal": terminal}
    else:
        affine = r34.recognize_complete_affine_cnf(final1)
        if affine.get("recognized"):
            cert_kind = "AFFINE"
            passes = True
        else:
            class_record = ai.signed_incidence_record(final1, budget)
            passes = bool(class_record["symbolic_class_pass"])
            cert_kind = "AI_CLASS_RESIDUAL" if passes else "OUTSIDE_AI_CLASS"

    intermediate = [list(exact1["CLV_after"])]
    for rec in simp1.get("history", []):
        intermediate.append(list(rec["measure_before"]))
        intermediate.append(list(rec["measure_after"]))
    max_lex = list(max((tuple(x) for x in intermediate), default=tuple(exact1["CLV_after"])))

    return {
        "ok": True,
        "var": int(var),
        "certificate_pass": bool(passes),
        "certificate_kind": cert_kind,
        "parent_CLV": [C, L, V],
        "exact_DP_CLV_after": list(exact1["CLV_after"]),
        "exact_DP_pair_checks": pair_checks,
        "exact_DP_pair_checks_bound_C2": pair_bound,
        "post_R33_CLV": final_CLV,
        "post_R33_hash": y.canonical_hash(final1),
        "R33_terminal": terminal,
        "R33_rule_counts": dict(simp1.get("rule_counts", {})),
        "R33_rule_applications": int(simp1.get("total_rule_applications", 0)),
        "R33_certificate_bytes": int(simp1.get("total_certificate_bytes", 0)),
        "R33_check_operation_upper_ledger": int(simp1.get("total_check_operation_count_upper_ledger", 0)),
        "R33_strict_progress": bool(simp1.get("strict_progress", False)),
        "post_R33_AI_class_pass": None if class_record is None else bool(class_record["symbolic_class_pass"]),
        "post_R33_AI_class_slack": None if class_record is None else int(class_record["symbolic_class_slack"]),
        "maximum_intermediate_CLV_lex": max_lex,
        "ledger_pass": ledger_pass,
        "transformed_exact_child": child1,
        "post_R33_state": final1,
        "R33_history": simp1.get("history", []),
    }


def audit_case(h, mode, chain):
    _b, r50g23, _r35b, _r33m, _r47jm = chain
    r34 = r50g23.r34
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
                "rung": {"holes": h, "mode": mode}, "meta": meta,
                "status": "TERMINAL", "terminal_label": label,
                "semantic_mismatch": not ("UNSAT" in str(label) or "EMPTY_CLAUSE" in str(label)),
                "initial_CLV": [c0, l0, v0], "budget": int(budget), "events": events,
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
                "residual_hash": residual_hash, "CLV": [C, L, V], "events": events,
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
                "residual_hash": residual_hash, "CLV": [C, L, V], "events": events,
            }

        tested = []
        chosen = None
        hard_failure = None
        for b in admissible:
            cert = post_dp_r33_certificate(core, budget, int(b["var"]), r34)
            tested.append(cert)
            if not cert.get("ok"):
                if cert.get("class") in {"EXACT_DP_REPLAY_FAILURE", "R33_REPLAY_FAILURE", "R33_CERTIFICATE_FAILURE", "POLYNOMIAL_LEDGER_FAILURE", "RESOURCE_LIMIT"}:
                    hard_failure = cert
                    break
                continue
            if cert["certificate_pass"]:
                chosen = cert
                break
        if hard_failure is not None:
            return {
                "rung": {"holes": h, "mode": mode}, "status": "COUNTEREXAMPLE",
                "class": hard_failure.get("class"), "outer_round": outer,
                "residual_hash": residual_hash, "CLV": [C, L, V],
                "failure": hard_failure, "events": events,
            }

        if chosen is None:
            later_door = None
            later_attempts = []
            for b in admissible:
                actual = ak.actual_landing(core, budget, int(b["var"]), chain)
                later_attempts.append({"var": int(b["var"]), "actual": actual})
                if actual.get("ok") and actual.get("self_preserving"):
                    later_door = (int(b["var"]), actual)
                    break
            cls = "AL_GAP_REQUIRES_LATER_CHEAP_LAYER" if residual_hash == AL_GAP_HASH and later_door is not None else "NO_POST_DP_R33_SELF_PRESERVING_DOOR"
            return {
                "rung": {"holes": h, "mode": mode}, "status": "COUNTEREXAMPLE",
                "class": cls, "outer_round": outer, "residual_hash": residual_hash,
                "CLV": [C, L, V], "budget": int(budget),
                "admissible_pivot_count": len(admissible), "R33_only_attempts": tested,
                "later_cheap_layer_door": None if later_door is None else {"var": later_door[0], "actual": later_door[1]},
                "later_cheap_layer_attempts": later_attempts, "events": events,
            }

        # Only after selection, replay the full inherited cheap policy as an external consistency check.
        full = ak.actual_landing(core, budget, int(chosen["var"]), chain)
        if not full.get("ok") or not full.get("self_preserving"):
            return {
                "rung": {"holes": h, "mode": mode}, "status": "COUNTEREXAMPLE",
                "class": "R33_CERTIFICATE_FAILURE", "outer_round": outer,
                "residual_hash": residual_hash, "certificate": chosen, "full_policy_check": full,
                "events": events,
            }

        event = {
            "outer_round": int(outer), "residual_hash": residual_hash, "CLV": [C, L, V],
            "parent_symbolic_class_slack": int(parent_si["symbolic_class_slack"]),
            "admissible_pivot_count": len(admissible), "candidates_tested": len(tested),
            "chosen_var": int(chosen["var"]), "certificate_kind": chosen["certificate_kind"],
            "exact_DP_CLV_after": chosen["exact_DP_CLV_after"], "post_R33_CLV": chosen["post_R33_CLV"],
            "post_R33_hash": chosen["post_R33_hash"], "post_R33_AI_class_pass": chosen["post_R33_AI_class_pass"],
            "post_R33_AI_class_slack": chosen["post_R33_AI_class_slack"],
            "R33_rule_counts": chosen["R33_rule_counts"], "R33_rule_applications": chosen["R33_rule_applications"],
            "R33_certificate_bytes": chosen["R33_certificate_bytes"],
            "R33_check_operation_upper_ledger": chosen["R33_check_operation_upper_ledger"],
            "exact_DP_pair_checks": chosen["exact_DP_pair_checks"],
            "maximum_intermediate_CLV_lex": chosen["maximum_intermediate_CLV_lex"],
            "full_policy_self_preserving_check": True,
            "AL_gap_diagnostic_control": bool(residual_hash == AL_GAP_HASH),
            "AL_gap_expected_pivot": AL_GAP_PIVOT if residual_hash == AL_GAP_HASH else None,
        }
        events.append(event)
        # Preserve the inherited route: the next outer replay receives the exact DP child,
        # and may further simplify it. AM only certifies that its R33 prefix already suffices.
        state = r33.canonical_formula(chosen["transformed_exact_child"])

    return {"rung": {"holes": h, "mode": mode}, "status": "RESOURCE_LIMIT", "events": events}


def run():
    chain = r50g25g._chain()
    rows = []
    for h, mode in DOMAIN:
        row = audit_case(h, mode, chain)
        rows.append(row)
        if row.get("status") in {"COUNTEREXAMPLE", "FAILURE", "RESOURCE_LIMIT"}:
            break

    events = [e for r in rows for e in r.get("events", [])]
    first_nonterminal = next((r for r in rows if r.get("status") != "TERMINAL"), None)
    semantic = [r for r in rows if r.get("semantic_mismatch")]
    control = next((e for e in events if e.get("AL_gap_diagnostic_control")), None)

    if first_nonterminal is None and not semantic and len(rows) == len(DOMAIN):
        verdict = "POST_DP_R33_CERTIFICATE_COVERS_FROZEN_DOMAIN"
    elif semantic:
        verdict = "SEMANTIC_MISMATCH"
    elif first_nonterminal is None:
        verdict = "IMPLEMENTATION_FAILURE"
    else:
        verdict = first_nonterminal.get("class", first_nonterminal.get("status", "IMPLEMENTATION_FAILURE"))

    max_candidates = max((int(e["candidates_tested"]) for e in events), default=0)
    max_pair_checks = max((int(e["exact_DP_pair_checks"]) for e in events), default=0)
    max_r33_checks = max((int(e["R33_check_operation_upper_ledger"]) for e in events), default=0)
    max_r33_apps = max((int(e["R33_rule_applications"]) for e in events), default=0)
    max_cert_bytes = max((int(e["R33_certificate_bytes"]) for e in events), default=0)

    return {
        "gate": GATE,
        "AM_preregistration_commit": PREREG_COMMIT,
        "parent_AL_receipt_commit": AL_RECEIPT_COMMIT,
        "verdict": verdict,
        "domain": DOMAIN,
        "root_count_completed_or_attempted": len(rows),
        "certified_residual_event_count": len(events),
        "semantic_mismatch_count": len(semantic),
        "maximum_candidates_tested_per_certified_residual": max_candidates,
        "maximum_exact_DP_pair_checks": max_pair_checks,
        "maximum_R33_check_operation_upper_ledger": max_r33_checks,
        "maximum_R33_rule_applications": max_r33_apps,
        "maximum_R33_certificate_bytes": max_cert_bytes,
        "AL_gap_diagnostic_control_reached": bool(control is not None),
        "AL_gap_diagnostic_control_result": control,
        "first_nonterminal_result": first_nonterminal,
        "rows": rows,
        "recommended_next_gate": (
            "R50G25AN_DERIVE_SYMBOLIC_R33_CONTRACTION_LOWER_BOUND_OR_COUNTEREXAMPLE"
            if verdict == "POST_DP_R33_CERTIFICATE_COVERS_FROZEN_DOMAIN"
            else "R50G25AN_LATER_CHEAP_LAYER_NECESSITY_FORENSICS"
        ),
        "firewall": {
            "P_VS_NP": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "TRUMP_finished": False,
            "finite_pass_is_not_universal_closure": True,
            "proof_carrying_local_transition_is_not_global_runtime_bound": True,
            "AI_class_membership_is_sufficient_not_necessary": True,
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
        "gate", "verdict", "root_count_completed_or_attempted", "certified_residual_event_count",
        "semantic_mismatch_count", "maximum_candidates_tested_per_certified_residual",
        "maximum_exact_DP_pair_checks", "maximum_R33_rule_applications",
        "AL_gap_diagnostic_control_reached", "recommended_next_gate",
    ]
    print(json.dumps({k: result.get(k) for k in keys}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
