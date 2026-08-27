#!/usr/bin/env python3
"""Exact finite probe of the SECOND Stage4 move with the ORIGINAL root budget.

This file targets the first R1 source known to remain OPEN after:
  Stage3 -> one verified Stage4 move -> exact typed-lane re-entry.

Critical firewall: the second move is NOT started as a fresh problem.  The
EngineState retains the original root CNF, root variables, original N, state
cap N^C, extension cap N^k, the first extension definition, its allocated id,
and a cumulative resource ledger.  This prevents budget rebasing and dead
extension-id reuse.

A finite success here is only an exact proof-chain specimen.  It does not prove
universal iterability, GPEI, arbitrary-CNF totality, or P=NP.
"""
from __future__ import annotations

import json

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_jec_extension_progress_proof as stage4
from experiments.direct import janus_matching_hall_escape as hall
from experiments.direct import janus_one_variable_separator_escape as stage3

P_VS_NP = "OPEN"

HOSTILE_ROOT = (
    (-2, -3, -4),
    (-2, -3, 4),
    (-1, -3, -4),
    (-1, -2, 3),
    (2, 3, -4),
)
EXPECTED_ROOT_FINGERPRINT = "d54a0b61cba47d2b4a3507f72bc53b599b24fc413d55f3f1aeb2964c159dc156"
EXPECTED_FIRST_RESULT_FINGERPRINT = "24f7b2088a7cc5f03bcdff921ddf8513c14249265c37fc99c04056868cb91400"


def _cnf(rows) -> base.CNF:
    return base.canon_cnf(rows)


def _exact_reentry(cnf: base.CNF) -> dict:
    h = hall.solve_matching_hall_escape(cnf)
    if h.get("status") in {"SAT", "UNSAT"}:
        if not hall.verify_matching_hall_escape(cnf, h):
            raise AssertionError("HALL_REENTRY_REPLAY_FAILED")
        return {"status": h["status"], "mode": "MATCHING_HALL_CARDINALITY_ESCAPE", "certificate": h}

    s = stage3.solve_one_variable_escape(cnf)
    if s.get("status") in {"SAT", "UNSAT"}:
        if not stage3.verify_one_variable_escape(cnf, s):
            raise AssertionError("STAGE3_REENTRY_REPLAY_FAILED")
        return {"status": s["status"], "mode": s.get("mode"), "certificate": s}
    return {"status": "OPEN", "mode": None}


def _ledger_from_first_proof(proof: dict) -> base.Ledger:
    delta = proof.get("discovery_ledger_delta", {})
    ledger = base.Ledger()
    ledger.proposal_work = int(delta.get("proposal_work", 0))
    ledger.certificate_discovery_work = int(delta.get("certificate_discovery_work", 0))
    ledger.verification_work = int(delta.get("verification_work", 0))
    ledger.elimination_pair_work = int(delta.get("elimination_pair_work", 0))
    ledger.recompression_work = int(delta.get("recompression_work", 0))
    ledger.extension_count = int(proof["extension_count_after"])
    ledger.proof_bytes = int(proof.get("proof_bytes", 0))
    ledger.extension_definition_bytes = len(
        json.dumps(proof["macro_certificate"], sort_keys=True, separators=(",", ":")).encode()
    )
    ledger.max_state_units = max(
        [
            base.state_units(_cnf(proof["source_cnf"])),
            base.state_units(_cnf(proof["macro_cnf"])),
            base.state_units(_cnf(proof["result_cnf"])),
        ]
        + [
            base.state_units(_cnf(step["before_cnf"]))
            for step in proof.get("elimination_steps", [])
        ]
        + [
            base.state_units(_cnf(step["after_cnf"]))
            for step in proof.get("elimination_steps", [])
        ]
    )
    return ledger


def _state_after_first(root: base.CNF, proof: dict) -> base.EngineState:
    if not stage4.verify_extension_progress_proof(root, proof, require_initial_context=True):
        raise AssertionError("FIRST_STAGE4_REPLAY_FAILED")
    if _cnf(proof["root_cnf"]) != root:
        raise AssertionError("FIRST_PROOF_ROOT_BINDING_FAILED")

    result = _cnf(proof["result_cnf"])
    macro = dict(proof["macro_certificate"])
    extension = int(macro["extension"])
    history = [
        base.ElimSnapshot(_cnf(step["before_cnf"]), int(step["pivot"]), "STAGE4_PROOF_CHAIN")
        for step in proof.get("elimination_steps", [])
    ]
    ledger = _ledger_from_first_proof(proof)
    return base.EngineState(
        root=root,
        residual=result,
        fixed_assignment={},
        root_vars=base.vars_of(root),
        extension_defs=[macro],
        elimination_history=history,
        seen={base.fingerprint(root), base.fingerprint(result)},
        N=int(proof["N"]),
        cap_exponent=int(proof["cap_exponent"]),
        extension_exponent=int(proof["extension_exponent"]),
        ledger=ledger,
    )


def _cumulative_work(first: dict, second: dict | None) -> dict:
    names = (
        "proposal_work",
        "certificate_discovery_work",
        "verification_work",
        "elimination_pair_work",
        "recompression_work",
    )
    first_delta = first.get("discovery_ledger_delta", {})
    second_delta = second.get("discovery_ledger_delta", {}) if second else {}
    return {
        name: int(first_delta.get(name, 0)) + int(second_delta.get(name, 0))
        for name in names
    }


def run() -> dict:
    root = _cnf(HOSTILE_ROOT)
    if base.fingerprint(root) != EXPECTED_ROOT_FINGERPRINT:
        raise AssertionError("HOSTILE_ROOT_FINGERPRINT_DRIFT")

    N = base.input_size_units(root)
    first = stage4.discover_initial_extension_progress(root, cap_exponent=2, extension_exponent=1)
    if first is None:
        raise AssertionError("HISTORICAL_FIRST_STAGE4_MOVE_DISAPPEARED")
    if not stage4.verify_extension_progress_proof(root, first, require_initial_context=True):
        raise AssertionError("FIRST_STAGE4_VERIFIER_FAILED")
    first_result = _cnf(first["result_cnf"])
    if base.fingerprint(first_result) != EXPECTED_FIRST_RESULT_FINGERPRINT:
        raise AssertionError("FIRST_STAGE4_CANONICAL_RESULT_DRIFT")

    first_reentry = _exact_reentry(first_result)
    if first_reentry["status"] != "OPEN":
        raise AssertionError("HOSTILE_SEED_NO_LONGER_REQUIRES_SECOND_STAGE4")

    state = _state_after_first(root, first)
    root_N = state.N
    root_state_cap = state.state_cap
    root_extension_cap = state.extension_cap
    historical_extensions_before = [int(row["extension"]) for row in state.extension_defs]

    second = stage4.build_from_state(state, context_mode="ENGINE_CONTEXT")
    if second is None:
        return {
            "schema": "JANUS/C025/SECOND-STAGE4-ROOT-ANCHORED-PROBE/v1",
            "status": "FINITE_SECOND_STAGE4_BARRIER_FOUND",
            "root_fingerprint": base.fingerprint(root),
            "root_N": root_N,
            "root_state_cap": root_state_cap,
            "root_extension_cap": root_extension_cap,
            "first_result_fingerprint": base.fingerprint(first_result),
            "first_reentry": first_reentry,
            "historical_extensions_before_second": historical_extensions_before,
            "second_stage4": None,
            "cumulative_work": _cumulative_work(first, None),
            "scientific_boundary": {
                "finite_specimen_only": True,
                "universal_iterability": "OPEN",
                "universal_GPEI_preservation": "OPEN",
                "P_VS_NP": P_VS_NP,
            },
        }

    if not stage4.verify_extension_progress_proof(first_result, second, require_initial_context=False):
        raise AssertionError("SECOND_STAGE4_STANDALONE_REPLAY_FAILED")
    if _cnf(second["root_cnf"]) != root:
        raise AssertionError("SECOND_STAGE4_REBASED_ROOT")
    if int(second["N"]) != N:
        raise AssertionError("SECOND_STAGE4_REBASED_N")
    if int(second["state_cap"]) != N ** 2:
        raise AssertionError("SECOND_STAGE4_REBASED_STATE_CAP")
    if int(second["extension_count_before"]) != 1 or int(second["extension_count_after"]) != 2:
        raise AssertionError("SECOND_STAGE4_EXTENSION_COUNT_DRIFT")

    second_extension = int(second["macro_certificate"]["extension"])
    if second_extension in set(historical_extensions_before):
        raise AssertionError("SECOND_STAGE4_REUSED_HISTORICAL_EXTENSION_ID")
    if second_extension <= max(historical_extensions_before):
        raise AssertionError("SECOND_STAGE4_EXTENSION_NOT_TOPOLOGICALLY_FRESH")

    second_result = _cnf(second["result_cnf"])
    second_reentry = _exact_reentry(second_result)
    all_state_units = [
        base.state_units(root),
        base.state_units(first_result),
        base.state_units(second_result),
        base.state_units(_cnf(first["macro_cnf"])),
        base.state_units(_cnf(second["macro_cnf"])),
    ]
    for proof in (first, second):
        for step in proof.get("elimination_steps", []):
            all_state_units.append(base.state_units(_cnf(step["before_cnf"])))
            all_state_units.append(base.state_units(_cnf(step["after_cnf"])))

    return {
        "schema": "JANUS/C025/SECOND-STAGE4-ROOT-ANCHORED-PROBE/v1",
        "status": (
            "FINITE_EXACT_DECISION_AFTER_TWO_STAGE4"
            if second_reentry["status"] in {"SAT", "UNSAT"}
            else "FINITE_THIRD_STAGE4_REQUIREMENT_FOUND"
        ),
        "root_fingerprint": base.fingerprint(root),
        "root_N": root_N,
        "root_state_cap": root_state_cap,
        "root_extension_cap": root_extension_cap,
        "first_stage4": {
            "mode": first["mode"],
            "extension": int(first["macro_certificate"]["extension"]),
            "before_phi": int(first["before_phi"]),
            "after_phi": int(first["after_phi"]),
            "proof_bytes": int(first["proof_bytes"]),
            "result_fingerprint": first["result_fingerprint"],
        },
        "first_reentry": first_reentry,
        "second_stage4": {
            "mode": second["mode"],
            "context_mode": second["context_mode"],
            "extension": second_extension,
            "extension_count_before": int(second["extension_count_before"]),
            "extension_count_after": int(second["extension_count_after"]),
            "before_phi": int(second["before_phi"]),
            "after_phi": int(second["after_phi"]),
            "proof_bytes": int(second["proof_bytes"]),
            "result_fingerprint": second["result_fingerprint"],
        },
        "second_reentry": {
            "status": second_reentry["status"],
            "mode": second_reentry.get("mode"),
        },
        "historical_extension_ids": [*historical_extensions_before, second_extension],
        "resource_observation": {
            "max_state_units_seen": max(all_state_units),
            "root_state_cap": root_state_cap,
            "within_root_state_cap": max(all_state_units) <= root_state_cap,
            "cumulative_proof_bytes": int(first["proof_bytes"]) + int(second["proof_bytes"]),
            "cumulative_work": _cumulative_work(first, second),
            "note": "Finite measured ledger only; no universal polynomial exponent is inferred from this specimen."
        },
        "scientific_boundary": {
            "finite_specimen_only": True,
            "root_budget_rebased": False,
            "runtime_grammar_changed": False,
            "universal_second_move_availability": "OPEN",
            "universal_iterability": "OPEN",
            "universal_GPEI_preservation": "OPEN",
            "arbitrary_CNF_totality": "OPEN",
            "P_VS_NP": P_VS_NP,
        },
    }


def main() -> int:
    report = run()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
