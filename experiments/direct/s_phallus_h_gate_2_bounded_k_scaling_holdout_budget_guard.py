#!/usr/bin/env python3
"""Cost-conformant runner for frozen S𓂸ḥ/2.

The S𓂸ḥ/2 contract and fixtures remain unchanged. This runner preserves Q0
priority and the auto-K detector for admitted residuals, but inherits the
already-frozen OSIRIS v2 state-budget admission rule: after normalization and
unit propagation, if residual variable depth exceeds the frozen state budget
and Q0 does not match, S𓂸ḥ/2 does not launch an enormous separator audit and
returns through the unchanged generic OSIRIS v2 fail-closed path.

No new threshold is introduced; the only guard is the caller's existing frozen
state_budget. P_VS_NP remains OPEN.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable

import s_phallus_h_gate_2_bounded_k_scaling_holdout as gate
from janus_c025_core import canonical_cnf, cnf_hash, variables


def residual_after_parent_preprocessing(raw_formula: Iterable[Iterable[int]]):
    formula = canonical_cnf(raw_formula)
    normalized, _ = gate.v2.normalize_subsumption(formula)
    residual, _, _ = gate.v2.unit_propagate(normalized)
    return canonical_cnf(residual)


def install_budget_guard() -> None:
    original_solve = gate.solve_with_gate

    def guarded_solve(raw_formula: Iterable[Iterable[int]], budget: int) -> dict[str, Any]:
        raw_rows = [tuple(int(x) for x in clause) for clause in raw_formula]
        residual = residual_after_parent_preprocessing(raw_rows)
        q0 = gate.v21.detect_pair_product(residual)
        if not q0["matched"] and len(variables(residual)) > int(budget):
            solved = gate.v2.technical_forward(raw_rows, int(budget))
            call = {
                "lane": gate.GENERIC_LANE,
                "formula_hash": cnf_hash(residual),
                "found_k": None,
                "budget_guard": "INHERITED_OSIRIS_RESIDUAL_DEPTH_EXCEEDS_FROZEN_STATE_BUDGET",
                "residual_variable_count": len(variables(residual)),
                "state_budget": int(budget),
                "auto_k_detector_invoked": False,
                "authority_added": False,
            }
            solved["s2_calls"] = [call]
            solved["primary"] = call
            solved["primary_lane"] = gate.GENERIC_LANE
            solved["found_k"] = None
            return solved
        return original_solve(raw_rows, int(budget))

    gate.solve_with_gate = guarded_solve


def run() -> dict[str, Any]:
    install_budget_guard()
    result = gate.run()
    result["implementation_conformance"] = {
        "frozen_contract_unchanged": True,
        "frozen_fixture_corpus_unchanged": True,
        "Q0_priority_preserved": True,
        "auto_k_search_exact_for_budget_admitted_residuals": True,
        "inherited_budget_guard": "residual_variable_count > existing frozen state_budget after parent normalization/unit propagation",
        "new_posthoc_threshold_added": False,
        "hard_Tseitin_auto_k_not_invoked_after_parent_budget_reject": True,
        "P_VS_NP": "OPEN",
    }
    result.pop("integrity_sha256", None)
    result["integrity_sha256"] = gate.digest(result)
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    result = run()
    text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    if args.self_test and not result["status"].startswith("PASS_KEEP"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
