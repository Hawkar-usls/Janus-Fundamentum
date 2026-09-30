#!/usr/bin/env python3
"""JANUS exact one-variable separator/backdoor escape.

When a connected CNF is not recognized by the current exact algebra selector,
try every live variable deterministically. For each bit:
  F -> exact restriction -> deterministic unit propagation
    -> exact component/algebra escape on the residual.

A variable closes the instance only when:
  * at least one branch has a verified SAT certificate, or
  * both branches have verified UNSAT certificates.

No recursive branching is performed here. The search adds only O(n) branch
attempts on top of the currently admitted exact subsolvers. This establishes
an exact one-variable escape rule, not a theorem that every CNF has such a
variable. P_VS_NP remains OPEN.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_instance_specific_algebraic_escape as component_escape


def _solve_branch(cnf: base.CNF, variable: int, bit: int) -> dict:
    restricted = base.restrict(cnf, variable, bit)
    residual, implied, consistent, work = base.unit_propagate(restricted)
    if not consistent:
        return {
            "bit": bit,
            "restricted_fingerprint": base.fingerprint(restricted),
            "unit_propagation_work": work,
            "unit_implied": dict(sorted(implied.items())),
            "residual_fingerprint": base.fingerprint(residual),
            "status": "UNSAT",
            "mode": "UNIT_PROPAGATION_CONTRADICTION",
            "escape_result": None,
        }

    result = component_escape.solve_by_component_escape(residual)
    if result.get("status") in {"SAT", "UNSAT"}:
        if not component_escape.verify_escape_result(residual, result):
            raise AssertionError("BRANCH_COMPONENT_ESCAPE_VERIFIER_FAILED")
    return {
        "bit": bit,
        "restricted_fingerprint": base.fingerprint(restricted),
        "unit_propagation_work": work,
        "unit_implied": dict(sorted(implied.items())),
        "residual_fingerprint": base.fingerprint(residual),
        "status": result.get("status", "OPEN"),
        "mode": "RESIDUAL_EXACT_ESCAPE",
        "escape_result": result,
    }


def solve_one_variable_escape(raw_clauses) -> dict:
    cnf = base.canon_cnf(raw_clauses)
    variables = base.vars_of(cnf)
    ledger = {
        "input_size_units_N": base.input_size_units(cnf),
        "input_state_units": base.state_units(cnf),
        "variables_considered": 0,
        "branch_attempts": 0,
        "unit_propagation_work": 0,
        "certificate_bytes": 0,
        "verification_work": 0,
        "progress_steps": 0,
    }

    direct = component_escape.solve_by_component_escape(cnf)
    if direct.get("status") in {"SAT", "UNSAT"}:
        if not component_escape.verify_escape_result(cnf, direct):
            raise AssertionError("DIRECT_ESCAPE_VERIFIER_FAILED")
        ledger["progress_steps"] = 1
        ledger["verification_work"] = max(1, base.state_units(cnf))
        ledger["certificate_bytes"] = len(
            json.dumps(direct, sort_keys=True, separators=(",", ":")).encode()
        )
        return {
            "kind": "JANUS_ONE_VARIABLE_SEPARATOR_ESCAPE",
            "source_fingerprint": base.fingerprint(cnf),
            "status": direct["status"],
            "mode": "DIRECT_EXACT_ESCAPE",
            "selected_variable": None,
            "branches": [],
            "direct_result": direct,
            "ledger": ledger,
            "P_VS_NP": "OPEN",
        }

    for variable in variables:
        ledger["variables_considered"] += 1
        branches = []
        for bit in (0, 1):
            branch = _solve_branch(cnf, variable, bit)
            branches.append(branch)
            ledger["branch_attempts"] += 1
            ledger["unit_propagation_work"] += int(branch["unit_propagation_work"])

        statuses = [branch["status"] for branch in branches]
        decision = None
        reason = None
        if "SAT" in statuses:
            decision = "SAT"
            reason = "VERIFIED_SAT_SHANNON_BRANCH"
        elif statuses == ["UNSAT", "UNSAT"]:
            decision = "UNSAT"
            reason = "BOTH_SHANNON_BRANCHES_VERIFIED_UNSAT"

        if decision is None:
            continue

        ledger["progress_steps"] = 1
        ledger["verification_work"] += 2 * max(1, base.state_units(cnf))
        output = {
            "kind": "JANUS_ONE_VARIABLE_SEPARATOR_ESCAPE",
            "source_fingerprint": base.fingerprint(cnf),
            "status": decision,
            "mode": "ONE_VARIABLE_EXACT_SHANNON_ESCAPE",
            "selected_variable": variable,
            "branches": branches,
            "direct_result": direct,
            "reason": reason,
            "ledger": ledger,
            "search_rule": "VARIABLES_ASCENDING__BITS_0_THEN_1__FIRST_EXACT_CLOSURE",
            "recursive_branching": False,
            "P_VS_NP": "OPEN",
        }
        output["ledger"]["certificate_bytes"] = len(
            json.dumps(branches, sort_keys=True, separators=(",", ":")).encode()
        )
        return output

    return {
        "kind": "JANUS_ONE_VARIABLE_SEPARATOR_ESCAPE",
        "source_fingerprint": base.fingerprint(cnf),
        "status": "OPEN",
        "mode": "NO_ONE_VARIABLE_EXACT_ESCAPE",
        "selected_variable": None,
        "branches": [],
        "direct_result": direct,
        "ledger": ledger,
        "recursive_branching": False,
        "reason": "NO_VARIABLE_CLOSED_THE_INSTANCE_WITH_CURRENT_EXACT_SUBSOLVERS",
        "P_VS_NP": "OPEN",
    }


def _verify_branch(cnf: base.CNF, variable: int, branch: dict) -> bool:
    bit = int(branch["bit"])
    restricted = base.restrict(cnf, variable, bit)
    if branch.get("restricted_fingerprint") != base.fingerprint(restricted):
        return False
    residual, implied, consistent, work = base.unit_propagate(restricted)
    if branch.get("unit_propagation_work") != work:
        return False
    supplied_implied = {int(k): int(v) for k, v in branch.get("unit_implied", {}).items()}
    if supplied_implied != implied:
        return False
    if branch.get("residual_fingerprint") != base.fingerprint(residual):
        return False

    if not consistent:
        return (
            branch.get("status") == "UNSAT"
            and branch.get("mode") == "UNIT_PROPAGATION_CONTRADICTION"
        )

    result = branch.get("escape_result")
    if not isinstance(result, dict):
        return branch.get("status") == "OPEN"
    if result.get("status") != branch.get("status"):
        return False
    if result.get("status") in {"SAT", "UNSAT"}:
        return component_escape.verify_escape_result(residual, result)
    return result.get("status") == "OPEN"


def verify_one_variable_escape(raw_clauses, result: dict) -> bool:
    try:
        cnf = base.canon_cnf(raw_clauses)
        if result.get("kind") != "JANUS_ONE_VARIABLE_SEPARATOR_ESCAPE":
            return False
        if result.get("source_fingerprint") != base.fingerprint(cnf):
            return False
        mode = result.get("mode")
        status = result.get("status")

        if mode == "DIRECT_EXACT_ESCAPE":
            direct = result.get("direct_result")
            return (
                status in {"SAT", "UNSAT"}
                and direct.get("status") == status
                and component_escape.verify_escape_result(cnf, direct)
            )

        if mode == "NO_ONE_VARIABLE_EXACT_ESCAPE":
            return status == "OPEN"

        if mode != "ONE_VARIABLE_EXACT_SHANNON_ESCAPE":
            return False
        variable = int(result["selected_variable"])
        if variable not in base.vars_of(cnf):
            return False
        branches = result.get("branches", [])
        if len(branches) != 2 or [int(row["bit"]) for row in branches] != [0, 1]:
            return False
        if not all(_verify_branch(cnf, variable, branch) for branch in branches):
            return False
        statuses = [branch["status"] for branch in branches]
        if status == "SAT":
            return "SAT" in statuses
        if status == "UNSAT":
            return statuses == ["UNSAT", "UNSAT"]
        return False
    except (AssertionError, KeyError, TypeError, ValueError):
        return False


def main() -> int:
    smoke = ((1, 2, 3), (-1, -2))
    result = solve_one_variable_escape(smoke)
    if result["status"] != "OPEN" and not verify_one_variable_escape(smoke, result):
        raise AssertionError("ONE_VARIABLE_ESCAPE_SMOKE_VERIFIER_FAILED")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
