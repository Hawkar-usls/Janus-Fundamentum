from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r50g25g_micro_rup_restart_replay_source_lift_family as r50g25g
import janus_trump_r50g25x_adversarial_stall_search as r50g25x
import janus_trump_r50g25y_minimal_w_policy_counterexample_forensics as r50g25y
import janus_trump_r50g25aa_universal_controlled_dp_door_or_symbolic_counterexample as r50g25aa

GATE = "JANUS_TRUMP_R50G25AB_ANALYTIC_UB_PIVOT_SELECTOR_AND_AMORTIZED_POTENTIAL_FALSIFICATION"
AB_PREREG_COMMIT = "af0ae06061797ec8149f42da9529e9ffab620fc1"
AA_RESOURCE_LIMIT_RECEIPT_COMMIT = "71557e8cb433a9494da2e064118becff8ffec998"
EXPECTED_X_RESIDUALS = 15
EXPECTED_Y_CORE_HASH = "98d929c32c0f838a920888ca10c4a2f2eb9afe5ad58ac471d8854851e5bb7532"
LOCAL_MUTATION_CAP = 12


def canonical_hash(formula):
    return r50g25y.canonical_hash(r33.canonical_formula(formula))


def phi(measure, exponent):
    c, l, v = map(int, measure)
    return (c + l) * ((v + 1) ** int(exponent))


def selector_bounds(core):
    rows = []
    for var in r33.variables(core):
        ub = r50g25aa.analytic_dp_upper_bound(core, var)
        if ub is not None:
            rows.append(ub)
    rows.sort(key=lambda x: (int(x["UB_S"]), int(x["var"])))
    return rows


def policy_terminal_label(w):
    if not w.get("route"):
        return w.get("kind")
    tail = w["route"][-1]
    if w["kind"] == "TERMINAL":
        return tail.get("R33_terminal") or tail.get("stop") or "TERMINAL"
    if w["kind"] == "AFFINE":
        return tail.get("stop") or "AFFINE"
    return None


def analytic_run(initial, chain):
    initial = r33.canonical_formula(initial)
    c0, l0, v0 = r33.measure(initial)
    budget = (c0 + l0) * ((v0 + 1) ** 2)
    state = initial
    fallback = []
    residual_events = []
    phi4_exact_failures = []
    phi4_analytic_certificate_count = 0
    phi4_analytic_gap_count = 0
    phi3_full_cycle_checks = 0
    phi3_full_cycle_failures = []
    selector_bound_checks = 0
    exact_materializations = 0
    previous_residual_measure = None
    previous_residual_hash = None

    for outer in range(v0 + 1):
        try:
            w = r50g25y.policy_replay(state, chain)
        except AssertionError as exc:
            return {
                "status": "IMPLEMENTATION_FAILURE",
                "class": "W_POLICY_REPLAY_ASSERTION",
                "error": repr(exc),
                "budget": budget,
                "fallback_trace": fallback,
                "residual_events": residual_events,
            }

        if w["kind"] in {"TERMINAL", "AFFINE"}:
            return {
                "status": "TERMINAL",
                "terminal_kind": w["kind"],
                "terminal_label": policy_terminal_label(w),
                "budget": budget,
                "fallback_DP_count": len(fallback),
                "fallback_trace": fallback,
                "residual_events": residual_events,
                "selector_bound_checks": selector_bound_checks,
                "exact_materializations": exact_materializations,
                "phi4_analytic_certificate_count": phi4_analytic_certificate_count,
                "phi4_analytic_gap_count": phi4_analytic_gap_count,
                "phi4_exact_failures": phi4_exact_failures,
                "phi3_full_cycle_checks": phi3_full_cycle_checks,
                "phi3_full_cycle_failures": phi3_full_cycle_failures,
                "max_controlled_state_size": max([c0 + l0] + [r["after_size"] for r in fallback]),
            }

        if w["kind"] != "RESIDUAL":
            return {
                "status": "IMPLEMENTATION_FAILURE",
                "class": "UNEXPECTED_W_KIND",
                "kind": w["kind"],
                "budget": budget,
                "fallback_trace": fallback,
                "residual_events": residual_events,
            }

        core = r33.canonical_formula(w["state"])
        before = r33.measure(core)
        h = canonical_hash(core)
        before_size = int(before[0] + before[1])

        if previous_residual_measure is not None:
            phi3_full_cycle_checks += 1
            if not (phi(before, 3) < phi(previous_residual_measure, 3)):
                phi3_full_cycle_failures.append({
                    "previous_residual_hash": previous_residual_hash,
                    "previous_CLV": list(previous_residual_measure),
                    "current_residual_hash": h,
                    "current_CLV": list(before),
                    "Phi3_previous": phi(previous_residual_measure, 3),
                    "Phi3_current": phi(before, 3),
                })

        if before_size > budget:
            return {
                "status": "SELECTOR_GAP",
                "class": "CURRENT_STATE_EXCEEDS_ROOT_BUDGET",
                "budget": budget,
                "residual_hash": h,
                "residual_CLV": list(before),
                "fallback_DP_count": len(fallback),
                "fallback_trace": fallback,
                "residual_events": residual_events,
            }

        if len(fallback) >= v0:
            return {
                "status": "RESIDUAL_LIMIT",
                "class": "RESIDUAL_AFTER_AT_MOST_V0_ANALYTIC_FALLBACKS",
                "budget": budget,
                "residual_hash": h,
                "residual_CLV": list(before),
                "fallback_DP_count": len(fallback),
                "fallback_trace": fallback,
                "residual_events": residual_events,
            }

        bounds = selector_bounds(core)
        selector_bound_checks += len(bounds)
        if not bounds:
            return {
                "status": "SELECTOR_GAP",
                "class": "NO_ANALYTIC_DP_PIVOT",
                "budget": budget,
                "residual_hash": h,
                "residual_CLV": list(before),
                "fallback_DP_count": len(fallback),
                "fallback_trace": fallback,
                "residual_events": residual_events,
            }

        chosen_bound = bounds[0]
        chosen_var = int(chosen_bound["var"])
        ub_s = int(chosen_bound["UB_S"])
        phi4_analytic = ub_s * (int(before[2]) ** 4) < before_size * ((int(before[2]) + 1) ** 4)
        if phi4_analytic:
            phi4_analytic_certificate_count += 1
        else:
            phi4_analytic_gap_count += 1

        event = {
            "outer_round": outer,
            "residual_hash": h,
            "residual_CLV": list(before),
            "budget": budget,
            "pivot_count": len(bounds),
            "chosen_var": chosen_var,
            "chosen_UB_S": ub_s,
            "budget_slack": int(budget - ub_s),
            "Phi4_analytic_certificate": bool(phi4_analytic),
            "second_best_UB_S": None if len(bounds) < 2 else int(bounds[1]["UB_S"]),
        }
        residual_events.append(event)

        if ub_s > budget:
            return {
                "status": "SELECTOR_GAP",
                "class": "MIN_ANALYTIC_UB_EXCEEDS_ROOT_BUDGET",
                "budget": budget,
                "residual_hash": h,
                "residual_CLV": list(before),
                "chosen_var": chosen_var,
                "min_UB_S": ub_s,
                "all_bounds": bounds,
                "fallback_DP_count": len(fallback),
                "fallback_trace": fallback,
                "residual_events": residual_events,
                "selector_bound_checks": selector_bound_checks,
                "exact_materializations": exact_materializations,
            }

        try:
            rec = r50g25y.exact_dp_record(core, chosen_var)
        except AssertionError as exc:
            return {
                "status": "IMPLEMENTATION_FAILURE",
                "class": "EXACT_DP_RECORD_ASSERTION",
                "error": repr(exc),
                "residual_hash": h,
                "chosen_var": chosen_var,
                "chosen_UB_S": ub_s,
                "budget": budget,
            }
        exact_materializations += 1
        if rec is None:
            return {
                "status": "IMPLEMENTATION_FAILURE",
                "class": "ANALYTIC_PIVOT_HAS_NO_EXACT_DP_RECORD",
                "residual_hash": h,
                "chosen_var": chosen_var,
                "chosen_UB_S": ub_s,
                "budget": budget,
            }
        if not rec.get("replay_pass"):
            return {
                "status": "IMPLEMENTATION_FAILURE",
                "class": "EXACT_DP_REPLAY_FAILURE",
                "residual_hash": h,
                "chosen_var": chosen_var,
                "chosen_UB_S": ub_s,
                "budget": budget,
            }

        transformed = r33.canonical_formula(rec["transformed"])
        after = r33.measure(transformed)
        after_size = int(after[0] + after[1])
        if after_size > ub_s:
            return {
                "status": "IMPLEMENTATION_FAILURE",
                "class": "ANALYTIC_BOUND_UNSOUND",
                "residual_hash": h,
                "chosen_var": chosen_var,
                "chosen_UB_S": ub_s,
                "exact_size": after_size,
                "budget": budget,
            }
        if after_size > budget:
            return {
                "status": "IMPLEMENTATION_FAILURE",
                "class": "CERTIFIED_WITHIN_BUT_EXACT_EXCEEDS_B",
                "residual_hash": h,
                "chosen_var": chosen_var,
                "chosen_UB_S": ub_s,
                "exact_size": after_size,
                "budget": budget,
            }
        if int(after[2]) >= int(before[2]):
            return {
                "status": "IMPLEMENTATION_FAILURE",
                "class": "VARIABLE_COUNT_NOT_DECREASING",
                "residual_hash": h,
                "chosen_var": chosen_var,
                "before_CLV": list(before),
                "after_CLV": list(after),
            }

        phi4_exact_ok = phi(after, 4) < phi(before, 4)
        if not phi4_exact_ok:
            phi4_exact_failures.append({
                "residual_hash": h,
                "chosen_var": chosen_var,
                "before_CLV": list(before),
                "after_CLV": list(after),
                "chosen_UB_S": ub_s,
                "Phi4_before": phi(before, 4),
                "Phi4_after": phi(after, 4),
            })

        fallback.append({
            "outer_round": outer,
            "residual_hash": h,
            "var": chosen_var,
            "before_CLV": list(before),
            "after_CLV": list(after),
            "before_size": before_size,
            "after_size": after_size,
            "budget": budget,
            "UB_S": ub_s,
            "analytic_slack": int(budget - ub_s),
            "replay_pass": True,
            "Phi4_analytic_certificate": bool(phi4_analytic),
            "Phi4_exact_descent": bool(phi4_exact_ok),
        })
        previous_residual_measure = before
        previous_residual_hash = h
        state = transformed

    return {
        "status": "RESIDUAL_LIMIT",
        "class": "RESIDUAL_AFTER_AT_MOST_V0_ANALYTIC_FALLBACKS",
        "budget": budget,
        "fallback_DP_count": len(fallback),
        "fallback_trace": fallback,
        "residual_events": residual_events,
    }


def reproduce_base_cases(chain):
    x = r50g25x.run()
    if x["residual_fixpoint_count"] != EXPECTED_X_RESIDUALS:
        raise AssertionError(("AB_X_RESIDUAL_COUNT_DRIFT", x["residual_fixpoint_count"]))
    cases = []
    for i, res in enumerate(x["residuals"]):
        f = r33.canonical_formula(res["residual_formula"])
        cases.append({
            "name": f"X_RESIDUAL_{i:02d}",
            "family": res["family"],
            "source": "ROOT_REACHABLE_X_RESIDUAL",
            "formula": f,
            "hash": canonical_hash(f),
        })

    _sealed, target = r47j.load_counterexample()
    minimized, _ledger = r50g25y.truth_blind_minimize(target, chain)
    y = r50g25y.policy_replay(minimized, chain)
    if y["kind"] != "RESIDUAL":
        raise AssertionError(("AB_Y_CORE_NOT_RESIDUAL", y["kind"]))
    ycore = r33.canonical_formula(y["state"])
    if canonical_hash(ycore) != EXPECTED_Y_CORE_HASH:
        raise AssertionError(("AB_Y_CORE_HASH_DRIFT", canonical_hash(ycore)))
    cases.append({
        "name": "Y_MINIMIZED_RESIDUAL_CORE",
        "family": "Y_MINIMIZED_R47",
        "source": "ROOT_REACHABLE_Y_CORE",
        "formula": ycore,
        "hash": canonical_hash(ycore),
    })
    return cases


def mutate_existing_variables(formula, seed):
    formula = list(r33.canonical_formula(formula))
    vs = list(r33.variables(formula))
    if len(vs) < 3 or not formula:
        return r33.canonical_formula(formula)
    rng = random.Random(int(seed))
    idx = rng.randrange(len(formula))
    for _ in range(80):
        chosen = sorted(rng.sample(vs, 3))
        clause = r33.canonical_clause([v if rng.getrandbits(1) else -v for v in chosen])
        if clause not in formula:
            formula[idx] = clause
            return r33.canonical_formula(formula)
    return r33.canonical_formula(formula)


def local_stress_cases(base_cases, chain):
    ranked = sorted(base_cases, key=lambda c: (r33.measure(c["formula"])[2], c["hash"]), reverse=True)[:6]
    accepted = []
    seen = {tuple(c["formula"]) for c in base_cases}
    attempts = 0
    for pi, parent in enumerate(ranked):
        for j in range(12):
            if len(accepted) >= LOCAL_MUTATION_CAP:
                break
            attempts += 1
            seed = 73000000 + 1000 * pi + j
            f = mutate_existing_variables(parent["formula"], seed)
            if tuple(f) in seen:
                continue
            seen.add(tuple(f))
            try:
                w = r50g25y.policy_replay(f, chain)
            except AssertionError:
                continue
            if w["kind"] != "RESIDUAL":
                continue
            core = r33.canonical_formula(w["state"])
            if tuple(core) in seen:
                continue
            seen.add(tuple(core))
            accepted.append({
                "name": f"LOCAL_RESIDUAL_MUTATION_{len(accepted):02d}",
                "family": "LOCAL_RESIDUAL_MUTATION",
                "source": "LOCAL_STRUCTURAL_STRESS_NOT_CLAIMED_ROOT_REACHABLE",
                "formula": core,
                "hash": canonical_hash(core),
                "meta": {"parent_hash": parent["hash"], "seed": seed},
            })
        if len(accepted) >= LOCAL_MUTATION_CAP:
            break
    return accepted, attempts


def run():
    chain = r50g25g._chain()
    base = reproduce_base_cases(chain)
    local, mutation_attempts = local_stress_cases(base, chain)
    cases = base + local

    rows = []
    status_hist = Counter()
    terminal_hist = Counter()
    selector_gaps = []
    implementation_failures = []
    residual_limits = []
    phi4_failures = []
    phi3_failures = []
    total_bound_checks = 0
    total_exact_materializations = 0
    max_fallback = None
    tightest_analytic_slack = None

    for case in cases:
        out = analytic_run(case["formula"], chain)
        row = {
            "name": case["name"],
            "family": case["family"],
            "source": case["source"],
            "hash": case["hash"],
            "initial_CLV": list(r33.measure(case["formula"])),
            **out,
        }
        rows.append(row)
        status_hist[out["status"]] += 1
        total_bound_checks += int(out.get("selector_bound_checks", 0))
        total_exact_materializations += int(out.get("exact_materializations", 0))
        if out["status"] == "TERMINAL":
            terminal_hist[str(out.get("terminal_label") or out.get("terminal_kind"))] += 1
        elif out["status"] == "SELECTOR_GAP":
            selector_gaps.append(row)
        elif out["status"] == "IMPLEMENTATION_FAILURE":
            implementation_failures.append(row)
        elif out["status"] == "RESIDUAL_LIMIT":
            residual_limits.append(row)
        phi4_failures.extend({"case": case["name"], **x} for x in out.get("phi4_exact_failures", []))
        phi3_failures.extend({"case": case["name"], **x} for x in out.get("phi3_full_cycle_failures", []))
        if out.get("fallback_DP_count") is not None:
            key = (int(out.get("fallback_DP_count", 0)), case["hash"])
            if max_fallback is None or key > (int(max_fallback.get("fallback_DP_count", 0)), max_fallback["hash"]):
                max_fallback = row
        for ev in out.get("residual_events", []):
            slack = int(ev["budget_slack"])
            if tightest_analytic_slack is None or slack < tightest_analytic_slack[0]:
                tightest_analytic_slack = (slack, case["name"], ev)

    if implementation_failures:
        verdict = "ANALYTIC_BOUND_UNSOUND_OR_DP_REPLAY_FAILURE" if any(
            r.get("class") in {"ANALYTIC_BOUND_UNSOUND", "EXACT_DP_REPLAY_FAILURE", "CERTIFIED_WITHIN_BUT_EXACT_EXCEEDS_B"}
            for r in implementation_failures
        ) else "IMPLEMENTATION_FAILURE"
    elif selector_gaps:
        verdict = "ANALYTIC_SELECTOR_BUDGET_GAP_FOUND"
    elif residual_limits:
        verdict = "RESIDUAL_AFTER_AT_MOST_V0_ANALYTIC_FALLBACKS"
    elif phi4_failures:
        verdict = "PHI4_CANDIDATE_FALSIFIED_WITHOUT_SELECTOR_FAILURE"
    else:
        verdict = "ANALYTIC_SELECTOR_TERMINATES_ON_PREREGISTERED_DOMAIN"

    next_gate = (
        "R50G25AC_MINIMIZE_ANALYTIC_SELECTOR_GAP_AND_COMPARE_WITH_EXACT_PIVOTS"
        if selector_gaps
        else "R50G25AC_SYMBOLIC_MIN_UB_EXISTENCE_INEQUALITY_OR_COUNTEREXAMPLE"
    )

    return {
        "gate": GATE,
        "AB_preregistration_commit": AB_PREREG_COMMIT,
        "parent_AA_resource_limit_receipt_commit": AA_RESOURCE_LIMIT_RECEIPT_COMMIT,
        "verdict": verdict,
        "domain": {
            "root_reachable_case_count": len(base),
            "local_structural_stress_case_count": len(local),
            "total_case_count": len(cases),
            "local_mutation_attempts": mutation_attempts,
            "truth_used_for_generation_ranking_or_selection": False,
            "exact_truth_authority": False,
        },
        "selector_contract": {
            "chosen_by": "min(UB_S,var)",
            "exact_DP_materializations_per_fallback": 1,
            "root_budget": "(C0+L0)*(V0+1)^2",
            "no_post_result_budget_change": True,
        },
        "status_partition": dict(sorted(status_hist.items())),
        "terminal_partition": dict(sorted(terminal_hist.items())),
        "selector_gap_count": len(selector_gaps),
        "implementation_failure_count": len(implementation_failures),
        "residual_limit_count": len(residual_limits),
        "Phi4_exact_failure_count": len(phi4_failures),
        "Phi3_full_cycle_failure_count": len(phi3_failures),
        "selector_gaps": selector_gaps,
        "implementation_failures": implementation_failures,
        "residual_limits": residual_limits,
        "Phi4_failures": phi4_failures,
        "Phi3_full_cycle_failures": phi3_failures,
        "total_selector_bound_checks": total_bound_checks,
        "total_exact_DP_materializations": total_exact_materializations,
        "tightest_analytic_slack": None if tightest_analytic_slack is None else {
            "slack": tightest_analytic_slack[0],
            "case": tightest_analytic_slack[1],
            "event": tightest_analytic_slack[2],
        },
        "max_fallback_case": max_fallback,
        "rows": rows,
        "potential_firewall": {
            "Phi3_and_Phi4_are_diagnostics_not_budget_replacements": True,
            "finite_potential_survival_is_not_universal_theorem": True,
        },
        "next_gate": next_gate,
        "firewall": {
            "P_VS_NP": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "TRUMP_finished": False,
            "finite_success_is_not_universal_coverage": True,
            "analytic_selector_gap_is_not_exact_DP_impossibility": True,
            "polynomial_state_bound_is_not_polynomial_runtime_without_universal_selector_existence_and_operation_bounds": True,
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
        "selector_gap_count": result["selector_gap_count"],
        "Phi4_exact_failure_count": result["Phi4_exact_failure_count"],
        "Phi3_full_cycle_failure_count": result["Phi3_full_cycle_failure_count"],
        "total_selector_bound_checks": result["total_selector_bound_checks"],
        "total_exact_DP_materializations": result["total_exact_DP_materializations"],
        "next_gate": result["next_gate"],
    }, indent=2, sort_keys=True))
    print("TIGHTEST_SLACK", json.dumps(result["tightest_analytic_slack"], sort_keys=True))
    print("MAX_FALLBACK", json.dumps(result["max_fallback_case"], sort_keys=True))


if __name__ == "__main__":
    main()
