from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from pathlib import Path

import janus_trump_r50g25b_source_realizability_minimum_joint_debt as r50g25b
import janus_trump_r50g25g_micro_rup_restart_replay_source_lift_family as r50g25g
import janus_trump_r50g25h_micro_rup_restart_broader_1212_polynomial_ledger_audit as r50g25h

GATE = "JANUS_TRUMP_R50G25L_POLYNOMIAL_SUPPORT_COVER_FINDER_OR_EXPLICIT_OBSTRUCTION"
EXPECTED_UNIQUE = 1212
PIVOT = 1


def canon(formula):
    return r50g25b.canon(formula)


def truth_signature(r33, formula):
    formula = r33.canonical_formula(formula)
    vs = list(r33.variables(formula))
    if len(vs) > 6:
        raise AssertionError(("R50G25L_VALIDATION_DOMAIN_DRIFT", len(vs)))
    bits = []
    model_count = 0
    for values in itertools.product((False, True), repeat=len(vs)):
        assignment = dict(zip(vs, values))
        sat = bool(r33.eval_formula(formula, assignment))
        bits.append("1" if sat else "0")
        model_count += int(sat)
    return {
        "variables": vs,
        "assignment_space_checked": 2 ** len(vs),
        "truth": "".join(bits),
        "model_count": model_count,
        "sat": model_count > 0,
    }


def polynomial_support_cover(formula):
    """Deterministic non-minimum cover. No subset search and no exact set cover."""
    a = r50g25b.r50g25a
    formula = canon(formula)
    bces = a.blocked_candidates(formula)
    bves = a.all_bve_candidates(formula)
    requirements = [("BCE", row) for row in bces] + [("BVE", row) for row in bves]
    additions = sorted(a.all_binary_additions(formula))

    masks = []
    incidence_checks = 0
    support_counts = [0] * len(requirements)
    for clause in additions:
        mask = 0
        for i, (kind, row) in enumerate(requirements):
            incidence_checks += 1
            if kind == "BCE":
                hit = a.bce_requirement_hit(row, clause)
            else:
                x = int(row["pivot"])
                hit = x in clause or -x in clause
            if hit:
                mask |= 1 << i
                support_counts[i] += 1
        masks.append((tuple(clause), mask))

    full = (1 << len(requirements)) - 1
    covered = 0
    chosen = []
    greedy_support_scans = 0
    obstruction = None
    while covered != full:
        missing = next(i for i in range(len(requirements)) if not (covered >> i) & 1)
        selected = None
        for clause, mask in masks:
            greedy_support_scans += 1
            if (mask >> missing) & 1:
                selected = (clause, mask)
                break
        if selected is None:
            kind, row = requirements[missing]
            obstruction = {
                "requirement_index": missing,
                "kind": kind,
                "row": row,
                "support_count": support_counts[missing],
            }
            break
        clause, mask = selected
        chosen.append(clause)
        covered |= mask

    c, l, v = r50g25b.r50g25a.r50g24.r50g23.r33.measure(formula)
    universe_bound = 2 * v * max(0, v - 1)
    requirement_bound = l + v
    incidence_bound = universe_bound * requirement_bound
    greedy_bound = universe_bound * requirement_bound
    # Direct loop-structure envelope for candidate discovery + incidence + greedy scan.
    # BCE: <= L*C pivot-opposite scans, BVE: <= V*C^2 parent pairs; each clause/set
    # operation is bounded by O(V) on this representation. The bound is deliberately loose.
    discovery_bound = (l * c + v * c * c + universe_bound) * max(1, v)
    total_meter = incidence_checks + greedy_support_scans
    total_bound = discovery_bound + incidence_bound + greedy_bound

    meter = {
        "C": c,
        "L": l,
        "V": v,
        "BCE_requirement_count": len(bces),
        "BVE_requirement_count": len(bves),
        "requirement_count": len(requirements),
        "binary_clause_universe_size": len(additions),
        "incidence_checks": incidence_checks,
        "greedy_support_scans": greedy_support_scans,
        "chosen_clause_count": len(chosen),
        "binary_clause_universe_bound_2VVm1": universe_bound,
        "requirement_bound_L_plus_V": requirement_bound,
        "incidence_check_bound": incidence_bound,
        "greedy_support_scan_bound": greedy_bound,
        "candidate_discovery_symbolic_bound": discovery_bound,
        "metered_incidence_plus_greedy": total_meter,
        "explicit_polynomial_total_bound": total_bound,
    }
    meter_pass = (
        len(additions) <= universe_bound
        and len(requirements) <= requirement_bound
        and incidence_checks <= incidence_bound
        and greedy_support_scans <= greedy_bound
        and total_meter <= total_bound
    )
    return {
        "clauses": [list(c) for c in chosen],
        "obstruction": obstruction,
        "all_requirements_covered": obstruction is None and covered == full,
        "meter": meter,
        "meter_pass": meter_pass,
    }


def run():
    _parent, unique = r50g25b.rebuild_unique_states()
    if len(unique) != EXPECTED_UNIQUE:
        raise AssertionError(("R50G25L_UNIQUE_TARGET_DRIFT", len(unique)))

    _b, r50g23, r35b, r33, r47j = r50g25g._chain()
    r42 = r50g23.r42

    cover_size_hist = Counter()
    requirement_hist = Counter()
    terminal_hist = Counter()
    rup_hist = Counter()
    restart_hist = Counter()
    obstruction_count = 0
    meter_violation_count = 0
    pivot_violation_count = 0
    micro_residual_count = 0
    exact_micro_mismatch_count = 0
    reconstruction_failure_count = 0
    target_to_augmented_truth_change_count = 0
    target_to_augmented_sat_status_change_count = 0
    scheduler_meter_violation_count = 0
    examples = []
    anomalies = []

    aggregate_finder_meter = Counter()

    for key, entry in sorted(unique.items(), key=lambda kv: (kv[1]["forced_CLV"], kv[0])):
        target = canon(entry["forced_formula"])
        state_hash = r50g23.r50g4.fhash(target)
        cover = polynomial_support_cover(target)
        meter = cover["meter"]
        for mk in ("incidence_checks", "greedy_support_scans", "chosen_clause_count", "explicit_polynomial_total_bound"):
            aggregate_finder_meter[mk] += int(meter[mk])
        requirement_hist[int(meter["requirement_count"])] += 1

        if not cover["meter_pass"]:
            meter_violation_count += 1
            anomalies.append({"state_hash": state_hash, "reason": "POLYNOMIAL_ACCOUNTING_VIOLATION", "meter": meter})
            continue
        if cover["obstruction"] is not None:
            obstruction_count += 1
            anomalies.append({"state_hash": state_hash, "reason": "EXPLICIT_REQUIREMENT_OBSTRUCTION", "obstruction": cover["obstruction"]})
            continue

        clauses = [tuple(int(x) for x in c) for c in cover["clauses"]]
        if any(PIVOT in c or -PIVOT in c for c in clauses):
            pivot_violation_count += 1
            anomalies.append({"state_hash": state_hash, "reason": "PIVOT_FREE_VIOLATION", "cover": cover["clauses"]})
            continue
        cover_size_hist[len(clauses)] += 1

        augmented = canon(r42.subsumption_minimize(list(target) + clauses))
        target_truth = truth_signature(r33, target)
        augmented_truth = truth_signature(r33, augmented)
        if target_truth["truth"] != augmented_truth["truth"]:
            target_to_augmented_truth_change_count += 1
        if bool(target_truth["sat"]) != bool(augmented_truth["sat"]):
            target_to_augmented_sat_status_change_count += 1

        micro = r50g25g.micro_normalize(augmented, r50g23, r35b, r33, r47j)
        term = str(micro.get("terminal")) if micro.get("terminal") is not None else "RESIDUAL_FIXPOINT"
        terminal_hist[term] += 1
        rup_count = int(micro.get("ledger", {}).get("RUP_successful_strengthenings", 0))
        restart_count = int(micro.get("restart_count", micro.get("ledger", {}).get("restart_count", 0)))
        rup_hist[rup_count] += 1
        restart_hist[restart_count] += 1

        if micro.get("semantic_sat") is None:
            micro_residual_count += 1
        elif bool(micro["semantic_sat"]) != bool(augmented_truth["sat"]):
            exact_micro_mismatch_count += 1
        if micro.get("semantic_sat") is True and not micro.get("SAT_reconstruction", {}).get("pass", False):
            reconstruction_failure_count += 1

        sched_env = r50g25h.polynomial_meter_envelope(r33.measure(augmented))
        observed_to_bound = {
            "R33_check_operation_upper_ledger": "R33_check_operation_upper_ledger_bound",
            "RUP_checks": "RUP_checks_bound",
            "RUP_UP_clause_scans": "RUP_UP_clause_scans_bound",
            "RUP_UP_literal_inspections": "RUP_UP_literal_inspections_bound",
            "restart_count": "restart_count_bound",
            "GF2_estimated_bit_ops": "GF2_estimated_bit_ops_bound",
        }
        if any(int(micro.get("ledger", {}).get(obs, 0)) > int(sched_env[bnd]) for obs, bnd in observed_to_bound.items()):
            scheduler_meter_violation_count += 1

        if len(examples) < 20:
            examples.append({
                "state_hash": state_hash,
                "requirements": int(meter["requirement_count"]),
                "polynomial_cover_size": len(clauses),
                "target_CLV": list(r33.measure(target)),
                "augmented_CLV": list(r33.measure(augmented)),
                "target_model_count": target_truth["model_count"],
                "augmented_model_count": augmented_truth["model_count"],
                "truth_changed": target_truth["truth"] != augmented_truth["truth"],
                "sat_status_changed": bool(target_truth["sat"]) != bool(augmented_truth["sat"]),
                "micro_terminal": term,
                "micro_RUP_strengthenings": rup_count,
                "micro_restarts": restart_count,
            })

    evaluated = EXPECTED_UNIQUE - obstruction_count - meter_violation_count - pivot_violation_count

    if meter_violation_count or scheduler_meter_violation_count:
        verdict = "POLYNOMIAL_ACCOUNTING_VIOLATION"
        next_gate = "R50G25M_POLYNOMIAL_ACCOUNTING_FORENSICS"
    elif pivot_violation_count:
        verdict = "IMPLEMENTATION_OR_REPLAY_FAILURE"
        next_gate = "R50G25M_PIVOT_FREE_COVER_FAILURE_FORENSICS"
    elif obstruction_count:
        verdict = "POLYNOMIAL_SUPPORT_COVER_EXPLICIT_REQUIREMENT_OBSTRUCTION"
        next_gate = "R50G25M_MINIMAL_SUPPORT_OBSTRUCTION_FORENSICS"
    elif micro_residual_count or exact_micro_mismatch_count or reconstruction_failure_count:
        verdict = "POLYNOMIAL_SUPPORT_COVER_SCHEDULER_COUNTEREXAMPLE"
        next_gate = "R50G25M_POLYNOMIAL_COVER_SCHEDULER_COUNTEREXAMPLE_FORENSICS"
    else:
        verdict = "POLYNOMIAL_SUPPORT_COVER_1212_TERMINAL"
        if target_to_augmented_truth_change_count:
            next_gate = "R50G25M_SEMANTICALLY_ADMISSIBLE_COVER_OR_EXPLICIT_NO_GO_WITNESS"
        else:
            next_gate = "R50G25M_OUTER_COVERAGE_AFTER_SEMANTICALLY_PRESERVING_POLYNOMIAL_COVER"

    return {
        "gate": GATE,
        "parent_preregistration_commit": "9ecbf412e4241d65e2d7f6a7f030a4de42439987",
        "coverage_contract": {
            "frozen_target_count": EXPECTED_UNIQUE,
            "new_source_skeletons_added": 0,
            "exact_minimum_cover_called_by_candidate_core": False,
            "truth_enumeration_is_validation_only": True,
        },
        "verdict": verdict,
        "evaluated_target_count": evaluated,
        "explicit_requirement_obstruction_count": obstruction_count,
        "finder_polynomial_meter_violation_count": meter_violation_count,
        "pivot_free_cover_violation_count": pivot_violation_count,
        "scheduler_polynomial_meter_violation_count": scheduler_meter_violation_count,
        "cover_size_histogram": {str(k): int(v) for k, v in sorted(cover_size_hist.items())},
        "requirement_count_histogram": {str(k): int(v) for k, v in sorted(requirement_hist.items())},
        "micro_terminal_partition": dict(sorted(terminal_hist.items())),
        "micro_RUP_strengthening_histogram": {str(k): int(v) for k, v in sorted(rup_hist.items())},
        "micro_restart_histogram": {str(k): int(v) for k, v in sorted(restart_hist.items())},
        "micro_residual_count": micro_residual_count,
        "exact_micro_semantic_mismatch_count": exact_micro_mismatch_count,
        "micro_SAT_reconstruction_failure_count": reconstruction_failure_count,
        "target_to_augmented_truth_change_count": target_to_augmented_truth_change_count,
        "target_to_augmented_sat_status_change_count": target_to_augmented_sat_status_change_count,
        "aggregate_finder_meter": dict(sorted(aggregate_finder_meter.items())),
        "examples": examples,
        "anomalies": anomalies[:24],
        "next_gate": next_gate,
        "interpretation_contract": {
            "polynomial_support_cover_is_not_minimum_cover": True,
            "covering_current_BCE_BVE_incidence_debt_is_not_global_scheduler_termination_proof": True,
            "adding_nonentailed_cover_clauses_is_not_a_semantics_preserving_SAT_reduction": True,
            "frozen_1212_success_is_not_outer_coverage": True,
        },
        "firewall": {
            "SAT_IN_P": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
            "ALL_DIRECT5_V7_HUB_CYCLE_ELIMINATED": False,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    args = ap.parse_args()
    out = run()
    text = json.dumps(out, sort_keys=True, indent=2)
    if args.out:
        p = Path(args.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
