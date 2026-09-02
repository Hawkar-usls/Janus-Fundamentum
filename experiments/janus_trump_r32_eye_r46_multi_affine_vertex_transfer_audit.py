#!/usr/bin/env python3
"""R32 audit of the EYE-R4.6 multi-affine vertex principle for TRUMP.

This is deliberately an observer, not a SAT-solver candidate.  It compiles a
width-at-most-three CNF to the explicit multi-affine clause-violation penalty

    P_F(x) = sum_C product_{literal l in C} q_l(x),

and charges the direct false-first vertex route used by the proposed transfer.
Enumeration is visible and permitted only because its 2^n cost is the object
being measured.
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
import random
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence


Clause = tuple[int, ...]
CNF = tuple[Clause, ...]
Factor = tuple[int, int]
Term = tuple[Factor, ...]

SCHEMA = "JANUS/TRUMP/R32/EYE_R46_MULTI_AFFINE_VERTEX_TRANSFER_AUDIT/RESULT/v1.0"
PREREGISTRATION_COMMIT = "6dd34b267e127c6a54d49e5bcddd25a058c2194e"
PREREGISTRATION_BLOB = "322108716166f650dd36ce9704583d260b210a90"
R31_COMMIT = "31e767296cbaa436ef97ac16b0c603880e38443f"
EYE_R46_MERGE_COMMIT = "14ac2d09e80dfa9141c72cd5ed35092b84e5f35a"
EYE_R46_RECEIPT_COMMIT = "6fe24536ac34f83971aac02bd6cedee6d091d87e"
EYE_R46_RUN_ID = 33644301485
MAX_CONTROL_VARIABLES = 18
MAX_VERTICES_IN_ONE_CONTROL = 1 << MAX_CONTROL_VARIABLES


class AuditError(ValueError):
    """The frozen audit input or an internal control is invalid."""


def normalize_cnf(variable_count: int, clauses: Iterable[Iterable[int]]) -> CNF:
    """Apply only the preregistered local normalization rules."""

    if not isinstance(variable_count, int) or variable_count < 0:
        raise AuditError("BAD_VARIABLE_COUNT")
    normalized: list[Clause] = []
    for raw_clause in clauses:
        raw = tuple(raw_clause)
        if len(raw) > 3:
            raise AuditError("CLAUSE_WIDTH_EXCEEDS_3")
        seen: set[int] = set()
        tautology = False
        for literal in raw:
            if not isinstance(literal, int) or isinstance(literal, bool):
                raise AuditError("NON_INTEGER_LITERAL")
            if literal == 0 or abs(literal) > variable_count:
                raise AuditError("LITERAL_OUT_OF_RANGE")
            if -literal in seen:
                tautology = True
            seen.add(literal)
        if tautology:
            continue
        # Sorting makes the serialized transform independent of literal order.
        normalized.append(tuple(sorted(seen, key=lambda lit: (abs(lit), lit < 0))))
    return tuple(normalized)


def compile_violation_terms(cnf: CNF) -> tuple[Term, ...]:
    """Compile one product term per normalized clause.

    A factor is (zero-based variable index, Boolean value that makes the
    literal false).  Positive x_i is false at 0; negative x_i is false at 1.
    """

    terms: list[Term] = []
    for clause in cnf:
        term = tuple((abs(literal) - 1, 0 if literal > 0 else 1) for literal in clause)
        if len({variable for variable, _ in term}) != len(term):
            raise AuditError("NON_MULTI_AFFINE_TERM_AFTER_NORMALIZATION")
        terms.append(term)
    return tuple(terms)


def verify_multi_affine_syntax(terms: Sequence[Term]) -> dict[str, object]:
    max_exponent = 0
    factors = 0
    for term in terms:
        variables = [variable for variable, _ in term]
        if len(variables) != len(set(variables)):
            return {
                "pass": False,
                "reason": "VARIABLE_REPEATED_WITHIN_PRODUCT_TERM",
                "term_count": len(terms),
            }
        max_exponent = max(max_exponent, 1 if term else 0)
        factors += len(term)
    return {
        "pass": True,
        "term_count": len(terms),
        "factor_occurrences": factors,
        "maximum_per_term_variable_exponent": max_exponent,
        "sum_preserves_multi_affinity": True,
    }


def mask_to_bits(mask: int, variable_count: int) -> tuple[int, ...]:
    return tuple((mask >> (variable_count - 1 - index)) & 1 for index in range(variable_count))


def penalty_at_boolean_vertex(terms: Sequence[Term], bits: Sequence[int]) -> tuple[int, int]:
    """Return exact penalty and charged factor evaluations (no short circuit)."""

    penalty = 0
    factor_evaluations = 0
    for term in terms:
        violated = 1
        for variable, false_value in term:
            factor_evaluations += 1
            violated *= int(bits[variable] == false_value)
        penalty += violated
    return penalty, factor_evaluations


def direct_unsatisfied_clause_count(cnf: CNF, bits: Sequence[int]) -> tuple[int, int]:
    """Independent Boolean-clause evaluator used only by the controls."""

    unsatisfied = 0
    literal_checks = 0
    for clause in cnf:
        clause_true = False
        for literal in clause:
            literal_checks += 1
            value = bool(bits[abs(literal) - 1])
            if (literal > 0 and value) or (literal < 0 and not value):
                clause_true = True
        if not clause_true:
            unsatisfied += 1
    return unsatisfied, literal_checks


def penalty_at_fractional_point(terms: Sequence[Term], point: Sequence[Fraction]) -> Fraction:
    penalty = Fraction(0, 1)
    for term in terms:
        product = Fraction(1, 1)
        for variable, false_value in term:
            product *= point[variable] if false_value == 1 else 1 - point[variable]
        penalty += product
    return penalty


def stream_false_first_vertices(
    cnf: CNF,
    variable_count: int,
    *,
    stop_at_zero: bool,
    max_vertices: int = MAX_VERTICES_IN_ONE_CONTROL,
) -> dict[str, object]:
    """Charge every vertex in the direct lexicographic false-first route."""

    total_vertices = 1 << variable_count
    if total_vertices > max_vertices:
        return {
            "status": "OPEN_RESOURCE_LIMIT",
            "reason": "VERTEX_COUNT_EXCEEDS_FROZEN_CONTROL_CEILING",
            "variable_count": variable_count,
            "required_vertices": total_vertices,
            "max_vertices": max_vertices,
        }
    terms = compile_violation_terms(cnf)
    best_penalty: int | None = None
    best_bits: tuple[int, ...] | None = None
    factor_evaluations = 0
    vertices_evaluated = 0
    first_zero_index: int | None = None
    for mask in range(total_vertices):
        bits = mask_to_bits(mask, variable_count)
        penalty, work = penalty_at_boolean_vertex(terms, bits)
        vertices_evaluated += 1
        factor_evaluations += work
        if best_penalty is None or penalty < best_penalty:
            best_penalty = penalty
            best_bits = bits
        if penalty == 0 and first_zero_index is None:
            first_zero_index = mask
            if stop_at_zero:
                break
    assert best_penalty is not None and best_bits is not None
    direct_count, witness_checks = direct_unsatisfied_clause_count(cnf, best_bits)
    if direct_count != best_penalty:
        raise AssertionError("INDEPENDENT_WITNESS_REPLAY_MISMATCH")
    terminal_sat = best_penalty == 0
    return {
        "status": "COMPLETE",
        "variable_count": variable_count,
        "clause_count": len(cnf),
        "term_count": len(terms),
        "factor_occurrences_per_full_penalty_evaluation": sum(len(term) for term in terms),
        "vertices_in_full_box": total_vertices,
        "vertices_generated": vertices_evaluated,
        "vertices_evaluated": vertices_evaluated,
        "literal_factors_evaluated": factor_evaluations,
        "minimum_penalty_seen": best_penalty,
        "minimizing_vertex": list(best_bits),
        "first_zero_penalty_vertex_index_zero_based": first_zero_index,
        "stop_at_zero": stop_at_zero,
        "terminal_decision": "SAT" if terminal_sat else "UNSAT",
        "peak_retained_vertex_records": 2,
        "sat_witness_direct_literal_checks": witness_checks if terminal_sat else None,
        "same_method_unsat_or_global_extremum_replay_vertices": total_vertices,
    }


def hand_controls() -> dict[str, object]:
    cases = [
        {
            "id": "SAT_ZERO_PENALTY",
            "variables": 2,
            "clauses": ((1, 2), (-1, 2), (1, -2)),
            "expected_minimum": 0,
            "expected_decision": "SAT",
        },
        {
            "id": "UNSAT_POSITIVE_MINIMUM",
            "variables": 1,
            "clauses": ((1,), (-1,)),
            "expected_minimum": 1,
            "expected_decision": "UNSAT",
        },
        {
            "id": "DUPLICATE_AND_TAUTOLOGY_NORMALIZATION",
            "variables": 2,
            "clauses": ((1, 1, -2), (2, -2, 1)),
            "expected_normalized": ((1, -2),),
            "expected_minimum": 0,
            "expected_decision": "SAT",
        },
        {
            "id": "EMPTY_CLAUSE_CONSTANT_TERM",
            "variables": 2,
            "clauses": ((),),
            "expected_minimum": 1,
            "expected_decision": "UNSAT",
        },
    ]
    rows = []
    passed = True
    for case in cases:
        cnf = normalize_cnf(case["variables"], case["clauses"])
        run = stream_false_first_vertices(cnf, case["variables"], stop_at_zero=False)
        ok = (
            run["status"] == "COMPLETE"
            and run["minimum_penalty_seen"] == case["expected_minimum"]
            and run["terminal_decision"] == case["expected_decision"]
            and ("expected_normalized" not in case or cnf == case["expected_normalized"])
        )
        passed = passed and ok
        rows.append(
            {
                "id": case["id"],
                "pass": ok,
                "normalized_cnf": [list(clause) for clause in cnf],
                "minimum_penalty": run["minimum_penalty_seen"],
                "decision": run["terminal_decision"],
            }
        )
    return {"pass": passed, "case_count": len(rows), "cases": rows}


def deterministic_formula_suite(seed: int = 32046, formula_count: int = 192) -> dict[str, object]:
    rng = random.Random(seed)
    formula_rows = 0
    assignments_checked = 0
    factor_evaluations = 0
    mismatches: list[dict[str, object]] = []
    grid_cases = 0
    grid_points_checked = 0
    for formula_index in range(formula_count):
        variable_count = rng.randint(1, 7)
        clause_count = rng.randint(1, 12)
        raw_clauses: list[Clause] = []
        for _ in range(clause_count):
            width = rng.randint(1, min(3, variable_count))
            variables = rng.sample(range(1, variable_count + 1), width)
            raw_clauses.append(tuple(variable if rng.randrange(2) else -variable for variable in variables))
        cnf = normalize_cnf(variable_count, raw_clauses)
        terms = compile_violation_terms(cnf)
        syntax = verify_multi_affine_syntax(terms)
        if not syntax["pass"]:
            mismatches.append({"formula_index": formula_index, "kind": "SYNTAX"})
            continue
        direct_sat = False
        min_penalty: int | None = None
        max_penalty: int | None = None
        for mask in range(1 << variable_count):
            bits = mask_to_bits(mask, variable_count)
            penalty, work = penalty_at_boolean_vertex(terms, bits)
            unsatisfied, _ = direct_unsatisfied_clause_count(cnf, bits)
            assignments_checked += 1
            factor_evaluations += work
            if penalty != unsatisfied:
                mismatches.append(
                    {
                        "formula_index": formula_index,
                        "kind": "BOOLEAN_PENALTY_MISMATCH",
                        "mask": mask,
                        "penalty": penalty,
                        "direct": unsatisfied,
                    }
                )
                break
            direct_sat = direct_sat or unsatisfied == 0
            min_penalty = penalty if min_penalty is None else min(min_penalty, penalty)
            max_penalty = penalty if max_penalty is None else max(max_penalty, penalty)
        if (min_penalty == 0) != direct_sat:
            mismatches.append({"formula_index": formula_index, "kind": "SAT_EQUIVALENCE_MISMATCH"})
        # Exact rational interior control on a fixed, small prefix.  This is an
        # implementation check; the analytic coordinate argument is separate.
        if formula_index < 48 and variable_count <= 4 and min_penalty is not None:
            grid_cases += 1
            for point in itertools.product((Fraction(0), Fraction(1, 2), Fraction(1)), repeat=variable_count):
                value = penalty_at_fractional_point(terms, point)
                grid_points_checked += 1
                if value < min_penalty or value > max_penalty:
                    mismatches.append(
                        {
                            "formula_index": formula_index,
                            "kind": "GRID_OUTSIDE_VERTEX_EXTREMA",
                            "point": [str(x) for x in point],
                            "value": str(value),
                        }
                    )
                    break
        formula_rows += 1
    return {
        "pass": not mismatches and formula_rows == formula_count,
        "seed": seed,
        "formula_count": formula_rows,
        "variable_range": [1, 7],
        "assignments_checked": assignments_checked,
        "literal_factors_evaluated": factor_evaluations,
        "exact_rational_grid_cases": grid_cases,
        "exact_rational_grid_points_checked": grid_points_checked,
        "mismatches": mismatches,
        "purpose": "IMPLEMENTATION_FALSIFICATION_ONLY__NOT_A_UNIVERSAL_THEOREM_OR_GENERALIZATION_CLAIM",
    }


def false_first_last_vertex_family(max_variables: int = MAX_CONTROL_VARIABLES) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    passed = True
    total_vertices = 0
    total_factor_evaluations = 0
    previous_vertices: int | None = None
    for variable_count in range(1, max_variables + 1):
        cnf = normalize_cnf(variable_count, ((variable,) for variable in range(1, variable_count + 1)))
        run = stream_false_first_vertices(cnf, variable_count, stop_at_zero=True)
        expected = 1 << variable_count
        recurrence_ok = previous_vertices is None or run["vertices_evaluated"] == 2 * previous_vertices
        ok = (
            run["status"] == "COMPLETE"
            and run["terminal_decision"] == "SAT"
            and run["minimum_penalty_seen"] == 0
            and run["vertices_evaluated"] == expected
            and run["first_zero_penalty_vertex_index_zero_based"] == expected - 1
            and run["minimizing_vertex"] == [1] * variable_count
            and recurrence_ok
        )
        passed = passed and ok
        vertices = int(run["vertices_evaluated"])
        factors = int(run["literal_factors_evaluated"])
        total_vertices += vertices
        total_factor_evaluations += factors
        rows.append(
            {
                "n": variable_count,
                "pass": ok,
                "vertices_evaluated": vertices,
                "expected_2_pow_n": expected,
                "first_zero_index": run["first_zero_penalty_vertex_index_zero_based"],
                "literal_factors_evaluated": factors,
                "peak_retained_vertex_records": run["peak_retained_vertex_records"],
            }
        )
        previous_vertices = vertices
    return {
        "pass": passed,
        "family": "U_n=AND_i_x_i",
        "policy": "LEXICOGRAPHIC_FALSE_FIRST__STOP_AT_FIRST_ZERO_PENALTY",
        "unique_satisfying_vertex": "11...1",
        "n_range": [1, max_variables],
        "closed_form_vertices_at_n": "2^n",
        "recurrence": "V(1)=2; V(n+1)=2*V(n)",
        "largest_case": rows[-1],
        "aggregate_vertices_evaluated": total_vertices,
        "aggregate_literal_factors_evaluated": total_factor_evaluations,
        "rows": rows,
        "scope_firewall": "EXACT_COST_WITNESS_FOR_THIS_FROZEN_DIRECT_POLICY__NOT_A_LOWER_BOUND_ON_OTHER_SAT_ALGORITHMS",
    }


def invalid_input_controls() -> dict[str, object]:
    cases = [
        ("LITERAL_ZERO", lambda: normalize_cnf(2, ((0,),)), "LITERAL_OUT_OF_RANGE"),
        ("OUT_OF_RANGE", lambda: normalize_cnf(2, ((3,),)), "LITERAL_OUT_OF_RANGE"),
        ("WIDTH_FOUR", lambda: normalize_cnf(4, ((1, 2, 3, 4),)), "CLAUSE_WIDTH_EXCEEDS_3"),
        ("BAD_COUNT", lambda: normalize_cnf(-1, ()), "BAD_VARIABLE_COUNT"),
    ]
    rows = []
    passed = True
    for name, operation, expected in cases:
        caught = None
        try:
            operation()
        except AuditError as exc:
            caught = str(exc)
        ok = caught == expected
        passed = passed and ok
        rows.append({"id": name, "pass": ok, "caught": caught, "expected": expected})
    return {"pass": passed, "case_count": len(rows), "cases": rows}


def run_audit() -> dict[str, object]:
    hand = hand_controls()
    suite = deterministic_formula_suite()
    last_vertex = false_first_last_vertex_family()
    invalid = invalid_input_controls()
    syntax_probe = verify_multi_affine_syntax(
        compile_violation_terms(normalize_cnf(3, ((1, -2, 3), (-1, 2), (3,))))
    )
    all_controls_pass = bool(
        hand["pass"] and suite["pass"] and last_vertex["pass"] and invalid["pass"] and syntax_probe["pass"]
    )
    verdict = (
        "R32_TRANSFER_SPLIT_CONFIRMED__EYE_GOVERNANCE_RETAINED__DIRECT_VERTEX_ROUTE_REJECTED_AS_R31_POLYNOMIAL_SOLVER"
        if all_controls_pass
        else "R32_FAIL_IMPLEMENTATION_OR_SEMANTIC_CONTROL"
    )
    return {
        "schema": SCHEMA,
        "created_date": "2026-09-02",
        "source_git_commit": os.getenv("GITHUB_SHA", "LOCAL_OR_UNKNOWN"),
        "verdict": verdict,
        "all_controls_pass": all_controls_pass,
        "lineage": {
            "R32_preregistration_commit": PREREGISTRATION_COMMIT,
            "R32_preregistration_blob": PREREGISTRATION_BLOB,
            "parent_R31_contract_commit": R31_COMMIT,
            "EYE_R4_6_merge_commit": EYE_R46_MERGE_COMMIT,
            "EYE_R4_6_receipt_commit": EYE_R46_RECEIPT_COMMIT,
            "EYE_R4_6_main_run_id": EYE_R46_RUN_ID,
        },
        "captain_verdict": {
            "question": "IS_EYE_R4_6_THE_MISSING_ANSWER_FOR_TRUMP_R31",
            "answer": "PARTLY_AS_METHOD__NO_AS_POLYNOMIAL_SOLVER",
            "what_transfers": [
                "FREEZE_ATTACK_PRESERVE_BREAKER_REPLAN_REATTACK_GOVERNANCE",
                "MULTI_AFFINE_EXTREMA_AT_BOX_VERTICES_FOR_THE_DECLARED_OBJECT",
                "FAIL_CLOSED_WHEN_THE_EXACT_ADVERSARY_EXCEEDS_ITS_RESOURCE_ENVELOPE",
            ],
            "what_does_not_transfer": [
                "A_POLYNOMIAL_VERTEX_SELECTOR",
                "A_POLYNOMIAL_BOUND_WHEN_DIMENSION_GROWS_WITH_3SAT_INPUT",
                "A_PROOF_THAT_COUNTEREXAMPLE_GUIDED_REPLANNING_CONVERGES_IN_POLYNOMIALLY_MANY_ROUNDS",
            ],
            "our_stuck_point": "WE_CONFUSED_A_THEOREM_IDENTIFYING_WHERE_AN_EXTREMUM_EXISTS_WITH_AN_ALGORITHM_FINDING_THE_RELEVANT_VERTEX_CHEAPLY",
        },
        "transform_certificate": {
            "penalty": "P_F(x)=SUM_C PRODUCT_(l in C) q_l(x)",
            "positive_false_factor": "q_(x_i)=1-x_i",
            "negative_false_factor": "q_(NOT_x_i)=x_i",
            "serialized_size": "LINEAR_IN_NORMALIZED_LITERAL_OCCURRENCES",
            "syntactic_multi_affinity": syntax_probe,
            "boolean_semantics": "P_F(a)=NUMBER_OF_UNSATISFIED_CLAUSES_UNDER_a",
            "decision_equivalence": "F_IS_SAT_IFF_MIN_OVER_[0,1]^n_P_F=0",
        },
        "analytic_ledger": [
            {
                "id": "L1_MULTI_AFFINITY",
                "status": "ESTABLISHED_BY_EXPLICIT_TERM_SYNTAX",
                "reason": "Each normalized clause contains each variable at most once, and sums preserve degree-at-most-one per variable.",
            },
            {
                "id": "L2_VERTEX_EXTREMUM",
                "status": "ESTABLISHED_BY_COORDINATE_ENDPOINT_ARGUMENT",
                "reason": "With all other coordinates fixed, the penalty is affine in one coordinate; one endpoint is no worse for minimization. Repeat for all coordinates.",
            },
            {
                "id": "L3_BOOLEAN_CORRESPONDENCE",
                "status": "ESTABLISHED_AND_INDEPENDENTLY_REPLAYED_ON_CONTROLS",
                "reason": "Each product is one exactly when all literals in its clause are false.",
            },
            {
                "id": "L4_DIRECT_SEARCH_COST",
                "status": "EXACT_2_POW_n_ROUTE_COUNT_CONFIRMED",
                "reason": "The frozen direct policy visits every false-first vertex on U_n before the unique all-one witness.",
            },
            {
                "id": "L5_SELECTOR_CIRCULARITY",
                "status": "REDUCTION_BOUNDARY_RECORDED",
                "reason": "Selecting a zero-penalty vertex when one exists and soundly rejecting otherwise decides SAT; that selector is the missing algorithm, not a consequence of the vertex theorem.",
            },
        ],
        "controls": {
            "hand_cases": hand,
            "deterministic_formula_suite": suite,
            "false_first_last_vertex_family": last_vertex,
            "invalid_input_fail_closed": invalid,
        },
        "EYE_R4_6_default_envelope_boundary": {
            "max_dimensions": 16,
            "max_corners": 65536,
            "corners_at_dimension_16": 1 << 16,
            "first_uncovered_dimension": 17,
            "corners_at_dimension_17": 1 << 17,
            "boundary_status": "FINITE_DECLARED_ENVELOPE__NOT_A_UNIFORM_3SAT_BOUND",
        },
        "complexity_ledger": {
            "transform_build": "O(L)",
            "one_vertex_penalty_evaluation": "O(L)",
            "direct_full_vertex_route": "THETA(2^n * L)",
            "streaming_working_vertex_records": "O(1)_VERTEX_RECORDS_PLUS_O(L)_FORMULA",
            "direct_same_method_UNSAT_or_global_extremum_replay": "THETA(2^n * L)",
            "counterexample_guided_round_count": "UNBOUNDED_BY_EYE_R4_6_FOR_GENERAL_3SAT",
            "polynomial_claim": "REJECTED_FOR_THIS_DIRECT_TRANSFER",
        },
        "R31_obligation_impact": {
            "obligations_closed": 0,
            "O5_PROGRESS_AND_TERMINATION": "BLOCKED_FOR_DIRECT_ROUTE_BY_2_POW_n_VERTEX_COUNT",
            "O10_REJECTION_AND_REPLAY": "BLOCKED_FOR_DIRECT_SAME_METHOD_BY_2_POW_n_REPLAY",
            "O11_END_TO_END_POLYNOMIAL_BOUND": "BLOCKED_FOR_DIRECT_ROUTE",
            "O12_3SAT_TO_P_EQUALS_NP_BRIDGE": "NOT_AUTHORIZED",
            "other_obligations": "NOT_EVALUATED_BECAUSE_R32_ADMITS_NO_R31_CANDIDATE",
        },
        "preserved_transfer": {
            "EYE_role": "ADVERSARIAL_FALSIFIER_AND_COUNTERMODEL_GENERATOR",
            "TRUMP_role": "POLICY_LANE_AND_CANDIDATE_ROUTING",
            "VERIFY_role": "INDEPENDENT_CONTROL_WITH_POWER_TO_SAY_NO",
            "authority": "ADVISORY_RESEARCH_ONLY",
        },
        "next_gate": {
            "id": "R33_POLICY_SELECTED_VERTEX_OR_FACE_COLLAPSE_CANDIDATE_INTAKE",
            "status": "BLOCKED_PENDING_EXPLICIT_POLICY_AND_SYMBOLIC_RECURRENCE",
            "required_object": "A_TRUTH_BLIND_UNIFORM_POLICY_SELECTING_OR_COLLAPSING_ONLY_POLY(L)_FACES_OR_STATES_WHILE_PRESERVING_SAT_AND_RECOVERING_A_WITNESS_OR_SOUND_REJECTION",
            "implementation_authorized": False,
            "rule": "NO_R33_CODE_UNTIL_BUILD_CHOOSE_STEP_TERMINAL_RECOVER_AND_THE_POLYNOMIAL_BOUND_ARE_WRITTEN",
        },
        "firewalls": [
            "EYE_AND_TRUMP_REMAIN_DISTINCT_ORGANS",
            "VERTEX_EXTREMUM_THEOREM != POLYNOMIAL_VERTEX_SELECTION",
            "EXACT_2_POW_n_ENUMERATION != P",
            "FINITE_CONTROLS != ASYMPTOTIC_COMPLEXITY_PROOF",
            "THIS_POLICY_COST_WITNESS != LOWER_BOUND_ON_ALL_SAT_ALGORITHMS",
            "RESEARCH_SUCCESS != RUNTIME_AUTHORITY",
            "P_VS_NP = OPEN",
        ],
        "claim_ceiling": "Exact transfer/complexity audit of the direct EYE-R4.6 vertex route. No general SAT lower bound, SAT-in-P, P=NP, P!=NP, release, or runtime-authority conclusion.",
        "TRUMP_finished": False,
        "SAT_IN_P": "NOT_PROVED",
        "P_VS_NP": "OPEN",
        "runtime_authority": False,
    }


def write_result(path: Path, result: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_self_test() -> None:
    result = run_audit()
    assert result["verdict"].startswith("R32_TRANSFER_SPLIT_CONFIRMED")
    assert result["all_controls_pass"] is True
    assert result["controls"]["hand_cases"]["pass"] is True
    assert result["controls"]["deterministic_formula_suite"]["formula_count"] == 192
    assert result["controls"]["false_first_last_vertex_family"]["largest_case"]["vertices_evaluated"] == 1 << 18
    assert result["EYE_R4_6_default_envelope_boundary"]["corners_at_dimension_17"] == 131072
    assert result["R31_obligation_impact"]["obligations_closed"] == 0
    assert result["TRUMP_finished"] is False
    assert result["SAT_IN_P"] == "NOT_PROVED"
    assert result["P_VS_NP"] == "OPEN"
    print(
        json.dumps(
            {
                "status": "PASS",
                "verdict": result["verdict"],
                "formula_controls": result["controls"]["deterministic_formula_suite"]["formula_count"],
                "largest_exact_policy_cost": result["controls"]["false_first_last_vertex_family"]["largest_case"],
            },
            sort_keys=True,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
        return
    if args.output is None:
        parser.error("--output is required unless --self-test is used")
    result = run_audit()
    write_result(args.output, result)
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "all_controls_pass": result["all_controls_pass"],
                "TRUMP_finished": result["TRUMP_finished"],
                "SAT_IN_P": result["SAT_IN_P"],
                "P_VS_NP": result["P_VS_NP"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
