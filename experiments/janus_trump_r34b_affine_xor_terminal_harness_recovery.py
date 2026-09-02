from __future__ import annotations

import argparse
import itertools
import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r34_affine_xor_terminal_against_tseitin_core as r34

Clause = Tuple[int, ...]
Formula = Tuple[Clause, ...]


def even_charge_prism_tseitin(n_vertices: int) -> Formula:
    """Connected 3-regular prism Tseitin instance with total charge 0 (SAT)."""
    if n_vertices < 8 or n_vertices % 2:
        raise ValueError("prism family requires even n >= 8")
    k = n_vertices // 2
    edges: List[Tuple[int, int]] = []

    def add_edge(u: int, v: int) -> None:
        if u > v:
            u, v = v, u
        if (u, v) not in edges:
            edges.append((u, v))

    for i in range(k):
        add_edge(i, (i + 1) % k)
        add_edge(k + i, k + ((i + 1) % k))
        add_edge(i, k + i)

    incident: Dict[int, List[int]] = defaultdict(list)
    for edge_var, (u, v) in enumerate(edges, 1):
        incident[u].append(edge_var)
        incident[v].append(edge_var)

    clauses: List[Clause] = []
    for vertex in range(n_vertices):
        xs = sorted(incident[vertex])
        if len(xs) != 3:
            raise AssertionError("prism must be 3-regular")
        target = 0
        for bits in itertools.product((0, 1), repeat=3):
            if sum(bits) % 2 == target:
                continue
            clauses.append(tuple(x if bit == 0 else -x for x, bit in zip(xs, bits)))
    return r33.canonical_formula(clauses)


def frozen_r33_positive_controls() -> list[dict]:
    return [
        r33.semantic_control("EASY_REDUNDANT_TAIL", r33.easy_redundant_tail(), "UNIT_PROPAGATION_WITH_RECONSTRUCTION_TRACE"),
        r33.semantic_control("BLOCKED_CLAUSE_CONTROL", r33.blocked_clause_control(), "BLOCKED_CLAUSE_ELIMINATION"),
        r33.semantic_control("BVE_CONTROL", r33.bve_control(), "BOUNDED_VARIABLE_ELIMINATION"),
    ]


def run_audit() -> dict:
    positive = frozen_r33_positive_controls()

    sat_formula = even_charge_prism_tseitin(8)
    sat_result = r34.apply_extended_policy(sat_formula)
    sat_control = {
        "id": "CONNECTED_EVEN_CHARGE_TSEITIN_PRISM_SAT",
        "n_vertices": 8,
        "initial_measure": list(r33.measure(sat_formula)),
        "R33_terminal": sat_result["R33"]["terminal"],
        "R33_rule_applications": sat_result["R33"]["total_rule_applications"],
        "R34_terminal": sat_result["terminal"],
        "recognized": sat_result.get("recognition", {}).get("recognized", False),
        "equation_count": sat_result.get("recognition", {}).get("equation_count"),
        "certificate_pass": sat_result.get("verification", {}).get("pass"),
        "certificate_kind": sat_result.get("verification", {}).get("kind"),
        "row_xors": sat_result.get("solution", {}).get("row_xors"),
        "estimated_bit_ops": sat_result.get("solution", {}).get("estimated_bit_ops"),
    }

    odd_tseitin = []
    for n in (8, 12, 16, 20, 24, 28, 32):
        formula = r33.prism_tseitin(n)
        result = r34.apply_extended_policy(formula)
        odd_tseitin.append({
            "n_vertices": n,
            "initial_measure": list(r33.measure(formula)),
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
        formula = r33.deterministic_random_3cnf(seed)
        result = r34.apply_extended_policy(formula)
        random_controls.append({
            "seed": seed,
            "initial_measure": list(r33.measure(formula)),
            "R33_final_measure": result["R33"]["final_measure"],
            "R33_rule_applications": result["R33"]["total_rule_applications"],
            "R34_terminal": result["terminal"],
            "affine_recognized": result.get("recognition", {}).get("recognized", False),
            "recognition_reason": result.get("recognition", {}).get("reason"),
            "recognition_failed_vars": result.get("recognition", {}).get("failed_vars"),
        })

    positive_ok = all(x["pass"] for x in positive)
    sat_ok = (
        sat_control["R33_terminal"] == "STALLED_STACK_LEAN_CORE"
        and sat_control["R33_rule_applications"] == 0
        and sat_control["R34_terminal"] == "AFFINE_XOR_SAT"
        and sat_control["recognized"]
        and sat_control["certificate_pass"]
    )
    tseitin_ok = all(
        x["R33_terminal"] == "STALLED_STACK_LEAN_CORE"
        and x["R33_rule_applications"] == 0
        and x["R34_terminal"] == "AFFINE_XOR_UNSAT"
        and x["recognized"]
        and x["certificate_pass"]
        for x in odd_tseitin
    )
    nonaffine = [x for x in random_controls if x["R34_terminal"] == "STALLED_NONAFFINE_CORE"]

    if not positive_ok:
        verdict = "R34B_FAIL_INTEGRITY"
    elif not sat_ok or not tseitin_ok:
        verdict = "R34B_AFFINE_MECHANISM_CERTIFICATE_MISMATCH"
    elif nonaffine:
        verdict = "R34B_AFFINE_TERMINAL_CLOSES_TSEITIN_CORE__NONAFFINE_CORE_REMAINS__NO_UNIVERSAL_CLAIM"
    else:
        verdict = "R34B_AFFINE_TERMINAL_CLOSES_ALL_FROZEN_CORES__NO_UNIVERSAL_CLAIM"

    smallest_nonaffine = None
    if nonaffine:
        smallest_nonaffine = min(
            nonaffine,
            key=lambda x: (tuple(x["R33_final_measure"]), x["seed"]),
        )

    return {
        "schema": "JANUS_TRUMP_R34B_AFFINE_XOR_TERMINAL_HARNESS_RECOVERY_RESULT",
        "version": "1.0",
        "date": "2026-09-02",
        "source_git_commit": os.environ.get("GITHUB_SHA", "LOCAL"),
        "verdict": verdict,
        "frozen_mechanism_provenance": {
            "module": "experiments/janus_trump_r34_affine_xor_terminal_against_tseitin_core.py",
            "R34_implementation_commit": "55c5bc02ffd9c26eb288897ceebf36ea3a0bc49f",
            "R34_implementation_blob": "7f9bec920fa47af066570d874fe9127dc4b9b968",
            "mechanism_modified_in_R34B": False,
        },
        "candidate_firewall": {
            "R33_stack_modified": False,
            "R34_affine_mechanism_modified": False,
            "external_SAT_solver_used": False,
            "second_new_mechanism_added": False,
            "only_harness_change": "CONNECTED_EVEN_CHARGE_TSEITIN_PRISM_SAT",
        },
        "R33_positive_controls": [
            {"name": x["name"], "pass": x["pass"], "required_rule": x["required_rule"], "required_rule_seen": x["required_rule_seen"]}
            for x in positive
        ],
        "connected_even_charge_tseitin_sat_control": sat_control,
        "odd_charge_tseitin_3regular_prism_family": odd_tseitin,
        "deterministic_random_3cnf": random_controls,
        "smallest_nonaffine_stalled_control_by_frozen_measure": smallest_nonaffine,
        "captain_verdict": {
            "answer": "AFFINE_XOR_IS_A_VALID_POLYNOMIAL_TERMINAL_FOR_THE_SEALED_TSEITIN_LANGUAGE__THE_FRONTIER_MOVES_TO_NONAFFINE_CORES",
            "lesson": "The theta/truncation idea works here only through certified recognition of a tractable residual language. It does not provide universal truncation of arbitrary 3-CNF.",
        },
        "R31_obligation_impact": {
            "obligations_closed": 0,
            "reason": "One structured terminal family is closed, but universal progress remains unproved.",
        },
        "next_gate": {
            "id": "R35_FREEZE_SMALLEST_NONAFFINE_RANDOM_CORE_AND_PROPOSE_AT_MOST_ONE_NEW_MECHANISM",
            "authorized": bool(nonaffine),
            "instruction": "Seal the smallest non-affine stalled core. R35 may propose exactly one new polynomially checkable proof-carrying structural mechanism after preregistration; do not add it to R34B.",
        },
        "TRUMP_finished": False,
        "SAT_IN_P": "NOT_PROVED",
        "P_VS_NP": "OPEN",
        "runtime_authority": False,
    }


def self_test() -> None:
    d = run_audit()
    assert d["verdict"] == "R34B_AFFINE_TERMINAL_CLOSES_TSEITIN_CORE__NONAFFINE_CORE_REMAINS__NO_UNIVERSAL_CLAIM"
    sat = d["connected_even_charge_tseitin_sat_control"]
    assert sat["R33_terminal"] == "STALLED_STACK_LEAN_CORE"
    assert sat["R33_rule_applications"] == 0
    assert sat["R34_terminal"] == "AFFINE_XOR_SAT"
    assert sat["recognized"] and sat["certificate_pass"]
    assert all(
        x["R34_terminal"] == "AFFINE_XOR_UNSAT" and x["recognized"] and x["certificate_pass"]
        for x in d["odd_charge_tseitin_3regular_prism_family"]
    )
    assert d["smallest_nonaffine_stalled_control_by_frozen_measure"] is not None
    print("R34B_SELF_TEST_PASS")


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
