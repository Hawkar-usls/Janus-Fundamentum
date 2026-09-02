from __future__ import annotations

import argparse
import itertools
import json
import os
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r42_subsumption_aware_bve_successor as r42

Clause = Tuple[int, ...]
Formula = Tuple[Clause, ...]

R42_CONTROLLER_BLOB_SHA = "d71d7edb284a37bc7d7039c0d585d64cf2844de9"


def exactify_binary_clauses(clauses: Iterable[Sequence[int]], first_fresh: int) -> Formula:
    out: List[Tuple[int, ...]] = []
    fresh = first_fresh
    for raw in clauses:
        clause = tuple(int(x) for x in raw)
        if len(clause) == 3:
            out.append(clause)
        elif len(clause) == 2:
            a, b = clause
            z = fresh
            fresh += 1
            out.append((a, b, z))
            out.append((a, b, -z))
        else:
            raise AssertionError(("R43_ONLY_BINARY_OR_TERNARY_ENCODING_ALLOWED", clause))
    formula = r33.canonical_formula(out)
    if not formula or any(len(c) != 3 or r33.is_tautology(c) for c in formula):
        raise AssertionError("R43 exact-3CNF encoding integrity failure")
    return formula


def k_color3_exact_3cnf(n_vertices: int) -> Formula:
    if n_vertices < 1:
        raise ValueError(n_vertices)

    def x(v: int, color: int) -> int:
        return v * 3 + color + 1

    clauses: List[Tuple[int, ...]] = []
    for v in range(n_vertices):
        clauses.append((x(v, 0), x(v, 1), x(v, 2)))
        for a, b in itertools.combinations(range(3), 2):
            clauses.append((-x(v, a), -x(v, b)))
    for u, v in itertools.combinations(range(n_vertices), 2):
        for color in range(3):
            clauses.append((-x(u, color), -x(v, color)))
    return exactify_binary_clauses(clauses, first_fresh=n_vertices * 3 + 1)


def php_4_to_3_exact_3cnf() -> Formula:
    pigeons, holes = 4, 3

    def x(p: int, h: int) -> int:
        return p * holes + h + 1

    clauses: List[Tuple[int, ...]] = []
    for p in range(pigeons):
        clauses.append(tuple(x(p, h) for h in range(holes)))
        for h1, h2 in itertools.combinations(range(holes), 2):
            clauses.append((-x(p, h1), -x(p, h2)))
    for h in range(holes):
        for p1, p2 in itertools.combinations(range(pigeons), 2):
            clauses.append((-x(p1, h), -x(p2, h)))
    return exactify_binary_clauses(clauses, first_fresh=pigeons * holes + 1)


def validate_exact_3cnf(formula: Formula) -> None:
    if not formula:
        raise AssertionError("empty search input")
    for clause in formula:
        if len(clause) != 3:
            raise AssertionError(("NOT_EXACT_3CNF", clause))
        if r33.is_tautology(clause):
            raise AssertionError(("TAUTOLOGICAL_SEARCH_INPUT", clause))


def frozen_search_cases():
    yield "STRUCTURED_K4_3COLOR_EXACT_3CNF", None, k_color3_exact_3cnf(4)
    yield "STRUCTURED_K5_3COLOR_EXACT_3CNF", None, k_color3_exact_3cnf(5)
    yield "STRUCTURED_PHP_4_TO_3_EXACT_3CNF", None, php_4_to_3_exact_3cnf()

    grids = (
        (43001, 43032, 48, 4.3, "RANDOM_GRID_A"),
        (43101, 43116, 64, 4.3, "RANDOM_GRID_B"),
        (43201, 43216, 48, 3.8, "RANDOM_GRID_C"),
        (43301, 43316, 48, 4.8, "RANDOM_GRID_D"),
    )
    for start, end, n, ratio, prefix in grids:
        for seed in range(start, end + 1):
            formula = r33.deterministic_random_3cnf(seed, n=n, ratio=ratio)
            yield f"{prefix}_SEED_{seed}_N{n}_R{ratio}", seed, formula


def compact_row(label: str, seed, formula: Formula, result: dict) -> dict:
    return {
        "label": label,
        "seed": seed,
        "input_formula_sha256": r42.formula_hash(formula),
        "input_measure_CLV": list(r33.measure(formula)),
        "terminal_status": result["terminal_status"],
        "semantic_decided": result["semantic_decided"],
        "semantic_sat": result["semantic_sat"],
        "SA_BVE_applications": result["SA_BVE_applications"],
        "cycle_count": result["cycle_count"],
        "terminal_formula_sha256": result["terminal_formula_hash"],
        "terminal_measure_CLV": result["terminal_measure_CLV"],
        "SAT_model_replay_pass": result["final_original_model_replay"]["pass"] if result["semantic_sat"] is True else None,
    }


def run_hunt() -> dict:
    tested = []
    first_counterexample = None
    integrity_error = None

    for ordinal, (label, seed, formula) in enumerate(frozen_search_cases(), 1):
        try:
            validate_exact_3cnf(formula)
            result = r42.run_fixed_successor(formula, label)
        except Exception as exc:  # integrity failure is never converted into a scientific counterexample
            integrity_error = {
                "ordinal": ordinal,
                "label": label,
                "seed": seed,
                "exception_type": type(exc).__name__,
                "message": str(exc),
            }
            break

        row = compact_row(label, seed, formula, result)
        tested.append(row)
        if not result["semantic_decided"]:
            first_counterexample = {
                "ordinal": ordinal,
                "label": label,
                "seed": seed,
                "input_formula_sha256": row["input_formula_sha256"],
                "input_measure_CLV": row["input_measure_CLV"],
                "input_formula": [list(c) for c in formula],
                "controller_terminal_status": result["terminal_status"],
                "terminal_formula_sha256": result["terminal_formula_hash"],
                "terminal_measure_CLV": result["terminal_measure_CLV"],
                "cycle_count": result["cycle_count"],
                "SA_BVE_applications": result["SA_BVE_applications"],
                "reason": "BYTE_PINNED_R42_CONTROLLER_HALTED_WITHOUT_SEMANTIC_DECISION",
            }
            break

    if integrity_error is not None:
        verdict = "R43_FAIL_INTEGRITY"
    elif first_counterexample is not None:
        verdict = "R43_COUNTEREXAMPLE_FOUND__R42_SUCCESSOR_REFUTED_FOR_L2"
    else:
        verdict = "R43_NO_COUNTEREXAMPLE_IN_FROZEN_FINITE_SEARCH__L2_STILL_OPEN"

    return {
        "schema": "JANUS_TRUMP_R43_FROZEN_R42_CONTROLLER_COUNTEREXAMPLE_HUNT_RESULT",
        "version": "1.0",
        "date": "2026-09-02",
        "source_git_commit": os.environ.get("GITHUB_SHA", "LOCAL"),
        "verdict": verdict,
        "frozen_controller": {
            "id": "TRUMP_R42_FIXED_SUCCESSOR_R33_R34_R35B_SA_BVE_v1",
            "source_blob_sha": R42_CONTROLLER_BLOB_SHA,
            "modified_during_R43": False,
        },
        "frozen_search_plan": {
            "structured_count": 3,
            "random_grid_count": 80,
            "maximum_case_count": 83,
            "first_counterexample_stops_search": True,
        },
        "tested_count": len(tested),
        "tested": tested,
        "semantic_decision_count": sum(bool(x["semantic_decided"]) for x in tested),
        "first_counterexample": first_counterexample,
        "integrity_error": integrity_error,
        "claim_ceiling": {
            "no_counterexample_in_this_finite_search_may_close_L2": False,
            "counterexample_refutes_only_this_frozen_R42_controller": first_counterexample is not None,
            "L2_UNIVERSAL_3CNF_COVERAGE": False,
            "L3_ONE_UNIFORM_TOTAL_TRUMP_RESOLVER": False,
            "L4_WORST_CASE_POLYNOMIAL_UNIFORM_TRUMP_RESOLVER": False,
        },
        "captain_verdict": {
            "if_counterexample": "SEAL FIRST STALL. DO NOT PATCH R42. EXTRACT A CLASS-LEVEL FAILURE MECHANISM FOR A NEW SUCCESSOR.",
            "if_none": "FINITE SILENCE IS NOT A THEOREM. ATTACK THE SYMBOLIC DECIDE-or-DESCEND OBLIGATION FOR THE SAME SNAPSHOT.",
        },
        "TRUMP_finished": False,
        "SAT_IN_P": "NOT_PROVED",
        "P_VS_NP": "OPEN",
        "runtime_authority": False,
    }


def self_test() -> None:
    k4 = k_color3_exact_3cnf(4)
    k5 = k_color3_exact_3cnf(5)
    php = php_4_to_3_exact_3cnf()
    for f in (k4, k5, php):
        validate_exact_3cnf(f)
    assert len(tuple(frozen_search_cases())) == 83
    print("R43_SELF_TEST_PASS", {"K4": list(r33.measure(k4)), "K5": list(r33.measure(k5)), "PHP4x3": list(r33.measure(php)), "cases": 83})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    text = json.dumps(run_hunt(), indent=2, sort_keys=True) + "\n"
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
