from __future__ import annotations

import argparse
import itertools
import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33

Clause = Tuple[int, ...]
Formula = Tuple[Clause, ...]
Equation = Tuple[Tuple[int, ...], int]


def recognize_complete_affine_cnf(formula: Formula) -> dict:
    """Recognize a whole CNF that is exactly a conjunction of complete XOR bundles.

    A width-k clause corresponds to one falsifying 0/1 assignment on its k variables.
    A complete XOR bundle contains exactly all 2^(k-1) assignments of one parity;
    therefore its conjunction enforces the opposite parity.  Recognition scans only
    clauses already present in the input and never enumerates the 2^k cube.
    """
    groups: Dict[Tuple[int, ...], List[Clause]] = defaultdict(list)
    literal_inspections = 0
    for clause in formula:
        if not clause:
            return {"recognized": False, "reason": "EMPTY_CLAUSE_NOT_AFFINE_BUNDLE", "literal_inspections": literal_inspections}
        vs = tuple(sorted(abs(l) for l in clause))
        literal_inspections += len(clause)
        if len(set(vs)) != len(vs):
            return {"recognized": False, "reason": "REPEATED_VARIABLE_IN_CLAUSE", "literal_inspections": literal_inspections}
        groups[vs].append(clause)

    equations: List[Equation] = []
    group_receipts = []
    for vs in sorted(groups):
        clauses = groups[vs]
        k = len(vs)
        if len(clauses) != (1 << (k - 1)):
            return {"recognized": False, "reason": "INCOMPLETE_PARITY_BUNDLE", "failed_vars": list(vs), "group_clause_count": len(clauses), "required_clause_count": 1 << (k - 1), "literal_inspections": literal_inspections}
        falsifying_assignments = set()
        parities = set()
        for clause in clauses:
            sign_by_var = {abs(l): l for l in clause}
            literal_inspections += len(clause)
            if tuple(sorted(sign_by_var)) != vs:
                return {"recognized": False, "reason": "VARIABLE_SET_MISMATCH", "failed_vars": list(vs), "literal_inspections": literal_inspections}
            bits = tuple(1 if sign_by_var[v] < 0 else 0 for v in vs)
            falsifying_assignments.add(bits)
            parities.add(sum(bits) & 1)
        if len(falsifying_assignments) != len(clauses) or len(parities) != 1:
            return {"recognized": False, "reason": "NOT_ONE_COMPLETE_PARITY_CLASS", "failed_vars": list(vs), "literal_inspections": literal_inspections}
        bad_parity = next(iter(parities))
        rhs = bad_parity ^ 1
        equations.append((vs, rhs))
        group_receipts.append({"vars": list(vs), "clause_count": len(clauses), "bad_parity": bad_parity, "equation_rhs": rhs})

    return {
        "recognized": True,
        "reason": "COMPLETE_AFFINE_CNF",
        "equations": equations,
        "group_receipts": group_receipts,
        "literal_inspections": literal_inspections,
        "equation_count": len(equations),
        "variable_count": len({v for vs, _ in equations for v in vs}),
    }


def solve_gf2_with_certificate(equations: List[Equation]) -> dict:
    var_order = sorted({v for vs, _ in equations for v in vs})
    pos = {v: i for i, v in enumerate(var_order)}
    rows = []
    for source_index, (vs, rhs) in enumerate(equations):
        mask = 0
        for v in vs:
            mask ^= 1 << pos[v]
        rows.append([mask, int(rhs), 1 << source_index])

    pivot_row = 0
    pivots: List[Tuple[int, int]] = []
    row_xors = 0
    swaps = 0
    for col, _ in enumerate(var_order):
        candidate = next((j for j in range(pivot_row, len(rows)) if (rows[j][0] >> col) & 1), None)
        if candidate is None:
            continue
        if candidate != pivot_row:
            rows[pivot_row], rows[candidate] = rows[candidate], rows[pivot_row]
            swaps += 1
        for j in range(len(rows)):
            if j != pivot_row and ((rows[j][0] >> col) & 1):
                rows[j][0] ^= rows[pivot_row][0]
                rows[j][1] ^= rows[pivot_row][1]
                rows[j][2] ^= rows[pivot_row][2]
                row_xors += 1
        pivots.append((pivot_row, col))
        pivot_row += 1

    estimated_bit_ops = row_xors * max(1, len(var_order) + len(equations) + 1)
    for mask, rhs, combo in rows:
        if mask == 0 and rhs == 1:
            source_indices = [i for i in range(len(equations)) if (combo >> i) & 1]
            return {
                "sat": False,
                "certificate": {"kind": "GF2_ZERO_EQUALS_ONE", "source_equation_indices": source_indices},
                "row_xors": row_xors,
                "row_swaps": swaps,
                "estimated_bit_ops": estimated_bit_ops,
                "rank": len(pivots),
                "variable_order": var_order,
            }

    assignment = {v: False for v in var_order}
    for row_index, col in pivots:
        mask, rhs, _ = rows[row_index]
        value = bool(rhs)
        remainder = mask & ~(1 << col)
        while remainder:
            lowbit = remainder & -remainder
            other_col = lowbit.bit_length() - 1
            value ^= assignment[var_order[other_col]]
            remainder ^= lowbit
        assignment[var_order[col]] = value
    return {
        "sat": True,
        "assignment": assignment,
        "row_xors": row_xors,
        "row_swaps": swaps,
        "estimated_bit_ops": estimated_bit_ops,
        "rank": len(pivots),
        "variable_order": var_order,
    }


def verify_affine_certificate(formula: Formula, recognition: dict, solution: dict) -> dict:
    equations: List[Equation] = recognition["equations"]
    if solution["sat"]:
        assignment = {int(v): bool(b) for v, b in solution["assignment"].items()}
        equations_ok = all((sum(1 for v in vs if assignment.get(v, False)) & 1) == rhs for vs, rhs in equations)
        cnf_ok = r33.eval_formula(formula, assignment)
        return {"pass": equations_ok and cnf_ok, "kind": "SAT_ASSIGNMENT", "equations_ok": equations_ok, "cnf_ok": cnf_ok}

    indices = solution["certificate"]["source_equation_indices"]
    parity_vars = set()
    rhs = 0
    for i in indices:
        vs, r = equations[i]
        for v in vs:
            if v in parity_vars:
                parity_vars.remove(v)
            else:
                parity_vars.add(v)
        rhs ^= r
    ok = not parity_vars and rhs == 1
    return {"pass": ok, "kind": "GF2_ZERO_EQUALS_ONE", "selected_equations": indices, "residual_variables": sorted(parity_vars), "rhs": rhs}


def apply_extended_policy(formula: Formula) -> dict:
    frozen = r33.simplify(formula)
    if frozen["terminal"] != "STALLED_STACK_LEAN_CORE":
        return {"terminal": frozen["terminal"], "R33": frozen, "new_mechanism_invoked": False}
    core = r33.canonical_formula(frozen["final_formula"])
    recognition = recognize_complete_affine_cnf(core)
    if not recognition["recognized"]:
        return {"terminal": "STALLED_NONAFFINE_CORE", "R33": frozen, "new_mechanism_invoked": True, "recognition": recognition}
    solution = solve_gf2_with_certificate(recognition["equations"])
    verification = verify_affine_certificate(core, recognition, solution)
    if not verification["pass"]:
        return {"terminal": "FAIL_CERTIFICATE", "R33": frozen, "new_mechanism_invoked": True, "recognition": recognition, "solution": solution, "verification": verification}
    return {"terminal": "AFFINE_XOR_SAT" if solution["sat"] else "AFFINE_XOR_UNSAT", "R33": frozen, "new_mechanism_invoked": True, "recognition": recognition, "solution": solution, "verification": verification}


def xor_bundle(vs: Iterable[int], rhs: int) -> Formula:
    variables = tuple(sorted(vs))
    clauses = []
    for bits in itertools.product((0, 1), repeat=len(variables)):
        if (sum(bits) & 1) == rhs:
            continue
        clauses.append(tuple(v if bit == 0 else -v for v, bit in zip(variables, bits)))
    return r33.canonical_formula(clauses)


def affine_sat_control() -> Formula:
    return r33.canonical_formula(list(xor_bundle((1, 2, 3), 0)) + list(xor_bundle((3, 4, 5), 1)))


def run_audit() -> dict:
    r33_positive = [
        r33.semantic_control("EASY_REDUNDANT_TAIL", r33.easy_redundant_tail(), "UNIT_PROPAGATION_WITH_RECONSTRUCTION_TRACE"),
        r33.semantic_control("BLOCKED_CLAUSE_CONTROL", r33.blocked_clause_control(), "BLOCKED_CLAUSE_ELIMINATION"),
        r33.semantic_control("BVE_CONTROL", r33.bve_control(), "BOUNDED_VARIABLE_ELIMINATION"),
    ]

    affine_sat = apply_extended_policy(affine_sat_control())

    tseitin = []
    for n in (8, 12, 16, 20, 24, 28, 32):
        f = r33.prism_tseitin(n)
        result = apply_extended_policy(f)
        tseitin.append({
            "n_vertices": n,
            "initial_measure": list(r33.measure(f)),
            "R33_terminal": result["R33"]["terminal"],
            "R33_rule_applications": result["R33"]["total_rule_applications"],
            "R34_terminal": result["terminal"],
            "recognized": result.get("recognition", {}).get("recognized", False),
            "equation_count": result.get("recognition", {}).get("equation_count"),
            "certificate_pass": result.get("verification", {}).get("pass"),
            "certificate_kind": result.get("verification", {}).get("kind"),
            "certificate_equation_count": len(result.get("solution", {}).get("certificate", {}).get("source_equation_indices", [])),
            "row_xors": result.get("solution", {}).get("row_xors"),
            "estimated_bit_ops": result.get("solution", {}).get("estimated_bit_ops"),
        })

    random_controls = []
    for seed in (33001, 33002, 33003, 33004):
        f = r33.deterministic_random_3cnf(seed)
        result = apply_extended_policy(f)
        random_controls.append({
            "seed": seed,
            "initial_measure": list(r33.measure(f)),
            "R33_final_measure": result["R33"]["final_measure"],
            "R33_rule_applications": result["R33"]["total_rule_applications"],
            "R34_terminal": result["terminal"],
            "affine_recognized": result.get("recognition", {}).get("recognized", False),
            "recognition_reason": result.get("recognition", {}).get("reason"),
        })

    positive_ok = all(x["pass"] for x in r33_positive)
    affine_sat_ok = affine_sat["terminal"] == "AFFINE_XOR_SAT" and affine_sat.get("verification", {}).get("pass") is True
    tseitin_ok = all(x["R33_terminal"] == "STALLED_STACK_LEAN_CORE" and x["R33_rule_applications"] == 0 and x["R34_terminal"] == "AFFINE_XOR_UNSAT" and x["recognized"] and x["certificate_pass"] for x in tseitin)
    any_nonaffine_stall = any(x["R34_terminal"] == "STALLED_NONAFFINE_CORE" for x in random_controls)

    if not (positive_ok and affine_sat_ok):
        verdict = "R34_FAIL_INTEGRITY"
    elif not tseitin_ok:
        verdict = "R34_AFFINE_TERMINAL_FAILS_TO_CLOSE_SOME_TSEITIN_CORES"
    elif any_nonaffine_stall:
        verdict = "R34_AFFINE_TERMINAL_CLOSES_TSEITIN_CORE__NONAFFINE_CORE_REMAINS__NO_UNIVERSAL_CLAIM"
    else:
        verdict = "R34_AFFINE_TERMINAL_CLOSES_ALL_FROZEN_CORES__NO_UNIVERSAL_CLAIM"

    return {
        "schema": "JANUS_TRUMP_R34_AFFINE_XOR_TERMINAL_AGAINST_TSEITIN_CORE_RESULT",
        "version": "1.0",
        "date": "2026-09-02",
        "source_git_commit": os.environ.get("GITHUB_SHA", "LOCAL"),
        "verdict": verdict,
        "single_new_mechanism": "AFFINE_XOR_TERMINAL_RECOGNITION_AND_GF2_CERTIFIED_SOLVE",
        "candidate_firewall": {
            "R33_stack_modified": False,
            "external_SAT_solver_used": False,
            "assignment_enumeration_inside_recognizer_or_GF2_solver": False,
            "partial_XOR_plus_search_used": False,
            "second_new_mechanism_added": False,
        },
        "R33_positive_controls": [{"name": x["name"], "pass": x["pass"], "required_rule": x["required_rule"], "required_rule_seen": x["required_rule_seen"]} for x in r33_positive],
        "affine_sat_control": {
            "terminal": affine_sat["terminal"],
            "recognized": affine_sat.get("recognition", {}).get("recognized", False),
            "equation_count": affine_sat.get("recognition", {}).get("equation_count"),
            "verification": affine_sat.get("verification"),
            "row_xors": affine_sat.get("solution", {}).get("row_xors"),
        },
        "tseitin_3regular_prism_family": tseitin,
        "deterministic_random_3cnf": random_controls,
        "captain_verdict": {
            "answer": "THE_R33_CORE_WAS_A_POLYNOMIAL_AFFINE_LANGUAGE__THE_SINGLE_XOR_TERMINAL_CLOSES_IT__GENERAL_3CNF_STILL_HAS_NONAFFINE_CORES",
            "lesson": "Recognizing a sealed core's exact tractable language is valid progress. It does not establish that every future core belongs to one of the current terminal classes.",
        },
        "R31_obligation_impact": {"obligations_closed": 0, "reason": "R34 closes one adversarial family under an extended fixed policy but does not prove universal progress for arbitrary 3-CNF."},
        "next_gate": {
            "id": "R35_FREEZE_SMALLEST_NONAFFINE_RANDOM_CORE_AND_PROPOSE_AT_MOST_ONE_NEW_MECHANISM",
            "authorized_only_if_nonaffine_stall": any_nonaffine_stall,
            "instruction": "Preserve the first deterministic non-affine stalled core byte-for-byte. Do not add a second R34 mechanism. R35 must preregister one new structural explanation or certified rule before implementation."
        },
        "TRUMP_finished": False,
        "SAT_IN_P": "NOT_PROVED",
        "P_VS_NP": "OPEN",
        "runtime_authority": False,
    }


def self_test() -> None:
    d = run_audit()
    assert d["verdict"] == "R34_AFFINE_TERMINAL_CLOSES_TSEITIN_CORE__NONAFFINE_CORE_REMAINS__NO_UNIVERSAL_CLAIM"
    assert d["affine_sat_control"]["terminal"] == "AFFINE_XOR_SAT"
    assert d["affine_sat_control"]["verification"]["pass"] is True
    assert all(x["R34_terminal"] == "AFFINE_XOR_UNSAT" and x["certificate_pass"] for x in d["tseitin_3regular_prism_family"])
    assert any(x["R34_terminal"] == "STALLED_NONAFFINE_CORE" for x in d["deterministic_random_3cnf"])
    print("R34_SELF_TEST_PASS")


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
        p = Path(args.output)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
