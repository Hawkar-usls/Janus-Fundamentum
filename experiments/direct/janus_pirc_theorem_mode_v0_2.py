#!/usr/bin/env python3
"""JANUS PIRC theorem-mode v0.2.

Reverse-pass repair over v0.1:
  after ONE independently verified Stage4 progress move, do not immediately
  stop. First re-enter the already admitted exact family-specific lanes on the
  verified result CNF. If they decide the result, compose that decision with
  the Stage4 decision-equivalence certificate. If they still return OPEN, stop
  before a second Stage4 move because iterated Stage4 GPEI remains unproved.

No runtime grammar evolution, recursive Shannon-depth increase, or heuristic
promotion is allowed. P_VS_NP remains OPEN.
"""
from __future__ import annotations

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_one_variable_separator_escape as current_solver
from experiments.direct import janus_jec_extension_progress_proof as stage4
from experiments.direct import janus_matching_hall_escape as hall

P_VS_NP = "OPEN"

FROZEN_PATH = (
    "SYNTACTIC_CANONICALIZE",
    "EXACT_TYPED_LANES",
    "ONE_VERIFIED_STAGE4_EXTENSION_PROGRESS_MOVE_IF_NEEDED",
    "REENTER_EXACT_TYPED_LANES_ON_VERIFIED_RESULT",
    "STOP_BEFORE_SECOND_STAGE4_MOVE_UNLESS_GPEI_IS_PROVED",
)


def _exact_typed_lanes(cnf) -> dict:
    hall_result = hall.solve_matching_hall_escape(cnf)
    if hall_result.get("status") in {"SAT", "UNSAT"}:
        if not hall.verify_matching_hall_escape(cnf, hall_result):
            return {"status": "SAFE_ERROR", "failure_gate": "MATCHING_HALL_INDEPENDENT_REPLAY"}
        return {
            "status": hall_result["status"],
            "mode": "MATCHING_HALL_CARDINALITY_ESCAPE",
            "certificate": hall_result,
        }

    exact_result = current_solver.solve_one_variable_escape(cnf)
    if exact_result.get("status") in {"SAT", "UNSAT"}:
        if not current_solver.verify_one_variable_escape(cnf, exact_result):
            return {"status": "SAFE_ERROR", "failure_gate": "CURRENT_EXACT_STACK_INDEPENDENT_REPLAY"}
        return {
            "status": exact_result["status"],
            "mode": exact_result.get("mode"),
            "certificate": exact_result,
        }

    return {"status": "OPEN"}


def run(raw_clauses) -> dict:
    source = base.canon_cnf(raw_clauses)
    N = base.input_size_units(source)
    initial_state_units = base.state_units(source)

    initial = _exact_typed_lanes(source)
    if initial["status"] == "SAFE_ERROR":
        return {
            "kind": "JANUS_PIRC_THEOREM_MODE_V0_2",
            **initial,
            "P_VS_NP": P_VS_NP,
        }
    if initial["status"] in {"SAT", "UNSAT"}:
        return {
            "kind": "JANUS_PIRC_THEOREM_MODE_V0_2",
            "status": initial["status"],
            "mode": initial.get("mode"),
            "N": N,
            "initial_state_units": initial_state_units,
            "decision_chain": [initial],
            "universal_claim": False,
            "P_VS_NP": P_VS_NP,
        }

    proof = stage4.discover_initial_extension_progress(
        source,
        cap_exponent=2,
        extension_exponent=1,
    )
    if proof is None:
        return {
            "kind": "JANUS_PIRC_THEOREM_MODE_V0_2",
            "status": "OPEN",
            "first_open_gate": "NO_CERTIFIED_STAGE4_PROGRESS_MOVE",
            "N": N,
            "initial_state_units": initial_state_units,
            "frozen_path": list(FROZEN_PATH),
            "universal_GPEI_preservation": "OPEN",
            "P_VS_NP": P_VS_NP,
        }

    if not stage4.verify_extension_progress_proof(source, proof, require_initial_context=True):
        return {
            "kind": "JANUS_PIRC_THEOREM_MODE_V0_2",
            "status": "SAFE_ERROR",
            "failure_gate": "STAGE4_PROGRESS_INDEPENDENT_REPLAY",
            "P_VS_NP": P_VS_NP,
        }

    result_cnf = base.canon_cnf(proof.get("result_cnf", []))
    if base.fingerprint(result_cnf) != proof.get("result_fingerprint"):
        return {
            "kind": "JANUS_PIRC_THEOREM_MODE_V0_2",
            "status": "SAFE_ERROR",
            "failure_gate": "STAGE4_RESULT_BINDING",
            "P_VS_NP": P_VS_NP,
        }

    after_one_stage4 = _exact_typed_lanes(result_cnf)
    if after_one_stage4["status"] == "SAFE_ERROR":
        return {
            "kind": "JANUS_PIRC_THEOREM_MODE_V0_2",
            **after_one_stage4,
            "P_VS_NP": P_VS_NP,
        }

    if after_one_stage4["status"] in {"SAT", "UNSAT"}:
        # The Stage4 verifier replayed one exact decision-preserving move; the
        # second certificate decides its verified result. This is a finite exact
        # certificate chain, not a universal complexity theorem.
        return {
            "kind": "JANUS_PIRC_THEOREM_MODE_V0_2",
            "status": after_one_stage4["status"],
            "mode": "STAGE4_THEN_EXACT_TYPED_LANE",
            "post_stage4_mode": after_one_stage4.get("mode"),
            "N": N,
            "initial_state_units": initial_state_units,
            "result_state_units": base.state_units(result_cnf),
            "decision_chain": [
                {
                    "kind": "VERIFIED_STAGE4_PROGRESS",
                    "result_fingerprint": proof.get("result_fingerprint"),
                    "before_phi": proof.get("before_phi"),
                    "after_phi": proof.get("after_phi"),
                    "proof_bytes": proof.get("proof_bytes"),
                },
                after_one_stage4,
            ],
            "universal_claim": False,
            "universal_GPEI_preservation": "OPEN",
            "P_VS_NP": P_VS_NP,
        }

    # Only here is a second Stage4 move required. The reverse-pass firewall
    # forbids taking it until iterative exact closure and one fixed global
    # polynomial envelope have been proved.
    return {
        "kind": "JANUS_PIRC_THEOREM_MODE_V0_2",
        "status": "OPEN",
        "first_open_gate": "SECOND_STAGE4_REQUIRES_ITERATED_GPEI_PRESERVATION",
        "N": N,
        "initial_state_units": initial_state_units,
        "result_state_units": base.state_units(result_cnf),
        "one_exact_progress_move_verified": True,
        "progress_before_phi": proof.get("before_phi"),
        "progress_after_phi": proof.get("after_phi"),
        "progress_proof_bytes": proof.get("proof_bytes"),
        "result_fingerprint": proof.get("result_fingerprint"),
        "frozen_path": list(FROZEN_PATH),
        "why_stop": (
            "The post-Stage4 result remained OPEN under all currently admitted exact typed lanes. "
            "A second Stage4 move would require the still-open iterative GPEI/closure theorem."
        ),
        "runtime_grammar_self_modification": False,
        "universal_GPEI_preservation": "OPEN",
        "arbitrary_CNF_totality": "OPEN",
        "P_VS_NP": P_VS_NP,
    }


def self_test() -> None:
    # Hall lane remains exact.
    m, n = 5, 4
    var = lambda p, h: 1 + p * n + h
    php54 = [tuple(var(p, h) for h in range(n)) for p in range(m)]
    for h in range(n):
        for p in range(m):
            for q in range(p + 1, m):
                php54.append((-var(p, h), -var(q, h)))
    out = run(php54)
    assert out["status"] == "UNSAT"
    assert out["P_VS_NP"] == "OPEN"

    # Frozen first R1 OPEN3 witness: v0.2 is allowed to close it after one
    # verified Stage4 move, or remain OPEN before a second Stage4 move.
    r1_first_open3 = (
        (-2, -3, -4),
        (-2, -3, 4),
        (-2, 3, -4),
        (-1, -3, -4),
        (-1, -2, -4),
    )
    out = run(r1_first_open3)
    assert out["status"] in {"SAT", "UNSAT", "OPEN"}
    assert out["P_VS_NP"] == "OPEN"
    if out["status"] == "OPEN":
        assert out["first_open_gate"] in {
            "NO_CERTIFIED_STAGE4_PROGRESS_MOVE",
            "SECOND_STAGE4_REQUIRES_ITERATED_GPEI_PRESERVATION",
        }


if __name__ == "__main__":
    self_test()
    probe = (
        (-2, -3, -4),
        (-2, -3, 4),
        (-2, 3, -4),
        (-1, -3, -4),
        (-1, -2, -4),
    )
    result = run(probe)
    print("JANUS_PIRC_THEOREM_MODE_V0_2_SELF_TEST=PASS")
    print("R1_FIRST_OPEN3_V0_2_STATUS=" + result["status"])
    print("R1_FIRST_OPEN3_V0_2_MODE=" + str(result.get("mode", result.get("first_open_gate"))))
    print("UNIVERSAL_GPEI_PRESERVATION=OPEN")
    print("P_VS_NP=OPEN")
