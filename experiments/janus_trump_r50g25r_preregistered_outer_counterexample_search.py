from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from pathlib import Path

import janus_trump_r50g25g_micro_rup_restart_replay_source_lift_family as r50g25g
import janus_trump_r50g25p_take_live_reduction_door_696_no_go_replay as r50g25p

GATE = "JANUS_TRUMP_R50G25R_PREREGISTERED_OUTER_COUNTEREXAMPLE_SEARCH"
PARENT_Q_COMMIT = "600ee156f0fc45bec538ee13c9a1dbe7046955bb"
PREREG_COMMIT = "a50a2712a9671b464e7d1391c4c1e6bbb7a6d395"
FROZEN_CLASSES = (
    "CERTIFICATE_FAILURE",
    "RECONSTRUCTION_FAILURE",
    "PROGRESS_FAILURE",
    "RESIDUAL_FIXPOINT",
    "POLYNOMIAL_LEDGER_FAILURE",
    "SEMANTIC_MISMATCH",
)


def exact_truth_validation(r33, formula):
    formula = r33.canonical_formula(formula)
    vs = list(r33.variables(formula))
    if len(vs) > 12:
        return {"performed": False, "reason": "VARIABLE_BOUND_GT_12", "variable_count": len(vs)}
    model_count = 0
    for bits in itertools.product((False, True), repeat=len(vs)):
        a = dict(zip(vs, bits))
        if r33.eval_formula(formula, a):
            model_count += 1
    return {
        "performed": True,
        "validation_only_not_algorithmic_authority": True,
        "variable_count": len(vs),
        "assignment_space_checked": 2 ** len(vs),
        "sat": model_count > 0,
        "model_count": model_count,
    }


def independent_r33_history_audit(r33, initial, result):
    state = r33.canonical_formula(initial)
    failures = []
    for index, record in enumerate(result.get("history", [])):
        before = tuple(r33.measure(state))
        rule = str(record.get("rule"))
        transformed = None
        cert_ok = True
        reason = None

        if rule == "TAUTOLOGY_DELETION":
            clause = tuple(int(x) for x in record["clause"])
            cert_ok = clause in state and r33.is_tautology(clause)
            transformed = r33.canonical_formula(c for c in state if c != clause)
        elif rule == "UNIT_PROPAGATION_WITH_RECONSTRUCTION_TRACE":
            lit = int(record["literal"])
            cert_ok = (lit,) in state
            nf = []
            for c in state:
                if lit in c:
                    continue
                if -lit in c:
                    nf.append(tuple(x for x in c if x != -lit))
                else:
                    nf.append(c)
            transformed = r33.canonical_formula(nf)
        elif rule == "PURE_LITERAL_AUTARKY":
            lit = int(record["literal"])
            cert_ok = lit in r33.pure_literals(state)
            transformed = r33.canonical_formula(c for c in state if lit not in c)
        elif rule == "SUBSUMPTION":
            deleted = tuple(int(x) for x in record["deleted"])
            witness = tuple(int(x) for x in record["witness_subclause"])
            cert_ok = deleted in state and witness in state and set(witness) <= set(deleted)
            transformed = r33.canonical_formula(c for c in state if c != deleted)
        elif rule == "BLOCKED_CLAUSE_ELIMINATION":
            cert, transformed = r50g25p.bce_step_certificate(r33, state, record)
            cert_ok = bool(cert.get("pass"))
            reason = cert if not cert_ok else None
        elif rule == "BOUNDED_VARIABLE_ELIMINATION":
            cert, transformed = r50g25p.bve_step_certificate(r33, state, record)
            cert_ok = bool(cert.get("pass"))
            reason = cert if not cert_ok else None
        else:
            cert_ok = False
            reason = {"unknown_rule": rule}

        if transformed is None:
            cert_ok = False
        after = tuple(r33.measure(transformed)) if transformed is not None else before
        record_before = tuple(int(x) for x in record.get("measure_before", before))
        record_after = tuple(int(x) for x in record.get("measure_after", after))
        if record_before != before or record_after != after:
            cert_ok = False
            reason = {"measure_receipt_mismatch": {"expected_before": before, "expected_after": after, "record_before": record_before, "record_after": record_after}}
        if transformed is not None and not after < before:
            failures.append({"class": "PROGRESS_FAILURE", "step": index, "rule": rule, "before": list(before), "after": list(after)})
        if not cert_ok:
            failures.append({"class": "CERTIFICATE_FAILURE", "step": index, "rule": rule, "reason": reason})
            break
        state = transformed

    expected_final = r33.canonical_formula(result.get("final_formula", []))
    if state != expected_final:
        failures.append({"class": "CERTIFICATE_FAILURE", "reason": "R33_FINAL_REPLAY_MISMATCH"})
    return failures


def classify_micro_exception(exc: AssertionError):
    text = repr(exc)
    if "MICRO_RUP_CERT_FAIL" in text or "DECLARED_TERMINAL_VERIFY_FAIL" in text or "AFFINE_VERIFY_FAIL" in text:
        return "CERTIFICATE_FAILURE"
    if "MICRO_SAT_RECONSTRUCTION_FAIL" in text:
        return "RECONSTRUCTION_FAILURE"
    if "NOT_STRICT_DESCENT" in text or "RESTART_NOT_STRICT_DESCENT" in text:
        return "PROGRESS_FAILURE"
    if "HEIGHT_BOUND_EXHAUSTED" in text:
        return "POLYNOMIAL_LEDGER_FAILURE"
    return None


def polynomial_ledger_audit(r47j, r33, formula, micro):
    ledger = micro.get("ledger", {})
    required = (
        "R33_check_operation_upper_ledger",
        "R33_certificate_bytes",
        "RUP_checks",
        "RUP_UP_clause_scans",
        "RUP_UP_literal_inspections",
        "RUP_successful_strengthenings",
        "GF2_estimated_bit_ops",
        "restart_count",
    )
    if any(k not in ledger or not isinstance(ledger[k], int) or ledger[k] < 0 for k in required):
        return False, "MISSING_OR_NEGATIVE_INTEGER_LEDGER"
    height = int(r47j.restart_height_bound(r33.canonical_formula(formula)))
    rounds = int(micro.get("round_count", 0))
    restarts = int(micro.get("restart_count", 0))
    rup_success = int(ledger.get("RUP_successful_strengthenings", -1))
    if rounds > height + 1:
        return False, "ROUND_COUNT_EXCEEDS_FROZEN_HEIGHT_BOUND"
    if restarts != rup_success or restarts != int(ledger.get("restart_count", -1)):
        return False, "RESTART_RUP_LEDGER_MISMATCH"
    if restarts > height:
        return False, "RESTART_COUNT_EXCEEDS_FROZEN_HEIGHT_BOUND"
    return True, None


def frozen_outer_suite(r33):
    rows = []
    for n, seed_start, seed_count in ((12, 0, 16), (16, 1000, 16), (24, 2000, 8)):
        for seed in range(seed_start, seed_start + seed_count):
            rows.append({
                "family": "DETERMINISTIC_RANDOM_3CNF",
                "parameters": {"n": n, "ratio": 4.2, "seed": seed},
                "formula": r33.deterministic_random_3cnf(seed=seed, n=n, ratio=4.2),
            })
    for n_vertices in (8, 10, 12, 14):
        rows.append({
            "family": "PRISM_TSEITIN",
            "parameters": {"n_vertices": n_vertices},
            "formula": r33.prism_tseitin(n_vertices),
        })
    if len(rows) != 44:
        raise AssertionError(("R50G25R_PREREG_SUITE_COUNT_DRIFT", len(rows)))
    return rows


def run():
    _b, r50g23, r35b, r33, r47j = r50g25g._chain()
    suite = frozen_outer_suite(r33)
    falsifier_hist = Counter()
    family_hist = Counter()
    terminal_hist = Counter()
    cases = []
    unclassifiable_checker_failures = []

    for spec in suite:
        formula = r33.canonical_formula(spec["formula"])
        family_hist[spec["family"]] += 1
        clv = tuple(r33.measure(formula))
        formula_hash = r50g23.r50g4.fhash(formula)
        exact = exact_truth_validation(r33, formula)
        case_classes = set()
        evidence = []

        baseline = r33.simplify(formula)
        for failure in independent_r33_history_audit(r33, formula, baseline):
            cls = failure["class"]
            case_classes.add(cls)
            evidence.append(failure)

        micro = None
        try:
            micro = r50g25g.micro_normalize(formula, r50g23, r35b, r33, r47j)
        except AssertionError as exc:
            cls = classify_micro_exception(exc)
            if cls is None:
                unclassifiable_checker_failures.append({"formula_hash": formula_hash, "exception": repr(exc)})
                continue
            case_classes.add(cls)
            evidence.append({"class": cls, "source": "MICRO_EXCEPTION", "exception": repr(exc)})

        if micro is not None:
            term = str(micro.get("terminal")) if micro.get("terminal") is not None else "RESIDUAL_FIXPOINT"
            terminal_hist[term] += 1
            if micro.get("terminal") is None:
                case_classes.add("RESIDUAL_FIXPOINT")
                evidence.append({
                    "class": "RESIDUAL_FIXPOINT",
                    "final_CLV": micro.get("final_CLV"),
                    "round_count": micro.get("round_count"),
                    "restart_count": micro.get("restart_count"),
                    "last_round": micro.get("rounds", [])[-1] if micro.get("rounds") else None,
                })
            ledger_ok, ledger_reason = polynomial_ledger_audit(r47j, r33, formula, micro)
            if not ledger_ok:
                case_classes.add("POLYNOMIAL_LEDGER_FAILURE")
                evidence.append({"class": "POLYNOMIAL_LEDGER_FAILURE", "reason": ledger_reason, "ledger": micro.get("ledger")})
            reconstruction = micro.get("SAT_reconstruction", {})
            if reconstruction.get("applicable") and not reconstruction.get("pass"):
                case_classes.add("RECONSTRUCTION_FAILURE")
                evidence.append({"class": "RECONSTRUCTION_FAILURE", "source": "MICRO_RETURN"})
            if exact.get("performed") and micro.get("semantic_sat") is not None:
                if bool(exact["sat"]) != bool(micro["semantic_sat"]):
                    case_classes.add("SEMANTIC_MISMATCH")
                    evidence.append({"class": "SEMANTIC_MISMATCH", "exact_sat": exact["sat"], "micro_sat": micro["semantic_sat"]})

        for cls in case_classes:
            falsifier_hist[cls] += 1

        cases.append({
            "family": spec["family"],
            "parameters": spec["parameters"],
            "formula_hash": formula_hash,
            "CLV": list(clv),
            "variable_count": clv[2],
            "exact_truth_validation": exact,
            "baseline_R33_terminal": str(baseline.get("terminal")),
            "micro_terminal": (str(micro.get("terminal")) if micro is not None and micro.get("terminal") is not None else ("RESIDUAL_FIXPOINT" if micro is not None else None)),
            "micro_final_CLV": micro.get("final_CLV") if micro is not None else None,
            "micro_round_count": micro.get("round_count") if micro is not None else None,
            "micro_restart_count": micro.get("restart_count") if micro is not None else None,
            "micro_ledger": micro.get("ledger") if micro is not None else None,
            "falsifier_classes": sorted(case_classes),
            "evidence": evidence,
        })

    if unclassifiable_checker_failures:
        raise AssertionError(("R50G25R_UNCLASSIFIABLE_CHECKER_FAILURE", unclassifiable_checker_failures[:3]))
    if len(cases) != 44:
        raise AssertionError(("R50G25R_CASE_COUNT_DRIFT", len(cases)))

    falsifiers = [c for c in cases if c["falsifier_classes"]]
    falsifiers.sort(key=lambda c: (c["variable_count"], c["CLV"][0], c["CLV"][1], c["formula_hash"]))
    primary = falsifiers[0] if falsifiers else None

    if primary is None:
        verdict = "NO_Q_FALSIFIER_FOUND_IN_PREREGISTERED_FINITE_OUTER_SUITE"
        next_gate = "R50G25S_SECOND_OUTER_SUITE_OR_STRUCTURAL_COVERAGE_ARGUMENT"
    else:
        verdict = "OUTER_Q_FALSIFIER_FOUND__" + "+".join(primary["falsifier_classes"])
        next_gate = "R50G25S_MINIMIZE_AND_INDEPENDENTLY_REPLAY_PRIMARY_OUTER_FALSIFIER"

    return {
        "gate": GATE,
        "parent_Q_commit": PARENT_Q_COMMIT,
        "preregistration_commit": PREREG_COMMIT,
        "suite_contract": {
            "formula_count": 44,
            "family_partition": dict(sorted(family_hist.items())),
            "entire_frozen_suite_executed": True,
            "stop_at_first_falsifier": False,
            "truth_enumeration_variable_bound": 12,
            "truth_enumeration_validation_only": True,
        },
        "frozen_Q_falsifier_classes": list(FROZEN_CLASSES),
        "falsifier_case_count": len(falsifiers),
        "falsifier_class_histogram": dict(sorted(falsifier_hist.items())),
        "terminal_partition": dict(sorted(terminal_hist.items())),
        "primary_falsifier": primary,
        "all_falsifiers": falsifiers,
        "all_cases": cases,
        "verdict": verdict,
        "next_gate": next_gate,
        "interpretation_contract": {
            "scientific_falsifier_is_successful_experiment_execution": True,
            "finite_outer_search_is_not_universal_coverage": True,
            "no_falsifier_in_finite_suite_is_not_proof": True,
            "outer_falsifier_of_candidate_schedule_is_not_P_vs_NP_resolution": True,
            "polynomial_normalization_schedule_is_not_SAT_completeness": True,
        },
        "firewall": {
            "P_VS_NP": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
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
