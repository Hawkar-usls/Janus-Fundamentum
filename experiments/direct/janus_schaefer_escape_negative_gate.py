#!/usr/bin/env python3
"""SCHAEFER_ESCAPE_NEGATIVE_GATE.

Feed the generic operation producer the positive exactly-one-of-three Boolean
relation.  No family label is supplied.  The gate expects only coordinate
projections among all preserving operations of arity <= 3.  Any nonprojection
operation is a falsification event for this frozen negative control.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.direct import janus_autonomous_boolean_operation_discovery as discovery


RELATION = ((1, 0, 0), (0, 1, 0), (0, 0, 1))


def main() -> int:
    report = discovery.discover([RELATION], max_arity=3)
    if not discovery.verify_discovery([RELATION], report):
        raise AssertionError("NEGATIVE_GATE_INDEPENDENT_DISCOVERY_VERIFIER_FAILED")

    if report["nonprojection_operation_count"] != 0:
        raise AssertionError(
            "SCHAEFER_ESCAPE_NEGATIVE_FALSIFIED_NONPROJECTION_OPERATION_FOUND"
        )

    counts = {
        arity: len(report["discovered_operations_by_arity"][str(arity)])
        for arity in (1, 2, 3)
    }
    expected_projection_counts = {1: 1, 2: 2, 3: 3}
    if counts != expected_projection_counts:
        raise AssertionError(
            f"PROJECTION_COUNT_DRIFT:{counts}!={expected_projection_counts}"
        )

    output = {
        "schema": "JANUS/C025/SCHAEFER-ESCAPE-NEGATIVE-GATE/v1",
        "status": "PASS_EXPECTED_OPEN",
        "input_relation": [list(row) for row in RELATION],
        "producer_input_family_label": False,
        "preserving_operation_counts_by_arity": counts,
        "nonprojection_operation_count": 0,
        "decision": "OPEN",
        "reason": (
            "ARITY_1_TO_3_EXACT_POLYMORPHISM_SEARCH_FOUND_ONLY_COORDINATE_PROJECTIONS"
        ),
        "ledger": report["ledger"],
        "source_fingerprint": report["source_fingerprint"],
        "scientific_boundary": {
            "this_is_a_negative_control_not_a_proof_of_np_hardness": True,
            "no_instance_specific_escape_attempted_here": True,
            "next_gate": "UNIVERSAL_INSTANCE_SPECIFIC_B_EXISTENCE_GATE",
            "P_VS_NP": "OPEN",
        },
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
