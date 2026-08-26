#!/usr/bin/env python3
"""Diagnostic regression gate for the standalone JEC extension-progress proof.

This replays the frozen PHP_5_4_C1 v2 root-free tail barrier and prints the
exact failure phase before raising.  The stage-4 grammar and verifier are not
changed by this diagnostic instrumentation.

P_VS_NP remains OPEN.
"""
from __future__ import annotations

import json
import traceback
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_unified_macro_restore_v2 as v2
from experiments.direct import janus_unified_macro_restore_v3 as v3
from experiments.direct import janus_jec_extension_progress_proof as proof_object
from experiments.direct.janus_php54_macro_restore_attack import pigeonhole

CAPTURED: base.EngineState | None = None
CAPTURE_SNAPSHOT: dict | None = None
ORIGINAL_DISCOVERY = v2.discover_macro_restore_v2


def state_summary(state: base.EngineState) -> dict:
    live = set(base.vars_of(state.residual))
    return {
        "root_fingerprint": base.fingerprint(state.root),
        "residual_fingerprint": base.fingerprint(state.residual),
        "N": state.N,
        "state_cap": state.state_cap,
        "extension_cap": state.extension_cap,
        "extension_count": state.ledger.extension_count,
        "live_variables": len(live),
        "live_root_variables": sum(1 for variable in state.root_vars if variable in live),
        "root_variable_count": len(state.root_vars),
        "residual_state_units": base.state_units(state.residual),
        "phi": state.progress_phi(),
    }


def emit(phase: str, **payload) -> None:
    print(json.dumps({"diagnostic_phase": phase, **payload}, sort_keys=True), flush=True)


def capture_root_free_barrier(state: base.EngineState):
    global CAPTURED, CAPTURE_SNAPSHOT
    out = ORIGINAL_DISCOVERY(state)
    live = set(base.vars_of(state.residual))
    if out is None and not any(variable in live for variable in state.root_vars):
        CAPTURED = state
        CAPTURE_SNAPSHOT = state_summary(state)
        emit("CAPTURE", state=CAPTURE_SNAPSHOT)
    return out


def main() -> int:
    global CAPTURED, CAPTURE_SNAPSHOT
    phase = "REPLAY_OLD_V2"
    try:
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

        emit(
            "OLD_V2_RETURNED",
            status=old_result.get("status"),
            reason=old_result.get("reason"),
            macro_restore_version=old_result.get("macro_restore_version"),
        )
        if old_result.get("status") != "OPEN" or CAPTURED is None or CAPTURE_SNAPSHOT is None:
            raise AssertionError("FROZEN_ROOT_FREE_BARRIER_NOT_REPLAYED")

        state = CAPTURED
        post_return = state_summary(state)
        emit(
            "CAPTURE_REFERENCE_CHECK",
            captured=CAPTURE_SNAPSHOT,
            post_return=post_return,
            reference_drift=(CAPTURE_SNAPSHOT != post_return),
        )

        source = state.residual
        if any(variable in set(base.vars_of(source)) for variable in state.root_vars):
            raise AssertionError("CAPTURED_STATE_STILL_HAS_LIVE_ROOTS")

        phase = "DIRECT_V3_DISCOVERY_DIAGNOSTIC"
        before_direct = state_summary(state)
        direct_plan = v3.discover_extension_tail_plan_v3(state)
        after_direct = state_summary(state)
        emit(
            phase,
            plan_found=(direct_plan is not None),
            before=before_direct,
            after=after_direct,
            ledger_mutated=(before_direct != after_direct),
            plan_pivots=None if direct_plan is None else list(direct_plan.pivots),
            plan_after_fingerprint=None if direct_plan is None else base.fingerprint(direct_plan.after),
        )
        if direct_plan is None:
            raise AssertionError("DIRECT_V3_DISCOVERY_FOUND_NO_PLAN_AT_FROZEN_BARRIER")

        phase = "PACKAGE_PROOF"
        proof = proof_object.build_from_state(state, context_mode="ENGINE_CONTEXT")
        emit(
            phase,
            proof_found=(proof is not None),
            mode=None if proof is None else proof.get("mode"),
            strict_progress=None if proof is None else proof.get("strict_progress"),
        )
        if proof is None:
            raise AssertionError("NO_V3_EXTENSION_PROGRESS_PROOF_AT_FROZEN_BARRIER")
        if proof.get("mode") != "EXTENSION_TAIL_V3":
            raise AssertionError(f"EXPECTED_V3_TAIL_PROOF_GOT:{proof.get('mode')}")
        if len(proof.get("elimination_steps", [])) != 2:
            raise AssertionError("V3_PROOF_DID_NOT_KEEP_FROZEN_CHAIN_LENGTH_2")

        phase = "STANDALONE_VERIFY"
        verified = proof_object.verify_extension_progress_proof(
            source,
            proof,
            require_initial_context=False,
        )
        emit(
            phase,
            verified=verified,
            proof_N=proof.get("N"),
            recomputed_root_N=base.input_size_units(base.canon_cnf(proof.get("root_cnf", []))),
            extension_count_before=proof.get("extension_count_before"),
            before_phi=proof.get("before_phi"),
            after_phi=proof.get("after_phi"),
        )
        if not verified:
            raise AssertionError("STANDALONE_VERIFIER_REJECTED_REPLAYED_V3_PROOF")
        if not proof.get("strict_progress"):
            raise AssertionError("PROOF_DID_NOT_CERTIFY_STRICT_PROGRESS")

        report = {
            "schema": "JANUS/C025/JEC-EXTENSION-PROGRESS-PROOF-GATE/v1",
            "status": "PASS",
            "P_VS_NP": "OPEN",
            "old_engine_result": {
                "status": old_result.get("status"),
                "reason": old_result.get("reason"),
                "macro_restore_version": old_result.get("macro_restore_version"),
            },
            "captured_context": state_summary(state),
            "capture_reference_drift": CAPTURE_SNAPSHOT != post_return,
            "standalone_proof": {
                "mode": proof["mode"],
                "proof_bytes": proof["proof_bytes"],
                "elimination_chain_length": len(proof["elimination_steps"]),
                "before_phi": proof["before_phi"],
                "after_phi": proof["after_phi"],
                "strict_progress": proof["strict_progress"],
                "result_fingerprint": proof["result_fingerprint"],
                "verified_without_rediscovery": True,
            },
            "scientific_boundary": {
                "finite_replayed_barrier_only": True,
                "universal_OPEN3_move_availability": "OPEN",
                "one_fixed_polynomial_discovery_bound_for_all_OPEN3": "OPEN",
                "P_VS_NP": "OPEN",
            },
        }
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    except Exception as error:
        emit(
            "FAIL",
            phase=phase,
            error_type=type(error).__name__,
            error=str(error),
            captured=None if CAPTURED is None else state_summary(CAPTURED),
            capture_snapshot=CAPTURE_SNAPSHOT,
        )
        traceback.print_exc()
        raise


if __name__ == "__main__":
    raise SystemExit(main())
