from __future__ import annotations

import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47f_small_reachable_fixpoint_full_macro_falsifier as r47f

ROOT = Path(__file__).resolve().parents[1]
R47G_CHECKPOINT = ROOT / "research" / "JANUS_TRUMP_R47_O4_ATTACK_CHECKPOINT_R47J_2026-09-03.json"
R47I_RESULT = ROOT / "research" / "JANUS_TRUMP_R47I_EXPLICIT_REACHABLE_ONE_SWAP_MACRO_DEAD_COUNTEREXAMPLE_RESULT_2026-09-03.json"


def theorem_safe_cap(formula) -> int:
    canonical = r33.canonical_formula(formula)
    C0, _, V0 = r33.measure(canonical)
    Lmax = C0 * V0
    H = (C0 + 1) * (Lmax + 1) * (V0 + 1)
    return H + 1


def comparable(result):
    return {
        "terminal": result["terminal"],
        "final_formula": result["final_formula"],
        "history": result["history"],
        "rule_counts": result["rule_counts"],
        "total_rule_applications": result["total_rule_applications"],
        "strict_progress": result["strict_progress"],
    }


def audit_case(name, formula):
    canonical = r33.canonical_formula(formula)
    cap = theorem_safe_cap(canonical)
    legacy = r33.simplify(canonical, max_steps=100000)
    candidate = r33.simplify(canonical, max_steps=cap)
    equal = comparable(legacy) == comparable(candidate)
    if not equal:
        raise AssertionError(("R47P_SEMANTIC_OR_TRACE_DRIFT", name))
    if candidate["terminal"] == "FAIL_STEP_LIMIT":
        raise AssertionError(("R47P_THEOREM_SAFE_CAP_EXHAUSTED", name, cap))
    if candidate["total_rule_applications"] >= cap:
        raise AssertionError(("R47P_RULE_COUNT_NOT_BELOW_CAP", name, candidate["total_rule_applications"], cap))
    C0, _, V0 = r33.measure(canonical)
    return {
        "name": name,
        "initial_CLV": list(r33.measure(canonical)),
        "theorem_safe_cap": cap,
        "legacy_terminal": legacy["terminal"],
        "candidate_terminal": candidate["terminal"],
        "rule_applications": candidate["total_rule_applications"],
        "cap_slack": cap - candidate["total_rule_applications"],
        "byte_equivalent_selected_fields": True,
        "C0": C0,
        "V0": V0,
    }


def load_r47g_residual():
    checkpoint = json.loads(R47G_CHECKPOINT.read_text())
    target_hash = checkpoint["sealed_lineage"]["R47G"]["fixpoint_hash"]
    original = r33.deterministic_random_3cnf(473383, n=30, ratio=3.8)
    reached = r47f.reachable_fixpoint(original)
    if reached is None:
        raise AssertionError("R47P_R47G_SOURCE_NO_LONGER_REACHES_FIXPOINT")
    residual = r33.canonical_formula(reached["formula"])
    if r47f.formula_hash(residual) != target_hash:
        raise AssertionError(("R47P_R47G_FIXPOINT_HASH_DRIFT", r47f.formula_hash(residual), target_hash))
    return residual


def frozen_cases():
    yield "EASY_REDUNDANT_TAIL", r33.easy_redundant_tail()
    yield "BLOCKED_CLAUSE_CONTROL", r33.blocked_clause_control()
    yield "BVE_CONTROL", r33.bve_control()
    for n in (8, 12, 16, 20, 24, 28, 32):
        yield f"PRISM_TSEITIN_{n}", r33.prism_tseitin(n)
    for seed in (33001, 33002, 33003, 33004):
        yield f"RANDOM_{seed}", r33.deterministic_random_3cnf(seed)
    yield "R47G_EARLIEST_FROZEN_LADDER_RESIDUAL", load_r47g_residual()
    r47i = json.loads(R47I_RESULT.read_text())
    yield "R47I_EXPLICIT_RESIDUAL", r33.canonical_formula(r47i["genuine_residual_fixpoint"]["formula"])


def run():
    rows = [audit_case(name, formula) for name, formula in frozen_cases()]
    out = {
        "gate": "JANUS_TRUMP_R47P_R33_INPUT_DEPENDENT_POLYNOMIAL_CAP",
        "verdict": "THEOREM_SAFE_INPUT_DEPENDENT_R33_CAP_MATCHES_LEGACY_ON_FROZEN_AUDIT__READY_FOR_SEPARATE_DEFAULT_INTEGRATION",
        "formula": "cap(F)=((C0+1)*(C0*V0+1)*(V0+1))+1",
        "case_count": len(rows),
        "rows": rows,
        "all_byte_equivalent_selected_fields": all(r["byte_equivalent_selected_fields"] for r in rows),
        "any_candidate_step_limit": any(r["candidate_terminal"] == "FAIL_STEP_LIMIT" for r in rows),
        "interpretation": {
            "magic_100000_is_not_needed_for_these_frozen_cases": True,
            "symbolic_reason_for_global_safe_cap": "STRICT_LEXICOGRAPHIC_CLV_DESCENT_AND_NO_FRESH_VARIABLES",
            "default_signature_modified_in_this_gate": False,
            "next_integration_requires_preserving_explicit_override_for_RESOURCE_LIMIT_TESTS": True,
        },
        "firewall": {
            "O4_UNIVERSAL_COVERAGE_FOR_EXTENDED_GRAMMAR": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_EQ_NP": "NOT_PROVED",
            "P_NE_NP": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }
    print(json.dumps(out, sort_keys=True))
    return out


if __name__ == "__main__":
    run()
