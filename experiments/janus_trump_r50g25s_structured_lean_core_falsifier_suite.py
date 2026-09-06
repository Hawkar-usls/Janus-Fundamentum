from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from pathlib import Path

import janus_trump_r50g25r_preregistered_outer_counterexample_search as r50g25r

GATE = "JANUS_TRUMP_R50G25S_STRUCTURED_LEAN_CORE_FALSIFIER_SUITE"
PARENT_R_RUN = 34039991475
PREREG_COMMIT = "d638447b873a08a1eef5c32ad1e46c49ab16ae83"


def nae_formula(r33, edges):
    clauses = []
    for edge in edges:
        e = tuple(sorted(int(x) for x in edge))
        if len(set(e)) != 3:
            raise AssertionError(("R50G25S_NON_3SET_EDGE", e))
        clauses.append(e)
        clauses.append(tuple(-x for x in e))
    return r33.canonical_formula(clauses)


def fano_edges():
    return [
        (1, 2, 3), (1, 4, 5), (1, 6, 7),
        (2, 4, 6), (2, 5, 7), (3, 4, 7), (3, 5, 6),
    ]


def complete_3uniform_edges(n):
    return list(itertools.combinations(range(1, n + 1), 3))


def van_der_waerden_3ap_edges(n):
    edges = []
    for a in range(1, n + 1):
        d = 1
        while a + 2 * d <= n:
            edges.append((a, a + d, a + 2 * d))
            d += 1
    return edges


def suite(r33):
    rows = [{"family": "FANO_NAE", "parameter": {"order": 7}, "formula": nae_formula(r33, fano_edges())}]
    for n in (4, 5, 6):
        rows.append({"family": "COMPLETE_3UNIFORM_NAE", "parameter": {"n": n}, "formula": nae_formula(r33, complete_3uniform_edges(n))})
    for n in (7, 8, 9, 10, 11):
        rows.append({"family": "VAN_DER_WAERDEN_3AP_NAE", "parameter": {"n": n}, "formula": nae_formula(r33, van_der_waerden_3ap_edges(n))})
    if len(rows) != 9:
        raise AssertionError(("R50G25S_SUITE_COUNT_DRIFT", len(rows)))
    return rows


def run():
    _b, r50g23, r35b, r33, r47j = r50g25r.r50g25g._chain()
    rows = suite(r33)
    family_hist = Counter()
    falsifier_hist = Counter()
    terminal_hist = Counter()
    cases = []
    unclassifiable = []

    for spec in rows:
        formula = r33.canonical_formula(spec["formula"])
        family_hist[spec["family"]] += 1
        clv = tuple(r33.measure(formula))
        formula_hash = r50g23.r50g4.fhash(formula)
        exact = r50g25r.exact_truth_validation(r33, formula)
        if not exact.get("performed"):
            raise AssertionError(("R50G25S_EXACT_VALIDATION_BOUND_DRIFT", spec, clv))

        baseline = r33.simplify(formula)
        classes = set()
        evidence = []
        for failure in r50g25r.independent_r33_history_audit(r33, formula, baseline):
            classes.add(failure["class"])
            evidence.append(failure)

        micro = None
        try:
            micro = r50g25r.r50g25g.micro_normalize(formula, r50g23, r35b, r33, r47j)
        except AssertionError as exc:
            cls = r50g25r.classify_micro_exception(exc)
            if cls is None:
                unclassifiable.append({"formula_hash": formula_hash, "exception": repr(exc)})
                continue
            classes.add(cls)
            evidence.append({"class": cls, "source": "MICRO_EXCEPTION", "exception": repr(exc)})

        if micro is not None:
            term = str(micro.get("terminal")) if micro.get("terminal") is not None else "RESIDUAL_FIXPOINT"
            terminal_hist[term] += 1
            if micro.get("terminal") is None:
                classes.add("RESIDUAL_FIXPOINT")
                evidence.append({
                    "class": "RESIDUAL_FIXPOINT",
                    "final_CLV": micro.get("final_CLV"),
                    "round_count": micro.get("round_count"),
                    "restart_count": micro.get("restart_count"),
                    "last_round": micro.get("rounds", [])[-1] if micro.get("rounds") else None,
                })
            ledger_ok, ledger_reason = r50g25r.polynomial_ledger_audit(r47j, r33, formula, micro)
            if not ledger_ok:
                classes.add("POLYNOMIAL_LEDGER_FAILURE")
                evidence.append({"class": "POLYNOMIAL_LEDGER_FAILURE", "reason": ledger_reason})
            rec = micro.get("SAT_reconstruction", {})
            if rec.get("applicable") and not rec.get("pass"):
                classes.add("RECONSTRUCTION_FAILURE")
                evidence.append({"class": "RECONSTRUCTION_FAILURE", "source": "MICRO_RETURN"})
            if micro.get("semantic_sat") is not None and bool(micro["semantic_sat"]) != bool(exact["sat"]):
                classes.add("SEMANTIC_MISMATCH")
                evidence.append({"class": "SEMANTIC_MISMATCH", "exact_sat": exact["sat"], "micro_sat": micro["semantic_sat"]})

        for cls in classes:
            falsifier_hist[cls] += 1
        cases.append({
            "family": spec["family"],
            "parameter": spec["parameter"],
            "formula_hash": formula_hash,
            "CLV": list(clv),
            "formula": [list(c) for c in formula],
            "exact_truth_validation": exact,
            "baseline_R33_terminal": str(baseline.get("terminal")),
            "baseline_R33_rule_applications": int(baseline.get("total_rule_applications", 0)),
            "micro_terminal": (str(micro.get("terminal")) if micro is not None and micro.get("terminal") is not None else ("RESIDUAL_FIXPOINT" if micro is not None else None)),
            "micro_final_CLV": micro.get("final_CLV") if micro is not None else None,
            "micro_round_count": micro.get("round_count") if micro is not None else None,
            "micro_restart_count": micro.get("restart_count") if micro is not None else None,
            "micro_RUP_successful_strengthenings": (micro.get("ledger", {}).get("RUP_successful_strengthenings") if micro is not None else None),
            "micro_ledger": micro.get("ledger") if micro is not None else None,
            "falsifier_classes": sorted(classes),
            "evidence": evidence,
        })

    if unclassifiable:
        raise AssertionError(("R50G25S_UNCLASSIFIABLE_CHECKER_FAILURE", unclassifiable))
    if len(cases) != 9:
        raise AssertionError(("R50G25S_CASE_COUNT_DRIFT", len(cases)))

    falsifiers = [c for c in cases if c["falsifier_classes"]]
    falsifiers.sort(key=lambda c: (c["CLV"][2], c["CLV"][0], c["CLV"][1], c["formula_hash"]))
    primary = falsifiers[0] if falsifiers else None
    if primary is None:
        verdict = "NO_Q_FALSIFIER_FOUND_IN_STRUCTURED_LEAN_CORE_SUITE"
        next_gate = "R50G25T_CONSTRUCT_EXPLICIT_RUP_LEAN_STALLED_CORE_OR_PROVE_LOCAL_COVERAGE"
    else:
        verdict = "OUTER_Q_FALSIFIER_FOUND__" + "+".join(primary["falsifier_classes"])
        next_gate = "R50G25T_MINIMIZE_AND_INDEPENDENTLY_REPLAY_STRUCTURED_OUTER_FALSIFIER"

    return {
        "gate": GATE,
        "parent_R_run": PARENT_R_RUN,
        "preregistration_commit": PREREG_COMMIT,
        "suite_contract": {
            "formula_count": 9,
            "family_partition": dict(sorted(family_hist.items())),
            "entire_suite_executed": True,
            "all_cases_exact_truth_validated": True,
            "truth_validation_only_not_algorithmic_authority": True,
        },
        "frozen_Q_falsifier_classes": list(r50g25r.FROZEN_CLASSES),
        "falsifier_case_count": len(falsifiers),
        "falsifier_class_histogram": dict(sorted(falsifier_hist.items())),
        "terminal_partition": dict(sorted(terminal_hist.items())),
        "primary_falsifier": primary,
        "all_falsifiers": falsifiers,
        "all_cases": cases,
        "verdict": verdict,
        "next_gate": next_gate,
        "interpretation_contract": {
            "structured_suite_targets_lean_nonaffine_symmetric_3CNF": True,
            "falsifier_of_micro_schedule_is_not_P_vs_NP_resolution": True,
            "no_falsifier_in_finite_suite_is_not_proof": True,
            "finite_suite_is_not_universal_coverage": True,
        },
        "firewall": {"P_VS_NP": "OPEN", "SAT_IN_P": "NOT_PROVED", "TRUMP_finished": False},
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
