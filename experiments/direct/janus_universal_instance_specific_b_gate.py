#!/usr/bin/env python3
"""UNIVERSAL_INSTANCE_SPECIFIC_B_EXISTENCE_GATE.

This module is a theorem/accounting gate, not an assumed theorem.

For a RAW CNF it:
  * canonicalizes the instance;
  * measures N and explicit state volume;
  * exposes the extensionalization upper bound 2^w for maximum clause width w;
  * runs the current exact JANUS stack:
      global exact algebra -> exact component direct-sum -> one-variable escape;
  * independently verifies any closed finite-instance result;
  * records whether this ONE instance is decided;
  * keeps the universal gate OPEN until a separate proof establishes one fixed
    polynomial bound and totality for every CNF.

The code is intentionally unable to promote finite success into P=NP.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_one_variable_separator_escape as current_solver


@dataclass
class UniversalLedger:
    input_size_units_N: int
    input_state_units: int
    input_variables: int
    input_clauses: int
    max_clause_width: int
    extensionalization_upper_bound_2_pow_w: int
    minimum_integer_exponent_covering_extensionalization: int
    discovery_work: int = 0
    max_state_units: int = 0
    certificate_bytes: int = 0
    verification_work: int = 0
    progress_steps: int = 0


def _min_poly_exponent(N: int, value: int) -> int:
    if value <= 1:
        return 0
    exponent = 0
    bound = 1
    while bound < value:
        exponent += 1
        bound *= N
    return exponent


def inspect_instance(raw_clauses) -> dict:
    cnf = base.canon_cnf(raw_clauses)
    variables = base.vars_of(cnf)
    state = base.state_units(cnf)
    N = base.input_size_units(cnf)
    width = max((len(clause) for clause in cnf), default=0)
    extensional = 1 << width if width >= 0 else 1

    ledger = UniversalLedger(
        input_size_units_N=N,
        input_state_units=state,
        input_variables=len(variables),
        input_clauses=len(cnf),
        max_clause_width=width,
        extensionalization_upper_bound_2_pow_w=extensional,
        minimum_integer_exponent_covering_extensionalization=_min_poly_exponent(N, extensional),
        max_state_units=state,
    )

    result = current_solver.solve_one_variable_escape(cnf)
    nested_ledger = result.get("ledger", {})
    ledger.discovery_work += (
        int(nested_ledger.get("variables_considered", 0))
        + int(nested_ledger.get("branch_attempts", 0))
        + int(nested_ledger.get("unit_propagation_work", 0))
    )
    ledger.progress_steps = int(nested_ledger.get("progress_steps", 0))

    instance_decision = result.get("status", "OPEN")
    certificate_verified = False
    if instance_decision in {"SAT", "UNSAT"}:
        certificate_verified = current_solver.verify_one_variable_escape(cnf, result)
        if not certificate_verified:
            raise AssertionError("CURRENT_INSTANCE_SOLVER_RETURNED_UNVERIFIED_CERTIFICATE")
        ledger.verification_work = max(
            int(nested_ledger.get("verification_work", 0)),
            max(1, state),
        )
        ledger.certificate_bytes = len(
            json.dumps(result, sort_keys=True, separators=(",", ":")).encode()
        )

    return {
        "schema": "JANUS/C025/UNIVERSAL-INSTANCE-SPECIFIC-B-EXISTENCE-GATE/v2",
        "instance": {
            "fingerprint": base.fingerprint(cnf),
            "decision_with_current_exact_stack": instance_decision,
            "current_solver_mode": result.get("mode"),
            "selected_variable": result.get("selected_variable"),
            "selected_certificate_verified": certificate_verified,
        },
        "current_exact_stack": {
            "stage_1": "GLOBAL_EXACT_ALGEBRA_SELECTOR",
            "stage_2": "EXACT_COMPONENT_DIRECT_SUM",
            "stage_3": "ONE_VARIABLE_EXACT_SHANNON_ESCAPE",
            "recursive_branching": False,
            "finite_instance_result": result,
        },
        "ledger": asdict(ledger),
        "universal_gate": {
            "status": "OPEN",
            "algorithm_totality_for_all_CNF_proved": False,
            "one_fixed_polynomial_discovery_bound_proved": False,
            "one_fixed_polynomial_state_bound_proved": False,
            "one_fixed_polynomial_certificate_bound_proved": False,
            "one_fixed_polynomial_verification_bound_proved": False,
            "one_fixed_polynomial_progress_step_bound_proved": False,
            "unbounded_width_extensionalization_removed": False,
            "connected_instances_without_one_variable_escape": "MAY_RETURN_OPEN",
            "arbitrary_CNF_coverage": "OPEN",
            "P_VS_NP": "OPEN",
        },
        "promotion_firewall": (
            "FINITE_INSTANCE_SUCCESS_MUST_NOT_CHANGE_UNIVERSAL_GATE_STATUS"
        ),
    }


def main() -> int:
    raw = ((1, 2, 3), (-1, -2))
    report = inspect_instance(raw)
    if report["universal_gate"]["status"] != "OPEN":
        raise AssertionError("UNIVERSAL_GATE_ILLEGALLY_PROMOTED")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
