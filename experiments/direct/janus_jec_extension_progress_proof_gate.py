#!/usr/bin/env python3
"""Exact outcome-neutral regression gate for stage-4 JEC progress proofs.

The old PHP_5_4_C1 v2 terminal state is replayed exactly.  The gate does NOT
assume a v3 move exists.  Instead it independently enumerates the entire frozen
B2-OR-pair + two-distinct-eliminations grammar under the same state cap and
counts plans with strict frozen-potential decrease.

Consistency rule:
  * zero strict-drop plans  => standalone producer MUST return None;
  * one or more plans       => producer MUST return a separately verified proof.

Thus a finite negative barrier is a PASS of the epistemic gate, not a solver
success.  Universal move availability and P_VS_NP remain OPEN.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_unified_macro_restore_v2 as v2
from experiments.direct import janus_jec_extension_progress_proof as proof_object
from experiments.direct.janus_php54_macro_restore_attack import pigeonhole

CAPTURED: base.EngineState | None = None
ORIGINAL_DISCOVERY = v2.discover_macro_restore_v2


def capture_root_free_barrier(state: base.EngineState):
    global CAPTURED
    out = ORIGINAL_DISCOVERY(state)
    live = set(base.vars_of(state.residual))
    if out is None and not any(variable in live for variable in state.root_vars):
        CAPTURED = state
    return out


def exact_frozen_grammar_spectrum(state: base.EngineState) -> dict:
    residual = state.residual
    live = tuple(base.vars_of(residual))
    fresh = max([*live, *state.root_vars], default=0) + 1
    cap = state.state_cap
    start_phi = state.progress_phi()

    macro_candidates = 0
    macro_under_cap = 0
    first_attempts = first_fits = 0
    second_attempts = second_fits = 0
    strict_drop_plans = []
    rejection_reasons = Counter()

    for a, b in v2.all_or_pair_candidates(residual):
        macro_candidates += 1
        try:
            macro, cert = v2.apply_or_pair_v2(residual, a, b, fresh)
        except ValueError:
            rejection_reasons["macro_invalid"] += 1
            continue
        if base.state_units(macro) > cap:
            rejection_reasons["macro_over_cap"] += 1
            continue
        if not v2.verify_or_pair_v2(residual, macro, cert):
            raise AssertionError("INDEPENDENT_SPECTRUM_MACRO_REPLAY_FAILED")
        macro_under_cap += 1

        for p1 in live:
            first_attempts += 1
            out1, stats1 = base.eliminate_var_capped(macro, p1, cap)
            if out1 is None:
                rejection_reasons["first_elim_over_cap"] += 1
                continue
            if not base.verify_elimination_transition(macro, p1, out1, cap):
                raise AssertionError("INDEPENDENT_SPECTRUM_FIRST_ELIM_REPLAY_FAILED")
            first_fits += 1
            live1 = set(base.vars_of(out1))

            for p2 in live:
                if p2 == p1 or p2 not in live1:
                    continue
                second_attempts += 1
                out2, stats2 = base.eliminate_var_capped(out1, p2, cap)
                if out2 is None:
                    rejection_reasons["second_elim_over_cap"] += 1
                    continue
                if not base.verify_elimination_transition(out1, p2, out2, cap):
                    raise AssertionError("INDEPENDENT_SPECTRUM_SECOND_ELIM_REPLAY_FAILED")
                second_fits += 1
                phi = state.progress_phi(out2, state.ledger.extension_count + 1)
                if phi < start_phi:
                    strict_drop_plans.append({
                        "pair": [a, b],
                        "pivots": [p1, p2],
                        "after_phi": phi,
                        "after_units": base.state_units(out2),
                        "first_pairs": int(stats1.get("pairs", 0)),
                        "second_pairs": int(stats2.get("pairs", 0)),
                        "after_fingerprint": base.fingerprint(out2),
                    })
                else:
                    rejection_reasons["no_strict_phi_drop"] += 1

    strict_drop_plans.sort(
        key=lambda row: (
            row["after_phi"],
            row["after_units"],
            row["pair"],
            row["pivots"],
        )
    )
    return {
        "source_fingerprint": base.fingerprint(residual),
        "state_cap": cap,
        "state_units": base.state_units(residual),
        "start_phi": start_phi,
        "live_variables": list(live),
        "macro_candidates": macro_candidates,
        "macro_under_cap": macro_under_cap,
        "first_elimination_attempts": first_attempts,
        "first_elimination_fits": first_fits,
        "second_elimination_attempts": second_attempts,
        "second_elimination_fits": second_fits,
        "strict_drop_plan_count": len(strict_drop_plans),
        "best_strict_drop_plans": strict_drop_plans[:16],
        "rejection_reasons": dict(sorted(rejection_reasons.items())),
    }


def main() -> int:
    global CAPTURED
    previous = v2.discover_macro_restore_v2
    v2.discover_macro_restore_v2 = capture_root_free_barrier
    try:
        old_result = v2.solve_fail_closed_v2(
            pigeonhole(5, 4),
            cap_exponent=1,
            extension_exponent=1,
        )
    finally:
        v2.discover_macro_restore_v2 = previous

    if old_result.get("status") != "OPEN" or CAPTURED is None:
        raise AssertionError("FROZEN_ROOT_FREE_BARRIER_NOT_REPLAYED")

    state = CAPTURED
    source = state.residual
    live = set(base.vars_of(source))
    if any(variable in live for variable in state.root_vars):
        raise AssertionError("CAPTURED_STATE_STILL_HAS_LIVE_ROOTS")

    spectrum = exact_frozen_grammar_spectrum(state)
    proof = proof_object.build_from_state(state, context_mode="ENGINE_CONTEXT")
    strict_count = int(spectrum["strict_drop_plan_count"])

    if strict_count == 0:
        if proof is not None:
            raise AssertionError("PRODUCER_FOUND_PROOF_WHERE_EXHAUSTIVE_SPECTRUM_FOUND_NONE")
        outcome = "PASS_NEGATIVE_BARRIER"
        proof_record = None
    else:
        if proof is None:
            raise AssertionError("PRODUCER_MISSED_EXISTING_STRICT_DROP_PLAN")
        if proof.get("mode") != "EXTENSION_TAIL_V3":
            raise AssertionError(f"EXPECTED_V3_TAIL_PROOF_GOT:{proof.get('mode')}")
        if len(proof.get("elimination_steps", [])) != 2:
            raise AssertionError("V3_PROOF_DID_NOT_KEEP_FROZEN_CHAIN_LENGTH_2")
        if not proof_object.verify_extension_progress_proof(
            source,
            proof,
            require_initial_context=False,
        ):
            raise AssertionError("STANDALONE_VERIFIER_REJECTED_REPLAYED_V3_PROOF")
        if not proof.get("strict_progress"):
            raise AssertionError("PROOF_DID_NOT_CERTIFY_STRICT_PROGRESS")
        outcome = "PASS_POSITIVE_PROGRESS_WITNESS"
        proof_record = {
            "mode": proof["mode"],
            "proof_bytes": proof["proof_bytes"],
            "elimination_chain_length": len(proof["elimination_steps"]),
            "before_phi": proof["before_phi"],
            "after_phi": proof["after_phi"],
            "strict_progress": proof["strict_progress"],
            "result_fingerprint": proof["result_fingerprint"],
            "verified_without_rediscovery": True,
        }

    report = {
        "schema": "JANUS/C025/JEC-EXTENSION-PROGRESS-PROOF-GATE/v2",
        "status": "PASS",
        "outcome": outcome,
        "P_VS_NP": "OPEN",
        "old_engine_result": {
            "status": old_result.get("status"),
            "reason": old_result.get("reason"),
            "macro_restore_version": old_result.get("macro_restore_version"),
        },
        "captured_context": {
            "source_fingerprint": base.fingerprint(source),
            "live_variables": len(base.vars_of(source)),
            "live_root_variables": 0,
            "N": state.N,
            "state_cap": state.state_cap,
            "extension_count_before": state.ledger.extension_count,
        },
        "independent_exhaustive_frozen_grammar_spectrum": spectrum,
        "standalone_proof": proof_record,
        "interpretation": (
            "CURRENT_B2_PLUS_TWO_ELIM_STAGE4_GRAMMAR_HAS_NO_STRICT_PROGRESS_MOVE_ON_THIS_FROZEN_STATE"
            if strict_count == 0
            else "CURRENT_STAGE4_GRAMMAR_HAS_AT_LEAST_ONE_EXACT_STRICT_PROGRESS_MOVE_ON_THIS_FROZEN_STATE"
        ),
        "scientific_boundary": {
            "finite_replayed_barrier_only": True,
            "negative_barrier_is_not_solver_failure": True,
            "universal_OPEN3_move_availability": "OPEN",
            "one_fixed_polynomial_discovery_bound_for_all_OPEN3": "OPEN",
            "P_VS_NP": "OPEN",
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
