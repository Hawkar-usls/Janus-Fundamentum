from __future__ import annotations

import inspect
import json

import research.tools.apma_inverted_pyramid.inverted_pyramid as ip
from research.tools.apma_trinity_sovereign.trinity import run_trinity
from research.tools.apma_ss_provenance.apma_ss_controller import run_apma_ss
from research.tools.apma_interface_quotient.exact_quotient import make_affine_control
from research.tools.apma_factorized_feedback.factorized_portfolio import solve_instance as direct_factorized
from research.tools.apma_log_alien_transfer.log_alien_transfer import solve_instance as direct_alien

ARTIFACT_ID = "JANUS-TRUMP-INVERTED-PYRAMID-ADMISSION-V2-INDEPENDENT-CHECK-2026-09-15-v1.0"
AUTHORITY = "INDEPENDENT_CHECKER__ARCHITECTURAL_DIAGNOSTIC_ONLY"


def bomb(*args, **kwargs):
    raise AssertionError("FORBIDDEN_EXECUTION_BEFORE_ADMISSION")


def main() -> None:
    checks: dict[str, bool] = {}
    guard = ip.source_guard()
    checks["P1_source_guard"] = bool(guard["ok"])

    legacy_case = ip.legacy_2cnf_case()
    legacy_routed = ip.route(legacy_case)
    legacy_direct = run_trinity(
        tuple(tuple(int(x) for x in c) for c in legacy_case["payload"]["source"]),
        int(legacy_case["payload"]["n"]),
    )
    checks["P2_legacy_admission_before_execution"] = (
        legacy_routed["status"] == "ROUTED"
        and legacy_routed["admission"]["admitted"] is True
        and legacy_routed["metrics"]["sealed_executions"] == 1
    )
    checks["P3_legacy_direct_equivalence"] = legacy_routed["execution"] == legacy_direct

    provenance_case = ip.provenance_2cnf_case()
    provenance_routed = ip.route(provenance_case)
    provenance_direct = run_apma_ss(provenance_case["payload"]["image"])
    checks["P3_provenance_direct_equivalence"] = (
        provenance_routed["status"] == "ROUTED"
        and provenance_routed["admission"]["door"] == ip.PROVENANCE
        and provenance_routed["execution"] == provenance_direct
    )

    affine_case = ip.affine_case()
    affine_routed = ip.route(affine_case)
    affine_direct = make_affine_control()
    checks["P3_affine_direct_equivalence"] = (
        affine_routed["status"] == "ROUTED"
        and affine_routed["admission"]["door"] == ip.AFFINE
        and affine_routed["execution"]["control"] == affine_direct
        and affine_routed["execution"]["status"] == "ADMITTED_EXACT_AFFINE_CARRIER"
    )

    factor_case = ip.factorized_case()
    factor_routed = ip.route(factor_case)
    factor_direct = direct_factorized(factor_case["payload"]["instance"])
    checks["P3_factorized_direct_equivalence"] = (
        factor_routed["status"] == "ROUTED"
        and factor_routed["admission"]["door"] == ip.FACTORIZED
        and factor_routed["execution"] == factor_direct
        and factor_routed["metrics"]["cartesian_products_materialized"] == 0
    )

    alien_case = ip.alien_case()
    alien_routed = ip.route(alien_case)
    alien_direct = direct_alien(alien_case["payload"]["instance"])
    checks["P3_log_alien_direct_equivalence"] = (
        alien_routed["status"] == "ROUTED"
        and alien_routed["admission"]["door"] == ip.ALIEN
        and alien_routed["execution"] == alien_direct
        and alien_routed["metrics"]["global_variable_cube_enumeration"] == 0
    )

    # Killer control 1: over-budget alien case must stop before the underlying solver can run.
    old_alien = ip.solve_alien_instance
    ip.solve_alien_instance = bomb
    try:
        over = ip.route(ip.alien_over_budget_case())
    finally:
        ip.solve_alien_instance = old_alien
    checks["P5_over_budget_fails_before_execution"] = (
        over["status"] == "OPEN_NO_ADMITTED_EXACT_BASIS"
        and over["admission"]["reason"] == "ALIEN_TUPLE_BUDGET"
        and over["metrics"]["sealed_executions"] == 0
        and over["metrics"]["generic_transfer_calls"] == 0
    )

    # Killer control 2: connected mixed feedback component must stop before the factorized solver can run.
    old_factor = ip.solve_factorized_instance
    ip.solve_factorized_instance = bomb
    try:
        mixed = ip.route(ip.unsupported_connected_mixed_feedback_case())
    finally:
        ip.solve_factorized_instance = old_factor
    checks["P5_unsupported_mixed_fails_before_execution"] = (
        mixed["status"] == "OPEN_NO_ADMITTED_EXACT_BASIS"
        and mixed["admission"]["reason"] == "NO_COMPLETE_SEALED_CARRIER_FOR_COMPONENT"
        and mixed["metrics"]["sealed_executions"] == 0
        and mixed["metrics"]["generic_transfer_calls"] == 0
    )

    candidate_source = inspect.getsource(ip)
    checks["P6_candidate_has_no_full_cube_enumerator"] = "itertools.product" not in candidate_source
    checks["P6_candidate_has_no_generic_transfer_executor"] = "def generic_transfer" not in candidate_source
    checks["P6_negative_controls_zero_cartesian"] = (
        over["metrics"]["cartesian_products_materialized"] == 0
        and mixed["metrics"]["cartesian_products_materialized"] == 0
    )

    control_run = ip.run_controls()
    sf = control_run["scientific_firewall"]
    checks["P7_firewall_general_sat_not_proved"] = sf["GENERAL_SAT_IN_P"] == "NOT_PROVED"
    checks["P7_firewall_p_vs_np_open"] = sf["P_VS_NP"] == "OPEN"
    checks["P7_no_global_frontier_advance"] = sf["GLOBAL_APMA_FRONTIER_ADVANCE"] == "NONE"
    checks["P7_no_new_sat_class_claim"] = sf["NEW_SAT_CLASS"] == "NOT_CLAIMED"

    # Architectural effect: all five sealed positive doors survive; two unsupported cases fail earlier than execution.
    positive_names = ["legacy_2cnf", "provenance_2cnf", "affine_wide", "factorized_feedback", "log_alien_connected"]
    results = control_run["results"]
    checks["architectural_five_positive_doors_routed"] = all(results[n]["status"] == "ROUTED" for n in positive_names)
    checks["architectural_two_negative_doors_open_early"] = (
        results["alien_over_budget"]["status"] == "OPEN_NO_ADMITTED_EXACT_BASIS"
        and results["unsupported_connected_mixed_feedback"]["status"] == "OPEN_NO_ADMITTED_EXACT_BASIS"
        and results["alien_over_budget"]["metrics"]["sealed_executions"] == 0
        and results["unsupported_connected_mixed_feedback"]["metrics"]["sealed_executions"] == 0
    )

    verdict = (
        "PASS_INVERTED_PYRAMID_ADMISSION_BEFORE_TRANSFER_ARCHITECTURAL_DIAGNOSTIC"
        if all(checks.values())
        else "FAIL_INVERTED_PYRAMID_DIAGNOSTIC"
    )
    out = {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "checks": checks,
        "source_guard": guard,
        "architectural_result": {
            "classification": "SUCCESSOR_REPAIR_OF_TRINITY__NOT_NEW_SAT_MECHANISM",
            "positive_sealed_doors_preserved": 5,
            "unsupported_cases_stopped_before_execution": 2,
            "generic_transfer_calls_on_negative_controls": 0,
            "interpretation": "The pyramid inversion is operationally consistent on the frozen controls: exact basis admission can be placed before execution without changing sealed-door results, and unsupported cases fail closed earlier."
        },
        "scientific_firewall": {
            "GENERAL_SAT_IN_P": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE",
            "NEW_SAT_CLASS": "NOT_CLAIMED",
            "UNSEEN_CARRIER_DISCOVERY": "NOT_TESTED_BY_THIS_DIAGNOSTIC"
        },
        "verdict": verdict,
    }
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
