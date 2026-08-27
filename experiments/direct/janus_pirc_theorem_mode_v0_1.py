#!/usr/bin/env python3
"""JANUS PIRC theorem-mode v0.1: one frozen deterministic path to the first OPEN.

This is deliberately a partial exact solver. It composes only already admitted
family-specific exact lanes and one independently replayed Stage-4 progress move.
It MUST stop OPEN before iterating a transition whose universal closure and global
polynomial envelope have not been proved.

The purpose is to expose the first real missing theorem, not to hide it behind
finite success or runtime grammar invention.
"""
from __future__ import annotations

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_one_variable_separator_escape as current_solver
from experiments.direct import janus_jec_extension_progress_proof as stage4
from experiments.direct import janus_matching_hall_escape as hall

P_VS_NP = "OPEN"

FROZEN_PATH = (
    "SYNTACTIC_CANONICALIZE",
    "MATCHING_HALL_CARDINALITY_ESCAPE_IF_EXACTLY_RECOGNIZED",
    "GLOBAL_EXACT_ALGEBRA_COMPONENT_ONE_VARIABLE_STACK",
    "ONE_VERIFIED_STAGE4_EXTENSION_PROGRESS_MOVE",
    "STOP_BEFORE_UNPROVED_STAGE4_ITERATION",
)


def run(raw_clauses) -> dict:
    cnf = base.canon_cnf(raw_clauses)
    N = base.input_size_units(cnf)
    initial_state_units = base.state_units(cnf)

    hall_result = hall.solve_matching_hall_escape(cnf)
    if hall_result["status"] in {"SAT", "UNSAT"}:
        if not hall.verify_matching_hall_escape(cnf, hall_result):
            return {
                "kind": "JANUS_PIRC_THEOREM_MODE_V0_1",
                "status": "SAFE_ERROR",
                "failure_gate": "MATCHING_HALL_INDEPENDENT_REPLAY",
                "P_VS_NP": P_VS_NP,
            }
        return {
            "kind": "JANUS_PIRC_THEOREM_MODE_V0_1",
            "status": hall_result["status"],
            "mode": "MATCHING_HALL_CARDINALITY_ESCAPE",
            "N": N,
            "initial_state_units": initial_state_units,
            "certificate": hall_result,
            "universal_claim": False,
            "P_VS_NP": P_VS_NP,
        }

    exact_result = current_solver.solve_one_variable_escape(cnf)
    if exact_result.get("status") in {"SAT", "UNSAT"}:
        if not current_solver.verify_one_variable_escape(cnf, exact_result):
            return {
                "kind": "JANUS_PIRC_THEOREM_MODE_V0_1",
                "status": "SAFE_ERROR",
                "failure_gate": "CURRENT_EXACT_STACK_INDEPENDENT_REPLAY",
                "P_VS_NP": P_VS_NP,
            }
        return {
            "kind": "JANUS_PIRC_THEOREM_MODE_V0_1",
            "status": exact_result["status"],
            "mode": exact_result.get("mode"),
            "N": N,
            "initial_state_units": initial_state_units,
            "certificate": exact_result,
            "universal_claim": False,
            "P_VS_NP": P_VS_NP,
        }

    proof = stage4.discover_initial_extension_progress(
        cnf,
        cap_exponent=2,
        extension_exponent=1,
    )
    if proof is None:
        return {
            "kind": "JANUS_PIRC_THEOREM_MODE_V0_1",
            "status": "OPEN",
            "first_open_gate": "NO_CERTIFIED_STAGE4_PROGRESS_MOVE",
            "N": N,
            "initial_state_units": initial_state_units,
            "frozen_path": list(FROZEN_PATH),
            "universal_GPEI_preservation": "OPEN",
            "P_VS_NP": P_VS_NP,
        }

    if not stage4.verify_extension_progress_proof(cnf, proof, require_initial_context=True):
        return {
            "kind": "JANUS_PIRC_THEOREM_MODE_V0_1",
            "status": "SAFE_ERROR",
            "failure_gate": "STAGE4_PROGRESS_INDEPENDENT_REPLAY",
            "P_VS_NP": P_VS_NP,
        }

    # Critical firewall: one exact progress move does not authorize us to loop it.
    # Re-running the producer on the resulting extended state would require a
    # theorem that the typed semantics, representation envelope, discovery work,
    # normalization and progress remain uniformly polynomial on every reachable
    # iteration. That theorem is precisely what is still OPEN.
    return {
        "kind": "JANUS_PIRC_THEOREM_MODE_V0_1",
        "status": "OPEN",
        "first_open_gate": "STAGE4_ITERATED_GPEI_PRESERVATION",
        "N": N,
        "initial_state_units": initial_state_units,
        "one_exact_progress_move_verified": True,
        "progress_before_phi": proof.get("before_phi"),
        "progress_after_phi": proof.get("after_phi"),
        "progress_proof_bytes": proof.get("proof_bytes"),
        "result_fingerprint": proof.get("result_fingerprint"),
        "frozen_path": list(FROZEN_PATH),
        "why_stop": (
            "Universal repeated Stage-4 operational closure, one fixed input-relative "
            "polynomial envelope, and total discovery/normalization bounds are not proved."
        ),
        "runtime_grammar_self_modification": False,
        "universal_GPEI_preservation": "OPEN",
        "arbitrary_CNF_totality": "OPEN",
        "P_VS_NP": P_VS_NP,
    }


def self_test() -> None:
    # Exact Hall lane: PHP(5,4) must close UNSAT without generic FRP.
    php54 = []
    m, n = 5, 4
    var = lambda p, h: 1 + p * n + h
    for p in range(m):
        php54.append(tuple(var(p, h) for h in range(n)))
    for h in range(n):
        for p in range(m):
            for q in range(p + 1, m):
                php54.append((-var(p, h), -var(q, h)))
    out = run(php54)
    assert out["status"] == "UNSAT"
    assert out["mode"] == "MATCHING_HALL_CARDINALITY_ESCAPE"

    # The theorem-mode machine may solve or return OPEN, but never promote the
    # universal claim from finite examples.
    sample = ((1, 2, 3), (-1, -2))
    out = run(sample)
    assert out["status"] in {"SAT", "UNSAT", "OPEN"}
    assert out["P_VS_NP"] == "OPEN"


if __name__ == "__main__":
    self_test()
    print("JANUS_PIRC_THEOREM_MODE_V0_1_SELF_TEST=PASS")
    print("UNIVERSAL_GPEI_PRESERVATION=OPEN")
    print("P_VS_NP=OPEN")
