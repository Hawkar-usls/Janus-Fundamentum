from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r50g25g_micro_rup_restart_replay_source_lift_family as r50g25g
import janus_trump_r50g25y_minimal_w_policy_counterexample_forensics as y
import janus_trump_r50g25an_later_cheap_layer_necessity_forensics as an

GATE = "JANUS_TRUMP_R50G25AP_INTERLEAVED_R33_RUP_COMBINED_PROGRESS_POTENTIAL_OR_COUNTEREXAMPLE"
PREREG_COMMIT = "1c195e38fcd8233ffcc0019ea735e4ac16d07581"
PARENT_AO_SYNC_HEAD = "e649c76a6592fbf080405bf69c37495c5539a6ac"
SUCCESS = "COMBINED_R33_RUP_ROOT_FROZEN_PHI_STRICT_DESCENT_AND_FROZEN_LEDGER_AUDIT_PASS"
COUNTEREXAMPLE = "COMBINED_R33_RUP_PHI_OR_LEDGER_COUNTEREXAMPLE_FOUND"
EXPECTED_AN_RUPS = 26


def measure3(formula):
    return tuple(map(int, r33.measure(r33.canonical_formula(formula))))


def constants(formula):
    C0, L0, V0 = measure3(formula)
    if C0 <= 0 or V0 <= 0:
        raise ValueError("AP phase root must be nonterminal with C0>0 and V0>0")
    M = C0 * V0 + 1
    Lmax = C0 * V0
    phi0 = L0 + M * V0
    K = 2 * Lmax + C0 + C0 * C0 + Lmax * C0 + max(1, V0) * max(1, C0 * C0)
    return {
        "C0": C0,
        "L0": L0,
        "V0": V0,
        "M": M,
        "Lmax": Lmax,
        "Phi0": phi0,
        "K_R33_search_iteration": K,
    }


def phi(clv, M):
    _C, L, V = map(int, clv)
    return L + int(M) * V


def falsifier(kind, **payload):
    x = {"kind": kind}
    x.update(payload)
    return x


def check_r33_record(record, root, context):
    before = tuple(map(int, record["measure_before"]))
    after = tuple(map(int, record["measure_after"]))
    Cb, Lb, Vb = before
    Ca, La, Va = after
    M = int(root["M"])
    rule = str(record["rule"])
    failures = []

    if Ca > Cb:
        failures.append(falsifier("R33_CLAUSE_COUNT_INCREASE", context=context, rule=rule, before=list(before), after=list(after)))
    if Va > Vb:
        failures.append(falsifier("R33_VARIABLE_INCREASE", context=context, rule=rule, before=list(before), after=list(after)))
    if La > Ca * Va:
        failures.append(falsifier("REPLAY_OR_IMPLEMENTATION_FAILURE", context=context, rule=rule, detail="canonical width bound L<=C*V failed", before=list(before), after=list(after)))

    if rule == "BOUNDED_VARIABLE_ELIMINATION":
        if Va >= Vb:
            failures.append(falsifier("BVE_VARIABLE_DESCENT_FAILURE", context=context, before=list(before), after=list(after)))
        if La > int(root["Lmax"]):
            failures.append(falsifier("BVE_ROOT_BOUND_FAILURE", context=context, before=list(before), after=list(after), Lmax=int(root["Lmax"])))
    else:
        if La >= Lb:
            failures.append(falsifier("NON_BVE_R33_LITERAL_DESCENT_FAILURE", context=context, rule=rule, before=list(before), after=list(after)))

    pb = phi(before, M)
    pa = phi(after, M)
    if pa >= pb:
        failures.append(falsifier("COMBINED_PHI_NONDECREASE", context=context, transition="R33", rule=rule, before=list(before), after=list(after), Phi_before=pb, Phi_after=pa, M=M))

    return {
        "rule": rule,
        "before_CLV": list(before),
        "after_CLV": list(after),
        "L_delta": La - Lb,
        "V_delta": Va - Vb,
        "Phi_before": pb,
        "Phi_after": pa,
        "Phi_drop": pb - pa,
        "literal_growth": La > Lb,
        "failures": failures,
    }


def check_rup_transition(before_formula, after_formula, root, context):
    before = measure3(before_formula)
    after = measure3(after_formula)
    Cb, Lb, Vb = before
    Ca, La, Va = after
    M = int(root["M"])
    failures = []
    if Ca > Cb or Va > Vb:
        failures.append(falsifier("RUP_CLAUSE_OR_VARIABLE_INCREASE", context=context, before=list(before), after=list(after)))
    if La >= Lb:
        failures.append(falsifier("RUP_LITERAL_DESCENT_FAILURE", context=context, before=list(before), after=list(after)))
    pb = phi(before, M)
    pa = phi(after, M)
    if pa >= pb:
        failures.append(falsifier("COMBINED_PHI_NONDECREASE", context=context, transition="RUP", before=list(before), after=list(after), Phi_before=pb, Phi_after=pa, M=M))
    return {
        "before_CLV": list(before),
        "after_CLV": list(after),
        "L_delta": La - Lb,
        "V_delta": Va - Vb,
        "Phi_before": pb,
        "Phi_after": pa,
        "Phi_drop": pb - pa,
        "failures": failures,
    }


def audit_simplify_formula(name, formula):
    formula = r33.canonical_formula(formula)
    root = constants(formula)
    result = r33.simplify(formula)
    rows = []
    failures = []
    growth = []
    for i, record in enumerate(result.get("history", [])):
        row = check_r33_record(record, root, f"{name}:r33:{i}")
        rows.append(row)
        failures.extend(row["failures"])
        if row["rule"] == "BOUNDED_VARIABLE_ELIMINATION" and row["literal_growth"]:
            growth.append(row)
    observed_checks = int(result.get("total_check_operation_count_upper_ledger", 0))
    check_bound = (len(rows) + 1) * int(root["K_R33_search_iteration"])
    if observed_checks > check_bound:
        failures.append(falsifier("R33_WORK_LEDGER_BOUND_FAILURE", context=name, observed=observed_checks, bound=check_bound))
    return {
        "name": name,
        "root": root,
        "terminal": result.get("terminal"),
        "rule_counts": result.get("rule_counts", {}),
        "R33_transition_count": len(rows),
        "R33_check_ops": observed_checks,
        "R33_local_bound": check_bound,
        "rows": rows,
        "BVE_literal_growth_rows": growth,
        "failures": failures,
    }


def guaranteed_rule_controls():
    return [
        ("TAUTOLOGY_CONTROL", r33.canonical_formula([(1, -1, 2), (1, 3), (-2, -3)])),
        ("PURE_CONTROL", r33.canonical_formula([(1, 2), (1, -2)])),
        ("SUBSUMPTION_CONTROL", r33.canonical_formula([(1, 2), (1, 2, 3), (-1, -2), (-1, -2, -3)])),
        ("BUILTIN_BLOCKED_CONTROL", r33.blocked_clause_control()),
        ("BUILTIN_BVE_CONTROL", r33.bve_control()),
        ("BUILTIN_EASY_REDUNDANT_TAIL", r33.easy_redundant_tail()),
    ]


def audit_control_corpus():
    audits = []
    failures = []
    growth_witnesses = []
    rule_counts = Counter()

    corpus = guaranteed_rule_controls()
    for n in (8, 12, 16, 20, 24):
        corpus.append((f"PRISM_{n}", r33.prism_tseitin(n)))
    for seed in (33001, 33002, 33003, 33004):
        corpus.append((f"RANDOM24_{seed}", r33.deterministic_random_3cnf(seed)))

    # Frozen, truth-blind stress corpus for an actual BVE L-growth history transition.
    for seed in range(51000, 51200):
        n = (8, 10, 12, 14)[seed % 4]
        ratio = (2.5, 3.0, 3.5, 4.0)[seed % 4]
        corpus.append((f"BVE_GROWTH_ATTACK_{seed}_n{n}_r{ratio}", r33.deterministic_random_3cnf(seed, n=n, ratio=ratio)))

    for name, formula in corpus:
        a = audit_simplify_formula(name, formula)
        audits.append(a)
        failures.extend(a["failures"])
        rule_counts.update({str(k): int(v) for k, v in a["rule_counts"].items()})
        for row in a["BVE_literal_growth_rows"]:
            growth_witnesses.append({"formula_name": name, **row})

    return {
        "formula_count": len(audits),
        "aggregate_rule_counts": dict(sorted(rule_counts.items())),
        "BVE_literal_growth_witness_count": len(growth_witnesses),
        "first_BVE_literal_growth_witness": growth_witnesses[0] if growth_witnesses else None,
        "audits": audits,
        "failures": failures,
    }


def audit_an_interleaving():
    chain = r50g25g._chain()
    _b, _r50g23, r35b, _r33m, _r47jm = chain
    parent, reconstruction = an.reconstruct_am_parent(chain)
    if y.canonical_hash(parent) != an.PARENT_HASH:
        return {"technical_failure": falsifier("AN_WITNESS_REPRODUCTION_FAILURE", stage="parent", observed_hash=y.canonical_hash(parent))}
    exact = y.exact_dp_record(parent, an.PIVOT)
    if exact is None or not exact.get("replay_pass"):
        return {"technical_failure": falsifier("AN_WITNESS_REPRODUCTION_FAILURE", stage="exact_dp")}
    state = r33.canonical_formula(exact["transformed"])
    if y.canonical_hash(state) != an.RAW_CHILD_HASH or list(measure3(state)) != list(an.RAW_CHILD_CLV):
        return {"technical_failure": falsifier("AN_WITNESS_REPRODUCTION_FAILURE", stage="raw_child", observed_hash=y.canonical_hash(state), observed_CLV=list(measure3(state)))}

    root_formula = state
    root = constants(root_formula)
    failures = []
    rows = []
    r33_rules = Counter()
    r33_check_ops = 0
    rup_ledger = {"rup_checks": 0, "up_clause_scans": 0, "up_literal_inspections": 0}
    successful_steps = 0
    r33_steps = 0
    rup_steps = 0

    for round_index in range(EXPECTED_AN_RUPS + 1):
        simp = r33.simpl(state)
        r33_check_ops += int(simp.get("total_check_operation_count_upper_ledger", 0))
        r33_rules.update({str(k): int(v) for k, v in simp.get("rule_counts", {}).items()})
        for i, record in enumerate(simp.get("history", [])):
            rr = check_r33_record(record, root, f"AN:round{round_index}:r33:{i}")
            rows.append({"transition": "R33", "round": round_index, **rr})
            failures.extend(rr["failures"])
            r33_steps += 1
            successful_steps += 1

        after_r33 = r33.canonical_formula(simp["final_formula"])
        cls = an.class_record(after_r33)
        if cls["AI_class_pass"] is True:
            return {"technical_failure": falsifier("AN_WITNESS_REPRODUCTION_FAILURE", stage="unexpected_R33_reentry", round=round_index, RUP_count=rup_steps)}
        if simp.get("terminal") != "STALLED_STACK_LEAN_CORE":
            return {"technical_failure": falsifier("AN_WITNESS_REPRODUCTION_FAILURE", stage="unexpected_R33_terminal", round=round_index, terminal=simp.get("terminal"))}

        proposal, ledger = r35b.first_rup_strengthening(after_r33)
        for k in rup_ledger:
            rup_ledger[k] += int(ledger.get(k, 0))
        if proposal is None:
            return {"technical_failure": falsifier("AN_WITNESS_REPRODUCTION_FAILURE", stage="missing_RUP", round=round_index, RUP_count=rup_steps)}
        if not r35b.independent_up_conflict_checker(after_r33, proposal["assumptions"]):
            return {"technical_failure": falsifier("REPLAY_OR_IMPLEMENTATION_FAILURE", stage="RUP_replay", round=round_index)}

        source = tuple(proposal["source_clause"])
        strengthened = tuple(proposal["strengthened_clause"])
        after_rup = r35b.replace_clause_with_subclause(after_r33, source, strengthened)
        after_rup = r33.canonical_formula(after_rup)
        rup_row = check_rup_transition(after_r33, after_rup, root, f"AN:round{round_index}:rup")
        rows.append({"transition": "RUP", "round": round_index, **rup_row})
        failures.extend(rup_row["failures"])
        rup_steps += 1
        successful_steps += 1

        after_cls = an.class_record(after_rup)
        if after_cls["AI_class_pass"] is True:
            if rup_steps != EXPECTED_AN_RUPS:
                return {"technical_failure": falsifier("AN_WITNESS_REPRODUCTION_FAILURE", stage="wrong_reentry_RUP_count", observed=rup_steps, expected=EXPECTED_AN_RUPS)}
            reentry = after_cls
            break
        state = after_rup
    else:
        return {"technical_failure": falsifier("AN_WITNESS_REPRODUCTION_FAILURE", stage="reentry_not_reached")}

    phi0 = int(root["Phi0"])
    if successful_steps > phi0:
        failures.append(falsifier("COMBINED_PHI_NONDECREASE", context="AN_total_step_count", successful_steps=successful_steps, Phi0=phi0))

    r33_bound = (2 * phi0 + 1) * int(root["K_R33_search_iteration"])
    if r33_check_ops > r33_bound:
        failures.append(falsifier("R33_WORK_LEDGER_BOUND_FAILURE", context="AN", observed=r33_check_ops, bound=r33_bound))

    calls = phi0 + 1
    Lmax = int(root["Lmax"])
    C0 = int(root["C0"])
    V0 = int(root["V0"])
    rup_bounds = {
        "rup_checks": calls * Lmax,
        "up_clause_scans": calls * Lmax * C0 * (V0 + 1),
        "up_literal_inspections": calls * Lmax * Lmax * (V0 + 1),
    }
    for k in rup_ledger:
        if rup_ledger[k] > rup_bounds[k]:
            failures.append(falsifier("RUP_WORK_LEDGER_BOUND_FAILURE", context="AN", metric=k, observed=rup_ledger[k], bound=rup_bounds[k]))

    phi_values = [int(row["Phi_after"]) for row in rows]
    return {
        "technical_failure": None,
        "root_hash": an.RAW_CHILD_HASH,
        "root_CLV": list(an.RAW_CHILD_CLV),
        "root_constants": root,
        "R33_steps": r33_steps,
        "RUP_steps": rup_steps,
        "successful_combined_steps": successful_steps,
        "R33_rule_counts": dict(sorted(r33_rules.items())),
        "R33_check_ops": r33_check_ops,
        "R33_check_ops_bound": r33_bound,
        "RUP_ledger": rup_ledger,
        "RUP_ledger_bounds": rup_bounds,
        "minimum_observed_Phi_drop": min((int(row["Phi_drop"]) for row in rows), default=None),
        "final_observed_Phi": phi_values[-1] if phi_values else phi0,
        "reentry": reentry,
        "parent_reconstruction_event_count": len(reconstruction),
        "rows": rows,
        "failures": failures,
    }


def structural_certificate():
    return {
        "potential": "Phi=L+(C0*V0+1)*V",
        "canonical_width_fact": "For canonical CNF, each clause contains at most one literal per variable, hence L<=C*V.",
        "RUP_schema": "Accepted one-literal RUP replaces one existing clause by a proper subclause, then canonicalizes. Therefore C'<=C, V'<=V, L'<=L-1, so Phi'<=Phi-1.",
        "non_BVE_R33_schema": "Tautology deletion, unit propagation, pure-literal autarky, subsumption, and blocked-clause elimination introduce no clauses or variables and remove at least one literal occurrence. Therefore L'<=L-1 and V'<=V, so Phi'<=Phi-1.",
        "BVE_schema": "Implemented BVE accepts only when number of unique resolvents <= number of removed parent clauses. Canonicalization cannot increase clause count; resolvents contain no pivot x, so C'<=C<=C0 and V'<=V-1<=V0-1. Thus L'<=C'*V'<=C0*(V0-1). With M=C0*V0+1, Phi'-Phi=(L'-L)+M(V'-V)<=C0*(V0-1)-M=-C0-1<0.",
        "successful_transition_bound": "Because Phi is a nonnegative integer and every successful R33 or accepted RUP transition decreases it by at least one, successful transitions in one fixed-root R33<->RUP phase are <= Phi0=L0+(C0*V0+1)*V0.",
        "formalization_status": "paper/executable certificate from the implemented transition definitions; not proof-assistant formalized"
    }


def run():
    control = audit_control_corpus()
    an_audit = audit_an_interleaving()
    if an_audit.get("technical_failure") is not None:
        return {
            "gate": GATE,
            "preregistration_commit": PREREG_COMMIT,
            "parent_AO_sync_head": PARENT_AO_SYNC_HEAD,
            "verdict": "REPLAY_OR_IMPLEMENTATION_FAILURE",
            "technical_failure": an_audit["technical_failure"],
            "firewalls": firewalls(),
        }

    failures = list(control["failures"]) + list(an_audit["failures"])
    verdict = COUNTEREXAMPLE if failures else SUCCESS
    return {
        "gate": GATE,
        "preregistration_commit": PREREG_COMMIT,
        "parent_AO_sync_head": PARENT_AO_SYNC_HEAD,
        "verdict": verdict,
        "structural_certificate": structural_certificate(),
        "AN_interleaving": an_audit,
        "control_corpus": control,
        "falsifier_count": len(failures),
        "falsifiers": failures,
        "scientific_scope": {
            "combined_R33_RUP_successful_transition_bound": "one fixed-root interleaving phase only",
            "outer_exact_DP_phase_count": "OPEN",
            "end_to_end_solver_runtime": "OPEN",
            "finite_controls": "attack surface only; structural claim is derived separately from implemented rule schemas",
            "BVE_growth_witness_absence_if_zero": "not evidence against possible BVE literal growth"
        },
        "recommended_next_gate": "R50G25AQ_OUTER_DP_PHASE_COUNT_OR_GLOBAL_AMORTIZED_POTENTIAL_COUNTEREXAMPLE" if verdict == SUCCESS else "R50G25AQ_AP_COUNTEREXAMPLE_FORENSICS",
        "firewalls": firewalls(),
    }


def firewalls():
    return {
        "P_VS_NP": "OPEN",
        "SAT_IN_P": "NOT_PROVED",
        "TRUMP_finished": False,
        "single_phase_polynomial_progress_is_not_end_to_end_polynomial_solver_runtime": True,
        "outer_exact_DP_phase_count_remains_open": True,
        "finite_replay_is_not_universal_proof": True,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="research/R50G25AP_RESULT.json")
    args = parser.parse_args()
    result = run()
    p = Path(args.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "gate": result.get("gate"),
        "verdict": result.get("verdict"),
        "falsifier_count": result.get("falsifier_count"),
        "AN_steps": result.get("AN_interleaving", {}).get("successful_combined_steps"),
        "AN_Phi0": result.get("AN_interleaving", {}).get("root_constants", {}).get("Phi0"),
        "BVE_literal_growth_witness_count": result.get("control_corpus", {}).get("BVE_literal_growth_witness_count"),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
