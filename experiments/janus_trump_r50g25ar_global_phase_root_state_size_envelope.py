from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r35b_single_literal_rup_vivification as r35b
import janus_trump_r42_subsumption_aware_bve_successor as r42
import janus_trump_r50g25g_micro_rup_restart_replay_source_lift_family as r50g25g
import janus_trump_r50g25y_minimal_w_policy_counterexample_forensics as y
import janus_trump_r50g25ad_safe_envelope_reachability_gphp as ad
import janus_trump_r50g25ah_raw_dp_reachability_induction as ah
import janus_trump_r50g25ai_symbolic_signed_incidence_residual_class as ai
import janus_trump_r50g25aj_signed_incidence_reachability_closure as aj

GATE = "JANUS_TRUMP_R50G25AR_GLOBAL_PHASE_ROOT_STATE_SIZE_ENVELOPE_OR_EXPLICIT_DP_BLOWUP_OBSTRUCTION"
PREREG_COMMIT = "9acedbc48b00a99b48d553fb2d61a08f1dd6e148"
PARENT_AQ_RECEIPT_COMMIT = "c69f113dea481280c3acba87cae3bc4059c5921d"
PARENT_AQ_SEALED_HEAD = "670ffd66e42fdb040d331131573c5a79d21beea0"
SUCCESS = "GLOBAL_PHASE_ROOT_STATE_SIZE_ENVELOPE_DERIVED_FOR_FROZEN_NORMATIVE_MACHINE"
OBSTRUCTION = "EXPLICIT_STATE_ENVELOPE_OR_SELECTOR_CONTRACT_OBSTRUCTION_FOUND"
DOMAIN = ah.DOMAIN

ALLOWED_R33_RULES = {
    "TAUTOLOGY_DELETION",
    "UNIT_PROPAGATION_WITH_RECONSTRUCTION_TRACE",
    "PURE_LITERAL_AUTARKY",
    "SUBSUMPTION",
    "BLOCKED_CLAUSE_ELIMINATION",
    "BOUNDED_VARIABLE_ELIMINATION",
}


def canonical(formula):
    return r33.canonical_formula(formula)


def clv(formula):
    return tuple(map(int, r33.measure(canonical(formula))))


def vars_set(formula):
    return set(map(int, r33.variables(canonical(formula))))


def fail(kind, **payload):
    out = {"kind": str(kind)}
    out.update(payload)
    return out


def root_constants(formula):
    C0, L0, V0 = clv(formula)
    N0 = C0 + L0
    B0 = N0 * ((V0 + 1) ** 2)
    return {
        "C0": C0,
        "L0": L0,
        "V0": V0,
        "N0": N0,
        "B0": B0,
        "C_cap": max(C0, B0 // 2),
        "L_cap": max(L0, (B0 // 2) * V0),
        "S_cap": max(N0, (B0 * (V0 + 1)) // 2),
    }


def numeric_state_check(C, L, V, root, context):
    fs = []
    if V > root["V0"]:
        fs.append(fail("VARIABLE_BOUND_FAILURE", context=context, CLV=[C, L, V], V0=root["V0"]))
    if L > C * V:
        fs.append(fail("CANONICAL_WIDTH_BOUND_FAILURE", context=context, CLV=[C, L, V], bound=C * V))
    if C > root["C_cap"] or L > root["L_cap"] or C + L > root["S_cap"]:
        fs.append(fail(
            "STATE_ENVELOPE_FAILURE",
            context=context,
            CLV=[C, L, V],
            caps={"C": root["C_cap"], "L": root["L_cap"], "S": root["S_cap"]},
        ))
    return fs


def formula_state_check(formula, root, context):
    C, L, V = clv(formula)
    return numeric_state_check(C, L, V, root, context)


def symbolic_envelope_audit():
    # Integer algebra checks sufficient for the frozen theorem statement.
    synthetic_roots = []
    failures = []
    for C0 in (1, 2, 7, 31):
        for L0 in (1, 3, 17, 97):
            for V0 in (1, 2, 8, 31):
                N0 = C0 + L0
                B0 = N0 * ((V0 + 1) ** 2)
                root_in = N0 <= B0 // 2
                v_input = V0 <= N0
                poly_B = B0 <= N0 * ((N0 + 1) ** 2) if V0 <= N0 else None
                row = {
                    "C0": C0, "L0": L0, "V0": V0, "N0": N0, "B0": B0,
                    "root_in_B0_half": root_in,
                    "V0_le_N0_assumption": v_input,
                    "B0_le_N0_N0plus1_sq_if_explicit": poly_B,
                }
                synthetic_roots.append(row)
                if not root_in:
                    failures.append(fail("ROOT_ENVELOPE_FAILURE", row=row))
                if v_input and not poly_B:
                    failures.append(fail("POLYNOMIAL_COROLLARY_FAILURE", row=row))
    derivation = {
        "root": "For V0>=1, (V0+1)^2>=4, hence N0<=B0/4<=B0/2.",
        "exact_DP": "Normative admission gives S'=C'+L'<=RAW_S_UB(x)<=T<=B0/2, and exact DP removes its pivot without introducing variables.",
        "cheap_layer": "Every cheap operator leaves C non-increasing and V non-increasing. Canonical explicit CNF satisfies L<=C*V, hence after any admitted DP, C<=B0/2 and L<=B0*V0/2 through the following cheap phase.",
        "composition": "The same original-root B0 is reused at every later DP, so induction gives C_i<=max(C0,B0/2), V_i<=V0, L_i<=max(L0,B0*V0/2), S_i<=max(N0,B0*(V0+1)/2).",
        "input_size": "For explicit canonical nonempty CNF, V0<=L0<=N0. Therefore B0=N0(V0+1)^2<=N0(N0+1)^2=O(N0^3), and L_i,S_i=O(N0^4).",
    }
    return {"derivation": derivation, "synthetic_integer_checks": synthetic_roots, "failures": failures}


def audit_r33_operator_contracts():
    controls = [
        ("TAUTOLOGY", canonical([(1, -1, 2), (1, 3), (-2, -3)])),
        ("PURE", canonical([(1, 2), (1, -2)])),
        ("SUBSUMPTION", canonical([(1, 2), (1, 2, 3), (-1, -2), (-1, -2, -3)])),
        ("BLOCKED", r33.blocked_clause_control()),
        ("BVE", r33.bve_control()),
        ("EASY_TAIL", r33.easy_redundant_tail()),
    ]
    for seed in range(61100, 61132):
        n = (8, 10, 12, 14)[seed % 4]
        ratio = (2.5, 3.0, 3.5, 4.0)[seed % 4]
        controls.append((f"RANDOM_{seed}", r33.deterministic_random_3cnf(seed, n=n, ratio=ratio)))

    rows = []
    failures = []
    seen_rules = set()
    for name, formula in controls:
        before_formula = canonical(formula)
        result = r33.simplify(before_formula)
        current_vars = vars_set(before_formula)
        for i, rec in enumerate(result.get("history", [])):
            rule = str(rec.get("rule"))
            seen_rules.add(rule)
            b = tuple(map(int, rec["measure_before"]))
            a = tuple(map(int, rec["measure_after"]))
            local = []
            if rule not in ALLOWED_R33_RULES:
                local.append(fail("CHEAP_OPERATOR_CONTRACT_FAILURE", context=f"{name}:{i}", reason="unexpected_R33_rule", rule=rule))
            if a[0] > b[0] or a[2] > b[2]:
                local.append(fail("CHEAP_OPERATOR_CONTRACT_FAILURE", context=f"{name}:{i}", rule=rule, before=list(b), after=list(a)))
            if a[1] > a[0] * a[2]:
                local.append(fail("CANONICAL_WIDTH_BOUND_FAILURE", context=f"{name}:{i}", rule=rule, after=list(a)))
            if not tuple(a) < tuple(b):
                local.append(fail("CHEAP_OPERATOR_CONTRACT_FAILURE", context=f"{name}:{i}", reason="R33_CLV_not_strict", rule=rule, before=list(b), after=list(a)))
            failures.extend(local)
            rows.append({"control": name, "index": i, "rule": rule, "before_CLV": list(b), "after_CLV": list(a), "failures": local})
        final_vars = vars_set(result["final_formula"])
        if not final_vars <= current_vars:
            failures.append(fail("CHEAP_OPERATOR_CONTRACT_FAILURE", context=name, reason="R33_new_variable", new_vars=sorted(final_vars-current_vars)))
    missing = sorted(ALLOWED_R33_RULES - seen_rules)
    if missing:
        failures.append(fail("CHEAP_OPERATOR_CONTRACT_FAILURE", context="R33_controls", reason="rule_coverage_missing", missing=missing))
    return {"control_count": len(controls), "transition_count": len(rows), "seen_rules": sorted(seen_rules), "rows": rows, "failures": failures}


def audit_rup_contract():
    source = canonical([(1, 2, 3), (-1, 2), (-2, 3), (1, -3)])
    strengthened = r35b.replace_clause_with_subclause(source, (1, 2, 3), (1, 2))
    strengthened = canonical(strengthened)
    b = clv(source)
    a = clv(strengthened)
    failures = []
    if not (a[0] <= b[0] and a[2] <= b[2] and a[1] < b[1]):
        failures.append(fail("CHEAP_OPERATOR_CONTRACT_FAILURE", context="RUP_REPLACEMENT_CONTROL", before=list(b), after=list(a)))
    if not vars_set(strengthened) <= vars_set(source):
        failures.append(fail("CHEAP_OPERATOR_CONTRACT_FAILURE", context="RUP_REPLACEMENT_CONTROL", reason="new_variable"))
    return {"before_CLV": list(b), "after_CLV": list(a), "failures": failures}


def audit_sa_bve_contract():
    corpus = [("BVE_CONTROL", canonical(r33.bve_control()))]
    for seed in range(62000, 62100):
        n = (8, 10, 12, 14)[seed % 4]
        ratio = (2.5, 3.0, 3.5, 4.0)[seed % 4]
        corpus.append((f"RANDOM_{seed}", r33.deterministic_random_3cnf(seed, n=n, ratio=ratio)))
    witness = None
    failures = []
    for name, formula in corpus:
        candidate, ledger = r42.best_sa_bve_candidate(formula)
        if candidate is None:
            continue
        replay = r42.independent_sa_bve_replay(formula, candidate)
        before = clv(formula)
        after_formula = canonical(candidate["transformed"])
        after = clv(after_formula)
        local = []
        if not replay.get("pass"):
            local.append(fail("REPLAY_OR_IMPLEMENTATION_FAILURE", context="SA_BVE", control=name, replay=replay))
        if not tuple(after) < tuple(before) or after[0] > before[0] or after[2] >= before[2]:
            local.append(fail("CHEAP_OPERATOR_CONTRACT_FAILURE", context="SA_BVE", control=name, before=list(before), after=list(after)))
        if not vars_set(after_formula) <= vars_set(formula):
            local.append(fail("CHEAP_OPERATOR_CONTRACT_FAILURE", context="SA_BVE", control=name, reason="new_variable"))
        witness = {"control": name, "before_CLV": list(before), "after_CLV": list(after), "var": int(candidate["var"]), "replay_pass": bool(replay.get("pass")), "scan_ledger": ledger, "failures": local}
        failures.extend(local)
        break
    if witness is None:
        failures.append(fail("CHEAP_OPERATOR_CONTRACT_FAILURE", context="SA_BVE", reason="no_control_candidate_found"))
    return {"witness": witness, "failures": failures}


def check_route_clv(route, root, prefix):
    failures = []
    checked = 0
    for ri, row in enumerate(route):
        for key in ("before_CLV", "after_R33_CLV", "after_door_CLV"):
            val = row.get(key)
            if isinstance(val, list) and len(val) == 3:
                C, L, V = map(int, val)
                failures.extend(numeric_state_check(C, L, V, root, f"{prefix}:route{ri}:{key}"))
                checked += 1
    return checked, failures


def audit_normative_routes():
    chain = r50g25g._chain()
    rows = []
    failures = []
    total_dp = 0
    total_intermediate = 0
    max_C = max_L = max_S = max_V = 0
    min_dp_slack = None
    max_rounds = 0

    for h, mode in DOMAIN:
        initial, meta = ad.graph_php(h, mode)
        initial = canonical(initial)
        root = root_constants(initial)
        local_failures = formula_state_check(initial, root, f"h{h}:{mode}:root")
        if root["V0"] >= 1 and root["N0"] > root["B0"] // 2:
            local_failures.append(fail("ROOT_ENVELOPE_FAILURE", rung=[h, mode], root=root))
        if not (root["V0"] <= root["L0"] <= root["N0"]):
            local_failures.append(fail("POLYNOMIAL_COROLLARY_FAILURE", rung=[h, mode], root=root))
        if root["B0"] > root["N0"] * ((root["N0"] + 1) ** 2):
            local_failures.append(fail("POLYNOMIAL_COROLLARY_FAILURE", rung=[h, mode], reason="B0_input_polynomial_bound", root=root))

        state = initial
        events = []
        status = "RESOURCE_LIMIT"
        terminal_label = None
        for outer in range(root["V0"] + 1):
            max_rounds = max(max_rounds, outer)
            w = y.policy_replay(state, chain)
            checked, fs = check_route_clv(w.get("route", []), root, f"h{h}:{mode}:outer{outer}")
            total_intermediate += checked
            local_failures.extend(fs)
            local_failures.extend(formula_state_check(w["state"], root, f"h{h}:{mode}:outer{outer}:policy_state"))

            Cw, Lw, Vw = clv(w["state"])
            max_C = max(max_C, Cw)
            max_L = max(max_L, Lw)
            max_S = max(max_S, Cw + Lw)
            max_V = max(max_V, Vw)

            if w["kind"] in {"TERMINAL", "AFFINE"}:
                status = w["kind"]
                terminal_label = aj.terminal_label(w)
                break
            if w["kind"] != "RESIDUAL":
                local_failures.append(fail("REPLAY_OR_IMPLEMENTATION_FAILURE", rung=[h, mode], outer=outer, policy_kind=w.get("kind")))
                status = "FAILURE"
                break

            core = canonical(w["state"])
            C, L, V = clv(core)
            if V <= 1:
                local_failures.append(fail("NORMATIVE_SELECTOR_SCOPE_FAILURE", rung=[h, mode], outer=outer, reason="residual_with_V<=1", CLV=[C, L, V]))
                status = "FAILURE"
                break
            parent_si = ai.signed_incidence_record(core, root["B0"])
            admissible = []
            for var in r33.variables(core):
                rec = aj.local_signed_incidence_bound(core, root["B0"], int(var))
                if rec is not None and rec["envelope_admissible"]:
                    admissible.append(rec)
            admissible.sort(key=lambda q: (int(q["RAW_S_UB"]), int(q["var"])))
            if not admissible:
                local_failures.append(fail("NORMATIVE_SELECTOR_SCOPE_FAILURE", rung=[h, mode], outer=outer, reason="no_global_root_budget_envelope_admissible_pivot", CLV=[C, L, V], AI_class_pass=bool(parent_si["symbolic_class_pass"])))
                status = "FAILURE"
                break

            chosen = admissible[0]
            var = int(chosen["var"])
            exact = y.exact_dp_record(core, var)
            if exact is None or not exact.get("replay_pass"):
                local_failures.append(fail("REPLAY_OR_IMPLEMENTATION_FAILURE", rung=[h, mode], outer=outer, var=var, reason="exact_DP_replay"))
                status = "FAILURE"
                break
            C1, L1, V1 = map(int, exact["CLV_after"])
            S1 = C1 + L1
            T = int(chosen["T"])
            ub = int(chosen["RAW_S_UB"])
            if not (ub <= T <= root["B0"] // 2):
                local_failures.append(fail("NORMATIVE_SELECTOR_SCOPE_FAILURE", rung=[h, mode], outer=outer, var=var, RAW_S_UB=ub, T=T, B0=root["B0"]))
            if S1 > ub or S1 > root["B0"] // 2:
                local_failures.append(fail("ADMISSIBLE_DP_SIZE_BOUND_FAILURE", rung=[h, mode], outer=outer, var=var, exact_CLV_after=[C1, L1, V1], RAW_S_UB=ub, T=T, B0=root["B0"]))
            if V1 >= V:
                local_failures.append(fail("VARIABLE_BOUND_FAILURE", rung=[h, mode], outer=outer, var=var, before_V=V, after_V=V1))
            child = canonical(exact["transformed"])
            local_failures.extend(formula_state_check(child, root, f"h{h}:{mode}:outer{outer}:exact_child"))
            max_C = max(max_C, C1)
            max_L = max(max_L, L1)
            max_S = max(max_S, S1)
            max_V = max(max_V, V1)
            slack = root["B0"] // 2 - S1
            min_dp_slack = slack if min_dp_slack is None else min(min_dp_slack, slack)
            total_dp += 1
            events.append({
                "outer": outer,
                "parent_CLV": [C, L, V],
                "parent_AI_class_pass": bool(parent_si["symbolic_class_pass"]),
                "admissible_pivot_count": len(admissible),
                "chosen_var": var,
                "chosen_RAW_S_UB": ub,
                "chosen_T": T,
                "exact_child_CLV": [C1, L1, V1],
                "B0_half_slack_after_exact_DP": slack,
            })
            state = child
        else:
            local_failures.append(fail("RESOURCE_LIMIT", rung=[h, mode], reason="outer_loop_exhausted", V0=root["V0"]))

        failures.extend(local_failures)
        rows.append({
            "rung": {"holes": h, "mode": mode},
            "meta": meta,
            "root": root,
            "status": status,
            "terminal_label": terminal_label,
            "event_count": len(events),
            "events": events,
            "failure_count": len(local_failures),
            "failures": local_failures,
        })
        if local_failures:
            break

    return {
        "root_count_audited": len(rows),
        "planned_root_count": len(DOMAIN),
        "total_exact_DP_transitions": total_dp,
        "total_policy_intermediate_CLV_checks": total_intermediate,
        "maximum_observed_C": max_C,
        "maximum_observed_L": max_L,
        "maximum_observed_S": max_S,
        "maximum_observed_V": max_V,
        "minimum_B0_half_slack_after_exact_DP": min_dp_slack,
        "maximum_outer_round_index": max_rounds,
        "rows": rows,
        "failures": failures,
    }


def run():
    symbolic = symbolic_envelope_audit()
    r33_audit = audit_r33_operator_contracts()
    rup_audit = audit_rup_contract()
    sa_audit = audit_sa_bve_contract()
    routes = audit_normative_routes()

    failures = []
    failures.extend(symbolic["failures"])
    failures.extend(r33_audit["failures"])
    failures.extend(rup_audit["failures"])
    failures.extend(sa_audit["failures"])
    failures.extend(routes["failures"])

    verdict = SUCCESS if not failures and routes["root_count_audited"] == len(DOMAIN) else OBSTRUCTION
    return {
        "gate": GATE,
        "preregistration_commit": PREREG_COMMIT,
        "parent_AQ_receipt_commit": PARENT_AQ_RECEIPT_COMMIT,
        "parent_AQ_sealed_head_observed": PARENT_AQ_SEALED_HEAD,
        "verdict": verdict,
        "normative_scope": {
            "budget": "B0=(C0+L0)*(V0+1)^2 computed once at original canonical root",
            "exact_DP_selector": "ascending (RAW_S_UB,var) among GLOBAL_ROOT_BUDGET envelope-admissible pivots only",
            "AQ_min_bipolar_selector": "DIAGNOSTIC_ONLY_NOT_NORMATIVE",
            "cheap_policy": "R33 -> terminal/affine -> RUP -> SA_BVE -> restart/residual",
            "SAT_truth_used_for_selector": False,
        },
        "symbolic_envelope": symbolic,
        "R33_operator_contract_audit": r33_audit,
        "RUP_operator_contract_audit": rup_audit,
        "SA_BVE_operator_contract_audit": sa_audit,
        "normative_route_audit": routes,
        "falsifier_count": len(failures),
        "falsifiers": failures,
        "scientific_scope": {
            "global_explicit_state_size_envelope": "DERIVED_CONDITIONALLY_FOR_FROZEN_NORMATIVE_MACHINE" if verdict == SUCCESS else "OBSTRUCTION_FOUND",
            "input_size_corollary": "C=O(N0^3), L=O(N0^4), S=O(N0^4) under the frozen selector/operator contract" if verdict == SUCCESS else "NOT_CLOSED",
            "universal_envelope_admissible_pivot_existence": "OPEN",
            "route_completeness_for_arbitrary_CNF": "OPEN",
            "end_to_end_polynomial_runtime": "OPEN",
        },
        "recommended_next_gate": "R50G25AS_UNIVERSAL_ENVELOPE_ADMISSIBLE_PIVOT_EXISTENCE_OR_REACHABLE_COUNTEREXAMPLE" if verdict == SUCCESS else "R50G25AS_MINIMIZE_AR_OBSTRUCTION",
        "firewalls": {
            "P_VS_NP": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "TRUMP_finished": False,
            "conditional_state_envelope_is_not_universal_pivot_existence": True,
            "state_envelope_is_not_runtime_theorem": True,
            "finite_replay_is_not_universal_proof": True,
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    result = run()
    p = Path(args.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "gate": result["gate"],
        "verdict": result["verdict"],
        "falsifier_count": result["falsifier_count"],
        "root_count_audited": result["normative_route_audit"]["root_count_audited"],
        "exact_DP_transitions": result["normative_route_audit"]["total_exact_DP_transitions"],
        "policy_intermediate_checks": result["normative_route_audit"]["total_policy_intermediate_CLV_checks"],
        "min_B0_half_slack": result["normative_route_audit"]["minimum_B0_half_slack_after_exact_DP"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
