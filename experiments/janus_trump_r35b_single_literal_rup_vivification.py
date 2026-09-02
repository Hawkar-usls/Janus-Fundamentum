from __future__ import annotations

import argparse
import itertools
import json
import os
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r35_nonaffine_core_freeze_structure_intake as r35

Clause = Tuple[int, ...]
Formula = Tuple[Clause, ...]


def lit_key(lit: int) -> Tuple[int, int]:
    return (abs(lit), 0 if lit > 0 else 1)


def formula_measure(formula: Formula) -> Tuple[int, int, int]:
    return (sum(len(c) for c in formula), len(formula), len(r33.variables(formula)))


def simplify_under_assignment(formula: Formula, assignment: Dict[int, bool]) -> Tuple[Optional[Formula], Optional[Clause]]:
    residual: List[Clause] = []
    for clause in formula:
        sat = False
        left: List[int] = []
        for lit in clause:
            v = abs(lit)
            if v in assignment:
                if assignment[v] == (lit > 0):
                    sat = True
                    break
            else:
                left.append(lit)
        if sat:
            continue
        if not left:
            return None, clause
        residual.append(tuple(left))
    return r33.canonical_formula(residual), None


def candidate_unit_propagation_trace(formula: Formula, assumptions: Iterable[int]) -> dict:
    """Deterministic full-scan UP used by the R35B candidate.

    This is deliberately simple and fully metered.  It is not a SAT solver: it
    only applies assumptions and forced unit assignments until fixpoint/conflict.
    """
    assignment: Dict[int, bool] = {}
    trail: List[dict] = []
    clause_scans = 0
    literal_inspections = 0

    for lit in assumptions:
        v, val = abs(int(lit)), int(lit) > 0
        if v in assignment and assignment[v] != val:
            return {
                "conflict": True,
                "trail": trail,
                "conflict_kind": "ASSUMPTION_CONTRADICTION",
                "conflict_clause": None,
                "clause_scans": clause_scans,
                "literal_inspections": literal_inspections,
            }
        if v not in assignment:
            assignment[v] = val
            trail.append({"literal": int(lit), "reason": "ASSUMPTION"})

    while True:
        changed = False
        for clause in formula:
            clause_scans += 1
            sat = False
            unassigned: List[int] = []
            for lit in clause:
                literal_inspections += 1
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
                return {
                    "conflict": True,
                    "trail": trail,
                    "conflict_kind": "EMPTY_RESIDUAL_CLAUSE",
                    "conflict_clause": list(clause),
                    "clause_scans": clause_scans,
                    "literal_inspections": literal_inspections,
                }
            if len(unassigned) == 1:
                lit = unassigned[0]
                v, val = abs(lit), lit > 0
                if v in assignment:
                    if assignment[v] != val:
                        return {
                            "conflict": True,
                            "trail": trail,
                            "conflict_kind": "UNIT_ASSIGNMENT_CONTRADICTION",
                            "conflict_clause": list(clause),
                            "clause_scans": clause_scans,
                            "literal_inspections": literal_inspections,
                        }
                else:
                    assignment[v] = val
                    trail.append({"literal": lit, "reason": list(clause)})
                    changed = True
        if not changed:
            return {
                "conflict": False,
                "trail": trail,
                "conflict_kind": None,
                "conflict_clause": None,
                "clause_scans": clause_scans,
                "literal_inspections": literal_inspections,
                "assignment_count": len(assignment),
            }


def independent_up_conflict_checker(formula: Formula, assumptions: Iterable[int]) -> bool:
    """Independent replay checker: a separate residual-formula implementation."""
    assignment: Dict[int, bool] = {}
    for lit in assumptions:
        v, val = abs(int(lit)), int(lit) > 0
        if v in assignment and assignment[v] != val:
            return True
        assignment[v] = val

    while True:
        residual, conflict_clause = simplify_under_assignment(formula, assignment)
        if conflict_clause is not None:
            return True
        assert residual is not None
        units = sorted((c[0] for c in residual if len(c) == 1), key=lit_key)
        new = False
        for lit in units:
            v, val = abs(lit), lit > 0
            if v in assignment:
                if assignment[v] != val:
                    return True
            else:
                assignment[v] = val
                new = True
        if not new:
            return False


def replace_clause_with_subclause(formula: Formula, source: Clause, strengthened: Clause) -> Formula:
    removed = False
    out: List[Clause] = []
    for clause in formula:
        if not removed and clause == source:
            out.append(strengthened)
            removed = True
        else:
            out.append(clause)
    if not removed:
        raise AssertionError("source clause missing from current formula")
    return r33.canonical_formula(out)


def first_rup_strengthening(formula: Formula) -> Tuple[Optional[dict], dict]:
    checks = 0
    clause_scans = 0
    literal_inspections = 0
    for clause in formula:
        if not clause:
            continue
        for removed_literal in sorted(clause, key=lit_key):
            strengthened = tuple(l for l in clause if l != removed_literal)
            assumptions = tuple(-l for l in sorted(strengthened, key=lit_key))
            receipt = candidate_unit_propagation_trace(formula, assumptions)
            checks += 1
            clause_scans += receipt["clause_scans"]
            literal_inspections += receipt["literal_inspections"]
            if receipt["conflict"]:
                return {
                    "source_clause": clause,
                    "removed_literal": removed_literal,
                    "strengthened_clause": strengthened,
                    "assumptions": assumptions,
                    "up_receipt": receipt,
                }, {
                    "rup_checks": checks,
                    "up_clause_scans": clause_scans,
                    "up_literal_inspections": literal_inspections,
                }
    return None, {
        "rup_checks": checks,
        "up_clause_scans": clause_scans,
        "up_literal_inspections": literal_inspections,
    }


def run_candidate(initial_formula: Formula) -> dict:
    formula = r33.canonical_formula(initial_formula)
    initial_measure = formula_measure(formula)
    max_successes = initial_measure[0]
    history: List[dict] = []
    ledger = {"rup_checks": 0, "up_clause_scans": 0, "up_literal_inspections": 0}

    initial_up = candidate_unit_propagation_trace(formula, ())
    ledger["up_clause_scans"] += initial_up["clause_scans"]
    ledger["up_literal_inspections"] += initial_up["literal_inspections"]
    if initial_up["conflict"]:
        return {
            "status": "UNSAT_BY_UNIT_PROPAGATION",
            "initial_measure": list(initial_measure),
            "final_measure": list(formula_measure(formula)),
            "history": history,
            "final_up_receipt": initial_up,
            "ledger": ledger,
            "successful_strengthenings": 0,
            "final_formula": [list(c) for c in formula],
        }

    for step in range(max_successes + 1):
        if step == max_successes and len(history) == max_successes:
            raise AssertionError("successful-strengthening bound exhausted without terminal check")

        proposal, scan_ledger = first_rup_strengthening(formula)
        for key in ledger:
            ledger[key] += scan_ledger.get(key, 0)

        if proposal is None:
            final_up = candidate_unit_propagation_trace(formula, ())
            ledger["up_clause_scans"] += final_up["clause_scans"]
            ledger["up_literal_inspections"] += final_up["literal_inspections"]
            return {
                "status": "UNSAT_BY_UNIT_PROPAGATION" if final_up["conflict"] else "STALLED_RUP_CORE",
                "initial_measure": list(initial_measure),
                "final_measure": list(formula_measure(formula)),
                "history": history,
                "final_up_receipt": final_up,
                "ledger": ledger,
                "successful_strengthenings": len(history),
                "final_formula": [list(c) for c in formula],
            }

        source = proposal["source_clause"]
        strengthened = proposal["strengthened_clause"]
        before_hash = r35.canonical_json_sha256([list(c) for c in formula])
        before_measure = formula_measure(formula)
        updated = replace_clause_with_subclause(formula, source, strengthened)
        after_measure = formula_measure(updated)
        if not after_measure < before_measure:
            raise AssertionError(("RUP strengthening failed frozen progress measure", before_measure, after_measure))
        after_hash = r35.canonical_json_sha256([list(c) for c in updated])
        history.append({
            "step": len(history) + 1,
            "formula_hash_before": before_hash,
            "source_clause": list(source),
            "removed_literal": proposal["removed_literal"],
            "strengthened_clause": list(strengthened),
            "assumptions": list(proposal["assumptions"]),
            "up_receipt": proposal["up_receipt"],
            "measure_before": list(before_measure),
            "measure_after": list(after_measure),
            "formula_hash_after": after_hash,
        })
        formula = updated

        final_up = candidate_unit_propagation_trace(formula, ())
        ledger["up_clause_scans"] += final_up["clause_scans"]
        ledger["up_literal_inspections"] += final_up["literal_inspections"]
        if final_up["conflict"]:
            return {
                "status": "UNSAT_BY_UNIT_PROPAGATION",
                "initial_measure": list(initial_measure),
                "final_measure": list(formula_measure(formula)),
                "history": history,
                "final_up_receipt": final_up,
                "ledger": ledger,
                "successful_strengthenings": len(history),
                "final_formula": [list(c) for c in formula],
            }

    raise AssertionError("unreachable candidate loop exit")


def independent_certificate_replay(initial_formula: Formula, candidate: dict) -> dict:
    formula = r33.canonical_formula(initial_formula)
    checked = 0
    for record in candidate["history"]:
        expected_before = r35.canonical_json_sha256([list(c) for c in formula])
        if expected_before != record["formula_hash_before"]:
            return {"pass": False, "reason": "FORMULA_HASH_BEFORE_MISMATCH", "checked_steps": checked}
        source = tuple(record["source_clause"])
        strengthened = tuple(record["strengthened_clause"])
        removed = int(record["removed_literal"])
        if source not in formula or removed not in source:
            return {"pass": False, "reason": "SOURCE_OR_REMOVED_LITERAL_INVALID", "checked_steps": checked}
        if tuple(l for l in source if l != removed) != strengthened:
            return {"pass": False, "reason": "NOT_SINGLE_LITERAL_STRENGTHENING", "checked_steps": checked}
        assumptions = tuple(-l for l in sorted(strengthened, key=lit_key))
        if assumptions != tuple(record["assumptions"]):
            return {"pass": False, "reason": "ASSUMPTION_MISMATCH", "checked_steps": checked}
        if not independent_up_conflict_checker(formula, assumptions):
            return {"pass": False, "reason": "RUP_CONFLICT_NOT_REPRODUCED", "checked_steps": checked}
        formula = replace_clause_with_subclause(formula, source, strengthened)
        expected_after = r35.canonical_json_sha256([list(c) for c in formula])
        if expected_after != record["formula_hash_after"]:
            return {"pass": False, "reason": "FORMULA_HASH_AFTER_MISMATCH", "checked_steps": checked}
        checked += 1

    final_conflict = independent_up_conflict_checker(formula, ())
    status_ok = (candidate["status"] == "UNSAT_BY_UNIT_PROPAGATION") == final_conflict
    final_formula_ok = [list(c) for c in formula] == candidate["final_formula"]
    return {
        "pass": status_ok and final_formula_ok,
        "checked_steps": checked,
        "final_conflict": final_conflict,
        "status_consistent": status_ok,
        "final_formula_consistent": final_formula_ok,
        "final_formula_hash": r35.canonical_json_sha256([list(c) for c in formula]),
    }


def model_set_small(formula: Formula) -> List[Tuple[Tuple[int, bool], ...]]:
    vs = r33.variables(formula)
    models = []
    for bits in itertools.product((False, True), repeat=len(vs)):
        assignment = dict(zip(vs, bits))
        if r33.eval_formula(formula, assignment):
            models.append(tuple(sorted(assignment.items())))
    return models


def small_semantic_controls() -> dict:
    positive = r33.canonical_formula([(1, 2), (-1, 2), (1, -2)])
    negative = r33.canonical_formula([(1, 2, 3), (-1, -2, -3)])
    out = {}
    for name, formula in (("RUP_POSITIVE_SMALL", positive), ("RUP_NEGATIVE_SMALL", negative)):
        before_models = model_set_small(formula)
        candidate = run_candidate(formula)
        replay = independent_certificate_replay(formula, candidate)
        final = r33.canonical_formula(candidate["final_formula"])
        after_models = model_set_small(final)
        out[name] = {
            "pass": replay["pass"] and before_models == after_models,
            "candidate_status": candidate["status"],
            "successful_strengthenings": candidate["successful_strengthenings"],
            "models_before": len(before_models),
            "models_after": len(after_models),
            "model_sets_equal": before_models == after_models,
            "certificate_replay": replay,
        }
    return out


def frozen_r35_core() -> Tuple[Formula, dict]:
    source = r33.deterministic_random_3cnf(33004, n=24, ratio=4.2)
    reduced = r33.simplify(source)
    core = r33.canonical_formula(reduced["final_formula"])
    core_hash = r35.canonical_json_sha256([list(c) for c in core])
    receipt = {
        "source_measure": list(r33.measure(source)),
        "R33_final_measure": reduced["final_measure"],
        "R33_rule_applications": reduced["total_rule_applications"],
        "core_measure": list(r33.measure(core)),
        "core_hash": core_hash,
    }
    if receipt != {
        "source_measure": [101, 303, 24],
        "R33_final_measure": [98, 300, 23],
        "R33_rule_applications": 3,
        "core_measure": [98, 300, 23],
        "core_hash": "7c42618d0fbb3b6e2d6681e265e56a76fa80b4021fd2ad1590d6f5fe9fb608ff",
    }:
        raise AssertionError(("R35 frozen core drift", receipt))
    return core, receipt


def run_audit() -> dict:
    core, core_receipt = frozen_r35_core()
    controls = small_semantic_controls()
    candidate = run_candidate(core)
    checker = independent_certificate_replay(core, candidate)

    if not all(c["pass"] for c in controls.values()):
        verdict = "R35B_FAIL_INTEGRITY"
    elif not checker["pass"]:
        verdict = "R35B_RUP_CERTIFICATE_MISMATCH"
    elif candidate["status"] == "UNSAT_BY_UNIT_PROPAGATION":
        verdict = "R35B_RUP_VIVIFICATION_PROVES_UNSAT_ON_EXPOSED_CORE__NO_UNIVERSAL_CLAIM"
    elif candidate["successful_strengthenings"]:
        verdict = "R35B_RUP_VIVIFICATION_REDUCES_THEN_STALLS__NO_SEMANTIC_VERDICT"
    else:
        verdict = "R35B_RUP_VIVIFICATION_STALLS_WITHOUT_REDUCTION__NO_SEMANTIC_VERDICT"

    history_bytes = len(json.dumps(candidate["history"], sort_keys=True, separators=(",", ":")).encode("utf-8"))
    return {
        "schema": "JANUS_TRUMP_R35B_SINGLE_LITERAL_RUP_VIVIFICATION_RESULT",
        "version": "1.0",
        "date": "2026-09-02",
        "source_git_commit": os.environ.get("GITHUB_SHA", "LOCAL"),
        "verdict": verdict,
        "mechanism": "SINGLE_LITERAL_RUP_VIVIFICATION",
        "frozen_R35_core_replay": core_receipt,
        "candidate_firewall": {
            "external_SAT_solver_used": False,
            "DPLL_or_CDCL_used": False,
            "assignment_enumeration_inside_candidate": False,
            "global_semantic_oracle_used": False,
            "multi_literal_removal_in_one_step": False,
            "second_new_mechanism_added": False,
        },
        "small_post_candidate_semantic_controls": controls,
        "candidate": {
            "status": candidate["status"],
            "initial_measure_LCV": candidate["initial_measure"],
            "final_measure_LCV": candidate["final_measure"],
            "successful_strengthenings": candidate["successful_strengthenings"],
            "ledger": candidate["ledger"],
            "certificate_history_bytes": history_bytes,
            "history": candidate["history"],
            "final_up_receipt": candidate["final_up_receipt"],
            "final_formula": candidate["final_formula"],
        },
        "independent_certificate_checker": checker,
        "captain_verdict": {
            "answer": "CERTIFIED_TAIL_TRUNCATION_REALIZED_AS_RUP_LITERAL_DELETION_ON_THE_EXPOSED_CORE",
            "boundary": "The rule was discovered using this core. A successful UNSAT proof closes only this exposed counterexample and must be frozen before a fresh unseen non-affine holdout.",
        },
        "R31_obligation_impact": {
            "obligations_closed": 0,
            "reason": "Polynomial checkability and strict progress of this rule are explicit, but universal availability of a RUP strengthening on every nonterminal 3-CNF is not proved.",
        },
        "next_gate": {
            "if_UNSAT_success": "R36_FRESH_NONAFFINE_RUP_VIVIFICATION_HOLDOUT",
            "if_stall": "Seal the R35B residual before proposing another mechanism.",
        },
        "TRUMP_finished": False,
        "SAT_IN_P": "NOT_PROVED",
        "P_VS_NP": "OPEN",
        "runtime_authority": False,
    }


def self_test() -> None:
    d = run_audit()
    assert d["frozen_R35_core_replay"]["core_hash"] == "7c42618d0fbb3b6e2d6681e265e56a76fa80b4021fd2ad1590d6f5fe9fb608ff"
    assert all(c["pass"] for c in d["small_post_candidate_semantic_controls"].values())
    assert d["independent_certificate_checker"]["pass"] is True
    assert d["candidate"]["successful_strengthenings"] <= 300
    print("R35B_SELF_TEST_PASS", d["verdict"], d["candidate"]["successful_strengthenings"], d["candidate"]["final_measure_LCV"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    text = json.dumps(run_audit(), indent=2, sort_keys=True) + "\n"
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
