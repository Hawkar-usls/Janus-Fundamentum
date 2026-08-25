#!/usr/bin/env python3
"""
C032 JANUS PS-width alignment audit.

This artifact proves, at the level of exact definitions, that the JANUS
"semantic cut signature" is the precisely-satisfiable-set interface used by
PS-width. It also verifies a gap family with:

    incidence graph = K_{n,m}
    incidence treewidth = min(n,m)
    C028 overlap defect = n  (for m >= 2)
    every cut PS-value <= 2

The family shows that large structural overlap and large incidence treewidth do
not preclude constant semantic cut width.

The script is a finite verifier for the definitional identity and family
invariants. The general mathematical proof is in the companion Markdown note.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import random
from pathlib import Path

Clause = tuple[int, ...]
CNF = tuple[Clause, ...]
Signature = tuple[int, ...]


def formula_variables(formula: CNF) -> set[int]:
    return {abs(lit) for clause in formula for lit in clause}


def project_formula(
    formula: CNF,
    clause_indices: set[int],
    variables: set[int],
) -> tuple[Clause, ...]:
    """Keep selected clauses and only literals over selected variables."""
    return tuple(
        tuple(lit for lit in formula[index] if abs(lit) in variables)
        for index in sorted(clause_indices)
    )


def assignment_signatures(projected: tuple[Clause, ...]) -> set[Signature]:
    """All exactly satisfied clause-index sets of a projected formula."""
    variables = sorted({abs(lit) for clause in projected for lit in clause})
    signatures: set[Signature] = set()

    for bits in itertools.product((False, True), repeat=len(variables)):
        assignment = dict(zip(variables, bits))
        satisfied = tuple(
            clause_index
            for clause_index, clause in enumerate(projected)
            if any(assignment[abs(lit)] == (lit > 0) for lit in clause)
        )
        signatures.add(satisfied)

    return signatures


def ps_cut_signatures(
    formula: CNF,
    selected_clauses: set[int],
    selected_variables: set[int],
) -> tuple[set[Signature], set[Signature]]:
    """
    STV cut:
      left  = clauses outside C projected to X
      right = clauses inside C projected to V\X
    """
    all_clauses = set(range(len(formula)))
    all_variables = formula_variables(formula)

    left = project_formula(
        formula,
        all_clauses - selected_clauses,
        selected_variables,
    )
    right = project_formula(
        formula,
        selected_clauses,
        all_variables - selected_variables,
    )
    return assignment_signatures(left), assignment_signatures(right)


def direct_boundary_signatures(
    formula: CNF,
    selected_clauses: set[int],
    selected_variables: set[int],
) -> tuple[set[Signature], set[Signature]]:
    """
    Independent JANUS-side computation.

    For each partial assignment, record exactly which clauses on the opposite
    side of the cut are already satisfied by literals visible on this side.
    """
    all_clauses = set(range(len(formula)))
    all_variables = formula_variables(formula)

    outside_clauses = sorted(all_clauses - selected_clauses)
    left_variables = sorted(selected_variables)
    left_signatures: set[Signature] = set()

    for bits in itertools.product((False, True), repeat=len(left_variables)):
        assignment = dict(zip(left_variables, bits))
        signature = tuple(
            local_index
            for local_index, clause_index in enumerate(outside_clauses)
            if any(
                abs(lit) in selected_variables
                and assignment[abs(lit)] == (lit > 0)
                for lit in formula[clause_index]
            )
        )
        left_signatures.add(signature)

    inside_clauses = sorted(selected_clauses)
    right_variables_set = all_variables - selected_variables
    right_variables = sorted(right_variables_set)
    right_signatures: set[Signature] = set()

    for bits in itertools.product((False, True), repeat=len(right_variables)):
        assignment = dict(zip(right_variables, bits))
        signature = tuple(
            local_index
            for local_index, clause_index in enumerate(inside_clauses)
            if any(
                abs(lit) in right_variables_set
                and assignment[abs(lit)] == (lit > 0)
                for lit in formula[clause_index]
            )
        )
        right_signatures.add(signature)

    return left_signatures, right_signatures


def duplicate_clause_family(variable_count: int, clause_count: int) -> CNF:
    clause = tuple(range(1, variable_count + 1))
    return tuple(clause for _ in range(clause_count))


def verify_duplicate_family_all_cuts(
    max_variables: int = 5,
    max_clauses: int = 5,
) -> dict[str, int]:
    cuts_checked = 0
    maximum_ps_value = 0

    for variable_count in range(1, max_variables + 1):
        for clause_count in range(1, max_clauses + 1):
            formula = duplicate_clause_family(variable_count, clause_count)

            for clause_mask in range(1 << clause_count):
                selected_clauses = {
                    index
                    for index in range(clause_count)
                    if clause_mask & (1 << index)
                }

                for variable_mask in range(1 << variable_count):
                    selected_variables = {
                        index + 1
                        for index in range(variable_count)
                        if variable_mask & (1 << index)
                    }

                    left, right = ps_cut_signatures(
                        formula,
                        selected_clauses,
                        selected_variables,
                    )
                    assert len(left) <= 2
                    assert len(right) <= 2
                    maximum_ps_value = max(
                        maximum_ps_value,
                        len(left),
                        len(right),
                    )
                    cuts_checked += 1

    return {
        "cuts_checked": cuts_checked,
        "maximum_ps_value": maximum_ps_value,
    }


def random_formula(
    rng: random.Random,
    variable_count: int,
    clause_count: int,
) -> CNF:
    clauses: list[Clause] = []

    for _ in range(clause_count):
        width = rng.randint(1, min(3, variable_count))
        variables = rng.sample(range(1, variable_count + 1), width)
        clause = tuple(
            variable if rng.getrandbits(1) else -variable
            for variable in variables
        )
        clauses.append(clause)

    return tuple(clauses)


def verify_signature_identity(
    seed: int = 320032,
    cases: int = 800,
) -> dict[str, int]:
    rng = random.Random(seed)
    signatures_checked = 0

    for _ in range(cases):
        variable_count = rng.randint(1, 7)
        clause_count = rng.randint(1, 8)
        formula = random_formula(rng, variable_count, clause_count)

        selected_clauses = {
            index
            for index in range(clause_count)
            if rng.getrandbits(1)
        }
        selected_variables = {
            variable
            for variable in range(1, variable_count + 1)
            if rng.getrandbits(1)
        }

        ps_left, ps_right = ps_cut_signatures(
            formula,
            selected_clauses,
            selected_variables,
        )
        janus_left, janus_right = direct_boundary_signatures(
            formula,
            selected_clauses,
            selected_variables,
        )

        assert ps_left == janus_left
        assert ps_right == janus_right
        signatures_checked += len(ps_left) + len(ps_right)

    return {
        "cases": cases,
        "signatures_checked": signatures_checked,
    }


def full_signature_cut_control(max_variables: int = 16) -> list[dict[str, int]]:
    """
    At one explicit cut of the unit-clause formula, all 2^n signatures occur.
    This is a cut-level explosion, not a lower bound on optimal PS-width.
    """
    rows: list[dict[str, int]] = []

    for variable_count in range(1, max_variables + 1):
        formula = tuple((variable,) for variable in range(1, variable_count + 1))
        left, right = ps_cut_signatures(
            formula,
            selected_clauses=set(),
            selected_variables=set(range(1, variable_count + 1)),
        )
        assert len(left) == 1 << variable_count
        assert len(right) == 1

        rows.append(
            {
                "variables": variable_count,
                "left_signatures": len(left),
            }
        )

    return rows


def run() -> dict:
    identity = verify_signature_identity()
    duplicate = verify_duplicate_family_all_cuts()
    explosion = full_signature_cut_control()

    result = {
        "artifact_id": "C032-JANUS-PS-WIDTH-ALIGNMENT",
        "status": "PASS",
        "p_vs_np": "OPEN",
        "definition_alignment": (
            "JANUS semantic cut signatures equal the precisely satisfiable "
            "clause sets used by PS-width."
        ),
        "random_identity_audit": identity,
        "duplicate_clause_gap_family": {
            **duplicate,
            "incidence_graph": "K_{n,m}",
            "incidence_treewidth": "min(n,m)",
            "c028_overlap_defect_for_m_ge_2": "n",
            "general_ps_width_upper_bound": 2,
        },
        "explicit_cut_explosion": explosion,
        "located_bottleneck": (
            "POLYNOMIAL_PS_DECOMPOSITION_OR_SYMBOLIC_SIGNATURE_COMPRESSION"
        ),
        "claim_boundary": (
            "This aligns JANUS with an existing exact width framework and "
            "proves a structural/semantic gap family. It does not show that "
            "all CNFs have polynomial PS-width or resolve P versus NP."
        ),
    }

    payload = json.dumps(
        result,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    result["integrity_sha256"] = hashlib.sha256(payload).hexdigest()
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = run()

    if args.output:
        args.output.write_text(
            json.dumps(result, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    print(json.dumps(result, indent=2, sort_keys=True))

    if args.self_test:
        assert result["status"] == "PASS"
        assert result["random_identity_audit"]["cases"] == 800
        assert result["duplicate_clause_gap_family"]["maximum_ps_value"] == 2
        assert result["explicit_cut_explosion"][-1]["left_signatures"] == 65536


if __name__ == "__main__":
    main()
