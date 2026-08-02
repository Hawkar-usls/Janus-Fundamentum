#!/usr/bin/env python3
"""Software-only audit of Observer roles in the JANUS Tear route."""

from __future__ import annotations

import argparse
import json
import random
from itertools import product

Clause = tuple[int, ...]
Formula = tuple[Clause, ...]
Assignment = dict[int, bool]


def vars_of(formula: Formula | None) -> tuple[int, ...]:
    if formula is None:
        return ()
    return tuple(sorted({abs(lit) for clause in formula for lit in clause}))


def simplify(formula: Formula | None, assignment: Assignment) -> Formula | None:
    if formula is None:
        return None
    out: list[Clause] = []
    for clause in formula:
        kept: list[int] = []
        satisfied = False
        for lit in clause:
            value = assignment.get(abs(lit))
            if value is None:
                kept.append(lit)
            elif value == (lit > 0):
                satisfied = True
                break
        if satisfied:
            continue
        if not kept:
            return None
        out.append(tuple(kept))
    return tuple(out)


def satisfies(formula: Formula, assignment: Assignment) -> bool:
    return all(
        any(assignment.get(abs(lit), False) == (lit > 0) for lit in clause)
        for clause in formula
    )


def brute_force(formula: Formula | None) -> tuple[str, Assignment | None, int]:
    if formula is None:
        return "UNSAT", None, 0
    variables = vars_of(formula)
    checked = 0
    for bits in product((False, True), repeat=len(variables)):
        checked += 1
        assignment = dict(zip(variables, bits))
        if satisfies(formula, assignment):
            return "SAT", assignment, checked
    return "UNSAT", None, checked


def dpll(formula: Formula, observer=None) -> dict[str, object]:
    variables = vars_of(formula)
    nodes = 0
    observer_calls = 0

    def rec(partial: Assignment) -> Assignment | None:
        nonlocal nodes, observer_calls
        nodes += 1
        residual = simplify(formula, partial)
        if observer is not None:
            observer(residual, dict(partial))
            observer_calls += 1
        if residual is None:
            return None
        if not residual:
            return dict(partial)
        variable = next((v for v in variables if v not in partial), None)
        if variable is None:
            return None
        for value in (False, True):
            partial[variable] = value
            witness = rec(partial)
            partial.pop(variable)
            if witness is not None:
                return witness
        return None

    witness = rec({})
    if witness is not None:
        for variable in variables:
            witness.setdefault(variable, False)
        assert satisfies(formula, witness)
    return {
        "status": "SAT" if witness is not None else "UNSAT",
        "witness": witness,
        "visited_nodes": nodes,
        "observer_calls": observer_calls,
    }


def passive_observer_audit() -> dict[str, object]:
    rng = random.Random(9379992)
    cases = 120
    same_status = 0
    same_nodes = 0
    calls = 0
    for _ in range(cases):
        n = rng.randint(2, 7)
        clauses: list[Clause] = []
        for _ in range(rng.randint(n, 3 * n)):
            width = rng.randint(1, min(3, n))
            scope = rng.sample(range(1, n + 1), width)
            clauses.append(tuple(v if rng.getrandbits(1) else -v for v in scope))
        formula = tuple(clauses)
        transcript = []
        control = dpll(formula)
        observed = dpll(formula, lambda residual, partial: transcript.append(
            (-1 if residual is None else len(residual), len(partial))
        ))
        same_status += int(control["status"] == observed["status"])
        same_nodes += int(control["visited_nodes"] == observed["visited_nodes"])
        calls += int(observed["observer_calls"])
    return {
        "cases": cases,
        "same_status": same_status,
        "same_visited_nodes": same_nodes,
        "observer_calls": calls,
        "result": "PASS",
        "meaning": "Passive deterministic observation preserves the search tree and adds overhead."
    }


def collapse_observer_audit() -> dict[str, object]:
    # x=false -> (a) & (!a) is UNSAT; x=true -> (b) is SAT.
    formula: Formula = ((1, 2), (1, -2), (-1, 3))
    whole, witness, _ = brute_force(formula)
    false_status, _, _ = brute_force(simplify(formula, {1: False}))
    true_status, true_witness, _ = brute_force(simplify(formula, {1: True}))
    assert (whole, false_status, true_status) == ("SAT", "UNSAT", "SAT")
    return {
        "formula": formula,
        "whole_status": whole,
        "whole_witness": witness,
        "measured_branch": {"x": False, "status": false_status},
        "discarded_branch": {"x": True, "status": true_status, "witness": true_witness},
        "naive_collapse_conclusion": "UNSAT",
        "correct_conclusion": "SAT",
        "result": "REJECT",
        "meaning": "Discarding unobserved branches is unsound without a proof that they contain no witness."
    }


def extendable(formula: Formula, partial: Assignment) -> tuple[bool, int]:
    residual = simplify(formula, partial)
    if residual is None:
        return False, 0
    remaining = [v for v in vars_of(formula) if v not in partial]
    checked = 0
    for bits in product((False, True), repeat=len(remaining)):
        checked += 1
        assignment = dict(partial)
        assignment.update(zip(remaining, bits))
        if satisfies(formula, assignment):
            return True, checked
    return False, checked


def oracle_guided_witness(formula: Formula) -> dict[str, object]:
    partial: Assignment = {}
    queries = 0
    hidden_checks = 0
    possible, checks = extendable(formula, {})
    queries += 1
    hidden_checks += checks
    if not possible:
        return {"status": "UNSAT", "queries": queries, "hidden_checks": hidden_checks}
    for variable in vars_of(formula):
        trial = dict(partial)
        trial[variable] = False
        possible, checks = extendable(formula, trial)
        queries += 1
        hidden_checks += checks
        partial[variable] = False if possible else True
    assert satisfies(formula, partial)
    return {
        "status": "SAT",
        "queries": queries,
        "hidden_checks": hidden_checks,
        "witness": partial,
    }


def oracle_observer_audit() -> dict[str, object]:
    records = []
    for n in range(1, 15):
        formula = tuple((v,) for v in range(1, n + 1))  # unique all-true witness
        result = oracle_guided_witness(formula)
        assert result["queries"] == n + 1
        assert result["hidden_checks"] == 2**n
        records.append({
            "variables": n,
            "outer_queries": result["queries"],
            "hidden_assignment_checks": result["hidden_checks"],
        })
    return {
        "records": records,
        "result": "PASS",
        "meaning": (
            "An EXTENDABLE observer recovers a witness with n+1 outer queries, "
            "but the exact observation can hide exponential work and is SAT-hard in general."
        )
    }


def certificate_observer_audit() -> dict[str, object]:
    formula: Formula = ((1, -2, 3), (-1, 2), (2, 3), (-3, 1))
    witness = {1: True, 2: True, 3: True}
    literal_checks = 0
    valid = True
    for clause in formula:
        clause_ok = False
        for lit in clause:
            literal_checks += 1
            if witness.get(abs(lit), False) == (lit > 0):
                clause_ok = True
                break
        valid &= clause_ok

    unsat_formula: Formula = ((1,), (-1,))
    # Tiny proof-bearing Tear: resolve x and !x to the empty clause.
    resolution_valid = (
        1 in unsat_formula[0]
        and -1 in unsat_formula[1]
        and tuple(sorted((set(unsat_formula[0]) - {1}) |
                         (set(unsat_formula[1]) - {-1}))) == ()
    )
    assert valid and resolution_valid
    return {
        "sat_witness_valid": valid,
        "sat_literal_checks": literal_checks,
        "bare_unsat_claim_verifiable": False,
        "proof_bearing_unsat_tear_verifiable": resolution_valid,
        "result": "PASS",
        "meaning": "Observation can verify supplied evidence; it does not generate the evidence."
    }


def postselection_audit() -> dict[str, object]:
    records = [{
        "variables": n,
        "unique_witness_probability": 2.0**(-n),
        "expected_uniform_samples": 2**n,
        "retained_samples_if_postselection_is_free": 1,
    } for n in (4, 8, 12, 16, 20, 24)]
    return {
        "records": records,
        "result": "BOUNDARY",
        "meaning": "Free postselection hides the inverse probability cost and is an extra resource."
    }


def run_audit() -> dict[str, object]:
    return {
        "artifact": "JANUS-OBSERVER-EFFECT-AUDIT",
        "status": "EXPLORATORY_SOFTWARE_ONLY",
        "execution_scope": {
            "swarm_touched": False,
            "devices_touched": False,
            "networked_runtime_touched": False,
            "quantum_hardware_used": False,
        },
        "observer_definition": (
            "An observer is an information-acquisition and state-update interface. "
            "Measurement, disturbance, policy, proof and recovery costs are all charged."
        ),
        "audits": {
            "passive": passive_observer_audit(),
            "collapse": collapse_observer_audit(),
            "extendability_oracle": oracle_observer_audit(),
            "certificate_verifier": certificate_observer_audit(),
            "postselection": postselection_audit(),
        },
        "role_matrix": [
            {
                "role": "passive_logger",
                "verdict": "same algorithm plus overhead",
            },
            {
                "role": "active_policy",
                "verdict": "part of the algorithm; can help structured families but needs a worst-case theorem",
            },
            {
                "role": "certificate_verifier",
                "verdict": "verification is polynomial when evidence is supplied; generation remains hard",
            },
            {
                "role": "extendability_oracle",
                "verdict": "linear outer self-reduction, with SAT hidden inside the observation",
            },
            {
                "role": "collapse_commit",
                "verdict": "unsound if an unobserved branch may contain the only witness",
            },
            {
                "role": "free_postselection",
                "verdict": "strong extra resource, not ordinary observation",
            },
            {
                "role": "quantum_measurement",
                "verdict": "physical interaction, not consciousness; no automatic NP-complete speedup",
            },
        ],
        "surviving_conjecture": (
            "A useful universal Observer must expose polynomial-cost measurements "
            "that select small proof languages and branches without computing SAT "
            "inside the measurement."
        ),
        "claim_boundary": (
            "No proof of P=NP, P!=NP, NP=coNP, or a physical observer effect on classical SAT."
        ),
    }


def self_test() -> None:
    audit = run_audit()
    passive = audit["audits"]["passive"]
    assert passive["same_status"] == passive["cases"]
    assert passive["same_visited_nodes"] == passive["cases"]
    collapse = audit["audits"]["collapse"]
    assert collapse["whole_status"] == "SAT"
    assert collapse["measured_branch"]["status"] == "UNSAT"
    assert collapse["discarded_branch"]["status"] == "SAT"
    oracle = audit["audits"]["extendability_oracle"]
    assert oracle["records"][-1]["outer_queries"] == 15
    assert oracle["records"][-1]["hidden_assignment_checks"] == 2**14
    assert audit["audits"]["certificate_verifier"]["sat_witness_valid"] is True
    print("JANUS_OBSERVER_EFFECT_AUDIT = PASS")
    print("PASSIVE_OBSERVER = SAME_TREE_PLUS_OVERHEAD")
    print("COLLAPSE_OBSERVER = UNSOUND")
    print("EXTENDABILITY_OBSERVER = LINEAR_QUERIES_HIDDEN_HARD_WORK")
    print("CERTIFICATE_OBSERVER = VERIFY_NOT_GENERATE")
    print("POSTSELECTION_OBSERVER = EXTRA_RESOURCE")
    print("SWARM_TOUCHED = false")
    print("DEVICES_TOUCHED = false")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.json:
        print(json.dumps(run_audit(), indent=2))
        return 0
    parser.error("use --self-test or --json")


if __name__ == "__main__":
    raise SystemExit(main())
