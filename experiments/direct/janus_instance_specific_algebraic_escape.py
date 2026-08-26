#!/usr/bin/env python3
"""JANUS exact instance-specific algebraic escape by component decomposition.

A RAW CNF enters without a family label. If the current global exact algebra
selector returns OPEN, this module computes the exact primal connected
components. Because clauses in different components share no variables, the
formula is their conjunction and each component may be represented by a
*different* exact algebra.

Soundness:
  * UNSAT if any independently verified component is UNSAT.
  * SAT only if every component is independently verified SAT.
  * Otherwise OPEN.

This is an exact B_1 (+) ... (+) B_k decomposition rule. It does not prove that
all connected CNFs admit such a decomposition and therefore does not establish
arbitrary-CNF polynomial solvability. P_VS_NP remains OPEN.
"""
from __future__ import annotations

from collections import deque
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_b_to_a_exact_algebra_selector as selector


def component_cnf_partition(raw_clauses) -> tuple[base.CNF, ...]:
    cnf = base.canon_cnf(raw_clauses)
    if () in cnf:
        return (((),),)
    variables = base.vars_of(cnf)
    if not variables:
        return tuple()

    adjacency = {variable: set() for variable in variables}
    for clause in cnf:
        scope = sorted({abs(literal) for literal in clause})
        if not scope:
            continue
        anchor = scope[0]
        for variable in scope[1:]:
            adjacency[anchor].add(variable)
            adjacency[variable].add(anchor)

    component_of = {}
    components = []
    for root in variables:
        if root in component_of:
            continue
        index = len(components)
        members = []
        queue = deque([root])
        component_of[root] = index
        while queue:
            variable = queue.popleft()
            members.append(variable)
            for neighbor in sorted(adjacency[variable]):
                if neighbor not in component_of:
                    component_of[neighbor] = index
                    queue.append(neighbor)
        components.append(tuple(sorted(members)))

    rows: list[list[base.Clause]] = [[] for _ in components]
    for clause in cnf:
        scope = [abs(literal) for literal in clause]
        if not scope:
            rows = [[()]]
            break
        index = component_of[scope[0]]
        if any(component_of[variable] != index for variable in scope):
            raise AssertionError("CLAUSE_CROSSES_COMPUTED_COMPONENTS")
        rows[index].append(clause)

    partition = tuple(
        base.canon_cnf(row)
        for _, row in sorted(
            zip(components, rows),
            key=lambda item: item[0][0] if item[0] else -1,
        )
    )
    rebuilt = base.canon_cnf(clause for component in partition for clause in component)
    if rebuilt != cnf:
        raise AssertionError("COMPONENT_PARTITION_EXACT_REPLAY_FAILED")
    return partition


def _public_selector_record(component: base.CNF, result: dict) -> dict:
    return {
        "component_fingerprint": base.fingerprint(component),
        "component_variables": list(base.vars_of(component)),
        "component_clause_count": len(component),
        "status": result.get("status"),
        "selected_algebra": result.get("selected_algebra"),
        "selector_result": result,
    }


def solve_by_component_escape(raw_clauses) -> dict:
    cnf = base.canon_cnf(raw_clauses)
    N = base.input_size_units(cnf)
    ledger = {
        "input_size_units_N": N,
        "input_state_units": base.state_units(cnf),
        "decomposition_work": sum(max(1, len(clause)) for clause in cnf),
        "selector_calls": 0,
        "component_count": 0,
        "certificate_bytes": 0,
        "verification_work": 0,
        "progress_steps": 0,
    }

    global_result = selector.select_exact_algebra(cnf)
    ledger["selector_calls"] += 1
    if global_result.get("status") in {"SAT", "UNSAT"}:
        if not selector.verify_selector_result(cnf, global_result):
            raise AssertionError("GLOBAL_SELECTOR_CERTIFICATE_FAILED")
        ledger["verification_work"] += max(1, base.state_units(cnf))
        ledger["progress_steps"] = 1
        output = {
            "kind": "JANUS_INSTANCE_SPECIFIC_ALGEBRAIC_ESCAPE",
            "source_fingerprint": base.fingerprint(cnf),
            "status": global_result["status"],
            "mode": "GLOBAL_EXACT_ALGEBRA",
            "global_selector_result": global_result,
            "components": [],
            "ledger": ledger,
            "P_VS_NP": "OPEN",
        }
        output["ledger"]["certificate_bytes"] = len(
            json.dumps(global_result.get("certificate"), sort_keys=True, separators=(",", ":")).encode()
        )
        return output

    partition = component_cnf_partition(cnf)
    ledger["component_count"] = len(partition)
    if len(partition) <= 1:
        return {
            "kind": "JANUS_INSTANCE_SPECIFIC_ALGEBRAIC_ESCAPE",
            "source_fingerprint": base.fingerprint(cnf),
            "status": "OPEN",
            "mode": "CONNECTED_NO_CURRENT_ESCAPE",
            "global_selector_status": global_result.get("status"),
            "components": [],
            "ledger": ledger,
            "reason": "NO_NONTRIVIAL_EXACT_COMPONENT_DECOMPOSITION",
            "P_VS_NP": "OPEN",
        }

    records = []
    all_sat = True
    for component in partition:
        result = selector.select_exact_algebra(component)
        ledger["selector_calls"] += 1
        record = _public_selector_record(component, result)
        records.append(record)

        if result.get("status") in {"SAT", "UNSAT"}:
            verified = selector.verify_selector_result(component, result)
            ledger["verification_work"] += max(1, base.state_units(component))
            record["certificate_verified"] = verified
            if not verified:
                raise AssertionError("COMPONENT_SELECTOR_CERTIFICATE_FAILED")
            if result["status"] == "UNSAT":
                ledger["progress_steps"] = 1
                output = {
                    "kind": "JANUS_INSTANCE_SPECIFIC_ALGEBRAIC_ESCAPE",
                    "source_fingerprint": base.fingerprint(cnf),
                    "status": "UNSAT",
                    "mode": "EXACT_COMPONENT_DIRECT_SUM",
                    "global_selector_status": global_result.get("status"),
                    "components": records,
                    "partition_fingerprints": [base.fingerprint(item) for item in partition],
                    "ledger": ledger,
                    "reason": "VERIFIED_UNSAT_COMPONENT_IN_EXACT_DISJOINT_CONJUNCTION",
                    "P_VS_NP": "OPEN",
                }
                output["ledger"]["certificate_bytes"] = len(
                    json.dumps(records, sort_keys=True, separators=(",", ":")).encode()
                )
                return output
        else:
            record["certificate_verified"] = False
            all_sat = False

    if all_sat and len(records) == len(partition):
        ledger["progress_steps"] = 1
        output = {
            "kind": "JANUS_INSTANCE_SPECIFIC_ALGEBRAIC_ESCAPE",
            "source_fingerprint": base.fingerprint(cnf),
            "status": "SAT",
            "mode": "EXACT_COMPONENT_DIRECT_SUM",
            "global_selector_status": global_result.get("status"),
            "components": records,
            "partition_fingerprints": [base.fingerprint(item) for item in partition],
            "ledger": ledger,
            "reason": "ALL_EXACT_DISJOINT_COMPONENTS_HAVE_VERIFIED_SAT_CERTIFICATES",
            "P_VS_NP": "OPEN",
        }
        output["ledger"]["certificate_bytes"] = len(
            json.dumps(records, sort_keys=True, separators=(",", ":")).encode()
        )
        return output

    return {
        "kind": "JANUS_INSTANCE_SPECIFIC_ALGEBRAIC_ESCAPE",
        "source_fingerprint": base.fingerprint(cnf),
        "status": "OPEN",
        "mode": "PARTIAL_COMPONENT_RECOGNITION",
        "global_selector_status": global_result.get("status"),
        "components": records,
        "partition_fingerprints": [base.fingerprint(item) for item in partition],
        "ledger": ledger,
        "reason": "AT_LEAST_ONE_COMPONENT_REMAINS_OPEN_AND_NO_VERIFIED_UNSAT_COMPONENT_EXISTS",
        "P_VS_NP": "OPEN",
    }


def verify_escape_result(raw_clauses, result: dict) -> bool:
    try:
        cnf = base.canon_cnf(raw_clauses)
        if result.get("kind") != "JANUS_INSTANCE_SPECIFIC_ALGEBRAIC_ESCAPE":
            return False
        if result.get("source_fingerprint") != base.fingerprint(cnf):
            return False
        status = result.get("status")
        mode = result.get("mode")

        if mode == "GLOBAL_EXACT_ALGEBRA":
            global_result = result["global_selector_result"]
            return status == global_result.get("status") and selector.verify_selector_result(cnf, global_result)

        if mode not in {"EXACT_COMPONENT_DIRECT_SUM", "PARTIAL_COMPONENT_RECOGNITION", "CONNECTED_NO_CURRENT_ESCAPE"}:
            return False
        partition = component_cnf_partition(cnf)

        if mode == "CONNECTED_NO_CURRENT_ESCAPE":
            return status == "OPEN" and len(partition) <= 1

        expected_fingerprints = [base.fingerprint(component) for component in partition]
        if result.get("partition_fingerprints") != expected_fingerprints:
            return False
        by_fingerprint = {base.fingerprint(component): component for component in partition}
        verified_statuses = []
        for record in result.get("components", []):
            component = by_fingerprint.get(record.get("component_fingerprint"))
            if component is None:
                return False
            selector_result = record.get("selector_result")
            component_status = selector_result.get("status")
            if component_status in {"SAT", "UNSAT"}:
                if not selector.verify_selector_result(component, selector_result):
                    return False
                verified_statuses.append(component_status)
            else:
                verified_statuses.append("OPEN")

        if status == "UNSAT":
            return "UNSAT" in verified_statuses
        if status == "SAT":
            return len(verified_statuses) == len(partition) and all(item == "SAT" for item in verified_statuses)
        if status == "OPEN":
            return "UNSAT" not in verified_statuses and (
                len(verified_statuses) < len(partition) or any(item == "OPEN" for item in verified_statuses)
            )
        return False
    except (AssertionError, KeyError, TypeError, ValueError):
        return False


def main() -> int:
    smoke = ((1, 2, 3), (-1, -2))
    report = solve_by_component_escape(smoke)
    if not verify_escape_result(smoke, report):
        raise AssertionError("ESCAPE_SMOKE_VERIFIER_FAILED")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
