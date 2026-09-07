from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r50g25g_micro_rup_restart_replay_source_lift_family as r50g25g
import janus_trump_r50g25y_minimal_w_policy_counterexample_forensics as y
import janus_trump_r50g25an_later_cheap_layer_necessity_forensics as an

GATE = "JANUS_TRUMP_R50G25AO_RUP_LADDER_PROGRESS_BOUND_OR_COUNTEREXAMPLE"
PREREG_COMMIT = "b3a7dda65813d1180d10e735fd0903856f9b51c7"
AN_SYNC_HEAD = "dc3b137179d4ab448986abd45c6ae8ac6d390690"
PARENT_HASH = an.PARENT_HASH
PIVOT = an.PIVOT
RAW_CHILD_HASH = an.RAW_CHILD_HASH
RAW_CHILD_CLV = list(an.RAW_CHILD_CLV)
EXPECTED_REENTRY_RUPS = 26


def fail(verdict: str, **extra):
    out = {
        "gate": GATE,
        "preregistration_commit": PREREG_COMMIT,
        "parent_AN_sync_head": AN_SYNC_HEAD,
        "verdict": verdict,
        "firewalls": {
            "P_VS_NP": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "TRUMP_finished": False,
            "finite_replay_is_not_universal_proof": True,
            "per_ladder_polynomial_bound_is_not_end_to_end_polynomial_solver_bound": True,
        },
    }
    out.update(extra)
    return out


def local_search_bounds(formula):
    C, L, V = map(int, r33.measure(formula))
    return {
        "C": C,
        "L": L,
        "V": V,
        "rup_checks": L,
        "up_clause_scans": L * C * (V + 1),
        "up_literal_inspections": L * L * (V + 1),
    }


def run():
    chain = r50g25g._chain()
    _b, r50g23, r35b, _r33m, _r47jm = chain

    parent, reconstruction = an.reconstruct_am_parent(chain)
    if y.canonical_hash(parent) != PARENT_HASH:
        return fail("AN_WITNESS_REPRODUCTION_FAILURE", stage="parent", observed_hash=y.canonical_hash(parent))

    exact = y.exact_dp_record(parent, PIVOT)
    if exact is None or not exact.get("replay_pass"):
        return fail("AN_WITNESS_REPRODUCTION_FAILURE", stage="exact_dp")
    state = r33.canonical_formula(exact["transformed"])
    if y.canonical_hash(state) != RAW_CHILD_HASH or list(r33.measure(state)) != RAW_CHILD_CLV:
        return fail(
            "AN_WITNESS_REPRODUCTION_FAILURE",
            stage="raw_child",
            observed_hash=y.canonical_hash(state),
            observed_CLV=list(r33.measure(state)),
        )

    C0, L0, V0 = map(int, r33.measure(state))
    frozen_total_bounds = {
        "successful_RUP_count": L0,
        "rup_checks_including_one_final_no_proposal_scan": L0 * (L0 + 1),
        "up_clause_scans_including_one_final_no_proposal_scan": L0 * (L0 + 1) * C0 * (V0 + 1),
        "up_literal_inspections_including_one_final_no_proposal_scan": L0 * L0 * (L0 + 1) * (V0 + 1),
    }

    totals = {"rup_checks": 0, "up_clause_scans": 0, "up_literal_inspections": 0}
    rows = []
    rup_count = 0
    aggregated_r33_rules = Counter()
    min_rup_literal_drop = None
    slack_deltas = []

    # The frozen AN witness reenters after 26 accepted RUP strengthenings.
    for round_index in range(EXPECTED_REENTRY_RUPS + 1):
        before_r33 = r33.canonical_formula(state)
        Cb, Lb, Vb = map(int, r33.measure(before_r33))
        simp = r33.simplify(before_r33)
        after_r33 = r33.canonical_formula(simp["final_formula"])
        Ca, La, Va = map(int, r33.measure(after_r33))
        aggregated_r33_rules.update({str(k): int(v) for k, v in simp.get("rule_counts", {}).items()})

        if La > Lb:
            return fail(
                "INTERLEAVED_R33_LITERAL_MONOTONICITY_FAILURE",
                round=round_index,
                before_CLV=[Cb, Lb, Vb],
                after_R33_CLV=[Ca, La, Va],
                R33_rule_counts=dict(simp.get("rule_counts", {})),
                completed_rows=rows,
            )

        after_r33_class = an.class_record(after_r33)
        if after_r33_class["AI_class_pass"] is True:
            return fail(
                "AN_WITNESS_REPRODUCTION_FAILURE",
                stage="unexpected_R33_reentry",
                round=round_index,
                RUP_count=rup_count,
                state=after_r33_class,
            )
        if simp["terminal"] != "STALLED_STACK_LEAN_CORE":
            return fail(
                "AN_WITNESS_REPRODUCTION_FAILURE",
                stage="unexpected_R33_terminal",
                round=round_index,
                terminal=str(simp["terminal"]),
            )

        bounds = local_search_bounds(after_r33)
        proposal, ledger = r35b.first_rup_strengthening(after_r33)
        for key in totals:
            totals[key] += int(ledger.get(key, 0))

        if proposal is None:
            return fail(
                "AN_WITNESS_REPRODUCTION_FAILURE",
                stage="missing_RUP_before_expected_reentry",
                round=round_index,
                RUP_count=rup_count,
                scan_ledger=ledger,
            )

        source = tuple(proposal["source_clause"])
        strengthened = tuple(proposal["strengthened_clause"])
        removed = int(proposal["removed_literal"])
        proper = (
            len(source) == len(strengthened) + 1
            and set(strengthened) < set(source)
            and removed in source
            and removed not in strengthened
            and set(source) - set(strengthened) == {removed}
        )
        if not proper:
            return fail(
                "RUP_PROPER_SUBCLAUSE_FAILURE",
                round=round_index,
                source_clause=list(source),
                strengthened_clause=list(strengthened),
                removed_literal=removed,
            )

        if not r35b.independent_up_conflict_checker(after_r33, proposal["assumptions"]):
            return fail("RUP_REPLAY_FAILURE", round=round_index, proposal=proposal)

        if int(ledger.get("rup_checks", 0)) > bounds["rup_checks"]:
            return fail("RUP_CHECK_BOUND_FAILURE", round=round_index, actual=ledger, bound=bounds)
        if int(ledger.get("up_clause_scans", 0)) > bounds["up_clause_scans"]:
            return fail("RUP_UP_CLAUSE_SCAN_BOUND_FAILURE", round=round_index, actual=ledger, bound=bounds)
        if int(ledger.get("up_literal_inspections", 0)) > bounds["up_literal_inspections"]:
            return fail("RUP_UP_LITERAL_INSPECTION_BOUND_FAILURE", round=round_index, actual=ledger, bound=bounds)

        before_rup_class = an.class_record(after_r33)
        after_rup = r35b.replace_clause_with_subclause(after_r33, source, strengthened)
        after_rup = r33.canonical_formula(after_rup)
        Cr, Lr, Vr = map(int, r33.measure(after_rup))
        literal_drop = La - Lr
        if literal_drop < 1 or Cr > Ca or Vr > Va:
            return fail(
                "RUP_STRICT_LITERAL_DESCENT_FAILURE",
                round=round_index,
                before_CLV=[Ca, La, Va],
                after_RUP_CLV=[Cr, Lr, Vr],
                literal_drop=literal_drop,
            )

        rup_count += 1
        min_rup_literal_drop = literal_drop if min_rup_literal_drop is None else min(min_rup_literal_drop, literal_drop)
        after_rup_class = an.class_record(after_rup)
        before_slack = before_rup_class.get("AI_class_slack")
        after_slack = after_rup_class.get("AI_class_slack")
        slack_delta = None if before_slack is None or after_slack is None else int(after_slack) - int(before_slack)
        if slack_delta is not None:
            slack_deltas.append(slack_delta)

        rows.append({
            "round": round_index,
            "before_R33_CLV": [Cb, Lb, Vb],
            "after_R33_CLV": [Ca, La, Va],
            "R33_rule_counts": dict(simp.get("rule_counts", {})),
            "R33_literal_nonincrease": La <= Lb,
            "RUP_source_clause_width": len(source),
            "RUP_strengthened_clause_width": len(strengthened),
            "RUP_removed_literal": removed,
            "RUP_scan_ledger": {k: int(ledger.get(k, 0)) for k in totals},
            "RUP_local_bounds": bounds,
            "after_RUP_CLV": [Cr, Lr, Vr],
            "RUP_literal_drop": literal_drop,
            "AI_slack_before_RUP": before_slack,
            "AI_slack_after_RUP": after_slack,
            "AI_slack_delta": slack_delta,
        })

        if after_rup_class["AI_class_pass"] is True:
            if rup_count != EXPECTED_REENTRY_RUPS:
                return fail(
                    "AN_WITNESS_REPRODUCTION_FAILURE",
                    stage="wrong_reentry_RUP_count",
                    observed=rup_count,
                    expected=EXPECTED_REENTRY_RUPS,
                    reentry_state=after_rup_class,
                )
            break
        state = after_rup
    else:
        return fail("AN_WITNESS_REPRODUCTION_FAILURE", stage="reentry_not_reached")

    if rup_count > frozen_total_bounds["successful_RUP_count"]:
        return fail("RUP_SUCCESS_COUNT_BOUND_FAILURE", actual=rup_count, bound=frozen_total_bounds)
    if totals["rup_checks"] > frozen_total_bounds["rup_checks_including_one_final_no_proposal_scan"]:
        return fail("RUP_CHECK_BOUND_FAILURE", actual=totals, bound=frozen_total_bounds)
    if totals["up_clause_scans"] > frozen_total_bounds["up_clause_scans_including_one_final_no_proposal_scan"]:
        return fail("RUP_UP_CLAUSE_SCAN_BOUND_FAILURE", actual=totals, bound=frozen_total_bounds)
    if totals["up_literal_inspections"] > frozen_total_bounds["up_literal_inspections_including_one_final_no_proposal_scan"]:
        return fail("RUP_UP_LITERAL_INSPECTION_BOUND_FAILURE", actual=totals, bound=frozen_total_bounds)

    diagnostic = {
        "slack_delta_min": min(slack_deltas) if slack_deltas else None,
        "slack_delta_max": max(slack_deltas) if slack_deltas else None,
        "slack_delta_negative_count": sum(1 for x in slack_deltas if x < 0),
        "slack_delta_zero_count": sum(1 for x in slack_deltas if x == 0),
        "slack_delta_positive_count": sum(1 for x in slack_deltas if x > 0),
        "note": "AI slack monotonicity is diagnostic only and is not required by the frozen literal-potential lemma.",
    }

    return {
        "gate": GATE,
        "preregistration_commit": PREREG_COMMIT,
        "parent_AN_sync_head": AN_SYNC_HEAD,
        "verdict": "RUP_LOCAL_LITERAL_DESCENT_PROVED_FROM_IMPLEMENTATION_AND_AN_LADDER_BOUND_AUDIT_PASS",
        "structural_certificate": {
            "accepted_RUP_removes_exactly_one_source_literal_before_canonicalization": True,
            "canonicalization_adds_no_literals_or_clauses": True,
            "therefore_RUP_strict_literal_descent": True,
            "candidate_search_is_single_literal_not_subset_enumeration": True,
            "per_candidate_UP_full_scan_bound": "V+1",
            "per_search_candidate_bound": "L",
            "conditional_ladder_statement": "If interleaved operators do not increase L, successful RUP strengthenings <= L_start.",
        },
        "frozen_AN_control": {
            "raw_child_hash": RAW_CHILD_HASH,
            "raw_child_CLV": RAW_CHILD_CLV,
            "RUP_count_to_AI_reentry": rup_count,
            "expected_RUP_count": EXPECTED_REENTRY_RUPS,
            "reentry": an.class_record(after_rup),
            "R33_rule_counts_before_reentry": dict(aggregated_r33_rules),
            "minimum_RUP_literal_drop": min_rup_literal_drop,
            "parent_reconstruction_event_count": len(reconstruction),
        },
        "frozen_symbolic_total_bounds": frozen_total_bounds,
        "observed_total_RUP_ledger": totals,
        "diagnostic_AI_slack": diagnostic,
        "rows": rows,
        "falsifier_counts": {
            "RUP_PROPER_SUBCLAUSE_FAILURE": 0,
            "RUP_STRICT_LITERAL_DESCENT_FAILURE": 0,
            "INTERLEAVED_R33_LITERAL_MONOTONICITY_FAILURE": 0,
            "RUP_SUCCESS_COUNT_BOUND_FAILURE": 0,
            "RUP_CHECK_BOUND_FAILURE": 0,
            "RUP_UP_CLAUSE_SCAN_BOUND_FAILURE": 0,
            "RUP_UP_LITERAL_INSPECTION_BOUND_FAILURE": 0,
            "RUP_REPLAY_FAILURE": 0,
            "AN_WITNESS_REPRODUCTION_FAILURE": 0,
            "LEDGER_OR_IMPLEMENTATION_FAILURE": 0,
        },
        "scientific_scope": {
            "source_level_RUP_literal_descent": "structural consequence of implemented first_rup_strengthening + replace_clause_with_subclause + canonical_formula semantics",
            "AN_interleaved_R33_nonincrease": "finite frozen witness audit",
            "end_to_end_solver_runtime": "OPEN",
            "outer_DP_phase_count": "NOT_BOUNDED_BY_AO",
        },
        "firewalls": {
            "P_VS_NP": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "TRUMP_finished": False,
            "finite_replay_is_not_universal_proof": True,
            "per_ladder_polynomial_bound_is_not_end_to_end_polynomial_solver_bound": True,
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="research/R50G25AO_RESULT.json")
    args = parser.parse_args()
    result = run()
    p = Path(args.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "gate": result.get("gate"),
        "verdict": result.get("verdict"),
        "RUP_count": result.get("frozen_AN_control", {}).get("RUP_count_to_AI_reentry"),
        "observed_ledger": result.get("observed_total_RUP_ledger"),
        "bounds": result.get("frozen_symbolic_total_bounds"),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
