#!/usr/bin/env python3
"""Standalone proof object for one exact JEC extension-progress move.

The producer may search. The verifier may not: it receives one proposed proof
object and deterministically replays the definitional extension, every exact
elimination, the frozen state cap, and strict progress-potential decrease.

Two producer modes are supported:
  * ROOT_RESTORE_V2: one exact OR-pair extension + one exact root elimination;
  * EXTENSION_TAIL_V3: one exact OR-pair extension + a frozen two-elimination
    chain on an already replayed engine state with no live roots.

The INITIAL_CONTEXT helper is the stage-4 primitive used on a fresh CNF after
stages 1-3 return OPEN. Historical engine-state extraction is only a regression
bridge and does not by itself prove universal availability.

P_VS_NP remains OPEN.
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
from experiments.direct import janus_unified_macro_restore_v3 as v3

ALLOWED_MODES = {"ROOT_RESTORE_V2", "EXTENSION_TAIL_V3"}
ALLOWED_CONTEXTS = {"INITIAL_CONTEXT", "ENGINE_CONTEXT"}


def _cnf_json(cnf: base.CNF) -> list[list[int]]:
    return [list(clause) for clause in cnf]


def _cnf_from_json(rows) -> base.CNF:
    return base.canon_cnf(rows)


def _phi(cnf: base.CNF, root_vars: tuple[int, ...], N: int, extension_exponent: int) -> int:
    live = set(base.vars_of(cnf))
    r = sum(1 for variable in root_vars if variable in live)
    v = len(live)
    kmax = N ** extension_exponent
    return r * (len(root_vars) + kmax + 1) + v


def _snapshot(ledger: base.Ledger) -> dict[str, int]:
    names = (
        "proposal_work",
        "certificate_discovery_work",
        "verification_work",
        "elimination_pair_work",
        "recompression_work",
    )
    return {name: int(getattr(ledger, name)) for name in names}


def _delta(before: dict[str, int], after: dict[str, int]) -> dict[str, int]:
    return {name: int(after[name] - before[name]) for name in before}


def _normalize_macro_certificate(certificate: dict) -> dict:
    normalized = dict(certificate)
    normalized["kind"] = "B2_OR_PAIR_MACRO_EXHAUSTIVE_V2"
    return normalized


def _step(before: base.CNF, pivot: int, after: base.CNF, stats: dict) -> dict:
    return {
        "pivot": int(pivot),
        "before_fingerprint": base.fingerprint(before),
        "after_fingerprint": base.fingerprint(after),
        "before_cnf": _cnf_json(before),
        "after_cnf": _cnf_json(after),
        "elimination_pairs": int(stats.get("pairs", 0)),
    }


def _assemble_proof(
    state: base.EngineState,
    *,
    mode: str,
    macro_cnf: base.CNF,
    macro_certificate: dict,
    elimination_steps: list[dict],
    discovery_delta: dict[str, int],
    context_mode: str,
) -> dict:
    if mode not in ALLOWED_MODES or context_mode not in ALLOWED_CONTEXTS:
        raise ValueError("UNSUPPORTED_PROOF_GRAMMAR")
    before = state.residual
    after = _cnf_from_json(elimination_steps[-1]["after_cnf"])
    root_vars = tuple(int(v) for v in state.root_vars)
    before_phi = _phi(before, root_vars, state.N, state.extension_exponent)
    after_phi = _phi(after, root_vars, state.N, state.extension_exponent)
    proof = {
        "schema": "JANUS/C025/JEC-EXTENSION-PROGRESS-PROOF/v1",
        "kind": "JANUS_JEC_EXTENSION_PROGRESS_PROOF",
        "mode": mode,
        "context_mode": context_mode,
        "source_fingerprint": base.fingerprint(before),
        "source_cnf": _cnf_json(before),
        "root_fingerprint": base.fingerprint(state.root),
        "root_cnf": _cnf_json(state.root),
        "root_vars": list(root_vars),
        "N": int(state.N),
        "cap_exponent": int(state.cap_exponent),
        "extension_exponent": int(state.extension_exponent),
        "state_cap": int(state.state_cap),
        "extension_cap": int(state.extension_cap),
        "extension_count_before": int(state.ledger.extension_count),
        "extension_count_after": int(state.ledger.extension_count + 1),
        "macro_cnf": _cnf_json(macro_cnf),
        "macro_certificate": _normalize_macro_certificate(macro_certificate),
        "elimination_steps": elimination_steps,
        "result_cnf": _cnf_json(after),
        "result_fingerprint": base.fingerprint(after),
        "before_phi": int(before_phi),
        "after_phi": int(after_phi),
        "strict_progress": bool(after_phi < before_phi),
        "discovery_ledger_delta": discovery_delta,
        "scientific_boundary": {
            "proof_object_certifies_one_progress_move_only": True,
            "universal_move_availability_proved": False,
            "recursive_branching": False,
            "heuristic_promotion": False,
            "P_VS_NP": "OPEN",
        },
    }
    proof["proof_bytes"] = len(json.dumps(proof, sort_keys=True, separators=(",", ":")).encode())
    return proof


def build_from_state(state: base.EngineState, *, context_mode: str = "ENGINE_CONTEXT") -> dict | None:
    """Search one exact v2/v3 move from a frozen EngineState and package it."""
    before_ledger = _snapshot(state.ledger)

    root_move = v2.discover_macro_restore_v2(state)
    if root_move is not None:
        macro_cnf, pivot, after, macro_certificate, stats = root_move
        proof = _assemble_proof(
            state,
            mode="ROOT_RESTORE_V2",
            macro_cnf=macro_cnf,
            macro_certificate=macro_certificate,
            elimination_steps=[_step(macro_cnf, pivot, after, stats)],
            discovery_delta=_delta(before_ledger, _snapshot(state.ledger)),
            context_mode=context_mode,
        )
        if not verify_extension_progress_proof(state.residual, proof, require_initial_context=(context_mode == "INITIAL_CONTEXT")):
            raise AssertionError("ROOT_RESTORE_PROOF_FAILED_STANDALONE_VERIFIER")
        return proof

    tail_plan = v3.discover_extension_tail_plan_v3(state)
    if tail_plan is None:
        return None
    steps = [
        _step(before_step, pivot, after_step, stats)
        for before_step, pivot, after_step, stats in zip(
            tail_plan.before_each_elim,
            tail_plan.pivots,
            tail_plan.after_each_elim,
            tail_plan.elim_stats,
        )
    ]
    proof = _assemble_proof(
        state,
        mode="EXTENSION_TAIL_V3",
        macro_cnf=tail_plan.macro_cnf,
        macro_certificate=tail_plan.macro_cert,
        elimination_steps=steps,
        discovery_delta=_delta(before_ledger, _snapshot(state.ledger)),
        context_mode=context_mode,
    )
    if not verify_extension_progress_proof(state.residual, proof, require_initial_context=False):
        raise AssertionError("EXTENSION_TAIL_PROOF_FAILED_STANDALONE_VERIFIER")
    return proof


def initial_state(raw_clauses, *, cap_exponent: int = 2, extension_exponent: int = 1) -> base.EngineState:
    root = base.canon_cnf(raw_clauses)
    ledger = base.Ledger()
    return base.EngineState(
        root=root,
        residual=root,
        fixed_assignment={},
        root_vars=base.vars_of(root),
        extension_defs=[],
        elimination_history=[],
        seen=set(),
        N=base.input_size_units(root),
        cap_exponent=cap_exponent,
        extension_exponent=extension_exponent,
        ledger=ledger,
    )


def discover_initial_extension_progress(
    raw_clauses,
    *,
    cap_exponent: int = 2,
    extension_exponent: int = 1,
) -> dict | None:
    state = initial_state(
        raw_clauses,
        cap_exponent=cap_exponent,
        extension_exponent=extension_exponent,
    )
    return build_from_state(state, context_mode="INITIAL_CONTEXT")


def verify_extension_progress_proof(
    raw_clauses,
    proof: dict,
    *,
    require_initial_context: bool = True,
) -> bool:
    """Verify one proposed progress proof without running discovery."""
    try:
        source = base.canon_cnf(raw_clauses)
        if proof.get("kind") != "JANUS_JEC_EXTENSION_PROGRESS_PROOF":
            return False
        mode = proof.get("mode")
        context_mode = proof.get("context_mode")
        if mode not in ALLOWED_MODES or context_mode not in ALLOWED_CONTEXTS:
            return False
        if proof.get("source_fingerprint") != base.fingerprint(source):
            return False
        if _cnf_from_json(proof.get("source_cnf", [])) != source:
            return False

        root = _cnf_from_json(proof.get("root_cnf", []))
        root_vars = tuple(int(v) for v in proof.get("root_vars", []))
        if root_vars != base.vars_of(root):
            return False
        if proof.get("root_fingerprint") != base.fingerprint(root):
            return False

        N = int(proof["N"])
        cap_exponent = int(proof["cap_exponent"])
        extension_exponent = int(proof["extension_exponent"])
        if N < 2 or cap_exponent < 1 or extension_exponent < 0:
            return False
        if N != base.input_size_units(root):
            return False
        if int(proof["state_cap"]) != N ** cap_exponent:
            return False
        if int(proof["extension_cap"]) != N ** extension_exponent:
            return False
        if int(proof["extension_count_after"]) != int(proof["extension_count_before"]) + 1:
            return False
        if int(proof["extension_count_before"]) < 0:
            return False
        if int(proof["extension_count_after"]) > int(proof["extension_cap"]):
            return False

        if require_initial_context:
            if context_mode != "INITIAL_CONTEXT":
                return False
            if root != source:
                return False
            if int(proof["extension_count_before"]) != 0:
                return False

        cap = int(proof["state_cap"])
        if base.state_units(source) > cap:
            return False
        macro_cnf = _cnf_from_json(proof["macro_cnf"])
        if base.state_units(macro_cnf) > cap:
            return False
        macro_certificate = _normalize_macro_certificate(proof["macro_certificate"])
        if not v2.verify_or_pair_v2(source, macro_cnf, macro_certificate):
            return False
        extension = int(macro_certificate["extension"])
        if extension in set(base.vars_of(source)):
            return False

        current = macro_cnf
        steps = proof.get("elimination_steps", [])
        expected_length = 1 if mode == "ROOT_RESTORE_V2" else 2
        if len(steps) != expected_length:
            return False
        pivots = [int(row["pivot"]) for row in steps]
        if mode == "ROOT_RESTORE_V2":
            if pivots[0] not in set(root_vars):
                return False
        else:
            source_vars = set(base.vars_of(source))
            if len(set(pivots)) != 2:
                return False
            if any(pivot not in source_vars for pivot in pivots):
                return False
            if extension in pivots:
                return False

        for row in steps:
            before_step = _cnf_from_json(row["before_cnf"])
            after_step = _cnf_from_json(row["after_cnf"])
            pivot = int(row["pivot"])
            if before_step != current:
                return False
            if row.get("before_fingerprint") != base.fingerprint(before_step):
                return False
            if row.get("after_fingerprint") != base.fingerprint(after_step):
                return False
            if base.state_units(before_step) > cap or base.state_units(after_step) > cap:
                return False
            rebuilt, stats = base.eliminate_var_capped(before_step, pivot, cap)
            if rebuilt is None or rebuilt != after_step:
                return False
            if not base.verify_elimination_transition(before_step, pivot, after_step, cap):
                return False
            if int(row.get("elimination_pairs", -1)) != int(stats.get("pairs", 0)):
                return False
            current = after_step

        result = _cnf_from_json(proof["result_cnf"])
        if result != current or proof.get("result_fingerprint") != base.fingerprint(result):
            return False

        before_phi = _phi(source, root_vars, N, extension_exponent)
        after_phi = _phi(result, root_vars, N, extension_exponent)
        if int(proof["before_phi"]) != before_phi or int(proof["after_phi"]) != after_phi:
            return False
        if not (after_phi < before_phi and proof.get("strict_progress") is True):
            return False

        return True
    except (AssertionError, KeyError, TypeError, ValueError):
        return False


def main() -> int:
    raw = ((1, 2, 3), (-1, 4))
    proof = discover_initial_extension_progress(raw)
    if proof is None:
        raise AssertionError("SMOKE_EXPECTED_ONE_EXTENSION_PROGRESS_PROOF")
    if not verify_extension_progress_proof(raw, proof, require_initial_context=True):
        raise AssertionError("SMOKE_EXTENSION_PROGRESS_VERIFIER_FAILED")
    print(json.dumps(proof, indent=2, sort_keys=True))
    print("P_VS_NP = OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
