#!/usr/bin/env python3
"""Frozen JANUS P=NP / P!=NP bidirectional threshold run.

This is a finite falsification experiment, not a P-vs-NP proof.
Forward: compare Q1 and proof-carrying BH-Q2 on untouched GT12.
Reverse/Tranception: signed coordinate reversal + polarity inversion, exact
Buzz return replay, and the C025 blocked-vs-interleaved order control.

The run contract was committed before this harness was executed.  No GT12 cap
raise or rule mutation is allowed after seeing the result.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from janus_certified_residual_quotient import run as run_c025
from janus_tear_policy0a_bh_q2_buzz_physarum_signed_singularity_probe import (
    Policy0ABHQ2,
    apply_signed_map,
    invert_signed_map,
    signed_map_roundtrip_ok,
)
from janus_tear_policy0a_graph_tautology_probe import graph_tautology_cnf
from janus_tear_policy0a_q1_lazy_typed_prefilter_probe import Policy0AQ1Lazy

ORDER = 12
STATE_CAP = 20000
CONTRACT_COMMIT = "32c298c766e40915ee4d37e39a4b4172a08d671d"
PARENT_BHQ2_HEAD = "8931f72e2534cb2fd97219788c1491624aaf104d"


def clean_hash(obj: object) -> str:
    payload = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def signed_reverse_copy(cnf, variable_count: int):
    # Tranception is implemented only as an isomorphic adversarial replay:
    # reverse variable coordinates and invert every variable polarity.
    mapping = {
        variable: (variable_count + 1 - variable, True)
        for variable in range(1, variable_count + 1)
    }
    if not signed_map_roundtrip_ok(mapping):
        raise AssertionError("frozen reverse signed map failed literal roundtrip")
    reverse = apply_signed_map(cnf, mapping)
    inverse = invert_signed_map(mapping)
    if apply_signed_map(reverse, inverse) != cnf:
        raise AssertionError("reverse GT12 copy cannot return to original CNF")
    return reverse, mapping


def q1_proxy(result: dict) -> int:
    return int(result["resolution_attempts"]) + int(result["refinement_edge_visits"])


def q2_proxy(result: dict) -> int:
    return (
        int(result["resolution_attempts"])
        + int(result["signed_refinement_edge_visits"])
        + int(result["q0_fallback_refinement_edge_visits"])
    )


def terminal_class(forward: dict, reverse: dict) -> str:
    if forward["answer"] is not None and reverse["answer"] == forward["answer"]:
        return "CERTIFIED_FINITE_HOLDOUT_SURVIVED__ASYMPTOTIC_GATE_OPEN"
    if forward["cap_exceeded"] and reverse["cap_exceeded"]:
        return "OPEN_RUNTIME_CAPABILITY__NO_COMPLEXITY_PROMOTION"
    return "REVERSE_REPLAY_DISAGREEMENT__PROMOTION_BLOCKED"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    # Historical exact controls are replayed unchanged.
    c025 = run_c025()
    if c025["status"] != "PASS":
        raise AssertionError("restored C025 control suite failed")

    equality = c025["equality_order_sensitivity"]
    blocked_order_obstruction_destroyed_by_reverse_control = (
        equality["blocked_budget_status"] == "OPEN"
        and equality["interleaved_budget_status"] == "EXACT"
        and equality["interleaved_witness_valid"]
    )
    if not blocked_order_obstruction_destroyed_by_reverse_control:
        raise AssertionError("mandatory C025 order-sensitivity reverse control changed")

    cnf, variable_count = graph_tautology_cnf(ORDER)
    reverse_cnf, reverse_map = signed_reverse_copy(cnf, variable_count)
    encoding_units = variable_count + len(cnf) + sum(len(clause) for clause in cnf)

    q1_forward_obj = Policy0AQ1Lazy(state_cap=STATE_CAP).solve(cnf, variable_count)
    q2_forward_obj = Policy0ABHQ2(state_cap=STATE_CAP).solve(cnf, variable_count)
    q2_reverse_obj = Policy0ABHQ2(state_cap=STATE_CAP).solve(reverse_cnf, variable_count)

    q1_forward = asdict(q1_forward_obj)
    q2_forward = asdict(q2_forward_obj)
    q2_reverse = asdict(q2_reverse_obj)

    for label, result in (("forward", q2_forward), ("reverse", q2_reverse)):
        if result["buzz_return_checks"] != (
            result["buzz_return_passes"] + result["hawking_escape_count"]
        ):
            raise AssertionError(f"{label} Buzz accounting lost a horizon decision")
        if result["buzz_return_passes"] < result["bytewise_distinct_absorptions"]:
            raise AssertionError(f"{label} absorption without enough return certificates")

    same_boolean_if_terminal = (
        q2_forward["answer"] is None
        or q2_reverse["answer"] is None
        or q2_forward["answer"] == q2_reverse["answer"]
    )
    if not same_boolean_if_terminal:
        raise AssertionError("signed reverse replay changed Boolean terminal")

    final_class = terminal_class(q2_forward, q2_reverse)

    result = {
        "artifact_id": "JANUS-PNP-BIDIRECTIONAL-C025-BHQ2-GT12-RUN-2026-08-18-v1.0",
        "status": "PASS",
        "contract_commit": CONTRACT_COMMIT,
        "parent_bhq2_head": PARENT_BHQ2_HEAD,
        "p_vs_np": "OPEN",
        "holdout": {
            "family": "GRAPH_TAUTOLOGY",
            "order": ORDER,
            "variables": variable_count,
            "clauses": len(cnf),
            "literal_occurrences": sum(len(clause) for clause in cnf),
            "encoding_units": encoding_units,
            "state_cap": STATE_CAP,
            "posthoc_cap_raise_allowed": False,
        },
        "c025_controls": {
            "status": c025["status"],
            "historical_integrity_sha256": c025["integrity"]["sha256"],
            "absorption_compression": c025["absorption_compression"],
            "equality_order_sensitivity": equality,
            "semantic_merge_barrier": c025["semantic_merge_barrier"],
            "chain_positive_control": c025["chain_positive_control"],
            "blocked_order_obstruction_destroyed_by_interleaving": blocked_order_obstruction_destroyed_by_reverse_control,
        },
        "forward_lane": {
            "q1": q1_forward,
            "bh_q2": q2_forward,
            "q1_work_proxy_resolution_plus_refinement_edges": q1_proxy(q1_forward),
            "bh_q2_work_proxy_resolution_plus_signed_and_fallback_refinement_edges": q2_proxy(q2_forward),
        },
        "reverse_tranception_lane": {
            "enabled": True,
            "operator": "BACK -> FORWARD -> LEFT -> RIGHT -> FORWARD -> BACK",
            "implementation": "SIGNED_VARIABLE_COORDINATE_REVERSAL_PLUS_GLOBAL_POLARITY_INVERSION",
            "mapping_digest": clean_hash(reverse_map),
            "exact_cnf_roundtrip": True,
            "bh_q2": q2_reverse,
            "same_boolean_if_both_terminal": same_boolean_if_terminal,
            "rules_mutated_after_forward": False,
        },
        "p_equals_np_lane": {
            "finite_evidence": "BH-Q2/Q1 GT12 result plus C025 certified absorption control",
            "general_all_input_polynomial_gate": False,
            "promotion": "BLOCKED_FINITE_RUN_CANNOT_PROVE_P_EQUALS_NP",
        },
        "p_not_equals_np_lane": {
            "finite_evidence": "GT12 capability result plus C025 continuation-width controls",
            "blocked_order_false_lower_bound_control": "DESTROYED_BY_INTERLEAVED_ORDER",
            "general_algorithm_lower_bound_gate": False,
            "promotion": "BLOCKED_FINITE_OR_RESTRICTED_ARCHITECTURE_RESULT_CANNOT_PROVE_P_NOT_EQUALS_NP",
        },
        "corridor_classification": final_class,
        "laws_checked": {
            "NO_CERTIFICATE_NO_ABSORPTION": True,
            "NO_RETURN_PATH_NO_ABSORPTION": True,
            "BAD_ORDER_NOT_HARDNESS": blocked_order_obstruction_destroyed_by_reverse_control,
            "SEMANTIC_ORACLE_FORBIDDEN": c025["semantic_merge_barrier"]["reduction"] == "F ≡ FALSE if and only if F is UNSAT",
            "P_VS_NP_REMAINS_OPEN": True,
        },
        "claim_boundary": (
            "This finite bidirectional run can localize algorithmic bottlenecks and "
            "falsify restricted claims. It cannot establish P=NP or P!=NP."
        ),
    }
    result["integrity"] = {"sha256": clean_hash(result)}

    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
