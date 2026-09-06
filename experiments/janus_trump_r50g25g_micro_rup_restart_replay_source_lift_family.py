from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from pathlib import Path

import janus_trump_r50g25f_pi_rup_threshold_causal_support_schedule_lift as r50g25f

GATE = "JANUS_TRUMP_R50G25G_MICRO_RUP_RESTART_REPLAY_ACROSS_SOURCE_LIFT_STATE_FAMILY"
EXPECTED_GE3_UNIQUE = 991
EXPECTED_GE3_WEIGHTED = 1317
PIVOT = 1


def _chain():
    r50g25e = r50g25f.r50g25e
    r50g25d_pi = r50g25e.r50g25d_pi
    r50g25d = r50g25d_pi.r50g25d
    r50g25c = r50g25d.r50g25c
    r50g25b = r50g25c.r50g25b
    r50g25a = r50g25b.r50g25a
    r50g23 = r50g25a.r50g24.r50g23
    return r50g25b, r50g23, r50g23.r35b, r50g23.r33, r50g23.r47j


def exact_semantic(r33, formula):
    formula = r33.canonical_formula(formula)
    vs = list(r33.variables(formula))
    if len(vs) > 6:
        raise AssertionError(("R50G25G_EXACT_CONTROL_VAR_BOUND_DRIFT", len(vs)))
    model_count = 0
    first_model = None
    for bits in itertools.product((False, True), repeat=len(vs)):
        assignment = dict(zip(vs, bits))
        if r33.eval_formula(formula, assignment):
            model_count += 1
            if first_model is None:
                first_model = {str(k): bool(v) for k, v in sorted(assignment.items())}
    return {
        "variable_count": len(vs),
        "assignment_space_checked": 2 ** len(vs),
        "sat": model_count > 0,
        "model_count": model_count,
        "first_model": first_model,
    }


def micro_normalize(initial, r50g23, r35b, r33, r47j):
    r34 = r50g23.r34
    r42 = r50g23.r42
    state = r33.canonical_formula(initial)
    height_bound = r47j.restart_height_bound(state)
    rounds = []
    r33_reconstruction_results = []
    terminal = None
    semantic_sat = None
    terminal_assignment = None
    terminal_verification = None
    ledger = {
        "R33_check_operation_upper_ledger": 0,
        "R33_certificate_bytes": 0,
        "RUP_checks": 0,
        "RUP_UP_clause_scans": 0,
        "RUP_UP_literal_inspections": 0,
        "RUP_successful_strengthenings": 0,
        "GF2_estimated_bit_ops": 0,
        "restart_count": 0,
    }

    for round_index in range(height_bound + 1):
        before = state
        before_clv = r33.measure(before)
        reduced = r33.simplify(before)
        after_r33 = r33.canonical_formula(reduced["final_formula"])
        after_r33_clv = r33.measure(after_r33)
        if after_r33 != before and not after_r33_clv < before_clv:
            raise AssertionError(("R50G25G_MICRO_R33_NOT_STRICT_DESCENT", round_index, before_clv, after_r33_clv))
        if reduced["history"]:
            r33_reconstruction_results.append(reduced)
        ledger["R33_check_operation_upper_ledger"] += int(reduced["total_check_operation_count_upper_ledger"])
        ledger["R33_certificate_bytes"] += int(reduced["total_certificate_bytes"])

        row = {
            "round": round_index,
            "before_CLV": list(before_clv),
            "R33_apps": int(reduced["total_rule_applications"]),
            "after_R33_CLV": list(after_r33_clv),
            "R33_terminal": str(reduced["terminal"]),
        }

        if reduced["terminal"] != "STALLED_STACK_LEAN_CORE":
            solved = r42.solve_declared_terminal(after_r33, reduced["terminal"])
            if not solved["verification_pass"]:
                raise AssertionError(("R50G25G_MICRO_DECLARED_TERMINAL_VERIFY_FAIL", solved))
            terminal = str(solved["kind"])
            semantic_sat = bool(solved["sat"])
            terminal_assignment = solved.get("assignment")
            terminal_verification = solved
            state = after_r33
            row["stop"] = terminal
            rounds.append(row)
            break

        affine = r34.recognize_complete_affine_cnf(after_r33)
        row["affine_recognized"] = bool(affine["recognized"])
        if affine["recognized"]:
            solution = r34.solve_gf2_with_certificate(affine["equations"])
            verify = r34.verify_affine_certificate(after_r33, affine, solution)
            if not verify["pass"]:
                raise AssertionError(("R50G25G_MICRO_AFFINE_VERIFY_FAIL", verify))
            terminal = "AFFINE_XOR_SAT" if solution["sat"] else "AFFINE_XOR_UNSAT"
            semantic_sat = bool(solution["sat"])
            terminal_assignment = solution.get("assignment")
            terminal_verification = verify
            ledger["GF2_estimated_bit_ops"] += int(solution["estimated_bit_ops"])
            state = after_r33
            row["stop"] = terminal
            rounds.append(row)
            break

        proposal, proposal_ledger = r35b.first_rup_strengthening(after_r33)
        ledger["RUP_checks"] += int(proposal_ledger["rup_checks"])
        ledger["RUP_UP_clause_scans"] += int(proposal_ledger["up_clause_scans"])
        ledger["RUP_UP_literal_inspections"] += int(proposal_ledger["up_literal_inspections"])
        if proposal is None:
            state = after_r33
            terminal = None
            semantic_sat = None
            row["stop"] = "CERTIFIED_MICRO_RUP_RESTART_FIXPOINT"
            rounds.append(row)
            break

        source = tuple(int(x) for x in proposal["source_clause"])
        strengthened = tuple(int(x) for x in proposal["strengthened_clause"])
        assumptions = tuple(int(x) for x in proposal["assumptions"])
        if not r35b.independent_up_conflict_checker(after_r33, assumptions):
            raise AssertionError(("R50G25G_MICRO_RUP_CERT_FAIL", round_index, proposal))
        after_rup = r35b.replace_clause_with_subclause(after_r33, source, strengthened)
        after_rup_clv = r33.measure(after_rup)
        if not after_rup_clv < after_r33_clv:
            raise AssertionError(("R50G25G_MICRO_RUP_NOT_STRICT_DESCENT", round_index, after_r33_clv, after_rup_clv))
        if not after_rup_clv < before_clv:
            raise AssertionError(("R50G25G_MICRO_RESTART_NOT_STRICT_DESCENT", round_index, before_clv, after_rup_clv))

        ledger["RUP_successful_strengthenings"] += 1
        ledger["restart_count"] += 1
        row.update({
            "RUP_source_clause": list(source),
            "RUP_removed_literal": int(proposal["removed_literal"]),
            "RUP_strengthened_clause": list(strengthened),
            "after_single_RUP_CLV": list(after_rup_clv),
            "restart": True,
        })
        rounds.append(row)
        state = after_rup
    else:
        raise AssertionError(("R50G25G_MICRO_HEIGHT_BOUND_EXHAUSTED", height_bound))

    reconstruction = {"applicable": False, "pass": True}
    if semantic_sat is True:
        assignment = dict(terminal_assignment or {})
        for result in reversed(r33_reconstruction_results):
            assignment = r33.reconstruct_model(result, assignment)
        for v in r33.variables(initial):
            assignment.setdefault(int(v), False)
        passed = r33.eval_formula(r33.canonical_formula(initial), assignment)
        reconstruction = {
            "applicable": True,
            "pass": bool(passed),
            "assignment": {str(k): bool(v) for k, v in sorted(assignment.items())},
        }
        if not passed:
            raise AssertionError("R50G25G_MICRO_SAT_RECONSTRUCTION_FAIL")

    return {
        "terminal": terminal,
        "semantic_sat": semantic_sat,
        "terminal_verification": terminal_verification,
        "final_CLV": list(r33.measure(state)),
        "round_count": len(rounds),
        "restart_count": int(ledger["restart_count"]),
        "rounds": rounds,
        "ledger": ledger,
        "SAT_reconstruction": reconstruction,
    }


def add_ledger(dst, src, rup_strengthenings=None):
    for key in (
        "R33_check_operation_upper_ledger",
        "R33_certificate_bytes",
        "RUP_checks",
        "RUP_UP_clause_scans",
        "RUP_UP_literal_inspections",
        "GF2_estimated_bit_ops",
        "restart_count",
    ):
        dst[key] += int(src.get(key, 0))
    if rup_strengthenings is not None:
        dst["RUP_successful_strengthenings"] += int(rup_strengthenings)


def run():
    parent = r50g25f.run()
    if parent["next_gate"] != "R50G25G_MICRO_RUP_RESTART_REPLAY_ACROSS_SOURCE_LIFT_STATE_FAMILY":
        raise AssertionError(("R50G25G_PARENT_GATE_DRIFT", parent["next_gate"]))
    if parent["micro_RUP_restart_schedule"]["ledger"]["RUP_successful_strengthenings"] != 1:
        raise AssertionError("R50G25G_PARENT_MICRO_WITNESS_DRIFT")

    r50g25b, r50g23, r35b, r33, r47j = _chain()
    r42 = r50g23.r42
    _p, unique = r50g25b.rebuild_unique_states()
    skeletons = r50g23.clean_skeletons_from_frozen_r50g22()
    source_by_hash = {item["source_hash"]: item for item in skeletons}
    if len(source_by_hash) != 30:
        raise AssertionError(("R50G25G_FROZEN_SOURCE_COUNT_DRIFT", len(source_by_hash)))

    sealed_terminal = Counter()
    micro_terminal = Counter()
    terminal_pairs = Counter()
    exact_truth = Counter()
    micro_round_hist = Counter()
    micro_restart_hist = Counter()
    sealed_round_hist = Counter()
    sealed_restart_hist = Counter()
    micro_rup_strength_hist = Counter()

    family_unique = 0
    family_weighted = 0
    source_lift_fail = 0
    micro_terminal_unique = 0
    micro_terminal_weighted = 0
    residual_unique = 0
    residual_weighted = 0
    solved_semantic_agreement_unique = 0
    solved_semantic_agreement_weighted = 0
    exact_sealed_mismatch = 0
    exact_micro_mismatch = 0
    micro_reconstruction_fail = 0

    sealed_ledger = Counter({
        "R33_check_operation_upper_ledger": 0,
        "R33_certificate_bytes": 0,
        "RUP_checks": 0,
        "RUP_UP_clause_scans": 0,
        "RUP_UP_literal_inspections": 0,
        "RUP_successful_strengthenings": 0,
        "GF2_estimated_bit_ops": 0,
        "restart_count": 0,
    })
    micro_ledger = Counter(sealed_ledger)
    examples = []
    residual_examples = []

    for _key, entry in sorted(unique.items(), key=lambda kv: (kv[1]["forced_CLV"], kv[0])):
        target = r50g25b.canon(entry["forced_formula"])
        cover = r50g25b.exact_minimum_cover(target)
        minimum = int(cover["minimum"])
        if minimum < 3:
            continue

        family_unique += 1
        count = int(entry["occurrence_count"])
        family_weighted += count
        witness = entry["witness"]
        source_item = source_by_hash[witness["source_hash"]]
        source = r50g25b.canon(source_item["source"])
        c1 = tuple(int(x) for x in witness["first_clause"])
        c2 = tuple(int(x) for x in witness["second_clause"])
        lifted = [tuple(int(x) for x in clause) for clause in cover["clauses"]]
        lifted_source = r50g25b.canon(list(source) + [c1, c2] + lifted)

        dp = r47j.r45a.exact_dp_record(lifted_source, PIVOT)
        if dp is None:
            source_lift_fail += 1
            continue
        dp_replay = r47j.r45a.independent_dp_replay(lifted_source, dp)
        if not dp_replay.get("pass"):
            source_lift_fail += 1
            continue
        actual = r50g25b.canon(dp["transformed"])
        expected = r50g25b.canon(list(target) + lifted)
        normalized_expected = r50g25b.canon(r42.subsumption_minimize(expected))
        if actual != expected and actual != normalized_expected:
            raise AssertionError(("R50G25G_SOURCE_NORMAL_FORM_DRIFT", witness))

        truth = exact_semantic(r33, actual)
        exact_truth["SAT" if truth["sat"] else "UNSAT"] += 1

        sealed = r47j.normalize_to_certified_fixpoint(actual)
        micro = micro_normalize(actual, r50g23, r35b, r33, r47j)

        sealed_term = str(sealed.get("terminal"))
        micro_term = str(micro.get("terminal")) if micro.get("terminal") is not None else "RESIDUAL_FIXPOINT"
        sealed_terminal[sealed_term] += 1
        micro_terminal[micro_term] += 1
        terminal_pairs[(sealed_term, micro_term)] += 1
        sealed_round_hist[int(sealed.get("round_count", 0))] += 1
        sealed_restart_hist[int(sealed.get("restart_count", 0))] += 1
        micro_round_hist[int(micro.get("round_count", 0))] += 1
        micro_restart_hist[int(micro.get("restart_count", 0))] += 1

        sealed_rup_strengthenings = sum(int(row.get("RUP_history_count", 0)) for row in sealed.get("rounds", []))
        micro_rup_strengthenings = int(micro["ledger"]["RUP_successful_strengthenings"])
        micro_rup_strength_hist[micro_rup_strengthenings] += 1
        add_ledger(sealed_ledger, sealed.get("ledger", {}), rup_strengthenings=sealed_rup_strengthenings)
        add_ledger(micro_ledger, micro.get("ledger", {}), rup_strengthenings=micro_rup_strengthenings)

        sealed_sat = sealed.get("semantic_sat")
        micro_sat = micro.get("semantic_sat")
        if sealed_sat is None:
            raise AssertionError(("R50G25G_SEALED_NONTERMINAL_DRIFT", sealed_term, witness))
        if bool(sealed_sat) != bool(truth["sat"]):
            exact_sealed_mismatch += 1
            raise AssertionError(("R50G25G_SEALED_EXACT_SEMANTIC_MISMATCH", witness, sealed_sat, truth))

        if micro_sat is None:
            residual_unique += 1
            residual_weighted += count
            if len(residual_examples) < 20:
                residual_examples.append({
                    "state_hash": r50g23.r50g4.fhash(target),
                    "post_DP_hash": r42.formula_hash(actual),
                    "post_DP_CLV": list(r33.measure(actual)),
                    "occurrence_count": count,
                    "sealed_terminal": sealed_term,
                    "micro_final_CLV": micro["final_CLV"],
                    "micro_round_count": micro["round_count"],
                    "micro_restart_count": micro["restart_count"],
                    "micro_RUP_strengthenings": micro_rup_strengthenings,
                })
        else:
            micro_terminal_unique += 1
            micro_terminal_weighted += count
            if bool(micro_sat) != bool(truth["sat"]):
                exact_micro_mismatch += 1
                raise AssertionError(("R50G25G_MICRO_EXACT_SEMANTIC_MISMATCH", witness, micro_sat, truth))
            if bool(micro_sat) == bool(sealed_sat):
                solved_semantic_agreement_unique += 1
                solved_semantic_agreement_weighted += count
            if micro_sat is True and not micro["SAT_reconstruction"].get("pass"):
                micro_reconstruction_fail += 1
                raise AssertionError(("R50G25G_MICRO_RECONSTRUCTION_DRIFT", witness))

        if len(examples) < 20:
            examples.append({
                "state_hash": r50g23.r50g4.fhash(target),
                "post_DP_hash": r42.formula_hash(actual),
                "post_DP_CLV": list(r33.measure(actual)),
                "occurrence_count": count,
                "exact_sat": bool(truth["sat"]),
                "sealed_terminal": sealed_term,
                "sealed_rounds": int(sealed.get("round_count", 0)),
                "sealed_restarts": int(sealed.get("restart_count", 0)),
                "sealed_RUP_strengthenings": sealed_rup_strengthenings,
                "micro_terminal": micro_term,
                "micro_rounds": int(micro["round_count"]),
                "micro_restarts": int(micro["restart_count"]),
                "micro_RUP_strengthenings": micro_rup_strengthenings,
            })

    if family_unique != EXPECTED_GE3_UNIQUE:
        raise AssertionError(("R50G25G_FAMILY_UNIQUE_DRIFT", family_unique))
    if family_weighted != EXPECTED_GE3_WEIGHTED:
        raise AssertionError(("R50G25G_FAMILY_WEIGHTED_DRIFT", family_weighted))
    if source_lift_fail != 0:
        raise AssertionError(("R50G25G_SOURCE_LIFT_REPLAY_FAILURE", source_lift_fail))
    if exact_sealed_mismatch != 0 or exact_micro_mismatch != 0 or micro_reconstruction_fail != 0:
        raise AssertionError(("R50G25G_SEMANTIC_OR_RECONSTRUCTION_FAILURE", exact_sealed_mismatch, exact_micro_mismatch, micro_reconstruction_fail))
    if micro_terminal_unique + residual_unique != family_unique:
        raise AssertionError(("R50G25G_MICRO_PARTITION_DRIFT", micro_terminal_unique, residual_unique, family_unique))

    all_micro_terminal = residual_unique == 0
    next_gate = (
        "R50G25H_MICRO_RUP_RESTART_BROADER_COVERAGE_AND_POLYNOMIAL_LEDGER_AUDIT"
        if all_micro_terminal
        else "R50G25H_MICRO_RUP_RESTART_RESIDUAL_FIXPOINT_FORENSICS"
    )

    def counter_json(counter):
        return {str(k): int(v) for k, v in sorted(counter.items(), key=lambda kv: str(kv[0]))}

    pair_json = {
        f"{a} -> {b}": int(v)
        for (a, b), v in sorted(terminal_pairs.items(), key=lambda kv: (kv[0][0], kv[0][1]))
    }

    return {
        "gate": GATE,
        "parent_gate": parent["gate"],
        "family_unique_state_count": family_unique,
        "family_weighted_occurrence_count": family_weighted,
        "frozen_source_skeleton_count": len(source_by_hash),
        "source_lift_replay_failure_unique_count": source_lift_fail,
        "exact_truth_unique_partition": counter_json(exact_truth),
        "sealed_terminal_unique_partition": counter_json(sealed_terminal),
        "micro_terminal_unique_partition": counter_json(micro_terminal),
        "sealed_to_micro_terminal_pair_unique_partition": pair_json,
        "micro_terminal_unique_count": micro_terminal_unique,
        "micro_terminal_weighted_count": micro_terminal_weighted,
        "micro_residual_fixpoint_unique_count": residual_unique,
        "micro_residual_fixpoint_weighted_count": residual_weighted,
        "all_991_micro_schedule_terminal": all_micro_terminal,
        "solved_semantic_agreement_with_sealed_unique_count": solved_semantic_agreement_unique,
        "solved_semantic_agreement_with_sealed_weighted_count": solved_semantic_agreement_weighted,
        "exact_sealed_semantic_mismatch_count": exact_sealed_mismatch,
        "exact_micro_semantic_mismatch_count": exact_micro_mismatch,
        "micro_SAT_reconstruction_failure_count": micro_reconstruction_fail,
        "sealed_round_count_unique_histogram": counter_json(sealed_round_hist),
        "sealed_restart_count_unique_histogram": counter_json(sealed_restart_hist),
        "micro_round_count_unique_histogram": counter_json(micro_round_hist),
        "micro_restart_count_unique_histogram": counter_json(micro_restart_hist),
        "micro_RUP_successful_strengthenings_unique_histogram": counter_json(micro_rup_strength_hist),
        "aggregate_sealed_ledger": dict(sorted((k, int(v)) for k, v in sealed_ledger.items())),
        "aggregate_micro_ledger": dict(sorted((k, int(v)) for k, v in micro_ledger.items())),
        "examples": examples,
        "micro_residual_examples": residual_examples,
        "next_gate": next_gate,
        "interpretation_contract": {
            "family_is_exactly_the_frozen_991_ge3_source_lift_states": True,
            "exact_assignment_enumeration_is_validation_oracle_only": True,
            "micro_schedule_is_not_promoted_to_current_R47J": True,
            "terminal_coverage_on_frozen_family_is_not_universal_coverage": True,
            "aggregate_ledger_improvement_is_not_asymptotic_complexity_proof": True,
            "RUP_each_step_is_independently_conflict_replayed": True,
            "SAT_terminals_require_reconstruction_to_the_post_DP_input": True,
            "no_claim_outside_frozen_family": True,
        },
        "firewall": {
            "ALL_DIRECT5_V7_HUB_CYCLE_ELIMINATED": False,
            "U_MU": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
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
