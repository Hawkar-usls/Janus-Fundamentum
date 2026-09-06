from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import janus_trump_r50g25s_structured_lean_core_falsifier_suite as r50g25s

GATE = "JANUS_TRUMP_R50G25T_FANO_RESIDUAL_MINIMIZATION_AND_INDEPENDENT_REPLAY"
PARENT_S_RUN = 34040310784
PREREG_COMMIT = "84f2a841bef4899a1a1177325f68a78df6c55d3c"
EXPECTED_HASH = "466163011411ccd10520539fb80f0bec7a9de934400961cfa6a25f1c58c38a00"
EXPECTED_CLV = (14, 42, 7)


def lit_key(lit: int):
    return (abs(int(lit)), 0 if int(lit) > 0 else 1)


def exact_models(r33, formula, universe=None):
    formula = r33.canonical_formula(formula)
    vs = list(universe if universe is not None else r33.variables(formula))
    models = []
    for bits in itertools.product((False, True), repeat=len(vs)):
        a = dict(zip(vs, bits))
        if r33.eval_formula(formula, a):
            models.append({str(k): bool(v) for k, v in sorted(a.items())})
    return models


def independent_up_conflict(formula, assumptions):
    assignment = {}
    for lit in assumptions:
        lit = int(lit)
        v, val = abs(lit), lit > 0
        if v in assignment and assignment[v] != val:
            return True, {"kind": "ASSUMPTION_CONTRADICTION", "assignment": assignment}
        assignment[v] = val

    while True:
        changed = False
        for clause in formula:
            sat = False
            unassigned = []
            for lit in clause:
                v = abs(lit)
                if v in assignment:
                    if assignment[v] == (lit > 0):
                        sat = True
                        break
                else:
                    unassigned.append(lit)
            if sat:
                continue
            if not unassigned:
                return True, {"kind": "EMPTY_RESIDUAL_CLAUSE", "clause": list(clause), "assignment": dict(sorted(assignment.items()))}
            if len(unassigned) == 1:
                lit = int(unassigned[0])
                v, val = abs(lit), lit > 0
                if v in assignment:
                    if assignment[v] != val:
                        return True, {"kind": "UNIT_CONTRADICTION", "clause": list(clause), "assignment": dict(sorted(assignment.items()))}
                else:
                    assignment[v] = val
                    changed = True
        if not changed:
            return False, {"kind": "FIXPOINT", "assignment": dict(sorted(assignment.items()))}


def independent_rup_scan(formula):
    rows = []
    conflicts = 0
    for clause in formula:
        for removed in sorted(clause, key=lit_key):
            strengthened = tuple(l for l in clause if l != removed)
            assumptions = tuple(-l for l in sorted(strengthened, key=lit_key))
            conflict, receipt = independent_up_conflict(formula, assumptions)
            conflicts += int(conflict)
            rows.append({
                "source_clause": list(clause),
                "removed_literal": int(removed),
                "strengthened_clause": list(strengthened),
                "assumptions": list(assumptions),
                "up_conflict": bool(conflict),
                "receipt": receipt,
            })
    return {"candidate_count": len(rows), "conflict_count": conflicts, "candidates": rows}


def independent_r33_applicability_audit(r33, formula):
    formula = r33.canonical_formula(formula)
    sets = [set(c) for c in formula]
    tautologies = [list(c) for c in formula if any(-l in set(c) for l in c)]
    units = [list(c) for c in formula if len(c) == 1]

    polarity = {}
    for c in formula:
        for l in c:
            polarity.setdefault(abs(l), set()).add(l > 0)
    pure_literals = []
    for v, signs in sorted(polarity.items()):
        if len(signs) == 1:
            pure_literals.append(v if True in signs else -v)

    subsumption_pairs = []
    for i, a in enumerate(sets):
        for j, b in enumerate(sets):
            if i != j and a <= b:
                subsumption_pairs.append({"small_index": i, "large_index": j, "small": list(formula[i]), "large": list(formula[j])})

    blocked = []
    nonblocked_witnesses = []
    for i, clause in enumerate(formula):
        cset = set(clause)
        for lit in clause:
            opposite = [other for other in formula if -lit in other]
            non_taut_witness = None
            for other in opposite:
                resolvent = (cset - {lit}) | (set(other) - {-lit})
                taut = any(-x in resolvent for x in resolvent)
                if not taut:
                    non_taut_witness = {"opposite_parent": list(other), "resolvent": sorted(resolvent, key=lit_key)}
                    break
            if non_taut_witness is None:
                blocked.append({"clause_index": i, "clause": list(clause), "blocking_literal": int(lit), "opposite_parent_count": len(opposite)})
            else:
                nonblocked_witnesses.append({"clause_index": i, "clause": list(clause), "literal": int(lit), **non_taut_witness})

    current = tuple(r33.measure(formula))
    bve_rows = []
    qualifying_bve = []
    for v in r33.variables(formula):
        pos = [c for c in formula if v in c]
        neg = [c for c in formula if -v in c]
        resolvents = []
        for p in pos:
            for n in neg:
                r = (set(p) - {v}) | (set(n) - {-v})
                if any(-l in r for l in r):
                    continue
                resolvents.append(r33.canonical_clause(r))
        resolvents = tuple(sorted(set(resolvents)))
        removed = set(pos + neg)
        transformed = r33.canonical_formula([c for c in formula if c not in removed] + list(resolvents))
        qualifies = bool(pos and neg and len(resolvents) <= len(removed) and tuple(r33.measure(transformed)) < current)
        row = {
            "var": int(v),
            "positive_parent_count": len(pos),
            "negative_parent_count": len(neg),
            "resolvent_count": len(resolvents),
            "removed_clause_count": len(removed),
            "transformed_CLV": list(r33.measure(transformed)),
            "qualifies_frozen_BVE": qualifies,
        }
        bve_rows.append(row)
        if qualifies:
            qualifying_bve.append(row)

    is_2cnf = all(len(c) <= 2 for c in formula)
    is_horn = all(sum(1 for l in c if l > 0) <= 1 for c in formula)
    pass_no_rule = not tautologies and not units and not pure_literals and not subsumption_pairs and not blocked and not qualifying_bve
    return {
        "pass_no_R33_reduction_rule_applies": bool(pass_no_rule),
        "tautologies": tautologies,
        "units": units,
        "pure_literals": pure_literals,
        "subsumption_pairs": subsumption_pairs,
        "blocked_candidates": blocked,
        "nonblocked_local_witness_count": len(nonblocked_witnesses),
        "nonblocked_local_witnesses": nonblocked_witnesses,
        "BVE_rows": bve_rows,
        "qualifying_BVE_candidates": qualifying_bve,
        "is_2cnf": bool(is_2cnf),
        "is_horn": bool(is_horn),
    }


def run():
    _b, r50g23, r35b, r33, r47j = r50g25s.r50g25r.r50g25g._chain()
    r34 = r50g23.r34

    formula = r50g25s.nae_formula(r33, r50g25s.fano_edges())
    formula_hash = r50g23.r50g4.fhash(formula)
    clv = tuple(r33.measure(formula))
    if formula_hash != EXPECTED_HASH or clv != EXPECTED_CLV:
        raise AssertionError(("R50G25T_TARGET_RECONSTRUCTION_DRIFT", formula_hash, clv))

    baseline = r33.simplify(formula)
    if baseline["terminal"] != "STALLED_STACK_LEAN_CORE" or baseline["total_rule_applications"] != 0:
        raise AssertionError(("R50G25T_BASELINE_DRIFT", baseline["terminal"], baseline["total_rule_applications"]))

    r33_audit = independent_r33_applicability_audit(r33, formula)
    if not r33_audit["pass_no_R33_reduction_rule_applies"]:
        raise AssertionError(("R50G25T_INDEPENDENT_R33_AUDIT_FAIL", r33_audit))

    affine = r34.recognize_complete_affine_cnf(formula)
    if affine["recognized"]:
        raise AssertionError(("R50G25T_AFFINE_RECOGNIZER_DRIFT", affine))

    independent_rup = independent_rup_scan(formula)
    if independent_rup["candidate_count"] != 42 or independent_rup["conflict_count"] != 0:
        raise AssertionError(("R50G25T_INDEPENDENT_RUP_SCAN_DRIFT", independent_rup["candidate_count"], independent_rup["conflict_count"]))
    frozen_proposal, frozen_ledger = r35b.first_rup_strengthening(formula)
    if frozen_proposal is not None or int(frozen_ledger["rup_checks"]) != 42:
        raise AssertionError(("R50G25T_FROZEN_RUP_COMPARISON_DRIFT", frozen_proposal, frozen_ledger))

    universe = list(range(1, 8))
    original_models = exact_models(r33, formula, universe)
    if original_models:
        raise AssertionError(("R50G25T_EXACT_UNSAT_VALIDATION_FAIL", original_models[:1]))

    deletions = []
    all_single_deletions_sat = True
    for i, clause in enumerate(formula):
        weakened = r33.canonical_formula(c for j, c in enumerate(formula) if j != i)
        models = exact_models(r33, weakened, universe)
        sat = bool(models)
        all_single_deletions_sat = all_single_deletions_sat and sat
        deletions.append({
            "removed_index": i,
            "removed_clause": list(clause),
            "weakened_CLV": list(r33.measure(weakened)),
            "sat": sat,
            "first_model": models[0] if models else None,
            "model_count": len(models),
        })
    if not all_single_deletions_sat:
        raise AssertionError(("R50G25T_SINGLE_DELETION_MINIMALITY_FAIL", [x for x in deletions if not x["sat"]]))

    micro = r50g25s.r50g25r.r50g25g.micro_normalize(formula, r50g23, r35b, r33, r47j)
    if micro["terminal"] is not None:
        raise AssertionError(("R50G25T_MICRO_NO_LONGER_RESIDUAL", micro["terminal"]))
    if micro["final_CLV"] != [14, 42, 7] or micro["ledger"]["RUP_successful_strengthenings"] != 0 or micro["restart_count"] != 0:
        raise AssertionError(("R50G25T_MICRO_RESIDUAL_LEDGER_DRIFT", micro))

    return {
        "gate": GATE,
        "parent_S_run": PARENT_S_RUN,
        "preregistration_commit": PREREG_COMMIT,
        "target": {
            "family": "FANO_NAE",
            "formula_hash": formula_hash,
            "CLV": list(clv),
            "formula": [list(c) for c in formula],
        },
        "independent_R33_applicability_audit": r33_audit,
        "frozen_R33_comparison": {
            "terminal": baseline["terminal"],
            "rule_applications": baseline["total_rule_applications"],
        },
        "affine_recognizer": {
            "recognized": bool(affine["recognized"]),
            "wording_firewall": "AFFINE_RECOGNIZER_FALSE_NEQ_MATHEMATICAL_NONAFFINITY",
        },
        "independent_single_literal_RUP_audit": independent_rup,
        "frozen_RUP_comparison": {
            "proposal_is_none": frozen_proposal is None,
            "rup_checks": int(frozen_ledger["rup_checks"]),
            "up_clause_scans": int(frozen_ledger["up_clause_scans"]),
            "up_literal_inspections": int(frozen_ledger["up_literal_inspections"]),
        },
        "exact_truth_validation": {
            "assignment_space_checked": 128,
            "model_count": 0,
            "sat": False,
            "validation_only_not_algorithmic_authority": True,
        },
        "clause_deletion_minimality": {
            "all_14_single_clause_deletions_sat": bool(all_single_deletions_sat),
            "single_deletion_count": len(deletions),
            "single_deletions": deletions,
            "proper_subformula_sat_conclusion_by_monotonicity": bool(all_single_deletions_sat),
            "claim_scope": "CLAUSE_DELETION_MINIMAL_UNSAT_WITHIN_THIS_14_CLAUSE_FORMULA",
            "global_minimum_3CNF_claimed": False,
        },
        "micro_replay": {
            "terminal": "RESIDUAL_FIXPOINT" if micro["terminal"] is None else micro["terminal"],
            "final_CLV": micro["final_CLV"],
            "round_count": micro["round_count"],
            "restart_count": micro["restart_count"],
            "ledger": micro["ledger"],
            "last_round": micro["rounds"][-1] if micro["rounds"] else None,
        },
        "verdict": "FANO_RESIDUAL_FIXPOINT_INDEPENDENTLY_REPLAYED_AND_CLAUSE_DELETION_MINIMAL_UNSAT_VALIDATED",
        "next_gate": "R50G25U_ADD_CERTIFIED_BRANCHING_OR_STRONGER_INFERENCE_TO_CROSS_FANO_RESIDUAL",
        "interpretation_contract": {
            "residual_fixpoint_is_counterexample_to_current_micro_schedule_completeness": True,
            "residual_fixpoint_is_not_UNSAT_proof": True,
            "finite_truth_table_establishes_this_witness_UNSAT_but_is_validation_only": True,
            "clause_deletion_minimality_is_not_global_3CNF_minimality": True,
            "affine_recognizer_false_is_not_mathematical_nonaffinity": True,
            "counterexample_to_micro_schedule_is_not_P_vs_NP_resolution": True,
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
