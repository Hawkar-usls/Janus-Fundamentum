#!/usr/bin/env python3
"""Exact frozen-v2 gate on the first reachable all-pivot-overflow pair-dispersed state.

The source and reachable product fingerprint were frozen by the preceding
adversarial Delta/pair search before this v2 result is observed.  This script
runs the unmodified PIRC_DECISION_CORE_V0_4 until frozen exhaustive v2 is called
on that exact target state, allows the original v2 implementation to return its
full exact result, records it, and only then stops the outer run.

If v2 returns None, the current root-phase grammar candidate L1 is refuted by an
exact reachable witness.  If v2 returns a rescue, L1 survives this witness while
L1A/L1B remain refuted.  P_VS_NP remains OPEN either way.
"""
from __future__ import annotations

import json
import time
from copy import deepcopy

from experiments.direct import janus_pirc_decision_core_v0_4 as core
from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.theorem_extraction import c025_adversarial_delta_pair_search as adv

P_VS_NP = "OPEN"
EXPECTED_SOURCE_FP = "69e4c811b0e34534c09beb27b75578ba3bfb6625c27aaeea1f8838f44d6281c4"
EXPECTED_PRODUCT_FP = "e10600e0f79ad6f143f3b67b04d4b616da5f59e4a4832af5cbb329a574f0dac7"
EXPECTED_N = 882
EXPECTED_CAP = 777924
EXPECTED_PRODUCT_UNITS = 46657


class GateObserved(Exception):
    pass


def main() -> int:
    source, left, right = adv.build_selector_source(8, 72, 4, 29100)
    product = adv.direct_selector_product(left, right)
    if base.fingerprint(source) != EXPECTED_SOURCE_FP:
        raise AssertionError("FROZEN_SOURCE_FINGERPRINT_DRIFT")
    if base.fingerprint(product) != EXPECTED_PRODUCT_FP:
        raise AssertionError("FROZEN_PRODUCT_FINGERPRINT_DRIFT")
    if base.input_size_units(source) != EXPECTED_N:
        raise AssertionError("FROZEN_N_DRIFT")
    if base.state_units(product) != EXPECTED_PRODUCT_UNITS:
        raise AssertionError("FROZEN_PRODUCT_UNITS_DRIFT")

    original_v2 = core.v2.discover_macro_restore_v2
    gate: dict | None = None

    def wrapped_v2(state: base.EngineState):
        nonlocal gate
        fp = base.fingerprint(state.residual)
        if fp != EXPECTED_PRODUCT_FP:
            return original_v2(state)

        live = set(base.vars_of(state.residual))
        roots_live = sorted(v for v in state.root_vars if v in live)
        if not roots_live:
            raise AssertionError("TARGET_STATE_UNEXPECTEDLY_ROOT_FREE")
        if state.N != EXPECTED_N or state.state_cap != EXPECTED_CAP:
            raise AssertionError("TARGET_BUDGET_DRIFT")
        if base.state_units(state.residual) != EXPECTED_PRODUCT_UNITS:
            raise AssertionError("TARGET_STATE_UNITS_DRIFT")

        before_events = deepcopy(state.ledger.events)
        before_counts = {
            "proposal_work": int(state.ledger.proposal_work),
            "certificate_discovery_work": int(state.ledger.certificate_discovery_work),
            "verification_work": int(state.ledger.verification_work),
            "elimination_pair_work": int(state.ledger.elimination_pair_work),
        }
        t0 = time.perf_counter()
        result = original_v2(state)
        elapsed = time.perf_counter() - t0
        after_counts = {
            "proposal_work": int(state.ledger.proposal_work),
            "certificate_discovery_work": int(state.ledger.certificate_discovery_work),
            "verification_work": int(state.ledger.verification_work),
            "elimination_pair_work": int(state.ledger.elimination_pair_work),
        }
        work_delta = {k: after_counts[k] - before_counts[k] for k in before_counts}

        payload = None
        if result is not None:
            macro_cnf, pivot, after, macro_cert, elim_stats = result
            if not core.v2.verify_or_pair_v2(state.residual, macro_cnf, macro_cert):
                raise AssertionError("RETURNED_V2_MACRO_FAILED_REPLAY")
            if not base.verify_elimination_transition(macro_cnf, pivot, after, state.state_cap):
                raise AssertionError("RETURNED_V2_ELIMINATION_FAILED_REPLAY")
            payload = {
                "macro_pair": list(macro_cert.get("represents", [])),
                "replaced_occurrences": int(macro_cert.get("replaced_occurrences", 0)),
                "extension": int(macro_cert["extension"]),
                "root_pivot": int(pivot),
                "macro_state_units": int(base.state_units(macro_cnf)),
                "macro_fingerprint": base.fingerprint(macro_cnf),
                "after_state_units": int(base.state_units(after)),
                "after_fingerprint": base.fingerprint(after),
                "elimination_stats": deepcopy(elim_stats),
            }

        gate = {
            "target_fingerprint": fp,
            "N": int(state.N),
            "state_cap": int(state.state_cap),
            "state_units": int(base.state_units(state.residual)),
            "root_variables_live": len(roots_live),
            "v2_rescue_exists": result is not None,
            "v2_result": payload,
            "v2_elapsed_seconds": elapsed,
            "v2_work_delta": work_delta,
            "event_prefix": before_events,
        }
        raise GateObserved()

    core.v2.discover_macro_restore_v2 = wrapped_v2
    outer_terminal = None
    try:
        try:
            outer_terminal = core.solve_decision_core(source)
        except GateObserved:
            pass
    finally:
        core.v2.discover_macro_restore_v2 = original_v2

    if gate is None:
        raise AssertionError(
            "FROZEN_CORE_DID_NOT_CALL_V2_ON_TARGET: "
            + json.dumps(
                {
                    "status": outer_terminal.get("status") if outer_terminal else None,
                    "reason": outer_terminal.get("reason") if outer_terminal else None,
                    "residual": outer_terminal.get("residual_fingerprint") if outer_terminal else None,
                },
                sort_keys=True,
            )
        )

    if gate["v2_rescue_exists"]:
        l1_status = "SURVIVES_THIS_WITNESS__V2_EXACT_RESCUE_EXISTS__NOT_PROVED"
        status = "V2_RESCUES_REACHABLE_MONSTER"
        next_gate = "DERIVE_RICHER_REACHABILITY_INVARIANT_BEYOND_FREQUENT_PAIR_OR_SEARCH_FOR_V2_FAILURE"
    else:
        l1_status = "REFUTED_BY_REACHABLE_WITNESS"
        status = "L1_ROOT_GRAMMAR_COUNTEREXAMPLE_FOUND"
        next_gate = "FREEZE_L1_COUNTEREXAMPLE_AND_DESIGN_STRICT_SUCCESSOR_POLYNOMIAL_GRAMMAR"

    report = {
        "schema": "JANUS/C025/REACHABLE-MONSTER-V2-GATE/v1",
        "status": status,
        "fixed_algorithm": "PIRC_DECISION_CORE_V0_4",
        "source_fingerprint": EXPECTED_SOURCE_FP,
        "reachable_product_fingerprint": EXPECTED_PRODUCT_FP,
        "frozen_pre_v2_facts": {
            "N": EXPECTED_N,
            "state_cap": EXPECTED_CAP,
            "product_state_units": EXPECTED_PRODUCT_UNITS,
            "all_ordinary_pivots_overflow": True,
            "pair_margin": -44040,
            "density_margin": -21408768,
            "L1A": "REFUTED_BY_REACHABLE_WITNESS",
            "L1B": "REFUTED_BY_REACHABLE_WITNESS",
        },
        "exact_v2_gate": gate,
        "candidate_results": {
            "L1_ROOT_PHASE_POLYNOMIAL_GRAMMAR_TOTALITY": l1_status,
            "L1A_ALL_PIVOT_OVERFLOW_FORCES_FREQUENT_PAIR": "REFUTED_BY_REACHABLE_WITNESS",
            "L1B_ALL_PIVOT_OVERFLOW_FORCES_PAIR_DENSITY": "REFUTED_BY_REACHABLE_WITNESS",
        },
        "next_gate": next_gate,
        "scientific_boundary": {
            "original_v2_return_value_observed_without_candidate_skipping": True,
            "outer_run_stopped_only_after_target_v2_returned": True,
            "v2_rescue_if_present_replayed_exactly": True,
            "finite_witness_can_refute_candidate_but_not_prove_universal_totality": True,
            "P2_REACHABLE_PRESERVATION": "OPEN",
            "P_VS_NP": P_VS_NP,
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
