#!/usr/bin/env python3
"""Regression gate for the standalone JEC extension-progress proof object.

The gate deterministically replays the old PHP_5_4_C1 v2 engine until it reaches
the previously observed root-free extension-tail barrier.  Only then does the
new proof-object producer run.  Its proposed v3 move must be accepted by the
standalone verifier, which does not rerun discovery.

This is a finite regression witness for proof-object extraction, not evidence
that every OPEN_3 instance has such a move.  P_VS_NP remains OPEN.
"""
from __future__ import annotations

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
    if any(variable in set(base.vars_of(source)) for variable in state.root_vars):
        raise AssertionError("CAPTURED_STATE_STILL_HAS_LIVE_ROOTS")

    proof = proof_object.build_from_state(state, context_mode="ENGINE_CONTEXT")
    if proof is None:
        raise AssertionError("NO_V3_EXTENSION_PROGRESS_PROOF_AT_FROZEN_BARRIER")
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

    report = {
        "schema": "JANUS/C025/JEC-EXTENSION-PROGRESS-PROOF-GATE/v1",
        "status": "PASS",
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


if __name__ == "__main__":
    raise SystemExit(main())
