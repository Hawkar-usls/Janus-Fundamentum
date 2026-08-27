#!/usr/bin/env python3
"""JANUS PIRC theorem-mode decision core v0.4.

Successor to v0.3 with one theorem-driven correction: historical extension
budget is N^2 instead of N.  This change is justified by the append-only proof
C025_TOTALITY_REDUCTION_LOW_VOLUME_AND_EXTENSION_BUDGET_2026-08-27.json:
under the frozen v2/v3 grammar at most n v2 macros and at most n v3 macros can
succeed, hence at most 2n<=2N<=N^2 extensions are ever introduced (N>=2).
Therefore the N^2 guard is polynomial and provably nonbinding for this grammar.

Decision truth remains separate from witness reconstruction.  Universal
totality is NOT proved; OPEN remains a valid output.  P_VS_NP remains OPEN.
"""
from __future__ import annotations

import json
from typing import Sequence

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_unified_macro_restore_v2 as v2
from experiments.direct import janus_unified_macro_restore_v3 as v3
from experiments.direct import janus_matching_hall_escape as hall
from experiments.direct import janus_one_variable_separator_escape as stage3
from experiments.direct import janus_theorem_input_normal_form as input_nf

P_VS_NP = "OPEN"


def _decision_result(state: base.EngineState, normal_form: input_nf.DenseInputNormalForm,
                     status: str, reason: str, *, missing_bridge: str | None = None) -> dict:
    out = base._result(state, status, reason, witness=None, missing_bridge=missing_bridge)
    out["schema"] = "JANUS/C025/PIRC-DECISION-CORE/v0.4"
    out["decision_core_version"] = "PIRC_DECISION_CORE_V0_4"
    out["source_fingerprint"] = base.fingerprint(normal_form.source)
    out["normalized_root_fingerprint"] = base.fingerprint(normal_form.normalized)
    out["source_binary_units"] = int(normal_form.source_binary_units)
    out["normalized_internal_N"] = int(normal_form.normalized_internal_N)
    out["dense_variable_normalization"] = True
    out["witness_layer_required_for_decision"] = False
    out["extension_budget_theorem"] = "N2_EXTENSION_CAP_NONBINDING"
    out["scientific_boundary"].update({
        "decision_vs_witness_separated": True,
        "extension_cap_nonbinding_proof_recorded": True,
        "universal_totality": "OPEN",
        "polynomial_partial_decider_only_until_totality_proved": True,
        "P_VS_NP": P_VS_NP,
    })
    return out


def solve_decision_core(
    clauses: Sequence[Sequence[int]],
    *,
    cap_exponent: int = 2,
    extension_exponent: int = 2,
    bounded_resolution_width: int = 3,
) -> dict:
    if cap_exponent != 2 or extension_exponent != 2 or bounded_resolution_width != 3:
        raise ValueError("v0.4 theorem core freezes C=2, extension exponent=2, resolution width=3")

    normal_form = input_nf.dense_normalize(clauses)
    root = normal_form.normalized
    ledger = base.Ledger()
    state = base.EngineState(
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
    if state.N != normal_form.normalized_internal_N:
        raise AssertionError("THEOREM_INPUT_N_DRIFT")

    ledger.event(
        "ROOT_DECISION_CORE_V0_4",
        source_fingerprint=base.fingerprint(normal_form.source),
        normalized_fingerprint=base.fingerprint(root),
        source_binary_units=normal_form.source_binary_units,
        N=state.N,
        n_vars=len(state.root_vars),
        n_clauses=len(root),
        state_cap=state.state_cap,
        extension_cap=state.extension_cap,
    )

    if base.state_units(root) > state.state_cap:
        return _decision_result(state, normal_form, "OPEN", "ROOT_EXCEEDS_FIXED_CAP")

    while True:
        state.note_state()
        before_phi = state.progress_phi()

        reduced, implied, ok, up_work = base.unit_propagate(state.residual)
        ledger.verification_work += up_work
        if implied:
            for variable, bit in implied.items():
                if variable in state.fixed_assignment and state.fixed_assignment[variable] != bit:
                    return _decision_result(state, normal_form, "UNSAT", "UNIT_ASSIGNMENT_CONTRADICTION")
                state.fixed_assignment[variable] = bit
            after_phi = state.progress_phi(reduced)
            if after_phi >= before_phi:
                return _decision_result(state, normal_form, "OPEN", "NONDECREASING_UNIT_PROGRESS")
            ledger.event("UNIT_PROPAGATION", implied=dict(sorted(implied.items())), before_phi=before_phi, after_phi=after_phi)
            state.residual = reduced
            ledger.recompression_work += base.state_units(reduced)
            if not ok or () in reduced:
                return _decision_result(state, normal_form, "UNSAT", "UNIT_REFUTATION")
            continue
        if not ok or () in state.residual:
            return _decision_result(state, normal_form, "UNSAT", "UNIT_REFUTATION")

        if not state.residual:
            return _decision_result(state, normal_form, "SAT", "EMPTY_RESIDUAL_EXACT_DECISION")

        hall_result = hall.solve_matching_hall_escape(state.residual)
        if hall_result.get("status") in {"SAT", "UNSAT"}:
            if not hall.verify_matching_hall_escape(state.residual, hall_result):
                raise AssertionError("MATCHING_HALL_TERMINAL_VERIFIER_FAILED")
            ledger.event("CERTIFICATE_PORTFOLIO_MATCHING_HALL", decision=hall_result["status"], certificate=hall_result.get("certificate"))
            return _decision_result(state, normal_form, hall_result["status"], "MATCHING_HALL_EXACT_DECISION")

        separator = stage3.solve_one_variable_escape(state.residual)
        if separator.get("status") in {"SAT", "UNSAT"}:
            if not stage3.verify_one_variable_escape(state.residual, separator):
                raise AssertionError("ONE_VARIABLE_ESCAPE_TERMINAL_VERIFIER_FAILED")
            ledger.event(
                "CERTIFICATE_PORTFOLIO_ONE_VARIABLE_ESCAPE",
                decision=separator["status"],
                mode=separator.get("mode"),
                selected_variable=separator.get("selected_variable"),
            )
            return _decision_result(state, normal_form, separator["status"], "ONE_VARIABLE_EXACT_DECISION")

        two = base.solve_2sat_exact(state.residual)
        if two is not None:
            sat, _assignment, cert = two
            ledger.two_sat_work += max(1, len(state.residual) + len(base.vars_of(state.residual)))
            ledger.event("CERTIFICATE_PORTFOLIO_2SAT", certificate=cert)
            return _decision_result(state, normal_form, "SAT" if sat else "UNSAT", "2SAT_CERTIFIED_DECISION")

        gf2 = base.solve_gf2_explicit_exact(state.residual)
        if gf2 is not None:
            sat, _assignment, cert = gf2
            ledger.gf2_work += max(1, len(state.residual) * max(1, len(base.vars_of(state.residual))))
            ledger.event("CERTIFICATE_PORTFOLIO_GF2", certificate=cert)
            return _decision_result(state, normal_form, "SAT" if sat else "UNSAT", "GF2_CERTIFIED_DECISION")

        refuted, width_cert = base.bounded_width_resolution_refutes(state.residual, bounded_resolution_width)
        ledger.bounded_width_resolution_work += int(width_cert.get("work", 0))
        if refuted:
            ledger.event("CERTIFICATE_PORTFOLIO_BOUNDED_RESOLUTION", certificate=width_cert)
            return _decision_result(state, normal_form, "UNSAT", "BOUNDED_WIDTH_RESOLUTION_REFUTATION")

        elim = base.first_capped_elimination(state)
        if elim is not None:
            pivot, after, stats = elim
            after_phi = state.progress_phi(after)
            if after_phi >= before_phi:
                return _decision_result(state, normal_form, "OPEN", "PROGRESS_GATE_REJECTED_ELIMINATION")
            state.elimination_history.append(base.ElimSnapshot(state.residual, pivot, "PURE_ELIM"))
            ledger.question_count += 1
            ledger.event(
                "AKINATOR_EXACT_ELIMINATION",
                pivot=pivot,
                before_fingerprint=base.fingerprint(state.residual),
                after_fingerprint=base.fingerprint(after),
                before_phi=before_phi,
                after_phi=after_phi,
                stats=stats,
            )
            state.residual = after
            ledger.recompression_work += base.state_units(after)
            continue

        root_restored = v2.discover_macro_restore_v2(state)
        if root_restored is not None:
            macro_cnf, pivot, after, macro_cert, elim_stats = root_restored
            after_phi = state.progress_phi(after, ledger.extension_count + 1)
            if after_phi >= before_phi:
                return _decision_result(state, normal_form, "OPEN", "PROGRESS_GATE_REJECTED_MACRO_RESTORE")
            state.elimination_history.append(base.ElimSnapshot(macro_cnf, pivot, "JEC_MACRO_PLUS_ELIM"))
            state.extension_defs.append(macro_cert)
            ledger.extension_count += 1
            if ledger.extension_count > 2 * len(state.root_vars):
                raise AssertionError("PROVED_2N_EXTENSION_BOUND_VIOLATED")
            ledger.extension_definition_bytes += len(json.dumps(macro_cert, sort_keys=True).encode())
            ledger.question_count += 1
            ledger.event(
                "JEC_MACRO_RESTORE_CAP",
                macro=macro_cert,
                pivot=pivot,
                before_fingerprint=base.fingerprint(state.residual),
                macro_fingerprint=base.fingerprint(macro_cnf),
                after_fingerprint=base.fingerprint(after),
                before_phi=before_phi,
                after_phi=after_phi,
                elimination=elim_stats,
            )
            state.residual = after
            ledger.recompression_work += base.state_units(macro_cnf) + base.state_units(after)
            continue

        tail_plan = v3.discover_extension_tail_plan_v3(state)
        if tail_plan is not None:
            v3._append_plan(state, tail_plan, before_phi)
            if ledger.extension_count > 2 * len(state.root_vars):
                raise AssertionError("PROVED_2N_EXTENSION_BOUND_VIOLATED")
            continue

        return _decision_result(
            state,
            normal_form,
            "OPEN",
            "NO_CAPPED_CERTIFIED_MOVE",
            missing_bridge="HIGH_VOLUME_RESCUE_TOTALITY",
        )


def selftest() -> None:
    fixtures = (
        ("SAT_SIMPLE", ((1, 2), (-1, 2)), "SAT"),
        ("UNSAT_UNITS", ((1,), (-1,)), "UNSAT"),
        ("SAT_3CNF", ((1, 2, 3), (-1, 2, 3), (1, -2, 3)), "SAT"),
    )
    for name, cnf, expected in fixtures:
        result = solve_decision_core(cnf)
        assert result["status"] == expected, (name, result)
        assert result["extension_cap"] == result["N"] ** 2
        assert result["scientific_boundary"]["P_VS_NP"] == "OPEN"

    result = solve_decision_core(hall._php(5, 4))
    assert result["status"] == "UNSAT"
    assert result["reason"] == "MATCHING_HALL_EXACT_DECISION"

    print("JANUS_PIRC_DECISION_CORE_V0_4_SELFTEST=PASS")
    print("N2_EXTENSION_CAP_NONBINDING_FIREWALL=PASS")
    print("HIGH_VOLUME_RESCUE_TOTALITY=OPEN")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    selftest()
